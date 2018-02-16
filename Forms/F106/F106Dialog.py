# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

# Форма 106: свидетельство о смерти

from PyQt4 import QtCore, QtGui, QtSql

from Events.ActionInfo import CActionInfoProxyList
from Events.EventEditDialog import CEventEditDialog, CDiseaseCharacter, CDiseaseStage, CDiseasePhases
from Events.EventInfo import CDiagnosticInfoProxyList
from Events.Utils import checkDiagnosis, checkIsHandleDiagnosisIsChecked, getAvailableCharacterIdByMKB, \
    getDiagnosisId2, getDiagnosisSetDateVisible, getEventShowTime, recordAcceptable, \
    setAskedClassValueForDiagnosisManualSwitch, getEventResultId, \
    setOrgStructureIdToCmbPerson
from Registry.Utils import fixClientDeath
from Ui_F106 import Ui_Dialog
from Users.Rights import urAdmin, urDoNotCheckResultAndMKB, urRegTabWriteRegistry
from library.AgeSelector import checkAgeSelector, parseAgeSelector
from library.ICDInDocTableCol import CICDExInDocTableCol
from library.ICDMorphologyInDocTableCol import CMKBMorphologyCol
from library.InDocTable import CInDocTableModel, CBoolInDocTableCol, CDateInDocTableCol, CRBInDocTableCol
from library.TNMS.TNMSComboBox import CTNMSCol
from library.Utils import forceBool, forceDate, forceInt, forceRef, forceString, toVariant, copyFields, \
    variantEq
from library.crbcombobox import CRBComboBox
from library.interchange import getDatetimeEditValue, getLineEditValue, getRBComboBoxValue, setDatetimeEditValue, \
    setLineEditValue, setRBComboBoxValue, setTextEditValue


