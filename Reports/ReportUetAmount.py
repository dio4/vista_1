# -*- coding: utf-8 -*-
#from KLADRUpdate.KLADRUtils import queryDb
from Reports.ReportBase import CReportBase, createTable

from Reports.Ui_ReportUetAmountSetup import Ui_ReportAmountSetup
from Reports.Report import CReport
from PyQt4 import QtCore, QtGui
from library.Utils import getVal, forceInt, forceString, forceDouble
from Orgs.Utils import getOrgStructureDescendants, getOrgStructures

def selectColumns(params):
    db = QtGui.qApp.db
    orgId = params.get('orgStructureId')

    tableOrgStructure = db.table('OrgStructure')
    tableOrgStructure_ActionType = db.table('OrgStructure_ActionType')
    tableActionType = db.table('ActionType')
    tableAction = db.table('Action')
    begDate = params.get('begDate')
    endDate = params.get('endDate')

    cond = []
    if begDate and endDate:
        cond.append(tableAction['begDate'].dateLe(endDate))
        cond.append(tableAction['endDate'].dateGe(begDate))

    if orgId:
        cond.append(tableOrgStructure['id'].eq(129))

    cols = [
        tableActionType['name'],
        tableActionType['UetDoctor'],
        tableActionType['id'].alias('actionType_id')
    ]

    queryTable = tableOrgStructure.innerJoin(tableOrgStructure_ActionType, tableOrgStructure['id'].eq(tableOrgStructure_ActionType['master_id']))
    queryTable = queryTable.innerJoin(tableActionType, tableOrgStructure_ActionType['actionType_id'].eq(tableActionType['id']))
    queryTable = queryTable.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))

    group = [
        tableActionType['id']
    ]

    stmt = db.selectStmt(queryTable, cols, where=cond, group=group)
    return db.query(stmt)

def selectLinesAndData(params):
    db = QtGui.qApp.db

    listUetActionIds = params.get('idList')
    personId = params.get('personId')
    orgId = params.get('orgStructureId')
    begDate = params.get('begDate')
    endDate = params.get('endDate')

    tableEvent = db.table('Event')
    tableAction = db.table('Action')
    tableUetActionType = db.table('ActionType').alias('UetActionType')
    tableActionProperty = db.table('ActionProperty')
    tableActionPropertyType = db.table('ActionPropertyType')
    tableActionPropertyOrgStructure = db.table('ActionProperty_OrgStructure')
    tableMovingAction = tableAction.alias('MovingAction')
    tableUetAction = tableAction.alias('UetAction')
    tablePerson = db.table('Person')
    tableOrgStructure = db.table('OrgStructure')

    cond = []
    cond.append(tableActionPropertyType['name'].eq(u'отделение пребывания'))
    cond.append(tableUetAction['amount'].ne(0))
    cond.append(tableOrgStructure['name'].notlike(u'%ультразвуковой и функциональной диагностики%'))
    if personId:
        cond.append(tablePerson['id'].eq(personId))
    if begDate and endDate:
        cond.append(tableUetAction['begDate'].dateLe(endDate))
        cond.append(tableUetAction['endDate'].dateGe(begDate))
    if orgId:
        cond.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgId)))
    elif orgId == None:
        allOrgId = getOrgStructures(QtGui.qApp.currentOrgId())
        cond.append(tableOrgStructure['id'].inlist(allOrgId))

    cols = [
        tableUetAction['amount'],
        tableUetAction['actionType_id'].alias('actionType_id'),
        tableActionPropertyOrgStructure['value'].alias('orgStructure_id'),
        '''SUM(IFNULL(UetActionType.`UetDoctor` * UetAction.`amount`, 0)) AS `sum`''',
        tableOrgStructure['name'].alias('orgStructureName')
    ]

    queryTable = tableEvent.innerJoin(tableMovingAction, [
        '''
        MovingAction.id = (
    SELECT
      max(Action.id)
    FROM
      Action
      INNER JOIN ActionType ON Action.actionType_id = ActionType.id
    WHERE
      ActionType.flatCode = 'moving'
      AND Action.deleted = 0
      AND Action.event_id = Event.id
  )
        '''
    ])
    queryTable = queryTable.innerJoin(tablePerson, [tableEvent['execPerson_id'].eq(tablePerson['id'])])
    queryTable = queryTable.innerJoin(tableActionProperty, [tableMovingAction['id'].eq(tableActionProperty['action_id'])])
    queryTable = queryTable.innerJoin(tableActionPropertyType, [tableActionPropertyType['id'].eq(tableActionProperty['type_id'])])
    queryTable = queryTable.innerJoin(tableActionPropertyOrgStructure, [tableActionProperty['id'].eq(tableActionPropertyOrgStructure['id'])])
    queryTable = queryTable.innerJoin(tableUetAction, [tableUetAction['event_id'].eq(tableEvent['id']), tableUetAction['actionType_id'].inlist(listUetActionIds)])
    queryTable = queryTable.innerJoin(tableUetActionType, [tableUetActionType['id'].eq(tableUetAction['actionType_id'])])
    queryTable = queryTable.innerJoin(tableOrgStructure, [tableActionPropertyOrgStructure['value'].eq(tableOrgStructure['id'])])

    group = [tableUetAction['actionType_id'], tableActionPropertyOrgStructure['value']]
    order = ['orgStructure_id']

    stmt = db.selectStmt(queryTable, cols, where=cond, group=group, order=order)
    return db.query(stmt)

