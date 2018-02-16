# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
from Orgs.Utils import getOrganisationShortName, getOrgStructureName, getOrgStructureDescendants
from Reports.Report import CReport
from Reports.ReportBase import CReportBase, createTable
from Reports.StGeorge.Ui_ReportCurePatientsSetup import Ui_ReportCurePatientsSetupDialog
from library.Utils import forceString, forceInt, formatSex, forceDate


def selectData(params):
    db = QtGui.qApp.db
    begDate = params.get('begDate')
    endDate = params.get('endDate')
    orgStructId = params.get('orgStructId')
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
    tableClient = db.table('Client')
    tableMES = db.table('mes.MES')

    cols = [
        tableClient['id'].alias('clientId'),
        tableEvent['externalId'],
        '''CONCAT_WS(' ', Client.`lastName`, Client.`firstName`, Client.`patrName`) AS clientName''',
        tableClient['sex'],
        tableClient['birthDate'],
        tableEvent['setDate'],
        tableEvent['execDate'],
        tableMovingAction['MKB'],
        tableMES['name'].alias('KSG'),
        tableOrgStructure['name'].alias('orgStructName'),
        '''IF(RealAction.customSum != 0, RealAction.customSum, RealAction.amount * Contract_Tariff.price) AS sum'''
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

    queryTable = queryTable.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
    queryTable = queryTable.innerJoin(tableMES, tableMovingAction['MES_id'].eq(tableMES['id']))

    where = [
        tableEvent['deleted'].eq(0),
        tableEvent['eventType_id'].eq(84),
        tableEvent['execDate'].isNotNull(),
        '''RealAction.`endDate` BETWEEN MovingAction.`begDate` AND MovingAction.`endDate`''',
        tableRbPolicyType['name'].like(u'ДМС')
    ]

    if begDate and endDate:
        where.append(tableEvent['execDate'].between(QtCore.QDateTime(begDate, QtCore.QTime(0,0,0)), QtCore.QDateTime(endDate, QtCore.QTime(23, 59, 59))))
    if organisationId:
        where.append(tableOrganisation['id'].eq(organisationId))
    if orgStructId:
        where.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructId)))

    order = [tableClient['id']]

    stmt = db.selectStmt(queryTable, cols, where=where, order=order)
    return db.query(stmt)

class PatientRecord:
    def __init__(self, id, extId, name, sex, birthDate, period, MKB, KSG, org, sum):
        self.id = id
        self.extId = extId
        self.name = name
        self.sex = sex
        self.birthDate = birthDate
        self.period = period
        self.MKB = MKB
        self.KSG = KSG
        self.org = org
        self.sum = sum

    def add(self, sum):
        self.sum += sum

class MasterRecord:
    def __init__(self):
        self.patients = []
        self.sum = 0
        self.amount = 0

    def currPatientId(self):
        if not self.patients: return None
        else: return self.patients[-1].id

    def addElement(self, patient):
        if patient.id == self.currPatientId(): self.patients[-1].add(patient.sum)
        else:
            self.patients.append(patient)
            self.amount += 1

        self.sum += patient.sum

def buildTable(table, masterRecord):
    for patient in masterRecord.patients:
        row = table.addRow()
        table.setText(row, 0, patient.id)
        table.setText(row, 1, patient.extId)
        table.setText(row, 2, patient.name)
        table.setText(row, 3, patient.sex)
        table.setText(row, 4, patient.birthDate)
        table.setText(row, 5, patient.period)
        table.setText(row, 6, patient.MKB)
        table.setText(row, 7, patient.KSG)
        table.setText(row, 8, patient.org)
        table.setText(row, 9, patient.sum)


    row = table.addRow()
    table.mergeCells(row, 0, 1, 2)
    table.setText(row, 0, u'Всего')
    table.setText(row, 2, masterRecord.amount)
    table.setText(row, 9, masterRecord.sum)


class CReportCurePatients(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчет о пролеченных больных')

    def getSetupDialog(self, parent):
        return CReportCurePatientsSetupDialog(parent=parent, title=self.title())

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
            (' 9%',         [u'Код пациента'],                      CReportBase.AlignLeft),
            (' 9%',         [u'Внешний идентификатор'],             CReportBase.AlignLeft),
            ('20%',         [u'ФИО пациента'],                      CReportBase.AlignLeft),
            (' 5%',         [u'Пол'],                               CReportBase.AlignLeft),
            ('10%',         [u'Дата рождения'],                     CReportBase.AlignLeft),
            ('10%',         [u'Период лечения'],                    CReportBase.AlignLeft),
            (' 9%',         [u'Код МКБ'],                           CReportBase.AlignLeft),
            (' 9%',         [u'Стандарт/КСГ'],                      CReportBase.AlignLeft),
            ('10%',         [u'Отделение пребывания'],              CReportBase.AlignLeft),
            (' 9%',         [u'Сумма ДМС-ОМС'],                     CReportBase.AlignLeft),
        ]

        table = createTable(cursor, tableColumns)

        masterRecord = MasterRecord()
        while query.next():
            record = query.record()

            masterRecord.addElement(PatientRecord(
                forceString(record.value('clientId')),
                forceString(record.value('externalId')),
                forceString(record.value('clientName')),
                formatSex(record.value('sex')),
                forceDate(record.value('birthDate')).toString('dd.MM.yyyy'),
                forceDate(record.value('setDate')).toString('dd.MM.yyyy') + '/' + forceDate(record.value('execDate')).toString('dd.MM.yyyy'),
                forceString(record.value('MKB')),
                forceString(record.value('KSG')),
                forceString(record.value('orgStructName')),
                forceInt(record.value('sum'))
            ))

        buildTable(table, masterRecord)

        return doc

class CReportCurePatientsSetupDialog(QtGui.QDialog, Ui_ReportCurePatientsSetupDialog):
    def __init__(self, parent=None, title=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setTitle(title)
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
                'organisationId'    : self.cmbOrganisation.value()
            }

    @QtCore.pyqtSlot()
    def on_buttonBox_accepted(self):
        self.accept()