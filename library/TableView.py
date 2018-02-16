# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from PyQt4.QtCore import QEventLoop, QMimeData, QVariant, Qt, SIGNAL

from Registry.ClientRecordProperties import CRecordProperties
from Reports.ReportBase import CReportBase, createTable
from Reports.ReportView import CReportViewDialog
from library.ExtendedTableView import CExtendedTableView
from library.PreferencesMixin import CPreferencesMixin
from library.TableModel import CRichTextItemDelegate, CTableModel
from library.Utils import forceInt, forceString, getPref, setPref, toVariant


class CTableView(CExtendedTableView, CPreferencesMixin):
    def __init__(self, parent):
        super(CTableView, self).__init__(parent)
        self._popupMenu = None
        self._actDeleteRow = None
        self._actCopyCell = None
        self._actRecordProperties = None
        self.__reportHeader = u'List of records'
        self.__reportDescription = u''

        self.setItemDelegate(CRichTextItemDelegate(self))

        h = self.fontMetrics().height()
        self.verticalHeader().setDefaultSectionSize(3*h/2)
        self.verticalHeader().hide()
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setStretchLastSection(True)

        self.setSortingEnabled(True)
        self.horizontalHeader().setSortIndicatorShown(False)

        self.setHorizontalScrollMode(self.ScrollPerPixel)
        self.setVerticalScrollMode(self.ScrollPerPixel)

    def createPopupMenu(self, actions=None):
        if not actions:
            actions = []
        self._popupMenu = QtGui.QMenu(self)
        self._popupMenu.setObjectName('popupMenu')
        for action in actions:
            if isinstance(action, QtGui.QAction):
                self._popupMenu.addAction(action)
            elif action == '-':
                self._popupMenu.addSeparator()
        self.connect(self._popupMenu, QtCore.SIGNAL('aboutToShow()'), self.popupMenuAboutToShow)
        return self._popupMenu

    def setPopupMenu(self, menu):
        self._popupMenu = menu

    def popupMenu(self):
        if not self._popupMenu:
            self.createPopupMenu()
        return self._popupMenu

    def addPopupSeparator(self):
        self.popupMenu().addSeparator()

    def addPopupAction(self, action):
        self.popupMenu().addAction(action)

    def addPopupDelRow(self):
        self._actDeleteRow = QtGui.QAction(u'Удалить запись', self)
        self._actDeleteRow.setObjectName('actDeleteRow')
        self.connect(self._actDeleteRow, QtCore.SIGNAL('triggered()'), self.removeCurrentRow)
        self.addPopupAction(self._actDeleteRow)

    def addPopupDelSelectedRow(self):
        self._actDeleteRow = QtGui.QAction(u'Удалить выбранные записи', self)
        self._actDeleteRow.setObjectName('actDeleteRow')
        self.connect(self._actDeleteRow, QtCore.SIGNAL('triggered()'), self.removeSelectedRows)
        self.addPopupAction(self._actDeleteRow)

    def addPopupCopyCell(self):
        self._actCopyCell = QtGui.QAction(u'Копировать', self)
        self._actCopyCell.setObjectName('actCopyCell')
        self.connect(self._actCopyCell, QtCore.SIGNAL('triggered()'), self.copyCurrentCell)
        self.addPopupAction(self._actCopyCell)

    def addPopupRecordProperies(self):
        self._actRecordProperties = QtGui.QAction(u'Свойства записи', self)
        self._actRecordProperties.setObjectName('actRecordProperties')
        self.connect(self._actRecordProperties, QtCore.SIGNAL('triggered()'), self.showRecordProperties)
        self.addPopupAction(self._actRecordProperties)

    def setReportHeader(self, reportHeader):
        self.__reportHeader = reportHeader

    def reportHeader(self):
        return self.__reportHeader

    def setReportDescription(self, reportDescription):
        self.__reportDescription = reportDescription

    def reportDescription(self):
        return self.__reportDescription

    def popupMenuAboutToShow(self):
        currentIndex = self.currentIndex()
        curentIndexIsValid = currentIndex.isValid()
        if self._actDeleteRow:
            self._actDeleteRow.setEnabled(curentIndexIsValid and self.canRemoveRow(currentIndex.row()))
        if self._actCopyCell:
            self._actCopyCell.setEnabled(curentIndexIsValid)
        if self._actRecordProperties:
            self._actRecordProperties.setEnabled(curentIndexIsValid)

    def setIdList(self, idList, itemId=None, realItemCount=None, **params):
        if not itemId:
            itemId = self.currentItemId()
        if not idList:
            selectionModel = self.selectionModel()
            if selectionModel:
                selectionModel.clear()
        self.model().setIdList(idList, realItemCount, **params)
        if idList:
            self.setCurrentItemId(itemId)
        if self.isSortingEnabled() and self.horizontalHeader().isSortIndicatorShown():
            self.sortByColumn(self.horizontalHeader().sortIndicatorSection(),
                              self.horizontalHeader().sortIndicatorOrder())

    def setCurrentRow(self, row):
        rowCount = self.model().rowCount()
        if row >= rowCount:
            row = rowCount-1
        if row >= 0:
            self.setCurrentIndex(self.model().index(row, 0))
        elif rowCount>0:
            self.setCurrentIndex(self.model().index(0, 0))

    def currentRow(self):
        index = self.currentIndex()
        if index.isValid():
            return index.row()
        return None

    def setCurrentItemId(self, itemId):
        self.setCurrentRow(self.model().findItemIdIndex(itemId))

    def currentItemId(self):
        return self.itemId(self.currentIndex())

    def currentItem(self):
        itemId = self.currentItemId()
        record = self.model().recordCache().get(itemId) if itemId else None
        return record

    def selectedRowList(self):
        return list(set([index.row() for index in self.selectedIndexes()]))

    def selectedElementsAsStringsList(self):
        return list(set([(unicode(index.data().toString())) for index in self.selectedIndexes()]))

    def selectedItemIdList(self):
        itemIdList = self.model().idList()
        return [itemIdList[row] for row in self.selectedRowList()]

    def setSelectedRowList(self, rowList):
        model = self.model()
        selectionModel = self.selectionModel()
        for row in rowList:
            index = model.index(row, 0)
            selectionModel.select(index, QtGui.QItemSelectionModel.Select|QtGui.QItemSelectionModel.Rows)

    def setSelectedItemIdList(self, idList):
        self.setSelectedRowList((self.model().findItemIdIndex(itemId) for itemId in idList))

    def prepareCopy(self):
        cbfItemId = 'application/x-s11/itemid'
        currentItemId = self.currentItemId()
        strData=self.model().table().tableName+':'
        if currentItemId:
            strData += str(currentItemId)
        return {cbfItemId:strData}

    def copy(self):
        dataList = self.prepareCopy()
        mimeData = QMimeData()
        for dataFormat, data in dataList.iteritems():
            v = toVariant(data)
            mimeData.setData(dataFormat, v.toByteArray())
        QtGui.qApp.clipboard().setMimeData(mimeData)

    def itemId(self, index):
        if index.isValid():
            row = index.row()
            itemIdList = self.model().idList()
            if row in xrange(len(itemIdList)):
                return itemIdList[row]
        return None

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:
            event.ignore()
        elif key == Qt.Key_Return or key == Qt.Key_Enter:
            event.ignore()
        elif key == Qt.Key_Space:
            event.accept()
            self.emit(SIGNAL('hide()'))
        elif event == QtGui.QKeySequence.Copy:
            event.accept()
            self.copy()
        else:
            super(CTableView, self).keyPressEvent(event)

    def contextMenuEvent(self, event): # event: QContextMenuEvent
        if self._popupMenu:
            self._popupMenu.exec_(event.globalPos())
            event.accept()
        else:
            event.ignore()

    def contentToHTML(self, columnRoleList=None, titles = None, fontSize = 8):
        u"""
        Переводит содержимое таблицы в экземляр класса QTextDocument (atronah: странная логика названия)
        :param columnRoleList: список с ролями данных для каждого столбца.
            Если роль для столбца не указана, то он не выводится, иначе выводятся данные, полученные для этой роли.
            Если вместо списка передано None, то отображаются все видимые столбцы модели.
        :param titles: список заголовков столбцов. Если задан, то данное имя используется для столбца в
            HTML-представлении, если None, то используется заголовок из модели.
        :param fontSize:
        :return:
        """
        model = self.model()
        cols = model.cols()
        if columnRoleList is None:
            columnRoleList = [None if self.isColumnHidden(idx) else Qt.DisplayRole 
                              for idx in xrange(len(cols))]
        
        if titles is None:
            titles = [None] * len(cols)
        
        QtGui.qApp.startProgressBar(model.rowCount())
        try:
            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)

            headerFormat = QtGui.QTextCharFormat()
            headerFormat.setFontWeight(QtGui.QFont.Bold)
            headerFormat.setFontPointSize(fontSize + 4)
            bodyFormat = QtGui.QTextCharFormat()
            bodyFormat.setFontPointSize(fontSize)
            tableFormat = QtGui.QTextCharFormat()
            tableFormat.setFontPointSize(fontSize)

            cursor.setCharFormat(headerFormat)
            header = self.reportHeader()
            if Qt.mightBeRichText(header):
                cursor.insertHtml(header)
            else:
                cursor.insertText(header)
            cursor.insertBlock()
            cursor.setCharFormat(bodyFormat)
            description = self.reportDescription()
            if Qt.mightBeRichText(description):
                cursor.insertHtml(description)
            else:
                cursor.insertText(description)
            cursor.insertBlock()

            colWidths  = [ self.columnWidth(i) for i in xrange(len(cols)) ]
            totalWidth = sum(colWidths)
            tableColumns = [('10?', [u'№'], CReportBase.AlignRight)]
            for iCol, colWidth in enumerate(colWidths):
                widthInPercents = str(max(1, colWidth*100./totalWidth))+'?'
                if columnRoleList[iCol] is None:
                    continue
                col = cols[iCol]
                colAlingment = Qt.AlignHorizontal_Mask & forceInt(col.alignment())
                blockFormat = QtGui.QTextBlockFormat()
                blockFormat.setAlignment(Qt.AlignmentFlag(colAlingment))
                columnTitle = forceString(titles[iCol] if isinstance(titles[iCol], basestring) else col.title())
                tableColumns.append((widthInPercents, [columnTitle], blockFormat))

            table = createTable(cursor, tableColumns, 1, 1, 2, 0, tableFormat)
            for iModelRow in xrange(model.rowCount()):
                QtGui.qApp.stepProgressBar()
                QtGui.qApp.processEvents(QEventLoop.ExcludeUserInputEvents)
                iTableRow = table.addRow()
                table.setText(iTableRow, 0, iModelRow + 1, tableFormat)
                iTableCol = 1
                for iModelCol in xrange(len(cols)):
                    columnRole = columnRoleList[iModelCol]
                    if columnRole is None:
                        continue
                    index = model.index(iModelRow, iModelCol)
                    text = forceString(model.data(index, role = columnRole))
                    table.setText(iTableRow, iTableCol, text, tableFormat)
                    iTableCol += 1

            return doc
        finally:
            QtGui.qApp.stopProgressBar()

    # Создан для вывода дополнительных столбцов, отсутствующих в таблице, на основание наличия в моделе таблицы eventId
    # Метод создан для использования в Сводке Стационарного монитора, в рамках задачи 1739
    def contentToHTMLWithAnAdditionalColumn(self, columnRoleList=None, titles=None, fontSize=8, additionalCol=None,
                                            additionalColTitle=None):
        if not additionalCol:
            additionalCol = {}
        if not additionalColTitle:
            additionalColTitle = []
        model = self.model()
        cols = model.cols()
        if columnRoleList is None:
            columnRoleList = [None if self.isColumnHidden(idx) else Qt.DisplayRole
                              for idx in xrange(len(cols))]
        columnRoleList.extend([Qt.DisplayRole for i in xrange(len(additionalCol))])

        if titles is None:
            titles = [None] * len(cols)

        QtGui.qApp.startProgressBar(model.rowCount())
        try:
            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)

            headerFormat = QtGui.QTextCharFormat()
            headerFormat.setFontWeight(QtGui.QFont.Bold)
            headerFormat.setFontPointSize(fontSize + 4)
            bodyFormat = QtGui.QTextCharFormat()
            bodyFormat.setFontPointSize(fontSize)
            tableFormat = QtGui.QTextCharFormat()
            tableFormat.setFontPointSize(fontSize)

            cursor.setCharFormat(headerFormat)
            header = self.reportHeader()
            if Qt.mightBeRichText(header):
                cursor.insertHtml(header)
            else:
                cursor.insertText(header)
            cursor.insertBlock()
            cursor.setCharFormat(bodyFormat)
            description = self.reportDescription()
            if Qt.mightBeRichText(description):
                cursor.insertHtml(description)
            else:
                cursor.insertText(description)
            cursor.insertBlock()

            colWidths  = [ self.columnWidth(i) for i in xrange(len(cols) + len(additionalCol)) ]
            totalWidth = sum(colWidths)
            tableColumns = [('10?', [u'№'], CReportBase.AlignRight)]
            tempAddColTitleList = []
            for iCol, colWidth in enumerate(colWidths):
                widthInPercents = str(max(1, colWidth*100./totalWidth))+'?'
                if columnRoleList[iCol] is None:
                    continue
                blockFormat = QtGui.QTextBlockFormat()
                if iCol < len(cols):
                    col = cols[iCol]
                    colAlingment = Qt.AlignHorizontal_Mask & forceInt(col.alignment())
                    blockFormat.setAlignment(Qt.AlignmentFlag(colAlingment))
                    columnTitle = forceString(titles[iCol] if isinstance(titles[iCol], basestring) else col.title())
                else:
                    blockFormat.setAlignment(Qt.AlignCenter)
                    i = 0
                    for key in additionalColTitle:
                        if additionalCol.has_key(key):
                            columnTitle = key
                            if i == iCol - len(cols):
                                break
                            i += 1
                    tempAddColTitleList.append(columnTitle)
                tableColumns.append((widthInPercents, [columnTitle], blockFormat))

            table = createTable(cursor, tableColumns, 1, 1, 2, 0, tableFormat)
            for iModelRow in xrange(model.rowCount()):
                QtGui.qApp.stepProgressBar()
                QtGui.qApp.processEvents(QEventLoop.ExcludeUserInputEvents)
                iTableRow = table.addRow()
                table.setText(iTableRow, 0, iModelRow + 1, tableFormat)
                iTableCol = 1
                for iModelCol in xrange(len(cols)):
                    columnRole = columnRoleList[iModelCol]
                    if columnRole is None:
                        continue
                    index = model.index(iModelRow, iModelCol)
                    text = forceString(model.data(index, role = columnRole))
                    table.setText(iTableRow, iTableCol, text, tableFormat)
                    iTableCol += 1
                try:
                    eventId = forceInt(model.items[iTableRow - 1].get('eventId'))
                except:
                    eventId = ''
                for iAddCol in xrange(len(additionalCol)):
                    tempList = additionalCol.get(tempAddColTitleList[iAddCol])
                    if tempList.has_key(eventId):
                        rowText = tempList.get(eventId)
                    else:
                        rowText = ''
                    table.setText(iTableRow, iTableCol + iAddCol, rowText, tableFormat)

            return doc
        finally:
            QtGui.qApp.stopProgressBar()

    def printContent(self, columnRoleList=None, titles=None, fontSize=8, additionalCol=None, additionalColTitle=None):
        if not additionalCol:
            additionalCol = {}
        if not additionalColTitle:
            additionalColTitle = []
        if additionalCol:
            html = self.contentToHTMLWithAnAdditionalColumn(columnRoleList, titles, fontSize, additionalCol, additionalColTitle)
        else:
            html = self.contentToHTML(columnRoleList, titles, fontSize)
        view = CReportViewDialog(self)
        view.setText(html)
        view.exec_()

    def canRemoveRow(self, row):
        return self.model().canRemoveRow(row)

    def confirmRemoveRow(self, row, multiple=False):
        return self.model().confirmRemoveRow(self, row, multiple)

    def removeCurrentRow(self):
        def removeCurrentRowInternal():
            index = self.currentIndex()
            if index.isValid() and self.confirmRemoveRow(self.currentIndex().row()):
                row = self.currentIndex().row()
                self.model().removeRow(row)
                self.setCurrentRow(row)
        QtGui.qApp.call(self, removeCurrentRowInternal)

    def removeSelectedRows(self):
        def removeSelectedRowsInternal():
            currentRow = self.currentIndex().row()
            newSelection = []
            deletedCount = 0
            rows = self.selectedRowList()
            rows.sort()
            for row in rows:
                actualRow = row-deletedCount
                self.setCurrentRow(actualRow)
                confirm = self.confirmRemoveRow(actualRow, len(rows)>1)
                if confirm is None:
                    newSelection.extend(x-deletedCount for x in rows if x>row)
                    break
                if confirm:
                    self.model().removeRow(actualRow)
                    deletedCount += 1
                    if currentRow>row:
                        currentRow-=1
                else:
                    newSelection.append(actualRow)
            if newSelection:
                self.setSelectedRowList(newSelection)
            else:
                self.setCurrentRow(currentRow)
        QtGui.qApp.call(self, removeSelectedRowsInternal)

    def copyCurrentCell(self):
        index = self.currentIndex()
        if index.isValid():
            carrier = QMimeData()
            dataAsText = self.model().data(index, Qt.DisplayRole)
            carrier.setText(dataAsText.toString() if dataAsText else '' )
            QtGui.qApp.clipboard().setMimeData(carrier)

    def showRecordProperties(self):
        table = self.model().table()
        itemId = self.currentItemId()
        CRecordProperties(self, table, itemId).exec_()

    def colKey(self, col):
        return unicode('width '+forceString(col.title()))

    def loadPreferences(self, preferences):
        model = self.model()
        if not preferences:
            return
        if isinstance(model, CTableModel):
            charWidth = self.fontMetrics().width('A0')/2
            cols = model.cols()
            i = 0
            for col in cols:
                width = forceInt(getPref(preferences, self.colKey(col), col.defaultWidth()*charWidth))
                if width:
                    self.setColumnWidth(i, width)
                i += 1
        else:
            if model:
                for i in xrange(model.columnCount()):
                    width = forceInt(getPref(preferences, 'col_'+str(i), None))
                    if width:
                        self.setColumnWidth(i, width)
        # self.resizeColumnsToContents()
        # self.resizeRowsToContents()

    def savePreferences(self):
        preferences = {}
        model = self.model()
        if isinstance(model, CTableModel):
            cols = model.cols()
            i = 0
            for col in cols:
                width = self.columnWidth(i)
                setPref(preferences, self.colKey(col), QVariant(width))
                i += 1
        else:
            if model:
                for i in xrange(model.columnCount()):
                    width = self.columnWidth(i)
                    setPref(preferences, 'col_'+str(i), QVariant(width))
        return preferences

    @property
    def object_name(self):
        return '%s.%s' % (self.parent().objectName(), self.objectName())

    def showEvent(self, evt):
        self.loadPreferences(getPref(QtGui.qApp.preferences.tablePrefs, self.object_name, {}))

    def hideEvent(self, evt):
        setPref(QtGui.qApp.preferences.tablePrefs, self.object_name, self.savePreferences())

    def getColumnNames(self):
        return [self.model().headerData(idx, Qt.Horizontal).toString() for idx in xrange(self.model().columnCount())]

    def getColumnSelection(self):
        return [not self.isColumnHidden(idx) for idx in xrange(self.model().columnCount())]

    def setColumnSelection(self, columnSelection):
        for column, isVisible in enumerate(columnSelection):
            self.setColumnHidden(column, not isVisible)

    def setColumnSelectionEnabled(self, enabled):
        hh = self.horizontalHeader()
        if enabled:
            hh.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            hh.customContextMenuRequested.connect(self.showColumnSelector)
        else:
            hh.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
            hh.customContextMenuRequested.connect(self.showColumnSelector)

    def showColumnSelector(self, pos):
        columnsSelector = CTableColumnSelectionMenu(self, self.getColumnNames(), self.getColumnSelection())
        columnsSelector.selectionChanged.connect(self.setColumnHidden)
        columnsSelector.exec_(self.mapToGlobal(pos))
        columnsSelector.selectionChanged.disconnect(self.setColumnHidden)


class CTableColumnSelectionMenu(QtGui.QMenu):
    selectionChanged = QtCore.pyqtSignal(int, bool)

    def __init__(self, parent, columnNames, columnSelection):
        super(CTableColumnSelectionMenu, self).__init__(parent)

        self._columnActions = []
        for columnName, columnSelected in zip(columnNames, columnSelection):
            act = QtGui.QAction(columnName, self, checkable=True, checked=columnSelected)
            self._columnActions.append(act)
            self.addAction(act)

        self.installEventFilter(self)

    def getColumnSelection(self):
        return [act.isChecked() for act in self._columnActions]

    def eventFilter(self, obj, evt):
        if evt.type() == QtCore.QEvent.MouseButtonRelease:
            if isinstance(obj, CTableColumnSelectionMenu):
                action = self.activeAction()
                if action:
                    action.trigger()
                    self.emitSelectionChanged(action)
                return True
        return False

    def emitSelectionChanged(self, action):
        try:
            idx = self._columnActions.index(action)
            self.selectionChanged.emit(idx, not action.isChecked())
        except ValueError:
            pass
