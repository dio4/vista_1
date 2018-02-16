# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

import itertools
from PyQt4 import QtCore, QtGui

from Events.Action import CAction, ensureActionTypePresence
from Events.Utils import getEventType
from Timeline.TemplateDialog import callObjectAttributeMethod, conversion, getObjectAttribute, listEdit, setInterval, \
    setSpinBoxInterval, setSignalMapper
from Ui_TemplateEdit import Ui_TemplateEdit
from Users.Rights import urEditFilledTimetableAction
from library import constants
from library.DialogBase import CDialogBase
from library.TableView import CTableView
from library.TimeEdit import CTimeRangeEdit, CTimeEdit
from library.Utils import forceStringEx, forceString, forceInt, forceRef, forceTime, forceBool, toVariant
from library.calendar import CCalendarExceptionList
from library.crbcombobox import CRBModel, CRBComboBox


def getEvent(eventTypeCode, date, person):
    db = QtGui.qApp.db
    eventTypeId = getEventType(eventTypeCode).eventTypeId
    eventTable = db.table('Event')
    cond = [eventTable['eventType_id'].eq(eventTypeId),
            eventTable['execDate'].eq(date),
            eventTable['execPerson_id'].eq(person)
            ]
    eventRecord = db.getRecordEx(eventTable, '*', cond)
    if not eventRecord:
        eventRecord = eventTable.newRecord()
        eventRecord.setValue('eventType_id', QtCore.QVariant(eventTypeId))
        eventRecord.setValue('setDate', toVariant(date))
        eventRecord.setValue('setPerson_id', QtCore.QVariant(person))
        eventRecord.setValue('execDate', toVariant(date))
        eventRecord.setValue('execPerson_id', QtCore.QVariant(person))
    return eventRecord


def formatTimeRange(range):
    if range:
        start, finish = range
        return start.toString('HH:mm') + ' - ' + finish.toString('HH:mm')
    else:
        return ''


def convertTimeRangeToVariant(range):
    if range:
        start, finish = range
        return QtCore.QVariant.fromList([toVariant(start), toVariant(finish)])
    else:
        return QtCore.QVariant()


def convertVariantToTimeRange(value):
    list = value.toList()
    if len(list) == 2:
        start = list[0].toTime()
        finish = list[1].toTime()
        if start.isNull() and finish.isNull():
            return None
        return start, finish
    else:
        return None


def calcSecondsInTimeRange(range):
    if range:
        start, finish = range
        result = start.secsTo(finish)
        if result <= 0:
            result += 86400
    else:
        result = 0
    return result


def calcSecondsInTime(time):
    if not time or time.isNull():
        result = 0
    else:
        result = (time.hour() * 60 + time.minute()) * 60 + time.second()
    return result


class CAttrs(object):

    def __init__(self):
        self.numDays = 0
        self.numAbsenceDays = 0
        self.numServDays = 0

        self.numAmbDays = 0
        self.numAmbTime = 0
        self.numAmbPlan = 0
        self.numAmbFact = 0

        self.numHomeDays = 0
        self.numHomeTime = 0
        self.numHomePlan = 0
        self.numHomeFact = 0

        self.numExpDays = 0
        self.numExpTime = 0
        self.numExpPlan = 0
        self.numExpFact = 0

    def __cmp__(self, other):
        return self.numDays - other.numDays or \
               self.numAbsenceDays - other.numAbsenceDays or \
               self.numServDays - other.numServDays or \
               self.numAmbDays - other.numAmbDays or \
               self.numAmbTime - other.numAmbTime or \
               self.numAmbPlan - other.numAmbPlan or \
               self.numAmbFact - other.numAmbFact or \
               self.numHomeDays - other.numHomeDays or \
               self.numHomeTime - other.numHomeTime or \
               self.numHomePlan - other.numHomePlan or \
               self.numHomeFact - other.numHomeFact or \
               self.numExpDays - other.numExpDays or \
               self.numExpTime - other.numExpTime or \
               self.numExpPlan - other.numExpPlan or \
               self.numExpFact - other.numExpFact


