# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
import copy
import itertools
import re
import traceback
from PyQt4 import QtCore, QtGui, QtSql

from PyQt4.QtCore import *
from PyQt4.QtGui import QMessageBox

from library.Utils import compareCallStack, forceRef, forceString, toVariant
from library.debug import printQueryTime
from library.exception import CException, CDatabaseException

queryLog = {}


def decorateString(s):
    u = unicode(s)
    return '\'' + u.replace('\\', '\\\\').replace('\'', '\\\'') + '\''


class CField(object):
    # field - либо QtSql.QSqlField для поля таблицы базы либо просто строка для суррагатного поля (в таком случае необходимо указать еще и fieldType)
    # fieldType - для случая создания виртуального/суррогатного поля
    def __init__(self, database, tableName, field, fieldType=None):
        self.database = database  # type: CDatabase
        self.tableName = tableName
        if isinstance(field, QtSql.QSqlField):
            self.fieldName = database.escapeFieldName(field.name())
            self.field = field
            self.isSurrogate = False
        elif isinstance(field, (basestring, QString)):
            self.fieldName = forceString(field)
            self.field = QtSql.QSqlField(field, fieldType if isinstance(fieldType, QVariant.Type) else QVariant.String)
            self.isSurrogate = True

    def __str__(self):
        return self.name()

    def name(self):
        prefix = (self.tableName + '.') if self.tableName else ''
        return prefix + self.fieldName

    def fieldType(self):
        return self.field.type()

    def alias(self, name=''):
        return ' '.join([self.name(),
                         self.database.aliasSymbol,
                         self.database.escapeFieldName(name) if name else self.fieldName])

    def asc(self):
        return u'{0} ASC'.format(self.name())

    def desc(self):
        return u'{0} DESC'.format(self.name())

    def toTable(self, tableName):
        return CField(self.database, tableName, self.field)

    ## Формирует строку для операции над текущим полем вида (<текущее_поле> <оператор> <выражение>)
    #    с учетом переданного оператора и выражения, а так же шаблона-модификатора, в который подставлюятся текущее поле и выражение, если необходимо
    # @param sign: оператор (заданый строкой). Подставляется в результат всегда в неизменном виде.
    # @param expr: выражение, над которым производится операция с текущим полем. Может быть None (в таком случае будет опущенно).
    # @param modifierTemplate: шаблон-модификатор, в который (если он задан, т.е. не None) помещаются имя текущего поля и выражение expr.
    #                        Является строкой-шаблоном (см. python string formatting) для одного значения.
    #                        Например, может иметь значение 'DATE(%s)', что приведет к формированию выражения вида 'DATE(<текущее_поле>) <оператор> DATE(<выражение>)'
    def signEx(self, sign, expr=None, modifierTemplate=None):
        # составляющая выражения может быть опущена, если передано значение None
        exprPart = [expr if modifierTemplate is None else (modifierTemplate % expr)] if expr is not None else []
        return ' '.join([self.name() if modifierTemplate is None else (modifierTemplate % self.name()),
                         sign]
                        + exprPart)

    def formatValue(self, value):
        if isinstance(value, CField):
            return value.name()
        else:
            return self.database.formatValueEx(self.fieldType(), value)

    def sign(self, sign, val, modifierTemplate=None):
        return self.signEx(sign, self.formatValue(val), modifierTemplate)

    def eq(self, val):
        return self.isNull() if val is None else self.sign('=', val)

    def eqEx(self, val):
        return self.isNull() if val is None else self.signEx('=', val)

    def __eq__(self, val):
        return CSqlExpression(self.database, self.eq(self.database.forceField(val)))

    def lt(self, val):
        return self.sign('<', val)

    def __lt__(self, val):
        return CSqlExpression(self.database, self.lt(self.database.forceField(val)))

    def le(self, val):
        return self.sign('<=', val)

    def __le__(self, val):
        return CSqlExpression(self.database, self.le(self.database.forceField(val)))

    def gt(self, val):
        return self.sign('>', val)

    def __gt__(self, val):
        return CSqlExpression(self.database, self.gt(self.database.forceField(val)))

    def ge(self, val):
        return self.sign('>=', val)

    def __ge__(self, val):
        return CSqlExpression(self.database, self.ge(self.database.forceField(val)))

    def ne(self, val):
        return self.isNotNull() if val is None else self.sign('!=', val)

    def __ne__(self, val):
        return CSqlExpression(self.database, self.ne(self.database.forceField(val)))

    def isNull(self):
        return self.signEx('IS NULL', None)

    def isNotNull(self):
        return self.signEx('IS NOT NULL', None)

    def setNull(self):
        return self.signEx('=', 'NULL')

    def isZeroDate(self):
        return self.eq(self.database.valueField('0000-00-00'))

    def isNullDate(self):
        return self.database.joinOr([self.isNull(),
                                     self.isZeroDate()])

    def __not__(self):
        return CSqlExpression(self.database, u'NOT {0}'.format(self))

    def __and__(self, other):
        return CSqlExpression(self.database, u'{0} AND {1}'.format(self, other))

    def __or__(self, other):
        return CSqlExpression(self.database, u'{0} OR {1}'.format(self, other))

    def __add__(self, other):
        return CSqlExpression(self.database, u'{0} + {1}'.format(self, other))

    def __sub__(self, other):
        return CSqlExpression(self.database, u'{0} - {1}'.format(self, other))

    def __mul__(self, other):
        return CSqlExpression(self.database, u'{0} * {1}'.format(self, other))

    def __div__(self, other):
        return CSqlExpression(self.database, u'{0} / {1}'.format(self, other))

    def decoratedlist(self, itemList):
        if not itemList:
            return '()'
        else:
            decoratedList = []
            for value in itemList:
                decoratedList.append(self.database.formatValueEx(self.fieldType(), value))
            return unicode('(' + (','.join(decoratedList)) + ')')

    def inlist(self, itemList, *args):
        if not isinstance(itemList, (list, tuple, set)):
            itemList = args + (itemList,)
        return '0' if not itemList else self.signEx('IN', self.decoratedlist(itemList))

    def notInlist(self, itemList):
        if not itemList:
            return '1'  # true
        else:
            return self.signEx('NOT IN', self.decoratedlist(itemList))

    def inInnerStmt(self, stmt):
        if not stmt:
            return '0'
        else:
            return self.signEx('IN', u'(%s)' % stmt)

    def notInInnerStmt(self, stmt):
        if not stmt:
            return '0'
        else:
            return self.signEx('NOT IN', u'(%s)' % stmt)

    def eqStmt(self, stmt):
        if not stmt:
            return '0'
        else:
            return self.signEx('=', u'(%s)' % stmt)

    def like(self, val):
        return self.sign('LIKE', undotLikeMask(val))

    def notlike(self, val):
        return self.sign('NOT LIKE ', undotLikeMask(val))

    def likeBinary(self, val):
        return self.sign('LIKE BINARY', undotLikeMask(val))

    def regexp(self, val):
        return self.sign('REGEXP', val)

    def between(self, low, high):
        return u'(%s BETWEEN %s AND %s)' % (self.name(), self.formatValue(low), self.formatValue(high))

    ## Формирует строку для сравнения текущего поля с датой-временем (или только датой при onlyDate = True), переданной в параметрах
    def compareDatetime(self, otherDatetime, compareOperator, onlyDate=True):
        if otherDatetime is None:
            return self.isNull()

        return self.signEx(compareOperator, self.formatValue(otherDatetime),
                           u'DATE(%s)' if onlyDate else u'TIMESTAMP(%s)')

    def dateEq(self, val):
        return self.compareDatetime(val, u'=')

    def dateLe(self, val):
        return self.compareDatetime(val, u'<=')

    def dateLt(self, val):
        return self.compareDatetime(val, u'<')

    def dateGe(self, val):
        return self.compareDatetime(val, u'>=')

    def dateGt(self, val):
        return self.compareDatetime(val, u'>')

    def datetimeEq(self, val):
        return self.compareDatetime(val, u'=', onlyDate=False)

    def datetimeLe(self, val):
        return self.compareDatetime(val, u'<=', onlyDate=False)

    def datetimeLt(self, val):
        return self.compareDatetime(val, u'<', onlyDate=False)

    def datetimeGe(self, val):
        return self.compareDatetime(val, u'>=', onlyDate=False)

    def datetimeGt(self, val):
        return self.compareDatetime(val, u'>', onlyDate=False)

    def datetimeBetween(self, low, high):
        return 'TIMESTAMP(%s) BETWEEN TIMESTAMP(%s) AND TIMESTAMP(%s)' % (
        self.name(), self.formatValue(low), self.formatValue(high))

    def dateBetween(self, low, high):
        return u'(DATE(%s) BETWEEN %s AND %s)' % (self.name(), self.formatValue(low), self.formatValue(high))

    def monthGe(self, val):
        if val is None:
            return self.isNull()
        else:
            return 'MONTH(' + self.name() + ')>=MONTH(' + unicode(self.formatValue(val) + ')')

    def yearGe(self, val):
        if val is None:
            return self.isNull()
        else:
            return 'YEAR(' + self.name() + ')>=YEAR(' + unicode(self.formatValue(val) + ')')

    def yearEq(self, val):
        if val is None:
            return self.isNull()
        else:
            return 'YEAR(' + self.name() + ')=YEAR(' + unicode(self.formatValue(val) + ')')


class CSurrogateField(CField):
    def __init__(self, name, fieldType):
        self.database = None
        self.tableName = ''
        self.fieldName = name
        self.field = QtSql.QSqlField(name, fieldType)


class CSqlExpression(CField):
    def __init__(self, db, name, fieldType=QVariant.String):
        super(CField, self).__init__()
        self.database = db
        self.tableName = ''
        self.fieldName = name
        self._fieldType = fieldType

    def convertUtf8(self):
        return CSqlExpression(self.database,
                              u'CONVERT({0}, CHAR CHARACTER SET utf8)'.format(self.name()))

    def __str__(self):
        return self.fieldName

    def name(self):
        return self.fieldName

    def fieldType(self):
        return self._fieldType

    def alias(self, name=''):
        return ' '.join([self.name(),
                         self.database.aliasSymbol,
                         self.database.escapeFieldName(name) if name else self.fieldName])


