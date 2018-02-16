# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

# Форма 030C: Стандарты

from PyQt4 import QtCore, QtGui, QtSql

from PyQt4.QtCore import QVariant

from Events.Action import CActionType, CActionTypeCache
from Events.ActionInfo import CActionInfoProxyList
from Events.ActionsSummaryModel import CFxxxActionsSummaryModel
from Events.DiagnosisType import CDiagnosisTypeCol
from Events.EventEditDialog import CEventEditDialog
from Events.EventInfo import CDiagnosticInfoProxyList, CVisitInfoProxyList
from Events.EventVisitsModel import CEventVisitsModel
from Events.Utils import checkDiagnosis, checkIsHandleDiagnosisIsChecked, findLastDiagnosisRecord, \
    getAvailableCharacterIdByMKB, getDiagnosisId2, getDiagnosisSetDateVisible, \
    getEventDuration, getEventShowTime, getExactServiceId, \
    getResultIdByDiagnosticResultId, hasEventVisitAssistant, inheritDiagnosis, \
    isEventLong, payStatusText, setAskedClassValueForDiagnosisManualSwitch, \
    CTableSummaryActionsMenuMixin, getEventLengthDays
from Forms.F030S.PreF030SDialog import CPreF030SDialog, CPreF030SDagnosticAndActionPresets
from Forms.Utils import check_data_text_TNM
from Ui_F030S import Ui_Dialog
from Users.Rights import urAdmin, urAccessF030planner, urEditDiagnosticsInPayedEvents, urRegTabWriteRegistry, \
    urOncoDiagnosisWithoutTNMS
from library.ICDInDocTableCol import CICDExInDocTableCol
from library.ICDMorphologyInDocTableCol import CMKBMorphologyCol
from library.InDocTable import CInDocTableModel, CBoolInDocTableCol, CDateInDocTableCol, CRBInDocTableCol, \
    CActionPersonInDocTableColSearch, CInDocTableCol
from library.PrintInfo import CInfoContext
from library.PrintTemplates import applyTemplate, customizePrintButton, getPrintButton
from library.TNMS.TNMSComboBox import CTNMSCol
from library.TableModel import CCol
from library.Utils import forceBool, forceDate, forceInt, forceRef, forceString, toVariant, copyFields, \
    formatNum, variantEq, forceTr
from library.crbcombobox import CRBComboBox
from library.interchange import getDateEditValue, getDatetimeEditValue, getRBComboBoxValue, \
    setDateEditValue, setDatetimeEditValue, setRBComboBoxValue


