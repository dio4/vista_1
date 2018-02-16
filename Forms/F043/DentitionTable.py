# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Events.Action import CAction
from Reports.ReportBase import createTable, CReportBase
from Reports.ReportView import CReportViewDialog
from library.TableView import CTableView
from library.Utils import forceDate, forceInt, forceRef, forceString, toVariant, formatNameInt


class CClientDentitionHistoryTableView(CTableView):
    def __init__(self, parent):
        CTableView.__init__(self, parent)
        self.printRowShift = 1
        self.createCopyPasteActions()
        self.colorStatus = [QtCore.Qt.white, QtCore.Qt.lightGray, QtCore.Qt.darkYellow, QtCore.Qt.cyan, QtCore.Qt.blue,
                            QtCore.Qt.green, QtCore.Qt.darkGreen, QtCore.Qt.magenta, QtCore.Qt.yellow, QtCore.Qt.red]

    def createCopyPasteActions(self):
        self._actPrintHistory = QtGui.QAction(u'Распечатать историю', self)
        self.addPopupAction(self._actPrintHistory)
        self.connect(self._actPrintHistory, QtCore.SIGNAL('triggered()'), self.printHistory)

        self._actSelectedAll = QtGui.QAction(u'Выбрать все', self)
        self.addPopupAction(self._actSelectedAll)
        self.connect(self._actSelectedAll, QtCore.SIGNAL('triggered()'), self.selectedAll)

        self._actDeselectedAll = QtGui.QAction(u'Отменить выбор', self)
        self.addPopupAction(self._actDeselectedAll)
        self.connect(self._actDeselectedAll, QtCore.SIGNAL('triggered()'), self.deselectedAll)

    def getLastDentitionTeeth(self, items):
        return self.getDentitionTeeth()

    def getDentitionTeeth(self):
        return ['8', '7', '6', '5', '4', '3', '2', '1', '1', '2', '3', '4', '5', '6', '7', '8']

    def getParodentTeeth(self):
        return ['8', '7', '6', '5', '4', '3', '2', '1', '1', '2', '3', '4', '5', '6', '7', '8']

    def getBaseTeethValues(self, action, modelClass, teethRows, teethColumns=range(16), middleRow=3):
        teethValuesTop = []
        teethValuesLower = []
        for row in teethRows:
            if row < middleRow:
                for column in teethColumns:
                    propertyName = modelClass.getPropertyName(row, column)
                    property = action.getProperty(propertyName)
                    value = property.getText()
                    teethValuesTop.append(value)
            elif row > middleRow:
                for column in teethColumns:
                    propertyName = modelClass.getPropertyName(row, column)
                    property = action.getProperty(propertyName)
                    value = property.getText()
                    teethValuesLower.append(value)
        return teethValuesTop, teethValuesLower

    def getDentitionValues(self, action, teethRows, teethColumns=range(16)):
        return self.getBaseTeethValues(action, CDentitionModel, teethRows, teethColumns, 3)

    def getParodentValues(self, action, teethRows, teethColumns=range(16)):
        return self.getBaseTeethValues(action, CParodentiumModel, teethRows, teethColumns, 4)

    def getTeethValues(self, action):
        teethNumber = self.getDentitionTeeth()
        teethStatusTop, teethStatusLower = self.getDentitionValues(action, [0, 6])
        teethStateTop, teethStateLower = self.getDentitionValues(action, [2, 4])
        teethMobilityTop, teethMobilityLower = self.getDentitionValues(action, [1, 5])
        return teethNumber, teethStatusTop, teethStatusLower, teethStateTop, teethStateLower, teethMobilityTop, teethMobilityLower

    def getParodentTeethValues(self, action):
        teethNumber = self.getParodentTeeth()
        cunealDefectTop, cunealDefectLower = self.getParodentValues(action, [0, 8])
        recessionTop, recessionLower = self.getParodentValues(action, [1, 7])
        mobilityTop, mobilityLower = self.getParodentValues(action, [2, 6])
        pocketDepthTop, pocketDepthLower = self.getParodentValues(action, [3, 5])
        return teethNumber, cunealDefectTop, cunealDefectLower, recessionTop, recessionLower, mobilityTop, mobilityLower, pocketDepthTop, pocketDepthLower

    def getSubTitle(self):
        clientId = self.model().clientId()
        db = QtGui.qApp.db
        table = db.table('Client')
        record = db.getRecord(table, '*', clientId)
        lastName = forceString(record.value('lastName'))
        firstName = forceString(record.value('firstName'))
        patrName = forceString(record.value('patrName'))
        fullName = formatNameInt(lastName, firstName, patrName)
        birthDate = forceString(record.value('birthDate'))
        result = u'Пациент(код %d): %s, %s года рождения' % (clientId, fullName, birthDate)
        return result

    def getResult(self):
        rows = [u'Дата: %s' % forceString(QtCore.QDateTime.currentDateTime())]
        eventEditor = self.model().eventEditor()
        personId = eventEditor.cmbPerson.value()
        if personId:
            personName = forceString(QtGui.qApp.db.translate('vrbPersonWithSpeciality', 'id', personId, 'name'))
            rows.append(u'Ответственный: %s' % personName)
        return '\n'.join(rows)

    def printHistory(self):
        def isLastInBlock(valueIdx, valueRowIdx, valuesCount, valueRowsCount):
            return (valueIdx == (valuesCount - 1)) and (valueRowIdx == (valueRowsCount - 1))

        self.printRowShift = 1
        title = u'Стоматологическая история пациента'
        model = self.model()
        items = list(model.items())
        items.reverse()
        if not items:
            return
        lastDentitionTeeth = self.getLastDentitionTeeth(items)
        teethAdditional = [('4.8%', [u''], CReportBase.AlignLeft) for col in lastDentitionTeeth[0:16]]
        tableColumns = [('3%', [u'№'], CReportBase.AlignLeft),
                        ('10%', [u'Дата'], CReportBase.AlignLeft),
                        ('10%', [u'Тип свойства'], CReportBase.AlignLeft)
                        ] + teethAdditional

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(title)
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertText(self.getSubTitle())
        cursor.insertBlock()
        table = createTable(cursor, tableColumns)

        lenItems = len(items)
        for iRow, dentition in enumerate(items):
            record, action, actionId, eventId, isChecked = dentition
            if isChecked:
                if action.getType().flatCode == u'dentitionInspection':
                    teethNumber, teethStatusTop, teethStatusLower, teethStateTop, teethStateLower, teethMobilityTop, teethMobilityLower = self.getTeethValues(
                        action)
                    valueRowList = (
                        (teethStatusTop, u'Статус'), (teethMobilityTop, u'Подвижность'), (teethStateTop, u'Состояние'),
                        (teethNumber, u'Номер'), (teethStateLower, u'Состояние'), (teethMobilityLower, u'Подвижность'),
                        (teethStatusLower, u'Статус'))
                elif action.getType().flatCode == u'parodentInsp':
                    teethNumber, cunealDefectTop, cunealDefectLower, recessionTop, recessionLower, mobilityTop, mobilityLower, pocketDepthTop, pocketDepthLower = self.getParodentTeethValues(
                        action)
                    valueRowList = ((cunealDefectTop, u'Клиновидный дефект'), (recessionTop, u'Рецессия'),
                                    (mobilityTop, u'Подвижность'), (pocketDepthTop, u'Глубина кармана'),
                                    (teethNumber, u'Номер'), (pocketDepthLower, u'Глубина кармана'),
                                    (mobilityLower, u'Подвижность'), (recessionLower, u'Рецессия'),
                                    (cunealDefectLower, u'Клиновидный дефект'))
                values = [
                    (record, 'begDate', u'Осмотр', dentition, valueRowList)
                ]
                i = table.addRow()
                begMergeRow = i
                for valueIdx, (record, dateField, dentitionTypeName, dentitionItem, valueRows) in enumerate(values):
                    i, lastDentitionTeeth = self.checkDentitionEquals(lastDentitionTeeth, dentitionItem, table, i)
                    table.setText(i, 0, iRow + 1)
                    if record:
                        date = forceDate(record.value(dateField))
                        dateText = (forceString(date) + '\n' + dentitionTypeName) if date.isValid() else u''
                        table.setText(i, 1, dateText)
                    for valueRowIdx, (valueRow, rowName) in enumerate(valueRows):
                        self.addRowValues(rowName, table, valueRow, i, len(values), valueRowIdx)
                        if not isLastInBlock(valueIdx, valueRowIdx, len(values), len(valueRows)):
                            i = table.addRow()
                table.mergeCells(begMergeRow, 0, len(valueRowList), 1)
                table.mergeCells(begMergeRow, 1, len(valueRowList), 1)
                if iRow + 1 != lenItems:
                    i = table.addRow()
                    table.mergeCells(i, 0, 1, len(tableColumns))

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(self.getResult())
        cursor.insertBlock()

        viewDialog = CReportViewDialog(self)
        viewDialog.setWindowTitle(title)
        viewDialog.setRepeatButtonVisible()
        viewDialog.setText(doc)
        viewDialog.buttonBox.removeButton(viewDialog.buttonBox.button(QtGui.QDialogButtonBox.Retry))
        viewDialog.setWindowState(QtCore.Qt.WindowMaximized)
        viewDialog.exec_()

    def addRowValues(self, rowName, table, rowValues, i, countRow, valueRowIdx):
        boldChars = QtGui.QTextCharFormat()
        boldChars.setFontWeight(QtGui.QFont.Bold)
        if valueRowIdx == 3:
            table.setText(i, 2, rowName, charFormat=boldChars)
        else:
            table.setText(i, 2, rowName)
        for idxVal, val in enumerate(rowValues):
            val = val if val else u''
            if valueRowIdx == 3:
                table.setText(i, idxVal + 3, val, charFormat=boldChars)
            elif valueRowIdx == 0 or valueRowIdx == 6:
                table.setText(i, idxVal + 3, val, brushColor=self.getToothColor(val))
            else:
                table.setText(i, idxVal + 3, val)

    def getToothColor(self, val):
        color = QtGui.QColor(255, 255, 255)
        if val in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15']:
            color = QtCore.QVariant(QtGui.QColor(self.colorStatus[forceInt(val)]))
        return color

    def checkDentitionEquals(self, mainDentitionTeeth, dentitionItem, table, i):
        if dentitionItem:
            dentitionTeeth = self.getDentitionTeeth()
            if len(set(mainDentitionTeeth) ^ set(dentitionTeeth)) != 0:
                boldChars = QtGui.QTextCharFormat()
                boldChars.setFontWeight(QtGui.QFont.Bold)
                for teethValueIdx, teethValue in enumerate(dentitionTeeth):
                    table.setText(i, teethValueIdx + 3, teethValue, charFormat=boldChars)
                i = table.addRow()
                mainDentitionTeeth = dentitionTeeth
                self.printRowShift += 1
        return i, mainDentitionTeeth

    def copyDentitionInspection(self):
        self.model().setCurrentInspectionForPaste(self.currentIndex())

    def copyDentitionResult(self):
        self.model().setCurrentResultForPaste(self.currentIndex())

    def popupMenuAboutToShow(self):
        CTableView.popupMenuAboutToShow(self)
        currentIndex = self.currentIndex()
        curentIndexIsValid = currentIndex.isValid()
        model = self.model()
        self._actPrintHistory.setEnabled(bool(model.rowCount()))
        self._actSelectedAll.setEnabled(bool(model.rowCount()))
        self._actDeselectedAll.setEnabled(bool(model.rowCount()))

    def selectedAll(self):
        for row, (record, action, actionId, eventId, isChecked) in enumerate(self.model()._dentitionHistoryItems):
            self.model()._dentitionHistoryItems[row] = (record, action, actionId, eventId, 1)

    def deselectedAll(self):
        for row, (record, action, actionId, eventId, isChecked) in enumerate(self.model()._dentitionHistoryItems):
            self.model()._dentitionHistoryItems[row] = (record, action, actionId, eventId, 0)


