# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
#
#
# AgeSelector -- это структура данных для описания ограничения возраста пациента
# по устройству - это кортеж из 4 значений: (begUnit, begCount, endUnit, endCount)
# begUnit и endUnit - единицы измерения времени:
# 0 - нет,
# 1 - дни
# 2 - недели
# 3 - месяцы
# 4 - года
# begCount и endCount - наименьший и наибольший подходящий возраст в
# указанных единицах
#
#############################################################################

from library.Utils  import *


AgeSelectorUnits = u'днмг'

def parseAgeSelectorPart(val):
    if val:
        matchObject = re.match(r'^(\d+)\s*([^\d\s]+)$', val)
        if matchObject:
            strCount, strUnit = matchObject.groups()
            count = int(strCount) if strCount else 0
            unit  = AgeSelectorUnits.find(strUnit.lower())+1
            if unit == 0:
                raise ValueError, u'Неизвестная единица измерения "%s"' % strUnit
            return (unit, count)
        else:
            raise ValueError, u'Недопустимый синтаксис части селектора возраста "%s"' % val
    else:
        return 0, 0

def parseAgeSelectorInt(value, isExtend=False):
    u"""
    Синтаксис:

        "{NNN{д|н|м|г}-{MMM{д|н|м|г}}{/SSS{+}{-}}, {...}, {...}, ...", где

    1. С NNN дней/недель/месяцев/лет по MMM дней/недель/месяцев/лет с шагом SSS;
    2. {+} только для лет - возраст считать по календарному году;
    3. {-} - исключить данный диапазон;
    4. Пустая нижняя или верхняя граница - нет ограничения снизу или сверху;
       Для шага и плюса единицы диапазонов должны совпадать, если заданы
    """

    def parseBase(value):
        begUnit, begCount, endUnit, endCount = 0, 0, 0, 0
        parts = value.split('-')
        if len(parts) == 1:
            begUnit, begCount = parseAgeSelectorPart(parts[0].strip())
        elif len(parts) == 2:
            begUnit, begCount = parseAgeSelectorPart(parts[0].strip())
            endUnit, endCount = parseAgeSelectorPart(parts[1].strip())
        else:
            raise ValueError(u'Недопустимый синтаксис селектора возраста "%s"' % value)
        return [begUnit, begCount, endUnit, endCount]

    def parseExtended(base, value, begUnit, endUnit):
        step, useCalendarYear, useExclusion = 0, False, False
        extendedValues = re.match(r'^\s*(\d*)\s*([\+]?)([\-]?)$', value)
        if extendedValues:
            stepValue, plusValue, exclusionValue = extendedValues.groups()
            step = int(stepValue) if stepValue else 0
            useCalendarYear = plusValue == '+'
            useExclusion = exclusionValue == '-'
        if (not (begUnit or endUnit) or (begUnit and endUnit and begUnit != endUnit)) and (step or useCalendarYear):
            raise ValueError(u'Недопустимый синтаксис расширенной части "%s" для селектора возраста '
                             u'"%s"' % (value, base))
        elif ((begUnit and AgeSelectorUnits[begUnit - 1] != u'г') or
                (endUnit and AgeSelectorUnits[endUnit - 1] != u'г')) and useCalendarYear:
            raise ValueError(u'Недопустимый синтаксис расширенной части "%s" для селектора возраста '
                             u'"%s"' % (value, base))
        return [step, useCalendarYear, useExclusion]

    def parse(value):
        if not isExtend:
            base = parseBase(value)
        else:
            parts = value.split('/')
            base = parseBase(parts[0])
            if len(parts) == 1:
                base.extend([0, False, False])
            elif len(parts) == 2:
                base.extend(parseExtended(parts[0], parts[1], base[0], base[2]))
            else:
                raise ValueError(u'Недопустимый синтаксис селектора возраста "%s"' % value)
        return base

    if not isExtend:
        result = parse(value)
    else:
        result = []
        for value in value.split(','):
            result.append(tuple(parse(value)))
    return tuple(result)


def parseAgeSelector(val, isExtend=False):
    try:
        return parseAgeSelectorInt(val, isExtend)
    except:
        QtGui.qApp.logCurrentException()
        if isExtend:
            return ()
        return 0, 0, 0, 0


def checkAgeSelectorSyntax(val, isExtend=False):
    if val.find('/') > -1 or val.find(',') > -1:
        isExtend = True
    try:
        parseAgeSelectorInt(val, isExtend)
        return True
    except:
        return False


def composeAgeSelectorPart(unit, count):
    if unit == 0 or count == 0:
        return ''
    else:
        return str(count)+AgeSelectorUnits[unit-1]


def composeAgeSelector(begUnit, begCount, endUnit, endCount):
    if (begUnit == 0 or begCount == 0) and (endUnit == 0 or endCount == 0):
        return ''
    else:
        return composeAgeSelectorPart(begUnit,begCount)+'-'+composeAgeSelectorPart(endUnit,endCount)


