#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Blank.BlankItemsListDialog import CActionBlankModel, CBlankModel
from Orgs.PersonComboBoxEx import CPersonFindInDocTableCol
from RefBooks.Person import COrgStructureInDocTableCol
from Ui_BlanksDialog import Ui_BlanksDialog
from library.DialogBase import CDialogBase
from library.InDocTable import CDateInDocTableCol, CInDocTableCol, CInDocTableModel, CIntInDocTableCol, CRBInDocTableCol
from library.Utils import forceInt, forceRef, forceString, toVariant, variantEq
from library.crbcombobox import CRBComboBox


class CBlanksDialog(CDialogBase, Ui_BlanksDialog):
    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        self.addModels('BlankTypeTempInvalid', CBlankModel(self))
        self.addModels('BlankTypeActions', CActionBlankModel(self))
        self.addModels('BlankTempInvalidParty', CBlankTempInvalidPartyModel(self))
        self.addModels('BlankTempInvalidMoving', CBlankTempInvalidMovingModel(self))
        self.addModels('BlankActionsParty', CBlankActionsPartyModel(self))
        self.addModels('BlankActionsMoving', CBlankActionsMovingModel(self))
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setModels(self.treeBlankTypeTempInvalid, self.modelBlankTypeTempInvalid, self.selectionModelBlankTypeTempInvalid)
        self.setModels(self.treeBlankTypeActions, self.modelBlankTypeActions, self.selectionModelBlankTypeActions)
        self.setModels(self.tblBlankTempInvalidParty,  self.modelBlankTempInvalidParty, self.selectionModelBlankTempInvalidParty)
        self.setModels(self.tblBlankTempInvalidMoving,  self.modelBlankTempInvalidMoving, self.selectionModelBlankTempInvalidMoving)
        self.setModels(self.tblBlankActionsParty,  self.modelBlankActionsParty, self.selectionModelBlankActionsParty)
        self.setModels(self.tblBlankActionsMoving,  self.modelBlankActionsMoving, self.selectionModelBlankActionsMoving)
        self.tblBlankTempInvalidParty.addPopupDelRow()
        self.tblBlankTempInvalidMoving.addPopupDelRow()
        self.tblBlankActionsParty.addPopupDelRow()
        self.tblBlankActionsMoving.addPopupDelRow()
        self.treeBlankTypeTempInvalid.header().hide()
        self.treeBlankTypeActions.header().hide()
        self.resetFilterTempInvalid()
        self.resetFilterActions()
        self.treeBlankTypeTempInvalid.expand(self.modelBlankTypeTempInvalid.index(0, 0))
        self.treeBlankTypeTempInvalid.setCurrentIndex(self.modelBlankTypeTempInvalid.index(0, 0))

    @QtCore.pyqtSlot(int)
    def on_tabWidget_currentChanged(self, widgetIndex):
        if widgetIndex == 0:
            self.treeBlankTypeTempInvalid.expand(self.modelBlankTypeTempInvalid.index(0, 0))
            self.treeBlankTypeTempInvalid.setCurrentIndex(self.modelBlankTypeTempInvalid.index(0, 0))
        else:
            self.treeBlankTypeActions.expand(self.modelBlankTypeActions.index(0, 0))
            self.treeBlankTypeActions.setCurrentIndex(self.modelBlankTypeActions.index(0, 0))

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelBlankTypeTempInvalid_currentChanged(self, current, previous):
        QtGui.qApp.callWithWaitCursor(self, self.saveItemsPrevious, self.tblBlankTempInvalidParty.currentIndex(), self.modelBlankTempInvalidParty, self.modelBlankTempInvalidMoving)
        treeDocTypeIdList = self.getTempInvalidDocTypeId()
        if treeDocTypeIdList:
            self.modelBlankTempInvalidParty.cols()[0].setFilter(treeDocTypeIdList)
        db = QtGui.qApp.db
        tableRBBlankTempInvalids = db.table('rbBlankTempInvalids')
        tableBlankTempInvalidParty = db.table('BlankTempInvalid_Party')
        table = tableBlankTempInvalidParty.innerJoin(tableRBBlankTempInvalids, tableBlankTempInvalidParty['doctype_id'].eq(tableRBBlankTempInvalids['id']))
        doctypeIdList = db.getDistinctIdList(table, [tableBlankTempInvalidParty['id']], [tableRBBlankTempInvalids['doctype_id'].inlist(treeDocTypeIdList), tableBlankTempInvalidParty['deleted'].eq(0)])
        filterParty, filterMoving = self.getFilterTempInvalidParams()
        self.modelBlankTempInvalidParty.loadPartyItems(doctypeIdList, filterParty)
        self.tblBlankTempInvalidParty.setFocus(QtCore.Qt.TabFocusReason)
        self.setItemsBlankTempInvalidMoving(filterMoving)

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelBlankTempInvalidParty_currentChanged(self, current, previous):
        QtGui.qApp.callWithWaitCursor(self, self.saveItemsPrevious, previous, self.modelBlankTempInvalidParty, self.modelBlankTempInvalidMoving)
        filterParty, filterMoving = self.getFilterTempInvalidParams()
        QtGui.qApp.callWithWaitCursor(self, self.setItemsBlankTempInvalidMoving, filterMoving)

    def setItemsBlankTempInvalidMoving(self, filterMoving):
        blankPartyId = self.getBlankPartyId(self.tblBlankTempInvalidParty, self.modelBlankTempInvalidParty)
        self.modelBlankTempInvalidMoving.loadSubPartyItems(blankPartyId, filterMoving)

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelBlankTypeActions_currentChanged(self, current, previous):
        QtGui.qApp.callWithWaitCursor(self, self.saveItemsPrevious, self.tblBlankActionsParty.currentIndex(), self.modelBlankActionsParty, self.modelBlankActionsMoving)
        treeDocTypeIdList = self.getActionsDocTypeId()
        if treeDocTypeIdList:
            self.modelBlankActionsParty.cols()[0].setFilter(treeDocTypeIdList)
        db = QtGui.qApp.db
        tableRBBlankActions = db.table('rbBlankActions')
        tableBlankActionsParty = db.table('BlankActions_Party')
        table = tableBlankActionsParty.innerJoin(tableRBBlankActions, tableBlankActionsParty['doctype_id'].eq(tableRBBlankActions['id']))
        doctypeIdList = db.getDistinctIdList(table, [tableBlankActionsParty['id']], [tableRBBlankActions['doctype_id'].inlist(treeDocTypeIdList), tableBlankActionsParty['deleted'].eq(0)])
        filterParty, filterMoving = self.getFilterActionsParams()
        self.modelBlankActionsParty.loadPartyItems(doctypeIdList, filterParty)
        self.tblBlankActionsParty.setFocus(QtCore.Qt.TabFocusReason)
        self.setItemsBlankActionsMoving(filterMoving)

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelBlankActionsParty_currentChanged(self, current, previous):
        QtGui.qApp.callWithWaitCursor(self, self.saveItemsPrevious, previous, self.modelBlankActionsParty, self.modelBlankActionsMoving)
        filterParty, filterMoving = self.getFilterActionsParams()
        self.setItemsBlankActionsMoving(filterMoving)

    def setItemsBlankActionsMoving(self, filterMoving):
        blankPartyId = self.getBlankPartyId(self.tblBlankActionsParty, self.modelBlankActionsParty)
        self.modelBlankActionsMoving.loadSubPartyItems(blankPartyId, filterMoving)

    def saveItemsPrevious(self, previous, modelParty, modelMoving):
        if previous.isValid():
            modelParty.savePartyItems()
            previousRow = previous.row()
            items = modelParty.items()
            if len(items) > previousRow:
                record = items[previousRow]
                previousBlankPartyId = forceRef(record.value('id'))
                if previousBlankPartyId:
                    modelMoving.saveItems(previousBlankPartyId)

    def updateTempInvalidBlankParty(self):
        received = 0
        used = 0
        returnAmount = 0
        for item in self.modelBlankTempInvalidMoving.items():
            received += forceInt(item.value('received'))
            used += forceInt(item.value('used'))
            returnAmount += forceInt(item.value('returnAmount'))
        currentIndex = self.tblBlankTempInvalidParty.currentIndex()
        if currentIndex.isValid():
            currentRow = currentIndex.row()
            blankPartyId = self.getBlankPartyId(self.tblBlankTempInvalidParty, self.modelBlankTempInvalidParty)
            itemsParty = self.modelBlankTempInvalidParty.items()
            record = itemsParty[currentRow]
            amountBlank = forceInt(record.value('amount'))
            writingBlank = forceInt(record.value('writing'))
            record.setValue('extradited', toVariant(received))
            record.setValue('used', toVariant(used))
            record.setValue('returnBlank', toVariant(returnAmount))
            record.setValue('balance', toVariant(amountBlank - received - writingBlank + returnAmount))
            itemsParty[currentRow] = record
            self.modelBlankTempInvalidParty.setItems(itemsParty)
            self.modelBlankTempInvalidParty.emitRowChanged(currentRow)

    def updateActionsBlankParty(self):
        received = 0
        used = 0
        returnAmount = 0
        for item in self.modelBlankActionsMoving.items():
            received += forceInt(item.value('received'))
            used += forceInt(item.value('used'))
            returnAmount += forceInt(item.value('returnAmount'))
        currentIndex = self.tblBlankActionsParty.currentIndex()
        if currentIndex.isValid():
            currentRow = currentIndex.row()
            blankPartyId = self.getBlankPartyId(self.tblBlankActionsParty, self.modelBlankActionsParty)
            itemsParty = self.modelBlankActionsParty.items()
            record = itemsParty[currentRow]
            amountBlank = forceInt(record.value('amount'))
            writingBlank = forceInt(record.value('writing'))
            record.setValue('extradited', toVariant(received))
            record.setValue('used', toVariant(used))
            record.setValue('returnBlank', toVariant(returnAmount))
            record.setValue('balance', toVariant(amountBlank - received -writingBlank + returnAmount))
            itemsParty[currentRow] = record
            self.modelBlankActionsParty.setItems(itemsParty)
            self.modelBlankActionsParty.emitRowChanged(currentRow)

    def getTempInvalidDocTypeId(self):
        return self.modelBlankTypeTempInvalid.getItemIdList(self.treeBlankTypeTempInvalid.currentIndex())

    def getActionsDocTypeId(self):
        return self.modelBlankTypeActions.getItemIdList(self.treeBlankTypeActions.currentIndex())

    def getBlankPartyId(self, table, model):
        currentIndex = table.currentIndex()
        if currentIndex.isValid():
            currentRow = currentIndex.row()
            items = model.items()
            if len(items) > currentRow:
                record = items[currentRow]
                blankPartyId = forceRef(record.value('id'))
                return blankPartyId
        return None

    def saveData(self):
        if not self.checkIntervalNumbers(self.tblBlankTempInvalidParty, self.tblBlankTempInvalidMoving, self.modelBlankTempInvalidParty, self.modelBlankTempInvalidMoving):
            return False
        if not self.checkIntervalNumbers(self.tblBlankActionsParty, self.tblBlankActionsMoving, self.modelBlankActionsParty, self.modelBlankActionsMoving):
            return False
        QtGui.qApp.callWithWaitCursor(self, self.saveBlankTempInvalid)
        QtGui.qApp.callWithWaitCursor(self, self.saveBlankActions)
        return True

    def saveBlankTempInvalid(self):
        self.modelBlankTempInvalidParty.savePartyItems()
        blankPartyId = self.getBlankPartyId(self.tblBlankTempInvalidParty, self.modelBlankTempInvalidParty)
        if blankPartyId:
            self.modelBlankTempInvalidMoving.saveItems(blankPartyId)

    def saveBlankActions(self):
        self.modelBlankActionsParty.savePartyItems()
        blankPartyId = self.getBlankPartyId(self.tblBlankActionsParty, self.modelBlankActionsParty)
        if blankPartyId:
            self.modelBlankActionsMoving.saveItems(blankPartyId)

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBoxFilter_clicked(self, button):
        buttonCode = self.buttonBoxFilter.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.applyFilterTempInvalid()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.resetFilterTempInvalid()

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBoxFilterActions_clicked(self, button):
        buttonCode = self.buttonBoxFilterActions.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.applyFilterActions()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.resetFilterActions()

    def getFilterTempInvalidParams(self):
        filterParty = []
        filterMoving = []
        db = QtGui.qApp.db
        table = db.table('BlankTempInvalid_Party')
        tableMoving = db.table('BlankTempInvalid_Moving')
        personId = self.cmbPersonParty.value()
        if personId:
            filterParty.append(table['person_id'].eq(personId))
        begDate = self.edtBegDateParty.date()
        if begDate:
            filterParty.append(table['date'].ge(begDate))
        endDate = self.edtEndDateParty.date()
        if endDate:
            filterParty.append(table['date'].le(endDate))
        serial = self.edtSerialParty.text()
        if serial:
            filterParty.append(table['serial'].eq(serial))
        numberTo = self.edtNumberTo.value()
        if numberTo:
            numberFrom = self.edtNumberFrom.value()
            filterParty.append(db.joinAnd([table['numberFrom'].ge(numberFrom),
                                           table['numberTo'].le(numberTo)]))
        orgStructureId = self.cmbOrgStructureSubParty.value()
        if orgStructureId:
            filterMoving.append(tableMoving['orgStructure_id'].eq(orgStructureId))
        personId = self.cmbPersonSubParty.value()
        if personId:
            filterMoving.append(tableMoving['person_id'].eq(personId))
        begDate = self.edtBegDateSubParty.date()
        if begDate:
            filterMoving.append(tableMoving['date'].ge(begDate))
        endDate = self.edtEndDateSubParty.date()
        if endDate:
            filterMoving.append(tableMoving['date'].le(endDate))
        return filterParty, filterMoving

    def getFilterActionsParams(self):
        filterParty = []
        filterMoving = []
        db = QtGui.qApp.db
        table = db.table('BlankActions_Party')
        tableMoving = db.table('BlankActions_Moving')
        personId = self.cmbPersonPartyActions.value()
        if personId:
            filterParty.append(table['person_id'].eq(personId))
        begDate = self.edtBegDatePartyActions.date()
        if begDate:
            filterParty.append(table['date'].ge(begDate))
        endDate = self.edtEndDatePartyActions.date()
        if endDate:
            filterParty.append(table['date'].le(endDate))
        serial = self.edtSerialPartyActions.text()
        if serial:
            filterParty.append(table['serial'].eq(serial))
        numberTo = self.edtNumberToActions.value()
        if numberTo:
            numberFrom = self.edtNumberFromActions.value()
            filterParty.append(db.joinAnd([table['numberFrom'].ge(numberFrom),
                                           table['numberTo'].le(numberTo)]))
        orgStructureId = self.cmbOrgStructureSubPartyActions.value()
        if orgStructureId:
            filterMoving.append(tableMoving['orgStructure_id'].eq(orgStructureId))
        personId = self.cmbPersonSubPartyActions.value()
        if personId:
            filterMoving.append(tableMoving['person_id'].eq(personId))
        begDate = self.edtBegDateSubPartyActions.date()
        if begDate:
            filterMoving.append(tableMoving['date'].ge(begDate))
        endDate = self.edtEndDateSubPartyActions.date()
        if endDate:
            filterMoving.append(tableMoving['date'].le(endDate))
        return filterParty, filterMoving

    def applyFilterTempInvalid(self):
        self.on_selectionModelBlankTypeTempInvalid_currentChanged(QtCore.QModelIndex(), QtCore.QModelIndex())

    def applyFilterActions(self):
        self.on_selectionModelBlankTypeActions_currentChanged(QtCore.QModelIndex(), QtCore.QModelIndex())

    def resetFilterTempInvalid(self):
        self.cmbPersonParty.setValue(None)
        self.edtBegDateParty.setDate(QtCore.QDate.currentDate())
        self.edtEndDateParty.setDate(QtCore.QDate.currentDate())
        self.edtSerialParty.setText(u'')
        self.edtNumberTo.setValue(0)
        self.edtNumberFrom.setValue(0)
        self.cmbOrgStructureSubParty.setValue(None)
        self.cmbPersonSubParty.setValue(None)
        self.edtBegDateSubParty.setDate(QtCore.QDate.currentDate())
        self.edtEndDateSubParty.setDate(QtCore.QDate.currentDate())
        self.applyFilterTempInvalid()

    def resetFilterActions(self):
        self.cmbPersonPartyActions.setValue(None)
        self.edtBegDatePartyActions.setDate(QtCore.QDate.currentDate())
        self.edtEndDatePartyActions.setDate(QtCore.QDate.currentDate())
        self.edtSerialPartyActions.setText(u'')
        self.edtNumberToActions.setValue(0)
        self.edtNumberFromActions.setValue(0)
        self.cmbOrgStructureSubPartyActions.setValue(None)
        self.cmbPersonSubPartyActions.setValue(None)
        self.edtBegDateSubPartyActions.setDate(QtCore.QDate.currentDate())
        self.edtEndDateSubPartyActions.setDate(QtCore.QDate.currentDate())
        self.applyFilterActions()

    def checkIntervalNumbers(self, table, tableMoving, model, modelMoving):
        for rowItem, record in enumerate(modelMoving.items()):
            if record:
                numberFrom = forceInt(record.value('numberFrom'))
                numberTo = forceInt(record.value('numberTo'))
                if not self.checkIntervalNumber(numberFrom, rowItem, record.indexOf('numberFrom'), table, tableMoving, model):
                    return False
                if not self.checkIntervalNumber(numberTo, rowItem, record.indexOf('numberTo'), table, tableMoving, model):
                    return False
        return True

    def checkIntervalNumber(self, number, rowItem, column, table, tableMoving, model):
        currentIndex = table.currentIndex()
        if currentIndex.isValid():
            currentRow = currentIndex.row()
            blankPartyId = self.getBlankPartyId(table, model)
            itemsParty = model.items()
            if itemsParty and len(itemsParty) < currentRow:
                record = itemsParty[currentRow]
                if record:
                    numberFrom = forceInt(record.value('numberFrom'))
                    numberTo = forceInt(record.value('numberTo'))
                    if not number or number < numberFrom or number > numberTo:
                        return self.checkValueMessage(u'Номер %s не попадает в диапазон %s-%s'% (forceString(number), forceString(numberFrom), forceString(numberTo)), False, tableMoving, rowItem, column)
        return True

    def checkDoubleNumber(self, number, row, column, table, model):
        if number:
            for rowItem, record in enumerate(model.items()):
                if rowItem != row and record:
                    numberFrom = forceInt(record.value('numberFrom'))
                    numberTo = forceInt(record.value('numberTo'))
                    if not number or number == numberFrom or number == numberTo:
                        return self.checkValueMessage(u'Номер %s дублируется'% (forceString(number)), False, table, row, column)
        return True

    def checkReturnBlank(self, row, column, table, model):
        items = model.items()
        record = items[row]
        if record:
            returnAmount = forceInt(record.value('returnAmount'))
            if returnAmount:
                self.checkValueMessage(u'Из подпартии был возврат', False, table, row, column)


