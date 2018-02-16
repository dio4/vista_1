# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

from Events.ActionInfo import CActionInfoProxyList
from Events.ActionTypeComboBox import CActionTypeModel
from Events.ActionsSelector import CActionsModel, CActionTypesSelectionManager, CEnableCol
from Events.ActionsSummaryModel import CFxxxActionsSummaryModel
from Events.EventEditDialog import CEventEditDialog
from Events.EventInfo import CDiagnosticInfoProxyList
from Events.Utils import checkIsHandleDiagnosisIsChecked, getDiagnosisId2, getDiagnosisSetDateVisible, \
    getEventContextData, getEventFinanceId, getEventIsTakenTissue, getEventShowTime, getExternalIdDateCond, \
    getResultIdByDiagnosticResultId, \
    CTableSummaryActionsMenuMixin, getRealPayed, getEventFinanceCode, setOrgStructureIdToCmbPerson, isLittleStranger
from Forms.F001.PreF001Dialog import CPreF001Dialog, CPreF001DagnosticAndActionPresets
from Forms.F025.F025Dialog import CF025DiagnosticsModel
from Forms.Utils import check_data_text_TNM
from Orgs.Utils import getOrgStructureActionTypeIdSet
from Registry.Utils import CClientInfo
from TissueJournal.TissueInfo import CTissueTypeInfo, CTakenTissueJournalInfo
from Ui_F001 import Ui_F001Dialog
from Users.Rights import urAccessF001planner, urEditDiagnosticsInPayedEvents, urOncoDiagnosisWithoutTNMS, \
    urViewPolicyInStat, urEditClientPolicyInClosedEvent
from library.ItemsListDialog import CItemEditorBaseDialog
from library.PrintInfo import CInfoContext
from library.PrintTemplates import applyTemplate, customizePrintButton, directPrintTemplate, getFirstPrintTemplate, \
    getPrintButton, CPrintButton
from library.TableModel import CCol, CTextCol
from library.Utils import forceBool, forceDate, forceDateTime, forceInt, forceRef, forceString, \
    forceStringEx, toVariant, copyFields, formatNum
from library.crbcombobox import CRBComboBox
from library.database import CRecordCache
from library.interchange import getDatetimeEditValue, getRBComboBoxValue, setDatetimeEditValue, \
    setRBComboBoxValue


class CF001Dialog(CEventEditDialog, Ui_F001Dialog, CActionTypesSelectionManager, CTableSummaryActionsMenuMixin):
    def __init__(self, parent):
        CEventEditDialog.__init__(self, parent)
        CActionTypesSelectionManager.__init__(self)

        self.addBarcodeScanAction('actScanBarcode')
        self.addModels('ActionTypeGroups', CActionTypeModel(self))
        self.addModels('ActionTypes', CActionLeavesModel(self))
        self.addModels('ActionsSummary', CFxxxActionsSummaryModel(self, True))

        self.createSaveAndCreateAccountButton()

        self.btnPrintLabel = CPrintButton(self, u'Печать наклейки')

        self.btnPrintLabel.setObjectName('btnPrintLabel')
        self.btnPrint = getPrintButton(self, '')
        self.btnPrint.setObjectName('btnPrint')

        self.btnPrintLabel.setShortcut('F6')

        self.setupUi(self)

        self.buttonBox.addButton(self.btnPrint, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btnPrintLabel, QtGui.QDialogButtonBox.ActionRole)

        self.modelActionTypeGroups.setAllSelectable(True)
        self.modelActionTypeGroups.setRootItemVisible(True)
        self.modelActionTypeGroups.setLeavesVisible(False)
        self.setActionTypeClasses([0, 1, 2, 3])
        self.setModels(self.treeActionTypeGroups, self.modelActionTypeGroups, self.selectionModelActionTypeGroups)

        self.setModels(self.tblActionTypes, self.modelActionTypes, self.selectionModelActionTypes)
        self.tblActions.setModel(self.modelActionsSummary)
        self.modelActionsSummary.addModel(self.tabActions.modelAPActions)
        self.tabCash.addActionModel(self.tabActions.modelAPActions)
        self.tabCash.isControlsCreate = True

        self.tabActions.setEventEditor(self)
        self.tabCash.setEventEditor(self)
        self.edtFindByCode.installEventFilter(self)
        self.treeActionTypeGroups.installEventFilter(self)
        # cmb
        self.cmbTissueType.setTable('rbTissueType')
        self.cmbTissueUnit.setTable('rbUnit')
        self.cmbTissueUnit.setRTF(True)
        self.cmbSetPerson.setDefaultOrgStructureId(None)
        self.cmbSetPerson.setOnlyDoctorsIfUnknowPost(True)

        self.setupSaveAndCreateAccountButton()
        self.setupSaveAndCreateAccountForPeriodButton()

        self.cmbContract.setCheckMaxClients(True)

        self.actionTypesByTissueType = None
        self.takenTissueJournalTable = QtGui.qApp.db.table('TakenTissueJournal')
        self._manualInputExternalId  = None

        self.setTabActionsSettings()
        self.prepareSettings = {}
        self.actionsRowNotForAdding = {}
        self.actualByTissueType = {}
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.btnNextStep = QtGui.QPushButton(u'Продолжить')
        self.buttonBox.addButton(self.btnNextStep, QtGui.QDialogButtonBox.ActionRole)

        CTableSummaryActionsMenuMixin.__init__(self, [self.tabActions.tblAPActions])

        self.connect(self.selectionModelActionTypeGroups,
                     QtCore.SIGNAL('currentChanged(QModelIndex, QModelIndex)'),
                     self.on_selectionModelActionTypeGroups_currentChanged)

        self.connect(self.tabActions.tblAPActions,
                     QtCore.SIGNAL('delRows()'),
                     self.modelAPActionsAmountChanged)

        self.connect(self.btnNextStep,
                     QtCore.SIGNAL('clicked()'),
                     self.makeNextStep)

        self.connect(self.tabActions.tblAPActions.model(),
                     QtCore.SIGNAL('itemsCountChanged()'),
                     self.recountActualByTissueType)

        self.addAction(self.actScanBarcode)
        self.labelTemplate = getFirstPrintTemplate('clientTissueLabel')
        self.postInitSetup()
        self.prolongateEvent = False
        self.prevEventId = None
        self.tabNotes.setEventEditor(self)
        self.prepareEisWidgets()

        self.cmbResult.setShowFields(CRBComboBox.showCodeAndName)

        self.cmbClientPolicy.editTextChanged.connect(self.on_cmbClientPolicy_currentIndexChanged)
        self.tabNotes.cmbClientPolicy.editTextChanged.connect(self.on_cmbClientPolicy_currentIndexChanged_from_notes)
        self.cmbClientPolicy.setClientId(self.clientId)

        #self.cmbClientPolicy.editTextChanged.connect(self.f)
        #self.cmbClientPolicy.highlighted.connect(self.d)
        self.changeFrom = False
        self.changeTo = False

        if QtGui.qApp.userHasRight(urViewPolicyInStat):
            #pass
            self.tabNotes.cmbClientPolicy.setVisible(False)
            self.tabNotes.lblClientPolicy.setVisible(False)
        else:
            self.cmbClientPolicy.setVisible(False)
            self.lblClientPolicy.setVisible(False)

        self.postSetupUi()
        self.groupIdCache = {}

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

    def on_cmbClientPolicy_currentIndexChanged(self):
        if not self.changeTo:
            if self.cmbClientPolicy._policyId:
                if self.tabNotes.cmbClientPolicy._policyId != self.cmbClientPolicy._policyId:
                    # self.tabNotes.cmbClientPolicy.setCurrentIndex(self.cmbClientPolicy.currentIndex())
                    self.tabNotes.cmbClientPolicy._policyId = self.cmbClientPolicy._policyId
                    self.tabNotes.cmbClientPolicy.setEditText(self.cmbClientPolicy.currentText())
                    #self.tabNotes.cmbClientPolicy.updatePolicy()
                    self.changeFrom = True
        else:
            self.changeTo = False

    def on_cmbClientPolicy_currentIndexChanged_from_notes(self):
        if not self.changeFrom:
            if self.tabNotes.cmbClientPolicy._policyId != self.cmbClientPolicy._policyId:
                # self.cmbClientPolicy.setCurrentIndex(self.tabNotes.cmbClientPolicy.currentIndex())
                self.cmbClientPolicy._policyId = self.tabNotes.cmbClientPolicy._policyId
                self.cmbClientPolicy.setEditText(self.tabNotes.cmbClientPolicy.currentText())
                #self.cmbClientPolicy.updatePolicy()
                self.changeTo = True
        else:
            self.changeFrom = False

    def postInitSetup(self):
        self.takenTissueRecord = None
        self.setActionTypeIdListInTabActions()
        self.actionsCacheByCode = {}
        self.actionsCodeCacheByName = {}
        self.selectedActionTypeIdList = []
        self.enabledActionTypes = []
        self.existsTypes = []
        self.focusOnAdd = False
        self.treeActionTypeGroups.updateExpandState()
        index = self.modelActionTypeGroups.createIndex(0, 0, self.modelActionTypeGroups.getRootItem())
        self.selectionModelActionTypeGroups.select(index, self.selectionModelActionTypeGroups.Toggle)
        self.on_selectionModelActionTypeGroups_currentChanged(index)
        self.totalAddedCount = 0
        self.nextStep = False

        self.plannedActionTypes = []
        self.setupDirtyCather()
