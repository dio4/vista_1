# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.database           import addDateInRange
from library.Utils              import forceInt, forceString, getVal

from Reports.Report             import CReport
from Reports.ReportBase         import createTable, CReportBase
from Reports.StatReport1NPUtil  import havePermanentAttach


groupTitles = [
        u'Образование (М80)',
        u'Здравоохранение (N85.1-N85.14)',
        u'Предоставление социальных услуг (N85.3)',
        u'Деятельность по организации отдыха, развлечений, культуры и спорта (О92)',
        u'Научно-исследовательские учреждения (К73)',
        u'Другие коды',
       ]


def dispatch(okved):
    if okved[:3] == u'M80':
        return 0
    if okved[:5] >= u'N85.1' and okved[:6] <= u'N85.14':
        return 1
    if okved[:5] == u'N85.3':
        return 2
    if okved[:3] == u'O92':
        return 3
    if okved[:3] == u'K73':
        return 4
    return 5


def selectData(begDate, endDate,  eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate):
    stmt="""
        SELECT
            Organisation.OKVED AS OKVED, Organisation.shortName AS shortName,
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
        LEFT JOIN rbDiagnosisType   ON rbDiagnosisType.id = Diagnostic.diagnosisType_id
        LEFT JOIN Person            ON Person.id = Diagnostic.person_id
        LEFT JOIN rbSpeciality      ON rbSpeciality.id = Person.speciality_id
        LEFT JOIN rbHealthGroup     ON rbHealthGroup.id = Diagnostic.healthGroup_id
        LEFT JOIN Client            ON Client.id = Event.client_id
        LEFT JOIN ClientWork        ON (ClientWork.client_id = Client.id
                                        AND ClientWork.id = (SELECT MAX(id) FROM ClientWork AS CW WHERE CW.client_id = Client.id)
                                       )
        LEFT JOIN Organisation      ON Organisation.id = ClientWork.org_id
        LEFT JOIN Account_Item ON ( Account_Item.id = (SELECT max(AI.id) FROM Account_Item AS AI WHERE AI.event_id = Event.id AND AI.deleted=0 AND AI.date IS NOT NULL AND AI.refuseType_id IS NULL AND AI.reexposeItem_id IS NULL AND AI.visit_id IS NULL AND AI.action_id IS NULL)
                                  )
        WHERE
            Event.deleted = 0 AND Diagnostic.deleted = 0 AND %s

        GROUP BY
            ClientWork.org_id
        ORDER BY
            Organisation.OKVED, Organisation.shortName
    """
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    setDate  = tableEvent['setDate']
    execDate = tableEvent['execDate']
    tableDiagnosisType = db.table('rbDiagnosisType')
    cond = []
    cond.append(tableDiagnosisType['code'].eq('1'))
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

    s=stmt % (execDate.between(begDate, endDate), db.joinAnd(cond))
    return db.query(stmt % (execDate.between(begDate, endDate), db.joinAnd(cond)))


class CStatReportF131ByEmployer(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(True)
        self.setTitle(u'Сводка по Ф.131 по работодателям', u'Сводка по Ф.131')


    def build(self, params):
        global groupTitles

        begDate = getVal(params, 'begDate', QtCore.QDate())
        endDate = getVal(params, 'endDate', QtCore.QDate())
        eventTypeId = getVal(params, 'eventTypeId', None)
        onlyPermanentAttach = getVal(params, 'onlyPermanentAttach', False)
        onlyPayedEvents = getVal(params, 'onlyPayedEvents', False)
        begPayDate = getVal(params, 'begPayDate', QtCore.QDate())
        endPayDate = getVal(params, 'endPayDate', QtCore.QDate())

        reportRowSize = 10
        reportDataByGroups = [ [] for group in groupTitles ]
        reportData = [ ]
        query = selectData(begDate, endDate, eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate)

        prevSpecialityId  = None
        while query.next() :
            record = query.record()
            specialityName = forceString(record.value('specialityName'))
#            specialityId = forceInt(record.value('speciality_id'))
            okved = forceString(record.value('OKVED'))
            shortName = forceString(record.value('shortName'))
            cntEvents = forceInt(record.value('cntEvents'))
            cntExecuted = forceInt(record.value('cntExecuted'))
            cntPayed = forceInt(record.value('cntPayed'))
            cntHG1 = forceInt(record.value('cntHG1'))
            cntHG2 = forceInt(record.value('cntHG2'))
            cntHG3 = forceInt(record.value('cntHG3'))
            cntHG4 = forceInt(record.value('cntHG4'))
            cntHG5 = forceInt(record.value('cntHG5'))
            reportData = reportDataByGroups[dispatch(okved)]
            reportData.append([okved,
                               shortName,
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
        cursor.insertText(u'Сводка по Ф.131 по работодателям')
        cursor.insertBlock()
        self.dumpParams(cursor, params)

        tableColumns = [
                          ('10%', [ u'ОКВЭД' ], CReportBase.AlignLeft ),
                          ('35%', [ u'Организация' ], CReportBase.AlignLeft ),
                          ('10%', [ u'Всего'     ], CReportBase.AlignRight ),
                          ('10%', [ u'Закончено' ], CReportBase.AlignRight ),
                          ('10%', [ u'Оплачено'  ], CReportBase.AlignRight ),
                          ( '5%', [ u'По группам здоровья', u'1'], CReportBase.AlignRight ),
                          ( '5%', [ u'',                    u'2'], CReportBase.AlignRight ),
                          ( '5%', [ u'',                    u'3'], CReportBase.AlignRight ),
                          ( '5%', [ u'',                    u'4'], CReportBase.AlignRight ),
                          ( '5%', [ u'',                    u'5'], CReportBase.AlignRight )
                       ]

        table = createTable(cursor, tableColumns)
        for i in xrange(5):
            table.mergeCells(0, i, 2, 1)
        table.mergeCells(0, 5, 1, 5)


        totalByReport = [0]*reportRowSize
        for iGroup, reportData in enumerate(reportDataByGroups):
            if reportData:
                totalByGroup = [0]*reportRowSize
                self.addGroupHeader(table, groupTitles[iGroup])
                for i, reportLine in enumerate(reportData):
                    i = table.addRow()
                    for j in xrange(reportRowSize):
                        table.setText(i, j, reportLine[j])
                    for j in xrange(2, reportRowSize):
                        totalByGroup[j] += reportLine[j]
                        totalByReport[j] += reportLine[j]
                self.addTotal(table, u'всего по группе', totalByGroup)
        self.addTotal(table, u'Всего', totalByReport)
        return doc

    def addGroupHeader(self, table, group):
        i = table.addRow()
        table.mergeCells(i, 0, 1, 10)
        table.setText(i, 0, group, CReportBase.TableHeader)


    def addTotal(self, table, title, reportLine):
        i = table.addRow()
        table.mergeCells(i, 0, 1, 2)
        table.setText(i, 0, title, CReportBase.TableTotal)
        for j in xrange(2, 10):
            table.setText(i, j, reportLine[j])
