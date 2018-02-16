# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

# Форма 131: ДД и т.п.

from PyQt4 import QtCore, QtGui, QtSql

from Events.Action import CActionType
from Events.ActionInfo import CActionInfoProxyList
from Events.ActionsSummaryModel import CFxxxActionsSummaryModel
from Events.DiagnosisType import CDiagnosisTypeCol
from Events.EventEditDialog import CEventEditDialog, CDiseaseCharacter, CDiseaseStage, CDiseasePhases
from Events.EventInfo import CDiagnosticInfoProxyList, CHospitalInfo
from Events.Utils import checkDiagnosis, checkIsHandleDiagnosisIsChecked, getAvailableCharacterIdByMKB, \
    getDiagnosisId2, getEventDuration, getEventShowTime, \
    getExactServiceId, getResultIdByDiagnosticResultId, getWorstPayStatus, \
    payStatusText, setAskedClassValueForDiagnosisManualSwitch, CPayStatus, \
    getEventLengthDays, CTableSummaryActionsMenuMixin, \
    setOrgStructureIdToCmbPerson
from Forms.F131.PreF131Dialog import CPreF131Dialog
from Forms.Utils import check_data_text_TNM
from Orgs.OrgComboBox import CPolyclinicExtendedInDocTableCol
from Orgs.Orgs import selectOrganisation
from Orgs.PersonInfo import CPersonInfo
from Orgs.Utils import getOrganisationInfo
from Registry.HurtModels import CWorkHurtFactorsModel, CWorkHurtsModel
from Ui_F131 import Ui_Dialog
from Users.Rights import urAdmin, urDoNotCheckResultAndMKB, urRegTabWriteRegistry, \
    urOncoDiagnosisWithoutTNMS
from library.ICDInDocTableCol import CICDExInDocTableCol
from library.ICDMorphologyInDocTableCol import CMKBMorphologyCol
from library.InDocTable import CInDocTableModel, CBoolInDocTableCol, CDateInDocTableCol, CRBInDocTableCol, \
    CRBLikeEnumInDocTableCol, CActionPersonInDocTableColSearch, CEnumInDocTableCol
from library.PrintInfo import CInfoContext, CDateInfo
from library.PrintTemplates import applyTemplate, customizePrintButton, getPrintButton
from library.TNMS.TNMSComboBox import CTNMSCol
from library.Utils import forceBool, forceDate, forceInt, forceRef, forceString, forceStringEx, toVariant, \
    copyFields, formatNum, variantEq, forceTr
from library.crbcombobox import CRBComboBox
from library.interchange import getDateEditValue, getDatetimeEditValue, getRBComboBoxValue, setDateEditValue, \
    setDatetimeEditValue, setRBComboBoxValue


def specialityName(specialityId):
    specialityRecord = QtGui.qApp.db.getRecord('rbSpeciality', 'name', specialityId)
    if specialityRecord:
        return forceString(specialityRecord.value('name'))
    else:
        return '{%d}'%specialityId


def actionTypeName(actionTypeId):
    actionTypeRecord = QtGui.qApp.db.getRecord('ActionType', 'name', actionTypeId)
    if actionTypeRecord:
        return forceString(actionTypeRecord.value('name'))
    else:
        return '{%d}'%actionTypeId


class CF131Dialog(CEventEditDialog, Ui_Dialog, CTableSummaryActionsMenuMixin):
    # типы диагнозов
    dtFinish = 0 # Заключительный
    dtBase   = 1 # Основной
    dfAccomp = 2 # Сопутствующий
