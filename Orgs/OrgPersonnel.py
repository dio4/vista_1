# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from library.Utils import forceRef, forceString, formatShortName


class CPersonnelBaseTreeItem(object):
    def __init__(self, parent, name):
        self._parent = parent
        self._idList = []
        self._name = name
        self._items = []

    def addId(self, id):
        self._idList.append(id)
        if self._parent:
            self._parent.addId(id)

    def child(self, row):
        return self._items[row]

    def childCount(self):
        return len(self._items)

    def columnCount(self):
        return 1

    def data(self, column):
        if column == 0:
            return QtCore.QVariant(self._name)
        else:
            return QtCore.QVariant()

    def flags(self):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def parent(self):
        return self._parent

    def row(self):
        if self._parent:
            return self._parent._items.index(self)
        return 0

    def getItemIdList(self):
        return self._idList


class CPersonnelTreeItem(CPersonnelBaseTreeItem):
    def __init__(self, parent, name, personId):
        CPersonnelBaseTreeItem.__init__(self, parent, name)
        self.addId(personId)

    def childCount(self):
        return 0

    def findPersonId(self, personId):
        if personId in self._idList:
            return self
        return None


class CSpecTreeItem(CPersonnelBaseTreeItem):
    def findPersonId(self, personId):
        if personId in self._idList:
            for item in self._items:
                result = item.findPersonId(personId)
                if result:
                    return result
        return None


class CPersonnelRootTreeItem(CPersonnelBaseTreeItem):
    def __init__(self, orgId):
        CPersonnelBaseTreeItem.__init__(self, None, 'all')
        self.orderBySpeciality = True

    def setOrgStructureIdList(self, orgId, orgStructureIdList, date):
        self._items = []
        if orgStructureIdList:
            records = self.getRecordsByOrgStructuresAndSpecialities(orgId, orgStructureIdList, date, [])
            self.setItemsByRecords(records)

    def setOrgStructuresAndSpecialities(self, orgId, orgStructureIdList, date, specialityIdList):
        self._items = []
        records = self.getRecordsByOrgStructuresAndSpecialities(orgId, orgStructureIdList, date, specialityIdList)
        self.setItemsByRecords(records)

    def getRecordsByOrgStructuresAndSpecialities(self, orgId, orgStructureIdList, date, specialityIdList=None):
        if not specialityIdList:
            specialityIdList = []
        self._items = []
        db = QtGui.qApp.db
        tablePerson = db.table('Person')
        tablePersonAttach = db.table('PersonAttach')
        tableSpeciality = db.table('rbSpeciality')

        queryTable = tablePerson.leftJoin(tableSpeciality, tableSpeciality['id'].eq(tablePerson['speciality_id']))
        cond = [
            tablePerson['org_id'].eq(orgId),
            tablePerson['speciality_id'].isNotNull()
        ]
        if orgStructureIdList:
            attachCond = [
                tablePersonAttach['master_id'].eq(tablePerson['id']),
                tablePersonAttach['orgStructure_id'].inlist(orgStructureIdList),
                tablePersonAttach['deleted'].eq(0),
            ]
            if date:
                attachCond.extend([
                    tablePersonAttach['begDate'].dateLe(date),
                    db.joinOr([tablePersonAttach['endDate'].isNull(),
                               tablePersonAttach['endDate'].dateGe(date)])
                ])
            else:
                attachCond.extend([
                    tablePersonAttach['endDate'].isNull()
                ])

            cond.append(db.joinOr([db.existsStmt(tablePersonAttach, attachCond),
                                   tablePerson['orgStructure_id'].inlist(orgStructureIdList)]))
        if specialityIdList:
            cond.append(tablePerson['speciality_id'].inlist(specialityIdList))
        if date:
            cond.append(db.joinOr([tablePerson['retireDate'].isNull(),
                                   tablePerson['retireDate'].dateGe(date)]))

        idList = db.getDistinctIdList(queryTable, tablePerson['id'], cond)

        queryTable = tablePerson.leftJoin(tableSpeciality, tableSpeciality['id'].eq(tablePerson['speciality_id']))
        cols = [
            tableSpeciality['name'],
            tablePerson['lastName'],
            tablePerson['firstName'],
            tablePerson['patrName'],
            tablePerson['id']
        ]
        cond = [
            tablePerson['id'].inlist(idList)
        ]
        if self.orderBySpeciality:
            order = [col.name() for col in cols]
        else:
            order = [col.name() for col in cols[1:]]

        return db.getRecordList(queryTable, cols, cond, order)

    def setItemsByRecords(self, records):
        specItem = None
        for record in records:
            specName = forceString(record.value('name'))
            personId = forceRef(record.value('id'))
            personName = formatShortName(record.value('lastName'),
                                         record.value('firstName'),
                                         record.value('patrName'))
            if not specItem or specItem._name != specName:
                specItem = CSpecTreeItem(self, specName)
                self._items.append(specItem)
            specItem._items.append(CPersonnelTreeItem(specItem, personName, personId))

    def setActivityIdList(self, orgId, activityIdList, date):
        self._items = []
        if activityIdList:
            db = QtGui.qApp.db
            tablePersonActivity = db.table('Person_Activity')
            tablePerson = db.table('Person')
            tableSpeciality = db.table('rbSpeciality')
            queryTable = tablePerson.leftJoin(tableSpeciality, tableSpeciality['id'].eq(tablePerson['speciality_id']))
            queryTable = queryTable.leftJoin(tablePersonActivity, tablePersonActivity['master_id'].eq(tablePerson['id']))
            cols = [tableSpeciality['name'], tablePerson['lastName'], tablePerson['firstName'], tablePerson['patrName'], tablePerson['id']]
            if self.orderBySpeciality:
                order = [col.name() for col in cols]
            else:
                order = [col.name() for col in cols[1:]]
            cond = [tablePerson['org_id'].eq(orgId),
                    tablePersonActivity['activity_id'].inlist(activityIdList),
                    tablePerson['speciality_id'].isNotNull()]
            if date:
                cond.append(db.joinOr([tablePerson['retireDate'].isNull(),
                                       db.joinAnd([tablePerson['retireDate'].monthGe(date),
                                                   tablePerson['retireDate'].yearGe(date)])]))
            records = db.getRecordList(queryTable, cols, cond, order)
            self.setItemsByRecords(records)

    def findPersonId(self, personId):
        for item in self._items:
            result = item.findPersonId(personId)
            if result:
                return result
        return None


