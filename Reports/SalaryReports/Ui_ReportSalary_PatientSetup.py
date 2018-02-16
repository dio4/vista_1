# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportSalary_PatientSetup.ui'
#
# Created: Wed Sep 09 14:40:39 2015
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

class Ui_ReportSalary_PatientSetupDialog(object):
    def setupUi(self, ReportSalary_PatientSetupDialog):
        ReportSalary_PatientSetupDialog.setObjectName(_fromUtf8("ReportSalary_PatientSetupDialog"))
        ReportSalary_PatientSetupDialog.resize(400, 203)
        self.formLayout = QtGui.QFormLayout(ReportSalary_PatientSetupDialog)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(ReportSalary_PatientSetupDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.edtBegDate = CDateEdit(ReportSalary_PatientSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.edtBegDate)
        self.label_2 = QtGui.QLabel(ReportSalary_PatientSetupDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.edtEndDate = CDateEdit(ReportSalary_PatientSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.edtEndDate)
        self.label_3 = QtGui.QLabel(ReportSalary_PatientSetupDialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_3)
        self.editAmbCard = QtGui.QLineEdit(ReportSalary_PatientSetupDialog)
        self.editAmbCard.setObjectName(_fromUtf8("editAmbCard"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.editAmbCard)
        self.label_4 = QtGui.QLabel(ReportSalary_PatientSetupDialog)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_4)
        self.editLastName = QtGui.QLineEdit(ReportSalary_PatientSetupDialog)
        self.editLastName.setObjectName(_fromUtf8("editLastName"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.editLastName)
        self.label_5 = QtGui.QLabel(ReportSalary_PatientSetupDialog)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.label_5)
        self.editFirstName = QtGui.QLineEdit(ReportSalary_PatientSetupDialog)
        self.editFirstName.setObjectName(_fromUtf8("editFirstName"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.editFirstName)
        self.label_6 = QtGui.QLabel(ReportSalary_PatientSetupDialog)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.LabelRole, self.label_6)
        self.editPatrName = QtGui.QLineEdit(ReportSalary_PatientSetupDialog)
        self.editPatrName.setObjectName(_fromUtf8("editPatrName"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.FieldRole, self.editPatrName)
        spacerItem = QtGui.QSpacerItem(244, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.formLayout.setItem(6, QtGui.QFormLayout.FieldRole, spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(ReportSalary_PatientSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(7, QtGui.QFormLayout.SpanningRole, self.buttonBox)

        self.retranslateUi(ReportSalary_PatientSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportSalary_PatientSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportSalary_PatientSetupDialog)

    def retranslateUi(self, ReportSalary_PatientSetupDialog):
        ReportSalary_PatientSetupDialog.setWindowTitle(_translate("ReportSalary_PatientSetupDialog", "Dialog", None))
        self.label.setText(_translate("ReportSalary_PatientSetupDialog", "Дата начала периода", None))
        self.label_2.setText(_translate("ReportSalary_PatientSetupDialog", "Дата окончания периода", None))
        self.label_3.setText(_translate("ReportSalary_PatientSetupDialog", "Код", None))
        self.label_4.setText(_translate("ReportSalary_PatientSetupDialog", "Фамилия", None))
        self.label_5.setText(_translate("ReportSalary_PatientSetupDialog", "Имя", None))
        self.label_6.setText(_translate("ReportSalary_PatientSetupDialog", "Отчество", None))

from library.DateEdit import CDateEdit
