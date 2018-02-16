# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2016 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Accounting.Utils import isShowJobTickets
from Events.Action import ActionStatus, CAction, CActionTypeCache
from Events.ActionInfo import CCookedActionInfo
from Events.AmbCardPage import CAmbCardDialog
from Events.EventInfo import CEventInfo
from Events.Utils import getExternalIdDateCond
from Exchange.n3labdata.OrderListDialog import CLabOrderListDialog
from Orgs.OrgStructComboBoxes import COrgStructureComboBox, COrgStructureModel
from Orgs.Utils import getOrgStructureFullName, getPersonInfo
from Registry.Utils import getStaffCondition
from Reports.ReportBase import CReportBase, createTable
from Reports.ReportView import CReportViewDialog
from Resources.JobTicketChooser import CJobTicketChooserComboBox, CJobTicketChooserDialog
from Resources.JobTicketEditor import CJobTicketEditor
from Resources.JobTicketEditor2 import CJobTicketEditor2
from Resources.JobTicketInfo import CJobTicketsWithActionsInfoList, makeDependentActionIdList
from Resources.JobsOperatingReportSetupDialog import CJobsOperatingReportSetupDialog
from Resources.Utils import JobTicketStatus, TakenTissueJournalStatus, getJobTicketActionIdList, \
    getTissueTypeCounterValue
from Ui_JobsOperatingDialog import Ui_JobsOperatingDialog
from Users.Rights import urEQCalling, urEQManaging, urEQSettings, urOpenJobTicketEditor, urShowColumnsInJobsOperDialog
from library.DialogBase import CDialogBase
from library.ElectronicQueue.EQController import CEQController
from library.ElectronicQueue.EQTicketModel import EQTicketStatus
from library.LoggingModule.Logger import getLoggerDbName
from library.PrintInfo import CInfoContext
from library.PrintTemplates import applyTemplate, getPrintAction
from library.TableModel import CCol, CDateTimeCol, CTableModel, CTextCol
from library.Utils import agreeNumberAndWord, clientQueueLog, forceBool, forceDate, forceDouble, forceInt, forceRef, \
    forceString, forceStringEx, formatName, \
    formatRecordsCount, formatSex, getPref, setPref, toVariant
from library.database import CTableRecordCache


