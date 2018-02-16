# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2014 Vista Software. All rights reserved.
##
#############################################################################

import re

import sip
from PyQt4 import QtCore, QtSql, QtGui, QtXml
from math import ceil

from library.CheckedHeaderView                  import CCheckedHeaderView
from library.TableModel import CTextCol
from library.database                           import connectDataBaseByInfo, CTableRecordCache, CDatabase
from library.exception import CDatabaseException
from library.QueryFilter.QueryFilterDelegate    import CQueryFilterDelegate
from library.QueryFilter.QueryFilterItemModel   import CQueryFilterItemModel
from library.TableView                          import CTableView
from library.Utils                              import forceStringEx, forceInt, forceRef, readNextStartXMLElement, \
                                                       readXMLElementText, skipCurrentXMLElement, forceString, getPref,\
                                                       setPref

from Registry.RegistryTable                     import CClientsTableModel
from Registry.Ui_CustomizableRegistryWidget     import Ui_CustomizableRegistryWidget

'''
Created on 13.01.2014

@author: atronah
'''

#TODO: atronah: list of todo is below:
#[low] Сделать умную строку поиска, для чего для запроса определять поля, в которые будут подставляться сущности из строки.
#[low] Вынести в отдельный виджет контролы переключения страниц (с коммуникацией через сигналы-слоты с основным отображающим виджетом) 
#[low] Разбить код на модули


## Модель настройки отображения столбцов
class CShowedColumnModel(QtCore.QAbstractListModel):
    def __init__(self, parent):
        super(CShowedColumnModel, self).__init__(parent)
        self._items = []
        self._isDirty = False
        self.dataChanged.connect(self.setAsDirty)
    
    
    def setDirty(self, isDirty):
        self._isDirty = isDirty
    
    
    @QtCore.pyqtSlot()
    def setAsDirty(self):
        self.setDirty(True)
        
    
    def isDirty(self):
        return self._isDirty
    
    
    def flags(self, index):
        if index.isValid() and index.row() in xrange(self.rowCount()):
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable
        
        return super(CShowedColumnModel, self).flags(index)
    
    
    ## Возвращает количество строк модели
    def rowCount(self, parent = QtCore.QModelIndex()):
        return len(self._items)
    
    
    ## Возвращает количество столбцов модели
    def columnCount(self, parent = QtCore.QModelIndex()):
        return 1
    
    
    ## Очистка модели
    def clear(self):
        self.beginRemoveRows(QtCore.QModelIndex(), 0, self.rowCount() - 1)
        self._items = []
        self.endRemoveRows()
        
        
    ## Добавляет новый элемент в список
    def addItem(self, name, title, checkState = True, idx = None):
        if idx is None:
            idx = self.rowCount()
        
        if idx not in xrange(self.rowCount() + 1):
            return
        self.beginInsertRows(QtCore.QModelIndex(), idx, idx)
        self._items.insert(idx, [checkState, title, name])
        self.endInsertRows()
        
    
    ## Проверка состояния элемента в строке
    def isChecked(self, row):
        if row in xrange(self.rowCount()):
            return self._items[row][0]
        
        return True
    
    
    ## Изменение состояния элемента
    def setChecked(self, row, value):
        if row in xrange(self.rowCount()):
            self.setData(self.index(row, 0), 
                         QtCore.Qt.Checked if value else QtCore.Qt.Unchecked, 
                         role = QtCore.Qt.CheckStateRole)
            
            
    ## Изменяет состояние всех элементов
    @QtCore.pyqtSlot(bool)
    def setAllChecked(self, isChecked):
        for row in xrange(self.rowCount()):
            self.setChecked(row, isChecked)
    
    
    ## Возвращает данные по указанному элементы (имя или состояние)
    def data(self, index, role = QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()
        
        row = index.row()
        if row not in xrange(self.rowCount()):
            return QtCore.QVariant()
        
        if role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self._items[row][1])
        elif role == QtCore.Qt.CheckStateRole:
            return QtCore.QVariant(QtCore.Qt.Checked if self._items[row][0] else QtCore.Qt.Unchecked)
        
        return QtCore.QVariant()
    
    ## Изменение данных модели
    def setData(self, index, value, role = QtCore.Qt.EditRole):
        if not index.isValid():
            return False
        
        row = index.row()
        if row not in xrange(self.rowCount()):
            return False
        
        if role == QtCore.Qt.CheckStateRole:
            self._items[row][0] = (value == QtCore.Qt.Checked)
            self.dataChanged.emit(index, index)
            return True
            
        return False
        
    
    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if section in xrange(self.columnCount()):
                if role ==  QtCore.Qt.CheckStateRole:
                    return QtCore.QVariant(QtCore.Qt.Checked)
                elif role == QtCore.Qt.DisplayRole:
                    return QtCore.QVariant()
        return QtCore.QVariant()
    
    
    def checkStates(self):
        return dict([(name, QtCore.Qt.Checked if isChecked else QtCore.Qt.Unchecked) for isChecked, _, name in self._items])
    
    
    def updateCheckStates(self, statesDict):
        for row, item in enumerate(self._items):
            itemName = QtCore.QString(item[2])
            if statesDict.has_key(itemName):
                index = self.index(row, 0)
                if isinstance(statesDict[itemName], bool):
                    checkState = QtCore.Qt.Checked if statesDict[itemName] else QtCore.Qt.Unchecked
                else:
                    checkState = QtCore.Qt.Checked if statesDict[itemName] == QtCore.Qt.Checked else QtCore.Qt.Unchecked
                self.setData(index, checkState, QtCore.Qt.CheckStateRole)



