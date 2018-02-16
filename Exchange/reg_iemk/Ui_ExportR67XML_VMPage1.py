# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ExportR67XML_VMPage1.ui'
#
# Created: Mon Nov 11 17:07:59 2013
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
        self.progressBar = CProgressBar(ExportPage1)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 4, 0, 1, 1)
        self.logBrowser = QtGui.QTextBrowser(ExportPage1)
        self.logBrowser.setObjectName(_fromUtf8("logBrowser"))
        self.gridLayout.addWidget(self.logBrowser, 3, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lblStartDate = QtGui.QLabel(ExportPage1)
        self.lblStartDate.setObjectName(_fromUtf8("lblStartDate"))
        self.horizontalLayout.addWidget(self.lblStartDate)
        self.edtStartDate = CDateEdit(ExportPage1)
        self.edtStartDate.setObjectName(_fromUtf8("edtStartDate"))
        self.horizontalLayout.addWidget(self.edtStartDate)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.lblRecordsCount = QtGui.QLabel(ExportPage1)
        self.lblRecordsCount.setObjectName(_fromUtf8("lblRecordsCount"))
        self.horizontalLayout_3.addWidget(self.lblRecordsCount)
        self.edtRecordsCount = QtGui.QSpinBox(ExportPage1)
        self.edtRecordsCount.setObjectName(_fromUtf8("edtRecordsCount"))
        self.horizontalLayout_3.addWidget(self.edtRecordsCount)
        self.gridLayout.addLayout(self.horizontalLayout_3, 1, 0, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.btnExport = QtGui.QPushButton(ExportPage1)
        self.btnExport.setObjectName(_fromUtf8("btnExport"))
        self.horizontalLayout_2.addWidget(self.btnExport)
        self.btnCancel = QtGui.QPushButton(ExportPage1)
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.horizontalLayout_2.addWidget(self.btnCancel)
        self.gridLayout.addLayout(self.horizontalLayout_2, 6, 0, 1, 1)
        self.chkExportEvents = QtGui.QCheckBox(ExportPage1)
        self.chkExportEvents.setChecked(True)
        self.chkExportEvents.setObjectName(_fromUtf8("chkExportEvents"))
        self.gridLayout.addWidget(self.chkExportEvents, 2, 0, 1, 1)

        self.retranslateUi(ExportPage1)
        QtCore.QMetaObject.connectSlotsByName(ExportPage1)

    def retranslateUi(self, ExportPage1):
        ExportPage1.setWindowTitle(_translate("ExportPage1", "Form", None))
        self.lblStartDate.setText(_translate("ExportPage1", "Выгружать изменения после", None))
        self.lblRecordsCount.setText(_translate("ExportPage1", "Количество обрабатываемых записей", None))
        self.btnExport.setText(_translate("ExportPage1", "экспорт", None))
        self.btnCancel.setText(_translate("ExportPage1", "прервать", None))
        self.chkExportEvents.setText(_translate("ExportPage1", "Выгружать данные об обращениях", None))

from library.ProgressBar import CProgressBar
from library.DateEdit import CDateEdit
