# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportContractsRegistry.ui'
#
# Created: Wed Oct 07 14:28:50 2015
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_ReportContractsRegistrySetupDialog(object):
    def setupUi(self, ReportContractsRegistrySetupDialog):
        ReportContractsRegistrySetupDialog.setObjectName(_fromUtf8("ReportContractsRegistrySetupDialog"))
        ReportContractsRegistrySetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportContractsRegistrySetupDialog.resize(390, 300)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ReportContractsRegistrySetupDialog.sizePolicy().hasHeightForWidth())
        ReportContractsRegistrySetupDialog.setSizePolicy(sizePolicy)
        ReportContractsRegistrySetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportContractsRegistrySetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.edtBegDate = CDateEdit(ReportContractsRegistrySetupDialog)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 1, 1, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportContractsRegistrySetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 1, 0, 1, 1)
        self.edtBegTime = CTimeEdit(ReportContractsRegistrySetupDialog)
        self.edtBegTime.setObjectName(_fromUtf8("edtBegTime"))
        self.gridLayout.addWidget(self.edtBegTime, 2, 1, 1, 1)
        self.lblBegTime = QtGui.QLabel(ReportContractsRegistrySetupDialog)
        self.lblBegTime.setObjectName(_fromUtf8("lblBegTime"))
        self.gridLayout.addWidget(self.lblBegTime, 2, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportContractsRegistrySetupDialog)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 3, 1, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportContractsRegistrySetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 3, 0, 1, 1)
        self.edtEndTime = CTimeEdit(ReportContractsRegistrySetupDialog)
        self.edtEndTime.setObjectName(_fromUtf8("edtEndTime"))
        self.gridLayout.addWidget(self.edtEndTime, 4, 1, 1, 1)
        self.lblEndTime = QtGui.QLabel(ReportContractsRegistrySetupDialog)
        self.lblEndTime.setObjectName(_fromUtf8("lblEndTime"))
        self.gridLayout.addWidget(self.lblEndTime, 4, 0, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(ReportContractsRegistrySetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 5, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportContractsRegistrySetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 5, 1, 1, 1)
        self.lblContract = QtGui.QLabel(ReportContractsRegistrySetupDialog)
        self.lblContract.setObjectName(_fromUtf8("lblContract"))
        self.gridLayout.addWidget(self.lblContract, 6, 0, 1, 1)
        self.cmbContract = CContractComboBox(ReportContractsRegistrySetupDialog)
        self.cmbContract.setObjectName(_fromUtf8("cmbContract"))
        self.gridLayout.addWidget(self.cmbContract, 6, 1, 1, 1)
        self.lblPerson = QtGui.QLabel(ReportContractsRegistrySetupDialog)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridLayout.addWidget(self.lblPerson, 7, 0, 1, 1)
        self.cmbPerson = CPersonComboBox(ReportContractsRegistrySetupDialog)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.gridLayout.addWidget(self.cmbPerson, 7, 1, 1, 1)
        self.lblFinance = QtGui.QLabel(ReportContractsRegistrySetupDialog)
        self.lblFinance.setObjectName(_fromUtf8("lblFinance"))
        self.gridLayout.addWidget(self.lblFinance, 8, 0, 1, 1)
        self.cmbFinance = CRBComboBox(ReportContractsRegistrySetupDialog)
        self.cmbFinance.setObjectName(_fromUtf8("cmbFinance"))
        self.gridLayout.addWidget(self.cmbFinance, 8, 1, 1, 1)
        self.lblEventType = QtGui.QLabel(ReportContractsRegistrySetupDialog)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridLayout.addWidget(self.lblEventType, 9, 0, 1, 1)
        self.cmbEventType = CRBComboBox(ReportContractsRegistrySetupDialog)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 9, 1, 1, 1)
        self.lblVisitPayStatus = QtGui.QLabel(ReportContractsRegistrySetupDialog)
        self.lblVisitPayStatus.setObjectName(_fromUtf8("lblVisitPayStatus"))
        self.gridLayout.addWidget(self.lblVisitPayStatus, 10, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 10, 1, 1, 1)
        self.cmbVisitPayStatus = QtGui.QComboBox(ReportContractsRegistrySetupDialog)
        self.cmbVisitPayStatus.setMinimumSize(QtCore.QSize(252, 0))
        self.cmbVisitPayStatus.setObjectName(_fromUtf8("cmbVisitPayStatus"))
        self.cmbVisitPayStatus.addItem(_fromUtf8(""))
        self.cmbVisitPayStatus.addItem(_fromUtf8(""))
        self.cmbVisitPayStatus.addItem(_fromUtf8(""))
        self.cmbVisitPayStatus.addItem(_fromUtf8(""))
        self.cmbVisitPayStatus.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbVisitPayStatus, 10, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportContractsRegistrySetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 12, 0, 1, 2)

        self.retranslateUi(ReportContractsRegistrySetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportContractsRegistrySetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportContractsRegistrySetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportContractsRegistrySetupDialog)

    def retranslateUi(self, ReportContractsRegistrySetupDialog):
        ReportContractsRegistrySetupDialog.setWindowTitle(_translate("ReportContractsRegistrySetupDialog", "Dialog", None))
        self.lblBegDate.setText(_translate("ReportContractsRegistrySetupDialog", "Дата начала периода", None))
        self.lblBegTime.setText(_translate("ReportContractsRegistrySetupDialog", "Время начала периода", None))
        self.lblEndDate.setText(_translate("ReportContractsRegistrySetupDialog", "Дата окончания периода", None))
        self.lblEndTime.setText(_translate("ReportContractsRegistrySetupDialog", "Время окончания периода", None))
        self.lblOrgStructure.setText(_translate("ReportContractsRegistrySetupDialog", "Подразделение", None))
        self.lblContract.setText(_translate("ReportContractsRegistrySetupDialog", "Договор", None))
        self.lblPerson.setText(_translate("ReportContractsRegistrySetupDialog", "Исполнитель", None))
        self.lblFinance.setText(_translate("ReportContractsRegistrySetupDialog", "Тип финансирования", None))
        self.lblEventType.setText(_translate("ReportContractsRegistrySetupDialog", "Тип обращения", None))
        self.lblVisitPayStatus.setText(_translate("ReportContractsRegistrySetupDialog", "Флаг Финансирования", None))
        self.cmbVisitPayStatus.setItemText(0, _translate("ReportContractsRegistrySetupDialog", "не задано", None))
        self.cmbVisitPayStatus.setItemText(1, _translate("ReportContractsRegistrySetupDialog", "не выставлено", None))
        self.cmbVisitPayStatus.setItemText(2, _translate("ReportContractsRegistrySetupDialog", "выставлено", None))
        self.cmbVisitPayStatus.setItemText(3, _translate("ReportContractsRegistrySetupDialog", "отказано", None))
        self.cmbVisitPayStatus.setItemText(4, _translate("ReportContractsRegistrySetupDialog", "оплачено", None))

from library.crbcombobox import CRBComboBox
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from Orgs.PersonComboBox import CPersonComboBox
from library.TimeEdit import CTimeEdit
from Accounting.ContractComboBox import CContractComboBox
from library.DateEdit import CDateEdit
