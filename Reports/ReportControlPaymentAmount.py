# coding=utf-8
from PyQt4 import QtGui, QtCore

from PyQt4.QtCore import *

from Orgs.Utils import getOrgStructureFullName
from Reports.Report import CReport
from Reports.ReportBase import CReportBase, createTable
from Reports.Ui_ReportControlPaymentAmount import Ui_ReportControlPaymentAmount
from library.DialogBase import CConstructHelperMixin
from library.TableModel import CTextCol, CTableModel
from library.Utils import forceString, forceInt, forceDate


def selectData(params):
    db = QtGui.qApp.db
    begDateReestr = params.get('begDateReestr')
    endDateReestr = params.get('endDateReestr')
    financeId = params.get('typeFinanceId', None)
    accountNumbersList = params.get('accountNumbersList', None)

    tableEvent = db.table('Event')
    tableAccountItem = db.table('Account_Item')
    tableAccount = db.table('Account')
    tableContract = db.table('Contract')
    tableVrbPersonWithSpeciality = db.table('vrbPersonWithSpeciality')
    tableClient = db.table('Client')

    cond = [
        tableAccount['deleted'].eq(0),
        tableAccountItem['deleted'].eq(0)
    ]

    cond.append(db.joinAnd([
        tableAccount['settleDate'].ge(begDateReestr),
        tableAccount['settleDate'].le(endDateReestr)
    ]))

    if financeId:
        cond.append(tableContract['finance_id'].eq(financeId))
    if accountNumbersList:
        cond.append(tableAccount['number'].inlist(accountNumbersList))

    cols = [
        tableClient['id'].alias('clientId'),
        # '''CONCAT_WS(' ', Client.`lastName`, Client.`firstName`, Client.`patrName`) AS `name`''',
        db.CONCAT_WS([tableClient['lastName'], tableClient['firstName'], tableClient['patrName']], alias='name'),
        tableClient['birthDate'].alias('birthDate'),
        tableEvent['setDate'].alias('start'),
        tableEvent['execDate'].alias('finish'),
        # '''CONCAT_WS(' ', vrbPersonWithSpeciality.`code`, vrbPersonWithSpeciality.`name`)  AS `doctor`''',
        db.CONCAT_WS([tableVrbPersonWithSpeciality['code'], tableVrbPersonWithSpeciality['name']], alias='doctor'),
        tableVrbPersonWithSpeciality['orgStructure_id'].alias('orgStructure'),
        # tableAccount['contract_id'].alias('contractId'),
        db.CONCAT_WS([tableContract['number'], tableContract['resolution'], tableContract['grouping']], alias='contract', separator='/'),
        tableAccount['number'].alias('accountNumber')
    ]

    queryTable = tableEvent.leftJoin(tableAccountItem, [tableEvent['id'].eq(tableAccountItem['event_id']),tableAccountItem['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(tableAccount, tableAccountItem['master_id'].eq(tableAccount['id']))
    queryTable = queryTable.leftJoin(tableContract, tableEvent['contract_id'].eq(tableContract['id']))
    queryTable = queryTable.leftJoin(tableVrbPersonWithSpeciality, tableEvent['execPerson_id'].eq(tableVrbPersonWithSpeciality['id']))
    queryTable = queryTable.leftJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))

    group = [tableAccountItem['event_id']]
    having = ''' SUM(Account_Item.sum) = 0 '''

    stmt = db.selectStmt(queryTable, cols, where=cond, group=group, having=having)
    return db.query(stmt)

class CReportControlPaymentAmount(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u"Обращения с суммой к оплате равной нулю")

    def getSetupDialog(self, parent):
        result = CReportControlPaymentAmountDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            (' 2%', [u'№ п/п'],            CReportBase.AlignLeft),
            (' 8%', [u'Код пациента'],      CReportBase.AlignLeft),
            ('15%', [u'ФИО пациента'],      CReportBase.AlignLeft),
            ('10%', [u'Д/р'],               CReportBase.AlignLeft),
            ('10%', [u'Период лечения'],    CReportBase.AlignLeft),
            ('15%', [u'Врач'],              CReportBase.AlignLeft),
            ('20%', [u'Подразделение'],     CReportBase.AlignLeft),
            ('10%', [u'Договор'],           CReportBase.AlignLeft),
            ('10%', [u'Номер реестра'],     CReportBase.AlignLeft)
        ]

        table = createTable(cursor, tableColumns)

        while query.next():
            record = query.record()
            row = table.addRow()
            fields = (
                row,
                forceInt(record.value('clientId')),
                forceString(record.value('name')),
                forceString(record.value('birthDate')),
                forceString(forceDate(record.value('start')).toString('dd.MM.yyyy') + ' - ' + forceDate(record.value('finish')).toString('dd.MM.yyyy')),
                forceString(record.value('doctor')),
                getOrgStructureFullName(record.value('orgStructure')),
                forceString(record.value('contract')),
                forceString(record.value('accountNumber'))
            )
            for col, val in enumerate(fields):
                table.setText(row, col, val)

        return doc


