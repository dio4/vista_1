# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from library.interchange            import getComboBoxValue, getLineEditValue, setComboBoxValue, setLineEditValue
from library.ItemsListDialog        import CItemsListDialog,  CItemEditorBaseDialog
from library.TableModel             import CEnumCol, CTextCol

from RefBooks.Tables                import rbCode, rbName, TempInvalidTypeList

from Ui_RBTempInvalidDocumentEditor import Ui_RBTempInvalidDocumentEditorDialog


class CRBTempInvalidDocumentList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CEnumCol(u'Класс',        ['type'], TempInvalidTypeList, 10),
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            ], 'rbTempInvalidDocument', ['type', rbCode, rbName])
        self.setWindowTitleEx(u'Типы документов ВУТ, инвалидности или ограничения жизнедеятельности')

    def getItemEditor(self):
        return CRBTempInvalidDocument(self)


class CRBTempInvalidDocument(CItemEditorBaseDialog, Ui_RBTempInvalidDocumentEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rbTempInvalidDocument')
        self.setupUi(self)
        self.setWindowTitleEx(u'Тип документа ВУТ, инвалидности или ограничения жизнедеятельности')
        self.cmbType.addItems(TempInvalidTypeList)


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setComboBoxValue(self.cmbType, record, 'type')
        setLineEditValue(self.edtCode, record, 'code')
        setLineEditValue(self.edtName, record, 'name')


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getComboBoxValue(self.cmbType, record, 'type')
        getLineEditValue(self.edtCode, record, 'code')
        getLineEditValue(self.edtName, record, 'name')
        return record