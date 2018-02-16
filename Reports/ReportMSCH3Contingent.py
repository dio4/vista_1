# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.ReportMSCH3Setup import CReportMSCH3SetupDialog
from library.Utils import forceInt, forceString


def selectData(params):
    db = QtGui.qApp.db
    Event = db.table('Event').alias('e')

    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    isWorker = params.get('isWorker', False)
    eventTypesDict = params.get('eventTypes', {})
    eventTypes = eventTypesDict.keys()

    workerStmt = u"""
        INNER JOIN (
            SELECT c.id clientId
            FROM Client c
                INNER JOIN (SELECT Client.id clientId, MAX(ClientWork.id) clientWorkId
                            FROM Client
                                INNER JOIN ClientWork ON Client.id = ClientWork.client_id
                            WHERE ClientWork.deleted = 0
                            GROUP BY Client.id) tmp ON c.id = tmp.clientId
                INNER JOIN ClientWork cw ON tmp.clientWorkId = cw.id
                LEFT JOIN Organisation org ON cw.org_id = org.id
            WHERE
               (cw.freeInput LIKE '%Балтийский Завод-Судостроение%' OR
                cw.freeInput LIKE '%Балтийский Завод Судостроение%' OR
                cw.freeInput LIKE '%БЗС%' OR
                org.fullName LIKE '%Балтийский Завод-Судостроение%' OR
                org.fullName LIKE '%Балтийский Завод Судостроение%' OR
                org.fullName LIKE '%БЗС%')
                AND cw.deleted = 0
        ) work ON work.clientId = e.client_id
    """
    stmt = u"""
    SELECT 
        d1.MKB AS 'MKB',
        COUNT(d1.MKB) AS 'count'
    FROM
        Event e
        INNER JOIN Diagnostic d ON d.event_id = e.id
        INNER JOIN Diagnosis d1 ON d.diagnosis_id = d1.id
        -- если надо из всех набитых посчитать всё таки только выставленных, раскомментировать:
        -- INNER JOIN (
        --     SELECT DISTINCT Account_Item.event_id FROM Account_Item WHERE Account_Item.deleted = 0
        -- ) pop ON pop.event_id = e.id
        {workerStmt}
    WHERE
        e.deleted = 0 
        AND d.deleted = 0
        AND d1.deleted = 0
        AND DATE(e.execDate) >= DATE('{begDate}')
        AND DATE(e.execDate) <= DATE('{endDate}')
        AND LENGTH(d1.MKB) > 1 
        {eventTypes}
    GROUP BY d1.MKB
    """
    stmt = stmt.format(
        begDate=begDate.toString('yyyy-MM-dd'),
        endDate=endDate.toString('yyyy-MM-dd'),
        workerStmt=workerStmt if isWorker else u'',
        eventTypes=(u'AND %s' % Event['eventType_id'].inlist(eventTypes)) if eventTypes else u''
    )

    return db.query(stmt)


class CReportMSCH3Contingent(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Сведения о работе с контингентами')

    def getSetupDialog(self, parent):
        result = CReportMSCH3SetupDialog(parent)
        result.setTitle(self.title())

        return result

    def build(self, params):
        isWorker = params.get('isWorker', False)

        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)

        if isWorker:
            cursor.insertText(u'Сводка о работе с сотрудниками ООО "Балтийский завод-Судостроение"')
        else:
            cursor.insertText(u'Сводка  о работе со всеми контингентами')

        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
            ('%50', [u'№ п/п'], CReportBase.AlignRight),
            ('%50', [u'Код МКБ'], CReportBase.AlignRight),
            ('%50', [u'Количество'], CReportBase.AlignRight)
        ]

        table = createTable(cursor, tableColumns)

        total = 0
        while query.next():
            record = query.record()

            i = table.addRow()
            total += forceInt(record.value('count'))

            table.setText(i, 0, i)
            table.setText(i, 1, forceString(record.value('MKB')))
            table.setText(i, 2, forceInt(record.value('count')))

        i = table.addRow()
        table.mergeCells(i, 0, 1, 2)
        table.setText(i, 0, u'Итого', CReportBase.TableTotal)
        table.setText(i, 2, total, CReportBase.TableTotal)

        return doc


# def main():
#     import sys
#     from s11main import CS11mainApp
#     from library.database import connectDataBaseByInfo
#
#     QtGui.qApp = CS11mainApp(sys.argv, False, 'S11App.ini', False)
#     QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))
#
#     connectionInfo = {
#         'driverName': 'mysql',
#         'host': 'msch3',
#         'port': 3306,
#         'database': 's11',
#         'user': 'dbuser',
#         'password': 'dbpassword',
#         'connectionName': 'vista-med',
#         'compressData': True,
#         'afterConnectFunc': None
#     }
#     QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)
#
#     w = CReportMSCH3Contingent(None)
#     w.exec_()
#
#
# if __name__ == '__main__':
#     main()
