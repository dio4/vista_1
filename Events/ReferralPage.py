#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from PyQt4 import QtCore, QtGui

from PyQt4.QtCore import QDate
from PyQt4.QtGui import QTableWidgetItem, QComboBox
from datetime import datetime
from suds.client import Client

from Exchange.R23.netrica.services import NetricaServices
from Exchange.TFOMSExchange.DCExchangeSrv_types import *
from Exchange.TFOMSExchange.config import *
from Orgs.Orgs import selectOrganisation
from RefBooks.RBCancellationReasonList import CRBCancellationReasonList
from Registry.ReferralEditDialog import CReferralEditDialog
from Ui_ReferralPage import Ui_ReferralPage
from library.DialogBase import CConstructHelperMixin
from library.TableModel import CTableModel, CTextCol
from library.Utils import smartDict, toVariant, forceInt, forceString, forceDate, \
    forceRef, forceDateTime, getPref, getPrefInt, setPref, getVal, forceBool

logging.basicConfig(level=logging.INFO)
if __debug__:
    logging.getLogger('suds.client').setLevel(logging.DEBUG)
else:
    logging.getLogger('suds.client').setLevel(logging.CRITICAL)
from Exchange.R78.AIS.hospital import Exchange


# Заполнение информации о пакете
def getPackageInformation(pname):
    db = QtGui.qApp.db
    recordOrg = db.getRecordEx('Organisation', 'infisCode',
                               'id = %s' % forceString(QtGui.qApp.currentOrgId()))
    recordCount = db.getRecordEx('rbCounter', 'value', 'code = 4964')
    query = db.query(
        'UPDATE rbCounter SET value = %s WHERE code = 4964' % (forceInt(recordCount.value('value')) + 1))
    if not query:
        pass
    from Exchange.TFOMSExchange.DCExchangeSrv_types import ns1
    pkgInfo = ns1.cPackageInformation_Def(pname=pname)
    pkgInfo._p10_pakagedate = toDateTuple(QtCore.QDateTime.currentDateTime())
    pkgInfo._p11_pakagesender = forceString(recordOrg.value('infisCode'))
    pkgInfo._p12_pakageguid = 'Vista_'
    pkgInfo._p12_pakageguid += forceString(recordOrg.value('infisCode')) + '_'
    pkgInfo._p12_pakageguid += forceString(recordCount.value('value'))
    pkgInfo._p13_zerrpkg = 0
    pkgInfo._p14_errmsg = ''
    return pkgInfo


def toDateTuple(datetime, date=None):
    if date is None:
        date = datetime.date()
    time = datetime.time()
    return date.year(), date.month(), date.day(), time.hour(), time.minute(), time.second(), 0