class CTable(object):
    def __init__(self, tableName, database, alias=''):
        self.fields = []
        self.fieldsDict = {}
        self.database = database
        self.tableName = unicode(tableName)
        self.aliasName = alias
        self.isQueryTable = True if self.tableName.strip().lower().startswith('select') else False
        # atronah: Если имя таблицы начинается с 'SELECT ', то предположить, что это таблица-подзапрос, а она должна иметь псевдоним
        if self.isQueryTable and not alias:
            self.aliasName = 'someSubQueryTable'
            # atronah: На момент написания глубокомысленного кода (обработки условия) ниже
            # опытным путем было установленно, что QSqlDatabase.record(tableStatement) пытается выполнить запрос
            # <tableStatement>LIMIT 0,1
            # если <tableStatement> - это запрос на выборку, а не имя таблицы, как ожидает функция согласно документации.
            # И, следовательно, возникает проблема отсутствия пробела перед добавляемым "LIMIT"
            if not self.tableName.endswith(' '):
                self.tableName += u' '
        self._idField = None
        self._idFieldName = None
        record = database.record(self.tableName)
        # TODO: atronah: - случай, когда таблица задана джойнами и есть поля с одинаковым именем (ибо они без префикса будут)
        for i in xrange(record.count()):
            qtfield = record.field(i)
            field = CField(self.database, self.tableName, qtfield)
            self.fields.append(field)
            fieldName = str(qtfield.name())
            if not self.fieldsDict.has_key(fieldName):
                self.fieldsDict[fieldName] = field

    def name(self, alias=''):
        alias = alias or self.aliasName
        if alias:
            return ' '.join([self.tableName if not self.isQueryTable else '(%s)' % self.tableName,
                             self.database.aliasSymbol,
                             unicode(alias)])
        else:
            return self.tableName

    def alias(self, name):
        # atronah: создаем копию объекта (словари/списки копируются как ссылки, т.е. остаются общими, иначе надо использовать deepcopy())
        newTable = copy.copy(self)
        newTable.aliasName = unicode(name)
        return newTable

    def setIdFieldName(self, name):
        self._idField = self.__getitem__(name)
        self._idFieldName = name

    def idField(self):
        if not self._idField:
            self.setIdFieldName('id')
        ##            raise CDatabaseException(CDatabase.errNoIdField % (self.tableName))
        return self._idField

    def idFieldName(self):
        if not self._idField:
            if self.hasField('id'):
                self.setIdFieldName('id')
            else:
                self.setIdFieldName(self.fields[0].fieldName.replace('`', ''))
        ##            raise CDatabaseException(CDatabase.errNoIdField % (self.tableName))
        return self._idFieldName

    def __getitem__(self, key):
        key = str(key)
        result = self.fieldsDict.get(key, None)
        if result:
            return result if not self.aliasName else result.toTable(self.aliasName)
        elif key == '*':
            return CSqlExpression(self.database, '{0}.*'.format(self.tableName))
        else:
            raise CDatabaseException(CDatabase.errFieldNotFound % (self.tableName, key))

    def hasField(self, fieldName):
        return self.fieldsDict.has_key(fieldName)

    def newRecord(self, fields=None, otherRecord=None):
        record = QtSql.QSqlRecord()
        for field in self.fields:
            if fields and field.field.name() not in fields:
                continue
            record.append(QtSql.QSqlField(field.field))
            if otherRecord and otherRecord.contains(field.field.name()) and field != self._idField:
                record.setValue(field.field.name(), otherRecord.value(field.field.name()))
        return record

    def beforeInsert(self, record):
        return

    def beforeUpdate(self, record):
        return

    def beforeDelete(self, record):
        return

    def join(self, table, onCond):
        return self.database.join(self, table, onCond)

    def leftJoin(self, table, onCond):
        return self.database.leftJoin(self, table, onCond)

    def innerJoin(self, table, onCond):
        return self.database.innerJoin(self, table, onCond)


class CDocumentTable(CTable):
    # fields in DocumentTables:
    dtfCreateDatetime = 'createDatetime'
    dtfCreateUserId = 'createPerson_id'
    dtfModifyDatetime = 'modifyDatetime'
    dtfModifyUserId = 'modifyPerson_id'
    dtfDeleted = 'deleted'

    def __init__(self, tableName, database):
        CTable.__init__(self, tableName, database)

    def beforeInsert(self, record):
        now = toVariant(QDateTime.currentDateTime().addSecs(QtGui.qApp.getDatetimeDiff()))
        userId = toVariant(QtGui.qApp.userId)
        #        userId = toVariant(None)
        if record.indexOf(CDocumentTable.dtfCreateDatetime) < 0:
            record.append(QtSql.QSqlField(CDocumentTable.dtfCreateDatetime, QVariant.DateTime))
        if record.indexOf(CDocumentTable.dtfCreateUserId) < 0:
            record.append(QtSql.QSqlField(CDocumentTable.dtfCreateUserId, QVariant.Int))
        if record.indexOf(CDocumentTable.dtfModifyDatetime) < 0:
            record.append(QtSql.QSqlField(CDocumentTable.dtfModifyDatetime, QVariant.DateTime))
        if record.indexOf(CDocumentTable.dtfModifyUserId) < 0:
            record.append(QtSql.QSqlField(CDocumentTable.dtfModifyUserId, QVariant.Int))

        record.setValue(CDocumentTable.dtfCreateDatetime, now)
        record.setValue(CDocumentTable.dtfCreateUserId, userId)
        record.setValue(CDocumentTable.dtfModifyDatetime, now)
        record.setValue(CDocumentTable.dtfModifyUserId, userId)
        return

    def beforeUpdate(self, record):
        now = toVariant(QDateTime.currentDateTime().addSecs(QtGui.qApp.getDatetimeDiff()))
        userId = toVariant(QtGui.qApp.userId)

        if record.isNull(CDocumentTable.dtfCreateDatetime):
            pos = record.indexOf(CDocumentTable.dtfCreateDatetime)
            record.remove(pos)
        if record.isNull(CDocumentTable.dtfCreateUserId):
            pos = record.indexOf(CDocumentTable.dtfCreateUserId)
            record.remove(pos)

        if record.indexOf(CDocumentTable.dtfModifyDatetime) < 0:
            record.append(QtSql.QSqlField(CDocumentTable.dtfModifyDatetime, QVariant.DateTime))
        if record.indexOf(CDocumentTable.dtfModifyUserId) < 0:
            record.append(QtSql.QSqlField(CDocumentTable.dtfModifyUserId, QVariant.Int))

        record.setValue(CDocumentTable.dtfModifyDatetime, now)
        record.setValue(CDocumentTable.dtfModifyUserId, userId)
        return


class CJoin(object):
    def __init__(self, firstTable, secondTable, onCond, stmt='JOIN'):
        self.firstTable = firstTable
        self.secondTable = secondTable
        self.onCond = onCond
        self.stmt = stmt
        self.database = firstTable.database
        assert firstTable.database == secondTable.database

    def name(self):
        return u'%s %s %s ON %s ' % (self.firstTable.name(), self.stmt, self.secondTable.name(), self.onCond)

    def join(self, table, onCond):
        return self.database.join(self, table, onCond)

    def leftJoin(self, table, onCond):
        return self.database.leftJoin(self, table, onCond)

    def innerJoin(self, table, onCond):
        return self.database.innerJoin(self, table, onCond)

    def getMainTable(self):
        if isinstance(self.firstTable, CJoin):
            return self.firstTable.getMainTable()
        else:
            return self.firstTable

    def getAllTables(self):
        if isinstance(self.firstTable, CJoin):
            return self.firstTable.getAllTables() + [self.secondTable]
        else:
            return [self.secondTable]

    def isTableJoin(self, table):
        return table in self.getAllTables()

    def idField(self):
        return self.firstTable.idField()

    def beforeUpdate(self, record):
        return


class CSubQueryTable(object):
    u"""
    Подзапрос, подключаемый как таблица в основном запросе
    """

    def __init__(self, db, stmt, alias='T'):
        self.stmt = stmt
        self.aliasName = alias
        self.database = db

    def name(self):
        return u'(%s) AS %s' % (self.stmt, self.aliasName)

    def alias(self, aliasName):
        return CSubQueryTable(self.database, self.stmt, aliasName)

    def __getitem__(self, fieldName):
        return CSqlExpression(self.database, ((self.aliasName + '.') if self.aliasName else '') + self.database.escapeFieldName(fieldName))

    def join(self, table, onCond):
        return self.database.join(self, table, onCond)

    def leftJoin(self, table, onCond):
        return self.database.leftJoin(self, table, onCond)

    def innerJoin(self, table, onCond):
        return self.database.innerJoin(self, table, onCond)


class CUnionTable(object):
    """
        Простейшая реализация для использования вложенных таблиц, состоящих из двух подзапросов,
        объединенных с помощью union. На момент написания требуется только для совместимости с CDatabase.join
    """

    def __init__(self, db, firstStmt, secondStmt, alias=''):
        def getColsCount(stmt):
            match = re.search('(<=SELECT ).*(?= FROM)', stmt)
            if match:
                return len(match.group(0).split(','))
            return 0

        self.firstStmt = firstStmt
        self.secondStmt = secondStmt
        self.aliasName = alias
        self.database = db
        assert getColsCount(firstStmt) == getColsCount(secondStmt)

    def __getitem__(self, fieldName):
        return CSqlExpression(self.database, ((self.aliasName + '.') if self.aliasName else '') + self.database.escapeFieldName(fieldName))

    def name(self):
        return u'((%s) UNION (%s)) %s' % (self.firstStmt, self.secondStmt, self.aliasName)

    def join(self, table, onCond):
        return self.database.join(self, table, onCond)

    def leftJoin(self, table, onCond):
        return self.database.leftJoin(self, table, onCond)

    def innerJoin(self, table, onCond):
        return self.database.innerJoin(self, table, onCond)


################################################################


DocumentTables = []


def registerDocumentTable(tableName):
    DocumentTables.append(tableName)


