# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

# Форма 025-12/у: Этап диспансерного наблюдения

from PyQt4 import QtCore, QtGui, QtSql

from Events.Action import CActionType, CActionTypeCache
from Events.ActionInfo import CActionInfoProxyList
from Events.ActionsSummaryModel import CFxxxActionsSummaryModel
from Events.DiagnosisType import CDiagnosisTypeCol
from Events.EventEditDialog import CEventEditDialog, CDiseaseCharacter
from Events.EventInfo import CDiagnosticInfoProxyList, CVisitInfoProxyList
from Events.EventVisitsModel import CEventVisitsModel, CRBServiceInDocTableCol
from Events.Utils import checkDiagnosis, checkIsHandleDiagnosisIsChecked, getAvailableCharacterIdByMKB, \
    getDiagnosisId2, getDiagnosisSetDateVisible, getEventDuration, getEventShowTime, getResultIdByDiagnosticResultId, \
    hasEventVisitAssistant, \
    isEventLong, payStatusText, setAskedClassValueForDiagnosisManualSwitch, \
    CTableSummaryActionsMenuMixin, getEventLengthDays, setOrgStructureIdToCmbPerson
from Forms.F02512.PreF02512Dialog import CPreF02512Dialog, CPreF02512DagnosticAndActionPresets
from Forms.Utils import check_data_text_TNM
from RefBooks.Tables import rbFinance, rbScene, rbVisitType
from Ui_F02512 import Ui_Dialog
from Users.Rights import urAccessF030planner, urAdmin, urEditDiagnosticsInPayedEvents, urRegTabWriteRegistry, \
    urOncoDiagnosisWithoutTNMS
from library.ICDInDocTableCol import CICDExInDocTableCol
from library.ICDMorphologyInDocTableCol import CMKBMorphologyCol
from library.InDocTable import CInDocTableModel, CBoolInDocTableCol, CDateInDocTableCol, CRBInDocTableCol, \
    CActionPersonInDocTableColSearch
from library.PrintInfo import CInfoContext
from library.PrintTemplates import applyTemplate, customizePrintButton, getPrintButton
from library.TNMS.TNMSComboBox import CTNMSCol
from library.Utils import forceBool, forceDate, forceInt, forceRef, forceString, toVariant, copyFields, \
    formatNum, variantEq
from library.crbcombobox import CRBComboBox
from library.interchange import getDateEditValue, getDatetimeEditValue, getRBComboBoxValue, \
    setDateEditValue, setDatetimeEditValue, setRBComboBoxValue


