# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils                      import forceBool, forceInt, forceString

from Reports.Report                     import CReport
from Reports.ReportBase                 import createTable, CReportBase
from Reports.StatReportDDFoundIllnesses import MKBinString

from Ui_ReportLeavedClients             import Ui_ReportLeavedClients


def selectData(params):

    begDate = params.get('begDate')
    endDate = params.get('endDate')

    db = QtGui.qApp.db
    tableLeavedAction = db.table('Action').alias('a1')
    tableMovingAction = db.table('Action').alias('a')
    tableOpAction = db.table('Action').alias('opAction1')
    tableResult = db.table('rbResult').alias('r')

    opActionTypeIdList = db.getIdList('ActionType', where=u'code LIKE \'6%\' OR code LIKE \'о%\'')
    opActionCond = tableOpAction['actionType_id'].inlist(opActionTypeIdList) if opActionTypeIdList else '0'

    cond = [tableLeavedAction['endDate'].dateLe(endDate),
            tableLeavedAction['endDate'].dateGe(begDate),
            tableResult['code'].notInlist(['105', '106', '205', '206']),
            db.joinOr([tableMovingAction['MKB'].like('I%'), tableMovingAction['MKB'].like('O%'),
                       tableMovingAction['MKB'].like('G45%'), tableMovingAction['MKB'].like('K2%')]),
            ]

    stmt = u'''SELECT a.MKB,
    IF(cw.id IS NOT NULL AND cw.freeInput NOT LIKE 'не работает%%' AND cw.freeInput NOT LIKE '%%безработный%%', 1, 0) as isWorking,
    opAction.id IS NOT NULL as isOperation,
    COUNT(DISTINCT a.id) as cnt
FROM Action a1
    INNER JOIN ActionType at1 ON at1.id = a1.actionType_id AND at1.deleted = 0 AND at1.flatCode = 'leaved'
  INNER JOIN Action a ON a.id =
    (SELECT a2.id
        FROM Action a2
        INNER JOIN ActionType at2 ON at2.id = a2.actionType_id
        WHERE at2.flatCode = 'moving'
                AND at2.deleted = 0
                AND a2.deleted = 0
                AND a2.event_id = a1.event_id
                AND a2.MKB != ''
        ORDER BY a2.begDate DESC
        LIMIT 1)
  INNER JOIN Event e ON e.id = a1.event_id AND e.deleted = 0
  INNER JOIN Client c ON c.id = e.client_id AND c.deleted = 0
  LEFT JOIN ClientWork cw ON cw.id = getClientWorkId(e.client_id)
  LEFT JOIN rbResult r ON r.id = e.result_id
  LEFT JOIN Action opAction ON opAction.id = (SELECT MAX(id) FROM Action opAction1 WHERE opAction1.deleted = 0
                AND opAction1.event_id = a1.event_id
                AND %s)
WHERE %s
GROUP BY a.MKB, IF(cw.id IS NOT NULL AND cw.freeInput NOT LIKE 'не работает%%' AND cw.freeInput NOT LIKE '%%безработный%%', 1, 0), opAction.id IS NOT NULL
''' % (opActionCond, db.joinAnd(cond))
    query = db.query(stmt)
    return query

def selectOpData(params):

    begDate = params.get('begDate')
    endDate = params.get('endDate')

    db = QtGui.qApp.db
    tableLeavedAction = db.table('Action').alias('a1')
    tableOpAction = db.table('Action').alias('opAction1')
    tableResult = db.table('rbResult').alias('r')

    opActionTypeIdList = db.getIdList('ActionType', where=u'code LIKE \'6%\' OR code LIKE \'о%\'')
    opActionCond = tableOpAction['actionType_id'].inlist(opActionTypeIdList) if opActionTypeIdList else '0'

    cond = [tableLeavedAction['endDate'].dateLe(endDate),
            tableLeavedAction['endDate'].dateGe(begDate),
            tableResult['code'].notInlist(['105', '106', '205', '206']),
            ]

    stmt = u'''SELECT COUNT(DISTINCT a1.id) as cntAll,
    COUNT(DISTINCT IF(cw.id IS NOT NULL AND cw.freeInput NOT LIKE 'не работает%%' AND cw.freeInput NOT LIKE '%%безработный%%', a1.id, NULL)) as cntWorking
FROM Action a1
    INNER JOIN ActionType at1 ON at1.id = a1.actionType_id AND at1.deleted = 0 AND at1.flatCode = 'leaved'
    INNER JOIN Action a2 ON a2.id =
        (SELECT a.id FROM Action a INNER JOIN ActionType at ON at.id = a.actionType_id
            WHERE at.code IN ('630812', '640809', '640826', '640828', '651306') AND at.deleted = 0 AND a.deleted = 0
                  AND a.event_id = a1.event_id LIMIT 1)
    INNER JOIN Event e ON e.id = a1.event_id AND e.deleted = 0
    INNER JOIN Client c ON c.id = e.client_id AND c.deleted = 0
    LEFT JOIN ClientWork cw ON cw.id = getClientWorkId(e.client_id)
    LEFT JOIN rbResult r ON r.id = e.result_id
    LEFT JOIN Action opAction ON opAction.id = (SELECT MAX(id) FROM Action opAction1 WHERE opAction1.deleted = 0
            AND opAction1.event_id = a1.event_id
            AND %s)
WHERE %s
''' % (opActionCond, db.joinAnd(cond))
    query = db.query(stmt)
    return query