class CDatabase(QObject):
    aliasSymbol = 'AS'

    errUndefinedDriver = u'Драйвер базы данных "%s" не зарегистрирован'
    errCannotConnectToDatabase = u'Невозможно подключиться к базе данных "%s"'
    errCannotOpenDatabase = u'Невозможно открыть базу данных "%s"'
    errDatabaseIsNotOpen = u'База данных не открыта'

    errCommitError = u'Ошибка закрытия тразнакции'
    errRollbackError = u'Ошибка отмены тразнакции'
    errTableNotFound = u'Таблица "%s" не найдена'
    errFieldNotFound = u'В таблице %s не найдено поле "%s"'
    errQueryError = u'Ошибка выполнения запроса\n%s'
    errNoIdField = u'В таблице %s не определен первичный ключ'
    errConnectionLost = u'Потеряна связь с сервером.'
    errRestoreConnectionFailed = u'Не удалось восстановить подключение к базе данных.\nНеобходимо перезапустить приложение.'

    errTransactionError = u'Ошибка открытия тразнакции'
    errNestedCommitTransactionError = u'Ошибка подтверждения вложенной транзакции'
    errNestedRollbackTransactionError = u'Ошибка отмены вложенной транзакции'
    errNestedTransactionCall = u'Попытка открытия вложенной транзакции'
    errUnexpectedTransactionCompletion = u'Неожиданное завершение транзакции'
    errInheritanceTransaction = u'Ошибка нессответствия наследования транзакций и вызвавших их функций'
    errNoRootTransaction = u'Нарушение требования корневой транзакции (уже открыто %s транзакций)'
    errPreviousTransactionCallStack = u'>>>>>>Стек вызовов предыдущей транзакции:\n%s<<<<<<'

    returnedDeadlockErrorText = u'<To be specified for a particular database.>'

    # добавлено для formatQVariant
    convMethod = {
        QVariant.Int      : lambda val: unicode(val.toInt()[0]),
        QVariant.UInt     : lambda val: unicode(val.toUInt()[0]),
        QVariant.LongLong : lambda val: unicode(val.toLongLong()[0]),
        QVariant.ULongLong: lambda val: unicode(val.toULongLong()[0]),
        QVariant.Double   : lambda val: unicode(val.toDouble()[0]),
        QVariant.Bool     : lambda val: u'1' if val.toBool() else u'0',
        QVariant.Char     : lambda val: decorateString(val.toString()),
        QVariant.String   : lambda val: decorateString(val.toString()),
        QVariant.Date     : lambda val: decorateString(val.toDate().toString(Qt.ISODate)),
        QVariant.Time     : lambda val: decorateString(val.toTime().toString(Qt.ISODate)),
        QVariant.DateTime : lambda val: decorateString(val.toDateTime().toString(Qt.ISODate)),
        QVariant.ByteArray: lambda val: 'x\'' + str(val.toByteArray().toHex()) + '\'',
        QVariant.Color    : lambda val: unicode(QtGui.QColor(val).name()),
    }

    connected = pyqtSignal()
    disconnected = pyqtSignal()

    def __init__(self, afterConnectFunc=None):
        QObject.__init__(self)
        self.deadLockRepeat = 3
        self.db = None
        self.tables = {}
        # restoreConnectState:  0 - соединение не было утеряно, 1 - соединение утеряно, пытаться переподключиться
        #                       2 - соединение утеряно, переподключение не требуется.
        self.restoreConnectState = 0

        self._transactionCallStackByLevel = []
        self._openTransactionsCount = 0

        self._func = None
        self._proc = None

    def getConnectionId(self):
        return None

    def makeField(self, fromString):
        u""" Raw SQL -> CField-like object
        :rtype: CSqlExpression
        """
        return CSqlExpression(self, fromString)

    def valueField(self, value):
        u""" Py-value (QVariant-convertible) -> CField-like object """
        return self.makeField(self.formatArg(value))

    def forceField(self, value):
        u""" CField instance, raw SQL or Py-value -> CField instance
        :rtype: CField
        """
        if isinstance(value, CField): return value
        elif isinstance(value, (str, unicode)): return self.makeField(value)
        return self.valueField(value)

    def subQueryTable(self, stmt, alias):
        u""" SELECT stmt -> CTable-like object """
        return CSubQueryTable(self, stmt, alias)

    def escapeIdentifier(self, name, identifierType):
        return unicode(self.driver().escapeIdentifier(name, identifierType))

    def escapeFieldName(self, name):
        return unicode(self.driver().escapeIdentifier(name, QtSql.QSqlDriver.FieldName))

    def escapeTableName(self, name):
        return unicode(self.driver().escapeIdentifier(name, QtSql.QSqlDriver.TableName))

    escapeSchemaName = escapeTableName

    @staticmethod
    def dummyRecord():
        return QtSql.QSqlRecord()

