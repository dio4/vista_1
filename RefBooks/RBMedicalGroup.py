# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013-2014 Vista Software. All rights reserved.
##
#############################################################################

from library.ItemsListDialog    import CItemsListDialog, CItemEditorDialog
from library.TableModel         import CTextCol

from RefBooks.Tables            import rbCode, rbName, rbMedicalGroup

class CRBMedicalGroupList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            ], rbMedicalGroup, [rbCode, rbName])
        self.setWindowTitleEx(u'Медицинские группы')

    def getItemEditor(self):
        return CRBMedicalGroupEditor(self)

class CRBMedicalGroupEditor(CItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorDialog.__init__(self, parent, rbMedicalGroup)
        self.setWindowTitleEx(u'Медицинские группы')
