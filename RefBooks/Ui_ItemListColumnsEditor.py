# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ItemListColumnsEditor.ui'
#
# Created: Tue Oct 28 17:05:47 2014
#      by: PyQt4 UI code generator 4.11
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

class Ui_ItemListColumnsEditorDialog(object):
    def setupUi(self, ItemListColumnsEditorDialog):
        ItemListColumnsEditorDialog.setObjectName(_fromUtf8("ItemListColumnsEditorDialog"))
        ItemListColumnsEditorDialog.resize(382, 366)
        ItemListColumnsEditorDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ItemListColumnsEditorDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonBox = QtGui.QDialogButtonBox(ItemListColumnsEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 2)
        self.lstColumns = QtGui.QListView(ItemListColumnsEditorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.lstColumns.sizePolicy().hasHeightForWidth())
        self.lstColumns.setSizePolicy(sizePolicy)
        self.lstColumns.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.lstColumns.setUniformItemSizes(True)
        self.lstColumns.setObjectName(_fromUtf8("lstColumns"))
        self.gridLayout.addWidget(self.lstColumns, 0, 0, 1, 1)

        self.retranslateUi(ItemListColumnsEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ItemListColumnsEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ItemListColumnsEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ItemListColumnsEditorDialog)

    def retranslateUi(self, ItemListColumnsEditorDialog):
        ItemListColumnsEditorDialog.setWindowTitle(_translate("ItemListColumnsEditorDialog", "Выбор колонок", None))