class CAmountIntInDocTableCol(CIntInDocTableCol):
    def __init__(self, title, fieldName, width, **params):
        CIntInDocTableCol.__init__(self, title, fieldName, width, **params)
        self.low = params.get('low', 0)
        self.high = params.get('high', 10000)


class CRBInvalDocTypeInDocTableCol(CRBInDocTableCol):
    def setFilter(self, doctypeIdList):
        self.filter = u'rbBlankTempInvalids.doctype_id IN (%s)'%(','.join(str(doctypeId) for doctypeId in doctypeIdList))


class CRBActionDocTypeInDocTableCol(CRBInDocTableCol):
    def setFilter(self, doctypeIdList):
        self.filter = u'rbBlankActions.doctype_id IN (%s)'%(','.join(str(doctypeId) for doctypeId in doctypeIdList))


class CBlankPartyInDocTableModel(CInDocTableModel):
    def removeRows(self, row, count, parentIndex = QtCore.QModelIndex()):
        if 0 <= row <= len(self._items) - count:
            self.beginRemoveRows(parentIndex, row, row + count - 1)
            item = self._items[row]
            self.deletedIdList.append(forceRef(item.value('id')))
            del self._items[row:row+count]
            self.endRemoveRows()
            return True
        else:
            return False

    def savePartyItems(self):
        if self._items is not None:
            db = QtGui.qApp.db
            table = self._table
            idFieldName = self._idFieldName
            for idx, record in enumerate(self._items):
                if self._idxFieldName:
                    record.setValue(self._idxFieldName, toVariant(idx))
                if self._extColsPresent:
                    outRecord = self.removeExtCols(record)
                else:
                    outRecord = record
                id = db.insertOrUpdate(table, outRecord)
                record.setValue(idFieldName, toVariant(id))
            if self.deletedIdList:
                filter = [table[idFieldName].inlist(self.deletedIdList)]
                if self._filter:
                    filter.append(self._filter)
                if table.hasField('deleted'):
                    db.markRecordsDeleted(table, filter)

    def loadPartyItems(self, masterIdList, filter=None):
        if not filter:
            filter = []
        db = QtGui.qApp.db
        cols = []
        for col in self._cols:
            if not col.external():
                cols.append(col.fieldName())
        cols.append(self._idFieldName)
        if self._idxFieldName:
            cols.append(self._idxFieldName)
        for col in self._hiddenCols:
            cols.append(col)
        table = self._table
        filter.append(table[self._idFieldName].inlist(masterIdList))
        if self._filter:
            filter.append(self._filter)
        if table.hasField('deleted'):
            filter.append(table['deleted'].eq(0))
        if self._idxFieldName:
            order = [self._idxFieldName, self._idFieldName]
        else:
            order = [self._idFieldName]
        self._items = db.getRecordList(table, cols, filter, order)
        self.reset()


