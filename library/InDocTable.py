# -*- coding: utf-8 -*-

from PyQt4 import QtSql
from __builtin__ import getattr

from PyQt4.QtGui import QAbstractItemView, QTableWidgetItem

from KLADR.KLADRModel import CKladrTreeModel
from KLADR.kladrComboxes import CKLADRComboBox
from Registry.ClientRecordProperties import CRecordProperties
from Reports.ReportBase import *
from Users.Rights import urAccessCrossingDates
from library.CComboBox import CComboBox
from library.DateEdit import CDateEdit
from library.Enum import CEnum
from library.MovingRowDialog import CMovingRowDialog
from library.PreferencesMixin import CPreferencesMixin
from library.Utils import *
from library.crbcombobox import CRBComboBox, CRBLikeEnumModel, CRBModelDataCache
from library.database import CTableRecordCache


def forcePyType(val):
    t = val.type()
    if t == QVariant.Bool:
        return val.toBool()
    elif t == QVariant.Date:
        return val.toDate()
    elif t == QVariant.DateTime:
        return val.toDateTime()
    elif t == QVariant.Double:
        return val.toDouble()[0]
    elif t == QVariant.Int:
        return val.toInt()[0]
    else:
        return unicode(val.toString())


class CInDocTableCol(object):
    # copied from CCol.alg
    alg = {
        'l': QVariant(Qt.AlignLeft + Qt.AlignVCenter),
        'c': QVariant(Qt.AlignHCenter + Qt.AlignVCenter),
        'r': QVariant(Qt.AlignRight + Qt.AlignVCenter),
        'j': QVariant(Qt.AlignJustify + Qt.AlignVCenter)
    }

    # Поле БД с созданием соответствующего виджета для редактирования
    def __init__(self, title, fieldName, width, **params):
        self._title = toVariant(title)
        self._fieldName = fieldName
        self._width = width
        self._toolTip = toVariant(params.get('toolTip', None))
        self._whatsThis = toVariant(params.get('whatThis', None))
        self._external = params.get('external', False)
        self._valueType = params.get('valueType', None)
        self._readOnly = params.get('readOnly', False)
        self._maxLength = params.get('maxLength', None)
        self._inputMask = params.get('inputMask', None)
        self._sortable = params.get('sortable', False)
        self._useNaturalStringCompare = params.get('naturalStringCompare', True)
        self._alignmentChar = params.get('alignment', 'l')
        self._isRTF = params.get('isRTF', False)
        self._completerModel = None
        self._completer = None
        self._completerCode = None

    def setCompleter(self, tableName=None, fieldName=u'name', completerCode=None):
        if tableName:
            self._completerModel = QtSql.QSqlTableModel(None, QtSql.QSqlDatabase.database('vistamed'))
            self._completerModel.setTable(tableName)
            self._completerCode = completerCode
            if completerCode:
                self._completerModel.setFilter("code like '%s'" % completerCode)
            self._completer = QtGui.QCompleter()
            self._completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
            self._completer.setCompletionMode(QtGui.QCompleter.PopupCompletion)

            self._completer.setCompletionColumn(max(0, self._completerModel.fieldIndex(fieldName)))
        else:
            self._completerModel = None
            self._completer = None

    def setTitle(self, title):
        self._title = toVariant(title)

    def title(self):
        return self._title

    def setToolTip(self, toolTip):
        self._toolTip = toVariant(toolTip)
        return self

    def toolTip(self):
        return self._toolTip

    def setWhatsThis(self, whatsThis):
        self._whatsThis = toVariant(whatsThis)
        return self

    def whatsThis(self):
        return self._whatsThis

    def fieldName(self):
        return self._fieldName

    def width(self):
        return self._width

    def setExternal(self, external):
        # Внешняя колонка есть в таблице БД, но не хранится в модели
        self._external = external

    def external(self):
        # Внешняя колонка есть в таблице БД, но не хранится в модели
        # Может наоборот: не хранится в БД, но есть в модели
        return self._external

    def setValueType(self, valueType):
        self._valueType = valueType

    def valueType(self):
        return self._valueType

    def setReadOnly(self, readOnly=True):
        self._readOnly = readOnly
        return self

    def readOnly(self):
        return self._readOnly

    def setSortable(self, value=True):
        self._sortable = value
        return self

    def sortable(self):
        return self._sortable

    def useNaturalStringCompare(self):
        return self._useNaturalStringCompare

    def flags(self, index=None):
        result = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if not self._readOnly:
            result |= Qt.ItemIsEditable
        return result

    def toString(self, val, record):
        # строковое представление (тип - QVariant!)
        return val

    def toSortString(self, val, record):
        return forcePyType(self.toString(val, record))

    def toStatusTip(self, val, record):
        return self.toString(val, record)

    def toCheckState(self, val, record):
        return QVariant()

    def getForegroundColor(self, val, record):
        return QVariant()

    def getBackgroundColor(self, val, record):
        return QVariant()

    def createEditor(self, parent):
        editor = QtGui.QLineEdit(parent)
        if self._completer is not None and self._completerModel.select():
            self._completer.setModel(self._completerModel)
            editor.setCompleter(self._completer)
        if self._maxLength:
            editor.setMaxLength(self._maxLength)
        if self._inputMask:
            editor.setInputMask(self._inputMask)
        return editor

    def setEditorData(self, editor, value, record):
        editor.setText(forceStringEx(value))

    def getEditorData(self, editor):
        """
        Получить значение из редактора.

        :param editor: редактор, значение из которого необходимо получить.
        :type editor: QVariant
        :return:
        """
        text = trim(editor.text())
        if text:
            if self._completer:
                variantText = QtCore.QVariant(text)
                completionColumn = self._completer.completionColumn()
                startIndex = self._completerModel.index(0,
                                                        completionColumn)
                if not self._completerModel.match(startIndex,
                                                  QtCore.Qt.DisplayRole,
                                                  variantText):
                    db = QtGui.qApp.db
                    completerTable = db.table('rbTextDataCompleter')
                    newRecord = completerTable.newRecord()
                    if newRecord.contains(u'code') and self._completerCode is not None:
                        newRecord.setValue(u'code', QtCore.QVariant(self._completerCode))
                    newRecord.setValue(self._completer.completionColumn(), variantText)
                    db.insertRecord(completerTable, newRecord)
            return toVariant(text)
        else:
            return QVariant()

    def isRTF(self):
        return self._isRTF

    def saveExternalData(self, rowRecord):
        """
        Сохраняет внешние данные, с которыми работает столбец, используя переданный экземпляр QSqlRecord строки.
        Необходимо для работы столбцов, которые обеспечивают доступ к данным из других таблиц (связь 1:1 или даже 1:М).

        :param rowRecord: экземпляр QSqlRecord-строки, для которой требуется сохранить внешние данные.
        """
        pass

    def alignment(self):
        return CInDocTableCol.alg[self._alignmentChar]


class CBackRelationInDockTableCol(CInDocTableCol):
    def __init__(self,
                 interfaceCol,
                 primaryKey,
                 surrogateFieldName,
                 subTableName,
                 subTableForeignKey,
                 subTableCond,
                 subTableNewRecord,
                 **params):
        """
        Создает экземпляр класса для обработки поведения столбца в модели.
        Основная задача класса: подгрузка и сохранение данных из подчиненной таблицы (относительно базовой таблицы модели)
        Для отображения и редактирования используется объект CInDocTableCol, переданный в параметрах (interfaceCol).

        :param interfaceCol: экземпляр класса для представления данных столбца (его отображения и редактирования)
        :param primaryKey: имя поля, хранящего id базовой записи из основной таблицы модели.
        :param surrogateFieldName: имя поле для временного хранения значения в базовой записи.
        :param subTableName: имя подчиненной таблицы, хранящей непосредственное значение для столбца.
        :param subTableForeignKey: имя поля в подчиненной таблице, по которому происходит связь с основной таблицей
        :param subTableCond: условие для ограничения выборки из подчиненной таблицы.
        :param subTableNewRecord: новая запись для подчиненной таблицы на случай записи ранее отсутствующего значения.
        :param params: дополнительные параметры.
        """
        super(CBackRelationInDockTableCol, self).__init__(title=interfaceCol.title(),
                                                          fieldName=surrogateFieldName,
                                                          width=interfaceCol.width(),
                                                          **params)
        self.setExternal(True)

        self._primaryKey = primaryKey
        self._surrogateFieldName = surrogateFieldName
        self._subTable = QtGui.qApp.db.table(subTableName)
        self._subRecordCache = {}
        self._subTableForeignKey = subTableForeignKey
        self._subTableNewRecord = subTableNewRecord
        self._subCol = interfaceCol
        self._subTableCond = subTableCond if isinstance(subTableCond, list) else [subTableCond]

    def subCol(self):
        return self._subCol

    def createEditor(self, parent):
        return self._subCol.createEditor(parent)

    def flags(self, index=None):
        return self._subCol.flags(index)

    def toString(self, val, record):
        return self._subCol.toString(val, record)

    def toStatusTip(self, val, record):
        return self._subCol.toStatusTip(val, record)

    def toCheckState(self, val, record):
        return self._subCol.toCheckState(val, record)

    def _getSubRecord(self, masterId):
        subRecord = self._subRecordCache.setdefault(masterId, None)
        if subRecord is None:
            subRecord = QtGui.qApp.db.getRecordEx(table=self._subTable,
                                                  cols='*',
                                                  where=[self._subTable[self._subTableForeignKey].eq(masterId)]
                                                        + self._subTableCond,
                                                  order=u'%s DESC' % self._subTable.idField())
            if subRecord is None:
                subRecord = QtSql.QSqlRecord(self._subTableNewRecord)
                subRecord.setValue(self._subTableForeignKey, QtCore.QVariant(masterId))
            self._subRecordCache[masterId] = subRecord
        return subRecord

    def setEditorData(self, editor, value, record):
        masterId = forceRef(record.value(self._primaryKey))
        subRecord = self._getSubRecord(masterId)
        # Если полученное из модели значение пустое
        if not value.isValid():
            # то попытаться вытянуть его из базы
            value = subRecord.value(self._subCol.fieldName())

        self._subCol.setEditorData(editor, value, subRecord)

    def getEditorData(self, editor):
        return self._subCol.getEditorData(editor)

    def saveExternalData(self, rowRecord):
        masterId = forceRef(rowRecord.value(self._primaryKey))
        value = rowRecord.value(self._surrogateFieldName)

        subRecord = self._getSubRecord(masterId)
        subRecord.setValue(self._subCol.fieldName(), value)
        subRecord.setValue(self._subTableForeignKey, QtCore.QVariant(masterId))
        subRecordId = QtGui.qApp.db.insertOrUpdate(self._subTable, subRecord)
        subRecord.setValue(self._subTable.idField(), QtCore.QVariant(subRecordId))

    def setEndDate(self, endDate):
        self._subCol.setEndDate(endDate)


