# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 - 2014 Vista Software. All rights reserved.
##
#############################################################################

from Reports.Report      import CReport
from Reports.ReportBase  import *
from library.Utils       import *
from Orgs.Utils          import getOrgStructureDescendants

def selectData(params):
    db = QtGui.qApp.db
    begDate = forceDate(params.get('begDate'))
    endDate = forceDate(params.get('endDate'))
    contractIdList = forceString(params.get('contractIdList'))
    financeId = forceInt(params.get('typeFinanceId'))
    eventTypeId = forceInt(params.get('eventTypeId'))

    where = ''
    join = ''
    if begDate:
        where += u"AND DATE(Account.createDatetime) >= DATE('%s') " % begDate.toString('yyyy-MM-dd')
    if endDate:
        where += u"AND DATE(Account.createDatetime) <= DATE('%s') " % endDate.toString('yyyy-MM-dd')
    if contractIdList:
        contractIdList = contractIdList.replace('[', '(')
        contractIdList = contractIdList.replace(']', ')')
        where += u'AND Contract.id IN %s ' % contractIdList
    if financeId:
        where += u'AND Contract.finance_id = %s ' % financeId
    if eventTypeId:
        join += u"INNER JOIN Event ON Event.contract_id = Contract.id AND Event.deleted = 0 AND Event.eventType_id = %s \n" % eventTypeId
    if params.get('orgStructureId', None):
        orgStruct = forceString(getOrgStructureDescendants(params['orgStructureId']))
        orgStruct = orgStruct.replace('[', '(')
        orgStruct = orgStruct.replace(']', ')')
        join += u'''
            INNER JOIN Action ON Action.contract_id = Contract.id
                AND Action.deleted = 0
            INNER JOIN Person ON Person.id = Action.person_id
                AND Person.deleted = 0
                AND Person.orgStructure_id IN %s
        ''' % orgStruct

    stmt = u'''
        SELECT Contract.number,
            Contract.resolution,
            Account.settleDate,
            Account_Item.amount,
            Account_Item.sum
        FROM Contract
        INNER JOIN Contract_Tariff ON Contract_Tariff.master_id = Contract.id
            AND Contract_Tariff.deleted = 0
        INNER JOIN Account_Item ON Account_Item.tariff_id = Contract_Tariff.id
            AND Account_Item.deleted = 0
        INNER JOIN Account ON Account.id = Account_Item.master_id
            AND Account.deleted = 0
        %(join)s
        WHERE Contract.deleted = 0 %(where)s
        ORDER BY Contract.number, Account.settleDate
    ''' % {'join' : join,
           'where' : where}
    return db.query(stmt)


