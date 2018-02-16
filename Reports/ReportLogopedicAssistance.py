# -*- coding: utf-8 -*-

__author__ = 'andreyk'

from PyQt4 import QtCore, QtGui

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Ui_ReportPnd import Ui_ReportPnd
from library.Utils import forceDate, forceInt, forceRef, forceString, pyDate, getVal


def selectData(begDate, endDate, personId, rowGrouping):
    db = QtGui.qApp.db

    tablePerson = db.table('Person')
    tableAction = db.table('Action')
    tableActionType = db.table('ActionType')
    tableActionPropertyType = db.table('ActionPropertyType')
    tableActionProperty = db.table('ActionProperty')
    tableAPInteger = db.table('ActionProperty_Integer')
    tableEvent = db.table('Event')
    tableClient = db.table('Client')

    queryTable = tableAction.innerJoin(tablePerson, tablePerson['id'].eq(tableAction['setPerson_id']))
    queryTable = queryTable.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
    queryTable = queryTable.innerJoin(tableActionProperty, tableActionProperty['action_id'].eq(tableAction['id']))
    queryTable = queryTable.innerJoin(
        tableActionPropertyType,
        tableActionPropertyType['id'].eq(tableActionProperty['type_id'])
    )
    queryTable = queryTable.innerJoin(tableAPInteger, tableAPInteger['id'].eq(tableActionProperty['id']))
    queryTable = queryTable.innerJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
    queryTable = queryTable.innerJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))

    if rowGrouping == 1:  # by personId
        groupField = 'Action.setPerson_id'
    else:
        groupField = 'DATE(Action.begDate)'

    cols = [
        '%s AS rowKey' % groupField,
        u'''
        sum(if(ActionPropertyType.name = 'Дети', ActionProperty_Integer.value, 0)) AS children,
        sum(if(ActionPropertyType.name = 'Подростки', ActionProperty_Integer.value, 0)) AS teens,
        sum(if(ActionPropertyType.name = 'Взрослые', ActionProperty_Integer.value, 0)) AS adults,
        sum(if(ActionPropertyType.name = 'Лиц, закончивших занят', ActionProperty_Integer.value, 0)) AS finished,
        sum(if(ActionPropertyType.name = 'Дети', ActionProperty_Integer.value, 0) +
            if(ActionPropertyType.name = 'Подростки', ActionProperty_Integer.value, 0) +
            if(ActionPropertyType.name = 'Взрослые', ActionProperty_Integer.value, 0)) AS summary
        '''
    ]

    cond = [
        tableAction['begDate'].dateLe(endDate),
        tableAction['begDate'].dateGe(begDate),
        tablePerson['deleted'].eq(0),
        tableActionPropertyType['deleted'].eq(0),
        tableActionType['code'].eq('02_14')
    ]

    group = u'rowKey'

    if personId:
        cond.append(tableAction['setPerson_id'].eq(personId))

    stmt = db.selectStmt(queryTable, cols, cond, group=group)
    query = db.query(stmt)
    return query


class CReportLogopedicAssistance(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Логопедическая помощь')

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
                QtGui.qApp.db.translate('vrbPersonWithSpeciality', 'id', personId, 'name')
            )
            keyName = u'Логопед'
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
            ('%5', [u'от 0 до 14 лет'], CReportBase.AlignLeft),
            ('%5', [u'от 14 до 18 лет'], CReportBase.AlignLeft),
            ('%5', [u'старше 18 лет'], CReportBase.AlignLeft),
            ('%5', [u'из низ законченных случаев'], CReportBase.AlignLeft),
            ('%5', [u'Итого'], CReportBase.AlignLeft)
        ]
        table = createTable(cursor, tableColumns)

        total = [0] * 5
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            rowKey = forceKeyVal(record.value('rowKey'))
            children = forceInt(record.value('children'))
            teens = forceInt(record.value('teens'))
            adults = forceInt(record.value('adults'))
            finished = forceInt(record.value('finished'))
            summary = forceInt(record.value('summary'))
            i = table.addRow()
            table.setText(i, 0, keyValToString(rowKey))
            table.setText(i, 1, children)
            table.setText(i, 2, teens)
            table.setText(i, 3, adults)
            table.setText(i, 4, finished)
            table.setText(i, 5, summary)

            total[0] += children
            total[1] += teens
            total[2] += adults
            total[3] += finished
            total[4] += summary

        i = table.addRow()
        table.setText(i, 0, u'Всего', CReportBase.TableTotal)
        for j in xrange(len(total)):
            table.setText(i, j + 1, total[j], CReportBase.TableTotal)

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


def main():
    import sys
    from s11main import CS11mainApp
    from library.database import connectDataBaseByInfo

    QtGui.qApp = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    connectionInfo = {
        'driverName': 'mysql',
        'host': 'pnd6',
        'port': 3306,
        'database': 's11',
        'user': 'dbuser',
        'password': 'dbpassword',
        'connectionName': 'vista-med',
        'compressData': True,
        'afterConnectFunc': None
    }
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    w = CReportLogopedicAssistance(None)
    w.exec_()


if __name__ == '__main__':
    main()
