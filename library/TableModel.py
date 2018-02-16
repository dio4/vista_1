# -*- coding: utf-8 -*-
from library.Enum import CEnum
from library.Utils import *
from library.crbcombobox import CRBModelDataCache, CRBComboBox
from library.database import CTableRecordCache
from library.exception import CException, CDatabaseException


class CCol(object):
    """
      Root of all columns
    """
    alg = {'l': QVariant(Qt.AlignLeft + Qt.AlignVCenter),
           'c': QVariant(Qt.AlignHCenter + Qt.AlignVCenter),
           'r': QVariant(Qt.AlignRight + Qt.AlignVCenter),
           'j': QVariant(Qt.AlignJustify + Qt.AlignVCenter)
           }

    invalid = QVariant()

    def __init__(self, title, fields, defaultWidth, alignment, isRTF=False, **params):
        assert isinstance(fields, (list, tuple))
        self._title = QVariant(title)
        self._toolTip = CCol.invalid
        self._whatsThis = CCol.invalid
        self._fields = fields
        self._defaultWidth = defaultWidth
        self._align = CCol.alg[alignment] if isinstance(alignment, basestring) else alignment
        self._fieldindexes = []
        self._adopted = False
        self._isRTF = isRTF  # rich text - обрабатывать как форматированный текст
        self._enabled = params.get('enabled', True)
        self._visible = params.get('visible', True)
        self.color = None
        self._cacheDict = params.get('cache', {})

    def fieldName(self):
        return self._fields[0] if len(self._fields) else None

    def flags(self, index=None):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def valueType(self):
        return None

    def toString(self, val, record=None):
        return val

    def toCheckState(self, val, record=None):
        return QVariant()

    def isKeyInCache(self, key):
        return self._cacheDict.has_key(key)

    def getFromCache(self, key):
        return self._cacheDict[key]

    def putIntoCache(self, key, value):
        self._cacheDict[key] = value

    def format(self, values):
        id = forceStringEx(values[0])
        if not self.isKeyInCache(id):
            self.load(id)
        return toVariant(self.getFromCache(id))

    def load(self, id):
        self.putIntoCache(id, id)

    def clearCache(self):
        self._cacheDict.clear()

    def clearCacheById(self, id):
        if self.isKeyInCache(id):
            self._cacheDict.pop(id)

    @staticmethod
    def resolveValueByCaches(value, rules):
        record = None
        fieldName = None
        for cache, fieldName in rules:
            itemId = forceRef(value)
            if not itemId:
                return CCol.invalid
            record = cache.get(itemId)
            if not record:
                return CCol.invalid
            value = record.value(fieldName)
        return value if value else CCol.invalid

    def adoptRecord(self, record):
        if record:
            self._fieldindexes = []
            if isinstance(self._fields, (list, tuple)):
                for fieldName in self._fields:
                    fieldIndex = record.indexOf(fieldName)
                    assert fieldIndex >= 0, fieldName
                    self._fieldindexes.append(fieldIndex)
            self._adopted = True

    def extractValuesFromRecord(self, record):
        if not self._adopted:
            self.adoptRecord(record)
        result = []
        if record:
            for i in self._fieldindexes:
                result.append(record.value(i))
        else:
            for i in self._fieldindexes:
                result.append(QVariant())
        result.append(record)
        return result

    def setTitle(self, title):
        self._title = toVariant(title)

    def title(self):
        return self._title

    def setToolTip(self, toolTip):
        self._toolTip = toVariant(toolTip)

    def toolTip(self):
        return self._toolTip

    def toolTipValue(self, values):
        return QVariant()

    def setWhatsThis(self, whatsThis):
        self._whatsThis = toVariant(whatsThis)

    def whatsThis(self):
        return self._whatsThis

    def fields(self):
        return self._fields

    def defaultWidth(self):
        return self._defaultWidth

    def alignment(self):
        return self._align

    def formatNative(self, values):
        u"""Столбец введен для возможности сортировки с учетом реального типа данных в столбце."""
        return forceStringEx(self.format(values))

    def checked(self, values):
        return CCol.invalid

    def getForegroundColor(self, values, record=None):
        return CCol.invalid

    def getBackgroundColor(self, values):
        return CCol.invalid

    def paintCell(self, values):
        val = self.color
        if val:
            colorName = forceString(val)
            if colorName:
                return QtCore.QVariant(QtGui.QColor(colorName))
        return CCol.invalid

    def getDecoration(self, values):
        return CCol.invalid

    def invalidateRecordsCache(self):
        pass

    def isRTF(self):
        return self._isRTF

    def isEnabled(self):
        return self._enabled

    def isVisible(self):
        return self._visible

    def setVisible(self, isVisible=True):
        self._visible = isVisible


