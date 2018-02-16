# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\RefBooks\KLADRMilitaryUnitsFilterDialog.ui'
#
# Created: Fri Jun 15 12:16:46 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ItemFilterDialog(object):
    def setupUi(self, ItemFilterDialog):
        ItemFilterDialog.setObjectName(_fromUtf8("ItemFilterDialog"))
        ItemFilterDialog.resize(400, 73)
        self.gridLayout = QtGui.QGridLayout(ItemFilterDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblNameTemplate = QtGui.QLabel(ItemFilterDialog)
        self.lblNameTemplate.setObjectName(_fromUtf8("lblNameTemplate"))
        self.gridLayout.addWidget(self.lblNameTemplate, 0, 0, 1, 1)
        self.edtNameTemplate = QtGui.QLineEdit(ItemFilterDialog)
        self.edtNameTemplate.setObjectName(_fromUtf8("edtNameTemplate"))
        self.gridLayout.addWidget(self.edtNameTemplate, 0, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ItemFilterDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)

        self.retranslateUi(ItemFilterDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ItemFilterDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ItemFilterDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ItemFilterDialog)

    def retranslateUi(self, ItemFilterDialog):
        ItemFilterDialog.setWindowTitle(QtGui.QApplication.translate("ItemFilterDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.lblNameTemplate.setText(QtGui.QApplication.translate("ItemFilterDialog", "Шаблон наименования", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ItemFilterDialog = QtGui.QDialog()
    ui = Ui_ItemFilterDialog()
    ui.setupUi(ItemFilterDialog)
    ItemFilterDialog.show()
    sys.exit(app.exec_())

