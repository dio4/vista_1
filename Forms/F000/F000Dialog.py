# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

# Форма 000: Платные услуги
from PyQt4 import QtCore, QtGui, QtSql

from Events.Action import CActionType, CActionTypeCache
from Events.ActionInfo import CActionInfoProxyList
from Events.ActionsSummaryModel import CFxxxActionsSummaryModel
from Events.DiagnosisType import CDiagnosisTypeCol
from Events.EventEditDialog import CEventEditDialog, CDiseaseCharacter, CDiseaseStage, CDiseasePhases
from Events.EventInfo import CDiagnosticInfoProxyList, CVisitInfoProxyList
from Events.EventVisitsModel import CEventVisitsModel
from Events.RecommendationsPage import CFastRecommendationsPage
from Events.Utils import checkDiagnosis, checkIsHandleDiagnosisIsChecked, getAvailableCharacterIdByMKB, \
    getDiagnosisId2, getDiagnosisSetDateVisible, getEventContextData, \
    getEventDuration, getEventShowTime, \
    getResultIdByDiagnosticResultId, hasEventVisitAssistant, \
    setAskedClassValueForDiagnosisManualSwitch, CTableSummaryActionsMenuMixin, \
    getEventLengthDays, \
    setOrgStructureIdToCmbPerson
from Forms.F000.PreF000Dialog import CPreF000Dialog, CPreF000DagnosticAndActionPresets
from Forms.F000.Ui_F000 import Ui_Dialog
from Forms.Utils import check_data_text_TNM
from RefBooks.Tables import rbDiagnosisType, rbDispanser, rbHealthGroup, rbResult, rbSpeciality, rbTraumaType
from Users.Rights import urAdmin, urAccessF000planner, urEditDiagnosticsInPayedEvents, urEditOwnEvents, \
    urRegTabWriteRegistry, \
    urOncoDiagnosisWithoutTNMS
from Users.UserInfo import CUserInfo
from library.ICDInDocTableCol import CICDExInDocTableCol
from library.ICDMorphologyInDocTableCol import CMKBMorphologyCol
from library.InDocTable import CInDocTableModel, CBoolInDocTableCol, CDateInDocTableCol, CRBInDocTableCol, \
    CActionPersonInDocTableColSearch
from library.PrintTemplates import applyTemplate, customizePrintButton, getPrintButton
from library.TNMS.TNMSComboBox import CTNMSCol
from library.Utils import forceBool, forceDate, forceInt, forceRef, forceString, toVariant, variantEq, \
    copyFields, formatNum, forceTr
from library.crbcombobox import CRBComboBox
from library.interchange import getDateEditValue, getDatetimeEditValue, getRBComboBoxValue, \
    setDateEditValue, setDatetimeEditValue, setRBComboBoxValue


