# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\RefBooks\RBDiseaseStageEditor.ui'
#
# Created: Fri Jun 15 12:15:41 2012
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
        ItemEditorDialog.resize(378, 114)
        ItemEditorDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(ItemEditorDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.edtCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridlayout.addWidget(self.edtCode, 0, 1, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ItemEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 4, 0, 1, 3)
        self.lblCode = QtGui.QLabel(ItemEditorDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridlayout.addWidget(self.lblCode, 0, 0, 1, 1)
        self.lblName = QtGui.QLabel(ItemEditorDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridlayout.addWidget(self.lblName, 1, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(ItemEditorDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridlayout.addWidget(self.edtName, 1, 1, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 3, 0, 1, 1)
        self.cmbCharacterRelation = QtGui.QComboBox(ItemEditorDialog)
        self.cmbCharacterRelation.setObjectName(_fromUtf8("cmbCharacterRelation"))
        self.cmbCharacterRelation.addItem(_fromUtf8(""))
        self.cmbCharacterRelation.addItem(_fromUtf8(""))
        self.cmbCharacterRelation.addItem(_fromUtf8(""))
        self.cmbCharacterRelation.addItem(_fromUtf8(""))
        self.cmbCharacterRelation.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbCharacterRelation, 2, 1, 1, 2)
        self.lblCharacterRelation = QtGui.QLabel(ItemEditorDialog)
        self.lblCharacterRelation.setObjectName(_fromUtf8("lblCharacterRelation"))
        self.gridlayout.addWidget(self.lblCharacterRelation, 2, 0, 1, 1)
        self.lblCode.setBuddy(self.edtCode)
        self.lblName.setBuddy(self.edtName)
        self.lblCharacterRelation.setBuddy(self.cmbCharacterRelation)

        self.retranslateUi(ItemEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ItemEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ItemEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ItemEditorDialog)
        ItemEditorDialog.setTabOrder(self.edtCode, self.edtName)
        ItemEditorDialog.setTabOrder(self.edtName, self.cmbCharacterRelation)
        ItemEditorDialog.setTabOrder(self.cmbCharacterRelation, self.buttonBox)

    def retranslateUi(self, ItemEditorDialog):
        ItemEditorDialog.setWindowTitle(QtGui.QApplication.translate("ItemEditorDialog", "ChangeMe!", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCode.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Код", None, QtGui.QApplication.UnicodeUTF8))
        self.lblName.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Наименование", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbCharacterRelation.setItemText(0, QtGui.QApplication.translate("ItemEditorDialog", "нет связи", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbCharacterRelation.setItemText(1, QtGui.QApplication.translate("ItemEditorDialog", "только для острых", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbCharacterRelation.setItemText(2, QtGui.QApplication.translate("ItemEditorDialog", "только для хронических", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbCharacterRelation.setItemText(3, QtGui.QApplication.translate("ItemEditorDialog", "для острых и хронических (но не для Z-к)", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbCharacterRelation.setItemText(4, QtGui.QApplication.translate("ItemEditorDialog", "только для Z-к", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCharacterRelation.setText(QtGui.QApplication.translate("ItemEditorDialog", "Связь с &характером", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ItemEditorDialog = QtGui.QDialog()
    ui = Ui_ItemEditorDialog()
    ui.setupUi(ItemEditorDialog)
    ItemEditorDialog.show()
    sys.exit(app.exec_())

