# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
import email.utils
from PyQt4             import QtCore, QtGui
from PyQt4.QtCore      import *

from Accounting.Utils  import CContractTreeModel


class CContractPopupView(QtGui.QTreeView):
    def __init__(self, parent):
        QtGui.QTreeView.__init__(self, parent)
        self.header().hide()
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setMinimumHeight(150)
        self.connect(self, QtCore.SIGNAL('expanded(QModelIndex)'), self.onExpanded)
#        self.connect(self, QtCore.SIGNAL('collapsed(QModelIndex)'), self.onCollapsed)
        self.searchString = ''
        self.searchParent = None


    def setRootIndex(self, index):
        pass

    def setRealRootIndex(self, index):
        QtGui.QTreeView.setRootIndex(self, index)
#        self.expandAll()


    def onExpanded(self, index):
        self.scrollTo(index, QtGui.QAbstractItemView.PositionAtTop)


class CContractComboBox(QtGui.QComboBox):
    def __init__(self, parent):
        QtGui.QComboBox.__init__(self, parent)
        self.SizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.setModelColumn(0)
        self._model = CContractTreeModel(self)
        self.setModel(self._model)
        self._popupView = CContractPopupView(self)
        self._popupView.setObjectName('popupView')
        self._popupView.setModel(self._model)
        self.setView(self._popupView)
        self._popupView.installEventFilter(self)
        self._popupView.viewport().installEventFilter(self)
        QtCore.QObject.connect(self._popupView, QtCore.SIGNAL('activated(QModelIndex)'), self.on_ItemActivated)
        QtCore.QObject.connect(self._popupView, QtCore.SIGNAL('entered(QModelIndex)'), self.setCurrentIndex)
        self.setExpandAll(True)


    def getPath(self):
        index = self._model.index(self.currentIndex(), 0, self.rootModelIndex())
        item = index.internalPointer()
        parts = []
        while item:
            parts.append(email.utils.quote(item.name))
            item = item.parent
        return '\\'.join(parts[::-1])


    def setPath(self, path):
        names = [email.utils.unquote(part) for part in path.split('\\')][1:]
        item = self._model.getRootItem()
        for name in names:
            nextItem = item.mapNameToItem.get(name, None)
            if nextItem:
                item = nextItem
            else:
                break
        index = self._model.createIndex(item.row(), 0, item)
        self.setCurrentIndex(index)

    # Чтобы сбросить фильтр, передайте None
    def setFinanceTypeCodes(self, financeTypeCodeList):
        self._model.setFinaceTypeCodes(financeTypeCodeList)

    def getPathById(self, contractId):
        path = self._model.getPathById(contractId)
        return '\\'.join(path)
        
    def getIdByPath(self, path):
        return self._model.getIdByPath(path)

    def getIdList(self):
        index = self._model.index(self.currentIndex(), 0, self.rootModelIndex())
        item = index.internalPointer()
        return item.idList

    def setExpandAll(self, value):
        self._expandAll = value


#    def value(self):
#        modelIndex = self._model.index(self.currentIndex(), 0, self.rootModelIndex())
#        if modelIndex.isValid():
#            return self._model.itemId(modelIndex)
#        return None


    def on_ItemActivated(self, index):
        if index.isValid():
            if (int(index.flags()) & Qt.ItemIsSelectable) != 0:
                self.hidePopup()
                self.emit(QtCore.SIGNAL('itemSelected(QModelIndex)'), index)
            else:
                self._popupView.setExpanded(index, not self._popupView.isExpanded(index))


    def showPopup(self):
        modelIndex = self._model.index(self.currentIndex(), 0, self.rootModelIndex())
        self._popupView.setRealRootIndex(QtCore.QModelIndex())
        if self._expandAll:
            self._popupView.expandAll()
        else:
            rootIndex = self._model.index(0,0)
            self._popupView.setExpanded(rootIndex, True)
        QtGui.QComboBox.showPopup(self)


    def setCurrentIndex(self, index):
        self.setRootModelIndex(index.parent())
        QtGui.QComboBox.setCurrentIndex(self, index.row())


    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress: # and obj == self.__popupView:
            if event.key() in [ Qt.Key_Enter, Qt.Key_Return, Qt.Key_Select ]:
                index = self._popupView.currentIndex()
                if index.isValid() and (int(index.flags()) & Qt.ItemIsSelectable) != 0:
                    self.hidePopup()
                    self.setCurrentIndex(index)
                    self.emit(QtCore.SIGNAL('itemSelected(QModelIndex)'), index)
                return True
            return False
        if event.type() == QEvent.MouseButtonRelease and obj == self._popupView.viewport():
            self._popupView.mouseReleaseEvent(event)  # i1883.c12401 - нужна реакция на mouseRelease от QTreeView
            return True
        return False
