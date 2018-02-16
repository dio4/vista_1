# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

from library.crbcombobox          import CRBComboBox
from library.InDocTable           import CInDocTableModel, CFloatInDocTableCol, CRBInDocTableCol

from Stock.NomenclatureComboBox   import CNomenclatureInDocTableCol
from Stock.StockMotionBaseDialog  import CStockMotionBaseDialog

from Stock.Ui_Inventory           import Ui_InventoryDialog


class CNomenclatureExpenseEditDialog(CStockMotionBaseDialog, Ui_InventoryDialog):
    def __init__(self,  parent):
        CStockMotionBaseDialog.__init__(self, parent)

        self.addModels('Items', CItemsModel(self))
        self.actDuplicate = QtGui.QAction(u'Дублировать', self)
        self.actDuplicate.setObjectName('actDuplicate')
        self.btnFill = QtGui.QPushButton(u'Заполнить', self)
        self.btnFill.setObjectName('btnFill')
        self.btnFill.setShortcut('F9')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setupDirtyCather()
        self.tblItems.setModel(self.modelItems)
        self.prepareItemsPopupMenu(self.tblItems)
        self.tblItems.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tblItems.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.buttonBox.addButton(self.btnFill, QtGui.QDialogButtonBox.ActionRole)


    def setDefaults(self):
        CStockMotionBaseDialog.setDefaults(self)


    def setRecord(self, record):
        CStockMotionBaseDialog.setRecord(self, record)
        self.modelItems.loadItems(self.itemId())
        self.setIsDirty(False)


    def getRecord(self):
        record = CStockMotionBaseDialog.getRecord(self)
        record.setValue('type', 4)
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

    @QtCore.pyqtSlot()
    def on_btnFill_clicked(self):
        orgStructureId = self.cmbSupplier.value()
        if orgStructureId:
            self.modelItems.fill(orgStructureId)


class CItemsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'StockMotion_Item', 'id', 'master_id', parent)
        self.addCol(CNomenclatureInDocTableCol(u'ЛСиИМН', 'nomenclature_id', 50, showFields = CRBComboBox.showName))
        self.addCol(CRBInDocTableCol(    u'Тип финансирования', 'finance_id', 15, 'rbFinance'))
        self.addCol(CFloatInDocTableCol( u'Кол-во по документам', 'oldQnt', 12))
        self.addCol(CFloatInDocTableCol( u'Сумма по документам', 'oldSum', 12))
        self.addCol(CFloatInDocTableCol( u'Фактическое кол-во', 'qnt', 12))
        self.addCol(CFloatInDocTableCol( u'Фактическая сумма', 'sum', 12))

    def fill(self, orgStructureId):
        stmt = u'''
SELECT nomenclature_id,
       finance_id,
       sum(qnt) AS `qnt`,
       sum(`sum`) AS `sum`
FROM
    (
    SELECT debNomenclature_id AS nomenclature_id,
           debFinance_id      AS finance_id,
           sum(qnt)           AS `qnt`,
           sum(`sum`)         AS `sum`
    FROM StockTrans
    WHERE debOrgStructure_id = %d
    GROUP BY debOrgStructure_id, debNomenclature_id, debFinance_id
    UNION
    SELECT creNomenclature_id AS nomenclature_id,
           creFinance_id      AS finance_id,
           -sum(qnt)          AS `qnt`,
           -sum(`sum`)        AS `sum`
    FROM StockTrans
    WHERE creOrgStructure_id = %d
    GROUP BY creOrgStructure_id, creNomenclature_id, creFinance_id
    ) AS T
GROUP BY nomenclature_id, finance_id
HAVING qnt != 0 OR `sum` != 0''' % (orgStructureId, orgStructureId)
        query = QtGui.qApp.db.query(stmt)
        while query.next():
            record = query.record()
            myItem = self.getEmptyRecord()
            myItem.setValue('nomenclature_id', record.value('nomenclature_id'))
            myItem.setValue('finance_id',      record.value('finance_id'))
            myItem.setValue('qnt',             record.value('qnt'))
            myItem.setValue('sum',             record.value('sum'))
            myItem.setValue('oldQnt',          record.value('qnt'))
            myItem.setValue('oldSum',          record.value('sum'))
            self.items().append(myItem)
        self.reset()
