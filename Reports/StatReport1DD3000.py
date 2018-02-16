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


Columns = [
        (u'A00-T98', u'всего'),
        (u'A00-B99', u'Некоторые инфекционные и паразитарные болезни'),
        (u'D50-D89', u'Болезни крови и кроветворных органов, отдельные нарушения, вовлекающие иммунный механизм'),
        (u'E00-E90', u'Болезни эндокринной системы, расстройства питания и нарушения обмена веществ'),
        (u'F00-F99', u'Психические расстройства и расстройства поведения'),
        (u'G00-G99', u'Болезни нервной системы'),
        (u'H00-H59', u'Болезни глаза и его придаточного органа'),
        (u'H60-H95', u'Болезни уха и сосцевидного отростка'),
        (u'I00-I99', u'Болезни системы кровообращения'),
        (u'J00-J99', u'Болезни органов дыхания'),
        (u'K00-K93', u'Болезни органов пищеварения'),
        (u'L00-L99', u'Болезни кожи и подкожной клетчатки'),
        (u'M00-M99', u'Болезни костно-мышечной системы и соединительной ткани'),
        (u'N00-N99', u'Болезни мочеполовой системы'),
        (u'R00-R99', u'Симптомы, признаки и отклонения от нормы, выявленные при клинических и лабораторных исследованиях'),
        (u'S00-T98', u'Травмы, отравления и некоторые другие последствия воздействия внешних причин'),
    ]

Rows = [
        (u'Численность выявленных больных с данным заболеванием, установленным во время дополнительной диспансеризации', u'02'),
    ]

