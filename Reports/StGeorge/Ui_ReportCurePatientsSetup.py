# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportCurePatientsSetup.ui'
#
# Created: Wed Sep 23 19:01:44 2015
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

class Ui_ReportCurePatientsSetupDialog(object):
    def setupUi(self, ReportCurePatientsSetupDialog):
        ReportCurePatientsSetupDialog.setObjectName(_fromUtf8("ReportCurePatientsSetupDialog"))
        ReportCurePatientsSetupDialog.resize(400, 151)
        self.formLayout = QtGui.QFormLayout(ReportCurePatientsSetupDialog)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(ReportCurePatientsSetupDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.edtBegDate = CDateEdit(ReportCurePatientsSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.edtBegDate)
        self.label_2 = QtGui.QLabel(ReportCurePatientsSetupDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.edtEndDate = CDateEdit(ReportCurePatientsSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.edtEndDate)
        self.label_3 = QtGui.QLabel(ReportCurePatientsSetupDialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_3)
        self.cmbOrganisation = COrgComboBox(ReportCurePatientsSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbOrganisation.sizePolicy().hasHeightForWidth())
        self.cmbOrganisation.setSizePolicy(sizePolicy)
        self.cmbOrganisation.setObjectName(_fromUtf8("cmbOrganisation"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.cmbOrganisation)
        self.label_4 = QtGui.QLabel(ReportCurePatientsSetupDialog)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_4)
        self.cmbOrgStruct = COrgStructureComboBox(ReportCurePatientsSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbOrgStruct.sizePolicy().hasHeightForWidth())
        self.cmbOrgStruct.setSizePolicy(sizePolicy)
        self.cmbOrgStruct.setObjectName(_fromUtf8("cmbOrgStruct"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.cmbOrgStruct)
        spacerItem = QtGui.QSpacerItem(327, 2, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.formLayout.setItem(4, QtGui.QFormLayout.FieldRole, spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(ReportCurePatientsSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.SpanningRole, self.buttonBox)

        self.retranslateUi(ReportCurePatientsSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportCurePatientsSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportCurePatientsSetupDialog)

    def retranslateUi(self, ReportCurePatientsSetupDialog):
        ReportCurePatientsSetupDialog.setWindowTitle(_translate("ReportCurePatientsSetupDialog", "Dialog", None))
        self.label.setText(_translate("ReportCurePatientsSetupDialog", "Дата начала", None))
        self.label_2.setText(_translate("ReportCurePatientsSetupDialog", "Дата окончания", None))
        self.label_3.setText(_translate("ReportCurePatientsSetupDialog", "Плательщик", None))
        self.label_4.setText(_translate("ReportCurePatientsSetupDialog", "Подразделение", None))

from Orgs.OrgComboBox import COrgComboBox
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
