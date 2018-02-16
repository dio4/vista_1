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

from Reports                    import OKVEDList
from Reports.Report             import normalizeMKB, CReport
from Reports.ReportBase         import createTable, CReportBase
from Reports.ReportSetupDialog  import CReportSetupDialog
from Reports.StatReport1NPUtil  import havePermanentAttach


Rows = [
          ( u'Всего', u'1.0', u'A00-T98'),
          ( u'Некоторые инфекционные и паразитарные болезни - всего', u'2.0', u'A00-B99'),
          ( u'в том числе туберкулез', u'2.1', u'A15-A19'),
          ( u'Злокачественные новообразования', u'3.0', u'C00-C97'),
          ( u'Болезни крови и кроветворных органов, отдельные нарушения, вовлекающие иммунный механизм', u'4.0', u'D50-D89'),
          ( u'Болезни эндокринной системы, расстройства питания и нарушения обмена веществ - всего', u'5.0', u'E00-E90'),
          ( u'в том числе сахарный диабет', u'5.1', u'E10-E14'),
          ( u'Психические расстройства и расстройства поведения', u'6.0', u'F00-F99'),
          ( u'Болезни нервной системы', u'7.0', u'G00-G99'),
          ( u'Болезни глаза и его придаточного аппарата - всего', u'8.0', u'H00-H59'),
          ( u'в том числе: катаракта', u'8.1', u'H25-H26'),
          ( u'глаукома', u'8.2', u'H40'),
          ( u'миопия', u'8.3', u'H52.1'),
          ( u'Болезни уха и сосцевидного отростка - всего', u'9', u'H60-H95'),
          ( u'в том числе: кондуктивная и нейросенсорная потеря слуха', u'9.1', u'H90'),
          ( u'Болезни системы кровообращения - всего', u'10', u'I00-I99'),
          ( u'из них: болезни, характеризующиеся повышенным кровяным давлением', u'10.1', u'I10-I13'),
          ( u'ишемическая болезнь сердца', u'10.2', u'I20-I25'),
          ( u'Болезни органов дыхания', u'11.0', u'J00-J99'),
          ( u'Болезни органов пищеварения', u'12.0', u'K00-K93'),
          ( u'Болезни кожи и подкожной клетчатки', u'13.0', u'L00-L99'),
          ( u'Болезни костно-мышечной системы и соединительной ткани', u'14.0', u'M00-M99'),
          ( u'Болезни мочеполовой системы', u'15.0', u'N00-N99'),
          ( u'Симптомы, признаки и отклонения от нормы, выявленные при клинических и лабораторных исследованиях', u'19.0', u'R00-R99'),
          ( u'Травмы, отравления и некоторые др. последствия воздействия внешних причин', u'20.0', u'S00-T98'),
          ( u'Доброкачественные новообразования', u'21.0', u'D00-D48'),
          ( u'Врождённые аномалии (пороки развития) деформации и хромосомные нарушения', u'22.0', u'Q00-Q99'),
       ]


