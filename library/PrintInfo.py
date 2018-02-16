# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from library.Utils import *


class CInfoContext(object):
    u"""Отображение (класс объекта, параметры объекта) -> Экземпляр класса"""
    def __init__(self):
        self._mapClassesToInstances = {}

    def getInstance(self, infoClass, *args, **kwargs):
        mapArgsToInstance = self._mapClassesToInstances.setdefault(infoClass, {})
        key = (args, tuple([x for x in kwargs.iteritems()]))
        if key in mapArgsToInstance:
            return mapArgsToInstance[key]
        else:
            result = infoClass(self, *args, **kwargs)
            if key != ((None, ), ()):
                mapArgsToInstance[key] = result
            return result


class CInfo(object):
    u"""Базовый класс для представления объектов при передаче в шаблоны печати"""
    def __init__(self, context, record=None):
        self._loaded = False
        self._ok = False
        self.context = context
        self._record = record

    def load(self):
        if not self._loaded:
            self._ok = self._load()
            self._loaded = True
        return self

    def setOkLoaded(self, ok=True):
        self._ok = ok
        self._loaded = True

    def getInstance(self, infoClass, *args, **kwargs):
        return self.context.getInstance(infoClass, *args, **kwargs)

    def __nonzero__(self):
        self.load()
        return self._ok

    def __cmp__(self, x):
        ss = unicode(self)
        sx = unicode(x)
        if ss>sx:
            return 1
        elif ss<sx:
            return -1
        else:
            return 0

    def __add__(self, x):
        return unicode(self) + unicode(x)

    def __radd__(self,x):
        return unicode(x) + unicode(self)

    def getProperties(self):
        result = []
        # class properties
        class_ = type(self)
        for name, value in class_.__dict__.iteritems():
            if name[:1] != '_' and isinstance(value, property):
                propvalue = self.__getattribute__(name)
                type_ = type(propvalue)
                result.append((name, str(type_), value.__doc__))
        return result


class CTemplatableInfoMixin:
    u"""Примесевый класс для представления возможности печати СInfo через собственный шаблон"""

    def getPrintTemplateContext(self):
        # "абстрактный" метод для получения контекста печати
        return None

    def getPrintTemplateList(self, printContext=None):
        # список пар (имяШаблона, idШаблона) подходящих для печати этого объекта
        from PrintTemplates import getPrintTemplates
        return getPrintTemplates(printContext if printContext else self.getPrintTemplateContext())

    def getData(self):
        # "абстрактный" метод для получения данных для шаблона печати
        return { }

    def formatByTemplateId(self, templateId):
        # формирование html по id шаблона
        from PrintTemplates import getTemplate, compileAndExecTemplate, htmlTemplate
        templateName, template, templateType = getTemplate(templateId)

        if templateType != htmlTemplate:
            template = u'<HTML><BODY>Поддержка шаблонов печати в формате'\
                u' отличном от html не реализована</BODY></HTML>'

        data = self.getData()
        html, canvases = compileAndExecTemplate(template, data)
        return html

    def formatByTemplate(self, name, printContext=None):
        # формирование html по имени шаблона
        for templateName, templateId in self.getPrintTemplateList(printContext):
            if templateName == name:
                return self.formatByTemplateId(templateId)
        return u'Шаблон "%s" не найден в контексте печати "%s"' % (name, printContext if printContext else self.getPrintTemplateContext())


class CInfoList(CInfo):
    u"""Базовый класс для представления списков (массивов) объектов при передаче в шаблоны печати"""
    def __init__(self, context):
        CInfo.__init__(self, context)
        self._items = []

    def __len__(self):
        self.load()
        return len(self._items)

    def __getitem__(self, key):
        self.load()
        return self._items[key]

    def __iter__(self):
        self.load()
        return iter(self._items)

    def __str__(self):
        self.load()
        return u', '.join([unicode(x) for x in self._items])

    def __nonzero__(self):
        self.load()
        return bool(self._items)

    def filter(self, **kw):
        self.load()

        result = CInfoList(self.context)
        result._loaded = True
        result._ok = True

        for item in self._items:
            if all([item.__getattribute__(key) == value for key, value in kw.iteritems()]):
                result._items.append(item)
        return result

    def __add__(self, right):
        if isinstance(right, CInfoList):
            right.load()
            rightItems = right.items
        elif isinstance(right, list):
            rightItems = right
        else:
            raise TypeError(u'can only concatenate CInfoList or list (not "%s") to CInfoList' % type(right).__name__)
        self.load()

        result = CInfoList(self.context)
        result._loaded = True
        result._ok = True

        result._items = self._items + rightItems
        return result


