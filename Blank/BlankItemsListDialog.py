#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Ui_BlankItemsListDialog import Ui_BlankItemsListDialog
from library.DialogBase import CDialogBase
from library.TableModel import CTableModel
from library.TreeModel import CTreeModel, CTreeItemWithId
from library.Utils import forceInt, forceRef, forceString, toVariant


class CBlankTreeItem(CTreeItemWithId):
    def __init__(self, parent, id, code, name):
        CTreeItemWithId.__init__(self, parent, name, id)
        self._code = code
        self._items = []

    def flags(self):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, column):
        if column == 0:
            s = self._name
            return toVariant(s)
        else:
            return QtCore.QVariant()

    def sortItems(self):
        pass

    def sortKey(self):
        return (2, self._code, self._name, self._id)


class CBlankTreeItems(CTreeItemWithId):
    def __init__(self, parent, name, id=None):
        CTreeItemWithId.__init__(self, parent, name, id)
        self._items = []

    def flags(self):
        return QtCore.Qt.ItemIsEnabled

    def sortItems(self):
        self._items.sort(key=lambda item: item.sortKey())
        for item in self._items:
            item.sortItems()

    def sortKey(self):
        return (1, self._name)


class CBlankRootTreeItem(CTreeItemWithId):
    def __init__(self, filter=None):
        if not filter:
            filter = {}
        CTreeItemWithId.__init__(self, None, '-', None)
        self._classesVisible = False

    def loadChildren(self):
        mapTypeToTreeItem = {}
        result = []
        tempInvalidTypeList = [u'ВУТ', u'Инвалидность', u'Ограничение жизнедеятельности']

        def getTempInvalidTypeTreeItem(type):
            if type in mapTypeToTreeItem:
                item = mapTypeToTreeItem[type]
            else:
                tempInvalidType = tempInvalidTypeList[type]
                parentItem = self
                item = CBlankTreeItems(parentItem, tempInvalidType)
                result.append(item)
                mapTypeToTreeItem[type] = item
            return item

        db = QtGui.qApp.db
        tableTempInvalid = db.table('rbTempInvalidDocument')
        table = tableTempInvalid
        cond = []
        query = db.query(db.selectStmt(table, '*', where=cond, order=tableTempInvalid['type'].name()))
        while query.next():
            record = query.record()
            id = forceRef(record.value('id'))
            code = forceString(record.value('code'))
            name = forceString(record.value('name'))
            type = forceInt(record.value('type'))
            tempInvalidTypeItem = getTempInvalidTypeTreeItem(type)
            tempInvalidTypeItem._items.append(CBlankTreeItem(tempInvalidTypeItem, id, code, name))

        result.sort(key=lambda item: item._name)
        for item in result:
            item.sortItems()
        return result


class CBlankModel(CTreeModel):
    def __init__(self, parent=None, filter=None):
        if not filter:
            filter = {}
        CTreeModel.__init__(self, parent, CBlankRootTreeItem(filter))