#        self.defineConditionSettings()
        self.isSetConditionSettings = False
        printer = QtGui.qApp.labelPrinter()
        self.btnPrintLabel.setEnabled(self.labelTemplate is not None and bool(printer))

    def makeNextStep(self):
        self.nextStep = True
        self.accept()

    def updateSelectedCount(self):
        n = len(self.selectedActionTypeIdList)
        if self.totalAddedCount == 0:
            if n == 0:
                msg = u'ничего не выбрано'
            else:
                msg = u'выбрано '+formatNum(n, [u'действие', u'действия', u'действий'])
        else:
            if n == 0:
                msg = u'Добавлено '+formatNum(self.totalAddedCount, [u'действие', u'действия', u'действий'])
            else:
                msg = u'выбрано '+formatNum(n, [u'действие', u'действия', u'действий'])
        self.lblSelectedCount.setText(msg)

    def defineConditionSettings(self):
        setPersonId = self.cmbSetPerson.value()
        orgStructureId = None
        specialityId = QtGui.qApp.userSpecialityId
        if not specialityId and setPersonId:
            specialityId = forceRef(QtGui.qApp.db.translate('Person', 'id', setPersonId, 'speciality_id'))
        if specialityId:
            self.specialityId = specialityId
        else:
            self.specialityId = None

        if QtGui.qApp.currentOrgStructureId():
            orgStructureId = QtGui.qApp.currentOrgStructureId()
            self.planner = False
        else:
            plannedActionTypes = self.getPlannedActionTypes()
            if plannedActionTypes:
                self.planner = True
            else:
                self.planner = False
                if QtGui.qApp.userSpecialityId:
                    orgStructureId = QtGui.qApp.userOrgStructureId
                elif setPersonId:
                    orgStructureId = forceRef(QtGui.qApp.db.translate('Person', 'id', setPersonId, 'orgStructure_id'))
        if orgStructureId:
            self.orgStructureId = orgStructureId
        else:
            self.orgStructureId = None

    def getActionTypesByTissueType(self):
        tissueTypeId = self.cmbTissueType.value()
        if tissueTypeId:
            db = QtGui.qApp.db
            table = db.table('ActionType_TissueType')
            cond = [table['tissueType_id'].eq(tissueTypeId)]
            idList = db.getDistinctIdList(table, 'master_id', cond)
            idList = db.getTheseAndParents('ActionType', 'group_id', idList)
            return idList
        return []

    def getPlannedActionTypes(self, exists=None):
        if not exists:
            exists = []
        if True:  # self.plannedActionTypes is None:
            db = QtGui.qApp.db
            table = db.table('EventType_Action')
            cond = [table['eventType_id'].eq(self.eventTypeId),
                    table['actionType_id'].isNotNull()
                   ]
            specialityId = self.specialityId
            if specialityId:
                cond.append(db.joinOr([table['speciality_id'].eq(specialityId),
                                       table['speciality_id'].isNull()]))
            else:
                cond.append(table['speciality_id'].isNull())
            if exists:
                cond.append(table['actionType_id'].notInlist(exists))
            idList = db.getIdList(table,
                               'actionType_id',
                               cond
                               )
            idList = db.getTheseAndParents('ActionType', 'group_id', idList)
            self.plannedActionTypes = set(idList)
        return self.plannedActionTypes

    def resetSettings(self):
        self.tabActions.modelAPActions._items = []
        self.tabActions.modelAPActions.reset()
        self.tblActions.setModel(None)
        self.addModels('ActionsSummary', CFxxxActionsSummaryModel(self, True))
        self.tblActions.setModel(self.modelActionsSummary)
        self.modelActionsSummary.addModel(self.tabActions.modelAPActions)
        self.tabNotes.edtEventNote.clear()
        self.edtEndDate.clearEditText()

    def exec_(self):
        self.preMakeNewEvent()
        if not self.prepareSettings:
            self.btnNextStep.setEnabled(False)
        self.recountActualByTissueType()
        result =  CEventEditDialog.exec_(self)
        if result:
            if not self.nextStep:
                return result
            else:
                self.postInitSetup()
                self.resetSettings()
                self._id = None
                self._record = None
                self.prepareFromCycle(**self.prepareSettings)
                self.defineConditionSettings()
                return self.exec_()
        return result

    def preMakeNewEvent(self):
        if not self.itemId():
            if self.cmbContract.model().rowCount() > 1:
                self.cmbContract.setFocus()
            else:
                self.cmbSetPerson.setFocus()
            self.updateTreeData()
        else:
            self.cmbSetPerson.setFocus()

    def setTabActionsSettings(self):
        self.tabActions.on_actAPActionsAdd_triggered = self.toDoNone
        for a in self.tabActions.tblAPActions.popupMenu().actions():
            if a.shortcut() == QtCore.Qt.Key_F9:
                self.tabActions.tblAPActions.popupMenu().removeAction(a)

    def toDoNone(self):
        pass

    def modelAPActionsAmountChanged(self):
        self.updateTreeData(True)
        self.recountActualByTissueType()

    def setSelected(self, actionTypeId, value):
        self.focusOnAdd = True
        CActionTypesSelectionManager.setSelected(self, actionTypeId, value)

    def eventFilter(self, obj, event):
        if obj == self.treeActionTypeGroups:
            if event.type() == QtCore.QEvent.KeyPress:
