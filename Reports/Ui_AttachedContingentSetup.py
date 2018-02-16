# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AttachedContingentSetup.ui'
#
# Created: Tue Aug 14 18:34:53 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_AttachedContingentSetupDialog(object):
    def setupUi(self, AttachedContingentSetupDialog):
        AttachedContingentSetupDialog.setObjectName(_fromUtf8("AttachedContingentSetupDialog"))
        AttachedContingentSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        AttachedContingentSetupDialog.resize(473, 195)
        AttachedContingentSetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(AttachedContingentSetupDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblEndDate = QtGui.QLabel(AttachedContingentSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 0, 0, 1, 1)
        self.edtEndDate = CDateEdit(AttachedContingentSetupDialog)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 0, 1, 1, 1)
        self.lblAddressOrgStructureType = QtGui.QLabel(AttachedContingentSetupDialog)
        self.lblAddressOrgStructureType.setObjectName(_fromUtf8("lblAddressOrgStructureType"))
        self.gridLayout.addWidget(self.lblAddressOrgStructureType, 4, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(AttachedContingentSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 6, 0, 1, 3)
        self.chkDetailByDepartment = QtGui.QCheckBox(AttachedContingentSetupDialog)
        self.chkDetailByDepartment.setObjectName(_fromUtf8("chkDetailByDepartment"))
        self.gridLayout.addWidget(self.chkDetailByDepartment, 2, 1, 1, 2)
        self.cmbOrgStructure = COrgStructureComboBox(AttachedContingentSetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 1, 1, 1, 2)
        self.lblOrgStructure = QtGui.QLabel(AttachedContingentSetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 1, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(61, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.cmbAddressOrgStructureType = QtGui.QComboBox(AttachedContingentSetupDialog)
        self.cmbAddressOrgStructureType.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbAddressOrgStructureType.sizePolicy().hasHeightForWidth())
        self.cmbAddressOrgStructureType.setSizePolicy(sizePolicy)
        self.cmbAddressOrgStructureType.setObjectName(_fromUtf8("cmbAddressOrgStructureType"))
        self.cmbAddressOrgStructureType.addItem(_fromUtf8(""))
        self.cmbAddressOrgStructureType.addItem(_fromUtf8(""))
        self.cmbAddressOrgStructureType.addItem(_fromUtf8(""))
        self.cmbAddressOrgStructureType.addItem(_fromUtf8(""))
        self.cmbAddressOrgStructureType.addItem(_fromUtf8(""))
        self.cmbAddressOrgStructureType.addItem(_fromUtf8(""))
        self.cmbAddressOrgStructureType.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbAddressOrgStructureType, 4, 1, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 5, 0, 1, 1)
        self.chkDetailByAge = QtGui.QCheckBox(AttachedContingentSetupDialog)
        self.chkDetailByAge.setObjectName(_fromUtf8("chkDetailByAge"))
        self.gridLayout.addWidget(self.chkDetailByAge, 3, 1, 1, 2)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblAddressOrgStructureType.setBuddy(self.cmbAddressOrgStructureType)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)

        self.retranslateUi(AttachedContingentSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), AttachedContingentSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), AttachedContingentSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AttachedContingentSetupDialog)
        AttachedContingentSetupDialog.setTabOrder(self.edtEndDate, self.cmbOrgStructure)
        AttachedContingentSetupDialog.setTabOrder(self.cmbOrgStructure, self.cmbAddressOrgStructureType)
        AttachedContingentSetupDialog.setTabOrder(self.cmbAddressOrgStructureType, self.buttonBox)

    def retranslateUi(self, AttachedContingentSetupDialog):
        AttachedContingentSetupDialog.setWindowTitle(QtGui.QApplication.translate("AttachedContingentSetupDialog", "параметры отчёта", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEndDate.setText(QtGui.QApplication.translate("AttachedContingentSetupDialog", "Дата", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAddressOrgStructureType.setText(QtGui.QApplication.translate("AttachedContingentSetupDialog", "Адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.chkDetailByDepartment.setText(QtGui.QApplication.translate("AttachedContingentSetupDialog", "Детализировать по подразделениям", None, QtGui.QApplication.UnicodeUTF8))
        self.lblOrgStructure.setText(QtGui.QApplication.translate("AttachedContingentSetupDialog", "Подразделение", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbAddressOrgStructureType.setItemText(0, QtGui.QApplication.translate("AttachedContingentSetupDialog", "Регистрация", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbAddressOrgStructureType.setItemText(1, QtGui.QApplication.translate("AttachedContingentSetupDialog", "Проживание", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbAddressOrgStructureType.setItemText(2, QtGui.QApplication.translate("AttachedContingentSetupDialog", "Регистрация или проживание", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbAddressOrgStructureType.setItemText(3, QtGui.QApplication.translate("AttachedContingentSetupDialog", "Прикрепление", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbAddressOrgStructureType.setItemText(4, QtGui.QApplication.translate("AttachedContingentSetupDialog", "Регистрация или прикрепление", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbAddressOrgStructureType.setItemText(5, QtGui.QApplication.translate("AttachedContingentSetupDialog", "Проживание или прикрепление", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbAddressOrgStructureType.setItemText(6, QtGui.QApplication.translate("AttachedContingentSetupDialog", "Регистрация, проживание или прикрепление", None, QtGui.QApplication.UnicodeUTF8))
        self.chkDetailByAge.setText(QtGui.QApplication.translate("AttachedContingentSetupDialog", "Детализировать по возрастам", None, QtGui.QApplication.UnicodeUTF8))

from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
