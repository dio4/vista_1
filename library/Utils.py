# -*- coding: utf-8 -*-
import codecs
import datetime
import inspect
import locale
import logging
import os
import re
import sys
import traceback
import urllib2
from PyQt4 import QtCore, QtGui
from decimal import *
from functools import wraps

from PyQt4.QtCore import *
from PyQt4.QtGui import QMessageBox

getcontext().prec = 12
TWO_PLACES = Decimal(10) ** -2


def trUtf8(text, comment = ''):
    encoding = QtGui.QApplication.UnicodeUTF8
    callerInfo = inspect.stack()[1]
    callerModule = inspect.getmodule(callerInfo[0])
    contextParts = ['general']
    if callerModule:
        contextParts.append(callerModule.__name__)
    return QtGui.QApplication.translate('.'.join(contextParts), text, comment, encoding)


def generalConnectionName():
    return u'vistamed'


class smartDict():
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def __len__(self):
        return len(self.__dict__)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __delitem__(self, key):
        del self.__dict__[key]

    def __iter__(self):
        return self.__dict__.__iter__()

    def __contain__(self, key):
        return key in self.__dict__

    def clear(self):
        self.__dict__.clear()

    def copy(self):
        return smartDict(**self.__dict__)

    def get(self, key, default=None):
        return self.__dict__.get(key, default)

    def setdefault(self, key, default=None):
        return self.__dict__.setdefault(key, default)

    def update(self, d, **i):
        return self.__dict__.update(d, **i)

    def items(self):
        return self.__dict__.items()

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def iteritems(self):
        return self.__dict__.iteritems()

    def iterkeys(self):
        return self.__dict__.iterkeys()

    def itervalues(self):
        return self.__dict__.itervalues()

smartDictMethods = ['__dict__'] + [name for name, _ in inspect.getmembers(smartDict)]


class LazySmartDict(smartDict, object):
    def __getattribute__(self, name):
        # NOTE: we need to exclude special methods,
        # otherwise they will be called (twice)
        if name in smartDictMethods:
            return object.__getattribute__(self, name)
        v = object.__getattribute__(self, name)()
        # aint no method will be called for the second time
        if not name.startswith('__'):
            setattr(self, name, lambda: v)
        return v

    def __getitem__(self, key):
        # values are assumed to be lazy, so they are
        # called when upon dict-style access
        return self.__dict__[key]()

    def values(self):
        return [v() for v in self.__dict__.values()]

    def items(self):
        return [(k, v()) for k, v in self.__dict__.items()]

    def iteritems(self):
        for k, v in self.__dict__.iteritems():
            yield k, v()

    def itervalues(self):
        for v in self.__dict__.itervalues():
            yield v()

    def get(self, key, default=None):
        return self.__dict__.get(key, lambda: default)()

    def setdefault(self, key, default=None):
        return self.__dict__.setdefault(key, lambda: default)


# added by atronah (31.05.2012) for issue #350- проверка существования поля в базе (записи из базы) с выводом сообщения
def checkExistFieldWithMessage(record,  fieldName,  parentWidget = None,  tableName = u'unknown'):
    fieldExist = not (record.indexOf(fieldName) == -1)
    if not fieldExist:
        if parentWidget:
            QMessageBox.information(parentWidget, 
                                                    u'Обновите структуру базы данных', 
                                                    u'Отсутствует поле %s в таблице %s' % (fieldName,  tableName))
    return fieldExist


def getVal(someDict, key, default):
    return someDict.get(key, default)


def getPref(someDict, key, default):
    return someDict.get(prepareKey(key), default)


def getPrefDate(someDict, key, default):
    return forceDate(someDict.get(prepareKey(key), default))


def getPrefTime(someDict, key, default):
    return forceTime(someDict.get(prepareKey(key), default))


def getPrefRef(someDict, key, default):
    return forceRef(someDict.get(prepareKey(key), default))


def getPrefBool(someDict, key, default):
    return forceBool(someDict.get(prepareKey(key), default))


def getPrefInt(someDict, key, default):
    return forceInt(someDict.get(prepareKey(key), default))


def getPrefString(someDict, key, default):
    return forceString(someDict.get(prepareKey(key), default))


def prepareKey(key):
    # TODO: skkachaev: Замедляет загрузку. Если будут баги — надо в сохранении заменять, а не в загрузке
    return unicode(key).lower()  #.replace('/', '').replace('\\', '')


def setPref(someDict, key, value):
    someDict[prepareKey(key)] = value


def toNativeType(val):
    if hasattr(val, 'isNull') and val.isNull():
        return None
    
    isOk = True
    try:
        if isinstance(val, QVariant):
            valType = val.type()
            if valType == QVariant.Int:
                val, isOk = val.toInt()
            elif valType == QVariant.String:
                val = val.toString()
            elif valType == QVariant.Double:
                val, isOk = val.toDouble()
            elif valType == QVariant.Date:
                val = val.toDate()
            elif valType == QVariant.DateTime:
                val = val.toDateTime()
            elif valType == QVariant.Bool:
                val = val.toBool()
       
        if isinstance(val, QString):
            val = unicode(val)
        elif isinstance(val, QDate):
            val = val.toPyDate()
        elif isinstance(val, QDateTime):
            val = val.toPyDateTime()
    except:
        isOk = False
    
    return val if isOk else None


def trim(s):
    return forceString(s).strip()


# Убирает из сложносоставленных имен из середины повторяющиеся " " и "-"
# НЕ убирает "Эркин- Угли"/"Эркин- -Угли" и всё подобное
# @nameMode == lastName || firstName || patrName
# Нужно для того, чтобы была возможность в patrName и только в нём не обрезать единственную "-"
def trimNameSeparators(s, nameMode):
    if s == "-":
        return s

    s = s.strip(" -")
    r = u''

    for i in range(0, len(s)-1):
        if (s[i] != '-' and s[i] != ' ') or s[i] != s[i+1]:
            r += s[i]

    if len(s) != 0:
        r += s[len(s)-1]
    return r


def nameCase(s):
    r = u''
    up = True
    for c in s:
        if c.isalpha():
            if up:
                r += c.upper()
                up = False
            else:
                r += c.lower()
        else:
            up = True
            r += c
    return r


def isNameValid(name):
    return not re.search(r'''[0-9a-zA-Z`~!@#$%^&*_=+\\|{}[\];:"<>?/().,]''', forceStringEx(name))


## Разбивает серию документа на 2 части, используя в качестве разделителя один из символов '=/_|-'.
# @param seria: серия документа в виде python-строки.
# @param isCheckLastDash: проверяет серию на наличие символа "-" в конце и, если найден, заменяя его на " -" 
#                         и удаляя его из списка разделителей серии
# @return: две строки, являющейся правой и левой частью серии.
def splitDocSerial(serial, isCheckLastDash = False):
    serial = trim(serial)
    
    removedSymbols = '=/_|'
    if isCheckLastDash and serial and (serial[-1] == '-'):
        serial = serial[:-1] + ' -'
    else:
        removedSymbols += '-'
    
    for c in removedSymbols:
        serial = serial.replace(c,' ')
    
    parts = trim(serial).partition(' ')
    return parts[0], parts[2]


def delWasteSymbols(serial):
    for c in ' -=/_|':
        serial = serial.replace(c, '')
    return serial


def addDots(s):
    if s and s[-3:] != '...':
        return s + '...'
    else:
        return s


def addDotsBefore(s):
    if s and s[:3] != '...':
        return '...' + s
    else:
        return s


def addDotsEx(s):
    if s:
        result = s
        if s[:3]  != '...': result = '...' + result
        if s[-3:] != '...': result = result + '...'
        return result
    else:
        return s


