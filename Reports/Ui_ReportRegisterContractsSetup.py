# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportRegisterContractsSetup.ui'
#
# Created: Thu Feb 05 18:29:16 2015
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

class Ui_ReportRegisterContractsSetupDialog(object):
    def setupUi(self, ReportRegisterContractsSetupDialog):
        ReportRegisterContractsSetupDialog.setObjectName(_fromUtf8("ReportRegisterContractsSetupDialog"))
        ReportRegisterContractsSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportRegisterContractsSetupDialog.resize(390, 277)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ReportRegisterContractsSetupDialog.sizePolicy().hasHeightForWidth())
        ReportRegisterContractsSetupDialog.setSizePolicy(sizePolicy)
        ReportRegisterContractsSetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportRegisterContractsSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblFinanceType = QtGui.QLabel(ReportRegisterContractsSetupDialog)
        self.lblFinanceType.setObjectName(_fromUtf8("lblFinanceType"))
        self.gridLayout.addWidget(self.lblFinanceType, 4, 0, 1, 1)
        self.lblContract = QtGui.QLabel(ReportRegisterContractsSetupDialog)
        self.lblContract.setObjectName(_fromUtf8("lblContract"))
        self.gridLayout.addWidget(self.lblContract, 3, 0, 1, 1)
        self.edtEndDate = QtGui.QDateEdit(ReportRegisterContractsSetupDialog)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 2, 1, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportRegisterContractsSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 2, 0, 1, 1)
        self.edtBegDate = QtGui.QDateEdit(ReportRegisterContractsSetupDialog)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 1, 1, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportRegisterContractsSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 1, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 8, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportRegisterContractsSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 9, 0, 1, 2)
        self.lblOrgStructure = QtGui.QLabel(ReportRegisterContractsSetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 6, 0, 1, 1)
        self.lblEventType = QtGui.QLabel(ReportRegisterContractsSetupDialog)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridLayout.addWidget(self.lblEventType, 5, 0, 1, 1)
        self.cmbFinanceType = CRBComboBox(ReportRegisterContractsSetupDialog)
        self.cmbFinanceType.setObjectName(_fromUtf8("cmbFinanceType"))
        self.gridLayout.addWidget(self.cmbFinanceType, 4, 1, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportRegisterContractsSetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 6, 1, 1, 1)
        self.cmbContract = CContractComboBox(ReportRegisterContractsSetupDialog)
        self.cmbContract.setObjectName(_fromUtf8("cmbContract"))
        self.gridLayout.addWidget(self.cmbContract, 3, 1, 1, 1)
        self.cmbEventType = CRBComboBox(ReportRegisterContractsSetupDialog)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 5, 1, 1, 1)
        self.lblDateSortType = QtGui.QLabel(ReportRegisterContractsSetupDialog)
        self.lblDateSortType.setObjectName(_fromUtf8("lblDateSortType"))
        self.gridLayout.addWidget(self.lblDateSortType, 7, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btnToMonth = QtGui.QRadioButton(ReportRegisterContractsSetupDialog)
        self.btnToMonth.setChecked(True)
        self.btnToMonth.setObjectName(_fromUtf8("btnToMonth"))
        self.horizontalLayout.addWidget(self.btnToMonth)
        self.btnToDay = QtGui.QRadioButton(ReportRegisterContractsSetupDialog)
        self.btnToDay.setObjectName(_fromUtf8("btnToDay"))
        self.horizontalLayout.addWidget(self.btnToDay)
        self.gridLayout.addLayout(self.horizontalLayout, 7, 1, 1, 1)

        self.retranslateUi(ReportRegisterContractsSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportRegisterContractsSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportRegisterContractsSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportRegisterContractsSetupDialog)

    def retranslateUi(self, ReportRegisterContractsSetupDialog):
        ReportRegisterContractsSetupDialog.setWindowTitle(_translate("ReportRegisterContractsSetupDialog", "параметры отчёта", None))
        self.lblFinanceType.setText(_translate("ReportRegisterContractsSetupDialog", "Тип финансирования", None))
        self.lblContract.setText(_translate("ReportRegisterContractsSetupDialog", "Договор", None))
        self.lblEndDate.setText(_translate("ReportRegisterContractsSetupDialog", "Дата окончания периода", None))
        self.lblBegDate.setText(_translate("ReportRegisterContractsSetupDialog", "Дата начала периода", None))
        self.lblOrgStructure.setText(_translate("ReportRegisterContractsSetupDialog", "Подразделение", None))
        self.lblEventType.setText(_translate("ReportRegisterContractsSetupDialog", "Тип обращения", None))
        self.lblDateSortType.setText(_translate("ReportRegisterContractsSetupDialog", "Выводить по", None))
        self.btnToMonth.setText(_translate("ReportRegisterContractsSetupDialog", "месяцам", None))
        self.btnToDay.setText(_translate("ReportRegisterContractsSetupDialog", "дням", None))

from library.crbcombobox import CRBComboBox
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from Accounting.ContractComboBox import CContractComboBox
