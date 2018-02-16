# -*- coding: utf-8 -*-
import re
from PyQt4 import QtGui, QtCore

from Reports.ReportsConstructor.RCComboBox import CRCFieldsComboBox, CRCComboBox
from Reports.ReportsConstructor.RCLineEdit import CRCFieldLineEdit, CRCColsLineEdit, CRCAliasLineEdit
from library.InDocTable import CInDocTableModel, CInDocTableCol, CLocItemDelegate, CRBInDocTableCol, CBoolInDocTableCol
from library.Utils import forceRef, forceString, forceBool, forceInt, toVariant, forceStringEx


class CRCLocItemFieldDelegate(CLocItemDelegate):
    def __init__(self, parent):
        CLocItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        column = index.column()
        extended = False
        if index.row() < index.model().rowCount() - 1:
            extended = index.model().cols()[column]._fieldName == 'field'
            extended = extended and forceBool(index.model().items()[index.row()].value('extended'))
        editor = index.model().createEditor(column, parent, extended=extended)
        self.connect(editor, QtCore.SIGNAL('commit()'), self.emitCommitData)
        self.connect(editor, QtCore.SIGNAL('editingFinished()'), self.commitAndCloseEditor)
        self.connect(editor, QtCore.SIGNAL('saveExtraData(QString, QString)'), self.saveExtraData)
        self.editor = editor
        self.row = index.row()
        self.rowcount = index.model().rowCount()
        self.column = column
        self._extraData = None
        self._extraField = None
        return editor


class CRCInDocTableModel(CInDocTableModel):
    def __init__(self, tableName, idFieldName, masterIdFieldName, parent, rowNumberTitle=None):
        CInDocTableModel.__init__(self, tableName, idFieldName, masterIdFieldName, parent, rowNumberTitle)

    def getRecordById(self, id):
        for index, record in enumerate(self._items):
            if forceInt(record.value('id')) == id:
                return index, record
        return None, None

    def getFieldValue(self, id):
        index, record = self.getRecordById(forceInt(id))
        if record:
            return index, forceString(record.value('field'))
        return 0, u''

    def getRecordByIndex(self, index):
        if index < len(self._items) and index >= 0:
            return self._items[index]
        return None

    def getFieldValueByIndex(self, index):
        record = self.getRecordByIndex(index)
        if record:
            return forceString(record.value('field'))
        return u''

    def getItem(self, id):
        index, record = self.getRecordById(forceInt(id))
        if record:
            return {
                'id': forceInt(record.value('id')),
                'field': forceString(record.value('field')),
                'alias': forceString(record.value('alias'))
            }
        return {}

    def getItemByNumber(self, number):
        record = None
        for item in self._items:
            if forceInt(item.value('number')) == forceInt(number):
                record = item
                break
        if record:
            return {'id': forceInt(record.value('id')),
                    'field': forceString(record.value('field')),
                    'alias': forceString(record.value('alias'))}
        return {}

    def createEditor(self, column, parent, extended):
        self.emit(QtCore.SIGNAL('editInProgress(bool)'), True)
        if extended:
            return self._cols[column].createEditor(parent, extended)
        else:
            return self._cols[column].createEditor(parent)

    def flags(self, index):
        flags = CInDocTableModel.flags(self, index)
        if index.isValid():
            return flags | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled
        return flags

    def loadItems(self, masterId):
        CInDocTableModel.loadItems(self, masterId)
        self.sortItems('number')

    def sortItems(self, fieldName):
        self._items.sort(key=lambda (item): forceInt(item.value(fieldName)))
        self.reset()
        self.emitDataChanged()

    def idsByOrder(self):
        result = {}
        for record in self._items:
            result[forceInt(record.value('number')) - 1] = forceInt(record.value('id'))
        return result

    def saveItems(self, masterId):
        self.reorderItems()
        CInDocTableModel.saveItems(self, masterId)
        newIds = self.idsByOrder()
        self.emitIdsChange(newIds)

    def emitIdsChange(self, newIds):
        for number, idFrom in newIds.items():
            self.emitIdChange(number, idFrom)

    def emitIdChange(self, idFrom, idTo):
        self.emit(QtCore.SIGNAL('idChanged(int, int)'), idFrom, idTo)

    def reorderItems(self):
        for idx, record in enumerate(self._items):
            record.setValue('number', toVariant(idx + 1))
        self.emit(QtCore.SIGNAL('reorderItems()'))
        self.emitDataChanged()

    def replaceItems(self, rowsFrom, rowTo):
        # rowsFromCount = len(rowsFrom)
        rowsOrder = [idx for idx in range(len(self._items)) if idx not in rowsFrom]
        for idx in rowsFrom:
            rowsOrder.insert(rowTo, idx)

        newItems = []
        for idx in rowsOrder:
            newItems.append(self._items[idx])
        self._items = newItems
        self.reorderItems()

    def deleteItem(self, row):
        if row < len(self._items):
            self._items = self._items[:row] + self._items[row + 1:]
            self.reset()

    def getItemId(self, index):
        if isinstance(index, QtCore.QModelIndex):
            row = index.row()
        else:
            row = index
        return self.getItemByIndex(row)

    def getIndexById(self, id):
        id = forceInt(id)
        for row, record in enumerate(self._items):
            if forceInt(record.value(self._idFieldName)) == id:
                return row
        return 0

    def getItemByIndex(self, index):
        if self._items and not len(self._items) < index:
            return forceRef(self._items[index].value(self._idFieldName))
        return None

    def getFullName(self, code):
        return self._baseModel.parcePathToTableNames(forceString(code))

    def getShortName(self, code):
        if not re.search('\$', code):
            code = '{%s}' % re.findall('\w+', code)[-1]
        return self._baseModel.parcePathToTableNames(forceString(code))

    def supportedDropActions(self):
        return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction

    def mimeTypes(self):
        types = QtCore.QStringList()
        # передаем index.row() в текстовом виде
        types.append('text/plain')
        return types

    def mimeData(self, index):
        row = index[0].row()

        mimeData = QtCore.QMimeData();
        mimeData.setText(forceString(row));
        return mimeData

    def dropMimeData(self, data, action, row, column, parentIndex):
        if action == QtCore.Qt.IgnoreAction:
            return True

        if not data.hasText():
            return False

        dragIdString = forceString(forceInt(data.text()))
        dragIdList = [forceInt(id) for id in dragIdString.split(',')]
        parentIndexRow = parentIndex.row()

        self.replaceItems(dragIdList, parentIndexRow)
        return True

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        """
        Parent's method is overrided to support adding many items by one time
        :param index:
        :param value:
        :param role:
        :return:
        """
        if role == QtCore.Qt.EditRole:
            column = index.column()
            row = index.row()
            if not isinstance(value, list):
                value = [value]
            for val in value:
                if val:
                    if row == len(self._items):
                        self._items.append(self.getEmptyRecord())
                        count = len(self._items)
                        rootIndex = QtCore.QModelIndex()
                        self.beginInsertRows(rootIndex, count, count)
                        self.insertRows(count, 1, rootIndex)
                        self.endInsertRows()
                    record = self._items[row]
                    col = self._cols[column]
                    record.setValue(col.fieldName(), toVariant(val))
                    self.emitCellChanged(row, column)
                    row += 1
                    self.reorderItems()
            return True
        if role == QtCore.Qt.CheckStateRole:
            column = index.column()
            row = index.row()
            state = value.toInt()[0]
            if row == len(self._items):
                if state == QtCore.Qt.Unchecked:
                    return False
                self._items.append(self.getEmptyRecord())
                count = len(self._items)
                rootIndex = QtCore.QModelIndex()
                self.beginInsertRows(rootIndex, count, count)
                self.insertRows(count, 1, rootIndex)
                self.endInsertRows()
            record = self._items[row]
            col = self._cols[column]
            record.setValue(col.fieldName(), QtCore.QVariant(0 if state == QtCore.Qt.Unchecked else 1))
            self.emitCellChanged(row, column)
            return True
        return False

    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = index.column()
        row = index.row()
        if 0 <= row < len(self._items):
            if role == QtCore.Qt.ToolTipRole:
                col = self._cols[column]
                record = self._items[row]
                return col.toString(record.value(col.fieldName()), record)
        return CInDocTableModel.data(self, index, role)


