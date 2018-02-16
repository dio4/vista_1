# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportF30PRRSubsidiarySetup.ui'
#
# Created: Wed Sep 11 19:52:50 2013
#      by: PyQt4 UI code generator 4.10
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

class Ui_ReportF30PRRSubsidiarySetupDialog(object):
    def setupUi(self, ReportF30PRRSubsidiarySetupDialog):
        ReportF30PRRSubsidiarySetupDialog.setObjectName(_fromUtf8("ReportF30PRRSubsidiarySetupDialog"))
        ReportF30PRRSubsidiarySetupDialog.resize(255, 100)
        self.gridLayout = QtGui.QGridLayout(ReportF30PRRSubsidiarySetupDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonBox = QtGui.QDialogButtonBox(ReportF30PRRSubsidiarySetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 5)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 3, 1, 1)
        self.edtDiagnosis = CICDCodeComboBoxEx(ReportF30PRRSubsidiarySetupDialog)
        self.edtDiagnosis.setObjectName(_fromUtf8("edtDiagnosis"))
        self.gridLayout.addWidget(self.edtDiagnosis, 1, 1, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 3, 1, 2)
        self.lblDiagnosis = QtGui.QLabel(ReportF30PRRSubsidiarySetupDialog)
        self.lblDiagnosis.setObjectName(_fromUtf8("lblDiagnosis"))
        self.gridLayout.addWidget(self.lblDiagnosis, 1, 0, 1, 1)

        self.retranslateUi(ReportF30PRRSubsidiarySetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportF30PRRSubsidiarySetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportF30PRRSubsidiarySetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportF30PRRSubsidiarySetupDialog)

    def retranslateUi(self, ReportF30PRRSubsidiarySetupDialog):
        ReportF30PRRSubsidiarySetupDialog.setWindowTitle(_translate("ReportF30PRRSubsidiarySetupDialog", "Dialog", None))
        self.lblDiagnosis.setText(_translate("ReportF30PRRSubsidiarySetupDialog", "Диагноз", None))

from library.ICDCodeEdit import CICDCodeComboBoxEx
