# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

"""
Created on 26.02.2013

@author: atronah
"""

from PyQt4 import QtCore

from library.Utils                              import toVariant
from Reports.ReportsGenerator.TemplateParameter import CTemplateParameter, CParameterDelegate


class CTemplateParametersModel(QtCore.QAbstractTableModel):
    def __init__(self, parent = None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._paramList = []
        self._horizontalHeaderInfo = [#1 column
                                    {'title' : u'Название', 
                                     'toolTip' : u'Название параметра'}, 
                                    #2 column
                                    {'title' : u'Значение',
                                     'toolTip' : u'Значение параметра'}
                                    ]

        self._numberToolTip = u'Номер параметра по порядку для использования в шаблоне отчета'
        self._itemDelegate = CParameterDelegate()
    
    
#    def __del__(self):
#        self.clear()
        
    
    def clear(self):
        for param in self._paramList:
            param.disconnectFromWidget()
        
        self.emit(QtCore.SIGNAL('beginRemoveRows(QtCore.QModelIndex, int, int)'), QtCore.QModelIndex(), 0, self.rowCount() - 1)
        self._paramList = []
        self.emit(QtCore.SIGNAL('endRemoveRows()'))
        self.reset() #TODO: atronah: Для сборок со свежими библиотеками заменить на beginResetModel и endResetModel
    
    
    def itemDelegate(self):
        return self._itemDelegate
    
    
    def data(self, index, role = QtCore.Qt.DisplayRole):
        value = None
        if not index.isValid():
            return toVariant(value)
        
        row = index.row()
        if row < self.rowCount():
            column = index.column()
            if role == QtCore.Qt.DisplayRole:
                if column == 0:   #caption
                    value = self._paramList[row].caption()
                elif column == 1:   #value
                    parameter = self._paramList[row] 
                    value = parameter.toString(parameter.value())
            
            elif role == QtCore.Qt.EditRole:
                if column == 1:   #value
                    parameter = self._paramList[row] 
                    value = parameter.value()
            
            elif role == QtCore.Qt.ToolTipRole or role == QtCore.Qt.StatusTipRole:
                parameter = self._paramList[row] 
                value = parameter.name()
        return toVariant(value)
    
    
    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        value = None
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                value = self._horizontalHeaderInfo[section]['title']
            elif role == QtCore.Qt.ToolTipRole or role == QtCore.Qt.StatusTipRole:
                value = self._horizontalHeaderInfo[section]['toolTip']
        else:
            if role == QtCore.Qt.DisplayRole:
                value = section + 1
            elif role == QtCore.Qt.ToolTipRole or role == QtCore.Qt.StatusTipRole:
                value = self._numberToolTip
        return toVariant(value)
    
    
    def flags(self, index):
        flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        if index.column() == 1: #value
            flags |= QtCore.Qt.ItemIsEditable
        return flags
    
    
    def setData(self, index, value, role = QtCore.Qt.EditRole):
        return True
    
    
    def rowCount(self, index = QtCore.QModelIndex()):
        return len(self._paramList)
    
    
    def columnCount(self, index = QtCore.QModelIndex()):
        return len(self._horizontalHeaderInfo)
    
    
    def addItem(self, parameter):
        result = False
        if parameter:
            insertRow = 0
            sortIndex = parameter.sortIndex()
            if sortIndex:
                while  insertRow < self.rowCount() and sortIndex > self._paramList[insertRow].sortIndex():
                    insertRow += 1
#            self.beginResetModel()
            self.emit(QtCore.SIGNAL('beginInsertRows(QModelIndex, int, int)'), QtCore.QModelIndex(), insertRow, insertRow)
            self._paramList.insert(insertRow, parameter)
            self.emit(QtCore.SIGNAL('endInsertRows()'))
#            self.endResetModel()
            self.reset()
            result = True
            
        return result
    
    
    def addItems(self, parametersList):
        for parameter in parametersList:
            self.addItem(parameter)
    
    
    def addItemByDescription(self, description, value = None):
        parameter = CTemplateParameter.getParameterByDescription(description)
        self.addItem(parameter)
        if value:
            parameter.setValue(value)
            
            
    def addItemsByDescriptions(self, descriptions):
        if isinstance(descriptions, list):
            for description in descriptions:
                if isinstance(description, (tuple, list)):
                    self.addItemByDescription(description[0], value = description[1])
                elif isinstance(description, (basestring, QtCore.QString)):
                    self.addItemByDescription(description)
        elif isinstance(descriptions, dict):
            for item in descriptions.items():
                self.addItemByDescription(item[0], item[1])
    
    
    def removeItemByRow(self, row):
        return self.removeItem(self.index(row, 0, QtCore.QModelIndex()))
    
    
    def removeItem(self, index):
        if not index.isValid():
            return False
        
        row = index.row()
        if self.rowCount() <= row < 0:
            return False
        
        self.emit(QtCore.SIGNAL('beginRemoveRows(QModelIndex, int, int)'), QtCore.QModelIndex(), row, row)
        self._paramList.pop(row)
        self.emit(QtCore.SIGNAL('endRemoveRows()'))
        return True

    
# atronah: not use...
#    
#     def setItemsByDict(self, parametersDict):
#         self.clear()
#         self.addItemsByDescriptions(parametersDict)
#
#     def updateParametersByDict(self, parametersDict):
#         needAddedList = list(parametersDict.keys()) 
#         for row, param in enumerate(self._paramList):
#             description = param.name() 
#             if description not in needAddedList:
#                 self.removeItem(self.index(row, 0, QtCore.QModelIndex()))
#             else:
#                 param.setValue(parametersDict[description])
#                 needAddedList.remove(description)
#         
#         for descriptionOfNew in needAddedList:
#             self.addItemByDescription(descriptionOfNew)
    
    
    def items(self):
        return self._paramList
    
    
    def itemAt(self, index):
        if index.isValid() and (index.row() < self.rowCount()):
            return self._paramList[index.row()]
        return None
    
    
    def itemsAsDict(self):
        resultDict = {}
        for parameter in self._paramList:
            resultDict[parameter.name()] = parameter.toString(parameter.value())
        return resultDict
    
    
    def setItemValues(self, valuesDict):
        for parameter in self._paramList:
            parameterName = parameter.name()
            if valuesDict.has_key(parameterName):
                parameter.setValue(valuesDict[parameterName])
    
    
    def itemName(self, index):
        if not index.isValid():
            return ''
        
        row = index.row()
        if row >= self.rowCount():
            return ''
        
        return self._paramList[row].name()
        
        