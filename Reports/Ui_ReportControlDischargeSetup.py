# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportControlDischargeSetup.ui'
#
# Created: Tue Jun  9 17:41:47 2015
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

class Ui_ReportControlDischargeSetup(object):
    def setupUi(self, ReportControlDischargeSetup):
        ReportControlDischargeSetup.setObjectName(_fromUtf8("ReportControlDischargeSetup"))
        ReportControlDischargeSetup.resize(398, 151)
        self.gridLayout = QtGui.QGridLayout(ReportControlDischargeSetup)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblEndDate = QtGui.QLabel(ReportControlDischargeSetup)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 2, 0, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportControlDischargeSetup)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportControlDischargeSetup)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 8, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 7, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 2, 1, 1)
        self.lblFinance = QtGui.QLabel(ReportControlDischargeSetup)
        self.lblFinance.setObjectName(_fromUtf8("lblFinance"))
        self.gridLayout.addWidget(self.lblFinance, 3, 0, 1, 1)
        self.cmbFinance = CRBComboBox(ReportControlDischargeSetup)
        self.cmbFinance.setObjectName(_fromUtf8("cmbFinance"))
        self.gridLayout.addWidget(self.cmbFinance, 3, 1, 1, 2)
        self.cmbOrgStructure = COrgStructureComboBox(ReportControlDischargeSetup)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 6, 1, 1, 2)
        self.lblOrgStructure = QtGui.QLabel(ReportControlDischargeSetup)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 6, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportControlDischargeSetup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 2, 1, 1, 1)
        self.edtBegDate = CDateEdit(ReportControlDischargeSetup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblBegDate.setBuddy(self.edtBegDate)

        self.retranslateUi(ReportControlDischargeSetup)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportControlDischargeSetup.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportControlDischargeSetup.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportControlDischargeSetup)

    def retranslateUi(self, ReportControlDischargeSetup):
        ReportControlDischargeSetup.setWindowTitle(_translate("ReportControlDischargeSetup", "Dialog", None))
        self.lblEndDate.setText(_translate("ReportControlDischargeSetup", "Дата &окончания периода", None))
        self.lblBegDate.setText(_translate("ReportControlDischargeSetup", "Дата &начала периода", None))
        self.lblFinance.setText(_translate("ReportControlDischargeSetup", "Тип финансирования", None))
        self.lblOrgStructure.setText(_translate("ReportControlDischargeSetup", "Подразделение", None))

from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from library.crbcombobox import CRBComboBox