class CTimeTableModel(QtCore.QAbstractTableModel):
    ciAmbTimeRange = 0  # интервал времени амбулаторного приёма
    ciAmbOffice = 1
    ciAmbPlan = 2
    ciAmbInterval = 3
    ciAmbTime = 4
    ciAmbFact = 5

    ciHomeTimeRange = 6  # интервал времени для вызовов на дом
    ciHomePlan = 7
    ciHomeInterval = 8
    ciHomeTime = 9
    ciHomeFact = 10

    ciExpTimeRange = 11  # интервал времени экспертной работы
    ciExpOffice = 12
    ciExpPlan = 13
    ciExpTime = 14
    ciExpFact = 15
    ciOtherTime = 16
    ciFactTime = 17
    ciReasonOfAbsence = 18
    ciAmbInterOffice = 19
    ciAmbInterPlan = 20
    ciAmbInterInterval = 21
    ciAmbInterColor = 22
    ciInterNotExternalSystem = 23

    ciAmbChange = 24
    ciHomeChange = 25
    ciAmbTimeRange1 = 26
    ciAmbOffice1 = 27
    ciAmbPlan1 = 28
    ciAmbInterval1 = 29
    ciAmbColor1 = 30
    ciHomeTimeRange1 = 31
    ciHomePlan1 = 32
    ciHomeInterval1 = 33
    ciNotExternalSystem1 = 34

    ciAmbTimeRange2 = 35
    ciAmbOffice2 = 36
    ciAmbPlan2 = 37
    ciAmbInterval2 = 38
    ciAmbColor2 = 39
    ciAmbColor = 40
    ciHomeTimeRange2 = 41
    ciHomePlan2 = 42
    ciHomeInterval2 = 43
    ciNotExternalSystem2 = 44

    ciExpChange = 45
    ciTimeLineChange = 46
    ciAmbTimesChange = 47
    ciHomeTimesChange = 48

    numCols = 49
    visibleCols = 19

    cilTimeRange = set([ciAmbTimeRange, ciHomeTimeRange, ciExpTimeRange])
    cilTime = set([ciAmbTime, ciHomeTime, ciExpTime, ciOtherTime, ciFactTime])
    cilNum = set([ciAmbPlan, ciAmbFact, ciHomePlan, ciHomeFact, ciExpPlan, ciExpFact])
    cilColors = set([ciAmbColor, ciAmbColor1, ciAmbColor2, ciAmbInterColor])
    cilPlan = set([ciAmbPlan, ciHomePlan])
    cilInterval = set([ciAmbInterval, ciHomeInterval])

    cilAmb = set([ciAmbTimeRange, ciAmbOffice, ciAmbPlan, ciAmbInterval, ciAmbTime, ciAmbFact])
    cilAmbTimes = set([ciAmbTimeRange, ciAmbPlan, ciAmbInterval])
    cilHome = set([ciHomeTimeRange, ciHomePlan, ciHomeInterval, ciHomeTime, ciHomeFact])
    cilHomeTimes = set([ciHomeTimeRange, ciHomePlan, ciHomeInterval])
    cilExp = set([ciExpTimeRange, ciExpOffice, ciExpPlan, ciExpTime, ciExpFact])

    headerText = [u'Амбулаторно', u'Кабинет', u'План', u'Интервал', u'ФЧасы', u'Принято',
                  u'На дому', u'План', u'Интервал', u'ФЧасы', u'Принято',
                  u'КЭР',  # КЭР = Клинико-экспертная работа
                  u'Кабинет', u'План', u'ФЧасы', u'Принято',
                  u'Прочее',
                  u'Табель',
                  u'Причина отсутствия'
                  ]

    __pyqtSignals__ = ('attrsChanged()',
                       )

    actionsTypesChecked = False

    def __init__(self, parent):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.personId = None
        self.year = None
        self.month = None
        self.begDate = None
        self.selectedDate = None
        self.daysInMonth = 0
        self.items = []
        self.dayInfoPersons = []
        self.redDays = []
        self.redBrush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        self.attrs = CAttrs()
        self.events = []
        self.actionAmbulance = []
        self.actionHome = []
        self.actionExp = []
        if not CTimeTableModel.actionsTypesChecked:
            self.checkActionTypes()
            CTimeTableModel.actionsTypesChecked = True
        self.modelReasonOfAbsence = CRBModel(self)
        self.modelReasonOfAbsence.setTable('rbReasonOfAbsence')
        self.days = {1: u"Пн", 2: u"Вт", 3: u"Ср", 4: u"Чт", 5: u"Пт", 6: u"Сб", 7: u"Вс"}
        self._isEditable = True
        self.userHasRightToEditFilledTimetableAction = QtGui.qApp.userHasRight(urEditFilledTimetableAction)

    def setEditable(self, editable):
        self._isEditable = editable

    def isEditable(self):
        return self._isEditable

    def checkActionTypes(self):
        ensureActionTypePresence(
            constants.atcAmbulance,
            [
                {'name': 'begTime', 'typeName': 'Time'},
                {'name': 'endTime', 'typeName': 'Time'},
                {'name': 'office', 'typeName': 'String'},
                {'name': 'plan', 'typeName': 'Integer'},
                {'name': 'color', 'typeName': 'String'},
                {'name': 'begTime1', 'typeName': 'Time'},
                {'name': 'endTime1', 'typeName': 'Time'},
                {'name': 'office1', 'typeName': 'String'},
                {'name': 'plan1', 'typeName': 'Integer'},
                {'name': 'color1', 'typeName': 'String'},
                {'name': 'begTime2', 'typeName': 'Time'},
                {'name': 'endTime2', 'typeName': 'Time'},
                {'name': 'office2', 'typeName': 'String'},
                {'name': 'plan2', 'typeName': 'Integer'},
                {'name': 'color2', 'typeName': 'String'},
                {'name': 'planInter', 'typeName': 'Integer'},
                {'name': 'officeInter', 'typeName': 'String'},
                {'name': 'colorInter', 'typeName': 'String'},
                {'name': 'fact', 'typeName': 'Integer'},
                {'name': 'time', 'typeName': 'Time'},
                {'name': 'times', 'typeName': 'Time', 'isVector': True},
                {'name': 'colors', 'typeName': 'String', 'isVector': True},
                {'name': 'queue', 'typeName': 'Reference', 'valueDomain': 'Action', 'isVector': True},
                {'name': 'notExternalSystems', 'typeName': 'Integer', 'isVector': True},
                {'name': 'notExternalSystem1', 'typeName': 'Integer'},
                {'name': 'notExternalSystem2', 'typeName': 'Integer'},
                {'name': 'notExternalSystemInter', 'typeName': 'Integer'}
            ]
        )
        ensureActionTypePresence(
            constants.atcHome,
            [
                {'name': 'begTime', 'typeName': 'Time'},
                {'name': 'endTime', 'typeName': 'Time'},
                {'name': 'plan', 'typeName': 'Integer'},
                {'name': 'begTime1', 'typeName': 'Time'},
                {'name': 'endTime1', 'typeName': 'Time'},
                {'name': 'plan1', 'typeName': 'Integer'},
                {'name': 'begTime2', 'typeName': 'Time'},
                {'name': 'endTime2', 'typeName': 'Time'},
                {'name': 'plan2', 'typeName': 'Integer'},
                {'name': 'fact', 'typeName': 'Integer'},
                {'name': 'time', 'typeName': 'Time'},
                {'name': 'times', 'typeName': 'Time', 'isVector': True},
                {'name': 'queue', 'typeName': 'Reference', 'valueDomain': 'Action', 'isVector': True},
            ]
        )
        ensureActionTypePresence(
            constants.atcExp,
            [
                {'name': 'begTime', 'typeName': 'Time'},
                {'name': 'endTime', 'typeName': 'Time'},
                {'name': 'office', 'typeName': 'String'},
                {'name': 'plan', 'typeName': 'Integer'},
                {'name': 'fact', 'typeName': 'Integer'},
                {'name': 'time', 'typeName': 'Time'},
                {'name': 'times', 'typeName': 'Time', 'isVector': True},
                {'name': 'queue', 'typeName': 'Reference', 'valueDomain': 'Action', 'isVector': True},
            ]
        )
        ensureActionTypePresence(
            constants.atcTimeLine,
            [
                {'name': 'otherTime', 'typeName': 'Time'},
                {'name': 'factTime', 'typeName': 'Time'},
                {'name': 'reasonOfAbsence', 'typeName': 'Reference', 'valueDomain': 'rbReasonOfAbsence'},
            ]
        )

    def columnCount(self, index=QtCore.QModelIndex()):
        return CTimeTableModel.visibleCols

    def flags(self, index=None):
        day = index.row()
        if day < self.daysInMonth:
            action = self.actionAmbulance[day]
            if action and any(action['queue']) and not self.userHasRightToEditFilledTimetableAction:
                return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

    def rowCount(self, index=QtCore.QModelIndex()):
        if self.daysInMonth:
            return self.daysInMonth + 1
        else:
            return 0

    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = index.column()
        row = index.row()

        if role == QtCore.Qt.EditRole:
            if row < self.daysInMonth:
                if column in CTimeTableModel.cilTimeRange:
                    return convertTimeRangeToVariant(self.items[row][column])
            return toVariant(self.items[row][column])

        if role == QtCore.Qt.DisplayRole:
            if row < self.daysInMonth:
                if column in CTimeTableModel.cilTimeRange:
                    reasonOfAbsenceId = self.items[row][CTimeTableModel.ciReasonOfAbsence]
                    return QtCore.QVariant(forceString(QtGui.qApp.db.translate('rbReasonOfAbsence', 'id', reasonOfAbsenceId, 'code'))) if reasonOfAbsenceId else QtCore.QVariant(formatTimeRange(self.items[row][column]))
                if column in CTimeTableModel.cilTime:
                    val = self.items[row][column]
                    if val:
                        return QtCore.QVariant(self.items[row][column].toString('HH:mm'))
                    else:
                        return QtCore.QVariant()
                if column == CTimeTableModel.ciReasonOfAbsence:
                    val = self.items[row][column]
                    if val:
                        index = self.modelReasonOfAbsence.searchId(val)
                        if index >= 0:
                            name = self.modelReasonOfAbsence.getName(index)
                        else:
                            name = '{%d}' % val
                        return QtCore.QVariant(name)
                if column in CTimeTableModel.cilColors:
                    return QtCore.QVariant()
            return QtCore.QVariant(self.items[row][column])

        if role == QtCore.Qt.TextAlignmentRole:
            if row < self.daysInMonth:
                if column not in CTimeTableModel.cilNum:
                    return QtCore.QVariant(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
            return QtCore.QVariant(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)

        if role == QtCore.Qt.BackgroundColorRole:
            if row < self.daysInMonth:
                if column in CTimeTableModel.cilColors:
                    c = self.items[row][column]
                    if c and not QtGui.QColor(c) == QtCore.Qt.white:
                        return QtCore.QVariant(QtGui.QColor(c))
        return QtCore.QVariant()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            column = index.column()
            row = index.row()
            if row < self.daysInMonth:
                if column in CTimeTableModel.cilTimeRange:
                    newValue = convertVariantToTimeRange(value)
                    if column == self.ciAmbTimeRange:
                        self.items[row][self.ciAmbPlan] = self.conversion(newValue, self.items[row][self.ciAmbInterval])
                    elif column == self.ciHomeTimeRange:
                        self.items[row][self.ciHomePlan] = self.conversion(newValue, self.items[row][self.ciHomeInterval])
                elif column in CTimeTableModel.cilTime:
                    newValue = value.toTime()
                elif column in CTimeTableModel.cilNum:
                    newValue = forceInt(value)
                    if column in self.cilPlan:
                        self.items[row][column + 1] = self.conversion(self.items[row][column - 2 if column in self.cilAmb else column - 1], newValue)
                elif column in self.cilInterval:
                    newValue = forceInt(value)
                    self.items[row][column - 1] = self.conversion(self.items[row][column - 3 if column in self.cilAmb else column - 2], newValue)
                elif column == CTimeTableModel.ciReasonOfAbsence:
                    newValue = forceRef(value)
                else:
                    newValue = forceStringEx(value)
                item = self.items[row]
                if item[column] != newValue:
                    item[column] = newValue
                    self.emitCellChanged(row, column)
                    self.updateSums(column)
                    self.updateAttrs()
                    if column in self.cilAmb:
                        item[self.ciAmbChange] = True
                        if column in self.cilAmbTimes:
                            item[self.ciAmbTimesChange] = True
                    elif column in self.cilHome:
                        item[self.ciHomeChange] = True
                        if column in self.cilHomeTimes:
                            item[self.ciHomeTimesChange] = True
                    elif column in self.cilExp:
                        item[self.ciExpChange] = True
                    else:
                        item[self.ciTimeLineChange] = True
            return True
        return False

    def emitCellChanged(self, row, column):
        index = self.index(row, column)
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)

    def emitAttrsChanged(self):
        self.emit(QtCore.SIGNAL('attrsChanged()'))

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.headerText[section])
        if orientation == QtCore.Qt.Vertical and self.daysInMonth:
            if role == QtCore.Qt.DisplayRole:
                if section < self.daysInMonth:
                    dayOfMonth = QtCore.QDate(self.year, self.month, section + 1)
                    return QtCore.QVariant(forceString(dayOfMonth.day()) + ' ' + self.days[dayOfMonth.dayOfWeek()])
                else:
                    return QtCore.QVariant(u'Всего')
            if role == QtCore.Qt.ToolTipRole:
                if section < self.daysInMonth:
                    return QtCore.QVariant(self.begDate.addDays(section))
                else:
                    return QtCore.QVariant(u'Всего')
            if role == QtCore.Qt.ForegroundRole:
                if section < self.daysInMonth and self.redDays[section]:
                    return QtCore.QVariant(self.redBrush)
                else:
                    return QtCore.QVariant()
        return QtCore.QVariant()

    def setPersonAndMonth(self, personId, year, month, selectedDate=None):
        self.selectedDate = selectedDate
        if self.personId != personId or self.year != year or self.month != month:
            self.saveData()
            self.loadData(personId, year, month)

    def saveData(self):
        db = QtGui.qApp.db

        def updateQueuedClient(action, newTimes, date=None):
            oldTimes = action['times']
            # atronah: предполагается, что новый набор времен больше старого и старый расширяется до его размеров добавлением пустых времен
            #            oldTimes.extend([None] * max(0, len(newTimes) - len(oldTimes)))
            oldQueues = action['queue']

            # Уровнение длин списка времен и списка записей на эти времена
            diff = len(oldTimes) - len(oldQueues)
            if diff < 0:
                oldTimes.extend([None] * (-diff))
            elif diff > 0:
                oldQueues.extend([None] * diff)

            # Заполнение списка новых записей пустыми значениями. Длин списка ровна максимально возможной
            newQueues = [None] * len(newTimes)

            # Поиск индекса последнего валидного времени в новом расписании
            lastValidNewTimeIndex = None
            for newIndex, newTime in enumerate(newTimes):
                if newTime is None:
                    break
                lastValidNewTimeIndex = newIndex

            # Для каждой записи в старом расписании
            for oldIndex, oldQueue in enumerate(oldQueues):
                if oldQueue:  # Если запись не пустая
                    oldTime = oldTimes[oldIndex]  # то получить старое время записи
                    if oldTime is None:
                        oldTime = forceTime(QtGui.qApp.db.translate('Action', 'id', oldQueue, 'directionDate'))

                    insertIndex = None
                    # Если в новом расписании есть валидное время и у записи из старого расписания тоже есть время
                    if insertIndex is None and lastValidNewTimeIndex >= 0 and oldTime:
                        # FIXME: xrange(lastValidNewTimeIndex+1)?
                        for newIndex in xrange(lastValidNewTimeIndex):  # Перебрать все валидные временые метки нового расписания
                            # Найти ближайшее подходящее (большее, либо равное старому) время в новом расписании
                            if oldTime <= newTimes[newIndex] and not newQueues[newIndex]:
                                insertIndex = newIndex
                                break

                    # Если новое время (новый индекс для старой записи) так и не было найдено
                    if insertIndex is None:
                        # Вставить старую запись в первое пустое поле старого расписания
                        for newIndex in xrange(len(newQueues)):
                            if not newQueues[newIndex]:
                                insertIndex = newIndex
                                break

                    if insertIndex is not None:
                        # Вставка записи из старого расписания в подходящее место нового расписания
                        newQueues[insertIndex] = oldQueue
                    else:
                        # Добавление записи из старого расписания в конец нового расписания
                        newQueues.append(oldQueue)

            # Обновляем время приема в действии 'запись на прием'
            tableAction = db.table('Action')
            for queueActionId, queueTime in itertools.izip(newQueues, newTimes):
                if queueActionId and queueTime:
                    queueRecord = db.getRecord(tableAction, '*', queueActionId)
                    queueRecord.setValue('directionDate', toVariant(QtCore.QDateTime(date, queueTime)))
                    db.updateRecord(tableAction, queueRecord)

            action['times'] = newTimes
            action['queue'] = newQueues

        # end updateQueuedClient

        if self.personId and self.year and self.month:
            eventTable = db.table('Event')
            db.transaction()
            try:
                for day in xrange(self.daysInMonth):
                    date = QtCore.QDate(self.year, self.month, day + 1)
                    dayInfo = self.items[day]
                    event = self.events[day]
                    if not event:
                        continue
                    eventId = db.insertOrUpdate(eventTable, event)
                    #
                    if dayInfo[self.ciAmbChange]:
                        action = self.actionAmbulance[day]
                        if not action:
                            action = CAction.createByTypeCode(constants.atcAmbulance)
                            self.actionAmbulance[day] = action
                        timeRange = dayInfo[self.ciAmbTimeRange]
                        if timeRange:
                            action['begTime'], action['endTime'] = timeRange
                        else:
                            del action['begTime']
                            del action['endTime']
                        action['office'] = dayInfo[self.ciAmbOffice]
                        action['plan'] = dayInfo[self.ciAmbInterval]
                        action['color'] = dayInfo[self.ciAmbColor]
                        timeRange1 = dayInfo[self.ciAmbTimeRange1]
                        if timeRange1:
                            action['begTime1'], action['endTime1'] = timeRange1
                        else:
                            del action['begTime1']
                            del action['endTime1']
                        action['office1'] = dayInfo[self.ciAmbOffice1]
                        action['plan1'] = dayInfo[self.ciAmbInterval1]
                        action['color1'] = dayInfo[self.ciAmbColor1]
                        timeRange2 = dayInfo[self.ciAmbTimeRange2]
                        if timeRange2:
                            action['begTime2'], action['endTime2'] = timeRange2
                        else:
                            del action['begTime2']
                            del action['endTime2']
                        action['office2'] = dayInfo[self.ciAmbOffice2]
                        action['plan2'] = dayInfo[self.ciAmbInterval2]
                        action['color2'] = dayInfo[self.ciAmbColor2]
                        action['fact'] = dayInfo[self.ciAmbFact]
                        action['time'] = dayInfo[self.ciAmbTime]
                        action['planInter'] = dayInfo[self.ciAmbInterInterval]
                        action['officeInter'] = dayInfo[self.ciAmbInterOffice]
                        action['colorInter'] = dayInfo[self.ciAmbInterColor]
                        if dayInfo[self.ciAmbTimesChange]:
                            if timeRange1 and timeRange2:
                                commonPlan = dayInfo[self.ciAmbPlan1]
                                result = calcTimeInterval(timeRange1, commonPlan, dayInfo[self.ciAmbInterval1], self.personId, True, result=[])
                                resultEx = [1 if dayInfo[self.ciNotExternalSystem1] else 0] * len(result)
                                if dayInfo[self.ciAmbInterInterval]:
                                    timeRangeInter = (timeRange1[1], timeRange2[0])
                                    commonPlan += dayInfo[self.ciAmbInterPlan]
                                    result = calcTimeInterval(timeRangeInter, commonPlan, dayInfo[self.ciAmbInterInterval], self.personId, True, result)
                                    resultEx = resultEx + [1 if dayInfo[self.ciInterNotExternalSystem] else 0] * (len(result) - len(resultEx))
                                commonPlan += dayInfo[self.ciAmbPlan2]
                                result = calcTimeInterval(timeRange2, commonPlan, dayInfo[self.ciAmbInterval2], self.personId, True, result)
                                resultEx = resultEx + [1 if dayInfo[self.ciNotExternalSystem2] else 0] * (len(result) - len(resultEx))
                            else:
                                result = calcTimeInterval(timeRange, dayInfo[self.ciAmbPlan], dayInfo[self.ciAmbInterval], self.personId, True, result=[])
                                resultEx = [1 if dayInfo[self.ciNotExternalSystem1] else 0] * len(result)
                            updateQueuedClient(action, result, date)
                            action['notExternalSystems'] = resultEx
                        colors = []
                        if dayInfo[self.ciAmbPlan1]:
                            col = dayInfo[self.ciAmbColor1]
                            colors.extend([col if col else ''] * dayInfo[self.ciAmbPlan1])
                        elif dayInfo[self.ciAmbPlan]:
                            col = dayInfo[self.ciAmbColor1]
                            colors.extend([col if col else ''] * dayInfo[self.ciAmbPlan])
                        if dayInfo[self.ciAmbInterPlan]:
                            col = dayInfo[self.ciAmbInterColor]
                            colors.extend([col if col else ''] * dayInfo[self.ciAmbInterPlan])
                        if dayInfo[self.ciAmbPlan2]:
                            col = dayInfo[self.ciAmbColor2]
                            colors.extend([col if col else ''] * dayInfo[self.ciAmbPlan2])
                        action['colors'] = colors
                        action['notExternalSystem1'] = dayInfo[self.ciNotExternalSystem1]
                        action['notExternalSystem2'] = dayInfo[self.ciNotExternalSystem2]
                        action['notExternalSystemInter'] = dayInfo[self.ciInterNotExternalSystem]

                        action.save(eventId)
                        #
                    if dayInfo[self.ciHomeChange]:
                        action = self.actionHome[day]
                        if not action:
                            action = CAction.createByTypeCode(constants.atcHome)
                            self.actionHome[day] = action
                        timeRange = dayInfo[self.ciHomeTimeRange]
                        if timeRange:
                            action['begTime'], action['endTime'] = timeRange
                        else:
                            del action['begTime']
                            del action['endTime']
                        action['plan'] = dayInfo[self.ciHomeInterval]
                        timeRange1 = dayInfo[self.ciHomeTimeRange1]
                        if timeRange1:
                            action['begTime1'], action['endTime1'] = timeRange1
                        else:
                            del action['begTime1']
                            del action['endTime1']
                        action['plan1'] = dayInfo[self.ciHomeInterval1]
                        timeRange2 = dayInfo[self.ciHomeTimeRange2]
                        if timeRange2:
                            action['begTime2'], action['endTime2'] = timeRange2
                        else:
                            del action['begTime2']
                            del action['endTime2']
                        action['plan2'] = dayInfo[self.ciHomeInterval2]
                        action['fact'] = dayInfo[self.ciHomeFact]
                        action['time'] = dayInfo[self.ciHomeTime]
                        if dayInfo[self.ciHomeTimesChange] or not action['times']:
                            if timeRange1 and timeRange2:
                                # result  = calcTimePlan(timeRange1, dayInfo[self.ciHomePlan1], self.personId, False, result = [])
                                # result  = calcTimePlan(timeRange2, dayInfo[self.ciHomePlan2], self.personId, False, result)
                                result = calcTimeInterval(timeRange1, dayInfo[self.ciHomePlan1], dayInfo[self.ciHomeInterval1], self.personId, True, result=[])
                                result = calcTimeInterval(timeRange2, dayInfo[self.ciHomePlan1] + dayInfo[self.ciHomePlan2], dayInfo[self.ciHomeInterval2], self.personId, True, result)
                            else:
                                result = calcTimeInterval(timeRange, dayInfo[self.ciHomePlan], dayInfo[self.ciHomeInterval], self.personId, True, result=[])
                            updateQueuedClient(action, result, date)
                        action.save(eventId)
                        #
                    if dayInfo[self.ciExpChange]:
                        action = self.actionExp[day]
                        if not action:
                            action = CAction.createByTypeCode(constants.atcExp)
                            self.actionExp[day] = action
                        timeRange = dayInfo[self.ciExpTimeRange]
                        if timeRange:
                            action['begTime'], action['endTime'] = timeRange
                        else:
                            del action['begTime']
                            del action['endTime']
                        action['office'] = dayInfo[self.ciExpOffice]
                        action['plan'] = dayInfo[self.ciExpPlan]
                        action['fact'] = dayInfo[self.ciExpPlan]
                        action['time'] = dayInfo[self.ciExpTime]
                        updateQueuedClient(action, calcTimePlan(timeRange, dayInfo[self.ciExpPlan], self.personId, False, result=[]), date)
                        action.save(eventId)

                    if dayInfo[self.ciTimeLineChange]:
                        action = self.actionTimeLine[day]
                        if not action:
                            action = CAction.createByTypeCode(constants.atcTimeLine)
                            self.actionTimeLine[day] = action
                        action['otherTime'] = dayInfo[self.ciOtherTime]
                        action['factTime'] = dayInfo[self.ciFactTime]
                        action['reasonOfAbsence'] = dayInfo[self.ciReasonOfAbsence]
                        action.save(eventId)
                db.commit()
            except:
                db.rollback()
                QtGui.qApp.logCurrentException()
                raise

    def conversion(self, timeRange, value):
        if timeRange:
            timeStart, timeFinish = timeRange
            diffTime = abs(timeFinish.secsTo(timeStart) / 60)
        else:
            return 0
        if value:
            return diffTime / value
        else:
            return 0

    def getOutTurnTime(self, ambTimeRange1, ambTimeRange2):
        if ambTimeRange1 and ambTimeRange2:
            return ambTimeRange1[1], ambTimeRange2[0]
        return None

    def loadData(self, personId, year, month):
        self.personId = personId
        self.year = year
        self.month = month
        self.begDate = QtCore.QDate(year, month, 1)
        self.daysInMonth = self.begDate.daysInMonth()
        self.redDays = []
        holidayList, changedayList, dayFromDateList = CCalendarExceptionList().loadYearMonth(year, month)
        for day in xrange(self.daysInMonth):
            self.redDays.append(((QtCore.QDate(year, month, day+1).dayOfWeek() in [QtCore.Qt.Saturday, QtCore.Qt.Sunday]) and ((day+1) not in dayFromDateList)) or ((day+1) in holidayList) or ((day+1) in changedayList))
        self.items = []
        self.events = [None] * self.daysInMonth
        self.actionTimeLine = [None] * self.daysInMonth
        self.actionAmbulance = [None] * self.daysInMonth
        self.actionHome = [None] * self.daysInMonth
        self.actionExp = [None] * self.daysInMonth

        for day in xrange(self.daysInMonth):
            dayInfo = [None] * CTimeTableModel.numCols
            self.items.append(dayInfo)

        if self.personId:
            for day in xrange(self.daysInMonth):
                black = not self.redDays[day]
                dayInfo = self.items[day]
                event = getEvent(constants.etcTimeTable, self.begDate.addDays(day), self.personId)
                self.events[day] = event
                eventId = forceRef(event.value('id'))
                if eventId:
                    action = CAction.getAction(eventId, constants.atcAmbulance)
                    self.actionAmbulance[day] = action
                    oldVersion = True if (len(action['times']) == action['plan']) else False
                    begTime1 = action['begTime1']
                    endTime1 = action['endTime1']
                    if begTime1 and endTime1:
                        dayInfo[self.ciAmbTimeRange1] = (begTime1, endTime1)
                    else:
                        dayInfo[self.ciAmbTimeRange1] = None
                    dayInfo[self.ciAmbOffice1] = action['office1']
                    dayInfo[self.ciAmbPlan1] = action['plan1'] if oldVersion else self.conversion(dayInfo[self.ciAmbTimeRange1], action['plan1'])
                    dayInfo[self.ciAmbInterval1] = self.conversion(dayInfo[self.ciAmbTimeRange1], action['plan1']) if oldVersion else action['plan1']
                    dayInfo[self.ciAmbColor1] = action['color1']
                    begTime2 = action['begTime2']
                    endTime2 = action['endTime2']
                    if begTime2 and endTime2:
                        dayInfo[self.ciAmbTimeRange2] = (begTime2, endTime2)
                    else:
                        dayInfo[self.ciAmbTimeRange2] = None
                    dayInfo[self.ciAmbOffice2] = action['office2']
                    dayInfo[self.ciAmbPlan2] = action['plan2'] if oldVersion else self.conversion(dayInfo[self.ciAmbTimeRange2], action['plan2'])
                    dayInfo[self.ciAmbInterval2] = self.conversion(dayInfo[self.ciAmbTimeRange2], action['plan2']) if oldVersion else action['plan2']
                    dayInfo[self.ciAmbColor2] = action['color2']
                    begTime = action['begTime']
                    endTime = action['endTime']
                    if begTime and endTime:
                        dayInfo[self.ciAmbTimeRange] = (begTime, endTime)
                    else:
                        dayInfo[self.ciAmbTimeRange] = None
                    dayInfo[self.ciAmbOffice] = action['office']
                    dayInfo[self.ciAmbPlan] = len(action['times'])
                    if oldVersion:
                        dayInfo[self.ciAmbInterval] = self.conversion(dayInfo[self.ciAmbTimeRange], len(action['times'])) if not action['plan'] else self.conversion(dayInfo[self.ciAmbTimeRange],
                                                                                                                                                                     action['plan']) if not action[
                            'plan1'] else  setInterval(self.conversion(dayInfo[self.ciAmbTimeRange1], action['plan1']), self.conversion(dayInfo[self.ciAmbTimeRange2], action['plan2']),
                                                       self.conversion(self.getOutTurnTime(dayInfo[self.ciAmbTimeRange1], dayInfo[self.ciAmbTimeRange2]), action['planInter']))
                    else:
                        dayInfo[self.ciAmbInterval] = self.conversion(dayInfo[self.ciAmbTimeRange], len(action['times'])) if not action['plan'] else action['plan'] if not action[
                            'plan1'] else setInterval(action['plan1'], action['plan2'], action['planInter'])
                    dayInfo[self.ciAmbColor] = action['color']
                    dayInfo[self.ciAmbInterOffice] = action['officeInter']
                    dayInfo[self.ciAmbInterPlan] = self.conversion((endTime1, begTime2) if endTime1 and begTime2 else None, action['planInter'])
                    dayInfo[self.ciAmbInterInterval] = action['planInter']
                    dayInfo[self.ciAmbInterColor] = action['colorInter']
                    dayInfo[self.ciAmbTime] = action['time']
                    dayInfo[self.ciAmbFact] = action['fact']
                    dayInfo[self.ciAmbChange] = False
                    dayInfo[self.ciAmbTimesChange] = False
                    dayInfo[self.ciNotExternalSystem1] = forceBool(action['notExternalSystem1'])
                    dayInfo[self.ciNotExternalSystem2] = forceBool(action['notExternalSystem2'])
                    dayInfo[self.ciInterNotExternalSystem] = forceBool(action['notExternalSystemInter'])

                    action = CAction.getAction(eventId, constants.atcHome)
                    self.actionHome[day] = action
                    oldVersion = True if (len(action['times']) == action['plan']) else False
                    begTime1 = action['begTime1']
                    endTime1 = action['endTime1']
                    if begTime1 and endTime1:
                        dayInfo[self.ciHomeTimeRange1] = (begTime1, endTime1)
                    else:
                        dayInfo[self.ciHomeTimeRange1] = None
                    dayInfo[self.ciHomePlan1] = action['plan1'] if oldVersion else self.conversion(dayInfo[self.ciHomeTimeRange1], action['plan1'] if action['plan1'] else len(action['times']))
                    dayInfo[self.ciHomeInterval1] = self.conversion(dayInfo[self.ciHomeTimeRange1], action['plan1']) if oldVersion else  action['plan1']
                    begTime2 = action['begTime2']
                    endTime2 = action['endTime2']
                    if begTime2 and endTime2:
                        dayInfo[self.ciHomeTimeRange2] = (begTime2, endTime2)
                    else:
                        dayInfo[self.ciHomeTimeRange2] = None
                    dayInfo[self.ciHomePlan2] = action['plan2'] if oldVersion else self.conversion(dayInfo[self.ciHomeTimeRange2], action['plan2'])
                    dayInfo[self.ciHomeInterval2] = self.conversion(dayInfo[self.ciHomeTimeRange2], action['plan2']) if oldVersion else action['plan2']
                    begTime = action['begTime']
                    endTime = action['endTime']
                    if begTime and endTime:
                        dayInfo[self.ciHomeTimeRange] = (begTime, endTime)
                    else:
                        dayInfo[self.ciHomeTimeRange] = None
                    dayInfo[self.ciHomePlan] = len(action['times'])
                    if oldVersion:
                        dayInfo[self.ciHomeInterval] = self.conversion(dayInfo[self.ciHomeTimeRange], len(action['times'])) if not action['plan'] else self.conversion(dayInfo[self.ciHomeTimeRange],
                                                                                                                                                                       action['plan']) if not action[
                            'plan1'] else  setInterval(self.conversion(dayInfo[self.ciHomeTimeRange1], action['plan1']), self.conversion(dayInfo[self.ciHomeTimeRange2], action['plan2']))
                    else:
                        dayInfo[self.ciHomeInterval] = self.conversion(dayInfo[self.ciHomeTimeRange], len(action['times'])) if not action['plan'] else action['plan'] if not action[
                            'plan1'] else setInterval(action['plan1'], action['plan2'])
                    dayInfo[self.ciHomeTime] = action['time']
                    dayInfo[self.ciHomeFact] = action['fact']
                    dayInfo[self.ciHomeChange] = False
                    dayInfo[self.ciHomeTimesChange] = False

                    action = CAction.getAction(eventId, constants.atcExp)
                    self.actionExp[day] = action
                    begTime = action['begTime']
                    endTime = action['endTime']
                    if begTime and endTime:
                        dayInfo[self.ciExpTimeRange] = (begTime, endTime)
                    else:
                        dayInfo[self.ciExpTimeRange] = None
                    dayInfo[self.ciExpOffice] = action['office']
                    dayInfo[self.ciExpPlan] = action['plan']
                    dayInfo[self.ciExpTime] = action['time']
                    dayInfo[self.ciExpFact] = action['fact']

                    action = CAction.getAction(eventId, constants.atcTimeLine)
                    self.actionTimeLine[day] = action
                    dayInfo[self.ciOtherTime] = action['otherTime']
                    dayInfo[self.ciFactTime] = action['factTime']
                    dayInfo[self.ciReasonOfAbsence] = action['reasonOfAbsence']

        self.items.append([0] * CTimeTableModel.numCols)
        for column in xrange(CTimeTableModel.numCols):
            self.updateSums(column, False)
        self.reset()
        self.updateAttrs()

    def setWorkPlanOnRotation(self, plan, selectedDaysList):
        (daysPlan, setRedDays) = plan
        daysPlanLen = len(daysPlan)
        if daysPlanLen <= 2:
            for day in selectedDaysList:
                if setRedDays or not self.redDays[day - 1]:
                    dayPlan = daysPlan[day % daysPlanLen]
                    self.setDayPlan(day - 1, dayPlan)
        for column in (
        self.ciAmbTimeRange, self.ciAmbOffice, self.ciAmbPlan, self.ciAmbInterval, self.ciHomeTimeRange, self.ciHomePlan, self.ciHomeInterval, self.ciExpTimeRange, self.ciExpOffice, self.ciExpPlan,
        self.ciAmbInterOffice, self.ciAmbInterPlan, self.ciAmbInterInterval):
            self.updateSums(column)
        self.updateAttrs()

    def setWorkPlan(self, plan, dateRange=None):
        if dateRange:
            (begDate, endDate) = dateRange
        else:
            (begDate, endDate) = None, None

        if not begDate:
            begDate = self.begDate
        if not endDate:
            endDate = self.begDate.addDays(self.daysInMonth - 1)

        for currentYear in xrange(begDate.year(), endDate.year() + 1):
            startMonth = begDate.month() if currentYear == begDate.year() else 1
            endMonth = endDate.month() if currentYear == endDate.year() else 12
            for currentMonth in xrange(startMonth, endMonth + 1):
                self.setPersonAndMonth(self.personId, currentYear, currentMonth, self.selectedDate)

                startDay = self.begDate.daysTo(begDate if (begDate.month() == currentMonth and begDate.year() == currentYear) \
                                                            else self.begDate
                                                )
                endDay =   self.begDate.daysTo(endDate) if (endDate.month() == currentMonth and endDate.year() == currentYear) \
                                                            else self.daysInMonth - 1

                (daysPlan, setRedDays) = plan
                daysPlanLen = len(daysPlan)
                if daysPlanLen <= 2:
                    for day in xrange(startDay, endDay + 1):
                        if setRedDays or not self.redDays[day]:
                            dayPlan = daysPlan[day % daysPlanLen]
                            self.setDayPlan(day, dayPlan)
                elif daysPlanLen == 5:
                    for day in xrange(startDay, endDay + 1):
                        if setRedDays or not self.redDays[day]:
                            dow = self.begDate.addDays(day).dayOfWeek()
                            if dow < 6:
                                dayPlan = daysPlan[dow - 1]
                                self.setDayPlan(day, dayPlan)
                elif daysPlanLen == 7:
                    for day in xrange(startDay, endDay + 1):
                        dow = self.begDate.addDays(day).dayOfWeek()
                        dayPlan = daysPlan[dow - 1]
                        self.setDayPlan(day, dayPlan)
                for column in (self.ciAmbTimeRange, self.ciAmbOffice, self.ciAmbPlan, self.ciAmbInterval, self.ciHomeTimeRange, self.ciHomePlan, self.ciHomeInterval, self.ciExpTimeRange, self.ciExpOffice, self.ciExpPlan):
                    self.updateSums(column)
                self.updateAttrs()
        self.setPersonAndMonth(self.personId, self.selectedDate.year(), self.selectedDate.month(), self.selectedDate)

    def setDayPlan(self, day, dayPlan):
        (ambPlan, homePlan, expPlan, reasonOfAbsenceId, notExternalSystem1, notExternalSystem2, notExternalSystemInter) = dayPlan
        dayInfo = self.items[day]
        self.setTaskPlan(day, ambPlan,  dayInfo, (self.ciAmbTimeRange,  self.ciAmbOffice, self.ciAmbPlan, self.ciAmbInterval, self.ciAmbColor, self.ciAmbTimeRange1,  self.ciAmbOffice1, self.ciAmbPlan1, self.ciAmbInterval1, self.ciAmbColor1, self.ciAmbTimeRange2,  self.ciAmbOffice2, self.ciAmbPlan2, self.ciAmbInterval2, self.ciAmbColor2, self.ciAmbInterOffice, self.ciAmbInterPlan, self.ciAmbInterInterval, self.ciAmbInterColor))
        self.setTaskPlan(day, homePlan, dayInfo, (self.ciHomeTimeRange, -1, self.ciHomePlan, self.ciHomeInterval, -1, self.ciHomeTimeRange1, -1, self.ciHomePlan1, self.ciHomeInterval1, -1, self.ciHomeTimeRange2, -1, self.ciHomePlan2, self.ciHomeInterval2, -1, -1, -1, -1))
        self.setTaskPlan(day, expPlan,  dayInfo, (self.ciExpTimeRange,  self.ciExpOffice, self.ciExpPlan, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1))
        if dayInfo[self.ciReasonOfAbsence] != reasonOfAbsenceId and reasonOfAbsenceId is not None:
            dayInfo[self.ciReasonOfAbsence] = reasonOfAbsenceId
            self.emitCellChanged(day, self.ciReasonOfAbsence)
            dayInfo[self.ciTimeLineChange] = True
        dayInfo[self.ciAmbChange] = True
        dayInfo[self.ciAmbTimesChange] = True
        dayInfo[self.ciHomeChange] = True
        dayInfo[self.ciHomeTimesChange] = True
        dayInfo[self.ciNotExternalSystem1] = notExternalSystem1
        dayInfo[self.ciNotExternalSystem2] = notExternalSystem2
        dayInfo[self.ciInterNotExternalSystem] = notExternalSystemInter

    def setTaskPlan(self, day, plan, dayInfo, columns):
        for i in xrange(len(columns)):
            column = columns[i]
            value = plan[i]
            if column >= 0:
                if dayInfo[column] != value:
                    dayInfo[column] = value
                    self.emitCellChanged(day, column)

    def setTaskPlanSecondPeriod(self, day, data):
        # TODO:
        dayInfo = self.items[day]
        if dayInfo[self.ciAmbTimeRange1] != data[0]:
            dayInfo[self.ciAmbTimeRange1] = data[0]
            self.emitCellChanged(day, self.ciAmbTimeRange1)
        if dayInfo[self.ciAmbOffice1] != data[1]:
            dayInfo[self.ciAmbOffice1] = data[1]
            self.emitCellChanged(day, self.ciAmbOffice1)
        if dayInfo[self.ciAmbPlan1] != data[2]:
            dayInfo[self.ciAmbPlan1] = data[2]
            self.emitCellChanged(day, self.ciAmbPlan1)
        if dayInfo[self.ciAmbInterval1] != data[3]:
            dayInfo[self.ciAmbInterval1] = data[3]
            self.emitCellChanged(day, self.ciAmbInterval1)
        if dayInfo[self.ciAmbColor1] != data[4]:
            dayInfo[self.ciAmbColor1] = data[4]
            self.emitCellChanged(day, self.ciAmbColor1)
        if dayInfo[self.ciAmbTimeRange2] != data[5]:
            dayInfo[self.ciAmbTimeRange2] = data[5]
            self.emitCellChanged(day, self.ciAmbTimeRange2)
        if dayInfo[self.ciAmbOffice2] != data[6]:
            dayInfo[self.ciAmbOffice2] = data[6]
            self.emitCellChanged(day, self.ciAmbOffice2)
        if dayInfo[self.ciAmbPlan2] != data[7]:
            dayInfo[self.ciAmbPlan2] = data[7]
            self.emitCellChanged(day, self.ciAmbPlan2)
        if dayInfo[self.ciAmbInterval2] != data[8]:
            dayInfo[self.ciAmbInterval2] = data[8]
            self.emitCellChanged(day, self.ciAmbInterval2)
        if dayInfo[self.ciAmbColor2] != data[9]:
            dayInfo[self.ciAmbColor2] = data[9]
            self.emitCellChanged(day, self.ciAmbColor2)
        if dayInfo[self.ciHomeTimeRange1] != data[10]:
            dayInfo[self.ciHomeTimeRange1] = data[10]
            self.emitCellChanged(day, self.ciHomeTimeRange1)
        if dayInfo[self.ciHomePlan1] != data[11]:
            dayInfo[self.ciHomePlan1] = data[11]
            self.emitCellChanged(day, self.ciHomePlan1)
        if dayInfo[self.ciHomeInterval1] != data[12]:
            dayInfo[self.ciHomeInterval1] = data[12]
            self.emitCellChanged(day, self.ciHomeInterval1)
        if dayInfo[self.ciHomeTimeRange2] != data[13]:
            dayInfo[self.ciHomeTimeRange2] = data[13]
            self.emitCellChanged(day, self.ciHomeTimeRange2)
        if dayInfo[self.ciHomePlan2] != data[14]:
            dayInfo[self.ciHomePlan2] = data[14]
            self.emitCellChanged(day, self.ciHomePlan2)
        if dayInfo[self.ciHomeInterval2] != data[15]:
            dayInfo[self.ciHomeInterval2] = data[15]
            self.emitCellChanged(day, self.ciHomeInterval2)
        if dayInfo[self.ciAmbTimeRange] != data[16]:
            dayInfo[self.ciAmbTimeRange] = data[16]
            self.emitCellChanged(day, self.ciAmbTimeRange)
        if dayInfo[self.ciAmbOffice] != data[17]:
            dayInfo[self.ciAmbOffice] = data[17]
            self.emitCellChanged(day, self.ciAmbOffice)
        if dayInfo[self.ciAmbPlan] != data[18]:
            dayInfo[self.ciAmbPlan] = data[18]
            self.emitCellChanged(day, self.ciAmbPlan)
        if dayInfo[self.ciAmbInterval] != data[19]:
            dayInfo[self.ciAmbInterval] = data[19]
            self.emitCellChanged(day, self.ciAmbInterval)
        if dayInfo[self.ciAmbColor] != data[20]:
            dayInfo[self.ciAmbColor] = data[20]
            self.emitCellChanged(day, self.ciAmbColor)
        if dayInfo[self.ciHomeTimeRange] != data[21]:
            dayInfo[self.ciHomeTimeRange] = data[21]
            self.emitCellChanged(day, self.ciHomeTimeRange)
        if dayInfo[self.ciHomePlan] != data[22]:
            dayInfo[self.ciHomePlan] = data[22]
            self.emitCellChanged(day, self.ciHomePlan)
        if dayInfo[self.ciHomeInterval] != data[23]:
            dayInfo[self.ciHomeInterval] = data[23]
            self.emitCellChanged(day, self.ciHomeInterval)
        if dayInfo[self.ciAmbInterOffice] != data[24]:
            dayInfo[self.ciAmbInterOffice] = data[24]
            self.emitCellChanged(day, self.ciAmbInterOffice)
        if dayInfo[self.ciAmbInterPlan] != data[25]:
            dayInfo[self.ciAmbInterPlan] = data[25]
            self.emitCellChanged(day, self.ciAmbInterPlan)
        if dayInfo[self.ciAmbInterInterval] != data[26]:
            dayInfo[self.ciAmbInterInterval] = data[26]
            self.emitCellChanged(day, self.ciAmbInterInterval)
        if dayInfo[self.ciAmbInterColor] != data[27]:
            dayInfo[self.ciAmbInterColor] = data[27]
            self.emitCellChanged(day, self.ciAmbInterColor)
        if dayInfo[self.ciNotExternalSystem1] != data[28]:
            dayInfo[self.ciNotExternalSystem1] = data[28]
        if dayInfo[self.ciNotExternalSystem2] != data[29]:
            dayInfo[self.ciNotExternalSystem2] = data[29]
        if dayInfo[self.ciInterNotExternalSystem] != data[30]:
            dayInfo[self.ciInterNotExternalSystem] = data[30]
        dayInfo[self.ciAmbChange] = True
        dayInfo[self.ciAmbTimesChange] = True
        dayInfo[self.ciHomeChange] = True
        dayInfo[self.ciHomeTimesChange] = True

    def setWorkPlanTemplates(self, plan, dateRange=None):
        self.dayInfoPersons = []
        for day in xrange(self.daysInMonth):
            self.dayInfoPersons.append([None] * (CTimeTableModel.numCols - 1))

        if dateRange:
            (begDate, endDate) = dateRange
        else:
            (begDate, endDate) = None, None

        if not begDate:
            begDate = self.begDate
        if not endDate:
            endDate = self.begDate.addDays(self.daysInMonth - 1)

        (daysPlan, setRedDays) = plan
        daysPlanLen = len(daysPlan)
        if daysPlanLen <= 2:
            for day in xrange(self.begDate.daysTo(begDate), self.begDate.daysTo(endDate) + 1):
                if setRedDays or not self.redDays[day]:
                    dayPlan = daysPlan[day % daysPlanLen]
                    self.setDayPlanTemplates(day, dayPlan)
        elif daysPlanLen == 5:
            for day in xrange(self.begDate.daysTo(begDate), self.begDate.daysTo(endDate) + 1):
                if setRedDays or not self.redDays[day]:
                    dow = self.begDate.addDays(day).dayOfWeek()
                    if dow < 6:
                        dayPlan = daysPlan[dow - 1]
                        self.setDayPlanTemplates(day, dayPlan)
        elif daysPlanLen == 7:
            for day in xrange(self.begDate.daysTo(begDate), self.begDate.daysTo(endDate) + 1):
                dow = self.begDate.addDays(day).dayOfWeek()
                dayPlan = daysPlan[dow - 1]
                self.setDayPlanTemplates(day, dayPlan)

    def setDayPlanTemplates(self, day, dayPlan):
        (ambPlan, homePlan, expPlan, reasonOfAbsenceId) = dayPlan
        dayInfo = self.dayInfoPersons[day]
        self.setTaskPlanTemplates(day, ambPlan,  dayInfo, (self.ciAmbTimeRange,  self.ciAmbOffice, self.ciAmbPlan, self.ciAmbTimeRange1,  self.ciAmbOffice1, self.ciAmbPlan1, self.ciAmbTimeRange2,  self.ciAmbOffice2, self.ciAmbPlan2, self.ciAmbInterOffice, self.ciAmbInterPlan))
        self.setTaskPlanTemplates(day, homePlan, dayInfo, (self.ciHomeTimeRange, -1, self.ciHomePlan, self.ciHomeTimeRange1, -1, self.ciHomePlan1, self.ciHomeTimeRange2, -1, self.ciHomePlan2, -1, -1))
        self.setTaskPlanTemplates(day, expPlan, dayInfo, (self.ciExpTimeRange, self.ciExpOffice, self.ciExpPlan, -1, -1, -1, -1, -1, -1, -1, -1))
        if dayInfo[self.ciReasonOfAbsence] != reasonOfAbsenceId and reasonOfAbsenceId is not None:
            dayInfo[self.ciReasonOfAbsence] = reasonOfAbsenceId

    def setTaskPlanTemplates(self, day, plan, dayInfo, columns):
        for i in xrange(11):
            column = columns[i]
            value = plan[i]
            if column >= 0:
                if dayInfo[column] != value:
                    dayInfo[column] = value

    def setWorkPlanPerson(self, dateRange, redDaysPerson, ambSecondPeriodPerson, homeSecondPeriodPerson, ambInterPeriodPerson, personId=None, selectPersons=False):
        self.dayInfoPersons = []
        if personId:
            if selectPersons:
                for day in xrange(self.daysInMonth):
                    self.dayInfoPersons.append([None] * (CTimeTableModel.numCols - 1))
            db = QtGui.qApp.db
            tablePerson = db.table('Person')
            table = db.table('Person_TimeTemplate')
            records = db.getRecordList(table, '*', [table['master_id'].eq(personId)], 'idx')
            if len(records) > 0:
                recordPerson = db.getRecordEx(tablePerson, tablePerson['typeTimeLinePerson'], [tablePerson['id'].eq(personId), tablePerson['deleted'].eq(0)])
                typeTimeLinePerson = forceInt(recordPerson.value('typeTimeLinePerson'))
                if dateRange:
                    (begDate, endDate) = dateRange
                else:
                    (begDate, endDate) = None, None
                if not begDate:
                    begDate = self.begDate
                if not endDate:
                    endDate = self.begDate.addDays(self.daysInMonth - 1)
                datas = []
                if typeTimeLinePerson == 0:
                    rangeTypeLine = 1
                elif typeTimeLinePerson == 1:
                    rangeTypeLine = 2
                else:
                    rangeTypeLine = (typeTimeLinePerson - 1) * 7
                datas.extend([[None] * (CTimeTableModel.numCols - 1) for i in range(rangeTypeLine)])
                redDays = []
                redDays.append([None] * (CTimeTableModel.numCols - 1))
                datasLen = len(datas)
                if typeTimeLinePerson < 2:
                    for record in records:
                        idx = forceInt(record.value('idx'))
                        if idx < datasLen:
                            self.getDatas(idx, datas, record, ambSecondPeriodPerson, homeSecondPeriodPerson, ambInterPeriodPerson)
                    for day in xrange(self.begDate.daysTo(begDate), self.begDate.daysTo(endDate) + 1):
                        if not redDaysPerson:
                            if self.begDate.addDays(day).dayOfWeek() not in [6, 7]:
                                if selectPersons:
                                    self.setTaskPlanForPersonsTemplate(day, datas[day % datasLen])
                                else:
                                    self.setTaskPlanForPersonTemplate(day, datas[day % datasLen])
                            else:
                                if selectPersons:
                                    self.setTaskPlanForPersonsTemplate(day, redDays[0])
                                else:
                                    self.setTaskPlanForPersonTemplate(day, redDays[0])
                        else:
                            if selectPersons:
                                self.setTaskPlanForPersonsTemplate(day, datas[day % datasLen])
                            else:
                                self.setTaskPlanForPersonTemplate(day, datas[day % datasLen])
                elif typeTimeLinePerson == 2:
                    for record in records:
                        idx = forceInt(record.value('idx'))
                        if idx < datasLen:
                            self.getDatas(idx, datas, record, ambSecondPeriodPerson, homeSecondPeriodPerson, ambInterPeriodPerson)
                    for day in xrange(self.begDate.daysTo(begDate), self.begDate.daysTo(endDate) + 1):
                        dow = self.begDate.addDays(day).dayOfWeek()
                        if not redDaysPerson:
                            if dow not in [6, 7]:
                                if selectPersons:
                                    self.setTaskPlanForPersonsTemplate(day, datas[dow - 1])
                                else:
                                    self.setTaskPlanForPersonTemplate(day, datas[dow - 1])
                            else:
                                if selectPersons:
                                    self.setTaskPlanForPersonsTemplate(day, redDays[0])
                                else:
                                    self.setTaskPlanForPersonTemplate(day, redDays[0])
                        else:
                            if selectPersons:
                                self.setTaskPlanForPersonsTemplate(day, datas[dow - 1])
                            else:
                                self.setTaskPlanForPersonTemplate(day, datas[dow - 1])
                else:
                    for record in records:
                        idx = forceInt(record.value('idx'))
                        if idx < datasLen:
                            self.getDatas(idx, datas, record, ambSecondPeriodPerson, homeSecondPeriodPerson, ambInterPeriodPerson)
                    week = 0
                    for day in xrange(self.begDate.daysTo(begDate), self.begDate.daysTo(endDate) + 1):
                        if week >= (typeTimeLinePerson - 1):
                            week = 0
                        dow = self.begDate.addDays(day).dayOfWeek()
                        dowNew = (dow - 1) + (7 * week)
                        if dow == 7:
                            week += 1
                        if not redDaysPerson:
                            if dow not in [6, 7, 13, 14, 20, 21, 27, 28]:
                                if selectPersons:
                                    self.setTaskPlanForPersonsTemplate(day, datas[dowNew])
                                else:
                                    self.setTaskPlanForPersonTemplate(day, datas[dowNew])
                            else:
                                if selectPersons:
                                    self.setTaskPlanForPersonsTemplate(day, redDays[0])
                                else:
                                    self.setTaskPlanForPersonTemplate(day, redDays[0])
                        else:
                            if selectPersons:
                                self.setTaskPlanForPersonsTemplate(day, datas[dowNew])
                            else:
                                self.setTaskPlanForPersonTemplate(day, datas[dowNew])
                if not selectPersons:
                    for column in (self.ciAmbTimeRange, self.ciAmbOffice, self.ciAmbPlan, self.ciAmbInterval, self.ciHomeTimeRange, self.ciHomePlan, self.ciHomeInterval, self.ciExpTimeRange, self.ciExpOffice, self.ciExpPlan):
                        self.updateSums(column)
                    self.updateAttrs()

    def getDatas(self, i, datas, record, ambSecondPeriodPerson, homeSecondPeriodPerson, ambInterPeriodPerson):
        ambBegTime = forceTime(record.value('ambBegTime'))
        ambEndTime = forceTime(record.value('ambEndTime'))
        datas[i][self.ciAmbTimeRange] = None if (ambBegTime.isNull() and ambEndTime.isNull()) else (ambBegTime, ambEndTime)
        datas[i][self.ciAmbOffice] = forceString(record.value('office'))
        datas[i][self.ciAmbPlan] = forceInt(record.value('ambPlan'))
        datas[i][self.ciAmbInterval] = forceInt(record.value('ambInterval'))
        datas[i][self.ciAmbColor] = forceString(record.value('ambColor'))
        if ambSecondPeriodPerson:
            ambBegTime2 = forceTime(record.value('ambBegTime2'))
            ambEndTime2 = forceTime(record.value('ambEndTime2'))
            datas[i][self.ciAmbTimeRange2] = None if (ambBegTime2.isNull() and ambEndTime2.isNull())else (ambBegTime2, ambEndTime2)
            datas[i][self.ciAmbOffice2] = forceString(record.value('office2'))
            datas[i][self.ciAmbPlan2] = forceInt(record.value('ambPlan2'))
            datas[i][self.ciAmbInterval2] = forceInt(record.value('ambInterval2'))
            datas[i][self.ciAmbColor2] = forceString(record.value('ambColor2'))
            if ambInterPeriodPerson:
                datas[i][self.ciAmbInterOffice] = forceString(record.value('officeInter'))
                datas[i][self.ciAmbInterPlan] = forceInt(record.value('ambPlanInter'))
                datas[i][self.ciAmbInterInterval] = forceInt(record.value('ambInterInterval'))
                datas[i][self.ciAmbInterColor] = forceString(record.value('ambColorInter'))
        homBegTime = forceTime(record.value('homBegTime'))
        homEndTime = forceTime(record.value('homEndTime'))
        datas[i][self.ciHomeTimeRange] = None if (homBegTime.isNull() and homEndTime.isNull()) else (homBegTime, homEndTime)
        datas[i][self.ciHomePlan] = forceInt(record.value('homPlan'))
        datas[i][self.ciHomePlan] = forceInt(record.value('homInterval'))
        if homeSecondPeriodPerson:
            homBegTime2 = forceTime(record.value('homBegTime2'))
            homEndTime2 = forceTime(record.value('homEndTime2'))
            datas[i][self.ciHomeTimeRange2] = None if (homBegTime2.isNull() and homEndTime2.isNull()) else (homBegTime2, homEndTime2)
            datas[i][self.ciHomePlan2] = forceInt(record.value('homPlan2'))
            datas[i][self.ciHomePlan2] = forceInt(record.value('homInterval2'))
        return datas

    # дурацкие имена переменных
    def getTaskPlanPerson(self, edtTimeRange, edtOffice, edtPlan, edtInterval, btnColor, edtTimeRange2, edtOffice2, edtPlan2, edtInterval2, btnColor2, edtOfficeInter, edtInterPlan, edtInterInterval,
                          btnColorInter):
        if edtTimeRange2:
            timeRange2 = edtTimeRange2
            if timeRange2:
                timeStart2, timeFinish2 = timeRange2
            else:
                timeStart2 = None
                timeFinish2 = None
            timeRange1 = edtTimeRange if edtTimeRange else None
            if timeRange1:
                timeStart, timeFinish = timeRange1
            else:
                timeStart = None
                timeFinish = None

            timeRangeStart = min(timeStart, timeStart2) if (timeStart and timeStart2) else (timeStart if timeStart else (timeStart2 if timeStart2 else None))
            timeRangeFinish = max(timeFinish, timeFinish2) if (timeFinish and timeFinish2) else (timeFinish if timeFinish else (timeFinish2 if timeFinish2 else None))
            if timeRangeStart and timeRangeFinish:
                timeRange = timeRangeStart, timeRangeFinish
            else:
                timeRange = None
        else:
            timeRange2 = None
            timeRange1 = None
            timeRange = edtTimeRange if edtTimeRange else None

        if edtOffice2:
            office2 = forceStringEx(edtOffice2) if edtOffice2 else None
            office1 = forceStringEx(edtOffice) if edtOffice else None
            if edtOfficeInter:
                officeInter = forceString(edtOfficeInter)
                office = office1 + u', ' + officeInter + u', ' + office2
            else:
                officeInter = None
                office = office1 + u', ' + office2
        else:
            office2 = None
            office1 = None
            officeInter = None
            office = forceStringEx(edtOffice) if edtOffice else None

        if edtPlan2:
            plan2 = edtPlan2 if edtPlan2 else 0
            interval2 = edtInterval2 if edtInterval2 else 0
            plan1 = edtPlan if edtPlan else 0
            interval1 = edtInterval if edtInterval else 0
            if edtInterPlan:
                interPlan = edtInterPlan
                interInterval = edtInterInterval if edtInterInterval else 0
                plan = plan1 + plan2 + interPlan
                interval = forceString(interval1) + u',' + forceString(interInterval) + u',' + forceString(interval2)
            else:
                interPlan = None
                interInterval = None
                plan = plan1 + plan2
                interval = forceString(interval1) + u',' + forceString(interval2)
        else:
            plan2 = None
            interval2 = None
            plan1 = None
            interval1 = None
            interPlan = None
            interInterval = None
            plan = edtPlan if edtPlan else None
            interval = edtInterval if edtInterval else 0

        color2 = btnColor2
        color1 = btnColor
        colorInter = btnColorInter
        color = btnColor

        return (timeRange, office, plan, interval, color, timeRange1, office1, plan1, interval1, color1, timeRange2, office2, plan2, interval2, color2, officeInter, interPlan, interInterval, colorInter)


    def setTaskPlanForPersonTemplate(self, day, data):
        ambTimeRange, ambOffice, ambPlan, ambInterval, ambColor, ambTimeRange1, ambOffice1, ambPlan1, ambInterval1, ambColor1, ambTimeRange2, ambOffice2, ambPlan2, ambInterval2, ambColor2, ambOfficeInter, ambInterPlan, ambInterInterval, ambInterColor = self.getTaskPlanPerson(data[CTimeTableModel.ciAmbTimeRange], data[CTimeTableModel.ciAmbOffice], data[CTimeTableModel.ciAmbPlan], data[CTimeTableModel.ciAmbInterval], data[CTimeTableModel.ciAmbColor], data[CTimeTableModel.ciAmbTimeRange2], data[CTimeTableModel.ciAmbOffice2], data[CTimeTableModel.ciAmbPlan2], data[CTimeTableModel.ciAmbInterval2], data[CTimeTableModel.ciAmbColor2], data[CTimeTableModel.ciAmbInterOffice], data[CTimeTableModel.ciAmbInterPlan], data[CTimeTableModel.ciAmbInterInterval], data[CTimeTableModel.ciAmbInterColor])
        homTimeRange, homOffice, homPlan, homInterval, homColor, homTimeRange1, homOffice1, homPlan1, homInterval1, homColor1, homTimeRange2, homOffice2, homPlan2, homInterval2, homColor2, homOfficeInter, homInterPlan, homInterInterval, homInterColor = self.getTaskPlanPerson(data[CTimeTableModel.ciHomeTimeRange], None, data[CTimeTableModel.ciHomePlan], data[CTimeTableModel.ciHomeInterval], None, data[CTimeTableModel.ciHomeTimeRange2], None, data[CTimeTableModel.ciHomePlan2], data[CTimeTableModel.ciHomeInterval2], None, None, None, None, None)
        dayInfo = self.items[day]
        if dayInfo[self.ciAmbTimeRange1] != ambTimeRange1:
            dayInfo[self.ciAmbTimeRange1] = ambTimeRange1
            self.emitCellChanged(day, self.ciAmbTimeRange1)
        if dayInfo[self.ciAmbOffice1] != ambOffice1:
            dayInfo[self.ciAmbOffice1] = ambOffice1
            self.emitCellChanged(day, self.ciAmbOffice1)
        if dayInfo[self.ciAmbPlan1] != ambPlan1:
            dayInfo[self.ciAmbPlan1] = ambPlan1
            self.emitCellChanged(day, self.ciAmbPlan1)
        if dayInfo[self.ciAmbInterval1] != ambInterval1:
            dayInfo[self.ciAmbInterval1] = ambInterval1
            self.emitCellChanged(day, self.ciAmbInterval1)
        if dayInfo[self.ciAmbColor1] != ambColor1:
            dayInfo[self.ciAmbColor1] = ambColor1
            self.emitCellChanged(day, self.ciAmbColor1)
        if dayInfo[self.ciAmbTimeRange2] != ambTimeRange2:
            dayInfo[self.ciAmbTimeRange2] = ambTimeRange2
            self.emitCellChanged(day, self.ciAmbTimeRange2)
        if dayInfo[self.ciAmbOffice2] != ambOffice2:
            dayInfo[self.ciAmbOffice2] = ambOffice2
            self.emitCellChanged(day, self.ciAmbOffice2)
        if dayInfo[self.ciAmbPlan2] != ambPlan2:
            dayInfo[self.ciAmbPlan2] = ambPlan2
            self.emitCellChanged(day, self.ciAmbPlan2)
        if dayInfo[self.ciAmbInterval2] != ambInterval2:
            dayInfo[self.ciAmbInterval2] = ambInterval2
            self.emitCellChanged(day, self.ciAmbInterval2)
        if dayInfo[self.ciAmbColor2] != ambColor2:
            dayInfo[self.ciAmbColor2] = ambColor2
            self.emitCellChanged(day, self.ciAmbColor2)
        if dayInfo[self.ciAmbInterOffice] != ambOfficeInter:
            dayInfo[self.ciAmbInterOffice] = ambOfficeInter
            self.emitCellChanged(day, self.ciAmbInterOffice)
        if dayInfo[self.ciAmbInterPlan] != ambInterPlan:
            dayInfo[self.ciAmbInterPlan] = ambInterPlan
            self.emitCellChanged(day, self.ciAmbInterPlan)
        if dayInfo[self.ciAmbInterInterval] != ambInterInterval:
            dayInfo[self.ciAmbInterInterval] = ambInterInterval
            self.emitCellChanged(day, self.ciAmbInterPlan)
        if dayInfo[self.ciAmbInterColor] != ambInterColor:
            dayInfo[self.ciAmbInterColor] = ambInterColor
            self.emitCellChanged(day, self.ciAmbInterColor)
        if dayInfo[self.ciHomeTimeRange1] != homTimeRange1:
            dayInfo[self.ciHomeTimeRange1] = homTimeRange1
            self.emitCellChanged(day, self.ciHomeTimeRange1)
        if dayInfo[self.ciHomePlan1] != homPlan1:
            dayInfo[self.ciHomePlan1] = homPlan1
            self.emitCellChanged(day, self.ciHomePlan1)
        if dayInfo[self.ciHomeInterval1] != homInterval1:
            dayInfo[self.ciHomeInterval1] = homInterval1
            self.emitCellChanged(day, self.ciHomeInterval1)
        if dayInfo[self.ciHomeTimeRange2] != homTimeRange2:
            dayInfo[self.ciHomeTimeRange2] = homTimeRange2
            self.emitCellChanged(day, self.ciHomeTimeRange2)
        if dayInfo[self.ciHomePlan2] != homPlan2:
            dayInfo[self.ciHomePlan2] = homPlan2
            self.emitCellChanged(day, self.ciHomePlan2)
        if dayInfo[self.ciHomeInterval2] != homInterval2:
            dayInfo[self.ciHomeInterval2] = homInterval2
            self.emitCellChanged(day, self.ciHomeInterval2)
        if dayInfo[self.ciAmbTimeRange] != ambTimeRange:
            dayInfo[self.ciAmbTimeRange] = ambTimeRange
            self.emitCellChanged(day, self.ciAmbTimeRange)
        if dayInfo[self.ciAmbOffice] != ambOffice:
            dayInfo[self.ciAmbOffice] = ambOffice
            self.emitCellChanged(day, self.ciAmbOffice)
        if dayInfo[self.ciAmbPlan] != ambPlan:
            dayInfo[self.ciAmbPlan] = ambPlan
            self.emitCellChanged(day, self.ciAmbPlan)
        if dayInfo[self.ciAmbInterval] != ambInterval:
            dayInfo[self.ciAmbInterval] = ambInterval
            self.emitCellChanged(day, self.ciAmbInterval)
        if dayInfo[self.ciAmbColor] != ambColor:
            dayInfo[self.ciAmbColor] = ambColor
            self.emitCellChanged(day, self.ciAmbColor)
        if dayInfo[self.ciHomeTimeRange] != homTimeRange:
            dayInfo[self.ciHomeTimeRange] = homTimeRange
            self.emitCellChanged(day, self.ciHomeTimeRange)
        if dayInfo[self.ciHomePlan] != homPlan:
            dayInfo[self.ciHomePlan] = homPlan
            self.emitCellChanged(day, self.ciHomePlan)
        if dayInfo[self.ciHomeInterval] != homInterval:
            dayInfo[self.ciHomeInterval] = homInterval
            self.emitCellChanged(day, self.ciHomeInterval)
        dayInfo[self.ciAmbChange] = True
        dayInfo[self.ciAmbTimesChange] = True
        dayInfo[self.ciHomeChange] = True
        dayInfo[self.ciHomeTimesChange] = True

    def setTaskPlanForPersonsTemplate(self, day, data):
        ambTimeRange, ambOffice, ambPlan, ambInterval, ambColor, ambTimeRange1, ambOffice1, ambPlan1, ambInterval1, ambColor1, ambTimeRange2, ambOffice2, ambPlan2, ambInterval2, ambColor2, ambOfficeInter, ambInterPlan, ambInterInterval, ambColorInter = self.getTaskPlanPerson(data[CTimeTableModel.ciAmbTimeRange], data[CTimeTableModel.ciAmbOffice], data[CTimeTableModel.ciAmbPlan], data[CTimeTableModel.ciAmbInterval], data[CTimeTableModel.ciAmbColor], data[CTimeTableModel.ciAmbTimeRange2], data[CTimeTableModel.ciAmbOffice2], data[CTimeTableModel.ciAmbPlan2], data[CTimeTableModel.ciAmbInterval2], data[CTimeTableModel.ciAmbColor2], data[CTimeTableModel.ciAmbInterOffice], data[CTimeTableModel.ciAmbInterPlan], data[CTimeTableModel.ciAmbInterInterval], data[CTimeTableModel.ciAmbInterColor])
        homTimeRange, homOffice, homPlan, homInterval, homColor, homTimeRange1, homOffice1, homPlan1, homInterval1, homColor1, homTimeRange2, homOffice2, homPlan2, homInterval2, homColor2, homeOfficeInter, homeInterPlan, homeInterInterval, homColorInter = self.getTaskPlanPerson(data[CTimeTableModel.ciHomeTimeRange], None, data[CTimeTableModel.ciHomePlan], data[CTimeTableModel.ciHomeInterval], None, data[CTimeTableModel.ciHomeTimeRange2],  None, data[CTimeTableModel.ciHomePlan2], data[CTimeTableModel.ciHomeInterval2], None, None, None, None, None)
        dayInfo = self.dayInfoPersons[day]
        if dayInfo[self.ciAmbTimeRange1] != ambTimeRange1:
            dayInfo[self.ciAmbTimeRange1] = ambTimeRange1
        if dayInfo[self.ciAmbOffice1] != ambOffice1:
            dayInfo[self.ciAmbOffice1] = ambOffice1
        if dayInfo[self.ciAmbPlan1] != ambPlan1:
            dayInfo[self.ciAmbPlan1] = ambPlan1
        if dayInfo[self.ciAmbInterval1] != ambInterval1:
            dayInfo[self.ciAmbInterval1] = ambInterval1
        if dayInfo[self.ciAmbColor1] != ambColor1:
            dayInfo[self.ciAmbColor1] = ambColor1
        if dayInfo[self.ciAmbTimeRange2] != ambTimeRange2:
            dayInfo[self.ciAmbTimeRange2] = ambTimeRange2
        if dayInfo[self.ciAmbOffice2] != ambOffice2:
            dayInfo[self.ciAmbOffice2] = ambOffice2
        if dayInfo[self.ciAmbPlan2] != ambPlan2:
            dayInfo[self.ciAmbPlan2] = ambPlan2
        if dayInfo[self.ciAmbInterval2] != ambInterval2:
            dayInfo[self.ciAmbInterval2] = ambInterval2
        if dayInfo[self.ciAmbColor2] != ambColor2:
            dayInfo[self.ciAmbColor2] = ambColor2
        if dayInfo[self.ciAmbInterOffice] != ambOfficeInter:
            dayInfo[self.ciAmbInterOffice] = ambOfficeInter
        if dayInfo[self.ciAmbInterPlan] != ambInterPlan:
            dayInfo[self.ciAmbInterPlan] = ambInterPlan
        if dayInfo[self.ciAmbInterInterval] != ambInterInterval:
            dayInfo[self.ciAmbInterInterval] = ambInterInterval
        if dayInfo[self.ciAmbInterColor] != ambColorInter:
            dayInfo[self.ciAmbInterColor] = ambColorInter
        if dayInfo[self.ciHomeTimeRange1] != homTimeRange1:
            dayInfo[self.ciHomeTimeRange1] = homTimeRange1
        if dayInfo[self.ciHomePlan1] != homPlan1:
            dayInfo[self.ciHomePlan1] = homPlan1
        if dayInfo[self.ciHomeInterval1] != homInterval1:
            dayInfo[self.ciHomeInterval1] = homInterval1
        if dayInfo[self.ciHomeTimeRange2] != homTimeRange2:
            dayInfo[self.ciHomeTimeRange2] = homTimeRange2
        if dayInfo[self.ciHomePlan2] != homPlan2:
            dayInfo[self.ciHomePlan2] = homPlan2
        if dayInfo[self.ciHomeInterval2] != homInterval2:
            dayInfo[self.ciHomeInterval2] = homInterval2
        if dayInfo[self.ciAmbTimeRange] != ambTimeRange:
            dayInfo[self.ciAmbTimeRange] = ambTimeRange
        if dayInfo[self.ciAmbOffice] != ambOffice:
            dayInfo[self.ciAmbOffice] = ambOffice
        if dayInfo[self.ciAmbPlan] != ambPlan:
            dayInfo[self.ciAmbPlan] = ambPlan
        if dayInfo[self.ciAmbInterval] != ambInterval:
            dayInfo[self.ciAmbInterval] = ambInterval
        if dayInfo[self.ciAmbColor] != ambColor:
            dayInfo[self.ciAmbColor] = ambColor
        if dayInfo[self.ciHomeTimeRange] != homTimeRange:
            dayInfo[self.ciHomeTimeRange] = homTimeRange
        if dayInfo[self.ciHomePlan] != homPlan:
            dayInfo[self.ciHomePlan] = homPlan
        if dayInfo[self.ciHomeInterval] != homInterval:
            dayInfo[self.ciHomePlan] = homInterval

    def saveDataPersonTemplate(self, personId):
        if personId:
            db = QtGui.qApp.db
            eventTable = db.table('Event')
            db.transaction()
            try:
                for day in xrange(self.daysInMonth):
                    dayInfo = self.dayInfoPersons[day]
                    event = getEvent(constants.etcTimeTable, self.begDate.addDays(day), personId)
                    eventId = db.insertOrUpdate(eventTable, event)
                    action = CAction.getAction(eventId, constants.atcAmbulance)
                    timeRange = dayInfo[self.ciAmbTimeRange]
                    if timeRange:
                        action['begTime'], action['endTime'] = timeRange
                    else:
                        del action['begTime']
                        del action['endTime']
                    action['office'] = dayInfo[self.ciAmbOffice]
                    action['plan'] = dayInfo[self.ciAmbInterval]
                    action['color'] = dayInfo[self.ciAmbColor]
                    action['notExternalSystem'] = dayInfo[self.ciNotExternalSystem]
                    timeRange1 = dayInfo[self.ciAmbTimeRange1]
                    if timeRange1:
                        action['begTime1'], action['endTime1'] = timeRange1
                    else:
                        del action['begTime1']
                        del action['endTime1']
                    action['office1'] = dayInfo[self.ciAmbOffice1]
                    action['plan1'] = dayInfo[self.ciAmbInterval1]
                    action['color1'] = dayInfo[self.ciAmbColor1]
                    timeRange2 = dayInfo[self.ciAmbTimeRange2]
                    if timeRange2:
                        action['begTime2'], action['endTime2'] = timeRange2
                    else:
                        del action['begTime2']
                        del action['endTime2']
                    action['office2'] = dayInfo[self.ciAmbOffice2]
                    action['plan2'] = dayInfo[self.ciAmbInterval2]
                    action['color2'] = dayInfo[self.ciAmbColor2]
                    action['officeInter'] = dayInfo[self.ciAmbInterOffice]
                    action['interInterval'] = dayInfo[self.ciAmbInterInterval]
                    action['colorInter'] = dayInfo[self.ciAmbInterColor]
                    action['fact'] = dayInfo[self.ciAmbFact]
                    action['time'] = dayInfo[self.ciAmbTime]
                    if timeRange1 and timeRange2:
                        result = calcTimePlan(timeRange1, dayInfo[self.ciAmbPlan1], personId, True, result=[], interval=dayInfo[self.ciAmbInterval1])
                        resultEx = [1 if dayInfo[self.ciNotExternalSystem1] else 0] * len(result)
                        if dayInfo[self.ciAmbInterPlan]:
                            timeRangeInter = (timeRange1[1], timeRange2[0])
                            result = calcTimePlan(timeRangeInter, dayInfo[self.ciAmbInterPlan], personId, True, result, dayInfo[self.ciAmbInterInterval])
                            resultEx = resultEx + [1 if dayInfo[self.ciInterNotExternalSystem] else 0] * (len(result) - len(resultEx))
                        result = calcTimePlan(timeRange2, dayInfo[self.ciAmbPlan2], personId, True, result, dayInfo[self.ciAmbInterval2])
                        resultEx = resultEx + [1 if dayInfo[self.ciNotExternalSystem2] else 0] * (len(result) - len(resultEx))
                        action['times'] = result
                        action['notExternalSystems'] = resultEx
                    else:
                        action['times'] = calcTimePlan(timeRange, dayInfo[self.ciAmbPlan], personId, True, result=[], interval=dayInfo[self.ciAmbInterval])
                        action['notExternalSystems'] = [1 if dayInfo[self.ciNotExternalSystem1] else 0] * len(result)
                    colors = []
                    if dayInfo[self.ciAmbPlan1]:
                        colors.extend([dayInfo[self.ciAmbColor1]] * dayInfo[self.ciAmbPlan1])
                    elif dayInfo[self.ciAmbPlan]:
                        colors.extend([dayInfo[self.ciAmbColor1]] * dayInfo[self.ciAmbPlan])
                    if dayInfo[self.ciAmbInterPlan]:
                        colors.extend([dayInfo[self.ciAmbInterColor]] * dayInfo[self.ciAmbInterPlan])
                    if dayInfo[self.ciAmbPlan2]:
                        colors.extend([dayInfo[self.ciAmbColor2]] * dayInfo[self.ciAmbPlan2])
                    action['colors'] = colors
                    action.save(eventId)

                    action = CAction.getAction(eventId, constants.atcHome)
                    timeRange = dayInfo[self.ciHomeTimeRange]
                    if timeRange:
                        action['begTime'], action['endTime'] = timeRange
                    else:
                        del action['begTime']
                        del action['endTime']
                    action['plan'] = dayInfo[self.ciHomePlan]
                    timeRange1 = dayInfo[self.ciHomeTimeRange1]
                    if timeRange1:
                        action['begTime1'], action['endTime1'] = timeRange1
                    else:
                        del action['begTime1']
                        del action['endTime1']
                    action['plan1'] = dayInfo[self.ciHomePlan1]
                    timeRange2 = dayInfo[self.ciHomeTimeRange2]
                    if timeRange2:
                        action['begTime2'], action['endTime2'] = timeRange2
                    else:
                        del action['begTime2']
                        del action['endTime2']
                    action['plan2'] = dayInfo[self.ciHomePlan2]
                    action['fact'] = dayInfo[self.ciHomeFact]
                    action['time'] = dayInfo[self.ciHomeTime]
                    if timeRange1 and timeRange2:
                        result = calcTimePlan(timeRange1, dayInfo[self.ciHomePlan1], personId, False, result=[], interval=dayInfo[self.ciHomeInterval1])
                        result = calcTimePlan(timeRange2, dayInfo[self.ciHomePlan2], personId, False, result, dayInfo[self.ciHomeInterval2])
                        action['times'] = result
                    else:
                        action['times'] = calcTimePlan(timeRange, dayInfo[self.ciHomePlan], personId, False, result=[], interval=dayInfo[self.ciHomeInterval])
                    action.save(eventId)

                    action = CAction.getAction(eventId, constants.atcExp)
                    timeRange = dayInfo[self.ciExpTimeRange]
                    if timeRange:
                        action['begTime'], action['endTime'] = timeRange
                    else:
                        del action['begTime']
                        del action['endTime']
                    action['office'] = dayInfo[self.ciExpOffice]
                    action['plan'] = dayInfo[self.ciExpPlan]
                    action['fact'] = dayInfo[self.ciExpPlan]
                    action['time'] = dayInfo[self.ciExpTime]
                    action['times'] = calcTimePlan(timeRange, dayInfo[self.ciExpPlan], personId, False, result=[])
                    action.save(eventId)

                    action = CAction.getAction(eventId, constants.atcTimeLine)
                    action['otherTime'] = dayInfo[self.ciOtherTime]
                    action['factTime'] = dayInfo[self.ciFactTime]
                    action['reasonOfAbsence'] = dayInfo[self.ciReasonOfAbsence]
                    action.save(eventId)
                db.commit()
            except:
                db.rollback()
                QtGui.qApp.logCurrentException()
                raise

    def fillSum(self):
        for day in xrange(self.daysInMonth):
            dayInfo = self.items[day]
            time = 0
            if dayInfo[self.ciAmbTimeRange1] or dayInfo[self.ciAmbTimeRange2]:
                time += calcSecondsInTimeRange(dayInfo[self.ciAmbTimeRange1]) + calcSecondsInTimeRange(dayInfo[self.ciAmbTimeRange2])
            else:
                time += calcSecondsInTimeRange(dayInfo[self.ciAmbTimeRange])

            if dayInfo[self.ciHomeTimeRange1] or dayInfo[self.ciHomeTimeRange2]:
                time += calcSecondsInTimeRange(dayInfo[self.ciHomeTimeRange1]) + calcSecondsInTimeRange(dayInfo[self.ciHomeTimeRange2])
            else:
                time += calcSecondsInTimeRange(dayInfo[self.ciHomeTimeRange])

            if dayInfo[self.ciExpTimeRange]:
                time += calcSecondsInTimeRange(dayInfo[self.ciExpTimeRange])

            if time:
                self.setData(self.index(day, self.ciFactTime), QtCore.QVariant(QtCore.QTime(0, 0).addSecs(time)))

    def fillFact(self):
        for day in xrange(self.daysInMonth):
            dayInfo = self.items[day]
            time = dayInfo[self.ciFactTime]
            if not time:
                continue
            minuts = QtCore.QTime(0, 0).secsTo(time) // 60

            if dayInfo[self.ciAmbTimeRange1] or dayInfo[self.ciAmbTimeRange2]:
                ambulanceTime = calcSecondsInTimeRange(dayInfo[self.ciAmbTimeRange1]) + calcSecondsInTimeRange(dayInfo[self.ciAmbTimeRange2])
            else:
                ambulanceTime = calcSecondsInTimeRange(dayInfo[self.ciAmbTimeRange])

            if dayInfo[self.ciHomeTimeRange1] or dayInfo[self.ciHomeTimeRange2]:
                homeTime = calcSecondsInTimeRange(dayInfo[self.ciHomeTimeRange1]) + calcSecondsInTimeRange(dayInfo[self.ciHomeTimeRange2])
            else:
                homeTime = calcSecondsInTimeRange(dayInfo[self.ciHomeTimeRange])

            expTime = calcSecondsInTimeRange(dayInfo[self.ciExpTimeRange])

            if ambulanceTime:
                ambulanceMinuts = (ambulanceTime * minuts) // (ambulanceTime + homeTime + expTime)
                self.setData(self.index(day, self.ciAmbTime), QtCore.QVariant(QtCore.QTime(0, 0).addSecs(ambulanceMinuts * 60)))
                minuts -= ambulanceMinuts
            if homeTime:
                homeMinuts = (homeTime * minuts) // (homeTime + expTime)
                self.setData(self.index(day, self.ciHomeTime), QtCore.QVariant(QtCore.QTime(0, 0).addSecs(homeMinuts * 60)))
            if expTime:
                self.setData(self.index(day, self.ciExpTime), QtCore.QVariant(QtCore.QTime(0, 0).addSecs(minuts * 60)))

    def updateSums(self, column, emitChanges=True):
        if self.personId:
            if column in self.cilTimeRange:
                sum = 0
                for day in xrange(self.daysInMonth):
                    sum += calcSecondsInTimeRange(self.items[day][column])
                minuts = sum // 60
                self.items[self.daysInMonth][column] = '%02d:%02d' % (minuts // 60, minuts % 60)
            elif column in self.cilTime:
                sum = 0
                for day in xrange(self.daysInMonth):
                    sum += calcSecondsInTime(self.items[day][column])
                minuts = sum // 60
                self.items[self.daysInMonth][column] = '%02d:%02d' % (minuts // 60, minuts % 60)
            elif column in self.cilNum:
                sum = 0
                for day in xrange(self.daysInMonth):
                    n = self.items[day][column]
                    if n:
                        sum += n
                self.items[self.daysInMonth][column] = sum
            else:
                self.items[self.daysInMonth][column] = ''
        if emitChanges:
            self.emitCellChanged(self.daysInMonth, column)

    def updateAttrs(self):
        attrs = CAttrs()
        if self.personId:
            for day in xrange(self.daysInMonth):
                item = self.items[day]
                factTime = item[self.ciFactTime]
                reasonOfAbsence = item[self.ciReasonOfAbsence]
                ambTime = item[self.ciAmbTime]
                ambPlan = item[self.ciAmbPlan]
                ambFact = item[self.ciAmbFact]
                homeTime = item[self.ciHomeTime]
                homePlan = item[self.ciHomePlan]
                homeFact = item[self.ciHomeFact]
                expTime = item[self.ciExpTime]
                expPlan = item[self.ciExpPlan]
                expFact = item[self.ciExpFact]

                if not factTime:  # factTime.isNull() or :
                    if reasonOfAbsence:
                        attrs.numAbsenceDays += 1
                else:
                    amb = False
                    attrs.numDays += 1
                    if ambTime and not ambTime.isNull():
                        attrs.numAmbDays += 1
                        attrs.numAmbTime += calcSecondsInTime(ambTime)
                        if ambPlan: attrs.numAmbPlan += ambPlan
                        if ambFact: attrs.numAmbFact += ambFact
                        amb = True
                    if homeTime and not homeTime.isNull():
                        attrs.numHomeDays += 1
                        attrs.numHomeTime += calcSecondsInTime(homeTime)
                        if homePlan: attrs.numHomePlan += homePlan
                        if homeFact: attrs.numHomeFact += homeFact
                        if amb:
                            attrs.numServDays += 1
                    if expTime and not expTime.isNull():
                        attrs.numExpDays += 1
                        attrs.numExpTime += calcSecondsInTime(expTime)
                        if expPlan: attrs.numExpPlan += expPlan
                        if expFact: attrs.numExpFact += expFact

        if self.attrs != attrs:
            self.attrs = attrs
            self.emitAttrsChanged()


# def createEditor(self, column, parent):
#        return self.__cols[column].createEditor(parent)


#    def setEditorData(self, column, editor, value, record):
#        return self.__cols[column].setEditorData(editor, value, record)


#    def getEditorData(self, column, editor):
#        return self.__cols[column].getEditorData(editor)


class CTimeRangeItemDelegate(QtGui.QItemDelegate):
    def __init__(self, parent=None):
        QtGui.QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        editor = CTimeRangeEdit(parent)
        # self.connect(editor, QtCore.SIGNAL('activated(int)'), self.emitCommitData)
        # self.connect(self, QtCore.SIGNAL('closeEditor(QWidget, QAbstractItemDelegate.EndEditHint)'), self.closeEditor)
        return editor

    def setEditorData(self, editor, index):
        model = index.model()
        data = model.data(index, QtCore.Qt.EditRole)
        editor.setTimeRange(convertVariantToTimeRange(data))

    def setModelData(self, editor, model, index):
        model.setData(index, convertTimeRangeToVariant(editor.timeRange()))


# def emitCommitData(self):
#        self.emit(QtCore.SIGNAL('commitData(QWidget *)'), self.sender())


class CTimeItemDelegate(QtGui.QItemDelegate):
    def __init__(self, parent=None):
        QtGui.QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        # editor = QtGui.QTimeEdit(parent)
        # editor.setDisplayFormat('HH:mm')
        editor = CTimeEdit(parent)
        # self.connect(editor, QtCore.SIGNAL('activated(int)'), self.emitCommitData)
        # self.connect(self, QtCore.SIGNAL('closeEditor(QWidget, QAbstractItemDelegate.EndEditHint)'), self.closeEditor)
        return editor

    def setEditorData(self, editor, index):
        model = index.model()
        data = model.data(index, QtCore.Qt.EditRole)
        editor.setTime(data.toTime())

    def setModelData(self, editor, model, index):
        model.setData(index, QtCore.QVariant(editor.time()))


# def emitCommitData(self):
#        self.emit(QtCore.SIGNAL('commitData(QWidget *)'), self.sender())


class CReasonOfAbsenceItemDelegate(QtGui.QItemDelegate):
    def __init__(self, parent=None):
        QtGui.QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        editor = CRBComboBox(parent)
        editor.setTable('rbReasonOfAbsence')
        return editor

    def setEditorData(self, editor, index):
        model = index.model()
        data = model.data(index, QtCore.Qt.EditRole)
        editor.setValue(forceRef(data))

    def setModelData(self, editor, model, index):
        model.setData(index, QtCore.QVariant(editor.value()))


# def emitCommitData(self):
#        self.emit(QtCore.SIGNAL('commitData(QWidget *)'), self.sender())


class CAmbOfficeEdit(QtGui.QLineEdit):
    def __init__(self, parent=None):
        QtGui.QLineEdit.__init__(self, parent)


class CAmbHomePlanEdit(QtGui.QSpinBox):
    def __init__(self, parent=None):
        QtGui.QSpinBox.__init__(self, parent)


class CAmbOfficeItemDelegate(QtGui.QItemDelegate):
    def __init__(self, parent=None):
        QtGui.QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        editor = CAmbOfficeEdit(parent)
        return editor

    def setEditorData(self, editor, index):
        model = index.model()
        data = model.data(index, QtCore.Qt.EditRole)
        editor.setText(forceString(data))

    def setModelData(self, editor, model, index):
        model.setData(index, toVariant(editor.text()))


class CAmbPlanItemDelegate(QtGui.QItemDelegate):
    def __init__(self, parent=None):
        QtGui.QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        editor = CAmbHomePlanEdit(parent)
        return editor

    def setEditorData(self, editor, index):
        model = index.model()
        data = model.data(index, QtCore.Qt.EditRole)
        editor.setValue(forceInt(data))

    def setModelData(self, editor, model, index):
        model.setData(index, QtCore.QVariant(editor.value()))


class CColorItemDelegate(QtGui.QItemDelegate):
    def __init__(self, parent=None):
        QtGui.QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        editor = QtGui.QColorDialog()
        model = index.model()
        # try:
        color = QtGui.QColor(model.data(index, QtCore.Qt.BackgroundRole))
        if color.isValid():
            editor.setCurrentColor(color)
        if editor.exec_():
            model.setData(index, QtCore.QVariant(editor.currentColor().name()))
        # finally:
        #     sip.delete(editor)
        #     return None
        return editor

    def setEditorData(self, editor, index):
        pass

    def setModelData(self, editor, model, index):
        pass


class CSecondPeriodItemDelegate(CTimeRangeItemDelegate):
    def createEditor(self, parent, option, index):
        column = index.column()
        model = index.model()
        row = index.row()
        if model.items[row][CTimeTableModel.ciAmbTimeRange1] or model.items[row][CTimeTableModel.ciAmbTimeRange2] or model.items[row][CTimeTableModel.ciHomeTimeRange1] or model.items[row][CTimeTableModel.ciHomeTimeRange2]:
            editor = CTemplateEdit(parent)
            QtGui.qApp.callWithWaitCursor(self, editor.loadData, model.items[row], model.selectedDate)
            editor.exec_()
            return None
        elif column in [CTimeTableModel.ciAmbTimeRange, CTimeTableModel.ciHomeTimeRange]:
            editor = CTimeRangeEdit(parent)
        elif column in [CTimeTableModel.ciAmbOffice]:
            editor = CAmbOfficeEdit(parent)
        elif column in [CTimeTableModel.ciAmbPlan, CTimeTableModel.ciAmbInterval, CTimeTableModel.ciHomePlan, CTimeTableModel.ciHomeInterval]:
            editor = CAmbHomePlanEdit(parent)
        return editor

    def setEditorData(self, editor, index):
        column = index.column()
        model = index.model()
        row = index.row()
        data = model.data(index, QtCore.Qt.EditRole)
        if isinstance(editor, CAmbHomePlanEdit):
            editor.setMaximum(9999)

        if model.items[row][CTimeTableModel.ciAmbTimeRange1] or model.items[row][CTimeTableModel.ciAmbTimeRange2] or model.items[row][CTimeTableModel.ciHomeTimeRange1] or model.items[row][CTimeTableModel.ciHomeTimeRange2]:
            pass
        elif column in [CTimeTableModel.ciAmbTimeRange, CTimeTableModel.ciHomeTimeRange]:
            editor.setTimeRange(convertVariantToTimeRange(data))
        elif column in [CTimeTableModel.ciAmbOffice]:
            editor.setText(forceString(data))
        elif column in [CTimeTableModel.ciAmbPlan, CTimeTableModel.ciAmbInterval, CTimeTableModel.ciHomePlan, CTimeTableModel.ciHomeInterval]:
            editor.setValue(forceInt(data))

    def setModelData(self, editor, model, index):
        column = index.column()
        model = index.model()
        row = index.row()
        if model.items[row][CTimeTableModel.ciAmbTimeRange1] or model.items[row][CTimeTableModel.ciAmbTimeRange2] or model.items[row][CTimeTableModel.ciHomeTimeRange1] or model.items[row][CTimeTableModel.ciHomeTimeRange2]:
            pass
        elif column in [CTimeTableModel.ciAmbTimeRange, CTimeTableModel.ciHomeTimeRange]:
            model.setData(index, convertTimeRangeToVariant(editor.timeRange()))
        elif column in [CTimeTableModel.ciAmbOffice]:
            model.setData(index, QtCore.QVariant(editor.text()))
        elif column in [CTimeTableModel.ciAmbPlan, CTimeTableModel.ciAmbInterval, CTimeTableModel.ciHomePlan, CTimeTableModel.ciHomeInterval]:
            model.setData(index, QtCore.QVariant(editor.value()))


class CTimeTable(CTableView):
    def __init__(self, parent):
        CTableView.__init__(self, parent)

        self.verticalHeader().show()
        self.verticalHeader().setResizeMode(QtGui.QHeaderView.Fixed)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setStretchLastSection(True)
        self.setTabKeyNavigation(True)
        self.setEditTriggers(QtGui.QAbstractItemView.AnyKeyPressed | QtGui.QAbstractItemView.EditKeyPressed | QtGui.QAbstractItemView.SelectedClicked | QtGui.QAbstractItemView.DoubleClicked)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.timeRangeDelegate = CSecondPeriodItemDelegate(self)
        self.timeDelegate = CTimeItemDelegate(self)
        self.reasonOfAbsenceDelegate = CReasonOfAbsenceItemDelegate(self)
        for column in [CTimeTableModel.ciAmbTimeRange, CTimeTableModel.ciHomeTimeRange, CTimeTableModel.ciExpTimeRange, CTimeTableModel.ciAmbOffice, CTimeTableModel.ciAmbPlan, CTimeTableModel.ciAmbInterval, CTimeTableModel.ciHomePlan, CTimeTableModel.ciHomeInterval, CTimeTableModel.ciNotExternalSystem1]:
            self.setItemDelegateForColumn(column, self.timeRangeDelegate)
        for column in CTimeTableModel.cilTime:
            self.setItemDelegateForColumn(column, self.timeDelegate)
        self.setItemDelegateForColumn(CTimeTableModel.ciReasonOfAbsence, self.reasonOfAbsenceDelegate)

    def setTaskPlanSecondPeriod(self, day, data):
        self.model().setTaskPlanSecondPeriod(day, data)

    def setSelectionModel(self, selectionModel):
        currSelectionModel = self.selectionModel()
        if currSelectionModel:
            self.disconnect(currSelectionModel, QtCore.SIGNAL('currentChanged(QModelIndex,QModelIndex))'), self.currentChanged)
        QtGui.QTableView.setSelectionModel(self, selectionModel)
        if selectionModel:
            self.connect(selectionModel, QtCore.SIGNAL('currentChanged(QModelIndex,QModelIndex))'), self.currentChanged)


def getGapList(personId):
    # gapList is list of (begGapTime, endGapTime) ordered by begGapTime
    # gaps may owerlap
    # gaps cannot cross midnight

    def addGap(gapList, record):
        bTime = forceTime(record.value('begTime'))
        eTime = forceTime(record.value('endTime'))
        if bTime < eTime:
            gapList.append((bTime, eTime))
        elif bTime > eTime:
            gapList.append((bTime, QtCore.QTime(23, 59, 59, 999)))
            gapList.append((QtCore.QTime(0, 0), eTime))

    db = QtGui.qApp.db
    specialityId = forceRef(db.translate('Person', 'id', personId, 'speciality_id'))
    orgStructureBaseId = forceRef(db.translate('Person', 'id', personId, 'orgStructure_id'))
    result = []
    orgStructureId = orgStructureBaseId
    while orgStructureId:
        orgStructureGapRecordList = db.getRecordList('OrgStructure_Gap', 'begTime, endTime',  'master_id=%d%s AND person_id IS NULL'%(orgStructureId, u' AND (speciality_id=%d OR speciality_id IS NULL)'%(specialityId) if specialityId else u' AND speciality_id IS NULL'), 'begTime, endTime')
        for record in orgStructureGapRecordList:
            addGap(result, record)
        recordInheritGaps = db.getRecordEx('OrgStructure', 'inheritGaps', 'id=%d' % (orgStructureId))
        inheritGaps = forceBool(recordInheritGaps.value(0)) if recordInheritGaps else (False if orgStructureGapRecordList else True)
        if not inheritGaps:
            break
        orgStructureId = forceRef(db.translate('OrgStructure', 'id', orgStructureId, 'parent_id'))
    orgStructureId = orgStructureBaseId
    while orgStructureId:
        personGapRecordList = db.getRecordList('OrgStructure_Gap', 'begTime, endTime', 'master_id=%d AND person_id=%d' % (orgStructureId, personId), 'begTime, endTime')
        for record in personGapRecordList:
            addGap(result, record)
        orgStructureId = forceRef(db.translate('OrgStructure', 'id', orgStructureId, 'parent_id'))
    result.sort()
    return result


def invertGapList(gapList):
    # inverted gapList (workList) is list of (begWorkTime, endWorkTime) ordered by begWorkTime
    # work times must not overlap
    # work times cannot cross midnight
    result = []
    workTime = QtCore.QTime(0, 0)
    for bTime, eTime in gapList:
        if workTime < bTime:
            result.append((workTime, bTime))
        workTime = max(workTime, eTime)
    lastTime = QtCore.QTime(23, 59, 59, 999)
    if workTime < lastTime:
        result.append((workTime, lastTime))
    return result


def filterWorkList(workList, begTime, endTime):
    # filtered workList is list of (begWorkTime, endWorkTime) limited by range(begTime, endTime)
    result = []
    for bTime, eTime in workList:
        if eTime > begTime:
            bPTime = max(bTime, begTime)
            ePTime = min(eTime, endTime)
            if bPTime < ePTime:
                result.append((bPTime, ePTime))
        if bTime >= endTime:
            break
    return result


def getPersonGaps(gapsTime):
    u"""
    Структуризация списока перерывов
    :param gapsTime: список перерывов [[QtCore.QTime, QtCore.QTime]]
    :return: список словарей перерывов [{'begTime': QtCore.QTime, 'endTime': QtCore.QTime}]
    """
    gaps = []
    for x in gapsTime:
        gaps.append({
            'begTime': x[0],
            'endTime': x[1]
        })
    return gaps


def recreateTimeByGaps(gapsTime, timeRange, times, queue=None):
    u"""
    Исключает те номерки, чье время попадает в рамки назначенных специалисту перерывов

    :param gapsTime: список перерывов [[QtCore.QTime, QtCore.QTime]]
    :param timeRange: диапазон времени према
    :param times: список времен для номерков
    :param queue: список очередей для номерков
    :return: скорректированный список времен для номерков
    """

    def isTimeInTimeRange(time, gaps, delta=0):
        for x in gaps:
            if x['begTime'].addSecs(-delta) <= time < x['endTime']:
                return True
        return False

    def clearList(lst, removeLst):
        for x in removeLst:
            lst.remove(x)

    if not gapsTime:
        return times

    gaps = getPersonGaps(gapsTime)

    removeList = {
        'times': [],
        'queue': []
    }
    if len(times) > 1:
        delta = times[0].secsTo(times[1])
    else:
        delta = 0

    for i, x in enumerate(times):
        if isTimeInTimeRange(x, gaps):
            if times:
                removeList['times'].append(times[i])
            if queue:
                removeList['queue'].append(queue[i])

    clearList(times, removeList['times'])
    clearList(queue, removeList['queue'])
    for i, gap in enumerate(gaps):
        firstTime = None
        # timeRange[0] - begDate
        if gap['endTime'] >= timeRange[0]:
            for x in times:
                endTime = gaps[i + 1]['begTime'] if i + 1 < len(gaps) else timeRange[1]
                if gap['endTime'].addSecs(-delta) <= x < endTime:
                    if firstTime is None:
                        firstTime = gap['endTime'].secsTo(x)

                    lstLen = len(times[times.index(x):])
                    for id, t in enumerate(times[times.index(x):]):
                        if t <= endTime:
                            times[times.index(t)] = t.addSecs(-firstTime)
                        if t > endTime.addSecs(-delta) or id + 1 == lstLen:
                            prevTime = times[times.index(t) - 1] if t in times else times[-1]
                            for t1 in times[times.index(prevTime):]:
                                if t1.secsTo(endTime) - delta > delta and t1 <= endTime:
                                    temp = t1.addSecs(delta)
                                    if temp not in times:
                                        times.insert(times.index(t1) + 1, temp)
                            break
                    break
    if times and times[-1] == timeRange[1]:
        times.pop()
    return times


def calcTimeInterval(timeRange, plan, interval, personId=None, allowGaps=False, result=None):
    u"""
    Вычисляет время для каждого номерка на прием врача.

    :param timeRange: диапазон времени према
    :param plan: план приемов пациентов
    :param interval: длительность одного приема
    :param personId: Person.id
    :param allowGaps: Флаг использования перерывов специалиста при выставлении номерков
    :param result: Список времен для номерков
    :return:
    """
    if not result:
        result = []
    interval = forceInt(interval)
    if timeRange and interval > 0:
        fullWorkList = [(QtCore.QTime(0, 0), QtCore.QTime(23, 59, 59, 999))]
        sbList = [(bTime.secsTo(eTime), bTime) for bTime, eTime in getWorkList(timeRange, fullWorkList)]
        sbList.sort()
        unallocatedSeconds = sum([sb[0] for sb in sbList])
        interval *= 60
        newPeriod = True
        while unallocatedSeconds >= interval and len(result) < plan:
            result.append(timeRange[0] if newPeriod else result[-1].addSecs(interval))
            newPeriod = False
            unallocatedSeconds -= interval

        if allowGaps:
            result = recreateTimeByGaps(getGapList(personId), timeRange, result)
    result.sort()
    return result


def calcTimePlan(timeRange, plan, personId, allowGaps, result=None, interval=None):
    if not result:
        result = []
    if timeRange and plan > 0:
        fullWorkList = invertGapList([])
        result = calcTimePlanEx(timeRange, plan, fullWorkList, result, interval)
        if allowGaps:
            result = recreateTimeByGaps(getGapList(personId), timeRange, result)
    result.sort()
    return result


def getWorkList(timeRange, fullWorkList):
    begTime, endTime = timeRange
    if begTime < endTime:
        workList = filterWorkList(fullWorkList, begTime, endTime)
    elif begTime > endTime:
        workList = filterWorkList(fullWorkList, QtCore.QTime(0, 0), endTime)
        workList.extend(filterWorkList(fullWorkList, begTime, QtCore.QTime(23, 59, 59, 999)))
    else:
        workList = fullWorkList
    return workList


def calcTimePlanEx(timeRange, plan, fullWorkList, result=None, interval=None):
    if not result:
        result = []
    if timeRange and plan > 0:
        sbList = [(bTime.secsTo(eTime), bTime) for bTime, eTime in getWorkList(timeRange, fullWorkList)]
        sbList.sort()
        unallocatedSeconds = sum([sb[0] for sb in sbList])
        unallocatedPlan = plan
        for seconds, bTime in sbList:
            # 0.4 - это такая цифровая магия
            # 10.5 номерков превратится в 10
            # a 10.6 в 11
            # при этом на следующие (бОльшие) периоды остаётся меньше номерков
            part = int(seconds * unallocatedPlan / float(unallocatedSeconds) + 0.5) if unallocatedSeconds else unallocatedPlan
            if part > 0:
                # if not interval:
                unit = seconds // part
                # else:
                #     unit = 60 * interval

                for j in xrange(part):
                    result.append(bTime.addSecs(j * unit))
            unallocatedSeconds -= seconds
            unallocatedPlan -= part
        result.sort()
    return result


class CTemplateEdit(CDialogBase, Ui_TemplateEdit):
    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.selectedDate = None
        self.prepareColors()

        setSignalMapper(self, listEdit['ambTimeRange'], self.edtAmbTimeRange_editingFinished, 1)
        setSignalMapper(self, listEdit['homeTimeRange'], self.edtHomeTimeRange_editingFinished, 1)
        setSignalMapper(self, listEdit['ambPlan'], self.edtAmbPlan_editingFinished, 1)
        setSignalMapper(self, listEdit['homePlan'], self.edtHomePlan_editingFinished, 1)
        setSignalMapper(self, listEdit['ambInterval'], self.edtAmbInterval_editingFinished, 1)
        setSignalMapper(self, listEdit['homeInterval'], self.edtHomeInterval_editingFinished, 1)
        for i in xrange(2):
            object = getObjectAttribute(self, listEdit['ambTimeRange'][i] % (1))
            object.installEventFilter(self)

    def prepareColors(self):
        self.btnAmbColor1.setStandardColors()
        self.btnAmbColorInter.setStandardColors()
        self.btnAmbColor2.setStandardColors()
        self.btnAmbColor1.setCurrentColor(QtCore.Qt.white)
        self.btnAmbColor2.setCurrentColor(QtCore.Qt.white)
        self.btnAmbColorInter.setCurrentColor(QtCore.Qt.white)

    def getData(self):
        ambTimeRange2 = self.edtAmbTimeRange12.timeRange() if self.edtAmbTimeRange12 else None
        if ambTimeRange2:
            timeStart2, timeFinish2 = ambTimeRange2
        else:
            timeStart2 = None
            timeFinish2 = None
        ambTimeRange1 = self.edtAmbTimeRange1.timeRange() if self.edtAmbTimeRange1 else None
        if ambTimeRange1:
            timeStart, timeFinish = ambTimeRange1
        else:
            timeStart = None
            timeFinish = None
        ambTimeRangeStart = min(timeStart, timeStart2) if (timeStart and timeStart2) else (timeStart if timeStart else (timeStart2 if timeStart2 else None))
        ambTimeRangeFinish = max(timeFinish, timeFinish2) if (timeFinish and timeFinish2) else (timeFinish if timeFinish else (timeFinish2 if timeFinish2 else None))
        if ambTimeRangeStart and ambTimeRangeFinish:
            ambTimeRange = ambTimeRangeStart, ambTimeRangeFinish
        else:
            ambTimeRange = None
        #        ambTimeRange = min(timeStart, timeStart2) if (timeStart and timeStart2) else (timeStart if timeStart else (timeStart2 if timeStart2 else None)), max(timeFinish, timeFinish2) if (timeFinish and timeFinish2) else (timeFinish if timeFinish else (timeFinish2 if timeFinish2 else None))
        ambOffice2 = forceStringEx(self.edtAmbOffice12.text()) if self.edtAmbOffice12 else None
        ambOffice1 = forceStringEx(self.edtAmbOffice1.text()) if self.edtAmbOffice1 else None
        ambOfficeInter = forceStringEx(self.edtAmbOfficeInter.text()) if self.edtAmbOfficeInter else None
        if ambOfficeInter:
            ambOffice = ambOffice1 + u', ' + ambOfficeInter + u', ' + ambOffice2
        else:
            ambOffice = ambOffice1 + u', ' + ambOffice2
        ambPlan2 = self.edtAmbPlan12.value() if self.edtAmbPlan12 else 0
        ambInterval2 = self.edtAmbInterval12.value() if self.edtAmbInterval12 else None
        ambPlan1 = self.edtAmbPlan1.value() if self.edtAmbPlan1 else 0
        ambInterval1 = self.edtAmbInterval1.value() if self.edtAmbInterval1 else None
        ambInterPlan = self.edtAmbInterPlan1.value() if self.edtAmbInterPlan1 else 0
        ambInterInterval = self.edtAmbInterInterval1.value() if self.edtAmbInterInterval1 else None
        ambPlan = ambPlan1 + ambPlan2 + ambInterPlan
        ambInterval = setInterval(ambInterval1, ambInterval2, ambInterInterval)

        homeTimeRange2 = self.edtHomeTimeRange12.timeRange() if self.edtHomeTimeRange12 else None
        if homeTimeRange2:
            timeStart2, timeFinish2 = homeTimeRange2
        else:
            timeStart2 = None
            timeFinish2 = None
        homeTimeRange1 = self.edtHomeTimeRange1.timeRange() if self.edtHomeTimeRange1 else None
        if homeTimeRange1:
            timeStart, timeFinish = homeTimeRange1
        else:
            timeStart = None
            timeFinish = None
        homeTimeRangeStart = min(timeStart, timeStart2) if (timeStart and timeStart2) else (timeStart if timeStart else (timeStart2 if timeStart2 else None))
        homeTimeRangeFinish = max(timeFinish, timeFinish2) if (timeFinish and timeFinish2) else (timeFinish if timeFinish else (timeFinish2 if timeFinish2 else None))
        if homeTimeRangeStart and homeTimeRangeFinish:
            homeTimeRange = homeTimeRangeStart, homeTimeRangeFinish
        else:
            homeTimeRange = None
        #        homeTimeRange = min(timeStart, timeStart2) if (timeStart and timeStart2) else (timeStart if timeStart else (timeStart2 if timeStart2 else None)), max(timeFinish, timeFinish2) if (timeFinish and timeFinish2) else (timeFinish if timeFinish else (timeFinish2 if timeFinish2 else None))
        homePlan2 = self.edtHomePlan12.value() if self.edtHomePlan12 else 0
        homeInterval2 = self.edtHomeInterval12.value() if self.edtHomeInterval12 else 0
        homePlan1 = self.edtHomePlan1.value() if self.edtHomePlan1 else 0
        homeInterval1 = self.edtHomeInterval1.value() if self.edtHomeInterval1 else 0
        homePlan = homePlan1 + homePlan2
        homeInterval = setInterval(homeInterval1, homeInterval2)

        ambColor1 = self.btnAmbColor1.currentColorName()
        if ambColor1 == u'#ffffff':
            ambColor1 == u'#ffffff'
        ambColor2 = self.btnAmbColor2.currentColorName()
        if ambColor2 == u'#ffffff':
            ambColor2 = None
        ambColorInter = self.btnAmbColorInter.currentColorName()
        if ambColorInter == u'#ffffff':
            ambColorInter = None
        ambColor = ambColor1
        notExternalSystem1 = self.chkNotExternalSystem1.isChecked()
        notExternalSystem2 = self.chkNotExternalSystem12.isChecked()
        notExternalSystemInter = self.chkInterNotExternalSystem1.isChecked()
        return [ambTimeRange1, ambOffice1, ambPlan1, ambInterval1, ambColor1, ambTimeRange2, ambOffice2, ambPlan2, ambInterval2, ambColor2, homeTimeRange1, homePlan1, homeInterval1, homeTimeRange2, homePlan2, homeInterval2, ambTimeRange, ambOffice, ambPlan, ambInterval, ambColor, homeTimeRange, homePlan, homeInterval, ambOfficeInter, ambInterPlan, ambInterInterval, ambColorInter, notExternalSystem1, notExternalSystem2, notExternalSystemInter]

    def loadData(self, dayInfo, selectedDate):
        self.selectedDate = selectedDate
        if dayInfo:
            self.edtAmbTimeRange1.setTimeRange(dayInfo[CTimeTableModel.ciAmbTimeRange1])
            self.edtAmbTimeRange12.setTimeRange(dayInfo[CTimeTableModel.ciAmbTimeRange2])
            self.edtAmbOffice1.setText(forceString(dayInfo[CTimeTableModel.ciAmbOffice1]))
            self.edtAmbOffice12.setText(forceString(dayInfo[CTimeTableModel.ciAmbOffice2]))
            self.edtAmbPlan1.setValue(forceInt(dayInfo[CTimeTableModel.ciAmbPlan1]))
            self.edtAmbInterval1.setValue(forceInt(dayInfo[CTimeTableModel.ciAmbInterval1]))
            self.edtAmbPlan12.setValue(forceInt(dayInfo[CTimeTableModel.ciAmbPlan2]))
            self.edtAmbInterval12.setValue(forceInt(dayInfo[CTimeTableModel.ciAmbInterval2]))
            self.edtHomeTimeRange1.setTimeRange(dayInfo[CTimeTableModel.ciHomeTimeRange1])
            self.edtHomeTimeRange12.setTimeRange(dayInfo[CTimeTableModel.ciHomeTimeRange2])
            self.edtHomePlan1.setValue(forceInt(dayInfo[CTimeTableModel.ciHomePlan1]))
            self.edtHomeInterval1.setValue(forceInt(dayInfo[CTimeTableModel.ciHomeInterval1]))
            self.edtHomePlan12.setValue(forceInt(dayInfo[CTimeTableModel.ciHomePlan2]))
            self.edtHomeInterval12.setValue(forceInt(dayInfo[CTimeTableModel.ciHomeInterval2]))
            self.btnAmbColor1.setCurrentColor(dayInfo[CTimeTableModel.ciAmbColor1])
            self.btnAmbColor2.setCurrentColor(dayInfo[CTimeTableModel.ciAmbColor2])
            self.edtAmbOfficeInter.setText(forceString(dayInfo[CTimeTableModel.ciAmbInterOffice]))
            self.edtAmbInterPlan1.setValue(forceInt(dayInfo[CTimeTableModel.ciAmbInterPlan]))
            self.edtAmbInterInterval1.setValue(forceInt(dayInfo[CTimeTableModel.ciAmbInterInterval]))
            self.btnAmbColorInter.setCurrentColor(dayInfo[CTimeTableModel.ciAmbInterColor])
            self.chkNotExternalSystem1.setChecked(dayInfo[CTimeTableModel.ciNotExternalSystem1])
            self.chkNotExternalSystem12.setChecked(dayInfo[CTimeTableModel.ciNotExternalSystem2])
            self.chkInterNotExternalSystem1.setChecked(dayInfo[CTimeTableModel.ciInterNotExternalSystem])

    def getCurrentObject(self, index, objects):
        ind = 1
        edit = objects[index] % (ind)
        indexTimeRange = None if index == 2 else index
        return ind, edit, indexTimeRange

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.FocusOut:
            if obj.objectName()[:15] == QtCore.QString('edtAmbTimeRange'):
                if not obj.timeRange():
                    callObjectAttributeMethod(self, listEdit['ambInterval'][2] % (1), 'setValue', 0)
                    callObjectAttributeMethod(self, listEdit['ambPlan'][2] % (1), 'setValue', 0)
                    return True
        return False

    def edtAmbTimeRange_editingFinished(self, index):
        ind, edit, indexTimeRange = self.getCurrentObject(index, listEdit['ambInterval'])
        interPlan = forceBool(getObjectAttribute(self, 'edtAmbInterPlan1').value())
        setSpinBoxInterval(self, ind, edit, indexTimeRange, listEdit['ambTimeRange'], interPlan)
        conversion(self, ind, edit, indexTimeRange, listEdit['ambPlan'], listEdit['ambTimeRange'])
        if interPlan:
            conversion(self, ind, 'edtAmbInterPlan%d' % (ind), None, listEdit['ambPlan'], None)

    def edtHomeTimeRange_editingFinished(self, index):
        ind, edit, indexTimeRange = self.getCurrentObject(index, listEdit['homeInterval'])
        setSpinBoxInterval(self, ind, edit, indexTimeRange, listEdit['homeTimeRange'])
        conversion(self, ind, edit, indexTimeRange, listEdit['homePlan'], listEdit['homeTimeRange'])

    def edtAmbPlan_editingFinished(self, index):
        ind, edit, indexTimeRange = self.getCurrentObject(index, listEdit['ambPlan'])
        conversion(self, ind, edit, indexTimeRange, listEdit['ambInterval'], listEdit['ambTimeRange'])

    def edtAmbInterval_editingFinished(self, index):
        ind, edit, indexTimeRange = self.getCurrentObject(index, listEdit['ambInterval'])
        conversion(self, ind, edit, indexTimeRange, listEdit['ambPlan'], listEdit['ambTimeRange'])

    def edtHomePlan_editingFinished(self, index):
        ind, edit, indexTimeRange = self.getCurrentObject(index, listEdit['homePlan'])
        conversion(self, ind, edit, indexTimeRange, listEdit['homeInterval'], listEdit['homeTimeRange'])

    def edtHomeInterval_editingFinished(self, index):
        ind, edit, indexTimeRange = self.getCurrentObject(index, listEdit['homeInterval'])
        conversion(self, ind, edit, indexTimeRange, listEdit['homePlan'], listEdit['homeTimeRange'])

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Close:
            self.close()
        elif buttonCode == QtGui.QDialogButtonBox.Ok:
            day = self.selectedDate.day() - 1
            data = self.getData()
            parent = QtCore.QObject.parent(self)
            QtGui.qApp.callWithWaitCursor(self, QtCore.QObject.parent(parent).setTaskPlanSecondPeriod, day, data)
            self.close()


class CPersonTimeTable(CTableView):
    def __init__(self, parent):
        CTableView.__init__(self, parent)
        self.verticalHeader().show()
        self.verticalHeader().setResizeMode(QtGui.QHeaderView.Fixed)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setStretchLastSection(True)
        self.setTabKeyNavigation(True)
        self.setEditTriggers(QtGui.QAbstractItemView.AnyKeyPressed | QtGui.QAbstractItemView.EditKeyPressed | QtGui.QAbstractItemView.SelectedClicked | QtGui.QAbstractItemView.DoubleClicked)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.timeRangeDelegate = CTimeRangeItemDelegate(self)
        self.officeDelegate = CAmbOfficeItemDelegate(self)
        self.planDelegate = CAmbPlanItemDelegate(self)
        self.colorDelegate = CColorItemDelegate(self)
        for column in [CPersonTimeTableModel.ciAmbTimeRange, CPersonTimeTableModel.ciAmbTimeRange2, CPersonTimeTableModel.ciHomeTimeRange, CPersonTimeTableModel.ciHomeTimeRange2]:
            self.setItemDelegateForColumn(column, self.timeRangeDelegate)
        for column in [CPersonTimeTableModel.ciAmbOffice, CPersonTimeTableModel.ciAmbOffice2]:
            self.setItemDelegateForColumn(column, self.officeDelegate)
        for column in [CPersonTimeTableModel.ciAmbPlan, CPersonTimeTableModel.ciAmbInterval, CPersonTimeTableModel.ciAmbPlan2, CPersonTimeTableModel.ciAmbInterval2, CPersonTimeTableModel.ciHomePlan, CPersonTimeTableModel.ciHomeInterval, CPersonTimeTableModel.ciHomePlan2, CPersonTimeTableModel.ciHomeInterval2]:
            self.setItemDelegateForColumn(column, self.planDelegate)
        for column in CPersonTimeTableModel.cilColor:
            self.setItemDelegateForColumn(column, self.colorDelegate)

    def setSelectionModel(self, selectionModel):
        currSelectionModel = self.selectionModel()
        if currSelectionModel:
            self.disconnect(currSelectionModel, QtCore.SIGNAL('currentChanged(QModelIndex,QModelIndex))'), self.currentChanged)
        QtGui.QTableView.setSelectionModel(self, selectionModel)
        if selectionModel:
            self.connect(selectionModel, QtCore.SIGNAL('currentChanged(QModelIndex,QModelIndex))'), self.currentChanged)


class CPersonTimeTableModel(QtCore.QAbstractTableModel):
    ciAmbTimeRange = 0
    ciAmbOffice = 1
    ciAmbPlan = 2
    ciAmbInterval = 3
    ciAmbColor = 4
    ciAmbTimeRange2 = 5
    ciAmbOffice2 = 6
    ciAmbPlan2 = 7
    ciAmbInterval2 = 8
    ciAmbColor2 = 9
    ciAmbOfficeInter = 10
    ciAmbInterPlan = 11
    ciAmbInterInterval = 12
    ciAmbColorInter = 13
    ciHomeTimeRange = 14
    ciHomePlan = 15
    ciHomeInterval = 16
    ciHomeTimeRange2 = 17
    ciHomePlan2 = 18
    ciHomeInterval2 = 19
    ciRecord = 20
    numCols = 21
    visibleCols = 20
    cilTimeRange = set([ciAmbTimeRange, ciAmbTimeRange2, ciHomeTimeRange, ciHomeTimeRange2])
    cilNum = set([ciAmbPlan, ciAmbInterval, ciAmbPlan2, ciAmbInterval2, ciHomePlan, ciHomeInterval, ciHomePlan2, ciHomeInterval2, ciAmbInterPlan, ciAmbInterInterval])
    cilPlan = set([ciAmbPlan, ciAmbPlan2, ciHomePlan, ciHomePlan2, ciAmbInterPlan])
    cilInterval = set([ciAmbInterval, ciAmbInterval2, ciHomeInterval, ciHomeInterval2, ciAmbInterInterval])
    cilOffice = set([ciAmbOffice, ciAmbOffice2, ciAmbOfficeInter])
    cilColor = set([ciAmbColor, ciAmbColor2, ciAmbColorInter])

    headerText = [u'Амбулаторно', u'Каб.', u'План', u'Интервал', u'Цвет', u'Амбулаторно2', u'Каб.2', u'План2', u'Интервал2', u'Цвет2', u'Каб. вне очереди', u'План вне очереди', u'Интервал вне очереди', u'Цвет вне очереди', u'Вызовы', u'План', u'Интервал', u'Вызовы2', u'План2', u'Интервал2']
    header0 = [u'Один день']
    header1 = [u'Нечётный день', u'Чётный день']
    header2 = [u'Понедельник', u'Вторник', u'Среда', u'Четверг', u'Пятница', u'Суббота', u'Воскресение']
    header3 = [u'Понедельник, нед.1', u'Вторник, нед.1', u'Среда, нед.1', u'Четверг, нед.1', u'Пятница, нед.1', u'Суббота, нед.1', u'Воскресение, нед.1', u'Понедельник, нед.2', u'Вторник, нед.2', u'Среда, нед.2', u'Четверг, нед.2', u'Пятница, нед.2', u'Суббота, нед.2', u'Воскресение, нед.2']
    header4 = [u'Понедельник, нед.1', u'Вторник, нед.1', u'Среда, нед.1', u'Четверг, нед.1', u'Пятница, нед.1', u'Суббота, нед.1', u'Воскресение, нед.1', u'Понедельник, нед.2', u'Вторник, нед.2', u'Среда, нед.2', u'Четверг, нед.2', u'Пятница, нед.2', u'Суббота, нед.2', u'Воскресение, нед.2', u'Понедельник, нед.3', u'Вторник, нед.3', u'Среда, нед.3', u'Четверг, нед.3', u'Пятница, нед.3', u'Суббота, нед.3', u'Воскресение, нед.3']
    header5 = [u'Понедельник, нед.1', u'Вторник, нед.1', u'Среда, нед.1', u'Четверг, нед.1', u'Пятница, нед.1', u'Суббота, нед.1', u'Воскресение, нед.1', u'Понедельник, нед.2', u'Вторник, нед.2', u'Среда, нед.2', u'Четверг, нед.2', u'Пятница, нед.2', u'Суббота, нед.2', u'Воскресение, нед.2', u'Понедельник, нед.3', u'Вторник, нед.3', u'Среда, нед.3', u'Четверг, нед.3', u'Пятница, нед.3', u'Суббота, нед.3', u'Воскресение, нед.3', u'Понедельник, нед.4', u'Вторник, нед.4', u'Среда, нед.4', u'Четверг, нед.4', u'Пятница, нед.4', u'Суббота, нед.4', u'Воскресение, нед.4']

    def __init__(self, parent):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.items = []
        self.countRow = 0
        self.typeTemplate = 0
        self.personId = None
        self.redBrush = QtGui.QBrush(QtGui.QColor(255, 0, 0))

    def columnCount(self, index=QtCore.QModelIndex()):
        return self.visibleCols

    def rowCount(self, index=QtCore.QModelIndex()):
        return self.countRow

    def flags(self, index=None):
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.headerText[section])
        if orientation == QtCore.Qt.Vertical and self.countRow:
            if role == QtCore.Qt.DisplayRole:
                if section < self.countRow:
                    if self.typeTemplate == 0:
                        return QtCore.QVariant(self.header0[0])
                    elif self.typeTemplate == 1:
                        return QtCore.QVariant(self.header1[section])
                    elif self.typeTemplate == 2:
                        return QtCore.QVariant(self.header2[section])
                    elif self.typeTemplate == 3:
                        return QtCore.QVariant(self.header3[section])
                    elif self.typeTemplate == 4:
                        return QtCore.QVariant(self.header4[section])
                    elif self.typeTemplate == 5:
                        return QtCore.QVariant(self.header5[section])
            if role == QtCore.Qt.ForegroundRole:
                if section in [5, 6, 12, 13, 19, 20, 26, 27]:
                    return QtCore.QVariant(self.redBrush)
                else:
                    return QtCore.QVariant()
        return QtCore.QVariant()

    def getRowCount(self, countRow, typeTemplate, personId=None):
        self.typeTemplate = typeTemplate
        self.personId = personId
        self.countRow = countRow
        self.rowCount()
        self.loadData(personId)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = index.column()
        row = index.row()

        if role == QtCore.Qt.EditRole:
            if row < self.countRow:
                if column in self.cilTimeRange:
                    return convertTimeRangeToVariant(self.items[row][column])
            return QtCore.QVariant(self.items[row][column])

        if role == QtCore.Qt.DisplayRole:
            if row < self.countRow:
                if column in self.cilTimeRange:
                    return toVariant(formatTimeRange(self.items[row][column]))
                if column in self.cilColor:
                    return QtCore.QVariant()
            return QtCore.QVariant(self.items[row][column])

        if role == QtCore.Qt.TextAlignmentRole:
            if row < self.countRow:
                if column not in self.cilNum:
                    return QtCore.QVariant(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            return QtCore.QVariant(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        if role == QtCore.Qt.BackgroundRole:
            if row < self.countRow:
                if column in self.cilColor and self.items[row][column]:
                    color = QtGui.QColor(self.items[row][column])
                    if color.isValid():
                        return QtCore.QVariant(QtGui.QBrush(color))
        return QtCore.QVariant()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            column = index.column()
            row = index.row()
            if row < self.countRow:
                if column in self.cilTimeRange:
                    newValue = convertVariantToTimeRange(value)
                elif column in self.cilNum:
                    newValue = forceInt(value)
                    if column in self.cilInterval:
                        if column != self.ciAmbInterInterval:
                            self.items[row][column - 1] = self.conversion(self.items[row][column - 3], newValue)
                        else:
                            self.items[row][column - 1] = self.conversion(self.getOutTurnTime(self.items[row][self.ciAmbTimeRange], self.items[row][self.ciAmbTimeRange2]), newValue)
                    if column in self.cilPlan:
                        if column != self.ciAmbInterPlan:
                            self.items[row][column + 1] = self.conversion(self.items[row][column - 2], newValue)
                        else:
                            self.items[row][column + 1] = self.conversion(self.getOutTurnTime(self.items[row][self.ciAmbTimeRange], self.items[row][self.ciAmbTimeRange2]), newValue)
                elif column in self.cilOffice:
                    newValue = forceStringEx(value)
                elif column in self.cilColor:
                    newValue = forceString(value)
                item = self.items[row]
                if item[column] != newValue:
                    item[column] = newValue
                    self.emitCellChanged(row, column)
            return True
        return False

    def conversion(self, timeRange, value):
        if timeRange:
            timeStart, timeFinish = timeRange
            diffTime = abs(timeFinish.secsTo(timeStart) / 60)
        else:
            return 0
        if value:
            return diffTime / value
        else:
            return 0

    def loadData(self, personId=None):
        self.items = []
        self.personId = personId
        db = QtGui.qApp.db
        table = db.table('Person_TimeTemplate')
        for day in xrange(self.countRow):
            record = table.newRecord()
            record.setValue('idx', QtCore.QVariant(day))
            dayInfo = [None] * (self.numCols - 1)
            dayInfo.append(record)
            self.items.append(dayInfo)
        if self.personId:
            records = db.getRecordList(table, '*', [table['master_id'].eq(self.personId)], 'idx')
            for record in records:
                idx = forceInt(record.value('idx'))
                if idx < self.countRow:
                    ambBegTime = forceTime(record.value('ambBegTime'))
                    ambEndTime = forceTime(record.value('ambEndTime'))
                    self.items[idx][self.ciAmbTimeRange] = None if (ambBegTime.isNull() and ambEndTime.isNull()) else (ambBegTime, ambEndTime)
                    self.items[idx][self.ciAmbOffice] = forceString(record.value('office'))
                    self.items[idx][self.ciAmbPlan] = forceString(record.value('ambPlan'))
                    self.items[idx][self.ciAmbInterval] = forceInt(record.value('ambInterval'))
                    self.items[idx][self.ciAmbColor] = forceString(record.value('ambColor'))
                    ambBegTime2 = forceTime(record.value('ambBegTime2'))
                    ambEndTime2 = forceTime(record.value('ambEndTime2'))
                    self.items[idx][self.ciAmbTimeRange2] = None if (ambBegTime2.isNull() and ambEndTime2.isNull()) else (ambBegTime2, ambEndTime2)
                    self.items[idx][self.ciAmbOffice2] = forceString(record.value('office2'))
                    self.items[idx][self.ciAmbPlan2] = forceString(record.value('ambPlan2'))
                    self.items[idx][self.ciAmbInterval2] = forceInt(record.value('ambInterval2'))
                    self.items[idx][self.ciAmbColor2] = forceString(record.value('ambColor2'))
                    self.items[idx][self.ciAmbOfficeInter] = forceString(record.value('officeInter'))
                    self.items[idx][self.ciAmbInterPlan] = forceInt(record.value('ambPlanInter'))
                    self.items[idx][self.ciAmbInterInterval] = forceInt(record.value('ambInterInterval'))
                    self.items[idx][self.ciAmbColorInter] = forceString(record.value('ambColorInter'))
                    homBegTime = forceTime(record.value('homBegTime'))
                    homEndTime = forceTime(record.value('homEndTime'))
                    self.items[idx][self.ciHomeTimeRange] = None if (homBegTime.isNull() and homEndTime.isNull()) else (homBegTime, homEndTime)
                    self.items[idx][self.ciHomePlan] = forceString(record.value('homPlan'))
                    self.items[idx][self.ciHomeInterval] = forceInt(record.value('homInterval'))
                    homBegTime2 = forceTime(record.value('homBegTime2'))
                    homEndTime2 = forceTime(record.value('homEndTime2'))
                    self.items[idx][self.ciHomeTimeRange2] = None if (homBegTime2.isNull() and homEndTime2.isNull()) else (homBegTime2, homEndTime2)
                    self.items[idx][self.ciHomePlan2] = forceString(record.value('homPlan2'))
                    self.items[idx][self.ciHomeInterval2] = forceInt(record.value('homInterval2'))
                    self.items[idx][self.ciRecord] = record
        self.reset()

    def saveData(self):
        if self.personId:
            db = QtGui.qApp.db
            table = db.table('Person_TimeTemplate')
            idList = []
            masterId = QtCore.QVariant(self.personId)
            for idx in xrange(self.countRow):
                record = self.items[idx][self.ciRecord]
                record.setValue('idx', QtCore.QVariant(idx))

                ambTimeRange = self.items[idx][self.ciAmbTimeRange]
                if ambTimeRange:
                    ambBegTime, ambEndTime = ambTimeRange
                else:
                    ambBegTime = None
                    ambEndTime = None
                record.setValue('ambBegTime', QtCore.QVariant(ambBegTime))
                record.setValue('ambEndTime', QtCore.QVariant(ambEndTime))
                record.setValue('office', QtCore.QVariant(self.items[idx][self.ciAmbOffice]))
                record.setValue('ambPlan', QtCore.QVariant(self.items[idx][self.ciAmbPlan]))
                record.setValue('ambInterval', QtCore.QVariant(self.items[idx][self.ciAmbInterval]))
                record.setValue('ambColor', QtCore.QVariant(self.items[idx][self.ciAmbColor]))

                ambTimeRange2 = self.items[idx][self.ciAmbTimeRange2]
                if ambTimeRange2:
                    ambBegTime2, ambEndTime2 = ambTimeRange2
                else:
                    ambBegTime2 = None
                    ambEndTime2 = None
                record.setValue('ambBegTime2', QtCore.QVariant(ambBegTime2))
                record.setValue('ambEndTime2', QtCore.QVariant(ambEndTime2))
                record.setValue('office2', QtCore.QVariant(self.items[idx][self.ciAmbOffice2]))
                record.setValue('ambPlan2', QtCore.QVariant(self.items[idx][self.ciAmbPlan2]))
                record.setValue('ambInterval2', QtCore.QVariant(self.items[idx][self.ciAmbInterval2]))
                record.setValue('ambColor2', QtCore.QVariant(self.items[idx][self.ciAmbColor2]))

                record.setValue('officeInter', QtCore.QVariant(self.items[idx][self.ciAmbOfficeInter]))
                record.setValue('ambPlanInter', QtCore.QVariant(self.items[idx][self.ciAmbInterPlan]))
                record.setValue('ambInterInterval', QtCore.QVariant(self.items[idx][self.ciAmbInterInterval]))
                record.setValue('ambColorInter', QtCore.QVariant(self.items[idx][self.ciAmbColorInter]))

                homTimeRange = self.items[idx][self.ciHomeTimeRange]
                if homTimeRange:
                    homBegTime, homEndTime = homTimeRange
                else:
                    homBegTime = None
                    homEndTime = None
                record.setValue('homBegTime', QtCore.QVariant(homBegTime))
                record.setValue('homEndTime', QtCore.QVariant(homEndTime))
                record.setValue('homPlan', QtCore.QVariant(self.items[idx][self.ciHomePlan]))
                record.setValue('homInterval', QtCore.QVariant(self.items[idx][self.ciHomeInterval]))

                homTimeRange2 = self.items[idx][self.ciHomeTimeRange2]
                if homTimeRange2:
                    homBegTime2, homEndTime2 = homTimeRange2
                else:
                    homBegTime2 = None
                    homEndTime2 = None
                record.setValue('homBegTime2', QtCore.QVariant(homBegTime2))
                record.setValue('homEndTime2', QtCore.QVariant(homEndTime2))
                record.setValue('homPlan2', QtCore.QVariant(self.items[idx][self.ciHomePlan2]))
                record.setValue('homInterval2', QtCore.QVariant(self.items[idx][self.ciHomeInterval2]))

                if ambTimeRange or ambTimeRange2 or homTimeRange or homTimeRange2:
                    record.setValue('master_id', masterId)
                    id = db.insertOrUpdate(table, record)
                    record.setValue('id', QtCore.QVariant(id))
                    idList.append(id)
            filter = [table['master_id'].eq(masterId),
                      'NOT (' + table['id'].inlist(idList) + ')']
            db.deleteRecord(table, filter)

    def getOutTurnTime(self, ambTimeRange1, ambTimeRange2):
        if ambTimeRange1 and ambTimeRange2:
            return ambTimeRange1[1], ambTimeRange2[0]
        return None

    def emitCellChanged(self, row, column):
        index = self.index(row, column)
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)
