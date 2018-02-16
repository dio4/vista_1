# -*- coding: utf-8 -*-

__author__ = 'andreyk'

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
            u'''sum(if(ActionPropertyType.name = 'Взрослые', ActionProperty_Integer.value, 0)) AS adults,
                sum(if(ActionPropertyType.name = 'Дети', ActionProperty_Integer.value, 0)) AS children,
                sum(if(ActionPropertyType.name = 'Подростки', ActionProperty_Integer.value, 0)) AS teens,
                sum(if(ActionPropertyType.name = 'АДН/АПЛ', ActionProperty_Integer.value, 0)) AS adn_apl,
                sum(if(ActionPropertyType.name = 'Босс', ActionProperty_Integer.value, 0)) AS boss,
                sum(if(ActionPropertyType.name = 'Взрослые', ActionProperty_Integer.value, 0) +
                    if(ActionPropertyType.name = 'Дети', ActionProperty_Integer.value, 0) +
                    if(ActionPropertyType.name = 'Подростки', ActionProperty_Integer.value, 0) +
                    if(ActionPropertyType.name = 'АДН/АПЛ', ActionProperty_Integer.value, 0) +
                    if(ActionPropertyType.name = 'Босс', ActionProperty_Integer.value, 0)) AS summary'''
            ]

    cond = [tableAction['begDate'].dateLe(endDate),
            tableAction['begDate'].dateGe(begDate),
            tablePerson['deleted'].eq(0),
                tableActionPropertyType['deleted'].eq(0),
            tableActionType['code'].eq('02_13')]

    group = u'rowKey'

    if personId:
        cond.append(tableAction['setPerson_id'].eq(personId))

    stmt = db.selectStmt(queryTable, cols, cond, group=group)
    query = db.query(stmt)
    return query


class CReportPsychologicalAssistance(CReport):

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Психологическая помощь')

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
        self.setQueryText(forceString(query.lastQuery()))

        if rowGrouping == 1: # by personId
            forceKeyVal = forceRef
            keyValToString = lambda personId: forceString(QtGui.qApp.db.translate('vrbPersonWithSpeciality', 'id', personId, 'name'))
            keyName = u'Психолог'
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
                        ('%5', [u'Взрослые'], CReportBase.AlignLeft),
                        ('%5', [u'Дети'], CReportBase.AlignLeft),
                        ('%5', [u'Подростки'], CReportBase.AlignLeft),
                        ('%5', [u'АДН/АПЛ'], CReportBase.AlignLeft),
                        ('%5', [u'Босс'], CReportBase.AlignLeft),
                        ('%5', [u'Итого'], CReportBase.AlignLeft)
        ]
        table = createTable(cursor, tableColumns)

        total = [0] * 6
        while query.next():
            record = query.record()
            rowKey = forceKeyVal(record.value('rowKey'))
            adults = forceInt(record.value('adults'))
            children = forceInt(record.value('children'))
            teens = forceInt(record.value('teens'))
            adn_apl = forceInt(record.value('adn_apl'))
            boss = forceInt(record.value('boss'))
            summary = forceInt(record.value('summary'))
            i = table.addRow()
            table.setText(i, 0, keyValToString(rowKey))
            table.setText(i, 1, adults)
            table.setText(i, 2, children)
            table.setText(i, 3, teens)
            table.setText(i, 4, adn_apl)
            table.setText(i, 5, boss)
            table.setText(i, 6, summary)
            total[0] += adults
            total[1] += children
            total[2] += teens
            total[3] += adn_apl
            total[4] += boss
            total[5] += summary

        i = table.addRow()
        table.setText(i, 0, u'Всего', CReportBase.TableTotal)
        for j in xrange(len(total)):
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
        params['begDate'] = self.edtBegDate.date()
        params['endDate'] = self.edtEndDate.date()
        params['personId'] = self.cmbPerson.value()
        params['rowGrouping'] = self.cmbRowGrouping.currentIndex()
        return params

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.cmbPerson.setEndDate(QtCore.QDate(date))