class CF106Dialog(CEventEditDialog, Ui_Dialog):
    filterDiagnosticResultByPurpose = False

    def __init__(self, parent):
        CEventEditDialog.__init__(self, parent)
        self.mapSpecialityIdToDiagFilter = {}

        #прим: '8' - код типа диагноза "предв. причина смерти", '9' код типа диагноза "предв.соп."
        self.addModels('PreliminaryDiagnostics', CF106DiagnosticsModel(self, '8', '10'))
        #прим: '4' - код типа диагноза "причина смерти", '9' код типа диагноза "сопутствующий"
        self.addModels('FinalDiagnostics',       CF106DiagnosticsModel(self, '4', '9'))

        self.actEditClient = QtGui.QAction(u'Изменить описание клиента', self)
        self.actEditClient.setObjectName('actEditClient')
        self.setupUi(self)

        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Ф.106/у')

        self.tabToken.setFocusProxy(self.tblPreliminaryDiagnostics)

        self.tabStatus.setEventEditor(self)
        self.tabMisc.setEventEditor(self)
        self.tabCash.setEventEditor(self)
        self.tabStatus.setActionTypeClass(0)
        self.tabMisc.setActionTypeClass(3)
        self.cmbContract.setCheckMaxClients(True)

        # мы полагаем, что cmbPerson - свой врач,
        # мы полагаем, что cmbPerson2 - любой паталогоанатом (код специальности - 51)
        self.cmbPerson2.setOrgId(None)
        self.cmbPerson2.setSpecialityId(forceRef(QtGui.qApp.db.translate('rbSpeciality', 'code', '51', 'id'))) # magic!
        # мы полагаем, что cmbStatusPerson - свой врач,
        # мы полагаем, что cmbMiscPerson - свой врач,

        self.tblPreliminaryDiagnostics.setModel(self.modelPreliminaryDiagnostics)
        self.tblFinalDiagnostics.setModel(self.modelFinalDiagnostics)
        self.tabCash.addActionModel(self.tabStatus.modelAPActions)
        self.tabCash.addActionModel(self.tabMisc.modelAPActions)

        self.markEditableTableWidget(self.tblPreliminaryDiagnostics)
        self.markEditableTableWidget(self.tblFinalDiagnostics)

        self.tblPreliminaryDiagnostics.addCopyDiagnos2Final(self)
        self.txtClientInfoBrowser.actions.append(self.actEditClient)
        self.actEditClient.setEnabled(QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteRegistry]))

        self.setupDirtyCather()
        self.setIsDirty(False)
        self.blankMovingIdList = []
        self.tabNotes.setEventEditor(self)
        self.cmbResult.setShowFields(CRBComboBox.showCodeAndName)

        self.edtNote.setDocument(self.tabNotes.edtEventNote.document())

        self.postSetupUi()

    @property
    def eventSetDateTime(self):
        return QtCore.QDateTime(self.edtBegDate.date(), self.edtBegTime.time())

    @eventSetDateTime.setter
    def eventSetDateTime(self, value):
        if isinstance(value, QtCore.QDate):
            self.edtBegDate.setDate(value)
            self.edtBegTime.setTime(QtCore.QTime())
        elif isinstance(value, QtCore.QDateTime):
            self.edtBegDate.setDate(value.date())
            self.edtBegTime.setTime(value.time())

    @property
    def eventDate(self):
        return self.edtEndDate.date()

    @eventDate.setter
    def eventDate(self, value):
        if isinstance(value, QtCore.QDate):
            self.edtEndDate.setDate(value)
            self.edtEndTime.setTime(QtCore.QTime())
        elif isinstance(value, QtCore.QDateTime):
            self.edtEndDate.setDate(value.date())
            self.edtEndTime.setTime(value.time())

    def prepare(self, clientId, eventTypeId, orgId, personId, eventSetDatetime, eventDatetime, includeRedDays, numDays,
                externalId, assistantId, curatorId, flagHospitalization=False, actionTypeIdValue=None,
                valueProperties=None, tissueTypeId=None, selectPreviousActions=False, relegateOrgId=None, diagnos=None,
                financeId=None, protocolQuoteId=None, actionByNewEvent=None, referrals=None, isAmb=True,
                recommendationList=None, useDiagnosticsAndActionsPresets=True, orgStructureId=None):
        if not valueProperties:
            valueProperties = []
        if not actionByNewEvent:
            actionByNewEvent = []
        if not referrals:
            referrals = {}
        if not recommendationList:
            recommendationList = []

        self.cmbResult.setTable('rbResult', True)
        self.eventSetDateTime = eventSetDatetime
        self.eventDate = eventDatetime
        self.setOrgId(orgId if orgId else QtGui.qApp.currentOrgId())
        self.cmbOrg.setValue(self.orgId)
        self.setClientId(clientId)
        self.setPersonId(personId)
        self.setOrgStructureId(orgStructureId)
        self.setContract()
        self.cmbPerson.setValue(personId)
        self.cmbPerson2.setValue(None)
        self.setEventTypeId(eventTypeId)
        self.setRecommendations(recommendationList)

        self.tabNotes.setNotesEx(externalId, assistantId, curatorId, relegateOrgId, referrals = referrals)
        self.initFocus()

        if useDiagnosticsAndActionsPresets:
            self.prepareActions(recommendationList)
        self.setIsDirty(False)
        self.tabNotes.setEventEditor(self)
        return True

    def prepareActions(self, recommendationList):
        if recommendationList is None:
            recommendationList = []
        def recordAcceptable(specialityId, sex, age):
            if specialityId:
                if specialityId != self.personSpecialityId:
                    return False
            if sex:
                if sex != self.clientSex :
                    return False
            if age:
                if self.clientAge == None:
                    return False
                ageSelector = parseAgeSelector(age)
                return checkAgeSelector(ageSelector, self.clientAge)
            return True

        db = QtGui.qApp.db
        table = db.table('EventType_Action')
        tableActionType = db.table('ActionType')
        cond = [table['eventType_id'].eq(self.eventTypeId)]
        for record in db.getRecordList(table.innerJoin(tableActionType, tableActionType['id'].eq(table['actionType_id'])),
                                       'actionType_id, speciality_id, EventType_Action.sex as sex, EventType_Action.age as age, selectionGroup, isCompulsory, EventType_Action.defaultOrg_id as defaultOrg_id, CONCAT_WS(\'|\', ActionType.code, ActionType.name) AS actionTypeName',
                                       cond):
            actionTypeId = forceRef(record.value('actionType_id'))
            specialityId = forceRef(record.value('speciality_id'))
            sex          = forceInt(record.value('sex'))
            age          = forceString(record.value('age'))
            selectionGroup = forceString(record.value('selectionGroup'))
            notDeleted = forceInt(record.value('isCompulsory'))
            org_id = forceRef(record.value('defaultOrg_id'))
            if recordAcceptable(specialityId, sex, age) and selectionGroup>0:
                for model in [self.tabStatus.modelAPActions,
                              self.tabMisc.modelAPActions]:
                    if notDeleted:
                        model.notDeletedActionTypes[actionTypeId] = forceString(record.value('actionTypeName'))
                    if actionTypeId in model.actionTypeIdList:
                        model.addRow(actionTypeId)
                        record = model.items()[-1][0]
                        record.setValue('org_id', toVariant(org_id))
                        break

        tableActionType = db.table('ActionType')
        actionTypeIdRecList = [forceInt(rec.value('actionType_id')) for rec in recommendationList]
        records = db.getRecordList(tableActionType, where=tableActionType['id'].inlist(actionTypeIdRecList))
        for record in records:
            actionTypeId = forceInt(record.value('id'))
            orgId = forceRef(record.value('defaultOrg_id'))
            for model in [self.tabStatus.modelAPActions,
                          self.tabMisc.modelAPActions]:
                if actionTypeId in model.actionTypeIdList:
                    model.addRow(actionTypeId)
                    record = model.items()[-1][0]
                    record.setValue('org_id', toVariant(orgId))

    def setLeavedAction(self, actionTypeIdValue):
        pass


    def initFocus(self):
        self.chkAutopsy.setFocus(QtCore.Qt.OtherFocusReason)
