# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Events.Action import ActionStatus, CAction, CActionType, CActionTypeCache, CJobTicketActionPropertyValueType
from Events.Utils import checkSpeciality, getActionTypeMesIdList, getEventActionContract, getEventLengthDays, \
    getEventTypeForm
from Orgs.OrgComboBox import CContractDbModel
from Users.Rights import urIgnoreRestrictActionByFrequency, urDeleteActionWithTissue
from library.InDocTable import CRBInDocTableCol
from library.Utils import addPeriod, firstHalfYearDay, firstMonthDay, firstQuarterDay, firstWeekDay, firstYearDay, \
    forceDate, forceDateTime, forceDouble, forceInt, forceRef, forceString, formatNum1, getActionTypeIdListByFlatCode, \
    lastHalfYearDay, lastMonthDay, lastQuarterDay, lastWeekDay, lastYearDay, toVariant


class CActionsModel(QtCore.QAbstractTableModel):
    __pyqtSignals__ = ('amountChanged(int)',
                      )

    def __init__(self, parent, actionTypeClass=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._actionsPage = parent  # type: Events.ActionsPage.CActionsPage
        self.actionTypeClass = None
        self.actionTypeIdList = []
        self.disabledActionTypeIdList = []
        self.enabledActionTypeIdList = None
        self.ignoredActionTypesIdList = []
        self.notDeletedActionTypes = {}
        if not QtGui.qApp.region() == '23':
            self.setIgnoredActionTypeByFlatCode(u'temperatureSheet%')
        self.setIgnoredActionTypeByFlatCode(u'permanentTeeth')
        self.setIgnoredActionTypeByFlatCode(u'calfTeeth')
        self.col = CRBInDocTableCol(u'',  'actionType_id', 10, 'ActionType', addNone=True)
        self._items = [] # each item is pair (record, action)
        self.eventEditor = None
        if actionTypeClass is not None:
            self.setActionTypeClass(actionTypeClass)
        self.idxFieldName = 'idx'  # :( для обеспечения возможности перемещения строк.
        self._isEditable = True
        self._actionTypeBaseFilter = ''
        self._actionTypeCompatibilitiesCache = {}
        self.__openDatetime = QtCore.QDateTime.currentDateTime()  # Храним время открытия для проверки на обновление.
        # # необходимо для грамотного подсчета квот на работы в isExistQuotaForPerson(), JobTicketChooser.py
        self.jobTicketsFromRemovedAction = []

    def setBaseActionTypeFilter(self, filter):
        self._actionTypeBaseFilter = filter
        self._updateActionTypeFilter()

    def _updateActionTypeFilter(self):
        filter = '1'
        if self.actionTypeClass is not None:
            if isinstance(self.actionTypeClass, list):
                filter += ' AND class IN (%s)' % ', '.join(map(str, self.actionTypeClass))
            else:
                filter += ' AND class = %d' % self.actionTypeClass
        if self._actionTypeBaseFilter:
            filter += ' AND %s' % self._actionTypeBaseFilter
        self.col.filter = filter

    def setEditable(self, editable):
        self._isEditable = editable

    def isEditable(self):
        return self._isEditable

    def setActionTypeClass(self, actionTypeClass):
        self.actionTypeClass = actionTypeClass
        self.actionTypeIdList = self.getActionTypeIdList(actionTypeClass)
        self._updateActionTypeFilter()

    def items(self):
        return self._items

    def addItem(self, item):
        self._items.append(item)
        return len(self._items) - 1

    def insertItem(self, item):
        self._items.append(item)
        index = QtCore.QModelIndex()
        cnt = len(self._items)
        self.beginInsertRows(index, cnt, cnt)
        self.insertRows(cnt, 1, index)
        self.endInsertRows()
        return cnt - 1

    def getItemByRow(self, row):
        return self._items[row] if 0 <= row < len(self._items) else (None, None)

    def getRecordByRow(self, row):
        return self._items[row][0] if 0 <= row < len(self._items) else None

    def getActionByRow(self, row):
        return self._items[row][1] if 0 <= row < len(self._items) else None

    def updatePersonId(self, oldPersonId, newPersonId):
        pass

    def emitAmountChanged(self, row):
        self.emit(QtCore.SIGNAL('amountChanged(int)'), row)

    def updateActionsAmount(self):
        for row, (record, action) in enumerate(self._items):
            actionTypeId = forceRef(record.value('actionType_id'))
            if actionTypeId:
                actionType = CActionTypeCache.getById(actionTypeId)
                if actionType.amountEvaluation in [CActionType.eventVisitCount,
                                                   CActionType.eventLength,
                                                   CActionType.eventLengthWithoutRedDays]:
                    prevValue = forceDouble(record.value('amount'))
                    value = float(self.getDefaultAmountEx(actionType, record, action))
                    if prevValue != value:
                        record.setValue('amount', toVariant(value))
                        self.emitRowsChanged(row, row)
                        self.emitAmountChanged(row)

    def updateActionAmount(self, row):
        if not (0 <= row < len(self._items)):
            return

        record, action = self._items[row]
        actionTypeId = forceRef(record.value('actionType_id'))
        if actionTypeId:
            actionType = CActionTypeCache.getById(actionTypeId)
            if actionType.amountEvaluation in [CActionType.eventVisitCount,
                                               CActionType.eventLength,
                                               CActionType.eventLengthWithoutRedDays,
                                               CActionType.actionLength,
                                               CActionType.actionLengthWithoutRedDays,
                                               CActionType.actionFilledProps]:
                prevValue = forceDouble(record.value('amount'))
                value = float(self.getDefaultAmountEx(actionType, record, action))
                if prevValue != value:
                    record.setValue('amount', toVariant(value))
                    self.emitRowsChanged(row, row)
                    self.emitAmountChanged(row)

    def getActionTypeIdList(self, actionTypeClass=None):
        db = QtGui.qApp.db
        tableActionType = db.table('ActionType')
        cond = [tableActionType['deleted'].eq(0)]
        if actionTypeClass is not None:
            if type(actionTypeClass) == list:
                cond.append(tableActionType['class'].inlist(actionTypeClass))
            else:
                cond.append(tableActionType['class'].eq(actionTypeClass))
        if self._actionTypeBaseFilter:
            cond.append(self._actionTypeBaseFilter)
        return db.getIdList('ActionType', 'id', cond)

    def disableActionType(self, actionTypeId):
        self.disabledActionTypeIdList.append(actionTypeId)

    def disableActionTypeList(self, actionTypeIdList):
        self.disabledActionTypeIdList.extend(actionTypeIdList)

    def enableActionType(self, actionTypeId):
        self.enabledActionTypeIdList.append(actionTypeId)

    def enableActionTypeList(self, actionTypeIdList):
        if self.enabledActionTypeIdList is None and actionTypeIdList is not None:
            self.enabledActionTypeIdList = []
        self.enabledActionTypeIdList.extend(actionTypeIdList)

    def enableAllActionTypeList(self):
        self.enabledActionTypeIdList = None

    def setIgnoredActionTypeId(self, actionTypeId):
        self.ignoredActionTypesIdList.append(actionTypeId)

    def clearIgnoredActionTypeId(self, actionTypeId):
        self.ignoredActionTypesIdList = []

    def setIgnoredActionTypeByFlatCode(self, flatCode):
        self.ignoredActionTypesIdList.extend(getActionTypeIdListByFlatCode(flatCode))

    def setIgnoredActionTypeByClass(self, class_):
        db = QtGui.qApp.db
        tableActionType = db.table('ActionType')
        cond = [tableActionType['class'].inlist(class_)]
        idList = db.getIdList(tableActionType, 'id', cond)
        if idList:
            self.ignoredActionTypesIdList.extend(idList)

    def setNotDeletedActionTypes(self, actionTypes):
        self.notDeletedActionTypes = actionTypes

    def getActionLength(self, record, countRedDays):
        if record:
            startDate = forceDate(record.value('begDate'))
            stopDate = forceDate(record.value('endDate'))
            if startDate and stopDate:
                return getEventLengthDays(startDate, stopDate, countRedDays, self.eventEditor.eventTypeId)
        return 0

    def getDefaultAmountEx(self, actionType, record, action):
        return getActionDefaultAmountEx(self, actionType, record, action)

    def getDefaultAmount(self, actionTypeId, record, action):
        if actionTypeId:
            actionType = CActionTypeCache.getById(actionTypeId)
            result = self.getDefaultAmountEx(actionType, record, action)
        else:
            result = 0
        return result

    def columnCount(self, index=QtCore.QModelIndex()):
        return 2

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self._items) + 1

    def inRange(self, row):
        return 0 <= row < self.rowCount() - 1

    def lastIndex(self):
        return self.index(self.rowCount() - 1, 0)

    def lastItemIndex(self):
        rowCount = self.rowCount()
        if rowCount < 2: return QtCore.QModelIndex()
        return self.index(rowCount - 2, 0)

    def flags(self, index):
        row = index.row()
        if row < len(self._items) or not self.isEditable():
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(u'Наименование') if section == 0 else QtCore.QVariant(u'Дата назначения')
        return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        row = index.row()
        column = index.column()

        if row < len(self._items):
            if role == QtCore.Qt.EditRole:
                record = self.getRecordByRow(row)
                return record.value('actionType_id')

            elif role == QtCore.Qt.DisplayRole:
                record = self.getRecordByRow(row)
                if column == 0:
                    outName = forceString(record.value('specifiedName'))
                    actionTypeId = forceRef(record.value('actionType_id'))
                    if actionTypeId:
                        actionType = CActionTypeCache.getById(actionTypeId)
                        if actionType:
                            outName = actionType.name + ' '+outName if outName else actionType.name
                    return QtCore.QVariant(outName)
                if column == 1:
                    return QtCore.QVariant(forceDate(record.value('directionDate')))

            elif role in (QtCore.Qt.StatusTipRole, QtCore.Qt.ToolTipRole):
                record = self.getRecordByRow(row)
                actionTypeId = forceRef(record.value('actionType_id'))
                actionType = CActionTypeCache.getById(actionTypeId) if actionTypeId else None
                return QtCore.QVariant(actionType.code + ': ' + actionType.name if actionType else '')

            elif role == QtCore.Qt.ForegroundRole:
                record, action = self.getItemByRow(row)
                if action and action.getType().isRequiredCoordination and record.isNull('coordDate'):
                    return QtCore.QVariant(QtGui.QColor(255, 0, 0))

            elif role == QtCore.Qt.TextAlignmentRole and column == 1:  # center date
                return QtCore.Qt.AlignCenter

        return QtCore.QVariant()

    def setData(self, index, value, role=QtCore.Qt.EditRole, presetAction=None):
        if role == QtCore.Qt.EditRole:
            row = index.row()
            actionTypeId = forceRef(value)
            if actionTypeId and not (self.checkMaxOccursLimit(actionTypeId) and
                                     self.checkMovingNoLeaved(actionTypeId) and
                                     self.checkMovingAfterReceived(actionTypeId) and
                                     self.checkLeavedAfterMoving(actionTypeId) and
                                     self.checkLeavedAfterMovingDate(actionTypeId) and
                                     self.checkCompatibility(actionTypeId) and
                                     self.checkPeriodicActionPosibility(actionTypeId)):
                return False
            if row == len(self._items):
                if actionTypeId is None:
                    return False
                self.addRow(presetAction=presetAction)
            if not presetAction:
                record = self._items[row][0]
                self.fillRecord(record, actionTypeId)
                action = None if actionTypeId is None else CAction(record=record)
            else:
                record = presetAction.getRecord()
                action = presetAction
            setPerson = forceRef(record.value('setPerson_id'))
            execPerson = forceRef(record.value('person_id'))
            if not QtGui.qApp.userSpecialityId:
                if setPerson == QtGui.qApp.userId:
                    record.setValue('setPerson_id', toVariant(None))
                if execPerson == QtGui.qApp.userId:
                    record.setValue('person_id', toVariant(None))

            self._items[row] = (record, action)
            self.emitDataChanged(index)
            self.emitItemsCountChanged()
            return True

    def emitItemsCountChanged(self):
        self.emit(QtCore.SIGNAL('itemsCountChanged()'))

    def emitDataChanged(self, topLeft, bottomRight=None):
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), topLeft, bottomRight if bottomRight is not None else topLeft)

    def addRow(self, actionTypeId=None, amount=None, financeId=None, contractId=None, presetAction=None):
        if not presetAction:
            record = self.fillNewRecord(actionTypeId, amount, financeId, contractId)
            item = (record, CAction(record=record) if actionTypeId else None)
        else:
            record = presetAction.getRecord()
            item = (record, presetAction)
        if item[1]:
            item[1].initPropertyPresetValues()
        return self.insertItem(item)

    def checkCompatibility(self, actionTypeId):
        incompatibilities = self.getIncompatibilities(actionTypeId)
        actionTypeName = CActionTypeCache.getById(actionTypeId).name
        for item in self._items:
            action = item[1]
            if not action:
                continue
            typeId = action.getType().id
            if typeId in incompatibilities:
                result = QtGui.QMessageBox.critical(self.eventEditor,
                                                    u'Внимание!', u'Выбранные мероприятия не совместимы.\n%s и %s могут иметь следующие последствия: %s' % (
                                                    action.getType().name, actionTypeName, incompatibilities[typeId]),
                                                    QtGui.QMessageBox.Ok | QtGui.QMessageBox.Ignore)
                if result == QtGui.QMessageBox.Ignore:
                    continue
                return False
        return True

    def getIncompatibilities(self, actionTypeId):
        result = self._actionTypeCompatibilitiesCache.get(actionTypeId, None)
        if result is None:
            db = QtGui.qApp.db
            tableATI = db.table('rbActionTypeIncompatibility')
            firstSecond = ('firstActionType_id', 'secondActionType_id')
            result = {}
            for idField, otherIdField in (firstSecond, reversed(firstSecond)):
                for record in db.iterRecordList(tableATI, [tableATI[idField], tableATI['reason']], tableATI[otherIdField].eq(actionTypeId)):
                    result[forceRef(record.value(idField))] = forceString(record.value('reason'))
            self._actionTypeCompatibilitiesCache[actionTypeId] = result
        return result

    def fillRecord(self, record, actionTypeId, amount=None, financeId=None, contractId=None):
        fillActionRecord(self, record, actionTypeId, amount, financeId, contractId)

    def fillNewRecord(self, actionTypeId, amount=None, financeId=None, contractId=None):
        record = QtGui.qApp.db.table('Action').newRecord()
        self.fillRecord(record, actionTypeId, amount, financeId, contractId)
        return record

    def getDefaultContractId(self, actionTypeId, financeId, begDate, endDate, contractId):
        return getActionDefaultContractId(self, actionTypeId, financeId, begDate, endDate, contractId)

    def removeRows(self, row, count, parentIndex=QtCore.QModelIndex()):
        def getJobTicketsFromAction(act):
            props = act.getProperties()
            for x in props:
                if x.type().tableName == u'ActionProperty_Job_Ticket' and x.getValue():
                    self.jobTicketsFromRemovedAction.append(forceString(x.getValue()))

        if 0 <= row <= len(self._items) - count:
            record = self.getRecordByRow(row)
            actionTypeId = forceRef(record.value('actionType_id'))

            if actionTypeId in self.notDeletedActionTypes:
                QtGui.QMessageBox.critical(None, u'Ошибка', u'Невозможно удалить обязательные услуги: \'%s\'.' % ', '.join(self.notDeletedActionTypes.values()),
                                           QtGui.QMessageBox.Ok)
                return False

            if any(self.isLocked(row + i) for i in xrange(count)):
                return False

            if actionTypeId and not (self.checkReceivedDeleted(actionTypeId) and
                                     self.checkMovingDeleted(actionTypeId, row)):
                return False

            ttj_id = forceRef(record.value('takenTissueJournal_id'))
            if ttj_id and forceString(QtGui.qApp.db.translate('TakenTissueJournal', 'id', ttj_id, 'externalId')) and not \
                    self.eventEditor.checkValueMessage(u'Вы пытаетесь удалить действие, зарегистрированное во внешней системе',
                                                       QtGui.qApp.userHasRight(urDeleteActionWithTissue), self._actionsPage.tblAPActions, row, 0):
                    return False

            self.beginRemoveRows(parentIndex, row, row + count - 1)
            # del self._items[row:row + count]

            removeItemList = self._items[row:row + count]
            for x in removeItemList:
                getJobTicketsFromAction(x[1])
                self._items.remove(x)

            self.endRemoveRows()
            return True
        else:
            return False

    def checkUpdates(self, eventId):
        changedItems = {}
        # db = QtGui.qApp.db
        # tableAction = db.table('Action')
        #
        # cond = [
        #     tableAction['deleted'].eq(0),
        #     tableAction['event_id'].eq(eventId),
        #     tableAction['modifyDatetime'].gt(self.__openDatetime),
        #     tableAction['modifyPerson_id'].ne(QtGui.qApp.userId)
        # ]
        # if self.actionTypeClass is not None:
        #     cond.append(tableAction['actionType_id'].inlist(self.actionTypeIdList))
        # if self.ignoredActionTypesIdList:
        #     cond.append(tableAction['actionType_id'].notInlist(self.ignoredActionTypesIdList))
        # actionTypeProtocolIdList = getActionTypeIdListByFlatCode(u'protocol%')
        # if actionTypeProtocolIdList:
        #     cond.append(tableAction['actionType_id'].notInlist(actionTypeProtocolIdList))
        #
        # for record in db.iterRecordList(tableAction, '*', cond, order=['idx', 'id']):
        #     changedItems[forceInt(record.value('id'))] = (record, CAction(record=record))

        return changedItems


    def loadItems(self, eventId):
        self._items = []
        db = QtGui.qApp.db
        tableAction = db.table('Action')
        tableEvent = db.table('Event')
        tableEventTypeAction = db.table('EventType_Action')
        tableActionType = db.table('ActionType')
        cond = [
            tableAction['deleted'].eq(0),
            tableAction['event_id'].eq(eventId)
        ]
        if self.actionTypeClass is not None:
            cond.append(tableAction['actionType_id'].inlist(self.actionTypeIdList))
        if self.ignoredActionTypesIdList:
            cond.append(tableAction['actionType_id'].notInlist(self.ignoredActionTypesIdList))
        actionTypeProtocolIdList = getActionTypeIdListByFlatCode(u'protocol%')
        if actionTypeProtocolIdList:
            cond.append(tableAction['actionType_id'].notInlist(actionTypeProtocolIdList))

        actionTypeIdList = []
        for record in db.iterRecordList(tableAction, '*', cond, order=['idx', 'id']):
            self.addItem((record, CAction(record=record)))
            actionTypeIdList.append(forceRef(record.value('actionType_id')))

        queryTable = tableEvent.innerJoin(tableEventTypeAction, tableEventTypeAction['eventType_id'].eq(tableEvent['eventType_id']))
        queryTable = queryTable.innerJoin(tableActionType, tableActionType['id'].eq(tableEventTypeAction['actionType_id']))
        notDeletedActionTypeRecordList = db.getRecordList(queryTable,
                                                          cols=[tableActionType['id'],
                                                                tableActionType['code'],
                                                                tableActionType['name']],
                                                          where=[tableEvent['id'].eq(eventId),
                                                                 tableEventTypeAction['isCompulsory'].eq(1),
                                                                 tableActionType['id'].inlist(actionTypeIdList)])
        for record in notDeletedActionTypeRecordList:
            self.notDeletedActionTypes[forceRef(record.value('id'))] = forceString(record.value('code')) + '|' + forceString(record.value('name'))
        self.reset()

    def saveItems(self, eventId, checkOnUpdates=True):
        updateItems = []
        if checkOnUpdates:
            updateItems = self.checkUpdates(eventId)
        if not updateItems:
            idList = []
            for record, action in self._items:
                if action:
                    self.eventEditor.getMKBValueForActionDuringSaving(record, action)
                    id = action.save(eventId, len(idList))
                    idList.append(id)

            db = QtGui.qApp.db
            Action = db.table('Action')

            cond = [Action['event_id'].eq(eventId),
                    Action['actionType_id'].inlist(self.actionTypeIdList),
                    Action['id'].notInlist(idList)]
            if self.ignoredActionTypesIdList:
                cond.append(Action['actionType_id'].notInlist(self.ignoredActionTypesIdList))

            actionTypeIgnoredIdList = getActionTypeIdListByFlatCode(u'protocol%')
            # actionTypeIgnoredIdList.extend(getActionTypeIdListByFlatCode(u'drug_therapy%'))
            # actionTypeIgnoredIdList.extend(getActionTypeIdListByFlatCode(u'drug_theraphy%')) # vitya mode
            if actionTypeIgnoredIdList:
                cond.append(Action['actionType_id'].notInlist(actionTypeIgnoredIdList))

            db.markRecordsDeleted(Action, cond)
        else:
            # TODO shepas: сделать окно с выбором отличий.
            if QtGui.QMessageBox.information(None, u'Информация', u'Обращение было изменено другим пользователем.\nПринять изменения?',
                                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                            QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
                self.applyAllUpdates(updateItems)
                self.saveItems(eventId, False)
            else:
                self.saveItems(eventId, False)

    def applyAllUpdates(self, updatesDict):
        u"""
        Замена обновленных экшенов и добавление новых
        """

        for record, action in self._items:
            actionId = forceInt(record.value('id'))
            if actionId in updatesDict.keys():
                if forceDateTime(updatesDict[actionId][0].value('createDatetime')) < self.__openDatetime:
                    idx = self._items.index((record, action))
                    self._items.remove((record, action))
                    self._items.insert(idx, updatesDict[actionId])
                else:
                    self._items.append(updatesDict[actionId])

    def isLocked(self, row):
        if 0 <= row < len(self._items):
            action = self._items[row][1]
            if action:
                return action.isLocked()
        return False

    def isLockedOrExposed(self, row):
        if 0 <= row < len(self._items):
            record, action = self._items[row]
            return forceInt(record.value('payStatus')) != 0 or action and action.isLocked()
        return False

    def isDeletable(self, row):
        if 0 <= row < len(self._items):
            record, action = self._items[row]
            if not action:
                return True
            return not self.isLockedOrExposed(row) and action.isDeletable()
        return True

    def actionTypeId(self, row):
        if 0 <= row < len(self._items):
            return forceInt(self._items[row][0].value('actionType_id'))
        else:
            return None

    def payStatus(self, row):
        if 0 <= row < len(self._items):
            return forceInt(self._items[row][0].value('payStatus'))
        else:
            return 0

    def removeRowEx(self, row):
        self.removeRows(row, 1)

    def upRow(self, row):
        if 0 < row < len(self._items):
            self._items[row - 1], self._items[row] = self._items[row], self._items[row - 1]
            self.emitRowsChanged(row - 1, row)
            return True
        else:
            return False

    def downRow(self, row):
        if 0 <= row < len(self._items) - 1:
            self._items[row + 1], self._items[row] = self._items[row], self._items[row + 1]
            self.emitRowsChanged(row, row + 1)
            return True
        else:
            return False

    def checkMaxOccursLimit(self, actionTypeId):
        actionType = CActionTypeCache.getById(actionTypeId)
        count = 0
        for record, action in self._items:
            if action and action.getType() == actionType:
                count += 1
        result = actionType.checkMaxOccursLimit(count, True)
        return result

    def checkReceivedDeleted(self, actionTypeId):
        result = True
        actionType = CActionTypeCache.getById(actionTypeId)
        if u'received' in actionType.flatCode.lower():
            for record, action in self._items:
                if action:
                    actionTypeItem = action.getType()
                    actFlatCode = actionTypeItem.flatCode.lower() if actionTypeItem else u''
                    errorName = u'Движение' if u'moving' in actFlatCode \
                                            else (u'Выписка' if u'leaved' in actFlatCode
                                                             else (u'Реанимация' if u'reanimation' in actFlatCode else None)
                                                 )
                    if errorName:
                        return actionType.checkReceivedMovingLeaved(u'Нельзя удалить действие "Поступление" если есть "%s"' % errorName)
        return result

    def checkMovingDeleted(self, actionTypeId, rowCurrent):
        result = True
        actionType = CActionTypeCache.getById(actionTypeId)
        if u'moving' in actionType.flatCode.lower():
            for row, item in enumerate(self.items()):
                action = item[1]
                if action:
                    actionTypeItem = action.getType()
                    if actionTypeItem and (u'leaved' in actionTypeItem.flatCode.lower()):
                        return actionType.checkReceivedMovingLeaved(u'Нельзя удалить действие "Движение" если есть "Выписка"')
                    elif row > rowCurrent and actionTypeItem and (u'moving' in actionTypeItem.flatCode.lower()):
                        return actionType.checkReceivedMovingLeaved(u'Нельзя удалить действие "Движение" если после него есть "Движение"')
        return result

    def checkMovingNoLeaved(self, actionTypeId):
        result = True
        actionType = CActionTypeCache.getById(actionTypeId)
        if u'moving' in actionType.flatCode.lower():
            for record, action in self._items:
                if action:
                    actionTypeItem = action.getType()
                    if actionTypeItem and (u'leaved' in actionTypeItem.flatCode.lower()):
                        return actionType.checkReceivedMovingLeaved(u'Действие "Движение" не должно применяться после действия "Выписка"')
                    elif actionTypeItem and (u'moving' in actionTypeItem.flatCode.lower()):
                        if not forceDate(record.value('endDate')):
                            return actionType.checkReceivedMovingLeaved(u'Действие "Движение" не может появится при наличии не законченного "Движение"')
        return result

    def checkMovingAfterReceived(self, actionTypeId):
        actionType = CActionTypeCache.getById(actionTypeId)
        if u'moving' in actionType.flatCode.lower():
            for record, action in self._items:
                if action:
                    actionTypeItem = action.getType()
                    if actionTypeItem and (u'received' in actionTypeItem.flatCode.lower()):
                        if not forceDate(record.value('endDate')):
                            return actionType.checkReceivedMovingLeaved(u'Действие "Движение" не может появиться при наличии неоконченного действия "Поступление"')
                        return True
            return actionType.checkReceivedMovingLeaved(u'Действие "Движение" не должно применяться пока нет действия действия "Поступление"')
        return True

    def checkLeavedAfterMoving(self, actionTypeId):
        actionType = CActionTypeCache.getById(actionTypeId)
        if u'leaved' in actionType.flatCode.lower():
            for record, action in self._items:
                if action:
                    actionTypeItem = action.getType()
                    if actionTypeItem and (u'moving' in actionTypeItem.flatCode.lower()):
                        return True
            return actionType.checkReceivedMovingLeaved(u'Действие "Выписка" не должно применяться пока нет действия "Движение"')
        return True

    def checkLeavedAfterMovingDate(self, actionTypeId):
        actionType = CActionTypeCache.getById(actionTypeId)
        if u'leaved' in actionType.flatCode.lower():
            for record, action in self._items:
                if action:
                    actionTypeItem = action.getType()
                    if actionTypeItem and (u'moving' in actionTypeItem.flatCode.lower()):
                        if not forceDate(record.value('endDate')):
                            return actionType.checkReceivedMovingLeaved(u'Действие "Выписка" не может появится при наличии не законченного действия "Движение"')
        return True

    def checkPeriodicActionPosibility(self, actionTypeId):
        actionType = CActionTypeCache.getById(actionTypeId)
        if actionType.frequencyCount:
            actionDate = forceDate(self.eventEditor.eventSetDateTime)
            db = QtGui.qApp.db
            tableAction = db.table('Action')
            tableEvent = db.table('Event')
            tableActionType = db.table('ActionType')
            cond = [tableEvent['client_id'].eq(self.eventEditor.clientId),
                    tableActionType['id'].eq(actionTypeId)]
            if actionType.frequencyPeriod and actionType.frequencyPeriodType:
                lowDate = None
                highDate = None
                if actionType.isFrequencyPeriodByCalendar:
                    if actionType.frequencyPeriodType == 1: # день
                        lowDate  = actionDate
                        highDate = actionDate
                    elif actionType.frequencyPeriodType == 2: # неделя
                        lowDate  = firstWeekDay(actionDate).addDays((1 - actionType.frequencyPeriod) * 7)
                        highDate = lastWeekDay(actionDate).addDays((1 - actionType.frequencyPeriod) * 7)
                    elif actionType.frequencyPeriodType == 3: # месяц
                        lowDate  = firstMonthDay(actionDate).addMonths(1 - actionType.frequencyPeriod)
                        highDate = lastMonthDay(actionDate).addMonths(1 - actionType.frequencyPeriod)
                    elif actionType.frequencyPeriodType == 4: # квартал (3 месяца)
                        lowDate  = firstQuarterDay(actionDate).addMonths((1 - actionType.frequencyPeriod) * 3)
                        highDate = lastQuarterDay(actionDate).addMonths((1 - actionType.frequencyPeriod) * 3)
                    elif actionType.frequencyPeriodType == 5: # полугодие
                        lowDate  = firstHalfYearDay(actionDate).addMonths((1 - actionType.frequencyPeriod) * 6)
                        highDate = lastHalfYearDay(actionDate).addMonths((1 - actionType.frequencyPeriod) * 6)
                    elif actionType.frequencyPeriodType == 6: # год
                        lowDate  = firstYearDay(actionDate).addYears((1 - actionType.frequencyPeriod))
                        highDate = lastYearDay(actionDate).addYears((1 - actionType.frequencyPeriod))
                else:
                    if actionType.frequencyPeriodType == 1: # день
                        lowDate = actionDate.addDays(-1 * actionType.frequencyPeriod)
                    elif actionType.frequencyPeriodType == 2: # неделя
                        lowDate = actionDate.addDays(-7 * actionType.frequencyPeriod)
                    elif actionType.frequencyPeriodType == 3: # месяц
                        lowDate = actionDate.addMonths(-1 * actionType.frequencyPeriod)
                    elif actionType.frequencyPeriodType == 4: # квартал (3 месяца)
                        lowDate = actionDate.addMonths(-3 * actionType.frequencyPeriod)
                    elif actionType.frequencyPeriodType == 5: # полугодие
                        lowDate = actionDate.addMonths(-6 * actionType.frequencyPeriod)
                    elif actionType.frequencyPeriodType == 6: # год
                        lowDate = actionDate.addYears(-1 * actionType.frequencyPeriod)
                    if lowDate:
                        lowDate = lowDate.addDays(1)
                    highDate = actionDate

                if lowDate and highDate:
                    cond.append(tableAction['begDate'].dateBetween(lowDate, highDate))

            table = tableAction.innerJoin(tableEvent, [tableEvent['id'].eq(tableAction['event_id']), tableEvent['deleted'].eq(0)])
            table = table.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
            count = db.getCount(table, tableAction['id'], cond)

            for record, action in self._items:
                if record.value('id').isNull() and actionTypeId == forceRef(record.value('actionType_id')):
                    count += 1

            if count >= actionType.frequencyCount:
                frequencyPeriodTypeNames = {0: (u'-',)*3,
                                            1: (u'день', u'дня', u'дней'),
                                            2: (u'неделю', u'недели', u'недель'),
                                            3: (u'месяц', u'месяца', u'месяцев'),
                                            4: (u'квартал', u'квартала', u'кварталов'),
                                            5: (u'полугодие', u'полугодия', u'полугодий'),
                                            6: (u'год', u'года', u'лет')}
                widget = QtGui.qApp.activeModalWidget() or QtGui.qApp.mainWindow or None
                isStrict = actionType.isStrictFrequency and not QtGui.qApp.userHasRight(urIgnoreRestrictActionByFrequency)
                res = QtGui.QMessageBox.critical(widget,
                                            u'Произошла ошибка',
                                            u'Действие типа "%s" должно применяться не более %s в %s'
                                                % (actionType.name,
                                                   formatNum1(actionType.frequencyCount, (u'раза', u'раз', u'раз')),
                                                   formatNum1(actionType.frequencyPeriod, frequencyPeriodTypeNames[actionType.frequencyPeriodType])),
                                            buttons = QtGui.QMessageBox.Close if isStrict else (QtGui.QMessageBox.Ignore | QtGui.QMessageBox.Close),
                                            defaultButton = QtGui.QMessageBox.Close)
                if res != QtGui.QMessageBox.Ignore:
                    return False
        return True

    def emitRowsChanged(self, row1, row2):
        index1 = self.index(row1, 0)
        index2 = self.index(row2, self.columnCount())
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index1, index2)


