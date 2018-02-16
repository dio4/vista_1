# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2016 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

# Форма 025: стат.талон и т.п.

from PyQt4 import QtCore, QtGui, QtSql

from Events.Action import CActionType, CActionTypeCache
from Events.ActionInfo import CActionInfoProxyList
from Events.ActionsSummaryModel import CFxxxActionsSummaryModel
from Events.EventEditDialog import CEventEditDialog, CDiseaseCharacter, CDiseaseStage, CDiseasePhases
from Events.EventInfo import CDiagnosticInfoProxyList, CHospitalInfo, CVisitInfoProxyList
from Events.EventRecipesPage import CFastEventRecipesPage
from Events.EventVisitsModel import CEventVisitsModel
from Events.Utils import checkDiagnosis, checkIsHandleDiagnosisIsChecked, findLastDiagnosisRecord, \
    getAvailableCharacterIdByMKB, getDiagnosisId2, getDiagnosisSetDateVisible, \
    getEventDuration, getEventShowTime, getExactServiceId, \
    getResultIdByDiagnosticResultId, hasEventVisitAssistant, inheritDiagnosis, \
    isEventLong, payStatusText, setAskedClassValueForDiagnosisManualSwitch, \
    CTableSummaryActionsMenuMixin, getEventLengthDays, \
    setOrgStructureIdToCmbPerson, CDiagnosisServiceMap
from Forms.F025.PreF025Dialog import CPreF025Dialog, CPreF025DagnosticAndActionPresets
from Forms.Utils import check_data_text_TNM
from Registry.Utils import checkTempInvalidNumber
from Ui_F025 import Ui_Dialog
from Users.Rights import urAccessF025planner, urAdmin, urEditDiagnosticsInPayedEvents, urRegTabWriteRegistry, \
    urCreateReferral, \
    urOncoDiagnosisWithoutTNMS
from Users.UserInfo import CUserInfo
from library.ICDInDocTableCol import CICDExInDocTableCol
from library.ICDMorphologyInDocTableCol import CMKBMorphologyCol
from library.InDocTable import CInDocTableModel, CBoolInDocTableCol, CDateInDocTableCol, CRBInDocTableCol, \
    CRBLikeEnumInDocTableCol
from library.PrintInfo import CInfoContext
from library.PrintTemplates import applyTemplate, customizePrintButton, getPrintButton
from library.TNMS.TNMSComboBox import CTNMSCol
from library.Utils import forceBool, forceDate, forceInt, forceRef, forceString, toVariant, copyFields, \
    formatNum, variantEq, forceTr
from library.crbcombobox import CRBComboBox
from library.interchange import getDateEditValue, getDatetimeEditValue, getRBComboBoxValue, \
    setDateEditValue, setDatetimeEditValue, setRBComboBoxValue