def checkExtendedAgeSelector(ageSelectors, clientAge):
    result = True
    for ageSelector in ageSelectors:
        begUnit, begCount, endUnit, endCount, step, useCalendarYear, useExclusion = ageSelector
        checkClientAge = clientAge
        if useCalendarYear and isinstance(checkClientAge, CAgeTuple):
            birthDate = checkClientAge.birthDate
            eventDate = checkClientAge.checkDate
            checkClientAge = CAgeTuple((checkClientAge[0], checkClientAge[1], checkClientAge[2],
                                        eventDate.year() - birthDate.year()),
                                       birthDate,
                                       eventDate)
        result = checkAgeSelector((begUnit, begCount, endUnit, endCount), checkClientAge)
        if result:
            if step:
                unit = begUnit if begUnit else endUnit
                if (checkClientAge[unit - 1] - begCount) % step != 0:
                    result = False
            if result:
                result = not useExclusion
                break
    return result


def findExtendedAgeSelectorDist(ageSelectors, clientAge):
    u"""
    По селектору и возрасту возвращает, на какое минимальное число дней
    надо изменить возраст клиента, чтобы он подходил под селектор (расширенный).
    """
    result = sys.maxint
    for ageSelector in ageSelectors:
        begUnit, begCount, endUnit, endCount, step, useCalendarYear, useExclusion = ageSelector
        unit = begUnit if begUnit != 0 else endUnit
        checkClientAge = clientAge
        if not useExclusion and (begUnit != 0 or endUnit != 0):
            if useCalendarYear and isinstance(checkClientAge, CAgeTuple):
                birthDate = checkClientAge.birthDate
                eventDate = checkClientAge.checkDate
                checkClientAge = CAgeTuple((checkClientAge[0], checkClientAge[1], checkClientAge[2],
                                            eventDate.year() - birthDate.year()),
                                           birthDate,
                                           eventDate)
            if not step:
                step = 1
            for time in range(begCount, endCount + step, step):
                dist = abs(checkClientAge[0] - time * [1, 7, 30, 365][unit - 1])
                result = min(result, dist)
    return result


def findAgeSelectorDist((begUnit, begCount, endUnit, endCount), ageTuple):
    u"""
    По селектору и возрасту возвращает, на какое минимальное число дней
    надо изменить возраст клиента, чтобы он подходил под селектор.
    """
    result = sys.maxint
    unit = begUnit if begUnit != 0 else endUnit
    for time in range(begCount, endCount + 1):
        dist = abs(ageTuple[0] - time * [1, 7, 30, 365][unit - 1])
        result = min(result, dist)
    return result


def checkAgeSelector((begUnit, begCount, endUnit, endCount), ageTuple):
    if begUnit != 0:
        if ageTuple[begUnit - 1] < begCount:
            return False
    if endUnit != 0:
        if ageTuple[endUnit - 1] > endCount:
            return False
    return True


def convertAgeSelectorToAgeRange((begUnit, begCount, endUnit, endCount)):
    begAge = 0
    if begUnit == 1: # д
        begAge = begCount/365
    elif begUnit == 2: # н
        begAge = begCount*7/365
    elif begUnit == 3: # м
        begAge = begCount/12
    elif begUnit == 4: # г
        begAge = begCount

    endAge = 150
    if endUnit == 1: # д
        endAge = (endCount+364)/365
    elif endUnit == 2: # н
        endAge = (endCount*7+364)/365
    elif endUnit == 3: # м
        endAge = (endCount+11)/12
    elif endUnit == 4: # г
        endAge = endCount

    return begAge, endAge


#class CAgeSelector(QtGui.QWidget, Ui_Form):
#    def __init__(self,  parent=None):
#        QtGui.QWidget.__init__(self,  parent)
#        self.setupUi(self)
#        self.edtBegAgeCount.setEnabled(False)
#        self.edtBegAgeCount.setText('')
#        self.edtEndAgeCount.setEnabled(False)
#        self.edtEndAgeCount.setText('')
#        self.cmbBegAgeUnit.setCurrentIndex(0)
#        self.cmbEndAgeUnit.setCurrentIndex(0)
#
#    def setValue(self, val):
#        (begUnit, begCount, endUnit, endCount) = parseAgeSelector(val)
#        self.cmbBegAgeUnit.setCurrentIndex(begUnit)
#        self.edtBegAgeCount.setText(begCount)
#        self.cmbEndAgeUnit.setCurrentIndex(endUnit)
#        self.edtEndAgeCount.setText(endCount)
#
#    def getValue(self):
#        return compseAgeSelector(
#                                 self.cmbBegAgeUnit.currentIndex,  self.edtBegAgeCount.text(),
#                                 self.cmbEndAgeUnit.currentIndex,  self.edtEndAgeCount.text()
#                                )
#
#
#    @QtCore.pyqtSlot(int)
#    def on_cmbBegAgeUnit_currentIndexChanged(self, index):
#        self.edtBegAgeCount.setEnabled(index>0)
#        self.emitValueChanged
#
#
#    @QtCore.pyqtSlot(QString)
#    def on_edtBegAgeCount_textEdited(self, text):
#        self.emitValueChanged
#
#
#    @QtCore.pyqtSlot(int)
#    def on_cmbEndAgeUnit_currentIndexChanged(self, index):
#        self.edtEndAgeCount.setEnabled(index>0)
#        self.emitValueChanged
#
#
#    @QtCore.pyqtSlot(QString)
#    def on_edtEndAgeCount_textEdited(self, text):
#        self.emitValueChanged
#
#
#    def emitValueChanged(self):
#        self.emit(QtCore.SIGNAL('valueChanged()'))
