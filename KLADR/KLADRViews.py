#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.TableView import CTableView


class CKLADRTreeView(QtGui.QTreeView):
    __pyqtSignals__ = ('hide()',)

    def __init__(self, parent):
        QtGui.QTreeView.__init__(self, parent)
        self.header().hide()
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.connect(self, QtCore.SIGNAL('expanded(QModelIndex)'), self.onExpanded)
#        self.connect(self, QtCore.SIGNAL('collapsed(QModelIndex)'), self.onCollapsed)
        self.searchString = ''
        self.searchParent = None

    def setRootIndex(self, index):
        pass

    def onExpanded(self, index):
        self.scrollTo(index, QtGui.QAbstractItemView.PositionAtTop)
#        self.searchString = ''

#    def onCollapsed(self, index):
#        self.searchString = ''


#    def resizeEvent(self, AResizeEvent):
#        QtGui.QTreeView.resizeEvent(self, AResizeEvent)
#        self.resizeColumnToContents(0)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Left or event.key() == QtCore.Qt.Key_Minus:
            current = self.currentIndex()
            if self.isExpanded(current) and self.model().rowCount(current):
                self.collapse(current)
            else:
                self.setCurrentIndex(current.parent())
                current = self.currentIndex()
                self.collapse(current)
                self.scrollTo(current, QtGui.QAbstractItemView.PositionAtTop)
            event.accept()
            return
        if event.key() == QtCore.Qt.Key_Right or event.key() == QtCore.Qt.Key_Plus:
            current = self.currentIndex()
            if not self.isExpanded(current) and self.model().rowCount(current):
                self.expand(current)
            event.accept()
            return
        if event.key() == QtCore.Qt.Key_Backspace:
            self.searchString = self.searchString[:-1]
            self.keyboardSearchBase(self.searchString)
            event.accept()
            return
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            event.accept()
            self.emit(QtCore.SIGNAL('doubleClicked(QModelIndex)'), self.currentIndex())
            return
        if event.key() == QtCore.Qt.Key_Space:
            event.accept()
            self.emit(QtCore.SIGNAL('hide()'))
            return
        return QtGui.QTreeView.keyPressEvent(self, event)


    def keyboardSearch(self, search):
        current = self.currentIndex()
        if self.searchParent != current.parent():
            self.searchString = u''
            self.searchParent = current.parent()
        self.keyboardSearchBase(self.searchString + unicode(search).upper())


    def keyboardSearchBase(self, searchString):
#        print len(searchString)
        found = self.model().keyboardSearch(self.searchParent, searchString)
        if found.isValid():
            if self.currentIndex() != found or len(self.searchString) > len(searchString):
                self.setCurrentIndex(found)
                self.searchString = searchString


class CKLADRSearchResult(CTableView):
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            event.accept()
            self.emit(QtCore.SIGNAL('doubleClicked(QModelIndex)'), self.currentIndex())
        else:
            CTableView.keyPressEvent(self, event)