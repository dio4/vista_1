# -*- coding: utf-8 -*-
from PyQt4 import QtSql

from library.DbEntityCache import CDbEntityCache
from library.Utils import *


### CHECKSUM TABLE table EXTENDED

def getDBCheckSum(tableName, fieldName, filter):
    db = QtGui.qApp.db
    # FIXME: переделать на запрос
    query = QtSql.QSqlQuery(QtGui.qApp.db.db)
    if filter:
        wherePart = u'WHERE ' + unicode(filter)
    else:
        wherePart = ''
    query.exec_('SELECT SUM(CRC32(CONCAT_WS(CHAR(127), id, %s))) FROM %s %s' % (fieldName, tableName, wherePart))
    if query.next():
        record = query.record()
        return record.value(0).toInt()[0]
    else:
        return None


class CDbData(object):
    def __init__(self):
        self.idList = []
        self.strList = []
        self.checkSum = None
        self.timestamp = QDateTime()

    @property
    def first(self):
        u""" :rtype: QVariant """
        return self.strList[0] if self.strList else QVariant()

    @property
    def last(self):
        u""" :rtype: QVariant """
        return self.strList[0] if self.strList else QVariant()

    def select(self, tableName, nameField, filter, addNone=None, noneText=None):
        db = QtGui.qApp.db
        table = db.table(tableName)
        self.idList = []
        self.strList = []
        if addNone:
            self.idList.append(None)
            self.strList.append(QVariant(noneText))

        stmt = db.selectStmt(table, [table.idField(), nameField], filter, order=nameField)
        query = db.query(stmt)
        while query.next():
            record = query.record()
            self.idList.append(record.value(0).toInt()[0])
            self.strList.append(record.value(1))


class CDbDataCache(CDbEntityCache):
    mapKeyToData = {}  # type: dict[tuple,CDbData]

    @classmethod
    def getData(cls, tableName, nameField, filter, addNone=None, noneText=None):
        key = (tableName, nameField, filter, addNone, noneText)
        result = cls.mapKeyToData.get(key, None)
        now = QDateTime.currentDateTime()
        if not result or result.timestamp.secsTo(now) > 60:  ## magic
            checkSum = getDBCheckSum(tableName, nameField, filter)
            if not result or result.checkSum != checkSum:
                result = CDbData()
                result.select(tableName, nameField, filter, addNone, noneText)
                result.checkSum = checkSum
                cls.connect()
                cls.mapKeyToData[key] = result
            result.timestamp = now
        return result

    @classmethod
    def purge(cls):
        cls.mapKeyToData.clear()

    @classmethod
    def purgeItem(cls, key):
        if key in cls.mapKeyToData.keys():
            del cls.mapKeyToData[key]


class CAbstractDbModel(QAbstractListModel):
    def __init__(self, parent):
        QAbstractListModel.__init__(self, parent)
        self.dbdata = None

        if parent != None:
            h = parent.fontMetrics().height()
        else:
            h = 14
        self.sizeHint = QVariant(QSize(h, h))

    def columnCount(self, index=QtCore.QModelIndex()):
        return 1

    def dbDataAvailable(self):
        if not self.dbdata:
            self.initDbData()
        return bool(self.dbdata)

    def rowCount(self, index=QtCore.QModelIndex()):
        if QtGui.qApp.db is not None and QtGui.qApp.db.isValid() and self.dbDataAvailable():
            return len(self.dbdata.idList)
        else:
            return 0

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role == Qt.DisplayRole or role == Qt.EditRole:
            if self.dbDataAvailable():
                row = index.row()
                if row < len(self.dbdata.strList):
                    return QVariant(self.dbdata.strList[row])
        return QVariant()

    def searchId(self, itemId):
        if self.dbDataAvailable():
            if itemId in self.dbdata.idList:
                return self.dbdata.idList.index(itemId)
        return -1

    def idList(self):
        if self.dbDataAvailable():
            return self.dbdata.idList
        return []

    def getNameById(self, itemId):
        row = self.searchId(itemId)
        if row >= 0:
            return self.dbdata.strList[row]
        else:
            return ''

    def getId(self, index):
        if self.dbdata and 0 <= index < len(self.dbdata.idList):
            return self.dbdata.idList[index]
        else:
            return None

    def getName(self, index):
        if self.dbdata and 0 <= index < len(self.dbdata.strList):
            return self.dbdata.strList[index]
        else:
            return ''

    def keyboardSearch(self, search):
        if self.dbDataAvailable():
            l = 0
            h = len(self.dbdata.strList) - 1
            while l <= h:
                m = (l + h) / 2
                c = cmp(forceString(self.dbdata.strList[m]).upper(), search)
                if c < 0:
                    l = m + 1
                elif c > 0:
                    h = m - 1
                else:
                    return m
            return l
        else:
            return -1

    def update(self):
        pass