class CF025BaseDialog(CEventEditDialog, Ui_Dialog, CTableSummaryActionsMenuMixin):
    isTabMesAlreadyLoad = False
    isTabStatusAlreadyLoad = False
    isTabDiagnosticAlreadyLoad = False
    isTabCureAlreadyLoad = False
    isTabMiscAlreadyLoad = False
    isTabAnalysesAlreadyLoad = False
    isTabAmbCardAlreadyLoad = False
    isTabTempInvalidEtcAlreadyLoad = False
    isTabCashAlreadyLoad = False
    isTabNotesAlreadyLoad = False
    isTabRecipesAlreadyLoad = False
    isTabDestinationsAlreadyLoad = False

    def __init__(self, parent):
        CEventEditDialog.__init__(self, parent)
        self.mapSpecialityIdToDiagFilter = {}
        self.actAddVisitsByLasting = None
        self.postUiSet = False

        self.addModels('Visits', CEventVisitsModel(self))
        self.addModels('Diagnostics', CF025DiagnosticsModel(self))
        self.addModels('ActionsSummary', CFxxxActionsSummaryModel(self, True, loadMedicaments = True))
        self.createSaveAndCreateAccountButton()

        self.actEditClient = QtGui.QAction(u'Изменить описание клиента', self)
        self.actEditClient.setObjectName('actEditClient')
        self.setupDiagnosticsMenu()
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

        self.tabAnalyses.preSetupUiMini()
        self.tabAnalyses.setupUiMini(self.tabAnalyses)
        self.tabAnalyses.postSetupUiMini()

        self.tabCash.preSetupUiMini()
        self.tabCash.setupUiMini(self.tabCash)
        self.tabCash.postSetupUiMini()

        hiddenWidgets = CUserInfo.loadHiddenGUIWidgetsNameList(QtGui.qApp.userId, QtGui.qApp.userInfo.userProfilesId[0])
        # if 'EventEditDialog.tabDestinations' not in hiddenWidgets:
        #     self.tabDestinations = CFastDestinationsPage()
        #     self.tabWidget.insertTab(5, self.tabDestinations, u'Лекарственные назначения')
        #     self.tabDestinations.preSetupUiMini()
        #     self.tabDestinations.preSetupUi()
        #     self.tabDestinations.setupUi(self.tabDestinations)
        #     self.tabDestinations.setupUiMini(self.tabDestinations)
        #     self.tabDestinations.postSetupUiMini()
        #     self.tabDestinations.postSetupUi()
        # else:
        self.tabDestinations = None

        if 'EventEditDialog.tabRecipes' not in hiddenWidgets:
            self.tabRecipes = CFastEventRecipesPage()
            self.tabWidget.insertTab(6, self.tabRecipes, u'Льготные рецепты')
            self.tabRecipes.setupUiMini(self.tabCash)
            self.tabRecipes.postSetupUiMini()

        self.tabNotes.preSetupUiMini()
        self.tabNotes.preSetupUi()
        self.tabNotes.setupUiMini(self.tabNotes)
        self.tabNotes.setupUi(self.tabNotes)
        self.tabNotes.postSetupUiMini(self.edtBegDate.date())

        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Осмотр Ф.025')
        self.tabToken.setFocusProxy(self.tblFinalDiagnostics)
        self.tabMes.setEventEditor(self)

        self.tabStatus.setEventEditor(self)
        self.tabDiagnostic.setEventEditor(self)
        self.tabCure.setEventEditor(self)
        self.tabMisc.setEventEditor(self)
        self.tabAnalyses.setEventEditor(self)
        self.tabCash.setEventEditor(self)
        self.tabStatus.setActionTypeClass(0)
        self.tabDiagnostic.setActionTypeClass(1)
        self.tabCure.setActionTypeClass(2)
        self.tabMisc.setActionTypeClass(3)
        self.tabAnalyses.setActionTypeClass(4)
        self.buttonBox.addButton(self.btnPrint, QtGui.QDialogButtonBox.ActionRole)
        self.setupSaveAndCreateAccountButton()
        self.setupSaveAndCreateAccountForPeriodButton()
        self.setupActionSummarySlots()
        self.cmbContract.setCheckMaxClients(True)

        self.tblVisits.setModel(self.modelVisits)
        self.tblFinalDiagnostics.setModel(self.modelDiagnostics)
        self.tblActions.setModel(self.modelActionsSummary)
        self.modelActionsSummary.addModel(self.tabStatus.modelAPActions)
        self.modelActionsSummary.addModel(self.tabDiagnostic.modelAPActions)
        self.modelActionsSummary.addModel(self.tabCure.modelAPActions)
        self.modelActionsSummary.addModel(self.tabMisc.modelAPActions)
        self.modelActionsSummary.addModel(self.tabAnalyses.modelAPActions)
        self.tabCash.addActionModel(self.tabStatus.modelAPActions)
        self.tabCash.addActionModel(self.tabDiagnostic.modelAPActions)
        self.tabCash.addActionModel(self.tabCure.modelAPActions)
        self.tabCash.addActionModel(self.tabMisc.modelAPActions)
        self.tabCash.addActionModel(self.tabAnalyses.modelAPActions)

        self.markEditableTableWidget(self.tblVisits)
        self.markEditableTableWidget(self.tblFinalDiagnostics)
        self.markEditableTableWidget(self.tblActions)

        self.txtClientInfoBrowser.actions.append(self.actEditClient)
        self.actEditClient.setEnabled(QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteRegistry]))
        self.tblVisits.addPopupDelRow()
        self.tblFinalDiagnostics.setPopupMenu(self.mnuDiagnostics)
        CTableSummaryActionsMenuMixin.__init__(self)

        db = QtGui.qApp.db
        table = db.table('rbScene')
        self.sceneListHome = db.getIdList(table, 'id', table['code'].inlist(['2', '3']))
        self.sceneListAmb  = db.getIdList(table, 'id', table['code'].inlist(['1']))

        self.setupDirtyCather()
        self.setIsDirty(False)
        self.blankMovingIdList = []
        self.clientId = None
        self.prolongateEvent = False
        self.prevEventId = None
        self.tabNotes.setEventEditor(self)
        self.cmbResult.setShowFields(CRBComboBox.showCodeAndName)
        self.chkHospParent.setVisible(not QtGui.qApp.defaultKLADR().startswith('23'))

        self.postSetupUi()
        self._isCheckPresenceInAccounts = True

        self.connect(self.modelActionsSummary, QtCore.SIGNAL('hideMedicamentColumns(bool)'), self.hideMedicamentCols)
        if self.tabDestinations:
            self.connect(self.tabDestinations.tblDestinations.selectionModel(), QtCore.SIGNAL('selectionChanged(QItemSelection, QItemSelection)'), self.tabDestinations.on_selectionModelDestinations_selectionChanged)

        if QtGui.qApp.userHasRight('editCycleDay'):
            self.lblCycleDay.setVisible(True)
            self.edtCycleDay.setVisible(True)
        else:
            self.lblCycleDay.setVisible(False)
            self.edtCycleDay.setVisible(False)

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

    def canClose(self):
        if self.tabDestinations and not self.tabDestinations.canClose():
            return False
        if hasattr(self, 'tabRecipes') and not self.tabRecipes.canClose():
            return False
        return CEventEditDialog.canClose(self)

    def getModelFinalDiagnostics(self):
        return self.modelDiagnostics

    def setupDiagnosticsMenu(self):
        self.mnuDiagnostics = QtGui.QMenu(self)
        self.mnuDiagnostics.setObjectName('mnuDiagnostics')
        self.actDiagnosticsRemove = QtGui.QAction(u'Удалить запись', self)
        self.actDiagnosticsRemove.setObjectName('actDiagnosticsRemove')
        self.mnuDiagnostics.addAction(self.actDiagnosticsRemove)

    def _prepare(self, contractId, clientId, eventTypeId, orgId, personId, eventSetDatetime, eventDatetime, includeRedDays, numDays,
                 presetDiagnostics, presetActions, disabledActions, notDeletedActions, externalId, assistantId, curatorId,
                 actionTypeIdValue=None, valueProperties=None, relegateOrgId=None, diagnos=None, financeId=None,
                 protocolQuoteId=None, actionByNewEvent=None, referrals=None, isAmb=True, recommendationList=None):
        if not valueProperties:
            valueProperties = []
        if not referrals:
            referrals = {}
        if not actionByNewEvent:
            actionByNewEvent = []
        if not recommendationList:
            recommendationList = []

        def getPrimacy():
            if QtGui.qApp.isAutoPrimacy():
                return self.setPrimacy()
            else:
                strategy = QtGui.qApp.f025DefaultPrimacy()
                if strategy == 3: # по специалисту
                    db = QtGui.qApp.db
                    table = db.table('Event')
                    date = eventDatetime if eventDatetime else eventSetDatetime
                    date = date.date() if isinstance(date, QtCore.QDateTime) else date
                    cond = [
                        table['eventType_id'].eq(eventTypeId),
                        table['execPerson_id'].eq(personId),
                        table['execDate'].ge(date.addDays(-14))
                    ]
                    record = db.getRecordEx(table, 'id', cond)
                    return not record
                elif strategy == 2: # по специальности
                    db = QtGui.qApp.db
                    table = db.table('Event')
                    tablePerson = db.table('Person')
                    date = eventDatetime if eventDatetime else eventSetDatetime
                    date = date.date() if isinstance(date, QtCore.QDateTime) else date
                    cond = [
                        table['eventType_id'].eq(eventTypeId),
                        tablePerson['speciality_id'].eq(self.personSpecialityId),
                        table['execDate'].ge(date.addDays(-14))
                    ]
                    record = db.getRecordEx(
                        table.leftJoin(tablePerson, tablePerson['id'].eq(table['execPerson_id'])),
                        'Event.id',
                        cond
                    )
                    return not record
                else:
                    return strategy == 1


        def prepVisit(date, isAmb=True, serviceId=None):
            sceneId = None if isAmb else QtGui.qApp.db.translate('rbScene', 'code', '2', 'id')
            visit = self.modelVisits.getEmptyRecord(sceneId=sceneId)
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
        self.setExternalId(externalId)
        self.cmbPerson.setValue(personId)
        self.tabReferralPage.cmbPerson.setValue(personId)
        self.setEventTypeId(eventTypeId)
        self.fillNextDate() # must be after self.setEventTypeId
        self.cmbPrimary.setCurrentIndex(not getPrimacy())
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
                    visits.append(prepVisit(date, isAmb, serviceId))
                    availDays -= 1
                i += 1
            visits.append(prepVisit(self.eventDate, isAmb, serviceId))
        else:
            visits.append(prepVisit(self.eventSetDateTime, isAmb, serviceId))
        self.modelVisits.setItems(visits)
        self.updateVisitsInfo()

        if presetDiagnostics:
            for MKB, dispanserId, healthGroupId, medicalGroupId, visitTypeId, goalId, serviceId in presetDiagnostics:
                item = self.modelDiagnostics.getEmptyRecord()
                item.setValue('MKB', toVariant(MKB))
                item.setValue('dispanser_id',   toVariant(dispanserId))
                item.setValue('healthGroup_id', toVariant(healthGroupId))
                self.modelDiagnostics.items().append(item)
            if presetDiagnostics[0][5]:
                self.cmbGoal.setValue(presetDiagnostics[0][5])
            self.modelDiagnostics.reset()
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
                diagJoinCond = [tableDiagnosis['id'].eq(forceRef(diagnosisRecord.value('id')))] if not aborted else 0

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
                    record = db.getRecordEx(queryTable, 'Diagnostic.*, Diagnosis.MKB, Diagnosis.MKBEx, Diagnosis.morphologyMKB', where=cond)

                if record:
                    newRecord = self.modelDiagnostics.getEmptyRecord()
                    copyFields(newRecord, record)
                    newRecord.setValue('id', toVariant(None))
                    newRecord.setValue('event_id', toVariant(self.itemId()))
                    if QtGui.qApp.isPNDDiagnosisMode():
                        newRecord.setValue('diagnosis_id', diagnosisRecord.value('id'))
                        newRecord.setValue('character_id', diagnosisRecord.value('character_id'))
                    else:
                        newRecord.setValue('diagnosis_id', toVariant(None))
                    newRecord.setValue('handleDiagnosis', QtCore.QVariant(0))
                    newRecord.setValue('result_id', toVariant(None))
                    self.modelDiagnostics.items().append(newRecord)
                    self.modelDiagnostics.reset()

        self.prepareActions(presetActions, disabledActions, notDeletedActions, valueProperties, diagnos, financeId, protocolQuoteId, actionByNewEvent)
        if self.isTabTempInvalidEtcAlreadyLoad:
            self.grpTempInvalid.pickupTempInvalid()                                                 # for tabTempInvalidEtc
            # self.grpAegrotat.pickupTempInvalid()                                                    # for tabTempInvalidEtc
            self.grpDisability.pickupTempInvalid()                                                  # for tabTempInvalidEtc
            self.grpVitalRestriction.pickupTempInvalid()                                            # for tabTempInvalidEtc
        self.setIsDirty(False)
        self.tabNotes.setEventEditor(self)
        self.tabMes.postSetupUi()
        self.on_cmbResult_currentIndexChanged()		# !!! add after merge !!!

        return self.checkEventCreationRestriction()


    def prepare(self, clientId, eventTypeId, orgId, personId, eventSetDatetime, eventDatetime, includeRedDays, numDays,
                externalId, assistantId, curatorId, flagHospitalization=False, actionTypeIdValue=None,
                valueProperties=None, tissueTypeId=None, selectPreviousActions=False, relegateOrgId=None, diagnos=None,
                financeId=None, protocolQuoteId=None, actionByNewEvent=None, referrals=None, isAmb=True,
                recommendationList=None, useDiagnosticsAndActionsPresets=True, orgStructureId=None):
        if not actionByNewEvent:
            actionByNewEvent = []
        if not valueProperties:
            valueProperties = []
        if not referrals:
            referrals = {}
        self.setPersonId(personId)
        self.setOrgStructureId(orgStructureId)

        if hasattr(self, 'tabRecipes'):
            finalDiagnosis = self.getFinalDiagnostic()
            self.tabRecipes.setEventId(self.itemId(), financeId, finalDiagnosis, clientId, personId)
        if self.tabDestinations:
            self.tabDestinations.setEventId(self.itemId(), clientId, personId)
        plannerDate = self.getPlannerDate(eventSetDatetime, eventDatetime)

        if QtGui.qApp.userHasRight(urAccessF025planner):
            dlg = CPreF025Dialog(self, self.contractTariffCache)
            dlg.prepare(clientId, eventTypeId, plannerDate, self.personId, self.personSpecialityId,
                        self.personTariffCategoryId, flagHospitalization, actionTypeIdValue, tissueTypeId,
                        recommendationList, useDiagnosticsAndActionsPresets=useDiagnosticsAndActionsPresets)
            if dlg.diagnosticsTableIsNotEmpty() or dlg.actionsTableIsNotEmpty():
                if not dlg.exec_():
                    return False
            return self._prepare(None, clientId, eventTypeId, orgId, personId, eventSetDatetime, eventDatetime, includeRedDays, numDays,
                                 dlg.diagnostics(), dlg.actions(), dlg.disabledActionTypeIdList, dlg.notDeletedActionTypes,
                                 externalId, assistantId, curatorId, actionTypeIdValue, valueProperties, relegateOrgId, diagnos, financeId, protocolQuoteId, actionByNewEvent,
                                 referrals=referrals, isAmb=isAmb, recommendationList=recommendationList)
        else:
            presets = CPreF025DagnosticAndActionPresets(clientId, eventTypeId, plannerDate, self.personSpecialityId,
                                                        flagHospitalization, actionTypeIdValue, recommendationList,
                                                        useDiagnosticsAndActionsPresets=useDiagnosticsAndActionsPresets)
            return self._prepare(None, clientId, eventTypeId, orgId, personId, eventSetDatetime, eventDatetime, includeRedDays, numDays,
                                 presets.unconditionalDiagnosticList, presets.unconditionalActionList, presets.disabledActionTypeIdList, presets.notDeletedActionTypes,
                                 externalId, assistantId, curatorId, None, [], relegateOrgId, diagnos, financeId, protocolQuoteId, actionByNewEvent,
                                 referrals=referrals, isAmb=isAmb, recommendationList=recommendationList)


    def prepareActions(self, presetActions, disabledActions, notDeletedActions, valueProperties, diagnos, financeId, protocolQuoteId, actionByNewEvent):
        def addActionType(actionTypeId, amount, idListActionType, idListActionTypeIPH, actionFinance, idListActionTypeMoving, org_id):
            for model in [self.tabStatus.modelAPActions,
                          self.tabDiagnostic.modelAPActions,
                          self.tabCure.modelAPActions,
                          self.tabMisc.modelAPActions,
                          self.tabAnalyses.modelAPActions]:
                model.setNotDeletedActionTypes(notDeletedActions)
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
                          self.tabMisc.modelAPActions,
                          self.tabAnalyses.modelAPActions]:
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


    def initFocus(self):
        if self.cmbContract.count() != 1:
            self.cmbContract.setFocus(QtCore.Qt.OtherFocusReason)
        else:
            self.tblFinalDiagnostics.setFocus(QtCore.Qt.OtherFocusReason)


