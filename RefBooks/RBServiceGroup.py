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

from RefBooks.Tables import rbCode, rbName, rbServiceGroup

from Ui_RBServiceGroupEditor import Ui_ItemEditorDialog


class CRBServiceGroupList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код', [rbCode], 10),
            CTextCol(u'Региональный код', ['regionalCode'], 10),
            CTextCol(u'Наименование', [rbName], 30),
        ], rbServiceGroup, [rbCode, rbName])
        self.setWindowTitleEx(u'Группы услуг')

    def getItemEditor(self):
        return CRBServiceGroupEditor(self)


#
# ##########################################################################
#

class CRBServiceGroupEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self, parent):
        CItemEditorBaseDialog.__init__(self, parent, rbServiceGroup)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Группа услуг')
        self.setupDirtyCather()

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        self.edtCode.setText(forceString(record.value(rbCode)))
        self.edtRegionalCode.setText(forceString(record.value('regionalCode')))
        self.edtName.setText(forceString(record.value(rbName)))

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue(rbCode, toVariant(forceStringEx(self.edtCode.text())))
        record.setValue('regionalCode', toVariant(forceStringEx(self.edtRegionalCode.text())))
        record.setValue(rbName, toVariant(forceStringEx(self.edtName.text())))
        return record
