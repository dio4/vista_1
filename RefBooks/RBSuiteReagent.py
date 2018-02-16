# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from library.InDocTable      import CInDocTableModel, CRBInDocTableCol
from library.interchange     import getDateEditValue, getLineEditValue, getRBComboBoxValue, getSpinBoxValue, \
                                    setDateEditValue, setLineEditValue, setRBComboBoxValue, setSpinBoxValue
from library.ItemsListDialog import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel      import CDateCol, CNumCol, CRefBookCol, CTextCol
from library.Utils           import forceRef

from Ui_RBSuiteReagentEditor import Ui_RBSuiteReagentEditorDialog


class CRBSuiteReagentList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',                          ['code'],               20),
            CTextCol(u'Наименование',                 ['name'],               40),
            CRefBookCol(u'Ответственный',             ['recipientPerson_id'], 'vrbPersonWithSpeciality', 10), 
            CDateCol(u'Дата выпуска',                 ['releaseDate'],        10), 
            CDateCol(u'Дата поступления',             ['supplyDate'],         12), 
            CDateCol(u'Дата передачи в работу',       ['startOperationDate'], 14), 
            CDateCol(u'Срок годности',                ['expiryDate'],         10),
            CNumCol(u'Плановое количество тестов',    ['planTestQuantity'],   15), 
            CNumCol(u'Выполненное количество тестов', ['execTestQuantity'],   15), 
            CTextCol(u'Производитель',                ['manufacturer'],       10), 
            CTextCol(u'Условия хранения',             ['storageConditions'],  12)
            ], 'SuiteReagent', ['code', 'name'])
        self.setWindowTitleEx(u'Наборы реагентов')

    def getItemEditor(self):
        return CRBSuiteReagentEditor(self)
        
        
class CRBSuiteReagentEditor(CItemEditorBaseDialog, Ui_RBSuiteReagentEditorDialog):
    def __init__(self, parent):
        CItemEditorBaseDialog.__init__(self, parent, 'SuiteReagent')
        self.setupUi(self)
        
        self.addModels('SuiteReagentTests', CSuiteReagentTestsModel(self))
        self.setModels(self.tblTests, self.modelSuiteReagentTests, self.selectionModelSuiteReagentTests)
        
        self.tblTests.addPopupDelRow()
        
        self.setWindowTitleEx(u'Набор реагентов')
        self.setupDirtyCather()
        self.setIsDirty(False)
        
    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(self.edtCode, record, 'code')
        setLineEditValue(self.edtName, record, 'name')
        setRBComboBoxValue(self.cmbRecipientPerson, record, 'recipientPerson_id')
        setDateEditValue(self.edtReleaseDate, record, 'releaseDate')
        setDateEditValue(self.edtSupplyDate, record, 'supplyDate')
        setDateEditValue(self.edtStartOperationDate, record, 'startOperationDate')
        setDateEditValue(self.edtExpiryDate, record, 'expiryDate')
        setSpinBoxValue(self.edtPlanTestQuantity, record, 'planTestQuantity')
        setLineEditValue(self.edtManufacturer, record, 'manufacturer')
        setLineEditValue(self.edtStorageConditions, record, 'storageConditions')
        
        self.modelSuiteReagentTests.loadItems(self.itemId())
        
    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(self.edtCode, record, 'code')
        getLineEditValue(self.edtName, record, 'name')
        getRBComboBoxValue(self.cmbRecipientPerson, record, 'recipientPerson_id')
        getDateEditValue(self.edtReleaseDate, record, 'releaseDate')
        getDateEditValue(self.edtSupplyDate, record, 'supplyDate')
        getDateEditValue(self.edtStartOperationDate, record, 'startOperationDate')
        getDateEditValue(self.edtExpiryDate, record, 'expiryDate')
        getSpinBoxValue(self.edtPlanTestQuantity, record, 'planTestQuantity')
        getLineEditValue(self.edtManufacturer, record, 'manufacturer')
        getLineEditValue(self.edtStorageConditions, record, 'storageConditions')
        return record
        
    def saveInternals(self, id):
        self.modelSuiteReagentTests.saveItems(id)
        
    def checkDataEntered(self):
        result = CItemEditorBaseDialog.checkDataEntered(self)
        if result:
            existsTestIdList = []
            for row, record in enumerate(self.modelSuiteReagentTests.items()):
                result = self.checkTestDataEntered(row, record, existsTestIdList)
                if not result:
                    break
        return result
        
    def checkTestDataEntered(self, row, record, existsTestIdList):
        result = True
        testId = forceRef(record.value('test_id'))
        if not testId :
            result = self.checkValueMessage(u'Необходимо указать тест', False, self.tblTests, row, 0)
        if result and testId in existsTestIdList:
            result = self.checkValueMessage(u'Тест уже связан с данным набором', False, self.tblTests, row, 0)
        if result:
            existsTestIdList.append(testId)
        return result
        
        
# #################################################

class CSuiteReagentTestsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'SuiteReagent_Test', 'id', 'master_id', parent)
        self.addCol(CRBInDocTableCol(   u'Тест',  'test_id',   10, 'rbTest', showFields=2))
        
