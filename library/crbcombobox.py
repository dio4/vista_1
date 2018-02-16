#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore
from random import randint

from library.DbEntityCache import CDbEntityCache
from library.Utils import forceRef, toVariant, forceInt, forceString


def getRBCheckSum(tableName, codeField='code', nameField='name'):
    query = QtGui.qApp.db.query('SELECT SUM(CRC32(CONCAT_WS(CHAR(127), id, %s, %s))) FROM %s' % (codeField, nameField, tableName))
    if query.next():
        record = query.record()
        return record.value(0).toInt()[0]
    else:
        return 0


class CAbstractRBModelData(object):
    idxId = 0
    idxCode = 1
    idxName = 2
    idxFlatCode = 3
    idxRegionalCode = 4
    idxFederalCode = 5

    def __init__(self):
        self._buff = []
        self.__maxCodeLen = 0
        self.__mapIdToIndex = {}

    def clear(self):
        self._buff = []
        self.__maxCodeLen = 0
        self.__mapIdToIndex = {}

    def addItem(self, item_id, code, name, flatCode=u'', regionalCode=u'', federalCode=u''):
        self.__mapIdToIndex[item_id] = len(self._buff)
        self._buff.append((item_id, code, name, flatCode, regionalCode, federalCode))
        self.__maxCodeLen = max(self.__maxCodeLen, len(code))

    def getCount(self):
        return len(self._buff)

    def getFieldByIndex(self, index, fieldIdx):
        if index < 0:
            return None
        return self._buff[index][fieldIdx]

    def getId(self, index):
        return self.getFieldByIndex(index, self.idxId)

    def getCode(self, index):
        return self.getFieldByIndex(index, self.idxCode)

    def getFlatCode(self, index):
        return self.getFieldByIndex(index, self.idxFlatCode)

    def getRegionalCode(self, index):
        return self.getFieldByIndex(index, self.idxRegionalCode)

    def getFederalCode(self, index):
        return self.getFieldByIndex(index, self.idxFederalCode)

    def getName(self, index):
        return self._buff[index][2]

    def getIndexById(self, item_id):
        result = self.__mapIdToIndex.get(item_id, -1)
        if result < 0 and not item_id:
            result = self.__mapIdToIndex.get(None, -1)
        return result

    def getIndexByCode(self, code):
        for i, item in enumerate(self._buff):
            if item[1] == code:
                return i
        return -1

    def getIndexByFlatCode(self, flatCode):
        for i, item in enumerate(self._buff):
            if item[self.idxFlatCode] == flatCode:
                return i
        return -1

    def getIndexByName(self, name, isStrict=True):
        for i, item in enumerate(self._buff):
            if (isStrict and item[2] == name) or (not isStrict and name in item[2]):
                return i
        return -1

    def getNameById(self, item_id):
        index = self.getIndexById(item_id)
        if index >= 0:
            return self.getName(index)
        return '{' + str(item_id) + '}'

    def getCodeById(self, item_id):
        index = self.getIndexById(item_id)
        if index >= 0:
            return self.getCode(index)
        return '{' + str(item_id) + '}'

    def getIdByCode(self, code):
        index = self.getIndexByCode(code)
        return self.getId(index)

    def getIdByFlatCode(self, flatCode):
        index = self.getIndexByFlatCode(flatCode)
        return self.getId(index)

    def getAllCodes(self):
        codes = set()
        for item in self._buff:
            codes.add(item[1])
        return codes

    def getString(self, index, showFields):
        if showFields == 0:
            return self.getCode(index)
        elif showFields == 1:
            return self.getName(index)
        elif showFields == 2:
            return '%-*s|%s' % (self.__maxCodeLen, self.getCode(index), self.getName(index))
        else:
            return 'bad field %s' % showFields

    def getStringById(self, item_id, showFields):
        index = self.getIndexById(item_id)
        if index >= 0:
            return self.getString(index, showFields)
        return '{' + str(item_id) + '}'

    def getBuff(self):
        return self._buff


