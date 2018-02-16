# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore

from library.ItemsListDialog import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel import CTextCol
from library.Utils import forceString, forceStringEx, toVariant

from RefBooks.Tables import rbCode, rbName, rbServiceCategory

from Ui_RBServiceCategoryEditor import Ui_ItemEditorDialog


class CRBServiceCategoryList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код', [rbCode], 10),
            CTextCol(u'Наименование', [rbName], 30),
        ], rbServiceCategory, [rbCode, rbName])
        self.setWindowTitleEx(u'Категори услуг')

    def getItemEditor(self):
        return CRBServiceCategoryEditor(self)


#
# ##########################################################################
#

class CRBServiceCategoryEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self, parent):
        CItemEditorBaseDialog.__init__(self, parent, rbServiceCategory)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Категория услуг')
        self.setupDirtyCather()

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        self.edtCode.setText(forceString(record.value(rbCode)))
        self.edtName.setText(forceString(record.value(rbName)))

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue(rbCode, toVariant(forceStringEx(self.edtCode.text())))
        record.setValue(rbName, toVariant(forceStringEx(self.edtName.text())))
        return record
