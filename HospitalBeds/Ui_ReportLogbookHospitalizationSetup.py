# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportLogbookHospitalizationSetup.ui'
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

class Ui_ReportLogbookHospitalizationSetupDialog(object):
    def setupUi(self, ReportLogbookHospitalizationSetupDialog):
        ReportLogbookHospitalizationSetupDialog.setObjectName(_fromUtf8("ReportLogbookHospitalizationSetupDialog"))
        ReportLogbookHospitalizationSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportLogbookHospitalizationSetupDialog.resize(305, 324)
        ReportLogbookHospitalizationSetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportLogbookHospitalizationSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.edtDiapTo = QtGui.QLineEdit(ReportLogbookHospitalizationSetupDialog)
        self.edtDiapTo.setObjectName(_fromUtf8("edtDiapTo"))
        self.gridLayout.addWidget(self.edtDiapTo, 4, 0, 1, 1)
        self.lblDiap = QtGui.QLabel(ReportLogbookHospitalizationSetupDialog)
        self.lblDiap.setObjectName(_fromUtf8("lblDiap"))
        self.gridLayout.addWidget(self.lblDiap, 0, 0, 1, 3)
        self.buttonBox = QtGui.QDialogButtonBox(ReportLogbookHospitalizationSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 12, 0, 1, 1)
        self.lblPrefix = QtGui.QLabel(ReportLogbookHospitalizationSetupDialog)
        self.lblPrefix.setObjectName(_fromUtf8("lblPrefix"))
        self.gridLayout.addWidget(self.lblPrefix, 5, 0, 1, 1)
        self.edtPrefix = QtGui.QLineEdit(ReportLogbookHospitalizationSetupDialog)
        self.edtPrefix.setObjectName(_fromUtf8("edtPrefix"))
        self.gridLayout.addWidget(self.edtPrefix, 6, 0, 1, 1)
        self.lblDiapTo = QtGui.QLabel(ReportLogbookHospitalizationSetupDialog)
        self.lblDiapTo.setObjectName(_fromUtf8("lblDiapTo"))
        self.gridLayout.addWidget(self.lblDiapTo, 3, 0, 1, 1)
        self.edtDiapFrom = QtGui.QLineEdit(ReportLogbookHospitalizationSetupDialog)
        self.edtDiapFrom.setObjectName(_fromUtf8("edtDiapFrom"))
        self.gridLayout.addWidget(self.edtDiapFrom, 2, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(129, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 11, 0, 1, 1)
        self.lblDiapFrom = QtGui.QLabel(ReportLogbookHospitalizationSetupDialog)
        self.lblDiapFrom.setObjectName(_fromUtf8("lblDiapFrom"))
        self.gridLayout.addWidget(self.lblDiapFrom, 1, 0, 1, 1)
        self.cmbContract = CContractComboBox(ReportLogbookHospitalizationSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbContract.sizePolicy().hasHeightForWidth())
        self.cmbContract.setSizePolicy(sizePolicy)
        self.cmbContract.setObjectName(_fromUtf8("cmbContract"))
        self.gridLayout.addWidget(self.cmbContract, 8, 0, 1, 1)
        self.lblContract = QtGui.QLabel(ReportLogbookHospitalizationSetupDialog)
        self.lblContract.setObjectName(_fromUtf8("lblContract"))
        self.gridLayout.addWidget(self.lblContract, 7, 0, 1, 1)
        self.label = QtGui.QLabel(ReportLogbookHospitalizationSetupDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 9, 0, 1, 1)
        self.cmbResult = CRBComboBox(ReportLogbookHospitalizationSetupDialog)
        self.cmbResult.setObjectName(_fromUtf8("cmbResult"))
        self.gridLayout.addWidget(self.cmbResult, 10, 0, 1, 1)

        self.retranslateUi(ReportLogbookHospitalizationSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportLogbookHospitalizationSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportLogbookHospitalizationSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportLogbookHospitalizationSetupDialog)

    def retranslateUi(self, ReportLogbookHospitalizationSetupDialog):
        ReportLogbookHospitalizationSetupDialog.setWindowTitle(_translate("ReportLogbookHospitalizationSetupDialog", "параметры отчёта", None))
        self.lblDiap.setText(_translate("ReportLogbookHospitalizationSetupDialog", "Диапазон номеров истории болезни:", None))
        self.lblPrefix.setText(_translate("ReportLogbookHospitalizationSetupDialog", "Префикс", None))
        self.lblDiapTo.setText(_translate("ReportLogbookHospitalizationSetupDialog", "до", None))
        self.lblDiapFrom.setText(_translate("ReportLogbookHospitalizationSetupDialog", "от", None))
        self.lblContract.setText(_translate("ReportLogbookHospitalizationSetupDialog", "Договор", None))
        self.label.setText(_translate("ReportLogbookHospitalizationSetupDialog", "Результат", None))

from Accounting.ContractComboBox import CContractComboBox
from library.crbcombobox import CRBComboBox