class CReferralPage(QtGui.QWidget, Ui_ReferralPage, CConstructHelperMixin):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)

        self.clientId = None
        self.eventId = None

        self._onlyTotalDoseSumInfo = True
        self.db = QtGui.qApp.db
        self.dtRefDate.setDate(QtCore.QDate.currentDate())
        self.dtRefPlaned.setDate(QtCore.QDate.currentDate())
        self.cmbPerson.setValue(QtGui.qApp.userId)
        self.cmbRefBedProfile.addItem(u'')

        tableOrganisation = self.db.table('Organisation')
        self.cmbRelegateMO.setFilter(tableOrganisation['isMedical'].ne(0))

        self.addModels('PoliclinicReferrals', CHistoryTableModel(self, self.clientId))
        self.addModels('ReferralType', CReferralTypeModel(self))
        self.setModels(self.tblHistory, self.modelPoliclinicReferrals, self.selectionModelPoliclinicReferrals)
        self.setModels(self.tblRefType, self.modelReferralType, self.selectionModelReferralType)
        self.tblHistory.horizontalHeader().setClickable(True)

        self.modelPoliclinicReferrals.loadData(self.clientId)
        self.modelReferralType.loadData()

        self.tblMoList.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tblMoList.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblMoList.resizeColumnsToContents()
        self.tblMoList.resizeRowsToContents()
        self.tblMoList.setColumnWidth(1, 240)
        header = self.tblMoList.horizontalHeader()
        header.setStretchLastSection(True)

        self.cmbRefBedProfile.setTable('rbHospitalBedProfile', order='name')
        self.cmbOrgStructure.setTable('rbOrgStructureProfile')

        self.tblRefType.resizeColumnsToContents()
        self.tblRefType.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblRefType.selectRow(0)
        type = forceString(self.db.translate('rbReferralType', 'name', forceString(self.tblRefType.currentIndex().data(0)), 'code'))
        if type:
            self.hideFields(type)
        self.tblHistory.resizeColumnsToContents()
        self.tblHistory.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.cmbMedProfile.setTable('rbMedicalAidProfile', False, filter='netrica_Code IS NOT NULL', order='name')
        self.cmbRefHospType.setCurrentIndex(1)
        self.setCmbBoxes('RefCmb')
        self.dtRefDate.setMinimumDate(QtCore.QDate.currentDate().addMonths(-1))
        self.dtRefPlaned.setMinimumDate(QtCore.QDate.currentDate().addMonths(-1))
        self.dtRefPlaned.setMaximumDate(QtCore.QDate.currentDate().addMonths(6))
        self.btnAnotherLpu.setVisible(False)

        # региональные настройки
        if (QtGui.qApp.defaultKLADR().startswith('78')):
            self.tblMoList.cols = [u'Код МО', u'Наименование МО', u'Дата комиссии', u'Мест на комиссию',
                                   u'Профиль комисии', u'Наименование комиссии', u'Комментарий', u'Код комиссии']
            # self.tblMoList.cols = [u'Профиль помощи', u'Наименование МО', u'Адрес', u'Контакты', u'Окончание приема', u'Комментарий']
            self.tblMoList.setColumnCount(len(self.tblMoList.cols))
            self.tblMoList.setHorizontalHeaderLabels(self.tblMoList.cols)
            self.edtRefNumber.setReadOnly(True)
            self.lblOrgStructureProfile.setVisible(False)
            self.cmbOrgStructure.setVisible(False)
        else:
            self.tblMoList.cols = [u'Код МО', u'Наименование МО', u'Профиль койки', u'Свободно коек']
            self.tblMoList.setColumnCount(len(self.tblMoList.cols))
            self.tblMoList.setHorizontalHeaderLabels(self.tblMoList.cols)
            #     self.tblMoList.setVisible(False)
            #     self.btnGetMoList.setVisible(False)

    @staticmethod
    def toDateTuple(datetime, date=None):
        if date is None:
            date = datetime.date()
        time = datetime.time()
        return date.year(), date.month(), date.day(), time.hour(), time.minute(), time.second(), 0

    def setMKB(self, MKB):
        if MKB:
            self.edtRefMKB.setText(MKB)


            ###########Reserve Page########

    def setRecord(self, record):
        if record:
            self.setEventId(forceInt(record.value('id')))
            self.setClientId(forceInt(record.value('client_id')))
            self.setEventDate(forceString(record.value('setDate')))
            self.cmbPerson.setValue(forceInt(record.value('setPerson_id')))
            MKB = self.db.getRecordEx('Diagnosis', 'MKB',
                                      'client_id = %s AND person_id =%s AND deleted = 0 AND diagnosisType_id = 1' % (
                                          forceString(record.value('client_id')),
                                          forceString(record.value('setPerson_id'))))
            if MKB and forceString(MKB.value('MKB')):
                self.edtRefMKB.setText(forceString(MKB.value('MKB')))
            self.modelPoliclinicReferrals.reset()
            self.modelPoliclinicReferrals.loadData(forceInt(record.value('client_id')))

    def setEventId(self, value):
        self.eventId = value

    def setEventDate(self, value):
        self.eventDate = value

    def setClientId(self, value):
        self.clientId = value

    def _generateRowMO(self, a, moName, commissionInfo, rowPosition):
        def inner(i):
            self.tblMoList.setItem(rowPosition, 0, QTableWidgetItem(a['MedicalInstitutionReestrNumber']))

            self.tblMoList.setItem(rowPosition, 1, QTableWidgetItem(moName))

            self.tblMoList.setItem(rowPosition, 3, QTableWidgetItem(forceString(
                commissionInfo['commissions'][i]['attendance'])))

            self.tblMoList.setItem(rowPosition, 4,
                                   QTableWidgetItem(forceString(
                                       QtGui.qApp.db.translate('rbHospitalBedProfile', 'code',
                                                               a['BedProfileCode'], 'name'))))

            self.tblMoList.setItem(rowPosition, 5, QTableWidgetItem(forceString(
                commissionInfo['SelectionCommissionName'] if commissionInfo else u'')))

            self.tblMoList.setItem(rowPosition, 6, QTableWidgetItem(forceString(
                commissionInfo['commissions'][i]['AdditionalInfo']).replace(u'\n', u' ')))

            self.tblMoList.setItem(rowPosition, 7, QTableWidgetItem(forceString(
                commissionInfo['SelectionCommissionCode'])))

        return inner

    def getMoListByBedProfileSPB(self, profileCode):
        tableRefType = self.db.table('rbReferralType')
        refType = forceInt(
            self.db.translate(tableRefType, tableRefType['name'], forceString(self.tblRefType.currentIndex().data(0)),
                              tableRefType['netrica_Code']))
        if refType == 1:
            # Получение сведений о коммисиях и АИС ИНФОРМ
            exchan = Exchange()
            bedProfile = forceInt(self.cmbRefBedProfile.code())
            if not bedProfile:
                QtGui.QMessageBox.information(
                    self,
                    u"Ошибка",
                    u'Не выбран профиль койки',
                    QtGui.QMessageBox.Ok,
                    QtGui.QMessageBox.Ok
                )
                return
            molist = exchan.selection_commission_bed_profile(bedProfile)
            if molist:
                for a in molist:
                    moName = forceString(
                        QtGui.qApp.db.translate('Organisation', 'infisCode', a['MedicalInstitutionReestrNumber'],
                                                'shortName'))
                    if not moName:
                        moName = forceString(a['MedicalInstitutionShortName'])
                        table = self.db.table('Organisation')
                        newOrg = table.newRecord()
                        newOrg.setValue('infisCode', forceString(a['MedicalInstitutionReestrNumber']))
                        newOrg.setValue('shortName', forceString(a['MedicalInstitutionShortName']))
                        self.db.insertRecord(table, newOrg)
                        self.cmbRelegateMO.update()

                    pyDate = self.dtRefPlaned.date().toPyDate()
                    newDate = pyDate.replace(year=pyDate.year + 1)
                    commisionDate = forceString(self.dtRefDate.date().toString('yyyy-MM-dd')) + u' ' + forceString(
                        QDate(newDate.year, newDate.month, newDate.day).toString('yyyy-MM-dd')
                        # self.dtRefPlaned.date().toString('yyyy-MM-dd')
                    )

                    commisionInfo = exchan.user_appointment_queue_timetable_sign_filter(commisionDate, forceString(
                        a['SelectionCommissionCode']))

                    rowPosition = self.tblMoList.rowCount()
                    if commisionInfo and len(commisionInfo['commissions']) > 0:
                        commisionDateComboBox = QComboBox()
                        commisionDateComboBox.addItems(['{} ({}-{})'
                                                       .format(datetime.strptime(x['CalendarDate'][:10],
                                                                                 '%Y-%m-%d').strftime('%d.%m.%Y'),
                                                               x['BeginTime'][:5],
                                                               x['EndTime'][:5])
                                                        for x in commisionInfo['commissions']])
                        commisionDateComboBox.currentIndexChanged['int'].connect(
                            self._generateRowMO(a, moName, commisionInfo, rowPosition))

                        self.tblMoList.insertRow(rowPosition)

                        self.tblMoList.setCellWidget(rowPosition, 2, commisionDateComboBox)

                        self._generateRowMO(a, moName, commisionInfo, rowPosition)(0)
        else:
            # Получение коек из сервиса нетрики (СПБ)
            tblOrganisation = self.db.table('Organisation')
            exchange = NetricaServices()
            result = exchange.getQueueInfo(profileCode)
            if result and result.ActiveProfiles and result.ActiveProfiles.ActiveProfile:
                for profile in result.ActiveProfiles.ActiveProfile:
                    rowPosition = self.tblMoList.rowCount()
                    self.tblMoList.insertRow(rowPosition)
                    self.tblMoList.setItem(rowPosition, 0, QTableWidgetItem(self.cmbMedProfile.currentText()))
                    self.tblMoList.setItem(rowPosition, 1, QTableWidgetItem(forceString(
                        self.db.translate(tblOrganisation, tblOrganisation['netrica_Code'],
                                          forceString(profile.TargetLpu.Code), tblOrganisation['shortName']))))

                    self.tblMoList.setItem(rowPosition, 2, QTableWidgetItem(forceString(profile.EndDate)))
                    self.tblMoList.setItem(rowPosition, 3, QTableWidgetItem(forceString(profile.Comment)))
                    self.tblMoList.setItem(rowPosition, 4, QTableWidgetItem(forceString(profile.Address)))
                    self.tblMoList.setItem(rowPosition, 5, QTableWidgetItem(forceString(profile.ContactValue)))

    def getRefNumSPB(self):
        ex = Exchange()
        refNum = ex.user_referral_number_download()
        self.edtRefNumber.setText(refNum)

    def sendReferralSpb(self):
        ex = Exchange()
        dict = {}
        dict['refDate'] = self.dtRefDate.date()
        dict['refPlanDate'] = self.dtRefPlaned.date()
        if self.chkRefAgreement.isChecked():
            dict['agreement'] = 1
        else:
            dict['agreement'] = 0
        dict['number'] = self.edtRefNumber.text()
        dict['refInfo'] = self.cmbRefBedProfile.value()
        dict['MKB'] = self.edtRefMKB.text()
        dict['order'] = self.cmbRefHospType.currentIndex()
        dict['Person'] = self.cmbPerson.value()
        dict['Organisation'] = self.cmbRelegateMO.value()
        dict['bedProfile'] = self.cmbRefBedProfile.code()
        tableMKB = self.db.table('MKB')
        mkb = self.db.getRecordEx(tableMKB, 'id', tableMKB['DiagID'].eq(self.edtRefMKB.text()))
        if mkb:
            if ex.owner_appointment_referral_upload(dict):
                tblReferral = self.db.table('Referral')
                recReferral = self.db.getRecordEx(tblReferral, '*', [tblReferral['number'].eq(dict['number']),
                                                                     tblReferral['isSend'].eq(1)])
                if recReferral:
                    dT = forceString(self.tblMoList.cellWidget(self.tblMoList.currentRow(), 2).currentText()).split(' ')

                    comDate = datetime.strptime(dT[0], '%d.%m.%Y').strftime('%Y-%m-%d')
                    comTime = dT[1].split('-')[0][1:] + ':00'
                    additionalInfo = forceString(self.tblMoList.item(self.tblMoList.currentRow(), 6).text())
                    comissionCode = forceString(self.tblMoList.item(self.tblMoList.currentRow(), 7).text())
                    self.value = recReferral.setValue('ticketNumber', toVariant(
                        u'{ "date": "' + comDate + u' ' + comTime + u'", "address": "' + forceString(
                            additionalInfo) + u'"}'))
                    self.db.updateRecord(tblReferral, recReferral)
                    comissionData = {}
                    comissionData['referralDate'] = self.dtRefPlaned.date().toString('yyyy-MM-dd')
                    comissionData['referralNumber'] = self.edtRefNumber.text()
                    comissionData['bedProfile'] = self.cmbRefBedProfile.code()
                    comissionData['commisionCode'] = comissionCode
                    comissionData['attendanceDate'] = comDate  # self.dtRefPlaned.date()
                    comissionData['attendanceTime'] = comTime
                    ex.owner_appointment_queue_upload(comissionData, 1)
                QtGui.QMessageBox.information(self, u'Успешно', u'Направление успешно отправлено в АИС ИНФОРМ')
            else:
                QtGui.QMessageBox.warning(self, u'Ошибка', u'При отправке направление возникли ошибки')
        else:
            QtGui.QMessageBox.information(self, u'Ошибка', u'Несуществующий код МКБ')

    def getMoListBybedProfile(self):
        try:
            db = QtGui.qApp.db
            org = db.table('Organisation')
            bedProf = db.table('rbHospitalBedProfile')
            api = Client('http://10.20.29.2:8888/EchangeServerTFOMS/DCExchangeSrv?wsdl')

            if self.cmbRelegateMO.currentIndex() > 0:
                response = api.service.GetKDInformationByMO(username=userName, password=password, sendercode=senderCode,
                                                            mocode=forceString(
                                                                db.translate(org, 'id', self.cmbRelegateMO.value(),
                                                                             'infisCode')))
            elif self.cmbRefBedProfile.currentIndex() > 0:
                response = api.service.GetKDInformationByKpk(username=userName, password=password,
                                                             sendercode=senderCode,
                                                             kpkcode=self.cmbRefBedProfile.model().getCode(
                                                                 self.cmbRefBedProfile.currentIndex()))
            else:
                response = api.service.GetKDInformation(username=userName, password=password, sendercode=senderCode)

            resultList = []
            if not response.p11_kdInformationlist.l10_orcl:
                QtGui.QMessageBox.information(self, u'Не найдено', u'Не найдены МО со свободными койками.')
                return
            for v in response.p11_kdInformationlist.l10_orcl:
                bedsDict = CBedPrifile(v.m12_mocd)
                for k in v.m13_bprlist.s10_bpr:
                    bedsDict.addBeds(k.k10_kpkcd, (k.k15_cntfrmn + k.k16_cntfrwm + k.k17_cntfrch), 0)
                resultList.append(bedsDict)

            result = dict()
            for v in resultList:
                result[v.getMo()] = dict()
                allBeds = v.getAllBeds()
                result[v.getMo()]['busyBeds'] = v.getBusyBeds()
                result[v.getMo()]['freeBeds'] = dict()
                for a in allBeds.keys():
                    result[v.getMo()]['freeBeds'][a] = v.getFreeBedsByProfile(a)
                    if forceInt(v.getFreeBedsByProfile(a)):
                        rowPosition = self.tblMoList.rowCount()
                        moName = forceString(db.translate(org, 'infisCode', forceString(v.getMo()), 'shortName'))
                        self.tblMoList.insertRow(rowPosition)
                        self.tblMoList.setItem(rowPosition, 0, QTableWidgetItem(forceString(v.getMo())))
                        self.tblMoList.setItem(rowPosition, 1, QTableWidgetItem(moName))
                        self.tblMoList.setItem(rowPosition, 2, QTableWidgetItem(
                            forceString(db.translate(bedProf, 'code', forceString(a), 'name'))))
                        self.tblMoList.setItem(rowPosition, 3, QTableWidgetItem(str(v.getFreeBedsByProfile(a))))
        except Exception as error:
            if hasattr(error, 'strerror') and len(error.message) == 0:
                error.message = error.strerror
            QtGui.QMessageBox.information(
                self,
                u"Бронирование",
                error.message.decode('cp1251'),
                QtGui.QMessageBox.Ok,
                QtGui.QMessageBox.Ok
            )

    # Заполнение и отправка направления
    def sendReferral(self, referralType):
        tableReferral = self.db.table('Referral')
        tableReferralType = self.db.table('rbReferralType')

        refInfo = {}
        refInfo['person'] = self.cmbPerson.personId
        refInfo['type'] = referralType
        refInfo['number'] = self.edtRefNumber.text()
        refInfo['refDate'] = forceDateTime(self.dtRefDate.date()).toPyDateTime()
        refInfo['MKB'] = self.edtRefMKB.text()
        refInfo['plannedDate'] = forceDateTime(self.dtRefPlaned.date()).toPyDateTime()
        refInfo['relegateMO'] = self.cmbRelegateMO.value()
        refInfo['medProfile'] = self.cmbMedProfile.value()
        if self.cmbRefBedProfile.code() == u'59':
            tblEvent = self.db.table('Event')
            tblAction = self.db.table('Action')
            tblActionType = self.db.table('ActionType')
            tblActProperty = self.db.table('ActionProperty')
            tblActPropertyType = self.db.table('ActionPropertyType')
            tblActPropertyStr = self.db.table('ActionProperty_String')

            tblOFT = tblEvent.innerJoin(tblAction, [tblAction['event_id'].eq(self.eventId), tblAction['deleted'].eq(0)])
            tblOFT = tblOFT.innerJoin(tblActionType, [tblActionType['id'].eq(tblAction['actionType_id']),
                                                      tblActionType['flatCode'].eq(u'oftolmolog')])
            recAction = self.db.getRecordEx(tblOFT, tblAction['id'], tblEvent['id'].eq(self.eventId))
            if recAction:
                typesList = ['LYeql', 'LYDax', 'LYcyl', 'LYsph', 'LYOS', 'LYIntPres', 'RYeql', 'RYDax', 'RYcyl',
                             'RYsph', 'RYOD', 'RYIntPres', 'AddCatComp', 'AddProff']
                tblPropStr = tblActProperty.innerJoin(tblActPropertyStr,
                                                      tblActPropertyStr['id'].eq(tblActProperty['id']))
                tblPropStr = tblPropStr.innerJoin(tblActPropertyType,
                                                  [tblActProperty['type_id'].eq(tblActPropertyType['id']),
                                                   tblActPropertyType['shortName'].inlist(typesList)])
                recList = self.db.getIdList(tblPropStr, tblActProperty['id'],
                                            tblActProperty['action_id'].eq(forceInt(recAction.value('id'))))
                if recList:
                    refInfo['eyesInfo'] = recList
            else:
                if QtGui.QMessageBox.question(self, u'Ошибка',
                                              u'Не заполнен тип действия для направления на госпитализацию по катаракте глаза (офтальмология)\n Продолжить?',
                                              QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                              QtGui.QMessageBox.No) != QtGui.QMessageBox.Yes:
                    return

        service = NetricaServices()
        if self.cmbRelegateMO.value() in QtGui.qApp.currentLpuList():
            newRef = tableReferral.newRecord()
            newRef.setValue('createDatetime', toVariant(QtCore.QDateTime.currentDateTime()))
            newRef.setValue('createPerson_id', toVariant(QtGui.qApp.userId))
            newRef.setValue('number', toVariant(self.edtRefNumber.text()))
            newRef.setValue('event_id', toVariant(self.eventId))
            newRef.setValue('client_id', toVariant(self.clientId if self.clientId else QtGui.qApp.currentClientId()))
            newRef.setValue('date', toVariant(self.dtRefDate.date()))
            newRef.setValue('hospDate', toVariant(self.dtRefPlaned.date()))
            newRef.setValue('relegateOrg_id', toVariant(self.cmbRelegateMO.value()))
            newRef.setValue('MKB', toVariant(self.edtRefMKB.text()))
            newRef.setValue('type', toVariant(forceInt(
                self.db.translate(tableReferralType, tableReferralType['netrica_Code'], referralType,
                                  tableReferralType['id']))))
            newRef.setValue('medProfile_id', toVariant(self.cmbMedProfile.value()))
            newRef.setValue('isSend', toVariant(1))
            self.db.insertRecord(tableReferral, newRef)
            QtGui.QMessageBox.information(self, u'Успешно', u'Направление успешно сохранено')
        else:
            responce = service.sendReferral(refInfo)
            if responce:
                QtGui.QMessageBox.information(self, u'Успешно', u'Направление успешно отправлено в УО')
                newRef = tableReferral.newRecord()
                newRef.setValue('createDatetime', toVariant(QtCore.QDateTime.currentDateTime()))
                newRef.setValue('createPerson_id', toVariant(QtGui.qApp.userId))
                newRef.setValue('number', toVariant(self.edtRefNumber.text()))
                newRef.setValue('event_id', toVariant(self.eventId))
                newRef.setValue('status', toVariant(forceInt(responce.MqReferralStatus.Code)))
                newRef.setValue('client_id',
                                toVariant(self.clientId if self.clientId else QtGui.qApp.currentClientId()))
                newRef.setValue('date', toVariant(self.dtRefDate.date()))
                newRef.setValue('hospDate', toVariant(self.dtRefPlaned.date()))
                newRef.setValue('relegateOrg_id', toVariant(self.cmbRelegateMO.value()))
                newRef.setValue('MKB', toVariant(self.edtRefMKB.text()))
                newRef.setValue('type', toVariant(forceInt(
                    self.db.translate(tableReferralType, tableReferralType['netrica_Code'], referralType,
                                      tableReferralType['id']))))
                newRef.setValue('netrica_id', toVariant(forceString(responce.IdMq)))
                newRef.setValue('medProfile_id', toVariant(self.cmbMedProfile.value()))
                newRef.setValue('isSend', toVariant(1))
                self.db.insertRecord(tableReferral, newRef)
                self.btnSendRef.setText(u'Отправить направление')
                self.btnSendRef.setEnabled(True)
            else:
                QtGui.QMessageBox.warning(self, u'Ошибка', u'При отправке направления возникла ошибка')

    # Заполнение информации о пакете
    def __getPackageInformation(self, pname):
        recordOrg = self.db.getRecordEx('Organisation', 'infisCode',
                                        'id = %s' % forceString(QtGui.qApp.currentOrgId()))
        recordCount = self.db.getRecordEx('rbCounter', 'value', 'code = 4964')
        query = self.db.query(
            'UPDATE rbCounter SET value = %s WHERE code = 4964' % (forceInt(recordCount.value('value')) + 1))
        if not query:
            pass
        pkgInfo = ns1.cPackageInformation_Def(pname=pname)
        pkgInfo._p10_pakagedate = self.toDateTuple(QtCore.QDateTime.currentDateTime())
        pkgInfo._p11_pakagesender = forceString(recordOrg.value('infisCode'))
        pkgInfo._p12_pakageguid = 'Vista_'
        pkgInfo._p12_pakageguid += forceString(recordOrg.value('infisCode')) + '_'
        pkgInfo._p12_pakageguid += forceString(recordCount.value('value'))
        pkgInfo._p13_zerrpkg = 0
        pkgInfo._p14_errmsg = ''
        return pkgInfo

    # Заполнение информации о направлении
    def __getOrderClinic(self):
        result = ns1.cOrderClinic_Def(pname='1')
        result._m10_nzap = 1
        result._m11_ornm = forceString(self.edtRefNumber.text())
        result._m12_ordt = self.toDateTuple(forceDateTime(self.dtRefDate.date()))
        result._m13_ortp = forceInt(self.cmbRefHospType.currentIndex())
        result._m14_moscd = forceString(userName)
        recMo = self.db.getRecordEx('Organisation', 'infisCode', 'id = %s' % forceString(self.cmbRelegateMO.value()))
        result._m15_modcd = forceString(recMo.value('infisCode'))
        result._m16_pr = self.__getCPerson(forceString(self.clientId))
        result._m18_mkbcd = forceString(self.edtRefMKB.text())
        result._m19_kpkcd = forceString(self.cmbRefBedProfile.code())
        recOrg = self.db.getRecordEx('rbHospitalBedProfile', 'regionalCode',
                                     'code = %s' % forceString(result._m19_kpkcd))
        if recOrg:
            result._m20_sccd = forceString(recOrg.value('regionalCode'))
        recPerson = self.db.getRecordEx('Person', 'regionalCode', 'id = %s' % forceString(self.cmbPerson.personId))
        result._m21_dcnm = forceString(recPerson.value('regionalCode'))
        result._m22_dtph = self.toDateTuple(forceDateTime(self.dtRefPlaned.date()))
        result._m23_zerr = 0
        return result

    # Получение данных о пациенте
    def __getCPerson(self, clientId):
        record = self.db.getRecordEx('ClientPolicy', 'serial, number, insurer_id, insuranceArea, policyKind_id',
                                     'client_id = %s AND endDate IS NULL' % clientId)
        result = ns1.cPerson_Def('_m17_pr')
        result._a11_dcs = forceString(record.value('serial'))
        result._a12_dcn = forceString(record.value('number'))
        recOrg = self.db.getRecordEx('Organisation', 'infisCode', 'id = %s' % forceString(record.value('insurer_id')))
        if recOrg:
            result._a13_smcd = forceString(recOrg.value('infisCode'))
        result._a14_trcd = forceString('03000')
        record = self.db.getRecordEx('rbPolicyKind', 'code', 'id = %s' % forceString(record.value('policyKind_id')))
        result._a10_dct = forceInt(record.value('code')) if record else 3
        record = self.db.getRecordEx('Client', 'lastName, firstName, patrName, sex, birthDate', 'id = %s' % clientId)
        result._a15_pfio = forceString(record.value('lastName'))
        result._a16_pnm = forceString(record.value('firstName'))
        result._a17_pln = forceString(record.value('patrName'))
        result._a18_ps = forceString(record.value('sex'))
        result._a19_pbd = self.toDateTuple(forceDateTime(record.value('birthDate')))
        recContact = self.db.getRecordEx('ClientContact', 'contact', 'client_id = %s' % clientId)
        if recContact:
            result._a20_pph = forceString('contact')
        record = self.db.getRecordEx('ClientDocument', 'serial, number, documentType_id', 'client_id = %s' % clientId)
        result._a21_ps = forceString(record.value('serial'))
        result._a22_pn = forceString(record.value('number'))
        record = self.db.getRecordEx('rbDocumentType', 'code', 'id = %s' % forceString(record.value('documentType_id')))
        result._a23_dt = forceInt(record.value('code'))
        return result

    def saveRef(self):
        if QtGui.qApp.defaultKLADR().startswith('78'):
            tableRef = self.db.table('Referral')
            tableBedProfile = self.db.table('rbHospitalBedProfile')
            tableRefType = self.db.table('rbReferralType')
            recBedProfile = self.db.getRecordEx(tableBedProfile, 'id',
                                                tableBedProfile['code'].eq(self.cmbRefBedProfile.code()))
            recRef = self.db.getRecordEx(tableRef, '*', tableRef['number'].eq(self.edtRefNumber.text()))

            type = forceInt(self.db.translate(tableRefType,
                                              tableRefType['name'],
                                              forceString(self.tblRefType.currentIndex().data(0)),
                                              tableRefType['netrica_Code']))
            if recBedProfile or type == 10:
                if recRef:
                    if forceString(recRef.value('refDate')) == forceString(self.dtRefDate.date()):
                        if QtGui.QMessageBox.question(self, u'Перезапись',
                                                      u'Подобное направление уже создано. Перезаписать?',
                                                      QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                                      QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
                            recRef.setValue('date', toVariant(self.dtRefDate.date()))
                            recRef.setValue('relegateOrg_id', toVariant(self.cmbRelegateMO.value()))
                            recRef.setValue('hospBedProfile_id', toVariant(recBedProfile.value('id')))
                            recRef.setValue('hospDate', toVariant(self.dtRefPlaned.date()))
                            recRef.setValue('person', toVariant(self.cmbPerson.value()))
                            recRef.setValue('client_id', toVariant(self.clientId))
                            recRef.setValue('MKB', toVariant(self.edtRefMKB.text()))
                            recRef.setValue('notes', toVariant(self.edtNotes.toPlainText()))
                            recRef.setValue('examType', toVariant(self.cmbExamType.currentIndex()))
                            self.db.updateRecord(tableRef, recRef)
                else:
                    newRec = tableRef.newRecord()
                    newRec.setValue('number', toVariant(self.edtRefNumber.text()))
                    newRec.setValue('date', toVariant(self.dtRefDate.date()))
                    newRec.setValue('relegateOrg_id', toVariant(self.cmbRelegateMO.value()))
                    newRec.setValue('hospBedProfile_id', toVariant(recBedProfile.value('id')))
                    newRec.setValue('hospDate', toVariant(self.dtRefPlaned.date()))
                    newRec.setValue('person', toVariant(self.cmbPerson.value()))
                    newRec.setValue('client_id', toVariant(self.clientId))
                    newRec.setValue('MKB', toVariant(self.edtRefMKB.text()))
                    newRec.setValue('note', toVariant(self.edtNotes.toPlainText()))
                    newRec.setValue('isSend', toVariant(1))
                    newRec.setValue('type', toVariant(type))
                    newRec.setValue('event_id', toVariant(self.eventId))
                    newRec.setValue('examType', toVariant(self.cmbExamType.currentIndex()))
                    self.db.insertRecord(tableRef, newRec)
            else:
                QtGui.QMessageBox.information(self, u'Ошибка', u'Указаный профиль койки не найден.')
        else:
            if self.checkData():
                tableRef = self.db.table('Referral')
                tableBedProfile = self.db.table('rbHospitalBedProfile')
                tableRefType = self.db.table('rbReferralType')
                tableEvent = self.db.table('Event')
                recBedProfile = self.db.getRecordEx(tableBedProfile, 'id',
                                                    tableBedProfile['code'].eq(self.cmbRefBedProfile.code()))
                recRef = self.db.getRecordEx(tableRef, '*', tableRef['number'].eq(self.edtRefNumber.text()))
                if recBedProfile:
                    if recRef:
                        if forceString(recRef.value('refDate')) == forceString(self.dtRefDate.date()):
                            if QtGui.QMessageBox.question(self, u'Перезапись',
                                                          u'Подобное направление уже создано. Перезаписать?',
                                                          QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                                          QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
                                recRef.setValue('date', toVariant(self.dtRefDate.date()))
                                recRef.setValue('relegateOrg_id', toVariant(self.cmbRelegateMO.value()))
                                recRef.setValue('hospBedProfile_id', toVariant(recBedProfile.value('id')))
                                recRef.setValue('hospDate', toVariant(self.dtRefPlaned.date()))
                                recRef.setValue('person', toVariant(self.cmbPerson.currentText()))
                                recRef.setValue('client_id', toVariant(self.clientId))
                                recRef.setValue('MKB', toVariant(self.edtRefMKB.text()))
                                recRef.setValue('notes', toVariant(self.edtNotes.toPlainText()))
                                recRef.setValue('orgStructure', toVariant(self.cmbOrgStructure.value()))
                                recRef.setValue('clinicType', toVariant(self.cmbStatyonaryType.currentIndex()))
                                recRef.setValue('examType', toVariant(self.cmbExamType.currentIndex()))
                                self.db.updateRecord(tableRef, recRef)
                                return True
                    else:
                        newRec = tableRef.newRecord()
                        newRec.setValue('number', toVariant(self.edtRefNumber.text()))
                        newRec.setValue('date', toVariant(self.dtRefDate.date()))
                        newRec.setValue('relegateOrg_id', toVariant(self.cmbRelegateMO.value()))
                        newRec.setValue('hospBedProfile_id', toVariant(recBedProfile.value('id')))
                        newRec.setValue('hospDate', toVariant(self.dtRefPlaned.date()))
                        newRec.setValue('person', toVariant(self.cmbPerson.currentText()))
                        newRec.setValue('client_id', toVariant(self.clientId))
                        newRec.setValue('MKB', toVariant(self.edtRefMKB.text()))
                        newRec.setValue('notes', toVariant(self.edtNotes.toPlainText()))
                        newRec.setValue('isSend', toVariant(1))
                        newRec.setValue('type', toVariant(forceInt(self.db.translate(tableRefType, tableRefType['name'],
                                                                                     forceString(
                                                                                         self.tblRefType.currentIndex().data(
                                                                                             0)),
                                                                                     tableRefType['netrica_Code']))))
                        newRec.setValue('event_id', toVariant(self.eventId))
                        newRec.setValue('orgStructure', toVariant(self.cmbOrgStructure.value()))
                        newRec.setValue('clinicType', toVariant(self.cmbStatyonaryType.currentIndex()))
                        newRec.setValue('examType', toVariant(self.cmbExamType.currentIndex()))
                        refId = self.db.insertRecord(tableRef, newRec)
                        recEvent = self.db.getRecordEx(tableEvent, '*', tableEvent['id'].eq(self.eventId))
                        if recEvent:
                            recEvent.setValue('referral_id', toVariant(refId))
                            self.db.updateRecord(tableEvent, recEvent)
                        return True
                else:
                    QtGui.QMessageBox.information(self, u'Ошибка', u'Указаный профиль койки не найден.')
                    return False
            else:
                return False

    def checkData(self):
        tableClient = self.db.table('Client')
        tablePolicy = self.db.table('ClientPolicy')
        tableRefType = self.db.table('rbReferralType')
        type = forceInt(self.db.translate(tableRefType,
                                          tableRefType['name'],
                                          forceString(self.tblRefType.currentIndex().data(0)),
                                          tableRefType['netrica_Code']))
        errors = []
        if self.dtRefDate.date().isNull():
            errors.append(u'Не указана дата направления')
        if not self.dtRefPlaned.date().isNull() and self.dtRefPlaned.date() < self.dtRefDate.date():
            errors.append(u'Дата плановой госпитализации меньше даты направления')
        if not self.dtRefPlaned.date().isNull() and self.dtRefPlaned.date() > self.dtRefDate.date().addMonths(6):
            errors.append(u'Дата плановой госпитализации должна быть в пределах 6 месяцев')
        if not forceString(self.edtRefNumber.text()):
            errors.append(u'Не заполнен номер направления')
        if not forceInt(self.cmbRefHospType.currentIndex()):
            errors.append(u'Не выбран тип госпитализации')
        if not forceString(self.cmbRefBedProfile.code()):
            errors.append(u'Выбран не верный профиль койки')
        if not forceString(self.cmbOrgStructure.code()):
            errors.append(u'Выбран не верный профиль отделения')
        if not forceString(self.cmbRelegateMO.value()):
            errors.append(u'Не выбрана целевая МО')
        if not forceString(self.edtRefMKB.text()):
            errors.append(u'Не заполнен код МКБ')
        if not forceInt(self.cmbStatyonaryType.currentIndex()):
            errors.append(u'Не выбран тип стационара')
        recClient = self.db.getRecordEx(tableClient, '*', tableClient['id'].eq(self.clientId))
        if not forceString(recClient.value('firstName')):
            errors.append(u'Не введено имя клиента')
        if not forceString(recClient.value('lastName')):
            errors.append(u'Не введена фамилия клиента')
        if not forceString(recClient.value('birthDate')):
            errors.append(u'Не задана дата рождения клиента')
        recPolicy = self.db.getRecordEx(tablePolicy,
                                        [tablePolicy['number'], tablePolicy['serial'], tablePolicy['insurer_id']],
                                        [tablePolicy['client_id'].eq(self.clientId),
                                         tablePolicy['deleted'].eq(0),
                                         ])
        if recPolicy:
            if not forceString(recPolicy.value('number')):
                errors.append(u'Не введен номер полиса у клиента')
            # if not forceString(recPolicy.value('serial')):
            #     errors.append(u'Не введена серия полиса клиента')
            if not forceString(recPolicy.value('insurer_id')):
                errors.append(u'Не задана территория страхования полиса клиента')
        else:
            errors.append(u'Не найден действующий полис клиента')
        if type == 3:
            if not self.cmbExamType.currentIndex():
                errors.append(u'Не выбран вид назначенного обследования')
        if errors:
            self.showErrors(errors)
            return False
        else:
            return True

    def showErrors(self, errors):
        QtGui.QMessageBox.warning(self, u'Ошибка', u'\n'.join(v for v in errors))

    def hideFields(self, type):
        if forceString(type) == u'hospitalisation':
            self.lblRefPlanned.setText(u'Плановая дата госпитализации:')
            self.btnAnotherLpu.setVisible(False)
            self.lblMedProfile.setVisible(True)
            self.cmbMedProfile.setVisible(True)
            self.btnGetMoList.setVisible(True)
            self.tblMoList.setVisible(True)
            self.dtRefPlaned.setVisible(True)
            self.cmbPerson.setVisible(True)
            self.cmbRefHospType.setVisible(True)
            self.cmbRefBedProfile.setVisible(True)
            self.edtRefMKB.setVisible(True)
            self.lblRefPlanned.setVisible(True)
            self.lblPerson.setVisible(True)
            self.lblRefHospType.setVisible(True)
            self.lblRefBedProfile.setVisible(True)
            self.lblRefMKB.setVisible(True)
            self.lblOrgStructureProfile.setVisible(True)
            self.cmbOrgStructure.setVisible(True)
            self.lblStatyonaryType.setVisible(True)
            self.cmbStatyonaryType.setVisible(True)
            self.lblExamType.setVisible(False)
            self.cmbExamType.setVisible(False)
            if QtGui.qApp.defaultKLADR().startswith('78'):
                self.lblOrgStructureProfile.setVisible(False)
                self.cmbOrgStructure.setVisible(False)
        elif forceString(type) == u'diagnostic':
            self.lblRefPlanned.setText(u'Плановая дата диагностики/исследования:')
            self.btnAnotherLpu.setVisible(False)
            self.lblMedProfile.setVisible(True)
            self.cmbMedProfile.setVisible(True)
            # self.dtRefPlaned.setVisible(False)
            # self.lblRefPlanned.setVisible(False)
            # self.lblPerson.setVisible(True)
            # self.cmbPerson.setVisible(True)
            self.btnGetMoList.setVisible(False)
            self.tblMoList.setVisible(False)
            self.lblRefHospType.setVisible(False)
            self.cmbRefHospType.setVisible(False)
            self.lblRefBedProfile.setVisible(False)
            self.cmbRefBedProfile.setVisible(False)
            # self.lblRefMKB.setVisible(False)
            # self.edtRefMKB.setVisible(False)
            self.lblOrgStructureProfile.setVisible(False)
            self.cmbOrgStructure.setVisible(False)
            self.lblStatyonaryType.setVisible(False)
            self.cmbStatyonaryType.setVisible(False)
            self.lblExamType.setVisible(True)
            self.cmbExamType.setVisible(True)
        elif forceString(type) == u'consultation':
            self.lblRefPlanned.setText(u'Плановая дата консультации:')
            self.btnAnotherLpu.setVisible(True)
            self.lblMedProfile.setVisible(True)
            self.cmbMedProfile.setVisible(True)
            # self.lblRefPlanned.setVisible(False)
            # self.dtRefPlaned.setVisible(False)
            # self.lblPerson.setVisible(False)
            # self.cmbPerson.setVisible(False)
            self.btnGetMoList.setVisible(True)
            self.tblMoList.setVisible(True)
            self.lblRefHospType.setVisible(False)
            self.cmbRefHospType.setVisible(False)
            self.lblRefBedProfile.setVisible(False)
            self.cmbRefBedProfile.setVisible(False)
            # self.lblRefMKB.setVisible(False)
            # self.edtRefMKB.setVisible(False)
            self.lblOrgStructureProfile.setVisible(False)
            self.cmbOrgStructure.setVisible(False)
            self.lblStatyonaryType.setVisible(False)
            self.cmbStatyonaryType.setVisible(False)
            self.lblExamType.setVisible(False)
            self.cmbExamType.setVisible(False)
        elif forceString(type) == u'grkm':
            self.btnAnotherLpu.setVisible(False)
            self.lblMedProfile.setVisible(False)
            self.cmbMedProfile.setVisible(False)
            self.btnGetMoList.setVisible(False)
            self.tblMoList.setVisible(False)
            self.lblRefHospType.setVisible(False)
            self.cmbRefHospType.setVisible(False)
            self.lblRefBedProfile.setVisible(False)
            self.cmbRefBedProfile.setVisible(False)
            self.lblOrgStructureProfile.setVisible(False)
            self.cmbOrgStructure.setVisible(False)
            self.lblStatyonaryType.setVisible(False)
            self.cmbStatyonaryType.setVisible(False)
            # self.edtRefNumber.setReadOnly(False)
            self.lblExamType.setVisible(False)
            self.lblExamType.setVisible(False)
            if forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'GRKMService', False)):
                level = forceInt(getVal(QtGui.qApp.preferences.appPrefs, 'GRKMServiceLevel', ''))
                if level == 0:
                    self.lblRefPlanned.setText(u'Плановая дата первичного осмотра:')
                elif level == 1:
                    self.lblRefPlanned.setText(u'Плановая дата:')
                elif level == 2:
                    self.lblRefPlanned.setText(u'Плановая дата госпитализации:')

    def setCmbBoxes(self, dicTag):
        preferences = getPref(QtGui.qApp.preferences.windowPrefs, 'RefCmb', {})
        checkList = getPref(preferences, forceString(dicTag), {})
        if checkList:
            self.cmbRelegateMO.setCurrentIndex(getPrefInt(checkList, 'RelMo', 0))
            self.cmbOrgStructure.setCurrentIndex(getPrefInt(checkList, 'OrgStruct', 0))
            self.cmbRefBedProfile.setCurrentIndex(getPrefInt(checkList, 'BedProfile', 0))
            self.cmbStatyonaryType.setCurrentIndex(getPrefInt(checkList, 'StatyonaryType', 0))
            self.cmbMedProfile.setCurrentIndex(getPrefInt(checkList, 'MedProfile', 0))

    def getCmbBoxes(self):
        checkList = {}
        setPref(checkList, 'RelMo', self.cmbRelegateMO.currentIndex())
        setPref(checkList, 'OrgStruct', self.cmbOrgStructure.currentIndex())
        setPref(checkList, 'BedProfile', self.cmbRefBedProfile.currentIndex())
        setPref(checkList, 'StatyonaryType', self.cmbStatyonaryType.currentIndex())
        setPref(checkList, 'MedProfile', self.cmbMedProfile.currentIndex())
        preferences = {}
        setPref(preferences, forceString('RefCmb'), checkList)
        setPref(QtGui.qApp.preferences.windowPrefs, 'RefCmb', preferences)

    def edtReferral(self, record):
        if record:
            edtDlg = CReferralEditDialog(parent=self, referralId=forceString(record.value('id')))
            if edtDlg.checkData():
                if not edtDlg.exec_():
                    return False
                if QtGui.qApp.defaultKLADR().startswith('23') and forceInt(record.value('type')) == 1:
                    if edtDlg.checkData() and edtDlg.beforeSave() and edtDlg.getRecord():
                        QtGui.QMessageBox.information(self, u'Успешно', u'Направление успешно изменено')
                    else:
                        QtGui.QMessageBox.warning(self, u'Ошибка', u'При изменении направления возникли ошибки')
                else:
                    if edtDlg.checkData() and edtDlg.beforeSave() and edtDlg.updReferral() and edtDlg.getRecord():
                        QtGui.QMessageBox.information(self, u'Успешно', u'Направление успешно изменено')
                    else:
                        QtGui.QMessageBox.warning(self, u'Ошибка', u'При изменении направления возникли ошибки')
        self.modelPoliclinicReferrals.loadData(self.clientId)
        self.tblHistory.resizeColumnsToContents()

    def checkOnAlreadyReferral(self, refType):
        tblReferral = self.db.table('Referral')
        recReferral = self.db.getRecordEx(tblReferral, '*', [tblReferral['date'].eq(forceDate(self.dtRefDate.date())),
                                                             tblReferral['type'].eq(forceInt(refType)),
                                                             tblReferral['client_id'].eq(self.clientId),
                                                             tblReferral['isCancelled'].eq(0),
                                                             tblReferral['isSend'].eq(1),
                                                             tblReferral['deleted'].eq(0),
                                                             tblReferral['medProfile_id'].eq(
                                                                 self.cmbMedProfile.value())])

        if recReferral:
            if QtGui.QMessageBox.information(self, u'Внимание',
                                             u'Для данного пациента сегодня уже было создано похожее направление\nОтредактировать?',
                                             QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                             QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
                self.edtReferral(recReferral)
                return True
            else:
                return True
        else:
            return False

    @QtCore.pyqtSlot()
    def on_btnGetMoList_clicked(self):
        if self.tblMoList.rowCount():
            for i in reversed(range(self.tblMoList.rowCount())):
                self.tblMoList.removeRow(i)

        if QtGui.qApp.defaultKLADR().startswith('78'):
            tblMedProfile = self.db.table('rbMedicalAidProfile')
            profileCode = forceString(self.db.translate(tblMedProfile, tblMedProfile['id'], self.cmbMedProfile.value(),
                                                        tblMedProfile['netrica_Code']))
            self.getMoListByBedProfileSPB(profileCode)
            self.tblMoList.resizeColumnsToContents()
        else:
            self.getMoListBybedProfile()
            self.tblMoList.resizeColumnsToContents()

    @QtCore.pyqtSlot()
    def on_btnSendRef_clicked(self):

        # функция кнопки Применить
        self.setRecord(QtGui.qApp.db.getRecord('Event', '*', self.eventId))

        self.getCmbBoxes()
        tableRefType = self.db.table('rbReferralType')
        refType = forceInt(
            self.db.translate(tableRefType, tableRefType['name'], forceString(self.tblRefType.currentIndex().data(0)),
                              tableRefType['netrica_Code']))
        if not self.checkOnAlreadyReferral(refType):
            if QtGui.qApp.defaultKLADR().startswith('23'):
                if refType and refType == 1:
                    if self.eventId:
                        if self.saveRef():
                            QtGui.QMessageBox.information(self, u'Сохранено', u'Направление успешно сохранено')
                        else:
                            QtGui.QMessageBox.warning(self, u'Ошибка', u'При сохранении обращения возникли ошибки')
                    else:
                        QtGui.QMessageBox.warning(self, u'Ошибка',
                                                  u'Перед отправкой направления необходимо сохранить обращение')
                elif refType:
                    if refType == 3 and not self.cmbExamType.currentIndex():
                        QtGui.QMessageBox.warning(self, u'Ошибка', u'Не выбран вид назначенного обследования')
                        return
                    self.sendReferral(refType)
            else:
                if refType and refType == 10:
                    if self.eventId and self.isDirty():
                        if self.saveRef():
                            QtGui.QMessageBox.information(self, u'Сохранено', u'Направление успешно сохранено')
                        else:
                            QtGui.QMessageBox.warning(self, u'Ошибка', u'При сохранении обращения возникли ошибки')
                    else:
                        QtGui.QMessageBox.warning(self, u'Ошибка',
                                                  u'Перед отправкой направления необходимо сохранить обращение')
                else:
                    self.sendReferral(refType)
                    if refType == 1:
                        self.sendReferralSpb()

    @QtCore.pyqtSlot()
    def on_btnRefGenNumber_clicked(self):
        if QtGui.qApp.defaultKLADR().startswith('78'):
            self.getRefNumSPB()
        else:
            num = self.db.getRecordEx('rbCounter', '*', 'code = %s' % u'4965')
            if num:
                refNumber = forceString(self.db.translate('OrgStructure',
                                                          'id', QtGui.qApp.currentOrgStructureId(),
                                                          'bookkeeperCode'))
                if not refNumber:
                    refNumber = forceString(self.db.translate('Organisation',
                                                              'id', QtGui.qApp.currentOrgId(),
                                                              'infisCode'))
                refNumber += u'_' + forceString(num.value('value'))
                self.edtRefNumber.setText(refNumber)
                num.setValue('value', forceInt(num.value('value')) + 1)
                self.db.updateRecord('rbCounter', num)

    @QtCore.pyqtSlot()
    def on_btnSelectOrganisation_clicked(self):
        orgId = selectOrganisation(self, self.cmbRelegateMO.value(), False)
        self.cmbRelegateMO.update()
        if orgId:
            self.cmbRelegateMO.setValue(orgId)

    @QtCore.pyqtSlot()
    def on_btnUpdateTable_clicked(self):
        self.modelPoliclinicReferrals.loadData(self.clientId)
        self.tblHistory.resizeColumnsToContents()

    @QtCore.pyqtSlot()
    def on_btnEditReferral_clicked(self):
        tableReferral = self.db.table('Referral')
        row = self.tblHistory.currentIndex().row()
        item = self.modelPoliclinicReferrals.items[row]
        recReferral = self.db.getRecordEx(tableReferral, '*', [tableReferral['number'].eq(forceString(item['number'])),
                                                               tableReferral['client_id'].eq(self.clientId)])
        if recReferral:
            self.edtReferral(recReferral)

    @QtCore.pyqtSlot()
    def on_btnCancellation_clicked(self):  # CANCEL
        tableReferral = self.db.table('Referral')
        row = self.tblHistory.currentIndex().row()
        item = self.modelPoliclinicReferrals.items[row]
        recReferral = self.db.getRecordEx(tableReferral, '*', tableReferral['number'].eq(forceString(item['number'])))
        if recReferral:
            if forceInt(recReferral.value('isCancelled')):
                QtGui.QMessageBox.warning(self, u'Ошибка', u'Направление уже аннулировано.')
                return
            reasonDialog = CRBCancellationReasonList(self)
            if not reasonDialog.exec_():
                return
            reason = reasonDialog.params()
            if QtGui.qApp.defaultKLADR().startswith('23') and forceInt(recReferral.value('type')) == 1:
                recReferral.setValue('cancelReason', toVariant(forceInt(reason)))
                recReferral.setValue('isCancelled', toVariant(1))
                recReferral.setValue('cancelPerson_id', toVariant(QtGui.qApp.userId))
                recReferral.setValue('cancelDate', toVariant(QtCore.QDateTime.currentDateTime()))
                recReferral.setValue('status'), toVariant(0)
                self.db.updateRecord(tableReferral, recReferral)
                QtGui.QMessageBox.information(self, u'Успешно',
                                              u'Направление успешно аннулировано.\nДанные обновятся в ЦОД при следующей передаче.')
            else:
                service = NetricaServices()
                cancellation = service.sendCancellation(forceString(recReferral.value('netrica_id')))
                if cancellation:
                    recReferral.setValue('isCancelled', toVariant(1))
                    recReferral.setValue('cancelPerson_id', toVariant(QtGui.qApp.userId))
                    recReferral.setValue('cancelDate', toVariant(QtCore.QDateTime.currentDateTime()))
                    recReferral.setValue('cancelReason', toVariant(forceInt(reason)))
                    recReferral.setValue('status', toVariant(0))
                    self.db.updateRecord(tableReferral, recReferral)
                    QtGui.QMessageBox.information(self, u'Успешно', u'Направление успешно аннулировано')
        self.modelPoliclinicReferrals.loadData(self.clientId)
        self.tblHistory.resizeColumnsToContents()

    @QtCore.pyqtSlot()
    def on_btnResultDocument_clicked(self):
        tableReferral = self.db.table('Referral')
        tableDocument = self.db.table('ClientFile')
        row = self.tblHistory.currentIndex().row()
        item = self.modelPoliclinicReferrals.items[row]
        recReferral = self.db.getRecordEx(tableReferral, '*', tableReferral['number'].eq(forceString(item['number'])))
        if recReferral:
            service = NetricaServices()
            doc = service.getResultDocument(forceString(recReferral.value('netrica_id')))
            if doc and doc.ResultDocument.Data:
                recFile = tableDocument.newRecord()
                recFile.setValue('client_id', toVariant(self.clientId))
                recFile.setValue('name',
                                 toVariant(u'Referral' + forceString(recReferral.value['netrica_id']) + u'Result.pdf'))
                recFile.setValue('file', toVariant(doc.ResultDocument.Data))
                self.db.insertRecord(tableDocument, recFile)

    @QtCore.pyqtSlot()
    def on_tblHistory_itemSelectionChanged(self):
        row = self.tblHistory.currentIndex().row()
        item = self.modelPoliclinicReferrals.items[row]
        if forceInt(item['status']) == 7:
            self.btnResultDocument.setEnabled(True)
        else:
            self.btnResultDocument.setEnabled(False)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblMoList_doubleClicked(self, index):
        tblOrganisation = self.db.table('Organisation')
        if (QtGui.qApp.defaultKLADR().startswith('78')):
            code = self.tblMoList.item(self.tblMoList.currentRow(), 1).text()
            orgRec = self.db.getRecordEx(tblOrganisation, tblOrganisation['id'],
                                         tblOrganisation['shortName'].eq(forceString(code)))
            if orgRec:
                self.cmbRelegateMO.update()
                self.cmbRelegateMO.setValue(forceInt(orgRec.value('id')))
        else:
            code = self.tblMoList.item(self.tblMoList.currentRow(), 0).text()
            orgRec = self.db.getRecordEx(tblOrganisation, tblOrganisation['id'],
                                         tblOrganisation['infisCode'].eq(forceString(code)))
            if orgRec:
                self.cmbRelegateMO.update()
                self.cmbRelegateMO.setValue(forceInt(orgRec.value('id')))

    @QtCore.pyqtSlot()
    def on_btnOrgFilter_clicked(self):
        orgId = selectOrganisation(self, self.cmbRelegateMO.value(), False)
        self.cmbRelegateMO.update()
        if orgId:
            self.cmbRelegateMO.setValue(orgId)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblRefType_clicked(self, index):
        tableRefType = self.db.table('rbReferralType')
        type = forceString(
            self.db.translate(tableRefType, tableRefType['name'], forceString(index.data(0)), tableRefType['code']))
        if type:
            self.hideFields(type)

    @QtCore.pyqtSlot()
    def on_btnUpdateStatuses_clicked(self):
        tableReferral = self.db.table('Referral')
        for item in self.tblHistory.model().items:
            if item['number']:
                recReferral = self.db.getRecordEx(tableReferral, '*',
                                                  tableReferral['number'].eq(forceString(item['number'])))
                if recReferral and forceString(recReferral.value('netrica_id')):
                    service = NetricaServices()
                    try:
                        responce = service.searchOne(forceString(recReferral.value('netrica_id')))
                    except:
                        QtGui.QMessageBox.warning(self, u'Ошибка', u'Синхронизация завершена с ошибками')
                    if responce and responce.MqReferralStatus.Code:
                        recReferral.setValue('status', toVariant(forceInt(responce.MqReferralStatus.Code)))
                        self.db.updateRecord(tableReferral, recReferral)
                    else:
                        QtGui.QMessageBox.warning(self, u'Ошибка',
                                                  u'В УО не найдено направление \n номер: %s \n идентификатор УО: %s' % (
                                                      forceString(item['number']),
                                                      forceString(recReferral.value('netrica_id'))))
        self.modelPoliclinicReferrals.clear()
        self.modelPoliclinicReferrals.loadData(self.clientId)
        QtGui.QMessageBox.information(self, u'Завершено', u'Синхронизация статусов завершена')

    @QtCore.pyqtSlot()
    def on_btnAnotherLpu_clicked(self):
        from Exchange.R23.netrica.Appointment import Appoinment
        Appoinment(self, self.edtRefNumber.text()).exec_()

    @QtCore.pyqtSlot()
    def on_btnResetMo_clicked(self):
        self.cmbRelegateMO.setCurrentIndex(0)


class CMOTableModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent, [
            CTextCol(u'Наименование МО', [], 5),
            CTextCol(u'Профиль койки', [], 30),
            CTextCol(u'Свободно', [], 20)
        ], '')

        self.parentWidget = parent