class CBlanksItemsListDialog(CDialogBase, Ui_BlankItemsListDialog):
    def __init__(self, parent, cols, tableName, tableName2, tableName3, tableName4, order, forSelect=False,
                 filterClass=None, findClass=None):
        CDialogBase.__init__(self, parent)
        self.cols = cols
        self.tableNameTI = tableName
        self.tableNameTI2 = tableName2
        self.tableNameAction = tableName3
        self.tableNameAction2 = tableName4
        self.order = order
        self.forSelect = forSelect
        self.filterClass = filterClass
        self.findClass = findClass
        self.props = {}
        self.preSetupUi()
        self.setupUi(self)
        self.postSetupUi()
        self.btnNew.setShortcut(QtCore.Qt.Key_F9)
        self.btnEdit.setShortcut(QtCore.Qt.Key_F4)

    def preSetupUi(self):
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.addModels('Tree', CBlankModel(self))
        self.addModels('Table', CTableModel(self, self.cols, self.tableNameTI2))
        self.addModels('Tree2', CActionBlankModel(self))
        self.addModels('Table2', CTableModel(self, self.cols, self.tableNameAction2))

    def postSetupUi(self):
        self.setModels(self.treeItemsTempInvalid, self.modelTree, self.selectionModelTree)
        self.setModels(self.tblItemsTempInvalid, self.modelTable, self.selectionModelTable)
        self.setModels(self.treeItemsOthers, self.modelTree2, self.selectionModelTree2)
        self.setModels(self.tblItemsOthers, self.modelTable2, self.selectionModelTable2)
        self.treeItemsTempInvalid.header().hide()
        self.treeItemsOthers.header().hide()
        idList = self.select(self.props)
        self.modelTable.setIdList(idList)
        self.tblItemsTempInvalid.selectRow(0)
        self.btnSelect.setEnabled(self.forSelect)
        self.btnSelect.setVisible(self.forSelect)
        self.btnSelect.setDefault(self.forSelect)
        self.btnFilter.setEnabled(bool(self.filterClass))
        self.btnFilter.setVisible(bool(self.filterClass))
        self.btnFind.setEnabled(bool(self.findClass))
        self.btnFind.setVisible(bool(self.findClass))
        self.btnEdit.setDefault(not self.forSelect)
        self.tblItemsTempInvalid.setFocus(QtCore.Qt.OtherFocusReason)

    def select(self, props):
        db = QtGui.qApp.db
        groupId = self.currentGroupId()
        widgetIndex = self.tabWidget.currentIndex()
        if widgetIndex == 0:
            table = self.modelTable.table()
            return db.getIdList(table.name(),
                                'id',
                                table['doctype_id'].eq(groupId),
                                self.order)
        else:
            table = self.modelTable2.table()
            groupIdList = db.getDescendants('ActionType', 'group_id', groupId)
            if not groupIdList:
                return None
            return db.getIdList(table.name(),
                                'id',
                                table['doctype_id'].inlist(groupIdList),
                                self.order)

    def selectItem(self):
        return self.exec_()

    def setCurrentItemId(self, itemId):
        widgetIndex = self.tabWidget.currentIndex()
        if widgetIndex == 0:
            self.tblItemsTempInvalid.setCurrentItemId(itemId)
        else:
            self.tblItemsOthers.setCurrentItemId(itemId)

    def currentItemId(self):
        widgetIndex = self.tabWidget.currentIndex()
        if widgetIndex == 0:
            return self.tblItemsTempInvalid.currentItemId()
        else:
            return self.tblItemsOthers.currentItemId()

    def currentGroupId(self):
        widgetIndex = self.tabWidget.currentIndex()
        if widgetIndex == 0:
            return self.modelTree.itemId(self.treeItemsTempInvalid.currentIndex())
        else:
            return self.modelTree2.itemId(self.treeItemsOthers.currentIndex())

    def findById(self, id):
        widgetIndex = self.tabWidget.currentIndex()
        if widgetIndex == 0:
            index = self.modelTree.findItemId(id)
            parentIndex = self.modelTree.parent(index)
            self.treeItemsTempInvalid.expand(parentIndex)
            self.treeItemsTempInvalid.setCurrentIndex(parentIndex)
        else:
            index = self.modelTree2.findItemId(id)
            parentIndex = self.modelTree2.parent(index)
            self.treeItemsOthers.expand(parentIndex)
            self.treeItemsOthers.setCurrentIndex(parentIndex)
        self.renewListAndSetTo(id)

    def renewListAndSetTo(self, itemId=None):
        widgetIndex = self.tabWidget.currentIndex()
        idList = self.select(self.props)
        if not itemId:
            if widgetIndex == 0:
                itemId = self.tblItemsTempInvalid.currentItemId()
            else:
                itemId = self.tblItemsOthers.currentItemId()
        if widgetIndex == 0:
            self.tblItemsTempInvalid.setIdList(idList, itemId)
        else:
            self.tblItemsOthers.setIdList(idList, itemId)
        groupId = self.currentGroupId()

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelTree2_currentChanged(self, current, previous):
        self.renewListAndSetTo(None)

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelTree_currentChanged(self, current, previous):
        self.renewListAndSetTo(None)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblItemsOthers_doubleClicked(self, index):
        self.on_btnEdit_clicked()

    @QtCore.pyqtSlot()
    def on_btnNew_clicked(self):
        if self.currentGroupId():
            dialog = self.getItemEditor()
            dialog.setGroupId(self.currentGroupId())
            if dialog.exec_():
                itemId = dialog.itemId()
                self.renewListAndSetTo(itemId)
        else:
            QtGui.QMessageBox.critical(
                self,
                u"Внимание!",
                u"Для создания бланка необходимо выбрать группу.",
                QtGui.QMessageBox.Ok,
                QtGui.QMessageBox.Ok
            )

    @QtCore.pyqtSlot()
    def on_btnEdit_clicked(self):
        itemId = self.currentItemId()
        if itemId:
            dialog = self.getItemEditor()
            dialog.load(itemId)
            if dialog.exec_():
                itemId = dialog.itemId()
                self.renewListAndSetTo(itemId)
        else:
            self.on_btnNew_clicked()