class CJobsOperatingDialog(CDialogBase, Ui_JobsOperatingDialog):
    eqSummon = QtCore.pyqtSignal(int, int, int)  # eQueueTypeId, eqTicketId, orgStructureId
    eqEmergency = QtCore.pyqtSignal(int, int)  # eQueueTypeId, eqTicketId
    eqComplete = QtCore.pyqtSignal(int, int)  # eQueueTypeId, eqTicketId
    eqCancel = QtCore.pyqtSignal(int, int)  # eQueueTypeId, eqTicketId
    eqReady = QtCore.pyqtSignal(int, int)  # eQueueTypeId, eqTicketId
    eqIssued = QtCore.pyqtSignal(int, int)  # eQueueTypeId, eqTicketId

    def __init__(self, parent):
        CDialogBase.__init__(self, parent)

        self.jobSuperviseInfo = {}
        self.jobTicketOrderColumn = None
        self.jobTicketOrderAscending = True
        self.eQueueTypeId = None

        self.addModels('OrgStructure', COrgStructureModel(self, QtGui.qApp.currentOrgId(), headerName=u'Структура ЛПУ'))
        self.addModels('OrgStructureWithBeds', COrgStructureModel(self, filter='hasHospitalBedsStructure(id)=1', headerName=u'Структура ЛПУ: фильтр по отделению пациента'))
        self.addModels('JobTypes', CJobTypesModel(self))
        self.addModels('JobTickets', CJobTicketsModel(self))

        self.actMainPrint = QtGui.QAction(u'Основная печать списка', self)
        self.actMainPrint.setObjectName('actMainPrint')
        self.actClientListPrint = QtGui.QAction(u'Список пациентов', self)
        self.actClientListPrint.setObjectName('actClientListPrint')
        self.actJobTicketListPrint = getPrintAction(self, 'jobsOperating', u'Печать списка', False)
        self.actJobTicketListPrint.setObjectName('actJobTicketListPrint')
        self.actActionPrint = getPrintAction(self, 'jobsOperating', u'Печать мероприятия')
        self.actActionPrint.setObjectName('actActionPrint')
        self.btnPrint = QtGui.QPushButton(u'Печать', self)
        self.btnPrint.setObjectName('btnPrint')
        self.mnuBtnPrint = QtGui.QMenu(self)
        self.mnuBtnPrint.setObjectName('mnuBtnPrint')
        self.mnuBtnPrint.addAction(self.actMainPrint)
        self.mnuBtnPrint.addAction(self.actClientListPrint)
        self.mnuBtnPrint.addSeparator()
        self.mnuBtnPrint.addAction(self.actJobTicketListPrint)
        self.mnuBtnPrint.addSeparator()
        self.mnuBtnPrint.addAction(self.actActionPrint)
        self.btnPrint.setMenu(self.mnuBtnPrint)
        self.btnShowLabOrders = QtGui.QPushButton(u'ОДЛИ', self)
        self.btnShowLabOrders.setObjectName('btnShowLabOrders')

        self.setupUi(self)

        self.pageBlock = [
            self.lblCurrentTablePage,
            self.lblMaxTablePagesCount,
            self.btnNextTablePage,
            self.btnPrevTablePage
        ]

        self.calendar.setList(QtGui.qApp.calendarInfo)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setModels(self.treeOrgStructure, self.modelOrgStructure, self.selectionModelOrgStructure)
        self.setModels(self.tblJobTypes, self.modelJobTypes, self.selectionModelJobTypes)
        self.tblJobTypes.setAutoScroll(False)
        self.setModels(self.tblJobTickets, self.modelJobTickets, self.selectionModelJobTickets)

        self.cmbClientAccountingSystem.setTable('rbAccountingSystem', addNone=True)
        self.cmbSpeciality.setTable('rbSpeciality', True)
        self.cmbTissueType.setTable('rbTissueType', addNone=True, specialValues=[(-1, '-', u'любой биоматериал'), (-2, '-', u'без биоматериала')])
        self.cmbTakenTissueType.setTable('rbTissueType', addNone=True, specialValues=[(-1, '-', u'любой биоматериал'), (-2, '-', u'без биоматериала')])
        self.cmbTissueType.setValue(None)
        self.cmbTakenTissueType.setValue(None)
        self.filter = {}
        self.resetFilter()

        orgStructureIndex = self.modelOrgStructure.findItemId(QtGui.qApp.currentOrgStructureId())
        if orgStructureIndex and orgStructureIndex.isValid():
            self.treeOrgStructure.setCurrentIndex(orgStructureIndex)
            self.treeOrgStructure.setExpanded(orgStructureIndex, True)
        self.updateJobTicketList() # Added (issue 644)

        self.calendar.setSelectedDate(QtCore.QDate.currentDate())
        self.connect(self.tblJobTickets.horizontalHeader(), QtCore.SIGNAL('sectionClicked(int)'), self.setSortJobTicketsByColumn)
        self.buttonBox.addButton(self.btnPrint, QtGui.QDialogButtonBox.ActionRole)

        if QtGui.qApp.preferences.appPrefs.get('JobsOperatingLabOrders', False):
            self.buttonBox.addButton(self.btnShowLabOrders, QtGui.QDialogButtonBox.ActionRole)

        self.actAmbCardShow = QtGui.QAction(u'Медицинская карта', self)

        self.actJobTicketEditor2 = QtGui.QAction(u'Редактор v2', self, triggered=self.editCurrentJobTicket2)

        self.actChangeStatusInProgress = QtGui.QAction(u'Выполняется', self, triggered=self.on_actChangeStatusInProgress_triggered)
        self.actChangeStatusDone = QtGui.QAction(u'Закончено', self, triggered=self.on_actChangeStatusDone_triggered)

        self.actEQSummon = QtGui.QAction(u'Вызвать пациента', self, triggered = self.on_actEQSummon_triggered)
        self.actEQComplete = QtGui.QAction(u'Завершить успешно', self, triggered = self.on_actEQComplete_triggered)
        self.actEQCancel = QtGui.QAction(u'Отменить вызов', self, triggered = self.on_actEQCancel_triggered)
        self.actEQEmergency = QtGui.QAction(u'Вне очереди', self, triggered = self.on_actEQEmergency_triggered)
        self.actEQReady = QtGui.QAction(u'Готов к вызову', self, triggered = self.on_actEQReady_triggered)
        self.actEQIssued = QtGui.QAction(u'Не готов к вызову', self, triggered = self.on_actEQIssued_triggered)

        self.tblJobTickets.createPopupMenu([self.actAmbCardShow,
                                            '-',
                                            self.actJobTicketEditor2,
                                            '-',
                                            self.actChangeStatusInProgress,
                                            self.actChangeStatusDone,
                                            '-',
                                            self.actEQSummon,
                                            self.actEQEmergency,
                                            self.actEQComplete,
                                            self.actEQCancel,
                                            self.actEQReady,
                                            self.actEQIssued])
        # self.tblJobTickets.addPopupAction(self.actAmbCardShow)
        self.connect(self.actAmbCardShow, QtCore.SIGNAL('triggered()'), self.on_actAmbCardShow)
        self.connect(self.tblJobTickets.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.on_jobTicketsMenuAboutToShow)

        self.tblJobTickets.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)

        # сканирование штрих кода
        self.addBarcodeScanAction('actScanBarcode')
        self.addAction(self.actScanBarcode)
        self.connect(self.actScanBarcode, QtCore.SIGNAL('triggered()'), self.on_actScanBarcode)

        eqController = CEQController.getInstance()
        eqController.controlModel().initGuiControl(QtGui.qApp.currentOrgStructureId())
        eqController.controlModel().guiControl().appendWidget(self.eqControlWidget)
        self.eqControlWidget.setOpenSettingsEnabled(QtGui.qApp.userHasRight(urEQSettings))
        eqController.ticketStatusChanged.connect(self.modelJobTickets.updateTicketStatus)
        eqController.controlModel().setOrgStructureId(eqController.controlModel().guiControlId(),
                                                      QtGui.qApp.currentOrgStructureId())
        self.eqSummon.connect(eqController.summon)
        self.eqComplete.connect(eqController.markAsCompleted)
        self.eqCancel.connect(eqController.markAsCanceled)
        self.eqEmergency.connect(eqController.markAsEmergency)
        self.eqReady.connect(eqController.markAsReady)
        self.eqIssued.connect(eqController.markAsIssued)
        self.btnEnableEQueue.setEnabled(QtGui.qApp.userHasRight(urEQManaging)
                                        or QtGui.qApp.userHasRight(urEQCalling))

        self.chkClientLastName.toggled.connect(self.chkClientLastName_clicked)
        self.chkClientFirstName.clicked.connect(self.chkClientFirstName_clicked)
        self.chkClientPatrName.clicked.connect(self.chkClientPatrName_clicked)
        self.chkClientId.clicked.connect(self.chkClientId_clicked)
        self.chkJobTicketId.clicked.connect(self.edtJobTicketId_clicked)

        # for table pages
        self.idList = []
        self.actionIdList = []
        self.amountCount = []
        self.currentPage = 1
        self.maxPagesCount = 1
        self.buttonBoxFilter.buttons()[0].setAutoDefault(False)
        self.buttonBoxFilter.buttons()[0].setDefault(False)
        self.buttonBoxFilter.buttons()[1].setAutoDefault(True)
        self.buttonBoxFilter.buttons()[1].setDefault(True)

        self.rejected.connect(self.close)

    def savePreferences(self):
        QtGui.qApp.contactInfoMap.clear()

        preferences = CDialogBase.savePreferences(self)
        setPref(preferences, 'chkAwaiting', toVariant(self.chkAwaiting.isChecked()))
        setPref(preferences, 'chkInProgress', toVariant(self.chkInProgress.isChecked()))
        setPref(preferences, 'chkDone', toVariant(self.chkDone.isChecked()))
        setPref(preferences, 'chkOnlyUrgent', toVariant(self.chkOnlyUrgent.isChecked()))

        setPref(preferences, 'cmbOrgStructure', toVariant(self.cmbOrgStructure.value()))
        setPref(preferences, 'cmbSpeciality', toVariant(self.cmbSpeciality.value()))
        setPref(preferences, 'cmbPerson', toVariant(self.cmbPerson.value()))
        setPref(preferences, 'chkFilterListLength', toVariant(self.chkFilterListLength.isChecked()))
        setPref(preferences, 'edtFilterListLength', toVariant(self.edtFilterListLength.value()))
        return preferences

    def loadPreferences(self, preferences):
        QtGui.qApp.contactInfoMap = dict()

        self.chkAwaiting.setChecked(forceBool(getPref(preferences, 'chkAwaiting', True)))
        self.chkInProgress.setChecked(forceBool(getPref(preferences, 'chkInProgress', False)))
        self.chkDone.setChecked(forceBool(getPref(preferences, 'chkDone', False)))
        self.chkOnlyUrgent.setChecked(forceBool(getPref(preferences, 'chkOnlyUrgent', False)))

        self.cmbOrgStructure.setValue(forceRef(getPref(preferences, 'cmbOrgStructure', None)))
        self.cmbSpeciality.setValue(forceRef(getPref(preferences, 'cmbSpeciality', None)))
        self.cmbPerson.setValue(forceRef(getPref(preferences, 'cmbPerson', None)))
        self.chkFilterListLength.setChecked(forceBool(getPref(preferences, 'chkFilterListLength', True)))
        self.edtFilterListLength.setValue(forceInt(getPref(preferences, 'edtFilterListLength', 250)))
        CDialogBase.loadPreferences(self, preferences)

    def chkClientFirstName_clicked(self):
        self.edtClientFirstName.setEnabled(self.chkClientFirstName.isChecked())
        self.edtClientFirstName.setFocus(QtCore.Qt.ShortcutFocusReason)

    def chkClientLastName_clicked(self):
        self.edtClientLastName.setEnabled(self.chkClientLastName.isChecked())
        self.edtClientLastName.setFocus(QtCore.Qt.ShortcutFocusReason)

    def chkClientPatrName_clicked(self):
        self.edtClientPatrName.setEnabled(self.chkClientPatrName.isChecked())
        self.edtClientPatrName.setFocus(QtCore.Qt.ShortcutFocusReason)

    def chkClientId_clicked(self):
        self.edtClientId.setEnabled(self.chkClientId.isChecked())
        self.edtClientId.setFocus(QtCore.Qt.ShortcutFocusReason)

    def edtJobTicketId_clicked(self):
        self.edtJobTicketId.setEnabled(self.chkJobTicketId.isChecked())
        self.edtJobTicketId.setFocus(QtCore.Qt.ShortcutFocusReason)

    def closeEvent(self, event):
        eqController = CEQController.getInstance()
        eqController.controlModel().guiControl().removeWidget(self.eqControlWidget)
        super(CJobsOperatingDialog, self).closeEvent(event)
        self.deleteLater()

    @QtCore.pyqtSlot()
    def on_actEQSummon_triggered(self):
        idx = self.tblJobTickets.currentIndex()
        eqTicketId = self.modelJobTickets.eQueueTicketId(idx)

        eqController = CEQController.getInstance()
        guiControlId = eqController.controlModel().guiControl().controlId()
        orgStructureId = eqController.baseOrgStructureByControl(guiControlId)
        if orgStructureId is None:
            orgStructureIdList = self.getOrgStructIdList()
            orgStructureId = orgStructureIdList[0] if orgStructureIdList else None
        selectedOrgStructure = None
        if orgStructureId:
            dlg = QtGui.QDialog(self)
            dlg.setWindowTitle(u'Выберите подразделение вызова')
            layout = QtGui.QVBoxLayout()
            cmbOrgStructure = COrgStructureComboBox(self)
            cmbOrgStructure.setOrgId(orgId=QtGui.qApp.currentOrgId(), orgStructureId=orgStructureId)
            layout.addWidget(cmbOrgStructure)
            buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
                                               QtCore.Qt.Horizontal)
            buttonBox.accepted.connect(dlg.accept)
            buttonBox.rejected.connect(dlg.reject)

            layout.addWidget(buttonBox)
            dlg.setLayout(layout)
            if dlg.exec_():
                selectedOrgStructure = cmbOrgStructure.value()

        if self.eQueueTypeId and eqTicketId and selectedOrgStructure:
            self.eqSummon.emit(self.eQueueTypeId, eqTicketId, selectedOrgStructure)

    @QtCore.pyqtSlot()
    def on_actEQEmergency_triggered(self):
        idx = self.tblJobTickets.currentIndex()
        eqTicketId = self.modelJobTickets.eQueueTicketId(idx)
        if self.eQueueTypeId and eqTicketId:
            self.eqEmergency.emit(self.eQueueTypeId, eqTicketId)

    @QtCore.pyqtSlot()
    def on_actEQComplete_triggered(self):
        idx = self.tblJobTickets.currentIndex()
        eqTicketId = self.modelJobTickets.eQueueTicketId(idx)
        if self.eQueueTypeId and eqTicketId:
            self.eqComplete.emit(self.eQueueTypeId, eqTicketId)

    @QtCore.pyqtSlot()
    def on_actEQCancel_triggered(self):
        idx = self.tblJobTickets.currentIndex()
        eqTicketId = self.modelJobTickets.eQueueTicketId(idx)
        if self.eQueueTypeId and eqTicketId:
            self.eqCancel.emit(self.eQueueTypeId, eqTicketId)

    @QtCore.pyqtSlot()
    def on_actEQReady_triggered(self):
        msg = ''
        try:
            idx = self.tblJobTickets.currentIndex()
            eqTicketId = self.modelJobTickets.eQueueTicketId(idx)
            if self.eQueueTypeId and eqTicketId:
                self.eqReady.emit(self.eQueueTypeId, eqTicketId)
        except Exception as e:
            msg = e.msg if hasattr(e, 'msg') else e.message
        finally:
            clientQueueLog(u'"Готов к вызову"', msg)

    def on_actEQIssued_triggered(self):
        idx = self.tblJobTickets.currentIndex()
        eqTicketId = self.modelJobTickets.eQueueTicketId(idx)
        if self.eQueueTypeId and eqTicketId:
            self.eqIssued.emit(self.eQueueTypeId, eqTicketId)

    @QtCore.pyqtSlot()
    def on_jobTicketsMenuAboutToShow(self):
        currentIndex = self.tblJobTickets.currentIndex()
        curentIndexIsValid = currentIndex.isValid()
        self.actAmbCardShow.setEnabled(curentIndexIsValid)
        status = self.modelJobTickets.eqTicketStatus(currentIndex)
        isEnabled = CEQController.getInstance().controlModel().guiControl().isActive() \
                    and QtGui.qApp.userHasRight(urEQManaging)

        if not QtGui.qApp.userHasRight(urShowColumnsInJobsOperDialog):
            self.actChangeStatusInProgress.setEnabled(False)
            self.actChangeStatusDone.setEnabled(False)

        self.actEQReady.setEnabled(isEnabled and status != EQTicketStatus.Ready)
        self.actEQIssued.setEnabled(isEnabled and status != EQTicketStatus.Issued)
        self.actEQComplete.setEnabled(isEnabled and status != EQTicketStatus.Complete)
        self.actEQCancel.setEnabled(isEnabled and status != EQTicketStatus.Canceled)
        self.actEQEmergency.setEnabled(isEnabled and status != EQTicketStatus.Emergency)
        self.actEQSummon.setEnabled(isEnabled and status in [EQTicketStatus.Ready, EQTicketStatus.InProgress, EQTicketStatus.Emergency])

    @QtCore.pyqtSlot()
    def on_actChangeStatusInProgress_triggered(self):
        jobTicketId = self.tblJobTickets.currentItemId()

        db = QtGui.qApp.db
        tableAction = db.table('Action')
        tableAP = db.table('ActionProperty')
        tableAPJT = db.table('ActionProperty_Job_Ticket')
        tableATTT = db.table('ActionType_TissueType')
        tableCounter = db.table('rbCounter')
        tableJobTicket = db.table('Job_Ticket')
        tableTTJ = db.table('TakenTissueJournal')

        table = tableAPJT.innerJoin(tableAP, tableAP['id'].eq(tableAPJT['id']))
        table = table.innerJoin(tableAction, tableAction['id'].eq(tableAP['action_id']))
        cols = [
            tableAction['id'].alias('actionId'),
            tableAction['actionType_id'].alias('actionTypeId'),
            tableAction['takenTissueJournal_id'].alias('ttjId')
        ]
        cond = [tableAPJT['value'].eq(jobTicketId)]
        recAction = db.getRecordEx(table, cols, cond)

        recJobTicket = db.getRecord(tableJobTicket, ['id', 'status', 'begDateTime'], jobTicketId)
        if recJobTicket and recAction:
            actionId = forceRef(recAction.value('actionId'))
            actionTypeId = forceRef(recAction.value('actionTypeId'))
            tissueTypeIdList = db.getIdList(tableATTT, tableATTT['tissueType_id'], tableATTT['master_id'].eq(actionTypeId)) if actionTypeId else []
            jtStatus = forceInt(recJobTicket.value('status'))
            ttjId = forceRef(recAction.value('ttjId'))

            if jtStatus == JobTicketStatus.Awaiting:
                recJobTicket.setValue('status', toVariant(JobTicketStatus.InProgress))
                recJobTicket.setValue('begDateTime', toVariant(QtCore.QDateTime.currentDateTime()))
                db.updateRecord(tableJobTicket, recJobTicket)

            if ttjId:
                db.updateRecords(tableTTJ,
                                 tableTTJ['status'].eq(TakenTissueJournalStatus.InProgress),
                                 tableTTJ['id'].eq(ttjId))

            elif len(tissueTypeIdList) == 1:
                tissueTypeId = tissueTypeIdList[0]
                tissueCounterValue = getTissueTypeCounterValue(tissueTypeId)
                if tissueCounterValue is not None:
                    counterId, counterValue = tissueCounterValue
                    ttjId = db.insertFromDict('TakenTissueJournal', {
                        'client_id'      : self.modelJobTickets.getClientId(jobTicketId),
                        'tissueType_id'  : tissueTypeId,
                        'externalId'     : counterValue,
                        'number'         : counterValue,
                        'datetimeTaken'  : QtCore.QDateTime.currentDateTime(),
                        'createDatetime' : QtCore.QDateTime.currentDateTime(),
                        'createPerson_id': QtGui.qApp.userId,
                        'execPerson_id'  : QtGui.qApp.userId,
                        'status'         : TakenTissueJournalStatus.InProgress
                    })
                    db.updateRecords(tableAction,
                                     tableAction['takenTissueJournal_id'].eq(ttjId),
                                     tableAction['id'].eq(actionId))
                    db.updateRecords(tableCounter,
                                     tableCounter['value'].eq(counterValue + 1),
                                     tableCounter['id'].eq(counterId))

            elif len(tissueTypeIdList) > 1:
                QtGui.QMessageBox.information(None, u'Ошибка', u'Необходимо ввести идентификатор')
        else:
            QtGui.QMessageBox.information(None, u'Ошибка', u'Номерок не найден')

        self.updateJobTicketList()

    @QtCore.pyqtSlot()
    def on_actChangeStatusDone_triggered(self):
        jobTicketId = self.tblJobTickets.currentItemId()
        db = QtGui.qApp.db
        tableAction = db.table('Action')
        tableAP = db.table('ActionProperty')
        tableAPJT = db.table('ActionProperty_Job_Ticket')
        tableATTT = db.table('ActionType_TissueType')
        tableJobTicket = db.table('Job_Ticket')
        tableTTJ = db.table('TakenTissueJournal')

        table = tableAPJT.innerJoin(tableAP, tableAP['id'].eq(tableAPJT['id']))
        table = table.innerJoin(tableAction, tableAction['id'].eq(tableAP['action_id']))
        cols = [
            tableAction['id'].alias('actionId'),
            tableAction['actionType_id'].alias('actionTypeId'),
            tableAction['takenTissueJournal_id'].alias('ttjId')
        ]
        cond = [tableAPJT['value'].eq(jobTicketId)]
        recAction = db.getRecordEx(table, cols, cond)
        recJobTicket = db.getRecord(tableJobTicket, ['id', 'begDateTime', 'endDateTime', 'status'], jobTicketId)
        if recJobTicket and recAction:
            actionId = forceRef(recAction.value('actionId'))
            actionTypeId = forceRef(recAction.value('actionTypeId'))
            tissueTypeIdList = db.getIdList(tableATTT, tableATTT['tissueType_id'], tableATTT['master_id'].eq(actionTypeId)) if actionTypeId else []
            jtStatus = forceInt(recJobTicket.value('status'))
            ttjId = forceRef(recAction.value('ttjId'))
            if jtStatus != JobTicketStatus.Done:
                curDatetime = QtCore.QDateTime.currentDateTime()
                if not recJobTicket.value('begDateTime'):
                    recJobTicket.setValue('begDateTime', toVariant(curDatetime))
                recJobTicket.setValue('endDateTime', toVariant(curDatetime))
                recJobTicket.setValue('status', toVariant(JobTicketStatus.Done))
                db.updateRecord(tableJobTicket, recJobTicket)
                db.updateRecords(tableAction, [tableAction['status'].eq(ActionStatus.Done),
                                               tableAction['endDate'].eq(curDatetime)], tableAction['id'].eq(actionId))

            if ttjId:
                db.updateRecords(tableTTJ,
                                 tableTTJ['status'].eq(TakenTissueJournalStatus.InProgress),
                                 tableTTJ['id'].eq(ttjId))
            elif len(tissueTypeIdList) > 1:
                QtGui.QMessageBox.information(None, u'Ошибка', u'Необходимо ввести идентификатор')

        else:
            QtGui.QMessageBox.information(None, u'Ошибка', u'Номерок не найден')
        self.updateJobTicketList()

    def on_actAmbCardShow(self):
        jobTicketId = self.tblJobTickets.currentItemId()
        clientId = self.modelJobTickets.getClientId(jobTicketId)
        CAmbCardDialog(self, clientId).exec_()

    def on_actScanBarcode(self):
        self.setCheckedAndEmit(self.chkJobTicketId, True)
        self.edtJobTicketId.clear()
        self.edtJobTicketId.setFocus(QtCore.Qt.OtherFocusReason)

    def getOrgStructIdList(self):
        treeIndex = self.treeOrgStructure.currentIndex()
        treeItem = treeIndex.internalPointer() if treeIndex.isValid() else None
        if treeItem:
            return treeItem.getItemIdList()
        return []

    def getJobTypeIdList(self, orgStructIdList, date, dateTo=None):
        if orgStructIdList:
            db = QtGui.qApp.db
            tableJob = db.table('Job')
            tableJobType = db.table('rbJobType')
            tableOSJ = db.table('OrgStructure_Job')

            table = tableJob.join(tableJobType, tableJobType['id'].eq(tableJob['jobType_id']))
            table = table.join(tableOSJ, tableOSJ['id'].eq(tableJob['orgStructureJob_id']))

            cond = [
                tableOSJ['master_id'].inlist(orgStructIdList),
                tableJob['deleted'].eq(0),
                tableJob['jobType_id'].isNotNull(),
            ]
            if dateTo is None:
                cond.append(tableJob['date'].dateEq(date))
            else:
                cond.extend([tableJob['date'].dateGe(date),
                             tableJob['date'].dateLe(dateTo)])

            return db.getDistinctIdList(table, tableJob['jobType_id'], cond, order=tableJobType['name'])
        return []

    def updateJobTypeList(self):
        orgStructIdList = self.getOrgStructIdList()
        if self.btnCalendarDate.isChecked():
            date = self.calendar.selectedDate()
            dateTo = None
        elif self.btnDateRange.isChecked():
            date = self.edtDateRangeFrom.date()
            dateTo = self.edtDateRangeTo.date()
        else:
            return
        jobTypeIdList = self.getJobTypeIdList(orgStructIdList, date, dateTo)
        self.tblJobTypes.setIdList(jobTypeIdList)

    def resetFilter(self):
        # self.chkAwaiting.setChecked(True)
        # self.chkInProgress.setChecked(False)
        # self.chkDone.setChecked(False)
        # self.chkOnlyUrgent.setChecked(False)
        self.cmbOrgStructure.setValue(None)
        self.cmbSpeciality.setValue(None)
        self.cmbPerson.setValue(None)
        self.cmbSex.setCurrentIndex(0)
        self.edtAgeFrom.setValue(self.edtAgeFrom.minimum())
        self.edtAgeTo.setValue(self.edtAgeTo.maximum())

        self.setCheckedAndEmit(self.chkClientId, False)
        self.cmbClientAccountingSystem.setValue(None)
        self.edtClientId.clear()

        self.setCheckedAndEmit(self.chkClientLastName, False)
        self.edtClientLastName.clear()

        self.setCheckedAndEmit(self.chkClientFirstName, False)
        self.edtClientFirstName.clear()

        self.setCheckedAndEmit(self.chkClientPatrName, False)
        self.edtClientPatrName.clear()

        self.setCheckedAndEmit(self.chkJobTicketId, False)
        self.edtJobTicketId.clear()

        self.setCheckedAndEmit(self.btnCalendarDate, True)

    def setCheckedAndEmit(self, chkWidget, value):
        chkWidget.setChecked(value)
        chkWidget.emit(QtCore.SIGNAL('clicked(bool)'), value)

    def setSortJobTicketsByColumn(self, logicalIndex):
        if self.jobTicketOrderColumn == logicalIndex:
            self.jobTicketOrderAscending = not self.jobTicketOrderAscending
        else:
            self.jobTicketOrderColumn = logicalIndex
            self.jobTicketOrderAscending = True

        header = self.tblJobTickets.horizontalHeader()
        header.setSortIndicatorShown(True)
        header.setSortIndicator(self.jobTicketOrderColumn, QtCore.Qt.AscendingOrder if self.jobTicketOrderAscending else QtCore.Qt.DescendingOrder)
        self.updateJobTicketList()

    def getFilter(self):
        return {
            'date'                    : self.calendar.selectedDate(),
            'orgStructIdList'         : self.getOrgStructIdList(),
            'jobTypeId'               : self.tblJobTypes.currentItemId(),
            'awaiting'                : self.chkAwaiting.isChecked(),
            'inProgress'              : self.chkInProgress.isChecked(),
            'done'                    : self.chkDone.isChecked(),
            'onlyUrgent'              : self.chkOnlyUrgent.isChecked(),
            'orgStructureId'          : self.cmbOrgStructure.value(),
            'specialityId'            : self.cmbSpeciality.value(),
            'setPersonId'             : self.cmbPerson.value(),
            'sex'                     : self.cmbSex.currentIndex(),
            'ageFrom'                 : self.edtAgeFrom.value(),
            'ageTo'                   : self.edtAgeTo.value(),
            'tissueTypeId'            : self.cmbTissueType.value(),
            'takenTissueTypeId'       : self.cmbTakenTissueType.value(),
            'chkClientId'             : self.chkClientId.isChecked(),
            'clientAccountingSystemId': self.cmbClientAccountingSystem.value(),
            'clientId'                : forceStringEx(self.edtClientId.text()),
            'chkClientLastName'       : self.chkClientLastName.isChecked(),
            'clientLastName'          : forceStringEx(self.edtClientLastName.text()),
            'chkClientFirstName'      : self.chkClientFirstName.isChecked(),
            'clientFirstName'         : forceStringEx(self.edtClientFirstName.text()),
            'chkClientPatrName'       : self.chkClientPatrName.isChecked(),
            'clientPatrName'          : forceStringEx(self.edtClientPatrName.text()),
            'chkJobTicketId'          : self.chkJobTicketId.isChecked(),
            'jobTicketId'             : forceStringEx(self.edtJobTicketId.text()),
            'chkCalendarDate'         : self.btnCalendarDate.isChecked(),
            'chkDateRange'            : self.btnDateRange.isChecked(),
            'dateRangeFrom'           : self.edtDateRangeFrom.date(),
            'dateRangeTo'             : self.edtDateRangeTo.date()
        }

    def prepareQueryPartsByJobTicketId(self, jobTicketId):
        db = QtGui.qApp.db
        tableAP = db.table('ActionProperty')
        tableAction = db.table('Action')
        tableAPJT = db.table('ActionProperty_Job_Ticket')
        tableClient = db.table('Client')
        tableEvent = db.table('Event')
        tableEQueueTicket = db.table('EQueueTicket')
        tableEQueue = db.table('EQueue')
        tableJob = db.table('Job')
        tableJT = db.table('Job_Ticket')
        queryTable = tableJT
        queryTable = queryTable.innerJoin(tableAPJT, tableAPJT['value'].eq(tableJT['id']))
        queryTable = queryTable.leftJoin(tableJob, tableJob['id'].eq(tableJT['master_id']))
        queryTable = queryTable.leftJoin(tableAP, tableAP['id'].eq(tableAPJT['id']))
        queryTable = queryTable.leftJoin(tableAction, tableAction['id'].eq(tableAP['action_id']))
        queryTable = queryTable.leftJoin(tableEQueueTicket, tableEQueueTicket['id'].eq(tableJT['eQueueTicket_id']))
        queryTable = queryTable.leftJoin(tableEQueue, tableEQueue['id'].eq(tableEQueueTicket['queue_id']))
        queryTable = queryTable.leftJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
        queryTable = queryTable.leftJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))
        order = self.getOrder()
        return queryTable, tableJT['id'].eq(jobTicketId), order

    def prepareQueryParts(self, filter):
        isClientFilter = True  # self.tabDateClientFilter.widget(self.tabDateClientFilter.currentIndex()) == self.tabClientFilter
        date = filter['date']
        orgStructIdList = filter['orgStructIdList']
        jobTypeId = filter['jobTypeId']
        awaiting = filter['awaiting']
        inProgress = filter['inProgress']
        done = filter['done']
        onlyUrgent = filter['onlyUrgent']
        orgStructureId = filter['orgStructureId']
        specialityId = filter['specialityId']
        setPersonId = filter['setPersonId']
        sex = filter['sex']
        ageFrom = filter['ageFrom']
        ageTo = filter['ageTo']
        tissueTypeId = filter['tissueTypeId']
        takenTissueTypeId = filter['takenTissueTypeId']
        chkJobTicketId = filter['chkJobTicketId']
        jobTicketId = filter['jobTicketId']
        chkCalendarDate = filter['chkCalendarDate']
        chkDateRange = filter['chkDateRange']
        dateRangeFrom = filter['dateRangeFrom']
        dateRangeTo = filter['dateRangeTo']

        if chkJobTicketId:
            return self.prepareQueryPartsByJobTicketId(jobTicketId)

        db = QtGui.qApp.db
        tableAction = db.table('Action')
        tableActionType = db.table('ActionType')
        tableAP = db.table('ActionProperty')
        tableAPJT = db.table('ActionProperty_Job_Ticket')
        tableClient = db.table('Client')
        tableEvent = db.table('Event')
        tableEQueue = db.table('EQueue')
        tableEQueueTicket = db.table('EQueueTicket')
        tableIdentification = db.table('ClientIdentification')
        tableJob = db.table('Job')
        tableJT = db.table('Job_Ticket')
        tableOrgStructureJob = db.table('OrgStructure_Job')
        tablePerson = db.table('vrbPersonWithSpeciality')

        queryTable = tableJT
        queryTable = queryTable.leftJoin(tableJob, tableJob['id'].eq(tableJT['master_id']))
        queryTable = queryTable.leftJoin(tableOrgStructureJob, tableOrgStructureJob['id'].eq(tableJob['orgStructureJob_id']))
        queryTable = queryTable.leftJoin(tableAPJT, tableAPJT['value'].eq(tableJT['id']))
        queryTable = queryTable.leftJoin(tableAP, tableAP['id'].eq(tableAPJT['id']))
        queryTable = queryTable.leftJoin(tableAction, tableAction['id'].eq(tableAP['action_id']))
        queryTable = queryTable.leftJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
        queryTable = queryTable.leftJoin(tablePerson, tablePerson['id'].eq(tableAction['setPerson_id']))
        queryTable = queryTable.leftJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
        queryTable = queryTable.leftJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))
        queryTable = queryTable.leftJoin(tableEQueueTicket, tableEQueueTicket['id'].eq(tableJT['eQueueTicket_id']))
        queryTable = queryTable.leftJoin(tableEQueue, tableEQueue['id'].eq(tableEQueueTicket['queue_id']))

        cond = []
        if awaiting and inProgress and done:
            pass
        else:
            statuses = []
            if awaiting: statuses.append(JobTicketStatus.Awaiting)
            if inProgress: statuses.append(JobTicketStatus.InProgress)
            if done: statuses.append(JobTicketStatus.Done)
            cond.append(tableJT['status'].inlist(statuses))
        if onlyUrgent:
            cond.append(tableAction['isUrgent'].ne(0))
        if setPersonId:
            cond.append(tableAction['setPerson_id'].eq(setPersonId))
        else:
            if orgStructureId:
                cond.append(tablePerson['orgStructure_id'].eq(orgStructureId))
            if specialityId:
                cond.append(tablePerson['speciality_id'].eq(specialityId))
        if sex:
            cond.append(tableClient['sex'].eq(sex))
        if ageFrom <= ageTo:
            cond.append('Job_Ticket.datetime >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)' % ageFrom)
            cond.append('Job_Ticket.datetime < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)' % (ageTo + 1))
        if tissueTypeId:
            if tissueTypeId == -1:
                cond.append('EXISTS (SELECT id FROM ActionType_TissueType WHERE master_id=ActionType.`id`)')
            elif tissueTypeId == -2:
                cond.append('NOT EXISTS (SELECT id FROM ActionType_TissueType WHERE master_id=ActionType.`id`)')
            else:
                cond.append('EXISTS (SELECT id FROM ActionType_TissueType WHERE master_id=ActionType.`id` AND tissueType_id=%d)' % tissueTypeId)
        if takenTissueTypeId:
            if takenTissueTypeId == -1:
                cond.append('EXISTS (SELECT id FROM TakenTissueJournal WHERE Action.`takenTissueJournal_id`=TakenTissueJournal.`id`)')
            elif takenTissueTypeId == -2:
                cond.append('NOT EXISTS (SELECT id FROM TakenTissueJournal WHERE Action.`takenTissueJournal_id`=TakenTissueJournal.`id`)')
            else:
                cond.append('EXISTS (SELECT id FROM TakenTissueJournal WHERE Action.`takenTissueJournal_id`=TakenTissueJournal.`id` and TakenTissueJournal.`tissueType_id`=%d)' % takenTissueTypeId)

        if isClientFilter:
            chkClientId = filter['chkClientId']
            clientAccountingSystemId = filter['clientAccountingSystemId']
            clientId = filter['clientId']
            chkClientLastName = filter['chkClientLastName']
            clientLastName = filter['clientLastName']
            chkClientFirstName = filter['chkClientFirstName']
            clientFirstName = filter['clientFirstName']
            chkClientPatrName = filter['chkClientPatrName']
            clientPatrName = filter['clientPatrName']

            if chkClientId:
                if bool(clientId):
                    if clientAccountingSystemId:
                        queryTable = queryTable.innerJoin(tableIdentification, tableIdentification['client_id'].eq(tableClient['id']))
                        cond.extend([tableIdentification['accountingSystem_id'].eq(clientAccountingSystemId),
                                     tableIdentification['identifier'].eq(clientId)])
                    else:
                        cond.append(tableClient['id'].eq(clientId))
            else:
                if chkClientLastName and bool(clientLastName):
                    cond.append(tableClient['lastName'].like('%' + clientLastName + '%'))
                if chkClientFirstName and bool(clientFirstName):
                    cond.append(tableClient['firstName'].like('%' + clientFirstName + '%'))
                if chkClientPatrName and bool(clientPatrName):
                    cond.append(tableClient['patrName'].like('%' + clientPatrName + '%'))
            if chkCalendarDate:
                cond.append(tableJob['date'].dateEq(date))
            elif chkDateRange:
                cond.append(tableJob['date'].dateGe(dateRangeFrom))
                cond.append(tableJob['date'].dateLe(dateRangeTo))

        if not QtGui.qApp.isDisplayStaff():
            cond.append('NOT (%s)' % getStaffCondition(tableClient['id'].name()))

        order = self.getOrder()

        cond.extend([
            tableJob['jobType_id'].eq(jobTypeId),
            tableOrgStructureJob['master_id'].inlist(orgStructIdList),
            tableAction['deleted'].eq(0),
            tableEvent['deleted'].eq(0),
            tableClient['deleted'].eq(0)
        ])

        return queryTable, cond, order

    def getOrder(self):
        if self.jobTicketOrderColumn == 0:
            order = 'EQueueTicket.idx'
        elif self.jobTicketOrderColumn == 1:
            order = 'Job_Ticket.datetime'
        elif self.jobTicketOrderColumn == 2:
            order = 'Client.lastName, Client.firstName, Client.patrName, Job_Ticket.datetime'
        elif self.jobTicketOrderColumn == 3:
            order = 'Client.birthDate, Job_Ticket.datetime'
        elif self.jobTicketOrderColumn == 4:
            order = 'Client.sex, Job_Ticket.datetime'
        elif self.jobTicketOrderColumn == 5:
            order = 'ActionType.name, Job_Ticket.datetime'
        elif self.jobTicketOrderColumn == 6:
            order = 'vrbPersonWithSpeciality.name, Job_Ticket.datetime'
        elif self.jobTicketOrderColumn == 7:
            order = 'Job_Ticket.label, Job_Ticket.datetime'
        elif self.jobTicketOrderColumn == 8:
            order = 'Job_Ticket.note, Job_Ticket.datetime'
        else:
            order = 'Job_Ticket.datetime'
        if not self.jobTicketOrderAscending:
            order = ','.join([part + ' DESC' for part in order.split(',')])

        return order

    def getFilterDescription(self, filter):
        date = filter['date']
        jobTypeId = filter['jobTypeId']
        awaiting = filter['awaiting']
        inProgress = filter['inProgress']
        done = filter['done']
        onlyUrgent = filter['onlyUrgent']
        orgStructureId = filter['orgStructureId']
        specialityId = filter['specialityId']
        setPersonId = filter['setPersonId']
        sex = filter['sex']
        ageFrom = filter['ageFrom']
        ageTo = filter['ageTo']

        db = QtGui.qApp.db
        description = [u'дата: ' + forceString(date)]
        if jobTypeId:
            jobTypeName = forceString(db.translate('rbJobType', 'id', jobTypeId, 'name'))
            description.append(u'работа: ' + jobTypeName)
        if awaiting:
            description.append(u'ожидающие')
        if inProgress:
            description.append(u'выполняемые')
        if done:
            description.append(u'законченные')
        if onlyUrgent:
            description.append(u'только срочные')
        if orgStructureId:
            description.append(u'подразделение: ' + getOrgStructureFullName(orgStructureId))
        if specialityId:
            description.append(u'специальность: ' + forceString(db.translate('rbSpeciality', 'id', specialityId, 'name')))
        if self.filter['setPersonId']:
            personInfo = getPersonInfo(setPersonId)
            description.append(u'врач: ' + personInfo['shortName'] + ', ' + personInfo['specialityName'])
        if sex:
            description.append(u'пол: ' + formatSex(sex))
        if ageFrom <= ageTo:
            description.append(u'возраст: c %d по %d %s' % (ageFrom, ageTo, agreeNumberAndWord(ageTo, (u'год', u'года', u'лет'))))
        return '\n'.join(description)

    def setEnabledTablePagesBlock(self, flag=True):
        if hasattr(self, 'pageBlock'):
            for x in self.pageBlock:
                x.setEnabled(flag)
        else:
            print '[JobsOperatingDialog] object has no attribute \'pageBlock\''

    def initPageBlock(self):
        self.setEnabledTablePagesBlock()

        self.btnPrevTablePage.setEnabled(False)
        self.currentPage = 1
        self.lblCurrentTablePage.setText(u"Страница %s" % self.currentPage)
        self.lblMaxTablePagesCount.setText(u"Всего страниц: %s" % self.maxPagesCount)
        # self.saveLbl = self.lblTicketsCount.text()

    def calculatePageCount(self):
        listLength = self.edtFilterListLength.value()
        if self.chkFilterListLength.isChecked() and listLength and len(self.idList):
            if listLength < len(self.idList):
                self.maxPagesCount = int(round((len(self.idList) / float(listLength)) + 0.5))
                if self.maxPagesCount > 1:
                    self.initPageBlock()
                    self.setTablePage()
            else:
                self.maxPagesCount = 1
                self.initPageBlock()
                self.setEnabledTablePagesBlock(False)

    def setTablePage(self):
        size = self.edtFilterListLength.value()
        try:
            idList = self.idList[size * (self.currentPage - 1):size * self.currentPage]
            self.tblJobTickets.setIdList(idList)
            self.setLblTicketsCount(idList)
        except Exception as e:
            print '[setTablePage error]: %s' % e.message
            try:
                idList = self.idList[:self.edtFilterListLength.value()]
                self.tblJobTickets.setIdList(idList)
            except:
                self.tblJobTickets.setIdList(list())
                self.setLblTicketsCount(list())
                # self.lblTicketsCount.setText(self.saveLbl)

    @QtCore.pyqtSlot(bool)
    def on_btnPrevTablePage_clicked(self, value):
        self.currentPage -= 1

        if self.currentPage == 1:
            self.btnPrevTablePage.setEnabled(False)
        if self.currentPage < self.maxPagesCount:
            self.btnNextTablePage.setEnabled(True)

        self.setTablePage()
        self.lblCurrentTablePage.setText(u"Страница %s" % self.currentPage)

    @QtCore.pyqtSlot(bool)
    def on_btnNextTablePage_clicked(self, value):
        self.currentPage += 1

        if self.currentPage == self.maxPagesCount:
            self.btnNextTablePage.setEnabled(False)
        if self.currentPage > 1:
            self.btnPrevTablePage.setEnabled(True)

        self.setTablePage()
        self.lblCurrentTablePage.setText(u"Страница %s" % self.currentPage)

    def setLblTicketsCount(self, viewedIdList):
        idListInfo = u'Всего найдено записей: %d' % len(self.idList)
        actionsInfo = u'Всего мероприятий: %d' % len(self.actionIdList)
        amountInfo = u'Всего услуг: %d' % self.amountCount
        viewedInfo = u'Показано записей: %d' % len(viewedIdList)
        self.lblTicketsCount.setText(u'\n'.join([
            idListInfo,
            # jobTicketsInfo,
            actionsInfo,
            amountInfo,
            viewedInfo
        ]))

    def updateJobTicketList(self):
        filter = self.getFilter()
        queryTable, cond, order = self.prepareQueryParts(filter)
        db = QtGui.qApp.db
        # idList = db.getDistinctIdList(queryTable, 'Job_Ticket.id', cond, order)
        idList = []
        actionIdList = []
        amountCount = 0
        # atronah for issue 317: add jobId
        recordList = db.getRecordList(queryTable,
                                      'Job_Ticket.id AS  jobTicketId, Action.id AS actionId, Action.amount AS actionAmount, Job.id AS jobId, EQueue.eQueueType_id AS queueTypeId',
                                      cond, order)

        # showJThelper = CShowJobTickets()
        queueTypeIdList = []
        for record in recordList:
            jobTicketId = forceRef(record.value('jobTicketId'))
            jobId = forceRef(record.value('jobId'))
            actionId = forceRef(record.value('actionId'))
            queueTypeId = forceRef(record.value('queueTypeId'))
            if queueTypeId not in queueTypeIdList:
                queueTypeIdList.append(queueTypeId)
            # atronah for issue 317: add check isShowJobTickets
            if (not jobTicketId in idList) and isShowJobTickets(jobId, actionId):
                idList.append(jobTicketId)

            if not actionId in actionIdList:
                actionIdList.append(actionId)
                actionAmount = forceDouble(record.value('actionAmount'))
                amountCount += actionAmount

        # self.eQueueTypeId = queueTypeIdList[0] if len(queueTypeIdList) == 1 else None
        for x in queueTypeIdList:
            if x:
                self.eQueueTypeId = x
                break

        self.filter = filter

        rowCount = int(self.edtFilterListLength.text())

        self.idList = idList
        self.actionIdList = actionIdList
        self.amountCount = amountCount

        self.calculatePageCount()
        idList = self.idList
        viewedIdList = idList[:rowCount] if len(idList) > rowCount and self.chkFilterListLength.isChecked() else idList

        self.tblJobTickets.setIdList(viewedIdList)
        # self.tblJobTickets.setIdList(idList)
        if filter['chkJobTicketId'] and idList:
            self.setValuesByJobTicketId(idList[0])
        # jobTicketsInfo = formatRecordsCount(len(idList))

        self.setLblTicketsCount(viewedIdList)

        # self.saveLbl = self.lblTicketsCount.text()
        self.jobSuperviseInfo = CJobTicketChooserDialog.getJobTicketsInfo(filter['jobTypeId'],
                                                                          filter['date'],
                                                                          filter['clientId'],
                                                                          None,
                                                                          {},
                                                                          [])[4]
        self.updateSuperviceUnitInfo(self.tblJobTickets.currentIndex())
        if self.eQueueTypeId and self.calendar.selectedDate() == QtCore.QDate.currentDate():
            controlModel = CEQController.getInstance().controlModel()
            controlModel.setQueueTypeId(controlModel.guiControlId(), self.eQueueTypeId)

    def setValuesByJobTicketId(self, jobTicketId):
        db = QtGui.qApp.db
        record = db.getRecord('Job_Ticket', 'datetime, master_id', jobTicketId)
        if record:
            date = forceDate(record.value('datetime'))
            jobTypeId = forceRef(db.translate('Job', 'id', forceRef(record.value('master_id')), 'jobType_id'))
            if self.btnCalendarDate.isChecked():
                self.calendar.setSelectedDate(date)
            elif self.btnDateRange.isChecked():
                self.edtDateRangeFrom.setDate(date)
                self.edtDateRangeTo.setDate(date)
            else:
                return
            jobTypeIdList = self.modelJobTypes.idList()
            if jobTypeId in jobTypeIdList:
                row = jobTypeIdList.index(jobTypeId)
                self.tblJobTypes.setCurrentIndex(self.modelJobTypes.index(row, 0))

    def editCurrentJobTicket(self, focusOnTissueExternalId=False):
        # FIXME: подставляет неверный id
        jobTicketId = self.tblJobTickets.currentItemId()
        if jobTicketId:
            dialog = CJobTicketEditor(self)
            dialog.load(jobTicketId)

            if focusOnTissueExternalId:
                dialog.setFocusToWidget(dialog.edtTissueExternalId)
                dialog.edtTissueExternalId.selectAll()

            if dialog.exec_():
                self.updateJobTicketList()

    def editCurrentJobTicket2(self):
        jobTicketId = self.tblJobTickets.currentItemId()
        if jobTicketId:
            dialog = CJobTicketEditor2(self)
            dialog.load(jobTicketId)
            if dialog.exec_():
                self.updateJobTicketList()

    def resetChkClientId(self):
        self.chkClientId.setChecked(False)
        self.chkClientId.emit(QtCore.SIGNAL('clicked(bool)'), False)

    @QtCore.pyqtSlot(bool)
    def on_chkClientId_clicked(self, value):
        if value:
            self.chkClientLastName.setChecked(False)
            self.chkClientLastName.emit(QtCore.SIGNAL('clicked(bool)'), False)
            self.chkClientFirstName.setChecked(False)
            self.chkClientFirstName.emit(QtCore.SIGNAL('clicked(bool)'), False)
            self.chkClientPatrName.setChecked(False)
            self.chkClientPatrName.emit(QtCore.SIGNAL('clicked(bool)'), False)

    @QtCore.pyqtSlot(bool)
    def on_chkClientLastName_clicked(self, value):
        if value and self.chkClientId.isChecked():
            self.resetChkClientId()

    @QtCore.pyqtSlot(bool)
    def on_chkClientFirstName_clicked(self, value):
        if value and self.chkClientId.isChecked():
            self.resetChkClientId()

    @QtCore.pyqtSlot(bool)
    def on_chkClientPatrName_clicked(self, value):
        if value and self.chkClientId.isChecked():
            self.resetChkClientId()

    @QtCore.pyqtSlot(int)
    def on_tabDateClientFilter_currentChanged(self, tabIndex):
        ticketId = self.tblJobTickets.currentItemId()
        needCheck = bool(ticketId)
        self.chkClientId.setChecked(needCheck)
        self.chkClientId.emit(QtCore.SIGNAL('clicked(bool)'), needCheck)
        if needCheck:
            clientId = self.modelJobTickets.getClientId(ticketId)
            if clientId:
                self.edtClientId.setText(unicode(clientId))
                self.updateJobTicketList()

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelJobTickets_currentChanged(self, current, previous):
        row = current.row()
        actionTypeId = self.modelJobTickets.getActionTypeId(row)
        actionType = CActionTypeCache.getById(actionTypeId) if actionTypeId else None
        context = actionType.context if actionType else None
        self.actActionPrint.setContext(context)
        self.updateSuperviceUnitInfo(current)

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelOrgStructure_currentChanged(self, current, previous):
        self.updateJobTypeList()

    @QtCore.pyqtSlot(int, int)
    def on_calendar_currentPageChanged(self, year, month):
        selectedDate = self.calendar.selectedDate()
        currYear = selectedDate.year()
        currMonth = selectedDate.month()
        newDate = selectedDate.addMonths((year - currYear) * 12 + (month - currMonth))
        self.calendar.setSelectedDate(newDate)

    #        self.updateJobTypeList()

    @QtCore.pyqtSlot()
    def on_calendar_selectionChanged(self):
        self.updateJobTypeList()

    @QtCore.pyqtSlot(bool)
    def on_btnCalendarDate_clicked(self, value):
        self.updateJobTypeList()

    @QtCore.pyqtSlot(bool)
    def on_btnDateRange_clicked(self, value):
        self.updateJobTypeList()

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtDateRangeFrom_dateChanged(self, date):
        self.updateJobTypeList()

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtDateRangeTo_dateChanged(self, date):
        self.updateJobTypeList()

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelJobTypes_currentChanged(self, current, previous):
        self.updateJobTicketList()
        jobTypeId = self.tblJobTypes.currentItemId()
        context = forceString(QtGui.qApp.db.translate('rbJobType', 'id', jobTypeId, 'listContext'))
        self.actJobTicketListPrint.setContext(context, False)

    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)

    @QtCore.pyqtSlot(int)
    def on_cmbSpeciality_currentIndexChanged(self, index):
        specialityId = self.cmbSpeciality.value()
        self.cmbPerson.setSpecialityId(specialityId)

    @QtCore.pyqtSlot(int)
    def on_modelJobTickets_itemsCountChanged(self, count):
        self.lblTicketsCount.setText(formatRecordsCount(count))

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBoxFilter_clicked(self, button):
        buttonCode = self.buttonBoxFilter.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.updateJobTicketList()
            if len(self.idList) == 1 and QtGui.qApp.preferences.appPrefs.get('autoJobTicketEditing', False):
                self.editCurrentJobTicket(focusOnTissueExternalId=True)
                self.setFocusToWidget(self.edtClientId)
                self.edtClientId.selectAll()

        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.resetFilter()
            self.updateJobTicketList()

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblJobTickets_doubleClicked(self, index):
        if QtGui.qApp.userHasRight(urOpenJobTicketEditor):
            self.editCurrentJobTicket()

    @QtCore.pyqtSlot(bool)
    def on_btnEnableStaticFilter_toggled(self, isChecked):
        if self.btnEnableEQueue.isEnabled():
            if isChecked:
                self.grpStaticFilter.setCurrentIndex(0)
            else:
                self.grpStaticFilter.setCurrentIndex(1)
            self.btnEnableEQueue.setChecked(not isChecked)
        else:
            self.btnEnableStaticFilter.setChecked(True)

    @QtCore.pyqtSlot(bool)
    def on_btnEnableEQueue_toggled(self, isChecked):
        if self.btnEnableStaticFilter.isEnabled():
            if isChecked:
                self.grpStaticFilter.setCurrentIndex(1)
            self.btnEnableStaticFilter.setChecked(not isChecked)
        else:
            self.btnEnableEQueue.setChecked(True)

    def on_grpStaticFilter_currentChanged(self, idx):
        if idx == 1:  # FIXME: atronah: заменить числа на имена
            self.resetFilter()
            if self.calendar.selectedDate() != QtCore.QDate.currentDate():
                self.calendar.setSelectedDate(QtCore.QDate.currentDate())
            else:
                self.updateJobTypeList()
            self.calendar.setEnabled(False)
            eqController = CEQController.getInstance()
            self.eqControlWidget.started.emit()
            eqController.updateButtonsState(eqController.controlModel().guiControl().controlId())
        else:
            self.eqControlWidget.stopped.emit()
            self.calendar.setEnabled(True)

    def updateSuperviceUnitInfo(self, index):
        infoText = u'Нет данных по УЕТ'
        if index.isValid():
            jobInfo = self.jobSuperviseInfo.get(self.modelJobTickets.getJobIdByRow(index.row()), {})
            jobLimitUnit = jobInfo.get('limit', 0.0)
            jobUsedUnit = jobInfo.get('used', 0.0)
            ticketId = self.modelJobTickets.getIdByRow(index.row())
            currentServiceUnit = self.modelJobTickets.getServiceSuperviseUnit(ticketId)
            infoText = u'Использовано УЕТ: %s из %s\nУЕТ текущей услуги: %s' % (jobUsedUnit,
                                                                                jobLimitUnit if jobLimitUnit > CJobTicketChooserComboBox.superviseUnitLimitPrecision
                                                                                else u'<без ограничения>',
                                                                                currentServiceUnit if currentServiceUnit else u'<нет данных>'
                                                                                )
        self.lblSuperviseInfo.setText(infoText)

    def mainReport(self):
        setupDialog = CJobsOperatingReportSetupDialog(self)
        setupDialog.setTitle(u'Выполнение работ')
        setupDialog.chkClientBirthday.setChecked(False)
        setupDialog.chkClientBirthday.setEnabled(False)
        setupDialog.chkClientBirthday.setVisible(False)
        if not setupDialog.exec_():
            return

        paramsMap = setupDialog.params()
        columnsMap = setupDialog.getReportColumns()
        selectedColumnsMap = [x for x in sorted(columnsMap.keys()) if paramsMap[x]]

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Выполнение работ')
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertText(self.getFilterDescription(self.filter))
        cursor.insertBlock()

        db = QtGui.qApp.db
        tableAction = db.table('Action')
        tableActionType = db.table('ActionType')
        tableClient = db.table('Client')
        tableJT = db.table('Job_Ticket')
        tablePerson = db.table('vrbPersonWithSpeciality')

        tableColumns = [columnsMap[x] for x in selectedColumnsMap]

        cols = [
            tableJT['id'],
            tableJT['idx'],
            tableJT['note'],
            tableJT['label'],
            tableJT['datetime'],
            tableClient['lastName'],
            tableClient['firstName'],
            tableClient['patrName'],
            tableClient['sex'],
            tableClient['birthDate'],
            tableActionType['name'].alias('actionTypeName'),
            tablePerson['name'].alias('setPersonName'),
            tableAction['begDate'].alias('begDate'),
            'getClientRegAddress(Client.id) AS regAddress'
        ]

        table = createTable(cursor, tableColumns)
        queryTable, cond, order = self.prepareQueryParts(self.filter)
        db = QtGui.qApp.db
        records = db.getRecordList(queryTable, cols, cond, order)
        prevTicketId = False
        ticketStartRow = 0
        lineNo = 0
        for record in records:
            ticketId = forceRef(record.value('id'))

            clientInfo = u"{clientName}\n{birthDate}\n{address}".format(
                clientName=formatName(record.value('lastName'), record.value('firstName'), record.value('patrName')),
                birthDate=forceString(record.value('birthDate')),
                address=forceString(record.value('regAddress'))
            )
            # key - номер столбца; value - значение столбца
            spaceRow = ' ' * 30

            rowFillingMap = {
                '00': forceInt(record.value('idx')) + 1,
                '01': forceString(record.value('datetime')),
                '02': clientInfo,
                '03': formatSex(forceInt(record.value('sex'))),
                # '04': forceString(record.value('birthDate')),
                '05': forceString(record.value('actionTypeName')),
                '06': ' ,'.join([forceString(record.value('setPersonName')), forceString(record.value('begDate'))]),
                '07': forceString(record.value('label')),
                '08': forceString(record.value('note')),
                '09': '\n'.join([spaceRow] * 3)
            }

            i = table.addRow()
            if prevTicketId == ticketId:
                temp = 0
                for x in sorted(selectedColumnsMap):
                    if x not in ['05', '06']:
                        table.mergeCells(ticketStartRow, temp, i - ticketStartRow + 1, 1)
                    temp += 1

            else:
                prevTicketId = ticketId
                ticketStartRow = i
                lineNo += 1

                temp = 0
                for x in sorted(rowFillingMap.keys()):
                    if x in selectedColumnsMap:
                        if x not in ['05', '06']:
                            table.setText(i, temp, rowFillingMap[x])
                        temp += 1

            if '05' in selectedColumnsMap:
                table.setText(i, selectedColumnsMap.index('05'), rowFillingMap['05'])
            if '06' in selectedColumnsMap:
                table.setText(i, selectedColumnsMap.index('06'), rowFillingMap['06'])

        view = CReportViewDialog(self)
        view.setText(doc)
        view.exec_()

    def clientListReport(self):
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Выполнение работ')
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertText(self.getFilterDescription(self.filter))
        cursor.insertBlock()

        db = QtGui.qApp.db
        tableActionType = db.table('ActionType')
        tableClient = db.table('Client')
        tableJT = db.table('Job_Ticket')
        tablePerson = db.table('vrbPersonWithSpeciality')

        tableColumns = [
            ('5%', [u'№'], CReportBase.AlignRight),
            ('10%', [u'Дата и время'], CReportBase.AlignLeft),
            ('20%', [u'Ф.И.О.'], CReportBase.AlignLeft),
            ('5%', [u'Пол'], CReportBase.AlignLeft),
            ('10%', [u'Дата рождения'], CReportBase.AlignLeft),
            ('20%', [u'Тип действия'], CReportBase.AlignLeft),
            ('15%', [u'Адрес проживания'], CReportBase.AlignLeft),
            ('15%', [u'Адрес регистрации'], CReportBase.AlignLeft)
        ]

        cols = [
            tableJT['id'],
            tableJT['idx'],
            tableJT['datetime'],
            tableClient['lastName'],
            tableClient['firstName'],
            tableClient['patrName'],
            tableClient['sex'],
            tableClient['birthDate'],
            tableActionType['name'].alias('actionTypeName'),
            tablePerson['name'].alias('setPersonName'),
            'getClientRegAddress(Client.id) AS regAddress',
            'getClientLocAddress(Client.id) AS locAddress'
        ]

        table = createTable(cursor, tableColumns)
        queryTable, cond, order = self.prepareQueryParts(self.filter)
        db = QtGui.qApp.db
        records = db.getRecordList(queryTable, cols, cond, order)
        prevTicketId = False
        ticketStartRow = 0
        lineNo = 0
        for record in records:
            ticketId = forceRef(record.value('id'))
            ticketIdx = forceInt(record.value('idx')) + 1
            datetime = forceString(record.value('datetime'))
            name = formatName(record.value('lastName'), record.value('firstName'), record.value('patrName'))
            sex = formatSex(forceInt(record.value('sex')))
            birthDate = forceString(record.value('birthDate'))
            actionTypeName = forceString(record.value('actionTypeName'))
            forceString(record.value('label'))
            i = table.addRow()
            if prevTicketId == ticketId:
                for x in range(len(tableColumns)):
                    if x != 5:
                        table.mergeCells(ticketStartRow, x, i - ticketStartRow + 1, 1)
            else:
                prevTicketId = ticketId
                ticketStartRow = i
                lineNo += 1
                table.setText(i, 0, ticketIdx)
                table.setText(i, 1, datetime)
                table.setText(i, 2, name)
                table.setText(i, 3, sex)
                table.setText(i, 4, birthDate)
                table.setText(i, 6, forceString(record.value('locAddress')))
                table.setText(i, 7, forceString(record.value('regAddress')))
            table.setText(i, 5, actionTypeName)
        view = CReportViewDialog(self)
        view.setText(doc)
        view.exec_()

    def mainPrint(self, reportType=0):
        u"""
        Вывод отчета со списком пациентов со столбцами в зависимости от типа
        :param reportType: тип отчета, влияющий на выводимые поля:
            0 - Основная печать (№, дата, фио, пол, др, тип, назначил, отметка, примечание)
            1 - Список пациентов (добавить адреса пациента и убрать отметку, примечание и назначил)
        :return:
        """
        if not self.filter:
            return

        if reportType == 0:
            self.mainReport()
        elif reportType == 1:
            self.clientListReport()

    @QtCore.pyqtSlot()
    def on_actMainPrint_triggered(self):
        self.mainPrint(0)

    @QtCore.pyqtSlot()
    def on_actClientListPrint_triggered(self):
        self.mainPrint(1)

    @QtCore.pyqtSlot(int)
    def on_actJobTicketListPrint_printByTemplate(self, templateId):
        jobTicketsIdList = self.modelJobTickets.idList()
        makeDependentActionIdList(jobTicketsIdList)
        context = CInfoContext()
        jobTicketsInfoList = context.getInstance(CJobTicketsWithActionsInfoList, tuple(jobTicketsIdList))
        data = {'jobTickets': jobTicketsInfoList}
        applyTemplate(self, templateId, data)

    @QtCore.pyqtSlot(int)
    def on_actActionPrint_printByTemplate(self, templateId):
        context = CInfoContext()
        index = self.tblJobTickets.currentIndex()
        if not index.isValid():
            return
        row = index.row()
        actionId = self.modelJobTickets.getActionId(row)
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

        actionRecord = QtGui.qApp.db.getRecord('Action', '*', actionId)
        eventId = forceRef(actionRecord.value('event_id'))
        eventInfo = context.getInstance(CEventInfo, eventId)

        eventActions = eventInfo.actions
        eventActions._idList = [actionId]
        eventActions._items = [CCookedActionInfo(context, actionRecord, CAction(record=actionRecord))]
        eventActions._loaded = True

        action = eventInfo.actions[0]
        data = {'event'             : eventInfo,
                'action'            : action,
                'client'            : eventInfo.client,
                'actions'           : eventActions,
                'currentActionIndex': 0,
                'tempInvalid'       : None
                }
        QtGui.qApp.restoreOverrideCursor()
        applyTemplate(self, templateId, data)

    def _getJobTicketLabOrders(self, jobTicketIdList):
        db = QtGui.qApp.db
        tableAction = db.table('Action')
        tableAP = db.table('ActionProperty')
        tableAPJT = db.table('ActionProperty_Job_Ticket')
        tableOrder = db.table('{0}.N3LabOrderLog'.format(getLoggerDbName()))

        table = tableAPJT
        table = table.innerJoin(tableAP, tableAP['id'].eq(tableAPJT['id']))
        table = table.innerJoin(tableAction, tableAction['id'].eq(tableAP['action_id']))
        table = table.innerJoin(tableOrder, [tableOrder['event_id'].eq(tableAction['event_id']),
                                             tableOrder['takenTissueJournal_id'].eq(tableAction['takenTissueJournal_id'])])
        return db.getDistinctIdList(table,
                                    tableOrder['id'],
                                    where=[tableAPJT['value'].inlist(jobTicketIdList)],
                                    order=tableOrder['id'].desc())

    def _getJobTicketLabResults(self, jobTicketIdList):
        db = QtGui.qApp.db
        tableOrderResponse = db.table('{0}.N3LabOrderResponseLog'.format(getLoggerDbName()))

        return db.getDistinctIdList(tableOrderResponse,
                                    tableOrderResponse['id'],
                                    where=tableOrderResponse['jobTicket_id'].inlist(jobTicketIdList),
                                    order=tableOrderResponse['id'].desc())

    @QtCore.pyqtSlot()
    def on_btnShowLabOrders_clicked(self):
        date = self.calendar.selectedDate()
        jobTicketIdList = self.tblJobTickets.model().idList()

        dlg = CLabOrderListDialog(self)
        dlg.edtOrderDate.setDate(date)

        orderIdList = self._getJobTicketLabOrders(jobTicketIdList)
        if orderIdList:
            dlg.setOrderIdList(orderIdList)

        orderRsponseIdList = self._getJobTicketLabResults(jobTicketIdList)
        if orderRsponseIdList:
            dlg.setOrderResponseIdList(orderRsponseIdList)

        if orderRsponseIdList and not orderIdList:
            dlg.tabWidget.setCurrentWidget(dlg.tabOrder)

        dlg.exec_()


class CJobTypesModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent, [
            CTextCol(u'Код', ['code'], 6),
            CTextCol(u'Наименование', ['name'], 6),
        ], 'rbJobType')
        self.parentWidget = parent


class CJobTicketsModel(CTableModel):
    class CEQueueStatusCol(CCol):

        def __init__(self, title, fields):
            super(CJobTicketsModel.CEQueueStatusCol, self).__init__(title, fields, 10, 'c', False)
            self._cache = CTableRecordCache(QtGui.qApp.db,
                                            u'vEQueueTicket',
                                            [u'status', u'value'],
                                            idCol='id')

        def format(self, values):
            ticketId = forceRef(values[0])
            if ticketId is not None:
                ticketRecord = self._cache.get(ticketId)
                if ticketRecord:
                    return ticketRecord.value('value')
            return QtCore.QVariant()

        def forceUpdateTicket(self, ticketId=None):
            self._cache.invalidate([ticketId] if ticketId else [])

        def ticketStatus(self, ticketId):
            status = None
            ticketRecord = self._cache.get(ticketId)
            if ticketRecord:
                status = ticketRecord.value('status').toInt()[0]
            return status

        def getBackgroundColor(self, values):
            ticketId = values[0]
            if ticketId:
                status = self.ticketStatus(ticketId)
                if status == EQTicketStatus.Emergency:
                    return QtCore.QVariant(QtGui.QColor(255, 128, 128))
            return CCol.invalid

        def getDecoration(self, values):
            ticketId = values[0]
            if ticketId:
                status = self.ticketStatus(ticketId)

                if status == EQTicketStatus.Issued:
                    return QtCore.QVariant(QtGui.QIcon(':/new/prefix1/icons/eq/clientAvailable.png'))
                elif status in [EQTicketStatus.Ready, EQTicketStatus.Emergency]:
                    return QtCore.QVariant(QtGui.QIcon(':/new/prefix1/icons/eq/clientReady.png'))
                elif status == EQTicketStatus.InProgress:
                    return QtCore.QVariant(QtGui.QIcon(':/new/prefix1/icons/eq/clientProcessed.png'))
                elif status == EQTicketStatus.Complete:
                    return QtCore.QVariant(QtGui.QIcon(':/new/prefix1/icons/eq/clientComplete.png'))
                elif status == EQTicketStatus.Canceled:
                    return QtCore.QVariant(QtGui.QIcon(':/new/prefix1/icons/eq/clientNotAvailable.png'))

            return QtCore.QVariant()

    def __init__(self, parent):
        self.ticketStatusCol = CJobTicketsModel.CEQueueStatusCol(u'', ['eQueueTicket_id'])
        self.clientCol = CLocClientColumn(u'Ф.И.О.', ['id'], 20)
        self.externalIdCol = CLocExternalIdColumn(u'Идентификатор', ['id'], 20, self.clientCol)
        self.statusCol = CLocStatusColumn(u'Состояние', ['status'], 20, self.clientCol)
        self.actionTypeCol = CLocActionTypeColumn(u'Тип действия', ['id'], 20, self.clientCol)
        self.labelCol = CTextCol(u'Отметка', ['label'], 20)
        self.noteCol = CTextCol(u'Примечание', ['note'], 20)

        self.editableCols = (self.ticketStatusCol, self.externalIdCol, self.labelCol, self.noteCol)

        columnsList = [
            self.ticketStatusCol,
            CDateTimeCol(u'Дата и время', ['datetime'], 10),
            self.clientCol,
            CLocClientSexColumn(u'Пол', ['id'], 3, self.clientCol),
            CLocClientBirthDateColumn(u'Дата рожд.', ['id'], 10, self.clientCol),
            self.actionTypeCol,
            CLocPersonColumn(u'Назначил', ['id'], 20, self.clientCol),
            self.labelCol,
            self.noteCol
        ]

        if QtGui.qApp.userHasRight(urShowColumnsInJobsOperDialog):
            columnsList.insert(5, self.statusCol)
            columnsList.insert(5, self.externalIdCol)

        CTableModel.__init__(self, parent, columnsList, 'Job_Ticket')
        self.loadField('master_id')
        self.setTable('Job_Ticket')

        self._updateTicketStatusTimerId = QtCore.QTimer(self)  # self.startTimer(500)
        self._updateTicketStatusTimerId.timeout.connect(self.updateTicketStatus)
        self._updateTicketStatusTimerId.start(500)

        # self.vipClientColor = CMonitoringModel.vipClientColor
        self.vipList = dict()
        if u'онко' in forceString(QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'infisCode')):
            for x in QtGui.qApp.db.getRecordList(
                    QtGui.qApp.db.table('ClientVIP'),
                    [QtGui.qApp.db.table('ClientVIP')['client_id'], QtGui.qApp.db.table('ClientVIP')['color']],
                    [QtGui.qApp.db.table('ClientVIP')['deleted'].eq(0)]
            ):
                self.vipList[forceInt(x.value('client_id'))] = forceString(x.value('color'))

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()
        column, row = index.column(), index.row()
        if role == QtCore.Qt.DisplayRole:  ### or role == Qt.EditRole:
            (col, values) = self.getRecordValues(column, row)

            # if column == 0:
            #     return row + 1

            return col.format(values)
        elif role == QtCore.Qt.BackgroundColorRole:
            idx = self.clientCol.getClientId(forceInt(self.getRecordByRow(row).value('id')))
            if idx in self.vipList:
                return QtCore.QVariant(QtGui.QColor(self.vipList[idx]))
        elif role == QtCore.Qt.UserRole:
            (col, values) = self.getRecordValues(column, row)
            return values[0]
        elif role == QtCore.Qt.TextAlignmentRole:
            col = self._cols[column]
            return col.alignment()
        elif role == QtCore.Qt.CheckStateRole:
            (col, values) = self.getRecordValues(column, row)
            return col.checked(values)
        elif role == QtCore.Qt.ForegroundRole:
            (col, values) = self.getRecordValues(column, row)
            return col.getForegroundColor(values)
        elif role == QtCore.Qt.BackgroundRole:
            (col, values) = self.getRecordValues(column, row)
            return col.getBackgroundColor(values)
        elif role == QtCore.Qt.DecorationRole:
            (col, values) = self.getRecordValues(column, row)
            return col.getDecoration(values)
        return QtCore.QVariant()

    def eQueueTicketId(self, index):
        if index.isValid():
            row = index.row()
            record = self.getRecordByRow(row)
            return forceRef(record.value('eQueueTicket_id')) if record else None

    def eqTicketStatus(self, index):
        status = None
        if index.isValid():
            row = index.row()
            record = self.getRecordByRow(row)
            eqTicketId = forceRef(record.value('eQueueTicket_id')) if record else None
            status = self.ticketStatusCol.ticketStatus(eqTicketId)
        return status

    def flags(self, index):
        result = super(CJobTicketsModel, self).flags(index)
        if index.isValid():
            if self._cols[index.column()] in self.editableCols:
                result = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
        return result

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        row, column = index.row(), index.column()
        ticketId = self.idList()[row]
        if ticketId:
            db = QtGui.qApp.db
            tableJobTicket = db.table('Job_Ticket')

            col = self._cols[column]
            if col == self.externalIdCol and forceString(value):
                tableAction = db.table('Action')
                tableATTT = db.table('ActionType_TissueType')
                tableTTJ = db.table('TakenTissueJournal')

                actionIdList, actionTypeIdList = getJobTicketActionIdList(ticketId)
                tissueTypeIdList = db.getIdList(tableATTT, tableATTT['tissueType_id'], tableATTT['master_id'].inlist(actionTypeIdList))
                if tissueTypeIdList:
                    clientId = self.clientCol.getClientId(ticketId)
                    dateCond = getExternalIdDateCond(tissueTypeIdList[0], QtCore.QDate.currentDate())
                    cond = [tableTTJ['tissueType_id'].inlist(tissueTypeIdList),
                            tableTTJ['externalId'].eq(forceString(value))]
                    if dateCond:
                        cond.append(dateCond)
                    recordTTJ = db.getRecordEx(tableTTJ, tableTTJ['id'], cond)
                    if recordTTJ is not None:
                        QtGui.QMessageBox.information(None, u'Запись существует', u'Запись с данным внешним идентификатором уже существует')
                        return False

                    recordJobTicket = db.getRecordEx(tableJobTicket, tableJobTicket['status'], tableJobTicket['id'].eq(ticketId))
                    if recordJobTicket is not None:
                        status = forceInt(recordJobTicket.value('status'))
                        if status == JobTicketStatus.InProgress:  # выполняется
                            QtGui.QMessageBox.information(None, u'Ошибка', u'Событие имеет статус "Выполняется"')
                            return False
                        elif status == JobTicketStatus.Done:  # закончено
                            QtGui.QMessageBox.information(None, u'Ошибка', u'Событие имеет статус "Закончено"')
                            return False
                    else:
                        QtGui.QMessageBox.information(None, u'Ошибка', u'Не удалось найти номерок')
                        return False

                    if actionIdList:
                        ttjId = db.insertFromDict(tableTTJ, {
                            'client_id'      : clientId,
                            'tissueType_id'  : forceInt(tissueTypeIdList[0]),  # TODO: тип действия может быть связан с несколькими биоматериалами
                            'externalId'     : forceString(value),
                            'number'         : forceString(value),
                            'datetimeTaken'  : QtCore.QDateTime.currentDateTime(),
                            'createDatetime' : QtCore.QDateTime.currentDateTime(),
                            'createPerson_id': QtGui.qApp.userId,
                            'execPerson_id'  : QtGui.qApp.userId
                        })
                        db.updateRecords(tableAction, tableAction['takenTissueJournal_id'].eq(ttjId), tableAction['id'].inlist(actionIdList))

                    else:
                        QtGui.QMessageBox.information(None, u'Ошибка', u'Ошибка при записи идентификатора')
                        return False
                else:
                    QtGui.QMessageBox.information(None, u'Ошибка', u'Не найден тип биоматериала')
                    return False

            elif col == self.labelCol:
                db.updateRecords(tableJobTicket, tableJobTicket['label'].eq(value), tableJobTicket['id'].eq(ticketId))

            elif col == self.noteCol:
                db.updateRecords(tableJobTicket, tableJobTicket['note'].eq(value), tableJobTicket['id'].eq(ticketId))

        return True

    def getIdByRow(self, row):
        return self._idList[row] if row < len(self._idList) else None

    def getJobIdByRow(self, row):
        record = self.getRecordByRow(row)
        return forceRef(record.value('master_id')) if record else None

    @QtCore.pyqtSlot(int)
    def updateTicketStatus(self, ticketId=None):
        self.ticketStatusCol.forceUpdateTicket(ticketId)
        self.dataChanged.emit(self.index(0, 0),
                              self.index(self.rowCount() - 1, 0))

    def getActionTypeId(self, row):
        ticketId = self.getIdByRow(row)
        return self.actionTypeCol.getActionTypeId(ticketId)

    def getClientIdByRow(self, row):
        ticketId = self.getIdByRow(row)
        return self.getClientId(ticketId)

    def getClientId(self, ticketId):
        return self.clientCol.getClientId(ticketId)

    def getActionId(self, row):
        ticketId = self.getIdByRow(row)
        return self.clientCol.getActionId(ticketId)

    def getServiceSuperviseUnit(self, ticketId):
        actionTypeCode = self.clientCol.getActionTypeCode(ticketId)
        return forceDouble(QtGui.qApp.db.translate('rbService', 'code', actionTypeCode, 'superviseComplexityFactor')) if actionTypeCode else None


