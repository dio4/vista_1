# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

# Форма 110/У: Станция скорой медицинской помощи

from PyQt4 import QtCore, QtGui, QtSql

from Events.Action import CActionType, CActionTypeCache
from Events.ActionInfo import CActionInfoProxyList
from Events.ActionsSummaryModel import CActionsSummaryModel
from Events.DiagnosisType import CDiagnosisTypeCol
from Events.EventEditDialog import CEventEditDialog, CDiseaseCharacter, CDiseaseStage, CDiseasePhases
from Events.EventInfo import CDiagnosticInfoProxyList, CEmergencyAccidentInfo, CEmergencyBrigadeInfo, \
    CEmergencyCauseCallInfo, CEmergencyDeathInfo, CEmergencyDiseasedInfo, \
    CEmergencyEbrietyInfo, CEmergencyEventInfo, CEmergencyMethodTransportInfo, \
    CEmergencyPlaceCallInfo, CEmergencyPlaceReceptionCallInfo, \
    CEmergencyReasondDelaysInfo, CEmergencyReceivedCallInfo, CEmergencyResultInfo, \
    CEmergencyTransferTransportInfo, CEmergencyTypeAssetInfo, CHospitalInfo, \
    CVisitPersonallInfo
from Events.Utils import checkDiagnosis, checkIsHandleDiagnosisIsChecked, getAvailableCharacterIdByMKB, \
    getDiagnosisId2, getDiagnosisSetDateVisible, getEventDuration, getEventShowTime, \
    setAskedClassValueForDiagnosisManualSwitch, getEventLengthDays, \
    setOrgStructureIdToCmbPerson, EventOrder
from Forms.F110.PreF110Dialog import CPreF110Dialog, CPreF110DagnosticAndActionPresets
from Forms.Utils import check_data_text_TNM
from Ui_F110 import Ui_Dialog
from Users.Rights import urAccessF110planner, urAdmin, urRegTabWriteRegistry, \
    urOncoDiagnosisWithoutTNMS
from library.ICDInDocTableCol import CICDExInDocTableCol
from library.ICDMorphologyInDocTableCol import CMKBMorphologyCol
from library.InDocTable import CInDocTableModel, CBoolInDocTableCol, CDateInDocTableCol, CRBInDocTableCol, \
    CRBLikeEnumInDocTableCol, \
    CActionPersonInDocTableColSearch
from library.ItemsListDialog import CItemEditorBaseDialog
from library.PrintInfo import CInfoContext, CDateInfo, CDateTimeInfo
from library.PrintTemplates import applyTemplate, customizePrintButton, getPrintButton
from library.TNMS.TNMSComboBox import CTNMSCol
from library.Utils import forceBool, forceDate, forceInt, forceRef, forceString, toVariant, copyFields, \
    formatNum, variantEq, forceTr
from library.crbcombobox import CRBComboBox
from library.interchange import getDatetimeEditValue, getLineEditValue, getRBComboBoxValue, setComboBoxValue, \
    setDatetimeEditValue, setLineEditValue, setRBComboBoxValue


class CEmergencyCallEditDialog(CItemEditorBaseDialog):
    def __init__(self, parent):
        CItemEditorBaseDialog.__init__(self, parent, 'EmergencyCall')


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)


    def getRecord(self):
        if not self.record():
            record = CItemEditorBaseDialog.getRecord(self)
        else:
            record = self.record()
        return record


    def saveEmergencyCall(self):
        self.save()


