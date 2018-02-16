# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/craz/s11_local/RefBooks/RBCureMethodEditor.ui'
#
# Created: Mon Mar  4 15:38:53 2013
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
        ItemEditorDialog.resize(301, 126)
        ItemEditorDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(ItemEditorDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.buttonBox = QtGui.QDialogButtonBox(ItemEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 5, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(103, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 4, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridlayout.addWidget(self.edtCode, 0, 1, 1, 1)
        self.edtName = QtGui.QLineEdit(ItemEditorDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridlayout.addWidget(self.edtName, 1, 1, 1, 1)
        self.lblRegionalCode = QtGui.QLabel(ItemEditorDialog)
        self.lblRegionalCode.setObjectName(_fromUtf8("lblRegionalCode"))
        self.gridlayout.addWidget(self.lblRegionalCode, 2, 0, 1, 1)
        self.lblName = QtGui.QLabel(ItemEditorDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridlayout.addWidget(self.lblName, 1, 0, 1, 1)
        self.lblCode = QtGui.QLabel(ItemEditorDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridlayout.addWidget(self.lblCode, 0, 0, 1, 1)
        self.edtRegionalCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtRegionalCode.setObjectName(_fromUtf8("edtRegionalCode"))
        self.gridlayout.addWidget(self.edtRegionalCode, 2, 1, 1, 1)
        self.chkIsObsolete = QtGui.QCheckBox(ItemEditorDialog)
        self.chkIsObsolete.setObjectName(_fromUtf8("chkIsObsolete"))
        self.gridlayout.addWidget(self.chkIsObsolete, 3, 1, 1, 1)
        self.lblRegionalCode.setBuddy(self.edtRegionalCode)
        self.lblName.setBuddy(self.edtName)
        self.lblCode.setBuddy(self.edtCode)

        self.retranslateUi(ItemEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ItemEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ItemEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ItemEditorDialog)
        ItemEditorDialog.setTabOrder(self.edtCode, self.edtName)
        ItemEditorDialog.setTabOrder(self.edtName, self.edtRegionalCode)
        ItemEditorDialog.setTabOrder(self.edtRegionalCode, self.buttonBox)

    def retranslateUi(self, ItemEditorDialog):
        ItemEditorDialog.setWindowTitle(QtGui.QApplication.translate("ItemEditorDialog", "ChangeMe!", None, QtGui.QApplication.UnicodeUTF8))
        self.lblRegionalCode.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Региональный код", None, QtGui.QApplication.UnicodeUTF8))
        self.lblName.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Наименование", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCode.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Код", None, QtGui.QApplication.UnicodeUTF8))
        self.chkIsObsolete.setText(QtGui.QApplication.translate("ItemEditorDialog", "Устаревший", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ItemEditorDialog = QtGui.QDialog()
    ui = Ui_ItemEditorDialog()
    ui.setupUi(ItemEditorDialog)
    ItemEditorDialog.show()
    sys.exit(app.exec_())