class CRBModelData(CAbstractRBModelData):
    """class for store data of ref book"""

    def __init__(self, tableName, addNone, filter, order, specialValues, group=''):
        CAbstractRBModelData.__init__(self)
        self._tableName = tableName
        self._addNone = addNone
        self._filter = filter
        self._order = order
        self._checkSum = None
        self._timestamp = None
        self._specialValues = specialValues
        self._notLoaded = True
        self._codeFieldName = 'code'
        self._group = group

    @property
    def codeFieldName(self):
        """
            Stores name of database table's field with code value.

        :rtype : string
        :return: field name for code column in database table.
        """
        return self._codeFieldName

    @codeFieldName.setter
    def codeFieldName(self, newFieldName):
        if newFieldName:
            self._codeFieldName = str(newFieldName)

    @property
    def group(self):
        """
            Stores name if grouping field
        :rtype  :   string
        :return :   grouping block value
        """
        return self._group

    @group.setter
    def group(self, newGroupValue):
        if newGroupValue:
            self._group = str(newGroupValue)

    def getCount(self):
        if self._notLoaded:
            self.load()
        return len(self._buff)

    def getId(self, index):
        if self._notLoaded:
            self.load()
        return CAbstractRBModelData.getId(self, index)

    def getIdByFlatCode(self, flatCode):
        idx = self.getIndexByFlatCode(flatCode)
        return self.getId(idx)

    def getCode(self, index):
        if self._notLoaded:
            self.load()
        return CAbstractRBModelData.getCode(self, index)

    def getFlatCode(self, index):
        if self._notLoaded:
            self.load()
        return CAbstractRBModelData.getFlatCode(self, index)

    def getName(self, index):
        if self._notLoaded:
            self.load()
        return CAbstractRBModelData.getName(self, index)

    def getIndexById(self, itemId):
        if self._notLoaded:
            self.load()
        return CAbstractRBModelData.getIndexById(self, itemId)

    def getIndexByCode(self, code):
        if self._notLoaded:
            self.load()
        return CAbstractRBModelData.getIndexByCode(self, code)

    def getIndexByFlatCode(self, flatCode):
        if self._notLoaded:
            self.load()
        return CAbstractRBModelData.getIndexByFlatCode(self, flatCode)

    def getIndexByName(self, name, isStrict=True):
        if self._notLoaded:
            self.load()
        return CAbstractRBModelData.getIndexByName(self, name, isStrict=isStrict)

    def getNameById(self, itemId):
        if self._notLoaded:
            self.load()
        return CAbstractRBModelData.getNameById(self, itemId)

    def getCodeById(self, itemId):
        if self._notLoaded:
            self.load()
        return CAbstractRBModelData.getCodeById(self, itemId)

    def getString(self, index, showFields):
        if self._notLoaded:
            self.load()
        return CAbstractRBModelData.getString(self, index, showFields)

    def getStringById(self, itemId, showFields):
        if self._notLoaded:
            self.load()
        return CAbstractRBModelData.getStringById(self, itemId, showFields)

    def load(self):
        self.clear()
        if self._specialValues:
            for fakeId, fakeCode, name in self._specialValues:
                self.addItem(fakeId, fakeCode, name, u'')
        if self._addNone:
            self.addItem(None, '0', u'не задано')
        db = QtGui.qApp.db
        table = db.table(self._tableName)
        cols = ['id', self.codeFieldName, 'name']
        isExistsFlatCode = 'flatCode' in table.fieldsDict
        if isExistsFlatCode:
            cols.append('flatCode')
        if 'regionalCode' in table.fieldsDict:
            cols.append('regionalCode')
        if 'federalCode' in table.fieldsDict:
            cols.append('federalCode')

        recordList = db.getRecordList(
            table=table,
            cols=cols,
            where=self._filter,
            order=self._order if self._order else '%s, name' % self.codeFieldName,
            group=self._group
        )
        for record in recordList:
            itemId = forceRef(record.value('id'))
            code = forceString(record.value(self.codeFieldName))
            name = forceString(record.value('name'))
            flatCode = forceString(record.value('flatCode'))
            regionalCode = forceString(record.value('regionalCode'))
            federalCode = forceString(record.value('federalCode'))
            self.addItem(itemId, code, name, flatCode, regionalCode, federalCode)
        self._timestamp = QtCore.QDateTime().currentDateTime()
        self._checkSum = getRBCheckSum(self._tableName, codeField=self.codeFieldName)
        self._notLoaded = False

    def isObsolete(self):
        # magic
        if self._timestamp and self._timestamp.secsTo(QtCore.QDateTime().currentDateTime()) > randint(300, 600):
            checkSum = getRBCheckSum(self._tableName, codeField=self.codeFieldName)
            return self._checkSum != checkSum
        else:
            return False

    def isLoaded(self):
        """
            Return loaded data status.

        :rtype : bool
        :return : True if data has been loaded, else False
        """
        return not self._notLoaded


