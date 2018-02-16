# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ExposedServicesReportsSetup.ui'
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

class Ui_ExposedServicesReportsSetupDialog(object):
    def setupUi(self, ExposedServicesReportsSetupDialog):
        ExposedServicesReportsSetupDialog.setObjectName(_fromUtf8("ExposedServicesReportsSetupDialog"))
        ExposedServicesReportsSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ExposedServicesReportsSetupDialog.resize(397, 218)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ExposedServicesReportsSetupDialog.sizePolicy().hasHeightForWidth())
        ExposedServicesReportsSetupDialog.setSizePolicy(sizePolicy)
        ExposedServicesReportsSetupDialog.setMinimumSize(QtCore.QSize(397, 218))
        ExposedServicesReportsSetupDialog.setMaximumSize(QtCore.QSize(397, 218))
        ExposedServicesReportsSetupDialog.setSizeGripEnabled(False)
        self.gridLayout = QtGui.QGridLayout(ExposedServicesReportsSetupDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.grbPeriod = QtGui.QGroupBox(ExposedServicesReportsSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.grbPeriod.sizePolicy().hasHeightForWidth())
        self.grbPeriod.setSizePolicy(sizePolicy)
        self.grbPeriod.setMaximumSize(QtCore.QSize(16777215, 70))
        self.grbPeriod.setObjectName(_fromUtf8("grbPeriod"))
        self.edtBegDate = CDateEdit(self.grbPeriod)
        self.edtBegDate.setGeometry(QtCore.QRect(143, 18, 121, 20))
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.lblEndDate = QtGui.QLabel(self.grbPeriod)
        self.lblEndDate.setGeometry(QtCore.QRect(10, 42, 129, 20))
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.edtEndDate = CDateEdit(self.grbPeriod)
        self.edtEndDate.setGeometry(QtCore.QRect(143, 42, 121, 20))
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.lblBegDate = QtGui.QLabel(self.grbPeriod)
        self.lblBegDate.setGeometry(QtCore.QRect(10, 18, 129, 20))
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.grbPeriod, 0, 1, 1, 1)
        self.wgtCommon = QtGui.QWidget(ExposedServicesReportsSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.wgtCommon.sizePolicy().hasHeightForWidth())
        self.wgtCommon.setSizePolicy(sizePolicy)
        self.wgtCommon.setMaximumSize(QtCore.QSize(400, 100))
        self.wgtCommon.setObjectName(_fromUtf8("wgtCommon"))
        self.gridLayoutWidget_2 = QtGui.QWidget(self.wgtCommon)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(10, 0, 371, 100))
        self.gridLayoutWidget_2.setObjectName(_fromUtf8("gridLayoutWidget_2"))
        self.gridLayout_3 = QtGui.QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.lblContract = QtGui.QLabel(self.gridLayoutWidget_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblContract.sizePolicy().hasHeightForWidth())
        self.lblContract.setSizePolicy(sizePolicy)
        self.lblContract.setObjectName(_fromUtf8("lblContract"))
        self.gridLayout_3.addWidget(self.lblContract, 2, 0, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(self.gridLayoutWidget_2)
        self.lblOrgStructure.setEnabled(True)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout_3.addWidget(self.lblOrgStructure, 0, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(self.gridLayoutWidget_2)
        self.cmbOrgStructure.setEnabled(True)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout_3.addWidget(self.cmbOrgStructure, 0, 1, 1, 1)
        self.cmbContract = CContractComboBox(self.gridLayoutWidget_2)
        self.cmbContract.setObjectName(_fromUtf8("cmbContract"))
        self.gridLayout_3.addWidget(self.cmbContract, 2, 1, 1, 1)
        self.lblFinance = QtGui.QLabel(self.gridLayoutWidget_2)
        self.lblFinance.setObjectName(_fromUtf8("lblFinance"))
        self.gridLayout_3.addWidget(self.lblFinance, 1, 0, 1, 1)
        self.cmbFinance = CRBComboBox(self.gridLayoutWidget_2)
        self.cmbFinance.setObjectName(_fromUtf8("cmbFinance"))
        self.gridLayout_3.addWidget(self.cmbFinance, 1, 1, 1, 1)
        self.cmbEventType = CRBComboBox(self.gridLayoutWidget_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbEventType.sizePolicy().hasHeightForWidth())
        self.cmbEventType.setSizePolicy(sizePolicy)
        self.cmbEventType.setMinimumSize(QtCore.QSize(0, 0))
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout_3.addWidget(self.cmbEventType, 3, 1, 1, 1)
        self.lblEventType = QtGui.QLabel(self.gridLayoutWidget_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblEventType.sizePolicy().hasHeightForWidth())
        self.lblEventType.setSizePolicy(sizePolicy)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridLayout_3.addWidget(self.lblEventType, 3, 0, 1, 1)
        self.gridLayout.addWidget(self.wgtCommon, 5, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ExposedServicesReportsSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 7, 1, 1, 1)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)

        self.retranslateUi(ExposedServicesReportsSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ExposedServicesReportsSetupDialog.reject)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ExposedServicesReportsSetupDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(ExposedServicesReportsSetupDialog)

    def retranslateUi(self, ExposedServicesReportsSetupDialog):
        ExposedServicesReportsSetupDialog.setWindowTitle(_translate("ExposedServicesReportsSetupDialog", "Параметры отчёта", None))
        self.grbPeriod.setTitle(_translate("ExposedServicesReportsSetupDialog", "Период", None))
        self.lblEndDate.setText(_translate("ExposedServicesReportsSetupDialog", "Дата &окончания периода", None))
        self.lblBegDate.setText(_translate("ExposedServicesReportsSetupDialog", "Дата &начала периода", None))
        self.lblContract.setText(_translate("ExposedServicesReportsSetupDialog", "Договор", None))
        self.lblOrgStructure.setText(_translate("ExposedServicesReportsSetupDialog", "Подразделение", None))
        self.lblFinance.setText(_translate("ExposedServicesReportsSetupDialog", "Тип финансирования", None))
        self.lblEventType.setText(_translate("ExposedServicesReportsSetupDialog", "Тип события", None))

from Accounting.ContractComboBox import CContractComboBox
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from library.DateEdit import CDateEdit
from library.crbcombobox import CRBComboBox