#    def getQuotaTypeId(self):
#        quotaTypeId = None
#        db = QtGui.qApp.db
#        tableClientQuoting = db.table('Client_Quoting')
#        tableActionType = db.table('ActionType')
#        recordActionType = db.getRecordEx(tableActionType, [tableActionType['id']], [tableActionType['deleted'].eq(0), tableActionType['flatCode'].like(u'protocol')])
#        actionTypeId = forceRef(recordActionType.value('id')) if recordActionType else None
#
#        def getQuotaTypeIsModel(model):
#            db = QtGui.qApp.db
#            tableClientQuoting = db.table('Client_Quoting')
#            for record, action in model.items():
#                propertiesByIdList = action._actionType._propertiesById
#                for propertiesBy in propertiesByIdList.values():
#                    if u'квота пациента' in propertiesBy.typeName.lower():
#                        propertiesById = propertiesBy.id
#                        if propertiesById:
#                            quotaId = action._propertiesById[propertiesById].getValue()
#                            if quotaId:
#                                record = db.getRecordEx(tableClientQuoting, [tableClientQuoting['quotaType_id']], [tableClientQuoting['deleted'].eq(0), tableClientQuoting['id'].eq(quotaId)])
#                                if record:
#                                    quotaTypeId = forceRef(record.value('quotaType_id'))
#                                    if quotaTypeId:
#                                        return quotaTypeId
#            return None
#
#        for model in [self.tabStatus.modelAPActions,
#              self.tabDiagnostic.modelAPActions,
#              self.tabCure.modelAPActions,
#              self.tabMisc.modelAPActions]:
#            if actionTypeId in model.actionTypeIdList:
#                for record, action in model.items():
#                    if actionTypeId == action._actionType.id:
#                        quotaTypeId = getQuotaTypeIsModel(model)
#
#
#
#
#        return quotaTypeId


    def newDiagnosticRecord(self, template):
        result = self.tblFinalDiagnostics.model().getEmptyRecord()
        return result


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
        self.loadVisits()
        self.loadDiagnostics(self.itemId())
        self.updateResultFilter()
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
        self.tabReferralPage.setRecord(record)
        self.initFocus()
        self.setIsDirty(False)
        self.blankMovingIdList = []
        payStatus = self.getEventPayStatus()
        self.addPayStatusBar(payStatus)
        self.setEditable(self.getEditable())
        self.addVisits()
        self.edtCycleDay.setValue(forceInt(record.value('cycleDay')))

        if hasattr(self, 'tabRecipes'):
            finalDiagnosis = self.getFinalDiagnostic()
            self.tabRecipes.setEventId(self.itemId(), self.eventFinanceId, finalDiagnosis, self.clientId, self.personId)
        if self.tabDestinations:
            self.tabDestinations.setEventId(self.itemId(), self.clientId, self.personId)
        self.postUiSet = True
        setOrgStructureIdToCmbPerson(self.cmbPerson)

    def setEditable(self, editable):
        self.modelVisits.setEditable(editable)
        self.modelActionsSummary.setEditable(editable)
        self.modelDiagnostics.setEditable(editable or QtGui.qApp.userHasRight(urEditDiagnosticsInPayedEvents))
        self.grpBase.setEnabled(editable)
        self.tabMes.setEnabled(editable)
        self.tabStatus.setEditable(editable)
        self.tabDiagnostic.setEditable(editable)
        self.tabCure.setEditable(editable)
        self.tabMisc.setEditable(editable)
        self.tabAnalyses.setEditable(editable)
        #tabTempInvalidEtc
        self.grpDisability.setEnabled(editable)
        self.grpVitalRestriction.setEnabled(editable)
        self.tabTempInvalid.setEnabled(editable)
        # self.tabAegrotat.setEnabled(editable)
        #end of tabTempInvalidEtc
        self.tabCash.setEditable(editable)
        self.tabNotes.setEditable(editable)


    def setLeavedAction(self, actionTypeIdValue):
        currentDateTime = QtCore.QDateTime.currentDateTime()
        flatCode = u'moving%'
        db = QtGui.qApp.db
        tableActionType = db.table('ActionType')
        idListActionType = db.getIdList(tableActionType, [tableActionType['id']], [tableActionType['flatCode'].like(flatCode), tableActionType['deleted'].eq(0)])
        for model in [self.tabStatus.modelAPActions,
                      self.tabDiagnostic.modelAPActions,
                      self.tabCure.modelAPActions,
                      self.tabMisc.modelAPActions,
                      self.tabAnalyses.modelAPActions]:
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
            self.loadDiagnostics(eventId)


    def loadDiagnostics(self, eventId):
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


    def loadActions(self):
        eventId = self.itemId()
        self.tabStatus.loadActionsLite(eventId)
        self.tabDiagnostic.loadActionsLite(eventId)
        self.tabCure.loadActionsLite(eventId)
        self.tabMisc.loadActionsLite(eventId)
        self.tabAnalyses.loadActionsLite(eventId)
        self.modelActionsSummary.regenerate()
        self.tabCash.modelAccActions.regenerate()


    def getRecord(self):
        record = CEventEditDialog.getRecord(self)
        showTime = getEventShowTime(self.eventTypeId)
        oldNextDate = forceDate(record.value('nextEventDate'))
        oldPersonId = forceRef(record.value('execPerson_id'))

