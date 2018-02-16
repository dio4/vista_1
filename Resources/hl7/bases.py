#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import xml.dom
import xml.dom.minidom


class THl7List:
    def __init__(self, elementType, defaultValue):
        self._elementType = elementType
        self._defaultValue = defaultValue
        self._values = []


    def append(self, value=None):
        self._values.append( copy.deepcopy(self._defaultValue) if value is None else value )

        
    def removeAll(self):
        self._values = []


    def __len__(self):
        return len(self._values)


    def __getitem__(self, key):
        return self._values[key]

    def __setitem__(self, key, value):
        self._values[key] = value


    def __delitem__(self, key):
        del self._values[key]


    def __iter__(self):
        return self._values.__iter__()



class THl7Compound:
    def __init__(self):
        self.initClass()
        self.initAttrs()

    @classmethod
    def initClass(cls):
        if not hasattr(cls, '_mapNameToItem'):
            cls._mapNameToItem = dict( (item[0], item) for item in cls._items )
        if not hasattr(cls, '_mapNodeNameToItem'):
            cls._mapNodeNameToItem = dict( (item[1], item) for item in cls._items )

    def initAttrs(self):
        for item in self._items:
            if len(item) == 4:
                name, elementName, itemType, defaultValue = item
                if type(itemType) in [list, tuple]:
                    defaultValue = THl7List(itemType[0], defaultValue)
                    defaultValue.append()
                self.__setattr__(name, defaultValue)


    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        item = self.__class__._mapNameToItem.get(name,None)
        if item is None:
            raise AttributeError, name
        if len(item) == 4:
            name, elementName, itemType, defaultValue = item
            if type(itemType) in [list, tuple]:
                defaultValue = THl7List(itemType[0], defaultValue)
        else:
            name, elementName, itemType = item
            if type(itemType) in [list, tuple]:
                defaultValue = THl7List(itemType[0], itemType[0]())
            else:
                defaultValue = itemType()
        self.__dict__[name] = defaultValue
        return defaultValue


    def __setattr__(self, name, value):
        self.__dict__[name] = value


    def _toDom(self, document, nodeName):
        result = document.createElement(nodeName)

        for item in self._items:
            itemName = item[0]
            nodeName = item[1]
            itemType = item[2]
            if itemName in self.__dict__:
                value = self.__dict__[itemName]
                if type(itemType) in [list, tuple]:
                    for element in value:
                        result.appendChild( self._valueToDom(element, nodeName, document))
                else:
                    result.appendChild( self._valueToDom(value, nodeName, document))
        return result


    def _valueToDom(self, value, nodeName, document):
        if isinstance(value, THl7Compound):
            result = value._toDom(document, nodeName)
        else:
            result = document.createElement(nodeName)
            result.appendChild( document.createTextNode(unicode(value)) )
        return result


    def _fromDom(self, element, skipUnknown=False):
        initalizedLists = set()
        notableTextNode = None
        for fox in element.childNodes:
            if fox.nodeType == xml.dom.Node.ELEMENT_NODE:
                name = fox.localName
                item = self._mapNodeNameToItem.get(name, None)
                if item:
                    itemName = item[0]
                    itemType = item[2]
                    if type(itemType) in [list, tuple]:
                        itemValue = self.__getattr__(itemName)
                        if name not in initalizedLists:
                            itemValue.removeAll()
                            initalizedLists.add(name)
                        value = self._valueFromDom(fox, itemType[0], skipUnknown)
                        itemValue.append(value)
                    else:
                        value = self._valueFromDom(fox, itemType, skipUnknown)
                        self.__setattr__(itemName, value)
                elif not skipUnknown:
                    raise Exception('Unknown element "%s"' %name)
                notableTextNode = False
            elif fox.nodeType == xml.dom.Node.TEXT_NODE and notableTextNode is None:
                notableTextNode = fox
        if notableTextNode:
            # fallback to first item; 
            item = self._items[0]
            itemName = item[0]
            itemType = item[2]
            if type(itemType) in [list, tuple]:
                itemValue = self.__getattr__(itemName)
                itemValue.removeAll()
                value = self._valueFromDom(element, itemType[0], skipUnknown)
                itemValue.append(value)
            else:
                value = self._valueFromDom(element, itemType, skipUnknown)
                self.__setattr__(itemName, value)
                

    def _valueFromDom(self, element, itemType, skipUnknown=False):
        if issubclass(itemType, THl7Compound):
            result = itemType()
            result._fromDom(element, skipUnknown)
        else:
            result = ''.join([fox.data for fox in element.childNodes if fox.nodeType == xml.dom.Node.TEXT_NODE])
        return result


class THl7Message(THl7Compound):
    _mapMessageNameToClass = {}

    @classmethod
    def register(cls):
        THl7Message._mapMessageNameToClass[cls._name] = cls

    def __init__(self):
        THl7Compound.__init__(self)
        assert self._name

    def toDom(self):
        di = xml.dom.minidom.getDOMImplementation()
        document = di.createDocument(None, None, None)
        result = THl7Compound._toDom(self, document, self._name)
        document.appendChild(result)
        result.setAttribute('xmlns', 'urn:hl7-org:v2xml')
        result.setAttribute('xmlns:xsi', 'http://www3/org/2001/XMLSchema-instance')
        result.setAttribute('xsi:schemaLocation', 'urn:hl7-org:v2xml %s.xsd' %self._name)
        return result

    @staticmethod
    def fromDom(element):
        cls = THl7Message._mapMessageNameToClass.get(element.localName, None)
        if cls:
            result = cls()
            result._fromDom(element)
            return result
        else:
            raise Exception('Unknown message "%s"' %element.localName)

