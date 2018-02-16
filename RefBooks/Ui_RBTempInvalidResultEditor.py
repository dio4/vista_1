# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\RefBooks\RBTempInvalidResultEditor.ui'
#
# Created: Fri Jun 15 12:15:46 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ItemEditorDialog(object):
    def setupUi(self, ItemEditorDialog):
        ItemEditorDialog.setObjectName(_fromUtf8("ItemEditorDialog"))
        ItemEditorDialog.resize(304, 198)
        ItemEditorDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ItemEditorDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblType = QtGui.QLabel(ItemEditorDialog)
        self.lblType.setObjectName(_fromUtf8("lblType"))
        self.gridLayout.addWidget(self.lblType, 0, 0, 1, 1)
        self.cmbType = QtGui.QComboBox(ItemEditorDialog)
        self.cmbType.setObjectName(_fromUtf8("cmbType"))
        self.gridLayout.addWidget(self.cmbType, 0, 1, 1, 1)
        self.lblCode = QtGui.QLabel(ItemEditorDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridLayout.addWidget(self.lblCode, 1, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout.addWidget(self.edtCode, 1, 1, 1, 1)
        self.lblName = QtGui.QLabel(ItemEditorDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout.addWidget(self.lblName, 2, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(ItemEditorDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 2, 1, 1, 1)
        self.lblClosed = QtGui.QLabel(ItemEditorDialog)
        self.lblClosed.setObjectName(_fromUtf8("lblClosed"))
        self.gridLayout.addWidget(self.lblClosed, 3, 0, 1, 1)
        self.cmbClosed = QtGui.QComboBox(ItemEditorDialog)
        self.cmbClosed.setObjectName(_fromUtf8("cmbClosed"))
        self.cmbClosed.addItem(_fromUtf8(""))
        self.cmbClosed.addItem(_fromUtf8(""))
        self.cmbClosed.addItem(_fromUtf8(""))
        self.cmbClosed.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbClosed, 3, 1, 1, 1)
        self.lblStatus = QtGui.QLabel(ItemEditorDialog)
        self.lblStatus.setObjectName(_fromUtf8("lblStatus"))
        self.gridLayout.addWidget(self.lblStatus, 4, 0, 1, 1)
        self.cmbStatus = QtGui.QComboBox(ItemEditorDialog)
        self.cmbStatus.setObjectName(_fromUtf8("cmbStatus"))
        self.cmbStatus.addItem(_fromUtf8(""))
        self.cmbStatus.setItemText(0, _fromUtf8(""))
        self.cmbStatus.addItem(_fromUtf8(""))
        self.cmbStatus.addItem(_fromUtf8(""))
        self.cmbStatus.addItem(_fromUtf8(""))
        self.cmbStatus.addItem(_fromUtf8(""))
        self.cmbStatus.addItem(_fromUtf8(""))
        self.cmbStatus.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbStatus, 4, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(103, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ItemEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 6, 0, 1, 2)
        self.lblType.setBuddy(self.cmbType)
        self.lblCode.setBuddy(self.edtCode)
        self.lblName.setBuddy(self.edtName)
        self.lblClosed.setBuddy(self.cmbClosed)
        self.lblStatus.setBuddy(self.cmbStatus)

        self.retranslateUi(ItemEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ItemEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ItemEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ItemEditorDialog)
        ItemEditorDialog.setTabOrder(self.cmbType, self.edtCode)
        ItemEditorDialog.setTabOrder(self.edtCode, self.edtName)
        ItemEditorDialog.setTabOrder(self.edtName, self.cmbClosed)
        ItemEditorDialog.setTabOrder(self.cmbClosed, self.cmbStatus)
        ItemEditorDialog.setTabOrder(self.cmbStatus, self.buttonBox)

    def retranslateUi(self, ItemEditorDialog):
        ItemEditorDialog.setWindowTitle(QtGui.QApplication.translate("ItemEditorDialog", "ChangeMe!", None, QtGui.QApplication.UnicodeUTF8))
        self.lblType.setText(QtGui.QApplication.translate("ItemEditorDialog", "К&ласс", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCode.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Код", None, QtGui.QApplication.UnicodeUTF8))
        self.lblName.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Наименование", None, QtGui.QApplication.UnicodeUTF8))
        self.lblClosed.setText(QtGui.QApplication.translate("ItemEditorDialog", "Состояние документа", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbClosed.setItemText(0, QtGui.QApplication.translate("ItemEditorDialog", "открыт", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbClosed.setItemText(1, QtGui.QApplication.translate("ItemEditorDialog", "закрыт", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbClosed.setItemText(2, QtGui.QApplication.translate("ItemEditorDialog", "продлён", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbClosed.setItemText(3, QtGui.QApplication.translate("ItemEditorDialog", "передан", None, QtGui.QApplication.UnicodeUTF8))
        self.lblStatus.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Статус", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbStatus.setItemText(1, QtGui.QApplication.translate("ItemEditorDialog", "Направление на КЭК", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbStatus.setItemText(2, QtGui.QApplication.translate("ItemEditorDialog", "Решение КЭК", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbStatus.setItemText(3, QtGui.QApplication.translate("ItemEditorDialog", "Направление на МСЭ", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbStatus.setItemText(4, QtGui.QApplication.translate("ItemEditorDialog", "Решение МСЭ", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbStatus.setItemText(5, QtGui.QApplication.translate("ItemEditorDialog", "Госпитализация", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbStatus.setItemText(6, QtGui.QApplication.translate("ItemEditorDialog", "Сан.кур.лечение", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ItemEditorDialog = QtGui.QDialog()
    ui = Ui_ItemEditorDialog()
    ui.setupUi(ItemEditorDialog)
    ItemEditorDialog.show()
    sys.exit(app.exec_())

