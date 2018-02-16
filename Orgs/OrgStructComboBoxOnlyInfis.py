# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from random                import randint

from PyQt4                 import QtGui, QtCore

from library.DbEntityCache import CDbEntityCache
from library.TreeModel     import CTreeModel, CTreeItemWithId
from library.Utils         import forceBool, forceInt, forceLong, forceRef, forceString


class COrgStructureTreeItem(CTreeItemWithId):
    def __init__(self, parent, id, code, isArea, hasStocks, bookkeeperCode):
        CTreeItemWithId.__init__(self, parent, code, id)
        self._isArea = isArea
        self._hasStocks = hasStocks
        self._bookkeeperCode = bookkeeperCode


    def bookkeeperCode(self):
        return self._bookkeeperCode


    def isArea(self):
        return self._isArea


class COrgStructureTreePurpose:
    general = None
    areaSelector = 1
    storageSelector = 2


class COrgStructureRootTreeItem(COrgStructureTreeItem):
    @staticmethod
    def getCheckSum():
        query = QtGui.qApp.db.query('CHECKSUM TABLE OrgStructure')
        if query.next():
            return forceLong(query.record().value(1))
        else:
            return None


    def __init__(self, orgId, orgStructureId, emptyRootName, purpose, filter=None):
        if emptyRootName is None:
            emptyRootName = u'ЛПУ'
        COrgStructureTreeItem.__init__(self, None, # parent
                                             orgStructureId, # id
                                             #atronah: почему-то не получилось импортировать from Orgs.Utils import getOrgStructureName
                                             emptyRootName if not orgStructureId
                                                            else forceString(QtGui.qApp.db.translate('OrgStructure',
                                                                                                     'id',
                                                                                                     orgStructureId,
                                                                                                     'code')),
                                             False, False, u'')
        self.orgId = orgId
        self.emptyRootName = emptyRootName
        self.purpose = purpose
        self.filter = filter
        self.timestamp = None
        self.checkSum  = None


    def isObsolete(self):
        if self.timestamp and self.timestamp.secsTo(QtCore.QDateTime.currentDateTime()) > randint(300, 600): ## magic
            return self.checkSum != self.getCheckSum()
        else:
            return False


    def loadChildren(self):
        self.timestamp = QtCore.QDateTime.currentDateTime()
        self.checkSum = self.getCheckSum()


        if not self.orgId:
            self._items = []
            return self._items

        db = QtGui.qApp.db
        table = db.table('OrgStructure')
#        if self.purpose == COrgStructureTreePurpose.areaSelector:

        if self.filter:
            cond = self.filter
        else:
            cond = [table['deleted'].eq(0),
                    table['organisation_id'].eq(self.orgId)]

        if not isinstance(cond, list):
            cond = [cond]
        cond.append(table['type'].ne(99))


        mapIdToNodes = { None:(self.emptyRootName, False, False, u'') }
        mapParentIdToIdList = {}
        query = db.query(db.selectStmt(table, 'parent_id, id, code, isArea, hasStocks, bookkeeperCode', where=cond, order='code'))
        while query.next():
            record = query.record()
            parentId = forceRef(record.value('parent_id'))
            id   = forceInt(record.value('id'))
            code = forceString(record.value('code'))
            isArea = forceBool(record.value('isArea'))
            hasStocks = forceBool(record.value('hasStocks'))
            bookkeeperCode = forceString(record.value('bookkeeperCode'))
            mapIdToNodes[id] = code, isArea, hasStocks, bookkeeperCode
            idList = mapParentIdToIdList.setdefault(parentId, [])
            idList.append(id)

        if self.purpose == COrgStructureTreePurpose.areaSelector:
            filter = lambda node: node[1]
        elif self.purpose == COrgStructureTreePurpose.storageSelector:
            filter = lambda node: node[2]
        else:
            filter = None

        if filter:
            self._filterNodes(mapIdToNodes, mapParentIdToIdList, self._id, filter, set())
        self._code, self._isArea, self._hasStocks, self._bookkeeperCode = mapIdToNodes[self._id]
        self._generateItems(mapIdToNodes, mapParentIdToIdList, self, set())
        return self._items

    @staticmethod
    def _filterNodes(mapIdToNodes, mapParentIdToIdList, id, filter, visitedIdSet):
        if id not in visitedIdSet:
            visitedIdSet.add(id)
            idList = mapParentIdToIdList.get(id, None)
            if idList:
                idList = [ childId
                           for childId in idList
                           if COrgStructureRootTreeItem._filterNodes(mapIdToNodes, mapParentIdToIdList, childId, filter, visitedIdSet)
                         ]
                mapParentIdToIdList[id] = idList
            return bool(idList) or filter(mapIdToNodes[id])
        else:
            return False


    @staticmethod
    def _generateItems(mapIdToNodes, mapParentIdToIdList, item, visitedIdSet):
        id = item._id
        if id not in visitedIdSet:
            visitedIdSet.add(id)
            code, isArea, hasStocks, bookkeeperCode = mapIdToNodes[id]
            idList = mapParentIdToIdList.get(id, None)
            item._items = []
            if idList:
                for childId in idList:
                    code, isArea, hasStocks, bookkeeperCode = mapIdToNodes[childId]
                    childItem = COrgStructureTreeItem(item, childId, code, isArea, hasStocks, bookkeeperCode)
                    item._items.append(childItem)
                    COrgStructureRootTreeItem._generateItems(mapIdToNodes, mapParentIdToIdList, childItem, visitedIdSet)



