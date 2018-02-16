# -*- coding: utf-8 -*-
u"""
Календарные отклонения - праздники и переносы
"""
from PyQt4 import QtGui, QtCore
from array import array

from PyQt4.QtCore import *
from PyQt4.QtSql import QSqlRecord, QSqlField

from library.Utils import forceDate, forceInt, toVariant


class CCalendarException:
    u"""
    Календарное отклонение - отклонение от стандартного режима работы.
    При стандартном режиме работы каждый день имеет один из режимов (понедельник, вторник, ..., воскресенье),
    определяемых днем недели.
    Отклонение характеризуется списком дат и особым режимом (одним из 7) для каждой даты из списка.
    Пока реализованы 2 вида отклонений: праздник и перенос.
    """

    def __init__(self):
        self.date = QtCore.QDate(9999, 9, 9)
        self.endDate = self.date
        self.text = ""
        self.day = Qt.Sunday

    def getDate(self):
        u"""Базовая дата"""
        return self.date

    def getEndDate(self):
        return self.endDate

    def getMonth(self):
        return self.date.month()

    def getDay(self):
        return self.date.day()

    def getYear(self):
        return self.date.year()

    def getNumber(self):
        return QDate(self.date.year(), 1, 1).daysTo(self.date) + 1

    # noinspection PyUnusedLocal
    def getDayOfWeek(self, date):
        return self.day

    def getText(self):
        return self.text

    def isNormal(self):
        return self.date.dayOfWeek() == self.day

    def isWorkDay(self):
        return self.day != Qt.Saturday and self.day != Qt.Sunday

    def getDates(self):
        u"""Абстрактный метод - полный список дат"""
        return [self.date, ]

    def getDatesForYear(self, year):
        u"""Абстрактный метод — полный список дат в пределах заданного года"""
        return [self.date, ]

    def has(self, date):
        u"""Абстрактный метод - включает ли в себя отклонение данную дату"""
        return self.date == date

    def intersects(self, exption):
        u"""Абстрактный метод - пересекается ли это отклонение с другим отклонением"""
        return exption.has(self.date)

    def update(self, db, new):
        u"""Абстрактный метод - обновить БД и установить новое отклонение new"""
        pass

    def addToDB(self, db):
        u"""Абстрактный метод - добавить отклонение в БД"""
        pass

    def deleteFromDB(self, db):
        u"""Абстрактный метод - удалить отклонение из БД"""
        pass


