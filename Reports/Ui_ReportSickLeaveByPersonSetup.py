# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportSickLeaveByPersonSetup.ui'
#
# Created: Fri Jul 04 16:32:54 2014
#      by: PyQt4 UI code generator 4.11
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

class Ui_ReportSickLeaveByPersonSetupDialog(object):
    def setupUi(self, ReportSickLeaveByPersonSetupDialog):
        ReportSickLeaveByPersonSetupDialog.setObjectName(_fromUtf8("ReportSickLeaveByPersonSetupDialog"))
        ReportSickLeaveByPersonSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportSickLeaveByPersonSetupDialog.resize(395, 193)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ReportSickLeaveByPersonSetupDialog.sizePolicy().hasHeightForWidth())
        ReportSickLeaveByPersonSetupDialog.setSizePolicy(sizePolicy)
        ReportSickLeaveByPersonSetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportSickLeaveByPersonSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.cmbForming = QtGui.QComboBox(ReportSickLeaveByPersonSetupDialog)
        self.cmbForming.setObjectName(_fromUtf8("cmbForming"))
        self.cmbForming.addItem(_fromUtf8(""))
        self.cmbForming.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbForming, 0, 1, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportSickLeaveByPersonSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 1, 0, 1, 1)
        self.edtBegDate = QtGui.QDateEdit(ReportSickLeaveByPersonSetupDialog)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 1, 1, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportSickLeaveByPersonSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 2, 0, 1, 1)
        self.edtEndDate = QtGui.QDateEdit(ReportSickLeaveByPersonSetupDialog)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 2, 1, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(ReportSickLeaveByPersonSetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 4, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportSickLeaveByPersonSetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 4, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 6, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportSickLeaveByPersonSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 8, 0, 1, 2)
        self.lblForming = QtGui.QLabel(ReportSickLeaveByPersonSetupDialog)
        self.lblForming.setObjectName(_fromUtf8("lblForming"))
        self.gridLayout.addWidget(self.lblForming, 0, 0, 1, 1)
        self.chkOpen = QtGui.QCheckBox(ReportSickLeaveByPersonSetupDialog)
        self.chkOpen.setObjectName(_fromUtf8("chkOpen"))
        self.gridLayout.addWidget(self.chkOpen, 3, 0, 1, 1)

        self.retranslateUi(ReportSickLeaveByPersonSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportSickLeaveByPersonSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportSickLeaveByPersonSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportSickLeaveByPersonSetupDialog)

    def retranslateUi(self, ReportSickLeaveByPersonSetupDialog):
        ReportSickLeaveByPersonSetupDialog.setWindowTitle(_translate("ReportSickLeaveByPersonSetupDialog", "параметры отчёта", None))
        self.cmbForming.setItemText(0, _translate("ReportSickLeaveByPersonSetupDialog", "Врачам", None))
        self.cmbForming.setItemText(1, _translate("ReportSickLeaveByPersonSetupDialog", "Отделениям", None))
        self.lblBegDate.setText(_translate("ReportSickLeaveByPersonSetupDialog", "Дата начала периода", None))
        self.lblEndDate.setText(_translate("ReportSickLeaveByPersonSetupDialog", "Дата окончания периода", None))
        self.lblOrgStructure.setText(_translate("ReportSickLeaveByPersonSetupDialog", "Подразделение", None))
        self.lblForming.setText(_translate("ReportSickLeaveByPersonSetupDialog", "Формировать отчёт по", None))
        self.chkOpen.setText(_translate("ReportSickLeaveByPersonSetupDialog", "Учитывать незакрытые", None))

from Orgs.OrgStructComboBoxes import COrgStructureComboBox
