# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Ui_ReportPayersSetup import Ui_ReportPayersSetupDialog
from library.Utils import forceDouble, forceInt, forceRef, forceString, forceStringEx


def formatDouble(dValue):
    return '%.2f' % dValue

def selectData(params):
    begDate                = params.get('begDate', None)
    endDate                = params.get('endDate', None)
    contractId             = params.get('contractId', None)
    financeId              = params.get('financeId', None)
    clientOrganisationId   = params.get('clientOrganisationId', None)
    insurerId              = params.get('insurerId', None)
    freeInputWork          = params.get('freeInputWork', False)
    freeInputWorkValue     = params.get('freeInputWorkValue', '')
    personSpec                 = params.get('specialityId', None)
    
    db = QtGui.qApp.db
    
    tableAccount      = db.table('Account')
    tableContract     = db.table('Contract')
    tableOrganisation = db.table('Organisation')
    tableAccountItem  = db.table('Account_Item')
    tableClientWork   = db.table('ClientWork')
    tablePerson     = db.table('Person')
    
    queryTable = tableAccount.innerJoin(tableContract, tableContract['id'].eq(tableAccount['contract_id']))
    queryTable = queryTable.innerJoin(tableOrganisation, tableOrganisation['id'].eq(tableAccount['payer_id']))
    
#    if clientOrganisationId:
#        queryTable = queryTable.leftJoin(tableAccountItem, tableAccountItem['master_id'].eq(tableAccount['id']))
    
    cond = [
        tableAccount['deleted'].eq(0)
    ]
    
    if begDate:
        cond.append(tableAccount['settleDate'].dateGe(begDate))
    if endDate:
        cond.append(tableAccount['settleDate'].dateLe(endDate))
    if contractId:
        cond.append(tableAccount['contract_id'].eq(contractId))
    if financeId:
        cond.append(tableContract['finance_id'].eq(financeId))
    if insurerId:
        cond.append(tableOrganisation['id'].eq(insurerId))
    
    if personSpec:
        persCond = [tableAccountItem['master_id'].eq(tableAccount['id'])]
        persCond.append(tablePerson['id'].eq(personSpec))
        cond.append(
                    """EXISTS(
                    SELECT Event.`execPerson_id`
                    FROM Event
                    LEFT JOIN Account_Item ON Account_Item.`event_id`=Event.`id` AND Account_Item.deleted = 0
                    LEFT JOIN Person ON Person.`id` = Event.`execPerson_id`
                    WHERE %s
                    )"""%db.joinAnd(persCond)
                    )

    if clientOrganisationId or(freeInputWork and freeInputWorkValue):
        workCond = [tableAccountItem['master_id'].eq(tableAccount['id'])]
        workSubCond = []
        if clientOrganisationId:
            workSubCond.append(tableClientWork['org_id'].eq(clientOrganisationId))
        if (freeInputWork and freeInputWorkValue):
            workSubCond.append(tableClientWork['freeInput'].like(freeInputWorkValue))
        workCond.append(db.joinOr(workSubCond))
        cond.append(
                    '''EXISTS(
                    SELECT Event.`client_id` 
                    FROM Event 
                    LEFT JOIN Account_Item ON Account_Item.`event_id`=Event.`id` AND Account_Item.deleted = 0
                    LEFT JOIN ClientWork ON ClientWork.`client_id`=Event.`client_id`
                    WHERE %s
                    )'''%db.joinAnd(workCond)
                   )
        
        
        
        
        
    cond = cond if cond else '1'
    
    fields = [tableOrganisation['id'].alias('payerId'), 
              tableOrganisation['shortName'].alias('payerName'), 
              tableContract['id'].alias('contractId'), 
              tableContract['finance_id'].alias('financeId'), 
              u'CONCAT_WS(\' \',Contract.`grouping`, Contract.`number`, DATE_FORMAT(Contract.`date`,\'%d:%m:%Y`\'), Contract.`resolution`) AS contractName',
              tableAccount['id'].alias('accountId'), 
              tableAccount['amount'].alias('accountServicesAmount'), 
              tableAccount['sum'].alias('accountSum'),
              u'CONCAT_WS(\' \', %s, \'от\', DATE_FORMAT(%s,\'%%d.%%m.%%Y`\')) AS %s' % (tableAccount['number'].name(),
                                                                                        tableAccount['settleDate'].name(),
                                                                                        'accountInfo'),
              u'Account.`sum`/Account.`amount` AS serviceMeanPrice',
              u'Account.`sum`/(SELECT COUNT(DISTINCT Event.`client_id`) FROM Account_Item INNER JOIN Event ON Event.`id`=Account_Item.`event_id` WHERE Account_Item.`master_id`=Account.`id`) AS clientMeanPrice']
              
    order = [tableContract['finance_id'].name(), 
             tableOrganisation['id'].name(), 
             tableAccount['settleDate'],
             tableContract['id']]
             
    stmt = db.selectStmt(queryTable, fields, cond,  order = order)
    return db.query(stmt)
    

