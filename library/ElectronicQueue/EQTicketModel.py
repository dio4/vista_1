# -*- coding: utf-8 -*-
# ############################################################################
##
## Copyright (C) 2014 Vista Software. All rights reserved.
##
#############################################################################
from library.Utils import forceInt

__author__ = 'atronah'

'''
    author: atronah
    date:   16.10.2014
'''

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import QtSql
from library.database import CDatabase

from library.SqlTableModel import CSqlTableModel


class EQTicketStatus:
    #atronah: при изменении порядка или вставке новых элементов не забудьте:
    #           * Поправить комментарий в базе для поля EQueueTicket.status
    #           * Проверить работоспособность SQL-функции updateEQueueTicket(), которая работает со статусам Reserved, Issued и Ready
    Unknown     = None
    Reserved    = 0 # Номерок доступен для выдачи пациенты
    Issued      = 1 # Выдан пациенту
    Ready       = 2 # Готов к вызову и может быть вызван
    Emergency   = 3 # Экстренно (вызывается первее, нежели Ready)
    InProgress  = 4 # Обрабатывается (находится на приеме)
    Complete    = 5 # Успешно завершено
    Canceled    = 6 # Отменено




class CEQTicketModel(CSqlTableModel):
    def __init__(self, ticketTableName, queueTypeId, db = QtSql.QSqlDatabase(), parent = None):
        super(CEQTicketModel, self).__init__(parent, db)
        self._queueTypeId = queueTypeId

        self._currentDate = None # для смены фильтра запросов к базе при смене дня (если класс живет на протяж неск. дней)


        self._queueId = None
        self._queueName = u''
        self._queueOffice = u''
        self._ticketPrefix = u''
        self._baseOrgStructureId = None

        self.setTable(ticketTableName)
        self.setSort([(u'status', QtCore.Qt.DescendingOrder),
                      (u'summonDatetime', QtCore.Qt.AscendingOrder),
                      (u'idx', QtCore.Qt.AscendingOrder)])
        self.setEditStrategy(self.OnManualSubmit)

        self._statusColumn = self.fieldIndex(u'status')
        self._summonColumn = self.fieldIndex(u'summonDatetime')
        self._orgStructureColumn = self.fieldIndex(u'orgStructure_id')

        self.updateForCurrentDate()


    @staticmethod
    def getEQueueRecord(db, eQueueTypeId, queueDate):
        if not eQueueTypeId:
            return None


        queueStmt = """SELECT `id`, `eQueueType_id`, `date`
                        FROM `EQueue`
                        WHERE
                            `eQueueType_id` = %s
                            AND `date` = '%s';
                    """ % (eQueueTypeId, queueDate.toString(QtCore.Qt.ISODate))

        query = QtSql.QSqlQuery(db)
        query.exec_(queueStmt)
        if query.first():
           record = query.record()
        else:
            record = db.record('EQueue')
            record.setValue('eQueueType_id', QtCore.QVariant(eQueueTypeId))
            record.setValue('date', QtCore.QVariant(queueDate))

        return record
        #
        # db = QtGui.qApp.db
        # tableEQueue = db.table('EQueue')
        # record = db.getRecordEx(tableEQueue,
        #                         '*',
        #                         where = [tableEQueue['eQueueType_id'].eq(eQueueTypeId),
        #                                  tableEQueue['date'].eq(queueDate)])
        # if record is None:
        #     record = tableEQueue.newRecord()
        #     record.setValue('eQueueType_id', QtCore.QVariant(eQueueTypeId))
        #     record.setValue('date', QtCore.QVariant(queueDate))
        # return record


    @staticmethod
    def getEQueueTicketRecord(db, queueId, idx = None):
        ticketRecord = None
        if queueId:
            query = QtSql.QSqlQuery(db)
            if idx is None:
                query.exec_("""SELECT max(`idx`)
                                FROM `EQueueTicket`
                                WHERE `queue_id` = %s
                            """ % queueId)
                if query.first():
                    record = query.record()
                    maxIdx, isOk  = record.value(0).toInt()
                    if isOk:
                        idx = maxIdx + 1
                else:
                    idx = 0

            else:
                query.exec_("""SELECT *
                                    FROM `EQueueTicket`
                                    WHERE `queue_id` = %s
                                            AND `idx` = %s
                             """ % (queueId, idx))
                if query.first():
                    ticketRecord = query.record()

            if not ticketRecord or ticketRecord.isEmpty():
                # attention: db is QSqlDatabase instead CDatabase
                ticketRecord = db.record('EQueueTicket')
                ticketRecord.setValue('queue_id', QtCore.QVariant(queueId))
                ticketRecord.setValue('status', QtCore.QVariant(EQTicketStatus.Reserved))
                ticketRecord.setValue('idx', QtCore.QVariant(idx))
                ticketRecord.setValue('value', QtCore.QVariant(idx + 1))

            # db = QtGui.qApp.db
            # tableEQueueTicket = db.table('EQueueTicket')
            #
            # record = db.getRecordEx(tableEQueueTicket,
            #                         '*',
            #                         where = [tableEQueueTicket['queue_id'].eq(queueId),
            #                                  tableEQueueTicket['idx'].eq(idx)])
            # if record is None:
            #     record = tableEQueueTicket.newRecord()
            #     record.setValue('queue_id', QtCore.QVariant(queueId))
            #     record.setValue('idx', QtCore.QVariant(idx))
            #
            # record.setValue('status', QtCore.QVariant(EQTicketStatus.Reserved))
            # record.setValue('value', QtCore.QVariant(idx + 1))
            # record.setValue('orgStructure_id', QtCore.QVariant())
            # ticketId = db.insertOrUpdate(tableEQueueTicket, record)

        return ticketRecord



    # --- re-impliment --
    def select(self):
        if self._currentDate != QtCore.QDate.currentDate():
            self.updateForCurrentDate()
        return super(CEQTicketModel, self).select()
    
    
    def flags(self, index):
        flags = super(CEQTicketModel, self).flags(index)
        return flags & ~QtCore.Qt.ItemIsEditable


    #--- interface ---
    def queueTypeId(self):
        return self._queueTypeId


    def setQueueTypeId(self, newId):
        self._queueTypeId = newId
        self.updateForCurrentDate()
        self.clear()




    def baseOrgStructureId(self):
        return self._baseOrgStructureId



    def queueName(self):
        return self._queueName


    def queueOffice(self):
        return self._queueOffice


    def queueId(self):
        return self._queueId


    def status(self, ticketId):
        row = self.rowById(ticketId)
        status = self.record(row).value('status')
        return status if status.isValid() else EQTicketStatus.Unknown


    def _rowByField(self, fieldName, value):
        for row in xrange(self.rowCount()):
            if self.record(row).value(fieldName) == value:
                return row
        return -1


    def rowByValue(self, value):
        return self._rowByField('value', self._ticketPrefix + value)


    def rowById(self, ticketId):
        return self._rowByField('id', ticketId)


    def ticketId(self, index):
        if index.isValid():
            row = index.row()
            ticketId = self.record(row).value('id').toInt()[0]
            if ticketId:
                return ticketId

        return None


    def baseFilter(self):
        return u'queue_id = %s' % (self._queueId or 'NULL')


    # def orderByClause(self):
    #     baseClause = super(CEQTicketModel, self).orderByClause()
    #     statement = u'ORDER BY'
    #     statementIdx = baseClause.indexOf(statement, 0, QtCore.Qt.CaseInsensitive)
    #
    #     baseClause = unicode(baseClause[statementIdx + len(statement) + 1:]) if statementIdx >= 0 else u''
    #     result = u'%s.`status` DESC, summonDatetime' % self.tableName()
    #     if baseClause.strip():
    #         result += u', %s' % baseClause
    #     return QtCore.QString(u'%s %s' % (statement, result))


    #--- logic ---
    def updateForCurrentDate(self):
        self._currentDate = QtCore.QDate.currentDate()
        query = QtSql.QSqlQuery(u'''SELECT
                                        EQueue.id AS queueId,
                                        rbEQueueType.name AS queueName,
                                        OrgStructure.name AS queueOffice,
                                        OrgStructure.id AS baseOrgStructureId,
                                        rbEQueueType.ticketPrefix AS ticketPrefix
                                    FROM rbEQueueType
                                        INNER JOIN OrgStructure ON OrgStructure.id = rbEQueueType.orgStructure_id
                                        LEFT JOIN EQueue ON EQueue.eQueueType_id = rbEQueueType.id
                                    WHERE rbEQueueType.id = %s
                                            AND EQueue.`date` = CURRENT_DATE''' % self._queueTypeId,
                                self.database())
        if query.first():
            record = query.record()
            queueId, isOk = record.value('queueId').toInt()
            if isOk:
                self._queueId = queueId
            self._queueName = record.value('queueName').toString()
            self._queueOffice = record.value('queueOffice').toString()
            self._ticketPrefix = record.value('ticketPrefix').toString()
            self._baseOrgStructureId = record.value('baseOrgStructureId').toInt()[0]

        self.setFilter(self.baseFilter())