#                if event.modifiers() != QtCore.Qt.ControlModifier:
                self.edtFindByCode.keyPressEvent(event)
                return True
            return False
        else:
            if event.type() == QtCore.QEvent.KeyPress:
                key = event.key()
                if key == QtCore.Qt.Key_Space:
                    index = self.tblActionTypes.currentIndex()
                    currentValue = forceInt(self.modelActionTypes.data(
                                            self.modelActionTypes.createIndex(index.row(), 0),
                                            QtCore.Qt.CheckStateRole))
                    value = 2 if currentValue == 0 else 0
                    if self.modelActionTypes.setData(index, value, QtCore.Qt.CheckStateRole):
                        self.edtFindByCode.selectAll()
                    self.tblActionTypes.model().emitDataChanged()
                    return True
        return False

    def needAddSelected(self):
        if self.focusOnAdd:
            self.on_btnAdd_clicked()
            self.focusOnAdd = False
            return True
        return False

    def keyPressEvent(self, event):
        modifier = event.modifiers()
        key = event.key()
        if event.type() == QtCore.QEvent.KeyPress:
            if not key in [QtCore.Qt.Key_Control, QtCore.Qt.Key_Alt, QtCore.Qt.Key_Shift]:
                if self.tabWidget.currentWidget() == self.tabToken:
                    self.edtFindByCode.setFocus()
                    self.edtFindByCode.keyPressEvent(event)
            if key == QtCore.Qt.Key_F9:
                CItemEditorBaseDialog.keyPressEvent(self, event)
            elif key in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
                if modifier == QtCore.Qt.ControlModifier:
                    if bool(self.itemId()):
                        if not self.needAddSelected():
                            self.accept()
                    else:
                        if not self.needAddSelected():
                            self.makeNextStep()
                else:
                    if not self.needAddSelected():
                        self.accept()
            elif key == QtCore.Qt.Key_F2:
                if self.tabWidget.currentWidget() == self.tabToken:
                    self.tblActionTypes.setFocus(QtCore.Qt.ShortcutFocusReason)
                CItemEditorBaseDialog.keyPressEvent(self, event)
            elif key in [QtCore.Qt.Key_Up, QtCore.Qt.Key_Down]:
                self.tblActionTypes.keyPressEvent(event)
                CItemEditorBaseDialog.keyPressEvent(self, event)
            else:
                CItemEditorBaseDialog.keyPressEvent(self, event)
        else:
            CItemEditorBaseDialog.keyPressEvent(self, event)

    def setActionTypeClasses(self, actionTypeClasses):
        self.actionTypeClasses = actionTypeClasses
        self.modelActionTypeGroups.setClasses(actionTypeClasses)
        self.modelActionTypeGroups.setClassesVisible(len(actionTypeClasses)>1)

    def setActionTypeIdListInTabActions(self):
        db = QtGui.qApp.db
        tableActionType = db.table('ActionType')
        self.tabActions.modelAPActions.actionTypeIdList = db.getIdList('ActionType', 'id',  [tableActionType['deleted'].eq(0)])

    def prepareFromCycle(self, contractId, clientId, eventTypeId, orgId, personId, eventSetDatetime, eventDatetime,
                         includeRedDays, numDays, presetDiagnostics, presetActions, disabledActions, externalId,
                         assistantId, curatorId, movingActionTypeId=None, valueProperties=None,
                         contractIdToCmbContract=None):
        if not valueProperties:
            valueProperties = []
        if contractIdToCmbContract:
            self.cmbContract.setValue(contractIdToCmbContract)
        return self._prepare(contractId, clientId, eventTypeId, orgId, personId, eventSetDatetime, eventDatetime, includeRedDays, numDays, presetDiagnostics, presetActions, disabledActions, externalId, assistantId, curatorId, movingActionTypeId, valueProperties)

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
        self.eventSetDateTime = eventSetDatetime
        self.eventDate = eventDatetime
        self.setOrgId(orgId if orgId else QtGui.qApp.currentOrgId())
        self.setEventTypeId(eventTypeId)
        self.setClientId(clientId)
        self.prolongateEvent = True if actionByNewEvent else False
        self.setExternalId(externalId)
        if getEventIsTakenTissue(self.eventTypeId):
            self.cmbTissueExecPerson.setValue(personId)
            if self.clientSex and self.clientSex != 0:
                cmbTissueTypeFilter = 'sex IN (0,%d)'%self.clientSex
                tissueTypeId = self.cmbTissueType.value()
                self.cmbTissueType.setFilter(cmbTissueTypeFilter)
                self.cmbTissueType.setValue(tissueTypeId)
            datetimeTaken = self.eventSetDateTime
            self.edtTissueDate.setDate(datetimeTaken.date())
            self.edtTissueTime.setTime(datetimeTaken.time())
        self.cmbSetPerson.setValue(personId)
        self.setRecommendations(recommendationList)

        self.initFocus()
        self.tabNotes.setNotesEx(externalId, assistantId, curatorId, relegateOrgId, referrals = referrals)
        self.prepareActions(contractId, presetActions, disabledActions, movingActionTypeId, valueProperties, diagnos, financeId, protocolQuoteId, actionByNewEvent)
        self.setIsDirty(False)
        self.tabNotes.setEventEditor(self)
        self.initGoal()
        self.setContract()
        if QtGui.qApp.isCheckMKB() and hasattr(self, 'modelDiagnostics'):
            self.updateMKB()
        return self.checkEventCreationRestriction()

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
        self.setContract()
        plannerDate = self.getPlannerDate(eventSetDatetime, eventDatetime)
        if QtGui.qApp.userHasAnyRight([urAccessF001planner]):
            dlg = CPreF001Dialog(self, self.contractTariffCache)
            dlg.prepare(clientId, eventTypeId, plannerDate, self.personId, self.personSpecialityId,
                        self.personTariffCategoryId, flagHospitalization, movingActionTypeId, tissueTypeId,
                        recommendationList, useDiagnosticsAndActionsPresets=useDiagnosticsAndActionsPresets)
            if dlg.diagnosticsTableIsNotEmpty() or dlg.actionsTableIsNotEmpty():
                if not dlg.exec_():
                    return False
            self.prepareSettings = {'contractId':dlg.contractId, 'clientId':clientId, 'eventTypeId':eventTypeId, 'orgId':orgId, 'personId':personId, 'eventSetDatetime':eventSetDatetime, 'eventDatetime':eventDatetime, 'includeRedDays':includeRedDays, 'numDays':numDays, 'presetDiagnostics':None, 'presetActions':None, 'disabledActions':None, 'externalId':externalId, 'assistantId':assistantId, 'curatorId':curatorId, 'movingActionTypeId':movingActionTypeId, 'valueProperties':valueProperties}

            result = self._prepare(dlg.contractId, clientId, eventTypeId, orgId, personId, eventSetDatetime, eventDatetime, includeRedDays, numDays, dlg.diagnostics(), dlg.actions(), dlg.disabledActionTypeIdList, externalId, assistantId, curatorId, movingActionTypeId, valueProperties, relegateOrgId, diagnos, financeId, protocolQuoteId, actionByNewEvent, referrals=referrals, isAmb=isAmb, recommendationList=recommendationList)
            if result and dlg.contractId:
                contractFinanceId = forceRef(QtGui.qApp.db.translate('Contract', 'id', dlg.contractId, 'finance_id'))
                if contractFinanceId == getEventFinanceId(eventTypeId):
                    self.cmbContract.setValue(dlg.contractId)
                    self.prepareSettings.update({'contractIdToCmbContract':dlg.contractId})
                else:
                    self.prepareSettings.update({'contractIdToCmbContract':None})
            else:
                self.prepareSettings.update({'contractIdToCmbContract':None})
            self.cmbTissueType.setValue(tissueTypeId)
            if selectPreviousActions:
                self.selectPreviousActions()
            return result
        else:
            presets = CPreF001DagnosticAndActionPresets(clientId, eventTypeId, plannerDate, self.personSpecialityId,
                                                        flagHospitalization, movingActionTypeId, recommendationList,
                                                        useDiagnosticsAndActionsPresets=useDiagnosticsAndActionsPresets)

            result = self._prepare(None, clientId, eventTypeId, orgId, personId, eventSetDatetime, eventDatetime, includeRedDays, numDays,
                                   presets.unconditionalDiagnosticList, presets.unconditionalActionList, presets.disabledActionTypeIdList,
                                   externalId, assistantId, curatorId, None, [], relegateOrgId, diagnos, financeId, protocolQuoteId, actionByNewEvent,
                                   referrals=referrals, isAmb=isAmb, recommendationList=recommendationList)
            if result:
                self.cmbTissueType.setValue(tissueTypeId)
                if selectPreviousActions:
                        self.selectPreviousActions()
            self.tblActionTypes.model().emitDataChanged()
            return result

    def selectPreviousActions(self):
        actionTypeIdList = QtGui.qApp.db.getDistinctIdList('Action', 'actionType_id', 'event_id=(SELECT MAX(id) FROM Event WHERE eventType_id=%d)'%self.eventTypeId)
        currentIdList = self.tblActionTypes.model().idList()
        for actionTypeId in actionTypeIdList:
            if actionTypeId in currentIdList:
                self.setSelected(actionTypeId, True)

    def setOrgId(self, orgId):
        self.orgId = orgId
        self.cmbContract.setOrgId(orgId)
        self.tabActions.setOrgId(orgId)

    def setEventTypeId(self, eventTypeId):
        CEventEditDialog.setEventTypeId(self, eventTypeId, u'Ф.001')
        self.tabCash.windowTitle = self.windowTitle()
        if not getEventIsTakenTissue(eventTypeId):
            self.grpTakenTissue.setVisible(False)
        else:
            self.grpTakenTissue.setVisible(True)
        showTime = getEventShowTime(eventTypeId)
        self.edtBegTime.setVisible(showTime)
        self.edtEndTime.setVisible(showTime)
        customizePrintButton(self.btnPrint, self.eventContext if self.eventContext else 'F001')

    def prepareEisWidgets(self):
        self.grpFinalDiagnostics.setVisible(False)
        self.lblResult.setVisible(False)
        self.cmbResult.setVisible(False)
        self.lblGoal.setVisible(False)
        self.cmbGoal.setVisible(False)

    def setExternalId(self, externalId):
        self.lblValueExternalId.setText((u'Внешний идентификатор: ' + externalId) if externalId else '')

    def initFocus(self):
        if self.cmbContract.count() != 1:
            self.cmbContract.setFocus(QtCore.Qt.OtherFocusReason)

    def prepareActions(self, contractId, presetActions, disabledActions, actionTypeIdValue, valueProperties, diagnos, financeId, protocolQuoteId, actionByNewEvent):
        def addActionType(actionTypeId, amount, financeId, contractId, idListActionType, idListActionTypeIPH, actionFinance, idListActionTypeMoving, org_id):
            for tab in self.getActionsTabsList():
                model = tab.modelAPActions
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

    def setRecord(self, record):
        CEventEditDialog.setRecord(self, record)
        setDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'setDate')
        setDatetimeEditValue(self.edtEndDate, self.edtEndTime, record, 'execDate')
        setRBComboBoxValue(self.cmbSetPerson, record, 'setPerson_id')
        self.setPersonId(self.cmbSetPerson.value())
        self.setContract()
        self.setExternalId(forceString(record.value('externalId')))
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
        self.loadActions()
        self.loadTakenTissue()
        if self.takenTissueRecord:
            self.setTissueWidgetsEditable(False)
            self.modelActionTypes.setTissueTypeId(self.cmbTissueType.value())
        self.tabCash.load(self.itemId())
        self.tabNotes.setNotes(record)

        setRBComboBoxValue(self.cmbClientPolicy, record, 'clientPolicy_id')
        self.cmbClientPolicy.setClientId(self.clientId)
        self.cmbClientPolicy.setPolicyFromRepresentative(isLittleStranger(self.clientId, forceDate(record.value('setDate')), forceDate(record.value('execDate'))))
        self.updateClientPolicy(record)

        self.tabNotes.setEventEditor(self)
        self.tabNotes.updateReferralPeriod(self.edtBegDate.date())
        self.initFocus()
        self.setIsDirty(False)
        self.updateTreeData()
        self.setEditable(self.getEditable())
        setOrgStructureIdToCmbPerson(self.cmbSetPerson)

    def setEditable(self, editable):
        self.modelActionsSummary.setEditable(editable)
        self.tabCash.setEditable(editable)
        self.tabNotes.setEditable(editable)
        self.tabActions.setEditable(editable)
        self.grpBase.setEnabled(editable)
        self.modelActionTypes.setEditable(editable)
        self.grpActionSearch.setEnabled(editable)

    def updateClientPolicy(self, record):
        if record is None:
            self.cmbClientPolicy.updatePolicy()
            return

        execDate = forceDate(record.value('execDate'))
        eventIsClosed = not execDate.isNull()
        eventIsPayed = getRealPayed(forceInt(record.value('payStatus')))

        if eventIsPayed or (eventIsClosed and not QtGui.qApp.userHasRight(urEditClientPolicyInClosedEvent)):
            self.cmbClientPolicy.setEnabled(False)
        else:
            self.cmbClientPolicy.setEventIsClosed(eventIsClosed)
            self.cmbClientPolicy.setDate(execDate if eventIsClosed else QtCore.QDate.currentDate())

            if getEventFinanceCode(forceRef(record.value('eventType_id'))) == 3:  # ДМС
                franchisPolicyTypeId = forceRef(QtGui.qApp.db.translate('rbPolicyType', 'code', 'franchis', 'id'))
                if franchisPolicyTypeId:
                    self.cmbClientPolicy.setPolicyTypeId(franchisPolicyTypeId)
                    self.cmbClientPolicy.updatePolicy()
                    if not self.cmbClientPolicy.value():
                        self.cmbClientPolicy.setPolicyTypeId(forceRef(QtGui.qApp.db.translate('rbPolicyType', 'code', '3', 'id')))
                        self.cmbClientPolicy.updatePolicy()
            else:
                self.cmbClientPolicy.updatePolicy()

    def checkSpecialityExists(self, cmbPersonFind, personId):
        specialityId = forceRef(QtGui.qApp.db.translate('Person', 'id', personId, 'speciality_id'))
        if not specialityId:
            cmbPersonFind.setSpecialityIndependents()

    def loadTakenTissue(self):
        if self.takenTissueRecord:
            self.cmbTissueType.blockSignals(True)
            self.edtTissueDate.blockSignals(True)
            execPersonId = forceRef(self.takenTissueRecord.value('execPerson_id'))
            self.checkSpecialityExists(self.cmbTissueExecPerson, execPersonId)
            self.cmbTissueType.setValue(forceRef(self.takenTissueRecord.value('tissueType_id')))
            self.edtTissueExternalId.setText(forceString(self.takenTissueRecord.value('externalId')))
            self.edtTissueNumber.setText(forceString(self.takenTissueRecord.value('number')))
            self.edtTissueAmount.setValue(forceInt(self.takenTissueRecord.value('amount')))
            self.cmbTissueUnit.setValue(forceRef(self.takenTissueRecord.value('unit_id')))
            self.cmbTissueExecPerson.setValue(execPersonId)
            self.edtTissueNote.setText(forceString(self.takenTissueRecord.value('note')))
            datetimeTaken = forceDateTime(self.takenTissueRecord.value('datetimeTaken'))
            self.edtTissueDate.setDate(datetimeTaken.date())
            self.edtTissueTime.setTime(datetimeTaken.time())
            self.edtTissueExternalId.setReadOnly(True)
            self.cmbTissueType.blockSignals(False)
            self.edtTissueDate.blockSignals(False)
        else:
            self.setTissueWidgetsEditable(True)
            self.edtTissueExternalId.setReadOnly(False)

    def setTissueWidgetsEditable(self, val):
        self.cmbTissueType.setEnabled(val)
        self.edtTissueExternalId.setEnabled(val)
        self.edtTissueNumber.setEnabled(val)
        self.edtTissueAmount.setEnabled(val)
        self.cmbTissueUnit.setEnabled(val)
        self.cmbTissueExecPerson.setEnabled(val)
        self.edtTissueNote.setEnabled(val)
        self.edtTissueDate.setEnabled(val)
        self.edtTissueTime.setEnabled(val)

    def loadActions(self):
        eventId = self.itemId()
        self.tabActions.loadActions(eventId)
        if getEventIsTakenTissue(self.eventTypeId):
            for record, action in self.tabActions.modelAPActions.items():
                takenTissueJournalId = forceRef(record.value('takenTissueJournal_id'))
                if takenTissueJournalId:
                    self.takenTissueRecord = QtGui.qApp.db.getRecord('TakenTissueJournal', '*', takenTissueJournalId)
                    break
        self.modelActionsSummary.regenerate()
        self.tabCash.modelAccActions.regenerate()

    def getRecord(self):
        record = CEventEditDialog.getRecord(self)
        showTime = getEventShowTime(self.eventTypeId)
        getRBComboBoxValue(self.cmbContract,    record, 'contract_id')
        getDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'setDate', showTime)
        getRBComboBoxValue(self.cmbSetPerson,      record, 'setPerson_id')
        getDatetimeEditValue(self.edtEndDate, self.edtEndTime, record, 'execDate', showTime)
        getRBComboBoxValue(self.cmbSetPerson,      record, 'execPerson_id')
        record.setValue('order', toVariant(1))
        self.tabNotes.getNotes(record, self.eventTypeId)
        getRBComboBoxValue(self.cmbClientPolicy, record, 'clientPolicy_id')
        record.setValue('isPrimary', toVariant(1))
        if self.prolongateEvent:
            record.setValue('order', toVariant(5))
            record.setValue('prevEvent_id', toVariant(self.prevEventId))
        self.saveTakenTissueRecord()
        return record

    def hasAnyAction(self):
        tabs = [self.tabActions]
        for tab in tabs:
            if self.hasTabAnyAction(tab):
                return True
        return False

    def hasTabAnyAction(self, tab):
        return bool(len(tab.modelAPActions.items()))

    def saveTakenTissueRecord(self):
        if getEventIsTakenTissue(self.eventTypeId):
            canBeSaved = bool(not self.takenTissueRecord) and bool(self.cmbTissueType.value()) and self.hasAnyAction()
            if canBeSaved:
                table = QtGui.qApp.db.table('TakenTissueJournal')
                record = table.newRecord()
                record.setValue('client_id', QtCore.QVariant(self.clientId))
                record.setValue('tissueType_id', QtCore.QVariant(self.cmbTissueType.value()))
                record.setValue('externalId', QtCore.QVariant(self.edtTissueExternalId.text()))
                record.setValue('number', QtCore.QVariant(self.edtTissueNumber.text()))
                record.setValue('amount', QtCore.QVariant(self.edtTissueAmount.value()))
                record.setValue('unit_id', QtCore.QVariant(self.cmbTissueUnit.value()))
                execPersonId = self.cmbTissueExecPerson.value()
                if not execPersonId:
                    execPersonId = QtGui.qApp.userId
                record.setValue('execPerson_id', QtCore.QVariant(execPersonId))
                record.setValue('note', QtCore.QVariant(self.edtTissueNote.text()))
                datetimeTaken = QtCore.QDateTime()
                datetimeTaken.setDate(self.edtTissueDate.date())
                datetimeTaken.setTime(self.edtTissueTime.time())
                record.setValue('datetimeTaken', QtCore.QVariant(datetimeTaken))
                QtGui.qApp.db.insertRecord(table, record)
                self.takenTissueRecord = record

    def getSetPersonId(self):
        return self.cmbSetPerson.value()

    def getEventInfo(self, context):
        result = CEventEditDialog.getEventInfo(self, context)
        # инициализация свойств
        result._isPrimary = True
        # инициализация таблиц
        result._actions = CActionInfoProxyList(context,
                [self.tabActions.modelAPActions],
                result)
        result._diagnosises = CDiagnosticInfoProxyList(context, [])
        return result

    def saveInternals(self, eventId):
        super(CF001Dialog, self).saveInternals(eventId)
        self.saveActions(eventId)
        self.tabCash.save(eventId)
        self.updateRecommendations()

    def saveActions(self, eventId):
        if self.takenTissueRecord:
            tissueType = forceRef(self.takenTissueRecord.value('tissueType_id'))
            actionTypeIdList = self.actualByTissueType.get(tissueType, ([], []))[1]
            id = forceRef(self.takenTissueRecord.value('id'))
            self.tabActions.setCommonTakenTissueJournalRecordId(id, actionTypeIdList)
        # self.tabNotes.saveOutgoingRef(eventId)
        self.tabActions.saveActions(eventId)

    def setAPSetPersonWhereNot(self):
        items = self.tabActions.modelAPActions.items()
        for item, action in items:
            if not forceRef(item.value('setPerson_id')):
                item.setValue('setPerson_id', QtCore.QVariant(self.cmbSetPerson.value()))

    def checkDataEntered(self):
        result = CEventEditDialog.checkDataEntered(self)
        begDate = self.edtBegDate.date()
        endDate = self.edtEndDate.date() if self._isClosedEventCheck else QtCore.QDate()
        self.actionsRowNotForAdding = {}
        result = result and self.checkSelectedActions()
        result = result and (not self.edtEndDate.date().isNull() or self.checkEndDate())
        result = result and (self.cmbSetPerson.value() or self.checkInputMessage(u'назначившего', False, self.cmbSetPerson))
        if getEventIsTakenTissue(self.eventTypeId):
            result = result and (self.cmbTissueType.value() or self.checkInputMessage(u'тип ткани', True, self.cmbTissueType))
            if self.edtTissueAmount.value() > 0:
                result = result and (self.cmbTissueUnit.value() or self.checkInputMessage(u'ед. измерения', True, self.cmbTissueUnit))
            result = result and self.checkIsSameTissueTypeExistsTodayForCurrentClient()
        result = result and self.checkActionsDataEntered([self.tabActions], begDate, endDate)
        result = result and self.checkSaveTakenTissue()
        result = result and self.checkUniqueTissueExternalId()
        result = result and self.tabCash.checkDataLocalContract()
        result = result and self.checkTabNotesReferral()
        if not result:
            self.updateTreeData()
        else:
            self.setAPSetPersonWhereNot()
        self.removeRowsForModel(self.actionsRowNotForAdding)
        return result

    def checkSelectedActions(self):
        if len(self.selectedActionTypeIdList) > 0:
            buttons = QtGui.QMessageBox.Ok | QtGui.QMessageBox.Ignore | QtGui.QMessageBox.Cancel
            res = QtGui.QMessageBox.warning( self,
                                             u'Внимание',
                                             u'Имееются выделенные и не добавленные действия.\nДобавить?',
                                             buttons,
                                             QtGui.QMessageBox.Cancel)
            if res == QtGui.QMessageBox.Ok:
                self.on_btnAdd_clicked()
                self.focusOnAdd = False
            elif res == QtGui.QMessageBox.Cancel:
                return False
        return True

    def checkUniqueTissueExternalId(self):
        if not bool(self.takenTissueRecord):
            tissueType = self.cmbTissueType.value()
            if not tissueType:
                return True
            needCountValueStr = unicode(self.edtTissueExternalId.text()).lstrip('0')
            if not self.isValidExternalId(needCountValueStr):
                return False
            needCountValue = int(needCountValueStr)
            if self._manualInputExternalId:
                existCountValue = needCountValue
            else:
                existCountValue = needCountValue - 1
            if existCountValue < 0:
                return self.checkInputMessage(u'другой идентификатор больше нуля', False, self.edtTissueExternalId)
            self.setTissueExternalId(existCountValue)
            date = self.edtTissueDate.date()
            if date.isValid():
                cond = [self.takenTissueJournalTable['deleted'].eq(0),
                        self.takenTissueJournalTable['tissueType_id'].eq(tissueType),
                        self.takenTissueJournalTable['externalId'].eq(self.edtTissueExternalId.text())]
                dateCond = self.getRecountExternalIdDateCond(tissueType, date)
                if dateCond:
                    cond.append(dateCond)
                record = QtGui.qApp.db.getRecordEx(self.takenTissueJournalTable, 'id', cond)
                if record and forceRef(record.value('id')):
                    return self.checkInputMessage(u'другой идентификатор.\nТакой уже существует', False, self.edtTissueExternalId)
        return True

    def isValidExternalId(self, needCountValueStr):
        if not needCountValueStr.isdigit():
            return self.checkInputMessage(u'корректный идентификатор.', False, self.edtTissueExternalId)
        return True

    def checkSaveTakenTissue(self):
        tissueType = self.cmbTissueType.value()
        if bool(tissueType):
            actionTypeIdList = self.actualByTissueType.get(tissueType, ([], []))[1]
            if not bool(actionTypeIdList):
                res = self.makeMessageBox(u'Нет соответствующих ткани добавленных действий, забор ткани не зафиксируется!')
                if res == QtGui.QMessageBox.Ok:
                    self.setFocusToWidget(self.tblActionTypes, None, None)
                    return False
        return True

    def checkValueMessageIsSameTissue(self):
        title   = u'Внимание!'
        message = u'Сегодня у данного пациента уже был забор ткани этого типа!\nИспользовать данные предыдущего забора?'
        buttons = QtGui.QMessageBox.Ok | QtGui.QMessageBox.Ignore | QtGui.QMessageBox.Cancel
        res = QtGui.QMessageBox.warning( self,
                                         title,
                                         message,
                                         buttons,
                                         QtGui.QMessageBox.Cancel)
        return res

    def checkIsSameTissueTypeExistsTodayForCurrentClient(self):
        if not bool(self.takenTissueRecord):
            tissueTypeId = self.cmbTissueType.value()
            date = self.edtTissueDate.date()
            cond = [self.takenTissueJournalTable['client_id'].eq(self.clientId),
                    self.takenTissueJournalTable['tissueType_id'].eq(tissueTypeId),
                    self.takenTissueJournalTable['datetimeTaken'].dateEq(date),
                    'EXISTS (SELECT id FROM Action WHERE Action.`deleted`=0 AND Action.`takenTissueJournal_id` = TakenTissueJournal.`id`)']
            record = QtGui.qApp.db.getRecordEx(self.takenTissueJournalTable, '*', cond, 'datetimeTaken DESC')
            if record:
                res = self.checkValueMessageIsSameTissue()
                if res == QtGui.QMessageBox.Cancel:
                    self.setFocusToWidget(self.cmbTissueType, None, None)
                    return False
                elif res == QtGui.QMessageBox.Ok:
                    self.takenTissueRecord = record
                    self.loadTakenTissue()
                    self.setTissueWidgetsEditable(False)
        return True

    def checkExistsActionsForCurrentDay(self, row, record, action, actionTab):
        db = QtGui.qApp.db
        tableAction = db.table('Action')
        tableEvent = db.table('Event')
        endDate = forceDate(record.value('endDate'))
        if not endDate.isValid():
            return True
        actionTypeId = forceRef(record.value('actionType_id'))
        cond = [tableEvent['client_id'].eq(self.clientId),
                tableAction['endDate'].eq(endDate),
                tableEvent['deleted'].eq(0),
                tableAction['deleted'].eq(0)]
        eventId = self.itemId()
        if eventId:
            cond.append(tableEvent['id'].ne(eventId))
        cond.append(tableAction['actionType_id'].eq(actionTypeId))
        stmt = 'SELECT Action.`id` From Action INNER JOIN ActionType ON ActionType.`id`=Action.`actionType_id` INNER JOIN Event ON Event.`id`=Action.`event_id` WHERE %s' % db.joinAnd(cond)
        query = db.query(stmt)
        if query.first():
            res = self.askActionExistingQuestion(actionTab.tblAPActions, row, action._actionType.name)
            if not res:
                return False
        return True

    def checkDiagnosticDoctorEntered(self, table, row, record):
        return True

    def removeRowsForModel(self, modelsRows):
        for model in modelsRows:
            rows = modelsRows.get(model)
            if rows:
                rows.sort(reverse=True)
                for row in rows:
                    model.removeRow(row)

    def askActionExistingQuestion(self, tbl, row, actionTypeName):
        buttons = QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ignore
        res = QtGui.QMessageBox.question(self, u'Внимание!', u'Действие "%s" уже было выполненно с данным пациентом в этот день!'%actionTypeName, buttons, QtGui.QMessageBox.Ok)
        if res == QtGui.QMessageBox.Ok:
            self.setFocusToWidget(tbl, row, 0)
            return False
        elif res == QtGui.QMessageBox.Cancel:
            rows = self.actionsRowNotForAdding.get(tbl.model())
            if rows:
                rows.append(row)
            else:
                self.actionsRowNotForAdding[tbl.model()] = [row]
        return True

    def checkEndDate(self):
        res = self.makeMessageBox(u'Нужно ввести дату выполнения!', u'Сегодняшняя дата')
        if res == QtGui.QMessageBox.Ok:
            self.setFocusToWidget(self.edtEndDate, None, None)
            return False
        elif res == 0:
            self.edtEndDate.setDate(QtCore.QDate.currentDate())
        return True

    def makeMessageBox(self, question, btnText=None):
        buttons = QtGui.QMessageBox.Ok
        buttons = buttons | QtGui.QMessageBox.Ignore
        messageBox = QtGui.QMessageBox()
        messageBox.setWindowTitle(u'Внимание!')
        messageBox.setText(question)
        messageBox.setStandardButtons(buttons)
        messageBox.setDefaultButton(QtGui.QMessageBox.Ok)
        if btnText:
            messageBox.addButton(QtGui.QPushButton(btnText), QtGui.QMessageBox.ActionRole)
        return messageBox.exec_()

    def updateTreeData(self, adding=False):
        if not self.isSetConditionSettings:
            self.defineConditionSettings()
            self.isSetConditionSettings = True
        existsTypes = []
        inServicetabItems = self.tabActions.modelAPActions.items()
        for i in inServicetabItems:
            typeId = forceRef(i[0].value('actionType_id'))
            if typeId not in existsTypes:
                existsTypes.append(typeId)
        self.existsTypes = existsTypes
        db = QtGui.qApp.db
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        if self.clientSex and self.clientAge:
            self.modelActionTypeGroups.setFilter(self.clientSex, self.clientAge)
        else:
            self.modelActionTypeGroups.setFilter(0, None)
        tableActionType = db.table('ActionType')

        index = self.treeActionTypeGroups.currentIndex() if adding else None

        cond = [tableActionType['deleted'].eq(0)]
        if existsTypes:
            cond.append(tableActionType['id'].notInlist(existsTypes))
        if not self.planner:
            self.enabledActionTypes = enabledActionTypes = self.getOrgStructureActionTypes(existsTypes)
        elif self.planner:
            self.enabledActionTypes = enabledActionTypes = self.getPlannedActionTypes(existsTypes)
        else:
            self.enabledActionTypes = enabledActionTypes = db.getIdList('ActionType', 'id',  cond)
        if getEventIsTakenTissue(self.eventTypeId):
            if bool(self.cmbTissueType.value()):
                self.actionTypesByTissueType = self.getActionTypesByTissueType()
                self.enabledActionTypes = enabledActionTypes = [id for id in self.actionTypesByTissueType if id in enabledActionTypes]
        self.modelActionTypeGroups.setEnabledActionTypeIdList(enabledActionTypes)
        if not index:
            index = self.modelActionTypeGroups.createIndex(0, 0, self.modelActionTypeGroups.getRootItem())
        self.treeActionTypeGroups.setCurrentIndex(index)
        self.on_selectionModelActionTypeGroups_currentChanged(index)
        if not self.enabledActionTypes:
            self.clearGroup()
        QtGui.qApp.restoreOverrideCursor()