class CHoliday(CCalendarException):
    u"""Календарное отклонение - праздник.
    Характеризуется днем, месяцем, годом начала и годом окончания.
    В заданный день и месяц каждый год (от начала до конца) режим работы - воскресенье.
    """

    def __init__(self, day, month, start, finish, name, endDate):
        CCalendarException.__init__(self)
        if start is not None:
            self.date = QtCore.QDate(start, month, day)
        else:
            self.date = QtCore.QDate(1, month, day)

        if finish is not None:
            self.end_year = finish
        else:
            self.end_year = 4999

        self.endDate = QtCore.QDate(self.end_year, endDate.month(), endDate.day())

        self.text = name
        self.day = Qt.Sunday

    def hasStartYear(self):
        return self.date.year() > 1

    def getStartYear(self):
        return self.date.year()

    def hasFinishYear(self):
        return self.end_year < 4999

    def getFinishYear(self):
        return self.end_year

    def has(self, date):
        return (date.month() == self.date.month()) \
               and (date.day() == self.date.day()) \
               and (date.year() >= self.date.year()) \
               and (date.year() <= self.end_year)

    def intersects(self, exption):
        if isinstance(exption, CHoliday):
            return self.getStartYear() <= exption.getFinishYear() \
                   and self.getFinishYear() >= exption.getStartYear() \
                   and self.getMonth() == exption.getMonth() \
                   and self.getDay() == exption.getDay()
        elif isinstance(exption, CChangeDay):
            return self.has(exption.getDate())
        else:
            return False

    def getDatesForYear(self, year):
        result = []
        if self.getFinishYear() >= year >= self.getStartYear():
            result = result + [QDate(year, self.getMonth(), self.getDay())]

        return result

    def getDates(self):
        result = []
        for i in xrange(self.getStartYear(), self.getFinishYear() + 1):
            result = result + [QtCore.QDate(i, self.getMonth(), self.getDay()), ]
        return result

    def load(self, db, date, startYear):
        result = db.query("""
        SELECT date, endDate, startYear, finishYear, text
        FROM CalendarExceptions
        WHERE isHoliday = 1
        AND date = '%s' AND deleted = 0
        AND (startYear = %d or (%d = 1 and isnull(startYear)))""" % (date.toString("yyyy-MM-dd"), startYear, startYear)
                          )
        startYear = 1
        finishYear = 4999
        name = self.text
        result.first()
        if result.isValid():
            holiday = result.record()
            endDate = holiday.value("endDate").toDate()
            if not holiday.isNull("startYear"):
                startYear = holiday.value("startYear").toInt()[0]
            if not holiday.isNull("finishYear"):
                finishYear = holiday.value("finishYear").toInt()[0]
            if not holiday.isNull("text"):
                name = holiday.value("text").toString()
        self.__init__(date.day(), date.month(), startYear, finishYear, name, endDate)

    def getId(self, db):
        result = db.query("""
            SELECT id
            FROM CalendarExceptions
            WHERE isHoliday = 1
            AND date = '%s' AND deleted = 0
            AND (startYear = %d or (%d = 1 and isnull(startYear)))""" % (
            self.getDate().toString("yyyy-MM-dd"), self.getStartYear(), self.getStartYear()
        ))
        result.first()
        if result.isValid():
            Id = result.record()
            Id = Id.value("id").toInt()[0]
            return Id

    def update(self, db, newhol):
        u"""Установить новый праздник с параметрами newhol"""
        table = db.table('CalendarExceptions')
        record = db.record('CalendarExceptions')

        record.setValue("id", toVariant(self.getId(db)))
        record.setValue("date", toVariant(newhol.getDate()))
        record.setValue("endDate", toVariant(newhol.getEndDate()))
        record.setValue("isHoliday", toVariant(1))
        record.setValue("startYear", toVariant(newhol.getStartYear() <= 1 if None else newhol.getStartYear()))
        record.setValue("finishYear", toVariant(newhol.getFinishYear() >= 4999 if None else newhol.getFinishYear()))
        record.setValue("text", toVariant(newhol.getText()))

        db.insertOrUpdate(table, record)

        self.__init__(
            newhol.getDay(),
            newhol.getMonth(),
            newhol.getStartYear(),
            newhol.getFinishYear(),
            newhol.getText(),
            newhol.getEndDate()
        )

    def addToDB(self, db):
        table = db.table('CalendarExceptions')
        record = db.record('CalendarExceptions')
        record.setValue("date", toVariant(self.getDate()))
        record.setValue("endDate", toVariant(self.getEndDate()))
        record.setValue("isHoliday", toVariant(1))
        record.setValue("startYear", toVariant(self.getStartYear() <= 1 if None else self.getStartYear()))
        record.setValue("finishYear", toVariant(self.getFinishYear() >= 4999 if None else self.getFinishYear()))
        record.setValue("fromDate", toVariant(None))
        record.setValue("text", toVariant(self.getText()))

        db.insertOrUpdate(table, record)

    def deleteFromDB(self, db):
        db.query(u"""
        DELETE FROM CalendarExceptions
        WHERE date = '%s'
        AND ((%d > 1 AND startYear = %d)
        OR (%d <= 1 AND isnull(startYear)))""" % (
            self.getDate().toString("yyyy-MM-dd"),
            self.getStartYear(),
            self.getStartYear(),
            self.getStartYear())
                 )


