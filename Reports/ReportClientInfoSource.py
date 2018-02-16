# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Reports.Report import CReport
from Reports.ReportBase import CReportBase, createTable
from Reports.ReportClientInfoSourceSetup import CReportClientInfoSourceSetup
from library.Utils import forceDouble, forceInt, forceRef, forceString


def selectData(params):
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    manyEvents = params.get('manyEvents', None)
    lstSource = params.get('lstSource', None)

    db = QtGui.qApp.db
    tableAccountItem = db.table('Account_Item')
    tableClient = db.table('Client')
    tableClientInfoSource = db.table('ClientInfoSource')
    tableEvent = db.table('Event')
    tableEventType = db.table('EventType')

    table = tableClientInfoSource
    table = table.innerJoin(tableClient, [tableClient['id'].eq(tableClientInfoSource['client_id']),
                                          tableClient['deleted'].eq(0)])
    if manyEvents:
        table = table.leftJoin(tableEvent, [tableEvent['client_id'].eq(tableClient['id']),
                                            tableEvent['setDate'].dateGe(tableClientInfoSource['infoSourceDate']),
                                            tableEvent['deleted'].eq(0)])
        table = table.leftJoin(tableEventType, [tableEventType['id'].eq(tableEvent['eventType_id']),
                                                tableEventType['code'].eq('01'),
                                                tableEventType['deleted'].eq(0)])
    else:
        table = table.leftJoin(tableEvent, tableEvent['id'].eqStmt(
            db.selectStmt(
                table=tableEvent.innerJoin(tableEventType, [tableEventType['id'].eq(tableEvent['eventType_id']),
                                                            tableEventType['code'].eq('01'),
                                                            tableEventType['deleted'].eq(0)]),
                fields=tableEvent['id'],
                where=[tableEvent['client_id'].eq(tableClient['id']),
                       tableEvent['setDate'].dateGe(tableClientInfoSource['infoSourceDate']),
                       tableEvent['deleted'].eq(0),
                       db.existsStmt(tableAccountItem, [tableAccountItem['event_id'].eq(tableEvent['id']),
                                                        tableAccountItem['deleted'].eq(0)])],
                order=[tableEvent['setDate']],
                limit=1
            )
        ))
    table = table.leftJoin(tableAccountItem, [tableAccountItem['event_id'].eq(tableEvent['id']),
                                              tableAccountItem['deleted'].eq(0)])
    cols = [
        tableClientInfoSource['rbInfoSource_id'],
        db.count(tableClient['id'], distinct=True).alias('clientsCount'),
        db.sum(tableAccountItem['sum']).alias('sum')
    ]
    cond = [
        tableClientInfoSource['infoSourceDate'].dateGe(begDate),
        tableClientInfoSource['infoSourceDate'].dateLe(endDate),
        tableClientInfoSource['deleted'].eq(0)
    ]
    group = []
    if lstSource:
        cond.append(tableClientInfoSource['rbInfoSource_id'].inlist(lstSource))
        group.append(tableClientInfoSource['rbInfoSource_id'])

    return db.query(db.selectStmt(table, cols, cond, group=group))


def selectInfoSourceNameMap(params):
    db = QtGui.qApp.db
    tableInfoSource = db.table('rbInfoSource')

    cond = []
    lstSource = params.get('lstSource', None)
    if lstSource:
        cond.append(tableInfoSource['id'].inlist(lstSource))

    return db.iterRecordList(tableInfoSource, ['id', 'name'], cond, order=['name'])


class CReportClientInfoSource(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчет по источникам информации')

    def getSetupDialog(self, parent):
        result = CReportClientInfoSourceSetup(parent)

        result.setTitle(self.title())
        return result

    def build(self, params):
        grouped = bool(params.get('lstSource'))

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
            ('%50', [u'Количество пациентов'], CReportBase.AlignRight),
            ('%50', [u'Cумма (р.)'], CReportBase.AlignRight),
        ]

        if grouped:
            tableColumns.insert(0, ('%50', [u'Источник'], CReportBase.AlignRight))

        table = createTable(cursor, tableColumns)

        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))

        if grouped:
            reportData = {}
            while query.next():
                rec = query.record()
                reportData[forceRef(rec.value('rbInfoSource_id'))] = (forceInt(rec.value('clientsCount')),
                                                                      forceDouble(rec.value('sum')))
            for rec in selectInfoSourceNameMap(params):
                sourceId = forceRef(rec.value('id'))
                sourceName = forceString(rec.value('name'))
                clientsCount, accountSum = reportData.get(sourceId, (0, 0.0))
                table.addRowWithContent(sourceName, clientsCount, accountSum)
        else:
            while query.next():
                rec = query.record()
                table.addRowWithContent(forceInt(rec.value('clientsCount')),
                                        forceDouble(rec.value('sum')))

        return doc

def main():
    import sys
    from s11main import CS11mainApp
    from library.database import connectDataBaseByInfo

    QtGui.qApp = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    connectionInfo = {
        'driverName': 'mysql',
        'host': 'pes',
        'port': 3306,
        'database': 's12',
        'user': 'dbuser',
        'password': 'dbpassword',
        'connectionName': 'vista-med',
        'compressData': True,
        'afterConnectFunc': None
    }
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    w = CReportClientInfoSource(None)
    w.exec_()


if __name__ == '__main__':
    main()
