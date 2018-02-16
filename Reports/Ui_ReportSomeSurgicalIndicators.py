# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportSomeSurgicalIndicators.ui'
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

class Ui_ReportSurgicalIndicators(object):
    def setupUi(self, ReportSurgicalIndicators):
        ReportSurgicalIndicators.setObjectName(_fromUtf8("ReportSurgicalIndicators"))
        ReportSurgicalIndicators.resize(498, 322)
        self.gridLayout = QtGui.QGridLayout(ReportSurgicalIndicators)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 7, 0, 1, 1)
        self.lstOrgStructure = CRBListBox(ReportSurgicalIndicators)
        self.lstOrgStructure.setObjectName(_fromUtf8("lstOrgStructure"))
        self.gridLayout.addWidget(self.lstOrgStructure, 5, 0, 1, 4)
        self.cmbOrgStructure = COrgStructureComboBox(ReportSurgicalIndicators)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 4, 2, 1, 2)
        self.chkOrgStructure = QtGui.QCheckBox(ReportSurgicalIndicators)
        self.chkOrgStructure.setObjectName(_fromUtf8("chkOrgStructure"))
        self.gridLayout.addWidget(self.chkOrgStructure, 4, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 3, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportSurgicalIndicators)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 2)
        self.lblEndDate = QtGui.QLabel(ReportSurgicalIndicators)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ReportSurgicalIndicators)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 8, 0, 1, 4)
        self.edtBegDate = CDateEdit(ReportSurgicalIndicators)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 2, 1, 1)
        self.edtEndDate = CDateEdit(ReportSurgicalIndicators)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 2, 1, 1)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)

        self.retranslateUi(ReportSurgicalIndicators)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportSurgicalIndicators.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportSurgicalIndicators.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportSurgicalIndicators)

    def retranslateUi(self, ReportSurgicalIndicators):
        ReportSurgicalIndicators.setWindowTitle(_translate("ReportSurgicalIndicators", "Dialog", None))
        self.chkOrgStructure.setText(_translate("ReportSurgicalIndicators", "Подразделение", None))
        self.lblBegDate.setText(_translate("ReportSurgicalIndicators", "Дата &начала периода", None))
        self.lblEndDate.setText(_translate("ReportSurgicalIndicators", "Дата &окончания периода", None))

from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from library.DateEdit import CDateEdit
from library.RBListBox import CRBListBox