class CRCGroupsModel(CRCInDocTableModel):
    def __init__(self, parent, model):
        CRCInDocTableModel.__init__(self, 'rcQuery_Group', 'id', 'master_id', parent)
        self._baseModel = model
        self.addCol(CQueryFieldInDocTableCol(u'Поле', 'field', 20, self._baseModel, sortable=True))
        self.addCol(CBoolInDocTableCol(u'Расширенный', 'extended', 10, sortable=True))
        self.addHiddenCol('number')


class CRCOrdersModel(CRCInDocTableModel):
    def __init__(self, parent, model):
        CRCInDocTableModel.__init__(self, 'rcQuery_Order', 'id', 'master_id', parent)
        self._baseModel = model
        self.addCol(CQueryFieldInDocTableCol(u'Поле', 'field', 20, self._baseModel, sortable=True))
        self.addCol(CBoolInDocTableCol(u'Расширенный', 'extended', 10, sortable=True))
        self.addHiddenCol('number')


class CRCColsModel(CRCInDocTableModel):
    def __init__(self, parent, model):
        CRCInDocTableModel.__init__(self, 'rcQuery_Cols', 'id', 'master_id', parent)
        self._baseModel = model
        self.addCol(CQueryFieldInDocTableCol(u'Поле', 'field', 200, self._baseModel, sortable=True))
        self.addCol(CQueryAliasInDocTableCol(u'Псевдоним', 'alias', 20, sortable=True))
        self.addCol(CBoolInDocTableCol(u'Расширенный', 'extended', 10, sortable=True))
        self.addHiddenCol('number')


class CRCParamValueModel(CRCInDocTableModel):
    def __init__(self, parent):
        CRCInDocTableModel.__init__(self, 'rcParam_Value', 'id', 'master_id', parent)
        self.addCol(CInDocTableCol(u'Наименование', 'title', 20, sortable=True))
        self.addCol(CInDocTableCol(u'Значение', 'value', 10, sortable=True))
        self.addHiddenCol('number')

    def createEditor(self, column, parent):
        return CInDocTableModel.createEditor(self, column, parent)


