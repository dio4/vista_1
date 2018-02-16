# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui, QtSql
from collections import defaultdict

from Events.Action import CActionType, CActionTypeCache, ActionStatus
from Events.ActionInfo import CActionInfoProxyList
from Events.ActionsSummaryModel import CFxxxActionsSummaryModel
from Events.DiagnosisType import CDiagnosisTypeCol
from Events.EventEditDialog import CDiseaseCharacter, CDiseasePhases, CDiseaseStage, CEventEditDialog
from Events.EventInfo import CDiagnosticInfoProxyList
from Events.Utils import CTableSummaryActionsMenuMixin, checkDiagnosis, checkIsHandleDiagnosisIsChecked, \
    getAvailableCharacterIdByMKB, getDiagnosisId2, getDiagnosisSetDateVisible, getEventAidTypeCode, \
    getEventDuration, getEventLengthDays, getEventShowTime, getEventTypeDefaultEndTime, \
    setAskedClassValueForDiagnosisManualSwitch, setOrgStructureIdToCmbPerson
from Forms.F003.PreF003Dialog import CPreF003DagnosticAndActionPresets, CPreF003Dialog
from Forms.F003.Ui_F003 import Ui_Dialog
from Forms.Utils import check_data_text_TNM
from Users.Rights import urAccessF003planner, urAdmin, urOncoDiagnosisWithoutTNMS, urRegTabWriteRegistry, \
    urSaveWithoutPrelimDiagF003, urSetEventExecDateF003, urSaveWithoutFinalDiagF003
from library.CSG.CSGComboBox import CCSGComboBox
from library.ICDInDocTableCol import CICDExInDocTableCol
from library.ICDMorphologyInDocTableCol import CMKBMorphologyCol
from library.InDocTable import CActionPersonInDocTableColSearch, CBoolInDocTableCol, CDateInDocTableCol, \
    CInDocTableModel, CRBInDocTableCol
from library.PrintInfo import CInfoContext
from library.PrintTemplates import applyTemplate, customizePrintButton, getPrintButton
from library.TNMS.TNMSComboBox import CTNMSCol
from library.Utils import copyFields, forceBool, forceDate, forceInt, forceRef, forceString, forceStringEx, forceTr, \
    formatNum, toVariant, variantEq, \
    calcAgeInYears
from library.crbcombobox import CRBComboBox
from library.interchange import getDatetimeEditValue, getRBComboBoxValue, setDatetimeEditValue, setRBComboBoxValue

# Форма 003: лечение в стационаре и т.п.


