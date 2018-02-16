# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportFinanceSummary.ui'
#
# Created: Fri May 08 17:12:17 2015
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

class Ui_ReportFinanceSummarySetupDialog(object):
    def setupUi(self, ReportFinanceSummarySetupDialog):
        ReportFinanceSummarySetupDialog.setObjectName(_fromUtf8("ReportFinanceSummarySetupDialog"))
        ReportFinanceSummarySetupDialog.resize(507, 624)
        self.gridLayout = QtGui.QGridLayout(ReportFinanceSummarySetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.groupBox = QtGui.QGroupBox(ReportFinanceSummarySetupDialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.edtBegDate = CDateEdit(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout_2.addWidget(self.edtBegDate, 1, 1, 1, 1)
        self.lblBegDate = QtGui.QLabel(self.groupBox)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout_2.addWidget(self.lblBegDate, 1, 0, 1, 1)
        self.edtEndDate = CDateEdit(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout_2.addWidget(self.edtEndDate, 2, 1, 1, 1)
        self.lblEndDate = QtGui.QLabel(self.groupBox)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout_2.addWidget(self.lblEndDate, 2, 0, 1, 1)
        self.rbtnByFormingAccountDate = QtGui.QRadioButton(self.groupBox)
        self.rbtnByFormingAccountDate.setChecked(True)
        self.rbtnByFormingAccountDate.setObjectName(_fromUtf8("rbtnByFormingAccountDate"))
        self.gridLayout_2.addWidget(self.rbtnByFormingAccountDate, 0, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(103, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 1, 2, 1, 1)
        self.rbtnByActionEndDate = QtGui.QRadioButton(self.groupBox)
        self.rbtnByActionEndDate.setObjectName(_fromUtf8("rbtnByActionEndDate"))
        self.gridLayout_2.addWidget(self.rbtnByActionEndDate, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 3)
        self.cmbOrgStruct = COrgStructureComboBox(ReportFinanceSummarySetupDialog)
        self.cmbOrgStruct.setObjectName(_fromUtf8("cmbOrgStruct"))
        self.gridLayout.addWidget(self.cmbOrgStruct, 7, 1, 1, 2)
        self.lblOrgStruct = QtGui.QLabel(ReportFinanceSummarySetupDialog)
        self.lblOrgStruct.setObjectName(_fromUtf8("lblOrgStruct"))
        self.gridLayout.addWidget(self.lblOrgStruct, 7, 0, 1, 1)
        self.lblFinanceType = QtGui.QLabel(ReportFinanceSummarySetupDialog)
        self.lblFinanceType.setObjectName(_fromUtf8("lblFinanceType"))
        self.gridLayout.addWidget(self.lblFinanceType, 1, 0, 1, 1)
        self.cmbFinanceType = CRBComboBox(ReportFinanceSummarySetupDialog)
        self.cmbFinanceType.setObjectName(_fromUtf8("cmbFinanceType"))
        self.gridLayout.addWidget(self.cmbFinanceType, 1, 1, 1, 2)
        self.cmbPerson = CPersonComboBoxEx(ReportFinanceSummarySetupDialog)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.gridLayout.addWidget(self.cmbPerson, 6, 1, 1, 2)
        self.label = QtGui.QLabel(ReportFinanceSummarySetupDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 3, 0, 1, 1)
        self.lblPerson = QtGui.QLabel(ReportFinanceSummarySetupDialog)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridLayout.addWidget(self.lblPerson, 6, 0, 1, 1)
        self.lstItems = CRBListBox(ReportFinanceSummarySetupDialog)
        self.lstItems.setObjectName(_fromUtf8("lstItems"))
        self.gridLayout.addWidget(self.lstItems, 4, 0, 1, 3)
        self.buttonBox = QtGui.QDialogButtonBox(ReportFinanceSummarySetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 10, 2, 1, 1)
        self.lblContract = QtGui.QLabel(ReportFinanceSummarySetupDialog)
        self.lblContract.setObjectName(_fromUtf8("lblContract"))
        self.gridLayout.addWidget(self.lblContract, 8, 0, 1, 1)
        self.lstContracts = CTableView(ReportFinanceSummarySetupDialog)
        self.lstContracts.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.lstContracts.setObjectName(_fromUtf8("lstContracts"))
        self.lstContracts.horizontalHeader().setVisible(True)
        self.gridLayout.addWidget(self.lstContracts, 9, 0, 1, 3)
        self.lblBegDate.setBuddy(self.edtBegDate)

        self.retranslateUi(ReportFinanceSummarySetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportFinanceSummarySetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportFinanceSummarySetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportFinanceSummarySetupDialog)

    def retranslateUi(self, ReportFinanceSummarySetupDialog):
        ReportFinanceSummarySetupDialog.setWindowTitle(_translate("ReportFinanceSummarySetupDialog", "Dialog", None))
        self.groupBox.setTitle(_translate("ReportFinanceSummarySetupDialog", "Период", None))
        self.lblBegDate.setText(_translate("ReportFinanceSummarySetupDialog", "Дата начала периода", None))
        self.lblEndDate.setText(_translate("ReportFinanceSummarySetupDialog", "Дата окончания периода", None))
        self.rbtnByFormingAccountDate.setText(_translate("ReportFinanceSummarySetupDialog", "формирования счета", None))
        self.rbtnByActionEndDate.setText(_translate("ReportFinanceSummarySetupDialog", "выполнения услуги", None))
        self.lblOrgStruct.setText(_translate("ReportFinanceSummarySetupDialog", "Подразделение", None))
        self.lblFinanceType.setText(_translate("ReportFinanceSummarySetupDialog", "Источник финансирования", None))
        self.label.setText(_translate("ReportFinanceSummarySetupDialog", "Типы обращений:", None))
        self.lblPerson.setText(_translate("ReportFinanceSummarySetupDialog", "Врач", None))
        self.lblContract.setText(_translate("ReportFinanceSummarySetupDialog", "Договоры:", None))

from library.crbcombobox import CRBComboBox
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from library.TableView import CTableView
from library.RBListBox import CRBListBox
from library.DateEdit import CDateEdit
