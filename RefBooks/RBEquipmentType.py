# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore

from library.interchange        import getLineEditValue, setLineEditValue
from library.ItemsListDialog    import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel         import CTextCol

from RefBooks.Tables            import rbCode, rbName, rbEquipmentType

from Ui_RBEquipmentTypeEditor   import Ui_RBEquipmentTypeEditorDialog


class CRBEquipmentTypeList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            ], rbEquipmentType, [rbCode, rbName])
        self.setWindowTitleEx(u'Типы оборудования')

    def getItemEditor(self):
        return CRBEquipmentTypeEditor(self)


class CRBEquipmentTypeEditor(CItemEditorBaseDialog, Ui_RBEquipmentTypeEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, rbEquipmentType)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Тип оборудования')
        self.setupDirtyCather()
        
        
    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(   self.edtCode,         record, 'code')
        setLineEditValue(   self.edtName,         record, 'name')

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(   self.edtCode,         record, 'code')
        getLineEditValue(   self.edtName,         record, 'name')
        return record
        
        
        
        
        
        
        
        
        
