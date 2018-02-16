# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RBAttachTypeEditor.ui'
#
# Created: Wed Oct 30 17:16:17 2013
#      by: PyQt4 UI code generator 4.10.3
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
        ItemEditorDialog.resize(320, 178)
        ItemEditorDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(ItemEditorDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.chkOutcome = QtGui.QCheckBox(ItemEditorDialog)
        self.chkOutcome.setObjectName(_fromUtf8("chkOutcome"))
        self.gridlayout.addWidget(self.chkOutcome, 3, 1, 1, 1)
        self.lblCode = QtGui.QLabel(ItemEditorDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridlayout.addWidget(self.lblCode, 0, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridlayout.addWidget(self.edtCode, 0, 1, 1, 1)
        self.cmbFinance = CRBComboBox(ItemEditorDialog)
        self.cmbFinance.setObjectName(_fromUtf8("cmbFinance"))
        self.gridlayout.addWidget(self.cmbFinance, 5, 1, 1, 1)
        self.lblFinance = QtGui.QLabel(ItemEditorDialog)
        self.lblFinance.setObjectName(_fromUtf8("lblFinance"))
        self.gridlayout.addWidget(self.lblFinance, 5, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(ItemEditorDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridlayout.addWidget(self.edtName, 1, 1, 1, 1)
        self.checkBox = QtGui.QCheckBox(ItemEditorDialog)
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.gridlayout.addWidget(self.checkBox, 2, 1, 1, 1)
        self.lblName = QtGui.QLabel(ItemEditorDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridlayout.addWidget(self.lblName, 1, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(103, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 6, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ItemEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 7, 0, 1, 2)
        self.lblGroup = QtGui.QLabel(ItemEditorDialog)
        self.lblGroup.setObjectName(_fromUtf8("lblGroup"))
        self.gridlayout.addWidget(self.lblGroup, 4, 0, 1, 1)
        self.edtGroup = QtGui.QSpinBox(ItemEditorDialog)
        self.edtGroup.setObjectName(_fromUtf8("edtGroup"))
        self.gridlayout.addWidget(self.edtGroup, 4, 1, 1, 1)
        self.lblCode.setBuddy(self.edtCode)
        self.lblFinance.setBuddy(self.cmbFinance)
        self.lblName.setBuddy(self.edtName)
        self.lblGroup.setBuddy(self.edtGroup)

        self.retranslateUi(ItemEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ItemEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ItemEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ItemEditorDialog)
        ItemEditorDialog.setTabOrder(self.edtCode, self.edtName)
        ItemEditorDialog.setTabOrder(self.edtName, self.checkBox)
        ItemEditorDialog.setTabOrder(self.checkBox, self.chkOutcome)
        ItemEditorDialog.setTabOrder(self.chkOutcome, self.edtGroup)
        ItemEditorDialog.setTabOrder(self.edtGroup, self.cmbFinance)
        ItemEditorDialog.setTabOrder(self.cmbFinance, self.buttonBox)

    def retranslateUi(self, ItemEditorDialog):
        ItemEditorDialog.setWindowTitle(_translate("ItemEditorDialog", "ChangeMe!", None))
        self.chkOutcome.setText(_translate("ItemEditorDialog", "Выбытие", None))
        self.lblCode.setText(_translate("ItemEditorDialog", "&Код", None))
        self.lblFinance.setText(_translate("ItemEditorDialog", "&Источник финансирования", None))
        self.checkBox.setText(_translate("ItemEditorDialog", "&Временный", None))
        self.lblName.setText(_translate("ItemEditorDialog", "&Наименование", None))
        self.lblGroup.setText(_translate("ItemEditorDialog", "Группа", None))
        self.edtGroup.setToolTip(_translate("ItemEditorDialog", "Прикрепления с одинаковым номером группы являются взаимоисключающими. При создании нового прикрепления предыдущие действующие прикрепления автоматически открепляются с датой открепления, равной дате нового прикрепления.", None))

from library.crbcombobox import CRBComboBox
