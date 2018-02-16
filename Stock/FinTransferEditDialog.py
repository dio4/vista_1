# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.crbcombobox         import CRBComboBox
from library.InDocTable          import CInDocTableModel, CInDocTableCol, CDateInDocTableCol, CFloatInDocTableCol, \
                                        CRBInDocTableCol
from library.interchange         import getRBComboBoxValue

from Stock.NomenclatureComboBox  import CNomenclatureInDocTableCol
from Stock.StockMotionBaseDialog import CStockMotionBaseDialog

from Ui_FinTransfer import Ui_FinTransferDialog


class CFinTransferEditDialog(CStockMotionBaseDialog, Ui_FinTransferDialog):
    def __init__(self,  parent):
        CStockMotionBaseDialog.__init__(self, parent)

        self.addModels('Items', CItemsModel(self))
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setupDirtyCather()
        self.tblItems.setModel(self.modelItems)
        self.prepareItemsPopupMenu(self.tblItems)
        self.tblItems.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tblItems.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

    def setDefaults(self):
        CStockMotionBaseDialog.setDefaults(self)


    def setRecord(self, record):
        CStockMotionBaseDialog.setRecord(self, record)
        self.modelItems.loadItems(self.itemId())
        self.setIsDirty(False)


    def getRecord(self):
        record = CStockMotionBaseDialog.getRecord(self)
        getRBComboBoxValue( self.cmbSupplier, record, 'receiver_id')
        getRBComboBoxValue( self.cmbSupplierPerson, record, 'receiverPerson_id')
        record.setValue('type', 2)
        return record


    def saveInternals(self, id):
        self.modelItems.saveItems(id)


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


class CItemsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'StockMotion_Item', 'id', 'master_id', parent)
        self.addCol(CNomenclatureInDocTableCol(u'ЛСиИМН', 'nomenclature_id', 50, showFields = CRBComboBox.showName))
        self.addCol(CInDocTableCol( u'Партия', 'batch', 16))
        self.addCol(CDateInDocTableCol( u'Годен до', 'shelfTime', 12, canBeEmpty=True))
        self.addCol(CRBInDocTableCol(    u'Прежний тип финансирования', 'oldFinance_id', 15, 'rbFinance'))
        self.addCol(CRBInDocTableCol(    u'Новый тип финансирования', 'finance_id', 15, 'rbFinance'))
        self.addCol(CFloatInDocTableCol( u'Кол-во', 'qnt', 12))
        self.addCol(CFloatInDocTableCol( u'Сумма',  'sum', 12))
