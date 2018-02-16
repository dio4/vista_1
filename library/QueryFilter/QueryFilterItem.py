# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2014 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore
#from library.QueryFilter.QueryFilterOperatorModel import CQueryFilterOperatorModel #deprecated
from library.Utils import readXMLElementText, forceRef, forceString
from library.QueryFilter.QueryFilterOperator import CQueryFilterOperator
from library.crbcombobox import CRBModelDataCache, CRBComboBox

'''
Created on 05.03.2014

@author: atronah
'''


## Описание фильтра для запроса к базе данных
class CQueryFilterItem(QtCore.QObject):
    _xmlTagName = u'filterItem'
    _xmlCaptionAttr = u'caption'
    _xmlValueTypeTagName = u'valueTypeInfo'
    _xmlValueTypeNameAttr = u'name'
    _xmlValueLeftFrameMarkTagName = u'leftFrameMark'
    _xmlValueRightFrameMarkTagName = u'rightFrameMark'
    _xmlExpressionTagName = u'expression'
    _xmlExpressionOperatorTagName = u'op'
    _xmlExpressionValuesTagName = u'val'
    _xmlOperatorListTagName = u'operatorList'
    
    
    
    RefBook = QtCore.QVariant.UserType + 1
    
    typeNameToVariantType = {'str' : QtCore.QVariant.String,
                             'string' : QtCore.QVariant.String,

                             'int' : QtCore.QVariant.Int,
                                 
                             'double' : QtCore.QVariant.Double,
                             'float' : QtCore.QVariant.Double,
                                 
                             'date' : QtCore.QVariant.Date,
                                 
                             'datetime' : QtCore.QVariant.DateTime,
                                 
                             'time' : QtCore.QVariant.Time,
                                 
                             'rb' : RefBook}
    
    
    def __init__(self, parent = None, **kwargs):
        super(CQueryFilterItem, self).__init__(parent)
        
        self._caption = kwargs.get('caption', u'<Произвольный фильтр>')
        self._expression = kwargs.get('expression', '') or u'1'
        
        valueTypeInfo = kwargs.get('valueTypeInfo', {})
        self._valueTypeInfo = {'name': valueTypeInfo.get('name', 'str'),
                               'leftFrameMark': valueTypeInfo.get('leftFrameMark', "'"),
                               'rightFrameMark': valueTypeInfo.get('rightFrameMark', "'")}

        self._operatorList = []
        for operator in kwargs.get('operatorList', []):
            self.appendOperator(operator)
            
        self._operatorIdx = -1 if not self._operatorList else 0
        self._value = QtCore.QVariant()
        
            
            
    @property
    def caption(self):
        return self._caption
    
    
    @property
    def expression(self):
        return self._expression
        
    
    @property
    def currentOperator(self):
        return self._operatorList[self._operatorIdx] if self._operatorIdx in xrange(len(self._operatorList)) else None
    
    
    @property
    def currentOperatorIndex(self):
        return self._operatorIdx
    
    
    def operatorList(self):
        return self._operatorList
    
    
    def setCurrentOperatorIndex(self, idx):
        if isinstance(idx, QtCore.QVariant):
            idx = idx.toInt()[0] if idx.canConvert(QtCore.QVariant.Int) else None
        if idx not in xrange(len(self._operatorList)):
            return False
        self._operatorIdx = idx
        return True
        
    
    @property
    def value(self):
        return self._value
    
    
    @value.setter
    def value(self, newValue):
        self.setValue(newValue)
    
    
    def setValue(self, value):
        self._value = QtCore.QVariant(value)
        return True
    
    
    def valueTypeName(self):
        return self._valueTypeInfo.get('name', u'str')
    
    
    def valueType(self):
        return self.valueTypeByName(self.valueTypeName())
        
        
    @classmethod
    def valueTypeByName(cls, typeName):
        cls.typeNameToVariantType.get(typeName, QtCore.QVariant.String)
    
    
    ## Загрузка из XML
    @staticmethod
    def loadFromXML(xmlReader):
        if not isinstance(xmlReader, QtCore.QXmlStreamReader):
            return None
        if not (xmlReader.isStartElement() and xmlReader.name() == CQueryFilterItem._xmlTagName):
            return None
        
        caption = unicode(xmlReader.attributes().value(CQueryFilterItem._xmlCaptionAttr).toString()) or u'<Произвольный фильтр>'
        expression = u''
        valueTypeInfo = {}
        operatorList = []
        while xmlReader.readNext() != QtCore.QXmlStreamReader.Invalid:
            if xmlReader.isStartElement():
                # Загрузка информации о типе значения
                if xmlReader.name() == CQueryFilterItem._xmlValueTypeTagName:
                    valueTypeInfo['name'] = unicode(xmlReader.attributes().value(CQueryFilterItem._xmlValueTypeNameAttr).toString()) or u'str'
                    # Загрузка доп. данных о типе значения
                    while xmlReader.readNext() != QtCore.QXmlStreamReader.Invalid:
                        if xmlReader.isStartElement():
                            if xmlReader.name() == CQueryFilterItem._xmlValueLeftFrameMarkTagName:
                                valueTypeInfo['leftFrameMark'] = unicode(readXMLElementText(xmlReader))
                            elif xmlReader.name() == CQueryFilterItem._xmlValueRightFrameMarkTagName:
                                valueTypeInfo['rightFrameMark'] = unicode(readXMLElementText(xmlReader))
                        elif xmlReader.isEndElement():
                            if xmlReader.name() == CQueryFilterItem._xmlValueTypeTagName:
                                break
                            else:
                                return None
                # Загрузка выражения фильтра
                elif xmlReader.name() == CQueryFilterItem._xmlExpressionTagName:
                    while xmlReader.readNext() != QtCore.QXmlStreamReader.Invalid:
                        if xmlReader.isCharacters():
                            expression += unicode(xmlReader.text().toString())
                        elif xmlReader.isStartElement():
                            elementName = xmlReader.name()
                            if elementName == CQueryFilterItem._xmlExpressionOperatorTagName:
                                expression += u'%(operator)s'
                            elif elementName == CQueryFilterItem._xmlExpressionValuesTagName:
                                expression += u'%(value)s'
                            if not (xmlReader.readNext() == QtCore.QXmlStreamReader.EndElement
                                    or xmlReader.name() == elementName):
                                return None
                        elif xmlReader.isEndElement():
                            if xmlReader.name() == CQueryFilterItem._xmlExpressionTagName:
                                break
                            else:
                                return None
                # Загрузка операторов фильтра
                elif xmlReader.name() == CQueryFilterItem._xmlOperatorListTagName:
                    while xmlReader.readNext() != QtCore.QXmlStreamReader.Invalid:
                        if xmlReader.isStartElement():
                            if xmlReader.name() == CQueryFilterOperator._xmlTagName:
                                operator = CQueryFilterOperator.loadFromXML(xmlReader)
                                if operator:
                                    operatorList.append(operator)
                        elif xmlReader.isEndElement():
                            if xmlReader.name() == CQueryFilterItem._xmlOperatorListTagName:
                                break
                            else:
                                return None
            elif xmlReader.isEndElement():
                if xmlReader.name() == CQueryFilterItem._xmlTagName:
                    break
                else:
                    return None
        
        return CQueryFilterItem(caption = caption,
                                expression = expression,
                                valueTypeInfo = valueTypeInfo,
                                operatorList = operatorList)

    
    def appendOperator(self, operator):
        self._operatorList.append(operator)
    
    
    ## Формирует условие для подстановки в запрос или для отображения пользователю
    def compileCondition(self, isHumanReadable = False):
        if self._operatorIdx not in xrange(len(self._operatorList)):
            return (u'%s: на задано' % self._caption) if isHumanReadable else '1' 
        
        filterOperator = self._operatorList[self._operatorIdx]
        template = (self.caption + u' %(operator)s %(value)s') if isHumanReadable else self.expression 
        operator = filterOperator.caption if isHumanReadable else filterOperator.expression
        encodedValue = self.encodeValue(self._value, self._valueTypeInfo, isHumanReadable)
        stringValue = filterOperator.encodeValueToString(encodedValue, isHumanReadable)
        return template % {'operator' : operator,
                           'value' : stringValue}

    

    ## Кодирует значение фильтра в значение(список значений) с учетом настроек фильтра.
    # Т.е. добавляет обрамляющие символы, заменяет на читаемый вариант при включенной опции isHumanReadable.
    @classmethod
    def encodeValue(cls, value, valueTypeInfo, isHumanReadable = False):
        isList = value.type() == QtCore.QVariant.List 
        valueList = value.toList() if isList else [value] 
        resultList = []
        for value in valueList:
            if value.type() in (QtCore.QVariant.Date, QtCore.QVariant.DateTime):
                value = value.toString(QtCore.Qt.ISODate)
            else:
                value = value.toString()
            typeName = valueTypeInfo.get('name', 'str')
            if isHumanReadable and cls.valueTypeByName(typeName) == cls.RefBook and valueTypeInfo.has_key('tableName'):
                tableName = valueTypeInfo['tableName']
                cond = [valueTypeInfo.get('condition', u''),
                        'id = %s' % forceRef(value)]
                cache = CRBModelDataCache.getData(tableName, filter = cond)
                value = cache.getStringById(forceRef(value), CRBComboBox.showName)
            resultList.append(value
                              .prepend(valueTypeInfo['leftFrameMark'])
                              .append(valueTypeInfo['rightFrameMark']))

        return QtCore.QVariant(resultList if isList else resultList[0])
    
    
    ## Декодирует значение фильтра из закодированого варианта (с обрамляющими символами и т.п.) в хранимый вариант.
    # Т.е. удаляет обрамляющие символы, ищет соответствующее значение для читаемого варианта при включенной опции isHumanReadable.
    @classmethod
    def decodeValue(cls, value, valueTypeInfo, isHumanReadable = False):
        isList = value.type() == QtCore.QVariant.List 
        valueList = value.toList() if isList else [value] 
        resultList = []
        for value in valueList:
            typeName = valueTypeInfo.get('name', 'str')
            valueType = cls.valueTypeByName(typeName)
            
            value = value.toString()
            if value.startsWith(valueTypeInfo['leftFrameMark']):
                value.remove(0, len(valueTypeInfo['leftFrameMark']))
            if value.startsWith(valueTypeInfo['rightFrameMark']):
                value.chop(len(valueTypeInfo['leftFrameMark']))
            
            if valueType == QtCore.QVariant.Date:
                value = QtCore.QDate.fromString(value, QtCore.Qt.ISODate)
            elif QtCore.QVariant.DateTime:
                value = QtCore.QDateTime.fromString(value, QtCore.Qt.ISODate)
            elif value.canConvert(valueType):
                value = value.convert(valueType)
            elif isHumanReadable and valueType == cls.RefBook and valueTypeInfo.has_key('tableName'):
                tableName = valueTypeInfo['tableName']
                cond = [valueTypeInfo.get('condition', u''),
                        "name like '%%%s%%'" % forceString(value)]
                cache = CRBModelDataCache.getData(tableName, filter = cond)
                valueIndex = cache.getIndexByName(forceString(value), isStrinct = False)
                value = cache.getId(valueIndex)
            resultList.append(value
                              .prepend()
                              .append(valueTypeInfo['rightFrameMark']))

        return QtCore.QVariant(resultList if isList else resultList[0])
    

        
       
    