class CBlankMovingInDocTableModel(CInDocTableModel):
    def removeRows(self, row, count, parentIndex = QtCore.QModelIndex()):
        if 0 <= row <= len(self._items) - count:
            self.beginRemoveRows(parentIndex, row, row+count-1)
            item = self._items[row]
            self.deletedIdList.append(forceRef(item.value('id')))
            del self._items[row:row+count]
            self.endRemoveRows()
            return True
        else:
            return False

    def saveItems(self, masterId):
        if self._items is not None:
            db = QtGui.qApp.db
            table = self._table
            masterId = toVariant(masterId)
            masterIdFieldName = self._masterIdFieldName
            idFieldName = self._idFieldName
            for idx, record in enumerate(self._items):
                record.setValue(masterIdFieldName, masterId)
                if self._idxFieldName:
                    record.setValue(self._idxFieldName, toVariant(idx))
                if self._extColsPresent:
                    outRecord = self.removeExtCols(record)
                else:
                    outRecord = record
                id = db.insertOrUpdate(table, outRecord)
                record.setValue(idFieldName, toVariant(id))
            if self.deletedIdList:
                filter = [table[masterIdFieldName].eq(masterId),
                          table[idFieldName].inlist(self.deletedIdList)]
                if self._filter:
                    filter.append(self._filter)
                if table.hasField('deleted'):
                    db.markRecordsDeleted(table, filter)

    def loadSubPartyItems(self, masterId, filter=None):
        if not filter:
            filter = []
        db = QtGui.qApp.db
        cols = []
        for col in self._cols:
            if not col.external():
                cols.append(col.fieldName())
        cols.append(self._idFieldName)
        cols.append(self._masterIdFieldName)
        if self._idxFieldName:
            cols.append(self._idxFieldName)
        for col in self._hiddenCols:
            cols.append(col)
        table = self._table
        filter.append(table[self._masterIdFieldName].eq(masterId))
        if self._filter:
            filter.append(self._filter)
        if table.hasField('deleted'):
            filter.append(table['deleted'].eq(0))
        if self._idxFieldName:
            order = [self._idxFieldName, self._idFieldName]
        else:
            order = [self._idFieldName]
        self._items = db.getRecordList(table, cols, filter, order)
        self.reset()


