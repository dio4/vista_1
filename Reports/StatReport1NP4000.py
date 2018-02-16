# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.database   import addDateInRange
from library.Utils      import forceDate, forceInt, getVal, calcAgeInYears

from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.StatReport1NPUtil  import ageSexRows, dispatchAgeSex, havePermanentAttach


def selectData(begDate, endDate,  eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate):
    stmt="""
SELECT
    Event.execDate as date,
    Client.birthDate AS birthDate,
    Client.sex AS sex,
    (SELECT
        COUNT(DISTINCT Diagnosis.MKB)
     FROM
        Diagnostic
        LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id
        WHERE Diagnostic.event_id = Event.id AND Diagnostic.deleted=0 AND Diagnosis.MKB > 'A' AND Diagnosis.MKB < 'U'
    ) AS cnt
FROM Event
LEFT JOIN Client ON Client.id = Event.client_id
LEFT JOIN Account_Item ON ( Account_Item.id = (SELECT max(AI.id) FROM Account_Item AS AI WHERE AI.event_id = Event.id AND AI.deleted=0 AND AI.date IS NOT NULL AND AI.refuseType_id IS NULL AND AI.reexposeItem_id IS NULL AND AI.visit_id IS NULL AND AI.action_id IS NULL)
                          )
WHERE Event.deleted=0 AND %s
    """
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    cond = []
    addDateInRange(cond, tableEvent['execDate'], begDate, endDate)
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if onlyPermanentAttach:
        cond.append(havePermanentAttach(endDate))
    if onlyPayedEvents:
        cond.append('isEventPayed(Event.id)')
        tableAccountItem = db.table('Account_Item')
        addDateInRange(cond, tableAccountItem['date'], begPayDate, endPayDate)
    return db.query(stmt % (db.joinAnd(cond)))


class CStatReport1NP4000(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(True)
        self.setTitle(u'Итоги дополнительной диспансеризации граждан (4000)', u'Итоги дополнительной диспансеризации')


    def build(self, params):
        begDate = getVal(params, 'begDate', QtCore.QDate())
        endDate = getVal(params, 'endDate', QtCore.QDate())
        eventTypeId = getVal(params, 'eventTypeId', None)
        onlyPermanentAttach =  getVal(params, 'onlyPermanentAttach', False)
        onlyPayedEvents = getVal(params, 'onlyPayedEvents', False)
        begPayDate = getVal(params, 'begPayDate', QtCore.QDate())
        endPayDate = getVal(params, 'endPayDate', QtCore.QDate())

        reportRowSize = 4
        reportData = [ [0] * reportRowSize for row in ageSexRows ]
        query = selectData(begDate, endDate, eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate)

        while query.next() :
            record = query.record()
            age  = calcAgeInYears(forceDate(record.value('birthDate')), forceDate(record.value('date')))
            sex  = forceInt(record.value('sex'))
            cnt  = forceInt(record.value('cnt'))
            if cnt >= 3:
                column = 3
            else:
                column = cnt
            for row in dispatchAgeSex(age, sex):
                reportData[row][column] += 1

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Итоги дополнительной диспансеризации граждан')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertText(u'(4000)')
        cursor.insertBlock()

        tableColumns = [
            ('30%', [u'Возрастной диапазон работающих граждан, прошедших диспансеризацию', u'', u'1'], CReportBase.AlignLeft),
            ('10%', [u'№ строки', u'', u'2'], CReportBase.AlignCenter),
            ('10%', [u'Распределение прошедших дополнительную диспансеризацию граждан по количеству заболеваний', u'нет заболеваний', u'3'], CReportBase.AlignRight),
            ('10%', [u'', u'1 заболевание',   u'4'], CReportBase.AlignRight),
            ('10%', [u'', u'2 заболевания',  u'5'], CReportBase.AlignRight),
            ('10%', [u'', u'3 и более заболеваний',   u'6'], CReportBase.AlignRight),
            ]
        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 1, 4)

        for iRow, row in enumerate(ageSexRows):
            i = table.addRow()
            for j in xrange(2):
                table.setText(i, j, row[j])
            for j in xrange(4):
                table.setText(i, 2+j, reportData[iRow][j])
        return doc