class CTextCol(CCol):
    """
      General text column
    """

    def __init__(self, title, fields, defaultWidth, alignment='l', isRTF=False, toolTipValue=False):
        CCol.__init__(self, title, fields, defaultWidth, alignment, isRTF)
        self._toolTipValue = toolTipValue

    def toolTipValue(self, values):
        if self._toolTipValue:
            return self.format(values)
        return QVariant()


class CIntCol(CCol):
    u"""
      General int column
    """

    def __init__(self, title, fields, defaultWidth, alignment='l', **params):
        CCol.__init__(self, title, fields, defaultWidth, alignment, **params)

    def format(self, values):
        return toVariant(forceInt(values[0]))

    def formatNative(self, values):
        return forceInt(values[0])


class CDecimalCol(CCol):
    u"""
        General Decimal column
    """

    def __init__(self, title, fields, defaultWidth, alignment='l'):
        CCol.__init__(self, title, fields, defaultWidth, alignment)

    def format(self, values):
        return toVariant(forceDecimal(values[0]))

    def formatNative(self, values):
        return forceDecimal(values[0])


class CIndexCol(CCol):
    u"""
      Atronah: Indexes column (increment by 1).
    """

    def __init__(self, title, fields, defaultWidth, alignment='l'):
        CCol.__init__(self, title, fields, defaultWidth, alignment)

    def format(self, values):
        return toVariant(forceInt(values[0]) + 1)

    def formatNative(self, values):
        return forceInt(values[0]) + 1


class CNameCol(CTextCol):
    u"""
      Name column: with appropriate capitalization
    """

    def __init__(self, title, fields, defaultWidth, alignment='l', isRTF=False):
        CTextCol.__init__(self, title, fields, defaultWidth, alignment, isRTF)

    def format(self, values):
        val = unicode(values[0].toString())
        return QVariant(nameCase(val))

    def formatNative(self, values):
        return nameCase(unicode(values[0].toString()))


class CNumCol(CCol):
    u"""
      Numeric column: right aligned
    """

    def __init__(self, title, fields, defaultWidth, alignment='r'):
        CCol.__init__(self, title, fields, defaultWidth, alignment)


class CSumCol(CNumCol):
    u"""
      Numeric column: right aligned, sum formatted
    """
    locale = QLocale()

    def format(self, values):
        sum = forceDouble(values[0])
        return toVariant(self.locale.toString(sum, 'f', 2))

    def formatNative(self, values):
        return forceDouble(values[0])


class CDateCol(CCol):
    u"""
      Date column
    """

    def __init__(self, title, fields, defaultWidth, alignment='l', highlightRedDate=True):
        CCol.__init__(self, title, fields, defaultWidth, alignment)
        self.highlightRedDate = highlightRedDate and QtGui.qApp.highlightRedDate()

    def format(self, values):
        u"""Преобразует дату в строку в формате dd.mm.yy.
        Это не очень удобно. А если нужно иметь 4 цифры года? тогда не нужно тормозить - нужно почитать код..."""
        val = values[0]
        if val and val.type() in (QVariant.Date, QVariant.DateTime):
            val = val.toDate()
            return QVariant(val.toString(Qt.LocaleDate))
        return CCol.invalid

    def formatNative(self, values):
        val = values[0]
        if val and val.type() in (QVariant.Date, QVariant.DateTime):
            return pyDate(val.toDate())
        return datetime.date(datetime.MINYEAR, 1, 1)

    def getForegroundColor(self, values):
        val = values[0]
        date = forceDate(val)
        if self.highlightRedDate and date and QtGui.qApp.calendarInfo.getDayOfWeek(date) in [6, 7]:
            return QVariant(QtGui.QColor(255, 0, 0))
        return QVariant()