def selectData(begDate, endDate,  eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate):
    stmt="""
        SELECT
            Event.client_id AS client_id,
            Diagnosis.mkb AS mkb,
            IF((rbDiseaseCharacter.code='1' AND rbDiseaseStage.code='1') OR rbDiseaseCharacter.code='2', 1, 0) AS R2a,
            IF(rbDiseaseCharacter.code IS NOT NULL, 1, 0) AS R2b,
            IF(rbDiagnosisType.code='1', 1, 0) AS final,
            IF(rbHealthGroup.code = '3', 1, 0) AS R3c,
            IF(rbDispanser.observed OR rbDiagnosticResult.code='32',  1, 0) AS R4c,
            IF(rbHealthGroup.code > '3', 1, 0) AS R5c,
            IF(Diagnostic.hospital>1, 1, 0) AS R6c
        FROM
            Diagnostic
            LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id
            LEFT JOIN Event     ON Event.id = Diagnostic.event_id
            LEFT JOIN Client    ON Client.id = Event.client_id
            LEFT JOIN rbDiagnosisType    ON rbDiagnosisType.id    = Diagnostic.diagnosisType_id
            LEFT JOIN rbDiseaseCharacter ON rbDiseaseCharacter.id = Diagnostic.character_id
            LEFT JOIN rbDiseaseStage     ON rbDiseaseStage.id     = Diagnostic.stage_id
            LEFT JOIN rbHealthGroup      ON rbHealthGroup.id      = Diagnostic.healthGroup_id
            LEFT JOIN rbDispanser        ON rbDispanser.id        = Diagnostic.dispanser_id
            LEFT JOIN rbDiagnosticResult ON rbDiagnosticResult.id = Diagnostic.result_id
            LEFT JOIN Account_Item       ON ( Account_Item.id = (SELECT max(AI.id) FROM Account_Item AS AI WHERE AI.deleted=0 AND AI.event_id = Event.id AND AI.date IS NOT NULL AND AI.refuseType_id IS NULL AND AI.reexposeItem_id IS NULL AND AI.visit_id IS NULL AND AI.action_id IS NULL)
                                            )
        WHERE
            Diagnostic.deleted=0 AND Event.deleted=0 AND
            %s
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
    return db.query(stmt % (db.joinAnd(cond)))


class CStatReport1DD3000(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(True)
        self.setTitle(u'Итоги дополнительной диспансеризации граждан (3000)', u'Итоги дополнительной диспансеризации')

    def build(self, params):
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Итоги дополнительной диспансеризации граждан')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        self.buildInt(params, cursor)

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText('\n\n\n')
        cursor.insertBlock()
        rows = []
        orgId = QtGui.qApp.currentOrgId()
        db = QtGui.qApp.db
        table = db.table('Organisation')
        record = db.getRecordEx(table, table['chief'], [table['id'].eq(orgId), table['deleted'].eq(0)])
        chief = forceString(record.value('chief'))
        text0 = u'Руководитель ЛПУ                                   %s'%(chief)
        rows.append([text0])
        rows.append([u'\n'])
        rows.append([u'_____________________________'])
        rows.append([u'                    (подпись)'])
        rows.append([u'\n                                                                                       М.П.\n'])
        rows.append([u'"_____"________________2010г.'])
        columnDescrs = [('100%', [], CReportBase.AlignLeft)]
        table1 = createTable (
            cursor, columnDescrs, headerRowCount=len(rows), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(rows):
            table1.setText(i, 0, row[0])
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        return doc


    def buildInt(self, params, cursor):
        global Columns
        global Rows

        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        eventTypeId = params.get('eventTypeId', None)
        onlyPermanentAttach =  params.get('onlyPermanentAttach', False)
        onlyPayedEvents = params.get('onlyPayedEvents', False)
        begPayDate = params.get('begPayDate', QtCore.QDate())
        endPayDate = params.get('endPayDate', QtCore.QDate())

        mapColumns = createMapCodeToRowIdx( [column[0] for column in Columns] )

        reportRowSize = len(Columns)
        reportData = [ [0] * reportRowSize for row in xrange(5) ]
        query = selectData(begDate, endDate, eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate)

        prevClientId = None
        clientData = None
        while query.next() :
            record = query.record()
            clientId = forceInt(record.value('client_id'))
            mkb      = normalizeMKB(forceString(record.value('mkb')))
            r2       = forceBool(record.value('R2b'))
            final    = forceBool(record.value('final'))
            r3       = final and r2 and forceBool(record.value('R3c'))
            r4       = final and r2 and forceBool(record.value('R4c'))
            r5       = final and r2 and forceBool(record.value('R5c'))
            r6       = r5 and forceBool(record.value('R6c'))

            if prevClientId != clientId:
                addClientData(reportData, clientData)
                clientData = [ [False] * reportRowSize for row in xrange(5) ]
                prevClientId = clientId

            diagColumns = mapColumns.get(mkb, [])
            if not r2 and diagColumns:
                pass
            if r2:
                setSigns(clientData, 0, diagColumns)
            if r3:
                setSigns(clientData, 1, diagColumns)
            if r4:
                setSigns(clientData, 2, diagColumns)
            if r5:
                setSigns(clientData, 3, diagColumns)
            if r6:
                setSigns(clientData, 4, diagColumns)
        addClientData(reportData, clientData)


        # now text
        cursor.insertText(u'(3000)')
        cursor.insertBlock()

        tableColumns = [
            ('15%', [u'Наименование заболевания', u'', u'1', u'Код по МКБ-10'], CReportBase.AlignLeft),
            ('5%', [u'№ строки', u'', u'2', '01'], CReportBase.AlignCenter),
            ('5%', [Columns[0][1], u'', u'3', Columns[0][0]], CReportBase.AlignRight),
            ]
        tableColumns.extend([('5%', [u'', Columns[i][1], str(i+3), Columns[i][0]], CReportBase.AlignRight) for i in xrange(1, len(Columns))])

        table = createTable(cursor, tableColumns, headerRowCount=1, border=3, cellPadding=2, cellSpacing=0)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 1, len(Columns)-1)

        for iRow, row in enumerate(Rows):
            i = table.addRow()
            for j in xrange(2):
                table.setText(i, j, row[j], CReportBase.TableHeader)
            for j in xrange(reportRowSize):
                table.setText(i, 2+j, reportData[iRow][j])
        return dict(zip([c[0] for c in Columns], reportData[0]))


def setSigns(clientData, row, columns):
    clientLine = clientData[row]
    for column in columns:
        clientLine[column] = True


def addClientData(reportData, clientData):
    if clientData:
        for row, clientLine in enumerate(clientData):
            reportLine = reportData[row]
            for column, sign in enumerate(clientLine):
                if sign:
                    reportLine[column] += 1
