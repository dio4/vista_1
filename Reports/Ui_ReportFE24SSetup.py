# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportFE24SSetup.ui'
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

class Ui_ReportFE24SSetupDialog(object):
    def setupUi(self, ReportFE24SSetupDialog):
        ReportFE24SSetupDialog.setObjectName(_fromUtf8("ReportFE24SSetupDialog"))
        ReportFE24SSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportFE24SSetupDialog.resize(397, 207)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ReportFE24SSetupDialog.sizePolicy().hasHeightForWidth())
        ReportFE24SSetupDialog.setSizePolicy(sizePolicy)
        ReportFE24SSetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportFE24SSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblFinance = QtGui.QLabel(ReportFE24SSetupDialog)
        self.lblFinance.setObjectName(_fromUtf8("lblFinance"))
        self.gridLayout.addWidget(self.lblFinance, 0, 0, 1, 1)
        self.lblAccountNumber = QtGui.QLabel(ReportFE24SSetupDialog)
        self.lblAccountNumber.setObjectName(_fromUtf8("lblAccountNumber"))
        self.gridLayout.addWidget(self.lblAccountNumber, 3, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 7, 0, 1, 1)
        self.cmbFinance = CRBComboBox(ReportFE24SSetupDialog)
        self.cmbFinance.setObjectName(_fromUtf8("cmbFinance"))
        self.gridLayout.addWidget(self.cmbFinance, 0, 1, 1, 1)
        self.cmbTariffType = QtGui.QComboBox(ReportFE24SSetupDialog)
        self.cmbTariffType.setEnabled(True)
        self.cmbTariffType.setObjectName(_fromUtf8("cmbTariffType"))
        self.cmbTariffType.addItem(_fromUtf8(""))
        self.cmbTariffType.addItem(_fromUtf8(""))
        self.cmbTariffType.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbTariffType, 2, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportFE24SSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 8, 0, 1, 2)
        self.gbOrgStructureInfo = QtGui.QGroupBox(ReportFE24SSetupDialog)
        self.gbOrgStructureInfo.setObjectName(_fromUtf8("gbOrgStructureInfo"))
        self.gridLayout_2 = QtGui.QGridLayout(self.gbOrgStructureInfo)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.rbtnByPerson = QtGui.QRadioButton(self.gbOrgStructureInfo)
        self.rbtnByPerson.setChecked(False)
        self.rbtnByPerson.setObjectName(_fromUtf8("rbtnByPerson"))
        self.gridLayout_2.addWidget(self.rbtnByPerson, 0, 0, 1, 1)
        self.rbtnByAction = QtGui.QRadioButton(self.gbOrgStructureInfo)
        self.rbtnByAction.setChecked(True)
        self.rbtnByAction.setObjectName(_fromUtf8("rbtnByAction"))
        self.gridLayout_2.addWidget(self.rbtnByAction, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.gbOrgStructureInfo, 6, 0, 1, 2)
        self.lblTariffType = QtGui.QLabel(ReportFE24SSetupDialog)
        self.lblTariffType.setObjectName(_fromUtf8("lblTariffType"))
        self.gridLayout.addWidget(self.lblTariffType, 2, 0, 1, 1)
        self.edtAccountNumber = QtGui.QLineEdit(ReportFE24SSetupDialog)
        self.edtAccountNumber.setObjectName(_fromUtf8("edtAccountNumber"))
        self.gridLayout.addWidget(self.edtAccountNumber, 3, 1, 1, 1)
        self.chkPayStatus = QtGui.QCheckBox(ReportFE24SSetupDialog)
        self.chkPayStatus.setObjectName(_fromUtf8("chkPayStatus"))
        self.gridLayout.addWidget(self.chkPayStatus, 4, 0, 1, 1)
        self.cmbPayStatus = QtGui.QComboBox(ReportFE24SSetupDialog)
        self.cmbPayStatus.setEnabled(False)
        self.cmbPayStatus.setObjectName(_fromUtf8("cmbPayStatus"))
        self.gridLayout.addWidget(self.cmbPayStatus, 4, 1, 1, 1)

        self.retranslateUi(ReportFE24SSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportFE24SSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportFE24SSetupDialog.reject)
        QtCore.QObject.connect(self.chkPayStatus, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbPayStatus.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(ReportFE24SSetupDialog)

    def retranslateUi(self, ReportFE24SSetupDialog):
        ReportFE24SSetupDialog.setWindowTitle(_translate("ReportFE24SSetupDialog", "параметры отчёта", None))
        self.lblFinance.setText(_translate("ReportFE24SSetupDialog", "Тип финансирования", None))
        self.lblAccountNumber.setText(_translate("ReportFE24SSetupDialog", "Номер реестра: ", None))
        self.cmbTariffType.setItemText(0, _translate("ReportFE24SSetupDialog", "общий по ОМС", None))
        self.cmbTariffType.setItemText(1, _translate("ReportFE24SSetupDialog", "по выполнению СОМП и повышению АПМП", None))
        self.cmbTariffType.setItemText(2, _translate("ReportFE24SSetupDialog", "по стимулирующим выплатам", None))
        self.gbOrgStructureInfo.setTitle(_translate("ReportFE24SSetupDialog", "Определять подразделение", None))
        self.rbtnByPerson.setText(_translate("ReportFE24SSetupDialog", "по врачу", None))
        self.rbtnByAction.setText(_translate("ReportFE24SSetupDialog", "по движению", None))
        self.lblTariffType.setText(_translate("ReportFE24SSetupDialog", "Тип тарифа", None))
        self.chkPayStatus.setText(_translate("ReportFE24SSetupDialog", "Тип реестра", None))

from library.crbcombobox import CRBComboBox