class CKLADRInDocTableCol(CInDocTableCol, QObject):
    __pyqtSignals__ = ('toCheckData(QString)',
                       )

    def __init__(self, title, fieldName, width, **params):
        CInDocTableCol.__init__(self, title, fieldName, width, **params)
        QObject.__init__(self)
        self.editorModel = CKladrTreeModel(None)
        self.editorModel.setAllSelectable(True)
        self.codeIsValid = True
        self.currentCode = None

    def setCodeIsValid(self, val):
        self.codeIsValid = val

    def createEditor(self, parent):
        editor = CKLADRComboBox(parent)
        editor._model = self.editorModel
        editor.setModel(self.editorModel)
        editor._popupView.treeModel = self.editorModel
        editor._popupView.treeView.setModel(self.editorModel)
        return editor

    def setEditorData(self, editor, value, record):
        val = forceString(value)
        self.currentCode = val
        editor.setCode(val)

    def getEditorData(self, editor):
        val = QString(editor.code())
        self.emit(QtCore.SIGNAL('toCheckData(QString)'), val)
        self.currentCode = None
        if self.codeIsValid:
            return toVariant(val)
        else:
            return QVariant()

    def toString(self, val, record):
        return QtGui.qApp.db.translate('kladr.KLADR', 'CODE', forceString(val), 'CONCAT(NAME,\' \', SOCR)', idFieldName='CODE')


class CEnumInDocTableCol(CInDocTableCol):
    # В базе данных хранится номер,
    # а на экране рисуется комбо-бокс с соотв. значениями
    def __init__(self, title, fieldName, width, values, **params):
        CInDocTableCol.__init__(self, title, fieldName, width, **params)
        self._addNone = params.get('addNone', False)
        self.values = values.nameMap if isinstance(values, type) and issubclass(values, CEnum) else values

    def toString(self, val, record):
        if self._addNone and val.isNull():
            return toVariant(u'Не задано')
        return toVariant(self.values[forceInt(val)])

    def createEditor(self, parent):
        editor = CComboBox(parent)
        if self._addNone:
            editor.addItem(u'Не задано', toVariant(None))
        for value, title in enumerate(self.values):
            editor.addItem(title, value)
        return editor

    def setEditorData(self, editor, value, record):
        idx = editor.findData(value)
        if idx in xrange(editor.count()):
            editor.setCurrentIndex(forceInt(idx))

    def getEditorData(self, editor):
        idx = editor.currentIndex()
        return editor.itemData(idx)


class CDesignationInDocTableCol(CInDocTableCol):
    # аналогично CDesignationCol
    def __init__(self, title, fieldName, designationChain, defaultWidth, **params):
        CInDocTableCol.__init__(self, title, fieldName, defaultWidth, **params)
        self._addNone = params.get('addNone', False)
        # Получение фильтра, по которому будут формироваться доступные для выбора значения при редактировании поля.
        # Фильтр будет применяться к таблице, указанной первой в designationChain.
        # Если в качестве фильтра будет передан кортеж из двух строк, то он будет восприниматься, как фильтр
        # <Таблица_модели>.<первое_имя_из_кортежа> = <Первая_таблица_поля>.<второе_имя_из_кортежа>
        # или
        # masterRecord[self._editorValueFilter[0]] = self._caches[0].table[self._editorValueFilter[0]]
        self._editorValueFilter = params.get('editorValueFilter', u'')
        db = QtGui.qApp.db
        if not isinstance(designationChain, list):
            designationChain = [designationChain]
        self._caches = []
        for tableName, fieldName in designationChain:
            self._caches.append(CTableRecordCache(db, db.table(tableName), fieldName))

        # словарь, хранящий для каждого условия фильтрации, список id, доступных для выбора для текущего столбца
        self._mapMasterIdToItemIdList = {}
        self.setReadOnly(True)

    def setReadOnly(self, readOnly):
        if not self._caches:
            readOnly = True
        super(CDesignationInDocTableCol, self).setReadOnly(readOnly)
        return self

    def createEditor(self, parent):
        return CComboBox(parent)

    def setEditorData(self, editor, value, record):
        subTable = self._caches[0].table
        cond = self._editorValueFilter
        if isinstance(cond, tuple) and len(cond) == 2:
            masterFieldName, slaveFieldName = self._editorValueFilter
            masterValue = record.value(masterFieldName)
            cond = subTable[slaveFieldName].eq(masterValue)

        if not self._mapMasterIdToItemIdList.has_key(cond):
            self._mapMasterIdToItemIdList[cond] = QtGui.qApp.db.getIdList(table=subTable,
                                                                          where=cond)
        editor.clear()
        if self._addNone:
            editor.addItem(u'Не выбрано', userData=toVariant(None))

        for itemId in self._mapMasterIdToItemIdList[cond]:
            itemText = forceString(self.toString(itemId, record))
            editor.addItem(itemText, userData=toVariant(itemId))

    def getEditorData(self, editor):
        itemIndex = editor.currentIndex()
        return editor.itemData(itemIndex)

    def toString(self, val, record):
        for cache in self._caches:
            itemId = forceRef(val)
            record = cache.get(itemId)
            if not record:
                return toVariant('')
            else:
                val = record.value(0)
                # На случай, когда нет ссылки на id в следующей таблицы цепочки
                # Но для текущей таблицы указаны резервные поля (нужно для полей вида freeInput)
                if val.isNull() and record.count() > 1:
                    for fieldIdx in xrange(1, record.count()):
                        val = record.value(fieldIdx)
                        if not val.isNull():
                            return toVariant(val)
        return val


class CSelectStrInDocTableCol(CEnumInDocTableCol):
    # В базе данных хранится строка,
    # а на экране рисуется комбо-бокс с соотв. значениями

    def __init__(self, title, fieldName, width, values, **params):
        CEnumInDocTableCol.__init__(self, title, fieldName, width, values, **params)

    def toString(self, val, record):
        str = forceString(val).lower()
        for item in self.values:
            if item.lower() == str:
                return toVariant(item)
        return toVariant(u'{' + forceString(val) + u'}')

    def setEditorData(self, editor, value, record):
        index = editor.findText(forceString(value), Qt.MatchFixedString)
        if index < 0:
            index = 0
        editor.setCurrentIndex(index)

    def getEditorData(self, editor):
        return toVariant(editor.currentText())


class CRBLikeEnumInDocTableCol(CInDocTableCol):
    # Чем отличается от CEnumInDocTableCol
    def __init__(self, title, fieldName, width, values, **params):
        CInDocTableCol.__init__(self, title, fieldName, width, **params)
        self.values = values
        self.showFields = params.get('showFields', CRBComboBox.showName)
        self.prefferedWidth = params.get('prefferedWidth', None)
        self.model = CRBLikeEnumModel(None)
        self.model.setValues(self.values)

    def toString(self, val, record):
        text = self.model.d.getStringById(forceInt(val), self.showFields)
        return toVariant(text)

    def toStatusTip(self, val, record):
        text = self.model.d.getStringById(forceInt(val), CRBComboBox.showName)
        return toVariant(text)

    def createEditor(self, parent):
        editor = CRBComboBox(parent)
        editor.setShowFields(self.showFields)
        editor.setPrefferedWidth(self.prefferedWidth)
        model = CRBLikeEnumModel(editor)
        model.setValues(self.values)
        editor.setModel(model)
        return editor

    def setEditorData(self, editor, value, record):
        editor.setCurrentIndex(forceInt(value))

    def getEditorData(self, editor):
        return toVariant(editor.currentIndex())


class CRBInDocTableCol(CInDocTableCol):
    def __init__(self, title, fieldName, width, tableName, **params):
        CInDocTableCol.__init__(self, title, fieldName, width, **params)
        self.tableName = tableName
        self.filter = params.get('filter', '')
        self.addNone = params.get('addNone', True)
        self.showFields = params.get('showFields', CRBComboBox.showName)
        self.order = params.get('order', None)
        self.prefferedWidth = params.get('prefferedWidth', None)
        self._codeFieldName = params.get('codeFieldName', None)

    def toString(self, val, record):
        cache = CRBModelDataCache.getData(self.tableName, True, codeFieldName=self._codeFieldName)
        text = cache.getStringById(forceInt(val), self.showFields)
        return toVariant(text)

    def toStatusTip(self, val, record):
        cache = CRBModelDataCache.getData(self.tableName, True, codeFieldName=self._codeFieldName)
        text = cache.getStringById(forceInt(val), CRBComboBox.showName)
        return toVariant(text)

    def getCode(self, itemId):
        cache = CRBModelDataCache.getData(self.tableName, True, codeFieldName=self._codeFieldName)
        return cache.getCodeById(itemId)

    def createEditor(self, parent):
        editor = CRBComboBox(parent)
        editor.setRTF(self._isRTF)
        editor.setTable(self.tableName, addNone=self.addNone, filter=self.filter, order=self.order, codeFieldName=self._codeFieldName)
        editor.setShowFields(self.showFields)
        editor.setPrefferedWidth(self.prefferedWidth)
        return editor

    def setEditorData(self, editor, value, record):
        editor.setValue(forceInt(value))

    def getEditorData(self, editor):
        return toVariant(editor.value())

    # Пока сортируем по коду (код - числовой). Можно и настраивать :)
    def toSortString(self, val, record):
        cache = CRBModelDataCache.getData(self.tableName, True, codeFieldName=self._codeFieldName)
        return forceString(cache.getStringById(forceInt(val), CRBComboBox.showCode))

    def setFilter(self, cond):
        self.filter = cond


class CRBInDocTableColSearch(CRBInDocTableCol):
    def __init__(self, title, fieldName, width, tableName, **params):
        CRBInDocTableCol.__init__(self, title, fieldName, width, tableName, **params)

    def createEditor(self, parent):
        editor = CRBComboBox(parent)
        editor.setRTF(self._isRTF)
        editor.setTable(self.tableName, addNone=self.addNone, filter=self.filter, order=self.order)
        editor.setShowFields(self.showFields)
        editor.setPrefferedWidth(self.prefferedWidth)
        return editor


class CCodeNameInDocTableCol(CRBInDocTableCol):
    # u"""Колонка, в которой отображается и код, и имя"""
    def toString(self, val, record):
        id = forceInt(val)
        if id:
            rec = QtGui.qApp.db.getRecord(self.tableName, ['code', 'name'], forceInt(val))
            return toVariant(rec.value('code').toString() + " - " + rec.value('name').toString())
        else:
            return toVariant(None)


