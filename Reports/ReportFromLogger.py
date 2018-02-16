# -*- coding: utf-8 -*-


from PyQt4 import QtGui, QtCore
from Report import CReport
from ReportBase import CReportBase, createTable
from library.Utils import forceString
from library.database import addDateInRange
from Ui_ReportFromLogger import Ui_ReportFromLogger
from library.LoggingModule import Logger

def selectData(begDate, endDate):
    stmt = "SELECT report_name FROM %s.Reports " % (Logger.getLoggerDbName())
    db = QtGui.qApp.db
    tableReports = db.table(Logger.getLoggerDbName() + '.Reports')
    cond = []
    addDateInRange(cond, tableReports['date'], begDate, endDate)
    return db.query(stmt + u"WHERE" + db.joinAnd(cond) + u";")

def selectDataWithDetails(begDate, endDate):
    stmt = """
SELECT report_name, date, lastName, firstName, patrName, lpu
FROM {dbName}.Reports
INNER JOIN {dbName}.Login ON {dbName}.Login.id = {dbName}.Reports.login_id
INNER JOIN Person ON Person.id = {dbName}.Login.person_id
    """.format(dbName=Logger.getLoggerDbName())
    db = QtGui.qApp.db
    tableReports = db.table(Logger.getLoggerDbName() + '.Reports')
    cond = []
    addDateInRange(cond, tableReports['date'], begDate, endDate)
    return db.query(stmt + u"WHERE" + db.joinAnd(cond) + u"ORDER BY lastName, date;")

class CReportFromLogger(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчет о формировании отчетов')

    def getSetupDialog(self, parent):
        result = CReportLogger(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        chkDetail = params.get('chkDetails', False)
        chkGroup = params.get('chkGroup', False)
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        if chkDetail:
            if chkGroup:
                query = selectDataWithDetails(begDate, endDate)
                self.setQueryText(forceString(query.lastQuery()))
                tableColumns = [
                    ('%5', [u"№"], CReportBase.AlignLeft),
                    ('%50', [u"Название отчета"], CReportBase.AlignLeft),
                    ('%50', [u"Количество"], CReportBase.AlignLeft)
                ]
                table = createTable(cursor, tableColumns)
                cnt = 0
                reportsList = []
                reportsNameList = []
                lastNameList = []
                while query.next():
                    record = query.record()
                    lastNameList.append(forceString(record.value('lastName')) + ' ' + forceString(record.value('firstName')) \
                    + " " + forceString(record.value('patrName')))
                    reportsNameList.append(forceString(record.value('report_name')))
                    reportsList.append(record)

                for k in set(lastNameList):
                    fio = forceString(k)
                    i = table.addRow()
                    table.setText(i, 1, u"Пользователь: " + fio)
                    for x in set(reportsNameList):
                        cntReports = []
                        for z in reportsList:
                            if(forceString(z.value('lastName')) + ' ' + forceString(z.value('firstName')) \
                                        + ' ' + forceString(z.value('patrName')) == k):
                                if forceString(z.value('report_name')):
                                    if x == z.value('report_name'):
                                        cntReports.append(forceString(x))
                        for z in set(cntReports):
                            cnt += 1
                            i = table.addRow()
                            table.setText(i, 0, cnt)
                            table.setText(i, 1, forceString(z))
                            table.setText(i, 2, cntReports.count(x))
            else:
                query = selectDataWithDetails(begDate, endDate)
                self.setQueryText(forceString(query.lastQuery()))
                tableColumns = [
                    ('%5', [u"№"], CReportBase.AlignLeft),
                    ('%50', [u"Название отчета"], CReportBase.AlignLeft),
                    ('%50', [u"Дата формирования"], CReportBase.AlignLeft),
                    ('%30', [u"ЛПУ"], CReportBase.AlignLeft)
                ]
                table = createTable(cursor, tableColumns)
                cnt = 0
                reportsList = []
                lastNameList = []
                while query.next():
                    record = query.record()
                    lastNameList.append(forceString(record.value('lastName')) + ' ' + forceString(record.value('firstName')) \
                    + " " + forceString(record.value('patrName')))
                    reportsList.append(record)

                for k in set(lastNameList):
                    fio = forceString(k)
                    i = table.addRow()
                    table.setText(i, 1, u"Пользователь: " + fio)
                    for x in reportsList:
                        if forceString(x.value('report_name')):
                            if(forceString(x.value('lastName')) + ' ' + forceString(x.value('firstName')) \
                                       + ' ' + forceString(x.value('patrName')) == k):
                                cnt += 1
                                i = table.addRow()
                                table.setText(i, 0, cnt)
                                table.setText(i, 1, forceString(x.value('report_name')))
                                table.setText(i, 2, forceString(x.value('date')))
                                table.setText(i, 3, forceString(x.value('lpu')))
        else:
            query = selectData(begDate, endDate)
            self.setQueryText(forceString(query.lastQuery()))

            tableColumns = [
                ('%5', [u'№'], CReportBase.AlignLeft),
                ('%50', [u'Название отчета'], CReportBase.AlignLeft),
                ('%10', [u'Количество'], CReportBase.AlignLeft)
            ]
            table = createTable(cursor, tableColumns)
            cnt = 0
            reportsList = []
            while query.next():
                record = query.record()
                if forceString(record.value('report_name')):
                    reportsList.append(forceString(record.value('report_name')))
            for x in set(reportsList):
                cnt += 1
                i = table.addRow()
                table.setText(i, 0, cnt)
                table.setText(i, 1, forceString(x))
                table.setText(i, 2, reportsList.count(x))
        return doc

class CReportLogger(QtGui.QDialog, Ui_ReportFromLogger):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setParams(self, params):
        self.chkGroup.setChecked(params.get('chkGroup', False))
        self.chkPersonDetail.setChecked(params.get('chkDetails', False))
        self.edtBegDate.setDate(params.get('BegDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('EndDate', QtCore.QDate.currentDate()))

    def params(self):
        result= {}
        result['chkGroup'] = self.chkGroup.isChecked()
        result['chkDetails'] = self.chkPersonDetail.isChecked()
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        return result

    def setTitle(self, title):
        self.setWindowTitle(title)


    @QtCore.pyqtSlot(bool)
    def on_chkPersonDetail_toggled(self, value):
        self.chkGroup.setEnabled(self.chkPersonDetail.isChecked())