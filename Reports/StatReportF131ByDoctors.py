# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.database           import addDateInRange
from library.Utils              import forceInt, forceString, getVal, formatName

from Reports.Report             import CReport
from Reports.ReportBase         import createTable, CReportBase
from Reports.StatReport1NPUtil  import havePermanentAttach


def selectData(begDate, endDate,  eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate):
    stmt="""
        SELECT
            rbSpeciality.name as specialityName,
            Person.lastName, Person.firstName, Person.patrName, Person.code,
            COUNT(Diagnostic.id) AS cntEvents,
            SUM( %s ) AS cntExecuted,
            SUM( isEventPayed(Diagnostic.event_id) ) as cntPayed,
            SUM( rbHealthGroup.code = '1' ) as cntHG1,
            SUM( rbHealthGroup.code = '2' ) as cntHG2,
            SUM( rbHealthGroup.code = '3' ) as cntHG3,
            SUM( rbHealthGroup.code = '4' ) as cntHG4,
            SUM( rbHealthGroup.code = '5' ) as cntHG5

        FROM Diagnostic
        LEFT JOIN Event             ON Event.id = Diagnostic.event_id
        LEFT JOIN Client            ON Client.id = Event.client_id
        LEFT JOIN rbDiagnosisType   ON rbDiagnosisType.id = Diagnostic.diagnosisType_id
        LEFT JOIN Person            ON Person.id = Diagnostic.person_id
        LEFT JOIN rbSpeciality      ON rbSpeciality.id = Person.speciality_id
        LEFT JOIN rbHealthGroup     ON rbHealthGroup.id = Diagnostic.healthGroup_id
        LEFT JOIN Account_Item ON ( Account_Item.id = (SELECT max(AI.id) FROM Account_Item AS AI WHERE AI.event_id = Event.id AND AI.deleted=0 AND AI.date IS NOT NULL AND AI.refuseType_id IS NULL AND AI.reexposeItem_id IS NULL AND AI.visit_id IS NULL AND AI.action_id IS NULL)
                                  )
        WHERE
            Event.deleted = 0 AND Diagnostic.deleted = 0 AND %s
        GROUP BY
            Diagnostic.person_id
        ORDER BY
            rbSpeciality.name, Person.lastName, Person.firstName, Person.patrName
    """
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    setDate  = tableEvent['setDate']
    execDate = tableEvent['execDate']
    tableDiagnosisType = db.table('rbDiagnosisType')
    cond = []
    cond.append(tableDiagnosisType['code'].inlist(['1', '2']))
    dateCond = []
    dateCond.append(db.joinAnd([setDate.le(endDate), execDate.isNull()]))
    dateCond.append(db.joinAnd([execDate.ge(begDate), execDate.le(endDate)]))
    dateCond.append(db.joinAnd([setDate.ge(begDate), execDate.le(endDate)]))
    cond.append(db.joinOr(dateCond))
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if onlyPermanentAttach:
        cond.append(havePermanentAttach(endDate))
    if onlyPayedEvents:
        cond.append('isEventPayed(Event.id)')
        tableAccountItem = db.table('Account_Item')
        addDateInRange(cond, tableAccountItem['date'], begPayDate, endPayDate)

    return db.query(stmt % (execDate.between(begDate, endDate), db.joinAnd(cond)))


