# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui


class CFilterPropertyOptionsItem(QtGui.QListWidgetItem):
    def __init__(self, strItem, parent):
        QtGui.QListWidgetItem.__init__(self, strItem, parent)
        self.statusChecked = True
        self.strItem = strItem


    def flags(self, index):
        if not index.isValid():
            return 0
        item = index.internalPointer()
        return item.flags()|QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsUserCheckable


    def data(self, role):
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return QtCore.QVariant(self.strItem)
        elif role == QtCore.Qt.CheckStateRole:
            return QtCore.QVariant(QtCore.Qt.Checked if not self.statusChecked else QtCore.Qt.Unchecked)
        return QtCore.QVariant()


    def setData(self, role, value):
        if role == QtCore.Qt.CheckStateRole:
            if not self.statusChecked:
                self.statusChecked = True
            else:
                self.statusChecked = False