#==========================================================================


class CEQTicketControlModel(CEQTicketModel):
    prevValueChanged = QtCore.pyqtSignal(int, QtCore.QString) # (queueTypeId, value)
    currentValueChanged = QtCore.pyqtSignal(int, QtCore.QString) # (queueTypeId, value)
    nextValueChanged = QtCore.pyqtSignal(int, QtCore.QString) # (queueTypeId, value)

    ticketStatusChanged = QtCore.pyqtSignal(int) # (ticketId)

    def __init__(self, queueTypeId, db = QtSql.QSqlDatabase(), parent = None):
        super(CEQTicketControlModel, self).__init__(u'EQueueTicket', queueTypeId, db, parent)
        # self.setEditStrategy(self.OnFieldChange)

        self._currentIdList = []
        self._nextId = QtCore.QVariant()
        self._prevIdStack = []

        # self._summonTimerId = None
        # self._summonTimeout = 5.0

        self._ticketIdToValue = {} #FIXME: atronah: возможно, лучше не хранить дубликаты данных и получать их через rowById

        self._noUpdateMutex = QtCore.QMutex()


    # --- re-implement ---
    def select(self):
        if self._noUpdateMutex.tryLock():
            # print time.time(),  'select for ', self.queueTypeId() #debug: atronah:
            if super(CEQTicketModel, self).select():
                self.findNext()
                self._noUpdateMutex.unlock()
                return True
            else:
                self._noUpdateMutex.unlock()
                CDatabase.checkDatabaseError(self.lastError(), self.selectStatement())
        return False


    def resetNext(self):
        self._nextId = QtCore.QVariant()


    def setData(self, index, value, role = QtCore.Qt.EditRole):
        result = super(CEQTicketModel, self).setData(index, value, role)
        CDatabase.checkDatabaseError(self.lastError(), self.selectStatement())
        if result and index.column() == self._statusColumn:
            #TODO: atronah: пока что вызывается 2 раза, на смену прошлого и текущего номерка, надо оптимизировать
            ticketId = self.ticketId(index)
            if ticketId:
                self.ticketStatusChanged.emit(ticketId)
        return result


    # def timerEvent(self, event):
    #     if event.timerId() == self._summonTimerId:
    #         self.clearSummon()


    # --- interface ---
    def prevId(self):
        return self._prevIdStack[-1] if self._prevIdStack else QtCore.QVariant()


    def currentIdList(self):
        return self._currentIdList


    def isFinished(self, ticketId):
        return self.status(ticketId) in [EQTicketStatus.Complete, EQTicketStatus.Canceled]


    def nextId(self):
        return self._nextId


    # def setSummonTimeout(self, seconds = 0):
        # self._summonTimeout = seconds


    # def summonTimeout(self):
    #     return self._summonTimeout

    # --- logic ---
    def findNext(self):
        nextId = None
        nextValue = QtCore.QString()

        for row in xrange(self.rowCount()):
            record = self.record(row)
            ticketId = record.value('id')
            if not record or record.isEmpty():
                continue

            if nextId is None:
                if record.value('status') in [EQTicketStatus.Ready, EQTicketStatus.Emergency]:
                    nextId = ticketId
                    nextValue = record.value('value').toString()


            # Если найден текущий, следующий и все имена для словаря, то выйти из цикла
            # if not (currentId is None or nextId is None or None in ticketIdToValue.values()):
            if nextId is not None:
                break

        # if nextId != self._nextId:
        if nextId != self._nextId:
            # print 'nextValueChanged for ', self.queueTypeId(), ': ', self._nextId.toInt(), '-->', nextId.toInt() #debug: atronah:
            self._nextId = QtCore.QVariant(nextId)
            self.nextValueChanged.emit(self._queueTypeId, nextValue)

    def findInProgress(self):
        ticketId = None
        for row in xrange(self.rowCount()):
            record = self.record(row)
            if not record or record.isEmpty():
                continue
            if record and forceInt(record.value('status')) == 4:
                ticketId = forceInt(record.value('id'))
        return ticketId



    def finishTicket(self, status = EQTicketStatus.Complete, ticketId = None):
        if ticketId and self._noUpdateMutex.tryLock():
            if not isinstance(ticketId, QtCore.QVariant):
                ticketId = QtCore.QVariant(ticketId)
            query = QtSql.QSqlQuery(self.database())
            if not query.exec_(u'SELECT finishTicket(%s, %s);' % (ticketId.toInt()[0],
                                                                  1 if status == EQTicketStatus.Complete else 0)):
                self._noUpdateMutex.unlock()
                CDatabase.checkDatabaseError(query.lastError(), query.lastQuery()) #TODO: atronah: возможно, стоит делать тихий краш
                return QtCore.QVariant()
            if ticketId in self._currentIdList:
                self._currentIdList.remove(ticketId)
            self.select()
            self._noUpdateMutex.unlock()


    def finishAllTickets(self, status = EQTicketStatus.Complete):
        for ticketId in self._currentIdList:
            self.finishTicket(status, ticketId)



    def changeTicketStatus(self, ticketId, status):
        if ticketId and self._noUpdateMutex.tryLock():
            row = self.rowById(ticketId)
            if row == -1:
                self._noUpdateMutex.unlock()
                self.select()
                row = self.rowById(ticketId) if self._noUpdateMutex.tryLock() else -1

            if row in xrange(self.rowCount()):
                self.setData(self.index(row, self._statusColumn),
                     status)
                if status != [EQTicketStatus.InProgress, EQTicketStatus.Complete, EQTicketStatus.Canceled]:
                    self.setData(self.index(row, self._summonColumn),
                                 QtCore.QVariant())
                    self.setData(self.index(row, self._orgStructureColumn),
                                 QtCore.QVariant())
                self.submitAll()

            self._noUpdateMutex.unlock()



    def markAsEmergency(self, ticketId):
        self.changeTicketStatus(ticketId, EQTicketStatus.Emergency)


    def markAsReady(self, ticketId):
        self.changeTicketStatus(ticketId, EQTicketStatus.Ready)


    def markAsIssued(self, ticketId):
        self.changeTicketStatus(ticketId, EQTicketStatus.Issued)



    def summon(self, ticketId, orgStructureId, pushCurrentToPrev = True):
        if not isinstance(ticketId, QtCore.QVariant):
            ticketId = QtCore.QVariant(ticketId)

        if self._noUpdateMutex.tryLock():
            row = self.rowById(ticketId)
            if row == -1:
                self._noUpdateMutex.unlock()
                return QtCore.QVariant()

            currentValue = self.record(row).value('value').toString()
            if ticketId not in self._currentIdList:
                if pushCurrentToPrev:
                    self._prevIdStack.append(ticketId)
                self._ticketIdToValue[ticketId] = currentValue
                prevId = self._prevIdStack[-1] if self._prevIdStack else QtCore.QVariant()
                prevValue = self._ticketIdToValue.get(prevId, QtCore.QString())
                self.prevValueChanged.emit(self._queueTypeId, prevValue)

                self.currentValueChanged.emit(self._queueTypeId, currentValue)
                self._currentIdList.append(ticketId)

            self.setData(self.index(row, self._statusColumn),
                         EQTicketStatus.InProgress)

            if orgStructureId is None:
                orgStructureId = self._baseOrgStructureId
            self.setData(self.index(row, self._orgStructureColumn),
                         QtCore.QVariant(orgStructureId))
            query = QtSql.QSqlQuery(self.database())
            if not query.exec_(u'SELECT summonTicket(%s);' % ticketId.toInt()[0]):
                self._noUpdateMutex.unlock()
                CDatabase.checkDatabaseError(query.lastError(), query.lastQuery()) #TODO: atronah: возможно, стоит делать тихий краш
                return QtCore.QVariant()
            # self._summonTimerId = self.startTimer(int(self._summonTimeout * 1000))
            self.submitAll()
            self._noUpdateMutex.unlock()
        return ticketId


    # def clearSummon(self):
    #     if self._currentId:
    #         summonRow = self.rowById(self._currentId)
    #         self.setData(self.index(summonRow, self._statusColumn),
    #                      EQTicketStatus.InProgress)
    #         self.killTimer(self._summonTimerId)
    #         self._summonTimerId = None


    def moveToNext(self, currentStatus = EQTicketStatus.Complete, orgStructurId = None, currentTicketId = None, value = QtCore.QString()):
        self.select()
        nextId = self._nextId
        if not value.isEmpty():
            row = self.rowByValue(value)
            if row in xrange(self.rowCount()):
                nextId = self.record(row).value('id')
        self.finishTicket(currentStatus, currentTicketId)
        if nextId.isValid():
            self.summon(nextId, orgStructureId= orgStructurId)
            self.findNext()
            return nextId
        return None


    def moveToPrev(self, currentStatus = EQTicketStatus.Complete, currentTicketId = None):
        self.select()
        prevId = self._prevIdStack.pop()
        self.finishTicket(currentStatus, currentTicketId)
        if prevId.isValid():
            self.summon(prevId, pushCurrentToPrev=False)
            self.findNext()
            return prevId
        return None


    def reCall(self, ticketId = None):
        if ticketId is None:
            ticketId = self._currentId
        self.summon(ticketId, self._baseOrgStructureId)