class CQueryFieldInDocTableCol(CInDocTableCol):
    def __init__(self, title, fieldName, width, model, **params):
        CInDocTableCol.__init__(self, title, fieldName, width, **params)
        self._baseModel = model

    def toString(self, val, record):
        return toVariant(self._baseModel.parcePathToTableNames(forceString(val)))

    def createEditor(self, parent, extended=False):
        if not extended:
            editor = CRCFieldsComboBox(parent)
            editor.setModel(self._baseModel)
        else:
            editor = CRCFieldLineEdit(parent, self._baseModel)
        return editor

    def getEditorData(self, editor):
        if isinstance(editor, QtGui.QLineEdit):
            return self._baseModel.parceTableNamesToPath(forceString(editor.text()))
        else:
            pathList = []
            for value in editor.value():
                path = value
                pathList.append(self._baseModel.forceString(path))
            return pathList

    def setEditorData(self, editor, value, record):
        if isinstance(editor, QtGui.QLineEdit):
            editor.setText(forceString(self.toString(value, record)))
        else:
            editor.setValue(forceString(value))


class CQueryAliasInDocTableCol(CInDocTableCol):
    def __init__(self, title, fieldName, width, **params):
        CInDocTableCol.__init__(self, title, fieldName, width, **params)

    def createEditor(self, parent):
        editor = CRCAliasLineEdit(parent)
        return editor


class CRCLocItemDelegate(CLocItemDelegate):
    def __init__(self, parent):
        CLocItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        if not index.isValid():
            return None
        editor = index.model().createEditor(index, parent)
        self.connect(editor, QtCore.SIGNAL('commit()'), self.emitCommitData)
        self.connect(editor, QtCore.SIGNAL('editingFinished()'), self.commitAndCloseEditor)
        self.connect(editor, QtCore.SIGNAL('saveExtraData(QString, QString)'), self.saveExtraData)
        self.editor = editor
        self.row = index.row()
        self.rowcount = index.model().rowCount()
        self._extraData = None
        self._extraField = None
        return editor

    def setEditorData(self, editor, index):
        if editor is not None and index.isValid():
            model = index.model()
            value = model.data(index, QtCore.Qt.EditRole)
            model.setEditorData(index, editor, value)

    def setModelData(self, editor, model, index):
        if editor is not None and index.isValid():
            editorData = index.model().getEditorData(index, editor)
            model.setData(index, editorData)


class CRCCapItem(object):
    def __init__(self, parent, name=u'', rowSpan=1, columnSpan=1, alignment=0, type='cap', bold=False):
        self._parent = parent
        self._name = name
        self._rowSpan = rowSpan
        self._columnSpan = columnSpan
        self._readOnly = False
        self._alignment = alignment
        self._bold = bold
        self._type = type
        self._value = {}
        self._modelCols = self._parent._modelCols
        self._modelFields = self._parent._modelFields
        if self.isField():
            self.setValue(forceInt(self._name))

    def name(self):
        return self._name

    def setName(self, name):
        self._name = name

    def getValueToSave(self):
        if self.isField():
            return forceString(self._value.get('number', 0))
        return self.name()

    def isCap(self):
        return self._type == 'cap'

    def isGroup(self):
        return self._type.startswith('group') or self._type.startswith('gdata') or self._type.startswith('gtotal')

    def getGroupId(self):
        if not self.isGroup():
            return 0
        return re.search('[0-9]+', self._type).group()

    def getGroupType(self):
        if not self.isGroup():
            return ''
        return re.search('[\D]+', self._type).group()

    def isField(self):
        return self._type == 'field'

    def setRowSpan(self, rowCount):
        self._rowSpan = rowCount

    def rowSpan(self):
        return self._rowSpan

    def setColumnSpan(self, columnCount):
        self._columnSpan = columnCount

    def columnSpan(self):
        return self._columnSpan

    def getAlignment(self):
        alignment = {
            0: QtCore.Qt.AlignLeft,
            1: QtCore.Qt.AlignCenter,
            2: QtCore.Qt.AlignRight
        }
        return alignment.get(self._alignment, QtCore.Qt.AlignLeft)

    def setAlignment(self, alignment):
        self._alignment = alignment

    def setBold(self, bold):
        self._bold = bold

    def getFont(self):
        font = QtGui.QFont()
        font.setBold(forceBool(self._bold))
        return font

    def toString(self):
        if self.isGroup():
            name = self._name
            for colId in re.findall('\{f(\d+)\}', name):
                item = self._modelCols.getItemByNumber(colId)
                name = name.replace(u'{f%s}' % colId,
                                    item.get('alias', u'') if item.get('alias') else item.get('field', u''))
            return self._modelFields.parcePathToTableNames(forceString(name))
        return self._name

    def toolTip(self):
        return self._value.get('tooltip', None)

    def color(self):
        if self.isField():
            return QtGui.QColor('darkGray')
        elif self.isGroup():
            id = forceInt(self.getGroupId())
            if id == 1:
                return QtGui.QColor('green')
            elif id == 2:
                return QtGui.QColor('limegreen')
            elif id == 3:
                return QtGui.QColor('lime')
            elif id == 4:
                return QtGui.QColor('greenyellow')
            elif id == 5:
                return QtGui.QColor('yellowgreen')
        return QtGui.QColor('white')

    def flags(self, index=None):
        result = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        if not self._readOnly:
            result |= QtCore.Qt.ItemIsEditable
        return result

    def createEditor(self, parent):
        if self.isField():
            editor = CRCComboBox(parent)
            editor.setModel(CRCColsItemModel(parent, modelCols=self._modelCols))
            editor.view().setMinimumWidth(400)
        elif self.isGroup():
            editor = CRCColsLineEdit(parent, self._modelCols, self._modelFields._modelFunctions)
        else:
            editor = QtGui.QLineEdit(parent)
        return editor

    def setEditorData(self, editor, value):
        if self.isField():
            editor.setIndex(self._value.get('number', 0) - 1)
        elif self.isGroup():
            editor.setValue(value)
        else:
            editor.setText(forceStringEx(value))

    def getEditorData(self, editor):
        if self.isField():
            self.setValue(editor.index() + 1)
            value = self._name
        elif self.isGroup():
            value = editor.getValue()
            self._value = {'tooltip': forceString(editor.text())}
        else:
            value = forceStringEx(editor.text())
        if value:
            return toVariant(value)
        else:
            return QtCore.QVariant()

    def setValue(self, number):
        number = forceInt(number)
        item = self._modelCols.getItemByNumber(number)
        if not item:
            return
        self._value['number'] = number
        self._value['tooltip'] = self._modelFields.parcePathToTableNames(item.get('field'))
        self._name = item.get('alias') if item.get('alias') else \
        self._modelFields.parcePathToTableNames(item.get('field')).split('.')[-1]


