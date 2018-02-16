# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtGui, QtCore


class CTreeView(QtGui.QTreeView):
    def __init__(self, parent):
        QtGui.QTreeView.__init__(self, parent)
        self._popupMenu = None

#        h = self.fontMetrics().height()
#        self.verticalHeader().setDefaultSectionSize(3*h/2)
#        self.verticalHeader().hide()
#        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
#        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
#        self.setAlternatingRowColors(True)
#        self.horizontalHeader().setStretchLastSection(True)
        self.collapseAll(True)

    def collapseAll(self, remember=True):
        if remember:
            self._treeDepth = 0
        QtGui.QTreeView.collapseAll(self)

    # def expand(self, index):
    #     QtGui.QTreeView.setExpanded(index, True)
    #     QtGui.QTreeView.expand(index)

    # def isExpanded(self, QModelIndex):
    #     pass
    #
    # def setExpanded(self, QModelIndex, bool):
    #     pass

    def createPopupMenu(self, actions=None):
        if not actions:
            actions = []
        self._popupMenu = QtGui.QMenu(self)
        self._popupMenu.setObjectName('popupMenu')
        for action in actions:
            if isinstance(action, QtGui.QAction):
                self._popupMenu.addAction(action)
            elif action == '-':
                self._popupMenu.addSeparator()
        self.connect(self._popupMenu, QtCore.SIGNAL('aboutToShow()'), self.popupMenuAboutToShow)
        return self._popupMenu


    def setPopupMenu(self, menu):
        self._popupMenu = menu


    def popupMenu(self):
        return self._popupMenu


    def popupMenuAboutToShow(self):
        pass
#        if self.__actDeleteRow :
#            self.__actDeleteRow.setEnabled(self.model().rowCount()>0)


    def contextMenuEvent(self, event): # event: QContextMenuEvent
        if self._popupMenu:
            self._popupMenu.exec_(event.globalPos())
            event.accept()
        else:
            event.ignore()

    def dragEnterEvent(self, event):
        for mimeType in self.model().mimeTypes():
            if event.mimeData().hasFormat(mimeType):
                event.acceptProposedAction()
                break
        super(CTreeView, self).dragEnterEvent(event)

    def dropEvent(self, event):
        index = self.indexAt(event.pos())
        if index.row() < 0:
            return
        for mimeType in self.model().mimeTypes():
            if event.mimeData().hasFormat(mimeType):
                self.model().dropMimeData(event.mimeData(), event.proposedAction(), index.row(), index.column(), index)
                self.selectionModel().emit(QtCore.SIGNAL('currentChanged(QModelIndex, QModelIndex)'), self.currentIndex(), self.currentIndex())
                break
            event.acceptProposedAction()
