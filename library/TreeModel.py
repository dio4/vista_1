# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from library.Utils import *

class CTreeItem(object):
    def __init__(self, parent, name):
        self._parent = parent
        self._name   = name
        self._items  = None


    def name(self):
        return self._name


    def child(self, row):
        items = self.items()
        if 0 <= row < len(items):
            return items[row]
        else:
            return None


    def childCount(self):
        return len(self.items())


    def isLeaf(self):
        return not bool(self.items())


    def columnCount(self):
        return 1


    def data(self, column):
        if column == 0 :
            return toVariant(self._name)
        else:
            return QtCore.QVariant()


    def flags(self):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable


    def parent(self):
        return self._parent


    def row(self):
        if self._parent and self._parent._items:
            return self._parent._items.index(self)
        return 0


    def items(self):
        if self._items is None:
            self._items = self.loadChildren()
        return self._items


    def update(self):
        self._items = self.loadChildren()


    def loadChildren(self):
        assert False, 'pure virtual call'

    ## Ищет элемент в дереве (текущем и дочерних элементах), для которого будет истинным значение переданного предиката сравнения.
    # @param predicat: функция или метод класса от одного аргумента, которая возвращает True, 
    #                  если переданный в нее аргумент удовлетворяет условию поиска, иначе возвращает False
    # @return: найденный объект или None, если не один из дочерних элементов не удовлетворяет предикату сравнения.
    def findItem(self, predicat):
        if predicat(self):
            return self
        for item in self.items():
            result = item.findItem(predicat)
            if result:
                return result
        return None


    def removeChildren(self):
        self._items  = None



#class CRootTreeItem(CTreeItem):
#    def __init__(self):
#        CTreeItem.__init__(self, None, '-')


class CTreeItemWithId(CTreeItem):
    def __init__(self, parent, name, itemId):
        CTreeItem.__init__(self, parent, name)
        self._id = itemId


    def id(self):
        return self._id


    def findItemId(self, itemId):
        if self._id == itemId:
            return self
        for item in self.items():
            result = item.findItemId(itemId)
            if result:
                return result
        return None


    def appendItemIds(self, l):
        if self._id:
            l.append(self._id)
        for item in self.items():
            item.appendItemIds(l)


    def getItemIdList(self):
        result = []
        self.appendItemIds(result)
        return result




