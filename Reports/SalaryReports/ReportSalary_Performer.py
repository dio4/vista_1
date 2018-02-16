# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore

from Orgs.Utils import getOrgStructureName
from Reports.Report import CReport
from Reports.ReportBase import CReportBase, createTable
from Reports.SalaryReports.Ui_ReportSalary_PerformerSetup import Ui_ReportSalary_PerformerSetupDialog
from library.Utils import forceString, forceInt


def selectData(params):
    db = QtGui.qApp.db
    begDate = params.get('begDate')
    endDate = params.get('endDate')
    performerId = params.get('performerId')
    type = params.get('type')

    tablePerson = db.table('Person')
    tableAction = db.table('Action')
    tableActionType = db.table('ActionType')
    tableOrgStructureActionType = db.table('OrgStructure_ActionType')
    tableAccountItem = db.table('Account_Item')
    tableAccount = db.table('Account')
    tableContract = db.table('Contract')

    cols = [
        tableActionType['name'].alias('serviceName'),
        tableAccountItem['amount'].alias('serviceAmount'),
        tableAccountItem['price'].alias('servicePrice'),
        tableOrgStructureActionType['master_id'].alias('orgStructId')
    ]

    if type == 0:
        queryTable = tablePerson.innerJoin(tableAction, [tablePerson['id'].eq(tableAction['person_id'])])
    else:
        queryTable = tablePerson.innerJoin(tableAction, [
            '''
            EXISTS(
                SELECT Action_Assistant.`id`
                FROM Action_Assistant
                    INNER JOIN rbActionAssistantType ON rbActionAssistantType.`id` = Action_Assistant.`assistantType_id`
                WHERE
                    Action_Assistant.`action_id` = Action.`id`
                    AND rbActionAssistantType.`code` LIKE 'assistant%'
                    AND Action_Assistant.`person_id` = Person.`id`
                LIMIT 1)
            '''
        ])
    queryTable = queryTable.innerJoin(tableActionType, [tableAction['actionType_id'].eq(tableActionType['id'])])
    queryTable = queryTable.innerJoin(tableOrgStructureActionType, [tableActionType['id'].eq(tableOrgStructureActionType['actionType_id'])])
    queryTable = queryTable.innerJoin(tableAccountItem, [tableAction['id'].eq(tableAccountItem['action_id'])])
    queryTable = queryTable.innerJoin(tableAccount, [tableAccountItem['master_id'].eq(tableAccount['id'])])
    queryTable = queryTable.innerJoin(tableContract, [tableAccount['contract_id'].eq(tableContract['id'])])

    where = [
        tablePerson['id'].eq(performerId),
        tableAccount['deleted'].eq(0),
        tableAccountItem['deleted'].eq(0),
    ]
    if begDate and endDate:
        where.append(tableAccountItem['date'].dateGe(begDate))
        where.append(tableAccountItem['date'].dateLe(endDate))
    where.append(tableAccountItem['refuseType_id'].isNull())
    where.append(db.joinOr([
        tableContract['ignorePayStatusForJobs'].eq(1),
        tableAccountItem['date'].isNotNull()
    ]))

    order = [
        tableOrgStructureActionType['master_id'],
        tableActionType['id']
    ]

    stmt = db.selectStmt(queryTable, cols, where=where, order=order)
    return db.query(stmt)

class ServiceRecord:
    def __init__(self, name, amount, price = 0):
        self.sum = price * amount
        self.amount = amount
        self.price = price
        self.name = name

    def add(self, amount):
        self.amount += amount
        self.sum += amount * self.price

    def asList(self):
        return [self.name, self.amount, self.price, self.sum]

    def __unicode__(self):
        return unicode(self.name) + ' ' + unicode(self.amount) + ' ' + unicode(self.price) + ' ' + unicode(self.sum)

class OrgRecord:
    def __init__(self, id, service = None):
        self.sum = 0
        self.amount = 0
        self.services = []
        self.id = id
        if service: self.addService(service)

    def __addToLastService(self, amount):
        self.amount += amount
        self.sum += amount * self.services[-1].price
        self.services[-1].add(amount)

    def addService(self, service):
        if self.services and service.name == self.services[-1].name:
            self.__addToLastService(service.amount)
        else:
            self.amount += service.amount
            self.sum += service.amount * service.price
            self.services.append(service)

    def __unicode__(self):
        return unicode(self.id) + ' ' + reduce(lambda res, x: (res + x + '\n'), map(lambda  x: unicode(x), self.services), '')

class MasterRecord:
    def __init__(self):
        self.orgs = []
        self.amount = 0
        self.sum = 0

    def currOrgId(self):
        if not self.orgs: return None
        else: return self.orgs[-1].id

    def addElement(self, orgId, service):
        if orgId == self.currOrgId(): self.orgs[-1].addService(service)
        else: self.orgs.append(OrgRecord(orgId, service))
        self.amount += service.amount
        self.sum += service.sum


    def __unicode__(self):
        return reduce(lambda res, x: (res + x + '\n'), map(lambda x: unicode(x), self.orgs), '') + '\n'