class CDbModel(CAbstractDbModel):
    def __init__(self, parent):
        CAbstractDbModel.__init__(self, parent)
        self.tableName = ''
        self.nameField = 'name'
        self.filter = ''
        self.addNone = True
        self.noneText = ''

        if parent != None:
            h = parent.fontMetrics().height()
        else:
            h = 14
        self.sizeHint = QVariant(QSize(h, h))

    def setTable(self, tableName):
        if self.tableName != tableName:
            self.tableName = tableName
            if self.dbdata != None:
                self.dbdata = None
                self.reset()

    def setNameField(self, nameField):
        if self.nameField != nameField:
            self.nameField = nameField
            if self.dbdata != None:
                self.dbdata = None
                self.reset()

    def setFilter(self, filter):
        if self.filter != filter:
            self.filter = filter
            if self.dbdata != None:
                self.dbdata = None
                self.reset()

    def setAddNone(self, addNone, noneText=''):
        if self.addNone != addNone or self.noneText != noneText:
            self.addNone = addNone
            self.noneText = noneText
            if self.dbdata != None:
                self.dbdata = None
                self.reset()

    def initDbData(self):
        if self.tableName and self.nameField:
            self.dbdata = CDbDataCache.getData(self.tableName, self.nameField, self.filter, self.addNone, self.noneText)

    def update(self):
        oldData = self.dbdata
        self.dbdata = CDbDataCache.getData(self.tableName, self.nameField, self.filter, self.addNone, self.noneText)
        if oldData != self.dbdata:
            self.reset()

    def forceUpdate(self):
        CDbDataCache.purgeItem((self.tableName, self.nameField, self.filter, self.addNone, self.noneText))


class CDbPopupView(QtGui.QListView):
    def __init__(self, parent):
        QtGui.QListView.__init__(self, parent)

    def sizeHint(self):
        s = QSize()
        s.setHeight(QSize(QtGui.QListView.sizeHint(self)).height())
        s.setWidth(self.sizeHintForColumn(0))
        return s

    def keyPressEvent(self, evt):
        if evt.key() == Qt.Key_Space:
            self.emit(SIGNAL('hide()'))
            evt.accept()
        else:
            super(CDbPopupView, self).keyPressEvent(evt)


