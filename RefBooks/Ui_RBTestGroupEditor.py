# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\RefBooks\RBTestGroupEditor.ui'
#
# Created: Fri Jun 15 12:17:36 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_RBTestGroupEditor(object):
    def setupUi(self, RBTestGroupEditor):
        RBTestGroupEditor.setObjectName(_fromUtf8("RBTestGroupEditor"))
        RBTestGroupEditor.resize(400, 140)
        RBTestGroupEditor.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(RBTestGroupEditor)
        self.gridLayout.setMargin(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblName = QtGui.QLabel(RBTestGroupEditor)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout.addWidget(self.lblName, 0, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(RBTestGroupEditor)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 0, 1, 1, 1)
        self.lblCode = QtGui.QLabel(RBTestGroupEditor)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridLayout.addWidget(self.lblCode, 1, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(RBTestGroupEditor)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout.addWidget(self.edtCode, 1, 1, 1, 1)
        self.lblGroup = QtGui.QLabel(RBTestGroupEditor)
        self.lblGroup.setObjectName(_fromUtf8("lblGroup"))
        self.gridLayout.addWidget(self.lblGroup, 2, 0, 1, 1)
        self.cmbGroup = CRBComboBox(RBTestGroupEditor)
        self.cmbGroup.setObjectName(_fromUtf8("cmbGroup"))
        self.gridLayout.addWidget(self.cmbGroup, 2, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(RBTestGroupEditor)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 1)

        self.retranslateUi(RBTestGroupEditor)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), RBTestGroupEditor.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), RBTestGroupEditor.reject)
        QtCore.QMetaObject.connectSlotsByName(RBTestGroupEditor)

    def retranslateUi(self, RBTestGroupEditor):
        RBTestGroupEditor.setWindowTitle(QtGui.QApplication.translate("RBTestGroupEditor", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.lblName.setText(QtGui.QApplication.translate("RBTestGroupEditor", "Наименование", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCode.setText(QtGui.QApplication.translate("RBTestGroupEditor", "Код", None, QtGui.QApplication.UnicodeUTF8))
        self.lblGroup.setText(QtGui.QApplication.translate("RBTestGroupEditor", "Группа", None, QtGui.QApplication.UnicodeUTF8))

from library.crbcombobox import CRBComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    RBTestGroupEditor = QtGui.QDialog()
    ui = Ui_RBTestGroupEditor()
    ui.setupUi(RBTestGroupEditor)
    RBTestGroupEditor.show()
    sys.exit(app.exec_())

