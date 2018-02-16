# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ExportPersons_VMPage1.ui'
#
# Created: Thu Nov 21 16:04:47 2013
#      by: PyQt4 UI code generator 4.10.3
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

class Ui_ExportPage1(object):
    def setupUi(self, ExportPage1):
        ExportPage1.setObjectName(_fromUtf8("ExportPage1"))
        ExportPage1.resize(928, 415)
        self.gridLayout = QtGui.QGridLayout(ExportPage1)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.btnExport = QtGui.QPushButton(ExportPage1)
        self.btnExport.setObjectName(_fromUtf8("btnExport"))
        self.horizontalLayout_2.addWidget(self.btnExport)
        self.btnCancel = QtGui.QPushButton(ExportPage1)
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.horizontalLayout_2.addWidget(self.btnCancel)
        self.gridLayout.addLayout(self.horizontalLayout_2, 6, 0, 1, 2)
        self.chkOnlyCurrentOrg = QtGui.QCheckBox(ExportPage1)
        self.chkOnlyCurrentOrg.setObjectName(_fromUtf8("chkOnlyCurrentOrg"))
        self.gridLayout.addWidget(self.chkOnlyCurrentOrg, 0, 0, 1, 1)
        self.progressBar = CProgressBar(ExportPage1)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 4, 0, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 5, 0, 1, 2)
        self.logBrowser = QtGui.QTextBrowser(ExportPage1)
        self.logBrowser.setObjectName(_fromUtf8("logBrowser"))
        self.gridLayout.addWidget(self.logBrowser, 3, 0, 1, 2)

        self.retranslateUi(ExportPage1)
        QtCore.QMetaObject.connectSlotsByName(ExportPage1)

    def retranslateUi(self, ExportPage1):
        ExportPage1.setWindowTitle(_translate("ExportPage1", "Form", None))
        self.btnExport.setText(_translate("ExportPage1", "экспорт", None))
        self.btnCancel.setText(_translate("ExportPage1", "прервать", None))
        self.chkOnlyCurrentOrg.setText(_translate("ExportPage1", "Выгружать только врачей текущей организации", None))

from library.ProgressBar import CProgressBar