def buildTable(table, masterRecord, type):
    for org in masterRecord.orgs:
        numRows = len(org.services)
        row = startRow = table.addRow()
        for service in org.services:
            table.setText(row, 1, service.name)
            table.setText(row, 2, service.amount)
            if type == 0:
                table.setText(row, 3, service.price)
                table.setText(row, 4, service.sum)
            row = table.addRow()
        table.setText(row, 1, u'Итого')
        table.setText(row, 2, org.amount)
        if type == 0:
            table.setText(row, 4, org.sum)
        table.mergeCells(startRow, 0, numRows+1, 1)
        table.setText(startRow, 0, getOrgStructureName(org.id))

    row = table.addRow()
    table.mergeCells(row, 0, 1, 2)
    table.setText(row, 0, u'ИТОГО')
    table.setText(row, 2, masterRecord.amount)
    if type == 0:
        table.setText(row, 4, masterRecord.sum)

class CReportSalary_Performer(CReport):
    def __init__(self, parent):
        CReport.__init__(self,parent)
        self.setTitle(u'Отчёт по заработной плате по исполнителю')

    def getSetupDialog(self, parent):
        return CReportSalary_PerformerSetupDialog(parent=parent, title=self.title())

    @staticmethod
    def getPerformerName(params):
        return QtGui.qApp.db.query(
            '''
            SELECT
                vrbPersonWithSpeciality.`name`
            FROM
                vrbPersonWithSpeciality
            WHERE
                vrbPersonWithSpeciality.`id` = %i
            ''' % params.get('performerId')
        )

    def dumpParams(self, cursor, params, charFormat = QtGui.QTextCharFormat()):
        description = self.getDescription(params)

        query = self.getPerformerName(params)
        while query.next():
            record = query.record()
            description.append(u'Исполнитель: ' + forceString(record.value('name')))

        columns = [ ('100%', [], CReportBase.AlignLeft) ]
        table = createTable(cursor, columns, headerRowCount=len(description), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(description):
            table.setText(i, 0, row, charFormat = charFormat)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()

    def build(self, params):
        type = params.get('type')
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
            ('10%',             [u'Подразделение'],                         CReportBase.AlignLeft),
            ('30%',             [u'Наименование услуги'],                   CReportBase.AlignLeft),
            ('5%',              [u'Кол-во'],                                CReportBase.AlignLeft)
        ]

        if type == 0:
            tableColumns.append(('5%',           [u'Цена'],              CReportBase.AlignLeft))
            tableColumns.append(('5%',           [u'Сумма'],             CReportBase.AlignLeft))

        table = createTable(cursor, tableColumns)


        masterRecord = MasterRecord()
        while query.next():
            record = query.record()
            orgId = forceInt(record.value('orgStructId'))
            service = ServiceRecord(forceString(record.value('serviceName')),
                                    forceInt(record.value('serviceAmount')),
                                    forceInt(record.value('servicePrice')))
            masterRecord.addElement(orgId, service)

        buildTable(table, masterRecord, type)

        return doc

class CReportSalary_PerformerSetupDialog(QtGui.QDialog, Ui_ReportSalary_PerformerSetupDialog):
    def __init__(self, parent=None, title=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setTitle(title)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        currentDate = QtCore.QDate.currentDate()
        self.cmbPerformer.setValue(params.get('performerId'))
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate(currentDate.year(), currentDate.month(), 1)))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate(currentDate.year(), currentDate.month(), currentDate.daysInMonth())))


    def params(self):
        return \
            {
                'begDate'       : self.edtBegDate.date(),
                'endDate'       : self.edtEndDate.date(),
                'performerId'   : self.cmbPerformer.value(),
                'type'          : self.cmbType.currentIndex()
            }

    def on_buttonBox_accepted(self):
        if not self.cmbPerformer.value():
            QtGui.QMessageBox.critical(self, u'Внимание!', u'Необходимо выбрать исполнителя!')
        else:
            self.accept()


def main():
    import sys
    from library.database import connectDataBaseByInfo
    from s11main import CS11mainApp
    app = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtGui.qApp = app
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    QtGui.qApp.currentOrgId = lambda: 3147

    connectionInfo = {'driverName' : 'mysql',
                      'host' : 'pes',
                      'port' : 3306,
                      'database' : 's12',
                      'user' : 'dbuser',
                      'password' : 'dbpassword',
                      'connectionName' : 'vista-med',
                      'compressData' : True,
                      'afterConnectFunc' : None}
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    CReportSalary_Performer(None).exec_()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()