# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportMonitoringOIMSetup.ui'
#
# Created: Tue Nov 11 15:03:18 2014
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

class Ui_ReportMonitoringOIMSetupDialog(object):
    def setupUi(self, ReportMonitoringOIMSetupDialog):
        ReportMonitoringOIMSetupDialog.setObjectName(_fromUtf8("ReportMonitoringOIMSetupDialog"))
        ReportMonitoringOIMSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportMonitoringOIMSetupDialog.resize(326, 156)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ReportMonitoringOIMSetupDialog.sizePolicy().hasHeightForWidth())
        ReportMonitoringOIMSetupDialog.setSizePolicy(sizePolicy)
        ReportMonitoringOIMSetupDialog.setSizeGripEnabled(True)
        self.formLayout = QtGui.QFormLayout(ReportMonitoringOIMSetupDialog)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.lblBegDate = QtGui.QLabel(ReportMonitoringOIMSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.lblBegDate)
        self.edtBegDate = QtGui.QDateEdit(ReportMonitoringOIMSetupDialog)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.edtBegDate)
        self.lblEndDate = QtGui.QLabel(ReportMonitoringOIMSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.lblEndDate)
        self.edtEndDate = QtGui.QDateEdit(ReportMonitoringOIMSetupDialog)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.edtEndDate)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.formLayout.setItem(3, QtGui.QFormLayout.FieldRole, spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(ReportMonitoringOIMSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.SpanningRole, self.buttonBox)
        self.cmbEndDiagnosis = QtGui.QComboBox(ReportMonitoringOIMSetupDialog)
        self.cmbEndDiagnosis.setObjectName(_fromUtf8("cmbEndDiagnosis"))
        self.cmbEndDiagnosis.addItem(_fromUtf8(""))
        self.cmbEndDiagnosis.addItem(_fromUtf8(""))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.cmbEndDiagnosis)
        self.lblEndDiagnosis = QtGui.QLabel(ReportMonitoringOIMSetupDialog)
        self.lblEndDiagnosis.setObjectName(_fromUtf8("lblEndDiagnosis"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.lblEndDiagnosis)

        self.retranslateUi(ReportMonitoringOIMSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportMonitoringOIMSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportMonitoringOIMSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportMonitoringOIMSetupDialog)

    def retranslateUi(self, ReportMonitoringOIMSetupDialog):
        ReportMonitoringOIMSetupDialog.setWindowTitle(_translate("ReportMonitoringOIMSetupDialog", "параметры отчёта", None))
        self.lblBegDate.setText(_translate("ReportMonitoringOIMSetupDialog", "Дата начала периода", None))
        self.lblEndDate.setText(_translate("ReportMonitoringOIMSetupDialog", "Дата окончания периода", None))
        self.cmbEndDiagnosis.setItemText(0, _translate("ReportMonitoringOIMSetupDialog", "по отделению", None))
        self.cmbEndDiagnosis.setItemText(1, _translate("ReportMonitoringOIMSetupDialog", "по обращению", None))
        self.lblEndDiagnosis.setText(_translate("ReportMonitoringOIMSetupDialog", "Заключительный диагноз", None))

