# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\RefBooks\RBContainerTypeEditor.ui'
#
# Created: Fri Jun 15 12:17:39 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_RBContainerTypeEditor(object):
    def setupUi(self, RBContainerTypeEditor):
        RBContainerTypeEditor.setObjectName(_fromUtf8("RBContainerTypeEditor"))
        RBContainerTypeEditor.resize(360, 164)
        RBContainerTypeEditor.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(RBContainerTypeEditor)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblCode = QtGui.QLabel(RBContainerTypeEditor)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridLayout.addWidget(self.lblCode, 0, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(RBContainerTypeEditor)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout.addWidget(self.edtCode, 0, 1, 1, 1)
        self.lblName = QtGui.QLabel(RBContainerTypeEditor)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout.addWidget(self.lblName, 1, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(RBContainerTypeEditor)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 1, 1, 1, 1)
        self.lblColor = QtGui.QLabel(RBContainerTypeEditor)
        self.lblColor.setObjectName(_fromUtf8("lblColor"))
        self.gridLayout.addWidget(self.lblColor, 2, 0, 1, 1)
        self.cmbColor = CColorComboBox(RBContainerTypeEditor)
        self.cmbColor.setObjectName(_fromUtf8("cmbColor"))
        self.gridLayout.addWidget(self.cmbColor, 2, 1, 1, 1)
        self.lblAmount = QtGui.QLabel(RBContainerTypeEditor)
        self.lblAmount.setObjectName(_fromUtf8("lblAmount"))
        self.gridLayout.addWidget(self.lblAmount, 3, 0, 1, 1)
        self.edtAmount = QtGui.QDoubleSpinBox(RBContainerTypeEditor)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAmount.sizePolicy().hasHeightForWidth())
        self.edtAmount.setSizePolicy(sizePolicy)
        self.edtAmount.setDecimals(1)
        self.edtAmount.setMaximum(1000.0)
        self.edtAmount.setObjectName(_fromUtf8("edtAmount"))
        self.gridLayout.addWidget(self.edtAmount, 3, 1, 1, 1)
        self.lblUnit = QtGui.QLabel(RBContainerTypeEditor)
        self.lblUnit.setObjectName(_fromUtf8("lblUnit"))
        self.gridLayout.addWidget(self.lblUnit, 4, 0, 1, 1)
        self.cmbUnit = CRBComboBox(RBContainerTypeEditor)
        self.cmbUnit.setObjectName(_fromUtf8("cmbUnit"))
        self.gridLayout.addWidget(self.cmbUnit, 4, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(RBContainerTypeEditor)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 6, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 0, 1, 2)
        self.lblCode.setBuddy(self.edtCode)
        self.lblName.setBuddy(self.edtName)
        self.lblColor.setBuddy(self.cmbColor)
        self.lblAmount.setBuddy(self.edtAmount)
        self.lblUnit.setBuddy(self.cmbUnit)

        self.retranslateUi(RBContainerTypeEditor)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), RBContainerTypeEditor.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), RBContainerTypeEditor.reject)
        QtCore.QMetaObject.connectSlotsByName(RBContainerTypeEditor)

    def retranslateUi(self, RBContainerTypeEditor):
        RBContainerTypeEditor.setWindowTitle(QtGui.QApplication.translate("RBContainerTypeEditor", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCode.setText(QtGui.QApplication.translate("RBContainerTypeEditor", "&Код", None, QtGui.QApplication.UnicodeUTF8))
        self.lblName.setText(QtGui.QApplication.translate("RBContainerTypeEditor", "&Наименование", None, QtGui.QApplication.UnicodeUTF8))
        self.lblColor.setText(QtGui.QApplication.translate("RBContainerTypeEditor", "&Цветовая маркировка", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAmount.setText(QtGui.QApplication.translate("RBContainerTypeEditor", "&Объем", None, QtGui.QApplication.UnicodeUTF8))
        self.lblUnit.setText(QtGui.QApplication.translate("RBContainerTypeEditor", "&Единица измерения", None, QtGui.QApplication.UnicodeUTF8))

from library.crbcombobox import CRBComboBox
from library.ColorEdit import CColorComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    RBContainerTypeEditor = QtGui.QDialog()
    ui = Ui_RBContainerTypeEditor()
    ui.setupUi(RBContainerTypeEditor)
    RBContainerTypeEditor.show()
    sys.exit(app.exec_())

