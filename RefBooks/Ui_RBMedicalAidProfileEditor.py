# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\RefBooks\RBMedicalAidProfileEditor.ui'
#
# Created: Fri Jun 15 12:16:59 2012
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
        ItemEditorDialog.resize(285, 145)
        ItemEditorDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ItemEditorDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblCode = QtGui.QLabel(ItemEditorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblCode.sizePolicy().hasHeightForWidth())
        self.lblCode.setSizePolicy(sizePolicy)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridLayout.addWidget(self.lblCode, 0, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout.addWidget(self.edtCode, 0, 1, 1, 1)
        self.lblName = QtGui.QLabel(ItemEditorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblName.sizePolicy().hasHeightForWidth())
        self.lblName.setSizePolicy(sizePolicy)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout.addWidget(self.lblName, 1, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(ItemEditorDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 1, 1, 1, 1)
        self.lblFederalCode = QtGui.QLabel(ItemEditorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblFederalCode.sizePolicy().hasHeightForWidth())
        self.lblFederalCode.setSizePolicy(sizePolicy)
        self.lblFederalCode.setObjectName(_fromUtf8("lblFederalCode"))
        self.gridLayout.addWidget(self.lblFederalCode, 2, 0, 1, 1)
        self.edtFederalCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtFederalCode.setObjectName(_fromUtf8("edtFederalCode"))
        self.gridLayout.addWidget(self.edtFederalCode, 2, 1, 1, 1)
        self.lblRegionalCode = QtGui.QLabel(ItemEditorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblRegionalCode.sizePolicy().hasHeightForWidth())
        self.lblRegionalCode.setSizePolicy(sizePolicy)
        self.lblRegionalCode.setObjectName(_fromUtf8("lblRegionalCode"))
        self.gridLayout.addWidget(self.lblRegionalCode, 3, 0, 1, 1)
        self.edtRegionalCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtRegionalCode.setObjectName(_fromUtf8("edtRegionalCode"))
        self.gridLayout.addWidget(self.edtRegionalCode, 3, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(73, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ItemEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 2)
        self.lblCode.setBuddy(self.edtCode)
        self.lblName.setBuddy(self.edtName)
        self.lblFederalCode.setBuddy(self.edtFederalCode)
        self.lblRegionalCode.setBuddy(self.edtRegionalCode)

        self.retranslateUi(ItemEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ItemEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ItemEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ItemEditorDialog)
        ItemEditorDialog.setTabOrder(self.edtCode, self.edtName)
        ItemEditorDialog.setTabOrder(self.edtName, self.edtFederalCode)
        ItemEditorDialog.setTabOrder(self.edtFederalCode, self.edtRegionalCode)
        ItemEditorDialog.setTabOrder(self.edtRegionalCode, self.buttonBox)

    def retranslateUi(self, ItemEditorDialog):
        ItemEditorDialog.setWindowTitle(QtGui.QApplication.translate("ItemEditorDialog", "ChangeMe!", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCode.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Код", None, QtGui.QApplication.UnicodeUTF8))
        self.lblName.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Наименование", None, QtGui.QApplication.UnicodeUTF8))
        self.lblFederalCode.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Федеральный код", None, QtGui.QApplication.UnicodeUTF8))
        self.lblRegionalCode.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Региональный код", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ItemEditorDialog = QtGui.QDialog()
    ui = Ui_ItemEditorDialog()
    ui.setupUi(ItemEditorDialog)
    ItemEditorDialog.show()
    sys.exit(app.exec_())