# Данные ниже функции используются в JobTicketEditor при добавлении действий однородных по jobType_id
def fillActionRecord(obj, record, actionTypeId, amount=None, financeId=None, contractId=None):
    eventEditor = obj.eventEditor
    if actionTypeId:
        actionType = CActionTypeCache.getById(actionTypeId)
        defaultStatus = actionType.defaultStatus
        defaultDirectionDate = actionType.defaultDirectionDate
        defaultBeginDate = actionType.defaultBeginDate
        defaultPlannedEndDate = actionType.defaultPlannedEndDate
        defaultEndDate = actionType.defaultEndDate
        defaultExecPersonId = actionType.defaultExecPersonId
        defaultSetPersonId = actionType.defaultSetPersonId
        defaultPerson = actionType.defaultPersonInEvent
        defaultMKB = actionType.defaultMKB
        defaultMorphology = actionType.defaultMorphology
        defaultMES = actionType.defaultMES
        defaultOrgId = actionType.defaultOrgId
        office = actionType.office

        record.setValue('actionType_id', toVariant(actionTypeId))
    else:
        defaultStatus = ActionStatus.Done  # Закончено
        defaultDirectionDate = CActionType.dddUndefined
        defaultBeginDate = CActionType.dddUndefined
        defaultPlannedEndDate = 0  # Не планируется
        defaultEndDate = CActionType.dedEventExecDate  # Дата события
        defaultExecPersonId = None
        defaultSetPersonId = None
        defaultPerson = CActionType.dpEmpty
        defaultMKB = None
        defaultMorphology = None
        defaultMES = 0
        defaultOrgId = None
        office = ''

    if defaultPlannedEndDate in [1, 2]:
        plannedEndDate = addPeriod(eventEditor.eventSetDateTime.date(), 2, defaultPlannedEndDate == 1)
    elif defaultPlannedEndDate == 3:
        plannedEndDate = getPlannedEndDateByJobTicketProperty(record)
    else:
        plannedEndDate = None

    if defaultEndDate == CActionType.dedEventExecDate:
        endDate = forceDateTime(eventEditor.eventDate)
        if not endDate.isNull():
            endDate.setTime(eventEditor.endTime())
    elif defaultEndDate == CActionType.dedEventSetDate:
        endDate = eventEditor.eventSetDateTime
    elif defaultEndDate == CActionType.dedCurrentDate:
        endDate = QtCore.QDateTime.currentDateTime()
    else:
        if defaultStatus in (ActionStatus.Done, ActionStatus.WithoutResult):
            endDate = QtCore.QDateTime.currentDateTime()
        elif defaultStatus == ActionStatus.NotProvided:
            endDate = forceDateTime(eventEditor.eventDate)
        else:
            endDate = QtCore.QDateTime()

    if defaultBeginDate == CActionType.dddEventSetDate:
        begDate = eventEditor.eventSetDateTime
    elif defaultBeginDate == CActionType.dddCurrentDate:
        begDate = QtCore.QDateTime().currentDateTime()
    elif defaultBeginDate == CActionType.dddActionExecDate:
        if endDate.isValid():
            if endDate < eventEditor.eventSetDateTime:
                begDate = eventEditor.eventSetDateTime
            else:
                begDate = endDate
        else:
            begDate = eventEditor.eventSetDateTime
    else:
        begDate = eventEditor.eventSetDateTime

    if defaultDirectionDate == CActionType.dddEventSetDate:
        directionDate = eventEditor.eventSetDateTime
    elif defaultDirectionDate == CActionType.dddCurrentDate:
        directionDate = QtCore.QDateTime().currentDateTime()
    elif defaultDirectionDate == CActionType.dddActionExecDate:
        if endDate.isValid():
            if endDate < eventEditor.eventSetDateTime:
                directionDate = eventEditor.eventSetDateTime
            else:
                directionDate = endDate
        else:
            directionDate = eventEditor.eventSetDateTime
    else:
        directionDate = eventEditor.eventSetDateTime

    if getEventTypeForm(eventEditor.eventTypeId) == '001':
        setPersonId = eventEditor.cmbSetPerson.value()
    elif defaultSetPersonId:
        setPersonId = defaultSetPersonId
    else:
        setPersonId = eventEditor.getSuggestedPersonId()

    if defaultExecPersonId:
        personId = defaultExecPersonId
    else:
        if defaultPerson == CActionType.dpCurrentUser:
            personId = QtGui.qApp.userId
        elif defaultPerson == CActionType.dpEventExecPerson:
            personId = eventEditor.personId
        elif defaultPerson == CActionType.dpSetPerson:
            personId = setPersonId
        else:
            personId = None

    if personId and not checkSpeciality(personId, actionTypeId):
        personId = None

    defaultMKBValue = ''
    defaultMorphologyMKBValue = ''
    if defaultMKB:
        defaultMKBValue = eventEditor.getDefaultMKBValue(defaultMKB, setPersonId)
    if defaultMorphology:
        defaultMorphologyMKBValue = eventEditor.getDefaultMorphologyValue(defaultMorphology, setPersonId)

    begDate = max(begDate, directionDate)
    record.setValue('directionDate', toVariant(directionDate))
    record.setValue('setPerson_id', toVariant(setPersonId))
    record.setValue('begDate', toVariant(begDate))
    record.setValue('begTime', toVariant(begDate.time()))
    record.setValue('plannedEndDate', toVariant(plannedEndDate))
    record.setValue('endDate', toVariant(endDate))
    record.setValue('endTime', toVariant(endDate.time()))
    record.setValue('status', toVariant(defaultStatus))
    record.setValue('office', toVariant(office))
    record.setValue('person_id', toVariant(personId))
    record.setValue('MKB', toVariant(defaultMKBValue))
    record.setValue('morphologyMKB', toVariant(defaultMorphologyMKBValue))
    record.setValue('org_id', toVariant(defaultOrgId))
    if actionTypeId:
        if not (amount and actionType.amountEvaluation == CActionType.userInput):
            amount = obj.getDefaultAmountEx(actionType, record, None)
    else:
        amount = 0
    record.setValue('amount', toVariant(amount))
    if not financeId:
        financeId = eventEditor.getActionFinanceId(record)
    if getEventActionContract(obj.eventEditor.eventTypeId):
        contractId = obj.getDefaultContractId(actionTypeId, financeId, begDate, endDate,
                                              contractId or eventEditor.contractId)
    else:
        contractId = None
    record.setValue('uet',
                    toVariant(amount * obj.eventEditor.getUet(actionTypeId, personId, financeId, contractId)))
    record.setValue('finance_id', toVariant(financeId))
    record.setValue('contract_id', toVariant(contractId))

    if defaultMES == 1:
        defaultMESId = eventEditor.getMesId()
    elif defaultMES == 2:
        mesIdList = getActionTypeMesIdList(actionTypeId, financeId)
        defaultMESId = mesIdList[0] if len(mesIdList) == 1 else None
    else:
        defaultMESId = None
    record.setValue('MES_id', toVariant(defaultMESId))