class CRCTableCapModel(QtCore.QAbstractTableModel):
    def __init__(self, parent, modelCols, modelGroups, modelFields=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._colsCount = 1
        self._items = []
        self._table = 'rcReport_TableCapCells'
        self._masterIdFieldName = 'master_id'
        self._modelCols = modelCols
        self._modelFields = modelFields
        self._modelGroups = modelGroups
        self._fieldRow = None
        self._groups = {}
        self._maxGroupCount = 5
        self.connect(self._modelCols, QtCore.SIGNAL('idChanged(int, int)'), self.on_modelCols_idChanged)
        self.connect(self._modelCols, QtCore.SIGNAL('reorderItems()'), self.on_modelCols_reorderItems)
        self.loadDefaut()

    def isEditable(self):
        return True

    def items(self):
        return self._items

    def addColumn(self, currentColumn):
        self.insertColumn(currentColumn)
        self._colsCount += 1
        newItems = []
        for i in range(len(self._items)):
            newItems.append({})
        for row, rowItems in enumerate(self._items):
            for column, item in rowItems.items():
                newColumn = column
                if column >= currentColumn:
                    newColumn += 1
                if (column < currentColumn) and (column + item.columnSpan() > currentColumn):
                    item._columnSpan += 1
                newItems[row][newColumn] = item
        self._items = newItems
        self.emitNeedSpanUpdate()

    def deleteColumn(self, currentColumn):
        self._colsCount -= 1
        newItems = []
        for i in range(len(self._items)):
            newItems.append({})
        for row, rowItems in enumerate(self._items):
            for column, item in rowItems.items():
                newColumn = column
                if column >= currentColumn:
                    newColumn -= 1
                if (column < currentColumn) and (column + item.columnSpan() > currentColumn):
                    item._columnSpan -= 1
                newItems[row][newColumn] = item
        self._items = newItems
        self.emitNeedSpanUpdate()

    def addRow(self, currentRow, type='cap'):
        self.insertRow(currentRow)
        newItems = []
        for i in range(len(self._items) + 1):
            newItems.append({})
        for row, rowItems in enumerate(self._items):
            newRow = row
            if row >= currentRow:
                newRow += 1
            for column, item in rowItems.items():
                if (row < currentRow) and (row + item.rowSpan() > currentRow):
                    item._rowSpan += 1
                newItems[newRow][column] = item

        if self._fieldRow >= currentRow:
            self._fieldRow += 1

        newGroups = {}
        for id, rowTypes in self._groups.items():
            newRowTypes = []
            for rowType, rows in rowTypes:
                newRows = [row + 1 if row >= currentRow else row for row in rows]
                newRowTypes.append((rowType, newRows))
            newGroups[id] = newRowTypes
        self._groups = newGroups
        self._items = newItems
        self.emitNeedSpanUpdate()

    def deleteGroupRow(self, row):
        if not self.isGroupRow(row):
            return
        curGroupId = self.getGroupRowId(row)
        curGroup = self._groups.get(curGroupId)
        newGroups = {}
        for groupId, group in self._groups.items():
            if groupId == curGroupId:
                continue
            newGroupId = groupId
            if groupId > curGroupId:
                newGroupId -= 1
            newGroups[newGroupId] = group
        self._groups = newGroups
        self.updateItemsType()
        deleteCounter = 0
        for rowType, rows in curGroup:
            for row in rows:
                self.deleteRow(row - deleteCounter)
                deleteCounter += 1
        self._modelGroups.deleteGroup(curGroupId)

    def addGroupRow(self):
        row = self.rowCount()
        group = self.getGroup()
        for id, rowTypes in group.items():
            for rowType, rows in rowTypes:
                rowType = '%s%d' % (rowType, id)
                for row in rows:
                    self.addRow(row, type=rowType)
        self._groups.update(group)

    def isGroupRow(self, curRow):
        """
        Проверка, что curRow принадлежит к строка группировки
        :param curRow:type int
        :return: возвращаем тип ряда группировки и id группировки, либо False
        """
        for id, rowTypes in self._groups.items():
            for rowType, rows in rowTypes:
                rowType = '%s%d' % (rowType, forceInt(id))
                for row in rows:
                    if row == curRow:
                        return rowType
        return False

    def getGroupRowId(self, curRow):
        for id, rowTypes in self._groups.items():
            for rowType, rows in rowTypes:
                rowType = '%s%d' % (rowType, forceInt(id))
                for row in rows:
                    if row == curRow:
                        return id
        return False

    def getDefaultGroupRowTypes(self):
        return [
            ('group', []),
            ('gtotal', [])
        ]

    def getGroup(self, id=0):
        if id:
            return {}
        if not self._groups:
            curRow = self._fieldRow
            newRowTypes = []
            for rowType, rows in self.getDefaultGroupRowTypes():
                rows = [curRow]
                curRow += 2
                newRowTypes.append((rowType, rows))
            return {1: newRowTypes}
        maxGroupId = max(self._groups.keys())
        newGroupId = maxGroupId + 1
        if newGroupId > self._maxGroupCount:
            return {}
        newRowTypes = []
        group = self._groups.get(maxGroupId)
        curRow = self._fieldRow
        for rowType, rows in self.getDefaultGroupRowTypes():
            rows = [curRow]
            curRow += 2
            newRowTypes.append((rowType, rows))
        return {newGroupId: newRowTypes}

    def updateGroup(self, id, type, row):
        rowTypes = self._groups.get(id, self.getDefaultGroupRowTypes())
        # isAdd = False
        for rowType, rows in rowTypes:
            if type == rowType:
                if not row in rows:
                    rows.append(row)
                rows.sort()
        self._groups[id] = rowTypes

    def getGroupFieldValue(self, index):
        groupId = self.getGroupRowId(index.row())
        return forceInt(self._modelGroups.getItem(groupId))

    def setGroupFieldValue(self, index, value):
        index.row()
        groupId = self.getGroupRowId(index.row())
        self._modelGroups.setItem(groupId, value)

    def deleteRow(self, currentRow):
        self.insertRow(currentRow)
        newItems = []
        for i in range(len(self._items) - 1):
            newItems.append({})
        for row, rowItems in enumerate(self._items):
            if row == currentRow:
                continue
            newRow = row
            if row > currentRow:
                newRow -= 1
            for column, item in rowItems.items():
                if (row < currentRow) and (row + item.rowSpan() > currentRow):
                    item._rowSpan -= 1
                newItems[newRow][column] = item
        self._items = newItems
        self.setFieldAndGroupRows()
        self.emitNeedSpanUpdate()

    def columnCount(self, index=QtCore.QModelIndex()):
        return self._colsCount

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self._items)

    def createEditor(self, index, parent):
        self.emit(QtCore.SIGNAL('editInProgress(bool)'), True)
        item = self.getItem(index)
        return item.createEditor(parent)

    def setEditorData(self, index, editor, value):
        return self.getItem(index).setEditorData(editor, value)

    def getEditorData(self, index, editor):
        return self.getItem(index).getEditorData(editor)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()
        item = self.getItem(index)
        if role == QtCore.Qt.EditRole:
            return item.name()

        if role == QtCore.Qt.DisplayRole:
            return item.toString()

        if role == QtCore.Qt.TextAlignmentRole:
            return item.getAlignment()

        if role == QtCore.Qt.ToolTipRole:
            return item.toolTip()

        if role == QtCore.Qt.BackgroundColorRole:
            return item.color()

        if role == QtCore.Qt.FontRole:
            return item.getFont()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            item = self.getItem(index)
            item.setName(forceStringEx(value))
            self.setItem(index, item)
            self.emitDataChanged(index.row(), index.column())
            return True
        return False

    def getItem(self, index):
        if not index.isValid():
            return None
        if index.row() >= len(self._items):
            return None
        return self.getItemEx(index.row(), index.column())

    def getItemEx(self, row, column):
        fieldRow = bool(row == self._fieldRow)
        groupRow = self.isGroupRow(row)
        type = 'cap'
        if fieldRow:
            type = 'field'
        elif groupRow:
            type = groupRow
        return self._items[row].setdefault(column, CRCCapItem(self, type=type))

    def setItem(self, index, item):
        if not index.isValid():
            return False
        self._items[index.row()][index.column()] = item
        return True

    def flags(self, index):
        flags = 0
        if not index.isValid():
            return flags
        flags = self.getItem(index).flags()
        return flags

    def afterUpdateEditorGeometry(self, editor, index):
        pass

    def emitNeedSpanUpdate(self):
        self.emit(QtCore.SIGNAL('needSpanUpdate()'))
        self.emitDataChanged(0, 0)

    def emitDataChanged(self, row, column):
        index = self.createIndex(row, column, self.getItem(self.createIndex(row, column)))
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)

    def loadDefaut(self):
        if not self._items:
            self.createTable(2, 2)

    def on_modelCols_idChanged(self, idFrom, idTo):
        for item in self._items[self._fieldRow].values():
            if item._value.get('id') == idFrom:
                item._value['id'] = forceString(idTo)

    def on_modelCols_reorderItems(self):
        for item in self._items[self._fieldRow].values():
            item.setValue(item._value.get('number'))
        self.reset()

    def loadItems(self, masterId):
        db = QtGui.qApp.db
        table = db.table(self._table)
        filterCond = [table[self._masterIdFieldName].eq(masterId)]
        cols = ['`name`', '`row`', '`column`', '`rowSpan`', '`columnSpan`', '`alignment`', '`bold`', '`type`']
        order = ['`row`', '`column`']
        items = db.getRecordList(table, cols, filterCond, order)
        if items:
            maxRow = max([forceInt(item.value('row')) for item in items])
            maxColumn = max([forceInt(item.value('column')) for item in items])
            self._items = []
            for i in range(maxRow + 1):
                self._items.append({})

            for record in items:
                row = forceInt(record.value('row'))
                column = forceInt(record.value('column'))
                name = forceString(record.value('name'))
                rowSpan = forceInt(record.value('rowSpan'))
                columnSpan = forceInt(record.value('columnSpan'))
                alignment = forceInt(record.value('alignment'))
                bold = forceBool(record.value('bold'))
                type = forceString(record.value('type'))
                self._items[row][column] = CRCCapItem(self, name, rowSpan, columnSpan, alignment, type=type, bold=bold)

            self._colsCount = maxColumn + 1
            self.setFieldAndGroupRows()

        self.emitNeedSpanUpdate()
        self.reset()

    def saveItems(self, masterId):
        db = QtGui.qApp.db
        table = db.table(self._table)
        filterCond = [table[self._masterIdFieldName].eq(masterId)]
        db.deleteRecord(table, filterCond)
        for row, items in enumerate(self._items):
            for column, item in items.items():
                record = table.newRecord()
                record.setValue('name', item.getValueToSave())
                record.setValue('row', row)
                record.setValue('column', column)
                record.setValue('rowSpan', item.rowSpan())
                record.setValue('columnSpan', item.columnSpan())
                record.setValue('master_id', masterId)
                record.setValue('alignment', item._alignment)
                record.setValue('bold', item._bold)
                record.setValue('type', item._type)
                db.insertRecord(table, record)

    def setFieldAndGroupRows(self):
        self._fieldRow = None
        self._groups = {}
        if not self._items:
            return
        for row, rowItems in enumerate(self._items):
            for column, item in rowItems.items():
                if item.isField():
                    self._fieldRow = row
                elif item.isGroup():
                    id = forceInt(item.getGroupId())
                    type = item.getGroupType()
                    self.updateGroup(id, type, row)

    def updateItemsType(self):
        for groupId, group in self._groups.items():
            for rowType, rows in group:
                for row in rows:
                    for column, item in self._items[row].items():
                        item._type = '%s%s' % (rowType, forceString(groupId))

    def createTable(self, rowCount, columnCount):
        if not (rowCount and columnCount):
            return
        self._items = []
        self._colsCount = columnCount
        for row in range(rowCount):
            self._items.append({})
            lastRow = forceBool(row == rowCount - 1)
            type = 'field' if lastRow else 'cap'
            for column in range(self._colsCount):
                self._items[row][column] = CRCCapItem(self, type=type)
        self._fieldRow = row
        self._groups = {}
        self.reset()
        self.emitNeedSpanUpdate()

    def clearTable(self):
        for row, rowItem in range(self._items):
            lastRow = forceBool(row == len(self._items) - 1)
            type = 'field' if lastRow else 'cap'
            for column, item in rowItem.items():
                self._items[row][column] = CRCCapItem(self, type=type)
        self.reset()
        self.emitNeedSpanUpdate()

    def deleteTable(self):
        self.createTable(2, 2)

    def fillFields(self):
        if not self._fieldRow == None and self._fieldRow < len(self._items):
            for column, item in self._items[self._fieldRow].items():
                item.setValue(column + 1)
            self.reset()


class CRCParamsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'rcReport_Params', 'id', 'master_id', parent)
        self.addCol(CRBInDocTableCol(u'Параметр', 'param_id', 20, 'rcParam'))
        self.modelParams = CRCItemModel(self, ['code', 'type_id', 'valueType_id', 'title', 'tableName', 'name'],
                                        'rcParam')
        self.modelParamsType = CRCItemModel(self, ['code'], 'rcParamType')
        self.modelParams.loadItems()
        self.modelParamsType.loadItems()
        self.rowsInserted.connect(self.emitModelDataChanged)
        self.rowsRemoved.connect(self.emitModelDataChanged)
        self.dataChanged.connect(self.emitModelDataChanged)

    def getParams(self, key='code'):
        result = {}
        for record in self._items:
            paramId = forceInt(record.value('param_id'))
            parametr = self.modelParams.getItem(paramId)
            code = forceString(paramId) if key == 'id' else parametr.get(key, '')
            if code and parametr:
                parametr.update({'type': self.modelParamsType.getItem(parametr.get('type_id', 0)).get('code'),
                                 'values': self.getCmbValues(parametr)})
                result[code] = parametr
        return result

    def getCmbValues(self, parametr):
        db = QtGui.qApp.db
        result = []
        if not self.modelParamsType.getItem(parametr.get('type_id', 0)).get('code') == 'customCmb':
            return result
        for record in db.getRecordList(
                'rcParam_Value',
                ['title', 'value'],
                'master_id = %s' % forceString(parametr.get('id', 0)),
                ['number']
        ):
            result.append((forceString(record.value('value')), forceString(record.value('title'))))
        return result

    def getIndexById(self, id):
        for idx, record in enumerate(self._items):
            if forceString(record.value(0)) == forceString(id):
                return idx
        return 0

    def getItemId(self, index):
        if isinstance(index, QtCore.QModelIndex):
            index = index.row()
        if index < len(self._items):
            return forceString(self._items[index].value('param_id'))
        return ''

    def getParamsById(self, id):
        result = {}
        for record in self._items:
            paramId = forceInt(record.value('param_id'))
            parametr = self.modelParams.getItem(paramId)
            code = parametr.get('code', '')
            if code:
                result[paramId] = parametr
        return result

    def emitModelDataChanged(self):
        self.emit(QtCore.SIGNAL('modelDataChanged()'))

    def deleteItem(self, row):
        if row < len(self._items):
            self._items = self._items[:row] + self._items[row + 1:]
            self.reset()


