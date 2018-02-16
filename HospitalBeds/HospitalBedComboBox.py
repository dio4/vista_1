# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################


from PyQt4 import QtCore, QtGui

from library.TreeModel  import CTreeModel, CTreeItemWithId
from library.Utils      import forceBool, forceInt, forceRef, forceString, toVariant


class CHospitalBedTreeItem(CTreeItemWithId):
    def __init__(self, parent, id, code, name, isBusy):
        CTreeItemWithId.__init__(self, parent, name, id)
        self._code = code
        self._isBusy = isBusy
        self._items = []


    def flags(self):
        return QtCore.Qt.NoItemFlags if self._isBusy else (QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)


    def data(self, column):
        if column == 0 :
            s = self._name
            return toVariant(s)
        else:
            return QtCore.QVariant()


    def sortItems(self):
        pass


    def sortKey(self):
        return (2, self._code, self._name, self._id)


class CHospitalBedOrgStructureTreeItem(CTreeItemWithId):
    def __init__(self, parent, name):
        CTreeItemWithId.__init__(self, parent, name, None)
        self._items = []

    def flags(self):
        return QtCore.Qt.ItemIsEnabled

    def sortItems(self):
        self._items.sort(key=lambda item: item.sortKey())
        for item in self._items:
            item.sortItems()

    def sortKey(self):
        return (1, self._name)


