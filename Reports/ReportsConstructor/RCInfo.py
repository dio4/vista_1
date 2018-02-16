# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui
from library.Utils import forceRef, forceString, forceInt
from models.RCTableModel                 import CRCColsModel, CRCTableCapModel, CRCParamsModel, CRCItemModel, CRCGroupsModel, CRCOrdersModel, CRCGroupItemModel
from models.RCFieldsTreeModel            import CQueryFieldsTreeModel
from models.RCConditionTreeModel         import CRCConditionTreeModel

class CRCQueryInfo(QtCore.QObject):
    def __init__(self, parent, modelParams, id):
        QtCore.QObject.__init__(self)
        self._parent = parent
        self.table = 'rcQuery'
        self._id = id
        self._record = None
        self._name = None
        self._referencedField = None
        self._tableId = None
        self._stateTree = None

        self.modelTree = None
        self.modelCols = None
        self.modelParams = None
        self.modelTableCap = None
        self.modelGroups = None
        self.modelOrders = None
        self.modelConditions = None
        self.modelFunctions = None

        self.modelParams = modelParams

    def _load(self):
        self._record = self.getRecord(self._id)
        if self._record:
            self._name = forceString(self._record.value('name'))
            self._tableId = forceInt(self._record.value('mainTable_id'))
            self._referencedField = forceString(self._record.value('referencedField'))
            self._stateTree = forceString(self._record.value('stateTree'))

            self.modelTree = CQueryFieldsTreeModel(self)
            self.modelCols = CRCColsModel(self, self.modelTree)
            self.modelGroups = CRCGroupsModel(self, self.modelTree)
            self.modelOrders = CRCOrdersModel(self, self.modelTree)
            self.modelConditions = CRCConditionTreeModel(self, self.modelTree, self.modelParams)
            self.modelFunctions = CRCItemModel(self, ['name', 'function', 'description', 'hasSpace'], 'rcFunction')

            self.modelFunctions.loadItems()
            self.modelTree.loadItems()

            self.modelTree.setModelParams(self.modelParams)
            self.modelTree.setModelFunctions(self.modelFunctions)
            self.modelTree.setMainTableId(self._tableId)
            self.modelTree.setState(forceString(self._record.value('stateTree')))
            self.modelCols.loadItems(self._id)
            self.modelGroups.loadItems(self._id)
            self.modelOrders.loadItems(self._id)
            self.modelConditions.loadItems(self._id)
            return True
        return False

    def getRecord(self, id):
        return QtGui.qApp.db.getRecord(self.table, '*', id)

class CRCReportInfo(QtCore.QObject):
    def __init__(self, parent, id):
        QtCore.QObject.__init__(self)
        self._parent = parent
        self.table = 'rcReport'
        self._id = id
        self._record = None
        self._referencedField = None
        self._stateTree = None
        self._query = None
        self._queryId = None
        self._name = u''
        self._tableId = None

        self.modelTree = None
        self.modelCols = None
        self.modelParams = None
        self.modelTableCapGroup = None
        self.modelTableCap = None
        self.modelGroups = None
        self.modelOrders = None
        self.modelConditions = None
        self.modelFunctions = None

    def _load(self):
        self._record = self.getRecord(self._id)
        if self._record:
            self.modelParams = CRCParamsModel(self)
            self.modelParams.loadItems(self._id)

            self._queryId = forceRef(self._record.value('query_id'))
            self._query = CRCQueryInfo(self, self.modelParams, self._queryId)
            if not self._query._load():
                return False
            self._name = forceString(self._record.value('name'))
            self._tableId = self._query._tableId
            self._referencedField = self._query._referencedField
            self._stateTree = self._query._stateTree

            self.modelTree = self._query.modelTree
            self.modelCols = self._query.modelCols
            self.modelConditions = self._query.modelConditions
            self.modelGroups = self._query.modelGroups
            self.modelOrders = self._query.modelOrders
            self.modelFunctions = self._query.modelFunctions

            self.modelTableCapGroup = CRCGroupItemModel(self)
            self.modelTableCapGroup.loadItems(self._id)
            self.modelTableCap = CRCTableCapModel(self, self.modelCols, self.modelGroups, self.modelTree)
            self.modelTableCap.loadItems(self._id)

            return True
        return False

    def getRecord(self, id):
        return QtGui.qApp.db.getRecord(self.table, '*', id)