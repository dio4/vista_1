# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.MapCode                import createMapCodeToRowIdx
from library.Utils                  import forceBool, forceInt, forceString

from Reports                        import OKVEDList
from Reports.Report                 import normalizeMKB, CReport
from Reports.ReportBase             import createTable, CReportBase
from Reports.ReportSetupDialog      import CReportSetupDialog
from Reports.StatReportF12_D_2_07   import selectDiagnostics


Rows = [
          ( u'Всего', u'1.0', u'A00-T98'),
          ( u'Некоторые инфекционные и паразитарные болезни - всего', u'2.0', u'A00-B99'),
          ( u'     в том числе туберкулез', u'2.1', u'A15-A19'),
          ( u'Новообразования', u'3.0', u'C00-D48'),
          ( u'   в том числе\nзлокачественные', u'3.1', u'C00-C97'),
          ( u'Болезни крови и кроветворных органов, отдельные нарушения, вовлекающие иммунный механизм', u'4.0', u'D50-D89'),
          ( u'Болезни эндокринной системы, расстройства питания и нарушения обмена веществ - всего', u'5.0', u'E00-E90'),
          ( u'     в том числе сахарный диабет', u'5.1', u'E10-E14'),
          ( u'Психические расстройства и расстройства поведения', u'6.0', u'F00-F99'),
          ( u'Болезни нервной системы', u'7.0', u'G00-G99'),
          ( u'Болезни глаза и его придаточного аппарата – всего', u'8.0', u'H00-H59'),
          ( u'     в том числе:\n      катаракта', u'8.1', u'H25-H26'),
          ( u'      глаукома', u'8.2', u'H40'),
          ( u'      миопия', u'8.3', u'H52.1'),
          ( u'Болезни уха и сосцевидного отростка - всего', u'9', u'H60-H95'),
          ( u'    в том числе\n    кондуктивная и нейросенсорная потеря слуха', u'9.1', u'H90'),
          ( u'Болезни системы кровообращения - всего', u'10', u'I00-I99'),
          ( u'          из них:     болезни,  характеризующиеся повышенным кровяным давлением', u'10.1', u'I10-I13'),
          ( u'     ишемическая болезнь сердца', u'10.2', u'I20-I25'),
          ( u'     ишемическая болезнь мозга', u'10.3', u'I67.8'),
          ( u'Болезни органов дыхания', u'11.0', u'J00-J99'),
          ( u'Болезни органов пищеварения', u'12.0', u'K00-K93'),
          ( u'Болезни кожи и подкожной клетчатки', u'13.0', u'L00-L99'),
          ( u'Болезни костно-мышечной системы и соединительной ткани', u'14.0', u'M00-M99'),
          ( u'Болезни мочеполовой системы', u'15.0', u'N00-N99'),
          ( u'Симптомы, признаки и отклонения от нормы, выявленные при клинических и лабораторных исследованиях', u'19.0', u'R00-R99'),
          ( u'Травмы, отравления и некоторые др. последствия воздействия внешних причин', u'20.0', u'S00-T98'),
          ( u'Прочие', u'21.0', u'O00-O99,Q00-Q99')
       ]


class CStatReportF12_D_2_10(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Сведения о результатах дополнительной диспансеризации работающих граждан, Ф.№ 12-Д-2-10',
                      u'Сведения о дополнительной диспансеризации работающих граждан')


    def getSetupDialog(self, parent):
        result = CReportSetupDialog(parent)
        result.setTitle(self.title())
        result.setEventTypeVisible(True)
        result.setPayPeriodVisible(True)
        result.setOwnershipVisible(True)
        return result


    def build(self, params):
        def addOnes(rows, column):
            for row in rows:
                reportLine = reportData[row]
                reportLine[column] += 1


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

        mapRows = createMapCodeToRowIdx( [row[2] for row in Rows] )
        reportRowSize = 7
        reportData = [ [0] * reportRowSize for row in Rows ]
        query = selectDiagnostics(begDate, endDate, eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate)
        prevClientId   = None
        prevMKB        = None
        clientRowsP8 = set([])
        clientRowsP9 = set([])
#        clientRowsP10 = set([])
        clientRowsP11 = set([])

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
                    addOnes(diagRows, 6)
                if p4 :
                    addOnes(diagRows, 0)
                if p5 :
                    addOnes(diagRows, 1)
                if p6 :
                    addOnes(diagRows, 2)
                prevMKB = mkb
            if prevClientId != clientId:
                addOnes(clientRowsP8, 3)
                addOnes(clientRowsP9, 4)
                addOnes(clientRowsP11, 5)
                clientRowsP8 = set([])
                clientRowsP9 = set([])
                clientRowsP11 = set([])
                prevClientId = clientId
            if p8:
                clientRowsP8.update(diagRows)
            if p9:
                clientRowsP9.update(diagRows)
            if p11:
                clientRowsP11.update(diagRows)
        addOnes(clientRowsP8, 4)
        addOnes(clientRowsP9, 4)
        addOnes(clientRowsP11, 5)

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
            ('8%', [u'Заболевания', u'ранее изве-\nстное хрони-\nческое', u'4'], CReportBase.AlignRight),
            ('8%', [u'', u'выявле-\nнное во время доп. дисп.', u'5'], CReportBase.AlignRight),
            ('8%', [u'', u'в том числе на поздней стадии (из гр.5)',         u'6'], CReportBase.AlignRight),
            ('8%', [u'Госпитализировано больных (из числа выявленных - графа 5)', u'в стационар (в том числе субъе-\nкта РФ)', u'8'], CReportBase.AlignRight),
            ('8%', [u'',u'в фед. спец. мед. уч. (для оказания ВМП)', u'9'], CReportBase.AlignRight),
            ('8%', [u'Из числа граждан, прошедших доп. дисп. взято под дисп. набл.', u'', u'10'], CReportBase.AlignRight),
            ('8%', [u'Выявлено забо-\nлеваний в течение 6 месяцев после прохождения доп. дисп.', u'', u'11'], CReportBase.AlignRight),
            ]
        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 2, 1)

        table.mergeCells(0, 3, 1, 3)
        table.mergeCells(0, 6, 1, 2)
        table.mergeCells(0, 8, 2, 1)
        table.mergeCells(0, 9, 2, 1)

        for iRow, row in enumerate(Rows):
            i = table.addRow()
            for j in xrange(3):
                table.setText(i, j, row[j])
            for j in xrange(reportRowSize):
                table.setText(i, 3+j, reportData[iRow][j])
        return doc