class CRBModelDataCache(CDbEntityCache):
    mapTableToData = {}

    @classmethod
    def getData(cls, tableName, addNone=True, filter='', order=None, specialValues=None, needCache=True,
                codeFieldName=None, group=''):
        strTableName = unicode(tableName)
        if isinstance(specialValues, list):
            specialValues = tuple(specialValues)
        key = (strTableName, addNone, filter, order, specialValues, codeFieldName, group)
        result = cls.mapTableToData.get(key, None)
        if not result or result.isObsolete():
            result = CRBModelData(strTableName, addNone, filter, order, specialValues, group=group)
            result.codeFieldName = codeFieldName
            cls.connect()
            if needCache:
                cls.mapTableToData[key] = result
        return result

    @classmethod
    def reset(cls, tableName=None):
        if tableName:
            for key in cls.mapTableToData.keys():
                if key[0] == tableName:
                    del cls.mapTableToData[key]
        else:
            cls.mapTableToData.clear()

    @classmethod
    def purge(cls):
        cls.reset()


class CRBModel(QtCore.QAbstractTableModel, object):
    def __init__(self, parent):
        super(CRBModel, self).__init__(parent)
        self.d = None
        self.resetRequired = False
        self.tableName = None
        self.coloredRows = []
        self.colorName = QtCore.Qt.lightGray  # QtCore.Qt.cyan

    def setTable(self, tableName, addNone=True, filter='', order=None, specialValues=None, needCache=True,
                 codeFieldName=None, group=''):
        self.tableName = tableName
        d = self.d
        self.d = CRBModelDataCache.getData(
            tableName,
            addNone,
            filter,
            order,
            specialValues,
            needCache,
            codeFieldName=codeFieldName,
            group=group
        )
        if d and d.isLoaded() or self.resetRequired:
            # Документация рекомендует использовать begin/end вместо простого reset, однако используемой нами версии Qt
            # это не реализовано. В каких-то сборках это приводило к ошибкам.
            # self.beginResetModel()
            self.reset()
            self.resetRequired = False
            # self.endResetModel()

    def columnCount(self, index=QtCore.QModelIndex(), **kwargs):
        return 3

    def rowCount(self, index=QtCore.QModelIndex(), **kwargs):
        if self.d:
            return self.d.getCount()
        else:
            self.resetRequired = True
            return 0

    def headerData(self, section, orientation, role=None):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                if section == 0:
                    return toVariant(u'Код')
                elif section == 1:
                    return toVariant(u'Наименование')
        return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()
        elif role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole or role == QtCore.Qt.ToolTipRole:
            row = index.row()
            if row < self.d.getCount():
                return QtCore.QVariant(self.d.getString(row, index.column()))
        elif role == QtCore.Qt.SizeHintRole:
            font = QtGui.QFont()
            fontMetric = QtGui.QFontMetrics(font)
            row = index.row()
            valueSize = fontMetric.size(QtCore.Qt.TextExpandTabs, self.d.getString(row, index.column())) + QtCore.QSize(
                16, 0)
            return valueSize
        elif role == QtCore.Qt.BackgroundRole:
            if self.d.getId(index.row()) in self.coloredRows:
                return QtCore.QVariant(QtGui.QColor(self.colorName))
        return QtCore.QVariant()

    def searchId(self, itemId):
        return self.d.getIndexById(itemId) if self.d else None

    def searchName(self, name):
        return self.d.getIndexByName(name)

    def getId(self, index):
        return self.d.getId(index) if self.d else None

    def getIdByFlatCode(self, flatCode):
        return self.d.getIdByFlatCode(flatCode)

    def getName(self, index):
        return self.d.getName(index)

    def getCode(self, index):
        return self.d.getCode(index)

    def getFlatCode(self, index):
        return self.d.getFlatCode(index)

    def searchFlatCode(self, flatCode):
        flatCode = unicode(flatCode).lower()
        n = self.d.getCount()
        for i in xrange(n):
            if unicode(self.d.getFlatCode(i)).lower().startswith(flatCode):
                return i
        return -1

    def searchCode(self, code):
        if code is None:
            return -1
        code = unicode(code).upper()
        n = self.d.getCount()
        for i in xrange(n):
            if unicode(self.d.getCode(i)).upper().startswith(code):
                return i
        for i in xrange(n):
            if unicode(self.d.getName(i)).upper().startswith(code):
                return i
        return -1

    # docIdList - список врачей, по которым должен вестись поиск. i2273
    def searchCodeEx(self, code, docIdList=None):
        def sortByCode(item):
            codeItem = item[1]
            intCodeItem = forceInt(codeItem)
            if forceString(intCodeItem) == codeItem:
                return intCodeItem
            else:
                return codeItem

        code = unicode(code).upper()
        items = self.d.getBuff()
        itemsSortByCode = sorted(items, key=sortByCode)

        for index in xrange(self.d.getCount()):
            if unicode(itemsSortByCode[index][1].upper()).startswith(code):
                if docIdList and len(code):
                    # if self.getId(index) in docIdList:
                    return self.d.getIndexById(itemsSortByCode[index][0]), code
                else:
                    return self.d.getIndexById(itemsSortByCode[index][0]), code
            if unicode(items[index][2].upper()).startswith(code):
                if docIdList and len(code):
                    if self.getId(index) in docIdList:
                        return index, code
                else:
                    return index, code
        return -1, code[:-1]