class CDentitionTableView(QtGui.QTableView):
    def __init__(self, parent=None):
        QtGui.QTableView.__init__(self, parent)

        h = self.fontMetrics().height()
        self.verticalHeader().setDefaultSectionSize(3 * h / 2)
        self.verticalHeader().setResizeMode(QtGui.QHeaderView.Fixed)

        w = self.geometry().width()
        self.horizontalHeader().setDefaultSectionSize(w / 2)
        self.horizontalHeader().hide()

        self.setShowGrid(True)
        self.setTabKeyNavigation(True)

        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)

        self.itemDelegate = CItemDelegate(self)
        self.setItemDelegate(self.itemDelegate)

    def createPopupMenu(self):
        self._popupMenu = QtGui.QMenu(self)
        self.connect(self._popupMenu, QtCore.SIGNAL('aboutToShow()'), self.popupMenuAboutToShow)

        self._actPasteDentition = QtGui.QAction(u'Вставить формулу', self)
        self.connect(self._actPasteDentition, QtCore.SIGNAL('triggered()'), self.pasteDentition)
        self._popupMenu.addAction(self._actPasteDentition)

        self._actCopyDentition = QtGui.QAction(u'Копировать формулу', self)
        self.connect(self._actCopyDentition, QtCore.SIGNAL('triggered()'), self.copyDentition)
        self._popupMenu.addAction(self._actCopyDentition)

    def popupMenuAboutToShow(self):
        model = self.model()
        actionForPaste = model.getActionForPaste()
        self._actPasteDentition.setEnabled(bool(actionForPaste) and bool(model.isCurrentDentitionAction()))
        self._actCopyDentition.setEnabled(bool(model.action()))

    def copyDentition(self):
        model = self.model()
        action = model.action()
        model.setActionForPaste(action)

    def pasteDentition(self):
        self.model().pasteCopiedAction()

    def contextMenuEvent(self, event):
        self._popupMenu.exec_(event.globalPos())
        event.accept()