class CF02512Dialog(CEventEditDialog, Ui_Dialog, CTableSummaryActionsMenuMixin):
    formTitle = u'Ф.025-12/у'

    isTabMesAlreadyLoad = False
    isTabStatusAlreadyLoad = False
    isTabDiagnosticAlreadyLoad = False
    isTabCureAlreadyLoad = False
    isTabMiscAlreadyLoad = False
    isTabAmbCardAlreadyLoad = False
    isTabTempInvalidEtcAlreadyLoad = False
    isTabCashAlreadyLoad = False
    isTabNotesAlreadyLoad = False

    def __init__(self, parent):
        CEventEditDialog.__init__(self, parent)
        self.mapSpecialityIdToDiagFilter = {}

        #self.addModels('Visits', CEventVisitsModel(self))
        self.addModels('Visits', CF02512VisitsModel(self))
        self.addModels('FinalDiagnostics',       CF02512FinalDiagnosticsModel(self))
        self.addModels('ActionsSummary', CFxxxActionsSummaryModel(self, True))

        self.createSaveAndCreateAccountButton()
        self.actEditClient = QtGui.QAction(u'Изменить описание клиента', self)
        self.actEditClient.setObjectName('actEditClient')
        self.btnPrint = getPrintButton(self, '')
        self.btnPrint.setObjectName('btnPrint')

        self.setupUi(self)

        self.tabMes.preSetupUiMini()
        self.tabMes.preSetupUi()
        self.tabMes.setupUi(self.tabMes)
        self.tabMes.setupUiMini(self.tabMes)
        self.tabMes.postSetupUiMini()

        self.tabStatus.preSetupUiMini()
        self.tabStatus.setupUiMini(self.tabStatus)
        self.tabStatus.postSetupUiMini()

        self.tabDiagnostic.preSetupUiMini()
        self.tabDiagnostic.setupUiMini(self.tabDiagnostic)
        self.tabDiagnostic.postSetupUiMini()

        self.tabCure.preSetupUiMini()
        self.tabCure.setupUiMini(self.tabCure)
        self.tabCure.postSetupUiMini()

        self.tabMisc.preSetupUiMini()
        self.tabMisc.setupUiMini(self.tabMisc)
        self.tabMisc.postSetupUiMini()

        self.tabCash.preSetupUiMini()
        self.tabCash.setupUiMini(self.tabCash)
        self.tabCash.postSetupUiMini()

        self.tabNotes.preSetupUiMini()
        self.tabNotes.preSetupUi()
        self.tabNotes.setupUiMini(self.tabNotes)
        self.tabNotes.setupUi(self.tabNotes)
        self.tabNotes.postSetupUiMini(self.edtBegDate.date())

        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Осмотр %s'  % self.formTitle)
        self.tabToken.setFocusProxy(self.tblFinalDiagnostics)
        self.tabMes.setEventEditor(self)

        self.tabStatus.setEventEditor(self)
        self.tabDiagnostic.setEventEditor(self)
        self.tabCure.setEventEditor(self)
        self.tabMisc.setEventEditor(self)
        self.tabCash.setEventEditor(self)
        self.tabStatus.setActionTypeClass(0)
        self.tabDiagnostic.setActionTypeClass(1)
        self.tabCure.setActionTypeClass(2)
        self.tabMisc.setActionTypeClass(3)
        self.buttonBox.addButton(self.btnPrint, QtGui.QDialogButtonBox.ActionRole)
        self.setupSaveAndCreateAccountButton()
        self.setupSaveAndCreateAccountForPeriodButton()
        self.setupActionSummarySlots()

        self.cmbPrimary.setVisible(False)
        self.cmbContract.setCheckMaxClients(True)

        self.tblVisits.setModel(self.modelVisits)
        self.tblFinalDiagnostics.setModel(self.modelFinalDiagnostics)
        self.tblFinalDiagnostics.setDelRowsChecker(None)
        self.tblActions.setModel(self.modelActionsSummary)
        self.modelActionsSummary.addModel(self.tabStatus.modelAPActions)
        self.modelActionsSummary.addModel(self.tabDiagnostic.modelAPActions)
        self.modelActionsSummary.addModel(self.tabCure.modelAPActions)
        self.modelActionsSummary.addModel(self.tabMisc.modelAPActions)
        self.tabCash.addActionModel(self.tabStatus.modelAPActions)
        self.tabCash.addActionModel(self.tabDiagnostic.modelAPActions)
        self.tabCash.addActionModel(self.tabCure.modelAPActions)
        self.tabCash.addActionModel(self.tabMisc.modelAPActions)

        self.markEditableTableWidget(self.tblVisits)
        self.markEditableTableWidget(self.tblFinalDiagnostics)
        self.markEditableTableWidget(self.tblActions)

        self.txtClientInfoBrowser.actions.append(self.actEditClient)
        self.actEditClient.setEnabled(QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteRegistry]))
        self.tblVisits.addPopupDelRow()
        CTableSummaryActionsMenuMixin.__init__(self)

        self.setupDirtyCather()
        self.setIsDirty(False)
        self.blankMovingIdList = []
        self.clientId = None
        self.prolongateEvent = False
        self.prevEventId = None
        self.tabNotes.setEventEditor(self)
        self.cmbResult.setShowFields(CRBComboBox.showCodeAndName)

        self.postSetupUi()

        self._isCheckPresenceInAccounts = True

        if (not QtGui.qApp.userHasRight('accessEditAutoPrimacy')):
            if QtGui.qApp.isAutoPrimacy():
                self.cmbPrimary.setEnabled(False)


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
        return self.modelFinalDiagnostics

    def _prepare(self, contractId, clientId, eventTypeId, orgId, personId, eventSetDatetime, eventDatetime, includeRedDays, numDays,
                 presetDiagnostics, presetActions, disabledActions, externalId, assistantId, curatorId,
                 actionTypeIdValue=None, valueProperties=None, relegateOrgId=None, diagnos=None, financeId=None,
                 protocolQuoteId=None, actionByNewEvent=None, referrals=None, isAmb=True, recommendationList=None):
        if not valueProperties:
            valueProperties = []
        if not actionByNewEvent:
            actionByNewEvent = []
        if not referrals:
            referrals = {}
        if not recommendationList:
            recommendationList = []

        def prepVisit(date, personId, isAmb=True):
            sceneId = None if isAmb else QtGui.qApp.db.translate('rbScene', 'code', '2', 'id')
            visit = self.modelVisits.getEmptyRecord(sceneId=sceneId, personId=personId)
            visit.setValue('date', toVariant(date))
            return visit

        self.cmbResult.setTable('rbResult', True)
        self.eventSetDateTime = eventSetDatetime
        self.eventDate = eventDatetime
        self.setOrgId(orgId if orgId else QtGui.qApp.currentOrgId())
        self.setClientId(clientId)
        self.clientId = clientId
        self.prolongateEvent = True if actionByNewEvent else False
        self.setExternalId(externalId)
        self.cmbPerson.setValue(personId)
        self.setEventTypeId(eventTypeId)
        self.fillNextDate() # must be after self.setEventTypeId
        self.cmbPrimary.setCurrentIndex(not self.isPrimary(clientId, eventTypeId, personId))
        self.cmbOrder.setCode(forceInt(QtGui.qApp.db.translate('EventType', 'id', eventTypeId, 'defaultOrder')))

        self.updateModelsRetiredList()

        self.tabNotes.setNotesEx(externalId, assistantId, curatorId, relegateOrgId, referrals = referrals)
        self.initFocus()
        self.setRecommendations(recommendationList)

        visitTypeId = presetDiagnostics[0][4] if presetDiagnostics else None
        self.modelVisits.setDefaultVisitTypeId(visitTypeId)
        visits = []

        if isEventLong(eventTypeId) and numDays >= 1:
            i = 0
            availDays = numDays
            while availDays>1:
                date = self.eventSetDateTime.addDays(i).date()
                if date.dayOfWeek()<=5 or includeRedDays:
                    visits.append(prepVisit(date, personId, isAmb))
                    availDays -= 1
                i += 1
            visits.append(prepVisit(self.eventDate, personId, isAmb))
        else:
            if self.eventDate:
                date = self.eventDate
            elif self.eventSetDateTime and self.eventSetDateTime.date():
                date = self.eventSetDateTime.date()
            else:
                date = QtCore.QDate.currentDate()
            visits.append(prepVisit(date, personId, isAmb))
        self.modelVisits.setItems(visits)
        self.updateVisitsInfo()

        if presetDiagnostics:
            for model in [self.modelFinalDiagnostics]:
                for MKB, dispanserId, healthGroupId, medicalGroupId, visitTypeId, goalId, serviceId in presetDiagnostics:
                    item = model.getEmptyRecord()
                    item.setValue('MKB', toVariant(MKB))
                    item.setValue('dispanser_id',   toVariant(dispanserId))
                    item.setValue('healthGroup_id', toVariant(healthGroupId))
                    item.setValue('medicalGroup_id', toVariant(medicalGroupId))
                    model.items().append(item)
                model.reset()
        self.prepareActions(presetActions, disabledActions, actionTypeIdValue, valueProperties, diagnos, financeId, protocolQuoteId, actionByNewEvent)
        if self.isTabTempInvalidEtcAlreadyLoad:
            self.grpTempInvalid.pickupTempInvalid()
            # self.grpAegrotat.pickupTempInvalid()
            self.grpDisability.pickupTempInvalid()
            self.grpVitalRestriction.pickupTempInvalid()
        self.setIsDirty(False)
        self.tabNotes.setEventEditor(self)
        self.tabMes.postSetupUi()
        return self.checkEventCreationRestriction()


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
        self.setOrgStructureId(orgStructureId)
        self.setContract()
        plannerDate = self.getPlannerDate(eventSetDatetime, eventDatetime)
        if QtGui.qApp.userHasRight(urAccessF030planner):
            dlg = CPreF02512Dialog(self, self.contractTariffCache)
            dlg.prepare(clientId, eventTypeId, plannerDate, self.personId, self.personSpecialityId,
                        self.personTariffCategoryId, flagHospitalization, actionTypeIdValue, tissueTypeId,
                        recommendationList, useDiagnosticsAndActionsPresets=useDiagnosticsAndActionsPresets)
            if dlg.diagnosticsTableIsNotEmpty() or dlg.actionsTableIsNotEmpty():
                if not dlg.exec_():
                    return False
            return self._prepare(None, clientId, eventTypeId, orgId, personId, eventSetDatetime, eventDatetime, includeRedDays, numDays, dlg.diagnostics(), dlg.actions(), dlg.disabledActionTypeIdList, externalId, assistantId, curatorId, actionTypeIdValue, valueProperties, relegateOrgId, diagnos, financeId, protocolQuoteId, actionByNewEvent, referrals=referrals, isAmb=isAmb, recommendationList=recommendationList)
        else:
            presets = CPreF02512DagnosticAndActionPresets(clientId, eventTypeId, plannerDate, self.personSpecialityId,
                                                          flagHospitalization, actionTypeIdValue, recommendationList,
                                                          useDiagnosticsAndActionsPresets=useDiagnosticsAndActionsPresets)
            return self._prepare(None, clientId, eventTypeId, orgId, personId, eventSetDatetime, eventDatetime, includeRedDays, numDays,
                                 presets.unconditionalDiagnosticList, presets.unconditionalActionList, presets.disabledActionTypeIdList,
                                 externalId, assistantId, curatorId, None, [], relegateOrgId, diagnos, financeId, protocolQuoteId, actionByNewEvent,
                                 referrals=referrals, isAmb=isAmb, recommendationList=recommendationList)


    def prepareActions(self, presetActions, disabledActions, actionTypeIdValue, valueProperties, diagnos, financeId, protocolQuoteId, actionByNewEvent):
        def addActionType(actionTypeId, amount, idListActionType, idListActionTypeIPH, actionFinance, idListActionTypeMoving, org_id):
            for model in [self.tabStatus.modelAPActions,
                          self.tabDiagnostic.modelAPActions,
                          self.tabCure.modelAPActions,
                          self.tabMisc.modelAPActions]:
                if actionTypeId in model.actionTypeIdList:
                    if actionTypeId in idListActionType and not actionByNewEvent:
                        model.addRow(actionTypeId, amount)
                        record, action = model.items()[-1]
                        record.setValue('org_id', toVariant(org_id))
                        if valueProperties and len(valueProperties) > 0 and valueProperties[0]:
                            action[u'Направлен в отделение'] = valueProperties[0]
                        if protocolQuoteId:
                            action[u'Квота'] = protocolQuoteId
                        if actionFinance == 0:
                            record.setValue('finance_id', toVariant(financeId))
                    elif actionTypeId in idListActionTypeIPH:
                        model.addRow(actionTypeId, amount)
                        record, action = model.items()[-1]
                        record.setValue('org_id', toVariant(org_id))
                        if diagnos:
                            record, action = model.items()[-1]
                            action[u'Диагноз'] = diagnos
                    #[self.eventActionFinance, self.receivedFinanceId, orgStructureTransfer, orgStructurePresence, oldBegDate, movingQuoting, personId]
                    elif actionByNewEvent and actionTypeId in idListActionTypeMoving:
                        model.addRow(actionTypeId, amount)
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
                        model.addRow(actionTypeId, amount)
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
                for actionTypeId, amount, cash, _ in presetActions:
                    if actionTypeId in idListActionTypeMoving:
                        actionTypeMoving = True
                        break
                if not actionTypeMoving and idListActionTypeMoving:
                    presetActions.append((idListActionTypeMoving[0], 1.0, False, None))
            for actionTypeId, amount, cash, org_id in presetActions:
                addActionType(actionTypeId, amount, idListActionType, idListActionTypeIPH, actionFinance, idListActionTypeMoving, org_id)


    def setLeavedAction(self, actionTypeIdValue):
        currentDateTime = QtCore.QDateTime.currentDateTime()
        flatCode = u'moving%'
        db = QtGui.qApp.db
        tableActionType = db.table('ActionType')
        idListActionType = db.getIdList(tableActionType, [tableActionType['id']], [tableActionType['flatCode'].like(flatCode), tableActionType['deleted'].eq(0)])
        for model in [self.tabStatus.modelAPActions,
                      self.tabDiagnostic.modelAPActions,
                      self.tabCure.modelAPActions,
                      self.tabMisc.modelAPActions]:
            if actionTypeIdValue in model.actionTypeIdList:
                orgStructureLeaved = None
                movingQuoting = None
                orgStructureMoving = False
                for record, action in model.items():
                    actionTypeId = forceRef(record.value('actionType_id'))
                    if actionTypeId in idListActionType:
                        if not forceDate(record.value('endDate')):
                            record.setValue('endDate', toVariant(currentDateTime))
                            record.setValue('status', toVariant(2))
                        actionType = CActionTypeCache.getById(actionTypeId) if actionTypeId else None
                        if u'moving' in actionType.flatCode.lower():
                            orgStructureMoving = True
                            orgStructurePresence = action[u'Отделение пребывания']
                            orgStructureTransfer = action[u'Переведен в отделение']
                            movingQuoting = action[u'Квота'] if action.getType().containsPropertyWithName(u'Квота') else None
                            if not orgStructureTransfer and orgStructurePresence:
                                orgStructureLeaved = orgStructurePresence
                        else:
                            orgStructureLeaved = None
                            movingQuoting = None
                        amount = actionType.amount
                        if actionTypeId:
                            if not(amount and actionType.amountEvaluation == CActionType.userInput):
                                amount = model.getDefaultAmountEx(actionType, record, None)
                        else:
                            amount = 0
                        record.setValue('amount', toVariant(amount))
                        model.updateActionAmount(len(model.items())-1)
                model.addRow(actionTypeIdValue)
                record, action = model.items()[-1]
                if not orgStructureLeaved and not orgStructureMoving:
                    currentOrgStructureId = QtGui.qApp.currentOrgStructureId()
                    if currentOrgStructureId:
                        typeRecord = QtGui.qApp.db.getRecordEx('OrgStructure', 'type', 'id = %d AND type = 4 AND deleted = 0'%(currentOrgStructureId))
                        if typeRecord and (typeRecord.value('type')) == 4:
                            orgStructureLeaved = currentOrgStructureId
                if orgStructureLeaved and action.getType().containsPropertyWithName(u'Отделение'):
                    action[u'Отделение'] = orgStructureLeaved
                if action.getType().containsPropertyWithName(u'Квота') and movingQuoting:
                    action[u'Квота'] = movingQuoting
                record.setValue('begDate', toVariant(currentDateTime))
                record.setValue('endDate', toVariant(currentDateTime))
                record.setValue('status', toVariant(2))
                model.updateActionAmount(len(model.items())-1)
                self.edtEndDate.setDate(currentDateTime.date() if isinstance(currentDateTime, QtCore.QDateTime) else QtCore.QDate())
                self.edtEndTime.setTime(currentDateTime.time() if isinstance(currentDateTime, QtCore.QDateTime) else QtCore.QTime())


    def initFocus(self):
        if self.cmbContract.count() != 1:
            self.cmbContract.setFocus(QtCore.Qt.OtherFocusReason)
        else:
            self.tblFinalDiagnostics.setFocus(QtCore.Qt.OtherFocusReason)


