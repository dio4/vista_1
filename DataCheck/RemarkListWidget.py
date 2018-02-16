# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils import forceInt


class CRemarkListWidget(QtGui.QListWidget):
    def __init__(self, parent):
        QtGui.QListWidget.__init__(self, parent)
        self._popupMenu = None
        self.checkRunListWidget = False
        self.recordBufferCorrectLW = []


    def createPopupMenu(self, actions=None):
        if not actions:
            actions = []
        self._popupMenu = QtGui.QMenu(self)
        self._popupMenu.setObjectName('popupMenu')
        self.connect(self._popupMenu, QtCore.SIGNAL('aboutToShow()'), self.popupMenuAboutToShow)
        self._actSelectCurrentError = QtGui.QAction(u'Выбрать по текущему типу ошибки', self)
        self._actSelectCurrentError.setObjectName('actSelectCurrentError')
        self.connect(self._actSelectCurrentError, QtCore.SIGNAL('triggered()'), self.selectCurrentError)
        self._popupMenu.addAction(self._actSelectCurrentError)
        return self._popupMenu


    def popupMenuAboutToShow(self):
        if self._actSelectCurrentError:
            self._actSelectCurrentError.setEnabled(True)


    def selectCurrentError(self):
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        try:
            if self.checkRunListWidget:
                listItemsSelectControl = self.selectedItems()
                correctSelect = []
                resSelect = []
                itemsSelect = []
                selectionModel = QtGui.QItemSelectionModel(self.model())
                for itemsSelect in listItemsSelectControl:
                    row = self.row(itemsSelect)
                    correctSelect.append(self.recordBufferCorrectLW[row])
                for resSelect in correctSelect:
                    errorName = forceInt(resSelect)
                    i = 0
                    for bufferCorrectLW in self.recordBufferCorrectLW:
                        if forceInt(bufferCorrectLW) == errorName:
                            self.setCurrentRow(i, selectionModel.Select)
                        i += 1
        finally:
            QtGui.qApp.restoreOverrideCursor()


    def contextMenuEvent(self, event): # event: QContextMenuEvent
        if self._popupMenu:
            self._popupMenu.exec_(event.globalPos())
            event.accept()
        else:
            event.ignore()
