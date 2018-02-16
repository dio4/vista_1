# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/hikarido/Documents/forge/VistaMad/s11/Orgs/OrgFilterDialog.ui'
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

class Ui_OrgFilterDialog(object):
    def setupUi(self, OrgFilterDialog):
        OrgFilterDialog.setObjectName(_fromUtf8("OrgFilterDialog"))
        OrgFilterDialog.resize(286, 288)
        self.gridlayout = QtGui.QGridLayout(OrgFilterDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 9, 0, 1, 1)
        self.lblName = QtGui.QLabel(OrgFilterDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridlayout.addWidget(self.lblName, 0, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(OrgFilterDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridlayout.addWidget(self.edtName, 0, 1, 1, 1)
        self.lblInfis = QtGui.QLabel(OrgFilterDialog)
        self.lblInfis.setObjectName(_fromUtf8("lblInfis"))
        self.gridlayout.addWidget(self.lblInfis, 3, 0, 1, 1)
        self.edtINN = QtGui.QLineEdit(OrgFilterDialog)
        self.edtINN.setObjectName(_fromUtf8("edtINN"))
        self.gridlayout.addWidget(self.edtINN, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(OrgFilterDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 10, 0, 1, 2)
        self.lblINN = QtGui.QLabel(OrgFilterDialog)
        self.lblINN.setObjectName(_fromUtf8("lblINN"))
        self.gridlayout.addWidget(self.lblINN, 1, 0, 1, 1)
        self.edtInfis = QtGui.QLineEdit(OrgFilterDialog)
        self.edtInfis.setObjectName(_fromUtf8("edtInfis"))
        self.gridlayout.addWidget(self.edtInfis, 3, 1, 1, 1)
        self.lblOGRN = QtGui.QLabel(OrgFilterDialog)
        self.lblOGRN.setObjectName(_fromUtf8("lblOGRN"))
        self.gridlayout.addWidget(self.lblOGRN, 2, 0, 1, 1)
        self.edtOGRN = QtGui.QLineEdit(OrgFilterDialog)
        self.edtOGRN.setObjectName(_fromUtf8("edtOGRN"))
        self.gridlayout.addWidget(self.edtOGRN, 2, 1, 1, 1)
        self.lblOKVED = QtGui.QLabel(OrgFilterDialog)
        self.lblOKVED.setObjectName(_fromUtf8("lblOKVED"))
        self.gridlayout.addWidget(self.lblOKVED, 4, 0, 1, 1)
        self.edtOKVED = QtGui.QLineEdit(OrgFilterDialog)
        self.edtOKVED.setObjectName(_fromUtf8("edtOKVED"))
        self.gridlayout.addWidget(self.edtOKVED, 4, 1, 1, 1)
        self.cmbIsInsurer = QtGui.QComboBox(OrgFilterDialog)
        self.cmbIsInsurer.setObjectName(_fromUtf8("cmbIsInsurer"))
        self.cmbIsInsurer.addItem(_fromUtf8(""))
        self.cmbIsInsurer.addItem(_fromUtf8(""))
        self.cmbIsInsurer.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbIsInsurer, 6, 1, 1, 1)
        self.lblIsInsurer = QtGui.QLabel(OrgFilterDialog)
        self.lblIsInsurer.setObjectName(_fromUtf8("lblIsInsurer"))
        self.gridlayout.addWidget(self.lblIsInsurer, 6, 0, 1, 1)
        self.edtmiacCode = QtGui.QLineEdit(OrgFilterDialog)
        self.edtmiacCode.setObjectName(_fromUtf8("edtmiacCode"))
        self.gridlayout.addWidget(self.edtmiacCode, 5, 1, 1, 1)
        self.chkLocalsOnly = QtGui.QCheckBox(OrgFilterDialog)
        self.chkLocalsOnly.setChecked(True)
        self.chkLocalsOnly.setObjectName(_fromUtf8("chkLocalsOnly"))
        self.gridlayout.addWidget(self.chkLocalsOnly, 7, 0, 1, 2)
        self.lblmiacCode = QtGui.QLabel(OrgFilterDialog)
        self.lblmiacCode.setObjectName(_fromUtf8("lblmiacCode"))
        self.gridlayout.addWidget(self.lblmiacCode, 5, 0, 1, 1)
        self.chkActiveOnly = QtGui.QCheckBox(OrgFilterDialog)
        self.chkActiveOnly.setObjectName(_fromUtf8("chkActiveOnly"))
        self.gridlayout.addWidget(self.chkActiveOnly, 8, 0, 1, 1)
        self.lblName.setBuddy(self.edtName)
        self.lblInfis.setBuddy(self.edtInfis)
        self.lblINN.setBuddy(self.edtINN)
        self.lblOGRN.setBuddy(self.edtOGRN)
        self.lblOKVED.setBuddy(self.edtOKVED)
        self.lblIsInsurer.setBuddy(self.cmbIsInsurer)

        self.retranslateUi(OrgFilterDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), OrgFilterDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), OrgFilterDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(OrgFilterDialog)
        OrgFilterDialog.setTabOrder(self.edtName, self.edtINN)
        OrgFilterDialog.setTabOrder(self.edtINN, self.edtOGRN)
        OrgFilterDialog.setTabOrder(self.edtOGRN, self.edtInfis)
        OrgFilterDialog.setTabOrder(self.edtInfis, self.edtOKVED)
        OrgFilterDialog.setTabOrder(self.edtOKVED, self.cmbIsInsurer)
        OrgFilterDialog.setTabOrder(self.cmbIsInsurer, self.buttonBox)

    def retranslateUi(self, OrgFilterDialog):
        OrgFilterDialog.setWindowTitle(_translate("OrgFilterDialog", "Выбор организации", None))
        self.lblName.setText(_translate("OrgFilterDialog", "&Название содержит", None))
        self.lblInfis.setText(_translate("OrgFilterDialog", "Код ИН&ФИС", None))
        self.lblINN.setText(_translate("OrgFilterDialog", "&ИНН", None))
        self.lblOGRN.setText(_translate("OrgFilterDialog", "&ОГРН", None))
        self.lblOKVED.setText(_translate("OrgFilterDialog", "ОКВЭ&Д", None))
        self.cmbIsInsurer.setItemText(0, _translate("OrgFilterDialog", "не задано", None))
        self.cmbIsInsurer.setItemText(1, _translate("OrgFilterDialog", "Нет", None))
        self.cmbIsInsurer.setItemText(2, _translate("OrgFilterDialog", "Да", None))
        self.lblIsInsurer.setText(_translate("OrgFilterDialog", "&Страховая компания", None))
        self.chkLocalsOnly.setText(_translate("OrgFilterDialog", "Только местные МО", None))
        self.lblmiacCode.setText(_translate("OrgFilterDialog", "МИАЦ", None))
        self.chkActiveOnly.setText(_translate("OrgFilterDialog", "Только действующие", None))