def selectStaffers(params):
    db = QtGui.qApp.db
    #TODO: skkachaev: правильно ли я понял?
    orgId = params.get('orgStructureId')

    personId = params.get('personId')
    listUetActionIds = params.get('idList')
    begDate = params.get('begDate')
    endDate = params.get('endDate')

    tableEvent = db.table('Event')
    tableAction = db.table('Action')
    tableUetActionType = db.table('ActionType').alias('UetActionType')
    tableActionProperty = db.table('ActionProperty')
    tableActionPropertyType = db.table('ActionPropertyType')
    tableActionPropertyOrgStructure = db.table('ActionProperty_OrgStructure')
    tableMovingAction = tableAction.alias('MovingAction')
    tableUetAction = tableAction.alias('UetAction')
    tablePerson = db.table('Person')
    tableClientWork = db.table('ClientWork')

    cond = []
    cond.append(tableUetAction['amount'].ne(0))
    if orgId:
        cond.append(tableClientWork['org_id'].eq(orgId))
    if personId:
        cond.append(tablePerson['id'].eq(personId))
    if begDate and endDate:
        cond.append(tableUetAction['begDate'].dateLe(endDate))
        cond.append(tableUetAction['endDate'].dateGe(begDate))

    cols = [
        tableUetAction['actionType_id'].alias('actionType_id'),
        '''SUM(IFNULL(UetActionType.`UetDoctor` * UetAction.`amount`, 0)) AS `sum`''',
    ]

    queryTable = tableEvent.innerJoin(tableMovingAction, [
        '''
        MovingAction.id = (
    SELECT
      max(Action.id)
    FROM
      Action
      INNER JOIN ActionType ON Action.actionType_id = ActionType.id
    WHERE
      ActionType.flatCode = 'moving'
      AND Action.deleted = 0
      AND Action.event_id = Event.id
  )
        '''
    ])
    queryTable = queryTable.innerJoin(tablePerson, [tableEvent['execPerson_id'].eq(tablePerson['id'])])
    queryTable = queryTable.innerJoin(tableActionProperty, [tableMovingAction['id'].eq(tableActionProperty['action_id'])])
    queryTable = queryTable.innerJoin(tableActionPropertyType, [tableActionPropertyType['id'].eq(tableActionProperty['type_id'])])
    queryTable = queryTable.innerJoin(tableActionPropertyOrgStructure, [tableActionProperty['id'].eq(tableActionPropertyOrgStructure['id'])])
    queryTable = queryTable.innerJoin(tableUetAction, [tableUetAction['event_id'].eq(tableEvent['id']), tableUetAction['actionType_id'].inlist(listUetActionIds)])
    queryTable = queryTable.innerJoin(tableUetActionType, [tableUetActionType['id'].eq(tableUetAction['actionType_id'])])
    queryTable = queryTable.innerJoin(tableClientWork, [tableClientWork['id'].eq('''getClientWorkId(Event.`client_id`)''')])

    group = [tableUetAction['actionType_id']]

    stmt = db.selectStmt(queryTable, cols, where=cond, group=group)
    return db.query(stmt)