class CReportPayers(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Сводный отчет по плательщикам')
        self._mapPayerIdToInfo = {}
        self._mapPayerIdToAttachedClientsCount = {}
        self._mapPayerAccountsClientsCount = {}
        self._mapFinanceIdToPayerId = {}
        self.resetHelpers()
        
    def resetHelpers(self):
        self._mapPayerIdToInfo.clear()
        self._mapPayerIdToAttachedClientsCount.clear()
        self._mapPayerAccountsClientsCount.clear()
        self._mapFinanceIdToPayerId.clear()
        
    def getSetupDialog(self, parent):
        result = CReportPayersSetup(parent, self)
        result.setTitle(self.title())
        return result
        
    def getDescription(self, params):
        begDate                = params.get('begDate', None)
        endDate                = params.get('endDate', None)
        contractText           = params.get('contractText', None)
        contractId             = params.get('contractId', None)
        financeText            = params.get('financeText', None)
        financeId              = params.get('financeId', None)
        personSpecText    = params.get('personSpecText', None)
        
        rows = []
        if begDate:
            rows.append(u'Начальная дата периода: %s'%forceString(begDate))
        if endDate:
            rows.append(u'Конечная дата периода: %s'%forceString(endDate))
        if financeId:
            rows.append(u'Тип финансирования: %s' % financeText)
        if contractId:
            rows.append(u'Контракт: %s' % contractText)
        if personSpecText:
            rows.append(u'Специальность врача: %s' % personSpecText)
            
        return rows
        
        
    def build(self, params):
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        self.structInfo(query, params)
        
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        
        detailContracts        = params.get('detailContracts', False)
        printPayerResult = params.get('printPayerResult', False)
        
        tableColumns = [
                        ('%15',
                        [u'Количество\nприкрепленных'], CReportBase.AlignRight),
                        ('%5',
                        [u'Количество\nпациентов в счете'], CReportBase.AlignRight),
                        ('%6',
                        [u'Количество\nуслуг'], CReportBase.AlignRight), 
                        ('%6', 
                        [u'Сумма счетов'], CReportBase.AlignRight),  
                        ('%6',
                        [u'Ср.цена\nобращения'], CReportBase.AlignRight), 
                        ('%6',
                        [u'Ср.цена\nуслуги'], CReportBase.AlignRight)
                       ]
        
        tableColumns.insert(0, ('%15', [u'Счет'], CReportBase.AlignLeft))
        

        if printPayerResult:
            tableColumns.insert(0, ('%2', [u'№'], CReportBase.AlignLeft))
        else:
            tableColumns.insert(0, ('%15', [u'Плательщик'], CReportBase.AlignLeft))

        
        table = createTable(cursor, tableColumns)

        boldChars = QtGui.QTextCharFormat()
        boldChars.setFontWeight(QtGui.QFont.Bold)
        
        detailFinance =  not bool(params.get('financeId', None))
        
        numShift = 0
        if detailFinance:
            totalResult = [0, 0, 0, 0, 0]
            for financeId, payerIdList in self._mapFinanceIdToPayerId.items():
                financeName = forceString(QtGui.qApp.db.translate('rbFinance', 'id', financeId, 'name'))
                self.printHeader(table, financeName, boldChars)
                numShift += 1
                result = self.printContractList(payerIdList, table, numShift, boldChars, printPayerResult, detailContracts)
                if printPayerResult:
                    payerCount = len(payerIdList)
                    numShift += 2*payerCount if payerCount > 1 else 0
                    self.printResult(table, result, boldChars)
                    
                for idx in range(len(totalResult)):
                    totalResult[idx] += result[idx]
                
            self.printResult(table, totalResult, boldChars)
            numShift += 1
                
        else:
            result = self.printContractList(self._mapPayerIdToInfo.keys(), table, numShift, boldChars, printPayerResult, detailContracts)
            self.printResult(table, result, boldChars)
            numShift += 1
        
        return doc
        
    def printContractList(self, payerIdList, table, numShift, boldChars, printPayerResult, detailContracts = False):
        def div(value, divider):
            return value/divider if divider else value
        resultAccountSum = 0
        resultAccountsClientsCount = 0
        resultAccountServicesAmount = 0
        for payerId in payerIdList:
            tmpResultAccountSum = 0
            tmpResultAccountsClientsCount = 0
            tmpResultAccountServicesAmount = 0
            payerInfo = self._mapPayerIdToInfo[payerId]
            if printPayerResult:
                self.printHeader(table, payerInfo['payerName'], boldChars, depth=1)
                numShift += 1
            
            contractInfoList = payerInfo['contractInfoList']
            if detailContracts:
                contractInfoList.sort(key=lambda item: item['contractName']) 
            prevContractName = None
            for contractInfo in contractInfoList:
                contractName = contractInfo['contractName']
                if contractName and contractName != prevContractName:
                    self.printHeader(table, contractName, boldChars, depth=2)
                    numShift += 1
                i = table.addRow()
                
                tmpResultAccountsClientsCount += contractInfo['accountsClientsCount']
                tmpResultAccountServicesAmount += contractInfo['accountServicesAmount']
                tmpResultAccountSum += contractInfo['accountSum']
  
                if printPayerResult:
                    table.setText(i, 0, i-numShift) 
                else:
                    table.setText(i, 0, payerInfo['payerName'])
                
                table.setText(i, 1, contractInfo['accountInfo'])
                table.setText(i, 2, contractInfo['attachedClientsCount']) 
                table.setText(i, 3, contractInfo['accountsClientsCount']) 
                table.setText(i, 4, contractInfo['accountServicesAmount']) 
                table.setText(i, 5, contractInfo['accountSum']) 
                table.setText(i, 6, formatDouble(contractInfo['clientMeanPrice'])) 
                table.setText(i, 7, formatDouble(contractInfo['serviceMeanPrice']))
                prevContractName = contractName
                
            tmpResult = [tmpResultAccountsClientsCount, 
                         tmpResultAccountServicesAmount, 
                         tmpResultAccountSum, 
                         div(tmpResultAccountSum, tmpResultAccountsClientsCount), 
                         div(tmpResultAccountSum, tmpResultAccountServicesAmount)]
            
            if printPayerResult:
                self.printResult(table, tmpResult, boldChars)
                numShift += 1
            
            resultAccountsClientsCount += tmpResultAccountsClientsCount
            resultAccountServicesAmount += tmpResultAccountServicesAmount
            resultAccountSum += tmpResultAccountSum
                
        return [resultAccountsClientsCount, 
                resultAccountServicesAmount, 
                resultAccountSum, 
                div(resultAccountSum, resultAccountsClientsCount), 
                div(resultAccountSum, resultAccountServicesAmount)]

    
    def printHeader(self, table, value, boldChars, depth=0):
        i = table.addRow()
        table.setText(i, 0, (u' '*4*depth)+value, charFormat=boldChars)
        table.mergeCells(i, 0, 1, table.table.columns())
        
        
    def printResult(self, table, result, boldChars):
        i = table.addRow()
        totalStartIdx = table.table.columns() - 5
        for idx, value in enumerate(result):
            if idx in [3, 4]:
                value = formatDouble(value)
            table.setText(i, idx + totalStartIdx, value, charFormat=boldChars)
        table.mergeCells(i, 0, 1, totalStartIdx)
    
    
    def structInfo(self, query, params):
        financeId              = params.get('financeId', None)
        detailContracts        = params.get('detailContracts', False)
        
        detailFinance = not bool(financeId)
        
        self.resetHelpers()
        
        while query.next():
            record = query.record()
            
            payerId = forceRef(record.value('payerId'))
            payerName = forceString(record.value('payerName'))
            financeId = forceRef(record.value('financeId'))
            contractName = forceString(record.value('contractName')) if detailContracts else None
            accountId = forceRef(record.value('accountId'))
            accountServicesAmount = forceInt(record.value('accountServicesAmount'))
            accountSum = forceDouble(record.value('accountSum'))
            accountInfo = forceString(record.value('accountInfo'))
            serviceMeanPrice = forceDouble(record.value('serviceMeanPrice'))
            clientMeanPrice = forceDouble(record.value('clientMeanPrice'))
        
            if detailFinance:
                payerIdList = self._mapFinanceIdToPayerId.setdefault(financeId, [payerId])
                if not payerId in payerIdList:
                    payerIdList.append(payerId)
        
            payerInfo = self._mapPayerIdToInfo.setdefault(payerId, {'payerName':payerName, 'contractInfoList':[]})
            contractInfoList = payerInfo.setdefault('contractInfoList', [])
            contractInfo = {}
            contractInfo['contractName'] = contractName
            contractInfo['payerName'] = payerName
            contractInfo['attachedClientsCount'] = self.getAttachedClientsCount(payerId)
            contractInfo['accountsClientsCount'] = self.getAccountsClientsCount(payerId, accountId)
            contractInfo['accountServicesAmount'] = accountServicesAmount
            contractInfo['accountSum'] = accountSum
            contractInfo['accountInfo'] = accountInfo
            contractInfo['serviceMeanPrice'] = serviceMeanPrice
            contractInfo['clientMeanPrice'] = clientMeanPrice
            contractInfoList.append(contractInfo)
        
        
        
    def getAttachedClientsCount(self, payerId):
        result = self._mapPayerIdToAttachedClientsCount.get(payerId, None)
        if result is None:
            db = QtGui.qApp.db
            tableClientPolicy = db.table('ClientPolicy')
            tableContract = db.table('Contract')
            tableAccount = db.table('Account')
            tableFinance = db.table('rbFinance')
            tablePolicuType = db.table('rbPolicyType')
            
            queryTable = tableClientPolicy
            queryTable = queryTable.leftJoin(tableAccount,    tableAccount['payer_id'].eq(tableClientPolicy['insurer_id']))
            queryTable = queryTable.leftJoin(tableContract,   tableContract['id'].eq(tableAccount['contract_id']))
            queryTable = queryTable.leftJoin(tableFinance,    tableFinance['id'].eq(tableContract['finance_id']))
            queryTable = queryTable.leftJoin(tablePolicuType, tablePolicuType['id'].eq(tableClientPolicy['policyType_id']))
            
            cond = [
                tableClientPolicy['insurer_id'].eq(payerId),
                tableAccount['exposeDate'].dateBetween(tableClientPolicy['begDate'], tableClientPolicy['endDate']),
                'IF(rbFinance.`code` = \'2\', rbPolicyType.`code` IN (\'1\',\'2\'), IF(rbFinance.`code` = \'3\', rbPolicyType.`code` IN (\'3\'), 0))',
                tableAccount['deleted'].eq(0)
            ]
            
            result = db.getDistinctCount(queryTable, tableClientPolicy['client_id'].name(), cond)
            self._mapPayerIdToAttachedClientsCount[payerId] = result
        return result
        
        
    def getAccountsClientsCount(self, payerId, accountId):
        result = self._mapPayerAccountsClientsCount.get((payerId, accountId), None)
        if result is None:
            db = QtGui.qApp.db
            tableAccountItem = db.table('Account_Item')
            tableEvent = db.table('Event')
            tableAccount = db.table('Account')
            queryTable = tableAccountItem.innerJoin(tableEvent, tableEvent['id'].eq(tableAccountItem['event_id']))
            queryTable = queryTable.innerJoin(tableAccount, tableAccount['id'].eq(tableAccountItem['master_id']))
            result = db.getDistinctCount(
                queryTable,
                tableEvent['client_id'].name(),
                [
                    tableAccount['payer_id'].eq(payerId),
                    tableAccount['id'].eq(accountId),
                    tableAccount['deleted'].eq(0),
                    tableAccountItem['deleted'].eq(0),
                ]
            )
            self._mapPayerAccountsClientsCount[(payerId, accountId)] = result
        return result
        
        
class CReportPayersSetup(QtGui.QDialog, Ui_ReportPayersSetupDialog):
    def __init__(self, parent, report):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self._report = report
        self.cmbFinance.setTable('rbFinance', addNone=True)
        self.cmbSpeciality.setTable('rbSpeciality', True)
        
        
    def setTitle(self, title):
        self.setWindowTitle(title)
        
        
    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbContract.setValue(params.get('contractId', None))
        self.cmbFinance.setValue(params.get('financeId', None))
        self.chkDetailContracts.setChecked(params.get('detailContracts', False))
        self.chkPrintPayerResult.setChecked(params.get('printPayerResult', False))
        self.cmbClientOrganisation.setValue(params.get('clientOrganisationId', None))
        self.cmbSpeciality.setValue(params.get('specialityId', None))
        self.cmbInsurer.setValue(params.get('insurerId'))
        self.chkFreeInputWork.setChecked(params.get('freeInputWork', False))
        self.edtFreeInputWork.setText(params.get('freeInputWorkValue', ''))
    
    
    def params(self):
        params = {}
        
        params['contractId'] = self.cmbContract.value()
        params['contractText'] = forceString(self.cmbContract.currentText())
        params['financeId']  = self.cmbFinance.value()
        params['financeText'] = self.cmbFinance.currentText()
        
        params['begDate'] = self.edtBegDate.date()
        params['endDate'] = self.edtEndDate.date()
        
        params['detailContracts']  = self.chkDetailContracts.isChecked()
        params['printPayerResult'] = self.chkPrintPayerResult.isChecked()
        
        params['clientOrganisationId'] = self.cmbClientOrganisation.value()
        params['insurerId'] = self.cmbInsurer.value()
        params['specialityId'] = self.cmbSpeciality.value()
        params['personSpecText'] = self.cmbSpeciality.currentText()
        
        params['freeInputWork'] = self.chkFreeInputWork.isChecked()
        params['freeInputWorkValue'] = forceStringEx(self.edtFreeInputWork.text())
        

        return params
        
        
    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.cmbContract.setBegDate(date)
        
        
    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtEndDate_dateChanged(self, date):
        self.cmbContract.setEndDate(date)
        
        
    @QtCore.pyqtSlot(int)
    def on_cmbFinance_currentChanged(self, index):
        financeId = self.cmbFinance.value()
        self.cmbContract.setFinanceId(financeId)
        
        
    @QtCore.pyqtSlot(int)
    def on_cmbContract_currentChanged(self, index):
        contractId = self.cmbContract.value()
        self.chkDetailContracts.setEnabled(bool(contractId))
        
        
        