class CRCItemModel(QtCore.QAbstractTableModel):
    def __init__(self, parent, cols=None, tableName=''):
        if not cols:
            cols = []
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._tableName = tableName
        self._cols = cols
        self._idColName = 'id'
        self._records = []
        self._items = {}
        self.hasCode = forceBool('code' in cols)
        self.fieldCode = 'code'
        self.hasName = forceBool('name' in cols)
        self.fieldName = 'name'

    def loadItems(self):
        db = QtGui.qApp.db
        table = db.table(self._tableName)
        cols = [self._idColName]
        cols += self._cols
        self._records = db.getRecordList(table, cols)
        for record in self._records:
            item = {}
            for col in cols:
                item[str(col)] = forceString(record.value(col))
            self._items[forceRef(record.value(self._idColName))] = item

    def getItemId(self, index):
        return self.getItemByIndex(index).get('id')

    def value(self, index, field):
        return self.getItemId(index)

    def getItem(self, id):
        if not isinstance(id, int):
            id = forceInt(id)
        return self._items.get(id, {})

    def getItemByIndex(self, index):
        if index < len(self._items):
            return self._items.values()[index]
        return {}

    def getItemByCode(self, code):
        if self.hasCode:
            for item in self._items.values():
                if item[self.fieldCode] == code:
                    return item
        return {}

    def getItemIdByCode(self, code):
        if self.hasCode:
            for id, item in self._items.items():
                if item[self.fieldCode] == code:
                    return id
        return None

    def getIndexById(self, id):
        for index, value in enumerate(self._items.keys()):
            if forceInt(id) == forceInt(value):
                return index
        return 0

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self._items)

    def columnCount(self, index=QtCore.QModelIndex()):
        return 2 if self.hasCode else 1

    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = index.column()
        row = index.row()
        if 0 <= row < len(self._items):
            if role == QtCore.Qt.DisplayRole:
                if self.hasName:
                    col = self.fieldName
                elif self.hasCode:
                    col = self.fieldCode
                else:
                    col = self._cols[column]
                item = self._items.values()[row]
                return forceString(item.get(col))