#        self.treeActionTypeGroups.reset()
        self.tblActionTypes.model().emitDataChanged()
        self.treeActionTypeGroups.updateExpandState()

    def updateMKB(self):
        begDate = self.edtBegDate.date()
        filter = None
        if begDate.isValid():
            filter = {'begDate': begDate, 'clientId': self.clientId}
        cols = self.modelDiagnostics.cols()
        for col in (0, 1):
            resultCol = cols[col]
            resultCol.setFilter(filter)

    def getOrgStructureActionTypes(self, exists=None):
        if not exists:
            exists = []
        if True:#self.orgStructureActionTypes is None:
            idSet = getOrgStructureActionTypeIdSet(self.orgStructureId)-set(exists)
            idList = QtGui.qApp.db.getTheseAndParents('ActionType', 'group_id', list(idSet))
            self.orgStructureActionTypes = set(idList)
        return self.orgStructureActionTypes

    def clearGroup(self):
        self.tblActionTypes.setIdList([])

    def findByCode(self, value):
        uCode = unicode(value).upper()
        codes = self.actionsCacheByCode.keys()
        codes.sort()
        for c in codes:
            if unicode(c).startswith(uCode):
                self.edtFindByCode.setFocus()
                return self.actionsCacheByCode[c]

        return self.findByName(value)

    def findByName(self, name):
        uName = unicode(name).upper()
        names = self.actionsCodeCacheByName.keys()
        for n in names:
            if uName in n:
                code = self.actionsCodeCacheByName[n]
                return self.actionsCacheByCode.get(code, None)
        return None

    def setGroupId(self, groupId, _class=None):
        if not self.actionTypeClasses:
            return
        self.actionsCacheByCode.clear()
        self.actionsCodeCacheByName.clear()
        db = QtGui.qApp.db
        tableActionType = db.table('ActionType')

        cond = [tableActionType['deleted'].eq(0),
                tableActionType['class'].inlist(self.actionTypeClasses)
               ]
        if groupId:
            groupIdList = self.getGroupIdList([groupId], tableActionType) + [groupId]
            cond.append(tableActionType['group_id'].inlist(groupIdList))
        if _class != None:
            cond.append(tableActionType['class'].eq(_class))
        if self.enabledActionTypes:
            cond.append(tableActionType['id'].inlist(self.enabledActionTypes))
        else:
            return