class CTimeCol(CCol):
    u"""
      Time column
    """

    def __init__(self, title, fields, defaultWidth, alignment='l'):
        CCol.__init__(self, title, fields, defaultWidth, alignment)

    def format(self, values):
        val = values[0]
        if val.type() in (QVariant.Time, QVariant.DateTime):
            val = val.toTime()
            return QVariant(val.toString(Qt.SystemLocaleShortDate))
        return CCol.invalid

    def formatNative(self, values):
        val = values[0]
        if val and val.type() in (QVariant.Time, QVariant.DateTime):
            return pyTime(val.toTime())
        return datetime.time()


class CDateTimeCol(CDateCol):
    u"""
      Date and time column
    """

    def format(self, values):
        val = values[0]
        if val is not None:
            if val.type() == QVariant.Date:
                val = val.toDate()
                return QVariant(val.toString(Qt.LocaleDate))
            elif val.type() == QVariant.DateTime:
                val = val.toDateTime()
                return QVariant(val.toString(Qt.LocaleDate))
        return CCol.invalid

    def formatNative(self, values):
        val = values[0]
        if val.type() == QVariant.Date:
            return pyDate(val.toDate())
        elif val.type() == QVariant.DateTime:
            return pyDateTime(val.toDateTime())
        return datetime.datetime(datetime.MINYEAR, 1, 1)


class CDateTimeFixedCol(CDateCol):
    """
      Date and time column
    """

    def format(self, values):
        val = values[0]
        if val.type() == QVariant.Date:
            val = val.toDate()
            return QVariant(val.toString('dd.MM.yyyy'))
        elif val.type() == QVariant.DateTime:
            val = val.toDateTime()
            return QVariant(val.toString('dd.MM.yyyy hh:mm'))

        return CCol.invalid

    def formatNative(self, values):
        val = values[0]
        if val.type() == QVariant.Date:
            return pyDate(val.toDate())
        elif val.type() == QVariant.DateTime:
            return pyDateTime(val.toDateTime())
        return datetime.datetime(datetime.MINYEAR, 1, 1)


class CBoolCol(CCol):
    u"""
      Boolean column
    """
    valChecked = QVariant(Qt.Checked)
    valUnchecked = QVariant(Qt.Unchecked)

    def __init__(self, title, fields, defaultWidth, alignment='c'):
        CCol.__init__(self, title, fields, defaultWidth, alignment)

    def format(self, values):
        return CCol.invalid

    def checked(self, values):
        val = values[0]
        if val.toBool():
            return CBoolCol.valChecked
        else:
            return CBoolCol.valUnchecked

    def formatNative(self, values):
        return values[0].toBool()


class CEnumCol(CCol):
    u"""
      Enum column (like sex etc)
    """

    def __init__(self, title, fields, vallist, defaultWidth, alignment='l', notPresentValue=None):
        CCol.__init__(self, title, fields, defaultWidth, alignment)
        self._vallist = vallist.nameMap if isinstance(vallist, type) and issubclass(vallist, CEnum) else vallist
        self._notPresentValue = notPresentValue

    def format(self, values):
        val = values[0]
        val_int, ok = val.toInt()
        i = val_int if ok else None
        if isinstance(self._vallist, dict):
            if i not in self._vallist:
                return QVariant('{%s}' % val.toString() if self._notPresentValue is None else self._notPresentValue)
            else:
                return QVariant(self._vallist[i])
        elif 0 <= i < len(self._vallist):
            return QVariant(self._vallist[i])
        else:
            return QVariant('{%s}' % val.toString() if self._notPresentValue is None else self._notPresentValue)

    def formatNative(self, values):
        val = values[0]
        i = forceInt(val)
        try:
            return self._vallist[i]
        except (IndexError, KeyError):
            return '{%s}' % val.toString()


class CBackRelationCol(CCol):
    def __init__(self,
                 interfaceCol,
                 primaryKey,
                 subTableName,
                 subTableForeignKey,
                 subTableCond,
                 alternativeValuesGetter=None
                 ):
        """
        Создает экземпляр класса для обработки поведения столбца в модели.
        Основная задача класса: подгрузка данных из подчиненной таблицы (относительно базовой таблицы модели)
        Для отображения используется объект CCol, переданный в параметрах (interfaceCol).

        :param interfaceCol: экземпляр класса для представления данных столбца (его отображения)
        :param primaryKey: имя поля, хранящего id базовой записи из основной таблицы модели.
        :param subTableName: имя подчиненной таблицы, хранящей непосредственное значение для столбца.
        :param subTableForeignKey: имя поля в подчиненной таблице, по которому происходит связь с основной таблицей
        :param subTableCond: условие для ограничения выборки из подчиненной таблицы.
        :param alternativeValuesGetter: альтернативный способ (функция) получения значений поля на основе значения prinaryKey.
        """
        super(CBackRelationCol, self).__init__(title=interfaceCol.title(),
                                               fields=[primaryKey],
                                               defaultWidth=interfaceCol.defaultWidth(),
                                               alignment=interfaceCol.alignment())

        self._subTable = QtGui.qApp.db.table(subTableName)
        self._cache = {}
        self._subTableForeignKey = subTableForeignKey
        self._subCol = interfaceCol
        self._subTableCond = subTableCond if isinstance(subTableCond, list) else [subTableCond]
        self._alternativeValuesGetter = alternativeValuesGetter

    def getRelativeValues(self, values):
        masterId = forceRef(values[0])
        if callable(self._alternativeValuesGetter):
            values = self._alternativeValuesGetter(masterId)
        else:
            if not self._cache.has_key(masterId):
                subRecord = QtGui.qApp.db.getRecordEx(table=self._subTable,
                                                      cols='*',
                                                      where=[self._subTable[self._subTableForeignKey].eq(masterId)]
                                                            + self._subTableCond,
                                                      order=u'%s DESC' % self._subTable.idField())
                if not subRecord:
                    subRecord = QtGui.qApp.db.record(self._subTable.name())
                subValues = [subRecord.value(fieldName) for fieldName in self._subCol.fields()]
                self._cache[masterId] = subValues
            values = self._cache[masterId]
        return values

    def format(self, values):
        values = self.getRelativeValues(values)
        return self._subCol.format(values)

    def formatNative(self, values):
        values = self.getRelativeValues(values)
        return self._subCol.formatNative(values)

    def invalidateRecordsCache(self):
        self._cache = {}


class CDesignationCol(CCol):
    u"""
        Ссылка в базу данных с простым разыменованием
    """

    def __init__(self, title, fields, designationChain, defaultWidth, alignment='l', isRTF=False, orgStructFilter=None):
        CCol.__init__(self, title, fields, defaultWidth, alignment, isRTF)
        db = QtGui.qApp.db
        if not isinstance(designationChain, list):
            designationChain = [designationChain]
        self._caches = []
        for info in designationChain:
            tableName = info[0]
            fieldName = info[1]
            idCol = info[2] if len(info) >= 3 else None
            table = db.table(tableName)
            deletedCol = table.hasField('deleted')
            filter = orgStructFilter
            self._caches.append(CTableRecordCache(db, table, fieldName, idCol=idCol, deletedCol=deletedCol, filter=filter))

    def getValues(self, values):
        if values[0] is None:
            return [CCol.invalid] * len(values)
        for cache in self._caches:
            itemId = forceRef(values[0])
            record = cache.get(itemId)
            if not record:
                return [CCol.invalid] * len(values)
            else:
                values = [record.value(idx) for idx in xrange(record.count())]
        return values

    def format(self, values):
        return self.getValues(values)[0]

    def formatNative(self, values):
        return forceString(self.getValues(values)[0])

    def invalidateRecordsCache(self):
        for cache in self._caches:
            cache.invalidate()


class CRefBookCol(CCol):
    u"""
      RefBook column
    """

    def __init__(self, title, fields, tableName, defaultWidth, showFields=CRBComboBox.showName, alignment='l', isRTF=False, cond=''):
        CCol.__init__(self, title, fields, defaultWidth, alignment, isRTF)
        self.data = CRBModelDataCache.getData(tableName, True, '')
        self.showFields = showFields

    def format(self, values):
        id = forceRef(values[0])
        if id:
            return toVariant(self.data.getStringById(id, self.showFields))
        else:
            return CCol.invalid

    def formatNative(self, values):
        id = forceRef(values[0])
        if not id:
            return None
        return self.data.getStringById(id, self.showFields)


class CColorCol(CCol):
    def getBackgroundColor(self, values):
        val = values[0]
        colorName = forceString(val)
        if colorName:
            return QVariant(QtGui.QColor(colorName))
        return CCol.invalid

    def format(self, values):
        return CCol.invalid