def selectNotOMS(params):
    db = QtGui.qApp.db
    personId = params.get('personId')
    listUetActionIds = params.get('idList')
    begDate = params.get('begDate')
    endDate = params.get('endDate')

    tableEvent = db.table('Event')
    tableAction = db.table('Action')
    tableUetActionType = db.table('ActionType').alias('UetActionType')
    tableActionProperty = db.table('ActionProperty')
    tableActionPropertyType = db.table('ActionPropertyType')
    tableActionPropertyOrgStructure = db.table('ActionProperty_OrgStructure')
    tableMovingAction = tableAction.alias('MovingAction')
    tableUetAction = tableAction.alias('UetAction')
    tablePerson = db.table('Person')
    tableRbFinance = db.table('rbFinance')

    cond = []
    cond.append(tableUetAction['amount'].ne(0))
    #TODO: skkachaev: заменить на нормальное (не хардкод-строкой) условие
    cond.append(
        '''rbFinance.`code` = 3 OR rbFinance.`code` = 4'''
    )
    if personId:
        cond.append(tablePerson['id'].eq(personId))
    if begDate and endDate:
        cond.append(tableUetAction['begDate'].dateLe(endDate))
        cond.append(tableUetAction['endDate'].dateGe(begDate))

    cols = [
        tableUetAction['actionType_id'].alias('actionType_id'),
        '''SUM(IFNULL(UetActionType.`UetDoctor` * UetAction.`amount`, 0)) AS `sum`''',
    ]

    queryTable = tableEvent.innerJoin(tableMovingAction, [
        '''
        MovingAction.id = (
    SELECT
      max(Action.id)
    FROM
      Action
      INNER JOIN ActionType ON Action.actionType_id = ActionType.id
    WHERE
      ActionType.flatCode = 'moving'
      AND Action.deleted = 0
      AND Action.event_id = Event.id
  )
        '''
    ])
    queryTable = queryTable.innerJoin(tablePerson, [tableEvent['execPerson_id'].eq(tablePerson['id'])])
    queryTable = queryTable.innerJoin(tableActionProperty, [tableMovingAction['id'].eq(tableActionProperty['action_id'])])
    queryTable = queryTable.innerJoin(tableActionPropertyType, [tableActionPropertyType['id'].eq(tableActionProperty['type_id'])])
    queryTable = queryTable.innerJoin(tableActionPropertyOrgStructure, [tableActionProperty['id'].eq(tableActionPropertyOrgStructure['id'])])
    queryTable = queryTable.innerJoin(tableUetAction, [tableUetAction['event_id'].eq(tableEvent['id']), tableUetAction['actionType_id'].inlist(listUetActionIds)])
    queryTable = queryTable.innerJoin(tableUetActionType, [tableUetActionType['id'].eq(tableUetAction['actionType_id'])])
    queryTable = queryTable.innerJoin(tableRbFinance, [tableUetAction['finance_id'].eq(tableRbFinance['id'])])

    group = [tableUetAction['actionType_id']]

    stmt = db.selectStmt(queryTable, cols, where=cond, group=group)
    return db.query(stmt)

def selectOMS(params):
    db = QtGui.qApp.db
    personId = params.get('personId')
    listUetActionIds = params.get('idList')
    begDate = params.get('begDate')
    endDate = params.get('endDate')

    tableEvent = db.table('Event')
    tablePerson = db.table('Person')
    tableEventType = db.table('EventType')
    tableRbMedicalAidType = db.table('rbMedicalAidType')
    tableUetAction = db.table('Action').alias('UetAction')
    tableUetActionType = db.table('ActionType').alias('UetActionType')

    cond = []
    cond.append(tableUetAction['amount'].ne(0))
    if personId:
        cond.append(tablePerson['id'].eq(personId))
    if begDate and endDate:
        cond.append(tableUetAction['begDate'].dateLe(endDate))
        cond.append(tableUetAction['endDate'].dateGe(begDate))

    cols = [
        tableUetAction['amount'],
        tableUetAction['actionType_id'].alias('actionType_id'),
        '''SUM(IFNULL(UetActionType.`UetDoctor` * UetAction.`amount`, 0)) AS `sum`''',
    ]

    queryTable = tableEvent.innerJoin(tablePerson, [tableEvent['execPerson_id'].eq(tablePerson['id'])])
    queryTable = queryTable.innerJoin(tableEventType, [tableEvent['eventType_id'].eq(tableEventType['id'])])
    queryTable = queryTable.innerJoin(tableRbMedicalAidType, [tableEventType['medicalAidType_id'].eq(tableRbMedicalAidType['id']), tableRbMedicalAidType['code'].eq(6)])
    queryTable = queryTable.innerJoin(tableUetAction, [tableEvent['id'].eq(tableUetAction['event_id']), tableUetAction['actionType_id'].inlist(listUetActionIds)])
    queryTable = queryTable.innerJoin(tableUetActionType, [tableUetAction['actionType_id'].eq(tableUetActionType['id'])])

    group = [tableUetAction['actionType_id']]

    stmt = db.selectStmt(queryTable, cols, where=cond, group=group)
    return db.query(stmt)