class COrgPersonnelModel(QtCore.QAbstractItemModel):
    def __init__(self, orgStructureIdList, parent=None):
        QtCore.QAbstractItemModel.__init__(self, parent)
        self._rootItem = CPersonnelRootTreeItem(orgStructureIdList)

    def getRootItem(self):
        return self._rootItem

    def setOrgStructureIdList(self, orgId, orgStructureIdList, date):
        self.getRootItem().setOrgStructureIdList(orgId, orgStructureIdList, date)
        self.reset()

    def setOrgStructuresAndSpecialities(self, orgId, orgStructureIdList, date, specialityIdList):
        self.getRootItem().setOrgStructuresAndSpecialities(orgId, orgStructureIdList, date, specialityIdList)
        self.reset()

    def setActivityIdList(self, orgId, activityIdList, date):
        self.getRootItem().setActivityIdList(orgId, activityIdList, date)
        self.reset()

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()

        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        item = index.internalPointer()
        return item.data(index.column())

    def flags(self, index):
        if not index.isValid():
            return 0
        item = index.internalPointer()
        return item.flags()

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(u'Персонал')
        return QtCore.QVariant()

    def index(self, row, column, parent):
        if not parent.isValid():
            parentItem = self.getRootItem()
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.getRootItem() or parentItem == None:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent and parent.isValid():
            parentItem = parent.internalPointer()
        else:
            parentItem = self.getRootItem()
        return parentItem.childCount()

    def findPersonId(self, personId):
        item = self.getRootItem().findPersonId(personId)
        if item:
            return self.createIndex(item.row(), 0, item)
        else:
            None

    def getItemIdList(self, index):
        item = index.internalPointer()
        if item:
            return item.getItemIdList()
        return []

    def getFirstLeafIndex(self):
        result = QtCore.QModelIndex()
        while self.rowCount(result):
            result = self.index(0, 0, result)
        return result


class CFlatPersonnelRootTreeItem(CPersonnelRootTreeItem):
    def __init__(self, orgId):
        CPersonnelRootTreeItem.__init__(self, orgId)
        self.orderBySpeciality = False

    def setItemsByRecords(self, records):
        specItem = None
        for record in records:
            specName = forceString(record.value('name'))
            personId = forceRef(record.value('id'))
            personName = formatShortName(record.value('lastName'),
                                         record.value('firstName'),
                                         record.value('patrName'))
            self._items.append(CPersonnelTreeItem(specItem, personName, personId))


class CFlatOrgPersonnelModel(COrgPersonnelModel):
    def __init__(self, orgStructureIdList, parent=None):
        COrgPersonnelModel.__init__(self, orgStructureIdList, parent)
        self._rootItem = CFlatPersonnelRootTreeItem(orgStructureIdList)