class CReportRegisterContracts(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Реестр договоров по месяцам')

    def getSetupDialog(self, parent):
        result = CReportRegisterContractsSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(CReportBase.AlignLeft)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)

        tableColumns = [
            ( '55%', [u'Номер договора'], CReportBase.AlignCenter),
            ( '15%', [u'Дата'], CReportBase.AlignCenter),
            ( '15%', [u'Количество'], CReportBase.AlignCenter),
            ( '15%', [u'Сумма'], CReportBase.AlignCenter)
        ]

        cursor.insertBlock()

        table = createTable(cursor, tableColumns)

        query = selectData(params)
        dateSortType = forceBool(params.get('dateSortType'))
        rowNumber = 0
        curContract = ''
        if dateSortType:
            curDay = None
        else:
            curMonth = 0
        amount = 0
        sum = 0
        contractAmount = 0
        contractSum = 0
        totalAmount = 0
        totalSum = 0
        i = 0
        newContract = False
        sumFormat = QtGui.QTextBlockFormat()
        sumFormat.setAlignment(QtCore.Qt.AlignLeft)
        while query.next():
            record = query.record()
            if curContract != forceString(record.value('number')):
                if i >= 1:
                    i = table.addRow()
                    table.setText(i, 0, u'Итого по договору:', blockFormat=sumFormat, fontBold=True)
                    table.setText(i, 2, contractAmount)
                    table.setText(i, 3, contractSum)
                    table.mergeCells(i, 0, 1, 2)
                    totalAmount += contractAmount
                    totalSum += contractSum
                    contractAmount = 0
                    contractSum = 0
                i = table.addRow()
                table.mergeCells(i - rowNumber - 1, 0, rowNumber, 1)
                rowNumber = 0
                table.setText(i, 0,  u"%s (%s)" % (forceString(record.value('resolution')), forceString(record.value('number'))))
                curContract = forceString(record.value('number'))
                newContract = True
            if dateSortType:
                if curDay != forceDate(record.value('settleDate')) or newContract:
                    if not newContract:
                        i = table.addRow()
                    table.setText(i, 1, forceDate(record.value('settleDate')).toString('dd.MM.yyyy'))
                    if i > 1:
                        if newContract:
                            table.setText(i - 2, 2, amount)
                            table.setText(i - 2, 3, sum)
                        else:
                            table.setText(i - 1, 2, amount)
                            table.setText(i - 1, 3, sum)
                        amount = 0
                        sum = 0
                    curDay = forceDate(record.value('settleDate'))
                    rowNumber += 1
                    newContract = False
            else:
                if curMonth != forceInt(forceDate(record.value('settleDate')).toString('MM')) or newContract:
                    if not newContract:
                        i = table.addRow()
                    table.setText(i, 1, monthName[forceInt(forceDate(record.value('settleDate')).toString('MM'))])
                    if i > 1:
                        if newContract:
                            table.setText(i - 2, 2, amount)
                            table.setText(i - 2, 3, sum)
                        else:
                            table.setText(i - 1, 2, amount)
                            table.setText(i - 1, 3, sum)
                        amount = 0
                        sum = 0
                    curMonth = forceInt(forceDate(record.value('settleDate')).toString('MM'))
                    rowNumber += 1
                    newContract = False
            contractAmount += forceInt(record.value('amount'))
            contractSum += forceInt(record.value('sum'))
            amount += forceInt(record.value('amount'))
            sum += forceInt(record.value('sum'))
        if i > 0:
            table.setText(i, 2, amount)
            table.setText(i, 3, sum)
        i = table.addRow()
        table.setText(i, 0, u'Итого по договору:', blockFormat=sumFormat, fontBold=True)
        table.setText(i, 2, contractAmount)
        table.setText(i, 3, contractSum)
        table.mergeCells(i, 0, 1, 2)
        totalAmount += contractAmount
        totalSum += contractSum
        i = table.addRow()
        table.setText(i, 0, u'Итого:', blockFormat=sumFormat, fontBold=True)
        table.setText(i, 2, totalAmount)
        table.setText(i, 3, totalSum)
        table.mergeCells(i, 0, 1, 2)
        table.mergeCells(i - rowNumber - 1, 0, rowNumber, 1)

        return doc

from Ui_ReportRegisterContractsSetup import Ui_ReportRegisterContractsSetupDialog

class CReportRegisterContractsSetupDialog(QtGui.QDialog, Ui_ReportRegisterContractsSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbFinanceType.setTable('rbFinance')
        self.cmbEventType.setTable('EventType', True)
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        date = QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', date))
        self.edtEndDate.setDate(params.get('endDate', date))
        self.cmbContract.setPath(params.get('contractPath', None))
        self.cmbFinanceType.setValue(params.get('typeFinanceId', None))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['contractPath'] = self.cmbContract.getPath()
        result['contractIdList'] = self.cmbContract.getIdList()
        result['contractText'] = forceString(self.cmbContract.currentText())
        result['typeFinanceId'] = self.cmbFinanceType.value()
        result['eventTypeId'] = self.cmbEventType.value()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['dateSortType'] = 0 if self.btnToMonth.isChecked() else 1
        return result

    @QtCore.pyqtSlot(bool)
    def on_btnToMonth_clicked(self, checked):
        self.btnToMonth.setChecked(True)
        self.btnToDay.setChecked(False)

    @QtCore.pyqtSlot(bool)
    def on_btnToDay_clicked(self, checked):
        self.btnToDay.setChecked(True)
        self.btnToMonth.setChecked(False)