class CBaseReferralTypeModel(QtCore.QAbstractTableModel):
    headerText = [u'Тип направления']
    tables = smartDict()

    def __init__(self, parent):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.items = []
        self.headerSortingCol = {}
        self._cols = []
        self.mapColFieldNameToColIndex = {}
        self.initTables()
        QtGui.qApp.db.disconnected.connect(self.onDatabaseDisconnected)
        self.updateStatuses = False

    @classmethod
    def initTables(self):
        if len(self.tables) == 0:
            db = QtGui.qApp.db
            self.tables.referralType = db.table('rbReferralType')

    @QtCore.pyqtSlot()
    def onDatabaseDisconnected(self):
        if CBaseReferralTypeModel.tables:
            CBaseReferralTypeModel.tables = smartDict()

    def cols(self):
        return self._cols

    def getColumnByFieldName(self, fieldName):
        if fieldName not in self.mapColFieldNameToColIndex:
            for i, column in enumerate(self.cols()):
                fields = column.fields()
                for field in fields:
                    if field not in self.mapColFieldNameToColIndex:
                        self.mapColFieldNameToColIndex[field] = i
        index = self.mapColFieldNameToColIndex.get(fieldName, None)
        return self.cols()[index]

    def columnCount(self, index=QtCore.QModelIndex()):
        return len(self._cols)

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self.items)

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.headerText[section])
            elif role == QtCore.Qt.ToolTipRole:
                return QtCore.QVariant(self._cols[section].title(short=False))
        return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = index.column()
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            item = self.items[row]
            return toVariant(item['name'])
        return QtCore.QVariant()

    def formColumns(self):
        self._cols = []
        self._cols.append(CTextCol(u'Наименование', ['name'], 100, 'l'))

    def getQueryCols(self):
        cols = []
        cols.append(self.tables.referralType['name'])
        return cols

    def getCondAndQueryTable(self):
        cond = []
        cols = self.getQueryCols()

        queryTable = self.tables.referralType

        return queryTable, cond, cols

    def getItemFromRecord(self, record):
        return {
            'name': forceString(record.value('name'))
        }


