# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.Ui_ReportHospitalization_Krasnodar import Ui_ReportHospitalization_Krasnodar
from library.Utils import forceString, forceDate


def selectData(params):
    stmt = u'''
        SELECT COUNT(*) AS COUNT_ALL, e.`order` AS ord
        FROM Event e
        WHERE e.deleted = 0
        AND e.`order` <> 0
        AND DATE(e.setDate) >= DATE('%s')
        AND DATE(e.execDate) <= DATE('%s')
        GROUP BY e.order
    '''

    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())

    return db.query(stmt % (begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd')))

class CReportArchiveListSetupDialog(QtGui.QDialog, Ui_ReportHospitalization_Krasnodar):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        currentDate = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate(currentDate.year(), currentDate.month(), 1)))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate(currentDate.year(), currentDate.month(), currentDate.daysInMonth())))

    def params(self):
        return {
            'begDate': self.edtBegDate.date(),
            'endDate': self.edtEndDate.date()
        }


class CReportArchiveList(CReport):

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u"Отчёт по госпитализации")

    def getSetupDialog(self, parent):
        result = CReportArchiveListSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        doc = QtGui.QTextDocument()

        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('30%', [u'Порядок наступления'], CReportBase.AlignLeft),
            ('30%', [u'Количество'], CReportBase.AlignLeft)
        ]
        table = createTable(cursor, tableColumns)

        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))

        while query.next():
            record = query.record()
            i = table.addRow()
            if forceString(record.value('ord')) == '1':
                table.setText(i, 0, str('плановый').decode('utf8'))
            elif forceString(record.value('ord')) == '2':
                table.setText(i, 0, str('экстренный').decode('utf8'))
            elif forceString(record.value('ord')) == '3':
                table.setText(i, 0, str('самотёком').decode('utf8'))
            elif forceString(record.value('ord')) == '4':
                table.setText(i, 0, str('принудительный').decode('utf8'))
            elif forceString(record.value('ord')) == '5':
                table.setText(i, 0, str('неотложный').decode('utf8'))

            table.setText(i, 1, forceString(record.value('COUNT_ALL')))

        return doc


def main():
    import sys
    from library.database import connectDataBaseByInfo
    from s11main import CS11mainApp
    app = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtGui.qApp = app
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    QtGui.qApp.currentOrgId = lambda: 3147

    """
    connectionInfo = {'driverName' : 'mysql',
                      'host' : 'pes',
                      'port' : 3306,
                      'database' : 's12',
                      'user' : 'dbuser',
                      'password' : 'dbpassword',
                      'connectionName' : 'vista-med',
                      'compressData' : True,
                      'afterConnectFunc' : None}
    """
    connectionInfo = {'driverName' : 'mysql',
                  'host' : '192.168.0.207',
                  'port' : 3306,
                  'database' : 'olyu_sochi2',
                  'user' : 'dbuser',
                  'password' : 'dbpassword',
                  'connectionName' : 'vista-med',
                  'compressData' : True,
                  'afterConnectFunc' : None}

    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    CReportArchiveList(None).exec_()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()









