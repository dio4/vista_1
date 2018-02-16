# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from library.Utils      import forceDouble, forceInt, forceString, forceMoneyRepr, TableColIndex

from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase

from Ui_ReportPlanningAndEconomicIndicators import Ui_ReportPlanningAndEconomicIndicators

def selectData(params, eventTypes = None):
    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    groupOrgStructure = params.get('groupOrgStructure', False)
    orgStructureId = params.get('orgStructureId', None)

    tableAction  = db.table('Action')
    tableOrgStructure = db.table('OrgStructure')

    contractTariffCond = '(ActionType_Service.`finance_id` AND ActionType_Service.`finance_id`=Contract.`finance_id` AND Contract_Tariff.`service_id`=ActionType_Service.`service_id`) OR (ActionType_Service.`finance_id` IS NULL AND Contract_Tariff.`service_id`=ActionType_Service.`service_id`)'
    cond = [contractTariffCond,
            tableAction['begDate'].dateGe(begDate),
            tableAction['endDate'].dateLe(endDate)]

    joins = ['ActionType ON ActionType.id = Action.actionType_id',
            'ActionType_Service ON ActionType_Service.master_id = ActionType.id',
            'Event ON Event.id = Action.event_id',
            'EventType ON EventType.id = Event.eventType_id',
            'Contract ON Contract.id = Event.contract_id',
            'Contract_Tariff ON Contract_Tariff.master_id = Contract.id']
    joinStmt = u'\n    inner join '.join(joins)
    if orgStructureId or groupOrgStructure:
        leftJoinStr = '\n    left join '
        joinStmt += leftJoinStr + leftJoinStr.join(
            ['Person ON Action.person_id = Person.id',
             'OrgStructure ON Person.orgStructure_id = OrgStructure.id'])
        if orgStructureId:
            orgStructureIdList = db.getDescendants(tableOrgStructure, 'parent_id', orgStructureId)
            cond.append(tableOrgStructure['id'].inlist(orgStructureIdList))

    if eventTypes:
        tableEventType = db.table('EventType')
        cond.append(tableEventType['id'].notInlist(eventTypes))

    if groupOrgStructure:
        cond.append(db.joinOr([tableOrgStructure['deleted'].eq(0), tableOrgStructure['deleted'].isNull()]))
        options = (u'OrgStructure.name as osName,', joinStmt, db.joinAnd(cond), u'\n  OrgStructure.id,')
    else:
        options = ('', joinStmt, db.joinAnd(cond), '')
    stmt = u'''
select %s
    ActionType.code,
    ActionType.name as actionName,
    sum(Action.amount) as amount,
    Contract_Tariff.price
from
    Action
    inner join %s
where %s
    and Action.deleted = 0
    and ActionType.deleted = 0
    and Event.deleted = 0
    and EventType.deleted = 0
    and Contract.deleted = 0
    and Contract_Tariff.deleted = 0
group by %s
  ActionType.code,
  Contract_Tariff.price
''' % options
    return db.query(stmt)

class CReportPlanningAndEconomicIndicators(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчет о выполнении планово-экономических показателей по объемам медицинской помощи')


    def getSetupDialog(self, parent):
        result = CPlanningAndEconomicIndicators(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        eventTypesDict = params.get('eventTypes', None)
        eventTypes =eventTypesDict.keys()
        query = selectData(params, eventTypes)
        self.setQueryText(forceString(query.lastQuery()))

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        if eventTypes:
            cursor.insertText(u'исключены обращения с типами действия: ' + ', '.join([forceString(eventTypesDict[key]) for key in eventTypes]))
        cursor.insertBlock()
        groupOrgStructure = params.get('groupOrgStructure')
        tabIndex = TableColIndex()
        tableColumns = []
        tableColumns.extend([
            ( '5%',  [u'Код услуги'], CReportBase.AlignLeft),
            ( '15%', [u'Название кода тарифа'], CReportBase.AlignRight),
            ( '5%',  [u'Кол-во'], CReportBase.AlignLeft),
            ( '10%', [u'Тариф'], CReportBase.AlignLeft),
            ( '10%', [u'Стоимость'], CReportBase.AlignLeft)])
        tabIndex.addColumns(['code', 'actionName', 'amount', 'price', 'cost'])
        table = createTable(cursor, tableColumns)
        totalAmount = 0
        totalCost = 0
        previousOsName = None
        while query.next():
            record = query.record()
            if groupOrgStructure:
                osName = forceString(record.value('osName'))
                if osName != previousOsName:
                    row = table.addRow()
                    table.mergeCells(row, 0, 1, len(tabIndex))
                    table.setText(row, 0, osName)
                    previousOsName = osName
            code = forceString(record.value('code'))
            actionName = forceString(record.value('actionName'))
            amount = forceInt(record.value('amount'))
            price = forceDouble(record.value('price'))
            cost = amount * price
            totalAmount += amount
            totalCost += cost

            row = table.addRow()
            table.setText(row, tabIndex.code, code)
            table.setText(row, tabIndex.actionName, actionName)
            table.setText(row, tabIndex.amount, amount)
            table.setText(row, tabIndex.price, forceMoneyRepr(price))
            table.setText(row, tabIndex.cost, forceMoneyRepr(cost))

        row = table.addRow()
        table.setText(row, tabIndex.actionName, u'Итого:', CReportBase.TableTotal)
        table.setText(row, tabIndex.amount, totalAmount, CReportBase.TableTotal)
        table.setText(row, tabIndex.cost, totalCost, CReportBase.TableTotal)
        return doc

class CPlanningAndEconomicIndicators(QtGui.QDialog, Ui_ReportPlanningAndEconomicIndicators):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.lstItems.setTable('EventType')
        self.cmbFinanceType.setTable('rbFinance')
        self.lblFinanceType.setVisible(False)
        self.cmbFinanceType.setVisible(False)
        self.chkGroupingOrgStructure.setChecked(False)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbFinanceType.setValue(params.get('financeId', None))
        self.chkGroupingOrgStructure.setChecked(params.get('groupOrgStructure', False))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['eventTypes'] = self.lstItems.nameValues()
        result['financeId'] = self.cmbFinanceType.value()
        result['groupOrgStructure'] = self.chkGroupingOrgStructure.isChecked()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        return result





