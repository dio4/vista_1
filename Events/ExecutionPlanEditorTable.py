# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from library.TableView  import CTableView
from Timeline.TimeTable import CTimeItemDelegate


class CExecutionPlanEditorTable(CTableView):
    def __init__(self, parent):
        CTableView.__init__(self, parent)
        self.verticalHeader().show()
        self.verticalHeader().setResizeMode(QtGui.QHeaderView.Fixed)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setStretchLastSection(True)
        self.setTabKeyNavigation(True)
        self.setEditTriggers(QtGui.QAbstractItemView.AnyKeyPressed | QtGui.QAbstractItemView.EditKeyPressed | QtGui.QAbstractItemView.SelectedClicked | QtGui.QAbstractItemView.DoubleClicked)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setItemDelegateForColumn(0, CTimeItemDelegate(self))