class CHospitalBedRootTreeItem(CTreeItemWithId):
    def __init__(self, filter=None):
        if not filter:
            filter = {}
        CTreeItemWithId.__init__(self, None, '-', None)
        self._classesVisible = False
        self.filter = filter
        self.domain = self.filter.get('domain', '')
        self.plannedEndDate = self.filter.get('plannedEndDate', QtCore.QDate())
        self.orgStructureId = self.filter.get('orgStructureId', None)


    def loadChildren(self):
        mapOrgStructureIdToTreeItem = {}
        result = []
        orgStructureIdList = []

        def getOrgStructureTreeItem(orgSructureId):
            if orgSructureId in mapOrgStructureIdToTreeItem:
                item = mapOrgStructureIdToTreeItem[orgSructureId]
            else:
                record = QtGui.qApp.db.getRecord('OrgStructure', 'name, parent_id', orgSructureId)
                name = forceString(record.value('name'))
                parentId = forceRef(record.value('parent_id'))
                if parentId:
                    parentItem = getOrgStructureTreeItem(parentId)
                    item = CHospitalBedOrgStructureTreeItem(parentItem, name)
                    parentItem._items.append(item)
                else:
                    parentItem = self
                    item = CHospitalBedOrgStructureTreeItem(parentItem, name)
                    result.append(item)
                mapOrgStructureIdToTreeItem[orgSructureId] = item
            return item

        db = QtGui.qApp.db
        if self.orgStructureId:
            orgStructureIdList = db.getDescendants('OrgStructure', 'parent_id', self.orgStructureId)
        tableHospitalBed = db.table('vHospitalBed')
        tableOrgStructure = db.table('OrgStructure')
        table = tableHospitalBed.leftJoin(tableOrgStructure, tableOrgStructure['id'].eq(tableHospitalBed['master_id']) )
        if orgStructureIdList:
            cond = [tableOrgStructure['id'].inlist(orgStructureIdList)]
        else:
            cond = [tableOrgStructure['organisation_id'].eq(QtGui.qApp.currentOrgId())]
        sex = self.filter.get('sex', 0)
        if sex:
            cond.append(db.joinOr([tableHospitalBed['sex'].eq(sex), tableHospitalBed['sex'].eq(0)]))
        ageForBed = self.filter.get('ageForBed', 0)
        ageToBed = self.filter.get('ageToBed', 0)
        if ageToBed > 0 and ageForBed <= ageToBed:
            ageForBedCount = ageForBed
            if ageForBed == 0:
                ageList = [u'']
            else:
                ageList = []
            while ageForBedCount <= ageToBed:
                ageList.append(str(ageForBedCount))
                ageForBedCount += 1
            cond.append(tableHospitalBed['age'].inlist(ageList))
        profileBed = self.filter.get('profileBed', None)
        if profileBed:
            cond.append(tableHospitalBed['profile_id'].eq(profileBed))
        typeBed = self.filter.get('typeBed', None)
        if typeBed:
            cond.append(tableHospitalBed['type_id'].eq(typeBed))
        isPermanentBed = self.filter.get('isPermanentBed', 0)
        if isPermanentBed:
            cond.append(tableHospitalBed['isPermanent'].eq(isPermanentBed-1))
        query = db.query(db.selectStmt(table, [tableHospitalBed['id'], tableHospitalBed['code'], tableHospitalBed['name'], tableHospitalBed['master_id'], tableHospitalBed['isBusy'], tableHospitalBed['involution'], tableHospitalBed['sex'], tableHospitalBed['age'], tableHospitalBed['isPermanent']], where=cond, order=tableHospitalBed['code'].name()))
        while query.next():
            record = query.record()
            id   = forceInt(record.value('id'))
            code = forceString(record.value('code'))
            name = forceString(record.value('name'))
            isBusy = forceBool(record.value('isBusy'))
            involution = forceInt(record.value('involution'))
            sex = forceInt(record.value('sex'))
            age = forceString(record.value('age'))
            isPermanent = u'[ш] 'if forceBool(record.value('isPermanent')) else u'[]'
            orgSructureId = forceString(record.value('master_id'))
            orgSructureItem = getOrgStructureTreeItem(orgSructureId)
            if isBusy and self.plannedEndDate and self.domain == u'busy':
                isBusy = self.getBusyForPlanning(isBusy, id)
            if involution > 0:
                isBusy = True
            strSexAge = isPermanent + code + u' ' + name
            sexage = u'('
            if sex:
                sexage += [u'', u'М', u'Ж'][sex] + (u', ' if age else '')
            if age:
                sexage += age
            if sex or age:
                strSexAge = isPermanent + code + name + sexage + u')'
            name = strSexAge
            orgSructureItem._items.append(CHospitalBedTreeItem(orgSructureItem, id, code, name, isBusy))

        result.sort(key=lambda item: item._name)
        for item in result:
            item.sortItems()
        return result


    def getBusyForPlanning(self, isBusy, hospitalBedId = None):
        if hospitalBedId:
            db = QtGui.qApp.db
            tableAPHB = db.table('ActionProperty_HospitalBed')
            tableAPT = db.table('ActionPropertyType')
            tableAP = db.table('ActionProperty')
            tableActionType = db.table('ActionType')
            tableAction = db.table('Action')
            tableOSHB = db.table('OrgStructure_HospitalBed')
            cols = [tableAction['id']]
            queryTable = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
            queryTable = queryTable.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
            queryTable = queryTable.innerJoin(tableAP, tableAP['type_id'].eq(tableAPT['id']))
            queryTable = queryTable.innerJoin(tableAPHB, tableAPHB['id'].eq(tableAP['id']))
            queryTable = queryTable.innerJoin(tableOSHB, tableOSHB['id'].eq(tableAPHB['value']))

            cond = [ tableOSHB['id'].eq(hospitalBedId),
                     tableActionType['flatCode'].like(u'moving%'),
                     tableAction['deleted'].eq(0),
                     tableAP['deleted'].eq(0),
                     tableActionType['deleted'].eq(0),
                     tableAPT['typeName'].like('HospitalBed'),
                     tableAP['action_id'].eq(tableAction['id'])
                   ]
            cond.append(u'Action.plannedEndDate != 0')
            cond.append(tableAction['plannedEndDate'].eq(self.plannedEndDate))
            records = db.getIdList(queryTable, cols, cond)
            if records:
                return False
        return isBusy


class CHospitalBedModel(CTreeModel):
    def __init__(self, parent=None, filter=None):
        if not filter:
            filter = {}
        CTreeModel.__init__(self, parent, CHospitalBedRootTreeItem(filter))


#    def headerData(self, section, orientation, role):
#        if role == QtCore.Qt.DisplayRole:
#            return QtCore.QVariant(u'-')
#        return QtCore.QVariant()