class CReportUetAmount(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчёт по УЗИ(УЕТ)')

    def getSetupDialog(self, parent):
        result = CReportUetAmountDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):

        ################################################################################################################
        #Билд шапки.
        ################################################################################################################
        query = selectColumns(params)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        width = '100'
        #TODO: skkachaev: Если будет плохо выглядеть — смотреть нужно на эту переменную и её применение

        tableColumns = [
            ('40',  [u'№'],             CReportBase.AlignLeft),
            (width, [u'Отделение'],      CReportBase.AlignLeft),
        ]

        uets = []
        ids = {}
        i = 2
        while query.next():
            record = query.record()
            tableColumns.append((width, forceString(record.value('name')), CReportBase.AlignLeft))
            uets.append(forceDouble(record.value('UetDoctor')))
            # ids.append(forceInt(record.value('id')))
            ids[forceInt(record.value('actionType_id'))] = i
            i += 1

        tableColumns.append((width, [u'Итого Исследований'], CReportBase.AlignLeft))

        table = createTable(cursor, tableColumns)

        row = table.addRow()
        table.setText(row, 1, u'У.е.')
        for i in xrange(0, len(uets)):
            table.setText(row, i+2, uets[i])

        ################################################################################################################
        #Билд основной части
        ################################################################################################################

        params['idList'] = ids.keys()
        query = selectLinesAndData(params)
        self.setQueryText(self.queryText() + ';\n\n' + forceString(query.lastQuery()))

        currOrgStruct_id = -1
        max_i = i+3
        i = 0
        sum_i = 0.0
        total = dict.fromkeys(range(2, max_i+1), 0)
        amount = dict.fromkeys(range(2, max_i), 0)
        while query.next():
            record = query.record()
            if currOrgStruct_id == forceInt(record.value('orgStructure_id')): #Остаёмся на старой строке.
                #Работает потому что мы отсортировали выдачу по orgStructure_id
                table.setText(row, ids[forceInt(record.value('actionType_id'))], forceDouble(record.value('sum')), clearBefore=True)
                sum_i += forceDouble(record.value('sum'))
                total[ids[forceInt(record.value('actionType_id'))]] += forceDouble(record.value('sum'))
                amount[ids[forceInt(record.value('actionType_id'))]] += forceInt(record.value('amount'))
            else: #Переходим на новую строку
                if currOrgStruct_id != -1:
                    table.setText(row, max_i, sum_i)
                    total[max_i] += sum_i
                    sum_i = 0.0

                currOrgStruct_id = forceInt(record.value('orgStructure_id'))
                row = table.addRow()
                for j in xrange(2, max_i):
                    table.setText(row, j, 0.0)
                i += 1
                table.setText(row, 0, i)
                table.setText(row, 1, forceString(record.value('orgStructureName')) + ' ' + str(forceInt(record.value('orgStructure_id'))))

                table.setText(row, ids[forceInt(record.value('actionType_id'))], forceDouble(record.value('sum')), clearBefore=True)
                sum_i += forceDouble(record.value('sum'))
                total[ids[forceInt(record.value('actionType_id'))]] += forceDouble(record.value('sum'))
                amount[ids[forceInt(record.value('actionType_id'))]] += forceInt(record.value('amount'))

        if currOrgStruct_id != -1:
            table.setText(row, max_i, sum_i)
            total[max_i] += sum_i
            sum_i = 0.0

        ################################################################################################################
        #Билд части с сотрудниками
        ################################################################################################################

        query = selectStaffers(params)
        self.setQueryText(self.queryText() + ';\n\n' + forceString(query.lastQuery()))

        row = table.addRow()
        table.setText(row, 0, i)
        i += 1
        table.setText(row, 1, u'Сотрудники')
        for j in xrange(2, max_i):
                table.setText(row, j, 0.0)

        while query.next():
            record = query.record()
            table.setText(row, ids[forceInt(record.value('actionType_id'))], forceDouble(record.value('sum')), clearBefore=True)
            sum_i += forceDouble(record.value('sum'))
            total[ids[forceInt(record.value('actionType_id'))]] += forceDouble(record.value('sum'))

        table.setText(row, max_i, sum_i)
        total[max_i] += sum_i
        sum_i = 0.0

        ################################################################################################################
        #Билд части с ПМУ, ДМС
        ################################################################################################################

        query = selectNotOMS(params)
        self.setQueryText(self.queryText() + ';\n\n' + forceString(query.lastQuery()))

        row = table.addRow()
        table.setText(row, 0, i)
        i += 1
        table.setText(row, 1, u'ПМУ, ДМС')
        for j in xrange(2, max_i):
                table.setText(row, j, 0.0)

        while query.next():
            record = query.record()
            table.setText(row, ids[forceInt(record.value('actionType_id'))], forceDouble(record.value('sum')), clearBefore=True)
            sum_i += forceDouble(record.value('sum'))
            total[ids[forceInt(record.value('actionType_id'))]] += forceDouble(record.value('sum'))

        table.setText(row, max_i, sum_i)
        total[max_i] += sum_i
        sum_i = 0.0

        ################################################################################################################
        #Билд части с ОМС (ОКДО)
        ################################################################################################################

        query = selectOMS(params)
        self.setQueryText(self.queryText() + ';\n\n' + forceString(query.lastQuery()))

        row = table.addRow()
        table.setText(row, 0, i)
        i += 1
        table.setText(row, 1, u'ОМС(ОКДО)')
        for j in xrange(2, max_i):
                table.setText(row, j, 0.0)

        while query.next():
            record = query.record()
            table.setText(row, ids[forceInt(record.value('actionType_id'))], forceDouble(record.value('sum')), clearBefore=True)
            sum_i += forceDouble(record.value('sum'))
            total[ids[forceInt(record.value('actionType_id'))]] += forceDouble(record.value('sum'))
            amount[ids[forceInt(record.value('actionType_id'))]] += forceInt(record.value('amount'))

        table.setText(row, max_i, sum_i)
        total[max_i] += sum_i
        sum_i = 0.0

        ################################################################################################################
        #Билд ИТОГО
        ################################################################################################################

        row = table.addRow()
        table.setText(row, 1, u'Итого')
        for j in xrange(2, max_i):
            table.setText(row, j, amount[j])

        row = table.addRow()
        table.setText(row, 1, u'Итого у.е.')
        for j in xrange(2, max_i+1):
            table.setText(row, j, total[j])

        return doc

