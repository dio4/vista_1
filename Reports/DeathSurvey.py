# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.database   import addDateInRange
from library.Utils      import forceBool, forceInt, forceRef, forceString, getVal

from Reports.DeathList  import addCondForDeathCurcumstance, CDeathReportSetupDialog
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase


def selectData(begDate, endDate, place, cause, foundBy, foundation):
    stmt="""
SELECT
  COUNT(*) AS cnt,
  (Event.isPrimary = 1 ) AS autopsy,
  (IF(FDiagnosis.MKB IS NULL, PDiagnosis.MKB, FDiagnosis.MKB) BETWEEN 'C00' AND 'C97.999') AS oncology,
  (IF(FDiagnosis.MKB IS NULL, PDiagnosis.MKB, FDiagnosis.MKB) BETWEEN 'I60' AND 'I64.999') AS cardiology,
  Event.result_id AS result_id
FROM
  Event
  LEFT JOIN EventType ON EventType.id = Event.eventType_id
  LEFT JOIN Client ON Client.id = Event.client_id
  LEFT JOIN ClientAddress ON ClientAddress.client_id = Client.id
                             AND ClientAddress.id = (SELECT MAX(id) FROM ClientAddress AS CA WHERE CA.Type=0 and CA.client_id = Client.id)
  LEFT JOIN Diagnostic AS PDiagnostic ON PDiagnostic.event_id = Event.id
  LEFT JOIN rbDiagnosisType AS PDiagnosisType ON PDiagnosisType.id = PDiagnostic.diagnosisType_id
  LEFT JOIN Diagnosis  AS PDiagnosis ON PDiagnosis.id = PDiagnostic.diagnosis_id
  LEFT JOIN Diagnostic AS FDiagnostic ON FDiagnostic.event_id = Event.id
  LEFT JOIN rbDiagnosisType AS FDiagnosisType ON FDiagnosisType.id = FDiagnostic.diagnosisType_id
  LEFT JOIN Diagnosis  AS FDiagnosis ON FDiagnosis.id = FDiagnostic.diagnosis_id
  LEFT JOIN rbResult ON rbResult.id = Event.result_id

WHERE
  EventType.code = '15'
  AND PDiagnosisType.code = '8'
  AND FDiagnosisType.code = '4'
  AND %s
GROUP BY autopsy, oncology, cardiology, result_id
    """
    db = QtGui.qApp.db
    tableEvent  = db.table('Event')
    cond = []
    cond.append(tableEvent['deleted'].eq(0))
    addDateInRange(cond, tableEvent['setDate'], begDate, endDate)
    if place or cause or foundBy or foundation:
        addCondForDeathCurcumstance(cond, tableEvent, place, cause, foundBy, foundation)

    return db.query(stmt % (db.joinAnd(cond)))


class CDeathSurvey(CReport):

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Сводка по умершим')


    def getSetupDialog(self, parent):
        result = CDeathReportSetupDialog(parent)
        result.setTitle(self.title())
        return result


    def build(self, params):
        begDate = getVal(params, 'begDate', QtCore.QDate())
        endDate = getVal(params, 'endDate', QtCore.QDate())
        place = params.get('deathPlace', '')
        cause = params.get('deathCause', '')
        foundBy = params.get('deathFoundBy', '')
        foundation = params.get('deathFoundation', '')

        query = selectData(begDate, endDate, place, cause, foundBy, foundation)

        cntTotal = 0
        cntAutopsy = 0
        cntOncology = 0
        cntCardiology = 0
        cntResults = {}
        self.setQueryText(forceString(query.lastQuery()))
        while query.next() :
            record   = query.record()
            cnt      = forceInt(record.value('cnt'))
            autopsy  = forceBool(record.value('autopsy'))
            oncology = forceBool(record.value('oncology'))
            cardiology = forceBool(record.value('cardiology'))
            resultId   = forceInt(record.value('result_id'))

            cntTotal += cnt
            if autopsy:
                cntAutopsy += cnt
            if oncology:
                cntOncology += cnt
            if cardiology:
                cntCardiology += cnt
            cntResults[resultId] = cntResults.get(resultId, 0) + cnt

        db = QtGui.qApp.db
        tableResult = db.table('rbResult')

        reportData = [
                        (u'Всего умерло',  cntTotal),
                        (u'- в том числе от онкозаболеваний', cntOncology),
                        (u'- в том числе от ОНМК',            cntCardiology),
                        (u'Из общего числа:',                 ''),
                        (u'- вскрытий было',                  cntAutopsy),
                        (u'- вскрытий не было',               cntTotal-cntAutopsy),
                        (u'Результаты:',                      ''),
                     ]
        for record in db.getRecordList(tableResult, 'id, name', tableResult['id'].inlist(cntResults.keys()), 'code'):
            id   = forceRef(record.value('id'))
            name = forceString(record.value('name'))
            reportData.append(('- '+name, cntResults.get(id, 0) ))


        tableColumns = [
            ('70%', [u'показатель'],  CReportBase.AlignLeft),
            ('20%', [u'значение'],    CReportBase.AlignRight),
            ]

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        table = createTable(cursor, tableColumns)

        for row in reportData:
            i = table.addRow()
            table.setText(i, 0, row[0])
            table.setText(i, 1, row[1])

        return doc
