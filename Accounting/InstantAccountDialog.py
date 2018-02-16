# -*- coding: utf-8 -*-

u"""Расчёты: создание счета по событию"""
from collections import defaultdict
from PyQt4 import QtCore, QtGui

from Accounting.AccountBuilder import CAccountBuilder, CAccountPool
from Accounting.AccountEditDialog import CAccountEditDialog
from Accounting.AccountInfo import CAccountInfo
from Accounting.AccountingDialog import accountantRightList, getAccountItemsTotals
from Accounting.Utils import CAccountItemsModel, CAccountsModel, clearPayStatus, editPayment, getContractInfo, getFranchisePercentByEvent, registerCheckInECR, setPayment, updateAccount
from Events.Action import ActionClass
from Events.EventInfo import CEventInfo
from Events.TempInvalidInfo import CTempInvalidInfo
from Events.Utils import getEventContext, getExternalIdAsAccountNumber
from Ui_InstantAccountDialog import Ui_InstantAccountDialog
from Users.Rights import urAccessEditPayment
from library.DialogBase import CDialogBase
from library.PrintInfo import CInfoContext
from library.PrintTemplates import additionalCustomizePrintButton, applyTemplate, getPrintAction, getPrintButton
from library.Utils import forceDate, forceDecimal, forceInt, forceRef, forceString, formatNum1, toVariant


# Выставление всех действий за период, указанный в умолчаниях. Группируются по типу события и клиенту.
def createInstantAccountForPeriod(eventId, eventTypeId, clientId):
    """Выставление всех действий за период, указанный в умолчаниях.

    @param eventId: id основного события, по которому будут определены контексты печати при показе результата выставления счетов.
    @param eventTypeId: тип событий, из которых будут выставлены действия.
    @param clientId: идентификатор клиента, чьи мероприятия попадут в счета.
    @raise:
    """
    db = QtGui.qApp.db
    tableAction = db.table('Action')
    tableActionType = db.table('ActionType')
    tableEvent = db.table('Event')
    tableContract = db.table('Contract')
    tableFinance = db.table('rbFinance')
    tableResult = db.table('rbResult')

    table = tableAction
    table = table.leftJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
    table = table.leftJoin(tableEvent, db.joinAnd([tableEvent['id'].eq(tableAction['event_id']), tableEvent['eventType_id'].eq(eventTypeId)]))
    table = table.leftJoin(tableContract, 'Contract.id = IF(Action.contract_id IS NULL, Event.contract_id, Action.contract_id)')
    table = table.leftJoin(tableFinance, tableFinance['id'].eq(tableContract['finance_id']))
    table = table.leftJoin(tableResult, tableResult['id'].eq(tableEvent['result_id']))
    cond = [
        tableAction['deleted'].eq(0),
        '(Action.payStatus & (3 << 2 * CAST(%s AS UNSIGNED ))) = 0' % tableFinance['code'].name(), #getPayStatusMaskByCode(CFinanceType.cash)
        db.joinOr([tableResult['notAccount'].eq(0), tableResult['notAccount'].isNull()]),
        tableEvent['client_id'].eq(clientId),
        'Action.createDatetime > \'%s\'' % forceString(QtCore.QDateTime.currentDateTime().addSecs(-(period*3600)).toString("yyyy-MM-dd hh:mm:ss")),
        db.joinOr([tableActionType['class'].ne(ActionClass.Analyses),
                   tableAction['parent_id'].isNotNull()])  # только дочерние дествия со вкладки "Анализы"
    ]

    mapContractIdToActionIdList = defaultdict(list)
    for record in db.iterRecordList(table, [tableContract['id'].alias('contract_id'),
                                            tableAction['id'].alias('action_id')], cond):
        contractId = forceRef(record.value('contract_id'))
        actionId = forceRef(record.value('action_id'))
        mapContractIdToActionIdList[contractId].append(actionId)

    accountIdList = []
    try:
        today = QtCore.QDate.currentDate()
        db.transaction()
        for contractId in sorted(mapContractIdToActionIdList.keys()):
            builder = CAccountBuilder()
            contractInfo = getContractInfo(contractId)
            accountPool = CAccountPool(contractInfo,
                                       QtGui.qApp.currentOrgId(),
                                       QtGui.qApp.currentOrgStructureId(),
                                       today,
                                       False)
            actionIdList = sorted(mapContractIdToActionIdList[contractId])
            builder.exposeByActions(None, contractInfo, accountPool.getAccount, actionIdList, today)
            accountPool.updateDetails()
            accountIdList += accountPool.getAccountIdList()
        db.commit()
    except:
        db.rollback()
        raise

    if accountIdList:
        dialog = CInstantAccountDialog(QtGui.qApp.mainWindow, eventId)
        dialog.setAccountIdList(accountIdList)
        dialog.exec_()
    else:
        QtGui.QMessageBox.information( QtGui.qApp.mainWindow,
                                u'Создание счёта по событию',
                                u'Счёт не создан, так как нечего выставлять.',
                                 QtGui.QMessageBox.Ok,
                                 QtGui.QMessageBox.Ok)