class CF110Dialog(CEventEditDialog, Ui_Dialog, CEmergencyCallEditDialog):
    isTabMesAlreadyLoad = False

    def __init__(self, parent):
        CEventEditDialog.__init__(self, parent)
        self.EmergencyCallEditDialog = CEmergencyCallEditDialog(self)
        self.mapSpecialityIdToDiagFilter = {}

        self.addModels('Personnel', CF110PersonnelModel(self))
        self.addModels('FinalDiagnostics', CF110FinalDiagnosticsModel(self))
        self.addModels('ActionsSummary', CActionsSummaryModel(self, True))

        self.actEditClient = QtGui.QAction(u'Изменить описание клиента', self)
        self.actEditClient.setObjectName('actEditClient')
        self.setupActionsMenu()
        self.btnPrint = getPrintButton(self, '')
        self.btnPrint.setObjectName('btnPrint')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Осмотр Ф.110')
        self.tabToken.setFocusProxy(self.tblFinalDiagnostics)
        # self.tabTempInvalidAndAegrotat.setCurrentIndex(1 if QtGui.qApp.tempInvalidDoctype() == '2' else 0)
        self.grpTempInvalid.setEventEditor(self)
        self.grpTempInvalid.setType(0, '1')
        # self.grpAegrotat.setEventEditor(self)
        # self.grpAegrotat.setType(0, '2')
        self.grpDisability.setEventEditor(self)
        self.grpDisability.setType(1)
        self.grpVitalRestriction.setEventEditor(self)
        self.grpVitalRestriction.setType(2)

        self.tabMes.preSetupUiMini()
        self.tabMes.preSetupUi()
        self.tabMes.setupUi(self.tabMes)
        self.tabMes.setupUiMini(self.tabMes)
        self.tabMes.postSetupUiMini()

        self.tabStatus.setEventEditor(self)
        self.tabDiagnostic.setEventEditor(self)
        self.tabCure.setEventEditor(self)
        self.tabMisc.setEventEditor(self)
        self.tabCash.setEventEditor(self)
        self.tabMes.setEventEditor(self)
        self.tabStatus.setActionTypeClass(0)
        self.tabDiagnostic.setActionTypeClass(1)
        self.tabCure.setActionTypeClass(2)
        self.tabMisc.setActionTypeClass(3)
        self.buttonBox.addButton(self.btnPrint, QtGui.QDialogButtonBox.ActionRole)
        self.setupActionSummarySlots()
        self.cmbContract.setCheckMaxClients(True)

        self.tblPersonnel.setModel(self.modelPersonnel)
        self.tblFinalDiagnostics.setModel(self.modelFinalDiagnostics)
        self.modelActionsSummary.addModel(self.tabStatus.modelAPActions)
        self.modelActionsSummary.addModel(self.tabDiagnostic.modelAPActions)
        self.modelActionsSummary.addModel(self.tabCure.modelAPActions)
        self.modelActionsSummary.addModel(self.tabMisc.modelAPActions)
        self.tabCash.addActionModel(self.tabStatus.modelAPActions)
        self.tabCash.addActionModel(self.tabDiagnostic.modelAPActions)
        self.tabCash.addActionModel(self.tabCure.modelAPActions)
        self.tabCash.addActionModel(self.tabMisc.modelAPActions)

        self.markEditableTableWidget(self.tblPersonnel)
        self.markEditableTableWidget(self.tblFinalDiagnostics)

        self.txtClientInfoBrowser.actions.append(self.actEditClient)
        self.actEditClient.setEnabled(QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteRegistry]))
        self.tblFinalDiagnostics.addPopupDelRow()
        self.tblPersonnel.addPopupDelRow()

        self.setupDirtyCather()
        self.setIsDirty(False)
        self.blankMovingIdList = []
        self.clientId = None
        self.tabNotes.setEventEditor(self)
        self.cmbResult.setShowFields(CRBComboBox.showCodeAndName)

        self.postSetupUi()

        self.connect(self.tabMes.cmbMes, QtCore.SIGNAL('editTextChanged(QString)'), self.updateMesDurationsMap)
        self.chkDispByMobileTeam.setVisible(QtGui.qApp.region() == '23')

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
        return self.edtFinishServiceDate.date()

    @eventDate.setter
    def eventDate(self, value):
        if isinstance(value, QtCore.QDate):
            self.edtFinishServiceDate.setDate(value)
            self.edtFinishServiceTime.setTime(QtCore.QTime())
        elif isinstance(value, QtCore.QDateTime):
            self.edtFinishServiceDate.setDate(value.date())
            self.edtFinishServiceTime.setTime(value.time())

    def setupActionsMenu(self):
        self.mnuAction = QtGui.QMenu(self)
        self.mnuAction.setObjectName('mnuAction')
        self.actActionEdit = QtGui.QAction(u'Перейти к редактированию', self)
        self.actActionEdit.setObjectName('actActionEdit')
        self.actActionEdit.setShortcut(QtCore.Qt.Key_F4)
        self.mnuAction.addAction(self.actActionEdit)

    def setOrder(self, order):
        u""" Устанавливает индекс порядка наступления
         @param order: целое число: 1-плановый, 2-экстренный, 3-самотёком, 4-принудительный, 5-неотложный (@see EventOrder)"""
        self.cmbOrder.setCurrentIndex({EventOrder.Emergency: 1,
                                       EventOrder.Urgent: 2}.get(order, 0))

    def order(self):
        return {1: EventOrder.Emergency,
                2: EventOrder.Urgent}.get(self.cmbOrder.currentIndex(), 0)

    def _prepare(self, contractId, clientId, eventTypeId, orgId, personId, eventSetDatetime, eventDatetime, includeRedDays, numDays,
                 presetDiagnostics, presetActions, disabledActions, externalId, assistantId, curatorId,
                 actionTypeIdValue=None, valueProperties=None, relegateOrgId=None, diagnos=None,
                 financeId=None, protocolQuoteId=None, actionByNewEvent=None,
                 referrals=None, isAmb=True, recommendationList=None):
        if not valueProperties:
            valueProperties = []
        if not actionByNewEvent:
            actionByNewEvent = []
        if not referrals:
            referrals = {}
        if not recommendationList:
            recommendationList = []

        def prepNumberBrigade(personId):
            numberBrigade = None
            if personId:
                numberBrigade = forceRef(QtGui.qApp.db.translate('EmergencyBrigade_Personnel', 'person_id', personId, 'master_id'))
            return numberBrigade

        def prepPersonnelBrigade(numberBrigade = None):
            if numberBrigade:
                visits = []
                db = QtGui.qApp.db
                tablePersonnel = db.table('EmergencyBrigade_Personnel')
                records = db.getRecordList(tablePersonnel, [tablePersonnel['person_id']], [tablePersonnel['master_id'].eq(numberBrigade)], 'idx')
                for record in records:
                    visit = self.modelPersonnel.getEmptyRecord()
                    person_Id = forceRef(record.value('person_id'))
                    if person_Id:
                        visit.setValue('person_id', toVariant(person_Id))
                        visits.append(visit)
                self.modelPersonnel.setItems(visits)

        self.cmbResult.setTable('rbResult', True)
        self.eventSetDateTime = eventSetDatetime
        self.eventDate = eventDatetime
        self.setOrgId(orgId if orgId else QtGui.qApp.currentOrgId())
        self.setClientId(clientId)
        self.clientId = clientId
        self.setExternalId(externalId)
        self.cmbPerson.setValue(personId)
        self.edtEndDate.setDate(QtCore.QDate())
        self.edtEndTime.setTime(QtCore.QTime())
        self.edtNextTime.setTime(QtCore.QTime())
        self.setEventTypeId(eventTypeId)
        self.fillNextDate() # must be after self.setEventTypeId
        brigadeId = prepNumberBrigade(personId)
        if brigadeId:
            self.cmbNumberBrigade.setValue(brigadeId)
        self.cmbDispatcher.setCurrentIndex(0)
        self.cmbPrimary.setCurrentIndex(0)
        self.setOrder(forceInt(QtGui.qApp.db.translate('EventType', 'id', eventTypeId, 'defaultOrder')))
        self.initGoal()
        self.setContract()
        self.setRecommendations(recommendationList)

        self.updateModelsRetiredList()

        self.cmbTypeAsset.setCurrentIndex(0)
        self.edtNextDate.setEnabled(False)
        self.edtNextTime.setEnabled(False)
        self.cmbCauseCall.setCurrentIndex(0)
        self.cmbPlaceReceptionCall.setCurrentIndex(0)
        self.cmbReceivedCall.setCurrentIndex(0)
        self.cmbReasondDelays.setCurrentIndex(0)
        self.cmbResultCircumstanceCall.setCurrentIndex(0)
        self.cmbAccident.setCurrentIndex(0)
        self.cmbDeath.setCurrentIndex(0)
        self.cmbEbriety.setCurrentIndex(0)
        self.cmbDiseased.setCurrentIndex(0)
        self.cmbPlaceCall.setCurrentIndex(0)
        self.cmbMethodTransportation.setCurrentIndex(0)
        self.cmbTransferredTransportation.setCurrentIndex(0)

        self.tabNotes.setNotesEx(externalId, assistantId, curatorId, relegateOrgId, referrals = {})

        visitTypeId = presetDiagnostics[0][4] if presetDiagnostics else None
        self.modelPersonnel.setDefaultVisitTypeId(visitTypeId)
        prepPersonnelBrigade(brigadeId)

        if presetDiagnostics:
            for model in [self.modelFinalDiagnostics]:
                for MKB, dispanserId, healthGroupId, medicalGroupId, visitTypeId, goalId, serviceId in presetDiagnostics:
                    item = model.getEmptyRecord()
                    item.setValue('MKB', toVariant(MKB))
                    item.setValue('dispanser_id',   toVariant(dispanserId))
                    item.setValue('healthGroup_id', toVariant(healthGroupId))
                    model.items().append(item)
                model.reset()
            self.cmbGoal.setValue(presetDiagnostics[0][5])
        self.prepareActions(presetActions, disabledActions, actionTypeIdValue, valueProperties)
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

        self.cmbAddressStreet.setCity(QtGui.qApp.defaultKLADR())
        plannerDate = self.getPlannerDate(eventSetDatetime, eventDatetime)
        if QtGui.qApp.userHasRight(urAccessF110planner):
            dlg = CPreF110Dialog(self, self.contractTariffCache)
            dlg.prepare(clientId, eventTypeId, plannerDate, self.personId, self.personSpecialityId,
                        self.personTariffCategoryId, flagHospitalization, actionTypeIdValue, tissueTypeId,
                        recommendationList, useDiagnosticsAndActionsPresets=useDiagnosticsAndActionsPresets)
            if dlg.diagnosticsTableIsNotEmpty() or dlg.actionsTableIsNotEmpty():
                if not dlg.exec_():
                    return False
            return self._prepare(None, clientId, eventTypeId, orgId, personId, eventSetDatetime, eventDatetime, includeRedDays, numDays, dlg.diagnostics(), dlg.actions(), dlg.disabledActionTypeIdList, externalId, assistantId, curatorId, actionTypeIdValue, valueProperties, relegateOrgId, referrals=referrals, isAmb=isAmb, recommendationList=recommendationList)
        else:
            presets = CPreF110DagnosticAndActionPresets(clientId, eventTypeId, plannerDate, self.personSpecialityId,
                                                        flagHospitalization, actionTypeIdValue, recommendationList,
                                                        useDiagnosticsAndActionsPresets=useDiagnosticsAndActionsPresets)
            return self._prepare(None, clientId, eventTypeId, orgId, personId, eventSetDatetime, eventDatetime, includeRedDays, numDays,
                                 presets.unconditionalDiagnosticList, presets.unconditionalActionList, presets.disabledActionTypeIdList,
                                 externalId, assistantId, curatorId, None, [], relegateOrgId, referrals=referrals, isAmb=isAmb, recommendationList=recommendationList)


    def prepareActions(self, presetActions, disabledActions, actionTypeIdValue, valueProperties):
        def addActionType(actionTypeId, amount, idListActionType, org_id):
            for model in [self.tabStatus.modelAPActions,
                          self.tabDiagnostic.modelAPActions,
                          self.tabCure.modelAPActions,
                          self.tabMisc.modelAPActions]:
                if actionTypeId in model.actionTypeIdList:
                    model.addRow(actionTypeId, amount)
                    record = model.items()[-1][0]
                    record.setValue('org_id', toVariant(org_id))
                    if actionTypeId in idListActionType:
                        action = model.items()[-1][1]
                        if valueProperties and len(valueProperties) > 0 and valueProperties[0]:
                            action[u'Направлен в отделение'] = valueProperties[0]
                    break

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
            idListActionType = db.getIdList(tableActionType, [tableActionType['id']], [tableActionType['flatCode'].like(u'received%'), tableActionType['deleted'].eq(0)])
            for actionTypeId, amount, cash, org_id in presetActions:
                addActionType(actionTypeId, amount, idListActionType, org_id)


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
                if orgStructureLeaved and u'Отделение' in action._actionType._propertiesByName:
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
        if len(self.edtNumberCardCall.text()) == 0:
            self.edtNumberCardCall.setFocus(QtCore.Qt.OtherFocusReason)
        else:
            self.tblFinalDiagnostics.setFocus(QtCore.Qt.OtherFocusReason)


    def setRecord(self, record):
        self.cmbResult.setTable('rbResult', True)
        CEventEditDialog.setRecord(self, record)
        setDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'setDate')
        setDatetimeEditValue(self.edtNextDate, self.edtNextTime, record, 'nextEventDate')
        setRBComboBoxValue(self.cmbPerson,      record, 'setPerson_id')
        setRBComboBoxValue(self.cmbPerson,      record, 'execPerson_id')
        setRBComboBoxValue(self.cmbDispatcher,  record, 'curator_id')
        setRBComboBoxValue(self.cmbResult,      record, 'result_id')
        self.cmbPrimary.setCurrentIndex(forceInt(record.value('isPrimary')))
        self.setOrder(forceInt(record.value('order')))
        self.setExternalId(forceString(record.value('externalId')))
        setComboBoxValue(self.cmbTypeAsset,     record, 'typeAsset_id')
        if not self.cmbTypeAsset.value():
            self.edtNextDate.setEnabled(False)
            self.edtNextTime.setEnabled(False)
        self.setPersonId(self.cmbPerson.value())
        self.setContract()
        setRBComboBoxValue(self.cmbContract, record, 'contract_id')
        self.loadDiagnostics(self.modelFinalDiagnostics)
        self.updateResultFilter()
        self.loadPersonnel()
        self.grpTempInvalid.pickupTempInvalid()
        # self.grpAegrotat.pickupTempInvalid()
        self.grpDisability.pickupTempInvalid()
        self.grpVitalRestriction.pickupTempInvalid()
        self.loadActions()
        self.tabCash.load(self.itemId())
        self.tabNotes.setNotes(record)
        self.tabNotes.updateReferralPeriod(self.edtBegDate.date())
        self.initFocus()
        self.setIsDirty(False)
        self.loadEmergencyCall(forceRef(record.value('id')))
        self.cmbNumberBrigade.setEnabled(False)
        self.initFocus()
        self.blankMovingIdList = []
        self.tabNotes.setEventEditor(self)
        self.setEditable(self.getEditable())
        self.tabMes.setRecord(record)
        setOrgStructureIdToCmbPerson(self.cmbPerson)

    def setEditable(self, editable):
        self.tabStatus.setEditable(editable)
        self.tabDiagnostic.setEditable(editable)
        self.tabCure.setEditable(editable)
        self.tabMisc.setEditable(editable)
        self.tabCash.setEditable(editable)
        self.tabNotes.setEditable(editable)
        self.tabTempInvalid.setEnabled(editable)
        self.tabTempInvalidS.setEnabled(editable)
        self.tabTempinvalidDisability.setEnabled(editable)
        # self.tabAegrotat.setEnabled(editable)

        self.grpBase.setEnabled(editable)
        self.grpActions.setEnabled(editable)
        self.grpRenunOfHospital.setEnabled(editable)
        self.grpDisability.setEnabled(editable)
        self.grpVitalRestriction.setEnabled(editable)

        self.modelPersonnel.setEditable(editable)
        self.modelFinalDiagnostics.setEditable(editable)

    def setRecordEmergencyCall(self, record):
        self.EmergencyCallEditDialog.setRecord(record)
        setDatetimeEditValue(self.edtEndDate, self.edtEndTime, record, 'endDate')
        setDatetimeEditValue(self.edtPassDate, self.edtPassTime, record, 'passDate')
        setDatetimeEditValue(self.edtDepartureDate, self.edtDepartureTime, record, 'departureDate')
        setDatetimeEditValue(self.edtArrivalDate, self.edtArrivalTime, record, 'arrivalDate')
        setDatetimeEditValue(self.edtFinishServiceDate, self.edtFinishServiceTime, record, 'finishServiceDate')
        setLineEditValue(self.edtWhoCallOnPhone, record, 'whoCallOnPhone')
        setLineEditValue(self.edtNumberPhone, record, 'numberPhone')
        setLineEditValue(self.edtNumberCardCall, record, 'numberCardCall')
        setLineEditValue(self.edtFaceRenunOfHospital, record, 'faceRenunOfHospital')
        self.grpRenunOfHospital.setChecked(forceInt(record.value('renunOfHospital')))
        self.chkDisease.setChecked(forceInt(record.value('disease')))
        self.chkBirth.setChecked(forceInt(record.value('birth')))
        self.chkPregnancyFailure.setChecked(forceInt(record.value('pregnancyFailure')))
        setRBComboBoxValue(self.cmbNumberBrigade,             record, 'brigade_id')
        self.cmbNumberBrigade.setEnabled(False)
        setRBComboBoxValue(self.cmbCauseCall,                 record, 'causeCall_id')
        setRBComboBoxValue(self.cmbPlaceReceptionCall,        record, 'placeReceptionCall_id')
        setRBComboBoxValue(self.cmbReceivedCall,              record, 'receivedCall_id')
        setRBComboBoxValue(self.cmbReasondDelays,             record, 'reasondDelays_id')
        setRBComboBoxValue(self.cmbResultCircumstanceCall,    record, 'resultCall_id')
        setRBComboBoxValue(self.cmbAccident,                  record, 'accident_id')
        setRBComboBoxValue(self.cmbDeath,                     record, 'death_id')
        setRBComboBoxValue(self.cmbEbriety,                   record, 'ebriety_id')
        setRBComboBoxValue(self.cmbDiseased,                  record, 'diseased_id')
        setRBComboBoxValue(self.cmbPlaceCall,                 record, 'placeCall_id')
        setRBComboBoxValue(self.cmbMethodTransportation,      record, 'methodTransport_id')
        setRBComboBoxValue(self.cmbTransferredTransportation, record, 'transfTransport_id')
        
        self.cmbAddressStreet.setCity(forceString(record.value('KLADRStreetCode'))[:13])
        self.cmbAddressStreet.setCode(forceString(record.value('KLADRStreetCode')))
        self.chkKLADR.setChecked(bool(self.cmbAddressStreet.code()))
        setLineEditValue(self.edtAddressHouse, record, 'house')
        setLineEditValue(self.edtAddressCorpus, record, 'build')
        setLineEditValue(self.edtAddressFlat, record, 'flat')
        setLineEditValue(self.edtAddressFreeInput, record, 'address_freeInput')
        
        self.calculationTimeTo()


    def loadEmergencyCall(self, eventId):
        db = QtGui.qApp.db
        table = db.table('EmergencyCall')
        record = db.getRecordEx(table, '*', table['event_id'].eq(eventId))
        if record:
            self.setRecordEmergencyCall(record)


    def loadPersonnel(self):
        self.modelPersonnel.loadItems(self.itemId())


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
        self.tabDiagnostic.loadActions(eventId)
        self.tabCure.loadActions(eventId)
        self.tabMisc.loadActions(eventId)
        self.modelActionsSummary.regenerate()
        self.tabCash.modelAccActions.regenerate()


    def getRecord(self):
        record = CEventEditDialog.getRecord(self)
        showTime = getEventShowTime(self.eventTypeId)
