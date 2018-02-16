# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils import forceDate, forceInt, forceRef, forceString, pyDate, getVal, forceDouble

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase

from Ui_ReportPnd import Ui_ReportPnd


def selectData(begDate, endDate, personId, rowGrouping):
    db = QtGui.qApp.db

    tablePerson = db.table('Person')
    tableAction = db.table('Action')
    tableActionType = db.table('ActionType')
    tableActionPropertyType = db.table('ActionPropertyType')
    tableActionProperty = db.table('ActionProperty')
    tableAPInteger = db.table('ActionProperty_Integer')

    queryTable = tableAction.innerJoin(tablePerson, tablePerson['id'].eq(tableAction['setPerson_id']))
    queryTable = queryTable.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
    queryTable = queryTable.innerJoin(tableActionProperty, tableActionProperty['action_id'].eq(tableAction['id']))
    queryTable = queryTable.innerJoin(tableActionPropertyType,
                                      tableActionPropertyType['id'].eq(tableActionProperty['type_id']))
    queryTable = queryTable.innerJoin(tableAPInteger, tableAPInteger['id'].eq(tableActionProperty['id']))

    if rowGrouping == 1:  # by personId
        groupField = 'Action.setPerson_id'
    else:
        groupField = 'DATE(Action.begDate)'

    cols = ['%s AS rowKey' % groupField,
            u'''sum(if(ActionPropertyType.name = 'консультация', ActionProperty_Integer.value, 0)) AS cons,
                sum(if(ActionPropertyType.name = 'ЭЭГ', ActionProperty_Integer.value, 0)) AS eed,
                sum(if(ActionPropertyType.name = 'УЗДГ', ActionProperty_Integer.value, 0)) AS uzdg,
                sum(if(ActionPropertyType.name = 'консультация', ActionProperty_Integer.value, 0)*1.8
                    +if(ActionPropertyType.name = 'ЭЭГ', ActionProperty_Integer.value, 0)*6
                    +if(ActionPropertyType.name = 'УЗДГ', ActionProperty_Integer.value, 0)*5
                    )AS Summary'''
            ]

    cond = [tableAction['begDate'].dateLe(endDate),
            tableAction['begDate'].dateGe(begDate),
            tablePerson['deleted'].eq(0),
            tableAction['deleted'].eq(0),
            tableActionProperty['deleted'].eq(0),
            tableActionType['deleted'].eq(0),
            tableActionPropertyType['deleted'].eq(0),
            tableActionType['code'].eq('002_10')]

    group = u'rowKey'

    if personId:
        cond.append(tableAction['setPerson_id'].eq(personId))

    stmt = db.selectStmt(queryTable, cols, cond, group=group)
    query = db.query(stmt)
    return query


class CReportNeurologicalAss(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Неврологическая помощь')

    def getSetupDialog(self, parent):
        result = CReportPnd(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        begDate = params.get('begDate', None)
        endDate = params.get('endDate', None)
        personId = params.get('personId', None)
        rowGrouping = params.get('rowGrouping', 0)
        query = selectData(begDate, endDate, personId, rowGrouping)

        if rowGrouping == 1:  # by personId
            forceKeyVal = forceRef
            keyValToString = lambda personId: forceString(
                QtGui.qApp.db.translate('vrbPersonWithSpeciality', 'id', personId, 'name'))
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
            ('%20', [keyName], CReportBase.AlignLeft),
            ('%5', [u'консультация'], CReportBase.AlignLeft),
            ('%5', [u'ЭЭГ'], CReportBase.AlignLeft),
            ('%5', [u'УЗДГ'], CReportBase.AlignLeft),
            ('%5', [u'УЕТ'], CReportBase.AlignLeft)
        ]
        table = createTable(cursor, tableColumns)

        boldChars = QtGui.QTextCharFormat()
        boldChars.setFontWeight(QtGui.QFont.Bold)

        boldItalicChars = QtGui.QTextCharFormat()
        boldItalicChars.setFontWeight(QtGui.QFont.Bold)
        boldItalicChars.setFontItalic(True)

        total = [0] * 4
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            row = table.addRow()
            fields = (
                forceKeyVal(record.value('rowKey')),
                forceInt(record.value('cons')),
                forceInt(record.value('eed')),
                forceInt(record.value('uzdg')),
                forceDouble(record.value('Summary'))
            )

            for col, val in enumerate(fields):
                if col == 0:
                    table.setText(row, 0, keyValToString(val))
                else:
                    table.setText(row, col, val, CReportBase.TableTotal)
                    total[col - 1] += val

        row = table.addRow()
        table.setText(row, 0, u'Всего', CReportBase.TableTotal)
        for j in xrange(4):
            table.setText(row, j + 1, total[j], CReportBase.TableTotal)

        return doc


class CReportPnd(QtGui.QDialog, Ui_ReportPnd):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbPerson.setValue(params.get('personId', None))
        self.cmbRowGrouping.setCurrentIndex(getVal(params, 'rowGrouping', 0))

    def params(self):
        params = {}
        params['begDate'] = self.edtBegDate.date()
        params['endDate'] = self.edtEndDate.date()
        params['personId'] = self.cmbPerson.value()
        params['rowGrouping'] = self.cmbRowGrouping.currentIndex()
        return params

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.cmbPerson.setEndDate(QtCore.QDate(date))
