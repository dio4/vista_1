# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui


class CEnum(object):
    nameMap = {}

    @classmethod
    def getNameList(cls):
        if not hasattr(cls, '_nameList'):
            cls._nameList = map(cls.getName, cls.keys())
        return cls._nameList

    @classmethod
    def keys(cls):
        return sorted(cls.nameMap)

    @classmethod
    def getName(cls, key):
        return cls.nameMap.get(key, u'')

    @classmethod
    def count(cls):
        return len(cls.nameMap)


class CEnumModel(QtCore.QAbstractListModel):
    NoneName = u'<Не задано>'

    def __init__(self, enum, keys=None, addNone=False, specialValues=None):
        QtCore.QAbstractListModel.__init__(self)
        self._enum = enum
        self._specialValues = specialValues or {}
        self._keys = []
        if addNone:
            self._keys.append(None)
        if specialValues:
            self._keys.extend(specialValues.keys())
        self._keys.extend(keys if keys is not None else self._enum.keys())

    def rowCount(self, index=None, *args, **kwargs):
        return len(self._keys)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()

        row = index.row()
        if 0 <= row < self.rowCount() and role == QtCore.Qt.DisplayRole:
            key = self._keys[row]
            if key in self._specialValues:
                value = self._specialValues[key]
            else:
                value = self.NoneName if key is None else self._enum.getName(key)
            return QtCore.QVariant(value)

        return QtCore.QVariant()

    def getValue(self, row):
        if 0 <= row < self.rowCount():
            return self._keys[row]
        return None

    def getValueIndex(self, key):
        try:
            index = self._keys.index(key)
        except ValueError:
            index = None
        return index


class CEnumComboBox(QtGui.QComboBox):
    def value(self):
        return self.model().getValue(self.currentIndex())

    def setValue(self, value):
        index = self.model().getValueIndex(value)
        if index is not None:
            self.setCurrentIndex(index)

    def setEnum(self, enumClass, keys=None, addNone=False, specialValues=None):
        self.setModel(CEnumModel(enumClass, keys=keys, addNone=addNone, specialValues=specialValues))