class CF030SDialog(CEventEditDialog, Ui_Dialog, CTableSummaryActionsMenuMixin):
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
        self.actAddVisitsByLasting = None

        self.addModels('Visits', CEventVisitsModel(self))
        self.addModels('PreliminaryDiagnostics', CTableMesModel(self))
        self.addModels('FinalDiagnostics',       CF030SFinalDiagnosticsModel(self))
        self.addModels('ActionsSummary', CFxxxActionsSummaryModel(self, True, loadMedicaments = True, addTime=True))

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
        self.setWindowTitleEx(u'Осмотр Ф.030С')
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
#        self.buttonBox.addButton(self.btnRelatedEvent, QtGui.QDialogButtonBox.ActionRole)
        self.setupActionSummarySlots()
        self.cmbContract.setCheckMaxClients(True)
        self.cmbPrimary.setVisible(False)
        self.lblOrder.setVisible(False)
        self.lblGoal.setVisible(False)
        self.cmbGoal.setVisible(False)

        self.tblVisits.setModel(self.modelVisits)
        self.tblMes.setModel(self.modelPreliminaryDiagnostics)
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

        self.connect(self.modelActionsSummary, QtCore.SIGNAL('hideMedicamentColumns(bool)'), self.hideMedicamentCols)

        if not QtGui.qApp.userHasRight('accessEditAutoPrimacy'):
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
        self.setClientId(clientId)
        self.clientId = clientId
        self.prolongateEvent = True if actionByNewEvent else False
        self.setExternalId(externalId)
        self.cmbPerson.setValue(personId)
        self.setEventTypeId(eventTypeId)
        self.fillNextDate() # must be after self.setEventTypeId
        self.cmbPrimary.setCurrentIndex(not self.isPrimary(clientId, eventTypeId, personId))
        self.cmbOrder.setCode(forceInt(QtGui.qApp.db.translate('EventType', 'id', eventTypeId, 'defaultOrder')))

        self.initGoal()
        self.setContract()
        self.setRecommendations(recommendationList)

        self.updateModelsRetiredList()

        self.tabNotes.setNotesEx(externalId, assistantId, curatorId, relegateOrgId, referrals = referrals)
        self.initFocus()

        visitTypeId = presetDiagnostics[0][4] if presetDiagnostics else None
        serviceId = presetDiagnostics[0][6] if presetDiagnostics else None
        self.modelVisits.setDefaultVisitTypeId(visitTypeId)
        visits = []

        if isEventLong(eventTypeId) and numDays >= 1:
            i = 0
            availDays = numDays
            while availDays>1:
                date = self.eventSetDateTime.addDays(i).date()
                if date.dayOfWeek()<=5 or includeRedDays:
                    visits.append(prepVisit(date, personId, isAmb, serviceId))
                    availDays -= 1
                i += 1
            visits.append(prepVisit(self.eventDate, personId, isAmb, serviceId))
        else:
            if self.eventDate:
                date = self.eventDate
            elif self.eventSetDateTime and self.eventSetDateTime.date():
                date = self.eventSetDateTime.date()
            else:
                date = QtCore.QDate.currentDate()
            visits.append(prepVisit(date, personId, isAmb, serviceId))
        self.modelVisits.setItems(visits)
        self.updateVisitsInfo()

        if presetDiagnostics:
            for model in [self.modelPreliminaryDiagnostics, self.modelFinalDiagnostics]:
                for MKB, dispanserId, healthGroupId, medicalGroupId, visitTypeId, goalId, serviceId in presetDiagnostics:
                    item = model.getEmptyRecord()
                    item.setValue('MKB', toVariant(MKB))
                    item.setValue('dispanser_id',   toVariant(dispanserId))
                    item.setValue('healthGroup_id', toVariant(healthGroupId))
                    item.setValue('medicalGroup_id', toVariant(medicalGroupId))
                    model.items().append(item)
                model.reset()
            if presetDiagnostics[0][5]:
                self.cmbGoal.setValue(presetDiagnostics[0][5])
        if inheritDiagnosis(eventTypeId):
            db = QtGui.qApp.db
            aborted = False
            tableEvent = db.table('Event')
            tableDiagnostic = db.table('Diagnostic')
            tableDiagnosis = db.table('Diagnosis')
            tableRBDiagnosisType = db.table('rbDiagnosisType')
            diagJoinCond = [tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']), tableDiagnosis['deleted'].eq(0)]
            if QtGui.qApp.isPNDDiagnosisMode():
                diagnosisRecord = findLastDiagnosisRecord(self.clientId)
                if not diagnosisRecord: aborted = True
                diagJoinCond = [tableDiagnosis['id'].eq(forceRef(diagnosisRecord.value('id')))]  if not aborted else 0

            if not aborted:
                queryTable = tableEvent.innerJoin(tableDiagnostic, [tableDiagnostic['event_id'].eq(tableEvent['id']),
                                                                    tableDiagnostic['deleted'].eq(0),
                                                                    tableEvent['deleted'].eq(0),
                                                                    tableEvent['client_id'].eq(self.clientId)])
                queryTable = queryTable.innerJoin(tableDiagnosis, diagJoinCond)
                queryTable = queryTable.innerJoin(tableRBDiagnosisType, [tableRBDiagnosisType['code'].eq(1),
                                                                         tableRBDiagnosisType['id'].eq(tableDiagnostic['diagnosisType_id'])])
                record = db.getRecordEx(queryTable, 'Diagnostic.*, Diagnosis.MKB, Diagnosis.MKBEx, Diagnosis.morphologyMKB', order='Event.id DESC')
                if QtGui.qApp.isPNDDiagnosisMode() and not record:
                    # Если мы в ПНД и нам еще не от чего наследоваться (нет ни одной подходящей Diagnostic),
                    # то берем Diagnosis с пустой записью Diagnostic
                    queryTable = tableDiagnosis.leftJoin(tableDiagnostic, '0')
                    cond = tableDiagnosis['id'].eq(forceRef(diagnosisRecord.value('id')))
                    record = db.getRecordEx(queryTable, 'Diagnostic.*, Diagnosis.diagnosisType_id as realDiagTypeId, Diagnosis.MKB, Diagnosis.MKBEx, Diagnosis.morphologyMKB', where=cond)
                    record.setValue('diagnosisType_id', record.value('realDiagTypeId'))
                    record.setValue('person_id',     toVariant(self.getSuggestedPersonId()))

                if record:
                    newRecord = self.modelFinalDiagnostics.getEmptyRecord()
                    copyFields(newRecord, record)
                    newRecord.setValue('id', toVariant(None))
                    newRecord.setValue('event_id', toVariant(self.itemId()))
                    if QtGui.qApp.isPNDDiagnosisMode():
                        newRecord.setValue('diagnosis_id', diagnosisRecord.value('id'))
                        newRecord.setValue('character_id', diagnosisRecord.value('character_id'))
                        self.tabMes.setMKB(forceString(diagnosisRecord.value('MKB')))
                        self.tabMes.setBegDate(record.value('begDate'))
                        self.tabMes.setEndDate(record.value('endDate'))
                        MKB2List = self.getRelatedDiagnosisMKB()
                        self.tabMes.setMKB2([r[0] for r in MKB2List])
                    else:
                        newRecord.setValue('diagnosis_id', toVariant(None))
                    newRecord.setValue('handleDiagnosis', QtCore.QVariant(0))
                    newRecord.setValue('result_id', toVariant(None))
                    self.modelFinalDiagnostics.items().append(newRecord)
                    self.modelFinalDiagnostics.reset()

        self.prepareActions(presetActions, disabledActions, actionTypeIdValue, valueProperties, diagnos, financeId, protocolQuoteId, actionByNewEvent)
        if self.isTabTempInvalidEtcAlreadyLoad:
            self.grpTempInvalid.pickupTempInvalid()
            self.grpAegrotat.pickupTempInvalid()
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
        plannerDate = self.getPlannerDate(eventSetDatetime, eventDatetime)
        if QtGui.qApp.userHasRight(urAccessF030planner):
            dlg = CPreF030SDialog(self, self.contractTariffCache)
            dlg.prepare(clientId, eventTypeId, plannerDate, self.personId, self.personSpecialityId, self.personTariffCategoryId, flagHospitalization, actionTypeIdValue, tissueTypeId, recommendationList, useDiagnosticsAndActionsPresets=useDiagnosticsAndActionsPresets)
            if dlg.diagnosticsTableIsNotEmpty() or dlg.actionsTableIsNotEmpty():
                if not dlg.exec_():
                    return False
            return self._prepare(None, clientId, eventTypeId, orgId, personId, eventSetDatetime, eventDatetime, includeRedDays, numDays, dlg.diagnostics(), dlg.actions(), dlg.disabledActionTypeIdList, externalId, assistantId, curatorId, actionTypeIdValue, valueProperties, relegateOrgId, diagnos, financeId, protocolQuoteId, actionByNewEvent, referrals=referrals, isAmb=isAmb, recommendationList=recommendationList)
        else:
            presets = CPreF030SDagnosticAndActionPresets(clientId, eventTypeId, plannerDate, self.personSpecialityId,
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
            self.grpAegrotat.pickupTempInvalid()
            self.grpDisability.pickupTempInvalid()
            self.grpVitalRestriction.pickupTempInvalid()
        self.loadActions()
        self.updateMesMKB()
        self.tabMes.setBegDate(forceDate(record.value('setDate')))
        self.tabMes.setEndDate(forceDate(record.value('execDate')))
        self.tabMes.mesItems = {}
        self.tabMes.treeStandartList.clear()
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
        self.addVisits()

    def setEditable(self, editable):
        self.modelVisits.setEditable(editable)
        self.modelActionsSummary.setEditable(editable)
        self.modelPreliminaryDiagnostics.setEditable(editable)
        self.modelFinalDiagnostics.setEditable(editable or QtGui.qApp.userHasRight(urEditDiagnosticsInPayedEvents))
        self.grpBase.setEnabled(editable)
        self.tabMes.setEnabled(True)
        self.tabStatus.setEditable(editable)
        self.tabDiagnostic.setEditable(editable)
        self.tabCure.setEditable(editable)
        self.tabMisc.setEditable(editable)
        #tabTempInvalidEtc
        self.grpDisability.setEnabled(editable)
        self.grpVitalRestriction.setEnabled(editable)
        self.tabTempInvalid.setEnabled(editable)
        self.tabAegrotat.setEnabled(editable)
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
            self.loadDiagnostics(self.modelPreliminaryDiagnostics, eventId)
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
        self.tblMes.model().loadData(eventId)
        self.modelActionsSummary.regenerate()
        self.tabCash.modelAccActions.regenerate()

    def getRecord(self):
        record = CEventEditDialog.getRecord(self)
        showTime = getEventShowTime(self.eventTypeId)
        oldNextDate = forceDate(record.value('nextEventDate'))
        oldPersonId = forceRef(record.value('execPerson_id'))

#перенести в exec_ в случае успеха или в accept?
        getRBComboBoxValue(self.cmbContract,    record, 'contract_id')
#        getDateEditValue(self.edtPrevDate,      record, 'prevEventDate')
        getDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'setDate', showTime)
        getRBComboBoxValue(self.cmbPerson,      record, 'setPerson_id')
        getDatetimeEditValue(self.edtEndDate, self.edtEndTime, record, 'execDate', showTime)
        getRBComboBoxValue(self.cmbPerson,      record, 'execPerson_id')
        getRBComboBoxValue(self.cmbResult,      record, 'result_id')
        getDateEditValue(self.edtNextDate,      record, 'nextEventDate')
        nextDate = self.edtNextDate.date()
        personId = self.cmbPerson.value()

        if not oldNextDate or not oldPersonId:
            self.createNextEvent(personId, nextDate, True)
            
        record.setValue('isPrimary', toVariant(self.cmbPrimary.currentIndex() + 1))
        if self.prolongateEvent:
            record.setValue('order', toVariant(5))
            record.setValue('prevEvent_id', toVariant(self.prevEventId))
        # getComboBoxValue(self.cmbOrder,         record, 'order')
        record.setValue('order', toVariant(self.cmbOrder.code()))

        self.tabNotes.getNotes(record, self.eventTypeId)
        return record

    def saveInternals(self, eventId):
        super(CF030SDialog, self).saveInternals(eventId)
        self.saveVisits(eventId)
        self.saveDiagnostics(self.modelFinalDiagnostics, eventId)
        setAskedClassValueForDiagnosisManualSwitch(None)
        if self.isTabTempInvalidEtcAlreadyLoad:
            self.grpTempInvalid.saveTempInvalid()
            self.grpAegrotat.saveTempInvalid()
            self.grpDisability.saveTempInvalid()
            self.grpVitalRestriction.saveTempInvalid()

        #self.updateVisits(eventId, self.modelFinalDiagnostics)  # i2809
        self.saveActions(eventId)
        self.tabCash.save(eventId)
        # self.tabNotes.saveOutgoingRef(eventId)
        self.saveBlankUsers(self.blankMovingIdList)
        self.tabMes.save(eventId)
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

    # i2809
    def updateVisits(self, eventId, modelDiagnostics):
        db = QtGui.qApp.db
        # sceneId = forceRef(db.translate('rbScene', 'code',  '1', 'id'))
        finishDiagnosisTypeId = modelDiagnostics.diagnosisTypeCol.ids[0]
        baseDiagnosisTypeId = modelDiagnostics.diagnosisTypeCol.ids[1]
        table = db.table('Visit')
        diagnostics = modelDiagnostics.items()
        visitIdList = []
        # if sceneId:
        for diagnostic in diagnostics:
            diagnosisTypeId = forceRef(diagnostic.value('diagnosisType_id'))
            if diagnosisTypeId == finishDiagnosisTypeId or diagnosisTypeId == baseDiagnosisTypeId:
                setDate = forceDate(diagnostic.value('setDate'))
                endDate = forceDate(diagnostic.value('endDate'))
                sceneId = forceRef(diagnostic.value('scene_id'))
                visitTypeId = forceRef(diagnostic.value('visitType_id'))
                specialityId = forceRef(diagnostic.value('speciality_id'))
                # visitId = forceRef(diagnostic.value('visit_id'))
                personId = forceRef(diagnostic.value('person_id'))
                financeId = forceRef(db.translate('Person', 'id', personId, 'finance_id'))
                if not financeId:
                    financeId = forceRef(db.translate('Contract', 'id', self.cmbContract.value(), 'finance_id'))
                personServiceId = forceRef(db.translate('rbSpeciality', 'id', specialityId, 'service_id'))
                diagnosisServiceId = forceRef(diagnostic.value('service_id'))
                serviceId = getExactServiceId(
                    diagnosisServiceId,
                    self.eventServiceId,
                    personServiceId,
                    self.eventTypeId,
                    visitTypeId,
                    sceneId
                )
                # serviceId = getExactServiceId(diagnostic.value('service_id'), self.eventServiceId, serviceId, self.eventTypeId, visitTypeId, sceneId)
                actuality = forceInt(diagnostic.value('actuality'))
                if not setDate.isNull() and (endDate.isNull() or setDate.addMonths(-actuality) <= endDate) and personId and visitTypeId:
                    visitId = forceRef(diagnostic.value('visit_id'))
                    if visitId:
                        record = db.getRecord(table, '*', visitId)
                    else:
                        record = table.newRecord()
                    record.setValue('event_id', toVariant(eventId))
                    record.setValue('scene_id', toVariant(sceneId))
                    record.setValue('date', toVariant(endDate))
                    record.setValue('visitType_id', toVariant(visitTypeId))
                    record.setValue('person_id', toVariant(personId))
                    record.setValue('isPrimary', toVariant(1))
                    record.setValue('finance_id', toVariant(financeId))
                    record.setValue('service_id', toVariant(serviceId))
                    # record.setValue('payStatus',    toVariant(0))
                    visitId = db.insertOrUpdate(table, record)
                    visitIdList.append(visitId)
        cond = [table['event_id'].eq(eventId)]
        if visitIdList:
            cond.append('NOT (' + table['id'].inlist(visitIdList) + ')')
        # запрещаю удалять выставленные визиты
        tableAccountItem = db.table('Account_Item')
        cond.append('NOT ' + db.existsStmt(tableAccountItem, tableAccountItem['visit_id'].eq(table['id'])))
        db.deleteRecord(table, where=cond)

    def getFinalDiagnosisMKB(self):
        MKB, MKBEx = self.modelFinalDiagnostics.getFinalDiagnosisMKB()
        return MKB, MKBEx

    def getFinalDiagnosisId(self):
        diagnosisId = self.modelFinalDiagnostics.getFinalDiagnosisId()
        if not diagnosisId:
            diagnosisId = self.modelPreliminaryDiagnostics.getFinalDiagnosisId()
        return diagnosisId

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
        CEventEditDialog.setEventTypeId(self, eventTypeId, u'Ф.030С')
        self.tabCash.windowTitle = self.windowTitle()
        showTime = getEventShowTime(eventTypeId)
        self.edtBegTime.setVisible(showTime)
        self.edtEndTime.setVisible(showTime)
        if self.cmbResult.value() is None:
            if self.inheritResult == True:
                self.cmbResult.setValue(self.defaultEventResultId.get(self.eventPurposeId))
        self.updateResultFilter()
        self.setVisitAssistantVisible(self.tblVisits, hasEventVisitAssistant(eventTypeId))
        customizePrintButton(self.btnPrint, self.eventContext if self.eventContext else 'F030S')
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
            result = result and self.checkDiagnosticsDataEntered([(self.tblFinalDiagnostics, True, True, endDate)],
                                                                 endDate)
#            result = result and self.checkActionsDataEntered(begDate, endDate)
            result = result and self.checkActionsDateEnteredActuality(begDate, endDate, [self.tabStatus, self.tabDiagnostic, self.tabCure, self.tabMisc])
            result = result and self.checkActionsDataEntered([self.tabStatus, self.tabDiagnostic, self.tabCure, self.tabMisc], begDate, endDate)
        result = result and (len(self.modelVisits.items())>0 or self.checkInputMessage(u'посещение', False, self.tblVisits))
        result = result and self.checkVisitsDataEntered(begDate, endDate)
        if self.isTabTempInvalidEtcAlreadyLoad:
            result = result and self.grpTempInvalid.checkTempInvalidDataEntered()
            result = result and self.grpAegrotat.checkTempInvalidDataEntered()
            result = result and self.grpDisability.checkTempInvalidDataEntered()
            result = result and self.grpVitalRestriction.checkTempInvalidDataEntered()
        result = result and (self.itemId() or self.primaryCheck(self.modelFinalDiagnostics))
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

    def checkDiagnosticResultEntered(self, table, row, record, endDate):
        if endDate is None:
            endDate = QtCore.QDate()
        if row == 0 and not endDate.isNull():
            resultId = forceRef(record.value('result_id'))
            return resultId or self.checkInputMessage(forceTr(u'результат', u'EventDiagnostic'), False, table, row, record.indexOf('result_id'))
        return True

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
        result._diagnosises = CDiagnosticInfoProxyList(context, [self.modelPreliminaryDiagnostics, self.modelFinalDiagnostics])
        result._visits = CVisitInfoProxyList(context, self.modelVisits)
        return result

    def getTempInvalidInfo(self, context):
        return self.grpTempInvalid.getTempInvalidInfo(context)

    def getAegrotatInfo(self, context):
        return self.grpAegrotat.getTempInvalidInfo(context)

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
        self.tabMes.preSetupUi()
        self.tabMes.postSetupUi()
        if show: self.tabMes.setVisible(True)
        self.tabMes.setEventId(self._id)
        self.isTabMesAlreadyLoad = True
        self.tabMes.setActionModel(self.modelActionsSummary)

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

        self.tabTempInvalidAndAegrotat.setCurrentIndex(1 if QtGui.qApp.tempInvalidDoctype() == '2' else 0)
        self.grpTempInvalid.setEventEditor(self)
        self.grpTempInvalid.setType(0, '1')
        self.grpAegrotat.setEventEditor(self)
        self.grpAegrotat.setType(0, '2')
        self.grpDisability.setEventEditor(self)
        self.grpDisability.setType(1)
        self.grpVitalRestriction.setEventEditor(self)
        self.grpVitalRestriction.setType(2)

        self.grpTempInvalid.pickupTempInvalid()
        self.grpAegrotat.pickupTempInvalid()
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

    def addVisits(self):
        isLong = isEventLong(self.getEventTypeId())
        begDate = self.edtBegDate.date()
        endDate = self.edtEndDate.date()
        if isLong and begDate and endDate and not self.actAddVisitsByLasting:
            self.actAddVisitsByLasting = QtGui.QAction(u'Добавить визиты по длительности', self)
            self.actAddVisitsByLasting.setObjectName('actAddVisitsByLasting')
            self.actAddVisitsByLastingIncludeRedDays = QtGui.QAction(u'Добавить визиты по длительности, включая выходные', self)
            self.actAddVisitsByLastingIncludeRedDays.setObjectName('actAddVisitsByLastingIncludeRegDays')
            self.tblVisits._popupMenu.addSeparator()
            self.tblVisits._popupMenu.addAction(self.actAddVisitsByLasting)
            self.tblVisits._popupMenu.addAction(self.actAddVisitsByLastingIncludeRedDays)
            self.connect(self.actAddVisitsByLasting, QtCore.SIGNAL('triggered()'), self.addVisitsByLasting)
            self.connect(self.actAddVisitsByLastingIncludeRedDays, QtCore.SIGNAL('triggered()'), self.addVisitsByLastingIncludeRedDays)

    def addVisitsByLasting(self):
        self.on_addVisitsByLasting(False)

    def addVisitsByLastingIncludeRedDays(self):
        self.on_addVisitsByLasting(True)

    def on_addVisitsByLasting(self, includeRedDays):
        begDate = self.edtBegDate.date()
        endDate = self.edtEndDate.date()
        totalDays = begDate.daysTo(endDate) + 1
        numDays = totalDays
        if not includeRedDays:
            for i in xrange(totalDays):
                if begDate.addDays(i).dayOfWeek() in [QtCore.Qt.Saturday, QtCore.Qt.Sunday]:
                    numDays -= 1
        def prepVisit(date):
            visit = self.modelVisits.getEmptyRecord(sceneId=None)
            visit.setValue('date', toVariant(date))
            return visit
        self.modelVisits.setDefaultVisitTypeId(1)
        visits = []
        if numDays >= 1:
            i = 1
            availDays = numDays
            while availDays > 1 :
                date = self.eventSetDateTime.addDays(i).date()
                if date.dayOfWeek() <= 5 or includeRedDays:
                    visits.append(prepVisit(date))
                    availDays -= 1
                i += 1
            visits.append(prepVisit(begDate))
        else:
            visits.append(prepVisit(endDate))
        self.modelVisits.setItems(visits)
        self.updateVisitsInfo()

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
        # i3110
        #self.updateResultFilter()
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
        self.addVisits()
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

    @QtCore.pyqtSlot()
    def on_modelFinalDiagnostics_diagnosisChanged(self):
        self.updateVisitsByDiagnostics(self.sender())
        self.updateMesMKB()

    @QtCore.pyqtSlot()
    def on_modelFinalDiagnostics_resultChanged(self):
        CEventEditDialog.defaultDiagnosticResultId[self.eventPurposeId] = self.modelFinalDiagnostics.resultId()
        self.updateResultFilter()

    @QtCore.pyqtSlot()
    def on_actDiagnosticsAddAccomp_triggered(self):
        currentRow = self.tblFinalDiagnostics.currentIndex().row()
        if currentRow>=0 :
            currentRecord = self.modelFinalDiagnostics.items()[currentRow]
            newRecord = self.modelFinalDiagnostics.getEmptyRecord()
            newRecord.setValue('diagnosisType', QtCore.QVariant(CF030SDialog.dfAccomp))
            newRecord.setValue('speciality_id', currentRecord.value('speciality_id'))
            newRecord.setValue('healthGroup_id', currentRecord.value('healthGroup_id'))
            newRecord.setValue('medicalGroup_id', currentRecord.value('medicalGroup_id'))
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
        if self.isDirty() and forceInt(QtGui.qApp.db.translate('rbPrintTemplate', 'id', templateId, 'banUnkeptDate')) == 2:
            if QtGui.QMessageBox.question(self,
                                       u'Внимание!',
                                       u'Для печати данного шаблона необходимо сохранить обращение.\nСохранить сейчас?',
                                       QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
                                       QtGui.QMessageBox.No) != QtGui.QMessageBox.Yes:
                return
            if not self.saveData():
                return
        context = CInfoContext()
        if not self.isTabTempInvalidEtcAlreadyLoad:
            self.initTabTempInvalidEtc(False)
        if not self.isTabCashAlreadyLoad:
            self.initTabCash(False)
        eventInfo = self.getEventInfo(context)
        tempInvalidInfo = self.getTempInvalidInfo(context)
        aegrotatInfo = self.getAegrotatInfo(context)

        data = { 'event' : eventInfo,
                 'client': eventInfo.client,
                 'tempInvalid': tempInvalidInfo,
                 'aegrotat': aegrotatInfo
               }
        data['templateCounterValue'] = self.oldTemplates.get(templateId, '')
        applyTemplate(self, templateId, data)

    @QtCore.pyqtSlot(int)
    def on_cmbResult_currentIndexChanged(self):
        self.modelFinalDiagnostics.setFinalResult(getResultIdByDiagnosticResultId(self.cmbResult.value()))


class CMKBIndoxTableCOl(CInDocTableCol):
    def __init__(self, title, fieldName, width, tableName, **params):
        CInDocTableCol.__init__(self, title, fieldName, width, **params)
        self.tableName = tableName
        self.filter = params.get('filter', '')
        self.prefferedWidth = params.get('prefferedWidth', None)
        self.db = QtGui.qApp.db
        self.tblMkb = self.db.table('MKB')

    def toString(self, val, record):
        return toVariant(forceString(self.db.translate(self.tblMkb, self.tblMkb['DiagID'], forceString(val), self.tblMkb['DiagName'])))

    def toStatusTip(self, val, record):
        return QVariant()

    def createEditor(self, parent):
        pass

    def setEditorData(self, editor, value, record):
        pass

    def getEditorData(self, editor):
        pass


class CF030SBaseDiagnosticsModel(CInDocTableModel):
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
        self.finishDiagnosisTypeCode = finishDiagnosisTypeCode
        self.baseDiagnosisTypeCode = baseDiagnosisTypeCode
        self.diagnosisTypeCol = CF030SDiagnosisTypeCol( u'Тип', 'diagnosisType_id', 2, [finishDiagnosisTypeCode, baseDiagnosisTypeCode, accompDiagnosisTypeCode, complicDiagnosisTypeCode], smartMode=False)
        self.addCol(self.diagnosisTypeCol)
        self.colPerson = self.addCol(CActionPersonInDocTableColSearch(u'Врач', 'person_id', 20, 'vrbPersonWithSpeciality', order = 'name', parent=parent))
        self.addExtCol(CICDExInDocTableCol(u'код МКБ',         'MKB',   6), QtCore.QVariant.String)
        self.addCol(CMKBIndoxTableCOl(u'Расш. МКБ', 'MKB', 10, 'MKB'))
        self.addExtCol(CICDExInDocTableCol(u'Доп. код МКБ',     'MKBEx', 6), QtCore.QVariant.String)
        self.addCol(CDateInDocTableCol(  u'Выявлено',      'setDate',        10))
        if QtGui.qApp.isTNMSVisible():
            self.addCol(CTNMSCol(u'TNM-Ст', 'TNMS',  10))
        if self.isMKBMorphology:
            self.addExtCol(CMKBMorphologyCol(u'Морф.', 'morphologyMKB', 10, 'MKB_Morphology', filter='`group` IS NOT NULL'), QtCore.QVariant.String)
        # self.addCol(CDiseaseCharacter(     u'Хар',         'character_id',   7, showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(u'Характер')
        if self.isManualSwitchDiagnosis:
            self.addExtCol(CBoolInDocTableCol( u'П',   'handleDiagnosis', 10), QtCore.QVariant.Int)
            self.characterIdForHandleDiagnosis = forceRef(QtGui.qApp.db.translate('rbDiseaseCharacter', 'code', '1', 'id'))
            self.columnHandleDiagnosis = self._mapFieldNameToCol.get('handleDiagnosis')

        # self.addCol(CDiseasePhases(        u'Фаза',        'phase_id',       6, showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(u'Фаза')
        # self.addCol(CDiseaseStage(         u'Ст',          'stage_id',       6, showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(u'Стадия')
        # self.addCol(CRBInDocTableCol(    u'ДН',            'dispanser_id',   6, 'rbDispanser', showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(u'Диспансерное наблюдение')
        # self.addCol(CRBLikeEnumInDocTableCol(u'Госп',      'hospital',       7, CHospitalInfo.names, showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(u'Потребность в госпитализации')
        # self.addCol(CRBInDocTableCol(    u'Травма',        'traumaType_id', 10, 'rbTraumaType', addNone=True, showFields=CRBComboBox.showName, prefferedWidth=150))
        # self.addCol(CRBInDocTableCol(    u'ГрЗд',          'healthGroup_id', 6, 'rbHealthGroup', addNone=True, showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(u'Группа здоровья')
        # self.addCol(CRBInDocTableCol(    u'МедГр',         'medicalGroup_id', 6, 'rbMedicalGroup', addNone=True, showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(u'Медицинская группа')
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
                    if not (bool(mkb) and mkb[0] in CF030SBaseDiagnosticsModel.MKB_allowed_morphology):
                        result = (result & ~QtCore.Qt.ItemIsEditable)
        if not self.isEditable():
            result = (result & ~QtCore.Qt.ItemIsEditable)
        if QtGui.qApp.isPNDDiagnosisMode() \
            and ((forceString(self.value(row, 'diagnosisType_id')) in (self.finishDiagnosisTypeCode, self.baseDiagnosisTypeCode) \
            and (index.column() != self._mapFieldNameToCol.get('result_id'))) or (row == len(self.items()) and index.column() != 0)): # Добавлять диагнозы можно только после указания типа диагноза.
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
                if QtGui.qApp.isPNDDiagnosisMode() and forceString(value) in (self.finishDiagnosisTypeCode, self.baseDiagnosisTypeCode):
                    return False
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
                    if not QtGui.qApp.isPNDDiagnosisMode(): self.updateDiagnosisType(set())
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
        baseDiagnosisTypeId = self.diagnosisTypeCol.ids[1]
        items = self.items()
        for item in items:
            diagnosisTypeId = forceRef(item.value('diagnosisType_id'))
            if (diagnosisTypeId == finalDiagnosisTypeId) or (diagnosisTypeId == baseDiagnosisTypeId):
                return forceRef(item.value('diagnosis_id'))
        return None

    def getFinalDiagnosis(self):
        finalDiagnosisTypeId = self.diagnosisTypeCol.ids[0]
        baseDiagnosisTypeId = self.diagnosisTypeCol.ids[1]
        items = self.items()
        for item in items:
            diagnosisTypeId = forceRef(item.value('diagnosisType_id'))
            if (diagnosisTypeId == finalDiagnosisTypeId) or (diagnosisTypeId == baseDiagnosisTypeId):
                return item
        return None

    def emitDiagnosisChanged(self):
        self.emit(QtCore.SIGNAL('diagnosisChanged()'))


class CF030SPreliminaryDiagnosticsModel(CF030SBaseDiagnosticsModel):
    def __init__(self, parent):
        CF030SBaseDiagnosticsModel.__init__(self, parent, None, '7', '11', None)

    def getEmptyRecord(self):
        result = CF030SBaseDiagnosticsModel.getEmptyRecord(self)
        return result


class CF030SFinalDiagnosticsModel(CF030SBaseDiagnosticsModel):
    __pyqtSignals__ = ('resultChanged()',
                      )

    def __init__(self, parent):
        CF030SBaseDiagnosticsModel.__init__(self, parent, '1', '2', '9', '3')
        self.addCol(CRBInDocTableCol(forceTr(u'Результат', u'EventDiagnostic'),     'result_id',     10, 'rbDiagnosticResult', showFields=CRBComboBox.showNameAndCode, prefferedWidth=350))
        self.mapMKBToServiceId = {}

    def addRecord(self, record):
        super(CF030SFinalDiagnosticsModel, self).addRecord(record)
        self.emitResultChanged()

    def getCloseOrMainDiagnosisTypeIdList(self):
        return self.diagnosisTypeCol.ids[:2]

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        resultId = self.resultId()
        result = CF030SBaseDiagnosticsModel.setData(self, index, value, role)
        if resultId != self.resultId():
            self.emitResultChanged()
        return result

    def removeRowEx(self, row):
        resultId = self.resultId()
        self.removeRows(row, 1)
        if resultId != self.resultId():
            self.emitResultChanged()

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


class CF030SDiagnosisTypeCol(CDiagnosisTypeCol):
    def __init__(self, title=u'Тип', fieldName='diagnosisType_id', width=5, diagnosisTypeCodes=None, smartMode=True,
                 **params):
        if not diagnosisTypeCodes:
            diagnosisTypeCodes = []
        CDiagnosisTypeCol.__init__(self, title, fieldName, width, diagnosisTypeCodes, smartMode, **params)
        self.namesF030 = [u'Закл', u'Осн', u'Соп', u'Осл']

    def toString(self, val, record):
        typeId = forceRef(val)
        if typeId in self.ids:
            return toVariant(self.namesF030[self.ids.index(typeId)])
        return QtCore.QVariant()

    def setEditorData(self, editor, value, record):
        editor.clear()
        if value.isNull():
            value = record.value(self.fieldName())
        typeId = forceRef(value)
        if self.smartMode:
            if typeId == self.ids[0]: #id текущего типа равен заключительному диагнозу
                editor.addItem(self.namesF030[0], toVariant(self.ids[0]))
            elif typeId == self.ids[1]: #id текущего типа равен основному диагнозу
                if self.ids[0]: #id заключительного диагнозf не NULL
                    editor.addItem(self.namesF030[0], toVariant(self.ids[0]))
                editor.addItem(self.namesF030[1], toVariant(self.ids[1]))
            else:
                editor.addItem(self.namesF030[2], toVariant(self.ids[2]))
                editor.addItem(self.namesF030[3], toVariant(self.ids[3]))
        else:
            for itemName, itemId in zip(self.namesF030, self.ids):
                if itemId:
                    editor.addItem(itemName, toVariant(itemId))
        currentIndex = editor.findData(toVariant(typeId))
        editor.setCurrentIndex(currentIndex)


class CTableMesModel(CInDocTableModel):
    headerText = [u'Наименование', u'Длительность', u'%']

    def __init__(self, parent):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._cols = []
        self._items = []
        self.db = QtGui.qApp.db

    def cols(self):
        self._cols = [CCol(u'Наименование', ['name'], 80, 'l'),
                      CCol(u'Длительность', ['begDate'], 15, 'l'),
                      CCol(u'%', ['endDate'], 15, 'l')
                      ]
        return self._cols

    def columnCount(self, index=QtCore.QModelIndex()):
        return 3

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self._items)

    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.headerText[section])
        return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = index.column()
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            item = self._items[row]
            return toVariant(item[column])
        return QtCore.QVariant()

    def loadData(self, eventId):
        self._items = []
        tableMes = self.db.table('mes.MES')
        tableAction = self.db.table('Action')
        tableActionType = self.db.table('ActionType')
        tableMesService = self.db.table('mes.MES_service')
        mesList = []
        if eventId:
            recMesList = self.db.getDistinctIdList(tableAction, tableAction['MES_id'], [tableAction['event_id'].eq(eventId),
                                                                                    tableAction['deleted'].eq(0),
                                                                                    tableAction['MES_id'].isNotNull()])
            if recMesList:
                for v in recMesList:
                    if not v in mesList:
                        mesList.append(v)

            for v in mesList:
                tableServices = tableAction.innerJoin(tableMes, tableMes['id'].eq(tableAction['MES_id']))
                tableServices = tableServices.innerJoin(tableActionType, [tableAction['actionType_id'].eq(tableActionType['id']), tableActionType['code'].ne('medicament')])
                tableServices = tableServices.innerJoin(tableMesService, [tableMesService['master_id'].eq(tableMes['id']), tableMesService['necessity'].eq(1)])

                actions = 0.0
                doneAction = 0.0
                recActions = self.db.getDistinctIdList(tableServices, tableAction['id'], [tableAction['event_id'].eq(eventId),
                                                                                tableAction['deleted'].eq(0),
                                                                                tableAction['MES_id'].eq(v)])
                recDoneActions = self.db.getDistinctIdList(tableServices, tableAction['id'], [tableAction['event_id'].eq(eventId),
                                                                                    tableAction['deleted'].eq(0),
                                                                                    tableAction['MES_id'].eq(v),
                                                                                    tableAction['endDate'].isNotNull()])

                actions += len(recActions)
                doneAction += len(recDoneActions)

                mesName = self.db.translate(tableMes, tableMes['id'], v, tableMes['name'])
                mesDuration = self.db.translate(tableMes, tableMes['id'], v, tableMes['maxDuration'])
                if actions - 1:
                    mesProcent = (doneAction / (actions - 1)) * 100
                    if mesName:
                        item = [forceString(mesName),
                                forceString(mesDuration),
                                forceString(round(mesProcent))
                                ]
                        self._items.append(item)
        self.reset()

    def createEditor(self):
        pass