class CReferralTypeModel(CBaseReferralTypeModel):
    def __init__(self, parent):
        self.parentWidget = parent
        CBaseReferralTypeModel.__init__(self, parent)
        self.items = []
        self.idList = []
        self.formColumns()
        self.isColor = False

    def data(self, index, role=QtCore.Qt.DisplayRole):
        return CBaseReferralTypeModel.data(self, index, role)

    def loadData(self):
        self.items = []
        db = QtGui.qApp.db

        queryTable, cond, cols = self.getCondAndQueryTable()
        records = db.getRecordList(queryTable, cols, cond)
        for record in records:
            item = self.getItemFromRecord(record)
            self.items.append(item)
        self.reset()


########History Page###########
class CBaseHistoryModel(QtCore.QAbstractTableModel):
    tables = smartDict()

    def __init__(self, parent):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.items = []
        self.headerSortingCol = {}
        self._cols = []
        self.mapColFieldNameToColIndex = {}
        self.initTables()
        QtGui.qApp.db.disconnected.connect(self.onDatabaseDisconnected)
        self.updateStatuses = False

    @classmethod
    def initTables(self):
        if len(self.tables) == 0:
            db = QtGui.qApp.db
            self.tables.Referral = db.table('Referral')
            self.tables.BedProfile = db.table('rbHospitalBedProfile')
            self.tables.Client = db.table('Client')
            self.tables.Person = db.table('Person')
            self.tables.Organisation = db.table('Organisation')
            self.tables.MedProfile = db.table('rbMedicalAidProfile')
            self.tables.ReferralType = db.table('rbReferralType')

    @QtCore.pyqtSlot()
    def onDatabaseDisconnected(self):
        if CBaseHistoryModel.tables:
            CBaseHistoryModel.tables = smartDict()

    def cols(self):
        return self._cols

    def getColumnByFieldName(self, fieldName):
        if fieldName not in self.mapColFieldNameToColIndex:
            for i, column in enumerate(self.cols()):
                fields = column.fields()
                for field in fields:
                    if field not in self.mapColFieldNameToColIndex:
                        self.mapColFieldNameToColIndex[field] = i
        index = self.mapColFieldNameToColIndex.get(fieldName, None)
        return self.cols()[index]

    def columnCount(self, index=QtCore.QModelIndex()):
        return len(self._cols)

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self.items)

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self._cols[section].title())
        return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = self.cols()[index.column()]
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            item = self.items[row]
            return toVariant(item[column._fields[0]])
        return QtCore.QVariant()

    def formColumns(self):
        self._cols = []
        self._cols.append(CTextCol(u'No Направления', ['number'], 15, 'l'))
        self._cols.append(CTextCol(u'Тип направления', ['type'], 15, 'l'))
        self._cols.append(CTextCol(u'Статус', ['status'], 15, 'l'))
        self._cols.append(CTextCol(u'МО, куда направлен пациент', ['orgName'], 30, 'l'))
        self._cols.append(CTextCol(u'Дата направления', ['date'], 25, 'l'))
        self._cols.append(CTextCol(u'Профиль медицинской помощи', ['medProfile'], 20, 'l'))
        self._cols.append(CTextCol(u'Диагноз направления', ['MKB'], 10, 'l'))
        self._cols.append(CTextCol(u'ФИО пациента', ['clientName'], 20, 'l'))
        self._cols.append(CTextCol(u'Дата рождения', ['birthDate'], 20, 'l'))
        self._cols.append(CTextCol(u'Примечания', ['notes'], 20, 'l'))
        self._cols.append(CTextCol(u'Предварительная запись', ['ticketNumber'], 20, 'l'))
        self._cols.append(CTextCol(u'Дата аннулирования', ['cancelDate'], 25, 'l'))
        self._cols.append(CTextCol(u'Причина аннулирования', ['cancelReason'], 'rbCancellationReason', 25))

    def getQueryCols(self):
        cols = []
        cols.append(self.tables.Client['lastName'].alias('clientLastName'))
        cols.append(self.tables.Client['firstName'].alias('clientFirstName'))
        cols.append(self.tables.Client['patrName'].alias('clientPatrName'))
        cols.append(self.tables.Client['birthDate'])
        cols.append(self.tables.ReferralType['name'].alias('referralTypeName'))

        cols.append(self.tables.Referral['number'])
        cols.append(self.tables.Referral['date'])
        cols.append(self.tables.Referral['hospDate'])
        cols.append(self.tables.Referral['MKB'])
        cols.append(self.tables.Referral['status'])
        cols.append(self.tables.Referral['id'].alias('policlinicReferralsId'))
        cols.append(self.tables.Referral['notes'])
        cols.append(self.tables.Referral['client_id'])
        cols.append(self.tables.Referral['ticketNumber'])
        cols.append(self.tables.Referral['cancelDate'])
        cols.append(self.tables.Referral['cancelReason'])

        cols.append(self.tables.Organisation['shortName'].alias('orgName'))
        cols.append(self.tables.MedProfile['id'].alias('medProfileId'))
        cols.append(self.tables.MedProfile['name'].alias('medProfileName'))
        return cols

    def getCondAndQueryTable(self, clientId):
        cond = []
        cols = self.getQueryCols()

        queryTable = self.tables.Referral.innerJoin(
            self.tables.Client,
            self.tables.Referral['client_id'].eq(self.tables.Client['id'])
        )

        queryTable = queryTable.leftJoin(
            self.tables.MedProfile,
            self.tables.Referral['medProfile_id'].eq(self.tables.MedProfile['id'])
        )
        queryTable = queryTable.leftJoin(
            self.tables.Organisation,
            self.tables.Referral['relegateOrg_id'].eq(self.tables.Organisation['id'])
        )
        queryTable = queryTable.leftJoin(
            self.tables.ReferralType,
            self.tables.ReferralType['id'].eq(self.tables.Referral['type'])
        )

        cond.append(self.tables.Referral['client_id'].eq(clientId))
        cond.append(self.tables.Referral['isSend'].eq(1))
        return queryTable, cond, cols

    def getItemFromRecord(self, record):
        db = QtGui.qApp.db
        tableCancellation = db.table('rbCancellationReason')
        return {
            'referralsId': forceRef(record.value('referralsId')),
            'personId': forceRef(record.value('person_id')),
            'clientId': forceRef(record.value('client_id')),
            # PoliclinicReferrals info
            'status': forceString(record.value('status')),
            'number': forceString(record.value('number')),
            'hospDate': forceDate(record.value('hospDate')),
            'date': forceDate(record.value('date')),
            'MKB': forceString(record.value('MKB')),
            'notes': forceString(record.value('notes')),
            'type': forceString(record.value('referralTypeName')),
            # Client info
            'clientName': forceString(record.value('clientLastName')) + \
                          u' ' + forceString(record.value('clientFirstName')) + \
                          u' ' + forceString(record.value('clientPatrName')),
            'birthDate': forceDate(record.value('birthDate')),
            # BedProfile info
            'medProfile': forceString(record.value('medProfileName')),
            # Organisation info
            'orgName': forceString(record.value('orgName')),
            # OrgStructure info
            'orgStructName': forceString(record.value('orgStructName')),
            'ticketNumber': forceString(record.value('ticketNumber')),
            'cancelDate': forceString(record.value('cancelDate')),
            'cancelReason': db.translate(tableCancellation, tableCancellation['id'],
                                         forceString(record.value('cancelReason')), tableCancellation['name']),
        }

    def sort(self, column, order):
        if column not in xrange(len(self.cols())):
            return

        column = self.cols()[column]
        sortFieldName = column.fields()[0]
        if sortFieldName.endswith('DateString'):
            sortFieldName = sortFieldName[:-6]
        self.items.sort(key=lambda item: item.get(sortFieldName, None),
                        reverse=(order == QtCore.Qt.DescendingOrder))
        self.reset()


