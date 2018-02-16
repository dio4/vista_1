#! /usr/bin/env python
# -*- coding: utf-8 -*-


#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
##
## Базовый класс записи протокола ASTM E-1394
##
#############################################################################



from PyQt4.QtCore import *


class EWrongRecordType(Exception):
    def __init__(self, classRecordType, stringRecordType):
        Exception.__init__(self, 'The record type from a string "%s" does not match with an expected record type "%s"' % (stringRecordType, classRecordType))


class CRecord(object):
# Базовый класс для представления записей ASTM.
#
# Принято решение в производных классах описывать структуру полей,
# a все данные хранить в некотором представлении напоминающем
# представление в MUMPS: списки списков и простых значений, для
# хранения отдельных значений используется строковое представление
# (возможно None для пустых значений). Это решение мотивировано
# желанием упростить добавление или изменение типов записей и их
# атрибутов. Существует альтернативное, и возможно, более
# производительное решение: каждый тип записи имеет своё описание
# как python class и в силу этого свою реализацию
# сериализации/десеарилизации. Меня "укачивает" при обсуждении
# подобной возможности. hl7 имеет подобную структуру записей, и
# поэтому есть надежда что что достижения в этой части ещё
# пригодятся.
#
#    Структура описывается следующим образом:
#    structure = { # имя            индекс   python -тип значения
#                   'fieldName' : ( (1,),    unicode),
#                   'd1'        : ( (2,),    int),
#                   'lastName'  : ( (3,0,0), unicode),
#                   'firstName' : ( (3,0,1), unicode),
#                   'patrName'  : ( (3,0,2), unicode),
#                }

    def __init__(self):
        # _storage: это список списков
        object.__setattr__(self, '_storage', [])
        if hasattr(type(self), 'recordType'):
            self.__setattr__('recordType', type(self).recordType)


    @classmethod
    def getIndex(cls, attr):
        # получить индекс атрибута в self._storage
        # в силу принятого решения индекс оказывается вектором
        index = cls.structure[attr][0]
        return index if isinstance(index, (list, tuple)) else [index]


    @classmethod
    def getType(cls, attr):
        # получить python тип значения
        return cls.structure[attr][1]


    @classmethod
    def convertScalarAttrValueToString(cls, type_, value):
        if value is None:
            return value
        if type_ in (str, unicode):
            return value if isinstance(value, basestring) else unicode(value)
        elif type_ in (int, long, float):
            return str(value)
        elif type_ is QDate:
            return str(value.toString('yyyyMMdd'))
        elif type_ is QDateTime:
            return str(value.toString('yyyyMMddhhmmss'))
        elif type_ is QTime:
            return str(value.toString('hhmmss'))
        else:
            assert False, '"%s"unknown type of attribute' % repr(type_)


    @classmethod
    def convertAttrValueToString(cls, type_, value):
        if isinstance(value, (list, tuple)):
            return [cls.convertAttrValueToString(type_, x) for x in value]
        else:
            return cls.convertScalarAttrValueToString(type_, value)


    @classmethod
    def convertScalarStringToAttrValue(cls, type_, value):
        if type_ in (str, unicode) or value is None:
            return value
        elif type_ in (int, long, float):
            return type_(value) if value else None
        elif type_ is QDate:
            return QDate.fromString(value, 'yyyyMMdd')
        elif type_ is QDateTime:
            return QDateTime.fromString(value, 'yyyyMMddhhmmss')
        elif type_ is QTime:
            return QTime.fromString(value, 'hhmmss')
        else:
            assert False, '"%s"unknown type of attribute' % repr(type_)


    @classmethod
    def convertStringToAttrValue(cls, type_, stringOrList):
        if isinstance(stringOrList, (list, tuple)):
            return [cls.convertStringToAttrValue(type_, x) for x in stringOrList]
        else:
            return cls.convertScalarStringToAttrValue(type_, stringOrList)


    def __setattr__(self, name, value):
        index = self.getIndex(name)
        strValue = self.convertAttrValueToString(self.getType(name), value)
        setData(self._storage, index, strValue)


    def __getattr__(self, name):
        index = self.getIndex(name)
        strValue = flatValue(getData(self._storage, index))
        return self.convertStringToAttrValue(self.getType(name), strValue)


    def asString(self, delimiters, encoding='utf8'):
        escape = lambda string: AstmEscape(string.encode(encoding), delimiters)
        return convertStorageToString(self._storage, delimiters[:-1], escape)


    def setString(self, string, delimiters, encoding='utf8'):
        if hasattr(type(self), 'recordType') and type(self).recordType != string[:1]:
            raise EWrongRecordType(type(self).recordType, string[:1])
        unescape = lambda string: AstmUnescape(string, delimiters).decode(encoding)
        object.__setattr__(self,
                           '_storage',
                           convertStringToStorage(string, delimiters[:-1], unescape)
                          )