#    def newDiagnosticRecord(self, template):
#        result = self.tblFinalDiagnostics.model().getEmptyRecord()
#        return result


    def setRecord(self, record):
        self.cmbResult.setTable('rbResult', True)
        CEventEditDialog.setRecord(self, record)
        setDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'setDate')
        setRBComboBoxValue(self.cmbPerson,      record, 'setPerson_id')
        setDatetimeEditValue(self.edtEndDate, self.edtEndTime, record, 'execDate')
        setRBComboBoxValue(self.cmbPerson,      record, 'execPerson_id')
        setRBComboBoxValue(self.cmbResult,      record, 'result_id')
        setDateEditValue(self.edtNextDate,      record, 'nextEventDate')
        self.cmbPrimary.setCurrentIndex(forceInt(record.value('isPrimary')) - 1)
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
        self.loadDiagnostics(self.modelFinalDiagnostics, self.itemId())
        self.updateResultFilter()
        self.loadVisits()
        if self.isTabTempInvalidEtcAlreadyLoad:
            self.grpTempInvalid.pickupTempInvalid()
            # self.grpAegrotat.pickupTempInvalid()
            self.grpDisability.pickupTempInvalid()
            self.grpVitalRestriction.pickupTempInvalid()
        self.loadActions()
        self.updateMesMKB()
        self.tabMes.setBegDate(forceDate(record.value('setDate')))
        self.tabMes.setEndDate(forceDate(record.value('execDate')))
        self.tabMes.setRecord(record)
        self.tabCash.load(self.itemId())
        self.tabNotes.setNotes(record)
        self.tabNotes.setEventEditor(self)
        self.initFocus()
        self.setIsDirty(False)
        self.blankMovingIdList = []
        payStatus = self.getEventPayStatus()
        self.addPayStatusBar(payStatus)
        self.setEditable(self.getEditable())
        setOrgStructureIdToCmbPerson(self.cmbPerson)


    def setEditable(self, editable):
        self.modelVisits.setEditable(editable)
        self.modelActionsSummary.setEditable(editable)
        self.modelFinalDiagnostics.setEditable(editable or QtGui.qApp.userHasRight(urEditDiagnosticsInPayedEvents))
        self.grpBase.setEnabled(editable)
        self.tabMes.setEnabled(editable)
        self.tabStatus.setEditable(editable)
        self.tabDiagnostic.setEditable(editable)
        self.tabCure.setEditable(editable)
        self.tabMisc.setEditable(editable)
        #tabTempInvalidEtc
        self.grpDisability.setEnabled(editable)
        self.grpVitalRestriction.setEnabled(editable)
        self.tabTempInvalid.setEnabled(editable)
        # self.tabAegrotat.setEnabled(editable)
        self.tabTempinvalidS.setEnabled(editable)
        self.tabTempInvalidDisability.setEnabled(editable)
        #end of tabTempInvalidEtc
        self.tabCash.setEditable(editable)
        self.tabNotes.setEditable(editable)

    def loadVisits(self):
        self.modelVisits.loadItems(self.itemId())
        self.updateVisitsInfo()


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
            self.createDiagnostics(eventId)


    def createDiagnostics(self, eventId):
        if eventId:
            self.loadDiagnostics(self.modelFinalDiagnostics, eventId)


    def loadDiagnostics(self, modelDiagnostics, eventId):
        db = QtGui.qApp.db
        table = db.table('Diagnostic')
        isDiagnosisManualSwitch = modelDiagnostics.manualSwitchDiagnosis()
        rawItems = db.getRecordList(table, '*', [table['deleted'].eq(0), table['event_id'].eq(eventId), modelDiagnostics.filter], 'id')
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
        eventId = self.itemId()
        self.tabStatus.loadActionsLite(eventId)
        self.tabDiagnostic.loadActionsLite(eventId)
        self.tabCure.loadActionsLite(eventId)
        self.tabMisc.loadActionsLite(eventId)
        self.modelActionsSummary.regenerate()
        self.tabCash.modelAccActions.regenerate()


    def getRecord(self):
        record = CEventEditDialog.getRecord(self)
        showTime = getEventShowTime(self.eventTypeId)
#перенести в exec_ в случае успеха или в accept?
        #atronah: такая конструкция выбрана по причине необходимости сохранить логику при наследовании от этого класса
        #если писать в self., то будет создана независимая от классовой переменная, а если в класс, то наследник не будет иметь своих эксемпляров переменной

        getRBComboBoxValue(self.cmbContract,    record, 'contract_id')
