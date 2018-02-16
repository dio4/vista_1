# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Timeline.TimeTable import invertGapList, calcTimePlanEx, recreateTimeByGaps
from library.ElectronicQueue.EQTicketModel import CEQTicketModel
from library.TableView import CTableView
from library.TimeEdit import CTimeEdit, CTimeRangeEdit
from library.Utils import forceBool, forceDateTime, forceDate, forceDouble, forceInt, forceRef, forceTime, \
    toVariant, formatDate, forceString


def formatTimeRange(timeRange):
    if timeRange:
        start, finish = timeRange
        return start.toString('HH:mm') + ' - ' + finish.toString('HH:mm')
    else:
        return ''


def convertTimeRangeToVariant(range):
    if range:
        start, finish = range
        return QtCore.QVariant.fromList([QtCore.QVariant(start), QtCore.QVariant(finish)])
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


class CJobPlanItem(object):
    def __init__(self):
        self.record = None
        self.timeRange = None
        self.oldTimeRange = None
        self.quantity = 0
        self.oldQuantity = 0
        self.isOvertime = False
        self.oldIsOvertime = False
        self.limitSuperviseUnit = 0.0
        self.oldLimitSuperviseUnit = 0.0
        self.personQuota = 100
        self.oldPersonQuota = 100
        self.reserved = 0
        self.busy = 0
        self.executed = 0
        self.tickets = []
        self.ticketIsDirty = []
        self.forceChange = False
        self.eQueueTypeId = None
        self.oldEQueueTypeId = None
        self._eQueueRecord = None

    def countUsed(self):
        return self.reserved + self.busy + self.executed

    def changed(self):
        return self.timeRange != self.oldTimeRange \
               or self.quantity != self.oldQuantity \
               or self.isOvertime != self.oldIsOvertime \
               or self.limitSuperviseUnit != self.oldLimitSuperviseUnit \
               or self.personQuota != self.oldPersonQuota \
               or self.eQueueTypeId != self.oldEQueueTypeId \
               or self.forceChange

    def setRecord(self, record):
        self.record = record
        self.timeRange = forceTime(record.value('begTime')), forceTime(record.value('endTime'))
        self.oldTimeRange = self.timeRange
        self.quantity = forceInt(record.value('quantity'))
        self.oldQuantity = self.quantity
        self.isOvertime = forceBool(record.value('isOvertime'))
        self.oldIsOvertime = self.isOvertime
        self.limitSuperviseUnit = forceDouble(record.value('limitSuperviseUnit'))
        self.oldLimitSuperviseUnit = self.limitSuperviseUnit
        self.personQuota = forceDouble(record.value('personQuota'))
        self.oldPersonQuota = self.personQuota
        self.eQueueTypeId = forceRef(record.value('eQueueType_id'))
        self.oldEQueueTypeId = self.eQueueTypeId
        self.reserved = 0
        self.busy = 0
        self.executed = 0
        db = QtGui.qApp.db
        tableTicket = db.table('Job_Ticket')
        cols = [
            tableTicket['id'],
            tableTicket['master_id'],
            tableTicket['idx'],
            tableTicket['datetime'],
            tableTicket['resTimestamp'],
            tableTicket['resConnectionId'],
            tableTicket['status'],
            tableTicket['begDateTime'],
            tableTicket['endDateTime'],
            tableTicket['label'],
            tableTicket['note'],
            '''
            EXISTS
            (
                SELECT ActionProperty_Job_Ticket.value
                FROM Job_Ticket AS JT
                LEFT JOIN ActionProperty_Job_Ticket ON ActionProperty_Job_Ticket.value = JT.id
                LEFT JOIN ActionProperty ON ActionProperty.id = ActionProperty_Job_Ticket.id
                LEFT JOIN Action ON Action.id = ActionProperty.action_id
                LEFT JOIN ActionType ON ActionType.id = Action.actionType_id
                WHERE
					JT.id=Job_Ticket.id
                    AND Action.deleted = 0
                    AND ActionType.deleted = 0
                    AND ActionProperty.deleted = 0
                ORDER BY JT.id
            ) AS usedInActionProperty
            '''
        ]
        self.tickets = db.getRecordList(
            tableTicket, cols, tableTicket['master_id'].eq(record.value('id')), 'Job_Ticket.id'
        )
        for ticket in self.tickets:
            status = forceInt(ticket.value('status'))
            usedInActionProperty = forceBool(ticket.value('usedInActionProperty'))
            if usedInActionProperty:
                if status == 0:
                    self.reserved += 1
                elif status == 1:
                    self.busy += 1
                elif status == 2:
                    self.executed += 1
        self.ticketIsDirty = [False] * len(self.tickets)

        self._eQueueRecord = CEQTicketModel.getEQueueRecord(db.db, self.eQueueTypeId, forceDate(record.value('date')))

    def updateRecord(self, orgStructureJobId, jobTypeId, date):
        db = QtGui.qApp.db
        orgStructureId = forceRef(db.translate('OrgStructure_Job', 'id', orgStructureJobId, 'master_id'))
        if not self.record:
            if self.timeRange or self.quantity:
                tableJob = db.table('Job')
                self.record = tableJob.newRecord()
                self.record.setValue('orgStructure_id', toVariant(orgStructureId))
                self.record.setValue('orgStructureJob_id', toVariant(orgStructureJobId))
                self.record.setValue('jobType_id', toVariant(jobTypeId))
                self.record.setValue('date', toVariant(date))
                self._eQueueRecord = CEQTicketModel.getEQueueRecord(db.db, self.eQueueTypeId, date)
        if self.record:
            self.quantity = max(self.quantity, self.countUsed())
            begTime, endTime = self.timeRange if self.timeRange else (None, None)
            self.record.setValue('begTime', toVariant(begTime))
            self.record.setValue('endTime', toVariant(endTime))
            self.record.setValue('quantity', toVariant(self.quantity))
            self.record.setValue('isOvertime', toVariant(self.isOvertime))
            self.record.setValue('limitSuperviseUnit', toVariant(self.limitSuperviseUnit))
            self.record.setValue('personQuota', toVariant(self.personQuota))
            self.record.setValue('eQueueType_id', toVariant(self.eQueueTypeId))
            if self._eQueueRecord is None:
                self._eQueueRecord = CEQTicketModel.getEQueueRecord(db.db, self.eQueueTypeId, date)
            else:
                # FIXME: atronah: EQ: хз, что будет, если на дату "date" уже есть другая очередь с тем же типом.. хотя,
                # врядли вообще date может меняться между вызовами updateRecord()
                self._eQueueRecord.setValue('date', toVariant(date))

            tableTicket = db.table('Job_Ticket')
            if len(self.tickets) > self.quantity:
                i = len(self.tickets)
                while i > 0 and len(self.tickets) > self.quantity:
                    i -= 1
                    ticket = self.tickets[i]
                    if not forceBool(ticket.value('usedInActionProperty')):
                        del self.tickets[i]
                        del self.ticketIsDirty[i]

            else:
                while len(self.tickets) < self.quantity:
                    self.tickets.append(tableTicket.newRecord(['id', 'master_id', 'datetime', 'idx']))
                    self.ticketIsDirty.append(True)

            timePlan = getTimePlan(self.timeRange, self.quantity, orgStructureId)
            for i, ticket in enumerate(self.tickets):
                datetime = forceDateTime(QtCore.QDateTime(date, timePlan[i]) if i < len(timePlan) else None)
                oldDatetime = forceDateTime(ticket.value('datetime'))
                oldIdx = forceInt(ticket.value('idx'))
                if oldDatetime != datetime or oldIdx != i:
                    ticket.setValue('datetime', toVariant(datetime))
                    ticket.setValue('idx', toVariant(i))
                    self.ticketIsDirty[i] = True

    def saveRecord(self):
        jobTicketIdList = []
        db = QtGui.qApp.db
        tableJob = db.table('Job')
        tableTicket = db.table('Job_Ticket')

        tableEQueueTicket = db.table('EQueueTicket')

        id = db.insertOrUpdate(tableJob, self.record)

        eQueueId = None
        eqIndexOffset = 0
        if self.eQueueTypeId:
            if self._eQueueRecord is None:
                self._eQueueRecord = CEQTicketModel.getEQueueRecord(
                    db.db, self.eQueueTypeId, forceDate(self.record.value('date'))
                )
            eQueueId = db.insertOrUpdate(db.table('EQueue'), self._eQueueRecord)

            eqIndexOffset, _, errorInfo = CJobPlanModel.getEQTicketIndexRange(
                forceDate(self.record.value('date')),
                self.eQueueTypeId,
                forceRef(self.record.value('jobType_id')),
                self.timeRange[0],
                self.timeRange[1]
            )
            assert len(errorInfo) == 0

        assert id is not None

        for i, ticket in enumerate(self.tickets):
            jobTicketId = forceRef(ticket.value('id'))
            eQueueTicketId = None
            if eQueueId:
                eQueueTicketId = forceRef(ticket.value('eQueueTicket_id'))
                if not eQueueTicketId:
                    eQueueTicketRecord = CEQTicketModel.getEQueueTicketRecord(
                        db.db, eQueueId, eqIndexOffset + forceInt(ticket.value('idx'))
                    )
                    if eQueueTicketRecord and not eQueueTicketRecord.isEmpty():
                        eQueueTicketId = forceRef(eQueueTicketRecord.value('id'))
                        if not eQueueTicketId:
                            eQueueTicketId = db.insertOrUpdate(db.table('EQueueTicket'), eQueueTicketRecord)
                    self.ticketIsDirty[i] = True
            if self.ticketIsDirty[i] or forceInt(ticket.value('master_id')) != id:
                record = tableTicket.newRecord(['id', 'master_id', 'datetime', 'idx', 'eQueueTicket_id'])
                record.setValue('id', ticket.value('id'))
                record.setValue('master_id', toVariant(id))
                record.setValue('datetime', ticket.value('datetime'))
                record.setValue('idx', ticket.value('idx'))
                record.setValue('eQueueTicket_id', toVariant(eQueueTicketId))
                jobTicketId = db.insertOrUpdate(tableTicket, record)

            if jobTicketId:
                jobTicketIdList.append(jobTicketId)
        if jobTicketIdList:
            db.deleteRecord(tableTicket,
                            [tableTicket['master_id'].eq(id),
                             tableTicket['id'].notInlist(jobTicketIdList)])
        else:
            db.deleteRecord(tableTicket,
                            [tableTicket['master_id'].eq(id)])

        deleteQueryTable = tableEQueueTicket.leftJoin(
            tableTicket, tableTicket['eQueueTicket_id'].eq(tableEQueueTicket['id'])
        )
        db.query('DELETE %s.* FROM %s %s' % (
            tableEQueueTicket.name(),
            deleteQueryTable.name(),
            db.prepareWhere([tableEQueueTicket['queue_id'].eq(eQueueId), tableTicket['id'].isNull()])
        ))


