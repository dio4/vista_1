# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from PyQt4.QtCore import Qt

from library.DateEdit import CDateEdit
from library.Enum import CEnum, CEnumComboBox
from library.Utils import forceDate, forceDecimal, forceInt, forceString, forceStringEx


class CItemListModel(QtCore.QAbstractTableModel, object):
    NoneName = u'<Не задано>'

    def __init__(self, parent, cols=None, addNone=False, editable=False, extendable=False, itemType=None):
        super(CItemListModel, self).__init__(parent)
        self._cols = cols or []
        self._items = []
        if addNone:
            self._items.insert(0, None)
        self._editable = editable
        self._extendable = extendable
        self._itemType = itemType
        self._idToRowMap = {}

    def cols(self):
        u"""
        :rtype: list[CItemTableCol]
        """
        return self._cols

    def items(self):
        return self._items

    def isEditable(self):
        return self._editable

    def setEditable(self, editable):
        self._editable = editable

    def isExtendable(self):
        return self._extendable

    def setExtendable(self, extendable):
        if not self._extendable and extendable:
            self.emit(QtCore.SIGNAL('rowsInserted(QModelIndex, int, int)'), self.index(0, 0), self.itemCount(), self.itemCount())
        elif self._extendable and not extendable:
            self.emit(QtCore.SIGNAL('rowsRemoved(QModelIndex, int, int)'), self.index(0, 0), self.itemCount(), self.itemCount())
        self._extendable = extendable

    def emitDataChanged(self, indexFrom, indexTo):
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), indexFrom, indexTo)

    def columnCount(self, parentIndex=None, *args, **kwargs):
        return len(self._cols)

    def itemCount(self):
        return len(self._items)

    def rowCount(self, parentIndex=None, *args, **kwargs):
        return len(self._items) + (1 if self._extendable else 0)

    def flags(self, index):
        col = self._cols[index.column()]  # type: CItemTableCol
        flags = col.flags()
        if not self.isEditable():
            flags &= (~Qt.ItemIsEditable)
        return flags

    def data(self, index, role=QtCore.Qt.DisplayRole):
        row, column = index.row(), index.column()
        if 0 <= row < self.itemCount():
            if role == QtCore.Qt.UserRole:
                return self._items[row]  # raw item
            elif 0 <= column < self.columnCount():
                item = self._items[row]
                col = self._cols[column]  # type: CItemTableCol
                if role in (QtCore.Qt.DisplayRole, QtCore.Qt.EditRole):
                    if item is None:
                        return QtCore.QVariant(col.noneName())
                    return QtCore.QVariant(col.displayValue(item, row=row))
                elif role == QtCore.Qt.TextColorRole:
                    return QtCore.QVariant(col.textColor(item))
                elif role == QtCore.Qt.BackgroundColorRole:
                    return QtCore.QVariant(col.bgColor(item))
                elif role == QtCore.Qt.TextAlignmentRole:
                    return QtCore.QVariant(col.alignment(item))
                elif role == QtCore.Qt.ToolTipRole:
                    return QtCore.QVariant(col.toolTip(item))
                elif role == QtCore.Qt.CheckStateRole:
                    return QtCore.QVariant(col.checkState(item))

        return QtCore.QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            row, column = index.row(), index.column()
            col = self._cols[column]  # type: CItemTableCol

            itemCount = self.itemCount()
            if row == itemCount:
                if not value or value.isNull():
                    return False

                self.appendNewItem()
                rootIndex = QtCore.QModelIndex()
                self.beginInsertRows(rootIndex, itemCount, itemCount)
                self.insertRows(itemCount, 1, rootIndex)
                self.endInsertRows()

            item = self._items[row]
            col.setValue(item, value)
            return True

        return False

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return self._cols[section].title()
        return QtCore.QVariant()

    def createEditor(self, column, parent, item):
        return self._cols[column].createEditor(parent, item)

    def getEditorData(self, column, editor):
        return self._cols[column].getEditorData(editor)

    def setEditorData(self, column, editor, value, item):
        return self._cols[column].setEditorData(editor, value, item)

    def getItem(self, row):
        if 0 <= row < len(self._items):
            return self._items[row]
        return None

    def isItemModified(self, row):
        return False

    def clearItems(self):
        self._items = []
        self.reset()

    def searchId(self, itemId):
        return self._idToRowMap.get(itemId, -1)

    def _resetIdMap(self):
        self._idToRowMap.clear()
        for row, item in enumerate(self.items()):
            self._addRowItemMap(row, item)

    def _addRowItemMap(self, row, item):
        if hasattr(item, 'id') and item.id is not None:
            self._idToRowMap[item.id] = row

    def _delRowItemMap(self, row):
        item = self._items[row]
        if hasattr(item, 'id') and item.id is not None and item.id in self._idToRowMap:
            del self._idToRowMap[item.id]

    def setCols(self, cols):
        self._cols = cols

    def addCol(self, col):
        self._cols.append(col)

    def insertCol(self, idx, col):
        self._cols.insert(idx, col)

    def setItem(self, row, item):
        self._items[row] = item
        self._addRowItemMap(row, item)
        self.emitDataChanged(self.index(row, 0),
                             self.index(row, self.columnCount() - 1))

    def setItems(self, items, itemType=None, addNone=False):
        self._items = []
        if addNone:
            self._items.append(None)
        if items:
            self._items.extend(items)
        if itemType:
            self._itemType = itemType
        self.reset()
        self._resetIdMap()

    def insertItem(self, row, item):
        self.beginInsertRows(QtCore.QModelIndex(), row, row)
        self._items.insert(row, item)
        self._addRowItemMap(row, item)
        self.endInsertRows()

    def appendNewItem(self):
        item = self.newItem()
        self.setDefaults(item)
        self._items.append(item)

    def addItem(self, item):
        self.insertItem(self.rowCount(), item)

    def newItem(self):
        item = self._itemType() if self._itemType else None
        return item

    def setDefaults(self, item):
        pass

    def _delItem(self, row):
        self._delRowItemMap(row)
        del self._items[row]

    def sort(self, column, order=Qt.AscendingOrder):
        col = self._cols[column]
        if not col.sortable():
            return
        self._items.sort(key=lambda item: col.sortValue(item),
                         reverse=order == Qt.DescendingOrder)
        self.emitDataChanged(self.index(0, column),
                             self.index(self.rowCount(), column))

    def removeRow(self, row, parent=QtCore.QModelIndex(), *args, **kwargs):
        if self._items and 0 <= row < len(self._items):
            self.beginRemoveRows(parent, row, row)
            self._delItem(row)
            self.endRemoveRows()
            return True
        return False

    def removeRows(self, row, count, parentIndex=QtCore.QModelIndex(), *args, **kwargs):
        if 0 <= row and row + count <= len(self._items):
            self.beginRemoveRows(parentIndex, row, row + count - 1)
            for r in range(row, row + count):
                self._delItem(row)
            self.endRemoveRows()
            return True
        return False


