# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013-2014 Vista Software. All rights reserved.
##
#############################################################################

# TimeSeries содержит функции для работы с временными интервалами
# These functions are tested with unittest.
# Tests can be found in 'test/library/TimeSeries_test.py'
# One can run all tests in a project by calling (s11 as a wd):
#     $ nosetests --rednose --with-path=. --verbose
# For further details one is welcome to cast a look at the test file.

from PyQt4 import QtGui

def intSeries(start, end, duration, interval, amount=0):
    if duration < 0 or interval < 0:
        raise ValueError("duration and interval must be non-negaitve")

    return list(intSeriesGen(start, end, duration, interval, amount))


def intSeriesGen(start, end, duration, interval, amount=0):
    begRange = start
    endRange = begRange + duration
    period = duration + interval
    if end >= 0:
        while endRange <= end:
            yield (begRange, endRange)
            begRange += period
            endRange += period
    else:
        while amount > 0:
            yield (begRange, endRange)
            begRange += period
            endRange += period
            amount -= 1


def timeSeries(startTime, endTime, durationDays, intervalDays, amount=0, weekend=False):
    endVal = startTime.daysTo(endTime)

    # XXX: durationDays = 1 => endDay = startDay
    # XXX: intervalDays = 1 => nextStart = endDay + 2 (one _full_ day)
    duration = durationDays - 1
    interval = intervalDays + 1
    if not  weekend:
        iseries = intSeries(0, endVal, duration, interval, amount)
        return mapSeries(startTime.addDays, iseries)
    return compileSeries(startTime, endTime, duration, interval, amount)

def shiftDate(date, holydays):
    shift = 0
    shiftedDate = date
    isShifted = False
    if shiftedDate.dayOfWeek() in (6, 7):
        shift += 8 - shiftedDate.dayOfWeek()
        shiftedDate = date.addDays(shift)

    for holyday in holydays:
        tmp = holyday.date
        if tmp.day() == shiftedDate.day() and tmp.month() == shiftedDate.month():
            shift += 1
            shiftedDate = date.addDays(shift)
            isShifted = True

    if isShifted:
        shiftedDate, exShift= shiftDate(shiftedDate, holydays)
        shift += exShift
    return shiftedDate, shift


def compileSeries(startTime, endTime, duration, interval, amount):
    holydays = {}
    shift = 0
    result = []
    resultEndDate = startTime
    i = 0
    if endTime:
        while resultEndDate < endTime:
            resultStartDate = startTime if i == 0 else resultEndDate.addDays(interval)
            tmpDate = resultStartDate
            for day in range(duration + 1):
                if not holydays.has_key(tmpDate.year()):
                    holydays[tmpDate.year()] = getHolydays(tmpDate.year())
                tmpDate, exShift = shiftDate(resultStartDate.addDays(shift + day), holydays[tmpDate.year()])
                if day == 0:
                    resultStartDate = tmpDate
                shift += exShift
            shift = 0
            resultEndDate = tmpDate
            result.append((resultStartDate, resultEndDate))
            i += 1
        return result[:-1]
    for i in range(amount):
        resultStartDate = startTime if i == 0 else resultEndDate.addDays(interval)
        tmpDate = resultStartDate
        for day in range(duration + 1):
            if not holydays.has_key(tmpDate.year()):
                holydays[tmpDate.year()] = getHolydays(tmpDate.year())
            tmpDate, exShift = shiftDate(resultStartDate.addDays(shift + day), holydays[tmpDate.year()])
            if day == 0:
                resultStartDate = tmpDate
            shift += exShift
        shift = 0
        resultEndDate = tmpDate
        result.append((resultStartDate, resultEndDate))
    return result




def getHolydays(year):
    from preferences.calendar import CCalendarExceptionList
    list = CCalendarExceptionList()
    holydays = list.loadYear(QtGui.qApp.db, year)
    return list.holiday_list

# mapSeries f = map (join (***) f)
def mapSeries(f, series):
    return [(f(s), f(e)) for s, e in series]
