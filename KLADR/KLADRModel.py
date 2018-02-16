# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4            import QtCore, QtGui, QtSql

from KLADR.Utils      import prefixLen, fixLevel

from library.database import decorateString
from library.Utils    import forceInt, forceString, toVariant


tblKLADR  = 'kladr.KLADR'
tblSTREET = 'kladr.STREET'

class CKladrTreeItem(object):
    def __init__(self, code, name, status, level, index, parent, model, showOnlyInsuranceArea):
        self._model  = model
        self._parent = parent
        self._code   = code
        self._name   = name
        self._status = status
        self._showOnlyInsuranceArea = showOnlyInsuranceArea
        self._level  = fixLevel(code, level)
        self._index  = index
        self._items  = None
        self._itemsCount = None


    def child(self, row):
        if self._items == None:
            self._items = self.loadChildren()
            self._itemsCount = len(self._items)
        if 0 <= row < self._itemsCount:
            return self._items[row]
        else:
#            print 'bad row %d from %d' % (row, self._itemsCount)
            return None

    def items(self):
        if self._items == None:
            self._items = self.loadChildren()
        return self._items


    def childCount(self):
        if self._itemsCount == None:
            self._itemsCount = self.countChildren()
        return self._itemsCount


    def columnCount(self):
        return 1


    def data(self, column):
        if column == 0:
            return QtCore.QVariant(self._name)
        elif column == 1:
            return QtCore.QVariant(self._code)
        elif column == 2:
            return QtCore.QVariant(self.getPath())


    def flags(self):
        if ( self.childCount() > 0 and
             (self._status == 0 or self._status == 4)
             and not self._model.areaSelectable ):
            return QtCore.Qt.ItemIsEnabled
        else:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


    def parent(self):
        return self._parent


    def row(self):
        if self._parent:
            return self._parent._items.index(self)
        return 0


    def countChildren(self):
        result = 0
        if self._level < 4:
            pl = prefixLen(self._level)
            prefix = self._code[:pl]
            query = QtSql.QSqlQuery(QtGui.qApp.db.db)
            cond = u'AND isInsuranceArea = 1' if self._showOnlyInsuranceArea else u''
            stmt   = u'SELECT COUNT(CODE) FROM %s WHERE parent=\'%s\' AND RIGHT(CODE,2)=\'00\' %s' % (tblKLADR, prefix, cond)
###            print stmt
            if query.exec_(stmt) and query.next():
                record = query.record()
                result = forceInt(record.value(0))
        return result


    def loadChildren(self):
        result = []
        if self._level < 4:
            pl = prefixLen(self._level)
            prefix = self._code[:pl]
            query = QtSql.QSqlQuery(QtGui.qApp.db.db)
            cond = u'AND isInsuranceArea = 1' if self._showOnlyInsuranceArea else u''
            stmt   = u'SELECT CODE, NAME, SOCR, STATUS FROM %s WHERE parent=\'%s\' AND RIGHT(CODE,2)=\'00\' %s ORDER BY NAME, SOCR, CODE' % (tblKLADR, prefix, cond)
###            print stmt
            if query.exec_(stmt):
                i = 0
                while query.next():
                    record = query.record()
                    code   = forceString(record.value('CODE'))
                    name   = forceString(record.value('NAME'))
                    status = forceInt(record.value('STATUS'))
                    socr   = forceString(record.value('SOCR'))
                    # возможно, что правильнее анализировать ОКАТО:
                    # "4" в третьем разряде или "5"|"6" в шестом.
                    if status == 0 and (socr == u'г' or socr == u'пгт'):
                        status = 1
                    result.append(CKladrTreeItem(code, name+' '+socr, status, self._level+1, i, self, self._model, self._showOnlyInsuranceArea))
                    i += 1
            else:
                pass
        return result


    def getPath(self):
        path = []
        fox = self #atronah: почему переменная названа "лисой"??????????
        while fox._parent:
            path.insert(0, fox._name)
            #atronah: 2 строки ниже убрано в рамках i868
