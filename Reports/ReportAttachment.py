# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils       import forceDate, forceRef, forceString

from Reports.Report      import CReport
from Reports.ReportBase  import createTable, CReportBase

from Ui_ReportAttachment import Ui_ReportAttachment


def selectData(params):
    begDate      = params.get('begDate', None)
    endDate      = params.get('endDate', None)

    db = QtGui.qApp.db

    tableClient       = db.table('Client')
    tableClientMonitoring = db.table('ClientMonitoring')
    tableClientMonitoringKind   = db.table('rbClientMonitoringKind')

    queryTable = tableClient.innerJoin(tableClientMonitoring, tableClientMonitoring['client_id'].eq(tableClient['id']))
    queryTable = queryTable.innerJoin(tableClientMonitoringKind, tableClientMonitoringKind['id'].eq(tableClientMonitoring['kind_id']))

    cols = [tableClient['lastName'],
            tableClient['firstName'],
            tableClient['patrName'],
            tableClientMonitoringKind['code'],
            tableClientMonitoring['setDate'],
            tableClientMonitoring['endDate']]

    cond = [tableClientMonitoring['setDate'].dateLe(endDate),
            tableClientMonitoring['setDate'].dateGe(begDate),
            db.joinOr([tableClientMonitoringKind['code'].eq(u'К'), tableClientMonitoringKind['code'].eq(u'Д')]),
            tableClient['deleted'].eq(0),
            tableClientMonitoring['deleted'].eq(0)]

    order = tableClient['lastName'].name()

    stmt = db.selectStmt(queryTable, cols, cond, order=order)
    query = db.query(stmt)
    return query


class CReportAttachment(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Установлено/снято с наблюдения')
        self.resetHelpers()

    def resetHelpers(self):
        self.tableAttachK = {}
        self.tableAttachD= {}
        self.tableDetachK = {}
        self.tableDetachD = {}

    def getSetupDialog(self, parent):
        result = CAttachment(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        beg = params.get('bDate', True)
        end = params.get('eDate', True)
        typeK = params.get('typeK', True)
        typeD = params.get('typeD', True)

        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        self.formationTable(query, params)
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        tableColumns = [('%5',[u'№'], CReportBase.AlignRight),
                        ('%20',  [u'Клиент'], CReportBase.AlignLeft)]

        if typeK and beg:
            self.fillTable(cursor, self.tableAttachK, tableColumns, params, u'Установлено наблюдение К')

        if typeD and beg:
            self.fillTable(cursor, self.tableAttachD, tableColumns, params, u'Установлено наблюдение Д')

        if typeK and end:
            self.fillTable(cursor, self.tableDetachK, tableColumns, params, u'Снято наблюдение К')

        if typeD and end:
            self.fillTable(cursor, self.tableDetachD, tableColumns, params, u'Снято наблюдение Д')
        return doc

    def fillTable(self, cursor, dicTable, tableColumns, params, title = None):
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(title)
        self.dumpParams(cursor, params)
        table = createTable(cursor, tableColumns)
        for key in dicTable:
            i = table.addRow()
            table.setText(i, 0, i)
            table.setText(i, 1, dicTable[key])
        i = table.addRow()
        table.setText(i, 0, u'Всего')
        table.setText(i, 1, i-1)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()

    def formationTable(self,query, params):
        begDate      = params.get('begDate', None)
        endDate      = params.get('endDate', None)
        beg          = params.get('bDate', True)
        end          = params.get('eDate', True)
        typeK        = params.get('typeK', True)
        typeD        = params.get('typeD', True)

        keyAttachK = 0
        keyAttachD = 0
        keyDetachK = 0
        keyDetachD = 0

        while query.next():
            record = query.record()
            nameClient = forceString(record.value('lastName')) + ' ' + forceString(record.value('firstName')) + ' ' + forceString(record.value('patrName'))
            attach = forceRef(record.value('code'))
            dateBeg = forceDate(record.value('begDate'))
            dateEnd = forceDate(record.value('endDate'))

            if typeK and beg and attach == u'К' and dateBeg > begDate and dateBeg < endDate :
                self.tableAttachK[keyAttachK] = nameClient
                keyAttachK += 1
            if typeD and beg and attach == u'Д' and dateBeg > begDate and dateBeg < endDate:
                self.tableAttachD[keyAttachD] = nameClient
                keyAttachD += 1
            if typeK and end and attach == u'К' and dateEnd > begDate and dateEnd < endDate:
                self.tableDetachK[keyDetachK] = nameClient
                keyDetachK += 1
            if typeD and end and attach == u'Д' and dateEnd > begDate and dateEnd < endDate:
                self.tableDetachK[keyDetachD] = nameClient
                keyDetachD += 1

class CAttachment(QtGui.QDialog, Ui_ReportAttachment):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.chkBegDate.setChecked(params.get('bDate', True))
        self.chkEndDate.setChecked(params.get('eDate', True))
        self.chkTypeK.setChecked(params.get('typeK', True))
        self.chkTypeD.setChecked(params.get('typeD', True))

    def params(self):
        params = {}
        params['begDate'] = self.edtBegDate.date()
        params['endDate'] = self.edtEndDate.date()
        params['bDate']   = self.chkBegDate.isChecked()
        params['eDate']   = self.chkEndDate.isChecked()
        params['typeK']   = self.chkTypeK.isChecked()
        params['typeD']   = self.chkTypeD.isChecked()
        return params

    @QtCore.pyqtSlot(bool)
    def on_chkTypeK_clicked(self):
        if not self.chkTypeD.isChecked():
            self.chkTypeK.setChecked(True)

    @QtCore.pyqtSlot(bool)
    def on_chkTypeD_clicked(self):
        if not self.chkTypeK.isChecked():
            self.chkTypeD.setChecked(True)

    @QtCore.pyqtSlot(bool)
    def on_chkBegDate_clicked(self):
        if not self.chkEndDate.isChecked():
            self.chkBegDate.setChecked(True)

    @QtCore.pyqtSlot(bool)
    def on_chkEndDate_clicked(self):
        if not self.chkBegDate.isChecked():
            self.chkEndDate.setChecked(True)