def toVariant(v):
    if v is None:
        return QVariant()
    t = type(v)
    if t == QVariant:
        return v
    elif t == datetime.time:
        return QVariant(QTime(v))
    elif t == datetime.datetime:
        return QVariant(QDateTime(v))
    elif t == datetime.date:
        return QVariant(QDate(v))
    elif t == Decimal:
        return QVariant(unicode(v))
    else:
        return QVariant(v)


def variantEq(value1, value2):
    return (value1.isNull() and value2.isNull()) or (value1 == value2)


def forceBool(val):
    if isinstance(val, QVariant):
        return val.toBool()
    return bool(val)


def forceDate(val):
    if isinstance(val, QVariant):
        return val.toDate()
    if isinstance(val, QDate):
        return val
    if isinstance(val, QDateTime):
        return val.date()
    if val is None:
        return QDate()
    return QDate(val)


def forceTime(val):
    if isinstance(val, QVariant):
        return val.toTime()
    if isinstance(val, QTime):
        return val
    if isinstance(val, QDateTime):
        return val.time()
    if val is None:
        return QTime()
    return QTime(val)


def forceDateTime(val):
    if isinstance(val, QVariant):
        return val.toDateTime()
    if isinstance(val, QDateTime):
        return val
    if isinstance(val, QDate):
        return QDateTime(val, QTime())
    if isinstance(val, QTime):
        return QDateTime(QDate(), val)
    if val is None:
        return QDateTime()
    return QDateTime(val)


def forceDateTuple(val):
    u"""
    Раньше использовалось, потому что так понимал SOAP. Предполагается, что новый формат SOAP 
    тоже будет нормально понимать. Собственно, теперь возвращает не tuple и надо будет починить попозже имя
    :type val: PyQt4.QtCore.QVariant
    :rtype: str
    """
    dt = forceDateTime(val)
    if dt == QDateTime():
        return None
    # d = dt.date()
    # t = dt.time()
    # return d.year(), d.month(), d.day(), t.hour(), t.minute(), t.second(), 0
    result = str(dt.toString('yyyy-MM-ddThh:mm:ss'))
    return result if result else None


def forceInt(val):
    if isinstance(val, QVariant):
        return val.toInt()[0]
    elif ((val is None) # Если пустое значение
          or (isinstance(val, QString) and not val.toInt()[1]) # Если нечисловой QString
          or isinstance(val, basestring) and not val.isdigit()): # Если нечисловая строка
        return 0
    return int(val)


def forceLong(val):
    if isinstance(val, QVariant):
        return val.toLongLong()[0]
    elif val is None:
        return 0L
    return long(val)


def forceRef(val):
    if isinstance(val, QVariant):
        if val.isNull():
            val = None
        else:
            val = int(val.toULongLong()[0])
            if val == 0:
                val = None
    return val


def forceString(val):
    if isinstance(val, QVariant):
        valType = val.type()
        if  valType == QVariant.Date:
            return formatDate(val.toDate())
        elif valType == QVariant.DateTime:
            return formatDateTime(val.toDateTime())
        elif valType == QVariant.Time:
            return formatTime(val.toTime())
        else:
            val = val.toString()
    if isinstance(val, QDate):
        return formatDate(val)
    if isinstance(val, QDateTime):
        return formatDateTime(val)
    if isinstance(val, QTime):
        return formatTime(val)
    if val is None:
        return u''
    if isinstance(val, QStringRef):
        val = val.toString()
    return unicode(val)


def forceStringEx(val):
    return forceString(val).strip()


def forceDouble(val):
    if isinstance(val, QVariant):
        return val.toDouble()[0]
    elif not val:
        return float(0)
    else:
        return float(val)


def forceDecimal(val):
    if isinstance(val, QVariant):
        res = unicode(val.toString())
        return Decimal(res) if res != u'' else Decimal(0)
    elif not val:
        return Decimal('0.0')
    elif isinstance(val, float):
        return Decimal(unicode(val))
    else:
        return Decimal(val)


def forceMoneyRepr(val):
    return u"%.2f" % forceDouble(val)


def forcePrettyDouble(val, digits=2):
    return round(forceDouble(val), digits)


def formatBool(val):
    if forceBool(val):
        return u'да'
    else:
        return u'нет'


def pyDate(date):
    if date and date.isValid():
        return date.toPyDate()
    else:
        return datetime.date(datetime.MINYEAR, 1, 1)


def pyTime(time):
    if time and time.isValid():
        return time.toPyTime()
    else:
        return datetime.time()


def pyDateTime(dateTime):
    if dateTime and dateTime.isValid():
        if isinstance(dateTime, QDate):
            dateTime = QtCore.QDateTime(dateTime)
        return dateTime.toPyDateTime()
    else:
        return datetime.datetime(datetime.MINYEAR, 1, 1)


def forceTr(text, context = 'AllOccurrence', disambiguation = None):
    # TODO:skkachaev: Происходит какая-то дичь, если мы пытаемся это вызвать не из виста-меда.
    # Падает где-то внутри translate, нам возвращается TypeError. Есть предположение,
    # что это потому что не инициализированны контексты. Надо бы придумать, как это сделать
    try:
        return forceString(QCoreApplication.translate(context, text, disambiguation))
    except TypeError as e:
        return text


def formatDate(val, toString = True):
    """
        Производит конвертацию даты из QDate в строку (при toString = True) или строку в QDate

    :param val: дата.
    :type val: QDate, QVariant, QString
    :param toString: указывает на направление конвертирования: True - из QDate в строку (по умол.), False - из строки в QDate)
    :return: дату в новом формате.
    :rtype: unicode или QDate
    """
    formatString = 'dd.MM.yyyy'
    if toString:
        if isinstance(val, QVariant):
            val = val.toDate()
        return unicode(val.toString(formatString))
    else:
        if isinstance(val, QVariant):
            val = val.toString()
        return QDate.fromString(val, formatString)


def formatTime(val):
    if isinstance(val, QVariant):
        val = val.toDate()
    return unicode(val.toString('H:mm'))


def formatDateTime(val):
    if isinstance(val, QVariant):
        val = val.toDateTime()
    return unicode(val.toString('dd.MM.yyyy H:mm'))


def formatNameInt(lastName, firstName, patrName):
    return trim(lastName+' '+firstName+' '+patrName)


def formatName(lastName, firstName, patrName):
    lastName  = nameCase(forceStringEx(lastName))
    firstName = nameCase(forceStringEx(firstName))
    patrName  = nameCase(forceStringEx(patrName))
    return formatNameInt(lastName, firstName, patrName)


def formatShortNameInt(lastName, firstName, patrName):
    return trim(lastName + ' ' +((firstName[:1]+'.') if firstName else '') + ((patrName[:1]+'.') if patrName else ''))


def formatShortName(lastName, firstName, patrName):
    lastName  = nameCase(forceStringEx(lastName))
    firstName = nameCase(forceStringEx(firstName))
    patrName  = nameCase(forceStringEx(patrName))
    return formatShortNameInt(lastName, firstName, patrName)


def formatSex(sex):
    sex = forceInt(sex)
    if sex == 1:
        return u'М'
    elif sex == 2:
        return u'Ж'
    else:
        return u''


def databaseFormatSex(sex):
    sex = forceString(sex).upper()
    if sex == u'М':
        return 1
    elif sex == u'Ж':
        return 2
    else:
        return None


def formatSNILS(SNILS):
    if SNILS:
        s = forceString(SNILS)+' '*14
        return s[0:3]+'-'+s[3:6]+'-'+s[6:9]+' '+s[9:11]
    else:
        return u''


def unformatSNILS(SNILS):
    return forceString(SNILS).replace('-', '').replace(' ', '')


def calcSNILSCheckCode(SNILS):
    result = 0
    for i in xrange(9):
        result += (9-i)*int(SNILS[i])
    result = result % 101
    if result == 100:
        result = 0
    return '%02.2d' % result


def checkSNILS(SNILS):
    raw = unformatSNILS(SNILS)
    if len(raw) == 11:
        return raw[:9]<='001001998' or raw[-2:] == calcSNILSCheckCode(raw)
    return False


