# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from library.interchange            import getLineEditValue, setLineEditValue
from library.ItemsListDialog        import CItemsListDialog, CItemEditorDialog
from library.TableModel             import CTextCol

from RefBooks.Tables                import rbCode, rbName, rbEventTypePurpose

from Ui_RBEventTypePurposeEditor    import Ui_ItemEditorDialog


class CRBEventTypePurposeList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',              [rbCode], 20),
            CTextCol(u'Региональный код', ['regionalCode'], 20),
            CTextCol(u'Наименование',     [rbName], 40),
            CTextCol(u'Федеральный код', ['federalCode'], 8),
            ], rbEventTypePurpose, [rbCode, rbName])
        self.setWindowTitleEx(u'Назначение типов событий')

    def getItemEditor(self):
        return CRBEventTypePurposeEditor(self)



class CRBEventTypePurposeEditor(Ui_ItemEditorDialog, CItemEditorDialog):
#    setupUi = Ui_ItemEditorDialog.setupUi
#    retranslateUi = Ui_ItemEditorDialog.retranslateUi

    def __init__(self,  parent):
        CItemEditorDialog.__init__(self, parent, rbEventTypePurpose)
        self.setWindowTitleEx(u'Назначение типа событий')

    def setRecord(self, record):
        CItemEditorDialog.setRecord(self, record)
        setLineEditValue(self.edtRegionalCode, record, 'regionalCode')
        setLineEditValue(self.edtFederalCode, record, 'federalCode')

    def getRecord(self):
        record = CItemEditorDialog.getRecord(self)
        getLineEditValue(self.edtRegionalCode, record, 'regionalCode')
        getLineEditValue(self.edtFederalCode, record, 'federalCode')
        return record
