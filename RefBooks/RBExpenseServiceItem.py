# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore

from library.ItemsListDialog    import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel         import CTextCol
from library.Utils              import forceString, forceStringEx, toVariant

from RefBooks.Tables            import rbCode, rbName, rbExpenseServiceItem

from Ui_RBExpenseServiceItem    import Ui_RBExpenseServiceItem


class CRBExpenseServiceItemList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40)
            ], rbExpenseServiceItem, [rbCode, rbName])
        self.setWindowTitleEx(u'Статьи затрат услуг')

    def getItemEditor(self):
        return CRBExpenseServiceItemEditor(self)

#
# ##########################################################################
#

class CRBExpenseServiceItemEditor(CItemEditorBaseDialog, Ui_RBExpenseServiceItem):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, rbExpenseServiceItem)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Статья затрат услуг')
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        self.edtCode.setText(forceString(record.value(rbCode)))
        self.edtName.setText(forceString(record.value(rbName)))


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue(rbCode,       toVariant(forceStringEx(self.edtCode.text())))
        record.setValue(rbName,       toVariant(forceStringEx(self.edtName.text())))
        return record
