# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from library.ItemsListDialog    import CItemsListDialog, CItemEditorDialog
from library.TableModel         import CTextCol

from RefBooks.Tables            import rbCode, rbName, rbHealthGroup


#from RefBooks.RBHealthGroup import CRBHealthGroupList

class CRBHealthGroupList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            ], rbHealthGroup, [rbCode, rbName])
        self.setWindowTitleEx(u'Группы здоровья')

    def getItemEditor(self):
        return CRBHealthGroupEditor(self)

class CRBHealthGroupEditor(CItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorDialog.__init__(self, parent, rbHealthGroup)
        self.setWindowTitleEx(u'Группа здоровья')
