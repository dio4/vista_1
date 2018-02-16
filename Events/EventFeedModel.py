# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QAbstractTableModel, QModelIndex

from Events.MealComboBox import CMealComboBox
from library.DialogBase import CConstructHelperMixin
from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
from library.InDocTable import CInDocTableView
from library.Utils import forceDate, forceInt, forceRef, forceString, toVariant, forceBool

from Ui_EventFeedMealList import Ui_EventFeedMealListDialog


class CFeedModel(QtCore.QAbstractTableModel):
    def __init__(self, parent):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.headers = []
        self.items = {}
        self.mealDays = []
        self.dates = []
        self.empty = []
        self.surrogateEventFeedId = 0  # we give surrogate IDs to new records that are not in DB yet
        self.editable = True

        db = QtGui.qApp.db

        tableRBMeal = db.table('rbMeal')
        records = db.getRecordList(tableRBMeal)
        self.mealMap = {}
        for record in records:
            mealId = forceInt(record.value('id'))
            mealName = forceString(record.value('name'))
            mealAmount = forceString(record.value('amount'))
            mealUnit = forceString(record.value('unit'))
            self.mealMap[mealId] = mealName + u', ' + mealAmount + u' ' + mealUnit

        tableRBDiet = db.table('rbDiet')
        records = db.getRecordList(tableRBDiet)
        self.dietMap = {}
        for record in records:
            dietId = forceInt(record.value('id'))
            dietCode = forceString(record.value('code'))
            dietName = forceString(record.value('name'))
            allowMeals = forceBool(record.value('allow_meals'))
            self.dietMap[dietId] = {'code': dietCode, 'name': dietName, 'allow_meals': allowMeals}

    def columnCount(self, index=QtCore.QModelIndex(), *args, **kwargs):
        return len(self.headers)

    def rowCount(self, index=QtCore.QModelIndex(), *args, **kwargs):
        return len(self.dates) + 1

    def cellIsEditable(self, index=QtCore.QModelIndex()):
        column = index.column()
        row = index.row()
        if row == len(self.dates):
            return column == 0
        elif column in [0, 1, 2]:
            return True
        else:
            dietId = forceRef(self.mealDays[row].value('diet_id'))
            return dietId is None or self.dietMap[dietId]['allow_meals']

    def flags(self, index=QtCore.QModelIndex()):
        column = index.column()
        result = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        if self.cellIsEditable(index) and column <= 2:
            result |= QtCore.Qt.ItemIsEditable
        return result

    def insertFromMenu(self, id, begDate, endDate, update=False):
        rbMenuRecord = QtGui.qApp.db.getRecord('rbMenu', '*', id)
        records = QtGui.qApp.db.getRecordList('rbMenu_Content', '*', 'master_id = %d' % id)
        if rbMenuRecord or records:
            if update:
                nextDate = begDate
                while nextDate <= endDate:
                    nextDate = nextDate.addDays(1)
            nextDate = begDate
            while nextDate <= endDate:
                if update or (not update and (nextDate not in self.dates)):
                    vCnt = len(self.dates) - 1
                    vIndex = QtCore.QModelIndex()
                    self.beginInsertRows(vIndex, vCnt, vCnt)

                    self.dates.append(nextDate)
                    self.mealDays.append(self.emptyEventFeedRecord())
                    self.surrogateEventFeedId -= 1
                    newId = self.surrogateEventFeedId
                    self.mealDays[-1].setValue('id', toVariant(newId))
                    self.mealDays[-1].setValue('date', toVariant(nextDate))
                    self.mealDays[-1].setValue('diet_id', rbMenuRecord.value('diet_id'))
                    self.mealDays[-1].setValue('courtingDiet_id', rbMenuRecord.value('courtingDiet_id'))
                    self.items.setdefault(newId, {})

                    for record in records:
                        mealTimeId = forceRef(record.value('mealTime_id'))
                        if mealTimeId:
                            newMealRecord = self.emptyEventFeedMealRecord()
                            newMealRecord.setValue('master_id', toVariant(newId))
                            newMealRecord.setValue('mealTime_id', toVariant(mealTimeId))
                            newMealRecord.setValue('meal_id', record.value('meal_id'))
                            self.items.setdefault(newId, {}).setdefault(mealTimeId, []).append(newMealRecord)
                    self.empty.append(False)

                    self.endInsertRows()
                nextDate = nextDate.addDays(1)

        self.reset()

    def setEditable(self, value):
        self.editable = value

    def isEditable(self):
        return self.editable

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                header = self.headers[section]
                if header:
                    return QtCore.QVariant(header[1])
        return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = index.column()
        row = index.row()
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.ToolTipRole:
            if row < len(self.dates):
                date = self.dates[row]
                if column == 0:
                    if date:
                        return QtCore.QVariant(QtCore.QDate(date))
                elif column in [1, 2]:
                    diet = forceRef(self.mealDays[row].value('diet_id' if column == 1 else 'courtingDiet_id'))
                    if diet is not None:
                        return toVariant(self.dietMap[diet]['name'])
                else:
                    if self.headers[column] and self.headers[column][0]:
                        eventFeedId = forceInt(self.mealDays[row].value('id'))
                        mealTimeId = self.headers[column][0]
                        if eventFeedId and mealTimeId:
                            mealIdList = self.items.get(eventFeedId, {}).get(mealTimeId, [])
                            mealMenu = [self.mealMap[forceInt(meal.value('meal_id'))] for meal in mealIdList]
                            return toVariant(u'\n'.join(mealMenu))
        elif role == QtCore.Qt.EditRole:
            if row < len(self.dates):
                date = self.dates[row]
                if column == 0:
                    if date:
                        return QtCore.QVariant(QtCore.QDate(date))
                elif column in [1, 2]:
                    diet = forceRef(self.mealDays[row].value('diet_id' if column == 1 else 'courtingDiet_id'))
                    if diet:
                        return toVariant(diet)
                else:
                    eventFeedId = forceInt(self.mealDays[row].value('id'))
                    mealTimeId = self.headers[column][0]
                    if eventFeedId and mealTimeId:
                        mealRecordList = self.items.get(eventFeedId, {}).get(mealTimeId, [])
                        return toVariant(mealRecordList)
        return QtCore.QVariant()

    def loadHeader(self):
        self.headers = [[None, u'Дата'], [None, u'Диета'], [None, u'Диета ухаживающего']]
        db = QtGui.qApp.db
        table = db.table('rbMealTime')
        records = db.getRecordList(table, '*', where='', order='code')
        for record in records:
            header = [forceRef(record.value('id')),
                      forceString(record.value('name'))
                      ]
            self.headers.append(header)
        self.reset()

    def items(self):
        return self.items

    @staticmethod
    def emptyEventFeedRecord():
        db = QtGui.qApp.db
        tableEventFeed = db.table('Event_Feed')
        return tableEventFeed.newRecord()

    @staticmethod
    def emptyEventFeedMealRecord():
        db = QtGui.qApp.db
        tableEventFeedMeal = db.table('Event_Feed_Meal')
        return tableEventFeedMeal.newRecord()

    def loadData(self, eventId):
        self.items = {}
        self.mealDays = []
        self.dates = []
        self.empty = []
        if eventId:
            db = QtGui.qApp.db

            tableEventFeed = db.table('Event_Feed')
            cond = [tableEventFeed['event_id'].eq(eventId), tableEventFeed['deleted'].eq(0)]
            records = db.getRecordList(tableEventFeed, '*', cond, 'Event_Feed.date ASC')
            eventFeedIdList = []
            for record in records:
                date = forceDate(record.value('date'))
                eventFeedIdList.append(forceInt(record.value('id')))
                if date and len(self.dates) > 0:
                    insertDate = self.dates[-1].addDays(1)
                    while date > insertDate:
                        self.dates.append(insertDate)
                        self.mealDays.append(self.emptyEventFeedRecord())
                        self.mealDays[-1].setValue('date', toVariant(insertDate))
                        self.surrogateEventFeedId -= 1
                        self.mealDays[-1].setValue('id', toVariant(self.surrogateEventFeedId))
                        self.items.setdefault(self.surrogateEventFeedId, {})
                        self.empty.append(True)
                        insertDate = insertDate.addDays(1)
                self.dates.append(date)
                self.mealDays.append(record)
                self.items.setdefault(forceInt(record.value('id')), {})
                self.empty.append(False)

            tableEventFeedMeal = db.table('Event_Feed_Meal')
            cond = [tableEventFeedMeal['master_id'].inlist(eventFeedIdList), tableEventFeedMeal['deleted'].eq(0)]
            mealRecords = db.getRecordList(tableEventFeedMeal, '*', cond)
            for mealRecord in mealRecords:
                eventFeedId = forceInt(mealRecord.value('master_id'))
                mealTimeId = forceInt(mealRecord.value('mealTime_id'))
                self.items.setdefault(eventFeedId, {}).setdefault(mealTimeId, []).append(mealRecord)

        self.reset()

    def addNewRow(self):
        vCnt = len(self.dates)
        vIndex = QtCore.QModelIndex()
        self.beginInsertRows(vIndex, vCnt, vCnt)
        self.dates.append(QtCore.QDate())
        self.mealDays.append(self.emptyEventFeedRecord())
        self.surrogateEventFeedId -= 1
        self.mealDays[-1].setValue('id', toVariant(self.surrogateEventFeedId))
        self.items.setdefault(self.surrogateEventFeedId, {})
        self.empty.append(True)
        self.insertRows(vCnt, 1, vIndex)
        self.endInsertRows()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            column = index.column()
            row = index.row()
            date = self.dates[row] if row < len(self.dates) else None
            header = self.headers[column]
            if column == 0:
                newDate = forceDate(value)
                if newDate:
                    if row == len(self.dates):
                        if value.isNull():
                            return False
                        self.addNewRow()
                    self.dates[row] = newDate
                    self.mealDays[row].setValue('date', newDate)
                    self.empty[row] = False
            elif date:
                self.empty[row] = False
                if column == 1:
                    self.mealDays[row].setValue('diet_id', value)
                elif column == 2:
                    self.mealDays[row].setValue('courtingDiet_id', value)
                else:
                    eventFeedId = forceInt(self.mealDays[row].value('id'))
                    mealTimeId = header[0]
                    self.items.setdefault(eventFeedId, {})
                    mealRecordList = [variantItem.toPyObject() for variantItem in value.toList()]
                    for mealRecord in mealRecordList:
                        mealRecord.setValue('master_id', eventFeedId)
                        mealRecord.setValue('mealTime_id', mealTimeId)
                    self.items[eventFeedId][mealTimeId] = mealRecordList
            self.emitCellChanged(row, column)
            return True
        return False

    def saveData(self, eventId):
        db = QtGui.qApp.db
        tableEventFeed = db.table('Event_Feed')
        tableEventFeedMeal = db.table('Event_Feed_Meal')
        eventId = toVariant(eventId)

        eventFeedIdList = []
        for row, record in enumerate(self.mealDays):
            if not self.empty[row]:
                oldId = forceInt(record.value('id'))
                if oldId < 0:
                    record.setNull('id')
                record.setValue('event_id', eventId)
                eventFeedId = db.insertOrUpdate(tableEventFeed, record)
                record.setValue('id', toVariant(eventFeedId))
                eventFeedIdList.append(eventFeedId)
                if oldId in self.items:
                    self.items[eventFeedId] = self.items.pop(oldId)
                    for mealList in self.items[eventFeedId].values():
                        for mealRecord in mealList:
                            mealRecord.setValue('master_id', toVariant(eventFeedId))
        eventFeedFilter = [
            tableEventFeed['event_id'].eq(eventId),
            tableEventFeed['id'].notInlist(eventFeedIdList)
        ]
        db.markRecordsDeleted(tableEventFeed, eventFeedFilter)

        for eventFeedId, mealTimeMap in self.items.items():
            eventFeedMealIdList = []
            for mealList in mealTimeMap.values():
                for mealRecord in mealList:
                    eventFeedMealId = db.insertOrUpdate(tableEventFeedMeal, mealRecord)
                    mealRecord.setValue('id', toVariant(eventFeedMealId))
                    eventFeedMealIdList.append(eventFeedMealId)
            eventFeedMealFilter = [
                tableEventFeedMeal['master_id'].eq(eventFeedId),
                tableEventFeedMeal['id'].notInlist(eventFeedMealIdList)
            ]
            db.markRecordsDeleted(tableEventFeedMeal, eventFeedMealFilter)

        db.markRecordsDeleted(tableEventFeedMeal, tableEventFeedMeal['master_id'].inlist(
            db.getIdList(tableEventFeed, where=[
                tableEventFeed['event_id'].eq(eventId),
                tableEventFeed['id'].notInlist(eventFeedIdList)
            ])
        ))

    def upRow(self, row):
        if 0 < row < len(self.dates):
            self.dates[row - 1], self.dates[row] = self.dates[row], self.dates[row - 1]
            self.mealDays[row - 1], self.mealDays[row] = self.mealDays[row], self.mealDays[row - 1]
            self.empty[row - 1], self.empty[row] = self.empty[row], self.empty[row - 1]
            self.emitRowsChanged(row - 1, row)
            return True
        else:
            return False

    def downRow(self, row):
        if 0 <= row < len(self.dates) - 1:
            self.dates[row + 1], self.dates[row] = self.dates[row], self.dates[row + 1]
            self.mealDays[row + 1], self.mealDays[row] = self.mealDays[row], self.mealDays[row + 1]
            self.empty[row + 1], self.empty[row] = self.empty[row], self.empty[row + 1]
            self.emitRowsChanged(row, row + 1)
            return True
        else:
            return False

    def removeRows(self, row, count, parentIndex=QtCore.QModelIndex(), *args, **kwargs):
        if 0 <= row and row + count <= len(self.dates):
            self.beginRemoveRows(parentIndex, row, row + count - 1)
            for index in range(row, row + count):
                self.items.pop(forceInt(self.mealDays[index].value('id')), None)
            del self.dates[row:(row + count)]
            del self.mealDays[row:(row + count)]
            del self.empty[row:(row + count)]
            self.endRemoveRows()
            self.emitItemsCountChanged()
            return True
        else:
            return False

    def removeRow(self, row, parent=QtCore.QModelIndex(), *args, **kwargs):
        if 0 <= row < len(self.dates):
            self.beginRemoveRows(parent, row, row)
            self.items.pop(forceInt(self.mealDays[row].value('id')), None)
            del self.dates[row]
            del self.mealDays[row]
            del self.empty[row]
            self.endRemoveRows()
            self.emitItemsCountChanged()
            return True
        return False

    def duplicateRow(self, row):
        if 0 <= row < len(self.dates):
            vCnt = len(self.dates)
            vIndex = QtCore.QModelIndex()
            self.beginInsertRows(vIndex, vCnt, vCnt)

            newDate = self.dates[row].addDays(1)
            self.dates.append(newDate)
            self.mealDays.append(self.emptyEventFeedRecord())
            self.surrogateEventFeedId -= 1
            newId = self.surrogateEventFeedId
            self.mealDays[-1].setValue('id', toVariant(newId))
            self.mealDays[-1].setValue('date', toVariant(newDate))
            self.mealDays[-1].setValue('diet_id', self.mealDays[row].value('diet_id'))
            self.mealDays[-1].setValue('courtingDiet_id', self.mealDays[row].value('courtingDiet_id'))
            self.items.setdefault(newId, {})

            oldId = forceInt(self.mealDays[row].value('id'))
            for mealTimeId, mealTimeList in self.items[oldId].items():
                for mealRecord in mealTimeList:
                    newMealRecord = self.emptyEventFeedMealRecord()
                    newMealRecord.setValue('master_id', toVariant(newId))
                    newMealRecord.setValue('mealTime_id', mealRecord.value('mealTime_id'))
                    newMealRecord.setValue('meal_id', mealRecord.value('meal_id'))
                    self.items.setdefault(newId, {}).setdefault(mealTimeId, []).append(newMealRecord)
            self.empty[row] = False  # is it really so?
            self.empty.append(False)

            self.endInsertRows()
            return True
        return False

    def emitItemsCountChanged(self):
        self.emit(QtCore.SIGNAL('itemsCountChanged(int)'), len(self.dates) if self.dates else 0)

    def emitCellChanged(self, row, column):
        index = self.index(row, column)
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)

    def emitRowsChanged(self, row1, row2):
        index1 = self.index(row1, 0)
        index2 = self.index(row2, self.columnCount())
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index1, index2)

    def emitColumnChanged(self, column):
        index1 = self.index(0, column)
        index2 = self.index(self.rowCount(), column)
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index1, index2)


