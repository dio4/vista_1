# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from library.AgeSelector import checkAgeSelector, parseAgeSelector
from library.DialogBase import CDialogBase
from library.Utils import agreeNumberAndWord, calcAgeTuple, forceDate, forceInt, forceRef, forceString, toVariant
from .ClientAttachReport import CAttachedClientsCountReport
from .Ui_CreateAttachClientsForAreaDialog import Ui_CreateAttachClientsForAreaDialog
from .Utils import CAttachType, getOrgStructureName


class CCreateAttachClientsForArea(CDialogBase, Ui_CreateAttachClientsForAreaDialog):
    def __init__(self, parent=None):
        super(CCreateAttachClientsForArea, self).__init__(parent)
        self.db = QtGui.qApp.db
        self.patientRequired = False
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setupUi(self)

        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())

        self.cmbFromOrgStructure.model().setFilter(self.clientAttachMonitoring.getOrgStructureSectionFilter())
        self.cmbToOrgStructure.model().setFilter(self.clientAttachMonitoring.getOrgStructureSectionFilter())

        self.progressBar.setFormat('%p%')
        self.progressBar.setValue(0)
        self.stopped = False

    @QtCore.pyqtSlot()
    def on_btnClose_clicked(self):
        self.stopped = True
        self.close()

    @QtCore.pyqtSlot()
    def on_btnStart_clicked(self):
        self.setAllEnabled(False)
        if self.rbtnByAddress.isChecked():
            self.createAttaches()
        else:
            self.moveAttaches()
        self.setAllEnabled(True)

    @QtCore.pyqtSlot()
    def on_btnPrint_clicked(self):
        CAttachedClientsCountReport(self).exec_()

    def setAllEnabled(self, enabled):
        self.frmFilters.setEnabled(enabled)

    def getOrgStructureIdList(self, treeIndex):
        treeItem = treeIndex.internalPointer() if treeIndex.isValid() else None
        return treeItem.getItemIdList() if treeItem else []

    def getRBNetValues(self):
        db = QtGui.qApp.db
        recordList = db.getRecordList('rbNet')
        self.nets = {}
        for record in recordList:
            netId = forceRef(record.value('id'))
            netSex = forceInt(record.value('sex'))
            netAge = forceString(record.value('age'))
            self.nets[netId] = {'sex': netSex, 'ageSelector': parseAgeSelector(netAge)}

    def createAttaches(self):
        self.logBrowser.append(u'Начинаем процесс прикрепления\n')
        self.logBrowser.append(u'Определение параметров\n')
        self.getRBNetValues()
        orgStructureIdList = self.getOrgStructureIdList(self.cmbOrgStructure._model.index(self.cmbOrgStructure.currentIndex(), 0, self.cmbOrgStructure.rootModelIndex()))
        areaAddressType = self.cmbAreaAddressType.currentIndex()
        self.attachByNet = self.cmbAttachBy.currentIndex() in [0, 1]
        self.attachByAreaType = self.cmbAttachBy.currentIndex() in [0, 2]
        db = QtGui.qApp.db
        tableOrgStructureAddress = db.table('OrgStructure_Address')
        tableOrgStructure = db.table('OrgStructure')
        tableClient = db.table('Client')
        tableClientAttach = db.table('ClientAttach')
        tableAttachType = db.table('rbAttachType')
        tableClientAddress = db.table('ClientAddress')
        tableAddress = db.table('Address')

        houseIdList = db.getDistinctIdList(tableOrgStructureAddress, tableOrgStructureAddress['house_id'], [tableOrgStructureAddress['master_id'].inlist(orgStructureIdList)])

        cols = [tableOrgStructureAddress['master_id'],
                tableOrgStructureAddress['house_id'],
                tableOrgStructure['organisation_id'],
                tableOrgStructure['net_id'],
                tableOrgStructure['isArea'],
                tableOrgStructure['parent_id']
                ]
        records = db.getRecordList(tableOrgStructureAddress.innerJoin(tableOrgStructure, tableOrgStructureAddress['master_id'].eq(tableOrgStructure['id'])), cols, [tableOrgStructureAddress['house_id'].inlist(houseIdList)])
        houseIdList = {}
        for record in records:
            houseMasterInfoList = {}
            masterId = forceRef(record.value('master_id'))
            houseMasterInfoList['masterId'] = masterId
            houseId = forceRef(record.value('house_id'))
            houseMasterInfoList['houseId'] = houseId
            parentId = forceRef(record.value('parent_id'))
            houseMasterInfoList['parentId'] = parentId
            houseMasterInfoList['organisationId'] = forceRef(record.value('organisation_id'))
            houseMasterInfoList['isArea'] = forceInt(record.value('isArea'))
            netId = forceRef(record.value('net_id'))
            while parentId and not netId:
                recordParent = db.getRecordEx(tableOrgStructure, [tableOrgStructure['parent_id'], tableOrgStructure['net_id']], [tableOrgStructure['id'].eq(parentId), tableOrgStructure['deleted'].eq(0)])
                if recordParent:
                    netId = forceRef(recordParent.value('net_id'))
                    parentId = forceRef(recordParent.value('parent_id'))
            houseMasterInfoList['netId'] = netId
            masterInfoList = houseIdList.get(houseId, {})
            if masterId not in masterInfoList.keys():
                masterInfoList[masterId] = houseMasterInfoList
                houseIdList[houseId] = masterInfoList

        self.logBrowser.append(u'Получение людей, которые будут прикреплены\n')
        clientsStmt = u'''
            SELECT DISTINCT
                Client.id
            FROM
                Address
                INNER JOIN ClientAddress ON ClientAddress.address_id = Address.id
                INNER JOIN Client ON Client.id = ClientAddress.client_id
            WHERE
                %s
        '''
        clientsCond = [
            tableAddress['house_id'].inlist(houseIdList.keys()),
            tableAddress['deleted'].eq(0),
            tableClientAddress['deleted'].eq(0),
            tableClientAddress['type'].eq(areaAddressType),
            'NOT EXISTS (SELECT ClientAttach.id FROM ClientAttach INNER JOIN rbAttachType ON rbAttachType.id = ClientAttach.attachType_id WHERE ClientAttach.id = (SELECT MAX(ClientAttachTemp.id) FROM ClientAttach AS ClientAttachTemp WHERE ClientAttachTemp.client_id = ClientAddress.client_id) AND rbAttachType.outcome = 1)'
        ]
        if self.cmbSex.currentIndex() != 0:
            clientsCond.append(tableClient['sex'].eq(self.cmbSex.currentIndex()))
        if self.cmbAge.currentIndex() != 0:
            clientsCond.append(u'age(Client.birthDate, DATE(NOW()))' + (u' < ' if self.cmbAge.currentIndex() == 1 else u' >= ') + u'18')
        query = db.query(clientsStmt % db.joinAnd(clientsCond))
        clientIdList = []
        while query.next():
            clientIdList.append(forceRef(query.record().value('id')))

        currentDate = QtCore.QDate.currentDate()
        cols = [tableClient['birthDate'],
                tableClient['sex'],
                tableClientAttach['id'].alias('clientAttachId'),
                tableClientAttach['client_id'],
                tableClientAttach['orgStructure_id'],
                tableAddress['house_id']
                ]
        #cols.append(u'age(Client.birthDate, %s) AS clientAge'%(db.formatDate(currentDate)))
        if self.chkAttach.isChecked():
            # Учитывать тип прикрепления "прикрепление":
            # (территориал или прикрепление) и (подразделение не указано или указано одно из тех, на которые надо прикрепить) -> 1 (заполнить найденное прикрепление)
            # иначе, если тип прикрепления не территориал и не прикрепление -> 2 (добавить новое прикрепление)
            # иначе 0 (ничего не делать)
            cols.append(u'IF((rbAttachType.code = 1 OR rbAttachType.code = 2) AND (ClientAttach.orgStructure_id IS NULL OR ClientAttach.orgStructure_id NOT IN (%s)), 1, IF(rbAttachType.code NOT IN (\'1\', \'2\'),2,0)) AS attachCode'%(u','.join(str(orgStructureId) for orgStructureId in orgStructureIdList if orgStructureId)))
        else:
            # Не учитывать ип прикрепления "прикрепление":
            # территориал и (подразделение не указано или указано одно из тех, на которые надо прикрепить) или (прикрепление и подразделение не указано) -> 1 (заполнить найденное прикрепление)
            cols.append(u'IF((rbAttachType.code = 1 AND (ClientAttach.orgStructure_id IS NULL OR ClientAttach.orgStructure_id NOT IN (%s))) OR (rbAttachType.code = 2 AND ClientAttach.orgStructure_id IS NULL), 1, IF(rbAttachType.code NOT IN (\'1\', \'2\'),2,0)) AS attachCode'%(u','.join(str(orgStructureId) for orgStructureId in orgStructureIdList if orgStructureId)))

        self.logBrowser.append(u'Будет прикреплено %i человек\n' % len(clientIdList))
        self.progressBar.setMaximum(len(clientIdList))
        i = 0
        for clientId in clientIdList:
            i += 1; self.progressBar.setValue(i)
            QtGui.qApp.processEvents()
            if self.stopped: break

            cond = [tableClientAttach['client_id'].eq(clientId),
                    tableClientAttach['deleted'].eq(0),
                    tableClient['deleted'].eq(0),
                    tableAddress['deleted'].eq(0),
                    tableClientAddress['type'].eq(areaAddressType)
                    ]
            table = tableClientAttach.leftJoin(tableAttachType, tableClientAttach['attachType_id'].eq(tableAttachType['id']))
            table = table.leftJoin(tableClient, tableClientAttach['client_id'].eq(tableClient['id']))
            table = table.innerJoin(tableClientAddress, tableClientAddress['client_id'].eq(tableClient['id']))
            table = table.innerJoin(tableAddress, tableClientAddress['address_id'].eq(tableAddress['id']))
            record = db.getRecordEx(table, cols, cond, u'ClientAttach.begDate DESC, ClientAddress.id DESC')
            if record:
                attachCode = forceInt(record.value('attachCode'))
                clientAttachId = forceRef(record.value('clientAttachId'))
                houseId = forceRef(record.value('house_id'))
                ageTuple = calcAgeTuple(forceDate(record.value('birthDate')), currentDate)
                sex = forceInt(record.value('sex'))
                #clientAge = forceInt(record.value('clientAge'))
                if attachCode:
                    masterId, organisationId = self.getMasterIdOrganisationId(houseIdList, houseId, ageTuple, sex)
                    if masterId:
                        if attachCode == 1:
                            newRecord = db.getRecordEx(tableClientAttach, '*', [tableClientAttach['id'].eq(clientAttachId)])
                            newRecord.setValue('orgStructure_id', QtCore.QVariant(masterId))
                            newRecord.setValue('LPU_id', QtCore.QVariant(organisationId))
                            newRecord.setValue('begDate', toVariant(currentDate))
                            db.updateRecords(tableClientAttach, newRecord, [tableClientAttach['id'].eq(clientAttachId)])
                        elif attachCode == 2:
                            newRecord = tableClientAttach.newRecord()
                            newRecord.setValue('client_id', QtCore.QVariant(clientId))
                            newRecord.setValue('attachType_id', QtCore.QVariant(1))
                            newRecord.setValue('LPU_id', QtCore.QVariant(organisationId))
                            newRecord.setValue('orgStructure_id', QtCore.QVariant(masterId))
                            newRecord.setValue('begDate', toVariant(currentDate))
                            db.insertRecord(tableClientAttach, newRecord)
            else:
                cols = [tableClient['birthDate'],
                        tableAddress['house_id'],
                        tableClient['sex'],
                        ]
                #cols.append(u'age(Client.birthDate, %s) AS clientAge'%(db.formatDate(currentDate)))
                cond = [tableClient['id'].eq(clientId),
                        tableClient['deleted'].eq(0),
                        tableAddress['house_id'].inlist(houseIdList.keys()),
                        tableAddress['deleted'].eq(0),
                        tableClientAddress['type'].eq(areaAddressType)
                        ]
                table = tableClient.innerJoin(tableClientAddress, tableClientAddress['client_id'].eq(tableClient['id']))
                table = table.innerJoin(tableAddress, tableClientAddress['address_id'].eq(tableAddress['id']))
                recordClient = db.getRecordEx(table, cols, cond, u'ClientAddress.id DESC')
                if recordClient:
                    ageTuple = calcAgeTuple(forceDate(recordClient.value('birthDate')), currentDate)
                    sex = forceInt(recordClient.value('sex'))
                    #clientAge = forceInt(recordClient.value('clientAge'))
                    houseId = forceRef(recordClient.value('house_id'))
                    masterId, organisationId = self.getMasterIdOrganisationId(houseIdList, houseId, ageTuple, sex)
                    newRecord = tableClientAttach.newRecord()
                    newRecord.setValue('client_id', QtCore.QVariant(clientId))
                    newRecord.setValue('attachType_id', QtCore.QVariant(1))
                    newRecord.setValue('LPU_id', QtCore.QVariant(organisationId))
                    newRecord.setValue('orgStructure_id', QtCore.QVariant(masterId))
                    newRecord.setValue('begDate', toVariant(currentDate))
                    db.insertRecord(tableClientAttach, newRecord)

        self.logBrowser.append(u'Прикрепление прошло успешно\n\n')
        self.modelTable.clearCache()
        self.updateOrgStructureTable()

    def moveAttaches(self):
        sex = self.cmbSex2.currentIndex()
        ageCategory = self.cmbAge2.currentIndex()
        orgStructureFrom = self.cmbFromOrgStructure.value()
        orgStructureTo = self.cmbToOrgStructure.value()
        count = self.edtAttachedCount.value()

        if not ((orgStructureFrom is not None or self.checkInputMessage(u'участок-источник', False, self.cmbFromOrgStructure))
                and (orgStructureTo is not None or self.checkInputMessage(u'участок-приемник', False, self.cmbToOrgStructure))
                and (orgStructureFrom != orgStructureTo or self.checkValueMessage(u'выбран один и тот же участок', False, self.cmbToOrgStructure))
                and (count > 0 or self.checkInputMessage(u'кол-во прикрепленных для переноса', False, self.edtAttachedCount))):
            return

        try:
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            clientIdList = self._selectAttachedTo(orgStructureFrom, sex, ageCategory, count)
            if clientIdList:
                attachCount = len(clientIdList)
                attachesWord = agreeNumberAndWord(attachCount, (u'прикрепление', u'прикрепления', u'прикреплений'))
                self.logBrowser.append(u'\nНайдено {0} {1} для переноса'.format(attachCount, attachesWord))
                self._moveAttachesTo(clientIdList, orgStructureTo)
                self.logBrowser.append(u'{0} {1} перенесено с участка "{2}" на участок "{3}"\n'.format(
                    attachCount, attachesWord, getOrgStructureName(orgStructureFrom), getOrgStructureName(orgStructureTo)
                ))
            else:
                self.logBrowser.append(u'\nНе найдено прикреплений для переноса')
        finally:
            QtGui.qApp.restoreOverrideCursor()

        self.clientAttachMonitoring.clearCache()
        self.clientAttachMonitoring.updateTable()

    def _selectAttachedTo(self, orgStructureId, sex, ageCategory, count):
        u""" Подбор пациентов для переноса """
        db = self.db
        tableAttachType = db.table('rbAttachType')
        tableClient = db.table('Client')
        tableClientAttach = db.table('ClientAttach')

        table = tableClientAttach.innerJoin(tableAttachType, tableAttachType['id'].eq(tableClientAttach['attachType_id']))
        table = table.innerJoin(tableClient, [tableClient['id'].eq(tableClientAttach['client_id']),
                                              tableClient['deleted'].eq(0)])
        cond = [
            tableClientAttach['orgStructure_id'].eq(orgStructureId),
            tableClientAttach['endDate'].isNull(),
            tableClientAttach['deleted'].eq(0),
            tableAttachType['code'].eq(CAttachType.Territorial),
        ]
        if sex:
            cond.append(tableClient['sex'].eq(sex))
        if ageCategory:
            clientAge = db.func.age(tableClient['birthDate'], db.curdate())
            if ageCategory == 1:
                cond.append(clientAge < 18)
            elif ageCategory == 2:
                cond.append(clientAge >= 18)

        order = [
            tableClientAttach['id']
        ]
        return db.getDistinctIdList(table, tableClient['id'], cond, order=order, limit=count)

    def _closePrevious(self, clientIdList):
        u""" Закрытие предыдущих прикреплений """
        db = self.db
        tableClientAttach = db.table('ClientAttach')
        cond = [
            tableClientAttach['client_id'].inlist(clientIdList),
            tableClientAttach['deleted'].eq(0),
            tableClientAttach['endDate'].isNull()
        ]
        expr = [
            tableClientAttach['endDate'].eq(QtCore.QDate.currentDate().addDays(-1))
        ]
        db.updateRecords(tableClientAttach, expr=expr, where=cond)

    def _attachTo(self, clientIdList, orgStructureId, attachTypeId):
        u""" Создание новых прикреплений к участку """
        db = self.db
        tableClientAttach = db.table('ClientAttach')

        orgId = QtGui.qApp.currentOrgId()

        newAttaches = [{
            'createDatetime' : db.now(),
            'createPerson_id': QtGui.qApp.userId,
            'client_id'      : clientId,
            'attachType_id'  : attachTypeId,
            'LPU_id'         : orgId,
            'orgStructure_id': orgStructureId,
            'begDate'        : db.curdate()
        } for clientId in clientIdList]
        db.insertFromDictList(tableClientAttach, newAttaches)

    def _moveAttachesTo(self, clientIdList, orgStructureId):
        u""" Перекрепление пациентов к участку """
        chunkSize = 500
        attachTypeId = CAttachType.getAttachTypeId(CAttachType.Territorial)

        self.progressBar.setMaximum(len(clientIdList))
        self.progressBar.setValue(0)

        for offset in range(0, len(clientIdList), chunkSize):
            QtGui.qApp.processEvents()
            if self.stopped: break

            idList = clientIdList[offset: offset + chunkSize]
            self._closePrevious(idList)
            self._attachTo(idList, orgStructureId, attachTypeId)
            self.progressBar.setValue(offset + len(idList))

        self.progressBar.setValue(len(clientIdList))

    def getMasterIdOrganisationId(self, houseIdList, houseId, ageTuple, sex):
        masterId = None
        organisationId = None
        #netCodeClient = 1 if clientAge >= 18 else 2
        houseMasterInfoList = houseIdList.get(houseId, {})
        if len(houseMasterInfoList) > 1:
            if self.attachByNet:
                for masterInfoList in houseMasterInfoList.values():
                    netId = masterInfoList.get('netId', None)
                    if netId:
                        net = self.nets[netId]
                        if (not net['sex'] or net['sex'] == sex) and (not net['ageSelector'] or checkAgeSelector(net['ageSelector'], ageTuple)):
                            masterId = masterInfoList.get('masterId', None)
                            organisationId = masterInfoList.get('organisationId', None)
                            break
            if self.attachByAreaType:
                preferableAreaType = 2 if ageTuple[3] < 18 else 1  # Педиатрический для детей, Терапевтический для взрослых
                defaultAreaType = 4  # Общей практики
                for areaType in [preferableAreaType, defaultAreaType]:
                    if not masterId:
                        for masterInfoList in houseMasterInfoList.values():
                            if masterInfoList.get('isArea', 0) == areaType:
                                masterId = masterInfoList.get('masterId', None)
                                organisationId = masterInfoList.get('organisationId', None)
                                break
        if not masterId:
            masterInfoList = houseMasterInfoList.values()
            if masterInfoList:
                masterInfo = masterInfoList[0]
                masterId = masterInfo.get('masterId', None)
                organisationId = masterInfo.get('organisationId', None)

        return masterId, organisationId
