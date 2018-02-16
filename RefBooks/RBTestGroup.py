# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from library.interchange     import getLineEditValue, getRBComboBoxValue, setLineEditValue, setRBComboBoxValue
from library.ItemsListDialog import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel      import CRefBookCol, CTextCol

from RefBooks.Tables         import rbCode, rbName

from Ui_RBTestGroupEditor    import Ui_RBTestGroupEditor


class CRBTestGroupList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            CRefBookCol(u'Группа', ['group_id'], 'rbTestGroup', 15)
            ], 'rbTestGroup', [rbCode, rbName])
        self.setWindowTitleEx(u'Группы показателей исследований')

    def getItemEditor(self):
        return CRBTestGroupEditor(self)


class CRBTestGroupEditor(CItemEditorBaseDialog, Ui_RBTestGroupEditor):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rbTestGroup')
        self.setupUi(self)
        self.cmbGroup.setTable('rbTestGroup', addNone=True)
        self.setWindowTitleEx(u'Группа показателей исследований')
        self.setupDirtyCather()
        
        
    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(self.edtCode, record, rbCode)
        setLineEditValue(self.edtName, record, rbName)
        setRBComboBoxValue(self.cmbGroup, record, 'group_id')


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(self.edtCode, record, rbCode)
        getLineEditValue(self.edtName, record, rbName)
        getRBComboBoxValue(self.cmbGroup, record, 'group_id')
        return record
        
        
        
        
        
        
        
        
        
        
