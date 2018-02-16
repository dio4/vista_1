# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'StoreItemSelectionDialog.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_StoreItemSelectionDialog(object):
    def setupUi(self, StoreItemSelectionDialog):
        StoreItemSelectionDialog.setObjectName(_fromUtf8("StoreItemSelectionDialog"))
        StoreItemSelectionDialog.resize(400, 291)
        StoreItemSelectionDialog.setModal(True)
        self.gridLayout = QtGui.QGridLayout(StoreItemSelectionDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tblItems = CItemListView(StoreItemSelectionDialog)
        self.tblItems.setObjectName(_fromUtf8("tblItems"))
        self.gridLayout.addWidget(self.tblItems, 0, 0, 1, 1)

        self.retranslateUi(StoreItemSelectionDialog)
        QtCore.QMetaObject.connectSlotsByName(StoreItemSelectionDialog)

    def retranslateUi(self, StoreItemSelectionDialog):
        StoreItemSelectionDialog.setWindowTitle(_translate("StoreItemSelectionDialog", "Dialog", None))

from library.ItemListView import CItemListView
