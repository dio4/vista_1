# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from library.Utils              import *
from Registry.NamesEditor import CNameCompleterModel


#class CCompleterModel(QAbstractListModel):
#    def __init__(self, parent, tableName):
#        QAbstractListModel.__init__(self, parent)


class CStaticCompleterModel(QAbstractListModel):
    def __init__(self, parent, strings):
        QAbstractListModel.__init__(self, parent)
        self.__strings = [toVariant(s) for s in strings]

    def rowCount(self, parentIndex = QtCore.QModelIndex()):
        return len(self.__strings)

    def data(self, index, role=Qt.DisplayRole):
        return self.__strings[index.row()]



class CCompleter(QtGui.QCompleter):
    def __init__(self, parent, model):
        QtGui.QCompleter.__init__(self, parent)
        self.setCompletionMode(QtGui.QCompleter.InlineCompletion)
        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setModelSorting(QtGui.QCompleter.CaseInsensitivelySortedModel)
        self.setModel(model)




class CNameCompleter(QtGui.QCompleter):
    def __init__(self, parent, model):
        self.setCompletionMode(QtGui.QCompleter.InlineCompletion)
        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setModelSorting(QtGui.QCompleter.CaseInsensitivelySortedModel)
        self.setModel(model)


class CFirstNameCompleter(CNameCompleter):
    model = None

    def __init__(self, parent):
        if not CFirstNameCompleter.model:
            CFirstNameCompleter.model = CNameCompleterModel(self, 'rdFirstName')
        CFirstNameCompleter.__init__(self, parent, CFirstNameCompleter.model)
