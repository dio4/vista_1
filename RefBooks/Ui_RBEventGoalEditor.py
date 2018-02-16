# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RBEventGoalEditor.ui'
#
# Created: Wed Jan 21 16:42:18 2015
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

class Ui_ItemEditorDialog(object):
    def setupUi(self, ItemEditorDialog):
        ItemEditorDialog.setObjectName(_fromUtf8("ItemEditorDialog"))
        ItemEditorDialog.resize(358, 227)
        ItemEditorDialog.setSizeGripEnabled(False)
        self.gridlayout = QtGui.QGridLayout(ItemEditorDialog)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setMargin(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.lblStrictVisitCount = QtGui.QLabel(ItemEditorDialog)
        self.lblStrictVisitCount.setObjectName(_fromUtf8("lblStrictVisitCount"))
        self.gridlayout.addWidget(self.lblStrictVisitCount, 5, 1, 1, 1)
        self.lblRegionalCode = QtGui.QLabel(ItemEditorDialog)
        self.lblRegionalCode.setObjectName(_fromUtf8("lblRegionalCode"))
        self.gridlayout.addWidget(self.lblRegionalCode, 1, 1, 1, 1)
        self.lblFederalCode = QtGui.QLabel(ItemEditorDialog)
        self.lblFederalCode.setObjectName(_fromUtf8("lblFederalCode"))
        self.gridlayout.addWidget(self.lblFederalCode, 2, 1, 1, 1)
        self.edtFederalCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtFederalCode.setObjectName(_fromUtf8("edtFederalCode"))
        self.gridlayout.addWidget(self.edtFederalCode, 2, 2, 1, 2)
        spacerItem = QtGui.QSpacerItem(307, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 8, 1, 1, 4)
        self.buttonBox = QtGui.QDialogButtonBox(ItemEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 9, 1, 1, 4)
        spacerItem1 = QtGui.QSpacerItem(131, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem1, 1, 4, 1, 1)
        self.edtName = QtGui.QLineEdit(ItemEditorDialog)
        self.edtName.setMaxLength(64)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridlayout.addWidget(self.edtName, 3, 2, 1, 3)
        self.lblCode = QtGui.QLabel(ItemEditorDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridlayout.addWidget(self.lblCode, 0, 1, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(131, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem2, 0, 4, 1, 1)
        self.edtCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtCode.setMaxLength(8)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridlayout.addWidget(self.edtCode, 0, 2, 1, 2)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem3, 2, 4, 1, 1)
        self.cmbPurpose = CRBComboBox(ItemEditorDialog)
        self.cmbPurpose.setObjectName(_fromUtf8("cmbPurpose"))
        self.gridlayout.addWidget(self.cmbPurpose, 6, 2, 1, 2)
        self.label = QtGui.QLabel(ItemEditorDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridlayout.addWidget(self.label, 6, 1, 1, 1)
        self.lblName = QtGui.QLabel(ItemEditorDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridlayout.addWidget(self.lblName, 3, 1, 1, 1)
        self.edtRegionalCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtRegionalCode.setMaxLength(8)
        self.edtRegionalCode.setObjectName(_fromUtf8("edtRegionalCode"))
        self.gridlayout.addWidget(self.edtRegionalCode, 1, 2, 1, 2)
        self.edtVisitCount = QtGui.QLineEdit(ItemEditorDialog)
        self.edtVisitCount.setObjectName(_fromUtf8("edtVisitCount"))
        self.gridlayout.addWidget(self.edtVisitCount, 5, 2, 1, 1)
        self.lblRegionalCode.setBuddy(self.edtRegionalCode)
        self.lblFederalCode.setBuddy(self.edtFederalCode)
        self.lblCode.setBuddy(self.edtCode)
        self.lblName.setBuddy(self.edtName)

        self.retranslateUi(ItemEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ItemEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ItemEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ItemEditorDialog)
        ItemEditorDialog.setTabOrder(self.edtCode, self.edtRegionalCode)
        ItemEditorDialog.setTabOrder(self.edtRegionalCode, self.edtFederalCode)
        ItemEditorDialog.setTabOrder(self.edtFederalCode, self.edtName)
        ItemEditorDialog.setTabOrder(self.edtName, self.cmbPurpose)
        ItemEditorDialog.setTabOrder(self.cmbPurpose, self.buttonBox)

    def retranslateUi(self, ItemEditorDialog):
        ItemEditorDialog.setWindowTitle(_translate("ItemEditorDialog", "ChangeMe!", None))
        self.lblStrictVisitCount.setText(_translate("ItemEditorDialog", "Количество посещений", None))
        self.lblRegionalCode.setText(_translate("ItemEditorDialog", "&Региональный код", None))
        self.lblFederalCode.setText(_translate("ItemEditorDialog", "&Федеральный код", None))
        self.lblCode.setText(_translate("ItemEditorDialog", "&Код", None))
        self.label.setText(_translate("ItemEditorDialog", "Назначение типа события", None))
        self.lblName.setText(_translate("ItemEditorDialog", "&Наименование", None))
        self.edtVisitCount.setInputMask(_translate("ItemEditorDialog", "000-000", None))
        self.edtVisitCount.setText(_translate("ItemEditorDialog", "-", None))

from library.crbcombobox import CRBComboBox
