# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportF027VerificationSetupDialog.ui'
#
# Created: Wed Feb  3 15:17:08 2016
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

class Ui_ReportF027VerificationSetupDialog(object):
    def setupUi(self, ReportF027VerificationSetupDialog):
        ReportF027VerificationSetupDialog.setObjectName(_fromUtf8("ReportF027VerificationSetupDialog"))
        ReportF027VerificationSetupDialog.resize(445, 242)
        self.gridLayout = QtGui.QGridLayout(ReportF027VerificationSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBegDate = QtGui.QLabel(ReportF027VerificationSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = CDateEdit(ReportF027VerificationSetupDialog)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportF027VerificationSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportF027VerificationSetupDialog)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(ReportF027VerificationSetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 2, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportF027VerificationSetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 2, 1, 1, 1)
        self.lblEventType = QtGui.QLabel(ReportF027VerificationSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblEventType.sizePolicy().hasHeightForWidth())
        self.lblEventType.setSizePolicy(sizePolicy)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridLayout.addWidget(self.lblEventType, 3, 0, 1, 1)
        self.cmbEventType = CRBComboBox(ReportF027VerificationSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbEventType.sizePolicy().hasHeightForWidth())
        self.cmbEventType.setSizePolicy(sizePolicy)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 3, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportF027VerificationSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 2)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)
        self.lblEventType.setBuddy(self.cmbEventType)

        self.retranslateUi(ReportF027VerificationSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportF027VerificationSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportF027VerificationSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportF027VerificationSetupDialog)

    def retranslateUi(self, ReportF027VerificationSetupDialog):
        ReportF027VerificationSetupDialog.setWindowTitle(_translate("ReportF027VerificationSetupDialog", "Dialog", None))
        self.lblBegDate.setText(_translate("ReportF027VerificationSetupDialog", "Дата &начала периода", None))
        self.lblEndDate.setText(_translate("ReportF027VerificationSetupDialog", "Дата &окончания периода", None))
        self.lblOrgStructure.setText(_translate("ReportF027VerificationSetupDialog", "&Подразделение", None))
        self.lblEventType.setText(_translate("ReportF027VerificationSetupDialog", "&Тип события", None))

from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
