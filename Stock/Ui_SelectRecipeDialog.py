# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Stock\SelectRecipeDialog.ui'
#
# Created: Fri Jun 15 12:17:17 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(314, 138)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblRecipe = QtGui.QLabel(Dialog)
        self.lblRecipe.setObjectName(_fromUtf8("lblRecipe"))
        self.gridLayout.addWidget(self.lblRecipe, 0, 0, 1, 1)
        self.cmbRecipe = CRBTreeComboBox(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbRecipe.sizePolicy().hasHeightForWidth())
        self.cmbRecipe.setSizePolicy(sizePolicy)
        self.cmbRecipe.setObjectName(_fromUtf8("cmbRecipe"))
        self.gridLayout.addWidget(self.cmbRecipe, 0, 1, 1, 2)
        self.lblRate = QtGui.QLabel(Dialog)
        self.lblRate.setObjectName(_fromUtf8("lblRate"))
        self.gridLayout.addWidget(self.lblRate, 1, 0, 1, 1)
        self.edtRate = QtGui.QDoubleSpinBox(Dialog)
        self.edtRate.setMaximum(999.99)
        self.edtRate.setProperty("value", 1.0)
        self.edtRate.setObjectName(_fromUtf8("edtRate"))
        self.gridLayout.addWidget(self.edtRate, 1, 1, 1, 1)
        self.lblFinance = QtGui.QLabel(Dialog)
        self.lblFinance.setObjectName(_fromUtf8("lblFinance"))
        self.gridLayout.addWidget(self.lblFinance, 2, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(103, 13, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 3)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 2, 1, 1)
        self.cmbFinance = CRBComboBox(Dialog)
        self.cmbFinance.setObjectName(_fromUtf8("cmbFinance"))
        self.gridLayout.addWidget(self.cmbFinance, 2, 1, 1, 2)
        self.lblRecipe.setBuddy(self.cmbRecipe)
        self.lblRate.setBuddy(self.edtRate)
        self.lblFinance.setBuddy(self.cmbFinance)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.cmbRecipe, self.edtRate)
        Dialog.setTabOrder(self.edtRate, self.cmbFinance)
        Dialog.setTabOrder(self.cmbFinance, self.buttonBox)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Укажите рецепт", None, QtGui.QApplication.UnicodeUTF8))
        self.lblRecipe.setText(QtGui.QApplication.translate("Dialog", "&Рецепт", None, QtGui.QApplication.UnicodeUTF8))
        self.lblRate.setText(QtGui.QApplication.translate("Dialog", "&Кратность", None, QtGui.QApplication.UnicodeUTF8))
        self.lblFinance.setText(QtGui.QApplication.translate("Dialog", "Тип &финансирования", None, QtGui.QApplication.UnicodeUTF8))

from library.RBTreeComboBox import CRBTreeComboBox
from library.crbcombobox import CRBComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