#        getDateEditValue(self.edtPrevDate,      record, 'prevEventDate')
        getDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'setDate', showTime)
        getRBComboBoxValue(self.cmbPerson,      record, 'setPerson_id')
        getDatetimeEditValue(self.edtEndDate, self.edtEndTime, record, 'execDate', showTime)
        getRBComboBoxValue(self.cmbPerson,      record, 'execPerson_id')
        getRBComboBoxValue(self.cmbResult,      record, 'result_id')
        getDateEditValue(self.edtNextDate,      record, 'nextEventDate')
        record.setValue('isPrimary', toVariant(self.cmbPrimary.currentIndex() + 1))
        if self.prolongateEvent:
            record.setValue('order', toVariant(5))
            record.setValue('prevEvent_id', toVariant(self.prevEventId))
        # getComboBoxValue(self.cmbOrder,         record, 'order')
        record.setValue('order', toVariant(self.cmbOrder.code()))
###  payStatus
        self.tabNotes.getNotes(record, self.eventTypeId)
        return record


    def saveInternals(self, eventId):
        super(CF02512Dialog, self).saveInternals(eventId)
        self.saveVisits(eventId)
        self.saveDiagnostics(self.modelFinalDiagnostics, eventId)
        setAskedClassValueForDiagnosisManualSwitch(None)
        if self.isTabTempInvalidEtcAlreadyLoad:
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
#        financeIdVariant = QtGui.qApp.db.translate('Person', 'id', personIdVariant, 'finance_id')

        for item in items :
            if not forceRef(item.value('person_id')):
                item.setValue('person_id', personIdVariant)
            if not forceDate(item.value('date')):
                item.setValue('date', toVariant(self.eventSetDateTime))
#            item.setValue('finance_id', financeIdVariant)
        self.modelVisits.saveItems(eventId)


    def saveDiagnostics(self, modelDiagnostics, eventId):
        items = modelDiagnostics.items()
        isDiagnosisManualSwitch = modelDiagnostics.manualSwitchDiagnosis()
        begDate = self.edtBegDate.date()
        endDate = self.edtEndDate.date()
        date = endDate if endDate else begDate
        MKBDiagnosisIdPairList = []
        prevId=0
        for item in items:
            MKB   = forceString(item.value('MKB'))
            MKBEx = forceString(item.value('MKBEx'))
            TNMS  = forceString(item.value('TNMS'))
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
                morphologyMKB=morphologyMKB,
                newSetDate=begDate)
            item.setValue('diagnosis_id', toVariant(diagnosisId))
            item.setValue('TNMS', toVariant(TNMS))
            item.setValue('character_id', toVariant(characterId))
            itemId = forceInt(item.value('id'))
            if prevId>itemId:
                item.setValue('id', QtCore.QVariant())
                prevId=0
            else :
                prevId=itemId
            MKBDiagnosisIdPairList.append((MKB, diagnosisId))
        modelDiagnostics.saveItems(eventId)
        self.modifyDiagnosises(MKBDiagnosisIdPairList)


    def getFinalDiagnosisMKB(self):
        MKB, MKBEx = self.modelFinalDiagnostics.getFinalDiagnosisMKB()
        return MKB, MKBEx


    def getFinalDiagnosisId(self):
        typeId = self.modelFinalDiagnostics.getFinalDiagnosisId()
        return typeId

    def getFinalDiagnostic(self):
        return self.getModelFinalDiagnostics().getFinalDiagnosis()

    def saveActions(self, eventId):
        self.tabStatus.saveActions(eventId)
        self.tabDiagnostic.saveActions(eventId)
        self.tabCure.saveActions(eventId)
        self.tabMisc.saveActions(eventId)


    def setOrgId(self, orgId):
        self.orgId = orgId
        self.cmbContract.setOrgId(orgId)
        self.cmbPerson.setOrgId(orgId)
        if self.isTabStatusAlreadyLoad:
            self.tabStatus.setOrgId(orgId)
        if self.isTabDiagnosticAlreadyLoad:
            self.tabDiagnostic.setOrgId(orgId)
        if self.isTabCureAlreadyLoad:
            self.tabCure.setOrgId(orgId)
        if self.isTabMiscAlreadyLoad:
            self.tabMisc.setOrgId(orgId)


    def setExternalId(self, externalId):
        self.lblValueExternalId.setText((u'Внешний идентификатор: ' + externalId) if externalId else '')


    def setEventTypeId(self, eventTypeId):
        CEventEditDialog.setEventTypeId(self, eventTypeId, self.formTitle)
        self.tabCash.windowTitle = self.windowTitle()
        showTime = getEventShowTime(eventTypeId)
        self.edtBegTime.setVisible(showTime)
        self.edtEndTime.setVisible(showTime)
        if self.cmbResult.value() is None:
            if self.inheritResult == True:
                self.cmbResult.setValue(self.defaultEventResultId.get(self.eventPurposeId))
        self.updateResultFilter()
        self.setVisitAssistantVisible(self.tblVisits, hasEventVisitAssistant(eventTypeId))
        customizePrintButton(self.btnPrint, self.eventContext if self.eventContext else 'F02512')
        self.diagnosisSetDateVisible = forceBool(getDiagnosisSetDateVisible(eventTypeId))
        if self.diagnosisSetDateVisible == False:
            self.tblFinalDiagnostics.setColumnHidden(4, True)

    def updateMKB(self):
        begDate = self.edtBegDate.date()
        filter = None
        if begDate.isValid():
            filter = {'begDate': begDate, 'clientId': self.clientId}
        cols = self.modelFinalDiagnostics.cols()
        resultCol = cols[2]
        resultCol.setFilter(filter)

    def resetActionTemplateCache(self):
        self.tabStatus.actionTemplateCache.reset()
        self.tabDiagnostic.actionTemplateCache.reset()
        self.tabCure.actionTemplateCache.reset()
        self.tabMisc.actionTemplateCache.reset()


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


    def checkDataEntered(self):
        result = CEventEditDialog.checkDataEntered(self)
        self.blankMovingIdList = []
        begDate = self.edtBegDate.date()
        endDate = self.edtEndDate.date() if self._isClosedEventCheck else QtCore.QDate()
        nextDate = self.edtNextDate.date()
        result = result and (self.orgId != QtGui.qApp.currentOrgId() or self.cmbContract.value() or self.checkInputMessage(u'договор', False, self.cmbContract))
        result = result and (self.cmbPerson.value()   or self.checkInputMessage(u'врача',        False, self.cmbPerson))
        result = result and (not begDate.isNull() or self.checkInputMessage(u'дату назначения', False, self.edtBegDate))
#        result = result and (not endDate.isNull() or self.checkInputMessage(u'дату выполнения', False, self.edtEndDate))
        if endDate.isNull():
            result = result and self.checkEventDate(begDate, endDate, nextDate, self.tabToken, self.edtNextDate,  self.edtEndDate, True)
        else:
#            maxEndDate = self.getMaxEndDateByVisits()
#            if not maxEndDate.isNull():
#                if QtGui.QMessageBox.question(self,
#                                    u'Внимание!',
#                                    u'Дата выполнения обращения не указана.\nУстановить дату завершения по максимальной дате посещений',
#                                    QtGui.QMessageBox.No|QtGui.QMessageBox.Yes,
#                                    QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
#                    self.edtEndDate.setDate(maxEndDate)
#                    endDate = maxEndDate
            result = result and self.checkActionDataEntered(begDate, QtCore.QDate(), endDate, self.tabToken, self.edtBegDate, None, self.edtEndDate)
            result = result and self.checkEventDate(begDate, endDate, nextDate, self.tabToken, self.edtNextDate,  self.edtEndDate, True)
            minDuration,  maxDuration = getEventDuration(self.eventTypeId)
            if minDuration <= maxDuration:
                countRedDays = not QtGui.qApp.isExcludeRedDaysInEventLength()
                eventDuration = getEventLengthDays(begDate, endDate, countRedDays, self.eventTypeId)
                eventDurationErrorString = u'Указана длительность с учётом выходных: %s.'%formatNum(eventDuration, (u'день', u'дня', u'дней'))
                result = result and (eventDuration >= minDuration or
                                     self.checkValueMessage(u'Длительность должна быть не менее %s. %s'%(formatNum(minDuration, (u'дня', u'дней', u'дней')), eventDurationErrorString), False, self.edtEndDate))
                result = result and (maxDuration==0 or eventDuration <= maxDuration or
                                     self.checkValueMessage(u'Длительность должна быть не более %s. %s'%(formatNum(maxDuration, (u'дня', u'дней', u'дней')), eventDurationErrorString), False, self.edtEndDate))
            # if not QtGui.qApp.userHasRight(urDoNotCheckResultAndMKB):
            #    result = result and (self.cmbResult.value()  or self.checkInputMessage(u'результат',   False, self.cmbResult))
        result = result and self.checkDiagnosticsDataEntered([(self.tblFinalDiagnostics, True, True, endDate)], 
                                                             endDate)
