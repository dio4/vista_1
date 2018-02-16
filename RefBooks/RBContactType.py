# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore
from library.ItemsListDialog         import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel              import CTextCol, CBoolCol
from library.Utils                   import forceStringEx, forceBool, forceString, toVariant

from RefBooks.Tables                 import rbCode, rbName, rbContactType, rbMask, rbMaskEnabled
from RefBooks.Ui_RBContactTypeEditor import Ui_ContractTypeEditorDialog


class CRBContactTypeList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',           [rbCode],    20),
            CTextCol(u'Наименование',  [rbName],    20),
            CTextCol(u'Маска',         [rbMask],    20),
            CBoolCol(u'Включить маску',[rbMaskEnabled], 10)
            ], rbContactType, [rbCode, rbName, rbMask, rbMaskEnabled, ])
        self.setWindowTitleEx(u'Способы связи с пациентом')

    def getItemEditor(self):
        return CRBContactTypeEditor(self)

class CRBContactTypeEditor(CItemEditorBaseDialog, Ui_ContractTypeEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, rbContactType)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Способ связи с пациентом')
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        self.edtCode.setText(forceString(record.value('code')))
        self.edtName.setText(forceString(record.value('name')))
        self.edtMask.setText(forceString(record.value('mask')))
        self.chkMaskEnabled.setChecked(forceBool(record.value('maskEnabled')))


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue('code',  toVariant(forceStringEx(self.edtCode.text())))
        record.setValue('name',  toVariant(forceStringEx(self.edtName.text())))
        record.setValue('mask',  toVariant(forceStringEx(self.edtMask.text())))
        record.setValue('maskEnabled',  toVariant(forceBool(self.chkMaskEnabled.isChecked())))
        return record