# Добавлено из-за обнаруженной ошибки в qt4 v.4.5.3:
# - значения полей типа DOUBLE считываются не как QVariant.Double а как QVariant.String
#   поведение в windows не исследовано, а в linux строка записывается с десятичной запятой.
#   при этом документированный способ исправить положение
#   query.setNumericalPrecisionPolicy(QSql.LowPrecisionDouble)
#   не срабатывает из-за того, что driver.hasFeature(QSqlDriver.LowPrecisionNumbers)
#   возвращает false
# - при записи значения в запрос формируется значение с запятой, что неприемлемо для MySql сервера
# поэтому принято решение написать свой вариант formatValue

    @classmethod
    def formatQVariant(cls, fieldType, val):
        if val.isNull():
            return 'NULL'
        return cls.convMethod[fieldType](val)

    @classmethod
    def formatValue(cls, field):
        return cls.formatQVariant(field.type(), field.value())

    @classmethod
    def formatValueEx(cls, fieldType, value):
        if isinstance(value, QVariant):
            return cls.formatQVariant(fieldType, value)
        else:
            return cls.formatQVariant(fieldType, toVariant(value))

    @classmethod
    def formatArg(cls, value):
        if isinstance(value, CField):
            return value.name()
        else:
            qValue = toVariant(value)
            return cls.formatValueEx(qValue.type(), qValue)

    def createConnection(self, driverName, connectionName, serverName, serverPort, databaseName, userName, password):
        if connectionName:
            if not QtSql.QSqlDatabase.contains(connectionName):
                db = QtSql.QSqlDatabase.addDatabase(driverName, connectionName)
            else:
                db = QtSql.QSqlDatabase.database(connectionName)
        else:
            db = QtSql.QSqlDatabase.addDatabase(driverName)
        if not db.isValid():
            raise CDatabaseException(CDatabase.errCannotConnectToDatabase % driverName, db.lastError())
        db.setHostName(serverName)
        if serverPort:
            db.setPort(serverPort)
        db.setDatabaseName(databaseName)
        db.setUserName(userName)
        db.setPassword(password)
        self.db = db

    def isConnectionLostError(self, sqlError):
        driverText = forceString(sqlError.driverText()).lower()
        if 'lost connection' in driverText:
            return True
        if 'server has gone away' in driverText:
            return True
        return False

    def connectUp(self):
        if not self.db.open():
            raise CDatabaseException(CDatabase.errCannotOpenDatabase % self.db.databaseName(), self.db.lastError())
        self.restoreConnectState = 0
        self._transactionCallStackByLevel = []
        self._openTransactionsCount = 0
        self.connected.emit()

    def reconnect(self):
        if not (self.db and self.db.isValid):
            return False
        if self.db.isOpen():
            self.db.close()
        if not self.db.open():
            self.connectDown()
            return False
        self.connected.emit()
        return True

    def connectDown(self):
        self.db.close()
        self._transactionCallStackByLevel = []
        self._openTransactionsCount = 0
        self.disconnected.emit()

    def close(self):
        if self.db:
            connectionName = self.db.connectionName()
            self.connectDown()
            QtSql.QSqlDatabase.removeDatabase(connectionName)
            self.driver = None
            self.db = None
        self.tables = {}

    def restoreConnection(self, quiet=False):
        from s11mainConsole import CS11MainConsoleApp
        if isinstance(QtGui.qApp, CS11MainConsoleApp):
            self.restoreConnectState = 2
            return False
        self.restoreConnectState = 1
        isReconnect = quiet or QMessageBox.critical(QtGui.qApp.activeWindow(),
                                                    u'Внимание',
                                                    CDatabase.errConnectionLost + u'\nПопробовать восстановить подключение?',
                                                    QMessageBox.Yes | QMessageBox.No,
                                                    QMessageBox.Yes) == QMessageBox.Yes
        if isReconnect:
            if QtGui.qApp.isRequiredLoginAndPass():
                QtGui.qApp.mainWindow.on_actLogin_triggered()
                if not QtGui.qApp.isAuth:
                    self.restoreConnectState = 2
                    return False

            if self.reconnect():
                self.restoreConnectState = 0
                return True
            else:
                QMessageBox.critical(QtGui.qApp.activeWindow(),
                                     u'Критическая ошибка',
                                     self.errRestoreConnectionFailed)
        self.restoreConnectState = 2
        return False

    def getTestConnectionStmt(self):
        return u'select \'test connection query\';'

    def checkdb(self):
        if not self.db or not self.db.isValid() or not self.db.isOpen():
            raise CDatabaseException(CDatabase.errDatabaseIsNotOpen)

    def isValid(self):
        return self.db is not None and self.db.isValid() and self.db.isOpen()

    def checkConnect(self, quietRestoreConnection=False):
        self.checkdb()
        sqlError = None

        testQuery = QtSql.QSqlQuery(self.db)
        stmt = self.getTestConnectionStmt()
        if testQuery.exec_(stmt):
            return
        else:
            sqlError = testQuery.lastError()

        if self.isConnectionLostError(sqlError):
            if self.restoreConnection(quietRestoreConnection):
                return
            else:
                self.connectDown()
                # TODO: skkachaev: Зачем?
                # raise CDatabaseException(CDatabase.errConnectionLost)

        raise self.onError(stmt, sqlError)

    def driver(self):
        return self.db.driver()

    def forceTable(self, table, idFieldName='id'):
        if isinstance(table, (CTable, CJoin, CUnionTable, CSubQueryTable)):
            return table
        elif isinstance(table, basestring):
            return self.table(table, idFieldName=idFieldName)
        else:
            raise AssertionError, u'Недопустимый тип'

    def mainTable(self, tableExpr, idFieldName='id'):
        if isinstance(tableExpr, (CTable, CJoin)):
            return tableExpr
        elif isinstance(tableExpr, basestring):
            name = tableExpr.split(None, 1)[0] if ' ' in tableExpr else tableExpr
            return self.table(name, idFieldName)
        else:
            raise AssertionError, u'Недопустимый тип'

    def getTableName(self, table):
        # atronah: проверка на строковость необходима, чтобы избежать рекурсию:
        # forceTable -> CTable.__init__() -> CTable.record() -> selectStmt() -> getTableName()
        # да и нет смысла создавать класс таблицы, для того чтобы получить ее имя из строки
        if isinstance(table, basestring):
            if table.strip().lower().startswith('select '):
                return ' '.join([u'(%s)' % table,
                                 self.aliasSymbol,
                                 u'someQueryTable'])
            return table
        return self.forceTable(table).name()

    def formatDate(self, val):
        return '\'' + str(val.toString(Qt.ISODate)) + '\''

    def formatTime(self, val):
        return '\'' + str(val.toString(Qt.ISODate)) + '\''

    def coalesce(self, *args):
        return CSqlExpression(self, u'COALESCE({0})'.format(u', '.join(map(self.formatArg, args))))

    def ifnull(self, exp1, exp2):
        return CSqlExpression(self, u'IFNULL({0}, {1})'.format(self.forceField(exp1), self.forceField(exp2)))

    @classmethod
    def joinAnd(cls, itemList):
        return (('((' if len(itemList) > 1 else '(') +
                u') AND ('.join(u'%s' % item for item in itemList) +
                ('))' if len(itemList) > 1 else ')')) if itemList else ''

    @classmethod
    def joinOr(cls, itemList):
        return (('((' if len(itemList) > 1 else '(') +
                u') OR ('.join(u'%s' % item for item in itemList) +
                ('))' if len(itemList) > 1 else ')')) if itemList else ''

    def not_(self, expr):
        return u'NOT ({0})'.format(expr)

    def if_(self, cond, thenPart, elsePart):
        return CSqlExpression(self, u'IF({0}, {1}, {2})'.format(cond,
                                                                self.forceField(thenPart),
                                                                self.forceField(elsePart)), QVariant.Bool)

    def case(self, field, caseDict, elseValue=None):
        parts = [
            u'WHEN {0} THEN {1}'.format(self.forceField(cond), self.forceField(value))
            for cond, value in caseDict.iteritems()
        ]
        if elseValue:
            parts.append(u'ELSE {0}'.format(self.forceField(elseValue)))
        return CSqlExpression(self, u'CASE {0} {1} END'.format(self.forceField(field), u' '.join(parts)))

    def concat(self, *args):
        return CSqlExpression(self, u'CONCAT({0})'.format(u', '.join(map(self.formatArg, args))))

    def concat_ws(self, sep, *args):
        return CSqlExpression(self, u'CONCAT_WS({0}, {1})'.format(self.formatArg(sep), u', '.join(map(self.formatArg, args))))

    def group_concat(self, item, distinct=False):
        return CSqlExpression(self, u'GROUP_CONCAT({0}{1})'.format(u'DISTINCT ' if distinct else u'', item))

    def count(self, item, distinct=False):
        return CSqlExpression(self, u'COUNT({0}{1})'.format(u'DISTINCT ' if distinct else u'', item if item else '*'), QVariant.Int)

    def countIf(self, cond, item, distinct=False):
        return self.count(self.if_(cond, item, 'NULL'), distinct)

    def datediff(self, dateTo, dateFrom):
        return CSqlExpression(self, u'DATEDIFF({0}, {1})'.format(dateTo, dateFrom), QVariant.Int)

    def addDate(self, date, count, type='DAY'):
        return CSqlExpression(self, u'ADDDATE({0}, INTERVAL {1} {2})'.format(date, count, type), QVariant.Date)

    def subDate(self, date, count, type='DAY'):
        return CSqlExpression(self, u'SUBDATE({0}, INTERVAL {1} {2})'.format(date, count, type), QVariant.Date)

    def date(self, date):
        return CSqlExpression(self, u'DATE({0})'.format(self.formatDate(date)))

    def dateYear(self, date):
        return CSqlExpression(self, u'YEAR({0})'.format(date), QVariant.Int)

    def dateQuarter(self, date):
        return CSqlExpression(self, u'QUARTER({0})'.format(date), QVariant.Int)

    def dateMonth(self, date):
        return CSqlExpression(self, u'MONTH({0})'.format(date), QVariant.Int)

    def dateDay(self, date):
        return CSqlExpression(self, u'DAY({0})'.format(date), QVariant.Int)

    def isZeroDate(self, date):
        return self.forceField(date).eq(self.valueField('0000-00-00'))

    def isNullDate(self, date):
        return self.joinOr([self.forceField(date).isNull(),
                            self.isZeroDate(date)])

    def sum(self, item):
        return CSqlExpression(self, u'SUM({0})'.format(item), item.fieldType() if isinstance(item, CField) else toVariant(item).type())

    def sumIf(self, cond, item):
        return self.sum(self.if_(cond, item, 0))

    def max(self, item):
        return CSqlExpression(self, u'MAX({0})'.format(item), QVariant.Int)

    def min(self, item):
        return CSqlExpression(self, u'MIN({0})'.format(item), QVariant.Int)

    def least(self, *args):
        return CSqlExpression(self, u'LEAST({0})'.format(u', '.join(map(self.formatArg, args))))

    def greatest(self, *args):
        return CSqlExpression(self, u'GREATEST({0})'.format(u', '.join(map(self.formatArg, args))))

    def left(self, str, len):
        return CSqlExpression(self, u'LEFT({0}, {1})'.format(str, len), QVariant.String)

    def right(self, str, len):
        return CSqlExpression(self, u'RIGHT({0}, {1})'.format(str, len), QVariant.String)

    def curdate(self):
        return CSqlExpression(self, u'CURDATE()', QVariant.Date)

    def now(self):
        return CSqlExpression(self, u'NOW()', QVariant.DateTime)

    def joinOp(self, op, *args):
        return CSqlExpression(self, u'({0})'.format(op.join(map(self.formatArg, args))), QVariant.Int)

    def bitAnd(self, *args):
        return self.joinOp(u'&', *args)

    def bitOr(self, *args):
        return self.joinOp(u'|', *args)

    def bitXor(self, *args):
        return self.joinOp(u'^', *args)

    @classmethod
    def prepareFieldList(cls, fields):
        if isinstance(fields, (list, tuple)):
            return ', '.join([field.name() if isinstance(field, CField) else field for field in fields])
        return fields.name() if isinstance(fields, CField) else fields

    @staticmethod
    def CONCAT_WS(fields, alias='', separator=' '):
        result = 'CONCAT_WS('
        result += ('\'' + separator + '\'')
        result += ', '
        if isinstance(fields, (list, tuple)):
            for field in fields:
                result += field.name() if isinstance(field, CField) else field
                result += ', '
        else:
            result += fields.name() if isinstance(fields, CField) else fields
            result += ', '
        result = result[:len(result) - 2]
        result += ')'
        if alias: result += (' AS ' + '`' + alias + '`')

        return result

    @classmethod
    def dateTimeIntersection(cls, fieldBegDateTime, fieldEndDateTime, begDateTime, endDateTime):
        if fieldBegDateTime is not None and fieldEndDateTime is not None and begDateTime is not None and endDateTime is not None:
            return cls.joinAnd([
                cls.joinOr([fieldBegDateTime.datetimeGe(begDateTime), fieldEndDateTime.datetimeGe(begDateTime),
                            fieldEndDateTime.isNull()]),
                # FIXME:skkachaev: fieldBegDateTime.isNull() у нас такого быть не может, но логически правильно. Возможно, в целях оптимизации, можно и вырезать
                cls.joinOr([fieldBegDateTime.datetimeLe(endDateTime), fieldEndDateTime.datetimeLe(endDateTime),
                            fieldBegDateTime.isNull()])
            ])
        else:
            return ''

    @classmethod
    def prepareWhere(cls, cond):
        if isinstance(cond, (list, tuple)):
            cond = cls.joinAnd(cond)
        return u' WHERE %s' % cond if cond else u''

    @classmethod
    def prepareOrder(cls, orderFields):
        if isinstance(orderFields, (list, tuple)):
            orderFields = ', '.join(
                [orderField.name() if isinstance(orderField, CField) else orderField for orderField in orderFields])
        if orderFields:
            return ' ORDER BY ' + (orderFields.name() if isinstance(orderFields, CField) else orderFields)
        else:
            return ''

    @classmethod
    def prepareGroup(cls, groupFields):
        if isinstance(groupFields, (list, tuple)):
            groupFields = ', '.join(
                [groupField.name() if isinstance(groupField, CField) else groupField for groupField in groupFields])
        if groupFields:
            return ' GROUP BY ' + (groupFields.name() if isinstance(groupFields, CField) else groupFields)
        else:
            return ''

    @classmethod
    def prepareHaving(cls, havingFields):
        if isinstance(havingFields, (list, tuple)):
            havingFields = cls.joinAnd(
                [havingField.name() if isinstance(havingField, CField) else havingField for havingField in
                 havingFields])
        if havingFields:
            return ' HAVING ' + (havingFields.name() if isinstance(havingFields, CField) else havingFields)
        else:
            return ''

    @classmethod
    def prepareLimit(cls, limit):
        assert False
        return ''

    def selectStmt(self, table, fields='*', where='', group='', order='', limit=None, isDistinct=False,
                   rowNumberFieldName=None, having=''):
        tableName = self.getTableName(table)

        beginWord = 'SELECT'
        if isDistinct:
            beginWord += ' DISTINCT'
        if rowNumberFieldName and fields != '*':
            fields.insert(0, '@__rowNumber := @__rowNumber + 1 AS %s' % rowNumberFieldName)
            tableName += ', (select @__rowNumber := 0) as __rowNumberInit'
        return ' '.join([
            beginWord, self.prepareFieldList(fields),
            'FROM', tableName,
            self.prepareWhere(where),
            self.prepareGroup(group),
            self.prepareHaving(having),
            self.prepareOrder(order),
            self.prepareLimit(limit)])

    def selectMax(self, table, col='id', where=''):
        return self.selectStmt(table, self.max(col), where)

    def selectMin(self, table, col='id', where=''):
        return self.selectStmt(table, self.min(col), where)

    def selectExpr(self, fields):
        u"""
        :type fields: CField or list of CField
        :rtype: QtSql.QSqlRecord
        """
        stmt = ' '.join(['SELECT', self.prepareFieldList(fields)])
        query = self.query(stmt)
        if query.first():
            record = query.record()
            return record
        return None

    def existsStmt(self, table, where, limit=None):
        field = '*'

        if isinstance(table, CJoin):
            mainTable = table.getMainTable()
            if mainTable.hasField('id'):
                field = mainTable['id'].name()

        return 'EXISTS (%s)' % self.selectStmt(table, field, where, limit=limit)

    def notExistsStmt(self, table, where):
        return 'NOT %s' % self.existsStmt(table, where)

    def _decreaseOpenTransactionCount(self):
        if self._openTransactionsCount > 0 and self._transactionCallStackByLevel:
            self._openTransactionsCount -= 1
            self._transactionCallStackByLevel.pop()
        else:
            raise CException(self.errUnexpectedTransactionCompletion)

    def nestedTransaction(self):
        formatedPrevTransactionStack = '\n'.join(
            traceback.format_list(self._transactionCallStackByLevel[self._openTransactionsCount - 1]))
        # self.decreaseTransactionLevel()
        raise CException('\n'.join([self.errNestedTransactionCall,
                                    self.errPreviousTransactionCallStack % formatedPrevTransactionStack]))

    def checkCallStackInheritance(self, currentCallStack):
        prevCallStack = self._transactionCallStackByLevel[self._openTransactionsCount - 1] \
            if (self._openTransactionsCount - 1) in xrange(len(self._transactionCallStackByLevel)) \
            else []
        compareCallStackResult = compareCallStack(prevCallStack, currentCallStack, 'traceback.extract_stack()')
        if prevCallStack and compareCallStackResult[1] != 1:
            formatedPrevTransactionStack = '\n'.join(traceback.format_list(prevCallStack))
            raise CException('\n'.join([self.errInheritanceTransaction,
                                        self.errPreviousTransactionCallStack % formatedPrevTransactionStack]))

    def transaction(self, checkIsInit=False):
        """
            Открывает транзакцию.
            Если ранее уже была открыта транзакция, то открывает вложенную транзакцию.
        :param checkIsInit: Включить проверку того, что открываемая транзакция должна быть первой\основной.
        """
        self.checkdb()

        currentCallStack = traceback.extract_stack()
        self.checkCallStackInheritance(currentCallStack)

        if self._openTransactionsCount == 0:
            if not self.db.transaction():
                raise CDatabaseException(CDatabase.errTransactionError, self.db.lastError())
        elif checkIsInit:
            raise CException(CDatabase.errNoRootTransaction % self._openTransactionsCount)
        else:
            self.nestedTransaction()

        self._openTransactionsCount += 1
        self._transactionCallStackByLevel.append(currentCallStack)

    def nestedCommit(self):
        pass

    def nestedRollback(self):
        pass

    def commit(self):
        self.checkdb()

        currentCallStack = traceback.extract_stack()
        self.checkCallStackInheritance(currentCallStack)

        if self._openTransactionsCount == 1:
            if not self.db.commit():
                raise CDatabaseException(CDatabase.errCommitError, self.db.lastError())
        else:
            self.nestedCommit()

        self._decreaseOpenTransactionCount()

    def rollback(self):
        self.checkdb()

        currentCallStack = traceback.extract_stack()
        self.checkCallStackInheritance(currentCallStack)

        if (self._openTransactionsCount - 1) == 0:
            if not self.db.rollback():
                raise CDatabaseException(CDatabase.errRollbackError, self.db.lastError())
        else:
            self.nestedRollback()

        self._decreaseOpenTransactionCount()

    def table(self, tableName, idFieldName='id'):
        if self.tables.has_key(tableName):
            return self.tables[tableName]
        else:
            if tableName in DocumentTables:
                table = CDocumentTable(tableName, self)
            else:
                table = CTable(tableName, self)
                if u'id' in [v.fieldName for v in table.fields]:
                    table.setIdFieldName(idFieldName)
            self.tables[tableName] = table
            return table

    def join(self, firstTable, secondTable, onCond, stmt='JOIN'):
        if isinstance(onCond, (list, tuple)):
            onCond = self.joinAnd(onCond)
        return CJoin(self.forceTable(firstTable), self.forceTable(secondTable), onCond, stmt)

    def leftJoin(self, firstTable, secondTable, onCond):
        return self.join(firstTable, secondTable, onCond, 'LEFT JOIN')

    def innerJoin(self, firstTable, secondTable, onCond):
        return self.join(firstTable, secondTable, onCond, 'INNER JOIN')

    def record(self, tableName):
        self.checkdb()
        if tableName.strip().lower().startswith('select'):
            res = self.query(tableName + self.prepareLimit(1)).record()
        else:
            parts = tableName.split('.', 1)
            if len(parts) <= 1:
                res = self.db.record(tableName)
                if not res:  # atronah: проверка соединения и повторная попытка в случае потери подключения
                    self.checkConnect()
                    res = self.db.record(tableName)
            else:
                currentDatabaseName = self.db.databaseName()
                databaseName = parts[0]
                # atronah: проверка подключения производится внутри query
                self.query('USE %s' % self.escapeSchemaName(databaseName))
                res = self.db.record(parts[1])
                self.query('USE %s' % self.escapeSchemaName(currentDatabaseName))

        if res.isEmpty():
            raise CDatabaseException(CDatabase.errTableNotFound % tableName)
        return res

    def recordFromDict(self, tableName, dct):
        table = self.forceTable(tableName)
        rec = table.newRecord(fields=dct.keys())
        for fieldName, value in dct.iteritems():
            rec.setValue(fieldName, toVariant(value))
        return rec

    def insertFromDict(self, tableName, dct):
        return self.insertRecord(tableName, self.recordFromDict(tableName, dct))

    def insertMultipleFromDict(self, tableName, lst):
        for dct in lst:
            self.insertRecord(tableName, self.recordFromDict(tableName, dct))

    @printQueryTime(callStack=False, printQueryFirst=True)
    def query(self, stmt, quietReconnect=False):
        # TODO: Обнаружено интересное поведение при отказе от восстановления разорванного соединения:
        # Все query, ожидающие восстановления узнают, что соединение закрыто и checkdb захламляет error.log.
        self.checkdb()
        result = QtSql.QSqlQuery(self.db)
        result.setForwardOnly(True)
        result.setNumericalPrecisionPolicy(QtSql.QSql.LowPrecisionDouble)
        repeatCounter = 0
        needRepeat = True
        while needRepeat:
            needRepeat = False
            if not result.exec_(stmt):
                lastError = result.lastError()
                if lastError.databaseText().contains(self.returnedDeadlockErrorText):
                    needRepeat = repeatCounter <= self.deadLockRepeat
                elif self.isConnectionLostError(lastError):
                    if self.restoreConnection(quietReconnect or self.restoreConnectState == 1):
                        needRepeat = True
                    else:
                        self.connectDown()
                else:
                    needRepeat = False
                    self.onError(stmt, lastError)
            repeatCounter += 1
        return result

    def onError(self, stmt, sqlError):
        raise CDatabaseException(stmt + u'\n' + CDatabase.errQueryError % stmt, sqlError)

    @staticmethod
    def checkDatabaseError(lastError, stmt=None):
        if lastError.isValid() and lastError.type() != QtSql.QSqlError.NoError:
            message = u'Неизвестная ошибка базы данных'
            if lastError.type() == QtSql.QSqlError.ConnectionError:
                message = u'Ошибка подключения к базе данных'
            elif lastError.type() == QtSql.QSqlError.StatementError:
                message = u'Ошибка SQL-запроса'
            elif lastError.type() == QtSql.QSqlError.TransactionError:
                message = u'Ошибка SQL-запроса'
            if stmt:
                message += u'\n(%s)\n' % stmt
            raise CDatabaseException(message, lastError)

    def getRecordEx(self, table=None, cols=None, where='', order='', stmt=None):
        if stmt is None: stmt = self.selectStmt(table, cols, where, order=order, limit=1)
        query = self.query(stmt)
        if query.first():
            record = query.record()
            #            del query
            return record
        else:
            return None

    def getRecord(self, table, cols, itemId):
        idCol = self.mainTable(table).idField()
        return self.getRecordEx(table, cols, idCol.eq(itemId))

    def updateRecord(self, table, record):
        table = self.forceTable(table)
        table.beforeUpdate(record)
        fieldsCount = record.count()
        idFieldName = table.idFieldName()
        values = []
        cond = ''
        itemId = None
        for i in range(fieldsCount):

            # My insertion for 'rbImageMap' table
            if table.name() == 'rbImageMap':
                pair = self.escapeFieldName(record.fieldName(i)) + '=' + self.formatValue(record.field(i))
                if record.fieldName(i) == idFieldName:
                    cond = pair
                    itemId = record.value(i).toInt()[0]
                elif record.fieldName(i) == 'image':
                    pass
                else:
                    values.append(pair)
            else:
                pair = self.escapeFieldName(record.fieldName(i)) + '=' + self.formatValue(record.field(i))
                if record.fieldName(i) == idFieldName:
                    cond = pair
                    itemId = record.value(i).toInt()[0]
                else:
                    values.append(pair)
        stmt = 'UPDATE ' + table.name() + ' SET ' + (', '.join(values)) + ' WHERE ' + cond
        self.query(stmt)
        return itemId

    def insertRecord(self, table, record):
        table = self.forceTable(table)
        table.beforeInsert(record)
        fieldsCount = record.count()
        fields = []
        values = []
        for i in xrange(fieldsCount):
            if not record.value(i).isNull():
                fields.append(self.escapeFieldName(record.fieldName(i)))
                values.append(self.formatValue(record.field(i)))
        stmt = ('INSERT INTO ' + table.name() +
                '(' + (', '.join(fields)) + ') ' +
                'VALUES (' + (', '.join(values)) + ')')
        itemId = self.query(stmt).lastInsertId().toInt()[0]
        idFieldName = table.idFieldName()
        record.setValue(idFieldName, QVariant(itemId))
        return itemId

    def insertMultipleRecords(self, table, records):
        if len(records) == 0: return
        table = self.forceTable(table)
        fields = []
        values = []
        for i in xrange(len(records)):
            tfields = []
            tvalues = []
            for j in xrange(records[i].count()):
                tfields.append(self.escapeFieldName(records[i].fieldName(j)))
                tvalues.append(self.formatValue(records[i].field(j)))
            fields.append(tfields)
            values.append(tvalues)
        stmt = (u'INSERT INTO ' + table.name() + (u'(' + u', '.join(fields[0])) + u') VALUES')
        for value in values:
            stmt += (u'(' + u', '.join(value) + u'),')
        stmt = stmt[:len(stmt) - 1]
        self.query(stmt)

    def insertMultipleRecordsByChunks(self, table, records, chunkSize=None):
        if len(records) == 0: return
        if chunkSize is None: chunkSize = len(records)
        table = self.forceTable(table)
        firstRecord = records[0]
        fields = [self.escapeFieldName(firstRecord.fieldName(i)) for i in xrange(firstRecord.count())]
        stmtInsert = u'INSERT INTO ' + table.name() + (u'(' + u', '.join(fields)) + u') VALUES '
        recordsIterator = iter(records)
        for _ in xrange(len(records) / chunkSize + 1):
            values = []
            for record in itertools.islice(recordsIterator, 0, chunkSize):
                values.append([self.formatValue(record.field(i)) for i in xrange(record.count())])
            if values:
                rows = [u'(' + u', '.join(value) + u')' for value in values]
                stmt = stmtInsert + ','.join(rows)
                self.query(stmt)

    def prepareInsertInto(self, table, fields):
        table = self.forceTable(table)
        return u'INSERT INTO {tableName} ({fields})'.format(
            tableName=table.name(),
            fields=u','.join(map(self.escapeFieldName, fields))
        )

    def prepareOnDuplicateKeyUpdate(self, fields, updateFields=None, keepOldFields=None):
        u"""
        Формирование условий обновления полей в INSERT INTO-запросе
        :param fields: все затрагиваемые поля
        :type fields: list
        :param updateFields: список обновляемых полей (если не задано - все, кроме неизменяемых)
        :type updateFields: list
        :param keepOldFields: список полей, значения которых не изменяются в результате запроса
        :type keepOldFields: list
        :rtype: unicode
        """
        updateMap = {}
        if keepOldFields is not None:
            if updateFields is None:
                updateFields = list(set(fields).difference(set(keepOldFields)))
            else:
                for field in keepOldFields:
                    updateMap[field] = u'{field}={field}'.format(field=self.escapeFieldName(field))
        if updateFields is not None:
            for field in updateFields:
                updateMap[field] = u'{field}=VALUES({field})'.format(field=self.escapeFieldName(field))

        if updateMap:
            return u'ON DUPLICATE KEY UPDATE {0}'.format(u','.join(updateMap.itervalues()))

        return u''

    def insertFromSelect(self, tableDest, tableSrc, fieldDict, cond=None, group=None, updateFields=None, excludeFields=None):
        u"""
        Вставка / обновление из результата SELECT-запроса
        :param tableDest: Заполняемая/обновляемая таблица
        :param tableSrc: Таблица-источник
        :param fieldDict: { 'fieldName': CField }: словарь источников данных для полей таблицы
        :type fieldDict: dict
        :param cond: Условие для формирующего SELECT-запроса
        :param group: Группировка
        :param updateFields: Список обновляемых полей (для ON DUPLICATE KEY UPDATE)
        :param excludeFields: Список неизменяемых полей (для ON DUPLICATE KEY UPDATE)
        """
        if not fieldDict: return

        fields = fieldDict.keys()

        parts = [
            self.prepareInsertInto(tableDest, fields),
            self.selectStmt(tableSrc,
                            [field.alias(fieldName) if isinstance(field, CField) else CSqlExpression(self, field).alias(fieldName)
                             for fieldName, field in fieldDict.iteritems()],
                            cond,
                            group=group),
            self.prepareOnDuplicateKeyUpdate(fields, updateFields=updateFields, keepOldFields=excludeFields)
        ]

        self.query(u' '.join(parts))

    def insertValues(self, table, fields, values=None, keepOldFields=None, updateFields=None):
        u"""
        Множественная вставка в таблицу / обновление
        :param table: Имя таблицы
        :param fields:  Поля, затрагиваемые при обновлении/вставки
        :param values: [list of tuple]: Список значениё полей
        :param keepOldFields: Сохраняемые поля
        :param updateFields: Обновляемые поля
        """
        if not (fields and values): return

        parts = [
            self.prepareInsertInto(table, fields),
            u'VALUES {0}'.format(u','.join(u'(%s)' % u','.join(map(self.formatArg, v)) for v in values)),
            self.prepareOnDuplicateKeyUpdate(fields, updateFields, keepOldFields)
        ]
        self.query(u' '.join(parts))

    def insertFromDictList(self, table, dctList, fields=None, keepOldFields=None, updateFields=None, chunkSize=None):
        u"""
        Множественная вставка в таблицу / обновление из спика словарей
        :param table: Имя таблицы
        :param dctList: [list of dict]: [ .., { .., 'fieldName': value, .. }, .. ]
        :param fields: Все затрагиваемые поля таблицы (если не задано, берутся из первого словаря)
        :param keepOldFields: Сохраняемые поля
        :param updateFields: Обновляемые поля
        :param chunkSize: Разбиение запроса на группы по chunkSize
        """
        if not dctList: return
        if not fields:
            fields = dctList[0].keys()
        if not chunkSize:
            chunkSize = len(dctList)

        listIterator = iter(dctList)
        for _ in xrange(0, len(dctList), chunkSize):
            values = [
                tuple(dct.get(field) for field in fields)
                for dct in itertools.islice(listIterator, 0, chunkSize)
            ]
            self.insertValues(table, fields, values, keepOldFields=keepOldFields, updateFields=updateFields)

    def insertOrUpdate(self, table, record):
        table = self.forceTable(table)
        idFieldName = table.idFieldName()
        if record.isNull(idFieldName):
            return self.insertRecord(table, record)
        else:
            return self.updateRecord(table, record)

    def deleteRecord(self, table, where):
        table = self.forceTable(table)
        #        table.beforeUpdate(record)
        stmt = 'DELETE FROM  ' + table.name() + self.prepareWhere(where)
        self.query(stmt)

    def markRecordsDeleted(self, table, where):
        table = self.forceTable(table)
        #        table.beforeUpdate(record)
        stmt = 'UPDATE  ' + table.name() + ' SET deleted=1 '
        if isinstance(table, CDocumentTable):
            now = QtCore.QDateTime.currentDateTime().addSecs(QtGui.qApp.getDatetimeDiff())
            stmt += ", modifyDateTime = '%s', modifyPerson_id = %s " % \
                    (now.toString(QtCore.Qt.ISODate),
                     QtGui.qApp.userId if QtGui.qApp.userId else 'NULL')
        if isinstance(where, tuple):
            where = list(where)
        if isinstance(where, list):
            where.append('deleted = 0')
        else:
            where = '(' + where + ') AND deleted = 0'
        stmt += self.prepareWhere(where)
        self.query(stmt)

    def updateRecords(self, table, expr, where=None):
        recQuery = None
        if table and expr:
            table = self.forceTable(table)
            if isinstance(expr, QtSql.QSqlRecord):
                tmpRecord = QtSql.QSqlRecord(expr)
                sets = []
            else:
                tmpRecord = QtSql.QSqlRecord()
                sets = []
                if not isinstance(expr, (list, tuple)):
                    sets = [expr]
                else:
                    sets.extend(expr)
            table.beforeUpdate(tmpRecord)
            for i in xrange(tmpRecord.count()):
                sets.append(table[tmpRecord.fieldName(i)].eq(tmpRecord.value(i)))
            stmt = 'UPDATE ' + table.name() + ' SET ' + ', '.join(sets) + self.prepareWhere(where)
            recQuery = self.query(stmt)
        return recQuery

    def getSum(self, table, sumCol='*', where=''):
        stmt = self.selectStmt(table, 'SUM(%s)' % sumCol, where)
        query = self.query(stmt)
        if query.first():
            return query.value(0)
        else:
            return 0

    def getCount(self, table=None, countCol='1', where='', stmt=None):
        if stmt is None:
            stmt = self.selectStmt(table, 'COUNT(%s)' % countCol, where)
        query = self.query(stmt)
        if query.first():
            return query.value(0).toInt()[0]
        else:
            return 0

    def getDistinctCount(self, table, countCol='*', where=''):
        stmt = self.selectStmt(table, 'COUNT(DISTINCT %s)' % countCol, where)
        query = self.query(stmt)
        if query.first():
            return query.value(0).toInt()[0]
        else:
            return 0

    def getColumnValues(self, table, column='id', where='', order='', limit=None, isDistinct=False,
                        handler=forceString):
        stmt = self.selectStmt(table, column, where, order=order, limit=limit, isDistinct=isDistinct)
        query = self.query(stmt)
        result = []
        while query.next():
            result.append(handler(query.value(0)))
        return result

    def getColumnValueMap(self, table, keyColumn='', valueColumn='', where='', order='', limit=None, isDistinct=False,
                          keyHandler=forceRef, valueHandler=forceRef):
        stmt = self.selectStmt(table, [keyColumn, valueColumn], where, order=order, limit=limit, isDistinct=isDistinct)
        query = self.query(stmt)
        result = {}
        while query.next():
            result[keyHandler(query.value(0))] = valueHandler(query.value(1))
        return result

    def getIdList(self, table=None, idCol='id', where='', order='', limit=None, stmt=None):
        if stmt is None:
            stmt = self.selectStmt(table, idCol, where, order=order, limit=limit)
        query = self.query(stmt)
        result = []
        while query.next():
            result.append(query.value(0).toInt()[0])
        return result

    # generator
    def iterIdList(self, table=None, idCol='id', where='', order='', limit=None, stmt=None):
        if stmt is None:
            stmt = self.selectStmt(table, idCol, where, order=order, limit=limit)
        query = self.query(stmt)
        while query.next():
            yield query.value(0).toInt()[0]

    def getDistinctIdList(self, table, idCol='id', where='', order='', limit=None):
        stmt = self.selectStmt(table, idCol, where, order=order, limit=limit, isDistinct=True)
        query = self.query(stmt)
        result = []
        while query.next():
            result.append(query.value(0).toInt()[0])
        return result

    # @param rowNumberFieldName: псевдоним столбца, в который будет выводится номер строки (если имя задано).
    def getRecordList(self, table=None, cols='*', where='', order='', isDistinct=False, limit=None, rowNumberFieldName=None,
                      group='', stmt=None):
        if stmt is None:
            stmt = self.selectStmt(table, cols, where, group=group, order=order, isDistinct=isDistinct, limit=limit,
                                   rowNumberFieldName=rowNumberFieldName)
        res = []
        query = self.query(stmt)
        while query.next():
            res.append(query.record())
        return res

    # generator-style version of getRecordList
    def iterRecordList(self, table=None, cols='*', where='', order='', isDistinct=False, limit=None, rowNumberFieldName=None,
                       group='', having='', stmt=None):
        if stmt is None:
            stmt = self.selectStmt(table, cols, where, group=group, order=order, isDistinct=isDistinct, limit=limit,
                                   rowNumberFieldName=rowNumberFieldName, having=having)
        query = self.query(stmt)
        while query.next():
            yield query.record()

    def getRecordListGroupBy(self, table, cols='*', where='', group='', order=''):
        stmt = self.selectStmt(table, cols, where, group=group, order=order)
        res = []
        query = self.query(stmt)
        while query.next():
            res.append(query.record())
        return res

    def translate(self, table, keyCol, keyVal, valCol, idFieldName='id', order=''):
        u"""
        Возвращает значение поля для записи, соответствующей ключу.
        Ищет в таблице table запись, у которой значение ключевого поля keyCol равно ключу keyVal и возвращает
        значение поля valCol этой записи.

        :param table: таблица для поиска
        :param keyCol: ключевое поле (столбец)
        :param keyVal: значение ключа поиска для ключевого поля/столбца
        :param valCol: поле, значение которого необходимо вернуть из найденой записи
        :param order: сортировка
        :param idFieldName: наименование primary key
        :return: значение поля valCol для найденной по ключу записи таблицы table
        """
        if keyCol == 'id' and keyVal is None:
            return None
        table = self.forceTable(table, idFieldName)
        if not isinstance(keyCol, CField):
            keyCol = table[keyCol]
        record = self.getRecordEx(table, valCol, keyCol.eq(keyVal), order)
        if record:
            return record.value(0)
        else:
            return None

    def translateEx(self, table, keyCol, keyVal, valCol):
        # При наличии флага deleted проверяем, чтобы он был равен 0
        if keyCol == 'id' and keyVal is None:
            return None
        self.checkdb()
        table = self.forceTable(table)
        if not isinstance(keyCol, CField):
            keyCol = table[keyCol]
        cond = [keyCol.eq(keyVal)]
        if table.hasField('deleted'):
            cond.append(table['deleted'].eq(0))
        record = self.getRecordEx(table, valCol, cond)
        if record:
            return record.value(0)

    def copyDepended(self, table, masterKeyCol, currentId, newId):
        table = self.forceTable(table)
        if not isinstance(masterKeyCol, CField):
            masterKeyCol = table[masterKeyCol]
        masterKeyColName = masterKeyCol.field.name()
        result = []
        stmt = self.selectStmt(table, '*', masterKeyCol.eq(currentId), order='id')
        qquery = self.query(stmt)
        while qquery.next():
            record = qquery.record()
            record.setNull('id')
            record.setValue(masterKeyColName, toVariant(newId))
            result.append(self.insertRecord(table, record))
        return result

    def getDescendants(self, table, groupCol, itemId):
        table = self.forceTable(table)
        group = groupCol if isinstance(groupCol, CField) else table[groupCol]

        result = set([itemId])
        parents = [itemId]

        while parents:
            cond = [group.inlist(parents)]
            if table.hasField('deleted'):
                cond.append(table['deleted'].eq(0))
            children = set(self.getIdList(table, where=cond))
            newChildren = children - result
            result |= newChildren
            parents = newChildren
        return list(result)

    def getTheseAndParents(self, table, groupCol, idList):
        table = self.forceTable(table)
        idField = table['id']
        group = groupCol if isinstance(groupCol, CField) else table[groupCol]

        result = set(idList)
        children = idList

        while children:
            parents = set(self.getDistinctIdList(table, idCol=groupCol, where=[idField.inlist(children), group.isNotNull()]))
            newParents = parents - result
            result |= newParents
            children = newParents
        return list(result)

    ## Поиск общего "родительского" элемента для указанного списка элементов
    #    @param table: имя таблицы (или инстанс CTable), элементы которой надо обрабатывать
    #    @param idList: список id элементов (или одно значение), для которых производится поиск "родительского" элемента
    #    @param groupCol: имя поля, по которому осуществляется построение иерархии в базе данных
    #    @param idCol: имя поля, на которое ссылается поле группировки и значения которого переданы в idList
    #    @param searchTopCommonParent: флаг, указывающий необходимость искать не первый общей элемент-"родител", а самый верхний, не имеющий "родителя"
    #    @param maxLevels: максимальное количество обрабатываемых уровней иерархии
    def getCommonParent(self, table, idList, groupCol='group_id', idCol='id', searchTopCommonParent=False, maxLevels=32):
        table = self.forceTable(table)

        idCol = idCol if isinstance(idCol, CField) else table[idCol]

        if not isinstance(idList, (list, set)):
            idList = [idList]

        idSet = set(idList)
        while maxLevels > 0 and idSet:
            oldIdSet = idSet
            parentIdRecordList = QtGui.qApp.db.getRecordList(table, groupCol, idCol.inlist(idSet))
            idSet = set([forceRef(record.value(0)) for record in parentIdRecordList])

            # Если список уникальных родителей состоит из одного элемента
            if len(idList) == 1:
                # Если не надо искать верхнего родителя, то возвращаем найденного родителя
                if not searchTopCommonParent:
                    return idSet.pop()
                # Иначе (если надо искать верхнего родителя), перебераем дальше до тех пор,
                # пока не найдем один общий для всех элемент, но без родителя
                elif None in idSet and len(oldIdSet) == 1:
                    return oldIdSet.pop()

        return None

    ## Поиск общего корневого (топового, верхнего) "родительского" элемента для указанного списка элементов
    #    @param table: имя таблицы (или инстанс CTable), элементы которой надо обрабатывать
    #    @param idList: список id элементов (или одно значение), для которых производится поиск корневого "родительского" элемента
    #    @param groupCol: имя поля, по которому осуществляется построение иерархии в базе данных
    #    @param idCol: имя поля, на которое ссылается поле группировки и значения которого переданы в idList
    #    @param maxLevels: максимальное количество обрабатываемых уровней иерархии
    def getTopParent(self, table, idList, groupCol='group_id', idCol='id', maxLevels=32):
        return self.getCommonParent(table=table,
                                    idList=idList,
                                    groupCol=groupCol,
                                    idCol=idCol,
                                    searchTopCommonParent=True,
                                    maxLevels=maxLevels)

    # Поиск всех записей таблицы, связанных c указанными (с учетом как прямых, так и косвенных связей)
    #    @param table: имя таблицы (или инстанс CTable), элементы которой надо обрабатывать
    #    @param idList: список id элементов (или одно значение), для которых производится поиск связанных с ними
    #    @param groupCol: имя поля, по которому осуществляется связь элементов в базе данных
    #    @param idCol: имя поля, на которое ссылается связующее поле и значения которого переданы в idList
    #    @param maxLevels: максимальное количество обрабатываемых уровней связи
    def getAllRelated(self, table, idList, groupCol, idCol='id', maxLevels=32):
        topParentId = self.getTopParent(table=table,
                                        idList=idList,
                                        groupCol=groupCol,
                                        idCol=idCol,
                                        maxLevels=maxLevels)
        if not topParentId:
            return idList if isinstance(idList, (list, set, tuple)) else [idList]

        return self.getDescendants(table, groupCol, topParentId)


