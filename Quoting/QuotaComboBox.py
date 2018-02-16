# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from RefBooks.QuotaType   import CQuotaTypeTreeModel


class CQuotaPopupView(QtGui.QTreeView):
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


    def onExpanded(self, index):
        self.scrollTo(index, QtGui.QAbstractItemView.PositionAtTop)


class CQuotaComboBox(QtGui.QComboBox):
    def __init__(self, parent, emptyRootName=None, purpose=None, filter=None):
        QtGui.QComboBox.__init__(self, parent)
        self.SizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.setModelColumn(0)
#        self.__searchString = ''
        self._model = CQuotaTypeTreeModel(self, 'QuotaType', 'id', 'group_code', 'name', 'class', ['class', 'group_code', 'code', 'name', 'id'])
        self._model.filterClassByExists(True)
        self._model.setLeavesVisible(True)
        self.setModel(self._model)
        self._popupView = CQuotaPopupView(self)
        self._popupView.setObjectName('popupView')
        self._popupView.setModel(self._model)
        self.setView(self._popupView)
        self._popupView.installEventFilter(self)
        self._popupView.viewport().installEventFilter(self)
        QtCore.QObject.connect(self._popupView, QtCore.SIGNAL('activated(QModelIndex)'), self.on_ItemActivated)
        QtCore.QObject.connect(self._popupView, QtCore.SIGNAL('entered(QModelIndex)'), self.setCurrentModelIndex)
        self.connect(self._model,
                     QtCore.SIGNAL('currentChanged(QModelIndex, QModelIndex)'),
                     self.on_selectionModelQuotaType_currentChanged)
        self.setExpandAll(False)


    def setPurpose(self, purpose):
        currValue = self.value()
        self._model.setPurpose(purpose)
        self.setValue(currValue)


    def setValue(self, id):
        index = self._model.findItemId(id)
        if index:
            self.setCurrentModelIndex(index)


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
        def expandUp(index):
            while index.isValid():
                self._popupView.setExpanded(index, True)
                index = index.parent()

        modelIndex = self._model.index(self.currentIndex(), 0, self.rootModelIndex())
        self._popupView.setRealRootIndex(QtCore.QModelIndex())
        if self._expandAll:
            self._popupView.expandAll()
        else:
            if modelIndex.isValid():
                index = modelIndex.parent()
                expandUp(index)
            #index = self._model.findItemId(None)
                if index.isValid():
                    index = index.parent()
                    expandUp(index)
            self._popupView.setExpanded(self._model.index(0,0), True)
        QtGui.QComboBox.showPopup(self)


    def setCurrentModelIndex(self, index):
        self.setRootModelIndex(index.parent())
        QtGui.QComboBox.setCurrentIndex(self, index.row())


    def currentGroupId(self):
        return self._model.itemId(self._model.index(self.currentIndex(), 0, self.rootModelIndex()))


    def currentClass(self):
        return self._model.itemClass(self._model.index(self.currentIndex(), 0, self.rootModelIndex()))


#    def select(self, props=None):
#        db = QtGui.qApp.db
#        table = db.table('QuotaType')
#        cond = []
#        groupId = self.currentGroupId()
#        groupCond = db.translate(table, 'id', groupId, 'code')
#        className = self.currentClass()
#        cond = [table['group_code'].eq(groupCond),
#                table['deleted'].eq(0),
#                table['class'].eq(className)
#               ]
#        return db.getIdList(table.name(),
#                           'id',
#                           cond)


    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelQuotaType_currentChanged(self, current, previous):
        groupId = self.currentGroupId()
        self.modelQuotaType.update()
        self.renewTblQuotingAndSetTo()


    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() in [ QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return, QtCore.Qt.Key_Select ] :
                index = self._popupView.currentIndex()
                if index.isValid() and (int(index.flags()) & QtCore.Qt.ItemIsSelectable) != 0 :
                    self.hidePopup()
                    self.setCurrentModelIndex(index)
                    self.emit(QtCore.SIGNAL('itemSelected(QModelIndex)'), index)
                return True
            return False
        if event.type() == QtCore.QEvent.MouseButtonRelease and obj == self._popupView.viewport():
            self._popupView.mouseReleaseEvent(event)  # i1883.c12401 - нужна реакция на mouseRelease от QTreeView
            return True
        return False