#перенести в exec_ в случае успеха или в accept?

        getRBComboBoxValue(self.cmbContract,    record, 'contract_id')
        getDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'setDate', showTime)
        getDatetimeEditValue(self.edtNextDate, self.edtNextTime, record, 'nextEventDate', showTime)
        getRBComboBoxValue(self.cmbPerson,      record, 'setPerson_id')
        getDatetimeEditValue(self.edtFinishServiceDate, self.edtFinishServiceTime, record, 'execDate', showTime)
        getRBComboBoxValue(self.cmbPerson,      record, 'execPerson_id')
        getRBComboBoxValue(self.cmbDispatcher,  record, 'curator_id')
        getRBComboBoxValue(self.cmbResult,      record, 'result_id')
        record.setValue('isPrimary', toVariant(self.cmbPrimary.currentIndex()))
        record.setValue('order', self.order())
        typeAssetId = self.cmbTypeAsset.currentIndex()
        record.setValue('typeAsset_id', toVariant(typeAssetId if typeAssetId != 0 else None))
###  payStatus
        self.tabNotes.getNotes(record, self.eventTypeId)
        return record


    def saveInternals(self, eventId):
        super(CF110Dialog, self).saveInternals(eventId)
        self.savePersonnel(eventId)
        self.saveDiagnostics(self.modelFinalDiagnostics, eventId)
        setAskedClassValueForDiagnosisManualSwitch(None)
        self.grpTempInvalid.saveTempInvalid()
        # self.grpAegrotat.saveTempInvalid()
        self.grpDisability.saveTempInvalid()
        self.grpVitalRestriction.saveTempInvalid()
        self.saveActions(eventId)
        self.getRecordEmergencyCall(eventId)
        self.tabCash.save(eventId)
        # self.tabNotes.saveOutgoingRef(eventId)
        self.saveBlankUsers(self.blankMovingIdList)
        self.updateRecommendations()

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        contractId = self.cmbContract.value()
        self.cmbContract.setBegDate(date)
        self.cmbContract.setEndDate(date)
        self.cmbContract.setValue(contractId)
        self.cmbPerson.setEndDate(date)
        self.tabStatus.setEndDate(date)
        self.tabDiagnostic.setEndDate(date)
        self.tabCure.setEndDate(date)
        self.tabMisc.setEndDate(date)
        self.tabNotes.updateReferralPeriod(date)
        self.emitUpdateActionsAmount()
        self.calculationTimeTo()
        self.updateResultFilter()
        if QtGui.qApp.isCheckMKB():
            self.updateMKB()
        self.setContract()

        self.updateModelsRetiredList()

        self.tabMes.setBegDate(date)

    @QtCore.pyqtSlot(QtCore.QTime)
    def on_edtBegTime_timeChanged(self, time):
        self.emitUpdateActionsAmount()
        self.calculationTimeTo()

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtPassDate_dateChanged(self, date):
        self.calculationTimeTo()

    @QtCore.pyqtSlot(QtCore.QTime)
    def on_edtPassTime_timeChanged(self, time):
        self.calculationTimeTo()

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtDepartureDate_dateChanged(self, date):
        self.calculationTimeTo()

    @QtCore.pyqtSlot(QtCore.QTime)
    def on_edtDepartureTime_timeChanged(self, time):
        self.calculationTimeTo()

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtArrivalDate_dateChanged(self, date):
        self.calculationTimeTo()

    @QtCore.pyqtSlot(QtCore.QTime)
    def on_edtArrivalTime_timeChanged(self, time):
        self.calculationTimeTo()

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtFinishServiceDate_dateChanged(self, date):
        self.emitUpdateActionsAmount()
        self.calculationTimeTo()

    @QtCore.pyqtSlot(QtCore.QTime)
    def on_edtFinishServiceTime_timeChanged(self, time):
        self.emitUpdateActionsAmount()
        self.calculationTimeTo()

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtEndDate_dateChanged(self, date):
        self.calculationTimeTo()
        self.setContract()

        self.tabMes.setEndDate(date)
        self.tabNotes.cmbClientPolicy.updatePolicy(date)
        if QtGui.qApp.isAutoClosed():
            self.chkIsClosed.setChecked(date != QtCore.QDate())

    @QtCore.pyqtSlot(QtCore.QTime)
    def on_edtEndTime_timeChanged(self, time):
        self.calculationTimeTo()

    @QtCore.pyqtSlot(bool)
    def on_chkKLADR_toggled(self, checked):
        self.edtAddressFreeInput.setEnabled(not checked)
        self.cmbAddressStreet.setEnabled(checked)

    def calculationTimeTo(self):
        begDateTime = QtCore.QDateTime()
        passDateTime = QtCore.QDateTime()
        departureDateTime = QtCore.QDateTime()
        arrivalDateTime = QtCore.QDateTime()
        finishServiceDateTime = QtCore.QDateTime()
        endDateTime = QtCore.QDateTime()
        begDateTime.setDate(self.edtBegDate.date())
        begDateTime.setTime(self.edtBegTime.time())
        passDateTime.setDate(self.edtPassDate.date())
        passDateTime.setTime(self.edtPassTime.time())
        departureDateTime.setDate(self.edtDepartureDate.date())
        departureDateTime.setTime(self.edtDepartureTime.time())
        arrivalDateTime.setDate(self.edtArrivalDate.date())
        arrivalDateTime.setTime(self.edtArrivalTime.time())
        finishServiceDateTime.setDate(self.edtFinishServiceDate.date())
        finishServiceDateTime.setTime(self.edtFinishServiceTime.time())
        endDateTime.setDate(self.edtEndDate.date())
        endDateTime.setTime(self.edtEndTime.time())
        if endDateTime.date() and begDateTime <= endDateTime:
            self.lblVisitsDurationValue.setText(self.disassembleSeconds(begDateTime.secsTo(endDateTime)))
        elif begDateTime <= finishServiceDateTime and not endDateTime.date():
                self.lblVisitsDurationValue.setText(self.disassembleSeconds(begDateTime.secsTo(finishServiceDateTime)))
        else:
            self.lblVisitsDurationValue.setText(u'--:--')
        if begDateTime <= passDateTime:
            self.lblTimeToPassDate.setText(self.disassembleSeconds(begDateTime.secsTo(passDateTime)))
        else:
            self.lblTimeToPassDate.setText(u'--:--')
        if  passDateTime <= departureDateTime:
            self.lblTimeToDepartureDate.setText(self.disassembleSeconds(passDateTime.secsTo(departureDateTime)))
        else:
            self.lblTimeToDepartureDate.setText(u'--:--')
        if departureDateTime <= arrivalDateTime:
            self.lblTimeToArrivalDate.setText(self.disassembleSeconds(departureDateTime.secsTo(arrivalDateTime)))
        else:
            self.lblTimeToArrivalDate.setText(u'--:--')
        if arrivalDateTime <= finishServiceDateTime:
            self.lblTimeToFinishServiceDate.setText(self.disassembleSeconds(arrivalDateTime.secsTo(finishServiceDateTime)))
        else:
            self.lblTimeToFinishServiceDate.setText(u'--:--')
        if endDateTime.date() and finishServiceDateTime.date() and finishServiceDateTime <= endDateTime:
            self.lblTimeToEndDate.setText(self.disassembleSeconds(finishServiceDateTime.secsTo(endDateTime)))
        else:
            self.lblTimeToEndDate.setText(u'--:--')

    def disassembleSeconds(self, timeToDateTimeSecs):
        string = u''
        timeToDays = int(timeToDateTimeSecs / 86400)
        timeToHour = int(timeToDateTimeSecs / 3600)
        timeToMinute = int(timeToDateTimeSecs / 60)
        timeToHour = timeToHour - (24 * timeToDays)
        if timeToHour > 0:
            if timeToHour > 9:
                string += u'%d' % (timeToHour)
            else:
                string += u'0%d' % (timeToHour)
        else:
            timeToHour = 0
            string += u'00'
        timeToMinute = timeToMinute - (60 * timeToHour) - (1440 * timeToDays)
        timeToSec = timeToDateTimeSecs - ( 60 * timeToMinute) - (3600 * timeToHour) - (86400 * timeToDays)
        if timeToSec > 29:
            timeToMinute += 1
        if timeToMinute > 0:
            if timeToMinute > 9:
                string += u':%d  ' % (timeToMinute)
            else:
                string += u':0%d  ' % (timeToMinute)
        else:
            string += u':00  '

        if timeToDays > 0:
            string += formatNum(timeToDays, (u'день', u'дня', u'дней'))
        return string

    def getRecordEmergencyCall(self, eventId):
        showTime = True
        record = self.EmergencyCallEditDialog.getRecord()
        record.setValue('event_id', toVariant(eventId))
        record.setValue('pregnancyFailure', toVariant(self.chkPregnancyFailure.isChecked()))
        record.setValue('birth', toVariant(self.chkBirth.isChecked()))
        record.setValue('disease', toVariant(self.chkDisease.isChecked()))
        record.setValue('renunOfHospital', toVariant(self.grpRenunOfHospital.isChecked()))
        getLineEditValue(self.edtWhoCallOnPhone, record, 'whoCallOnPhone')
        getLineEditValue(self.edtNumberPhone, record, 'numberPhone')
        getLineEditValue(self.edtNumberCardCall, record, 'numberCardCall')
        getLineEditValue(self.edtFaceRenunOfHospital, record, 'faceRenunOfHospital')
        getDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'begDate', showTime)
        getDatetimeEditValue(self.edtPassDate, self.edtPassTime, record, 'passDate', showTime)
        getDatetimeEditValue(self.edtDepartureDate, self.edtDepartureTime, record, 'departureDate', showTime)
        getDatetimeEditValue(self.edtArrivalDate, self.edtArrivalTime, record, 'arrivalDate', showTime)
        getDatetimeEditValue(self.edtEndDate, self.edtEndTime, record, 'endDate', showTime)
        getDatetimeEditValue(self.edtFinishServiceDate, self.edtFinishServiceTime, record, 'finishServiceDate', showTime)
        getRBComboBoxValue(self.cmbNumberBrigade,    record, 'brigade_id')
        getRBComboBoxValue(self.cmbDiseased,    record, 'diseased_id')
        getRBComboBoxValue(self.cmbPlaceCall,    record, 'placeCall_id')
        getRBComboBoxValue(self.cmbMethodTransportation,    record, 'methodTransport_id')
        getRBComboBoxValue(self.cmbTransferredTransportation,    record, 'transfTransport_id')
        getRBComboBoxValue(self.cmbCauseCall,    record, 'causeCall_id')
        getRBComboBoxValue(self.cmbPlaceReceptionCall,    record, 'placeReceptionCall_id')
        getRBComboBoxValue(self.cmbReceivedCall,    record, 'receivedCall_id')
        getRBComboBoxValue(self.cmbReasondDelays,    record, 'reasondDelays_id')
        getRBComboBoxValue(self.cmbResultCircumstanceCall,    record, 'resultCall_id')
        getRBComboBoxValue(self.cmbAccident,    record, 'accident_id')
        getRBComboBoxValue(self.cmbDeath,    record, 'death_id')
        getRBComboBoxValue(self.cmbEbriety,    record, 'ebriety_id')
        
        if self.chkKLADR.isChecked():
            record.setValue('KLADRStreetCode', toVariant(self.cmbAddressStreet.code()))
            record.setValue('address_freeInput', toVariant(None))
        else:
            getLineEditValue(self.edtAddressFreeInput, record, 'address_freeInput')
            record.setValue('KLADRStreetCode', toVariant(None))
        
        getLineEditValue(self.edtAddressHouse, record, 'house')
        getLineEditValue(self.edtAddressCorpus, record, 'build')
        getLineEditValue(self.edtAddressFlat, record, 'flat')
        
        self.EmergencyCallEditDialog.saveEmergencyCall()

    def savePersonnel(self, eventId):
        items = self.modelPersonnel.items()
        itemVisit = self.itemVisitPersonnelModel()
        sceneId = itemVisit[0]
        dateVisit = itemVisit[1]
        visitTypeId = itemVisit[2] #FIXME: добавить проверку на наличие visitTypeId, иначе все падает на попытке записать в базу визит без типа.
        financeId = itemVisit[3]
        for item in items :
            item.setValue('visitType_id', toVariant(forceRef(visitTypeId)))
            item.setValue('isPrimary', toVariant(self.cmbPrimary.currentIndex()))
            item.setValue('date', toVariant(dateVisit))
            item.setValue('scene_id', toVariant(sceneId))
            item.setValue('finance_id', toVariant(financeId))
            if forceRef(item.value('person_id')) == self.personId and self.personServiceId:
                item.setValue('service_id', self.personServiceId)
        self.modelPersonnel.saveItems(eventId)

    def saveDiagnostics(self, modelDiagnostics, eventId):
        items = modelDiagnostics.items()
        isDiagnosisManualSwitch = modelDiagnostics.manualSwitchDiagnosis()

        begDate = self.edtBegDate.date()
        endDate = self.edtFinishServiceDate.date()
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
                None,
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
            MKBDiagnosisIdPairList.append((MKB, diagnosisId))
        modelDiagnostics.saveItems(eventId)
        self.modifyDiagnosises(MKBDiagnosisIdPairList)

    def getFinalDiagnosisMKB(self):
        diagnostics = self.modelDiagnostics.items() if hasattr(self, 'modelDiagnostics') else None
        if diagnostics:
            MKB   = forceString(diagnostics[0].value('MKB'))
            MKBEx = forceString(diagnostics[0].value('MKBEx'))
            return MKB, MKBEx
        else:
            return '', ''

    def getFinalDiagnosisId(self):
        diagnostics = self.modelFinalDiagnostics.items()
        return forceRef(diagnostics[0].value('diagnosis_id')) if diagnostics else None

    def getModelFinalDiagnostics(self):
        return self.modelFinalDiagnostics

    def saveActions(self, eventId):
        self.tabStatus.saveActions(eventId)
        self.tabDiagnostic.saveActions(eventId)
        self.tabCure.saveActions(eventId)
        self.tabMisc.saveActions(eventId)

    def setOrgId(self, orgId):
        self.orgId = orgId
        self.cmbContract.setOrgId(orgId)
        self.cmbPerson.setOrgId(orgId)
        self.tabStatus.setOrgId(orgId)
        self.tabDiagnostic.setOrgId(orgId)
        self.tabCure.setOrgId(orgId)
        self.tabMisc.setOrgId(orgId)

    def setExternalId(self, externalId):
        self.lblValueExternalId.setText((u'Внешний идентификатор: ' + externalId) if externalId else '')

    def setEventTypeId(self, eventTypeId):
        CEventEditDialog.setEventTypeId(self, eventTypeId, u'Ф.110')
        self.tabCash.windowTitle = self.windowTitle()
        self.cmbNumberBrigade.setTable('EmergencyBrigade', addNone=False, order='code')
        self.cmbCauseCall.setTable('rbEmergencyCauseCall', order='code')
        self.cmbTypeAsset.setTable('rbEmergencyTypeAsset', order='code')
        self.cmbPlaceReceptionCall.setTable('rbEmergencyPlaceReceptionCall', addNone=False, order='code')
        self.cmbReceivedCall.setTable('rbEmergencyReceivedCall', addNone=False, order='code')
        self.cmbReasondDelays.setTable('rbEmergencyReasondDelays', order='code')
        self.cmbResultCircumstanceCall.setTable('rbEmergencyResult', addNone=False, order='code')
        self.cmbAccident.setTable('rbEmergencyAccident', order='code')
        self.cmbDeath.setTable('rbEmergencyDeath', order='code')
        self.cmbEbriety.setTable('rbEmergencyEbriety', order='code')
        self.cmbDiseased.setTable('rbEmergencyDiseased', addNone=False, order='code')
        self.cmbPlaceCall.setTable('rbEmergencyPlaceCall', addNone=False, order='code')
        self.cmbMethodTransportation.setTable('rbEmergencyMethodTransportation', order='code')
        self.cmbTransferredTransportation.setTable('rbEmergencyTransferredTransportation', order='code')
        showTime = getEventShowTime(eventTypeId)
        self.edtBegTime.setVisible(showTime)
        self.edtPassTime.setVisible(showTime)
        self.edtDepartureTime.setVisible(showTime)
        self.edtArrivalTime.setVisible(showTime)
        self.edtFinishServiceTime.setVisible(showTime)
        self.edtEndTime.setVisible(showTime)
        if self.cmbResult.value() is None:
            if self.inheritResult == True:
                self.cmbResult.setValue(self.defaultEventResultId.get(self.eventPurposeId))
        self.updateResultFilter()
        customizePrintButton(self.btnPrint, self.eventContext if self.eventContext else 'F110')
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

    def checkDataEntered(self):
        result = CEventEditDialog.checkDataEntered(self)
        self.blankMovingIdList = []
        begDate = self.edtBegDate.date()
        endDate = self.edtEndDate.date() if self._isClosedEventCheck else QtCore.QDate()
        passDate = self.edtPassDate.date()
        departureDate = self.edtDepartureDate.date()
        arrivalDate = self.edtArrivalDate.date()
        finishServiceDate = self.edtFinishServiceDate.date()
        nextDate = self.edtNextDate.date()

        result = result and (not finishServiceDate.isNull() or self.checkInputMessage(u'Дату оконч. обслуж.', False, self.edtFinishServiceDate))
        result = result and (self.orgId != QtGui.qApp.currentOrgId() or self.cmbContract.value() or self.checkInputMessage(u'договор', False, self.cmbContract))
        result = result and (self.cmbPerson.value()   or self.checkInputMessage(u'ответственного врача', False, self.cmbPerson))
        result = result and (self.cmbDispatcher.value()   or self.checkInputMessage(u'диспетчера', False, self.cmbDispatcher))
        result = result and (not begDate.isNull() or self.checkInputMessage(u'Дату приема вызова', False, self.edtBegDate))
        result = result and (not passDate.isNull() or self.checkInputMessage(u'Дату передачи бригаде', False, self.edtPassDate))
        result = result and (not departureDate.isNull() or self.checkInputMessage(u'Дату выезда', False, self.edtDepartureDate))
        result = result and (not arrivalDate.isNull() or self.checkInputMessage(u'Дату прибытия', False, self.edtArrivalDate))
        result = result and (not endDate.isNull() or self.checkInputMessage(u'Дату возвращения на станцию', True, self.edtEndDate))
        result = result and (self.cmbPlaceReceptionCall.value() or self.checkInputMessage(u'место получения вызова', False, self.cmbPlaceReceptionCall))

        if self.cmbTypeAsset.value():
            result = result and (not nextDate.isNull() or self.checkInputMessage(u'Дату активного посещения', True, self.edtNextDate))
        result = result and self.checkEmergencyCallDate()
        if finishServiceDate.isNull():
            pass
        else:
            result = result and self.checkActionDataEntered(begDate, QtCore.QDate(), finishServiceDate, self.tabToken, self.edtBegDate, None, self.edtFinishServiceDate)
            result = result and self.checkEventDate(begDate, finishServiceDate, None, self.tabToken, None, self.edtFinishServiceDate, True)
            minDuration,  maxDuration = getEventDuration(self.eventTypeId)
            if minDuration<=maxDuration:
                countRedDays = not QtGui.qApp.isExcludeRedDaysInEventLength()
                eventDuration = getEventLengthDays(begDate, endDate, countRedDays, self.eventTypeId)
                eventDurationErrorString = u'Указана длительность с учётом выходных: %s.'%formatNum(eventDuration, (u'день', u'дня', u'дней'))
                result = result and (eventDuration >= minDuration or
                                     self.checkValueMessage(u'Длительность должна быть не менее %s. %s'%(formatNum(minDuration, (u'дня', u'дней', u'дней')), eventDurationErrorString), False, self.edtFinishServiceDate))
                result = result and (maxDuration==0 or eventDuration <= maxDuration or
                                     self.checkValueMessage(u'Длительность должна быть не более %s. %s'%(formatNum(maxDuration, (u'дня', u'дней', u'дней')), eventDurationErrorString), False, self.edtFinishServiceDate))
            # if not QtGui.qApp.userHasRight(urDoNotCheckResultAndMKB):
            #    result = result and (self.cmbResult.value()  or self.checkInputMessage(u'результат',   False, self.cmbResult))
        result = result and self.checkDiagnosticsDataEntered([(self.tblFinalDiagnostics, False, True, self.edtFinishServiceDate.date())],
                                                             endDate)
        result = result and self.checkActionsDateEnteredActuality(begDate, finishServiceDate, [self.tabStatus, self.tabDiagnostic, self.tabCure, self.tabMisc])
        result = result and self.checkActionsDataEntered([self.tabStatus, self.tabDiagnostic, self.tabCure, self.tabMisc], begDate, finishServiceDate)
        result = result and (len(self.modelPersonnel.items())>0 or self.checkInputMessage(u'состав бригады', False, self.tblPersonnel))
        result = result and self.grpTempInvalid.checkTempInvalidDataEntered()
        # result = result and self.grpAegrotat.checkTempInvalidDataEntered()
        result = result and self.grpDisability.checkTempInvalidDataEntered()
        result = result and self.grpVitalRestriction.checkTempInvalidDataEntered()
        result = result and (((not self.grpRenunOfHospital.isChecked()) or (self.grpRenunOfHospital.isChecked() and len(self.edtFaceRenunOfHospital.text()) > 0)) or  self.checkInputMessage(u'Лицо отказа от госпитализации', False, self.edtFaceRenunOfHospital))
        result = result and ((len(self.edtNumberCardCall.text()) > 0) or  self.checkInputMessage(u'Карта вызова №', True, self.edtNumberCardCall))
        if self.cmbNumberBrigade.isEnabled():
            result = result and (self.cmbNumberBrigade.value() or  self.checkInputMessage(u'Номер бригады', False, self.cmbNumberBrigade))
        result = result and (self.cmbCauseCall.value() or  self.checkInputMessage(u'Повод к вызову', True, self.cmbCauseCall))
        result = result and ((len(self.edtWhoCallOnPhone.text()) > 0) or  self.checkInputMessage(u'Кто вызывал', True, self.edtWhoCallOnPhone))
        result = result and ((len(self.edtNumberPhone.text()) > 0) or  self.checkInputMessage(u'С какого телефона', True, self.edtNumberPhone))
        result = result and (self.cmbPrimary.currentIndex()>0 or  self.checkInputMessage(u'Вызов', False, self.cmbPrimary))
        result = result and (self.order()>0 or  self.checkInputMessage(u'Порядок', False, self.cmbOrder))
        result = result and self.tabCash.checkDataLocalContract()
        result = result and self.checkSerialNumberEntered()
        result = result and self.checkTabNotesReferral()

        if \
                self.getFinalDiagnosisMKB()[0] is not None and self.getFinalDiagnosisMKB()[0] != u'' and self.getFinalDiagnosisMKB()[0][0] == u'C' \
                and not QtGui.qApp.userHasRight(urOncoDiagnosisWithoutTNMS)\
                and QtGui.qApp.isTNMSVisible() and (self.modelDiagnostics.items()[0].value('TNMS') is None or
                                forceString(self.modelDiagnostics.items()[0].value('TNMS')) == ''):
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

    def checkEmergencyCallDate(self):
        begDate = self.edtBegDate.date()
        endDate = self.edtEndDate.date() if self._isClosedEventCheck else QtCore.QDate()
        passDate = self.edtPassDate.date()
        departureDate = self.edtDepartureDate.date()
        arrivalDate = self.edtArrivalDate.date()
        finishServiceDate = self.edtFinishServiceDate.date()
        begTime = self.edtBegTime.time()
        endTime = self.edtEndTime.time()
        passTime = self.edtPassTime.time()
        departureTime = self.edtDepartureTime.time()
        arrivalTime = self.edtArrivalTime.time()
        finishServiceTime = self.edtFinishServiceTime.time()
        nextDate = self.edtNextDate.date()
        nextTime = self.edtNextTime.time()

        result = True
        if endDate and begDate:
            result = result and (begDate <= endDate or self.checkValueMessage(u'Датa приема вызова %s не может быть позже даты возвр. на станц. %s'% (forceString(begDate), forceString(endDate)), False, self.edtBegDate))
        elif begDate and finishServiceDate:
            result = result and (begDate <= finishServiceDate or self.checkValueMessage(u'Датa приема вызова %s не может быть позже даты оконч. обслуж. %s'% (forceString(begDate), forceString(finishServiceDate)), False, self.edtBegDate))
        result = result and ((begDate <= passDate) or self.checkValueMessage(u'Датa приема вызова %s не может быть позже даты передачи вызова бригаде %s'% (forceString(begDate), forceString(passDate)), False, self.edtBegDate))
        if begDate == passDate:
            result = result and ((begTime <= passTime) or self.checkValueMessage(u'Время приема вызова %s не может быть позже времени передачи вызова бригаде %s'% (begTime.toString('hh:mm'), passTime.toString('hh:mm')), False, self.edtBegTime))
        result = result and ((passDate <= departureDate) or self.checkValueMessage(u'Дата передачи вызова бригаде %s не может быть позже даты выезда %s'% (forceString(passDate), forceString(departureDate)), False, self.edtPassDate))
        if passDate == departureDate:
            result = result and ((passTime <= departureTime) or self.checkValueMessage(u'Время передачи вызова бригаде %s не может быть позже времени выезда %s'% (passTime.toString('hh:mm'), departureTime.toString('hh:mm')), False, self.edtPassTime))
        result = result and ((departureDate <= arrivalDate) or self.checkValueMessage(u'Дата выезда %s не может быть позже даты прибытия %s'% (forceString(departureDate), forceString(arrivalDate)), False, self.edtDepartureDate))
        if departureDate == arrivalDate:
            result = result and ((departureTime <= arrivalTime) or self.checkValueMessage(u'Время выезда %s не может быть позже времени прибытия %s'% (departureTime.toString('hh:mm'), arrivalTime.toString('hh:mm')), False, self.edtDepartureTime))
        result = result and ((arrivalDate <= finishServiceDate) or self.checkValueMessage(u'Дата прибытия %s не может быть позже даты оконч. обслуж. %s'% (forceString(arrivalDate), forceString(finishServiceDate)), False, self.edtArrivalDate))
        if arrivalDate == finishServiceDate:
            result = result and ((arrivalTime <= finishServiceTime) or self.checkValueMessage(u'Время прибытия %s не может быть позже времени оконч. обслуж. %s'% (arrivalTime.toString('hh:mm'), finishServiceTime.toString('hh:mm')), False, self.edtArrivalTime))
        if self.cmbTypeAsset.value() and nextDate:
            result = result and ((finishServiceDate <= nextDate) or self.checkValueMessage(u'Дата активного посещения %s не может быть раньше даты оконч. обслуж. %s'% (forceString(nextDate), forceString(finishServiceDate)), False, self.edtNextDate))
            if nextDate == finishServiceDate:
                result = result and ((finishServiceTime <= nextTime) or self.checkValueMessage(u'Время активного посещения %s не может быть раньше времени оконч. обслуж. %s'% (nextTime.toString('hh:mm'), finishServiceTime.toString('hh:mm')), False, self.edtNextTime))
        if endDate:
            result = result and ((finishServiceDate <= endDate) or self.checkValueMessage(u'Дата оконч. обслуж. %s не может быть позже даты возвр. на станц. %s'% (forceString(finishServiceDate), forceString(endDate)), False, self.edtFinishServiceDate))
            if finishServiceDate == endDate:
                result = result and ((finishServiceTime <= endTime) or self.checkValueMessage(u'Время оконч. обслуж. %s не может быть позже времени возвр. на станц. %s'% (finishServiceTime.toString('hh:mm'), endTime.toString('hh:mm')), False, self.edtFinishServiceTime))
        return result

