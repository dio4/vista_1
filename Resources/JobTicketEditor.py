# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from PyQt4.QtGui import QMessageBox

from Accounting.Utils import getContractInfo, isShowJobTickets
from Events.Action import ActionStatus, CAction, CActionType, CJobTicketActionPropertyValueType
from Events.ActionInfo import CCookedActionInfo
from Events.ActionPropertiesTable import CActionPropertiesTableModel
from Events.ActionTemplateSaveDialog import CActionTemplateSaveDialog
from Events.ActionsModel import fillActionRecord, getActionDefaultAmountEx, getActionDefaultContractId
from Events.AmbCardPage import CAmbCardDialog
from Events.ContractTariffCache import CContractTariffCache
from Events.CreateEvent import editEvent
from Events.EventInfo import CEventInfo
from Events.MapActionTypeToServiceIdList import CMapActionTypeIdToServiceIdList
from Events.Utils import CActionTemplateCache, checkTissueJournalStatus, checkTissueJournalStatusByActions, \
    getEventActionFinance, getEventFinanceId, payStatusText, recordAcceptable, setActionPropertiesColumnVisible
from HospitalBeds.models.MonitoringModel import CMonitoringModel
from KLADR.Utils import KLADRMatch
from Orgs.Utils import getOrgStructureName
from RefBooks.RBTissueType import TisssueTypeCounterResetType
from Registry.Utils import CClientInfo, getClientBanner, getClientInfo, getClientWork
from Resources.JobTicketInfo import CJobTicketWithActionsInfo, makeDependentActionIdList
from Resources.JobTicketProbeModel import CJobTicketProbeModel
from Resources.JobTicketReserveMixin import CJobTicketReserveMixin
from Resources.JobTypeActionsSelector import CJobTypeActionsSelector
from Resources.Utils import JobTicketStatus, getTissueTypeCounterValue
from TissueJournal.TissueInfo import CTakenTissueJournalInfo, CTissueTypeInfo
from TissueJournal.Utils import CTissueJournalTotalEditorDialog as CActionValuesEditor
from Ui_JobTicketEditor import Ui_JobTicketEditorDialog
from Users.Rights import urEditExecutionPlanAction, urLoadActionTemplate, urSaveActionTemplate
from library.ItemsListDialog import CItemEditorBaseDialog
from library.PrintInfo import CInfoContext
from library.PrintTemplates import additionalCustomizePrintButton, applyTemplate, customizePrintButton, \
    directPrintTemplate, getFirstPrintTemplate, getPrintButton
from library.TableModel import CBackRelationCol, CCol, CDateTimeCol, CDesignationCol, CEnumCol, CTableModel, CTextCol
from library.Utils import calcAgeTuple, forceBool, forceDate, forceDateTime, forceInt, forceRef, forceString, \
    forceStringEx, toVariant
from library.interchange import getComboBoxValue, getDatetimeEditValue, getLineEditValue, setComboBoxValue, \
    setDatetimeEditValue, setLineEditValue
from library.web import openInDicomViewer


