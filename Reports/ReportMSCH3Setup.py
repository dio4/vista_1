# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Events.Utils import getWorkEventTypeFilter
from Reports.Ui_ReportMSCH3Setup import Ui_ReportMSCH3SetupDialog
from library.Utils import getVal


class CReportMSCH3SetupDialog(QtGui.QDialog, Ui_ReportMSCH3SetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.lstEventTypes.setTable('EventType', filter=getWorkEventTypeFilter())

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(getVal(params, 'begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(getVal(params, 'endDate', QtCore.QDate.currentDate()))
        self.chkIsWorker.setChecked(getVal(params, 'isWorker', False))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['eventTypes'] = self.lstEventTypes.nameValues()
        result['isWorker'] = self.chkIsWorker.isChecked()

        return result


# def main():
#     import sys
#     from s11main import CS11mainApp
#     from library.database import connectDataBaseByInfo
#
#     QtGui.qApp = CS11mainApp(sys.argv, False, 'S11App.ini', False)
#     QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))
#
#     connectionInfo = {
#         'driverName': 'mysql',
#         'host': 'msch3',
#         'port': 3306,
#         'database': 's11',
#         'user': 'dbuser',
#         'password': 'dbpassword',
#         'connectionName': 'vista-med',
#         'compressData': True,
#         'afterConnectFunc': None
#     }
#     QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)
#
#     w = CReportMSCH3SetupDialog(None)
#     w.exec_()
#
#
# if __name__ == '__main__':
#     main()
