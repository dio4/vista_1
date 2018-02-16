# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2016 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Accounting.Utils import getContractInfo, isShowJobTickets

from Events.Action import CAction, CActionType, CJobTicketActionPropertyValueType
from Events.ActionInfo import CCookedActionInfo
from Events.ActionPropertiesTable import CActionPropertiesTableModel
from Events.ActionsModel import fillActionRecord, getActionDefaultAmountEx, getActionDefaultContractId
from Events.ActionTemplateSaveDialog import CActionTemplateSaveDialog
from Events.AmbCardPage import CAmbCardDialog
from Events.ContractTariffCache import CContractTariffCache
from Events.EventInfo import CEventInfo
from Events.MapActionTypeToServiceIdList import CMapActionTypeIdToServiceIdList
from Events.CreateEvent import editEvent
from Events.Utils import \
    getEventActionFinance, getEventFinanceId, payStatusText, \
    recordAcceptable, setActionPropertiesColumnVisible, CActionTemplateCache
from HospitalBeds.models.MonitoringModel import CMonitoringModel

from KLADR.Utils import KLADRMatch

from library.interchange import getComboBoxValue, getDatetimeEditValue, \
    setComboBoxValue, setDatetimeEditValue
from library.ItemsListDialog import CItemEditorBaseDialog
from library.PrintInfo import CInfoContext
from library.PrintTemplates import additionalCustomizePrintButton, applyTemplate, customizePrintButton, \
    getPrintButton
from library.TableModel import CTableModel, CCol, CDateTimeCol, CDesignationCol, CEnumCol, CTextCol, \
    CBackRelationCol
from library.Utils import forceBool, forceDate, forceDateTime, forceInt, forceRef, forceString, \
    toVariant, calcAgeTuple

from Orgs.Utils import getOrgStructureName

from Registry.Utils import getClientBanner, getClientInfo, getClientWork

from Resources.JobTicketInfo import makeDependentActionIdList, CJobTicketWithActionsInfo
from Resources.JobTicketProbeModel2 import CJobTicketProbeModel, CJobTicketTreeActionItem
from Resources.JobTicketReserveMixin import CJobTicketReserveMixin

from Users.Rights import urLoadActionTemplate, urSaveActionTemplate, urEditExecutionPlanAction

from Ui_JobTicketEditor2 import Ui_JobTicketEditorDialog


