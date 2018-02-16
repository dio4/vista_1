# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportSalary_ServiceSetup.ui'
#
# Created: Wed Sep 09 14:42:02 2015
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

class Ui_ReportSalary_ServiceSetupDialog(object):
    def setupUi(self, ReportSalary_ServiceSetupDialog):
        ReportSalary_ServiceSetupDialog.setObjectName(_fromUtf8("ReportSalary_ServiceSetupDialog"))
        ReportSalary_ServiceSetupDialog.resize(400, 144)
        self.formLayout = QtGui.QFormLayout(ReportSalary_ServiceSetupDialog)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(ReportSalary_ServiceSetupDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.edtBegDate = CDateEdit(ReportSalary_ServiceSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.edtBegDate)
        self.label_2 = QtGui.QLabel(ReportSalary_ServiceSetupDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.edtEndDate = CDateEdit(ReportSalary_ServiceSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.edtEndDate)
        self.label_3 = QtGui.QLabel(ReportSalary_ServiceSetupDialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_3)
        self.cmbService = CActionTypeComboBox(ReportSalary_ServiceSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbService.sizePolicy().hasHeightForWidth())
        self.cmbService.setSizePolicy(sizePolicy)
        self.cmbService.setObjectName(_fromUtf8("cmbService"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.cmbService)
        self.label_4 = QtGui.QLabel(ReportSalary_ServiceSetupDialog)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_4)
        self.chkGroup = QtGui.QCheckBox(ReportSalary_ServiceSetupDialog)
        self.chkGroup.setText(_fromUtf8(""))
        self.chkGroup.setObjectName(_fromUtf8("chkGroup"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.chkGroup)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.formLayout.setItem(4, QtGui.QFormLayout.LabelRole, spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(ReportSalary_ServiceSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.SpanningRole, self.buttonBox)

        self.retranslateUi(ReportSalary_ServiceSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportSalary_ServiceSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportSalary_ServiceSetupDialog)

    def retranslateUi(self, ReportSalary_ServiceSetupDialog):
        ReportSalary_ServiceSetupDialog.setWindowTitle(_translate("ReportSalary_ServiceSetupDialog", "Dialog", None))
        self.label.setText(_translate("ReportSalary_ServiceSetupDialog", "Дата начала периода", None))
        self.label_2.setText(_translate("ReportSalary_ServiceSetupDialog", "Дата окончания периода", None))
        self.label_3.setText(_translate("ReportSalary_ServiceSetupDialog", "Услуга", None))
        self.label_4.setText(_translate("ReportSalary_ServiceSetupDialog", "Группировать по пациентам", None))

from Events.ActionTypeComboBox import CActionTypeComboBox
from library.DateEdit import CDateEdit