class CRBLikeEnumModel(CRBModel):
    def __init__(self, parent):
        CRBModel.__init__(self, parent)
        self.d = None

    def setValues(self, values):
        self.d = CAbstractRBModelData()
        for i, val in enumerate(values):
            item_id = i
            code = str(i)
            name = val
            self.d.addItem(item_id, code, name)


class CRBSelectionModel(QtGui.QItemSelectionModel):
    def select(self, indexOrSelection, command):
        if isinstance(indexOrSelection, QtCore.QModelIndex):
            index = indexOrSelection
            if index.column() > 1:
                correctIndex = self.model().index(index.row(), 1)
            else:
                correctIndex = index
            if command & QtGui.QItemSelectionModel.Select and not (command & QtGui.QItemSelectionModel.Current):
                self.setCurrentIndex(
                    correctIndex,
                    QtGui.QItemSelectionModel.Clear | QtGui.QItemSelectionModel.Select | QtGui.QItemSelectionModel.Current
                )
            else:
                QtGui.QItemSelectionModel.select(self, correctIndex, command)

        else:
            QtGui.QItemSelectionModel.select(self, indexOrSelection, command)


class CRBPopupViewDelegate(QtGui.QStyledItemDelegate):
    def paint(self, painter, option, index):
        option = QtGui.QStyleOptionViewItemV4(option)
        self.initStyleOption(option, index)
        painter.save()
        doc = QtGui.QTextDocument()
        doc.setDefaultFont(option.font)
        doc.setHtml(option.text)
        option.text = ''  # model.data(index, Qt.DisplayRole).toString()
        option.widget.style().drawControl(QtGui.QStyle.CE_ItemViewItem, option, painter)
        painter.translate(option.rect.left(), option.rect.top())
        clip = QtCore.QRectF(0, 0, option.rect.width(), option.rect.height())
        doc.drawContents(painter, clip)
        painter.restore()

    def sizeHint(self, option, index):
        option = QtGui.QStyleOptionViewItemV4(option)
        self.initStyleOption(option, index)
        doc = QtGui.QTextDocument()
        doc.setDefaultFont(option.font)
        doc.setHtml(option.text)
        doc.setTextWidth(option.rect.width())
        return QtCore.QSize(doc.idealWidth(), doc.size().height())


class CRBPopupView(QtGui.QTableView):
    def __init__(self, parent):
        QtGui.QTableView.__init__(self, parent)
        self.crbComboBox = parent
        # self.verticalHeader().setResizeMode(QtGui.QHeaderView.Fixed)
        self.verticalHeader().hide()
        self.horizontalHeader().setStretchLastSection(True)
        self.setFrameShape(QtGui.QFrame.NoFrame)
        self.setMinimumWidth(300)

    def keyboardSearch(self, search):
        rowIndex, search = self.model().searchCodeEx(search)
        if rowIndex >= 0:
            index = self.model().index(rowIndex, 1)
            self.setCurrentIndex(index)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            CRBComboBox.keyPressEvent(self.crbComboBox, event)
            self.emit(QtCore.SIGNAL('hide()'))
        else:
            QtGui.QTableView.keyPressEvent(self, event)


