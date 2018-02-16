# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Orgs.Utils import getOrgStructureDescendants, getOrgStructureFullName
from Reports.Report import CReport
from Reports.ReportBase import CReportBase, createTable
from Reports.SalaryReports.Ui_ReportSalary_OrgStructureSetup import Ui_ReportSalary_OrgStructureSetupDialog
from library.Utils import forceInt, forceString


def selectData(params):
    db = QtGui.qApp.db
    begDate = params.get('begDate')
    endDate = params.get('endDate')
    orgStructId = params.get('orgStructId')

    tableEvent = db.table('Event')
    tableAction = db.table('Action')
    tableActionType = db.table('ActionType')
    tableAccountItem = db.table('Account_Item')
    tableOrgStructureActionType = db.table('OrgStructure_ActionType')
    tableOrgStructure = db.table('OrgStructure')
    tableVrbPersonWithSpeciality = db.table('vrbPersonWithSpeciality')
    tableAccount = db.table('Account')
    tableContract = db.table('Contract')

    cols = [
        tableActionType['name'].alias('serviceName'),
        tableAccountItem['amount'].alias('serviceAmount'),
        tableAccountItem['price'].alias('servicePrice'),
        tableVrbPersonWithSpeciality['id'].alias('personId'),
        tableVrbPersonWithSpeciality['name'].alias('performerName'),
        tableOrgStructureActionType['master_id'].alias('orgStructId'),
        tableOrgStructure['code'].alias('orgStructName')
    ]

    queryTable = tableEvent.innerJoin(tableAction, [tableEvent['id'].eq(tableAction['event_id'])])
    queryTable = queryTable.innerJoin(tableActionType, [tableAction['actionType_id'].eq(tableActionType['id'])])
    queryTable = queryTable.innerJoin(tableAccountItem, [tableAction['id'].eq(tableAccountItem['action_id']), tableAccountItem['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(tableOrgStructureActionType, [tableActionType['id'].eq(tableOrgStructureActionType['actionType_id'])])
    queryTable = queryTable.innerJoin(tableOrgStructure, tableOrgStructure['id'].eq(tableOrgStructureActionType['master_id']))
    queryTable = queryTable.innerJoin(tableAccount, [tableAccountItem['master_id'].eq(tableAccount['id'])])
    queryTable = queryTable.innerJoin(tableContract, [tableAccount['contract_id'].eq(tableContract['id'])])
    queryTable = queryTable.innerJoin(tableVrbPersonWithSpeciality, [tableAction['person_id'].eq(tableVrbPersonWithSpeciality['id'])])

    where = [tableEvent['deleted'].eq(0), tableAccount['deleted'].eq(0), tableAccountItem['deleted'].eq(0)]

    if begDate and endDate:
        where.append(tableAccountItem['date'].dateGe(begDate))
        where.append(tableAccountItem['date'].dateLe(endDate))

    where.append(tableOrgStructureActionType['master_id'].inlist(getOrgStructureDescendants(orgStructId)))

    where.append(tableAccountItem['refuseType_id'].isNull())
    where.append(db.joinOr([
        tableContract['ignorePayStatusForJobs'].eq(1),
        tableAccountItem['date'].isNotNull()
    ]))

    order = [
        tableVrbPersonWithSpeciality['name'],
        tableOrgStructure['code'],
        tableActionType['name']
    ]

    stmt = db.selectStmt(queryTable, cols, where=where, order=order)
    return db.query(stmt)


class ServiceRecord:
    def __init__(self, name, amount, price=0):
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


class OrgStructureRecord:
    def __init__(self, name, service):
        self.name = name
        self.sum = 0
        self.amount = 0
        self.services = []
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
        return unicode(self.name) + ' ' + reduce(lambda res, x: (res + x + '\n'), map(lambda x: unicode(x), self.services), '')


class PersonRecord:
    def __init__(self, id, name, orgStructure):
        self.id = id
        self.name = name
        self.sum = 0
        self.amount = 0
        self.orgStructures = []
        if orgStructure: self.addOrgStructure(orgStructure)

    def __addToLastOrgStructure(self, service):
        self.amount += service.amount
        self.sum += service.sum
        self.orgStructures[-1].addService(service)

    def addOrgStructure(self, orgStructure):
        if self.orgStructures and orgStructure.name == self.orgStructures[-1].name:
            self.__addToLastOrgStructure(orgStructure.services[-1])
        else:
            self.amount += orgStructure.amount
            self.sum += orgStructure.sum
            self.orgStructures.append(orgStructure)

    def __unicode__(self):
        return unicode(self.id) + ' ' + reduce(lambda res, x: (res + x + '\n'), map(lambda x: unicode(x), self.orgStructures), '')


class MasterRecord:
    def __init__(self):
        self.persons = []
        self.amount = 0
        self.sum = 0

    def currPersonId(self):
        return self.persons[-1].id if self.persons else None

    def addElement(self, personId, personName, orgStructure):
        if personId == self.currPersonId():
            self.persons[-1].addOrgStructure(orgStructure)
        else:
            self.persons.append(PersonRecord(personId, personName, orgStructure))
        self.amount += orgStructure.amount
        self.sum += orgStructure.sum

    def __unicode__(self):
        return reduce(lambda res, x: (res + x + '\n'), map(lambda x: unicode(x), self.persons), '') + '\n'


def buildTable(table, masterRecord):
    i = 1
    for person in masterRecord.persons:
        numRows = reduce(lambda res, x: (res + x), map(lambda x: len(x.services), person.orgStructures), 0) + len(person.orgStructures)
        row = perfStartRow = orgStartRow = table.addRow()
        for orgStructure in person.orgStructures:
            numRowsPerf = len(orgStructure.services)
            for service in orgStructure.services:
                table.setText(row, 3, service.name)
                table.setText(row, 4, service.amount)
                table.setText(row, 5, service.price)
                table.setText(row, 6, service.sum)
                row = table.addRow()
            table.setText(row, 3, u'Итого')
            table.setText(row, 4, orgStructure.amount)
            table.setText(row, 6, orgStructure.sum)
            table.mergeCells(perfStartRow, 2, numRowsPerf + 1, 1)
            table.setText(perfStartRow, 2, orgStructure.name)
            row = perfStartRow = table.addRow()
        table.setText(row, 2, u'Итого')
        table.setText(row, 4, person.amount)
        table.setText(row, 6, person.sum)
        table.mergeCells(orgStartRow, 0, numRows + 1, 1)
        table.mergeCells(orgStartRow, 1, numRows + 1, 1)
        table.setText(orgStartRow, 1, person.name)
        table.setText(orgStartRow, 0, i)
        i += 1

    row = table.addRow()
    table.mergeCells(row, 0, 1, 4)
    table.setText(row, 0, u'ИТОГО')
    table.setText(row, 4, masterRecord.amount)
    table.setText(row, 6, masterRecord.sum)


class CReportSalary_OrgStructure(CReport):
    def __init__(self, parent):
        super(CReportSalary_OrgStructure, self).__init__(parent)
        self.setTitle(u'Отчёт по заработной плате по подразделению')

    def getSetupDialog(self, parent):
        return CReportSalary_OrgStructureSetupDialog(parent=parent, title=self.title())

    def dumpParams(self, cursor, params, charFormat=QtGui.QTextCharFormat()):
        description = self.getDescription(params)
        description.append(u'Старшее подразделение: ' + getOrgStructureFullName(params.get('orgStructId')))

        columns = [('100%', [], CReportBase.AlignLeft)]
        table = createTable(cursor, columns, headerRowCount=len(description), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(description):
            table.setText(i, 0, row, charFormat=charFormat)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()

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
            ('2%', [u'№'], CReportBase.AlignLeft),
            ('10%', [u'Подразделение'], CReportBase.AlignLeft),
            ('10%', [u'ФИО исполнителя'], CReportBase.AlignLeft),
            ('40%', [u'Наименование услуги'], CReportBase.AlignLeft),
            ('5%', [u'Кол-во'], CReportBase.AlignLeft),
            ('5%', [u'Цена'], CReportBase.AlignLeft),
            ('5%', [u'Сумма'], CReportBase.AlignLeft)
        ]
        table = createTable(cursor, tableColumns)

        masterRecord = MasterRecord()
        while query.next():
            record = query.record()
            personId = forceInt(record.value('personId'))
            service = ServiceRecord(forceString(record.value('serviceName')),
                                    forceInt(record.value('serviceAmount')),
                                    forceInt(record.value('servicePrice')))
            orgStructure = OrgStructureRecord(forceString(record.value('orgStructName')), service)
            masterRecord.addElement(personId, forceString(record.value('performerName')), orgStructure)

        buildTable(table, masterRecord)

        return doc


class CReportSalary_OrgStructureSetupDialog(QtGui.QDialog, Ui_ReportSalary_OrgStructureSetupDialog):
    def __init__(self, parent=None, title=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setTitle(title)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        currentDate = QtCore.QDate.currentDate()
        self.cmbOrgStructure.setValue(params.get('orgStructId', None))
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate(currentDate.year(), currentDate.month(), 1)))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate(currentDate.year(), currentDate.month(), currentDate.daysInMonth())))

    def params(self):
        return {
            'begDate'    : self.edtBegDate.date(),
            'endDate'    : self.edtEndDate.date(),
            'orgStructId': self.cmbOrgStructure.value()
        }

    @QtCore.pyqtSlot()
    def on_buttonBox_accepted(self):
        if not self.cmbOrgStructure.value():
            QtGui.QMessageBox.critical(self, u'Внимание!', u'Необходимо выбрать подразделение!')
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

    connectionInfo = {'driverName'      : 'mysql',
                      'host'            : 'pes',
                      'port'            : 3306,
                      'database'        : 's12',
                      'user'            : 'dbuser',
                      'password'        : 'dbpassword',
                      'connectionName'  : 'vista-med',
                      'compressData'    : True,
                      'afterConnectFunc': None}
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    CReportSalary_OrgStructure(None).exec_()

    # sys.exit(app.exec_())


if __name__ == '__main__':
    main()