#        self.tblPreliminaryDiagnostics.setFocus(QtCore.Qt.OtherFocusReason)


    def newDiagnosticRecord(self, template):
        result = self.tblPreliminaryDiagnostics.model().getEmptyRecord()
        return result


    def setRecord(self, record):
        self.cmbResult.setTable('rbResult', True)
        CEventEditDialog.setRecord(self, record)
        setLineEditValue(self.edtNumber,        record, 'externalId')
        setDatetimeEditValue(self.edtEndDate, self.edtEndTime, record, 'setDate')
        setRBComboBoxValue(self.cmbPerson,      record, 'execPerson_id')
        setDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'execDate')
        setRBComboBoxValue(self.cmbPerson2,     record, 'setPerson_id')
        self.chkAutopsy.setChecked(forceInt(record.value('isPrimary'))==1)
        self.setPersonId(self.cmbPerson.value())
        self.setContract()
        setRBComboBoxValue(self.cmbResult,      record, 'result_id')
        setRBComboBoxValue(self.cmbContract,    record, 'contract_id')
        setTextEditValue(self.edtNote,          record, 'note')
        self.loadDiagnostics(self.modelPreliminaryDiagnostics)
        self.loadDiagnostics(self.modelFinalDiagnostics)
        self.loadActions()
        self.tabCash.load(self.itemId())
        self.tabNotes.setNotes(record)
        self.tabNotes.setEventEditor(self)
        self.tabNotes.updateReferralPeriod(self.edtBegDate.date())
        self.initFocus()
        self.setIsDirty(False)
        self.blankMovingIdList = []
        self.setEditable(self.getEditable())
        setOrgStructureIdToCmbPerson(self.cmbPerson)

    def setEditable(self, editable):
        self.tabStatus.setEditable(editable)
        self.tabMisc.setEditable(editable)
        self.tabCash.setEditable(editable)
        self.tabNotes.setEditable(editable)

        self.grpBase.setEnabled(editable)
        self.grpExtra.setEnabled(editable)
        self.modelPreliminaryDiagnostics.setEditable(editable)
        self.modelFinalDiagnostics.setEditable(editable)

    def loadDiagnostics(self, modelDiagnostics):
        db = QtGui.qApp.db
        table = db.table('Diagnostic')
        isDiagnosisManualSwitch = modelDiagnostics.manualSwitchDiagnosis()
        rawItems = db.getRecordList(table, '*', [table['deleted'].eq(0), table['event_id'].eq(self.itemId()), modelDiagnostics.filter], 'id')
        items = []
        for record in rawItems:
            diagnosisId     = record.value('diagnosis_id')
            MKB             = db.translate('Diagnosis', 'id', forceRef(diagnosisId), 'MKB')
            MKBEx           = db.translate('Diagnosis', 'id', forceRef(diagnosisId), 'MKBEx')
            morphologyMKB   = db.translate('Diagnosis', 'id', forceRef(diagnosisId), 'morphologyMKB')
            setDate         = forceDate(record.value('setDate'))
            newRecord =  modelDiagnostics.getEmptyRecord()
            copyFields(newRecord, record)
            newRecord.setValue('MKB',           MKB)
            newRecord.setValue('MKBEx',         MKBEx)
            newRecord.setValue('morphologyMKB', morphologyMKB)

            if isDiagnosisManualSwitch:
                isCheckedHandleDiagnosis = checkIsHandleDiagnosisIsChecked(setDate,
                                                                           self.clientId,
                                                                           diagnosisId)
                newRecord.setValue('handleDiagnosis', QtCore.QVariant(isCheckedHandleDiagnosis))

            items.append(newRecord)
        modelDiagnostics.setItems(items)


    def loadActions(self):
        eventId = self.itemId()
        self.tabStatus.loadActions(eventId)
        self.tabMisc.loadActions(eventId)
        self.tabCash.modelAccActions.regenerate()


    def getRecord(self):
        record = CEventEditDialog.getRecord(self)
        showTime = getEventShowTime(self.eventTypeId)
#перенести в exec_ в случае успеха или в accept?
        getRBComboBoxValue(self.cmbContract,    record, 'contract_id')
#        getDateEditValue(self.edtPrevDate,      record, 'prevEventDate')
        getLineEditValue(self.edtNumber,        record, 'externalId')
        getDatetimeEditValue(self.edtEndDate, self.edtEndTime, record, 'setDate', showTime)
        getRBComboBoxValue(self.cmbPerson2,     record, 'setPerson_id')
        getDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'execDate', showTime)
        getRBComboBoxValue(self.cmbPerson,      record, 'execPerson_id')
        getRBComboBoxValue(self.cmbResult,      record, 'result_id')
        record.setValue('isPrimary', toVariant(1 if self.chkAutopsy.isChecked() else 2))
        self.tabNotes.getNotes(record, self.eventTypeId)
        # getTextEditValue(self.edtNote,          record, 'note')
