from PyQt4 import QtCore
from abc import abstractmethod


class CItemsListModel(QtCore.QAbstractItemModel):
    """Model that stores (id, displayName) tuples"""

    def __init__(self, parent=None):
        super(CItemsListModel, self).__init__(parent)
        self._items = []

    @abstractmethod
    def loadItems(self):
        return []  # items list

    def reset(self):
        self._items = self.loadItems()
        super(CItemsListModel, self).reset()

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self._items)

    def columnCount(self, parent=None, *args, **kwargs):
        return 1

    def data(self, index, role=None):
        row = index.row()
        col = index.column()
        if role in (QtCore.Qt.DisplayRole, QtCore.Qt.ToolTipRole):
            if len(self._items) > row >= 0 and col == 0:
                return self._items[row][1]
        return QtCore.QVariant()

    def index(self, row, col, parent=None, *args, **kwargs):
        if len(self._items) > row >= 0 and col == 0:
            return self.createIndex(row, col, self._items[row][0])
        return QtCore.QModelIndex()

    def parent(self, index=None):
        return QtCore.QModelIndex()

    def value(self, index):
        row = index.row()
        col = index.column()
        if len(self._items) > row >= 0 and col == 0:
            return self._items[row][0]
        return None

    def first(self):
        return self.index(0, 0)
