# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ExportAttachClientPage1.ui'
#
# Created: Thu Mar 26 17:22:38 2015
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_ExportAttachClientPage1(object):
    def setupUi(self, ExportAttachClientPage1):
        ExportAttachClientPage1.setObjectName(_fromUtf8("ExportAttachClientPage1"))
        ExportAttachClientPage1.resize(400, 368)
        self.gridLayout = QtGui.QGridLayout(ExportAttachClientPage1)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.progressBar = CProgressBar(ExportAttachClientPage1)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 7, 0, 1, 4)
        self.logBrowser = QtGui.QTextBrowser(ExportAttachClientPage1)
        self.logBrowser.setObjectName(_fromUtf8("logBrowser"))
        self.gridLayout.addWidget(self.logBrowser, 8, 0, 1, 4)
        self.lblDate = QtGui.QLabel(ExportAttachClientPage1)
        self.lblDate.setObjectName(_fromUtf8("lblDate"))
        self.gridLayout.addWidget(self.lblDate, 0, 0, 1, 1)
        self.lblInsurer = QtGui.QLabel(ExportAttachClientPage1)
        self.lblInsurer.setObjectName(_fromUtf8("lblInsurer"))
        self.gridLayout.addWidget(self.lblInsurer, 2, 0, 1, 1)
        self.edtDate = CDateEdit(ExportAttachClientPage1)
        self.edtDate.setEnabled(True)
        self.edtDate.setCalendarPopup(True)
        self.edtDate.setObjectName(_fromUtf8("edtDate"))
        self.gridLayout.addWidget(self.edtDate, 0, 1, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(ExportAttachClientPage1)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 5, 0, 1, 1)
        self.cmbInsurer = CInsurerComboBox(ExportAttachClientPage1)
        self.cmbInsurer.setObjectName(_fromUtf8("cmbInsurer"))
        self.gridLayout.addWidget(self.cmbInsurer, 2, 1, 1, 3)
        self.btnCancel = QtGui.QPushButton(ExportAttachClientPage1)
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.gridLayout.addWidget(self.btnCancel, 9, 3, 1, 1)
        self.btnExport = QtGui.QPushButton(ExportAttachClientPage1)
        self.btnExport.setObjectName(_fromUtf8("btnExport"))
        self.gridLayout.addWidget(self.btnExport, 9, 2, 1, 1)
        self.lstOrgStructure = CRBListBox(ExportAttachClientPage1)
        self.lstOrgStructure.setObjectName(_fromUtf8("lstOrgStructure"))
        self.gridLayout.addWidget(self.lstOrgStructure, 5, 1, 1, 3)

        self.retranslateUi(ExportAttachClientPage1)
        QtCore.QMetaObject.connectSlotsByName(ExportAttachClientPage1)

    def retranslateUi(self, ExportAttachClientPage1):
        ExportAttachClientPage1.setWindowTitle(_translate("ExportAttachClientPage1", "Dialog", None))
        self.lblDate.setText(_translate("ExportAttachClientPage1", "Дата", None))
        self.lblInsurer.setText(_translate("ExportAttachClientPage1", "Плательщик", None))
        self.lblOrgStructure.setText(_translate("ExportAttachClientPage1", "Подразделение", None))
        self.btnCancel.setText(_translate("ExportAttachClientPage1", "прервать", None))
        self.btnExport.setText(_translate("ExportAttachClientPage1", "экспорт", None))

from Orgs.OrgComboBox import CInsurerComboBox
from library.RBListBox import CRBListBox
from library.ProgressBar import CProgressBar
from library.DateEdit import CDateEdit