#
#    def checkDiagnosticsDataEntered(self, endDate):
#        if QtGui.qApp.userHasRight(urDoNotCheckResultAndMKB):
#            return True
#        
#        if endDate and len(self.modelFinalDiagnostics.items()) <= 0:
#            self.checkInputMessage(u'диагноз', False, self.tblFinalDiagnostics)
#            return False
#        
#        if endDate and not self.checkDiagnosticsType():
#            return False
#        
#        for row, record in enumerate(self.modelFinalDiagnostics.items()):
#            if not self.checkDiagnosticDataEntered(row, record):
#                return False
#        return True
#    
#
#
#    def checkDiagnosticsType(self):
#        result = True
#        endDate = self.edtFinishServiceDate.date()
#        if endDate:
#            result = result and self.checkDiagnosticsTypeEnd(self.modelFinalDiagnostics) or self.checkValueMessage(u'Необходимо указать основной диагноз', True, self.tblFinalDiagnostics)
#        return result
#
#
#    def checkDiagnosticsTypeEnd(self, model):
#        for record in model.items():
#            if  forceInt(record.value('diagnosisType_id')) == model.diagnosisTypeCol.ids[0]:
#                return True
#        return False
#
#
#    def checkDiagnosticDataEntered(self, row, record):
####     self.checkValueMessage(self, message, canSkip, widget, row=None, column=None):
#        result = True
#        if result:
#            MKB = forceString(record.value('MKB'))
#            result = MKB or self.checkInputMessage(u'диагноз', True, self.tblFinalDiagnostics, row, record.indexOf('MKB'))
#            if result:
#                char = MKB[:1]
#                traumaTypeId = forceRef(record.value('traumaType_id'))
#                if char in 'ST' and not traumaTypeId:
#                    result = self.checkValueMessage(u'Необходимо указать тип травмы', True, self.tblFinalDiagnostics, row, record.indexOf('traumaType_id'))
#                if char not in 'ST' and traumaTypeId:
#                    result = self.checkValueMessage(u'Необходимо удалить тип травмы', False, self.tblFinalDiagnostics, row, record.indexOf('traumaType_id'))
#        return result

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

    def getCuratorId(self):
        return self.cmbDispatcher.value()

    def getEventInfo(self, context):
        result = CEventEditDialog.getEventInfo(self, context, CEmergencyEventInfo)
        showTime = getEventShowTime(self.eventTypeId) if self.eventTypeId else True
        # ручная инициализация свойств
        result._isPrimary = forceInt(self.cmbPrimary.currentIndex())
        result._order = self.order()
        result._typeAsset = context.getInstance(CEmergencyTypeAssetInfo, self.cmbTypeAsset.value())
        recordEmergency = self.EmergencyCallEditDialog.record()
        result._numberCardCall = self.edtNumberCardCall.text()
        result._brigade = context.getInstance(CEmergencyBrigadeInfo, self.cmbNumberBrigade.value())
        result._causeCall = context.getInstance(CEmergencyCauseCallInfo, self.cmbCauseCall.value())
        result._whoCallOnPhone = self.edtWhoCallOnPhone.text()
        result._numberPhone = self.edtNumberPhone.text()
        if showTime:
            result._passDate = CDateTimeInfo(QtCore.QDateTime(self.edtPassDate.date(), self.edtPassTime.time()))
            result._departureDate = CDateTimeInfo(QtCore.QDateTime(self.edtDepartureDate.date(), self.edtDepartureTime.time()))
            result._arrivalDate = CDateTimeInfo(QtCore.QDateTime(self.edtArrivalDate.date(), self.edtArrivalTime.time()))
            result._finishServiceDate = CDateTimeInfo(QtCore.QDateTime(self.edtFinishServiceDate.date(), self.edtFinishServiceTime.time()))
        else:
            result._passDate = CDateInfo(self.edtPassDate.date())
            result._departureDate = CDateInfo(self.edtDepartureDate.date())
            result._arrivalDate = CDateInfo(self.edtArrivalDate.date())
            result._finishServiceDate = CDateInfo(self.edtFinishServiceDate.date())
        result._placeReceptionCall = context.getInstance(CEmergencyPlaceReceptionCallInfo, self.cmbPlaceReceptionCall.value())
        result._receivedCall = context.getInstance(CEmergencyReceivedCallInfo, self.cmbReceivedCall.value())
        result._reasondDelays = context.getInstance(CEmergencyReasondDelaysInfo, self.cmbReasondDelays.value())
        result._resultCall = context.getInstance(CEmergencyResultInfo, self.cmbResultCircumstanceCall.value())
        result._accident = context.getInstance(CEmergencyAccidentInfo, self.cmbAccident.value())
        result._death = context.getInstance(CEmergencyDeathInfo, self.cmbDeath.value())
        result._ebriety = context.getInstance(CEmergencyEbrietyInfo, self.cmbEbriety.value())
        result._diseased = context.getInstance(CEmergencyDiseasedInfo, self.cmbDiseased.value())
        result._placeCall = context.getInstance(CEmergencyPlaceCallInfo, self.cmbPlaceCall.value())
        result._methodTransport = context.getInstance(CEmergencyMethodTransportInfo, self.cmbMethodTransportation.value())
        result._transfTransport = context.getInstance(CEmergencyTransferTransportInfo, self.cmbTransferredTransportation.value())
        result._renunOfHospital = self.grpRenunOfHospital.isChecked()
        result._faceRenunOfHospital = self.edtFaceRenunOfHospital.text()
        result._disease = self.chkDisease.isChecked()
        result._birth = self.chkBirth.isChecked()
        result._pregnancyFailure = self.chkPregnancyFailure.isChecked()
        result._noteCall = forceString(recordEmergency.value('noteCall')) if recordEmergency else ''

        # ручная инициализация таблиц
        result._actions = CActionInfoProxyList(context,
                [self.tabStatus.modelAPActions, self.tabDiagnostic.modelAPActions, self.tabCure.modelAPActions, self.tabMisc.modelAPActions],
                result)
        result._diagnosises = CDiagnosticInfoProxyList(context, [self.modelFinalDiagnostics])
        result._visits = self.getVisitsPersonell(context)
        return result

    def itemVisitPersonnelModel(self):
        contractId = self.cmbContract.value()
        codeScene = 4
        db = QtGui.qApp.db
        keyVal = u'СМП'  #В справочнике для типа визитов должна быть строка с кодом "СМП",
        record = db.translate('rbVisitType', 'code', keyVal, 'id')
        if not record:
            keyVal = u'' #если ее нет, то берется тип с пустым кодом
            record = db.translate('rbVisitType', 'code', keyVal, 'id')
        visitTypeId = forceRef(record)
        dateVisit = QtCore.QDateTime()
        if self.edtFinishServiceDate.date().isValid():
            dateVisit.setDate(self.edtFinishServiceDate.date())
            if self.edtFinishServiceTime and self.edtFinishServiceTime.time():
                dateVisit.setTime(self.edtFinishServiceTime.time())
        elif self.edtArrivalDate.date().isValid():
            dateVisit.setDate(self.edtArrivalDate.date())
            if self.edtArrivalTime and self.edtArrivalTime.time():
                dateVisit.setTime(self.edtArrivalTime.time())
        sceneId = forceRef(db.translate('rbScene', 'code', codeScene, 'id'))
        financeId = forceRef(db.translate('Contract', 'id', contractId, 'finance_id')) #по договору(cmbContract)
        return [sceneId, dateVisit, visitTypeId, financeId]

    def getVisitsPersonell(self, context):
        visitItems = []
        items = self.modelPersonnel.items()
        itemVisit = self.itemVisitPersonnelModel()
        sceneId = itemVisit[0]
        dateVisit = itemVisit[1]
        visitTypeId = itemVisit[2]
        financeId = itemVisit[3]
        for item in items:
            visitItem = []
            visitItem.append(sceneId)
            visitItem.append(dateVisit)
            visitItem.append(visitTypeId)
            visitItem.append(forceRef(item.value('person_id')))
            visitItem.append(self.cmbPrimary.currentIndex())
            visitItem.append(financeId)
            visitItem.append(forceRef(item.value('service_id')))
            visitItem.append(forceInt(item.value('payStatus')))
            visitItems.append(visitItem)
        visits = [CVisitPersonallInfo(context, visitItem) for visitItem in visitItems]
        return visits

    def getTempInvalidInfo(self, context):
        return self.grpTempInvalid.getTempInvalidInfo(context)

    # def getAegrotatInfo(self, context):
    #     return self.grpAegrotat.getTempInvalidInfo(context)

    def updateMesDurationsMap(self, mesCmbIndex = None):
        mesId = self.getMesId()
        if mesId and not mesId in self.mesDurationsMap.keys():
            record = QtGui.qApp.db.getRecordEx('mes.MES', 'minDuration, maxDuration', 'id=%d' % forceRef(mesId))
            minDuration = forceInt(record.value('minDuration'))
            maxDuration = forceInt(record.value('maxDuration'))
            self.mesDurationsMap[mesId] = (minDuration, maxDuration)
            self.updateDuration()

    #TODO:skkachaev: Не вызывается никогда. Должно?
    def updateMesMKB(self):
        MKB = self.getFinalDiagnosisMKB()[0]
        self.tabMes.setMKB(MKB)
        MKB2List = self.getRelatedDiagnosisMKB()
        self.tabMes.setMKB2([r[0] for r in MKB2List])

    def initTabMes(self, show=True):
        if show: self.tabMes.setVisible(False)
        self.tabMes.postSetupUi()
        if show: self.tabMes.setVisible(True)

        self.isTabMesAlreadyLoad = True

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

    @QtCore.pyqtSlot(int)
    def on_cmbTypeAsset_currentIndexChanged(self):
        if self.cmbTypeAsset.value():
            self.edtNextDate.setEnabled(True)
            self.edtNextTime.setEnabled(True)
        else:
            self.edtNextDate.setEnabled(False)
            self.edtNextTime.setEnabled(False)

    def on_modelFinalDiagnostics_resultChanged(self):
        CEventEditDialog.defaultDiagnosticResultId[self.eventPurposeId] = self.modelFinalDiagnostics.resultId()
        self.updateResultFilter()
        # if self.cmbResult.value() is None:
        #     self.cmbResult.setValue(getEventResultId(CEventEditDialog.defaultDiagnosticResultId.get(self.eventPurposeId)))

    @QtCore.pyqtSlot()
    def on_actDiagnosticsAddAccomp_triggered(self):
        currentRow = self.tblFinalDiagnostics.currentIndex().row()
        if currentRow>=0 :
            currentRecord = self.modelFinalDiagnostics.items()[currentRow]
            newRecord = self.modelFinalDiagnostics.getEmptyRecord()
            newRecord.setValue('diagnosisType', QtCore.QVariant(CF110Dialog.dfAccomp))
            newRecord.setValue('speciality_id', currentRecord.value('speciality_id'))
            newRecord.setValue('healthGroup_id', currentRecord.value('healthGroup_id'))
            self.modelFinalDiagnostics.insertRecord(currentRow+1, newRecord)
            self.tblFinalDiagnostics.setCurrentIndex(self.modelFinalDiagnostics.index(currentRow+1, newRecord.indexOf('MKB')))

    @QtCore.pyqtSlot(int)
    def on_btnPrint_printByTemplate(self, templateId):
        if self.beforePrintTemplate(templateId) == -1:
            return
        context = CInfoContext()
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
    
    @QtCore.pyqtSlot()
    def on_btnLoadAddress_clicked(self):
        clientInfo = self.clientInfo
        if clientInfo and hasattr(clientInfo, 'locAddressInfo'):
            locAddressInfo = clientInfo.locAddressInfo
            self.cmbAddressStreet.setCity(locAddressInfo.KLADRStreetCode[:13])
            self.cmbAddressStreet.setCode(locAddressInfo.KLADRStreetCode)
            self.chkKLADR.setChecked(bool(self.cmbAddressStreet.code()))
            self.edtAddressFreeInput.setText(locAddressInfo.freeInput)
            self.edtAddressHouse.setText(locAddressInfo.number)
            self.edtAddressCorpus.setText(locAddressInfo.corpus)
            self.edtAddressFlat.setText(locAddressInfo.flat)