#        if self.mesActionTypeIdList:
#            cond.append('NOT EXISTS(SELECT id FROM ActionType AS at WHERE ActionType.id NOT IN (%s) AND at.group_id = ActionType.id)'%(u','.join(str(mesActionTypeId) for mesActionTypeId in self.mesActionTypeIdList if mesActionTypeId)))
#        else:
        cond.append('NOT EXISTS(SELECT id FROM ActionType AS at WHERE at.group_id = ActionType.id and at.deleted = 0)')
        if self.existsTypes:
            cond.append(tableActionType['id'].notInlist(self.existsTypes))
        recordList = QtGui.qApp.db.getRecordList(tableActionType, 'id, code, name', cond, 'code, name')
        if recordList:
            idList = []
            for index, record in enumerate(recordList):
                id = forceRef(record.value('id'))
                code = forceString(record.value('code')).upper()
                name = forceString(record.value('name')).upper()
                idList.append(id)
                existCode = self.actionsCacheByCode.get(code, None)
                if existCode is None:
                    self.actionsCacheByCode[code] = id
                existName = self.actionsCodeCacheByName.get(name, None)
                if existName is None:
                    self.actionsCodeCacheByName[name] = code
        else:
            idList = []
        self.tblActionTypes.setIdList(idList)

    def getGroupIdList(self, groupIdList, table):
        if not groupIdList:
            return []
        resume = []

        for id in groupIdList:
            idList = self.groupIdCache.get('%s:%s' % (table.name(), id), None)
            if idList is None:
                cond = [table['deleted'].eq(0), table['group_id'].eq(id)]
                idList = QtGui.qApp.db.getIdList(table.name(), 'id', cond, 'code, name')
                self.groupIdCache['%s:%s' % (table.name(), id)] = idList
            if idList:
                resume.append(id)

        return resume + self.getGroupIdList(idList, table)

    def invalidateChecks(self):
        model = self.modelActionTypes
        lt = model.index(0, 0)
        rb = model.index(model.rowCount()-1, 1)
        model.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), lt, rb)

    def getEventDataPlanning(self, eventId):
        if eventId:
            db = QtGui.qApp.db
            tableEvent = db.table('Event')
            tableEventType = db.table('EventType')
            cols = [tableEvent['patientModel_id'],
                    tableEvent['cureType_id'],
                    tableEvent['cureMethod_id'],
                    tableEvent['contract_id'],
                    tableEvent['externalId'],
                    tableEvent['note'],
                    tableEvent['setDate'],
                    tableEvent['ZNOFirst'],
                    tableEvent['ZNOMorph'],
                    tableEventType['name']
                    ]
            cond = [tableEvent['deleted'].eq(0),
                    tableEvent['id'].eq(eventId),
                    tableEventType['deleted'].eq(0)
                    ]
            table = tableEvent.innerJoin(tableEventType, tableEvent['eventType_id'].eq(tableEventType['id']))
            record = db.getRecordEx(table, cols, cond)
            if record:
                patientModelId = forceRef(record.value('patientModel_id'))
                if patientModelId:
                    self.tabNotes.cmbPatientModel.setValue(patientModelId)
                    self.tabNotes.on_cmbPatientModel_currentIndexChanged(None)
                cureTypeId = forceRef(record.value('cureType_id'))
                if cureTypeId:
                    self.tabNotes.cmbCureType.setValue(cureTypeId)
                cureMethodId = forceRef(record.value('cureMethod_id'))
                if cureMethodId:
                    self.tabNotes.cmbCureMethod.setValue(cureMethodId)
                if self.prolongateEvent:
                    self.cmbContract.setValue(forceRef(record.value('contract_id')))
                    self.tabNotes.edtEventExternalIdValue.setText(forceString(record.value('externalId')))
                    self.tabNotes.edtEventNote.setText(forceString(record.value('note')))
                    self.prevEventId = eventId
                    self.lblProlongateEvent.setText(u'п')
                    self.tabNotes.edtPrevEventInfo.setText(u'Продолжение обращения: %s от %s.'%(forceString(record.value('name')), forceDate(record.value('setDate')).toString('dd.MM.yyyy')))

    def on_actAPActionsAdd_triggered(self):
        pass

    def setTissueExternalId(self, existCountValue=None):
        externalIdValue = self.recountExternalId(existCountValue, _manualInputExternalId=self._manualInputExternalId)
        self.edtTissueExternalId.setText(unicode(externalIdValue))

        if existCountValue is None and not self._manualInputExternalId:
            self.edtTissueNumber.setText(unicode(externalIdValue))
        else:
            numberValue = self.recountExternalId(existCountValue=None, _manualInputExternalId=False)
            self.edtTissueNumber.setText(unicode(numberValue))

    def recountExternalId(self, existCountValue=None, _manualInputExternalId=False):
        if self.takenTissueRecord:
            return forceString(self.takenTissueRecord.value('externalId'))

        tissueType = self.cmbTissueType.value()
        date = self.edtTissueDate.date()
        if tissueType and date.isValid():
            if _manualInputExternalId:
                return '' if existCountValue is None else existCountValue
            if existCountValue is None:
                cond = [self.takenTissueJournalTable['tissueType_id'].eq(tissueType)]
                dateCond = self.getRecountExternalIdDateCond(tissueType, date)
                if dateCond:
                    cond.append(dateCond)
                existCountValue = QtGui.qApp.db.getCount(self.takenTissueJournalTable, where=cond)
            return unicode(existCountValue+1).lstrip('0').zfill(6)
        return ''

    def getRecountExternalIdDateCond(self, tissueType, date):
        return getExternalIdDateCond(tissueType, date)

    def recountActualByTissueType(self):
        self.actualByTissueType.clear()
        actionList = []
        for record, action in self.tabActions.tblAPActions.model().items():
            actionList.append(record.value('actionType_id'))
        db = QtGui.qApp.db
        tableActionType = db.table('ActionType')
        cond = [tableActionType['id'].inlist(actionList)]
        stmt = 'SELECT DISTINCT ActionType.`id` AS actionTypeId, ActionType_TissueType.`id`, ActionType_TissueType.`tissueType_id`, ActionType_TissueType.`amount`, ActionType_TissueType.`unit_id` FROM ActionType INNER JOIN ActionType_TissueType ON ActionType_TissueType.`master_id`=ActionType.`id` WHERE %s' % db.joinAnd(cond)
        query = db.query(stmt)
        while query.next():
            record = query.record()
            tissueType = forceRef(record.value('tissueType_id'))
            actionTypeId = forceRef(record.value('actionTypeId'))

            actualByTissueTypeList, actionTypeIdList = self.actualByTissueType.get(tissueType, (None, None))
            if actualByTissueTypeList:
                actualByTissueTypeList.append(record)
                actionTypeIdList.append(actionTypeId)
            else:
                self.actualByTissueType[tissueType] = ([record], [actionTypeId])
        if not bool(self.takenTissueRecord):
            self.prepareTissueWidgets()

    def prepareTissueWidgets(self):
        tissueType = self.cmbTissueType.value()
        actualByTissueTypeList = self.actualByTissueType.get(tissueType, ([], []))[0]
        actionTypesList = []
        globalUnitId = None
        totalAmount = 0
        for actualRecord in actualByTissueTypeList:
            actionTypeId = forceRef(actualRecord.value('actionTypeId'))
            amount = forceInt(actualRecord.value('amount'))
            unitId = forceRef(actualRecord.value('unit_id'))
            if not unitId:
                continue
            if not actionTypeId in actionTypesList:
                actionTypesList.append(actionTypeId)
                if not globalUnitId:
                    globalUnitId = unitId
                else:
                    if unitId != globalUnitId:
                        continue
                totalAmount += amount
        self.edtTissueAmount.setValue(totalAmount)
        self.cmbTissueUnit.setValue(globalUnitId)
        self.cmbTissueUnit.setEnabled(not bool(globalUnitId))

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelActionTypeGroups_currentChanged(self, current, previous=None):
        if current.isValid() and current.internalPointer():
            actionTypeId = current.internalPointer().id()
            _class = current.internalPointer().class_()
        else:
            actionTypeId = None
            _class = None
        self.setGroupId(actionTypeId, _class)
        text = forceStringEx(self.edtFindByCode.text())
        if text:
            self.on_edtFindByCode_textChanged(text)

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtFindByCode_textChanged(self, text):
        if text:
            itemId = self.findByCode(text)
            if itemId is not None:
                self.tblActionTypes.setCurrentItemId(itemId)
            else:
                self.tblActionTypes.setCurrentRow(0)
        else:
            self.tblActionTypes.setCurrentRow(0)

    @QtCore.pyqtSlot()
    def on_btnSelectAll_clicked(self):
        for actionTypeId in self.modelActionTypes.idList():
            self.setSelected(actionTypeId, True)
        self.invalidateChecks()

    @QtCore.pyqtSlot()
    def on_btnClearSelection_clicked(self):
        self.selectedActionTypeIdList = []
        self.updateSelectedCount()
        self.invalidateChecks()

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        contractId = self.cmbContract.value()
        self.cmbContract.setBegDate(date)
        self.cmbContract.setEndDate(date)
        self.cmbContract.setValue(contractId)
        self.tabNotes.updateReferralPeriod(self.edtBegDate.date())
        self.updateModelsRetiredList()

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtEndDate_dateChanged(self, date):
        self.tabNotes.cmbClientPolicy.updatePolicy(date)
        if QtGui.qApp.isAutoClosed():
            self.chkIsClosed.setChecked(date != QtCore.QDate())

    @QtCore.pyqtSlot(int)
    def on_cmbTissueType_currentIndexChanged(self, index):
        tissueType = self.cmbTissueType.value()
        self._manualInputExternalId = forceBool(QtGui.qApp.db.translate('rbTissueType', 'id',
                                                              tissueType, 'counterManualInput'))
        self.setTissueExternalId()
        self.updateTreeData()
        if not bool(self.takenTissueRecord):
            self.prepareTissueWidgets()
        self.modelActionTypes.setTissueTypeId(tissueType)

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtTissueDate_dateChanged(self, date):
        if self._manualInputExternalId is None:
            tissueType = self.cmbTissueType.value()
            self._manualInputExternalId = forceBool(QtGui.qApp.db.translate('rbTissueType', 'id',
                                                                            tissueType, 'counterManualInput'))
        self.setTissueExternalId()

    @QtCore.pyqtSlot()
    def on_actScanBarcode_triggered(self):
        if not self.edtTissueExternalId.isReadOnly():
            self.edtTissueExternalId.setFocus(QtCore.Qt.OtherFocusReason)
            self.edtTissueExternalId.selectAll()

    @QtCore.pyqtSlot()
    def on_btnAdd_clicked(self):
        n = len(self.selectedActionTypeIdList)
        self.totalAddedCount += n
        for id in self.selectedActionTypeIdList:
            self.tabActions.modelAPActions.addRow(id, None, None, self.cmbContract.value())
        self.selectedActionTypeIdList = []
        self.updateTreeData(True)
        self.updateSelectedCount()
        self.recountActualByTissueType()

    @QtCore.pyqtSlot()
    def on_btnPrintLabel_clicked(self):
        printer = QtGui.qApp.labelPrinter()
        if self.labelTemplate and printer:
            context = CInfoContext()
            date = self.eventDate if self.eventDate else QtCore.QDate.currentDate()
            takenTissueId = forceRef(self.takenTissueRecord.value('id')) if self.takenTissueRecord else None
            data = {'client'     : context.getInstance(CClientInfo, self.clientId, date),
                    'tissueType' : context.getInstance(CTissueTypeInfo, self.cmbTissueType.value()),
                    'externalId' : self.edtTissueExternalId.text(),
                    'takenTissue': context.getInstance(CTakenTissueJournalInfo, takenTissueId)
                   }
            QtGui.qApp.call(self, directPrintTemplate, (self.labelTemplate[1], data, printer))

    @QtCore.pyqtSlot(int)
    def on_btnPrint_printByTemplate(self, templateId):
        if self.beforePrintTemplate(templateId) == -1:
            return
        #if not self.isTabCashAlreadyLoad:
        #    self.initTabCash(False)
        data = getEventContextData(self)
        data['templateCounterValue'] = self.oldTemplates.get(templateId, '')
        applyTemplate(self, templateId, data)

    @QtCore.pyqtSlot(int)
    def on_cmbSetPerson_currentIndexChanged(self):
        self.personId = self.cmbSetPerson.value()


