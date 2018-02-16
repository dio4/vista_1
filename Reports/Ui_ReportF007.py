# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportF007.ui'
#
# Created: Wed May 20 13:54:17 2015
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

class Ui_ReportF007(object):
    def setupUi(self, ReportF007):
        ReportF007.setObjectName(_fromUtf8("ReportF007"))
        ReportF007.resize(690, 191)
        self.gridLayout = QtGui.QGridLayout(ReportF007)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblEndDate = QtGui.QLabel(ReportF007)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportF007)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 4, 1, 1)
        self.edtBegTime = QtGui.QTimeEdit(ReportF007)
        self.edtBegTime.setObjectName(_fromUtf8("edtBegTime"))
        self.gridLayout.addWidget(self.edtBegTime, 0, 3, 1, 1)
        self.label = QtGui.QLabel(ReportF007)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 2, 1, 1)
        self.edtBegDate = CDateEdit(ReportF007)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportF007)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(ReportF007)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 2, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportF007)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 7, 3, 1, 2)
        self.cmbOrgStructure = COrgStructureComboBox(ReportF007)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 2, 1, 1, 4)
        self.lblReportType = QtGui.QLabel(ReportF007)
        self.lblReportType.setObjectName(_fromUtf8("lblReportType"))
        self.gridLayout.addWidget(self.lblReportType, 4, 0, 1, 1)
        self.cmbReportType = QtGui.QComboBox(ReportF007)
        self.cmbReportType.setObjectName(_fromUtf8("cmbReportType"))
        self.cmbReportType.addItem(_fromUtf8(""))
        self.cmbReportType.addItem(_fromUtf8(""))
        self.cmbReportType.addItem(_fromUtf8(""))
        self.cmbReportType.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbReportType, 4, 1, 1, 4)
        self.chkOAR = QtGui.QCheckBox(ReportF007)
        self.chkOAR.setObjectName(_fromUtf8("chkOAR"))
        self.gridLayout.addWidget(self.chkOAR, 5, 0, 1, 3)
        self.chkUngroupFinance = QtGui.QCheckBox(ReportF007)
        self.chkUngroupFinance.setEnabled(False)
        self.chkUngroupFinance.setObjectName(_fromUtf8("chkUngroupFinance"))
        self.gridLayout.addWidget(self.chkUngroupFinance, 6, 0, 1, 4)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblBegDate.setBuddy(self.edtBegDate)

        self.retranslateUi(ReportF007)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportF007.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportF007.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportF007)

    def retranslateUi(self, ReportF007):
        ReportF007.setWindowTitle(_translate("ReportF007", "Dialog", None))
        self.lblEndDate.setText(_translate("ReportF007", "Дата &окончания периода", None))
        self.edtBegTime.setDisplayFormat(_translate("ReportF007", "HH:mm", None))
        self.label.setText(_translate("ReportF007", "Время начала суток", None))
        self.lblBegDate.setText(_translate("ReportF007", "Дата &начала периода", None))
        self.lblOrgStructure.setText(_translate("ReportF007", "Подразделение", None))
        self.lblReportType.setText(_translate("ReportF007", "Вид отчета", None))
        self.cmbReportType.setItemText(0, _translate("ReportF007", "Сводка для ОНКО 2", None))
        self.cmbReportType.setItemText(1, _translate("ReportF007", "Сводка для НИИ Петрова", None))
        self.cmbReportType.setItemText(2, _translate("ReportF007", "Сводка для Москвы", None))
        self.cmbReportType.setItemText(3, _translate("ReportF007", "Сводка для Краснодарского края", None))
        self.chkOAR.setText(_translate("ReportF007", "включить Отделение анестезиологии-реанимации", None))
        self.chkUngroupFinance.setText(_translate("ReportF007", "не группировать по каналам финансирования", None))

from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
