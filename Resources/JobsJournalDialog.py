# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2016 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Accounting.Utils import isShowJobTickets
from Events.Action import CAction, CActionTypeCache
from Events.ActionInfo import CCookedActionInfo
from Events.AmbCardPage import CAmbCardDialog
from Events.EventInfo import CClientInfo, CEventInfo
from HospitalBeds.HospitalizationEventDialog import CHospitalizationEventDialog
from Orgs.OrgStructComboBoxes import COrgStructureComboBox, COrgStructureModel
from Orgs.Utils import getOrgStructureFullName, getPersonInfo
from Registry.Utils import getStaffCondition
from Reports.ReportBase import CReportBase, createTable
from Reports.ReportView import CReportViewDialog
from Resources.JobTicketChooser import CJobTicketChooserComboBox, CJobTicketChooserDialog
from Resources.JobTicketEditor import CJobTicketEditor
from Resources.JobTicketEditor2 import CJobTicketEditor2
from Resources.JobTicketInfo import CJobTicketsWithActionsInfoList, getJobTicketClientIdList, makeDependentActionIdList
from Resources.JobsOperatingDialog import CJobTypesModel, CLocActionTypeColumn, CLocClientBirthDateColumn, CLocExternalIdColumn, CLocPersonColumn, CLocStatusColumn
from Resources.Utils import JobTicketStatus
from Ui_JobsJournalDialog import Ui_JobsJournalDialog
from Users.Rights import urEQCalling, urEQManaging, urEQSettings
from library.DialogBase import CDialogBase
from library.ElectronicQueue.EQController import CEQController
from library.ElectronicQueue.EQTicketModel import EQTicketStatus
from library.PrintInfo import CInfoContext
from library.PrintTemplates import applyTemplate, getPrintAction
from library.TableModel import CCol, CDateTimeCol, CTableModel
from library.Utils import agreeNumberAndWord, forceDate, forceDouble, forceInt, forceRef, forceString, forceStringEx, formatName, formatSex, toVariant
from library.database import CTableRecordCache