class CF001ExtendedDialog(CF001Dialog):
    u"""
        Расширенная форма 001. Добавлены результат обращения и ввод диагнозов.
    """

    def __init__(self, parent):
        super(CF001ExtendedDialog, self).__init__(parent)
        self.mapSpecialityIdToDiagFilter = {}
        # На форме указывается только один врач. Он является и назначившим, и ответственным. Делать виджеты с универсальным названием не хочу, т.к. на это название завзано много кода, а смысла нет. Поэтому пока просто меняем название.
        self.lblSetPerson.setText(u'Ответственный')
        self.connect(self.modelDiagnostics, QtCore.SIGNAL('resultChanged()'), self.on_modelDiagnostics_resultChanged)

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
        result = super(CF001ExtendedDialog, self)._prepare(contractId, clientId, eventTypeId, orgId, personId, eventSetDatetime, eventDatetime, includeRedDays, numDays, presetDiagnostics, presetActions, disabledActions, externalId, assistantId, curatorId, movingActionTypeId, valueProperties, relegateOrgId, diagnos, financeId, protocolQuoteId, actionByNewEvent, referrals, isAmb)
        if presetDiagnostics:
            for MKB, dispanserId, healthGroupId, medicalGroupId, visitTypeId, goalId, serviceId in presetDiagnostics:
                item = self.modelDiagnostics.getEmptyRecord()
                item.setValue('MKB', toVariant(MKB))
                item.setValue('dispanser_id',   toVariant(dispanserId))
                item.setValue('healthGroup_id', toVariant(healthGroupId))
                self.modelDiagnostics.items().append(item)
            if presetDiagnostics[0][5]:
                self.cmbGoal.setValue(presetDiagnostics[0][5])

        self.updateModelsRetiredList()

        return result

    def prepareEisWidgets(self):
        self.addModels('Diagnostics', CF025DiagnosticsModel(self))
        self.setModels(self.tblFinalDiagnostics, self.modelDiagnostics, self.selectionModelDiagnostics)
        self.cmbResult.setTable('rbResult')
        self.setupDiagnosticsMenu()
        self.markEditableTableWidget(self.tblFinalDiagnostics)
        self.tblFinalDiagnostics.setPopupMenu(self.mnuDiagnostics)

    def setupDiagnosticsMenu(self):
        self.mnuDiagnostics = QtGui.QMenu(self)
        self.mnuDiagnostics.setObjectName('mnuDiagnostics')
        self.actDiagnosticsRemove = QtGui.QAction(u'Удалить запись', self)
        self.actDiagnosticsRemove.setObjectName('actDiagnosticsRemove')
        self.mnuDiagnostics.addAction(self.actDiagnosticsRemove)

    def setRecord(self, record):
        super(CF001ExtendedDialog, self).setRecord(record)
        setRBComboBoxValue(self.cmbResult,      record, 'result_id')
        self.loadDiagnostics(self.itemId())

    def getRecord(self):
        record = super(CF001ExtendedDialog, self).getRecord()
        getRBComboBoxValue(self.cmbResult,      record, 'result_id')
        return record

    def setEditable(self, editable):
        super(CF001ExtendedDialog, self).setEditable(editable)
        self.modelDiagnostics.setEditable(editable or QtGui.qApp.userHasRight(urEditDiagnosticsInPayedEvents))

    def loadDiagnostics(self, eventId):
        # Нагло скопировано из F. 025
        db = QtGui.qApp.db
        table = db.table('Diagnostic')
        isDiagnosisManualSwitch = self.modelDiagnostics.manualSwitchDiagnosis()
        rawItems = db.getRecordList(table, '*', [table['deleted'].eq(0), table['event_id'].eq(eventId)], 'id')
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
            currentEventId = self.itemId()
            if eventId != currentEventId:
                newRecord.setValue('id', toVariant(None))
                newRecord.setValue('event_id', toVariant(currentEventId))
                newRecord.setValue('diagnosis_id', toVariant(None))
                newRecord.setValue('handleDiagnosis', QtCore.QVariant(0))
            else:
                if isDiagnosisManualSwitch:
                    isCheckedHandleDiagnosis = checkIsHandleDiagnosisIsChecked(setDate,
                                                                               self.clientId,
                                                                               diagnosisId)
                    newRecord.setValue('handleDiagnosis', QtCore.QVariant(isCheckedHandleDiagnosis))

            items.append(newRecord)
        self.modelDiagnostics.setItems(items)

    def saveInternals(self, eventId):
        super(CF001ExtendedDialog, self).saveInternals(eventId)
        self.saveDiagnostics(eventId)
        self.updateRecommendations()

    def updateDiagnosisTypes(self):
        items = self.modelDiagnostics.items()
        isFirst = True
        for item in items :
            diagnosisTypeId = self.getDiagnosisTypeId(isFirst)
            item.setValue('diagnosisType_id', toVariant(diagnosisTypeId))
            isFirst = False

    def getDiagnosisTypeId(self, dt):
        return forceRef(QtGui.qApp.db.translate('rbDiagnosisType', 'code', '2' if dt else '9', 'id'))

    def saveDiagnostics(self, eventId):
        items = self.modelDiagnostics.items()
        isDiagnosisManualSwitch = self.modelDiagnostics.manualSwitchDiagnosis()
        isFirst = True
        endDate = self.edtEndDate.date()
        endDateVariant = toVariant(endDate)
        begDate = self.edtBegDate.date()
        specialityIdVariant = QtGui.qApp.db.translate('Person', 'id', self.personId, 'speciality_id')
        MKBDiagnosisIdPairList = []
        prevId = 0
        for item in items:
            MKB           = forceString(item.value('MKB'))
            MKBEx         = forceString(item.value('MKBEx'))
            TNMS          = forceString(item.value('TNMS'))
            morphologyMKB = forceString(item.value('morphologyMKB'))
            #if self.diagnosisSetDateVisible == False:
            item.setValue('setDate', endDateVariant)
            date = forceDate(endDateVariant)
            #else:
            #    date = forceDate(item.value('setDate'))
            diagnosisTypeId = self.getDiagnosisTypeId(isFirst)
            item.setValue('diagnosisType_id', toVariant(diagnosisTypeId))
            item.setValue('speciality_id', specialityIdVariant)
            item.setValue('person_id', toVariant(self.personId) )
            item.setValue('endDate', endDateVariant )
            diagnosisId = forceRef(item.value('diagnosis_id'))
            characterId = forceRef(item.value('character_id'))
            if not QtGui.qApp.isPNDDiagnosisMode():
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
                        morphologyMKB=morphologyMKB,
                        newSetDate=begDate
                        )
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
        self.modelDiagnostics.saveItems(eventId)
        self.modifyDiagnosises(MKBDiagnosisIdPairList)

    def getFinalDiagnosisMKB(self):
        diagnostics = self.modelDiagnostics.items()
        if diagnostics:
            MKB   = forceString(diagnostics[0].value('MKB'))
            MKBEx = forceString(diagnostics[0].value('MKBEx'))
            return MKB, MKBEx
        else:
            return '', ''

    def getFinalDiagnosisId(self):
        diagnostics = self.modelDiagnostics.items()
        return forceRef(diagnostics[0].value('diagnosis_id')) if diagnostics else None

    def setEventTypeId(self, eventTypeId):
        super(CF001ExtendedDialog, self).setEventTypeId(eventTypeId)
        self.cmbResult.setTable('rbResult', True, 'eventPurpose_id=\'%d\'' % self.eventPurposeId)
        if self.cmbResult.value() is None:
            if self.inheritResult == True:
                self.cmbResult.setValue(self.defaultEventResultId.get(self.eventPurposeId))
        cols = self.modelDiagnostics.cols()
        resultCol = cols[len(cols)-1]
        resultCol.filter = 'eventPurpose_id=\'%d\'' % self.eventPurposeId
        self.diagnosisSetDateVisible = forceBool(getDiagnosisSetDateVisible(eventTypeId))
        if self.diagnosisSetDateVisible == False:
            self.tblFinalDiagnostics.setColumnHidden(2, True)

    def checkDataEntered(self):
        result = super(CF001ExtendedDialog, self).checkDataEntered()
        endDate = self.edtEndDate.date() if self._isClosedEventCheck else QtCore.QDate()
        # if endDate and not QtGui.qApp.userHasRight(urDoNotCheckResultAndMKB):
        #    result = result and (self.cmbResult.value() or self.checkInputMessage(u'результат', False, self.cmbResult))

        result = result and self.checkDiagnosticsDataEntered([(self.tblFinalDiagnostics, True, True, None)],
                                                             endDate)

        if \
                self.getFinalDiagnosisMKB()[0] is not None and self.getFinalDiagnosisMKB()[0] != u'' and self.getFinalDiagnosisMKB()[0][0] == u'C' \
                and not QtGui.qApp.userHasRight(urOncoDiagnosisWithoutTNMS)\
                and QtGui.qApp.isTNMSVisible() and (self.modelDiagnostics.items()[0].value('TNMS') is None or
                                forceString(self.modelDiagnostics.items()[0].value('TNMS')) == ''):
            result = result and self.checkValueMessage(check_data_text_TNM, False, None)

        result = result and (self.itemId() or self.primaryCheck(self.modelDiagnostics))
        return result

    def getEventInfo(self, context):
        result = super(CF001ExtendedDialog, self).getEventInfo(context)
        result._diagnosises = CDiagnosticInfoProxyList(context, [self.modelDiagnostics])
        return result

    @QtCore.pyqtSlot()
    def on_mnuDiagnostics_aboutToShow(self):
        canRemove = False
        currentRow = self.tblFinalDiagnostics.currentIndex().row()
        if currentRow>=0 :
            canRemove = self.modelDiagnostics.payStatus(currentRow) == 0
        self.actDiagnosticsRemove.setEnabled(canRemove)

    @QtCore.pyqtSlot()
    def on_modelDiagnostics_resultChanged(self):
        CEventEditDialog.defaultDiagnosticResultId[self.eventPurposeId] = self.modelDiagnostics.resultId()
        self.updateResultFilter()
        # if self.cmbResult.value() is None:
        #     self.cmbResult.setValue(getEventResultId(CEventEditDialog.defaultDiagnosticResultId.get(self.eventPurposeId)))

    @QtCore.pyqtSlot()
    def on_actDiagnosticsRemove_triggered(self):
        currentRow = self.tblFinalDiagnostics.currentIndex().row()
        self.modelDiagnostics.removeRowEx(currentRow)
        self.updateDiagnosisTypes()

    @QtCore.pyqtSlot(int)
    def on_cmbResult_currentIndexChanged(self):
        self.modelDiagnostics.setResult(getResultIdByDiagnosticResultId(self.cmbResult.value()))

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