def selectDiagnostics(begDate, endDate, eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate):
    stmt="""
        SELECT
            Event.client_id as client_id,
            Event.isPrimary as isPrimary,
            Diagnosis.mkb as mkb,
            IF(rbDiseaseCharacter.code='3' OR rbDiseaseCharacter.code='4', 1, 0) AS P4,
            IF(rbDiseaseCharacter.code='2'
               OR (rbDiseaseCharacter.code='1' AND rbDiseaseStage.code='1'),
               1,
               0 ) AS P5,
            IF(rbDiseaseCharacter.code='2' AND rbDiseaseStage.code='2',
               1,
               0 ) AS P6,
            IF(Diagnostic.hospital>1, 1, 0) AS P8,
            IF(Diagnostic.hospital>1 AND rbHealthGroup.code = 5, 1, 0) AS P9,
            rbDispanser.observed AS P10,
            rbDispanser.code in ('2', '6') AS P11,
            Organisation.OKVED as OKVED,
            rbOKFS.ownership as ownership
        FROM
            Diagnostic
            LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id
            LEFT JOIN Event     ON Event.id = Diagnostic.event_id
            LEFT JOIN rbDiseaseCharacter ON rbDiseaseCharacter.id = Diagnostic.character_id
            LEFT JOIN rbDiseaseStage     ON rbDiseaseStage.id     = Diagnostic.stage_id
            LEFT JOIN rbHealthGroup      ON rbHealthGroup.id      = Diagnostic.healthGroup_id
            LEFT JOIN rbDispanser        ON rbDispanser.id        = Diagnostic.dispanser_id
            LEFT JOIN Client             ON Client.id             = Event.client_id
            LEFT JOIN ClientWork         ON (    ClientWork.client_id = Client.id
                                             AND ClientWork.id = (SELECT MAX(id) FROM ClientWork AS CW WHERE CW.client_id = Client.id)
                                            )
            LEFT JOIN Organisation       ON Organisation.id = ClientWork.org_id
            LEFT JOIN rbOKFS             ON rbOKFS.id = Organisation.OKFS_id
            LEFT JOIN Account_Item       ON ( Account_Item.id = (SELECT max(AI.id) FROM Account_Item AS AI WHERE AI.event_id = Event.id AND AI.deleted=0 AND AI.date IS NOT NULL AND AI.refuseType_id IS NULL AND AI.reexposeItem_id IS NULL AND AI.visit_id IS NULL AND AI.action_id IS NULL)
                                            )
        WHERE
            %s
        ORDER BY
            Event.client_id, Diagnosis.mkb, Diagnostic.diagnosisType_id, Diagnostic.id
    """
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    cond = []
    cond.append(tableEvent['execDate'].ge(begDate))
    cond.append(tableEvent['execDate'].le(endDate))
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if onlyPermanentAttach:
        cond.append(havePermanentAttach(endDate))
    if onlyPayedEvents:
        cond.append('isEventPayed(Event.id)')
        tableAccountItem = db.table('Account_Item')
        addDateInRange(cond, tableAccountItem['date'], begPayDate, endPayDate)
    return db.query(stmt % (db.joinAnd(cond)))


class CStatReportF12_D_2_07(CReport):
    def __init__(self, parent,  mode = '07'):
        CReport.__init__(self, parent)
        self.mode = mode
        self.setTitle(u'Сведения о результатах дополнительной диспансеризации работающих граждан, Ф.№ 12-Д-2-'+mode,
                      u'Сведения о дополнительной диспансеризации работающих граждан')

    def getSetupDialog(self, parent):
        result = CReportSetupDialog(parent)
        result.setTitle(self.title())
        result.setEventTypeVisible(True)
        result.setPayPeriodVisible(True)
        if self.mode == '08':
            result.setOwnershipVisible(True)
        elif self.mode == '09':
            result.setOwnershipVisible(True)
        else:
            result.setWorkTypeVisible(True)
        return result


    def build(self, params):
        def addOnes(rows, column):
            for row in rows:
                reportLine = reportData[row]
                reportLine[column] += 1