class COrgStructureRootTreeItemsCache(CDbEntityCache):
    mapKeyToRootItem = {}

    @classmethod
    def purge(cls):
        cls.mapKeyToRootItem.clear()


    @classmethod
    def getItem(cls, orgId, orgStructureId, emptyRootName, purpose, filter=None):
        key = orgId, orgStructureId, emptyRootName, purpose
        result = cls.mapKeyToRootItem.get(key, None)
        if not result or result.isObsolete():
            orgStructureId = orgStructureId if not (hasattr(QtGui.qApp, 'isRestrictByUserOS')\
                                                    and QtGui.qApp.isRestrictByUserOS())\
                                            else QtGui.qApp.userOrgStructureId
            result = COrgStructureRootTreeItem(orgId, orgStructureId, emptyRootName, purpose, filter)
            cls.connect()
            cls.mapKeyToRootItem[key] = result
        return result


    @classmethod
    def getItemFromFilter(cls, orgId, orgStructureId, emptyRootName, purpose, filter=None):
        orgStructureId = orgStructureId if not (hasattr(QtGui.qApp, 'isRestrictByUserOS')\
                                                    and QtGui.qApp.isRestrictByUserOS())\
                                            else QtGui.qApp.userOrgStructureId
        result = COrgStructureRootTreeItem(orgId, orgStructureId, emptyRootName, purpose, filter)
        cls.connect()
        return result


class COrgStructureModel(CTreeModel):
    def __init__(self, parent, orgId=None, orgStructureId=None, emptyRootName=None, purpose=None, filter=None, headerName=u'Структура ЛПУ'):
        self.orgId = orgId
        self.orgStructureId = orgStructureId
        self.emptyRootName = emptyRootName
        self.purpose = purpose
        self.filter = filter
        self.headerName = headerName
        CTreeModel.__init__(self, parent, None)
        self.connect(QtGui.qApp, QtCore.SIGNAL('currentUserIdChanged()'), self.updateItems)


    def __del__(self):
        if QtGui.qApp:
            self.disconnect(QtGui.qApp, QtCore.SIGNAL('currentUserIdChanged()'), self.updateItems)
        if hasattr(super(COrgStructureModel, self), '__del__'):
            super(COrgStructureModel, self).__del__()


    def setFilter(self, newFillter):
        self.filter = newFillter
        self.updateItems()


    @QtCore.pyqtSlot()
    def updateItems(self):
        if self and QtGui.qApp.db and QtGui.qApp.db.db and QtGui.qApp.db.db.isOpen():
            del self._rootItem
            self._rootItem = None
            COrgStructureRootTreeItemsCache.purge()
            self.reset()


    def getRootItem(self):
        result = self._rootItem
        if not result:
            if self.filter:
                result = COrgStructureRootTreeItemsCache.getItemFromFilter(self.orgId, self.orgStructureId, self.emptyRootName, self.purpose, self.filter)
            else:
                result = COrgStructureRootTreeItemsCache.getItem(self.orgId, self.orgStructureId, self.emptyRootName, self.purpose, self.filter)
            self._rootItem = result
        return result


    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.headerName)