#перенести в exec_ в случае успеха или в accept?
        #FIXME: atronah: self.cmbContract не является наследником CRBComboBox и вызывать для него getRBComboBoxValue - не стоит
        getRBComboBoxValue(self.cmbContract,    record, 'contract_id')
        getDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'setDate', showTime)
        getRBComboBoxValue(self.cmbPerson,      record, 'setPerson_id')
        getDatetimeEditValue(self.edtEndDate, self.edtEndTime, record, 'execDate', showTime)
        getRBComboBoxValue(self.cmbPerson,      record, 'execPerson_id')
        getRBComboBoxValue(self.cmbResult,      record, 'result_id')
        getDateEditValue(self.edtNextDate,      record, 'nextEventDate')
        nextDate = self.edtNextDate.date()
        personId = self.cmbPerson.value()

        record.setValue('cycleDay', toVariant(self.edtCycleDay.value()))

        if not oldNextDate or not oldPersonId:
            self.createNextEvent(personId, nextDate, True)

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
        super(CF025BaseDialog, self).saveInternals(eventId)
        self.saveVisits(eventId)
        self.saveDiagnostics(eventId)
        setAskedClassValueForDiagnosisManualSwitch(None)
        if self.isTabTempInvalidEtcAlreadyLoad:
            self.grpTempInvalid.saveTempInvalid()
            # self.grpAegrotat.saveTempInvalid()
            self.grpDisability.saveTempInvalid()
            self.grpVitalRestriction.saveTempInvalid()

        #self.updateVisits(eventId, self.modelFinalDiagnostics)  # i2809
        self.saveActions(eventId)
        self.tabCash.save(eventId)
        # self.tabNotes.saveOutgoingRef(eventId)
        self.saveBlankUsers(self.blankMovingIdList)
        self.updateRecipes(eventId)
        if hasattr(self, 'tabRecipes'):
            self.tabRecipes.saveData(eventId)

        self.updateRecommendations()

    def updateRecipes(self, eventId):
        db = QtGui.qApp.db
        stmt = u'UPDATE DrugRecipe SET event_id=%d WHERE event_id=0' % forceInt(eventId)
        db.query(stmt)


    def saveVisits(self, eventId):
        items = self.modelVisits.items()
        personIdVariant = toVariant(self.personId)
#        financeIdVariant = QtGui.qApp.db.translate('Person', 'id', personIdVariant, 'finance_id')

        for item in items :
            item.setValue('person_id', personIdVariant)
#            item.setValue('finance_id', financeIdVariant)
        self.modelVisits.saveItems(eventId)


    def updateDiagnosisTypes(self):
        items = self.modelDiagnostics.items()
        isFirst = True
        for item in items :
            diagnosisTypeId = self.getDiagnosisTypeId(isFirst)
            item.setValue('diagnosisType_id', toVariant(diagnosisTypeId))
            isFirst = False


    def saveDiagnostics(self, eventId):
        person = self.personId if self.personId else self.cmbPerson.personId
        items = self.modelDiagnostics.items()
        isDiagnosisManualSwitch = self.modelDiagnostics.manualSwitchDiagnosis()
        isFirst = True
        endDate = self.edtEndDate.date()
        endDateVariant = toVariant(endDate)
        begDate = self.edtBegDate.date()
        personIdVariant = toVariant(person)
        specialityIdVariant = QtGui.qApp.db.translate('Person', 'id', personIdVariant, 'speciality_id')
        MKBDiagnosisIdPairList = []
        prevId = 0
        for item in items:
            MKB           = forceString(item.value('MKB'))
            MKBEx         = forceString(item.value('MKBEx'))
            TNMS          = forceString(item.value('TNMS'))
            morphologyMKB = forceString(item.value('morphologyMKB'))
            if self.diagnosisSetDateVisible == False:
                item.setValue('setDate', endDateVariant)
                date = forceDate(endDateVariant)
            else:
                date = forceDate(item.value('setDate'))
            diagnosisTypeId = self.getDiagnosisTypeId(isFirst)
            item.setValue('diagnosisType_id', toVariant(diagnosisTypeId))
            item.setValue('speciality_id', specialityIdVariant)
            item.setValue('person_id', toVariant(person))
            item.setValue('endDate', endDateVariant)
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

    def saveActions(self, eventId):
        self.tabStatus.saveActions(eventId)
        self.tabDiagnostic.saveActions(eventId)
        self.tabCure.saveActions(eventId)
        self.tabMisc.saveActions(eventId)
        self.tabAnalyses.saveActions(eventId)

    def setOrgId(self, orgId):
        self.orgId = orgId
        self.cmbContract.setOrgId(orgId)

        if self.isTabStatusAlreadyLoad:
            self.tabStatus.setOrgId(orgId)
        if self.isTabDiagnosticAlreadyLoad:
            self.tabDiagnostic.setOrgId(orgId)
        if self.isTabCureAlreadyLoad:
            self.tabCure.setOrgId(orgId)
        if self.isTabMiscAlreadyLoad:
            self.tabMisc.setOrgId(orgId)
        if self.isTabAnalysesAlreadyLoad:
            self.tabAnalyses.setOrgId(orgId)

        # if not self.itemId():
        self.cmbPerson.setOrgId(orgId)

    def setExternalId(self, externalId):
        self.lblValueExternalId.setText((u'Внешний идентификатор: ' + externalId) if externalId else '')


    def setEventTypeId(self, eventTypeId):
        CEventEditDialog.setEventTypeId(self, eventTypeId, u'Ф.025')
        self.tabCash.windowTitle = self.windowTitle()
        showTime = getEventShowTime(eventTypeId)
        self.edtBegTime.setVisible(showTime)
        self.edtEndTime.setVisible(showTime)
        if self.cmbResult.value() is None:
            if self.inheritResult == True:
                self.cmbResult.setValue(self.defaultEventResultId.get(self.eventPurposeId))
        self.updateResultFilter()
        self.setVisitAssistantVisible(self.tblVisits, hasEventVisitAssistant(eventTypeId))
        customizePrintButton(self.btnPrint, self.eventContext if self.eventContext else 'F025')
        self.diagnosisSetDateVisible = forceBool(getDiagnosisSetDateVisible(eventTypeId))
        if self.diagnosisSetDateVisible == False:
            self.tblFinalDiagnostics.setColumnHidden(2, True)


    def updateMKB(self):
        begDate = self.edtBegDate.date()
        filter = None
        if begDate.isValid():
            filter = {'begDate': begDate, 'clientId': self.clientId}
        cols = self.modelDiagnostics.cols()
        for col in (0, 1):
            resultCol = cols[col]
            resultCol.setFilter(filter)

    def resetActionTemplateCache(self):
        self.tabStatus.actionTemplateCache.reset()
        self.tabDiagnostic.actionTemplateCache.reset()
        self.tabCure.actionTemplateCache.reset()
        self.tabMisc.actionTemplateCache.reset()
        self.tabAnalyses.actionTemplateCache.reset()

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
        result = checkTempInvalidNumber(self, self.grpTempInvalid.edtTempInvalidNumber.text())
        result = result and CEventEditDialog.checkDataEntered(self)
        self.blankMovingIdList = []
        result = result and (self.orgId != QtGui.qApp.currentOrgId() or self.cmbContract.value() or self.checkInputMessage(u'договор', False, self.cmbContract))
        result = result and (self.cmbPerson.value()   or self.checkInputMessage(u'врач',        False, self.cmbPerson))
