# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from library.TableView          import CTableView


class CFreeQueueTableView(CTableView):
    def __init__(self, parent=None):
        CTableView.__init__(self, parent)
        self.currentItemKey = None
        self.offset = 0
        self.currentColumn = 0
        self.horizontalPosition = 0


    def setModel(self, model):
        oldModel = self.model()
        if oldModel:
            QtCore.QObject.disconnect(oldModel, QtCore.SIGNAL('beforeReset()'), self.storeRowPos)
            QtCore.QObject.disconnect(oldModel, QtCore.SIGNAL('afterReset()'), self.restoreRowPos)
        CTableView.setModel(self, model)
        if model:
            QtCore.QObject.connect(model, QtCore.SIGNAL('beforeReset()'), self.storeRowPos)
            QtCore.QObject.connect(model, QtCore.SIGNAL('afterReset()'), self.restoreRowPos)


    def storeRowPos(self):
        topIndex = self.indexAt(QtCore.QPoint(0,0))
        topRow = topIndex.row() if topIndex.isValid() else 0
        currentIndex = self.currentIndex()
        currentRow = currentIndex.row() if currentIndex.isValid() else max(0, topRow)
        self.currentColumn = currentIndex.column() if currentIndex.isValid() else 0
        model = self.model()
        if currentRow<len(model.items):
            self.currentItemKey = model.getKey(currentRow)
            self.offset = currentRow-topRow
        else:
            self.currentItemKey = None
            self.offset = topRow
        self.horizontalPosition = self.horizontalScrollBar().value()


    def restoreRowPos(self):
        model = self.model()
        if self.currentItemKey:
            row = model.lookupRowByKey(self.currentItemKey)
            self.scrollTo(model.index(max(0, row-self.offset), 0), QtGui.QAbstractItemView.PositionAtTop)
            self.setCurrentIndex(model.index(max(0, row), self.currentColumn))
        else:
            self.scrollTo(model.index(self.offset, 0), QtGui.QAbstractItemView.PositionAtTop)
            self.setCurrentIndex(model.index(0, 0))
        self.horizontalScrollBar().setValue(self.horizontalPosition)