class CCodeRefInDocTableCol(CRBInDocTableCol):
    # u"""Ссылка на справочник не по id, а по code"""
    def toString(self, val, record):
        code = forceString(val)
        if len(code):
            result = QtGui.qApp.db.query("""
                                            SELECT id, name
                                            from %s
                                            WHERE code = '%s'
                                        """ % (self.tableName, code))
            if result.first():
                rec = result.record()
                return toVariant(code + " - " + rec.value("name").toString())
        return toVariant("")

    def setEditorData(self, editor, value, record):
        editor.setCode(forceString(value))

    def getEditorData(self, editor):
        return toVariant(editor.code())


class CDetachmentReasonTableCol(CRBInDocTableCol):
    def setEditorData(self, editor, value, record):
        editor.setFilter('attachType_id = %s OR attachType_id IS NULL' % forceString(record.value('attachType_id')))


class CDateInDocTableCol(CInDocTableCol):
    def __init__(self, title, fieldName, width, **params):
        CInDocTableCol.__init__(self, title, fieldName, width, **params)
        self.highlightRedDate = params.get('highlightRedDate', True) and QtGui.qApp.highlightRedDate()
        self.canBeEmpty = params.get('canBeEmpty', False)
        self.defaultDate = params.get('defaultDate', QDate.currentDate())

    def toString(self, val, record):
        if not val.isNull():
            date = val.toDate()
            if date.isValid():
                return toVariant(formatDate(date))
        return QVariant()

    def toSortString(self, val, record):
        return forcePyType(val)

    def useNaturalStringCompare(self):
        return False

    def getForegroundColor(self, val, record):
        date = forceDate(val)
        if self.highlightRedDate and date and QtGui.qApp.calendarInfo.getDayOfWeek(date) in [6, 7]:
            return QVariant(QtGui.QColor(255, 0, 0))
        return QVariant()

    def createEditor(self, parent):
        editor = CDateEdit(parent)
        editor.setHighlightRedDate(self.highlightRedDate)
        editor.canBeEmpty(self.canBeEmpty)
        return editor

    def setEditorData(self, editor, value, record):
        value = value.toDate()
        if not value.isValid() and not self.canBeEmpty:
            value = self.defaultDate
        editor.setDate(value)

    def getEditorData(self, editor):
        value = editor.date()
        if value.isValid():
            return toVariant(value)
        elif self.canBeEmpty:
            return QVariant()
        else:
            return QVariant(self.defaultDate)


class CTimeInDocTableCol(CInDocTableCol):
    def __init__(self, title, fieldName, width, **params):
        CInDocTableCol.__init__(self, title, fieldName, width, **params)

    def toString(self, val, record):
        if not val.isNull():
            time = val.toTime()
            if time.isValid():
                return toVariant(formatTime(time))
        return QVariant()

    def toSortString(self, val, record):
        return forcePyType(val)

    def useNaturalStringCompare(self):
        return False

    def createEditor(self, parent):
        editor = QtGui.QTimeEdit(parent)
        if self._inputMask:
            editor.setDisplayFormat(self._inputMask)
        return editor

    def setEditorData(self, editor, value, record):
        editor.setTime(value.toTime())

    def getEditorData(self, editor):
        value = editor.time()
        if value.isValid():
            return toVariant(value)
        else:
            return QVariant()


class CDateTimeInDocTableCol(CInDocTableCol):
    def __init__(self, title, fieldName, width, **params):
        CInDocTableCol.__init__(self, title, fieldName, width, **params)
        self.highlightRedDate = params.get('highlightRedDate', True)

    def toString(self, val, record):
        if not val.isNull():
            datetime = val.toDateTime()
            if datetime.isValid():
                return toVariant(forceDateTime(datetime))
        return QVariant()

    def toSortString(self, val, record):
        return forcePyType(val)

    def useNaturalStringCompare(self):
        return False

    def getForegroundColor(self, val, record):
        date = forceDate(val)
        if self.highlightRedDate and date and QtGui.qApp.calendarInfo.getDayOfWeek(date) in [6, 7]:
            return QVariant(QtGui.QColor(255, 0, 0))
        return QVariant()


class CBoolInDocTableCol(CInDocTableCol):
    def __init__(self, title, fieldName, width, **params):
        CInDocTableCol.__init__(self, title, fieldName, width, **params)

    def flags(self, index=None):
        result = CInDocTableCol.flags(self)
        if result & Qt.ItemIsEditable:
            result = (result & ~Qt.ItemIsEditable) | Qt.ItemIsUserCheckable
        return result

    def toCheckState(self, val, record):
        if forceInt(val) == 0:
            return QVariant(Qt.Unchecked)
        else:
            return QVariant(Qt.Checked)

    def toString(self, val, record):
        return QVariant()

    def toSortString(self, val, record):
        return forcePyType(val)

    def createEditor(self, parent):
        editor = QtGui.QCheckBox(parent)
        return editor

    def setEditorData(self, editor, value, record):
        editor.setChecked(forceInt(value) != 0)

    def getEditorData(self, editor):
        return toVariant(1 if editor.isChecked() else 0)


class CIntInDocTableCol(CInDocTableCol):
    def __init__(self, title, fieldName, width, **params):
        CInDocTableCol.__init__(self, title, fieldName, width, **params)
        self.low = params.get('low', 0)
        self.high = params.get('high', 100)

    def createEditor(self, parent):
        editor = QtGui.QSpinBox(parent)
        editor.setMinimum(self.low)
        editor.setMaximum(self.high)
        return editor

    def setEditorData(self, editor, value, record):
        editor.setValue(forceInt(value))
        editor.selectAll()

    def getEditorData(self, editor):
        return toVariant(editor.value())


class CFloatInDocTableCol(CInDocTableCol):
    def __init__(self, title, fieldName, width, **params):
        CInDocTableCol.__init__(self, title, fieldName, width, **params)
        self.precision = params.get('precision', None)
        self.min = params.get('min', None)
        self.max = params.get('max', None)

    def _toString(self, value):
        if value.isNull():
            return None
        s = QString()
        if self.precision is None:
            s.setNum(value.toDouble()[0])
        else:
            # atronah: добавил round(), так как setNum(0.3450, 'f', 2) = 0.34, а не 0.35, как при математическом принципе округдения
            s.setNum(round(value.toDouble()[0], self.precision), 'f', self.precision)
        return s

    def toString(self, value, record):
        return toVariant(self._toString(value))

    def createEditor(self, parent):
        editor = QtGui.QLineEdit(parent)
        validator = QtGui.QDoubleValidator(editor)
        if self.min is not None:
            validator.setBottom(self.min)
        if self.max > self.min:
            validator.setTop(self.max)
        if self.precision is not None:
            validator.setDecimals(self.precision)
        editor.setValidator(validator)
        return editor

    def setEditorData(self, editor, value, record):
        s = self._toString(value)
        editor.setText('' if s is None else s)
        editor.selectAll()
        self._prevValue = editor.text()

    def getEditorData(self, editor):
        validator = editor.validator()
        validateState = validator.validate(editor.text(), 0)[0]
        value = editor.text() if validateState == QtGui.QValidator.Acceptable else self._prevValue
        return toVariant(value.toDouble()[0])


## Столбец только для чтения с вычисляемым значением.
class CCalculatedInDocTableCol(CInDocTableCol):
    ##
    # @param additionalFieldList: дополнительные поля (помимо fieldName), которые необходимы для вычисления отображаемого значения.
    # @param func: функция, производящая вычисление отображаемого значения на основе значений аргументов.
    #                При этом количество аргументов этой функции должно соответствовать кол-ву полей в additionalFieldList + 1 (поле из fieldName)
    def __init__(self, title, fieldName, width, **params):
        super(CCalculatedInDocTableCol, self).__init__(title, fieldName, width, **params)
        super(CCalculatedInDocTableCol, self).setReadOnly(True)
        self.additionalFieldList = params.get('additionalFieldList', [])
        self.calculateFunc = params.get('calculateFunc', lambda fieldValue: fieldValue)

    def setReadOnly(self, isReadOnly):
        pass  # Запрет на изменение редактируемости

    def toString(self, val, record):
        result = val
        if callable(self.calculateFunc):
            argList = [val] + [record.value(fieldName) for fieldName in self.additionalFieldList]
            result = self.calculateFunc(*argList)
        return toVariant(result)


