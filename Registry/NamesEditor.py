# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtGui, QtCore

from library.Utils              import forceString, toVariant

class CFirstNameEditor(QtGui.QLineEdit):
    def __init__(self, parent=None):
        QtGui.QLineEdit.__init__(self, parent)
        result = []
        self._completerModel = CNameCompleterModel(self, result, u'rdFirstName')
        self._completer = CCompleter(self, self._completerModel)
        self.setCompleter(self._completer)


class CPatrNameEditor(QtGui.QLineEdit):
    def __init__(self, parent=None):
        QtGui.QLineEdit.__init__(self, parent)
        result = []
        self._completerModel = CNameCompleterModel(self, result, u'rdPatrName')
        self._completer = CCompleter(self, self._completerModel)
        self.setCompleter(self._completer)


class CCompleter(QtGui.QCompleter):
    def __init__(self, parent, model):
        QtGui.QCompleter.__init__(self, parent)
        self.setCompletionMode(QtGui.QCompleter.InlineCompletion)
        self.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setModelSorting(QtGui.QCompleter.CaseInsensitivelySortedModel)
        self.setModel(model)
        self._model = model

    def splitPath(self, prefix):
        if len(prefix) > 2:
            self._model.dataReadName(prefix[:2])
        return [prefix]


class CNameCompleterModel(QtCore.QAbstractListModel):
    def __init__(self, parent, strings, tableName = None):
        QtCore.QAbstractListModel.__init__(self, parent)
        self._tableName = tableName
        self.listPrefixName = set()
        self._strings = []

    def rowCount(self, parentIndex = QtCore.QModelIndex()):
        return len(self._strings)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        return toVariant(self._strings[index.row()])

    def addStrings(self, strings):
        self._strings += strings
        self._strings.sort()
        self.reset()

    def getNameDataBase(self, prefix):
        db = QtGui.qApp.db
        result = []
        try:
            if self._tableName:
                table = db.table(self._tableName)
                records = db.getRecordList(table, 'name', table['name'].like(unicode(prefix)+'%'))
                result = [forceString(record.value('name')) for record in records]
        except:
            pass
        return result

    def dataReadName(self, prefix):
        if prefix not in self.listPrefixName:
            self.addStrings(self.getNameDataBase(prefix))
            self.listPrefixName.add(prefix)
