# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.Ui_ReportFeedDistributionSetup import Ui_ReportFeedDistributionSetup
from library.Utils import forceString, forceInt


def selectData(params):
    stmt = u'''
SELECT
    T.amount,
    rbDiet.code AS dietCode,
    OrgStructure.code AS orgStructureCode
FROM
 
    (
        SELECT
            (
                SELECT
                    OS.id
                FROM
                    ActionPropertyType AS APT
                    INNER JOIN ActionProperty AS AP ON AP.type_id=APT.id
                    INNER JOIN ActionProperty_OrgStructure AS APOS ON APOS.id=AP.id
                    INNER JOIN OrgStructure AS OS ON OS.id=APOS.value
                WHERE
                    APT.actionType_id = A2.actionType_id
                    AND AP.action_id = A2.id
                    AND APT.deleted = 0
                    AND (APT.name RLIKE 'Отделение')
                    AND OS.deleted = 0
                LIMIT 1
            )
            AS orgStructure_id,

            Event_Feed.diet_id AS rbDiet_id,
            COUNT(*) AS amount
        FROM
            Event
            INNER JOIN Event_Feed ON Event.id = Event_Feed.event_id
            INNER JOIN Action A1 ON Event.id = A1.event_id
            INNER JOIN Action A2 ON Event.id = A2.event_id
            LEFT JOIN Contract ON Event.contract_id = Contract.id
        WHERE
            A1.actionType_id IN (SELECT id FROM ActionType where name = 'Поступление')
            AND A2.actionType_id IN (SELECT id FROM ActionType where name = 'Движение')
            AND NOT EXISTS (
                SELECT
                    id
                FROM
                    Action
                WHERE
                    actionType_id IN (SELECT id FROM ActionType where name = 'Движение')
                    AND event_id = A2.event_id
                    AND begDate < A2.begDate
            )
            AND %s
        GROUP BY
            orgStructure_id, Event_Feed.diet_id
    )
    AS T
    
    LEFT JOIN OrgStructure on T.orgStructure_id = OrgStructure.id
    INNER JOIN rbDiet on T.rbDiet_id = rbDiet.id
    '''

    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    orgStructureId = params.get('orgStructureId', None)
    eventTypeId = params.get('eventTypeId', None)
    financeId = params.get('typeFinanceId', None)

    db = QtGui.qApp.db
    tableAction = db.table('Action').alias('A1')
    tableOrgStructure = db.table('OrgStructure')
    tableEvent = db.table('Event')
    tableContract = db.table('Contract')

    cond = [
        tableAction['begDate'].dateGe(begDate),
        tableAction['begDate'].dateLe(endDate)
    ]
    if eventTypeId is not None:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if financeId is not None:
        cond.append(tableContract['finance_id'].eq(financeId))

    if orgStructureId:
        condOrgStructure = db.joinAnd([
            db.joinOr([
                tableOrgStructure['id'].eq(orgStructureId),
                tableOrgStructure['id'].inInnerStmt(
                    "(SELECT id FROM OrgStructure_Ancestors WHERE fullPath LIKE '%" + str(orgStructureId) + "%')"
                )
            ]),
        ])
        stmt += u'\nWHERE\n' + condOrgStructure

    return db.query(stmt % db.joinAnd(cond))


class CReportFeedDistributionSetupDialog(QtGui.QDialog, Ui_ReportFeedDistributionSetup):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbFinance.setTable('rbFinance', addNone=True)
        self.cmbEventType.setTable('EventType', addNone=True)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        currentDate = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate(currentDate.year(), currentDate.month(), 1)))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate(currentDate.year(), currentDate.month(), currentDate.daysInMonth())))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbFinance.setValue(params.get('typeFinanceId', None))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['eventTypeId'] = self.cmbEventType.value()
        result['typeFinanceId'] = self.cmbFinance.value()
        return result


class CReportFeedDistribution(CReport):

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u"Раздаточная ведомость")

    def getSetupDialog(self, parent):
        result = CReportFeedDistributionSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def getTables(self):
        db = QtGui.qApp.db
        tableRbDiet = db.table('rbDiet')
        return [forceString(record.value('code')) for record in db.getRecordList(tableRbDiet, [tableRbDiet['code']])]

    def build(self, params):
        doc = QtGui.QTextDocument()

        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        orgStructurePercentage = 30
        numbersPercentage = 100 - orgStructurePercentage
        tableColumns = [(str(orgStructurePercentage) + '%', [u'Отделение'], CReportBase.AlignLeft)]
        # tables to sit at, not to write information into
        tables = self.getTables()
        for tableType in tables:
            tableColumns.append((str(numbersPercentage / (1 + len(tables))) + '%', [tableType], CReportBase.AlignLeft))
        tableColumns.append((str(numbersPercentage / (1 + len(tables))) + '%', [u'Всего'], CReportBase.AlignLeft))
        table = createTable(cursor, tableColumns)

        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))

        statsMap = {}
        totalTables = {}
        while query.next():
            record = query.record()
            orgStructure = forceString(record.value('orgStructureCode'))
            tableType = forceString(record.value('dietCode'))
            amount = forceInt(record.value('amount'))

            statsMap.setdefault(orgStructure, {}).setdefault(tableType, 0)
            statsMap[orgStructure][tableType] += amount

            totalTables.setdefault(tableType, 0)
            totalTables[tableType] += amount

        for orgStructure in statsMap:
            for tableType in tables:
                statsMap[orgStructure].setdefault(tableType, 0)
        for tableType in tables:
            totalTables.setdefault(tableType, 0)

        orgStructures = statsMap.keys()
        orgStructures.sort()
        for orgStructure in orgStructures:
            i = table.addRow()
            table.setText(i, 0, orgStructure if orgStructure is not None else u'Без уточнения')
            totalByOrgStructure = 0
            for j, tableType in enumerate(tables):
                amount = statsMap[orgStructure][tableType]
                table.setText(i, j + 1, amount)
                totalByOrgStructure += amount
            table.setText(i, len(tableColumns) - 1, totalByOrgStructure)

        i = table.addRow()
        table.setText(i, 0, u'Всего', charFormat=CReportBase.TableTotal)
        for j, tableType in enumerate(tables):
            table.setText(i, j + 1, totalTables[tableType], charFormat=CReportBase.TableTotal)
        table.setText(i, len(tableColumns) - 1, sum(totalTables.values()), charFormat=CReportBase.TableTotal)

        return doc

