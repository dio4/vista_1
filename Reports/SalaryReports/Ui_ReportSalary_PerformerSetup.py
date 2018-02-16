# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportSalary_PerformerSetup.ui'
#
# Created: Wed Sep 09 14:41:29 2015
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

class Ui_ReportSalary_PerformerSetupDialog(object):
    def setupUi(self, ReportSalary_PerformerSetupDialog):
        ReportSalary_PerformerSetupDialog.setObjectName(_fromUtf8("ReportSalary_PerformerSetupDialog"))
        ReportSalary_PerformerSetupDialog.resize(400, 125)
        self.gridLayout = QtGui.QGridLayout(ReportSalary_PerformerSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(ReportSalary_PerformerSetupDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.edtBegDate = CDateEdit(ReportSalary_PerformerSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(ReportSalary_PerformerSetupDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportSalary_PerformerSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        self.cmbType = QtGui.QComboBox(ReportSalary_PerformerSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbType.sizePolicy().hasHeightForWidth())
        self.cmbType.setSizePolicy(sizePolicy)
        self.cmbType.setObjectName(_fromUtf8("cmbType"))
        self.cmbType.addItem(_fromUtf8(""))
        self.cmbType.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbType, 2, 0, 1, 1)
        self.cmbPerformer = CPersonComboBoxEx(ReportSalary_PerformerSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbPerformer.sizePolicy().hasHeightForWidth())
        self.cmbPerformer.setSizePolicy(sizePolicy)
        self.cmbPerformer.setObjectName(_fromUtf8("cmbPerformer"))
        self.gridLayout.addWidget(self.cmbPerformer, 2, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportSalary_PerformerSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 0, 1, 1)

        self.retranslateUi(ReportSalary_PerformerSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportSalary_PerformerSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportSalary_PerformerSetupDialog)

    def retranslateUi(self, ReportSalary_PerformerSetupDialog):
        ReportSalary_PerformerSetupDialog.setWindowTitle(_translate("ReportSalary_PerformerSetupDialog", "Dialog", None))
        self.label.setText(_translate("ReportSalary_PerformerSetupDialog", "Дата начала периода", None))
        self.label_2.setText(_translate("ReportSalary_PerformerSetupDialog", "Дата окончания периода", None))
        self.cmbType.setItemText(0, _translate("ReportSalary_PerformerSetupDialog", "Исполнитель", None))
        self.cmbType.setItemText(1, _translate("ReportSalary_PerformerSetupDialog", "Ассистент", None))

from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.DateEdit import CDateEdit
