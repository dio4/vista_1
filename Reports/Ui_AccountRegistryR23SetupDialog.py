# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AccountRegistryR23SetupDialog.ui'
#
# Created: Mon Apr 01 19:22:23 2013
#      by: PyQt4 UI code generator 4.9.6
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

class Ui_AccountRegistryR23Setup(object):
    def setupUi(self, AccountRegistryR23Setup):
        AccountRegistryR23Setup.setObjectName(_fromUtf8("AccountRegistryR23Setup"))
        AccountRegistryR23Setup.resize(359, 184)
        self.gridLayout = QtGui.QGridLayout(AccountRegistryR23Setup)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(AccountRegistryR23Setup)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.cmbInsurerFilterDialog = CInsurerComboBox(AccountRegistryR23Setup)
        self.cmbInsurerFilterDialog.setObjectName(_fromUtf8("cmbInsurerFilterDialog"))
        self.gridLayout.addWidget(self.cmbInsurerFilterDialog, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(AccountRegistryR23Setup)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.cmbOrgStructure = QtGui.QComboBox(AccountRegistryR23Setup)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.cmbOrgStructure.addItem(_fromUtf8(""))
        self.cmbOrgStructure.addItem(_fromUtf8(""))
        self.cmbOrgStructure.addItem(_fromUtf8(""))
        self.cmbOrgStructure.addItem(_fromUtf8(""))
        self.cmbOrgStructure.addItem(_fromUtf8(""))
        self.cmbOrgStructure.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbOrgStructure, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(AccountRegistryR23Setup)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.edtRegistryNumber = QtGui.QLineEdit(AccountRegistryR23Setup)
        self.edtRegistryNumber.setObjectName(_fromUtf8("edtRegistryNumber"))
        self.gridLayout.addWidget(self.edtRegistryNumber, 2, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 37, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(AccountRegistryR23Setup)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 2)

        self.retranslateUi(AccountRegistryR23Setup)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), AccountRegistryR23Setup.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), AccountRegistryR23Setup.reject)
        QtCore.QMetaObject.connectSlotsByName(AccountRegistryR23Setup)

    def retranslateUi(self, AccountRegistryR23Setup):
        AccountRegistryR23Setup.setWindowTitle(_translate("AccountRegistryR23Setup", "Dialog", None))
        self.label.setText(_translate("AccountRegistryR23Setup", "Плательщик", None))
        self.label_2.setText(_translate("AccountRegistryR23Setup", "Подразделение", None))
        self.cmbOrgStructure.setItemText(0, _translate("AccountRegistryR23Setup", "Поликлиника взрослая", None))
        self.cmbOrgStructure.setItemText(1, _translate("AccountRegistryR23Setup", "Поликлиника детская", None))
        self.cmbOrgStructure.setItemText(2, _translate("AccountRegistryR23Setup", "Стационар взрослый", None))
        self.cmbOrgStructure.setItemText(3, _translate("AccountRegistryR23Setup", "Стационар детский", None))
        self.cmbOrgStructure.setItemText(4, _translate("AccountRegistryR23Setup", "Дневной стационар взрослый", None))
        self.cmbOrgStructure.setItemText(5, _translate("AccountRegistryR23Setup", "Дневной стационар детский", None))
        self.label_3.setText(_translate("AccountRegistryR23Setup", "Реестр счета", None))

from Orgs.OrgComboBox import CInsurerComboBox