class CJobPlanModel(QtCore.QAbstractTableModel):
    monthlyChoice = False
    ciTime = 0
    ciPlan = 1
    ciIsOvertime = 2
    ciLimitSuperviseUnit = 3
    ciPersonQuota = 4
    ciReserve = 5
    ciBusy = 6
    ciExecute = 7
    ciEQ = 8
    headerText = [
        u'Время', u'План', u'Сверх плана', u'Лимит ед.учета', u'Врачебная квота', u'Резерв', u'Занято', u'Закончено',
        u'Тип эл.очереди'
    ]

    actionsTypesChecked = False

    error = QtCore.pyqtSignal(QtCore.QString)

    def __init__(self, parent):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.orgStructureJobId = None
        self.jobTypeId = None
        self.year = None
        self.month = None
        self.begDate = None
        self.daysInMonth = 0
        self.items = []
        self.redDays = []
        self.redBrush = QtGui.QBrush(QtGui.QColor(255, 0, 0))

    def columnCount(self, index=QtCore.QModelIndex()):
        return 6

    def rowCount(self, index=QtCore.QModelIndex()):
        return self.daysInMonth

    def flags(self, index):
        column = index.column()
        result = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        if column in [self.ciTime, self.ciPlan, self.ciLimitSuperviseUnit, self.ciPersonQuota]:
            result |= QtCore.Qt.ItemIsEditable
        if column == self.ciIsOvertime:
            result |= QtCore.Qt.ItemIsUserCheckable
        return result

    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = index.column()
        row = index.row()

        if role == QtCore.Qt.EditRole:
            if row < self.daysInMonth:
                item = self.items[row]
                if column == self.ciTime:
                    return convertTimeRangeToVariant(item.timeRange)
                elif column == self.ciPlan:
                    return toVariant(item.quantity)
                elif column == self.ciLimitSuperviseUnit:
                    return toVariant(item.limitSuperviseUnit)
                elif column == self.ciPersonQuota:
                    return toVariant(item.personQuota)
        elif role == QtCore.Qt.DisplayRole:
            if row < self.daysInMonth:
                item = self.items[row]
                if column == self.ciTime:
                    return toVariant(formatTimeRange(item.timeRange))
                elif column == self.ciPlan:
                    return toVariant(item.quantity)
                elif column == self.ciLimitSuperviseUnit:
                    return toVariant(item.limitSuperviseUnit)
                elif column == self.ciPersonQuota:
                    return toVariant(item.personQuota)
                elif column == self.ciReserve:
                    return toVariant(item.reserved)
                elif column == self.ciBusy:
                    return toVariant(item.busy)
                elif column == self.ciExecute:
                    return toVariant(item.executed)

        elif role == QtCore.Qt.CheckStateRole:
            if row < self.daysInMonth:
                item = self.items[row]
                if column == self.ciIsOvertime:
                    return toVariant(QtCore.Qt.Checked if item.isOvertime else QtCore.Qt.Unchecked)
        elif role == QtCore.Qt.TextAlignmentRole:
            if row < self.daysInMonth:
                if column == self.ciPlan:
                    return QtCore.QVariant(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            return QtCore.QVariant(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        return QtCore.QVariant()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            column = index.column()
            row = index.row()
            old = None

            if row < self.daysInMonth:
                item = self.items[row]
                valueChanged = False
                if column == self.ciTime:
                    newValue = convertVariantToTimeRange(value)
                    valueChanged = item.timeRange != newValue
                    if valueChanged and self.checkEQRangeIntersection(
                            row, item.eQueueTypeId, newValue, item.quantity
                    ):
                        item.timeRange = newValue
                    else:
                        return False
                elif column == self.ciPlan:
                    newValue = forceInt(value)
                    valueChanged = item.quantity != newValue

                    newValue = max(newValue, item.countUsed())
                    if valueChanged and self.checkEQRangeIntersection(
                            row, item.eQueueTypeId, item.timeRange, newValue
                    ):
                        old = item.quantity
                        item.quantity = newValue
                    else:
                        return False

                elif column == self.ciLimitSuperviseUnit:
                    newValue = forceDouble(value)
                    valueChanged = item.limitSuperviseUnit != newValue
                    item.limitSuperviseUnit = newValue if newValue > 0 else 0.0
                elif column == self.ciPersonQuota:
                    newValue = forceInt(value)
                    valueChanged = item.personQuota != newValue
                    newValue = newValue if newValue > 0 else 0
                    newValue = newValue if newValue < 100 else 100
                    item.personQuota = newValue
                if valueChanged:
                    self.emitCellChanged(row, column, old)
            return True
        elif role == QtCore.Qt.CheckStateRole:
            column = index.column()
            row = index.row()
            if row < self.daysInMonth:
                item = self.items[row]
                valueChanged = False
                if column == self.ciIsOvertime:
                    newValue = forceInt(value) == QtCore.Qt.Checked
                    valueChanged = item.isOvertime != newValue
                    item.isOvertime = newValue
                if valueChanged:
                    self.emitCellChanged(row, column)
            return True
        return False

    @staticmethod
    def getEQTicketOnDayRecordList(date, eQueueTypeId, exceptJobTypeId):
        db = QtGui.qApp.db
        tableJob = db.table('Job')
        tableJobTicket = db.table('Job_Ticket')
        tableJobType = db.table('rbJobType')
        tableEQueueTicket = db.table('EQueueTicket')

        queryTable = tableJob.innerJoin(
            tableJobTicket, tableJobTicket['master_id'].eq(tableJob['id'])
        )
        queryTable = queryTable.innerJoin(
            tableEQueueTicket, tableEQueueTicket['id'].eq(tableJobTicket['eQueueTicket_id'])
        )
        queryTable = queryTable.innerJoin(
            tableJobType, tableJobType['id'].eq(tableJob['jobType_id'])
        )

        cols = [tableJob['begTime'],
                tableJob['endTime'],
                'min(%s) AS minEQIndex' % tableEQueueTicket['idx'].name(),
                'max(%s) AS maxEQIndex' % tableEQueueTicket['idx'].name(),
                tableJobType['name'].alias('jobName')
                ]

        cond = [tableJob['date'].eq(date),
                tableJob['jobType_id'].ne(exceptJobTypeId),
                tableJob['eQueueType_id'].eq(eQueueTypeId)]

        order = [tableJob['begTime']]

        return db.getRecordListGroupBy(queryTable, cols=cols, where=cond, group=tableJob['id'], order=order)

    @staticmethod
    def getEQTicketIndexRange(date, eQueueTypeId, exceptJobTypeId, currentBegTime, currentEndTime):
        minAvailableEQIndex = 0
        maxAvailableEQIndex = None
        errorMessage = u''

        recordList = CJobPlanModel.getEQTicketOnDayRecordList(date, eQueueTypeId, exceptJobTypeId)
        for record in recordList:
            begTime = forceTime(record.value('begTime'))
            endTime = forceTime(record.value('endTime'))
            if currentBegTime >= endTime:
                minAvailableEQIndex = forceInt(record.value('maxEQIndex')) + 1
            else:
                if currentEndTime > begTime:
                    errorMessage = u'\n'.join([
                        u'Обнаружено недопустимо пересечение периода',
                        u'текущей работы (%s) с работой "%s" (%s)' % (
                            formatTimeRange((currentBegTime, currentEndTime)),
                            forceString(record.value('jobName')),
                            formatTimeRange((begTime, endTime))
                        ),
                        u'на %s' % formatDate(date)])
                    break
                maxAvailableEQIndex = forceInt(record.value('minEQIndex')) - 1
                break
        return minAvailableEQIndex, maxAvailableEQIndex, errorMessage

    def checkEQRangeIntersection(self, day, eQueueTypeId, timeRange, quantity):
        if not eQueueTypeId:
            return True

        date = self.begDate.addDays(day % self.begDate.daysInMonth())

        currentBegTime, currentEndTime = timeRange
        minAvailableEQIndex, maxAvailableEQIndex, errorInfo = self.getEQTicketIndexRange(
            date, eQueueTypeId, self.jobTypeId, currentBegTime, currentEndTime
        )

        errorMessageTemplate = u'Неудалось создать расписание для эл. очереди.\n%s'
        if errorInfo:
            self.error.emit(QtCore.QString(errorMessageTemplate % errorInfo))
            return False

        elif maxAvailableEQIndex is not None and quantity > (maxAvailableEQIndex - minAvailableEQIndex + 1):
            errorInfo = u'\n'.join([
                u'Требуемое кол-во номерков (%s) не соответствует' % quantity,
                u'доступному диапазону номеров (%s - %s) с учетом идущей следом работы' % (
                    minAvailableEQIndex, maxAvailableEQIndex
                ),
                u'привязанной к этой же электронной очереди',
                u'на %s' % formatDate(date)]
            )
            self.error.emit(QtCore.QString(errorMessageTemplate % errorInfo))
            return False
        return True

    def messageBoxQuantity(self, row, column, quantityPrevChosen):
        if self.items[row].quantity < self.items[row].oldQuantity and self.monthlyChoice == False:
            answer = QtGui.QMessageBox.question(
                None,
                u'Cменa плана',
                u'Вы уверены, что хотите поменять план? Назначенные номерки могут удалиться',
                QtGui.QMessageBox.Yes, QtGui.QMessageBox.No
            )
            if answer == QtGui.QMessageBox.Yes:
                index = self.index(row, column)
                self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)
            else:
                self.items[row].quantity = quantityPrevChosen

    def emitCellChanged(self, row, column, quantity=None):
        if column == self.ciPlan:
            self.messageBoxQuantity(row, column, quantity)
        else:
            index = self.index(row, column)
            self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.headerText[section])
        if orientation == QtCore.Qt.Vertical and self.daysInMonth:
            if role == QtCore.Qt.DisplayRole:
                if section < self.daysInMonth:
                    return QtCore.QVariant(section + 1)
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

    def setJobAndMonth(self, orgStructureJobId, jobTypeId, year, month):
        if self.orgStructureJobId != orgStructureJobId \
                or self.jobTypeId != jobTypeId \
                or self.year != year \
                or self.month != month:
            self.saveData()
            self.loadData(orgStructureJobId, jobTypeId, year, month)

    def saveData(self):
        if self.orgStructureJobId and self.jobTypeId and self.year and self.month:
            db = QtGui.qApp.db
            db.transaction()
            try:
                for day in xrange(self.daysInMonth):
                    item = self.items[day]
                    if item.changed():
                        item.updateRecord(
                            self.orgStructureJobId, self.jobTypeId, QtCore.QDate(self.year, self.month, day + 1)
                        )
                        if item.record:
                            item.saveRecord()
                db.commit()
            except:
                db.rollback()
                QtGui.qApp.logCurrentException()
                raise

    def loadData(self, orgStructureJobId, jobTypeId, year, month):
        self.orgStructureJobId = orgStructureJobId
        self.jobTypeId = jobTypeId
        self.year = year
        self.month = month
        self.begDate = QtCore.QDate(year, month, 1)
        self.daysInMonth = self.begDate.daysInMonth()
        self.redDays = []
        for day in xrange(self.daysInMonth):
            self.redDays.append(
                QtCore.QDate(year, month, day + 1).dayOfWeek() in [QtCore.Qt.Saturday, QtCore.Qt.Sunday]
            )

        self.items = [CJobPlanItem() for day in xrange(self.daysInMonth)]
        db = QtGui.qApp.db
        tableJob = db.table('Job')

        records = db.getRecordList(tableJob, '*',
                                   [tableJob['orgStructureJob_id'].eq(orgStructureJobId),
                                    tableJob['jobType_id'].eq(jobTypeId),
                                    tableJob['deleted'].eq(0),
                                    tableJob['date'].ge(self.begDate),
                                    tableJob['date'].lt(self.begDate.addMonths(1)),
                                    ])

        for record in records:
            day = self.begDate.daysTo(forceDate(record.value('date')))
            self.items[day].setRecord(record)
        self.reset()

    def setWorkPlan(self, plan, dateRange, eQueueTypeId=None):

        (begDate, endDate) = dateRange
        if not begDate:
            begDate = self.begDate
        if not endDate:
            endDate = self.begDate.addDays(self.daysInMonth - 1)

        (daysPlan, setRedDays) = plan
        daysPlanLen = len(daysPlan)

        startDay, finishDay = self.begDate.daysTo(begDate), self.begDate.daysTo(endDate) + 1

        # Проверка возможности создания работы с привязкой к эл. очереди.
        if eQueueTypeId:
            for day in xrange(startDay, finishDay):
                if daysPlanLen <= 2 and self.redDays[day] and not setRedDays:
                    continue

                # OPTIMIZE: atronah: Можно заменить на простой инкремент с вычислением остатка его деления на константу
                # (вычислив до цикла стартовое значение и делитель для получения остатка)
                planIndex = (day % daysPlanLen) if daysPlanLen <= 2 else (self.begDate.addDays(day).dayOfWeek() - 1)
                timeRange, quantity = daysPlan[planIndex][:2]
                if not self.checkEQRangeIntersection(day, eQueueTypeId, timeRange, quantity):
                    return False

        if daysPlanLen <= 2 or daysPlanLen == 7:
            for day in xrange(startDay, finishDay):
                if daysPlanLen <= 2 and self.redDays[day] and not setRedDays:
                    continue
                planIndex = (day % daysPlanLen) if daysPlanLen <= 2 else (self.begDate.addDays(day).dayOfWeek() - 1)
                self.setDayPlan(day, daysPlan[planIndex], eQueueTypeId)
                self.monthlyChoice = True

    def setDayPlan(self, day, dayPlan, eQueueTypeId=None):
        timeRange, quantity, isOvertime, limitSuperviseUnit, personQuota = dayPlan
        dayInfo = self.items[day]
        dayInfo.timeRange = timeRange
        dayInfo.quantity = max(quantity, dayInfo.countUsed())
        dayInfo.isOvertime = isOvertime
        dayInfo.limitSuperviseUnit = limitSuperviseUnit
        dayInfo.personQuota = personQuota
        dayInfo.eQueueTypeId = eQueueTypeId

        self.emitCellChanged(day, self.ciTime)
        self.emitCellChanged(day, self.ciPlan)
        self.emitCellChanged(day, self.ciIsOvertime)
        self.emitCellChanged(day, self.ciLimitSuperviseUnit)
        self.emitCellChanged(day, self.ciPersonQuota)
        self.emitCellChanged(day, self.ciEQ)

    def copyDayFromDate(self, day, sourceDate):
        db = QtGui.qApp.db
        tableJob = db.table('Job')

        record = db.getRecordEx(
            tableJob,
            (
                'begTime',
                'endTime',
                'quantity',
                'isOvertime',
                'limitSuperviseUnit',
                'personQuota',
                'eQueueType_id'
            ),
            [
                tableJob['orgStructureJob_id'].eq(self.orgStructureJobId),
                tableJob['jobType_id'].eq(self.jobTypeId),
                tableJob['deleted'].eq(0),
                tableJob['date'].eq(sourceDate),
            ])
        if record:
            timeRange = forceTime(record.value('begTime')), forceTime(record.value('endTime'))
            quantity = forceInt(record.value('quantity'))
            isOvertime = forceBool(record.value('isOvertime'))
            limitSuperviseUnit = forceDouble(record.value('limitSuperviseUnit'))
            personQuota = forceInt(record.value('personQuota'))
            eQueueTypeId = forceRef(record.value('eQueueType_id'))
        else:
            timeRange = None
            quantity = 0
            isOvertime = False
            limitSuperviseUnit = 0.0
            personQuota = 100
            eQueueTypeId = None
        if not self.checkEQRangeIntersection(day, eQueueTypeId, timeRange, quantity):
            return
        self.setDayPlan(day, (timeRange, quantity, isOvertime, limitSuperviseUnit, personQuota), eQueueTypeId)

    def copyDataFromPrevDate(self, startDate, mode, fillRedDays):
        startDateDow = startDate.dayOfWeek()
        if mode == 0:  # один день
            fixedStartDate = startDate.addDays(0 if fillRedDays or startDateDow not in (6, 7)  else 2)
            for day in range(self.daysInMonth):
                if fillRedDays or not self.redDays[day]:
                    self.copyDayFromDate(day, fixedStartDate)
                else:
                    self.setDayPlan(day, (None, 0, False, 0.0, 0))

        elif mode == 1:  # два дня
            fixedStartDates = [startDate.addDays(0 if fillRedDays or startDateDow not in (6, 7) else 2),
                               startDate.addDays(1 if fillRedDays or startDateDow not in (5, 6) else 3)]
            for day in range(self.daysInMonth):
                if fillRedDays or not self.redDays[day]:
                    self.copyDayFromDate(day, fixedStartDates[day % 2])
                else:
                    self.setDayPlan(day, (None, 0, False, 0.0, 0))
        else:  # mode == 2: # неделя
            for day in xrange(self.daysInMonth):
                offset = (self.begDate.addDays(day).dayOfWeek() - startDateDow) % 7  # yes, it is python '%'
                self.copyDayFromDate(day, startDate.addDays(offset))

    def updateSums(self, column, emitChanges=True):
        pass

    def updateAttrs(self):
        pass


