# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils                      import forceInt, forceString


from Reports.Report                     import CReport
from Reports.ReportBase                 import createTable, CReportBase

from Ui_ReportBaseSetup import Ui_ReportBaseSetup

def selectData(params):
    begDate = params.get('begDate', QtCore.QDate()).toString(QtCore.Qt.ISODate)
    endDate = params.get('endDate', QtCore.QDate()).toString(QtCore.Qt.ISODate)

    stmt = u'''SELECT rbThesaurus.name
                    , COUNT(rbThesaurus.id) AS count
                    , rbThesaurus.code
               FROM EventType
                      INNER JOIN Event ON Event.eventType_id = EventType.id AND Event.deleted = 0
                      INNER JOIN Action ON Action.event_id = Event.id AND Action.deleted = 0
                      INNER JOIN ActionType ON ActionType.id = Action.actionType_id AND ActionType.code = '04' AND ActionType.deleted = 0
                      INNER JOIN ActionPropertyType ON ActionPropertyType.actionType_id = ActionType.id AND ActionPropertyType.name = 'наименование' AND ActionPropertyType.deleted = 0
                      INNER JOIN ActionProperty ON ActionProperty.action_id = Action.id AND ActionProperty.type_id = ActionPropertyType.id AND ActionProperty.deleted = 0
                      INNER JOIN ActionProperty_String ON ActionProperty_String.id = ActionProperty.id
                      INNER JOIN rbThesaurus ON ActionProperty_String.value LIKE CONCAT('%%', rbThesaurus.name, '%%') AND rbThesaurus.code LIKE '3%%'
               WHERE EventType.code = '21' AND Date(Action.endDate) >= Date('%s') AND DATE(Action.endDate) <= Date('%s') AND EventType.deleted = 0
               GROUP BY rbThesaurus.id
               HAVING code LIKE '3-%%' ''' % (begDate, endDate)
    return QtGui.qApp.db.query(stmt)

class CReportMedicinesSMP(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчет по лекарственным средствам СМП')

    def getSetupDialog(self, parent):
        result = CReportBaseSetup(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
            ('20%',  [u'Наименование'                                          ], CReportBase.AlignLeft),
            ('3%',   [u'Количество'], CReportBase.AlignRight)]

        table = createTable(cursor, tableColumns)

        total = 0
        while query.next():
            record = query.record()
            name = forceString(record.value('name'))
            count = forceInt(record.value('count'))

            i = table.addRow()
            table.setText(i, 0, name)
            table.setText(i, 1, count)
            total += count
        i = table.addRow()
        table.setText(i, 0, u'Итого', CReportBase.TableTotal)
        table.setText(i, 1, total, CReportBase.TableTotal)
        return doc

class CReportBaseSetup(QtGui.QDialog, Ui_ReportBaseSetup):
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