class CJobTicketEditor2(CItemEditorBaseDialog, Ui_JobTicketEditorDialog, CJobTicketReserveMixin):
    def __init__(self, parent):
        self.isPostUISet = False
        CItemEditorBaseDialog.__init__(self, parent, 'Job_Ticket')
        CJobTicketReserveMixin.__init__(self)

        self.setupUi(self)

        self.clientSex = self.clientBirthDate = self.clientAge = self.isVipClient = self.date = self.datetime = \
            self.eventEditor = None
        self.vipColor = CMonitoringModel.vipClientColor
        self.modelJobTicketProbe = CJobTicketProbeModel(self, self.tblTreeProbe)
        self.selectionModelJobTicketProbe = QtGui.QItemSelectionModel(self.modelJobTicketProbe, self)
        self.modelActionProperties = CActionPropertiesTableModel(self, CActionPropertiesTableModel.visibleInJobTicket)
        self.selectionModelActionProperties = QtGui.QItemSelectionModel(self.modelActionProperties, self)
        self.setModels(self.tblTreeProbe, self.modelJobTicketProbe, self.selectionModelJobTicketProbe)
        self.setModels(self.tblProps, self.modelActionProperties, self.selectionModelActionProperties)

        self.selectionModelJobTicketProbe.currentRowChanged.connect(self.currentTreeItemChanged)
        self.modelJobTicketProbe.externalIdChanged.connect(self.externalIdChanged)

        self.btnPrint = getPrintButton(self, u'jobTicket')
        self.connect(self.btnPrint, QtCore.SIGNAL('printByTemplate(int)'), self.on_printByTemplate)
        self.buttonBox.addButton(self.btnPrint, QtGui.QDialogButtonBox.ActionRole)

        self.actionStatusChanger = self.actionPersonChanger = self.actionDateChanger = self.jobStatusModifier = 0

        self.btnLoadTemplate.setModelCallback(self.templateModel)

    def currentTreeItemChanged(self, current, previous):
        abort = False
        if not current.isValid() or current.row() < 0:
            abort = True
        else:
            item = current.internalPointer()
            if isinstance(item, CJobTicketTreeActionItem):
                action = item.action()
                self.tblProps.model().setAction(action, self.clientId, self.clientSex, self.clientAge)
                setActionPropertiesColumnVisible(action.getType(), self.tblProps)
                self.tblProps.resizeRowsToContents()
                self.tblProps.setEnabled(True)

                context = forceString(QtGui.qApp.db.translate('ActionType', 'id', action.getType().id, 'context'))
                additionalCustomizePrintButton(self, self.btnPrint, context)

                if not self.eventEditor:
                    self.createEventPossibilities(forceRef(action.getRecord().value('event_id')))
                self.btnLoadTemplate.setEnabled(True)
            else:
                abort = True

        if abort:
            self.btnLoadTemplate.setEnabled(False)
            self.tblProps.setEnabled(False)
            additionalCustomizePrintButton(self, self.btnPrint, '')

    def externalIdChanged(self):
        if self.cmbStatus.currentIndex() == 0:  # ожидается
            self.cmbStatus.setCurrentIndex(1)  # выполняется

    def on_removeSelectedActionRows(self):
        self.tblActions.removeSelectedRows()
        self.resetProbesTree()

    def on_printByTemplate(self, templateId):
        context = CInfoContext()
        if templateId in [printAction.id for printAction in self.btnPrint.additionalActions()]:
            self.additionalPrint(context, templateId)
        else:
            jobTicketId = self.itemId()
            makeDependentActionIdList([jobTicketId])
            presetActions = tuple(self.modelJobTicketProbe.actionList())
            jobTicketInfo = context.getInstance(CJobTicketWithActionsInfo, jobTicketId, presetActions=presetActions)
            data = {'jobTicket': jobTicketInfo}
            applyTemplate(self, templateId, data)

    def additionalPrint(self, context, templateId):
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

        item = self.tblTreeProbe.currentIndex().internalPointer()
        actionObj = item.action()
        actionId = actionObj.getId()
        actionRecord = actionObj.getRecord()
        eventId = forceRef(actionRecord.value('event_id'))
        eventInfo = context.getInstance(CEventInfo, eventId)

        eventActions = eventInfo.actions
        eventActions._idList = [actionId]
        eventActions._items = [CCookedActionInfo(context, actionRecord, actionObj)]
        eventActions._loaded = True

        action = eventInfo.actions[0]
        data = {
            'event': eventInfo,
            'action': action,
            'client': eventInfo.client,
            'actions': eventActions,
            'currentActionIndex': 0,
            'tempInvalid': None
        }
        QtGui.qApp.restoreOverrideCursor()
        applyTemplate(self, templateId, data)

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)

        self.setJobInfo(forceRef(record.value('master_id')))

        dateTime = forceDateTime(record.value('datetime'))
        begDateTime = forceDateTime(record.value('begDateTime'))

        self.lblDatetimeValue.setText(forceString(dateTime))
        setDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'begDateTime')
        setDatetimeEditValue(self.edtEndDate, self.edtEndTime, record, 'endDateTime')
        setComboBoxValue(self.cmbStatus, record, 'status')

        if self.cmbStatus.currentIndex() == 2:
            self.modelJobTicketProbe.setEditable(False)
            self.edtBegDate.setEnabled(False)
            self.edtBegTime.setEnabled(False)
            self.edtEndDate.setEnabled(False)
            self.edtEndTime.setEnabled(False)
            self.btnSetBegDateTime.setEnabled(False)
            self.btnSetEndDateTime.setEnabled(False)
            self.cmbStatus.setEnabled(False)

        self.date = dateTime.date()
        self.datetime = begDateTime if begDateTime.date().isValid() else dateTime

        clients, actions = self.getActions()
        self.modelJobTicketProbe.setActionIdList(actions)

        self.cmbStatus.setCurrentIndex(max(self.jobStatusModifier, self.cmbStatus.currentIndex()))

        if clients:
            self.setClientId(clients[0])

            self.setIsDirty(False)
        self.isPostUISet = True

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getComboBoxValue(self.cmbStatus, record, 'status')
        getDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'begDateTime', True)
        getDatetimeEditValue(self.edtEndDate, self.edtEndTime, record, 'endDateTime', True)

        self.saveTakenTissueRecords()

        return record

    def saveTakenTissueRecords(self):
        self.modelJobTicketProbe.save(self.clientId, '000', self.cmbStatus.currentIndex(), QtCore.QDateTime(self.edtEndDate.date(), self.edtEndTime.time()))

    def checkDate(self):
        if self.cmbStatus.currentIndex() == 2 and self.edtEndDate.date() < self.edtBegDate.date() or \
                (self.edtEndDate.date() == self.edtBegDate.date() and self.edtEndTime.time() < self.edtBegTime.time()):
            QtGui.QMessageBox().warning(
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
        # result = result and self.checkActionsValue()
        return result

    # def checkActionsValue(self):
    #     def isNull(val, typeName):
    #         if val is None:
    #             return True
    #         if isinstance(val, basestring):
    #             if typeName == 'ImageMap':
    #                 return not 'object' in val
    #             if typeName == 'Html':
    #                 edt = QtGui.QTextEdit()
    #                 edt.setHtml(val)
    #                 val = edt.toPlainText()
    #             if not forceStringEx(val):
    #                 return True
    #         if type(val) == list:
    #             if len(val) == 0:
    #                 return True
    #         if isinstance(val, (QtCore.QDate, QtCore.QDateTime, QtCore.QTime)):
    #             return not val.isValid()
    #         return False
    #
    #     actionsModel = self.modelActions
    #     for actionRow, actionId in enumerate(actionsModel.idList()):
    #         action = self.mapActionIdToAction[actionId]
    #
    #         actionType = action.getType()
    #         propertyTypeList = actionType.getPropertiesById().items()
    #         propertyTypeList.sort(key=lambda x: (x[1].idx, x[0]))
    #         propertyTypeList = [x[1] for x in propertyTypeList if
    #                             x[1].applicable(self.clientSex, self.clientAge) and x[1].visibleInJobTicket]
    #
    #         #            actionEndDate = forceDate(action.getRecord().value('endDate'))
    #
    #         if action.getType().hasAssistant:
    #             assistantId = action.getAssistantId('assistant') \
    #                           or action.getAssistantId('assistant2') \
    #                           or action.getAssistantId('assistant3')
    #             if not assistantId:
    #                 dialogButtons = QtGui.QMessageBox.Yes
    #                 if action.getType().hasAssistant == 1:
    #                     dialogButtons |= QtGui.QMessageBox.Ignore
    #                 if QtGui.QMessageBox.Yes == QtGui.QMessageBox().warning(self,
    #                                                                         u'Внимание',
    #
    #                                                                         u'Ассистент не выбран.\n'
    #                                                                         u'Для того, чтобы сохранить результат\n'
    #                                                                         u'необходимо выбрать ассистента\n'
    #                                                                         u'\n'
    #                                                                         u'Перейти к выбору?',
    #
    #                                                                         dialogButtons,
    #                                                                         defaultButton=QtGui.QMessageBox.Yes):
    #                     self.on_changeValueCurrentAction()
    #                     return False
    #
    #         for row, propertyType in enumerate(propertyTypeList):
    #             penalty = propertyType.penalty
    #             needChecking = penalty > 0
    #             if needChecking:
    #                 skippable = penalty < 100
    #                 property = action.getPropertyById(propertyType.id)
    #                 if isNull(property._value, propertyType.typeName):
    #                     actionTypeName = action._actionType.name
    #                     propertyTypeName = propertyType.name
    #                     if actionRow:
    #                         self.tblActions.setCurrentIndex(actionsModel.model().createIndex(actionRow, 0))
    #                     if not self.checkValueMessage(u'Необходимо заполнить значение свойства "%s" в действии "%s"' % (
    #                             propertyTypeName, actionTypeName), skippable, self.tblProps, row, 1):
    #                         return False
    #     return True

    def getActions(self):
        db = QtGui.qApp.db
        table = db.table('Job_Ticket')
        tableAPJT = db.table('ActionProperty_Job_Ticket')
        tableAP = db.table('ActionProperty')
        tableAction = db.table('Action')
        tableActionType = db.table('ActionType')
        tablePerson = db.table('vrbPersonWithSpeciality')
        tableEvent = db.table('Event')
        tableClient = db.table('Client')

        queryTable = table
        queryTable = queryTable.leftJoin(tableAPJT, tableAPJT['value'].eq(table['id']))
        queryTable = queryTable.leftJoin(tableAP, tableAP['id'].eq(tableAPJT['id']))
        queryTable = queryTable.leftJoin(tableAction, tableAction['id'].eq(tableAP['action_id']))
        queryTable = queryTable.leftJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
        queryTable = queryTable.leftJoin(tablePerson, tablePerson['id'].eq(tableAction['person_id']))
        queryTable = queryTable.leftJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
        queryTable = queryTable.leftJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))

        cond = [
            table['id'].eq(self.itemId()),
            tableAction['deleted'].eq(0),
            tableEvent['deleted'].eq(0),
            tableClient['deleted'].eq(0),
        ]

        order = 'Action.id'

        actionIdList = []
        clientIdSet = set()
        fields = 'Action.id AS actionId, Client.id AS clientId, Job_Ticket.master_id AS jobId'
        records = db.getRecordList(queryTable, fields, cond, order)
        for record in records:
            if isShowJobTickets(record.value('jobId'), record.value('actionId')):
                actionIdList.append(forceRef(record.value('actionId')))
                clientIdSet.add(forceRef(record.value('clientId')))
        return list(clientIdSet), actionIdList

    def checkVipPerson(self, textBrowser):
        if self.isVipClient:
            textBrowser.setStyleSheet("background-color: %s;" % self.vipColor)
        else:
            textBrowser.setStyleSheet("")

    def setClientId(self, clientId):
        self.clientId = clientId
        if clientId:
            if u'онко' in forceString(QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'infisCode')):
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

                self.isVipClient = forceBool(vipRecord);
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
        else:
            self.txtClientInfoBrowser.setText('')

    def setDateTime(self, edtDate, edtTime):
        now = QtCore.QDateTime.currentDateTime()
        edtDate.setDate(now.date())
        edtTime.setTime(now.time())

    def setDateTimeByStatus(self, status):
        begEnabled = True
        endEnabled = True
        if status == 0:
            if not QtGui.qApp.userHasRight(urEditExecutionPlanAction):
                begEnabled = False
                endEnabled = False
        elif status == 1:
            endEnabled = False
            if not self.edtBegDate.date():
                self.setDateTime(self.edtBegDate, self.edtBegTime)
        elif status == 2:
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

    def getJobTicketDate(self):
        return self.date

    def getDefaultAmountEx(self, actionType, record, action):
        return getActionDefaultAmountEx(self, actionType, record, action)

    def getDefaultContractId(self, actionTypeId, financeId, begDate, endDate, contractId):
        return getActionDefaultContractId(self, actionTypeId, financeId, begDate, endDate, contractId)

    def setJobInfo(self, jobId):
        db = QtGui.qApp.db
        record = db.getRecord('Job', '*', jobId)
        orgStructureId = forceRef(record.value('orgStructure_id'))
        jobTypeId = forceRef(record.value('jobType_id'))
        self.lblOrgStructureValue.setText(getOrgStructureName(orgStructureId))

        jobTypeRec = db.getRecord('rbJobType', '*', jobTypeId)
        if jobTypeRec:
            self.lblJobTypeValue.setText(forceString(jobTypeRec.value('name')))
            self.actionStatusChanger = forceInt(jobTypeRec.value('actionStatusChanger'))
            self.actionPersonChanger = forceInt(jobTypeRec.value('actionPersonChanger'))
            self.actionDateChanger = forceInt(jobTypeRec.value('actionDateChanger'))
            self.jobStatusModifier = forceInt(jobTypeRec.value('jobStatusModifier'))

    def addEventAction(self, eventId, actionTypeId, jobTicketId, date, idx, amount):
        def checkActionTypeIdByTissueType(actionTypeId):
            tissueTypeId = forceRef(self.takenTissueRecord.value('tissueType_id'))
            table = QtGui.qApp.db.table('ActionType_TissueType')
            cond = [table['master_id'].eq(actionTypeId),
                    table['tissueType_id'].eq(tissueTypeId)]
            return bool(QtGui.qApp.db.getRecordEx(table, 'id', cond))

        def setTicketIdToAction(action, jobTicketId):
            propertyTypeList = action.getType().getPropertiesById().values() if action else []
            for propertyType in propertyTypeList:
                if type(propertyType.valueType) == CJobTicketActionPropertyValueType:
                    property = action.getPropertyById(propertyType.id)
                    property.setValue(jobTicketId)
                    return True
            return False

        db = QtGui.qApp.db
        record = db.table('Action').newRecord()
        fillActionRecord(self, record, actionTypeId)
        action = CAction(record=record)
        if setTicketIdToAction(action, jobTicketId):
            #            record.setValue('directionDate', QVariant(date))
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

    def createEventPossibilities(self, eventId):
        self.eventEditor = CFakeEventEditor(self, eventId)
        self.actionTemplateCache = CActionTemplateCache(self.eventEditor)

    @QtCore.pyqtSlot()
    def on_btnSetBegDateTime_clicked(self):
        self.setDateTime(self.edtBegDate, self.edtBegTime)

    @QtCore.pyqtSlot()
    def on_btnSetEndDateTime_clicked(self):
        self.setDateTime(self.edtEndDate, self.edtEndTime)

    @QtCore.pyqtSlot(int)
    def on_cmbStatus_currentIndexChanged(self, index):
        self.setDateTimeByStatus(index)
        if index == 2:  # закончено
            eventPersonCache = {}
            for action in self.modelJobTicketProbe.actionList():  # type: CAction
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
                if self.actionDateChanger == 1 and not forceDate(record.value('endDate')).isValid():
                    record.setValue('endDate',
                                    toVariant(QtCore.QDateTime(self.edtEndDate.date(), self.edtEndTime.time())))


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
                self.cmbStatus.setCurrentIndex(0)
            elif self.cmbStatus.currentIndex() == 0:
                self.cmbStatus.setCurrentIndex(2)

    def updateEndDateTime(self):
        date, time = self.edtEndDate.date(), self.edtEndTime.time()
        self.edtEndTime.setEnabled(self.edtEndDate.isEnabled() and bool(date))
        if self.cmbStatus.currentIndex() == 2:
            for action in self.modelJobTicketProbe.actionList():  # type: CAction
                actionId = action.getId()
                record = action.getRecord()
                if self.actionDateChanger == 1 and self.mapActionIdToDateChangePossibility[actionId]['endDate']:
                    record.setValue('endDate', toVariant(QtCore.QDateTime(date, time)))

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtTissueDate_dateChanged(self, date):
        if self._manualInputExternalId is None:
            self._manualInputExternalId = forceBool(
                QtGui.qApp.db.translate('rbTissueType', 'id', self.cmbTissueType.value(), 'counterManualInput'))
        self.setTissueExternalId()

    @QtCore.pyqtSlot()
    def on_btnAmbCard_clicked(self):
        CAmbCardDialog(self, self.clientId).exec_()

    def templateModel(self):
        currentRow = self.tblTreeProbe.currentIndex().internalPointer()
        if not isinstance(currentRow, CJobTicketTreeActionItem):
            return
        action = currentRow.action()
        if QtGui.qApp.userHasRight(urLoadActionTemplate) and action:
            personId = forceRef(action.getRecord().value('person_id'))
            actionTemplateTreeModel = self.actionTemplateCache.getModel(
                action.getType().id,
                personId if personId else forceRef(action.getRecord().value('setPerson_id'))
            )
            return actionTemplateTreeModel
        return None

    @QtCore.pyqtSlot(int)
    def on_btnLoadTemplate_templateSelected(self, templateId):
        if QtGui.qApp.userHasRight(urLoadActionTemplate):
            currentRow = self.tblTreeProbe.currentIndex().internalPointer()
            if not isinstance(currentRow, CJobTicketTreeActionItem):
                return
            action = currentRow.action()
            if action:
                action.updateByTemplate(templateId)
                action.save(idx=forceRef(action.getRecord().value('idx')))
                self.modelActionProperties.emitDataChanged()

    @QtCore.pyqtSlot()
    def on_btnSaveAsTemplate_clicked(self):
        if QtGui.qApp.userHasRight(urSaveActionTemplate):
            currentRow = self.tblTreeProbe.currentIndex().internalPointer()
            if not isinstance(currentRow, CJobTicketTreeActionItem):
                return
            action = currentRow.action()
            if action:
                actionRecord = action.getRecord()
                if not self.eventEditor:
                    self.creatEventPossibilities(forceRef(actionRecord.value('event_id')))
                dlg = CActionTemplateSaveDialog(self,
                                                actionRecord,
                                                action,
                                                self.eventEditor.clientSex,
                                                self.eventEditor.clientAge,
                                                self.eventEditor.personId,
                                                self.eventEditor.personSpecialityId)
                dlg.exec_()
                self.actionTemplateCache.reset(action.getType().id)
                personId = forceRef(action.getRecord().value('person_id'))
                actionTemplateTreeModel = self.actionTemplateCache.getModel(action.getType().id,
                                                                            personId if personId else forceRef(
                                                                                action.getRecord().value(
                                                                                    'setPerson_id')))
                self.btnLoadTemplate.setModel(actionTemplateTreeModel)

    @QtCore.pyqtSlot()
    def on_btnEditEvent_clicked(self):
        db = QtGui.qApp.db
        table = db.table('Job_Ticket')
        tableAPJT = db.table('ActionProperty_Job_Ticket')
        tableActionProperty = db.table('ActionProperty')
        tableAction = db.table('Action')
        tableEvent = db.table('Event')

        queryTable = table
        queryTable = queryTable.leftJoin(tableAPJT, tableAPJT['value'].eq(table['id']))
        queryTable = queryTable.leftJoin(tableActionProperty, tableActionProperty['id'].eq(tableAPJT['id']))
        queryTable = queryTable.leftJoin(tableAction, tableAction['id'].eq(tableActionProperty['action_id']))
        queryTable = queryTable.leftJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))

        where = [
            table['id'].eq(self._id),
            tableAction['deleted'].eq(0),
            tableEvent['deleted'].eq(0)
        ]

        cols = 'Event.id as eventId'

        query = db.query(db.selectStmt(queryTable, cols, where))

        if query.size():
            query.next()
            record = query.record()
            eventId = forceRef(record.value('eventId'))
            editEvent(self, eventId)
        else:
            QtGui.QMessageBox().warning(self,
                                        u'Внимание!',
                                        u'По данной работе не найдено обращения',
                                        QtGui.QMessageBox.Ok)

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
    def format(self, values):
        payStatus = forceInt(values[0])
        result = payStatusText(payStatus)
        contractId = forceRef(values[1])  # forceRef(QtGui.qApp.db.translate('Event', 'id', eventId, 'contract_id'))
        try:
            contractInfo = getContractInfo(contractId)
            if contractInfo.isIgnorePayStatusForJobs:
                result += u', %s' % contractInfo.resolution
        finally:
            return toVariant(result)


