# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2015 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Reports.ReportLeavedClients import CLeavedClients
from library.Utils          import forceInt, forceString, forceDateTime
from Reports.Report         import CReport
from Reports.ReportBase     import createTable, CReportBase


class CReportVerifiedAction(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Контроль услуг')

    def getSetupDialog(self, parent):
        result = CLeavedClients(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        def selectData(params):
            begDate = params.get('begDate', None).toString(QtCore.Qt.ISODate)
            endDate = params.get('endDate', None).toString(QtCore.Qt.ISODate)

            db = QtGui.qApp.db

            tableAction = db.table('Action').alias('a')

            cond = [
                tableAction['begDate'].dateGe(begDate),
                tableAction['begDate'].dateLe(endDate)
            ]

            stmt = u'''
                SELECT
                    e.id AS eventId,
                    e.externalId AS eventExternalId,

                    at.code AS actionCode,
                    at.name AS actionName,

                    a.isVerified AS verifiedStatus,
                    a.begDate AS actionBegDate,
                    a.endDate AS actionEndDate
                FROM
                    Action a
                    LEFT JOIN ActionType at ON a.actionType_id = at.id
                    LEFT JOIN Event e ON a.event_id = e.id
                WHERE
                    a.isVerified = 2;
                    AND %s
            ''' % db.joinAnd(cond)

            return db.query(stmt)

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
            ('%2', [u'№ п/п'], CReportBase.AlignRight),
            ('%2', [u'Код карточки'], CReportBase.AlignRight),
            ('%10', [u'Внешний идентификатор'], CReportBase.AlignLeft),
            ('%10', [u'Код действия'], CReportBase.AlignLeft),
            ('%20', [u'Наименование'], CReportBase.AlignLeft),
            ('%5', [u'Статус проверки'], CReportBase.AlignLeft),
            ('%5', [u'Дата начала'], CReportBase.AlignLeft),
            ('%5', [u'Дата окончания'], CReportBase.AlignLeft)
        ]

        table = createTable(cursor, tableColumns)

        while query.next():
            record = query.record()

            eventId = forceString(record.value('eventId'))
            actionCode = forceString(record.value('actionCode'))
            actionName = forceString(record.value('actionName'))
            eventExternalId = forceString(record.value('eventExternalId'))
            # verifiedStatus = forceString(record.value('verifiedStatus'))

            actionBegDate = forceDateTime(record.value('actionBegDate')).toString('dd.MM.yyyy hh:mm')
            actionEndDate = forceDateTime(record.value('actionEndDate')).toString('dd.MM.yyyy hh:mm')

            i = table.addRow()
            table.setText(i, 0, i)
            table.setText(i, 1, eventId)
            table.setText(i, 2, eventExternalId)
            table.setText(i, 3, actionCode)
            table.setText(i, 4, actionName)
            table.setText(i, 5, u"Проверено с ошибкой")
            table.setText(i, 6, actionBegDate)
            table.setText(i, 7, actionEndDate)

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
        'database': 'b15',
        'user': 'dbuser',
        'password': 'dbpassword',
        'connectionName': 'vista-med',
        'compressData': True,
        'afterConnectFunc': None
    }
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    w = CReportVerifiedAction(None)
    w.exec_()
    sys.exit(QtGui.qApp.exec_())


if __name__ == '__main__':
    main()