class CDatabaseRoutine(object):
    u"""
     cond = [.., db.func.age(tableClient['birthDate'], tableEvent['setDate']) >= 18
    """

    FUNCTION = 1
    PROCEDURE = 2

    def __init__(self, db, name, type):
        self._db = db
        self._name = name
        self._type = type

    def __call__(self, *args, **kwargs):
        nameWithArgs = u'{0}({1})'.format(self._name, u', '.join(self._db.formatArg(it) for it in args))
        return self._db.query(u'CALL {0};'.format(nameWithArgs)) if self._type == CDatabaseRoutine.PROCEDURE else CSqlExpression(self._db, nameWithArgs)


class CDatabaseRoutineMap(object):
    def __init__(self, db, routineType):
        self._db = db
        self._routineType = routineType
        self._routineMap = None

    def __getattr__(self, item):
        if item in self._routineMap:
            return self._routineMap[item]
        if item in self.__dict__:
            return self.__dict__[item]
        raise CDatabaseException('Routine \'{0}.{1}\' doesn`t exists'.format(self._db.db.databaseName(), item))

    def _load(self):
        raise NotImplementedError


class CMySqlRoutineMap(CDatabaseRoutineMap):
    def __init__(self, db, routineType):
        CDatabaseRoutineMap.__init__(self, db, routineType)
        self._load()

    def _load(self):
        table = self._db.table('INFORMATION_SCHEMA.ROUTINES')
        typeNameMap = {
            CDatabaseRoutine.FUNCTION : 'FUNCTION',
            CDatabaseRoutine.PROCEDURE: 'PROCEDURE'
        }
        cols = [
            table['ROUTINE_NAME'],
            table['ROUTINE_TYPE']
        ]
        cond = [
            table['ROUTINE_SCHEMA'].eq(self._db.db.databaseName()),
            table['ROUTINE_TYPE'].eq(typeNameMap[self._routineType])
        ]
        self._routineMap = dict((forceString(rec.value('ROUTINE_NAME')),
                                 CDatabaseRoutine(self._db, forceString(rec.value('ROUTINE_NAME')), self._routineMap))
                                for rec in self._db.iterRecordList(table, cols, cond))