class CF110PersonnelModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'Visit', 'id', 'event_id', parent)
        self._parent = parent
        self.colPerson = self.addCol(CActionPersonInDocTableColSearch(u'ФИО', 'person_id', 20, 'vrbPersonWithSpeciality', order = 'name', parent=parent))
        self.addHiddenCol('visitType_id')
        self.addHiddenCol('date')
        self.addHiddenCol('isPrimary')
        self.addHiddenCol('scene_id')
        self.addHiddenCol('payStatus')
        self.addHiddenCol('finance_id')
        self.addHiddenCol('service_id')
        self.defaultVisitTypeId = None
        self.tryFindDefaultVisitTypeId = True

    def loadItems(self, eventId):
        CInDocTableModel.loadItems(self, eventId)
        if self.items():
            lastItem = self.items()[-1]
            if self.defaultVisitTypeId is None:
                self.defaultVisitTypeId = forceRef(lastItem.value('visitType_id'))

    def getEmptyRecord(self, personId=None):
        result = CInDocTableModel.getEmptyRecord(self)
        result.setValue('person_id', toVariant(personId if personId else QtCore.QObject.parent(self).getSuggestedPersonId()))
        return result

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        column = index.column()
        if not variantEq(self.data(index, role), value):
            if column in [0] : # врач
                result = CInDocTableModel.setData(self, index, value, role)
                return result
            else:
                return CInDocTableModel.setData(self, index, value, role)
        else:
            return True

    def setDefaultVisitTypeId(self, visitTypeId):
        self.defaultVisitTypeId = visitTypeId
        if visitTypeId is None:
            self.tryFindDefaultVisitTypeId = True

    def getDefaultVisitTypeId(self):
        if self.defaultVisitTypeId is None:
            if self.tryFindDefaultVisitTypeId:
                self.defaultVisitTypeId = forceRef(QtGui.qApp.db.translate('rbVisitType', 'code', '', 'id'))
                self.tryFindDefaultVisitTypeId = False
        return self.defaultVisitTypeId

    def addAbsentPersons(self, personIdList, eventDate = None):
        for item in self.items():
            personId = forceRef(item.value('person_id'))
            if personId in personIdList:
                personIdList.remove(personId)
        for personId in personIdList:
            item = self.getEmptyRecord(personId=personId)
            date = eventDate if eventDate else QtCore.QDate.currentDate()
            item.setValue('date', toVariant(date))
            self.items().append(item)
        if personIdList:
            self.reset()


