# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RBAccountingSystemEditor.ui'
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

class Ui_ItemEditorDialog(object):
    def setupUi(self, ItemEditorDialog):
        ItemEditorDialog.setObjectName(_fromUtf8("ItemEditorDialog"))
        ItemEditorDialog.resize(374, 227)
        ItemEditorDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(ItemEditorDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.chkEditable = QtGui.QCheckBox(ItemEditorDialog)
        self.chkEditable.setObjectName(_fromUtf8("chkEditable"))
        self.gridlayout.addWidget(self.chkEditable, 3, 1, 1, 1)
        self.chkShowInClientInfo = QtGui.QCheckBox(ItemEditorDialog)
        self.chkShowInClientInfo.setObjectName(_fromUtf8("chkShowInClientInfo"))
        self.gridlayout.addWidget(self.chkShowInClientInfo, 4, 1, 1, 1)
        self.chkIsUnique = QtGui.QCheckBox(ItemEditorDialog)
        self.chkIsUnique.setObjectName(_fromUtf8("chkIsUnique"))
        self.gridlayout.addWidget(self.chkIsUnique, 5, 1, 1, 1)
        self.lblCode = QtGui.QLabel(ItemEditorDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridlayout.addWidget(self.lblCode, 0, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(ItemEditorDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridlayout.addWidget(self.edtName, 1, 1, 1, 1)
        self.edtCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtCode.setMaxLength(8)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridlayout.addWidget(self.edtCode, 0, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(103, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 7, 0, 1, 1)
        self.lblName = QtGui.QLabel(ItemEditorDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridlayout.addWidget(self.lblName, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ItemEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 8, 0, 1, 2)
        self.cmbCounter = CRBComboBox(ItemEditorDialog)
        self.cmbCounter.setObjectName(_fromUtf8("cmbCounter"))
        self.gridlayout.addWidget(self.cmbCounter, 2, 1, 1, 1)
        self.label = QtGui.QLabel(ItemEditorDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridlayout.addWidget(self.label, 2, 0, 1, 1)
        self.chkAutoIdentificator = QtGui.QCheckBox(ItemEditorDialog)
        self.chkAutoIdentificator.setObjectName(_fromUtf8("chkAutoIdentificator"))
        self.gridlayout.addWidget(self.chkAutoIdentificator, 6, 1, 1, 1)
        self.lblCode.setBuddy(self.edtCode)
        self.lblName.setBuddy(self.edtName)
        self.label.setBuddy(self.cmbCounter)

        self.retranslateUi(ItemEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ItemEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ItemEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ItemEditorDialog)
        ItemEditorDialog.setTabOrder(self.edtCode, self.edtName)
        ItemEditorDialog.setTabOrder(self.edtName, self.cmbCounter)
        ItemEditorDialog.setTabOrder(self.cmbCounter, self.chkEditable)
        ItemEditorDialog.setTabOrder(self.chkEditable, self.chkShowInClientInfo)
        ItemEditorDialog.setTabOrder(self.chkShowInClientInfo, self.chkIsUnique)
        ItemEditorDialog.setTabOrder(self.chkIsUnique, self.buttonBox)

    def retranslateUi(self, ItemEditorDialog):
        ItemEditorDialog.setWindowTitle(_translate("ItemEditorDialog", "ChangeMe!", None))
        self.chkEditable.setText(_translate("ItemEditorDialog", "&Разрешать изменение", None))
        self.chkShowInClientInfo.setText(_translate("ItemEditorDialog", "Отображать в информации о пациенте", None))
        self.chkIsUnique.setText(_translate("ItemEditorDialog", "Требует ввод уникального значения", None))
        self.lblCode.setText(_translate("ItemEditorDialog", "&Код", None))
        self.lblName.setText(_translate("ItemEditorDialog", "&Наименование", None))
        self.label.setText(_translate("ItemEditorDialog", "Счетчик", None))
        self.chkAutoIdentificator.setText(_translate("ItemEditorDialog", "Автоматическое добавление идентификатора", None))

from library.crbcombobox import CRBComboBox
