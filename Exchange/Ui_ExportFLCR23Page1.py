# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ExportFLCR23Page1.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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

class Ui_ExportFLCR23Page1(object):
    def setupUi(self, ExportFLCR23Page1):
        ExportFLCR23Page1.setObjectName(_fromUtf8("ExportFLCR23Page1"))
        ExportFLCR23Page1.resize(500, 350)
        self.gridLayout = QtGui.QGridLayout(ExportFLCR23Page1)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblOrgCode = QtGui.QLabel(ExportFLCR23Page1)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblOrgCode.sizePolicy().hasHeightForWidth())
        self.lblOrgCode.setSizePolicy(sizePolicy)
        self.lblOrgCode.setObjectName(_fromUtf8("lblOrgCode"))
        self.gridLayout.addWidget(self.lblOrgCode, 1, 0, 1, 1)
        self.edtOrgCode = QtGui.QLineEdit(ExportFLCR23Page1)
        self.edtOrgCode.setInputMask(_fromUtf8(""))
        self.edtOrgCode.setObjectName(_fromUtf8("edtOrgCode"))
        self.gridLayout.addWidget(self.edtOrgCode, 1, 1, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(ExportFLCR23Page1)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 2, 0, 1, 1)
        self.lblPeriod = QtGui.QLabel(ExportFLCR23Page1)
        self.lblPeriod.setObjectName(_fromUtf8("lblPeriod"))
        self.gridLayout.addWidget(self.lblPeriod, 3, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lblBegDate = QtGui.QLabel(ExportFLCR23Page1)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.horizontalLayout.addWidget(self.lblBegDate)
        self.edtBegDate = CDateEdit(ExportFLCR23Page1)
        self.edtBegDate.setCalendarPopup(False)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.horizontalLayout.addWidget(self.edtBegDate)
        self.lblEndDate = QtGui.QLabel(ExportFLCR23Page1)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.horizontalLayout.addWidget(self.lblEndDate)
        self.edtEndDate = CDateEdit(ExportFLCR23Page1)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.horizontalLayout.addWidget(self.edtEndDate)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.gridLayout.addLayout(self.horizontalLayout, 3, 1, 1, 2)
        self.logBrowser = QtGui.QTextBrowser(ExportFLCR23Page1)
        self.logBrowser.setObjectName(_fromUtf8("logBrowser"))
        self.gridLayout.addWidget(self.logBrowser, 4, 0, 1, 3)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.btnExport = QtGui.QPushButton(ExportFLCR23Page1)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnExport.sizePolicy().hasHeightForWidth())
        self.btnExport.setSizePolicy(sizePolicy)
        self.btnExport.setObjectName(_fromUtf8("btnExport"))
        self.horizontalLayout_2.addWidget(self.btnExport)
        self.btnCancel = QtGui.QPushButton(ExportFLCR23Page1)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnCancel.sizePolicy().hasHeightForWidth())
        self.btnCancel.setSizePolicy(sizePolicy)
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.horizontalLayout_2.addWidget(self.btnCancel)
        self.gridLayout.addLayout(self.horizontalLayout_2, 5, 0, 1, 3)
        self.progressBar = CProgressBar(ExportFLCR23Page1)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 0, 0, 1, 3)
        self.cmbOrgStructure = COrgStructureComboBox(ExportFLCR23Page1)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 2, 1, 1, 2)

        self.retranslateUi(ExportFLCR23Page1)
        QtCore.QMetaObject.connectSlotsByName(ExportFLCR23Page1)

    def retranslateUi(self, ExportFLCR23Page1):
        ExportFLCR23Page1.setWindowTitle(_translate("ExportFLCR23Page1", "Form", None))
        self.lblOrgCode.setText(_translate("ExportFLCR23Page1", "Код ЛПУ", None))
        self.lblOrgStructure.setText(_translate("ExportFLCR23Page1", "Подразделение", None))
        self.lblPeriod.setText(_translate("ExportFLCR23Page1", "Период", None))
        self.lblBegDate.setText(_translate("ExportFLCR23Page1", "с", None))
        self.lblEndDate.setText(_translate("ExportFLCR23Page1", "по", None))
        self.btnExport.setText(_translate("ExportFLCR23Page1", "экспорт", None))
        self.btnCancel.setText(_translate("ExportFLCR23Page1", "прервать", None))

from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from library.DateEdit import CDateEdit
from library.ProgressBar import CProgressBar
