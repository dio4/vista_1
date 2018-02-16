# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui, QtSql

from library.Utils      import forceBool, forceDouble, forceInt, forceRef
from library.DialogBase import CDialogBase
from library.InDocTable import CRecordListModel, CBoolInDocTableCol, CFloatInDocTableCol, CRBInDocTableCol

from Ui_JobTypeActionsSelector import Ui_JobTypeActionsSelectorDialog


class CJobTypeActionsSelector(CDialogBase, Ui_JobTypeActionsSelectorDialog):
    def __init__(self, parent, jobTypeId, existsActionTypeIdList=None):
        if not existsActionTypeIdList:
            existsActionTypeIdList = []
        CDialogBase.__init__(self, parent)
        
        self._jobTypeId = jobTypeId
        
        self.addModels('ActionTypes', CJobTypeActionsSelectorModel(self, existsActionTypeIdList))
        
        self.setupUi(self)
        
        self.setModels(self.tblActionTypes, self.modelActionTypes, self.selectionModelActionTypes)
        
        self._load()
        
        self.setWindowTitle(u'Добавить действия')
        
    def _load(self):        
        self.modelActionTypes.loadItems(self._jobTypeId)


    def checkedItems(self):
        return self.modelActionTypes.checkedItems()

# #######################################################

class CJobTypeActionsSelectorModel(CRecordListModel):
    def __init__(self, parent, existsActionTypeIdList=None):
        if not existsActionTypeIdList:
            existsActionTypeIdList = []
        CRecordListModel.__init__(self, parent)
        self.addCol(CBoolInDocTableCol( u'Включить',      'checked',        10))
        self.addCol(CRBInDocTableCol(   u'Тип действия',  'actionType_id',  14, 'ActionType', showFields=2).setReadOnly())
        self.addCol(CFloatInDocTableCol(u'Количество',    'amount',         12, precision=2))
#        self.addCol(CIntInDocTableCol(  u'Группа выбора', 'selectionGroup', 12).setReadOnly())
        
        self._existsActionTypeIdList = existsActionTypeIdList
        
        self._cacheItemsByGroup = {}
        
        
    def loadItems(self, masterId):
        db = QtGui.qApp.db
        cols = ['id', 'master_id', 'actionType_id', 'selectionGroup']
        table = db.table('rbJobType_ActionType')
        cond = [table['master_id'].eq(masterId), 
                table['actionType_id'].notInlist(self._existsActionTypeIdList)]
        self._items = db.getRecordList(table, cols, cond, ['id'])
        for item in self._items:
            item.append(QtSql.QSqlField('checked', QtCore.QVariant.Bool))
            item.append(QtSql.QSqlField('amount',  QtCore.QVariant.Double))
            
            selectionGroup = forceInt(item.value('selectionGroup'))
            groupItemList = self._cacheItemsByGroup.setdefault(selectionGroup, [])
            groupItemList.append(item)
            
            if selectionGroup == 1 or (selectionGroup and len(groupItemList) == 1):
                item.setValue('checked', QtCore.QVariant(True))
    
        self.reset()
    
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.CheckStateRole and forceBool(value):
            row = index.row()
            item = self._items[row]
            selectionGroup = forceInt(item.value('selectionGroup'))
            if selectionGroup > 1:
                groupItemList = self._cacheItemsByGroup.get(selectionGroup, [])
                for item in groupItemList:
                    item.setValue('checked', QtCore.QVariant(False))
                self.emitColumnChanged(self.getColIndex('checked'))
        return CRecordListModel.setData(self, index, value, role)
    
    def checkedItems(self):
        return [(forceRef(item.value('actionType_id')), forceDouble(item.value('amount'))) for item in self._items if forceBool(item.value('checked'))]
