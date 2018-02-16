# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FinanceSummaryByLoadOnDoctorSetupDialog.ui'
#
# Created: Wed Dec  9 17:09:40 2015
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

class Ui_FinanceSummaryByLoadOnDoctorSetupDialog(object):
    def setupUi(self, FinanceSummaryByLoadOnDoctorSetupDialog):
        FinanceSummaryByLoadOnDoctorSetupDialog.setObjectName(_fromUtf8("FinanceSummaryByLoadOnDoctorSetupDialog"))
        FinanceSummaryByLoadOnDoctorSetupDialog.resize(460, 247)
        self.gridLayout = QtGui.QGridLayout(FinanceSummaryByLoadOnDoctorSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblOrgStructure = QtGui.QLabel(FinanceSummaryByLoadOnDoctorSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblOrgStructure.sizePolicy().hasHeightForWidth())
        self.lblOrgStructure.setSizePolicy(sizePolicy)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 4, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(FinanceSummaryByLoadOnDoctorSetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 4, 1, 1, 3)
        self.lblEndDate = QtGui.QLabel(FinanceSummaryByLoadOnDoctorSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblEndDate.sizePolicy().hasHeightForWidth())
        self.lblEndDate.setSizePolicy(sizePolicy)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 2, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(FinanceSummaryByLoadOnDoctorSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 8, 1, 1, 2)
        self.rbtnByActionAmount = QtGui.QRadioButton(FinanceSummaryByLoadOnDoctorSetupDialog)
        self.rbtnByActionAmount.setObjectName(_fromUtf8("rbtnByActionAmount"))
        self.gridLayout.addWidget(self.rbtnByActionAmount, 0, 2, 1, 1)
        self.lblBegDate = QtGui.QLabel(FinanceSummaryByLoadOnDoctorSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblBegDate.sizePolicy().hasHeightForWidth())
        self.lblBegDate.setSizePolicy(sizePolicy)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 1, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(33, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 3, 1, 1)
        self.cmbEventType = CRBComboBox(FinanceSummaryByLoadOnDoctorSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbEventType.sizePolicy().hasHeightForWidth())
        self.cmbEventType.setSizePolicy(sizePolicy)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 5, 1, 1, 3)
        self.lblEventType = QtGui.QLabel(FinanceSummaryByLoadOnDoctorSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblEventType.sizePolicy().hasHeightForWidth())
        self.lblEventType.setSizePolicy(sizePolicy)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridLayout.addWidget(self.lblEventType, 5, 0, 1, 1)
        self.rbtnByMoney = QtGui.QRadioButton(FinanceSummaryByLoadOnDoctorSetupDialog)
        self.rbtnByMoney.setChecked(True)
        self.rbtnByMoney.setObjectName(_fromUtf8("rbtnByMoney"))
        self.gridLayout.addWidget(self.rbtnByMoney, 0, 1, 1, 1)
        self.lblBegDate_2 = QtGui.QLabel(FinanceSummaryByLoadOnDoctorSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblBegDate_2.sizePolicy().hasHeightForWidth())
        self.lblBegDate_2.setSizePolicy(sizePolicy)
        self.lblBegDate_2.setObjectName(_fromUtf8("lblBegDate_2"))
        self.gridLayout.addWidget(self.lblBegDate_2, 0, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 118, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 6, 2, 1, 1)
        self.edtBegDate = QtGui.QDateEdit(FinanceSummaryByLoadOnDoctorSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 1, 1, 1, 1)
        self.edtEndDate = QtGui.QDateEdit(FinanceSummaryByLoadOnDoctorSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 2, 1, 1, 1)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEventType.setBuddy(self.cmbEventType)
        self.lblBegDate_2.setBuddy(self.edtBegDate)

        self.retranslateUi(FinanceSummaryByLoadOnDoctorSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), FinanceSummaryByLoadOnDoctorSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), FinanceSummaryByLoadOnDoctorSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(FinanceSummaryByLoadOnDoctorSetupDialog)

    def retranslateUi(self, FinanceSummaryByLoadOnDoctorSetupDialog):
        FinanceSummaryByLoadOnDoctorSetupDialog.setWindowTitle(_translate("FinanceSummaryByLoadOnDoctorSetupDialog", "параметры отчёта", None))
        self.lblOrgStructure.setText(_translate("FinanceSummaryByLoadOnDoctorSetupDialog", "&Подразделение", None))
        self.lblEndDate.setText(_translate("FinanceSummaryByLoadOnDoctorSetupDialog", "Дата &окончания периода", None))
        self.rbtnByActionAmount.setText(_translate("FinanceSummaryByLoadOnDoctorSetupDialog", "количество услуг", None))
        self.lblBegDate.setText(_translate("FinanceSummaryByLoadOnDoctorSetupDialog", "Дата &начала периода", None))
        self.lblEventType.setText(_translate("FinanceSummaryByLoadOnDoctorSetupDialog", "&Тип обращения", None))
        self.rbtnByMoney.setText(_translate("FinanceSummaryByLoadOnDoctorSetupDialog", "денежные суммы", None))
        self.lblBegDate_2.setText(_translate("FinanceSummaryByLoadOnDoctorSetupDialog", "&Вид отчёта", None))

from library.crbcombobox import CRBComboBox
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