class CChangeDay(CCalendarException):
    u"""Календарное отклонение - перенос.
    Характеризуется базовой датой и датой переноса.
    Режим в базовую дату копируется с режима в дату переноса."""

    def __init__(self, date, chdate, comment):
        u"""Установить параметры переноса: дату, дату, которая переносится, комментарий"""
        CCalendarException.__init__(self)
        self.date = date
        self.chdate = chdate
        self.text = comment
        self.day = self.chdate.dayOfWeek()

    def getChangeDate(self):
        return self.chdate

    def load(self, db, date):
        result = db.query(u"""
        SELECT date, fromDate, text
        FROM CalendarExceptions
        WHERE isHoliday = 0 AND deleted = 0
        AND date = '%s'""" % (date.toString("yyyy-MM-dd")))
        result.first()
        if result.isValid():
            chday = result.record()
            fromDate = forceDate(chday.value("fromDate"))
            comment = chday.value("text").toString()
            self.__init__(date, fromDate, comment)

    def getId(self, db):
        result = db.query("""
        SELECT id
        FROM CalendarExceptions
        WHERE isHoliday = 0 AND deleted = 0
        AND date = '%s'""" % (self.getDate().toString("yyyy-MM-dd")))
        result.first()
        if result.isValid():
            Id = result.record()
            Id = Id.value("id").toInt()[0]
            return Id

    def update(self, db, newch):
        u"""Установить новый перенос с параметрами newch"""
        record = QSqlRecord()
        record.append(QSqlField("id", QVariant.Int))
        record.setValue("id", toVariant(self.getId(db)))
        record.append(QSqlField("date", QVariant.Date))
        record.setValue("date", toVariant(newch.getDate()))
        record.append(QSqlField("isHoliday", QVariant.Int))
        record.setValue("isHoliday", toVariant(0))
        record.append(QSqlField("fromDate", QVariant.Date))
        record.setValue("fromDate", toVariant(newch.getChangeDate()))
        record.append(QSqlField("text", QVariant.String))
        record.setValue("text", toVariant(newch.getText()))
        db.updateRecord("CalendarExceptions", record)
        self.__init__(newch.getDate(), newch.getChangeDate(), newch.getText())

    def addToDB(self, db):
        record = QSqlRecord()
        record.append(QSqlField("date", QVariant.Date))
        record.setValue("date", toVariant(self.getDate()))
        record.append(QSqlField("isHoliday", QVariant.Int))
        record.setValue("isHoliday", toVariant(0))
        record.append(QSqlField("startYear", QVariant.Int))
        record.setValue("startYear", toVariant(None))
        record.append(QSqlField("finishYear", QVariant.Int))
        record.setValue("finishYear", toVariant(None))
        record.append(QSqlField("fromDate", QVariant.Date))
        record.setValue("fromDate", toVariant(self.getChangeDate()))
        record.append(QSqlField("text", QVariant.String))
        record.setValue("text", toVariant(self.getText()))
        db.insertRecord("CalendarExceptions", record)

    def deleteFromDB(self, db):
        db.query("""
        DELETE FROM CalendarExceptions
        WHERE date = '%s'
        AND fromDate = '%s'""" % (self.getDate().toString("yyyy-MM-dd"), self.getChangeDate().toString("yyyy-MM-dd")))