class CReportLeavedClients(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Пациенты, подлежащие сан-кор лечению (Б15)')

    def getSetupDialog(self, parent):
        result = CLeavedClients(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        query = selectData(params)
        queryOp = selectOpData(params)
        self.setQueryText('\n\n'.join([forceString(query.lastQuery()),
                                       forceString(queryOp.lastQuery())
                                       ])
                          )
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
                        ('%20',  [u'Нозология'], CReportBase.AlignLeft),
                        ('%20',  [u'Диапазон диагнозов'], CReportBase.AlignLeft),
                        ('%20',  [u'Выписано больных (без учета умерших)', u'Всего'], CReportBase.AlignLeft),
                        ('%5',   [u'',                                     u'в т.ч. работающих'], CReportBase.AlignLeft)]

        tableOpColumns = [
                        ('%20',  [u'Операции'], CReportBase.AlignLeft),
                        ('%20',  [u'Диапазон диагнозов (услуг, КСГ)'], CReportBase.AlignLeft),
                        ('%20',  [u'Прооперировано больных (без учета умерших)', u'Всего'], CReportBase.AlignLeft),
                        ('%5',   [u'',                                     u'в т.ч. работающих'], CReportBase.AlignLeft)
        ]

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 1, 2)


        boldChars = QtGui.QTextCharFormat()
        boldChars.setFontWeight(QtGui.QFont.Bold)

        boldItalicChars = QtGui.QTextCharFormat()
        boldItalicChars.setFontWeight(QtGui.QFont.Bold)
        boldItalicChars.setFontItalic(True)

        titelsRow = [u'Острое нарушение мозгового кровообращения', u'Патология беременности', u'Острый инфаркт миокарда', u'Нестабильная стенокардия', u'Холецистэктомия (в т.ч. эндоскопическим меодом)', u'По поводу язвенной болезни']
        ranges =['I60-I66, G45', 'O00-O08, O10-O16, O20-O29, O99', 'I21.0-I21.4, I21.9, I23.0-I23.6, I23.8', 'I20.0', '630812, 640809, 640826, 640828, 651306', 'K25, K26']
        self.modelTableWork = [0]*6
        self.modelTable = [0]*6

        while query.next():
            record = query.record()
            MKB  = forceString(record.value('MKB'))
            work = forceBool(record.value('isWorking'))
            isOperation = forceBool(record.value('isOperation'))
            cnt = forceInt(record.value('cnt'))

            for index in xrange(len(ranges)-2):
                if MKBinString(MKB, ranges[index]):
                    self.addRowInTableModel(work, index, cnt)
                    continue
            if isOperation:
                if MKBinString(MKB, ranges[-1]):
                    self.addRowInTableModel(work, 5, cnt)
        queryOp.first()
        record = queryOp.record()
        self.modelTable[-2] += forceInt(record.value('cntAll'))
        self.modelTableWork[-2] += forceInt(record.value('cntWorking'))

        for index in xrange(len(ranges)-2):
            i = table.addRow()
            table.setText(i, 0, titelsRow[index])
            table.setText(i, 1, ranges[index])
            table.setText(i, 2, self.modelTable[index])
            table.setText(i, 3, self.modelTableWork[index])

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText('\n\n')
        cursor.movePosition(QtGui.QTextCursor.End)

        tableOp = createTable(cursor, tableOpColumns)
        tableOp.mergeCells(0, 0, 2, 1)
        tableOp.mergeCells(0, 1, 2, 1)
        tableOp.mergeCells(0, 2, 1, 2)
        for index in xrange(len(ranges)-2, len(ranges)):
            i = tableOp.addRow()
            tableOp.setText(i, 0, titelsRow[index])
            tableOp.setText(i, 1, ranges[index])
            tableOp.setText(i, 2, self.modelTable[index])
            tableOp.setText(i, 3, self.modelTableWork[index])

        return doc

    def addRowInTableModel(self, work, index, cnt):
        self.modelTable[index] += cnt
        if work:
            self.modelTableWork[index] += cnt


class CLeavedClients(QtGui.QDialog, Ui_ReportLeavedClients):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))

    def params(self):
        params = {}
        params['begDate']     = self.edtBegDate.date()
        params['endDate']     = self.edtEndDate.date()
        return params

