# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtGui, QtCore

from library.Utils                       import forceRef, forceString, forceBool, forceInt, forceStringEx
from library.TreeModel                   import CTreeModel, CTreeItem

import re

class CQueryFieldsTreeModel(CTreeModel):
    u"""
    Модель для дверовидного списка таблиц и полей в них. А так же для подключения дополнительных таблиц по определённым полям
    """
    def __init__(self, parent):
        CTreeModel.__init__(self, parent, CQueryFieldsHeadTreeItem(None, u'все', '', 0,  self))
        self.tableTableName     = 'rcTable'
        self.tableFieldName     = 'rcField'
        self.idColName          = 'id'
        self.groupColName       = 'rcTable_id'
        self.nameColName        = 'name'
        self.refColName         = 'ref_id'
        self.fieldColName       = 'field'
        self._filter            = None
        self.order              = self.nameColName
        self.leavesVisible      = False
        self._defaultRootItem   = self._rootItem
        self.rootItemVisible = False
        self._items = {}
        self._tables = {}
        self._modelParams = None
        self._modelFunctions = None

    def setModelParams(self, modelParams):
        self._modelParams = modelParams
        self.connect(self._modelParams, QtCore.SIGNAL('modelDataChanged()'), self.addItemsFromModelParams)
        self.addItemsFromModelParams()

    def setModelFunctions(self, modelFunctions):
        self._modelFunctions = modelFunctions
        self.addItemsFromModelFunctions()

    def addItemsFromModelParams(self):
        if not self._modelParams:
            return
        params = self._modelParams.getParams()
        self._rootItem.deleteItemsByType('param')
        for code, param in params.items():
            self._rootItem.addItem(u'@%s' % param.get('name'), param.get('code'), u'@%s' % param.get('id'), 'param')

    def addItemsFromModelFunctions(self):
        if not self._modelFunctions:
            return
        functions = self._modelFunctions._items
        self._rootItem.deleteItemsByType('func')
        for code, func in functions.items():
            self._rootItem.addItem(u'$%s' % func.get('name'), func.get('function'), u'$%s' % func.get('id'), 'func', comment=func.get('description', u''))

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

    def getItemById(self, itemId):
        return self._rootItem.getItemById(itemId)

    def loadItems(self):
        u"""
        Загрузка данных в модель
         _tables - данные о таблицах
         _items - данные о полях с сылкой на таблицы
        """
        self._items = {}
        self._tables = {}
        db = QtGui.qApp.db
        tableTable = db.table(self.tableTableName)
        tableField = db.table(self.tableFieldName)

        cond = []
        if tableField.hasField('deleted'):
            cond.append(tableField['deleted'].eq(0))

        cols = ['id',
                'name',
                'field',
                'rcTable_id',
                'ref_id',
                'description',
                'visible'
                ]

        recordList = db.getRecordList(tableField, cols, cond, order=self.order)
        for record in recordList:
            visible = forceBool(record.value('visible'))
            if not visible:
                continue
            self._items[forceString(record.value('id'))] = {
                'name'   : forceString(record.value('name')),
                'field': forceString(record.value('field')),
                'tableId': forceRef(record.value('rcTable_id')),
                'refId': forceString(record.value('ref_id')),
                'description': forceString(record.value('description')),
                'visible': forceBool(record.value('visible'))
             }

        cond = []
        if tableTable.hasField('deleted'):
            cond.append(tableTable['deleted'].eq(0))
        cols = [tableTable['id'],
                tableTable['name'],
                tableTable['table'],
                tableTable['group']
                ]
        recordList = db.getRecordList(tableTable, cols, cond)
        for record in recordList:
            self._tables[forceRef(record.value('id'))] = {
                'table': forceString(record.value('table')),
                'tableName'  : forceString(record.value('name')),
                'group'  : forceString(record.value('group')),
            }

    def loadChildrenItems(self, head):
        u"""
        Подгрузка дочерних элементов к элементу head
        @param head: элемент дерева
        @type head: CQueryFieldsTreeItem
        @return: список из CQueryFieldsTreeItem
        """
        if not self._items:
            self.loadItems()
        result = []
        for tableId, table in self._tables.items():
            tableItem = CQueryFieldsTreeItem(head, table['tableName'], table['table'], tableId, self, True)
            tableItem._items = []
            for itemId, item in self._items.items():
                if tableId == item.get('tableId', 0):
                    tableItem._items.append(CQueryFieldsTreeItem(tableItem, item['name'], item['field'], itemId, self, comment=item.get('description', u'')))
            result.append(tableItem)
        return result

    def extendItem(self, index, type='inner'):
        u"""
        Вызов загрузки дочерних элементов и создание дупликата
        @param index: индекс элемента
        @type index: QModelIndex
        @param type: значения ['inner', 'left', 'right'] параметр JOIN'а при подключении дополнительной таблицы
        """
        item = index.internalPointer()
        item._items = self.loadReferenceItems(item)
        item._type = type
        self.addItemDuplicated(item)

    def diconnectChildItem(self, index):
        u"""
        Отключение дополнительной таблицы
        @param index: индекс элемента
        @type index: QModelIndex
        """
        item = index.internalPointer()
        item._items = []
        item.type = u''

    def addSubQuery(self, subQueryId):
        u"""
        Добавление подзапроса.
            Загрузка подзапроса. Добавление полей из подзапроса в _items. Загрузка полей в основное дерево.
        @param subQueryId: - id подзапроса в таблице rcQuery
        @type subQueryId: int
        @return: CQueryFieldsTreeItem - элемент который отвечает за подзапрос
        """
        from Reports.ReportsConstructor.RCInfo import CRCQueryInfo
        query = CRCQueryInfo(self, self._modelParams, subQueryId)
        query._load()
        index = self.getIndexByPath(query._referencedField)
        child = index.internalPointer()
        if not child:
            return None
        tableId = self._items.get(child._baseId, {}).get('tableId', 0)
        item = index.internalPointer()._parent
        childField = child._id if forceString(tableId)[0] =='q' else child._field

        queryId = u'q%s' % forceString(query._id)
        subQueryColsInfo = {}
        for record in query.modelCols._items:
            subQueryColsInfo[forceInt(record.value('number'))] = {
                'field': forceString(record.value('field')),
                'name': forceString(record.value('alias')) if forceString(record.value('alias')) else query.modelTree.parcePathToTableNames(forceString(record.value('field'))),
                'id': u'f%d' % forceRef(record.value('id'))
            }
        self._tables[queryId] = {
            'table': queryId,
            'tableName': query._name
            }
        self._items[queryId] = {
            'field': childField,
            'name': query._name,
            'refId': subQueryColsInfo.get(1, {}).get('id', u'0'),
            'tableId': tableId
        }
        for colInfo in subQueryColsInfo.values():
            self._items[colInfo.get('id', u'')] = {
                'field': colInfo.get('field', u''),
                'name': self.parcePathToTableNames(colInfo.get('name', u'')),
                'refId': u'0',
                'tableId': queryId
            }
        newItem = CQueryFieldsTreeItem(item, query._name, childField, queryId, self, comment=u'%s: %s' % (childField, child._name))
        item._items.append(newItem)
        return newItem

    def changeSubQuery(self, subQueryId, currentIndex):
        u"""
        Изменение подзапроса.
            Загрузка подзапроса. Добавление полей из подзапроса в _items. Загрузка полей в основное дерево.
        @param subQueryId: - id подзапроса в таблице rcQuery
        @type subQueryId: int
        @param currentIndex: индекс элемента, на который подключён текущий подзапрос
        @type currentIndex: QModelIndex
        @return: dict с данными о элементе, к которому подключён позапрос
        """
        from Reports.ReportsConstructor.RCInfo import CRCQueryInfo
        query = CRCQueryInfo(self, self._modelParams, subQueryId)
        query._load()
        currentItem = currentIndex.internalPointer()
        index = self.getIndexByPath(query._referencedField)
        child = index.internalPointer()
        if not child:
            return None
        tableId = self._items.get(child._baseId, {}).get('tableId', 0)
        childField = child._id if forceString(tableId)[0] =='q' else child._field

        queryId = u'q%s' % forceString(query._id)
        subQueryColsInfo = {}
        for record in query.modelCols._items:
            subQueryColsInfo[forceInt(record.value('number'))] = {
                'field': forceString(record.value('field')),
                'name': forceString(record.value('alias')) if forceString(record.value('alias')) else query.modelTree.parcePathToTableNames(forceString(record.value('field'))),
                'id': u'f%d' % forceRef(record.value('id'))
            }
        self._tables[queryId] = {
            'table': queryId,
            'tableName': query._name
            }
        self._items[queryId] = {
            'field': childField,
            'name': query._name,
            'refId': subQueryColsInfo.get(1, {}).get('id', u'0'),
            'tableId': tableId
        }

        hasChild = forceBool(currentItem._items)
        for item in currentItem._items:
            itemInfo = self._items[item.baseId()]
            if itemInfo.get('refId') and itemInfo.get('ref_id') != u'0':
                subQueryColsInfo[item._id] = itemInfo
        currentItem._items = []
        for id, item in self._items.items():
            if item.get('tableId') == queryId:
                self._items.pop(id)

        for colInfo in subQueryColsInfo.values():
            self._items[colInfo.get('id', u'')] = {
                'field': colInfo.get('field', u''),
                'name': self.parcePathToTableNames(colInfo.get('name', u'')),
                'refId': colInfo.get('refId', u'0'),
                'tableId': colInfo.get('tableId', queryId)
            }
        currentItem._comment = u'%s: %s' % (childField, child._name)
        currentItem._field = childField
        if hasChild:
            currentItem._items = self.loadReferenceItems(currentItem)
        return self._items[queryId]

    def addItemDuplicated(self, item, row=None):
        u"""
        Добавление дубликата элемента с увелиением счётчика
        Поле
        Поле2
        Поле3
        @param item: элемент дерева, к которому подключён текущий подзапрос
        @type item: CQueryFieldsTreeItem
        @param row: номер строки в списке родителя
        @type row: int
        """
        if not item:
            return None
        parent = item._parent
        itemInfo = self._items.get(item.baseId(), {})
        if not row:
            for idx, child in enumerate(parent._items):
                if child._id == item._id:
                    row = idx
        if not row:
            return None
        newItem = CQueryFieldsTreeItem(parent, itemInfo.get('name', u''), itemInfo.get('field', u''), item.baseId(), self, comment=item._comment, number=item._number + 1)
        parent._items = parent._items[:row + 1] + [newItem] + parent._items[row + 1:]
        return newItem

    def loadReferenceItems(self, reference):
        u"""
        Загрузка элементов из таблицы, на поле который ссылается ref_id
        @param reference:
        @type reference:
        @return: список CQueryFieldsTreeItem - список подключаемых жлементов
        """
        result = []
        refItem = self._items.get(reference.baseId(), {})
        referencedItem = self._items.get(refItem.get('refId', 0), {})
        tableId = referencedItem.get('tableId', '')
        if not tableId:
            return result
        for itemId, item in self._items.items():
            if item.get('tableId', 0) == tableId:
                result.append(CQueryFieldsTreeItem(reference, item['name'], item['field'], itemId, self, comment=item.get('description', u'')))
        return result

    def getState(self):
        u"""
         Получить текущее состояние дерева.
         Например:
         i797 ( i65 i89 ) i796 ( i986 ) i783 iq6 ( iq7 )
         , где:
         [i, r, l] - типо подключения [inner, left, right] oin
         797 - id поля {rcField}
         q7 - id позапроса {rcQuery}
         @return: состояние записаное в unicode
        """
        return self.getRootItem().getReferencedChildren()

    def setState(self, state):
        u"""
        Установить состояние:
            - парсим состояние в дерево
            - затем применяем
        @param state: состояние, его стркутура описана в методе getState
        @type state: unicode
        """
        stateList = state.split(' ')
        self.acceptState(self.parceState(stateList))

    def getTableLinksFromState(self, stateTree, item=None):
        u"""
        Получаем из состояния дерево вида:
        {
            table: str,
            field: str,
            refTable: str
            refField: str,
            type: [inner, left, right]
        }: [{}, {}]
        @return: dict
        """
        if not isinstance(stateTree, dict):
            stateTree = self.parceState(stateTree.split(' '))
        if not item:
            item = self.getRootItem()
        result = []
        typeTranslate = {
            u'l': 'left',
            u'i': 'inner',
            u'r': 'right'
        }
        for id, state in stateTree.items():
            match = re.search('(\w)((\w?\d+)(:\d+)?)', id)
            if not match:
                return
            child = item.getItemById(match.groups()[1])
            childInfo = self._items.get(child.baseId(), {})
            refInfo = self._items.get(childInfo.get('refId', u''), {})
            childTable = u'%s%s' % (self._tables.get(childInfo.get('tableId'), {}).get('table'), u'' if item._number == 1 else u'[%d]' % item._number)
            refTable = u'%s%s' % (self._tables.get(refInfo.get('tableId'), {}).get('table'), u'' if child._number == 1 else u'[%d]' % child._number)
            type = typeTranslate.get(match.groups()[0], 'inner')
            result.append(({'table': childTable,
                           'field': childInfo.get('field', u''),
                           'refTable': refTable,
                           'refField': refInfo.get('field', u''),
                           'type': type
                           }, self.getTableLinksFromState(state, child) if child else []))
        if item._isTable:
            result = ({'table': self._tables.get(item._id, {}).get('table')}, result)
        return result

    def acceptState(self, stateTree, item=None):
        u"""
        Применение состояния. к полям подгружаем поля из подзапросов и присоединённых таблиц
        """
        if not item:
            item = self.getRootItem()
        if not item._items:
            return
        typeTranslate = {
            u'l': 'left',
            u'i': 'inner',
            u'r': 'right'
        }
        for id, state in stateTree.items():
            match = re.search('(\w)((\w?\d+)(:\d+)?)', id)
            if not match:
                return
            child = item.getItemById(match.groups()[1])
            if not child:
                subQueryIdMatch = re.search('q(\d+)', match.groups()[1])
                if subQueryIdMatch:
                    child = self.addSubQuery(subQueryIdMatch.groups()[0])
                else:
                    child = self.addItemDuplicated(self.getItemById(match.groups()[2]))
            if child:
                child._type = typeTranslate.get(match.groups()[0], 'inner')
                child.loadReferenceItems()
                self.acceptState(state, child)
        self.reset()

    def parceState(self, stateList):
        u"""
            Из списка собирает дерево
        """
        result = {}
        currentValue = None
        enter = 0
        for index, value in enumerate(stateList):
            if value == '(':
                if index:
                    if not enter:
                        result[currentValue] = self.parceState(stateList[index:])
                    enter += 1
            elif value == ')':
                if currentValue:
                    result.setdefault(currentValue, {})
                if not enter:
                    return result
                enter -= 1
            else:
                if not enter:
                    if currentValue:
                        result.setdefault(currentValue, {})
                    currentValue = forceString(value)
        if currentValue:
            result.setdefault(currentValue, {})
        return result

    def setMainTableId(self, id):
        self._rootItem.deleteItemsByType('param')
        self._rootItem.deleteItemsByType('func')
        self._rootItem = self._defaultRootItem
        if not self.getRootItem().items():
            self.getRootItem().update()
        for table in self.getRootItem().items():
            if table.id() == forceInt(id):
                self._rootItem = table
        self.addItemsFromModelParams()
        self.addItemsFromModelFunctions()

    def getItem(self, index):
        item = index.internalPointer()
        if not item:
            return None
        path = [forceString(item.id())]
        parent = self.parentByItem(item).internalPointer()
        while parent and parent.id() and not parent.isTable():
            parentItem = self._items.get(parent.baseId(), {})
            refId = parentItem.get('refId', 0)
            path.append(u'.')
            path.append(forceString(refId))
            if parent._type == 'left':
                path.append(u'|')
            else:
                path.append(u'.')
            path.append(forceString(parent.id()))
            parent = self.parentByItem(parent).internalPointer()
        return u'{%s}' % u''.join(path[::-1])

    def getIndexByPath(self, path):
        path = self.forceList(path)[::2]
        row, found, item = self.getRootItem().findItemByPath(path)
        return self.createIndex(row, 0, item)

    def forceList(self, path, withSeparetor=False):
        result = []
        if isinstance(path, str) or isinstance(path, unicode):
            if withSeparetor:
                result = re.split('([\.|])', path[1:-1])
            else:
                result = re.split('[\.|]', path[1:-1])
        elif isinstance(path, list):
            result = path
        return result

    def forceString(self, path):
        result = u''
        if isinstance(path, str) or isinstance(path, unicode):
            result = path
        elif isinstance(path, list):
            result = u'{%s}' % u'.'.join([str(id) for id in path])
        return result

    def parcePath(self, path): #path = []
        wordList = self.getWordList(path)
        pattern = re.compile('\{(\w?\d+(:\d)?)([\.|](\w?\d+(:\d)?))*\}')
        additionalList = []
        for idx, word in enumerate(wordList):
            if re.search(pattern, word):
                result = []
                pathList = self.forceList(word, withSeparetor=True)
                number = 1
                addAlias = 0
                for id in pathList:
                    if id == '|':
                        result.append('|')
                        continue
                    elif id == '.':
                        result.append(' ')
                        continue
                    item = self.getItemById(id)
                    if item == None:
                        raise ValueError(u"Ошибка при обработке поля '%s'" % (self.parcePathToTableNames(path)))
                    itemInfo = self._items.get(item.baseId())
                    tableId = itemInfo.get('tableId', 0)
                    table = self._tables.get(tableId, {})
                    if addAlias:
                        tableName = u'%s[%d]' %(table.get('table', ''), number)
                        addAlias -= 1
                    else:
                        tableName = table.get('table', '')
                    if item._number != 1:
                        number = item._number
                        addAlias = 2
                    result.append(u'.'.join([tableName, itemInfo.get('field', '')]))
                additionalList.append(u''.join(result))
                wordList[idx] = u'{%d}' % (len(additionalList) - 1)
        return u''.join(wordList), additionalList

    def getWordList(self, text):
        if not text:
            return []
        text = u' %s ' % text.replace(u'\n', ' ')
        charListToInsertSpace = [u'(', u')', u',', u'*', u'/', u'+', u'-', u'=', u'>', u'>']
        for char in charListToInsertSpace:
            text = text.replace(char, ' %s ' %char)
        text = text.replace('}', '} ')
        text = text.replace(u'}{', u'} {')
        match = re.search('[^a-zA-Z](IN)', text)
        if match:
            text = u''.join([text[:match.regs[1][0]], u' IN ', text[match.regs[1][1]:]])
        replaceSubstr = {}
        for subStr in re.findall('\'[^\'.]*\'', text):
            key = '{#%d}' % len(replaceSubstr.keys())
            text = text.replace(subStr, key)
            replaceSubstr[key] = subStr
        return [replaceSubstr.get(word, word) for word in text.split(' ') if word]

    def getFieldListFromString(self, text):
        result = []
        wordList = self.getWordList(text)
        pattern = re.compile('\{[0-9]+(\.[0-9]+)*\}')
        for word in wordList:
            match = re.search(pattern, word)
            if match:
                result.append(match.group())
        return result

    def parcePathToTableNames(self, path): #path = [] or str
        wordList = self.getWordList(path)
        patternField = re.compile('\{([a-z]?\d+(:\d)?)([\.|]([a-z]?\d+(:\d)?))*\}')
        patternParam = re.compile('\{@\d+\}')
        patternFunc = re.compile('\{\$\d+\}')
        newWordList = []
        for idx, word in enumerate(wordList):
            result = []
            if re.search(patternField, word):
                pathList = self.forceList(word)
                for index,id in enumerate(pathList[:-1]):
                    if not index % 2:
                        item = self.getItemById(id)
                        result.append(item._name if item else u'')
                item = self._items.get(pathList[-1], {})
                result.append(item.get('name', ''))
                wordList[idx] = u'.'.join(result)
                newWordList.append(u'.'.join(result))
            elif re.search(patternParam, word):
                id = word[1:-1]
                item = self._items.get(id, {})
                wordList[idx] = item.get('name', '')
                newWordList.append(item.get('name', ''))
            elif re.search(patternFunc, word):
                id = word[1:-1]
                item = self._items.get(id, {})
                wordList[idx] = item.get('name', '')
                newWordList.append(item.get('name', ''))
            elif word in ['-', 'IN', '=', '+', '/', '']:
                newWordList.append(u' ')
                newWordList.append(word)
                newWordList.append(u' ')
            elif word in [',', ')']:
                newWordList.append(word)
                newWordList.append(u' ')
            else:
                newWordList.append(word)

        return u''.join(newWordList)

    def parceTableNamesToPath(self, text):
        wordList = self.getWordList(text)
        for idx, word in enumerate(wordList):
            result = []
            tableNamesList = word.split('.')
            tableName = self.forceString(self.getRootItem().getPathByTableNames(tableNamesList))
            if tableName and tableName != u'{None}':
                wordList[idx] = tableName
        return u''.join(wordList)

    def checkItemHasReference(self, id):
        return forceBool(self._items.get(id, {}).get('refId') != u'0') and forceBool(self._items.get(id, {}).get('refId'))

    def data(self, index, role):
        if index.isValid():
            item = index.internalPointer()
            column = index.column()
            row = index.row()
            if not item:
                return QtCore.QVariant()
            if role == QtCore.Qt.DisplayRole:
                return item.data(column)
            elif role == QtCore.Qt.ForegroundRole:
                return item.color()
            elif role == QtCore.Qt.BackgroundColorRole:
                return item.backgroundColor()
            elif role == QtCore.Qt.ToolTipRole:
                return item.toolTip()
        return QtCore.QVariant()