#            result = result and self.checkActionsDataEntered(begDate, endDate)
        result = result and self.checkActionsDateEnteredActuality(begDate, endDate, [self.tabStatus, self.tabDiagnostic, self.tabCure, self.tabMisc])
        result = result and self.checkActionsDataEntered([self.tabStatus, self.tabDiagnostic, self.tabCure, self.tabMisc], begDate, endDate)
        result = result and (len(self.modelVisits.items())>0 or self.checkInputMessage(u'посещение', False, self.tblVisits))
        result = result and self.checkVisitsDataEntered(begDate, endDate)
        if self.isTabTempInvalidEtcAlreadyLoad:
            result = result and self.grpTempInvalid.checkTempInvalidDataEntered()
            # result = result and self.grpAegrotat.checkTempInvalidDataEntered()
            result = result and self.grpDisability.checkTempInvalidDataEntered()
            result = result and self.grpVitalRestriction.checkTempInvalidDataEntered()
        if self.isTabCashAlreadyLoad:
            result = result and self.tabCash.checkDataLocalContract()
        result = result and self.checkSerialNumberEntered()
        result = result and self.checkTabNotesReferral()

        if \
                self.getFinalDiagnosisMKB()[0] is not None and self.getFinalDiagnosisMKB()[0] != u'' and self.getFinalDiagnosisMKB()[0][0] == u'C' \
                and not QtGui.qApp.userHasRight(urOncoDiagnosisWithoutTNMS)\
                and QtGui.qApp.isTNMSVisible() and (self.getModelFinalDiagnostics().getFinalDiagnosis().value('TNMS') is None or
                                forceString(self.getModelFinalDiagnostics().getFinalDiagnosis().value('TNMS')) == ''):
            result = result and self.checkValueMessage(check_data_text_TNM, False, None)

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
#        if endDate and not (len(self.modelFinalDiagnostics.items()) > 0 and self.checkDiagnosticsType()):
#            self.checkInputMessage(u'диагноз', False, self.tblFinalDiagnostics)
#            return False
#        
#        for table, modelName in [(self.tblPreliminaryDiagnostics, u'предварительный'), (self.tblFinalDiagnostics, u'заключительный')]:
#            for row, record in enumerate(table.model().items()):
#                if not self.checkDiagnosticDataEntered(table, modelName, row, record):
#                    return False
#        return True


#    def checkDiagnosticsType(self):
#        result = True
#        endDate = self.edtEndDate.date()
#        if endDate:
#            result = result and self.checkDiagnosticsTypeEnd(self.modelFinalDiagnostics) or self.checkValueMessage(u'Необходимо указать заключительный диагноз', False, self.tblFinalDiagnostics)
#        return result
#
#
#    def checkDiagnosticsTypeEnd(self, model):
#        for record in model.items():
#            if  forceInt(record.value('diagnosisType_id')) == model.diagnosisTypeCol.ids[0]:
#                return True
#        return False


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
#        if result and row == 0 and table != self.tblPreliminaryDiagnostics:
#            resultId = forceRef(record.value('result_id'))
#            result = resultId or self.checkInputMessage(u'результат', False, table, row, record.indexOf('result_id'))
#        return result