###  payStatus

        return record


    def saveInternals(self, eventId):
        super(CF106Dialog, self).saveInternals(eventId)
        self.saveDiagnostics(self.modelPreliminaryDiagnostics, eventId)
        self.saveDiagnostics(self.modelFinalDiagnostics, eventId)
        setAskedClassValueForDiagnosisManualSwitch(None)
        self.saveActions(eventId)
        self.tabCash.save(eventId)
        # self.tabNotes.saveOutgoingRef(eventId)
        fixClientDeath(self.clientId, self.edtBegDate.date(), self.edtEndDate.date(), self.orgId)
        self.saveBlankUsers(self.blankMovingIdList)
        self.updateRecommendations()

    def saveDiagnostics(self, modelDiagnostics, eventId):
        items = modelDiagnostics.items()
        isDiagnosisManualSwitch = modelDiagnostics.manualSwitchDiagnosis()
        isFirst = True
        date = self.edtBegDate.date()
        dateVariant = toVariant(date)
        personIdVariant = toVariant(self.personId)
        specialityIdVariant = QtGui.qApp.db.translate('Person', 'id', personIdVariant, 'speciality_id')
        MKBDiagnosisIdPairList = []
        prevId=0
        for item in items :
            MKB   = forceString(item.value('MKB'))
            MKBEx = forceString(item.value('MKBEx'))
            TNMS  = forceString(item.value('TNMS'))
            morphologyMKB = forceString(item.value('morphologyMKB'))
            if self.diagnosisSetDateVisible == False:
                item.setValue('setDate', dateVariant )
            else:
                date = forceDate(item.value('setDate'))
            diagnosisTypeId = modelDiagnostics.getDiagnosisTypeId(isFirst)
            item.setValue('diagnosisType_id', toVariant(diagnosisTypeId))
            item.setValue('speciality_id', specialityIdVariant)
            item.setValue('person_id', toVariant(self.personId) )
            item.setValue('endDate', dateVariant )
            diagnosisId = forceRef(item.value('diagnosis_id'))
            characterId = forceRef(item.value('character_id'))
            diagnosisId, characterId = getDiagnosisId2(
                date,
                self.personId,
                self.clientId,
                diagnosisTypeId,
                MKB,
                MKBEx,
                forceRef(item.value('character_id')),
                forceRef(item.value('dispanser_id')),
                forceRef(item.value('traumaType_id')),
                diagnosisId,
                forceRef(item.value('id')),
                isDiagnosisManualSwitch,
                forceBool(item.value('handleDiagnosis')),
                TNMS=TNMS,
                morphologyMKB=morphologyMKB)
            item.setValue('diagnosis_id', toVariant(diagnosisId))
            item.setValue('TNMS', toVariant(TNMS))
            item.setValue('character_id', toVariant(characterId))
            itemId = forceInt(item.value('id'))
            if prevId>itemId:
                item.setValue('id', QtCore.QVariant())
                prevId=0
            else :
                prevId=itemId
            isFirst = False
            MKBDiagnosisIdPairList.append((MKB, diagnosisId))
        modelDiagnostics.saveItems(eventId)
        self.modifyDiagnosises(MKBDiagnosisIdPairList)


    def saveActions(self, eventId):
        self.tabStatus.saveActions(eventId)
        self.tabMisc.saveActions(eventId)


    def setOrgId(self, orgId):
        self.orgId = orgId
        self.cmbContract.setOrgId(orgId)
        self.tabStatus.setOrgId(orgId)
        self.tabMisc.setOrgId(orgId)
        self.cmbOrg.setValue(self.orgId)


    def setEventTypeId(self, eventTypeId):
        CEventEditDialog.setEventTypeId(self, eventTypeId, u'Ф.106')
        self.tabCash.windowTitle = self.windowTitle()
        showTime = getEventShowTime(eventTypeId)
        self.edtBegTime.setVisible(showTime)
        self.edtEndTime.setVisible(showTime)
        if self.cmbResult.value() is None:
            if self.inheritResult == True:
                self.cmbResult.setValue(self.defaultEventResultId.get(self.eventPurposeId))
        self.updateResultFilter()
        self.diagnosisSetDateVisible = forceBool(getDiagnosisSetDateVisible(eventTypeId))
        if self.diagnosisSetDateVisible == False:
            self.tblFinalDiagnostics.setColumnHidden(2, True)
            self.tblPreliminaryDiagnostics.setColumnHidden(2, True)

    def resetActionTemplateCache(self):
        self.tabStatus.actionTemplateCache.reset()
        self.tabMisc.actionTemplateCache.reset()


    def checkDataEntered(self):
        result = True
        self.blankMovingIdList = []
#        result = result and (self.orgId != QtGui.qApp.currentOrgId() or self.cmbContract.value() or self.checkInputMessage(u'договор', False, self.cmbContract))
        begDate = self.edtBegDate.date()
        endDate = self.edtEndDate.date() if self._isClosedEventCheck else QtCore.QDate()
        result = result and (not begDate.isNull() or self.checkInputMessage(u'дату смерти', False, self.edtBegDate))
        result = result and (not endDate.isNull() or self.checkInputMessage(u'дату констатации', False, self.edtEndDate))
        if not QtGui.qApp.userHasRight(urDoNotCheckResultAndMKB):
            result = result and (self.cmbResult.value()   or self.checkInputMessage(u'результат',    False, self.cmbResult))
        result = result and (self.cmbPerson.value()   or self.checkInputMessage(u'врач',         False, self.cmbPerson))