class CItemListSortFilterProxyModel(QtGui.QSortFilterProxyModel, object):
    def __init__(self, parent=None):
        super(CItemListSortFilterProxyModel, self).__init__(parent)
        self._columnPatternFilterMap = {}

    def clearFilter(self):
        self._columnPatternFilterMap.clear()

    def addColumnPatternFilter(self, column, pattern):
        self._columnPatternFilterMap[column] = forceStringEx(pattern).lower()

    def filterAcceptsRow(self, sourceRow, sourceParent):
        if not self._columnPatternFilterMap:
            return True

        for column, pattern in self._columnPatternFilterMap.items():
            index = self.sourceModel().index(sourceRow, column)
            data = forceStringEx(index.data()).lower()
            if pattern in data:
                return True

        return False

    def getItem(self, row):
        proxyIndex = self.index(row, 0)
        sourceIndex = self.mapToSource(proxyIndex)
        return self.sourceModel().getItem(sourceIndex.row())

    def searchId(self, itemId):
        return self.sourceModel().searchId(itemId)


class ColAlignment(CEnum):
    left = 'l'
    center = 'c'
    right = 'r'
    justify = 'j'

    valueMap = {
        left   : Qt.AlignLeft + Qt.AlignVCenter,
        center : Qt.AlignHCenter + Qt.AlignVCenter,
        right  : Qt.AlignRight + Qt.AlignVCenter,
        justify: Qt.AlignJustify + Qt.AlignVCenter
    }


class CItemTableCol(object):
    def __init__(self, title, **params):
        super(CItemTableCol, self).__init__()
        self._title = title
        self._sortable = params.get('sortable', False)
        self._editable = params.get('editable', False)
        self._valueType = params.get('valueType', QtCore.QVariant.String)
        self._visible = params.get('visible', True)
        self._noneName = params.get('noneName', u'<Не задано>')
        self._alignment = ColAlignment.valueMap[params.get('alignment', ColAlignment.left)]

    def title(self):
        return self._title

    def isVisible(self):
        return self._visible

    def sortable(self):
        return self._sortable

    def isEditable(self):
        return self._editable

    def setEditable(self, editable=True):
        self._editable = editable

    def alignment(self, item, **params):
        return self._alignment

    def noneName(self):
        return self._noneName

    def displayValue(self, item, **params):
        return None

    def setValue(self, item, value):
        pass

    def sortValue(self, item, **params):
        return self.displayValue(item, **params)

    def toVariant(self, item, **params):
        return QtCore.QVariant(self.displayValue(item, **params))

    def textColor(self, item, **params):
        return None

    def bgColor(self, item, **params):
        return None

    def toolTip(self, item, **params):
        return None

    def checkState(self, item, **params):
        return None

    def flags(self):
        result = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if self._editable:
            result |= Qt.ItemIsEditable
        return result

    def createEditor(self, parent, item):
        editor = QtGui.QLineEdit(parent)
        return editor

    def getEditorData(self, editor):
        text = editor.text()
        return QtCore.QVariant(text)

    def setEditorData(self, editor, value, item):
        editor.setText(forceString(value))