class CItemDelegate(QtGui.QItemDelegate):
    def __init__(self, parent):
        QtGui.QItemDelegate.__init__(self, parent)

    def commit(self):
        editor = self.sender()
        self.emit(QtCore.SIGNAL('commitData(QWidget *)'), editor)

    def commitAndCloseEditor(self):
        editor = self.sender()
        self.emit(QtCore.SIGNAL('commitData(QWidget *)'), editor)
        self.emit(QtCore.SIGNAL('closeEditor(QWidget *,QAbstractItemDelegate::EndEditHint)'), editor,
                  QtGui.QAbstractItemDelegate.NoHint)

    def createEditor(self, parent, option, index):
        model = index.model()
        row = index.row()
        # if row == 3:
        #     return None
        column = index.column()
        propertyType = model.getPropertyType(row, column)
        editor = propertyType.createEditor(model.action(), parent, model.clientId)
        self.connect(editor, QtCore.SIGNAL('commit()'), self.commit)
        self.connect(editor, QtCore.SIGNAL('editingFinished()'), self.commitAndCloseEditor)
        editor.setMinimumWidth(200)
        editor.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents)
        editor.setStyleSheet('width:150')
        return editor

    def setEditorData(self, editor, index):
        model = index.model()
        value = model.data(index, QtCore.Qt.EditRole)
        editor.setValue(value)

    def setModelData(self, editor, model, index):
        model = index.model()
        model.setData(index, toVariant(editor.value()))


