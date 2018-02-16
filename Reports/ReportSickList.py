# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui

from library.Utils                              import forceInt, forceString
from Reports.Report                             import CReport
from Reports.ReportBase                         import createTable, CReportBase
from Reports.ReportPrimaryRepeatHospitalization import CPrimaryRepeatHospitalization


diagnosis = [u'S00.1', u'S00.5', u'S00.8', u'S01.0', u'S01.4', u'S01.7', u'S01.8', u'S02.3', u'S02.4', u'S02.5',
             u'S02.6',
             u'S02.7', u'S02.8', u'S02.9', u'S06.0', u'S13.4', u'S20.2', u'S21.1', u'S22.3', u'S22.4', u'S30.0',
             u'S32.0', u'S32.7', u'S40.0', u'S40.8', u'S41.0', u'S42.0', u'S42.2', u'S42.3', u'S43.0', u'S43.5',
             u'S50.0', u'S50.1', u'S51.8', u'S52.0', u'S52.1', u'S52.2', u'S52.5', u'S52.6', u'S60.0', u'S60.2',
             u'S61.0', u'S61.8', u'S62', u'S62.3', u'S62.6', u'S63.1', u'S63.4', u'S63.5', u'S63.6', u'S63.7',
             u'S66.0', u'S68.1', u'S70.0', u'S70.0', u'S70.8', u'S71.1', u'S72.4', u'S80.0', u'S80.0', u'S80.1',
             u'S80.8', u'S81.0', u'S81.8', u'S82.0', u'S82.3', u'S82.4', u'S82.5', u'S82.6', u'S82.7', u'S82.8',
             u'S83.0', u'S83.2', u'S83.6', u'S86.0', u'S86.8', u'S86.0', u'S86.8', u'S90.0', u'S90.1', u'S90.3',
             u'S90.8', u'S91.3', u'S92.0', u'S92.3', u'S92.4', u'S92.5', u'S93.4', u'S93.5', u'S93.6', u'T21',
             u'T22', u'T23', u'T24', u'T25', u'T92.1', u'T93.2']


def selectData(begDate, endDate, isEventCreateParams, eventBegDatetime, eventEndDatetime, eventTypeId, personId):
    db = QtGui.qApp.db
    tableMKB = db.table('MKB_Tree')
    tableTempInvalid = db.table('TempInvalid')
    tableNextTempInvalid = db.table('TempInvalid').alias('NextTempInvalid')
    tableEvent = db.table('Event')
    tablePerson = db.table('Person')

    cond = [tableMKB['DiagID'].inlist(diagnosis),
            tableTempInvalid['type'].eq('0'),
            tableNextTempInvalid['id'].isNull()]

    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if personId:
        cond.append(tablePerson['id'].eq(personId))
    if isEventCreateParams:
        cond.append(tableTempInvalid['createDatetime'].dateGe(eventBegDatetime))
        cond.append(tableTempInvalid['createDatetime'].dateLe(eventEndDatetime))
    else:
        cond.append(tableTempInvalid['endDate'].dateGe(begDate))
        cond.append(tableTempInvalid['endDate'].dateLe(endDate))

    cond.append(tableTempInvalid['deleted'].eq('0'))
    cond.append(tableEvent['deleted'].eq('0'))
    cond.append(tablePerson['deleted'].eq('0'))

    stmt = u'''SELECT MKB_Tree.DiagName AS name
                    , MKB_Tree.DiagID AS MKB
                    , count(TempInvalid.id) AS countAll
                    , sum(datediff(TempInvalid.endDate, TempInvalid.caseBegDate) + 1) AS countDays
                    , round(sum(datediff(TempInvalid.endDate, TempInvalid.caseBegDate) + 1)/count(TempInvalid.id), 1) AS average
               FROM
                    MKB_Tree
                    INNER JOIN Diagnosis ON Diagnosis.MKB = MKB_Tree.DiagID
                    INNER JOIN Diagnostic ON Diagnosis.id = Diagnostic.diagnosis_id
                    INNER JOIN Event ON Event.id = Diagnostic.event_id
                    INNER JOIN TempInvalid ON TempInvalid.diagnosis_id = Diagnosis.id
                    LEFT JOIN Person ON Person.id = TempInvalid.person_id
                    LEFT JOIN TempInvalid AS NextTempInvalid ON TempInvalid.id = NextTempInvalid.prev_id
               WHERE
                    %s
               GROUP BY
                    MKB_Tree.DiagID
            ''' % (db.joinAnd(cond))

    return db.query(stmt)

