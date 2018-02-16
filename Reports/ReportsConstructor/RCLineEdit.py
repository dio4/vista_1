# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore
from library.Utils                         import forceString
from models.RCFieldsTreeModel import CQueryFieldsTreeModel

import re


class CRCLineEdit(QtGui.QLineEdit):
    def __init__(self, parent):
        QtGui.QLineEdit.__init__(self, parent)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            event.ignore()
            return
        return QtGui.QLineEdit.keyPressEvent(self, event)

class CRCCompleter(QtGui.QCompleter):
    def __init__(self, parent):
        QtGui.QCompleter.__init__(self, parent)
        self.setCompletionRole(QtCore.Qt.DisplayRole)
        self.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        self.setCaseSensitivity(QtCore.Qt.CaseInsensitive)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            event.accept()
            return
        return QtGui.QLineEdit.keyPressEvent(self, event)

class CRCFieldLineEdit(CRCLineEdit):
    def __init__(self, parent, model=None):
        CRCLineEdit.__init__(self, parent)
        self._model = None
        self.setModel(model)

    def setModel(self, model=None):
        if not model:
            return
        self._model = CQueryFieldsTreeModel(self)
        self._model._items = model._items
        self._model._rootItem = model._rootItem
        self.setCompleter(CRCFiledCompleter(self, self._model))

class CRCFiledCompleter(CRCCompleter):
    def __init__(self, parent, model):
        CRCCompleter.__init__(self, parent)
        self.setModel(model)
        self.setCompletionColumn(0)

    def splitPath(self, path):
        pattern = re.compile('([ \(\)\+\-\*\\\/=])')
        list = pattern.split(path)
        if len(list):
            return list[-1].split('.')
        return list

    def getCurrentText(self):
        pattern = re.compile('([ \(\)\+\-\*\\\/=])')
        textList = pattern.split(self.parent().text())
        if len(textList):
            return u''.join([forceString(str) for str in textList[:-1]])
        return u''

    def pathFromIndex(self, index):
        result = []
        item = index.internalPointer()
        currentText = self.getCurrentText()
        while index.isValid() and (item and item._name != u'все' and item._field):
            result = [forceString(self.model().data(index, QtCore.Qt.DisplayRole))] + result
            index = index.parent()
            item = index.internalPointer()
        return u''.join([currentText, u'.'.join(result)])

class CRCColsLineEdit(CRCLineEdit):
    def __init__(self, parent, model=None, modelFunctions=None):
        CRCLineEdit.__init__(self, parent)
        self._model = None
        self.setModel(model, modelFunctions)
        self.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(u'^\$[a-zA-Z]+\([a-zA-Zа-яА-ЯЁё\.]+\)$|^[a-zA-Zа-яА-ЯЁё\.]+$|^\'.+\'$'), self))

    def setModel(self, model=None, modelFunctions=None):
        from Reports.ReportsConstructor.models.RCTableModel import CRCColsItemModel
        if not model:
            return
        self._model = CRCColsItemModel(self)
        self._model.setModelCols(model)
        self._model.setModelFunctions(modelFunctions)
        self.setCompleter(CRCColsCompleter(self, self._model))

    def getValue(self):
        return self._model.getValue(self.text())

    def setValue(self, value):
        self.setText(self._model.parceValue(value))

class CRCColsCompleter(CRCCompleter):
    def __init__(self, parent, model):
        CRCCompleter.__init__(self, parent)
        self.setModel(model)
        self.setCompletionColumn(0)

    def splitPath(self, path):
        pattern = re.compile('([ \(])')
        list = pattern.split(path)
        if len(list):
            return [list[-1]]
        return list

    def getCurrentText(self):
        pattern = re.compile('([ \(])')
        textList = pattern.split(self.parent().text())
        if len(textList):
            return u''.join([forceString(str) for str in textList[:-1]])
        return u''

    def pathFromIndex(self, index):
        currentText = self.getCurrentText()
        result = forceString(self.model().data(index, QtCore.Qt.DisplayRole))
        return u''.join([currentText, result])

class CRCAliasLineEdit(QtGui.QLineEdit):
    def __init__(self, parent):
        QtGui.QLineEdit.__init__(self, parent)
        self.connect(self, QtCore.SIGNAL('textEdited(QString)'), self.on_textEdited)

    def on_textEdited(self, text):
        text = re.sub(u'[^a-zA-Z0-9а-яА-ЯёЁ]', '_', forceString(text), re.UNICODE)
        self.setText(text)