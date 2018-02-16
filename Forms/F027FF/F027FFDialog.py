# -*- coding: utf-8 -*-

# Форма 027_financeFragment: форма ввода "Протокол"

from PyQt4 import QtCore, QtGui, QtSql

from Accounting.Utils import isEventPresenceInAccounts
from Events.Action import ActionStatus, CAction
from Events.ActionEditDialog import CActionEditDialog
from Events.ActionInfo import CCookedActionInfo
from Events.ActionPropertiesTable import CActionPropertiesTableModel
from Events.ActionsSummaryModel import CFxxxActionsSummaryModel
from Events.DiagnosisType import CDiagnosisTypeCol
from Events.EventEditDialog import CDiseaseCharacter, CDiseasePhases, CDiseaseStage, CEventEditDialog
from Events.EventInfo import CDiagnosticInfoProxyList, CEventInfo
from Events.Utils import CTableSummaryActionsMenuMixin, checkDiagnosis, checkIsHandleDiagnosisIsChecked, \
    getAvailableCharacterIdByMKB, getDiagnosisId2, getDiagnosisSetDateVisible, getEventContextData, getEventDuration, \
    getEventLengthDays, getEventShowTime, \
    setActionPropertiesColumnVisible, setAskedClassValueForDiagnosisManualSwitch, setOrgStructureIdToCmbPerson
from Forms.F025.PreF025Dialog import CPreF025DagnosticAndActionPresets, CPreF025Dialog
from Forms.F027.F027Dialog import CProtocolEventEditDialog
from Forms.Utils import check_data_text_TNM
from Orgs.OrgComboBox import CPolyclinicComboBox
from Orgs.Orgs import selectOrganisation
from Orgs.Utils import getPersonChiefs
from Ui_F027FF import Ui_Dialog
from Users.Rights import urAccessF025planner, urAdmin, urDoNotCheckResultAndMKB, urEditF027IfHospitalizationEventExists, \
    urEditOtherPeopleAction, urEditPayedEvents, urOncoDiagnosisWithoutTNMS, urRegTabWriteRegistry
from library.ICDInDocTableCol import CICDExInDocTableCol
from library.ICDMorphologyInDocTableCol import CMKBMorphologyCol
from library.InDocTable import CActionPersonInDocTableColSearch, CBoolInDocTableCol, CDateInDocTableCol, \
    CInDocTableModel, CRBInDocTableCol
from library.PrintInfo import CInfoContext, CInfoProxyList
from library.PrintTemplates import applyTemplate, customizePrintButton, getPrintButton
from library.TNMS.TNMSComboBox import CTNMSCol
from library.Utils import copyFields, forceBool, forceDate, forceInt, forceRef, forceString, forceTr, formatNum, \
    getActionTypeIdListByFlatCode, toVariant, variantEq
from library.crbcombobox import CRBComboBox
from library.interchange import getDatetimeEditValue, getRBComboBoxValue, setDatetimeEditValue, setRBComboBoxValue


