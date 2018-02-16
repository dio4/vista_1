# -*- coding: utf-8 -*-
#
##############################################################################
###
### Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
###
##############################################################################
# Форма 043: стоматология и другие зубные дела

from PyQt4 import QtCore, QtGui, QtSql

from Events.Action import CAction
from Events.ActionInfo import CActionInfoProxyList
from Events.ActionsSelector import selectActionTypes
from Events.ActionsSummaryModel import CFxxxActionsSummaryModel
from Events.DiagnosisType import CDiagnosisTypeCol
from Events.EventEditDialog import CEventEditDialog, CDiseaseCharacter, CDiseaseStage, CDiseasePhases
from Events.EventInfo import CDiagnosticInfoProxyList, CVisitInfoProxyList
from Events.EventVisitsModel import CEventVisitsModel
from Events.TeethEventInfo import CTeethEventInfo
from Events.Utils import checkDiagnosis, checkIsHandleDiagnosisIsChecked, getAvailableCharacterIdByMKB, \
    getDiagnosisId2, getDiagnosisSetDateVisible, getEventDuration, getEventShowTime, hasEventVisitAssistant, \
    getEventLengthDays, \
    setAskedClassValueForDiagnosisManualSwitch, \
    setOrgStructureIdToCmbPerson
from Forms.F025.PreF025Dialog import CPreF025DagnosticAndActionPresets
from Forms.F043.DentitionTable import CClientDentitionHistoryModel, CDentitionModel, CParodentiumModel
from Forms.F043.PreF043Dialog import CPreF043Dialog
from Forms.F043.Ui_F043 import Ui_F043Dialog
from Orgs.Utils import getTopParentIdForOrgStructure
from RefBooks.Tables import rbDispanser, rbHealthGroup, rbTraumaType
from Users.Rights import urAccessF043planner, urAdmin, urRegTabWriteRegistry
from library.ICDInDocTableCol import CICDExInDocTableCol
from library.ICDMorphologyInDocTableCol import CMKBMorphologyCol
from library.InDocTable import CInDocTableModel, CBoolInDocTableCol, CDateInDocTableCol, CRBInDocTableCol, \
    CActionPersonInDocTableColSearch
from library.PrintTemplates import customizePrintButton, getPrintButton
from library.TNMS.TNMSComboBox import CTNMSCol
from library.Utils import forceBool, forceDate, forceInt, forceRef, forceString, forceStringEx, toVariant, \
    copyFields, formatNum, variantEq, forceTr
from library.crbcombobox import CRBComboBox
from library.interchange import getDatetimeEditValue, getDateEditValue, getRBComboBoxValue, \
    setDatetimeEditValue, setRBComboBoxValue, setDateEditValue

INSPECTION_DENTITION_TAB_INDEX = 0
INSPECTION_DENTITION_ADDITIONAL_TAB_INDEX = 1
RESULT_DENTITION_TAB_INDEX = 2


class CF043Dialog(CEventEditDialog, Ui_F043Dialog):
    # filterDiagnosticResultByPurpose = False

    def __init__(self, parent):
        CEventEditDialog.__init__(self, parent)
        self.dentitionActionTypeId = forceRef(
                                    QtGui.qApp.db.translate('ActionType', 'flatCode', 'dentitionInspection', 'id'))
        self.parodentActionTypeId = forceRef(
                                    QtGui.qApp.db.translate('ActionType', 'flatCode', 'parodentInsp', 'id'))
        self.mapSpecialityIdToDiagFilter = {}
        self.addModels('Visits', CEventVisitsModel(self))
        self.addModels('Diagnostics', CF043FinalDiagnosticsModel(self))
        self.addModels('ActionsSummary', CFxxxActionsSummaryModel(self, True))
        self.addModels('ClientDentitionHistory', CClientDentitionHistoryModel(self))
        self.addModels('Dentition', CDentitionModel(self, self.modelClientDentitionHistory))
        self.addModels('Parodentium', CParodentiumModel(self, self.modelClientDentitionHistory))
        self.modelDentition.setIsExistsDentitionAction(bool(self.dentitionActionTypeId))
        self.modelParodentium.setIsExistsDentitionAction(bool(self.parodentActionTypeId))

        self.actEditClient = QtGui.QAction(u'Изменить описание клиента', self)

        self.actEditClient.setObjectName('actEditClient')
        self.setupDiagnosticsMenu()
        self.btnPrint = getPrintButton(self, '')
        self.btnPrint.setObjectName('btnPrint')
        self.createSaveAndCreateAccountButton()

        self.setupUi(self)

        self.setupSaveAndCreateAccountButton()
        self.setupSaveAndCreateAccountForPeriodButton()

        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Стоматология Ф.043')

        self.tabToken.setFocusProxy(self.tblDiagnostics)
        # self.tabTempInvalidAndAegrotat.setCurrentIndex(1 if QtGui.qApp.tempInvalidDoctype() == '2' else 0)
        self.grpTempInvalid.setEventEditor(self)
        self.grpTempInvalid.setType(0, '1')
        # self.grpAegrotat.setEventEditor(self)
        # self.grpAegrotat.setType(0, '2')
        self.grpDisability.setEventEditor(self)
        self.grpDisability.setType(1)
        self.grpVitalRestriction.setEventEditor(self)
        self.grpVitalRestriction.setType(2)

        self.tabStatus.setEventEditor(self)
        self.tabDiagnostic.setEventEditor(self)
        self.tabTreatmentPlan.setEventEditor(self)
        self.tabCure.setEventEditor(self)
        self.tabMisc.setEventEditor(self)
        self.tabCash.setEventEditor(self)
        self.tabStatus.setActionTypeClass(0)
        self.tabDiagnostic.setActionTypeClass(1)
        self.tabTreatmentPlan.modelAPActions.setIgnoredActionTypeByClass([3])
        self.tabTreatmentPlan.setNotFilteredActionTypesClasses([0, 1, 2])
        self.tabCure.setActionTypeClass(2)
        self.tabMisc.setActionTypeClass(3)
        self.tabCash.setEventEditor(self)
        self.buttonBox.addButton(self.btnPrint, QtGui.QDialogButtonBox.ActionRole)
        self.tabCash.isControlsCreate = True

        self.tblVisits.setModel(self.modelVisits)
        self.tblDiagnostics.setModel(self.modelDiagnostics)
        self.setModels(self.tblClientDentitionHistory,
                       self.modelClientDentitionHistory,
                       self.selectionModelClientDentitionHistory)
        self.setModels(self.tblDentition,
                       self.modelDentition,
                       self.selectionModelDentition)
        self.setModels(self.tblParodentium,
                       self.modelParodentium,
                       self.selectionModelParodentium)

        self.cmbContract.setCheckMaxClients(True)

# mark tables as editable to prevent saving event while editing child item
        self.markEditableTableWidget(self.tblVisits)
        self.markEditableTableWidget(self.tblDiagnostics)
#        self.markEditableTableWidget(self.tblClientDentitionHistory)
#        self.markEditableTableWidget(self.tblDentition)
#        self.markEditableTableWidget(self.tblParodentium)

        self.modelActionsSummary.addModel(self.tabStatus.modelAPActions)
        self.modelActionsSummary.addModel(self.tabDiagnostic.modelAPActions)
        self.modelActionsSummary.addModel(self.tabCure.modelAPActions)
        self.modelActionsSummary.addModel(self.tabMisc.modelAPActions)
        self.modelActionsSummary.addModel(self.tabTreatmentPlan.modelAPActions)
        self.tabCash.addActionModel(self.tabStatus.modelAPActions)
        self.tabCash.addActionModel(self.tabDiagnostic.modelAPActions)
        #self.tabCash.addActionModel(self.tabTreatmentPlan.modelAPActions)
        self.tabCash.addActionModel(self.tabCure.modelAPActions)
        self.tabCash.addActionModel(self.tabMisc.modelAPActions)