class CTimeRangeItemDelegate(QtGui.QItemDelegate):
    def __init__(self, parent=None):
        QtGui.QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        editor = CTimeRangeEdit(parent)
        return editor

    def setEditorData(self, editor, index):
        model = index.model()
        data = model.data(index, QtCore.Qt.EditRole)
        editor.setTimeRange(convertVariantToTimeRange(data))

    def setModelData(self, editor, model, index):
        model.setData(index, convertTimeRangeToVariant(editor.timeRange()))


class CTimeItemDelegate(QtGui.QItemDelegate):
    def __init__(self, parent=None):
        QtGui.QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        editor = CTimeEdit(parent)
        return editor

    def setEditorData(self, editor, index):
        model = index.model()
        data = model.data(index, QtCore.Qt.EditRole)
        editor.setTime(data.toTime())

    def setModelData(self, editor, model, index):
        model.setData(index, QtCore.QVariant(editor.time()))


class CJobPlanTable(CTableView):
    def __init__(self, parent):
        CTableView.__init__(self, parent)
        self.verticalHeader().show()
        self.verticalHeader().setResizeMode(QtGui.QHeaderView.Fixed)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setStretchLastSection(True)
        self.setTabKeyNavigation(True)
        self.setEditTriggers(
            QtGui.QAbstractItemView.AnyKeyPressed
            | QtGui.QAbstractItemView.EditKeyPressed
            | QtGui.QAbstractItemView.SelectedClicked
            | QtGui.QAbstractItemView.DoubleClicked
        )
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.timeRangeDelegate = CTimeRangeItemDelegate(self)
        self.setItemDelegateForColumn(0, self.timeRangeDelegate)

    def setSelectionModel(self, selectionModel):
        currSelectionModel = self.selectionModel()
        if currSelectionModel:
            self.disconnect(
                currSelectionModel, QtCore.SIGNAL('currentChanged(QModelIndex,QModelIndex))'), self.currentChanged
            )
        QtGui.QTableView.setSelectionModel(self, selectionModel)
        if selectionModel:
            self.connect(selectionModel, QtCore.SIGNAL('currentChanged(QModelIndex,QModelIndex))'), self.currentChanged)


