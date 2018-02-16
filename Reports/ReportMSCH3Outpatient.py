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
    eventTypesDict = params.get('eventTypes', {})
    eventTypes = eventTypesDict.keys()

    stmt = u"""
    SELECT 
        rbFinance.name AS financeName,
        SUM((
            SELECT DISTINCT
                COUNT(DISTINCT e.id)
            FROM
                Event e
                INNER JOIN EventType et ON e.eventType_id = et.id
            WHERE
                e.deleted = 0 
                AND et.finance_id = rbFinance.id
                AND DATE(e.execDate) >= DATE('{begDate}')
                AND DATE(e.execDate) <= DATE('{endDate}')
                AND e.isPrimary = 1
                {eventTypes}
        )) AS countPrimary,
        SUM((
            SELECT DISTINCT
                COUNT(DISTINCT e.id)
            FROM
                Event e
                INNER JOIN EventType et ON e.eventType_id = et.id
            WHERE
                e.deleted = 0 
                AND et.finance_id = rbFinance.id
                AND DATE(e.execDate) >= DATE('{begDate}')
                AND DATE(e.execDate) <= DATE('{endDate}')
                AND e.isPrimary = 2
                {eventTypes}
        )) AS countSecondary
    FROM
        rbFinance
    WHERE
        rbFinance.name LIKE '%ДМС%'
    UNION
    SELECT 
        rbFinance.name AS financeName,
        SUM((
            SELECT DISTINCT
                COUNT(DISTINCT e.id)
            FROM
                Event e
                INNER JOIN EventType et ON e.eventType_id = et.id
            WHERE
                e.deleted = 0 
                AND et.finance_id = rbFinance.id
                AND DATE(e.execDate) >= DATE('{begDate}')
                AND DATE(e.execDate) <= DATE('{endDate}')
                AND e.isPrimary = 1
                {eventTypes}
        )) AS countPrimary,
        SUM((
            SELECT DISTINCT
                COUNT(DISTINCT e.id)
            FROM
                Event e
                INNER JOIN EventType et ON e.eventType_id = et.id
            WHERE
                e.deleted = 0 
                AND et.finance_id = rbFinance.id
                AND DATE(e.execDate) >= DATE('{begDate}')
                AND DATE(e.execDate) <= DATE('{endDate}')
                AND e.isPrimary = 2
                {eventTypes}
        )) AS countSecondary
    FROM
        rbFinance
    WHERE
        rbFinance.name LIKE '%платные услуги%'
    UNION
    SELECT 
        'БЗС' AS financeName,
        SUM((
            SELECT DISTINCT
                COUNT(DISTINCT e.id)
            FROM
                Event e
                INNER JOIN EventType et ON e.eventType_id = et.id
            WHERE
                e.deleted = 0 
                AND e.client_id = ClientWork.client_id
                AND DATE(e.execDate) >= DATE('{begDate}')
                AND DATE(e.execDate) <= DATE('{endDate}')
                AND e.isPrimary = 1
                {eventTypes}
        )) AS countPrimary,
        SUM((
            SELECT DISTINCT
                COUNT(DISTINCT e.id)
            FROM
                Event e
                INNER JOIN EventType et ON e.eventType_id = et.id
            WHERE
                e.deleted = 0 
                AND e.client_id = ClientWork.client_id
                AND DATE(e.execDate) >= DATE('{begDate}')
                AND DATE(e.execDate) <= DATE('{endDate}')
                AND e.isPrimary = 2
                {eventTypes}
        )) AS countSecondary
    FROM
        (
            SELECT c.id client_id
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
        ) ClientWork
    """
    stmt = stmt.format(
        begDate=begDate.toString('yyyy-MM-dd'),
        endDate=endDate.toString('yyyy-MM-dd'),
        eventTypes=(u'AND %s' % Event['eventType_id'].inlist(eventTypes)) if eventTypes else u''
    )

    return db.query(stmt)


class CReportMSCH3Outpatient(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'ССведения о посещениях к врачу во время амбулаторного приема')

    def getSetupDialog(self, parent):
        result = CReportMSCH3SetupDialog(parent)
        result.setTitle(self.title())
        result.chkIsWorker.setVisible(False)

        return result

    def build(self, params):
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)

        cursor.insertText(u'Сводка о посещениях к врачу во время амбулаторного приема')

        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
            ('%50', [u'№ п/п'], CReportBase.AlignRight),
            ('%50', [u'Наименование'], CReportBase.AlignRight),
            ('%50', [u'Количество первичных'], CReportBase.AlignRight),
            ('%50', [u'Количество вторичных'], CReportBase.AlignRight)
        ]

        table = createTable(cursor, tableColumns)

        total = [0] * 2
        while query.next():
            record = query.record()

            i = table.addRow()
            if u'БЗС' not in forceString(record.value('financeName')):
                total[0] += forceInt(record.value('countPrimary'))
                total[1] += forceInt(record.value('countSecondary'))

            table.setText(i, 0, i)
            table.setText(i, 1, forceString(record.value('financeName')))
            table.setText(i, 2, forceInt(record.value('countPrimary')))
            table.setText(i, 3, forceInt(record.value('countSecondary')))

        i = table.addRow()
        table.mergeCells(i, 0, 1, 2)
        table.setText(i, 0, u'Итого', CReportBase.TableTotal)
        table.setText(i, 2, total[0], CReportBase.TableTotal)
        table.setText(i, 3, total[1], CReportBase.TableTotal)

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
#     w = CReportMSCH3Outpatient(None)
#     w.exec_()
#
#
# if __name__ == '__main__':
#     main()
