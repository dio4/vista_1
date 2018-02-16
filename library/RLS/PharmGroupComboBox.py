# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from PyQt4.QtCore import Qt

from library.TreeModel import CTreeItemWithId, CTreeModel
from library.Utils import forceInt, forceString


class CPharmGroupTreeItem(CTreeItemWithId):
    def __init__(self, parent, id, name):
        CTreeItemWithId.__init__(self, parent, name, id)

    def loadChildren(self):
        result = []
        db = QtGui.qApp.db
        table = db.table('rls.rlsPharmGroup')
        cond = [table['group_id'].eq(self._id)]
        query = db.query(db.selectStmt(table, 'id, name', where=cond, order='name'))
        while query.next():
            record = query.record()
            id = forceInt(record.value('id'))
            name = forceString(record.value('name'))
            result.append(CPharmGroupTreeItem(self, id, name))
        return result


class CPharmGroupRootTreeItem(CPharmGroupTreeItem):
    def __init__(self, id=None):
        CPharmGroupTreeItem.__init__(self, None, '-', id)
        self.setId(id)

    def setId(self, id=None):
        if self._id != id:
            self._id = id
            self._items = None
            if self._id:
                self._name = forceString(QtGui.qApp.db.translate('rls.rlsPharmGroup', 'id', self._id, 'name'))
            else:
                self._name = u'-'


class CPharmGroupModel(CTreeModel):
    def __init__(self, id, parent=None):
        CTreeModel.__init__(self, parent, CPharmGroupRootTreeItem(id))

    def setId(self, id=None):
        self.getRootItem().setId(id)
        self.reset()

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(u'АТХ')
        return QtCore.QVariant()


class CPharmGroupPopupView(QtGui.QTreeView):
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


class CPharmGroupComboBox(QtGui.QComboBox):
    def __init__(self, parent):
        QtGui.QComboBox.__init__(self, parent)
        self.SizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.setModelColumn(0)
        self._model = CPharmGroupModel(None, self)
        self.setModel(self._model)
        self._popupView = CPharmGroupPopupView(self)
        self._popupView.setObjectName('popupView')
        self._popupView.setModel(self._model)
        self.setView(self._popupView)
        self._popupView.installEventFilter(self)
        self._popupView.viewport().installEventFilter(self)
        QtCore.QObject.connect(self._popupView, QtCore.SIGNAL('activated(QModelIndex)'), self.on_ItemActivated)
        QtCore.QObject.connect(self._popupView, QtCore.SIGNAL('entered(QModelIndex)'), self.setCurrentIndex)
        self._expandAll = False

    def setValue(self, id):
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
            if (int(index.flags()) & Qt.ItemIsSelectable) != 0:
                self.hidePopup()
                self.emit(QtCore.SIGNAL('itemSelected(QModelIndex)'), index)
            else:
                self._popupView.setExpanded(index, not self._popupView.isExpanded(index))

    def showPopup(self):
        self._popupView.setRealRootIndex(QtCore.QModelIndex())
        if self._expandAll:
            self._popupView.expandAll()
        else:
            rootIndex = self._model.index(0, 0)
            self._popupView.setExpanded(rootIndex, True)
        QtGui.QComboBox.showPopup(self)

    def setCurrentIndex(self, index):
        self.setRootModelIndex(index.parent())
        QtGui.QComboBox.setCurrentIndex(self, index.row())

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress:  # and obj == self._popupView :
            if event.key() in [Qt.Key_Enter, Qt.Key_Return, Qt.Key_Select]:
                index = self._popupView.currentIndex()
                if index.isValid() and (int(index.flags()) & Qt.ItemIsSelectable) != 0:
                    self.hidePopup()
                    self.setCurrentIndex(index)
                    self.emit(QtCore.SIGNAL('itemSelected(QModelIndex)'), index)
                return True
            return False
        if event.type() == QtCore.QEvent.MouseButtonRelease and obj == self._popupView.viewport():
            self._popupView.mouseReleaseEvent(event)  # i1883.c12401 - нужна реакция на mouseRelease от QTreeView
            return True
        return False