class CTreeModel(QtCore.QAbstractItemModel):
    def __init__(self, parent, rootItem):
        QAbstractItemModel.__init__(self, parent)
        self._rootItem = rootItem
        self.rootItemVisible = True

    def setRootItem(self, rootItem):
        self._rootItem = rootItem
        self.reset()


    def getRootItem(self):
        return self._rootItem


    def setRootItemVisible(self, val):
        self.rootItemVisible = val
        self.reset()


    def columnCount(self, parent=QtCore.QModelIndex()):
        return 1


    def index(self, row, column, parent = QModelIndex()):
        if parent and parent.isValid():
            parentItem = parent.internalPointer()
            childItem = parentItem.child(row)
            return self.createIndex(row, column, childItem)
        elif self.rootItemVisible:
            return self.createIndex(0, 0, self.getRootItem())
        else:
            parentItem = self.getRootItem()
            childItem = parentItem.child(row)
            return self.createIndex(row, column, childItem)


    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()
        childItem = index.internalPointer()
        return self.parentByItem(childItem)


    def parentByItem(self, childItem):
        parentItem = childItem.parent() if childItem else None
        if not parentItem or (parentItem == self.getRootItem() and not self.rootItemVisible):
            return QtCore.QModelIndex()
        return self.createIndex(parentItem.row(), 0, parentItem)


    def rowCount(self, parent=QtCore.QModelIndex()):
        # if hasattr(QtGui.qApp, 'db') and QtGui.qApp.db is None:
        #     return 0
        if QtGui.qApp.db is not None and QtGui.qApp.db.isValid():
            if parent and parent.isValid():
                parentItem = parent.internalPointer()
                return parentItem.childCount() if 'childCount' in dir(parentItem) else 0
            elif self.rootItemVisible:
                return 1
            else:
                return self.getRootItem().childCount()
        else: return 0

    def data(self, index, role):
        if index.isValid() and (role == QtCore.Qt.DisplayRole or role == QtCore.Qt.ToolTipRole):
            item = index.internalPointer()
            if item:
                return item.data(index.column())
        return QtCore.QVariant()


    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        item = index.internalPointer()
        if not item:
            return Qt.NoItemFlags
        return item.flags()


    def findItem(self, predicat):
        item = self.getRootItem().findItem(predicat)
        if item:
            return self.createIndex(item.row(), 0, item)
        else:
            return None


    def findItemId(self, itemId):
        item = self.getRootItem().findItemId(itemId)
        if item and (self.rootItemVisible or item != self.getRootItem()):
            return self.createIndex(item.row(), 0, item)
        else:
            return None

    def getItemById(self, itemId):
        return self.getRootItem().findItemId(itemId)

    def getItemByIdEx(self, itemId):
        return self.getItemById(itemId)

    def itemId(self, index):
        item = index.internalPointer()
        return item._id if item else None


    def getItemIdList(self, index):
        result = []
        item = index.internalPointer()
        if item:
            item.appendItemIds(result)
        return result


    def isLeaf(self, index):
        if not index.isValid():
            return False
        item = index.internalPointer()
        return item.isLeaf()


    def updateItem(self, index):
        item = index.internalPointer()
        if item:
            item.update()


    def updateItemById(self, itemId):
        item = self.getRootItem().findItemId(itemId)
        if item:
            item.update()

    def emitDataChanged(self, group, row):
        index = self.createIndex(row, 0, group._items[row])
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)


class CDBTreeItem(CTreeItemWithId):
    def __init__(self, parent, name, itemId, model, childrenCount=None):
        CTreeItemWithId.__init__(self, parent, name, itemId)
        self.model = model
        self.childrenCount = childrenCount

    def childCount(self):
        if self.childrenCount is not None:
            return self.childrenCount
        else:
            return super(CDBTreeItem, self).childCount()

    def loadChildren(self):
        return self.model.loadChildrenItems(self)

    def update(self, light=False):
        u"""Модификатор light отключает подгрузку дочерних элементов из базы данных"""
        if self._items != None:
            newItems = self.loadChildren()
            if [ child._id for child in self._items ] == [ child._id for child in newItems ] :
                for i in xrange(len(self._items)):
                    if self._items[i]._name != newItems[i]._name:
                        self._items[i]._name = newItems[i]._name
                        self.model.emitDataChanged(self, i)
                    if not light:
                        self._items[i].update()
            else:
                index = self.model.createIndex(self.row(), 0, self)
                if self._items:
                    self.model.beginRemoveRows(index, 0, len(self._items)-1)
                    self._items = []
                    self.model.endRemoveRows()
                if newItems:
                    self.model.beginInsertRows(index, 0, len(newItems)-1)
                    self._items = newItems
                    self.model.endInsertRows()
                self.childrenCount = len(self._items)


