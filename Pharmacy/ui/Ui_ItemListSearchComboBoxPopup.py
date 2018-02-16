# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ItemListSearchComboBoxPopup.ui'
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

class Ui_ItemListSearchComboBoxPopup(object):
    def setupUi(self, ItemListSearchComboBoxPopup):
        ItemListSearchComboBoxPopup.setObjectName(_fromUtf8("ItemListSearchComboBoxPopup"))
        ItemListSearchComboBoxPopup.resize(400, 240)
        self.gridLayout = QtGui.QGridLayout(ItemListSearchComboBoxPopup)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.edtName = CLineEdit(ItemListSearchComboBoxPopup)
        self.edtName.setPlaceholderText(_fromUtf8(""))
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 0, 0, 1, 1)
        self.tableView = CItemListView(ItemListSearchComboBoxPopup)
        self.tableView.setObjectName(_fromUtf8("tableView"))
        self.gridLayout.addWidget(self.tableView, 1, 0, 1, 1)

        self.retranslateUi(ItemListSearchComboBoxPopup)
        QtCore.QMetaObject.connectSlotsByName(ItemListSearchComboBoxPopup)

    def retranslateUi(self, ItemListSearchComboBoxPopup):
        ItemListSearchComboBoxPopup.setWindowTitle(_translate("ItemListSearchComboBoxPopup", "Form", None))

from library.ItemListView import CItemListView
from library.LineEdit import CLineEdit