#            if fox._status == 2:
#                break
            fox = fox._parent
        return ', '.join(path)


    def findCode(self, code):
        shortCode = code[:11]
        query = QtSql.QSqlQuery(QtGui.qApp.db.db)
        cond = u'AND isInsuranceArea = 1' if self._showOnlyInsuranceArea else u''
        stmt   = u'SELECT parent FROM %s WHERE CODE LIKE \'%s%%\' %s LIMIT 1' % (tblKLADR, shortCode, cond)
        if query.exec_(stmt) and query.next():
            record = query.record()
            parentCode =  forceString(record.value('parent')).ljust(11, '0')
            if parentCode == '0'*11:
                parent = self
            else:
                parent = self.findCode(parentCode)

                # adres v kladre pomenjalsja
                # msg = QtGui.QMessageBox()
                # msg.setIcon(QtGui.QMessageBox.Information)
                # msg.setText(forceString("Адрес данного клиента поменялся в КЛАДРЕ").decode('utf-8'))
                # msg.setWindowTitle(forceString("Адрес клиента поменялся").decode('utf-8'))
                # msg.setDetailedText(forceString("Подробности:\n"
                #                                "По данным КЛАДР адрес, указанный у этого пациента, изменился. "
                #                                "Необходимо выбрать правильный адрес.").decode('utf-8'))
                # msg.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
                # msg.exec_()
                # parent = self


            n = parent.childCount()
            if n > 0:
                for i in xrange(n):
                    child = parent.child(i)
                    if child._code[:11] == shortCode:
                        return child
        return self


    def prefix(self):
        len = prefixLen(self._level)
        return self._code[:len]


    def keyboardSearch(self, search):
        h = self.childCount()-1
        if h:
            l = 0
            while 0<=l<=h:
                m = (l+h)/2
                c = cmp(self.child(m)._name.upper(), search)
                if c<0:
                    l = m+1
                elif c>0:
                    h = m-1
                else:
                    return m
            return min(l, self.childCount()-1)
        else:
            return -1


class CKladrRootTreeItem(CKladrTreeItem):
    def __init__(self, model, showOnlyInsuranceArea):
        CKladrTreeItem.__init__(self, '', '-', 0, 0, 0, None, model, showOnlyInsuranceArea)

    def flags(self):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


class CKladrTreeModel(QtCore.QAbstractItemModel):
    def __init__(self, parent=None, showOnlyInsuranceArea = False):
        QtCore.QAbstractItemModel.__init__(self, parent)
        self._rootItem = CKladrRootTreeItem(self, showOnlyInsuranceArea)
        self.areaSelectable = False
        self.isAllSelectable = False
        h = parent.fontMetrics().height() if parent else 14
        self.sizeHint = QtCore.QVariant(QtCore.QSize(h, h))

    def getRootItem(self):
        return self._rootItem

    def setAllSelectable(self, val):
        self.isAllSelectable = val

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 1

    def data(self, index, role=None):
        if not index.isValid() or index.internalPointer() == None:
            return QtCore.QVariant()
        elif role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            item = index.internalPointer()
            return QtCore.QVariant(item.data(index.column()))
        elif role == QtCore.Qt.SizeHintRole:
            return self.sizeHint

        return QtCore.QVariant()

    def flags(self, index):
        if not index.isValid():
            return 0
        item = index.internalPointer()
        if self.isAllSelectable:
            return item.flags() | QtCore.Qt.ItemIsSelectable
        return item.flags()

    def headerData(self, section, orientation, role):
        return QtCore.QVariant()

    def index(self, row, column, parent):
        if not parent or not parent.isValid():
            return self.createIndex(row, column, self.getRootItem())
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

        if parentItem == None:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent and parent.isValid():
            parentItem = parent.internalPointer()
            return parentItem.childCount()
        else:
            return 1

    def findCode(self, code):
        item = self.getRootItem().findCode(code)
        return self.createIndex(item._index, 0, item)

    def code(self, index):
        item = index.internalPointer()
        return item._code
        
    def getChildrenCodeList(self, code):
        def setChildrenColdeList(result, item):
            result.append(item._code)
            for item in item.items():
                setChildrenColdeList(result, item)
        result = []
        if code:
            index = self.findCode(code)
            if index and index.isValid():
                item = index.internalPointer()
                setChildrenColdeList(result, item)
        return result

    def keyboardSearch(self, parentIndex, search):
        parentItem = parentIndex.internalPointer()
        if not parentItem:
            parentItem = self.getRootItem()
        row = parentItem.keyboardSearch(search)
        return self.index(row, 0, parentIndex)


gKladrTreeModel = None
gAllSelectableKladrTreeModel = None
gInsuranceAreaTreeModel = None

def getKladrTreeModel():
    global gKladrTreeModel
    if gKladrTreeModel is None:
        gKladrTreeModel = CKladrTreeModel(None)
    return gKladrTreeModel

