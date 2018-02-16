# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from library.TreeModel import *
from library.crbcombobox import *
from library.InDocTable import CInDocTableCol
from library.Utils import *


class CRBTreeItem(CTreeItemWithId):
    def __init__(self, rootItem, parent, id, name):
        CTreeItemWithId.__init__(self, parent, name, id)
        self.rootItem = rootItem


    def loadChildren(self):
        result = []
        db = QtGui.qApp.db
        table = self.rootItem.table
        rootItem = self.rootItem
        cond = [table[rootItem.groupField].eq(self._id)]
        if rootItem.filter:
            cond.append(rootItem.filter)
        order = rootItem.order if rootItem.order else rootItem.nameField
        query = db.query(db.selectStmt(table, ['id', rootItem.nameField], where=cond, order=order))
        while query.next():
            record = query.record()
            id   = forceInt(record.value(0))
            name = forceString(record.value(1))
            result.append(CRBTreeItem(rootItem, self, id, name))
        return result


class CRBRootTreeItem(CRBTreeItem):
    nameField = 'name'
    groupField = 'group_id'

    def __init__(self, tableName, filter, order, id):
        CRBTreeItem.__init__(self, self, None, '-', id)
        db = QtGui.qApp.db
        self.table  = db.table(tableName)
        self.filter = filter
        self.order = order
        self.setId(id)

    def setId(self, id=None):
        if self._id != id:
            self._id = id
            self._items = None
            if self._id:
                self._name = forceString(QtGui.qApp.db.translate(self.table, 'id', self._id, 'name'))
            else:
                self._name = u'-'


    def isObsolete(self):
        return False



class CRBRootTreeItemCache(object):
    _mapTableToData = {}

    @classmethod
    def getData(cls, tableName, filter='', order=None, rootId=None):
        key = '|'.join([unicode(tableName), filter, unicode(order), unicode(rootId)])
        result = cls._mapTableToData.get(key, None)
        if result is None or result.isObsolete():
            result = CRBRootTreeItem(tableName, filter, order, rootId)
            cls._mapTableToData[key] = result
        return result


    @classmethod
    def reset(cls):
        cls._mapTableToData.clear()



class CRBTreeModel(CTreeModel):
    def __init__(self, id, parent=None):
        CTreeModel.__init__(self, parent, None)
        self.resetRequired = False


    def setTable(self, tableName, filter='', order=None, rootId=None, showRoot=True):
        rootItem = self._rootItem
        self._rootItem = CRBRootTreeItemCache.getData(tableName, filter, order, rootId)
        if rootItem and rootItem.isLoaded() or self.resetRequired:
            self.reset()
            self.resetRequired = False


    def setId(self, id=None):
        self.getRootItem().setId(id)
        self.reset()


class CRBTreePopupView(QtGui.QTreeView):
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


class CRBTreeComboBox(QtGui.QComboBox):
    def __init__(self, parent):
        QtGui.QComboBox.__init__(self, parent)
        self.SizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.setModelColumn(0)
#        self.__searchString = ''
        self._model = CRBTreeModel(None, self)
        self.setModel(self._model)
        self._popupView = CRBTreePopupView(self)
        self._popupView.setObjectName('popupView')
        self._popupView.setModel(self._model)
        self.setView(self._popupView)
        self._popupView.installEventFilter(self)
        self._popupView.viewport().installEventFilter(self)
        QtCore.QObject.connect(self._popupView, QtCore.SIGNAL('activated(QModelIndex)'), self.on_ItemActivated)
        QtCore.QObject.connect(self._popupView, QtCore.SIGNAL('entered(QModelIndex)'), self.setCurrentIndex)
        self._expandAll = False


    def setTable(self, tableName, filter='', order=None, rootId=None, showRoot=True):
        self._tableName = tableName
        self._rootId    = rootId
        self._showRoot  = showRoot
        self._filier    = filter
        self._order     = order
        self._model.setTable(tableName, filter, order, rootId, showRoot)


    def setFilter(self, filter=''):
        self._filier = filter
        self._model.setTable(self._tableName, self._filter, self._order, self._rootId, self._showRoot)


    def setRoot(self, rootId):
        self._rootId = rootId
        self._model.setTable(self._tableName, self._addNone, filter, self._order, self._rootId, self._showRoot)


    def setValue(self, id):
#        id = None
        index = self._model.findItemId(id)
        if index:
            self.setCurrentIndex(index)


    def value(self):
        modelIndex = self._model.index(self.currentIndex(), 0, self.rootModelIndex())
        if modelIndex.isValid():
            return self._model.itemId(modelIndex)
        return None


    def on_ItemActivated(self, index):
        if index.isValid():
            if (int(index.flags()) & Qt.ItemIsSelectable) != 0 :
                self.hidePopup()
                self.emit(QtCore.SIGNAL('itemSelected(QModelIndex)'), index)
            else:
                self._popupView.setExpanded(index, not self._popupView.isExpanded(index))


    def showPopup(self):
#        self.__searchString = ''
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
        if event.type() == QEvent.KeyPress: # and obj == self._popupView :
            if event.key() in [ Qt.Key_Enter, Qt.Key_Return, Qt.Key_Select ] :
                index = self._popupView.currentIndex()
                if index.isValid() and (int(index.flags()) & Qt.ItemIsSelectable) != 0 :
                    self.hidePopup()
                    self.setCurrentIndex(index)
                    self.emit(QtCore.SIGNAL('itemSelected(QModelIndex)'), index)
                return True
            return False
        if event.type() == QEvent.MouseButtonRelease and obj == self._popupView.viewport():
            self._popupView.mouseReleaseEvent(event)  # i1883.c12401 - нужна реакция на mouseRelease от QTreeView
            return True
        return False


class CRBTreeInDocTableCol(CInDocTableCol):
    def __init__(self, title, fieldName, width, tableName, **params):
        CInDocTableCol.__init__(self, title, fieldName, width, **params)
        self.tableName  = tableName
        self.filter     = params.get('filter', '')
        self.order      = params.get('order', '')
        self.rootId     = params.get('rootId', None)
        self.showRoot   = params.get('showRoot', True)

#        self.addNone    = params.get('addNone', True)
        self.showFields = params.get('showFields', CRBComboBox.showName)
        self.prefferedWidth = params.get('prefferedWidth', None)


    def toString(self, val, record):
        cache = CRBModelDataCache.getData(self.tableName, True)
        text = cache.getStringById(forceInt(val), self.showFields)
        return toVariant(text)

    def toStatusTip(self, val, record):
        cache = CRBModelDataCache.getData(self.tableName, True)
        text = cache.getStringById(forceInt(val), CRBComboBox.showName)
        return toVariant(text)


    def createEditor(self, parent):
        editor = CRBTreeComboBox(parent)
        editor.setTable(self.tableName, filter=self.filter, order=self.order, rootId=self.rootId, showRoot=self.showRoot)
#        editor.setShowFields(self.showFields)
#        editor.setPrefferedWidth(self.prefferedWidth)
        return editor


    def setEditorData(self, editor, value, record):
        editor.setValue(forceInt(value))


    def getEditorData(self, editor):
        return toVariant(editor.value())
