# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore
from PyQt4.QtCore import QAbstractListModel, Qt
from RefBooks.Ui_ItemListColumnsEditor import Ui_ItemListColumnsEditorDialog
from library.DialogBase import CDialogBase

from library.Utils              import forceString


class CItemListColumnsEditor(CDialogBase, Ui_ItemListColumnsEditorDialog):
    def __init__(self, itemListDialog, parent):
        CDialogBase.__init__(self, parent)
        self.itemListDialog = itemListDialog
        self.addModels('Columns', CItemListColumnsModel(parent=self, cols=itemListDialog.model._cols))
        self.setupUi(self)
        self.lstColumns.setModel(self.modelColumns)

class CItemListColumnsModel(QAbstractListModel):
    def __init__(self, parent, cols):
        QAbstractListModel.__init__(self, parent)
        self._cols = cols

    def flags(self, QModelIndex):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable

    def rowCount(self, parentIndex = QtCore.QModelIndex()):
        return len(self._cols)

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.CheckStateRole:
            isVisible = True if value == Qt.Checked else False
            self._cols[index.row()].setVisible(isVisible)
            self.reset()
            return True
        else:
            return super(CItemListColumnsModel, self).setData(index, value, role)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return QtCore.QVariant(forceString(self._cols[index.row()].title()))
        if role == Qt.CheckStateRole:
            return QtCore.QVariant(Qt.Checked if self._cols[index.row()].isVisible() else Qt.Unchecked)
        return QtCore.QVariant()