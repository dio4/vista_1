# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui, QtSql

from library.crbcombobox           import CRBComboBox
from library.InDocTable            import CInDocTableModel, CFloatInDocTableCol, CRBInDocTableCol
from library.interchange           import getCheckBoxValue, getDateEditValue, getDatetimeEditValue, getLineEditValue, \
                                          getRBComboBoxValue, setCheckBoxValue, setDateEditValue, setDatetimeEditValue,\
                                          setLineEditValue, setRBComboBoxValue
from library.ItemsListDialog       import CItemEditorBaseDialog
from library.Utils                 import forceDouble, forceString

from Stock.NomenclatureComboBox    import CNomenclatureInDocTableCol

from Ui_StockRequisitionEditDialog import Ui_StockRequisitionDialog


class CStockRequisitionEditDialog(CItemEditorBaseDialog, Ui_StockRequisitionDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'StockRequisition')

        self.addModels('Items', CItemsModel(self))
        self.actDuplicate = QtGui.QAction(u'Дублировать', self)
        self.actDuplicate.setObjectName('actDuplicate')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setupDirtyCather()
        self.tblItems.setModel(self.modelItems)
        self.tblItems.createPopupMenu([self.actDuplicate, '-'])
        self.tblItems.popupMenu().addSeparator()
        self.tblItems.addMoveRow()
        self.tblItems.addPopupDelRow()
        self.tblItems.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tblItems.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)


    def setDefaults(self):
        self.edtDate.setDate(QtCore.QDate.currentDate())
        self.edtDeadlineDate.setDate(QtCore.QDate())
        self.cmbRecipient.setValue(QtGui.qApp.currentOrgStructureId())


#    def setRequestMode(self):
#        self.edtDate.setEnabled(False)
#        self.cmbRecipient.setEnabled(False)


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setDateEditValue(   self.edtDate,           record, 'date')
        setDatetimeEditValue(self.edtDeadlineDate, self.edtDeadlineTime, record, 'deadline')
        setCheckBoxValue(   self.chkRevoked,        record, 'revoked')
        setRBComboBoxValue( self.cmbSupplier,       record, 'supplier_id')
        setRBComboBoxValue( self.cmbRecipient,      record, 'recipient_id')
        setLineEditValue(   self.edtNote,           record, 'note')
        self.modelItems.loadItems(self.itemId())
        self.setIsDirty(False)


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getDateEditValue(   self.edtDate,           record, 'date')
        getDatetimeEditValue(self.edtDeadlineDate, self.edtDeadlineTime, record, 'deadline', True)
        getCheckBoxValue(   self.chkRevoked,        record, 'revoked')
        getRBComboBoxValue( self.cmbSupplier,       record, 'supplier_id')
        getRBComboBoxValue( self.cmbRecipient,      record, 'recipient_id')
        getLineEditValue(   self.edtNote,           record, 'note')
        return record


    def saveInternals(self, id):
        self.modelItems.saveItems(id)


    def checkDataEntered(self):
        result = True
#        result = result and (self.cmbPurpose.value() or self.checkInputMessage(u'назначение', False, self.cmbPurpose))
        result = result and self.checkItemsDataEntered()
        return result


    def checkItemsDataEntered(self):
        for row, item in enumerate(self.modelItems.items()):
            if not self.checkItemDataEntered(row, item):
                return False
        return True


    def checkItemDataEntered(self, row, item):
        nomenclatureId = forceString(item.value('nomenclature_id'))
        qnt            = forceDouble(item.value('qnt'))
        result = nomenclatureId or self.checkInputMessage(u'лекарственное средство или изделие медицинского назначения', False, self.tblProperties, row, 0)
        result = result and (qnt or self.checkInputMessage(u'количество', False, self.tblProperties, row, 2))
        return result


    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtDeadlineDate_dateChanged(self, date):
        self.edtDeadlineTime.setEnabled(bool(date))


    @QtCore.pyqtSlot()
    def on_actDuplicate_triggered(self):
        index = self.tblItems.currentIndex()
        row = index.row()
        items = self.modelItems.items()
        if 0<=row<len(items):
            newItem = QtSql.QSqlRecord(items[row])
            newItem.setValue('id', QtCore.QVariant())
            self.modelItems.insertRecord(row+1, newItem)


class CItemsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'StockRequisition_Item', 'id', 'master_id', parent)
        self.addCol(CNomenclatureInDocTableCol(u'ЛСиИМН', 'nomenclature_id', 50, showFields = CRBComboBox.showName))
        self.addCol(CRBInDocTableCol(    u'Тип финансирования', 'finance_id', 15, 'rbFinance'))
        self.addCol(CFloatInDocTableCol( u'Кол-во', 'qnt', 12))
        self.addCol(CFloatInDocTableCol( u'Отпущено', 'satisfiedQnt', 12)).setReadOnly()
