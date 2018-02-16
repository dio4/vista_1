# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

from Registry.NamesEditor import CNameCompleterModel


#Atronah:  есть аналогичный и более полный класс в Registry/NameEditor
#class CNameCompleterModel(QAbstractListModel):
#    def __init__(self, parent, tableName):
#        QAbstractListModel.__init__(self, parent)
#
#Atronah: не используется во всем проекте
#class CStaticNameCompleterModel(CNameCompleterModel):
#    def __init__(self, parent, strings):
#        QAbstractListModel.__init__(self, parent)
#        self.strings = [s.toVariant() for s in strings]
#
#    def data(self, index, role=Qt.DisplayRole):
#        return self.strings[index.row()]
#
#    def rowCount(self, parentIndex = QModelIndex()):
#        return len(self.strings)

class CNameCompleter(QtGui.QCompleter):
    def __init__(self, parent, model):
        self.setCompletionMode(QtGui.QCompleter.InlineCompletion)
        self.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setModelSorting(QtGui.QCompleter.CaseInsensitivelySortedModel)
        self.setModel(model)


class CFirstNameCompleter(CNameCompleter):
    model = None

    def __init__(self, parent):
        if CFirstNameCompleter.model == None:
            CFirstNameCompleter.model = CNameCompleterModel(self, 'rdFirstName')
        CFirstNameCompleter.__init__(self, parent, CFirstNameCompleter.model)