class CJobTicketEditor(CItemEditorBaseDialog, Ui_JobTicketEditorDialog, CJobTicketReserveMixin):
    def __init__(self, parent):
        self.isPostUISet = False

        CItemEditorBaseDialog.__init__(self, parent, 'Job_Ticket')
        CJobTicketReserveMixin.__init__(self)

        self.mapActionIdToAction = {}
        self.mapActionIdToDateChangePossibility = {}

        self.addModels('Actions', CActionsModel(self, self.mapActionIdToAction))
        self.addModels(
            'ActionProperties',
            CActionPropertiesTableModel(self, CActionPropertiesTableModel.visibleInJobTicket)
        )
        self.addModels('JobTicketProbe', CJobTicketProbeModel(self))

        self.addBarcodeScanAction('actScanBarcode')

        self.isVipClient = None
        self.vipColor = CMonitoringModel.vipClientColor
        self.clientId = None
        self.clientSex = None
        self.clientAge = None
        self.actionStatusChanger = 0
        self.actionPersonChanger = 0
        self.actionDateChanger = 0
        self.jobStatusModifier = 0
        self.takenTissueRecord = None
        self.tissueExternalIdForProperty = None
        self.isTakenTissueChangable = False
        self._manualInputExternalId = None
        self._needUpdateTissueCounterId = False
        self.actionIdListCanDeleted = []
        self.isTakenTissue = False
        self.date = QtCore.QDate.currentDate()
        self.labelTemplate = getFirstPrintTemplate('clientTissueLabel')

        self.setupUi(self)
        self.edtBegDate.canBeEmpty(True)
        self.edtEndDate.canBeEmpty(True)
        self.cmbTissueType.setTable('rbTissueType')
        self.cmbTissueUnit.setTable('rbUnit')
        self.cmbTissueUnit.setRTF(True)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Выполнение работы')
        self.setModels(self.tblActions, self.modelActions, self.selectionModelActions)
        self.setModels(self.tblProps, self.modelActionProperties, self.selectionModelActionProperties)
        self.setModels(self.tblTreeProbe, self.modelJobTicketProbe, self.selectionModelJobTicketProbe)

        self.actualByTissueType = {}
        self.actionIdWithTissue = []
        self.eventEditor = None
        self.actionTemplateCache = None
        self.setupDirtyCather()

        self.btnPrint = getPrintButton(self, u'')

        self.btnPrint.setObjectName('btnPrint')
        customizePrintButton(self.btnPrint, 'jobTicket')
        self.connect(self.btnPrint, QtCore.SIGNAL('printByTemplate(int)'), self.on_printByTemplate)
        self.buttonBox.addButton(self.btnPrint, QtGui.QDialogButtonBox.ActionRole)

        self.tblActions.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

        # popupMenu tblActions
        self.actSelectAllRowActions = QtGui.QAction(u'Выделить все строки', self)
        self.tblActions.addPopupAction(self.actSelectAllRowActions)
        self.connect(self.actSelectAllRowActions, QtCore.SIGNAL('triggered()'), self.on_selectAllRowActions)

        self.actClearSelectionRowActions = QtGui.QAction(u'Снять выделение', self)
        self.tblActions.addPopupAction(self.actClearSelectionRowActions)
        self.connect(self.actClearSelectionRowActions, QtCore.SIGNAL('triggered()'), self.on_clearSelectionRowActions)

        self.actChangeValueActions = QtGui.QAction(u'Изменить данные', self)
        self.tblActions.addPopupAction(self.actChangeValueActions)
        self.connect(self.actChangeValueActions, QtCore.SIGNAL('triggered()'), self.on_changeValueActions)

        self.actChangeValueCurrentAction = QtGui.QAction(u'Изменить данные текущего элемента', self)
        self.actChangeValueCurrentAction.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F2))
        self.addAction(self.actChangeValueCurrentAction)
        self.connect(self.actChangeValueCurrentAction, QtCore.SIGNAL('triggered()'), self.on_changeValueCurrentAction)

        self.tblActions.addPopupSeparator()

        self.actAddActions = QtGui.QAction(u'Добавить действия', self)
        self.tblActions.addPopupAction(self.actAddActions)
        self.connect(self.actAddActions, QtCore.SIGNAL('triggered()'), self.on_addActions)

        self.actDelAddedActions = QtGui.QAction(u'Удалить', self)
        self.tblActions.addPopupAction(self.actDelAddedActions)
        self.connect(self.actDelAddedActions, QtCore.SIGNAL('triggered()'), self.on_removeSelectedActionRows)

        self.connect(self.tblActions.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.tblActionsPopupMenuAboutToShow)
        self.addAction(self.actScanBarcode)

        self.snapshotId = 0

        self.btnShowSnapshots.setVisible(QtGui.qApp.userHasRight('pictureViewAndFind'))
        self.btnFindSnapshots.setVisible(QtGui.qApp.userHasRight('pictureViewAndFind'))
        self.execPersonId = None

        self.btnLoadTemplate.setModelCallback(self.templateModel)

    def on_removeSelectedActionRows(self):
        self.tblActions.removeSelectedRows()
        self.resetProbesTree()

    def on_printByTemplate(self, templateId):
        if self.saveTakenTissueRecord():
            self.saveInternals(self.itemId())

        if self.modelJobTicketProbe.isExistsNotCheckedItems():
            self.modelJobTicketProbe.registrateProbe(forceCheck=True)

        context = CInfoContext()
        if templateId in [printAction.id for printAction in self.btnPrint.additionalActions()]:
            self.additionalPrint(context, templateId)
        else:
            jobTicketId = self.itemId()
            makeDependentActionIdList([jobTicketId])
            presetActions = tuple(self.mapActionIdToAction.values())
            data = {
                'jobTicket': context.getInstance(CJobTicketWithActionsInfo, jobTicketId, presetActions=presetActions)
            }
            applyTemplate(self, templateId, data)

    def additionalPrint(self, context, templateId):
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

        actionObj = self.modelActionProperties.action
        actionId = actionObj.getId()
        actionRecord = self.tblActions.currentItem()
        eventId = forceRef(actionRecord.value('event_id'))
        eventInfo = context.getInstance(CEventInfo, eventId)

        eventActions = eventInfo.actions
        eventActions._idList = [actionId]
        eventActions._items = [CCookedActionInfo(context, actionRecord, actionObj)]
        eventActions._loaded = True

        data = {
            'event': eventInfo,
            'action': eventInfo.actions[0],
            'client': eventInfo.client,
            'actions': eventActions,
            'currentActionIndex': 0,
            'tempInvalid': None
        }
        QtGui.qApp.restoreOverrideCursor()
        applyTemplate(self, templateId, data)

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        dateTime = forceDateTime(record.value('datetime'))
        begDateTime = forceDateTime(record.value('begDateTime'))
        self.date = dateTime.date()
        self.datetime = begDateTime if begDateTime.date().isValid() else dateTime
        self.lblDatetimeValue.setText(forceString(dateTime))
        setLineEditValue(self.edtLabel, record, 'label')
        setLineEditValue(self.edtNote, record, 'note')
        setComboBoxValue(self.cmbStatus, record, 'status')
        setDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'begDateTime')
        setDatetimeEditValue(self.edtEndDate, self.edtEndTime, record, 'endDateTime')

        self.setJobInfo(forceRef(record.value('master_id')))
        self.setDateTimeByStatus(self.cmbStatus.currentIndex())
        self.setupActions()
        if self.mapActionIdToAction.values():
            action = self.mapActionIdToAction.values()[0].getRecord()
            setDatetimeEditValue(self.edtBegDate, self.edtBegTime, action, 'begDate')
            setDatetimeEditValue(self.edtEndDate, self.edtEndTime, action, 'endDate')
        self.loadTakenTissue()
        self.setIsDirty(False)

        self.cmbStatus.setCurrentIndex(max(self.jobStatusModifier, self.cmbStatus.currentIndex()))

        self.isPostUISet = True

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(self.edtLabel, record, 'label')
        getLineEditValue(self.edtNote, record, 'note')
        getComboBoxValue(self.cmbStatus, record, 'status')
        getDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'begDateTime', True)
        getDatetimeEditValue(self.edtEndDate, self.edtEndTime, record, 'endDateTime', True)

        self.saveTakenTissueRecord()
        return record

    def afterSave(self):
        if self._needUpdateTissueCounterId is not None:
            db = QtGui.qApp.db
            db.selectExpr(db.func.getCounterValue(self._needUpdateTissueCounterId))
        super(CJobTicketEditor, self).afterSave()

    def saveTakenTissueRecord(self):
        if self.isTakenTissue:
            tissueTypeId = self.cmbTissueType.value()
            if tissueTypeId:
                db = QtGui.qApp.db
                tableTissueType = db.table('rbTissueType')
                tableTTJ = db.table('TakenTissueJournal')
                tmpRec = db.getRecordEx(tableTissueType, tableTissueType['issueExternalIdLimit'],
                                        tableTissueType['id'].eq(tissueTypeId))
                if tmpRec:
                    issueExternalIdLimit = forceInt(tmpRec.value('issueExternalIdLimit'))
                    if len(forceString(self.edtTissueExternalId.text())) > issueExternalIdLimit > 0:
                        QMessageBox.information(
                            None,
                            u'Неверный идентификатор',
                            u'Превышено количество символов в идентификаторе, максимально: %s' % issueExternalIdLimit,
                            QtGui.QMessageBox.Ok
                        )
                        return
                if self.takenTissueRecord:
                    if self.cmbStatus.currentIndex() > 0:
                        self.takenTissueRecord.setValue('datetimeTaken', toVariant(
                            QtCore.QDateTime(self.edtEndDate.date(), self.edtEndTime.time())))
                    db.updateRecord(tableTTJ, self.takenTissueRecord)
                    return True
                else:
                    newTTJ = tableTTJ.newRecord()
                    newTTJ.setValue('client_id', QtCore.QVariant(self.clientId))
                    newTTJ.setValue('tissueType_id', QtCore.QVariant(self.cmbTissueType.value()))
                    newTTJ.setValue('externalId', QtCore.QVariant(self.edtTissueExternalId.text()))
                    newTTJ.setValue('number', QtCore.QVariant(self.edtTissueNumber.text()))
                    newTTJ.setValue('amount', QtCore.QVariant(self.edtTissueAmount.value()))
                    newTTJ.setValue('unit_id', QtCore.QVariant(self.cmbTissueUnit.value()))
                    newTTJ.setValue(
                        'execPerson_id',
                        QtCore.QVariant(self.cmbTissueExecPerson.value() or QtGui.qApp.userId)
                    )
                    newTTJ.setValue('note', QtCore.QVariant(self.edtTissueNote.text()))
                    newTTJ.setValue(
                        'datetimeTaken',
                        QtCore.QVariant(QtCore.QDateTime(self.edtTissueDate.date(), self.edtTissueTime.time()))
                    )
                    db.insertRecord(tableTTJ, newTTJ)
                    self.takenTissueRecord = newTTJ
                    self.setTissueWidgetsEditable(False)
                    return True
        return False

    def saveInternals(self, id):
        takenTissueEnabled = self.isTakenTissue and bool(self.takenTissueRecord)
        for action in self.mapActionIdToAction.values():
            record = action.getRecord()
            actionId = forceRef(record.value('id'))
            actualByTissueTypeList, actionIdList = self.actualByTissueType.get(self.cmbTissueType.value(), ([], []))
            if takenTissueEnabled and actionId in actionIdList:
                record.setValue('takenTissueJournal_id', self.takenTissueRecord.value('id'))

            getComboBoxValue(self.cmbStatus, record, 'status')
            getDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'begDate', True)
            getDatetimeEditValue(self.edtEndDate, self.edtEndTime, record, 'endDate', True)
            action.save()

        if takenTissueEnabled:
            takenTissueJournalId = forceRef(self.takenTissueRecord.value('id'))
            checkTissueJournalStatus(takenTissueJournalId, fromJobTicketEditor=True)

    def fillPropertyValueForTakenTissue(self):
        if self.isTakenTissue and self.cmbTissueType.value():
            for action in self.mapActionIdToAction.values():
                record = action.getRecord()
                actionId = forceRef(record.value('id'))
                actualByTissueTypeList, actionIdList = self.actualByTissueType.get(self.cmbTissueType.value(), ([], []))
                if actionId in actionIdList:
                    actionType = action.getType()
                    propertyTypeList = [propertyType for propertyType in actionType.getPropertiesByName().values()
                                        if propertyType.typeName == u'Проба' and propertyType.visibleInJobTicket]
                    for propertyType in propertyTypeList:
                        property = action.getPropertyById(propertyType.id)
                        value = property.getValue()
                        if not value:
                            value = unicode(self.edtTissueExternalId.text()).lstrip('0')
                            property.setValue(value)
                            self.modelActionProperties.emitDataChanged()

    def checkDate(self):
        if self.cmbStatus.currentIndex() == JobTicketStatus.Done:  # 2
            if self.edtEndDate.date() < self.edtBegDate.date() or (
                            self.edtEndDate.date() == self.edtBegDate.date() and self.edtEndTime.time() < self.edtBegTime.time()):
                QtGui.QMessageBox.warning(
                    self,
                    u'Внимание',
                    u'Дата и время начала выполнения не может быть больше даты и времени окончания выполнения.\n',
                    QtGui.QMessageBox.Ok,
                    QtGui.QMessageBox.Ok
                )
                return False
        return True

    def checkDataEntered(self):
        result = True
        result = result and self.checkDate()
        result = result and self.checkMorphologyMKB()
        # FIXME: pirozhok, в некоторых случаях опустошал идентификатор. Вопрос почему?
        # На пустой идентификатор выскакивало предупреждение
        temp = self.edtTissueExternalId.text()
        self.setTissueExternalId()
        if len(self.edtTissueExternalId.text()) == 0:
            self.edtTissueExternalId.setText(temp)
        # END TODO
        if self.isTakenTissue:
            result = result and self.checkUniqueTissueExternalId()
        result = result and self.checkActionsValue()
        return result

    def checkActionsValue(self):
        def isNull(val, typeName):
            if val is None:
                return True
            if isinstance(val, basestring):
                if typeName == 'ImageMap':
                    return not 'object' in val
                if typeName == 'Html':
                    edt = QtGui.QTextEdit()
                    edt.setHtml(val)
                    val = edt.toPlainText()
                if not forceStringEx(val):
                    return True
            if type(val) == list:
                if len(val) == 0:
                    return True
            if isinstance(val, (QtCore.QDate, QtCore.QDateTime, QtCore.QTime)):
                return not val.isValid()
            return False

        actionsModel = self.modelActions
        for actionRow, actionId in enumerate(actionsModel.idList()):
            action = self.mapActionIdToAction[actionId]

            actionType = action.getType()
            propertyTypeList = actionType.getPropertiesById().items()
            propertyTypeList.sort(key=lambda x: (x[1].idx, x[0]))
            propertyTypeList = [x[1] for x in propertyTypeList if
                                x[1].applicable(self.clientSex, self.clientAge) and x[1].visibleInJobTicket]

            if action.getType().hasAssistant:
                assistantId = action.getAssistantId('assistant') \
                              or action.getAssistantId('assistant2') \
                              or action.getAssistantId('assistant3')
                if not assistantId:
                    dialogButtons = QtGui.QMessageBox.Yes
                    if action.getType().hasAssistant == 1:
                        dialogButtons |= QtGui.QMessageBox.Ignore
                    if QtGui.QMessageBox.Yes == QtGui.QMessageBox.warning(
                            self,
                            u'Внимание',
                            u'Ассистент не выбран.\n'
                            u'Для того, чтобы сохранить результат\n'
                            u'необходимо выбрать ассистента\n'
                            u'\n'
                            u'Перейти к выбору?',
                            dialogButtons,
                            defaultButton=QtGui.QMessageBox.Yes
                    ):
                        self.on_changeValueCurrentAction()
                        return False

            for row, propertyType in enumerate(propertyTypeList):
                penalty = propertyType.penalty
                needChecking = penalty > 0
                if needChecking:
                    skippable = penalty < 100
                    property = action.getPropertyById(propertyType.id)
                    if isNull(property._value, propertyType.typeName):
                        actionTypeName = action._actionType.name
                        propertyTypeName = propertyType.name
                        if actionRow:
                            self.tblActions.setCurrentIndex(actionsModel.model().createIndex(actionRow, 0))
                        if not self.checkValueMessage(u'Необходимо заполнить значение поля "%s" в действии "%s"' % (
                                propertyTypeName, actionTypeName), skippable, self.tblProps, row, 1):
                            return False
        return True

    def checkMorphologyMKB(self):
        if QtGui.qApp.defaultMorphologyMKBIsVisible():
            import re
            for row, actionId in enumerate(self.modelActions.idList()):
                action = self.mapActionIdToAction.get(actionId, None)
                if action:
                    actionType = action.getType()
                    record = action.getRecord()
                    defaultMKB = actionType.defaultMKB
                    isMorphologyRequired = actionType.isMorphologyRequired
                    morphologyMKB = forceString(record.value('morphologyMKB'))
                    status = forceInt(record.value('status'))
                    isValidMorphologyMKB = bool(re.match('M\d{4}/', morphologyMKB))
                    if not isValidMorphologyMKB and defaultMKB > 0 and isMorphologyRequired > 0:
                        if status == ActionStatus.WithoutResult and isMorphologyRequired == 2:
                            continue
                        skippable = True if isMorphologyRequired == 1 else False
                        message = u'Необходимо ввести корректную морфологию диагноза действия `%s`' % actionType.name
                        result = self.checkValueMessage(message, skippable, self.tblActions, row, column=4)
                        if not result:
                            return result
        return True

    def setJobInfo(self, jobId):
        db = QtGui.qApp.db
        record = db.getRecord('Job', ['orgStructure_id', 'jobType_id'], jobId)
        if record:
            jobTypeId = forceRef(record.value('jobType_id'))
            orgStructureId = forceRef(record.value('orgStructure_id'))
            self.lblOrgStructureValue.setText(getOrgStructureName(orgStructureId))
        else:
            jobTypeId = None

        jobTypeRec = db.getRecord('rbJobType', '*', jobTypeId)
        if jobTypeRec:
            self.lblJobTypeValue.setText(forceString(jobTypeRec.value('name')))
            self.actionStatusChanger = forceInt(jobTypeRec.value('actionStatusChanger'))
            self.actionPersonChanger = forceInt(jobTypeRec.value('actionPersonChanger'))
            self.actionDateChanger = forceInt(jobTypeRec.value('actionDateChanger'))
            self.jobStatusModifier = forceInt(jobTypeRec.value('jobStatusModifier'))

    def setupActions(self):
        db = QtGui.qApp.db
        tableJobTicket = db.table('Job_Ticket')
        tableAPJT = db.table('ActionProperty_Job_Ticket')
        tableAP = db.table('ActionProperty')
        tableAction = db.table('Action')
        tableActionType = db.table('ActionType')
        tablePerson = db.table('vrbPersonWithSpeciality')
        tableEvent = db.table('Event')
        tableClient = db.table('Client')

        queryTable = tableJobTicket.leftJoin(tableAPJT, tableAPJT['value'].eq(tableJobTicket['id']))
        queryTable = queryTable.leftJoin(tableAP, tableAP['id'].eq(tableAPJT['id']))
        queryTable = queryTable.leftJoin(tableAction, tableAction['id'].eq(tableAP['action_id']))
        queryTable = queryTable.leftJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
        queryTable = queryTable.leftJoin(tablePerson, tablePerson['id'].eq(tableAction['person_id']))
        queryTable = queryTable.leftJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
        queryTable = queryTable.leftJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))
        cols = [
            tableAction['id'].alias('actionId'),
            tableClient['id'].alias('clientId'),
            tableJobTicket['master_id'].alias('jobId')
        ]
        cond = [
            tableJobTicket['id'].eq(self.itemId()),
            tableAction['deleted'].eq(0),
            tableEvent['deleted'].eq(0),
            tableClient['deleted'].eq(0)
        ]

        actionIdList = []
        clientIdSet = set()
        for record in db.iterRecordList(queryTable, cols, cond, order=tableAction['id']):
            if isShowJobTickets(forceRef(record.value('jobId')), forceRef(record.value('actionId'))):
                actionIdList.append(forceRef(record.value('actionId')))
                clientIdSet.add(forceRef(record.value('clientId')))

        self.setClientId(list(clientIdSet)[0] if clientIdSet else None)
        self.setActionIdList(actionIdList)
        self.checkIsTakenTissue(actionIdList)

    def checkIsTakenTissue(self, actionIdList):
        db = QtGui.qApp.db
        tableAction = db.table('Action')
        tableActionType = db.table('ActionType')
        tableATTT = db.table('ActionType_TissueType')
        tableTissueType = db.table('rbTissueType')

        table = tableAction.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
        table = table.innerJoin(tableATTT, tableATTT['master_id'].eq(tableActionType['id']))
        cols = [
            tableAction['id'].alias('actionId'),
            tableActionType['id'].alias('actionTypeId'),
            tableATTT['id'],
            tableATTT['tissueType_id'],
            tableATTT['amount'],
            tableATTT['unit_id']
        ]
        cond = [
            tableAction['id'].inlist(actionIdList)
        ]
        recordList = db.getRecordList(table, cols, cond, isDistinct=True)
        isTakenTissue = bool(recordList)

        self.isTakenTissue = isTakenTissue
        self.grpTissue.setVisible(isTakenTissue)
        self.tabWidget.setTabEnabled(self.tabWidget.indexOf(self.tabProbes), isTakenTissue)
        self.btnFillPropertiesValue.setVisible(isTakenTissue)
        if isTakenTissue:
            tissueTypeList = []
            for record in recordList:
                tissueType = forceRef(record.value('tissueType_id'))
                actionId = forceRef(record.value('actionId'))
                actualByTissueTypeList, actionIdList = self.actualByTissueType.get(tissueType, (None, None))
                if actualByTissueTypeList:
                    actualByTissueTypeList.append(record)
                    actionIdList.append(actionId)
                else:
                    self.actualByTissueType[tissueType] = ([record], [actionId])
                if not tissueType in tissueTypeList:
                    tissueTypeList.append(tissueType)
                self.actionIdWithTissue.append(actionId)
            tmpFilter = db.joinAnd([
                self.cmbTissueType._filter,
                tableTissueType['id'].inlist(tissueTypeList)
            ]) if self.cmbTissueType._filter else tableTissueType['id'].inlist(tissueTypeList)
            self.cmbTissueType.setFilter(tmpFilter)
            if len(tissueTypeList) == 1:
                self.cmbTissueType.setValue(tissueTypeList[0])

    def checkSpecialityExists(self, cmbPersonFind, personId):
        specialityId = forceRef(QtGui.qApp.db.translate('Person', 'id', personId, 'speciality_id'))
        if not specialityId:
            cmbPersonFind.setSpecialityIndependents()

    def loadTakenTissue(self):
        if self.isTakenTissue:
            if self.takenTissueRecord:
                if not self.isTakenTissueChangable:
                    self.cmbTissueType.blockSignals(True)
                    self.edtTissueDate.blockSignals(True)
                    self.setTissueWidgetsEditable(False)
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
            else:
                datetimeTaken = self.datetime
                self.edtTissueDate.setDate(datetimeTaken.date())
                self.edtTissueTime.setTime(datetimeTaken.time())
                self.setTissueWidgetsEditable(True)
                execPersonId = QtGui.qApp.userId
                self.checkSpecialityExists(self.cmbTissueExecPerson, execPersonId)
                self.cmbTissueExecPerson.setValue(execPersonId)
            self.execPersonId = execPersonId

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
        self.btnFillPropertiesValue.setEnabled(val)

    def checkVipPerson(self, textBrowser):
        if self.isVipClient:
            textBrowser.setStyleSheet("background-color: %s;" % self.vipColor)
        else:
            textBrowser.setStyleSheet("")

    def setClientId(self, clientId):
        self.clientId = clientId
        if clientId:
            if u'онко' in forceString(
                    QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'infisCode')
            ):
                vipRecord = QtGui.qApp.db.getRecordEx(
                    QtGui.qApp.db.table('ClientVIP'),
                    [
                        QtGui.qApp.db.table('ClientVIP')['client_id'],
                        QtGui.qApp.db.table('ClientVIP')['color']
                    ],
                    [
                        QtGui.qApp.db.table('ClientVIP')['deleted'].eq(0),
                        QtGui.qApp.db.table('ClientVIP')['client_id'].eq(self.clientId)
                    ]
                )

                self.isVipClient = forceBool(vipRecord)
                if self.isVipClient:
                    self.vipColor = forceString(vipRecord.value('color'))

            self.txtClientInfoBrowser.setHtml(getClientBanner(clientId))
            self.checkVipPerson(self.txtClientInfoBrowser)
            db = QtGui.qApp.db
            table = db.table('Client')
            record = db.getRecord(table, 'sex, birthDate', clientId)
            if record:
                self.clientSex = forceInt(record.value('sex'))
                self.clientBirthDate = forceDate(record.value('birthDate'))
                self.clientAge = calcAgeTuple(self.clientBirthDate, self.date)
                cmbTissueTypeFilter = 'sex IN (0,%d)' % self.clientSex
                self.cmbTissueType.setFilter(cmbTissueTypeFilter)
            self.btnFindSnapshots.setEnabled(True)
        else:
            self.txtClientInfoBrowser.setText('')
            self.btnFindSnapshots.setEnabled(False)

    def setActionIdList(self, actionIdList):
        db = QtGui.qApp.db
        table = db.table('Action')
        takenTissueJournalId = None
        for actionRecord in db.iterRecordList(table, '*', table['id'].inlist(actionIdList)):
            actionId = forceRef(actionRecord.value('id'))
            if not takenTissueJournalId:
                takenTissueJournalId = forceRef(actionRecord.value('takenTissueJournal_id'))
            self.mapActionIdToAction[actionId] = CAction(record=actionRecord)
            self.mapActionIdToDateChangePossibility[actionId] = {
                'endDate': not forceDate(actionRecord.value('endDate')).isValid()
            }

        if takenTissueJournalId:
            self.takenTissueRecord = db.getRecord('TakenTissueJournal', '*', takenTissueJournalId)
            self.updateTakenTissueChangable()

        self.tblActions.setIdList(actionIdList)
        self.resetProbesTree()
        self.btnShowSnapshots.setEnabled(bool(actionIdList))

    def updateTakenTissueChangable(self):
        self.isTakenTissueChangable = False
        if self.takenTissueRecord:
            tissueTypeId = forceRef(self.takenTissueRecord.value('tissueType_id'))
            externalId = forceString(self.takenTissueRecord.value('externalId'))
            counterManualInput = forceBool(
                QtGui.qApp.db.translate('rbTissueType', 'id', tissueTypeId, 'counterManualInput')
            )
            # Не блокировать поля ввода, если разрешен ручной и идентификатор пуст
            # (блокировать, только если условие выше не выполняется, т.е. не разрешен ручной ввод или идентификатор не пуст)
            if counterManualInput and not externalId.strip():
                self.isTakenTissueChangable = True

    def addActionList(self, actionList):
        for action in actionList:
            record = action.getRecord()
            id = forceRef(record.value('id'))
            self.modelActions.idList().append(id)
            self.modelActions.recordCache().put(id, record)
        self.modelActions.reset()

    def setDateTime(self, edtDate, edtTime):
        now = QtCore.QDateTime.currentDateTime()
        edtDate.setDate(now.date())
        edtTime.setTime(now.time())

    def setDateTimeByStatus(self, status):
        begEnabled = True
        endEnabled = True
        if status == JobTicketStatus.Awaiting:  # 0
            if (not QtGui.qApp.userHasRight(urEditExecutionPlanAction)):
                begEnabled = False
                endEnabled = False
        elif status == JobTicketStatus.InProgress:  # !
            endEnabled = False
            if not self.edtBegDate.date():
                self.setDateTime(self.edtBegDate, self.edtBegTime)
        elif status == JobTicketStatus.Done:  # 2
            if not self.edtBegDate.date():
                self.setDateTime(self.edtBegDate, self.edtBegTime)
            if not self.edtEndDate.date():
                self.setDateTime(self.edtEndDate, self.edtEndTime)

        self.edtBegDate.setEnabled(begEnabled)
        self.edtBegTime.setEnabled(begEnabled)
        self.btnSetBegDateTime.setEnabled(begEnabled)
        self.edtEndDate.setEnabled(endEnabled)
        self.edtEndTime.setEnabled(endEnabled)
        self.btnSetEndDateTime.setEnabled(endEnabled)

    def cloneValues(self):
        idList = self.modelActions.idList()
        row = self.tblActions.currentIndex().row()
        actionId = idList[row]
        values = self.getPropValues(self.mapActionIdToAction[actionId])
        for row in xrange(row + 1, len(idList)):
            actionId = idList[row]
            self.setPropValues(self.mapActionIdToAction[actionId], values)

    def getPropValues(self, action):
        result = {}
        actionType = action.getType()
        propertyTypeList = actionType.getPropertiesById().values()
        for propertyType in propertyTypeList:
            if propertyType.applicable(self.clientSex, self.clientAge) and propertyType.visibleInJobTicket:
                name = propertyType.name
                typeName = propertyType.typeName
                tableName = propertyType.tableName
                value = action.getPropertyById(propertyType.id).getValue()
                result[(name, typeName, tableName)] = value
        return result

    def setPropValues(self, action, values):
        actionType = action.getType()
        propertyTypeList = actionType.getPropertiesById().values()
        for propertyType in propertyTypeList:
            if propertyType.applicable(self.clientSex, self.clientAge) and propertyType.visibleInJobTicket:
                name = propertyType.name
                typeName = propertyType.typeName
                tableName = propertyType.tableName
                value = values.get((name, typeName, tableName), None)
                if value is not None:
                    property = action.getPropertyById(propertyType.id)
                    property.setValue(value)

    def recountTissueExternalId(self, tissueTypeId=None, existCountValue=None, _manualInputExternalId=False):
        if self.takenTissueRecord:
            externaId = forceString(self.takenTissueRecord.value('externalId'))
            if externaId.strip():
                return externaId

        if not tissueTypeId:
            tissueTypeId = self.cmbTissueType.value()

        db = QtGui.qApp.db
        tableTTJ = db.table('TakenTissueJournal')
        date = self.edtTissueDate.date()
        if tissueTypeId and date.isValid():
            if _manualInputExternalId:
                return '' if existCountValue is None else existCountValue
            if existCountValue is None:
                cond = [tableTTJ['tissueType_id'].eq(tissueTypeId)]
                dateCond = self.getRecountExternalIdDateCond(tissueTypeId, date, tableTTJ)
                if dateCond:
                    cond.append(dateCond)
                existCountValue = db.getCount(tableTTJ, where=cond)
            existCountValue += 1
            self.tissueExternalIdForProperty = existCountValue
            return unicode(existCountValue).zfill(6)
        else:
            return ''

    def getRecountExternalIdDateCond(self, tissueTypeId, date, tableTTJ):
        db = QtGui.qApp.db
        counterResetType = forceInt(db.translate('rbTissueType', 'id', tissueTypeId, 'counterResetType'))
        if counterResetType == TisssueTypeCounterResetType.Daily:
            return tableTTJ['datetimeTaken'].dateEq(date)
        elif counterResetType == TisssueTypeCounterResetType.Weekly:
            begDate = QtCore.QDate(date.year(), date.month(), QtCore.QDate(date).addDays(-(date.dayOfWeek() - 1)).day())
            endDate = QtCore.QDate(begDate).addDays(6)
        elif counterResetType == TisssueTypeCounterResetType.Monthly:
            begDate = QtCore.QDate(date.year(), date.month(), 1)
            endDate = QtCore.QDate(date.year(), date.month(), date.daysInMonth())
        elif counterResetType == TisssueTypeCounterResetType.HalfYearly:
            begMonth = 1 if date.month() <= 6 else 7
            endDays = 30 if begMonth == 1 else 31
            begDate = QtCore.QDate(date.year(), begMonth, 1)
            endDate = QtCore.QDate(date.year(), begMonth + 5, endDays)
        elif counterResetType == TisssueTypeCounterResetType.Yearly:
            begDate = QtCore.QDate(date.year(), 1, 1)
            endDate = QtCore.QDate(date.year(), 12, 31)
        else:
            return None  # никогда
        return db.joinAnd([
            tableTTJ['datetimeTaken'].dateGe(begDate),
            tableTTJ['datetimeTaken'].dateLe(endDate)
        ])

    def checkUniqueTissueExternalId(self):
        if not bool(self.takenTissueRecord) or self.isTakenTissueChangable:
            tissueTypeId = self.cmbTissueType.value()
            if not tissueTypeId:
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
                tableTTJ = QtGui.qApp.db.table('TakenTissueJournal')
                cond = [
                    tableTTJ['deleted'].eq(0),
                    tableTTJ['tissueType_id'].eq(tissueTypeId),
                    tableTTJ['externalId'].eq(self.edtTissueExternalId.text())
                ]
                dateCond = self.getRecountExternalIdDateCond(tissueTypeId, date, tableTTJ)
                if dateCond:
                    cond.append(dateCond)
                record = QtGui.qApp.db.getRecordEx(tableTTJ, 'id', cond)
                if record and forceRef(record.value('id')):
                    return self.checkInputMessage(
                        u'другой идентификатор.\nТакой уже существует',
                        False,
                        self.edtTissueExternalId
                    )
        return True

    def isValidExternalId(self, needCountValueStr):
        if not needCountValueStr.isdigit():
            return self.checkInputMessage(u'корректный идентификатор.', False, self.edtTissueExternalId)
        return True

    def setTissueExternalId(self, existCountValue=None):
        if not self._manualInputExternalId:
            tissueCounterValue = getTissueTypeCounterValue(self.cmbTissueType.value())
            if tissueCounterValue is not None:
                self._needUpdateTissueCounterId = tissueCounterValue[0]
                externalIdValue = tissueCounterValue[1]
            else:
                externalIdValue = self.recountTissueExternalId(existCountValue=existCountValue,
                                                               _manualInputExternalId=self._manualInputExternalId)
        else:
            externalIdValue = self.recountTissueExternalId(existCountValue=existCountValue,
                                                           _manualInputExternalId=self._manualInputExternalId)
        self.edtTissueExternalId.setText(unicode(externalIdValue))
        if existCountValue is None and not self._manualInputExternalId:
            self.edtTissueNumber.setText(unicode(externalIdValue))
        else:
            numberValue = self.recountTissueExternalId(existCountValue=None,
                                                       _manualInputExternalId=False)
            self.edtTissueNumber.setText(unicode(numberValue))

    def recountTissueAmount(self):
        tissueType = self.cmbTissueType.value()
        actualByTissueTypeList, actionIdList = self.actualByTissueType.get(tissueType, ([], []))
        actionTypesList = []
        globalUnitId = None
        totalAmount = 0
        for actualRecord in actualByTissueTypeList:
            actionTypeId = forceRef(actualRecord.value('actionTypeId'))
            amount = forceInt(actualRecord.value('amount'))
            unitId = forceRef(actualRecord.value('unit_id'))
            if not actionTypeId in actionTypesList:
                actionTypesList.append(actionTypeId)
                totalAmount += amount
                if not globalUnitId:
                    globalUnitId = unitId
                else:
                    if unitId != globalUnitId:
                        continue
        self.edtTissueAmount.setValue(totalAmount)
        self.cmbTissueUnit.setValue(globalUnitId)
        self.cmbTissueUnit.setEnabled(not bool(globalUnitId))

    def on_selectAllRowActions(self):
        self.tblActions.selectAll()

    def on_clearSelectionRowActions(self):
        self.tblActions.clearSelection()

    def on_changeValueCurrentAction(self):
        itemId = self.tblActions.currentItemId()
        if itemId:
            self.on_changeValueActions(itemId)

    def on_changeValueActions(self, itemId=None):
        db = QtGui.qApp.db
        dlg = CActionValuesEditor(self)
        dlg.setVisibleJournalWidgets(False)
        dlg.setVisibleExtraAssistants(True)
        dlg.setStatusNames(CActionType.retranslateClass(False).statusNames)
        selectedIdList = self.tblActions.selectedItemIdList()
        lenSelectedIdList = len(selectedIdList)
        if lenSelectedIdList == 1 and itemId:
            tableAction = db.table('Action')
            tableActionType = db.table('ActionType')
            record = db.getRecordEx(
                table=tableAction.innerJoin(tableActionType, tableAction['actionType_id'].eq(tableActionType['id'])),
                cols=[
                    tableActionType['name'],
                    tableAction['person_id'],
                    tableAction['status'],
                    tableAction['MKB'],
                    tableAction['morphologyMKB'],
                    tableAction['assistant_id'],
                    tableAction['assistant2_id'],
                    tableAction['assistant3_id']
                ],
                where=[
                    tableActionType['deleted'].eq(0),
                    tableAction['deleted'].eq(0),
                    tableAction['id'].eq(itemId)
                ]
            )
            if record:
                dlg.setWindowTitle(forceString(record.value('name')))
                dlg.setPersonIdInAction(forceRef(record.value('person_id')))
                dlg.setAssistantInAction(forceInt(record.value('assistant_id')))
                dlg.setAssistantInAction2(forceInt(record.value('assistant2_id')))
                dlg.setAssistantInAction3(forceInt(record.value('assistant3_id')))
                dlg.setStatus(forceInt(record.value('status')))
                dlg.setMKB(forceString(record.value('MKB')))
                dlg.setMorphology(forceString(record.value('morphologyMKB')))
            dlg.updateIsChecked(True)

        if dlg.exec_():
            values = dlg.values()
            personIdInAction = values['personIdInAction']
            assistantIdInAction = values['assistantIdInAction']
            assistantIdInAction2 = values['assistantIdInAction2']
            assistantIdInAction3 = values['assistantIdInAction3']
            status = values['status']
            mkb = values['mkb']
            morphologyMKB = values['morphologyMKB']
            makeChanges = not status is None or bool(assistantIdInAction) or bool(assistantIdInAction2) or bool(
                assistantIdInAction3) or bool(personIdInAction) or bool(mkb) or (not morphologyMKB is None)
            if makeChanges:
                currentIndex = self.tblActions.currentIndex()
                checkItems = []
                for action in self.mapActionIdToAction.values():
                    record = action.getRecord()
                    actionId = forceRef(record.value('id'))
                    if actionId in selectedIdList:
                        if not status is None:
                            record.setValue('status', QtCore.QVariant(status))
                            if status in [ActionStatus.Done, ActionStatus.WithoutResult]:
                                endDate = forceDate(record.value('endDate'))
                                if not endDate.isValid():
                                    record.setValue('endDate', toVariant(QtCore.QDateTime.currentDateTime()))
                            elif status == ActionStatus.Cancelled:
                                record.setValue('endDate', toVariant(QtCore.QDateTime()))
                        if bool(personIdInAction):
                            record.setValue('person_id', QtCore.QVariant(personIdInAction))
                        if bool(assistantIdInAction):
                            record.setValue('assistant_id', toVariant(assistantIdInAction))
                        if bool(assistantIdInAction2):
                            record.setValue('assistant2_id', toVariant(assistantIdInAction2))
                        if bool(assistantIdInAction3):
                            record.setValue('assistant3_id', toVariant(assistantIdInAction3))
                        if bool(mkb):
                            record.setValue('MKB', QtCore.QVariant(mkb))
                        if not morphologyMKB is None:
                            record.setValue('morphologyMKB', QtCore.QVariant(morphologyMKB))

                        checkItems.append((record, action))
                        QtGui.qApp.db.updateRecord('Action', record)
                        self.modelActions.recordCache().put(actionId, record)

                checkTissueJournalStatusByActions(checkItems)
                self.modelActions.emitDataChanged()
                self.tblActions.setCurrentIndex(currentIndex)

    def on_addActions(self):
        db = QtGui.qApp.db
        tableAction = db.table('Action')

        jobTicketId = self.itemId()
        jobId = forceRef(db.translate('Job_Ticket', 'id', jobTicketId, 'master_id'))
        jobTypeId = forceRef(db.translate('Job', 'id', jobId, 'jobType_id'))

        actionTypeIdList = [action.getType().id for action in self.mapActionIdToAction.values()]
        dlg = CJobTypeActionsSelector(self, jobTypeId, actionTypeIdList)
        if dlg.exec_():
            actionTypeItemsList = dlg.checkedItems()
            if actionTypeItemsList:
                actionId = self.tblActions.currentItemId()
                eventId = forceRef(db.translate('Action', 'id', actionId, 'event_id'))
                currentActionCount = db.getCount(tableAction, tableAction['id'], tableAction['event_id'].eq(eventId))
                if not self.eventEditor:
                    self.creatEventPossibilities(eventId)
                date = QtCore.QDate.currentDate()
                actionList = []
                for additionalIdx, (actionTypeId, amount) in enumerate(actionTypeItemsList):
                    idx = additionalIdx + currentActionCount
                    action = self.addEventAction(eventId, actionTypeId, jobTicketId, date, idx, amount)
                    if action:
                        actionList.append(action)
                self.addActionList(actionList)

    def getJobTicketDate(self):
        return self.date

    def getDefaultAmountEx(self, actionType, record, action):
        return getActionDefaultAmountEx(self, actionType, record, action)

    def getDefaultContractId(self, actionTypeId, financeId, begDate, endDate, contractId):
        return getActionDefaultContractId(self, actionTypeId, financeId, begDate, endDate, contractId)

    def addEventAction(self, eventId, actionTypeId, jobTicketId, date, idx, amount):
        def checkActionTypeIdByTissueType(actionTypeId):
            tissueTypeId = forceRef(self.takenTissueRecord.value('tissueType_id'))
            tableATTT = QtGui.qApp.db.table('ActionType_TissueType')
            cond = [
                tableATTT['master_id'].eq(actionTypeId),
                tableATTT['tissueType_id'].eq(tissueTypeId)
            ]
            return bool(QtGui.qApp.db.getRecordEx(tableATTT, 'id', cond))

        def setTicketIdToAction(action, jobTicketId):
            propertyTypeList = action.getType().getPropertiesById().values() if action else []
            for propertyType in propertyTypeList:
                if isinstance(propertyType.valueType, CJobTicketActionPropertyValueType):
                    property = action.getPropertyById(propertyType.id)
                    property.setValue(jobTicketId)
                    return True
            return False

        db = QtGui.qApp.db
        record = db.table('Action').newRecord()
        fillActionRecord(self, record, actionTypeId)
        action = CAction(record=record)
        if setTicketIdToAction(action, jobTicketId):
            record.setValue('setPerson_id', QtCore.QVariant(QtGui.qApp.userId))
            if not amount is None:
                record.setValue('amount', QtCore.QVariant(amount))
            if self.takenTissueRecord and checkActionTypeIdByTissueType(actionTypeId):
                record.setValue('takenTissueJournal_id', self.takenTissueRecord.value('id'))
            actionId = action.save(eventId, idx)
            self.actionIdListCanDeleted.append(actionId)
            self.mapActionIdToAction[actionId] = action
            return action
        return None

    def removeCanDeletedId(self, actionId):
        if actionId in self.actionIdListCanDeleted:
            self.actionIdListCanDeleted.remove(actionId)
            del self.mapActionIdToAction[actionId]
            del self.mapActionIdToDateChangePossibility[actionId]

    def syncActionProperties(self, previousActionState, action):
        action._propertiesByName = dict(previousActionState._propertiesByName)
        action._propertiesById = dict(previousActionState._propertiesById)
        action._properties = list(previousActionState._properties)

    def tblActionsPopupMenuAboutToShow(self):
        currentIndex = self.tblActions.currentIndex()
        curentIndexIsValid = currentIndex.isValid()
        b = bool(self.tblActions.selectedItemIdList()) and curentIndexIsValid
        self.actClearSelectionRowActions.setEnabled(b)
        self.actChangeValueActions.setEnabled(b)

        # i3090: (pirozhok) убрал на время
        # удаление добаленных действий
        try:
            selected = set(self.tblActions.selectedItemIdList())
            exists = set(self.actionIdListCanDeleted)
            b = (exists ^ selected) & exists == exists ^ selected
            self.actDelAddedActions.setEnabled(b)
        except:
            pass

    def resetProbesTree(self):
        self.modelJobTicketProbe.resetCache()
        self.modelJobTicketProbe.setActionList(self.mapActionIdToAction.values(), force=True)
        self.modelJobTicketProbe.resetItems()
        self.tblTreeProbe.expandAll()

    def creatEventPossibilities(self, eventId):
        self.eventEditor = CFakeEventEditor(self, eventId)
        self.actionTemplateCache = CActionTemplateCache(self.eventEditor)

    @QtCore.pyqtSlot()
    def on_btnSetBegDateTime_clicked(self):
        self.setDateTime(self.edtBegDate, self.edtBegTime)

    @QtCore.pyqtSlot()
    def on_btnSetEndDateTime_clicked(self):
        self.setDateTime(self.edtEndDate, self.edtEndTime)

    @QtCore.pyqtSlot(int)
    def on_cmbStatus_currentIndexChanged(self, status):
        self.setDateTimeByStatus(status)
        if status == JobTicketStatus.Done:
            eventPersonCache = {}
            for actionId in self.mapActionIdToAction:
                action = self.mapActionIdToAction[actionId]
                record = action.getRecord()
                if self.actionStatusChanger:
                    record.setValue('status', QtCore.QVariant(self.actionStatusChanger - 1))
                if self.actionPersonChanger:
                    if self.actionPersonChanger == 1:
                        record.setValue('person_id', QtCore.QVariant(QtGui.qApp.userId))
                    elif self.actionPersonChanger == 2:
                        record.setValue('person_id', record.value('setPerson_id'))
                    elif self.actionPersonChanger == 3:
                        eventId = forceRef(record.value('event_id'))
                        eventPersonId = eventPersonCache.get(eventId, None)
                        if not eventPersonId:
                            eventPersonId = QtGui.qApp.db.translate('Event', 'id', eventId, 'execPerson_id')
                            eventPersonCache[eventId] = eventPersonId
                        record.setValue('person_id', eventPersonId)
                if self.actionDateChanger == 1 and self.mapActionIdToDateChangePossibility[actionId]['endDate']:
                    record.setValue(
                        'endDate',
                        toVariant(QtCore.QDateTime(self.edtEndDate.date(), self.edtEndTime.time()))
                    )
                self.modelActions.recordCache().put(forceRef(record.value('id')), record)
            self.modelActions.emitDataChanged()

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.edtBegTime.setEnabled(self.edtBegDate.isEnabled() and bool(date))

    @QtCore.pyqtSlot(QtCore.QTime)
    def on_edtEndTime_timeChanged(self, time):
        if self.isPostUISet:
            self.updateEndDateTime()

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtEndDate_dateChanged(self, date):
        if self.isPostUISet:
            self.updateEndDateTime()
            if self.edtEndDate.date().isNull():
                self.cmbStatus.setCurrentIndex(JobTicketStatus.Awaiting)
            elif self.cmbStatus.currentIndex() == JobTicketStatus.Awaiting:
                self.cmbStatus.setCurrentIndex(JobTicketStatus.Done)

    def updateEndDateTime(self):
        date, time = self.edtEndDate.date(), self.edtEndTime.time()
        self.edtEndTime.setEnabled(self.edtEndDate.isEnabled() and bool(date))
        if self.cmbStatus.currentIndex() == JobTicketStatus.Done:
            for actionId in self.mapActionIdToAction.keys():
                action = self.mapActionIdToAction[actionId]
                record = action.getRecord()
                if self.actionDateChanger == 1 and self.mapActionIdToDateChangePossibility[actionId]['endDate']:
                    record.setValue('endDate', toVariant(QtCore.QDateTime(date, time)))

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelActions_currentChanged(self, current, previous):
        row = current.row()
        if row >= 0:
            idList = self.modelActions.idList()
            actionId = idList[row]
            action = self.mapActionIdToAction[actionId]
            self.tblProps.model().setAction(action, self.clientId, self.clientSex, self.clientAge)
            setActionPropertiesColumnVisible(action.getType(), self.tblProps)
            self.tblProps.resizeRowsToContents()
            self.tblProps.setEnabled(True)
            self.btnCloneValues.setEnabled(row < len(idList) - 1)

            context = forceString(QtGui.qApp.db.translate('ActionType', 'id', action.getType().id, 'context'))
            additionalCustomizePrintButton(self, self.btnPrint, context)

            if not self.eventEditor:
                self.creatEventPossibilities(forceRef(action.getRecord().value('event_id')))

            if QtGui.qApp.userHasRight(urLoadActionTemplate) and action:
                self.btnLoadTemplate.setEnabled(True)
            else:
                self.btnLoadTemplate.setEnabled(False)
        else:
            self.tblProps.setEnabled(False)
            self.btnCloneValues.setEnabled(False)
            additionalCustomizePrintButton(self, self.btnPrint, '')

    @QtCore.pyqtSlot()
    def on_btnCloneValues_clicked(self):
        self.cloneValues()

    def templateModel(self):
        row = self.tblActions.currentIndex().row()
        if row >= 0:
            idList = self.modelActions.idList()
            actionId = idList[row]
            action = self.mapActionIdToAction[actionId]
            if QtGui.qApp.userHasRight(urLoadActionTemplate) and action:
                personId = forceRef(action.getRecord().value('person_id'))
                actionTemplateTreeModel = self.actionTemplateCache.getModel(
                    action.getType().id,
                    personId if personId else forceRef(action.getRecord().value('setPerson_id'))
                )
                return actionTemplateTreeModel
        return None

    @QtCore.pyqtSlot()
    def on_btnPrintTissueLabel_clicked(self):
        if self.saveTakenTissueRecord():
            self.saveInternals(self.itemId())

        if self.modelJobTicketProbe.isExistsNotCheckedItems():
            self.modelJobTicketProbe.registrateProbe(forceCheck=True)

        if self.takenTissueRecord:
            printer = QtGui.qApp.labelPrinter()
            if self.labelTemplate and printer:
                context = CInfoContext()
                takenTissueId = forceRef(self.takenTissueRecord.value('id'))
                date = QtCore.QDate.currentDate()
                data = {
                    'client': context.getInstance(CClientInfo, self.clientId, date),
                    'tissueType': context.getInstance(CTissueTypeInfo, self.cmbTissueType.value()),
                    'externalId': self.edtTissueExternalId.text(),
                    'takenTissue': context.getInstance(CTakenTissueJournalInfo, takenTissueId)
                }
                QtGui.qApp.call(self, directPrintTemplate, (self.labelTemplate[1], data, printer))

        if forceBool(QtGui.qApp.preferences.appPrefs.get('autoJobTicketEditing', False)):
            self.buttonBox.button(QtGui.QDialogButtonBox.Ok).click()

    @QtCore.pyqtSlot(int)
    def on_cmbTissueType_currentIndexChanged(self, index):
        self._manualInputExternalId = forceBool(
            QtGui.qApp.db.translate('rbTissueType', 'id', self.cmbTissueType.value(), 'counterManualInput')
        )
        self.edtTissueExternalId.setReadOnly(not self._manualInputExternalId)
        self.setTissueExternalId()
        self.recountTissueAmount()
        self.resetProbesTree()
        self.btnPrintTissueLabel.setEnabled(bool(self.cmbTissueType.value()))

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtTissueDate_dateChanged(self, date):
        if self._manualInputExternalId is None:
            self._manualInputExternalId = forceBool(
                QtGui.qApp.db.translate('rbTissueType', 'id', self.cmbTissueType.value(), 'counterManualInput')
            )
        self.setTissueExternalId()

    @QtCore.pyqtSlot()
    def on_actScanBarcode_triggered(self):
        if not self.edtTissueExternalId.isReadOnly():
            self.edtTissueExternalId.setFocus(QtCore.Qt.OtherFocusReason)
            self.edtTissueExternalId.selectAll()

    @QtCore.pyqtSlot()
    def on_btnFillPropertiesValue_clicked(self):
        self.fillPropertyValueForTakenTissue()

    @QtCore.pyqtSlot()
    def on_btnAmbCard_clicked(self):
        CAmbCardDialog(self, self.clientId).exec_()

    @QtCore.pyqtSlot(int)
    def on_btnLoadTemplate_templateSelected(self, templateId):
        if QtGui.qApp.userHasRight(urLoadActionTemplate):
            actionId = self.tblActions.currentItemId()
            action = self.mapActionIdToAction.get(actionId, None)
            if action:
                action.updateByTemplate(templateId)
                action.save(idx=forceRef(action.getRecord().value('idx')))
                self.modelActions.emitDataChanged()
                self.modelActionProperties.emitDataChanged()

    @QtCore.pyqtSlot()
    def on_btnSaveAsTemplate_clicked(self):
        if QtGui.qApp.userHasRight(urSaveActionTemplate):
            actionId = self.tblActions.currentItemId()
            action = self.mapActionIdToAction.get(actionId, None)
            if action:
                actionRecord = action.getRecord()
                if not self.eventEditor:
                    self.creatEventPossibilities(forceRef(actionRecord.value('event_id')))
                dlg = CActionTemplateSaveDialog(
                    self,
                    actionRecord,
                    action,
                    self.eventEditor.clientSex,
                    self.eventEditor.clientAge,
                    self.eventEditor.personId,
                    self.eventEditor.personSpecialityId
                )
                dlg.exec_()
                self.actionTemplateCache.reset(action.getType().id)

    @QtCore.pyqtSlot()
    def on_btnFindSnapshots_clicked(self):
        postfix = '?client_id=%s' % self.clientId
        openInDicomViewer(postfix)

    @QtCore.pyqtSlot()
    def on_btnShowSnapshots_clicked(self):
        postfix = '?action_id=%s' % self.tblActions.currentItemId()
        openInDicomViewer(postfix)

    @QtCore.pyqtSlot()
    def on_btnEditEvent_clicked(self):
        self.save()
        db = QtGui.qApp.db
        tableAction = db.table('Action')
        tableAP = db.table('ActionProperty')
        tableAPJT = db.table('ActionProperty_Job_Ticket')
        tableEvent = db.table('Event')
        tableJobTicket = db.table('Job_Ticket')

        queryTable = tableJobTicket
        queryTable = queryTable.innerJoin(tableAPJT, tableAPJT['value'].eq(tableJobTicket['id']))
        queryTable = queryTable.innerJoin(tableAP, [tableAP['id'].eq(tableAPJT['id']), tableAP['deleted'].eq(0)])
        queryTable = queryTable.innerJoin(
            tableAction, [tableAction['id'].eq(tableAP['action_id']), tableAction['deleted'].eq(0)]
        )
        queryTable = queryTable.innerJoin(
            tableEvent, [tableEvent['id'].eq(tableAction['event_id']), tableEvent['deleted'].eq(0)]
        )
        cond = [
            tableJobTicket['id'].eq(self._id),
            tableAction['deleted'].eq(0),
            tableEvent['deleted'].eq(0)
        ]
        eventIdList = db.getDistinctIdList(queryTable, tableEvent['id'], cond)

        if len(eventIdList) > 1:
            QtGui.QMessageBox.warning(
                self, u'Внимание!', u'По данной работе найдено несколько обращений.', QtGui.QMessageBox.Ok
            )

        if eventIdList:
            editEvent(self, eventIdList[0])
        else:
            QtGui.QMessageBox.warning(
                self, u'Внимание!', u'По данной работе не найдено обращения', QtGui.QMessageBox.Ok
            )

    def exec_(self):
        QtGui.qApp.setJTR(self)
        result = CItemEditorBaseDialog.exec_(self)
        try:
            if not result:
                self.delAllJobTicketReservations()
        except:
            QtGui.qApp.logCurrentException()
        QtGui.qApp.setJTR(None)
        QtGui.qApp.disconnectClipboard()
        return result


