# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

from library.TreeView                  import CTreeView

class CRCTreeView(CTreeView):
    def __init__(self, parent):
        CTreeView.__init__(self, parent)
        self.expandedItemsState = {}

    def onExpanded(self, index):
        self.scrollTo(index, QtGui.QAbstractItemView.PositionAtTop)

    def saveExpandedState(self):
        def saveStateInternal(model,  parent=QtCore.QModelIndex(),  prefix=''):
            for column in xrange(model.columnCount(parent)):
                for row in xrange(model.rowCount(parent)):
                    index = model.index(row, column,  parent)
                    if index.isValid():
                        prefix += index.internalPointer().name() + '_'
                        isExpanded = self.isExpanded(index)
                        self.expandedItemsState[prefix] = isExpanded
                        if isExpanded:
                            saveStateInternal(model,  index, prefix)
        self.expandedItemsState = {}
        if self.model():
            if hasattr(self.model(), '_items'):
                if self.model()._items:
                    saveStateInternal(self.model())
            else:
                saveStateInternal(self.model())

    def restoreExpandedState(self):
        def restoreStateInternal(model,  parent=QtCore.QModelIndex(),  prefix=''):
            for column in xrange(model.columnCount(parent)):
                for row in xrange(model.rowCount(parent)):
                    index = model.index(row, column,  parent)
                    if index.isValid():
                        prefix += index.internalPointer().name() + '_'
                        isExpanded = self.expandedItemsState.get(prefix,  False)
                        if isExpanded:
                            self.setExpanded(index, isExpanded)
                            restoreStateInternal(model,  index, prefix)
        if self.model():
            if hasattr(self.model(), '_items'):
                if self.model()._items:
                    restoreStateInternal(self.model())
            else:
                restoreStateInternal(self.model())
        self.expandedItemsState.clear()

    def reset(self):
        currentIndex = self.currentIndex()
        self.saveExpandedState()
        if currentIndex.isValid():
            if currentIndex.parent().internalPointer():
                self.model().emitDataChanged(currentIndex.parent().internalPointer(), currentIndex.row())
        CTreeView.reset(self)
        self.restoreExpandedState()
        if currentIndex.isValid():
            self.setCurrentIndex(currentIndex)
            self.scrollTo(currentIndex)
            pass

    def popupMenu(self):
        if self._popupMenu is None:
            self.createPopupMenu()
        return self._popupMenu

    def addPopupAction(self, action):
        self.popupMenu().addAction(action)

    def initPopupAction(self, act, objectName, actName, slot):
        act = QtGui.QAction(actName, self)
        act.setObjectName(objectName)
        self.connect(act, QtCore.SIGNAL('triggered()'), slot)
        self.addPopupAction(act)
        return act