# atronah: Не помню, каков логический смысл CInfoProxyList, но этот класс нужен для формирования Read Only обертки
# для изменяемого класса с данными.
class CInfoProxy(CInfo):
    """
        Info-класс для шаблонов печати, который предоставляет доступ на чтение к атррибутам имеющегося контейнера данных,
        но предотвращает изменения данных в этом контейнере.
    """
    def __init__(self, context, baseObject):
        super(CInfoProxy, self).__init__(context)
        self._baseObject = baseObject


    # atronah: не учел, что setattr(instance, name, property) приводит к тому, что instance.name возвращает не значение, а объект типа property ><
    # def wrapBaseObject(self, baseObject):
    #     # Получение класса базового объекта (для того, чтобы вытянуть из него свойства (property)
    #     baseClass = type(baseObject)
    #
    #     import inspect
    #     if not inspect.isclass(baseClass):
    #         return False
    #
    #     self._baseObject = baseObject
    #     #Перебор всех аттрибутов класса в поисках свойств
    #     for attr in dir(baseClass):
    #         if type(attr) == property:
    #             # Получение значения свойства
    #             value = getattr(self._baseObject, attr)
    #             # Проверка на то, что значение свойства является простым типом
    #             isSimpleType = isinstance(value, (int, float,
    #                                               basestring,
    #                                               datetime.datetime, datetime.date, datetime.time,
    #                                               QtCore.QDateTime, QtCore.QDate, QtCore.QTime))
    #             setattr(self,
    #                     attr,
    #                     property(lambda obj: getattr(obj._baseObject, attr) if isSimpleType
    #                                                                           else CInfoProxy(obj._context, getattr(obj._baseObject, attr))))
    #
    #     return True

    def __getattr__(self, item):
        if self._baseObject:
            baseType = type(self._baseObject)
            value = None
            isExistsValue = True
            if inspect.isclass(baseType) and hasattr(self._baseObject, item):
                value = getattr(self._baseObject, item)
            elif baseType == dict and self._baseObject.has_key(item):
                value = self._baseObject[item]
            else:
                isExistsValue = False

            if isExistsValue:
                if isinstance(value, (int, float,
                                      basestring,
                                      datetime.datetime, datetime.date, datetime.time,
                                      QtCore.QDateTime, QtCore.QDate, QtCore.QTime,
                                      tuple, list
                                      )) or value is None:
                    return value
                return CInfoProxy(self.context, value)

        return getattr(super(CInfoProxy, self), item)


class CInfoProxyList(CInfo):
    def __init__(self, context):
        CInfo.__init__(self, context)
#        self._loaded = True
#        self._ok = True
        self._items = []

    def __len__(self):
        return len(self._items)

    def __getitem__(self, key): # чисто-виртуальный
        return None

    def __iter__(self):
        for i in xrange(len(self._items)): # цикл по self._items исп. нельзя т.к. у нас хитрый __getitem__
            yield self.__getitem__(i)

    def __str__(self):
        return u', '.join([unicode(x) for x in self.__iter__()])

    def __nonzero__(self):
        return bool(self._items)