#        result = result and (self.cmbResult.value()   or self.checkInputMessage(u'результат',   False, self.cmbResult))
        begDate = self.edtBegDate.date()
        endDate = self.edtEndDate.date() if self._isClosedEventCheck else QtCore.QDate()
        nextDate = self.edtNextDate.date()
        if self.tabDestinations:
            result = result and self.tabDestinations.checkDataEntered()
        result = result and (not begDate.isNull() or self.checkInputMessage(u'дату назначения', False, self.edtBegDate))
        result = result and (not endDate.isNull() or self.checkInputMessage(u'дату выполнения', True, self.edtEndDate))
        if begDate:
            result = result and self.checkActionDataEntered(begDate, QtCore.QDate(), endDate, self.tabToken, self.edtBegDate, None, self.edtEndDate)
            result = result and self.checkEventDate(begDate, endDate, nextDate, self.tabToken, self.edtNextDate, self.edtEndDate, True)
            minDuration,  maxDuration = getEventDuration(self.eventTypeId)
            if minDuration<=maxDuration and endDate:
                countRedDays = not QtGui.qApp.isExcludeRedDaysInEventLength()
                eventDuration = getEventLengthDays(begDate, endDate, countRedDays, self.eventTypeId)
                eventDurationErrorString = u'Указана длительность с учётом выходных: %s.'%formatNum(eventDuration, (u'день', u'дня', u'дней'))
                result = result and (eventDuration >= minDuration or
                                     self.checkValueMessage(u'Длительность должна быть не менее %s. %s'%(formatNum(minDuration, (u'дня', u'дней', u'дней')), eventDurationErrorString), False, self.edtEndDate))
                result = result and (maxDuration==0 or eventDuration <= maxDuration or
                                     self.checkValueMessage(u'Длительность должна быть не более %s. %s'%(formatNum(maxDuration, (u'дня', u'дней', u'дней')), eventDurationErrorString), False, self.edtEndDate))

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
        
        # if endDate and not QtGui.qApp.userHasRight(urDoNotCheckResultAndMKB):
        #    result = result and (self.cmbResult.value() or self.checkInputMessage(u'результат', False, self.cmbResult))
        
        result = result and self.checkDiagnosticsDataEntered([(self.tblFinalDiagnostics, True, True, None)],
                                                             endDate)
        
        result = result and (len(self.modelVisits.items())>0 or self.checkInputMessage(u'посещение', False, self.tblVisits))
        result = result and self.checkVisitsDataEntered(begDate, endDate)
        result = result and self.checkActionsDateEnteredActuality(begDate, endDate, [self.tabStatus, self.tabDiagnostic, self.tabCure, self.tabMisc, self.tabAnalyses])
        result = result and self.checkActionsDataEntered([self.tabStatus, self.tabDiagnostic, self.tabCure, self.tabMisc, self.tabAnalyses], begDate, endDate)
        if self.isTabTempInvalidEtcAlreadyLoad:
            result = result and self.grpTempInvalid.checkTempInvalidDataEntered()
            # result = result and self.grpAegrotat.checkTempInvalidDataEntered()
            result = result and self.grpDisability.checkTempInvalidDataEntered()
            result = result and self.grpVitalRestriction.checkTempInvalidDataEntered()
        result = result and (self.itemId() or self.primaryCheck(self.modelDiagnostics))
        if self.isTabCashAlreadyLoad:
            result = result and self.tabCash.checkDataLocalContract()
        result = result and self.checkSerialNumberEntered()
        result = result and self.checkTabNotesReferral()

        if \
                self.getFinalDiagnosisMKB()[0] is not None and self.getFinalDiagnosisMKB()[0] != u'' and self.getFinalDiagnosisMKB()[0][0] == u'C' \
                and not QtGui.qApp.userHasRight(urOncoDiagnosisWithoutTNMS)\
                and QtGui.qApp.isTNMSVisible() and (self.getModelFinalDiagnostics().items()[0].value('TNMS') is None or
                                forceString(self.getModelFinalDiagnostics().items()[0].value('TNMS')) == ''):
            result = result and self.checkValueMessage(check_data_text_TNM, False, None)
        return result


    def checkDiagnosticsMKBForMes(self, tableFinalDiagnostics, SPR69_id):
        return self.checkMKBForMes(tableFinalDiagnostics, SPR69_id, self.getDiagnosisTypeId(True))[0]


    def checkSerialNumberEntered(self):
        result = True
        self.blankMovingIdList = []
        db = QtGui.qApp.db
        table = db.table('ActionPropertyType')
        actionTypeIdListSerial = db.getDistinctIdList(table, [table['actionType_id']], [table['deleted'].eq(0), table['typeName'].like('BlankSerial')])

        for tab in [self.tabStatus,
                    self.tabDiagnostic,
                    self.tabCure,
                    self.tabMisc,
                    self.tabAnalyses]:
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

    def checkDiagnosticDoctorEntered(self, table, row, record):
        return True

#    def getMaxEndDateByVisits(self):
#        result = QtCore.QDate()
#        for record in self.modelVisits.items():
#            date = forceDate(record.value('date'))
#            if date.isNull() or result<date:
#                result = date
#        return result


