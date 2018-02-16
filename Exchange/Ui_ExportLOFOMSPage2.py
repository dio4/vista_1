# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ExportLOFOMSPage2.ui'
#
# Created: Fri Jun 15 12:16:12 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ExportLOFOMSPage2(object):
    def setupUi(self, ExportLOFOMSPage2):
        ExportLOFOMSPage2.setObjectName(_fromUtf8("ExportLOFOMSPage2"))
        ExportLOFOMSPage2.resize(400, 300)
        self.gridlayout = QtGui.QGridLayout(ExportLOFOMSPage2)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 0, 0, 1, 3)
        self.progressBar = CProgressBar(ExportLOFOMSPage2)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridlayout.addWidget(self.progressBar, 4, 0, 1, 3)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem1, 5, 0, 1, 3)
        self.btnExport = QtGui.QPushButton(ExportLOFOMSPage2)
        self.btnExport.setObjectName(_fromUtf8("btnExport"))
        self.gridlayout.addWidget(self.btnExport, 6, 1, 1, 1)
        self.btnCancel = QtGui.QPushButton(ExportLOFOMSPage2)
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.gridlayout.addWidget(self.btnCancel, 6, 2, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem2, 6, 0, 1, 1)
        self.logBrowser = QtGui.QTextBrowser(ExportLOFOMSPage2)
        self.logBrowser.setObjectName(_fromUtf8("logBrowser"))
        self.gridlayout.addWidget(self.logBrowser, 3, 0, 1, 3)
        self.chkVerboseLog = QtGui.QCheckBox(ExportLOFOMSPage2)
        self.chkVerboseLog.setObjectName(_fromUtf8("chkVerboseLog"))
        self.gridlayout.addWidget(self.chkVerboseLog, 1, 0, 1, 1)
        self.chkIgnoreErrors = QtGui.QCheckBox(ExportLOFOMSPage2)
        self.chkIgnoreErrors.setObjectName(_fromUtf8("chkIgnoreErrors"))
        self.gridlayout.addWidget(self.chkIgnoreErrors, 2, 0, 1, 1)

        self.retranslateUi(ExportLOFOMSPage2)
        QtCore.QMetaObject.connectSlotsByName(ExportLOFOMSPage2)

    def retranslateUi(self, ExportLOFOMSPage2):
        ExportLOFOMSPage2.setWindowTitle(QtGui.QApplication.translate("ExportLOFOMSPage2", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.btnExport.setText(QtGui.QApplication.translate("ExportLOFOMSPage2", "экспорт", None, QtGui.QApplication.UnicodeUTF8))
        self.btnCancel.setText(QtGui.QApplication.translate("ExportLOFOMSPage2", "прервать", None, QtGui.QApplication.UnicodeUTF8))
        self.chkVerboseLog.setText(QtGui.QApplication.translate("ExportLOFOMSPage2", "Подробный отчет", None, QtGui.QApplication.UnicodeUTF8))
        self.chkIgnoreErrors.setText(QtGui.QApplication.translate("ExportLOFOMSPage2", "Игнорировать ошибки", None, QtGui.QApplication.UnicodeUTF8))

from library.ProgressBar import CProgressBar

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ExportLOFOMSPage2 = QtGui.QWidget()
    ui = Ui_ExportLOFOMSPage2()
    ui.setupUi(ExportLOFOMSPage2)
    ExportLOFOMSPage2.show()
    sys.exit(app.exec_())

