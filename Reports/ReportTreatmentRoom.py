
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils      import forceDate, forceInt, forceRef, forceString, pyDate, getVal

from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase

from Ui_ReportPnd import Ui_ReportPnd


def selectData(begDate, endDate, personId, rowGrouping):

    db = QtGui.qApp.db

    tablePerson             = db.table('Person')
    tableAction             = db.table('Action')
    tableActionType         = db.table('ActionType')
    tableActionPropertyType = db.table('ActionPropertyType')
    tableActionProperty     = db.table('ActionProperty')
    tableAPInteger          = db.table('ActionProperty_Integer')

    queryTable = tableAction.innerJoin(tablePerson, tablePerson['id'].eq(tableAction['setPerson_id']))
    queryTable = queryTable.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
    queryTable = queryTable.innerJoin(tableActionProperty, tableActionProperty['action_id'].eq(tableAction['id']))
    queryTable = queryTable.innerJoin(tableActionPropertyType, tableActionPropertyType['id'].eq(tableActionProperty['type_id']))
    queryTable = queryTable.innerJoin(tableAPInteger, tableAPInteger['id'].eq(tableActionProperty['id']))

    if rowGrouping == 1: # by personId
        groupField = 'Action.setPerson_id'
    else:
        groupField = 'DATE(Action.begDate)'

    cols = ['%s AS rowKey' % groupField,
            u'''sum(if(ActionPropertyType.name = 'в/венно', ActionProperty_Integer.value, 0)) AS vena,
                sum(if(ActionPropertyType.name = 'в/в капельно', ActionProperty_Integer.value, 0)) AS drip,
                sum(if(ActionPropertyType.name = 'в/мышечно', ActionProperty_Integer.value, 0)) AS muscle,
                sum(if(ActionPropertyType.name = 'АД', ActionProperty_Integer.value, 0)) AS AD,
                sum(if(ActionPropertyType.name = 'АТМ', ActionProperty_Integer.value, 0)) AS ATM,
                sum(if(ActionPropertyType.name = 'АТМ', ActionProperty_Integer.value, 0)
                    +if(ActionPropertyType.name = 'АД', ActionProperty_Integer.value, 0)
                    +(if(ActionPropertyType.name = 'в/мышечно', ActionProperty_Integer.value, 0))
                    +(if(ActionPropertyType.name = 'в/в капельно', ActionProperty_Integer.value, 0))
                    +(if(ActionPropertyType.name = 'в/венно', ActionProperty_Integer.value, 0))
                    )AS Summary'''
            ]

    cond = [tableAction['begDate'].dateLe(endDate),
            tableAction['begDate'].dateGe(begDate),
            tablePerson['deleted'].eq(0),
            #tableActionProperty['deleted'].eq(0),
            tableActionPropertyType['deleted'].eq(0),
            tableActionType['code'].eq('002_2')]

    group = u'rowKey'

    if personId:
        cond.append(tableAction['setPerson_id'].eq(personId))

    stmt = db.selectStmt(queryTable, cols, cond, group=group)
    query = db.query(stmt)
    return query

class CReportTreatmentRoom(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Процедурный кабинет')

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
                        ('%5',  [u'в/венно'], CReportBase.AlignLeft),
                        ('%5',  [u'в/в капельно'], CReportBase.AlignLeft),
                        ('%5',  [u'в/мышечно'], CReportBase.AlignLeft),
                        ('%5',  [u'АД'], CReportBase.AlignLeft),
                        ('%5',  [u'АТМ'], CReportBase.AlignLeft),
                        ('%5',  [u'Сумма'], CReportBase.AlignLeft)]
        table = createTable(cursor, tableColumns)

        boldChars = QtGui.QTextCharFormat()
        boldChars.setFontWeight(QtGui.QFont.Bold)

        boldItalicChars = QtGui.QTextCharFormat()
        boldItalicChars.setFontWeight(QtGui.QFont.Bold)
        boldItalicChars.setFontItalic(True)

        total = [0]*6
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            rowKey     = forceKeyVal(record.value('rowKey'))
            vena       = forceInt(record.value('vena'))
            drop       = forceInt(record.value('drip'))
            muscle     = forceInt(record.value('muscle'))
            ad         = forceInt(record.value('AD'))
            atm        = forceInt(record.value('ATM'))
            sum        = forceInt(record.value('Summary'))
            i = table.addRow()
            table.setText(i, 0, keyValToString(rowKey))
            table.setText(i, 1, vena)
            total[0] = total[0] + vena
            table.setText(i, 2, drop)
            total[1] = total[1] + drop
            table.setText(i, 3, muscle)
            total[2] = total[2] + muscle
            table.setText(i, 4, ad)
            total[3] = total[3] + ad
            table.setText(i, 5, atm)
            total[4] = total[4] + atm
            table.setText(i, 6, sum)
            total[5] = total[5] + sum
        i = table.addRow()
        table.setText(i, 0, u'Всего', CReportBase.TableTotal )
        for j in xrange(6):
            table.setText(i, j+1, total[j], CReportBase.TableTotal)
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
        params['begDate']     = self.edtBegDate.date()
        params['endDate']     = self.edtEndDate.date()
        params['personId'] = self.cmbPerson.value()
        params['rowGrouping'] = self.cmbRowGrouping.currentIndex()
        return params

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.cmbPerson.setEndDate(QtCore.QDate(date))