#            return QVariant(u'Структура ЛПУ')
        return QtCore.QVariant()


    def setOrgId(self, orgId=None, orgStructureId=None, emptyRootName=None):
        if ( self.orgId != orgId
             or self.orgStructureId != orgStructureId
             or self.emptyRootName != emptyRootName
           ):
            self.orgId = orgId
            self.orgStructureId = orgStructureId
            self.emptyRootName = emptyRootName
            if self._rootItem:
                self._rootItem = None
                self.reset()


    def setPurpose(self, purpose=None):
        if self.purpose != purpose:
            self.purpose = purpose
            if self._rootItem:
                self._rootItem = None
                self.reset()


    def orgId(self):
        return self.orgId


    def isArea(self, index):
        if not index.isValid():
            return False
        item = index.internalPointer()
        return item.isArea()

    def flags(self, index):
        flags = CTreeModel.flags(self, index)
        item = index.internalPointer()
        if not item.bookkeeperCode():
            flags = flags & ~QtCore.Qt.ItemIsEnabled
        return flags


class COrgStructurePopupView(QtGui.QTreeView):
    def __init__(self, parent):
        QtGui.QTreeView.__init__(self, parent)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setMinimumHeight(150)
        self.connect(self, QtCore.SIGNAL('expanded(QModelIndex)'), self.onExpanded)
#        self.connect(self, SIGNAL('collapsed(QModelIndex)'), self.onCollapsed)
        self.searchString = ''
        self.searchParent = None


#    def setModel(self, model):
#        QtGui.QTreeView.setModel(self, model)
#        self.expandAll()

    def setRootIndex(self, index):
        pass

    def setRealRootIndex(self, index):
        QtGui.QTreeView.setRootIndex(self, index)
#        self.expandAll()


    def onExpanded(self, index):
        self.scrollTo(index, QtGui.QAbstractItemView.PositionAtTop)



class COrgStructureComboBoxOnlyInfisEnabled(QtGui.QComboBox):
    def __init__(self, parent, emptyRootName=None, purpose=None, filter=None):
        QtGui.QComboBox.__init__(self, parent)
        self.SizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.setModelColumn(0)
#        self.__searchString = ''
        self._model = COrgStructureModel(self,
                                         orgId=QtGui.qApp.currentOrgId(),
                                         orgStructureId=None,
                                         emptyRootName=emptyRootName,
                                         purpose=purpose,
                                         filter=filter)
        self.setModel(self._model)
        self._popupView = COrgStructurePopupView(self)
        self._popupView.setObjectName('popupView')
        self._popupView.setModel(self._model)
        self.setView(self._popupView)
        self._popupView.installEventFilter(self)
        self._popupView.viewport().installEventFilter(self)
        QtCore.QObject.connect(self._popupView, QtCore.SIGNAL('activated(QModelIndex)'), self.on_ItemActivated)
        QtCore.QObject.connect(self._popupView, QtCore.SIGNAL('entered(QModelIndex)'), self.setCurrentIndex)
        self.setExpandAll(False)


    def setOrgId(self, orgId, orgStructureId=None, emptyRootName=None):
        currValue = self.value()
        self._model.setOrgId(orgId, orgStructureId=orgStructureId, emptyRootName=emptyRootName)
        self.setValue(currValue)


    def orgId(self):
        return self._model.orgId


    def setPurpose(self, purpose):
        currValue = self.value()
        self._model.setPurpose(purpose)
        self.setValue(currValue)


    def setValue(self, id):
        index = self._model.findItemId(id)
        if index:
            self.setCurrentIndex(index)


    def setExpandAll(self, value):
        self._expandAll = value


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
        def expandUp(index):
            while index.isValid():
                self._popupView.setExpanded(index, True)
                index = index.parent()

#        self.__searchString = ''
        modelIndex = self._model.index(self.currentIndex(), 0, self.rootModelIndex())
        self._popupView.setRealRootIndex(QtCore.QModelIndex())
        if self._expandAll:
            self._popupView.expandAll()
        else:
            if modelIndex and modelIndex.isValid():
                index = modelIndex.parent()
                expandUp(index)
            index = self._model.findItemId(QtGui.qApp.currentOrgStructureId())
            if index and index.isValid():
                index = index.parent()
                expandUp(index)
            self._popupView.setExpanded(self._model.index(0,0), True)
        QtGui.QComboBox.showPopup(self)
        self._popupView.header().hide()
#        self._popupView.setCurrentIndex(modelIndex)


    def setCurrentIndex(self, index):
        self.setRootModelIndex(index.parent())
        QtGui.QComboBox.setCurrentIndex(self, index.row())
#        self.emit(SIGNAL('codeSelected(QString)'), self._model.code(index))


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
        if obj == self._popupView.viewport() and not self._popupView.viewport().isVisible():
            return True
        return False