class CF027FFDialog(CProtocolEventEditDialog, Ui_Dialog, CTableSummaryActionsMenuMixin):
    addActPrintEventCost = False

    def __init__(self, parent):
        CProtocolEventEditDialog.__init__(self, parent)
        self.mapSpecialityIdToDiagFilter = {}
        self.notSetCmbResult = False
        self.setObsoleteCureMethod = False

        self.addModels('PreliminaryDiagnostics', CF003PreliminaryDiagnosticsModel(self))
        self.addModels('FinalDiagnostics', CF003FinalDiagnosticsModel(self))
        self.addModels('ActionsSummary', CFxxxActionsSummaryModel(self))
        self.addModels('APActionProperties', CActionPropertiesTableModel(self))

        self.createSaveAndCreateAccountButton()
        self.actEditClient = QtGui.QAction(u'Изменить описание клиента', self)
        self.actEditClient.setObjectName('actEditClient')
        self.btnPrint = getPrintButton(self, '')
        self.btnPrint.setObjectName('btnPrint')
        self.setupUi(self)

        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Осмотр Ф.027ФФ')
        self.tabToken.setFocusProxy(self.tblFinalDiagnostics)
        self.buttonBox.addButton(self.btnPrint, QtGui.QDialogButtonBox.ActionRole)
        self.setupSaveAndCreateAccountButton()
        self.setupSaveAndCreateAccountForPeriodButton()
        self.setupActionSummarySlots()

        self.tblPreliminaryDiagnostics.setModel(self.modelPreliminaryDiagnostics)
        self.tblFinalDiagnostics.setModel(self.modelFinalDiagnostics)
        self.tblActionProperties.setModel(self.modelAPActionProperties)

        self.markEditableTableWidget(self.tblPreliminaryDiagnostics)
        self.markEditableTableWidget(self.tblFinalDiagnostics)

        self.tblPreliminaryDiagnostics.addCopyDiagnos2Final(self)
        self.txtClientInfoBrowser.actions.append(self.actEditClient)
        self.actEditClient.setEnabled(QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteRegistry]))

        db = QtGui.qApp.db
        self.setupDirtyCather()
        self.setIsDirty(False)
        self.blankMovingIdList = []
        self.clientId = None
        self.prolongateEvent = False
        self.prevEventId = None
        self.cmbCureType.setTable('rbCureType')
        self.cmbCureMethod.setTable('rbCureMethod')
        self.cmbCureType.setFilter('rbCureType.isObsolete = 0')
        self.cmbCureMethod.setFilter('rbCureMethod.isObsolete = 0')

        ids = db.getIdList('rbPost', where="code IN ('2005', '1001', '2006')")
        order = "FIELD(code, " + ', '.join("'%d'" % i for i in ids) + ") DESC"
        self.cmbPerson.setOrder(order)
        self.cmbPersonManager.setOrder(order)
        self.cmbPersonMedicineHead.setOrder(order)
        self.cmbEventCurator.setOrder(order)
        self.cmbEventAssistant.setOrder(order)
        self.cmbQuota.setTable('QuotaType')

        self.cmbPatientModel.setEventEditor(self)
        self.valueForAllActionEndDate = None
        self.cmbResult.setShowFields(CRBComboBox.showCodeAndName)

        self.edtBegDate.setEnabled(QtGui.qApp.userHasRight(urAdmin))
        self.edtBegTime.setEnabled(QtGui.qApp.userHasRight(urAdmin))

        self.edtEndDate.setEnabled(QtGui.qApp.userHasRight(urAdmin))
        self.edtEndTime.setEnabled(QtGui.qApp.userHasRight(urAdmin))

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

    def getEditable(self):
        db = QtGui.qApp.db
        Event = db.table('Event')
        EventType = db.table('EventType')
        queryTable = Event.leftJoin(EventType, EventType['id'].eq(Event['eventType_id']))
        cond = [
            Event['deleted'].eq(0),
            Event['client_id'].eq(self.clientId),
            Event['setDate'].gt(self.getExecDateTime()),
            EventType['code'].eq('03')  # код Типа События "Госпитализация" в НИИ Петрова
        ]
        hospitalizationEventAfterThisEvent = db.getRecordEx(queryTable, Event['id'], cond)
        editable = hospitalizationEventAfterThisEvent is None or \
                   QtGui.qApp.userHasRight(urEditF027IfHospitalizationEventExists)
        if self._isCheckPresenceInAccounts:
            editable = editable and not isEventPresenceInAccounts(
                forceRef(self._record.value('id'))) or QtGui.qApp.userHasRight(urEditPayedEvents)
        return editable

    def setEditable(self, editable):
        self.grpBase.setEnabled(editable)
        self.grpActions.setEnabled(editable)
        self.modelPreliminaryDiagnostics.setEditable(editable)
        self.modelFinalDiagnostics.setEditable(editable)
        self.grpInspections.setEnabled(editable)
        self.grpInspections_2.setEnabled(editable)

        self.tabAmbCard.setEnabled(editable)
        self.tabNotes.setEnabled(editable)

    def openMainActionInRedactor(self):
        oldAction = self.modelAPActionProperties.action
        if oldAction:
            oldRecord = oldAction.getRecord()

            dialog = CActionEditDialog(self)

            dialog.save = lambda: True

            dialog.setForceClientId(self.clientId)

            dialog.setRecord(QtSql.QSqlRecord(oldRecord))

            dialog.setReduced(True)

            CAction.copyAction(oldAction, dialog.action)

            if dialog.exec_():
                self.modelAPActionProperties.action = dialog.action
                self.modelAPActionProperties.emitDataChanged()

                record = dialog.getRecord()

                setDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'begDate')
                setDatetimeEditValue(self.edtEndDate, self.edtEndTime, record, 'endDate')
                self.cmbPersonManager.setValue(forceRef(record.value('person_id')))
                self.cmbPersonMedicineHead.setValue(forceRef(record.value('setPerson_id')))

    def keyPressEvent(self, event):
        key = event.key()
        if hasattr(self, 'tabWidget'):
            widget = self.tabWidget.currentWidget()
            cond = []
            if hasattr(self, 'tabToken'):
                cond.append(self.tabToken)
            if widget in cond:
                if key == QtCore.Qt.Key_F2:
                    self.openMainActionInRedactor()
        CProtocolEventEditDialog.keyPressEvent(self, event)

    def updatePropTable(self, action):
        self.tblActionProperties.model().setAction(action, self.clientId, self.clientSex, self.clientAge)
        self.tblActionProperties.resizeRowsToContents()

    def createAction(self):
        eventId = self.itemId()
        action = None
        if self.clientId:
            db = QtGui.qApp.db
            tableAction = db.table('Action')
            record = None
            actionTypeIdList = getActionTypeIdListByFlatCode(u'protocol')
            if eventId:
                actionTypeId = actionTypeIdList[0] if len(actionTypeIdList) else None
                cond = [tableAction['deleted'].eq(0),
                        tableAction['event_id'].eq(eventId),
                        tableAction['actionType_id'].eq(actionTypeId)
                        ]
                record = db.getRecordEx(tableAction, '*', cond)
                if record:
                    action = CAction(record=record)
                    setDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'begDate')
                    setDatetimeEditValue(self.edtEndDate, self.edtEndTime, record, 'endDate')
                    self.cmbPersonManager.setValue(forceRef(record.value('person_id')))
                    self.cmbPersonMedicineHead.setValue(forceRef(record.value('setPerson_id')))
                    # self.cmbPersonExpert.setValue(forceRef(record.value('assistant_id')))
            if not record:
                actionTypeId = actionTypeIdList[0] if len(actionTypeIdList) else None
                if actionTypeId:
                    record = tableAction.newRecord()
                    record.setValue('event_id', toVariant(eventId))
                    record.setValue('actionType_id', toVariant(actionTypeId))
                    record.setValue('begDate',
                                    toVariant(QtCore.QDateTime(self.edtBegDate.date(), self.edtBegTime.time())))
                    record.setValue('endDate',
                                    toVariant(QtCore.QDateTime(self.edtEndDate.date(), self.edtEndTime.time())))
                    record.setValue('status', toVariant(2))
                    record.setValue('person_id', toVariant(self.cmbPersonManager.value()))
                    record.setValue('setPerson_id', toVariant(self.cmbPersonMedicineHead.value()))
                    # record.setValue('assistant_id', toVariant(self.cmbPersonExpert.value()))
                    record.setValue('org_id', toVariant(QtGui.qApp.currentOrgId()))
                    record.setValue('amount', toVariant(1))
                    action = CAction(record=record)

            if action:
                # action.setAssistant('assistant', self.cmbPersonExpert.value())
                status = forceInt(record.value('status'))
                personManagerId = self.cmbPersonManager.value()
                personId = self.cmbPerson.value()
                personMedicineHeadId = self.cmbPersonMedicineHead.value()
                eventCuratorId = self.cmbEventCurator.value()
                # personExpertId = self.cmbPersonExpert.value()
                eventAssistantId = self.cmbEventAssistant.value()
                if status == ActionStatus.Done and (
                                personId or personManagerId or personMedicineHeadId or eventCuratorId or eventAssistantId):  # or personExpertId:
                    action._locked = not (QtGui.qApp.userId == personId
                                          or QtGui.qApp.userId == personManagerId
                                          or QtGui.qApp.userId == personMedicineHeadId
                                          or QtGui.qApp.userId == eventCuratorId
                                          # or QtGui.qApp.userId == personExpertId
                                          or QtGui.qApp.userId == eventAssistantId
                                          or QtGui.qApp.userHasRight(urEditOtherPeopleAction)
                                          or QtGui.qApp.userId in getPersonChiefs(personId)
                                          )
                else:
                    self._locked = False
                setActionPropertiesColumnVisible(action._actionType, self.tblActionProperties)
                self.updatePropTable(action)
                canEdit = not action.isLocked() if action else True
                self.tblActionProperties.setEnabled(canEdit)
        return action

    def _prepare(self, contractId, clientId, eventTypeId, orgId, personId, eventSetDatetime, eventDatetime,
                 includeRedDays, numDays,
                 presetDiagnostics, presetActions, disabledActions, externalId, assistantId, curatorId,
                 actionTypeIdValue=None, valueProperties=None, relegateOrgId=None, diagnos=None, financeId=None,
                 protocolQuoteId=None, actionByNewEvent=None, referrals=None, isAmb=True, recommendationList=None,
                 orgStructureId=None):
        db = QtGui.qApp.db

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
        self.setEventTypeId(eventTypeId)
        self.setClientId(clientId)
        self.clientId = clientId
        self.prolongateEvent = True if actionByNewEvent else False
        self.cmbRelegateOrg.setValue(relegateOrgId)
        try:
            self.cmbEventExternalIdValue.setCurrentIndex([u'КС', u'ДС'].index(externalId))
        except ValueError:
            pass
        # self.cmbEventAssistant.setValue(assistantId)
        self.cmbEventCurator.setValue(curatorId)
        self.setExternalId(externalId)
        self.cmbPerson.setValue(personId)
        # self.tabReferral.cmbPerson.setValue(personId)

        head = db.getRecordEx(
            stmt='SELECT p.id AS id FROM Person p INNER JOIN rbPost rbp ON p.post_id = rbp.id WHERE rbp.code = \'2005\' LIMIT 0, 1')
        if head:
            self.cmbPersonMedicineHead.setValue(forceRef(head.value('id')))
        assistant = db.getRecordEx(
            stmt='SELECT p.id AS id FROM Person p INNER JOIN rbPost rbp ON p.post_id = rbp.id WHERE rbp.code = \'2006\' LIMIT 0, 1')
        if assistant:
            self.cmbEventAssistant.setValue(forceRef(assistant.value('id')))
        self.chkPrimary.setChecked(self.setPrimacy())

        self.cmbOrder.setCode(1)
        self.createAction()
        self.initFocus()
        self.setContract()
        self.setRecommendations(recommendationList)

        self.updateModelsRetiredList()

        if presetDiagnostics:
            for model in [self.modelPreliminaryDiagnostics, self.modelFinalDiagnostics]:
                for MKB, dispanserId, healthGroupId, medicalGroup, visitTypeId, goalId, serviceId in presetDiagnostics:
                    item = model.getEmptyRecord()
                    item.setValue('MKB', toVariant(MKB))
                    item.setValue('dispanser_id', toVariant(dispanserId))
                    item.setValue('healthGroup_id', toVariant(healthGroupId))
                    model.items().append(item)
                model.reset()
        # self.prepareActions(presetActions, disabledActions, actionTypeIdValue, valueProperties, diagnos, financeId, protocolQuoteId, actionByNewEvent)
        self.setIsDirty(False)
        self.cmbPatientModel.setEventEditor(self)
        self.notSetCmbResult = True
        self.cmbQuota.setValue(self.getQuotaTypeIdFromAction())

        self.tabNotes.updateClientPolicy(None)

        return True

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
        self.setPersonId(personId)
        self.setContract()
        plannerDate = self.getPlannerDate(eventSetDatetime, eventDatetime)
        if QtGui.qApp.userHasRight(urAccessF025planner):
            dlg = CPreF025Dialog(self)
            dlg.prepare(clientId, eventTypeId, plannerDate, self.personId, self.personSpecialityId,
                        self.personTariffCategoryId, flagHospitalization, actionTypeIdValue, tissueTypeId,
                        recommendationList, useDiagnosticsAndActionsPresets=useDiagnosticsAndActionsPresets)
            if dlg.diagnosticsTableIsNotEmpty() or dlg.actionsTableIsNotEmpty():
                if not dlg.exec_():
                    return False
            return self._prepare(None, clientId, eventTypeId, orgId, personId, eventSetDatetime, eventDatetime,
                                 includeRedDays, numDays, dlg.diagnostics(), dlg.actions(),
                                 dlg.disabledActionTypeIdList, externalId, assistantId, curatorId, actionTypeIdValue,
                                 valueProperties, relegateOrgId, diagnos, financeId, protocolQuoteId, actionByNewEvent,
                                 isAmb=isAmb, recommendationList=recommendationList)
        else:
            presets = CPreF025DagnosticAndActionPresets(clientId, eventTypeId, plannerDate, self.personSpecialityId,
                                                        flagHospitalization, actionTypeIdValue, recommendationList,
                                                        useDiagnosticsAndActionsPresets=useDiagnosticsAndActionsPresets)
            return self._prepare(None, clientId, eventTypeId, orgId, personId, eventSetDatetime, eventDatetime,
                                 includeRedDays, numDays,
                                 presets.unconditionalDiagnosticList, presets.unconditionalActionList,
                                 presets.disabledActionTypeIdList,
                                 externalId, assistantId, curatorId, None, [], relegateOrgId, diagnos, financeId,
                                 protocolQuoteId, actionByNewEvent, isAmb=isAmb, recommendationList=recommendationList,
                                 orgStructureId=orgStructureId)

    def getQuotaTypeId(self):
        return self.cmbQuota.value()

    def getQuotaTypeIdFromAction(self):
        quotaTypeId = None
        action = self.tblActionProperties.model().action
        if action:
            quotaTypeId = action[u'Квота']
        return quotaTypeId

    def setQuotaTypeIdFromAction(self):
        action = self.tblActionProperties.model().action
        if action:
            action[u'Квота'] = self.cmbQuota.value()

    def createDiagnostics(self, eventId):
        if eventId:
            self.loadDiagnostics(self.modelPreliminaryDiagnostics, eventId)
            self.loadDiagnostics(self.modelFinalDiagnostics, eventId)

    def prepareActions(self, presetActions, disabledActions, actionTypeIdValue, valueProperties, diagnos, financeId,
                       protocolQuoteId, actionByNewEvent):
        if presetActions:
            db = QtGui.qApp.db
            tableActionType = db.table('ActionType')
            tableEventType = db.table('EventType')
            idListActionType = db.getIdList(tableActionType, [tableActionType['id']],
                                            [tableActionType['flatCode'].like(u'received%'),
                                             tableActionType['deleted'].eq(0)])
            idListActionTypeIPH = db.getIdList(tableActionType, [tableActionType['id']],
                                               [tableActionType['flatCode'].like(u'inspectPigeonHole%'),
                                                tableActionType['deleted'].eq(0)])
            idListActionTypeMoving = db.getIdList(tableActionType, [tableActionType['id']],
                                                  [tableActionType['flatCode'].like(u'moving%'),
                                                   tableActionType['deleted'].eq(0)])
            eventTypeId = self.getEventTypeId()
            actionFinance = None
            if eventTypeId:
                recordET = db.getRecordEx(tableEventType, [tableEventType['actionFinance']],
                                          [tableEventType['deleted'].eq(0), tableEventType['id'].eq(eventTypeId)])
                actionFinance = forceInt(recordET.value('actionFinance')) if recordET else None
            if actionByNewEvent:
                actionTypeMoving = False
                for actionTypeId, amount, cash, _ in presetActions:
                    if actionTypeId in idListActionTypeMoving:
                        actionTypeMoving = True
                        break
                if not actionTypeMoving and idListActionTypeMoving:
                    presetActions.append((idListActionTypeMoving[0], 1.0, False, None))

    def setLeavedAction(self, actionTypeIdValue):
        pass

    def initFocus(self):
        self.tblFinalDiagnostics.setFocus(QtCore.Qt.OtherFocusReason)

    def newDiagnosticRecord(self, template):
        result = self.tblFinalDiagnostics.model().getEmptyRecord()
        return result

    def setRecord(self, record):
        db = QtGui.qApp.db
        self.cmbResult.setTable('rbResult', True)
        CProtocolEventEditDialog.setRecord(self, record)
        setDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'setDate')
        setRBComboBoxValue(self.cmbPerson, record, 'setPerson_id')
        setDatetimeEditValue(self.edtEndDate, self.edtEndTime, record, 'execDate')
        setRBComboBoxValue(self.cmbPerson, record, 'execPerson_id')
        self.chkPrimary.setChecked(forceInt(record.value('isPrimary')) == 1)
        self.setExternalId(forceString(record.value('externalId')))
        # setComboBoxValue(self.cmbOrder,       record, 'order')
        self.cmbOrder.setCode(forceString(record.value('order')))
        setRBComboBoxValue(self.cmbResult, record, 'result_id')

        self.cmbRelegateOrg.setValue(forceRef(record.value('relegateOrg_id')))
        try:
            self.cmbEventExternalIdValue.setCurrentIndex([u'КС', u'ДС'].index(forceString(record.value('externalId'))))
        except ValueError:
            pass
        setRBComboBoxValue(self.cmbEventAssistant, record, 'assistant_id')
        setRBComboBoxValue(self.cmbEventCurator, record, 'curator_id')
        setRBComboBoxValue(self.cmbPatientModel, record, 'patientModel_id')
        self.on_cmbPatientModel_currentIndexChanged(None)
        setRBComboBoxValue(self.cmbCureType, record, 'cureType_id')
        setRBComboBoxValue(self.cmbCureMethod, record, 'cureMethod_id')
        self.prevEventId = forceRef(record.value('prevEvent_id'))
        if self.prevEventId:
            self.lblProlongateEvent.setText(u'п')
            tableEvent = db.table('Event')
            tableEventType = db.table('EventType')
            prevEventRecord = db.getRecordEx(
                tableEvent.innerJoin(tableEventType, tableEvent['eventType_id'].eq((tableEventType['id']))),
                [tableEventType['name'], tableEvent['setDate']],
                [tableEvent['deleted'].eq(0), tableEvent['id'].eq(self.prevEventId)])
            if prevEventRecord:
                self.tabNotes.edtPrevEventInfo.setText(u'Продолжение обращения: %s от %s.' % (
                forceString(prevEventRecord.value('name')),
                forceDate(prevEventRecord.value('setDate')).toString('dd.MM.yyyy')))

        self.setPersonId(self.cmbPerson.value())
        self.setContract()
        self.loadDiagnostics(self.modelPreliminaryDiagnostics, self.itemId())
        self.loadDiagnostics(self.modelFinalDiagnostics, self.itemId())
        self.updateResultFilter()
        self.loadActions()
        self.tabNotes.setNotes(record)
        # self.tabReferral.setRecord(record)
        self.cmbPatientModel.setEventEditor(self)
        self.createAction()

        # Если модель пациента устарела, то запрещаем изменение типа и метода лечения
        if self.cmbPatientModel.isObsolete:
            self.cmbCureType.showPopup = lambda: None
            self.cmbCureMethod.showPopup = lambda: None

            cureTypeId = forceRef(self.cmbCureType.value())
            cureTypeFilter = 'id = %d' % cureTypeId if cureTypeId else '0'
            self.cmbCureType.setTable('rbCureType', addNone=not cureTypeId, filter=cureTypeFilter)
            self.cmbCureType.setValue(cureTypeId)

            cureMethodId = forceRef(self.cmbCureMethod.value())
            cureMethodFilter = 'id = %d' % cureMethodId if cureMethodId else '0'
            self.cmbCureMethod.setTable('rbCureMethod', addNone=not cureMethodId, filter=cureMethodFilter)
            self.cmbCureMethod.setValue(cureMethodId)

            self.cmbCureType.setEditable(True)
            self.cmbCureType.lineEdit().setReadOnly(True)
            self.cmbCureMethod.setEditable(True)
            self.cmbCureMethod.lineEdit().setReadOnly(True)

        self.initFocus()
        self.setIsDirty(False)
        self.blankMovingIdList = []
        self.notSetCmbResult = (False if self.cmbResult.value() else True)
        quota = self.getQuotaTypeIdFromAction()
        if quota:
            self.cmbQuota.reloadData()
            self.cmbQuota.setValue(quota)
        setOrgStructureIdToCmbPerson(self.cmbPerson)
        self.setEditable(self.getEditable())

    @QtCore.pyqtSlot(int)
    def on_cmbQuota_currentIndexChanged(self, index):
        self.setQuotaTypeIdFromAction()

    def loadEventDiagnostics(self, modelDiagnostics, eventId):
        db = QtGui.qApp.db
        tableDiagnostic = db.table('Diagnostic')
        tableRBDiagnosisType = db.table('rbDiagnosisType')
        table = tableDiagnostic.innerJoin(tableRBDiagnosisType,
                                          tableRBDiagnosisType['id'].eq(tableDiagnostic['diagnosisType_id']))
        cond = [tableDiagnostic['deleted'].eq(0), tableDiagnostic['event_id'].eq(eventId)]
        cond.append('''(rbDiagnosisType.code = '1'
OR (rbDiagnosisType.code = '2'
AND (NOT EXISTS (SELECT DC.id FROM Diagnostic AS DC
INNER JOIN rbDiagnosisType AS DT ON DT.id = DC.diagnosisType_id WHERE DT.code = '1'
AND DC.event_id = %s
LIMIT 1))))''' % (str(eventId)))
        rawItems = db.getRecordList(table, '*', cond, 'Diagnostic.id')
        items = []
        isDiagnosisManualSwitch = modelDiagnostics.manualSwitchDiagnosis()
        for record in rawItems:
            diagnosisId = record.value('diagnosis_id')
            MKB = db.translate('Diagnosis', 'id', forceRef(diagnosisId), 'MKB')
            MKBEx = db.translate('Diagnosis', 'id', forceRef(diagnosisId), 'MKBEx')
            morphologyMKB = db.translate('Diagnosis', 'id', forceRef(diagnosisId), 'morphologyMKB')
            setDate = forceDate(record.value('setDate'))
            TNMS = forceString(record.value('TNMS'))
            diagnosisTypeCode = forceString(record.value('code'))
            newRecord = modelDiagnostics.getEmptyRecord()
            copyFields(newRecord, record)
            newRecord.setValue('MKB', MKB)
            newRecord.setValue('MKBEx', MKBEx)
            newRecord.setValue('TNMS', toVariant(TNMS))
            newRecord.setValue('morphologyMKB', morphologyMKB)
            if diagnosisTypeCode != 7:
                diagnosisTypeId = db.translate('rbDiagnosisType', 'code', '7', 'id')
                newRecord.setValue('diagnosisType_id', toVariant(diagnosisTypeId))
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
        modelDiagnostics.setItems(items)

    def loadDiagnostics(self, modelDiagnostics, eventId):
        db = QtGui.qApp.db
        table = db.table('Diagnostic')
        rawItems = db.getRecordList(table, '*',
                                    [table['deleted'].eq(0), table['event_id'].eq(eventId), modelDiagnostics.filter],
                                    'id')
        items = []
        isDiagnosisManualSwitch = modelDiagnostics.manualSwitchDiagnosis()
        for record in rawItems:
            diagnosisId = record.value('diagnosis_id')
            MKB = db.translate('Diagnosis', 'id', forceRef(diagnosisId), 'MKB')
            MKBEx = db.translate('Diagnosis', 'id', forceRef(diagnosisId), 'MKBEx')
            morphologyMKB = db.translate('Diagnosis', 'id', forceRef(diagnosisId), 'morphologyMKB')
            setDate = forceDate(record.value('setDate'))
            TNMS = forceString(record.value('TNMS'))
            newRecord = modelDiagnostics.getEmptyRecord()
            copyFields(newRecord, record)
            newRecord.setValue('MKB', MKB)
            newRecord.setValue('MKBEx', MKBEx)
            newRecord.setValue('TNMS', toVariant(TNMS))
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
        modelDiagnostics.setItems(items)

    def loadActions(self):
        self.modelActionsSummary.regenerate()

    def getRecord(self):
        record = CProtocolEventEditDialog.getRecord(self)
        showTime = getEventShowTime(self.eventTypeId)
        # перенести в exec_ в случае успеха или в accept?

        getDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'setDate', showTime)
        getRBComboBoxValue(self.cmbPerson, record, 'setPerson_id')
        getDatetimeEditValue(self.edtEndDate, self.edtEndTime, record, 'execDate', showTime)
        getRBComboBoxValue(self.cmbPerson, record, 'execPerson_id')
        getRBComboBoxValue(self.cmbResult, record, 'result_id')
        record.setValue('isPrimary', toVariant(1 if self.chkPrimary.isChecked() else 2))
        if self.prolongateEvent:
            record.setValue('order', toVariant(5))
            record.setValue('prevEvent_id', toVariant(self.prevEventId))
        # getComboBoxValue(self.cmbOrder,         record, 'order')
        record.setValue('order', toVariant(self.cmbOrder.code()))
        record.setValue('relegateOrg_id', toVariant(self.cmbRelegateOrg.value()))
        record.setValue('externalId', toVariant(self.cmbEventExternalIdValue.currentText()))
        getRBComboBoxValue(self.cmbEventAssistant, record, 'assistant_id')
        getRBComboBoxValue(self.cmbEventCurator, record, 'curator_id')
        getRBComboBoxValue(self.cmbPatientModel, record, 'patientModel_id')
        getRBComboBoxValue(self.cmbCureType, record, 'cureType_id')
        getRBComboBoxValue(self.cmbCureMethod, record, 'cureMethod_id')
        self.setQuotaTypeIdFromAction()
        # getRBComboBoxValue(self.cmbQuota, record, 'cureMethod_id')
        self.tabNotes.getNotes(record, self.eventTypeId)
        return record

    @QtCore.pyqtSlot()
    def on_btnSelectRelegateOrg_clicked(self):
        orgId = selectOrganisation(self, self.cmbRelegateOrg.value(), False, filter=CPolyclinicComboBox._filter)
        self.cmbRelegateOrg.update()
        if orgId:
            self.cmbRelegateOrg.setValue(orgId)

    @QtCore.pyqtSlot(int)
    def onCmbResultCurrentIndexChanged(self, index):
        self.notSetCmbResult = True

    def updateResultFilter(self):
        db = QtGui.qApp.db
        tblResult = db.table('rbResult')
        cond = [tblResult['eventPurpose_id'].eq(self.eventPurposeId)]

        cmbResultFilter = self.getCmbResultFilter()
        if cmbResultFilter:
            cond.append(cmbResultFilter)

        begDate = self.edtBegDate.date()
        if begDate.isValid():
            cond.append(tblResult['begDate'].dateLe(begDate))
            cond.append(tblResult['endDate'].dateGe(begDate))

        val = self.cmbResult.value()
        self.cmbResult.setFilter(db.joinAnd(cond), order='code')
        self.cmbResult.setValue(val)

        if self.filterDiagnosticResultByPurpose:
            self.updateDiagnosticResultFilter()

    ##Обработка сигнала изменения поля (combobox) "Модель пациента"
    #    @param index:индекс нового выбранного элемента списка
    @QtCore.pyqtSlot(int)
    def on_cmbPatientModel_currentIndexChanged(self, index):
        patientModelId = self.cmbPatientModel.value()
        db = QtGui.qApp.db
        if self.cmbPatientModel.isObsolete:
            record = self.record()
            cureTypeId = forceRef(record.value('cureType_id'))
            cureMethodId = forceRef(record.value('cureMethod_id'))
            self.cmbCureMethod.setFilter('rbCureMethod.id = %s' % cureMethodId)
            self.cmbCureType.setFilter('rbCureType.id = %s' % cureTypeId)
            self.setObsoleteCureMethod = True
            return
        tablePatientModelItem = db.table('rbPatientModel_Item')
        cond = [tablePatientModelItem['master_id'].eq(patientModelId)]
        cureTypeIdList = db.getDistinctIdList(tablePatientModelItem, [tablePatientModelItem['cureType_id']], cond)
        if cureTypeIdList:
            self.cmbCureType.setFilter('rbCureType.id IN (%s) AND rbCureType.isObsolete = 0' % (
            u','.join(str(cureTypeId) for cureTypeId in cureTypeIdList if cureTypeId)))
            cureTypeId = self.cmbCureType.value()
            cond = [tablePatientModelItem['cureType_id'].eq(cureTypeId),
                    tablePatientModelItem['master_id'].eq(patientModelId)]
            cureMethodIdList = db.getDistinctIdList(tablePatientModelItem, [tablePatientModelItem['cureMethod_id']],
                                                    cond)
            if cureMethodIdList:
                self.cmbCureMethod.setFilter('rbCureMethod.id IN (%s) AND rbCureMethod.isObsolete = 0' % (
                u','.join(str(cureMethodId) for cureMethodId in cureMethodIdList if cureMethodId)))
            else:
                cond = [tablePatientModelItem['master_id'].eq(patientModelId)]
                cureMethodIdList = db.getDistinctIdList(tablePatientModelItem, [tablePatientModelItem['cureMethod_id']],
                                                        cond)
                if cureMethodIdList:
                    self.cmbCureMethod.setFilter('rbCureMethod.id IN (%s) AND rbCureMethod.isObsolete = 0' % (
                    u','.join(str(cureMethodId) for cureMethodId in cureMethodIdList if cureMethodId)))
                else:
                    self.cmbCureMethod.setFilter('rbCureMethod.id IS NULL')
            self.cmbCureMethod.setCurrentIndex(0)
        else:
            self.cmbCureType.setFilter('rbCureType.id IS NULL')
        self.cmbCureType.setCurrentIndex(0)

    ##Обработка сигнала изменения поля (combobox) "Вид лечения"
    #    @param index: индекс нового выбранного элемента списка
    @QtCore.pyqtSlot(int)
    def on_cmbCureType_currentIndexChanged(self, index):
        if self.setObsoleteCureMethod:
            return
        db = QtGui.qApp.db
        cureTypeId = self.cmbCureType.value()
        patientModelId = self.cmbPatientModel.value()
        tablePatientModelItem = db.table('rbPatientModel_Item')
        if cureTypeId:
            cond = [tablePatientModelItem['cureType_id'].eq(cureTypeId),
                    tablePatientModelItem['master_id'].eq(patientModelId)]
            cureMethodIdList = db.getDistinctIdList(tablePatientModelItem, [tablePatientModelItem['cureMethod_id']],
                                                    cond)
            if cureMethodIdList:
                self.cmbCureMethod.setFilter('rbCureMethod.id IN (%s) AND rbCureMethod.isObsolete = 0' % (
                u','.join(str(cureMethodId) for cureMethodId in cureMethodIdList if cureMethodId)))
            else:
                self.cmbCureMethod.setFilter('rbCureMethod.id IS NULL')
        elif patientModelId:
            cond = [tablePatientModelItem['master_id'].eq(patientModelId)]
            cureMethodIdList = db.getDistinctIdList(tablePatientModelItem, [tablePatientModelItem['cureMethod_id']],
                                                    cond)
            if cureMethodIdList:
                self.cmbCureMethod.setFilter('rbCureMethod.id IN (%s) AND rbCureMethod.isObsolete = 0' % (
                u','.join(str(cureMethodId) for cureMethodId in cureMethodIdList if cureMethodId)))
            else:
                self.cmbCureMethod.setFilter('rbCureMethod.id IS NULL')
        else:
            self.cmbCureMethod.setFilter('rbCureMethod.id IS NULL')
        self.cmbCureMethod.setCurrentIndex(0)

    def saveInternals(self, eventId):
        super(CF027FFDialog, self).saveInternals(eventId)
        self.saveDiagnostics(self.modelPreliminaryDiagnostics, eventId)
        self.saveDiagnostics(self.modelFinalDiagnostics, eventId)
        setAskedClassValueForDiagnosisManualSwitch(None)
        self.saveActions(eventId)
        self.saveBlankUsers(self.blankMovingIdList)
        self.updateRecommendations()

    def saveDiagnostics(self, modelDiagnostics, eventId):
        items = modelDiagnostics.items()
        isDiagnosisManualSwitch = modelDiagnostics.manualSwitchDiagnosis()
        begDate = self.edtBegDate.date()
        endDate = self.edtEndDate.date()
        date = endDate if endDate else begDate

        #        specialityIdVariant = QtGui.qApp.db.translate('Person', 'id', personIdVariant, 'speciality_id')
        MKBDiagnosisIdPairList = []
        prevId = 0
        for item in items:
            MKB = forceString(item.value('MKB'))
            MKBEx = forceString(item.value('MKBEx'))
            TNMS = forceString(item.value('TNMS'))
            morphologyMKB = forceString(item.value('morphologyMKB'))
            if self.diagnosisSetDateVisible == False:
                item.setValue('setDate', toVariant(begDate))
            else:
                date = forceDate(item.value('setDate'))
            diagnosisTypeId = forceRef(item.value('diagnosisType_id'))
            personId = forceRef(item.value('person_id'))
            specialityId = forceRef(QtGui.qApp.db.translate('Person', 'id', personId, 'speciality_id'))
            item.setValue('speciality_id', toVariant(specialityId))
            item.setValue('endDate', toVariant(endDate))
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
            if prevId > itemId:
                item.setValue('id', QtCore.QVariant())
                prevId = 0
            else:
                prevId = itemId
            MKBDiagnosisIdPairList.append((MKB, diagnosisId))
        modelDiagnostics.saveItems(eventId)
        self.modifyDiagnosises(MKBDiagnosisIdPairList)

    def getFinalDiagnosisMKB(self):
        MKB, MKBEx = self.modelFinalDiagnostics.getFinalDiagnosisMKB()
        if not MKB:
            MKB, MKBEx = self.modelPreliminaryDiagnostics.getFinalDiagnosisMKB()
        return MKB, MKBEx

    def getFinalDiagnosisId(self):
        diagnosisId = self.modelFinalDiagnostics.getFinalDiagnosisId()
        if not diagnosisId:
            diagnosisId = self.modelPreliminaryDiagnostics.getFinalDiagnosisId()
        return diagnosisId

    def saveActions(self, eventId):
        self.saveAPropertys(eventId)

    def getProtocolAction(self, eventId=None, save=False):
        action = self.modelAPActionProperties.action
        if action:
            action[u'Квота'] = self.getQuotaTypeId()

            record = action._record
            record.setValue('event_id', toVariant(self.itemId() if self.itemId() else eventId))
            record.setValue('begDate', toVariant(QtCore.QDateTime(self.edtBegDate.date(), self.edtBegTime.time())))
            record.setValue('endDate', toVariant(QtCore.QDateTime(self.edtEndDate.date(), self.edtEndTime.time())))
            record.setValue('person_id', toVariant(self.cmbPersonManager.value()))
            record.setValue('setPerson_id', toVariant(self.cmbPersonMedicineHead.value()))
            # action.setAssistant('assistant', self.cmbPersonExpert.value())
            if save:
                action.save()
        return action

    def saveAPropertys(self, eventId):
        self.getProtocolAction(eventId, save=True)

    def setOrgId(self, orgId):
        self.orgId = orgId
        self.cmbPerson.setOrgId(orgId)

    def setExternalId(self, externalId):
        self.lblValueExternalId.setText((u'Внешний идентификатор: ' + externalId) if externalId else '')

    def setOrgStructureTitle(self):
        title = u''
        orgStructureName = u''
        eventId = self.itemId()
        if eventId:
            db = QtGui.qApp.db
            tableAPHB = db.table('ActionProperty_HospitalBed')
            tableAPT = db.table('ActionPropertyType')
            tableAP = db.table('ActionProperty')
            tableActionType = db.table('ActionType')
            tableAction = db.table('Action')
            tableEvent = db.table('Event')
            tableOSHB = db.table('OrgStructure_HospitalBed')
            tableOS = db.table('OrgStructure')
            cols = [tableEvent['id'].alias('eventId'),
                    tableOS['name'].alias('nameOS')
                    ]
            queryTable = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
            queryTable = queryTable.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
            queryTable = queryTable.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
            queryTable = queryTable.innerJoin(tableAP, tableAP['type_id'].eq(tableAPT['id']))
            queryTable = queryTable.innerJoin(tableAPHB, tableAPHB['id'].eq(tableAP['id']))
            queryTable = queryTable.innerJoin(tableOSHB, tableOSHB['id'].eq(tableAPHB['value']))
            queryTable = queryTable.innerJoin(tableOS, tableOS['id'].eq(tableOSHB['master_id']))
            cond = [tableActionType['flatCode'].like(u'moving%'),
                    tableAction['event_id'].eq(eventId),
                    tableAction['deleted'].eq(0),
                    tableEvent['deleted'].eq(0),
                    tableAP['deleted'].eq(0),
                    tableActionType['deleted'].eq(0),
                    tableAPT['deleted'].eq(0),
                    tableOS['deleted'].eq(0),
                    tableAPT['typeName'].like('HospitalBed'),
                    tableAP['action_id'].eq(tableAction['id'])
                    ]
            cond.append(
                u'Action.begDate = (SELECT MAX(A.begDate) AS begDateMax FROM ActionType AS AT INNER JOIN Action AS A ON AT.id=A.actionType_id INNER JOIN Event AS E ON A.event_id=E.id INNER JOIN ActionPropertyType AS APT ON APT.actionType_id=AT.id INNER JOIN ActionProperty AS AP ON AP.type_id=APT.id INNER JOIN ActionProperty_HospitalBed AS APHB ON APHB.id=AP.id INNER JOIN OrgStructure_HospitalBed AS OSHB ON OSHB.id=APHB.value INNER JOIN OrgStructure AS OS ON OS.id=OSHB.master_id WHERE (AT.flatCode LIKE \'moving%%\') AND (APT.typeName LIKE \'HospitalBed\') AND (A.deleted=0) AND (E.deleted=0) AND (AP.deleted=0) AND (AT.deleted=0) AND (APT.deleted=0) AND (OS.deleted=0) AND (AP.action_id=Action.id) AND (A.event_id = %d))' % (
                eventId))
            recordsMoving = db.getRecordList(queryTable, cols, cond)
            for record in recordsMoving:
                eventIdRecord = forceRef(record.value('eventId'))
                if eventId == eventIdRecord:
                    orgStructureName = u'подразделение: ' + forceString(record.value('nameOS'))
            title = orgStructureName

            def findTitle(flatCode, flatTitle):
                cols = [tableEvent['id'].alias('eventId'),
                        tableAction['id']
                        ]
                queryTable = tableActionType.innerJoin(tableAction,
                                                       tableActionType['id'].eq(tableAction['actionType_id']))
                queryTable = queryTable.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
                queryTable = queryTable.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
                queryTable = queryTable.innerJoin(tableAP, tableAP['type_id'].eq(tableAPT['id']))
                cond = [tableActionType['flatCode'].like(flatCode),
                        tableAction['deleted'].eq(0),
                        tableAction['event_id'].eq(eventId),
                        tableEvent['deleted'].eq(0),
                        tableAP['deleted'].eq(0),
                        tableActionType['deleted'].eq(0),
                        tableAPT['deleted'].eq(0),
                        tableAP['action_id'].eq(tableAction['id'])
                        ]
                group = u'Event.id, Action.`id`'
                recordsReceived = db.getRecordListGroupBy(queryTable, cols, cond, group)
                for record in recordsReceived:
                    eventIdRecord = forceRef(record.value('eventId'))
                    if eventId == eventIdRecord:
                        actionId = forceRef(record.value('id'))
                        if actionId:
                            return flatTitle
                return u''

            if title == u'':
                title = findTitle(u'received%', u'ПРИЕМНЫЙ ПОКОЙ')
        return title

    def setEventTypeId(self, eventTypeId):
        CEventEditDialog.setEventTypeId(self, eventTypeId, u'Ф.001')
        titleF027 = self.setOrgStructureTitle()
        CProtocolEventEditDialog.setEventTypeId(self, eventTypeId, u'Ф.027ФФ', titleF027)
        showTime = getEventShowTime(eventTypeId)
        self.edtBegTime.setVisible(showTime)
        self.edtEndTime.setVisible(showTime)

        if self.cmbResult.value() is None:
            if self.inheritResult == True:
                self.cmbResult.setValue(self.defaultEventResultId.get(self.eventPurposeId))
        self.updateResultFilter()
        customizePrintButton(self.btnPrint, self.eventContext if self.eventContext else 'F027')
        self.diagnosisSetDateVisible = forceBool(getDiagnosisSetDateVisible(eventTypeId))
        if self.diagnosisSetDateVisible == False:
            self.tblFinalDiagnostics.setColumnHidden(4, True)
            self.tblPreliminaryDiagnostics.setColumnHidden(4, True)

    def getModelFinalDiagnostics(self):
        return self.modelFinalDiagnostics

    def updateMKB(self):
        begDate = self.edtBegDate.date()
        filter = None
        if begDate.isValid():
            filter = {'begDate': begDate, 'clientId': self.clientId}
        cols = self.modelFinalDiagnostics.cols()
        resultCol = cols[2]
        resultCol.setFilter(filter)

    def resetActionTemplateCache(self):
        pass

    def checkDataEntered(self):
        result = CEventEditDialog.checkDataEntered(self)
        self.blankMovingIdList = []
        result = result and (self.cmbPerson.value() or self.checkInputMessage(u'врача', False, self.cmbPerson))
        begDate = self.edtBegDate.date()
        endDate = self.edtEndDate.date() if self._isClosedEventCheck else QtCore.QDate()
        result = result and (not begDate.isNull() or self.checkInputMessage(u'дату назначения', False, self.edtBegDate))
        if not QtGui.qApp.userHasRight(urDoNotCheckResultAndMKB):
            result = result and (
            endDate.isNull() or self.cmbResult.value() or self.checkInputMessage(u'результат', True, self.cmbResult))
        if endDate.isNull():
            pass
        else:
            result = result and self.checkActionDataEntered(begDate, QtCore.QDate(), endDate, self.tabToken,
                                                            self.edtBegDate, None, self.edtEndDate)
            result = result and self.checkEventDate(begDate, endDate, None, self.tabToken, None, self.edtEndDate, True)
            minDuration, maxDuration = getEventDuration(self.eventTypeId)
            if minDuration <= maxDuration:
                countRedDays = not QtGui.qApp.isExcludeRedDaysInEventLength()
                eventDuration = getEventLengthDays(begDate, endDate, countRedDays, self.eventTypeId)
                eventDurationErrorString = u'Указана длительность с учётом выходных: %s.' % formatNum(eventDuration, (
                u'день', u'дня', u'дней'))
                result = result and (eventDuration >= minDuration or
                                     self.checkValueMessage(u'Длительность должна быть не менее %s. %s' % (
                                     formatNum(minDuration, (u'дня', u'дней', u'дней')), eventDurationErrorString),
                                                            False, self.edtEndDate))
                result = result and (maxDuration == 0 or eventDuration <= maxDuration or
                                     self.checkValueMessage(u'Длительность должна быть не более %s. %s' % (
                                     formatNum(maxDuration, (u'дня', u'дней', u'дней')), eventDurationErrorString),
                                                            False,
                                                            self.edtEndDate))  # result = result and (len(self.modelFinalDiagnostics.items())>0 or self.checkInputMessage(u'диагноз', False, self.tblFinalDiagnostics))
        # result = result and self.checkDiagnosticsDataEntered(endDate)
        # result = result and self.checkActionsDateEnteredActuality(begDate, endDate, [self.tabMisc])  # , self.tabInspectionPlan])
        # result = result and self.checkActionsDataEntered([self.tabMisc], begDate, endDate)
        result = result and self.checkActionsPropertiesDataEntered([self.tblActionProperties])
        result = result and self.checkTabNotesReferral()

        if \
                                                                self.getFinalDiagnosisMKB()[0] is not None and \
                                                                self.getFinalDiagnosisMKB()[0] != u'' and \
                                                        self.getFinalDiagnosisMKB()[0][0] == u'C' \
                                        and not QtGui.qApp.userHasRight(urOncoDiagnosisWithoutTNMS) \
                                and QtGui.qApp.isTNMSVisible() and (
                        self.modelFinalDiagnostics.getFinalDiagnosis().value('TNMS') is None or
                        forceString(self.modelFinalDiagnostics.getFinalDiagnosis().value('TNMS')) == ''):
            result = result and self.checkValueMessage(check_data_text_TNM, False, None)

        self.valueForAllActionEndDate = None
        return result

    def checkActionsPropertiesDataEntered(self, tabList):
        for actionTab in tabList:
            model = actionTab.model()
            action = model.action
            if action and action._actionType.id:
                if not self.checkActionProperties(actionTab, action, actionTab):
                    return False
        return True

    def checkActionEndDate(self, strNameActionType, tblWidget, row, column, widgetEndDate):
        if self.valueForAllActionEndDate is None:
            buttons = QtGui.QMessageBox.Ok | QtGui.QMessageBox.Ignore
            message = u'Должна быть указана дата выполнения действия%s' % (strNameActionType)
            messageBox = QtGui.QMessageBox(QtGui.QMessageBox.Warning,
                                           u'Внимание!',
                                           message,
                                           buttons,
                                           self
                                           )
            messageBox.setDefaultButton(QtGui.QMessageBox.Ok)
            messageBox.setEscapeButton(QtGui.QMessageBox.Ok)

            currentDateButton = QtGui.QPushButton(u'текущая дата')
            currentDateForAllButton = QtGui.QPushButton(u'текущая дата(для всех)')
            ignoreForAllButton = QtGui.QPushButton(u'игнорировать(для всех)')

            messageBox.addButton(ignoreForAllButton, QtGui.QMessageBox.AcceptRole)
            messageBox.addButton(currentDateButton, QtGui.QMessageBox.AcceptRole)
            messageBox.addButton(currentDateForAllButton, QtGui.QMessageBox.AcceptRole)

            res = messageBox.exec_()

            clickedButton = messageBox.clickedButton()

            if res in [QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ignore]:
                if res == QtGui.QMessageBox.Ok:
                    model = tblWidget.model()
                    tblWidget.setCurrentIndex(model.index(row, 0))
                    self.setFocusToWidget(widgetEndDate, row, column)
                    return False
                elif res == QtGui.QMessageBox.Ignore:
                    return True
                else:
                    return True

            if clickedButton == currentDateButton:
                model = tblWidget.model()
                record = model._items[row][0]
                record.setValue('endDate', QtCore.QVariant(QtCore.QDate.currentDate()))
                record.setValue('status', QtCore.QVariant(2))
                return True
            elif clickedButton == currentDateForAllButton:
                self.valueForAllActionEndDate = True
            elif clickedButton == ignoreForAllButton:
                self.valueForAllActionEndDate = False
            else:
                return True

        if self.valueForAllActionEndDate == True:
            model = tblWidget.model()
            record = model._items[row][0]
            record.setValue('endDate', QtCore.QVariant(QtCore.QDate.currentDate()))
            record.setValue('status', QtCore.QVariant(2))
            return True
        elif self.valueForAllActionEndDate == False:
            return True
        else:
            return True

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
        return checkDiagnosis(self, MKB, diagFilter, self.clientId, self.clientSex, self.clientAge, self.begDate(),
                              self.endDate(), self.eventTypeId, isEx)

    def getDiagnosisTypeId(self, dt):
        return forceRef(QtGui.qApp.db.translate('rbDiagnosisType', 'code', '2' if dt else '9', 'id'))

    def getEventInfo(self, context, infoClass=CEventInfo):
        result = CProtocolEventEditDialog.getEventInfo(self, context)
        # ручная инициализация свойств
        result._isPrimary = self.chkPrimary.isChecked()
        # ручная инициализация таблиц
        # record используется для обновления modelAPActionProperties данными из комбобоксов с главной вкладки формы для дальнейшего вывода на печать
        # Автоматически при изменении данных в комбобоксах и т.д. этого не происходит, поэтому такой изврат.
        protocolAction = self.getProtocolAction()

        result._actions = []
        if protocolAction:
            result._actions.append(context.getInstance(CCookedActionInfo, protocolAction.getRecord(), protocolAction))

        result._diagnosises = CDiagnosticInfoProxyList(context,
                                                       [self.modelPreliminaryDiagnostics, self.modelFinalDiagnostics])
        return result

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.cmbPerson.setEndDate(date)
        # self.tabMisc.setEndDate(self.eventSetDateTime.date())
        # self.tabInspectionPlan.setEndDate(self.eventSetDateTime.date())
        self.updateResultFilter()
        if QtGui.qApp.isCheckMKB():
            self.updateMKB()
        self.emitUpdateActionsAmount()
        self.setContract()
        self.updateModelsRetiredList()

    @QtCore.pyqtSlot(QtCore.QTime)
    def on_edtBegTime_timeChanged(self, time):
        self.emitUpdateActionsAmount()

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtEndDate_dateChanged(self, date):
        self.emitUpdateActionsAmount()
        self.setContract()
        self.tabNotes.cmbClientPolicy.updatePolicy(date)
        if QtGui.qApp.isAutoClosed():
            self.chkIsClosed.setChecked(date != QtCore.QDate())

    @QtCore.pyqtSlot(QtCore.QTime)
    def on_edtEndTime_timeChanged(self, time):
        self.emitUpdateActionsAmount()

    @QtCore.pyqtSlot(int)
    def on_cmbPerson_currentIndexChanged(self):
        self.setPersonId(self.cmbPerson.value())

    @QtCore.pyqtSlot()
    def on_modelFinalDiagnostics_resultChanged(self):
        CEventEditDialog.defaultDiagnosticResultId[self.eventPurposeId] = self.modelFinalDiagnostics.resultId()
        self.updateResultFilter()

    @QtCore.pyqtSlot()
    def on_actDiagnosticsAddAccomp_triggered(self):
        currentRow = self.tblFinalDiagnostics.currentIndex().row()
        if currentRow >= 0:
            currentRecord = self.modelFinalDiagnostics.items()[currentRow]
            newRecord = self.modelFinalDiagnostics.getEmptyRecord()
            newRecord.setValue('diagnosisType', QtCore.QVariant(CF027FFDialog.dfAccomp))
            newRecord.setValue('speciality_id', currentRecord.value('speciality_id'))
            newRecord.setValue('healthGroup_id', currentRecord.value('healthGroup_id'))
            self.modelFinalDiagnostics.insertRecord(currentRow + 1, newRecord)
            self.tblFinalDiagnostics.setCurrentIndex(
                self.modelFinalDiagnostics.index(currentRow + 1, newRecord.indexOf('MKB')))

    def getHeadPersonName(self):
        db = QtGui.qApp.db
        r = db.getRecordEx(
            stmt="SELECT CONCAT_WS(' ', p.lastName, p.firstName, p.patrName) name FROM Person p INNER JOIN rbPost rbp ON p.post_id = rbp.id and rbp.code=1001")
        if r:
            return forceString(r.value('name'))
        else:
            return ''

    @QtCore.pyqtSlot(int)
    def on_btnPrint_printByTemplate(self, templateId):
        if self.beforePrintTemplate(templateId) == -1:
            return
        context = CInfoContext()
        data = getEventContextData(self)
        data['templateCounterValue'] = self.oldTemplates.get(templateId, '')
        # FIXME: добавить данные
        idList = []
        applyTemplate(self, templateId, data)