class CBlankTempInvalidPartyModel(CBlankPartyInDocTableModel):
    def __init__(self, parent):
        CBlankPartyInDocTableModel.__init__(self, 'BlankTempInvalid_Party', 'id', 'doctype_id', parent)
        self.addCol(CRBInvalDocTypeInDocTableCol(u'Тип', 'doctype_id', 10, 'rbBlankTempInvalids', addNone=False, showFields=CRBComboBox.showCodeAndName))
        self.addCol(CDateInDocTableCol(u'Дата', 'date', 20))
        self.addCol(CPersonFindInDocTableCol(u'Получатель', 'person_id',  20, 'vrbPersonWithSpeciality', parent=parent))
        self.addCol(CInDocTableCol(u'Серия', 'serial', 10))
        self.addCol(CInDocTableCol(u'Номер с', 'numberFrom', 10))
        self.addCol(CInDocTableCol(u'Номер по', 'numberTo', 10))
        self.addCol(CAmountIntInDocTableCol(u'Исходное количество', 'amount', 10))
        self.addCol(CAmountIntInDocTableCol(u'Выдано', 'extradited', 10)).setReadOnly(True)
        self.addCol(CAmountIntInDocTableCol(u'Списано', 'writing', 10))
        self.addCol(CAmountIntInDocTableCol(u'Возврат', 'returnBlank', 10)).setReadOnly(True)
        self.addCol(CAmountIntInDocTableCol(u'Остаток', 'balance', 10)).setReadOnly(True)
        self.addCol(CAmountIntInDocTableCol(u'Использовано', 'used', 10)).setReadOnly(True)
        self.deletedIdList = []