class CJobsJournalDialog(CDialogBase, Ui_JobsJournalDialog):
    eqSummon = QtCore.pyqtSignal(int, int, int) # eQueueTypeId, eqTicketId, orgStructureId
    eqEmergency = QtCore.pyqtSignal(int, int)   # eQueueTypeId, eqTicketId
    eqComplete = QtCore.pyqtSignal(int, int)    # eQueueTypeId, eqTicketId
    eqCancel = QtCore.pyqtSignal(int, int)      # eQueueTypeId, eqTicketId
    eqReady = QtCore.pyqtSignal(int, int)       # eQueueTypeId, eqTicketId
    eqIssued = QtCore.pyqtSignal(int, int)      # eQueueTypeId, eqTicketId

    def __init__(self, parent):
        CDialogBase.__init__(self, parent)

        self.jobSuperviseInfo = {}
        self.jobTicketOrderColumn = None
        self.jobTicketOrderAscending = True
        self.eQueueTypeId = None

        self.addModels('OrgStructure', COrgStructureModel(self, QtGui.qApp.currentOrgId(), headerName=u'Структура ЛПУ: фильтр по назначившему'))
        self.addModels('OrgStructureWithBeds', COrgStructureModel(self, filter='hasHospitalBedsStructure(id)=1', headerName=u'Структура ЛПУ: фильтр по отделению пациента'))
        self.addModels('JobTypes', CJobTypesModel(self))

        self.addModels('JobTickets', CJobTicketsModel(self))

        self.actMainPrint = QtGui.QAction(u'Основная печать списка', self)

        self.actMainPrint.setObjectName('actMainPrint')
        self.actClientListPrint = QtGui.QAction(u'Список пациентов', self)
        self.actClientListPrint.setObjectName('actClientListPrint')
        self.actJobTicketListPrint = getPrintAction(self, None, u'Печать списка', False)
        self.actJobTicketListPrint.setObjectName('actJobTicketListPrint')
        self.actActionPrint = getPrintAction(self, None, u'Печать мероприятия')
        self.actActionPrint.setObjectName('actActionPrint')
        self.actJobsJournalPrint = getPrintAction(self, 'jobsJournal', u'Напечатать шаблон')
        self.actJobsJournalPrint.setObjectName('actJobsJournalPrint')
        self.btnPrint = QtGui.QPushButton(u'Печать', self)
        self.btnPrint.setObjectName('btnPrint')
        self.btnReg = QtGui.QPushButton(u'Зарегистрировать', self)
        self.btnReg.setObjectName('btnReg')
        self.mnuBtnPrint = QtGui.QMenu(self)
        self.mnuBtnPrint.setObjectName('mnuBtnPrint')
        self.mnuBtnPrint.addAction(self.actMainPrint)
        self.mnuBtnPrint.addAction(self.actClientListPrint)
        self.mnuBtnPrint.addSeparator()
        self.mnuBtnPrint.addAction(self.actJobTicketListPrint)
        self.mnuBtnPrint.addSeparator()
        self.mnuBtnPrint.addAction(self.actActionPrint)
        self.mnuBtnPrint.addAction(self.actJobsJournalPrint)
        self.btnPrint.setMenu(self.mnuBtnPrint)

        self.setupUi(self)

        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setModels(self.tblJobTickets, self.modelJobTickets, self.selectionModelJobTickets)

        self.cmbClientAccountingSystem.setTable('rbAccountingSystem', addNone=True)
        self.cmbSpeciality.setTable('rbSpeciality', True)
        self.cmbTissueType.setTable('rbTissueType', addNone=True, specialValues=[(-1, '-', u'любой биоматериал'), (-2, '-', u'без биоматериала')])
        self.cmbTakenTissueType.setTable('rbTissueType', addNone=True, specialValues=[(-1, '-', u'любой биоматериал'), (-2, '-', u'без биоматериала')])
        self.cmbTissueType.setValue(None)
        self.cmbTakenTissueType.setValue(None)
        self.filter = {}
        self.resetFilter()

        self.lblSuperviseInfo.setText("")

        self.updateJobTicketList() # Added (issue 644)

        self.connect(self.tblJobTickets.horizontalHeader(), QtCore.SIGNAL('sectionClicked(int)'), self.setSortJobTicketsByColumn)
        self.buttonBox.addButton(self.btnPrint, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btnReg, QtGui.QDialogButtonBox.ActionRole)
        self.btnReg.clicked.connect(self.reg)

        self.actAmbCardShow = QtGui.QAction(u'Медицинская карта', self)

        self.actEQSummon = QtGui.QAction(u'Вызвать пациента', self, triggered=self.on_actEQSummon_triggered)
        self.actEQComplete = QtGui.QAction(u'Завершить успешно', self, triggered=self.on_actEQComplete_triggered)
        self.actEQCancel = QtGui.QAction(u'Отменить вызов', self, triggered=self.on_actEQCancel_triggered)
        self.actEQEmergency = QtGui.QAction(u'Вне очереди', self, triggered=self.on_actEQEmergency_triggered)
        self.actEQReady = QtGui.QAction(u'Готов к вызову', self, triggered=self.on_actEQReady_triggered)
        self.actEQIssued = QtGui.QAction(u'Не готов к вызову', self, triggered=self.on_actEQIssued_triggered)

        self.tblJobTickets.createPopupMenu([self.actAmbCardShow,
                                            '-',
                                            self.actEQSummon,
                                            self.actEQEmergency,
                                            self.actEQComplete,
                                            self.actEQCancel,
                                            self.actEQReady,
                                            self.actEQIssued])
        self.tblJobTickets.addPopupAction(self.actAmbCardShow)
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

        self.tblJobTickets.addPopupSeparator()

        self.actChangeAddedActions = QtGui.QAction(u'Изменить', self)
        self.tblJobTickets.addPopupAction(self.actChangeAddedActions)
        self.connect(self.actChangeAddedActions, QtCore.SIGNAL('triggered()'), self.on_addChangeAddedActions)

        #self.actAddAddedActions = QtGui.QAction(u'Добавить', self)
        #self.tblJobTickets.addPopupAction(self.actAddAddedActions)
        #self.connect(self.actAddAddedActions, QtCore.SIGNAL('triggered()'), self.on_addSelectedActionRows)

        #self.actDelAddedActions = QtGui.QAction(u'Удалить', self)
        #self.tblJobTickets.addPopupAction(self.actDelAddedActions)
        #self.connect(self.actDelAddedActions, QtCore.SIGNAL('triggered()'), self.on_removeSelectedActionRows)

        self.chkClientLastName.toggled.connect(self.chkClientLastName_clicked)
        self.chkClientFirstName.clicked.connect(self.chkClientFirstName_clicked)
        self.chkClientPatrName.clicked.connect(self.chkClientPatrName_clicked)
        self.chkClientId.clicked.connect(self.chkClientId_clicked)
        self.chkJobTicketId.clicked.connect(self.edtJobTicketId_clicked)

        self.rejected.connect(self.close)

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

    def on_addChangeAddedActions(self):
        self.editCurrentJobTicket()

    def reg(self):
        regDialog = CHospitalizationEventDialog(self, self.parent)
        regDialog.btnCommit.setText(u"Назначить (Пробел)")
        regDialog.setWindowTitle(u"Регистрация")

        if regDialog:
            regDialog.exec_()

    def closeEvent(self, event):
        eqController = CEQController.getInstance()
        eqController.controlModel().guiControl().removeWidget(self.eqControlWidget)
        super(CJobsJournalDialog, self).closeEvent(event)
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
        idx = self.tblJobTickets.currentIndex()
        eqTicketId = self.modelJobTickets.eQueueTicketId(idx)
        if self.eQueueTypeId and eqTicketId:
            self.eqReady.emit(self.eQueueTypeId, eqTicketId)

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

        self.actEQReady.setEnabled(isEnabled and status != EQTicketStatus.Ready)
        self.actEQIssued.setEnabled(isEnabled and status != EQTicketStatus.Issued)
        self.actEQComplete.setEnabled(isEnabled and status != EQTicketStatus.Complete)
        self.actEQCancel.setEnabled(isEnabled and status != EQTicketStatus.Canceled)
        self.actEQEmergency.setEnabled(isEnabled and status != EQTicketStatus.Emergency)
        self.actEQSummon.setEnabled(isEnabled and status in [EQTicketStatus.Ready, EQTicketStatus.InProgress, EQTicketStatus.Emergency])

    def on_actAmbCardShow(self):
        jobTicketId = self.tblJobTickets.currentItemId()
        clientId = self.modelJobTickets.getClientId(jobTicketId)
        CAmbCardDialog(self, clientId).exec_()

    def on_actScanBarcode(self):
        self.setCheckedAndEmit(self.chkJobTicketId, True)
        self.edtJobTicketId.clear()
        self.edtJobTicketId.setFocus(QtCore.Qt.OtherFocusReason)

    def getOrgStructIdList(self):
        # pass
        # treeIndex = self.treeOrgStructure.currentIndex()
        # treeItem = treeIndex.internalPointer() if treeIndex.isValid() else None
        # if treeItem:
        #     return treeItem.getItemIdList()
        return []

    def getJobTypeIdList(self, orgStructIdList, date, dateTo=None):
        if orgStructIdList:
            db = QtGui.qApp.db
            tableJob = db.table('Job')
            tableOrgStructureJob = db.table('OrgStructure_Job')
            cond = [tableJob['deleted'].eq(0),
                    tableJob['jobType_id'].isNotNull(),
                    tableOrgStructureJob['master_id'].inlist(orgStructIdList),
                    ]
            if dateTo is None:
                cond.append(tableJob['date'].dateGe(date))
            else:
                cond.append(tableJob['date'].dateGe(date))
                cond.append(tableJob['date'].dateLe(dateTo))
            tableJobType = db.table('rbJobType')

            table = tableJob.join(tableJobType, tableJobType['id'].eq(tableJob['jobType_id']))
            table = table.join(tableOrgStructureJob, tableOrgStructureJob['id'].eq(tableJob['orgStructureJob_id']))
            return db.getDistinctIdList(table, idCol='Job.jobType_id', where=cond, order='rbJobType.name')
        return []

    def updateJobTypeList(self):
        return
        # orgStructIdList = self.getOrgStructIdList()
        # return
        # if self.btnCalendarDate.isChecked():
        #     date = self.calendar.selectedDate()
        #     dateTo = None
        # elif self.btnDateRange.isChecked():
        # date = self.edtDateRangeFrom.date()
        # dateTo = self.edtDateRangeTo.date()
        # else:
        #     return
        # jobTypeIdList = self.getJobTypeIdList(orgStructIdList, date, dateTo)
        # self.tblJobTypes.setIdList(jobTypeIdList)

    def resetFilter(self):
        self.chkAwaiting.setChecked(True)
        self.chkInProgress.setChecked(False)
        self.chkDone.setChecked(False)
        self.chkOnlyUrgent.setChecked(False)
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

        #self.setCheckedAndEmit(self.btnCalendarDate, True)

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
            'date'                    : QtCore.QDate.currentDate(),  # self.calendar.selectedDate(),
            # 'orgStructIdList': self.getOrgStructIdList(),
            'jobTypeId'               : None,  # self.tblJobTypes.currentItemId(),
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
            # 'chkCalendarDate': self.btnCalendarDate.isChecked(),
            'chkDateRange'            : True,  # self.btnDateRange.isChecked(),
            'dateRangeFrom'           : self.edtDateRangeFrom.date(),
            'dateRangeTo'             : self.edtDateRangeTo.date()
        }

    def prepareQueryPartsByJobTicketId(self, jobTicketId):
        db = QtGui.qApp.db
        table = db.table('Job_Ticket')
        tableAPJT = db.table('ActionProperty_Job_Ticket')
        tableAP = db.table('ActionProperty')
        tableAction = db.table('Action')
        tableActionType = db.table('ActionType')
        tablePerson = db.table('vrbPersonWithSpeciality')
        tableEvent = db.table('Event')
        tableClient = db.table('Client')
        tableJob = db.table('Job')
        tableIdentification = db.table('ClientIdentification')
        tableOrgStructureJob = db.table('OrgStructure_Job')
        tableEQueueTicket = db.table('EQueueTicket')
        tableEQueue = db.table('EQueue')
        queryTable = table
        queryTable = queryTable.leftJoin(tableJob, tableJob['id'].eq(table['master_id']))
        queryTable = queryTable.leftJoin(tableOrgStructureJob, tableOrgStructureJob['id'].eq(tableJob['orgStructureJob_id']))
        queryTable = queryTable.leftJoin(tableAPJT, tableAPJT['value'].eq(table['id']))
        queryTable = queryTable.leftJoin(tableAP, tableAP['id'].eq(tableAPJT['id']))
        queryTable = queryTable.leftJoin(tableAction, tableAction['id'].eq(tableAP['action_id']))
        queryTable = queryTable.leftJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
        queryTable = queryTable.leftJoin(tablePerson, tablePerson['id'].eq(tableAction['setPerson_id']))
        queryTable = queryTable.leftJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
        queryTable = queryTable.leftJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))
        queryTable = queryTable.leftJoin(tableEQueueTicket, tableEQueueTicket['id'].eq(table['eQueueTicket_id']))
        queryTable = queryTable.leftJoin(tableEQueue, tableEQueue['id'].eq(tableEQueueTicket['queue_id']))
        order = self.getOrder()
        return queryTable, table['id'].eq(jobTicketId), order

    def prepareQueryParts(self, filter):
        isClientFilter = True  # self.tabDateClientFilter.widget(self.tabDateClientFilter.currentIndex()) == self.tabClientFilter
        date = filter['date']
        # orgStructIdList = filter['orgStructIdList']
        # jobTypeId = filter['jobTypeId']
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
        # chkCalendarDate = filter['chkCalendarDate']
        chkDateRange = filter['chkDateRange']
        dateRangeFrom = filter['dateRangeFrom']
        dateRangeTo = filter['dateRangeTo']

        if chkJobTicketId:
            return self.prepareQueryPartsByJobTicketId(jobTicketId)

        db = QtGui.qApp.db
        tableJobTicket = db.table('Job_Ticket')
        tableAPJT = db.table('ActionProperty_Job_Ticket')
        tableAP = db.table('ActionProperty')
        tableAction = db.table('Action')
        tableActionType = db.table('ActionType')
        tablePerson = db.table('vrbPersonWithSpeciality')
        tableEvent = db.table('Event')
        tableClient = db.table('Client')
        tableJob = db.table('Job')
        tableIdentification = db.table('ClientIdentification')
        tableOrgStructureJob = db.table('OrgStructure_Job')
        tableEQueueTicket = db.table('EQueueTicket')
        tableEQueue = db.table('EQueue')

        queryTable = tableJobTicket
        queryTable = queryTable.leftJoin(tableJob, tableJob['id'].eq(tableJobTicket['master_id']))
        queryTable = queryTable.leftJoin(tableOrgStructureJob, tableOrgStructureJob['id'].eq(tableJob['orgStructureJob_id']))
        queryTable = queryTable.leftJoin(tableAPJT, tableAPJT['value'].eq(tableJobTicket['id']))
        queryTable = queryTable.leftJoin(tableAP, tableAP['id'].eq(tableAPJT['id']))
        queryTable = queryTable.leftJoin(tableAction, tableAction['id'].eq(tableAP['action_id']))
        queryTable = queryTable.leftJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
        queryTable = queryTable.leftJoin(tablePerson, tablePerson['id'].eq(tableAction['setPerson_id']))
        queryTable = queryTable.leftJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
        queryTable = queryTable.leftJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))
        queryTable = queryTable.leftJoin(tableEQueueTicket, tableEQueueTicket['id'].eq(tableJobTicket['eQueueTicket_id']))
        queryTable = queryTable.leftJoin(tableEQueue, tableEQueue['id'].eq(tableEQueueTicket['queue_id']))

        cond = []
        if awaiting and inProgress and done:
            pass
        else:
            statuses = []
            if awaiting: statuses.append(JobTicketStatus.Awaiting)
            if inProgress: statuses.append(JobTicketStatus.InProgress)
            if done: statuses.append(JobTicketStatus.Done)
            cond.append(tableJobTicket['status'].inlist(statuses))
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
                        queryTable = queryTable.innerJoin(tableIdentification,
                                                          tableIdentification['client_id'].eq(tableClient['id']))
                        cond.extend(
                            [tableIdentification['accountingSystem_id'].eq(clientAccountingSystemId),
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
            if chkDateRange:
                cond.append(tableJob['date'].dateGe(dateRangeFrom))
                cond.append(tableJob['date'].dateLe(dateRangeTo))
        else:
            #if chkCalendarDate:
                #cond.append(tableJob['date'].dateGe(date))
            if chkDateRange:
                cond.append(tableJob['date'].dateGe(dateRangeFrom))
                cond.append(tableJob['date'].dateLe(dateRangeTo))

        if not QtGui.qApp.isDisplayStaff():
            cond.append('NOT (%s)' % getStaffCondition(tableClient['id'].name()))

        order = self.getOrder()
        cond = cond + [#tableJob['jobType_id'].eq(jobTypeId),
                       #tableOrgStructureJob['master_id'].inlist(orgStructIdList),
                       tableAction['deleted'].eq(0),
                       tableEvent['deleted'].eq(0),
                       tableClient['deleted'].eq(0),
                       ]

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

    def updateJobTicketList(self):
        filter = self.getFilter()
        queryTable, cond, order = self.prepareQueryParts(filter)
        db = QtGui.qApp.db
        idList = []
        actionIdList = []
        amountCount = 0

        recordList = db.getRecordList(queryTable,
                                      'Job_Ticket.id AS  jobTicketId, Action.id AS actionId, Action.amount AS actionAmount, Job.id AS jobId, EQueue.eQueueType_id AS queueTypeId',
                                      cond, order)

        queueTypeIdList = []
        for record in recordList:
            jobTicketId = forceRef(record.value('jobTicketId'))
            jobId = forceRef(record.value('jobId'))
            actionId = forceRef(record.value('actionId'))
            queueTypeId = forceRef(record.value('queueTypeId'))
            if queueTypeId not in queueTypeIdList:
                queueTypeIdList.append(queueTypeId)

            if (not jobTicketId in idList) and isShowJobTickets(jobId, actionId):
                idList.append(jobTicketId)

            if not actionId in actionIdList:
                actionIdList.append(actionId)
                actionAmount = forceDouble(record.value('actionAmount'))
                amountCount += actionAmount

        self.eQueueTypeId = queueTypeIdList[0] if len(queueTypeIdList) == 1 else None
        self.filter = filter

        rowCount = int(self.edtFilterListLength.text())

        viewedIdList = idList[:rowCount] if len(idList) > rowCount and self.chkFilterListLength.isChecked() else idList

        self.tblJobTickets.setIdList(viewedIdList)
        if filter['chkJobTicketId'] and idList:
            self.setValuesByJobTicketId(idList[0])

        idListInfo = u'Всего найдено записей: %d' % len(idList)
        actionsInfo = u'Всего мероприятий: %d' % len(actionIdList)
        amountInfo = u'Всего услуг: %d' % amountCount
        viewedInfo = u'Показано записей: %d' % len(viewedIdList)
        self.lblTicketsCount.setText(u'\n'.join([
            idListInfo,
            # jobTicketsInfo,
            actionsInfo,
            amountInfo,
            viewedInfo
        ]))

        self.jobSuperviseInfo = CJobTicketChooserDialog.getJobTicketsInfo(None,  # filter['jobTypeId'],
                                                                          filter['date'],
                                                                          filter['clientId'],
                                                                          None,
                                                                          {},
                                                                          [])[4]
        self.updateSuperviceUnitInfo(self.tblJobTickets.currentIndex())

    def setValuesByJobTicketId(self, jobTicketId):
        db = QtGui.qApp.db
        record = db.getRecord('Job_Ticket', 'datetime, master_id', jobTicketId)
        if record:
            date = forceDate(record.value('datetime'))
            jobTypeId = forceRef(db.translate('Job', 'id', forceRef(record.value('master_id')), 'jobType_id'))
            # if self.btnCalendarDate.isChecked():
            #     self.calendar.setSelectedDate(date)
            # elif self.btnDateRange.isChecked():
            self.edtDateRangeFrom.setDate(date)
            self.edtDateRangeTo.setDate(date)
            # else:
            #     return
            jobTypeIdList = self.modelJobTypes.idList()
            if jobTypeId in jobTypeIdList:
                row = jobTypeIdList.index(jobTypeId)
                self.tblJobTypes.setCurrentIndex(self.modelJobTypes.index(row, 0))

    def editCurrentJobTicketOld(self):
        jobTicketId = self.tblJobTickets.currentItemId()
        if jobTicketId:
            dialog = CJobTicketEditor(self)
            dialog.load(jobTicketId)
            if dialog.exec_():
                self.updateJobTicketList()

    def editCurrentJobTicket(self):
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
        # return
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


    @QtCore.pyqtSlot()
    def on_calendar_selectionChanged(self):
        self.updateJobTypeList()

    # @QtCore.pyqtSlot(bool)
    # def on_btnCalendarDate_clicked(self, value):
    #     self.updateJobTypeList()


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
        self.lblTicketsCount.setText("")

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBoxFilter_clicked(self, button):
        buttonCode = self.buttonBoxFilter.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.updateJobTicketList()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.resetFilter()
            self.updateJobTicketList()

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblJobTickets_doubleClicked(self, index):
        # return
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

    def updateSuperviceUnitInfo(self, index):
        return
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

    ## Вывод отчета со списком пациентов со столбцами в зависимости от типа:
    #    @param reportType: тип отчета, влияющий на выводимые поля:
    #        0 - Основная печать (№, дата, фио, пол, др, тип, назначил, отметка, примечание)
    #        1 - Список пациентов (добавить адреса пациента и убрать отметку, примечание и назначил)
    def mainPrint(self, reportType=0):
        if not self.filter:
            return
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Выполнение работ')
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertText(self.getFilterDescription(self.filter))
        cursor.insertBlock()

        tableColumns = [
            ('5%', [u'№'], CReportBase.AlignRight),
            ('10%', [u'Дата и время'], CReportBase.AlignLeft),
            ('20%', [u'Ф.И.О.'], CReportBase.AlignLeft),
            ('5%', [u'Пол'], CReportBase.AlignLeft),
            ('10%', [u'Дата рождения'], CReportBase.AlignLeft),
            ('20%', [u'Назначение'], CReportBase.AlignLeft)
        ]

        cols = ['Job_Ticket.id', 'Job_Ticket.datetime',
                'Client.lastName', 'Client.firstName', 'Client.patrName',
                'Client.sex', 'Client.birthDate',
                'ActionType.name AS actionTypeName',
                'vrbPersonWithSpeciality.name AS setPersonName', 'Job_Ticket.idx'
                ]

        if reportType == 1:
            tableColumns.extend([
                ('15%', [u'Адрес проживания'], CReportBase.AlignLeft),
                ('15%', [u'Адрес регистрации'], CReportBase.AlignLeft)
            ])
            cols.extend(['getClientRegAddress(Client.id) AS regAddress',
                         'getClientLocAddress(Client.id) AS locAddress'])
        else:
            tableColumns.extend([
                ('20%', [u'Назначил, дата'], CReportBase.AlignLeft),
                # ('10%', [u'Выполнил'], CReportBase.AlignLeft),
                # ('10%', [u'Идентификатор БМ'], CReportBase.AlignLeft),
                # ('10%', [u'Биоматериал'], CReportBase.AlignLeft)
                ('10%', [u'Отметка'], CReportBase.AlignLeft),
                ('10%', [u'Примечание'], CReportBase.AlignLeft),
            ])
            cols.extend(['Action.begDate as begDate',
                         'Job_Ticket.label',
                         'Job_Ticket.note'])

        table = createTable(cursor, tableColumns)
        queryTable, cond, order = self.prepareQueryParts(self.filter)
        db = QtGui.qApp.db
        records = db.getRecordList(queryTable,
                                   cols,
                                   cond, order)
        prevTicketId = False
        ticketStartRow = 0
        lineNo = 0
        for record in records:
            ticketId = forceRef(record.value('id'))
            ticketIdx = forceInt(record.value('idx')) + 1
            datetime = forceString(record.value('datetime'))
            name = formatName(record.value('lastName'),
                              record.value('firstName'),
                              record.value('patrName'))
            sex = formatSex(forceInt(record.value('sex')))
            birthDate = forceString(record.value('birthDate'))
            actionTypeName = forceString(record.value('actionTypeName'))
            setPersonDate = ' ,'.join([forceString(record.value('setPersonName')),
                                       forceString(record.value('begDate'))])
            forceString(record.value('label'))
            note = forceString(record.value('note'))
            i = table.addRow()
            if prevTicketId == ticketId:
                table.mergeCells(ticketStartRow, 0, i - ticketStartRow + 1, 1)
                table.mergeCells(ticketStartRow, 1, i - ticketStartRow + 1, 1)
                table.mergeCells(ticketStartRow, 2, i - ticketStartRow + 1, 1)
                table.mergeCells(ticketStartRow, 3, i - ticketStartRow + 1, 1)
                table.mergeCells(ticketStartRow, 4, i - ticketStartRow + 1, 1)
                if reportType == 1:
                    table.mergeCells(ticketStartRow, 6, i - ticketStartRow + 1, 1)
                table.mergeCells(ticketStartRow, 7, i - ticketStartRow + 1, 1)
                if reportType == 0:
                    table.mergeCells(ticketStartRow, 8, i - ticketStartRow + 1, 1)
            else:
                prevTicketId = ticketId
                ticketStartRow = i
                lineNo += 1
                table.setText(i, 0, ticketIdx)
                table.setText(i, 1, datetime)
                table.setText(i, 2, name)
                table.setText(i, 3, sex)
                table.setText(i, 4, birthDate)
                if reportType == 1:
                    table.setText(i, 6, forceString(record.value('locAddress')))
                table.setText(i, 7, forceString(record.value('label')) if reportType == 0 else forceString(record.value('regAddress')))
                if reportType == 0:
                    table.setText(i, 8, note)

            table.setText(i, 5, actionTypeName)
            if reportType == 0:
                table.setText(i, 6, setPersonDate)

        view = CReportViewDialog(self)
        view.setText(doc)
        view.exec_()

    @QtCore.pyqtSlot()
    def on_actMainPrint_triggered(self):
        self.mainPrint(0)

    @QtCore.pyqtSlot()
    def on_actClientListPrint_triggered(self):
        self.mainPrint(1)

    @QtCore.pyqtSlot(int)
    def on_actJobsJournalPrint_printByTemplate(self, templateId):
        currIndex = self.tblJobTickets.currentIndex()
        if not currIndex.isValid():
            return

        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

        jobTicketIdList = self.modelJobTickets.idList()
        clientIdList = getJobTicketClientIdList(jobTicketIdList)
        makeDependentActionIdList(jobTicketIdList)

        actionId = self.modelJobTickets.getActionId(currIndex.row())
        actionRec = QtGui.qApp.db.getRecord('Action', '*', actionId)

        context = CInfoContext()
        eventInfo = context.getInstance(CEventInfo, forceRef(actionRec.value('event_id')))
        eventActions = eventInfo.actions
        eventActions._idList = [actionId]
        eventActions._items = [CCookedActionInfo(context, actionRec, CAction(record=actionRec))]
        eventActions._loaded = True

        data = {
            'event'     : eventInfo,
            'action'    : eventInfo.actions[0],
            'client'    : eventInfo.client,
            'actions'   : eventActions,
            'clients'   : [context.getInstance(CClientInfo, clientId) for clientId in clientIdList],
            'jobTickets': context.getInstance(CJobTicketsWithActionsInfoList, tuple(jobTicketIdList))
        }

        QtGui.qApp.restoreOverrideCursor()

        applyTemplate(self, templateId, data)

    @QtCore.pyqtSlot(int)
    def on_actJobTicketListPrint_printByTemplate(self, templateId):
        jobTicketsIdList = self.modelJobTickets.idList()
        makeDependentActionIdList(jobTicketsIdList)
        context = CInfoContext()
        data = {
            'jobTickets': context.getInstance(CJobTicketsWithActionsInfoList, tuple(jobTicketsIdList))
        }
        applyTemplate(self, templateId, data)

    @QtCore.pyqtSlot(int)
    def on_actActionPrint_printByTemplate(self, templateId):
        index = self.tblJobTickets.currentIndex()
        if not index.isValid():
            return
        row = index.row()
        actionId = self.modelJobTickets.getActionId(row)
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

        actionRecord = QtGui.qApp.db.getRecord('Action', '*', actionId)
        eventId = forceRef(actionRecord.value('event_id'))

        context = CInfoContext()
        eventInfo = context.getInstance(CEventInfo, eventId)
        eventActions = eventInfo.actions
        eventActions._idList = [actionId]
        eventActions._items = [CCookedActionInfo(context, actionRecord, CAction(record=actionRecord))]
        eventActions._loaded = True

        data = {
            'event'             : eventInfo,
            'action'            : eventInfo.actions[0],
            'client'            : eventInfo.client,
            'actions'           : eventActions,
            'currentActionIndex': 0,
            'tempInvalid'       : None
        }
        QtGui.qApp.restoreOverrideCursor()
        applyTemplate(self, templateId, data)


class CJobTicketsModel(CTableModel):
    class CEQueueStatusCol(CCol):
        def __init__(self, title, fields):
            super(CJobTicketsModel.CEQueueStatusCol, self).__init__(title, fields, 10, 'c', False)
            self._cache = CTableRecordCache(QtGui.qApp.db,
                                            u'vEQueueTicket',
                                            [u'status', u'value'],
                                            idCol='id')

        def format(self, values):
            ticketId = values[0]
            if ticketId:
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
        self.ticketStatusCol = CJobTicketsModel.CEQueueStatusCol(u'Номерок', ['eQueueTicket_id'])
        clientCol = CLocClientColumn(u'Ф.И.О.', ['id'], 20)
        self.clientCol = clientCol
        clientBirthDateCol = CLocClientBirthDateColumn(u'Дата рожд.', ['id'], 10, clientCol)
        self.actionTypeCol = CLocActionTypeColumn(u'Назначение', ['id'], 20, clientCol)
        actionPersonCol = CLocPersonColumn(u'Назначил', ['id'], 20, clientCol)
        actionExecPersonCol = CLocExecPersonColumn(u'Выполнил', ['id'], 20, clientCol)
        externalId = CLocExternalIdColumn(u'Идентификатор', ['id'], 20, clientCol)
        tissue = CLocTissueColumn(u"Биоматериал", ['id'], 20, clientCol)
        status = CLocStatusColumn(u'Состояние', ['id'], 20, clientCol)

        columnsList = [
            self.ticketStatusCol,
            externalId,
            status,
            CDateTimeCol(u'Дата и время', ['datetime'], 10),
            clientCol,
            clientBirthDateCol,
            self.actionTypeCol,
            tissue,
            actionPersonCol,
            actionExecPersonCol
        ]

        CTableModel.__init__(self, parent, columnsList, 'Job_Ticket')
        self.loadField('master_id')
        self.setTable('Job_Ticket')

        self._updateTicketStatusTimerId = QtCore.QTimer(self)  # self.startTimer(500)
        self._updateTicketStatusTimerId.timeout.connect(self.updateTicketStatus)
        self._updateTicketStatusTimerId.start(500)

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        print "setData", index.row(), index.column(), value

    def flags(self, index):
        if (index.column() == 0):
            return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled
        else:
            return QtCore.Qt.ItemIsEnabled

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
        self.ActionCache = CTableRecordCache(db, db.table('Action'),
                                             'actionType_id, event_id, setPerson_id, takenTissueJournal_id, person_id')
        self.actionTypeCache = CTableRecordCache(db, db.table('ActionType'), 'name, code')
        self.eventCache = CTableRecordCache(db, db.table('Event'), 'client_id')
        self.personCache = CTableRecordCache(db, db.table('vrbPersonWithSpeciality'), 'name')
        self.clientCache = CTableRecordCache(db, db.table('Client'), 'firstName, lastName, patrName, birthDate, sex')
        self.externalIdCashe = CTableRecordCache(db, db.table('TakenTissueJournal'), 'externalId, tissueType_id')

    def getActionRecord(self, ticketId):
        actionId = self.getActionId(ticketId)
        return self.ActionCache.get(actionId) if actionId else None

    def getActionTypeCode(self, ticketId):
        actionRecord = self.getActionRecord(ticketId) if ticketId else None
        actionTypeRecord = self.actionTypeCache.get(
            forceRef(actionRecord.value('actionType_id'))) if actionRecord else None
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

    def getTissueRecord(self, tickedId):
        record = self.getActionRecord(tickedId)
        journalId = self.externalIdCashe.get(forceRef(record.value('takenTissueJournal_id'))) if record else None
        if journalId:
            if forceRef(journalId.value('tissueType_id')) == 1:
                return u"Кровь"
            elif forceRef(journalId.value('tissueType_id')) == 2:
                return u"Моча"
            else:
                return u"-"
        else:
            return None

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


class CLocExecPersonColumn(CCol):
    def __init__(self, title, fields, defaultWidth, master):
        CCol.__init__(self, title, fields, defaultWidth, 'l')
        self.master = master

    def format(self, values):
        ticketId = forceRef(values[0])
        record = self.master.getActionRecord(ticketId)
        setPersonId = forceRef(record.value('person_id')) if record else None
        record = self.master.personCache.get(setPersonId) if setPersonId else None
        if record:
            return toVariant(forceString(record.value('name')))
        else:
            return CCol.invalid


class CLocTissueColumn(CCol):
    def __init__(self, title, fields, defaultWidth, master):
        CCol.__init__(self, title, fields, defaultWidth, 'l')
        self.master = master

    def format(self, values):
        tickedId = forceRef((values[0]))
        record = self.master.getTissueRecord(tickedId)
        if record:
            return toVariant(forceString(record))
        else:
            return None