class CDateInfo(ComparableMixin):
    def __init__(self, date=None):
        if date is None:
            self.date = QtCore.QDate()
        else:
            self.date = forceDate(date)

    def __str__(self):
        return forceString(self.date)

    def toString(self, fmt):
        return unicode(self.date.toString(fmt))

    def __nonzero__(self):
        return bool(self.date.isValid())

    def __add__(self, x):
        return forceString(self.date) + str(x)

    def __radd__(self,x):
        return str(x)+forceString(self.date)

    def _compare_to(self, other):
        if isinstance(other, CDateInfo):
            return (self.date, other.date)
        elif isinstance(other, CDateTimeInfo):
            return (self.date, other.date)
        elif isinstance(other, QDate):
            return (self.date, other)
        elif isinstance(other, QDateTime):
            return (self.date, other.date())

        raise NotImplementedError(u'CDateInfo._compare_to: incompatible type: "%s" (%s)' % (other, type(other)))

    year   = property(lambda self: self.date.year()  if self.date else None)
    month  = property(lambda self: self.date.month() if self.date else None)
    day    = property(lambda self: self.date.day()   if self.date else None)


class CTimeInfo(ComparableMixin):
    def __init__(self, time=None):
        self.time = QtCore.QTime() if time is None else time

    def toString(self, fmt=None):
        return unicode(self.time.toString(fmt)) if fmt else formatTime(self.time)

    def __str__(self):
        return formatTime(self.time)

    def __nonzero__(self):
        return bool(self.time.isValid())

    def __add__(self, x):
        return self.toString() + str(x)

    def __radd__(self,x):
        return str(x)+self.toString()

    def _compare_to(self, other):
        if isinstance(other, CTimeInfo):
            return self.time, other.time
        elif isinstance(other, QTime):
            return self.time, other
        raise NotImplementedError(u'CTimeInfo._compare_to: incompatible type: "%s" (%s)' % (other, type(other)))

    hour   = property(lambda self: self.time.hour())
    minute = property(lambda self: self.time.minute())
    second = property(lambda self: self.time.second())


class CDateTimeInfo(ComparableMixin):
    def __init__(self, date=None):
        if date is None:
            self.datetime = QtCore.QDateTime()
        else:
            self.datetime = forceDateTime(date)

    def __str__(self):
        if self.datetime:
            date = self.datetime.date()
            time = self.datetime.time()
            return forceString(date)+' '+formatTime(time)
        else:
            return ''

    def __nonzero__(self):
        return bool(self.datetime.isValid())

    def toString(self, fmt):
        return unicode(self.datetime.toString(fmt))

    def __add__(self, x):
        return forceString(self.datetime) + str(x)

    def __radd__(self,x):
        return str(x)+forceString(self.datetime)

    def _compare_to(self, other):
        if isinstance(other, CDateInfo):
            return self.date, other.date
        elif isinstance(other, CDateTimeInfo):
            return self.datetime, other.datetime
        elif isinstance(other, QDate):
            return self.date, other
        elif isinstance(other, QDateTime):
            return self.datetime, other

        raise NotImplementedError(u'CDateTimeInfo._compare_to: incompatible type: "%s" (%s)' % (other, type(other)))

    date   = property(lambda self: self.datetime.date())
    time   = property(lambda self: self.datetime.time())
    year   = property(lambda self: self.datetime.date.year()   if self.datetime else None)
    month  = property(lambda self: self.datetime.date.month()  if self.datetime else None)
    day    = property(lambda self: self.datetime.date.day()    if self.datetime else None)
    hour   = property(lambda self: self.datetime.time.hour()   if self.datetime else None)
    minute = property(lambda self: self.datetime.time.minute() if self.datetime else None)
    second = property(lambda self: self.datetime.time.second() if self.datetime else None)


class CRBInfo(CInfo):
    def __init__(self, context, id):
        CInfo.__init__(self, context)
        self.id = id
        assert self.tableName, 'tableName must be defined in derivative'

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord(self.tableName, '*', self.id) if self.id else None
        if record:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            self._initByRecord(record)
            return True
        else:
            self._code = ''
            self._name = ''
            self._initByNull()
            return False

    def _initByRecord(self, record):
        pass

    def _initByNull(self):
        pass

    def __str__(self):
        return self.load()._name

    code = property(lambda self: self.load()._code)
    name = property(lambda self: self.load()._name)
