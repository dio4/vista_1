# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportSalary_OrgStructureSetup.ui'
#
# Created: Wed Sep 09 14:40:06 2015
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

class Ui_ReportSalary_OrgStructureSetupDialog(object):
    def setupUi(self, ReportSalary_OrgStructureSetupDialog):
        ReportSalary_OrgStructureSetupDialog.setObjectName(_fromUtf8("ReportSalary_OrgStructureSetupDialog"))
        ReportSalary_OrgStructureSetupDialog.resize(400, 125)
        self.formLayout = QtGui.QFormLayout(ReportSalary_OrgStructureSetupDialog)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(ReportSalary_OrgStructureSetupDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.edtBegDate = CDateEdit(ReportSalary_OrgStructureSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.edtBegDate)
        self.label_2 = QtGui.QLabel(ReportSalary_OrgStructureSetupDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.edtEndDate = CDateEdit(ReportSalary_OrgStructureSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.edtEndDate)
        self.label_3 = QtGui.QLabel(ReportSalary_OrgStructureSetupDialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_3)
        self.cmbOrgStructure = COrgStructureComboBox(ReportSalary_OrgStructureSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbOrgStructure.sizePolicy().hasHeightForWidth())
        self.cmbOrgStructure.setSizePolicy(sizePolicy)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.cmbOrgStructure)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.formLayout.setItem(3, QtGui.QFormLayout.LabelRole, spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(ReportSalary_OrgStructureSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.SpanningRole, self.buttonBox)

        self.retranslateUi(ReportSalary_OrgStructureSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportSalary_OrgStructureSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportSalary_OrgStructureSetupDialog)

    def retranslateUi(self, ReportSalary_OrgStructureSetupDialog):
        ReportSalary_OrgStructureSetupDialog.setWindowTitle(_translate("ReportSalary_OrgStructureSetupDialog", "Dialog", None))
        self.label.setText(_translate("ReportSalary_OrgStructureSetupDialog", "Дата начала периода", None))
        self.label_2.setText(_translate("ReportSalary_OrgStructureSetupDialog", "Дата окончания периода", None))
        self.label_3.setText(_translate("ReportSalary_OrgStructureSetupDialog", "Подразделение", None))

from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
