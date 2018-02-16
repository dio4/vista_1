# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from library.ExtendedTableView import CExtendedTableView
from library.TableModel import CBoolCol, CNameCol
import copy


class CActionTemplatePrintTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.dataIsValid = True
        self._items = []
        self._itemsDict = {}
        self._cols = []
        self.addColumn(CNameCol(u'Наименование', ['actionName'], 200))
        self.addColumn(CNameCol(u'Шаблон печати', ['templateName'], None))
        self.addColumn(CBoolCol(u'', ['print'], 20))

    def columnCount(self, index=QtCore.QModelIndex()):
        return len(self._cols)

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self._items)

    def setItems(self, items, dirty=False, lazy=False):
        """input:
            items: dictionary:
            key: id
            value: dict{'name': str , 'actionData': list(tuple(int, dateTime)), 'templates': list(template))
            template: tuple"""
        self._isDirty = dirty
        self._itemsDict = copy.deepcopy(items)
        self._items = []
        for id, val in self._itemsDict.items():
            printValue = True
            if lazy and len(val['templates']):
                templates = [val['templates'][0]]
            else:
                templates = val['templates']
            for template in templates:
                value = {'templateName'        : template[0],
                         'templateId'          : template[1],
                         'templateDpdAgreement': template[2],
                         'templateBanUnkeptDat': template[3],
                         'template'            : template,
                         'actionName'          : val['name'],
                         'actionId'            : id,
                         'print'               : printValue,
                         'actionData'          : val['actionData'],
                         }
                if len(templates) == 1:
                    self._items.append(value)
                    del self._itemsDict[id]
                else:
                    self._items.append(value)
                printValue = False
        self.reset()
        pass

    def spanInfo(self):
        result = []
        row = 0
        for items in self._itemsDict.values():
            length = len(items['templates'])
            result.append((row, 0, length, 1))
            row += length
        return result

    def getValue(self, index):
        row = index.row()
        column = index.column()
        col = self._cols[column]
        result = []
        for field in col.fields():
            result.append(QtCore.QVariant(self._items[row][field]))
        return col, result

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()
        column = index.column()
        if role == QtCore.Qt.DisplayRole:  # or role == QtCore.Qt.EditRole:
            (col, values) = self.getValue(index)
            return col.format(values)
        elif role == QtCore.Qt.UserRole:
            (col, values) = self.getValue(index)
            return values[0]
        elif role == QtCore.Qt.TextAlignmentRole:
            col = self._cols[column]
            return col.alignment()
        elif role == QtCore.Qt.CheckStateRole:
            (col, values) = self.getValue(index)
            return col.checked(values)
        elif role == QtCore.Qt.ForegroundRole:
            (col, values) = self.getValue(index)
            return col.getForegroundColor(values)
        elif role == QtCore.Qt.BackgroundRole:
            (col, values) = self.getValue(index)
            return col.getBackgroundColor(values)
        elif role == QtCore.Qt.DecorationRole:
            (col, values) = self.getValue(index)
            return col.getDecoration(values)
        return QtCore.QVariant()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.CheckStateRole:
            self._items[index.row()]['print'] = value == QtCore.Qt.Checked
            self.dataIsValid = self.checkData()
            self.dataChanged.emit(index, index)
            return True
        return super(CActionTemplatePrintTableModel, self).setData(index, value, role)

    def checkData(self):
        temp = {}
        result = True
        for item in self._items:
            actionId = item['actionId']
            if not temp.has_key(actionId):
                temp[actionId] = False
            temp[actionId] = temp[actionId] | item['print']
        for values in temp.values():
            result = result & values
        return result

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                if section in xrange(len(self._cols)):
                    return QtCore.QVariant(self._cols[section].title())
        return QtCore.QVariant()

    def addColumn(self, col):
        self._cols.append(col)

    def getColumnFields(self, column):
        return self._cols[column].fields()

    def flags(self, index):
        flags = super(CActionTemplatePrintTableModel, self).flags(index) | QtCore.Qt.ItemIsSelectable
        if index.isValid():
            fields = self.getColumnFields(index.column())
            row = index.row()
            if self._items[row]['templateBanUnkeptDat'] == 1 and self._isDirty and not 'actionName' in fields:
                flags = QtCore.Qt.NoItemFlags
            if 'print' in fields:
                return flags | QtCore.Qt.ItemIsUserCheckable
        return flags


class CActionTemplatePrintTableView(CExtendedTableView):
    def __init__(self, parent=None):
        super(CActionTemplatePrintTableView, self).__init__(parent)
        self.verticalHeader().hide()
        self.setSelectionMode(QtGui.QAbstractItemView.NoSelection)

    def setModel(self, model):
        super(CActionTemplatePrintTableView, self).setModel(model)
        for i, col in enumerate(model._cols):
            if (col.defaultWidth()):
                self.setColumnWidth(i, col.defaultWidth())
            else:
                self.horizontalHeader().setResizeMode(i, QtGui.QHeaderView.Stretch)