class CMySqlDatabase(CDatabase):
    limit1 = 'LIMIT 0, %d'
    limit2 = 'LIMIT %d, %d'
    CR_SERVER_GONE_ERROR = 2006
    CR_SERVER_LOST = 2013

    returnedDeadlockErrorText          = u'Deadlock found when trying to get lock;'

    def __init__(self, serverName, serverPort, databaseName, userName, password, connectionName=None, compressData=False, afterConnectFunc=None, **kwargs):
        CDatabase.__init__(self, afterConnectFunc)
        self.createConnection('QMYSQL', connectionName, serverName, serverPort, databaseName, userName, password)
        options = []
        if compressData:
            options.append('CLIENT_COMPRESS=1')
        if options:
            self.db.setConnectOptions(';'.join(options))
        self.connectUp()
        self.query('SET NAMES \'utf8\' COLLATE \'utf8_general_ci\';')
        self.query('SET SQL_AUTO_IS_NULL=0;')
        self.query('SET SQL_MODE=\'\';')

        self._func = None
        self._proc = None

    NULL = property(lambda self: CSqlExpression(self, 'NULL'))
    func = property(lambda self: self.loadFunctions()._func)
    proc = property(lambda self: self.loadFunctions()._proc)

    def loadFunctions(self):
        if self._func is None:
            self._func = CMySqlRoutineMap(self, CDatabaseRoutine.FUNCTION)
        if self._proc is None:
            self._proc = CMySqlRoutineMap(self, CDatabaseRoutine.PROCEDURE)
        return self

    def getConnectionId(self):
        query = self.query('SELECT CONNECTION_ID();')
        return forceRef(query.record().value(0)) if query.first() else None

    def escapeFieldName(self, name):
        u = unicode(name)
        if u.startswith('`') and u.endswith('`'):
            return u
        else:
            return '`' + u + '`'

    escapeTableName = escapeFieldName
    escapeSchemaName = escapeFieldName

    def prepareLimit(self, limit):
        if isinstance(limit, (list, tuple)):
            assert len(limit) == 2
            return self.limit2 % limit
        elif isinstance(limit, int):
            return self.limit1 % limit
        else:
            return ''

    def nestedTransaction(self):
        QtSql.QSqlQuery(self.db).exec_('SAVEPOINT LEVEL_%d' % (self._openTransactionsCount + 1))
        if self.db.lastError().isValid():
            raise CDatabaseException(CDatabase.errTransactionError, self.db.lastError())

    def nestedCommit(self):
        QtSql.QSqlQuery(self.db).exec_('RELEASE SAVEPOINT LEVEL_%d' % self._openTransactionsCount)
        if self.db.lastError().isValid():
            raise CDatabaseException(CDatabase.errNestedCommitTransactionError, self.db.lastError())

    def nestedRollback(self):
        QtSql.QSqlQuery(self.db).exec_('ROLLBACK TO SAVEPOINT LEVEL_%d' % self._openTransactionsCount)
        if self.db.lastError().isValid():
            raise CDatabaseException(CDatabase.errNestedRollbackTransactionError, self.db.lastError())

    def isConnectionLostError(self, sqlError):
        if sqlError and sqlError.number() in [CMySqlDatabase.CR_SERVER_GONE_ERROR,
                                              CMySqlDatabase.CR_SERVER_LOST]:
            return True
        return CDatabase.isConnectionLostError(self, sqlError)