class CDBTreeModel(CTreeModel):
    def __init__(self, parent, tableName, idColName, groupColName, nameColName, order=None, filters=None):
        CTreeModel.__init__(self, parent, CDBTreeItem(None, u'все', None, self))
        self.tableName = tableName
        self.idColName    = idColName
        self.groupColName = groupColName
        self.nameColName  = nameColName
        self._filter      = filters
        self.order = order if order else nameColName
        self.leavesVisible = False

    def setFilter(self, filters):
        if self._filter != filters:
            self._filter = filters
            self.reset()


    def setLeavesVisible(self, value):
        if self.leavesVisible != value:
            self.leavesVisible = value
            self.reset()


    def setOrder(self, order):
        if self.order != order:
            self.order = order
            self.reset()


    def update(self):
        self.getRootItem().update()
        #self.reset()

    def loadChildrenItems(self, group):
        db = QtGui.qApp.db
        table = db.table(self.tableName)
        children = table.alias(self.tableName + '_children')
        children_alias = table.alias(self.tableName+'_children2')
        alias = table.alias(self.tableName+'2')
        cond = [table[self.groupColName].eq(group.id())]
        if self._filter:
            cond.append(self._filter)
        if table.hasField('deleted'):
            cond.append(table['deleted'].eq(0))
        if not self.leavesVisible:
            cond.append(db.existsStmt(alias, alias[self.groupColName].eq(table[self.idColName])))
        recordList = db.getRecordList(table,
                                      [self.idColName, self.nameColName,
                                       '(' + db.selectStmt(children,
                                                           db.count('*'),
                                                           [
                                                               table[self.idColName].eq(children[self.groupColName]),
                                                               self._filter if self._filter else '1=1',
                                                               children['deleted'].eq(0) if children.hasField('deleted') else '1=1',
                                                               '1=1' if self.leavesVisible else db.existsStmt(children_alias, children_alias[self.groupColName].eq(children[self.idColName]))
                                                           ]) + ')'],
                                      cond,
                                      self.order)
        return self.getItemListByRecords(recordList, group)

    def getItemFromRecord(self, record, group):
        itemId   = forceRef(record.value(0))
        name = forceString(record.value(1))
        children = forceInt(record.value(2))
        return CDBTreeItem(group, name, itemId, self, children)

    def getItemListByRecords(self, recordList, group):
        result = []
        for record in recordList:
            item = self.getItemFromRecord(record, group)
            result.append(item)
        return result

    def emitDataChanged(self, group, row):
        index = self.createIndex(row, 0, group._items[row])
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)

    def dataChanged(self, group, row):
        index = self.createIndex(row, 0, group._items[row])
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)

    def findItemInParentById(self, parent, itemId):
        for i in parent.items():
            if i.id() == itemId:
                return i
        return None

    def findFirstLevelItemById(self, itemId):
        return self.findItemInParentById(self.getRootItem(), itemId)

    def getItemById(self, itemId):
        db = QtGui.qApp.db
        path = [itemId]
        child = itemId
        while True:
            rec = db.getRecord(self.tableName, [self.groupColName], child)
            if rec and forceRef(rec.value(self.groupColName)):
                path = [forceRef(rec.value(self.groupColName))] + path
                child = forceRef(rec.value(self.groupColName))
            else:
                break
        item = self.findFirstLevelItemById(path[0])
        while True:
            if item is None or item.id() == itemId:
                return item
            path = path[1:]
            if not path:
                return None
            item = self.findItemInParentById(item, path[0])