def fixSNILS(SNILS):
    raw = unformatSNILS(SNILS)
    return (raw+'0'*11)[:9] + calcSNILSCheckCode(raw)


def calcENPCheckCode(ENP):
    def digits_of(n):
        return [int(digit) for digit in str(n)]
    digits = digits_of(str(ENP)[:-1])
    even_digits = digits[-2::-2]
    odd_digits = digits[-1::-2]
    checksum = sum(even_digits) + sum([sum(digits_of(d * 2)) for d in odd_digits])
    return -checksum % 10


def checkENP(ENP):
    return len(str(ENP)) == 16 and calcENPCheckCode(ENP) == int(str(ENP)[-1])


def fixENP(ENP):
    return str(ENP)[:-1] + str(calcENPCheckCode(ENP))


def agreeNumberAndWord(num, words):
    u"""
        Согласовать число и слово:
        num - число, слово = (один, два, много)
        agreeNumberAndWord(12, (u'год', u'года', u'лет'))
    """
    if num<0: num = -num
    if (num/10)%10 != 1:
        if num%10 == 1 :
            return words[0]
        elif 1 < num%10 < 5 :
            return words[1]
    return words[-1]


def formatNum(num, words):
    return u'%d %s' % (num, agreeNumberAndWord(num,words))


def formatNum1(num, words):
    if num == 1:
        return agreeNumberAndWord(num,words)
    else:
        return u'%d %s' % (num, agreeNumberAndWord(num,words))


def formatYears(years):
    return '%d %s' % (years, agreeNumberAndWord(years, (u'год', u'года', u'лет')))


def formatMonths(months):
    return '%d %s' % (months, agreeNumberAndWord(months, (u'месяц', u'месяца', u'месяцев')))


def formatWeeks(weeks):
    return '%d %s' % (weeks, agreeNumberAndWord(weeks, (u'неделя', u'недели', u'недель')))


def formatDays(days):
    return '%d %s' % (days, agreeNumberAndWord(days, (u'день', u'дня', u'дней')))


def formatYearsMonths(years, months):
    if years == 0:
        return formatMonths(months)
    elif months == 0:
        return formatYears(years)
    else:
        return formatYears(years) + ' ' + formatMonths(months)


def formatMonthsWeeks(months, weeks):
    if  months == 0:
        return formatWeeks(weeks)
    elif weeks == 0:
        return formatMonths(months)
    else:
        return formatMonths(months) + ' ' + formatWeeks(weeks)


def formatRecordsCountInt(count):
    return '%d %s' % (count, agreeNumberAndWord(count, (u'запись', u'записи', u'записей')))


def formatRecordsCount(count):
    if count:
        return u'в списке '+formatRecordsCountInt(count)
    else:
        return u'список пуст'


def formatRecordsCount2(count, totalCount):
    if count and totalCount and count<totalCount:
        return formatRecordsCount(totalCount)+ u', показаны первые '+formatRecordsCountInt(count)
    else:
        return formatRecordsCount(count)


def formatList(someList):
    if len(someList)>2:
        return u' и '.join([', '.join(someList[:-1]), someList[-1]])
    else:
        return u' и '.join(someList)


def splitText(text, widths):
    result = []
    if not text:
        return result

    width = widths[0]

    lines = text.splitlines()
    count = 0

    for line in lines:
        p = 0
        l = len(line)
        while p<l:
            while line[p:p+1].isspace():
                p += 1
            s = p + width
            if s>=l:
                breakpos = s
            else:
                breakpos = line.rfind(' ', p, s+1)
            if breakpos<0:
                breakpos = max([line.rfind(sep, p, s) for sep in '-,.;:!?)]}\\|/'])
                if breakpos>= 0 :
                    breakpos+=1
            if breakpos<0:
                breakpos = s
            result.append(line[p:breakpos])
            p = breakpos
            count += 1
            width = widths[count if count<len(widths) else -1]
    return result


def foldText(text, widths):
    return '\n'.join(splitText(text, widths))


def calcAgeInDays(birthDay, today):
    assert isinstance(birthDay, QDate)
    assert isinstance(today, QDate)
    return birthDay.daysTo(today)


def calcAgeInMonths(birthDay, today):
    assert isinstance(birthDay, QDate)
    assert isinstance(today, QDate)

    bYear  = birthDay.year()
    bMonth = birthDay.month()
    bDay   = birthDay.day()

    tYear  = today.year()
    tMonth = today.month()
    tDay   = today.day()

    result = (tYear-bYear)*12+(tMonth-bMonth)
    if bDay > tDay:
        result -= 1
    return result


def calcAgeInYears(birthDay, today):
    assert isinstance(birthDay, QDate)
    assert isinstance(today, QDate)

    bYear  = birthDay.year()
    bMonth = birthDay.month()
    bDay   = birthDay.day()

    tYear  = today.year()
    tMonth = today.month()
    tDay   = today.day()

    result = tYear-bYear
    if bMonth>tMonth or (bMonth == tMonth and bDay > tDay):
        result -= 1
    return result


def calcAgeTuple(birthDay, today):
    if not today or today.isNull():
        today = QDate.currentDate()
    elif isinstance(today, QDateTime):
        today = today.date()
    d = calcAgeInDays(birthDay, today)
    if d >= 0:
        return CAgeTuple( (d,
                d/7,
                calcAgeInMonths(birthDay, today),
                calcAgeInYears(birthDay, today)
               ), birthDay, today)
    else:
        return None


def formatAgeTuple(ageTuple, bd, td):
    if not ageTuple:
        return u'ещё не родился'
    (days, weeks, months, years) = ageTuple
    if years>=7:
        return formatYears(years)
    elif years>=1:
        return formatYearsMonths(years, months-12*years)
    elif months>=1:
        if not td:
            td = QDate.currentDate()
        return formatMonthsWeeks(months, bd.addMonths(months).daysTo(td)/7)
    else:
        return formatDays(days)


def calcAge(birthDay, today=None):
    bd = forceDate(birthDay)
    td = forceDate(today) if today else QDate.currentDate()
    ageTuple = calcAgeTuple(bd, td)
    return formatAgeTuple(ageTuple, bd, td)


def firstWeekDay(date):
    date = forceDate(date)
    return date.addDays(1 - date.dayOfWeek())


def lastWeekDay(date):
    date = forceDate(date)
    return date.addDays(7 - date.dayOfWeek())


def firstMonthDay(date):
    date = forceDate(date)
    return QDate(date.year(), date.month(), 1)


def lastMonthDay(date):
    date = forceDate(date)
    return QDate(date.year(), date.month(), date.daysInMonth())


def lastQuarterDay(date):
    return firstQuarterDay(date).addMonths(3).addDays(-1)


def firstQuarterDay(date):
    date = forceDate(date)
    return QDate(date.year(),
                 ((date.month() - 1) / 3) * 3 + 1,
                 1)


def firstHalfYearDay(date):
    date = forceDate(date)
    month = 1 if date.month() < 7 else 7
    return QDate(date.year(), month, 1)


def lastHalfYearDay(date):
    date = forceDate(date)
    month = 6 if date.month() < 7 else 12
    return QDate(date.year(), month, 30 if month == 6 else 31)


def firstYearDay(date):
    date = forceDate(date)
    return QDate(date.year(), 1, 1)


def lastYearDay(date):
    date = forceDate(date)
    return QDate(date.year(), 12, 31)


def _determineMondayAndWorkDaysCount2(date, weekdays=5):
    date = forceDate(date)
    doy = date.dayOfWeek()
    monday = date.addDays(-doy+Qt.Monday)
    if weekdays == 7:
        workDaysCount = doy
        doyIsRed = False
    elif weekdays == 6:
        workDaysCount = doy if doy<Qt.Sunday else Qt.Friday
        doyIsRed = doy == Qt.Sunday
    else:
        workDaysCount = doy if doy<Qt.Saturday else Qt.Friday
        doyIsRed = doy in [Qt.Saturday, Qt.Sunday]
    return monday, workDaysCount, doyIsRed