class CColorCol(CCol):
    def __init__(self, title, fields, defaultWidth, model):
        CCol.__init__(self, title, fields, defaultWidth, 'r')
        self._model = model
        self._cache = CRecordCache()

    def getBackgroundColor(self, values):
        tissueTypeId = self._model.tissueTypeId()
        if tissueTypeId:
            actionTypeId = forceRef(values[0])
            key = (actionTypeId, tissueTypeId)
            color = self._cache.get(key)
            if color is None:
                db = QtGui.qApp.db
                cond = 'master_id=%d AND tissueType_id=%d' %(actionTypeId, tissueTypeId)
                rec = db.getRecordEx('ActionType_TissueType', 'containerType_id', cond)
                colorName = None
                if rec:
                    containerTypeId = forceRef(rec.value('containerType_id'))
                    if containerTypeId:
                        colorName = forceString(db.translate('rbContainerType', 'id', containerTypeId, 'color'))
                if colorName:
                    color = QtCore.QVariant(QtGui.QColor(colorName))
                else:
                    color = QtCore.QVariant()
                self._cache.put(key, color)
            return color
        return CCol.invalid

    def format(self, values):
        return CCol.invalid


class CPriceCol(CCol):
    def __init__(self, title, fields, defaultWidth, model):
        CCol.__init__(self, title, fields, defaultWidth, 'r')
        self._model = model
        self._cache = CRecordCache()

    def load(self, actTypeId):
        query = u'''
            SELECT DISTINCT ct.price FROM
            ActionType at
            INNER JOIN rbService s ON s.code = at.code
            INNER JOIN Contract_Tariff ct ON ct.service_id = s.id
            INNER JOIN Contract c ON ct.master_id = %s
            WHERE at.id = %s AND c.endDate > '%s'
        '''
        db = QtGui.qApp.db
        record = db.query(query % (
            forceString(self._model.contractId), forceString(actTypeId), forceString(QtCore.QDate.currentDate())
        ))
        if record.next():
            self.putIntoCache(actTypeId, forceString(record.value(0)) if record.value(0) else u'Не установлена')
        else:
            self.putIntoCache(actTypeId, '')

class CActionLeavesModel(CActionsModel):
    def __init__(self, parent):
        self._tissueTypeId = None
        cols = [CEnableCol(u'Включить',     ['id'],   20, parent),
                CColorCol(u'Цветовая маркировка', ['id'], 10, self),
                CTextCol(u'Код',            ['code'], 20),
                CTextCol(u'Наименование',   ['name'], 20),
                CPriceCol(u'Стоимость',     ['id'], 20, parent)]
        self.initModel(parent, cols)
        self._isEditable = True

    def setTissueTypeId(self, tissueTypeId):
        self._tissueTypeId = tissueTypeId
        self.emitDataChanged()

    def tissueTypeId(self):
        return self._tissueTypeId
