# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2014 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore
from library.Utils import readXMLElementText, forceString

'''
Created on 05.03.2014

@author: atronah
'''


## Оператор фильтра для запроса.
# Описывает, каким образом форматируется значение от пользователя (список значений) 
# и отношение между этим значением (список значений) и фильтруемым параметром.
class CQueryFilterOperator(object):
    _xmlTagName = u'operator'
    _xmlCaptionAttr = u'caption'
    _xmlExpression = u'expression'
    _xmlValuesSeparator = u'valuesSeparator'
    _xmlValueListFrameMarks = u'valueListFrameMarks'
    _xmlValueCount = u'valueCount'
    
    ## Создает новый оператор фильтра.
    # @param caption: отображаемое (в списке операторов фильтра) имя.
    # @param expression: выражение (символ), подставляемое(-ый) на место оператора в строку-результат фильтра для запроса
    # @param valuesSeparator: символ/выражение, подставляемое в строку-результат между значениями (если их несколько) в качестве разделителя 
    #                                (например, "," или " AND ")
    # @param valuesSeparatorCaption: отображаемое имя разделителя нескольких значений 
    #                                    (используется в выводе справочной информации по фильтру для пользователя)
    # @param valueListFrameMarks: кортеж из двух символов, ставящихся слева и справа от списка значений (значения) в строке-результате соответственно.
    # @param valuesCount: количество запрашиваемых значений.
    #                        Варианты значений:
    #                            '[0-9]+' - задает точное количество требуемых значений (если 0, то запрос значений будет пропущен),
    #                            '*' - пользователю будет предложено ввести произвольное число значений
    def __init__(self, **kwargs):
        self._caption = kwargs.get('caption', '=')
        self._expression = kwargs.get('expression', '=')
        self._valuesSeparator = kwargs.get('valuesSeparator', u', ')
        self._valuesSeparatorCaption = kwargs.get('valuesSeparatorCaption', u'или')
        self._valueListFrameMarks = kwargs.get('valueListFrameMarks', ('', ''))
        self._valueListFrameMarksCaption = kwargs.get('valueListFrameMarksCaption', ('', ''))
        self.setValueCount(kwargs.get('valueCount', 0))
    
    
    
    @staticmethod
    def loadFromXML(xmlReader):
        if not isinstance(xmlReader, QtCore.QXmlStreamReader):
            return None
        if not (xmlReader.isStartElement() and xmlReader.name() == CQueryFilterOperator._xmlTagName):
            return None
        
        caption = unicode(xmlReader.attributes().value(CQueryFilterOperator._xmlCaptionAttr).toString())
        expression = u''
        valuesSeparator = u','
        valuesSeparatorCaption = u'или'
        valueListFrameMarks = (u'', u'')
        valueListFrameMarksCaption = (u'', u'')
        valueCount = 0
        while xmlReader.readNext() != QtCore.QXmlStreamReader.Invalid:
            if xmlReader.isStartElement():
                if xmlReader.name() == CQueryFilterOperator._xmlExpression:
                    expression = readXMLElementText(xmlReader)
                elif xmlReader.name() == CQueryFilterOperator._xmlValuesSeparator:
                    valuesSeparatorCaption = unicode(xmlReader.attributes().value(CQueryFilterOperator._xmlCaptionAttr).toString())
                    if xmlReader.readNext() != QtCore.QXmlStreamReader.Characters:
                        return None
                    valuesSeparator = unicode(xmlReader.text().toString())
                    if not (xmlReader.readNext() == QtCore.QXmlStreamReader.EndElement
                            and xmlReader.name() == CQueryFilterOperator._xmlValuesSeparator):
                        return None
                elif xmlReader.name() == CQueryFilterOperator._xmlValueListFrameMarks:
                    valueListFrameMarks = (unicode(xmlReader.attributes().value(u'left').toString()),
                                           unicode(xmlReader.attributes().value(u'right').toString()))
                    valueListFrameMarksCaption = (unicode(xmlReader.attributes().value(u'leftCaption').toString()),
                                                  unicode(xmlReader.attributes().value(u'rightCaption').toString()))
                    if not (xmlReader.readNext() == QtCore.QXmlStreamReader.EndElement
                            and xmlReader.name() == CQueryFilterOperator._xmlValueListFrameMarks):
                        return None
                elif xmlReader.name() == CQueryFilterOperator._xmlValueCount:
                    if xmlReader.readNext() != QtCore.QXmlStreamReader.Characters:
                        return None
                    valueCount = unicode(xmlReader.text().toString())
                    if not (xmlReader.readNext() == QtCore.QXmlStreamReader.EndElement
                            and xmlReader.name() == CQueryFilterOperator._xmlValueCount):
                        return None
            elif xmlReader.isEndElement():
                if xmlReader.name() == CQueryFilterOperator._xmlTagName:
                    break
                else:
                    return None
        
        return CQueryFilterOperator(caption = caption,
                                    expression = expression,
                                    valuesSeparator = valuesSeparator,
                                    valuesSeparatorCaption =valuesSeparatorCaption,
                                    valueListFrameMarks = valueListFrameMarks,
                                    valueListFrameMarksCaption = valueListFrameMarksCaption,
                                    valueCount = valueCount)
    
    
    @property
    def expression(self):
        return self._expression
    
    
    @property
    def caption(self):
        return self._caption
    
       
    def valueCount(self):
        return self._valueCount
    
    
    def setValueCount(self, count):
        if isinstance(count, basestring):
            if count == '*':
                self._valueCount = -1
            else:
                self._valueCount = int(count) if count.isdigit() else 0
        elif isinstance(count, int):
            self._valueCount = count
        else:
            self._valueCount = 0
            
            
    def encodeValueToString(self, value, isHumanReadable = False):
        if value.type() == QtCore.QVariant.List:
            valueList = [forceString(valueItem) for valueItem in value.toList()]
        elif isinstance(value, list):
            valueList = value
        else:
            valueList = [forceString(value)]
        
        if not valueList:
            return ''
        
        if len(valueList) < self.valueCount():
            valueList.extend([valueList[0]] * (self.valueCount() - len(valueList)))
        
        if u'' in valueList:
            return u''
        
        valueSep = self._valuesSeparatorCaption if isHumanReadable else self._valuesSeparator
        frameMarks = self._valueListFrameMarksCaption if isHumanReadable else self._valueListFrameMarks
        return frameMarks[0] + valueSep.join(valueList) + frameMarks[-1] 

    
    def decodeValueFromString(self, valueString, isHumanReadable = False):
        result = QtCore.QVariant()
        valueString = unicode(valueString).strip()
        if not valueString:
            return result
        
        frameMarks = self._valueListFrameMarksCaption if isHumanReadable else self._valueListFrameMarks
        if valueString.startswith(frameMarks[0]):
            # Обрезание левого края списка, соответствующего левому обрамляющему выражению
            valueString = valueString[len(frameMarks[0]):] 
        else:
            return result
        
        if valueString.endswith(frameMarks[-1]):
            # Обрезание правого края списка, соответствующего правому обрамляющему выражению
            valueString = valueString[:len(valueString) - len(frameMarks[-1])] 
        else:
            return result
        
        valueSep = self._valuesSeparatorCaption if isHumanReadable else self._valuesSeparator
        result = QtCore.QVariant(valueString.split(valueSep))
        
        return result
        

