# -*- coding: utf-8 -*-

# Страница редактирования action одного класса в пределах event'а
from PyQt4 import QtCore, QtGui

from Events.Action import ActionStatus, CAction, CActionType, CActionTypeCache
from Events.ActionPropertiesTable import CExActionPropertiesTableModel, CExActionPropertiesTableView
from Events.ActionTemplateSaveDialog import CActionTemplateSaveDialog
from Events.ActionTypeDialog import CActionTypeDialogTableModel
from Events.ActionsForPeriod import CActionsForPeriodDialog
from Events.ActionsModel import CActionsModel, getActionDefaultAmountEx, getActionDefaultContractId
from Events.ActionsSelector import selectActionTypes
from Events.ActionsTable import CActionsTableView, CSupportServiceButtonBox
from Events.ExecutionPlanDialog import CGetExecutionPlan
from Events.PrevActionChooser import CPrevActionChooser
from Events.Utils import CActionTemplateCache, CFinanceType, getActionTypeMesIdList, getEventContextData, \
    getEventLengthDays, getEventShowTime, \
    getEventTypeForm, isEventAnyActionDatePermited, setActionPropertiesColumnVisible, setOrgStructureIdToCmbPerson
from Orgs.OrgComboBox import CContractDbModel
from Orgs.Orgs import selectOrganisation
from Orgs.Utils import getOrgStructureActionTypeIdList, getRealOrgStructureId, getTopParentIdForOrgStructure
from Resources.Utils import JobTicketStatus
from Ui_ActionsPage import Ui_ActionsPageWidget
from Users.Rights import urCopyPrevAction, urLoadActionTemplate, urSaveActionTemplate, urSkipEventCreationAfterMoving
from library.DateEdit import CDateEdit
from library.DialogBase import CConstructHelperMixin
from library.ICDMorphologyCodeEdit import CICDMorphologyCodeEditEx
from library.PrintTemplates import applyMultiTemplateList, applyTemplate, customizePrintButton
from library.TimeSeries import timeSeries
from library.Utils import addPeriod, copyFields, forceBool, forceDate, forceDateTime, forceDouble, forceInt, forceRef, \
    forceString, forceStringEx, \
    getActionTypeIdListByFlatCode, getPref, setPref, setValues, toVariant
from library.interchange import setDatetimeEditValue