class CQueryFieldsTreeItem(CTreeItem):
    def __init__(self, parent, name, field, id, model, isTable=False, type='', comment='', number=1):
        CTreeItem.__init__(self, parent, name)
        self.model = model
        self._field = field
        self._id = id
        self._baseId = id
        self._isTable = isTable
        self._selected = False
        self._type = type
        self._comment = comment
        self._number = number
        self.setName()

    def setName(self):
        if self._number != 1:
            self._name = u'%s%d' % (self._name, self._number)
            self._field = u'%s%d' % (self._field, self._number)
            self._id = u'%s:%d' % (self._id, self._number)

    def getNumber(self):
        return self._number

    def update(self):
        pass

    def loadChildren(self):
        return []

    def id(self):
        return self._id

    def baseId(self):
        return self._baseId

    def tableId(self):
        result = forceInt(self._id)
        matchId = re.search('\w?(\d+)', self._id)
        if matchId:
            result = forceInt(matchId.groups()[0])
        return result

    def isTable(self):
        return self._isTable

    def field(self):
        return self._field

    def loadReferenceItems(self):
        self._items = self.model.loadReferenceItems(self)

    def getReferencedChildren(self):
        result = [u'%s%s' %('l' if self._type == 'left' else 'i', forceString(self._id))]
        children = []
        if not self._items:
            return u''
        for item in self._items:
            if item._items:
                children.append(item.getReferencedChildren())
        if self._isTable:
            return u' '.join(children)
        if children:
            result.append(u'( %s )'%(u' '.join(children)))
        return u' '.join(result)

    def findItemByPath(self, path):
        rowCount = 0
        found = True
        if not path:
            return rowCount, found, self
        for row, item in enumerate(self._items):
            if item._id == path[0]:
                rowCount, found, foundItem = item.findItemByPath(path[1:])
                if foundItem == item:
                    rowCount = row
                if found:
                    return rowCount, found, foundItem
        found = False
        return rowCount, found, None

    def getPathByTableNames(self, tableNames):
        currentTableName = tableNames[0]
        result = []
        for child in self._items:
            if forceStringEx(child._name).lower() == forceStringEx(currentTableName).lower():
                id = child._id
                refId = self.model._items.get(id, {}).get('refId', 0)
                result.append(id)
                if refId:
                    result.append(refId)
                if len(tableNames) == 1:
                    result = [id]
                else:
                    result += child.getPathByTableNames(tableNames[1:])
                return result if result else [None]
        return [None]

    def setSelected(self, val):
        self._selected = val

    def selected(self):
        return self._selected

    def backgroundColor(self):
        if self._selected:
            return QtCore.QVariant(QtGui.QColor(0, 200, 200))
        return QtCore.QVariant()

    def color(self):
        hasReferense = self.model.checkItemHasReference(self._baseId)
        if hasReferense and self._items:
            if self._type == 'left':
                return QtCore.QVariant(QtGui.QBrush(QtGui.QColor(0, 200, 200)))
            return QtCore.QVariant(QtGui.QBrush(QtGui.QColor(0, 255, 0)))
        elif hasReferense:
            return QtCore.QVariant(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
        return QtCore.QVariant()

    def toolTip(self):
        if self._comment:
            return QtCore.QVariant(self._comment)
        return QtCore.QVariant()

    def addItem(self, name, field, id, type, comment=u''):
        child = CQueryFieldsTreeItem(self, name, field, id, self.model, type=type, comment=comment)
        if self._items:
            self._items.append(child)
        self.model._items.update({id: {'name': name, 'field': field}})

    def deleteItemsByType(self, type):
        if self._items:
            for index, item in enumerate(self._items):
                item.deleteItemsByType(type)
            self._items = [item for index, item in enumerate(self._items) if not item._type == type]

    def getItemById(self, itemId):
        if not self._items:
            return None
        for item in self._items:
            if item._id == itemId:
                return item
            found = item.getItemById(itemId)
            if found:
                return found
        return None

class CQueryFieldsHeadTreeItem(CQueryFieldsTreeItem):
    def __init__(self, parent, name, field, id, model, isTable=False, comment=u''):
        CQueryFieldsTreeItem.__init__(self, parent, name, field, id, model, isTable, comment)

    def loadChildren(self):
        return self.model.loadChildrenItems(self)

    def update(self):
        self._items = self.loadChildren()