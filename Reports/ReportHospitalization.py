# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.ReportTreatmentRoom import CReportPnd
from library.Utils import forceDate, forceInt, forceRef, forceString, pyDate


def selectData(begDate, endDate, personId, rowGrouping):
    db = QtGui.qApp.db

    tablePerson = db.table('Person')
    tableAction = db.table('Action')
    tableActionType = db.table('ActionType')
    tableActionPropertyType = db.table('ActionPropertyType')
    tableActionProperty = db.table('ActionProperty')
    tableAPString = db.table('ActionProperty_String')
    tableEvent = db.table('Event')
    tableClientMonitoring = db.table('ClientMonitoring')
    tableClientMonitoringKind = db.table('rbClientMonitoringKind')
    tableACTT = db.table('ActionType').alias('ACTT')
    tableACTP = db.table('ActionProperty').alias('ACTP')
    tableACTPT = db.table('ActionPropertyType').alias('ACTPT')
    tableACTP_S = db.table('ActionProperty_String').alias("ACTP_S")

    queryTable = tableAction.innerJoin(tablePerson, tablePerson['id'].eq(tableAction['setPerson_id']))
    queryTable = queryTable.innerJoin(tableActionType, tableAction['actionType_id'].eq(tableActionType['id']))
    queryTable = queryTable.innerJoin(tableActionProperty, tableActionProperty['action_id'].eq(tableAction['id']))
    queryTable = queryTable.innerJoin(
        tableActionPropertyType,
        db.joinAnd([
            tableActionPropertyType['id'].eq(tableActionProperty['type_id']),
            tableActionPropertyType['name'].eq(u'Кем направлен')
        ])
    )
    queryTable = queryTable.innerJoin(tableAPString, tableAPString['id'].eq(tableActionProperty['id']))
    queryTable = queryTable.innerJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
    queryTable = queryTable.innerJoin(
        tableClientMonitoring,
        tableClientMonitoring['client_id'].eq(tableEvent['client_id'])
    )
    queryTable = queryTable.leftJoin(
        tableClientMonitoringKind,
        tableClientMonitoringKind['id'].eq(tableClientMonitoring['kind_id'])
    )
    queryTable = queryTable.innerJoin(tableACTT, tableAction['actionType_id'].eq(tableACTT['id']))
    queryTable = queryTable.innerJoin(tableACTP, tableACTP['action_id'].eq(tableAction['id']))
    queryTable = queryTable.innerJoin(tableACTPT,
            db.joinAnd([
                tableACTPT['id'].eq(tableACTP['type_id']),
                tableACTPT['name'].eq(u'направляется в больницу')
        ])
    )
    queryTable = queryTable.innerJoin(tableACTP_S, tableACTP_S['id'].eq(tableACTP['id']))


    if rowGrouping == 1:  # by personId
        groupField = 'Action.setPerson_id'
    else:
        groupField = 'DATE(Action.begDate)'

    cols = [
        '%s rowKey' % groupField,
        u'''
        COUNT(DISTINCT IF(ActionProperty_String.value = '0 - ПНД', Action.id, NULL)) AS pnd,
        COUNT(DISTINCT IF(ActionProperty_String.value = '1 - Скорая', Action.id, NULL)) AS cmp,
        COUNT(DISTINCT IF(ActionProperty_String.value = '2 - Др. учр.', Action.id, NULL)) AS other,
        COUNT(DISTINCT IF(ACTP_S.value = 'впервые', Action.id, NULL)) AS primaryCount,
        COUNT(DISTINCT IF((ACTP_S.value = 'повторно'), Action.id, NULL)) AS secondaryCount,
        COUNT(DISTINCT IF(ACTP_S.value = 'повторно в течение года', Action.id, NULL)) AS repeatedCount
        '''
    ]

    cond = [
        tableActionType['code'].eq(u'госп'),
        tableClientMonitoringKind['code'].inlist([u'Д', u'К']),
        tableAction['begDate'].dateLe(endDate),
        tableAction['begDate'].dateGe(begDate),
        tablePerson['deleted'].eq(0),
        tableActionProperty['deleted'].eq(0),
        tableActionPropertyType['deleted'].eq(0),
        tableAction['deleted'].eq('0'),
        tableEvent['deleted'].eq('0')
    ]

    if personId:
        cond.append(tableAction['setPerson_id'].eq(personId))

    stmt = db.selectStmt(queryTable, cols, cond, group=u'rowKey')
    query = db.query(stmt)
    return query


class CReportHospitalization(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Госпитализация')

    def getSetupDialog(self, parent):
        result = CReportPnd(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        begDate = params.get('begDate', None)
        endDate = params.get('endDate', None)
        personId = params.get('personId', None)
        rowGrouping = params.get('rowGrouping', 0)
        query = selectData(begDate, endDate, personId, rowGrouping)
        self.setQueryText(forceString(query.lastQuery()))
        if rowGrouping == 1:  # by personId
            forceKeyVal = forceRef
            keyValToString = lambda personId: forceString(
                QtGui.qApp.db.translate('vrbPersonWithSpeciality', 'id', personId, 'name')
            )
            keyName = u'Врач'
        else:
            forceKeyVal = lambda x: pyDate(forceDate(x))
            keyValToString = lambda x: forceString(QtCore.QDate(x))
            keyName = u'Дата'

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
            ('%20', [keyName], CReportBase.AlignLeft),
            ('%5', [u'ПНД'], CReportBase.AlignLeft),
            ('%5', [u'СМП'], CReportBase.AlignLeft),
            ('%5', [u'Др.учреждения'], CReportBase.AlignLeft),
            ('%5', [u'Первично'], CReportBase.AlignLeft),
            ('%5', [u'Повторно'], CReportBase.AlignLeft),
            ('%5', [u'из них: повторно в течение года'], CReportBase.AlignLeft)
        ]
        table = createTable(cursor, tableColumns)

        boldChars = QtGui.QTextCharFormat()
        boldChars.setFontWeight(QtGui.QFont.Bold)

        boldItalicChars = QtGui.QTextCharFormat()
        boldItalicChars.setFontWeight(QtGui.QFont.Bold)
        boldItalicChars.setFontItalic(True)

        total = [0] * (len(tableColumns) - 1)

        while query.next():
            record = query.record()

            i = table.addRow()
            table.setText(i, 0, keyValToString(forceKeyVal(record.value('rowKey'))))
            row = [
                forceInt(record.value('pnd')),
                forceInt(record.value('cmp')),
                forceInt(record.value('other')),
                forceInt(record.value('primaryCount')),
                forceInt(record.value('secondaryCount')),
                forceInt(record.value('repeatedCount'))
            ]

            for n, x in enumerate(row):
                table.setText(i, n + 1, x)
                total[n] = total[n] + x

        i = table.addRow()
        table.setText(i, 0, u'Всего', CReportBase.TableTotal)
        for n, x in enumerate(total):
            table.setText(i, n + 1, x, CReportBase.TableTotal)

        return doc


def main():
    import sys
    from s11main import CS11mainApp
    from library.database import connectDataBaseByInfo

    QtGui.qApp = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    connectionInfo = {
        'driverName': 'mysql',
        'host': '192.168.0.3',
        'port': 3306,
        'database': 'pes',
        'user': 'dbuser',
        'password': 'dbpassword',
        'connectionName': 'vista-med',
        'compressData': True,
        'afterConnectFunc': None
    }
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    w = CReportHospitalization(None)
    w.exec_()


if __name__ == '__main__':
    main()