class CDentitionModel(QtCore.QAbstractTableModel):
    # adultDefaultTeethValues = ['8', '7', '6', '5', '4', '3', '2', '1', '1', '2', '3', '4', '5', '6', '7', '8']
    colorStatus = [QtCore.Qt.white, QtCore.Qt.lightGray, QtCore.Qt.darkYellow, QtCore.Qt.cyan, QtCore.Qt.blue,
                   QtCore.Qt.green, QtCore.Qt.darkGreen, QtCore.Qt.magenta, QtCore.Qt.yellow, QtCore.Qt.red]

    teethRowTypes = {
        0: u'Статус',
        7: u'Статус',
        1: u'Подвижность',
        6: u'Подвижность',
        2: u'Состояние',
        5: u'Состояние',
        3: u'Верх',  # Номер
        4: u'Низ',  # Номер
    }

    wayJaw = {
        0: u'Левая',
        1: u'Правая'
    }

    jawHalfTypes = {
        0: u'Верхний',
        1: u'Верхний',
        2: u'Верхний',
        3: u'Верхний',
        4: u'Нижний',
        5: u'Нижний',
        6: u'Нижний',
        7: u'Нижний',
    }

    def __init__(self, parent, clientDentitionHistoryModel):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._actionRecord = None
        self._action = None
        self._isExistsDentitionAction = False
        self._isCurrentDentitionAction = False
        self.clientId = None

    def setIsExistsDentitionAction(self, isExistsDentitionAction):
        self._isExistsDentitionAction = isExistsDentitionAction

    def columnCount(self, index=QtCore.QModelIndex()):
        return 16

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(CDentitionModel.teethRowTypes.keys())

    def getPropertyType(self, row, column):
        return self._getProperty(row, column).type()

    def setClientId(self, clientId):
        self.clientId = clientId

    def getClientId(self):
        return self.clientId

    def _getProperty(self, row, column):
        # магия в том что у каждого ActionPropertyType зубной формулы
        # имя состоит (через точку) из типа свойства по отношению к формуле,
        # части челюсти и номера с права на лево(1...16)
        # например `Подвижность.Верхний.1`
        # обращение к значениям свойст происходит через их названия.
        # по row определяется тип и часть челюсти, а номер column+1
        propertyName = self.getPropertyName(row, column)
        return self._action.getProperty(propertyName)

    @classmethod
    def getPropertyName(cls, row, column):
        propertyTeethRowType = cls.teethRowTypes[row]
        propertyJawHalfType = cls.jawHalfTypes[row]
        propertyToothIdx = unicode(column + 1)
        propertyName = u'.'.join([propertyTeethRowType, propertyJawHalfType, propertyToothIdx])
        return propertyName

    def action(self):
        return self._action

    def loadAction(self, actionRecord, action, isCurrentDentitionAction=False):
        self._isCurrentDentitionAction = isCurrentDentitionAction
        self._actionRecord = actionRecord
        self._action = action
        self.reset()

    def isCurrentDentitionAction(self):
        return self._isCurrentDentitionAction

    def setNullValues(self):
        self.loadAction(None, None, None)

    def flags(self, index):
        if not self._isCurrentDentitionAction:
            return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Vertical:
                return QtCore.QVariant(CDentitionModel.teethRowTypes.get(section, None))
        return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()
        if not self._isExistsDentitionAction:
            return QtCore.QVariant()
        if not self._action:
            return QtCore.QVariant()
        row = index.row()
        column = index.column()
        if role == QtCore.Qt.DisplayRole:
            property = self._getProperty(row, column)
            return toVariant(property.getText())
        elif role == QtCore.Qt.BackgroundRole:
            if row == 0 or row == 7:
                property = self._getProperty(row, column)
                propertyValue = property.getValue()
                fSmb = propertyValue[0] if propertyValue else None
                if fSmb in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15']:
                    return QtCore.QVariant(QtGui.QColor(CDentitionModel.colorStatus[forceInt(fSmb)]))
        elif role == QtCore.Qt.EditRole:
            property = self._getProperty(row, column)
            return toVariant(property.getValue())
        return QtCore.QVariant()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid():
            return False
        row = index.row()
        column = index.column()
        if role == QtCore.Qt.EditRole:
            property = self._getProperty(row, column)
            propertyType = property.type()
            if not propertyType.isVector:
                property.setValue(propertyType.convertQVariantToPyValue(value))
                if row <= 2:
                    begIndex = self.index(0, column)
                    endIndex = self.index(3, column)
                    self.emitDataChanged(begIndex, endIndex)
                if row >= 4:
                    begIndex = self.index(3, column)
                    endIndex = self.index(6, column)
                    self.emitDataChanged(begIndex, endIndex)
                else:
                    self.emitDataChanged(index, index)
                return True
        return False

    def emitAllDataChanged(self):
        begIndex = self.index(0, 0)
        endIndex = self.index(self.rowCount() - 1, self.columnCount() - 1)
        self.emitDataChanged(begIndex, endIndex)

    def emitDataChanged(self, begIndex, endIndex):
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), begIndex, endIndex)

    def setDefaults(self):
        for row in [2]:
            for column in range(16):
                defaultValue = self._defaultValue(row, column)
                self.setData(self.index(row, column), defaultValue)

    def _defaultValue(self, row, column):
        return CDentitionModel.adultDefaultTeethValues[column]