class CAbstractRegistryWidget(QtGui.QWidget):
    requestNewEvent = QtCore.pyqtSignal()
    currentClientChanged = QtCore.pyqtSignal()
    

    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self._viewWidget = None
        self._model = None
        self._selectionModel = None
        
        
    def initContent(self, view, model):
        if not(isinstance(view, CTableView) and isinstance(model, QtCore.QAbstractItemModel)):
            return False
        
        self._viewWidget = view
        self._model = model
        self._selectionModel = QtGui.QItemSelectionModel(self._model, self)
        self._selectionModel.currentRowChanged.connect(self.currentClientChanged)
        self._viewWidget.setModel(model)
        self._viewWidget.setSelectionModel(self._selectionModel)
        self._viewWidget.installEventFilter(self)
        self._viewWidget.setColumnSelectionEnabled(True)

        return True
        
    
    def model(self):
        return self._model
    
    
    def selectionModel(self):
        return self._selectionModel
    
    
    def viewWidget(self):
        return self._viewWidget
    
    
    def eventFilter(self, watched, event):
        if isinstance(watched, CTableView):
            if event.type() == QtCore.QEvent.KeyPress:
                if event.key() == QtCore.Qt.Key_Space:
                    event.accept()
                    self.requestNewEvent.emit()
                    return True

        return QtGui.QWidget.eventFilter(self, watched, event)
    
    
#    def setCurrentItemId(self, itemId):
#        if isinstance(self.viewWidget(), CTableView):
#            self.viewWidget().setCurrentItemId(itemId)
#    
#    
#    def currentItemId(self):
#        if isinstance(self.viewWidget(), CTableView):
#            return self.viewWidget().currentItemId()
#        return None
#    
#    
#    def idList(self):
#        if isinstance(self.viewWidget(), CTableView):
#            return self.viewWidget().idList()
#        return None
#    
#    
#    def setIdList(self, idList):
#        if isinstance(self.viewWidget(), CTableView):
#            self.viewWidget().setIdList(idList)


class CStandardRegistryWidget(CAbstractRegistryWidget):
    def __init__(self, parent = None):
        CAbstractRegistryWidget.__init__(self, parent)
        
        tableView = CTableView(self)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(tableView)
        
        self.setLayout(layout)
        
        self.initContent(tableView,
                         CClientsTableModel(self))
        

class CCustomizableRegistryWidget(CAbstractRegistryWidget, Ui_CustomizableRegistryWidget):
#    idxFilterItemPage = 0
#    idxOperatorPage = 1
#    idxValuesPage = 2

    idxRegistryTab = 0
    idxFiltersTab = 1
    
    showedPrefName = u'showedRegistryColumns'
    
    def __init__(self, parent = None):
        CAbstractRegistryWidget.__init__(self, parent)
        self.setupUi(self)

        self._sourceFileName = None
        self._doc = None
        
        model = CCustomizableRegistryModel(database = QtGui.qApp.db)
        model.startUpdating.connect(self.waitUpdating)
        model.endUpdating.connect(self.updateStates)
        # model.columnsInserted.connect(self.updateHeaderData)
        # model.columnsRemoved.connect(self.updateHeaderData)
        
        self.sbCurrentPage.setValue(model.currentPage())
        
        self.initContent(self.tblView,
                         model)
        self.viewWidget().setSortingEnabled(True)
        self.viewWidget().clicked.connect(self.viewCellClicked)
        self.viewWidget().verticalHeader().setVisible(True)
        self.viewWidget().horizontalHeader().sectionResized.connect(self.saveColumnWidth)
        self.viewWidget().setEditTriggers(QtGui.QAbstractItemView.AllEditTriggers)

        self.viewWidget().initFreeze(count = model.filterRowCount(), color = QtGui.QColor(u'cyan'))
        self.viewWidget().frozenView().installEventFilter(self)


        self.tvFilterItem.setModel(self.model().filterItemModel())
        self.tvFilterItem.setItemDelegate(CQueryFilterDelegate(self.tvFilterItem))
        self.tvFilterItem.horizontalHeader().setStretchLastSection(True)
        self.tvFilterItem.installEventFilter(self)
