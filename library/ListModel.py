# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore
from PyQt4.QtCore import Qt, QVariant
from PyQt4 import QtGui


#TODO: mdldml: подумать над более вменяемым названием
#TODO: mdldml: подумать над более богатым функционалом, чтобы можно было спокойно использовать вместо crbmodel
# Readonly-модель для комбобоксов и списков, которые нежелательно хранить в базе.
# Список значений values должен быть подмножеством refBook
class CListModel(QtCore.QAbstractListModel):
    def __init__(self, values, refBook=None):
        QtCore.QAbstractListModel.__init__(self)
        self._values = values
        self._refBook = refBook if refBook is not None else values[:]

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self._values)

    def data(self, index, role=None):
        if not index.isValid():
            return QVariant()

        row = index.row()
        if 0 <= row < self.rowCount() and role == Qt.DisplayRole:
            return QVariant(self._values[row])

        return QVariant()

    def getCode(self, index):
        return self._refBook.index(self._values[index])

    def getIndex(self, code):
        return self._values.index(self._refBook[code])

    def getValueIndex(self, value):
        try:
            index = self._values.index(value)
        except ValueError:
            index = None
        return index

    def getValue(self, index):
        if 0 <= index < self.rowCount():
            return self._values[index]
        return None

    def setValues(self, values):
        self._values = values


class CListComboBox(QtGui.QComboBox):
    def value(self):
        return self.model().getValue(self.currentIndex())

    def setValue(self, value):
        index = self.model().getValueIndex(value)
        if index is not None:
            self.setCurrentIndex(index)

    def setValues(self, values):
        self.setModel(CListModel(values))


class CMultiSelectionListModel(CListModel):
    def __init__(self, values, refBook=None):
        CListModel.__init__(self, values, refBook)
        self._selected = set()

    def isSelected(self, row):
        return row in self._selected

    def selectRow(self, row):
        self._selected.add(row)

    def unselectRow(self, row):
        self._selected.remove(row)

    def toggleSelection(self, index):
        row = index.row()
        if 0 <= row < self.rowCount():
            if self.isSelected(row):
                self.unselectRow(row)
            else:
                self.selectRow(row)
        return self.createIndex(row, 0)

    def getSelected(self):
        return self._selected

    def getSelectedValues(self):
        return [self._values[row] for row in self.getSelected()]

    def setSelected(self, selected):
        self._selected = selected

    def selectAll(self):
        self._selected = set(xrange(self.rowCount()))

    def unselectAll(self):
        self._selected = set()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        row, col = index.row(), index.column()
        if 0 <= row < self.rowCount() and role == Qt.CheckStateRole:
            return QVariant(self.isSelected(row))
        return CListModel.data(self, index, role)


class CMultiComboBox(QtGui.QComboBox):
    NoSelection = u'<Не выбрано>'

    def __init__(self, parent):
        super(CMultiComboBox, self).__init__(parent)
        self._model = CMultiSelectionListModel([])

        self._popup = QtGui.QListView(self)
        self._popup.setModel(self._model)

        self.setModel(self._model)
        self.setView(self._popup)
        self.installEventFilter(self)
        self._popup.viewport().installEventFilter(self)

        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.setMaxVisibleItems(20)

    def updateText(self):
        self.setEditText(u', '.join(map(unicode, self._model.getSelectedValues())) or self.NoSelection)

    def setModel(self, model):
        super(CMultiComboBox, self).setModel(model)
        self._popup.setModel(model)
        self._model = model
        self.updateText()

    def eventFilter(self, obj, evt):
        if evt.type() == QtCore.QEvent.MouseButtonRelease:
            if obj == self._popup.viewport():
                index = self._popup.currentIndex()
                self._popup.update(self._model.toggleSelection(index))
                self.updateText()
                return True
        return False

    def setValue(self, rowList):
        if isinstance(rowList, (list, tuple, set)):
            self._model.setSelected(set(rowList))
        elif isinstance(rowList, int):
            self._model.setSelected(set([rowList]))
        elif not rowList:
            self._model.setSelected(set())
        self.updateText()

    def values(self):
        return self._model.getSelectedValues()

    def selectAll(self):
        self._model.selectAll()
        self.updateText()