class CRCConditionTypeItemModel(CRCItemModel):
    def __init__(self, parent, cols=None, tableName=''):
        CRCItemModel.__init__(self, parent, cols, tableName)
        self.OR = None
        self.AND = None

    def loadItems(self):
        CRCItemModel.loadItems(self)
        self.OR = self.getItemIdByCode('or')
        self.AND = self.getItemIdByCode('and')


class CRCGroupItemModel(CRCItemModel):
    def __init__(self, parent):
        cols = ['number', 'field']
        tableName = 'rcReport_Group'
        CRCItemModel.__init__(self, parent, cols, tableName)
        self._number = cols[0]
        self._field = cols[1]
        self._maxId = 0
        self._masterIdFieldName = 'master_id'
        self._dirty = False

    def getNewId(self):
        self._maxId += 1
        return self._maxId

    def getFieldValue(self, id):
        return self._items.get(forceInt(id), {}).get('field', None)

    def loadItems(self, masterId):
        db = QtGui.qApp.db
        table = db.table(self._tableName)
        cols = [self._idColName]
        cols += self._cols
        conds = []
        conds.append(table[self._masterIdFieldName].eq(masterId))
        self._records = db.getRecordList(table, cols, conds)
        for record in self._records:
            item = {}
            for col in cols:
                item[str(col)] = forceString(record.value(col))
            self._items[forceRef(record.value(self._idColName))] = item
        if self._items:
            self._maxId = max(self._items.keys())

    def saveItems(self, masterId):
        if not self._dirty:
            return
        db = QtGui.qApp.db
        table = db.table(self._tableName)
        filterCond = [table[self._masterIdFieldName].eq(masterId)]
        db.deleteRecord(table, filterCond)
        for item in self._items.values():
            record = table.newRecord()
            record.setValue('number', item.get('number', ''))
            record.setValue('field', item.get('field', ''))
            record.setValue('master_id', masterId)
            item['id'] = db.insertRecord(table, record)

    def getItem(self, number):
        for item in self._items.values():
            if forceInt(item.get(self._number)) == number:
                return item.get(self._field, '')
        return ''

    def setItem(self, number, value):
        curId = 0
        for id, item in self._items.items():
            if forceInt(item.get(self._number)) == number:
                curId = id
        if not curId:
            curId = self.getNewId()
        self._items[curId] = {self._number: number, self._field: value, self._idColName: forceString(curId)}
        self._dirty = True

    def getFieldValue(self, id):
        self._items.get(id, {}).get(self.fieldName)

    def deleteGroup(self, groupId):
        for id, item in self._items.items():
            if item.get('number') == groupId:
                self._items.pop(id)
            if item.get('number') > groupId:
                item['number'] = forceInt(item['number']) - 1
        self._dirty = True


