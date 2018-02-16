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

from RefBooks.Tables            import rbCode, rbName, rbCodeRegional, rbEmergencyAccident

from Ui_RBEmergency             import Ui_ItemEditorDialog


class CRBEmergencyAccidentList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            CTextCol(u'Региональный код', [rbCodeRegional], 20),
            ], rbEmergencyAccident, [rbCode, rbName])
        self.setWindowTitleEx(u'Несчастный случай')

    def getItemEditor(self):
        return CRBEmergencyAccidentEditor(self)

#
# ##########################################################################
#

class CRBEmergencyAccidentEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, rbEmergencyAccident)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Несчастный случай')
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        self.edtCode.setText(forceString(record.value(rbCode)))
        self.edtName.setText(forceString(record.value(rbName)))
        self.edtCodeRegional.setText(forceString(record.value(rbCodeRegional)))

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue(rbCode,       toVariant(forceStringEx(self.edtCode.text())))
        record.setValue(rbName,       toVariant(forceStringEx(self.edtName.text())))
        record.setValue(rbCodeRegional,  toVariant(forceStringEx(self.edtCodeRegional.text())))
        return record