class CItemAttribCol(CItemTableCol):
    u""" Столбец: значение аттрибута объекта """

    def __init__(self, title, attribName, default=None, **params):
        super(CItemAttribCol, self).__init__(title, **params)
        self._attribName = attribName
        self._default = default

    def value(self, item):
        return getattr(item, self._attribName, self._default)

    def displayValue(self, item, **params):
        return getattr(item, self._attribName, self._default)

    def setValue(self, item, value):
        setattr(item, self._attribName, value)


class CItemIndexCol(CItemTableCol):
    u""" Столбец: значение по индексу """

    def __init__(self, title, idx, default=None, **params):
        super(CItemIndexCol, self).__init__(title, **params)
        self._idx = idx
        self._default = default

    def value(self, item):
        try:
            return item[self._idx]
        except IndexError:
            return self._default

    def displayValue(self, item, **params):
        return self.value(item)

    def setValue(self, item, value):
        item[self._idx] = value


class CItemProxyCol(CItemAttribCol):
    u""" Столбец: значение аттрибута вложенного объекта """

    def __init__(self, title, sourceCol, attribName, default=None, **params):
        super(CItemProxyCol, self).__init__(title, attribName, default, **params)
        self._sourceCol = sourceCol  # type: CItemAttribCol

    def value(self, item):
        return getattr(self._sourceCol.value(item), self._attribName, self._default)

    def displayValue(self, item, **params):
        return self.value(item)

    def setValue(self, item, value):
        setattr(self._sourceCol.value(item), self._attribName, value)


class CStringAttribCol(CItemAttribCol):
    u""" Столбец: строковый аттрибут """

    def setValue(self, item, value):
        super(CStringAttribCol, self).setValue(item, forceString(value))


class CIntAttribCol(CItemAttribCol):
    u""" Столбец: целочисленный аттрибут """

    def __init__(self, title, attribName, default=None, **params):
        super(CIntAttribCol, self).__init__(title, attribName, default, **params)
        self._minimum = params.get('minimum', 0)
        self._maximum = params.get('maximum', 1000000)

    def setValue(self, item, value):
        super(CIntAttribCol, self).setValue(item, forceInt(value))

    def getMinimum(self, item):
        return self._minimum

    def getMaximum(self, item):
        return self._maximum

    def createEditor(self, parent, item):
        editor = QtGui.QSpinBox(parent)
        editor.setMinimum(self.getMinimum(item))
        editor.setMaximum(self.getMaximum(item))
        return editor

    def getEditorData(self, editor):
        return QtCore.QVariant(editor.value())

    def setEditorData(self, editor, value, item):
        return editor.setValue(forceInt(value))


class CEnumAttribCol(CItemAttribCol):
    u""" Столбец: значение из словаря (CEnum) """

    def __init__(self, title, attribName, enumClass, default=None, **params):
        super(CEnumAttribCol, self).__init__(title, attribName, default, **params)
        self._enumClass = enumClass  # type: CEnum

    def displayValue(self, item, **params):
        return self._enumClass.getName(self.value(item))

    def createEditor(self, parent, item):
        editor = CEnumComboBox(parent)
        editor.setEnum(self._enumClass)
        return editor

    def getEditorData(self, editor):
        u"""
        :type editor: CEnumComboBox
        """
        return QtCore.QVariant(editor.value())

    def setEditorData(self, editor, value, item):
        u"""
        :type editor: CEnumComboBox
        :type value: QVariant
        :param item:
        """
        editor.setValue(self.value(item))

    def setValue(self, item, value):
        super(CEnumAttribCol, self).setValue(item, forceInt(value))


class CDecimalAttribCol(CItemAttribCol):
    u""" Столбец: число в десятичном представлении """

    def __init__(self, title, attribName, default=None, numberFormat='%.2f', **params):
        super(CDecimalAttribCol, self).__init__(title, attribName, default, **params)
        self._format = numberFormat

    def displayValue(self, item, **params):
        v = super(CDecimalAttribCol, self).displayValue(item, **params)
        return self._format % v if v else 0

    def setValue(self, item, value):
        decValue = forceDecimal(value)
        super(CDecimalAttribCol, self).setValue(item, decValue)

    def createEditor(self, parent, item):
        editor = QtGui.QLineEdit(parent)
        validator = QtGui.QDoubleValidator(editor)
        editor.setValidator(validator)
        return editor


class CDateAttribCol(CItemAttribCol):
    u""" Столбец: дата """

    def createEditor(self, parent, item):
        editor = CDateEdit(parent)
        return editor

    def setEditorData(self, editor, value, item):
        editor.setDate(forceDate(value))

    def getEditorData(self, editor):
        date = editor.date()
        return date if date.isValid() else None

    def displayValue(self, item, **params):
        value = super(CDateAttribCol, self).displayValue(item, **params)
        if isinstance(value, QtCore.QDateTime):
            return forceString(value.toString('dd.MM.yyyy hh:mm'))
        elif isinstance(value, QtCore.QDate):
            return forceString(value.toString('dd.MM.yyyy'))
        return value


class CRowCounterCol(CItemTableCol):
    u""" Столбец: номер строки """

    def displayValue(self, item, **params):
        return params.get('row', 0) + 1