#    def checkDiagnosticsDataEntered(self, endDate):
#        if QtGui.qApp.userHasRight(urDoNotCheckResultAndMKB):
#            return True
#        if endDate and len(self.modelDiagnostics.items()) <= 0:
#            self.checkInputMessage(u'диагноз', False, self.tblFinalDiagnostics)
#            return False
#        for row, record in enumerate(self.modelDiagnostics.items()):
#            if not self.checkDiagnosticDataEntered(row, record):
#                return False
#        return True
#
#
#    def checkDiagnosticDataEntered(self, row, record):
####     self.checkValueMessage(self, message, canSkip, widget, row=None, column=None):
#        result = True
#        if result:
#            MKB = forceString(record.value('MKB'))
#            result = MKB or self.checkInputMessage(u'диагноз', False, self.tblFinalDiagnostics, row, record.indexOf('MKB'))
#            if result:
#                char = MKB[:1]
#                traumaTypeId = forceRef(record.value('traumaType_id'))
#                if char in 'ST' and not traumaTypeId:
#                    result = self.checkValueMessage(u'Необходимо указать тип травмы', True, self.tblFinalDiagnostics, row, record.indexOf('traumaType_id'))
#                if char not in 'ST' and traumaTypeId:
#                    result = self.checkValueMessage(u'Необходимо удалить тип травмы', False, self.tblFinalDiagnostics, row, record.indexOf('traumaType_id'))
#        if result and row == 0:
#            resultId = forceRef(record.value('result_id'))
#            result = resultId or self.checkInputMessage(u'результат', False, self.tblFinalDiagnostics, row, record.indexOf('result_id'))
##        result = result and (self.cmbResult.value()   or self.checkInputMessage(u'результат',   False, self.cmbResult))
#        return result


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

    def getDiagnosisTypeId(self, isFirstDiagnostic):
        """
        Возвращает id типа диагноза.

        :param isFirstDiagnostic: признак того, что это первый диагноз
        :return: id заключительного диагноза (code = '2'), для первого диагноза, и id сопутствующего (code = '9') для остальных
        """
        return self.modelDiagnostics.mainDiagnosisId if isFirstDiagnostic else self.modelDiagnostics.concominantDiagnosisId

    def getEventInfo(self, context):
        if not self.isTabCashAlreadyLoad:
            self.initTabCash(False)
        result = CEventEditDialog.getEventInfo(self, context)
        # ручная инициализация свойств
        result._isPrimary = self.cmbPrimary.currentIndex() + 1
        # ручная инициализация таблиц
        result._actions = CActionInfoProxyList(context,
                [self.tabStatus.modelAPActions, self.tabDiagnostic.modelAPActions, self.tabCure.modelAPActions, self.tabMisc.modelAPActions, self.tabAnalyses.modelAPActions],
                result)
        self.updateDiagnosisTypes()
        result._diagnosises = CDiagnosticInfoProxyList(context, [self.modelDiagnostics])
        result._visits = CVisitInfoProxyList(context, self.modelVisits)
        return result

    def getTempInvalidInfo(self, context):
        return self.grpTempInvalid.getTempInvalidInfo(context)

    # def getAegrotatInfo(self, context):
    #     return self.grpAegrotat.getTempInvalidInfo(context)

    def updateMesMKB(self):
        self.tabReferralPage.setMKB(self.getFinalDiagnosisMKB()[0])
        self.tabMes.setMKB(self.getFinalDiagnosisMKB()[0])

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

    def initTabAnalyses(self, show=True):
        if show: self.tabAnalyses.setVisible(False)
        self.tabAnalyses.preSetupUi()
        self.tabAnalyses.clearBeforeSetupUi()
        self.tabAnalyses.setupUi(self.tabAnalyses)
        self.tabAnalyses.postSetupUi()
        self.tabAnalyses.updateActionEditor()
        self.tabAnalyses.setOrgId(self.orgId)
        self.tabAnalyses.setEndDate(self.eventSetDateTime.date())
        if show: self.tabAnalyses.setVisible(True)

        self.isTabAnalysesAlreadyLoad = True

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
        if self.isTabAnalysesAlreadyLoad:
            self.tabAnalyses.setEndDate(date)
        self.tabNotes.updateReferralPeriod(date)
        self.updateResultFilter()
        if QtGui.qApp.isCheckMKB():
            self.updateMKB()
        self.emitUpdateActionsAmount()
        self.setContract()

        self.updateModelsRetiredList()

        self.tabMes.setBegDate(date)

    @QtCore.pyqtSlot(QtCore.QTime)
    def on_edtBegTime_timeChanged(self, time):
        self.emitUpdateActionsAmount()

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtEndDate_dateChanged(self, date):
        self.emitUpdateActionsAmount()
        self.modelActionsSummary.updateRetiredList()		# !!! add after merge !!!
        self.addVisits()
        self.setContract()

        self.tabMes.setEndDate(date)
        self.tabNotes.cmbClientPolicy.updatePolicy(date)
        if QtGui.qApp.isAutoClosed():
            if hasattr(self, 'chkIsClosed'):
                self.chkIsClosed.setChecked(date != QtCore.QDate())

    @QtCore.pyqtSlot(int)
    def on_cmbPerson_currentIndexChanged(self):
        oldPersonId = self.personId
        self.setPersonId(self.cmbPerson.value())
        if self.postUiSet:
            self.modelVisits.updatePersonAndService()
# что-то сомнительным показалось - ну поменяли отв. врача,
# всё равно менять врачей в действии вроде неправильно. или правильно?
        self.tabStatus.updatePersonId(oldPersonId, self.personId)
        self.tabDiagnostic.updatePersonId(oldPersonId, self.personId)
        self.tabCure.updatePersonId(oldPersonId, self.personId)
        self.tabMisc.updatePersonId(oldPersonId, self.personId)
        self.tabAnalyses.updatePersonId(oldPersonId, self.personId)

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
    def on_mnuDiagnostics_aboutToShow(self):
        canRemove = False
        currentRow = self.tblFinalDiagnostics.currentIndex().row()
        if currentRow>=0 :
            canRemove = self.modelDiagnostics.payStatus(currentRow) == 0
        self.actDiagnosticsRemove.setEnabled(canRemove)

    @QtCore.pyqtSlot()
    def on_modelDiagnostics_diagnosisChanged(self):
        self.updateMesMKB()

    @QtCore.pyqtSlot()
    def on_modelDiagnostics_diagnosisServiceChanged(self):
        diagnosis = self.modelDiagnostics.getFinalDiagnosis()
        if diagnosis:
            mkbCode = forceString(diagnosis.value('MKB'))
            if CDiagnosisServiceMap.get(mkbCode):
                self.modelVisits.updatePersonAndService()

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
        self.modelDiagnostics.setResult(getResultIdByDiagnosticResultId(self.cmbResult.value()))


class CF025Dialog(CF025BaseDialog):
    """
        Отличается отсутствием столбца "Врач" в таблице "Посещения"
    """
    def __init__(self, parent):
        CF025BaseDialog.__init__(self, parent)
        self.tblVisits.hideColumn(self.modelVisits.getColIndex('person_id'))
        self.cmbHMPKind.setVisible(False)
        self.lblHMPKind.setVisible(False)
        self.cmbHMPMethod.setVisible(False)
        self.lblHMPMethod.setVisible(False)


