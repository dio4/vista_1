# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\RefBooks\RBLaboratoryEditor.ui'
#
# Created: Fri Jun 15 12:16:27 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_LaboratoryEditorDialog(object):
    def setupUi(self, LaboratoryEditorDialog):
        LaboratoryEditorDialog.setObjectName(_fromUtf8("LaboratoryEditorDialog"))
        LaboratoryEditorDialog.resize(587, 305)
        LaboratoryEditorDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(LaboratoryEditorDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.lblCode = QtGui.QLabel(LaboratoryEditorDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridlayout.addWidget(self.lblCode, 0, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(LaboratoryEditorDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridlayout.addWidget(self.edtCode, 0, 1, 1, 1)
        self.lblName = QtGui.QLabel(LaboratoryEditorDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridlayout.addWidget(self.lblName, 1, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(LaboratoryEditorDialog)
        self.edtName.setMinimumSize(QtCore.QSize(200, 0))
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridlayout.addWidget(self.edtName, 1, 1, 1, 1)
        self.tblTests = CInDocTableView(LaboratoryEditorDialog)
        self.tblTests.setObjectName(_fromUtf8("tblTests"))
        self.gridlayout.addWidget(self.tblTests, 6, 1, 2, 1)
        self.buttonBox = QtGui.QDialogButtonBox(LaboratoryEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 8, 0, 1, 2)
        self.cmbProtocol = QtGui.QComboBox(LaboratoryEditorDialog)
        self.cmbProtocol.setObjectName(_fromUtf8("cmbProtocol"))
        self.cmbProtocol.addItem(_fromUtf8(""))
        self.cmbProtocol.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbProtocol, 2, 1, 1, 1)
        self.lblProtocol = QtGui.QLabel(LaboratoryEditorDialog)
        self.lblProtocol.setObjectName(_fromUtf8("lblProtocol"))
        self.gridlayout.addWidget(self.lblProtocol, 2, 0, 1, 1)
        self.edtAddress = QtGui.QLineEdit(LaboratoryEditorDialog)
        self.edtAddress.setObjectName(_fromUtf8("edtAddress"))
        self.gridlayout.addWidget(self.edtAddress, 3, 1, 1, 1)
        self.edtOwnName = QtGui.QLineEdit(LaboratoryEditorDialog)
        self.edtOwnName.setObjectName(_fromUtf8("edtOwnName"))
        self.gridlayout.addWidget(self.edtOwnName, 4, 1, 1, 1)
        self.edtLabName = QtGui.QLineEdit(LaboratoryEditorDialog)
        self.edtLabName.setObjectName(_fromUtf8("edtLabName"))
        self.gridlayout.addWidget(self.edtLabName, 5, 1, 1, 1)
        self.lblAddress = QtGui.QLabel(LaboratoryEditorDialog)
        self.lblAddress.setObjectName(_fromUtf8("lblAddress"))
        self.gridlayout.addWidget(self.lblAddress, 3, 0, 1, 1)
        self.lblOwnName = QtGui.QLabel(LaboratoryEditorDialog)
        self.lblOwnName.setObjectName(_fromUtf8("lblOwnName"))
        self.gridlayout.addWidget(self.lblOwnName, 4, 0, 1, 1)
        self.lblLabName = QtGui.QLabel(LaboratoryEditorDialog)
        self.lblLabName.setObjectName(_fromUtf8("lblLabName"))
        self.gridlayout.addWidget(self.lblLabName, 5, 0, 1, 1)
        self.label = QtGui.QLabel(LaboratoryEditorDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridlayout.addWidget(self.label, 6, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 7, 0, 1, 1)
        self.lblCode.setBuddy(self.edtCode)
        self.lblName.setBuddy(self.edtName)
        self.lblProtocol.setBuddy(self.cmbProtocol)
        self.lblAddress.setBuddy(self.edtAddress)
        self.lblOwnName.setBuddy(self.edtOwnName)
        self.lblLabName.setBuddy(self.edtLabName)
        self.label.setBuddy(self.tblTests)

        self.retranslateUi(LaboratoryEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), LaboratoryEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), LaboratoryEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(LaboratoryEditorDialog)
        LaboratoryEditorDialog.setTabOrder(self.edtCode, self.edtName)
        LaboratoryEditorDialog.setTabOrder(self.edtName, self.cmbProtocol)
        LaboratoryEditorDialog.setTabOrder(self.cmbProtocol, self.edtAddress)
        LaboratoryEditorDialog.setTabOrder(self.edtAddress, self.edtOwnName)
        LaboratoryEditorDialog.setTabOrder(self.edtOwnName, self.edtLabName)
        LaboratoryEditorDialog.setTabOrder(self.edtLabName, self.tblTests)
        LaboratoryEditorDialog.setTabOrder(self.tblTests, self.buttonBox)

    def retranslateUi(self, LaboratoryEditorDialog):
        LaboratoryEditorDialog.setWindowTitle(QtGui.QApplication.translate("LaboratoryEditorDialog", "ChangeMe!", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCode.setText(QtGui.QApplication.translate("LaboratoryEditorDialog", "&Код", None, QtGui.QApplication.UnicodeUTF8))
        self.lblName.setText(QtGui.QApplication.translate("LaboratoryEditorDialog", "На&именование", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbProtocol.setItemText(0, QtGui.QApplication.translate("LaboratoryEditorDialog", "hl2.5 через SOAP по предложению AKSi", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbProtocol.setItemText(1, QtGui.QApplication.translate("LaboratoryEditorDialog", "Обмен файлами по ASTM E-1381 и E-1394", None, QtGui.QApplication.UnicodeUTF8))
        self.lblProtocol.setText(QtGui.QApplication.translate("LaboratoryEditorDialog", "&Протокол", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAddress.setText(QtGui.QApplication.translate("LaboratoryEditorDialog", "&Адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.lblOwnName.setText(QtGui.QApplication.translate("LaboratoryEditorDialog", "Наименование &своей стороны", None, QtGui.QApplication.UnicodeUTF8))
        self.lblLabName.setText(QtGui.QApplication.translate("LaboratoryEditorDialog", "Наименование стороны &ЛИС", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("LaboratoryEditorDialog", "Тесты", None, QtGui.QApplication.UnicodeUTF8))

from library.InDocTable import CInDocTableView

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    LaboratoryEditorDialog = QtGui.QDialog()
    ui = Ui_LaboratoryEditorDialog()
    ui.setupUi(LaboratoryEditorDialog)
    LaboratoryEditorDialog.show()
    sys.exit(app.exec_())