class CReportControlPaymentAmountDialog(QtGui.QDialog, Ui_ReportControlPaymentAmount, CConstructHelperMixin):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        
        self.cols = [CTextCol(u'Номер счета', ['number'], 100)]
        self.tableName = 'Account'

        self.preSetupUi()
        self.setupUi(self)

        self.cmbFinance.setTable('rbFinance')

        self.postSetupUi()

        # self.cmbContract.setCheckMaxClients(True)

        
    def preSetupUi(self):
        self.addModels('Table', CTableModel(self, self.cols, self.tableName))
        
    def postSetupUi(self):
        idList = self.getIdList(self.params())
        self.setModels(self.tblNumbers, self.modelTable, self.selectionModelTable)
        self.tblNumbers.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.modelTable.setIdList(idList)
        self.selectionModelTable.clearSelection()
        self.tblNumbers.setFocus(Qt.OtherFocusReason)
        self.tblNumbers.setEnabled(True)

        self.connect(self.cmbFinance, QtCore.SIGNAL('currentIndexChanged(int)'), self.on_filterChanged)
        self.connect(self.edtBegDate, QtCore.SIGNAL('dateChanged(const QDate &)'), self.on_filterChanged)
        self.connect(self.edtEndDate, QtCore.SIGNAL('dateChanged(const QDate &)'), self.on_filterChanged)
        self.connect(self.cmbContract, QtCore.SIGNAL('currentIndexChanged(int)'), self.on_filterChanged)

    @QtCore.pyqtSlot()
    def on_filterChanged(self):
        self.modelTable.setIdList(self.getIdList(self.params()))

    def getIdList(self, params):
        db = QtGui.qApp.db

        table = self.modelTable.table()
        tableContract = db.table('Contract')

        cond = []
        cond.append(db.joinAnd(
            [table['settleDate'].ge(params.get('begDateReestr')),
            table['settleDate'].le(params.get('endDateReestr'))]
        ))
        cond.append(tableContract['id'].inlist(params.get('contractIdList')))

        # print params.get('contractIdList')

        if params.get('typeFinanceId'):
            cond.append(tableContract['finance_id'].eq(params.get('typeFinanceId')))

        queryTable = table.innerJoin(tableContract, table['contract_id'].eq(tableContract['id']))
        return QtGui.qApp.db.getIdList(table=queryTable, where=cond, idCol=table['id'])

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        currentDate = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDateReestr', QtCore.QDate(currentDate.year(), currentDate.month(), 1)))
        self.edtEndDate.setDate(params.get('endDateReestr', QtCore.QDate(currentDate.year(), currentDate.month(), currentDate.daysInMonth())))
        self.cmbFinance.setValue(params.get('typeFinanceId', 2))
        self.cmbContract.setPath(params.get('contractPath', u''))

    def params(self):
        result = {
            'begDateReestr'           : self.edtBegDate.date(),
            'endDateReestr'           : self.edtEndDate.date(),
            'typeFinanceId'           : self.cmbFinance.value(),
            'accountNumbersList'      : self.tblNumbers.selectedElementsAsStringsList(),
            'contractIdList'          : self.cmbContract.getIdList(),
            'contractPath'            : self.cmbContract.getPath()
        }

        return result

    @QtCore.pyqtSlot(int)
    def on_cmbFinance_currentIndexChanged(self, index):
        if self.cmbFinance.getValue():
            self.cmbContract.setFinanceTypeCodes([self.cmbFinance.getValue()])
        else:
            self.cmbContract.setFinanceTypeCodes(None)
