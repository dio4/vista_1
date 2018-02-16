# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2014 Vista Software. All rights reserved.
##
#############################################################################


from PyQt4 import QtCore
from library.QueryFilter.QueryFilterItem import CQueryFilterItem
from library.Utils import skipCurrentXMLElement, readNextStartXMLElement

'''
Created on 04.03.2014

@author: atronah
'''


class CQueryFilterItemModel(QtCore.QAbstractTableModel):
    # Названия столбцов
    _headerData = [u'Название',
                   u'Оператор',
                   u'Значение']
    
    # Индексы столбцов
    ciName = 0
    ciOperator = 1
    ciValue = 2
    
    _xmlRootTagName = 'registry' #FIXME: atronah: разобраться с дублированием константы (CCustomizableRegistryModel._xmlRegistryTagName)
    _xmlTagName = 'filterItemList'
    
    def __init__(self, parent = None):
        super(CQueryFilterItemModel, self).__init__(parent)
        self._items = []
        self._isDirty = False
        self.dataChanged.connect(self.setAsDirty)
        
    
    ## Проверяет индекс на корректность.
    def validateIndex(self, index):
        if not index.isValid():
            return False
        
        row = index.row()
        if row not in xrange(self.rowCount()):
            return False
        
        column = index.column()
        if column not in xrange(self.columnCount()):
            return False
        
        return True
    
    
    ## Очистка списка/модели фильтров
    def clear(self):
        self.beginRemoveRows(QtCore.QModelIndex(), 0, self.rowCount() - 1)
        while self._items:
            filterItem, operatorIdx, valueList = self._items.pop(0)
            del filterItem
            del operatorIdx
            del valueList
        self.endRemoveRows()
        
        
    def setDirty(self, isDirty):
        self._isDirty = isDirty
    
    
    @QtCore.pyqtSlot()
    def setAsDirty(self):
        self.setDirty(True)
        
    
    def isDirty(self):
        return self._isDirty
    
        
    ## Добавление нового фильтра в модель
    def addFilterItem(self, filterItem, idx = None):
        if not isinstance(filterItem, CQueryFilterItem):
            return False
        
        if idx is None:
            idx = self.rowCount()
        
        if idx not in xrange(self.rowCount() + 1):
            return False
        
        self.beginInsertRows(QtCore.QModelIndex(), idx, idx)
        self._items.insert(idx, filterItem)
        self.endInsertRows()
    
    
    ## Возвращает класс, описывающий фильтр, находящийся по указанному индексу/номеру строки
    # @param index: либо индекс (QModelIndex) либо номер строки модели
    def filterItem(self, index):
        if isinstance(index, QtCore.QModelIndex):
            if self.validateIndex(index):
                row = index.row()
        elif isinstance(index, int):
            row = index
        else:
            row = None
        
        return self._items[row]
    
    
    ## Возвращает класс, описывающий оператор фильтра, находящийся по указанному индексу/номеру строки
    # @param index: либо индекс (QModelIndex) либо номер строки модели
#    def filterOperator(self, index):
#        filterItem, filterOperatorIdx = self.getFilterInfo(index)[:2]
#        return filterItem.operatorModel().operator(filterOperatorIdx) if filterItem else None
    
    
    ## Возвращает номер выбранного оператора фильтра, находящийся по указанному индексу/номеру строки
    # @param index: либо индекс (QModelIndex) либо номер строки модели
#    def filterOperatorIdx(self, index):
#        return self.getFilterInfo(index)[1]

    
    ## Возвращает список значений фильтра для указанной строки модели
    # @param index: либо индекс (QModelIndex) либо номер строки модели
#    def filterValueList(self, index):
#        return self.getFilterInfo(index)[2]
            
    
    ## Возвращает количество отображаемых столбцов модели
    def columnCount(self, parent = QtCore.QModelIndex()):
        return len(self._headerData)
    
    
    ## Возвращает количество отображаемых строк
    def rowCount(self, parent = QtCore.QModelIndex()):
        return len(self._items)
    
    
    ## Возвращает флаги элемента, влияющие на его поведение в отображении.
    def flags(self, index):
        flags = QtCore.Qt.NoItemFlags
        if self.validateIndex(index):
            column = index.column()
            if column in [self.ciName, self.ciOperator, self.ciValue]:
                flags |= QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
            
            if column in [self.ciOperator, self.ciValue]:
                flags |= QtCore.Qt.ItemIsEditable
        
        return flags
    
    
    
    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):        
        if orientation == QtCore.Qt.Horizontal:
            if section in xrange(len(self._headerData)):
                if role == QtCore.Qt.DisplayRole:
                    return QtCore.QVariant(self._headerData[section])
        return super(CQueryFilterItemModel, self).headerData(section, orientation, role)
        
    
    
    ## Предоставляет данные указанной ячейки для указанной роли
    def data(self, index, role = QtCore.Qt.DisplayRole):
        if not self.validateIndex(index):
            return QtCore.QVariant()
        
        column = index.column()
        if role ==  QtCore.Qt.DisplayRole:
            if column == self.ciName:
                filterItem = self.filterItem(index)
                return QtCore.QVariant(filterItem.caption if filterItem else u'<ОШИБКА>')
            elif column == self.ciOperator:
                filterOperator = self.filterItem(index).currentOperator
                return QtCore.QVariant(filterOperator.caption if filterOperator else u'<ОШИБКА>')
            elif column == self.ciValue:
                filterItem = self.filterItem(index)
                if filterItem:
                    valueString = filterItem.currentOperator.encodeValueToString(filterItem.value, isHumanReadable = True)
                else:
                    valueString = u'<ОШИБКА>'
                return QtCore.QVariant(valueString)
        elif role == QtCore.Qt.EditRole:
            if column == self.ciOperator:
                QtCore.QVariant(self.getFilterInfo(index)[1])
            elif column == self.ciValue:
                QtCore.QVariant(self.filterValueList(index))
    


    def resetFilters(self):
        for idx in xrange(self.rowCount()):
            self.clearValue(self.index(idx, self.ciValue))


    def clearValue(self, index):
        return self.setData(self.index(index.row(), self.ciValue), QtCore.QVariant())
    
    
    ## Заносит новые данные в ячейку
    def setData(self, index, value, role = QtCore.Qt.EditRole):
        if not self.validateIndex(index):
            return False
        
        if role == QtCore.Qt.EditRole:
            row = index.row()
            column = index.column()
            if column == self.ciOperator:
                if not self._items[row].setCurrentOperatorIndex(value):
                    return False
                self.dataChanged.emit(index, index)
                return True
            elif column == self.ciValue:
                self._items[row].setValue(value)
                self.dataChanged.emit(index, index)
                return True
        return False
        
    
    ## Загружает фильтры из XML файла
    def loadFromXML(self, source):        
        xmlReader = QtCore.QXmlStreamReader(source)
        while readNextStartXMLElement(xmlReader):
            if xmlReader.name() == self._xmlRootTagName:
                continue
            elif xmlReader.name() == self._xmlTagName:
                break
            else:
                skipCurrentXMLElement(xmlReader)
            
        while readNextStartXMLElement(xmlReader):
            if xmlReader.name() == CQueryFilterItem._xmlTagName:
                filterItem = CQueryFilterItem.loadFromXML(xmlReader)
                self.addFilterItem(filterItem)
            else:
                skipCurrentXMLElement(xmlReader)  
        return True
    
    
    ## Получение списка фильтров    
    def getConditionList(self):
        result = []
        for filterItem in self._items:
            if not filterItem.value.isValid():
                continue
            result.append(filterItem.compileCondition(isHumanReadable = False))
        return result
    
