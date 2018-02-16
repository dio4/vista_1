
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils               import forceDate, forceInt, forceRef, forceString, pyDate

from Reports.Report              import CReport
from Reports.ReportBase          import createTable, CReportBase
from Reports.ReportTreatmentRoom import CReportPnd


def selectData(begDate, endDate, personId, rowGrouping):

    db = QtGui.qApp.db

    tablePerson             = db.table('Person')
    tableAction             = db.table('Action')
    tableActionType         = db.table('ActionType')
    tableActionPropertyType = db.table('ActionPropertyType')
    tableActionProperty     = db.table('ActionProperty')
    tableAPInteger          = db.table('ActionProperty_Integer')

    queryTable = tableAction.innerJoin(tablePerson, tablePerson['id'].eq(tableAction['setPerson_id']))
    queryTable = queryTable.innerJoin(tableActionType, tableAction['actionType_id'].eq(tableActionType['id']))
    queryTable = queryTable.innerJoin(tableActionProperty, tableActionProperty['action_id'].eq(tableAction['id']))
    queryTable = queryTable.innerJoin(tableActionPropertyType, tableActionPropertyType['id'].eq(tableActionProperty['type_id']))
    queryTable = queryTable.innerJoin(tableAPInteger, tableAPInteger['id'].eq(tableActionProperty['id']))

    if rowGrouping == 1: # by personId
        groupField = 'Action.setPerson_id'
    else:
        groupField = 'DATE(Action.begDate)'

    cols = ['%s rowKey' % groupField,
            u'''sum(if(ActionPropertyType.name = 'Справки', ActionProperty_Integer.value, 0)) AS inform,
                sum(if(ActionPropertyType.name = 'ЭЭГ', ActionProperty_Integer.value, 0)) AS eeg,
                sum(if(ActionPropertyType.name = 'Психолог', ActionProperty_Integer.value, 0)) AS psihologist,
                sum(if(ActionPropertyType.name = 'Психотерапевт', ActionProperty_Integer.value, 0)) AS psihoth,
                sum(if(ActionPropertyType.name = 'Психиатр', ActionProperty_Integer.value, 0)) AS psychiatrist,
                sum(if(ActionPropertyType.name = 'Процедурный кабинет', ActionProperty_Integer.value, 0)) AS room,
                sum(if(ActionPropertyType.name = 'Невролог', ActionProperty_Integer.value, 0)) AS nevr,
                sum(if(ActionPropertyType.name = 'Справки', ActionProperty_Integer.value, 0))
                    + sum(if(ActionPropertyType.name = 'ЭЭГ', ActionProperty_Integer.value, 0))
                    + sum(if(ActionPropertyType.name = 'Психолог', ActionProperty_Integer.value, 0))
                    + sum(if(ActionPropertyType.name = 'Психотерапевт', ActionProperty_Integer.value, 0))
                    + sum(if(ActionPropertyType.name = 'Психиатр', ActionProperty_Integer.value, 0))
                    + sum(if(ActionPropertyType.name = 'Процедурный кабинет', ActionProperty_Integer.value, 0))
                    + sum(if(ActionPropertyType.name = 'Невролог', ActionProperty_Integer.value, 0)) AS Summary
                ''']

    cond = [tableAction['begDate'].dateLe(endDate),
            tableAction['begDate'].dateGe(begDate),
            tablePerson['deleted'].eq(0),
            tableActionPropertyType['deleted'].eq(0),
            tableActionType['code'].eq('002_3')]

    group = u'rowKey'

    if personId:
        cond.append(tableAction['setPerson_id'].eq(personId))

    stmt = db.selectStmt(queryTable, cols, cond, group=group)
    query = db.query(stmt)
    return query

class CReportPaidServices(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Платные услуги')

    def getSetupDialog(self, parent):
        result = CReportPnd(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        begDate      = params.get('begDate', None)
        endDate      = params.get('endDate', None)
        personId     = params.get('personId', None)
        rowGrouping = params.get('rowGrouping', 0)
        query = selectData(begDate, endDate, personId, rowGrouping)
        self.setQueryText(forceString(query.lastQuery()))

        if rowGrouping == 1: # by personId
            forceKeyVal = forceRef
            keyValToString = lambda personId: forceString(QtGui.qApp.db.translate('vrbPersonWithSpeciality', 'id', personId, 'name'))
            keyName = u'Врач'
        else:
            forceKeyVal = lambda x: pyDate(forceDate(x))
            keyValToString = lambda x: forceString(QtCore.QDate(x))
            keyName = u'Дата'

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
                        ('%20',  [keyName], CReportBase.AlignLeft),
                        ('%5',  [u'Справки'], CReportBase.AlignLeft),
                        ('%5',  [u'ЭЭГ'], CReportBase.AlignLeft),
                        ('%5',  [u'Психолог'], CReportBase.AlignLeft),
                        ('%5',  [u'Психотерапевт'], CReportBase.AlignLeft),
                        ('%5',  [u'Психиатр'], CReportBase.AlignLeft),
                        ('%5',  [u'Процедурный кабинет'], CReportBase.AlignLeft),
                        ('%5',  [u'Невролог'], CReportBase.AlignLeft),
                        ('%5',  [u'Итого'], CReportBase.AlignLeft),
        ]
        table = createTable(cursor, tableColumns)

        boldChars = QtGui.QTextCharFormat()
        boldChars.setFontWeight(QtGui.QFont.Bold)

        boldItalicChars = QtGui.QTextCharFormat()
        boldItalicChars.setFontWeight(QtGui.QFont.Bold)
        boldItalicChars.setFontItalic(True)

        total = [0]*8

        while query.next():
            record = query.record()
            rowKey      = forceKeyVal(record.value('rowKey'))
            inform      = forceInt(record.value('inform'))
            eeg         = forceInt(record.value('eeg'))
            psihologist = forceInt(record.value('psihologist'))
            psihoth     = forceInt(record.value('psihoth'))
            psychiatrist = forceInt(record.value('psychiatrist'))
            room = forceInt(record.value('room'))
            nevr = forceInt(record.value('nevr'))
            summary = forceInt(record.value('Summary'))
            i = table.addRow()
            table.setText(i, 0, keyValToString(rowKey))
            table.setText(i, 1, inform)
            total[0] = total[0] + inform
            table.setText(i, 2, eeg)
            total[1] = total[1] + eeg
            table.setText(i, 3, psihologist)
            total[2] = total[2] + psihologist
            table.setText(i, 4, psihoth)
            total[3] = total[3] + psihoth
            table.setText(i, 5, psychiatrist)
            total[4] += psychiatrist
            table.setText(i, 6, room)
            total[5] += room
            table.setText(i, 7, nevr)
            total[6] += nevr
            table.setText(i, 8, summary)
            total[7] += summary
        i = table.addRow()
        table.setText(i, 0, u'Всего', CReportBase.TableTotal )
        for j in xrange(8):
            table.setText(i, j+1, total[j], CReportBase.TableTotal)
        return doc