class CParodentiumTableView(CDentitionTableView):
    def __init__(self, parent=None):
        CDentitionTableView.__init__(self, parent)

        h = self.fontMetrics().height()
        self.verticalHeader().setDefaultSectionSize(3 * h / 2)
        self.verticalHeader().setResizeMode(QtGui.QHeaderView.Fixed)

        w = self.geometry().width()
        self.horizontalHeader().setDefaultSectionSize(w / 2)
        self.horizontalHeader().hide()

        self.setShowGrid(True)
        self.setTabKeyNavigation(True)

        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)

        self.itemDelegate = CParodentiumItemDelegate(self)
        self.setItemDelegate(self.itemDelegate)


class CParodentiumItemDelegate(CItemDelegate):
    def __init__(self, parent):
        CItemDelegate.__init__(self, parent)

    def commit(self):
        editor = self.sender()
        self.emit(QtCore.SIGNAL('commitData(QWidget *)'), editor)

    def commitAndCloseEditor(self):
        editor = self.sender()
        self.emit(QtCore.SIGNAL('commitData(QWidget *)'), editor)
        self.emit(QtCore.SIGNAL('closeEditor(QWidget *,QAbstractItemDelegate::EndEditHint)'), editor,
                  QtGui.QAbstractItemDelegate.NoHint)

    def createEditor(self, parent, option, index):
        model = index.model()
        row = index.row()
        # if row == 4:
        #     return None
        column = index.column()
        propertyType = model.getPropertyType(row, column)
        editor = propertyType.createEditor(model.action(), parent, model.clientId)
        self.connect(editor, QtCore.SIGNAL('commit()'), self.commit)
        self.connect(editor, QtCore.SIGNAL('editingFinished()'), self.commitAndCloseEditor)
        return editor