#        global Rows

        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        eventTypeId = params.get('eventTypeId', None)
        onlyPermanentAttach =  params.get('onlyPermanentAttach', False)
        onlyPayedEvents = params.get('onlyPayedEvents', False)
        begPayDate = params.get('begPayDate', QtCore.QDate())
        endPayDate = params.get('endPayDate', QtCore.QDate())
        workType = params.get('workType', 0)
        ownership = params.get('ownership', 0)

        db = QtGui.qApp.db

        self.Rows = [] + Rows
        if self.mode == '09':
            self.Rows.insert(18, (u'ишемическая болезнь мозга', u'10.3', u'I67.8'))
            self.Rows.append(    (u'прочие', u'21.0', u'D00-D49'))

        mapRows = createMapCodeToRowIdx( [row[2] for row in self.Rows] )
        reportRowSize = 11
        reportData = [ [0] * reportRowSize for row in self.Rows ]
        query = selectDiagnostics(begDate, endDate, eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate)
        prevClientId   = None
        prevMKB        = None
        clientRowsP8 = set([])
        clientRowsP9 = set([])
        clientRowsP10 = set([])
        clientRowsP11 = set([])
        clientRowsP13 = set([])
        clientRowsP14 = set([])

        while query.next() :
            record = query.record()

            if ownership>0 and ownership != forceInt(record.value('ownership')):
                continue
            if workType>0:
                okved = forceString(record.value('OKVED'))
                if workType not in OKVEDList.dispatch(okved):
                    continue
            clientId = forceInt(record.value('client_id'))
            isPrimary= forceInt(record.value('isPrimary')) == 1
            mkb      = normalizeMKB(forceString(record.value('mkb')))
            p4       = forceBool(record.value('P4'))
            p5       = forceBool(record.value('P5'))
            p6       = forceBool(record.value('P6'))
            p8       = forceBool(record.value('P8'))
            p9       = forceBool(record.value('P9'))
            p10      = forceBool(record.value('P10'))
            p11      = forceBool(record.value('P11'))

            diagRows = mapRows.get(mkb, [])
            if prevClientId != clientId or prevMKB != mkb:
                if not isPrimary:
                    addOnes(diagRows, 8)
                addOnes(diagRows, 0)
                if p4 :
                    addOnes(diagRows, 1)
                if p5 :
                    addOnes(diagRows, 2)
                if p6 :
                    addOnes(diagRows, 3)
                prevMKB = mkb
            if prevClientId != clientId:
                addOnes(clientRowsP8, 4)
                addOnes(clientRowsP9, 5)
                addOnes(clientRowsP10, 6)
                addOnes(clientRowsP11, 7)
                addOnes(clientRowsP13, 9)
                addOnes(clientRowsP14, 10)
                clientRowsP8 = set([])
                clientRowsP9 = set([])
                clientRowsP10 = set([])
                clientRowsP11 = set([])
                clientRowsP13 = set([])
                clientRowsP14 = set([])
                prevClientId = clientId
            if p8:
                clientRowsP8.update(diagRows)
            if p9:
                clientRowsP9.update(diagRows)
            if p10 and p6:
                clientRowsP10.update(diagRows)
            if p11 and p6:
                clientRowsP11.update(diagRows)
            if p10:
                clientRowsP13.update(diagRows)
            if p11:
                clientRowsP14.update(diagRows)
        addOnes(clientRowsP8, 4)
        addOnes(clientRowsP9, 5)
        addOnes(clientRowsP10, 6)
        addOnes(clientRowsP11, 7)
        addOnes(clientRowsP13, 9)
        addOnes(clientRowsP14, 10)

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)

        tableColumns = [
            ('18%', [u'Наименование заболевания (по классам и отдельным нозологиям)', u'', u'1'], CReportBase.AlignLeft),
            ('6%', [u'№ строки',  u'',      u'2'], CReportBase.AlignCenter),
            ('10%',[u'Код по МКБ-10', u'', u'3'], CReportBase.AlignCenter),
            ('6%', [u'Заболевания', u'всего', u'4'], CReportBase.AlignRight),
            ('6%', [u'', u'ранее изве-\nстное хрони-\nческое', u'5'], CReportBase.AlignRight),
            ('6%', [u'', u'выявле-\nнное во время доп. дисп.', u'6'], CReportBase.AlignRight),
            ('6%', [u'', u'в том числе на поздней стадии (из гр.6)',         u'7'], CReportBase.AlignRight),
            ('6%', [u'Госпитализировано больных (из числа выявленных - графа 6)', u'в стационар (в том числе субъе-\nкта РФ)', u'8'], CReportBase.AlignRight),
            ('6%', [u'',u'в фед. спец. мед. уч. (для оказания ВМП)', u'9'], CReportBase.AlignRight),
            ('6%', [u'Из числа граждан, прошедших доп. дисп. сост. под дисп. набл. (из гр.6)', u'', u'10'], CReportBase.AlignRight),
            ('6%', [u'Из числа граждан, прошедших доп. дисп. взято под дисп. набл. (из гр.6)', u'', u'11'], CReportBase.AlignRight),
            ('6%', [u'Выявлено забо-\nлеваний в течение 6 месяцев после прохождения доп. дисп.', u'', u'12'], CReportBase.AlignRight),
            ('6%', [u'Из числа граждан, прошедших доп. дисп. сост. под дисп. набл.', u'', u'13'], CReportBase.AlignRight),
            ('6%', [u'Из числа граждан, прошедших доп. дисп. взято под дисп. набл.', u'', u'14'], CReportBase.AlignRight),
            ]
        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 1, 4)
        table.mergeCells(0, 7, 1, 2)
        table.mergeCells(0, 9, 2, 1)
        table.mergeCells(0,10, 2, 1)
        table.mergeCells(0,11, 2, 1)
        table.mergeCells(0,12, 2, 1)
        table.mergeCells(0,13, 2, 1)

        for iRow, row in enumerate(self.Rows):
            i = table.addRow()
            for j in xrange(3):
                table.setText(i, j, row[j])
            for j in xrange(reportRowSize):
                table.setText(i, 3+j, reportData[iRow][j])
        return doc

