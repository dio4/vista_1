# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.database           import addDateInRange
from library.Utils              import forceBool, forceInt, forceString, getVal

from Reports.Report             import CReport
from Reports.ReportBase         import createTable, CReportBase
from Reports.StatReport1NPUtil  import havePermanentAttach


def selectData(begDate, endDate,  eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate):
    stmt="""
        SELECT
            Organisation.OKVED as OKVED,
            rbDispanser.code in ('2', '6') AS dispanser,
            rbDiseaseStage.code as stage,
            rbHealthGroup.code as `group`,
            COUNT(Event.id) as cnt
        FROM
            Event
            LEFT JOIN Client ON Client.id = Event.client_id
            LEFT JOIN ClientWork     ON (    ClientWork.client_id = Client.id
                                         AND ClientWork.id = (SELECT MAX(id) FROM ClientWork AS CW WHERE CW.client_id = Client.id)
                                        )
            LEFT JOIN Organisation   ON Organisation.id = ClientWork.org_id
            LEFT JOIN Diagnostic AS D2 ON ( D2.event_id = Event.id AND D2.id = (
                SELECT MIN(D3.id)
                FROM Diagnostic AS D3
                LEFT JOIN rbDispanser  ON rbDispanser.id = D3.dispanser_id
                LEFT JOIN rbDiseaseStage ON rbDiseaseStage.id = D3.stage_id
                WHERE D3.event_id = Event.id
                  AND D3.deleted = 0
                  AND rbDispanser.code in ('2', '6')
                  AND IF(rbDiseaseStage.code IS NULL, 0,rbDiseaseStage.code) = (
                    SELECT MAX(IF(rbDiseaseStage.code IS NULL, 0,rbDiseaseStage.code))
                    FROM Diagnostic AS D4
                    LEFT JOIN rbDispanser  ON rbDispanser.id = D4.dispanser_id
                    LEFT JOIN rbDiseaseStage ON rbDiseaseStage.id = D4.stage_id
                    WHERE D4.event_id = Event.id AND D4.deleted=0 AND rbDispanser.code in ('2', '6'))))
            LEFT JOIN rbDispanser    ON rbDispanser.id    = D2.dispanser_id
            LEFT JOIN rbDiseaseStage ON rbDiseaseStage.id = D2.stage_id
            LEFT JOIN rbDiseaseCharacter ON rbDiseaseCharacter.id = D2.character_id
            LEFT JOIN Diagnostic AS D5 ON (     D5.event_id = Event.id
                                          AND D5.diagnosisType_id = (SELECT id FROM rbDiagnosisType WHERE code = '1')
                                        )
            LEFT JOIN rbHealthGroup  ON rbHealthGroup.id  = D5.healthGroup_id
            LEFT JOIN Account_Item ON ( Account_Item.id = (SELECT max(AI.id) FROM Account_Item AS AI WHERE AI.event_id = Event.id AND AI.deleted=0 AND AI.date IS NOT NULL AND AI.refuseType_id IS NULL AND AI.reexposeItem_id IS NULL AND AI.visit_id IS NULL AND AI.action_id IS NULL)
                                      )
        WHERE
            Event.deleted=0 AND %s
        GROUP BY
            OKVED, dispanser, stage, `group`
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


class CStatReport1NP2000(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(True)
        self.setTitle(u'Итоги дополнительной диспансеризации граждан (2000)', u'Итоги дополнительной диспансеризации')


    def build(self, params):
        rows = [
                (u'Образование', u'01', u'М80'),
                (u'Здравоохранение', u'02', u'N85.1-N85.14'),
                (u'Предоставление социальных услуг', u'03', u'N85.3'),
                (u'Деятельность по организации отдыха, развлечений, культуры и спорта', u'04', u'О92'),
                (u'Научно-исследовательские учреждения', u'05', u'К73'),
                (u'ВСЕГО', u'06', u'X'),
               ]

        def dispatch(okved):
            result = [len(rows)-1]
            if okved[:3] == u'M80':
                result.append(0)
            if okved[:5] >= u'N85.1' and okved[:6] <= u'N85.14':
                result.append(1)
            if okved[:5] == u'N85.3':
                result.append(2)
            if okved[:3] == u'O92':
                result.append(3)
            if okved[:3] == u'K73':
                result.append(4)
            return result

        begDate = getVal(params, 'begDate', QtCore.QDate())
        endDate = getVal(params, 'endDate', QtCore.QDate())
        eventTypeId = getVal(params, 'eventTypeId', None)
        onlyPermanentAttach =  getVal(params, 'onlyPermanentAttach', False)
        onlyPayedEvents = getVal(params, 'onlyPayedEvents', False)
        begPayDate = getVal(params, 'begPayDate', QtCore.QDate())
        endPayDate = getVal(params, 'endPayDate', QtCore.QDate())

        reportRowSize = 12
        reportData = [ [0] * reportRowSize for row in rows ]
        query = selectData(begDate, endDate, eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate)

        while query.next() :
            record = query.record()
            okved  = forceString(record.value('OKVED'))
            dispanser = forceBool(record.value('dispanser'))
            stage  = forceString(record.value('stage'))
            group  = forceString(record.value('group'))
            cnt = forceInt(record.value('cnt'))

            columns = [0]
            if dispanser:
                columns.append(4)
                if stage == '1':
                    columns.append(5)
                elif stage == '2':
                    columns.append(6)
            if group == '1':
                columns.append(7)
            elif group == '2':
                columns.append(8)
            elif group == '3':
                columns.append(9)
            elif group == '4':
                columns.append(10)
            elif group == '5':
                columns.append(11)
            for row in dispatch(okved):
                for column in columns:
                    reportData[row][column] += cnt

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Итоги дополнительной диспансеризации граждан')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertText(u'(2000)')
        cursor.insertBlock()

        tableColumns = [
            ('30%', [u'Наименование вида экономической деятельности гражданина, прошедшего диспансеризацию', u'', u'', u'1'], CReportBase.AlignLeft),
            ('5%', [u'№ строки', u'', u'', u'2'], CReportBase.AlignCenter),
            ('5%', [u'Численность работающих граждан, прошедших дополнительную диспансеризацию (законченные случаи), чел.', u'Всего', u'', u'3'], CReportBase.AlignRight),
            ('5%', [u'', u'в том числе:', u'Город-\nских', u'4'], CReportBase.AlignRight),
            ('5%', [u'', u'', u'Сель-\nских', u'5'], CReportBase.AlignRight),
            ('5%', [u'', u'', u'осмо-\nтренных спе-\nциали-\nстами выез-\nдных бри-\nгад (зако-\nнчен-\nные слу-\nчаи)', u'6'], CReportBase.AlignRight),
            ('5%', [u'взято на Д-учет', u'Всего', u'', u'7'], CReportBase.AlignRight),
            ('5%', [u'', u'в том числе:', u'на ранних стад-\nиях забо-\nлева-\nния', u'8'], CReportBase.AlignRight),
            ('5%', [u'', u'', u'на поздних стади-\nях забо-\nлева-\nния', u'9'], CReportBase.AlignRight),
            ('5%', [u'Распределение прошедших дополнительную диспансеризацию граждан по группам состояния здоровья', u'I гр.', u'', u'10'], CReportBase.AlignRight),
            ('5%', [u'', u'II гр.', u'',   u'11'], CReportBase.AlignRight),
            ('5%', [u'', u'III гр.', u'',  u'12'], CReportBase.AlignRight),
            ('5%', [u'', u'IV гр.', u'',   u'13'], CReportBase.AlignRight),
            ('5%', [u'', u'V гр.', u'',    u'14'], CReportBase.AlignRight),
            ]

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 3, 1)
        table.mergeCells(0, 2, 1, 4)
        table.mergeCells(1, 2, 2, 1)
        table.mergeCells(1, 3, 1, 3)
        table.mergeCells(0, 6, 1, 3)
        table.mergeCells(1, 6, 2, 1)
        table.mergeCells(1, 7, 1, 2)
        table.mergeCells(0, 9, 1, 5)
        table.mergeCells(1, 9, 2, 1)
        table.mergeCells(1,10, 2, 1)
        table.mergeCells(1,11, 2, 1)
        table.mergeCells(1,12, 2, 1)
        table.mergeCells(1,13, 2, 1)

        for iRow, row in enumerate(rows):
            tableRow = table.addRow()
            for i in xrange(2):
                table.setText(tableRow, i, row[i])
            for i in xrange(reportRowSize):
                if not(i in [1, 2, 3]):
                    table.setText(tableRow, 2+i, reportData[iRow][i])

        return doc