class CF000Dialog(CEventEditDialog, Ui_Dialog, CTableSummaryActionsMenuMixin):
    isTabStatusAlreadyLoad = False
    isTabDiagnosticAlreadyLoad = False
    isTabCureAlreadyLoad = False
    isTabMiscAlreadyLoad = False
    isTabAnalysesAlreadyLoad = False
    isTabAmbCardAlreadyLoad = False
    isTabTempInvalidEtcAlreadyLoad = False
    isTabCashAlreadyLoad = False
    isTabNotesAlreadyLoad = False
    isTabDestinationsAlreadyLoad = False
    isTabRecommendationsAlreadyLoad = False

    # Параметры класса для вызова метода prepare родительского
    preDialogCheckedRightList = [urAccessF000planner]
    PreDialogClass = CPreF000Dialog
    PreDagnosticAndActionPresetsClass = CPreF000DagnosticAndActionPresets

    addActPrintEventCost = False

    def __init__(self, parent):
        # ctor
        CEventEditDialog.__init__(self, parent)
        self.mapSpecialityIdToDiagFilter = {}

        # create models
        self.addModels('Visits', CEventVisitsModel(self))
        self.addModels('FinalDiagnostics', CF000FinalDiagnosticsModel(self))
        self.addModels('ActionsSummary', CFxxxActionsSummaryModel(self, True, loadMedicaments=True))
        # ui
        self.createSaveAndCreateAccountButton()
        self.actEditClient = QtGui.QAction(u'Изменить описание клиента', self)
        self.actEditClient.setObjectName('actEditClient')
        self.btnPrint = getPrintButton(self, '')
        self.btnPrint.setObjectName('btnPrint')
        #        self.addObject('btnRelatedEvent', QPushButton(u'Связанные события', self))

        self.setupUi(self)

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

        if 'EventEditDialog.tabRecommendations' not in hiddenWidgets:
            self.tabRecommendations = CFastRecommendationsPage()
            self.tabWidget.insertTab(6, self.tabRecommendations, u'Рекомендации')
            self.tabRecommendations.preSetupUiMini()
            self.tabRecommendations.preSetupUi()
            self.tabRecommendations.setupUi(self.tabRecommendations)
            self.tabRecommendations.setupUiMini(self.tabRecommendations)
            self.tabRecommendations.postSetupUiMini()
            self.tabRecommendations.postSetupUi()
            self.tabRecommendations.setEventEditor(self)
        else:
            self.tabRecommendations = None

        self.tabNotes.preSetupUiMini()
        self.tabNotes.preSetupUi()
        self.tabNotes.setupUiMini(self.tabNotes)
        self.tabNotes.setupUi(self.tabNotes)
        self.tabNotes.postSetupUiMini(self.edtBegDate.date())

        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Осмотр Ф.000')
        #        self.edtBirthDate.setHighlightRedDate(False)
        self.tabToken.setFocusProxy(self.tblFinalDiagnostics)

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
        # tables to rb and combo-boxes

        # assign models
        self.tblVisits.setModel(self.modelVisits)
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
        self.markEditableTableWidget(self.tblVisits)
        self.markEditableTableWidget(self.tblFinalDiagnostics)
        self.markEditableTableWidget(self.tblActions)

        # popup menus
        self.txtClientInfoBrowser.actions.append(self.actEditClient)
        self.actEditClient.setEnabled(QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteRegistry]))
        self.tblFinalDiagnostics.addPopupDelRow()
        self.tblVisits.addPopupDelRow()
        CTableSummaryActionsMenuMixin.__init__(self)

        # default values
        db = QtGui.qApp.db
        self.setupDirtyCather()
        self.setIsDirty(False)
        self.blankMovingIdList = []
        self.valueForAllActionEndDate = None
        self.clientId = None
        self.prolongateEvent = False
        self.prevEventId = None
        self.tabNotes.setEventEditor(self)

        self.customPrimaryChkBox = QtGui.qApp.changePrimaryChkBox()
        if self.customPrimaryChkBox:
            self.chkSecondary.setVisible(True)
        else:
            self.chkSecondary.setVisible(False)

        self.cmbResult.setShowFields(CRBComboBox.showCodeAndName)

        self.postSetupUi()

        self.connect(self.modelActionsSummary, QtCore.SIGNAL('hideMedicamentColumns(bool)'), self.hideMedicamentCols)
        if self.tabDestinations:
            self.connect(self.tabDestinations.tblDestinations.selectionModel(),
                         QtCore.SIGNAL('selectionChanged(QItemSelection, QItemSelection)'),
                         self.tabDestinations.on_selectionModelDestinations_selectionChanged)

        if (not QtGui.qApp.userHasRight('accessEditAutoPrimacy')):
            if QtGui.qApp.isAutoPrimacy():
                self.chkPrimary.setEnabled(False)
                self.chkSecondary.setEnabled(False)

        # moved to EventEditDialog
        # self.cmbOrder.setTable('rbEventOrder', addNone=False)

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
        else:
            return CEventEditDialog.canClose(self)

    def getModelFinalDiagnostics(self):
        return self.modelFinalDiagnostics

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

        def prepVisit(date, personId, isAmb=True):
            sceneId = None if isAmb else QtGui.qApp.db.translate('rbScene', 'code', '2', 'id')
            visit = self.modelVisits.getEmptyRecord(sceneId=sceneId, personId=personId)
            visit.setValue('date', toVariant(date))
            return visit

        if self.tabDestinations:
            self.tabDestinations.setEventId(self.itemId(), clientId, personId)
        if self.tabRecommendations:
            self.tabRecommendations.setData(clientId, personId, self.contractId)

        self.eventSetDateTime = eventSetDatetime
        self.eventDate = eventDatetime
        self.setOrgId(orgId if orgId else QtGui.qApp.currentOrgId())
        self.setEventTypeId(eventTypeId)
        self.setClientId(clientId)
        self.prolongateEvent = True if actionByNewEvent else False
        self.setExternalId(externalId)
        self.cmbPerson.setValue(personId)
        self.edtNextDate.setDate(QtCore.QDate())
        self.cmbOrder.setCode(forceInt(QtGui.qApp.db.translate('EventType', 'id', eventTypeId, 'defaultOrder')))

        self.fillNextDate()  # must be after self.setEventTypeId
        if self.customPrimaryChkBox:
            self.setDefaultPrimaryState(clientId)
        else:
            self.chkPrimary.setChecked(self.isPrimary(clientId, eventTypeId, personId))
        self.paymentScheme = bool(self.clientInfo.paymentScheme)
        # self.paymentScheme = False
        self.setVisiblePaymentScheme(self.paymentScheme)
        self.setPaymentScheme()
        self.cmbResult.setCurrentIndex(0)
        self.tabNotes.setNotesEx(externalId, assistantId, curatorId, relegateOrgId, referrals=referrals)
        self.initFocus()
        self.setRecommendations(recommendationList)

        self.updateModelsRetiredList()

        visitTypeId = presetDiagnostics[0][4] if presetDiagnostics else None
        self.modelVisits.setDefaultVisitTypeId(visitTypeId)
        visits = []
        date = QtCore.QDate()
        if self.eventDate:
            date = self.eventDate
            resultId = self.cmbResult.value()
            # FINDME
            if not resultId and not QtGui.qApp.noDefaultResult():
                if self.cmbResult.model().rowCount() > 1:
                    self.cmbResult.setValue(self.cmbResult.model().getId(1))
        elif self.eventSetDateTime and self.eventSetDateTime.date():
            date = self.eventSetDateTime.date()
        else:
            date = QtCore.QDate.currentDate()
        visits.append(prepVisit(date, personId, isAmb))
        self.modelVisits.setItems(visits)
        self.updateVisitsInfo()

        if presetDiagnostics:
            resultId = None
            if self.cmbResult.model().rowCount() > 1:
                resultId = self.cmbResult.model().getId(1)
            for MKB, dispanserId, healthGroupId, medicalGroupId, visitTypeId, goalId, serviceId in presetDiagnostics:
                item = self.modelFinalDiagnostics.getEmptyRecord()
                item.setValue('MKB', toVariant(MKB))
                item.setValue('dispanser_id', toVariant(dispanserId))
                item.setValue('healthGroup_id', toVariant(healthGroupId))
                item.setValue('result_id', toVariant(getResultIdByDiagnosticResultId(resultId)))
                self.modelFinalDiagnostics.items().append(item)
            self.modelFinalDiagnostics.reset()
        self.prepareActions(contractId, presetActions, disabledActions, movingActionTypeId, valueProperties, diagnos,
                            financeId, protocolQuoteId, actionByNewEvent)
        if self.isTabTempInvalidEtcAlreadyLoad:
            self.grpTempInvalid.pickupTempInvalid()
            # self.grpAegrotat.pickupTempInvalid()
            self.grpDisability.pickupTempInvalid()
            self.grpVitalRestriction.pickupTempInvalid()
        self.setIsDirty(False)
        self.tabNotes.setEventEditor(self)
        return self.checkEventCreationRestriction()

    def prepareActions(self, contractId, presetActions, disabledActions, actionTypeIdValue, valueProperties, diagnos,
                       financeId, protocolQuoteId, actionByNewEvent):
        def addActionType(actionTypeId, amount, financeId, contractId, idListActionType, idListActionTypeIPH,
                          actionFinance, idListActionTypeMoving, org_id):
            for model in [self.tabStatus.modelAPActions,
                          self.tabDiagnostic.modelAPActions,
                          self.tabCure.modelAPActions,
                          self.tabMisc.modelAPActions,
                          self.tabAnalyses.modelAPActions]:
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

        ## Запрещает конкретный тип действия для выбора (в делегатах CActionTable, к примеру)
        def disableActionType(actionTypeId):
            for model in [self.tabStatus.modelAPActions,
                          self.tabDiagnostic.modelAPActions,
                          self.tabCure.modelAPActions,
                          self.tabMisc.modelAPActions,
                          self.tabAnalyses.modelAPActions]:
                if actionTypeId in model.actionTypeIdList:
                    model.disableActionType(actionTypeId)
                    break

        # end of sub-function disableActionType

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
                for actionTypeId, amount, cash, org_id in presetActions:
                    if actionTypeId in idListActionTypeMoving:
                        actionTypeMoving = True
                        break
                if not actionTypeMoving and idListActionTypeMoving:
                    presetActions.append((idListActionTypeMoving[0], 1.0, False, None))
            for actionTypeId, amount, cash, org_id in presetActions:
                addActionType(actionTypeId, amount, financeId if cash else None, contractId if cash else None,
                              idListActionType, idListActionTypeIPH, actionFinance, idListActionTypeMoving, org_id)

    def setLeavedAction(self, leavedActionTypeId):
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
            if leavedActionTypeId in model.actionTypeIdList:
                orgStructureLeaved = None
                movingQuoting = None
                orgStructureMoving = False
                for record, action in model.items():
                    actionTypeId = forceRef(record.value('actionType_id'))
                    if actionTypeId in idListActionType:
                        if not forceDate(record.value('endDate')):
                            record.setValue('endDate', toVariant(currentDateTime))
                            record.setValue('status', toVariant(2))
                        # atronah: Не понятно, зачем провека на существование actionTypeId, если выше проверяется его вхождение в список id всех moving action'ов
                        actionType = CActionTypeCache.getById(actionTypeId) if actionTypeId else None
                        # atronah: Не понятно, зачем проверять флэтКод типа действия на содержание 'moving' еще раз.
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
                model.addRow(leavedActionTypeId)
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

    # TODO: atronah: refactoring: необходимо вынести в EventEditDialog (почти у всех форм одинакова)
    def initFocus(self):
        if self.cmbContract.count() != 1 and not self.paymentScheme:
            self.cmbContract.setFocus(QtCore.Qt.OtherFocusReason)
        else:
            self.tblFinalDiagnostics.setFocus(QtCore.Qt.OtherFocusReason)

    def setVisiblePaymentScheme(self, bool):
        self.cmbContract.setVisible(not bool)
        self.lblCurrentItem.setVisible(bool)
        self.lblContract.setVisible(bool)
        self.lblPaymentScheme.setVisible(bool)
        self.cmbPaymentScheme.setVisible(bool)
        self.btnPaymentScheme.setVisible(bool)
        if bool:
            self.cmbPaymentScheme.setClientId(self.clientId)
            self.cmbPaymentScheme.setType(0 if forceString(
                QtGui.qApp.db.translate('EventType', 'id', self.eventTypeId, 'code')) == 'protocol' else 1)
            if len(self.clientInfo.paymentScheme) == 1:
                self.cmbPaymentScheme.setValue(self.clientInfo.paymentScheme[0][0])
            self.contractId = None
        if self.paymentSchemeItem:
            self.lblPaymentScheme.setEnabled(False)
            self.cmbPaymentScheme.setEnabled(False)

    def btnNextActionSetFocus(self):
        modelFind = self.tabMisc.modelAPActions
        items = modelFind.items()
        for rowFind, item in enumerate(items):
            record = item[0]
            if record:
                actionTypeIdFind = forceRef(record.value('actionType_id'))
                actionTypeFind = CActionTypeCache.getById(actionTypeIdFind) if actionTypeIdFind else None
                if u'received' in actionTypeFind.flatCode.lower():
                    self.tabWidget.setCurrentIndex(4)
                    self.tabMisc.tblAPActions.setCurrentIndex(modelFind.index(rowFind, 0))
                    self.tabMisc.btnNextAction.setFocus(QtCore.Qt.OtherFocusReason)
                    break

    def setRecord(self, record):
        CEventEditDialog.setRecord(self, record)
        self.paymentScheme = bool(self.clientInfo.paymentScheme)
        # self.paymentScheme = False
        self.setVisiblePaymentScheme(self.paymentScheme)
        setDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'setDate')
        setRBComboBoxValue(self.cmbPerson, record, 'setPerson_id')
        setDatetimeEditValue(self.edtEndDate, self.edtEndTime, record, 'execDate')
        setRBComboBoxValue(self.cmbPerson, record, 'execPerson_id')
        setRBComboBoxValue(self.cmbResult, record, 'result_id')
        setDateEditValue(self.edtNextDate, record, 'nextEventDate')
        self.chkPrimary.setChecked(forceInt(record.value('isPrimary')) == 1)
        self.chkSecondary.setChecked(forceInt(record.value('isPrimary')) == 2)
        self.setExternalId(forceString(record.value('externalId')))
        # setComboBoxValue(self.cmbOrder,         record, 'order')
        self.cmbOrder.setCode(forceString(record.value('order')))
        self.setPersonId(self.cmbPerson.value())
        if self.paymentScheme:
            self.contractId = forceRef(record.value('contract_id'))
        else:
            self.setContract()
            setRBComboBoxValue(self.cmbContract, record, 'contract_id')
        self.prevEventId = forceRef(record.value('prevEvent_id'))
        if self.prevEventId:
            self.lblProlongateEvent.setText(u'п')
            db = QtGui.qApp.db
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
        self.loadDiagnostics(self.modelFinalDiagnostics, self.itemId())
        self.loadVisits()
        if self.isTabTempInvalidEtcAlreadyLoad:
            self.grpTempInvalid.pickupTempInvalid()
            # self.grpAegrotat.pickupTempInvalid()
            self.grpDisability.pickupTempInvalid()
            self.grpVitalRestriction.pickupTempInvalid()
        self.loadActions()
        self.tabCash.load(self.itemId())
        self.tabNotes.setNotes(record)
        self.tabNotes.updateReferralPeriod(self.edtBegDate.date())
        self.tabNotes.setEventEditor(self)
        self.initFocus()
        self.setIsDirty(False)
        self.blankMovingIdList = []
        self.setEditable(self.getEditable())
        self.setPaymentScheme()
        if self.tabDestinations:
            self.tabDestinations.setEventId(self.itemId(), self.clientId, self.personId)
        self.paymentScheme = self.cmbPaymentScheme.value()
        setOrgStructureIdToCmbPerson(self.cmbPerson)

    def setEditable(self, editable):
        if not editable:
            localEditable = editable
        else:
            # Если последний изменивший - не я, настройки редактирования распространяются на все
            if self.cmbPerson.value() != QtGui.qApp.userId:
                localEditable = editable
            else:  # Если ответственный - я, то
                # Если только создаем обращение или есть право на редактирование собственных обращений
                if QtGui.qApp.userHasRight(urEditOwnEvents) or not self.itemId():
                    localEditable = True
                # Если права нет, то закрыть стат. учет и статус.
                else:
                    localEditable = False
        self.modelVisits.setEditable(editable and localEditable)
        self.modelActionsSummary.setEditable(editable and localEditable)
        self.modelFinalDiagnostics.setEditable(
            (editable or QtGui.qApp.userHasRight(urEditDiagnosticsInPayedEvents)) and localEditable)
        self.grpBase.setEnabled(editable and localEditable)
        self.tabStatus.setEditable(editable and localEditable)
        self.tabDiagnostic.setEditable(editable)
        self.tabCure.setEditable(editable)
        self.tabMisc.setEditable(editable)
        self.tabAnalyses.setEditable(editable)
        # tabTempInvalidEtc
        self.grpDisability.setEnabled(editable)
        self.grpVitalRestriction.setEnabled(editable)
        self.tabTempInvalid.setEnabled(editable)
        self.tabInvalidDisability.setEnabled(editable)
        self.tabInvalidTempInv.setEnabled(editable)
        # self.tabAegrotat.setEnabled(editable)
        # end of tabTempInvalidEtc
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
                    self.tabNotes.edtPrevEventInfo.setText(u'Продолжение обращения: %s от %s.' % (
                    forceString(record.value('name')), forceDate(record.value('setDate')).toString('dd.MM.yyyy')))
            self.createDiagnostics(eventId)

    def createDiagnostics(self, eventId):
        if eventId:
            self.loadDiagnostics(self.modelPreliminaryDiagnostics, eventId)
            self.loadDiagnostics(self.modelFinalDiagnostics, eventId)

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
        self.tabCash.modelAccActions.regenerate()

    def getRecord(self):
        record = CEventEditDialog.getRecord(self)
        showTime = getEventShowTime(self.eventTypeId)
        # перенести в exec_ в случае успеха или в accept?
        if self.paymentScheme:
            record.setValue('contract_id', toVariant(self.contractId))
        else:
            getRBComboBoxValue(self.cmbContract, record, 'contract_id')
        #        getDateEditValue(self.edtPrevDate,      record, 'prevEventDate')
        getDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'setDate', showTime)
        getRBComboBoxValue(self.cmbPerson, record, 'setPerson_id')
        getDatetimeEditValue(self.edtEndDate, self.edtEndTime, record, 'execDate', showTime)
        getRBComboBoxValue(self.cmbPerson, record, 'execPerson_id')
        getRBComboBoxValue(self.cmbResult, record, 'result_id')
        getDateEditValue(self.edtNextDate, record, 'nextEventDate')
        if self.customPrimaryChkBox:
            primaryStatus = 1 if self.chkPrimary.isChecked() else None
            if not primaryStatus:
                primaryStatus = 2 if self.chkSecondary.isChecked() else None
            record.setValue('isPrimary', toVariant(primaryStatus))
        else:
            record.setValue('isPrimary', toVariant(1 if self.chkPrimary.isChecked() else 2))
        if self.prolongateEvent:
            record.setValue('order', toVariant(5))
            record.setValue('prevEvent_id', toVariant(self.prevEventId))
        # getComboBoxValue(self.cmbOrder,         record, 'order')
        record.setValue('order', toVariant(self.cmbOrder.code()))
        ###  payStatus
        self.tabNotes.getNotes(record, self.eventTypeId)
        return record

    def saveInternals(self, eventId):
        super(CF000Dialog, self).saveInternals(eventId)
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
        if self.tabRecommendations:
            self.tabRecommendations.save(eventId)
        self.updateRecommendations()

    def saveVisits(self, eventId):
        items = self.modelVisits.items()
        personIdVariant = toVariant(self.personId)
        eventSetDateTimeVariant = toVariant(self.eventSetDateTime)

        for item in items:
            if not forceRef(item.value('person_id')):
                item.setValue('person_id', personIdVariant)
            if not forceDate(item.value('date')):
                item.setValue('date', eventSetDateTimeVariant)
        self.modelVisits.saveItems(eventId)

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
        diagnostics = self.modelFinalDiagnostics.items()
        if diagnostics:
            MKB = forceString(diagnostics[0].value('MKB'))
            MKBEx = forceString(diagnostics[0].value('MKBEx'))
            return MKB, MKBEx
        else:
            return '', ''

    def getFinalDiagnosisId(self):
        diagnostics = self.modelFinalDiagnostics.items()
        return forceRef(diagnostics[0].value('diagnosis_id')) if diagnostics else None

    def saveActions(self, eventId):
        self.tabStatus.saveActions(eventId)
        self.tabDiagnostic.saveActions(eventId)
        self.tabCure.saveActions(eventId)
        self.tabMisc.saveActions(eventId)
        self.tabAnalyses.saveActions(eventId)

    def setOrgId(self, orgId):
        super(CF000Dialog, self).setOrgId(orgId)
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

    def setEventTypeId(self, eventTypeId):
        CEventEditDialog.setEventTypeId(self, eventTypeId, u'Ф.000')
        self.tabCash.windowTitle = self.windowTitle()
        showTime = getEventShowTime(eventTypeId)
        self.edtBegTime.setVisible(showTime)
        self.edtEndTime.setVisible(showTime)
        self.cmbResult.setTable(rbResult, True, 'eventPurpose_id=\'%d\'' % self.eventPurposeId)
        if self.cmbResult.value() is None:
            if self.inheritResult == True:
                self.cmbResult.setValue(self.defaultEventResultId.get(self.eventPurposeId))
        cols = self.modelFinalDiagnostics.cols()
        resultCol = cols[len(cols) - 1]
        resultCol.filter = 'eventPurpose_id=\'%d\'' % self.eventPurposeId
        self.setVisitAssistantVisible(self.tblVisits, hasEventVisitAssistant(eventTypeId))
        customizePrintButton(self.btnPrint, self.eventContext if self.eventContext else 'F000')
        self.diagnosisSetDateVisible = forceBool(getDiagnosisSetDateVisible(eventTypeId))
        if self.diagnosisSetDateVisible == False:
            self.tblFinalDiagnostics.setColumnHidden(4, True)

    def setDefaultPrimaryState(self, clientId):
        if not QtGui.qApp.db.getRecordEx('Event', 'Event.id',
                                         'Event.client_id = %s AND year(Event.execDate) = year(curdate()) AND Event.deleted = 0' % clientId) is None:
            isPrimary = False
        else:
            isPrimary = True
        self.chkPrimary.setChecked(isPrimary)
        self.chkSecondary.setChecked(not isPrimary)

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
            date = forceDate(item.value('date'))
            if not date.isNull():
                dates.append(date)
        if dates:
            minDate = min(dates)
            maxDate = max(dates)
            days = minDate.daysTo(maxDate) + 1
        else:
            days = 0
        self.setEventDuration(days)
        self.lblVisitsDurationValue.setText(str(days))

    def updateMKB(self):
        begDate = self.edtBegDate.date()
        filter = None
        if begDate.isValid():
            filter = {'begDate': begDate, 'clientId': self.clientId}
        cols = self.modelFinalDiagnostics.cols()
        resultCol = cols[2]
        resultCol.setFilter(filter)

    def checkDataEntered(self):
        result = CEventEditDialog.checkDataEntered(self)
        self.blankMovingIdList = []
        begDate = self.edtBegDate.date()
        endDate = self.edtEndDate.date() if self._isClosedEventCheck else QtCore.QDate()
        nextDate = self.edtNextDate.date()
        if self.tabDestinations:
            result = result and self.tabDestinations.checkDataEntered()
        result = result and (
        self.orgId != QtGui.qApp.currentOrgId() or self.cmbContract.value() or self.checkInputMessage(u'договор', False,
                                                                                                      self.cmbContract))
        result = result and (self.cmbPerson.value() or self.checkInputMessage(u'врача', False, self.cmbPerson))
        result = result and (not begDate.isNull() or self.checkInputMessage(u'дату назначения', False, self.edtBegDate))
        if endDate:
            result = result and self.checkActionDataEntered(begDate, QtCore.QDate(), endDate, self.tabToken,
                                                            self.edtBegDate, None, self.edtEndDate)
            result = result and self.checkEventDate(begDate, endDate, nextDate, self.tabToken, self.edtNextDate,
                                                    self.edtEndDate, True)
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
                                                            False, self.edtEndDate))
                # if not QtGui.qApp.userHasRight(urDoNotCheckResultAndMKB):
                #    result = result and (self.cmbResult.value()  or self.checkInputMessage(u'результат',   False, self.cmbResult))

        if \
                                                                self.getFinalDiagnosisMKB()[0] is not None and \
                                                                self.getFinalDiagnosisMKB()[0] != u'' and \
                                                        self.getFinalDiagnosisMKB()[0][0] == u'C' \
                                        and not QtGui.qApp.userHasRight(urOncoDiagnosisWithoutTNMS) \
                                and QtGui.qApp.isTNMSVisible() and (
                        self.getModelFinalDiagnostics().items()[0].value('TNMS') is None or
                        forceString(self.getModelFinalDiagnostics().items()[0].value('TNMS')) == ''):
            result = result and self.checkValueMessage(check_data_text_TNM, False, None)

        result = result and self.checkDiagnosticsDataEntered([(self.tblFinalDiagnostics, True, True, None)], endDate)

        result = result and self.checkActionsDateEnteredActuality(begDate, endDate,
                                                                  [self.tabStatus, self.tabDiagnostic, self.tabCure,
                                                                   self.tabMisc, self.tabAnalyses])
        result = result and self.checkActionsDataEntered(
            [self.tabStatus, self.tabDiagnostic, self.tabCure, self.tabMisc, self.tabMisc], begDate, endDate)
        result = result and (
        len(self.modelVisits.items()) > 0 or self.checkInputMessage(u'посещение', False, self.tblVisits))
        result = result and self.checkVisitsDataEntered(begDate, endDate)
        result = result and self.checkPrimaryStatus()
        if self.isTabTempInvalidEtcAlreadyLoad:
            result = result and self.grpTempInvalid.checkTempInvalidDataEntered()
            # result = result and self.grpAegrotat.checkTempInvalidDataEntered()
            result = result and self.grpDisability.checkTempInvalidDataEntered()
            result = result and self.grpVitalRestriction.checkTempInvalidDataEntered()
        result = result and self.checkSerialNumberEntered()
        if self.isTabCashAlreadyLoad:
            result = result and self.tabCash.checkDataLocalContract()
        result = result and self.checkTabNotesReferral()
        if self.isTabRecommendationsAlreadyLoad:
            result = result and self.checkRecommendationsDataEntered()
        self.valueForAllActionEndDate = None
        return result

    def checkPrimaryStatus(self):
        if self.customPrimaryChkBox:
            return self.chkPrimary.isChecked() or \
                   self.chkSecondary.isChecked() or \
                   self.checkInputMessage(u'признак первичности', False, self.chkPrimary)
        return True

    def checkActionEndDate(self, strNameActionType, tblWidget, row, column, widgetEndDate):
        # переопределяем CEventEditDialog.checkActionEndDate
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

    def checkSerialNumberEntered(self):
        result = True
        self.blankMovingIdList = []
        db = QtGui.qApp.db
        tableAPT = db.table('ActionPropertyType')
        actionTypeIdListSerial = db.getDistinctIdList(tableAPT, tableAPT['actionType_id'], [tableAPT['deleted'].eq(0),
                                                                                            tableAPT['typeName'].like(
                                                                                                'BlankSerial')])

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

    def getVisitCount(self):
        return len(self.modelVisits.items())

    def getDiagFilter(self):
        specialityId = self.personSpecialityId
        result = self.mapSpecialityIdToDiagFilter.get(specialityId, None)
        if result == None:
            result = QtGui.qApp.db.translate(rbSpeciality, 'id', specialityId, 'mkbFilter')
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
        return forceRef(QtGui.qApp.db.translate(rbDiagnosisType, 'code', '2' if dt else '9', 'id'))

    def getEventInfo(self, context):
        if not self.isTabCashAlreadyLoad:
            self.initTabCash(False)
        result = CEventEditDialog.getEventInfo(self, context)
        # инициализация свойств
        result._isPrimary = self.chkPrimary.isChecked()
        # инициализация таблиц
        result._actions = CActionInfoProxyList(context,
                                               [self.tabStatus.modelAPActions, self.tabDiagnostic.modelAPActions,
                                                self.tabCure.modelAPActions, self.tabMisc.modelAPActions,
                                                self.tabAnalyses.modelAPActions],
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

    def initTabDestinations(self, show=True):
        if self.tabDestinations:
            if show: self.tabDestinations.setVisible(False)
            self.tabDestinations.postSetupUi()
            self.tabDestinations.setData(self.itemId(), self.personId)
            if show: self.tabDestinations.setVisible(True)

            self.isTabDestinationsAlreadyLoad = True

    def initTabRecommendations(self, show=True):
        if self.tabRecommendations:
            if show: self.tabRecommendations.setVisible(False)
            self.tabRecommendations.postSetupUi()
            self.tabRecommendations.setData(self.clientId, self.personId, self.contractId)
            self.tabRecommendations.load(self.itemId())
            if show: self.tabRecommendations.setVisible(True)
            self.isTabRecommendationsAlreadyLoad = True

    @QtCore.pyqtSlot(int)
    def on_btnPrint_printByTemplate(self, templateId):
        if self.beforePrintTemplate(templateId) == -1:
            return
        if not self.isTabTempInvalidEtcAlreadyLoad:
            self.initTabTempInvalidEtc(False)
        if not self.isTabCashAlreadyLoad:
            self.initTabCash(False)
        data = getEventContextData(self)
        data['templateCounterValue'] = self.oldTemplates.get(templateId, '')
        applyTemplate(self, templateId, data)

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
        self.emitUpdateActionsAmount()
        self.setContract()
        if QtGui.qApp.isCheckMKB():
            self.updateMKB()

        self.updateModelsRetiredList()

    @QtCore.pyqtSlot(QtCore.QTime)
    def on_edtBegTime_timeChanged(self, time):
        self.emitUpdateActionsAmount()

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtEndDate_dateChanged(self, date):
        resultId = self.cmbResult.value()
        if not resultId:
            if self.cmbResult.model().rowCount() > 1:
                self.cmbResult.setValue(self.cmbResult.model().getId(1))
        self.emitUpdateActionsAmount()
        self.setContract()
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
        self.tabAnalyses.updatePersonId(oldPersonId, self.personId)
        if self.isTabRecommendationsAlreadyLoad:
            self.tabRecommendations.updatePersonId(self.personId)

    def on_modelFinalDiagnostics_typeOrPersonChanged(self):
        self.updateVisitsByDiagnostics(self.sender())

    @QtCore.pyqtSlot()
    def on_modelFinalDiagnostics_resultChanged(self):
        CEventEditDialog.defaultDiagnosticResultId[self.eventPurposeId] = self.modelFinalDiagnostics.resultId()
        self.updateResultFilter()
        # if self.cmbResult.value() is None:
        #     self.cmbResult.setValue(getEventResultId(CEventEditDialog.defaultDiagnosticResultId.get(self.eventPurposeId)))

    @QtCore.pyqtSlot()
    def on_actDiagnosticsAddAccomp_triggered(self):
        currentRow = self.tblFinalDiagnostics.currentIndex().row()
        if currentRow >= 0:
            currentRecord = self.modelFinalDiagnostics.items()[currentRow]
            newRecord = self.modelFinalDiagnostics.getEmptyRecord()
            newRecord.setValue('diagnosisType', QtCore.QVariant(CF000Dialog.dfAccomp))
            newRecord.setValue('speciality_id', currentRecord.value('speciality_id'))
            newRecord.setValue('healthGroup_id', currentRecord.value('healthGroup_id'))
            self.modelFinalDiagnostics.insertRecord(currentRow + 1, newRecord)
            self.tblFinalDiagnostics.setCurrentIndex(
                self.modelFinalDiagnostics.index(currentRow + 1, newRecord.indexOf('MKB')))

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

    @QtCore.pyqtSlot(bool)
    def on_chkPrimary_toggled(self, state):
        if self.customPrimaryChkBox and state:
            self.chkSecondary.setChecked(False)

    @QtCore.pyqtSlot(bool)
    def on_chkSecondary_toggled(self, state):
        if self.customPrimaryChkBox and state:
            self.chkPrimary.setChecked(False)


class CF000BaseDiagnosticsModel(CInDocTableModel):
    __pyqtSignals__ = ('typeOrPersonChanged()',
                       )
    MKB_allowed_morphology = ['C', 'D']

    def __init__(self, parent, finishDiagnosisTypeCode, baseDiagnosisTypeCode, accompDiagnosisTypeCode):
        CInDocTableModel.__init__(self, 'Diagnostic', 'id', 'event_id', parent)
        self._parent = parent
        self.isManualSwitchDiagnosis = QtGui.qApp.defaultIsManualSwitchDiagnosis()
        self.isMKBMorphology = QtGui.qApp.defaultMorphologyMKBIsVisible()
        self.characterIdForHandleDiagnosis = None
        self.columnHandleDiagnosis = None
        self._parent = parent
        self.diagnosisTypeCol = CDiagnosisTypeCol(u'Тип', 'diagnosisType_id', 2,
                                                  [finishDiagnosisTypeCode, baseDiagnosisTypeCode,
                                                   accompDiagnosisTypeCode], smartMode=False)
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
        self.addCol(CRBInDocTableCol(u'ДН', 'dispanser_id', 7, rbDispanser, showFields=CRBComboBox.showCode,
                                     prefferedWidth=150)).setToolTip(u'Диспансерное наблюдение')
        #        self.addCol(CRBLikeEnumInDocTableCol(u'Госп',      'hospital',       7, CHospitalInfo.names, showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(u'Потребность в госпитализации')
        self.addCol(CRBInDocTableCol(u'Травма', 'traumaType_id', 10, rbTraumaType, addNone=True,
                                     showFields=CRBComboBox.showName, prefferedWidth=150))
        self.addCol(
            CRBInDocTableCol(u'ГрЗд', 'healthGroup_id', 7, rbHealthGroup, addNone=True, showFields=CRBComboBox.showCode,
                             prefferedWidth=150)).setToolTip(u'Группа здоровья')
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
                    if not (mkb and mkb[0] in CF000BaseDiagnosticsModel.MKB_allowed_morphology):
                        result = (result & ~QtCore.Qt.ItemIsEditable)
        if QtGui.qApp.isPNDDiagnosisMode() and (
                row == len(self.items()) or index.column() != self._mapFieldNameToCol.get('result_id')):
            result = (result & ~QtCore.Qt.ItemIsEditable)
        return result

    def getEmptyRecord(self):
        eventEditor = QtCore.QObject.parent(self)
        result = CInDocTableModel.getEmptyRecord(self)
        result.append(QtSql.QSqlField('diagnosis_id', QtCore.QVariant.Int))
        result.append(QtSql.QSqlField('speciality_id', QtCore.QVariant.Int))
        result.append(QtSql.QSqlField('setDate', QtCore.QVariant.DateTime))
        result.append(QtSql.QSqlField('endDate', QtCore.QVariant.DateTime))
        result.setValue('person_id', toVariant(eventEditor.getSuggestedPersonId()))
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
                    self.emitTypeOrPersonChanged()
                return result
            elif column == 1:  # врач
                personId = forceRef(value)
                if not eventEditor.checkClientAttendaceEE(personId):
                    return False
                result = CInDocTableModel.setData(self, index, value, role)
                if result:
                    self.updateDiagnosisType(set())
                    # self.emitTypeOrPersonChanged()
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
                    self.emitTypeOrPersonChanged()
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
                return result

            return CInDocTableModel.setData(self, index, value, role)
        else:
            return True

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


class CF000FinalDiagnosticsModel(CF000BaseDiagnosticsModel):
    __pyqtSignals__ = ('resultChanged()',)

    def __init__(self, parent):
        CF000BaseDiagnosticsModel.__init__(self, parent, '1', '2', '9')
        self.addCol(CRBInDocTableCol(forceTr(u'Результат', u'EventDiagnostic'), 'result_id', 10, 'rbDiagnosticResult',
                                     showFields=CRBComboBox.showNameAndCode, prefferedWidth=350))
        self.mapMKBToServiceId = {}

    def addRecord(self, record):
        super(CF000FinalDiagnosticsModel, self).addRecord(record)
        self.emitResultChanged()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        result = CF000BaseDiagnosticsModel.setData(self, index, value, role)
        if result:
            column = index.column()
            if column == 0 or column == self._mapFieldNameToCol.get('result_id'):  # тип диагноза и результат
                row = index.row()
                item = self.items()[row]
                diagnosisTypeId = forceRef(item.value('diagnosisType_id'))
        self.emitResultChanged()
        return result

    def getCloseOrMainDiagnosisTypeIdList(self):
        return [self.diagnosisTypeCol.codeToId(code) for code in ['1', '2']]

    def getFinalDiagnosis(self):
        finalDiagnosisId = self.diagnosisTypeCol.ids[0]
        items = self.items()
        for item in items:
            diagnosisTypeId = forceRef(item.value('diagnosisType_id'))
            if diagnosisTypeId == finalDiagnosisId:
                return item
        return None

    def resultId(self):
        finalDiagnosisId = self.diagnosisTypeCol.ids[0]
        items = self.items()
        for item in items:
            diagnosisTypeId = forceRef(item.value('diagnosisType_id'))
            if diagnosisTypeId == finalDiagnosisId:
                return forceRef(item.value('result_id'))
        return None

    def emitResultChanged(self):
        self.emit(QtCore.SIGNAL('resultChanged()'))