class CDragDropDBTreeModel(CDBTreeModel):
    u""" Модель дерева с возможностью таскать листики с ветку на ветку"""
    __pyqtSignals__ = ('saveExpandedState()',
                       'restoreExpandedState()')

    def __init__(self, parent, tableName, idColName, groupColName, nameColName, order=None):
        CDBTreeModel.__init__(self, parent, tableName, idColName, groupColName, nameColName, order)
        self.mapItemToId = {}

    def getItemByIdEx(self, itemId):
        return self.mapItemToId.get(itemId, None)

    def getItemIdListById(self, itemId, light=False):
        u"""Модификатор light отключает подгрузку дочерних элементов из базы данных"""
        item = self.getItem(itemId, light)
        result = []
        if item:
            item.appendItemIds(result)
        return result

    def getItem(self, itemId, light=False):
        u"""Модификатор light отключает подгрузку дочерних элементов из базы данных"""
        item = self.getItemByIdEx(itemId)
        if not item and not light:
            item = self.getItemById(itemId)
        return item

    def getItemListByRecords(self, recordList, group):
        result = []
        for record in recordList:
            item = self.getItemFromRecord(record, group)
            self.mapItemToId[item.id()] = item
            result.append(item)
        return result

    def supportedDropActions(self):
        return Qt.CopyAction | Qt.MoveAction


    def flags(self, index):
        defaultFlags = CDBTreeModel.flags(self, index)

        if index.isValid():
            return Qt.ItemIsDragEnabled | \
                   Qt.ItemIsDropEnabled | defaultFlags
        else:
            return Qt.ItemIsDropEnabled | defaultFlags


    def mimeTypes(self):
        types = QStringList()
        # передаем id элементов дерева в текстовом виде
        types.append('text/plain')
        return types


    def mimeData(self, index):
        mimeData = QMimeData()
        mimeData.setText(forceString(u','.join(map(str, map(self.itemId, index)))))
        return mimeData


    def dropMimeData(self, data, action, row, column, parentIndex):
        if action == Qt.IgnoreAction:
            return True

        if not data.hasText():
            return False

        dragIdString = forceString(data.text())
        dragIdList = dragIdString.split(',')
        parentId = self.itemId(parentIndex)

        self.changeParent(dragIdList, parentId)
        self.emit(SIGNAL('dataChanged(QModelIndex,QModelIndex)'), parentIndex, parentIndex)
        return True


    def changeParent(self,  itemIdList,  parentId):
        u"""Меняем у записи id родителя на parentId"""
        updateDict = {}
        lastKey = 0
        self.emit(SIGNAL('saveExpandedState()'))
        for i, itemId in enumerate(itemIdList):
            updateDict[i] = self.getItemByIdEx(forceInt(itemId)).parent()
            lastKey = i
            #light используется, для отключения подгузки элементов из бд и работы толькос загруженными
            #Нам этого достаточно, т.к. перетаскиваемые элементы уже загружены в модель
            if parentId in self.getItemIdListById(itemId, light=True):
                self.emit(SIGNAL('restoreExpandedState()'))
                return

        db = QtGui.qApp.db
        table = db.table(self.tableName)
        recordList = db.getRecordList(table,
                                      [self.idColName, self.groupColName],
                                      table[self.idColName].inlist(itemIdList))
        # На данный момент я считаю, что мы должны либо перенести все, либо не переносить ничего.
        if len(recordList) == len(itemIdList):
            # при последующем вызове reset дерево свернется в корень,
            # поэтому сигналим о необходимости сохранить его вид
            self.emit(SIGNAL('saveExpandedState()'))
            db.transaction()
            try:
                reload_items = []
                for record in recordList:
                    oldParentId = forceRef(record.value(self.groupColName))
                    record.setValue(self.groupColName, toVariant(parentId))
                    db.updateRecord(table, record)
                db.commit()
                self.getRootItem().removeChildren()
                self.reset()

                # i = 0
                # while i < len(updateDict.keys()) - 1:  # Сортировка для корректного обновления веток дерева
                #     j = i + 1                          # Порядок обновления от дочерних элементов к родительским
                #     work = True
                #     while j < len(updateDict.keys()) and work:
                #         parent = updateDict[i].parent()
                #         while not parent == updateDict[j] and parent:
                #             parent = parent.parent()
                #         if parent:
                #             updateDict[i].childrenCount -= 1
                #             updateDict[j].childrenCount += 1
                #             updateDict[i], updateDict[j] = updateDict[j], updateDict[i]
                #             # updateDict[i] - предыдущий parent
                #             # updateDict[j] - следующий parent
                #             work = False
                #         else:
                #             j += 1
                #     if work:
                #         i += 1
                #
                # for item in updateDict.values()[::-1]:
                #     item.update()
                #     if item.parent():
                #         item.parent().loadChildren()
                #     else:
                #         self.getRootItem().loadChildren()
            except:
                db.rollback()
                QtGui.qApp.logCurrentException()
                raise
            #сигналим о необходимости  восстановить вид дерева
            self.emit(SIGNAL('restoreExpandedState()'))


class CDBTreeItemWithClass(CDBTreeItem):
    def __init__(self, parent, name, itemId, className, model, isClass=False, childrenCount=None):
        CDBTreeItem.__init__(self, parent, name, itemId, model)
        self.className = className
        self.isClass = isClass
        self.childrenCount = childrenCount
       

    def row(self):
        if self._parent and self in self._parent._items:
            return self._parent._items.index(self)
        return 0