class CCalendarExceptionList:
    u"""Список всех отклонений календаря"""

    def __init__(self):
        self.holiday_list = []
        self.changeday_list = []

    def clear(self):
        self.holiday_list = []
        self.changeday_list = []

    def load(self, db):
        u"""Загружает из БД все праздники и переносы (сортирует по дате)"""
        self.clear()
        holidays = db.query("""
        SELECT date, endDate, startYear, finishYear, text
        FROM CalendarExceptions
        WHERE isHoliday = 1 AND deleted = 0
        ORDER BY date_format(date, '%%m%%d')
        """)
        holidays.first()
        while holidays.isValid():
            holiday = holidays.record()
            date = holiday.value("date").toDate()
            endDate = holiday.value("endDate").toDate()
            if holiday.isNull("startYear"):
                startYear = 1
            else:
                startYear = holiday.value("startYear").toInt()[0]
            if holiday.isNull("finishYear"):
                finishYear = 4999
            else:
                finishYear = holiday.value("finishYear").toInt()[0]
            text = holiday.value("text").toString()
            self.addHoliday(date, startYear, finishYear, text, endDate)
            holidays.next()
        changedays = db.query("""
        SELECT date, fromDate, text
        FROM CalendarExceptions
        WHERE isHoliday = 0 AND deleted = 0
        ORDER BY date_format(date, '%%Y%%m%%d')
        """)
        changedays.first()
        while changedays.isValid():
            changeday = changedays.record()
            self.addChangeday(
                changeday.value("date").toDate(),
                changeday.value("fromDate").toDate(),
                changeday.value("text").toString()
            )
            changedays.next()

    def loadYear(self, db, year):
        u"""Загружает из БД все праздники и переносы на указанный год (сортирует по дате)
        Возвращает два списка: список id загруженных праздников и список id загруженных переносов"""
        self.clear()
        holidays = db.query("""
        SELECT id, date, endDate, startYear, finishYear, text
        FROM CalendarExceptions
        WHERE isHoliday = 1 AND deleted = 0
        AND (startYear <= %d or isnull(startYear))
        AND (finishYear >= %d or isnull(finishYear))
        ORDER BY date_format(date, '%%m%%d')
        """ % (year, year))
        holidlist = []
        holidays.first()
        while holidays.isValid():
            holiday = holidays.record()
            date = holiday.value("date").toDate()
            endDate = holiday.value("endDate").toDate()
            if holiday.isNull("startYear"):
                startYear = 1
            else:
                startYear = holiday.value("startYear").toInt()[0]
            if holiday.isNull("finishYear"):
                finishYear = 4999
            else:
                finishYear = holiday.value("finishYear").toInt()[0]
            text = holiday.value("text").toString()
            self.addHoliday(date, startYear, finishYear, text, endDate)
            holidlist = holidlist + [holiday.value("id").toInt()[0], ]
            holidays.next()
        changedays = db.query("""
        SELECT id, date, fromDate, text
        FROM CalendarExceptions
        WHERE isHoliday = 0 AND deleted = 0
        AND year(date) = %d
        ORDER BY date_format(date, '%%Y%%m%%d')
        """ % year)
        chidlist = []
        changedays.first()
        while changedays.isValid():
            changeday = changedays.record()
            self.addChangeday(
                changeday.value("date").toDate(),
                changeday.value("fromDate").toDate(),
                changeday.value("text").toString()
            )
            chidlist = chidlist + [changeday.value("id").toInt()[0], ]
            changedays.next()
        return holidlist, chidlist

    def loadYearMonth(self, year, month):
        u"""Загружает из БД все праздники и переносы на указанный год и месяц(сортирует по дате)
        Возвращает два списка: список id загруженных праздников и список id загруженных переносов"""
        self.clear()
        db = QtGui.qApp.db
        holidays = db.query("""
        SELECT date, day(date) AS dayDate
        FROM CalendarExceptions
        WHERE isHoliday = 1 AND deleted = 0
        AND (startYear <= %d or isnull(startYear))
        AND (finishYear >= %d or isnull(finishYear))
        AND month(date) = %d
        ORDER BY date_format(date, '%%m%%d')
        """ % (year, year, month))
        holidayList = []
        changedayList = []
        dayFromDateList = []
        while holidays.next():
            holiday = holidays.record()
            holidayList.append(forceInt(holiday.value('dayDate')))
        changedays = db.query("""
        SELECT date, fromDate, day(fromDate) AS dayFromDate, day(date) AS dayDate
        FROM CalendarExceptions
        WHERE isHoliday = 0 AND deleted = 0
        AND year(date) = %d
        AND month(date) = %d
        ORDER BY date_format(date, '%%Y%%m%%d')
        """ % (year, month))
        while changedays.next():
            changeday = changedays.record()
            changedayList.append(forceInt(changeday.value('dayDate')))
            dayFromDateList.append(forceInt(changeday.value('dayFromDate')))
        return holidayList, changedayList, dayFromDateList

    def getCount(self):
        return len(self.holiday_list) + len(self.changeday_list)

    def getHolidayCount(self):
        return len(self.holiday_list)

    def getChangedayCount(self):
        return len(self.changeday_list)

    def getHolidayList(self):
        return self.holiday_list

    def getChangedayList(self):
        return self.changeday_list

    def getList(self):
        return self.holiday_list + self.changeday_list

    def has(self, date):
        for exception in self.getList():
            if exception.has(date):
                return True
        return False

    def getException(self, date):
        for exception in self.getList():
            if exception.has(date):
                return exception
        return None

    def getDayOfWeek(self, date):
        exception = self.getException(date)
        if exception is not None:
            return exception.getDayOfWeek(date)
        else:
            return date.dayOfWeek()

    def addHoliday(self, date, startYear, finishYear, text, endDate):
        year = date.year() if endDate.month() >= date.month() else date.year() + 1
        dayCount = date.daysTo(QtCore.QDate(year, endDate.month(), endDate.day()))
        ext_holiday = []

        tempDate = date
        for i in range(dayCount):
            tempDate = tempDate.addDays(1)
            ext_holiday.append(CHoliday(tempDate.day(), tempDate.month(), startYear, finishYear, text, endDate))

        self.holiday_list = self.holiday_list + [
            CHoliday(date.day(), date.month(), startYear, finishYear, text, endDate),
        ] + ext_holiday

    def addChangeday(self, date, fromDate, text):
        self.changeday_list = self.changeday_list + [CChangeDay(date, fromDate, text), ]


