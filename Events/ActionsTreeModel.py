# coding=utf-8
from PyQt4 import QtCore, QtGui

from Events.Action import ActionClass, CAction, CActionType
from Events.ActionsModel import fillActionRecord, getActionDefaultAmountEx, getActionDefaultContractId
from library.ICDCodeEdit import CICDCodeEditEx
from library.TreeModel import CTreeItem, CTreeModel
from library.Utils import forceDouble, forceString, forceInt


class Columns:
    NAME = 0
    AMOUNT = 1
    MKB = 2


class CActionAmountDelegate(QtGui.QStyledItemDelegate):
    _editor = None

    def createEditor(self, parent, option, idx):
        self._editor = QtGui.QDoubleSpinBox(parent)
        self._editor.editingFinished.connect(self.commitAndCloseEditor)
        return self._editor

    def commitAndCloseEditor(self):
        self.commitData.emit(self._editor)
        self.closeEditor.emit(self._editor, QtGui.QAbstractItemDelegate.NoHint)

    def setEditorData(self, editor, idx):
        editor.setValue(forceDouble(idx.internalPointer().action().getRecord().value('amount')))

    def setModelData(self, editor, mdl, idx):
        idx.internalPointer().action().getRecord().setValue('amount', editor.value())
        mdl.dataChanged.emit(idx, idx)
        mdl.amountChanged.emit(idx.row())


class CActionMKBDelegate(QtGui.QStyledItemDelegate):
    _editor = None

    def createEditor(self, parent, option, idx):
        self._editor = CICDCodeEditEx(parent)
        self._editor.editingFinished.connect(self.commitAndCloseEditor)
        return self._editor

    def commitAndCloseEditor(self):
        self.commitData.emit(self._editor)
        self.closeEditor.emit(self._editor, QtGui.QAbstractItemDelegate.NoHint)

    def setEditorData(self, editor, idx):
        editor.setText(forceString(idx.internalPointer().action().getRecord().value('MKB')))

    def setModelData(self, editor, mdl, idx):
        idx.internalPointer().action().getRecord().setValue('MKB', editor.text())
        mdl.dataChanged.emit(idx, idx)


class CActionItem(CTreeItem):
    def __init__(self, model, parent, action):
        self._model = model
        self._action = action  # type: CAction
        self._amount = 1
        self._mkb = ''
        CTreeItem.__init__(self, parent, action.getType().name)

    def action(self):
        return self._action

    def columnCount(self):
        return 3

    def getClass(self):
        return self._action.getType().class_

    def loadChildren(self):
        return []

    def data(self, column):
        if column == Columns.NAME:
            return self._action.getType().name
        elif column == Columns.AMOUNT:
            return forceString(self._action.getRecord().value('amount'))
        elif column == Columns.MKB:
            return forceString(self._action.getRecord().value('MKB')) or ''
        return None


class CActionsClassItem(CTreeItem):
    def __init__(self, model, parent, cls, name):
        self._model = model  # type: CActionsTreeModel
        self._cls = cls
        CTreeItem.__init__(self, parent, name)

    def loadChildren(self):
        return [CActionItem(self._model, self, action) for action in self._model.groups()[self._cls]]

    def getClass(self):
        return self._cls


class CActionsRootItem(CTreeItem):
    def __init__(self, model):
        self._model = model  # type: CActionsModel
        CTreeItem.__init__(self, None, u'')

    def loadChildren(self):
        return [CActionsClassItem(self._model, self, idx, itemName)
                for idx, itemName in enumerate(ActionClass.nameList)]