class CDragDropDBTreeModelWithClassItems(CDragDropDBTreeModel):
    mapClassItemsSourceByExists = {}
    def __init__(self, parent, tableName, idColName, groupColName, nameColName, classColName, order=None, dropToRootItem=True):
        CDragDropDBTreeModel.__init__(self, parent, tableName, idColName, groupColName, nameColName, order)
        self.classColName = classColName
        self.classItems = []
        self._classItemsSource = None
        self._availableItemIdList = None
        self.setRootItem(CDBTreeItemWithClass(None, u'Все', None, None, self, True))
        self.dropToRootItem = dropToRootItem

    def setAvailableItemIdList(self, idList):
        self._availableItemIdList = idList
        self.update()

    def setClassItems(self, items):
        self._classItemsSource = items
        rootItem = self.getRootItem()
        for name, val in items:
            self.classItems.append(CDBTreeItemWithClass(rootItem, name, None, val, self, True))

    def filterClassByExists(self, value):
        self.classItems = []
        if self._classItemsSource:
            if value:
                self.classItems = self._getClassItemsByExists()
            else:
                self.setClassItems(self._classItemsSource)
        self.reset()
            
            
    def _getClassItemsByExists(self):
        result = CDragDropDBTreeModelWithClassItems.mapClassItemsSourceByExists.get(self.tableName, None)
        if result is None:
            result = []
            for name, val in self._classItemsSource:
                if self._checkClassByExists(val):
                    result.append((name, val))
            CDragDropDBTreeModelWithClassItems.mapClassItemsSourceByExists[self.tableName] = tuple(result)
        
        rootItem = self.getRootItem()
        return [CDBTreeItemWithClass(rootItem, name, None, val, self, True) for name, val in result]
    
    
    def _checkClassByExists(self, _class):
        db = QtGui.qApp.db
        table = db.table(self.tableName)
        return bool(db.getCount(table, table['id'].name(), table['class'].eq(_class)))
        
    
    def loadChildrenItems(self, group):
        result = []
        if group == self.getRootItem():
            result = self.classItems
        else:
            db = QtGui.qApp.db
            table = db.table(self.tableName)
            children = table.alias(self.tableName + '_children')
            children_alias = table.alias(self.tableName+'_children2')
            alias = table.alias(self.tableName+'2')
            cond = [
                table[self.groupColName].eq(group.id()),
                table[self.classColName].eq(group.className)
            ]
            if table.hasField('deleted'):
                cond.append(table['deleted'].eq(0))
            if not self.leavesVisible:
                cond.append(db.existsStmt(alias, alias[self.groupColName].eq(table[self.idColName])))
            for record in db.getRecordList(table,
                                           [self.idColName, self.nameColName,
                                            '(' + db.selectStmt(children,
                                                                db.count('*'),
                                                                [
                                                                    table[self.idColName].eq(children[self.groupColName]),
                                                                    children[self.classColName].eq(group.className),
                                                                    children['deleted'].eq(0) if children.hasField('deleted') else '1=1',
                                                                    '1=1' if self.leavesVisible else db.existsStmt(children_alias, children_alias[self.groupColName].eq(children[self.idColName])),
                                                                    '1=1' if self._availableItemIdList is None else children['id'].inlist(self._availableItemIdList)
                                                                ]) + ')'],
                                           cond,
                                           self.order):
                itemId = forceRef(record.value(0))
                if (not self._availableItemIdList is None) and (itemId not in self._availableItemIdList):
                    continue
                name = forceString(record.value(1))
                childrenCount = forceInt(record.value(2))
                item = CDBTreeItemWithClass(group, name, itemId, group.className, self, childrenCount=childrenCount)
                self.mapItemToId[itemId] = item
                result.append(item)
        return result


    def itemClass(self, index):
        item = index.internalPointer()
        return item.className if item else None


    def flags(self, index):
        defaultFlags = CDBTreeModel.flags(self, index)
        item = index.internalPointer()
        if index.isValid() and not item.isClass:
            return Qt.ItemIsDragEnabled | \
                   Qt.ItemIsDropEnabled | defaultFlags
        elif index.isValid() and item.isClass and (item.parent() or self.dropToRootItem):
            return Qt.ItemIsDropEnabled | defaultFlags
        else:
            return defaultFlags


    def dropMimeData(self, data, action, row, column, parentIndex):
        if action == Qt.IgnoreAction:
            return True

        if not data.hasText():
            return False

        dragIdString = forceString(data.text())
        dragIdList = dragIdString.split(',')
        parentId = self.itemId(parentIndex)
        parentClass = self.itemClass(parentIndex)

        self.changeParent(dragIdList, parentId, parentClass)
        self.emit(SIGNAL('dataChanged(QModelIndex,QModelIndex)'), parentIndex, parentIndex)
        return True


    def changeParent(self,  itemIdList,  parentId, parentClass):
        updateDict = {}
        lastKey = 0
        for i, itemId in enumerate(itemIdList):
            updateDict[i] = self.getItemByIdEx(forceInt(itemId)).parent()
            lastKey = i
            #light используется, для отключения подгузки элементов из бд и работы толькос загруженными
            #Нам этого достаточно, т.к. перетаскиваемые элементы уже загружены в модель
            if parentId in self.getItemIdListById(itemId, light=True):
                return
        db = QtGui.qApp.db
        table = db.table(self.tableName)
        recordList = db.getRecordList(table,
                                      [self.idColName, self.groupColName, self.classColName],
                                      table[self.idColName].inlist(itemIdList))
        # На данный момент я считаю, что мы должны либо перенести все, либо не переносить ничего.
        if len(recordList) == len(itemIdList):
            self.emit(SIGNAL('saveExpandedState()'))
            db.transaction()
            try:
                for record in recordList:
                    record.setValue(self.groupColName, toVariant(parentId))
                    record.setValue(self.classColName, toVariant(parentClass))
                    db.updateRecord(table, record)
                for itemId in itemIdList:
                    self.setClass(parentClass, itemId)
                db.commit()
                self.reset()

                if parentId == None and not parentClass == None:
                    for item in self.classItems:
                        if item.className == parentClass:
                            newParentItem = item
                elif parentId:
                    newParentItem = self.getItemById(parentId)
                else:
                    newParentItem = self.getRootItem()
                updateDict[lastKey + 1] = newParentItem

                i = 0
                while i < len(updateDict.keys()) - 1: #Сортировка для корректного обновления веток дерева
                    j = i + 1                         #Порядок обновления от дочерних элементов к родительским
                    work = True
                    while j < len(updateDict.keys()) and work:
                        parent = updateDict[i].parent()
                        while not parent == updateDict[j] and parent:
                            parent = parent.parent()
                        if parent:
                            updateDict[i], updateDict[j] = updateDict[j], updateDict[i]
                            work = False
                        else:
                            j += 1
                    if work:
                        i += 1

                for item in updateDict.values()[::-1]:
                    item.update(light=True) #Используется update c модификатором light для отключения подгрузки дочерних элементов
            except:
                db.rollback()
                QtGui.qApp.logCurrentException()
                raise
            self.emit(SIGNAL('restoreExpandedState()'))

                
    def setClass(self, _class, itemId):
        db = QtGui.qApp.db
        table = db.table(self.tableName)
        idList = db.getDescendants(table, self.groupColName, itemId)
        if itemId in idList:
            idList.remove(itemId)
        if idList:
            expr = table[self.classColName].eq(_class)
            cond = table['id'].inlist(idList)
            stmt = 'UPDATE %s SET %s WHERE %s' % (self.tableName, expr, cond)
            db.query(stmt)

    def findFirstLevelItemById(self, itemId):
        for i in self.getRootItem().items():
            item = self.findItemInParentById(i, itemId)
            if item:
                return item
        return None