class CSortFilterProxyTableModel(QtGui.QSortFilterProxyModel):
    def __init__(self, parent=None):
        QtGui.QSortFilterProxyModel.__init__(self, parent)
        self._idList = []

    def addColumn(self, col):
        return self.sourceModel().addColumn(col)

    def cols(self):
        return self.sourceModel().cols()

    def loadField(self, field):
        self.sourceModel().loadField(field)

    def setTable(self, tableName, recordCacheCapacity=300):
        self.sourceModel().setTable(tableName, recordCacheCapacity)

    def table(self):
        return self.sourceModel().table()

    def recordCache(self):
        return self.sourceModel().recordCache()

    def invalidateRecordsCache(self):
        self.sourceModel().invalidateRecordsCache()

    def setIdList(self, idList, realItemCount=None):
        self.sourceModel().setIdList(idList, realItemCount)

    def idList(self):
        self.updateIdList()
        return self._idList

    def getRealItemCount(self):
        return self.sourceModel().getRealItemCount()

    def getRecordByRow(self, row):
        return self.sourceModel().getRecordByRow(row)

    def getRecordById(self, id):
        return self.sourceModel().getRecordById(id)

    def findItemIdIndex(self, id):
        return self.sourceModel().findItemIdIndex(id)

    def getRecordValues(self, column, row):
        return self.sourceModel().getRecordValues(column, row)

    def canRemoveRow(self, row):
        return self.sourceModel().canRemoveRow(row)

    def canRemoveItem(self, itemId):
        return self.sourceModel().canRemoveItem(itemId)

    def confirmRemoveRow(self, view, row, multiple=False):
        return self.sourceModel().confirmRemoveRow(view, row, multiple)

    def confirmRemoveItem(self, view, itemId, multiple=False):
        return self.sourceModel().confirmRemoveItem(view, itemId, multiple)

    def beforeRemoveItem(self, itemId):
        self.sourceModel().beforeRemoveItem(itemId)

    def afterRemoveItem(self, itemId):
        self.sourceModel().afterRemoveItem(itemId)

    def deleteRecord(self, table, itemId):
        self.sourceModel().deleteRecord(table, itemId)

    def emitItemsCountChanged(self):
        self.sourceModel().emitItemsCountChanged()

    def emitDataChanged(self):
        self.sourceModel().emitDataChanged()

    @QtCore.pyqtSlot()
    def updateIdList(self):
        if self.rowCount() < self.sourceModel().rowCount():
            self._idList = []
            sourceIdList = self.sourceModel().idList()
            for row in xrange(self.rowCount()):
                proxyIndex = self.index(row, 0)
                sourceIndex = self.mapToSource(proxyIndex)
                sourceRow = sourceIndex.row()
                if 0 <= sourceRow < len(sourceIdList):
                    self._idList.append(sourceIdList[sourceRow])
        else:
            self._idList = self.sourceModel().idList()


class CRichTextItemDelegate(QtGui.QStyledItemDelegate):
    def paint(self, painter, option, index):
        option = QtGui.QStyleOptionViewItemV4(option)
        self.initStyleOption(option, index)
        model = index.model()
        if hasattr(model, 'cols'):
            column = index.column()
            col = model.cols()[column]
            if col.isRTF():
                painter.save()
                doc = QtGui.QTextDocument()
                doc.setDefaultFont(option.font)
                doc.setHtml(option.text)
                option.text = ''  # model.data(index, Qt.DisplayRole).toString()
                option.widget.style().drawControl(QtGui.QStyle.CE_ItemViewItem, option, painter)
                painter.translate(option.rect.left(), option.rect.top())
                clip = QRectF(0, 0, option.rect.width(), option.rect.height())
                doc.drawContents(painter, clip)

                painter.restore()
                return
        return QtGui.QStyledItemDelegate.paint(self, painter, option, index)

    def sizeHint(self, option, index):
        option = QtGui.QStyleOptionViewItemV4(option)
        self.initStyleOption(option, index)
        model = index.model()
        if hasattr(model, 'cols'):
            column = index.column()
            col = model.cols()[column]
            if col.isRTF():
                doc = QtGui.QTextDocument()
                doc.setDefaultFont(option.font)
                doc.setHtml(option.text)
                doc.setTextWidth(option.rect.width())
                return QtCore.QSize(doc.idealWidth(), doc.size().height())
        return QtGui.QStyledItemDelegate.sizeHint(self, option, index)


