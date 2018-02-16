# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

from library.InDocTable                  import CInDocTableView
from models.RCTableModel                 import CRCLocItemDelegate, CRCLocItemFieldDelegate

class CInDocTableViewModifyPopup(CInDocTableView):
    def addPopupAction(self, action):
        self.popupMenu().addAction(action)

    def initPopupAction(self, act, objectName, actName, slot):
        act = QtGui.QAction(actName, self)
        act.setObjectName(objectName)
        self.connect(act, QtCore.SIGNAL('triggered()'), slot)
        self.addPopupAction(act)
        return act



class CRCTableFieldsView(CInDocTableViewModifyPopup):
    def __init__(self, parent):
        CInDocTableView.__init__(self, parent)
        self.setItemDelegate(CRCLocItemFieldDelegate(self))
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self._actDelete = None
        self._actEdit = None

        self.addPopupDeleteCol()

    def setColSize(self):
        self.horizontalHeader().setStretchLastSection(False)
        self.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)

    def addPopupDeleteCol(self):
        self._actDelete = self.initPopupAction(self._actDelete, 'actDelete', u'Удалить', self.on_actDelete_triggered)

    def addPopupEdit(self):
        self._actEdit = self.initPopupAction(self._actEdit, 'actEdit', u'Изменить', self.on_actEdit_triggered)

    def on_actDelete_triggered(self):
        row = self.currentIndex().row()
        self.model().deleteItem(row)

    def on_actEdit_triggered(self):
        self.model().setExtededEditMode(self.curretIndex.row())

class CRCTableParamsView(CInDocTableViewModifyPopup):
    def __init__(self, parent):
        CInDocTableView.__init__(self, parent)
        self._actDelete = None

        self.addPopupDeleteCol()

    def addPopupDeleteCol(self):
        self._actDelete = self.initPopupAction(self._actDelete, 'actDelete', u'Удалить', self.on_actDelete_triggered)

    def on_actDelete_triggered(self):
        row = self.currentIndex().row()
        self.model().deleteItem(row)

