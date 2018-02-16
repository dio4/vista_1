# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2014 Vista Software. All rights reserved.
##
#############################################################################


from PyQt4 import QtGui
from Reports.ReportsGenerator.TemplateParameter import CTemplateParameter
from library.QueryFilter.QueryFilterItemModel import CQueryFilterItemModel
from library.QueryFilter.MultipleValuesEditor import CMultipleValuesEditor


'''
Created on 05.03.2014

@author: atronah
'''


class CQueryFilterDelegate(QtGui.QStyledItemDelegate):
    
    def __init__(self, parent = None):
        super(CQueryFilterDelegate, self).__init__(parent)
    
    
    def createEditor(self, parent, option, index):
        editor = None
        if not index.isValid():
            return editor
        
        # Получение модели, для элемента которой формируется редактор
        model = index.model()
        
        if not isinstance(model, CQueryFilterItemModel):
            return editor
        
        column = index.column()
        if column == CQueryFilterItemModel.ciOperator:
            # Получение информации о текущем фильтре, чье значение редактируется
            filterItem = model.filterItem(index)
            # Создание экземпляра класса редактора в виде выпадающего списка, основанного на моделе операторов текущего фильтра
            editor = QtGui.QComboBox(parent)
            editor.addItems([operator.caption for operator in filterItem.operatorList()])
        elif column == CQueryFilterItemModel.ciValue:
            # Получение информации о текущем фильтре, чье значение редактируется
            filterItem = model.filterItem(index)
            # Получение имени типа фильтра для выбора нужного редактора
            typeName = filterItem.valueTypeName()
            # Получение количества значений, которые будут запрошены у пользователя для этого фильтра
            valueCount = filterItem.currentOperator.valueCount()
            # Для случая простого фильтра по одному значению
            if valueCount == 1 and CTemplateParameter.editWidgetInfoForTypes.has_key(typeName):
                # Создание экземпляра класса редактора в соответствии с типом фильтра
                editorClass = CTemplateParameter.editWidgetInfoForTypes[typeName]['widgetClass']
                editor = editorClass(parent)
                # Опции настройки редактора #TODO: atronah: необходимо реализовать
                editorOptions = None #Опции конфигурирования редактора
                # Конфигрурирование редактора перед передачей отображению
                configureFunction = CTemplateParameter.editWidgetInfoForTypes[typeName]['configure']
                if callable(configureFunction):
                    configureFunction(editor, editorOptions)
            # Использование редактора для мультизначного фильтра
            else:
                editor = CMultipleValuesEditor(typeName = typeName,
                                               valueEncoder = filterItem.currentOperator.encodeValueToString,
                                               valueDecoder = filterItem.currentOperator.decodeValueFromString,
                                               valueCount = valueCount,
                                               parent = parent)
        return editor
    
    
    def setEditorData(self, editor, index):
        if not index.isValid():
            return
        
        # Получение модели, для элемента которой формируется редактор
        model = index.model()
        
        if not isinstance(model, CQueryFilterItemModel):
            return
        
        column = index.column()
        if column == CQueryFilterItemModel.ciOperator:    
            editor.setCurrentIndex(model.filterItem(index).currentOperatorIndex)
        elif column == CQueryFilterItemModel.ciValue:
            # Получение информации о текущем фильтре, чье значение редактируется
            filterItem = model.filterItem(index)
            # Получение имени типа фильтра для выбора нужного редактора
            typeName = filterItem.valueTypeName()
            # Получение количества значений, которые будут запрошены у пользователя для этого фильтра
            valueCount = filterItem.currentOperator.valueCount()
            # Для случая простого фильтра по одному значению
            if valueCount == 1 and CTemplateParameter.editWidgetInfoForTypes.has_key(typeName):
                # Получение функции установки значения для редактора
                setter = CTemplateParameter.editWidgetInfoForTypes[typeName]['setter']
                #TODO: atronah: доработать для поддержки нескольких значений
                value = filterItem.value.toPyObject()
                if value is not None:
                    setter(editor, value)
            elif isinstance(editor, CMultipleValuesEditor):
                editor.setValue(filterItem.value)
                
        
    
    
    def setModelData(self, editor, model, index):
        if not index.isValid():
            return
        
        # Получение модели, для элемента которой формируется редактор
        model = index.model()
        
        if not isinstance(model, CQueryFilterItemModel):
            return
        
        column = index.column()
        if column == CQueryFilterItemModel.ciOperator:
            model.setData(index, editor.currentIndex())
        elif column == CQueryFilterItemModel.ciValue:
            # Получение информации о текущем фильтре, чье значение редактируется
            filterItem = model.filterItem(index)
            # Получение имени типа фильтра для выбора нужного редактора
            typeName = filterItem.valueTypeName()
            # Получение количества значений, которые будут запрошены у пользователя для этого фильтра
            valueCount = filterItem.currentOperator.valueCount()
            if valueCount == 1 and CTemplateParameter.editWidgetInfoForTypes.has_key(typeName):
                # Получение функции получения значения из редактора
                getter = CTemplateParameter.editWidgetInfoForTypes[typeName]['getter']
                #TODO: atronah: доработать для поддержки нескольких значений
                value = getter(editor)
                model.setData(index, value)
            elif isinstance(editor, CMultipleValuesEditor):
                model.setData(index, editor.value())
                
    
    