# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from PyQt4.QtCore import *
 
#############################################################################
##
## Copyright (C) 2012 Vista Software. All rights reserved.
##
#############################################################################

'''
Created on 30.10.2012

@author: atronah
@reason: issue 526
'''

from library.crbcombobox    import CRBComboBox
from library.InDocTable     import CInDocTableModel, CRBInDocTableCol, CIntInDocTableCol
from library.Utils          import forceInt, forceRef, toVariant


class CPrerecordQuotaModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'PersonPrerecordQuota', 'id', 'person_id', parent)
        self.addCol(CRBInDocTableCol(u'Тип квоты', 'quotaType_id', 20, 'rbPrerecordQuotaType', showFields = CRBComboBox.showName, addNone = False)).setReadOnly(True)
        self.addCol(CIntInDocTableCol(u'Значение', 'value', 20, low = 0, high = 100))
        self.disabledTypeIdList = []
        self.setEnableAppendLine(False)
        self.checkQuotesAndAddIfNotExist()
    
    
    ## Удаляет лишние квоты и добавляет отсутствующие
    def checkQuotesAndAddIfNotExist(self):
        isChanged = False
        tablePrerecordQuotaType = QtGui.qApp.db.table('rbPrerecordQuotaType')
        nonExistingQuotaTypeIdList = QtGui.qApp.db.getIdList(tablePrerecordQuotaType, 'id')
        for item in self.items():
            quotaTypeId = forceRef(item.value('quotaType_id'))
            if quotaTypeId in nonExistingQuotaTypeIdList:
                nonExistingQuotaTypeIdList.remove(quotaTypeId)
            else:
                isChanged = True
                self.items().remove(item)
        
        for quotaTypeId in nonExistingQuotaTypeIdList:
            isChanged = True
            defaultValue = QtGui.qApp.db.translate(tablePrerecordQuotaType, 'id', quotaTypeId, 'defaultValue')
            newRecord = self.getEmptyRecord()
            newRecord.setValue('quotaType_id', toVariant(quotaTypeId))
            newRecord.setValue('value', defaultValue)
            self.addRecord(newRecord)
        if isChanged:
            self.reset()
    
    
    def loadItems(self, masterId):
        CInDocTableModel.loadItems(self, masterId)
        self.checkQuotesAndAddIfNotExist()

    
    def setDisabledTypeCodes(self, disabledTypeCodeList):
        tablePrerecordQuotaType = QtGui.qApp.db.table('rbPrerecordQuotaType')
        self.disabledTypeIdList = QtGui.qApp.db.getIdList(tablePrerecordQuotaType, 'id', where = tablePrerecordQuotaType['code'].inlist(disabledTypeCodeList))
    
    
    def flags(self, index):
        row = index.row()
        editable = True
        if forceRef(self.value(row, 'quotaType_id')) in self.disabledTypeIdList:
            editable = False
        flags = CInDocTableModel.flags(self, index)
        if not editable:
            flags &= ~Qt.ItemIsEditable
        return flags

    
    def summaryQuota(self, excludedTypeCodeList=None):
        if not excludedTypeCodeList:
            excludedTypeCodeList = []
        summary = 0
        tablePrerecordQuotaType = QtGui.qApp.db.table('rbPrerecordQuotaType')
        excludedTypeIdList = QtGui.qApp.db.getIdList(tablePrerecordQuotaType, 'id', where = tablePrerecordQuotaType['code'].inlist(excludedTypeCodeList))
        for row in xrange(self.rowCount()):
            summary += forceInt(self.value(row, 'value')) if forceRef(self.value(row, 'quotaType_id')) not in excludedTypeIdList else 0
        return summary
    
    