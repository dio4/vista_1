# -*- coding: utf-8 -*-

from Accounting.AccountBuilder import CAccountPool, CAccountBuilder
from Accounting.AccountEditDialog import CAccountEditDialog
from Accounting.AccountItemEditor import CAccountItemEditor
from Accounting.Utils import *
from Events.EditDispatcher import *
from Events.Utils import *
from Exchange.ExportR23Native import exportR23Native
from Exchange.ImportEISOMS import importEISOMS
from Exchange.ImportPayRefuseR23 import ImportPayRefuseR23Native
from Exchange.ImportRD1 import ImportRD1
from ExposeConfirmationDialog import CExposeConfirmationDialog
from ExposeStatisticsDialog import CExposeStatisticsDialog
from FormProgressDialog import CFormProgressCanceled, CFormProgressDialog
from Orgs.Contracts import CContractEditor
from Orgs.Utils import *
from Registry.ClientEditDialog import CClientEditDialog
from Registry.Utils import CClientInfo
from Reports.AccountRegistry import CAccountRegistry
from Reports.AccountRegistryDMS import CAccountRegistryDMS
from Reports.AccountRegistryR23 import CAccountRegistryR23, getAccountRegistryR23Params
from Reports.AccountRegistryR51 import CAccountRegistryR51
from Reports.AccountSummary import CAccountSummary
from Reports.ClientsListByRegistry import CClientsListByRegistry
from Reports.FinanceSummaryByDoctors import CFinanceSummaryByDoctors, CFinanceSummaryByDoctorsEx
from Reports.FinanceSummaryByServices import CFinanceSummaryByServices, CFinanceSummaryByServicesEx
from Reports.ReportDopDisp import CReportDopDisp
from Reports.ReportView import CReportViewDialog
from Ui_AccountingDialog import Ui_AccountingDialog
from Ui_InsurerFilterDialog import Ui_InsurerFilterDialog
from Users.Rights import *
from library.DialogBase import CDialogBase
from library.PrintInfo import CInfoContext
from library.PrintTemplates import getPrintAction, applyTemplate
from library.TableModel import *
from library.Utils import *
from library.crbcombobox import CRBModelDataCache
from library.database import addDateInRange, addCondLike

u"""
Расчёты: создание/просмотр/печать/etc счетов
"""

getcontext().prec = 12


def getAvailableFinanceTypeCodeList():
    app = QtGui.qApp
    if app.userHasAnyRight([urAdmin, urAccessAccountInfo, urAccessAccounting]):
        return None
    result = []
    for right, code in ((urAccessAccountingBudget, CFinanceType.budget),
                        (urAccessAccountingCMI, CFinanceType.CMI),
                        (urAccessAccountingVMI, CFinanceType.VMI),
                        (urAccessAccountingCash, CFinanceType.cash),
                        (urAccessAccountingTargeted, CFinanceType.targeted),
                        ):
        if app.userHasRight(right):
            result.append(code)
    return result


def selectInsurer(parent, strict):
    ok = False
    orgId = None
    assistant = False
    filterDialog = CInsurerFilterDialog(parent, strict)
    try:
        ok = filterDialog.exec_()
        if ok:
            orgId = filterDialog.orgId()
            assistant = filterDialog.assistant()
    finally:
        return ok, orgId, assistant


class CInsurerFilterDialog(QtGui.QDialog, Ui_InsurerFilterDialog):
    def __init__(self, parent, strict):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbInsurerFilterDialog.setAddNone(not strict, u'все')
        self.cmbInsurerFilterDialog.setCurrentIndex(0)
        self.chkAssistent.setChecked(False)

    def orgId(self):
        return self.cmbInsurerFilterDialog.value()

    def assistant(self):
        return self.chkAssistent.isChecked()