class CPayStatusColumn(CCol):
    def __init__(self, title, fields, defaultWidth, alignment, isRTF=False, **params):
        CCol.__init__(self, title, fields, defaultWidth, alignment, isRTF, **params)
        if not hasattr(QtGui.qApp, 'contactInfoMap'):
            QtGui.qApp.contactInfoMap = dict()

    def format(self, values):
        payStatus = forceInt(values[0])
        result = payStatusText(payStatus)
        contractId = forceRef(values[1])  # forceRef(QtGui.qApp.db.translate('Event', 'id', eventId, 'contract_id'))
        try:
            if not contractId in QtGui.qApp.contactInfoMap:
                contractInfo = getContractInfo(contractId)
                if contractInfo.isIgnorePayStatusForJobs:
                    result += u', %s' % contractInfo.resolution
                QtGui.qApp.contactInfoMap[contractId] = result
            else:
                result = QtGui.qApp.contactInfoMap[contractId]
        finally:
            if not contractId in QtGui.qApp.contactInfoMap:
                QtGui.qApp.contactInfoMap[contractId] = result

            return toVariant(result)


class CActionsModel(CTableModel):
    class CAssistantIdGetter(object):
        """
        Функтор, выполняющий роль хранилища и getter'а списка значений идентификаторов ассистентов по actionId.
        Создан для того, чтобы выдавать изменненые, но не сохраненные в базу данные
        (при условии, что изменения отражаются в sourceMap)
        """

        def __init__(self, sourceMap, assistantTypeCode):
            """
            :param sourceMap: ссылка на словарь вида {actionId : CAction} с обновляемыми данными.
            :param assistantTypeCode: код типа ассистента, id которого необходимо возвращать для указанного actionId
            """
            self._sourceMap = sourceMap
            self._assistantTypeCode = assistantTypeCode

        def __call__(self, actionId):
            """
            Собственно, сам функтор.

            :param actionId: id действия, для которого необходимо вернуть assistantId
            :return:
            """
            action = self._sourceMap.get(actionId, None)
            if action is not None:
                values = [action.getAssistantId(self._assistantTypeCode)]
            else:
                values = [None]
            return values

    # end of child-class CAssistantIdGetter


    def __init__(self, parent, actionsMap=None):
        """
        :param parent: владелец создаваемого объекта
        :param actionsMap: словарь {actionId : CAction} для актуализации вывода ассистентов
        """
        self._parent = parent
        self._actionsMap = actionsMap or {}

        fields = [
            CDesignationCol(u'Мероприятие', ['actionType_id'], ('ActionType', 'name'), 20),
            CPayStatusColumn(u'Оплата', ['payStatus', 'contract_id'], 20, 'l'),
            CEnumCol(u'Статус', ['status'], CActionType.retranslateClass(False).statusNames, 6),
            CDateTimeCol(u'Назначено', ['directionDate'], 20),
            CDesignationCol(u'Назначил', ['setPerson_id'], ('vrbPersonWithSpeciality', 'name'), 20),
            CDesignationCol(u'Ответственный', ['person_id'], ('vrbPersonWithSpeciality', 'name'), 20)
        ]

        # Добавление столбцов с ассистентами
        # FIXME: atronah: не обновляется значение после изменения его через F2 (диалоговый редактор),
        # так как здесь чтение из базы, в которую изменения еще не попали
        for assistantSuffix in [u'', u'2', u'3']:
            if self._actionsMap:
                valuesGetter = self.CAssistantIdGetter(self._actionsMap, u'assistant' + assistantSuffix)
            else:
                valuesGetter = None
            assistantTypeId = forceRef(QtGui.qApp.db.translate('rbActionAssistantType',
                                                               'code',
                                                               u'assistant' + assistantSuffix,
                                                               'id'))
            fields.append(CBackRelationCol(
                interfaceCol=CDesignationCol(
                    title=u'Ассистент' + assistantSuffix,
                    fields=['person_id'],
                    designationChain=('vrbPersonWithSpeciality', 'name'),
                    defaultWidth=20
                ),
                primaryKey='id',
                subTableName='Action_Assistant',
                subTableForeignKey='action_id',
                subTableCond='assistantType_id = %s' % assistantTypeId,
                alternativeValuesGetter=valuesGetter
            ))

        if QtGui.qApp.defaultMorphologyMKBIsVisible():
            fields.insert(2, CTextCol(u'МКБ', ['MKB'], 8))
            fields.insert(3, CTextCol(u'Морфология МКБ', ['morphologyMKB'], 14))
        CTableModel.__init__(self, parent, fields)
        self.loadField('*')
        self.setTable('Action', recordCacheCapacity=None)

    def deleteRecord(self, table, itemId):
        CTableModel.deleteRecord(self, table, itemId)
        self._parent.removeCanDeletedId(itemId)