try:
    _encoding = QtGui.QApplication.UnicodeUTF8


    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class CF003Dialog(CEventEditDialog, Ui_Dialog, CTableSummaryActionsMenuMixin):
    isTabMesAlreadyLoad = False
    isTabStatusAlreadyLoad = False
    isTabDiagnosticAlreadyLoad = False
    isTabCureAlreadyLoad = False
    isTabMiscAlreadyLoad = False
    isTabAnalysesAlreadyLoad = False
    isTabAmbCardAlreadyLoad = False
    isTabTempInvalidEtcAlreadyLoad = False
    isTabFeedAlreadyLoaded = False
    isTabCashAlreadyLoad = False
    isTabNotesAlreadyLoad = False

    def __init__(self, parent):
        CEventEditDialog.__init__(self, parent)
        self.mapSpecialityIdToDiagFilter = {}

        self.addModels('PreliminaryDiagnostics', CF003PreliminaryDiagnosticsModel(self))
        self.addModels('FinalDiagnostics', CF003FinalDiagnosticsModel(self))
        self.addModels('ActionsSummary', CFxxxActionsSummaryModel(self, True, loadMedicaments=True, addTime=True))
        # ui
        self.createSaveAndCreateAccountButton()
        self.actEditClient = QtGui.QAction(u'Изменить описание клиента', self)
        self.actEditClient.setObjectName('actEditClient')
        self.btnPrint = getPrintButton(self, '')
        self.btnPrint.setObjectName('btnPrint')
        if QtGui.qApp.isNextEventCreationFromAction():
            self.btnRelatedEvent = QtGui.QPushButton(u'Связанные события', self)
            self.btnRelatedEvent.setObjectName('btnRelatedEvent')

        self.setupUi(self)
        if hasattr(self, 'tabMes'):
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

        self.tabFeed.preSetupUiMini()
        self.tabFeed.setupUiMini(self.tabFeed)
        self.tabFeed.setupUi(self.tabFeed)
        self.tabFeed.postSetupUiMini()

        self.tabCash.preSetupUiMini()
        self.tabCash.setupUiMini(self.tabCash)
        self.tabCash.postSetupUiMini()

        self.tabNotes.preSetupUiMini()
        self.tabNotes.preSetupUi()
        self.tabNotes.setupUiMini(self.tabNotes)
        self.tabNotes.setupUi(self.tabNotes)
        self.tabNotes.postSetupUiMini(self.edtBegDate.date())

        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Осмотр Ф.003')
        self.tabToken.setFocusProxy(self.tblFinalDiagnostics)
        if hasattr(self, 'tabMes'):
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
        if QtGui.qApp.isNextEventCreationFromAction():
            self.buttonBox.addButton(self.btnRelatedEvent, QtGui.QDialogButtonBox.ActionRole)
        self.setupActionSummarySlots()
        self.cmbIBLocation.setTable('rbHospitalBedsLocationCardType', True)
        self.cmbIBLocation.setShowFields(CRBComboBox.showCodeAndName)

        if QtGui.qApp.userHasRight('editCycleDay'):
            self.lblCycleDay.setVisible(True)
            self.edtCycleDay.setVisible(True)
        else:
            self.lblCycleDay.setVisible(False)
            self.edtCycleDay.setVisible(False)

        self.cmbContract.setCheckMaxClients(True)
        # tables to rb and combo-boxes

        # assign models
        self.tblPreliminaryDiagnostics.setModel(self.modelPreliminaryDiagnostics)
        self.tblFinalDiagnostics.setModel(self.modelFinalDiagnostics)
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

        # mark tables as editable to prevent saving event while editing child item
        self.markEditableTableWidget(self.tblPreliminaryDiagnostics)
        self.markEditableTableWidget(self.tblFinalDiagnostics)
        self.markEditableTableWidget(self.tblActions)

        # popup menus
        self.tblPreliminaryDiagnostics.addCopyDiagnos2Final(self)
        self.txtClientInfoBrowser.actions.append(self.actEditClient)
        self.actEditClient.setEnabled(QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteRegistry]))
        CTableSummaryActionsMenuMixin.__init__(self)

        self.setupDirtyCather()
        self.setIsDirty(False)
        self.blankMovingIdList = []
        self.clientId = None
        self.prolongateEvent = False
        self.prevEventId = None
        self.mesDurationsMap = {}
        self.tabNotes.setEventEditor(self)
        self.valueForAllActionEndDate = None
        self.cmbResult.setShowFields(CRBComboBox.showCodeAndName)

        self.postSetupUi()
        self.tabNotes.useBtnExternalIdupd(self.updateExternalId)

        self.connect(self.modelActionsSummary, QtCore.SIGNAL('hideMedicamentColumns(bool)'), self.hideMedicamentCols)
        if hasattr(self, 'tabMes'):
            self.connect(self.tabMes.cmbMes, QtCore.SIGNAL('editTextChanged(QString)'), self.updateMesDurationsMap)
        # i2878
        self.connect(self.gbLittleStrangerFlag, QtCore.SIGNAL('clicked()'), self.setChildParams)

        if QtGui.qApp.isAutoPrimacy():
            self.chkPrimary.setVisible(True)
            self.cmbPrimary.setVisible(False)
        else:
            self.chkPrimary.setVisible(False)
            self.cmbPrimary.setVisible(True)

        if (not QtGui.qApp.userHasRight('accessEditAutoPrimacy')):
            if QtGui.qApp.isAutoPrimacy():
                self.cmbPrimary.setEnabled(False)

        self.cmbPrimary.currentIndexChanged.connect(self.chkPrimarySync)

        if not QtGui.qApp.userHasRight(urSetEventExecDateF003):
            self.edtEndDate.setEnabled(False)
            self.edtEndTime.setEnabled(False)
        else:
            self.edtEndDate.setEnabled(True)
            self.edtEndTime.setEnabled(True)

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

    def chkPrimarySync(self):
        self.chkPrimary.setChecked(self.cmbPrimary.currentIndex() == 1)

    # done
    def setChildParams(self):
        self.edtChildBirthDate.setDate(self.clientBirthDate)
        try:
            self.cmbChildSex.setCurrentIndex(self.clientSex)
        except:
            pass

    def updateExternalId(self):
        externalId = self.tabNotes.getExternalId()
        resultId = self.getResult()
        if resultId is None:
            QtGui.QMessageBox.warning(self, u'Внимание!', u'Необходимо выставить результат', QtGui.QMessageBox.Ok)
            return
        externalId += u' ' + forceString(QtGui.qApp.db.translate('rbResult', 'id', resultId, 'federalCode'))
        if self.contractId is None:
            QtGui.QMessageBox.warning(self, u'Внимание!', u'Необходимо выставить договор', QtGui.QMessageBox.Ok)
            return
        externalId += u' ' + forceString(QtGui.qApp.db.translate('Contract', 'id', self.contractId, 'grouping'))
        self.tabNotes.edtEventExternalIdValue.setText(externalId)

    def _prepare(self, contractId, clientId, eventTypeId, orgId, personId, eventSetDatetime, eventDatetime,
                 includeRedDays, numDays,
                 presetDiagnostics, presetActions, disabledActions, notDeletedActions, externalId, assistantId,
                 curatorId,
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

        self.cmbResult.setTable('rbResult', True)
        self.eventSetDateTime = eventSetDatetime
        self.eventDate = eventDatetime
        defaultEndTime = getEventTypeDefaultEndTime(eventTypeId)
        if defaultEndTime and (not isinstance(eventDatetime, QtCore.QDateTime) or eventDatetime.time().isNull()):
            self.edtEndTime.setTime(defaultEndTime)

        self.setOrgId(orgId if orgId else QtGui.qApp.currentOrgId())

        self.setEventTypeId(eventTypeId)
        self.setClientId(clientId)
        self.prolongateEvent = True if actionByNewEvent else False
        self.setExternalId(externalId)
        self.cmbPerson.setValue(personId)

        if QtGui.qApp.isAutoPrimacy():
            isPrimary = self.isPrimary(clientId, eventTypeId, personId)
            # self.chkPrimary.setChecked(isPrimary)
            if isPrimary:
                self.cmbPrimary.setCurrentIndex(1)
        else:
            self.chkPrimary.setChecked(True)
        self.cmbOrder.setCode(forceInt(QtGui.qApp.db.translate('EventType', 'id', eventTypeId, 'defaultOrder')))

        self.updateModelsRetiredList()

        self.tabNotes.setNotesEx(externalId, assistantId, curatorId, relegateOrgId, referrals=referrals)
        self.initFocus()
        self.setContract()
        self.setRecommendations(recommendationList)

        if presetDiagnostics:
            for model in [self.modelPreliminaryDiagnostics, self.modelFinalDiagnostics]:
                for MKB, dispanserId, healthGroupId, medicalGroup, visitTypeId, goalId, serviceId in presetDiagnostics:
                    item = model.getEmptyRecord()
                    item.setValue('MKB', toVariant(MKB))
                    item.setValue('dispanser_id', toVariant(dispanserId))
                    item.setValue('healthGroup_id', toVariant(healthGroupId))
                    model.items().append(item)
                model.reset()
        self.prepareActions(presetActions, disabledActions, notDeletedActions, valueProperties, diagnos, financeId,
                            protocolQuoteId, actionByNewEvent)
        if self.isTabTempInvalidEtcAlreadyLoad:
            self.grpTempInvalid.pickupTempInvalid()
            # self.grpAegrotat.pickupTempInvalid()
            self.grpDisability.pickupTempInvalid()
            self.grpVitalRestriction.pickupTempInvalid()
        self.setIsDirty(False)
        self.tabFeed.prepare()
        self.tabFeed.setClientId(clientId)
        self.tabNotes.setEventEditor(self)
        if hasattr(self, 'tabMes'):
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
        if QtGui.qApp.userHasRight(urAccessF003planner):
            dlg = CPreF003Dialog(self, self.contractTariffCache)
            dlg.prepare(clientId, eventTypeId, plannerDate, self.personId, self.personSpecialityId,
                        self.personTariffCategoryId, flagHospitalization, actionTypeIdValue, tissueTypeId,
                        recommendationList, useDiagnosticsAndActionsPresets=useDiagnosticsAndActionsPresets)
            if dlg.diagnosticsTableIsNotEmpty() or dlg.actionsTableIsNotEmpty():
                if not dlg.exec_():
                    return False
            return self._prepare(None, clientId, eventTypeId, orgId, personId, eventSetDatetime, eventDatetime,
                                 includeRedDays, numDays, dlg.diagnostics(), dlg.actions(),
                                 dlg.disabledActionTypeIdList, dlg.notDeletedActionTypes, externalId, assistantId,
                                 curatorId, actionTypeIdValue, valueProperties, relegateOrgId, diagnos, financeId,
                                 protocolQuoteId, actionByNewEvent, referrals=referrals, isAmb=isAmb,
                                 recommendationList=recommendationList)
        else:
            presets = CPreF003DagnosticAndActionPresets(clientId, eventTypeId, plannerDate, self.personSpecialityId,
                                                        flagHospitalization, actionTypeIdValue, recommendationList,
                                                        useDiagnosticsAndActionsPresets=useDiagnosticsAndActionsPresets)
            return self._prepare(None, clientId, eventTypeId, orgId, personId, eventSetDatetime, eventDatetime,
                                 includeRedDays, numDays, presets.unconditionalDiagnosticList,
                                 presets.unconditionalActionList, presets.disabledActionTypeIdList,
                                 presets.notDeletedActionTypes, externalId, assistantId, curatorId, actionTypeIdValue,
                                 valueProperties, relegateOrgId, diagnos, financeId, protocolQuoteId, actionByNewEvent,
                                 referrals=referrals, isAmb=isAmb, recommendationList=recommendationList)

    def prepareActions(self, presetActions, disabledActions, notDeletedActions, valueProperties, diagnos, financeId,
                       protocolQuoteId, actionByNewEvent):
        def addActionType(actionTypeId, amount, idListActionType, idListActionTypeIPH, actionFinance,
                          idListActionTypeMoving, org_id):
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
            for actionTypeId, amount, _, org_id in presetActions:
                addActionType(actionTypeId, amount, idListActionType, idListActionTypeIPH, actionFinance,
                              idListActionTypeMoving, org_id)

    def setLeavedAction(self, actionTypeIdValue):
        currentDateTime = QtCore.QDateTime.currentDateTime()
        flatCode = u'moving%'
        db = QtGui.qApp.db
        tableActionType = db.table('ActionType')
        idListActionType = db.getIdList(tableActionType, [tableActionType['id']],
                                        [tableActionType['flatCode'].like(flatCode), tableActionType['deleted'].eq(0)])
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
                            movingQuoting = action[u'Квота'] if action.getType().containsPropertyWithName(
                                u'Квота') else None
                            if not orgStructureTransfer and orgStructurePresence:
                                orgStructureLeaved = orgStructurePresence
                        else:
                            orgStructureLeaved = None
                            movingQuoting = None
                        amount = actionType.amount
                        if actionTypeId:
                            if not (amount and actionType.amountEvaluation == CActionType.userInput):
                                amount = model.getDefaultAmountEx(actionType, record, None)
                        else:
                            amount = 0
                        record.setValue('amount', toVariant(amount))
                        model.updateActionAmount(len(model.items()) - 1)
                model.addRow(actionTypeIdValue)
                record, action = model.items()[-1]
                if not orgStructureLeaved and not orgStructureMoving:
                    currentOrgStructureId = QtGui.qApp.currentOrgStructureId()
                    if currentOrgStructureId:
                        typeRecord = QtGui.qApp.db.getRecordEx('OrgStructure', 'type',
                                                               'id = %d AND type = 4 AND deleted = 0' % (
                                                               currentOrgStructureId))
                        if typeRecord and (typeRecord.value('type')) == 4:
                            orgStructureLeaved = currentOrgStructureId
                if orgStructureLeaved and action.getType().containsPropertyWithName(u'Отделение'):
                    action[u'Отделение'] = orgStructureLeaved
                if action.getType().containsPropertyWithName(u'Квота') and movingQuoting:
                    action[u'Квота'] = movingQuoting
                record.setValue('begDate', toVariant(currentDateTime))
                record.setValue('endDate', toVariant(currentDateTime))
                record.setValue('status', toVariant(2))
                model.updateActionAmount(len(model.items()) - 1)
                self.edtEndDate.setDate(
                    currentDateTime.date() if isinstance(currentDateTime, QtCore.QDateTime) else QtCore.QDate())
                self.edtEndTime.setTime(
                    currentDateTime.time() if isinstance(currentDateTime, QtCore.QDateTime) else QtCore.QTime())

    def initFocus(self):
        if self.cmbContract.count() != 1:
            self.cmbContract.setFocus(QtCore.Qt.OtherFocusReason)
        else:
            self.tblFinalDiagnostics.setFocus(QtCore.Qt.OtherFocusReason)

    def newDiagnosticRecord(self, template):
        result = self.tblFinalDiagnostics.model().getEmptyRecord()
        return result

    def setRecord(self, record):
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        tableEventType = db.table('EventType')
        tableCard = db.table('Event_HospitalBedsLocationCard')
        self.cmbResult.setTable('rbResult', True)
        CEventEditDialog.setRecord(self, record)
        setDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'setDate')
        setRBComboBoxValue(self.cmbPerson, record, 'setPerson_id')
        setDatetimeEditValue(self.edtEndDate, self.edtEndTime, record, 'execDate')
        if forceDate(record.value('execDate')).isNull():
            self.edtEndTime.setTime(getEventTypeDefaultEndTime(self.eventTypeId))
        setRBComboBoxValue(self.cmbPerson, record, 'execPerson_id')
        self.chkPrimary.setChecked(forceInt(record.value('isPrimary')) == 1)
        self.setExternalId(forceString(record.value('externalId')))
        self.cmbOrder.setCode(forceString(record.value('order')))
        setRBComboBoxValue(self.cmbResult, record, 'result_id')
        self.prevEventId = forceRef(record.value('prevEvent_id'))
        if self.prevEventId:
            self.lblProlongateEvent.setText(u'п')
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
        setRBComboBoxValue(self.cmbContract, record, 'contract_id')
        self.loadDiagnostics(self.modelPreliminaryDiagnostics, self.itemId())
        self.loadDiagnostics(self.modelFinalDiagnostics, self.itemId())
        self.updateResultFilter()
        self.tabFeed.load(self.itemId())
        self.tabFeed.setClientId(self.clientId)
        if self.isTabTempInvalidEtcAlreadyLoad:
            self.grpTempInvalid.pickupTempInvalid()
            # self.grpAegrotat.pickupTempInvalid()
            self.grpDisability.pickupTempInvalid()
            self.grpVitalRestriction.pickupTempInvalid()
        self.loadActions()
        self.updateMesMKB()
        self.edtCycleDay.setValue(forceInt(record.value('cycleDay')))
        if hasattr(self, 'tabMes'):
            self.tabMes.setBegDate(forceDate(record.value('setDate')))
            self.tabMes.setEndDate(forceDate(record.value('execDate')))
            self.tabMes.setRecord(record)

        self.tabCash.load(self.itemId())
        self.tabCash.modelAccActions.regenerate()
        self.tabNotes.setNotes(record)
        self.tabNotes.setEventEditor(self)
        self.tabNotes.updateReferralPeriod(self.edtBegDate.date())
        recCard = QtGui.qApp.db.getRecordEx(tableCard, tableCard['locationCardType_id'],
                                            tableCard['event_id'].eq(forceInt(record.value('id'))))
        if recCard:
            self.cmbIBLocation.setValue(forceInt(recCard.value('locationCardType_id')))

        self.initFocus()
        self.setIsDirty(False)
        self.blankMovingIdList = []
        self.setEditable(self.getEditable())
        self.chkHospParent.setVisible(self.getEventProfile())

        self.setHtgRecord(record)

        self.updateCsg()
        self.setCsgRecord(record)
        if hasattr(self, 'cmbCsg'):
            self.cmbCsg.fillById()
        setOrgStructureIdToCmbPerson(self.cmbPerson)

    def setEditable(self, editable):
        self.modelPreliminaryDiagnostics.setEditable(editable)
        self.modelFinalDiagnostics.setEditable(editable)
        self.modelActionsSummary.setEditable(editable)
        self.grpBase.setEnabled(editable)
        if hasattr(self, 'tabMes'):
            self.tabMes.setEnabled(editable)
        if hasattr(self, 'cmbCsg'):
            self.cmbCsg.setEnabled(editable)
        if hasattr(self, 'chkHTG'):
            self.chkHTG.setEnabled(editable)
        if hasattr(self, 'cmbHTG'):
            self.cmbHTG.setEnabled(editable)
        self.tabStatus.setEditable(editable)
        self.tabDiagnostic.setEditable(editable)
        self.tabCure.setEditable(editable)
        self.tabMisc.setEditable(editable)
        self.tabAnalyses.setEditable(editable)
        # tabTempInvalidEtc
        self.grpDisability.setEnabled(editable)
        self.grpVitalRestriction.setEnabled(editable)
        self.tabTempInvalid.setEnabled(editable)
        # self.tabAegrotat.setEnabled(editable)
        self.tabTempInvalidDisability.setEnabled(editable)
        self.tabTempInvalidS.setEnabled(editable)
        # end of tabTempInvalidEtc
        self.tabCash.setEditable(editable)
        self.tabNotes.setEditable(editable)

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
                    self.tabNotes.edtPrevEventInfo.setText(u'Продолжение обращения: %s от %s.' % (
                    forceString(record.value('name')), forceDate(record.value('setDate')).toString('dd.MM.yyyy')))
            self.createDiagnostics(eventId)

    def createDiagnostics(self, eventId):
        if eventId:
            self.loadDiagnostics(self.modelPreliminaryDiagnostics, eventId)
            self.loadDiagnostics(self.modelFinalDiagnostics, eventId)

    def btnNextActionSetFocus(self):
        modelFind = self.tabMisc.modelAPActions
        items = modelFind.items()
        for rowFind, item in enumerate(items):
            record = item[0]
            if record:
                actionTypeIdFind = forceRef(record.value('actionType_id'))
                actionTypeFind = CActionTypeCache.getById(actionTypeIdFind) if actionTypeIdFind else None
                if u'received' in actionTypeFind.flatCode.lower():
                    idx = \
                    filter(lambda idx: self.tabWidget.tabText(idx) == u'&Мероприятия', xrange(self.tabWidget.count()))[
                        0]
                    self.tabWidget.setCurrentIndex(idx)
                    self.tabMisc.tblAPActions.setCurrentIndex(modelFind.index(rowFind, 0))
                    self.tabMisc.btnNextAction.setFocus(QtCore.Qt.OtherFocusReason)
                    break

    def loadDiagnostics(self, modelDiagnostics, eventId):
        db = QtGui.qApp.db
        table = db.table('Diagnostic')
        isDiagnosisManualSwitch = modelDiagnostics.manualSwitchDiagnosis()
        rawItems = db.getRecordList(table, '*',
                                    [table['deleted'].eq(0), table['event_id'].eq(eventId), modelDiagnostics.filter],
                                    'id')
        items = []
        for record in rawItems:
            diagnosisId = record.value('diagnosis_id')
            MKB = db.translate('Diagnosis', 'id', forceRef(diagnosisId), 'MKB')
            MKBEx = db.translate('Diagnosis', 'id', forceRef(diagnosisId), 'MKBEx')
            morphologyMKB = db.translate('Diagnosis', 'id', forceRef(diagnosisId), 'morphologyMKB')
            setDate = forceDate(record.value('setDate'))
            newRecord = modelDiagnostics.getEmptyRecord()
            copyFields(newRecord, record)
            newRecord.setValue('MKB', MKB)
            newRecord.setValue('MKBEx', MKBEx)
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
        self.tabAnalyses.loadActionsLite(eventId)
        self.modelActionsSummary.regenerate()

    def getEventProfile(self):
        # db = QtGui.qApp.db
        # tableEventType = 'EventType'
        # tableEventProfile = 'rbEventProfile'
        # codesProfile = ['12', '102', '302', '402']
        # result = False
        # record = db.getRecord(tableEventType, 'eventProfile_id', self.eventTypeId)
        # if record is None: return result
        # record = db.getRecord(tableEventProfile, 'code', forceInt(record.value('eventProfile_id')))
        # if record is None: return result
        # if record:
        #     for k in codesProfile:
        #         if (forceString(record.value('code')) == forceString(k)):
        #             result = True
        result = True
        if self.clientBirthDate and self.begDate():
            result = result and 4 <= calcAgeInYears(self.clientBirthDate, self.begDate()) < 18
        else:
            result = False
        return result

    def getRecord(self):
        record = CEventEditDialog.getRecord(self)
        showTime = getEventShowTime(self.eventTypeId)
        # перенести в exec_ в случае успеха или в accept?
        getRBComboBoxValue(self.cmbContract, record, 'contract_id')
        getDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'setDate', showTime)
        getRBComboBoxValue(self.cmbPerson, record, 'setPerson_id')
        getDatetimeEditValue(self.edtEndDate, self.edtEndTime, record, 'execDate', showTime)
        getRBComboBoxValue(self.cmbPerson, record, 'execPerson_id')
        getRBComboBoxValue(self.cmbResult, record, 'result_id')
        record.setValue('isPrimary', toVariant(1 if self.chkPrimary.isChecked() else 2))
        if self.prolongateEvent:
            record.setValue('order', toVariant(5))
            record.setValue('prevEvent_id', toVariant(self.prevEventId))

        record.setValue('cycleDay', toVariant(self.edtCycleDay.value()))
        # self.getHtgRecord(record)
        # getComboBoxValue(self.cmbOrder,         record, 'order')
        record.setValue('order', toVariant(self.cmbOrder.code()))
        self.tabNotes.getNotes(record, self.eventTypeId)
        return record

    def saveInternals(self, eventId):
        super(CF003Dialog, self).saveInternals(eventId)
        self.saveDiagnostics(self.modelPreliminaryDiagnostics, eventId)
        self.saveDiagnostics(self.modelFinalDiagnostics, eventId)
        setAskedClassValueForDiagnosisManualSwitch(None)
        if self.isTabTempInvalidEtcAlreadyLoad:
            self.grpTempInvalid.saveTempInvalid()
            # self.grpAegrotat.saveTempInvalid()
            self.grpDisability.saveTempInvalid()
            self.grpVitalRestriction.saveTempInvalid()
        self.saveActions(eventId)
        self.tabFeed.save(eventId)
        self.tabCash.save(eventId)
        # self.tabNotes.saveOutgoingRef(eventId)
        self.saveBlankUsers(self.blankMovingIdList)
        self.updateRecommendations()
        db = QtGui.qApp.db
        if self.cmbIBLocation.value():
            tblCard = db.table('Event_HospitalBedsLocationCard')
            recCard = db.getRecordEx(tblCard, '*', tblCard['event_id'].eq(eventId))
            if recCard and not forceInt(recCard.value('locationCardType_id')) == forceInt(self.cmbIBLocation.value()):
                recCard.setValue('event_id', toVariant(eventId))
                recCard.setValue('locationCardType_id', toVariant(forceInt(self.cmbIBLocation.value())))
                recCard.setValue('moveDate', toVariant(forceDate(QtCore.QDate.currentDate())))
            elif not recCard:
                recCard = tblCard.newRecord()
                recCard.setValue('deleted', toVariant(0))
                recCard.setValue('event_id', toVariant(eventId))
                recCard.setValue('locationCardType_id', toVariant(forceInt(self.cmbIBLocation.value())))
                recCard.setValue('moveDate', toVariant(forceDate(QtCore.QDate.currentDate())))
            db.insertOrUpdate(tblCard, recCard)

    def saveDiagnostics(self, modelDiagnostics, eventId):
        items = modelDiagnostics.items()
        isDiagnosisManualSwitch = modelDiagnostics.manualSwitchDiagnosis()
        begDate = self.edtBegDate.date()
        endDate = self.edtEndDate.date()
        date = endDate if endDate else begDate

        MKBDiagnosisIdPairList = []
        prevId = 0
        for item in items:
            MKB = forceString(item.value('MKB'))
            MKBEx = forceString(item.value('MKBEx'))
            TNMS = forceString(item.value('TNMS'))
            morphologyMKB = forceString(item.value('morphologyMKB'))
            diagnosisTypeId = forceRef(item.value('diagnosisType_id'))
            personId = forceRef(item.value('person_id'))
            if self.diagnosisSetDateVisible == False:
                item.setValue('setDate', toVariant(begDate))
            else:
                date = forceDate(item.value('setDate'))
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
            item.setValue('TMNS', toVariant(TNMS))
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
        typeId = self.modelFinalDiagnostics.getFinalDiagnosisId()
        if not typeId:
            typeId = self.modelPreliminaryDiagnostics.getFinalDiagnosisId()
        return typeId

    def getModelFinalDiagnostics(self):
        return self.modelFinalDiagnostics

    def getFinalDiagnostic(self):
        return self.getModelFinalDiagnostics().getFinalDiagnosis()

    def saveActions(self, eventId):
        self.tabStatus.saveActions(eventId)
        self.tabDiagnostic.saveActions(eventId)
        self.tabCure.saveActions(eventId)
        self.tabMisc.saveActions(eventId)
        self.tabAnalyses.saveActions(eventId)

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
        if self.isTabAnalysesAlreadyLoad:
            self.tabAnalyses.setOrgId(orgId)

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
            if title == u'':
                title = findTitle(u'planning%', u'ПЛАНИРОВАНИЕ')
        return title

    def setEventTypeId(self, eventTypeId):
        titleF003 = self.setOrgStructureTitle()
        CEventEditDialog.setEventTypeId(self, eventTypeId, u'Ф.003', titleF003)
        self.tabCash.windowTitle = self.windowTitle()
        showTime = getEventShowTime(eventTypeId)
        self.edtBegTime.setVisible(showTime)
        self.edtEndTime.setVisible(showTime)
        self.updateMKB()
        if self.cmbResult.value() is None:
            if self.inheritResult == True:
                self.cmbResult.setValue(self.defaultEventResultId.get(self.eventPurposeId))
            else:
                self.cmbResult.setValue(0)
        self.updateResultFilter()
        customizePrintButton(self.btnPrint, self.eventContext if self.eventContext else 'F003')
        self.diagnosisSetDateVisible = forceBool(getDiagnosisSetDateVisible(eventTypeId))
        if self.diagnosisSetDateVisible == False:
            self.tblFinalDiagnostics.setColumnHidden(4, True)
            self.tblPreliminaryDiagnostics.setColumnHidden(4, True)

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
        self.tabAnalyses.actionTemplateCache.reset()

    def checkFinalAndPreDiagnosis(self):
        if forceStringEx(
                QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'infisCode')) == u'онко':
            def searchElem(lst, id):
                for x in range(len(lst)):
                    if forceRef(lst[x].value('diagnosisType_id')) == id:
                        return x
                return -1

            finalDiag = self.modelFinalDiagnostics.getFinalDiagnosis()
            prelimDiag = self.tblPreliminaryDiagnostics.model().items()

            pId = searchElem(prelimDiag, 12)

            if finalDiag and pId >= 0 and forceString(finalDiag.value('MKB')) != forceString(
                    prelimDiag[pId].value('MKB')):
                if QtGui.QMessageBox.information(
                        self,
                        u'Внимание!',
                        u'Заключительный и предварительный (основной) диагнозы отличаются. '
                        u'Задать соотвествие с заключительным диагнозом?',
                                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                        QtGui.QMessageBox.Yes
                ) == QtGui.QMessageBox.Yes:
                    prelimDiag[pId].setValue('MKB', finalDiag.value('MKB'))
                    self.tblPreliminaryDiagnostics.model().setItems(prelimDiag)

    def checkHaveFinalDiagnostics(self):
        if not QtGui.qApp.userHasRight(urSaveWithoutFinalDiagF003):
            finalDiag = self.modelFinalDiagnostics.getFinalDiagnosis()

            if not self.edtEndDate.date().isNull() and (not finalDiag or not forceString(finalDiag.value('MKB'))):
                return self.checkInputMessage(
                    u"заключительный диагноз.",
                    skipable=False,
                    widget=self.tblFinalDiagnostics
                )
        return True


    def checkHavePreliminaryDiagnostics(self):
        if not QtGui.qApp.userHasRight(urSaveWithoutPrelimDiagF003):
            prelimDiag = self.tblPreliminaryDiagnostics.model().items()
            if not prelimDiag:
                QtGui.QMessageBox.warning(
                    self,
                    u'Внимание!',
                    u'Предварительный диагноз не указан. '
                    u'Укажите предварительный диагноз.',
                    QtGui.QMessageBox.Ok,
                    QtGui.QMessageBox.Ok
                )
                return False
            else:
                for x in prelimDiag:
                    if not len(forceString(x.value('MKB'))):
                        QtGui.QMessageBox.warning(
                            self,
                            u'Внимание!',
                            u'Код МКБ у предварительного диагноза не указан. '
                            u'Укажите код МКБ.',
                            QtGui.QMessageBox.Ok,
                            QtGui.QMessageBox.Ok
                        )
                        return False
        return True

    def checkContract(self):
        return (
            self.orgId != QtGui.qApp.currentOrgId() or
            self.cmbContract.value() or
            self.checkInputMessage(u'договор', False, self.cmbContract)
        )

    def checkPerson(self):
        return (self.cmbPerson.value() or self.checkInputMessage(u'врача', False, self.cmbPerson))

    def checkTNMS(self):
        result = self.getFinalDiagnosisMKB()[0] is not None
        result = result and self.getFinalDiagnosisMKB()[0] != u''
        result = result and self.getFinalDiagnosisMKB()[0][0] == u'C'
        result = result and not QtGui.qApp.userHasRight(urOncoDiagnosisWithoutTNMS)
        result = result and QtGui.qApp.isTNMSVisible()
        result = result and (
            self.modelFinalDiagnostics.getFinalDiagnosis().value('TNMS') is None or
            forceString(self.modelFinalDiagnostics.getFinalDiagnosis().value('TNMS')) == u''
        )
        if result:
            return self.checkValueMessage(check_data_text_TNM, False, None)
        return True

    def checkDataEntered(self):
        result = CEventEditDialog.checkDataEntered(self)
        self.blankMovingIdList = []
        self.checkFinalAndPreDiagnosis()
        result = result and self.checkHavePreliminaryDiagnostics()
        result = result and self.checkHaveFinalDiagnostics()
        result = result and self.checkDifferentDepartment()
        result = result and self.checkContract()
        result = result and self.checkPerson()

        begDate = self.edtBegDate.date()
        endDate = self.edtEndDate.date() if self._isClosedEventCheck else QtCore.QDate()

        result = result and (not begDate.isNull() or self.checkInputMessage(u'дату назначения', False, self.edtBegDate))
        if endDate:
            result = result and self.checkActionDataEntered(
                begDate, QtCore.QDate(), endDate, self.tabToken, self.edtBegDate, None, self.edtEndDate
            )
            result = result and self.checkEventDate(begDate, endDate, None, self.tabToken, None, self.edtEndDate, True)
            minDuration, maxDuration = getEventDuration(self.eventTypeId)
            if minDuration <= maxDuration:
                aidTypeCode = getEventAidTypeCode(self.eventTypeId)
                countRedDays = True if not QtGui.qApp.isExcludeRedDaysInEventLength() or aidTypeCode not in ('7', '10') else False
                eventDuration = getEventLengthDays(begDate, endDate, countRedDays, self.eventTypeId)
                eventDurationErrorString = u'Указана длительность с учётом выходных: %s.' % formatNum(eventDuration, (u'день', u'дня', u'дней'))
                result = result and (
                    eventDuration >= minDuration or
                    self.checkValueMessage(
                        u'Длительность должна быть не менее %s. %s' % (
                            formatNum(minDuration, (u'дня', u'дней', u'дней')), eventDurationErrorString
                        ),
                        False,
                        self.edtEndDate
                    )
                )
                result = result and (
                    maxDuration == 0 or
                    eventDuration <= maxDuration or
                    self.checkValueMessage(
                        u'Длительность должна быть не более %s. %s' % (
                            formatNum(maxDuration, (u'дня', u'дней', u'дней')),
                            eventDurationErrorString
                        ),
                        False,
                        self.edtEndDate
                    )
                )
        result = result and self.checkDiagnosticsDataEntered([(self.tblFinalDiagnostics, True, True, None)], endDate)
        result = result and self.checkActionsDateEnteredActuality(
            begDate, endDate, [self.tabStatus, self.tabDiagnostic, self.tabCure, self.tabMisc, self.tabAnalyses]
        )
        result = result and self.checkActionsDataEntered(
            [self.tabStatus, self.tabDiagnostic, self.tabCure, self.tabMisc, self.tabAnalyses], begDate, endDate)
        if self.isTabTempInvalidEtcAlreadyLoad:
            result = result and self.grpTempInvalid.checkTempInvalidDataEntered()
            # result = result and self.grpAegrotat.checkTempInvalidDataEntered()
            result = result and self.grpDisability.checkTempInvalidDataEntered()
            result = result and self.grpVitalRestriction.checkTempInvalidDataEntered()
        if self.isTabCashAlreadyLoad:
            result = result and self.tabCash.checkDataLocalContract()
        result = result and self.checkSerialNumberEntered()
        result = result and self.checkDischargePaymentAndQuoting(self.tabCash, self.tabMisc)
        result = result and self.checkTabNotesReferral()
        result = result and self.checkTNMS()

        self.valueForAllActionEndDate = None
        return result

    def checkActionEndDate(self, strNameActionType, tblWidget, row, column, widgetEndDate):
        # переопределяем CEventEditDialog.checkActionEndDate
        if self.valueForAllActionEndDate is None:
            buttons = QtGui.QMessageBox.Ok | QtGui.QMessageBox.Ignore
            message = u'Должна быть указана дата выполнения действия%s' % (strNameActionType)
            messageBox = QtGui.QMessageBox(QtGui.QMessageBox.Warning, u'Внимание!', message, buttons, self)
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

    def checkSerialNumberEntered(self):
        result = True
        self.blankMovingIdList = []
        db = QtGui.qApp.db
        table = db.table('ActionPropertyType')
        actionTypeIdListSerial = db.getDistinctIdList(table, [table['actionType_id']],
                                                      [table['deleted'].eq(0), table['typeName'].like('BlankSerial')])

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
                                    result, blankMovingId = self.checkBlankParams(blankParams, result, serial, number,
                                                                                  tab.tblAPActions, row)
                                    self.blankMovingIdList.append(blankMovingId)
                                    if not result:
                                        return result
        return result

    def checkDifferentDepartment(self):
        try:
            result = True
            model = self.tabMisc.modelAPActions
            flag = False
            receivedAction = movingAction = None
            receivedActionRow = movingActionRow = 0
            received = moving = None
            for row, (record, action) in enumerate(model.items()):
                if forceString(action._actionType.flatCode) == u'received' and flag == False:
                    received = forceString(action[u'Направлен в отделение'])
                    receivedAction = action
                    receivedActionRow = row
                    flag = True
                if forceString(action._actionType.flatCode) == u'moving' and flag == True:
                    moving = forceString(action[u'Отделение пребывания'])
                    movingAction = action
                    movingActionRow = row
                    break
            if received != moving:
                if received and moving:
                    self.tabMisc.tblAPActions.setCurrentIndex(model.createIndex(receivedActionRow, 0))
                    propertyTypeList = receivedAction.getType().getPropertiesByName().items()
                    propertyTypeList.sort(key=lambda x: (x[1].idx, x[1].id))
                    row = 0
                    for row, item in enumerate(propertyTypeList):
                        if item[0] == u'направлен в отделение':
                            break
                    self.checkInputMessage(u'одинаковые отделения направления и пребывания', False,
                                           self.tabMisc.tblAPProps, row, 0)
                    result = False
                else:
                    if received:
                        message = u'Не указано отделение пребывания в действии "Движение".\nСинхронизировать с отделением, указанным в "Поступлении"?'
                    elif moving:
                        message = u'Не указано отделение, в которое направлен пациент в действии "Поступление".\nСинхронизировать с отделением пребывания, указанным в действии "Движение"?'
                    buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
                    res = QtGui.QMessageBox.warning(self,
                                                    u'Внимание!',
                                                    message,
                                                    buttons,
                                                    QtGui.QMessageBox.Yes)
                    if res == QtGui.QMessageBox.Yes:
                        if received:
                            movingAction[u'Отделение пребывания'] = receivedAction[u'Направлен в отделение']
                        elif moving:
                            receivedAction[u'Направлен в отделение'] = movingAction[u'Отделение пребывания']
                        result = True
                    else:
                        if not moving:
                            self.tabMisc.tblAPActions.setCurrentIndex(model.createIndex(movingActionRow, 0))
                            propertyTypeList = movingAction.getType().getPropertiesByName().items()
                            propertyTypeList.sort(key=lambda x: (x[1].idx, x[1].id))
                            row = 0
                            for row, item in enumerate(propertyTypeList):
                                if item[0] == u'отделение пребывания':
                                    break
                        else:
                            self.tabMisc.tblAPActions.setCurrentIndex(model.createIndex(receivedActionRow, 0))
                            propertyTypeList = receivedAction.getType().getPropertiesByName().items()
                            propertyTypeList.sort(key=lambda x: (x[1].idx, x[1].id))
                            row = 0
                            for row, item in enumerate(propertyTypeList):
                                if item[0] == u'направлен в отделение':
                                    break
                        self.setFocusToWidget(self.tabMisc.tblAPProps, row, 0)
                        result = False
            return result
        except:
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

    def getEventInfo(self, context):
        if not self.isTabCashAlreadyLoad:
            self.initTabCash(False)
        result = CEventEditDialog.getEventInfo(self, context)
        # ручная инициализация свойств
        result._isPrimary = self.chkPrimary.isChecked()
        # ручная инициализация таблиц
        result._actions = CActionInfoProxyList(context,
                                               [self.tabStatus.modelAPActions, self.tabDiagnostic.modelAPActions,
                                                self.tabCure.modelAPActions, self.tabMisc.modelAPActions,
                                                self.tabAnalyses.modelAPActions],
                                               result)
        result._diagnosises = CDiagnosticInfoProxyList(context,
                                                       [self.modelPreliminaryDiagnostics, self.modelFinalDiagnostics])
        return result

    def getTempInvalidInfo(self, context):
        u" Листок нетрудоспособности->ВУТ "
        return self.grpTempInvalid.getTempInvalidInfo(context)

    # def getAegrotatInfo(self, context):
    #     u" Справка->ВУТ "
    #     return self.grpAegrotat.getTempInvalidInfo(context)

    def updateDuration(self):
        begDate = self.edtBegDate.date()
        endDate = self.edtEndDate.date()
        if endDate.isNull():
            endDate = QtCore.QDate.currentDate()
        text = '-'
        duration = None
        if not begDate.isNull():
            aidTypeCode = getEventAidTypeCode(self.eventTypeId)
            if hasattr(self, 'cmbCsg'):
                csgName = self.cmbCsg.currentText()
            else:
                csgName = self.tabMes.cmbMes.currentText()

            if u'G50' in csgName or u'G40' in csgName:
                countRedDays = False
            else:
                countRedDays = True if not QtGui.qApp.isExcludeRedDaysInEventLength() or aidTypeCode not in (
                '7', '10') else False

            # countRedDays = not QtGui.qApp.isExcludeRedDaysInEventLength()
            duration = getEventLengthDays(begDate, endDate, countRedDays, self.eventTypeId)
            if duration > 0:
                text = str(duration)
        self.setEventDuration(duration)
        self.lblDurationValue.setText(text)
        self.updateDurationAberration(duration)

    def updateDurationAberration(self, duration):
        mesId = self.getMesId()
        if not duration or duration <= 0 or not mesId:
            self.lblDurationValueAberration.setText('- / -')
            self.lblDurationValueAberration.setStyleSheet('QLabel { color: black; }')
            return
        minDuration, maxDuration = self.mesDurationsMap[mesId]
        if duration < minDuration:
            text = "%d-%d / %+d" % (minDuration, maxDuration, duration - minDuration)
            self.lblDurationValueAberration.setStyleSheet('QLabel { color: red; }')
        elif duration > maxDuration:
            text = "%d-%d / %+d" % (minDuration, maxDuration, duration - maxDuration)
            self.lblDurationValueAberration.setStyleSheet('QLabel { color: red; }')
        else:
            text = "%d-%d / 0" % (minDuration, maxDuration)
            self.lblDurationValueAberration.setStyleSheet('QLabel { color: black; }')
        self.lblDurationValueAberration.setText(text)

    def updateMesDurationsMap(self, mesCmbIndex=None):
        mesId = self.getMesId()
        if mesId and not mesId in self.mesDurationsMap.keys():
            record = QtGui.qApp.db.getRecordEx('mes.MES', 'minDuration, maxDuration', 'id=%d' % forceRef(mesId))
            minDuration = forceInt(record.value('minDuration'))
            maxDuration = forceInt(record.value('maxDuration'))
            self.mesDurationsMap[mesId] = (minDuration, maxDuration)
            self.updateDuration()

    def updateMesMKB(self):
        MKB = self.getFinalDiagnosisMKB()[0]
        MKB2List = self.getRelatedDiagnosisMKB()

        if hasattr(self, 'tabMes'):
            self.tabMes.setMKB(MKB)
            self.tabMes.setMKB2([r[0] for r in MKB2List])

        if hasattr(self, 'cmbCsg'):
            self.cmbCsg.setMKB(MKB)
            self.cmbCsg.setMKB2([r[0] for r in MKB2List])

    def updateCsg(self):
        if hasattr(self, 'chkHTG') and not self.chkHTG.isChecked() or not hasattr(self, 'chkHTG'):
            items = self.tblActions.model().items()
            actionTypeIdList = [
                forceInt(item.value('actionType_id'))
                for item in items if forceInt(item.value('status')) == ActionStatus.Done
            ]
            self.setContract()
            self.updateMesMKB()
            if hasattr(self, 'tabMes'):
                self.tabMes.cmbMes.setActionTypeIdList(actionTypeIdList)
                self.tabMes.cmbMes.setBegDate(self.begDate())
                self.tabMes.cmbMes.setEndDate(self.endDate())
                self.tabMes.cmbMes.setDefaultValue()

            if hasattr(self, 'cmbCsg'):
                self.cmbCsg.fill(self.eventTypeId)
                self.cmbCsg.setActionTypeIdList(actionTypeIdList)
                self.cmbCsg.setBegDate(self.begDate())
                self.cmbCsg.setEndDate(self.endDate())
                self.cmbCsg.setDefaultValue()

            self.updateDuration()
        elif hasattr(self, 'cmbCsg'):
            self.cmbCsg.reset()
        elif hasattr(self, 'tabMes'):
            self.tabMes.cmbMes.reset()

    def on_modelFinalDiagnostics_updateCsg(self):
        self.updateCsg()

    def on_modelPreliminaryDiagnostics_updateCsg(self):
        self.updateCsg()

    def on_modelActionsSummary_updateCsg(self):
        self.updateCsg()

    def initTabMes(self, show=True):
        if hasattr(self, 'tabMes'):
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

    def initTabFeed(self):
        self.tabFeed.setVisible(False)
        self.tabFeed.preSetupUi()
        self.tabFeed.postSetupUi()
        self.tabFeed.setVisible(True)

        self.isTabFeedAlreadyLoaded = True

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

    def createCsgComboBox(self):
        if QtGui.qApp.defaultKLADR()[:2] == '23' and QtGui.qApp.currentOrgInfis() not in ['07526', '07112',
                                                                                          '07108']:  # ДККБ
            self.CsgGridLayout = QtGui.QGridLayout()
            self.CsgGridLayout.setObjectName('CsgGridLayout')
            self.cmbCsg = CCSGComboBox(self.grpBase)
            self.cmbCsg.setObjectName('cmbCsg')
            self.CsgGridLayout.addWidget(self.cmbCsg, 0, 1, 1, 1)
            self.lblCsg = QtGui.QLabel(self.grpBase)
            self.lblCsg.setObjectName('lblCsg')
            self.lblCsg.setMaximumSize(QtCore.QSize(24, 32))
            self.lblCsg.setText(_translate("Dialog", "КСГ", None))
            self.CsgGridLayout.addWidget(self.lblCsg, 0, 0, 1, 1)
            self.gridLayoutCsg.addLayout(self.CsgGridLayout, 1, 0, 1, 2)
            self.deleteTabMes()

    def createHtgComboBox(self):
        if QtGui.qApp.defaultKLADR()[:2] == '23' and QtGui.qApp.currentOrgInfis() not in ['07526', '07112',
                                                                                          '07108']:  # ДККБ
            self.HtgGridLayout = QtGui.QGridLayout()
            self.HtgGridLayout.setObjectName('HtgGridLayout')
            self.cmbHTG = CRBComboBox(self.grpBase)
            self.cmbHTG.setObjectName('cmbHTG')
            self.HtgGridLayout.addWidget(self.cmbHTG, 0, 1, 1, 1)
            self.chkHTG = QtGui.QCheckBox(self.grpBase)
            self.chkHTG.setObjectName('chkHTG')
            self.chkHTG.setMaximumSize(QtCore.QSize(60, 32))
            self.chkHTG.setText(_translate("Dialog", "ВМП", None))
            self.HtgGridLayout.addWidget(self.chkHTG, 0, 0, 1, 1)
            self.gridLayoutCsg.addLayout(self.HtgGridLayout, 2, 0, 1, 2)

            self.cmbHTG.setTable('mes.mrbHighTechMedicalGroups')
            self.connect(self.chkHTG, QtCore.SIGNAL('toggled(bool)'), self.on_chkHTG_toggled)
            self.cmbHTG.setEnabled(False)
            self.deleteTabMes()

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
        self.updateMKB()
        self.updateDuration()
        self.emitUpdateActionsAmount()
        self.setContract()
        self.chkHospParent.setVisible(self.getEventProfile())

        self.updateModelsRetiredList()
        if hasattr(self, 'tabMes'):
            self.tabMes.setBegDate(date)

        if hasattr(self, 'cmbCsg'):
            self.cmbCsg.setBegDate(date)

    @QtCore.pyqtSlot(QtCore.QTime)
    def on_edtBegTime_timeChanged(self, time):
        self.emitUpdateActionsAmount()

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtEndDate_dateChanged(self, date):
        self.updateDuration()
        self.emitUpdateActionsAmount()
        self.setContract()
        if hasattr(self, 'tabMes'):
            self.tabMes.setEndDate(date)
        if hasattr(self, 'cmbCsg'):
            self.cmbCsg.setEndDate(date)
        self.tabNotes.cmbClientPolicy.updatePolicy(date)
        if QtGui.qApp.isAutoClosed():
            self.chkIsClosed.setChecked(date != QtCore.QDate())

    @QtCore.pyqtSlot(QtCore.QTime)
    def on_edtEndTime_timeChanged(self, time):
        self.emitUpdateActionsAmount()

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
        self.tabAnalyses.updatePersonId(oldPersonId, self.personId)

    def on_modelPreliminaryDiagnostics_diagnosisChanged(self):
        self.updateMesMKB()

    def on_modelFinalDiagnostics_diagnosisChanged(self):
        self.updateMesMKB()

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
            newRecord.setValue('diagnosisType', QtCore.QVariant(CF003Dialog.dfAccomp))
            newRecord.setValue('speciality_id', currentRecord.value('speciality_id'))
            newRecord.setValue('healthGroup_id', currentRecord.value('healthGroup_id'))
            self.modelFinalDiagnostics.insertRecord(currentRow + 1, newRecord)
            self.tblFinalDiagnostics.setCurrentIndex(
                self.modelFinalDiagnostics.index(currentRow + 1, newRecord.indexOf('MKB')))

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

        data = {
            'event': eventInfo,
            'client': eventInfo.client,
            'tempInvalid': tempInvalidInfo,
            # 'aegrotat': aegrotatInfo,
            'templateCounterValue': self.oldTemplates.get(templateId, '')
        }
        applyTemplate(self, templateId, data)

    @QtCore.pyqtSlot()
    def on_btnRelatedEvent_clicked(self):
        from HospitalBeds.RelatedEventListDialog import CRelatedEventListDialog
        currentEventId = self.itemId()
        if currentEventId or self.prevEventId:
            CRelatedEventListDialog(self, currentEventId, self.prevEventId).exec_()

    # @QtCore.pyqtSlot(int)
    # def on_cmbResult_currentIndexChanged(self):
    #     self.modelFinalDiagnostics.setResult(getResultIdByDiagnosticResultId(self.cmbResult.value()))