class CAccountingDialog(CDialogBase, Ui_AccountingDialog, CAccountBuilder):
    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        CAccountBuilder.__init__(self)

        self.accessCountTotalSumWithFranchise = False
        self.franchisePercent = 0

        self.addModels('Contracts', CContractTreeModel(self, getAvailableFinanceTypeCodeList()))
        self.addModels('Accounts', CAccountsModel(self))
        self.addModels('AccountItems', CAccountItemsModel(self))

        self.setupAccountsMenu()
        self.setupAccountItemsMenu()
        self.setupBtnPrintMenu()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.clnCalcCalendar.setList(QtGui.qApp.calendarInfo)

        self.splitter_3.setCollapsible(0, True)

        today = QDate.currentDate()
        self.edtContractBegDate.setDate(QDate(today.year(), 1, 1))
        self.edtContractEndDate.setDate(QDate(today.year(), 12, 31))

        self.treeContracts.setModel(self.modelContracts)
        self.treeContracts.setSelectionModel(self.selectionModelContracts)
        self.treeContracts.setRootIsDecorated(False)
        self.treeContracts.setAlternatingRowColors(True)
        self.treeContracts.header().hide()

        self.cmbAnalysisPayRefuseType.setTable('rbPayRefuseType', addNone=True)
        self.cmbAnalysisPayRefuseType.setShowFields(CRBComboBox.showCodeAndName)
        self.cmbAnalysisPayRefuseType.view().horizontalHeader().show()
        self.cmbAnalysisPayRefuseType.view().horizontalHeader().setMinimumSectionSize(50)
        self.cmbHistoryPayRefuseType.setTable('rbPayRefuseType', addNone=True)
        self.cmbHistoryPayRefuseType.setShowFields(CRBComboBox.showCodeAndName)
        self.cmbAnalysisClientCodeType.setTable('rbAccountingSystem', True)

        self.tblAccounts.setModel(self.modelAccounts)
        self.tblAccounts.setSelectionModel(self.selectionModelAccounts)
        self.tblAccounts.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tblAccounts.setPopupMenu(self.mnuAccounts)
        self.tblAccountItems.setModel(self.modelAccountItems)
        self.tblAccountItems.setSelectionModel(self.selectionModelAccountItems)
        self.tblAccountItems.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tblAccountItems.setPopupMenu(self.mnuAccountItems)
        self.tblAccountItems.horizontalHeader().setSortIndicator(0, QtCore.Qt.AscendingOrder)
        self.tblAccountItems.setSortingEnabled(True)
        self.btnPrint.setMenu(self.mnuBtnPrint)

        self.cmbCalcOrgStructure.setExpandAll(False)
        self.cmbAnalysisOrgStructure.setExpandAll(False)
        self.cmbHistoryOrgStructure.setExpandAll(False)
        yesterday = QDate.currentDate().addDays(-1)
        self.clnCalcCalendar.setSelectedDate(yesterday)
        self.cmbCalcOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.resetAnalysisPage()
        self.on_cmbAnalysisAccountItems_currentIndexChanged(0)
        self.resetHistoryPage()
        self.on_cmbHistoryAccountItems_currentIndexChanged(0)
        self.payParams = {}
        self.historyFilter = {}
        self.currentAccountId = None
        self.currentFinanceId = None
        self.tabWorkType.setTabEnabled(2, False)
        # Поля заполненность которых сигналит о том что мы закрываем
        # возможность редактирования, а просто ищем данные по ним.
        self.eventIdWatching = None
        self.actionIdWatching = None
        self.visitIdWatching = None
        self.watchingAccountItemIdList = None
        self.updateFilterAccountsEtc()
        self.setExtendedFiltersVisible(False)
        if QtGui.qApp.region() != '91':
            self.btnFLC.setVisible(False)
            self.btnFLCImport.setVisible(False)

        # сканирование штрих кода
        self.addBarcodeScanAction('actScanBarcode')
        self.tabAnalysis.addAction(self.actScanBarcode)
        self.connect(self.actScanBarcode, SIGNAL('triggered()'), self.on_actScanBarcode_triggered)
        self.connect(self.chkAnalysisExtendedFilter, SIGNAL('toggled(bool)'), self.setExtendedFiltersVisible)

        self.testConnectionTimerId = None

        self.cmbCompulsoryPolisCompany.setPolicyTypeFilter(True)
        self.date = None
        self.oldPref = dict()

    @QtCore.pyqtSlot()
    def on_btnApplyContractDates_clicked(self):
        begDate = self.edtContractBegDate.date()
        endDate = self.edtContractEndDate.date()
        self.modelContracts.setContractDates(begDate, endDate)

    @QtCore.pyqtSlot(bool)
    def setExtendedFiltersVisible(self, visible):
        self.chkAnalysisRecipient.setVisible(visible)
        self.cmbAnalysisRecipient.setVisible(visible)
        self.chkAnalysisClientLastName.setVisible(visible)
        self.edtAnalysisClientLastName.setVisible(visible)
        self.chkAnalysisClientFirstName.setVisible(visible)
        self.edtAnalysisClientFirstName.setVisible(visible)
        self.chkAnalysisClientPatrName.setVisible(visible)
        self.edtAnalysisClientPatrName.setVisible(visible)
        self.chkAnalysisClientBirthday.setVisible(visible)
        self.edtAnalysisClientBirthday.setVisible(visible)
        self.chkAnalysisClientTenPercentRandom.setVisible(visible)
        self.chkAnalysisDiagnosis.setVisible(visible)
        self.edtAnalysisDiagnosis.setVisible(visible)
        self.chkAnalysisServiceArea.setVisible(visible)
        self.cmbAnalysisServiceArea.setVisible(visible)
        self.chkCompulsoryPolisCompany.setVisible(visible)
        self.cmbCompulsoryPolisCompany.setVisible(visible)
        self.gbAnalysisService.setVisible(visible)

    def exec_(self):
        if self.eventIdWatching or self.actionIdWatching or self.visitIdWatching:
            self.setWatchingMode()
        else:
            self.selectionModelContracts.setCurrentIndex(self.modelContracts.index(0, 0),
                                                         QtGui.QItemSelectionModel.SelectCurrent)
        return CDialogBase.exec_(self)

    def savePreferences(self):
        result = CDialogBase.savePreferences(self)
        setPref(result, 'contractbegdate', toVariant(self.edtContractBegDate.date()))
        setPref(result, 'contractenddate', toVariant(self.edtContractEndDate.date()))
        setPref(result, 'treecontacts', self.treeContracts.savePreferences())
        setPref(result, 'tblaccountitems', self.tblAccountItems.savePreferences())
        setPref(result, 'layoutaccountitems', toVariant(self.layoutAccountItems.geometry()))

        for x in result:
            self.oldPref[x] = result[x]

        return self.oldPref

    def loadPreferences(self, preferences):
        self.oldPref = preferences.copy()

        if 'treecontacts' in preferences:
            self.treeContracts.loadPreferences(preferences['treecontacts'])

        self.edtContractBegDate.setDate(
            forceDate(getPref(preferences, 'contractbegdate', QDate(QDate.currentDate().year(), 1, 1))))
        self.edtContractEndDate.setDate(
            forceDate(getPref(preferences, 'contractenddate', QDate(QDate.currentDate().year(), 12, 31))))
        CDialogBase.loadPreferences(self, preferences)

    def on_actScanBarcode_triggered(self):
        self.chkAnalysisAccountId.setChecked(True)
        self.chkAnalysisAccountId.emit(SIGNAL('clicked(bool)'), True)
        self.edtAnalysisAccountId.clear()
        self.edtAnalysisAccountId.setFocus(Qt.OtherFocusReason)
        self.edtAnalysisAccountId.startHearingPoint()

    def setWatchingContent(self):
        db = QtGui.qApp.db
        tableAccount = db.table('Account')
        tableAccountItem = db.table('Account_Item')

        cond = [
            tableAccountItem['deleted'].eq(0)
        ]
        if self.eventIdWatching:
            cond.append(tableAccountItem['event_id'].eq(self.eventIdWatching))
        elif self.actionIdWatching:
            cond.append(tableAccountItem['action_id'].eq(self.actionIdWatching))
        elif self.visitIdWatching:
            cond.append(tableAccountItem['visit_id'].eq(self.visitIdWatching))
        else:
            return

        table = tableAccountItem.innerJoin(tableAccount, [tableAccount['id'].eq(tableAccountItem['master_id']),
                                                          tableAccount['deleted'].eq(0)])
        cols = [
            tableAccountItem['id'],
            tableAccountItem['master_id']
        ]

        accountIdList = []
        accountItemIdList = []
        for record in db.iterRecordList(table, cols, cond):
            accountId = forceRef(record.value('master_id'))
            if not accountId in accountIdList:
                accountIdList.append(accountId)
            accountItemId = forceRef(record.value('id'))
            if not accountItemId in accountItemIdList:
                accountItemIdList.append(accountItemId)
        self.watchingAccountItemIdList = accountItemIdList
        currentAccountId = self.tblAccounts.currentItemId()
        self.tblAccounts.setIdList(accountIdList, currentAccountId)
        self.updateAccountsPanel(accountIdList)

    def setWatchingMode(self):
        self.splitter_3.widget(0).setVisible(False)
        self.btnForm.setEnabled(False)
        self.btnRefresh.setEnabled(False)
        self.btnExport.setEnabled(False)
        self.btnImport.setEnabled(False)
        self.tabWidget_2.setTabEnabled(1, False)
        if not QtGui.qApp.userHasAnyRight(accountantRightList):
            self.tblAccounts.setPopupMenu(None)
            self.tblAccountItems.setPopupMenu(None)
        self.setWatchingContent()

    def setWatchingFields(self, eventId=None, actionId=None, visitId=None):
        self.eventIdWatching = eventId
        self.actionIdWatching = actionId
        self.visitIdWatching = visitId
        self.franchisePercent = getFranchisePercentByEvent(eventId)

    def setupAccountsMenu(self):
        self.mnuAccounts = QtGui.QMenu(self)
        self.mnuAccounts.setObjectName('mnuAccounts')
        self.actEditAccount = QtGui.QAction(u'Изменить счёт', self)
        self.actEditAccount.setObjectName('actEditAccount')
        self.actPrintAccount = QtGui.QAction(u'Напечатать счёт (бланк)', self)
        self.actPrintAccount.setObjectName('actPrintAccount')
        self.actPrintAccountSummary = QtGui.QAction(u'Напечатать сводный счёт', self)
        self.actPrintAccountSummary.setObjectName('actPrintAccountSummary')
        self.actPrintAccountInsurer = QtGui.QAction(u'Счёт на СМО', self)
        self.actPrintAccountInsurer.setObjectName('actPrintAccountInsurer')
        self.actPrintAccountRegistry = QtGui.QAction(u'Напечатать реестр счёта (бланк)', self)
        self.actPrintAccountRegistry.setObjectName('actPrintAccountRegistry')
        self.actPrintR51LocRegistry = QtGui.QAction(u'Реестр счета для страховых компаний г. Мурманск', self)
        self.actPrintR51LocRegistry.setObjectName('actPrintR51LocRegistry')
        self.actPrintR51ExtRegistry = QtGui.QAction(u'Реестр счета для ТФОМС', self)
        self.actPrintR51ExtRegistry.setObjectName('actPrintR51ExtRegistry')
        self.actReportByDoctorsEx = QtGui.QAction(u'Финансовая сводка по врачам за период', self)
        self.actReportByDoctorsEx.setObjectName('actReportByDoctorsEx')
        self.actReportByServicesEx = QtGui.QAction(u'Финансовая сводка по услугам за период', self)
        self.actReportByServicesEx.setObjectName('actReportByServicesEx')
        self.actCheckMesInAccount = QtGui.QAction(u'Проверить счёт на соответствие МЭС', self)
        self.actCheckMesInAccount.setObjectName('actCheckMesInAccount')
        self.actSelectAllAccounts = QtGui.QAction(u'Выбрать все', self)
        self.actSelectAllAccounts.setObjectName('actSelectAllAccounts')
        self.actPrintR23Registry = QtGui.QAction(u'Напечатать счёт (г. Краснодар)', self)
        self.actPrintR23Registry.setObjectName('actPrintR23Registry')
        self.actDeleteAccounts = QtGui.QAction(u'Удалить', self)
        self.actDeleteAccounts.setObjectName('actDeleteAccounts')
        self.mnuAccounts.addAction(self.actEditAccount)
        self.mnuAccounts.addAction(self.actPrintAccount)
        self.mnuAccounts.addAction(self.actPrintAccountSummary)
        self.mnuAccounts.addAction(self.actPrintAccountInsurer)
        self.mnuAccounts.addAction(self.actPrintAccountRegistry)
        self.mnuAccounts.addAction(self.actReportByDoctorsEx)
        self.mnuAccounts.addAction(self.actReportByServicesEx)
        self.mnuAccounts.addSeparator()
        self.mnuAccounts.addAction(self.actCheckMesInAccount)
        self.mnuAccounts.addSeparator()
        self.mnuAccounts.addAction(self.actSelectAllAccounts)
        self.mnuAccounts.addSeparator()
        self.mnuAccounts.addAction(self.actDeleteAccounts)

    def setupAccountItemsMenu(self):
        self.mnuAccountItems = QtGui.QMenu(self)
        self.mnuAccountItems.setObjectName('mnuAccountItems')
        self.actOpenClient = QtGui.QAction(u'Открыть регистрационную карточку', self)
        self.actOpenClient.setObjectName('actOpenClient')
        self.actOpenEvent = QtGui.QAction(u'Открыть первичный документ', self)
        self.actOpenEvent.setObjectName('actOpenEvent')
        self.actSetPayment = QtGui.QAction(u'Подтверждение оплаты', self)
        self.actSetPayment.setObjectName('actSetPayment')
        self.actEditPayment = QtGui.QAction(u'Изменение подтверждения оплаты', self)
        self.actEditPayment.setObjectName('actEditPayment')
        self.actSelectExposed = QtGui.QAction(u'Выбрать без подтверждения', self)
        self.actSelectExposed.setObjectName('actSelectExposed')
        self.actSelectAll = QtGui.QAction(u'Выбрать все', self)
        self.actSelectAll.setObjectName('actSelectAll')
        self.actReportByDoctors = QtGui.QAction(u'Финансовая сводка по врачам', self)
        self.actReportByDoctors.setObjectName('actReportByDoctors')
        self.actReportDopDisp = QtGui.QAction(u'Дополнительная диспансеризация', self)
        self.actReportDopDisp.setObjectName('actReportDopDisp')
        self.actReportByServices = QtGui.QAction(u'Финансовая сводка по услугам', self)
        self.actReportByServices.setObjectName('actReportByServices')
        self.actReportByClients = QtGui.QAction(u'Список пациентов по реестру', self)
        self.actReportByClients.setObjectName('actReportByClients')
        self.actReportByClientsTwoAddr = QtGui.QAction(u'Список пациентов', self)
        self.actReportByClientsTwoAddr.setObjectName('actReportByClientsTwoAddr')
        self.actReportByRegistry = QtGui.QAction(u'Реестр счёта', self)
        self.actReportByRegistry.setObjectName('actReportByRegistry')
        self.actReportByRegistryDMS = QtGui.QAction(u'Реестр счёта ДМС', self)
        self.actReportByRegistryDMS.setObjectName('actReportByRegistryDMS')
        self.actPrintAccountByTemplate = getPrintAction(self, 'account', u'Ещё печать')
        self.actPrintAccountByTemplate.setObjectName('actPrintAccountByTemplate')
        self.actDeleteAccountItems = QtGui.QAction(u'Удалить', self)
        self.actDeleteAccountItems.setObjectName('actDeleteAccountItems')
        self.mnuAccountItems.addAction(self.actOpenClient)
        self.mnuAccountItems.addAction(self.actOpenEvent)
        self.mnuAccountItems.addSeparator()
        self.mnuAccountItems.addAction(self.actSetPayment)
        self.mnuAccountItems.addAction(self.actEditPayment)
        self.mnuAccountItems.addSeparator()
        self.mnuAccountItems.addAction(self.actSelectExposed)
        self.mnuAccountItems.addAction(self.actSelectAll)
        self.mnuAccountItems.addSeparator()
        self.mnuAccountItems.addAction(self.actPrintAccountByTemplate)
        self.mnuAccountItems.addSeparator()
        self.mnuAccountItems.addAction(self.actReportByRegistry)
        self.mnuAccountItems.addAction(self.actReportByRegistryDMS)
        self.mnuAccountItems.addAction(self.actReportByClients)
        self.mnuAccountItems.addAction(self.actReportByClientsTwoAddr)
        self.mnuAccountItems.addAction(self.actReportByDoctors)
        self.mnuAccountItems.addAction(self.actReportByServices)
        self.mnuAccountItems.addAction(self.actReportDopDisp)
        self.mnuAccountItems.addSeparator()
        self.mnuAccountItems.addAction(self.actDeleteAccountItems)

    def setupBtnPrintMenu(self):
        self.mnuBtnPrint = QtGui.QMenu(self)
        self.mnuBtnPrint.setObjectName('mnuBtnPrint')
        self.mnuBtnPrint.addAction(self.actPrintAccount)
        self.mnuBtnPrint.addAction(self.actPrintAccountSummary)
        self.mnuBtnPrint.addAction(self.actPrintAccountInsurer)
        self.mnuBtnPrint.addAction(self.actPrintAccountRegistry)
        self.mnuBtnPrint.addAction(self.actPrintAccountByTemplate)
        self.mnuBtnPrint.addAction(self.actReportByRegistry)
        self.mnuBtnPrint.addAction(self.actReportByRegistryDMS)
        self.mnuBtnPrint.addAction(self.actPrintR51LocRegistry)
        self.mnuBtnPrint.addAction(self.actPrintR51ExtRegistry)
        self.mnuBtnPrint.addAction(self.actPrintR23Registry)
        self.mnuBtnPrint.addAction(self.actReportByClients)
        self.mnuBtnPrint.addAction(self.actReportByClientsTwoAddr)
        self.mnuBtnPrint.addAction(self.actReportByDoctors)
        self.mnuBtnPrint.addAction(self.actReportByDoctorsEx)
        self.mnuBtnPrint.addAction(self.actReportByServices)
        self.mnuBtnPrint.addAction(self.actReportByServicesEx)
        self.mnuBtnPrint.addAction(self.actReportDopDisp)

    def resetAnalysisPage(self):
        yesterday = QDate.currentDate().addDays(-1)
        self.edtAnalysisBegDate.setDate(firstYearDay(yesterday))
        self.edtAnalysisEndDate.setDate(lastYearDay(yesterday))
        self.edtAnalysisNumber.setText('')
        if QtGui.qApp.filterPaymentByOrgStructure():
            orgStructureId = self.cmbCalcOrgStructure.value()
        else:
            orgStructureId = None
        self.cmbAnalysisOrgStructure.setValue(orgStructureId)
        self.cmbAnalysisAccountItems.setCurrentIndex(0)
        self.edtAnalysisDocument.setText('')
        self.cmbAnalysisPayRefuseType.setValue(0)
        self.edtAnalysisNote.setText('')
        self.chkAnalysisClientCode.setChecked(False)
        self.chkAnalysisClientCode.emit(QtCore.SIGNAL('clicked(bool)'), False)
        self.edtAnalysisClientCode.setText('')
        self.cmbAnalysisClientCodeType.setValue(None)
        self.chkAnalysisRecipient.setChecked(False)
        self.cmbAnalysisRecipient.setCurrentIndex(0)
        self.chkAnalysisClientLastName.setChecked(False)
        self.edtAnalysisClientLastName.clear()
        self.chkAnalysisClientFirstName.setChecked(False)
        self.edtAnalysisClientFirstName.clear()
        self.chkAnalysisClientPatrName.setChecked(False)
        self.edtAnalysisClientPatrName.clear()
        self.chkAnalysisClientBirthday.setChecked(False)
        self.chkAnalysisClientTenPercentRandom.setChecked(False)
        self.chkAnalysisDiagnosis.setChecked(False)
        self.edtAnalysisDiagnosis.clear()
        self.chkAnalysisServiceCode.setChecked(False)
        self.chkAnalysisServiceArea.setChecked(False)
        self.cmbAnalysisServiceArea.setCurrentIndex(0)

        # reset treeView. Show all items
        allIndexList = self.modelContracts.match(self.treeContracts.rootIndex(), 0, toVariant(u''), -1,
                                                 Qt.MatchContains | Qt.MatchRecursive)
        for aindex in allIndexList:
            self.treeContracts.setRowHidden(aindex.row(), aindex.parent(), False)

    def resetHistoryPage(self):
        self.edtHistoryBegDate.setDate(self.edtAnalysisBegDate.date())
        self.edtHistoryEndDate.setDate(self.edtAnalysisEndDate.date())
        self.edtHistoryNumber.setText(self.edtAnalysisNumber.text())
        self.cmbHistoryOrgStructure.setValue(self.cmbAnalysisOrgStructure.value())
        self.cmbHistoryAccountItems.setCurrentIndex(self.cmbAnalysisAccountItems.currentIndex())
        self.edtHistoryDocument.setText(self.edtAnalysisDocument.text())
        self.cmbHistoryPayRefuseType.setValue(self.cmbAnalysisPayRefuseType.value())
        self.edtHistoryNote.setText(self.edtAnalysisNote.text())
        self.chkHistoryOnlyCurrentService.setChecked(False)

    def getContractIdList(self, treeIndex):
        treeItem = treeIndex.internalPointer() if treeIndex.isValid() else None
        return treeItem.idList if treeItem else []

    def updateFilterAccountsEtc(self, newAccountId=None):
        self.edtAnalysisAccountId.stopHearingPoint()
        isWatchMode = (self.eventIdWatching or self.actionIdWatching or self.visitIdWatching)
        currentAccountId = newAccountId if newAccountId else self.tblAccounts.currentItemId()
        if isWatchMode:
            self.modelAccounts.invalidateRecordsCache()
            self.tblAccounts.setCurrentItemId(currentAccountId)
        else:
            db = QtGui.qApp.db
            tableAccount = db.table('Account')
            tableAccountItem = db.table('Account_Item')
            tableEvent = db.table('Event')
            tableClient = db.table('Client')
            tableClientIdentification = db.table('ClientIdentification')
            tableEx = tableAccount

            workIndex = self.tabWorkType.currentIndex()

            if workIndex == 1 and self.chkAnalysisAccountId.isChecked():
                self.selectionModelContracts.setCurrentIndex(self.modelContracts.index(0, 0),
                                                             QtGui.QItemSelectionModel.ClearAndSelect)

            contractIdList = self.getContractIdList(self.treeContracts.currentIndex())
            enableBtnForm = False
            cond = [
                tableAccount['deleted'].eq(0)
            ]
            if contractIdList:
                cond.append(tableAccount['contract_id'].inlist(contractIdList))
                if workIndex == 0:
                    enableBtnForm = True
                    begDate = QDate.currentDate()
                    addDateInRange(cond, tableAccount['createDatetime'], begDate, begDate)
                elif workIndex == 1:
                    if self.chkAnalysisAccountId.isChecked():
                        cond.append(tableAccount['id'].eq(trim(self.edtAnalysisAccountId.text())))
                    else:
                        begDate = self.edtAnalysisBegDate.date()
                        endDate = self.edtAnalysisEndDate.date()
                        addDateInRange(cond, tableAccount['date'], begDate, endDate)
                        number = unicode(self.edtAnalysisNumber.text())
                        if number:
                            cond.append(tableAccount['number'].like(number))
                        orgStructureId = self.cmbAnalysisOrgStructure.value()
                        if orgStructureId:
                            cond.append(tableAccount['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
                        filterChkClientCode = self.chkAnalysisClientCode.isChecked()
                        filterChkClientLastName = self.chkAnalysisClientLastName.isChecked()
                        filterChkClientFirstName = self.chkAnalysisClientFirstName.isChecked()
                        filterChkClientPatrName = self.chkAnalysisClientPatrName.isChecked()
                        filterChkClientBirthday = self.chkAnalysisClientBirthday.isChecked()
                        filterChkDiagnosis = self.chkAnalysisDiagnosis.isChecked()
                        filterChkServiceCode = self.chkAnalysisServiceCode.isChecked()
                        filterChkRecipient = self.chkAnalysisRecipient.isChecked()
                        filterChkServiceArea = self.chkAnalysisServiceArea.isChecked()
                        filterChkSMO = self.chkCompulsoryPolisCompany.isChecked()

                        if filterChkClientCode \
                                or filterChkClientLastName or filterChkClientFirstName or filterChkClientPatrName \
                                or filterChkClientBirthday \
                                or filterChkDiagnosis \
                                or filterChkServiceCode \
                                or filterChkServiceArea \
                                or filterChkSMO:
                            tableEx = tableEx.leftJoin(tableAccountItem,
                                                       tableAccountItem['master_id'].eq(tableEx['id']))
                            tableEx = tableEx.leftJoin(tableEvent, tableEvent['id'].eq(tableAccountItem['event_id']))
                        if filterChkClientCode \
                                or filterChkClientLastName \
                                or filterChkClientFirstName \
                                or filterChkClientPatrName \
                                or filterChkClientBirthday \
                                or filterChkSMO:
                            tableEx = tableEx.leftJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))

                        if filterChkClientCode:
                            filterClientCode = forceStringEx(self.edtAnalysisClientCode.text())
                            filterClientCodeType = self.cmbAnalysisClientCodeType.value()
                            if bool(filterClientCode):
                                if filterClientCodeType:
                                    tableEx = tableEx.innerJoin(tableClientIdentification,
                                                                tableClientIdentification['client_id'].eq(
                                                                    tableClient['id']))
                                    cond.append(
                                        tableClientIdentification['accountingSystem_id'].eq(filterClientCodeType))
                                    cond.append(tableClientIdentification['identifier'].eq(filterClientCode))
                                else:
                                    try:
                                        i_filterClientCode = int(filterClientCode)
                                        cond.append(tableClient['id'].eq(i_filterClientCode))
                                    except ValueError:
                                        pass
                        if filterChkClientLastName:
                            addCondLike(cond, tableClient['lastName'],
                                        addDots(forceString(self.edtAnalysisClientLastName.text())))
                        if filterChkClientFirstName:
                            addCondLike(cond, tableClient['firstName'],
                                        addDots(forceString(self.edtAnalysisClientFirstName.text())))
                        if filterChkClientPatrName:
                            addCondLike(cond, tableClient['patrName'],
                                        addDots(forceString(self.edtAnalysisClientPatrName.text())))
                        if filterChkClientBirthday:
                            birthday = forceDate(self.edtAnalysisClientBirthday.date())
                            if birthday.isValid():
                                cond.append(tableClient['birthDate'].eq(birthday))
                        if filterChkDiagnosis:
                            tableDiagnostic = db.table('Diagnostic')
                            tableDiagnosisType = db.table('rbDiagnosisType')
                            tableDiagnosis = db.table('Diagnosis')
                            tableEx = tableEx.leftJoin(tableDiagnostic,
                                                       tableDiagnostic['event_id'].eq(tableEvent['id']))
                            tableEx = tableEx.leftJoin(tableDiagnosisType,
                                                       tableDiagnosisType['id'].eq(tableDiagnostic['diagnosisType_id']))
                            tableEx = tableEx.leftJoin(tableDiagnosis,
                                                       tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']))
                            filterDiagnosis = forceString(self.edtAnalysisDiagnosis.text())
                            cond.append(tableDiagnosisType['code'].inlist(['1', '2']))
                            cond.append(tableDiagnostic['deleted'].eq(0))
                            cond.append(tableDiagnosis['MKB'].like(filterDiagnosis))
                        if filterChkServiceCode:
                            tableVisit = db.table('Visit')
                            tableEventType = db.table('EventType')
                            tableEx = tableEx.leftJoin(tableVisit, tableVisit['id'].eq(tableAccountItem['visit_id']))
                            tableEx = tableEx.leftJoin(tableEventType,
                                                       tableEventType['id'].eq(tableEvent['eventType_id']))
                            filterServiceCode = forceStringEx(self.edtAnalysisServiceCode.text())
                            if filterServiceCode:
                                tableS = db.table('rbService').alias('s')
                                tableEx = tableEx.innerJoin(tableS,
                                                            'IF(Account_Item.service_id IS NOT NULL, Account_Item.service_id,'
                                                            'IF(Account_Item.visit_id IS NOT NULL, Visit.service_id, EventType.service_id)) = s.id')
                                cond.append(tableS['code'].like(filterServiceCode))
                        if filterChkServiceArea or filterChkSMO:
                            tableClientPolicy = db.table('ClientPolicy')
                            tableEx = tableEx.leftJoin(tableClientPolicy,
                                                       'ClientPolicy.id = Event.clientPolicy_id')  # getClientPolicyId(Event.client_id, 1)')
                            if filterChkServiceArea:
                                cond.append('insurerServiceAreaMatch(ClientPolicy.insurer_id, %s, %s, %s)' %
                                            (self.cmbAnalysisServiceArea.currentIndex() + 1,
                                             quote(QtGui.qApp.defaultKLADR()),
                                             quote(QtGui.qApp.provinceKLADR())))
                            if filterChkSMO:
                                cond.append(tableClientPolicy['insurer_id'].eq(self.cmbCompulsoryPolisCompany.value()))
                        if filterChkRecipient:
                            tableContract = db.table('Contract')
                            tableEx = tableEx.leftJoin(tableContract, tableContract['id'].eq(tableAccount['contract_id']))
                            filterRecipientId = forceRef(self.cmbAnalysisRecipient.value())
                            cond.append(tableContract['recipient_id'].eq(filterRecipientId))

                            # hide items
                            textToFind = self.cmbAnalysisRecipient.text().replace('-', '')
                            ri = self.modelContracts.getRootItem()
                            rin = self.modelContracts.index(0, 0)
                            if ri:
                                i = 0
                                while i < ri.childCount():
                                    rii = ri.child(i)
                                    rjn = rin.child(i, 0)
                                    i += 1
                                    j = 0
                                    while j < rii.childCount():
                                        rij = rii.child(j)
                                        rkn = rjn.child(j, 0)
                                        j += 1
                                        k = 0
                                        while k < rij.childCount():
                                            rik = rij.child(k)
                                            rln = rkn.child(k, 0)
                                            k += 1
                                            l = 0
                                            found = False
                                            smofound = False
                                            tdata = forceString(rik.data(0))
                                            found = False
                                            while l < rik.childCount():
                                                ril = rik.child(l)
                                                rmn = rln.child(l, 0)
                                                l += 1
                                                recid = QtGui.qApp.db.translate('Contract', 'id',
                                                                                self.getContractIdList(rmn)[0],
                                                                                'recipient_id')
                                                self.treeContracts.setRowHidden(rmn.row(), rmn.parent(), False)
                                                if recid != self.cmbAnalysisRecipient.value():
                                                    self.treeContracts.setRowHidden(rmn.row(), rmn.parent(), True)
                                                else:
                                                    found = True
                                            self.treeContracts.setRowHidden(rln.row(), rln.parent(), False)
                                            if not found:
                                                self.treeContracts.setRowHidden(rln.row(), rln.parent(), True)

                elif workIndex == 2:
                    begDate = self.edtHistoryBegDate.date()
                    endDate = self.edtHistoryEndDate.date()
                    addDateInRange(cond, tableAccount['date'], begDate, endDate)
                    number = unicode(self.edtHistoryNumber.text())
                    if number:
                        cond.append(tableAccount['number'].like(number))
                    orgStructureId = self.cmbHistoryOrgStructure.value()
                    if orgStructureId:
                        cond.append(tableAccount['orgStructure_id'].eq(orgStructureId))
                    itemQueryTable, itemCond = self.formAccountItemQueryParts()
                    itemCond.append(tableAccountItem['master_id'].eq(tableAccount['id']))
                    cond.append(db.existsStmt(itemQueryTable, itemCond))
                order = [
                    tableAccount['date'],
                    tableAccount['number'],
                    tableAccount['id']
                ]
                accountIdList = db.getDistinctIdList(tableEx, tableAccount['id'], cond, order)
            else:
                accountIdList = []
            self.tblAccounts.setIdList(accountIdList, currentAccountId)
            self.updateAccountsPanel(accountIdList)
            self.btnForm.setEnabled(enableBtnForm)

    def updateAccountsPanel(self, idList):
        count = len(idList)
        sum = forceDecimal(0.0)
        payedSum = forceDecimal(0.0)
        refusedSum = forceDecimal(0.0)
        if idList:
            db = QtGui.qApp.db
            table = db.table('Account')
            record = db.getRecordEx(
                table, 'SUM(`sum`), SUM(`payedSum`), SUM(`refusedSum`)', table['id'].inlist(idList))
            if record:
                sum = forceDecimal(record.value(0))
                payedSum = forceDecimal(record.value(1))
                refusedSum = forceDecimal(record.value(2))
        locale = QLocale()
        if self.franchisePercent and self.accessCountTotalSumWithFranchise:
            sum = sum * (forceDecimal(self.franchisePercent) / forceDecimal(100.0))

        self.edtTolalAccounts.setText(locale.toString(count))
        self.edtTotalSum.setText(unicode(sum))
        self.edtTotalPayed.setText(unicode(payedSum))
        self.edtTotalRefused.setText(unicode(refusedSum))
        self.btnECashRegister.setEnabled(
            bool(self.currentAccountId) and QtGui.qApp.userHasRight(urAccessEditPayment) and QtGui.qApp.userHasAnyRight(
                accountantRightList) and QtGui.qApp.userHasRight(urECRAccess))

    def setVisibleFederalPriceColumn(self):
        self.tblAccountItems.setColumnHidden(7, True)
        contractIdList = self.getContractIdList(self.treeContracts.currentIndex())
        if len(contractIdList) == 1:
            contractInfo = getContractInfo(contractIdList[0])
            if contractInfo.isConsiderFederalPrice:
                self.tblAccountItems.setColumnHidden(7, False)

    def updateAccountItemsPanel(self, idList):
        count, totalSum, payedSum, refusedSum = getAccountItemsTotals(idList)
        locale = QLocale()
        if self.franchisePercent and self.accessCountTotalSumWithFranchise:
            totalSum = totalSum * (forceDecimal(self.franchisePercent) / forceDecimal(100.0))

        self.edtAccountItemsCount.setText(locale.toString(count))
        self.edtAccountItemsSum.setText(unicode(totalSum))
        self.edtAccountItemsPayed.setText(unicode(payedSum))
        self.edtAccountItemsRefused.setText(unicode(refusedSum))
        self.tabWorkType.setTabEnabled(2, self.tabWorkType.currentIndex() == 2 or bool(idList))

    def updateAccountItemInfo(self, accountItemId):
        text = '\n'
        if accountItemId:
            itemRecord = self.modelAccountItems.recordCache().get(accountItemId)
            if itemRecord:
                document = forceString(itemRecord.value('number'))
                date = forceString(itemRecord.value('date'))
                refuseTypeId = forceRef(itemRecord.value('refuseType_id'))
                reexposeItemId = forceRef(itemRecord.value('reexposeItem_id'))
                note = forceString(itemRecord.value('note'))
                if document and date:
                    if refuseTypeId:
                        data = CRBModelDataCache.getData('rbPayRefuseType', True, '')
                        refuseText = u'причина отказа: ' + data.getStringById(refuseTypeId, CRBComboBox.showCodeAndName)
                        if reexposeItemId:
                            text = u'перевыставлен'
                        else:
                            text = u'отказан: %s от %s, %s' % (document, date, refuseText)
                    else:
                        text = u'оплачен: %s от %s' % (document, date)
                else:
                    text = u'без подтверждения'
                if note:
                    text = text + u'\nПримечание: ' + note
                else:
                    text = text + u'\n'
        self.lblAccountItemInfo.setText(text)

    def formAccountItemQueryParts(self):
        db = QtGui.qApp.db
        table = db.table('Account_Item')
        tableEvent = db.table('Event')
        tableVisit = db.table('Visit')
        tableAction = db.table('Action')
        tableClient = db.table('Client')
        tableClientIdentification = db.table('ClientIdentification')

        queryTable = table
        workIndex = self.tabWorkType.currentIndex()
        cond = []
        filterCode = 0
        filterDocument = ''
        filterNote = ''
        filterChkClientCode = filterClientCodeType = False
        if workIndex == 0:
            pass
        elif workIndex == 1:
            filterCode = self.cmbAnalysisAccountItems.currentIndex()
            filterDocument = forceStringEx(self.edtAnalysisDocument.text())
            filterRefuseType = self.cmbAnalysisPayRefuseType.value()
            filterNote = forceStringEx(self.edtAnalysisNote.text())
            filterChkClientCode = self.chkAnalysisClientCode.isChecked()
            if filterChkClientCode:
                filterClientCode = forceStringEx(self.edtAnalysisClientCode.text())
                filterClientCodeType = self.cmbAnalysisClientCodeType.value()
        elif workIndex == 2:
            filterCode = self.cmbHistoryAccountItems.currentIndex()
            filterDocument = forceStringEx(self.edtHistoryDocument.text())
            filterRefuseType = self.cmbHistoryPayRefuseType.value()
            filterNote = forceStringEx(self.edtHistoryNote.text())

        if filterCode == 0:  # 0:Все
            pass
        elif filterCode == 1:  # 1:Без подтверждения
            cond.append(db.joinOr([table['date'].isNull(), table['number'].eq('')]))
        elif filterCode == 2:  # 2:Подтверждённые
            cond.append(table['date'].isNotNull())
            self.__appendDocCondition(cond, table['number'], filterDocument)
            self.__appendNoteCondition(cond, table['note'], filterNote)
        elif filterCode == 3:  # 3:Оплаченные
            cond.append(table['date'].isNotNull())
            self.__appendDocCondition(cond, table['number'], filterDocument)
            cond.append(table['refuseType_id'].isNull())
            self.__appendNoteCondition(cond, table['note'], filterNote)
        elif filterCode == 4:  # 4:Отказанные
            cond.append(table['date'].isNotNull())
            self.__appendDocCondition(cond, table['number'], filterDocument)
            self.__appendPayStatusCondition(cond, table['refuseType_id'], filterRefuseType)
            self.__appendNoteCondition(cond, table['note'], filterNote)
        elif filterCode == 5:  # 5:Перевыставляемые
            cond.append(table['date'].isNotNull())
            self.__appendDocCondition(cond, table['number'], filterDocument)
            self.__appendPayStatusCondition(cond, table['refuseType_id'], filterRefuseType)
            tablePayRefuseType = db.table('rbPayRefuseType')
            cond.append(tablePayRefuseType['rerun'].ne(0))
            queryTable = queryTable.leftJoin(
                tablePayRefuseType, table['refuseType_id'].eq(tablePayRefuseType['id']))
            self.__appendNoteCondition(cond, table['note'], filterNote)
        elif filterCode == 6:  # 6:Неперевыставляемые
            cond.append(table['date'].isNotNull())
            self.__appendDocCondition(cond, table['number'], filterDocument)
            self.__appendPayStatusCondition(cond, table['refuseType_id'], filterRefuseType)
            tablePayRefuseType = db.table('rbPayRefuseType')
            cond.append(tablePayRefuseType['rerun'].eq(0))
            queryTable = queryTable.leftJoin(
                tablePayRefuseType, table['refuseType_id'].eq(tablePayRefuseType['id']))
            self.__appendNoteCondition(cond, table['note'], filterNote)

        queryTable = queryTable.leftJoin(tableEvent, tableEvent['id'].eq(table['event_id']))
        queryTable = queryTable.leftJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))
        if filterChkClientCode:
            if filterClientCodeType and filterClientCode:
                queryTable = queryTable.innerJoin(tableClientIdentification,
                                                  tableClientIdentification['client_id'].eq(tableClient['id']))
                cond.append(tableClientIdentification['accountingSystem_id'].eq(filterClientCodeType))
                cond.append(tableClientIdentification['identifier'].eq(filterClientCode))
            else:
                if filterClientCode:
                    try:
                        i_filterClientCode = int(filterClientCode)
                        cond.append(tableClient['id'].eq(i_filterClientCode))
                    except ValueError:
                        pass

        if workIndex == 1:
            filterChkClientLastName = self.chkAnalysisClientLastName.isChecked()
            filterChkClientFirstName = self.chkAnalysisClientFirstName.isChecked()
            filterChkClientPatrName = self.chkAnalysisClientPatrName.isChecked()
            filterChkClientBirthday = self.chkAnalysisClientBirthday.isChecked()
            filterChkDiagnosis = self.chkAnalysisDiagnosis.isChecked()
            filterChkServiceCode = self.chkAnalysisServiceCode.isChecked()
            filterChkServiceArea = self.chkAnalysisServiceArea.isChecked()
            filterChkSMO = self.chkCompulsoryPolisCompany.isChecked()
            if filterChkClientLastName:
                addCondLike(cond, tableClient['lastName'], addDots(forceString(self.edtAnalysisClientLastName.text())))
            if filterChkClientFirstName:
                addCondLike(cond, tableClient['firstName'],
                            addDots(forceString(self.edtAnalysisClientFirstName.text())))
            if filterChkClientPatrName:
                addCondLike(cond, tableClient['patrName'], addDots(forceString(self.edtAnalysisClientPatrName.text())))
            if filterChkClientBirthday:
                birthday = forceDate(self.edtAnalysisClientBirthday.date())
                if birthday.isValid():
                    cond.append(tableClient['birthDate'].eq(birthday))
            if filterChkDiagnosis:
                tableDiagnostic = db.table('Diagnostic')
                tableDiagnosisType = db.table('rbDiagnosisType')
                tableDiagnosis = db.table('Diagnosis')
                queryTable = queryTable.leftJoin(tableDiagnostic, tableDiagnostic['event_id'].eq(tableEvent['id']))
                queryTable = queryTable.leftJoin(tableDiagnosisType,
                                                 tableDiagnosisType['id'].eq(tableDiagnostic['diagnosisType_id']))
                queryTable = queryTable.leftJoin(tableDiagnosis,
                                                 tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']))
                filterDiagnosis = forceString(self.edtAnalysisDiagnosis.text())
                cond.append(tableDiagnosisType['code'].inlist(['1', '2']))
                cond.append(tableDiagnostic['deleted'].eq(0))
                cond.append(tableDiagnosis['MKB'].like(filterDiagnosis))
            if filterChkServiceCode:
                filterServiceCode = forceStringEx(self.edtAnalysisServiceCode.text())
                if filterServiceCode:
                    tableS = db.table('rbService').alias('s')
                    tableCT = db.table('Contract_Tariff').alias('ct')
                    queryTable = queryTable.leftJoin(tableCT, tableCT['id'].eq(table['tariff_id']))
                    queryTable = queryTable.leftJoin(tableS, tableS['id'].eq(tableCT['service_id']))
                    cond.append(tableS['code'].like(filterServiceCode))
            if filterChkServiceArea or filterChkSMO:
                tableClientPolicy = db.table('ClientPolicy')
                queryTable = queryTable.leftJoin(tableClientPolicy, tableClientPolicy['id'].eq(tableEvent['clientPolicy_id']))
                if filterChkServiceArea:
                    cond.append('insurerServiceAreaMatch(ClientPolicy.insurer_id, %s, %s, %s)' %
                                (self.cmbAnalysisServiceArea.currentIndex() + 1,
                                 quote(QtGui.qApp.defaultKLADR()),
                                 quote(QtGui.qApp.provinceKLADR())))
                if filterChkSMO:
                    cond.append(tableClientPolicy['insurer_id'].eq(self.cmbCompulsoryPolisCompany.value()))
        if workIndex == 2:
            clientId = self.historyFilter.get('client_id', None)
            actionTypeId = self.historyFilter.get('actionType_id', None)
            serviceId = self.historyFilter.get('service_id', None)
            eventTypeId = self.historyFilter.get('eventType_id', None)
            cond.append(tableEvent['client_id'].eq(clientId))
            if self.chkHistoryOnlyCurrentService.isChecked():
                queryTable = queryTable.leftJoin(tableVisit, tableVisit['id'].eq(table['visit_id']))
                queryTable = queryTable.leftJoin(tableAction, tableAction['id'].eq(table['action_id']))
                condActionEq = [
                    table['action_id'].isNotNull(), tableAction['actionType_id'].eq(actionTypeId)]
                condVisitEq = [table['visit_id'].isNotNull(), tableVisit['service_id'].eq(serviceId)]
                condEventEq = [
                    table['action_id'].isNull(), table['visit_id'].isNull(),
                    tableEvent['eventType_id'].eq(eventTypeId)]
                cond.append(db.joinOr([
                    db.joinAnd(condActionEq), db.joinAnd(condVisitEq), db.joinAnd(condEventEq)]))
        return queryTable, cond

    def __appendDocCondition(self, cond, field, document):
        if document:
            cond.append(field.like(document))
        else:
            cond.append(field.ne(''))

    def __appendNoteCondition(self, cond, field, note):
        if note:
            cond.append(field.like(note))

    def __appendPayStatusCondition(self, cond, field, id):
        if id:
            cond.append(field.eq(id))
        else:
            cond.append(field.isNotNull())

    def formAccountItemReportDescription(self):
        accountRecord = self.modelAccounts.recordCache().get(self.tblAccounts.currentItemId())
        if accountRecord:
            descr = [u'к счету']
        else:
            descr = [u'к неуказанному счёту']

        payer_id = forceString(accountRecord.value('payer_id'))
        payerName = forceString(QtGui.qApp.db.translate('Organisation', 'id', payer_id, 'shortName'))
        descr.append(payerName)

        workIndex = self.tabWorkType.currentIndex()
        if workIndex == 0:
            filterCode = 0
            filterDocument = ''
            filterRefuseType = ''
            filterNote = ''
        elif workIndex == 1:
            filterCode = self.cmbAnalysisAccountItems.currentIndex()
            filterDocument = forceStringEx(self.edtAnalysisDocument.text())
            filterRefuseType = self.cmbAnalysisPayRefuseType.currentText()
            filterNote = forceStringEx(self.edtAnalysisNote.text())
        elif workIndex == 2:
            filterCode = self.cmbHistoryAccountItems.currentIndex()
            filterDocument = forceStringEx(self.edtHistoryDocument.text())
            filterRefuseType = self.cmbHistoryPayRefuseType.currentText()
            filterNote = forceStringEx(self.edtHistoryNote.text())
        if filterDocument:
            filterDocument = u'С подтверждающим документом «%s»' % filterDocument
        if filterRefuseType:
            filterRefuseType = u'С причиной отказа %s' % filterRefuseType
        if filterNote:
            filterNote = u'С примечанием «%s»' % filterNote
        if filterCode == 0:  # 0:Все
            descr.append(u'Все позиции')
        elif filterCode == 1:  # 1:Без подтверждения
            descr.append(u'Позиции без подтверждения')
        elif filterCode == 2:  # 2:Подтверждённые
            descr.append(u'Подтверждённые позиции')
            if filterDocument:
                descr.append(filterDocument)
            if filterNote:
                descr.append(filterNote)
        elif filterCode == 3:  # 3:Оплаченные
            descr.append(u'Оплаченные позиции')
            if filterDocument:
                descr.append(filterDocument)
            if filterNote:
                descr.append(filterNote)
        elif filterCode == 4:  # 4:Отказанные
            descr.append(u'Отказанные позиции')
            if filterDocument:
                descr.append(filterDocument)
            if filterRefuseType:
                descr.append(filterRefuseType)
            if filterNote:
                descr.append(filterNote)
        elif filterCode == 5:  # 5:Перевыставляемые
            descr.append(u'Перевыставляемые позиции')
            if filterDocument:
                descr.append(filterDocument)
            if filterRefuseType:
                descr.append(filterRefuseType)
            if filterNote:
                descr.append(filterNote)
        elif filterCode == 6:  # 6:Неперевыставляемые
            descr.append(u'Неперевыставляемые позиции')
            if filterDocument:
                descr.append(filterDocument)
            if filterRefuseType:
                descr.append(filterRefuseType)
            if filterNote:
                descr.append(filterNote)
        if workIndex == 2:
            descr.append(u'Фильтр по текущему пациенту')
        return u'\n'.join(descr)

    def updateAccountInfo(self):
        db = QtGui.qApp.db
        queryTable, cond = self.formAccountItemQueryParts()
        table = db.table('Account_Item')
        cond.extend([table['master_id'].eq(self.currentAccountId), table['deleted'].eq(0)])
        if self.watchingAccountItemIdList:
            cond.append(table['id'].inlist(self.watchingAccountItemIdList))
        tableClient = db.table('Client')
        order = [tableClient['lastName'].name(),
                 tableClient['firstName'].name(),
                 tableClient['patrName'].name(),
                 tableClient['birthDate'].name(),
                 tableClient['sex'].name(),
                 table['id'].name()
                 ]
        stmt = db.selectStmt(table=queryTable,
                             fields=[table['id'],
                                     table['event_id'].alias('eventId'),
                                     tableClient['id'].alias('clientId'),
                                     table['service_id'].alias('serviceId')],
                             where=cond,
                             order=order
                             )
        query = db.query(stmt)
        idList = []
        eventIdList = []
        clientIdList = []
        serviceIdList = []
        while query.next():
            record = query.record()
            idList.append(forceRef(record.value('id')))
            eventIdList.append(forceRef(record.value('eventId')))
            clientIdList.append(forceRef(record.value('clientId')))
            serviceIdList.append(forceRef(record.value('serviceId')))

        if self.chkAnalysisClientTenPercentRandom.isChecked():
            import random
            newIdList = []
            oldLen = len(idList)
            newIdListLen = int(round(oldLen / 10.0))
            if newIdListLen > 0:
                for counter in xrange(newIdListLen):
                    newIdList.append(idList.pop(random.randint(0, oldLen - counter - 1)))
                idList = newIdList
        currentAccountItemId = self.tblAccountItems.currentItemId()

        # подгрузка данных в кэши
        self.modelAccountItems.recordCache().strongFetch(idList)
        self.modelAccountItems.eventCache.capacity = max(len(eventIdList), 3000)
        self.modelAccountItems.eventCache.strongFetch(eventIdList)
        self.modelAccountItems.clientCache.capacity = max(len(clientIdList), 3000)
        self.modelAccountItems.clientCache.strongFetch(clientIdList)
        self.modelAccountItems.serviceCache.capacity = max(len(serviceIdList), 3000)
        self.modelAccountItems.serviceCache.strongFetch(serviceIdList)
        self.tblAccountItems.setIdList(idList, resetCache=False)

        self.setVisibleFederalPriceColumn()
        self.tblAccountItems.setCurrentItemId(currentAccountItemId)
        self.updateAccountItemsPanel(idList)

    def form(self, contractIdList, date, orgStructureId, reexpose, reexposeInSeparateAccount, checkMes,
             checkCalendarDaysLength, lockEvent, acceptNewKSLPForChild=False):
        progressDialog = None
        self.resetBuilder()
        accountIdList = []
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(Qt.WaitCursor))
        try:
            if orgStructureId:
                personIdList = getOrgStructurePersonIdList(orgStructureId)  # не используется
            else:
                personIdList = None
            try:
                progressDialog = CFormProgressDialog(self)
                progressDialog.setNumContracts(len(contractIdList))
                progressDialog.show()
                # atronah: периодическая проверка соединения путем выполнения тестового запроса
                self.testConnectionTimerId = self.startTimer(299000)
                for contractId in contractIdList:
                    newAccountIdList = self.formByContract(
                        progressDialog, contractId, orgStructureId, personIdList, date, reexpose,
                        reexposeInSeparateAccount, checkMes, checkCalendarDaysLength, lockEvent, acceptNewKSLPForChild)

                    updateAccounts(newAccountIdList, QtGui.qApp.db.db.databaseName())

                    accountIdList += newAccountIdList
                    self.updateFilterAccountsEtc(newAccountIdList if newAccountIdList else None)
            except CFormProgressCanceled:
                pass
        finally:
            QtGui.QApplication.restoreOverrideCursor()
            self.killTimer(self.testConnectionTimerId)
            self.testConnectionTimerId = None
            if progressDialog:
                progressDialog.close()
        return accountIdList

    def formByContract(self, progressDialog, contractId, orgStructureId, personIdList, date, reexpose,
                       reexposeInSeparateAccount, checkMes, checkCalendarDaysLength, lockEvent,
                       acceptNewKSLPForChild=False):
        db = QtGui.qApp.db
        db.transaction()
        try:
            self.date = date
            nextDate = date.addDays(1)
            contractInfo = getContractInfo(contractId)
            remainSum = None
            if contractInfo.deposit > 0:
                sumUsedRecord = db.getRecordEx('Account', 'SUM(Account.sum) as totalSum',
                                               'Account.deleted = 0 AND Account.contract_id = %s' % contractId)
                sumUsed = forceDecimal(sumUsedRecord.value('totalSum'))
                remainSum = forceDecimal(contractInfo.deposit - sumUsed)
                if remainSum <= 0:
                    QtGui.QMessageBox.critical(
                        self, u'Внимание!',
                        u'Выставление счета невозможно, так как сумма депозита по договору %s исчерпана.' % contractInfo.number,
                        QMessageBox.Ok, QMessageBox.Ok)
                    db.rollback()
                    return None
            progressDialog.setContractName(contractInfo.number + ' ' + forceString(contractInfo.date))
            accountPool = CAccountPool(contractInfo, QtGui.qApp.currentOrgId(), orgStructureId, date,
                                       reexposeInSeparateAccount)
            accountFactory = accountPool.getAccount
            eventIdList = selectEvents(contractInfo, personIdList, nextDate, orgStructureId)
            if eventIdList:
                pass
            mapServiceIdToVisitIdList = selectVisitsByActionServices(contractInfo, personIdList, nextDate, orgStructureId)
            visitIdList = selectVisits(contractInfo, personIdList, nextDate, orgStructureId)
            actionIdList = selectActions(contractInfo, personIdList, nextDate, orgStructureId)
            actionPropertyIdList = selectHospitalBedActionProperties(contractInfo, personIdList, nextDate, orgStructureId)
            if reexpose:
                reexposableIdList = selectReexposableAccountItems(contractInfo, nextDate)
            else:
                reexposableIdList = []
            progressDialog.setNumContractSteps(len(eventIdList) +
                                               sum(len(idList) for idList in mapServiceIdToVisitIdList.values()) +
                                               len(visitIdList) +
                                               len(actionIdList) +
                                               len(actionPropertyIdList) +
                                               len(reexposableIdList))
            self.exposeByEvents(progressDialog, contractInfo, accountFactory, eventIdList, checkMes, acceptNewKSLPForChild)
            self.exposeByVisitsByActionServices(progressDialog, contractInfo, accountFactory, mapServiceIdToVisitIdList)
            self.exposeByVisits(progressDialog, contractInfo, accountFactory, visitIdList)
            self.exposeByActions(progressDialog, contractInfo, accountFactory, actionIdList, checkMes)
            self.exposeByHospitalBedActionProperties(
                progressDialog, contractInfo, accountFactory, actionPropertyIdList, checkCalendarDaysLength)
            if reexpose:
                self.reexpose(progressDialog, contractInfo, accountFactory, reexposableIdList)
            if contractInfo.exposeDiscipline != 2:
                accountPool.addAccountIfEmpty(reexpose)
            accountPool.updateDetails()
            detailsList = accountPool.getDetailsList()
            if remainSum != None:
                exposedSum = forceDecimal(0)
                for details in detailsList:
                    exposedSum += details.totalSum
                if exposedSum > remainSum:
                    QMessageBox.critical(
                        self, u'Внимание!',
                        u'Выставление счета невозможно, так как выставляемая сумма превышает сумму депозита по договору %s.' % contractInfo.number,
                        QMessageBox.Ok, QMessageBox.Ok)
                    db.rollback()
                    return None
            accounts = accountPool.getAccountIdList()
            if lockEvent and accounts:
                self.lockEventsByAccounts(accounts)
            db.commit()
            return accounts
        except:
            db.rollback()
            QtGui.qApp.logCurrentException()
            raise

    def lockEventsByAccounts(self, accounts):
        q = u'UPDATE Event ' \
            u'SET locked=1 ' \
            u'WHERE id IN (' \
            u'  SELECT event_id ' \
            u'  FROM Account_Item ' \
            u'  WHERE master_id IN (\'{}\')' \
            u')'.format('\', \''.join([str(x) for x in accounts]))
        QtGui.qApp.db.query(q)

    def getEventRecord(self, eventId):
        # for CAccountBuilder, we need eventType_id, client_id, exec_date
        return self.modelAccountItems.eventCache.get(eventId)

    def getClientRecord(self, clientId):
        # for CAccountBuilder, we need sex and birthDate
        return self.modelAccountItems.clientCache.get(clientId)

    def getCurrentEventId(self):
        itemId = self.tblAccountItems.currentItemId()
        if itemId:
            itemRecord = self.modelAccountItems.recordCache().get(itemId)
            if itemRecord:
                return forceRef(itemRecord.value('event_id'))
        return None

    def getCurrentIds(self):
        clientId = None
        eventId = None
        visitId = None
        actionId = None
        eventTypeId = None
        serviceId = None
        actionTypeId = None

        itemId = self.tblAccountItems.currentItemId()
        if itemId:
            itemRecord = self.modelAccountItems.recordCache().get(itemId)
            if itemRecord:
                eventId = forceRef(itemRecord.value('event_id'))
                visitId = forceRef(itemRecord.value('visit_id'))
                actionId = forceRef(itemRecord.value('action_id'))
                if eventId:
                    eventRecord = self.modelAccountItems.eventCache.get(eventId)
                    if eventRecord:
                        clientId = forceRef(eventRecord.value('client_id'))
                        eventTypeId = forceRef(eventRecord.value('eventType_id'))
                if visitId:
                    visitRecord = self.modelAccountItems.visitCache.get(visitId)
                    if visitRecord:
                        serviceId = forceRef(visitRecord.value('service_id'))
                if actionId:
                    actionRecord = self.modelAccountItems.actionCache.get(actionId)
                    if actionRecord:
                        actionTypeId = forceRef(actionRecord.value('actionType_id'))
        return (clientId, eventTypeId, serviceId, actionTypeId)

    def getCurrentClientId(self):
        eventId = self.getCurrentEventId()
        if eventId:
            eventRecord = self.modelAccountItems.eventCache.get(eventId)
            if eventRecord:
                return forceRef(eventRecord.value('client_id'))
        return None

    def prepareHistoryFilterParameters(self):
        clientId, eventTypeId, serviceId, actionTypeId = self.getCurrentIds()
        self.historyFilter = {'client_id': clientId,
                              'eventType_id': eventTypeId,
                              'service_id': serviceId,
                              'actionType_id': actionTypeId}

    def updateDocsPayStatus(self, accountItem, contractInfo, bits):
        updateDocsPayStatus(accountItem, contractInfo.payStatusMask, bits)

    def execAccountItemsReport(self, reportClass, params=None):
        if not params:
            params = {}

        def execAccountItemsReportInt():
            report = reportClass(self)
            descr = self.formAccountItemReportDescription()
            params.update({'accountId': self.currentAccountId,
                           'accountItemIdList': self.modelAccountItems.idList(),
                           'currentFinanceId': self.currentFinanceId
                           })
            reportTxt = report.build(descr, params)
            view = CReportViewDialog(self)
            view.setWindowTitle(report.title())
            view.setText(reportTxt)
            return view

        view = QtGui.qApp.callWithWaitCursor(self, execAccountItemsReportInt)
        view.exec_()

    def execAccountItemsReportInsurer(self, reportClass, orgInsurerId=None, assistant=False):
        def execAccountItemsReportInsurerInt():
            report = reportClass(self)
            descr = self.formAccountItemReportDescription()
            params = {'accountId': self.currentAccountId,
                      'accountIdList': self.modelAccountItems.idList(),
                      'orgInsurerId': orgInsurerId,
                      'currentFinanceId': self.currentFinanceId,
                      'assistant': assistant
                      }
            if orgInsurerId:
                reportTxt = report.build(descr, params)
            view = CReportViewDialog(self)
            view.setWindowTitle(report.title())
            view.setText(reportTxt)
            return view

        view = QtGui.qApp.callWithWaitCursor(self, execAccountItemsReportInsurerInt)
        view.exec_()

    # TODO: Atronah: частично объединить с execAccountItemsReportInsurer и execAccountItemsReport
    def execPrintR51Registry(self, reportClass, orgInsurerId=None, isLocRegistry=True):
        def execAccountItemsReportInt():
            report = reportClass(self)
            params = {'accountId': self.currentAccountId,
                      'accountItemIdList': self.modelAccountItems.idList(),
                      'orgInsurerId': orgInsurerId,
                      'isLocRegistry': isLocRegistry,
                      'begDate': self.edtAnalysisBegDate.date(),
                      'endDate': self.edtAnalysisEndDate.date()
                      }
            reportTxt = report.build(params)
            view = CReportViewDialog(self)
            view.setWindowTitle(report.title())
            view.setText(reportTxt)
            return view

        view = QtGui.qApp.callWithWaitCursor(self, execAccountItemsReportInt)
        view.exec_()

    def execPrintR23Registry(self, reportClass, orgInsurerId, orgStructure, registryNumber):
        def execAccountItemsReportInt():
            report = reportClass(self)
            params = {'accountId': self.currentAccountId,
                      'accountItemIdList': self.modelAccountItems.idList(),
                      'orgInsurerId': orgInsurerId,
                      'orgStructure': orgStructure,
                      'registryNumber': registryNumber
                      }
            reportTxt = report.build(params)
            view = CReportViewDialog(self)
            view.setWindowTitle(report.title())
            view.setText(reportTxt)
            return view

        view = QtGui.qApp.callWithWaitCursor(self, execAccountItemsReportInt)
        view.exec_()

    def __setupDocumentAndPayRefuseType(self, index, edtDocument, cmbPayRefuseType, edtNote):
        edtDocument.setEnabled(index not in [0, 1])
        edtNote.setEnabled(index not in [0, 1])
        if index == 4:
            cmbPayRefuseType.setFilter('')
            cmbPayRefuseType.setEnabled(True)
        elif index == 5:
            cmbPayRefuseType.setFilter('rerun!=0 AND finance_id=\'%s\'' % self.currentFinanceId)
            cmbPayRefuseType.setEnabled(True)
        elif index == 6:
            cmbPayRefuseType.setFilter('rerun=0 AND finance_id=\'%s\'' % self.currentFinanceId)
            cmbPayRefuseType.setEnabled(True)
        else:
            cmbPayRefuseType.setEnabled(False)

    def runGenRep(self, formatName):
        if formatName:
            queryTable, cond = self.formAccountItemQueryParts()
            #                cond.append(db.table('Account_Item')['master_id'].eq(self.currentAccountId))
            if cond:
                cond = QtGui.qApp.db.joinAnd(cond)
            else:
                cond = ''
            descr = self.formAccountItemReportDescription()
            QtGui.qApp.execProgram('genrep', [formatName, self.currentAccountId, cond, descr])

    @pyqtSlot()
    def timerEvent(self, event):
        if event.timerId() == self.testConnectionTimerId:
            QtGui.qApp.db.checkConnect(True)

    @pyqtSlot(QModelIndex, QModelIndex)
    def on_selectionModelContracts_currentChanged(self, current, previous):
        self.updateFilterAccountsEtc()

    @pyqtSlot(QModelIndex)
    def on_treeContracts_doubleClicked(self, index):
        contractIdList = self.getContractIdList(self.treeContracts.currentIndex())
        if contractIdList and len(contractIdList) == 1:
            dialog = CContractEditor(self)
            dialog.freezeHeadFields()
            dialog.load(contractIdList[0])
            dialog.exec_()

    @pyqtSlot(int)
    def on_tabWorkType_currentChanged(self, index):
        if index == 2:
            self.prepareHistoryFilterParameters()
        self.updateFilterAccountsEtc()

    @pyqtSlot(int)
    def on_cmbAnalysisAccountItems_currentIndexChanged(self, index):
        self.__setupDocumentAndPayRefuseType(
            index, self.edtAnalysisDocument, self.cmbAnalysisPayRefuseType, self.edtAnalysisNote)

    @pyqtSlot(bool)
    def on_chkAnalysisClientCode_clicked(self, checked):
        if checked:
            self.chkAnalysisClientLastName.setChecked(not checked)
            self.chkAnalysisClientFirstName.setChecked(not checked)
            self.chkAnalysisClientPatrName.setChecked(not checked)
            self.chkAnalysisClientBirthday.setChecked(not checked)

    @pyqtSlot(bool)
    def on_chkAnalysisClientLastName_clicked(self, checked):
        if checked:
            self.chkAnalysisClientCode.setChecked(not checked)

    @pyqtSlot(bool)
    def chkAnalysisClientFirstName_clicked(self, checked):
        if checked:
            self.chkAnalysisClientCode.setChecked(not checked)

    @pyqtSlot(bool)
    def on_chkAnalysisClientPatrName_clicked(self, checked):
        if checked:
            self.chkAnalysisClientCode.setChecked(not checked)

    @pyqtSlot(bool)
    def on_chkAnalysisClientBirthday_clicked(self, checked):
        if checked:
            self.chkAnalysisClientCode.setChecked(not checked)

    @pyqtSlot(bool)
    def on_chkAnalysisServiceArea_clicked(self, checked):
        if checked:
            self.chkAnalysisClientCode.setChecked(not checked)

    @pyqtSlot(QtGui.QAbstractButton)
    def on_bbxAnalysis_clicked(self, button):
        buttonCode = self.bbxAnalysis.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.updateFilterAccountsEtc()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.resetAnalysisPage()
            self.updateFilterAccountsEtc()

    @pyqtSlot(int)
    def on_cmbHistoryAccountItems_currentIndexChanged(self, index):
        self.__setupDocumentAndPayRefuseType(
            index, self.edtHistoryDocument, self.cmbHistoryPayRefuseType, self.edtHistoryNote)

    @pyqtSlot(QtGui.QAbstractButton)
    def on_bbxHistory_clicked(self, button):
        buttonCode = self.bbxHistory.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.updateFilterAccountsEtc()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.resetHistoryPage()
            self.updateFilterAccountsEtc()

    def editCurrentAccount(self):
        isAccountant = QtGui.qApp.userHasAnyRight(accountantRightList)
        if isAccountant:
            dialog = CAccountEditDialog(self)
            id = self.tblAccounts.currentItemId()
            if id:
                dialog.load(id)
                if dialog.exec_():
                    self.updateFilterAccountsEtc(id)

    @pyqtSlot(QModelIndex)
    def on_tblAccounts_doubleClicked(self, index):
        self.editCurrentAccount()

    @pyqtSlot(QModelIndex, QModelIndex)
    def on_selectionModelAccounts_currentRowChanged(self, current, previous):
        self.currentAccountId = self.tblAccounts.itemId(current)
        self.currentFinanceId = None
        if self.currentAccountId:
            contractId = forceRef(QtGui.qApp.db.translate(
                'Account', 'id', self.currentAccountId, 'contract_id'))
            if contractId:
                self.currentFinanceId = forceRef(QtGui.qApp.db.translate(
                    'Contract', 'id', contractId, 'finance_id'))
            isPrintR23Registry = False
            isPrintR51Registry = False
            exportInfo = getAccountExportFormat(self.currentAccountId).split()
            if exportInfo:
                isPrintR51Registry = exportInfo[0] == 'R51OMS'
                isPrintR23Registry = exportInfo[0] in ('R23NATIVE', 'R23NATIVES', 'R23DKKB', 'R23DKKBS')
            self.actPrintR51LocRegistry.setVisible(isPrintR51Registry)
            self.actPrintR51ExtRegistry.setVisible(isPrintR51Registry)
            self.actPrintR23Registry.setVisible(isPrintR23Registry)
        self.updateAccountInfo()

    @pyqtSlot()
    def on_mnuAccounts_aboutToShow(self):
        isWatchMode = (self.eventIdWatching or self.actionIdWatching or self.visitIdWatching)
        isAccountant = QtGui.qApp.userHasAnyRight(accountantRightList)
        currentRow = self.tblAccounts.currentIndex().row()
        itemPresent = currentRow >= 0 and isAccountant
        enablePrint = False
        if itemPresent:
            exportInfo = getAccountExportFormat(self.currentAccountId).split()
            if exportInfo:
                enablePrint = bool(exportInfo[0])
        else:
            enablePrint = False

        self.actEditAccount.setEnabled(itemPresent)
        self.actPrintAccount.setEnabled(enablePrint and not isWatchMode)
        self.actPrintAccountRegistry.setEnabled(enablePrint and not isWatchMode)
        self.actPrintAccountSummary.setEnabled(itemPresent and not isWatchMode)
        self.actPrintAccountInsurer.setEnabled(itemPresent and not isWatchMode)
        self.actReportByDoctorsEx.setEnabled(itemPresent and not isWatchMode)
        self.actReportByServicesEx.setEnabled(itemPresent and not isWatchMode)
        self.actCheckMesInAccount.setEnabled(itemPresent and not isWatchMode)
        self.actSelectAllAccounts.setEnabled(itemPresent)
        self.actDeleteAccounts.setEnabled(itemPresent)

    @pyqtSlot()
    def on_actEditAccount_triggered(self):
        self.editCurrentAccount()

    @pyqtSlot()
    def on_actPrintAccount_triggered(self):
        if self.currentAccountId:
            formatName = ''
            exportInfo = getAccountExportFormat(self.currentAccountId).split()
            if exportInfo:
                if exportInfo[0] == 'RD1':
                    formatName = 'CH1'
                elif exportInfo[0] == 'RD2':
                    formatName = 'CH2'
                elif exportInfo[0] in ('RD3', 'RD-DS'):
                    formatName = 'CH3'
                elif exportInfo[0] == 'RD4':
                    formatName = 'CH4'
                elif exportInfo[0] in ('RD5', 'RD6'):
                    formatName = 'CH5'
                elif exportInfo[0] == 'RD7':
                    # TODO: Костыль для genrep, после фикса - вернуть CH7
                    # formatName = 'CH7'
                    formatName = 'CH5'
                elif exportInfo[0] == 'R51DD2010':
                    formatName = 'CH51DD2010'
                else:
                    formatName = 'CH' + exportInfo[0]

            self.runGenRep(formatName)

    @pyqtSlot()
    def on_actPrintAccountSummary_triggered(self):
        if self.currentAccountId:
            self.execAccountItemsReport(CAccountSummary)

    @pyqtSlot()
    def on_actPrintAccountInsurer_triggered(self):
        if self.currentAccountId:
            ok, orgInsurerId, assistant = selectInsurer(self, True)
            if orgInsurerId:
                self.execAccountItemsReportInsurer(CAccountSummary, orgInsurerId)

    @pyqtSlot()
    def on_actPrintAccountRegistry_triggered(self):
        if self.currentAccountId:
            formatName = ''
            exportInfo = getAccountExportFormat(self.currentAccountId).split()
            if exportInfo:
                if exportInfo[0] == 'RD-DS':
                    formatName = 'RD3'
                # TODO: Костыль для genrep, необходимо убрать
                elif exportInfo[0] == 'RD7':
                    formatName = 'RD6'
                    # END TODO
                else:
                    formatName = exportInfo[0]
            self.runGenRep(formatName)

    @pyqtSlot()
    def on_actCheckMesInAccount_triggered(self):
        if self.currentAccountId:
            self.resetBuilder()
            db = QtGui.qApp.db
            contractId = forceRef(db.translate('Account', 'id', self.currentAccountId, 'contract_id'))
            contractInfo = getContractInfo(contractId)
            financeId = contractInfo.finance_id
            # фишка в sum для списков; по определению это reduce(operator.add, a, [])
            tariffList = dict([(tariff.id, tariff) for tariff in sum(contractInfo.tariffVisitsByMES.values(), [])])
            semifinishedMesRefuseTypeId = self.getSemifinishedMesRefuseTypeId(financeId)
            itemIdList = self.tblAccountItems.selectedItemIdList()
            tableAccountItem = db.table('Account_Item')
            tableContractTariff = db.table('Contract_Tariff')
            table = tableAccountItem.leftJoin(tableContractTariff,
                                              tableContractTariff['id'].eq(tableAccountItem['tariff_id']))
            cond = [tableAccountItem['id'].inlist(itemIdList),
                    db.joinOr([tableAccountItem['date'].isNull(),
                               tableAccountItem['refuseType_id'].eq(semifinishedMesRefuseTypeId)]),
                    tableContractTariff['tariffType'].eq(CTariff.ttVisitsByMES)
                    ]
            modifiedItemCount = 0
            amountModified = False
            for accountItem in db.getRecordList(table, 'Account_Item.*', cond):
                itemModified = False
                eventId = forceRef(accountItem.value('event_id'))
                clientId = forceRef(db.translate('Event', 'id', eventId, 'client_id'))
                mesId = forceRef(db.translate('Event', 'id', eventId, 'MES_id'))
                tariffId = forceRef(accountItem.value('tariff_id'))
                tariff = tariffList.get(tariffId, None)
                if tariff:
                    amount = float(getMesAmount(eventId, mesId))
                    amount, price, sum_ = tariff.evalAmountPriceSum(amount, clientId)
                    norm = self.getMesNorm(mesId)
                    if amount < norm and accountItem.value('refuseType_id').isNull():
                        self.rejectAccountItemBySemifinishedMes(accountItem, financeId)
                        itemModified = True
                    if amount != forceDecimal(
                            accountItem.value('amount')):  # верую, что небольшие целые числа не портятся
                        accountItem.setValue('amount', toVariant(amount))
                        accountItem.setValue('price', toVariant(price))
                        accountItem.setValue('sum', toVariant(sum_))
                        itemModified = True
                        amountModified = True
                    if itemModified:
                        db.updateRecord(tableAccountItem, accountItem)
                        modifiedItemCount += 1
            if amountModified:
                updateAccountTotals(self.currentAccountId)
                self.updateFilterAccountsEtc()
            currentAccountItemId = self.tblAccountItems.currentItemId()
            if modifiedItemCount:
                self.modelAccountItems.invalidateRecordsCache()
                self.tblAccountItems.setCurrentItemId(currentAccountItemId)
            QtGui.QMessageBox.information(self,
                                          u'Проверка счёта',
                                          u'Проверка счёта на соответствие МЭС закончена.'
                                          + (('\n'
                                              + agreeNumberAndWord(modifiedItemCount,
                                                                   (u'Измененa', u'Изменено', u'Изменено'))
                                              + ' '
                                              + formatNum(modifiedItemCount, (u'позиция', u'позиции', u'позиций'))
                                              + u' счёта')
                                             if modifiedItemCount
                                             else ''),
                                          QtGui.QMessageBox.Ok,
                                          QtGui.QMessageBox.Ok)

    @pyqtSlot()
    def on_actSelectAllAccounts_triggered(self):
        self.tblAccounts.selectAll()

    @pyqtSlot()
    def on_actDeleteAccounts_triggered(self):
        self.tblAccounts.removeSelectedRows()
        self.updateAccountsPanel(self.modelAccounts.idList())

    @pyqtSlot(QModelIndex, QModelIndex)
    def on_selectionModelAccountItems_currentRowChanged(self, current, previous):
        currentAccountItemId = self.tblAccountItems.itemId(current)
        self.updateAccountItemInfo(currentAccountItemId)

    @pyqtSlot()
    def on_mnuAccountItems_aboutToShow(self):
        isWatchMode = (self.eventIdWatching or self.actionIdWatching or self.visitIdWatching)
        isAccountant = QtGui.qApp.userHasAnyRight(accountantRightList)
        currentRow = self.tblAccountItems.currentIndex().row()
        itemPresent = currentRow >= 0 and isAccountant
        self.actOpenClient.setEnabled(
            itemPresent and QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteRegistry]) and not isWatchMode)
        self.actOpenEvent.setEnabled(itemPresent and not isWatchMode)
        self.actSetPayment.setEnabled(itemPresent and QtGui.qApp.userHasRight(urAccessEditPayment))
        self.actEditPayment.setEnabled(itemPresent and QtGui.qApp.userHasRight(urAccessEditPayment))
        self.actSelectExposed.setEnabled(itemPresent and not isWatchMode)
        self.actSelectAll.setEnabled(itemPresent and not isWatchMode)
        self.actReportByRegistry.setEnabled(itemPresent and not isWatchMode)
        self.actReportByRegistryDMS.setEnabled(itemPresent and not isWatchMode)
        self.actPrintR51LocRegistry.setEnabled(itemPresent and not isWatchMode)
        self.actPrintR51ExtRegistry.setEnabled(itemPresent and not isWatchMode)
        self.actPrintR23Registry.setEnabled(itemPresent and not isWatchMode)
        self.actReportByClients.setEnabled(itemPresent and not isWatchMode)
        self.actReportByClientsTwoAddr.setEnabled(itemPresent and not isWatchMode)
        self.actReportByDoctors.setEnabled(itemPresent and not isWatchMode)
        self.actReportDopDisp.setEnabled(itemPresent and not isWatchMode)
        self.actReportByServices.setEnabled(itemPresent and not isWatchMode)
        self.actDeleteAccountItems.setEnabled(itemPresent)

    @pyqtSlot()
    def on_actOpenClient_triggered(self):
        clientId = self.getCurrentClientId()
        if clientId and QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteRegistry]):
            dialog = CClientEditDialog(self)
            dialog.load(clientId)
            if dialog.exec_():
                self.modelAccountItems.invalidateRecordsCache()

    @pyqtSlot()
    def on_actOpenEvent_triggered(self):
        eventId = self.getCurrentEventId()
        if eventId:
            formClass = getEventFormClass(eventId)
            dialog = formClass(self)
            dialog.load(eventId)
            dialog.setClientId(self.getCurrentClientId())
            dialog.exec_()

    @pyqtSlot()
    def on_actSetPayment_triggered(self):
        if setPayment(self, self.currentAccountId, self.tblAccountItems.selectedItemIdList(), self.payParams):
            currentAccountItemId = self.tblAccountItems.currentItemId()
            self.updateFilterAccountsEtc()
            self.modelAccountItems.invalidateRecordsCache()
            self.tblAccountItems.setCurrentItemId(currentAccountItemId)

    @pyqtSlot()
    def on_actEditPayment_triggered(self):
        accountItemId = self.tblAccountItems.currentItemId()
        if accountItemId:
            itemRecord = self.modelAccountItems.recordCache().get(accountItemId)
            payParams = {}
            payParams['date'] = forceDate(itemRecord.value('date'))
            payParams['number'] = forceString(itemRecord.value('number'))
            payParams['refuseTypeId'] = forceRef(itemRecord.value('refuseType_id'))
            payParams['accepted'] = payParams['refuseTypeId'] is None
            payParams['note'] = forceString(itemRecord.value('note'))
            if editPayment(self, self.currentAccountId, accountItemId, payParams):
                currentAccountItemId = self.tblAccountItems.currentItemId()
                self.updateFilterAccountsEtc()
                self.modelAccountItems.invalidateRecordsCache()
                self.tblAccountItems.setCurrentItemId(currentAccountItemId)

    @pyqtSlot()
    def on_actSelectExposed_triggered(self):
        db = QtGui.qApp.db
        table = db.table('Account_Item')
        idList = self.modelAccountItems.idList()
        cond = []
        cond.append(table['id'].inlist(idList))
        cond.append(db.joinOr([table['date'].isNull(), table['number'].eq('')]))
        exposedIdList = db.getIdList(table, where=cond)
        selectionModel = self.tblAccountItems.selectionModel()
        if not ((QtGui.qApp.keyboardModifiers() & Qt.ControlModifier) != Qt.NoModifier):
            selectionModel.clear()
        rows = []
        for id in exposedIdList:
            row = idList.index(id)
            rows.append(row)
        rows.sort()
        lastIndex = None
        for row in rows:
            index = self.modelAccountItems.index(row, 0)
            selectionModel.select(index, QtGui.QItemSelectionModel.Select | QtGui.QItemSelectionModel.Rows)
            lastIndex = index
        if lastIndex:
            selectionModel.setCurrentIndex(lastIndex, QtGui.QItemSelectionModel.NoUpdate)

    @pyqtSlot()
    def on_actSelectAll_triggered(self):
        self.tblAccountItems.selectAll()

    @pyqtSlot()
    def on_actPrintR51LocRegistry_triggered(self):
        ok, orgInsurerId, assistant = selectInsurer(self, False)
        if ok:
            self.execPrintR51Registry(CAccountRegistryR51, orgInsurerId, isLocRegistry=True)

    @pyqtSlot()
    def on_actPrintR51ExtRegistry_triggered(self):
        ok, orgInsurerId, assistant = selectInsurer(self, False)
        if ok:
            self.execPrintR51Registry(CAccountRegistryR51, orgInsurerId, isLocRegistry=False)

    @pyqtSlot()
    def on_actPrintR23Registry_triggered(self):
        ok, orgId, orgStructure, registryNumber = getAccountRegistryR23Params(self)
        if ok:
            self.execPrintR23Registry(CAccountRegistryR23, orgId, orgStructure, registryNumber)

    @pyqtSlot()
    def on_actReportByRegistry_triggered(self):
        ok, orgInsurerId, assistant = selectInsurer(self, False)
        if ok:
            if orgInsurerId:
                self.execAccountItemsReportInsurer(CAccountRegistry, orgInsurerId, assistant)
            else:
                self.execAccountItemsReport(CAccountRegistry, {'assistant': assistant})

    @pyqtSlot()
    def on_actReportByRegistryDMS_triggered(self):
        ok, orgInsurerId, assistant = selectInsurer(self, False)
        if ok:
            if orgInsurerId:
                self.execAccountItemsReportInsurer(CAccountRegistryDMS, orgInsurerId, assistant)
            else:
                self.execAccountItemsReport(CAccountRegistryDMS, {'assistant': assistant})

    @pyqtSlot()
    def on_actReportByClients_triggered(self):
        self.execAccountItemsReport(CClientsListByRegistry)

    @pyqtSlot()
    def on_actReportByClientsTwoAddr_triggered(self):
        self.execAccountItemsReport(CClientsListByRegistry, {'showLocAddr': True})

    @pyqtSlot()
    def on_actReportByDoctors_triggered(self):
        self.execAccountItemsReport(CFinanceSummaryByDoctors)

    @pyqtSlot()
    def on_actReportDopDisp_triggered(self):
        self.execAccountItemsReport(CReportDopDisp)

    @pyqtSlot()
    def on_actReportByDoctorsEx_triggered(self):
        CFinanceSummaryByDoctorsEx(self).exec_(self.modelAccounts.idList())

    @pyqtSlot()
    def on_actReportByServices_triggered(self):
        self.execAccountItemsReport(CFinanceSummaryByServices)

    @pyqtSlot()
    def on_actReportByServicesEx_triggered(self):
        CFinanceSummaryByServicesEx(self).exec_(self.modelAccounts.idList())

    @pyqtSlot(int)
    def on_actPrintAccountByTemplate_printByTemplate(self, templateId):
        context = CInfoContext()
        accountInfo = context.getInstance(CAccountInfo, self.currentAccountId)
        accountInfo.selectedItemIdList = self.modelAccountItems.idList()
        data = {'account': accountInfo,
                'client': CClientInfo(context, self.getCurrentClientId(), None)}
        applyTemplate(self, templateId, data)

    @pyqtSlot()
    def on_actDeleteAccountItems_triggered(self):
        db = QtGui.qApp.db
        table = db.table('Account_Item')
        selectedItemIdList = self.tblAccountItems.selectedItemIdList()
        cond = [table['id'].inlist(selectedItemIdList), table['date'].isNotNull(), table['number'].ne('')]
        itemIdList = db.getIdList(table, where=cond)
        if itemIdList:
            QtGui.QMessageBox.critical(self,
                                       u'Внимание!',
                                       u'Подтверждённые записи реестра не подлежат удалению',
                                       QtGui.QMessageBox.Close)
        else:
            n = len(selectedItemIdList)
            message = u'Вы действительно хотите удалить %s реестра? ' % formatNum1(n,
                                                                                   (u'запись', u'записи', u'записей'))
            if QtGui.QMessageBox.question(self,
                                          u'Внимание!',
                                          message,
                                          QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                          QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:

                QtGui.QApplication.setOverrideCursor(QtGui.QCursor(Qt.WaitCursor))
                try:
                    # db.transaction()
                    try:
                        clearPayStatus(self.currentAccountId, selectedItemIdList)
                        db.markRecordsDeleted(table, table['id'].inlist(selectedItemIdList))
                        # removeAccountItems(selectedItemIdList)
                        updateAccount(self.currentAccountId)
                        # db.commit()
                    except:
                        db.rollback()
                        QtGui.qApp.logCurrentException()
                        raise
                    self.updateAccountInfo()
                    self.updateFilterAccountsEtc(self.currentAccountId)
                finally:
                    QtGui.QApplication.restoreOverrideCursor()

    @pyqtSlot()
    def on_btnForm_clicked(self):
        contractIdList = self.getContractIdList(self.treeContracts.currentIndex())
        if not contractIdList:
            QtGui.QMessageBox.warning(self,
                                      u'Внимание!',
                                      u'Для формирования счёта необходимо выбрать договор',
                                      QtGui.QMessageBox.Close)
            return
        date = self.clnCalcCalendar.selectedDate()
        lst = formatList([self.modelContracts.contracts[contractId] for contractId in contractIdList])
        message = u'Подтвердите, что Вы действительно хотите сформировать счета\nпо %s %s\nна дату %s' % \
                  ((u'договору № ' if len(contractIdList) == 1 else u'договорам №№ '),
                   lst if len(lst) < 400 else lst[:400] + u'...',
                   forceString(date)
                   )
        dialog = CExposeConfirmationDialog(self, foldText(message, [80]))
        if dialog.exec_():
            filterPaymentByOrgStructure, reexpose, reexposeInSeparateAccount, checkMes, checkCalendarDaysLength, showStats, lockEvent, acceptNewKSLPForChild = dialog.options()
            if filterPaymentByOrgStructure:
                orgStructureId = self.cmbCalcOrgStructure.value()
            else:
                orgStructureId = None
            accountIdList = self.form(contractIdList, date, orgStructureId, reexpose, reexposeInSeparateAccount,
                                      checkMes, checkCalendarDaysLength, lockEvent, acceptNewKSLPForChild)
            if showStats:
                statsDialog = CExposeStatisticsDialog(self, accountIdList)
                statsDialog.refreshStatistics()
                statsDialog.exec_()

    @pyqtSlot()
    def on_btnFLC_clicked(self):
        contractIdList = self.getContractIdList(self.treeContracts.currentIndex())
        if not contractIdList:
            QtGui.QMessageBox.warning(self,
                                      u'Внимание!',
                                      u'Для проведения ФЛК необходимо выбрать договор',
                                      QtGui.QMessageBox.Close)
            return
        date = self.clnCalcCalendar.selectedDate()
        accountIdList = self.form(contractIdList, date, None, False, False, True, False)
        if accountIdList:
            from Exchange.R85.ExportMultiple import exportR85Multiple
            exportR85Multiple(self, accountIdList)
        else:
            QtGui.QMessageBox.warning(self, u'Внимание!',
                                      u'Отсутствуют данные для проведения ФЛК.')

    @pyqtSlot()
    def on_btnECashRegister_clicked(self):
        registerCheckInECR(self, self.franchisePercent)
        currentAccountItemId = self.tblAccountItems.currentItemId()
        self.updateFilterAccountsEtc()
        self.modelAccountItems.invalidateRecordsCache()
        self.tblAccountItems.setCurrentItemId(currentAccountItemId)

    @pyqtSlot()
    def on_mnuBtnPrint_aboutToShow(self):
        self.on_mnuAccounts_aboutToShow()
        self.on_mnuAccountItems_aboutToShow()

    def checkFLCStatuses(self):
        stmt = u'''
            SELECT
                COUNT(*) AS count
            FROM
                Account
                INNER JOIN Account_Item ON Account.id = Account_Item.master_id
                INNER JOIN Event ON Event.id = Account_Item.event_id
            WHERE
                Event.FLCStatus != 2
                AND Account.id = %i
        ''' % self.currentAccountId
        query = QtGui.qApp.db.query(stmt)
        query.next()
        record = query.record()
        return forceInt(record.value('count')) == 0

    @pyqtSlot()
    def on_btnExport_clicked(self):
        exportInfo = getAccountExportFormat(self.currentAccountId).split()
        if exportInfo:
            exportFormat = exportInfo[0]
            accountItemIdList = self.modelAccountItems.idList()
            if exportFormat in ('RD1', 'RD2', 'RD3', 'RD4', 'RD-DS', 'RD5', 'RD6', 'RD7'):
                from Exchange.Export_RD1_RD2 import Export_RD1_RD2
                Export_RD1_RD2(accountItemIdList, [self.currentAccountId], self).exec_()
            # СПБ
            elif exportFormat == 'EISOMS':
                from Exchange.ExportEISOMS import exportEISOMS
                exportEISOMS(self, self.currentAccountId, accountItemIdList)
            # Краснодарский край стационар
            elif exportFormat == 'R23NATIVES':
                from Exchange.ExportR23NativeS import exportR23NativeS
                exportR23NativeS(self, self.currentAccountId, accountItemIdList)
            # Краснодар Стационар (ДККБ only)
            elif exportFormat == 'R23DKKBS':
                from Exchange.R23.ExportDKKBHospital import exportR23DKKBS
                exportR23DKKBS(self, self.currentAccountId, accountItemIdList)
            # Краснодарский край амбулатория
            elif exportFormat == 'R23NATIVE':
                exportR23Native(self, self.currentAccountId, accountItemIdList)
            # Краснодар амбулатория (ДККБ only).
            elif exportFormat == 'R23DKKB':
                from Exchange.R23.ExportDKKB import exportR23DKKB
                exportR23DKKB(self, self.currentAccountId, accountItemIdList)
            else:
                QtGui.QMessageBox.warning(self, u'Внимание!',
                                          u'Формат %s на данный момент не поддерживается' % exportFormat,
                                          QtGui.QMessageBox.Close)

            self.modelAccounts.invalidateRecordsCache()
        else:
            QtGui.QMessageBox.warning(self, u'Внимание!', u'Не выбран реестр для экспорта', QtGui.QMessageBox.Close)

    @pyqtSlot()
    def on_btnFLCImport_clicked(self):
        def updateData():
            CRBModelDataCache.reset('rbPayRefuseType')
            self.modelAccountItems.invalidateRecordsCache()
            self.cmbAnalysisPayRefuseType.reloadData()
            self.cmbHistoryPayRefuseType.reloadData()
            self.updateFilterAccountsEtc()

        from Exchange.R85.ImportPayRefuseR85 import importPayRefuseR85
        importPayRefuseR85(self, QtGui.qApp.currentOrgId(), True)
        updateData()

    @pyqtSlot()
    def on_btnImport_clicked(self):
        def updateData():
            CRBModelDataCache.reset('rbPayRefuseType')
            self.modelAccountItems.invalidateRecordsCache()
            self.cmbAnalysisPayRefuseType.reloadData()
            self.cmbHistoryPayRefuseType.reloadData()
            self.updateFilterAccountsEtc()

        exportInfo = getAccountExportFormat(self.currentAccountId).split()
        if not exportInfo:
            contractIds = self.getContractIdList(self.treeContracts.currentIndex())
            if contractIds and len(contractIds) == 1:
                exportInfo = getContractExportFormat(contractIds[0]).split()

        if exportInfo:
            exportFormat = exportInfo[0]
            if exportFormat in ('RD1', 'RD4', 'RD5', 'RD6', 'RD7'):
                accountItemIdList = self.modelAccountItems.idList()
                ImportRD1(self, self.currentAccountId, accountItemIdList)
                updateData()
            elif exportFormat in ('R23NATIVE', 'R23NATIVES', 'R23DKKB', 'R23DKKBS'):
                ImportPayRefuseR23Native(self, self.currentAccountId, self.modelAccountItems.idList(), exportFormat)
                updateData()
            elif exportFormat == 'EISOMS':
                importEISOMS(self, self.currentAccountId)
                updateData()
            else:
                QtGui.QMessageBox.warning(self, u'Внимание!',
                                          u'Формат %s на данный момент не поддерживается' % exportFormat,
                                          QtGui.QMessageBox.Close)
        else:
            QtGui.QMessageBox.warning(self, u'Внимание!', u'Не выбран реестр для импорта', QtGui.QMessageBox.Close)

    def on_tblAccountItems_doubleClicked(self, index):
        if not QtGui.qApp.userHasRight(urEditAccountItem):
            return
        itemId = self.tblAccountItems.itemId(index)
        record = self.tblAccountItems.model().getRecordById(itemId)
        itemEditor = CAccountItemEditor(self,
                                        QtGui.qApp.db,
                                        eventCache=self.tblAccountItems.model().eventCache,
                                        visitCache=self.tblAccountItems.model().visitCache,
                                        actionCache=self.tblAccountItems.model().actionCache,
                                        serviceCache=self.tblAccountItems.model().serviceCache)
        itemEditor.setRecord(record)
        if itemEditor.exec_():
            itemId = forceRef(record.value(u'id'))
            self.tblAccountItems.model().recordCache().invalidate(keyList=[itemId])
            self.updateAccountInfo()


def getMesAmount(eventId, mesId):
    result = 0
    db = QtGui.qApp.db
    stmt = u'''
        SELECT
        mMV.groupCode  AS prvsGroup,
        mMV.averageQnt AS averageQnt,
        Visit.id       AS visit_id,
        IF(mMV.visitType_id=mVT.id, 0, 1) AS visitTypeErr
        FROM Visit
        LEFT JOIN Person ON Person.id  = Visit.person_id
        LEFT JOIN rbSpeciality ON rbSpeciality.id = Person.speciality_id
        LEFT JOIN rbVisitType  ON rbVisitType.id = Visit.visitType_id
        LEFT JOIN mes.mrbVisitType  AS mVT  ON rbVisitType.code = mVT.code
        LEFT JOIN mes.mrbSpeciality AS mS   ON mS.regionalCode = rbSpeciality.regionalCode
        LEFT JOIN mes.MES_visit     AS mMV  ON mMV.speciality_id = mS.id
        WHERE Visit.deleted = 0 AND Visit.event_id = %d AND mMV.master_id = %d AND mVT.code in ('Л','К')
        ORDER BY visitTypeErr, mMV.groupCode, Visit.date
    ''' % (eventId, mesId)

    query = db.query(stmt)
    groupAvailable = {}
    countedVisits = set()
    while query.next():
        record = query.record()
        visitId = forceRef(record.value('visit_id'))
        if visitId not in countedVisits:
            prvsGroup = forceInt(record.value('prvsGroup'))
            averageQnt = forceInt(record.value('averageQnt'))
            available = groupAvailable.get(prvsGroup, averageQnt)
            if available > 0:
                groupAvailable[prvsGroup] = available - 1
                result += 1
                countedVisits.add(visitId)
    return result


def getAccountItemsTotals(idList):  # , franchisePercent=0):
    count = len(idList)
    totalSum = forceDecimal(0.0)
    payedSum = forceDecimal(0.0)
    refusedSum = forceDecimal(0.0)

    if idList:
        db = QtGui.qApp.db
        table = db.table('Account_Item')
        stmt = u'''
        SELECT
            SUM(`sum`) AS `sum`,
            (`date` IS NOT NULL AND `number` != '') AS `confirmed`,
            (`refuseType_id` IS NOT NULL) AS `refused`
        FROM Account_Item
        WHERE %s
        GROUP BY `confirmed`, `refused`''' % table['id'].inlist(idList)
        query = db.query(stmt)
        while query.next():
            record = query.record()
            sum = forceDecimal(record.value('sum'))
            confirmed = forceBool(record.value('confirmed'))
            refused = forceBool(record.value('refused'))
            totalSum += sum  # (sum * (franchisePercent/100.0)) if franchisePercent else sum
            if confirmed:
                if refused:
                    refusedSum += sum
                else:
                    payedSum += sum
    return count, totalSum, payedSum, refusedSum