u'''Классы и функции помогающие сэмитировать ситуацию добавления действия в редакторе.'''


class CFakeEventEditor(QtCore.QObject):
    ctOther = 0
    ctLocal = 1
    ctProvince = 2

    def __init__(self, parent, eventId):
        QtCore.QObject.__init__(self, parent)
        db = QtGui.qApp.db
        self._parent = parent
        self._id = eventId
        self._record = db.getRecord('Event', '*', eventId)

        self.eventTypeId = forceRef(self._record.value('eventType_id'))
        self.eventSetDateTime = forceDateTime(self._record.value('setDate'))
        self.eventDate = forceDate(self._record.value('execDate'))
        self.personId = forceRef(self._record.value('setPerson_id'))
        orgId = forceRef(self._record.value('org_id'))
        self.orgId = orgId if orgId else QtGui.qApp.currentOrgId()
        self.personSpecialityId = forceRef(db.translate('Person', 'id', self.personId, 'speciality_id'))

        self.contractId = forceRef(self._record.value('contract_id'))
        if self.contractId:
            self.eventFinanceId = forceRef(db.translate('Contract', 'id', self.contractId, 'finance_id'))
        else:
            self.eventFinanceId = getEventFinanceId(self.eventTypeId)

        self.clientId = forceRef(self._record.value('client_id'))
        self.clientInfo = getClientInfo(self.clientId)
        try:
            clientKLADRCode = self.clientInfo.regAddressInfo.KLADRCode
        except:
            clientKLADRCode = ''
        if KLADRMatch(clientKLADRCode, QtGui.qApp.defaultKLADR()):
            self.clientType = CFakeEventEditor.ctLocal
        elif KLADRMatch(clientKLADRCode, QtGui.qApp.provinceKLADR()):
            self.clientType = CFakeEventEditor.ctProvince
        else:
            self.clientType = CFakeEventEditor.ctOther
        self.clientSex = self.clientInfo.sexCode
        self.clientBirthDate = self.clientInfo.birthDate
        self.clientAge = calcAgeTuple(self.clientBirthDate, self.eventDate)

        workRecord = getClientWork(self.clientId)
        self.clientWorkOrgId = forceRef(workRecord.value('org_id')) if workRecord else None

        self.clientPolicyInfoList = []
        policyRecord = self.clientInfo.compulsoryPolicyRecord
        if policyRecord:
            self.clientPolicyInfoList.append(self.getPolicyInfo(policyRecord))
        policyRecord = self.clientInfo.voluntaryPolicyRecord
        if policyRecord:
            self.clientPolicyInfoList.append(self.getPolicyInfo(policyRecord))

        self.personCache = {}
        self.contractTariffCache = CContractTariffCache()

    def getPolicyInfo(self, policyRecord):
        if policyRecord:
            insurerId = forceRef(policyRecord.value('insurer_id'))
            policyTypeId = forceRef(policyRecord.value('policyType_id'))
        else:
            insurerId = None
            policyTypeId = None
        return insurerId, policyTypeId

    def getActionFinanceId(self, actionRecord):
        finance = getEventActionFinance(self.eventTypeId)
        if finance == 1:
            return self.eventFinanceId
        elif finance == 2:
            personId = forceRef(actionRecord.value('setPerson_id'))
            return self.getPersonFinanceId(personId) if personId else self.personFinanceId
        elif finance == 3:
            personId = forceRef(actionRecord.value('person_id'))
            return self.getPersonFinanceId(personId) if personId else self.personFinanceId
        else:
            return None

    def getPersonSSF(self, personId):
        key = personId, self.clientType
        result = self.personCache.get(key, None)
        if not result:
            db = QtGui.qApp.db
            tablePerson = db.table('Person')
            tableSpeciality = db.table('rbSpeciality')
            queryTable = tablePerson.leftJoin(tableSpeciality, tableSpeciality['id'].eq(tablePerson['speciality_id']))
            cols = [
                tablePerson['speciality_id'],
                tablePerson['finance_id'],
                tablePerson['tariffCategory_id'],
                tableSpeciality['service_id'],
                tableSpeciality['otherService_id'],
                tableSpeciality['provinceService_id']
            ]
            rec = db.getRecord(queryTable, cols, personId)
            if rec:
                specialityId = forceRef(rec.value('speciality_id'))
                financeId = forceRef(rec.value('finance_id'))
                tariffCategoryId = forceRef(rec.value('tariffCategory_id'))
                serviceId = forceRef(rec.value('service_id'))
                otherServiceId = forceRef(rec.value('otherService_id'))
                provinceServiceId = forceRef(rec.value('provinceService_id'))
                if self.clientType == CFakeEventEditor.ctOther and otherServiceId:
                    serviceId = otherServiceId
                elif self.clientType == CFakeEventEditor.ctProvince and provinceServiceId:
                    serviceId = provinceServiceId
                result = (specialityId, serviceId, financeId, tariffCategoryId)
            else:
                result = (None, None, None, None)
            self.personCache[key] = result
        return result

    def getDefaultMKBValue(self, defaultMKB, setPersonId):
        return '', ''

    def getSuggestedPersonId(self):
        return QtGui.qApp.userId if QtGui.qApp.userSpecialityId else self.personId

    def getUet(self, actionTypeId, personId, financeId, contractId):
        if not contractId:
            contractId = self.contractId
            financeId = self.eventFinanceId
        if contractId and actionTypeId:
            serviceIdList = CMapActionTypeIdToServiceIdList.getActionTypeServiceIdList(actionTypeId, financeId)
            tariffDescr = self.contractTariffCache.getTariffDescr(contractId, self)
            tariffCategoryId = self.getPersonTariffCategoryId(personId)
            uet = CContractTariffCache.getUet(tariffDescr.actionTariffMap, serviceIdList, tariffCategoryId)
            return uet
        return 0

    def getPersonFinanceId(self, personId):
        return self.getPersonSSF(personId)[2]

    def getPersonTariffCategoryId(self, personId):
        return self.getPersonSSF(personId)[3]

    def getEventTypeId(self):
        return self.eventTypeId

    def recordAcceptable(self, record):
        return recordAcceptable(self.clientSex, self.clientAge, record)