class CAbstractDbComboBox(QtGui.QComboBox):
    def __init__(self, parent):
        QtGui.QComboBox.__init__(self, parent)
        self.__searchString = ''
        self.setMinimumContentsLength(20)
        self.__popupView = CDbPopupView(self)
        self.setView(self.__popupView)
        self.connect(self.__popupView, SIGNAL('hide()'), self.hidePopup)

    def setModel(self, model):
        self.__model = model
        QtGui.QComboBox.setModel(self, model)
        self.view().adjustSize()

    def showPopup(self):
        totalItems = self.__model.rowCount()
        if totalItems > 0:
            self.__searchString = ''
            view = self.__popupView
            selectionModel = view.selectionModel()
            selectionModel.setCurrentIndex(self.__model.index(self.currentIndex(), 0),
                                           QtGui.QItemSelectionModel.ClearAndSelect)
            sizeHint = view.sizeHint()
            comboRect = self.rect()
            below = self.mapToGlobal(comboRect.bottomLeft())
            above = self.mapToGlobal(comboRect.topLeft())
            screen = QtGui.qApp.desktop().availableGeometry(below)

            if QtGui.qApp.preferences.decor_crb_width_unlimited:
                sizeHint.setWidth(screen.width() + 40)

            maxVisibleItems = self.maxVisibleItems()
            visibleItems = min(maxVisibleItems, totalItems)
            if visibleItems > 0:
                if self.parent() != None:
                    h = self.parent().fontMetrics().height()
                else:
                    h = 14
                view.setFixedHeight(h * visibleItems)

            prefferedWidth = sizeHint.width()
            frame = view.parent()
            frame.resize((prefferedWidth + 40), view.height())

            # выравниваем по месту
            popupTop = 0
            popupLeft = 0
            if screen.bottom() - below.y() >= view.height():
                popupTop = below.y()
            elif above.y() - screen.y() >= view.height():
                popupTop = above.y() - view.height() - 2 * frame.frameWidth()
            else:
                popupTop = max(screen.top(), screen.bottom() - view.height() - frame.frameWidth())
            if screen.right() - below.x() >= view.width():
                popupLeft = below.x()
            else:
                popupLeft = max(screen.left(), screen.right() - view.width() - frame.frameWidth())
            frame.move(popupLeft, popupTop)

            frame.show()
            view.setFocus()
            scrollBar = view.horizontalScrollBar()
            scrollBar.setValue(0)

    def focusInEvent(self, event):
        self.__searchString = ''
        QtGui.QComboBox.focusInEvent(self, event)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:
            event.ignore()
        elif key in (Qt.Key_Return, Qt.Key_Enter):
            event.ignore()
        if key == Qt.Key_Delete:
            self.__searchString = ''
            self.lookup()
            event.accept()
        elif key == Qt.Key_Backspace:  # BS
            self.__searchString = self.__searchString[:-1]
            self.lookup()
            event.accept()
        elif key == Qt.Key_Space:
            self.showPopup()
            event.accept()
        elif not event.text().isEmpty():
            char = event.text().at(0)
            if char.isPrint():
                self.__searchString = self.__searchString + unicode(QString(char)).upper()
                self.lookup()
                event.accept()
            else:
                QtGui.QComboBox.keyPressEvent(self, event)
        else:
            QtGui.QComboBox.keyPressEvent(self, event)

    def lookup(self):
        i = self.__model.keyboardSearch(self.__searchString)
        if i != self.currentIndex():
            self.setCurrentIndex(i)

    def sizeHint(self):
        return QSize(20, 20)

    def setValue(self, itemId):
        if itemId in self.values():
            rowIndex = self.__model.searchId(itemId)
            self.setCurrentIndex(rowIndex)

    def value(self):
        rowIndex = self.currentIndex()
        return self.__model.getId(rowIndex)

    def setText(self, name):
        rowIndex = self.__model.keyboardSearch(name)
        self.setCurrentIndex(rowIndex)

    def text(self):
        rowIndex = self.currentIndex()
        return forceString(self.__model.getName(rowIndex))

    def addItem(self, item):
        pass

    def update(self):
        itemId = self.value()
        self.__model.update()
        self.setValue(itemId)
        self.view().adjustSize()

    def forceUpdate(self):
        self.__model.forceUpdate()

    def values(self):
        return self.__model.idList()


class CDbComboBox(CAbstractDbComboBox):
    def __init__(self, parent):
        CAbstractDbComboBox.__init__(self, parent)
        self.setModel(CDbModel(self))

    def setTable(self, tableName, nameField=None, addNone=None):
        if nameField != None:
            self.model().setNameField(nameField)
        if addNone != None:
            self.model().setAddNone(addNone)
        self.model().setTable(tableName)

    def setNameField(self, nameField):
        self.model().setNameField(nameField)

    def setAddNone(self, addNone, noneText=''):
        self.model().setAddNone(addNone, noneText)

    def setFilter(self, filter):
        self.model().setFilter(filter)

    def filter(self):
        return self.model().filter
