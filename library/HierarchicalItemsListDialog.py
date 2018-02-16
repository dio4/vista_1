#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Ui_HierarchicalItemsListDialog import Ui_HierarchicalItemsListDialog
#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from library.DialogBase import CDialogBase
from library.TableModel import *
from library.TreeModel import *


class CHierarchicalItemsListDialog(CDialogBase, Ui_HierarchicalItemsListDialog):
    def __init__(self, parent, cols, tableName, order, forSelect=False, filterClass=None, findClass=None, where=''):
        CDialogBase.__init__(self, parent)
        self.cols = cols
        self.tableName = tableName
        self.order = order
        self.forSelect = forSelect
        self.filterClass = filterClass
        self.findClass = findClass
        self.where = where
        self.props = {}
        self.preSetupUi()
        self.setupUi(self)
        self.postSetupUi()
        self.btnNew.setShortcut(Qt.Key_F9)
        self.btnEdit.setShortcut(Qt.Key_F4)

    def preSetupUi(self):
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.addModels('Tree', CDBTreeModel(self, self.tableName, 'id', 'group_id', 'name', self.order))
        self.addModels('Table', CTableModel(self, self.cols, self.tableName))

    def postSetupUi(self):
        self.setModels(self.treeItems,  self.modelTree,  self.selectionModelTree)
        self.setModels(self.tblItems,   self.modelTable, self.selectionModelTable)
        # self.treeItems.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.tblItems.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.treeItems.header().hide()
        idList = self.select(self.props)
        self.modelTable.setIdList(idList)
        self.tblItems.selectRow(0)
        self.btnSelect.setEnabled(self.forSelect)
        self.btnSelect.setVisible(self.forSelect)
        self.btnSelect.setDefault(self.forSelect)
        self.btnFilter.setEnabled(bool(self.filterClass))
        self.btnFilter.setVisible(bool(self.filterClass))
        self.btnFind.setEnabled(bool(self.findClass))
        self.btnFind.setVisible(bool(self.findClass))
        self.btnEdit.setDefault(not self.forSelect)
        self.tblItems.setFocus(Qt.OtherFocusReason)

    def select(self, props):
        table = self.modelTable.table()
        groupId = self.currentGroupId()
        db = QtGui.qApp.db
        where = table['group_id'].eq(groupId)
        if self.where:
            where = db.joinAnd([where, self.where])
        return db.getIdList(table.name(),
                            'id',
                            where,
                            self.order)

    def selectItem(self):
        return self.exec_()

    def setCurrentItemId(self, itemId):
        self.tblItems.setCurrentItemId(itemId)

    def currentItemId(self):
        return self.tblItems.currentItemId()

    def currentGroupId(self):
        return self.modelTree.itemId(self.treeItems.currentIndex())

    def findById(self, id):
        item = self.modelTree.getItemByIdEx(id)
        if not item:
            item = self.modelTree.getItemById(id)
        parentIndex = self.modelTree.parentByItem(item)
        self.treeItems.expand(parentIndex)
        self.treeItems.setCurrentIndex(parentIndex)
        self.renewListAndSetToWithoutUpdate(id)

    def renewListAndSetTo(self, itemId=None):
        self.renewListAndSetToWithoutUpdate(itemId)
        self.modelTree.update()

    def renewListAndSetToWithoutUpdate(self, itemId=None):
        if not itemId:
            itemId = self.tblItems.currentItemId()
        idList = self.select(self.props)
        self.tblItems.setIdList(idList, itemId)

    def saveExpandedState(self):
        def saveStateInternal(model,  parent=QModelIndex(),  prefix=''):
            for column in xrange(model.columnCount(parent)):
                for row in xrange(model.rowCount(parent)):
                    index = model.index(row, column,  parent)
                    if index.isValid():
                        prefix += index.internalPointer().name() + '_'
                        isExpanded = self.treeItems.isExpanded(index)
                        self.expandedItemsState[prefix] = isExpanded
                        if isExpanded:
                            saveStateInternal(model,  index, prefix)
        self.expandedItemsState = {}
        saveStateInternal(self.modelTree)

    def restoreExpandedState(self):
        def restoreStateInternal(model,  parent=QModelIndex(),  prefix=''):
            for column in xrange(model.columnCount(parent)):
                for row in xrange(model.rowCount(parent)):
                    index = model.index(row, column,  parent)
                    if index.isValid():
                        prefix += index.internalPointer().name() + '_'
                        isExpanded = self.expandedItemsState.get(prefix,  False)
                        if isExpanded:
                            self.treeItems.setExpanded(index, isExpanded)
                            restoreStateInternal(model,  index, prefix)
        restoreStateInternal(self.modelTree)
        self.expandedItemsState.clear()

    @QtCore.pyqtSlot(QModelIndex, QModelIndex)
    def on_selectionModelTree_currentChanged(self, current, previous):
        self.renewListAndSetToWithoutUpdate(None)

    @QtCore.pyqtSlot(QModelIndex)
    def on_tblItems_doubleClicked(self, index):
        if self.forSelect:
            self.on_btnSelect_clicked()
        else:
            self.on_btnEdit_clicked()

    @QtCore.pyqtSlot()
    def on_btnFind_clicked(self):
        if self.findClass:
            dialog = self.findClass(self)
            dialog.setProps(self.props)
            if dialog.exec_():
                self.props = dialog.getProps()
                id = dialog.id()
                self.findById(id)

    @QtCore.pyqtSlot()
    def on_btnFilter_clicked(self):
        if self.filterClass:
            dialog = self.filterClass(self)
            dialog.setProps(self.props)
            if dialog.exec_():
                self.props = dialog.props()
                self.renewListAndSetTo(None)

    @QtCore.pyqtSlot()
    def on_btnSelect_clicked(self):
        self.accept()

    @QtCore.pyqtSlot()
    def on_btnNew_clicked(self):
        dialog = self.getItemEditor()
        dialog.setGroupId(self.currentGroupId())
        if dialog.exec_() :
            itemId = dialog.itemId()
            self.modelTree.update()
            self.renewListAndSetTo(itemId)

    @QtCore.pyqtSlot()
    def on_btnEdit_clicked(self):
        itemId = self.currentItemId()
        if itemId:
            dialog = self.getItemEditor()
            dialog.load(itemId)
            if dialog.exec_():
                itemId = dialog.itemId()
                self.modelTree.update()
                self.renewListAndSetTo(itemId)
        else:
            self.on_btnNew_clicked()
