# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
from Events.Utils import CFinanceType
from Orgs.Utils import getOrganisationShortName, getOrgStructureName, getOrgStructureDescendants
from Reports.Report import CReport
from Reports.ReportBase import CReportBase, createTable
from Reports.StGeorge.Ui_ReportOrgByDoctorSetup import Ui_ReportOrgByDoctorSetupDialog
from library.Utils import forceString, forceInt


def selectData(params):
    db = QtGui.qApp.db
    begDate = params.get('begDate')
    endDate = params.get('endDate')
    orgStructId = params.get('orgStructId')
    contractIds = params.get('contractIds')
    organisationId = params.get('organisationId')
    personId = params.get('personId')

    tableEvent = db.table('Event')
    tableRealAction = db.table('Action').alias('RealAction')
    tableMovingAction = db.table('Action').alias('MovingAction')
    tableRealActionType = db.table('ActionType').alias('RealActionType')
    tableMovingActionType = db.table('ActionType').alias('MovingActionType')
    tableMovingActionPropertyType = db.table('ActionPropertyType').alias('MovingActionPropertyType')
    tableMovingActionProperty = db.table('ActionProperty').alias('MovingActionProperty')
    tableMovingActionProperty_OrgStructure = db.table('ActionProperty_OrgStructure').alias('MovingActionProperty_OrgStructure')
    tableOrgStructure = db.table('OrgStructure')
    tableClientPolicy = db.table('ClientPolicy')
    tableRbPolicyType = db.table('rbPolicyType')
    tableOrganisation = db.table('Organisation')
    tableRealActionType_Service = db.table('ActionType_Service').alias('RealActionType_Service')
    tableContract_Tariff = db.table('Contract_Tariff')
    tableVrbPersonWithSpeciality = db.table('vrbPersonWithSpeciality')

    cols = [
        tableVrbPersonWithSpeciality['name'].alias('doctorName'),
        tableVrbPersonWithSpeciality['orgStructure_id'].alias('orgStructureId'),
        tableRealActionType['code'].alias('serviceCode'),
        tableRealActionType['name'].alias('serviceName'),
        '''SUM(RealAction.`amount`)         AS amount''',
        tableContract_Tariff['price'].alias('price'),
        '''IF(RealAction.customSum != 0, RealAction.customSum, SUM(RealAction.amount) * Contract_Tariff.price) as sum'''
    ]

    queryTable = tableEvent.innerJoin(tableRealAction, tableEvent['id'].eq(tableRealAction['event_id']))
    queryTable = queryTable.innerJoin(tableRealActionType, [tableRealAction['actionType_id'].eq(tableRealActionType['id']), tableRealActionType['flatCode'].ne('moving')])
    queryTable = queryTable.innerJoin(tableMovingAction, tableEvent['id'].eq(tableMovingAction['event_id']))
    queryTable = queryTable.innerJoin(tableMovingActionType, [tableMovingAction['actionType_id'].eq(tableMovingActionType['id']), tableMovingActionType['flatCode'].eq('moving')])

    #JOIN OrgStruct
    queryTable = queryTable.innerJoin(tableMovingActionPropertyType, [tableMovingActionType['id'].eq(tableMovingActionPropertyType['actionType_id']), tableMovingActionPropertyType['name'].eq(u'Отделение пребывания')])
    queryTable = queryTable.innerJoin(tableMovingActionProperty, [tableMovingActionPropertyType['id'].eq(tableMovingActionProperty['type_id']), tableMovingAction['id'].eq(tableMovingActionProperty['action_id'])])
    queryTable = queryTable.innerJoin(tableMovingActionProperty_OrgStructure, tableMovingActionProperty['id'].eq(tableMovingActionProperty_OrgStructure['id']))
    queryTable = queryTable.innerJoin(tableOrgStructure, tableMovingActionProperty_OrgStructure['value'].eq(tableOrgStructure['id']))

    #JOIN Organisation AND rbPolicyType
    queryTable = queryTable.innerJoin(tableClientPolicy, tableEvent['client_id'].eq(tableClientPolicy['client_id']))
    queryTable = queryTable.innerJoin(tableRbPolicyType, tableClientPolicy['policyType_id'].eq(tableRbPolicyType['id']))
    queryTable = queryTable.innerJoin(tableOrganisation, tableClientPolicy['insurer_id'].eq(tableOrganisation['id']))

    #JOIN Contract_Tariff
    queryTable = queryTable.innerJoin(tableRealActionType_Service, tableRealActionType['id'].eq(tableRealActionType_Service['master_id']))
    queryTable = queryTable.innerJoin(tableContract_Tariff, [
        tableRealActionType_Service['service_id'].eq(tableContract_Tariff['service_id']),
        tableRealAction['contract_id'].eq(tableContract_Tariff['master_id']),
        '''Event.`eventType_id` = IFNULL(Contract_Tariff.`eventType_id`, Event.`eventType_id`)''',
        '''RealAction.`endDate` BETWEEN IFNULL(Contract_Tariff.`begDate`, '0001-01-01') AND IFNULL(Contract_Tariff.`endDate`, '9999-01-01')'''
    ])

    queryTable = queryTable.innerJoin(tableVrbPersonWithSpeciality, tableRealAction['person_id'].eq(tableVrbPersonWithSpeciality['id']))

    where = [
        tableEvent['deleted'].eq(0),
        tableEvent['eventType_id'].eq(84),
        tableEvent['execDate'].isNotNull(),
        '''RealAction.`endDate` BETWEEN MovingAction.`begDate` AND MovingAction.`endDate`''',
        tableRbPolicyType['name'].like(u'ДМС')
    ]

    if begDate and endDate:
        where.append(tableEvent['execDate'].between(QtCore.QDateTime(begDate, QtCore.QTime(0,0,0)), QtCore.QDateTime(endDate, QtCore.QTime(23, 59, 59))))
    if contractIds:
        where.append(tableRealAction['contract_id'].inlist(contractIds))
    if organisationId:
        where.append(tableOrganisation['id'].eq(organisationId))
    if orgStructId:
        where.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructId)))
    if personId:
        where.append(tableVrbPersonWithSpeciality['id'].eq(personId))

    group = [tableVrbPersonWithSpeciality['id'], tableRealActionType['code']]

    order = [tableVrbPersonWithSpeciality['id'], tableRealActionType['code']]

    stmt = db.selectStmt(queryTable, cols, where=where, order=order, group=group)
    return db.query(stmt)