class CParodentiumModel(QtCore.QAbstractTableModel):
    adultDefaultTeethValues = ['8', '7', '6', '5', '4', '3', '2', '1', '1', '2', '3', '4', '5', '6', '7', '8']
    colorStatus = [QtCore.Qt.white, QtCore.Qt.lightGray, QtCore.Qt.darkYellow, QtCore.Qt.cyan, QtCore.Qt.blue,
                   QtCore.Qt.green, QtCore.Qt.darkGreen, QtCore.Qt.magenta, QtCore.Qt.yellow, QtCore.Qt.red]
    teethRowTypesHeader = {
        0: u'Клиновидный дефект',
        1: u'Рецессия',
        2: u'Подвижность',
        3: u'Глубина кармана',
        4: u'Верх',
        5: u'Низ',
        6: u'Глубина кармана',
        7: u'Подвижность',
        8: u'Рецессия',
        9: u'Клиновидный дефект',
    }

    teethRowTypes = {
        0: u'Клиновидный дефект',
        1: u'Рецессия',
        2: u'Подвижность',
        3: u'Глубина кармана',
        4: u'Верх',
        5: u'Низ',
        6: u'Глубина кармана',
        7: u'Подвижность',
        8: u'Рецессия',
        9: u'Клиновидный дефект',
    }

    jawHalfTypes = {
        0: u'Верхний',
        1: u'Верхний',
        2: u'Верхний',
        3: u'Верхний',
        4: u'Верхний',
        5: u'Нижний',
        6: u'Нижний',
        7: u'Нижний',
        8: u'Нижний',
        9: u'Нижний',
    }

    def __init__(self, parent, clientDentitionHistoryModel):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._actionRecord = None
        self._action = None
        self._isExistsDentitionAction = False
        self.clientId = None
        self._isCurrentParodentiumAction = False

    def setIsExistsDentitionAction(self, isExistsDentitionAction):
        self._isExistsDentitionAction = isExistsDentitionAction

    def columnCount(self, index=QtCore.QModelIndex()):
        return 16

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(CParodentiumModel.teethRowTypes.keys())

    def getPropertyType(self, row, column):
        return self._getProperty(row, column).type()

    def setClientId(self, clientId):
        self.clientId = clientId

    def getClientId(self):
        return self.clientId

    def _getProperty(self, row, column):
        # магия в том что у каждого ActionPropertyType зубной формулы
        # имя состоит (через точку) из типа свойства по отношению к формуле,
        # части челюсти и номера с права на лево(1...16)
        # например `Подвижность.Верхний.1`
        # обращение к значениям свойст происходит через их названия.
        # по row определяется тип и часть челюсти, а номер column+1
        propertyName = self.getPropertyName(row, column)
        return self._action.getProperty(propertyName)

    @classmethod
    def getPropertyName(cls, row, column):
        propertyTeethRowType = cls.teethRowTypes[row]
        propertyJawHalfType = cls.jawHalfTypes[row]
        propertyToothIdx = unicode(column + 1)
        propertyName = u'.'.join([propertyTeethRowType, propertyJawHalfType, propertyToothIdx])
        return propertyName

    def action(self):
        return self._action

    def loadAction(self, actionRecord, action, isCurrentParodentiumAction=False):
        self._isCurrentParodentiumAction = isCurrentParodentiumAction
        self._actionRecord = actionRecord
        self._action = action
        self.reset()

    def setNullValues(self):
        self.loadAction(None, None, None)

    def isCurrentParodentiumAction(self):
        return self._isCurrentParodentiumAction

    def flags(self, index):
        row = index.row()
        column = index.column()
        if self._isCurrentParodentiumAction:
            return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Vertical:
                return QtCore.QVariant(CParodentiumModel.teethRowTypesHeader.get(section, None))
        return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()
        if not self._isExistsDentitionAction:
            return QtCore.QVariant()
        if not self._action:
            return QtCore.QVariant()
        row = index.row()
        column = index.column()
        if role == QtCore.Qt.DisplayRole:
            # if row != 4:
            property = self._getProperty(row, column)
            return toVariant(property.getText())
            # else:
            #     return toVariant(CParodentiumModel.adultDefaultTeethValues[column])
        elif role == QtCore.Qt.EditRole:
            property = self._getProperty(row, column)
            return toVariant(property.getValue())
        return QtCore.QVariant()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid():
            return False
        if not self._action:
            return False
        row = index.row()
        column = index.column()
        if role == QtCore.Qt.EditRole:
            # if row != 4:
            property = self._getProperty(row, column)
            propertyType = property.type()
            if not propertyType.isVector:
                property.setValue(propertyType.convertQVariantToPyValue(value))
                if row <= 3:
                    begIndex = self.index(0, column)
                    endIndex = self.index(4, column)
                    self.emitDataChanged(begIndex, endIndex)
                if row >= 5:
                    begIndex = self.index(4, column)
                    endIndex = self.index(8, column)
                    self.emitDataChanged(begIndex, endIndex)
                else:
                    self.emitDataChanged(index, index)
                return True
        return False

    def emitAllDataChanged(self):
        begIndex = self.index(0, 0)
        endIndex = self.index(self.rowCount() - 1, self.columnCount() - 1)
        self.emitDataChanged(begIndex, endIndex)

    def emitDataChanged(self, begIndex, endIndex):
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), begIndex, endIndex)

    def setDefaults(self):
        for row in [2]:
            for column in range(16):
                defaultValue = self._defaultValue(row, column)
                self.setData(self.index(row, column), defaultValue)

    def _defaultValue(self, row, column):
        return CParodentiumModel.adultDefaultTeethValues[column]