# popup menus
        self.txtClientInfoBrowser.actions.append(self.actEditClient)
        self.actEditClient.setEnabled(QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteRegistry]))
        self.tblVisits.addPopupDelRow()
        self.tblDiagnostics.setPopupMenu(self.mnuDiagnostics)

        self.setupDirtyCather()
        self.setIsDirty(False)
        self.blankMovingIdList = []
        self.isResultDentitionLoadedByInspection = False
        self.isNewDentitionActionInitialized = False
        self.clientId = None
        self.prolongateEvent = False
        self.prevEventId = None
        self.tabNotes.setEventEditor(self)
        self.edtDentitionObjectively.getThesaurus(1)
        self.edtDentitionMucosa.getThesaurus(2)
        self.cmbResult.setShowFields(CRBComboBox.showCodeAndName)

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

    def getModelFinalDiagnostics(self):
        return self.modelDiagnostics

    def setupDiagnosticsMenu(self):
        self.mnuDiagnostics = QtGui.QMenu(self)
        self.mnuDiagnostics.setObjectName('mnuDiagnostics')
        self.actDiagnosticsRemove = QtGui.QAction(u'Удалить запись', self)
        self.actDiagnosticsRemove.setObjectName('actDiagnosticsRemove')
        self.mnuDiagnostics.addAction(self.actDiagnosticsRemove)

    @QtCore.pyqtSlot()
    def on_actDiagnosticsRemove_triggered(self):
        currentRow = self.tblDiagnostics.currentIndex().row()
        self.getModelFinalDiagnostics().removeRowEx(currentRow)
        # self.updateDiagnosisTypes()

    def updateDiagnosisTypes(self):
        items = self.getModelFinalDiagnostics().items()
        isFirst = True
        for item in items :
            diagnosisTypeId = self.getDiagnosisTypeId(isFirst)
            item.setValue('diagnosisType_id', toVariant(diagnosisTypeId))
            isFirst = False

    def _prepare(self, contractId, clientId, eventTypeId, orgId, personId, eventSetDatetime, eventDatetime,
                 includeRedDays, numDays, presetDiagnostics, presetActions, disabledActions, externalId, assistantId,
                 curatorId, movingActionTypeId=None, valueProperties=None, relegateOrgId=None, diagnos=None,
                 financeId=None, protocolQuoteId=None, actionByNewEvent=None, referrals=None, isAmb=True,
                 recommendationList=None):
        if not valueProperties:
            valueProperties = []
        if not actionByNewEvent:
            actionByNewEvent = []
        if not referrals:
            referrals = {}
        if not recommendationList:
            recommendationList = []

        def prepVisit(date, personId, isAmb=True, serviceId=None):
            sceneId = None if isAmb else QtGui.qApp.db.translate('rbScene', 'code', '2', 'id')
            visit = self.modelVisits.getEmptyRecord(sceneId=sceneId, personId=personId)
            visit.setValue('date', toVariant(date))
            if serviceId is not None:
                visit.setValue('service_id', serviceId)
            return visit

        self.cmbResult.setTable('rbResult', True)
        self.eventSetDateTime = eventSetDatetime
        self.eventDate = eventDatetime
        self.setOrgId(orgId if orgId else QtGui.qApp.currentOrgId())
        self.setEventTypeId(eventTypeId)
        self.setClientId(clientId)
        self.clientId = clientId
        self.prolongateEvent = True if actionByNewEvent else False
        self.setExternalId(externalId)
        self.cmbPerson.setValue(personId)
        self.setEventTypeId(eventTypeId)
        self.fillNextDate() # must be after self.setEventTypeId
        #Temporary solution, edtNextdate is added to the interface but not used yet, so make it invisible
        #self.edtNextDate.setVisible(False)
        self.cmbOrder.setCode(1)
        self.initGoal()
        self.setContract()
        self.setRecommendations(recommendationList)

        self.updateModelsRetiredList()
        
        self.cmbResult.setCurrentIndex(0)
        self.tabNotes.setNotesEx(externalId, assistantId, curatorId, relegateOrgId, referrals = referrals)
        self.initFocus()

        visitTypeId = presetDiagnostics[0][4] if presetDiagnostics else None
        serviceId = presetDiagnostics[0][6] if presetDiagnostics else None
        self.modelVisits.setDefaultVisitTypeId(visitTypeId)
        visits = []
        date = QtCore.QDate()
        if self.eventDate:
            date = self.eventDate
            resultId = self.cmbResult.value()
            if not resultId and self.inheritResult:
                if self.cmbResult.model().rowCount() > 1:
                    self.cmbResult.setValue(self.cmbResult.model().getId(1))
        elif self.eventSetDateTime and self.eventSetDateTime.date():
            date = self.eventSetDateTime.date()
        else:
            date = QtCore.QDate.currentDate()
        visits.append(prepVisit(date, personId, isAmb, serviceId))
        self.modelVisits.setItems(visits)
        self.updateVisitsInfo()

        if presetDiagnostics:
            resultId = None
            if self.cmbResult.model().rowCount() > 1:
                resultId = self.cmbResult.model().getId(1)
            for MKB, dispanserId, healthGroupId, medicalGroupID, visitTypeId, goalId, serviceId in presetDiagnostics:
                item = self.modelDiagnostics.getEmptyRecord()
                item.setValue('MKB', toVariant(MKB))
                item.setValue('dispanser_id',   toVariant(dispanserId))
                item.setValue('healthGroup_id', toVariant(healthGroupId))
                if self.inheritResult:
                    item.setValue('result_id', toVariant(resultId))
                self.modelDiagnostics.items().append(item)
            self.modelDiagnostics.reset()
            if presetDiagnostics[0][5]:
                self.cmbGoal.setValue(presetDiagnostics[0][5])
        self.prepareActions(contractId, presetActions, disabledActions, movingActionTypeId, valueProperties, diagnos, financeId, protocolQuoteId, actionByNewEvent)
        self.grpTempInvalid.pickupTempInvalid()
        # self.grpAegrotat.pickupTempInvalid()
        self.grpDisability.pickupTempInvalid()
        self.grpVitalRestriction.pickupTempInvalid()
        self.setIsDirty(False)
        self.prepareDentition()
        self.prepareParodentium()
        self.modelDentition.setClientId(self.clientId)
        self.modelParodentium.setClientId(self.clientId)
        self.tabNotes.setEventEditor(self)
        return self.checkEventCreationRestriction()


    def prepareActions(self, contractId, presetActions, disabledActions, actionTypeIdValue, valueProperties, diagnos, financeId, protocolQuoteId, actionByNewEvent):
        def addActionType(actionTypeId, amount, financeId, contractId, idListActionType, idListActionTypeIPH, actionFinance, idListActionTypeMoving, org_id=None):
            for model in [self.tabStatus.modelAPActions,
                          self.tabDiagnostic.modelAPActions,
                          self.tabCure.modelAPActions,
                          self.tabTreatmentPlan.modelAPActions,
                          self.tabMisc.modelAPActions]:
                if actionTypeId in model.actionTypeIdList:
                    if actionTypeId in idListActionType and not actionByNewEvent:
                        model.addRow(actionTypeId, amount, financeId, contractId)
                        record, action = model.items()[-1]
                        record.setValue('org_id', toVariant(org_id))
                        if valueProperties and len(valueProperties) > 0 and valueProperties[0]:
                            action[u'Направлен в отделение'] = valueProperties[0]
                        if protocolQuoteId:
                            action[u'Квота'] = protocolQuoteId
                        if actionFinance == 0:
                            record.setValue('finance_id', toVariant(financeId))
                    elif actionTypeId in idListActionTypeIPH:
                        model.addRow(actionTypeId, amount, financeId, contractId)
                        record, action = model.items()[-1]
                        record.setValue('org_id', toVariant(org_id))
                        if diagnos:
                            record, action = model.items()[-1]
                            action[u'Диагноз'] = diagnos
                    #[self.eventActionFinance, self.receivedFinanceId, orgStructureTransfer, orgStructurePresence, oldBegDate, movingQuoting, personId]
                    elif actionByNewEvent and actionTypeId in idListActionTypeMoving:
                        model.addRow(actionTypeId, amount, financeId, contractId)
                        record, action = model.items()[-1]
                        record.setValue('org_id', toVariant(org_id))
                        if actionByNewEvent[0] == 0:
                            record.setValue('finance_id', toVariant(actionByNewEvent[1]))
                        action[u'Отделение пребывания'] = actionByNewEvent[2]
                        if actionByNewEvent[3]:
                            action[u'Переведен из отделения'] = actionByNewEvent[3]
                        if actionByNewEvent[4]:
                            record.setValue('begDate', toVariant(actionByNewEvent[4]))
                        else:
                            record.setValue('begDate', toVariant(QtCore.QDateTime.currentDateTime()))
                        if action.getType().containsPropertyWithName(u'Квота') and actionByNewEvent[5]:
                            action[u'Квота'] = actionByNewEvent[5]
                        if actionByNewEvent[6]:
                            record.setValue('person_id', toVariant(actionByNewEvent[6]))
                    elif (actionByNewEvent and actionTypeId not in idListActionType) or not actionByNewEvent:
                        model.addRow(actionTypeId, amount, financeId, contractId)
                        record, action = model.items()[-1]
                        record.setValue('org_id', toVariant(org_id))

        def disableActionType(actionTypeId):
            for model in [self.tabStatus.modelAPActions,
                          self.tabDiagnostic.modelAPActions,
                          self.tabCure.modelAPActions,
                          self.tabTreatmentPlan.modelAPActions,
                          self.tabMisc.modelAPActions]:
                if actionTypeId in model.actionTypeIdList:
                    model.disableActionType(actionTypeId)
                    break

        if disabledActions:
            for actionTypeId in disabledActions:
                disableActionType(actionTypeId)
        if presetActions:
            db = QtGui.qApp.db
            tableActionType = db.table('ActionType')
            tableEventType = db.table('EventType')
            idListActionType = db.getIdList(tableActionType, [tableActionType['id']], [tableActionType['flatCode'].like(u'received%'), tableActionType['deleted'].eq(0)])
            idListActionTypeIPH = db.getIdList(tableActionType, [tableActionType['id']], [tableActionType['flatCode'].like(u'inspectPigeonHole%'), tableActionType['deleted'].eq(0)])
            idListActionTypeMoving = db.getIdList(tableActionType, [tableActionType['id']], [tableActionType['flatCode'].like(u'moving%'), tableActionType['deleted'].eq(0)])
            eventTypeId = self.getEventTypeId()
            actionFinance = None
            if eventTypeId:
                recordET = db.getRecordEx(tableEventType, [tableEventType['actionFinance']], [tableEventType['deleted'].eq(0), tableEventType['id'].eq(eventTypeId)])
                actionFinance = forceInt(recordET.value('actionFinance')) if recordET else None
            if actionByNewEvent:
                actionTypeMoving = False
                for actionTypeId, amount, cash, org_id in presetActions:
                    if actionTypeId in idListActionTypeMoving:
                        actionTypeMoving = True
                        break
                if not actionTypeMoving and idListActionTypeMoving:
                    presetActions.append((idListActionTypeMoving[0], 1.0, False, None))
            for actionTypeId, amount, cash, org_id in presetActions:
                addActionType(actionTypeId, amount, financeId if cash else None, contractId if cash else None, idListActionType, idListActionTypeIPH, actionFinance, idListActionTypeMoving, org_id)


    def prepare(self, clientId, eventTypeId, orgId, personId, eventSetDatetime, eventDatetime, includeRedDays, numDays,
                externalId, assistantId, curatorId, flagHospitalization=False, movingActionTypeId=None,
                valueProperties=None, tissueTypeId=None, selectPreviousActions=False, relegateOrgId=None, diagnos=None,
                financeId=None, protocolQuoteId=None, actionByNewEvent=None, referrals=None, isAmb=True,
                recommendationList=None, useDiagnosticsAndActionsPresets=True, orgStructureId=None):
        if not valueProperties:
            valueProperties = []
        if not actionByNewEvent:
            actionByNewEvent = []
        if not referrals:
            referrals = {}
        self.setPersonId(personId)
        self.setOrgStructureId(orgStructureId)

        plannerDate = self.getPlannerDate(eventSetDatetime, eventDatetime)
        if QtGui.qApp.userHasAnyRight([urAccessF043planner, urAdmin]):
            dlg = CPreF043Dialog(self, self.contractTariffCache)
            dlg.prepare(clientId, eventTypeId, plannerDate, self.personId, self.personSpecialityId,
                        self.personTariffCategoryId, flagHospitalization, movingActionTypeId, tissueTypeId,
                        recommendationList, useDiagnosticsAndActionsPresets=useDiagnosticsAndActionsPresets)
            if dlg.diagnosticsTableIsNotEmpty() or dlg.actionsTableIsNotEmpty():
                if not dlg.exec_():
                    return False
            result = self._prepare(dlg.contractId, clientId, eventTypeId, orgId, personId, eventSetDatetime, eventDatetime, includeRedDays, numDays, dlg.diagnostics(), dlg.actions(), dlg.disabledActionTypeIdList, externalId, assistantId, curatorId, movingActionTypeId, valueProperties, relegateOrgId, diagnos, financeId, protocolQuoteId, actionByNewEvent, referrals=referrals, isAmb=isAmb, recommendationList=recommendationList)
            return result
        else:
            presets = CPreF025DagnosticAndActionPresets(clientId, eventTypeId, plannerDate, self.personSpecialityId,
                                                        flagHospitalization, movingActionTypeId, recommendationList,
                                                        useDiagnosticsAndActionsPresets=useDiagnosticsAndActionsPresets)
            return self._prepare(None, clientId, eventTypeId, orgId, personId, eventSetDatetime, eventDatetime, includeRedDays, numDays,
                                 presets.unconditionalDiagnosticList, presets.unconditionalActionList, presets.disabledActionTypeIdList,
                                 externalId, assistantId, curatorId, None, [], relegateOrgId, diagnos, financeId, protocolQuoteId, actionByNewEvent,
                                 referrals=referrals, isAmb=isAmb, recommendationList=recommendationList)


    def setEventTypeId(self, eventTypeId, title = ''):
        CEventEditDialog.setEventTypeId(self, eventTypeId, u'Ф.043')
        showTime = getEventShowTime(eventTypeId)
        self.edtBegTime.setVisible(showTime)
        self.edtEndTime.setVisible(showTime)
        if self.cmbResult.value() is None:
            if self.inheritResult == True:
                self.cmbResult.setValue(self.defaultEventResultId.get(self.eventPurposeId))
        self.updateResultFilter()
        self.cmbContract.setEventTypeId(eventTypeId)
        self.setVisitAssistantVisible(self.tblVisits, hasEventVisitAssistant(eventTypeId))
        customizePrintButton(self.btnPrint, self.eventContext if self.eventContext else 'F043')
        if title != u'Ф.001':
            self.actDialogAPActionsAdd = QtGui.QAction(u'Добавить ...', self)
            self.actDialogAPActionsAdd.setObjectName('actDialogAPActionsAdd')
            self.actDialogAPActionsAdd.setShortcut(QtCore.Qt.Key_F9)
            #self.mnuAction.addAction(self.actDialogAPActionsAdd)
            self.connect(self.actDialogAPActionsAdd, QtCore.SIGNAL('triggered()'), self.on_actDialogAPActionsAdd_triggered)
        self.diagnosisSetDateVisible = forceBool(getDiagnosisSetDateVisible(eventTypeId))
        if self.diagnosisSetDateVisible == False:
            self.tblDiagnostics.setColumnHidden(4, True)
        # self.setResultFilter()

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_modelVisits_dataChanged(self, topLeft, bottomRight):
        self.updateVisitsInfo()


    @QtCore.pyqtSlot(QtCore.QModelIndex, int, int)
    def on_modelVisits_rowsInserted(self, parent, start, end):
        self.updateVisitsInfo()
        self.emitUpdateActionsAmount()


    @QtCore.pyqtSlot(QtCore.QModelIndex, int, int)
    def on_modelVisits_rowsRemoved(self, parent, start, end):
        self.updateVisitsInfo()
        self.emitUpdateActionsAmount()

    @QtCore.pyqtSlot()
    def on_actDialogAPActionsAdd_triggered(self):
        model = self.modelActionsSummary
        if not hasattr(model, 'isEditable') or model.isEditable():
            if QtGui.qApp.isHideActionsFromOtherTopOrgStructures():
                orgStructureId = getTopParentIdForOrgStructure(QtGui.qApp.userOrgStructureId)
            elif QtGui.qApp.currentOrgStructureId():
                orgStructureId = QtGui.qApp.currentOrgStructureId()
            else:
                if QtGui.qApp.userSpecialityId:
                    orgStructureId = QtGui.qApp.userOrgStructureId
                else:
                    orgStructureId = None
            financeCode = forceStringEx(QtGui.qApp.db.translate('rbFinance', 'id', self.eventFinanceId, 'code'))
            if financeCode:
                financeCode = financeCode in ('3', '4')
            existsActionTypesList = []
            for item in model.items():
                existsActionTypesList.append(forceRef(item.value('actionType_id')))

            actionTypes = selectActionTypes(self,
                                            [0, 1, 2, 3],
                                            self.clientSex, self.clientAge,
                                            orgStructureId,
                                            self.eventTypeId,
                                            self.contractId,
                                            self.getMesId(),
                                            financeCode,
                                            self._id,
                                            existsActionTypesList,
                                            contractTariffCache=self.contractTariffCache,
                                            showAmountFromMes=self.showAmountFromMes,
                                            eventBegDate = self.edtBegDate.date(),
                                            eventEndDate = self.edtEndDate.date(),
                                            showMedicaments = self.showMedicaments,
                                            MKB=self.getFinalDiagnosisMKB()[0]
            )

            for actionTypeId, action in actionTypes:
                index = model.index(model.rowCount()-1, 0)
                model.setData(index, toVariant(actionTypeId), presetAction=action)
            model.emitDataChanged()

    def setOrgId(self, orgId):
        self.orgId = orgId
        self.cmbContract.setOrgId(orgId)
        self.cmbPerson.setOrgId(orgId)

    def setExternalId(self, externalId):
        self.lblValueExternalId.setText((u'Внешний идентификатор: ' + externalId) if externalId else '')

    def setRecord(self, record):
        self.cmbResult.setTable('rbResult', True)
        CEventEditDialog.setRecord(self, record)
        setDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'setDate')
        setRBComboBoxValue(self.cmbPerson,      record, 'setPerson_id')
        setDatetimeEditValue(self.edtEndDate, self.edtEndTime, record, 'execDate')
        setDateEditValue(self.edtNextDate, record, 'nextEventDate')
        setRBComboBoxValue(self.cmbPerson,      record, 'execPerson_id')
        setRBComboBoxValue(self.cmbResult,      record, 'result_id')
        self.setExternalId(forceString(record.value('externalId')))
        # setComboBoxValue(self.cmbOrder,         record, 'order')
        self.cmbOrder.setCode(forceString(record.value('order')))
        self.setPersonId(self.cmbPerson.value())
        self.setContract()
        setRBComboBoxValue(self.cmbContract, record, 'contract_id')
        self.prevEventId = forceRef(record.value('prevEvent_id'))
        if self.prevEventId:
            self.lblProlongateEvent.setText(u'п')
            db = QtGui.qApp.db
            tableEvent = db.table('Event')
            tableEventType = db.table('EventType')
            prevEventRecord = db.getRecordEx(tableEvent.innerJoin(tableEventType, tableEvent['eventType_id'].eq((tableEventType['id']))), [tableEventType['name'], tableEvent['setDate']], [tableEvent['deleted'].eq(0), tableEvent['id'].eq(self.prevEventId)])
            if prevEventRecord:
                self.tabNotes.edtPrevEventInfo.setText(u'Продолжение обращения: %s от %s.'%(forceString(prevEventRecord.value('name')), forceDate(prevEventRecord.value('setDate')).toString('dd.MM.yyyy')))
        self.loadVisits()
        self.loadDiagnostics()
        self.updateResultFilter()
        self.loadActions()
        self.modelClientDentitionHistory.loadClientDentitionHistory(self.clientId, self.eventSetDateTime.date())
        self.loadParodentium()
        self.loadDentition()
        self.modelDentition.setClientId(self.clientId)
        self.modelParodentium.setClientId(self.clientId)
        self.setIsDirty(False)

        self.grpTempInvalid.pickupTempInvalid()
        # self.grpAegrotat.pickupTempInvalid()
        self.grpDisability.pickupTempInvalid()
        self.grpVitalRestriction.pickupTempInvalid()
        self.tabCash.load(self.itemId())
        self.tabNotes.setNotes(record)
        self.tabReferralPage.setRecord(record)
        self.tabNotes.setEventEditor(self)
        self.tabNotes.updateReferralPeriod(self.edtBegDate.date())
        self.initFocus()
        self.setIsDirty(False)
        self.blankMovingIdList = []
        self.setEditable(self.getEditable())
        setOrgStructureIdToCmbPerson(self.cmbPerson)

    def setEditable(self, editable):
        # self.tabAegrotat.setEnabled(editable)
        self.tabStatus.setEditable(editable)
        self.tabDiagnostic.setEditable(editable)
        self.tabCure.setEditable(editable)
        self.tabMisc.setEditable(editable)
        self.tabCash.setEditable(editable)
        self.tabNotes.setEditable(editable)
        self.tabTempInvalid.setEnabled(editable)
        self.tabTempInvalidDisability.setEnabled(editable)
        self.tabTempInvalidS.setEnabled(editable)
        self.tabTreatmentPlan.setEditable(editable)
        # self.tabReferralPage.sete

        self.modelVisits.setEditable(editable)
        self.modelActionsSummary.setEditable(editable)
        self.modelDiagnostics.setEditable(editable)

        self.grpBase.setEnabled(editable)
        self.grpDisability.setEnabled(editable)
        self.grpVitalRestriction.setEnabled(editable)
        self.edtDentitionNote.setReadOnly(not editable)
        self.edtDentitionMucosa.setReadOnly(not editable)
        self.edtDentitionObjectively.setReadOnly(not editable)

    def getDiagnosisTypeId(self, dt):
        return forceRef(QtGui.qApp.db.translate('rbDiagnosisType', 'code', '2' if dt else '9', 'id'))

    def loadVisits(self):
        self.modelVisits.loadItems(self.itemId())
        self.updateVisitsInfo()

    def loadDiagnostics(self):
        db = QtGui.qApp.db
        table = db.table('Diagnostic')
        isDiagnosisManualSwitch = self.modelDiagnostics.manualSwitchDiagnosis()
        rawItems = db.getRecordList(table, '*', [table['deleted'].eq(0), table['event_id'].eq(self.itemId())], 'id')
        items = []
        for record in rawItems:
            diagnosisId     = record.value('diagnosis_id')
            MKB             = db.translate('Diagnosis', 'id', forceRef(diagnosisId), 'MKB')
            MKBEx           = db.translate('Diagnosis', 'id', forceRef(diagnosisId), 'MKBEx')
            morphologyMKB   = db.translate('Diagnosis', 'id', forceRef(diagnosisId), 'morphologyMKB')
            setDate         = forceDate(record.value('setDate'))
            newRecord = self.modelDiagnostics.getEmptyRecord()
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
        self.modelDiagnostics.setItems(items)

    def setResultFilter(self):
        """
        в модели modelDiagnostics
        устанавливаем фильтр на колонке, которая называется Исход (Результат)
        """
        if self.eventPurposeId:
            resultCol = self.modelDiagnostics.getCol('result_id')
            resultCol.setFilter('eventPurpose_id = %s' % self.eventPurposeId)

    def loadActions(self):
        eventId = self.itemId()
        self.tabTreatmentPlan.loadActions(eventId)
        self.tabStatus.loadActions(eventId)
        self.tabDiagnostic.loadActions(eventId)
        self.tabCure.loadActions(eventId)
        self.tabMisc.loadActions(eventId)
        self.modelActionsSummary.regenerate()
        self.tabCash.modelAccActions.regenerate()

    def loadDentition(self):
        model = self.modelClientDentitionHistory
        for tab in [self.tabStatus,
                    self.tabDiagnostic,
                    self.tabCure,
                    self.tabMisc]:
            modelAPActions = tab.tblAPActions.model()
            for record, action in modelAPActions.items():
                actionType = action.getType()
                if actionType.flatCode == u'dentitionInspection':
                    row = model.setCurrentDentitionItem(record, action)
                    self.tblClientDentitionHistory.setCurrentIndex(model.index(row, 0))

    def loadParodentium(self):
        model = self.modelClientDentitionHistory
        for tab in [self.tabStatus,
                    self.tabDiagnostic,
                    self.tabCure,
                    self.tabMisc]:
            modelAPActions = tab.tblAPActions.model()
            for record, action in modelAPActions.items():
                actionType = action.getType()
                if actionType.flatCode == u'parodentInsp':
                    row = model.setCurrentParodentiumItem(record, action)
                    self.tblClientDentitionHistory.setCurrentIndex(model.index(row, 0))

    def loadDentitionAdditional(self, record, action, isCurrentDentitionAction):
        #дополнительные свойства для Dentition
        for widget in [self.edtDentitionObjectively,
                       self.cmbDentitionBite,
                       self.edtDentitionMucosa,
                       self.edtDentitionNote]:
            widget.setEnabled(isCurrentDentitionAction)
        
        dentitionObjectivelyProperty = action.getProperty(u'Объективность')
        dentitionObjectivelyText = dentitionObjectivelyProperty.getText() if dentitionObjectivelyProperty else u''
        self.edtDentitionObjectively.setValue(dentitionObjectivelyText)

        self.cmbDentitionBite.blockSignals(True)
        dentitionBiteProperty = action.getProperty(u'Прикус')
        self.cmbDentitionBite.setDomain(dentitionBiteProperty.type().valueDomain if dentitionBiteProperty else u'')
        dentitionBiteText = dentitionBiteProperty.getText() if dentitionBiteProperty else u''
        self.cmbDentitionBite.setEditText(dentitionBiteText)
        self.cmbDentitionBite.blockSignals(False)

        dentitionMucosaProperty = action.getProperty(u'Слизистая')
        dentitionMucosaText = dentitionMucosaProperty.getText() if dentitionMucosaProperty else ''
        self.edtDentitionMucosa.setValue(dentitionMucosaText)
        
        dentitionNoteProperty = action.getProperty(u'Примечание')
        dentitionNoteText = dentitionNoteProperty.getText() if dentitionNoteProperty else u''
        self.edtDentitionNote.setPlainText(dentitionNoteText)


    def updateActionProperties(self, oldAction, newAction):
        newActionType = newAction.getType()
        actionTypeList = newActionType.getPropertiesById().items()
        for actionPropertyType in actionTypeList:
            actionPropertyType = actionPropertyType[1]
            actionPropertyTypeName = actionPropertyType.name
            actionPropertyTypeValue = newAction.getProperty(actionPropertyTypeName).getText()
            oldAction.getProperty(actionPropertyTypeName).setValue(
                                actionPropertyType.convertQVariantToPyValue(actionPropertyTypeValue))
        return oldAction


    def prepareDentition(self, actionTypeId = None):
        if not actionTypeId:
            db = QtGui.qApp.db
            actionTypeIdList = db.getIdList('ActionType', 'id', 'flatCode=\'dentitionInspection\' AND deleted = 0')
            if actionTypeIdList:
                actionTypeId = actionTypeIdList[0]
        if actionTypeId:
            for actionsModel in [self.tabStatus.modelAPActions,
                                 self.tabDiagnostic.modelAPActions,
                                 self.tabCure.modelAPActions,
                                 self.tabMisc.modelAPActions]:
                if actionTypeId in actionsModel.actionTypeIdList:
                    actionsModel.addRow(actionTypeId)
                    newRecord, newAction = actionsModel.items()[-1]
                    newRecord.setValue('begDate', QtCore.QVariant(self.eventSetDateTime.date()))

                    self.modelDentition.clientId = self.clientId
                    if not self.modelDentition.clientId:
                        return
                    setDate = self.eventSetDateTime.date()
                    self.modelClientDentitionHistory.loadClientDentitionHistory(self.clientId, setDate)
                    db = QtGui.qApp.db
                    tableEvent            = db.table('Event')
                    tableAction           = db.table('Action')
                    tableActionType       = db.table('ActionType')
                    cond = [tableEvent['client_id'].eq(self.modelDentition.clientId),
                            tableEvent['deleted'].eq(0),
                            tableAction['deleted'].eq(0),
                            tableActionType['flatCode'].eq('dentitionInspection')
                            ]
                    if setDate:
                        cond.append(tableAction['begDate'].yearEq(setDate))

                    queryTable = tableEvent.innerJoin(tableAction,
                                                      tableAction['event_id'].eq(tableEvent['id']))
                    queryTable = queryTable.innerJoin(tableActionType,
                                                      tableActionType['id'].eq(tableAction['actionType_id']))
                    # order  = tableAction['begDate'].name() + ' DESC' + ', ' + tableAction['event_id'].name() + ' DESC'
                    order = [tableAction['id']]
                    fields = 'Action.*'
                    record = db.getRecordEx(queryTable, fields, cond, order)
                    if record:
                        record.setValue('id', toVariant(None))
                        actionsModel.fillRecord(record, actionTypeId)
                        record.setValue('event_id', toVariant(self.itemId()))
                        record.setValue('begDate', QtCore.QVariant(self.eventSetDateTime.date()))
                        action = CAction(record=record)
                        updateAction = self.updateActionProperties(newAction, action)
                        actionsModel._items[len(actionsModel.items())-1] = (record, updateAction)
                        actionsModel.emitItemsCountChanged()
                        self.modelClientDentitionHistory.addNewDentitionItem(record, updateAction)
                    else:
                        self.modelClientDentitionHistory.addNewDentitionItem(newRecord, newAction)
                    self.tblClientDentitionHistory.setCurrentIndex(self.modelClientDentitionHistory.index(0, 0))
                    self.isNewDentitionActionInitialized = True


    def prepareParodentium(self, actionTypeId = None):
        if not actionTypeId:
            db = QtGui.qApp.db
            actionTypeIdList = db.getIdList('ActionType', 'id', 'flatCode=\'parodentInsp\' AND deleted = 0')
            if actionTypeIdList:
                actionTypeId = actionTypeIdList[0]
        if actionTypeId:
            for actionsModel in [self.tabStatus.modelAPActions,
                                 self.tabDiagnostic.modelAPActions,
                                 self.tabCure.modelAPActions,
                                 self.tabMisc.modelAPActions]:
                if actionTypeId in actionsModel.actionTypeIdList:
                    actionsModel.addRow(actionTypeId)
                    newRecord, newAction = actionsModel.items()[-1]
                    newRecord.setValue('begDate', QtCore.QVariant(self.eventSetDateTime.date()))

                    self.modelParodentium.clientId = self.clientId
                    if not self.modelParodentium.clientId:
                        return
                    db = QtGui.qApp.db
                    tableEvent            = db.table('Event')
                    tableAction           = db.table('Action')
                    tableActionType       = db.table('ActionType')
                    cond = [tableEvent['client_id'].eq(self.modelParodentium.clientId),
                            tableEvent['deleted'].eq(0),
                            tableAction['deleted'].eq(0),
                            tableActionType['flatCode'].eq('parodentInsp')
                            ]
                    setDate = self.eventSetDateTime.date()
                    if setDate:
                        cond.append(tableAction['begDate'].yearEq(setDate))

                    queryTable = tableEvent.innerJoin(tableAction,
                                                      tableAction['event_id'].eq(tableEvent['id']))
                    queryTable = queryTable.innerJoin(tableActionType,
                                                      tableActionType['id'].eq(tableAction['actionType_id']))
                    # order  = tableAction['begDate'].name() + ' DESC' + ', ' + tableAction['event_id'].name() + ' DESC'
                    order = [tableAction['id']]
                    fields = 'Action.*'
                    record = db.getRecordEx(queryTable, fields, cond, order)
                    if record:
                        record.setValue('id', toVariant(None))
                        actionsModel.fillRecord(record, actionTypeId)
                        record.setValue('event_id', toVariant(self.itemId()))
                        record.setValue('begDate', QtCore.QVariant(self.eventSetDateTime.date()))
                        action = CAction(record=record)
                        updateAction = self.updateActionProperties(newAction, action)
                        actionsModel._items[len(actionsModel.items())-1] = (record, updateAction)
                        actionsModel.emitItemsCountChanged()
                        #self.modelParodentium.loadAction(record, updateAction)
                        self.modelClientDentitionHistory.addNewParodentiumItem(record, updateAction)
                    else:
                        #self.modelParodentium.loadAction(newRecord, newAction)
                        self.modelClientDentitionHistory.addNewParodentiumItem(newRecord, newAction)


    @QtCore.pyqtSlot()
    def on_edtDentitionObjectively_editingFinished(self):
        txt = self.edtDentitionObjectively.value()
        current = self.tblClientDentitionHistory.currentIndex()
        action = self.modelClientDentitionHistory.getItem(current)[1]
        actionProperty = action.getProperty(u'Объективность')
        if actionProperty:
            propertyType = actionProperty.type()
            actionProperty.setValue(propertyType.convertQVariantToPyValue(txt))


    @QtCore.pyqtSlot(QtCore.QString)
    def on_cmbDentitionBite_editTextChanged(self, txt):
        current = self.tblClientDentitionHistory.currentIndex()
        action = self.modelClientDentitionHistory.getItem(current)[1]
        actionProperty = action.getProperty(u'Прикус')
        if actionProperty:
            propertyType = actionProperty.type()
            actionProperty.setValue(propertyType.convertQVariantToPyValue(txt))


    @QtCore.pyqtSlot()
    def on_edtDentitionMucosa_editingFinished(self):
        txt = self.edtDentitionMucosa.value()
        current = self.tblClientDentitionHistory.currentIndex()
        action = self.modelClientDentitionHistory.getItem(current)[1]
        actionProperty = action.getProperty(u'Слизистая')
        if actionProperty:
            propertyType = actionProperty.type()
            actionProperty.setValue(propertyType.convertQVariantToPyValue(txt))


    @QtCore.pyqtSlot()
    def on_edtDentitionNote_textChanged(self):
        txt = self.edtDentitionNote.toPlainText()
        current = self.tblClientDentitionHistory.currentIndex()
        action = self.modelClientDentitionHistory.getItem(current)[1]
        actionProperty = action.getProperty(u'Примечание')
        if actionProperty:
            propertyType = actionProperty.type()
            actionProperty.setValue(propertyType.convertQVariantToPyValue(txt))


    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelClientDentitionHistory_currentChanged(self, current, previous):
        if current.isValid():
            record, action = self.modelClientDentitionHistory.getItem(current)[:2]
            if action.getType().flatCode == u'dentitionInspection':
                self.dentitionTabWidget.setCurrentIndex(0)
                isCurrentDentitionAction = self.modelClientDentitionHistory.isCurrentDentitionAction(current.row())
                self.modelDentition.loadAction(record, action, isCurrentDentitionAction)
                self.loadDentitionAdditional(record, action, isCurrentDentitionAction)
            else:
                self.dentitionTabWidget.setCurrentIndex(2)
                isCurrentParodentiumAction = self.modelClientDentitionHistory.isCurrentParodentiumAction(current.row())
                self.modelParodentium.loadAction(record, action, isCurrentParodentiumAction)



    def initFocus(self):
        if self.cmbContract.count() != 1:
            self.cmbContract.setFocus(QtCore.Qt.OtherFocusReason)
        else:
            self.tblDiagnostics.setFocus(QtCore.Qt.OtherFocusReason)


    def updateVisitsInfo(self):
        items = self.modelVisits.items()
        self.lblVisitsCountValue.setText(str(len(items)))
        dates = []
        for item in items:
            date    = forceDate(item.value('date'))
            if not date.isNull():
                dates.append(date)
        if dates:
            minDate = min(dates)
            maxDate = max(dates)
            days = minDate.daysTo(maxDate)+1
        else:
            days = 0
        self.setEventDuration(days)
        self.lblVisitsDurationValue.setText(str(days))


    def getRecord(self):
        record = CEventEditDialog.getRecord(self)
        showTime = getEventShowTime(self.eventTypeId)

        getRBComboBoxValue(self.cmbContract,    record, 'contract_id')
        getDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'setDate', showTime)
        getRBComboBoxValue(self.cmbPerson,      record, 'setPerson_id')
        getDatetimeEditValue(self.edtEndDate, self.edtEndTime, record, 'execDate', showTime)
        getDateEditValue(self.edtNextDate, record, 'nextEventDate')
        getRBComboBoxValue(self.cmbPerson,      record, 'execPerson_id')
        getRBComboBoxValue(self.cmbResult,      record, 'result_id')
        # getComboBoxValue(self.cmbOrder,         record, 'order')
        record.setValue('order', toVariant(self.cmbOrder.code()))
        if self.prolongateEvent:
            record.setValue('order', toVariant(5))
            record.setValue('prevEvent_id', toVariant(self.prevEventId))
        self.tabNotes.getNotes(record, self.eventTypeId)
        return record

    def getFinalDiagnosisId(self):
        diagnostics = self.modelDiagnostics.items()
        return forceRef(diagnostics[0].value('diagnosis_id')) if diagnostics else None

    def saveInternals(self, eventId):
        super(CF043Dialog, self).saveInternals(eventId)
        self.saveVisits(eventId)
        self.saveDiagnostics(eventId)
        setAskedClassValueForDiagnosisManualSwitch(None)
        self.grpTempInvalid.saveTempInvalid()
        # self.grpAegrotat.saveTempInvalid()
        self.grpDisability.saveTempInvalid()
        self.grpVitalRestriction.saveTempInvalid()
        self.saveActions(eventId)
        self.tabCash.save(eventId)
        # self.tabNotes.saveOutgoingRef(eventId)
        self.saveBlankUsers(self.blankMovingIdList)
        self.updateRecommendations()

    def saveVisits(self, eventId):
        items = self.modelVisits.items()
        personIdVariant = toVariant(self.personId)
        for item in items :
            item.setValue('person_id', personIdVariant)
        self.modelVisits.saveItems(eventId)


    def saveDiagnostics(self, eventId):
        items = self.modelDiagnostics.items()
        isDiagnosisManualSwitch = self.modelDiagnostics.manualSwitchDiagnosis()
        isFirst = True
        endDate = self.edtEndDate.date()
        endDateVariant = toVariant(endDate)
        personIdVariant = toVariant(self.personId)
        specialityIdVariant = QtGui.qApp.db.translate('Person', 'id', personIdVariant, 'speciality_id')
        MKBDiagnosisIdPairList = []
        prevId = 0
        for row, item in enumerate(items):
            MKB   = forceString(item.value('MKB'))
            MKBEx = forceString(item.value('MKBEx'))
            TNMS  = forceString(item.value('TNMS'))
            morphologyMKB = forceString(item.value('morphologyMKB'))
            if self.diagnosisSetDateVisible == False:
                item.setValue('setDate', endDateVariant )
                date = forceDate(endDateVariant)
            else:
                date = forceDate(item.value('setDate'))
            diagnosisTypeId = self.getDiagnosisTypeId(isFirst)
            item.setValue('diagnosisType_id', toVariant(diagnosisTypeId))
            item.setValue('speciality_id', specialityIdVariant)
            item.setValue('person_id', toVariant(self.personId) )
            item.setValue('endDate', endDateVariant )
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
                    morphologyMKB=morphologyMKB
                    )
            item.setValue('diagnosis_id', toVariant(diagnosisId))
            item.setValue('TNMS', toVariant(TNMS))
            item.setValue('character_id', toVariant(characterId))
            itemId = forceInt(item.value('id'))
            if prevId > itemId:
                item.setValue('id', QtCore.QVariant())
                prevId=0
            else :
                prevId = itemId
            isFirst = False
            MKBDiagnosisIdPairList.append((MKB, diagnosisId))
        self.modelDiagnostics.saveItems(eventId)
        self.modifyDiagnosises(MKBDiagnosisIdPairList)


    def saveActions(self, eventId):
        self.tabStatus.saveActions(eventId)
        self.tabDiagnostic.saveActions(eventId)
        self.tabCure.saveActions(eventId)
        self.tabMisc.saveActions(eventId)
        self.tabTreatmentPlan.saveActions(eventId)

    ####################################################
        # checkDataEntered #

    def checkDataEntered(self):
        result = CEventEditDialog.checkDataEntered(self)
        self.blankMzovingIdList = []
        begDate = self.edtBegDate.date()
        endDate = self.edtEndDate.date() if self._isClosedEventCheck else QtCore.QDate()
        nextDate = self.edtNextDate.date()
        result = result and (self.orgId != QtGui.qApp.currentOrgId() or self.cmbContract.value() or self.checkInputMessage(u'договор', False, self.cmbContract))
        result = result and (self.cmbPerson.value()   or self.checkInputMessage(u'врача',        False, self.cmbPerson))
        result = result and (not begDate.isNull() or self.checkInputMessage(u'дату назначения', False, self.edtBegDate))
        if endDate:
            result = result and self.checkActionDataEntered(begDate, QtCore.QDate(), endDate, self.tabToken, self.edtBegDate, None, self.edtEndDate)
            result = result and self.checkEventDate(begDate, endDate, nextDate, self.tabToken, self.edtNextDate,self.edtEndDate, True)
            minDuration,  maxDuration = getEventDuration(self.eventTypeId)
            if minDuration<=maxDuration:
                countRedDays = not QtGui.qApp.isExcludeRedDaysInEventLength()
                eventDuration = getEventLengthDays(begDate, endDate, countRedDays, self.eventTypeId)
                eventDurationErrorString = u'Указана длительность с учётом выходных: %s.'%formatNum(eventDuration, (u'день', u'дня', u'дней'))
                result = result and (eventDuration >= minDuration or
                                     self.checkValueMessage(u'Длительность должна быть не менее %s. %s'%(formatNum(minDuration, (u'дня', u'дней', u'дней')), eventDurationErrorString), False, self.edtEndDate))
                result = result and (maxDuration==0 or eventDuration <= maxDuration or
                                     self.checkValueMessage(u'Длительность должна быть не более %s. %s'%(formatNum(maxDuration, (u'дня', u'дней', u'дней')), eventDurationErrorString), False, self.edtEndDate))
            # if not QtGui.qApp.userHasRight(urDoNotCheckResultAndMKB):
            #    result = result and (self.cmbResult.value()  or self.checkInputMessage(u'результат',   False, self.cmbResult))
        result = result and self.checkDiagnosticsDataEntered([(self.tblDiagnostics, True, True, None)],
                                                             endDate)
        result = result and self.checkActionsDateEnteredActuality(begDate, endDate, [self.tabStatus, self.tabDiagnostic, self.tabTreatmentPlan, self.tabCure, self.tabMisc])
        result = result and self.checkActionsDataEntered([self.tabStatus, self.tabDiagnostic, self.tabTreatmentPlan, self.tabCure, self.tabMisc], begDate, endDate)
        result = result and (len(self.modelVisits.items())>0 or self.checkInputMessage(u'посещение', False, self.tblVisits))
        result = result and self.checkVisitsDataEntered(begDate, endDate)
        result = result and self.grpTempInvalid.checkTempInvalidDataEntered()
        # result = result and self.grpAegrotat.checkTempInvalidDataEntered()
        result = result and self.grpDisability.checkTempInvalidDataEntered()
        result = result and self.grpVitalRestriction.checkTempInvalidDataEntered()
        result = result and self.tabCash.checkDataLocalContract()
        result = result and self.checkSerialNumberEntered()
        result = result and self.checkTabNotesReferral()

        # if \
        #         self.getFinalDiagnosisMKB()[0] is not '' and self.getFinalDiagnosisMKB()[0][0] == u'C' \
        #         and not QtGui.qApp.userHasRight(urOncoDiagnosisWithoutTNMS)\
        #         and QtGui.qApp.isTNMSVisible() and self.getModelFinalDiagnostics().items()[0].value('TNMS') is None:
        #     result = result and self.checkValueMessage(u'Поле TNMS-Ст должно быть заполнено!', False, None)

        self.valueForAllActionEndDate = None
        return result


    def checkSerialNumberEntered(self):
        result = True
        self.blankMovingIdList = []
        db = QtGui.qApp.db
        table = db.table('ActionPropertyType')
        actionTypeIdListSerial = db.getDistinctIdList(table, [table['actionType_id']], [table['deleted'].eq(0), table['typeName'].like('BlankSerial')])

        for tab in [self.tabStatus,
                      self.tabDiagnostic,
                      self.tabCure,
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
#        if QtGui.qApp.userHasRight(urDoNotCheckResultAndMKB):
#            return True
#        
#        if endDate and len(self.modelDiagnostics.items()) <= 0:
#            self.checkInputMessage(u'диагноз', False, self.tblDiagnostics)
#            return False
#        
#        for row, record in enumerate(self.modelDiagnostics.items()):
#            if not self.checkDiagnosticDataEntered(row, record):
#                return False
#        return True
#
#
#    def checkDiagnosticDataEntered(self, row, record):
#        result = True
#        if result:
#            MKB = forceString(record.value('MKB'))
#            result = MKB or self.checkInputMessage(u'диагноз', False, self.tblDiagnostics, row, record.indexOf('MKB'))
#            if result:
#                char = MKB[:1]
#                traumaTypeId = forceRef(record.value('traumaType_id'))
#                if char in 'ST' and not traumaTypeId:
#                    result = self.checkValueMessage(u'Необходимо указать тип травмы', True, self.tblDiagnostics, row, record.indexOf('traumaType_id'))
#                if char not in 'ST' and traumaTypeId:
#                    result = self.checkValueMessage(u'Необходимо удалить тип травмы', False, self.tblDiagnostics, row, record.indexOf('traumaType_id'))
#
#        return result


        # checkDataEntered #
    ####################################################


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


    def getEventInfo(self, context):
        result = CEventEditDialog.getEventInfo(self, context, CTeethEventInfo)
        # инициализация свойств
        result._isPrimary = None
        # инициализация таблиц
        result._actions = CActionInfoProxyList(context,
                [self.tabStatus.modelAPActions, self.tabDiagnostic.modelAPActions, self.tabCure.modelAPActions, self.tabMisc.modelAPActions],
                result)
        result._diagnosises = CDiagnosticInfoProxyList(context, [self.modelDiagnostics])
        result._visits = CVisitInfoProxyList(context, self.modelVisits)
        return result


    def getTempInvalidInfo(self, context):
        return self.grpTempInvalid.getTempInvalidInfo(context)

    # def getAegrotatInfo(self, context):
    #     return self.grpAegrotat.getTempInvalidInfo(context)

    @QtCore.pyqtSlot()
    def on_modelDiagnostics_resultChanged(self):
        CEventEditDialog.defaultDiagnosticResultId[self.eventPurposeId] = self.modelDiagnostics.resultId()
        self.updateResultFilter()
        # if self.cmbResult.value() is None:
        #     self.cmbResult.setValue(getEventResultId(CEventEditDialog.defaultDiagnosticResultId.get(self.eventPurposeId)))


    @QtCore.pyqtSlot(int)
    def on_cmbPerson_currentIndexChanged(self):
        self.setPersonId(self.cmbPerson.value())


    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtEndDate_dateChanged(self, date):
        self.setContract()
        self.tabNotes.cmbClientPolicy.updatePolicy(date)
        if QtGui.qApp.isAutoClosed():
            self.chkIsClosed.setChecked(date != QtCore.QDate())


    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.tabNotes.updateReferralPeriod(date)
        contractId = self.cmbContract.value()
        self.cmbContract.setBegDate(date)
        self.cmbContract.setEndDate(date)
        self.cmbContract.setValue(contractId)
        self.updateResultFilter()
        self.setContract()

        self.updateModelsRetiredList()


class CF043BaseDiagnosticsModel(CInDocTableModel):
    __pyqtSignals__ = ('typeOrPersonChanged()',
                      )
    MKB_allowed_morphology = ['C', 'D']

    def __init__(self, parent, finishDiagnosisTypeCode, baseDiagnosisTypeCode, accompDiagnosisTypeCode):
        CInDocTableModel.__init__(self, 'Diagnostic', 'id', 'event_id', parent)
        self.isManualSwitchDiagnosis = QtGui.qApp.defaultIsManualSwitchDiagnosis()
        self.isMKBMorphology = QtGui.qApp.defaultMorphologyMKBIsVisible()
        self.characterIdForHandleDiagnosis = None
        self.columnHandleDiagnosis = None
        self._parent = parent
        self.diagnosisTypeCol = CDiagnosisTypeCol( u'Тип', 'diagnosisType_id', 2, [finishDiagnosisTypeCode, baseDiagnosisTypeCode, accompDiagnosisTypeCode], smartMode=False)
        self.addCol(self.diagnosisTypeCol)
        self.colPerson = self.addCol(CActionPersonInDocTableColSearch(u'Врач', 'person_id', 20, 'vrbPersonWithSpeciality', order = 'name', parent=parent))
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
        self.addCol(CRBInDocTableCol(    u'ДН',            'dispanser_id',   7, rbDispanser, showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(u'Диспансерное наблюдение')
#        self.addCol(CRBLikeEnumInDocTableCol(u'Госп',      'hospital',       7, CHospitalInfo.names, showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(u'Потребность в госпитализации')
        self.addCol(CRBInDocTableCol(    u'Травма',        'traumaType_id', 10, rbTraumaType, addNone=True, showFields=CRBComboBox.showName, prefferedWidth=150))
        self.addCol(CRBInDocTableCol(    u'ГрЗд',          'healthGroup_id', 7, rbHealthGroup, addNone=True, showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(u'Группа здоровья')
        self.setFilter(self.table['diagnosisType_id'].inlist([id for id in self.diagnosisTypeCol.ids if id]))

    def manualSwitchDiagnosis(self):
        return self.isManualSwitchDiagnosis


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
                    if not (bool(mkb) and mkb[0] in CF043BaseDiagnosticsModel.MKB_allowed_morphology):
                        result = (result & ~QtCore.Qt.ItemIsEditable)
        if QtGui.qApp.isPNDDiagnosisMode() and (row == len(self.items()) or index.column() != self._mapFieldNameToCol.get('result_id')):
            result = (result & ~QtCore.Qt.ItemIsEditable)
        return result


    def getEmptyRecord(self):
        eventEditor = QtCore.QObject.parent(self)
        result = CInDocTableModel.getEmptyRecord(self)
        result.append(QtSql.QSqlField('diagnosis_id',     QtCore.QVariant.Int))
        result.append(QtSql.QSqlField('speciality_id',    QtCore.QVariant.Int))
        result.append(QtSql.QSqlField('setDate',          QtCore.QVariant.DateTime))
        result.append(QtSql.QSqlField('endDate',          QtCore.QVariant.DateTime))
        result.setValue('person_id',     toVariant(eventEditor.getSuggestedPersonId()))
        if self.items():
            result.setValue('diagnosisType_id',  toVariant(self.diagnosisTypeCol.ids[2]))
        else:
            result.setValue('diagnosisType_id',  toVariant(self.diagnosisTypeCol.ids[0] if self.diagnosisTypeCol.ids[0] else self.diagnosisTypeCol.ids[1]))
            if self._parent.inheritResult == True:
                result.setValue('result_id', toVariant(CEventEditDialog.defaultDiagnosticResultId.get(self._parent.eventPurposeId)))
            else:
                result.setValue('result_id', toVariant(None))
        return result


    def setData(self, index, value, role=QtCore.Qt.EditRole):
        column = index.column()
        row = index.row()
        if not variantEq(self.data(index, role), value):
            eventEditor = QtCore.QObject.parent(self)
            if column == 0: # тип диагноза
                result = CInDocTableModel.setData(self, index, value, role)
                if result:
                    self.updateDiagnosisType(set([row]))
                    self.emitTypeOrPersonChanged()
                return result
            elif column == 1: # врач
                personId = forceRef(value)
                if not eventEditor.checkClientAttendaceEE(personId):
                    return False
                result = CInDocTableModel.setData(self, index, value, role)
                if result:
                    self.updateDiagnosisType(set())
                    #self.emitTypeOrPersonChanged()
                return result
            elif column == 2: # код МКБ
                newMKB = forceString(value)
                if not newMKB:
                    specifiedMKB = ''
                    specifiedCharacterId = None
                    specifiedTraumaTypeId = None
                else:
                    acceptable, specifiedMKB, specifiedMKBEx, specifiedCharacterId, specifiedTraumaTypeId = eventEditor.specifyDiagnosis(newMKB)
                    if not acceptable:
                        return False
                value = toVariant(specifiedMKB)
                result = CInDocTableModel.setData(self, index, value, role)
                if result:
                    self.updateCharacterByMKB(row, specifiedMKB, specifiedCharacterId)
                    self.updateTraumaType(row, specifiedMKB, specifiedTraumaTypeId)
                    self.emitTypeOrPersonChanged()
                return result
            if column == 3: # доп. код МКБ
                newMKB = forceString(value)
                if not newMKB:
                    pass
                else:
                    acceptable = eventEditor.checkDiagnosis(newMKB, True)
                    if not acceptable:
                        return False
                value = toVariant(newMKB)
                result = CInDocTableModel.setData(self, index, value, role)
#                if result:
#                    self.updateCharacterByMKB(row, specifiedMKB)
                return result

            return CInDocTableModel.setData(self, index, value, role)
        else:
            return True


    def removeRowEx(self, row):
        self.removeRows(row, 1)


    def updateDiagnosisType(self, fixedRowSet):
        mapPersonIdToRow = {}
        diagnosisTypeIds = []
        for row, item in enumerate(self.items()):
            personId = forceRef(item.value('person_id'))
            rows = mapPersonIdToRow.setdefault(personId, [])
            rows.append(row)
            diagnosisTypeId = forceRef(item.value('diagnosisType_id'))
            diagnosisTypeIds.append(diagnosisTypeId)

        for personId, rows in mapPersonIdToRow.iteritems():
            if self.diagnosisTypeCol.ids[0] and personId == self._parent.personId:
                firstDiagnosisId = self.diagnosisTypeCol.ids[0]
            else:
                firstDiagnosisId = self.diagnosisTypeCol.ids[1]
            otherDiagnosisId = self.diagnosisTypeCol.ids[2]

            usedDiagnosisTypeIds = [diagnosisTypeIds[row] for row in fixedRowSet.intersection(set(rows))]
            diagnosisTypeId = firstDiagnosisId if firstDiagnosisId not in usedDiagnosisTypeIds else otherDiagnosisId
            freeRows = set(rows).difference(fixedRowSet)
            for row in rows:
                if (row in freeRows) or diagnosisTypeIds[row] not in [firstDiagnosisId, otherDiagnosisId]:
                    if diagnosisTypeId != diagnosisTypeIds[row]:
                        self.items()[row].setValue('diagnosisType_id', toVariant(diagnosisTypeId))
                        self.emitCellChanged(row, item.indexOf('diagnosisType_id'))
                    diagnosisTypeId = otherDiagnosisId


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


    def getPersonsWithSignificantDiagnosisType(self):
        result = []
        significantDiagnosisTypeIdList = [self.diagnosisTypeCol.ids[0], self.diagnosisTypeCol.ids[1]]
        for item in self.items():
            diagnosisTypeId = forceRef(item.value('diagnosisType_id'))
            if diagnosisTypeId and diagnosisTypeId in significantDiagnosisTypeIdList:
                personId = forceRef(item.value('person_id'))
                if personId and personId not in result:
                    result.append(personId)
        return result


    def emitTypeOrPersonChanged(self):
        self.emit(QtCore.SIGNAL('typeOrPersonChanged()'))


class CF043FinalDiagnosticsModel(CF043BaseDiagnosticsModel):
    __pyqtSignals__ = ('resultChanged()',
                      )

    def __init__(self, parent):
        CF043BaseDiagnosticsModel.__init__(self, parent, '1', '2', '9')
        self.addCol(CRBInDocTableCol(forceTr(u'Результат', u'EventDiagnostic'),     'result_id',     10, 'rbDiagnosticResult', showFields=CRBComboBox.showNameAndCode, prefferedWidth=350))
        self.mapMKBToServiceId = {}

    def addRecord(self, record):
        super(CF043FinalDiagnosticsModel, self).addRecord(record)
        self.emitResultChanged()

    def getCloseOrMainDiagnosisTypeIdList(self):
        return [self.diagnosisTypeCol.codeToId(code) for code in ['1', '2']]

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        result = CF043BaseDiagnosticsModel.setData(self, index, value, role)
        if result:
            column = index.column()
            if column == 0 or column == self._mapFieldNameToCol.get('result_id'): # тип диагноза и результат
                row = index.row()
                item = self.items()[row]
                diagnosisTypeId = forceRef(item.value('diagnosisType_id'))
                if diagnosisTypeId == self.diagnosisTypeCol.ids[0]:
                    self.emitResultChanged()
        return result

    def resultId(self):
        finalDiagnosisId = self.diagnosisTypeCol.ids[0]
        items = self.items()
        for item in items:
            diagnosisTypeId = forceRef(item.value('diagnosisType_id'))
            if diagnosisTypeId == finalDiagnosisId:
                return forceRef(item.value('result_id'))
        return None

    def getFinalDiagnosis(self):
        finalDiagnosisTypeId = self.diagnosisTypeCol.ids[0]
        baseDiagnosisTypeId = self.diagnosisTypeCol.ids[1]
        items = self.items()
        for item in items:
            diagnosisTypeId = forceRef(item.value('diagnosisType_id'))
            if diagnosisTypeId in (finalDiagnosisTypeId, baseDiagnosisTypeId):
                return item
        return None

    def emitResultChanged(self):
        self.emit(QtCore.SIGNAL('resultChanged()'))