class CBlankTempInvalidMovingModel(CBlankMovingInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'BlankTempInvalid_Moving', 'id', 'blankParty_id', parent)
        self.addCol(CDateInDocTableCol(u'Дата', 'date', 20))
        self.addCol(CInDocTableCol(u'Номер с', 'numberFrom', 10))
        self.addCol(CInDocTableCol(u'Номер по', 'numberTo', 10))
        self.addCol(COrgStructureInDocTableCol(u'Подразделение',  'orgStructure_id',  15))
        self.addCol(CPersonFindInDocTableCol(u'Получил', 'person_id',  20, 'vrbPersonWithSpeciality', parent=parent))
        self.addCol(CAmountIntInDocTableCol(u'Получено', 'received', 10))
        self.addCol(CAmountIntInDocTableCol(u'Использовано', 'used', 10))
        self.addCol(CDateInDocTableCol(u'Дата возврата', 'returnDate', 20, canBeEmpty=True))
        self.addCol(CAmountIntInDocTableCol(u'Возвращено', 'returnAmount', 10))
        self.deletedIdList = []

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        column = index.column()
        row = index.row()
        if not variantEq(self.data(index, role), value):
            if column == 1:
                QtCore.QObject.parent(self).checkReturnBlank(row, column, QtCore.QObject.parent(self).tblBlankTempInvalidMoving, self)
                QtCore.QObject.parent(self).checkDoubleNumber(forceInt(value), row, column, QtCore.QObject.parent(self).tblBlankTempInvalidMoving, self)
                return CInDocTableModel.setData(self, index, value, role)
            elif column == 2:
                QtCore.QObject.parent(self).checkReturnBlank(row, column, QtCore.QObject.parent(self).tblBlankTempInvalidMoving, self)
                QtCore.QObject.parent(self).checkDoubleNumber(forceInt(value), row, column, QtCore.QObject.parent(self).tblBlankTempInvalidMoving, self)
                return CInDocTableModel.setData(self, index, value, role)
            elif column == 3:
                self._cols[4].orgStructureId = forceRef(value)
                return CInDocTableModel.setData(self, index, value, role)
            elif column == 5:
                QtCore.QObject.parent(self).checkReturnBlank(row, column, QtCore.QObject.parent(self).tblBlankTempInvalidMoving, self)
                result = CInDocTableModel.setData(self, index, value, role)
                if result:
                    QtCore.QObject.parent(self).updateTempInvalidBlankParty()
                return result
            elif column == 6:
                QtCore.QObject.parent(self).checkReturnBlank(row, column, QtCore.QObject.parent(self).tblBlankTempInvalidMoving, self)
                result = CInDocTableModel.setData(self, index, value, role)
                if result:
                    QtCore.QObject.parent(self).updateTempInvalidBlankParty()
                return result
            elif column == 8:
                QtCore.QObject.parent(self).checkReturnBlank(row, column, QtCore.QObject.parent(self).tblBlankTempInvalidMoving, self)
                result = CInDocTableModel.setData(self, index, value, role)
                if result:
                    QtCore.QObject.parent(self).updateTempInvalidBlankParty()
                return result
            return CInDocTableModel.setData(self, index, value, role)
        else:
            return True