#    dfMapToCode   = {dtFinish:'1', dtBase:'2', dfAccomp:'9'}
#    dfMapFromCode = {'1': dtFinish, '2':dtBase, '9':dfAccomp}

    isTabMesAlreadyLoad = False
    isTabStatusAlreadyLoad = False
    isTabDiagnosticAlreadyLoad = False
    isTabCureAlreadyLoad = False
    isTabMiscAlreadyLoad = False
    isTabCashAlreadyLoad = False
    isTabNotesAlreadyLoad = False

    def __init__(self, parent):
        CEventEditDialog.__init__(self, parent)
        self.__workRecord   = None

        self.availableDiagnostics = []
        self.mapSpecialityIdToDiagFilter = {}

        self.addModels('WorkHurts', CWorkHurtsModel(self))
        self.addModels('WorkHurtFactors', CWorkHurtFactorsModel(self))
        self.addModels('Diagnostics', CF131DiagnosticsModel(self))
        self.addModels('ActionsSummary', CFxxxActionsSummaryModel(self, True))

        self.actEditClient = QtGui.QAction(u'Изменить описание клиента', self)
        self.actEditClient.setObjectName('actEditClient')
        self.setupDiagnosticsMenu()
        self.setupActionsMenu()

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
        self.setWindowTitleEx(u'Осмотр Ф.131')
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
        self.setupActionSummarySlots()
        self.cmbContract.setCheckMaxClients(True)

        self.tblWorkHurts.setModel(self.modelWorkHurts)
        self.tblWorkHurtFactors.setModel(self.modelWorkHurtFactors)
        self.tblFinalDiagnostics.setModel(self.modelDiagnostics)
        self.tblActions.setModel(self.modelActionsSummary)
        self.modelActionsSummary.addModel(self.tabStatus.modelAPActions)
        self.modelActionsSummary.addModel(self.tabDiagnostic.modelAPActions)
        self.modelActionsSummary.addModel(self.tabCure.modelAPActions)
        self.modelActionsSummary.addModel(self.tabMisc.modelAPActions)
        self.tabCash.addActionModel(self.tabStatus.modelAPActions)
        self.tabCash.addActionModel(self.tabDiagnostic.modelAPActions)
        self.tabCash.addActionModel(self.tabCure.modelAPActions)
        self.tabCash.addActionModel(self.tabMisc.modelAPActions)

        self.markEditableTableWidget(self.tblWorkHurts)
        self.markEditableTableWidget(self.tblWorkHurtFactors)
        self.markEditableTableWidget(self.tblFinalDiagnostics)
        self.markEditableTableWidget(self.tblActions)

        self.txtClientInfoBrowser.actions.append(self.actEditClient)
        self.actEditClient.setEnabled(QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteRegistry]))
        self.tblWorkHurts.addPopupDelRow()
        self.tblWorkHurtFactors.addPopupDelRow()
        self.tblFinalDiagnostics.setPopupMenu(self.mnuDiagnostics)
        self.tblActions.setPopupMenu(self.mnuAction)
        self.qshcActionsEdit = QtGui.QShortcut(QtGui.QKeySequence('F4'), self.tblActions, self.on_actActionEdit_triggered)
        self.qshcActionsEdit.setObjectName('qshcActionsEdit')
        self.qshcActionsEdit.setContext(QtCore.Qt.WidgetShortcut)
        CTableSummaryActionsMenuMixin.__init__(self)

        self.setupDirtyCather()
        self.setIsDirty(False)
        self.blankMovingIdList = []
        self.prolongateEvent = False
        self.prevEventId = None
        self.tabNotes.setEventEditor(self)
        self.availableSpecialities = {}
        self.cmbResult.setShowFields(CRBComboBox.showCodeAndName)

        self.postSetupUi()

        self._isCheckPresenceInAccounts = True

        self.cmbPerson.addNotSetValue()
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
        return self.edtEndDate.date()

    @eventDate.setter
    def eventDate(self, value):
        if isinstance(value, QtCore.QDate):
            self.edtEndDate.setDate(value)
            self.edtEndTime.setTime(QtCore.QTime())
        elif isinstance(value, QtCore.QDateTime):
            self.edtEndDate.setDate(value.date())
            self.edtEndTime.setTime(value.time())

    def setEditable(self, editable):
        self.modelDiagnostics.setEditable(editable)
        self.modelActionsSummary.setEditable(editable)
        self.modelWorkHurts.setEditable(editable)
        self.modelWorkHurtFactors.setEditable(editable)
        self.grpBase.setEnabled(editable)
        self.grpWork.setEnabled(editable)
        self.tabMes.setEnabled(editable)
        self.tabStatus.setEditable(editable)
        self.tabDiagnostic.setEditable(editable)
        self.tabCure.setEditable(editable)
        self.tabMisc.setEditable(editable)
        self.tabCash.setEditable(editable)
        self.tabNotes.setEditable(editable)

    def setupDiagnosticsMenu(self):
        self.mnuDiagnostics = QtGui.QMenu(self)
        self.mnuDiagnostics.setObjectName('mnuDiagnostics')
        self.actDiagnosticsAddBase = QtGui.QAction(u'Добавить осмотр', self)
        self.actDiagnosticsAddBase.setObjectName('actDiagnosticsAddBase')
        self.actDiagnosticsAddAccomp = QtGui.QAction(u'Добавить сопутствующий диагноз', self)
        self.actDiagnosticsAddAccomp.setObjectName('actDiagnosticsAddAccomp')
        self.actDiagnosticsRemove = QtGui.QAction(u'Удалить запись', self)
        self.actDiagnosticsRemove.setObjectName('actDiagnosticsRemove')
        self.mnuDiagnostics.addAction(self.actDiagnosticsAddBase)
        self.mnuDiagnostics.addAction(self.actDiagnosticsAddAccomp)
        self.mnuDiagnostics.addSeparator()
        self.mnuDiagnostics.addAction(self.actDiagnosticsRemove)

    ## Проверка на первичность.
    def isPrimary(self, clientId, eventTypeId, personId, eventSetDatetime):
        eventSetDate = eventSetDatetime.date() if isinstance(eventSetDatetime, QtCore.QDateTime) else eventSetDatetime
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        cond = [tableEvent['deleted'].eq(0),
                tableEvent['client_id'].eq(clientId),
                tableEvent['eventType_id'].eq(eventTypeId),
                tableEvent['execDate'].ge(eventSetDate.addMonths(-self.eventPeriod))
               ]
        record = db.getRecordEx(tableEvent, 'id', cond)
        return not record
    
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
        if not recommendationList:
            recommendationList = []
        self.setPersonId(personId)
        self.setOrgStructureId(orgStructureId)

        dlg = CPreF131Dialog(self, self.personSpecialityId)
        plannerDate = self.getPlannerDate(eventSetDatetime, eventDatetime)
        dlg.prepare(clientId, eventTypeId, plannerDate, tissueTypeId, recommendationList,
                    useDiagnosticsAndActionsPresets=useDiagnosticsAndActionsPresets
                    )
        if not dlg.boolPersonSpecialityId:
            widget = QtGui.qApp.activeModalWidget() or QtGui.qApp.mainWindow or None
            QtGui.QMessageBox.critical( widget,
                                        u'Произошла ошибка',
                                        u'В планировщике отсутствует специальность ответственного лица',
                                        QtGui.QMessageBox.Ok)
            return False
        if not dlg.exec_():
            return False

        self.cmbResult.setTable('rbResult', True)
        self.eventSetDateTime = eventSetDatetime
        self.eventDate = eventDatetime
        self.setOrgId(orgId if orgId else QtGui.qApp.currentOrgId())
        self.setClientId(clientId)
        self.prolongateEvent = True if actionByNewEvent else False
        self.setExternalId(externalId)
        self.cmbPerson.setValue(personId)
        self.setEventTypeId(eventTypeId)
        self.edtPrevDate.setDate(QtCore.QDate())
        self.chkPrimary.setChecked(self.isPrimary(clientId, eventTypeId, personId, eventSetDatetime))
        self.initGoal()
        self.setContract()
        self.setRecommendations(recommendationList)

        self.updateModelsRetiredList()

        self.fillNextDate() # must be after self.setEventTypeId
        self.prepareDiagnostics(dlg.diagnostics())
        self.prepareActions(dlg.actions())
        if self.cmbContract.count() == 1:
            self.edtEndDate.setFocus(QtCore.Qt.OtherFocusReason)
        self.tabNotes.setNotesEx(externalId, assistantId, curatorId, relegateOrgId, referrals = referrals)
        self.setIsDirty(False)
        self.tabNotes.setEventEditor(self)
        self.tabMes.postSetupUi()
        return self.checkEventCreationRestriction()

    def newDiagnosticRecord(self, template, boolSetRecord = True):
        finishDiagnosisTypeId, baseDiagnosisTypeId, accompDiagnosisTypeId = self.modelDiagnostics.diagnosisTypeCol.ids
        result = self.tblFinalDiagnostics.model().getEmptyRecord()
        result.setValue('speciality_id',  template.value('speciality_id'))
        if boolSetRecord:
            diagnosisTypeId = template.value('diagnosisType_id')
            result.setValue('diagnosisType_id', diagnosisTypeId if diagnosisTypeId.isValid() else QtCore.QVariant(accompDiagnosisTypeId))
        else:
            if self.personSpecialityId == forceRef(template.value('speciality_id')):
                result.setValue('person_id', QtCore.QVariant(self.personId))
                result.setValue('diagnosisType_id', QtCore.QVariant(finishDiagnosisTypeId))
                for item in self.modelDiagnostics.items():
                    if self.personSpecialityId == forceRef(item.value('speciality_id')) and forceInt(item.value('diagnosisType_id')) == finishDiagnosisTypeId:
                        result.setValue('diagnosisType_id', QtCore.QVariant(baseDiagnosisTypeId))
                        break
            else:
                result.setValue('diagnosisType_id', QtCore.QVariant(baseDiagnosisTypeId))
        result.setValue('setDate',        toVariant(self.eventSetDateTime))
        result.setValue('healthGroup_id', template.value('defaultHealthGroup_id'))
        result.setValue('medicalGroup_id', template.value('defaultMedicalGroup_id'))
        result.setValue('MKB',            template.value('defaultMKB'))
        result.setValue('defaultMKB',     template.value('defaultMKB'))
        result.setValue('actuality',      template.value('actuality'))
        result.setValue('visitType_id',   template.value('visitType_id'))
        result.setValue('scene_id',       QtCore.QVariant(forceRef(QtGui.qApp.db.translate('rbScene', 'code',  '1', 'id'))))
        result.setValue('selectionGroup', template.value('selectionGroup'))
        result.setValue('service_id', template.value('service_id'))
        return result


    def prepareDiagnostics(self, diagnostics):
        firstWithGoal = True
        for record in diagnostics:
            if firstWithGoal:
                goalId = forceRef(record.value('defaultGoal_id'))
                if goalId:
                    self.cmbGoal.setValue(goalId)
                    firstWithGoal = False
            if forceInt(record.value('include')) != 0:
                self.modelDiagnostics.items().append(self.newDiagnosticRecord(record, False))
        self.modelDiagnostics.reset()


    def prepareActions(self, presetActions):
        def addActionType(actionTypeId, amount, org_id):
            for model in [self.tabStatus.modelAPActions,
                          self.tabDiagnostic.modelAPActions,
                          self.tabCure.modelAPActions,
                          self.tabMisc.modelAPActions]:
                if actionTypeId in model.actionTypeIdList:
                    model.addRow(actionTypeId, amount)
                    record = model.items()[-1][0]
                    record.setValue('org_id', toVariant(org_id))
                    break

        for actionTypeId, amount, payable, org_id in presetActions:
            addActionType(actionTypeId, amount, org_id)

    def setRecord(self, record):
        self.cmbResult.setTable('rbResult', True)
        CEventEditDialog.setRecord(self, record)
        setDateEditValue(self.edtPrevDate,      record, 'prevEventDate')
        setDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'setDate')
        setRBComboBoxValue(self.cmbPerson,      record, 'setPerson_id')
        setDatetimeEditValue(self.edtEndDate, self.edtEndTime, record, 'execDate')
        setRBComboBoxValue(self.cmbPerson,      record, 'execPerson_id')
        setRBComboBoxValue(self.cmbResult,      record, 'result_id')
        setDateEditValue(self.edtNextDate,      record, 'nextEventDate')
        self.chkPrimary.setChecked(forceInt(record.value('isPrimary'))==1)
        self.setExternalId(forceString(record.value('externalId')))
        self.setPersonId(self.cmbPerson.value())
        self.setContract()
        setRBComboBoxValue(self.cmbContract,    record, 'contract_id')
        self.prevEventId = forceRef(record.value('prevEvent_id'))
        self.tabReferral.setRecord(record)

        payStatus = self.getEventPayStatus()

        self.addPayStatusBar(payStatus)
        self.setEditable(self.getEditable())

        if self.prevEventId:
            self.lblProlongateEvent.setText(u'п')
            db = QtGui.qApp.db
            tableEvent = db.table('Event')
            tableEventType = db.table('EventType')
            prevEventRecord = db.getRecordEx(tableEvent.innerJoin(tableEventType, tableEvent['eventType_id'].eq((tableEventType['id']))), [tableEventType['name'], tableEvent['setDate']], [tableEvent['deleted'].eq(0), tableEvent['id'].eq(self.prevEventId)])
            if prevEventRecord:
                self.tabNotes.edtPrevEventInfo.setText(u'Продолжение обращения: %s от %s.'%(forceString(prevEventRecord.value('name')), forceDate(prevEventRecord.value('setDate')).toString('dd.MM.yyyy')))
        self.blankMovingIdList = []
        dlg = CPreF131Dialog(None, self.personSpecialityId)
        dlg.prepare(self.clientId, self.eventTypeId, self.eventSetDateTime.date(), None)
        if not dlg.boolPersonSpecialityId:
            widget = QtGui.qApp.activeModalWidget() or QtGui.qApp.mainWindow or None
            QtGui.QMessageBox.critical( widget,
                                        u'Произошла ошибка',
                                        u'В планировщике отсутствует специальность ответственного лица',
                                        QtGui.QMessageBox.Ok)
        self.loadDiagnostics(dlg.diagnostics(), self.itemId())
        self.updateResultFilter()
        self.loadActions()
        self.updateMesMKB()
        self.tabMes.setBegDate(forceDate(record.value('setDate')))
        self.tabMes.setEndDate(forceDate(record.value('execDate')))
        self.tabMes.setRecord(record)
        if self.cmbContract.count() == 1:
            self.edtEndDate.setFocus(QtCore.Qt.OtherFocusReason)
        self.tabCash.load(self.itemId())
        self.tabNotes.setNotes(record)
        self.tabNotes.setEventEditor(self)
        self.setIsDirty(False)
        setOrgStructureIdToCmbPerson(self.cmbPerson)

    def setLeavedAction(self, actionTypeIdValue):
        pass

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

    def loadDiagnostics(self, diagnostics, eventId):
        def selectionGroup(i):
            return forceInt(diagnostics[i].value('selectionGroup'))

        def getDiagnosisType(diagnosisTypeId):
            if diagnosisTypeId in self.modelDiagnostics.diagnosisTypeCol.ids:
                return self.modelDiagnostics.diagnosisTypeCol.ids.index(diagnosisTypeId)
            else:
                return 2

        n = len(diagnostics)
        db = QtGui.qApp.db
        table = db.table('Diagnostic')
        tableVisit  = db.table('Visit')
        tablePerson = db.table('Person')
        isDiagnosisManualSwitch = self.modelDiagnostics.manualSwitchDiagnosis()
        joinVisitPerson = tableVisit.leftJoin(tablePerson, tablePerson['id'].eq(tableVisit['person_id']))
        rawItems = db.getRecordList(table, '*', [table['deleted'].eq(0), table['event_id'].eq(eventId)], 'id')
        specInTemplate = []
        for record in diagnostics:
            specialityId = forceRef(record.value('speciality_id'))
            if specialityId in specInTemplate:
                specInTemplate.append(None)
            else:
                specInTemplate.append(specialityId)

        # группируем записи по группам по id специальности
        rawSorted = [ [] for record in diagnostics ]
        for record in rawItems:
            specialityId = forceRef(record.value('speciality_id'))
            if specialityId and specialityId in specInTemplate:
                i = specInTemplate.index(specialityId)
                diagnosisTypeId = record.value('diagnosisType_id')
                diagnosisId     = record.value('diagnosis_id')
                MKB             = db.translate('Diagnosis', 'id', forceRef(diagnosisId), 'MKB')
                morphologyMKB   = db.translate('Diagnosis', 'id', forceRef(diagnosisId), 'morphologyMKB')
                newRecord = self.modelDiagnostics.getEmptyRecord()
                copyFields(newRecord, record)
                newRecord.setValue('diagnosisTypeId', diagnosisTypeId)
                if MKB:
                    newRecord.setValue('MKB',           MKB)
                if morphologyMKB:
                    newRecord.setValue('morphologyMKB', morphologyMKB)
                newRecord.setValue('defaultMKB',    diagnostics[i].value('defaultMKB'))
                newRecord.setValue('actuality',     diagnostics[i].value('actuality'))
                newRecord.setValue('visitType_id',  diagnostics[i].value('visitType_id'))
                newRecord.setValue('service_id',    diagnostics[i].value('service_id'))
                newRecord.setValue('scene_id',    diagnostics[i].value('scene_id'))
                newRecord.setValue('selectionGroup',diagnostics[i].value('selectionGroup'))
                setDate = forceDate(record.value('setDate'))
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
                rawSorted[i].append(newRecord)

        # в случае обнаружения альтернативных групп (имеющих равный не 0 и не 1 код выбора)
        # оставляем только первый выбор
        for i in xrange(n):
            group = selectionGroup(i)
            if rawSorted[i] and group not in [0, 1]:
                for j in xrange(i+1, n):
                    if selectionGroup(j) == group:
                        rawSorted[j] = []
        # упорядочиваем по коду типа диагноза
        for group in rawSorted:
            group.sort(key=lambda record: getDiagnosisType(forceInt(record.value('diagnosisType_id'))))
        # в пустые группы с ненулевым кодом добавляем строки из планировщика
        for i in xrange(n):
            if not rawSorted[i]:
                group = selectionGroup(i)
                needAdd = group > 0
                if group > 1 :
                    for j in xrange(n):
                        if i != j and rawSorted[j] and selectionGroup(j) == group:
                            needAdd = False
                            break
                if needAdd and specInTemplate[i]:
                    rawSorted[i].append(self.newDiagnosticRecord(diagnostics[i]))

        # восстанавливаем тип диагноза (если он утрачен), устанавливаем ссылки на визиты и статусы оплаты
        finishDiagnosisTypeId, baseDiagnosisTypeId, accompDiagnosisTypeId = self.modelDiagnostics.diagnosisTypeCol.ids
        visitIdListRecord = []
        for groupIndex, group in enumerate(rawSorted):
            for i, record in enumerate(group):
                diagnosisTypeId = forceRef(record.value('diagnosisType_id'))
                if i == 0 and diagnosisTypeId == accompDiagnosisTypeId:
                    diagnosisTypeId = baseDiagnosisTypeId
                    record.setValue('diagnosisType_id', toVariant(diagnosisTypeId))
                visitId = None
                visitTypeId = None
                serviceId = None
                sceneId = None
                payStatus = CPayStatus.initial
                if diagnosisTypeId in [finishDiagnosisTypeId, baseDiagnosisTypeId]:
                    visitCond = [tableVisit['event_id'].eq(self.itemId()),
                                 tablePerson['speciality_id'].eq(record.value('speciality_id'))
                                 ]
                    if visitIdListRecord:
                        visitCond.append(tableVisit['id'].notInlist(visitIdListRecord))
                    visitRecord = db.getRecordEx(joinVisitPerson,
                                                [tableVisit['id'], tableVisit['scene_id'], tableVisit['visitType_id'], tableVisit['service_id'], tableVisit['payStatus']],
                                                where=visitCond,
                                                order=tableVisit['id'])
                    if visitRecord:
                        visitId = forceRef(visitRecord.value('id'))
                        if visitId not in visitIdListRecord:
                            visitIdListRecord.append(visitId)
                        sceneId = forceRef(visitRecord.value('scene_id'))
                        visitTypeId = forceRef(visitRecord.value('visitType_id'))
                        serviceId = forceRef(visitRecord.value('service_id'))
                        payStatus = getWorstPayStatus(forceInt(visitRecord.value('payStatus')))
                if visitId:
                    record.setValue('visit_id',      toVariant(visitId))
                    record.setValue('visitType_id',  toVariant(visitTypeId))
                    record.setValue('service_id',    toVariant(serviceId))
                    record.setValue('scene_id',      toVariant(sceneId))
                    record.setValue('payStatus',     toVariant(payStatus))
        # объединяем в один список
        items = []
        for group in rawSorted:
            items.extend(group)
        # и устанавливаем в модель:
        self.modelDiagnostics.setItems(items)

    def loadActions(self):
        id = self.itemId()
        self.tabStatus.loadActionsLite(id)
        self.tabDiagnostic.loadActionsLite(id)
        self.tabCure.loadActionsLite(id)
        self.tabMisc.loadActionsLite(id)
        self.modelActionsSummary.regenerate()
        self.tabCash.modelAccActions.regenerate()

    def getRecord(self):
        record = CEventEditDialog.getRecord(self)
        if not self.record():
            record.setValue('order', QtCore.QVariant(1))
        
        showTime = getEventShowTime(self.eventTypeId)

        getRBComboBoxValue(self.cmbContract,    record, 'contract_id')
        getDateEditValue(self.edtPrevDate,      record, 'prevEventDate')
        getDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'setDate', showTime)
        getRBComboBoxValue(self.cmbPerson,      record, 'setPerson_id')
        getDatetimeEditValue(self.edtEndDate, self.edtEndTime, record, 'execDate', showTime)
        getRBComboBoxValue(self.cmbPerson,      record, 'execPerson_id')
        getRBComboBoxValue(self.cmbResult,      record, 'result_id')
        getDateEditValue(self.edtNextDate,      record, 'nextEventDate')
        record.setValue('isPrimary', toVariant(1 if self.chkPrimary.isChecked() else 2))
        if self.prolongateEvent:
            record.setValue('order', toVariant(5))
            record.setValue('prevEvent_id', toVariant(self.prevEventId))
        self.tabNotes.getNotes(record, self.eventTypeId)
        return record

    def saveInternals(self, eventId):
        super(CF131Dialog, self).saveInternals(eventId)
        self.saveWorkRecord()
        self.saveDiagnostics(eventId)
        setAskedClassValueForDiagnosisManualSwitch(None)
        self.updateVisits(eventId)
        self.saveActions(eventId)
        self.tabCash.save(eventId)
        self.saveBlankUsers(self.blankMovingIdList)
        self.updateRecommendations()

    def saveWorkRecord(self):
        workRecord, workRecordChanged = self.getWorkRecord()
        if workRecordChanged and workRecord:
            workRecordId = QtGui.qApp.db.insertOrUpdate('ClientWork', workRecord)
        elif workRecord:
            workRecordId = forceRef(workRecord.value('id'))
        else:
            workRecordId = None
        if workRecordId:
            self.modelWorkHurts.saveItems(workRecordId)
            self.modelWorkHurtFactors.saveItems(workRecordId)

    def saveDiagnostics(self, eventId):
        accompDiagnosisTypeId = self.modelDiagnostics.diagnosisTypeCol.ids[2]
        items = self.modelDiagnostics.items()
        isDiagnosisManualSwitch = self.modelDiagnostics.manualSwitchDiagnosis()
        prevId = 0
        prevItem = None

        for item in items:
            diagnosisTypeId = forceRef(item.value('diagnosisType_id'))
            MKB = forceString(item.value('MKB'))
            TNMS = forceString(item.value('TNMS'))
            morphologyMKB = forceString(item.value('morphologyMKB'))
            if diagnosisTypeId == accompDiagnosisTypeId and prevItem:
                for fieldName in ['speciality_id', 'person_id', 'setDate', 'endDate']:
                    item.setValue(fieldName, prevItem.value(fieldName))
            diagnosisId = forceRef(item.value('diagnosis_id'))
            diagnosisId, characterId = getDiagnosisId2(
                forceDate(item.value('endDate')),
                forceRef(item.value('person_id')),
                self.clientId,
                diagnosisTypeId,
                MKB,
                '',
                forceRef(item.value('character_id')),
                forceRef(item.value('dispanser_id')),
                None,
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
            payStatus = forceInt(item.value('payStatus'))
            itemId = forceInt(item.value('id'))
            if prevId>itemId and payStatus == CPayStatus.initial:
                item.setValue('id', QtCore.QVariant())
                prevId = 0
            else:
                prevId = itemId
            prevItem = item
        self.modelDiagnostics.saveItems(eventId)

    def updateVisits(self, eventId):
        db = QtGui.qApp.db
        # sceneId = forceRef(db.translate('rbScene', 'code',  '1', 'id'))
        finishDiagnosisTypeId = self.modelDiagnostics.diagnosisTypeCol.ids[0]
        baseDiagnosisTypeId = self.modelDiagnostics.diagnosisTypeCol.ids[1]
        table = db.table('Visit')
        diagnostics = self.modelDiagnostics.items()
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
                actuality = forceInt(diagnostic.value('actuality'))
                if not setDate.isNull() and (endDate.isNull() or setDate.addMonths(-actuality)<=endDate) and personId and visitTypeId:
                    visitId = forceRef(diagnostic.value('visit_id'))
                    if visitId:
                        record = db.getRecord(table, '*', visitId)
                    else:
                        record = table.newRecord()
                    record.setValue('event_id',     toVariant(eventId))
                    record.setValue('scene_id',     toVariant(sceneId))
                    record.setValue('date',         toVariant(endDate))
                    record.setValue('visitType_id', toVariant(visitTypeId))
                    record.setValue('person_id',    toVariant(personId))
                    record.setValue('isPrimary',    toVariant(1))
                    record.setValue('finance_id',   toVariant(financeId))
                    record.setValue('service_id',   toVariant(serviceId))
                    record.setValue('diagnostic_id', toVariant(forceRef(diagnostic.value('id'))))
                    visitId = db.insertOrUpdate(table, record)
                    visitIdList.append(visitId)
        cond = [table['event_id'].eq(eventId)]
        if visitIdList:
            cond.append('NOT ('+table['id'].inlist(visitIdList)+')')
        # запрещаю удалять выставленные визиты
        tableAccountItem = db.table('Account_Item')
        cond.append('NOT '+db.existsStmt(tableAccountItem, tableAccountItem['visit_id'].eq(table['id'])))
        db.deleteRecord(table, where=cond)

    def getFinalDiagnosisMKB(self):
        for row, record in enumerate(self.modelDiagnostics.items()):
            diagnosisType = self.modelDiagnostics.diagnosisType(row)
            if diagnosisType == CF131Dialog.dtFinish:
                MKB   = forceString(record.value('MKB'))
                MKBEx = forceString(record.value('MKBEx'))
                return MKB, MKBEx
        return '', ''

    def getFinalDiagnosis(self):
        for row, record in enumerate(self.modelDiagnostics.items()):
            diagnosisType = self.modelDiagnostics.diagnosisType(row)
            if diagnosisType == CF131Dialog.dtFinish:
                return record
        return None

    def saveActions(self, eventId):
        self.tabStatus.saveActions(eventId)
        self.tabDiagnostic.saveActions(eventId)
        self.tabCure.saveActions(eventId)
        self.tabMisc.saveActions(eventId)

    def setOrgId(self, orgId):
        self.orgId = orgId
        self.cmbPerson.setOrgId(orgId)
        self.cmbContract.setOrgId(orgId)

    def setExternalId(self, externalId):
        self.lblValueExternalId.setText((u'Внешний идентификатор: ' + externalId) if externalId else '')

    def setEventTypeId(self, eventTypeId):
        CEventEditDialog.setEventTypeId(self, eventTypeId, u'Ф.131')
        self.tabCash.windowTitle = self.windowTitle()
        showTime = getEventShowTime(eventTypeId)
        self.edtBegTime.setVisible(showTime)
        self.edtEndTime.setVisible(showTime)
        if self.cmbResult.value() is None:
            if self.inheritResult == True:
                self.cmbResult.setValue(self.defaultEventResultId.get(self.eventPurposeId))
        self.updateResultFilter()
        customizePrintButton(self.btnPrint, self.eventContext if self.eventContext else 'F131')

    def updateMKB(self):
        begDate = self.edtBegDate.date()
        filter = None
        if begDate.isValid():
            filter = {'begDate': begDate, 'clientId': self.clientId}
        cols = self.modelDiagnostics.cols()
        for col in (0, 1):
            resultCol = cols[len(cols) - 1]
            resultCol.filter = filter

    def getModelFinalDiagnostics(self):
        return self.modelDiagnostics

    def setWorkRecord(self, record):
        self.__workRecord = record
        self.cmbWorkOrganisation.setValue(forceRef(record.value('org_id')) if record else None)
        self.UpdateWorkOrganisationInfo()
        self.edtWorkPost.setText(forceString(record.value('post')) if record else '')
        self.cmbWorkOKVED.setText(forceString(record.value('OKVED')) if record else '')
        self.edtWorkStage.setValue(forceInt(record.value('stage')) if record else 0)
        self.modelWorkHurts.loadItems(forceRef(record.value('id')) if record else None)
        self.modelWorkHurtFactors.loadItems(forceRef(record.value('id')) if record else None)

    def getWorkRecord(self):
        organisationId = self.cmbWorkOrganisation.value()
        post  = forceStringEx(self.edtWorkPost.text())
        OKVED = forceStringEx(self.cmbWorkOKVED.text())
        stage = self.edtWorkStage.value()
        if self.__workRecord:
            recordChanged = (
                organisationId  != forceRef(self.__workRecord.value('org_id')) or
                post            != forceString(self.__workRecord.value('post')) or
                OKVED           != forceString(self.__workRecord.value('OKVED')) or
                stage           != forceInt(self.__workRecord.value('stage'))
                )
        else:
            recordChanged=True
        if recordChanged:
            record = QtGui.qApp.db.record('ClientWork')
            record.setValue('client_id',    toVariant(self.clientId))
            record.setValue('org_id',       toVariant(organisationId))
            record.setValue('post',         toVariant(post))
            record.setValue('OKVED',        toVariant(OKVED))
            record.setValue('stage',        toVariant(stage))
        else:
            record = self.__workRecord
        return record, recordChanged


    def UpdateWorkOrganisationInfo(self):
        id = self.cmbWorkOrganisation.value()
        orgInfo = getOrganisationInfo(id)
        self.lblINN.setText(u'ИНН ' + orgInfo.get('INN', ''))
        self.lblKPP.setText(u'КПП ' + orgInfo.get('KPP', ''))
        self.lblOGRN.setText(u'ОГРН ' + orgInfo.get('OGRN', ''))
        self.cmbWorkOKVED.setOrgCode(orgInfo.get('OKVED', ''))

    def checkDiagnosticMKBCodeEntered(self, row, record):
        MKB = forceString(record.value('MKB'))
        diagnosysType = forceString(record.value('diagnosisType_id'))

        if diagnosysType and not MKB:
            return self.checkValueMessage(
                u'Необходимо указать код МКБ.',
                False,
                self.tblFinalDiagnostics,
                row,
                self.tblFinalDiagnostics.model().indexOf('MKB')
            )
        return True

    def checkDiagnosticMKBCode(self):
        for row, record in enumerate(self.tblFinalDiagnostics.model().items()):
            if not self.checkDiagnosticMKBCodeEntered(row, record):
                return False
        return True

    def checkDataEntered(self):
        result = CEventEditDialog.checkDataEntered(self)
        result = result and self.checkDiagnosticMKBCode()
        if not QtGui.qApp.userHasRight('createSeveralVisits'):
            result = result and self.checkMoreThanOneVisit()
        result = result and (self.orgId != QtGui.qApp.currentOrgId() or self.cmbContract.value() or self.checkInputMessage(u'договор', False, self.cmbContract))
        self.blankMovingIdList = []
        begDate = self.edtBegDate.date()
        endDate = self.edtEndDate.date() if self._isClosedEventCheck else QtCore.QDate()
        nextDate = self.edtNextDate.date()
        if endDate.isNull():
            maxEndDate = self.getMaxEndDateByDiagnostics()
            if not maxEndDate.isNull():
                if QtGui.QMessageBox.question(self,
                                    u'Внимание!',
                                    u'Дата выполнения обращения не указана.\nУстановить дату завершения по максимальной дате осмотров?',
                                    QtGui.QMessageBox.No|QtGui.QMessageBox.Yes,
                                    QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
                    self.edtEndDate.setDate(maxEndDate)
                    endDate = maxEndDate
        if not endDate.isNull():
            result = result and self.checkActionDataEntered(begDate, QtCore.QDate(), endDate, self.tabToken, self.edtBegDate, None, self.edtEndDate)
            result = result and self.checkEventDate(begDate, endDate, nextDate, self.tabToken, self.edtNextDate, self.edtEndDate, True)
            minDuration,  maxDuration = getEventDuration(self.eventTypeId)
            if minDuration<=maxDuration:
                countRedDays = not QtGui.qApp.isExcludeRedDaysInEventLength()
                eventDuration = getEventLengthDays(begDate, endDate, countRedDays, self.eventTypeId)
                eventDurationErrorString = u'Указана длительность с учётом выходных: %s.'%formatNum(eventDuration, (u'день', u'дня', u'дней'))
                result = result and (eventDuration >= minDuration or
                                     self.checkValueMessage(u'Длительность должна быть не менее %s. %s'%(formatNum(minDuration, (u'дня', u'дней', u'дней')), eventDuration), False, self.edtEndDate))
                result = result and (maxDuration==0 or eventDuration <= maxDuration or
                                     self.checkValueMessage(u'Длительность должна быть не более %s. %s'%(formatNum(maxDuration, (u'дня', u'дней', u'дней')), eventDuration), False, self.edtEndDate))
            result = result and self.checkDiagnosticsDataEntered(begDate, endDate)
            result = result and self.checkActionsDateEnteredActuality(begDate, endDate, [self.tabStatus, self.tabDiagnostic, self.tabCure, self.tabMisc])
            result = result and self.checkActionsDataEntered([self.tabStatus, self.tabDiagnostic, self.tabCure, self.tabMisc], begDate, endDate)
        if self.isTabCashAlreadyLoad:
            result = result and self.tabCash.checkDataLocalContract()
        result = result and self.checkSerialNumberEntered()
        result = result and self.checkTabNotesReferral()

        if self.getFinalDiagnosisMKB()[0] is not None and self.getFinalDiagnosisMKB()[0] != u'' \
                and self.getFinalDiagnosisMKB()[0][0] == u'C' \
                and not QtGui.qApp.userHasRight(urOncoDiagnosisWithoutTNMS)\
                and QtGui.qApp.isTNMSVisible() and (self.getFinalDiagnosis().value('TNMS') is None or
                                forceString(self.getFinalDiagnosis().value('TNMS')) == ''):
            result = result and self.checkValueMessage(check_data_text_TNM, False, None)

        return result

    def checkMoreThanOneVisit(self):
        result = True
        record_list = self.modelDiagnostics.items()
        personId_list = []
        datePerson_list = []
        visitListFromModel = []
        for record in record_list:
            date = forceString(forceDate(record.value('endDate')))
            person_id = forceRef(record.value('person_id'))
            visit_id = forceRef(record.value('visit_id'))
            if visit_id:
                visitListFromModel.append(visit_id)
            datePerson_list.append((date, person_id))
            personId_list.append(person_id)
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        tableVisit = db.table('Visit')
        cond = [tableEvent['client_id'].eq(self.clientId), tableEvent['deleted'].eq(0)]
        rl = db.getRecordList(tableEvent, ['id'], where=db.joinAnd(cond))
        events_list = map(lambda r: forceRef(r.value('id')), rl)
        cond = [tableVisit['event_id'].inlist(events_list),
                tableVisit['id'].notInlist(visitListFromModel),
                tableVisit['deleted'].eq(0)]
        rl = db.getRecordList(tableVisit, ['id', 'date', 'person_id'], where=db.joinAnd(cond))
        for record in rl:
            date = forceString(forceDate(record.value('date')))
            person_id = forceRef(record.value('person_id'))
            datePerson_list.append((date, person_id))
            personId_list.append(person_id)
        tablePerson = db.table('Person')
        rl = db.getRecordList('Person', ['id', 'speciality_id'], where=tablePerson['id'].inlist(personId_list))
        personSpecMap = {}
        speciality_list = []
        for r in rl:
            person_id = forceRef(r.value('id'))
            speciality_id = forceRef(r.value('speciality_id'))
            personSpecMap[person_id] = speciality_id
            speciality_list.append(speciality_id)
        dateSpeciality = {}
        for dp in datePerson_list:
            date = dp[0]
            person_id = dp[1]
            t = (date, personSpecMap.get(person_id))
            c = dateSpeciality.setdefault(t, 0)
            c += 1
            dateSpeciality[t] = c
        tablerbSpeciality = db.table('rbSpeciality')
        rl = db.getRecordList('rbSpeciality', ['id', 'name'], where=tablerbSpeciality['id'].inlist(speciality_list))
        specIdNameMap = dict(map(lambda r: (forceRef(r.value('id')), forceString(r.value('name'))), rl))
        msg = u''
        for t, num in dateSpeciality.items():
            if num > 1:
                msg += u'%s, %s : %s посещений\n' % (t[0], specIdNameMap.get(t[1]), num)
        if msg:
            message = u'На следующие даты существует больше одного посещения врача с той же специальностью:\n' + msg
            result = self.checkValueMessage(message, True, self.tblFinalDiagnostics)
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

    def getMaxEndDateByDiagnostics(self):
        result = QtCore.QDate()
        for row, record in enumerate(self.modelDiagnostics.items()):
            diagnosisType = self.modelDiagnostics.diagnosisType(row)
            if diagnosisType != CF131Dialog.dfAccomp:
                endDate = forceDate(record.value('endDate'))
                if endDate.isNull():
                    return endDate
                if result.isNull() or result<endDate:
                    result = endDate
        return result

    def checkDiagnosticsDataEntered(self, begDate, endDate):
        if QtGui.qApp.userHasRight(urDoNotCheckResultAndMKB):
            return True

        for row, record in enumerate(self.modelDiagnostics.items()):
            if not self.checkDiagnosticDataEntered(begDate, endDate, row, record):
                return False
        return self.checkEventResult()

    def checkDiagnosticDataEntered(self, begDate, endDate, row, record):
        result = self.checkRowEndDate(begDate, endDate, row, record, self.tblFinalDiagnostics)
        rowSetDate = forceDate(record.value('setDate'))
        rowEndDate = forceDate(record.value('endDate'))
        eventPersonId = self.cmbPerson.value()
        specialityId = forceRef(record.value('speciality_id'))
        column = self.tblFinalDiagnostics.model().getColIndex('endDate')
        diagnosisTypeId = forceRef(record.value('diagnosisType_id'))
        result = result and (begDate <= rowSetDate or self.checkUpdateMessage(
            u'Датa назначения осмотра не указана или предшествует дате назначения события %s.\nИзменить дату назначения на %s?' %
            (forceString(begDate), forceString(begDate)),
            self.edtBegDate, self.tblFinalDiagnostics, rowSetDate, row, record.indexOf('rowSetDate')))
        if endDate and (self.modelDiagnostics.diagnosisTypeCol.ids[2] != diagnosisTypeId):
            result = result and (rowEndDate or self.checkInputMessage(
                u'дату выполнения в осмотре по специальности: %s' %
                (forceString(QtGui.qApp.db.translate('rbSpeciality', 'id', specialityId, 'name'))),
                True, self.tblFinalDiagnostics, row, column))
        if result and not rowEndDate.isNull() and eventPersonId and eventPersonId == forceRef(record.value('person_id')):
            if rowEndDate!=endDate:
                result = self.checkValueMessage(
                    u'Дата выполнения осмотра ответственным лицом должна совпадать с датой выполнения обращения',
                    True, self.tblFinalDiagnostics, row, column)
        # i3588: ~0015231
        # проверять результат для осмотров при условиях:
        # 1) выставлена дата окончания обращения
        # 2) диагноз является заключительным
        if endDate and diagnosisTypeId == 1:
            result = result and (forceRef(record.value('result_id')) or self.checkInputMessage(
                forceTr(u'результат', u'EventDiagnostic'),
                False, self.tblFinalDiagnostics, row, self.tblFinalDiagnostics.model().getColIndex('result_id')))
        return result

    def checkRowEndDate(self, begDate, endDate, row, record, widget):
        result = True
        column = record.indexOf('endDate')
        rowEndDate = forceDate(record.value('endDate'))
        if not rowEndDate.isNull():
            actuality = forceInt(record.value('actuality'))
            if rowEndDate>endDate:
                result = result and self.checkValueMessage(u'Дата выполнения должна быть не позже %s' % forceString(endDate), False, widget, row, column)
            lowDate = begDate.addMonths(-actuality)
            if rowEndDate < lowDate:
                result = result and self.checkValueMessage(u'Дата выполнения должна быть не раньше %s' % forceString(lowDate), False, widget, row, column)
        return result

    def checkSpecialityUsed(self, specialityId):
        cnt = self.availableSpecialities[specialityId]
        for i in xrange(self.modelDiagnostics.rowCount()):
                if self.modelDiagnostics.specialityId(i) == specialityId:
                    cnt -= 1
                    if cnt==0:
                        return True
        return False

    def checkSelectionGroupUsed(self, model, selectionGroup):
        if selectionGroup != 0:
            for item in model.items():
                if forceInt(item.value('selectionGroup')) == selectionGroup:
                    return True
        return False

    def getAvailableDiagnostics(self):
        if self.eventTypeId:
            records = QtGui.qApp.db.getRecordList(
                  'EventType_Diagnostic',
                  cols='speciality_id, sex, age, selectionGroup, defaultHealthGroup_id, defaultMedicalGroup_id, defaultMKB, actuality, visitType_id',
                  where='eventType_id=\'%d\'' % self.eventTypeId, order='id')
            available = []
            self.availableSpecialities = {}
            for record in records:
                specialityId = forceInt(record.value('speciality_id'))
                selectionGroup = forceInt(record.value('selectionGroup'))
                if not specialityId in self.availableSpecialities.keys():
                    self.availableSpecialities[specialityId] = 1
                else:
                    self.availableSpecialities[specialityId] += 1
                if self.recordAcceptable(record) \
                and not self.checkSpecialityUsed(specialityId) \
                and not self.checkSelectionGroupUsed(self.modelDiagnostics, selectionGroup)  \
                and selectionGroup <= 0:
                    available.append(self.newDiagnosticRecord(record, False))
            return available
        return []

    def canAddDiagnostic(self):
        available = self.getAvailableDiagnostics()
        if available:
            newMenu = QtGui.QMenu(self.mnuDiagnostics)
            for i, record in enumerate(available):
                specialityId = forceRef(record.value('speciality_id'))
                action = newMenu.addAction(specialityName(specialityId))
                action.setData( QtCore.QVariant(i) )
                self.connect(action, QtCore.SIGNAL('triggered()'), self.addBaseDiagnostic)
            self.actDiagnosticsAddBase.setMenu(newMenu)
            self.availableDiagnostics = available
            return True
        else:
            self.availableDiagnostics = []
            return False

    def addBaseDiagnostic(self):
        sender = self.sender()
        if isinstance(sender, QtGui.QAction):
            index = forceInt(sender.data())
            rowIndex = self.modelDiagnostics.rowCount()
            self.modelDiagnostics.insertRecord(rowIndex, self.availableDiagnostics[index])
            self.tblFinalDiagnostics.setCurrentIndex(self.modelDiagnostics.index(rowIndex, 0))

    def isRemovableDiagnostic(self, row):
        specialityId = self.modelDiagnostics.specialityId(row)
        ids = QtGui.qApp.db.getIdList('EventType_Diagnostic',
                                       where='eventType_id=\'%d\' AND selectionGroup<=\'0\' AND speciality_id=\'%d\'' % (self.eventTypeId, specialityId))
        return bool(ids)

    def checkActionTypeUsed(self, actionTypeId):
        return False

    def getDiagFilter(self, specialityId):
        result = self.mapSpecialityIdToDiagFilter.get(specialityId, None)
        if result == None:
            result = QtGui.qApp.db.translate('rbSpeciality', 'id', specialityId, 'mkbFilter')
            if result == None:
                result = ''
            else:
                result = forceString(result)
            self.mapSpecialityIdToDiagFilter[specialityId] = forceString(result)
        return result

    def checkDiagnosis(self, specialityId, MKB, isEx=False):
        diagFilter = self.getDiagFilter(specialityId)
        return checkDiagnosis(self, MKB, diagFilter, self.clientId, self.clientSex, self.clientAge, self.begDate(), self.endDate(), self.eventTypeId, isEx)

    def canChangeDiagnostic(self, row, strict=False):
        if strict:
            checkDiagChange = 0
        else:
            checkDiagChange = QtGui.qApp.checkDiagChange()
            if checkDiagChange == 2:
                return True

        result = True
        payStatus = self.modelDiagnostics.payStatus(row)
        if payStatus == CPayStatus.exposed:
            eventId  = self.itemId()
            personId = forceRef(self.modelDiagnostics.items()[row].value('person_id'))
            db = QtGui.qApp.db
            tableAccount = db.table('Account')
            tableAccountItem = db.table('Account_Item')
            tableVisit   = db.table('Visit')
            table = tableAccountItem.leftJoin(tableAccount, tableAccount['id'].eq(tableAccountItem['master_id']))
            table = table.leftJoin(tableVisit, tableVisit['id'].eq(tableAccountItem['visit_id']))
            cond = [ tableVisit['event_id'].eq(eventId),
                     tableVisit['person_id'].eq(personId),
                     tableAccount['exposeDate'].isNotNull()
                   ]
            idList = db.getIdList(table, tableAccount['id'].name(), where=cond)
            result = not idList
        elif payStatus == CPayStatus.payed:
            result = False

        if not result:
            if checkDiagChange == 1:
                message = u'Данная строка включена в счёт\nи её данные изменять нежелательно\nВы настаиваете на изменении?'
                result = QtGui.QMessageBox.critical(self, u'Внимание!', message, QtGui.QMessageBox.Yes|QtGui.QMessageBox.No, QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes
            else:
                message = u'Данная строка включена в счёт\nи её данные не могут быть изменены'
                QtGui.QMessageBox.critical(self, u'Внимание!', message)
        return result

    def getEventInfo(self, context):
        if not self.isTabCashAlreadyLoad:
            self.initTabCash(False)
        result = CEventEditDialog.getEventInfo(self, context)
        # инициализация свойств
        result._isPrimary = self.chkPrimary.isChecked()
        # инициализация таблиц
        result._actions = CActionInfoProxyList(context,
                [self.tabStatus.modelAPActions, self.tabDiagnostic.modelAPActions, self.tabCure.modelAPActions, self.tabMisc.modelAPActions],
                result)
        result._diagnosises = CDiagnosticInfoProxyList(context, [self.modelDiagnostics])
        return result

    def updateMesMKB(self):
        self.tabMes.setMKB(self.getFinalDiagnosisMKB()[0])
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
        date1 = QtCore.QDate(date)
        for row in xrange(self.modelDiagnostics.rowCount()):
            self.modelDiagnostics.setSetDate(row, date1)
        for row in xrange(self.modelActionsSummary.rowCount()):
            self.modelActionsSummary.setBegDate(row, date1)
        contractId = self.cmbContract.value()
        self.cmbContract.setBegDate(date1)
        self.cmbContract.setEndDate(date)
        self.cmbContract.setValue(contractId)
        self.cmbPerson.setEndDate(date1)
        self.updateResultFilter()
        self.setContract()
        if QtGui.qApp.isCheckMKB():
            self.updateMKB()

        self.updateModelsRetiredList()

    @QtCore.pyqtSlot(QtCore.QTime)
    def on_edtBegTime_timeChanged(self, time):
        self.tabNotes.updateReferralPeriod(self.edtBegDate.date())

    @QtCore.pyqtSlot(int)
    def on_cmbPerson_currentIndexChanged(self):
        self.setPersonId(self.cmbPerson.value())

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtEndDate_dateChanged(self, date):
        self.setContract()
        self.tabNotes.cmbClientPolicy.updatePolicy(date)
        if QtGui.qApp.isAutoClosed():
            self.chkIsClosed.setChecked(date != QtCore.QDate())

    @QtCore.pyqtSlot(int)
    def on_cmbWorkOrganisation_currentIndexChanged(self):
        self.UpdateWorkOrganisationInfo()

    @QtCore.pyqtSlot()
    def on_btnSelectWorkOrganisation_clicked(self):
        orgId = selectOrganisation(self, self.cmbWorkOrganisation.value(), False)
        self.cmbWorkOrganisation.update()
        if orgId:
            self.setIsDirty()
            self.cmbWorkOrganisation.setValue(orgId)

    @QtCore.pyqtSlot(int)
    def on_btnPrint_printByTemplate(self, templateId):
        if self.beforePrintTemplate(templateId) == -1:
            return
        context = CInfoContext()
        eventInfo = self.getEventInfo(context)
        data = {'event' : eventInfo, 'client': eventInfo.client}
        data['templateCounterValue'] = self.oldTemplates.get(templateId, '')
        actionsCols = [(0, 'type'), (1, 'directionDate'), (2,'begDate'),  (3,'endDate'), (5,'person'), (10, 'note')]
        actions = []
        for row in xrange(self.modelActionsSummary.rowCount()):
            action = {}
            for col, colName in actionsCols:
                action[colName] = forceString(self.modelActionsSummary.data(self.modelActionsSummary.index(row, col)))
            actions.append(action)
        data['actions'] = actions
        data['setDate']  = CDateInfo(self.edtBegDate.date())
        data['execDate'] = CDateInfo(self.edtEndDate.date())
        person = context.getInstance(CPersonInfo, self.cmbPerson.value())
        data['setPerson'] = person
        data['execPerson'] = person
        data['person'] = person
        QtGui.qApp.call(self, applyTemplate, (self, templateId, data))

    @QtCore.pyqtSlot()
    def on_mnuDiagnostics_aboutToShow(self):
        canRemove = False
        currentRow = self.tblFinalDiagnostics.currentIndex().row()
        if currentRow>=0 :
            canRemove = self.modelDiagnostics.isAccompDiagnostic(currentRow) or self.isRemovableDiagnostic(currentRow)
            canRemove = canRemove and self.modelDiagnostics.payStatus(currentRow) == 0
        self.actDiagnosticsAddBase.setEnabled(self.canAddDiagnostic())
        self.actDiagnosticsAddAccomp.setEnabled(True)
        self.actDiagnosticsRemove.setEnabled(canRemove)

    @QtCore.pyqtSlot()
    def on_actDiagnosticsAddAccomp_triggered(self):
        currentRow = self.tblFinalDiagnostics.currentIndex().row()
        if currentRow>=0 :
            currentRecord = self.modelDiagnostics.items()[currentRow]
            newRecord = self.modelDiagnostics.getEmptyRecord()
            newRecord.setValue('diagnosisType_id', QtCore.QVariant(self.modelDiagnostics.diagnosisTypeCol.ids[2]))
            newRecord.setValue('speciality_id', currentRecord.value('speciality_id'))
            newRecord.setValue('setDate', currentRecord.value('setDate'))
            newRecord.setValue('healthGroup_id', currentRecord.value('healthGroup_id'))
            newRecord.setValue('medicalGroup_id', currentRecord.value('medicalGroup_id'))
            self.modelDiagnostics.insertRecord(currentRow+1, newRecord)
            self.tblFinalDiagnostics.setCurrentIndex(self.modelDiagnostics.index(currentRow+1, newRecord.indexOf('MKB')))

    @QtCore.pyqtSlot()
    def on_actDiagnosticsRemove_triggered(self):
        currentRow = self.tblFinalDiagnostics.currentIndex().row()
        self.modelDiagnostics.removeRowEx(currentRow)

    @QtCore.pyqtSlot()
    def on_modelDiagnostics_diagnosisChanged(self):
        self.updateMesMKB()

    @QtCore.pyqtSlot()
    def on_modelDiagnostics_resultChanged(self):
        CEventEditDialog.defaultDiagnosticResultId[self.eventPurposeId] = self.modelDiagnostics.resultId()
        self.updateResultFilter()

    @QtCore.pyqtSlot(int)
    def on_cmbResult_currentIndexChanged(self):
        self.modelDiagnostics.setFinalResult(getResultIdByDiagnosticResultId(self.cmbResult.value()))


class CDiagnosisPerson(CActionPersonInDocTableColSearch):
    def setEditorData(self, editor, value, record):
        editor.setSpecialityId(forceRef(record.value('speciality_id')))
        super(CDiagnosisPerson, self).setEditorData(editor, value, record)


class CF131DiagnosticsModel(CInDocTableModel):
    __pyqtSignals__ = ('diagnosisChanged()',
                                'resultChanged()',
                      )
    MKB_allowed_morphology = ['C', 'D']

    def __init__(self, parent,  editable=True):
        CInDocTableModel.__init__(self, 'Diagnostic', 'id', 'event_id', parent)
        self._parent = parent
        self.isManualSwitchDiagnosis = QtGui.qApp.defaultIsManualSwitchDiagnosis()
        self.isMKBMorphology = QtGui.qApp.defaultMorphologyMKBIsVisible()
        self.characterIdForHandleDiagnosis = None
        self.columnHandleDiagnosis = None

        self.diagnosisTypeCol = self.addCol(CDiagnosisTypeCol(   u'Тип',           'diagnosisType_id', 5, ['1', '2', '9']))
        self.addCol(CRBInDocTableCol(    u'Специальность', 'speciality_id', 20, 'rbSpeciality'))
        self.addCol(CDiagnosisPerson( u'Врач', 'person_id', 20, 'vrbPerson', showFields=CRBComboBox.showName, order='name', prefferedWidth=250, parent=parent))
        self.colAssistant = self.addCol(CDiagnosisPerson(       u'Ассистент',     'assistant_id', 20, 'vrbPersonWithSpeciality', order = 'name', parent=parent))
        self.addCol(CDateInDocTableCol(  u'Назначен',      'setDate',     10))
        self.addCol(CDateInDocTableCol(  u'Выполнен',      'endDate',     10, canBeEmpty=True))
        self.addExtCol(CRBInDocTableCol( u'Место визита',  'scene_id',    10, 'rbScene', addNone=False, prefferedWidth=150), QtCore.QVariant.Int)
        self.addExtCol(CRBInDocTableCol( u'Тип визита',    'visitType_id', 10, 'rbVisitType', addNone=False, showFields=CRBComboBox.showCodeAndName), QtCore.QVariant.Int)
        self.addExtCol(CRBInDocTableCol(      u'Услуга',         'service_id', 10, 'rbService', prefferedWidth=300, showFields=CRBComboBox.showCodeAndName), QtCore.QVariant.Int)
        self.addCol(CEnumInDocTableCol(u'Состояние', 'status', 10, CActionType.retranslateClass(False).statusNames))
        self.addCol(CPolyclinicExtendedInDocTableCol(u'Место выполнения', 'org_id', 20))
        self.addCol(CRBInDocTableCol(    u'ГрЗд',          'healthGroup_id',     7, 'rbHealthGroup', addNone=False, showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(u'Группа здоровья')
        self.addCol(CRBInDocTableCol(    u'МедГр',         'medicalGroup_id',    7, 'rbMedicalGroup', addNone=False, showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(u'Медицинская группа')
        self.addExtCol(CICDExInDocTableCol(u'МКБ',           'MKB', 5), QtCore.QVariant.String)
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
        self.addCol(CRBInDocTableCol(    u'ДН',            'dispanser_id',       4, 'rbDispanser', showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(u'Диспансерное наблюдение')
        self.addCol(CRBLikeEnumInDocTableCol(u'СКЛ',       'sanatorium',         2, CHospitalInfo.names, showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(u'Потребность в санаторно-курортном лечении')
        self.addCol(CRBLikeEnumInDocTableCol(u'Госп',      'hospital',           2, CHospitalInfo.names, showFields=CRBComboBox.showCode, prefferedWidth=150)).setToolTip(u'Потребность в госпитализации')
        self.addCol(CRBInDocTableCol(forceTr(u'Результат', u'EventDiagnostic'),     'result_id',          4, 'rbDiagnosticResult', showFields=CRBComboBox.showNameAndCode, prefferedWidth=350))
        self.setEnableAppendLine(False)
        self.columnResult = self._mapFieldNameToCol.get('result_id')

        self.setEditable(editable)

    def addRecord(self, record):
        super(CF131DiagnosticsModel, self).addRecord(record)
        self.emitResultChanged()

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

    def getCloseOrMainDiagnosisTypeIdList(self):
        return [self.diagnosisTypeCol.codeToId(code) for code in ['1', '2']]

    def manualSwitchDiagnosis(self):
        return self.isManualSwitchDiagnosis

    def getEmptyRecord(self):
        result = CInDocTableModel.getEmptyRecord(self)
        result.append(QtSql.QSqlField('diagnosis_id',     QtCore.QVariant.Int))
        result.append(QtSql.QSqlField('defaultMKB',       QtCore.QVariant.String))
        result.append(QtSql.QSqlField('actuality',        QtCore.QVariant.Int))
        result.append(QtSql.QSqlField('selectionGroup',   QtCore.QVariant.Int))
        result.append(QtSql.QSqlField('visit_id',         QtCore.QVariant.Int))
        result.append(QtSql.QSqlField('scene_id',         QtCore.QVariant.Int))
        result.append(QtSql.QSqlField('visitType_id',     QtCore.QVariant.Int))
        result.append(QtSql.QSqlField('status',           QtCore.QVariant.Int))
        result.append(QtSql.QSqlField('org_id',           QtCore.QVariant.Int))
        if not result.contains('service_id'):
            result.append(QtSql.QSqlField('service_id',   QtCore.QVariant.Int))
        result.append(QtSql.QSqlField('payStatus',        QtCore.QVariant.Int))
        empty = not self.items()
        if empty:
            if self._parent.inheritResult == True:
                result.setValue('result_id', toVariant(CEventEditDialog.defaultDiagnosticResultId.get(self._parent.eventPurposeId)))
            else:
                result.setValue('result_id', toVariant(None))
        return result

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
                    if not (bool(mkb) and mkb[0] in CF131DiagnosticsModel.MKB_allowed_morphology):
                        result = (result & ~QtCore.Qt.ItemIsEditable)
        if not self.isEditable():
            result = (result & ~QtCore.Qt.ItemIsEditable)
        return result


    def cellReadOnly(self, index):
        if index.isValid():
            row = index.row()
            column = index.column()
            if self.diagnosisType(row) != 2:
                if column == 1:
                    return False
        return False


    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid() and role==QtCore.Qt.DisplayRole :
            row = index.row()
            column = index.column()
            # atronah: проверка на равенство индекса диагноза в массиве diagnosisTypeCol.ids значению '2'
            # При инициализации модели столбец self.diagnosisTypeCol заполняется списком [1, 2, 9], т.е. индекс=2 у типа '9', т.е. у сопутствующего
            # if self.diagnosisType(row) == 2:
            #     if 0 < column <= 7 :
            #         return QtCore.QVariant()
            if column == 3:
                record = self.items()[row]
                setDate = record.value('setDate').toDate()
                endDate = record.value('endDate').toDate()
                if not endDate.isNull() and endDate < setDate:
                    return QtCore.QVariant()

            if column == 9:
                record = self.items()[row]
                endDate = record.value('endDate').toDate()
                status = forceInt(record.value('status'))
                if not endDate.isNull() and not status in CActionType.retranslateClass(False).ignoreStatus:
                    record.setValue('status', toVariant(2))
                    self.emitCellChanged(row, 1)
                    return QtCore.QVariant(2)

        return CInDocTableModel.data(self, index, role)


    def setData(self, index, value, role=QtCore.Qt.EditRole):
        column = index.column()
        row = index.row()
        if not variantEq(self.data(index, role), value):
            if column == 0: # тип, может быть изменён всегда
                if forceInt(value) == self.diagnosisTypeCol.ids[0]:
                    for i, record in enumerate(self.items()):
                        if forceInt(record.value('diagnosisType_id')) == self.diagnosisTypeCol.ids[0]:
                            record.setValue('diagnosisType_id', toVariant(self.diagnosisTypeCol.ids[1]))
                            self.emitCellChanged(i, 0)
                            self.emit(QtCore.SIGNAL('diagnosisChanged()'))
            elif column == 1: # old: специальность, не меняется никогда | new: теперь меняем -> i3382
                pass
                # return False
            elif column == 2: # врач, изменяется всегда
                pass
            elif column == 3: # ассистент, изменяется всегда
                pass
            elif column == 4 or column == 5: # даты, меняются только если нет счёта
                if not QtCore.QObject.parent(self).canChangeDiagnostic(row, True):
                    return False
            elif column == 6:
                pass
            elif column == 13: # код МКБ
                if not QtCore.QObject.parent(self).canChangeDiagnostic(row):
                    return False
                newMKB = forceString(value)
                if not newMKB:
                    value = self.items()[row].value('defaultMKB')
                    newMKB = forceString(value)
                elif not QtCore.QObject.parent(self).checkDiagnosis(self.specialityId(row), newMKB):
                    return False
                value = toVariant(newMKB)
                self.updateCharacterByMKB(row, newMKB)
            else:
                if not QtCore.QObject.parent(self).canChangeDiagnostic(row):
                    return False
            result = CInDocTableModel.setData(self, index, value, role)
            if result:
                self.emit(QtCore.SIGNAL('diagnosisChanged()'))
            if row == 0 and column == self.columnResult:
                self.emitResultChanged()
            return result
        else:
            return True

    def resultId(self):
        items = self.items()
        if items:
            return forceRef(items[0].value('result_id'))
        else:
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
                return True
        return False

    def getFinalDiagnosis(self):
        finalDiagnosisTypeId = self.diagnosisTypeCol.ids[0]
        items = self.items()
        for item in items:
            diagnosisTypeId = forceRef(item.value('diagnosisType_id'))
            if diagnosisTypeId == finalDiagnosisTypeId:
                return item
        return None


    def diagnosisTypeId(self, row):
        return forceRef(self.items()[row].value('diagnosisType_id'))


    def diagnosisType(self, row):
        diagnosisTypeId = self.diagnosisTypeId(row)
        if diagnosisTypeId in self.diagnosisTypeCol.ids:
            return self.diagnosisTypeCol.ids.index(diagnosisTypeId)
        else:
            return -1


    def specialityId(self, row):
        return forceInt(self.items()[row].value('speciality_id'))


    def payStatus(self, row):
        return forceInt(self.items()[row].value('payStatus'))


    def isAccompDiagnostic(self, row):
        diagnosisType = self.diagnosisType(row)
        return diagnosisType == 2


    def removeRowEx(self, row):
        if QtCore.QObject.parent(self).canChangeDiagnostic(row, True):
            diagnosisType = self.diagnosisType(row)
            if diagnosisType == 2:
                self.removeRows(row, 1)
            else:
                i = row+1
                while i<len(self.items()) and self.diagnosisType(i) == 2:
                    i += 1
                self.removeRows(row, i-row)


    def setSetDate(self, row, date):
        self.items()[row].setValue('setDate',  toVariant(date))
        self.emitCellChanged(row, 3)


    def updateCharacterByMKB(self, row, MKB):
        characterIdList = getAvailableCharacterIdByMKB(MKB)
        item = self.items()[row]
        characterId = forceRef(item.value('character_id'))
        if (characterId in characterIdList) or (characterId == None and not characterIdList) :
            return
        if characterIdList:
            characterId = characterIdList[0]
        else:
            characterId = None
        item.setValue('character_id', toVariant(characterId))
        self.emitCellChanged(row, item.indexOf('character_id'))

    def emitResultChanged(self):
        self.emit(QtCore.SIGNAL('resultChanged()'))
