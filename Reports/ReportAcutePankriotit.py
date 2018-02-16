# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils      import forceInt, forceString
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase

from Ui_ReportAcutePankriotit import Ui_ReportAcutePankriotit


def selectData(begDate, endDate):
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    tableAct = db.table('Action').alias('act')

    actTypeIdList = db.getIdList('ActionType', where=u'code LIKE \'6%\' OR code LIKE \'о%\'')
    actCond = tableAct['actionType_id'].inlist(actTypeIdList) if actTypeIdList else '0'

    cond = [tableEvent['deleted'].eq(0),
            tableEvent['setDate'].dateLe(endDate),
            tableEvent['setDate'].dateGe(begDate)]

    stmt = u'''SELECT count(LeavedAction.id) AS leaved,
                      count(if(rbResult.code IN ('105', '106', '205', '206'), LeavedAction.id, NULL)) AS leavedDeath,
                      sum(if(opAction.id IS NULL, 1, 0)) AS notOperation,
                      sum(if(opAction.id IS NULL AND rbResult.code IN ('105', '106', '205', '206'), 1, 0)) AS notOperationDeath,
                      count(opAction.id) AS operation,
                      count(if(rbResult.code IN ('105', '106', '205', '206'), opAction.id, NULL)) AS operationDeath,
                      count(if(DATEDIFF(opAction.begDate, Event.setDate) < 7, opAction.id, NULL)) AS operationBefore,
                      count(if(DATEDIFF(opAction.begDate, Event.setDate) < 7 AND rbResult.code IN ('105', '106', '205', '206'), opAction.id, NULL)) AS operationDeathBefore,
                      count(if(DATEDIFF(opAction.begDate, Event.setDate) > 7, opAction.id, NULL)) AS operationAfter,
                      count(if(DATEDIFF(opAction.begDate, Event.setDate) > 7 AND rbResult.code IN ('105', '106', '205', '206'), opAction.id, NULL)) AS operationDeathAfter
                FROM
                    Event
                    INNER JOIN Action ON Action.event_id AND Action.id = (SELECT max(act.id)
                                                                          FROM Action act
                                                                          INNER JOIN ActionType actType ON act.actionType_id = actType.id AND actType.flatCode = 'moving'
                                                                          WHERE act.deleted = 0 AND act.event_id = Event.id)

                    INNER JOIN mes.MES mes ON Action.MES_id = mes.id AND mes.code IN (311200, 311210, 311220)
                    LEFT JOIN ActionType leavedActionType ON leavedActionType.deleted = 0 AND leavedActionType.flatCode = 'leaved'
                    INNER JOIN Action LeavedAction ON LeavedAction.event_id = Action.event_id AND LeavedAction.actionType_id = leavedActionType.id
                    LEFT JOIN Action opAction ON opAction.id = (SELECT MAX(id)
                                                                FROM Action act
                                                                WHERE act.deleted = 0 AND act.event_id = Event.id AND %s)
                    LEFT JOIN rbResult ON rbResult.id = Event.result_id
                    WHERE
                        %s
                    GROUP BY mes.code''' % (actCond, db.joinAnd(cond))
    return db.query(stmt)

class CReportAcutePankriotit(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Доп. сведения по экстренной хирургической помощи по "Острому панкреатиту"')


    def getSetupDialog(self, parent):
        result = CAcutePankriotit(parent)
        result.setTitle(self.title())
        return result

    def build(self,params):
        begDate = params.get('begDate')
        endDate = params.get('endDate')

        query = selectData(begDate, endDate)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [('2%',  [u'Степень тяжести заболевания'],                             CReportBase.AlignLeft),
                        ('15%', [u'Выбыло человек',         u'',                  u'Всего'],  CReportBase.AlignLeft),
                        ('10%', [u'',                       u'',                  u'Умерло'], CReportBase.AlignLeft),
                        ('15%', [u'Не оперировано человек', u'',                  u'Всего'],  CReportBase.AlignLeft),
                        ('10%', [u'',                       u'',                  u'Умерло'], CReportBase.AlignLeft),
                        ('10%', [u'Оперировано человек',    u'Всего'],                        CReportBase.AlignLeft),
                        ('10%', [u'',                       u'Умерло'],                       CReportBase.AlignLeft),
                        ('5%',  [u'',                       u'В срок до 7 суток', u'Всего'],  CReportBase.AlignLeft),
                        ('5%',  [u'',                       u'',                  u'Умерло'], CReportBase.AlignLeft),
                        ('5%',  [u'',                       u'Позднее 7 суток',   u'Всего'],  CReportBase.AlignLeft),
                        ('10%', [u'',                       u'',                  u'Умерло'], CReportBase.AlignLeft)]
        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 3, 1) #Степень тяжески заболевания
        table.mergeCells(0, 1, 2, 2) #Выбыло человек
        table.mergeCells(0, 3, 2, 2) #Не оперировано человек
        table.mergeCells(0, 5, 1, 6) #Оперировано человек
        table.mergeCells(1, 5, 2, 1) #Всего
        table.mergeCells(1, 6, 2, 1) #Умерло
        table.mergeCells(1, 7, 1, 2) #В срок до 7 суток
        table.mergeCells(1, 9, 1, 2) #Позднее 7 суток
        rows = [u'Легкая', u'Средняя', u'Тяжелая']
        while query.next():
            record = query.record()
            leaved = forceInt(record.value('leaved'))
            leavedDeath = forceInt(record.value('leavedDeath'))
            notOperation = forceInt(record.value('notOperation'))
            notOperationDeath = forceInt(record.value('notOperationDeath'))
            operation = forceInt(record.value('operation'))
            operationDeath = forceInt(record.value('operationDeath'))
            operationBefore = forceInt(record.value('operationBefore'))
            operationDeathBefore = forceInt(record.value('operationDeathBefore'))
            operationAfter = forceInt(record.value('operationAfter'))
            operationDeathAfter = forceInt(record.value('operationDeathAfter'))
            i = table.addRow()
            table.setText(i, 0, rows[i-3])
            table.setText(i, 1, leaved)
            table.setText(i, 2, leavedDeath)
            table.setText(i, 3, notOperation)
            table.setText(i, 4, notOperationDeath)
            table.setText(i, 5, operation)
            table.setText(i, 6, operationDeath)
            table.setText(i, 7, operationBefore)
            table.setText(i, 8, operationDeathBefore)
            table.setText(i, 9, operationAfter)
            table.setText(i, 10, operationDeathAfter)
        return doc

class CAcutePankriotit(QtGui.QDialog, Ui_ReportAcutePankriotit):
    def __init__(self, parent = None):
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
