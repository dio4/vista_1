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

import re

from PyQt4 import QtCore, QtGui

from library.Utils import forceString


class CParameterDelegate(QtGui.QItemDelegate):
    def __init__(self, parent = None):
        QtGui.QItemDelegate.__init__(self, parent)
        
    
    def createEditor(self, parent, option, index):
        parameter = index.model().itemAt(index)
        editWidgetClass = parameter.editWidgetClass() 
        return editWidgetClass(parent)
    
    def setEditorData(self, editor, index):
        parameter = index.model().itemAt(index) if index.isValid() else None
        if parameter:
            parameter.connectToWidget(editor)
        return 
    
    def setModelData(self, editor, model, index):
        parameter = model.itemAt(index)
        if parameter:
            parameter.disconnectFromWidget()
        return
    
    

class CTemplateParameter(object):
    """
    Описание объекта, позволяющего оперировать параметрами шаблонов (выводить их в интерфейс, получать их значение)
    """
    
    _parameterDescriptionPattern = ur'(?P<caption>[\wа-яА-Я]+)(?:#(?P<sortIndex>\d{1,3}))?(?:@(?P<type>\w{1,16}))?'
    
    editWidgetInfoForTypes = {'date' : {'widgetClass' : QtGui.QDateEdit,
                                         'setter' : QtGui.QDateEdit.setDate,
                                         'getter' : QtGui.QDateEdit.date,
                                         'toString' : lambda value : forceString(value.toString(QtCore.Qt.ISODate)) if value else '',
                                         'fromString' : lambda value : QtCore.QDate.fromString(value, QtCore.Qt.ISODate) if value else QtCore.QDate(),
                                         'configure' : lambda obj, options = None : (QtGui.QDateEdit.setCalendarPopup(obj, options['isCalendarPopup'] if options else True), 
                                                                                    QtGui.QDateEdit.setDate(obj, options['date'] if options else QtCore.QDate.currentDate()),
                                                                                    QtGui.QDateEdit.setDisplayFormat(obj, 'yyyy-MM-dd')
                                                                                    )
                                        },
                              'datetime' : {'widgetClass' : QtGui.QDateTimeEdit,
                                            'setter' : QtGui.QDateTimeEdit.setDateTime,
                                            'getter' : QtGui.QDateTimeEdit.dateTime,
                                            'toString' : lambda value : forceString(value.toString(QtCore.Qt.ISODate)) if value else '',
                                            'fromString' : lambda value : QtCore.QDateTime.fromString(value, QtCore.Qt.ISODate) if value else QtCore.QDateTime(),
                                            'configure' : lambda obj, options = None : (QtGui.QDateTimeEdit.setCalendarPopup(obj, options['isCalendarPopup'] if options else True), 
                                                                                        QtGui.QDateTimeEdit.setDateTime(obj, options['datetime'] if options else QtCore.QDateTime.currentDateTime()),
                                                                                        QtGui.QDateTimeEdit.setDisplayFormat(obj, 'yyyy-MM-dd HH:mm:ss')
                                                                                        )
                                            },
                              'int' : {'widgetClass' : QtGui.QSpinBox,
                                            'setter' : QtGui.QSpinBox.setValue,
                                            'getter' : QtGui.QSpinBox.value,
                                            'toString' : lambda value : forceString(value),
                                            'fromString' : lambda value : int(value) if value and value.isdigit() else 0,
                                            'configure' :  lambda obj, options = None: (QtGui.QSpinBox.setMaximum(obj, options['maximum'] if options else 999),
                                                                                       QtGui.QSpinBox.setMinimum(obj, options['minimum'] if options else 0),
                                                                                       QtGui.QSpinBox.setSingleStep(obj, options['step'] if options else 1))
                                            },
                              'str' : {'widgetClass' : QtGui.QLineEdit,
                                            'setter' : QtGui.QLineEdit.setText,
                                            'getter' : QtGui.QLineEdit.text,
                                            'toString' : lambda value : value if value is not None else '',
                                            'fromString' : lambda value : value if value is not None else '',
                                            'configure' : None
                                            },
                              'float' : {'widgetClass' : QtGui.QDoubleSpinBox,
                                            'setter' : QtGui.QDoubleSpinBox.setValue,
                                            'getter' : QtGui.QDoubleSpinBox.value,
                                            'toString' : lambda value : forceString(value),
                                            'fromString' : lambda value : float(value) if value else 0.0,
                                            'configure' : lambda obj, options = None: (QtGui.QDoubleSpinBox.setMaximum(obj, options['maximum'] if options else 99.9),
                                                                                       QtGui.QDoubleSpinBox.setMinimum(obj, options['minimum'] if options else 0.0),
                                                                                       QtGui.QDoubleSpinBox.setSingleStep(obj, options['step'] if options else 0.1))
                                            },
                              'bool' : {'widgetClass' : QtGui.QComboBox,
                                            'setter' : QtGui.QComboBox.setCurrentIndex,
                                            'getter' : QtGui.QComboBox.currentIndex,
                                            'toString' : lambda value : u'1' if value == 1 else (u'0' if value == 2 else 'NULL'),
                                            'fromString' : lambda value : 1 if value == '1' else (2 if value == '0' else 0),
                                            'configure' : lambda obj, options = None: (QtGui.QComboBox.addItems([u'Не задано', u'Да', 'Нет']),
                                                                                       QtGui.QComboBox.setCurrentIndex(obj, 0))
                                            }
                              }
    
    
    @classmethod
    def addWidgetInfoForType(cls, typeName, widgetInfo=None):
        if not widgetInfo:
            widgetInfo = {}
        if widgetInfo:
            cls.editWidgetInfoForTypes[typeName] = widgetInfo
    
    
    @staticmethod
    def parseParametersFromText(sourceText, withReplays = False):
        parameterDescriptionsList = [] 
        parameterPattern = ur'\{' + CTemplateParameter._parameterDescriptionPattern + ur'\}'
        
        match = re.search(parameterPattern, sourceText)
        while match:
            description = match.group()
            parameterDescriptionsList.append(description)
            if withReplays:
                noProcessedText = match.string[:match.start()] + match.string[match.end():]
            else:
                noProcessedText = match.string.replace(description, '')
            match = re.search(parameterPattern, noProcessedText)
                
        
        return parameterDescriptionsList
        
    
    
    @staticmethod
    def transcriptParameters(sourceText, valuesMap=None):
        if not valuesMap:
            valuesMap = {}
        parametersNameList = CTemplateParameter.parseParametersFromText(sourceText)
        outText = sourceText
        for name in parametersNameList:
            if valuesMap.has_key(name):
                outText = outText.replace(name, forceString(valuesMap.get(name, '')))
        
        return outText
            
    
    @classmethod
    def getParameterByDescription(cls, paramDescription):
        paramInfoSearch = re.compile(cls._parameterDescriptionPattern).search(paramDescription)
        paramInfo = paramInfoSearch.groupdict() if paramInfoSearch else {'caption': u'Ошибка описания параметра',
                                                                         'type' : 'str', 
                                                                         'sortIndex' : None}
        
        name = paramDescription
        caption = paramInfo.get('caption', name)
        typeName = paramInfo.get('type', 'str') 
        if not cls.editWidgetInfoForTypes.has_key(typeName):
            typeName = 'str'
        sortIndex = paramInfo.get('sortIndex', None)
        
        return cls(name = name,
                   typeName = typeName,
                   caption = caption,
                   sortIndex = sortIndex)
        
    
    
    def __init__(self, 
                 name,
                 typeName,
                 caption = u'',
                 sortIndex = None):
        
        self._name = name
        self._caption = caption
        self._typeName = typeName
        self._sortIndex = sortIndex
        self._bindedWidget = None
        self._value = None

    
    def name(self):
        return self._name
           
    
    def typeName(self):
        return self._typeName
    
    
    def sortIndex(self):
        return self._sortIndex
            
    
    def editWidgetClass(self):
        return self.editWidgetInfoForTypes[self.typeName()]['widgetClass']
        
    
    def caption(self):
        return self._caption.replace('_', ' ')
    
    
    def connectToWidget(self, widget, options = None):
        if isinstance(widget, self.editWidgetInfoForTypes[self.typeName()]['widgetClass']):
            self._bindedWidget = widget
            configure = self.editWidgetInfoForTypes[self.typeName()]['configure']
            if callable(configure):
                configure(widget, options)
            self.setValue(self._value)
            return True
        return False
    
    
    def disconnectFromWidget(self):
        if self._bindedWidget:
            self._value = self.value()
            self._bindedWidget = None 
    
    
    def bindedWidget(self):
        return self._bindedWidget
    
    
    def setValue(self, value):
#        if value is None:
#            value = ''
        if isinstance(value, QtCore.QString):
            value = forceString(value)
        
        if isinstance(value, basestring):
            fromString = self.editWidgetInfoForTypes[self.typeName()]['fromString']
            value = fromString(value)
        
        if value is not None and self._bindedWidget:
            setter = self.editWidgetInfoForTypes[self.typeName()]['setter']
            setter(self._bindedWidget, value)
        else:
            self._value = value
    
    
    def value(self):
        if self._bindedWidget:
            getter = self.editWidgetInfoForTypes[self.typeName()]['getter']
            value = getter(self._bindedWidget)
        else:
            value = self._value
        return value
    
    
    def stringValue(self):
        return self.toString(self.value())
        
    
    def toString(self, value):
        toString = self.editWidgetInfoForTypes[self.typeName()]['toString']
        return toString(value) if value is not None else u''