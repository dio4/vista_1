# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PatientEntranceSetup.ui'
#
# Created: Tue Feb 17 18:04:30 2015
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

class Ui_PatientEntranceSetupDialog(object):
    def setupUi(self, PatientEntranceSetupDialog):
        PatientEntranceSetupDialog.setObjectName(_fromUtf8("PatientEntranceSetupDialog"))
        PatientEntranceSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        PatientEntranceSetupDialog.resize(438, 159)
        PatientEntranceSetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(PatientEntranceSetupDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.cmbOrgStructure = COrgStructureComboBox(PatientEntranceSetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 2, 1, 1, 3)
        self.buttonBox = QtGui.QDialogButtonBox(PatientEntranceSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 4)
        self.lblOrgStructure = QtGui.QLabel(PatientEntranceSetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 2, 0, 1, 1)
        self.edtBegDate = CDateEdit(PatientEntranceSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.lblBegDate = QtGui.QLabel(PatientEntranceSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtEndDate = CDateEdit(PatientEntranceSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        self.lblEndDate = QtGui.QLabel(PatientEntranceSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.edtEndTime = QtGui.QTimeEdit(PatientEntranceSetupDialog)
        self.edtEndTime.setObjectName(_fromUtf8("edtEndTime"))
        self.gridLayout.addWidget(self.edtEndTime, 1, 2, 1, 1)
        self.edtBegTime = QtGui.QTimeEdit(PatientEntranceSetupDialog)
        self.edtBegTime.setObjectName(_fromUtf8("edtBegTime"))
        self.gridLayout.addWidget(self.edtBegTime, 0, 2, 1, 1)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)

        self.retranslateUi(PatientEntranceSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), PatientEntranceSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), PatientEntranceSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PatientEntranceSetupDialog)
        PatientEntranceSetupDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        PatientEntranceSetupDialog.setTabOrder(self.edtEndDate, self.cmbOrgStructure)
        PatientEntranceSetupDialog.setTabOrder(self.cmbOrgStructure, self.buttonBox)

    def retranslateUi(self, PatientEntranceSetupDialog):
        PatientEntranceSetupDialog.setWindowTitle(_translate("PatientEntranceSetupDialog", "параметры отчёта", None))
        self.lblOrgStructure.setText(_translate("PatientEntranceSetupDialog", "&Подразделение", None))
        self.edtBegDate.setDisplayFormat(_translate("PatientEntranceSetupDialog", "dd.MM.yyyy", None))
        self.lblBegDate.setText(_translate("PatientEntranceSetupDialog", "Дата &начала периода", None))
        self.edtEndDate.setDisplayFormat(_translate("PatientEntranceSetupDialog", "dd.MM.yyyy", None))
        self.lblEndDate.setText(_translate("PatientEntranceSetupDialog", "Дата &окончания периода", None))

from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