class CHospitalBedPopupView(QtGui.QTreeView):
    def __init__(self, parent):
        QtGui.QTreeView.__init__(self, parent)
        self.header().hide()
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setMinimumHeight(150)
        self.connect(self, QtCore.SIGNAL('expanded(QModelIndex)'), self.onExpanded)
        self.searchString = ''
        self.searchParent = None

    def setRootIndex(self, index):
        pass

    def setRealRootIndex(self, index):
        QtGui.QTreeView.setRootIndex(self, index)

    def onExpanded(self, index):
        self.scrollTo(index, QtGui.QAbstractItemView.PositionAtTop)

    def keyPressEvent(self, evt):
        if evt.key() == QtCore.Qt.Key_Space:
            self.emit(QtCore.SIGNAL('hide()'))
            evt.accept()
        else:
            super(CHospitalBedPopupView, self).keyPressEvent(evt)


class CHospitalBedComboBox(QtGui.QComboBox):
    def __init__(self, parent):
        QtGui.QComboBox.__init__(self, parent)
        self.SizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.setModelColumn(0)
#        self.__searchString = ''
        self._model = CHospitalBedModel(self)
        self.setModel(self._model)
        self._popupView = CHospitalBedPopupView(self)
        self._popupView.setObjectName('popupView')
        self._popupView.setModel(self._model)
        self.setView(self._popupView)
        self._popupView.installEventFilter(self)
        self._popupView.viewport().installEventFilter(self)
        QtCore.QObject.connect(self._popupView, QtCore.SIGNAL('activated(QModelIndex)'), self.on_ItemActivated)
        QtCore.QObject.connect(self._popupView, QtCore.SIGNAL('entered(QModelIndex)'), self.setCurrentIndex)
        self.prefferedWidth = 0

    def setPrefferedWidth(self, prefferedWidth):
        self.prefferedWidth = prefferedWidth


    def setValue(self, id):
        index = self._model.findItemId(id)
        self.setCurrentIndex(index)


    def value(self):
        modelIndex = self._model.index(self.currentIndex(), 0, self.rootModelIndex())
        if modelIndex.isValid():
            return self._model.itemId(modelIndex)
        return None


    def on_ItemActivated(self, index):
        if index.isValid():
            if (int(index.flags()) & QtCore.Qt.ItemIsSelectable) != 0 :
                self.hidePopup()
                self.emit(QtCore.SIGNAL('itemSelected(QModelIndex)'), index)
            else:
                self._popupView.setExpanded(index, not self._popupView.isExpanded(index))


    def showPopup(self):
#        self.__searchString = ''
        modelIndex = self._model.index(self.currentIndex(), 0, self.rootModelIndex())

        self._popupView.setRealRootIndex(QtCore.QModelIndex())
        self._popupView.expandAll()
        prefferedWidth = self._popupView.sizeHint().width()
        prefferedWidth = max(self.prefferedWidth if self.prefferedWidth else 0, self._popupView.sizeHint().width())
        if prefferedWidth:
            if self.width() < prefferedWidth:
                self._popupView.setFixedWidth(prefferedWidth)
        QtGui.QComboBox.showPopup(self)
        scrollBar = self._popupView.horizontalScrollBar()
        scrollBar.setValue(0)


    def setCurrentIndex(self, index):
        if not index:
            index = QtCore.QModelIndex()
        if index:
            self.setRootModelIndex(index.parent())
            QtGui.QComboBox.setCurrentIndex(self, index.row())

#        self.emit(QtCore.SIGNAL('codeSelected(QString)'), self._model.code(index))


    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress: # and obj == self.__popupView :
            if event.key() in [ QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return, QtCore.Qt.Key_Select ] :
                index = self._popupView.currentIndex()
                if index.isValid() and (int(index.flags()) & QtCore.Qt.ItemIsSelectable) != 0 :
                    self.hidePopup()
                    self.setCurrentIndex(index)
                    self.emit(QtCore.SIGNAL('itemSelected(QModelIndex)'), index)
                return True
            return False
        if event.type() == QtCore.QEvent.MouseButtonRelease and obj == self._popupView.viewport():
            self._popupView.mouseReleaseEvent(event)  # i1883.c12401 - нужна реакция на mouseRelease от QTreeView
            return True
        return False