class ServiceRecord:
    def __init__(self, code, name, amount, price, sum):
        self.code = code
        self.name = name
        self.amount = amount
        self.price = price
        self.sum = sum

class DoctorRecord:
    def __init__(self, name, service):
        self.name = name
        self.amount = 0
        self.sum = 0
        self.services = []
        if service: self.addService(service)

    def addService(self, service):
        self.amount += service.amount
        self.sum += service.sum
        self.services.append(service)

class MasterRecord:
    def __init__(self):
        self.doctors = []
        self.amount = 0
        self.sum = 0

    def currDoctorName(self):
        if not self.doctors: return None
        else: return self.doctors[-1].name

    def addElement(self, orgName, service):
        if orgName == self.currDoctorName(): self.doctors[-1].addService(service)
        else: self.doctors.append(DoctorRecord(orgName, service))
        self.amount += service.amount
        self.sum += service.sum

def buildTable(table, masterRecord):
    for doctor in masterRecord.doctors:
        row = table.addRow()
        table.mergeCells(row, 0, 1, 5)
        table.setText(row, 0, doctor.name, fontBold=True)

        for service in doctor.services:
            row = table.addRow()
            table.setText(row, 0, service.code)
            table.setText(row, 1, service.name)
            table.setText(row, 2, service.amount)
            table.setText(row, 3, service.price)
            table.setText(row, 4, service.sum)

        row = table.addRow()
        table.setText(row, 0, u'Итого по врачу', fontBold=True)
        table.setText(row, 2, doctor.amount)
        table.setText(row, 4, doctor.sum)

    row = table.addRow()
    table.setText(row, 0, u'Всего', fontBold=True)
    table.setText(row, 2, masterRecord.amount)
    table.setText(row, 4, masterRecord.sum)

class CReportOrgByDoctor(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Анализ нагрузки на врачей')

    def getSetupDialog(self, parent):
        return CReportOrgByDoctorSetupDialog(parent=parent, title=self.title())

    def dumpParams(self, cursor, params, charFormat = QtGui.QTextCharFormat()):
        description = self.getDescription(params)

        description.append(u'Тип финансирования: ДМС')
        description.append(u'Плательщик: ' + getOrganisationShortName(params.get('organisationId', u'Все')))
        description.append(u'Подразделение пребывания пациента: ' + getOrgStructureName(params.get('orgStructId', u'Все')))

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
            ('30%',         [u'Код услуги'],                    CReportBase.AlignLeft),
            ('30%',         [u'Наименование услуги'],           CReportBase.AlignLeft),
            ('10%',         [u'Кол-во'],                        CReportBase.AlignLeft),
            ('10%',         [u'Цена за ед.'],                   CReportBase.AlignLeft),
            ('20%',         [u'Сумма'],                         CReportBase.AlignLeft)
        ]

        table = createTable(cursor, tableColumns)

        masterRecord = MasterRecord()
        while query.next():
            record = query.record()
            doctorName = forceString(record.value('doctorName')) + ', ' + getOrgStructureName(record.value('orgStructureId'))
            service = ServiceRecord(
                forceString(record.value('serviceCode')),
                forceString(record.value('serviceName')),
                forceInt(record.value('amount')),
                forceInt(record.value('price')),
                forceInt(record.value('sum'))
            )
            masterRecord.addElement(doctorName, service)

        buildTable(table, masterRecord)

        return doc

class CReportOrgByDoctorSetupDialog(QtGui.QDialog, Ui_ReportOrgByDoctorSetupDialog):
    def __init__(self, parent=None, title=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setTitle(title)
        self.cmbContract.setFinanceTypeCodes([CFinanceType.VMI])

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        currentDate = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate(currentDate.year(), currentDate.month(), 1)))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate(currentDate.year(), currentDate.month(), currentDate.daysInMonth())))
        self.cmbOrganisation.setValue(params.get('organisationId', None))
        self.cmbOrgStruct.setValue(params.get('orgStructId', None))
        self.cmbPerson.setValue(params.get('personId', None))

    def params(self):
        return \
            {
                'begDate'           : self.edtBegDate.date(),
                'endDate'           : self.edtEndDate.date(),
                'orgStructId'       : self.cmbOrgStruct.value(),
                'contractIds'       : self.cmbContract.getIdList(),
                'organisationId'    : self.cmbOrganisation.value(),
                'personId'          : self.cmbPerson.value()
            }

    @QtCore.pyqtSlot()
    def on_buttonBox_accepted(self):
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
                      'host' : 'bsvgvm',
                      'port' : 3306,
                      'database' : 's11',
                      'user' : 'dbuser',
                      'password' : 'dbpassword',
                      'connectionName' : 'vista-med',
                      'compressData' : True,
                      'afterConnectFunc' : None}
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    CReportOrgByDoctor(None).exec_()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
