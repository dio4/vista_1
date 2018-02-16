# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from library.DialogBase import CDialogBase
from library.Utils      import forceDate, forceDateTime, forceInt, forceRef, forceString

from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase

from Ui_DailyServicesReport import Ui_DailyServicesReportSetupDialog


def selectData(date, financeSource, payStatus):
    db = QtGui.qApp.db
    tableAccount = db.table('Account')
    tableAccountItem = db.table('Account_Item')
    tableAction = db.table('Action')
    tableClient = db.table('Client')
    tableContract = db.table('Contract')
    tableEvent = db.table('Event')
    tableFinance = db.table('rbFinance')
    tablePerson = db.table('Person')
    tableService = db.table('rbService')
    tableVisit = db.table('Visit')

    subqueryTable = tableAccountItem.leftJoin(tableAccount, tableAccount['id'].eq(tableAccountItem['master_id']))
    subqueryTable = subqueryTable.leftJoin(tableContract, tableContract['id'].eq(tableAccount['contract_id']))
    subqueryTable = subqueryTable.leftJoin(tableFinance, tableFinance['id'].eq(tableContract['finance_id']))
    subqueryTable = subqueryTable.leftJoin(tableEvent, tableEvent['id'].eq(tableAccountItem['event_id']))
    subqueryTable = subqueryTable.leftJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))
    subqueryTable = subqueryTable.leftJoin(tableService, tableService['id'].eq(tableAccountItem['service_id']))
    subqueryTable = subqueryTable.leftJoin(tablePerson, tablePerson['id'].eq(tableAccount['createPerson_id']))
    subqueryTable = subqueryTable.leftJoin(tableAction, tableAction['id'].eq(tableAccountItem['action_id']))
    subqueryTable = subqueryTable.leftJoin(tableVisit, tableVisit['id'].eq(tableAccountItem['visit_id']))

    subQueryCols = [
        "concat_ws(' ', Client.lastName, Client.firstName, Client.patrName) AS clientName",
        tableService['name'].alias('serviceName'),
        'if(Action.endDate IS NULL, Visit.date, Action.endDate) AS serviceDate',
        tableFinance['name'].alias('financeSource'),
        u"if(Account_Item.date AND Account_Item.refuseType_id IS NULL, 'оплачено', if(Account_Item.date AND Account_Item.refuseType_id, 'отказано', if(Account_Item.id, 'выставлено', ''))) AS payStatus",
        "concat_ws(' ', Person.lastName, Person.firstName, Person.patrName) AS registrar"
    ]
    subQueryCond = [
        tableAccount['deleted'].eq(0),
        tableAccountItem['deleted'].eq(0),
        tableClient['deleted'].eq(0),
        tableContract['deleted'].eq(0),
        tableEvent['deleted'].eq(0),
        tablePerson['deleted'].eq(0)
    ]

    if not financeSource is None:
        subQueryCond.append(tableFinance['id'].eq(financeSource))

    queryTable = '(' + db.selectStmt(subqueryTable, subQueryCols, subQueryCond) + ') AS T'
    cond = [
        "DATE(serviceDate) = DATE('%s')" % date.toString('yyyy-MM-dd')
    ]
    order = [
        'clientName'
    ]

    if payStatus != 0:
        payStatusMap = {
            1: u'оплачено',
            2: u'выставлено',
            3: u'отказано'
        }
        cond.append("payStatus = '%s'" % payStatusMap[payStatus])

    stmt = db.selectStmt(queryTable, '*', cond, order=order)
    return db.query(stmt)


class CDailyServicesReportSetupDialog(CDialogBase, Ui_DailyServicesReportSetupDialog):

    def __init__(self, parent = None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.cmbFinanceSource.setTable('rbFinance', addNone=True)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtDate.setDate(params.get('date', QtCore.QDate.currentDate()))
        self.cmbFinanceSource.setValue(params.get('financeSource', None))
        self.cmbPayStatus.setCurrentIndex(params.get('payStatus', 0))

    def params(self):
        params = {}
        params['date'] = self.edtDate.date()
        params['financeSource'] = self.cmbFinanceSource.value()
        params['payStatus'] = self.cmbPayStatus.currentIndex()
        return params


class CDailyServicesReport(CReport):

    def __init__(self, parent = None):
        CReport.__init__(self, parent)
        self.setTitle(u'Ежедневный отчет')

    def getSetupDialog(self, parent):
        result = CDailyServicesReportSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        date = forceDate(params.get('date', QtCore.QDate()))
        financeSource = forceRef(params.get('financeSource', None))
        payStatus = forceInt(params.get('payStatus', 0))

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('20%', [u'ФИО пациента'], CReportBase.AlignRight),
            ('20%', [u'Услуга'], CReportBase.AlignRight),
            ('20%', [u'Дата и время'], CReportBase.AlignRight),
            ('10%', [u'Источник финансирования'], CReportBase.AlignRight),
            ('10%', [u'Отметка об оплате'], CReportBase.AlignRight),
            ('20%', [u'Регистратор'], CReportBase.AlignRight),
        ]
        table = createTable(cursor, tableColumns)

        query = selectData(date, financeSource, payStatus)
        self.setQueryText(forceString(query.lastQuery()))

        while query.next():
            record = query.record()
            clientName = forceString(record.value('clientName'))
            serviceName = forceString(record.value('serviceName'))
            serviceDate = forceDateTime(record.value('serviceDate')).toString('dd.MM.yyyy hh:mm')
            financeSource = forceString(record.value('financeSource'))
            payStatus = forceString(record.value('payStatus'))
            registrar = forceString(record.value('registrar'))

            i = table.addRow()
            table.setText(i, 0, clientName)
            table.setText(i, 1, serviceName)
            table.setText(i, 2, serviceDate)
            table.setText(i, 3, financeSource)
            table.setText(i, 4, payStatus)
            table.setText(i, 5, registrar)

        return doc