class CRCColsItemModel(CRCItemModel):
    def __init__(self, parent, cols=None, tableName='', modelCols=None, addNone=False):
        CRCItemModel.__init__(self, parent, cols, tableName)
        self._masterIdFieldName = 'master_id'
        self._dirty = False
        self._modelFunctions = None
        self._modelCols = None
        self.addNone = addNone
        if addNone:
            self.addNoneItem()
        if modelCols:
            self.setModelCols(modelCols)

    def setModelCols(self, modelCols):
        self._modelCols = modelCols
        self.addItemsFromModelCols()

    def setModelFunctions(self, modelFunctions):
        self._modelFunctions = modelFunctions
        self.addItemsFromModelFunctions()

    def addItemsFromModelFunctions(self):
        if not self._modelFunctions:
            return
        functions = self._modelFunctions._items
        self.deleteItemsByType('func')
        for code, func in functions.items():
            self.addFuncinton(func.get('id'), u'$%s' % func.get('name'), func.get('description', u''))

    def addItemsFromModelCols(self):
        if not self._modelCols:
            return
        records = sorted(self._modelCols._items, key=lambda rec: forceInt(rec.value('number')))
        self.deleteItemsByType('field')
        for record in records:
            self.addInDocTableColumn(record, self._modelCols._baseModel)

    def deleteItemsByType(self, type):
        for key, item in self._items.items():
            if item.get('type') == type:
                self._items.pop(key)

    def loadItems(self, masterId):
        db = QtGui.qApp.db
        table = db.table(self._tableName)
        cols = [self._idColName]
        cols += self._cols
        conds = []
        conds.append(table[self._masterIdFieldName].eq(masterId))
        self._records = db.getRecordList(table, cols, conds)
        for record in self._records:
            item = {}
            for col in cols:
                item[str(col)] = forceString(record.value(col))
            self._items[forceRef(record.value(self._idColName))] = item
        if self._items:
            self._maxId = max(self._items.keys())

    def saveItems(self, masterId):
        if not self._dirty:
            return
        db = QtGui.qApp.db
        table = db.table(self._table)
        filterCond = [table[self._masterIdFieldName].eq(masterId)]
        db.deleteRecord(table, filterCond)
        for item in enumerate(self._items):
            record = table.newRecord()
            record.setValue('field', item.get('field', ''))
            record.setValue('master_id', masterId)
            item['id'] = db.insertRecord(table, record)

    def setItems(self, itemList, type):
        self._items = {}
        for index, item in enumerate(itemList):
            id = index + 1
            self._items.update(self.addItem(id, item, type))
        self._dirty = True

    def addFuncinton(self, id, name, description):
        id = u'$%s' % forceString(id)
        self._items[id] = {
            'field': name,
            'description': description if description else name,
            'type': 'func',
        }

    def addInDocTableColumn(self, record, modelFields=None):
        id = u'f%s' % forceInt(record.value('number'))
        self._items[id] = {
            'field': modelFields.parcePathToTableNames(
                forceString(record.value('field'))) if modelFields else forceString(record.value('field')),
            'alias': forceString(record.value('alias')),
            'description': forceString(record.value('comment')),
            'type': 'field',
            'number': forceInt(record.value('number'))
        }

    def addNoneItem(self):
        self._items[0] = {'field': u''}

    def addItem(self, item, type, id=None, description=u''):
        self.items.update(self.parceItem(item, type, id, description))

    def parceItem(self, item, type, id=None, description=u''):
        result = {}
        matchField = re.search(u'((\w+.)+)(`?\w+`?)( (as)? (`?\w+`?))?', item, re.IGNORECASE)
        if id:
            id = forceString(id)
        if matchField and type == 'field':
            result[id] = {
                'field': matchField.groups()[3],
                'alias': matchField.groups()[5],
                'id': id,
                'description': description if description else item,
                'type': 'field'
            }
        return result

    def getFuncIdByName(self, funcName):
        if not self._modelFunctions:
            return u''
        for id, item in self._items.items():
            if item.get('type') == 'func' and item.get('field') == funcName:
                return id
        return u''

    def getFieldIdByName(self, fieldName):
        if not self._modelCols:
            return u''
        for id, item in self._items.items():
            if item.get('type') == 'field' and (
            item.get('alias') if item.get('alias') else item.get('field')) == fieldName:
                return id
        return u''

    def getValue(self, text):
        wordList = self.getWordList(text)
        funcPattern = re.compile('\$\w+')
        fieldPattern = re.compile('(\w+(.\w+)?)', re.U)
        labelPattern = re.compile('\'.+\'', re.U)
        result = []
        for word in wordList:
            if re.search(funcPattern, word):
                result.append(
                    u'{%s}' % re.sub(funcPattern, self.getFuncIdByName(re.search(funcPattern, word).group()), word))
            elif re.search(labelPattern, word):
                result.append(word)
            elif re.search(fieldPattern, word):
                result.append(
                    u'{%s}' % re.sub(fieldPattern, self.getFieldIdByName(re.search(fieldPattern, word).group()), word))
            else:
                result.append(word)
        return u''.join(result)

    def getWordList(self, text):
        if re.search('^\'.+\'$', text):
            return [forceString(text)]
        return [forceString(word) for word in re.split('([ \(\)])', text)]

    def getFieldValue(self, id):
        self._items.get(id, {}).get(self.fieldName)

    def parceValue(self, value):
        for id in re.findall('\{([\$f]\d+)\}', value, re.U):
            item = self._items.get(id)
            if item:
                value = value.replace(u'{%s}' % id, item.get('alias') if item.get('alias') else item.get('field'))
        return value

    def data(self, index, role=QtCore.Qt.DisplayRole):
        # column = index.column()
        row = index.row()
        # item = index.internalPointer()
        if 0 <= row < len(self._items):
            if role == QtCore.Qt.DisplayRole:
                item = sorted(self._items.values(), key=lambda item: item.get('number', item.get('field', u'')))[row]
                return forceString(item.get('alias') if item.get('alias') else item.get('field'))
