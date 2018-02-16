# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportInvalidMKBEventsListSetup.ui'
#
# Created: Fri Feb 13 17:35:30 2015
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

class Ui_ReportInvalidMKBEventsListSetup(object):
    def setupUi(self, ReportInvalidMKBEventsListSetup):
        ReportInvalidMKBEventsListSetup.setObjectName(_fromUtf8("ReportInvalidMKBEventsListSetup"))
        ReportInvalidMKBEventsListSetup.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportInvalidMKBEventsListSetup.resize(436, 156)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ReportInvalidMKBEventsListSetup.sizePolicy().hasHeightForWidth())
        ReportInvalidMKBEventsListSetup.setSizePolicy(sizePolicy)
        ReportInvalidMKBEventsListSetup.setSizeGripEnabled(True)
        ReportInvalidMKBEventsListSetup.setModal(True)
        self.gridLayout = QtGui.QGridLayout(ReportInvalidMKBEventsListSetup)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBegDate = QtGui.QLabel(ReportInvalidMKBEventsListSetup)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportInvalidMKBEventsListSetup)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 5, 1, 1, 5)
        self.lblEndDate = QtGui.QLabel(ReportInvalidMKBEventsListSetup)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(61, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 3, 1, 3)
        self.buttonBox = QtGui.QDialogButtonBox(ReportInvalidMKBEventsListSetup)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 8, 0, 1, 6)
        spacerItem1 = QtGui.QSpacerItem(428, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 7, 0, 1, 6)
        self.lblOrgStructure = QtGui.QLabel(ReportInvalidMKBEventsListSetup)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 5, 0, 1, 1)
        self.lblFinance = QtGui.QLabel(ReportInvalidMKBEventsListSetup)
        self.lblFinance.setObjectName(_fromUtf8("lblFinance"))
        self.gridLayout.addWidget(self.lblFinance, 6, 0, 1, 1)
        self.edtBegDate = CDateEdit(ReportInvalidMKBEventsListSetup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 2)
        self.edtEndDate = CDateEdit(ReportInvalidMKBEventsListSetup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 2)
        spacerItem2 = QtGui.QSpacerItem(61, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 1, 3, 1, 3)
        self.cmbFinance = CRBComboBox(ReportInvalidMKBEventsListSetup)
        self.cmbFinance.setObjectName(_fromUtf8("cmbFinance"))
        self.gridLayout.addWidget(self.cmbFinance, 6, 1, 1, 5)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)

        self.retranslateUi(ReportInvalidMKBEventsListSetup)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportInvalidMKBEventsListSetup.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportInvalidMKBEventsListSetup.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportInvalidMKBEventsListSetup)
        ReportInvalidMKBEventsListSetup.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportInvalidMKBEventsListSetup.setTabOrder(self.edtEndDate, self.cmbOrgStructure)
        ReportInvalidMKBEventsListSetup.setTabOrder(self.cmbOrgStructure, self.cmbFinance)
        ReportInvalidMKBEventsListSetup.setTabOrder(self.cmbFinance, self.buttonBox)

    def retranslateUi(self, ReportInvalidMKBEventsListSetup):
        ReportInvalidMKBEventsListSetup.setWindowTitle(_translate("ReportInvalidMKBEventsListSetup", "параметры отчёта", None))
        self.lblBegDate.setText(_translate("ReportInvalidMKBEventsListSetup", "Дата &начала периода", None))
        self.lblEndDate.setText(_translate("ReportInvalidMKBEventsListSetup", "Дата &окончания периода", None))
        self.lblOrgStructure.setText(_translate("ReportInvalidMKBEventsListSetup", "Подразделение", None))
        self.lblFinance.setText(_translate("ReportInvalidMKBEventsListSetup", "Тип финанисирования", None))

from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