class CF003ExtendedDialog(CF003Dialog):
    formTitle = u'Ф.003/р'

    def __init__(self, parent):
        CF003Dialog.__init__(self, parent)
        if QtGui.qApp.checkGlobalPreference('43', u'да'):
            self.grpBase.setTitle(self.formTitle.lower())
        else:
            self.cmbHMPKind.setVisible(False)
            self.lblHMPKind.setVisible(False)
            self.cmbHMPMethod.setVisible(False)
            self.lblHMPMethod.setVisible(False)
        self.cmbHMPKind.setTable('rbHighTechCureKind', addNone=False)
        self.cmbHMPMethod.setTable('rbHighTechCureMethod', addNone=False)
        self.cmbHMPKind.setCurrentIndex(0)

    def on_cmbHMPKind_currentIndexChanged(self):
        cureKindId = forceRef(self.cmbHMPKind.value())
        self.cmbHMPMethod.setFilter('cureKind_id = %d' % cureKindId if cureKindId else '0')

        if self._record:
            oldIndex = self.cmbHMPMethod.model().searchId(forceRef(self._record.value('hmpMethod_id')))
        else:
            oldIndex = 0
        self.cmbHMPMethod.setCurrentIndex(oldIndex if oldIndex != -1 else 0)
        self.saveMovingWithoutMes = forceBool(self.getCureKindCode(cureKindId) != '0')

    def getCureKindCode(self, cureKindId):
        return forceString(QtGui.qApp.db.translate('rbHighTechCureKind', 'id', cureKindId, 'code'))

    def getRecord(self):
        record = CF003Dialog.getRecord(self)
        getRBComboBoxValue(self.cmbHMPKind, record, 'hmpKind_id')
        getRBComboBoxValue(self.cmbHMPMethod, record, 'hmpMethod_id')
        return record

    def setRecord(self, record):
        CF003Dialog.setRecord(self, record)
        setRBComboBoxValue(self.cmbHMPKind, record, 'hmpKind_id')
        setRBComboBoxValue(self.cmbHMPMethod, record, 'hmpMethod_id')