class CRecordListModel(QAbstractTableModel, object):
    __pyqtSignals__ = ('editInProgress(bool)',
                       )

    # модель для взаимодействия со списком QSqlRecord; возможно редактирование
    def __init__(self, parent, cols=None):
        QAbstractTableModel.__init__(self, parent)
        self._cols = cols or []
        self._hiddenCols = []
        self._items = []
        self._mapFieldNameToCol = dict((col.fieldName(), idx) for idx, col in enumerate(self._cols))
        self._enableAppendLine = False
        self._isDirty = False
        self._extColsPresent = False

        self.rowsInserted.connect(self.markAsDirty)
        self.rowsRemoved.connect(self.markAsDirty)
        #        self.rowsMoved.connect(self.markAsDirty)
        self.dataChanged.connect(self.markAsDirty)

    @QtCore.pyqtSlot(bool)
    def setDirty(self, isDirty):
        self._isDirty = isDirty

    def isDirty(self):
        return self._isDirty

    @QtCore.pyqtSlot()
    def markAsDirty(self):
        self.setDirty(True)

    def setEnableAppendLine(self, enableAppendLine=True):
        self._enableAppendLine = enableAppendLine

    def addCol(self, col):
        self._mapFieldNameToCol[col.fieldName()] = len(self._cols)
        self._cols.append(col)
        return col

    def removeCol(self, index):
        if index in xrange(self.columnCount()):
            self.beginRemoveColumns(QtCore.QModelIndex(), index, index)
            removedCol = self.cols().pop(index)
            self._mapFieldNameToCol.pop(removedCol.fieldName())
            self.endRemoveColumns()

    def insertCol(self, idx, col):
        if idx < 0:
            idx = 0
        elif idx > len(self._cols):
            idx = len(self._cols)

        self._cols.insert(idx, col)
        for colName, existIdx in self._mapFieldNameToCol.items():
            if idx <= existIdx:
                self._mapFieldNameToCol[colName] = existIdx + 1
        self._mapFieldNameToCol[col.fieldName()] = idx

    def addHiddenCol(self, col):
        # col - название поля
        self._hiddenCols.append(col)
        return col

    def addExtCol(self, col, valType):
        self._extColsPresent = True
        col.setExternal(True)
        col.setValueType(valType)
        self._mapFieldNameToCol[col.fieldName()] = len(self._cols)
        self._cols.append(col)
        return col

    def getColIndex(self, fieldName):
        return self._mapFieldNameToCol.get(fieldName, -1)

    def getCol(self, fieldName):
        idx = self.getColIndex(fieldName)
        return self.cols()[idx] if idx != -1 and idx in xrange(len(self.cols())) else None

    def setExtColsPresent(self, val=True):
        self._extColsPresent = val

    def cols(self):
        return self._cols

    def hiddenCols(self):
        return self._hiddenCols

    def clearItems(self):
        self._items = []
        self.setDirty(False)
        self.reset()

    def setItems(self, items):
        if id(self._items) != id(items):
            self._items = items
            self.setDirty(False)
            self.reset()

    def items(self):
        return self._items

    def columnCount(self, index=QtCore.QModelIndex()):
        return len(self._cols)

    def flags(self, index):
        column = index.column()
        flags = self._cols[column].flags()
        if self.cellReadOnly(index):
            flags = flags & (~Qt.ItemIsEditable) & (~Qt.ItemIsUserCheckable)
        return flags

    def cellReadOnly(self, index):
        return False

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self._items) + (1 if self._enableAppendLine else 0)

    def getEmptyRecord(self):
        record = QtSql.QSqlRecord()
        for col in self.cols():
            fieldName = col.fieldName()
            if not record.contains(fieldName):
                fieldType = col.valueType()
                if fieldType is not None:
                    record.append(QtSql.QSqlField(fieldName, fieldType))
        return record

    def getRecordByRow(self, row):
        return self._items[row] if 0 <= row < len(self._items) else None

    def insertRecord(self, row, record):
        self.beginInsertRows(QModelIndex(), row, row)
        self._items.insert(row, record)
        self.endInsertRows()

    def addRecord(self, record):
        self.insertRecord(len(self._items), record)

    # def upRow(self, row):
    #     if 0 < row < len(self._items):
    #         self._items[row-1], self._items[row] = self._items[row], self._items[row-1]
    #         self.emitRowsChanged(row-1, row)
    #         return True
    #     else:
    #         return False
    #
    # def downRow(self, row):
    #     if 0 <= row < len(self._items)-1:
    #         self._items[row+1], self._items[row] = self._items[row], self._items[row+1]
    #         self.emitRowsChanged(row, row+1)
    #         return True
    #     else:
    #         return False

    def upRow(self, row, pos=1):
        if 0 < row < len(self._items):
            for x in range(pos):
                self._items[row - x], self._items[row - (x + 1)] = self._items[row - (x + 1)], self._items[row - x]
                self.emitRowsChanged(row - (x + 1), row - x)
            return True
        else:
            return False

    def downRow(self, row, pos=1):
        if 0 <= row < len(self._items) - pos:
            for x in range(pos):
                self._items[row + x], self._items[row + (x + 1)] = self._items[row + (x + 1)], self._items[row + x]
                self.emitRowsChanged(row + (x + 1), row + x)
            return True
        else:
            return False

    def removeRows(self, row, count, parentIndex=QModelIndex()):
        if 0 <= row and row + count <= len(self._items):
            self.beginRemoveRows(parentIndex, row, row + count - 1)
            del self._items[row:row + count]
            self.endRemoveRows()
            return True
        else:
            return False

    def data(self, index, role=Qt.DisplayRole):
        column = index.column()
        row = index.row()
        if 0 <= row < len(self._items):
            if role == Qt.EditRole:
                col = self._cols[column]
                record = self._items[row]
                return record.value(col.fieldName())

            if role == Qt.DisplayRole:
                col = self._cols[column]
                record = self._items[row]
                return col.toString(record.value(col.fieldName()), record)

            if role == Qt.StatusTipRole:
                col = self._cols[column]
                record = self._items[row]
                return col.toStatusTip(record.value(col.fieldName()), record)

            if role == Qt.CheckStateRole:
                col = self._cols[column]
                record = self._items[row]
                return col.toCheckState(record.value(col.fieldName()), record)

            if role == Qt.ForegroundRole:
                col = self._cols[column]
                record = self._items[row]
                return col.getForegroundColor(record.value(col.fieldName()), record)

            if role == Qt.BackgroundRole:
                col = self._cols[column]
                record = self._items[row]
                return col.getBackgroundColor(record.value(col.fieldName()), record)

            if role == Qt.TextAlignmentRole:
                col = self._cols[column]
                return col.alignment()

        return QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            column = index.column()
            row = index.row()
            if row == len(self._items):
                if value.isNull():
                    return False
                self._items.append(self.getEmptyRecord())
                count = len(self._items)
                rootIndex = QModelIndex()
                self.beginInsertRows(rootIndex, count, count)
                # atronah: Смысл этой котовасии, если insertRows виртуальная и ничего не делает?
                self.insertRows(count, 1, rootIndex)
                self.endInsertRows()
            record = self._items[row]
            col = self._cols[column]
            record.setValue(col.fieldName(), value)
            self.emitCellChanged(row, column)
            return True
        if role == Qt.CheckStateRole:
            column = index.column()
            row = index.row()
            state = value.toInt()[0]
            if row == len(self._items):
                if state == Qt.Unchecked:
                    return False
                self._items.append(self.getEmptyRecord())
                count = len(self._items)
                rootIndex = QModelIndex()
                self.beginInsertRows(rootIndex, count, count)
                self.insertRows(count, 1, rootIndex)
                self.endInsertRows()
            record = self._items[row]
            col = self._cols[column]
            record.setValue(col.fieldName(), QVariant(0 if state == Qt.Unchecked else 1))
            self.emitCellChanged(row, column)
            return True
        return False

    def setValue(self, row, fieldName, value):
        if 0 <= row < len(self._items):
            item = self._items[row]
            valueAsVariant = toVariant(value)
            if item.value(fieldName) != valueAsVariant:
                item.setValue(fieldName, valueAsVariant)
                self.emitValueChanged(row, fieldName)

    def value(self, row, fieldName):
        if 0 <= row < len(self._items):
            return self._items[row].value(fieldName)
        return None

    def sort(self, column, order=QtCore.Qt.AscendingOrder):
        col = self._cols[column]  # type: CInDocTableCol
        if not col.sortable():
            return

        self._items.sort(cmp=naturalStringCompare if col.useNaturalStringCompare() else None,
                         key=lambda (item): col.toSortString(item.value(col.fieldName()), item),
                         reverse=order == QtCore.Qt.DescendingOrder)
        self.emitRowsChanged(0, len(self._items) - 1)

    def emitCellChanged(self, row, column):
        index = self.index(row, column)
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)

    def emitRowChanged(self, row):
        self.emitRowsChanged(row, row)

    def emitRowsChanged(self, begRow, endRow):
        index1 = self.index(begRow, 0)
        index2 = self.index(endRow, self.columnCount())
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index1, index2)

    def emitColumnChanged(self, column):
        index1 = self.index(0, column)
        index2 = self.index(self.rowCount(), column)
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index1, index2)

    def emitDataChanged(self):
        index1 = self.index(0, 0)
        index2 = self.index(self.rowCount(), self.columnCount())
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index1, index2)

    def emitValueChanged(self, row, fieldName):
        column = self.getColIndex(fieldName)
        if column >= 0:
            self.emitCellChanged(row, column)

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return self._cols[section].title()
            if role == Qt.ToolTipRole:
                return self._cols[section].toolTip()
            if role == Qt.WhatsThisRole:
                return self._cols[section].whatsThis()

        return QVariant()

    def createEditor(self, column, parent):
        self.emit(QtCore.SIGNAL('editInProgress(bool)'), True)
        return self._cols[column].createEditor(parent)

    def setEditorData(self, column, editor, value, record):
        return self._cols[column].setEditorData(editor, value, record)

    def getEditorData(self, column, editor):
        return self._cols[column].getEditorData(editor)

    def setExtraData(self, field, data):
        pass

    def afterUpdateEditorGeometry(self, editor, index):
        pass


