# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
from Orgs.Utils import getOrgStructureName, getOrgStructureDescendants
from Reports.Report import CReport
from Reports.ReportBase import CReportBase, createTable
from Reports.StGeorge.Ui_ReportReceivedPatientsSetup import Ui_ReportReceivedPatientsSetupDialog
from library.Utils import forceString, formatSex, forceDate, calcAgeInYears, forceDateTime


def selectData(params):
    db = QtGui.qApp.db
    begDateTime         = params.get('begDateTime'          )
    endDateTime         = params.get('endDateTime'          )
    orgStructId     = params.get('orgStructId'      )

    tableEvent = db.table('Event')
    tableMovingAction = db.table('Action').alias('MovingAction')
    tableMovingActionType = db.table('ActionType').alias('MovingActionType')
    tableClient = db.table('Client')
    tableClientDocument = db.table('ClientDocument')
    tableRbDocumentType = db.table('rbDocumentType')
    tableClientWork = db.table('ClientWork')
    tableDMSClientPolicy = db.table('ClientPolicy').alias('DMSClientPolicy')
    tableDMSRbPolicyType = db.table('rbPolicyType').alias('DMSRbPolicyType')
    tableDMSRbPolicyKind = db.table('rbPolicyKind').alias('DMSRbPolicyKind')
    tableDMSOrganisation = db.table('Organisation').alias('DMSOrganisation')
    tableOMSClientPolicy = db.table('ClientPolicy').alias('OMSClientPolicy')
    tableOMSRbPolicyType = db.table('rbPolicyType').alias('OMSRbPolicyType')
    tableOMSRbPolicyKind = db.table('rbPolicyKind').alias('OMSRbPolicyKind')
    tableOMSOrganisation = db.table('Organisation').alias('OMSOrganisation')
    tableMovingActionPropertyType = db.table('ActionPropertyType').alias('MovingActionPropertyType')
    tableMovingActionProperty = db.table('ActionProperty').alias('MovingActionProperty')
    tableMovingActionProperty_OrgStructure = db.table('ActionProperty_OrgStructure').alias('MovingActionProperty_OrgStructure')
    tableOrgStructure = db.table('OrgStructure')
    tableReceivedAction = db.table('Action').alias('ReceivedAction')
    tableReceivedActionType = db.table('ActionType').alias('ReceivedActionType')
    tableReceivedActionPropertyType1 = db.table('ActionPropertyType').alias('ReceivedActionPropertyType1')
    tableReceivedActionProperty1 = db.table('ActionProperty').alias('ReceivedActionProperty1')
    tableReceivedActionProperty_String1 = db.table('ActionProperty_String').alias('ReceivedActionProperty_String1')
    tableReceivedActionPropertyType2 = db.table('ActionPropertyType').alias('ReceivedActionPropertyType2')
    tableReceivedActionProperty2 = db.table('ActionProperty').alias('ReceivedActionProperty2')
    tableReceivedActionProperty_String2 = db.table('ActionProperty_String').alias('ReceivedActionProperty_String2')
    tableReceivedActionPropertyType3 = db.table('ActionPropertyType').alias('ReceivedActionPropertyType3')
    tableReceivedActionProperty3 = db.table('ActionProperty').alias('ReceivedActionProperty3')
    tableReceivedActionProperty_Organisation = db.table('ActionProperty_Organisation').alias('ReceivedActionProperty_Organisation')
    tableReceivedOrganisation = db.table('Organisation').alias('ReceivedOrganisation')

    cols = [
        tableEvent['externalId'],
        tableClient['lastName'],
        tableClient['firstName'],
        tableClient['patrName'],
        tableClient['sex'],
        tableClient['birthDate'],
        tableReceivedAction['begDate'].alias('receivedDate'),
        tableMovingAction['begDate'].alias('movingDate'),
        tableMovingAction['endDate'].alias('endMovingDate'),
        tableOrgStructure['name'].alias('orgStructName'),
        tableRbDocumentType['name'].alias('documentName'),
        tableClientDocument['serial'].alias('documentSerial'),
        tableClientDocument['number'].alias('documentNumber'),
        tableClientDocument['date'].alias('documentDate'),
        tableClientDocument['origin'].alias('documentOrigin'),
        '''getClientLocAddress(Client.`id`) AS locAddress''',
        '''getClientRegAddress(Client.`id`) AS regAddress''',
        '''CONCAT_WS(' ', DMSRbPolicyType.`name`, DMSRbPolicyKind.`name`, DMSOrganisation.`shortName`, DMSClientPolicy.`serial`, DMSClientPolicy.`number`, DMSClientPolicy.`begDate`) AS DMS''',
        '''CONCAT_WS(' ', OMSRbPolicyType.`name`, OMSRbPolicyKind.`name`, OMSOrganisation.`shortName`, OMSClientPolicy.`serial`, OMSClientPolicy.`number`, OMSClientPolicy.`begDate`) AS OMS''',
        tableClientWork['freeInput'].alias('work'),
        tableReceivedOrganisation['shortName'].alias('receivedName'),
        tableReceivedActionProperty_String1['value'].alias('fromD'),
        tableReceivedActionProperty_String2['value'].alias('toD')
    ]

    queryTable = tableEvent.leftJoin(tableMovingAction,
        '''MovingAction.id = (
    SELECT
      Action.id
    FROM Action
      INNER JOIN ActionType ON Action.actionType_id = ActionType.id AND ActionType.flatCode = 'moving'
    WHERE
      Event.id = Action.event_id
    GROUP BY Event.id
    HAVING MAX(Action.begDate)
    )'''
    )
    queryTable = queryTable.leftJoin(tableMovingActionType, tableMovingAction['actionType_id'].eq(tableMovingActionType['id']))

    queryTable = queryTable.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
    queryTable = queryTable.innerJoin(tableClientDocument, tableClient['id'].eq(tableClientDocument['client_id']))
    queryTable = queryTable.innerJoin(tableRbDocumentType, tableClientDocument['documentType_id'].eq(tableRbDocumentType['id']))
    queryTable = queryTable.leftJoin(tableClientWork, tableClient['id'].eq(tableClientWork['client_id']))

    #JOIN Policy
    queryTable = queryTable.innerJoin(tableDMSClientPolicy, tableClient['id'].eq(tableDMSClientPolicy['client_id']))
    queryTable = queryTable.innerJoin(tableDMSRbPolicyType, [tableDMSClientPolicy['policyType_id'].eq(tableDMSRbPolicyType['id']), tableDMSRbPolicyType['name'].like(u'ДМС')])
    queryTable = queryTable.leftJoin(tableDMSRbPolicyKind, tableDMSClientPolicy['policyKind_id'].eq(tableDMSRbPolicyKind['id']))
    queryTable = queryTable.innerJoin(tableDMSOrganisation, tableDMSClientPolicy['insurer_id'].eq(tableDMSOrganisation['id']))
    queryTable = queryTable.leftJoin(tableOMSClientPolicy, tableClient['id'].eq(tableOMSClientPolicy['client_id']))
    queryTable = queryTable.leftJoin(tableOMSRbPolicyType, [tableOMSClientPolicy['policyType_id'].eq(tableOMSRbPolicyType['id']), tableOMSRbPolicyType['name'].like(u'ОМС%')])
    queryTable = queryTable.leftJoin(tableOMSRbPolicyKind, tableOMSClientPolicy['policyKind_id'].eq(tableOMSRbPolicyKind['id']))
    queryTable = queryTable.leftJoin(tableOMSOrganisation, tableOMSClientPolicy['insurer_id'].eq(tableOMSOrganisation['id']))

    #JOIN OrgStructure
    queryTable = queryTable.leftJoin(tableMovingActionPropertyType, [
        tableMovingActionType['id'].eq(tableMovingActionPropertyType['actionType_id']),
        tableMovingActionPropertyType['name'].eq(u'Отделение пребывания')
    ])
    queryTable = queryTable.leftJoin(tableMovingActionProperty, [
        tableMovingActionPropertyType['id'].eq(tableMovingActionProperty['type_id']),
        tableMovingActionProperty['action_id'].eq(tableMovingAction['id'])
    ])
    queryTable = queryTable.leftJoin(tableMovingActionProperty_OrgStructure, tableMovingActionProperty['id'].eq(tableMovingActionProperty_OrgStructure['id']))
    queryTable = queryTable.leftJoin(tableOrgStructure, tableMovingActionProperty_OrgStructure['value'].eq(tableOrgStructure['id']))

    #Received
    queryTable = queryTable.innerJoin(tableReceivedAction, tableEvent['id'].eq(tableReceivedAction['event_id']))
    queryTable = queryTable.innerJoin(tableReceivedActionType, [tableReceivedAction['actionType_id'].eq(tableReceivedActionType['id']), tableReceivedActionType['flatCode'].eq('received')])
    queryTable = queryTable.leftJoin(tableReceivedActionPropertyType1, [
        tableReceivedActionType['id'].eq(tableReceivedActionPropertyType1['actionType_id']),
        tableReceivedActionPropertyType1['name'].eq(u'Диагноз направителя')
    ])
    queryTable = queryTable.leftJoin(tableReceivedActionProperty1, [tableReceivedActionPropertyType1['id'].eq(tableReceivedActionProperty1['type_id']), tableReceivedActionProperty1['action_id'].eq(tableReceivedAction['id'])])
    queryTable = queryTable.leftJoin(tableReceivedActionProperty_String1, tableReceivedActionProperty1['id'].eq(tableReceivedActionProperty_String1['id']))
    queryTable = queryTable.leftJoin(tableReceivedActionPropertyType2, [
        tableReceivedActionType['id'].eq(tableReceivedActionPropertyType2['actionType_id']),
        tableReceivedActionPropertyType2['name'].eq(u'Диагноз приемного отделения')
    ])
    queryTable = queryTable.leftJoin(tableReceivedActionProperty2, [tableReceivedActionPropertyType2['id'].eq(tableReceivedActionProperty2['type_id']), tableReceivedActionProperty2['action_id'].eq(tableReceivedAction['id'])])
    queryTable = queryTable.leftJoin(tableReceivedActionProperty_String2, tableReceivedActionProperty2['id'].eq(tableReceivedActionProperty_String2['id']))
    queryTable = queryTable.leftJoin(tableReceivedActionPropertyType3, [
        tableReceivedActionType['id'].eq(tableReceivedActionPropertyType3['actionType_id']),
        tableReceivedActionPropertyType3['name'].eq(u'Кем направлен')
    ])
    queryTable = queryTable.leftJoin(tableReceivedActionProperty3, [tableReceivedActionPropertyType3['id'].eq(tableReceivedActionProperty3['type_id']), tableReceivedActionProperty3['action_id'].eq(tableReceivedAction['id'])])
    queryTable = queryTable.leftJoin(tableReceivedActionProperty_Organisation, tableReceivedActionProperty3['id'].eq(tableReceivedActionProperty_Organisation['id']))
    queryTable = queryTable.leftJoin(tableReceivedOrganisation, tableReceivedActionProperty_Organisation['value'].eq(tableReceivedOrganisation['id']))

    where = [
        tableEvent['deleted'].eq(0),
        tableEvent['eventType_id'].eq(84)
    ]

    if begDateTime and endDateTime:
        where.append(tableReceivedAction['begDate'].between(begDateTime, endDateTime))
    if orgStructId:
        where.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructId)))

    order = [tableEvent['id']]
    group = [tableClient['id']]

    stmt = db.selectStmt(queryTable, cols, where=where, order=order, group=group)
    return db.query(stmt)

