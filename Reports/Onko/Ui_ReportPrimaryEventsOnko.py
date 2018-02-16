# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportPrimaryEventsOnko.ui'
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

class Ui_ReportPrimaryEventsOnkoSetupDialog(object):
    def setupUi(self, ReportPrimaryEventsOnkoSetupDialog):
        ReportPrimaryEventsOnkoSetupDialog.setObjectName(_fromUtf8("ReportPrimaryEventsOnkoSetupDialog"))
        ReportPrimaryEventsOnkoSetupDialog.resize(450, 250)
        self.gridLayout = QtGui.QGridLayout(ReportPrimaryEventsOnkoSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBegDate = QtGui.QLabel(ReportPrimaryEventsOnkoSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = CDateEdit(ReportPrimaryEventsOnkoSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportPrimaryEventsOnkoSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportPrimaryEventsOnkoSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(ReportPrimaryEventsOnkoSetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 2, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportPrimaryEventsOnkoSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 2, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportPrimaryEventsOnkoSetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 2, 1, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 3)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)

        self.retranslateUi(ReportPrimaryEventsOnkoSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportPrimaryEventsOnkoSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportPrimaryEventsOnkoSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportPrimaryEventsOnkoSetupDialog)
        ReportPrimaryEventsOnkoSetupDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportPrimaryEventsOnkoSetupDialog.setTabOrder(self.edtEndDate, self.cmbOrgStructure)
        ReportPrimaryEventsOnkoSetupDialog.setTabOrder(self.cmbOrgStructure, self.buttonBox)

    def retranslateUi(self, ReportPrimaryEventsOnkoSetupDialog):
        ReportPrimaryEventsOnkoSetupDialog.setWindowTitle(_translate("ReportPrimaryEventsOnkoSetupDialog", "Dialog", None))
        self.lblBegDate.setText(_translate("ReportPrimaryEventsOnkoSetupDialog", "Дата начала периода", None))
        self.edtBegDate.setDisplayFormat(_translate("ReportPrimaryEventsOnkoSetupDialog", "dd.MM.yyyy", None))
        self.lblEndDate.setText(_translate("ReportPrimaryEventsOnkoSetupDialog", "Дата окончания периода", None))
        self.edtEndDate.setDisplayFormat(_translate("ReportPrimaryEventsOnkoSetupDialog", "dd.MM.yyyy", None))
        self.lblOrgStructure.setText(_translate("ReportPrimaryEventsOnkoSetupDialog", "Подразделение", None))

from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from library.DateEdit import CDateEdit
