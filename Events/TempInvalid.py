# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui, QtSql

from Events.MKBInfo import CMKBInfo
from Events.TempInvalidInfo import CTempInvalidDocTypeInfo, CTempInvalidExtraReasonInfo, CTempInvalidInfo, CTempInvalidPeriodInfoList, CTempInvalidReasonInfo
from Exchange.R78.FssLn.LnService import LnService
from Orgs.PersonComboBoxEx import CPersonFindInDocTableCol
from Orgs.Utils import getOrganisationShortName
from Registry.Utils import getClientWork
from Ui_TempInvalid import Ui_grpTempInvalid
from Users.Rights import urAdmin, urRefEditMedTempInvalidExpertKAK, urRegWriteInsurOfficeMark
from library.DialogBase import CConstructHelperMixin
from library.InDocTable import CBoolInDocTableCol, CDateInDocTableCol, CInDocTableCol, CInDocTableModel, CIntInDocTableCol, CRBInDocTableCol
from library.PrintInfo import CDateInfo
from library.Utils import forceBool, forceDate, forceInt, forceRef, forceString, forceStringEx, formatSex, toVariant
from library.interchange import getComboBoxValue, getLineEditValue, getRBComboBoxValue, getSpinBoxValue, \
    setComboBoxValue, setLineEditValue, setRBComboBoxValue, setSpinBoxValue, setWidgetValue, getWidgetValue
from library.Enum import CEnum


class Busyness(CEnum):
    u""" Занятость (TempInvalid.busyness) """
    NotSet = 0
    Main = 1
    Combine = 2
    Registered = 3

    nameMap = {
        NotSet    : u'не задано',
        Main      : u'основное',
        Combine   : u'совместитель',
        Registered: u'на учете',
    }