#    def checkActionsDataEntered(self, begDate, endDate):
#        for row, record in enumerate(self.modelActions.items()):
#            if not self.checkActionDataEntered(begDate, endDate, row, record):
#                return False
#        return True


    def getVisitCount(self):
        return len(self.modelVisits.items())

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

    def getDiagnosisTypeId(self, dt):
        return forceRef(QtGui.qApp.db.translate('rbDiagnosisType', 'code', '2' if dt else '9', 'id'))

    def getEventInfo(self, context):
        if not self.isTabCashAlreadyLoad:
            self.initTabCash(False)
        result = CEventEditDialog.getEventInfo(self, context)
        # ручная инициализация свойств
        result._isPrimary = self.cmbPrimary.currentIndex() + 1
        # ручная инициализация таблиц
        result._actions = CActionInfoProxyList(context,
                [self.tabStatus.modelAPActions, self.tabDiagnostic.modelAPActions, self.tabCure.modelAPActions, self.tabMisc.modelAPActions],
                result)
        result._diagnosises = CDiagnosticInfoProxyList(context, [self.modelFinalDiagnostics])
        result._visits = CVisitInfoProxyList(context, self.modelVisits)
        return result


    def getTempInvalidInfo(self, context):
        return self.grpTempInvalid.getTempInvalidInfo(context)

    # def getAegrotatInfo(self, context):
    #     return self.grpAegrotat.getTempInvalidInfo(context)

    def updateVisitsByDiagnostics(self, diagnosticsModel):
        personIdList = diagnosticsModel.getPersonsWithSignificantDiagnosisType()
        self.modelVisits.addAbsentPersons(personIdList, self.eventDate)
        self.updateVisitsInfo()

    def updateMesMKB(self):
        MKB = self.getFinalDiagnosisMKB()[0]
        self.tabMes.setMKB(MKB)
        MKB2List = self.getRelatedDiagnosisMKB()
        self.tabMes.setMKB2([r[0] for r in MKB2List])


    def addPayStatusBar(self,  payStatus):
        self.statusBar.addPermanentWidget(QtGui.QLabel(payStatusText(payStatus)))

    def initTabMes(self, show=True):
        if show: self.tabMes.setVisible(False)
        self.tabMes.postSetupUi()
        if show: self.tabMes.setVisible(True)

        self.isTabMesAlreadyLoad = True

    def initTabStatus(self, show=True):
        if show: self.tabStatus.setVisible(False)
        self.tabStatus.preSetupUi()
        self.tabStatus.clearBeforeSetupUi()
        self.tabStatus.setupUi(self.tabStatus)
        self.tabStatus.postSetupUi()
        self.tabStatus.updateActionEditor()
        self.tabStatus.setOrgId(self.orgId)
        self.tabStatus.setEndDate(self.eventSetDateTime.date())
        if show: self.tabStatus.setVisible(True)

        self.isTabStatusAlreadyLoad = True

    def initTabDiagnostic(self, show=True):
        if show: self.tabDiagnostic.setVisible(False)
        self.tabDiagnostic.preSetupUi()
        self.tabDiagnostic.clearBeforeSetupUi()
        self.tabDiagnostic.setupUi(self.tabDiagnostic)
        self.tabDiagnostic.postSetupUi()
        self.tabDiagnostic.updateActionEditor()
        self.tabDiagnostic.setOrgId(self.orgId)
        self.tabDiagnostic.setEndDate(self.eventSetDateTime.date())
        if show: self.tabDiagnostic.setVisible(True)

        self.isTabDiagnosticAlreadyLoad = True

    def initTabCure(self, show=True):
        if show: self.tabCure.setVisible(False)
        self.tabCure.preSetupUi()
        self.tabCure.clearBeforeSetupUi()
        self.tabCure.setupUi(self.tabCure)
        self.tabCure.postSetupUi()
        self.tabCure.updateActionEditor()
        self.tabCure.setOrgId(self.orgId)
        self.tabCure.setEndDate(self.eventSetDateTime.date())
        if show: self.tabCure.setVisible(True)

        self.isTabCureAlreadyLoad = True

    def initTabMisc(self, show=True):
        if show: self.tabMisc.setVisible(False)
        self.tabMisc.preSetupUi()
        self.tabMisc.clearBeforeSetupUi()
        self.tabMisc.setupUi(self.tabMisc)
        self.tabMisc.postSetupUi()
        self.tabMisc.updateActionEditor()
        self.tabMisc.setOrgId(self.orgId)
        self.tabMisc.setEndDate(self.eventSetDateTime.date())
        if show: self.tabMisc.setVisible(True)

        self.isTabMiscAlreadyLoad = True

    def initTabAmbCard(self, show=True):
        if show: self.tabAmbCard.setVisible(False)
        self.tabAmbCard.preSetupUi()
        self.tabAmbCard.setupUi(self.tabAmbCard)
        self.tabAmbCard.postSetupUi()
        self.tabAmbCard.setClientId(self.clientId)
        if show: self.tabAmbCard.setVisible(True)

        self.isTabAmbCardAlreadyLoad = True

    def initTabTempInvalidEtc(self, show=True):
        if show: self.tabTempInvalidEtc.setVisible(False)

        # self.tabTempInvalidAndAegrotat.setCurrentIndex(1 if QtGui.qApp.tempInvalidDoctype() == '2' else 0)
        self.grpTempInvalid.setEventEditor(self)
        self.grpTempInvalid.setType(0, '1')
        # self.grpAegrotat.setEventEditor(self)
        # self.grpAegrotat.setType(0, '2')
        self.grpDisability.setEventEditor(self)
        self.grpDisability.setType(1)
        self.grpVitalRestriction.setEventEditor(self)
        self.grpVitalRestriction.setType(2)

        self.grpTempInvalid.pickupTempInvalid()
        # self.grpAegrotat.pickupTempInvalid()
        self.grpDisability.pickupTempInvalid()
        self.grpVitalRestriction.pickupTempInvalid()
        if show: self.tabTempInvalidEtc.setVisible(True)

        self.isTabTempInvalidEtcAlreadyLoad = True

    def initTabCash(self, show=True):
        if show: self.tabCash.setVisible(False)
        self.tabCash.preSetupUi()
        self.tabCash.clearBeforeSetupUi()
        self.tabCash.setupUi(self.tabCash)
        self.tabCash.postSetupUi()
        self.tabCash.isControlsCreate = True
        self.tabCash.loadLocalContract(self.itemId())
        self.tabCash.setUpdatePaymentsSum()
        if show: self.tabCash.setVisible(True)

        self.isTabCashAlreadyLoad = True

    def initTabNotes(self, show=True):
        if show: self.tabNotes.setVisible(False)
        self.tabNotes.postSetupUi()
        if show: self.tabNotes.setVisible(True)

        self.isTabNotesAlreadyLoad = True


    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        contractId = self.cmbContract.value()
        self.cmbContract.setBegDate(date)
        self.cmbContract.setEndDate(date)
        self.cmbContract.setValue(contractId)
        self.cmbPerson.setEndDate(date)
        if self.isTabStatusAlreadyLoad:
            self.tabStatus.setEndDate(date)
        if self.isTabDiagnosticAlreadyLoad:
            self.tabDiagnostic.setEndDate(date)
        if self.isTabCureAlreadyLoad:
            self.tabCure.setEndDate(date)
        if self.isTabMiscAlreadyLoad:
            self.tabMisc.setEndDate(date)
        self.tabNotes.updateReferralPeriod(date)

        self.updateModelsRetiredList()

        self.updateResultFilter()
        if QtGui.qApp.isCheckMKB():
            self.updateMKB()
        self.emitUpdateActionsAmount()
        self.setContract()

        self.tabMes.setBegDate(date)

    @QtCore.pyqtSlot(QtCore.QTime)
    def on_edtBegTime_timeChanged(self, time):
        self.emitUpdateActionsAmount()

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtEndDate_dateChanged(self, date):
        self.emitUpdateActionsAmount()
        self.setContract()

        self.tabMes.setEndDate(date)
        self.tabNotes.cmbClientPolicy.updatePolicy(date)
        if QtGui.qApp.isAutoClosed():
            self.chkIsClosed.setChecked(date != QtCore.QDate())

    @QtCore.pyqtSlot(int)
    def on_cmbPerson_currentIndexChanged(self):
        oldPersonId = self.personId
        self.setPersonId(self.cmbPerson.value())
# что-то сомнительным показалось - ну поменяли отв. врача,
# всё равно менять врачей в действии вроде неправильно. или правильно?
        self.tabStatus.updatePersonId(oldPersonId, self.personId)
        self.tabDiagnostic.updatePersonId(oldPersonId, self.personId)
        self.tabCure.updatePersonId(oldPersonId, self.personId)
        self.tabMisc.updatePersonId(oldPersonId, self.personId)
#        self.grpTempInvalid.pickupTempInvalid()
#        self.grpAegrotat.pickupTempInvalid()
#        self.grpDisability.pickupTempInvalid()
#        self.grpVitalRestriction.pickupTempInvalid()

    @QtCore.pyqtSlot()
    def on_modelFinalDiagnostics_diagnosisChanged(self):
        self.updateVisitsByDiagnostics(self.sender())
        self.updateMesMKB()

    @QtCore.pyqtSlot()
    def on_modelFinalDiagnostics_resultChanged(self):
        CEventEditDialog.defaultDiagnosticResultId[self.eventPurposeId] = self.modelFinalDiagnostics.resultId()
        self.updateResultFilter()
        # if self.cmbResult.value() is None:
        #     self.cmbResult.setValue(getEventResultId(CEventEditDialog.defaultDiagnosticResultId.get(self.eventPurposeId)))

    @QtCore.pyqtSlot(QtCore.QString)
    def on_modelFinalDiagnostics_significantMKBPresent(self, MKB):
        self.modelVisits.fillEmptyMKB(MKB)
        self.modelVisits.setDefaultMKB(MKB)

    @QtCore.pyqtSlot()
    def on_actDiagnosticsAddAccomp_triggered(self):
        currentRow = self.tblFinalDiagnostics.currentIndex().row()
        if currentRow>=0 :
            currentRecord = self.modelFinalDiagnostics.items()[currentRow]
            newRecord = self.modelFinalDiagnostics.getEmptyRecord()
            newRecord.setValue('diagnosisType', QtCore.QVariant(self.__class__.dfAccomp))
            newRecord.setValue('speciality_id', currentRecord.value('speciality_id'))
            newRecord.setValue('healthGroup_id', currentRecord.value('healthGroup_id'))
            self.modelFinalDiagnostics.insertRecord(currentRow+1, newRecord)
            self.tblFinalDiagnostics.setCurrentIndex(self.modelFinalDiagnostics.index(currentRow+1, newRecord.indexOf('MKB')))

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

    @QtCore.pyqtSlot(int)
    def on_modelActionsSummary_currentRowMovedTo(self, row):
        self.tblActions.setCurrentIndex(self.modelActionsSummary.index(row, 0))

    @QtCore.pyqtSlot(int)
    def on_btnPrint_printByTemplate(self, templateId):
        if self.beforePrintTemplate(templateId) == -1:
            return
        context = CInfoContext()
        if not self.isTabTempInvalidEtcAlreadyLoad:
            self.initTabTempInvalidEtc(False)
        if not self.isTabCashAlreadyLoad:
            self.initTabCash(False)
        eventInfo = self.getEventInfo(context)
        tempInvalidInfo = self.getTempInvalidInfo(context)
        # aegrotatInfo = self.getAegrotatInfo(context)

        data = { 'event' : eventInfo,
                 'client': eventInfo.client,
                 'tempInvalid': tempInvalidInfo,
                 # 'aegrotat': aegrotatInfo
               }
        data['templateCounterValue'] = self.oldTemplates.get(templateId, '')
        applyTemplate(self, templateId, data)

    @QtCore.pyqtSlot(int)
    def on_cmbResult_currentIndexChanged(self):
        self.modelFinalDiagnostics.setFinalResult(getResultIdByDiagnosticResultId(self.cmbResult.value()))