class CClientDentitionHistoryModel(QtCore.QAbstractTableModel):
    def __init__(self, parent):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._clientId = None
        self._currentDentitionItemRow = None
        self._currentParodentiumItemRow = None
        self._dentitionHistoryItems = []
        self._resultDentitionHistoryItems = {}
        self._actionForPaste = None

    def eventEditor(self):
        return QtCore.QObject.parent(self)

    def setActionForPaste(self, action):
        self._actionForPaste = action

    def setCurrentInspectionForPaste(self, index):
        record, action, actionId, eventId = self.getItem(index)
        self.setActionForPaste(action)

    def setCurrentResultForPaste(self, index):
        record, action, actionId, eventId = self.getResultItem(index)
        self.setActionForPaste(action)

    def getActionForPaste(self):
        return self._actionForPaste

    def currentDentitionItemRow(self):
        return self._currentDentitionItemRow

    def currentParodentiumItemRow(self):
        return self._currentParodentiumItemRow

    def clientId(self):
        return self._clientId

    def loadClientDentitionHistory(self, clientId, setDate):
        self._dentitionHistoryItems = []
        self._resultDentitionHistoryItems.clear()
        self._clientId = clientId
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        tableAction = db.table('Action')
        tableActionType = db.table('ActionType')

        cond = [
            tableEvent['client_id'].eq(clientId),
            tableEvent['deleted'].eq(0),
            tableAction['deleted'].eq(0),
            tableActionType['flatCode'].inlist([u'dentitionInspection', u'parodentInsp'])
        ]
        if setDate:
            cond.append(tableAction['begDate'].yearEq(setDate))

        queryTable = tableEvent.innerJoin(tableAction,
                                          tableAction['event_id'].eq(tableEvent['id']))
        queryTable = queryTable.innerJoin(tableActionType,
                                          tableActionType['id'].eq(tableAction['actionType_id']))
        # order  = tableAction['begDate'].name() + ' DESC' + ', ' + tableAction['event_id'].name() + ' DESC'
        order = [tableAction['id']]
        fields = 'Event.id AS eventId, ActionType.flatCode AS flatCode, Action.*'
        recordList = db.getRecordList(queryTable, fields, cond, order)
        for record in recordList:
            id = forceRef(record.value('id'))
            eventId = forceRef(record.value('eventId'))
            action = CAction(record=record)
            isChecked = 0
            self._resultDentitionHistoryItems[eventId] = (record, action, id, eventId, isChecked)
            self._dentitionHistoryItems.append((record, action, id, eventId, isChecked))
        if len(self._dentitionHistoryItems) > 0:
            self._dentitionHistoryItems.sort(key=lambda x: forceDate(x[0].value('begDate')))
            self._dentitionHistoryItems.reverse()
        self.reset()

    def addNewDentitionItem(self, newItemRecord, newItemAction):
        newItem = (newItemRecord, newItemAction, None, None, 0)
        self._dentitionHistoryItems.insert(0, newItem)
        print newItem[2]  # id
        self._currentDentitionItemRow = 0
        if self._currentParodentiumItemRow is not None:
            self._currentParodentiumItemRow += 1
        self.reset()

    def addNewParodentiumItem(self, newItemRecord, newItemAction):
        newItem = (newItemRecord, newItemAction, None, None, 0)
        self._dentitionHistoryItems.insert(0, newItem)
        self._currentParodentiumItemRow = 0
        if self._currentDentitionItemRow is not None:
            self._currentDentitionItemRow += 1
        else:
            self._currentDentitionItemRow = 1

        self.reset()

    def setCurrentDentitionItem(self, currentActionRecord, currentAction):
        currentActionId = forceRef(currentActionRecord.value('id'))
        print currentActionId
        currentEventId = forceRef(currentActionRecord.value('event_id'))
        for row, (record, action, id, currentEventId, isChecked) in enumerate(self._dentitionHistoryItems):
            if id == currentActionId:
                self._currentDentitionItemRow = row
                self._dentitionHistoryItems[row] = (
                    currentActionRecord, currentAction, currentActionId, currentEventId, isChecked)
                self.emitDataRowChanged(row)
                break
        return self._currentDentitionItemRow

    def setCurrentParodentiumItem(self, currentActionRecord, currentAction):
        currentActionId = forceRef(currentActionRecord.value('id'))
        for row, (record, action, id, currentEventId, isChecked) in enumerate(self._dentitionHistoryItems):
            if id == currentActionId:
                self._currentParodentiumItemRow = row
                self._dentitionHistoryItems[row] = (
                    currentActionRecord, currentAction, currentActionId, currentEventId, isChecked
                )
                self.emitDataRowChanged(row)
                break
        return self._currentParodentiumItemRow

    def emitDataRowChanged(self, row):
        begIndex = self.index(row, 0)
        endIndex = self.index(row, self.columnCount() - 1)
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), begIndex, endIndex)

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self._dentitionHistoryItems)

    def columnCount(self, index=QtCore.QModelIndex()):
        return 3

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                if section == 0:
                    return QtCore.QVariant(u'Печать')
                elif section == 1:
                    return QtCore.QVariant(u'Дата начала')
                elif section == 2:
                    return QtCore.QVariant(u'Дата окончания')
        return QtCore.QVariant()

    def getItem(self, index):
        row = index.row()
        return self.getItemByRow(row)

    def getResultItem(self, index):
        row = index.row()
        return self.getResultItemByRow(row)

    def getItemByRow(self, row):
        return self._dentitionHistoryItems[row]

    def getResultItemByRow(self, row):
        record, action, actionId, eventId, isChecked = self.getItemByRow(row)
        return self.getResultItemByEventId(eventId)

    def getResultItemByEventId(self, eventId):
        return self._resultDentitionHistoryItems.get(eventId, None)

    def setResultItem(self, record, action, actionId, eventId, isChecked):
        self._resultDentitionHistoryItems[eventId] = (record, action, actionId, eventId, isChecked)

    def items(self):
        return self._dentitionHistoryItems

    def flags(self, index):
        column = index.column()
        if column == 0:
            return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled
        else:
            return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()
        row = index.row()
        column = index.column()
        record, action, id, eventId, isChecked = self._dentitionHistoryItems[row]
        if role == QtCore.Qt.DisplayRole:
            if column == 1:
                val = forceDate(record.value('begDate'))
            elif column == 2:
                val = forceDate(record.value('endDate'))
            else:
                return QtCore.QVariant()
            return QtCore.QVariant(val.toString(QtCore.Qt.LocaleDate))
        elif role == QtCore.Qt.CheckStateRole:
            if column == 0:
                return toVariant(QtCore.Qt.Unchecked if isChecked == 0 else QtCore.Qt.Checked)
        elif role == QtCore.Qt.ForegroundRole:
            if self.isCurrentDentitionAction(row):
                return QtCore.QVariant(QtGui.QColor(0, 0, 255))
            elif self.isCurrentParodentiumAction(row):
                return QtCore.QVariant(QtGui.QColor(90, 0, 157))
        else:
            return QtCore.QVariant()
        return QtCore.QVariant()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        column = index.column()
        row = index.row()
        if role == QtCore.Qt.CheckStateRole:
            if column == 0:
                record, action, id, eventId, isChecked = self._dentitionHistoryItems[row]
                if forceInt(value) == 2:
                    isChecked = 1
                elif forceInt(value) == 0:
                    isChecked = 0
                self._dentitionHistoryItems[row] = (record, action, id, eventId, isChecked)
                return True
        return False

    def isCurrentDentitionAction(self, row):
        return row == self._currentDentitionItemRow

    def isCurrentParodentiumAction(self, row):
        return row == self._currentParodentiumItemRow