class CLocClientColumn(CCol):
    def __init__(self, title, fields, defaultWidth):
        CCol.__init__(self, title, fields, defaultWidth, 'l')
        db = QtGui.qApp.db
        self.mapTicketIdToActionPropertyId = {}
        self.APCache = CTableRecordCache(db, db.table('ActionProperty'), 'action_id')
        self.ActionCache = CTableRecordCache(db, db.table('Action'), 'actionType_id, event_id, setPerson_id, takenTissueJournal_id')
        self.actionTypeCache = CTableRecordCache(db, db.table('ActionType'), 'name, code')
        self.eventCache = CTableRecordCache(db, db.table('Event'), 'client_id')
        self.personCache = CTableRecordCache(db, db.table('vrbPersonWithSpeciality'), 'name')
        self.clientCache = CTableRecordCache(db, db.table('Client'), 'firstName, lastName, patrName, birthDate, sex')
        self.externalIdCashe = CTableRecordCache(db, db.table('TakenTissueJournal'), 'externalId')

    def getActionRecord(self, ticketId):
        actionId = self.getActionId(ticketId)
        return self.ActionCache.get(actionId) if actionId else None

    def getActionTypeCode(self, ticketId):
        actionRecord = self.getActionRecord(ticketId) if ticketId else None
        actionTypeRecord = self.actionTypeCache.get(forceRef(actionRecord.value('actionType_id'))) if actionRecord else None
        return forceString(actionTypeRecord.value('code')) if actionTypeRecord else None

    def getActionId(self, ticketId):
        db = QtGui.qApp.db
        actionPropertyId = self.mapTicketIdToActionPropertyId.get(ticketId, -1)
        if actionPropertyId == -1:
            actionPropertyId = forceRef(db.translate('ActionProperty_Job_Ticket', 'value', ticketId, 'id'))
            self.mapTicketIdToActionPropertyId[ticketId] = actionPropertyId
        record = self.APCache.get(actionPropertyId) if actionPropertyId else None
        return forceRef(record.value('action_id')) if record else None

    def getExternalIdRecord(self, tickedId):
        record = self.getActionRecord(tickedId)
        journalId = self.externalIdCashe.get(forceRef(record.value('takenTissueJournal_id'))) if record else None
        return forceString(journalId.value('externalId')) if journalId else None

    def getClientRecord(self, ticketId):
        clientId = self.getClientId(ticketId)
        return self.clientCache.get(clientId) if clientId else None

    def getClientId(self, ticketId):
        record = self.getActionRecord(ticketId)
        eventId = forceRef(record.value('event_id')) if record else None
        record = self.eventCache.get(eventId)
        clientId = forceRef(record.value('client_id')) if record else None
        return clientId

    def format(self, values):
        ticketId = forceRef(values[0])
        record = self.getClientRecord(ticketId)
        if record:
            name = formatName(record.value('lastName'),
                              record.value('firstName'),
                              record.value('patrName'))
            return toVariant(name)
        else:
            return CCol.invalid

    def invalidateRecordsCache(self):
        self.mapTicketIdToActionPropertyId = {}
        self.APCache.invalidate()
        self.ActionCache.invalidate()
        self.actionTypeCache.invalidate()
        self.eventCache.invalidate()
        self.personCache.invalidate()
        self.clientCache.invalidate()