class CF110DiagnosisTypeCol(CDiagnosisTypeCol):
    def __init__(self, title=u'Тип', fieldName='diagnosisType_id', width=5, diagnosisTypeCodes=None, smartMode=True,
                 **params):
        if not diagnosisTypeCodes:
            diagnosisTypeCodes = []
        CDiagnosisTypeCol.__init__(self, title, fieldName, width, diagnosisTypeCodes, smartMode, **params)
        self.namesF110 = [u'Осн', u'Соп', u'Осл']

    def toString(self, val, record):
        typeId = forceRef(val)
        if typeId in self.ids:
            return toVariant(self.namesF110[self.ids.index(typeId)])
        return QtCore.QVariant()

    def setEditorData(self, editor, value, record):
        editor.clear()
        if value.isNull():
            value = record.value(self.fieldName())
        typeId = forceRef(value)
        if self.smartMode:
            if typeId == self.ids[0]:
                editor.addItem(self.namesF110[0], toVariant(self.ids[0]))
            elif typeId == self.ids[1]:
                if self.ids[0]:
                    editor.addItem(self.namesF110[0], toVariant(self.ids[0]))
                editor.addItem(self.namesF110[1], toVariant(self.ids[1]))
            else:
                editor.addItem(self.namesF110[2], toVariant(self.ids[2]))
        else:
            for itemName, itemId in zip(self.namesF110, self.ids):
                if itemId:
                    editor.addItem(itemName, toVariant(itemId))
        currentIndex = editor.findData(toVariant(typeId))
        editor.setCurrentIndex(currentIndex)