class CHistoryTableModel(CBaseHistoryModel):
    def __init__(self, parent, clientId):
        self.parentWidget = parent
        CBaseHistoryModel.__init__(self, parent)
        self.items = []
        self.idList = []
        self.formColumns()
        self.isColor = False
        self.clientId = clientId

    def data(self, index, role=QtCore.Qt.DisplayRole):
        return CBaseHistoryModel.data(self, index, role)

    def loadData(self, clientId):
        self.items = []
        db = QtGui.qApp.db

        queryTable, cond, cols = self.getCondAndQueryTable(clientId)
        records = db.getRecordList(queryTable, cols, cond)
        for record in records:
            item = self.getItemFromRecord(record)
            self.items.append(item)
        self.reset()

    def clear(self):
        self.items = []
        self.reset()


#########Utils##############

# Класс для хранения списка мо и профилями коек
class CBedPrifile():
    def __init__(self, mo):
        self.mo = mo
        self.allBeds = {}
        self.busyBeds = {}

    def addBeds(self, bedProfile, allBeds, busyBeds):
        if not bedProfile in self.allBeds:
            self.allBeds[bedProfile] = 0
        self.allBeds[bedProfile] += forceInt(allBeds)
        if not bedProfile in self.busyBeds:
            self.busyBeds[bedProfile] = 0
        self.busyBeds[bedProfile] += forceInt(busyBeds)

    def getMo(self):
        return self.mo

    def getAllBeds(self):
        return self.allBeds

    def getAllBedsByProfile(self, profile):
        if profile in self.allBeds:
            return self.allBeds[profile]

    def getBusyBeds(self):
        return self.busyBeds

    def getBusyBedsByProfile(self, profile):
        if profile in self.busyBeds:
            return self.busyBeds[profile]

    def getFreeBedsByProfile(self, profile):
        if profile in self.busyBeds and profile in self.allBeds:
            freeBeds = forceInt(self.getAllBedsByProfile(profile)) - forceInt(self.getBusyBedsByProfile(profile))
            return freeBeds
