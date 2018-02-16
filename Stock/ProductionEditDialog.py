# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.crbcombobox         import CRBComboBox
from library.DialogBase          import CDialogBase
from library.InDocTable          import CInDocTableModel, CInDocTableCol, CDateInDocTableCol, CFloatInDocTableCol, \
                                        CRBInDocTableCol
from library.interchange         import getRBComboBoxValue
from library.Utils               import forceBool, forceDouble, toVariant

from Stock.NomenclatureComboBox  import CNomenclatureInDocTableCol
from Stock.StockMotionBaseDialog import CStockMotionBaseDialog

from Ui_Production               import Ui_ProductionDialog
from Ui_SelectRecipeDialog       import Ui_Dialog as Ui_SelectRecipeDialog


class CProductionEditDialog(CStockMotionBaseDialog, Ui_ProductionDialog):
    def __init__(self,  parent):
        CStockMotionBaseDialog.__init__(self, parent)
        self.btnAddRecipe = QtGui.QPushButton(u'По рецепту', self)
        self.btnAddRecipe.setObjectName('btnAddRecipe')

        self.addModels('InItems', CItemsModel(self, False))
        self.addModels('OutItems', CItemsModel(self, True))
        self.setupUi(self)
        self.buttonBox.addButton(self.btnAddRecipe, QtGui.QDialogButtonBox.ActionRole)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setupDirtyCather()
        self.tblInItems.setModel(self.modelInItems)
        self.prepareItemsPopupMenu(self.tblInItems)
        self.tblInItems.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tblInItems.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        self.tblOutItems.setModel(self.modelOutItems)
        self.prepareItemsPopupMenu(self.tblOutItems)
        self.tblOutItems.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tblOutItems.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)


    def setDefaults(self):
        CStockMotionBaseDialog.setDefaults(self)


    def setRecord(self, record):
        CStockMotionBaseDialog.setRecord(self, record)
        self.modelInItems.loadItems(self.itemId())
        self.modelOutItems.loadItems(self.itemId())
        self.setIsDirty(False)


    def getRecord(self):
        record = CStockMotionBaseDialog.getRecord(self)
        getRBComboBoxValue( self.cmbSupplier, record, 'receiver_id')
        getRBComboBoxValue( self.cmbSupplierPerson, record, 'receiverPerson_id')
        record.setValue('type', 3)
        return record


    def saveInternals(self, id):
        self.modelInItems.saveItems(id)
        self.modelOutItems.saveItems(id)


    def checkDataEntered(self):
        result = True
#        result = result and (self.cmbPurpose.value() or self.checkInputMessage(u'назначение', False, self.cmbPurpose))
#        result = result and self.checkItemsDataEntered()
        return result


#    def checkItemsDataEntered(self):
#        for row, item in enumerate(self.modelItems.items()):
#            if not self.checkItemDataEntered(row, item):
#                return False
#        return True
#
#
#    def checkItemDataEntered(self, row, item):
#        nomenclatureId = forceString(item.value('nomenclature_id'))
#        qnt            = forceDouble(item.value('qnt'))
#        result = nomenclatureId or self.checkInputMessage(u'лекарственное средство или изделие медицинского назначения', False, self.tblProperties, row, 0)
#        result = result and (qnt or self.checkInputMessage(u'количество', False, self.tblProperties, row, 2))
#        return result

    def addRecipe(self, recipeId, rate, financeId):
        db = QtGui.qApp.db
        table = db.table('rbStockRecipe_Item')
        records = db.getRecordList(table, '*', table['master_id'].eq(recipeId), 'idx')
        models = [self.modelInItems, self.modelOutItems]
        for record in records:
            model = models[forceBool(record.value('isOut'))]
            newRecord = model.getEmptyRecord()
            newRecord.setValue('nomenclature_id', record.value('nomenclature_id'))
            newRecord.setValue('finance_id',      toVariant(financeId))
            newRecord.setValue('qnt',             toVariant(rate*forceDouble(record.value('qnt'))))
            model.addRecord(newRecord)


    @QtCore.pyqtSlot()
    def on_btnAddRecipe_clicked(self):
        dialog = CSelectRecipe(self)
        if dialog.exec_():
            recipeId, rate, financeId = dialog.getResult()
            if recipeId and rate:
                self.addRecipe(recipeId, rate, financeId)


class CItemsModel(CInDocTableModel):
    def __init__(self, parent, isOut):
        CInDocTableModel.__init__(self, 'StockMotion_Item', 'id', 'master_id', parent)
        self.isOut = isOut
        self.addCol(CNomenclatureInDocTableCol(u'ЛСиИМН', 'nomenclature_id', 50, showFields = CRBComboBox.showName))
        self.addCol(CInDocTableCol( u'Партия', 'batch', 16))
        self.addCol(CDateInDocTableCol( u'Годен до', 'shelfTime', 12, canBeEmpty=True))
        self.addCol(CRBInDocTableCol(    u'Тип финансирования', 'finance_id', 15, 'rbFinance'))
        self.addCol(CFloatInDocTableCol( u'Кол-во', 'qnt', 12))
        self.addCol(CFloatInDocTableCol( u'Сумма', 'sum', 12))
        self.addHiddenCol('isOut')
        self.setFilter('isOut!=0' if isOut else 'isOut=0')


    def getEmptyRecord(self):
        record = CInDocTableModel.getEmptyRecord(self)
        record.setValue('isOut', toVariant(self.isOut))
        return record


class CSelectRecipe(CDialogBase, Ui_SelectRecipeDialog):
    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.cmbRecipe.setTable('rbStockRecipe', order='name')
        self.cmbFinance.setTable('rbFinance', True)


    def getResult(self):
        return self.cmbRecipe.value(), self.edtRate.value(), self.cmbFinance.value()