class CF110BaseDiagnosticsModel(CInDocTableModel):
    __pyqtSignals__ = ('typeOrPersonChanged()',)
    resultChanged = QtCore.pyqtSignal()
    MKB_allowed_morphology = ['C', 'D']

    def __init__(self, parent, baseDiagnosisTypeCode, accompDiagnosisTypeCode, complicDiagnosisTypeCode):
        CInDocTableModel.__init__(self, 'Diagnostic', 'id', 'event_id', parent)
        self._parent = parent
        self.isManualSwitchDiagnosis = QtGui.qApp.defaultIsManualSwitchDiagnosis()
        self.isMKBMorphology = QtGui.qApp.defaultMorphologyMKBIsVisible()
        self.characterIdForHandleDiagnosis = None
        self.columnHandleDiagnosis = None
        self.diagnosisTypeCol = CF110DiagnosisTypeCol( u'Тип', 'diagnosisType_id', 2, [baseDiagnosisTypeCode, accompDiagnosisTypeCode, complicDiagnosisTypeCode], smartMode=False)
        self.addCol(self.diagnosisTypeCol)
        self.colPerson = self.addCol(CActionPersonInDocTableColSearch(     u'Врач',            'person_id',  20, 'vrbPersonWithSpeciality', order = 'name', parent=parent))
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
        self.addCol(CRBLikeEnumInDocTableCol(u'Госп',      'hospital',       7, CHospitalInfo.names, showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(u'Потребность в госпитализации')
        self.addCol(CRBInDocTableCol(    u'Травма',        'traumaType_id', 10, 'rbTraumaType', addNone=True, showFields=CRBComboBox.showName, prefferedWidth=150))
        self.addCol(CRBInDocTableCol(forceTr(u'Результат', u'EventDiagnostic'),     'result_id',     10, 'rbDiagnosticResult', showFields=CRBComboBox.showNameAndCode, prefferedWidth=350))
        self.columnResult = self._mapFieldNameToCol.get('result_id')
        self.setFilter(self.table['diagnosisType_id'].inlist([typeId for typeId in self.diagnosisTypeCol.ids if typeId]))

    def manualSwitchDiagnosis(self):
        return self.isManualSwitchDiagnosis

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
                    if not (bool(mkb) and mkb[0] in CF110BaseDiagnosticsModel.MKB_allowed_morphology):
                        result = (result & ~QtCore.Qt.ItemIsEditable)
        if QtGui.qApp.isPNDDiagnosisMode() and (row == len(self.items()) or index.column() != self._mapFieldNameToCol.get('result_id')):
            result = (result & ~QtCore.Qt.ItemIsEditable)
        return result

    def getEmptyRecord(self):
        result = CInDocTableModel.getEmptyRecord(self)
        result.append(QtSql.QSqlField('diagnosis_id',     QtCore.QVariant.Int))
        result.append(QtSql.QSqlField('speciality_id',    QtCore.QVariant.Int))
        result.append(QtSql.QSqlField('setDate',          QtCore.QVariant.DateTime))
        result.append(QtSql.QSqlField('endDate',          QtCore.QVariant.DateTime))
        result.setValue('person_id',     toVariant(QtCore.QObject.parent(self).getSuggestedPersonId()))
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
            if column == 0: # тип диагноза
                result = CInDocTableModel.setData(self, index, value, role)
                if result:
                    self.updateDiagnosisType(set([row]))
                    self.emitTypeOrPersonChanged()
                return result
            elif column == 1: # врач
                result = CInDocTableModel.setData(self, index, value, role)
                if result:
                    self.updateDiagnosisType(set())
                    self.emitTypeOrPersonChanged()
                return result
            elif column == 2: # код МКБ
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
                if result:
                    self.updateCharacterByMKB(row, specifiedMKB, specifiedCharacterId)
                    self.updateTraumaType(row, specifiedMKB, specifiedTraumaTypeId)
                    self.emitTypeOrPersonChanged()
                return result
            elif column == self.columnResult and row == 0:
                oldDesultId = self.resultId()
                result = CInDocTableModel.setData(self, index, value, role)
                if oldDesultId != self.resultId():
                    self.resultChanged.emit()
                return result
            if column == 3: # доп. код МКБ
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

    def removeRowEx(self, row):
        self.removeRows(row, 1)
        if row == 0:
            self.resultChanged.emit()

    def updateDiagnosisType(self, fixedRowSet):
        mapPersonIdToRow = {}
        diagnosisTypeIds = []
        basePersonId = []
        for row, item in enumerate(self.items()):
            personId = forceRef(item.value('person_id'))
            rows = mapPersonIdToRow.setdefault(personId, [])
            rows.append(row)
            diagnosisTypeId = forceRef(item.value('diagnosisType_id'))
            diagnosisTypeIds.append(diagnosisTypeId)
        for personId, rows in mapPersonIdToRow.iteritems():
            basePersonId = []
            firstDiagnosisId = diagnosisTypeIds[rows[0]]
            for rowFixed in fixedRowSet.intersection(set(rows)):
                if (self.diagnosisTypeCol.ids[0] == diagnosisTypeIds[rowFixed]):
                    firstDiagnosisId = self.diagnosisTypeCol.ids[0]
                    if personId not in basePersonId:
                        basePersonId.append(personId)
                else:
                    firstDiagnosisId = diagnosisTypeIds[rowFixed]
            freeRows = set(rows).difference(fixedRowSet)
            for row in rows:
                if (row in freeRows) and firstDiagnosisId == self.diagnosisTypeCol.ids[0] and diagnosisTypeIds[row] == self.diagnosisTypeCol.ids[0] and (personId in basePersonId):
                    self.items()[row].setValue('diagnosisType_id', toVariant(self.diagnosisTypeCol.ids[1]))
                    self.emitCellChanged(row, self.items()[row].indexOf('diagnosisType_id'))
                    diagnosisTypeIds[row] = forceRef(self.items()[row].value('diagnosisType_id'))

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
    
    def resultId(self):
        items = self.items()
        if items:
            return forceRef(items[0].value('result_id'))
        else:
            return None
        
    def setResult(self,  resultID, onlyIfNone = True):
        items = self.items()
        if len(items) > 0 and (not onlyIfNone or forceRef(items[0].value('result_id')) is None):
            items[0].setValue('result_id', resultID)
            self.setItems(items)
            self.resultChanged.emit()

    def getFinalDiagnosis(self):
        return self._items[0] if self._items else None
    
    
class CF110FinalDiagnosticsModel(CF110BaseDiagnosticsModel):
    def __init__(self, parent):
        CF110BaseDiagnosticsModel.__init__(self, parent, '2', '9', '3')
        self.mapMKBToServiceId = {}

    def getCloseOrMainDiagnosisTypeIdList(self):
        return [self.diagnosisTypeCol.codeToId(code) for code in ['1', '2']]
