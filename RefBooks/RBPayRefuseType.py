# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore

from library.ItemsListDialog    import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel         import CBoolCol, CRefBookCol, CTextCol
from library.Utils              import forceBool, forceInt, forceString, forceStringEx, toVariant

from RefBooks.Tables            import rbCode, rbName, rbFinance, rbPayRefuseType

from Ui_RBPayRefuseTypeEditor   import Ui_ItemEditorDialog


class CRBPayRefuseTypeList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CRefBookCol(u'Источник финансирования', ['finance_id'], rbFinance, 30),
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            CBoolCol(u'Возможно перевыставление',   ['rerun'], 10),

            ], rbPayRefuseType, [rbCode, rbName])
        self.setWindowTitleEx(u'Причины отказа платежа')

    def getItemEditor(self):
        return CRBPayRefuseTypeEditor(self)

#
# ##########################################################################
#

class CRBPayRefuseTypeEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, rbPayRefuseType)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Причина отказа платежа')
        self.cmbFinance.setTable(rbFinance, False)
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        self.cmbFinance.setValue(forceInt(record.value('finance_id')))
        self.edtCode.setText(forceString(record.value(rbCode)))
        self.edtName.setText(forceString(record.value(rbName)))
        self.chkCanRerun.setChecked(forceBool(record.value('rerun')))


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue('finance_id', toVariant(self.cmbFinance.value()))
        record.setValue(rbCode,       toVariant(forceStringEx(self.edtCode.text())))
        record.setValue(rbName,       toVariant(forceStringEx(self.edtName.text())))
        record.setValue('rerun',      toVariant(self.chkCanRerun.isChecked()))
        return record

