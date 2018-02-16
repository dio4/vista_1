# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.database           import addDateInRange
from library.MapCode            import createMapCodeToRowIdx
from library.Utils              import forceBool, forceInt, forceString

from Reports.Report             import normalizeMKB, CReport
from Reports.ReportBase         import createTable, CReportBase
from Reports.StatReport1NPUtil  import havePermanentAttach


ColumnGroups = [
        (u'A15-A19', u'туберкулез A15-A19 (чел.)'),
        (u'C00-C97', u'злокачественные новообразования C00-C97 (чел.)'),
        (u'E10-E14', u'сахарный диабет E10-E14 (чел.)'),
        (u'D66-D67, D68.0-D68.1',    u'гемофилия D66-D67, D68.0-D68.1 (чел.)'),
        (u'B16, B17.1, B18.0-B18.2', u'гепатиты B и C B16, B17.1, B18.0-B18.2 (чел.)'),
    ]

def selectData(begDate, endDate,  eventTypeId, stageId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate):
    stmt="""
        SELECT
            Event.client_id AS client_id,
            Diagnosis.mkb AS mkb,
            ((rbDiseaseCharacter.code='1' AND rbDiseaseStage.code='1') OR rbDiseaseCharacter.code='2') AS P1,
            (%s) AS P2
        FROM
            Diagnostic
            LEFT JOIN Diagnosis          ON Diagnosis.id = Diagnostic.diagnosis_id
            LEFT JOIN Event              ON Event.id = Diagnostic.event_id
            LEFT JOIN Client             ON Client.id = Event.client_id
            LEFT JOIN rbDiseaseCharacter ON rbDiseaseCharacter.id = Diagnostic.character_id
            LEFT JOIN rbDiseaseStage     ON rbDiseaseStage.id     = Diagnostic.stage_id
            LEFT JOIN Account_Item       ON ( Account_Item.id = (SELECT max(AI.id) FROM Account_Item AS AI WHERE AI.event_id = Event.id AND AI.deleted=0 AND AI.date IS NOT NULL AND AI.refuseType_id IS NULL AND AI.reexposeItem_id IS NULL AND AI.visit_id IS NULL AND AI.action_id IS NULL)
                                            )
        WHERE
            Event.deleted=0 AND Diagnostic.deleted=0 AND %s
        ORDER BY
            Event.client_id, Diagnosis.mkb, Diagnostic.diagnosisType_id, Diagnostic.id
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

    stageCond = ('Diagnostic.stage_id=%s'%stageId) if stageId else 'Diagnostic.stage_id IS NULL'
    return db.query(stmt % (stageCond, db.joinAnd(cond)))


class CStatReport1NP7000(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(True)
        self.setTitle(u'Итоги дополнительной диспансеризации граждан (7000)', u'Итоги дополнительной диспансеризации')


    def getSetupDialog(self, parent):
        result = CReport.getSetupDialog(self, parent)
        result.setStageVisible(True)
        return result


    def build(self, params):
        def addOnes(rows, column):
            for row in rows:
                reportData[row][column] += 1

        global ColumnGroups

        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        eventTypeId = params.get('eventTypeId', None)
        stageId = params.get('stageId', None)
        onlyPermanentAttach =  params.get('onlyPermanentAttach', False)
        onlyPayedEvents = params.get('onlyPayedEvents', False)
        begPayDate = params.get('begPayDate', QtCore.QDate())
        endPayDate = params.get('endPayDate', QtCore.QDate())

        db = QtGui.qApp.db

        mapColumnGroups = createMapCodeToRowIdx( [columnGroup[0] for columnGroup in ColumnGroups] )
        reportRowSize = 3
        reportData = [ [0] * reportRowSize for columnGroup in ColumnGroups ]
        query = selectData(begDate, endDate, eventTypeId, stageId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate)

        prevClientId   = None
        prevMKB        = None
        while query.next() :
            record = query.record()
            clientId = forceInt(record.value('client_id'))
            mkb      = normalizeMKB(forceString(record.value('mkb')))
            if prevClientId != clientId or prevMKB != mkb:
                prevClientId = clientId
                prevMKB = mkb
                diagColumnGroups = mapColumnGroups.get(mkb, [])
                addOnes(diagColumnGroups,  0)
                if forceBool(record.value('P1')):
                    addOnes(diagColumnGroups, 1)
                    if forceBool(record.value('P2')):
                        addOnes(diagColumnGroups, 2)


        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Итоги дополнительной диспансеризации граждан')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertText(u'(7000)')
        cursor.insertBlock()

        tableColumns = [
                          ('5%',
                            [ u'Выявлено больных с социально-значимыми заболеваниями (код по МКБ-10)' if i == 0 else u'',
                              ColumnGroups[i/3][1] if i%3 ==0 else u'',
                              [u'всего', u'в том числе впер-\nвые выяв-\nлено', u'из них на заданных ста-\nдиях забо-\nлева\nния'][i%3],
                              str(i+1)
                            ],
                            CReportBase.AlignRight
                          ) for i in xrange(3*len(ColumnGroups))
                       ]

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 1, 3*len(ColumnGroups))
        for i in xrange(len(ColumnGroups)):
            table.mergeCells(1, i*3, 1, 3)

        i = table.addRow()
        for j in xrange(3*len(ColumnGroups)):
            table.setText(i, j, reportData[j/3][j%3])
        return doc

