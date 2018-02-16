# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

import webbrowser

from PyQt4.QtCore                 import QAbstractTableModel, Qt, QVariant, QModelIndex
from PyQt4                        import QtGui

from library.TableView            import CTableView
from library.Utils                import forceString

class CKeyValueTableView(CTableView):
    def mousePressEvent(self, event):
        button = event.button()
        if button == Qt.RightButton:
            pos = event.pos()
            index = self.indexAt(pos)
            #index = self.currentIndex()
            self.setCurrentIndex(index)
            if index.column() == 1:
                value = forceString(self.model().data(index))
                if value.startswith('http://'):
                    browser = webbrowser.get()
                    browser.open_new_tab(value)
                    event.accept()
                    return
        CTableView.mousePressEvent(self, event)


class CKeyValueModel(QAbstractTableModel):
    def __init__(self, parent):
        QAbstractTableModel.__init__(self, parent)
        self._items = []
        self._editable = True

    def columnCount(self, index = QModelIndex()):
        return 2

    def rowCount(self, index = QModelIndex()):
        return len(self._items) + 1

    def setItems(self, items):
        self._items = items[:] #atronah: nice
        self.reset()

    def items(self):
        return self._items

    def setEditable(self, editable):
        self._editable = editable

    def data(self, index, role = Qt.DisplayRole):
        column = index.column()
        row = index.row()
        if row in xrange(len(self._items)):
            if role == Qt.DisplayRole or role == Qt.EditRole:
                return QVariant(self._items[row][column])
            elif role == Qt.FontRole:
                result = QtGui.QFont()
                if forceString(self._items[row][column]).startswith('http://') and column == 1:
                    result.setItalic(True)
                    result.setUnderline(True)
                return result
        return QVariant()

    def headerData(self, section, orientation, role = Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                if section == 0:
                    return QVariant(u'Ключ')
                elif section == 1:
                    return QVariant(u'Значение')
        return QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        row = index.row()
        column = index.column()
        if role == Qt.EditRole:
            if row == len(self._items):
                if value.isNull():
                    return False
                rootIndex = QModelIndex()
                count = len(self._items)
                self.beginInsertRows(rootIndex, count, count)
                if column == 0:
                    item = (forceString(value), u'')
                else:
                    item = (u'', forceString(value))
                self._items.append(item)
                self.endInsertRows()
                return True
            else:
                key, val = self._items[row]
                if column == 0:
                    key = value
                if column == 1:
                    val = value
                self._items[row] = (forceString(key), forceString(val))
                return True
        return False


    def flags(self, index):
        if self._editable:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable