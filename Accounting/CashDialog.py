# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from Events.EventInfo           import CEventInfo, CCashOperationInfo
from library.ItemsListDialog    import CItemEditorBaseDialog
from library.PrintInfo          import CInfoContext, CDateInfo
from library.PrintTemplates     import getPrintButton, applyTemplate
from library.Utils              import *

from Ui_CashDialog              import Ui_CashDialog


class CashDialogEditor(CItemEditorBaseDialog, Ui_CashDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'Event_Payment')
        self.btnPrint = getPrintButton(self, 'cashOrder')
        self.btnPrint.setObjectName('btnPrint')
        self.setupUi(self)
        self.cmbCashOperation.setTable('rbCashOperation', True)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.buttonBox.addButton(self.btnPrint, QtGui.QDialogButtonBox.ActionRole)
        self.setupDirtyCather()
        self.eventId = None
        self.cashBox = ''


    def setEventId(self, eventId):
        self.eventId = eventId


    def setCashBox(self, cashBox):
        self.cashBox = cashBox


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        self.edtDate.setDate(forceDate(record.value('date')))
        self.cmbCashOperation.setValue(forceRef(record.value('cashOperation_id')))
        self.edtSum.setValue(forceDecimal(record.value('sum')))
        self.eventId = forceRef(record.value('master_id'))
        self.cashBox = forceString(record.value('cashBox'))


    def checkDataEntered(self):
        return True


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue('master_id',         toVariant(self.eventId))
        record.setValue('date',              toVariant(self.edtDate.date()))
        record.setValue('cashOperation_id',  toVariant(self.cmbCashOperation.value()))
        record.setValue('sum',               toVariant(self.edtSum.value()))
        record.setValue('cashBox',           toVariant(self.cashBox))
        return record


    def save(self):
        if self.lock('Event', self.eventId):
            try:
                return CItemEditorBaseDialog.save(self)
            finally:
                self.releaseLock()
        else:
            return False


    @pyqtSlot(int)
    def on_btnPrint_printByTemplate(self, templateId):
        printCashOrder(self,
                       templateId,
                       self.eventId,
                       self.edtDate.date(),
                       self.cmbCashOperation.value(),
                       self.edtSum.value(),
                       self.cashBox
                      )


def printCashOrder(widget, templateId, eventId, date, cashOperationId, sum, cashBox):
    context = CInfoContext()
    eventInfo = context.getInstance(CEventInfo, eventId)
    data = { 'event'        : eventInfo,
             'client'       : eventInfo.client,
             'date'         : CDateInfo(date),
             'cashOperation': context.getInstance(CCashOperationInfo, cashOperationId),
             'sum'          : sum,
             'cashBox'      : cashBox
           }
    applyTemplate(widget, templateId, data)