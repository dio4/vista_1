# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\RefBooks\RBNomenclatureTypeEditor.ui'
#
# Created: Fri Jun 15 12:17:18 2012
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
        ItemEditorDialog.resize(320, 147)
        ItemEditorDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ItemEditorDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblClass = QtGui.QLabel(ItemEditorDialog)
        self.lblClass.setObjectName(_fromUtf8("lblClass"))
        self.gridLayout.addWidget(self.lblClass, 0, 0, 1, 1)
        self.cmbClass = CRBComboBox(ItemEditorDialog)
        self.cmbClass.setObjectName(_fromUtf8("cmbClass"))
        self.gridLayout.addWidget(self.cmbClass, 0, 1, 1, 1)
        self.lblCode = QtGui.QLabel(ItemEditorDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridLayout.addWidget(self.lblCode, 2, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout.addWidget(self.edtCode, 2, 1, 1, 1)
        self.lblName = QtGui.QLabel(ItemEditorDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout.addWidget(self.lblName, 3, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(ItemEditorDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 3, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(103, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ItemEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 2)
        self.cmbKind = CRBComboBox(ItemEditorDialog)
        self.cmbKind.setObjectName(_fromUtf8("cmbKind"))
        self.gridLayout.addWidget(self.cmbKind, 1, 1, 1, 1)
        self.lblKind = QtGui.QLabel(ItemEditorDialog)
        self.lblKind.setObjectName(_fromUtf8("lblKind"))
        self.gridLayout.addWidget(self.lblKind, 1, 0, 1, 1)
        self.lblClass.setBuddy(self.cmbClass)
        self.lblCode.setBuddy(self.edtCode)
        self.lblName.setBuddy(self.edtName)
        self.lblKind.setBuddy(self.cmbKind)

        self.retranslateUi(ItemEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ItemEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ItemEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ItemEditorDialog)
        ItemEditorDialog.setTabOrder(self.cmbClass, self.cmbKind)
        ItemEditorDialog.setTabOrder(self.cmbKind, self.edtCode)
        ItemEditorDialog.setTabOrder(self.edtCode, self.edtName)
        ItemEditorDialog.setTabOrder(self.edtName, self.buttonBox)

    def retranslateUi(self, ItemEditorDialog):
        ItemEditorDialog.setWindowTitle(QtGui.QApplication.translate("ItemEditorDialog", "ChangeMe!", None, QtGui.QApplication.UnicodeUTF8))
        self.lblClass.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Класс", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCode.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Код", None, QtGui.QApplication.UnicodeUTF8))
        self.lblName.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Наименование", None, QtGui.QApplication.UnicodeUTF8))
        self.lblKind.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Вид", None, QtGui.QApplication.UnicodeUTF8))

from library.crbcombobox import CRBComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ItemEditorDialog = QtGui.QDialog()
    ui = Ui_ItemEditorDialog()
    ui.setupUi(ItemEditorDialog)
    ItemEditorDialog.show()
    sys.exit(app.exec_())