class CReportUetAmountDialog(QtGui.QDialog, Ui_ReportAmountSetup):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(getVal(params, 'begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(getVal(params, 'endDate', QtCore.QDate.currentDate()))
        self.cmbOrgStructure.setValue(getVal(params, 'orgStructureId', None))
        self.cmbPerson.setValue(getVal(params, 'personId', None))

    def params(self):
        return \
        {
            'begDate'           : self.edtBegDate.date(),
            'endDate'           : self.edtEndDate.date(),
            'orgStructureId'    : self.cmbOrgStructure.value(),
            'personId'          : self.cmbPerson.value()
        }

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.cmbPerson.setEndDate(QtCore.QDate(date))

    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        self.cmbPerson.setOrgStructureId(forceInt(self.cmbOrgStructure.value()))

def main():
    import sys
    from s11main import CS11mainApp
    from library.database import connectDataBaseByInfo
    app = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtGui.qApp = app
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    QtGui.qApp.currentOrgId = lambda: 386271 #229917

    connectionInfo = {'driverName' : 'mysql',
                      'host' : 'mos36',
                      'port' : 3306,
                      'database' : 's11',
                      'user' : 'dbuser',
                      'password' : 'dbpassword',
                      'connectionName' : 'vista-med',
                      'compressData' : True,
                      'afterConnectFunc' : None}
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    CReportUetAmount(None).exec_()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()