class CTableModel(QAbstractTableModel, object):
    u"""Модель для хранения содержимого таблицы БД"""
    __pyqtSignals__ = ('itemsCountChanged(int)',
                       )
    idFieldName = 'id'
    fetchSize = 20

    def __init__(self, parent, cols=None, tableName='', allowColumnsHiding=False):
        u"""
        :param parent:
        :type cols: list of CCol
        :param tableName:
        :param allowColumnsHiding:
        """
        if not cols:
            cols = []
        QAbstractTableModel.__init__(self, parent)
        self._cols = []
        self._recordsCache = None
        self._table = None
        self._allowColumnsHiding = allowColumnsHiding
        self._loadFields = []
        self._isSorted = False
        self._sortColumn = 0
        self._sortOrder = QtCore.Qt.AscendingOrder

        self.setIdList([])
        self._cols.extend(col for col in cols if col.isEnabled())
        if tableName:
            self.setTable(tableName)

    def addColumn(self, col):
        u"""
        :type col: CCol
        """
        if col.isEnabled():
            self._cols.append(col)
        return col

    def cols(self):
        u"""
        :rtype: list of CCol
        """
        if not self.hasHiddenCols() or not self._allowColumnsHiding:
            return self._cols

        cols = []
        for col in self._cols:
            if col.isVisible():
                cols.append(col)
        return cols

    def hasHiddenCols(self):
        for col in self._cols:
            if col.isVisible() == False:
                return True
        return False

    def loadField(self, field):
        self._loadFields.append(field)

    def setTable(self, tableName, recordCacheCapacity=300):
        db = QtGui.qApp.db
        self._table = db.table(tableName, self.idFieldName)
        loadFields = [self.idFieldName]
        loadFields.extend(self._loadFields)
        for col in self._cols:
            loadFields.extend(col.fields())
        loadFields = set(loadFields)
        if '*' in loadFields:
            loadFields = '*'
        else:
            loadFields = ', '.join([self._table[fieldName].name() for fieldName in loadFields])
        self._recordsCache = CTableRecordCache(db, self._table, loadFields, recordCacheCapacity, idFieldName=self.idFieldName)

    def table(self):
        return self._table

    def recordCache(self):
        return self._recordsCache

    def invalidateRecordsCache(self):
        if self._recordsCache:
            self._recordsCache.invalidate()
        for col in self._cols:
            col.invalidateRecordsCache()

    def setIdList(self, idList, realItemCount=None, resetCache=True):
        self._idList = idList
        self._realItemCount = realItemCount
        self._prevColumn = None
        self._prevRow = None
        self._prevData = None
        if resetCache:
            self.invalidateRecordsCache()
        self._isSorted = False
        self.reset()
        self.emitItemsCountChanged()

    def idList(self):
        return self._idList

    def getRealItemCount(self):
        return self._realItemCount

    def getRecordByRow(self, row):
        id = self._idList[row]
        self._recordsCache.weakFetch(id, self._idList[max(0, row - self.fetchSize):(row + self.fetchSize)])
        return self._recordsCache.get(id)

    def getRecordById(self, id):
        return self._recordsCache.get(id)

    def findItemIdIndex(self, id):
        if id in self._idList:
            return self._idList.index(id)
        else:
            return -1

    def getRecordValues(self, column, row):
        u""" :rtype: (CCol, list[QtCore.QVariant]) """
        col = self._cols[column]
        if self._prevColumn != column or self._prevRow != row or self._prevData is None:
            id = self._idList[row]
            self._recordsCache.weakFetch(id, self._idList[max(0, row - self.fetchSize):(row + self.fetchSize)])
            record = self._recordsCache.get(id)
            self._prevData = col.extractValuesFromRecord(record)
            self._prevColumn = column
            self._prevRow = row
        return col, self._prevData

    def sort(self, column, order=QtCore.Qt.AscendingOrder):
        def sortHelper(row):
            col, values = self.getRecordValues(column, row)
            val = col.formatNative(values)
            return val

        if column != self._sortColumn:
            self._sortColumn = column
            self._isSorted = False
        if order != self._sortOrder:
            self._sortOrder = order
            self._isSorted = False
        if self._idList and not self._isSorted:
            self.setIdList(map(lambda x: self._idList[x],
                               sorted(range(len(self._idList)),
                                      key=lambda x: sortHelper(x),
                                      reverse=order == QtCore.Qt.DescendingOrder)),
                           resetCache=False)
            self._isSorted = True

    def columnCount(self, index=QtCore.QModelIndex()):
        return len(self._cols)

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self._idList)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        column = index.column()
        row = index.row()
        if role == Qt.DisplayRole:  ### or role == Qt.EditRole:
            (col, values) = self.getRecordValues(column, row)
            return col.format(values)
        elif role == Qt.UserRole:
            (col, values) = self.getRecordValues(column, row)
            return values[0]
        elif role == Qt.TextAlignmentRole:
            col = self._cols[column]
            return col.alignment()
        elif role == Qt.CheckStateRole:
            (col, values) = self.getRecordValues(column, row)
            return col.checked(values)
        elif role == Qt.ForegroundRole:
            (col, values) = self.getRecordValues(column, row)
            return col.getForegroundColor(values)
        elif role == Qt.BackgroundRole:
            (col, values) = self.getRecordValues(column, row)
            return col.getBackgroundColor(values)
        elif role == Qt.DecorationRole:
            (col, values) = self.getRecordValues(column, row)
            return col.getDecoration(values)
        elif role == Qt.ToolTipRole:
            (col, values) = self.getRecordValues(column, row)
            return col.toolTipValue(values)
        return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return self._cols[section].title()
            if role == Qt.ToolTipRole:
                return self._cols[section].toolTip()
            if role == Qt.WhatsThisRole:
                return self._cols[section].whatsThis()
        return QVariant()

    def canRemoveRow(self, row):
        return self.canRemoveItem(self._idList[row])

    def canRemoveItem(self, itemId):
        return True

    def confirmRemoveRow(self, view, row, multiple=False):
        return self.confirmRemoveItem(view, self._idList[row], multiple)

    def confirmRemoveItem(self, view, itemId, multiple=False):
        # multiple: запрос относительно одного элемента из множества, нужно предусмотреть досрочный выход из серии вопросов
        # результат: True: можно удалять
        #            False: нельзя удалять
        #            None: удаление прервано
        buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
        if multiple:
            buttons |= QtGui.QMessageBox.Cancel
        mbResult = QtGui.QMessageBox.question(view, u'Внимание!', u'Действительно удалить?', buttons, QtGui.QMessageBox.No)
        return {QtGui.QMessageBox.Yes: True,
                QtGui.QMessageBox.No : False}.get(mbResult, None)

    def beforeRemoveItem(self, itemId):
        pass

    def afterRemoveItem(self, itemId):
        pass

    def removeRow(self, row, parent=QModelIndex()):
        if self._idList and 0 <= row < len(self._idList):
            itemId = self._idList[row]
            if self.canRemoveItem(itemId):
                QtGui.QApplication.setOverrideCursor(QtGui.QCursor(Qt.WaitCursor))
                try:
                    db = QtGui.qApp.db
                    table = self._table
                    db.transaction()
                    try:
                        self.beforeRemoveItem(itemId)
                        self.deleteRecord(table, itemId)
                        self.afterRemoveItem(itemId)
                        db.commit()
                    except:
                        db.rollback()
                        raise
                    self.beginRemoveRows(parent, row, row)
                    del self._idList[row]
                    self.endRemoveRows()
                    self.emitItemsCountChanged()
                    for x in self._cols:
                        if (hasattr(x, 'clearCache')):
                            x.clearCache()
                    return True
                finally:
                    QtGui.QApplication.restoreOverrideCursor()
        return False

    def removeRowList(self, rowList, parent=QModelIndex(), raiseExceptions=False):
        if self._idList:  # and 0<=row<len(self._idList):
            try:
                QtGui.QApplication.setOverrideCursor(QtGui.QCursor(Qt.WaitCursor))
                db = QtGui.qApp.db
                db.transaction()
                table = self._table
                for row in rowList:
                    itemId = self._idList[row]
                    if not self.canRemoveItem(itemId):
                        raise CException(u'cannot remove item with id %i' % itemId)
                    self.beforeRemoveItem(itemId)
                    self.beginRemoveRows(parent, row, row)
                    self.deleteRecord(table, itemId)
                    del self._idList[row]
                    self.endRemoveRows()
                    self.afterRemoveItem(itemId)
                    self.emitItemsCountChanged()
                db.commit()
            except:
                db.rollback()
                if raiseExceptions:
                    raise
            finally:
                QtGui.QApplication.restoreOverrideCursor()

    def removeIdList(self, idList, parent=QModelIndex(), raiseExceptions=False):
        if self._idList:
            try:
                QtGui.QApplication.setOverrideCursor(QtGui.QCursor(Qt.WaitCursor))
                db = QtGui.qApp.db
                db.transaction()
                table = self._table
                for itemId in idList:
                    if itemId in self._idList:
                        row = self._idList.index(itemId)
                        if not self.canRemoveItem(itemId):
                            raise CException(u'cannot remove item with id %i' % itemId)
                        self.beforeRemoveItem(itemId)
                        self.beginRemoveRows(parent, row, row)
                        self.deleteRecord(table, itemId)
                        del self._idList[row]
                        self.endRemoveRows()
                        self.afterRemoveItem(itemId)
                        self.emitItemsCountChanged()
                db.commit()
            except:
                db.rollback()
                if raiseExceptions:
                    raise
            finally:
                QtGui.QApplication.restoreOverrideCursor()

    def deleteRecord(self, table, itemId):
        if table.hasField('deleted'):
            QtGui.qApp.db.markRecordsDeleted(table, table[self.idFieldName].eq(itemId))
        else:
            try:
                QtGui.qApp.db.deleteRecord(table, table[self.idFieldName].eq(itemId))
            except CDatabaseException:
                QMessageBox().critical(None, u'Ошибка', u'Не удалось удалить. Возможно, запись используется другим объектом.')

    def emitItemsCountChanged(self):
        self.emit(QtCore.SIGNAL('itemsCountChanged(int)'), len(self._idList) if self._idList else 0)

    def emitDataChanged(self):
        leftTop = self.index(0, 0)
        rightBottom = self.index(self.rowCount(), self.columnCount())
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), leftTop, rightBottom)