class CInDocTableSortFilterProxyModel(QtGui.QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(CInDocTableSortFilterProxyModel, self).__init__(parent)
        self._isEnabledSortingBySource = False
        self.mapColumnPattetn = {}
        self.mapColumnFixedString = {}
        self.begDateColumn = None
        self.endDateColumn = None
        self.operateDate = QDate()

    def setFiterDateIntervalKeyColumns(self, columnTuple):
        self.begDateColumn = columnTuple[0]
        self.endDateColumn = columnTuple[1]

    def addFilterStartsWithString(self, column, pattern):
        self.mapColumnPattetn[column] = forceString(pattern).lower()

    def addFilterFixedString(self, column, fixedString):
        self.mapColumnFixedString[column] = forceString(fixedString).lower()

    def clearFilterFixedString(self):
        self.mapColumnPattetn.clear()
        self.mapColumnFixedString.clear()

    def addFilterDateInInterval(self, date):
        self.operateDate = QDate.fromString(date, 'dd.MM.yyyy')

    def filterAcceptsRow(self, row, index):
        if not (self.mapColumnPattetn or self.operateDate):
            return True
        result = False
        for key, value in self.mapColumnPattetn.items():
            curIndex = self.sourceModel().index(row, key)
            data = forceString(curIndex.data())
            result = (data.lower().startswith(value) if value else True)
            if not result:
                return result
        for key, value in self.mapColumnFixedString.items():
            curIndex = self.sourceModel().index(row, key)
            data = forceString(curIndex.data())
            result = data.lower() == value
            if not result:
                return result
        if not self.operateDate:
            return result
        begDate = QDate.fromString(forceString(self.sourceModel().index(row, self.begDateColumn).data()), 'dd.MM.yyyy')
        endDate = QDate.fromString(forceString(self.sourceModel().index(row, self.endDateColumn).data()), 'dd.MM.yyyy')
        if begDate:
            result = result and begDate <= self.operateDate
        if endDate:
            result = result and endDate >= self.operateDate
        return result

    def setSortingBySourceModel(self, enabled):
        self._isEnabledSortingBySource = enabled

    def sort(self, logicalIdx, order=QtCore.Qt.AscendingOrder):
        if self._isEnabledSortingBySource:
            self.sourceModel().sort(logicalIdx, order)
            self.reset()
        else:
            super(CInDocTableSortFilterProxyModel, self).sort(logicalIdx, order)

    def __getattr__(self, attrName):
        # if not hasattr(self, attrName) and hasattr(self.sourceModel(), attrName):
        #     return getattr(self.sourceModel(), attrName)
        # else:

        try:
            return super(CInDocTableSortFilterProxyModel, self).__getattr__(attrName)
        except:
            return getattr(self.sourceModel(), attrName)


class CInDocTableModel(CRecordListModel):
    rowNumberFieldName = u'__rowNumber'

    # модель для взаимодействия со списком QSqlRecord
    # основное назначение: табличная часть документа
    def __init__(self, tableName, idFieldName, masterIdFieldName, parent, rowNumberTitle=None):
        CRecordListModel.__init__(self, parent)
        db = QtGui.qApp.db
        self._table = db.table(tableName)  # TODO: atronah: сделать поддержку как tableName, так и CTable
        self._idFieldName = idFieldName
        self._masterIdFieldName = masterIdFieldName
        self._rowNumberTitle = rowNumberTitle
        if self._table.hasField('idx'):
            self._idxFieldName = 'idx'
        else:
            self._idxFieldName = ''
        self._tableFields = None
        self._enableAppendLine = True
        self._extColsPresent = False
        self._isEditable = True
        self._filter = None

        if rowNumberTitle:
            self.addExtCol(CInDocTableCol(u'№ п/п', self.rowNumberFieldName, 10).setReadOnly(True), QVariant.Int)

    table = property(lambda self: self._table)
    idFieldName = property(lambda self: self._idFieldName)
    idxFieldName = property(lambda self: self._idxFieldName)
    masterIdFieldName = property(lambda self: self._masterIdFieldName)
    filter = property(lambda self: self._filter)

    def updateRetiredList(self):
        if hasattr(self, 'colPerson'):
            self.colPerson.setEndDate(self._parent.edtBegDate.date() if hasattr(self._parent, 'edtBegDate') else None)
        if hasattr(self, 'colAssistant'):
            self.colAssistant.setEndDate(self._parent.edtBegDate.date() if hasattr(self._parent, 'edtBegDate') else None)
        if hasattr(self, 'colSetPerson'):
            self.colSetPerson.setEndDate(self._parent.edtBegDate.date() if hasattr(self._parent, 'edtBegDate') else None)
        if hasattr(self, 'colExecPerson'):
            self.colExecPerson.setEndDate(self._parent.edtBegDate.date() if hasattr(self._parent, 'edtBegDate') else None)

    def diagnosisServiceId(self):
        u"""
        Метод необходим для автоматической подстановки услуги по заданному коду диагноза МКБ,
        согласно таблице соотвествий из справочника (Справочники -> Медицинские -> Коды МКБ Х).

        Если соотвествие найдено, то метод возвращает id соотвествующей услуги, иначе None.

        Используется в моделях CF***[Final]DiagnosticsModel форм F000, F025, F02512, F030, F030S
        :return: int or None
        """
        items = self.items()
        if items:
            code = forceString(items[0].value('MKB'))
            if code in self.mapMKBToServiceId:
                return self.mapMKBToServiceId[code]
            elif hasattr(self._parent, 'cmbPerson') and self._parent.cmbPerson.value() and forceString(items[0].value('MKB')):
                stmt_1 = u"""
                                SELECT
                                    mkb_ss.service_id
                                FROM
                                    Person p
                                    INNER JOIN MKBServiceSpeciality mkb_ss ON p.speciality_id = mkb_ss.speciality_id
                                    INNER JOIN MKB_Tree mkb_t ON mkb_t.id = mkb_ss.mkb_id
                                WHERE
                                    p.id = %s
                                    AND mkb_t.DiagID = '%s'
                                """ % (self._parent.cmbPerson.value(), forceString(items[0].value('MKB')))
                stmt_2 = u"""
                                SELECT
                                    mkb_ss.service_id
                                FROM
                                    MKBServiceSpeciality mkb_ss
                                    INNER JOIN MKB_Tree mkb_t ON mkb_t.id = mkb_ss.mkb_id
                                WHERE
                                    mkb_ss.speciality_id IS NULL
                                    AND mkb_t.DiagID = '%s'
                                """ % forceString(items[0].value('MKB'))

                rec = QtGui.qApp.db.getRecordEx(stmt=stmt_1)
                rec_2 = QtGui.qApp.db.getRecordEx(stmt=stmt_2)
                if rec:
                    serviceId = forceRef(rec.value('service_id'))
                elif rec_2:
                    serviceId = forceRef(rec_2.value('service_id'))
                else:
                    return None
            else:
                return None

            self.mapMKBToServiceId[code] = serviceId
            return serviceId
        return None

    def indexOf(self, fieldName):
        for colNumber, col in enumerate(self._cols):
            if col._fieldName == fieldName:
                return colNumber
        return None

    def setEditable(self, editable):
        self._isEditable = editable

    def isEditable(self):
        return self._isEditable

    def setFilter(self, filterCond):
        self._filter = filterCond

    def loadItems(self, masterId):
        db = QtGui.qApp.db
        cols = []
        for col in self._cols:
            if col.external():
                cols.append(u'NULL AS %s' % col.fieldName())
            else:
                cols.append('`' + col.fieldName() + '`')

        cols.append(self._idFieldName)
        cols.append(self._masterIdFieldName)
        if self._idxFieldName:
            cols.append(self._idxFieldName)
        for col in self._hiddenCols:
            cols.append(col)
        table = self._table
        filterCond = [table[self._masterIdFieldName].eq(masterId)]
        if self._filter:
            filterCond.append(self._filter)
        if table.hasField('deleted'):
            filterCond.append(table['deleted'].eq(0))
        if self._idxFieldName:
            order = [self._idxFieldName, self._idFieldName]
        else:
            order = [self._idFieldName]
        self._items = db.getRecordList(table, cols, filterCond, order, rowNumberFieldName=self.rowNumberFieldName if self._rowNumberTitle else None)
        self.reset()
        self.setDirty(False)

    def flags(self, index):
        flags = CRecordListModel.flags(self, index)
        if not self._isEditable:
            flags &= (~ Qt.ItemIsEditable)
        return flags

    def doAfterSaving(self, condition):
        db = QtGui.qApp.db
        table = self._table
        if self._filter:
            condition.append(self._filter)
        if table.hasField('deleted'):
            db.markRecordsDeleted(table, condition)
        else:
            db.deleteRecord(table, condition)

    def saveItems(self, masterId):
        if self._items is not None:
            db = QtGui.qApp.db
            table = self._table
            masterId = toVariant(masterId)
            masterIdFieldName = self._masterIdFieldName
            idFieldName = self._idFieldName
            idList = []
            for idx, record in enumerate(self._items):
                record.setValue(masterIdFieldName, masterId)
                if self._idxFieldName:
                    record.setValue(self._idxFieldName, toVariant(idx))
                if self._extColsPresent:
                    outRecord = self.removeExtCols(record)
                else:
                    outRecord = record
                itemId = db.insertOrUpdate(table, outRecord)
                record.setValue(idFieldName, toVariant(itemId))
                for col in self.cols():
                    # сохранение внешних данных столбцов, если такие имеются
                    col.saveExternalData(record)
                idList.append(itemId)

            cond = [table[masterIdFieldName].eq(masterId),
                    table[idFieldName].notInlist(idList)]

            self.doAfterSaving(cond)
            self.setDirty(False)

    def removeExtCols(self, srcRecord):
        record = self._table.newRecord()
        for i in xrange(record.count()):
            record.setValue(i, srcRecord.value(record.fieldName(i)))
        return record

    # FIXME: atronah: странно, что логика по добавление External Columns реализована в родительском классе,
    # а правильная обработка этих External Columns реализована только тут, а не в родительском классе
    def getEmptyRecord(self):
        record = super(CInDocTableModel, self).getEmptyRecord()
        newRecord = self._table.newRecord()
        for fieldIdx in xrange(newRecord.count()):
            field = newRecord.field(fieldIdx)
            if not record.contains(field.name()):
                record.append(field)

        if self._rowNumberTitle:
            record.setValue(self.rowNumberFieldName, toVariant(self.rowCount()))
        return record


class CActionPersonInDocTableColSearch(CRBInDocTableColSearch):
    def __init__(self, title, fieldName, width, tableName, **params):
        CRBInDocTableColSearch.__init__(self, title, fieldName, width, tableName, **params)
        self._parent = params.get('parent', None)
        self._isExecPerson = params.get('isExecPerson', False)
        self._endDate = params.get('endDate', None)
        self._specialityRequired = False
        self._orgStructureId = QtGui.qApp.currentOrgStructureId()
        # self.filter = self.compileFilter()

    def createEditor(self, parent):
        import Orgs.PersonComboBoxEx
        editor = Orgs.PersonComboBoxEx.CPersonComboBoxEx(parent)
        editor.setOrgStructureId(self._orgStructureId)
        return editor

    def setEditorData(self, editor, value, record):
        # editor.setTable(self.tableName, self.addNone, self.compileFilter(), order = self.order)
        # editor.setShowFields(self.showFields)
        editor.setValue(forceInt(value))

    def getEditorData(self, editor):
        return toVariant(editor.value())

    def setEndDate(self, endDate):
        self._endDate = endDate
        self.filter = self.compileFilter()

    def setSpecialityRequired(self, flag):
        self._specialityRequired = flag
        self.filter = self.compileFilter()

    def getAcceptableSpecialities(self):
        if not self._isExecPerson: return []
        if not hasattr(self._parent, 'tblActions') or not hasattr(self._parent, 'modelActionsSummary'): return []
        row = self._parent.tblActions.currentIndex().row()
        if not self._parent.modelActionsSummary.items() or row >= len(self._parent.modelActionsSummary.items()): return []
        record = self._parent.modelActionsSummary.items()[row]
        actionTypeId = forceRef(record.value('actionType_id'))
        if not actionTypeId:
            return []
        db = QtGui.qApp.db
        records = db.getRecordList('ActionType_Speciality', 'speciality_id', 'master_id=%s' % actionTypeId)
        specialities = []
        for record in records:
            specialities.append(forceRef(record.value('speciality_id')))
        return specialities

    def compileFilter(self):
        db = QtGui.qApp.db
        tblPerson = db.table('vrbPersonWithSpeciality')  # deleted = 0 уже заложено
        cond = []
        if self._parent:
            cond.append('org_id=\'%s\'' % self._parent.orgId)
        if self._endDate:
            cond.append(db.joinOr([tblPerson['retireDate'].isNull(),
                                   tblPerson['retireDate'].ge(self._endDate)]))
        acceptableSpecialities = self.getAcceptableSpecialities()
        if acceptableSpecialities:
            cond.append(tblPerson['speciality_id'].inlist(acceptableSpecialities))
        if self._specialityRequired:
            cond.append(tblPerson['speciality_id'].isNotNull())

        return db.joinAnd(cond)


class CLocItemDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, parent):
        QtGui.QStyledItemDelegate.__init__(self, parent)
        self.row = 0
        self.lastrow = 0
        self.column = 0
        self.editor = None

    def createEditor(self, parent, option, index):
        column = index.column()
        editor = index.model().createEditor(column, parent)
        self.connect(editor, QtCore.SIGNAL('commit()'), self.emitCommitData)
        self.connect(editor, QtCore.SIGNAL('editingFinished()'), self.commitAndCloseEditor)
        self.connect(editor, QtCore.SIGNAL('saveExtraData(QString, QString)'), self.saveExtraData)
        self.editor = editor
        self.row = index.row()
        self.rowcount = index.model().rowCount()
        self.column = column
        self._extraData = None
        self._extraField = None
        return editor

    def setEditorData(self, editor, index):
        if editor is not None:
            model = index.model()
            column = index.column()
            row = index.row()
            if row < len(model.items()):
                record = model.items()[row]
                value = model.data(index, Qt.EditRole)
            else:
                record = model.getEmptyRecord()
                value = record.value(index.model().cols()[column].fieldName())
            model.setEditorData(column, editor, value, record)

    def setModelData(self, editor, model, index):
        if editor is not None:
            column = index.column()
            editorData = index.model().getEditorData(column,
                                                     editor)  # вынесено сюда, т.к. до этого не успевает сработать вызов saveExtraData -> не заполняется значение freeInput в ClientRelations
            if self._extraField:
                model.setExtraData(self._extraField, self._extraData)
            model.setData(index, editorData)

    def emitCommitData(self):
        self.emit(QtCore.SIGNAL('commitData(QWidget *)'), self.sender())

    def commitAndCloseEditor(self):
        editor = self.sender()
        self.emit(QtCore.SIGNAL('commitData(QWidget *)'), editor)
        self.emit(QtCore.SIGNAL('closeEditor(QWidget *,QAbstractItemDelegate::EndEditHint)'), editor, QtGui.QAbstractItemDelegate.NoHint)

    def editorEvent(self, event, model, option, index):
        flags = int(model.flags(index))
        checkableFlags = int(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        notCheckableFlags = (checkableFlags & flags) != checkableFlags
        if notCheckableFlags:
            return False

        value = index.data(Qt.CheckStateRole)
        if not value.isValid():
            return False

        editableFlags = int(Qt.ItemIsEnabled | Qt.ItemIsEditable)
        if (editableFlags & flags) == editableFlags:
            return QtGui.QStyledItemDelegate.editorEvent(self, event, model, option, index)

        state = QVariant(Qt.Unchecked if forceInt(value) == Qt.Checked else Qt.Checked)

        eventType = event.type()
        if eventType in [QEvent.MouseButtonRelease, QEvent.MouseButtonDblClick]:
            return model.setData(index, state, Qt.CheckStateRole)

        if eventType == QEvent.KeyPress:
            if event.key() in [Qt.Key_Space, Qt.Key_Select]:
                return model.setData(index, state, Qt.CheckStateRole)
        return QtGui.QStyledItemDelegate.editorEvent(self, event, model, option, index)

    def saveExtraData(self, fieldName, data):
        if fieldName:
            self._extraField = fieldName
            self._extraData = data

    def eventFilter(self, object, event):
        def editorCanEatTab():
            if isinstance(self.editor, QtGui.QDateEdit):
                return self.editor.currentSection() != QtGui.QDateTimeEdit.YearSection
            return False

        def editorCanEatBacktab():
            if isinstance(self.editor, QtGui.QDateEdit):
                return self.editor.currentSection() != QtGui.QDateTimeEdit.DaySection
            return False

        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Tab:
                if editorCanEatTab():
                    self.editor.keyPressEvent(event)
                    return True
                if self.editor is not None:
                    self.parent().commitData(self.editor)
                self.parent().keyPressEvent(event)
                return True
            elif event.key() == Qt.Key_Backtab:
                if editorCanEatBacktab():
                    self.editor.keyPressEvent(event)
                    return True
                if self.editor is not None:
                    self.parent().commitData(self.editor)
                self.parent().keyPressEvent(event)
                return True
        return QtGui.QStyledItemDelegate.eventFilter(self, object, event)

    def updateEditorGeometry(self, editor, option, index):
        QtGui.QStyledItemDelegate.updateEditorGeometry(self, editor, option, index)
        index.model().afterUpdateEditorGeometry(editor, index)

    # Функции, дублирующиеся с делегатом для CTableView
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


class CInDocTableView(QtGui.QTableView, CPreferencesMixin):
    __pyqtSignals__ = ('editInProgress(bool)',
                       )
    MAX_COLS_SIZE = 350
    MIN_COLS_SIZE = 72

    def __init__(self, parent):
        QtGui.QTableView.__init__(self, parent)
        self._popupMenu = None

        self.isClientEditDialog = False
        # self.isConfirmSendingData = None
        # self.mailParsed = True

        self.isTblPolices = False
        self.isCorrectPolicies = True

        h = self.fontMetrics().height()
        self.verticalHeader().setDefaultSectionSize(3 * h / 2)
        self.verticalHeader().hide()

        self.setShowGrid(True)
        # self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.setItemDelegate(CLocItemDelegate(self))
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setStretchLastSection(True)
        self.setTabKeyNavigation(True)
        #        self.setEditTriggers(QtGui.QAbstractItemView.AllEditTriggers)
        self.setEditTriggers(
            QtGui.QAbstractItemView.AnyKeyPressed | QtGui.QAbstractItemView.EditKeyPressed | QtGui.QAbstractItemView.SelectedClicked | QtGui.QAbstractItemView.DoubleClicked)
        self.setFocusPolicy(Qt.StrongFocus)
        self.__actUpRow = None
        self.__actDownRow = None
        self.__actDeleteRows = None
        self.__actSelectAllRow = None
        self.__actSelectRowsByData = None
        self.__actDuplicateCurrentRow = None
        self.__actAddFromReportRow = None
        self.__actDuplicateSelectRows = None
        self.__actClearSelectionRow = None
        self.__actRecordProperties = None
        self.__sortColumn = None
        self.__sortAscending = False
        self.__delRowsChecker = None
        self.rbTable = None
        # self.connect( self.horizontalHeader(), QtCore.SIGNAL('sectionClicked(int)'), self.on_sortByColumn)
        self.horizontalHeader().sectionClicked[int].connect(self.enableSorting)
        self.isCloseDate = False

        self.setHorizontalScrollMode(self.ScrollPerPixel)
        self.setVerticalScrollMode(self.ScrollPerPixel)

        # self.setDragEnabled(True)
        # self.setAcceptDrops(True)
        # self.viewport().setAcceptDrops(True)
        # self.setDragDropOverwriteMode(False)
        # self.setDropIndicatorShown(True)
        #
        # self.setSelectionMode(QAbstractItemView.SingleSelection)
        # self.setSelectionBehavior(QAbstractItemView.SelectRows)
        # self.setDragDropMode(QAbstractItemView.InternalMove)

    def dropEvent(self, event):
        if event.source() == self and (
                event.dropAction() == Qt.MoveAction or self.dragDropMode() == QAbstractItemView.InternalMove):
            success, row, col, topIndex = self.dropOn(event)
            if success:
                selRows = self.getSelectedRowsFast()
                top = selRows[0]
                dropRow = row
                if dropRow == -1:
                    dropRow = self.rowCount()
                offset = dropRow - top

                for i, row in enumerate(selRows):
                    r = row + offset
                    if r > self.rowCount() or r < 0:
                        r = 0
                    self.insertRow(r)

                selRows = self.getSelectedRowsFast()
                top = selRows[0]
                offset = dropRow - top
                for i, row in enumerate(selRows):
                    r = row + offset
                    if r > self.rowCount() or r < 0:
                        r = 0

                    for j in range(self.columnCount()):
                        source = QTableWidgetItem(self.item(row, j))
                        self.setItem(r, j, source)

                event.accept()
        else:
            QtGui.QTableView.dropEvent(event)

    def getSelectedRowsFast(self):
        selRows = []
        for item in self.selectedItems():
            if item.row() not in selRows:
                selRows.append(item.row())
        return selRows

    def droppingOnItself(self, event, index):
        dropAction = event.dropAction()

        if self.dragDropMode() == QAbstractItemView.InternalMove:
            dropAction = Qt.MoveAction

        if event.source() == self and event.possibleActions() & Qt.MoveAction and dropAction == Qt.MoveAction:
            selectedIndexes = self.selectedIndexes()
            child = index
            while child.isValid() and child != self.rootIndex():
                if child in selectedIndexes:
                    return True
                child = child.parent()

        return False

    def dropOn(self, event):
        if event.isAccepted():
            return False, None, None, None

        index = QModelIndex()
        row = -1
        col = -1

        if self.viewport().rect().contains(event.pos()):
            index = self.indexAt(event.pos())
            if not index.isValid() or not self.visualRect(index).contains(event.pos()):
                index = self.rootIndex()

        if self.model().supportedDropActions() & event.dropAction():
            if index != self.rootIndex():
                dropIndicatorPosition = self.position(event.pos(), self.visualRect(index), index)

                if dropIndicatorPosition == QAbstractItemView.AboveItem:
                    row = index.row()
                    col = index.column()
                    # index = index.parent()
                elif dropIndicatorPosition == QAbstractItemView.BelowItem:
                    row = index.row() + 1
                    col = index.column()
                    # index = index.parent()
                else:
                    row = index.row()
                    col = index.column()

            if not self.droppingOnItself(event, index):
                return True, row, col, index

        return False, None, None, None

    def position(self, pos, rect, index):
        r = QAbstractItemView.OnViewport
        margin = 2
        if pos.y() - rect.top() < margin:
            r = QAbstractItemView.AboveItem
        elif rect.bottom() - pos.y() < margin:
            r = QAbstractItemView.BelowItem
        elif rect.contains(pos, True):
            r = QAbstractItemView.OnItem

        if r == QAbstractItemView.OnItem and not (self.model().flags(index) & Qt.ItemIsDropEnabled):
            r = QAbstractItemView.AboveItem if pos.y() < rect.center().y() else QAbstractItemView.BelowItem

        return r

    @QtCore.pyqtSlot(int)
    def enableSorting(self, logicalIdx):
        if self.isSortingEnabled():
            return

        model = self.model()
        if logicalIdx not in xrange(model.columnCount()):
            return

        if isinstance(model, CInDocTableModel):
            if not model.cols()[logicalIdx].sortable():
                return

        self.setSortingEnabled(True)

    def setSelectionModel(self, selectionModel):
        currSelectionModel = self.selectionModel()
        if currSelectionModel:
            self.disconnect(currSelectionModel, QtCore.SIGNAL('currentChanged(QModelIndex,QModelIndex))'), self.currentChanged)
        QtGui.QTableView.setSelectionModel(self, selectionModel)
        if selectionModel:
            self.connect(selectionModel, QtCore.SIGNAL('currentChanged(QModelIndex,QModelIndex))'), self.currentChanged)

    def createPopupMenu(self, actions=None):
        if not actions:
            actions = []
        self._popupMenu = QtGui.QMenu(self)
        self._popupMenu.setObjectName('popupMenu')
        self.connect(self._popupMenu, QtCore.SIGNAL('aboutToShow()'), self.on_popupMenu_aboutToShow)
        self.addPopupActions(actions)
        return self._popupMenu

    def addPopupActions(self, actionList, isAddSeparatorBefore=False):
        if self._popupMenu is None:
            self.createPopupMenu()

        if isAddSeparatorBefore:
            self.addPopupSeparator()

        for action in actionList:
            if isinstance(action, QtGui.QAction):
                self._popupMenu.addAction(action)
            elif action == '-':
                self._popupMenu.addSeparator()

    def addPopupSeparator(self):
        if self._popupMenu is None:
            self.createPopupMenu()
        self._popupMenu.addSeparator()

    def addMoveRow(self):
        #        if self.model().idxFieldName:
        if self._popupMenu is None:
            self.createPopupMenu()
        self.__actUpRow = QtGui.QAction(u'Поднять строку', self)
        self.__actUpRow.setObjectName('actUpRow')
        self._popupMenu.addAction(self.__actUpRow)
        self.connect(self.__actUpRow, QtCore.SIGNAL('triggered()'), self.on_upRow)
        self.__actDownRow = QtGui.QAction(u'Опустить строку', self)
        self.__actDownRow.setObjectName('actDownRow')
        self._popupMenu.addAction(self.__actDownRow)
        self.connect(self.__actDownRow, QtCore.SIGNAL('triggered()'), self.on_downRow)

    def addSpecialMoveRow(self):
        if self._popupMenu is None:
            self.createPopupMenu()
        self.__actSpecialUpRow = QtGui.QAction(u'Поднять строку на число позиций', self)
        self.__actSpecialUpRow.setObjectName('actSpecialUpRow')
        self._popupMenu.addAction(self.__actSpecialUpRow)
        self.connect(self.__actSpecialUpRow, QtCore.SIGNAL('triggered()'), self.on_specialUpRow)
        self.__actSpecialDownRow = QtGui.QAction(u'Опустить строку на число позиций', self)
        self.__actSpecialDownRow.setObjectName('actSpecialDownRow')
        self._popupMenu.addAction(self.__actSpecialDownRow)
        self.connect(self.__actSpecialDownRow, QtCore.SIGNAL('triggered()'), self.on_specialDownRow)

    def addPopupDelRow(self):
        if self._popupMenu is None:
            self.createPopupMenu()
        self.__actDeleteRows = QtGui.QAction(u'Удалить строку', self)
        self.__actDeleteRows.setObjectName('actDeleteRows')
        self._popupMenu.addAction(self.__actDeleteRows)
        self.connect(self.__actDeleteRows, QtCore.SIGNAL('triggered()'), self.on_deleteRows)

    def addPopupSelectAllRow(self):
        if self._popupMenu == None:
            self.createPopupMenu()
        self.__actSelectAllRow = QtGui.QAction(u'Выделить все строки', self)
        self.__actSelectAllRow.setObjectName('actSelectAllRow')
        self._popupMenu.addAction(self.__actSelectAllRow)
        self.connect(self.__actSelectAllRow, QtCore.SIGNAL('triggered()'), self.on_selectAllRow)

    def addPopupSelectRowsByData(self):
        if self._popupMenu == None:
            self.createPopupMenu()
        self.__actSelectRowsByData = QtGui.QAction(u'Выделить строки соответствующие текущему столбцу', self)
        self.__actSelectRowsByData.setObjectName('actSelectRowsByDate')
        self._popupMenu.addAction(self.__actSelectRowsByData)
        self.connect(self.__actSelectRowsByData, QtCore.SIGNAL('triggered()'), self.on_selectRowsByData)

    def addPopupClearSelectionRow(self):
        if self._popupMenu == None:
            self.createPopupMenu()
        self.__actClearSelectionRow = QtGui.QAction(u'Снять выделение', self)
        self.__actClearSelectionRow.setObjectName('actClearSelectionRow')
        self._popupMenu.addAction(self.__actClearSelectionRow)
        self.connect(self.__actClearSelectionRow, QtCore.SIGNAL('triggered()'), self.on_clearSelectionRow)

    def addPopupRecordProperies(self):
        if self._popupMenu == None:
            self.createPopupMenu()
        self.__actRecordProperties = QtGui.QAction(u'Свойства записи', self)
        self.__actRecordProperties.setObjectName('actRecordProperties')
        self._popupMenu.addAction(self.__actRecordProperties)
        self.connect(self.__actRecordProperties, QtCore.SIGNAL('triggered()'), self.showRecordProperties)

    def addPopupDuplicateCurrentRow(self):
        if self._popupMenu == None:
            self.createPopupMenu()
        self.__actDuplicateCurrentRow = QtGui.QAction(u'Дублировать строку', self)
        self.__actDuplicateCurrentRow.setObjectName('actDuplicateCurrentRow')
        self._popupMenu.addAction(self.__actDuplicateCurrentRow)
        self.connect(self.__actDuplicateCurrentRow, QtCore.SIGNAL('triggered()'), self.on_duplicateCurrentRow)

    def addPopupRowFromReport(self, rbTable, rbTableName=u''):
        self.rbTable = rbTable
        if self._popupMenu == None:
            self.createPopupMenu()
        self.__actAddFromReportRow = QtGui.QAction(u'Добавить строки из справочника%s' % ((u': ' + rbTableName) if rbTableName else u''), self)
        self.__actAddFromReportRow.setObjectName('actAddFromReportRow')
        self._popupMenu.addAction(self.__actAddFromReportRow)
        self.connect(self.__actAddFromReportRow, QtCore.SIGNAL('triggered()'), self.on_addFromReportRow)

    def addPopupDuplicateSelectRows(self):
        if self._popupMenu == None:
            self.createPopupMenu()
        self.__actDuplicateSelectRows = QtGui.QAction(u'Дублировать выделенные строки', self)
        self.__actDuplicateSelectRows.setObjectName('actDuplicateSelectRows')
        self._popupMenu.addAction(self.__actDuplicateSelectRows)
        self.connect(self.__actDuplicateSelectRows, QtCore.SIGNAL('triggered()'), self.on_duplicateSelectRows)

    def setPopupMenu(self, menu):
        self._popupMenu = menu

    def popupMenu(self):
        if self._popupMenu is None:
            self.createPopupMenu()
        return self._popupMenu

    def setDelRowsChecker(self, func):
        self.__delRowsChecker = func

    def keyPressEvent(self, event):
        key = event.key()
        text = unicode(event.text())
        if key == Qt.Key_Escape:
            event.ignore()
        elif key == Qt.Key_Return or key == Qt.Key_Enter:
            event.ignore()
        elif event.key() == Qt.Key_Tab:
            index = self.currentIndex()
            model = self.model()
            if index.row() == model.rowCount() - 1 and index.column() == model.columnCount() - 1:
                self.parent().focusNextChild()
                event.accept()
            else:
                QtGui.QTableView.keyPressEvent(self, event)
        elif event.key() == Qt.Key_Backtab:
            index = self.currentIndex()
            if index.row() == 0 and index.column() == 0:
                self.parent().focusPreviousChild()
                event.accept()
            else:
                QtGui.QTableView.keyPressEvent(self, event)
        else:
            QtGui.QTableView.keyPressEvent(self, event)

    def focusInEvent(self, event):
        reason = event.reason()
        model = self.model()
        if reason in [Qt.TabFocusReason, Qt.ShortcutFocusReason, Qt.OtherFocusReason]:
            if not self.hasFocus():
                self.setCurrentIndex(model.index(0, 0))
        elif reason == Qt.BacktabFocusReason:
            if not self.hasFocus():
                self.setCurrentIndex(model.index(model.rowCount() - 1, model.columnCount() - 1))
        QtGui.QTableView.focusInEvent(self, event)
        self.updateStatusTip(self.currentIndex())

    def focusOutEvent(self, event):
        self.updateStatusTip(None)
        QtGui.QTableView.focusOutEvent(self, event)

    def closeEditor(self, editor, hint):
        if hasattr(editor, 'deletePopup'):
            editor.deletePopup()
        self.emit(QtCore.SIGNAL('editInProgress(bool)'), False)
        QtGui.QTableView.closeEditor(self, editor, hint)

    def addNewRow(self):
        self.model().addRow()

    def removeCurrentRow(self):
        index = self.currentIndex()
        if index.isValid():
            row = index.row()
            self.model().removeRow(row)

    def contextMenuEvent(self, event):  # event: QContextMenuEvent
        if self._popupMenu and self.model().isEditable():
            self._popupMenu.exec_(event.globalPos())
            event.accept()
        else:
            event.ignore()

    def colKey(self, col):
        return unicode('width ' + forceString(col.title()))

    def getSelectedRows(self):
        rowCount = len(self.model().items())
        rowSet = set([index.row() for index in self.selectionModel().selectedIndexes() if index.row() < rowCount])
        result = list(rowSet)
        result.sort()
        return result

    def getSelectedItems(self):
        items = self.model().items()
        rows = self.getSelectedRows()
        return [items[row] for row in rows]

    def on_popupMenu_aboutToShow(self):
        row = self.currentIndex().row()
        rowCount = len(self.model().items())
        if self.__actUpRow:
            self.__actUpRow.setEnabled(0 < row < rowCount)
        if self.__actDownRow:
            self.__actDownRow.setEnabled(0 <= row < rowCount - 1)
        if self.__actDuplicateCurrentRow:
            self.__actDuplicateCurrentRow.setEnabled(0 <= row < rowCount)
        if self.__actAddFromReportRow:
            self.__actAddFromReportRow.setEnabled(rowCount <= 0)
        if self.__actDeleteRows:
            rows = self.getSelectedRows()
            canDeleteRow = bool(rows)
            if canDeleteRow and self.__delRowsChecker:
                canDeleteRow = self.__delRowsChecker(rows)
            if len(rows) == 1 and rows[0] == row:
                self.__actDeleteRows.setText(u'Удалить текущую строку')
            elif len(rows) == 1:
                self.__actDeleteRows.setText(u'Удалить выделенную строку')
            else:
                self.__actDeleteRows.setText(u'Удалить выделенные строки')
            self.__actDeleteRows.setEnabled(canDeleteRow)
            if self.__actDuplicateSelectRows:
                self.__actDuplicateSelectRows.setEnabled(canDeleteRow)
        if self.__actSelectAllRow:
            self.__actSelectAllRow.setEnabled(0 <= row < rowCount)
        if self.__actSelectRowsByData:
            column = self.currentIndex().column()
            items = self.model().items()
            value = items[row].value(column) if row < len(items) else None
            self.__actSelectRowsByData.setEnabled(forceBool(0 <= row < rowCount and (value and value.isValid())))
        if self.__actClearSelectionRow:
            self.__actClearSelectionRow.setEnabled(0 <= row < rowCount)
        if self.__actRecordProperties:
            self.__actRecordProperties.setEnabled(0 <= row < rowCount)

    def on_upRow(self):
        index = self.currentIndex()
        if index.isValid():
            row = index.row()
            if self.model().upRow(row):
                self.setCurrentIndex(self.model().index(row - 1, index.column()))
                self.resetSorting()

    def on_downRow(self):
        index = self.currentIndex()
        if index.isValid():
            row = index.row()
            if self.model().downRow(row):
                self.setCurrentIndex(self.model().index(row + 1, index.column()))
                self.resetSorting()

    def on_specialUpRow(self):
        index = self.currentIndex()
        if index.isValid():
            row = index.row()

            dlg = CMovingRowDialog()
            dlg.setTitle(u'Переместить строку вверх')
            dlg.setLabelName(u'вверх')

            dlg.edtValue.setMaximum(row)

            if dlg.exec_():
                if self.model().upRow(row, dlg.edtValue.value()):
                    self.setCurrentIndex(self.model().index(row - dlg.edtValue.value(), index.column()))
                    self.resetSorting()

    def on_specialDownRow(self):
        index = self.currentIndex()
        if index.isValid():
            row = index.row()

            dlg = CMovingRowDialog()
            dlg.setTitle(u'Переместить строку вниз')
            dlg.setLabelName(u'вниз')

            dlg.edtValue.setMaximum(len(self.model().items()) - row - 1)

            if dlg.exec_():
                if self.model().downRow(row, dlg.edtValue.value()):
                    self.setCurrentIndex(self.model().index(row + dlg.edtValue.value(), index.column()))
                    self.resetSorting()

    def on_deleteRows(self):
        rows = self.getSelectedRows()
        rows.sort(reverse=True)
        for row in rows:
            self.model().removeRow(row)

    #        self.removeCurrentRow()

    def on_selectAllRow(self):
        self.selectAll()

    def on_selectRowsByData(self):
        items = self.model().items()
        currentRow = self.currentIndex().row()
        if currentRow < len(items):
            currentColumn = self.currentIndex().column()
            selectIndexes = self.selectedIndexes()
            selectRowList = []
            for selectIndex in selectIndexes:
                selectRow = selectIndex.row()
                if selectRow not in selectRowList:
                    selectRowList.append(selectRow)
            currentRecord = items[currentRow]
            data = currentRecord.value(currentColumn)
            if data.isValid():
                for row, item in enumerate(items):
                    if (item.value(currentColumn) == data) and (row not in selectRowList):
                        self.selectRow(row)

    def on_duplicateCurrentRow(self):
        currentRow = self.currentIndex().row()
        items = self.model().items()
        if currentRow < len(items):
            newRecord = self.model().getEmptyRecord()
            copyFields(newRecord, items[currentRow])
            newRecord.setValue(self.model()._idFieldName, toVariant(None))
            self.model().insertRecord(currentRow + 1, newRecord)

    def on_addFromReportRow(self):
        if self.rbTable:
            db = QtGui.qApp.db
            table = db.table(self.rbTable)
            rbTableIdList = db.getDistinctIdList(table, 'id')
            items = self.model().items()
            for row, rbTableId in enumerate(rbTableIdList):
                if row <= len(items):
                    newRecord = self.model().getEmptyRecord()
                    newRecord.setValue('rbTable_id', toVariant(rbTableId))
                    self.model().insertRecord(row, newRecord)

    def on_duplicateSelectRows(self):
        currentRow = self.currentIndex().row()
        items = self.model().items()
        if currentRow < len(items):
            selectIndexes = self.selectedIndexes()
            selectRowList = []
            for selectIndex in selectIndexes:
                selectRow = selectIndex.row()
                if selectRow not in selectRowList:
                    selectRowList.append(selectRow)
            selectRowList.sort()
            for row in selectRowList:
                newRecord = self.model().getEmptyRecord()
                copyFields(newRecord, items[row])
                items.append(newRecord)
            self.model().reset()

    def on_clearSelectionRow(self):
        self.clearSelection()

    def showRecordProperties(self):
        currentRow = self.currentIndex().row()
        items = self.model().items()
        if currentRow < len(items):
            itemId = forceRef(items[currentRow].value('id'))
        else:
            return
        table = self.model().table
        CRecordProperties(self, table, itemId).exec_()

    def resetSorting(self):
        self.horizontalHeader().setSortIndicatorShown(False)
        self.__sortColumn = None

    def columnsResize(self):
        if not QtGui.qApp.isNotLimitedTableColsSize():
            if hasattr(self.model(), "_cols"):
                self.resizeColumnsToContents()
                self.resizeRowsToContents()
                for x in range(len(self.model()._cols)):
                    if self.columnWidth(x) > self.MAX_COLS_SIZE:
                        self.setColumnWidth(x, self.MAX_COLS_SIZE)
                    elif self.columnWidth(x) < self.MIN_COLS_SIZE:
                        self.setColumnWidth(x, self.MIN_COLS_SIZE)

    def loadPreferences(self, preferences):
        model = self.model()
        if isinstance(model, (CDrugRecipeModel, CInDocTableSortFilterProxyModel, CInDocTableModel, CRecordListModel)):
            cols = model.cols()
            i = 0
            for col in cols:
                width = forceInt(getPref(preferences, self.colKey(col), self.columnWidth(i)))
                if width:
                    self.setColumnWidth(i, width)
                i += 1
        # self.columnsResize()
        self.horizontalHeader().setStretchLastSection(True)

    def savePreferences(self):
        preferences = {}
        model = self.model()
        if isinstance(model, (CDrugRecipeModel, CInDocTableSortFilterProxyModel, CInDocTableModel, CRecordListModel)):
            cols = model.cols()
            i = 0
            for col in cols:
                width = self.columnWidth(i)
                setPref(preferences, self.colKey(col), QVariant(width))
                i += 1
        return preferences

    @property
    def object_name(self):
        return '%s.%s' % (self.parent().objectName(), self.objectName())

    def showEvent(self, evt):
        self.loadPreferences(getPref(QtGui.qApp.preferences.tablePrefs, self.object_name.lower(), {}))

    def hideEvent(self, evt):
        setPref(QtGui.qApp.preferences.tablePrefs, self.object_name.lower(), self.savePreferences())

    def updateStatusTip(self, index):
        tip = forceString(index.data(Qt.StatusTipRole)) if index else ''
        event = QtGui.QStatusTipEvent(tip)
        QtGui.qApp.sendEvent(self, event)

    def checkPolicyCorrect(self):
        if not QtGui.qApp.userHasRight(urAccessCrossingDates):
            for x in self.model().items():
                if forceDate(x.value('begDate')) != QDate():
                    for y in self.model().items():
                        if forceDate(y.value('begDate')) != QDate() and \
                                forceRef(y.value('policyType_id')) == forceRef(x.value('policyType_id')):
                            if forceDate(y.value('endDate')) != QDate():
                                if forceDate(y.value('begDate')) <= forceDate(x.value('begDate')) and \
                                        forceDate(y.value('endDate')) > forceDate(x.value('endDate')):
                                    return False
                            else:
                                if forceDate(y.value('begDate')) <= forceDate(x.value('begDate')):
                                    return False
        return True

    def checkPolicy(self):
        if not self.checkPolicyCorrect():
            self.isCorrectPolicies = False
            QtGui.QMessageBox.warning(self,
                                      u'ОШИБКА',
                                      u'Обнаружено пересечение дат полисов одного типа.',
                                      QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok,
                                      QtGui.QMessageBox.Ok)
            return False
        else:
            self.isCorrectPolicies = True
            return True

    def currentChanged(self, current, previous):
        # if self.isTblPolices:
        #    self.checkPolicy()
        QtGui.QTableView.currentChanged(self, current, previous)
        self.updateStatusTip(current)
        # self.resizeColumnsToContents()
        # self.resizeRowsToContents()
        # self.columnsResize()

    def addContentToTextCursor(self, cursor):
        model = self.model()
        cols = model.cols()
        colWidths = [self.columnWidth(i) for i in xrange(len(cols))]
        colWidths.insert(0, 10)
        totalWidth = sum(colWidths)
        tableColumns = []
        alignRight = CReportBase.AlignRight
        alignLeft = CReportBase.AlignLeft
        for iCol, colWidth in enumerate(colWidths):
            widthInPercents = str(max(1, colWidth * 90 / totalWidth)) + '%'
            if iCol == 0:
                tableColumns.append((widthInPercents, [u'№'], alignRight))
            else:
                col = cols[iCol - 1]
                tableColumns.append((widthInPercents, [forceString(col.title())], alignLeft))

        table = createTable(cursor, tableColumns)
        for iModelRow in xrange(model.rowCount()):
            QtGui.qApp.processEvents(QEventLoop.ExcludeUserInputEvents)
            iTableRow = table.addRow()
            table.setText(iTableRow, 0, iModelRow + 1)
            iTableCol = 1
            for iModelCol in xrange(len(cols)):
                index = model.createIndex(iModelRow, iModelCol)
                text = forceString(model.data(index))
                table.setText(iTableRow, iTableCol, text)
                iTableCol += 1


class CLocEnableInDocTableCol(CBoolInDocTableCol):
    def __init__(self, selector):
        CBoolInDocTableCol.__init__(self, u'Включить', 'checked', 10)
        self.selector = selector

    def toCheckState(self, val, record):
        return CBoolInDocTableCol.toCheckState(self, val, record)


from Exchange.R23.recipes.SynchronizeDLOMIAC import CDrugRecipeModel
