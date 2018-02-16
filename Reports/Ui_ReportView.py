# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './Reports/ReportView.ui'
#
# Created: Tue Aug  7 16:08:45 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ReportViewDialog(object):
    def setupUi(self, ReportViewDialog):
        ReportViewDialog.setObjectName(_fromUtf8("ReportViewDialog"))
        ReportViewDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportViewDialog.resize(554, 470)
        ReportViewDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(ReportViewDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.txtReport = CReportBrowser(ReportViewDialog)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("MS Shell Dlg 2"))
        font.setPointSize(10)
        self.txtReport.setFont(font)
        self.txtReport.setObjectName(_fromUtf8("txtReport"))
        self.gridlayout.addWidget(self.txtReport, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportViewDialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Retry|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(ReportViewDialog)
        QtCore.QMetaObject.connectSlotsByName(ReportViewDialog)

    def retranslateUi(self, ReportViewDialog):
        ReportViewDialog.setWindowTitle(QtGui.QApplication.translate("ReportViewDialog", "просмотр отчёта", None, QtGui.QApplication.UnicodeUTF8))

from ReportBrowser import CReportBrowser