def getPeriodLength(startDate, stopDate, countRedDays, weekdays=5):
    from calendar import CCalendarWorkdaysGetter
    # определение длительности периода в днях (включая или исключая выходные)
    # учитывается и начальная и конечная дата
    # необходимо доделать для работы с праздничными днямиC
    if startDate > stopDate:
        return 0
    if countRedDays or weekdays == 7:
        return startDate.daysTo(stopDate)+1
    else:
        if isinstance(startDate, QDateTime):
            startDate = startDate.date()
        if isinstance(stopDate, QDateTime):
            stopDate = stopDate.date()

        if weekdays == 5:
            calWorkdaysGetter = CCalendarWorkdaysGetter(True, True)
        elif weekdays == 6:
            calWorkdaysGetter = CCalendarWorkdaysGetter(False, True)
        elif weekdays == 7:
            calWorkdaysGetter = CCalendarWorkdaysGetter(False, False)
        else:
            raise Exception("Слишком много выходных дней. Жизнь нас к такому не подготовила :( ")

        return calWorkdaysGetter.getCountWorkdays(startDate, stopDate.addDays(1))


def addPeriod(startDate, length, countRedDays):
    # добавление к некоторой дате некоторого периода в днях (включая или исключая выходные)
    # длительность с учётом начальной и конечной даты
    if countRedDays:
        return startDate.addDays(length - 1)
    else:
        startMonday, startWDC = _determineMondayAndWorkDaysCount2(startDate)[:2]
        stopDate = startMonday.addDays((length - 1) * 7 // 5 + startWDC - 1)

        stopDate = stopDate.addDays(31)

        stmt = """
        SELECT 
            DATE_FORMAT(`date`,'2013-%%m-%%d'),
            DATEDIFF(DATE_FORMAT(`endDate`,'2013-%%m-%%d'), DATE_FORMAT(`date`,'2013-%%m-%%d'))
        FROM 
            `CalendarExceptions` 
        WHERE 
            DATE_FORMAT(`date`,'%%m-%%d')>= DATE_FORMAT('%s','%%m-%%d') 
            AND DATE_FORMAT(`date`,'%%m-%%d')<= DATE_FORMAT('%s','%%m-%%d')
        """ % (
            forceDate(startDate).toString(QtCore.Qt.ISODate),
            forceDate(stopDate).toString(QtCore.Qt.ISODate)
        )

        holidays = []
        db = QtGui.qApp.db
        query = db.query(stmt)
        if query.exec_():
            while query.next():
                holidays.append(forceDate(query.record().value(0)))
                dayCount = forceInt(query.record().value(1))
                for i in range(dayCount):
                    holidays.append(forceDate(query.record().value(0)).addDays(i + 1))

        stopDate = startDate
        uLen = length
        if ((stopDate not in holidays) and (stopDate.dayOfWeek() not in (Qt.Saturday, Qt.Sunday))):
            uLen -= 1

        while uLen > 0:
            stopDate = stopDate.addDays(1)
            if ((stopDate not in holidays) and (stopDate.dayOfWeek() not in (Qt.Saturday, Qt.Sunday))):
                uLen -= 1

        return stopDate

monthName =   ['', u'январь', u'февраль', u'март', u'апрель', u'май', u'июнь', u'июль', u'август', u'сентябрь', u'октябрь', u'ноябрь', u'декабрь']
monthNameGC = ['', u'января', u'февраля', u'марта', u'апреля', u'мая', u'июня', u'июля', u'августа', u'сентября', u'октября', u'ноября', u'декабря']


####################################################


def setBits(val, mask, bits):
    return ( val & ~mask ) | ( bits & mask )


def checkBits(val, mask, bits):
    return ( val & mask ) == ( bits & mask )


####################################################


def get_date(d):
    d=forceDate(d)
    if d and 1800<=d.year()<=2200:
        return d.toPyDate()
    else:
        return None


def getInfisCodes(KLADRCode, KLADRStreetCode, house, corpus):
    db = QtGui.qApp.db
    area = ''
    region = ''
    street = '*'
    streettype = ''
    npunkt = forceString(db.translate('kladr.KLADR', 'CODE', KLADRCode, 'NAME', idFieldName='CODE'))
    if KLADRCode[:2] == '78':
        OCATO=forceString(db.translate('kladr.STREET', 'CODE', KLADRStreetCode, 'OCATD'))
        if KLADRStreetCode and not OCATO:
            firstPart = house.split('/')[0]
            if re.match('^\d+$', firstPart):
                intHouse = int(firstPart)
            else:
                intHouse = None
            table = db.table('kladr.DOMA')
            cond=table['CODE'].like(KLADRStreetCode[:-2]+'%')
            housesList = db.getRecordList(table, 'CODE,NAME,KORP,OCATD', where=cond)
            for record in housesList:
                NAME=forceString(record.value('NAME'))
                KORP=forceString(record.value('KORP'))
                if checkHouse(NAME, KORP, house, intHouse, corpus):
                    OCATO = forceString(record.value('OCATD'))
                    break
        if OCATO:
            area = forceString(db.translate('kladr.OKATO', 'CODE', OCATO[:5], 'infis'))
        if KLADRCode!='7800000000000':
            region = forceString(db.translate(
                'kladr.KLADR', 'CODE', KLADRStreetCode[:-6]+'00', 'infis'))
            if region == u'СПб':
                region = area
        else:
            region = area
        street=forceString(db.translate('kladr.STREET', 'CODE', KLADRStreetCode, 'infis'))
        SOCR=forceString(db.translate('kladr.STREET', 'CODE', KLADRStreetCode, 'SOCR'))
        streettype=forceString(db.translate('kladr.SOCRBASE', 'SCNAME', SOCR, 'infisCODE'))
    elif KLADRCode[:2] == '47':
        KLADRArea   = KLADRCode[:2]+'0'*11
        KLADRRegion = KLADRCode[:5]+'0'*8
        area = forceString(db.translate('kladr.KLADR', 'CODE', KLADRArea, 'infis', idFieldName='CODE'))
        if KLADRArea != KLADRRegion:
            region = forceString(db.translate('kladr.KLADR', 'CODE', KLADRRegion, 'infis', idFieldName='CODE'))
        else:
            region = area
    else:
        KLADRArea   = KLADRCode[:2]+'0'*11
        area = forceString(db.translate('kladr.KLADR', 'CODE', KLADRArea, 'infis', idFieldName='CODE'))
        table = db.table('kladr.KLADR')
        region = area
        code = KLADRCode
        SOCR=forceString(db.translate('kladr.STREET', 'CODE', KLADRStreetCode, 'SOCR'))
        streettype=forceString(db.translate('kladr.SOCRBASE', 'SCNAME', SOCR, 'infisCODE'))
        while True:
            record = db.getRecordEx(table, 'parent, infis', table['CODE'].eq(code))
            if record:
                parent = forceString(record.value(0))
                infis  = forceString(record.value(1))
                if len(parent) <= 3 and infis:
                    region = infis
                    break
                else:
                    code = parent+'0'*(13-len(parent))
            else:
                break
    return area, region, npunkt, street, streettype


def checkHouse(rHouse, rCorpus, house, intHouse, corpus):
    for range in rHouse.split(','):
        if intHouse:
            simple = re.match('^(\d+)-(\d+)$', range)
            if simple:
                if int(simple.group(1)) <= intHouse <= int(simple.group(2)):
                    return True
                else:
                    continue
            if intHouse%2 == 0:
                even = re.match(u'^Ч\((\d+)-(\d+)\)$', range)
                if even:
                    if int(even.group(1)) <= intHouse <= int(even.group(2)):
                        return True
                    else:
                        continue
            else:
                odd = re.match(u'^Н\((\d+)-(\d+)\)$', range)
                if odd:
                    if int(odd.group(1)) <= intHouse <= int(odd.group(2)):
                        return True
                    else:
                        continue
        if house == range:
            return True
    return False



## Эмуляция перечисления QXmlStreamReader.ReadElementTextBehaviour для версии Qt ниже 4.6
class XmlReadElementTextBehaviour:
    ErrorOnUnexpectedElement = QXmlStreamReader.ErrorOnUnexpectedElement if hasattr(QXmlStreamReader, 'ErrorOnUnexpectedElement') else 0
    IncludeChildElements = QXmlStreamReader.IncludeChildElements if hasattr(QXmlStreamReader, 'IncludeChildElements') else 1
    SkipChildElements = QXmlStreamReader.SkipChildElements if hasattr(QXmlStreamReader, 'SkipChildElements') else 2


## Реализация метода readNextStartElement() класса QXmlStreamReader, который был добавлен в Qt 4.6 (у нас есть сборка с Qt 4.5)
# @param xmlReader: объект класса QXmlStreamReader, для которого применяется алгоритм. 
def readNextStartXMLElement(xmlReader):
    if not isinstance(xmlReader, QXmlStreamReader):
        return False
    
    if hasattr(xmlReader, 'readNextStartElement') and int(qVersion().split('.')[1]) >= 6:
        return xmlReader.readNextStartElement()
    
    #atronah: весь код ниже нагло скомунизден из исходников Qt 5.1.1
    while xmlReader.readNext() != QXmlStreamReader.Invalid:
        if xmlReader.isEndElement():
            return False
        elif xmlReader.isStartElement():
            return True
    
    return False


## Реализация метода skipCurrentElement() класса QXmlStreamReader, который был добавлен в Qt 4.6 (у нас есть сборка с Qt 4.5)
# @param xmlReader: объект класса QXmlStreamReader, для которого применяется алгоритм. 
def skipCurrentXMLElement(xmlReader):
    if not isinstance(xmlReader, QXmlStreamReader):
        return
    
    if hasattr(xmlReader, 'skipCurrentElement') and int(qVersion().split('.')[1]) >= 6:
        xmlReader.skipCurrentElement()
        return
    
    depth = 1
    while (depth and xmlReader.readNext() != QXmlStreamReader.Invalid):
        if xmlReader.isEndElement():
            depth -= 1
        elif xmlReader.isStartElement():
            depth += 1
    



## Реализация метода readElementText() класса QXmlStreamReader, который был добавлен в Qt 4.6 (у нас есть сборка с Qt 4.5)
# @param xmlReader: объект класса QXmlStreamReader, для которого применяется алгоритм. 
def readXMLElementText(xmlReader, behaviour = XmlReadElementTextBehaviour.ErrorOnUnexpectedElement):
    result = QString()
    if not isinstance(xmlReader, QXmlStreamReader):
        return result
    
    if hasattr(xmlReader, 'readElementText') and int(qVersion().split('.')[1]) >= 6:
        return xmlReader.readElementText(behaviour)
    
    if not xmlReader.isStartElement():
        return result
    
    while xmlReader.readNext():
        if xmlReader.tokenType() in [QXmlStreamReader.Characters,
                                     QXmlStreamReader.EntityReference]:
            result.insert(result.size(), xmlReader.text().toString())
        elif xmlReader.isEndElement():
            return result
        elif xmlReader.tokenType() in [QXmlStreamReader.ProcessingInstruction,
                                       QXmlStreamReader.Comment]:
            break
        elif xmlReader.isStartElement():
            if behaviour == XmlReadElementTextBehaviour.SkipChildElements:
                skipCurrentXMLElement(xmlReader)
                break
            elif behaviour == XmlReadElementTextBehaviour.IncludeChildElements:
                result.insert(result.size(), readXMLElementText(xmlReader))
            else:
                xmlReader.raiseError('Expected character data.')
                break
        
    return result
         

#Необычный порядок аргументов: dst, src (вместо src, dst)
def copyFields(newRecord, record, names = None):
    if names == None:
        copyAllFields(newRecord, record)
    else:
        copyFieldsByName(newRecord, record, names)

def copyAllFields(newRecord, record):
    for i in xrange(newRecord.count()):
        newRecord.setValue(i, record.value(newRecord.fieldName(i)))

def copyFieldsByName(newRecord, record, names):
    # nothing happens for nonexistent fields (see QSqlRecord API)
    for name in names:
        newRecord.setValue(name, record.value(name))


def setValues(record, **kwargs):
    """ Set values for a record, mapping 'toVariant' to each value."""
    for name, val in kwargs.iteritems():
        record.setValue(name, toVariant(val))


def quote(string, sep='\''):
    magicChars = { '\\' : '\\\\',
                   sep  : '\\'+sep,
#                   '\n' : '\\n',
#                   '\r' : '\\r',
#                   '\0' : '\x00'
                 }
    res = ''
    for c in string:
        res += magicChars.get(c, c)
    return sep + res + sep


## Сравнивает два стека
# @return: (common_elements, parent_flag)
# ,где common_elements - это количество первых одинаковых элементов обоих стеков
#     parent_flag - это флаг наследования, принимающий значение
#                    1, если функция левого стека является "родительской" для функции правого,
#                    0, если стеки относятся к несвязанным функциям,
#                    -1, если функция правого стека является "родительской" для функции левого
def compareCallStack(leftStack, rightStack, excludeLastCallFunctionName = None):
    fullEqualityNumber = 0 # количество первых полностью схожих элементов стеков 
    isInherit = 0
    
    if not (isinstance(leftStack, (list, tuple)) and isinstance(rightStack, (list, tuple))):
        return (fullEqualityNumber, isInherit)
    
    if not (leftStack and rightStack):
        return (fullEqualityNumber, isInherit)
    
    fileNameIdx = 0
    lineNumberIdx = 1
    callerIdx = 2
    calleesIdx = 3
    
    leftStackLength = len(leftStack)
    rightStackLength = len(rightStack)
    
    inheritanceDirection = 1
    if rightStackLength < leftStackLength:
        leftStackLength, rightStackLength = rightStackLength, leftStackLength
        leftStack, rightStack = rightStack, leftStack
        inheritanceDirection = -1
        
# В сборке имя вызываемой функции всегда NoneType    
#    if (excludeLastCallFunctionName
#        and leftStack
#        and excludeLastCallFunctionName in leftStack[-1][calleesIdx]):
    if excludeLastCallFunctionName:
        leftStackLength -= 1
    
    for stackIdx in xrange(leftStackLength):
        isFileNameEquality = leftStack[stackIdx][fileNameIdx] == rightStack[stackIdx][fileNameIdx]
        if (isFileNameEquality
            and leftStack[stackIdx][lineNumberIdx] == rightStack[stackIdx][lineNumberIdx]
            and leftStack[stackIdx][callerIdx] == rightStack[stackIdx][callerIdx]
            and leftStack[stackIdx][calleesIdx] == rightStack[stackIdx][calleesIdx]):
            fullEqualityNumber += 1
        else:
            break
    
    isInherit = inheritanceDirection * (1 if fullEqualityNumber in [leftStackLength, # та же функция
                                                                    leftStackLength - 1] # вложенная функция\
                                        else 0)  
    
    return (fullEqualityNumber, isInherit)


def MKBwithoutSubclassification(mkb):
    mkb = (mkb[:5]).strip()
    if mkb.endswith('.'):
        mkb = mkb[:-1]
    return mkb


def getActionTypeIdListByFlatCode(flatCode):
    db = QtGui.qApp.db
    tableActionType = db.table('ActionType')
    cond =[tableActionType['flatCode'].like(flatCode),
           tableActionType['deleted'].eq(0)
          ]
    return db.getIdList(tableActionType, 'id', cond)


def getMKB():
    return '''(SELECT Diagnosis.MKB
FROM Diagnosis INNER JOIN Diagnostic ON Diagnostic.diagnosis_id=Diagnosis.id
INNER JOIN rbDiagnosisType ON Diagnostic.diagnosisType_id=rbDiagnosisType.id
WHERE Diagnostic.event_id = Event.id AND Diagnosis.deleted = 0 AND Diagnostic.deleted = 0
AND (rbDiagnosisType.code = '1'
OR (rbDiagnosisType.code = '2' AND Diagnostic.person_id = Event.execPerson_id
AND (NOT EXISTS (SELECT DC.id FROM Diagnostic AS DC
INNER JOIN rbDiagnosisType AS DT ON DT.id = DC.diagnosisType_id WHERE DT.code = '1'
AND DC.event_id = Event.id
)))) LIMIT 1) AS MKB'''

def getProvisionalDiagnosis():
    return '''(SELECT Diagnosis.MKB
FROM Diagnosis INNER JOIN Diagnostic ON Diagnostic.diagnosis_id=Diagnosis.id
INNER JOIN rbDiagnosisType ON Diagnostic.diagnosisType_id=rbDiagnosisType.id
WHERE Diagnostic.event_id = Event.id AND Diagnosis.deleted = 0 AND Diagnostic.deleted = 0
AND rbDiagnosisType.code = '7'
LIMIT 1) AS provisionalDiagnosis'''

def getAdmissionDiagnosis():
    return u'''(SELECT APS.value
FROM ActionProperty AP INNER JOIN ActionProperty_String APS ON APS.id = AP.id
WHERE AP.action_id = Action.id
    AND AP.type_id = (SELECT APT.id FROM ActionPropertyType APT
                         INNER JOIN ActionType AT ON AT.id = APT.actionType_id
                             AND AT.flatCode = 'received' AND AT.deleted = 0 AND APT.deleted = 0
                             AND APT.name = 'Диагноз приемного отделения')
LIMIT 1) AS admissionDiagnosis'''


def getDataOSHB():
    return '''(SELECT CONCAT_WS('  ', OSHB.code, OSHB.name, IF(OSHB.sex=1, \'%s\', IF(OSHB.sex=2, \'%s\', ' ')))
FROM ActionPropertyType AS APT
INNER JOIN ActionProperty AS AP ON AP.type_id=APT.id
INNER JOIN ActionProperty_HospitalBed AS APHB ON APHB.id=AP.id
INNER JOIN OrgStructure_HospitalBed AS OSHB ON OSHB.id=APHB.value
WHERE APT.actionType_id=Action.actionType_id AND AP.action_id=Action.id AND AP.deleted=0 AND APT.deleted=0 AND APT.typeName LIKE 'HospitalBed' LIMIT 1) AS bedCodeName'''%(forceString(u''' /М'''), forceString(u''' /Ж'''))

def getDataOSHBProfile():
    return '''(SELECT HBP.name
FROM ActionPropertyType AS APT
INNER JOIN ActionProperty AS AP ON AP.type_id=APT.id
INNER JOIN ActionProperty_HospitalBed AS APHB ON APHB.id=AP.id
INNER JOIN OrgStructure_HospitalBed AS OSHB ON OSHB.id=APHB.value
INNER JOIN rbHospitalBedProfile AS HBP ON HBP.id = OSHB.profile_id
WHERE APT.actionType_id=Action.actionType_id AND AP.action_id=Action.id AND AP.deleted=0 AND APT.deleted=0 AND APT.typeName LIKE 'HospitalBed' LIMIT 1) AS bedProfile'''
    


## Получение первой лексемы, т.е. группы однотипных символов (либо только числа, либо только не числа)
# @param sourceString: исходная строка для поиска
# @return: (lexeme, isDigit, stumpString)
def getFirstLexeme(sourceString):
    isDigit = False
    lexeme = u''
    if sourceString:
        isDigit = sourceString[0].isdigit()
    for symbol in sourceString:
        # если тип очередного символа строки отличается от типа первого символа
        if symbol.isdigit() ^ isDigit:
            break #прервать формирование токена
        lexeme += symbol
    return lexeme, isDigit, sourceString[len(lexeme):]


## Сравнивает строки путем естественного сравнения ('text1' < 'text2' < 'text11'), 
# вместо лексографического ('text1' < 'text11' < 'text2'), выполняемого стандартными методами сранения.
# @param leftString: левый аргумент сравнения в виде строки (basestring или QString)
# @param rightString: правый аргумент сравнения в виде строки (basestring или QString)
# @return отрицательное число, если leftString < rightString, 
#         ноль, если leftString = rightString, 
#         положительное, если leftString > rightString
def naturalStringCompare(leftString, rightString):
    leftString, rightString = forceString(leftString), forceString(rightString)
    
    if leftString == rightString:
        return 0
    
    while True:
        leftLexeme, leftIsDigit, leftString = getFirstLexeme(leftString)
        rightLexeme, rightIsDigit, rightString = getFirstLexeme(rightString)

        
        if leftIsDigit != rightIsDigit or not (leftLexeme and rightLexeme):
            return cmp(leftLexeme, rightLexeme)
        
        # сравниваем блоки, как числа, если они состоят из чисел, иначе, как строки
        partCompareResult = cmp(forceInt(leftLexeme), forceInt(rightLexeme)) \
                            if leftIsDigit \
                            else cmp(leftLexeme, rightLexeme)
        
        # если лексемы не равны, то считаем, что нашли результат, иначе пляшем дальше
        if partCompareResult:
            return partCompareResult
        
    
        
##################################################################################
    
def timeRangeColorParser(rawString):
    timeRanges = rawString.split(';')
    results = {}
    for timeRangeDescr in timeRanges:
        timeRangeDescr = timeRangeDescr.strip()
        tmp = timeRangeDescr.split(':')
        if len(tmp) != 2:
            continue
        timeRange, color = tmp
        times = timeRange.split('-')
        if len(times) != 2:
            continue
        timeLow, timeHigh = times
        try:
            timeLow = int(timeLow)
            timeHigh = int(timeHigh)
        except ValueError:
            continue
        color = QtGui.QColor(color)
        if not color.isValid():
            continue
        results[(timeLow, timeHigh)] = color
    return results


def splitShellCommand(command):
    """
    Разбивает команду на запускаемую утилиту и параметры запуска.

    :param command: обрабатываемая команда.
    :return: кортеж (string, list of string) из 2 элементов (путь_к_запускаемой_программе, список_аргументов)
    """

    # if not command:
    #     return command, []
    command = command.strip()


    parts = []
    while command:
        part, _, command = command.partition(' ') if command[0] not in ['"', "'"] \
                                                     else command[1:].partition(command[0])
        parts.append(part)
        command = command.strip()

    if parts:
        return parts.pop(0), parts

    return '', []


def clientQueueLog(status, msg, logDir=os.path.join(unicode(QDir.toNativeSeparators(QDir.homePath())), '.vista-med')):
    try:
        from buildInfo import lastChangedRev, lastChangedDate
    except:
        lastChangedRev = 'unknown'
        lastChangedDate = 'unknown'
    if not os.path.exists(logDir):
        os.makedirs(logDir)
    logFile = os.path.join(logDir, 'clientQueueLog.log')
    timeString = unicode(QDateTime.currentDateTime().toString(Qt.SystemLocaleDate))

    logString = u'[R%s|%s] Статус: %s %s\t(user_id=%s, python: %s; Qt: %s)\n' % (
        lastChangedRev,
        timeString,
        status,
        u'| Сообщение: ' + msg if msg else u'',
        QtGui.qApp.userId,
        sys.version,
        QtCore.qVersion()
    )
    file = codecs.open(logFile, mode='a', encoding=locale.getpreferredencoding())
    file.write(logString)
    file.close()


def log(logDir, title, message, stack=None, fileName='error.log'):
    try:
        try:
            from buildInfo import lastChangedRev, lastChangedDate
        except:
            lastChangedRev  = 'unknown'
            lastChangedDate = 'unknown'
        if not os.path.exists(logDir):
            os.makedirs(logDir)
        logFile = os.path.join(logDir, fileName)
        timeString = unicode(QDateTime.currentDateTime().toString(Qt.SystemLocaleDate))
        logString = u'%s\nRevision: %s\n(python: %s)\n(Qt: %s)\n%s: %s\n(%s)\n' % ('='*72,
                                                                lastChangedRev,
                                                                sys.version,
                                                                QtCore.qVersion(),
                                                                timeString,
                                                                title,
                                                                message)
        if stack:
            try:
                logString += ''.join(traceback.format_list(stack)).decode('utf-8') + '\n'
            except:
                logString += 'stack lost\n'
        file = codecs.open(logFile, mode='a', encoding=locale.getpreferredencoding())
        file.write(logString)
        file.close()
    except:
        pass


def logException(logDir, exceptionType, exceptionValue, exceptionTraceback):
    title = repr(exceptionType)
    message = unicode(exceptionValue)
    log(logDir, title, message, traceback.extract_tb(exceptionTraceback))
    sys.__excepthook__(exceptionType, exceptionValue, exceptionTraceback)


# описание рабочих дней для разных вариантов работы
wpFiveDays = (0, 1, 2, 3, 4, 5, 5, 5) # пятидневка
wpSixDays  = (0, 1, 2, 3, 4, 5, 6, 6) # шестидневка
wpSevenDays= (0, 1, 2, 3, 4, 5, 6, 7) # полная неделя

def _determineMondayAndWorkDaysCount(date, weekProfile):
    # date: QDate
    # weekProfile: список или кортеж из 8 значений, нулевое - нуль,
    # weekProfile[doy] - количество предшествующих рабочих дней включая день doy
    # соглажение Qt: понедельник - doy == 1, воскресение - doy == 7
    doy = date.dayOfWeek()
    monday = date.addDays(Qt.Monday-doy)
    workDaysCount = weekProfile[doy]
    return monday, workDaysCount, workDaysCount == weekProfile[doy-1]

def countWorkDays(startDate, stopDate, weekProfile):
    # определение количества рабочих дней в заданном отрезке дат
    # учитывается и начальная и конечная дата
    # weekProfile: список или кортеж из 8 значений, нулевое - нуль,
    # weekProfile[doy] - количество  предшествующих рабочих дней включая день doy
    # соглажение Qt: понедельник - doy == 1, воскресение - doy == 7
    # возможно, что необходимо доделать для работы с праздничными днями
    if weekProfile is wpSevenDays:
        return startDate.daysTo(stopDate)+1
    else:
        startMonday, startWDC, startIsRed = _determineMondayAndWorkDaysCount(startDate, weekProfile)
        stopMonday, stopWDC, stopIsRed = _determineMondayAndWorkDaysCount(stopDate, weekProfile)
        return startMonday.daysTo(stopMonday)*weekProfile[-1]//7+stopWDC-startWDC+(0 if startIsRed else 1)


def getWeekProfile(index):
    return {0: wpSevenDays, 1: wpSixDays, 2: wpFiveDays}.get(index, wpSevenDays)


def getActionTypeIdListByMKB(MKB):
    db = QtGui.qApp.db
    tblActionType = db.table('ActionType')
    tblActionTypeService = db.table('ActionType_Service')
    tblRbService = db.table('rbService')
    tblRbServiceMKB = db.table('rbService_MKB')

    qTable = tblActionType.innerJoin(tblActionTypeService, tblActionType['id'].eq(tblActionTypeService['master_id']))
    qTable = qTable.innerJoin(tblRbService, tblActionTypeService['service_id'].eq(tblRbService['id']))
    qTable = qTable.innerJoin(tblRbServiceMKB, tblRbService['id'].eq(tblRbServiceMKB['master_id']))

    cond = [
        tblRbServiceMKB['mkb'].eq(MKB),
        tblActionType['deleted'].eq(0)
    ]

    return db.getDistinctIdList(qTable, tblActionType['id'].name(), where=cond)


def getClassName(obj, isFull = True):
    parts = [obj.__module__] if isFull else []
    parts.append(obj.__class__.__name__)
    return '.'.join(parts)


def argMin(lst, key=lambda x: x):
    """
    :param lst: list of values
    :param key: функция
    :return: value x from lst such that key(x) = min([key(l) for l in lst]); None if lst is empty
    If key attains minimum value on multiple elements of lst, first one is returned
    """
    return reduce(lambda x, y: x if key(x) <= key(y) else y, lst) if lst else None


#############################################################################

class CLogHandler(QtCore.QObject):
    logged = QtCore.pyqtSignal(QtCore.QString)

    def __init__(self, logger, parent=None):
        super(CLogHandler, self).__init__(parent)
        self._logBuffer = QtCore.QBuffer()
        self._logBuffer.open(self._logBuffer.ReadWrite)
        self._logBuffer.bytesWritten.connect(self.onLogReceived)
        self._logHandler = logging.StreamHandler(self._logBuffer)
        self._logFormatter = logging.Formatter(u'%(levelname)-8s [%(asctime)s]  %(message)s')
        self._logHandler.setFormatter(self._logFormatter)
        logger.addHandler(self._logHandler)


    def setLevel(self, level):
        self._logHandler.setLevel(level)


    def setFormat(self, newFormat):
        if isinstance(newFormat, basestring):
            newFormat = logging.Formatter(newFormat)
        if isinstance(newFormat, logging.Formatter):
            self._logFormatter = newFormat
            self._logHandler.setFormatter(newFormat)


    @QtCore.pyqtSlot(int)
    def onLogReceived(self, length):
        self._logBuffer.seek(self._logBuffer.pos() - length)
        self.logged.emit(QtCore.QString(self._logBuffer.read(length).decode('utf-8')))


class MQSingleton(pyqtWrapperType):
    def __init__(cls, name, bases, dct):
        super(MQSingleton, cls).__init__(name, bases, dct)
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super(MQSingleton, cls).__call__(*args, **kw)
        return cls.instance


class CCustomContextMenuManager(QObject):
    def __init__(self, parent = None):
        QObject.__init__(self, parent)
        self.customContextMenuActions = []
        self.widget = None
        
    def configureWidget(self, widget):
        if isinstance(widget, QtGui.QWidget):
            self.widget = widget            
            widget.setContextMenuPolicy(Qt.CustomContextMenu)
            widget.connect(widget, SIGNAL('customContextMenuRequested(QPoint)'), self.showContextMenu)
    
    def addActionToPopup(self, action):
        if isinstance(action, QtGui.QAction):
            self.customContextMenuActions.append(action)
    
    @QtCore.pyqtSlot(QPoint)
    def showContextMenu(self, point):
        if self.widget:
            menu = self.widget.createStandardContextMenu()
            menu.setAttribute(Qt.WA_DeleteOnClose)
            menu.addSeparator()
            for action in self.customContextMenuActions:
                    menu.addAction(action)
            menu.exec_(self.widget.mapToGlobal(point))


class CClickSignalAdder(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonRelease:
            obj.emit(SIGNAL('clicked()'))
            return True
        return False


class CIncremetalFilterHelper(QObject):
    filterApplied = QtCore.pyqtSignal()

    def __init__(self, parent = None):
        super(CIncremetalFilterHelper, self).__init__(parent)
        self._applyFilterTimer = QtCore.QTimer(self)
        self._applyFilterTimer.setSingleShot(True)
        self._applyFilterTimer.timeout.connect(self.filterApplied)

    @QtCore.pyqtSlot(int)
    def filteredStringChanged(self, filteringString):
        self._applyFilterTimer.stop()
        idleTimeout = forceInt(QtGui.qApp.preferences.appPrefs.get('completerReduceIdleTimeout', 3))
        self._applyFilterTimer.start(idleTimeout * 1000)


class CAgeTuple(tuple):
    def __new__(cls, values, birthDate, checkDate):
        return tuple.__new__(cls, tuple(values))

    def __init__(self, values, birthDate, checkDate):
        tuple.__init__(self)
        self.birthDate = birthDate
        self.checkDate = checkDate


class TableColIndex(object):
    def __init__(self):
        self.__idx = 0

    def addColumn(self, col):
        assert col not in self.__dict__
        self.__dict__[col] = self.__idx
        self.__idx += 1

    def addColumns(self, cols):
        for col in cols:
            self.addColumn(col)

    def __len__(self):
        return self.__idx

class TableRecord(object):
    def __init__(self, cols, functions):
        self._cols = dict(zip(cols, functions))
        self._record = {}

    def extractFields(self, record):
        for col, f in self._cols.iteritems():
            self._record[col] = f(record.value(col))
        return self._record

    def __getitem__(self, arg):
        return self._record[arg]

    def __setitem__(self, key, val):
        self._record[key] = val


class AnyRequest(urllib2.Request):
    def __init__(self, *args, **kwargs):
        if 'method' in kwargs:
            self._method = kwargs['method']
            del kwargs['method']
        else:
            self._method = None
        urllib2.Request.__init__(self, *args, **kwargs)

    def get_method(self):
        if self._method is not None:
            return self._method
        return urllib2.Request.get_method(self)


class CQuotaColQuery:
    QUOTA_COL = u'''
    (
        SELECT DISTINCT
          QuotaType.code
        FROM
          Action a
          INNER JOIN Event e
            ON ((a.`event_id` = e.`id`)
            AND (e.`deleted` = 0))
          INNER JOIN EventType
            ON e.`eventType_id` = EventType.`id`
          INNER JOIN ActionType
            ON ActionType.`id` = a.`actionType_id`
          LEFT JOIN ActionPropertyType
            ON ActionPropertyType.`actionType_id` = ActionType.`id`
          LEFT JOIN ActionProperty
            ON ((ActionProperty.`type_id` = ActionPropertyType.`id`)
            AND (ActionProperty.`action_id` = a.`id`)
            AND (((ActionProperty.`deleted` = 0)
            OR (ActionProperty.`id` IS NULL))))
          LEFT JOIN ActionProperty_Client_Quoting
            ON ActionProperty_Client_Quoting.`id` = ActionProperty.`id`
          LEFT JOIN Client_Quoting
            ON Client_Quoting.`id` = ActionProperty_Client_Quoting.`value`
          LEFT JOIN QuotaType
            ON QuotaType.`id` = Client_Quoting.`quotaType_id`
          WHERE
              a.id = Action.id
              AND QuotaType.code IS NOT NULL
    ) AS quotaCode
    '''


def forceUnicode(val):
    if val is None:
        return u''

    try:
        decoded = unicode(val)
    except UnicodeDecodeError:
        decoded = str(val).decode('utf-8', 'replace')

    return decoded


def fromDateTimeTuple(dateTuple):
    y, m, d, h, mi, s = dateTuple[:6]
    return QtCore.QDateTime(QtCore.QDate(y, m, d), QtCore.QTime(h, mi, s))


def toDateTimeTuple(dateValue):
    dt = forceDateTime(dateValue)
    d, t = dt.date(), dt.time()
    return d.year(), d.month(), d.day(), t.hour(), t.minute(), t.second(), t.msec()


def getEventProfileForService(service, date, spec=None, birthDate=None, sex=None, diag=None):
    db = QtGui.qApp.db
    tblSP = db.table('rbService_Profile')
    tblEP = db.table('rbEventProfile')
    tbl = tblSP.innerJoin(tblEP, tblSP['eventProfile_id'].eq(tblEP['id']))
    cond = [tblSP['master_id'].eq(service)]
    if spec:
        cond.append(db.joinOr([
            tblSP['speciality_id'].eq(spec),
            tblSP['speciality_id'].isNull()
        ]))
    if birthDate and sex:
        cond.append("isSexAndAgeSuitable('%s', '%s', %s, %s, '%s')" % (sex, birthDate, tblSP['sex'], tblSP['age'], date))
    if diag:
        cond.append(db.joinOr([
            tblSP['mkbRegExp'].regexp(diag),
            tblSP['mkbRegExp'].eq('')
        ]))
    rec = db.getRecordEx(tbl, tblEP['code'], db.joinAnd(cond))
    if rec:
        return forceString(rec.value('code'))
    return None


class CChunkProcessor(object):
    def __init__(self, process, chunkSize, *args, **kwargs):
        self._chunkSize = chunkSize
        self._process = process
        self._values = []
        self._args = args
        self._kwargs = kwargs

    def append(self, value):
        if isinstance(value, tuple) and len(value) == 1:
            value = value[0]
        self._values.append(value)
        if len(self._values) >= self._chunkSize:
            self.process()

    def process(self):
       if self._values:
            self._process(self._values, *self._args, **self._kwargs)
            self._values = []

    def __call__(self, *args):
        self.append(args)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.process()


def withWaitCursor(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            return func(*args, **kwargs)
        except:
            raise
        finally:
            QtGui.qApp.restoreOverrideCursor()

    return wrapper


def dateRange(date1, date2):
    u"""
    :type date1: QtCore.QDate
    :type date2: QtCore.QDate
    """
    if date1 and date1.isValid() and date2 and date2.isValid():
        d1, d2 = min(date1, date2), max(date1, date2)
        for days in xrange(d1.daysTo(d2) + 1):
            yield d1.addDays(days)


def getCounter(code):
    return forceRef(QtGui.qApp.db.translate('rbCounter', 'code', code, 'id'))


def getCounterValue(counterId):
    v = QtGui.qApp.db.translate('rbCounter', 'id', counterId, 'value')
    return forceLong(v) if v is not None else None


def updateCounterValue(counterId, value=None):
    if not counterId: return
    if value is None:
        currValue = getCounterValue(counterId=counterId)
        value = (currValue + 1) if currValue is not None else None
    if value is not None:
        db = QtGui.qApp.db
        tableCounter = db.table('rbCounter')
        QtGui.qApp.db.updateRecords(tableCounter,
                                    tableCounter['value'].eq(value),
                                    tableCounter['id'].eq(counterId))


def isIterable(obj):
    try:
        _ = iter(obj)
        return True
    except TypeError:
        return False


def asIterable(obj):
    return obj if isIterable(obj) else [obj]


def reverseDict(dct):
    u"""
    { k1: v1, k2: [v2, v3] } -> { v1: k1, v2: k2, v3: k3 }
    :type dct: dict
    :rtype: dict
    """
    res = {}
    for ks, vs in dct.iteritems():
        for k in asIterable(ks):
            for v in asIterable(vs):
                res[v] = k
    return res


def splitBy(valueList, chunkSize):
    for offset in range(0, len(valueList), chunkSize):
        yield valueList[offset: offset + chunkSize]


class ComparableMixin(object):
    def _compare_to(self, other):
        raise NotImplementedError(u'_compare_to() must be implemented by subclass')

    def __eq__(self, other):
        keys = self._compare_to(other)
        return keys[0] == keys[1] if keys else NotImplemented

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        keys = self._compare_to(other)
        return keys[0] < keys[1] if keys else NotImplemented

    def __le__(self, other):
        keys = self._compare_to(other)
        return keys[0] <= keys[1] if keys else NotImplemented

    def __gt__(self, other):
        keys = self._compare_to(other)
        return keys[0] > keys[1] if keys else NotImplemented

    def __ge__(self, other):
        keys = self._compare_to(other)
        return keys[0] >= keys[1] if keys else NotImplemented