# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

from library.crbcombobox                 import CRBComboBox
from library.HierarchicalItemsListDialog import CHierarchicalItemsListDialog
from library.InDocTable                  import CInDocTableModel, CFloatInDocTableCol
from library.interchange                 import getLineEditValue, setLineEditValue
from library.ItemsListDialog             import CItemEditorBaseDialog
from library.TableModel                  import CTextCol
from library.Utils                       import forceRef, forceString, toVariant

from RefBooks.Tables                     import rbCode, rbName

from Stock.NomenclatureComboBox          import CNomenclatureInDocTableCol

from Ui_RBStockRecipeEditor              import Ui_ItemEditorDialog


class CRBStockRecipeList(CHierarchicalItemsListDialog):
    def __init__(self, parent):
        CHierarchicalItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            ], 'rbStockRecipe', [rbCode, rbName])
        self.setWindowTitleEx(u'Рецепты производства ЛСиИМН')


    def preSetupUi(self):
        CHierarchicalItemsListDialog.preSetupUi(self)
        self.modelTree.setLeavesVisible(True)
        self.modelTree.setOrder('code')
        self.actDuplicate = QtGui.QAction(u'Дублировать', self)
        self.actDuplicate.setObjectName('actDuplicate')
        self.actDelete =    QtGui.QAction(u'Удалить', self)
        self.actDelete.setObjectName('actDelete')


    def postSetupUi(self):
        CHierarchicalItemsListDialog.postSetupUi(self)
        self.tblItems.createPopupMenu([self.actDuplicate, '-', self.actDelete])
        self.connect(self.tblItems.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.popupMenuAboutToShow)


    def getItemEditor(self):
        return CRBStockRecipeEditor(self)


    def popupMenuAboutToShow(self):
        currentItemId = self.currentItemId()
        self.actDuplicate.setEnabled(bool(currentItemId))
        self.actDelete.setEnabled(bool(currentItemId))

    @QtCore.pyqtSlot()
    def on_actDuplicate_triggered(self):
        def duplicateContent(currentId, newId):
            db = QtGui.qApp.db
            table = db.table('rbStockRecipe_Item')
            records = db.getRecordList(table, '*', table['master_id'].eq(currentId))
            for record in records:
                record.setValue('master_id', toVariant(newId))
                record.setNull('id')
                db.insertRecord(table, record)

        def duplicateGroup(currentGroupId, newGroupId):
            db = QtGui.qApp.db
            table = db.table('rbStockRecipe')
            records = db.getRecordList(table, '*', table['group_id'].eq(currentGroupId))
            for record in records:
                currentItemId = record.value('id')
                record.setValue('group_id', toVariant(newGroupId))
                record.setNull('id')
                newItemId = db.insertRecord(table, record)
                duplicateGroup(currentItemId, newItemId)
                duplicateContent(currentItemId, newItemId)

        def duplicateCurrentInternal():
            currentItemId = self.currentItemId()
            if currentItemId :
                db = QtGui.qApp.db
                table = db.table('rbStockRecipe')
                db.transaction()
                try:
                    record = db.getRecord(table, '*', currentItemId)
                    record.setValue('code', toVariant(forceString(record.value('code'))+'_1'))
                    record.setNull('id')
                    newItemId = db.insertRecord(table, record)
                    duplicateGroup(currentItemId, newItemId)
                    duplicateContent(currentItemId, newItemId)
                    db.commit()
                except:
                    db.rollback()
                    QtGui.qApp.logCurrentException()
                    raise
                self.renewListAndSetTo(newItemId)
        QtGui.qApp.call(self, duplicateCurrentInternal)


    @QtCore.pyqtSlot()
    def on_actDelete_triggered(self):
        def deleteCurrentInternal():
            currentItemId = self.currentItemId()
            if currentItemId :
                row = self.tblItems.currentIndex().row()
                db = QtGui.qApp.db
                table = db.table('rbStockRecipe')
                db.deleteRecord(table, table['id'].eq(currentItemId))
                self.renewListAndSetTo()
                self.tblItems.setCurrentRow(row)
        QtGui.qApp.call(self, deleteCurrentInternal)


#
# ##########################################################################
#

class CRBStockRecipeEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rbStockRecipe')
        self.addModels('InItems', CItemsModel(self, False))
        self.addModels('OutItems', CItemsModel(self, True))
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Рецепт производства ЛСиИМН')
        self.prepareTable(self.tblInItems, self.modelInItems)
        self.prepareTable(self.tblOutItems, self.modelOutItems)
        self.setupDirtyCather()
        self.groupId = None


    def prepareTable(self, tblWidget, model):
        tblWidget.setModel(model)
        tblWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        tblWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        tblWidget.addPopupDuplicateCurrentRow()
        tblWidget.addPopupSeparator()
        tblWidget.addMoveRow()
        tblWidget.addPopupDelRow()


    def setGroupId(self, id):
        self.groupId = id


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(   self.edtCode,          record, 'code')
        setLineEditValue(   self.edtName,          record, 'name')
        self.groupId = forceRef(record.value('group_id'))
        self.modelInItems.loadItems(self.itemId())
        self.modelOutItems.loadItems(self.itemId())


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue('group_id', toVariant(self.groupId))
        getLineEditValue(   self.edtCode,          record, 'code')
        getLineEditValue(   self.edtName,          record, 'name')
        return record


    def saveInternals(self, id):
        self.modelInItems.saveItems(id)
        self.modelOutItems.saveItems(id)


class CItemsModel(CInDocTableModel):
    def __init__(self, parent, isOut):
        CInDocTableModel.__init__(self, 'rbStockRecipe_Item', 'id', 'master_id', parent)
        self.isOut = isOut
        self.addCol(CNomenclatureInDocTableCol(u'ЛСиИМН', 'nomenclature_id', 50, showFields = CRBComboBox.showName))
        self.addCol(CFloatInDocTableCol( u'Кол-во', 'qnt', 12))
        self.addHiddenCol('isOut')
        self.setFilter('isOut!=0' if isOut else 'isOut=0')


    def getEmptyRecord(self):
        record = CInDocTableModel.getEmptyRecord(self)
        record.setValue('isOut', toVariant(self.isOut))
        return record
