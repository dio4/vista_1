#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.DialogBase import CDialogBase
from library.TableModel import CTableModel
from library.TreeModel  import CTreeModel, CTreeItemWithId
from library.Utils      import forceInt, forceRef, forceString, toVariant

from Ui_BlankItemsListDialog import Ui_BlankItemsListDialog

class CBlanksItemsListDialog(CDialogBase, Ui_BlankItemsListDialog):
    def __init__(self, parent, cols, tableName, tableName2, order, forSelect=False, filterClass=None, findClass=None):
        CDialogBase.__init__(self, parent)
        self.cols = cols
        self.tableName = tableName
        self.tableName2 = tableName2
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
        self.addModels('Table',CTableModel(self, self.cols, self.tableName2))


    def postSetupUi(self):
        self.setModels(self.treeItemsTempInvalid,  self.modelTree,  self.selectionModelTree)
        self.setModels(self.tblItemsTempInvalid,   self.modelTable, self.selectionModelTable)
        self.treeItemsTempInvalid.header().hide()
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
        table = self.modelTable.table()
        groupId = self.currentGroupId()
        return QtGui.qApp.db.getIdList(table.name(),
                           'id',
                           table['doctype_id'].eq(groupId),
                           self.order)

    def selectItem(self):
        return self.exec_()


    def setCurrentItemId(self, itemId):
        self.tblItemsTempInvalid.setCurrentItemId(itemId)


    def currentItemId(self):
        return self.tblItemsTempInvalid.currentItemId()


    def currentGroupId(self):
        return self.modelTree.itemId(self.treeItemsTempInvalid.currentIndex())


    def findById(self, id):
        index = self.modelTree.findItemId(id)
        parentIndex = self.modelTree.parent(index)
        self.treeItemsTempInvalid.expand(parentIndex)
        self.treeItemsTempInvalid.setCurrentIndex(parentIndex)
        self.renewListAndSetTo(id)


    def renewListAndSetTo(self, itemId=None):
        if not itemId:
            itemId = self.tblItemsTempInvalid.currentItemId()
        idList = self.select(self.props)
        self.tblItemsTempInvalid.setIdList(idList, itemId)
        groupId = self.currentGroupId()


    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelTree_currentChanged(self, current, previous):
        self.renewListAndSetTo(None)


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblItemsTempInvalid_doubleClicked(self, index):
        self.on_btnEdit_clicked()


    @QtCore.pyqtSlot()
    def on_btnNew_clicked(self):
        dialog = self.getItemEditor()
        dialog.setGroupId(self.currentGroupId())
        if dialog.exec_() :
            itemId = dialog.itemId()
            self.renewListAndSetTo(itemId)


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


class CBlankTreeItem(CTreeItemWithId):
    def __init__(self, parent, id, code, name):
        CTreeItemWithId.__init__(self, parent, name, id)
        self._code = code
        self._items = []


    def flags(self):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


    def data(self, column):
        if column == 0 :
            s = self._name
            return toVariant(s)
        else:
            return QtCore.QVariant()


    def sortItems(self):
        pass


    def sortKey(self):
        return (2, self._code, self._name, self._id)


class CBlankTreeItems(CTreeItemWithId):
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
            id   = forceRef(record.value('id'))
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