class CRCConditionsTreeView(CRCTreeView):
    def __init__(self, parent):
        CRCTreeView.__init__(self, parent)
        self.header().close()
        self._actAddCond = None
        self._actEditCond = None
        self._actDeleteCond = None
        self.addPopupAddCond()
        self.addPopupEditCond()
        self.addPopupAddCondAnd()
        self.addPopupAddCondOr()
        self.addPopupChangeCondAnd()
        self.addPopupChangeCondOr()
        self.addPopupDeleteCond()

    def addPopupAddCond(self):
        self._actAddCond = QtGui.QAction(u'Добавить условие', self)
        self._actAddCond.setObjectName('actAddCond')
        self.connect(self._actAddCond, QtCore.SIGNAL('triggered()'), self.actAddCond_triggered)
        self.addPopupAction(self._actAddCond)

    def addPopupAddCondAnd(self):
        self._actAddCondAnd = QtGui.QAction(u'Добавить условие И', self)
        self._actAddCondAnd.setObjectName('actAddCondAnd')
        self.connect(self._actAddCondAnd, QtCore.SIGNAL('triggered()'), self.actAddCondAnd_triggered)
        self.addPopupAction(self._actAddCondAnd)

    def addPopupAddCondOr(self):
        self._actAddCondOr = QtGui.QAction(u'Добавить условие ИЛИ', self)
        self._actAddCondOr.setObjectName('actAddCondOr')
        self.connect(self._actAddCondOr, QtCore.SIGNAL('triggered()'), self.actAddCondOr_triggered)
        self.addPopupAction(self._actAddCondOr)

    def addPopupChangeCondAnd(self):
        self._actChangeCondAnd = QtGui.QAction(u'Изменить И на ИЛИ', self)
        self._actChangeCondAnd.setObjectName('actChangeCondAnd')
        self.connect(self._actChangeCondAnd, QtCore.SIGNAL('triggered()'), self.actChangeCondAnd_triggered)
        self.addPopupAction(self._actChangeCondAnd)

    def addPopupChangeCondOr(self):
        self._actChangeCondOr = QtGui.QAction(u'Изменить ИЛИ на И', self)
        self._actChangeCondOr.setObjectName('actChangeCondOr')
        self.connect(self._actChangeCondOr, QtCore.SIGNAL('triggered()'), self.actChangeCondOr_triggered)
        self.addPopupAction(self._actChangeCondOr)

    def addPopupEditCond(self):
        self._actEditCond = QtGui.QAction(u'Изменить условие', self)
        self._actEditCond.setObjectName('actEditCond')
        self.connect(self._actEditCond, QtCore.SIGNAL('triggered()'), self.actEditCond_triggered)
        self.addPopupAction(self._actEditCond)

    def addPopupDeleteCond(self):
        self._actDeleteCond = QtGui.QAction(u'Удалить условие', self)
        self._actDeleteCond.setObjectName('actDeleteCond')
        self.connect(self._actDeleteCond, QtCore.SIGNAL('triggered()'), self.actDeleteCond_triggered)
        self.addPopupAction(self._actDeleteCond)

    def popupMenuSetActionsDisable(self):
        for action in self.popupMenu().actions():
            action.setEnabled(False)

    def popupMenuAboutToShow(self):
        self.popupMenu().clear()
        if not self.currentIndex().isValid():
            return
        item = self.currentIndex().internalPointer()
        data = self.model()._items.get(item.id(), {})
        conditionType_id = data.get('conditionType_id', None)
        if conditionType_id == 1:
            self.addPopupAction(self._actAddCondOr)
            self.addPopupAction(self._actChangeCondAnd)
        elif conditionType_id == 2:
            self.addPopupAction(self._actAddCondAnd)
            self.addPopupAction(self._actChangeCondOr)
        else:
            self.addPopupAction(self._actEditCond)
        if self.currentIndex().parent():
            self.addPopupAction(self._actDeleteCond)
        self.addPopupAction(self._actAddCond)



    def conditionDialog(self, id=None):
        dialog = self.model().getItemEditor()
        groupId = None
        if self.currentIndex().isValid():
            groupId = self.currentIndex().internalPointer().id()
        dialog.setGroupId(groupId)
        if id:
            dialog.load(id)
        dialog.exec_()
        self.reset()

    def actAddCond_triggered(self):
        self.conditionDialog()

    def actEditCond_triggered(self):
        self.conditionDialog(self.currentIndex().internalPointer().id())
        pass

    def actAddCondAnd_triggered(self):
        self.model().addCondAnd(self.currentIndex())
        self.reset()

    def actAddCondOr_triggered(self):
        self.model().addCondOr(self.currentIndex())
        self.reset()

    def actChangeCondAnd_triggered(self):
        self.model().changeCondAnd(self.currentIndex())
        self.reset()

    def actChangeCondOr_triggered(self):
        self.model().changeCondOr(self.currentIndex())
        self.reset()

    def actDeleteCond_triggered(self):
        parentIndex = self.currentIndex().parent()
        self.model().markItemToDelete(self.currentIndex(), True)
        self.setCurrentIndex(parentIndex)
        self.reset()