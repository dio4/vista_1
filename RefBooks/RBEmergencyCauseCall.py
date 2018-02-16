# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore

from library.ItemsListDialog    import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel         import CEnumCol, CTextCol
from library.Utils              import forceInt, forceString, forceStringEx, toVariant

from RefBooks.Tables            import rbCode, rbName, rbCodeRegional, rbEmergencyCauseCall, rbTypeCause

from Ui_RBEmergencyCauseCall    import Ui_ItemEditorDialog


class CRBEmergencyCauseCallList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            CEnumCol(u'Тип', [rbTypeCause], [u'вызов', u'обслуживание общ.мероприятия'], 20),
            CTextCol(u'Региональный код', [rbCodeRegional], 20)
            ], rbEmergencyCauseCall, [rbCode, rbName, rbTypeCause])
        self.setWindowTitleEx(u'Повод к вызову')

    def getItemEditor(self):
        return CRBEmergencyCauseCallEditor(self)

#
# ##########################################################################
#

class CRBEmergencyCauseCallEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, rbEmergencyCauseCall)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Повод к вызову')
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        self.edtCode.setText(forceString(record.value(rbCode)))
        self.edtName.setText(forceString(record.value(rbName)))
        self.edtCodeRegional.setText(forceString(record.value(rbCodeRegional)))
        self.cmbType.setCurrentIndex(forceInt(record.value(rbTypeCause)))

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue(rbCode,       toVariant(forceStringEx(self.edtCode.text())))
        record.setValue(rbName,       toVariant(forceStringEx(self.edtName.text())))
        record.setValue(rbCodeRegional,  toVariant(forceStringEx(self.edtCodeRegional.text())))
        record.setValue(rbTypeCause, toVariant(forceInt(self.cmbType.currentIndex())))
        return record
