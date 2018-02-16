# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore

from library.interchange        import getLineEditValue, setLineEditValue
from library.ItemsListDialog    import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel         import CTextCol

from RefBooks.Tables            import rbCode, rbName, rbPost

from Ui_RBPostEditor            import Ui_ItemEditorDialog


class CRBPostList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 8),
            CTextCol(u'Наименование', [rbName], 40),
            CTextCol(u'Региональный код', ['regionalCode'], 8),
            ], rbPost, [rbCode, rbName])
        self.setWindowTitleEx(u'Должности')

    def getItemEditor(self):
        return CRBPostEditor(self)

class CRBPostEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    setupUi = Ui_ItemEditorDialog.setupUi

    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, rbPost)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Должность')
        self.setupDirtyCather()

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(self.edtCode, record, 'code')
        setLineEditValue(self.edtName, record, 'name')
        setLineEditValue(self.edtRegionalCode, record, 'regionalCode')
        setLineEditValue(self.edtFlatCode, record, 'flatCode')
        setLineEditValue(self.edtSyncGUID, record, 'syncGUID')

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(self.edtCode,record, 'code')
        getLineEditValue(self.edtName,record, 'name')
        getLineEditValue(self.edtRegionalCode, record, 'regionalCode')
        getLineEditValue(self.edtFlatCode, record, 'flatCode')
        getLineEditValue(self.edtSyncGUID, record, 'syncGUID')
        return record