#        self.tvFilterItem.selectionModel().currentChanged.connect(self.filterItemChanged)
        self.tvViewSettings.setModel(self.model().showedColumnModel())
        headerView = CCheckedHeaderView(QtCore.Qt.Horizontal, self)
        headerView.setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.tvViewSettings.setHeader(headerView)
        headerView.setCheckable(0, True, True)
        headerView.toggled.connect(self.model().showedColumnModel().setAllChecked)
        
        
        self.sbCurrentPage.installEventFilter(self)
        
        # Список виджетов для реализации быстрых фильтров вида "да"/"нет" под основной таблицей
        self._quickFilterWidgetList = []
        

        self.model().showedColumnModel().dataChanged.connect(self.resetSavedSettingsIndex)
        self.loadSavedShowSettings()



    def eventFilter(self, obj, event):
        if obj == self.tvFilterItem:
            if event.type() == QtCore.QEvent.KeyPress:
                if event.key() in [QtCore.Qt.Key_Backspace, 
                                   QtCore.Qt.Key_Delete]:
                    self.tvFilterItem.model().clearValue(self.tvFilterItem.currentIndex())
        if obj == self.tblView.frozenView() and event.type() == QtCore.QEvent.KeyPress:
            if (event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]
                and self.tblView.frozenView().currentIndex().row() in xrange(self.model().filterRowCount())
            ):
                self.model().updateContent()
        elif obj == self.sbCurrentPage:
                if event.type() == QtCore.QEvent.KeyPress and event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
                      #or ) # срабатывает, когда происходит смена страницы в коде.
                    self.model().setCurrentPage(self.sbCurrentPage.value())
                elif event.type() == QtCore.QEvent.FocusOut:
                    self.sbCurrentPage.setValue(self.model().currentPage())
        return super(CCustomizableRegistryWidget, self).eventFilter(obj, event)
                
    
    @QtCore.pyqtSlot()
    def resetSavedSettingsIndex(self):
        self.cmbSavedSettings.setCurrentIndex(-1)


    @QtCore.pyqtSlot(int, int, int)
    def saveColumnWidth(self, logicalIndex, oldSize, newSize):
        if newSize == 0:
            return
        self.model().headerList()[logicalIndex][2] = newSize

        if abs(oldSize - newSize) < 3:
            return
        if self._sourceFileName is None:
            return

        if self._doc is None:
            self._doc = QtXml.QDomDocument()
            sourceFile = QtCore.QFile(self._sourceFileName)
            if not sourceFile.open(QtCore.QFile.ReadOnly):
                return
            try:
                self._doc.setContent(sourceFile, False)
            finally:
                sourceFile.close()
        root = self._doc.documentElement()

        if root.tagName() != self.model()._xmlRegistryTagName:
            return
        queryElement = root.firstChildElement(self.model()._xmlQueryTagName)
        if queryElement.isNull():
            return

        selectElement = queryElement.firstChildElement(u'select')
        if selectElement.isNull():
            return

        fieldElement = selectElement.firstChildElement('field')
        while not fieldElement.isNull():
            alias = forceString(fieldElement.attribute('alias'))
            columnIdx = self.model().columnIndexByAlias(alias)
            columnWidth = self.viewWidget().columnWidth(columnIdx)
            fieldElement.setAttribute('width', '%s' % columnWidth)
            fieldElement = fieldElement.nextSiblingElement('field')


        # with open(self._sourceFileName, 'w') as outFile:
        #     outFile.write(unicode(self._doc.toString(4), 'windows-1251', errors='ignore'))
        #
        sourceFile = QtCore.QFile(self._sourceFileName)
        if not sourceFile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
            return
        try:
            outStream = QtCore.QTextStream(sourceFile)
            outStream.setCodec('UTF-8')
            outStream << self._doc.toString(4).replace('&#xd;', '')
        finally:
            sourceFile.close()

    
    def activateFiltersTab(self):
        self.tabWidget.setCurrentIndex(self.idxFiltersTab)
        
    
    def loadSavedShowSettings(self):
        self.cmbSavedSettings.clear()
        if hasattr(QtGui.qApp, "preferences"):
            for name, checkStates in getPref(QtGui.qApp.preferences.appPrefs, self.showedPrefName, QtCore.QVariant.fromMap({})).toMap().items():
                self.cmbSavedSettings.addItem(name, checkStates)
        self.cmbSavedSettings.setCurrentIndex(-1)
        
        
        
    def saveSavedShowSettings(self):
        if hasattr(QtGui.qApp, "preferences"):
            savedInfo = {}
            for idx in xrange(self.cmbSavedSettings.count()):
                name = self.cmbSavedSettings.itemText(idx)
                states = self.cmbSavedSettings.itemData(idx)
                savedInfo[name] = states
            setPref(QtGui.qApp.preferences.appPrefs, self.showedPrefName, QtCore.QVariant.fromMap(savedInfo))

    
    def setSource(self, xmlSource):
        if not isinstance(xmlSource, (QtCore.QIODevice, QtCore.QString)):
            return False

        if isinstance(xmlSource, QtCore.QFile):
            self._sourceFileName = xmlSource.fileName()
        
        self.model().parseRegistryXML(xmlSource)
        # self.model().updateContent()
        
        if isinstance(xmlSource, QtCore.QIODevice):
            xmlSource.reset()

        self.initQuickFilters()
        
        
    ## Инициализирует быстрые фильтры вида "да/нет", отображаемые под таблицей картотеки
    def initQuickFilters(self):
        while self._quickFilterWidgetList:
            checkWidget = self._quickFilterWidgetList.pop(0)
            checkWidget.toggled.disconnect(self.updateQuickFilterStates)
            self.quickFilterLayout.removeWidget(checkWidget)
            sip.delete(checkWidget)
        
        
        for caption, _, checkState in self.model().quickFilterList():
            checkWidget = QtGui.QCheckBox(caption, self)
            checkWidget.setChecked(checkState)
            checkWidget.toggled.connect(self.updateQuickFilterStates)
            self._quickFilterWidgetList.append(checkWidget)
            self.quickFilterLayout.addWidget(checkWidget)
        return True
    
    
    ## Обновляет состояние быстрых фильтров 
    @QtCore.pyqtSlot()
    def updateQuickFilterStates(self):
        for idx, checkWidget in enumerate(self._quickFilterWidgetList):
            self.model().setQuickFilterState(idx, checkWidget.isChecked())
        self.model().updateContent()
            
    
    
    
    def updateNavigationButtonsState(self):
        canPrevPage = self._model.canPrevPage()
        self.btnBegin.setEnabled(canPrevPage)
        self.btnPrevious.setEnabled(canPrevPage)
        canNextPage = self._model.canNextPage()
        self.btnNext.setEnabled(canNextPage)
        self.btnEnd.setEnabled(canNextPage)
        
    
    #Для предотвращения повторных нажатий из-за нервозности пользователя, ждущего выполнение запроса.
    def disableUi(self):
        self.viewWidget().setEnabled(False)
        self.btnBegin.setEnabled(False)
        self.btnPrevious.setEnabled(False)
        self.btnNext.setEnabled(False)
        self.btnEnd.setEnabled(False)
        self.sbCurrentPage.setEnabled(False)
        self.btnUpdate.setEnabled(False)
        self.btnReset.setEnabled(False)
        
    
    @QtCore.pyqtSlot()
    def waitUpdating(self):
        self.disableUi()
        self.lblElementsCountInfo.setText(u'(Выполнение запроса...)')
        # QtGui.qApp.processEvents(flags = QtCore.QEventLoop.ExcludeUserInputEvents | QtCore.QEventLoop.ExcludeSocketNotifiers)
    
    
    def updateInfoState(self):
        self.sbCurrentPage.setEnabled(True)
        self.sbCurrentPage.setValue(self._model.currentPage())
        self.sbCurrentPage.setMaximum(self._model.totalPageCount())
        self.sbCurrentPage.setMinimum(min(1, self._model.totalPageCount()))
        self.lblTotalPages.setText(forceStringEx(self._model.totalPageCount()))
        recordsInterval = self._model.recordsInterval()
        self.lblElementsCountInfo.setText(u'(%s - %s из %s записей)' % (recordsInterval[0],
                                                                        recordsInterval[1],
                                                                        self._model.totalRowCount(False)))
   
    @QtCore.pyqtSlot()
    def updateStates(self):
        self.viewWidget().setEnabled(True)
        self.updateNavigationButtonsState()
        self.updateInfoState()
        self.btnUpdate.setEnabled(True)
        self.btnReset.setEnabled(True)
        for column in xrange(self._model.columnCount()):
            self._model.setHeaderData(column, QtCore.Qt.Horizontal, QtCore.QVariant(self._model.headerName(column)))
            width = self._model.headerList()[column][2]
            if width is not None:
                self.viewWidget().setColumnWidth(column, width)
            if self._model.isColumnHidden(column):
                self.viewWidget().hideColumn(column)
            else:
                self.viewWidget().showColumn(column)
        self.viewWidget().selectRow(0)
        for row in xrange(self.model().filterRowCount()):
            self.viewWidget().setRowHeight(row, 26)




    # @QtCore.pyqtSlot()
    # def updateHeaderData(self):
    #     for column in xrange(self._model.columnCount()):
    #         self._model.setHeaderData(column, QtCore.Qt.Horizontal, QtCore.QVariant(self._model.headerName(column)))
    #
    
    
    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def viewCellClicked(self, index):
        pass
        # if self.model().isInlineFiltersChanged():
        #     if (#Если полльзователь сменил строку со строки с фильтрами, на любую другую
        #         index.row() not in xrange(self.model().filterRowCount())
        #         #Или, если модель пуста
        #         or self.model().rowCount() <= self.model().filterRowCount()
        #         ):
        #         self.model().updateContent()
            
    
    
    @QtCore.pyqtSlot()
    def on_btnBegin_clicked(self):
        self._model.beginPage()

    
    @QtCore.pyqtSlot()
    def on_btnPrevious_clicked(self):
        self._model.prevPage()
        
    
    @QtCore.pyqtSlot()
    def on_btnNext_clicked(self):
        self._model.nextPage()
        
    
    @QtCore.pyqtSlot()
    def on_btnEnd_clicked(self):
        self._model.endPage()
        
        
    
    @QtCore.pyqtSlot(int)
    def on_cmbSavedSettings_currentIndexChanged(self, newIdx):
        if newIdx >= 0 :
            checkStates = self.cmbSavedSettings.itemData(newIdx).toMap()
            self.model().showedColumnModel().dataChanged.disconnect(self.resetSavedSettingsIndex)
            self.model().showedColumnModel().updateCheckStates(checkStates)
            self.model().showedColumnModel().dataChanged.connect(self.resetSavedSettingsIndex)
        
    
    @QtCore.pyqtSlot()
    def on_btnSaveSettings_clicked(self):
        currentText = self.cmbSavedSettings.currentText()
        if currentText.trimmed().isEmpty():
            currentText = QtCore.QString(u'Без имени')
            
        idx = self.cmbSavedSettings.findText(currentText)
        if idx == -1:
            self.cmbSavedSettings.addItem(currentText,
                                          QtCore.QVariant.fromMap(self.model().showedColumnModel().checkStates()))
        else:
            self.cmbSavedSettings.setItemData(idx, 
                                              QtCore.QVariant.fromMap(self.model().showedColumnModel().checkStates()))
        self.saveSavedShowSettings()
    
    
    @QtCore.pyqtSlot()
    def on_btnDelSettings_clicked(self):
        idx = self.cmbSavedSettings.findText(self.cmbSavedSettings.currentText())
        if idx != -1:
            self.cmbSavedSettings.removeItem(idx)
        self.saveSavedShowSettings()
        self.cmbSavedSettings.setCurrentIndex(idx)
    
    
