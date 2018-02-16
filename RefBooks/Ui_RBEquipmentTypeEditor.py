# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\RefBooks\RBEquipmentTypeEditor.ui'
#
# Created: Fri Jun 15 12:17:45 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_RBEquipmentTypeEditorDialog(object):
    def setupUi(self, RBEquipmentTypeEditorDialog):
        RBEquipmentTypeEditorDialog.setObjectName(_fromUtf8("RBEquipmentTypeEditorDialog"))
        RBEquipmentTypeEditorDialog.resize(414, 125)
        RBEquipmentTypeEditorDialog.setSizeGripEnabled(False)
        self.gridlayout = QtGui.QGridLayout(RBEquipmentTypeEditorDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.buttonBox = QtGui.QDialogButtonBox(RBEquipmentTypeEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 3, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(103, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 2, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(RBEquipmentTypeEditorDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridlayout.addWidget(self.edtCode, 0, 1, 1, 1)
        self.edtName = QtGui.QLineEdit(RBEquipmentTypeEditorDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridlayout.addWidget(self.edtName, 1, 1, 1, 1)
        self.lblCode = QtGui.QLabel(RBEquipmentTypeEditorDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridlayout.addWidget(self.lblCode, 0, 0, 1, 1)
        self.lblName = QtGui.QLabel(RBEquipmentTypeEditorDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridlayout.addWidget(self.lblName, 1, 0, 1, 1)
        self.lblCode.setBuddy(self.edtCode)
        self.lblName.setBuddy(self.edtName)

        self.retranslateUi(RBEquipmentTypeEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), RBEquipmentTypeEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), RBEquipmentTypeEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(RBEquipmentTypeEditorDialog)
        RBEquipmentTypeEditorDialog.setTabOrder(self.edtCode, self.edtName)

    def retranslateUi(self, RBEquipmentTypeEditorDialog):
        RBEquipmentTypeEditorDialog.setWindowTitle(QtGui.QApplication.translate("RBEquipmentTypeEditorDialog", "ChangeMe!", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCode.setText(QtGui.QApplication.translate("RBEquipmentTypeEditorDialog", "&Код", None, QtGui.QApplication.UnicodeUTF8))
        self.lblName.setText(QtGui.QApplication.translate("RBEquipmentTypeEditorDialog", "&Наименование", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    RBEquipmentTypeEditorDialog = QtGui.QDialog()
    ui = Ui_RBEquipmentTypeEditorDialog()
    ui.setupUi(RBEquipmentTypeEditorDialog)
    RBEquipmentTypeEditorDialog.show()
    sys.exit(app.exec_())

