# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from PyQt4.QtCore import Qt

from Reports.ReportBase import createTable
from library.ItemListModel import CItemListModel, CItemTableCol
from library.PreferencesMixin import CPreferencesMixin
from library.Utils import forceInt, forceString, getPref, setPref


class CLocItemDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, parent):
        super(CLocItemDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        column = index.column()
        item = index.model().getItem(index.row())
        editor = index.model().createEditor(column, parent, item)
        return editor

    def setEditorData(self, editor, index):
        if editor is not None:
            model = index.model()  # type: CItemListModel
            row, column = index.row(), index.column()
            col = model.cols()[column]  # type: CItemTableCol
            if row < model.itemCount():
                item = model.items()[row]
                value = model.data(index, Qt.EditRole)
            else:
                item = model.newItem()
                value = QtCore.QVariant(col.displayValue(item))
            model.setEditorData(column, editor, value, item)

    def setModelData(self, editor, model, index):
        if editor is not None:
            column = index.column()
            editorData = index.model().getEditorData(column, editor)
            model.setData(index, editorData)


class CLocItemProxyDelegate(QtGui.QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        sourceModel = index.model().sourceModel()
        sourceIndex = index.model().mapToSource(index)
        column = sourceIndex.column()
        item = sourceModel.getItem(sourceIndex.row())
        editor = sourceModel.createEditor(column, parent, item)
        return editor

    def setEditorData(self, editor, index):
        sourceModel = index.model().sourceModel() # type: CItemListModel
        sourceIndex = index.model().mapToSource(index)
        if editor is not None:
            model = index.model()  # type: # CItemListModel
            row, column = sourceIndex.row(), sourceIndex.column()
            if row < sourceModel.itemCount():
                item = sourceModel.items()[row]
                value = sourceModel.data(sourceIndex, Qt.EditRole)
            else:
                item = sourceModel.newItem()
                value = None
            sourceModel.setEditorData(column, editor, value, item)

    def setModelData(self, editor, model, index):
        sourceModel = index.model().sourceModel()
        sourceIndex = index.model().mapToSource(index)
        if editor is not None:
            column = sourceIndex.column()
            editorData = sourceModel.getEditorData(column, editor)
            sourceModel.setData(sourceIndex, editorData)


class CItemListView(QtGui.QTableView, CPreferencesMixin):
    def __init__(self, parent):
        super(CItemListView, self).__init__(parent)
        self._popupMenu = None
        self.__actDeleteRows = None

        self.setShowGrid(True)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setItemDelegate(CLocItemDelegate(self))
        self.verticalHeader().setDefaultSectionSize(3 * self.fontMetrics().height() / 2)
        self.verticalHeader().setResizeMode(QtGui.QHeaderView.Fixed)
        self.verticalHeader().hide()
        self.horizontalHeader().setStretchLastSection(True)
        self.setEditTriggers(QtGui.QAbstractItemView.AnyKeyPressed |
                             QtGui.QAbstractItemView.EditKeyPressed |
                             QtGui.QAbstractItemView.SelectedClicked |
                             QtGui.QAbstractItemView.DoubleClicked)
        self.setAlternatingRowColors(True)
        self.setTabKeyNavigation(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setHorizontalScrollMode(self.ScrollPerPixel)
        self.setVerticalScrollMode(self.ScrollPerPixel)

    def item(self, index):
        return self.model().getItem(index.row())

    def itemId(self, index):
        item = self.item(index)
        return item.id if item else None

    def currentItem(self):
        return self.model().getItem(self.currentIndex().row())

    def currentItemId(self):
        item = self.currentItem()
        return item.id if item else None

    def setCurrentRow(self, row):
        rowCount = self.model().rowCount()
        if row >= rowCount :
            row = rowCount - 1
        if row >= 0:
            self.setCurrentIndex(self.model().index(row, 0))
        elif rowCount >= 0:
            self.setCurrentIndex(self.model().index(0, 0))

    def setCurrentItemId(self, itemId):
        self.setCurrentRow(self.model().searchId(itemId))

    def contextMenuEvent(self, event):
        if self._popupMenu and self.model().isEditable():
            self._popupMenu.exec_(event.globalPos())
            event.accept()
        else:
            event.ignore()

    def createPopupMenu(self, actions=None):
        if not actions:
            actions = []
        self._popupMenu = QtGui.QMenu(self)
        self._popupMenu.setObjectName('popupMenu')
        self.connect(self._popupMenu, QtCore.SIGNAL('aboutToShow()'), self.on_popupMenu_aboutToShow)
        self.addPopupActions(actions)
        return self._popupMenu

    def on_popupMenu_aboutToShow(self):
        row = self.currentIndex().row()
        rowCount = self.model().rowCount()
        if self.__actDeleteRows:
            rows = self.getSelectedRows()
            if len(rows) == 1 and rows[0] == row:
                self.__actDeleteRows.setText(u'Удалить текущую строку')
            elif len(rows) == 1:
                self.__actDeleteRows.setText(u'Удалить выделенную строку')
            else:
                self.__actDeleteRows.setText(u'Удалить выделенные строки')

            self.__actDeleteRows.setEnabled(len(rows) > 1 or (len(rows) == 1 and self.model().getItem(row) is not None))

    def addPopupActions(self, actionList, isAddSeparatorBefore=False):
        if self._popupMenu is None:
            self.createPopupMenu()

        if isAddSeparatorBefore:
            self.addPopupSeparator()

        for action in actionList:
            if isinstance(action, QtGui.QAction):
                self._popupMenu.addAction(action)
            elif action == '-':
                self._popupMenu.addSeparator()

    def addPopupDelRow(self):
        if self._popupMenu is None:
            self.createPopupMenu()
        self.__actDeleteRows = QtGui.QAction(u'Удалить строку', self)
        self.__actDeleteRows.setObjectName('actDeleteRows')
        self._popupMenu.addAction(self.__actDeleteRows)
        self.connect(self.__actDeleteRows, QtCore.SIGNAL('triggered()'), self.on_deleteRows)

    def on_deleteRows(self):
        rows = self.getSelectedRows()
        rows.sort(reverse=True)
        for row in rows:
            self.model().removeRow(row)

    def getSelectedRows(self):
        rowCount = self.model().rowCount()
        result = list(set(index.row() for index in self.selectionModel().selectedIndexes() if index.row() < rowCount))
        result.sort()
        return result

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:
            event.ignore()
        elif key == Qt.Key_Return or key == Qt.Key_Enter:
            if self.model().isEditable():
                index = self.currentIndex()
                self.setCurrentIndex(self.model().index(index.row() + 1, index.column()))
                event.accept()
            else:
                event.ignore()
        elif event.key() == Qt.Key_Tab:
            index = self.currentIndex()
            model = self.model()
            if index.row() == model.rowCount() - 1 and index.column() == model.columnCount() - 1:
                self.parent().focusNextChild()
                event.accept()
            else:
                QtGui.QTableView.keyPressEvent(self, event)
        elif event.key() == Qt.Key_Backtab:
            index = self.currentIndex()
            if index.row() == 0 and index.column() == 0:
                self.parent().focusPreviousChild()
                event.accept()
            else:
                QtGui.QTableView.keyPressEvent(self, event)
        else:
            QtGui.QTableView.keyPressEvent(self, event)

    @staticmethod
    def colKey(col):
        return u'width_{0}'.format(col.title())

    def loadPreferences(self, preferences):
        if isinstance(self.model(), CItemListModel):
            for idx, col in enumerate(self.model().cols()):
                width = forceInt(getPref(preferences, self.colKey(col), self.columnWidth(idx)))
                if width:
                    self.setColumnWidth(idx, width)

    def savePreferences(self):
        preferences = {}
        if isinstance(self.model(), CItemListModel):
            for idx, col in enumerate(self.model().cols()):
                setPref(preferences, self.colKey(col), QtCore.QVariant(self.columnWidth(idx)))
        return preferences

    def getColumnsWidth(self):
        return [self.columnWidth(colIdx) for colIdx in range(len(self.model().cols()))]

    def setColumnsWidth(self, columnsWidth):
        if columnsWidth:
            for colIdx, width in enumerate(columnsWidth):
                self.setColumnWidth(colIdx, width)

    def toTextDocument(self, fontSize=8):
        model = self.model()  # type: CItemListModel
        cols = model.cols()

        tableHeader = [forceString(col.title()) for col in cols]

        QtGui.qApp.startProgressBar(model.rowCount())
        try:
            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)

            headerFormat = QtGui.QTextCharFormat()
            headerFormat.setFontWeight(QtGui.QFont.Bold)
            headerFormat.setFontPointSize(fontSize + 4)
            tableHeaderFormat = QtGui.QTextCharFormat()
            tableHeaderFormat.setFontPointSize(fontSize)
            tableHeaderFormat.setFontWeight(QtGui.QFont.Bold)
            tableBodyFormat = QtGui.QTextCharFormat()
            tableBodyFormat.setFontPointSize(fontSize)

            colWidths = [self.columnWidth(i) for i in xrange(len(cols))]
            totalWidth = sum(colWidths)

            cursor.setCharFormat(headerFormat)
            tableColumns = []
            for colIdx, colWidth in enumerate(colWidths):
                widthInPercents = str(max(1, colWidth * 100.0 / totalWidth)) + '?'
                col = cols[colIdx]
                colAlingment = Qt.AlignHorizontal_Mask & forceInt(col.alignment(None))
                blockFormat = QtGui.QTextBlockFormat()
                blockFormat.setAlignment(Qt.AlignmentFlag(colAlingment))
                tableColumns.append((widthInPercents, [tableHeader[colIdx]], blockFormat))

            table = createTable(cursor, tableColumns, 1, 1, 2, 0, tableHeaderFormat)
            for rowIdx in xrange(model.rowCount()):
                QtGui.qApp.stepProgressBar()
                QtGui.qApp.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
                iTableRow = table.addRow()
                for colIdx in xrange(len(cols)):
                    text = forceString(model.data(model.index(rowIdx, colIdx)))
                    table.setText(iTableRow, colIdx, text, tableBodyFormat)

            return doc
        finally:
            QtGui.qApp.stopProgressBar()
