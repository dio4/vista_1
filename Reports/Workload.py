# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils              import forceInt, forceString, getVal
from Reports.Report             import CReport
from Reports.ReportBase         import createTable, CReportBase
from Reports.ReportSetupDialog  import CReportSetupDialog


def selectData(begDate, endDate, eventTypeId):
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    cond = [
        tableEvent['createDatetime'].ge(begDate),
        tableEvent['createDatetime'].lt(endDate.addDays(1)),
        ]
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    condStr = db.joinAnd(cond)
    stmt=u"""
SELECT
    Person.login, Person.lastName, Person.firstName, Person.patrName,
    COUNT(*) AS cnt1, SUM(IF(Event.execDate is null,1,0)) AS cnt2
FROM
    Event
    LEFT JOIN Person ON Person.id=Event.createPerson_id
WHERE Event.deleted=0 AND %s
GROUP BY Event.createPerson_id
ORDER BY Person.lastName, Person.firstName, Person.patrName
    """ % (condStr)
    return db.query(stmt)


class CWorkload(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Выработка')

    def getSetupDialog(self, parent):
        result = CReportSetupDialog(parent)
        result.setTitle(self.title())
        result.setEventTypeVisible(True)
        result.setPayPeriodVisible(False)
        result.setWorkTypeVisible(False)
        result.chkOnlyPermanentAttach.setVisible(False)
        result.chkOnlyPayedEvents.setVisible(False)
        return result

    def build(self, params):
        begDate = getVal(params, 'begDate', QtCore.QDate())
        endDate = getVal(params, 'endDate', QtCore.QDate())
        eventTypeId = getVal(params, 'eventTypeId', None)

        db = QtGui.qApp.db

        reportData = []

        query = selectData(begDate, endDate, eventTypeId)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next() :
            record = query.record()
            login = forceString(record.value('login'))
            lastName = forceString(record.value('lastName'))
            firstName = forceString(record.value('firstName'))
            patrName = forceString(record.value('patrName'))
            cnt1 = forceInt(record.value('cnt1'))
            cnt2 = forceInt(record.value('cnt2'))
            reportData.append([login, lastName, firstName, patrName, cnt1, cnt2])

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ( '10%', [u'Регистрационное имя'], CReportBase.AlignLeft),
            ( '20%', [u'Фамилия'], CReportBase.AlignLeft),
            ( '20%', [u'Имя'], CReportBase.AlignLeft),
            ( '20%', [u'Отчество'], CReportBase.AlignLeft),
            ( '10%', [u'Всего'], CReportBase.AlignRight),
            ( '10%', [u'В т.ч. без даты выполнения'], CReportBase.AlignRight),
        ]

        table = createTable(cursor, tableColumns)
        totalCnt1 = 0
        totalCnt2 = 0

        for row in reportData:
            i = table.addRow()
            for j in xrange(len(row)):
                table.setText(i, j, row[j])
            totalCnt1 += row[4]
            totalCnt2 += row[5]

        i = table.addRow()
        table.mergeCells(i, 0, 1, 4)
        table.setText(i, 0, u'всего', CReportBase.TableTotal)
        table.setText(i, 4, totalCnt1, CReportBase.TableTotal)
        table.setText(i, 5, totalCnt2, CReportBase.TableTotal)
        return doc