class CRCTableCapView(CInDocTableViewModifyPopup):
    def __init__(self, parent):
        CInDocTableView.__init__(self, parent)
        self.setItemDelegate(CRCLocItemDelegate(self))
        self.buffer = []
        self.verticalHeader().show()
        self.verticalHeader().setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.horizontalHeader().setSelectionBehavior(QtGui.QAbstractItemView.SelectColumns)
        self.horizontalHeader().setSortIndicatorShown(False)
        self.horizontalHeader().setStretchLastSection(False)

        self._actAddColBeforeCurrent = None
        self._actAddColAfterCurrent = None
        self._actDeleteCol = None
        self._actAddRowBeforeCurrent = None
        self._actAddRowAfterCurrent = None
        self._actDeleteRow = None
        self._actSpan = None
        self._actClearCurrentSpan = None
        self._actAddGroupRow = None
        self._actDeleteGroupRow = None

        self.addPopupAddColBeforeCurrent()
        self.addPopupAddColAfterCurrent()
        self.addPopupDeleteCol()
        self.addPopupAddRowBeforeCurrent()
        self.addPopupAddRowAfterCurrent()
        self.addPopupDeleteRow()
        self.addPopupSpan()
        self.addPopupClearCurrentSpan()
        self.addPopupAddGroupRow()
        self.addPopupDeleteGroupRow()

    def addPopupAddColBeforeCurrent(self):
        self._actAddColBeforeCurrent = self.initPopupAction(self._actAddColBeforeCurrent, 'actAddColBeforeCurrent', u'Вставить столбец до', self.on_actAddColBeforeCurrent_triggered)

    def addPopupAddColAfterCurrent(self):
        self._actAddColBeforeCurrent = self.initPopupAction(self._actAddColAfterCurrent, 'actAddColAfterCurrent', u'Вставить столбец после', self.on_actAddColAfterCurrent_triggered)

    def addPopupDeleteCol(self):
        self._actDeleteCol = self.initPopupAction(self._actDeleteCol, 'actDeleteCol', u'Удалить колонку', self.on_actDeleteCol_triggered)

    def addPopupAddRowBeforeCurrent(self):
        self._actAddRowBeforeCurrent = self.initPopupAction(self._actAddRowBeforeCurrent, 'actAddRowBeforeCurrent', u'Вставить строку до', self.on_actAddRowBeforeCurrent_triggered)

    def addPopupAddRowAfterCurrent(self):
        self._actAddRowAfterCurrent = self.initPopupAction(self._actAddRowAfterCurrent, 'actAddRowAfterCurrent', u'Вставить строку после', self.on_actAddRowAfterCurrent_triggered)

    def addPopupDeleteRow(self):
        self._actDeleteRow = self.initPopupAction(self._actDeleteRow, 'actDeleteRow', u'Удалить строку', self.on_actDeleteRow_triggered)

    def addPopupSpan(self):
        self._actSpan = self.initPopupAction(self._actSpan, 'actSpan', u'Объединить ячейки', self.on_actSpan_triggered)

    def addPopupClearCurrentSpan(self):
        self._actClearCurrentSpan = self.initPopupAction(self._actClearCurrentSpan, 'actClearCurrentSpan', u'Разделить ячейки', self.on_actClearCurrentSpan_triggered)

    def addPopupAddGroupRow(self):
        self._actAddGroupRow = self.initPopupAction(self._actAddGroupRow, 'actAddGroupRow', u'Добавить группировку', self.on_actAddGroupRow_triggered)

    def addPopupDeleteGroupRow(self):
        self._actDeleteGroupRow = self.initPopupAction(self._actDeleteGroupRow, 'actDeleteGroupRow', u'Удалить группировку', self.on_actDeleteGroupRow_triggered)

    def on_actAddColBeforeCurrent_triggered(self):
        row, column, rowCount, columnCount = self.getSelectionRectangle()
        self.model().addColumn(column)
        self.model().reset()
        self.resizeColumnsToContents()

    def on_actAddColAfterCurrent_triggered(self):
        row, column, rowCount, columnCount = self.getSelectionRectangle()
        self.model().addColumn(column + columnCount)
        self.model().reset()
        self.resizeColumnsToContents()

    def on_actDeleteCol_triggered(self):
        row, column, rowCount, columnCount = self.getSelectionRectangle()
        self.model().deleteColumn(column + 1)
        self.model().reset()
        self.resizeColumnsToContents()

    def on_actAddRowBeforeCurrent_triggered(self):
        row, column, rowCount, columnCount = self.getSelectionRectangle()
        self.model().addRow(row)
        self.model().reset()
        self.resizeColumnsToContents()

    def on_actAddRowAfterCurrent_triggered(self):
        row, column, rowCount, columnCount = self.getSelectionRectangle()
        self.model().addRow(row + rowCount)
        self.model().reset()
        self.resizeColumnsToContents()

    def on_actDeleteRow_triggered(self):
        indexes = self.selectionModel().selectedRows()
        for index in indexes:
            row = index.row()
            self.model().deleteRow(row)
        self.model().reset()
        self.resizeColumnsToContents()

    def on_actSpan_triggered(self):
        row, column, rowCount, columnCount = self.getSelectionRectangle()

        self.setSpan(row, column, rowCount, columnCount)

        index = self.model().createIndex(row, column)
        item = self.model().getItem(index)
        item.setRowSpan(rowCount)
        item.setColumnSpan(columnCount)
        self.model().setItem(index, item)

    def on_actClearCurrentSpan_triggered(self):
        indexes = self.selectionModel().selectedIndexes()
        for index in indexes:
            item = self.model().getItem(index)
            item.setRowSpan(1)
            item.setColumnSpan(1)
            self.model().setItem(index, item)
        self.spanUpdate()

    def on_actAddGroupRow_triggered(self):
        self.model().addGroupRow()
        self.model().reset()
        self.resizeColumnsToContents()

    def on_actDeleteGroupRow_triggered(self):
        row = self.currentIndex().row()
        self.model().deleteGroupRow(row)
        self.model().reset()
        self.resizeColumnsToContents()

    def on_popupMenu_aboutToShow(self):
        row = self.getSelectionRectangle()[0]
        checkSelectionEqCurrentSpan = self.checkSelectionEqCurrentSpan()
        checkSelectionContainsFieldRow = self.checkSelectionContainsFieldRow()
        checkSelectionContainsGroupRow = self.checkSelectionContainsGroupRow()
        multiSelection = bool(len(self.selectionModel().selectedIndexes()) > 1)
        singleSelection = bool(len(self.selectionModel().selectedIndexes()) == 1)
        selectedColumns = bool(len(self.selectionModel().selectedColumns()))
        selectedRows = bool(len(self.selectionModel().selectedRows()))
        selectedOneRow = self.checkSelectedOneRow()
        fieldRow = bool(row == self.model()._fieldRow)
        groupRow = self.model().isGroupRow(row)
        capRow = not fieldRow and not groupRow

        if self._actSpan:
            self._actSpan.setEnabled(multiSelection and not checkSelectionEqCurrentSpan
                                     and not checkSelectionContainsFieldRow
                                     and (not checkSelectionContainsGroupRow or (selectedOneRow and bool(groupRow))))
        if self._actClearCurrentSpan:
            self._actClearCurrentSpan.setEnabled(multiSelection and checkSelectionEqCurrentSpan)
        if self._actDeleteCol:
            self._actDeleteCol.setEnabled(singleSelection)
        if self._actDeleteRow:
            self._actDeleteRow.setEnabled(selectedRows and not fieldRow)
        if self._actAddRowAfterCurrent:
            self._actAddRowAfterCurrent.setEnabled((singleSelection or checkSelectionEqCurrentSpan) and capRow)
        if self._actAddColBeforeCurrent:
            self._actAddColBeforeCurrent.setEnabled(singleSelection or checkSelectionEqCurrentSpan)
        if self._actAddColAfterCurrent:
            self._actAddColAfterCurrent.setEnabled(singleSelection or checkSelectionEqCurrentSpan)
        if self._actAddRowBeforeCurrent:
            self._actAddRowBeforeCurrent.setEnabled((singleSelection or checkSelectionEqCurrentSpan) and capRow)
        if self._actAddGroupRow:
            self._actAddGroupRow.setEnabled(True)
        if self._actDeleteGroupRow:
            self._actDeleteGroupRow.setEnabled(bool(groupRow) and singleSelection)

    def checkSelectionEqCurrentSpan(self):
        row, column, rowCount, columnCount = self.getSelectionRectangle()
        index = self.model().createIndex(row, column)
        item = self.model().getItem(index)
        if item and (rowCount == item.rowSpan()) and (columnCount == item.columnSpan()):
            return True
        return False

    def checkSelectionContainsFieldRow(self):
        row, column, rowCount, columnCount = self.getSelectionRectangle()
        fieldRow = self.model()._fieldRow
        if fieldRow < row + rowCount and fieldRow >= row:
            return True
        return False

    def checkSelectionContainsGroupRow(self):
        row, column, rowCount, columnCount = self.getSelectionRectangle()
        for idx in range(row, row + rowCount):
            if self.model().isGroupRow(idx):
                return True
        return False

    def checkSelectedOneRow(self):
        row, column, rowCount, columnCount = self.getSelectionRectangle()
        return bool(rowCount == 1)

    def getSelectionRectangle(self):
        indexes = self.selectionModel().selectedIndexes()
        if not indexes:
            return 0, 0, 0, 0
        rows = [index.row() for index in indexes]
        columns = [index.column() for index in indexes]
        minRow = min(rows)
        minColumn = min(columns)
        rowCount = max(rows) - min(rows) + 1
        columnCount = max(columns) - min(columns) + 1
        return minRow, minColumn, rowCount, columnCount

    def spanUpdate(self):
        self.clearSpans()
        for row, items in enumerate(self.model().items()):
            for col, item in items.items():
                self.setSpan(row, col, item.rowSpan(), item.columnSpan())

    def copy(self):
        self.buffer = {}
        indexes = self.selectionModel().selectedIndexes()
        row, column, rowCount, columnCount = self.getSelectionRectangle()
        for index in indexes:
            self.buffer.setdefault(index.row() - row, {})[index.column() - column] = self.model()._items[index.row()][index.column()]
        self.buffer

    def paste(self):
        curRow, curColumn, rowCount, columnCount = self.getSelectionRectangle()
        for row, rowItems in self.buffer.items():
            for column, item in rowItems.items():
                newRow = curRow + row
                newColumn = curColumn + column
                if newRow < self.model().rowCount() and newColumn < self.model().columnCount():
                    self.pasteCell(newRow, newColumn, item)
        self.model().reset()
        self.resizeColumnsToContents()


    def pasteCell(self, row, column, item):
        oldItem = self.model().getItemEx(row, column)
        if item._type.startswith('g') != oldItem._type.startswith('g') and item._type != oldItem._type:
            return
        oldItem._alignment = item._alignment
        oldItem._bold = item._bold
        oldItem._name = item._name
        oldItem._columnSpan = item._columnSpan
        oldItem._rowSpan = item._rowSpan
        oldItem._value = item._value
        oldItem._readOnly = item._readOnly

    def keyPressEvent(self, event):
        key = event.key()
        text = unicode(event.text())
        if event.matches(QtGui.QKeySequence.Copy):
            event.ignore()
            self.copy()
        if event.matches(QtGui.QKeySequence.Paste):
            event.ignore()
            self.paste()
        else:
            CInDocTableViewModifyPopup.keyPressEvent(self, event)