class CStatReportF131ByDoctors(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(True)
        self.setTitle(u'Сводка по Ф.131 по врачам', u'Сводка по Ф.131')


    def build(self, params):
        begDate = getVal(params, 'begDate', QtCore.QDate())
        endDate = getVal(params, 'endDate', QtCore.QDate())
        eventTypeId = getVal(params, 'eventTypeId', None)
        onlyPermanentAttach = getVal(params, 'onlyPermanentAttach', False)
        onlyPayedEvents = getVal(params, 'onlyPayedEvents', False)
        begPayDate = getVal(params, 'begPayDate', QtCore.QDate())
        endPayDate = getVal(params, 'endPayDate', QtCore.QDate())

        reportRowSize = 11
        reportData = []
        query = selectData(begDate, endDate, eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate)
        self.setQueryText(forceString(query.lastQuery()))

        while query.next() :
            record = query.record()
            specialityName = forceString(record.value('specialityName'))
            lastName = forceString(record.value('lastName'))
            firstName = forceString(record.value('firstName'))
            patrName = forceString(record.value('patrName'))
            code = forceString(record.value('code'))
            cntEvents = forceInt(record.value('cntEvents'))
            cntExecuted = forceInt(record.value('cntExecuted'))
            cntPayed = forceInt(record.value('cntPayed'))
            cntHG1 = forceInt(record.value('cntHG1'))
            cntHG2 = forceInt(record.value('cntHG2'))
            cntHG3 = forceInt(record.value('cntHG3'))
            cntHG4 = forceInt(record.value('cntHG4'))
            cntHG5 = forceInt(record.value('cntHG5'))
            name = formatName(lastName,  firstName, patrName)
            reportData.append([specialityName if specialityName else u'Без указания специальности',
                               name if name else u'Без указания врача',
                               code,
                               cntEvents,
                               cntExecuted,
                               cntPayed,
                               cntHG1,
                               cntHG2,
                               cntHG3,
                               cntHG4,
                               cntHG5,
                               ])

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Сводка по Ф.131 по врачам')
        cursor.insertBlock()
        self.dumpParams(cursor, params)

        tableColumns = [
                          ('30%', [ u'Врач', u'ФИО'], CReportBase.AlignLeft ),
                          ('5%',  [ u'',     u'код'], CReportBase.AlignLeft ),
                          ('10%', [ u'Всего'     ], CReportBase.AlignRight ),
                          ('10%', [ u'Закончено' ], CReportBase.AlignRight ),
                          ('10%', [ u'Оплачено'  ], CReportBase.AlignRight ),
                          ( '7%', [ u'по группам здоровья', u'1'], CReportBase.AlignRight ),
                          ( '7%', [ u'',                    u'2'], CReportBase.AlignRight ),
                          ( '7%', [ u'',                    u'3'], CReportBase.AlignRight ),
                          ( '7%', [ u'',                    u'4'], CReportBase.AlignRight ),
                          ( '7%', [ u'',                    u'5'], CReportBase.AlignRight )
                       ]

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 1, 2)
        for i in xrange(3):
            table.mergeCells(0, i+2, 2, 1)
        table.mergeCells(0, 5, 1, 5)

        prevSpecialityName = None
        totalBySpeciality = [0]*reportRowSize
        totalByReport = [0]*reportRowSize
        for i, reportLine in enumerate(reportData):
            specialityName = reportLine[0]
            if prevSpecialityName != specialityName:
                if prevSpecialityName != None:
                    self.addTotal(table, u'Всего по специальности', totalBySpeciality)
                    totalBySpeciality = [0]*reportRowSize
                self.addSpecialityHeader(table, specialityName)
                prevSpecialityName = specialityName

            i = table.addRow()
            for j in xrange(reportRowSize-1):
                table.setText(i, j, reportLine[j+1])
            for j in xrange(3, reportRowSize):
                totalBySpeciality[j] += reportLine[j]
                totalByReport[j] += reportLine[j]
        self.addTotal(table, u'Всего по специальности', totalBySpeciality)
        self.addTotal(table, u'Всего', totalByReport)
        return doc

    def addSpecialityHeader(self, table, specialityName):
#        format = QtGui.QTextCharFormat()
        i = table.addRow()
        table.mergeCells(i, 0, 1, 10)
        table.setText(i, 0, specialityName, CReportBase.TableHeader)


    def addTotal(self, table, title, reportLine):
        i = table.addRow()
        table.mergeCells(i, 0, 1, 2)
        table.setText(i, 0, title, CReportBase.TableTotal)
        for j in xrange(2, 10):
            table.setText(i, j, reportLine[j+1])

