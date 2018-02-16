# -*- coding: utf-8 -*-
import itertools
from PyQt4 import QtCore, QtGui, QtSql

from library.Enum import CEnum
from library.ItemListModel import CItemTableCol
from library.Utils import forceInt, forceString, toVariant


class CColHandler(object):
    u""" Базовый обработчик чтения/записи значения ячейки """

    def value(self, item, **params):
        return None

    def setValue(self, item, value, **params):
        pass


class RecValue(CColHandler):
    u""" Поле QtSql.SqlRecord """

    def __init__(self, fieldName):
        self._fieldName = fieldName

    def value(self, item, **params):
        return item.value(self._fieldName) if isinstance(item, QtSql.QSqlRecord) else None

    def setValue(self, item, value, **params):
        if isinstance(item, QtSql.QSqlRecord):
            item.setValue(self._fieldName, toVariant(value))


class RecValues(CColHandler):
    u""" Список полей QtSql.QSqlRecord """

    def __init__(self, fields):
        self._fields = fields

    def value(self, item, **params):
        if isinstance(item, QtSql.QSqlRecord):
            return [item.value(field) for field in self._fields]
        return [None for field in self._fields]

    def setValue(self, item, values, **params):
        if isinstance(item, QtSql.QSqlRecord):
            for fileldName, value in itertools.izip(self._fields, values):
                item.setValue(fileldName, toVariant(value))


class Index(CColHandler):
    u""" Доступ по индексу """

    def __init__(self, idx, defaultValue=None):
        self._idx = idx
        self._default = defaultValue

    def value(self, item, **params):
        try:
            return item[self._idx]
        except IndexError:
            return self._default

    def setValue(self, item, value, **params):
        try:
            item[self._idx] = value
        except IndexError:
            pass


class Attrib(CColHandler):
    u""" Доступ по имени аттрибута """

    def __init__(self, attribName, defaultValue=None):
        self._attribName = attribName
        self._default = defaultValue

    def value(self, item, **params):
        return getattr(item, self._attribName, self._default)

    def setValue(self, item, value, **params):
        setattr(item, self._attribName, value)


class NestedAttrib(CColHandler):
    u""" Вложенный аттрибут """

    def __init__(self, attribs, defaultValue=None):
        self._attribs = attribs.split('.') if isinstance(attribs, (str, unicode)) else attribs
        self._default = defaultValue

    def value(self, item, **params):
        v = item
        for attr in self._attribs:
            v = getattr(v, attr, None)
        return self._default if v is None else v

    def setValue(self, item, value, **params):
        if self._attribs:
            obj = item
            for attr in self._attribs[:-1]:
                obj = getattr(obj, attr, None)
            setattr(obj, self._attribs[-1], value)


class CColView(object):
    u""" Базовое отображение значения столбца """

    def displayValue(self, item, value, **params):
        return value

    def sortValue(self, item, value, **params):
        return value

    def textColor(self, item, value, **params):
        return None

    def bgColor(self, item, value, **params):
        return None

    def toolTip(self, item, value, **params):
        return None

    def checkState(self, item, value, **params):
        return None


class BoolView(CColView):
    def checkState(self, item, value, **params):
        return QtCore.Qt.Checked if bool(value) else QtCore.Qt.Unchecked


class NameView(CColView):
    def displayValue(self, item, value, **params):
        return unicode(value).capitalize() if value else u''


class DateView(CColView):
    def __init__(self, dateFormat='dd.MM.yyyy'):
        self._format = dateFormat

    def displayValue(self, item, value, **params):
        return value.toString(self._format) if value else u''


class EnumView(CColView):
    def __init__(self, enum):
        self._enum = enum  # type: CEnum

    def displayValue(self, item, value, **params):
        return self._enum.getName(value)


class CColEditor(object):
    u""" Базовый редактор знаяения столбца """

    def createEditor(self, parent, item):
        return QtGui.QLineEdit(parent)

    def setData(self, editor, value, item):
        editor.setText(forceString(value))

    def getData(self, editor):
        return QtCore.QVariant(editor.text())


class StringEditor(CColEditor):
    def createEditor(self, parent, item):
        return QtGui.QLineEdit(parent)

    def setData(self, editor, value, item):
        editor.setText(forceString(value))

    def getData(self, editor):
        return forceString(editor.text())


class CIntColEditor(CColEditor):
    def __init__(self, min=None, max=None, step=None):
        self._min = min
        self._max = max
        self._step = step

    def getMinimum(self, item):
        return self._min

    def getMaximum(self, item):
        return self._max

    def createEditor(self, parent, item):
        editor = QtGui.QSpinBox(parent)
        minimum = self.getMinimum(item)
        if minimum is not None:
            editor.setMinimum(minimum)
        maximum = self.getMaximum(item)
        if maximum is not None:
            editor.setMaximum(maximum)
        if self._step is not None:
            editor.setSingleStep(self._step)
        return editor

    def setData(self, editor, value, item):
        u"""
        :type editor: QtGui.QSpinBox
        :param value:
        :param item:
        """
        editor.setValue(forceInt(value))

    def getData(self, editor):
        u"""
        :type editor: QtGui.QSpinBox
        """
        return QtCore.QVariant(editor.value())


class CItemCol(CItemTableCol):
    def __init__(self, title, handler=None, view=None, editor=None, **kwargs):
        super(CItemCol, self).__init__(title, **kwargs)
        self._handler = handler  # type: CColHandler
        self._view = view  # type: CColView
        self._editor = editor  # type: CColEditor

    def value(self, item, **params):
        return self.handler(item).value(item, **params)

    def displayValue(self, item, **params):
        value = self.value(item, **params)
        return self.view(item).displayValue(item, value, **params)

    def sortValue(self, item, **params):
        value = self.value(item, **params)
        return self.view(item).sortValue(item, value, **params)

    def setValue(self, item, value, **params):
        self.handler(item).setValue(item, value, **params)

    def textColor(self, item, **params):
        value = self.value(item, **params)
        return self.view(item).textColor(item, value, **params)

    def bgColor(self, item, **params):
        value = self.value(item, **params)
        return self.view(item).bgColor(item, value, **params)

    def toolTip(self, item, **params):
        value = self.value(item, **params)
        return self.view(item).toolTip(item, value, **params)

    def checkState(self, item, **params):
        value = self.value(item, **params)
        return self.view(item).checkState(item, value, **params)

    def createEditor(self, parent, item):
        return self.editor(item).createEditor(parent, item)

    def setEditorData(self, editor, value, item):
        self.editor(item).setData(editor, value, item)
        # raise NotImplementedError

    def getEditorData(self, editor):
        return self._editor.getData(editor)

    def handler(self, item):
        return self._handler if self._handler else self.defaultHandler()

    def view(self, item):
        return self._view if self._view else self.defaultView()

    def editor(self, item):
        return self._editor if self._editor else self.defaultEditor()

    def defaultHandler(self):
        return CColHandler()

    def defaultView(self):
        return CColView()

    def defaultEditor(self):
        return CColEditor()