u'''
Предоставляет методы, связанные с проверкой, является ли день рабочим,
сколько рабочих дней в промежутке и т.п.
'''


class CCalendarWorkdaysGetter:
    u"""
    @:param isSaturdayIsDayOff : bool
    @:param isSundayIsDayOff : bool
    """

    def __init__(self, isSaturdayDayOff=False, isSundayDayOff=True):

        u"""
        Структура данных, которая представляет количество рабочих дней
        словарь {int : array('i')}, где
        int : номер года. (Можно получать как QDate::year())
        array('i') : массив интов. _data[year][i] - Количество рабочих дней с начала года year до числа i того же года
        """
        self._data = {}

        u"""
        Для каждого года хранится смещение воскресения.
        """
        self.dayOffOffset = {}

        self._isSaturdayDayOff = isSaturdayDayOff
        self._isSundayDayOff = isSundayDayOff

        self._calendarExceptionList = CCalendarExceptionList()

    u'''
    Учитывается ли суббота как выходной
    @:return : bool
    '''

    def isSaturdayDayOff(self):
        return self._isSaturdayDayOff

    u'''
    Учитывается ли воскресение как выходной
    @:return : bool
    '''

    def isSundayDayOff(self):
        return self._isSundayDayOff

    u'''
    Учитывать субботу выходным?
    @:param flag : bool
    '''

    def setSaturdayDayOff(self, flag):
        self._isSaturdayDayOff = flag
        self._data = {}

    u'''
    Учитывать воскресение выходным?
    @:param flag : bool
    '''

    def setSundayDayOff(self, flag):
        self._isSundayDayOff = flag
        self._data = {}

    u'''
    Возвращает количество рабрчих дней в промежутке [begin; end)
    На всякий случай: [begin; end) - значит, что промежуток включает начало и не включает конец
    @:param begin : QDate
    @:param end : QDate
    @:return : int
    '''

    def getCountWorkdays(self, begin, end):
        result = 0
        first = self.__getDayNumber(begin)
        # daysInYear + 1 Чтобы считать [begin; endOfYear], а не [begin; endOfYear)
        last = QDate(begin.year(), 1, 1).daysInYear() + 1 if begin.year() != end.year() else self.__getDayNumber(end)
        for i in xrange(begin.year(), end.year() + 1):
            arr = self.__getYearArray(i)
            result += arr[last] - arr[first]
            first = 1
            last = QDate(i + 1, 1, 1).daysInYear() + 1 if i + 1 != end.year() else self.__getDayNumber(end)

        return result

    u'''
    Возвращает, является ли текущий день рабочим
    @:param day : QDate
    @:return : bool
    '''

    def isWorkday(self, day):
        return not (self.getCountWorkdays(day, self.__nextDay(day)) == 0)

    # noinspection PyMethodMayBeStatic
    def __nextDay(self, day):
        return day.addDays(1)

    def __getYearArray(self, year):
        if year not in self._data.keys():
            self.__loadYearArray(year)

        return self._data[year]

    def __loadYearArray(self, year):
        self._calendarExceptionList.loadYear(QtGui.qApp.db, year)

        calExcept = map(lambda x: self.__getDayNumber(x),
                        [item for sublist in
                         map(lambda e: e.getDatesForYear(year),
                             self._calendarExceptionList.getHolidayList())
                         for item in sublist
                         ]
                        )

        firstDay = QDate(year, 1, 1).dayOfWeek()
        self.dayOffOffset[year] = firstDay - 1

        list = [0, 0]
        # +2 чтобы иметь возожность что-то сказать про последний день года
        for i in xrange(2, QDate(year, 1, 1).daysInYear() + 2):
            list.append(list[i - 1])
            if (i - 1 in calExcept) or \
                    (((i - 1) + ((self.dayOffOffset[year] + 1) % 7)) % 7 == 0 and self._isSaturdayDayOff) or \
                    (((i - 1) + self.dayOffOffset[year]) % 7 == 0 and self._isSundayDayOff):
                pass
            else:
                list[i] += 1
        yearArr = array('i', list)
        self._data[year] = yearArr

    u'''
    Принимает на вход день, возвращает номер, какой по счету это день в году.
    @:param day : QDate
    @:return : int
    '''

    # noinspection PyMethodMayBeStatic
    def __getDayNumber(self, day):
        return day.dayOfYear()
        # firstDayOfYear = QDate(day.year(), 1, 1)
        # return firstDayOfYear.daysTo(day) + 1