class CLocClientBirthDateColumn(CCol):
    def __init__(self, title, fields, defaultWidth, master):
        CCol.__init__(self, title, fields, defaultWidth, 'l')
        self.master = master

    def format(self, values):
        ticketId = forceRef(values[0])
        record = self.master.getClientRecord(ticketId)
        if record:
            return toVariant(forceString(record.value('birthDate')))
        else:
            return CCol.invalid


class CLocClientSexColumn(CCol):
    def __init__(self, title, fields, defaultWidth, master):
        CCol.__init__(self, title, fields, defaultWidth, 'l')
        self.master = master

    def format(self, values):
        ticketId = forceRef(values[0])
        record = self.master.getClientRecord(ticketId)
        if record:
            return toVariant(formatSex(record.value('sex')))
        else:
            return CCol.invalid


class CLocActionTypeColumn(CCol):
    def __init__(self, title, fields, defaultWidth, master):
        CCol.__init__(self, title, fields, defaultWidth, 'l')
        self.master = master

    def format(self, values):
        ticketId = forceRef(values[0])
        actionTypeId = self.getActionTypeId(ticketId)
        record = self.master.actionTypeCache.get(actionTypeId) if actionTypeId else None
        if record:
            return toVariant(forceString(record.value('name')))
        else:
            return CCol.invalid

    def getActionTypeId(self, ticketId):
        record = self.master.getActionRecord(ticketId) if ticketId else None
        return forceRef(record.value('actionType_id')) if record else None


