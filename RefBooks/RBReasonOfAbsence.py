# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from library.ItemsListDialog    import CItemsListDialog, CItemEditorDialog
from library.TableModel         import CTextCol

from RefBooks.Tables            import rbCode, rbName, rbReasonOfAbsence


class CRBReasonOfAbsenceList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            ], rbReasonOfAbsence, [rbCode, rbName])
        self.setWindowTitleEx(u'Причины отсутствия')

    def getItemEditor(self):
        return CRBReasonOfAbsenceEditor(self)


class CRBReasonOfAbsenceEditor(CItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorDialog.__init__(self, parent, rbReasonOfAbsence)
        self.setWindowTitleEx(u'Причина отсутствия')