# TODO: atronah: возможно стоит найти общее с CAbstractDbComboBox и объединить
class CRBComboBox(QtGui.QComboBox):
    u"""ComboBox, в котором отображается содержимое таблицы - справочника"""
    showCode = 0
    showName = 1
    showCodeAndName = 2
    showNameAndCode = 2

    def __init__(self, parent):
        super(CRBComboBox, self).__init__(parent)
        self._searchString = ''
        self.showFields = CRBComboBox.showName
        # self._searchColumn = 0
        self._model = CRBModel(self)
        self._selectionModel = CRBSelectionModel(self._model)
        self._tableName = ''
        self._addNone = True
        self._needCache = True
        self._filter = ''
        self._order = ''
        self._specialValues = None
        self.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.prefferedWidth = None
        self.popupView = CRBPopupView(self)
        self.setShowFields(self.showFields)
        self.setView(self.popupView)
        self.setModel(self._model)
        self.popupView.setSelectionModel(self._selectionModel)
        self._isRTF = False
        self.isShown = False

    def setRTF(self, isRTF):
        self._isRTF = isRTF
        if isRTF:
            self.popupView.setItemDelegate(CRBPopupViewDelegate(self.popupView))
        else:
            self.popupView.setItemDelegate(QtGui.QItemDelegate(self.popupView))

    def setPrefferedWidth(self, prefferedWidth):
        self.prefferedWidth = prefferedWidth

    def setTable(self, tableName, addNone=True, filter='', order=None, specialValues=None, needCache=True,
                 codeFieldName=None, group=''):
        self._tableName = tableName
        self._addNone = addNone
        self._filter = filter
        self._order = order
        self._needCache = needCache
        self._specialValues = specialValues
        self._model.setTable(
            tableName,
            addNone,
            filter,
            order,
            specialValues,
            needCache,
            codeFieldName=codeFieldName,
            group=group
        )

    def tableName(self):
        return self._tableName

    def order(self):
        return self._order

    def model(self):
        return self._model

    def setSpecialValues(self, specialValues):
        if self._specialValues != specialValues:
            self._specialValues = specialValues
            self.reloadData()

    def setFilter(self, filter='', order=None):
        self._filter = filter
        self._order = order
        self.setTable(self._tableName, self._addNone, filter, order, self._specialValues, self._needCache)

    def reloadData(self):
        self._model.setTable(
            self._tableName,
            self._addNone,
            self._filter,
            self._order,
            self._specialValues,
            self._needCache
        )

    # Задает правило отображения данных в режиме просмотра (Не редактирования!)
    # В режиме редактирования (с выпадающим списком) всегда показываются и код и имя элемента.
    # TODO: разбить настройку отображения на две части (то, что отображается при просмотре и то, что при редактировании)
    def setShowFields(self, showFields):
        self.showFields = showFields
        self.setModelColumn(self.showFields)

    def setMaxVisibleItems(self, count):
        QtGui.QComboBox.setMaxVisibleItems(self, count)

    def setModel(self, model):
        QtGui.QComboBox.setModel(self, model)
        self.popupView.hideColumn(2)
        self._model = model

    def setView(self, view):
        QtGui.QComboBox.setView(self, view)

    def setValue(self, itemId):
        rowIndex = self._model.searchId(itemId)
        if rowIndex > -1:
            self.setCurrentIndex(rowIndex)
        else:
            self.setCurrentIndex(0)

    def getValue(self):
        u"""id записи"""
        return self.value()

    def value(self):
        u"""id записи"""
        rowIndex = self.currentIndex()
        return self._model.getId(rowIndex)

    def setCode(self, code):
        u"""поле code записи"""
        rowIndex = self._model.searchCode(code)
        self.setCurrentIndex(rowIndex)

    def setFlatCode(self, flatCode):
        rowIndex = self.model().searchFlatCode(flatCode)
        self.setCurrentIndex(rowIndex)

    def code(self):
        u"""поле code записи"""
        rowIndex = self.currentIndex()
        return self._model.getCode(rowIndex)

    def name(self):
        return self._model.getName(self.currentIndex())

    def addItem(self, item):
        pass

    def showPopup(self):
        totalItems = self._model.rowCount()
        self.isShown = True
        if totalItems > 0:
            self._searchString = ''
            view = self.popupView
            selectionModel = view.selectionModel()
            selectionModel.setCurrentIndex(
                self._model.index(self.currentIndex(), 1),
                QtGui.QItemSelectionModel.ClearAndSelect
            )
            sizeHint = view.sizeHint()
            comboRect = self.rect()
            below = self.mapToGlobal(comboRect.bottomLeft())
            above = self.mapToGlobal(comboRect.topLeft())
            screen = QtGui.qApp.desktop().availableGeometry(below)

            if QtGui.qApp.preferences.decor_crb_width_unlimited:
                sizeHint.setWidth(screen.width())

            maxVisibleItems = self.maxVisibleItems()
            visibleItems = min(maxVisibleItems, totalItems)
            if visibleItems > 0:
                headerHeight = view.horizontalHeader().height()
                view.setFixedHeight(view.rowHeight(0) * visibleItems + headerHeight)

            view.resizeRowsToContents()
            prefferedWidth = sizeHint.width()
            if self.prefferedWidth:
                prefferedWidth = max(self.prefferedWidth, prefferedWidth)
            prefferedWidth = max(prefferedWidth, self.width())
            frame = view.parent()
            frame.resize(prefferedWidth, view.height())
            view.resize(prefferedWidth, view.height())

            # выравниваем по месту
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
            view.resizeColumnToContents(0)

    def hidePopup(self):
        super(CRBComboBox, self).hidePopup()
        self.isShown = False

    def focusOutEvent(self, event):
        self._searchString = ''
        QtGui.QComboBox.focusOutEvent(self, event)

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Escape:
            event.ignore()
        elif key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            event.ignore()
        if key == QtCore.Qt.Key_Delete:
            self._searchString = ''
            self.lookup()
            event.accept()
        elif key == QtCore.Qt.Key_Backspace:
            self._searchString = self._searchString[:-1]
            self.lookup()
            event.accept()
        elif key == QtCore.Qt.Key_Space:
            if self.isShown:
                self.hidePopup()
            else:
                self.showPopup()
        elif not event.text().isEmpty():
            char = event.text().at(0)
            if char.isPrint():
                self._searchString += unicode(QtCore.QString(char)).upper()
                self.lookup()
                event.accept()
            else:
                QtGui.QComboBox.keyPressEvent(self, event)
        else:
            QtGui.QComboBox.keyPressEvent(self, event)

    def lookup(self):
        i, self._searchString = self._model.searchCodeEx(self._searchString)
        if i >= 0 and i != self.currentIndex():
            self.setCurrentIndex(i)

    def paintEvent(self, event):
        index = self.currentIndex()
        if isinstance(index, QtCore.QModelIndex):
            QtGui.QComboBox.paintEvent(self, event)
            return
        data = self.itemData(index, QtCore.Qt.DisplayRole)
        if self._isRTF:
            p = QtGui.QStylePainter(self)
            opt = QtGui.QStyleOptionComboBox()

            doc = QtGui.QTextDocument(self)
            doc.setDefaultFont(QtGui.qApp.font())
            doc.setHtml(data.toString())
            self.initStyleOption(opt)
            p.drawComplexControl(QtGui.QStyle.CC_ComboBox, opt)

            clip = QtCore.QRectF(p.style().subElementRect(QtGui.QStyle.SE_ComboBoxFocusRect, opt, self))
            doc.drawContents(p, clip)
        else:
            QtGui.QComboBox.paintEvent(self, event)