class CLocPersonColumn(CCol):
    def __init__(self, title, fields, defaultWidth, master):
        CCol.__init__(self, title, fields, defaultWidth, 'l')
        self.master = master

    def format(self, values):
        ticketId = forceRef(values[0])
        record = self.master.getActionRecord(ticketId)
        setPersonId = forceRef(record.value('setPerson_id')) if record else None
        record = self.master.personCache.get(setPersonId) if setPersonId else None
        if record:
            return toVariant(forceString(record.value('name')))
        else:
            return CCol.invalid


class CLocStatusColumn(CCol):
    def __init__(self, title, fields, defaultWidth, master):
        CCol.__init__(self, title, fields, defaultWidth, 'l')
        self.master = master

    def format(self, values):
        status = forceInt(values[0])
        if status in JobTicketStatus.nameMap:
            return toVariant(JobTicketStatus.nameMap[status])
        return CCol.invalid


class CLocExternalIdColumn(CCol):
    def __init__(self, title, fields, defaultWidth, master):
        CCol.__init__(self, title, fields, defaultWidth, 'l')
        self.master = master

    def format(self, values):
        tickedId = forceRef((values[0]))
        record = self.master.getExternalIdRecord(tickedId)
        if record:
            return toVariant(forceString(record))
        else:
            return None