class CReportReceivedPatients(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Список поступивших пациентов')

    def getSetupDialog(self, parent):
        return CReportReceivedPatientsSetupDialog(parent=parent, title=self.title())

    def dumpParams(self, cursor, params, charFormat = QtGui.QTextCharFormat()):
        description = self.getDescription(params)

        description.append(u'Тип финансирования: ДМС')
        description.append(u'Отделение: ' + getOrgStructureName(params.get('orgStructId', u'Все')))
        description.append(u'За период: ' + forceDateTime(params.get('begDateTime')).toString('dd.MM.yyyy hh:mm') + u' по ' + forceDateTime(params.get('endDateTime')).toString('dd.MM.yyyy hh:mm'))

        columns = [ ('100%', [], CReportBase.AlignLeft) ]
        table = createTable(cursor, columns, headerRowCount=len(description), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(description):
            table.setText(i, 0, row, charFormat = charFormat)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()

    def build(self, params):
        def getPatientDesc(record):
            desc = ''
            desc += u'ИБ №' + (forceString(record.value('externalId'))       +   '\n')
            desc += (forceString(record.value('lastName'))         +   '\n')
            desc += (forceString(record.value('firstName'))        +   '\n')
            desc += (forceString(record.value('patrName'))         +   '\n')
            desc += u'Пол: ' + (formatSex(record.value('sex'))                +   '\n')
            date = forceDate(record.value('birthDate'))
            desc += u'Дата рождения: ' + (date.toString('dd.MM.yyyy') + u'(' + repr(calcAgeInYears(date, QtCore.QDate.currentDate())) + u' лет)\n')
            return desc

        def getOrgStruct(record):
            result = ''
            result += u'Текущие к/д: ' + repr((forceDate(record.value('movingDate'))).daysTo(forceDate(record.value('endMovingDate') if forceDate(record.value('endMovingDate')) != QtCore.QDate() else QtCore.QDate.currentDate()))) + '\n'
            result += (forceString(record.value('receivedDate')) + '\n')
            result += (forceString(record.value('movingDate')) + '\n')
            result += (forceString(record.value('orgStructName')) if forceString(record.value('orgStructName')) != '' else u'Приёмное отделение' + '\n')
            return result

        def getStuff(record):
            result = ''
            if params['flagDoc']: result += (   forceString(record.value('documentName'))   + ': '
                        + forceString(record.value('documentSerial')) + ' '
                        + forceString(record.value('documentNumber')) + ' '
                        + forceString(record.value('documentDate'))   + ' '
                        + forceString(record.value('documentOrigin')) + '\n')
            if params['flagAddressReg']: result += u'Адрес регистрации: ' + (forceString(record.value('regAddress')) + '\n')
            if params['flagAddress']: result += u'Адрес проживания: ' + (forceString(record.value('locAddress')) + '\n')
            if params['flagOMS']: result += u'ОМС: ' + (forceString(record.value('OMS')) + '\n')
            if params['flagDMS']: result += u'ДМС: ' + (forceString(record.value('DMS')) + '\n')
            if params['flagWork']: result += u'Место работы: ' + (forceString(record.value('work')) + '\n')
            if params['flagDir']: result += u'Кем направлен: ' + (forceString(record.value('receivedName')) + '\n')
            if params['flagDiagDir']: result += u'Д-з напр.: ' + (forceString(record.value('fromD')) + '\n')
            if params['flagDiag']: result += u'Д-з пост.: ' + (forceString(record.value('toD')) + '\n')
            return result


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
            (' 4%',      [u'№ п/п'],                       CReportBase.AlignLeft),
            ('32%',      [u'Данные пациента'],              CReportBase.AlignLeft),
            ('32%',      [u'Отделение пребывания'],         CReportBase.AlignLeft),
            ('32%',      [u'Данные пациента'],              CReportBase.AlignLeft)
        ]

        table = createTable(cursor, tableColumns)

        while query.next():
            record = query.record()
            row = table.addRow()
            chrf = QtGui.QTextCharFormat()
            chrf.setFontPointSize(12)
            table.setText(row, 0, row, charFormat=chrf)
            table.setText(row, 1, getPatientDesc(record), charFormat=chrf)
            table.setText(row, 2, getOrgStruct(record), charFormat=chrf)
            chrf.setFontPointSize(8)
            table.setText(row, 3, getStuff(record), charFormat=chrf)

        return doc

class CReportReceivedPatientsSetupDialog(QtGui.QDialog, Ui_ReportReceivedPatientsSetupDialog):
    def __init__(self, parent=None, title=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setTitle(title)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        currentDate = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(forceDate(params.get('begDateTime', QtCore.QDate(currentDate.year(), currentDate.month(), 1))))
        self.edtEndDate.setDate(forceDate(params.get('endDateTime', QtCore.QDate(currentDate.year(), currentDate.month(), currentDate.daysInMonth()))))
        self.cmbOrgStruct.setValue(params.get('orgStructId', None))


    def params(self):
        return \
            {
                'begDateTime'           : QtCore.QDateTime(self.edtBegDate.date(), self.edtBegTime.time()),
                'endDateTime'           : QtCore.QDateTime(self.edtEndDate.date(), self.edtEndTime.time()),
                'flagDoc'           : self.chkDoc.isChecked(),
                'flagAddress'       : self.chkAddress.isChecked(),
                'flagAddressReg'    : self.chkAddressReg.isChecked(),
                'flagDMS'            : self.chkDMS.isChecked(),
                'flagOMS'            : self.chkOMS.isChecked(),
                'flagDiag'           : self.chkDiag.isChecked(),
                'flagDiagDir'        : self.chkDiagDir.isChecked(),
                'flagDir'            : self.chkDir.isChecked(),
                'flagWork'           : self.chkWork.isChecked(),
                'orgStructId'       : self.cmbOrgStruct.value()
            }