def selectMKB():
     db = QtGui.qApp.db
     tableMKB = db.table('MKB_Tree')

     stmt = u'''SELECT MKB_Tree.DiagName AS name
                    , MKB_Tree.DiagId AS MKB
                FROM
                    MKB_Tree
                WHERE
                    %s''' % (tableMKB['DiagID'].inlist(diagnosis))
     return db.query(stmt)

class CReportSickList(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Развернутая форма по больничным листам (травма)')

    def getSetupDialog(self, parent):
        dialog = CPrimaryRepeatHospitalization(parent)
        dialog.setTitle(self.title())
        return dialog

    def build(self, params):
        nameMKB = {}
        query = selectMKB()
        while query.next():
            record = query.record()
            name = forceString(record.value('name'))
            MKB = forceString(record.value('MKB'))
            nameMKB[MKB] = name
        begDate = params.get('begDate', None)
        endDate = params.get('endDate', None)
        isEventCreateParams = params.get('isEventCreateParams', False)
        eventBegDatetime =params.get('eventBegDatetime', None)
        eventEndDatetime = params.get('eventEndDatetime', None)
        eventTypeId = params.get('eventTypeId', None)
        personId = params.get('personId', None)
        query = selectData(begDate, endDate, isEventCreateParams, eventBegDatetime, eventEndDatetime, eventTypeId, personId)
        self.setQueryText(forceString(query.lastQuery()))

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
                        ('35%', [u'Нозологическая единица'],       CReportBase.AlignRight),
                        ('35%', [u'Шифр по МКБ-Х'],  CReportBase.AlignLeft),
                        ('15%', [u'Всего Б/л'],     CReportBase.AlignLeft),
                        ('15%', [u'Всего дней'],     CReportBase.AlignLeft),
                        ('15%', [u'Средняя прод.'],     CReportBase.AlignLeft)
                        ]

        table = createTable(cursor, tableColumns)

        resultTable, total = self.getTable(query, nameMKB)
        for key in sorted(resultTable.keys()):
            i = table.addRow()
            table.setText(i, 0, resultTable[key][0])
            table.setText(i, 1, key)
            table.setText(i, 2, resultTable[key][1])
            table.setText(i, 3, resultTable[key][2])
            table.setText(i, 4, resultTable[key][3])

        i = table.addRow()
        table.setText(i, 0, u'ИТОГО:', CReportBase.TableTotal)
        for index in xrange(len(total)):
            table.setText(i, index + 2, total[index])
        return doc

    def getTable(self, query, nameMKB):
        total = [0]*3
        table = {}
        while query.next():
            record = query.record()
            name = forceString(record.value('name'))
            MKB = forceString(record.value('MKB'))
            countAll = forceInt(record.value('countAll'))
            countDays = forceInt(record.value('countDays'))
            average = forceInt(record.value('average'))
            table[MKB] = [0]*4
            table[MKB][0] = name
            table[MKB][1] = countAll
            table[MKB][2] = countDays
            table[MKB][3] = average
            del nameMKB[MKB]
            total[0] += countAll
            total[1] += countDays
        for key in nameMKB:
            table[key] = [0]*4
            table[key][0] = nameMKB[key]
        if total[0]:
            total[2] = total[1]/total[0]
        return table, total
