# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ReportDeathBSKSetup.ui'
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

class Ui_ReportDeathBSKSetupDialog(object):
    def setupUi(self, ReportDeathBSKSetupDialog):
        ReportDeathBSKSetupDialog.setObjectName(_fromUtf8("ReportDeathBSKSetupDialog"))
        ReportDeathBSKSetupDialog.resize(400, 168)
        self.formLayout = QtGui.QFormLayout(ReportDeathBSKSetupDialog)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(ReportDeathBSKSetupDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.label_2 = QtGui.QLabel(ReportDeathBSKSetupDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_2)
        self.label_3 = QtGui.QLabel(ReportDeathBSKSetupDialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.label_3)
        self.chkHell = QtGui.QCheckBox(ReportDeathBSKSetupDialog)
        self.chkHell.setText(_fromUtf8(""))
        self.chkHell.setObjectName(_fromUtf8("chkHell"))
        self.formLayout.setWidget(6, QtGui.QFormLayout.LabelRole, self.chkHell)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.formLayout.setItem(8, QtGui.QFormLayout.FieldRole, spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(ReportDeathBSKSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(9, QtGui.QFormLayout.SpanningRole, self.buttonBox)
        self.edtBegDate = CDateEdit(ReportDeathBSKSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.edtBegDate)
        self.edtEndDate = CDateEdit(ReportDeathBSKSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.edtEndDate)
        self.cmbOrgStruct = COrgStructureComboBox(ReportDeathBSKSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbOrgStruct.sizePolicy().hasHeightForWidth())
        self.cmbOrgStruct.setSizePolicy(sizePolicy)
        self.cmbOrgStruct.setObjectName(_fromUtf8("cmbOrgStruct"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.cmbOrgStruct)
        self.label_4 = QtGui.QLabel(ReportDeathBSKSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.formLayout.setWidget(6, QtGui.QFormLayout.FieldRole, self.label_4)

        self.retranslateUi(ReportDeathBSKSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportDeathBSKSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportDeathBSKSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportDeathBSKSetupDialog)

    def retranslateUi(self, ReportDeathBSKSetupDialog):
        ReportDeathBSKSetupDialog.setWindowTitle(_translate("ReportDeathBSKSetupDialog", "Dialog", None))
        self.label.setText(_translate("ReportDeathBSKSetupDialog", "Дата начала", None))
        self.label_2.setText(_translate("ReportDeathBSKSetupDialog", "Дата окончания", None))
        self.label_3.setText(_translate("ReportDeathBSKSetupDialog", "Подразделение", None))
        self.label_4.setText(_translate("ReportDeathBSKSetupDialog", "Детализовать по пациентам", None))

from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from library.DateEdit import CDateEdit