class CMealListModel(QtCore.QAbstractTableModel):
    def __init__(self, parent):
        QAbstractTableModel.__init__(self, parent)
        self.mealRecordList = []
        self.editable = True

        db = QtGui.qApp.db
        tableRBMeal = db.table('rbMeal')
        records = db.getRecordList(tableRBMeal)
        self.mealMap = {}
        for record in records:
            mealId = forceInt(record.value('id'))
            mealName = forceString(record.value('name'))
            mealAmount = forceString(record.value('amount'))
            mealUnit = forceString(record.value('unit'))
            self.mealMap[mealId] = mealName + u', ' + mealAmount + u' ' + mealUnit

    def setEditable(self, value):
        self.editable = value

    def isEditable(self):
        return self.editable

    def items(self):
        return self.mealRecordList

    @staticmethod
    def getEmptyRecord():
        db = QtGui.qApp.db
        tableEventFeedMeal = db.table('Event_Feed_Meal')
        return tableEventFeedMeal.newRecord()

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return 1

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.mealRecordList) + 1

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(u'Наименование')
        return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        row = index.row()
        if 0 <= row < len(self.mealRecordList):
            mealId = forceRef(self.mealRecordList[row].value('meal_id'))
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.mealMap[mealId])
            elif role == QtCore.Qt.EditRole:
                return toVariant(mealId)
        return QtCore.QVariant()

    def loadItems(self, mealRecordList):
        self.mealRecordList = mealRecordList
        self.reset()

    def getItems(self):
        return self.mealRecordList

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            if value.isNull():
                return False
            mealId = forceRef(value)
            if mealId:
                row = index.row()
                if 0 <= row <= len(self.mealRecordList) and mealId in self.mealMap:
                    if row == len(self.mealRecordList):
                        mealRecord = self.getEmptyRecord()
                        mealRecord.setValue('meal_id', mealId)
                        self.mealRecordList.append(mealRecord)
                    else:
                        self.mealRecordList[row].setValue('meal_id', mealId)
                    self.reset()
                    return True
        return False

    def upRow(self, row):
        if 0 < row < len(self.mealRecordList):
            self.mealRecordList[row - 1], self.mealRecordList[row] = self.mealRecordList[row], self.mealRecordList[row - 1]
            self.emitRowsChanged(row - 1, row)
            return True
        else:
            return False

    def downRow(self, row):
        if 0 <= row < len(self.mealRecordList) - 1:
            self.mealRecordList[row + 1], self.mealRecordList[row] = self.mealRecordList[row], self.mealRecordList[row + 1]
            self.emitRowsChanged(row, row + 1)
            return True
        else:
            return False

    def removeRows(self, row, count, parentIndex=QtCore.QModelIndex(), *args, **kwargs):
        if 0 <= row and row + count <= len(self.mealRecordList):
            self.beginRemoveRows(parentIndex, row, row + count - 1)
            del self.mealRecordList[row:(row + count)]
            self.endRemoveRows()
            self.emitItemsCountChanged()
            return True
        else:
            return False

    def removeRow(self, row, parent=QtCore.QModelIndex(), *args, **kwargs):
        if 0 <= row < len(self.mealRecordList):
            self.beginRemoveRows(parent, row, row)
            del self.mealRecordList[row]
            self.endRemoveRows()
            self.emitItemsCountChanged()
            return True
        return False

    def emitItemsCountChanged(self):
        self.emit(QtCore.SIGNAL('itemsCountChanged(int)'), len(self.mealRecordList) if self.mealRecordList else 0)

    def emitRowsChanged(self, row1, row2):
        index1 = self.index(row1, 0)
        index2 = self.index(row2, self.columnCount())
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index1, index2)

    def flags(self, index):
        return super(CMealListModel, self).flags(index) | QtCore.Qt.ItemIsEditable