class CTempInvalid(QtGui.QGroupBox, CConstructHelperMixin, Ui_grpTempInvalid):
    def __init__(self, parent=None):
        QtGui.QGroupBox.__init__(self, parent)
        self.eventEditor = None
        self.modelTempInvalidPeriods = CTempInvalidPeriodModel(self)
        self.modelTempInvalidPeriods.setObjectName('modelTempInvalidPeriods')

        self.setupUi(self)

        self.cmbBusyness.setEnum(Busyness)
        self.tblTempInvalidPeriods.setModel(self.modelTempInvalidPeriods)
        self.tblTempInvalidPeriods.addPopupDelRow()

        self.tempInvalidRecord = None
        self.tempInvalidId = None
        self.tempInvalidProlonging = False
        self.prevTempInvalidId = None
        self.caseBegDate = None
        self.insuranceOfficeMark = None
        self.edtCaseBegDate.setDate(self.caseBegDate)
        self.edtCaseBegDate.setEnabled(False)
        # self.connect(self, QtCore.SIGNAL('clicked(bool)'), self.onClicked, QtCore.Qt.QueuedConnection)
        self.blankParams = {}
        self.defaultBlankMovingId = None

    def getBlankParams(self):
        self.defaultBlankMovingId = None
        self.blankParams = {}

        db = QtGui.qApp.db
        tableTempInvalid = db.table('TempInvalid')

        blankIdList = []
        docTypeId = self.cmbTempInvalidDoctype.value()
        if docTypeId:
            date = self.eventEditor.eventSetDateTime.date() if self.eventEditor.eventSetDateTime else None
            personId = self.eventEditor.personId

            tableBTI = db.table('rbBlankTempInvalids')
            tableBTIMoving = db.table('BlankTempInvalid_Moving')
            tableBTIParty = db.table('BlankTempInvalid_Party')
            tablePerson = db.table('Person')

            orgStructureId = None
            if personId:
                orgStructRecord = db.getRecordEx(tablePerson, [tablePerson['orgStructure_id']], [tablePerson['deleted'].eq(0),
                                                                                                 tablePerson['id'].eq(personId)])
                orgStructureId = forceRef(orgStructRecord.value('orgStructure_id')) if orgStructRecord else None
            cols = [tableBTIMoving['id'].alias('blankMovingId'),
                    tableBTI['checkingSerial'],
                    tableBTI['checkingNumber'],
                    tableBTI['checkingAmount'],
                    tableBTIParty['serial'],
                    tableBTIMoving['numberFrom'],
                    tableBTIMoving['numberTo'],
                    tableBTIMoving['returnAmount'],
                    tableBTIMoving['used'],
                    tableBTIMoving['received']]
            cond = [tableBTI['doctype_id'].eq(docTypeId),
                    tableBTIParty['deleted'].eq(0),
                    tableBTIMoving['deleted'].eq(0)]
            order = []
            if date:
                cond.append(tableBTIMoving['date'].le(date))
            orgStructureIdList = db.getTheseAndParents('OrgStructure', 'parent_id', [orgStructureId]) if orgStructureId else []
            if personId and orgStructureIdList:
                cond.append(db.joinOr([tableBTIMoving['person_id'].eq(personId),
                                       tableBTIMoving['orgStructure_id'].inlist(orgStructureIdList)]))
                order.append(tableBTIMoving['person_id'])
            elif personId:
                cond.append(tableBTIMoving['person_id'].eq(personId))
            elif orgStructureIdList:
                cond.append(tableBTIMoving['orgStructure_id'].inlist(orgStructureIdList))
            queryTable = tableBTI.innerJoin(tableBTIParty, tableBTIParty['doctype_id'].eq(tableBTI['id']))
            queryTable = queryTable.innerJoin(tableBTIMoving, tableBTIMoving['blankParty_id'].eq(tableBTIParty['id']))
            order.extend([tableBTI['checkingSerial'],
                          tableBTI['checkingNumber'],
                          tableBTI['checkingAmount'].desc()])
            for record in db.iterRecordList(queryTable, cols, cond, order):
                blankMovingId = forceRef(record.value('blankMovingId'))
                self.blankParams[blankMovingId] = {
                    'checkingSerial': forceInt(record.value('checkingSerial')),
                    'checkingNumber': forceInt(record.value('checkingNumber')),
                    'checkingAmount': forceInt(record.value('checkingAmount')),
                    'serial'        : forceString(record.value('serial')),
                    'numberFrom'    : forceInt(record.value('numberFrom')),
                    'numberTo'      : forceInt(record.value('numberTo')),
                    'returnAmount'  : forceInt(record.value('returnAmount')),
                    'used'          : forceInt(record.value('used')),
                    'received'      : forceInt(record.value('received'))
                }
                blankIdList.append(blankMovingId)
        # self.edtTempInvalidSerial.setTempInvalidBlankIdList(blankIdList)
        # if self.edtTempInvalidSerial.blankIdList:
        #     movingId = self.edtTempInvalidSerial.blankIdList[0]
        # else:
        # movingId = None
        # self.edtTempInvalidSerial.setValue(movingId)
        # if movingId:
        #     blankInfo = self.blankParams.get(movingId, None)
        #     if blankInfo:
        #         serial = forceString(blankInfo.get('serial', u''))
        #         numberFrom = blankInfo.get('numberFrom', 0)
        #         numberTo = blankInfo.get('numberTo', 0)
        #         returnAmount = forceInt(blankInfo.get('returnAmount', 0))
        #         used = forceInt(blankInfo.get('used', 0))
        #         received = forceInt(blankInfo.get('received', 0))
        #         balance = received - used - returnAmount
        #         if balance > 0:
        #             number = numberFrom + used + returnAmount + 1
        #             if number <= numberTo:
        #                 self.edtTempInvalidNumber.setText(forceString(number))
                        # record = db.getRecordEx(tableTempInvalid, [tableTempInvalid['id']], [tableTempInvalid['deleted'].eq(0), tableTempInvalid['serial'].eq(serial), tableTempInvalid['number'].eq(number)])
                        # if not record:
                        #     self.edtTempInvalidNumber.setText(forceString(number))

    def setEventEditor(self, eventEditor):
        self.eventEditor = eventEditor
        self.modelTempInvalidPeriods.setEventEditor(eventEditor)

    def setType(self, type_, docCode=None):
        self.type_ = type_
        self.docCode = docCode
        self.docId = forceRef(QtGui.qApp.db.translate('rbTempInvalidDocument', 'code', self.docCode, 'id')) if self.docCode else None
        filter = 'type=%d'%self.type_
        filierDoc = (filter+' AND code=\'%s\''%self.docCode) if self.docCode else filter
        self.cmbTempInvalidDoctype.setTable('rbTempInvalidDocument', False, filierDoc)
        self.cmbTempInvalidReason.setTable('rbTempInvalidReason', False, filter)
        self.cmbExtraReason.setTable('rbTempInvalidExtraReason', True, filter)
        self.modelTempInvalidPeriods.setType(self.type_)

        for widget in [self.lblTempInvalidOtherSex, self.cmbTempInvalidOtherSex,
                       self.lblTempInvalidOtherAge, self.edtTempInvalidOtherAge]:
            widget.setVisible(self.type_==0)
        if self.type_ == 0:
            self.cmbTempInvalidReason.setCode(QtGui.qApp.tempInvalidReason())
            if self.docCode:
                self.cmbTempInvalidDoctype.setEnabled(False)
                self.cmbTempInvalidDoctype.setValue(self.docId)

    @QtCore.pyqtSlot(int)
    def on_cmbTempInvalidDoctype_currentIndexChanged(self, index):
        self.getBlankParams()

    @QtCore.pyqtSlot()
    def on_btnNewLN_clicked(self):
        if forceString(QtGui.qApp.preferences.appPrefs['LNService']) and forceString(QtGui.qApp.preferences.appPrefs['LNAddress']):
            ex = LnService()
            number = ex.getNewLnNumber()
            if number:
                self.edtTempInvalidNumber.setText(number)
        else:
            QtGui.QMessageBox.warning(self, u'Ошибка', u'Сервис листов нетрудоспособности не настроен.')

    @QtCore.pyqtSlot()
    def on_btnSendInFss_clicked(self):
        self.saveTempInvalid()
        ex = LnService()
        if forceString(self.edtTempInvalidNumber.text()):
            if ex.prParseFilelnlpu(self.edtTempInvalidNumber.text()):
                QtGui.QMessageBox.information(self, u'Успешно', u'Лист нетрудоспособности успешно отправлен')
        else:
            QtGui.QMessageBox.warning(self, u'Ошибка', u'Не заполнен номер листа нетрудоспособности')
            return

    def pickupTempInvalid(self):
        db = QtGui.qApp.db
        tableTempInvalid = db.table('TempInvalid')
        condDeleted = tableTempInvalid['deleted'].eq(0)
        condClient = tableTempInvalid['client_id'].eq(self.eventEditor.clientId)
        condClosed = tableTempInvalid['closed'].eq(0)
        condDate = None
        if self.eventEditor.eventDate:
            condDate = db.joinAnd([
                tableTempInvalid['begDate'].le(self.eventEditor.eventDate),
                db.joinOr([
                    tableTempInvalid['endDate'].ge(self.eventEditor.eventSetDateTime),
                    tableTempInvalid['endDate'].isNull(),
                    tableTempInvalid['closed'].eq(0)
                ])
            ])
        elif self.eventEditor.eventSetDateTime:
            condDate = db.joinOr([
                tableTempInvalid['endDate'].isNull(),
                tableTempInvalid['endDate'].ge(self.eventEditor.eventSetDateTime),
                tableTempInvalid['closed'].eq(0)
            ])

        condType = tableTempInvalid['type'].eq(self.type_)
        if self.docCode:
            tableTempInvalidDocument = db.table('rbTempInvalidDocument')
            condDocCode = tableTempInvalidDocument['code'].eq(self.docCode)
            table = tableTempInvalid.leftJoin(tableTempInvalidDocument, tableTempInvalid['doctype_id'].eq(tableTempInvalidDocument['id']))
        else:
            condDocCode = None
            table = tableTempInvalid

        cond = [condDeleted, condType, condClient, condClosed]
        if condDate:
            cond.append(condDate)
        if condDocCode:
            cond.append(condDocCode)

        record = db.getRecordEx(table, 'TempInvalid.*', cond, 'endDate DESC')
        if not record:
            cond = [condDeleted, condType, condClient]
            if condDate:
                cond.append(condDate)
            if condDocCode:
                cond.append(condDocCode)
            record = db.getRecordEx(table, 'TempInvalid.*', cond, 'endDate DESC')

        if record:
            self.tempInvalidRecord = record
            self.insuranceOfficeMark = forceInt(record.value('insuranceOfficeMark'))
            self.tempInvalidId = forceRef(record.value('id'))
            setRBComboBoxValue(self.cmbTempInvalidDoctype, record, 'doctype_id')
            setRBComboBoxValue(self.cmbTempInvalidReason,  record, 'tempInvalidReason_id')
            setRBComboBoxValue(self.cmbExtraReason,  record, 'tempInvalidExtraReason_id')
            setWidgetValue(self.cmbBusyness, record, 'busyness')
            setLineEditValue(self.edtPlaceWork, record, 'placeWork')
            # setLineEditValue(self.edtTempInvalidSerial,    record, 'serial')
            setLineEditValue(self.edtTempInvalidNumber,    record, 'number')
            setComboBoxValue(self.cmbTempInvalidOtherSex,  record, 'sex')
            setSpinBoxValue(self.edtTempInvalidOtherAge,   record, 'age')
            self.setEnabledWidget(self.insuranceOfficeMark, [self.cmbTempInvalidDoctype, self.cmbTempInvalidReason, self.cmbExtraReason, self.edtTempInvalidNumber, self.tblTempInvalidPeriods])
            self.modelTempInvalidPeriods.loadItems(self.tempInvalidId)

            prevCond = [condDeleted, condClient, tableTempInvalid['closed'].eq(2), tableTempInvalid['endDate'].eq(forceDate(record.value('begDate')).addDays(-1))]
            prevRecord = db.getRecordEx(table, '*', prevCond, 'endDate DESC')
            self.setPrevTempInvalid(prevRecord)
            self.updateTempInvalidLength()
        else:
            self.tempInvalidRecord = None
            self.tempInvalidId = None
            self.setPrevTempInvalid(None)
            self.insuranceOfficeMark = None
        if record and forceInt(self.tempInvalidRecord.value('closed'))==2:
            self.btnTempInvalidProlong.setEnabled(False)
        self.tempInvalidProlonging = False
        self.defaultBlankMovingId = None

    def setPrevTempInvalid(self, prevTempInvalidRecord):
        if prevTempInvalidRecord:
            serial = forceString(prevTempInvalidRecord.value('serial'))
            number = forceString(prevTempInvalidRecord.value('number'))
            self.prevTempInvalidId = forceRef(prevTempInvalidRecord.value('id'))
            self.caseBegDate = forceDate(prevTempInvalidRecord.value('caseBegDate'))
        else:
            serial = ''
            number = ''
            self.prevTempInvalidId = None
            self.caseBegDate = None
        self.lblTempInvalidPrevSerialValue.setText(serial)
        self.lblTempInvalidPrevNumberValue.setText(number)
        self.edtCaseBegDate.setDate(self.caseBegDate)
        self.edtCaseBegDate.setEnabled(False)

    def newTempInvalid(self, begDate):
        self.tempInvalidRecord = None
        self.tempInvalidId = None
        self.insuranceOfficeMark = None
        self.btnTempInvalidProlong.setEnabled(not self.tempInvalidProlonging)
        self.tempInvalidProlonging = False
        self.modelTempInvalidPeriods.clearItems()
        self.modelTempInvalidPeriods.addStart(begDate)
        self.edtTempInvalidNumber.setText('')
        self.updateTempInvalidLength()

    def checkTempInvalidSerialNumber(self, editor, docTypeId = None):
        return True
        # result = True
        # serial = self.edtTempInvalidSerial.text()
        # number = self.edtTempInvalidNumber.text()
        # if len(serial) > 0 or len(number) > 0:
        #     db = QtGui.qApp.db
        #     table = db.table('TempInvalid')
        #     cond =[table['id'].ne(self.tempInvalidId),
        #            table['doctype_id'].eq(docTypeId)]
        #     if len(serial) > 0:
        #         cond.append(table['serial'].eq(serial))
        #     if len(number) > 0:
        #         cond.append(table['number'].eq(number))
        #     recordNumber = db.getRecordEx(table, 'id, serial, number', cond)
        #     if recordNumber:
        #         serialRecord = forceString(recordNumber.value('serial'))
        #         numberRecord = forceString(recordNumber.value('number'))
        #         if len(serialRecord) > 0 and len(numberRecord) > 0:
        #             message = u'Серия и номер: %s %s, документа ВУТ не уникальны' % (serialRecord, numberRecord)
        #         elif len(serialRecord) > 0:
        #             message = u'Серия: %s, документа ВУТ не уникальна' % (serialRecord)
        #         elif len(numberRecord) > 0:
        #             message = u'Номер: %s, документа ВУТ не уникален' % (numberRecord)
        #
        #         result = result and editor.checkValueMessage(message, True, self.edtTempInvalidNumber)
        # return result

    def checkBlankSerialNumberAmount(self, editor):
        return True
        # self.defaultBlankMovingId = None
        # result = True
        # blankMovingId = self.edtTempInvalidSerial.value()
        # serial = forceString(self.edtTempInvalidSerial.text())
        # number = forceInt(toVariant(self.edtTempInvalidNumber.text()))
        # if blankMovingId:
        #     blankInfo = self.blankParams.get(blankMovingId, {})
        #     if blankInfo:
        #         result = self.checkBlankParams(blankInfo, result, serial, editor, blankMovingId, number)
        # elif serial:
        #     for movingId, blankInfo in self.blankParams.items():
        #         serialCache = forceString(blankInfo.get('serial', u''))
        #         if serial == serialCache:
        #             result = self.checkBlankParams(blankInfo, result, serial, editor, movingId, number)
        #             if result:
        #                 self.defaultBlankMovingId = movingId
        #             return result
        # return result

    def checkBlankParams(self, blankInfo, result, serial, editor, blankMovingId, number):
        db = QtGui.qApp.db
        tableBlankTempInvalidMoving = db.table('BlankTempInvalid_Moving')
        # checkingSerialCache = forceInt(toVariant(blankInfo.get('checkingSerial', 0)))
        # serialCache = forceString(blankInfo.get('serial', u''))
        # if checkingSerialCache:
        #     result = result and (serialCache == serial or editor.checkValueMessage(u'Серия не соответсвует документу', True if checkingSerialCache == 1 else False, self.edtTempInvalidSerial))
        if result:
            checkingNumberCache = forceInt(toVariant(blankInfo.get('checkingNumber', 0)))
            if checkingNumberCache:
                numberFromCache = forceInt(toVariant(blankInfo.get('numberFrom', u'')))
                numberToCache = forceInt(toVariant(blankInfo.get('numberTo', u'')))
                result = result and ((number >= numberFromCache and  number <= numberToCache) or editor.checkValueMessage(u'Номер не соответсвует диапазону номеров документа', True if checkingNumberCache == 1 else False, self.edtTempInvalidNumber))
        if result:
            checkingAmountCache = forceInt(toVariant(blankInfo.get('checkingAmount', 0)))
            if checkingAmountCache:
                record = db.getRecordEx(tableBlankTempInvalidMoving, [tableBlankTempInvalidMoving['returnAmount'], tableBlankTempInvalidMoving['used'], tableBlankTempInvalidMoving['received']], [tableBlankTempInvalidMoving['deleted'].eq(0), tableBlankTempInvalidMoving['id'].eq(blankMovingId)])
                returnAmount = forceInt(record.value('returnAmount'))
                used = forceInt(record.value('used'))
                received = forceInt(record.value('received'))
                balance = received - used - returnAmount
                result = result # and (balance > 0 or editor.checkValueMessage(u'В партии закончились соответствующие документы', True if checkingAmountCache == 1 else False, self.edtTempInvalidSerial))
        return result

    def checkTempInvalidDataEntered(self):
        if self.isChecked():
            editor = self.eventEditor
            result = True
            docCode = self.cmbTempInvalidDoctype.code()
            tempInvalidReasonId = self.cmbTempInvalidReason.value()
            result = result and (docCode or editor.checkInputMessage(u'тип документа', False, self.cmbTempInvalidDoctype))
            result = result and (tempInvalidReasonId or editor.checkInputMessage(u'причину', False, self.cmbTempInvalidReason))
