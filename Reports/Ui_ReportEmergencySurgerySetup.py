# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportEmergencySurgerySetup.ui'
#
# Created: Wed Nov 26 13:37:19 2014
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

class Ui_ReportEmergencySurgerySetupDialog(object):
    def setupUi(self, ReportEmergencySurgerySetupDialog):
        ReportEmergencySurgerySetupDialog.setObjectName(_fromUtf8("ReportEmergencySurgerySetupDialog"))
        ReportEmergencySurgerySetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportEmergencySurgerySetupDialog.resize(322, 156)
        ReportEmergencySurgerySetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportEmergencySurgerySetupDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        spacerItem = QtGui.QSpacerItem(129, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportEmergencySurgerySetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 6, 0, 1, 3)
        self.lblEndDiagnosis = QtGui.QLabel(ReportEmergencySurgerySetupDialog)
        self.lblEndDiagnosis.setObjectName(_fromUtf8("lblEndDiagnosis"))
        self.gridLayout.addWidget(self.lblEndDiagnosis, 4, 0, 1, 1)
        self.cmbEndDiagnosis = QtGui.QComboBox(ReportEmergencySurgerySetupDialog)
        self.cmbEndDiagnosis.setObjectName(_fromUtf8("cmbEndDiagnosis"))
        self.cmbEndDiagnosis.addItem(_fromUtf8(""))
        self.cmbEndDiagnosis.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbEndDiagnosis, 4, 1, 1, 2)
        self.edtBegDate = QtGui.QDateEdit(ReportEmergencySurgerySetupDialog)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 1, 1, 1, 2)
        self.edtEndDate = QtGui.QDateEdit(ReportEmergencySurgerySetupDialog)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 3, 1, 1, 2)
        self.lblEndDate = QtGui.QLabel(ReportEmergencySurgerySetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 3, 0, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportEmergencySurgerySetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 1, 0, 1, 1)

        self.retranslateUi(ReportEmergencySurgerySetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportEmergencySurgerySetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportEmergencySurgerySetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportEmergencySurgerySetupDialog)

    def retranslateUi(self, ReportEmergencySurgerySetupDialog):
        ReportEmergencySurgerySetupDialog.setWindowTitle(_translate("ReportEmergencySurgerySetupDialog", "параметры отчёта", None))
        self.lblEndDiagnosis.setText(_translate("ReportEmergencySurgerySetupDialog", "Заключительный диагноз", None))
        self.cmbEndDiagnosis.setItemText(0, _translate("ReportEmergencySurgerySetupDialog", "по отделению", None))
        self.cmbEndDiagnosis.setItemText(1, _translate("ReportEmergencySurgerySetupDialog", "по обращению", None))
        self.lblEndDate.setText(_translate("ReportEmergencySurgerySetupDialog", "Дата &окончания периода", None))
        self.lblBegDate.setText(_translate("ReportEmergencySurgerySetupDialog", "Дата &начала периода", None))