class CRBMultiPopupViewDelegate(CRBPopupViewDelegate):
    def paint(self, painter, option, index):
        col = index.column()
        if col == 0:
            style = QtGui.qApp.style()
            data = index.model().data(index, QtCore.Qt.DisplayRole).toBool()
            checkbox_style = QtGui.QStyleOptionButton()
            checkbox_rect = style.subElementRect(QtGui.QStyle.SE_CheckBoxIndicator, checkbox_style)
            checkbox_style.rect = option.rect
            checkbox_style.rect.setLeft(option.rect.x() + option.rect.width() / 2 - checkbox_rect.width() / 2)
            if data:
                checkbox_style.state = QtGui.QStyle.State_On | QtGui.QStyle.State_Enabled
            else:
                checkbox_style.state = QtGui.QStyle.State_Off | QtGui.QStyle.State_Enabled
            style.drawControl(QtGui.QStyle.CE_CheckBox, checkbox_style, painter)
        else:
            super(CRBMultiPopupViewDelegate, self).paint(painter, option, index)


class CRBMultiModel(CRBModel):
    def __init__(self, parent):
        super(CRBMultiModel, self).__init__(parent)
        self.checked = []

    def setValue(self, val):
        self.checked = val

    def value(self):
        return self.checked

    def columnCount(self, index=QtCore.QModelIndex(), **kwargs):
        return 4

    def data(self, index, role=QtCore.Qt.DisplayRole):
        col = index.column()
        row = index.row()
        item_id = self.getId(row)
        if role == QtCore.Qt.DisplayRole and col == 0:
            return QtCore.QVariant(item_id in self.checked)
        return super(CRBMultiModel, self).data(self.createIndex(row, col - 1), role)

    def headerData(self, section, orientation, role=None):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                if section == 1:
                    return toVariant(u'Код')
                elif section == 2:
                    return toVariant(u'Наименование')
        return QtCore.QVariant()

    def toggle(self, index):
        row = index.row()
        item_id = self.getId(row)
        if row < self.d.getCount():
            if item_id in self.checked:
                self.checked.remove(item_id)
            else:
                self.checked.append(item_id)
        return self.createIndex(row, 0)

    def setTable(self, tableName, addNone=True, filter='', order=None, specialValues=None, needCache=True,
                 codeFieldName=None, group=''):
        super(CRBMultiModel, self).setTable(
            tableName,
            addNone=False,
            filter=filter,
            order=order,
            specialValues=specialValues,
            needCache=needCache,
            codeFieldName=codeFieldName,
            group=group
        )

    def getCheckedNames(self):
        return list(self.getName(self.searchId(itemId)) for itemId in self.checked)