def createInstantAccount(eventId):
    """Создание счёта по всем действиям события.

    @param eventId: идентификатор события, которое будет выставлено в счета.
    """
    db = QtGui.qApp.db
    tableAction = db.table('Action')
    tableActionType = db.table('ActionType')
    tableEvent = db.table('Event')
    tableContract = db.table('Contract')
    tableFinance = db.table('rbFinance')
    tableResult = db.table('rbResult')
    tablePaymentScheme = db.table('PaymentScheme')
    tablePaymentSchemeItem = db.table('PaymentSchemeItem')

    remainSum = None
    depositTable = tableContract.innerJoin(tableEvent, db.joinAnd([tableEvent['contract_id'].eq(tableContract['id']), tableEvent['id'].eq(eventId)]))
    depositRecord = db.getRecordEx(depositTable, 'Contract.deposit, Contract.id as contract_id, Contract.number as contract_number, Event.externalId, Event.eventType_id')
    deposit = forceDecimal(depositRecord.value('deposit'))
    eventContractId = forceRef(depositRecord.value('contract_id'))
    eventContractNumber = forceRef(depositRecord.value('contract_number'))
    eventExternalId = forceString(depositRecord.value('externalId'))
    eventTypeId = forceRef(depositRecord.value('eventType_id'))

    if deposit > 0:
        sumUsedRecord = db.getRecordEx('Account', 'SUM(Account.sum) as totalSum', 'Account.deleted = 0 AND Account.contract_id = %s' % eventContractId)
        sumUsed = forceDecimal(sumUsedRecord.value('totalSum'))
        remainSum = deposit - sumUsed
        if remainSum <= 0:
            QtGui.QMessageBox.critical(None,
                                    u'Внимание!',
                                    u'Выставление счета невозможно, так как сумма депозита по договору %s исчерпана.' % eventContractNumber,
                                    QtGui.QMessageBox.Ok,
                                    QtGui.QMessageBox.Ok
                                    )
            return

    table = tableAction
    table = table.leftJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
    table = table.leftJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
    table = table.leftJoin(tableContract, 'Contract.id = IF(Action.contract_id IS NULL, Event.contract_id, Action.contract_id)')
    table = table.leftJoin(tableFinance, tableFinance['id'].eq(tableContract['finance_id']))
    table = table.leftJoin(tableResult, tableResult['id'].eq(tableEvent['result_id']))
    cond = [
        tableAction['deleted'].eq(0),
        tableAction['event_id'].eq(eventId),
        '(Action.payStatus & (3 << 2 * CAST(%s AS UNSIGNED ))) = 0' % tableFinance['code'].name(), #getPayStatusMaskByCode(CFinanceType.cash)
        db.joinOr([tableResult['notAccount'].eq(0),
                   tableResult['notAccount'].isNull()]),
        db.joinOr([tableActionType['class'].ne(ActionClass.Analyses),
                   tableAction['parent_id'].isNotNull()])  # только дочерние дествия со вкладки "Анализы"
    ]

    mapContractIdToActionIdList = defaultdict(list)
    for record in db.iterRecordList(table, [tableContract['id'].alias('contract_id'),
                                            tableAction['id'].alias('action_id')], cond):
        contractId = forceRef(record.value('contract_id'))
        actionId = forceRef(record.value('action_id'))
        mapContractIdToActionIdList[contractId].append(actionId)

    accountIdList = []
    try:
        today = QtCore.QDate.currentDate()

        franchisPercent = getFranchisePercentByEvent(eventId)

        db.transaction()
        for contractId in sorted(mapContractIdToActionIdList.keys()):
            builder = CAccountBuilder()
            contractInfo = getContractInfo(contractId)
            accountPool = CAccountPool(contractInfo,
                                       QtGui.qApp.currentOrgId(),
                                       QtGui.qApp.currentOrgStructureId(),
                                       today,
                                       False)
            actionIdList = sorted(mapContractIdToActionIdList[contractId])

            builder.exposeByActions(None, contractInfo, accountPool.getAccount, actionIdList, today, franchisePercent=franchisPercent)
            accountPool.updateDetails()
            if getExternalIdAsAccountNumber(eventTypeId):
                for details in accountPool.getDetailsList():
                    details.changeNumber(eventExternalId, step=True, fromZero=True)
            if contractId == eventContractId and remainSum != None:
                exposedSum = 0
                for details in accountPool.getDetailsList():
                    exposedSum += (details.totalSum * (franchisPercent/100.0)) if franchisPercent else details.totalSum

                paySchemeId = forceInt(
                    db.translate(tablePaymentSchemeItem, tablePaymentSchemeItem['contract_id'], contractId,
                                 tablePaymentSchemeItem['paymentScheme_id']))
                if paySchemeId:
                    recPayScheme = db.getRecordEx(tablePaymentScheme, '*', tablePaymentScheme['id'].eq(paySchemeId))
                    remainSumPayScheme = forceDecimal(recPayScheme.value('total')) - forceDecimal(recPayScheme.value('spent'))
                    if exposedSum > remainSumPayScheme:
                        QtGui.QMessageBox.critical(None,
                                                   u'Внимание!',
                                                   u'Выставление счета невозможно, так как выставляемая сумма превышает сумму схемы оплаты %s.' % forceString(recPayScheme.value('numberProtocol')),
                                                   QtGui.QMessageBox.Ok,
                                                   QtGui.QMessageBox.Ok)
                        db.rollback()
                        return
                    else:
                        recPayScheme.setValue('spent', toVariant(forceDecimal(recPayScheme.value('spent')) + forceDecimal(exposedSum)))
                        db.updateRecord(tablePaymentScheme, recPayScheme)
                if exposedSum > remainSum:
                    QtGui.QMessageBox.critical(None,
                                u'Внимание!',
                                u'Выставление счета невозможно, так как выставляемая сумма превышает сумму депозита по договору %s.' % eventContractNumber,
                                QtGui.QMessageBox.Ok,
                                QtGui.QMessageBox.Ok)
                    db.rollback()
                    return
                if contractInfo.endDate:
                    if forceDate(contractInfo.endDate) > QtCore.QDate.currentDate():
                        QtGui.QMessageBox.critical(None,
                                                   u'Внимание!',
                                                   u'Выставление счета невозможно, так как срок действия договора %s истек.' % eventContractNumber,
                                                   QtGui.QMessageBox.Ok,
                                                   QtGui.QMessageBox.Ok)
                    db.rollback()
                    return
            accountIdList += accountPool.getAccountIdList()
        db.commit()
    except:
        db.rollback()
        raise

    if accountIdList:
        dialog = CInstantAccountDialog(QtGui.qApp.mainWindow, eventId)
        dialog.setAccountIdList(accountIdList)
        dialog.exec_()
    else:
        QtGui.QMessageBox.information( QtGui.qApp.mainWindow,
                                u'Создание счёта по событию',
                                u'Счёт не создан, так как нечего выставлять.',
                                 QtGui.QMessageBox.Ok,
                                 QtGui.QMessageBox.Ok)