# "механика" ##############################################################################
# есть стремление сделать эти методы статическими в классе, но
# необходимсть явно указывать имя класса в рекурсии удручает.

def setData(storage, index, value):
    # поместить в хранилище по заданонму индексу указанное значение
    index, subIndex = index[0], index[1:]
    if len(storage)<=index:
        storage.extend(['']*(index-len(storage)+1))
    if not subIndex:
        storage[index] = value
    else:
        subStorage = storage[index]
        if not isinstance(subStorage, list):
            subStorage = list(subStorage) if isinstance(subStorage, tuple) else [subStorage]
            storage[index] = subStorage
        setData(subStorage, subIndex, value)


def getData(storage, index):
    # получить значение из хранилища по заданному индексу
    index, subIndex = index[0], index[1:]
    if len(storage)<=index:
        return None
    if not subIndex:
        return storage[index]
    else:
        subStorage = storage[index]
        if not isinstance(subStorage, (list, tuple)):
            subStorage = [subStorage]
        return getData(subStorage, subIndex)


def flatValue(value):
    # в принятом методе хранения данных нет принципиальной разницы между
    # 'val', ['val'] или [['val']]
    # это связано с тем, что когда мы видим в записи |val|
    # мы не можем сказать - val это просто значение атрибута,
    # первый и единственный элемент сложного атрибута
    # или первый и единственный экземпляр повторяемого значения
    # первого и единственного элемента сложного атрибута.
    flatten = value
    while isinstance(flatten, (list, tuple)):
        if len(flatten) == 1:
            flatten = flatten[0]
        else:
            return value
    return flatten


def convertStorageToString(storage, delimiters, escape):
    delimiter, subDelimiters = delimiters[:1], delimiters[1:]
    return delimiter.join( '' if part is None else
                           escape(part) if isinstance(part, basestring) else
                           convertStorageToString(part, subDelimiters, escape)
                           for part in storage
                         )


def convertStringToStorage(string, delimiters, unescape):
    delimiter, subDelimiters = delimiters[:1], delimiters[1:]
    result = string.split(delimiter)
    if subDelimiters:
        for i, part in enumerate(result):
            result[i] = flatValue(convertStringToStorage(part, subDelimiters, unescape))
    else:
        for i, part in enumerate(result):
            result[i] = unescape(part)
    return result


def AstmEscape(string, delimiters):
    # delimiters это строка типа '|\\^&'
#    assert len(delimiters) == 4

    escape = delimiters[-1]
    result = string.replace(escape, escape + 'E' + escape)
    for i, name, in enumerate('FSR'):
        result = result.replace(delimiters[i], escape + name + escape )
    return result


def AstmUnescape(string, delimiters):
    # delimiters это строка типа '|\\^&'
#    assert len(delimiters) == 4
    escape = delimiters[-1]
    result = string
    for i, name, in enumerate('FSR'):
        result = result.replace(escape + name + escape, delimiters[i])
    result = result.replace(escape + 'E' + escape, escape)
    return result


if __name__ == '__main__':
    class CTestRecord(CRecord):
        structure = {
                       'recordType': ( 0,       str),
                       'seqNo'     : ( 1,       int),
                       'greeting'  : ( 2,       unicode),
                       'age'       : ( 3,       int),
                       'lastName'  : ( (5,0,0), unicode),
                       'firstName' : ( (5,0,1), unicode),
                       'patrName'  : ( (5,0,2), unicode),
                    }
        recordType = 'T'

    r = CTestRecord()
    r.seqNo     = 1
    r.greeting  = 'hello'
    r.age       = 321
    r.lastName  = 'Ivanov'
    r.firstName = u'Ivan|\\^&:)'
    r.patrName  = u'Иванович'

    print r._storage
    print r.greeting, r.age, r.lastName, r.firstName, r.patrName
    s = r.asString('|\\^&', 'cp1251')
    print s

    r1 = CTestRecord()
    r1.setString(s, '|\\^&', 'cp1251')
    print r1.greeting, r1.age, r1.lastName, r1.firstName, r1.patrName
