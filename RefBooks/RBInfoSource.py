# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from library.ItemsListDialog import CItemsListDialogEx, CItemEditorDialog
from library.TableModel import CTextCol
from RefBooks.Tables import rbCode, rbName


class CRBInfoSourceList(CItemsListDialogEx):
    def __init__(self, parent):
        super(CRBInfoSourceList, self).__init__(parent, [
            CTextCol(u'Код источника', [rbCode], 20),
            CTextCol(u'Название источника', [rbName], 40)
            ], 'rbInfoSource', [rbCode, rbName])
        self.setWindowTitleEx(u'Источники информации')

    def getItemEditor(self):
        return CRBInfoSourceEditor(self)


class CRBInfoSourceEditor(CItemEditorDialog):
    def __init__(self, parent):
        super(CRBInfoSourceEditor, self).__init__(parent, 'rbInfoSource')
        self.setWindowTitleEx(u'Редактировать источник информации')
        self.setupDirtyCather()
