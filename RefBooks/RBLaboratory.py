# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from library.crbcombobox        import CRBComboBox
from library.InDocTable         import CInDocTableCol, CRBInDocTableCol, CInDocTableModel
from library.interchange        import getComboBoxValue, getLineEditValue, setComboBoxValue, setLineEditValue
from library.ItemsListDialog    import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel         import CTextCol

from RefBooks.Tables            import rbCode, rbName

from Ui_RBLaboratoryEditor      import Ui_LaboratoryEditorDialog


class CRBLaboratoryList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            ], 'rbLaboratory', [rbCode, rbName])
        self.setWindowTitleEx(u'Лабораторные информационные системы')

    def getItemEditor(self):
        return CRBLaboratoryEditor(self)

#
# ##########################################################################
#

class CRBLaboratoryEditor(CItemEditorBaseDialog, Ui_LaboratoryEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rbLaboratory')
        self.addModels('Tests', CTestsModel(self))
        self.setupUi(self)
        self.setModels(self.tblTests, self.modelTests, self.selectionModelTests)
        self.tblTests.addPopupDelRow()
        self.setWindowTitleEx(u'Лабораторная информационная система')
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(   self.edtCode,      record, 'code')
        setLineEditValue(   self.edtName,      record, 'name')
        setComboBoxValue(   self.cmbProtocol,  record, 'protocol')
        setLineEditValue(   self.edtAddress,   record, 'address')
        setLineEditValue(   self.edtOwnName,   record, 'ownName')
        setLineEditValue(   self.edtLabName,   record, 'labName')
        self.modelTests.loadItems(self.itemId())
        self.setIsDirty(False)


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(   self.edtCode,      record, 'code')
        getLineEditValue(   self.edtName,      record, 'name')
        getComboBoxValue(   self.cmbProtocol,  record, 'protocol')
        getLineEditValue(   self.edtAddress,   record, 'address')
        getLineEditValue(   self.edtOwnName,   record, 'ownName')
        getLineEditValue(   self.edtLabName,   record, 'labName')
        return record


    def saveInternals(self, id):
        self.modelTests.saveItems(id)


    def checkDataEntered(self):
        result = CItemEditorBaseDialog.checkDataEntered(self)
        return result


class CTestsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'rbLaboratory_Test', 'id', 'master_id', parent)
        self.addCol(CRBInDocTableCol(   u'Наименование',  'test_id', 20, 'rbTest', showFields = CRBComboBox.showNameAndCode))
        self.addCol(CInDocTableCol(     u'Справочник ЛИС',  'book', 20))
        self.addCol(CInDocTableCol(     u'Код ЛИС',         'code', 20))
#        self.setEnableAppendLine(True)