class CInstantAccountDialog(CDialogBase, Ui_InstantAccountDialog):
    u"""Использует контекст печати eventAccount, унаследованный от соответствующего event'а и, вдобавок, содержащий переменную 'account' и PrintAction контекста 'account'"""
    def __init__(self, parent, eventId):
        CDialogBase.__init__(self, parent)
        
        self.currentAccountId = None
        
        self.setEventId(eventId)

        self.addModels('Accounts', CAccountsModel(self))
        self.addModels('AccountItems', CAccountItemsModel(self))

        self.setupAccountsMenu()
        self.setupAccountItemsMenu()
        self.setupBtnPrintMenu()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.buttonBox.addButton(self.btnPrint, QtGui.QDialogButtonBox.ActionRole)

        self.tblAccounts.setModel(self.modelAccounts)
        self.tblAccounts.setSelectionModel(self.selectionModelAccounts)
        self.tblAccounts.setPopupMenu(self.mnuAccounts)
        self.tblAccountItems.setModel(self.modelAccountItems)
        self.tblAccountItems.setSelectionModel(self.selectionModelAccountItems)
        self.tblAccountItems.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tblAccountItems.setPopupMenu(self.mnuAccountItems)
        
        self.payParams = {}

        self.franchisePercent = getFranchisePercentByEvent(eventId)

    def setupAccountsMenu(self):
        self.mnuAccounts = QtGui.QMenu(self)
        self.mnuAccounts.setObjectName('mnuAccounts')
        self.actEditAccount = QtGui.QAction(u'Изменить счёт', self)
        self.actEditAccount.setObjectName('actEditAccount')
        self.actPrintAccount = getPrintAction(self, 'account', u'Печать')
        self.actPrintAccount.setObjectName('actPrintAccount')
        self.actDeleteAccount = QtGui.QAction(u'Удалить счёт', self)
        self.actDeleteAccount.setObjectName('actDeleteAccount')
        self.mnuAccounts.addAction(self.actEditAccount)
        self.mnuAccounts.addAction(self.actPrintAccount)
        self.mnuAccounts.addSeparator()
        self.mnuAccounts.addAction(self.actDeleteAccount)

    def setupAccountItemsMenu(self):
        self.mnuAccountItems = QtGui.QMenu(self)
        self.mnuAccountItems.setObjectName('mnuAccountItems')
        self.actSetPayment = QtGui.QAction(u'Подтверждение оплаты', self)
        self.actSetPayment.setObjectName('actSetPayment')
        self.actEditPayment = QtGui.QAction(u'Изменение подтверждения оплаты', self)
        self.actEditPayment.setObjectName('actEditPayment')
        self.actSelectAll = QtGui.QAction(u'Выбрать все', self)
        self.actSelectAll.setObjectName('actSelectAll')
        self.actDeleteAccountItems = QtGui.QAction(u'Удалить', self)
        self.actDeleteAccountItems.setObjectName('actDeleteAccountItems')
        self.mnuAccountItems.addAction(self.actSetPayment)
        self.mnuAccountItems.addAction(self.actEditPayment)
        self.mnuAccountItems.addSeparator()
        self.mnuAccountItems.addAction(self.actSelectAll)
        self.mnuAccountItems.addSeparator()
        self.mnuAccountItems.addAction(self.actPrintAccount)
        self.mnuAccountItems.addSeparator()
        self.mnuAccountItems.addAction(self.actDeleteAccountItems)

    def setupBtnPrintMenu(self):
        self.btnPrint = getPrintButton(self, 'account', u'Печать')
        self.btnPrint.setObjectName('btnPrint')
        eventTypeId = QtGui.qApp.db.getRecord('Event', 'eventType_id', self.eventId).value(0)
        context = getEventContext(eventTypeId)
        additionalCustomizePrintButton(self, self.btnPrint, context)
        self.btnPrint.setShortcut('F6')

    def setAccountIdList(self, accountIdList):
        self.tblAccounts.setIdList(accountIdList)
        
    def setEventId(self, eventId):
        self.eventId = eventId

    def editCurrentAccount(self):
        dialog = CAccountEditDialog(self)
        id = self.tblAccounts.currentItemId()
        if id:
            dialog.load(id)
            if dialog.exec_():
                self.modelAccounts.invalidateRecordsCache()
                self.modelAccounts.reset()

    def printCurrentAccount(self, templateId):
        context = CInfoContext()
        accountInfo = context.getInstance(CAccountInfo, self.currentAccountId)
        accountInfo.selectedItemIdList = self.modelAccountItems.idList()
        eventInfo = context.getInstance(CEventInfo, self.eventId)
        clientInfo = eventInfo.client
        tempInvalidInfo = context.getInstance(CTempInvalidInfo, None)
        data = { 'account' : accountInfo,
                 'event': eventInfo, 
                 'client': clientInfo, 
                 'tempInvalid': tempInvalidInfo
               }
        applyTemplate(self, templateId, data)

    def updateAccounts(self):
        accountId = self.currentAccountId
        self.modelAccounts.invalidateRecordsCache()
        self.modelAccounts.reset()
        self.tblAccounts.setCurrentItemId(accountId)
        self.btnECashRegister.setEnabled(bool(self.currentAccountId) and QtGui.qApp.userHasRight(urAccessEditPayment) and QtGui.qApp.userHasAnyRight(accountantRightList))

    def updateAccountInfo(self):
        db = QtGui.qApp.db
        table = db.table('Account_Item')
        idList = db.getIdList(table, 'id', table['master_id'].eq(self.currentAccountId), 'id')
        currentAccountItemId = self.tblAccountItems.currentItemId()
        self.modelAccountItems.setIdList(idList)
        self.tblAccountItems.setCurrentItemId(currentAccountItemId)
        self.updateAccountItemsPanel(idList)

    def updateAccountItemsPanel(self, idList):
        count, totalSum, payedSum, refusedSum = getAccountItemsTotals(idList)  # , franchisePercent=self.franchisePercent)
        locale = QtCore.QLocale()
        if self.franchisePercent:
            totalSum = totalSum * (self.franchisePercent / 100.0)
        self.edtAccountItemsCount.setText(locale.toString(count))
        self.edtAccountItemsSum.setText(locale.toString(float(totalSum), 'f', 2))
        self.edtAccountItemsPayed.setText(locale.toString(float(payedSum), 'f', 2))
        self.edtAccountItemsRefused.setText(locale.toString(float(refusedSum), 'f', 2))

    @QtCore.pyqtSlot()
    def on_btnECashRegister_clicked(self):
        registerCheckInECR(self, self.franchisePercent)
        currentAccountItemId = self.tblAccountItems.currentItemId()
        self.modelAccountItems.invalidateRecordsCache()
        self.tblAccountItems.setCurrentItemId(currentAccountItemId)
    
    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblAccounts_doubleClicked(self, index):
        self.editCurrentAccount()

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelAccounts_currentRowChanged(self, current, previous):
        self.currentAccountId = self.tblAccounts.itemId(current)
        self.updateAccountInfo()

    @QtCore.pyqtSlot()
    def on_mnuAccounts_aboutToShow(self):
        currentRow = self.tblAccounts.currentIndex().row()
        itemPresent = currentRow>=0
        self.actEditAccount.setEnabled(itemPresent)
        self.actPrintAccount.setEnabled(itemPresent)
        self.actDeleteAccount.setEnabled(itemPresent)

    @QtCore.pyqtSlot()
    def on_actEditAccount_triggered(self):
        self.editCurrentAccount()

    @QtCore.pyqtSlot(int)
    def on_actPrintAccount_printByTemplate(self, templateId):
        self.printCurrentAccount(templateId)

    @QtCore.pyqtSlot()
    def on_mnuAccountItems_aboutToShow(self):
        currentRow = self.tblAccountItems.currentIndex().row()
        itemPresent = currentRow>=0
        self.actSetPayment.setEnabled(itemPresent and QtGui.qApp.userHasRight(urAccessEditPayment))
        self.actEditPayment.setEnabled(itemPresent and QtGui.qApp.userHasRight(urAccessEditPayment))
        self.actSelectAll.setEnabled(self.currentAccountId is not None)
        self.actPrintAccount.setEnabled(itemPresent)
        self.actDeleteAccountItems.setEnabled(itemPresent)

    @QtCore.pyqtSlot()
    def on_actSetPayment_triggered(self):
        if setPayment(self, self.currentAccountId, self.tblAccountItems.selectedItemIdList(), self.payParams):            
            currentAccountItemId = self.tblAccountItems.currentItemId()
            self.modelAccountItems.invalidateRecordsCache()
            self.tblAccountItems.setCurrentItemId(currentAccountItemId)
            self.updateAccounts()

    @QtCore.pyqtSlot()
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
                self.modelAccountItems.invalidateRecordsCache()
                self.tblAccountItems.setCurrentItemId(currentAccountItemId)
                self.updateAccounts()

    @QtCore.pyqtSlot()
    def on_actSelectAll_triggered(self):
        self.tblAccountItems.selectAll()

    @QtCore.pyqtSlot()
    def on_actDeleteAccount_triggered(self):
        self.tblAccounts.removeSelectedRows()
        self.updateAccountItemsPanel(self.modelAccounts.idList())

    @QtCore.pyqtSlot()
    def on_actDeleteAccountItems_triggered(self):
        db = QtGui.qApp.db
        table = db.table('Account_Item')
        selectedItemIdList = self.tblAccountItems.selectedItemIdList()
        cond=[table['id'].inlist(selectedItemIdList), table['date'].isNotNull(), table['number'].ne('')]
        itemIdList = db.getIdList(table, where=cond)
        if itemIdList:
            QtGui.QMessageBox.critical( self,
                                       u'Внимание!',
                                       u'Подтверждённые записи реестра не подлежат удалению',
                                       QtGui.QMessageBox.Close)
        else:
            n = len(selectedItemIdList)
            message = u'Вы действительно хотите удалить %s реестра? ' % formatNum1(n, (u'запись', u'записи', u'записей'))
            if QtGui.QMessageBox.question( self,
                                       u'Внимание!',
                                       message,
                                       QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
                                       QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:

                QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                try:
                    db.transaction()
                    try:
                        clearPayStatus(self.currentAccountId, selectedItemIdList)
                        db.deleteRecord(table, table['id'].inlist(selectedItemIdList))
                        updateAccount(self.currentAccountId)
                        db.commit()
                    except:
                        db.rollback()
                        QtGui.qApp.logCurrentException()
                        raise
                    self.updateAccounts()
                finally:
                    QtGui.QApplication.restoreOverrideCursor()

    @QtCore.pyqtSlot(int)
    def on_btnPrint_printByTemplate(self, templateId):
        self.printCurrentAccount(templateId)
