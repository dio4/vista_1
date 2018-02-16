# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ExportR51DDPage1.ui'
#
# Created: Fri Jun 15 12:16:36 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ExportR51DDPage1(object):
    def setupUi(self, ExportR51DDPage1):
        ExportR51DDPage1.setObjectName(_fromUtf8("ExportR51DDPage1"))
        ExportR51DDPage1.resize(435, 300)
        self.gridlayout = QtGui.QGridLayout(ExportR51DDPage1)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 0, 0, 1, 3)
        self.progressBar = CProgressBar(ExportR51DDPage1)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridlayout.addWidget(self.progressBar, 5, 0, 1, 3)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem1, 6, 0, 1, 3)
        self.btnExport = QtGui.QPushButton(ExportR51DDPage1)
        self.btnExport.setObjectName(_fromUtf8("btnExport"))
        self.gridlayout.addWidget(self.btnExport, 7, 1, 1, 1)
        self.btnCancel = QtGui.QPushButton(ExportR51DDPage1)
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.gridlayout.addWidget(self.btnCancel, 7, 2, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem2, 7, 0, 1, 1)
        self.logBrowser = QtGui.QTextBrowser(ExportR51DDPage1)
        self.logBrowser.setObjectName(_fromUtf8("logBrowser"))
        self.gridlayout.addWidget(self.logBrowser, 4, 0, 1, 3)
        self.chkVerboseLog = QtGui.QCheckBox(ExportR51DDPage1)
        self.chkVerboseLog.setObjectName(_fromUtf8("chkVerboseLog"))
        self.gridlayout.addWidget(self.chkVerboseLog, 2, 0, 1, 1)
        self.chkIgnoreErrors = QtGui.QCheckBox(ExportR51DDPage1)
        self.chkIgnoreErrors.setEnabled(False)
        self.chkIgnoreErrors.setObjectName(_fromUtf8("chkIgnoreErrors"))
        self.gridlayout.addWidget(self.chkIgnoreErrors, 3, 0, 1, 1)
        self.chkMarkFirstForMKBZ00 = QtGui.QCheckBox(ExportR51DDPage1)
        self.chkMarkFirstForMKBZ00.setChecked(True)
        self.chkMarkFirstForMKBZ00.setObjectName(_fromUtf8("chkMarkFirstForMKBZ00"))
        self.gridlayout.addWidget(self.chkMarkFirstForMKBZ00, 1, 0, 1, 3)

        self.retranslateUi(ExportR51DDPage1)
        QtCore.QMetaObject.connectSlotsByName(ExportR51DDPage1)

    def retranslateUi(self, ExportR51DDPage1):
        ExportR51DDPage1.setWindowTitle(QtGui.QApplication.translate("ExportR51DDPage1", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.btnExport.setText(QtGui.QApplication.translate("ExportR51DDPage1", "экспорт", None, QtGui.QApplication.UnicodeUTF8))
        self.btnCancel.setText(QtGui.QApplication.translate("ExportR51DDPage1", "прервать", None, QtGui.QApplication.UnicodeUTF8))
        self.chkVerboseLog.setText(QtGui.QApplication.translate("ExportR51DDPage1", "Подробный отчет", None, QtGui.QApplication.UnicodeUTF8))
        self.chkIgnoreErrors.setText(QtGui.QApplication.translate("ExportR51DDPage1", "Игнорировать ошибки", None, QtGui.QApplication.UnicodeUTF8))
        self.chkMarkFirstForMKBZ00.setText(QtGui.QApplication.translate("ExportR51DDPage1", "Считать характер для обстоятельств обращения как ранее известный", None, QtGui.QApplication.UnicodeUTF8))

from library.ProgressBar import CProgressBar

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ExportR51DDPage1 = QtGui.QWidget()
    ui = Ui_ExportR51DDPage1()
    ui.setupUi(ExportR51DDPage1)
    ExportR51DDPage1.show()
    sys.exit(app.exec_())