#        if endDate.isNull():
#            maxEndDate = self.getMaxEndDateByVisits()
#            if not maxEndDate.isNull():
#                if QtGui.QMessageBox.question(self,
#                                    u'Внимание!',
#                                    u'Дата выполнения обращения не указана.\nУстановить дату завершения по максимальной дате посещений',
#                                    QtGui.QMessageBox.No|QtGui.QMessageBox.Yes,
#                                    QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
#                    self.edtEndDate.setDate(maxEndDate)
#                    endDate = maxEndDate
        if not (begDate.isNull() or endDate.isNull()):
            result = result and self.checkActionDataEntered(begDate, QtCore.QDate(), endDate, self.tabToken, self.edtBegDate, None, self.edtEndDate)
            result = result and self.checkEventDate(begDate, endDate, None, self.tabToken, None, self.edtEndDate, True)

        result = result and self.checkDiagnosticsDataEntered([(self.tblPreliminaryDiagnostics, False,True, None),
                                                              (self.tblFinalDiagnostics, False, True, None)],
                                                             endDate)
        result = result and self.checkActionsDateEnteredActuality(begDate, endDate, [self.tabStatus, self.tabMisc])
        result = result and self.checkActionsDataEntered([self.tabStatus, self.tabMisc], begDate, endDate)
        #result = result and self.checkActionsDataEntered(begDate, endDate)
        result = result and self.tabCash.checkDataLocalContract()
        result = result and self.checkSerialNumberEntered()
        result = result and self.checkTabNotesReferral()

        # if \
        #         self.getFinalDiagnosisMKB()[0] is not '' and self.getFinalDiagnosisMKB()[0][0] == u'C' \
        #         and not QtGui.qApp.userHasRight(urOncoDiagnosisWithoutTNMS)\
        #         and QtGui.qApp.isTNMSVisible() and self.getModelFinalDiagnostics().items()[0].value('TNMS') is None:
        #     result = result and self.checkValueMessage(u'Поле TNMS-Ст должно быть заполнено!', False, None)

        return result

    def checkDiagnosticDoctorEntered(self, table, row, record):
        return True

    def checkSerialNumberEntered(self):
        result = True
        self.blankMovingIdList = []
        db = QtGui.qApp.db
        table = db.table('ActionPropertyType')
        actionTypeIdListSerial = db.getDistinctIdList(table, [table['actionType_id']], [table['deleted'].eq(0), table['typeName'].like('BlankSerial')])

        for tab in [self.tabStatus,
                      self.tabMisc]:
            model = tab.modelAPActions
            for actionTypeIdSerial in actionTypeIdListSerial:
                if actionTypeIdSerial in model.actionTypeIdList:
                    for row, (record, action) in enumerate(model.items()):
                        if action and action._actionType.id:
                            actionTypeId = action._actionType.id
                            if actionTypeId == actionTypeIdSerial:
                                serial = action[u'Серия бланка']
                                number = action[u'Номер бланка']
                                if serial and number:
                                    blankParams = self.getBlankIdList(action)
                                    result, blankMovingId = self.checkBlankParams(blankParams, result, serial, number, tab.tblAPActions, row)
                                    self.blankMovingIdList.append(blankMovingId)
                                    if not result:
                                        return result
        return result


#    def checkDiagnosticsDataEntered(self, endDate):
#        
#        if QtGui.qApp.userHasRight(urDoNotCheckResultAndMKB):
#            return True
#        
#        for table, modelName in [(self.tblPreliminaryDiagnostics, u'предварительный'), (self.tblFinalDiagnostics, u'заключительный')]:
#            if endDate and len(table.model().items()) <= 0:
#                self.checkInputMessage(u'%s диагноз' % modelName, False, table)
#                return False
#            for row, record in enumerate(table.model().items()):
#                if not self.checkDiagnosticDataEntered(table, modelName, row, record):
#                    return False
#        return True


#    def checkDiagnosticDataEntered(self, table, modelName, row, record):
####     self.checkValueMessage(self, message, canSkip, widget, row=None, column=None):
#        result = True
#        if result:
#            MKB = forceString(record.value('MKB'))
#            result = MKB or self.checkInputMessage(u'%s диагноз' % modelName, False, table, row, record.indexOf('MKB'))
#            if result:
#                char = MKB[:1]
#                traumaTypeId = forceRef(record.value('traumaType_id'))
#                if char in 'ST' and not traumaTypeId:
#                    result = self.checkValueMessage(u'Необходимо указать тип травмы', True, table, row, record.indexOf('traumaType_id'))
#                if char not in 'ST' and traumaTypeId:
#                    result = self.checkValueMessage(u'Необходимо удалить тип травмы', False, table, row, record.indexOf('traumaType_id'))
##        if result and row == 0:
##            resultId = forceRef(record.value('result_id'))
##            result = resultId or self.checkInputMessage(u'результат', False, tbl, row, record.indexOf('result_id'))
#        return result


#    def checkActionsDataEntered(self, begDate, endDate):
##        for row, record in enumerate(self.modelActions.items()):
##            if not self.checkActionDataEntered(begDate, endDate, row, record):
##                return False
#        return True