#==========================================================================


class CEQTicketViewModel(CEQTicketModel):

    summon = QtCore.pyqtSignal(QtCore.QString, QtCore.QString) # (номерок, кабинет)

    def __init__(self, queueTypeId, orgStructureId = None, db = QtSql.QSqlDatabase(), parent = None):
        self._orgStructureId = orgStructureId
        self._isInProgressDisplay = True
        self._isWaitersDisplay = True

        super(CEQTicketViewModel, self).__init__(u'vEQueueTicket', queueTypeId, db, parent)
        self._valueColumn = self.fieldIndex('value')

        self._rowLimit = 0

        self._baseFont = QtGui.QFont()
        self._baseFont.setPointSize(64)

        self._inProgressBrush = QtGui.QBrush(QtGui.QColor(QtCore.Qt.green).lighter())#, QtCore.Qt.Dense5Pattern)

        self._summonRowList = []
        self._lastInProgressRow = -1

        self._isBlink = False
        self._blinkTimerId = None
        self._blinkTimeout = 0.5 # seconds

        self._maxElapsedSummon = QtCore.QTime(0,  # hours
                                              0,  # minutes
                                              5,  # seconds
                                              0)  # mseconds

        self._alreadySommoningList = []




    def setWaitersDisplayEnabled(self, enabled):
        self._isWaitersDisplay = enabled
        self.updateForCurrentDate()



    def setInProgressDisplayEnabled(self, enabled):
        self._isInProgressDisplay = enabled
        self.updateForCurrentDate()

    
    
    def updateForCurrentDate(self):
        super(CEQTicketViewModel, self).updateForCurrentDate()
        if self._orgStructureId:
            query = QtSql.QSqlQuery(u'''SELECT
                                            OrgStructure.name
                                        FROM OrgStructure
                                        WHERE OrgStructure.id = %s ''' % self._orgStructureId,
                                    self.database())
            if query.first():
                self._queueOffice = query.record().value(0).toString()


    def stopTimer(self):
        if self._blinkTimerId:
            self.killTimer(self._blinkTimerId)
            self._blinkTimerId = None


    @QtCore.pyqtSlot(int)
    def setRowLimit(self, maxRowCount):
        self._rowLimit = maxRowCount


    def rowLimit(self):
        return self._rowLimit



    # --- re-implement ---
    def timerEvent(self, event):
        if event.timerId() == self._blinkTimerId:
            self._isBlink = not self._isBlink
            # print self._isBlink #debug: atronah:
            for row in self._summonRowList:
                index = self.index(row, 0)
                self.dataChanged.emit(index, index)


    def columnCount(self, parentIndex = QtCore.QModelIndex()):
        return 1


    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if section == 0:
                if role == QtCore.Qt.DisplayRole:
                    return self._queueOffice
                elif role == QtCore.Qt.FontRole:
                    font = QtGui.QFont(self._baseFont)
                    font.setBold(True)
                    return QtCore.QVariant(font)
        return super(CEQTicketViewModel, self).headerData(section, orientation, role)


    def data(self, index, role = QtCore.Qt.DisplayRole):
        if index.isValid():
            row = index.row()
            if role == QtCore.Qt.DisplayRole:
                return self.record(row).value('value')
            elif role == QtCore.Qt.FontRole:
                font = QtGui.QFont(self._baseFont)
                fontScale = 0.9 - 0.08 * max(0, row - self._lastInProgressRow)
                font.setPointSizeF(max(10, font.pointSizeF() * fontScale))
                return QtCore.QVariant(font)
            elif role == QtCore.Qt.ForegroundRole:
                if row > self._lastInProgressRow:
                    return QtCore.QVariant(QtGui.QBrush(QtGui.QColor(QtCore.Qt.gray)))
            elif role == QtCore.Qt.BackgroundRole:
                status = self.record(row).value('status')
                isSummon = row in self._summonRowList
                if status == EQTicketStatus.InProgress and (not isSummon or self._isBlink):
                    return QtCore.QVariant(self._inProgressBrush)
            elif role == QtCore.Qt.TextAlignmentRole:
                return QtCore.QVariant(QtCore.Qt.AlignCenter)
        return super(CEQTicketViewModel, self).data(index, role)


    def setData(self, index, value, role = QtCore.Qt.EditRole):
        return False


    def select(self):
        result = super(CEQTicketViewModel, self).select()

        if not self._isInProgressDisplay:
            return result


        # Фиксирование номеров строк, в которых находятся пациенты с вызовом.
        self._summonRowList = []
        self._lastInProgressRow = -1
        for row in xrange(self.rowCount()):
            status = self.record(row).value('status')
            ticketId = self.record(row).value('id')
            if status == EQTicketStatus.InProgress:
                self._lastInProgressRow = row
                elapsedSinceSummon = self.record(row).value('elapsedSinceSummon').toTime()
                # print row, elapsedSinceSummon #debug: atronah:
                if elapsedSinceSummon.isValid() and elapsedSinceSummon <= self._maxElapsedSummon:
                    self._summonRowList.append(row)
                    if ticketId not in self._alreadySommoningList:
                        self._alreadySommoningList.append(ticketId)
                        ticketValue = self.record(row).value('value').toString()
                        ticketOffice = self.record(row).value('office')
                        self.summon.emit(ticketValue, ticketOffice)
                else:
                    continue
            else:
                if ticketId in self._alreadySommoningList:
                    self._alreadySommoningList.remove(ticketId)

        # Запуск таймера мигания, если есть вызыванные, иначе отключить таймер
        if self._summonRowList:
            if not self._blinkTimerId:
                self._blinkTimerId = self.startTimer(self._blinkTimeout * 1000)
        else:
            self.stopTimer()

        return result


    def selectStatement(self):
        stmt = super(CEQTicketViewModel, self).selectStatement()
        if self.rowLimit() and not stmt.isEmpty():
            stmt += u' LIMIT %s' % self.rowLimit()
        return stmt


    def baseFilter(self):
        baseFilter = super(CEQTicketViewModel, self).baseFilter()
        orgStructureFilter = u'orgStructure_id = %s' % self._orgStructureId if self._orgStructureId else u'1'
        statusFilterList = []
        if self._isInProgressDisplay:
            statusFilterList.append(u'(status = %s AND %s)' % (EQTicketStatus.InProgress, orgStructureFilter))
        if self._isWaitersDisplay:
            statusFilterList.append(u'status = %s' % EQTicketStatus.Ready)
            statusFilterList.append(u'status = %s' % EQTicketStatus.Emergency)
        statusFilter = u' OR '.join(statusFilterList) if statusFilterList else u'1'
        return u'(%s) AND (%s)' % (baseFilter, statusFilter)

    # --- logic ---




def main():
    import sys
    from PyQt4 import QtGui
    from library.ElectronicQueue.test_EQTicketModel import initTestDatabase

    app = QtGui.QApplication(sys.argv)

    tv = QtGui.QTableView()
    tv.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
    tv.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
    tv.verticalHeader().hide()

    db = initTestDatabase()
    m = CEQTicketViewModel(1, db)
    m.select()

    tv.setModel(m)
    tv.show()

    s = QtCore.QSize(tv.verticalHeader().width() + (m.columnCount() + 1) * tv.frameWidth() + sum([tv.horizontalHeader().sectionSize(i) for i in xrange(m.columnCount())]),
                     tv.horizontalHeader().height() + (m.rowCount() + 1) * tv.frameWidth() + sum([tv.verticalHeader().sectionSize(i) for i in xrange(m.rowCount())]))
    tv.setMinimumSize(s)


    # tv.showMaximized()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()