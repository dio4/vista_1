# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from library.TableModel         import CTextCol
from library.ItemsListDialog    import CItemsListDialog, CItemEditorDialog

from RefBooks.Tables            import rbCode, rbName, rbHurtType


#from RefBooks.RBHurtType import CRBHurtTypeList

class CRBHurtTypeList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            ], rbHurtType, [rbCode, rbName])
        self.setWindowTitleEx(u'Типы вредности')

    def getItemEditor(self):
        return CRBHurtTypeEditor(self)

class CRBHurtTypeEditor(CItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorDialog.__init__(self, parent, rbHurtType)
        self.setWindowTitleEx(u'Тип вредности')