class CF003BaseDiagnosticsModel(CInDocTableModel):
    __pyqtSignals__ = ('diagnosisChanged()',
                       )
    MKB_allowed_morphology = ['C', 'D']

    def __init__(self, parent, finishDiagnosisTypeCode, baseDiagnosisTypeCode, accompDiagnosisTypeCode,
                 complicDiagnosisTypeCode):
        CInDocTableModel.__init__(self, 'Diagnostic', 'id', 'event_id', parent)
        self._parent = parent
        self.isManualSwitchDiagnosis = QtGui.qApp.defaultIsManualSwitchDiagnosis()
        self.isMKBMorphology = QtGui.qApp.defaultMorphologyMKBIsVisible()
        self.characterIdForHandleDiagnosis = None
        self.columnHandleDiagnosis = None
        self.diagnosisTypeCol = CF003DiagnosisTypeCol(u'Тип', 'diagnosisType_id', 2,
                                                      [finishDiagnosisTypeCode, baseDiagnosisTypeCode,
                                                       accompDiagnosisTypeCode, complicDiagnosisTypeCode],
                                                      smartMode=False)
        self.addCol(self.diagnosisTypeCol)
        self.colPerson = self.addCol(
            CActionPersonInDocTableColSearch(u'Врач', 'person_id', 20, 'vrbPersonWithSpeciality', order='name',
                                             parent=parent))
        self.addExtCol(CICDExInDocTableCol(u'МКБ', 'MKB', 7), QtCore.QVariant.String)
        self.addExtCol(CICDExInDocTableCol(u'Доп.МКБ', 'MKBEx', 7), QtCore.QVariant.String)
        self.addCol(CDateInDocTableCol(u'Выявлено', 'setDate', 10))
        if QtGui.qApp.isTNMSVisible():
            self.addCol(CTNMSCol(u'TNM-Ст', 'TNMS', 10))
        if self.isMKBMorphology:
            self.addExtCol(
                CMKBMorphologyCol(u'Морф.', 'morphologyMKB', 10, 'MKB_Morphology', filter='`group` IS NOT NULL'),
                QtCore.QVariant.String)
        self.addCol(CDiseaseCharacter(u'Хар', 'character_id', 7, showFields=CRBComboBox.showCode,
                                      prefferedWidth=150)).setToolTip(u'Характер')
        if self.isManualSwitchDiagnosis:
            self.addExtCol(CBoolInDocTableCol(u'П', 'handleDiagnosis', 10), QtCore.QVariant.Int)
            self.characterIdForHandleDiagnosis = forceRef(
                QtGui.qApp.db.translate('rbDiseaseCharacter', 'code', '1', 'id'))
            self.columnHandleDiagnosis = self._mapFieldNameToCol.get('handleDiagnosis')

        self.addCol(
            CDiseasePhases(u'Фаза', 'phase_id', 7, showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(
            u'Фаза')
        self.addCol(
            CDiseaseStage(u'Ст', 'stage_id', 7, showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(
            u'Стадия')
        self.addCol(CRBInDocTableCol(u'ДН', 'dispanser_id', 7, 'rbDispanser', showFields=CRBComboBox.showCode,
                                     prefferedWidth=150)).setToolTip(u'Диспансерное наблюдение')
        self.addCol(CRBInDocTableCol(u'Травма', 'traumaType_id', 10, 'rbTraumaType', addNone=True,
                                     showFields=CRBComboBox.showName, prefferedWidth=150))
        self.addCol(CRBInDocTableCol(u'ГрЗд', 'healthGroup_id', 7, 'rbHealthGroup', addNone=True,
                                     showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(
            u'Группа здоровья')
        self.setFilter(
            self.table['diagnosisType_id'].inlist([typeId for typeId in self.diagnosisTypeCol.ids if typeId]))

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
            if self.isMKBMorphology and index.isValid():
                if column == self._mapFieldNameToCol.get('morphologyMKB'):
                    mkb = forceString(self.items()[row].value('MKB'))
                    if not (bool(mkb) and mkb[0] in CF003BaseDiagnosticsModel.MKB_allowed_morphology):
                        result = (result & ~QtCore.Qt.ItemIsEditable)
        if QtGui.qApp.isPNDDiagnosisMode() and (
                row == len(self.items()) or index.column() != self._mapFieldNameToCol.get('result_id')):
            result = (result & ~QtCore.Qt.ItemIsEditable)
        return result

    def getEmptyRecord(self):
        result = CInDocTableModel.getEmptyRecord(self)
        result.append(QtSql.QSqlField('diagnosis_id', QtCore.QVariant.Int))
        result.append(QtSql.QSqlField('speciality_id', QtCore.QVariant.Int))
        result.append(QtSql.QSqlField('setDate', QtCore.QVariant.DateTime))
        result.append(QtSql.QSqlField('endDate', QtCore.QVariant.DateTime))
        result.append(QtSql.QSqlField('payStatus', QtCore.QVariant.Int))
        if self.items():
            result.setValue('diagnosisType_id', toVariant(self.diagnosisTypeCol.ids[2]))
        else:
            result.setValue('diagnosisType_id', toVariant(
                self.diagnosisTypeCol.ids[0] if self.diagnosisTypeCol.ids[0] else self.diagnosisTypeCol.ids[1]))
            if self._parent.inheritResult == True:
                result.setValue('result_id',
                                toVariant(CEventEditDialog.defaultDiagnosticResultId.get(self._parent.eventPurposeId)))
            else:
                result.setValue('result_id', toVariant(None))
        result.setValue('person_id',
                        toVariant(QtGui.qApp.userId if QtGui.qApp.userSpecialityId else self._parent.personId))
        return result

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        column = index.column()
        row = index.row()
        if not variantEq(self.data(index, role), value):
            eventEditor = QtCore.QObject.parent(self)
            if column == 0:  # тип диагноза
                result = CInDocTableModel.setData(self, index, value, role)
                if result:
                    self.updateDiagnosisType(set([row]))
                    self.emitDiagnosisChanged()
                return result
            elif column == 1:  # врач
                personId = forceRef(value)
                if not eventEditor.checkClientAttendaceEE(personId):
                    return False
                result = CInDocTableModel.setData(self, index, value, role)
                if result:
                    self.updateDiagnosisType(set())
                return result
            elif column == 2:  # код МКБ
                newMKB = forceString(value)
                if not newMKB:
                    specifiedMKB = ''
                    specifiedCharacterId = None
                    specifiedTraumaTypeId = None
                else:
                    acceptable, specifiedMKB, specifiedMKBEx, specifiedCharacterId, specifiedTraumaTypeId = eventEditor.specifyDiagnosis(
                        newMKB)
                    if not acceptable:
                        return False
                value = toVariant(specifiedMKB)
                result = CInDocTableModel.setData(self, index, value, role)
                if result:
                    self.updateCharacterByMKB(row, specifiedMKB, specifiedCharacterId)
                    self.updateTraumaType(row, specifiedMKB, specifiedTraumaTypeId)
                    self.emitDiagnosisChanged()
                return result
            if column == 3:  # доп. код МКБ
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

    def payStatus(self, row):
        if 0 <= row < len(self.items()):
            return forceInt(self.items()[row].value('payStatus'))
        else:
            return 0

    def removeRowEx(self, row):
        self.removeRows(row, 1)

    def updateDiagnosisType(self, fixedRowSet):
        mapPersonIdToRow = {}
        diagnosisTypeIds = []
        endDiagnosisTypeIds = None
        endPersonId = None
        endRow = -1
        for row, item in enumerate(self.items()):
            personId = forceRef(item.value('person_id'))
            rows = mapPersonIdToRow.setdefault(personId, [])
            rows.append(row)
            diagnosisTypeId = forceRef(item.value('diagnosisType_id'))
            diagnosisTypeIds.append(diagnosisTypeId)
            if self.diagnosisTypeCol.ids[0] == diagnosisTypeId and personId == self._parent.personId:
                endDiagnosisTypeIds = diagnosisTypeId
                endPersonId = personId
                endRow = row

        for personId, rows in mapPersonIdToRow.iteritems():
            usedDiagnosisTypeIds = [diagnosisTypeIds[row] for row in fixedRowSet.intersection(set(rows))]
            listFixedRowSet = [row for row in fixedRowSet.intersection(set(rows))]
            if ((self.diagnosisTypeCol.ids[0] in usedDiagnosisTypeIds) or (
                self.diagnosisTypeCol.ids[0] == diagnosisTypeIds[rows[0]])) and personId == self._parent.personId:
                firstDiagnosisId = self.diagnosisTypeCol.ids[0]
            elif (self.diagnosisTypeCol.ids[0] in usedDiagnosisTypeIds) and personId != self._parent.personId:
                res = QtGui.QMessageBox.warning(self._parent,
                                                u'Внимание!',
                                                u'Смена заключительного диагноза.\nОтветственный будет заменен на \'%s\'.\nВы подтверждаете изменения?' % (
                                                forceString(
                                                    QtGui.qApp.db.translate('vrbPersonWithSpeciality', 'id', personId,
                                                                            'name'))),
                                                QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                                                QtGui.QMessageBox.Cancel)
                if res == QtGui.QMessageBox.Ok:
                    self._parent.personId = personId
                    self._parent.cmbPerson.setValue(self._parent.personId)
                    firstDiagnosisId = self.diagnosisTypeCol.ids[0]
                    rowEndPersonId = mapPersonIdToRow[endPersonId] if endPersonId else None
                    diagnosisTypeColIdsEnd = -1
                    if rowEndPersonId and len(rowEndPersonId) > 1:
                        for rowPerson in rowEndPersonId:
                            if diagnosisTypeIds[rowPerson] == self.diagnosisTypeCol.ids[1] or diagnosisTypeIds[
                                rowPerson] == self.diagnosisTypeCol.ids[0]:
                                if endRow > -1 and endDiagnosisTypeIds == self.diagnosisTypeCol.ids[
                                    0] and endRow != rowPerson:
                                    diagnosisTypeColIdsEnd = self.diagnosisTypeCol.ids[2]
                                    break
                        if diagnosisTypeColIdsEnd == -1:
                            diagnosisTypeColIdsEnd = self.diagnosisTypeCol.ids[1]
                    else:
                        if endRow > -1 and endDiagnosisTypeIds == self.diagnosisTypeCol.ids[0]:
                            diagnosisTypeColIdsEnd = self.diagnosisTypeCol.ids[1]
                    if diagnosisTypeColIdsEnd > -1:
                        self.items()[endRow].setValue('diagnosisType_id', toVariant(diagnosisTypeColIdsEnd))
                        self.emitCellChanged(endRow, self.items()[endRow].indexOf('diagnosisType_id'))
                        diagnosisTypeIds[endRow] = forceRef(self.items()[endRow].value('diagnosisType_id'))
                else:
                    if endRow > -1 and endDiagnosisTypeIds == self.diagnosisTypeCol.ids[0]:
                        self.items()[endRow].setValue('diagnosisType_id', toVariant(endDiagnosisTypeIds))
                        self.emitCellChanged(endRow, self.items()[endRow].indexOf('diagnosisType_id'))
                        diagnosisTypeIds[endRow] = forceRef(self.items()[endRow].value('diagnosisType_id'))
                    firstDiagnosisId = self.diagnosisTypeCol.ids[1]
                    diagnosisTypeColIdsRows = -1
                    if len(rows) > 1:
                        for rowPerson in rows:
                            if diagnosisTypeIds[rowPerson] == self.diagnosisTypeCol.ids[1] or diagnosisTypeIds[
                                rowPerson] == self.diagnosisTypeCol.ids[0] and (rowPerson not in listFixedRowSet):
                                diagnosisTypeColIdsRows = self.diagnosisTypeCol.ids[2]
                                break
                        if diagnosisTypeColIdsRows == -1:
                            diagnosisTypeColIdsRows = self.diagnosisTypeCol.ids[1]
                    else:
                        diagnosisTypeColIdsRows = self.diagnosisTypeCol.ids[1]
                    if diagnosisTypeColIdsRows > -1:
                        for rowFixed in listFixedRowSet:
                            self.items()[rowFixed].setValue('diagnosisType_id', toVariant(diagnosisTypeColIdsRows))
                            self.emitCellChanged(rowFixed, self.items()[rowFixed].indexOf('diagnosisType_id'))
                            diagnosisTypeIds[rowFixed] = forceRef(self.items()[rowFixed].value('diagnosisType_id'))
                            usedDiagnosisTypeIds = [diagnosisTypeIds[row] for row in
                                                    fixedRowSet.intersection(set(rows))]
            else:
                firstDiagnosisId = self.diagnosisTypeCol.ids[1]
            otherDiagnosisId = self.diagnosisTypeCol.ids[2]

            diagnosisTypeId = firstDiagnosisId if firstDiagnosisId not in usedDiagnosisTypeIds else otherDiagnosisId
            freeRows = set(rows).difference(fixedRowSet)
            for row in rows:
                if (row in freeRows) or diagnosisTypeIds[row] not in [firstDiagnosisId, otherDiagnosisId]:
                    if diagnosisTypeId != diagnosisTypeIds[row] and diagnosisTypeIds[row] != self.diagnosisTypeCol.ids[
                        3]:
                        self.items()[row].setValue('diagnosisType_id', toVariant(diagnosisTypeId))
                        self.emitCellChanged(row, self.items()[row].indexOf('diagnosisType_id'))
                        diagnosisTypeId = forceRef(self.items()[row].value('diagnosisType_id'))
                        diagnosisTypeIds[row] = diagnosisTypeId
                    diagnosisTypeId = otherDiagnosisId

    def updateCharacterByMKB(self, row, MKB, specifiedCharacterId):
        characterIdList = getAvailableCharacterIdByMKB(MKB)
        item = self.items()[row]
        if specifiedCharacterId in characterIdList:
            characterId = specifiedCharacterId
        else:
            characterId = forceRef(item.value('character_id'))
            if (characterId in characterIdList) or (characterId == None and not characterIdList):
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

    def getFinalDiagnosisMKB(self):
        finalDiagnosisTypeId = self.diagnosisTypeCol.ids[0] or self.diagnosisTypeCol.ids[1]
        items = self.items()
        for item in items:
            diagnosisTypeId = forceRef(item.value('diagnosisType_id'))
            if diagnosisTypeId == finalDiagnosisTypeId:
                return forceString(item.value('MKB')), forceString(item.value('MKBEx'))
        return '', ''

    def getFinalDiagnosisId(self):
        finalDiagnosisTypeId = self.diagnosisTypeCol.ids[0]
        items = self.items()
        for item in items:
            diagnosisTypeId = forceRef(item.value('diagnosisType_id'))
            if diagnosisTypeId == finalDiagnosisTypeId:
                return forceRef(item.value('diagnosis_id'))
        return None

    def getFinalDiagnosis(self):
        finalDiagnosisTypeId = self.diagnosisTypeCol.ids[0]
        items = self.items()
        for item in items:
            diagnosisTypeId = forceRef(item.value('diagnosisType_id'))
            if diagnosisTypeId == finalDiagnosisTypeId:
                return item
        return None

    def emitDiagnosisChanged(self):
        self.emit(QtCore.SIGNAL('diagnosisChanged()'))


class CF003PreliminaryDiagnosticsModel(CF003BaseDiagnosticsModel):
    def __init__(self, parent):
        CF003BaseDiagnosticsModel.__init__(self, parent, None, '7', '11', None)

    def getEmptyRecord(self):
        result = CF003BaseDiagnosticsModel.getEmptyRecord(self)
        return result


class CF003FinalDiagnosticsModel(CF003BaseDiagnosticsModel):
    __pyqtSignals__ = ('resultChanged()',
                       )

    def __init__(self, parent):
        CF003BaseDiagnosticsModel.__init__(self, parent, '1', '2', '9', '3')
        self.addCol(CRBInDocTableCol(forceTr(u'Результат', u'EventDiagnostic'), 'result_id', 10, 'rbDiagnosticResult',
                                     showFields=CRBComboBox.showNameAndCode, prefferedWidth=350))

    def addRecord(self, record):
        super(CF003FinalDiagnosticsModel, self).addRecord(record)
        self.emitResultChanged()

    def getCloseOrMainDiagnosisTypeIdList(self):
        return self.diagnosisTypeCol.ids[:2]

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        resultId = self.resultId()
        result = CF003BaseDiagnosticsModel.setData(self, index, value, role)
        if resultId != self.resultId():
            self.emitResultChanged()
        return result

    def removeRowEx(self, row):
        resultId = self.resultId()
        self.removeRows(row, 1)
        if resultId != self.resultId():
            self.emitResultChanged()

    def resultId(self):
        items = self.items()
        diagnosisTypeId = self.diagnosisTypeCol.ids[0]
        for item in items:
            if forceRef(item.value('diagnosisType_id')) == diagnosisTypeId:
                return forceRef(item.value('result_id'))
        else:
            return None

    def emitResultChanged(self):
        self.emit(QtCore.SIGNAL('resultChanged()'))


class CF003DiagnosisTypeCol(CDiagnosisTypeCol):
    def __init__(self, title=u'Тип', fieldName='diagnosisType_id', width=5, diagnosisTypeCodes=None, smartMode=True,
                 **params):
        if not diagnosisTypeCodes:
            diagnosisTypeCodes = []
        CDiagnosisTypeCol.__init__(self, title, fieldName, width, diagnosisTypeCodes, smartMode, **params)
        self.namesF003 = [u'Закл', u'Осн', u'Соп', u'Осл']

    def toString(self, val, record):
        typeId = forceRef(val)
        if typeId in self.ids:
            return toVariant(self.namesF003[self.ids.index(typeId)])
        return QtCore.QVariant()

    def setEditorData(self, editor, value, record):
        editor.clear()
        if value.isNull():
            value = record.value(self.fieldName())
        typeId = forceRef(value)
        if self.smartMode:
            if typeId == self.ids[0]:
                editor.addItem(self.namesF003[0], toVariant(self.ids[0]))
            elif typeId == self.ids[1]:
                if self.ids[0]:
                    editor.addItem(self.namesF003[0], toVariant(self.ids[0]))
                editor.addItem(self.namesF003[1], toVariant(self.ids[1]))
            else:
                editor.addItem(self.namesF003[2], toVariant(self.ids[2]))
                editor.addItem(self.namesF003[3], toVariant(self.ids[3]))
        else:
            for itemName, itemId in zip(self.namesF003, self.ids):
                if itemId:
                    editor.addItem(itemName, toVariant(itemId))
        currentIndex = editor.findData(toVariant(typeId))
        editor.setCurrentIndex(currentIndex)


class CActionInfoProxyListProtocol(CInfoProxyList):
    def __init__(self, context, models, protocol, eventInfo):
        CInfoProxyList.__init__(self, context)
        self._rawItems = []
        for model in models:
            self._rawItems.extend(model.items())
        protocolItem = [(protocol.action._record, protocol.action)] if protocol.action else []
        self._rawItems.extend(protocolItem)
        self._items = [None] * len(self._rawItems)
        self._eventInfo = eventInfo

    def __getitem__(self, key):
        v = self._items[key]
        if v is None:
            record, action = self._rawItems[key]
            v = self.getInstance(CCookedActionInfo, record, action)
            v._eventInfo = self._eventInfo
            self._items[key] = v
        return v