#     @QtCore.pyqtSlot()
#     def on_sbCurrentPage_editingFinished(self):


#    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
#    def filterItemChanged(self, current, previous):
#        if current != previous:
#            if self.lvFilterOperator.selectionModel():
#                self.lvFiltgerOperator.selectionModel().currentChanged.disconnect(self.filterOperatorChanged)
#            self.lvFilterOperator.setModel(current.model().filterItem(current).operatorModel())
#            self.lvFilterOperator.selectionModel().currentChanged.connect(self.filterOperatorChanged)
            
            
#    
#    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
#    def filterOperatorChanged(self, current, previous):
#        operator = current.model().operator(current)
#        valueCount = operator.valueCount()
#        self._valuesModel.clear()
#        filterItemIndex = self.lvFilterItem.selectionModel().currentIndex()
#        filterItem = filterItemIndex.model().filterItem(filterItemIndex)
#        if valueCount == -1:
#            valueCount = 1
#        while valueCount > 0:
#            valueCount -= 1
#            self._valuesModel.addItem(CTemplateParameter(name = unicode(self._valuesModel.rowCount()),
#                                                         caption = u'',
#                                                         typeName = filterItem.valueTypeName()))
#        self.filterItemOptions.setCurrentIndex(self.idxValuesPage)
        
            
            
#    @QtCore.pyqtSlot()
#    def on_btnAddFilterItem_clicked(self):
#        valueList = [item.stringValue() for item in self._valuesModel.items()]
#        self._userFilterItemModel.addContraint(filterItemIndex = self.lvFilterItem.currentIndex(), 
#                                               filterOperatorIndex = self.lvFilterOperator.currentIndex(), 
#                                               valueList = valueList)
        
        
    @QtCore.pyqtSlot(int)
    def on_tabWidget_currentChanged(self, idx):
        if idx == self.idxRegistryTab and (self.model().filterItemModel().isDirty()
                                           or self.model().showedColumnModel().isDirty()):
            self.model().updateContent()
            
    
    @QtCore.pyqtSlot()    
    def on_btnUpdate_clicked(self):
        self.model().updateContent()


    @QtCore.pyqtSlot()
    def on_btnReset_clicked(self):
        self.viewWidget().horizontalHeader().setSortIndicator(-1, QtCore.Qt.AscendingOrder)
        self.model().filterItemModel().resetFilters()
        for idx, (_, isHidden, _, _) in enumerate(self.model().headerList()):
            self.model().showedColumnModel().setChecked(idx, not isHidden)
            for row in xrange(self.model().filterRowCount()):
                self.model().setData(self.model().index(row, idx), QtCore.QVariant(u''))
        if not self.model().beginPage():
            self.model().updateContent()

            
    


