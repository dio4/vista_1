# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.crbcombobox    import CRBModelDataCache, CRBComboBox
from library.InDocTable     import CInDocTableCol
from library.TreeModel      import CDBTreeModel
from library.Utils          import forceRef, toVariant


class CJobTypeModel(CDBTreeModel):
    def __init__(self, parent):
        CDBTreeModel.__init__(self, parent, 'rbJobType', 'id', 'group_id', 'name', order='code')
#            self.treeModel.setRootItem(CDBTreeItem(None, domain, rootItemId, self.treeModel))
        self.setRootItemVisible(True)
        self.setLeavesVisible(True)


class CJobTypePopupView(QtGui.QTreeView):
    def __init__(self, parent):
        QtGui.QTreeView.__init__(self, parent)
        self.header().hide()
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setMinimumHeight(150)
        self.connect(self, QtCore.SIGNAL('expanded(QModelIndex)'), self.onExpanded)
        self.searchString = ''
        self.searchParent = None


    def setRootIndex(self, index):
        pass

    def setRealRootIndex(self, index):
        QtGui.QTreeView.setRootIndex(self, index)
#        self.expandAll()


    def onExpanded(self, index):
        self.scrollTo(index, QtGui.QAbstractItemView.PositionAtTop)


class CJobTypeComboBox(QtGui.QComboBox):
    def __init__(self, parent):
        QtGui.QComboBox.__init__(self, parent)
        self.SizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.setModelColumn(0)
#        self.__searchString = ''
        self._model = CJobTypeModel(self)
        self.setModel(self._model)
        self._popupView = CJobTypePopupView(self)
        self._popupView.setObjectName('popupView')
        self._popupView.setModel(self._model)
        self.setView(self._popupView)
        self._popupView.installEventFilter(self)
        self._popupView.viewport().installEventFilter(self)
        QtCore.QObject.connect(self._popupView, QtCore.SIGNAL('activated(QModelIndex)'), self.on_ItemActivated)
        QtCore.QObject.connect(self._popupView, QtCore.SIGNAL('entered(QModelIndex)'), self.setCurrentIndex)
        self.setExpandAll(True)



    def setValue(self, id):
        index = self._model.findItemId(id)
        if index:
            self.setCurrentIndex(index)


    def setExpandAll(self, value):
        self._expandAll = value


    def value(self):
        modelIndex = self._model.index(self.currentIndex(), 0, self.rootModelIndex())
        if modelIndex.isValid():
            return self._model.itemId(modelIndex)
        return None


    def on_ItemActivated(self, index):
        if index.isValid():
            if (int(index.flags()) & QtCore.Qt.ItemIsSelectable) != 0 :
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
#        self._popupView.setCurrentIndex(modelIndex)


    def setCurrentIndex(self, index):
        self.setRootModelIndex(index.parent())
        QtGui.QComboBox.setCurrentIndex(self, index.row())
#        self.emit(QtCore.SIGNAL('codeSelected(QString)'), self._model.code(index))


    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress: # and obj == self.__popupView :
            if event.key() in [ QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return, QtCore.Qt.Key_Select ] :
                index = self._popupView.currentIndex()
                if index.isValid() and (int(index.flags()) & QtCore.Qt.ItemIsSelectable) != 0 :
                    self.hidePopup()
                    self.setCurrentIndex(index)
                    self.emit(QtCore.SIGNAL('itemSelected(QModelIndex)'), index)
                return True
            return False
        if event.type() == QtCore.QEvent.MouseButtonRelease and obj == self._popupView.viewport():
            self._popupView.mouseReleaseEvent(event)  # i1883.c12401 - нужна реакция на mouseRelease от QTreeView
            return True
        return False



class CJobTypeInDocTableCol(CInDocTableCol):
    def __init__(self, title, fieldName, width):
        CInDocTableCol.__init__(self, title, fieldName, width)


    def toString(self, val, record):
        cache = CRBModelDataCache.getData('rbJobType', True)
        text = cache.getStringById(forceRef(val), CRBComboBox.showName)
        return toVariant(text)


    def toStatusTip(self, val, record):
        cache = CRBModelDataCache.getData('rbJobType', True)
        text = cache.getStringById(forceRef(val), CRBComboBox.showCodeAndName)
        return toVariant(text)


    def createEditor(self, parent):
        editor = CJobTypeComboBox(parent)
        editor.model().getRootItem()._name = u'не задано'
        return editor


    def setEditorData(self, editor, value, record):
        editor.setValue(forceRef(value))


    def getEditorData(self, editor):
        return toVariant(editor.value())