def getPlannedEndDateByJobTicketProperty(record):
    # план заполняется по номерку, a номерок может подбираться автоматом
    if record:
        action = CAction(record=record)
        actionType = action.getType()
        propertyTypeList = actionType.getPropertiesById().values()
        for propertyType in propertyTypeList:
            if type(propertyType.valueType) == CJobTicketActionPropertyValueType:
                property = action.getPropertyById(propertyType.id)
                jobTicketId = property.getValue()
                if jobTicketId:
                    db = QtGui.qApp.db
                    date = forceDate(db.translate('Job_Ticket', 'id', jobTicketId, 'datetime'))
                    jobId = forceRef(db.translate('Job_Ticket', 'id', jobTicketId, 'master_id'))
                    jobTypeId = forceRef(db.translate('Job', 'id', jobId, 'jobType_id'))
                    ticketDuration = forceInt(db.translate('rbJobType', 'id', jobTypeId, 'ticketDuration'))
                    return date.addDays(ticketDuration)
        return None


def getActionDefaultAmountEx(obj, actionType, record, action):
    result = actionType.amount
    if actionType.amountEvaluation == CActionType.eventVisitCount:
        result = result * obj.eventEditor.getVisitCount()
    elif actionType.amountEvaluation == CActionType.eventLength:
        result = result * obj.eventEditor.getEventLength(True)
    elif actionType.amountEvaluation == CActionType.eventLengthWithoutRedDays:
        result = result * obj.eventEditor.getEventLength(False)
    elif actionType.amountEvaluation == CActionType.actionLength:
        result = result * obj.getActionLength(record, True)
    elif actionType.amountEvaluation == CActionType.actionLengthWithoutRedDays:
        result = result * obj.getActionLength(record, False)
    elif actionType.amountEvaluation == CActionType.actionFilledProps:
        result = result * action.getFilledPropertiesCount() if action else 0
    elif actionType.amountEvaluation in (CActionType.bedDaysEventLength, CActionType.bedDaysEventLengthWithoutRedDays):
        mesId = obj.eventEditor.getMesId()
        if mesId and obj.eventEditor.eventDate >= obj.eventEditor.eventSetDateTime.date():
            dayCount = obj.eventEditor.getEventLength(actionType.amountEvaluation == CActionType.bedDaysEventLength)
            #obj.eventEditor.eventSetDateTime.date().daysTo(obj.eventEditor.eventDate)
            #if dayCount <= 0:
            #    dayCount = 1
            minAmount = forceInt(QtGui.qApp.db.translate('mes.MES', 'id', mesId, 'minDuration'))
            maxAmount = forceInt(QtGui.qApp.db.translate('mes.MES', 'id', mesId, 'maxDuration'))
            if dayCount > maxAmount:
                result = dayCount - maxAmount
            elif dayCount < minAmount:
                result = dayCount

    return result


def getActionDefaultContractId(obj, actionTypeId, financeId, begDate, endDate, contractId):
    model = CContractDbModel(None)
    model.setOrgId(obj.eventEditor.orgId)
    model.setEventTypeId(obj.eventEditor.eventTypeId)
    model.setClientInfo(obj.eventEditor.clientId,
                        obj.eventEditor.clientSex,
                        obj.eventEditor.clientAge,
                        obj.eventEditor.clientWorkOrgId,
                        obj.eventEditor.clientPolicyInfoList)
    model.setFinanceId(financeId)
    model.setActionTypeId(actionTypeId)
    model.setBegDate(begDate or QtCore.QDate.currentDate())
    model.setEndDate(endDate or QtCore.QDate.currentDate())
    model.initDbData()
    return contractId if contractId and model.searchId(contractId) >= 0 else model.getId(0)