class CF003BaseDiagnosticsModel(CInDocTableModel):
    __pyqtSignals__ = (
        'diagnosisChanged()',
        'updateCsg()'
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
            if self._parent.inheritCheckupResult == True:
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

            if column == self.getColIndex('diagnosisType_id'):  # тип диагноза
                result = CInDocTableModel.setData(self, index, value, role)
                if result:
                    self.updateDiagnosisType(set([row]))
                    self.emitDiagnosisChanged()
                    self.emitUpdateCsg()
                return result

            elif column == self.getColIndex('person_id'):  # врач
                personId = forceRef(value)
                if not eventEditor.checkClientAttendaceEE(personId):
                    return False
                result = CInDocTableModel.setData(self, index, value, role)
                if result:
                    self.updateDiagnosisType(set())
                return result

            elif column == self.getColIndex('MKB'):  # код МКБ
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
                    self.emitUpdateCsg()
                return result

            elif column == self.getColIndex('MKBEx'):  # доп. код МКБ
                newMKB = forceString(value)
                if not newMKB:
                    pass
                else:
                    acceptable = eventEditor.checkDiagnosis(newMKB, True)
                    if not acceptable:
                        return False
                value = toVariant(newMKB)
                result = CInDocTableModel.setData(self, index, value, role)
                if result:
                    self.emitUpdateCsg()
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
        self.emitUpdateCsg()

    def updateDiagnosisType(self, fixedRowSet):
        mapPersonIdToRow = defaultdict(list)
        diagnosisTypeIds = []
        endDiagnosisTypeIds = None
        endPersonId = None
        endRow = -1

        for row, item in enumerate(self.items()):
            personId = forceRef(item.value('person_id'))
            mapPersonIdToRow[personId].append(row)
            diagnosisTypeId = forceRef(item.value('diagnosisType_id'))
            diagnosisTypeIds.append(diagnosisTypeId)
            if self.diagnosisTypeCol.ids[0] == diagnosisTypeId and personId == self._parent.personId:
                endDiagnosisTypeIds = diagnosisTypeId
                endPersonId = personId
                endRow = row

        for personId, rows in mapPersonIdToRow.iteritems():
            usedDiagnosisTypeIds = [diagnosisTypeIds[row] for row in fixedRowSet.intersection(set(rows))]
            listFixedRowSet = list(fixedRowSet.intersection(set(rows)))

            if ((self.diagnosisTypeCol.ids[0] in usedDiagnosisTypeIds) or
                    (self.diagnosisTypeCol.ids[0] == diagnosisTypeIds[rows[0]])) and personId == self._parent.personId:
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
                    usedDiagnosisTypeIds = [diagnosisTypeIds[row] for row in fixedRowSet.intersection(set(rows))]
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

    def getRelatedDiagnosisMKB(self):
        relatedDiagnosisTypeId = self.diagnosisTypeCol.ids[2]
        items = self.items()
        mkbList = []
        for item in items:
            diagnosisTypeId = forceRef(item.value('diagnosisType_id'))
            if diagnosisTypeId == relatedDiagnosisTypeId:
                mkbList.append([forceString(item.value('MKB')), forceString(item.value('MKBEx'))])
        if mkbList:
            return mkbList
        else:
            return [['', '']]

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

    def emitUpdateCsg(self):
        self.emit(QtCore.SIGNAL('updateCsg()'))


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

    def getCloseOrMainDiagnosisTypeIdList(self):
        return self.diagnosisTypeCol.ids[:2]

    def addRecord(self, record):
        super(CF003FinalDiagnosticsModel, self).addRecord(record)
        self.emitResultChanged()

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

# def main():
#     import sys
#     from s11main import CS11mainApp
#     from s11main import CS11MainWindow
#     from Events.CreateEvent import editEvent
#     from library.database import connectDataBaseByInfo
#
#     login = u'админ'
#     userId = 1
#     eventId = 2074139
#
#     connectionInfo = {
#         'driverName': 'mysql',
#         'host': '192.168.0.3',
#         'port': 3306,
#         'database': 'ant_p17',
#         'user': 'dbuser',
#         'password': 'dbpassword',
#         'connectionName': 'vista-med',
#         'compressData': True,
#         'afterConnectFunc': None
#     }
#
#     QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))
#
#     QtGui.qApp = CS11mainApp(sys.argv, False, 'S11App.ini', False)
#     QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)
#     QtGui.qApp.mainWindow = CS11MainWindow()
#
#     QtGui.qApp.setUserId(userId, False)
#     QtGui.qApp.preferences.appUserName = login
#     QtGui.qApp.loadGlobalPreferences()
#
#     w = editEvent(None, eventId)
#     w.exec_()
#
#
# if __name__ == '__main__':
#     main()
