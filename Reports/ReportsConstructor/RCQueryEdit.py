# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore

from library.Utils import forceString, forceBool, toVariant, forceInt

from library.ItemsListDialog             import CItemEditorBaseDialog
from library.interchange                 import setLineEditValue

from models.RCTableModel                 import CRCColsModel, CRCItemModel, CRCGroupsModel, CRCOrdersModel
from models.RCFieldsTreeModel            import CQueryFieldsTreeModel
from models.RCConditionTreeModel         import CRCConditionTreeModel

from Ui_QueryEditorDialog import Ui_QueryDialog

class CRCQueryEditorDialog(CItemEditorBaseDialog, Ui_QueryDialog):
    def __init__(self, parent, modelFields, index):
        CItemEditorBaseDialog.__init__(self, parent, 'rcQuery')
        self.modelFields = modelFields
        self.modelParams = modelFields._modelParams
        self.referencedField = modelFields.getItem(index)
        self.preSetupUi()
        self.setupUi(self)
        self.postSetupUi()
        self.setWindowTitleEx(u'Отчёт')


    def preSetupUi(self):
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMaximizeButtonHint)
        self.addModels('Tree', CQueryFieldsTreeModel(self))
        self.addModels('Cols', CRCColsModel(self, self.modelTree))
        self.addModels('Groups', CRCGroupsModel(self, self.modelTree))
        self.addModels('Orders', CRCOrdersModel(self, self.modelTree))
        self.addModels('Conditions', CRCConditionTreeModel(self, self.modelTree, self.modelParams))
        self.addModels('Functions', CRCItemModel(self, ['name', 'function', 'description', 'hasSpace'], 'rcFunction'))
        self.addModels('Tables', CRCItemModel(self, ['name'], 'rcTable'))

    def postSetupUi(self):
        self.setModels(self.tableFields, self.modelCols, self.selectionModelCols)
        self.setModels(self.tableGroups, self.modelGroups, self.selectionModelGroups)
        self.setModels(self.tableOrders, self.modelOrders, self.selectionModelOrders)
        self.tableFields.setColSize()
        self.cmbMainTable.setModel(self.modelTables)
        self.setModels(self.treeConds, self.modelConditions, self.selectionModelConditions)
        self.modelTables.loadItems()
        self.modelFunctions.loadItems()
        self.modelTree.loadItems()
        self.modelTree.setModelParams(self.modelParams)
        self.modelTree.setModelFunctions(self.modelFunctions)
        self.cmbReference.setModel(self.modelFields)

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(self.edtName, record, 'name')
        self.cmbMainTable.setValue(forceInt(record.value('mainTable_id')))
        self.modelTree.setMainTableId(self.cmbMainTable.value())
        self.modelTree.setState('')
        self.modelCols.loadItems(self.itemId())
        self.modelGroups.loadItems(self.itemId())
        self.modelOrders.loadItems(self.itemId())
        self.modelConditions.loadItems(self.itemId())
        self.modelTree.setState(forceString(record.value('stateTree')))
        self.referencedField = forceString(record.value('referencedField'))
        self.cmbReference.setValue(self.referencedField)

    def getRecord(self):
        self.referencedField = self.cmbReference.value()[0]
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue('name', toVariant(self.edtName.text()))
        record.setValue('mainTable_id', toVariant(self.cmbMainTable.value()))
        record.setValue('stateTree', toVariant(self.modelTree.getState()))
        record.setValue('referencedField', toVariant(self.referencedField))
        return record

    def saveInternals(self, id):
        self.modelCols.saveItems(id)
        self.modelGroups.saveItems(id)
        self.modelOrders.saveItems(id)
        self.modelConditions.saveItems(id)

    def checkDataEntered(self):
        result = True
        result = result & forceBool(self.edtName.text())
        return result

    def on_cmbMainTable_currentIndexChanged(self, value):
        self.modelTree.setMainTableId(self.cmbMainTable.value())

    def on_cmbReference_currentIndexChanged(self, value):
        self.referencedField = self.cmbReference.value()[0]