class CActionsModel(CTableModel):
    class CAssistantIdGetter(object):
        """
        Функтор, выполняющий роль хранилища и getter'а списка значений идентификаторов ассистентов по actionId.
        Создан для того, чтобы выдавать изменненые, но не сохраненные в базу данные (при условии, что изменения отражаются в sourceMap)
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
        if not actionsMap:
            actionsMap = {}
        self._parent = parent
        self._actionsMap = actionsMap

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
            fields.append(CBackRelationCol(interfaceCol=CDesignationCol(title=u'Ассистент' + assistantSuffix,
                                                                        fields=['person_id'],
                                                                        designationChain=(
                                                                            'vrbPersonWithSpeciality', 'name'),
                                                                        defaultWidth=20),
                                           primaryKey='id',
                                           subTableName='Action_Assistant',
                                           subTableForeignKey='action_id',
                                           subTableCond='assistantType_id = %s' % assistantTypeId,
                                           alternativeValuesGetter=valuesGetter))

        if QtGui.qApp.defaultMorphologyMKBIsVisible():
            fields.insert(2, CTextCol(u'МКБ', ['MKB'], 8))
            fields.insert(3, CTextCol(u'Морфология МКБ', ['morphologyMKB'], 14))
        CTableModel.__init__(self, parent, fields)
        self.loadField('*')
        self.setTable('Action', recordCacheCapacity=None)

    def deleteRecord(self, table, itemId):
        CTableModel.deleteRecord(self, table, itemId)
        self._parent.removeCanDeletedId(itemId)


# #############################################################################
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
            record = QtGui.qApp.db.getRecord('Person LEFT JOIN rbSpeciality ON rbSpeciality.id = Person.speciality_id',
                                             'speciality_id, service_id, provinceService_id, otherService_id, finance_id, tariffCategory_id',
                                             personId
                                             )
            if record:
                specialityId = forceRef(record.value('speciality_id'))
                serviceId = forceRef(record.value('service_id'))
                provinceServiceId = forceRef(record.value('provinceService_id'))
                otherServiceId = forceRef(record.value('otherService_id'))
                financeId = forceRef(record.value('finance_id'))
                tariffCategoryId = forceRef(record.value('tariffCategory_id'))
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
            db = QtGui.qApp.db
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