class CFastActionsPage(QtGui.QWidget, CConstructHelperMixin, Ui_ActionsPageWidget):
    JOB_STATUS_MAP = {
        ActionStatus.Started: JobTicketStatus.Awaiting,  # 0: 0
        ActionStatus.Awaiting: JobTicketStatus.Awaiting,  # 1: 0
        ActionStatus.Cancelled: JobTicketStatus.Awaiting,  # 3: 0
        ActionStatus.WithoutResult: JobTicketStatus.InProgress,  # 4: 1
        ActionStatus.Appointed: JobTicketStatus.InProgress,  # 5: 1
        ActionStatus.Done: JobTicketStatus.Done,  # 2: 2
        ActionStatus.NotProvided: JobTicketStatus.Done  # 6: 2
    }

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.eventEditor = None
        self._isEditable = True
        self.extraAssistantsVisible = True

        self.isUiMiniSetted = False
        self.isPreUiMiniSetted = False
        self.isPreUiSetted = False
        self.isPostUiMiniSetted = False
        self.isPostUiSetted = False

        self.mesIdListByActionTypeCach = {}
        if hasattr(self, 'cmbAPPerson'):
            setOrgStructureIdToCmbPerson(self.cmbAPPerson)
        if hasattr(self, 'cmbAPSetPerson'):
            setOrgStructureIdToCmbPerson(self.cmbAPSetPerson)

    def setupUiMini(self, Dialog):
        self.tblAPActions = CActionsTableView(Dialog)
        self.tblAPProps = CExActionPropertiesTableView(Dialog)
        self.tblAPProps.setEnabled(False)
        self.edtAPDirectionDate = CDateEdit(Dialog)
        self.edtAPBegDate = CDateEdit(Dialog)
        self.edtAPEndDate = CDateEdit(Dialog)
        self.cmbAPMorphologyMKB = CICDMorphologyCodeEditEx(Dialog)
        self.isUiMiniSetted = True

    def setEditable(self, editable):
        self._isEditable = editable
        self._updateEditable()

    def _updateEditable(self):
        if hasattr(self, 'modelAPActions') and hasattr(self, 'modelAPActionProperties'):
            self.modelAPActions.setEditable(self._isEditable)
            self.modelAPActionProperties.setReadOnly(not self._isEditable)
        if hasattr(self, 'attrsAP'):
            self.attrsAP.setEnabled(self._isEditable)

    def clearBeforeSetupUi(self):
        self.tblAPActions.setModel(None)
        self.tblAPProps.setModel(None)
        self.tblAPActions.deleteLater()
        self.tblAPActions = None
        self.tblAPProps.deleteLater()
        self.tblAPProps = None
        self.edtAPDirectionDate.deleteLater()
        self.edtAPDirectionDate = None
        self.edtAPBegDate.deleteLater()
        self.edtAPBegDate = None
        self.edtAPEndDate.deleteLater()
        self.edtAPEndDate = None
        self.cmbAPMorphologyMKB.deleteLater()
        self.cmbAPMorphologyMKB = None

        del self.tblAPActions
        del self.tblAPProps
        del self.edtAPDirectionDate
        del self.edtAPBegDate
        del self.edtAPEndDate
        del self.cmbAPMorphologyMKB

        self.isPostUiSetted = False

    def preSetupUiMini(self):
        self.addModels('APActions', CActionsModel(self))
        if QtGui.qApp.isHideActionsFromOtherTopOrgStructures():
            topOrgStructureId = getTopParentIdForOrgStructure(QtGui.qApp.userOrgStructureId)
            if topOrgStructureId:
                actionTypeIdList = getOrgStructureActionTypeIdList(topOrgStructureId, True)
                actionTypeIdList = QtGui.qApp.db.getTheseAndParents('ActionType', 'group_id', actionTypeIdList)
                self.modelAPActions.enableActionTypeList(actionTypeIdList)
        self.addModels('APActionProperties', CExActionPropertiesTableModel(self))
        self._updateEditable()
        self.commonTakenTissueJournalRecordId = None
        self._visibleMorphologyMKB = QtGui.qApp.defaultMorphologyMKBIsVisible()
        self._canUseLaboratoryCalculator = False
        self.receivedFinanceId = None
        self.eventActionFinance = None
        self.defaultFinanceId = None
        self.defaultContractFilterPart = None
        self.allowedActionTypesByTissue = []
        self.notFilteredActionTypesClasses = []
        self.defaultDirectionDate = CActionType.dddUndefined
        self.actionTemplateCache = CActionTemplateCache(self.eventEditor)
        self.isPreUiMiniSetted = True

    def preSetupUi(self):
        actionsDesc = [
            ('actAPActionAddSuchAs', u'Добавить такой же'),
            ('actAPActionAddSameForPeriod', u'Добавить такие же на период...'),
            ('actAPActionDup', u'Дублировать'),
            # ('actAPActionAdd', u'Добавить'),
            ('actAPActionsAddToRecs', u'Добавить в направления'),
            ('actAPActionsAdd', u'Добавить ...'),

            ('actAPLoadAnyonesPrevAction', u'Врача любой специальности'),
            ('actAPLoadSameSpecialityPrevAction', u'Той же самой специальности'),
            ('actAPLoadOwnPrevAction', u'Только свои')
        ]
        for actionName, text in actionsDesc:
            setattr(self, actionName, QtGui.QAction(text, self))
            getattr(self, actionName).setObjectName(actionName)

        self.mnuAPLoadPrevAction = QtGui.QMenu(self)

        self.mnuAPLoadPrevAction.setObjectName('mnuAPLoadPrevAction')
        self.mnuAPLoadPrevAction.addAction(self.actAPLoadAnyonesPrevAction)
        self.mnuAPLoadPrevAction.addAction(self.actAPLoadSameSpecialityPrevAction)
        self.mnuAPLoadPrevAction.addAction(self.actAPLoadOwnPrevAction)

        self.actAPActionsAdd.setShortcut(QtCore.Qt.Key_F9)
        self.addAction(self.actAPActionsAdd)
        self.isPreUiSetted = True
        self.gBoxSupportService = CSupportServiceButtonBox(self)

    def postSetupUiMini(self):
        self.tblAPActions.setParentWidget(self)
        self.setFocusProxy(self.tblAPActions)
        self.setupModels()
        self._updateEditable()
        self.isPostUiMiniSetted = True

    def postSetupUi(self):
        # Заполнение элементов комбобокса переведенными значениями из первоисточника
        self.cmbAPStatus.clear()
        self.setupModels()
        self.cmbAPStatus.addItems(CActionType.retranslateClass(False).statusNames)
        self.tblAPActions.setParentWidget(self)
        self.setFocusProxy(self.tblAPActions)
        self.connect(self.tblAPActions, QtCore.SIGNAL('printActionTemplateList'),
                     self.on_tblAPActions_printByTemplateList)
        self.cmbHMPKind.setTable('rbHighTechCureKind', addNone=False)
        self.cmbHMPMethod.setTable('rbHighTechCureMethod', addNone=False)
        self.connect(self.cmbHMPKind, QtCore.SIGNAL('currentIndexChanged(int)'), self.on_cmbHMPKind_currentIndexChanged)
        self.edtAPDirectionDate.canBeEmpty(True)
        self.edtAPBegDate.canBeEmpty(True)
        self.edtAPEndDate.canBeEmpty(True)
        self.setupActionPopupMenu()
        self.btnAPLoadPrevAction.setMenu(self.mnuAPLoadPrevAction)
        self.btnAPLoadTemplate.setModelCallback(self.getTemplatesModel)
        if self.eventEditor and not getEventTypeForm(self.eventEditor.getEventTypeId()) in (u'000', u'003'):
            self.cmbAPAssistant2.setVisible(False)
            self.cmbAPAssistant3.setVisible(False)
            self.lblAPAssistant2.setVisible(False)
            self.lblAPAssistant3.setVisible(False)
            self.extraAssistantsVisible = False
            self.cmbActionMes._popup.setCheckBoxes('actionPage' + forceString(self.eventEditor.getEventTypeId()))
        action = QtGui.QAction(self)
        self.actSetLaboratoryCalculatorInfo = action
        self.actSetLaboratoryCalculatorInfo.setObjectName('actSetLaboratoryCalculatorInfo')
        action.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F3))
        self.addAction(action)
        self.connect(self.actSetLaboratoryCalculatorInfo, QtCore.SIGNAL('triggered()'),
                     self.on_actSetLaboratoryCalculatorInfo)

        self._canUseLaboratoryCalculatorPropertyTypeList = None
        self._mainWindowState = QtGui.qApp.mainWindow.windowState()

        self.connect(self.modelAPActionProperties,
                     QtCore.SIGNAL('actionNameChanged()'), self.updateCurrentActionName)
        # self.connect(self.modelAPActionProperties,
        #              QtCore.SIGNAL('setCurrentActionEndDate(QDate)'), self.setCurrentActionEndDate)
        self.isPostUiSetted = True

        self.supportServiceBtnsDesc = {
            'reanimation': {'name': 'btnReanimation', 'text': u'Реанимация', 'object': None},
            'maternityward': {'name': 'btnMaternityWard', 'text': u'Родовое', 'object': None}
        }
        for btn in self.supportServiceBtnsDesc.values():
            btn['object'] = self.__getattribute__(btn['name'])
            self.connect(btn['object'], QtCore.SIGNAL('clicked()'), self.__getattribute__('on%s_clicked' % btn['name']))
        for code, btn in self.supportServiceBtnsDesc.items():
            self.gBoxSupportService.addBtn(btn['object'], code, btn['text'])
        self.gBoxSupportService.setVisible(False)
        self.onActionCurrentChanged()
        self._updateEditable()

        self.btnToggleAttrsAP.toggled.connect(lambda state: self.btnToggleAttrsAP.setText(u'v' if state else u'^'))

    def hideEvent(self, evt):
        if self.isPostUiSetted:
            setPref(QtGui.qApp.preferences.windowPrefs, 'cactionspage.' + self.objectName(), self.savePreferences())

    def showEvent(self, evt=None):
        if self.isPostUiSetted:
            self.loadPreferences(getPref(QtGui.qApp.preferences.windowPrefs, 'cactionspage.' + self.objectName(), {}))

    def savePreferences(self):
        return {
            'splitter': self.splitterAP.saveState(),
            # 'tbl': self.tblAPActions.horizontalHeader().saveState(),
        }

    def loadPreferences(self, pref):
        splitter_state = getPref(pref, 'splitter', None)
        if splitter_state:
            if isinstance(splitter_state, QtCore.QVariant):
                splitter_state = splitter_state.toByteArray()
            self.splitterAP.restoreState(splitter_state)
        attrs_state = getPref(QtGui.qApp.preferences.windowPrefs, '{0}_attrs_collapsed'.format(self.objectName()),
                              False)
        if isinstance(attrs_state, QtCore.QVariant):
            attrs_state = attrs_state.toBool()
        self.btnToggleAttrsAP.setChecked(attrs_state)

    def setupModels(self):
        self.setModels(self.tblAPActions, self.modelAPActions, self.selectionModelAPActions)
        self.setModelsEx(self.tblAPProps, self.modelAPActionProperties, self.selectionModelAPActionProperties)

    def updateCurrentActionName(self):
        index = self.tblAPActions.currentIndex()
        self.tblAPActions.dataChanged(index, index)

    def setActionTypeClass(self, actionTypeClass):
        self.modelAPActions.setActionTypeClass(actionTypeClass)

    def setNotFilteredActionTypesClasses(self, classes):
        self.notFilteredActionTypesClasses = classes if isinstance(classes, list) else [classes]

    def setEventEditor(self, eventEditor):
        self.eventEditor = eventEditor
        self.modelAPActions.eventEditor = eventEditor
        self.actionTemplateCache.eventEditor = eventEditor
        self.connect(eventEditor, QtCore.SIGNAL('updateActionsAmount()'), self.modelAPActions.updateActionsAmount)
        self.connect(eventEditor, QtCore.SIGNAL('eventEditorSetDirty(bool)'), self.setIsDirty)

    def getActionLength(self, record, countRedDays):
        if record:
            startDate = forceDate(record.value('begDate'))
            stopDate = forceDate(record.value('endDate'))
            if startDate and stopDate:
                return getEventLengthDays(startDate, stopDate, countRedDays, self.eventEditor.eventTypeId)
        return 0

    def setupActionPopupMenu(self):
        tbl = self.tblAPActions
        tbl.createPopupMenu([self.actAPActionAddSuchAs,
                             self.actAPActionAddSameForPeriod,
                             self.actAPActionDup,
                             '-',
                             # self.actAPActionAdd,
                             self.actAPActionsAddToRecs,
                             self.actAPActionsAdd])
        tbl.popupMenu().addSeparator()
        tbl.addMoveRow()
        tbl.popupMenu().addSeparator()
        tbl.addPopupDelRow()
        tbl.popupMenu().addSeparator()
        tbl.addOpenInRedactor()
        tbl.addPrintSelected()
        tbl.addCopyFromPrevious()
        tbl.setDelRowsChecker(lambda rows: any(map(self.modelAPActions.isDeletable, rows)))

    def setOrgId(self, orgId):
        self.cmbAPSetPerson.setOrgId(orgId)
        self.cmbAPPerson.setOrgId(orgId)
        self.cmbAPAssistant.setOrgId(orgId)
        if self.extraAssistantsVisible:
            self.cmbAPAssistant2.setOrgId(orgId)
            self.cmbAPAssistant3.setOrgId(orgId)

    def setEndDate(self, date):
        self.cmbAPSetPerson.setEndDate(date)
        self.cmbAPPerson.setEndDate(date)
        self.cmbAPAssistant.setEndDate(date)
        if self.extraAssistantsVisible:
            self.cmbAPAssistant2.setEndDate(date)
            self.cmbAPAssistant3.setEndDate(date)

    def setCommonTakenTissueJournalRecordIdToActions(self):
        for record, action in self.modelAPActions.items():
            actionTypeId = forceRef(record.value('actionType_id'))
            if actionTypeId in self.allowedActionTypesByTissue:
                record.setValue('takenTissueJournal_id', toVariant(self.commonTakenTissueJournalRecordId))

    def updatePersonId(self, oldPersonId, newPersonId):
        self.modelAPActions.updatePersonId(oldPersonId, newPersonId)
        #        self.cmbAPPerson.setValue(newPersonId)
        #        self.cmbAPSetPerson.setValue(newPersonId)
        self.presetPerson = newPersonId
        if hasattr(self, 'cmbAPPerson'):
            self.onActionCurrentChanged()

    def loadActions(self, eventId):
        self.modelAPActions.loadItems(eventId)
        self.updateActionEditor()

    def loadActionsLite(self, eventId):
        # mdldml: пытаемся сохранить страницу в том же состоянии, в котором она
        # была до загрузки, если это имеет смысл (предполагаем, что если
        # действие в той же строке имеет тот же тип, что и до загрузки, то
        # его можно оставить выделенным). Это необходимо, например, для того,
        # чтобы при нажатии кнопки "Применить" в обращении не сбрасывалось
        # выделение текущего элемента.

        model = self.modelAPActions
        index = self.tblAPActions.currentIndex()
        row = index.row()
        rowIsValid = 0 <= row < len(model.items())
        action = model.items()[row][1] if rowIsValid else None

        model.loadItems(eventId)
        rowIsValid = 0 <= row < len(model.items())
        if rowIsValid:
            newAction = model.items()[row][1]
            if newAction.getType().id == action.getType().id:
                self.tblAPActions.setCurrentIndex(index)

    def setCommonTakenTissueJournalRecordId(self, id=None, actionTypeIdList=None):
        if not actionTypeIdList:
            actionTypeIdList = []
        self.commonTakenTissueJournalRecordId = id
        self.allowedActionTypesByTissue = actionTypeIdList

    def syncDataWithJobTicket(self):
        actionIdList = [action.getId() for record, action in self.modelAPActions.items()]
        if not actionIdList:
            return

        db = QtGui.qApp.db
        tableAction = db.table('Action')
        tableAP = db.table('ActionProperty')
        tableAPJT = db.table('ActionProperty_Job_Ticket')
        tableJobTicket = db.table('Job_Ticket')

        table = tableAction.innerJoin(tableAP, [tableAP['action_id'].eq(tableAction['id']),
                                                tableAP['deleted'].eq(0)])
        table = table.innerJoin(tableAPJT, tableAPJT['id'].eq(tableAP['id']))
        table = table.innerJoin(tableJobTicket, tableJobTicket['id'].eq(tableAPJT['value']))
        cols = [
            tableJobTicket['id'].alias('jobTicketId'),
            tableAction['status'].alias('status'),
            tableAction['begDate'].alias('begDate'),
            tableAction['endDate'].alias('endDate')
        ]
        cond = [
            tableAction['id'].inlist(actionIdList)
        ]

        jobTicketValues = [(forceRef(rec.value('jobTicketId')),
                            self.JOB_STATUS_MAP.get(forceInt(rec.value('status')), 0),
                            forceDateTime(rec.value('begDate')),
                            forceDateTime(rec.value('endDate'))) for rec in db.iterRecordList(table, cols, cond)]
        updateFields = ['status', 'begDateTime', 'endDateTime']
        db.insertValues(tableJobTicket, ['id'] + updateFields, jobTicketValues, updateFields=updateFields)

    def createTakenTissueJournal(self):
        actionIdList = [str(action.getId()) for record, action in self.modelAPActions.items()]
        if not actionIdList:
            return

        db = QtGui.qApp.db
        tableAction = db.table('Action')
        tableATTT = db.table('ActionType_TissueType')

        table = tableAction.innerJoin(tableATTT, tableATTT['master_id'].eq(tableAction['actionType_id']))
        cols = [
            tableAction['id'],
            tableAction['status'],
            tableATTT['tissueType_id']
        ]
        cond = [
            tableAction['id'].inlist(actionIdList),
            tableAction['takenTissueJournal_id'].isNull()
        ]
        group = [
            tableAction['id']
        ]

        for rec in db.iterRecordList(table, cols, cond, group=group):
            if self.JOB_STATUS_MAP.get(forceInt(rec.value('status')), 0) == JobTicketStatus.InProgress:
                ttjId = db.insertFromDict('TakenTissueJournal', {
                    'client_id': self.eventEditor.clientId,
                    'tissueType_id': forceRef(rec.value('tissueType_id')),
                    'datetimeTaken': QtCore.QDateTime.currentDateTime()
                })
                db.updateRecords(tableAction,
                                 tableAction['takenTissueJournal_id'].eq(ttjId),
                                 tableAction['id'].eq(forceRef(rec.value('id'))))

    def saveActions(self, eventId):
        if self.commonTakenTissueJournalRecordId:
            self.setCommonTakenTissueJournalRecordIdToActions()
        self.modelAPActions.saveItems(eventId)
        self.syncDataWithJobTicket()
        self.createTakenTissueJournal()

    def updateActionEditor(self):
        model = self.tblAPActions.model()
        if QtGui.qApp.isCheckMKB():
            self.cmbAPMKB.setMKBFilter(
                {'begDate': self.eventEditor.edtBegDate.date(), 'clientId': self.eventEditor.clientId})
        if model.rowCount() > 0:
            self.tblAPActions.setCurrentIndex(model.index(0, 0))
        else:
            for widget in [self.edtAPDirectionDate, self.edtAPDirectionTime,
                           # self.edtAPPlannedEndDate, self.edtAPPlannedEndTime,
                           self.cmbAPSetPerson,
                           self.cmbAPStatus, self.edtAPBegDate, self.edtAPBegTime,
                           self.edtAPEndDate, self.edtAPEndTime,
                           self.cmbAPPerson, self.edtAPOffice,
                           self.cmbAPAssistant,
                           self.cmbAPAssistant2,
                           self.cmbAPAssistant3,
                           self.edtAPAmount, self.edtAPUet,
                           self.edtAPNote,
                           self.tblAPProps,
                           self.btnAPPrint, self.btnAPLoadTemplate, self.btnAPSaveAsTemplate, self.btnAPLoadPrevAction]:
                widget.setEnabled(False)

    def setIsDirty(self, dirty):
        self.resetPrintButton()
        self.tblAPActions.setIsDirty(dirty)

    def resetPrintButton(self):
        if hasattr(self, 'btnAPPrint'):
            row = self.tblAPActions.currentIndex().row()
            actionType = None
            items = self.tblAPActions.model().items()
            if 0 <= row < len(items):
                record, action = items[row]
                actionTypeId = forceRef(record.value('actionType_id'))
                actionType = CActionTypeCache.getById(actionTypeId) if actionTypeId else None
            self.updatePrintButton(actionType)

    def updatePrintButton(self, actionType):
        context = actionType.context if actionType else ''
        customizePrintButton(self.btnAPPrint, context, self.eventEditor.isDirty() or not self.eventEditor.itemId())

    def onActionCurrentChanged(self):
        if not self.isPostUiSetted:
            return
        model = self.tblAPActions.model()
        items = model.items()
        row = self.tblAPActions.currentIndex().row()
        editWidgets = [self.edtAPDirectionDate, self.edtAPDirectionTime,
                       # self.edtAPPlannedEndDate, self.edtAPPlannedEndTime,
                       self.cmbAPSetPerson, self.chkAPIsUrgent,
                       self.cmbAPStatus, self.edtAPBegDate, self.edtAPBegTime,
                       self.edtAPEndDate, self.edtAPEndTime, self.cmbAPOrg,
                       self.cmbAPPerson, self.edtAPOffice,
                       self.cmbAPAssistant,
                       self.cmbAPAssistant2,
                       self.cmbAPAssistant3,
                       self.edtAPAmount, self.edtAPUet,
                       self.edtAPNote,
                       self.btnAPLoadTemplate, self.btnAPLoadPrevAction, self.btnAPSelectOrg,
                       self.cmbActionMes, self.cmbHMPKind, self.cmbHMPMethod]
        otherWidgets = [self.tblAPProps, self.btnAPPrint, self.btnAPSaveAsTemplate]
        mkbWidgets = [self.cmbAPMKB, self.cmbAPMorphologyMKB]
        if 0 <= row < len(items):
            record, action = items[row]
        else:
            record = action = None
        if record:
            actionTypeId = forceRef(record.value('actionType_id'))
            actionType = CActionTypeCache.getById(actionTypeId) if actionTypeId else None
            personId = forceRef(record.value('person_id'))
            financeId = forceRef(record.value('finance_id'))
            contractId = forceRef(record.value('contract_id'))
        else:
            actionType = actionTypeId = None
            self.defaultDirectionDate = CActionType.dddUndefined
        if actionType:
            setActionPropertiesColumnVisible(actionType, self.tblAPProps)
            self.defaultDirectionDate = actionType.defaultDirectionDate
            visibleMKB = True
            if actionType.defaultMKB == CActionType.dmkbNotUsed:
                enableMKB = False
                visibleMKB = False
            elif actionType.defaultMKB in (CActionType.dmkbSyncFinalDiag,
                                           CActionType.dmkbSyncSetPersonDiag):
                enableMKB = not forceString(record.value('MKB'))
            else:
                enableMKB = True

            visibleMorphology = True
            if actionType.defaultMorphology == CActionType.dmorphologyNotUsed:
                enableMorphology = False
                visibleMorphology = False
            elif actionType.defaultMorphology in (CActionType.dmorphologySyncFinalDiag,
                                                  CActionType.dmorphologySyncSetPersonDiag):
                enableMorphology = not forceString(record.value('morphologyMKB'))
            else:
                enableMorphology = True

            visibleMES = True
            if not actionType.defaultMES:
                visibleMES = False

            canEdit = self._isEditable and (not action.isLocked() if action else True)
            for widget in editWidgets:
                widget.setEnabled(canEdit)

            for widget in (self.lblAPMKB, self.cmbAPMKB, self.lblAPMKBText):
                widget.setVisible(visibleMKB)
                widget.setEnabled(canEdit and enableMKB)

            self.lblAPMorphologyMKB.setVisible(self._visibleMorphologyMKB and visibleMorphology)
            self.cmbAPMorphologyMKB.setVisible(self._visibleMorphologyMKB and visibleMorphology)
            self.cmbAPMorphologyMKB.setEnabled(canEdit and enableMorphology)

            self.cmbActionMes.setVisible(visibleMES)
            self.lblActionMes.setVisible(visibleMES)

            self.cmbHMPKind.setVisible(visibleMES)
            self.lblHMPKind.setVisible(visibleMES)
            self.cmbHMPMethod.setVisible(visibleMES)
            self.lblHMPMethod.setVisible(visibleMES)

            for widget in otherWidgets:
                widget.setEnabled(True)
            try:
                for widget in editWidgets + mkbWidgets:
                    widget.blockSignals(True)

                if (u'moving' in actionType.flatCode.lower()
                    or u'received' in actionType.flatCode.lower()
                    or u'reanimation' in actionType.flatCode.lower()
                    or u'maternityward' in actionType.flatCode.lower()
                    ):
                    self.onCurrentActionAdd(actionType.flatCode, action)
                else:
                    self.btnNextAction.setText(u'Действие')
                    self.btnNextAction.setVisible(False)
                    self.btnPlanNextAction.setVisible(False)
                showTime = actionType.showTime if actionType else False
                self.cmbAPPerson.setAcceptableSpecialities(self.getAcceptableSpecialities(actionTypeId))
                self.edtAPDirectionTime.setVisible(showTime)
                # self.edtAPPlannedEndTime.setVisible(showTime)
                self.edtAPBegTime.setVisible(showTime)
                self.edtAPEndTime.setVisible(showTime)
                showAPOrg = actionType.showAPOrg if actionType else False
                self.lblAPOrg.setVisible(showAPOrg)
                self.grpAPOrg.setVisible(showAPOrg)
                showAPNotes = actionType.showAPNotes if actionType else False
                self.lblAPNote.setVisible(showAPNotes)
                self.edtAPNote.setVisible(showAPNotes)
                showAssistant = actionType.hasAssistant if actionType else False
                self.lblAPAssistant.setVisible(showAssistant)
                self.cmbAPAssistant.setVisible(showAssistant)
                self.lblAPAssistant2.setVisible(showAssistant and self.extraAssistantsVisible)
                self.cmbAPAssistant2.setVisible(showAssistant and self.extraAssistantsVisible)
                self.lblAPAssistant3.setVisible(showAssistant and self.extraAssistantsVisible)
                self.cmbAPAssistant3.setVisible(showAssistant and self.extraAssistantsVisible)
                setDatetimeEditValue(self.edtAPDirectionDate, self.edtAPDirectionTime, record, 'directionDate')
                # setDatetimeEditValue(self.edtAPPlannedEndDate,   self.edtAPPlannedEndTime,   record, 'plannedEndDate')
                self.chkAPIsUrgent.setChecked(forceBool(record.value('isUrgent')))
                setDatetimeEditValue(self.edtAPBegDate, self.edtAPBegTime, record, 'begDate')
                setDatetimeEditValue(self.edtAPEndDate, self.edtAPEndTime, record, 'endDate')
                if hasattr(self,
                           'edtAPEndTime') and u'moving' in actionType.flatCode and self.edtAPEndDate.date() == QtCore.QDate():
                    self.edtAPEndTime.setTime(QtCore.QTime(12, 00))
                self.edtAPDirectionTime.setEnabled(canEdit and bool(self.edtAPDirectionDate.date()))
                canEditPlannedEndDate = canEdit and actionType.defaultPlannedEndDate not in [
                    CActionType.dpedBegDatePlusAmount,
                    CActionType.dpedBegDatePlusDuration]
                # self.edtAPPlannedEndDate.setEnabled(canEditPlannedEndDate)
                # self.edtAPPlannedEndTime.setEnabled(canEditPlannedEndDate and bool(self.edtAPPlannedEndDate.date()))
                setPerson = forceRef(record.value('setPerson_id'))
                self.cmbAPSetPerson.setValue(setPerson if setPerson else self.presetPerson if (
                u'moving' in actionType.flatCode.lower() and self.eventEditor.prevEventId) else None)
                self.edtAPBegTime.setEnabled(canEdit and bool(self.edtAPBegDate.date()))
                self.edtAPEndTime.setEnabled(canEdit and bool(self.edtAPEndDate.date()))

                # FIXME: pirozhok: куда делся статус?? Вернуть стутас в record, а после и эти строки
                # status = forceRef(QtGui.qApp.db.translate(QtGui.qApp.db.table('Action'), 'id', forceInt(record.value('id')), 'status'))
                # record.setValue('status', status)
                # FIXME: end

                if not forceDate(record.value('endDate')).isNull() and not (
                    forceInt(record.value('status')) in CActionType.retranslateClass(False).ignoreStatus) and forceRef(
                        record.value('status')) is not None:
                    self.cmbAPStatus.setCurrentIndex(2)
                else:
                    self.cmbAPStatus.setCurrentIndex(forceInt(record.value('status')))

                self.substituteEndDateTimeToEvent(forceRef(record.value('actionType_id')),
                                                  forceDateTime(record.value('endDate')))

                self.cmbAPPerson.setValue(personId if personId else self.presetPerson if (
                u'moving' in actionType.flatCode.lower() and self.eventEditor.prevEventId) else None)
                self.edtAPOffice.setText(forceString(record.value('office')))
                self.cmbAPAssistant.setValue(action.getAssistantId('assistant'))
                if self.extraAssistantsVisible:
                    self.cmbAPAssistant2.setValue(forceRef(record.value('assistant2_id')))
                    self.cmbAPAssistant3.setValue(forceRef(record.value('assistant3_id')))
                amount = forceDouble(record.value('amount'))
                self.edtAPAmount.setValue(amount)
                self.edtAPAmount.setEnabled(canEdit and bool(actionType) and actionType.amountEvaluation == 0)
                self.edtAPUet.setValue(amount * self.eventEditor.getUet(actionTypeId, personId, financeId, contractId))
                self.edtAPUet.setEnabled(False)
                self.edtAPNote.setText(forceString(record.value('note')))
                MKB = forceString(record.value('MKB'))
                self.oldMKB = MKB
                self.cmbAPMKB.setText(MKB)

                self.cmbActionMes.setSpeciality(self.eventEditor.personSpecialityId)
                self.cmbActionMes.setContract(self.eventEditor.getContractId())
                if not self.edtAPEndDate.date().isNull():
                    self.cmbActionMes.setEndDateForTariff(self.edtAPEndDate.date())
                elif not self.edtAPBegDate.date().isNull():
                    self.cmbActionMes.setEndDateForTariff(self.edtAPBegDate.date())

                self.cmbActionMes.setClientSex(self.eventEditor.clientSex)
                self.cmbActionMes.setClientAge(self.eventEditor.clientAge)
                self.cmbActionMes.setMKB(forceString(record.value('MKB')))
                actionMesId = forceRef(record.value('MES_id'))
                eventSetDate = self.eventEditor.eventSetDateTime.date() if self.eventEditor.eventSetDateTime else None
                self.cmbActionMes.setAvailableIdList(self.mesIdListByActionTypeCach.setdefault(actionTypeId,
                                                                                               getActionTypeMesIdList(
                                                                                                   actionTypeId,
                                                                                                   financeId,
                                                                                                   date=eventSetDate)))
                self.cmbActionMes.searchStringChanged(self.cmbActionMes.getText(actionMesId))
                self.cmbActionMes.setValue(actionMesId)

                self.cmbHMPKind.setValue(forceRef(record.value('hmpKind_id')))
                self.on_cmbHMPKind_currentIndexChanged()
                self.cmbHMPMethod.setValue(forceRef(record.value('hmpMethod_id')))
                self.cmbAPMorphologyMKB.setText(forceString(record.value('morphologyMKB')))
                self.cmbAPOrg.setValue(forceRef(record.value('org_id')))
                self.on_cmbAPMKB_textChanged(MKB)
                self.tblAPProps.setEnabled(bool(action))
                self.updatePropTable(action)
                self.updatePrintButton(actionType)
                if QtGui.qApp.userHasRight(urLoadActionTemplate) and action and canEdit:
                    self.btnAPLoadTemplate.setEnabled(True)
                else:
                    self.btnAPLoadTemplate.setEnabled(False)
                self.btnAPSaveAsTemplate.setEnabled(QtGui.qApp.userHasRight(urSaveActionTemplate))
                self.btnAPLoadPrevAction.setEnabled(
                    canEdit and QtGui.qApp.userHasRight(urCopyPrevAction) and bool(action))
                self._canUseLaboratoryCalculator = False
                QtGui.qApp.disconnectClipboard()
            finally:
                for widget in editWidgets + mkbWidgets:
                    widget.blockSignals(False)
        else:
            self.defaultDirectionDate = CActionType.dddUndefined
            for widget in editWidgets + mkbWidgets:
                widget.setEnabled(False)
            for widget in otherWidgets:
                widget.setEnabled(False)
            self.edtAPDirectionTime.setVisible(False)
            # self.edtAPPlannedEndTime.setVisible(False)
            self.edtAPBegTime.setVisible(False)
            self.edtAPEndTime.setVisible(False)
            self.btnNextAction.setText(u'Действие')
            self.btnNextAction.setVisible(False)
            self.btnPlanNextAction.setVisible(False)

    def getTemplatesModel(self):
        if not self.isPostUiSetted:
            return
        model = self.tblAPActions.model()
        items = model.items()
        row = self.tblAPActions.currentIndex().row()
        if 0 <= row < len(items):
            record, action = items[row]
        else:
            return None
        personId = forceRef(action.getRecord().value('person_id'))
        return self.actionTemplateCache.getModel(action.getType().id,
                                                 personId if personId
                                                 else forceRef(action.getRecord().value('setPerson_id')))

    @staticmethod
    def getAcceptableSpecialities(actionTypeId):
        db = QtGui.qApp.db
        tableATS = db.table('ActionType_Speciality')
        return [forceRef(rec.value('speciality_id'))
                for rec in db.iterRecordList(tableATS, 'speciality_id', tableATS['master_id'].eq(actionTypeId))]

    def getDefaultAmountEx(self, actionType, record, action):
        return getActionDefaultAmountEx(self, actionType, record, action)

    def getDefaultContractId(self, actionTypeId, financeId, begDate, endDate, contractId):
        return getActionDefaultContractId(self, actionTypeId, financeId, begDate, endDate, contractId)

    def on_actSetLaboratoryCalculatorInfo(self):
        result = self.eventEditor.checkNeedLaboratoryCalculator(self.modelAPActionProperties.propertyTypeList,
                                                                self.on_laboratoryCalculatorClipboard)
        self._canUseLaboratoryCalculatorPropertyTypeList = result
        self.setInfoToLaboratoryCalculatorClipboard()

    def setInfoToLaboratoryCalculatorClipboard(self):
        if self._canUseLaboratoryCalculatorPropertyTypeList:
            propertyTypeList = self._canUseLaboratoryCalculatorPropertyTypeList
            actual = unicode('; '.join(
                ['(' + ','.join([forceString(propType.id), propType.laboratoryCalculator, propType.name]) + ')' for
                 propType in propertyTypeList]))
            mimeData = QtCore.QMimeData()
            mimeData.setData(QtGui.qApp.inputCalculatorMimeDataType,
                             QtCore.QString(actual).toUtf8())
            QtGui.qApp.clipboard().setMimeData(mimeData)
            self._mainWindowState = QtGui.qApp.mainWindow.windowState()
            QtGui.qApp.mainWindow.showMinimized()

    def on_laboratoryCalculatorClipboard(self):
        QtGui.qApp.setActiveWindow(self.eventEditor)
        mimeData = QtGui.qApp.clipboard().mimeData()
        baData = mimeData.data(QtGui.qApp.outputCalculatorMimeDataType)
        if baData:
            QtGui.qApp.mainWindow.setWindowState(self._mainWindowState)
            data = forceString(QtCore.QString.fromUtf8(baData))
            self.modelAPActionProperties.setLaboratoryCalculatorData(data)

    def onCurrentActionAdd(self, flatCode, action):
        model = self.tblAPActions.model()
        items = model.items()
        noPresentLeaved = True
        self.noPresent = {}
        if hasattr(self, 'supportServiceBtnsDesc'):
            for code in self.supportServiceBtnsDesc.keys():
                self.noPresent[code] = True
        self.gBoxSupportService.setVisible(False)
        for item in items:
            record = item[0]
            if record:
                if not (noPresentLeaved):
                    break
                actionTypeId = forceRef(record.value('actionType_id'))
                actionType = CActionTypeCache.getById(actionTypeId) if actionTypeId else None
                if u'leaved' in actionType.flatCode.lower():
                    noPresentLeaved = False
                for code, value in self.noPresent.items():
                    if not value:
                        break
                    actionTypeId = forceRef(record.value('actionType_id'))
                    actionType = CActionTypeCache.getById(actionTypeId) if actionTypeId else None
                    if (code in actionType.flatCode.lower()
                        and record.value('endDate').isNull()
                        and forceInt(record.value('status')) != ActionStatus.Done
                        ):
                        self.noPresent[code] = False
        self.gBoxSupportService.cleartBtns()
        for code, value in self.noPresent.items():
            if value:
                self.gBoxSupportService.addShowingBtn(code)

        if noPresentLeaved:
            if u'received' in flatCode.lower():
                if action[u'Направлен в отделение']:
                    self.btnNextAction.setText(u'Движение')
                    self.btnNextAction.setVisible(
                        not self.edtAPEndDate.date() or bool(QtGui.qApp.userId and not QtGui.qApp.userSpecialityId))
                else:
                    self.btnNextAction.setText(u'Выписка')
                    self.btnNextAction.setVisible(True)
            elif u'moving' in flatCode.lower():
                if action[u'Переведен в отделение']:
                    self.btnNextAction.setText(u'Движение')
                    self.btnNextAction.setVisible(
                        not self.edtAPEndDate.date() or bool(QtGui.qApp.userId and not QtGui.qApp.userSpecialityId))
                else:
                    self.btnNextAction.setText(u'Выписка')
                    self.btnNextAction.setVisible(True)
                self.gBoxSupportService.setVisible(True)
            elif (
                        u'inspectPigeonHole'.lower() in flatCode.lower() or u'reanimation' in flatCode.lower() or u'maternityward' in flatCode.lower()):
                self.btnNextAction.setText(u'Закончить')
                self.btnNextAction.setVisible(not self.edtAPEndDate.date())
            else:
                self.btnNextAction.setText(u'Действие')
                self.btnNextAction.setVisible(False)
                self.btnPlanNextAction.setVisible(False)
        else:
            self.btnNextAction.setText(u'Действие')
            self.btnNextAction.setVisible(False)
            self.btnPlanNextAction.setVisible(False)

    def getIdListActionType(self, flatCode):
        db = QtGui.qApp.db
        tableActionType = db.table('ActionType')
        actionTypeIdList = db.getIdList(tableActionType, [tableActionType['id']],
                                        [tableActionType['flatCode'].like(flatCode), tableActionType['deleted'].eq(0)])
        if len(actionTypeIdList) > 1:
            actionTypeId = self.getPriorityActionType(actionTypeIdList)
            if not actionTypeId:
                dialogActionType = CActionTypeDialogTableModel(self, actionTypeIdList)
                if dialogActionType.exec_():
                    actionTypeId = dialogActionType.currentItemId()
        else:
            actionTypeId = actionTypeIdList[0] if actionTypeIdList else None
        return actionTypeId

    def getPriorityActionType(self, idList):
        eventTypeId = self.eventEditor.getEventTypeId()
        db = QtGui.qApp.db
        tableEventTypeAction = db.table('EventType_Action')
        cond = [tableEventTypeAction['eventType_id'].eq(eventTypeId),
                tableEventTypeAction['actionType_id'].inlist(idList)]
        actionTypeIdList = db.getIdList(tableEventTypeAction, 'actionType_id', db.joinAnd(cond))
        if actionTypeIdList:
            return actionTypeIdList[0]
        else:
            return None

    def checkActionByNextEventCreation(self):
        if QtGui.qApp.isNextEventCreationFromAction():
            res = QtGui.QMessageBox.warning(self,
                                            u'Внимание!',
                                            u'Добавить движение во вновь зарегистрированное Событие?',
                                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                            QtGui.QMessageBox.No)
            if res == QtGui.QMessageBox.Yes:
                return True
            else:
                return False
        return False

    @QtCore.pyqtSlot()
    def on_btnPlanNextAction_clicked(self):
        model = self.tblAPActions.model()
        items = model.items()
        row = self.tblAPActions.currentIndex().row()
        if 0 <= row < len(items):
            record, action = items[row]
            dialog = CGetExecutionPlan(self, record, action.getExecutionPlan())
            dialog.exec_()
            action.setExecutionPlan(dialog.model.executionPlan)

    @QtCore.pyqtSlot()
    def onbtnReanimation_clicked(self):
        if not self.noPresent.get('maternityward', True):
            QtGui.QMessageBox.information(self,
                                          u'Внимание!',
                                          u'В действии "Родовое отделение" не указана дата выполнения.\n'
                                          u'Добавление действия "Реанимация" невозможно')
            return False
        model = self.tblAPActions.model()
        row = self.tblAPActions.currentIndex().row()
        items = model.items()
        if 0 <= row < len(items):
            sourceRecord, sourceAction = items[row]
            sourceActionTypeId = forceRef(sourceRecord.value('actionType_id')) if sourceRecord else None
            sourceActionType = CActionTypeCache.getById(sourceActionTypeId) if sourceActionTypeId else None
            if sourceActionType and u'moving' in sourceActionType.flatCode.lower():
                orgStructurePresence = sourceAction[u'Отделение пребывания']

                actionTypeId = self.getIdListActionType(u'reanimation')
                if actionTypeId:
                    actionType = CActionTypeCache.getById(actionTypeId)
                    model.addRow(actionTypeId, actionType.amount)
                    record, action = model.items()[-1]
                    if orgStructurePresence:
                        action[u'Переведен из отделения'] = orgStructurePresence
                    record.setValue('begDate', toVariant(QtCore.QDateTime.currentDateTime()))
                    record.setValue('finance_id', toVariant(sourceRecord.value(u'finance_id')))
                    row = len(model.items()) - 1
                    self.tblAPActions.setCurrentIndex(model.index(row, 0))
                    self.edtAPBegDate.setFocus(QtCore.Qt.OtherFocusReason)
                    self.updateAmount()
                else:
                    QtGui.QMessageBox.information(self,
                                                  u'Не найден тип действия',
                                                  u'Не удалось найти тип действия "Реанимация"\n'
                                                  u'(код для отчетов "reanimation")')
            else:
                QtGui.QMessageBox.information(self,
                                              u'Не найден тип действия',
                                              u'Не удалось найти тип действия "Движение"\n'
                                              u'из которого осуществляется перевод в реанимацию')

    def onbtnMaternityWard_clicked(self):
        if not self.noPresent.get('reanimation', True):
            QtGui.QMessageBox.information(self,
                                          u'Внимание!',
                                          u'В действии "Реанимация" не указана дата выполнения.\n'
                                          u'Добавление действия "Родовое отделение" невозможно')
            return False
        model = self.tblAPActions.model()
        row = self.tblAPActions.currentIndex().row()
        items = model.items()
        if 0 <= row < len(items):
            sourceRecord, sourceAction = items[row]
            sourceActionTypeId = forceRef(sourceRecord.value('actionType_id')) if sourceRecord else None
            sourceActionType = CActionTypeCache.getById(sourceActionTypeId) if sourceActionTypeId else None
            if sourceActionType and u'moving' in sourceActionType.flatCode.lower():
                orgStructurePresence = sourceAction[u'Отделение пребывания']

                actionTypeId = self.getIdListActionType(u'maternityward')
                if actionTypeId:
                    actionType = CActionTypeCache.getById(actionTypeId)
                    model.addRow(actionTypeId, actionType.amount)
                    record, action = model.items()[-1]
                    if orgStructurePresence:
                        action[u'Переведен из отделения'] = orgStructurePresence
                    record.setValue('begDate', toVariant(QtCore.QDateTime.currentDateTime()))
                    record.setValue('finance_id', toVariant(sourceRecord.value(u'finance_id')))
                    row = len(model.items()) - 1
                    self.tblAPActions.setCurrentIndex(model.index(row, 0))
                    self.edtAPBegDate.setFocus(QtCore.Qt.OtherFocusReason)
                    self.updateAmount()
                else:
                    QtGui.QMessageBox.information(self,
                                                  u'Не найден тип действия',
                                                  u'Не удалось найти тип действия "Родовое отделение"\n'
                                                  u'(код для отчетов "maternityward")')
            else:
                QtGui.QMessageBox.information(self,
                                              u'Не найден тип действия',
                                              u'Не удалось найти тип действия "Движение"\n'
                                              u'из которого осуществляется перевод в родовое отделение')

    @QtCore.pyqtSlot()
    def on_btnNextAction_clicked(self):
        db = QtGui.qApp.db
        if self.cmbAPStatus.currentIndex() == 3:
            currentDateTime = QtCore.QDateTime.currentDateTime()
            table = db.table('vrbPersonWithSpeciality')
            personId = QtGui.qApp.userId if (
            QtGui.qApp.userId and QtGui.qApp.userSpecialityId) else self.cmbAPSetPerson.value()
            record = db.getRecordEx(table, [table['name']], [table['id'].eq(personId)]) if personId else None
            personName = forceString(record.value('name')) if record else ''
            self.edtAPNote.setText(u'Отменить: %s %s' % (currentDateTime.toString('dd-MM-yyyy hh:mm'), personName))
        else:
            tableEventType = db.table('EventType')
            model = self.tblAPActions.model()
            items = model.items()
            row = self.tblAPActions.currentIndex().row()
            newRow = 0
            currentDateTime = QtCore.QDateTime.currentDateTime()
            noExecTimeNextDialog = True
            if 0 <= row < len(items):
                record, action = items[row]
                actionTypeId = forceRef(record.value('actionType_id')) if record else None
                directionDate = forceDateTime(record.value('directionDate')) if record else None
                setPersonId = forceRef(record.value('setPerson_id')) if record else None
                actionType = CActionTypeCache.getById(actionTypeId) if actionTypeId else None
                if not actionType:
                    return
                if u'inspectPigeonHole'.lower() in actionType.flatCode.lower():
                    oldEndDate = forceDateTime(record.value('endDate'))
                    if not oldEndDate:
                        record.setValue('endDate', toVariant(currentDateTime))
                    if forceInt(record.value('status')) != ActionStatus.NotProvided:  # "Не предусмотрено"
                        record.setValue('status', toVariant(ActionStatus.Done))
                    if hasattr(self.eventEditor, 'btnNextActionSetFocus'):
                        self.eventEditor.btnNextActionSetFocus()
                elif u'received' in actionType.flatCode.lower():
                    orgStructureMoving = action[u'Направлен в отделение']
                    receivedQuoting = action[u'Квота'] if action.getType().containsPropertyWithName(u'Квота') else None
                    currentOrgStructureId = None
                    if orgStructureMoving:
                        actionTypeId = self.getIdListActionType(u'moving')
                    else:
                        actionTypeId = self.getIdListActionType(u'leaved')
                        currentOrgStructureId = QtGui.qApp.currentOrgStructureId()
                    if actionTypeId:
                        oldEndDate = forceDateTime(record.value('endDate'))
                        if not oldEndDate:
                            record.setValue('endDate', toVariant(currentDateTime))
                        if forceInt(record.value('status')) != ActionStatus.NotProvided:  # "Не предусмотрено"
                            record.setValue('status', toVariant(ActionStatus.Done))
                        self.receivedFinanceId = forceRef(record.value('finance_id'))
                        model.addRow(actionTypeId, actionType.amount)
                        newRow = len(model.items()) - 1
                        self.updateAmount()
                        oldBegDate = forceDateTime(record.value('begDate'))
                        record, action = model.items()[-1]
                        eventTypeId = self.eventEditor.getEventTypeId()
                        if eventTypeId:
                            recordET = db.getRecordEx(tableEventType, [tableEventType['actionFinance']],
                                                      [tableEventType['deleted'].eq(0),
                                                       tableEventType['id'].eq(eventTypeId)])
                            self.eventActionFinance = forceInt(recordET.value('actionFinance')) if recordET else None
                            if self.eventActionFinance == 0:
                                record.setValue('finance_id', toVariant(self.receivedFinanceId))
                        if orgStructureMoving:
                            action[u'Отделение пребывания'] = orgStructureMoving
                        elif currentOrgStructureId:
                            typeRecord = QtGui.qApp.db.getRecordEx('OrgStructure', 'type',
                                                                   'id = %d AND type = 4 AND deleted = 0' % (
                                                                   currentOrgStructureId))
                            if typeRecord and (typeRecord.value('type')) == 4:
                                if action.getType().containsPropertyWithName(u'Отделение'):
                                    action[u'Отделение'] = currentOrgStructureId
                        if forceStringEx(
                                db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'infisCode')) == u'б15':
                            record.setValue('begDate', toVariant(oldBegDate))
                        else:
                            if oldEndDate:
                                record.setValue('begDate', toVariant(oldEndDate))
                            else:
                                record.setValue('begDate', toVariant(currentDateTime))
                        if action.getType().containsPropertyWithName(u'Квота') and receivedQuoting:
                            action[u'Квота'] = receivedQuoting
                elif u'moving' in actionType.flatCode.lower():
                    orgStructureTransfer = action[u'Переведен в отделение']
                    orgStructurePresence = action[u'Отделение пребывания']
                    oldEndDate = forceDateTime(record.value('endDate'))
                    if not oldEndDate:
                        record.setValue('endDate', toVariant(currentDateTime))
                        oldEndDate = currentDateTime
                    if forceInt(record.value('status')) != ActionStatus.NotProvided:  # "Не предусмотрено"
                        record.setValue('status', toVariant(ActionStatus.Done))
                    movingQuoting = action[u'Квота'] if action.getType().containsPropertyWithName(u'Квота') else None
                    if orgStructureTransfer:
                        actionTypeId = self.getIdListActionType(u'moving')
                        if actionTypeId:
                            # Добавление связанного события
                            if QtGui.qApp.isNextEventCreationFromAction():  # and (self.eventEditor.getMesId() or self.eventEditor.getCSGId()) and self.eventEditor.getMesSpecificationId():
                                reanimationAction = None
                                maternitywardAction = None
                                for tmpRecord, tmpAction in items:
                                    if not any(flatCode in tmpAction.getType().flatCode.lower() for flatCode in
                                               [u'reanimation', u'maternityward']):
                                        continue  # пропустить не реанимационные и не родовые действия
                                    elif not tmpRecord.value('endDate').isNull() or tmpRecord.value(
                                            'status') == ActionStatus.Done:
                                        continue  # пропустить все законченные реанимации и родовые
                                    else:
                                        if (u'reanimation' in tmpAction.getType().flatCode.lower()):
                                            reanimationAction = tmpAction
                                        elif (u'maternityward' in tmpAction.getType().flatCode.lower()):
                                            maternitywardAction = tmpAction
                                            # if maternitywardAction and reanimationAction:
                                            #     break
                                            # else:
                                            #     continue
                                if QtGui.qApp.userHasRight(urSkipEventCreationAfterMoving):
                                    if QtGui.QMessageBox.question(
                                            self, u'Действие "Движение"', u'Создать новое обращение?',
                                            QtGui.QMessageBox.No | QtGui.QMessageBox.Yes, QtGui.QMessageBox.No
                                    ) == QtGui.QMessageBox.Yes:
                                        self.eventEditor.eventDate = forceDate(record.value('endDate'))
                                        self.eventEditor.edtEndDate.setDate(self.eventEditor.eventDate)
                                        self.createMovingEvent(
                                            actionTypeId,
                                            oldEndDate,
                                            orgStructurePresence,
                                            orgStructureTransfer,
                                            reanimationAction,
                                            maternitywardAction
                                        )
                                        return

                            model.addRow(actionTypeId, actionType.amount)
                            newRow = len(model.items()) - 1
                            self.updateAmount()
                            record, action = model.items()[-1]
                            if self.eventActionFinance == 0:
                                record.setValue('finance_id', toVariant(self.receivedFinanceId))
                            action[u'Отделение пребывания'] = orgStructureTransfer
                            if orgStructurePresence:
                                action[u'Переведен из отделения'] = orgStructurePresence
                            if oldEndDate:
                                record.setValue('begDate', toVariant(oldEndDate))
                            else:
                                record.setValue('begDate', toVariant(currentDateTime))
                            if action.getType().containsPropertyWithName(u'Квота') and movingQuoting:
                                action[u'Квота'] = movingQuoting
                    else:
                        actionTypeId = self.getIdListActionType(u'leaved')
                        if actionTypeId:
                            model.addRow(actionTypeId, actionType.amount)
                            newRow = len(model.items()) - 1
                            self.updateAmount()
                            record, action = model.items()[-1]
                            if self.eventActionFinance == 0:
                                record.setValue('finance_id', toVariant(self.receivedFinanceId))
                            if orgStructurePresence:
                                if action.getType().containsPropertyWithName(u'Отделение'):
                                    action[u'Отделение'] = orgStructurePresence
                            if oldEndDate:
                                record.setValue('begDate', toVariant(oldEndDate))
                            else:
                                record.setValue('begDate', toVariant(currentDateTime))
                            if action.getType().containsPropertyWithName(u'Квота') and movingQuoting:
                                action[u'Квота'] = movingQuoting
                elif u'reanimation' in actionType.flatCode.lower():
                    oldEndDate = forceDateTime(record.value('endDate'))
                    if not oldEndDate:
                        oldEndDate = currentDateTime
                        record.setValue('endDate', toVariant(oldEndDate))
                    if forceInt(record.value('status')) != ActionStatus.NotProvided:  # "Не предусмотрено"
                        record.setValue('status', toVariant(ActionStatus.Done))
                    # Ищем незакрытое движение и используем его отделение пребывания для заполнения Реанимация['Переведен в отделение']
                    for movingRow, (otherRecord, otherAction) in enumerate(model.items()):
                        movingActionTypeId = self.getIdListActionType(u'moving')
                        if (forceRef(otherRecord.value('actionType_id')) == movingActionTypeId
                            and forceInt(otherRecord.value('status')) != ActionStatus.Done):
                            action[u'Переведен в отделение'] = otherAction[u'Отделение пребывания']
                            self.tblAPActions.setCurrentIndex(model.index(movingRow, 0))
                            noExecTimeNextDialog = False
                            break

                elif u'maternityward' in actionType.flatCode.lower():
                    oldEndDate = forceDateTime(record.value('endDate'))
                    if not oldEndDate:
                        oldEndDate = currentDateTime
                        record.setValue('endDate', toVariant(oldEndDate))
                    if forceInt(record.value('status')) != ActionStatus.NotProvided:  # "Не предусмотрено"
                        record.setValue('status', toVariant(ActionStatus.Done))
                    # Ищем незакрытое движение и используем его отделение пребывания для заполнения Родовое отделение['Переведен в отделение']
                    for movingRow, (otherRecord, otherAction) in enumerate(model.items()):
                        movingActionTypeId = self.getIdListActionType(u'moving')
                        if (forceRef(otherRecord.value('actionType_id')) == movingActionTypeId
                            and forceInt(otherRecord.value('status')) != ActionStatus.Done):
                            action[u'Переведен в отделение'] = otherAction[u'Отделение пребывания']
                            self.tblAPActions.setCurrentIndex(model.index(movingRow, 0))
                            noExecTimeNextDialog = False
                            break
                if noExecTimeNextDialog:
                    row = newRow if newRow else (row + 1) if (row + 1) <= model.rowCount() - 1 else model.rowCount() - 1
                    self.tblAPActions.setCurrentIndex(model.index(row, 0))
                    self.edtAPBegDate.setFocus(QtCore.Qt.OtherFocusReason)

    def getCurrentTimeAction(self, actionDate):
        currentDateTime = QtCore.QDateTime.currentDateTime()
        if currentDateTime == actionDate:
            currentTime = currentDateTime.time()
            return currentTime.addSecs(60)
        else:
            return currentDateTime.time()

    def clientId(self):
        return self.eventEditor.clientId

    def getDischargeQuotaTypeNumber(self):
        for row in range(self.modelAPActions.rowCount()):
            actTypeName = forceString(self.modelAPActions.data(self.modelAPActions.index(row, 0)))
            if u'Выписка' in actTypeName:
                model = self.tblAPActions.model()
                items = model.items()
                action = items[row][1]
                if not action.containsPropertyWithName(u'Квота'):
                    return None, None
                quotaText = action.getProperty(u'Квота').getText()
                quotaNumber = quotaText.split('|')[0].strip()
                if quotaNumber:
                    return forceInt(quotaNumber[:2]), row
                else:
                    return None, row

        return None, None

    def createMovingEvent(self, actionTypeId, datetime, oldOrgStructure, newOrgStructure, reanimationAction=None,
                          maternitywardAction=None):
        db = QtGui.qApp.db
        eventTable = db.table('Event')
        actionTable = db.table('Action')
        actionPropertyTable = db.table('ActionProperty')
        actionPropertyOSTable = db.table('ActionProperty_OrgStructure')

        osEventTypeTable = db.table('OrgStructure_EventType')
        eventTypeActionTable = db.table('EventType_Action')

        eventTypeQueryTable = osEventTypeTable.innerJoin(eventTypeActionTable,
                                                         eventTypeActionTable['eventType_id'].eq(
                                                             osEventTypeTable['eventType_id']))
        eventTypeRecord = db.getRecordEx(eventTypeQueryTable,
                                         osEventTypeTable['eventType_id'],
                                         where=[osEventTypeTable['master_id'].eq(newOrgStructure),
                                                eventTypeActionTable['actionType_id'].inlist(
                                                    getActionTypeIdListByFlatCode('received%'))])

        eventTypeId = forceRef(eventTypeRecord.value(0)) if eventTypeRecord else self.eventEditor.eventTypeId

        clientId = self.eventEditor.clientId

        contractDbModel = CContractDbModel(self)
        contractDbModel.setOrgId(QtGui.qApp.currentOrgId())
        contractDbModel.setBegDate(datetime)
        contractDbModel.setEndDate(datetime)
        contractDbModel.setClientInfo(clientId,
                                      self.eventEditor.clientSex,
                                      self.eventEditor.clientAge,
                                      self.eventEditor.clientWorkOrgId,
                                      self.eventEditor.clientPolicyInfoList)
        contractDbModel.setEventTypeId(eventTypeId)
        contractIdList = contractDbModel.idList()
        contractId = contractIdList[0] if contractIdList else self.eventEditor.contractId

        externalId = self.eventEditor.getExternalId()
        order = self.eventEditor.getOrder()

        if not self.eventEditor.checkDataEntered():
            return

        if reanimationAction:
            reanimationRecord = reanimationAction.getRecord()
            # копирование действия реанимации в новое событие
            newReanimationRecord = actionTable.newRecord(otherRecord=reanimationRecord)
            newReanimationAction = CAction(record=newReanimationRecord)
            newReanimationRecord.setValue('begDate', toVariant(datetime))
            # закрытие действия-реанимации прошлого события
            reanimationRecord.setValue('endDate', toVariant(datetime))
            if forceInt(reanimationRecord.value('status')) != ActionStatus.NotProvided:  # "Не предусмотрено"
                reanimationRecord.setValue('status', toVariant(ActionStatus.Done))
            # копирование свойств действия
            for propertyObject in reanimationAction.getType().getPropertiesByName().values():
                newReanimationAction[propertyObject.name] = reanimationAction[propertyObject.name]
                # сохранение нового действия-реанимация в рамках нового события

        if maternitywardAction:
            maternitywardRecord = maternitywardAction.getRecord()
            # копирование действия родовое отделение в новое событие
            newMaternitywardRecord = actionTable.newRecord(otherRecord=maternitywardRecord)
            newMaternitywardAction = CAction(record=newMaternitywardRecord)
            newMaternitywardRecord.setValue('begDate', toVariant(datetime))
            # закрытие действия-родовое отделение прошлого события
            maternitywardRecord.setValue('endDate', toVariant(datetime))
            if forceInt(maternitywardRecord.value('status')) != ActionStatus.NotProvided:  # "Не предусмотрено"
                maternitywardRecord.setValue('status', toVariant(ActionStatus.Done))
            # копирование свойств действия
            for propertyObject in maternitywardAction.getType().getPropertiesByName().values():
                newMaternitywardAction[propertyObject.name] = maternitywardAction[propertyObject.name]
                # сохранение нового действия-родовое отделение в рамках нового события

        prevEventId = self.eventEditor.save()
        self.eventEditor.close()

        db.transaction()
        eventRecord = eventTable.newRecord()
        eventRecord.setValue('externalId', toVariant(externalId))
        eventRecord.setValue('eventType_id', eventTypeId)
        eventRecord.setValue('org_id', toVariant(QtGui.qApp.currentOrgId()))
        eventRecord.setValue('client_id', toVariant(clientId))
        eventRecord.setValue('contract_id', contractId)
        eventRecord.setValue('setDate', toVariant(datetime))
        eventRecord.setValue('isPrimary', toVariant(1))
        eventRecord.setValue('order', toVariant(order))
        eventRecord.setValue('prevEvent_id', toVariant(prevEventId))
        eventId = db.insertRecord(eventTable, eventRecord)

        actionRecord = actionTable.newRecord()
        actionRecord.setValue('actionType_id', actionTypeId)
        actionRecord.setValue('event_id', toVariant(eventId))
        actionRecord.setValue('directionDate', toVariant(datetime.addSecs(60)))
        actionRecord.setValue('status', toVariant(
            ActionStatus.Started))  # ожидание  #TODO: atronah: возможно надо согласовать с i939
        actionRecord.setValue('begDate', toVariant(datetime.addSecs(60)))
        actionId = db.insertRecord(actionTable, actionRecord)

        APTypeFromId = forceRef(db.getRecordEx('ActionPropertyType', 'id',
                                               'actionType_id=%s AND name=\'%s\' AND deleted = 0' % (
                                               actionTypeId, u'Переведен из отделения')).value(0))
        APTypeCurrentId = forceRef(db.getRecordEx('ActionPropertyType', 'id',
                                                  'actionType_id=%s AND name=\'%s\' AND deleted = 0' % (
                                                  actionTypeId, u'Отделение пребывания')).value(0))

        actionPropertyRecordFrom = actionPropertyTable.newRecord()
        actionPropertyRecordFrom.setValue('action_id', actionId)
        actionPropertyRecordFrom.setValue('type_id', APTypeFromId)
        actionPropertyFromId = db.insertRecord(actionPropertyTable, actionPropertyRecordFrom)

        actionPropertyOSRecordFrom = actionPropertyOSTable.newRecord()
        actionPropertyOSRecordFrom.setValue('id', actionPropertyFromId)
        actionPropertyOSRecordFrom.setValue('value', oldOrgStructure)
        db.insertRecord(actionPropertyOSTable, actionPropertyOSRecordFrom)

        actionPropertyRecordCurrent = actionPropertyTable.newRecord()
        actionPropertyRecordCurrent.setValue('action_id', actionId)
        actionPropertyRecordCurrent.setValue('type_id', APTypeCurrentId)
        actionPropertyCurrentId = db.insertRecord(actionPropertyTable, actionPropertyRecordCurrent)

        actionPropertyOSRecordCurrent = actionPropertyOSTable.newRecord()
        actionPropertyOSRecordCurrent.setValue('id', actionPropertyCurrentId)
        actionPropertyOSRecordCurrent.setValue('value', newOrgStructure)
        db.insertRecord(actionPropertyOSTable, actionPropertyOSRecordCurrent)

        if reanimationAction:
            newReanimationAction.save(eventId)

        if maternitywardAction:
            newMaternitywardAction.save(eventId)

        db.commit()

        return eventId, actionId

    def requestNewEvent(self, orgStructureTransfer, personId, financeId, orgStructurePresence, actionDate,
                        movingQuoting, actionTypeId, actionByNewEvent):
        from Events.CreateEvent import requestNewEvent
        clientId = self.eventEditor.clientId
        externalId = self.eventEditor.getExternalId()
        eventId = self.eventEditor.save()
        self.eventEditor.close()
        orgStructureId = orgStructureTransfer
        flagHospitalization = True
        diagnos = None
        if clientId:
            eventTypeFilterHospitalization = '(EventType.medicalAidType_id IN (SELECT rbMedicalAidType.id from rbMedicalAidType where rbMedicalAidType.code IN (\'1\', \'2\', \'3\', \'7\')))'
            return requestNewEvent(self.eventEditor, clientId, flagHospitalization, actionTypeId, [orgStructureId],
                                   eventTypeFilterHospitalization, actionDate, personId, eventId, diagnos, financeId,
                                   movingQuoting, actionByNewEvent, externalId)
        return None

    def updatePropTable(self, action):
        self.tblAPProps.model().setAction(action, self.eventEditor.clientId, self.eventEditor.clientSex,
                                          self.eventEditor.clientAge)
        self.tblAPProps.init()
        self.tblAPProps.resizeRowsToContents()

    def onActionDataChanged(self, name, value):
        if not self.isPostUiSetted:
            return
        model = self.tblAPActions.model()
        items = model.items()
        row = self.tblAPActions.currentIndex().row()
        if 0 <= row < len(items):
            # record = items[row][0]
            record, action = items[row]
            # i3095 Принужительно проставляем статус мероприятия "Проведено", при условии что
            # если есть дата выполнения и статус "начато"
            if self.edtAPEndDate.date() and forceInt(record.value('status')) == ActionStatus.Started:
                record.setValue('status', ActionStatus.Done)
            elif (not self.edtAPEndDate.date()) and forceInt(record.value('status')) == ActionStatus.Done:
                record.setValue('status', ActionStatus.Started)

            record.setValue(name, toVariant(value))
            actionTypeId = forceRef(record.value('actionType_id')) if record else None
            actionType = CActionTypeCache.getById(actionTypeId) if actionTypeId else None

            if (u'moving' in actionType.flatCode.lower()
                or u'received' in actionType.flatCode.lower()
                or u'inspectPigeonHole'.lower() in actionType.flatCode.lower()
                or u'reanimation' in actionType.flatCode.lower()
                or u'maternityward' in actionType.flatCode.lower()
                ):
                self.onCurrentActionAdd(actionType.flatCode, action)
            else:
                self.gBoxSupportService.setVisible(False)
                self.btnNextAction.setText(u'Действие')
                self.btnNextAction.setVisible(False)
                self.btnPlanNextAction.setVisible(False)
            if actionType.defaultPlannedEndDate == CActionType.dpedBegDatePlusAmount and name in ['amount', 'begDate']:
                begDate = self.edtAPBegDate.date()
                amountValue = int(self.edtAPAmount.value())
                date = begDate.addDays(amountValue - 1) if (amountValue and begDate.isValid()) else QtCore.QDate()
                # self.edtAPPlannedEndDate.setDate(date)

    def updateAmount(self):
        model = self.tblAPActions.model()
        index = self.tblAPActions.currentIndex()
        if index.isValid():
            model.updateActionAmount(index.row())

    def loadPrevAction(self, searchMode):
        model = self.tblAPActions.model()
        items = model.items()
        row = self.tblAPActions.currentIndex().row()
        if QtGui.qApp.userHasRight(urCopyPrevAction) and 0 <= row < len(items):
            action = items[row][1]
            prevActionIds = self.getPrevActionsList(action, searchMode)
            if prevActionIds:
                dialog = CPrevActionChooser(self)
                dialog.tblPrevActions.setIdList(prevActionIds)
                if dialog.exec_():
                    prevActionId = dialog.tblPrevActions.currentItemId()

                    # prevActionId = self.eventEditor.getPrevActionId(action, anyWithSameSpeciality)
                    if prevActionId:
                        action.updateByActionId(prevActionId)
                        self.tblAPProps.model().reset()
                        self.tblAPProps.init()
                        self.tblAPProps.resizeRowsToContents()
                        model.updateActionAmount(row)

    def getPrevActionsList(self, action, searchMode):
        actionTypeId = action.getType().id
        actionTypes = QtGui.qApp.db.getDistinctIdList('rbActionTypeSimilarity', 'firstActionType_id',
                                                      ['secondActionType_id=%s' % actionTypeId, 'similarityType=0'])
        actionTypes.extend(QtGui.qApp.db.getDistinctIdList('rbActionTypeSimilarity', 'secondActionType_id',
                                                           ['firstActionType_id=%s' % actionTypeId,
                                                            'similarityType=0']))
        actionTypes.append(actionTypeId)
        actionTypes = tuple(set(actionTypes))
        actionId = forceRef(action.getRecord().value('id')) if action.getRecord() else None
        personId = forceRef(action.getRecord().value('person_id')) or self.eventEditor.personId
        eventDate = self.eventEditor.eventDate if self.eventEditor.eventDate else QtCore.QDate.currentDate()

        db = QtGui.qApp.db
        tableAction = db.table('Action')
        tableEvent = db.table('Event')
        table = tableAction.leftJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
        if searchMode == 1:
            tablePerson = db.table('Person')
            tablePerson2 = db.table('Person').alias('Person2')
            table = table.leftJoin(tablePerson, tablePerson['id'].eq(tableEvent['execPerson_id']))
            table = table.leftJoin(tablePerson2, tablePerson2['speciality_id'].eq(tablePerson['speciality_id']))

        cond = [tableAction['deleted'].eq(0),
                tableEvent['deleted'].eq(0),
                tableAction['actionType_id'].inlist(actionTypes),
                tableEvent['client_id'].eq(self.eventEditor.clientId),
                # tableEvent['execDate'].le(eventDate),
                tableAction['begDate'].le(eventDate)
                ]
        if searchMode == 1:
            cond.append(tablePerson2['id'].eq(personId))
        elif searchMode == 0:
            cond.append(tableEvent['execPerson_id'].eq(personId))
        if actionId:
            cond.append(tableAction['id'].ne(actionId))
        idList = db.getIdList(table, tableAction['id'].name(), cond, tableEvent['execDate'].name() + ' DESC')
        if idList:
            return idList
        else:
            return None

    @QtCore.pyqtSlot()
    def on_cmbHMPKind_currentIndexChanged(self):
        self.onActionDataChanged('hmpKind_id', self.cmbHMPKind.value())
        cureKindId = forceRef(self.cmbHMPKind.value())
        self.cmbHMPMethod.setFilter('cureKind_id = %d' % cureKindId if cureKindId else '0')

        record = self.tblAPActions.model().items()[self.tblAPActions.currentIndex().row()][0]

        if record:
            oldIndex = self.cmbHMPMethod.model().searchId(forceRef(record.value('hmpMethod_id')))
        else:
            oldIndex = 0
        self.cmbHMPMethod.setCurrentIndex(oldIndex if oldIndex != -1 else 0)
        self.saveMovingWithoutMes = forceBool(self.getCureKindCode(cureKindId) != '0')

    @QtCore.pyqtSlot(int)
    def on_cmbHMPMethod_currentIndexChanged(self, index=None):
        self.onActionDataChanged('hmpMethod_id', self.cmbHMPMethod.value())

    def getCureKindCode(self, cureKindId):
        return forceString(QtGui.qApp.db.translate('rbHighTechCureKind', 'id', cureKindId, 'code'))

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelAPActions_currentChanged(self, current, previous):
        if hasattr(self.eventEditor, 'scrollArea'):
            scrollPos = self.eventEditor.scrollArea.verticalScrollBar().sliderPosition()
        self.onActionCurrentChanged()
        if hasattr(self.eventEditor, 'scrollArea'):
            self.eventEditor.scrollArea.verticalScrollBar().setSliderPosition(scrollPos)
            index = self.tblAPActions.currentIndex()
            rowPos = self.tblAPActions.rowViewportPosition(index.row())
            self.eventEditor.scrollArea.ensureWidgetVisible(self.tblAPActions, rowPos, 0)

    # @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    # def on_selectionModelAPActionProperties_currentChanged(self, current, previous):
    #     if hasattr(self.eventEditor, 'scrollArea'):
    #         index = self.tblAPProps.currentIndex()
    #         rowPos = self.tblAPProps.rowViewportPosition(index.row())
    #         self.eventEditor.scrollArea.ensureWidgetVisible(self.tblAPProps, rowPos, 0)

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_modelAPActions_dataChanged(self, topLeft, bottomRight):
        topLeftRow = topLeft.row()
        bottomRightRow = bottomRight.row()
        if topLeftRow <= self.tblAPActions.currentIndex().row() <= bottomRightRow:
            self.onActionCurrentChanged()

    @QtCore.pyqtSlot(int)
    def on_modelAPActions_amountChanged(self, row):
        if row == self.tblAPActions.currentIndex().row():
            model = self.modelAPActions
            record = model._items[row][0]
            actionTypeId = forceRef(record.value('actionType_id'))
            amount = forceDouble(record.value('amount'))
            personId = forceRef(record.value('person_id'))
            financeId = forceRef(record.value('finance_id'))
            contractId = forceRef(record.value('contract_id'))
            self.edtAPAmount.setValue(amount)
            self.edtAPUet.setValue(amount * self.eventEditor.getUet(actionTypeId, personId, financeId, contractId))

    @QtCore.pyqtSlot()
    def on_actAPActionAddSuchAs_triggered(self):
        model = self.tblAPActions.model()
        row = self.tblAPActions.currentIndex().row()
        if 0 <= row < model.rowCount() - 1:
            record = model._items[row][0]
            actionTypeId = forceRef(record.value('actionType_id'))
            if not self.checkPossibilityAddingActionType(actionTypeId):
                return
            index = model.index(model.rowCount() - 1, 0)
            if model.setData(index, toVariant(actionTypeId)):
                self.tblAPActions.setCurrentIndex(index)

    @QtCore.pyqtSlot()
    def on_actAPActionAddSameForPeriod_triggered(self):
        model = self.tblAPActions.model()
        row = self.tblAPActions.currentIndex().row()
        if not model.inRange(row): return

        baseRecord = model._items[row][0]
        actionTypeId = forceRef(baseRecord.value('actionType_id'))
        if not self.checkPossibilityAddingActionType(actionTypeId):
            return

        periodParams = self.getPeriodParameters(baseRecord)
        if not periodParams: return

        ranges = timeSeries(*periodParams)
        self.addSameActionsForPeriod(baseRecord, actionTypeId, ranges)

        # NOTE: reset() is faster than updating one-by-one
        model.reset()
        self.tblAPActions.setCurrentIndex(model.lastItemIndex())

    def getPeriodParameters(self, baseRecord):
        baseBegDate = forceDateTime(baseRecord.value('begDate'))
        # XXX: when does eventDate equals endDate?
        baseEndDate = forceDateTime(self.eventEditor.eventDate)

        eventTypeId = self.eventEditor.eventTypeId
        anyDateAllowed = isEventAnyActionDatePermited(eventTypeId)

        minBegPeriod = baseBegDate if not anyDateAllowed else None
        maxEndPeriod = baseEndDate if not baseEndDate.isNull() else None

        dlg = CActionsForPeriodDialog(self, minBegPeriod, maxEndPeriod)
        if dlg.exec_():
            return dlg.periodParameters()

    def addSameActionsForPeriod(self, baseRecord, actionTypeId, ranges):
        model = self.tblAPActions.model()
        for range_ in ranges:
            record = self.sameActionInRange(baseRecord, actionTypeId, range_)
            model.addRow(presetAction=CAction(record=record))

    def sameActionInRange(self, baseRecord, actionTypeId, range_):
        model = self.tblAPActions.model()
        record = model.fillNewRecord(actionTypeId)
        begDate, endDate = range_
        copyFields(record, baseRecord,
                   ['directionDate',
                    'setPerson_id',
                    'person_id',
                    'amount'])

        setValues(record,
                  status=ActionStatus.Done,
                  begDate=begDate,
                  endDate=endDate)
        return record

    def checkPossibilityAddingActionType(self, actionTypeId):
        model = self.tblAPActions.model()
        if QtGui.qApp.isHideActionsFromOtherTopOrgStructures():
            if actionTypeId not in model.getActionTypeIdList():
                QtGui.QMessageBox.warning(self,
                                          u'Внимание!',
                                          u'Нельзя добавить услугу, относящуюся к другому верхнему подразделению',
                                          QtGui.QMessageBox.Ok,
                                          QtGui.QMessageBox.Ok)
                return False
        return True

    @QtCore.pyqtSlot()
    def on_actAPActionDup_triggered(self):
        model = self.tblAPActions.model()
        row = self.tblAPActions.currentIndex().row()
        if 0 <= row < model.rowCount() - 1:
            record, action = model._items[row]
            actionTypeId = forceRef(record.value('actionType_id'))
            if not self.checkPossibilityAddingActionType(actionTypeId):
                return
            index = model.index(model.rowCount() - 1, 0)
            if model.setData(index, toVariant(actionTypeId)):
                newRecord, newAction = model._items[index.row()]
                if action:
                    newAction = CAction.clone(action)
                    newAction._record = newRecord
                    model._items[index.row()] = newRecord, newAction
                self.tblAPActions.setCurrentIndex(index)

    @QtCore.pyqtSlot()
    def on_actAPActionsAddToRecs_triggered(self):
        model = self.tblAPActions.model()
        row = self.tblAPActions.currentIndex().row()
        if 0 <= row < model.rowCount() - 1:
            record, action = model._items[row]
            actionTypeId = forceRef(record.value('actionType_id'))
            if hasattr(self.eventEditor, 'tabRecommendations'):
                recsModel = self.eventEditor.tabRecommendations.modelRecommendations
                index = recsModel.index(recsModel.rowCount() - 1,
                                        2)  # TODO: 2 -- номер колонки с типом действия, надо как-то избавиться от этой магической константы
                recsModel.setData(index, toVariant(actionTypeId))
                recsModel.emitDataChanged()

    @QtCore.pyqtSlot()
    def on_actAPActionsAdd_triggered(self):
        model = self.tblAPActions.model()
        if not hasattr(model, 'isEditable') or model.isEditable():
            chkContractByFinanceId = CFinanceType.getCode(self.eventEditor.eventFinanceId) in (CFinanceType.VMI,
                                                                                               CFinanceType.cash)
            existsActionTypesList = [forceRef(rec.value('actionType_id')) for rec, action in
                                     self.modelAPActions.items()]
            typeClasses = self.modelAPActions.actionTypeClass

            actionTypes = selectActionTypes(self.eventEditor,
                                            actionTypeClasses=typeClasses if isinstance(typeClasses, list) else [
                                                typeClasses],
                                            clientSex=self.eventEditor.clientSex,
                                            clientAge=self.eventEditor.clientAge,
                                            orgStructureId=getRealOrgStructureId(),
                                            eventTypeId=self.eventEditor.getEventTypeId(),
                                            contractId=self.eventEditor.getContractId(),
                                            mesId=self.eventEditor.getMesId(),
                                            chkContractByFinanceId=chkContractByFinanceId,
                                            eventId=self.eventEditor.itemId(),
                                            existsActionTypesList=existsActionTypesList,
                                            contractTariffCache=self.eventEditor.contractTariffCache,
                                            notFilteredActionTypesClasses=self.notFilteredActionTypesClasses,
                                            defaultFinanceId=self.defaultFinanceId,
                                            defaultContractFilterPart=self.defaultContractFilterPart,
                                            eventBegDate=self.eventEditor.begDate(),
                                            eventEndDate=self.eventEditor.endDate(),
                                            paymentScheme=self.eventEditor.getPaymentScheme())

            for actionTypeId, action in actionTypes:
                index = model.index(model.rowCount() - 1, 0)
                model.setData(index, toVariant(actionTypeId), presetAction=action)
            self.onActionCurrentChanged()
            self.tblAPActions.selectRow(len(model.items()) - 1)

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtAPDirectionDate_dateChanged(self, date):
        self.edtAPDirectionTime.setEnabled(bool(date))
        time = self.edtAPDirectionTime.time() if date and self.edtAPDirectionTime.isVisible() else QtCore.QTime()
        self.onActionDataChanged('directionDate', QtCore.QDateTime(date, time))
        row = self.tblAPActions.currentIndex().row()
        model = self.tblAPActions.model()
        action = model.items()[row][1]
        if action:
            defaultPlannedEndDate = action.getType().defaultPlannedEndDate
            if defaultPlannedEndDate:
                plannedEndDate = addPeriod(date, 2, defaultPlannedEndDate == 1)
                # self.edtAPPlannedEndDate.setDate(plannedEndDate)

    @QtCore.pyqtSlot(QtCore.QString)
    def on_cmbAPMKB_textChanged(self, value):
        if value[-1:] == '.':
            value = value[:-1]
        diagName = forceString(QtGui.qApp.db.translate('MKB_Tree', 'DiagID', value, 'DiagName'))
        if diagName:
            self.lblAPMKBText.setText(diagName)
        else:
            self.lblAPMKBText.clear()
        self.cmbAPMorphologyMKB.setMKBFilter(self.cmbAPMorphologyMKB.getMKBFilter(unicode(value)))
        self.onActionDataChanged('MKB', value)
        self.cmbActionMes.setMKB(forceStringEx(value))

    @QtCore.pyqtSlot()
    def on_cmbAPMKB_editingFinished(self):
        if not self.eventEditor.checkDiagnosis(self.cmbAPMKB.text()):
            self.cmbAPMKB.setText(self.oldMKB)
            self.cmbAPMKB.setFocus(QtCore.Qt.OtherFocusReason)

    def on_cmbActionMes_editTextChanged(self, text):
        self.onActionDataChanged('MES_id', self.cmbActionMes.value())

    @QtCore.pyqtSlot(QtCore.QString)
    def on_cmbAPMorphologyMKB_textChanged(self, value):
        self.onActionDataChanged('morphologyMKB', value)

    @QtCore.pyqtSlot(QtCore.QTime)
    def on_edtAPDirectionTime_timeChanged(self, time):
        date = self.edtAPDirectionDate.date()
        self.onActionDataChanged('directionDate', QtCore.QDateTime(date, time if date else QtCore.QTime()))

    @QtCore.pyqtSlot(bool)
    def on_chkAPIsUrgent_toggled(self, checked):
        self.onActionDataChanged('isUrgent', checked)

    # @QtCore.pyqtSlot(QtCore.QDate)
    # def on_edtAPPlannedEndDate_dateChanged(self, date):
    #     self.edtAPPlannedEndTime.setEnabled(bool(date))
    #     time = self.edtAPPlannedEndTime.time() if date and self.edtAPPlannedEndTime.isVisible() else QtCore.QTime()
    #     self.onActionDataChanged('plannedEndDate', QtCore.QDateTime(date, time))

    # @QtCore.pyqtSlot(QtCore.QTime)
    # def on_edtAPPlannedEndTime_timeChanged(self, time):
    #     date = self.edtAPPlannedEndDate.date()
    #     self.onActionDataChanged('plannedEndDate', QtCore.QDateTime(date, time if date else QtCore.QTime()))

    @QtCore.pyqtSlot(int)
    def on_cmbAPSetPerson_currentIndexChanged(self, index):
        self.onActionDataChanged('setPerson_id', self.cmbAPSetPerson.value())

    @QtCore.pyqtSlot(int)
    def on_cmbAPOrg_currentIndexChanged(self, index):
        self.onActionDataChanged('org_id', self.cmbAPOrg.value())
        if self.cmbAPOrg.currentIndex() > 0:
            self.cmbAPStatus.setCurrentIndex(10)

    @QtCore.pyqtSlot()
    def on_btnAPSelectOrg_clicked(self):
        orgId = selectOrganisation(self, self.cmbAPOrg.value(), False, self.cmbAPOrg.filter())
        self.cmbAPOrg.update()
        if orgId:
            self.cmbAPOrg.setValue(orgId)

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtAPBegDate_dateChanged(self, date):
        self.edtAPBegTime.setEnabled(bool(date))
        time = self.edtAPBegTime.time() if date and self.edtAPBegTime.isVisible() else QtCore.QTime()
        self.onActionDataChanged('begDate', QtCore.QDateTime(date, time))
        self.updateAmount()
        if not self.edtAPEndDate.date().isNull():
            self.cmbActionMes.setEndDateForTariff(self.edtAPEndDate.date())
        elif not self.edtAPBegDate.date().isNull():
            self.cmbActionMes.setEndDateForTariff(self.edtAPBegDate.date())

    @QtCore.pyqtSlot(QtCore.QTime)
    def on_edtAPBegTime_timeChanged(self, time):
        date = self.edtAPBegDate.date()
        self.onActionDataChanged('begDate', QtCore.QDateTime(date, time if date else QtCore.QTime()))

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtAPEndDate_dateChanged(self, date):
        eventEditor = self.eventEditor
        defaultDirectionDate = self.defaultDirectionDate
        eventSetDate = eventEditor.eventSetDateTime.date() if eventEditor and eventEditor.eventSetDateTime else None
        begDate = eventEditor.eventSetDateTime
        if defaultDirectionDate == CActionType.dddActionExecDate:
            if date.isValid():
                if date < eventSetDate:
                    directionDate = eventSetDate
                    begDate = QtCore.QDate()
                else:
                    directionDate = date
                    begDate = date
            else:
                directionDate = eventSetDate
            self.edtAPBegDate.setDate(begDate)
            self.edtAPDirectionDate.setDate(directionDate)
        else:
            if date and eventSetDate and date < eventSetDate:
                self.edtAPBegDate.setDate(date)
                self.edtAPBegTime.setTime(QtCore.QTime())
                self.edtAPDirectionDate.setDate(date)
                self.edtAPDirectionTime.setTime(QtCore.QTime())
            elif date and eventSetDate and date >= eventSetDate:
                if not self.edtAPDirectionDate.date():
                    self.edtAPDirectionDate.setDate(eventSetDate)
                if not self.edtAPBegDate.date():
                    self.edtAPBegDate.setDate(eventSetDate)
        self.edtAPEndTime.setEnabled(bool(date))
        time = self.edtAPEndTime.time() if date and self.edtAPEndTime.isVisible() else QtCore.QTime()
        self.onActionDataChanged('endDate', QtCore.QDateTime(date, time))
        self.updateAmount()
        if date:
            if self.cmbAPStatus.currentIndex() not in (2, 3, 5, 7, 8, 9, 10, 11):
                self.cmbAPStatus.setCurrentIndex(2)
        else:
            if self.cmbAPStatus.currentIndex() == 2:
                self.cmbAPStatus.setCurrentIndex(3)

        record = self.tblAPActions.model().items()[self.tblAPActions.currentIndex().row()][0]
        if record:
            self.substituteEndDateTimeToEvent(forceRef(record.value('actionType_id')), QtCore.QDateTime(date, time))

        if not self.edtAPEndDate.date().isNull():
            self.cmbActionMes.setEndDateForTariff(self.edtAPEndDate.date())
        elif not self.edtAPBegDate.date().isNull():
            self.cmbActionMes.setEndDateForTariff(self.edtAPBegDate.date())

        if self.edtAPEndDate.date().isNull():
            self.cmbAPStatus.setCurrentIndex(0)
        elif self.cmbAPStatus.currentIndex() == 0:
            self.cmbAPStatus.setCurrentIndex(3)  # 2)

    @QtCore.pyqtSlot(QtCore.QTime)
    def on_edtAPEndTime_timeChanged(self, time):
        date = self.edtAPEndDate.date()
        self.onActionDataChanged('endDate', QtCore.QDateTime(date, time if date else QtCore.QTime()))

        record = self.tblAPActions.model().items()[self.tblAPActions.currentIndex().row()][0]
        if record:
            self.substituteEndDateTimeToEvent(forceRef(record.value('actionType_id')), QtCore.QDateTime(date, time))

    @QtCore.pyqtSlot(int)
    def on_cmbAPStatus_currentIndexChanged(self, index):
        self.onActionDataChanged('status', index)
        if index in [2, 4, 7, 8, 9, 10, 11]:
            if not self.edtAPEndDate.date():
                now = QtCore.QDateTime.currentDateTime()
                self.edtAPEndDate.setDate(now.date())
                if self.edtAPEndTime.isVisible():
                    self.edtAPEndTime.setTime(now.time())
        elif index in [3]:
            eventPurposeId = self.eventEditor.getEventPurposeId()
            if not forceBool(QtGui.qApp.db.translate('rbEventTypePurpose', 'id', eventPurposeId, 'federalCode = 8')):
                if QtGui.qApp.userId and QtGui.qApp.userSpecialityId:
                    self.cmbAPPerson.setValue(QtGui.qApp.userId)
                else:
                    self.cmbAPPerson.setValue(self.cmbAPSetPerson.value())
        elif index in [1, 5, 6]:
            pass
        else:
            self.edtAPEndDate.setDate(QtCore.QDate())

    @QtCore.pyqtSlot(int)
    def on_edtAPPeriodicity_valueChanged(self, value):
        self.onActionDataChanged('periodicity', value)

    @QtCore.pyqtSlot(int)
    def on_edtAPAliquoticity_valueChanged(self, value):
        self.onActionDataChanged('aliquoticity', value)

    @QtCore.pyqtSlot(float)
    def on_edtAPAmount_valueChanged(self, value):
        self.onActionDataChanged('amount', value)
        row = self.tblAPActions.currentIndex().row()
        model = self.modelAPActions
        model.emitAmountChanged(row)

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtAPOffice_textChanged(self, text):
        self.onActionDataChanged('office', text)

    @QtCore.pyqtSlot(int)
    def on_cmbAPPerson_currentIndexChanged(self, index):
        self.onActionDataChanged('person_id', self.cmbAPPerson.value())

    @QtCore.pyqtSlot(int)
    def on_cmbAPAssistant_currentIndexChanged(self, index):
        row = self.tblAPActions.currentIndex().row()
        items = self.tblAPActions.model().items()
        if row in xrange(len(items)):
            action = items[row][1]
            action.setAssistant('assistant', self.cmbAPAssistant.value())
            self.onActionDataChanged('assistant_id', self.cmbAPAssistant.value())

    @QtCore.pyqtSlot(int)
    def on_cmbAPAssistant2_currentIndexChanged(self, index):
        row = self.tblAPActions.currentIndex().row()
        items = self.tblAPActions.model().items()
        if row in xrange(len(items)):
            action = items[row][1]
            action.setAssistant('assistant2', self.cmbAPAssistant2.value())
            self.onActionDataChanged('assistant2_id', self.cmbAPAssistant2.value())

    @QtCore.pyqtSlot(int)
    def on_cmbAPAssistant3_currentIndexChanged(self, index):
        row = self.tblAPActions.currentIndex().row()
        items = self.tblAPActions.model().items()
        if row in xrange(len(items)):
            action = items[row][1]
            action.setAssistant('assistant3', self.cmbAPAssistant3.value())
            self.onActionDataChanged('assistant3_id', self.cmbAPAssistant3.value())

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtAPNote_textChanged(self, text):
        self.onActionDataChanged('note', text)

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_modelAPActionProperties_dataChanged(self, topLeft, bottomRight):
        self.updateAmount()
        model = self.tblAPActions.model()
        items = model.items()
        row = self.tblAPActions.currentIndex().row()
        record, action = items[row]
        actionTypeId = forceRef(record.value('actionType_id')) if record else None
        actionType = CActionTypeCache.getById(actionTypeId) if actionTypeId else None
        if u'moving' in actionType.flatCode.lower():
            if action[u'Переведен в отделение']:
                self.btnNextAction.setText(u'Движение')
                self.btnNextAction.setVisible(
                    not self.edtAPEndDate.date() or bool(QtGui.qApp.userId and not QtGui.qApp.userSpecialityId))
            self.gBoxSupportService.setVisible(True)
        elif u'received' in actionType.flatCode.lower():
            if action[u'Направлен в отделение']:
                self.btnNextAction.setText(u'Движение')
                self.btnNextAction.setVisible(
                    not self.edtAPEndDate.date() or bool(QtGui.qApp.userId and not QtGui.qApp.userSpecialityId))
            else:
                self.btnNextAction.setText(u'Выписка')
                self.btnNextAction.setVisible(True)
        elif (u'inspectPigeonHole'.lower() in actionType.flatCode.lower()
              or u'reanimation' in actionType.flatCode.lower()
              or u'maternityward' in actionType.flatCode.lower()
              ):
            self.btnNextAction.setText(u'Закончить')
            self.btnNextAction.setVisible(not self.edtAPEndDate.date())
        else:
            self.gBoxSupportService.setVisible(False)
        if u'planning' in actionType.flatCode.lower():
            from library.vm_collections import OrderedDict
            row = topLeft.row()
            propType = self.modelAPActionProperties._rowDataList[row]
            if propType.name == u'подразделение':
                prop = action.getPropertyById(propType.id)
                org_struct_id = prop.getValue()
                db = QtGui.qApp.db
                org_struct_limit = forceInt(db.translate('OrgStructure', 'id', org_struct_id, 'dayLimit'))
                if org_struct_limit < 1:
                    return
                # plannedDate = self.edtAPPlannedEndDate.date()
                stmt = """SELECT
                        DATE(a.plannedEndDate) as plannedEndDate,
                        COUNT(plannedEndDate) as count
                        FROM Action a
                        INNER JOIN ActionType at ON at.id = a.actionType_id AND at.flatCode = 'planning'
                        INNER JOIN ActionProperty ap ON ap.action_id = a.id
                        INNER JOIN ActionProperty_OrgStructure apos ON apos.id = ap.id AND apos.value = %s
                        WHERE plannedEndDate >= DATE(NOW())
                        AND a.deleted = 0
                        AND at.deleted = 0
                        AND ap.deleted = 0
                        GROUP BY plannedEndDate
                        ORDER BY plannedEndDate
                        """ % org_struct_id
                query = db.query(stmt)
                busyDates = OrderedDict()
                while query.next():
                    record = query.record()
                    plDate = forceDate(record.value('plannedEndDate'))
                    count = forceInt(record.value('count'))
                    busyDates[plDate] = count
                hiddenDates = []
                for date, limit in busyDates.items():
                    if limit >= org_struct_limit:
                        hiddenDates.append(date)
                        # self.edtAPPlannedEndDate.setHiddenDates(hiddenDates)
                        # if forceString(plannedDate):
                        #     if plannedDate in hiddenDates:
                        #         nextdate = QtCore.QDate.currentDate()
                        #         while nextdate in hiddenDates:
                        #             nextdate = nextdate.addDays(1)
                        #         nextdate = forceString(nextdate)
                        #         QtGui.QMessageBox.information(self,
                        #                                       u'Внимание',
                        #                                       u'На текущую дату запись закрыта. Ближайшая свободная дата: %s' % nextdate)

    @QtCore.pyqtSlot(int)
    def on_btnAPPrint_printByTemplate(self, templateId):
        if self.eventEditor.isDirty() and forceInt(
                QtGui.qApp.db.translate('rbPrintTemplate', 'id', templateId, 'banUnkeptDate')) == 2:
            if QtGui.QMessageBox.question(self,
                                          u'Внимание!',
                                          u'Для печати данного шаблона необходимо сохранить обращение.\nСохранить сейчас?',
                                          QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                          QtGui.QMessageBox.No) != QtGui.QMessageBox.Yes:
                return
            if not self.eventEditor.saveData():
                return
        model = self.tblAPActions.model()
        items = model.items()
        row = self.tblAPActions.currentIndex().row()
        if 0 <= row < len(items):
            data = getEventContextData(self.eventEditor)
            eventInfo = data['event']
            # FIXME: atronah: CActionInfoList (eventInfo.actions) не имеет атрибута _rawItems
            currentActionIndex = eventInfo.actions._rawItems.index(items[row])
            action = eventInfo.actions[currentActionIndex]
            action.setCurrentPropertyIndex(self.tblAPProps.currentIndex().row())
            data['action'] = action
            data['actions'] = eventInfo.actions
            data['currentActionIndex'] = currentActionIndex
            applyTemplate(self.eventEditor, templateId, data)

    def on_tblAPActions_printByTemplateList(self, list):
        """list: list of tuple(templateId, row, dateTime)"""
        for templateId, rows, dateTime in list:
            if self.eventEditor.isDirty() and forceInt(
                    QtGui.qApp.db.translate('rbPrintTemplate', 'id', templateId, 'banUnkeptDate')) == 2:
                if QtGui.QMessageBox.question(self,
                                              u'Внимание!',
                                              u'Для печати данного шаблона необходимо сохранить обращение.\nСохранить сейчас?',
                                              QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                              QtGui.QMessageBox.No) != QtGui.QMessageBox.Yes:
                    return
                if not self.eventEditor.saveData():
                    return
        model = self.tblAPActions.model()
        items = model.items()
        templateList = []
        dataList = []
        for templateId, row, dateTime in list:
            if 0 <= row < len(items):
                data = getEventContextData(self.eventEditor)
                eventInfo = data['event']
                # FIXME: atronah: CActionInfoList (eventInfo.actions) не имеет атрибута _rawItems
                currentActionIndex = eventInfo.actions._rawItems.index(items[row])
                action = eventInfo.actions[currentActionIndex]
                action.setCurrentPropertyIndex(self.tblAPProps.currentIndex().row())
                data['action'] = action
                data['actions'] = eventInfo.actions
                data['currentActionIndex'] = currentActionIndex
                templateList.append(templateId)
                dataList.append(data)
        applyMultiTemplateList(self.eventEditor, templateList, dataList)

    @QtCore.pyqtSlot(int)
    def on_btnAPLoadTemplate_templateSelected(self, templateId):
        model = self.tblAPActions.model()
        items = model.items()
        row = self.tblAPActions.currentIndex().row()
        if QtGui.qApp.userHasRight(urLoadActionTemplate) and 0 <= row < len(items):
            action = items[row][1]
            action.updateByTemplate(templateId)
            self.tblAPProps.model().reset()
            self.tblAPProps.init()
            self.tblAPProps.resizeRowsToContents()
            model.updateActionAmount(row)

    @QtCore.pyqtSlot()
    def on_btnAPSaveAsTemplate_clicked(self):
        model = self.tblAPActions.model()
        items = model.items()
        row = self.tblAPActions.currentIndex().row()
        if QtGui.qApp.userHasRight(urSaveActionTemplate) and 0 <= row < len(items):
            actionRecord, action = items[row]
            # model = self.actionTemplateCache.getModel(action.getType().id, forceRef(action.getRecord().value('setPerson_id')))
            # dlg = CActionTemplateSaveDialog(self, actionRecord, action, self.eventEditor.clientSex, self.eventEditor.clientAge, self.eventEditor.personId, self.eventEditor.personSpecialityId, model=model)
            dlg = CActionTemplateSaveDialog(self, actionRecord, action, self.eventEditor.clientSex,
                                            self.eventEditor.clientAge, self.eventEditor.personId,
                                            self.eventEditor.personSpecialityId)
            dlg.exec_()
            self.actionTemplateCache.reset(action.getType().id)
            personId = forceRef(action.getRecord().value('person_id'))
            actionTemplateTreeModel = self.actionTemplateCache.getModel(action.getType().id,
                                                                        personId if personId else forceRef(
                                                                            action.getRecord().value('setPerson_id')))
            self.btnAPLoadTemplate.setModel(actionTemplateTreeModel)

    @QtCore.pyqtSlot()
    def on_mnuAPLoadPrevAction_aboutToShow(self):
        model = self.tblAPActions.model()
        items = model.items()
        row = self.tblAPActions.currentIndex().row()
        if 0 <= row < len(items):
            record, action = items[row]
        else:
            action = None
        self.actAPLoadAnyonesPrevAction.setEnabled(bool(action and self.eventEditor.getPrevActionId(action, 2)))
        self.actAPLoadSameSpecialityPrevAction.setEnabled(bool(action and self.eventEditor.getPrevActionId(action, 1)))
        self.actAPLoadOwnPrevAction.setEnabled(bool(action and self.eventEditor.getPrevActionId(action, 0)))

    @QtCore.pyqtSlot()
    def on_actAPLoadAnyonesPrevAction_triggered(self):
        self.loadPrevAction(2)

    @QtCore.pyqtSlot()
    def on_actAPLoadSameSpecialityPrevAction_triggered(self):
        self.loadPrevAction(1)

    @QtCore.pyqtSlot()
    def on_actAPLoadOwnPrevAction_triggered(self):
        self.loadPrevAction(0)

    @QtCore.pyqtSlot(bool)
    def on_btnToggleAttrsAP_toggled(self, state):
        setPref(QtGui.qApp.preferences.windowPrefs, '{0}_attrs_collapsed'.format(self.objectName()), state)

    def substituteEndDateTimeToEvent(self, actionTypeId, endDateTime):
        actionType = CActionTypeCache.getById(actionTypeId) if actionTypeId else None
        if actionType and actionType.isSubstituteEndDateToEvent and self.eventEditor:
            if hasattr(self.eventEditor, 'edtEndDate'):
                self.eventEditor.edtEndDate.setDate(endDateTime.date())
            if hasattr(self.eventEditor, 'edtEndTime') and getEventShowTime(self.eventEditor.eventTypeId):
                self.eventEditor.edtEndTime.setTime(endDateTime.time())


class CActionsPage(CFastActionsPage):
    def __init__(self, parent=None):
        CFastActionsPage.__init__(self, parent)
        self.preSetupUiMini()
        self.preSetupUi()
        #        self.setupUiMini(self)
        self.setupUi(self)
        #        self.postSetupUiMini()
        self.postSetupUi()
