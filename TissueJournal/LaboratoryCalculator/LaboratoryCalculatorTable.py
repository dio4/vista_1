# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from decimal import Decimal, Context

from PyQt4 import QtCore, QtGui, QtSql

from library.PreferencesMixin   import CPreferencesMixin
from library.Utils              import forceDouble, forceInt, forceString, forceStringEx, smartDict


FiledType = smartDict()
FiledType.PercentType = '%'
FiledType.GlobalType  = 'A'

groupList = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D']

class CLaboratoryCalculatorTableModel(QtCore.QAbstractTableModel):
    horizontalHeaders = [u'Имя свойства(А)', u'А', u'Сумма', u'%', u'Имя свойства(%)', u'Группа']
    fields        = [('name(A)', QtCore.QVariant.String), 
                     ('A', QtCore.QVariant.Int), 
                     ('Sum', QtCore.QVariant.Int), 
                     ('%', QtCore.QVariant.Double), 
                     ('name(%)', QtCore.QVariant.String), 
                     ('group', QtCore.QVariant.String)]
    
    ciPropNameGlobal  = 0
    ciGlobalCount     = 1
    ciGroupSumm       = 2
    ciPercentCount    = 3
    ciPropNamePercent = 4
    
    def __init__(self, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._parent = parent
        self.clear()
        self.resetAdditional(False)
        self._inputData = None
        self._maxGroupValue = 100
        self._rounding = 0
        self._locale = QtCore.QLocale()
        
        
        self._historyPointer = 0
        self._history = []
        self._needToSave = False
        self._onHistoryPointer = True
        
        self._emptyItem = smartDict(
                                    items=[], 
                                    mapKeyToRow={}, 
                                    mapGroupToRows={}, 
                                    mapNameToRow={}, 
                                    mapRowToGroup={}, 
                                    mapRowToButtonKey={}, 
                                    mapPropertyTypeIdToCoords={}
                                   )
        self._history.append(self._emptyItem)
        
    def setRounding(self, rounding):
        self._rounding = rounding
        
    def load(self, data):
        if data:
            self._inputData = data
            self.clear()
            for value in data.split(';'):
                value = forceStringEx(value).strip('()').split(',')
                itemValues = int(value[0]), value[1], value[2]
                self._fullStruct.append(itemValues)
            self._fullStruct.sort(key=lambda item: item[1][2]) # сортирует по группам
        self.addItems()
        if self._additionalItems:
            for item in self._additionalItems:
                item.setValue('A', QtCore.QVariant())
                item.setValue('Sum', QtCore.QVariant())
                item.setValue('%', QtCore.QVariant())
        self.reset()
            
    def acceptKeys(self):
        self._parent.enabledKeys(self._mapKeyToRow.keys())
            
            
    def hasOuterItems(self):
        return bool(len(self._items))
            
            
    def addItems(self):
        for itemValues in self._fullStruct:
            self.addItem(itemValues)
        self.acceptKeys()
            
    def addItem(self, values):
        propertyTypeId, settings, propertyTypeName = values
        buttonKey = settings[0]
        fieldNameType = settings[1]
        group = settings[2]
        column = 1 if fieldNameType == 'A' else 3
        if propertyTypeName in self._mapNameToRow.keys():
            row = self._mapNameToRow[propertyTypeName]
            item = self._items[row]
        else:
            item = self.getNewRecord()
            self._items.append(item)
            row = len(self._items)-1
            self._mapNameToRow[propertyTypeName] = row
            result = self._mapGroupToRows.setdefault(group, [row])
            self._mapRowToGroup[row] = group
            if not row in result:
                result.append(row)
            
        self.mapKeyToRow(buttonKey, row, fieldNameType)
            
        valueCords = (row, column)
        self._mapPropertyTypeIdToCoords[propertyTypeId] = valueCords
        
        buttonKeyList = self._mapRowToButtonKey.setdefault(row, [buttonKey])
        if not buttonKey in buttonKeyList:
            buttonKeyList.append(buttonKey)
            
        existsGroupValue = forceStringEx(item.value('group'))
        if existsGroupValue and existsGroupValue != group:
            newGroupValue = existsGroupValue+'|'+group 
        else:
            newGroupValue = group
            
        item.setValue('group', QtCore.QVariant(newGroupValue))
        item.setValue('name('+fieldNameType+')', propertyTypeName)
        
    def addAdditionalRow(self, key, group, name):
        if not name:
            name = '-----'
        self._mapAdditionalKeyToGroup[key] = group
        item = self.getNewRecord()
        item.setValue('name(A)', QtCore.QVariant(name))
        item.setValue('name(%)', QtCore.QVariant(name))
        item.setValue('group', QtCore.QVariant(group))
        self._additionalItems.append(item)
        row = len(self._items) + len(self._additionalItems)-1
        
        self.mapKeyToRow(key, row, 'A')
        self.mapKeyToRow(key, row, '%')
        
        result = self._mapGroupToRows.setdefault(group, [row])
        self._mapRowToGroup[row] = group
        if not row in result:
            result.append(row)
            
        buttonKeyList = self._mapRowToButtonKey.setdefault(row, [key])
        if not key in buttonKeyList:
            buttonKeyList.append(key)
            
        self.updateDataForGroup(row)
            
        self.reset()
        
    def resetAdditional(self, sentData=True):
        for key in self._mapAdditionalKeyToGroup.keys():
            del self._mapKeyToRow[key]
        realItemsCount = len(self._items)
        for row in range(realItemsCount, len(self._additionalItems)+realItemsCount):
            del self._mapRowToButtonKey[row]
            group = self._mapRowToGroup[row]
            del self._mapRowToGroup[row]
            rows = self._mapGroupToRows[group]
            if row in rows:
                del rows[rows.index(row)]
            
        self._mapAdditionalKeyToGroup = {}
        self._additionalItems = []
        
        self.reset()
        
        for row in range(realItemsCount):
            self.updateDataForGroup(row)
            self.countPercentValueForGroup(row)
            
        if sentData:
            self._parent.sentData()
        
    def mapKeyToRow(self, buttonKey, row, fieldNameType):
        if buttonKey in self._mapKeyToRow.keys():
            self._mapKeyToRow[buttonKey].append((row, fieldNameType))
        else:
            self._mapKeyToRow[buttonKey] = [(row, fieldNameType)]
                
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()
        row    = index.row()
        column = index.column()
        if role == QtCore.Qt.DisplayRole:
            realItemsCount = len(self._items)
            additionalItemsCount = len(self._additionalItems)
            item = None
            if 0 <= row and row < realItemsCount: 
                item = self._items[row]
            elif  realItemsCount <= row and row < additionalItemsCount+realItemsCount:
                item = self._additionalItems[row-realItemsCount]
            if item:
                value = item.value(CLaboratoryCalculatorTableModel.fields[column][0])
                if column == CLaboratoryCalculatorTableModel.ciPercentCount:
                    value = forceDouble(value)
                    value = QtCore.QVariant(self._locale.toString(value, 'f', self._rounding))
                return value
        return QtCore.QVariant()
        
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid() and role == QtCore.Qt.EditRole:
            realItemsCount = len(self._items)
            additionalItemsCount = len(self._additionalItems)
            row = index.row()
            item = None
            if 0 <= row and row < realItemsCount: 
                item = self._items[row]
            elif  realItemsCount <= row and row < additionalItemsCount+realItemsCount:
                item = self._additionalItems[row-realItemsCount]
            if item:
                column = index.column()
                fieldName = CLaboratoryCalculatorTableModel.fields[column][0]
                item.setValue(fieldName, value)
                self.emitRowDataChanged(row)
                if column == CLaboratoryCalculatorTableModel.ciGlobalCount:
                    self.updateDataForGroup(row)
                return True
        return False
        
    def emitRowDataChanged(self, row):
        begIndex = self.index(row, 0)
        endIndex = self.index(row, self.columnCount()-1)
        self.emitDataChanged(begIndex, endIndex)
        
    def emitDataChanged(self, begIndex, endIndex):
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex,QModelIndex)'), begIndex, endIndex)
        
    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return QtCore.QVariant(CLaboratoryCalculatorTableModel.horizontalHeaders[section])
            elif orientation == QtCore.Qt.Vertical:                
                bittonKeyList = self._mapRowToButtonKey[section]
                return QtCore.QVariant('|'.join(bittonKeyList))
        return QtCore.QVariant()
            
    
    def columnCount(self, index=QtCore.QModelIndex()):
        return len(CLaboratoryCalculatorTableModel.horizontalHeaders)
        
    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self._items) + len(self._additionalItems)
        
    def availableGroupList(self):
        return groupList
        
    def clear(self):
        self._origStruct = []
        self._fullStruct = []
        self._items = []
        self._additionalItems = []
        self._mapAdditionalKeyToGroup = {}
        self._mapKeyToRow  = {}
        self._mapGroupToRows = {}
        self._mapNameToRow = {}
        self._mapRowToGroup = {}
        self._mapRowToButtonKey = {}
        self._mapPropertyTypeIdToCoords = {}
            
    def additionalKeyList(self):
        return self._mapAdditionalKeyToGroup.keys()
            
    def copyItems(self, items=None):
        if not items:
            items = []
        newItems = []
        for item in items:
            newItems.append(QtSql.QSqlRecord(item))
        return newItems
            
    def saveSetData(self):
        if self._needToSave:
                
            itemToSave = smartDict()
            itemToSave.items = self.copyItems(self._items)
            itemToSave.additionalItems = self.copyItems(self._additionalItems)
            itemToSave.mapAdditionalKeyToGroup = dict(self._mapAdditionalKeyToGroup)
            itemToSave.mapKeyToRow = dict(self._mapKeyToRow)
            itemToSave.mapGroupToRows = dict(self._mapGroupToRows)
            itemToSave.mapNameToRow = dict(self._mapNameToRow)
            itemToSave.mapRowToGroup = dict(self._mapRowToGroup)
            itemToSave.mapRowToButtonKey = dict(self._mapRowToButtonKey)
            itemToSave.mapPropertyTypeIdToCoords = dict(self._mapPropertyTypeIdToCoords)
            self._history.append(itemToSave)
            
            self._historyPointer += 1
            self._onHistoryPointer = True
            self._needToSave = False
        
    def loadLastSetData(self):
        if self._onHistoryPointer:
            self.downHistoryPointer()
        if self._historyPointer > 0:
            itemToLoad = self._history[self._historyPointer]
            
            self._items = self.copyItems(itemToLoad.items)
            self._additionalItems = self.copyItems(itemToLoad.additionalItems)
            self._mapAdditionalKeyToGroup = itemToLoad.mapAdditionalKeyToGroup
            self._mapKeyToRow  = itemToLoad.mapKeyToRow
            self._mapGroupToRows = itemToLoad.mapGroupToRows 
            self._mapNameToRow = itemToLoad.mapNameToRow
            self._mapRowToGroup = itemToLoad.mapRowToGroup
            self._mapRowToButtonKey = itemToLoad.mapRowToButtonKey
            self._mapPropertyTypeIdToCoords = itemToLoad.mapPropertyTypeIdToCoords
            
            self._onHistoryPointer = True
            self._needToSave = False
        else:
            self.clear()
            self._history = [self._emptyItem]
            self._historyPointer = 0
            self.resetData()
            
        self.reset()
        
    def downHistoryPointer(self):
        self._historyPointer -= 1
        del self._history[-1]
        
    def reset(self):
        QtCore.QAbstractTableModel.reset(self)
        
    def resetData(self):
        self.load(self._inputData)
        
        
    def commands(self, keyList=None):
        if not keyList:
            keyList = []
        for key in keyList:
            self.command(key)
        
        
    def command(self, key):
        CLaboratoryCalculatorTableModel.__dict__.get(key, lambda val: val)(self)
        
    def done(self, key, rounding=0):
        result = False
        for cellDescription in self._mapKeyToRow.get(key, []):
            result = True
            row, fieldType = cellDescription
            if forceInt(self.data(self.index(row, CLaboratoryCalculatorTableModel.ciGroupSumm))) < self._maxGroupValue:
                if self.needDoneGlobalRowValue(key, fieldType):
                    self._needToSave = True
                    self._onHistoryPointer = False
                    self.doneGlobalRowValue(row)
                    self.countPercentValueForGroup(row, rounding)
            else:
                QtGui.QApplication.beep()
                return result
        if result:
            self.saveSetData()
        return result
        
    def setMaxGroupValue(self, val):
        self._maxGroupValue = val
        
    def needDoneGlobalRowValue(self, key, fieldType):
        if fieldType == FiledType.GlobalType:
            return True
        result = True
        for row, fieldType in self._mapKeyToRow.get(key, []):
            if fieldType == FiledType.GlobalType:
                result = False
        return result
        
    def doneGlobalRowValue(self, row):
        column = CLaboratoryCalculatorTableModel.ciGlobalCount
        fieldName = CLaboratoryCalculatorTableModel.fields[column][0]
        
        realItemsCount = len(self._items)
        additionalItemsCount = len(self._additionalItems)
        item = None
        if 0 <= row and row < realItemsCount: 
            item = self._items[row]
        elif  realItemsCount <= row and row < additionalItemsCount+realItemsCount:
            item = self._additionalItems[row-realItemsCount]
        if item:
            value = forceInt(item.value(fieldName))+1
            self.setData(self.index(row, column), QtCore.QVariant(value))
        
    def updateDataForGroup(self, row):
        rows = self.getGroupRows(row)
        rowGroupData = 0
        for row in rows:
            rowGroupData += forceInt(self.data(self.index(row, CLaboratoryCalculatorTableModel.ciGlobalCount)))
        for row in rows:
            self.setData(self.index(row, CLaboratoryCalculatorTableModel.ciGroupSumm), QtCore.QVariant(rowGroupData))
        
        
    def countPercentValueForGroup(self, row, rounding=0):
        column = CLaboratoryCalculatorTableModel.ciPercentCount
        rows = self.getGroupRows(row)
        for row in rows:
            rowGroupData = forceInt(self.data(self.index(row, CLaboratoryCalculatorTableModel.ciGroupSumm)))
            if rowGroupData:
                rowData = forceInt(self.data(self.index(row, CLaboratoryCalculatorTableModel.ciGlobalCount)))
                value = (100.0*rowData)/rowGroupData
                
                decimalValue = Decimal(unicode(value))
                context = Context(prec=rounding+len(str(int(value))))
                value = float(decimalValue.normalize(context)/1)
                
                self.setData(self.index(row, column), QtCore.QVariant(value))
        
    def recountPercentValueForGroup(self, rounding=0):
        for row in xrange(self.rowCount()):
            self.countPercentValueForGroup(row, rounding)
        
    def getGroupRows(self, row):
        group = self._mapRowToGroup[row]
        return self._mapGroupToRows.get(group, [])
        
    def formatData(self):
        self.saveSetData()
        valueList = []
        for propertyTypeId in self._mapPropertyTypeIdToCoords.keys():
            valueCoords = self._mapPropertyTypeIdToCoords[propertyTypeId]
            value = forceString(self.data(self.index(*valueCoords)))
            valueList.append(u'('+unicode(propertyTypeId)+', '+unicode(value)+')')
        return ';'.join(valueList)
            
    @classmethod
    def getNewRecord(cls):
        record = QtSql.QSqlRecord()
        for fieldName, fieldType in cls.fields:
            record.append(QtSql.QSqlField(fieldName, fieldType))
        return record
    
    
# ###############################################


class CLaboratoryCalculatorTableView(QtGui.QTableView, CPreferencesMixin):
    def __init__(self, parent):
        QtGui.QTableView.__init__(self, parent)
        self._popupMenu = None

        h = self.fontMetrics().height()
        self.verticalHeader().setDefaultSectionSize(3*h/2)
#        self.verticalHeader().hide()
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setStretchLastSection(True)
    
    
    
