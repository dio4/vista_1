# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Orgs.Utils import getOrgStructureName
from Reports.Report import CReport
from Reports.ReportBase import CReportBase, createTable
from Reports.SalaryReports.Ui_ReportSalary_PatientSetup import Ui_ReportSalary_PatientSetupDialog
from library.Utils import forceString, forceInt


def selectData(params):
    db = QtGui.qApp.db
    begDate = params.get('begDate')
    endDate = params.get('endDate')
    clientId = params.get('patientId')

    tableEvent = db.table('Event')
    tableAction = db.table('Action')
    tableActionType = db.table('ActionType')
    tableAccountItem = db.table('Account_Item')
    tableOrgStructureActionType = db.table('OrgStructure_ActionType')
    tableVrbPersonWithSpeciality = db.table('vrbPersonWithSpeciality')
    tableAccount = db.table('Account')
    tableContract = db.table('Contract')
    tableClient = db.table('Client')

    cols = [
        tableActionType['name'].alias('serviceName'),
        tableAccountItem['amount'].alias('serviceAmount'),
        tableAccountItem['price'].alias('servicePrice'),
        tableVrbPersonWithSpeciality['name'].alias('performerName'),
        tableOrgStructureActionType['master_id'].alias('orgStructId')
    ]

    queryTable = tableEvent.innerJoin(tableAction, [tableEvent['id'].eq(tableAction['event_id'])])
    queryTable = queryTable.innerJoin(tableActionType, [tableAction['actionType_id'].eq(tableActionType['id'])])
    queryTable = queryTable.innerJoin(tableAccountItem, [tableAction['id'].eq(tableAccountItem['action_id']), tableAccountItem['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(tableOrgStructureActionType, [tableActionType['id'].eq(tableOrgStructureActionType['actionType_id'])])
    queryTable = queryTable.innerJoin(tableClient, [tableEvent['client_id'].eq(tableClient['id'])])
    queryTable = queryTable.innerJoin(tableAccount, [tableAccountItem['master_id'].eq(tableAccount['id'])])
    queryTable = queryTable.innerJoin(tableContract, [tableAccount['contract_id'].eq(tableContract['id'])])
    queryTable = queryTable.innerJoin(tableVrbPersonWithSpeciality, [tableAction['person_id'].eq(tableVrbPersonWithSpeciality['id'])])

    where = [
        tableEvent['deleted'].eq(0),
        tableAccount['deleted'].eq(0),
        tableAccountItem['deleted'].eq(0),
    ]

    if begDate and endDate:
        where.append(tableAccountItem['date'].dateGe(begDate))
        where.append(tableAccountItem['date'].dateLe(endDate))

    where.append(tableClient['id'].eq(clientId))

    where.append(tableAccountItem['refuseType_id'].isNull())
    where.append(db.joinOr([
        tableContract['ignorePayStatusForJobs'].eq(1),
        tableAccountItem['date'].isNotNull()
    ]))

    order = [
        tableOrgStructureActionType['master_id'],
        tableVrbPersonWithSpeciality['name'],
        tableActionType['name']
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

class PerformerRecord:
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
        return unicode(self.name) + ' ' + reduce(lambda res, x: (res + x + '\n'), map(lambda  x: unicode(x), self.services), '')

class OrgRecord:
    def __init__(self, id, performer):
        self.id = id
        self.sum = 0
        self.amount = 0
        self.performers = []
        if performer: self.addPerformer(performer)

    def __addToLastPerformer(self, service):
        self.amount += service.amount
        self.sum += service.sum
        self.performers[-1].addService(service)

    def addPerformer(self, performer):
        if self.performers and performer.name == self.performers[-1].name:
            self.__addToLastPerformer(performer.services[-1])
        else:
            self.amount += performer.amount
            self.sum += performer.sum
            self.performers.append(performer)

    def __unicode__(self):
        return unicode(self.id) + ' ' + reduce(lambda res, x: (res + x + '\n'), map(lambda  x: unicode(x), self.performers), '')

class MasterRecord:
    def __init__(self):
        self.orgs = []
        self.amount = 0
        self.sum = 0

    def currOrgId(self):
        if not self.orgs: return None
        else: return self.orgs[-1].id

    def addElement(self, orgId, performer):
        if orgId == self.currOrgId(): self.orgs[-1].addPerformer(performer)
        else: self.orgs.append(OrgRecord(orgId, performer))
        self.amount += performer.amount
        self.sum += performer.sum

    def __unicode__(self):
        return reduce(lambda res, x: (res + x + '\n'), map(lambda x: unicode(x), self.orgs), '') + '\n'

def buildTable(table, masterRecord):
    i = 1
    for org in masterRecord.orgs:
        numRows = reduce(lambda res, x: (res + x), map(lambda x: len(x.services), org.performers), 0) + len(org.performers)
        row = perfStartRow = orgStartRow = table.addRow()
        for performer in org.performers:
            numRowsPerf = len(performer.services)
            for service in performer.services:
                table.setText(row, 3, service.name)
                table.setText(row, 4, service.amount)
                table.setText(row, 5, service.price)
                table.setText(row, 6, service.sum)
                row = table.addRow()
            table.setText(row, 3, u'Итого')
            table.setText(row, 4, performer.amount)
            table.setText(row, 6, performer.sum)
            table.mergeCells(perfStartRow, 2, numRowsPerf+1, 1)
            table.setText(perfStartRow, 2, performer.name)
            row = perfStartRow = table.addRow()
        table.setText(row, 2, u'Итого')
        table.setText(row, 4, org.amount)
        table.setText(row, 6, org.sum)
        table.mergeCells(orgStartRow, 0, numRows+1, 1)
        table.mergeCells(orgStartRow, 1, numRows+1, 1)
        table.setText(orgStartRow, 1, getOrgStructureName(org.id))
        table.setText(orgStartRow, 0, i)
        i += 1

    row = table.addRow()
    table.mergeCells(row, 0, 1, 4)
    table.setText(row, 0, u'ИТОГО')
    table.setText(row, 4, masterRecord.amount)
    table.setText(row, 6, masterRecord.sum)


class CReportSalary_Patient(CReport):
    def __init__(self, parent):
        super(CReportSalary_Patient, self).__init__(parent)
        self.setTitle(u'Отчёт по заработной плате по пациенту')

    def getSetupDialog(self, parent):
        return CReportSalary_PatientSetupDialog(parent=parent, title=self.title())

    def dumpParams(self, cursor, params, charFormat = QtGui.QTextCharFormat()):
        description = self.getDescription(params)
        name = params['patientName']['firstName'] + ' ' + params['patientName']['lastName'] + ' ' + params['patientName']['patrName']
        description.append(u'Пациент: ' + name)

        columns = [ ('100%', [], CReportBase.AlignLeft) ]
        table = createTable(cursor, columns, headerRowCount=len(description), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(description):
            table.setText(i, 0, row, charFormat = charFormat)
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
            ('2%',          [u'№'],                                CReportBase.AlignLeft),
            ('10%',         [u'Подразделение'],                     CReportBase.AlignLeft),
            ('10%',         [u'ФИО исполнителя'],                   CReportBase.AlignLeft),
            ('40%',         [u'Наименование услуги'],               CReportBase.AlignLeft),
            ('5%',          [u'Кол-во'],                            CReportBase.AlignLeft),
            ('5%',          [u'Цена'],                              CReportBase.AlignLeft),
            ('5%',          [u'Сумма'],                             CReportBase.AlignLeft)
        ]
        table = createTable(cursor, tableColumns)

        masterRecord = MasterRecord()
        while query.next():
            record = query.record()
            orgId = forceInt(record.value('orgStructId'))
            service = ServiceRecord(forceString(record.value('serviceName')),
                                    forceInt(record.value('serviceAmount')),
                                    forceInt(record.value('servicePrice')))
            performer = PerformerRecord(forceString(record.value('performerName')), service)
            masterRecord.addElement(orgId, performer)

        buildTable(table, masterRecord)

        return doc

class CReportSalary_PatientSetupDialog(QtGui.QDialog, Ui_ReportSalary_PatientSetupDialog):
    def __init__(self, parent=None, title=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setTitle(title)

        self.editAmbCard.editingFinished.connect(self.on_CardNumberEntered)
        self.editFirstName.editingFinished.connect(self.on_NameEntered)
        self.editLastName.editingFinished.connect(self.on_NameEntered)
        self.editPatrName.editingFinished.connect(self.on_NameEntered)

        self.editAmbCard.setValidator(QtGui.QIntValidator())

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        currentDate = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate(currentDate.year(), currentDate.month(), 1)))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate(currentDate.year(), currentDate.month(), currentDate.daysInMonth())))
        self.editAmbCard.setText(params.get('ambCardNumb', '0'))

    def on_CardNumberEntered(self):
        if self.editAmbCard.text():
            name = self.__getPatientName(forceInt(self.editAmbCard.text()))
            if name:
                self.editFirstName.setText(name['firstName'])
                self.editLastName.setText(name['lastName'])
                self.editPatrName.setText(name['patrName'])
            else:
                self.editFirstName.clear()
                self.editLastName.clear()
                self.editPatrName.clear()

    def on_NameEntered(self):
        if self.editFirstName.text() and self.editLastName.text() and self.editPatrName.text():
            id = self.__getPatientId({  'firstName'     : self.editFirstName.text(),
                                        'lastName'      : self.editLastName.text(),
                                        'patrName'      : self.editPatrName.text()})
            if id:
                self.editAmbCard.setText(forceString(id))
            else:
                self.editAmbCard.setText('0')

    def __getPatientName(self, id):
        #TODO:skkachaev:удалить обращения к базе данных из вьюхи
        db = QtGui.qApp.db
        tableClient = db.table('Client')
        cols = [tableClient['firstName'], tableClient['lastName'], tableClient['patrName']]
        record = db.getRecordEx(tableClient, cols, [tableClient['id'].eq(id)])
        name = None
        if record: name = {'firstName'  : forceString(record.value('firstName')),
                           'lastName' : forceString(record.value('lastName')),
                           'patrName'   : forceString(record.value('patrName'))}
        return name

    def __getPatientId(self, name):
        #TODO:skkachaev:удалить обращения к базе данных из вьюхи
        db = QtGui.qApp.db
        tableClient = db.table('Client')
        cols = [tableClient['id']]
        record = db.getRecordEx(tableClient, cols, [tableClient['firstName'].eq(name['firstName']),
                                                    tableClient['lastName'].eq(name['lastName']),
                                                    tableClient['patrName'].eq(name['patrName'])])
        id = None
        if record: id = forceInt(record.value('id'))
        return id

    def params(self):
        return \
            {
                'begDate'           : self.edtBegDate.date(),
                'endDate'           : self.edtEndDate.date(),
                'patientId'         : forceInt(self.editAmbCard.text()),
                'patientName'       : {'firstName' : self.editFirstName.text(), 'lastName' : self.editLastName.text(), 'patrName' : self.editPatrName.text()}
            }

    def on_buttonBox_accepted(self):
        if (not self.editAmbCard.text() or self.editAmbCard.text() == '0') and (
            not self.editFirstName.text() or
            not self.editPatrName.text() or
            not self.editLastName.text()
        ):
            QtGui.QMessageBox.critical(self, u'Внимание!', u'Необходимо выбрать пациента!')
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

    CReportSalary_Patient(None).exec_()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()