class CBlankActionsPartyModel(CBlankPartyInDocTableModel):
    def __init__(self, parent):
        CBlankPartyInDocTableModel.__init__(self, 'BlankActions_Party', 'id', 'doctype_id', parent)
        self.addCol(CRBActionDocTypeInDocTableCol(u'Тип', 'doctype_id', 10, 'rbBlankActions', addNone=False, showFields=CRBComboBox.showCodeAndName))
        self.addCol(CDateInDocTableCol(u'Дата', 'date', 20))
        self.addCol(CPersonFindInDocTableCol(u'Получатель', 'person_id',  20, 'vrbPersonWithSpeciality', parent=parent))
        self.addCol(CInDocTableCol(u'Серия', 'serial', 10))
        self.addCol(CInDocTableCol(u'Номер с', 'numberFrom', 10))
        self.addCol(CInDocTableCol(u'Номер по', 'numberTo', 10))
        self.addCol(CAmountIntInDocTableCol(u'Исходное количество', 'amount', 10))
        self.addCol(CAmountIntInDocTableCol(u'Выдано', 'extradited', 10)).setReadOnly(True)
        self.addCol(CAmountIntInDocTableCol(u'Списано', 'writing', 10))
        self.addCol(CAmountIntInDocTableCol(u'Возврат', 'returnBlank', 10)).setReadOnly(True)
        self.addCol(CAmountIntInDocTableCol(u'Остаток', 'balance', 10)).setReadOnly(True)
        self.addCol(CAmountIntInDocTableCol(u'Использовано', 'used', 10)).setReadOnly(True)
        self.deletedIdList = []