class CF02512BaseDiagnosticsModel(CInDocTableModel):
    __pyqtSignals__ = ('diagnosisChanged()',
                      )
    MKB_allowed_morphology = ['C', 'D']

    def __init__(self, parent, finishDiagnosisTypeCode, baseDiagnosisTypeCode, accompDiagnosisTypeCode, complicDiagnosisTypeCode):
        CInDocTableModel.__init__(self, 'Diagnostic', 'id', 'event_id', parent)
        self._parent = parent
        self.isManualSwitchDiagnosis = QtGui.qApp.defaultIsManualSwitchDiagnosis()
        self.isMKBMorphology = QtGui.qApp.defaultMorphologyMKBIsVisible()
        self.setEditable(True)
        self.characterIdForHandleDiagnosis = None
        self.columnHandleDiagnosis = None
        self.diagnosisTypeCol = CF02512DiagnosisTypeCol( u'Тип', 'diagnosisType_id', 2, [finishDiagnosisTypeCode, baseDiagnosisTypeCode, accompDiagnosisTypeCode, complicDiagnosisTypeCode], smartMode=False)
        self.addCol(self.diagnosisTypeCol)
        self.colPerson = self.addCol(CActionPersonInDocTableColSearch(     u'Врач',            'person_id',  20, 'vrbPersonWithSpeciality', order = 'name', parent=parent))
        self.addExtCol(CICDExInDocTableCol(u'МКБ',         'MKB',   7), QtCore.QVariant.String)
        self.addExtCol(CICDExInDocTableCol(u'МКБ первич',     'MKBEx', 7), QtCore.QVariant.String)
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

        #self.addCol(CDiseasePhases(        u'Фаза',        'phase_id',       7, showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(u'Фаза')
        #self.addCol(CDiseaseStage(         u'Ст',          'stage_id',       7, showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(u'Стадия')
        self.addCol(CRBInDocTableCol(    u'ДН',            'dispanser_id',   7, 'rbDispanser', showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(u'Диспансерное наблюдение')
#        self.addCol(CRBLikeEnumInDocTableCol(u'Госп',      'hospital',       7, CHospitalInfo.names, showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(u'Потребность в госпитализации')
        #self.addCol(CRBInDocTableCol(    u'Травма',        'traumaType_id', 10, 'rbTraumaType', addNone=True, showFields=CRBComboBox.showName, prefferedWidth=150))
        #self.addCol(CRBInDocTableCol(    u'ГрЗд',          'healthGroup_id', 7, 'rbHealthGroup', addNone=True, showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(u'Группа здоровья')
        self.setFilter(self.table['diagnosisType_id'].inlist([typeId for typeId in self.diagnosisTypeCol.ids if typeId]))

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
                    if not (bool(mkb) and mkb[0] in CF02512BaseDiagnosticsModel.MKB_allowed_morphology):
                        result = (result & ~QtCore.Qt.ItemIsEditable)
        if not self.isEditable():
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
        self.updateRetiredList()
        if not variantEq(self.data(index, role), value):
            eventEditor = QtCore.QObject.parent(self)
            if column == 0: # тип диагноза
                result = CInDocTableModel.setData(self, index, value, role)
                if result:
                    self.updateDiagnosisType(set([row]))
                    self.emitDiagnosisChanged()
                return result
            elif column == 1: # врач
                personId = forceRef(value)
                if not eventEditor.checkClientAttendaceEE(personId):
                    return False
                result = CInDocTableModel.setData(self, index, value, role)
                if result:
                    self.updateDiagnosisType(set())
                    self.emitDiagnosisChanged()
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
                    self.emitDiagnosisChanged()
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

    def updateDiagnosisType(self, changedRowSet):
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
            # Список типов диагнозов (их id) использованные текущей персоной в списке измененных строк changedRowSet
            usedDiagnosisTypeIds = [diagnosisTypeIds[row] for row in changedRowSet.intersection(set(rows))]
            listChangedRowSet = [row for row in changedRowSet.intersection(set(rows))]

            if (((self.diagnosisTypeCol.ids[0] in usedDiagnosisTypeIds) #закл диагноз есть среди использованных персоной в измененных строках
                 or (self.diagnosisTypeCol.ids[0] == diagnosisTypeIds[rows[0]])) #закл диагноз равен первому диагнозу, выставленному этой персоной
                and personId == self._parent.personId): #персона соответствует лечащему врачу
                firstDiagnosisId = self.diagnosisTypeCol.ids[0]
            #закл диагноз есть среди использованных этой персоной в списке измененных строк и текущая персона - не лечащий врач
            elif (self.diagnosisTypeCol.ids[0] in usedDiagnosisTypeIds) and personId != self._parent.personId:
                res = QtGui.QMessageBox.warning(self._parent,
                                           u'Внимание!',
                                           u'Смена заключительного диагноза.\nОтветственный будет заменен на \'%s\'.\nВы подтверждаете изменения?' % (forceString(QtGui.qApp.db.translate('vrbPersonWithSpeciality', 'id', personId, 'name'))),
                                           QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel,
                                           QtGui.QMessageBox.Cancel)
                if res == QtGui.QMessageBox.Ok:
                    self._parent.personId = personId
                    self._parent.cmbPerson.setValue(self._parent.personId)
                    firstDiagnosisId = self.diagnosisTypeCol.ids[0]
                    rowEndPersonId = mapPersonIdToRow[endPersonId] if endPersonId else None
                    diagnosisTypeColIdsEnd = -1
                    if rowEndPersonId and len(rowEndPersonId) > 1:
                        for rowPerson in rowEndPersonId:
                            if diagnosisTypeIds[rowPerson] == self.diagnosisTypeCol.ids[1] or diagnosisTypeIds[rowPerson] == self.diagnosisTypeCol.ids[0]:
                                if endRow > -1 and endDiagnosisTypeIds == self.diagnosisTypeCol.ids[0] and endRow != rowPerson:
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
                            if diagnosisTypeIds[rowPerson] == self.diagnosisTypeCol.ids[1] or diagnosisTypeIds[rowPerson] == self.diagnosisTypeCol.ids[0] and (rowPerson not in listChangedRowSet):
                                diagnosisTypeColIdsRows = self.diagnosisTypeCol.ids[2]
                                break
                        if diagnosisTypeColIdsRows == -1:
                            diagnosisTypeColIdsRows = self.diagnosisTypeCol.ids[1]
                    else:
                        diagnosisTypeColIdsRows = self.diagnosisTypeCol.ids[1]
                    if diagnosisTypeColIdsRows > -1:
                        for rowFixed in listChangedRowSet:
                            self.items()[rowFixed].setValue('diagnosisType_id', toVariant(diagnosisTypeColIdsRows))
                            self.emitCellChanged(rowFixed, self.items()[rowFixed].indexOf('diagnosisType_id'))
                            diagnosisTypeIds[rowFixed] = forceRef(self.items()[rowFixed].value('diagnosisType_id'))
                    usedDiagnosisTypeIds = [diagnosisTypeIds[row] for row in changedRowSet.intersection(set(rows))]
            else:
                #первый диагноз равен основному
                firstDiagnosisId = self.diagnosisTypeCol.ids[1]

            #другой диагноз равен сопутствующему
            otherDiagnosisId = self.diagnosisTypeCol.ids[2]

            diagnosisTypeId = firstDiagnosisId if firstDiagnosisId not in usedDiagnosisTypeIds else otherDiagnosisId
            freeRows = set(rows).difference(changedRowSet) #список неизмененных строк этого врача
            for row in rows: # Для каждой строки этого врача
                # Если строка в списке неотредактированных или диагноз строки не принадлежит списку (закл/осн, соп)
                if (row in freeRows) or diagnosisTypeIds[row] not in [firstDiagnosisId, otherDiagnosisId]:
                    # Если вычисленный диагноз строки не равен прошлому и новый диагноз не равен осл, то изменить его в списке на новый
                    if diagnosisTypeId != diagnosisTypeIds[row] and diagnosisTypeIds[row] != self.diagnosisTypeCol.ids[3]:
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

    def getFinalDiagnosisMKB(self):
        finalDiagnosisTypeId = self.diagnosisTypeCol.ids[0]
        items = self.items()
        for item in items:
            diagnosisTypeId = forceRef(item.value('diagnosisType_id'))
            if diagnosisTypeId == finalDiagnosisTypeId:
                return forceString(item.value('MKB')), forceString(item.value('MKBEx'))
        return '', ''

    def getRelatedDiagnosisMKB(self):
        relatedDiagnosisTypeId = self.diagnosisTypeCol.ids[2]
        items = self.items()
        mkbList = []
        for item in items:
            diagnosisTypeId = forceRef(item.value('diagnosisType_id'))
            if diagnosisTypeId == relatedDiagnosisTypeId:
                mkbList.append([forceString(item.value('MKB')), forceString(item.value('MKBEx'))])
        if mkbList: return mkbList
        else: return [['', '']]

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


class CF02512FinalDiagnosticsModel(CF02512BaseDiagnosticsModel):
    __pyqtSignals__ = ('resultChanged()',
                       'significantMKBPresent(QString)',
                      )

    def __init__(self, parent):
        CF02512BaseDiagnosticsModel.__init__(self, parent, '1', '2', '9', '3')
        self.addCol(CRBInDocTableCol(    u'Исход заболевания',     'result_id',     10, 'rbDiagnosticResult', showFields=CRBComboBox.showNameAndCode, prefferedWidth=350))
        self.mapMKBToServiceId = {}

    def addRecord(self, record):
        super(CF02512FinalDiagnosticsModel, self).addRecord(record)
        self.emitResultChanged()

    def getCloseOrMainDiagnosisTypeIdList(self):
        return self.diagnosisTypeCol.ids[:2]

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        resultId = self.resultId()
        result = CF02512BaseDiagnosticsModel.setData(self, index, value, role)
        self.MKBtoVisits()
        if resultId != self.resultId():
            self.emitResultChanged()
        return result

    def removeRowEx(self, row):
        resultId = self.resultId()
        self.removeRows(row, 1)
        if resultId != self.resultId():
            self.emitResultChanged()

    def MKBtoVisits(self):
        finalDiagnosisTypeId = self.diagnosisTypeCol.ids[0]
        baseDiagnosisTypeId = self.diagnosisTypeCol.ids[1]
        items = self.items()
        for item in items:
            diagnosisTypeId = forceRef(item.value('diagnosisType_id'))
            MKB = forceString(item.value('MKB'))
            if diagnosisTypeId in (finalDiagnosisTypeId, baseDiagnosisTypeId) and MKB:
                self.emit(QtCore.SIGNAL('significantMKBPresent(QString)'), MKB)

    def resultId(self):
        finalDiagnosisTypeId = self.diagnosisTypeCol.ids[0]
        items = self.items()
        for item in items:
            diagnosisTypeId = forceRef(item.value('diagnosisType_id'))
            if diagnosisTypeId == finalDiagnosisTypeId:
                return forceRef(item.value('result_id'))
        return None

    def setFinalResult(self,  resultID, onlyIfNone = True):
        finalDiagnosisTypeId = self.diagnosisTypeCol.ids[0]
        items = self.items()
        for item in items:
            diagnosisTypeId = forceRef(item.value('diagnosisType_id'))
            if diagnosisTypeId == finalDiagnosisTypeId \
                and (not onlyIfNone or forceRef(item.value('result_id')) is None
                     ):
                item.setValue('result_id', resultID)
                self.setItems(items)
                self.emitResultChanged()
                return True
        return False

    def emitResultChanged(self):
        self.emit(QtCore.SIGNAL('resultChanged()'))


class CF02512VisitsModel(CEventVisitsModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'Visit', 'id', 'event_id', parent)
        self.colPerson = self.addCol(CActionPersonInDocTableColSearch(       u'Врач',          'person_id',    20, 'vrbPersonWithSpeciality', order = 'name', parent=parent))
        self.addCol(CActionPersonInDocTableColSearch(       u'Ассистент',     'assistant_id', 20, 'vrbPersonWithSpeciality', order = 'name', parent=parent))
        self.addCol(CRBInDocTableCol(    u'Место',         'scene_id',     10, rbScene, addNone=False, prefferedWidth=150))
        self.addCol(CDateInDocTableCol(  u'Дата',          'date',         20))
        self.addCol(CICDExInDocTableCol(u'МКБ',         'MKB',   7))
        self.addCol(CRBInDocTableCol(    u'Тип',           'visitType_id', 10, rbVisitType, addNone=False, showFields=CRBComboBox.showCodeAndName))
        self.addCol(CRBServiceInDocTableCol(u'Услуга',     'service_id',   50, 'rbService', addNone=False, showFields=CRBComboBox.showCodeAndName, prefferedWidth=150, eventEditor=parent))
        self.addCol(CRBInDocTableCol(    u'Тип финансирования', 'finance_id',  50, rbFinance, addNone=False, showFields=CRBComboBox.showCodeAndName, prefferedWidth=150))
        self.addHiddenCol('payStatus')
        self.hasAssistant = True #TODO: atronah: в чем суть поля? Оно вроде нигде не используется...
        self.defaultSceneId = None
        self.defaultMKB = None
        self.tryFindDefaultSceneId = True
        self.defaultVisitTypeId = None
        self.tryFindDefaultVisitTypeId = True
        self._parent = parent

    def fillEmptyMKB(self, MKB):
        for row, item in enumerate(self.items()):
            if not forceString(item.value('MKB')):
                item.setValue('MKB', QtCore.QVariant(MKB))
                self.emitCellChanged(row, self.getColIndex('MKB'))

    def setDefaultMKB(self, MKB):
        self.defaultMKB = MKB

    def getEmptyRecord(self, sceneId = None, personId = None):
        result = CEventVisitsModel.getEmptyRecord(self, sceneId, personId)
        if self.defaultMKB:
            result.setValue('MKB', QtCore.QVariant(self.defaultMKB))
        return result

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        column = index.column()
        if column == 4: # код МКБ
                newMKB = forceString(value)
                if not newMKB:
                    pass
                else:
                    acceptable = QtCore.QObject.parent(self).checkDiagnosis(newMKB)
                    if not acceptable:
                        return False
                value = toVariant(newMKB)
                result = CEventVisitsModel.setData(self, index, value, role)
                return result
        return CEventVisitsModel.setData(self, index, value, role)


class CF02512DiagnosisTypeCol(CDiagnosisTypeCol):
    def __init__(self, title=u'Тип', fieldName='diagnosisType_id', width=5, diagnosisTypeCodes=None, smartMode=True,
                 **params):
        if not diagnosisTypeCodes:
            diagnosisTypeCodes = []
        CDiagnosisTypeCol.__init__(self, title, fieldName, width, diagnosisTypeCodes, smartMode, **params)
        self.namesF02512 = [u'Осн', u'Соп', u'Осл']

    def toString(self, val, record):
        typeId = forceRef(val)
        if typeId in self.ids:
            return toVariant(self.namesF02512[self.ids.index(typeId)])
        return QtCore.QVariant()

    def setEditorData(self, editor, value, record):
        editor.clear()
        if value.isNull():
            value = record.value(self.fieldName())
        typeId = forceRef(value)
        if self.smartMode:
            if typeId == self.ids[0]: #id текущего типа равен заключительному диагнозу
                editor.addItem(self.namesF02512[0], toVariant(self.ids[0]))
            elif typeId == self.ids[1]: #id текущего типа равен основному диагнозу
                if self.ids[0]: #id заключительного диагнозf не NULL
                    editor.addItem(self.namesF02512[0], toVariant(self.ids[0]))
                editor.addItem(self.namesF02512[1], toVariant(self.ids[1]))
            else:
                editor.addItem(self.namesF02512[2], toVariant(self.ids[2]))
                editor.addItem(self.namesF02512[3], toVariant(self.ids[3]))
        else:
            for itemName, itemId in zip(self.namesF02512, self.ids):
                if itemId:
                    editor.addItem(itemName, toVariant(itemId))
        currentIndex = editor.findData(toVariant(typeId))
        editor.setCurrentIndex(currentIndex)
