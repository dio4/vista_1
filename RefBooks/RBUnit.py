# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from library.ItemsListDialog import CItemsListDialog, CItemEditorDialog
from library.TableModel import CTextCol

from RefBooks.Tables import rbCode, rbName, rbUnit


class CRBUnitList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20, isRTF = True),
            CTextCol(u'Наименование', [rbName], 40, isRTF = True),
            ], rbUnit, [rbCode, rbName])
        self.setWindowTitleEx(u'Единицы измерения')

    def getItemEditor(self):
        return CRBUnitEditor(self)

class CRBUnitEditor(CItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorDialog.__init__(self, parent, rbUnit)
        self.setWindowTitleEx(u'Единица измерения')