class CInterbaseDatabase(CDatabase):
    aliasSymbol = ''

    limit1 = 'FIRST %d'
    limit2 = 'FIRST %d SKIP %d'
    convMethod = {
        QVariant.Int      : lambda val: unicode(val.toInt()[0]),
        QVariant.UInt     : lambda val: unicode(val.toUInt()[0]),
        QVariant.LongLong : lambda val: unicode(val.toLongLong()[0]),
        QVariant.ULongLong: lambda val: unicode(val.toULongLong()[0]),
        QVariant.Double   : lambda val: unicode(val.toDouble()[0]),
        QVariant.Bool     : lambda val: u'1' if val.toBool() else u'0',
        QVariant.Char     : lambda val: decorateString(val.toString()),
        QVariant.String   : lambda val: decorateString(val.toString()),
        QVariant.Date     : lambda val: decorateString(val.toDate().toString('dd.MM.yyyy')),
        QVariant.Time     : lambda val: decorateString(val.toTime().toString('hh:mm:ss')),
        QVariant.DateTime : lambda val: decorateString(val.toDateTime().toString('dd.MM.yyyy hh:mm:ss')),
        QVariant.ByteArray: lambda val: 'x\'' + str(val.toByteArray().toHex()) + '\'',
    }

    DEFAULT_LC_CTYPE = 'Win_1251'  # may be 'WIN1251', 'windows-1251', 'UNICODE_FSS', etc.

    def __init__(self, serverName, serverPort, databaseName, userName, password, connectionName=None, afterConnectFunc=None, **kwargs):
        CDatabase.__init__(self, afterConnectFunc)
        self.createConnection('QIBASE', connectionName, serverName, serverPort, databaseName, userName, password)

        LC_CTYPE = kwargs.get('LC_CTYPE', '') or CInterbaseDatabase.DEFAULT_LC_CTYPE
        self.db.setConnectOptions('ISC_DPB_LC_CTYPE={0}'.format(LC_CTYPE))
        self.connectUp()

    def escapeFieldName(self, name):
        u = unicode(name)
        if u.startswith('"') and u.endswith('"'):
            return u
        else:
            return '"' + u.replace('"', '""') + '"'

    escapeTableName = escapeFieldName

    def prepareLimit(self, limit):
        if isinstance(limit, (list, tuple)):
            assert len(limit) == 2
            return self.limit2 % (limit[1], limit[0])
        elif isinstance(limit, int):
            return self.limit1 % limit
        else:
            return ''

    def selectStmt(self, table, fields='*', where='', group='', order='', limit=None, isDistinct=False):
        tableName = self.getTableName(table)
        return ' '.join([
            'SELECT',
            self.prepareLimit(limit),
            'DISTINCT' if isDistinct else '',
            self.prepareFieldList(fields),
            'FROM', tableName,
            self.prepareWhere(where),
            self.prepareGroup(group),
            self.prepareOrder(order),
        ])

    def getTestConnectionStmt(self):
        return u'SELECT \'test connection query\' FROM rdb$database;'


