# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\RefBooks\RBBlanksEditor.ui'
#
# Created: Fri Jun 15 12:17:15 2012
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
        ItemEditorDialog.resize(356, 168)
        ItemEditorDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ItemEditorDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblCode = QtGui.QLabel(ItemEditorDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridLayout.addWidget(self.lblCode, 0, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout.addWidget(self.edtCode, 0, 1, 1, 1)
        self.lblName = QtGui.QLabel(ItemEditorDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout.addWidget(self.lblName, 1, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(ItemEditorDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 1, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(103, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ItemEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 6, 0, 1, 2)
        self.lblCheckingSerial = QtGui.QLabel(ItemEditorDialog)
        self.lblCheckingSerial.setObjectName(_fromUtf8("lblCheckingSerial"))
        self.gridLayout.addWidget(self.lblCheckingSerial, 2, 0, 1, 1)
        self.lblCheckingNumber = QtGui.QLabel(ItemEditorDialog)
        self.lblCheckingNumber.setObjectName(_fromUtf8("lblCheckingNumber"))
        self.gridLayout.addWidget(self.lblCheckingNumber, 3, 0, 1, 1)
        self.lblCheckingAmount = QtGui.QLabel(ItemEditorDialog)
        self.lblCheckingAmount.setObjectName(_fromUtf8("lblCheckingAmount"))
        self.gridLayout.addWidget(self.lblCheckingAmount, 4, 0, 1, 1)
        self.cmbCheckingSerial = QtGui.QComboBox(ItemEditorDialog)
        self.cmbCheckingSerial.setObjectName(_fromUtf8("cmbCheckingSerial"))
        self.cmbCheckingSerial.addItem(_fromUtf8(""))
        self.cmbCheckingSerial.addItem(_fromUtf8(""))
        self.cmbCheckingSerial.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbCheckingSerial, 2, 1, 1, 1)
        self.cmbCheckingNumber = QtGui.QComboBox(ItemEditorDialog)
        self.cmbCheckingNumber.setObjectName(_fromUtf8("cmbCheckingNumber"))
        self.cmbCheckingNumber.addItem(_fromUtf8(""))
        self.cmbCheckingNumber.addItem(_fromUtf8(""))
        self.cmbCheckingNumber.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbCheckingNumber, 3, 1, 1, 1)
        self.cmbCheckingAmount = QtGui.QComboBox(ItemEditorDialog)
        self.cmbCheckingAmount.setObjectName(_fromUtf8("cmbCheckingAmount"))
        self.cmbCheckingAmount.addItem(_fromUtf8(""))
        self.cmbCheckingAmount.addItem(_fromUtf8(""))
        self.cmbCheckingAmount.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbCheckingAmount, 4, 1, 1, 1)
        self.lblCode.setBuddy(self.edtCode)
        self.lblName.setBuddy(self.edtName)
        self.lblCheckingSerial.setBuddy(self.cmbCheckingSerial)
        self.lblCheckingNumber.setBuddy(self.cmbCheckingNumber)
        self.lblCheckingAmount.setBuddy(self.cmbCheckingAmount)

        self.retranslateUi(ItemEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ItemEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ItemEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ItemEditorDialog)
        ItemEditorDialog.setTabOrder(self.edtCode, self.edtName)
        ItemEditorDialog.setTabOrder(self.edtName, self.buttonBox)

    def retranslateUi(self, ItemEditorDialog):
        ItemEditorDialog.setWindowTitle(QtGui.QApplication.translate("ItemEditorDialog", "ChangeMe!", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCode.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Код", None, QtGui.QApplication.UnicodeUTF8))
        self.lblName.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Наименование", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCheckingSerial.setText(QtGui.QApplication.translate("ItemEditorDialog", "Контроль &серии", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCheckingNumber.setText(QtGui.QApplication.translate("ItemEditorDialog", "Контроль но&мера", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCheckingAmount.setText(QtGui.QApplication.translate("ItemEditorDialog", "Контроль &количества", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbCheckingSerial.setItemText(0, QtGui.QApplication.translate("ItemEditorDialog", "нет", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbCheckingSerial.setItemText(1, QtGui.QApplication.translate("ItemEditorDialog", "мягко", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbCheckingSerial.setItemText(2, QtGui.QApplication.translate("ItemEditorDialog", "жестко", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbCheckingNumber.setItemText(0, QtGui.QApplication.translate("ItemEditorDialog", "нет", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbCheckingNumber.setItemText(1, QtGui.QApplication.translate("ItemEditorDialog", "мягко", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbCheckingNumber.setItemText(2, QtGui.QApplication.translate("ItemEditorDialog", "жестко", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbCheckingAmount.setItemText(0, QtGui.QApplication.translate("ItemEditorDialog", "нет", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbCheckingAmount.setItemText(1, QtGui.QApplication.translate("ItemEditorDialog", "мягко", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbCheckingAmount.setItemText(2, QtGui.QApplication.translate("ItemEditorDialog", "жестко", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ItemEditorDialog = QtGui.QDialog()
    ui = Ui_ItemEditorDialog()
    ui.setupUi(ItemEditorDialog)
    ItemEditorDialog.show()
    sys.exit(app.exec_())