class CEventFeedMealListDialog(QtGui.QDialog, CConstructHelperMixin, Ui_EventFeedMealListDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)

        self.delegate = None
        self.setupUi(self)
        self.setModal(True)
        self.addModels('MealList', CMealListModel(self))
        self.tblMeals.setModel(self.modelMealList)

        self.tblMeals.setItemDelegate(CMealItemDelegate())
        self.tblMeals.addMoveRow()
        self.tblMeals.addPopupSelectAllRow()
        self.tblMeals.addPopupClearSelectionRow()
        self.tblMeals.addPopupDelRow()

    def setValue(self, value):
        mealRecordList = [variantItem.toPyObject() for variantItem in value.toList()]
        self.modelMealList.loadItems(mealRecordList)

    def value(self):
        return toVariant(self.modelMealList.getItems())

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Ok:
            self.accept()
        else:
            self.reject()


class CMealItemDelegate(QtGui.QItemDelegate):
    def __init__(self, parent=None):
        QtGui.QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        editor = CMealComboBox(parent)
        editor.setTable('rbMeal')
        return editor

    def setEditorData(self, editor, index):
        model = index.model()
        data = model.data(index, QtCore.Qt.EditRole)
        editor.setShowFields(editor.showFields)
        editor.setValue(forceRef(data))

    def setModelData(self, editor, model, index):
        model.setData(index, toVariant(editor.value()))