class CRBMultiComboBox(CRBComboBox):
    EMPTY_TEXT = u'<не выбрано>'

    def __init__(self, parent):
        super(CRBMultiComboBox, self).__init__(parent)
        self._model = CRBMultiModel(self)
        self.setModel(self._model)

        self.popupView = CRBPopupView(self)
        self.popupView.setModel(self._model)
        self.popupView.setItemDelegate(CRBMultiPopupViewDelegate(self.popupView))
        self.popupView.hideColumn(3)

        self.setView(self.popupView)
        self.installEventFilter(self)
        self.popupView.viewport().installEventFilter(self)

        self.__displayText = self.EMPTY_TEXT

    def currentText(self):
        return ', '.join(self._model.getCheckedNames()) or self.EMPTY_TEXT

    def setModel(self, model):
        QtGui.QComboBox.setModel(self, model)
        self._model = model

    def eventFilter(self, obj, evt):
        if evt.type() == QtCore.QEvent.MouseButtonRelease:
            if obj == self.popupView.viewport():
                idx = self.popupView.currentIndex()
                self.popupView.update(self._model.toggle(idx))
                self.repaint()
                return True
        return False

    def paintEvent(self, evt):
        painter = QtGui.QStylePainter(self)
        painter.setPen(self.palette().color(QtGui.QPalette.Text))
        option = QtGui.QStyleOptionComboBox()
        self.initStyleOption(option)
        painter.drawComplexControl(QtGui.QStyle.CC_ComboBox, option)
        textRect = QtGui.qApp.style().subControlRect(
            QtGui.QStyle.CC_ComboBox,
            option,
            QtGui.QStyle.SC_ComboBoxEditField,
            self
        )
        painter.drawItemText(
            textRect.adjusted(*((2, 2, -1, 0) if self.isShown else (1, 0, -1, 0))),
            QtGui.qApp.style().visualAlignment(self.layoutDirection(), QtCore.Qt.AlignLeft),
            self.palette(),
            self.isEnabled(),
            self.fontMetrics().elidedText(self.currentText(), QtCore.Qt.ElideRight, textRect.width())
        )

    def showPopup(self):
        super(CRBMultiComboBox, self).showPopup()
        self.repaint()

    def hidePopup(self):
        super(CRBMultiComboBox, self).hidePopup()
        self.repaint()

    def resizeEvent(self, evt):
        super(CRBMultiComboBox, self).resizeEvent(evt)
        self.repaint()

    def setValue(self, itemIdList):
        if isinstance(itemIdList, (list, tuple, set)):
            self._model.checked = list(itemIdList)
        elif isinstance(itemIdList, int):
            self._model.checked = [itemIdList]
        elif itemIdList is None:
            self._model.checked = []

    def getValue(self):
        return self.value()

    def value(self):
        return self._model.checked
