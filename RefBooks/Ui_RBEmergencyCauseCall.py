# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\RefBooks\RBEmergencyCauseCall.ui'
#
# Created: Fri Jun 15 12:16:26 2012
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
        ItemEditorDialog.resize(320, 159)
        ItemEditorDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(ItemEditorDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.buttonBox = QtGui.QDialogButtonBox(ItemEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 6, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(103, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 5, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridlayout.addWidget(self.edtCode, 0, 1, 1, 1)
        self.edtName = QtGui.QLineEdit(ItemEditorDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridlayout.addWidget(self.edtName, 2, 1, 1, 1)
        self.lblName = QtGui.QLabel(ItemEditorDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridlayout.addWidget(self.lblName, 2, 0, 1, 1)
        self.lblCode = QtGui.QLabel(ItemEditorDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridlayout.addWidget(self.lblCode, 0, 0, 1, 1)
        self.lblType = QtGui.QLabel(ItemEditorDialog)
        self.lblType.setObjectName(_fromUtf8("lblType"))
        self.gridlayout.addWidget(self.lblType, 4, 0, 1, 1)
        self.cmbType = QtGui.QComboBox(ItemEditorDialog)
        self.cmbType.setObjectName(_fromUtf8("cmbType"))
        self.cmbType.addItem(_fromUtf8(""))
        self.cmbType.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbType, 4, 1, 1, 1)
        self.edtCodeRegional = QtGui.QLineEdit(ItemEditorDialog)
        self.edtCodeRegional.setObjectName(_fromUtf8("edtCodeRegional"))
        self.gridlayout.addWidget(self.edtCodeRegional, 1, 1, 1, 1)
        self.lblCodeRegional = QtGui.QLabel(ItemEditorDialog)
        self.lblCodeRegional.setObjectName(_fromUtf8("lblCodeRegional"))
        self.gridlayout.addWidget(self.lblCodeRegional, 1, 0, 1, 1)
        self.lblName.setBuddy(self.edtName)
        self.lblCode.setBuddy(self.edtCode)
        self.lblType.setBuddy(self.cmbType)
        self.lblCodeRegional.setBuddy(self.edtCodeRegional)

        self.retranslateUi(ItemEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ItemEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ItemEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ItemEditorDialog)
        ItemEditorDialog.setTabOrder(self.edtCode, self.edtCodeRegional)
        ItemEditorDialog.setTabOrder(self.edtCodeRegional, self.edtName)
        ItemEditorDialog.setTabOrder(self.edtName, self.cmbType)
        ItemEditorDialog.setTabOrder(self.cmbType, self.buttonBox)

    def retranslateUi(self, ItemEditorDialog):
        ItemEditorDialog.setWindowTitle(QtGui.QApplication.translate("ItemEditorDialog", "ChangeMe!", None, QtGui.QApplication.UnicodeUTF8))
        self.lblName.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Наименование", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCode.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Код", None, QtGui.QApplication.UnicodeUTF8))
        self.lblType.setText(QtGui.QApplication.translate("ItemEditorDialog", "Тип", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbType.setItemText(0, QtGui.QApplication.translate("ItemEditorDialog", "вызов", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbType.setItemText(1, QtGui.QApplication.translate("ItemEditorDialog", "обслуживание общ.мероприятия", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCodeRegional.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Региональный код", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ItemEditorDialog = QtGui.QDialog()
    ui = Ui_ItemEditorDialog()
    ui.setupUi(ItemEditorDialog)
    ItemEditorDialog.show()
    sys.exit(app.exec_())