def getAllSelectableKladrTreeModel():
    global gAllSelectableKladrTreeModel
    if gAllSelectableKladrTreeModel is None:
        gAllSelectableKladrTreeModel = CKladrTreeModel(None)
        gAllSelectableKladrTreeModel.setAllSelectable(True)
    return gAllSelectableKladrTreeModel

def getInsuranceAreaTreeModel():
    global gInsuranceAreaTreeModel
    if gInsuranceAreaTreeModel is None:
        gInsuranceAreaTreeModel = CKladrTreeModel(None, True)
        gInsuranceAreaTreeModel.setAllSelectable(True)
    return gInsuranceAreaTreeModel

def getCityName(code):
    model = getKladrTreeModel()
    index = model.findCode(code)
    if index != None:
        item = index.internalPointer()
        return item.getPath()
    else:
        return '{%s}' % code


def getExactCityName(code):
    model = getKladrTreeModel()
    index = model.findCode(code)
    if index != None:
        item = index.internalPointer()
        return item._name
    else:
        return '{%s}' % code


def getMainRegionName(code):
    model = getKladrTreeModel()
    index = model.findCode(code)
    if index != None:
        item = index.internalPointer()
        while item._parent and not isinstance(item._parent, CKladrRootTreeItem):
            item = item._parent
        return item._name
    else:
        return '{%s}' % code


def getRegionName(code):
    model = getKladrTreeModel()
    index = model.findCode(code[:5].ljust(11, '0'))
    if index != None:
        item = index.internalPointer()
        return item._name
#        return item.getPath()
    else:
        return '{%s}' % code


def getOKATO(KLADRCode, KLADRStreetCode, number):
    db = QtGui.qApp.db
    stmt = 'SELECT `kladr`.`getOKATO`(%s, %s, %s)' % (
                decorateString(KLADRCode),
                decorateString(KLADRStreetCode),
                decorateString(number))
    try:
        query = db.query(stmt)
        if query.next():
            return forceString(query.record().value(0))
    except:
        pass
    return ''


def getDistrictName(KLADRCode, KLADRStreetCode, number):
    db = QtGui.qApp.db
    stmt = 'SELECT `kladr`.`getDistrict`(%s, %s, %s)' % (
                decorateString(KLADRCode),
                decorateString(KLADRStreetCode),
                decorateString(number))
    try:
        query = db.query(stmt)
        if query.next():
            return forceString(query.record().value(0))
    except:
        pass
    return ''






#######################################################################################


class CKLADRSearchModel(QtCore.QAbstractTableModel):
    def __init__(self, parent):
        QtCore.QAbstractListModel.__init__(self, parent)
        self.codes = []
        self.names = []
        self.indices = []
        self.rootCode = ''
        self.searchString = ''


    def columnCount(self, parent = QtCore.QModelIndex()):
        return 1


    def rowCount(self, parent = QtCore.QModelIndex()):
        return len(self.codes)


    def setFilter(self, rootCode, searchString):
        if self.rootCode != rootCode or self.searchString != searchString:
            db = QtGui.qApp.db
            table = db.table(tblKLADR)
            cond = ['RIGHT(CODE,2)=\'00\'']
            if rootCode:
                cond.append(table['CODE'].like(rootCode+'%'))
            if searchString:
                tempCond = []
                tempCond.append(table['NAME'].like(searchString))
                tempCond.append(table['INDEX'].like(searchString))
                #cond.append(db.joinOr(tempCond))
                cond.append("NAME LIKE '%%%s%%' OR KLADR.INDEX LIKE '%s%%'" % (searchString,  searchString))
            stmt = db.selectStmt(table,
                    'CODE, getTownName(CODE, 1) AS NAMEEX, KLADR.INDEX as INDEXEX',
                    cond,
                    order = 'NAME, SOCR, CODE',
                    limit=500)
            self.codes = []
            self.names = []
            self.indices = []
            query = db.query(stmt)
            while query.next():
                record = query.record()
                self.codes.append(forceString(record.value(0)))
                self.names.append(forceString(record.value(1)))
                self.indices.append(forceString(record.value(2)))
            self.rootCode = rootCode
            self.searchString = searchString
            self.reset()


#    def headerData(self, section, orientation, role):
#        if role == QtCore.Qt.DisplayRole:
#            return QtCore.QVariant(u'Населённые пункты')
#        return QtCore.QVariant()


    def data(self, index, role):
        if not index.isValid() or not self.names:
            return QtCore.QVariant()
        elif role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            row = index.row()
            return toVariant(', '.join([self.names[row], self.indices[row]]))
