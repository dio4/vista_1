# -*- coding: utf-8 -*-

from RefBooks.Tables import rbAccountType, rbCode, rbName
from library.ItemsListDialog import CItemEditorDialog, CItemsListDialog
from library.TableModel import CTextCol


class CRBAccountTypeList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код', [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
        ], rbAccountType, [rbCode, rbName])
        self.setWindowTitleEx(u'Типы счетов')

    def getItemEditor(self):
        return CRBFinanceEditor(self)


class CRBFinanceEditor(CItemEditorDialog):
    def __init__(self, parent):
        CItemEditorDialog.__init__(self, parent, rbAccountType)
        self.setWindowTitleEx(u'Тип счета')