#            if self.type_==0 and docCode == '1' : # листок нетрудоспособности
#                result = result and (forceStringEx(self.edtTempInvalidSerial.text()) or editor.checkInputMessage(u'серию', True, self.edtTempInvalidSerial))
            result = result and (forceStringEx(self.edtTempInvalidNumber.text()) or editor.checkInputMessage(u'номер', True, self.edtTempInvalidNumber))
            result = result and self.checkTempInvalidSerialNumber(editor, docCode)
            result = result and self.checkBlankSerialNumberAmount(editor)
            if requiredOtherPerson(tempInvalidReasonId):
                result = result and (self.cmbTempInvalidOtherSex.currentIndex() or editor.checkInputMessage(u'пол', False, self.cmbTempInvalidOtherSex))
                result = result and (self.edtTempInvalidOtherAge.value() or editor.checkInputMessage(u'возраст', False, self.edtTempInvalidOtherAge))

            items = self.modelTempInvalidPeriods.items()
            result = result and (len(items) or editor.checkInputMessage(u'период', False, self.tblTempInvalidPeriods, 0, 0))
            if not result:
                return
            date = None
            for row, record in enumerate(items):
                date, recordOk = self.checkTempInvalidPeriodDataEntered(date, row, record)
                if not recordOk:
                    return False

            db = QtGui.qApp.db
            table = db.table('TempInvalid')
            # проверка на 2 или более листов трудоспособности у пациента за период
            cond = [
                table['client_id'].eq(self.clientId),
                table['deleted'].eq(0),
                table['endDate'].eq('0000-00-00')
            ]
            stmt = 'SELECT ' + db.existsStmt(table, cond)
            query = db.query(stmt)
            if query.first():
                anotherClientTempInvalid = forceBool(query.record().value(0))
                if anotherClientTempInvalid:
                    return self.checkValueMessage(
                        u'Этот пациент уже имееть незакрытый листок ВУТ', False, self.tblPeriods, 0, 0
                    )

            # проверка отсутствия пересекающихся периодов нетрудоспособности, если не совместитель
            if self.cmbBusyness.value() != Busyness.Combine:
                begDate = self.modelTempInvalidPeriods.begDate()
                endDate = self.modelTempInvalidPeriods.endDate()

                cond = [table['begDate'].between(begDate, endDate),
                        table['endDate'].between(begDate, endDate),
                        db.joinAnd([table['begDate'].le(begDate), table['endDate'].ge(begDate)]),
                        db.joinAnd([table['begDate'].le(endDate), table['endDate'].ge(endDate)]), # а на бумажке рисую - вроде-бы и не нужно...
                       ]
                cond = [db.joinOr(cond)]
                if self.tempInvalidId:
                    cond.append(table['id'].ne(self.tempInvalidId))
                cond.append(table['client_id'].eq(editor.clientId))
                cond.append(table['deleted'].eq(0))
    ###            cond.append(table['type'].eq(self.type_)) # т.к. doctype_id ограничит сильнее.
                cond.append(table['doctype_id'].eq(self.cmbTempInvalidDoctype.value()))

                stmt = 'SELECT '+db.existsStmt(table, cond)+' AS X';
                query = db.query(stmt)
                if query.first():
                    present = forceBool(query.record().value(0))
                    if present:
                        result = editor.checkValueMessage(u'Период нетрудоспособности пересекается с существующим', False, self.tblTempInvalidPeriods, 0, 0)
                        return False
            return self.checkTempInvalidPeriodsDateKAKEntered(editor, tempInvalidReasonId)

        return True

    def checkTempInvalidPeriodDataEntered(self, prevPerionEndDate, row, record):
        editor = self.eventEditor
        begDateIndex = record.indexOf('begDate')
        endDateIndex = record.indexOf('endDate')
        resultIndex  = record.indexOf('result_id')
        begDate = forceDate(record.value(begDateIndex))
        endDate = forceDate(record.value(endDateIndex))
        resultId = forceRef(record.value(resultIndex))
        result = True
        if result and (not begDate or begDate.isNull()):
            result = editor.checkValueMessage(u'Не заполнена дата начала периода', False, self.tblTempInvalidPeriods, row, begDateIndex)
        if result and (prevPerionEndDate and prevPerionEndDate.daysTo(begDate) != 1):
            result = editor.checkValueMessage(u'Недопустимая дата начала периода', False, self.tblTempInvalidPeriods, row, begDateIndex)
        #В соответствии с Приказом Минздравсоцразвития России от 29.06.2011 N 624н
        #Больничный лист может выдаваться на руки без даты закрытия, так что проверка на дату закрытия не актуальна
        #if result and (not endDate or endDate.isNull()):
        #    result = editor.checkValueMessage(u'Не заполнена дата окончания периода', False, self.tblTempInvalidPeriods, row, endDateIndex)
        if result and endDate and not endDate.isNull() and (begDate.daysTo(endDate)<0):
            result = editor.checkValueMessage(u'Недопустимая дата окончания периода', False, self.tblTempInvalidPeriods, row, endDateIndex)
        if result and (not resultId):
            result = editor.checkValueMessage(u'Не заполнен результат периода', False, self.tblTempInvalidPeriods, row, resultIndex)
        return endDate, result

    def checkTempInvalidPeriodsDateKAKEntered(self, editor, tempInvalidReasonId):
        db = QtGui.qApp.db
        table = db.table('rbTempInvalidReason')
        tableTempInvalid = db.table('TempInvalid')
        tableTempInvalidPeriod = db.table('TempInvalid_Period')
        recordReason = db.getRecordEx(table, [table['restriction']], [table['id'].eq(tempInvalidReasonId)])
        restriction = forceInt(recordReason.value('restriction')) if recordReason else 0
        if restriction:
            itemsPrev = []
            if self.prevTempInvalidId:
                prevId = self.prevTempInvalidId
                tempInvalidIdList = []
                while prevId:
                    cond = [tableTempInvalid['prev_id'].isNotNull(),
                            tableTempInvalid['id'].eq(prevId),
                            tableTempInvalid['deleted'].eq(0),
                            tableTempInvalid['doctype_id'].eq(self.cmbTempInvalidDoctype.value())
                            ]
                    if self.eventEditor.clientId:
                        cond.append(tableTempInvalid['client_id'].eq(self.eventEditor.clientId))
                    cond.append(u'TempInvalid.closed = 2 OR TempInvalid.closed = 0')
                    stmt = db.selectDistinctStmt(tableTempInvalid, [tableTempInvalid['prev_id']], cond, '', None)
                    query = db.query(stmt)
                    prevId = None
                    while query.next():
                        prevId = query.value(0).toInt()[0]
                        if prevId and prevId not in tempInvalidIdList:
                            tempInvalidIdList.append(prevId)
                if self.prevTempInvalidId not in tempInvalidIdList:
                    tempInvalidIdList.append(self.prevTempInvalidId)
                if tempInvalidIdList:
                    prevRecords = db.getRecordListGroupBy(tableTempInvalidPeriod, u'TempInvalid_Period.*', [tableTempInvalidPeriod['master_id'].inlist(tempInvalidIdList)], u'TempInvalid_Period.id', u'TempInvalid_Period.begDate')
                    for recordPrev in prevRecords:
                        itemsPrev.append(recordPrev)
            items = self.modelTempInvalidPeriods.items()
            if itemsPrev:
                for item in items:
                    itemsPrev.append(item)
            else:
                itemsPrev = items
            date = None
            durationSum = 0
            begDate = None
            for row, record in enumerate(itemsPrev):
                begDateDur = forceDate(record.value('begDate'))
                endDateDur = forceDate(record.value('endDate'))
                duration = begDateDur.daysTo(endDateDur)+1 if begDateDur and endDateDur and begDateDur <= endDateDur else 0
                directDateOnKAK = forceDate(record.value('directDateOnKAK'))
                isExternal = forceBool(record.value('isExternal'))
                directDateOnKAKIndex = record.indexOf('directDateOnKAK')
                resultId = forceRef(record.value('result_id'))
                able = forceBool(db.translate('rbTempInvalidResult', 'id', resultId, 'able'))
                if able or directDateOnKAK or isExternal:
                    durationSum = 0
                    begDate = None
                else:
                    durationSum += duration
                    if not begDate:
                        begDate = forceDate(record.value('begDate'))
            if durationSum and restriction < durationSum:
                if begDate:
                    newDirectDateOnKAK = begDate.addDays(restriction - 1)
                result = editor.checkValueMessage(u'Необходимо направить на КЭК%s'%((u', предположительная дата напрвления на КЭК %s'%(newDirectDateOnKAK.toString('dd.MM.yyyy'))) if newDirectDateOnKAK else u''), False, self.tblTempInvalidPeriods, len(items)-1, directDateOnKAKIndex)
                if newDirectDateOnKAK:
                    record.setValue('directDateOnKAK', toVariant(newDirectDateOnKAK))
                return result
        return True

    def saveTempInvalid(self):
        if self.isChecked():
            diagnosisId = self.eventEditor.getFinalDiagnosisId()

            db = QtGui.qApp.db
            table = db.table('TempInvalid')
            tableBlankTempInvalidMoving = db.table('BlankTempInvalid_Moving')
            if not self.tempInvalidId:
                record = table.newRecord()
                self.tempInvalidRecord = record
                record.setValue('type', toVariant(self.type_))
                record.setValue('client_id', toVariant(self.eventEditor.clientId))
            else:
                record = self.tempInvalidRecord
            getRBComboBoxValue(self.cmbTempInvalidDoctype, record, 'doctype_id')
            getRBComboBoxValue(self.cmbTempInvalidReason,  record, 'tempInvalidReason_id')
            getRBComboBoxValue(self.cmbExtraReason,  record, 'tempInvalidExtraReason_id')
            getWidgetValue(self.cmbBusyness, record, 'busyness')
            getLineEditValue(self.edtPlaceWork, record, 'placeWork')
            # getLineEditValue(self.edtTempInvalidSerial,    record, 'serial')
            getLineEditValue(self.edtTempInvalidNumber,    record, 'number')
            getComboBoxValue(self.cmbTempInvalidOtherSex,  record, 'sex')
            getSpinBoxValue(self.edtTempInvalidOtherAge,   record, 'age')
            fullLength, externalLength = self.modelTempInvalidPeriods.calcLengths()
            record.setValue('begDate',  toVariant(self.modelTempInvalidPeriods.begDate()))
            record.setValue('endDate',  toVariant(self.modelTempInvalidPeriods.endDate()))
            record.setValue('duration', toVariant(fullLength))
            if self.tempInvalidProlonging or forceInt(record.value('closed'))==2:
                closed = 2
            else:
                closed = self.modelTempInvalidPeriods.getTempInvalidClosedStatus()
            record.setValue('closed',   toVariant(closed))
            if requiredDiagnosis(self.cmbTempInvalidReason.value()):
                if diagnosisId:
                    record.setValue('diagnosis_id', toVariant(diagnosisId))
            else:
                record.setValue('diagnosis_id', QtCore.QVariant())
            record.setValue('person_id', toVariant(self.modelTempInvalidPeriods.lastPerson()))
            record.setValue('prev_id', toVariant(self.prevTempInvalidId))
            if not self.caseBegDate:
                self.caseBegDate = self.modelTempInvalidPeriods.begDate()
            record.setValue('caseBegDate', toVariant(self.caseBegDate))
            self.tempInvalidId = db.insertOrUpdate(table, record)
            record.setValue('id', toVariant(self.tempInvalidId))
            self.modelTempInvalidPeriods.saveItems(self.tempInvalidId)
            # if not self.defaultBlankMovingId:
            #     blankMovingId = self.edtTempInvalidSerial.value()
            # else:
            #     blankMovingId = self.defaultBlankMovingId
            # if blankMovingId:
            #     recordMoving = db.getRecordEx(tableBlankTempInvalidMoving, u'*', [tableBlankTempInvalidMoving['deleted'].eq(0), tableBlankTempInvalidMoving['id'].eq(blankMovingId)])
            #     if recordMoving:
            #         used = forceInt(recordMoving.value('used'))
            #         recordMoving.setValue('used', toVariant(used + 1))
            #         db.updateRecord(tableBlankTempInvalidMoving, recordMoving)

    def getTempInvalidInfo(self, context):
        result = context.getInstance(CTempInvalidInfo, None)
        if self.isChecked():
            result._doctype = context.getInstance(CTempInvalidDocTypeInfo,  self.cmbTempInvalidDoctype.value())
            result._reason  = context.getInstance(CTempInvalidReasonInfo,  self.cmbTempInvalidReason.value())
            result._extraReason  = context.getInstance(CTempInvalidExtraReasonInfo, forceRef(self.cmbExtraReason.value()))
            result._busyness = forceInt(self.cmbBusyness.value())
            result._placeWork = forceString(self.edtPlaceWork.text())
            # result._serial  = forceStringEx(self.edtTempInvalidSerial.text())
            result._number  = forceStringEx(self.edtTempInvalidNumber.text())
            result._sex     = formatSex(self.cmbTempInvalidOtherSex.currentIndex())
            result._age     = self.edtTempInvalidOtherAge.value()
            result._duration, result._externalDuration = self.modelTempInvalidPeriods.calcLengths()
            result._begDate = CDateInfo(self.modelTempInvalidPeriods.begDate())
            result._endDate = CDateInfo(self.modelTempInvalidPeriods.endDate())
            MKB, MKBEx = self.eventEditor.getFinalDiagnosisMKB()
            result._MKB = context.getInstance(CMKBInfo, MKB)
            result._MKBEx = context.getInstance(CMKBInfo, MKBEx)
            closed = self.modelTempInvalidPeriods.getTempInvalidClosedStatus()
            result._closed = closed
            result._periods = self.modelTempInvalidPeriods.getPeriodsInfo(context)
            if self.prevTempInvalidId:
                result._prev = context.getInstance(CTempInvalidInfo, self.prevTempInvalidId)
            else:
                result._prev = None
            result._ok = True
        else:
            result._ok = False
        result._loaded = True
        return result

    def setOrgId(self, orgId):
        self.cmbAPPerson.setOrgId(orgId)

    def updateTempInvalidLength(self):
        fullLength, externalLength = self.modelTempInvalidPeriods.calcLengths()
        self.lblTempInvalidLengthValue.setText(str(fullLength))
        self.lblTempInvalidExternalLengthValue.setText(str(externalLength))
        if self.caseBegDate:
            caseLength = self.caseBegDate.daysTo(self.modelTempInvalidPeriods.begDate())+fullLength
        else:
            caseLength = fullLength
        self.lblTempInvalidCaseLengthValue.setText(str(caseLength))

    # def onClicked(self, checked):
    #     if checked:
    #         # self.getBlankParams()
    #         if self.eventEditor.clientId and not self.edtPlaceWork.text() and 0<=self.cmbBusyness.currentIndex()<=1:
    #             work = getClientWork(self.eventEditor.clientId)
    #             if work:
    #                 self.edtPlaceWork.setText(formatWorkTempInvalid(work))
    #                 self.cmbBusyness.setCurrentIndex(1)
    #         if self.tempInvalidId:
    #             self.tblTempInvalidPeriods.setFocus(QtCore.Qt.OtherFocusReason)
    #         else:
    #             self.cmbTempInvalidDoctype.setFocus(QtCore.Qt.OtherFocusReason)
    #         self.setEnabledWidget(self.insuranceOfficeMark, [self.cmbTempInvalidDoctype, self.cmbTempInvalidReason, self.cmbExtraReason, self.edtTempInvalidNumber, self.tblTempInvalidPeriods])

    def setEnabledWidget(self, checked, listWidget=None):
        if not listWidget:
            listWidget = []
        enabled = QtGui.qApp.userHasRight(urRegWriteInsurOfficeMark)
        if self.isChecked():
            self.cmbTempInvalidReason.setFocus(QtCore.Qt.TabFocusReason)
            otherPersonEnabled = requiredOtherPerson(self.cmbTempInvalidReason.value())
        else:
            otherPersonEnabled = False
        if checked and self.isChecked():
            for widget in listWidget:
                widget.setEnabled(enabled)
            self.cmbTempInvalidOtherSex.setEnabled(otherPersonEnabled and enabled)
            self.edtTempInvalidOtherAge.setEnabled(otherPersonEnabled and enabled)
            if self.btnTempInvalidProlong.isEnabled():
                self.btnTempInvalidProlong.setEnabled(enabled)
        elif (not checked) and self.isChecked():
            self.cmbTempInvalidOtherSex.setEnabled(otherPersonEnabled)
            self.edtTempInvalidOtherAge.setEnabled(otherPersonEnabled)

    @QtCore.pyqtSlot(int)
    def on_cmbTempInvalidReason_currentIndexChanged(self, index):
        self.setEnabledWidget(self.insuranceOfficeMark, [self.cmbTempInvalidDoctype, self.cmbTempInvalidReason, self.cmbExtraReason, self.edtTempInvalidNumber, self.tblTempInvalidPeriods])

    @QtCore.pyqtSlot()
    def on_btnTempInvalidProlong_clicked(self):
        editor = self.eventEditor
        if not editor.checkDataEntered():
            return

        self.tempInvalidProlonging = True
        if not self.eventEditor.save():
            self.tempInvalidProlonging = False
            return

        self.setPrevTempInvalid(self.tempInvalidRecord)
        self.newTempInvalid(forceDate(self.tempInvalidRecord.value('endDate')).addDays(1))

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_modelTempInvalidPeriods_dataChanged(self, topLeft, bottomRight):
        self.updateTempInvalidLength()
        closed = self.modelTempInvalidPeriods.getTempInvalidClosedStatus()
        self.btnTempInvalidProlong.setEnabled(closed == 0)


class CTempInvalidPeriodModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'TempInvalid_Period', 'id', 'master_id', parent)
        self.begPersonCol = CPersonFindInDocTableCol(u'Начавший',   'begPerson_id',  20, 'vrbPersonWithSpeciality', order = 'name')
        self.endPersonCol = CPersonFindInDocTableCol(u'Закончивший','endPerson_id',  20, 'vrbPersonWithSpeciality', order = 'name')
        self.addCol(CDateInDocTableCol(u'Начало',    'begDate', 10))
        self.addCol(CDateInDocTableCol(u'Окончание', 'endDate', 10))
        self.addExtCol(CIntInDocTableCol(u'Длительность', 'duration', 10, high=999), QtCore.QVariant.Int).setReadOnly(not QtGui.qApp.userSpecialityId)
        self.colResult = self.addCol(CRBInDocTableCol(  u'Результат', 'result_id', 10, 'rbTempInvalidResult', prefferedWidth=150))
        self.addCol(self.endPersonCol)
        self.colRegime = self.addCol(CRBInDocTableCol(  u'Режим',     'regime_id', 10, 'rbTempInvalidRegime', prefferedWidth=150))
        self.colBreak  = self.addCol(CRBInDocTableCol(  u'Нарушение', 'break_id',  10, 'rbTempInvalidBreak', prefferedWidth=200 ))
        self.addCol(CDateInDocTableCol(u'Дата нарушения', 'breakDate', 15, prefferedWidth=200))
        self.addCol(CInDocTableCol(u'Примечание', 'note', 15, prefferedWidth=200))
        self.addCol(CBoolInDocTableCol(u'Внешний', 'isExternal', 3))
        self.addCol(self.begPersonCol)
        self.addCol(CDateInDocTableCol(u'Направлен на КЭК', 'directDateOnKAK', 10, canBeEmpty=True))
        self.addCol(CDateInDocTableCol(u'Дата КЭК', 'dateKAK', 10, canBeEmpty=True)).setReadOnly(not QtGui.qApp.userHasAnyRight([urAdmin, urRefEditMedTempInvalidExpertKAK]))
        self.addCol(CPersonFindInDocTableCol(u'Эксперт','expert_id',  20, 'vrbPersonWithSpeciality', order = 'name').setReadOnly(not QtGui.qApp.userHasAnyRight([urAdmin, urRefEditMedTempInvalidExpertKAK])))
        self.addCol(CInDocTableCol(u'Номер путевки', 'numberPermit',    22))
        self.addCol(CDateInDocTableCol(u'Дата1', 'begDatePermit', 10))
        self.addCol(CDateInDocTableCol(u'Дата2', 'endDatePermit', 10))
        self.addCol(CRBInDocTableCol(u'Группа инвалидности', 'disability_id', 10, 'rbTempInvalidRegime', filter='type=1', prefferedWidth=150))
        self.addCol(CDateInDocTableCol(u'Дата поступления в стационар', 'begDateHospital', 30, prefferedWidth=300))
        self.addCol(CDateInDocTableCol(u'Дата выписки из стационара', 'endDateHospital', 30, prefferedWidth=300))
        self.eventEditor = None

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        result = CInDocTableModel.setData(self, index, value, role)
        if result and role == QtCore.Qt.EditRole:
            row = index.row()
            column = index.column()
            fieldName = self.cols()[column].fieldName()
            if fieldName == 'begDate' or fieldName == 'endDate': # начало или окончание
                begDate = forceDate(self.value(row, 'begDate'))
                endDate = forceDate(self.value(row, 'endDate'))
                duration = self._calcDuration(begDate, endDate)
                self.setValue(row, 'duration', duration)
            elif fieldName == 'duration': # длительность
                duration = forceInt(self.value(row, 'duration'))
                if duration>0:
                    begDate = forceDate(self.value(row, 'begDate'))
                    endDate = forceDate(self.value(row, 'endDate'))
                    if begDate:
                        self.setValue(row, 'endDate',  begDate.addDays(duration-1))
                    elif endDate:
                        self.setValue(row, 'begDate',  endDate.addDays(1-duration))
            elif fieldName == 'dateKAK': # Дата КЭК
                expertId = forceRef(self.value(row, 'expert_id'))
                dateKAK = forceDate(self.value(row, 'dateKAK'))
                if not expertId and dateKAK:
                    self.setValue(row, 'expert_id', toVariant(QtGui.qApp.userId))
            elif fieldName == 'break_id':
                if forceInt(self.value(row, 'break_id')) == 0:
                    self.setValue(row, 'breakDate', CDateInfo())
        return result

    def cellReadOnly(self, index):
        row = index.row()
        column = index.column()
        fieldName = self.cols()[column].fieldName()
        if fieldName == 'breakDate': #Дата нарушения. Можно выставить, только если есть нарушение
            if forceInt(self.value(row, 'break_id')) == 0:
                return True
        return False

    def loadItems(self, masterId):
        CInDocTableModel.loadItems(self, masterId)
        for item in self.items():
            begDate = forceDate(item.value('begDate'))
            endDate = forceDate(item.value('endDate'))
            duration = self._calcDuration(begDate, endDate)
            if not item.contains('duration'):
                fieldDuration = QtSql.QSqlField('duration', QtCore.QVariant.Int)
                item.append(fieldDuration)
            item.setValue('duration', toVariant(duration))

    def setEventEditor(self, eventEditor):
        self.eventEditor = eventEditor

    def setType(self, type_):
        filter = 'type=%d' % type_
        self.colResult.filter = filter
        self.colRegime.filter = filter

    def getEmptyRecord(self):
        result = CInDocTableModel.getEmptyRecord(self)
        result.setValue('begPerson_id',  toVariant(self.eventEditor.personId))
        result.setValue('endPerson_id',  toVariant(self.eventEditor.personId))
        return result

    def _calcDuration(self, begDate, endDate):
        return begDate.daysTo(endDate)+1 if begDate and endDate and begDate <= endDate else 0

    def calcLengths(self):
        internalLength = 0
        externalLength = 0
        for record in self.items():
            isExternal = forceBool(record.value('isExternal'))
            begDate = forceDate(record.value('begDate'))
            endDate = forceDate(record.value('endDate'))
            length = self._calcDuration(begDate, endDate)
            if isExternal:
                externalLength += length
            else:
                internalLength += length
        return internalLength+externalLength, externalLength

    def begDate(self):
        items = self.items()
        if items:
            firstRecord = items[0]
            return forceDate(firstRecord.value('begDate'))
        else:
            return None

    def endDate(self):
        items = self.items()
        if items:
            lastRecord = items[-1]
            return forceDate(lastRecord.value('endDate'))
        else:
            return None

    def getTempInvalidClosedStatus(self):
        items = self.items()
        if items:
            lastRecord = items[-1]
            resultId = forceRef(lastRecord.value('result_id'))
            if resultId:
                return forceInt(QtGui.qApp.db.translate('rbTempInvalidResult', 'id', resultId, 'closed'))
        return 0

    def lastPerson(self):
        result = None
        items = self.items()
        if items:
            lastRecord = items[-1]
            result = forceRef(lastRecord.value('endPerson_id'))
            if not result:
                result = forceRef(lastRecord.value('begPerson_id'))
        return result

    def addStart(self, begDate):
        item = self.getEmptyRecord()
        item.setValue('begDate', toVariant(begDate))
        self.items().append(item)
        self.reset()

    def getPeriodsInfo(self, context):
        result = context.getInstance(CTempInvalidPeriodInfoList, None)
        for i, item in enumerate(self.items()):
            id = forceRef(item.value('id'))
            result.addItem(id or -i-1, item)
        return result


def requiredOtherPerson(tempInvalidReasonId):
    grouping = forceInt(QtGui.qApp.db.translate('rbTempInvalidReason', 'id', tempInvalidReasonId, 'grouping'))
    return grouping == 1


def requiredDiagnosis(tempInvalidReasonId):
    return forceBool(QtGui.qApp.db.translate('rbTempInvalidReason', 'id', tempInvalidReasonId, 'requiredDiagnosis'))


def formatWorkTempInvalid(workRecord):
    if workRecord:
        orgId = forceRef(workRecord.value('org_id'))
        if orgId:
            orgShortName = getOrganisationShortName(orgId)
        else:
            orgShortName = forceString(workRecord.value('freeInput'))
    else:
        orgShortName = ''
    return orgShortName
