# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
from Events.Utils import CFinanceType
from Orgs.Utils import getOrganisationShortName, getOrgStructureName, getOrgStructureDescendants
from Reports.Report import CReport
from Reports.ReportBase import CReportBase, createTable
from Reports.StGeorge.Ui_ReportOrgByOrganisationSetup import Ui_ReportOrgByOrganisationSetupDialog
from library.Utils import forceString, forceInt, forceDate


def selectData(params):
    db = QtGui.qApp.db
    begDate = params.get('begDate')
    endDate = params.get('endDate')
    orgStructId = params.get('orgStructId')
    contractIds = params.get('contractIds')
    organisationId = params.get('organisationId')

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

    cols = [
        tableOrganisation['fullName'].alias('organisationName'),
        tableOrgStructure['name'].alias('orgStructureName'),
        tableMovingAction['endDate'].alias('endDate'),
        tableMovingAction['begDate'].alias('begDate'),
        tableEvent['client_id'].alias('clientId'),
        tableEvent['id'].alias('eventId'),
        '''IF(RealAction.customSum != 0, RealAction.customSum, RealAction.amount * Contract_Tariff.price) as sum'''

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

    order = [tableOrganisation['id'], tableOrgStructure['id'], tableEvent['client_id'], tableEvent['id']]

    stmt = db.selectStmt(queryTable, cols, where=where, order=order)
    return db.query(stmt)

class OrgStructRecord:
    def __init__(self, name = '', numDays = 0, sum = 0, clientId = -1, eventId = -1):
        self.name = name
        self.numPhys = 0 if clientId == -1 else 1
        self.numBills = 0 if eventId == -1 else 1
        self.numDays= numDays
        self.sum = sum
        self.currClientId = clientId
        self.currEventId = eventId

    def addElement(self, numDays, sum, clientId, eventId):
        self.sum += sum
        if clientId != self.currClientId:
            self.numPhys += 1
            self.numBills += 1
            self.numDays += numDays
            self.currClientId = clientId
            self.currEventId = eventId
        elif eventId != self.currEventId:
            self.numBills += 1
            self.numDays += numDays
            self.currEventId = eventId

    def __unicode__(self):
        return '%s; %i; %i; %i; %i;' % self.name, self.numPhys, self.numBills, self.numDays, self.sum

class OrganisationRecord:
    def __init__(self, name, nameOrgStruct, numDays, sum, clientId, eventId):
        self.orgStructures = []
        self.sumPhys = 0
        self.sumBills = 0
        self.sumDays = 0
        self.sum = 0
        self.name = name
        self.addStructure(nameOrgStruct, numDays, sum, clientId, eventId)

    def currOrgStructName(self):
        if not self.orgStructures: return None
        else: return self.orgStructures[-1].name

    def addStructure(self, name, numDays, sum, clientId, eventId):
        if name != self.currOrgStructName():
            if self.orgStructures:
                self.sumPhys += self.orgStructures[-1].numPhys
                self.sumBills += self.orgStructures[-1].numBills
                self.sumDays += self.orgStructures[-1].numDays
                self.sum += self.orgStructures[-1].sum
            self.orgStructures.append(OrgStructRecord(name, numDays, sum, clientId, eventId))
        else:
            self.orgStructures[-1].addElement(numDays, sum, clientId, eventId)

    def end(self):
        if self.orgStructures:
                self.sumPhys +=  self.orgStructures[-1].numPhys
                self.sumBills += self.orgStructures[-1].numBills
                self.sumDays +=  self.orgStructures[-1].numDays
                self.sum +=      self.orgStructures[-1].sum

    def __unicode__(self):
        return reduce(lambda res, x: (res + x + '\n'), self.orgStructures, u'') + '\n'

class MasterRecord:
    def __init__(self):
        self.organisations = []
        self.sumPhys = 0
        self.sumBills = 0
        self.sumDays = 0
        self.sum = 0

    def currOrganisationName(self):
        if not self.organisations: return None
        else: return self.organisations[-1].name

    def addElement(self, organisationName, nameOrgStruct, numDays, sum, clientId, eventId):
        if organisationName == self.currOrganisationName(): self.organisations[-1].addStructure(nameOrgStruct, numDays, sum, clientId, eventId)
        else:
            if self.organisations:
                self.organisations[-1].end()
                self.sumPhys +=     self.organisations[-1].sumPhys
                self.sumBills +=    self.organisations[-1].sumBills
                self.sumDays +=     self.organisations[-1].sumDays
                self.sum +=         self.organisations[-1].sum
            self.organisations.append(OrganisationRecord(organisationName, nameOrgStruct, numDays, sum, clientId, eventId))

    def end(self):
        if self.organisations:
            self.organisations[-1].end()
            self.sumPhys +=     self.organisations[-1].sumPhys
            self.sumBills +=    self.organisations[-1].sumBills
            self.sumDays +=     self.organisations[-1].sumDays
            self.sum +=         self.organisations[-1].sum

    def __unicode__(self):
        return reduce(lambda res, x: (res + x + '\n'), map(lambda x: unicode(x), self.organisations), u'') + '\n'

def buildTable(table, masterRecord):
    for organ in masterRecord.organisations:
        row = table.addRow()
        table.mergeCells(row, 0, 1, 5)
        table.setText(row, 0, organ.name)

        for orgStruct in organ.orgStructures:
            row = table.addRow()
            table.setText(row, 0, orgStruct.name)
            table.setText(row, 1, orgStruct.numPhys)
            table.setText(row, 2, orgStruct.numBills)
            table.setText(row, 3, orgStruct.numDays)
            table.setText(row, 4, orgStruct.sum)

        row = table.addRow()
        table.setText(row, 0, u'Итого по плательщику')
        table.setText(row, 1, organ.sumPhys)
        table.setText(row, 2, organ.sumBills)
        table.setText(row, 3, organ.sumDays)
        table.setText(row, 4, organ.sum)

    row = table.addRow()
    table.setText(row, 0, u'Всего')
    table.setText(row, 1, masterRecord.sumPhys)
    table.setText(row, 2, masterRecord.sumBills)
    table.setText(row, 3, masterRecord.sumDays)
    table.setText(row, 4, masterRecord.sum)

class CReportOrgByOrganisation(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Анализ нагрузки на отделение по плательщикам')

    def getSetupDialog(self, parent):
        return CReportOrgByOrganisationSetupDialog(parent=parent, title=self.title())

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
            ('30%',         [u'Отделение'],                     CReportBase.AlignLeft),
            ('14%',         [u'Кол-во физ. лиц'],               CReportBase.AlignLeft),
            ('13%',         [u'Кол-во п/счетов'],               CReportBase.AlignLeft),
            ('13%',         [u'Кол-во к/д'],                    CReportBase.AlignLeft),
            ('30%',         [u'Сумма ДМС-ОМС'],                 CReportBase.AlignLeft)
        ]

        table = createTable(cursor, tableColumns)

        masterRecord = MasterRecord()
        while query.next():
            record = query.record()
            organisationName = forceString(record.value('organisationName'))
            masterRecord.addElement(organisationName,
                                    forceString(record.value('orgStructureName')),
                                    forceDate(record.value('begDate')).daysTo(forceDate(record.value('endDate'))),
                                    forceInt(record.value('sum')),
                                    forceInt(record.value('clientId')),
                                    forceInt(record.value('eventId')))

        masterRecord.end()
        buildTable(table, masterRecord)

        return doc

class CReportOrgByOrganisationSetupDialog(QtGui.QDialog, Ui_ReportOrgByOrganisationSetupDialog):
    def __init__(self, parent=None, title=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setTitle(title)
        self.cmbContract.setFinanceTypeCodes([CFinanceType.VMI])
        cond = [
            QtGui.qApp.db.table('Organisation')['area'].eq(QtGui.qApp.defaultKLADR()),
            QtGui.qApp.db.table('Organisation')['isInsurer'].eq(1)
        ]
        self.cmbOrganisation.setFilter(QtGui.qApp.db.joinAnd(cond))

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        currentDate = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate(currentDate.year(), currentDate.month(), 1)))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate(currentDate.year(), currentDate.month(), currentDate.daysInMonth())))
        self.cmbOrganisation.setValue(params.get('organisationId', None))
        self.cmbOrgStruct.setValue(params.get('orgStructId', None))

    def params(self):
        return \
            {
                'begDate'           : self.edtBegDate.date(),
                'endDate'           : self.edtEndDate.date(),
                'orgStructId'       : self.cmbOrgStruct.value(),
                'contractIds'       : self.cmbContract.getIdList(),
                'organisationId'    : self.cmbOrganisation.value()
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

    CReportOrgByOrganisation(None).exec_()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()