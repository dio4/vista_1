# -*- coding: utf-8 -*-

from PyQt4 import QtGui

from library.Utils                         import forceInt
from Stock.FinTransferEditDialog           import CFinTransferEditDialog
from Stock.InventoryEditDialog             import CInventoryEditDialog
from Stock.InvoiceEditDialog               import CInvoiceEditDialog
from Stock.ProductionEditDialog            import CProductionEditDialog


def editStockMotion(widget, id):
    type = forceInt(QtGui.qApp.db.translate('StockMotion', 'id', id, 'type'))
    dialogClass = [CInvoiceEditDialog, CInventoryEditDialog, CFinTransferEditDialog, CProductionEditDialog][type]
    dialog = dialogClass(widget)
    dialog.load(id)
    return dialog.exec_()