class CF025ExtendedDialog(CF025BaseDialog):
    formTitle = u'Ф.025/р'

    def __init__(self, parent):
        self.listMethodId = []
        self.methodLock = False

        CF025BaseDialog.__init__(self, parent)
        self.grpBase.setTitle(self.formTitle.lower())
        self.cmbHMPKind.setTable('rbHighTechCureKind', addNone=True)
        self.cmbHMPKind.setEnabled(False)
        self.cmbHMPMethod.setTable('rbHighTechCureMethod', addNone=True)
        self.loadMethod()
        self.connect(self.modelDiagnostics,  QtCore.SIGNAL('rowDeleted(int)'), self.on_modelDiagnostics_rowDeleted)

    def on_cmbHMPKind_currentIndexChanged(self, index):
        self.cmbHMPKind.setToolTip(self.cmbHMPKind.currentText())

    def on_cmbHMPMethod_currentIndexChanged(self, index):
        if self.methodLock:
           return
        db = QtGui.qApp.db
        cureMethodId = forceRef(self.cmbHMPMethod.value())
        currentIndex = self.cmbHMPMethod.currentIndex()
        if cureMethodId:
            listId = db.getIdList('rbHighTechCureMethod', 'cureKind_id', 'id = %d' %cureMethodId, limit=1)
            newIndex = self.cmbHMPKind.model().searchId(listId[0]) if listId else 0
            oldIndex = self.cmbHMPKind.currentIndex()
            newIndex = 0 if newIndex == -1 else newIndex
            if oldIndex != newIndex:
                self.cmbHMPKind.setCurrentIndex(newIndex)
        else:
            self.methodLock = True
            self.cmbHMPMethod.setCurrentIndex(0)
            self.cmbHMPKind.setCurrentIndex(0)
            self.methodLock = False

    def loadMethod(self, value = None, index = 0, load = False):
        db = QtGui.qApp.db
        if index > 0:
            listId = db.getIdList('rbHighTechCureMethod', 'cureKind_id', 'id = %d' %value, limit=1)
            newIndex = self.cmbHMPKind.model().searchId(listId[0]) if listId else 0
            oldIndex = self.cmbHMPKind.currentIndex()
            newIndex = 0 if newIndex == -1 else newIndex
            self.cmbHMPKind.setCurrentIndex(newIndex)
            self.methodLock = True
            self.cmbHMPMethod.setCurrentIndex(index)
            self.methodLock = False
            return

        if not load:
            self.cmbHMPKind.setCurrentIndex(0)
            self.methodLock = True
            self.cmbHMPMethod.setCurrentIndex(0)
            self.methodLock = False
            return

        recordIndex = 0
        recordMethodId = None
        if self._record:
            recordMethodId = forceRef(self._record.value('hmpMethod_id'))
            recordIndex = self.cmbHMPMethod.model().searchId(recordMethodId)
            recordIndex = 0 if recordIndex == -1 else recordIndex
        if recordMethodId:
            listId = db.getIdList('rbHighTechCureMethod', 'cureKind_id', 'id = %d' %recordMethodId, limit=1)
            newIndex = self.cmbHMPKind.model().searchId(listId[0]) if listId else 0
            oldIndex = self.cmbHMPKind.currentIndex()
            newIndex = 0 if newIndex == -1 else newIndex
            self.cmbHMPKind.setCurrentIndex(newIndex)
            self.methodLock = True
            self.cmbHMPMethod.setCurrentIndex(recordIndex)
            self.methodLock = False

    def getRecord(self):
        record = CF025BaseDialog.getRecord(self)
        getRBComboBoxValue(self.cmbHMPKind, record, 'hmpKind_id')
        getRBComboBoxValue(self.cmbHMPMethod, record, 'hmpMethod_id')
        return record

    def setRecord(self, record):
        CF025BaseDialog.setRecord(self, record)
        setRBComboBoxValue(self.cmbHMPKind, record, 'hmpKind_id')
        setRBComboBoxValue(self.cmbHMPMethod, record, 'hmpMethod_id')
        self.setMethodFilter(load=True)
        self.tabReferralPage.setRecord(record)

    @QtCore.pyqtSlot()
    def on_modelDiagnostics_diagnosisChanged(self):
        CF025BaseDialog.on_modelDiagnostics_diagnosisChanged(self)
        self.setMethodFilter()
        #self.modelDiagnostics.mainDiagnosisId == forceInt(self.modelDiagnostics.items()[0].value('diagnosisType_id'))

    @QtCore.pyqtSlot(int)
    def on_modelDiagnostics_rowDeleted(self, row):
        if row == 0:
            self.setMethodFilter()

    def setMethodFilter(self, load = False):
        value = self.cmbHMPMethod.value()
        self.cmbHMPMethod.setFilter(self.makeFilter(updateList=True))
        index = self.cmbHMPMethod.model().searchId(value)
        self.loadMethod(value, index, load)

    def makeFilter(self, updateList=False):
        db = QtGui.qApp.db
        if not self.listMethodId or updateList:
            self.listMethodId = db.getDistinctIdList('rbHighTechCureMethodDiag', 'cureMethod_id', "Locate(MKB, '%s')" %forceString(self.modelDiagnostics._items[0].value('MKB'))) \
                if len(self.modelDiagnostics._items) else []
        cond = [u'id in (%s)' %u','.join([str(item) for item in self.listMethodId])] if self.listMethodId else [u'0']
        return db.joinAnd(cond)
    
    def checkTabNotesReferral(self):
        isCrimea = QtGui.qApp.region() == '91'
        if isCrimea:    
            if QtGui.qApp.isReferralRequired():
                if not self.tabNotes.chkLPUReferral.isChecked():
                    self.checkInputMessage(u'данные о направлении', skipable=False, widget=self.tabNotes.chkLPUReferral)
                    return False
                numRow = self.tabNotes.cmbNumber.currentIndex()
                numText = forceString(self.tabNotes.cmbNumber.lineEdit().text()).strip()
                numRight = QtGui.qApp.userHasRight(urCreateReferral)
                if numRow == 0:
                    if not numRight and numText:
                        QtGui.QMessageBox.critical(self, u'Внимание!', u'Вы не имеете права создавать направления.\nПожалуйста, выберите одно из уже существующих.', QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                        self.setFocusToWidget(self.tabNotes.cmbNumber)
                        return False
                    elif not numText:
                        self.checkInputMessage(u'номер направления', skipable=False, widget=self.tabNotes.cmbNumber)
                        return False

                elif numRow != 0 and not numText:
                    self.checkInputMessage(u'номер направления', skipable=False, widget=self.tabNotes.cmbNumber)
                    return False
                if self.tabNotes.cmbRelegateOrg.currentIndex()==0 and not forceString(self.tabNotes.edtFreeInput.text()).strip():
                    self.checkInputMessage(u'организацию направителя', skipable=False, widget=self.tabNotes.cmbRelegateOrg)
                    return False
                if self.tabNotes.chkArmyReferral.isChecked():
                    numRow = self.tabNotes.cmbArmyNumber.currentIndex()
                    numText = forceString(self.tabNotes.cmbArmyNumber.lineEdit().text()).strip()
                    numRight = QtGui.qApp.userHasRight(urCreateReferral)
                    if numRow == 0:
                        if not numRight and numText:
                            QtGui.QMessageBox.critical(self, u'Внимание!', u'Вы не имеете права создавать направления.\nПожалуйста, выберите одно из уже существующих.', QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                            self.setFocusToWidget(self.tabNotes.cmbArmyNumber)
                            return False
                        elif not numText:
                            boxResult = QtGui.QMessageBox.critical(self, u'Внимание!', u'Не указан номер направления. Не создавать направление для обращения?', QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Ok)
                            if boxResult == QtGui.QMessageBox.Ok:
                                self.tabNotes.dontSaveReferral = True
                                return True
                            self.tabNotes.dontSaveReferral = False
                            self.setFocusToWidget(self.tabNotes.cmbArmyNumber)
                            return False
    
                    elif numRow != 0 and not numText:
                        boxResult = QtGui.QMessageBox.critical(self, u'Внимание!', u'Не указан номер направления. Не прикреплять обращение к направлению?', QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Ok)
                        if boxResult == QtGui.QMessageBox.Ok:
                            self.tabNotes.dontSaveReferral = True
                            return True
                        self.tabNotes.dontSaveReferral = False
                        self.setFocusToWidget(self.tabNotes.cmbArmyNumber)
                        return False
                    elif not forceString(self.tabNotes.edtArmyDate.text()).strip():
                        boxResult = QtGui.QMessageBox.critical(self, u'Внимание!', u'Не указана организация направителя. Не прикреплять обращение к направлению?', QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Ok)
                        if boxResult == QtGui.QMessageBox.Ok:
                            self.tabNotes.dontSaveReferral = True
                            return True
                        self.tabNotes.dontSaveReferral = False
                        self.setFocusToWidget(self.tabNotes.edtArmyDate)
                        return False
            return True
        else:
            return super(CF025ExtendedDialog, self).checkTabNotesReferral()


class CF025DiagnosticsModel(CInDocTableModel):
    __pyqtSignals__ = ('diagnosisServiceChanged()',
                       'diagnosisChanged()',
                       'resultChanged()',
                       'rowDeleted(int)',
                      )
    MKB_allowed_morphology = ['C', 'D']

    def __init__(self, parent):
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
        self.addCol(CDiseaseCharacter(     u'Хар',           'character_id',   7, showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(u'Характер')
        if self.isManualSwitchDiagnosis:
            self.addExtCol(CBoolInDocTableCol( u'П',   'handleDiagnosis', 10), QtCore.QVariant.Int)
            self.characterIdForHandleDiagnosis = forceRef(QtGui.qApp.db.translate('rbDiseaseCharacter', 'code', '1', 'id'))
            self.columnHandleDiagnosis = self._mapFieldNameToCol.get('handleDiagnosis')

        self.addCol(CDiseasePhases(        u'Фаза',          'phase_id',       7, showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(u'Фаза')
        self.addCol(CDiseaseStage(         u'Ст',            'stage_id',       7, showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(u'Стадия')
        self.addCol(CRBInDocTableCol(      u'ДН',            'dispanser_id',   7, 'rbDispanser', showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(u'Диспансерное наблюдение')
        self.addCol(CRBLikeEnumInDocTableCol(u'Госп',        'hospital',       7, CHospitalInfo.names, showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(u'Потребность в госпитализации')
        self.addCol(CRBInDocTableCol(      u'Травма',        'traumaType_id', 10, 'rbTraumaType', addNone=True, showFields=CRBComboBox.showName, prefferedWidth=150))
        self.addCol(CRBInDocTableCol(      u'ГрЗд',          'healthGroup_id', 7, 'rbHealthGroup', addNone=True, showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(u'Группа здоровья')
        self.addCol(CRBInDocTableCol(forceTr(u'Результат', u'EventDiagnostic'),     'result_id',     10, 'rbDiagnosticResult', showFields=CRBComboBox.showNameAndCode, prefferedWidth=350))
        self.columnResult = self._mapFieldNameToCol.get('result_id')
        self.mapMKBToServiceId = {}
        self.eventEditor = parent

        self.mainDiagnosisId = forceRef(QtGui.qApp.db.translate('rbDiagnosisType', 'code', '2', 'id'))
        # atronah: Возможно не используется и нафиг не нужно.. в updatesDiagosisType все типы приводятся к заключительному.
        self.concominantDiagnosisId = forceRef(QtGui.qApp.db.translate('rbDiagnosisType', 'code', '9', 'id'))

        self.setEditable(True)

    def manualSwitchDiagnosis(self):
        return self.isManualSwitchDiagnosis

    def addRecord(self, record):
        super(CF025DiagnosticsModel, self).addRecord(record)
        self.emitResultChanged()

    def getEmptyRecord(self):
        result = CInDocTableModel.getEmptyRecord(self)
        result.append(QtSql.QSqlField('diagnosis_id',     QtCore.QVariant.Int))
        result.append(QtSql.QSqlField('diagnosisType_id', QtCore.QVariant.Int))
        result.append(QtSql.QSqlField('speciality_id',    QtCore.QVariant.Int))
        result.append(QtSql.QSqlField('person_id',        QtCore.QVariant.Int))
        result.append(QtSql.QSqlField('setDate',          QtCore.QVariant.DateTime))
        result.append(QtSql.QSqlField('endDate',          QtCore.QVariant.DateTime))
        result.append(QtSql.QSqlField('payStatus',        QtCore.QVariant.Int))
        isFirst = not self.items()
        if isFirst:
            if self._parent.inheritResult == True:
                result.setValue('result_id', toVariant(CEventEditDialog.defaultDiagnosticResultId.get(self._parent.eventPurposeId)))
            else:
                result.setValue('result_id', toVariant(None))

        # atronah: Не очень понимаю, зачем всем диагнозам кроме первого ставить тип "сопутствующий", если потом
        # вызовом функции CF025BaseDialog.updateDiagnosisTypes все диагнозы приводятся к типу "заключительный"
        result.setValue('diagnosisType_id',  toVariant(self.eventEditor.getDiagnosisTypeId(isFirst)))
        return result

    def getCloseOrMainDiagnosisTypeIdList(self):
        items = self.items()
        idList = []
        if len(items) > 0:
            idList = [forceRef(self.items()[0].value('diagnosisType_id'))]
        return idList

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
                    if not (bool(mkb) and mkb[0] in CF025DiagnosticsModel.MKB_allowed_morphology):
                        result = (result & ~QtCore.Qt.ItemIsEditable)
        if QtGui.qApp.isPNDDiagnosisMode() and (row == len(self.items()) or index.column() != self._mapFieldNameToCol.get('result_id')):
            result = (result & ~QtCore.Qt.ItemIsEditable)
        if not self.isEditable():
            result = (result & ~QtCore.Qt.ItemIsEditable)
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
                serviceId = self.diagnosisServiceId() if row == 0 else None
                result = CInDocTableModel.setData(self, index, value, role)
                if result:
                    self.updateCharacterByMKB(row, specifiedMKB, specifiedCharacterId)
                    self.updateTraumaType(row, specifiedMKB, specifiedTraumaTypeId)
                    if row == 0:
                        self.emit(QtCore.SIGNAL('diagnosisChanged()'))
                        # if serviceId != self.diagnosisServiceId():
                        self.emit(QtCore.SIGNAL('diagnosisServiceChanged()'))
                return result

            elif column == 1: # доп. код МКБ
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

            elif column == self.columnResult and row == 0:
                oldDesultId = self.resultId()
                result = CInDocTableModel.setData(self, index, value, role)
                if oldDesultId != self.resultId():
                    self.emitResultChanged()
                return result

            return CInDocTableModel.setData(self, index, value, role)
        else:
            return True

    def setResult(self,  resultID, onlyIfNone = True):
        items = self.items()
        if len(items) > 0 and (not onlyIfNone or forceRef(items[0].value('result_id')) is None):
            items[0].setValue('result_id', resultID)
            self.setItems(items)
            self.emitResultChanged()

    def payStatus(self, row):
        if 0 <= row < len(self.items()):
            return forceInt(self.items()[row].value('payStatus'))
        else:
            return 0

    def removeRowEx(self, row):
        self.removeRows(row, 1)
        if row == 0:
            self.emitResultChanged()
            self.emitFirstRowDeleted()

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

    def resultId(self):
        items = self.items()
        if items:
            return forceRef(items[0].value('result_id'))
        else:
            return None

    def getFinalDiagnosis(self):
        return self._items[0] if self._items else None

    def emitResultChanged(self):
        self.emit(QtCore.SIGNAL('resultChanged()'))

    def emitFirstRowDeleted(self):
        self.emitRowDeleted(0)

    def emitRowDeleted(self, row):
        self.emit(QtCore.SIGNAL('rowDeleted(int)'), row)