class CDietItemDelegate(QtGui.QItemDelegate):
    def __init__(self, parent=None):
        QtGui.QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        row = index.row()
        column = index.column()
        model = index.model()
        eventFeedId = forceInt(model.mealDays[row].value('id'))
        showAllDiets = True
        if column == 1 and eventFeedId in model.items:
            for mealList in model.items[eventFeedId].values():
                if len(mealList) != 0:
                    showAllDiets = False
                    break
        editor = CRBComboBox(parent)
        editor.setTable('rbDiet', addNone=True)
        if not showAllDiets:
            editor.setFilter('allow_meals = 1')
        return editor

    def setEditorData(self, editor, index):
        model = index.model()
        data = model.data(index, QtCore.Qt.EditRole)
        editor.setShowFields(editor.showFields)
        editor.setValue(forceRef(data))

    def setModelData(self, editor, model, index):
        model.setData(index, toVariant(editor.value()))


class CDateEditItemDelegate(QtGui.QItemDelegate):
    def __init__(self, parent=None):
        QtGui.QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        editor = CDateEdit(parent)
        return editor

    def setEditorData(self, editor, index):
        model = index.model()
        data = model.data(index, QtCore.Qt.EditRole)
        editor.setDate(forceDate(data))

    def setModelData(self, editor, model, index):
        model.setData(index, toVariant(editor.date()))