def getTimePlan(timeRange, plan, orgStructureId, allowGaps=True):
    result = []
    if timeRange and plan > 0:
        fullWorkList = invertGapList([])
        result = calcTimePlanEx(timeRange, plan, fullWorkList, result)
        if allowGaps:
            result = recreateTimeByGaps(getGapList(orgStructureId), timeRange, result)
    return result


def getGapList(orgStructureId):
    def addGap(gapList, record):
        bTime = forceTime(record.value('begTime'))
        eTime = forceTime(record.value('endTime'))
        if bTime < eTime:
            gapList.append((bTime, eTime))
        elif bTime > eTime:
            gapList.append((bTime, QtCore.QTime(23, 59, 59, 999)))
            gapList.append((QtCore.QTime(0, 0), eTime))

    db = QtGui.qApp.db
    orgStructureBaseId = orgStructureId
    result = []
    orgStructureId = orgStructureBaseId
    while orgStructureId:
        recordsOrgStructureGap = db.getRecordList(
            'OrgStructure_Gap',
            'begTime, endTime',
            'master_id=%d' % (orgStructureId),
            'begTime, endTime'
        )
        for record in recordsOrgStructureGap:
            addGap(result, record)
        recordInheritGaps = db.getRecordEx('OrgStructure', 'inheritGaps', 'id=%d' % (orgStructureId))

        # inheritGaps = forceBool(recordInheritGaps.value(0)) if recordInheritGaps else (
        #     False if recordsOrgStructureGap else True
        # )

        if recordInheritGaps:
            inheritGaps = forceBool(recordInheritGaps.value(0))
        elif recordsOrgStructureGap:
            inheritGaps = False
        else:
            inheritGaps = True

        if not inheritGaps:
            break

        orgStructureId = forceRef(db.translate('OrgStructure', 'id', orgStructureId, 'parent_id'))
    result.sort()
    return result
