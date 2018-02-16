# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from library.interchange import *
from library.ItemsListDialog import CItemEditorBaseDialog

from Ui_AccountEditDialog import Ui_AccountEditDialog


class CAccountEditDialog(CItemEditorBaseDialog, Ui_AccountEditDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'Account')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Счет')
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(self.edtNumber,       record, 'number')
        setDateEditValue(self.edtDate,         record, 'date')
        setDateEditValue(self.edtExposeDate,   record, 'exposeDate')
        self.setIsDirty(False)


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(self.edtNumber,       record, 'number')
        getDateEditValue(self.edtDate,         record, 'date')
        getDateEditValue(self.edtExposeDate,   record, 'exposeDate')
        return record


    def checkDataEntered(self):
        result = True
        number = forceStringEx(self.edtNumber.text())
        result = result and (number or self.checkInputMessage(u'Номер', False, self.edtNumber))
        return result