#
#    def checkActionDataEntered(self, begDate, endDate, row, record):
##        result = self.checkRowEndDate(begDate, endDate, row, record, self.tblActions)
##        return result
#        pass


    def checkRowEndDate(self, begDate, endDate, row, record, widget):
        result = True
        column = record.indexOf('endDate')
        rowEndDate = forceDate(record.value('endDate'))
        if not rowEndDate.isNull():
            if rowEndDate>endDate:
                result = result and self.checkValueMessage(u'Дата выполнения должна быть не позже %s' % forceString(endDate), False, widget, row, column)
#            if rowEndDate < lowDate:
#                result = result and self.checkValueMessage(u'Дата выполнения должна быть не раньше %s' % forceString(lowDate), False, widget, row, column)
        return result


    def recordAcceptable(self, record):
        return recordAcceptable(self.clientSex, self.clientAge, record)


    def getDiagFilter(self):
        specialityId = self.personSpecialityId
        result = self.mapSpecialityIdToDiagFilter.get(specialityId, None)
        if result == None:
            result = QtGui.qApp.db.translate('rbSpeciality', 'id', specialityId, 'mkbFilter')
            if result == None:
                result = ''
            else:
                result = forceString(result)
            self.mapSpecialityIdToDiagFilter[specialityId] = forceString(result)
        return result


    def checkDiagnosis(self, MKB, isEx=False):
        diagFilter = self.getDiagFilter()
        return checkDiagnosis(self, MKB, diagFilter, self.clientId, self.clientSex, self.clientAge, self.begDate(), self.endDate(), self.eventTypeId, isEx)


#    def canChangeAction(self, row):
#        payStatus = self.modelActions.payStatus(row)
#        result = True
#        if payStatus  == CPayStatus.exposed:
#            actionId = forceRef(self.modelActions.items()[row].value('id'))
#            #SELECT Account.id
#            #FROM
#            #    Account_Item
#            #    LEFT JOIN Account on Account.id = Account_Item.master_id
#            #WHERE
#            #    Account_Item.action_id = $actionId
#            #AND Account.exposeDate IS NOT NULL
#
#            db = QtGui.qApp.db
#            tableAccount = db.table('Account')
#            tableAccountItem = db.table('Account_Item')
#            table = tableAccountItem.leftJoin(tableAccount, tableAccount['id'].eq(tableAccountItem['master_id']))
#            cond = [ tableAccountItem['action_id'].eq(actionId),
#                     tableAccount['exposeDate'].isNotNull()
#                   ]
#            idList = db.getIdList(table, tableAccount['id'].name(), where=cond)
#            result = not idList
#        elif payStatus  == CPayStatus.payed:
#            result = False
#        if not result:
#            message = u'Данная строка включена в счёт\nи её данные не могут быть изменены'
#            QtGui.QMessageBox.critical(self, u'Внимание!', message)
#        return result


    def getDiagnosisTypeId(self, dt):
        return forceRef(QtGui.qApp.db.translate('rbDiagnosisType', 'code', '2' if dt else '9', 'id'))


    def getEventInfo(self, context):
        result = CEventEditDialog.getEventInfo(self, context)
        # ручная инициализация свойств
        result._isPrimary = False
        # ручная инициализация таблиц
        result._actions = CActionInfoProxyList(context, [self.tabStatus.modelAPActions, self.tabMisc.modelAPActions], result)
        result._diagnosises = CDiagnosticInfoProxyList(context, [self.modelPreliminaryDiagnostics, self.modelFinalDiagnostics])
        return result


    def getTempInvalidInfo(self, context):
        return None

    def getAegrotatInfo(self, context):
        return None


    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        contractId = self.cmbContract.value()
        self.cmbContract.setBegDate(date)
        self.cmbContract.setEndDate(date)
        self.cmbContract.setValue(contractId)
        self.tabNotes.updateReferralPeriod(date)
        self.updateResultFilter()
        self.setContract()

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtEndDate_dateChanged(self, date):
        self.cmbPerson.setEndDate(date)
        self.cmbPerson2.setEndDate(date)
        self.tabStatus.setEndDate(date)
        self.tabMisc.setEndDate(date)
        self.setContract()
        self.tabNotes.cmbClientPolicy.updatePolicy(date)
        if QtGui.qApp.isAutoClosed():
            self.chkIsClosed.setChecked(date != QtCore.QDate())

    @QtCore.pyqtSlot(int)
    def on_cmbOrg_currentIndexChanged(self):
        self.setOrgId(self.cmbOrg.value())

    @QtCore.pyqtSlot(QtCore.QVariant)
    def on_modelFinalDiagnostics_resultChanged(self, resultId):
        # Не должна вызываться вообще
        CEventEditDialog.defaultDiagnosticResultId[self.eventPurposeId] = self.modelFinalDiagnostics.resultId()
        if self.cmbResult.value() is None:
            self.cmbResult.setValue(getEventResultId(CEventEditDialog.defaultDiagnosticResultId.get(self.eventPurposeId)))

    @QtCore.pyqtSlot(int)
    def on_cmbPerson_currentIndexChanged(self):
        oldPersonId = self.personId
        self.setPersonId(self.cmbPerson.value())
