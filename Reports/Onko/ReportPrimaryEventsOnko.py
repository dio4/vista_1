# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from library.DialogBase import CDialogBase
from library.Utils import forceInt, forceRef, forceString
from Orgs.Utils import getOrgStructureDescendants
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase

from Ui_ReportPrimaryEventsOnko import Ui_ReportPrimaryEventsOnkoSetupDialog


def selectData(begDate, endDate, orgStructureId):
    db = QtGui.qApp.db
    Action = db.table('Action')
    ActionType = db.table('ActionType')
    Client = db.table('Client')
    Event = db.table('Event')
    EventType = db.table('EventType')
    Person = db.table('Person')

    visitToSpecEventTypeId = forceRef(db.translate(EventType, 'name', u'Осмотр специалиста', 'id'))
    isVisitToSpecCond = EventType['id'].eq(visitToSpecEventTypeId)

    ultrasoundGroupId = forceRef(db.getRecordEx(ActionType, ActionType['id'], [ActionType['name'].eq(u'Ультразвуковые исследования'), ActionType['group_id'].isNull()]).value('id'))
    isUltrasoundDiagnosticCond = ActionType['id'].inlist(db.getDescendants(ActionType, 'group_id', ultrasoundGroupId))

    diagnosticGroupId = forceRef(db.getRecordEx(ActionType, ActionType['id'], [ActionType['name'].eq(u'Лабораторная диагностика'), ActionType['group_id'].isNull()]).value('id'))
    isDiagnosticCond = ActionType['id'].inlist(db.getDescendants(ActionType, 'group_id', diagnosticGroupId))

    table = Event.innerJoin(EventType, [EventType['id'].eq(Event['eventType_id']), EventType['deleted'].eq(0)])
    table = table.innerJoin(Client, [Client['id'].eq(Event['client_id']), Client['deleted'].eq(0)])
    table = table.leftJoin(Action, [Action['event_id'].eq(Event['id']), Action['deleted'].eq(0)])
    table = table.leftJoin(ActionType, [ActionType['id'].eq(Action['actionType_id']), ActionType['deleted'].eq(0)])
    table = table.leftJoin(Person, [Person['id'].eq(Event['setPerson_id'])])

    cols = [
        Client['id'].alias('clientId'),
        u'count(DISTINCT if({0}, Event.id, NULL)) AS visitsTotal'.format(isVisitToSpecCond),
        u'count(DISTINCT if({0}, Event.id, NULL)) AS primaryTotal'.format(Event['isPrimary'].eq(1)),
        u'count(DISTINCT if({0}, Event.id, NULL)) AS primaryVisits'.format(db.joinAnd([Event['isPrimary'].eq(1), isVisitToSpecCond])),
        u'count(DISTINCT if({0}, Event.id, NULL)) AS secondaryTotal'.format(Event['isPrimary'].eq(2)),
        u'count(DISTINCT if({0}, Event.id, NULL)) AS secondaryVisits'.format(db.joinAnd([Event['isPrimary'].eq(2), isVisitToSpecCond])),
        u'count(DISTINCT if({0}, Action.id, NULL)) AS ultrasoundDiagnostics'.format(isUltrasoundDiagnosticCond),
        u'count(DISTINCT if({0}, Action.id, NULL)) AS clinicalAnalysis'.format(isDiagnosticCond)
    ]

    cond = [
        Event['deleted'].eq(0),
        Event['setDate'].dateGe(begDate),
        Event['setDate'].dateLe(endDate)
    ]
    if orgStructureId:
        cond.append(Person['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))

    stmt = db.selectStmt(table, cols, cond, group=Client['id'], order=Client['id'])
    return db.query(stmt)


class CReportPrimaryEventsOnkoSetupDialog(CDialogBase, Ui_ReportPrimaryEventsOnkoSetupDialog):

    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())

    def setTitle(self, title):
        self.setWindowTitle(title)

    def params(self):
        return {
            'begDate': self.edtBegDate.date(),
            'endDate': self.edtEndDate.date(),
            'orgStructureId': self.cmbOrgStructure.value()
        }

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))


class CReportPrimaryEventsOnko(CReport):

    def __init__(self, parent=None):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчет для Выборгского центра')

    def getSetupDialog(self, parent):
        dlg = CReportPrimaryEventsOnkoSetupDialog(parent)
        dlg.setTitle(self.title())
        return dlg

    def build(self, params):
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        orgStructureId = params.get('orgStructureId', None)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('10%', [u'№ п/п'], CReportBase.AlignLeft),
            ('13%', [u'№ карты'], CReportBase.AlignLeft),
            ('13%', [u'Перв. прием'], CReportBase.AlignCenter),
            ('13%', [u'Повт. прием'], CReportBase.AlignCenter),
            ('13%', [u'Акция', u'перв. прием'], CReportBase.AlignCenter),
            ('13%', [u'', u'повт. прием'], CReportBase.AlignCenter),
            ('13%', [u'УЗИ'], CReportBase.AlignCenter),
            ('13%', [u'Анализы'], CReportBase.AlignCenter),
        ]
        table = createTable(cursor, tableColumns)
        for c in range(4) + [6, 7]:
            table.mergeCells(0, c, 2, 1)
        table.mergeCells(0, 4, 1, 2)

        query = selectData(begDate, endDate, orgStructureId)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            clientId = forceRef(record.value('clientId'))
            visitsTotal = forceInt(record.value('visitsTotal'))
            primaryTotal = forceInt(record.value('primaryTotal'))
            primaryVisits = forceInt(record.value('primaryVisits'))
            secondaryTotal = forceInt(record.value('secondaryTotal'))
            secondaryVisits = forceInt(record.value('secondaryVisits'))
            ultrasoundDiagnostics = forceInt(record.value('ultrasoundDiagnostics'))
            clinicalAnalysis = forceInt(record.value('clinicalAnalysis'))

            i = table.addRow()
            table.setText(i, 0, i-1)
            table.setText(i, 1, clientId)
            table.setText(i, 2, primaryTotal)
            table.setText(i, 3, secondaryTotal)
            table.setText(i, 4, primaryVisits)
            table.setText(i, 5, secondaryVisits)
            table.setText(i, 6, ultrasoundDiagnostics)
            table.setText(i, 7, clinicalAnalysis)

        return doc


# def main():
#     import sys
#     from s11main import CS11mainApp
#     from library.database import connectDataBaseByInfo
#
#     app = CS11mainApp(sys.argv, False, 'S11App.ini', False)
#     QtGui.qApp = app
#     QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))
#
#     QtGui.qApp.currentOrgId = lambda: 3147
#
#     QtGui.qApp.db = connectDataBaseByInfo({
#         'driverName' :      'mysql',
#         'host' :            'pes',
#         'port' :            3306,
#         'database' :        's12',
#         'user':             'dbuser',
#         'password':         'dbpassword',
#         'connectionName':   'vista-med',
#         'compressData' :    True,
#         'afterConnectFunc': None
#     })
#
#     CReportPrimaryEventsOnko(None).exec_()
#
#
# if __name__ == '__main__':
#     main()