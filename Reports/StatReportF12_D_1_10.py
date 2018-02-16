# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils                  import forceBool, forceInt, forceRef, forceString

from Reports.Report                 import CReport
from Reports.ReportBase             import createTable, CReportBase
from Reports.ReportSetupDialog      import CReportSetupDialog
from Reports.StatReportF12_D_1_08   import countDispensariable, countByGroups, countBySanatoriumAndHospital


def prepareOKFS():
    mapIdToRowIndex = {}
    rows = [(u'ВСЕГО работающих', u'0.0'),
            (u'в том числе в бюджетных организациях', u'1.0')]

    db = QtGui.qApp.db
    for record in db.getRecordList('rbOKFS', 'id, ownership', order='code'):
        id = forceInt(record.value('id'))
        ownership = forceInt(record.value('ownership'))
        if ownership == 1:
            rowIndexes = [0, 1]
        else:
            rowIndexes = [0]
        mapIdToRowIndex[id] = rowIndexes
    return mapIdToRowIndex, rows



class CStatReportF12_D_1_10(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Сведения о дополнительной диспансеризации работающих граждан, Ф.№ 12-Д-1-10',
                      u'Сведения о дополнительной диспансеризации работающих граждан')


    def getSetupDialog(self, parent):
        result = CReportSetupDialog(parent)
        result.setTitle(self.title())
        result.setEventTypeVisible(True)
        result.setPayPeriodVisible(True)
        return result


    def build(self, params):
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        eventTypeId = params.get('eventTypeId', None)
        onlyPermanentAttach =  params.get('onlyPermanentAttach', False)
        onlyPayedEvents = params.get('onlyPayedEvents', False)
        begPayDate = params.get('begPayDate', QtCore.QDate())
        endPayDate = params.get('endPayDate', QtCore.QDate())

        mapOkfsIdToRow, rows = prepareOKFS()
        reportRowSize = 11
        reportData = [[0]*reportRowSize for row in rows ]

        query = countDispensariable(begDate, endDate, eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate)
        while query.next() :
            record = query.record()
            okfsId = forceRef(record.value('OKFS_id'))
            cnt    = forceInt(record.value('cnt'))
            for i in mapOkfsIdToRow.get(okfsId, [0]):
                reportData[i][0] += cnt

        query = countByGroups(begDate, endDate, eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate)
        while query.next() :
            record = query.record()
            okfsId = forceRef(record.value('OKFS_id'))
            cnt    = forceInt(record.value('cnt'))
            group  = forceString(record.value('group'))
            DOD    = forceBool(record.value('DOD'))
#            isPrimary= forceInt(record.value('isPrimary')) == 1
            columns = []
            if group == '2':
                columns = [1, 3]
            elif group == '3':
                if DOD:
                    columns = [1, 4, 5]
                else:
                    columns = [1, 4]
            elif group == '4':
                columns = [1, 6]
            elif group == '5' or group == '6':
                columns = [1, 7]
            else:
                columns = [1, 2]
            for i in mapOkfsIdToRow.get(okfsId, [0]):
                reportLine = reportData[i]
                for j in columns:
                    reportLine[j] += cnt

        query = countBySanatoriumAndHospital(begDate, endDate, eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate)
        while query.next() :
            record = query.record()
            okfsId = forceRef(record.value('OKFS_id'))
            sanatorium  = forceBool(record.value('sanatorium'))
            hospital    = forceBool(record.value('hospital'))
            highTechAid = forceBool(record.value('highTechAid'))
            cnt         = forceInt(record.value('cnt'))
            columns = []
            if sanatorium:
                columns.append(8)
            if hospital:
                columns.append(9)
            if highTechAid:
                columns.append(10)

            for i in mapOkfsIdToRow.get(okfsId, []):
                reportLine = reportData[i]
                for j in columns:
                    reportLine[j] += cnt

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)


        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
#        cursor.setCharFormat(CReportBase.ReportBody)

        self.dumpParams(cursor, params)
        tableColumns = [
            ('18%', [u'Наименование',
                     u'',
                     u'',
                     u'1'],            CReportBase.AlignLeft),
            ('5%', [u'№ строки',
                     u'',
                     u'',
                     u'2'],            CReportBase.AlignCenter),
            ('5%', [u'Число лиц',
                     u'под-\nле-\nжа-\nщих ДД',
                     u'',
                     u'3'],            CReportBase.AlignRight),
            ('5%', [u'',
                     u'про-\nшед-\nших ДД',
                     u'',
                     u'4'],            CReportBase.AlignRight),
            ('5%', [u'Распределение прошедших дополнительную диспансеризацию (ДД) граждан по группам состояния здоровья',
                     u'I гр.',
                     u'',
                     u'5'],              CReportBase.AlignRight),
            ('5%', [u'',
                     u'II гр.',
                     u'',
                     u'6'],              CReportBase.AlignRight),
            ('5%',  [u'',
                     u'III гр.',
                     u'все-\nго',
                     u'7'
                     ],              CReportBase.AlignRight),
            ('5%',  [u'',
                     u'',
                     u'в т.ч. выя-\nвле-\nнные при ДД',
                     u'8'],              CReportBase.AlignRight),
            ('5%',  [u'',
                     u'IV гр.',
                     u'',
                     u'9'],              CReportBase.AlignRight),
            ('5%',  [u'',
                     u'V гр.',
                     u'',
                     u'10'],              CReportBase.AlignRight),
            ('5%',  [u'из числа прошедших ДД (графа 4) нуждалось в санаторно- курортном лечении',
                     u'',
                     u'',
                     u'11'],              CReportBase.AlignRight),
            ('5%',  [u'Направлено граждан',
                     u'на гос-\nпита-\nлизацию в ста-\nцио-\nнар',
                     u'',
                     u'12'],              CReportBase.AlignRight),
            ('5%' , [u'',
                     u'в ОУЗ суб. РФ на ВМП',
                     u'',
                     u'13'],              CReportBase.AlignRight),
            ]
        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 3, 1)

        table.mergeCells(0, 2, 1, 2)
        table.mergeCells(1, 2, 2, 1)
        table.mergeCells(1, 3, 2, 1)

        table.mergeCells(0, 4, 1, 6)
        table.mergeCells(1, 4, 2, 1)
        table.mergeCells(1, 5, 2, 1)
        table.mergeCells(1, 6, 1, 2)
        table.mergeCells(1, 8, 2, 1)
        table.mergeCells(1, 9, 2, 1)

        table.mergeCells(0,10, 3, 1)

        table.mergeCells(0,11, 1, 2)
        table.mergeCells(1,11, 2, 1)
        table.mergeCells(1,12, 2, 1)

        for iRow, row in enumerate(rows):
            i = table.addRow()
            for j in xrange(2):
                table.setText(i, j, row[j])
            for j in xrange(reportRowSize):
                table.setText(i, 2+j, reportData[iRow][j])

        return doc