#        elif role == Qt.SizeHintRole:
#            return self.sizeHint
        return QtCore.QVariant()


    def code(self, index):
        if self.codes and 0<=index<len(self.codes):
            return self.codes[index]
        else:
            return None

#######################################################################################

class CStreetList(object):
    def __init__(self):
        self.prefix = ''
        self.codes = []
        self.names = []


    def setPrefix(self, prefix):
        if self.prefix != prefix:
            self.prefix = prefix
            query = QtSql.QSqlQuery(QtGui.qApp.db.db)
            stmt   = u'SELECT CODE, CONCAT(NAME, \' \', SOCR) AS NAMEEX FROM %s WHERE CODE LIKE \'%s%%\' AND RIGHT(CODE,2)=\'00\' ORDER BY NAME, SOCR, CODE' % (tblSTREET, prefix)
            if query.exec_(stmt):
                while query.next():
                    record = query.record()
                    self.codes.append(forceString(record.value(0)))
                    self.names.append(forceString(record.value(1)))


    def getLen(self):
        return len(self.codes)


    def indexByCode(self, code):
        try:
            return self.codes.index(code)
        except:
            return -1


    def searchStreet(self, streetName):
        h = len(self.names)-1
        if h<0:
            return -1, ''

        if not streetName:
            return 0, ''
        # т.к. улицы отсортированы по алфавиту есть резон искать двоичным поиским
        l = 0
        h = len(self.names)-1
        findName = streetName.lower()

        while l<h:
            m = (l+h)/2
            name = self.names[m].lower()
            if name>findName:
                h = m
            else:
                l = m+1

        name = self.names[l].lower()
        for i in range(min(len(name), len(findName))):
            if name[i] != findName[i]:
                return l, findName[:i-1]
        return l, findName[:min(len(name), len(findName))]



class CStreetListCache(object):
    __shared_map = {}

    def __init__(self):
        self.map = self.__shared_map

    def getList(self,  prefix):
        result = self.map.setdefault(prefix, CStreetList())
        if not result.prefix:
            result.setPrefix(prefix)
        return result




class CStreetModel(QtCore.QAbstractListModel):
    def __init__(self, parent):
        QtCore.QAbstractListModel.__init__(self, parent)
        self.stringList = None
        h = parent.fontMetrics().height() if parent else 14
        self.sizeHint = QtCore.QVariant(QtCore.QSize(h,h))
        self.addNone = False


    def columnCount(self, index=QtCore.QModelIndex()):
        return 1


    def rowCount(self, index = QtCore.QModelIndex()):
        if self.stringList == None:
            return 0
        else:
            return self.stringList.getLen() + (1 if self.addNone else 0)


    def setAddNone(self, flag):
        if self.addNone != flag:
            self.addNone = flag
            if self.stringList:
                self.reset()


    def setPrefix(self, prefix):
        self.stringList = CStreetListCache().getList(prefix)
        self.reset()


    def data(self, index, role):
        if not index.isValid() or self.stringList == None:
            return QtCore.QVariant()
        elif role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            row = index.row()
            if self.addNone:
                if row == 0:
                    return toVariant(u'не задано')
                else:
                    return toVariant(self.stringList.names[row-1])
            return toVariant(self.stringList.names[row])
        elif role == QtCore.Qt.SizeHintRole:
            return self.sizeHint
        return QtCore.QVariant()


    def code(self, index):
        if self.addNone:
            index -= 1
        if self.stringList != None and index >= 0:
            return self.stringList.codes[index]
        else:
            return None


    def indexByCode(self, code):
        if self.stringList != None:
            if self.addNone:
                if code:
                    return self.stringList.indexByCode(code) + 1
                else:
                    return 0
            else:
                return self.stringList.indexByCode(code)
        else:
            return -1


    def searchStreet(self, searchString):
        if self.stringList and searchString:
            index, searchString = self.stringList.searchStreet(searchString)
        else:
            index, searchString = -1, ''
        if self.addNone:
            index += 1
        return index, searchString


##########################################################################

def getStreetNameParts(code):
    stmt = 'SELECT NAME, SOCR FROM %s WHERE code =\'%s\'' %(tblSTREET, code)
    query = QtSql.QSqlQuery(QtGui.qApp.db.db)
    query.exec_(stmt)
    if query.next():
        record = query.record()
        return forceString(record.value(0)), forceString(record.value(1))
    else:
        return '{%s}' % code, ''

def getStreetName(code):
    if code:
        return ' '.join(getStreetNameParts(code))
    else:
        return ''