class CFeedInDocTableView(CInDocTableView):
    def __init__(self, parent):
        CInDocTableView.__init__(self, parent)
        self.dietItemDelegate = CDietItemDelegate(self)
        self.dateEditItemDelegate = CDateEditItemDelegate(self)
        self.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)

    @QtCore.pyqtSlot(QModelIndex, QModelIndex)
    def dataChanged(self, index1, index2):
        QtGui.QTableView.dataChanged(self, index1, index2)

    def on_popupMenu_aboutToShow(self):
        row = self.currentIndex().row()
        rowCount = self.model().rowCount()
        if self._CInDocTableView__actUpRow:
            self._CInDocTableView__actUpRow.setEnabled(0 < row < rowCount)
        if self._CInDocTableView__actDownRow:
            self._CInDocTableView__actDownRow.setEnabled(0 <= row < rowCount - 1)
        if self._CInDocTableView__actDeleteRows:
            rows = self.getSelectedRows()
            canDeleteRow = bool(rows)
            if canDeleteRow and self._CInDocTableView__delRowsChecker:
                canDeleteRow = self._CInDocTableView__delRowsChecker(rows)
            if len(rows) == 1 and rows[0] == row:
                self._CInDocTableView__actDeleteRows.setText(u'Удалить текущую строку')
            elif len(rows) == 1:
                self._CInDocTableView__actDeleteRows.setText(u'Удалить выделенную строку')
            else:
                self._CInDocTableView__actDeleteRows.setText(u'Удалить выделенные строки')
            self._CInDocTableView__actDeleteRows.setEnabled(canDeleteRow)
            if self._CInDocTableView__actDuplicateSelectRows:
                self._CInDocTableView__actDuplicateSelectRows.setEnabled(canDeleteRow)
        if self._CInDocTableView__actSelectAllRow:
            self._CInDocTableView__actSelectAllRow.setEnabled(0 <= row < rowCount)
        if self._CInDocTableView__actClearSelectionRow:
            rows = self.getSelectedRows()
            self._CInDocTableView__actClearSelectionRow.setEnabled(bool(rows))

    def getSelectedRows(self):
        rowCount = self.model().rowCount()
        rowSet = set([index.row() for index in self.selectedIndexes() if index.row() < rowCount])
        result = list(rowSet)
        result.sort()
        return result

    def on_deleteRows(self):
        rows = self.getSelectedRows()
        rows.sort(reverse=True)
        for row in rows:
            self.model().removeRow(row)

    def on_duplicateCurrentRow(self):
        currentRow = self.currentIndex().row()
        self.model().duplicateRow(currentRow)
        self.model().reset()

    def on_duplicateSelectRows(self):
        selectIndexes = self.selectedIndexes()
        selectRowList = []
        for selectIndex in selectIndexes:
            selectRow = selectIndex.row()
            if selectRow not in selectRowList:
                selectRowList.append(selectRow)
        selectRowList.sort()
        for row in selectRowList:
            self.model().duplicateRow(row)
        self.model().reset()

    def colKey(self, col):
        pass

    def resetSorting(self):
        pass

    def loadPreferences(self, preferences):
        pass

    def savePreferences(self):
        preferences = {}
        return preferences

    def addContentToTextCursor(self, cursor):
        pass