class CCalendarWidget(QtGui.QCalendarWidget):
    u"""Календарь с подсветкой выходных дней и праздников"""
    list = CCalendarExceptionList()

    def __init__(self, parent):
        QtGui.QCalendarWidget.__init__(self, parent)
        self.setFirstDayOfWeek(Qt.Monday)
        self.datesForSelect = None
        self.disabledDates = []
        self.colorDates = None
        self.currentDate = QtCore.QDate()
        self.connect(self, QtCore.SIGNAL('clicked(QDate)'), self.onClicked)
        self.ignoredDate = []
        self.prevDate = None

    # noinspection PyMethodMayBeStatic
    def setList(self, list):
        u"""Устанавливает объект типа CCalendarExceptionList - список праздников и переносов"""
        CCalendarWidget.list = list

    ###        self.update()

    # подсчет количества дней недели выбранного дня в месяце
    # noinspection PyMethodMayBeStatic
    def getCountSuitableWeeksInMonth(self, date, startMonth=False):
        lastDayMonth = QtCore.QDate(date.year(), date.month(), date.daysInMonth())
        firstDayMonth = QtCore.QDate(date.year(), date.month(), 1)
        weekNumberCurrentWeekDate = date.weekNumber()[0] if not startMonth else firstDayMonth.weekNumber()[0]
        weekNumberLastDayMonth = lastDayMonth.weekNumber()[0]
        if weekNumberLastDayMonth == 1:
            lastDayMonth = lastDayMonth.addDays(-7)
            weekNumberLastDayMonth = lastDayMonth.weekNumber()[0] + 1
        if lastDayMonth.dayOfWeek() >= date.dayOfWeek() and not startMonth:
            return weekNumberLastDayMonth - weekNumberCurrentWeekDate + 1
        else:
            return weekNumberLastDayMonth - weekNumberCurrentWeekDate

    # noinspection PyTypeChecker,PyCallByClass
    def update(self):
        u"""Устанавливает режим рисования дат"""
        # сперва очищаем все старые установки!!!!!!!!!!!!!!!!!!!
        for (date, format) in self.dateTextFormat().items():
            if (date.dayOfWeek() == Qt.Saturday) or (date.dayOfWeek() == Qt.Sunday):
                format.setForeground(QtGui.QColor.fromRgb(255, 0, 0))  # праздники и выходные - красные
            else:
                format.setForeground(self.palette().color(QtGui.QPalette.Text))  # остальные дни - черные
            self.setDateTextFormat(date, format)
        for ex in self.list.getList():
            for date in ex.getDates():
                day = ex.getDayOfWeek(date)
                format = QtGui.QTextCharFormat()
                if (day == Qt.Saturday) or (day == Qt.Sunday):
                    format.setForeground(QtGui.QColor.fromRgb(255, 0, 0))  # праздники и выходные - красные
                else:
                    format.setForeground(self.palette().color(QtGui.QPalette.Text))  # остальные дни - черные
                self.setDateTextFormat(date, format)

    # noinspection PyCallByClass,PyTypeChecker
    def paintCell(self, painter, rect, date):
        # сперва определяем цвет текста:
        day = CCalendarWidget.list.getDayOfWeek(date)
        if date.month() != self.monthShown():
            painter.setPen(self.palette().color(QtGui.QPalette.Mid))  # дни за пределом текущего месяца - серенькие
        elif (day == Qt.Saturday) or (day == Qt.Sunday):
            painter.setPen(QtGui.QColor.fromRgb(255, 0, 0))  # праздники и выходные - красные
            # если нужна полная зависимость от палитры, можно сделать их фиолетовенькими:)
            # painter.setPen(self.palette().color(QtGui.QPalette.LinkVisited))
        else:
            painter.setPen(self.palette().color(QtGui.QPalette.Text))  # остальные дни - черные
        # затем определяем цвет фона:
        if date == self.selectedDate():
            if self.datesForSelect is not None and not len(self.datesForSelect):
                brush = QtGui.QBrush(self.palette().color(QtGui.QPalette.AlternateBase))
                painter.setPen(self.palette().color(QtGui.QPalette.Text))
            else:
                brush = QtGui.QBrush(self.palette().color(QtGui.QPalette.Highlight))  # текущую дату выделяем
                painter.setPen(self.palette().color(QtGui.QPalette.HighlightedText))
        elif date < self.minimumDate() or date > self.maximumDate():
            # за пределом диапазона окрашиваем в светло-серый
            brush = QtGui.QBrush(self.palette().color(QtGui.QPalette.AlternateBase))
        elif date in self.ignoredDate:
            brush = QtGui.QBrush(self.palette().color(QtGui.QPalette.AlternateBase))
        else:
            brush = QtGui.QBrush(self.palette().color(QtGui.QPalette.Base))  # а вообще календарь - белый
        if self.datesForSelect is not None and date not in self.datesForSelect:
            brush = QtGui.QBrush(self.palette().color(QtGui.QPalette.AlternateBase))
        # определяем фон ячеек, который задан в функции setColor
        if self.colorDates is not None and self.colorDates:
            for colorDate in self.colorDates:
                if date in colorDate['values'] and self.datesForSelect is not None and date not in self.datesForSelect:
                    brush = QtGui.QBrush(colorDate['brush'])
                if date in colorDate['values'] and self.disabledDates and date in self.disabledDates:
                    brush = QtGui.QBrush(colorDate['brush'])
        # а теперь рисуем:
        painter.fillRect(rect, brush)
        painter.drawText(rect, Qt.AlignCenter, '%d' % date.day())

    # вероятно, лучше использовать QCalendarWidget::setDateTextFormat
    # и менять/подгружать по сигналу currentPageChanged
    # чем самому рисовать клеточки.
    # образец для подражания функция void Window::reformatCalendarPage()
    # в Calendar Widget Example (widgets/calendarwidget/window.cpp)

    # можно задавать несколько доступных периодов, используя функцию несколько раз с разным аргуметом
    def setDateForSelect(self, dates):
        if dates and self.currentDate not in dates:
            self.currentDate = dates[0]
            self.setSelectedDate(self.currentDate)
        self.datesForSelect = dates
        self.updateCells()

    # установка выделения цветом дней, содержащихся в списке
    # аргумент colorDates представляет собой список словарей, которые имеют ключи brush и values
    def setColor(self, colorDates, disabledDates=None):
        self.colorDates = colorDates
        self.disabledDates = disabledDates if disabledDates else []
        self.updateCells()

    def addIgnoredDate(self, date):
        self.ignoredDate.append(QtCore.QDate(date))

    def onClicked(self, date):
        if self.datesForSelect is not None and date not in self.datesForSelect:
            self.setSelectedDate(self.currentDate)
