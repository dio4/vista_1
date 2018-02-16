# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ExportR51StomatologyProcessPage.ui'
#
# Created: Wed Apr 17 10:25:03 2013
#      by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_ExportR51StomatologyProcessPage(object):
    def setupUi(self, ExportR51StomatologyProcessPage):
        ExportR51StomatologyProcessPage.setObjectName(_fromUtf8("ExportR51StomatologyProcessPage"))
        ExportR51StomatologyProcessPage.resize(400, 300)
        self.gridlayout = QtGui.QGridLayout(ExportR51StomatologyProcessPage)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 0, 0, 1, 3)
        self.progressBar = CProgressBar(ExportR51StomatologyProcessPage)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridlayout.addWidget(self.progressBar, 4, 0, 1, 3)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem1, 5, 0, 1, 3)
        self.btnExport = QtGui.QPushButton(ExportR51StomatologyProcessPage)
        self.btnExport.setObjectName(_fromUtf8("btnExport"))
        self.gridlayout.addWidget(self.btnExport, 6, 1, 1, 1)
        self.btnCancel = QtGui.QPushButton(ExportR51StomatologyProcessPage)
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.gridlayout.addWidget(self.btnCancel, 6, 2, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem2, 6, 0, 1, 1)
        self.logBrowser = QtGui.QTextBrowser(ExportR51StomatologyProcessPage)
        self.logBrowser.setObjectName(_fromUtf8("logBrowser"))
        self.gridlayout.addWidget(self.logBrowser, 3, 0, 1, 3)
        self.chkVerboseLog = QtGui.QCheckBox(ExportR51StomatologyProcessPage)
        self.chkVerboseLog.setObjectName(_fromUtf8("chkVerboseLog"))
        self.gridlayout.addWidget(self.chkVerboseLog, 1, 0, 1, 1)
        self.chkIgnoreErrors = QtGui.QCheckBox(ExportR51StomatologyProcessPage)
        self.chkIgnoreErrors.setObjectName(_fromUtf8("chkIgnoreErrors"))
        self.gridlayout.addWidget(self.chkIgnoreErrors, 2, 0, 1, 1)

        self.retranslateUi(ExportR51StomatologyProcessPage)
        QtCore.QMetaObject.connectSlotsByName(ExportR51StomatologyProcessPage)

    def retranslateUi(self, ExportR51StomatologyProcessPage):
        ExportR51StomatologyProcessPage.setWindowTitle(_translate("ExportR51StomatologyProcessPage", "Form", None))
        self.btnExport.setText(_translate("ExportR51StomatologyProcessPage", "экспорт", None))
        self.btnCancel.setText(_translate("ExportR51StomatologyProcessPage", "прервать", None))
        self.chkVerboseLog.setText(_translate("ExportR51StomatologyProcessPage", "Подробный отчет", None))
        self.chkIgnoreErrors.setText(_translate("ExportR51StomatologyProcessPage", "Игнорировать ошибки", None))

from library.ProgressBar import CProgressBar