class CDragDropTableModel(CTableModel):
    def __init__(self, parent, cols=None, tableName=''):
        if not cols:
            cols = []
        super(CDragDropTableModel, self).__init__(parent, cols, tableName)

    def flags(self, index):
        flags = super(CDragDropTableModel, self).flags(index)
        if index.isValid():
            return flags | QtCore.Qt.ItemIsDragEnabled
        return flags

    def mimeData(self, indexes):
        idList = set()
        for index in indexes:
            idList.add(forceString(self.idList()[index.row()]))

        mimeData = QMimeData()
        mimeData.setText(u','.join(idList))
        return mimeData


class CSelectionManager(object):
    def __init__(self, parent):
        self.parent = parent
        self.selectedIdList = []

    def updateSelectedCount(self):
        if hasattr(self.parent, 'lblSelectedCount'):
            n = len(self.selectedIdList)
            if n == 0:
                msg = u'ничего не выбрано'
            else:
                msg = u'выбрано ' + formatNum(n, [u'действие', u'действия', u'действий'])
            self.parent.lblSelectedCount.setText(msg)

    def setSelectedIdList(self, selectedIdList):
        self.selectedIdList = selectedIdList

    def getSelectedList(self):
        return self.getSelectedIdList()

    def getSelectedIdList(self):
        return self.selectedIdList

    def setSelected(self, itemId, value):
        present = self.isSelected(itemId)
        if value:
            if not present:
                self.selectedIdList.append(itemId)
                self.updateSelectedCount()
                return True
        else:
            if present:
                self.selectedIdList.remove(itemId)
                self.updateSelectedCount()
                return True
        return False

    def isSelected(self, itemId):
        return itemId in self.selectedIdList

    def clear(self):
        self.selectedIdList = []


class CFindManager(object):
    def __init__(self, parent):
        self.idList = []
        self.cacheByCode = {}
        self.cacheByName = {}

    def setIdList(self, idList):
        self.idList = idList

    def setCacheByCode(self, cacheByCode):
        self.cacheByCode = cacheByCode

    def setCacheByName(self, cacheByName):
        self.cacheByName = cacheByName

    def getIdList(self):
        return self.idList

    def findByCode(self, value):
        uCode = unicode(value).upper()
        codes = self.cacheByCode.keys()
        codes.sort()
        idList = []
        for c in codes:
            if unicode(c).startswith(uCode):
                idList.append(self.idList[self.cacheByCode[c]])
        return idList

    def findByName(self, name):
        uName = unicode(name).upper()
        names = self.cacheByName.keys()
        idList = []
        for n in names:
            if (unicode(n.upper()).find(uName)) != -1:
                idList.append(self.idList[self.cacheByName[n]])
        return idList