class CCustomizableRegistryModel(QtSql.QSqlQueryModel):
    sourceFileName = u'registry.xml'
    recordsPerPage = 100
    
    _xmlRegistryTagName = 'registry'
    _xmlQueryTagName = 'query'
    
    _filterRowCount = 1
    
    startUpdating = QtCore.pyqtSignal()
    endUpdating = QtCore.pyqtSignal()

    pageChanged = QtCore.pyqtSignal(int, int)
    
    #TODO: atronah: возможно стоит брать(парсить) из блока FROM запроса.. 
    #Хотя данный класс подразумевает работу именно с таблицей Client (точнее, что Сlient.id всегда будет первым полем в результате)
    _mainTableName = u'Client'
    #-------------- special methods block
    def __init__(self, database, parent = None):
        QtSql.QSqlQueryModel.__init__(self, parent)
        self._sourceFile = None
        self._headerList = []
        self._selectFieldList = []
        self._filterByColumns = {}
        self._fromBlock = u''
        self._whereBlock = u''
        self._orderBlock = u''
        self._sortBlock = u''
        self._db = database
        self._lastTotalRowCount = 1
        self._currentPage = 1
       
        self._colorFieldAlias = None
       
        self._quickFilterList = []
        
        self._userFilterItemConditionList = []
        
        self._showedColumnModel = CShowedColumnModel(self)
        
        self._recordsCache = CTableRecordCache(self._db, 
                                               self._db.forceTable(self._mainTableName)) #for compability with CTableView
        
        self._filterItemModel = CQueryFilterItemModel()
        self._isInlineFiltersChanged = False

        self.pageChanged.connect(self.updateAfterChangingPage)
        self.vipList = []

    def cols(self):
        return [CTextCol(title = self.headerData(column, orientation=QtCore.Qt.Horizontal),
                         fields = [self.record().fieldName(column)],
                         defaultWidth=self.headerList()[column][2],
                         alignment=self.headerList()[column][3])
                for column in xrange(self.columnCount())]

        
    def isInlineFiltersChanged(self):
        return self._isInlineFiltersChanged
    
    
    ## Меняет индекс с учетом строк фильтрации
    def correctIndex(self, index):
        return self.index(index.row() - self._filterRowCount,
                          index.column(), 
                          index.parent())
    
    
    def filterRowCount(self):
        return self._filterRowCount
    #-------------- end of special methods block
    
    #-------------- re-implemented block
    def rowCount(self, parentIndex = QtCore.QModelIndex()):
        return super(CCustomizableRegistryModel, self).rowCount(parentIndex) + self._filterRowCount
    
    
    def flags(self, index):
        if index.row() in xrange(self._filterRowCount):
            return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled

        return super(CCustomizableRegistryModel, self).flags(self.correctIndex(index))
    
    
    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Vertical:
            if section in xrange(self.filterRowCount()):
                if role == QtCore.Qt.DecorationRole:
                    return QtCore.QVariant(QtGui.QPixmap(u':/new/prefix1/icons/filter-icon.png'))
                elif role == QtCore.Qt.DisplayRole:
                    return QtCore.QVariant(u'')
                # elif role == QtCore.Qt.SizeHintRole:
                #     return QtCore.QVariant(QtCore.QSize(50, 50))
            elif section in xrange(self.rowCount()):
                if role == QtCore.Qt.DisplayRole:
                    return QtCore.QVariant(u'%s' % section)
        return super(CCustomizableRegistryModel, self).headerData(section, orientation, role)
    
    
    def data(self, index, role = QtCore.Qt.DisplayRole):
        if index.isValid() and index.row() in xrange(self._filterRowCount):
            if role in [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole]:
                column = index.column()
                condition = self._filterByColumns.setdefault(column, [u''] * self._filterRowCount)[index.row()]
                return QtCore.QVariant(condition)
            elif role == QtCore.Qt.BackgroundRole:
                return QtCore.QVariant(QtGui.QColor('#7fffd4'))
            # elif role == QtCore.Qt.SizeHintRole:
            #     return QtCore.QVariant(QtCore.QSize(50, 50))

        elif role == QtCore.Qt.BackgroundRole and index.isValid() and self.colorFieldAlias():
            record = self.record(index.row())
            if record and record.contains(self.colorFieldAlias()):
                colorName = forceStringEx(record.value(self.colorFieldAlias()))
                if colorName:
                    return QtCore.QVariant(QtGui.QColor(colorName))

        elif role == QtCore.Qt.TextAlignmentRole:
            align = self._headerList[index.column()][3]
            return QtCore.QVariant(QtCore.Qt.AlignLeft if align == 'l'
                                                       else QtCore.Qt.AlignRight if align == 'r'
                                                                                 else QtCore.Qt.AlignCenter)

        return super(CCustomizableRegistryModel, self).data(self.correctIndex(index), role)
    
    
    def setData(self, index, value, role = QtCore.Qt.EditRole):
        if index.isValid() and index.row() in xrange(self._filterRowCount) and role == QtCore.Qt.EditRole:
            column = index.column()
            stringValue = forceString(value)
            oldValue = self._filterByColumns.setdefault(column, [u''] * self._filterRowCount)[index.row()]
            if stringValue != oldValue:
                self._filterByColumns[column][index.row()] = stringValue
                self.dataChanged.emit(index, index)
                self._isInlineFiltersChanged = True
                return True
        return super(CCustomizableRegistryModel, self).setData(self.correctIndex(index), value, role)
    
    #-------------- end of re-implemented block
        
    
    #-------------- interface block
    def table(self):
        return self._db.forceTable(self._mainTableName) if self._db else None
    
    
    def recordCache(self):
        return self._recordsCache
    
    
    def itemId(self, index):
        if index.row() in xrange(self._filterRowCount):
            return None
        return forceRef(self.index(index.row(), 0).data())
    
    
    def idList(self):
        return [self.itemId(self.index(row, 0)) for row in xrange(self.rowCount())]


    def headerList(self):
        return self._headerList
    
    
    ## Добавляет пользовательское условие для ограничения выборки
    def addUserCondition(self, filterItemCondition):
        if isinstance(filterItemCondition, QtCore.QString):
            filterItemCondition = forceStringEx(filterItemCondition)
        
        if not isinstance(filterItemCondition, basestring):
            return False
        
        self._userFilterItemConditionList.append(filterItemCondition)
        return True
    
    
    ## Добавляет список пользовательских условий для ограничения выборки
    def addUserConditionList(self, filterItemConditionList):
        if not isinstance(filterItemConditionList, list):
            return False
        
        for filterItemCondition in filterItemConditionList:
            self.addUserFilterItemCondition(filterItemCondition)


    def clearUserConditionList(self):
        self._userFilterItemConditionList = []
    
    
    ## Загружает основные, видимые под основной таблицей картотеки, фильтры-галочки из XML
    def loadQuickFilterListFromXML(self, source):
        self._quickFilterList = []
        
        xmlListTagName = u'generalCheckFilterList'
        xmlCheckFilterTagName = u'generalCheckFilter'
        xmlCaprionAttrName = u'caption'
        doc = QtXml.QDomDocument()
        if doc.setContent(source)[0]:
            checkFilterListElements = doc.elementsByTagName(xmlListTagName)
            for checkFilterListIdx in xrange(checkFilterListElements.count()):
                checkFilterListElement = checkFilterListElements.at(checkFilterListIdx).toElement()
                if checkFilterListElement:
                    checkFilterElements = checkFilterListElement.elementsByTagName(xmlCheckFilterTagName)
                    for checkFilterIdx in xrange(checkFilterElements.count()):
                        checkFilterElement = checkFilterElements.at(checkFilterIdx).toElement()
                        if checkFilterElement:
                            caption = checkFilterElement.attribute(xmlCaprionAttrName, u'???')
                            expression = unicode(checkFilterElement.text())
