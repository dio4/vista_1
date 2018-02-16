# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportControlEventResultSetup.ui'
#
# Created: Thu May 07 16:42:11 2015
#      by: PyQt4 UI code generator 4.11.3
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

class Ui_ReportControlEventResultSetup(object):
    def setupUi(self, ReportControlEventResultSetup):
        ReportControlEventResultSetup.setObjectName(_fromUtf8("ReportControlEventResultSetup"))
        ReportControlEventResultSetup.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportControlEventResultSetup.resize(436, 156)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ReportControlEventResultSetup.sizePolicy().hasHeightForWidth())
        ReportControlEventResultSetup.setSizePolicy(sizePolicy)
        ReportControlEventResultSetup.setSizeGripEnabled(True)
        ReportControlEventResultSetup.setModal(True)
        self.gridLayout = QtGui.QGridLayout(ReportControlEventResultSetup)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        spacerItem = QtGui.QSpacerItem(428, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 9, 0, 1, 6)
        self.buttonBox = QtGui.QDialogButtonBox(ReportControlEventResultSetup)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 10, 0, 1, 6)
        self.cmbOrgStructure = COrgStructureComboBox(ReportControlEventResultSetup)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 7, 1, 1, 5)
        self.lblEndDate = QtGui.QLabel(ReportControlEventResultSetup)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 3, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(61, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 3, 1, 3)
        self.lblOrgStructure = QtGui.QLabel(ReportControlEventResultSetup)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 7, 0, 1, 1)
        self.lblFinance = QtGui.QLabel(ReportControlEventResultSetup)
        self.lblFinance.setObjectName(_fromUtf8("lblFinance"))
        self.gridLayout.addWidget(self.lblFinance, 8, 0, 1, 1)
        self.edtBegDate = CDateEdit(ReportControlEventResultSetup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 1, 1, 1, 2)
        self.edtEndDate = CDateEdit(ReportControlEventResultSetup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 3, 1, 1, 2)
        spacerItem2 = QtGui.QSpacerItem(61, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 3, 3, 1, 3)
        self.cmbFinance = CRBComboBox(ReportControlEventResultSetup)
        self.cmbFinance.setObjectName(_fromUtf8("cmbFinance"))
        self.gridLayout.addWidget(self.cmbFinance, 8, 1, 1, 5)
        self.lblBegDate = QtGui.QLabel(ReportControlEventResultSetup)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 1, 0, 1, 1)
        self.lblBegDate_2 = QtGui.QLabel(ReportControlEventResultSetup)
        self.lblBegDate_2.setObjectName(_fromUtf8("lblBegDate_2"))
        self.gridLayout.addWidget(self.lblBegDate_2, 0, 0, 1, 1)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblBegDate_2.setBuddy(self.edtBegDate)

        self.retranslateUi(ReportControlEventResultSetup)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportControlEventResultSetup.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportControlEventResultSetup.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportControlEventResultSetup)
        ReportControlEventResultSetup.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportControlEventResultSetup.setTabOrder(self.edtEndDate, self.cmbOrgStructure)
        ReportControlEventResultSetup.setTabOrder(self.cmbOrgStructure, self.cmbFinance)
        ReportControlEventResultSetup.setTabOrder(self.cmbFinance, self.buttonBox)

    def retranslateUi(self, ReportControlEventResultSetup):
        ReportControlEventResultSetup.setWindowTitle(_translate("ReportControlEventResultSetup", "параметры отчёта", None))
        self.lblEndDate.setText(_translate("ReportControlEventResultSetup", "по", None))
        self.lblOrgStructure.setText(_translate("ReportControlEventResultSetup", "Подразделение", None))
        self.lblFinance.setText(_translate("ReportControlEventResultSetup", "Тип финанисирования", None))
        self.lblBegDate.setText(_translate("ReportControlEventResultSetup", "с", None))
        self.lblBegDate_2.setText(_translate("ReportControlEventResultSetup", "Дата окончания лечения:", None))

from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