# что-то сомнительным показалось - ну поменяли отв. врача,
# всё равно менять врачей в действии вроде неправильно. или правильно?
        self.tabStatus.updatePersonId(oldPersonId, self.personId)
        self.tabMisc.updatePersonId(oldPersonId, self.personId)

    @QtCore.pyqtSlot()
    def on_actDiagnosticsAddAccomp_triggered(self):
        tbl = self.tblPreliminaryDiagnostics
        model = tbl.model()
        currentRow = tbl.currentIndex().row()
        if currentRow>=0 :
            currentRecord = model.items()[currentRow]
            newRecord = model.getEmptyRecord()
            newRecord.setValue('diagnosisType', QtCore.QVariant(CF106Dialog.dfAccomp))
            newRecord.setValue('speciality_id', currentRecord.value('speciality_id'))
            newRecord.setValue('healthGroup_id', currentRecord.value('healthGroup_id'))
            model.insertRecord(currentRow+1, newRecord)
            tbl.setCurrentIndex(model.index(currentRow+1, newRecord.indexOf('MKB')))

    def getModelFinalDiagnostics(self):
        return self.modelFinalDiagnostics

    def getPrevActionId(self, action, searchMode):
        return None


class CF106DiagnosticsModel(CInDocTableModel):
    __pyqtSignals__ = ('resultChanged(QVariant)',
                      )
    MKB_allowed_morphology = ['C', 'D']
    deathDiagnosisTypes = True

    def __init__(self, parent, mainDiagnosisTypeCode, accompDiagnosisTypeCode):
        CInDocTableModel.__init__(self, 'Diagnostic', 'id', 'event_id', parent)
        self._parent = parent
        self.isManualSwitchDiagnosis = QtGui.qApp.defaultIsManualSwitchDiagnosis()
        self.isMKBMorphology = QtGui.qApp.defaultMorphologyMKBIsVisible()
        self.characterIdForHandleDiagnosis = None
        self.columnHandleDiagnosis = None
        self.addExtCol(CICDExInDocTableCol(u'МКБ',         'MKB',   7), QtCore.QVariant.String)
        self.addExtCol(CICDExInDocTableCol(u'Доп.МКБ',     'MKBEx', 7), QtCore.QVariant.String)
        self.addCol(CDateInDocTableCol(  u'Выявлено',      'setDate',        10))
        if QtGui.qApp.isTNMSVisible():
            self.addCol(CTNMSCol(u'TNM-Ст', 'TNMS',  10))
        if self.isMKBMorphology:
            self.addExtCol(CMKBMorphologyCol(u'Морф.', 'morphologyMKB', 10, 'MKB_Morphology', filter='`group` IS NOT NULL'), QtCore.QVariant.String)
        self.addCol(CDiseaseCharacter(     u'Хар',         'character_id',   7, showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(u'Характер')
        if self.isManualSwitchDiagnosis:
            self.addExtCol(CBoolInDocTableCol( u'П',   'handleDiagnosis', 10), QtCore.QVariant.Int)
            self.characterIdForHandleDiagnosis = forceRef(QtGui.qApp.db.translate('rbDiseaseCharacter', 'code', '1', 'id'))
            self.columnHandleDiagnosis = self._mapFieldNameToCol.get('handleDiagnosis')
        self.addCol(CDiseasePhases(        u'Фаза',        'phase_id',       7, showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(u'Фаза')
        self.addCol(CDiseaseStage(         u'Ст',          'stage_id',       7, showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(u'Стадия')
        self.addCol(CRBInDocTableCol(    u'Травма',        'traumaType_id', 10, 'rbTraumaType', addNone=True, showFields=CRBComboBox.showName, prefferedWidth=150))
        db = QtGui.qApp.db
        self.mainDiagnosisTypeId   = forceRef(db.translate('rbDiagnosisType', 'code', mainDiagnosisTypeCode, 'id'))
        self.accompDiagnosisTypeId = forceRef(db.translate('rbDiagnosisType', 'code', accompDiagnosisTypeCode, 'id'))
        self.setFilter(self.table['diagnosisType_id'].inlist([self.mainDiagnosisTypeId, self.accompDiagnosisTypeId]))

    def addRecord(self, record):
        super(CF106DiagnosticsModel, self).addRecord(record)
        self.emitResultChanged(None)

    def manualSwitchDiagnosis(self):
        return self.isManualSwitchDiagnosis

    def getCloseOrMainDiagnosisTypeIdList(self):
        return []

    def flags(self, index=QtCore.QModelIndex()):
        result = CInDocTableModel.flags(self, index)
        row = index.row()
        if row < len(self._items):
            column = index.column()
            if self.isManualSwitchDiagnosis and index.isValid():
                if column == self.columnHandleDiagnosis:
                    characterId = forceRef(self.items()[row].value('character_id'))
                    if characterId != self.characterIdForHandleDiagnosis:
                        result = (result & ~QtCore.Qt.ItemIsUserCheckable)
#                        return result
            if self.isMKBMorphology and index.isValid():
                if column == self._mapFieldNameToCol.get('morphologyMKB'):
                    mkb = forceString(self.items()[row].value('MKB'))
                    if not (bool(mkb) and mkb[0] in CF106DiagnosticsModel.MKB_allowed_morphology):
                        result = (result & ~QtCore.Qt.ItemIsEditable)
        if QtGui.qApp.isPNDDiagnosisMode() and (row == len(self.items()) or index.column() != self._mapFieldNameToCol.get('result_id')):
            result = (result & ~QtCore.Qt.ItemIsEditable)
        return result

    def getDiagnosisTypeId(self, first):
        if first:
            return self.mainDiagnosisTypeId
        else:
            return self.accompDiagnosisTypeId

    def getEmptyRecord(self):
        isFirst = not bool(self.items())
        result = CInDocTableModel.getEmptyRecord(self)
        result.append(QtSql.QSqlField('diagnosis_id',     QtCore.QVariant.Int))
        result.append(QtSql.QSqlField('diagnosisType_id', QtCore.QVariant.Int))
        result.append(QtSql.QSqlField('speciality_id',    QtCore.QVariant.Int))
        result.append(QtSql.QSqlField('person_id',        QtCore.QVariant.Int))
        result.append(QtSql.QSqlField('dispanser_id',     QtCore.QVariant.Int))
        result.append(QtSql.QSqlField('hospital',         QtCore.QVariant.Int))
        result.append(QtSql.QSqlField('healthGroup_id',   QtCore.QVariant.Int))
        result.append(QtSql.QSqlField('setDate',          QtCore.QVariant.DateTime))
        result.append(QtSql.QSqlField('endDate',          QtCore.QVariant.DateTime))
        result.append(QtSql.QSqlField('payStatus',        QtCore.QVariant.Int))
        result.setValue('diagnosisType_id', QtCore.QVariant(self.getDiagnosisTypeId(isFirst)))
        if isFirst:
            if self._parent.inheritResult == True:
                result.setValue('result_id', toVariant(CEventEditDialog.defaultDiagnosticResultId.get(self._parent.eventPurposeId)))
            else:
                result.setValue('result_id', toVariant(None))
        return result

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        column = index.column()
        row = index.row()
        if not variantEq(self.data(index, role), value):
            if column == 0: # код МКБ
                newMKB = forceString(value)
                if not newMKB:
                    specifiedMKB = ''
                    specifiedCharacterId = None
                    specifiedTraumaTypeId = None
                else:
                    acceptable, specifiedMKB, specifiedMKBEx, specifiedCharacterId, specifiedTraumaTypeId = QtCore.QObject.parent(self).specifyDiagnosis(newMKB)
                    if not acceptable:
                        return False
                value = toVariant(specifiedMKB)
                result = CInDocTableModel.setData(self, index, value, role)
                #self.emitResultChanged(item.value('result_id'))
                self.emitResultChanged(self.items()[row].value('result_id'))
                if result:
                    self.updateCharacterByMKB(row, specifiedMKB, specifiedCharacterId)
                    self.updateTraumaType(row, specifiedMKB, specifiedTraumaTypeId)
                return result
            if column == 1: # доп. код МКБ
                newMKB = forceString(value)
                if not newMKB:
                    pass
                else:
                    acceptable = QtCore.QObject.parent(self).checkDiagnosis(newMKB, True)
                    if not acceptable:
                        return False
                value = toVariant(newMKB)
                result = CInDocTableModel.setData(self, index, value, role)
                return result

            return CInDocTableModel.setData(self, index, value, role)
        else:
            return True

    def payStatus(self, row):
        if 0 <= row < len(self.items()):
            return forceInt(self.items()[row].value('payStatus'))
        else:
            return 0

    def removeRowEx(self, row):
        self.removeRows(row, 1)

    def updateCharacterByMKB(self, row, MKB, specifiedCharacterId):
        characterIdList = getAvailableCharacterIdByMKB(MKB)
        item = self.items()[row]
        if specifiedCharacterId in characterIdList:
            characterId = specifiedCharacterId
        else:
            characterId = forceRef(item.value('character_id'))
            if (characterId in characterIdList) or (characterId == None and not characterIdList) :
                return
            if characterIdList:
                characterId = characterIdList[0]
            else:
                characterId = None
        item.setValue('character_id', toVariant(characterId))
        self.emitCellChanged(row, item.indexOf('character_id'))

    def updateTraumaType(self, row, MKB, specifiedTraumaTypeId):
        item = self.items()[row]
        prevTraumaTypeId = forceRef(item.value('traumaType_id'))
        if specifiedTraumaTypeId:
            traumaTypeId = specifiedTraumaTypeId
        else:
            traumaTypeId = prevTraumaTypeId
        if traumaTypeId != prevTraumaTypeId:
            item.setValue('traumaType_id', toVariant(traumaTypeId))
            self.emitCellChanged(row, item.indexOf('traumaType_id'))

    def getFinalDiagnosis(self):
        finalDiagnosisTypeId = 4  # "Причина смерти"
        items = self.items()
        for item in items:
            diagnosisTypeId = forceRef(item.value('diagnosisType_id'))
            if diagnosisTypeId == finalDiagnosisTypeId:
                return item
        return None

    def emitResultChanged(self, resultId):
        self.emit(QtCore.SIGNAL('resultChanged(QVariant&)'), resultId)