class CActionBlankTreeItem(CTreeItemWithId):
    def __init__(self, parent, id, code, name):
        CTreeItemWithId.__init__(self, parent, name, id)
        self._code = code
        self._items = []

    def flags(self):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, column):
        if column == 0:
            s = self._name
            return toVariant(s)
        else:
            return QtCore.QVariant()

    def sortItems(self):
        pass

    def sortKey(self):
        return (2, self._code, self._name, self._id)


class CActionBlankTreeItems(CTreeItemWithId):
    def __init__(self, parent, name):
        CTreeItemWithId.__init__(self, parent, name, None)
        self._items = []

    def flags(self):
        return QtCore.Qt.ItemIsEnabled

    def sortItems(self):
        self._items.sort(key=lambda item: item.sortKey())
        for item in self._items:
            item.sortItems()

    def sortKey(self):
        return (1, self._name)


class CActionBlankRootTreeItem(CTreeItemWithId):
    def __init__(self, filter=None):
        if not filter:
            filter = {}
        CTreeItemWithId.__init__(self, None, '-', None)
        self._classesVisible = False

    def loadChildren(self):
        mapTypeToTreeItem = {}
        result = []

        def getTempInvalidTypeTreeItem(groupId):
            if groupId in mapTypeToTreeItem:
                item = mapTypeToTreeItem[groupId]
            else:
                db = QtGui.qApp.db
                tableActionType = db.table('ActionType')
                record = QtGui.qApp.db.getRecordEx(tableActionType,
                                                   'ActionType.id, ActionType.name, ActionType.group_id',
                                                   [tableActionType['id'].eq(groupId),
                                                    tableActionType['deleted'].eq(0)])
                if record:
                    actionTypeId = forceRef(record.value('id'))
                    name = forceString(record.value('name'))
                    groupId = forceRef(record.value('group_id'))
                    if groupId:
                        parentItem = getTempInvalidTypeTreeItem(groupId)
                        item = CBlankTreeItems(parentItem, name)
                        parentItem._items.append(item)
                    else:
                        parentItem = self
                        item = CBlankTreeItems(parentItem, name, actionTypeId)
                        result.append(item)
                mapTypeToTreeItem[groupId] = item
            return item

        db = QtGui.qApp.db
        tableActionType = db.table('ActionType')
        tableActionPropertyType = db.table('ActionPropertyType')
        table = tableActionType.innerJoin(tableActionPropertyType,
                                          tableActionPropertyType['actionType_id'].eq(tableActionType['id']))
        cond = [tableActionPropertyType['deleted'].eq(0),
                tableActionType['deleted'].eq(0),
                tableActionPropertyType['typeName'].like('BlankSerial')]
        query = db.query(db.selectStmt(table, '*', where=cond, order=tableActionType['name'].name()))
        while query.next():
            record = query.record()
            id = forceRef(record.value('id'))
            code = forceString(record.value('code'))
            name = forceString(record.value('name'))
            groupId = forceInt(record.value('group_id'))
            tempInvalidTypeItem = getTempInvalidTypeTreeItem(groupId)
            tempInvalidTypeItem._items.append(CActionBlankTreeItem(tempInvalidTypeItem, id, code, name))

        result.sort(key=lambda item: item._name)
        for item in result:
            item.sortItems()
        return result


class CActionBlankModel(CTreeModel):
    def __init__(self, parent=None, filter=None):
        if not filter:
            filter = {}
        CTreeModel.__init__(self, parent, CActionBlankRootTreeItem(filter))