class CActionsTreeModel(CTreeModel):
    amountChanged = QtCore.pyqtSlot(int)

    def __init__(self, parent=None):
        self._root = CActionsRootItem(self)
        self._parent = parent
        CTreeModel.__init__(self, parent, self._root)
        self._items = dict()
        self.setRootItemVisible(False)
        self.notDeletedActionTypes = {}
        self.eventEditor = None
        self.init()

    def init(self):
        self._items = dict((idx, []) for idx in ActionClass.All)
        self._items.update({'deleted': []})

    def groups(self):
        return self._items

    def items(self):
        return ((action.getRecord(), action) for action in self.actions())

    def reloadTree(self):
        for cls in self.getRootItem().items():
            cls.update()
        self.reset()
        self.modelReset.emit()
        self._parent.expandAll()

    def addItems(self, items):
        self._parent.clearSelection()
        for type_id, action in items:
            action.initPropertyPresetValues()
            amount = forceDouble(action.getRecord().value('amount'))
            fillActionRecord(self, action.getRecord(), type_id, amount)
            self._items[action.getType().class_].append(action)
        for cls in self.getRootItem().items():
            cls.update()
        # sel = self._parent.currentIndex()
        self.reloadTree()
        self.rowsInserted.emit(QtCore.QModelIndex(), 0, 0)
        # self._parent.setCurrentIndex(sel)

    def getDefaultAmountEx(self, actionType, record, action):
        return getActionDefaultAmountEx(self, actionType, record, action)

    def getDefaultContractId(self, actionTypeId, financeId, begDate, endDate, contractId):
        return getActionDefaultContractId(self, actionTypeId, financeId, begDate, endDate, contractId)

    def isLockedOrExposed(self, item):
        record, action = item.action().getRecord(), item.action()
        return forceInt(record.value('payStatus')) != 0 or action and action.isLocked()

    def isDeletable(self, item):
        record, action = item.action().getRecord(), item.action()
        if not action:
            return True
        return not self.isLockedOrExposed(item) and action.isDeletable()

    def deleteAction(self, action):
        if action:
            self._items['deleted'].append(action)
            self._items[action.getType().class_].remove(action)
        self.reloadTree()
        self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())
        self.rowsRemoved.emit(QtCore.QModelIndex(), 0, 0)

    def headerData(self, col, orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            if col == 0:
                return QtCore.QVariant(u'Наименование')
            elif col == 1:
                return QtCore.QVariant(u'Кол-во')
            elif col == 2:
                return QtCore.QVariant(u'МКБ')
        return QtCore.QVariant()

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 3

    def loadEvent(self, event_id):
        db = QtGui.qApp.db
        for rec in db.getRecordList('Action', where='event_id=%d AND deleted=0' % event_id):
            action = CAction(record=rec)
            action_type = action.getType()  # type: CActionType
            self._items[action_type.class_].append(action)

    def actions(self, deleted=False):
        result = []
        for cls in self._items.keys():
            if cls != 'deleted' or deleted:
                result += self._items[cls]
        return result

    def save(self, eventId):
        for action in self._items['deleted']:
            action.getRecord().setValue('deleted', True)
        for action in self.actions(deleted=True):  # type: CAction
            action.save(eventId)

    def flags(self, idx):
        if isinstance(idx.internalPointer(), CActionItem) and idx.column() in (Columns.AMOUNT, Columns.MKB):
            return super(CActionsTreeModel, self).flags(idx) | QtCore.Qt.ItemIsEditable
        elif isinstance(idx.internalPointer(), CActionsClassItem):
            return super(CActionsTreeModel, self).flags(idx) & ~QtCore.Qt.ItemIsSelectable
        return super(CActionsTreeModel, self).flags(idx)

    def isLocked(self, action):
        return True


class CActionsTreeView(QtGui.QTreeView):
    actionSelected = QtCore.pyqtSignal(CAction)
    actionDeselected = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(CActionsTreeView, self).__init__(parent)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenu)
        self.actDelete = QtGui.QAction(u'Удалить', self)
        # self.act
        self._menu = QtGui.QMenu()
        self._menu.addAction(self.actDelete)
        self.actDelete.triggered.connect(self.deleteAction)

        self._amount_delegate = CActionAmountDelegate(self)
        self._mkb_delegate = CActionMKBDelegate(self)
        self.setItemDelegateForColumn(Columns.AMOUNT, self._amount_delegate)
        self.setItemDelegateForColumn(Columns.MKB, self._mkb_delegate)
        QtCore.QObject.connect(self._menu, QtCore.SIGNAL('aboutToShow()'), self.onAboutToShow)

    def onAboutToShow(self):
        items = list(self.getSelectedItems())
        canDeleteRow = any(map(self.model().isDeletable, items)) if items else False
        self.actDelete.setEnabled(canDeleteRow)

    def contextMenu(self, pos):
        idx = self.indexAt(pos)
        if idx.isValid() and isinstance(idx.internalPointer(), CActionItem):
            self._menu.popup(self.viewport().mapToGlobal(pos))

    def deleteAction(self):
        for item in self.getSelectedItems():
            if self.model().isDeletable(item):
                self.model().deleteAction(item.action())
        self.actionDeselected.emit()

    def initHeader(self):
        hdr = self.header()  # type: QtGui.QHeaderView
        hdr.setResizeMode(QtGui.QHeaderView.Fixed)
        hdr.setDefaultSectionSize(100)
        hdr.setResizeMode(0, QtGui.QHeaderView.Stretch)
        hdr.setStretchLastSection(False)

    def getSelectedItems(self):
        return set(index.internalPointer() for index in self.selectedIndexes())

    def selectedRowsCount(self):
        return len(self.getSelectedItems())

    def selectionChanged(self, selected, deselected):
        super(CActionsTreeView, self).selectionChanged(selected, deselected)
        if self.selectedRowsCount() != 1:
            self.actionDeselected.emit()
            return
        item = self.selectedIndexes()[0].internalPointer()
        if isinstance(item, CActionItem):
            self.actionSelected.emit(item.action())
        else:
            self.actionDeselected.emit()

    # def keyPressEvent(self, evt):