#                            checkWidget = QtGui.QCheckBox(caption, self)
                            self._quickFilterList.append([caption, expression, False])
#                            self.generalCheckFilterLayout.addWidget(checkWidget)
        return True
    
    
    ## Возвращает список простых фильтров вида "да/нет"
    def quickFilterList(self):
        return self._quickFilterList
    
    
    ## Обновляет/установливает состояние для простого фильтра с указанным индексом  
    def setQuickFilterState(self, idx, checkState):
        if idx in xrange(len(self._quickFilterList)):
            self._quickFilterList[idx][2] = checkState
            
    
    def showedColumnModel(self):
        return self._showedColumnModel
    
    
    
    def filterItemModel(self):
        return self._filterItemModel 
    
    
    def headerName(self, section):
        if section in xrange(len(self._headerList)):
            return self._headerList[section][0] or self._selectFieldList[section][1]
        return u'-'
        
    
    def isColumnHidden(self, column):
        if column in xrange(len(self._headerList)):
            return not self._showedColumnModel.isChecked(column)
        return True
    
        
    def sort(self, column, order):
        fieldName = self.record().fieldName(column)
        if fieldName:
            self._sortBlock = u"`%s` %s" % (fieldName,
                                            u'ASC' if order == QtCore.Qt.AscendingOrder else u'DESC')
            self.updateContent()
    
    
    ## Возвращает номер первой и последней отображаемой в модели записи в виде кортежа.
    def recordsInterval(self):
        startRecordIdx = (self._currentPage - 1) * self.recordsPerPage
        totalRowCount = self.totalRowCount(False)
        return (min(startRecordIdx + 1, totalRowCount),
                min(startRecordIdx + self.recordsPerPage, totalRowCount)) 
    
    
    def totalPageCount(self):
        #atronah: может будет лучше так:
        # (self.totalRowCount(False)  + (self.recordsPerPage - 1))/ self.recordsPerPage
        return int(ceil(self.totalRowCount(False) / float(self.recordsPerPage)))
    
    
    def totalRowCount(self, forceUpdate = False):
        if forceUpdate:
            query = self._db.query(self.queryStmt(True))
            if query.first():
                record = query.record()
                self._lastTotalRowCount = forceInt(record.value(0))
        return self._lastTotalRowCount
    
    
    def canPrevPage(self):
        return self._currentPage > 1
    
    
    def canNextPage(self):
        return self.currentPage() < self.totalPageCount()
    
    
    def currentPage(self):
        return self._currentPage
    
    
    def getColumnInCellCondition(self, column):
        if not self._filterByColumns.has_key(column):
            return None
        
        fieldName, alias = self._selectFieldList[column]
        conditionList = []
        for columnFilter in self._filterByColumns[column]:
            for filterPart in columnFilter.split(','):
                filterPart = filterPart.strip()
                if not filterPart:
                    continue
                filterPart, isNot = re.subn(ur'^НЕ\s(.*)', ur'\1', filterPart)
                notModifier = u'NOT ' if isNot else u''
                #Преобразование шаблонов вида "12 -- 44" или "ОТ 12 ДО 44" в выражение BETWEEN 12 AND 44
                filterPart, isBetween = re.subn(ur'\s*(ОТ )*\s*((?:\s*\S+)+)\s*(?(1) ДО |--)\s*(.+)\s*', ur"BETWEEN '\2' AND '\3'", filterPart)
                if not isBetween:
                    filterPart = u"LIKE '%s'" % filterPart

                fieldType = self.record().field(alias).type()
                if fieldType == QtCore.QVariant.String:
                    filterPart = filterPart.replace(u'*', u'%').replace(u'?', u'_')
                elif fieldType in [QtCore.QVariant.Date, QtCore.QVariant.DateTime]:
                    # Преобразование даты в формате dd.MM.yy и dd.MM.yyyy в ISO-формат yyyy-MM-dd
                    filterPart = re.sub(ur'(\d{2}).(\d{2}).(\d{2,4})',
                                        lambda m: u'%s-%s-%s' % (m.group(3) if len(m.group(3)) == 4\
                                                                            else '20' + m.group(3) if int(m.group(3)) < 50\
                                                                                                   else '19' + m.group(3),
                                                                 m.group(2),
                                                                 m.group(1)),
                                        filterPart)
                    # Преобразование даты и времени вида "yyyy-MM-dd hh:mm" в ISO-формат "yyyy-MM-ddThh:mm:00"
                    filterPart = re.sub(ur'(\d{4}-\d{2}-\d{2})\s(\d{2}:\d{2})', ur'\1T\2:00', filterPart)

                conditionList.append(u'%s %s%s' % (fieldName, notModifier, filterPart))
        return CDatabase.joinOr(conditionList) if conditionList else None
        
    
    
    def queryStmt(self, isCountStmt = False):
        #TODO: atronah: возможно правильнее будет использовать группу функций QSqlTableModel.setTable, setFilter и т.п. вместо готового запроа.
        #Хотя вряд ли, так как тогда непонятно, как передать список нужных столбцов и не думаю, что setTable работает с JOIN'ами
        
        stmtParts = []
        
        #Генерация блока SELECT
        selectParts = []
        inCellFilters = []
        if isCountStmt:
            selectParts = [u'COUNT(*)']
        else:
            for column, (fieldName, alias) in enumerate(self._selectFieldList):
                if (column > 0 
                    and not self.showedColumnModel().isChecked(column)
                    and self.colorFieldAlias() != alias 
                    ):
                    # Вывод единицы вместо реальных данных для полей, которые скрыты в отображении, 
                    # чтобы увеличить скорость выполнения запроса при наличии сложных полей.
                    # 0-й столбец всегда выводится, так как это id-пациента.
                    fieldDescrpiption = "1 AS '%s'" % (alias)
                else:
                    fieldDescrpiption = fieldName if fieldName == alias else u"%s AS '%s'" % (fieldName, alias)
                selectParts.append(fieldDescrpiption)
        if not selectParts:
            selectParts.append("'empty statement'")
        stmtParts.append('SELECT %s' % ', '.join(selectParts))
        
        #Генерация блока FROM
        if self._fromBlock.strip():
            stmtParts.append(u'FROM %s' % self._fromBlock.strip())
        
        #Генерация блока WHERE
        conditionList = []
        if self._whereBlock.strip():
            conditionList.append(self._whereBlock.strip()) 
        conditionList.extend(self.filterItemModel().getConditionList())
        conditionList.extend(self._userFilterItemConditionList)
        conditionList.extend([expression for _, expression, checkState in self.quickFilterList() if bool(checkState)])
        for column in self._filterByColumns.keys():
            columnCondition = self.getColumnInCellCondition(column)
            if columnCondition:
                inCellFilters.append(columnCondition)
        conditionList.extend(inCellFilters)
        
        stmtParts.append(u'WHERE %s' % CDatabase.joinAnd(conditionList))
        
        #Генерация блока ORDER
        orderList = []
        if self._sortBlock.strip():
            orderList.append(self._sortBlock.strip())
        elif self._orderBlock.strip():
            orderList.append(self._orderBlock.strip())
        #atronah: Раньше сортировка шла по обоим условиям (из файла и по выбранному пользователем полю)
        # но как-то глючило и решил сделать либо такую, либо такую.
        if not isCountStmt and orderList:
            stmtParts.append(u'ORDER BY %s' % (', '.join(orderList)))
        
        #Генерация блока LIMIT
        if not isCountStmt and self.currentPage() > 0:
            currentPage = min(self.currentPage(), self.totalPageCount())
            startRow = max(0, self.recordsPerPage * (currentPage - 1))
            stmtParts.append(u'LIMIT %d, %d' % (startRow,
                                                self.recordsPerPage))
        return u' '.join(stmtParts)
    
    
    def setColorFieldAlias(self, alias):
        self._colorFieldAlias = alias
        
    
    def colorFieldAlias(self):
        return self._colorFieldAlias


    def columnIndexByAlias(self, alias):
        for idx, (_, columnAlias) in enumerate(self._selectFieldList):
            if alias == columnAlias:
                return idx
        return -1


    def parseRegistryXML(self, source):
        def parseSelectBlock(xmlReader):
            clientIdFieldName = u'clientId'
            self._selectFieldList = [(self.table()['id'].name(), clientIdFieldName)]
            clientIdTitle = u'Код пациента'
            self._headerList = [[clientIdTitle, True, None, 'c']]
            self._showedColumnModel.addItem(clientIdFieldName, clientIdTitle, False)
            while True:
                xmlReader.readNext()
                if (xmlReader.isStartElement() and xmlReader.name() == 'field'):
                    attributes = xmlReader.attributes()
                    alias = forceStringEx(attributes.value('alias'))
                    isColor = forceStringEx(attributes.value('isColor')).lower() in ['true', '1']
                    if isColor:
                        self.setColorFieldAlias(alias)
                    isHidden = True if isColor else forceStringEx(attributes.value('isHidden')).lower() in ['true', '1']
                    displayName = forceStringEx(attributes.value('displayName')).replace(u'\\n', u'\n')
                    stringWidth = forceStringEx(attributes.value('width'))
                    width = forceInt(stringWidth) if stringWidth else None
                    align = forceStringEx(attributes.value('align')).lower()
                    if align not in ['l', 'r', 'c']:
                        align = 'l' if ('left' in align)\
                                    else ('r' if ('right' in align) \
                                              else 'c')
                    fieldExpr = forceStringEx(xmlReader.readElementText())
                    if not alias:
                        alias = fieldExpr
                    self._selectFieldList.append((fieldExpr,
                                                  alias))
                    self._headerList.append([displayName, isHidden, width, align])
                    self._showedColumnModel.addItem(alias, displayName, not isHidden)
                    
                if xmlReader.isEndElement():
                    if xmlReader.name() == 'select':
                        return
                    elif xmlReader.name() != 'field':
                        assert False, 'unexpected xml end element %s at (%d, %d)' % (xmlReader.name(),
                                                                                    xmlReader.lineNumber(),
                                                                                    xmlReader.columnNumber())
                        return
                if xmlReader.atEnd():
                    assert False, 'unexpected xml end document at (%d, %d)' % (xmlReader.lineNumber(),
                                                                               xmlReader.columnNumber())
        #end parseSelectBlock
        
        def parseFromBlock(xmlReader):
            self._fromBlock = forceStringEx(readXMLElementText(xmlReader))
        #end parseFromBlock
        
        def parseWhereBlock(xmlReader): 
            self._whereBlock = forceStringEx(readXMLElementText(xmlReader))
        #end parseWhereBlock
        
        def parseOrderBlock(xmlReader):
            self._orderBlock = forceStringEx(readXMLElementText(xmlReader))
        #end parseOrderBlock
        
        
        self._showedColumnModel.clear()
        
        xmlReader = QtCore.QXmlStreamReader(source)
        while readNextStartXMLElement(xmlReader):
            if xmlReader.name() == self._xmlRegistryTagName:
                continue
            elif xmlReader.name() == self._xmlQueryTagName:
                break
            else:
                skipCurrentXMLElement(xmlReader)
            
        while readNextStartXMLElement(xmlReader):
            if xmlReader.name() == u'select':
                parseSelectBlock(xmlReader)
            elif xmlReader.name() == u'from':
                parseFromBlock(xmlReader)
            elif xmlReader.name() == u'where':
                parseWhereBlock(xmlReader)
            elif xmlReader.name() == u'order':
                parseOrderBlock(xmlReader)
            else:
                skipCurrentXMLElement(xmlReader)
        
        if isinstance(source, QtCore.QIODevice):
            source.reset()
        self._filterItemModel.loadFromXML(source)
        if isinstance(source, QtCore.QIODevice):
            source.reset()
        self.loadQuickFilterListFromXML(source)
    #-------------- end of interface block
    
    
    #-------------- behaviour block    
    def beginPage(self):
        if self.canPrevPage():
            oldPage = self._currentPage
            self._currentPage = 1
            self.pageChanged.emit(oldPage, self._currentPage)
            return True
        return False

    
    @QtCore.pyqtSlot()
    def prevPage(self):
        if self.canPrevPage():
            oldPage = self._currentPage
            self._currentPage -= 1
            self.pageChanged.emit(oldPage, self._currentPage)
            return True
        return False

            
    @QtCore.pyqtSlot()
    def nextPage(self):
        if self._currentPage + 1 <= self.totalPageCount():
            oldPage = self._currentPage
            self._currentPage += 1
            self.pageChanged.emit(oldPage, self._currentPage)
            return True
        return False

    
    @QtCore.pyqtSlot()
    def endPage(self):
        if self.totalPageCount() > 0:
            oldPage = self._currentPage
            self._currentPage = self.totalPageCount()
            self.pageChanged.emit(oldPage, self._currentPage)
            return True
        return False

            
    @QtCore.pyqtSlot(int)
    def setCurrentPage(self, page):
        if page > 0 and page != self._currentPage:
            oldPage = self._currentPage
            self._currentPage = page
            self.pageChanged.emit(oldPage, self._currentPage)
            return True
        return False


    @QtCore.pyqtSlot()
    def updateAfterChangingPage(self):
        """
            Slot for connect to signal pageChanged(int, int).

            atronah: In some platforms error occurs if connect updateContent slot to signal pageChanged,
            because signal setted slot's attr clientId to oldPage value.

        """
        self.updateContent(clientId = None)


    @QtCore.pyqtSlot()
    def updateContent(self, clientId = None):
        self.startUpdating.emit()
        try:
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            if clientId:
                self.addUserCondition('%s = %s' % (self.table()['id'].name(), clientId))
            self.totalRowCount(True) #update total row count
            self.setQuery(self.queryStmt(False), self._db.db)
            self.clearUserConditionList()
            if self.lastError().isValid():
                raise CDatabaseException(u'Ошибка выполнения запроса', sqlError = self.lastError())
            self.filterItemModel().setDirty(False)
            self.showedColumnModel().setDirty(False)
            self._isInlineFiltersChanged = False
        except:
            QtGui.qApp.logCurrentException()
        finally:
            QtGui.qApp.restoreOverrideCursor()
            self.endUpdating.emit()
    
    #-------------- end of behaviour block
    
    

def main():
    import sys
    from s11main import CS11mainApp
    app = QtGui.QApplication(sys.argv)
    connectionInfo = {'driverName' : 'mysql',
                      'host' : '192.168.0.3',
                      'port' : 3306,
                      'database' : u's11',
                      'user' : u'dbuser',
                      'password' : 'dbpassword',
                      'connectionName' : CS11mainApp.connectionName,
                      'compressData' : True,
                      'afterConnectFunc' : None}
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)
    r = CCustomizableRegistryWidget()
    r.show()
    impFile = QtCore.QFile('..\\registry.xml')
    if not impFile.open(QtCore.QIODevice.ReadOnly):
        return 1
    r.setSource(impFile)
    return app.exec_()

if __name__ == '__main__':
    main()
        