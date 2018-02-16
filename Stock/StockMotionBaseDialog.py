# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

from library.interchange     import getDatetimeEditValue, getLineEditValue, getRBComboBoxValue, setDatetimeEditValue, \
                                    setLineEditValue, setRBComboBoxValue
from library.ItemsListDialog import CItemEditorBaseDialog
from library.Utils           import forceDouble


class CStockCache:
    def __init__(self):
        self._mapIdsToStock = {}


    def getStock(self, orgStructureId, nomenclatureId, financeId):
        key = orgStructureId, nomenclatureId, financeId
        result = self._mapIdsToStock.get(key, None)
        if result is None:
            result = self.readStock(orgStructureId, nomenclatureId, financeId)
            self._mapIdsToStock[key] = result
        return result


    def readStock(self, orgStructureId, nomenclatureId, financeId):
        qnt = 0.0
        sum = 0.0
        if orgStructureId and nomenclatureId and financeId:
            try:
                db = QtGui.qApp.db
                query = db.query('CALL getStock(%d, %d, %d, NULL, @resQnt, @resSum)' % (orgStructureId, nomenclatureId, financeId))
                query = db.query('SELECT @resQnt, @resSum')
                if query.next():
                    record = query.record()
                    qnt = forceDouble(record.value(0))
                    sum = forceDouble(record.value(1))
            except:
                QtGui.qApp.logCurrentException()
        return qnt, sum


    def getPrice(self, orgStructureId, nomenclatureId, financeId):
        qnt, sum = self.getStock(orgStructureId, nomenclatureId, financeId)
        if qnt:
            return sum/qnt
        else:
            return 0.0



class CStockMotionBaseDialog(CItemEditorBaseDialog, CStockCache):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'StockMotion')
        CStockCache.__init__(self)


    def prepareItemsPopupMenu(self, tblWidget):
        tblWidget.addPopupDuplicateCurrentRow()
        tblWidget.addPopupSeparator()
        tblWidget.addMoveRow()
        tblWidget.addPopupDelRow()


    def setDefaults(self):
        now = QtCore.QDateTime.currentDateTime()
        self.edtDate.setDate(now.date())
        self.edtTime.setTime(now.time())
        self.cmbSupplier.setValue(QtGui.qApp.currentOrgStructureId())


    def getPrice(self, nomenclatureId, financeId):
        return CStockCache.getPrice(self, self.cmbSupplier.value(), nomenclatureId, financeId)


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setDatetimeEditValue(self.edtDate, self.edtTime, record, 'date')
        setRBComboBoxValue( self.cmbSupplier,  record, 'supplier_id')
        setRBComboBoxValue( self.cmbSupplierPerson,  record, 'supplierPerson_id')
        setLineEditValue(   self.edtNote,      record, 'note')


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getDatetimeEditValue(self.edtDate, self.edtTime, record, 'date', True)
        getRBComboBoxValue( self.cmbSupplier,       record, 'supplier_id')
        getRBComboBoxValue( self.cmbSupplierPerson,  record, 'supplierPerson_id')
        getLineEditValue(   self.edtNote,           record, 'note')
        return record


    @QtCore.pyqtSlot(int)
    def on_cmbSupplier_currentIndexChanged(self, val):
        orgStructureId = self.cmbSupplier.value()
#        if orgStructureId:
        self.cmbSupplierPerson.setOrgStructureId(orgStructureId)


    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtDate_dateChanged(self, date):
        self.edtTime.setEnabled(bool(date))