class CODBCDatabase(CDatabase):
    #    limit1 = 'FIRST %d'
    #    limit2 = 'FIRST %d SKIP %d'

    def __init__(self, serverName, serverPort, databaseName, userName, password, connectionName=None, afterConnectFunc = None, **kwargs):
        CDatabase.__init__(self, afterConnectFunc)
        self.createConnection('QODBC3', connectionName, serverName, serverPort, databaseName, userName, password)
        self.db.setConnectOptions('SQL_ATTR_ACCESS_MODE=SQL_MODE_READ_ONLY')
        self.connectUp()

    def escapeFieldName(self, name):
        u = unicode(name)
        if u.startswith('"') and u.endswith('"'):
            return u
        else:
            return '"' + u.replace('"', '""') + '"'

    escapeTableName = escapeFieldName

    def prepareLimit(self, limit):
        return ''


class CRecordCache(object):
    def __init__(self, capacity=200, fakeValues=None):
        if not fakeValues:
            fakeValues = []
        self.map = {}
        self.queue = []
        self.fakeKeys = []
        self.capacity = capacity
        self.fakeValues = fakeValues
        if fakeValues:
            self.loadFakeValues(fakeValues)

    def loadFakeValues(self, fakeValues):
        if fakeValues:
            self.clearFakeValues()
            for fakeKey, fakeRecord in fakeValues:
                self.fakeKeys.append(fakeKey)
                self.map[fakeKey] = fakeRecord
        else:
            self.clearFakeValues()

    def clearFakeValues(self):
        for key in self.fakeKeys:
            if key in self.map:
                del (self.map[key])
        self.fakeKeys = []

    def invalidate(self, keyList=None):
        if not keyList:
            keyList = []
        if keyList:
            for key in keyList:
                if self.map.has_key(key):
                    del self.map[key]
                if key in self.queue:
                    self.queue.remove(key)
        else:
            self.map = {}
            self.queue = []
            self.fakeKeys = []
            if self.fakeValues:
                self.loadFakeValues(self.fakeValues)

    def has_key(self, key):
        return self.map.has_key(key)

    def get(self, key):
        return self.map.get(key, None)

    def put(self, key, record):
        if self.map.has_key(key):
            self.map[key] = record
        else:
            if self.capacity and len(self.queue) >= self.capacity:
                top = self.queue[0]
                del (self.queue[0])
                del (self.map[top])
            self.queue.append(key)
            self.map[key] = record


class CTableRecordCache(CRecordCache):
    def __init__(self, database, table, cols='*', capacity=300, fakeValues=None, idCol=None, deletedCol=False, idFieldName='id', filter=None):
        if not fakeValues:
            fakeValues = []
        CRecordCache.__init__(self, capacity, fakeValues)
        self.database = database
        self.table = table
        try:
            self.idCol = self.database.mainTable(self.table, idFieldName)[idCol] if idCol else self.database.mainTable(self.table, idFieldName).idField()
            orderFieldName = self.database.mainTable(self.table).idField().name()
        except:
            self.idCol = orderFieldName = self.database.mainTable(self.table, idFieldName)[idFieldName]

        self.setCols(cols)
        self.deletedCol = deletedCol
        self._order = u'%s DESC' % orderFieldName
        self.filter = filter

    # noinspection PyAttributeOutsideInit
    def setCols(self, cols):
        if isinstance(cols, (tuple, list)):
            cols = ', '.join(u'%s' % c for c in cols)
        # Если среди указаных полей нет поля для сравнения (idCol), то добавить его
        if cols.strip() != '*' \
                and not re.search(ur'\b%s\b' % re.escape(unicode(self.idCol)), cols):
            cols = ', '.join([cols, unicode(self.idCol)])
        self.cols = cols

    def strongFetch(self, idList):
        fieldName = self.idCol.field.name()
        records = self.database.getRecordList(self.table,
                                              self.cols if self.cols == '*' else [self.cols, self.idCol],
                                              self.idCol.inlist(idList),
                                              order=self._order,
                                              limit=self.capacity)
        for record in records:
            itemId = record.value(fieldName).toInt()[0]
            self.put(itemId, record)

    def fetch(self, idList):
        filteredIdList = [itemId for itemId in idList if not self.has_key(itemId)]
        if filteredIdList:
            self.strongFetch(idList)

    def weakFetch(self, itemId, idList):
        if not self.has_key(itemId):
            self.fetch(idList)

    def get(self, itemId):
        if type(itemId) == QVariant:
            itemId = itemId.toInt()[0]
        res = CRecordCache.get(self, itemId)

        # atronah: Чтобы избежать ситуации с постоянным обращением к базе, если в кеше есть запись, но она пустая
        # было принято решение разделить понятия
        # None - отсутствие в кэше, используется в CRecordCache.get как результат отстутствия в словаре
        #  и
        # QtSql.QSqlRecord() - есть в кэше, но имеет пустое значение.
        if res is None:
            cond = [self.idCol.eq(itemId)]
            if self.deletedCol:
                cond.append(self.database.mainTable(self.table)['deleted'].eq(0))
            if self.filter:
                tblPerson = self.database.table('Person')
                tblOrgStructJob = self.database.table('OrgStructure_Job')
                tblorgStruct = self.database.table('OrgStructure')
                queryTbl = tblPerson.innerJoin(tblorgStruct, tblPerson['orgStructure_id'].eq(tblorgStruct['id']))
                queryTbl = queryTbl.innerJoin(tblOrgStructJob, tblOrgStructJob['master_id'].eq(tblorgStruct['id']))
                orgStructJobId = self.database.translate(queryTbl, tblPerson['id'], QtGui.qApp.userId, tblOrgStructJob['id'])
                if orgStructJobId:
                    cond.append(self.database.mainTable(self.table)['orgStructureJob_id'].eq(orgStructJobId))
            res = self.database.getRecordEx(self.table, self.cols, cond, order=self._order)

            self.put(itemId, res if res else QtSql.QSqlRecord())

        # atronah: для совместимости со старым кодом решено не возвращать QtSql.QSqlRecord(), а как и раньше - None для пустой записи
        return res if res and not res.isEmpty() else None


class CTableFilteredRecordCache(CTableRecordCache):
    def __init__(self, database, table, cols='*', capacity=300, fakeValues=None, idCol=None, deletedCol=False, cond=None):
        CTableRecordCache.__init__(self, database, table, cols, capacity, fakeValues, idCol, deletedCol)
        self._cond = cond

    def strongFetch(self, idList):
        fieldName = self.idCol.field.name()
        whereStmt = self.idCol.inlist(idList)
        cond = self._cond
        if cond is not None:
            if isinstance(cond, basestring):
                cond = [cond]
            if isinstance(cond, list):
                whereStmt = QtGui.qApp.db.joinAnd([whereStmt] + cond)
        records = self.database.getRecordList(self.table,
                                              self.cols if self.cols == '*' else [self.cols, self.idCol],
                                              whereStmt,
                                              order = self._order,
                                              limit=self.capacity)
        for record in records:
            itemId = record.value(fieldName).toInt()[0]
            self.put(itemId, record)


def undotLikeMask(val):
    if isinstance(val, CSqlExpression): return val
    if val.endswith('...'):
        val = val[:-3]+'%'
    return val.replace('...','%').replace('%%', '%')


def addCondLike(cond, field, val):
    if val.strip(' .'):
        if val.find('...') != -1:
            cond.append(field.like(val.strip()))
        else :
            cond.append(field.eq(val.strip()))


def addCondEq(cond, field, val):
    if val:
        cond.append(field.eq(val))


def addDateInRange(cond, field, begDate, endDate):
    if begDate and not begDate.isNull():
        cond.append(field.ge(begDate))
    if endDate and not endDate.isNull():
        cond.append(field.lt(endDate.addDays(1)))


def connectDataBase(driverName, serverName, serverPort, databaseName, userName, password, connectionName=None, compressData=False, afterConnectFunc=None, **kwargs):
    driverName = unicode(driverName).upper()
    if driverName == 'MYSQL':
        return CMySqlDatabase(serverName, serverPort, databaseName, userName, password, connectionName, compressData=compressData, afterConnectFunc=afterConnectFunc, **kwargs)
    elif driverName in ['INTERBASE', 'FIREBIRD']:
        return CInterbaseDatabase(serverName, serverPort, databaseName, userName, password, connectionName, afterConnectFunc=afterConnectFunc, **kwargs)
    elif driverName in ['ODBC']:
        return CODBCDatabase(serverName, serverPort, databaseName, userName, password, connectionName, afterConnectFunc=afterConnectFunc, **kwargs)
    else:
        raise CDatabaseException(CDatabase.errUndefinedDriver % driverName)


def connectDataBaseByInfo(connectionInfo):
    return connectDataBase(connectionInfo['driverName'], connectionInfo['host'], connectionInfo['port'], connectionInfo['database'], connectionInfo['user'], connectionInfo['password'], connectionInfo['connectionName'], connectionInfo['compressData'], connectionInfo.get('afterConnectFunc', None))