# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from itertools import chain
from library.vm_collections import DefaultOrderedDict

from Events.Action import ActionClass, CAction, CActionTypeCache, CJobTicketActionPropertyValueType
from Events.ActionsModel import CActionsModel
from Events.Utils import getMainActionTypeAnalyses, getMainActionTypesAnalyses
from library.Utils import forceDate, forceRef, forceString, toVariant


class CActionsAnalysesModel(CActionsModel):
    def __init__(self, parent, actionTypeClass=None):
        CActionsModel.__init__(self, parent, actionTypeClass)
        self._mainActionTypes = set(getMainActionTypesAnalyses())
        self._analysesGroups = DefaultOrderedDict(list)  # { CAction: [list of CAction] }
        self.orderByDirectionDate = QtGui.qApp.isSortAnalizesByDirectionDateAndShowImportDate()

    def _recalcItems(self):
        self._items = [(action.getRecord(), action) for action in self.flatActions()]

    def flatActions(self):
        return list(chain.from_iterable([main] + children for main, children in self._analysesGroups.iteritems() if children))

    def isMainActionType(self, actionTypeId):
        return actionTypeId in self._mainActionTypes

    def getAnalysesGroups(self):
        return self._analysesGroups

    def getMainActions(self):
        return self._analysesGroups.keys()

    def getMainAction(self, actionTypeId, checkFilledJobTicket=True):
        u""" Проверка наличия в модели главного действия группы анализов (с заполненным номерком) """
        for mainAction in filter(lambda a: a.getType().id == actionTypeId, self._analysesGroups):
            hasFilledJobTicket = any((actionProperty.getRecord() is not None and
                                      actionProperty.getValue() is not None)
                                     for actionProperty in mainAction
                                     if isinstance(actionProperty.type().valueType, CJobTicketActionPropertyValueType))
            if not checkFilledJobTicket or not hasFilledJobTicket:
                return mainAction

        return self.newAction(actionTypeId)

    def newAction(self, actionTypeId):
        record = self.fillNewRecord(actionTypeId)
        return CAction(record=record)

    def addItem(self, item):
        _, action = item
        if self.isMainActionType(action.getType().id):
            self._analysesGroups[action] = []
        else:
            if action.getType().groupId is None:
                QtGui.QMessageBox.critical(QtGui.qApp.mainWindow, u'Внимание!', u'Один или несколько анализов не настроено!')
                return
            self._analysesGroups[self.getMainAction(action.getType().groupId)].append(action)
        action.initPropertyPresetValues()

        cnt = len(self._items)
        self.beginInsertRows(self.index(cnt, 0), 1, 1)
        self._recalcItems()
        self.endInsertRows()

    def insertItem(self, item):
        self.addItem(item)
        return len(self._items) - 1

    def items(self):
        return [(action.getRecord(), action) for action in self.flatActions()]

    def loadItems(self, eventId):
        self._analysesGroups.clear()
        self._items = []

        db = QtGui.qApp.db
        tableAction = db.table('Action')
        tableAT = db.table('ActionType')

        table = tableAction.innerJoin(tableAT, [tableAT['id'].eq(tableAction['actionType_id']),
                                                tableAT['class'].eq(ActionClass.Analyses),
                                                tableAT['deleted'].eq(0)])
        cols = [
            tableAction['id'],
            tableAction['parent_id']
        ]
        cond = [
            tableAction['event_id'].eq(eventId),
            tableAction['deleted'].eq(0)
        ]

        idList = []
        childMap = DefaultOrderedDict(list)
        for record in db.iterRecordList(table, cols, cond, order=tableAction['idx'] if not self.orderByDirectionDate else tableAction['directionDate'].desc()):
            id = forceRef(record.value('id'))
            parentId = forceRef(record.value('parent_id'))
            idList.append(id)
            if parentId:
                childMap[parentId].append(id)

        recordMap = dict((forceRef(rec.value('id')), rec)
                         for rec in db.iterRecordList(tableAction, '*', tableAction['id'].inlist(idList)))

        for mainActionId, childrenIdList in childMap.iteritems():
            mainAction = CAction(record=recordMap[mainActionId])
            for actionId in childrenIdList:
                action = CAction(record=recordMap[actionId])
                self._analysesGroups[mainAction].append(action)

        self._recalcItems()
        self.reset()

    def _removeRow(self, row):
        u"""
        Удаление действия в заданной строке
        :param row: номер строки
        :return: кол-во удаленных действий
        """
        removedRows = 0
        record, action = self._items[row]
        if action in self._analysesGroups:
            removedRows = len(self._analysesGroups[action]) + 1
            del self._analysesGroups[action]
        else:
            for mainAction, children in self._analysesGroups.iteritems():
                if action in children:
                    if len(children) == 1:
                        removedRows = 2
                        del self._analysesGroups[mainAction]
                    else:
                        removedRows = 1
                        self._analysesGroups[mainAction].remove(action)
        return removedRows

    def removeRows(self, row, count, parentIndex=QtCore.QModelIndex()):
        if 0 <= row <= len(self._items) - count:
            actionTypeId = forceRef(self.getRecordByRow(row).value('actionType_id'))

            if actionTypeId in self.notDeletedActionTypes:
                QtGui.QMessageBox.critical(None, u'Ошибка', u'Невозможно удалить обязательные услуги: \'%s\'.' % ', '.join(self.notDeletedActionTypes.values()),
                                           QtGui.QMessageBox.Ok)
                return False

            if any(self.isLocked(r) for r in xrange(row, row + count)):
                return False

            itemsCount = len(self._items)
            removedRows = sum(map(self._removeRow, xrange(row, row + count)))

            self.beginRemoveRows(parentIndex, itemsCount - removedRows, itemsCount - 1)
            self._recalcItems()
            self.endRemoveRows()

            return True

        return False

    def setData(self, index, value, role=QtCore.Qt.EditRole, presetAction=None):
        # create action from combobox
        if role == QtCore.Qt.EditRole:
            actionTypeId = forceRef(value)
            if self.isMainActionType(actionTypeId):
                self._analysesGroups.setdefault(self.getMainAction(actionTypeId), [])
            else:
                mainActionTypeId = getMainActionTypeAnalyses(actionTypeId)
                self._analysesGroups[self.getMainAction(mainActionTypeId)].append(self.newAction(actionTypeId))

            self._recalcItems()

            self.emitItemsCountChanged()
            self.emitDataChanged(self.index(0, 0), self.index(len(self._items) - 1, self.columnCount() - 1))

            return True
        return False

    def data(self, index, role=QtCore.Qt.DisplayRole):
        row, column = index.row(), index.column()
        if 0 <= row < len(self._items):
            item = self.getItemByRow(row)
            record, action = item

            if role == QtCore.Qt.EditRole:
                return record.value('actionType_id')

            elif role == QtCore.Qt.DisplayRole:
                if column == 0:
                    outName = forceString(record.value('specifiedName'))
                    actionTypeId = forceRef(record.value('actionType_id'))
                    if actionTypeId:
                        actionType = CActionTypeCache.getById(actionTypeId)
                        if actionType:
                            outName = actionType.name + ' ' + outName if outName else actionType.name
                        if not self.isMainActionType(actionTypeId):
                            outName = ' ' * 10 + outName
                    return QtCore.QVariant(outName)

                elif column == 1:
                    if action in self.getMainActions():
                        return toVariant(forceDate(record.value('directionDate')))
                    elif self.orderByDirectionDate:
                        return toVariant(forceString(record.value('importDate')))

            elif role in (QtCore.Qt.StatusTipRole, QtCore.Qt.ToolTipRole):
                if action:
                    actionType = action.getType()
                    return QtCore.QVariant(u'{0}: {1}'.format(actionType.code, actionType.name))

            elif role == QtCore.Qt.ForegroundRole:
                if action and action.getType().isRequiredCoordination and record.isNull('coordDate'):
                    return QtCore.QVariant(QtGui.QColor(255, 0, 0))

            elif role == QtCore.Qt.FontRole:
                if self.isMainActionType(forceRef(record.value('actionType_id'))):
                    boldFont = QtGui.QFont()
                    boldFont.setWeight(QtGui.QFont.Bold)
                    return QtCore.QVariant(boldFont)

        return QtCore.QVariant()

    def saveItems(self, eventId):
        idList = []
        for mainAction, childrendActions in self._analysesGroups.iteritems():
            parentId = mainAction.save(eventId, len(idList))
            idList.append(parentId)

            for childAction in childrendActions:
                childAction.getRecord().setValue('parent_id', toVariant(parentId))
                actionId = childAction.save(eventId, len(idList))
                idList.append(actionId)

        db = QtGui.qApp.db
        tableAction = db.table('Action')
        tableActionType = db.table('ActionType')

        table = tableAction.innerJoin(tableActionType, [tableActionType['id'].eq(tableAction['actionType_id']),
                                                        tableActionType['class'].eq(ActionClass.Analyses)])
        existsIdList = db.getIdList(table, tableAction['id'], tableAction['event_id'].eq(eventId))

        deletedIdList = list(set(existsIdList).difference(set(idList)))
        db.markRecordsDeleted(tableAction, tableAction['id'].inlist(deletedIdList))
