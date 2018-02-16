# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from library.ItemsListDialog    import CItemsListDialog, CItemEditorDialog
from library.TableModel         import CTextCol

from RefBooks.Tables            import rbCode, rbName, rbHurtFactorType


class CRBHurtFactorTypeList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            ], rbHurtFactorType, [rbCode, rbName])
        self.setWindowTitleEx(u'Факторы вредности')

    def getItemEditor(self):
        return CRBHurtFactorTypeEditor(self)

class CRBHurtFactorTypeEditor(CItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorDialog.__init__(self, parent, rbHurtFactorType)
        self.setWindowTitleEx(u'Фактор вредности')