class CBlankActionsMovingModel(CBlankMovingInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'BlankActions_Moving', 'id', 'blankParty_id', parent)
        self.addCol(CDateInDocTableCol(u'Дата', 'date', 20))
        self.addCol(CInDocTableCol(u'Номер с', 'numberFrom', 10))
        self.addCol(CInDocTableCol(u'Номер по', 'numberTo', 10))
        self.addCol(COrgStructureInDocTableCol(u'Получатель подразделение',  'orgStructure_id',  15))
        self.addCol(CPersonFindInDocTableCol(u'Получатель персона', 'person_id',  20, 'vrbPersonWithSpeciality', parent=parent))
        self.addCol(CAmountIntInDocTableCol(u'Получено', 'received', 10))
        self.addCol(CAmountIntInDocTableCol(u'Использовано', 'used', 10))
        self.addCol(CDateInDocTableCol(u'Возврат дата', 'returnDate', 20))
        self.addCol(CAmountIntInDocTableCol(u'Возврат количество', 'returnAmount', 10))
        self.deletedIdList = []

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        column = index.column()
        row = index.row()
        if not variantEq(self.data(index, role), value):
            if column == 1:
                QtCore.QObject.parent(self).checkReturnBlank(row, column, QtCore.QObject.parent(self).tblBlankActionsMoving, self)
                result = CInDocTableModel.setData(self, index, value, role)
                QtCore.QObject.parent(self).checkDoubleNumber(forceInt(value), row, column, QtCore.QObject.parent(self).tblBlankActionsMoving, self)
                return CInDocTableModel.setData(self, index, value, role)

            elif column == 2:
                QtCore.QObject.parent(self).checkReturnBlank(row, column, QtCore.QObject.parent(self).tblBlankActionsMoving, self)
                result = CInDocTableModel.setData(self, index, value, role)
                QtCore.QObject.parent(self).checkDoubleNumber(forceInt(value), row, column, QtCore.QObject.parent(self).tblBlankActionsMoving, self)
                return CInDocTableModel.setData(self, index, value, role)

            elif column == 3:
                self._cols[4].orgStructureId = forceRef(value)
                return CInDocTableModel.setData(self, index, value, role)

            elif column == 5:
                QtCore.QObject.parent(self).checkReturnBlank(row, column, QtCore.QObject.parent(self).tblBlankActionsMoving, self)
                result = CInDocTableModel.setData(self, index, value, role)
                result = CInDocTableModel.setData(self, index, value, role)
                if result:
                    QtCore.QObject.parent(self).updateActionsBlankParty()
                return result

            elif column == 6:
                QtCore.QObject.parent(self).checkReturnBlank(row, column, QtCore.QObject.parent(self).tblBlankActionsMoving, self)
                result = CInDocTableModel.setData(self, index, value, role)
                result = CInDocTableModel.setData(self, index, value, role)
                if result:
                    QtCore.QObject.parent(self).updateActionsBlankParty()
                return result

            elif column == 8:
                QtCore.QObject.parent(self).checkReturnBlank(row, column, QtCore.QObject.parent(self).tblBlankActionsMoving, self)
                result = CInDocTableModel.setData(self, index, value, role)
                if result:
                    QtCore.QObject.parent(self).updateActionsBlankParty()
                return result

            return CInDocTableModel.setData(self, index, value, role)

        return True
