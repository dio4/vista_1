# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Action                import CAction, CActionType
from Events.ActionEditDialog      import CActionEditDialog
from Events.ActionInfo            import CActionInfo, CActionTypeInfo, CCookedActionInfo
from Events.ActionTypeComboBox    import CActionTypeModel
from Events.CreateEvent           import editEvent
from Events.EventInfo             import CEventInfo
from Events.Utils                 import checkTissueJournalStatusByActions

from library.DialogBase           import CDialogBase
from library.PrintInfo            import CInfoContext, CInfoList
from library.PrintTemplates       import additionalCustomizePrintButton, applyTemplate, applyTemplateList, \
                                         getPrintButton, getPrintButtonWithOtherActions
from library.TableModel           import CTableModel, CCol, CDateTimeFixedCol, CEnumCol, CRefBookCol, CTextCol
from library.TableView            import CTableView
from library.Utils                import forceBool, forceDate, forceDouble, forceInt, forceRef, forceString, \
                                         forceStringEx, getVal, setPref, calcAgeTuple, formatNameInt, nameCase

from Orgs.OrgStructComboBoxes     import COrgStructureModel

from Registry.Utils               import getClientInfo, formatClientBanner, getStaffCondition

from Reports.ReportBase           import createTable, CReportBase
from Reports.ReportView           import CReportViewDialog, CPageFormat

from TissueJournal.ActionTableRedactor     import CActionTableRedactor
from TissueJournal.SamplePreparationDialog import CSamplePreparationDialog
from TissueJournal.TissueInfo              import CTakenTissueJournalInfo
from TissueJournal.TissueJournalModels     import CResultActionPropertiesModel, CResultActionsModel, CResultTestsModel,\
                                                  CResultTissueTypesModel, CTissueJournalActionsModel, \
                                                  CTissueJournalModel, CTissueTypesModel
from TissueJournal.Utils                   import deleteEventsIfWithoutActions, getActionContextListByTissue, \
                                                  getDependentEventIdList, CClientIdentifierSelector, \
                                                  CSamplePreparationProgressBar, CTissueJournalTotalEditorDialog

from Ui_TissueJournalDialog                import Ui_TissueJournalDialog


DIGIT_KEY_MAP = {QtCore.Qt.Key_0:u'0', 
                 QtCore.Qt.Key_1:u'1', 
                 QtCore.Qt.Key_2:u'2', 
                 QtCore.Qt.Key_3:u'3', 
                 QtCore.Qt.Key_4:u'4', 
                 QtCore.Qt.Key_5:u'5', 
                 QtCore.Qt.Key_6:u'6', 
                 QtCore.Qt.Key_7:u'7', 
                 QtCore.Qt.Key_8:u'8', 
                 QtCore.Qt.Key_9:u'9', }


class CItemsSelector(QtCore.QObject):
    __pyqtSignals__ = ('changeTableSelectedItems(QString)',
                      )
    def __init__(self, parent, tableNames=None):
        if not tableNames:
            tableNames = []
        QtCore.QObject.__init__(self, parent)
        self.talesSelectedItemsList = {}
        self.tableNames = []
        if tableNames:
            self.setTableNames(tableNames)

    def setTableNames(self, tableNames):
        assert isinstance(tableNames, (list, tuple))
        self.tableNames = tableNames
        for tableName in tableNames:
            self.talesSelectedItemsList[tableName] = []

    def isSelected(self, id, tableName):
        return id in self.getSlectedTableItems(tableName)

    def getSlectedTableItems(self, tableName):
        return self.talesSelectedItemsList.get(tableName, [])

    def setSelected(self, id, value, tableName):
        present = self.isSelected(id, tableName)
        tableSelectedIdList = self.getSlectedTableItems(tableName)
        if value:
            if not present:
                tableSelectedIdList.append(id)
        else:
            if present:
                tableSelectedIdList.remove(id)
        self.emitChangeTableSelectedItems(tableName)

    def setAllSelectionOff(self, tableName):
        self.talesSelectedItemsList[tableName] = []
        self.emitChangeTableSelectedItems(tableName)

    def setAllSelectionOn(self, tableName, idList):
        newList = list(idList)
        self.talesSelectedItemsList[tableName] = newList
        self.emitChangeTableSelectedItems(tableName)

    def emitChangeTableSelectedItems(self, tableName):
        self.emit(QtCore.SIGNAL('changeTableSelectedItems(QString)'), QtCore.QString(tableName))


class CTissueJournalDialog(CDialogBase, Ui_TissueJournalDialog):
    def __init__(self, parent):
        CDialogBase.__init__(self, parent)

        # tables
        db = QtGui.qApp.db
        self.tablePersonWithSpeciality = db.table('vrbPersonWithSpeciality')
        self.tablePerson = db.table('Person')
        self.tableAction = db.table('Action')
        self.tableTissueJournal = db.table('TakenTissueJournal')
        self.tableClient = db.table('Client')

        self.mapPersonIdList = {}
        self.previousSelectedClientIdentifier = None
        self.mapAccounSystemNameToId = {}
        self.clientIdentifierTypesList = []
        self._ibmSearch = [u'', None] # string value and last result row 
        self._tissueScanBarcodeActive = False
        self._tissueScanBarcodeActiveTimer = QtCore.QTimer()
        self.connect(self._tissueScanBarcodeActiveTimer, QtCore.SIGNAL('timeout()'), self.on_tissueScanBarcodeActiveTimer_timeout)

        self.addModels('OrgStructure',        COrgStructureModel(self, QtGui.qApp.currentOrgId()))
        self.addModels('TissueTypes',         CTissueTypesModel(self))
        self.addModels('TissueJournal',       CTissueJournalModel(self))
        self.addModels('TissueJournaActions', CTissueJournalActionsModel(self))

        self.modelTissueTypes.setFullIdList()

        self.setupUi(self)

        self.actTissueTabMainPrint = QtGui.QAction(u'Печать журнала', self)
        self.otherTissueActions = [{'action': self.actTissueTabMainPrint, 'slot': self.on_btnPrint_tissueTabMainPrint}]
        self.tissueTabBtnPrint = getPrintButtonWithOtherActions(self, 'tissueJournal', name=u'Печать', otherActions=self.otherTissueActions)
        self.tissueTabBtnPrint.setObjectName('tissueTabBtnPrint')
        self.connect(self.tissueTabBtnPrint, QtCore.SIGNAL('printByTemplate(int)'), self.on_tabTissuePrintByTemplate)

        self.resultTabBtnPrint = getPrintButton(self, context='tissueJournalResult', name=u'Печать')

        self.resultTabBtnPrint.setObjectName('resultTabBtnPrint')
        self.connect(self.resultTabBtnPrint, QtCore.SIGNAL('printByTemplate(int)'), self.on_tabResultPrintByTemplate)

        self.buttonBox.addButton(self.tissueTabBtnPrint, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.resultTabBtnPrint, QtGui.QDialogButtonBox.ActionRole)
        self.resultTabBtnPrint.setVisible(False)

        # для удобства важен вывод порядкого номера записи в tblTissueJournal
        # так что визаулизируем обратно verticalHeader
        tissueJournalVerticalHeader = self.tblTissueJournal.verticalHeader()
        tissueJournalVerticalHeader.show()
        tissueJournalVerticalHeader.setResizeMode(QtGui.QHeaderView.Fixed)

        self.cmbFilterAccountingSystem.setTable('rbAccountingSystem',  True)

        self.tissueJournalFilter = {}
        self.resultActionsFilter = {}
        self.clientFilter = {}
        self.currentClientId   = None
        self.currentClientInfo = None

        self.blockSelections(True)
        self.setModels(self.treeOrgStructure, self.modelOrgStructure, self.selectionModelOrgStructure)
        self.setModels(self.tblTissueTypes, self.modelTissueTypes, self.selectionModelTissueTypes)
        self.setModels(self.tblTissueJournal, self.modelTissueJournal, self.selectionModelTissueJournal)
        self.setModels(self.tblTissueJournalActions, self.modelTissueJournaActions, self.selectionModelTissueJournaActions)

        # настройка меню
        self.createTblTissueJournalMenu()

        self.tblTissueJournal.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

        self.tblTissueTypes.setCurrentIndex(self.modelTissueTypes.index(0, 0))

        previewFind = None
        orgStructureIndex = self.modelOrgStructure.findItemId(previewFind)
        if orgStructureIndex and orgStructureIndex.isValid():
            self.treeOrgStructure.setCurrentIndex(orgStructureIndex)
            self.treeOrgStructure.setExpanded(orgStructureIndex, True)
        self.cmbExecOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbExecPerson.addNotSetValue()
        
        self.cmbExecPerson.setValue(0)
        self.cmbEventType.setTable('EventType')
        self.cmbFinanceType.setTable('rbFinance')
        self.cmbActionType.setClassesVisible(True)
        self.cmbActionType.setAllSelectable(True)
        self.cmbActionType.setPrefferedWidth(500)
        self.cmbActionType.setMaxVisibleItems(30)
        self.cmbExecOrg.setValue(QtGui.qApp.currentOrgId())

        self.updateTissueJournalList()
        self.blockSelections(False)

        self.clientIdentifierSelector = CClientIdentifierSelector(self)
        self.previousChkNeedAmountAndUnit = False
        self.previousChkNeedStatus        = False
        self.previousChkNeedDatetime      = False
        self.previousChkNeedPerson        = False
        self.previousChkNeedMKB           = False

        self.connect(self.tblTissueJournal.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.tblTissueJournalPopupMenuAboutToShow)
        
        self.tabWidgetFilter.setObjectName('tabWidgetFilter')
#        self.connect(self.tabWidgetFilter, QtCore.SIGNAL('currentChanged(int)'), self.on_tabWidgetFilter_currentChanged)

        self.updateActionTypeComboBox()

        # вкладка результат
        self._previousResultActionTypeIdListByService = []
        self._previousResultServiceId = None

        self.edtResultTissueIdentifierTo.setEnabled(False)
        self.edtResultSamplingNumberTo.setEnabled(False)

        self.itemsSelector = CItemsSelector(self, ['rbTissueType', 'rbTest'])
        self.connect(self.itemsSelector, QtCore.SIGNAL('changeTableSelectedItems(QString)'), self.on_changeTableSelectedItems)
        
        self.cmbResultActionExecPerson.addNotSetValue()
        self.cmbResultActionAssistant.addNotSetValue()
        self.cmbResultEventType.setTable('EventType')
        self.cmbResultFinanceType.setTable('rbFinance')
        self.cmbResultActionSetPersonSpeciality.setTable('rbSpeciality', addNone=True)
        self.cmbResultClientIdAccountingSystem.setTable('rbAccountingSystem')
        self.cmbResultActionSetPersonOrgStructure.setValue(None)
        self.cmbResultExecOrg.setValue(QtGui.qApp.currentOrgId())

        self.addModels('ResultActions',    CResultActionsModel(self))
        self.addModels('ResultProperties', CResultActionPropertiesModel(self))
        self.addModels('ResultTissueType', CResultTissueTypesModel(self))
        self.addModels('ResultTests',      CResultTestsModel(self))
        self.addModels('ResultActionType', CActionTypeModel(self))

        # для удобства важен вывод порядкого номера записи в tblResultActions
        # так что визаулизируем обратно verticalHeader
        resultActionsVerticalHeader = self.tblResultActions.verticalHeader()
        resultActionsVerticalHeader.show()
        resultActionsVerticalHeader.setResizeMode(QtGui.QHeaderView.Fixed)

        self.modelResultActionType.setClassesVisible(True)
        self.modelResultTissueType.setFullIdList()
        self.modelResultTests.setFullIdList()
        self.modelResultProperties.setReadOnly(True)

        self.setModels(self.tblResultActions, self.modelResultActions, self.selectionModelResultActions)
        self.setModels(self.tblResultProperties, self.modelResultProperties, self.selectionModelResultProperties)
        self.setModels(self.tblResultTissueType, self.modelResultTissueType, self.selectionModelResultTissueType)
        self.setModels(self.tblResultTests, self.modelResultTests, self.selectionModelResultTests)
        self.setModels(self.tblResultActionType, self.modelResultActionType, self.selectionModelResultActionType)

        self.tblResultActionType.expand(self.modelResultActionType.index(0, 0))
        self.tblResultProperties.verticalHeader().show()
        self.tblResultActions.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

        self.createTblResultActionsMenu()

        self.connect(self.tblResultActions.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.tblResultActionsPopupMenuAboutToShow)

        self.actSelectOnAllResultTissue  = QtGui.QAction(u'Выбрать все', self)
        self.actSelectOffAllResultTissue = QtGui.QAction(u'Снять все отметки', self)
        self.actSelectOnAllResultTests  = QtGui.QAction(u'Отметить все', self)
        self.actSelectOffAllResultTests = QtGui.QAction(u'Снять все отметки', self)

        self.tblResultTissueType.addPopupAction(self.actSelectOnAllResultTissue)
        self.tblResultTissueType.addPopupAction(self.actSelectOffAllResultTissue)
        self.tblResultTests.addPopupAction(self.actSelectOnAllResultTests)
        self.tblResultTests.addPopupAction(self.actSelectOffAllResultTests)

        self.connect(self.actSelectOnAllResultTissue, QtCore.SIGNAL('triggered()'), self.selectOnAllResultTissue)
        self.connect(self.actSelectOffAllResultTissue, QtCore.SIGNAL('triggered()'), self.selectOffAllResultTissue)
        self.connect(self.actSelectOnAllResultTests, QtCore.SIGNAL('triggered()'), self.selectOnAllResultTests)
        self.connect(self.actSelectOffAllResultTests, QtCore.SIGNAL('triggered()'), self.selectOffAllResultTests)

        self.connect(self.selectionModelResultActionType, QtCore.SIGNAL('currentChanged(QModelIndex,QModelIndex)'),
                     self.on_selectionModelResultActionTypeCurrentChanged)
        self.connect(self.selectionModelResultActions, QtCore.SIGNAL('currentChanged(QModelIndex,QModelIndex)'),
                     self.on_selectionModelResultActionsCurrentChanged)

        self.updateResultActionsFromAll()

        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)

        self.setWindowTitle(u'Лабораторный журнал')

        self.setServiceStaticFilter()

        self.addBarcodeScanAction('actResultScanBarcode')
        self.tabResult.addAction(self.actResultScanBarcode)
        self.connect(self.actResultScanBarcode, QtCore.SIGNAL('triggered()'), self.on_actResultScanBarcode_triggered)
        
        self.addBarcodeScanAction('actTissueScanBarcode')
        self.tabTissue.addAction(self.actTissueScanBarcode)
        self.connect(self.actTissueScanBarcode, QtCore.SIGNAL('triggered()'), self.on_actTissueScanBarcode_triggered)
        
        # eventFilters
        self.tblTissueJournal.installEventFilter(self)
        self.tblTissueJournalActions.installEventFilter(self)

        self.prepareStatusBar()

    def prepareStatusBar(self):
        self.progressBar = CSamplePreparationProgressBar()
        self.progressBar.setMaximumWidth(200)
        self.progressBar.setMaximumHeight(self.statusBar.height()/2)
        self.progressBarVisible = False

    def startProgressBar(self, itemsCount=0):
        progressBar = self.getProgressBar()
        progressBar.setMaximum(itemsCount)
        progressBar.setValue(0)

    def stepProgressBar(self):
        self.progressBar.step()

    def stopProgressBar(self):
        self.hideProgressBar()
        
    def getProgressBar(self):
        if not self.progressBarVisible:
            self.progressBarVisible = True
            self.statusBar.addWidget(self.progressBar)
            self.progressBar.show()
        return self.progressBar

    def hideProgressBar(self):
        self.statusBar.removeWidget(self.progressBar)
        self.progressBarVisible = False

    def blockSelections(self, value):
        self.selectionModelOrgStructure.blockSignals(value)
        self.selectionModelTissueTypes.blockSignals(value)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress:
            key = event.key()
            if obj in [self.tblTissueJournal, self.tblTissueJournalActions] and event.modifiers() == QtCore.Qt.ControlModifier and key == QtCore.Qt.Key_Down:
                self.keyPressEvent(event)
                return True
        return False

    def analiseKeyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Enter:
            self.resetIbmSearch()
            return None
        return QtGui.QKeyEvent(QtCore.QEvent.KeyPress, key, QtCore.Qt.ControlModifier)

    def keyPressEvent(self, event): # QKeyEvent
        if self.mainTabWidget.currentIndex() == 0:
            if self._tissueScanBarcodeActive:
                event = self.analiseKeyPressEvent(event)
                if not event:
                    return
            self.searchIbmEvent(event)
        CDialogBase.keyPressEvent(self, event)
    
    def searchIbmEvent(self, event):
        modifiers = event.modifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            key = event.key()
            if key == QtCore.Qt.Key_Down:
                searchString = self._ibmSearch[0]
                if searchString:
                    resultRow = self.searchIbm(searchString, self._ibmSearch[1])
                    self.setTissueJournalByRow(resultRow)
            elif key in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Backspace]:
                searchString = self._ibmSearch[0][:-1]
                self._ibmSearch[0] = searchString
                self.statusBar.showMessage(searchString, 5000)
                if searchString:
                    resultRow = self.searchIbm(searchString, 0)
                    self.setTissueJournalByRow(resultRow)
            elif key in DIGIT_KEY_MAP.keys():
                keyText = DIGIT_KEY_MAP.get(key, u'')
                searchString = u''.join([self._ibmSearch[0], keyText])
                self._ibmSearch[0] = searchString
                self.statusBar.showMessage(searchString, 5000)
                resultRow = self.searchIbm(searchString, self._ibmSearch[1])
                self.setTissueJournalByRow(resultRow)
    
    def setTissueJournalByRow(self, resultRow):
        if not resultRow is None:
            self.tblTissueJournal.clearSelection()
            self._ibmSearch[1] = resultRow
            self.tblTissueJournal.setCurrentRow(resultRow)
                
    def searchIbm(self, searchString, lastResultRow):
        extremeValue = lastResultRow+1 if not lastResultRow is None else 0
        actualIdList    = self.modelTissueJournal.idList()[extremeValue:]
        passedRowsCount = len(self.modelTissueJournal.idList()[:extremeValue])
        for row, tissueJournalId in enumerate(actualIdList):
            record = self.modelTissueJournal.getRecordById(tissueJournalId)
            if searchString in forceString(record.value('externalId')):
                return row+passedRowsCount
        return lastResultRow
            
    def keyReleaseEvent(self, event):
        if self.mainTabWidget.currentIndex() == 0 and not self._tissueScanBarcodeActive:
            if event.key() == QtCore.Qt.Key_Control:
                self.resetIbmSearch()
        CDialogBase.keyReleaseEvent(self, event)
        
    def on_actTissueScanBarcode_triggered(self):
        self._tissueScanBarcodeActive = True
        self._tissueScanBarcodeActiveTimer.start(1500)
        
    def on_tissueScanBarcodeActiveTimer_timeout(self):
        self.resetIbmSearch()
        
    def resetIbmSearch(self):
        self.statusBar.clearMessage()
        self._ibmSearch = [u'', None]
        self._tissueScanBarcodeActive = False
        self._tissueScanBarcodeActiveTimer.stop()

    def createTblTissueJournalMenu(self):
        self.actDeleteRow = QtGui.QAction(u'Удалить запись', self)
        self.actDeleteRow.setObjectName('actDeleteRow')
        self.connect(self.actDeleteRow, QtCore.SIGNAL('triggered()'), self.removeCurrentRow)
        self.tblTissueJournal.addPopupAction(self.actDeleteRow)
        self.actOpenEvent = QtGui.QAction(u'Открыть событие', self)
        self.actOpenEvent.setObjectName('actOpenEvent')
        self.connect(self.actOpenEvent, QtCore.SIGNAL('triggered()'), self.on_tblTissueJournal_doubleClicked)
        self.tblTissueJournal.addPopupAction(self.actOpenEvent)

        self.actOpenActionTableRedactor = QtGui.QAction(u'Табличный редактор действий', self)
        self.actOpenActionTableRedactor.setObjectName('actOpenActionTableRedactor')
        self.connect(self.actOpenActionTableRedactor, QtCore.SIGNAL('triggered()'), self.on_openActionTableRedactor)
        self.tblTissueJournal.addPopupAction(self.actOpenActionTableRedactor)

        self.actOpenPropertiesTableRedactor = QtGui.QAction(u'Табличный редактор свойств', self)
        self.actOpenPropertiesTableRedactor.setObjectName('actOpenPropertiesTableRedactor')
        self.connect(self.actOpenPropertiesTableRedactor, QtCore.SIGNAL('triggered()'), self.on_openPropertiesTableRedactor)
        self.tblTissueJournal.addPopupAction(self.actOpenPropertiesTableRedactor)

        self.tblTissueJournal.addPopupSeparator()

        self.actSelectAllRowTissueJournal = QtGui.QAction(u'Выделить все строки', self)
        self.tblTissueJournal.addPopupAction(self.actSelectAllRowTissueJournal)
        self.connect(self.actSelectAllRowTissueJournal, QtCore.SIGNAL('triggered()'), self.on_selectAllRowTissueJournal)

        self.actClearSelectionRowTissueJournal = QtGui.QAction(u'Снять выделение', self)
        self.tblTissueJournal.addPopupAction(self.actClearSelectionRowTissueJournal)
        self.connect(self.actClearSelectionRowTissueJournal, QtCore.SIGNAL('triggered()'), self.on_clearSelectionRowTissueJournal)

        self.actChangeValueTissueJournal = QtGui.QAction(u'Изменить данные', self)
        self.tblTissueJournal.addPopupAction(self.actChangeValueTissueJournal)
        self.connect(self.actChangeValueTissueJournal, QtCore.SIGNAL('triggered()'), self.on_changeValueTissueJournal)

        self.tblTissueJournal.addPopupSeparator()

        self.actSamplingPreparation = QtGui.QAction(u'Пробоподготовка', self)
        self.tblTissueJournal.addPopupAction(self.actSamplingPreparation)
        self.connect(self.actSamplingPreparation, QtCore.SIGNAL('triggered()'), self.on_samplingPreparation)

    def createTblResultActionsMenu(self):
        self.actSelectAllRowResultActions = QtGui.QAction(u'Выделить все строки', self)
        self.tblResultActions.addPopupAction(self.actSelectAllRowResultActions)
        self.connect(self.actSelectAllRowResultActions, QtCore.SIGNAL('triggered()'), self.on_selectAllRowResultActions)


        self.actClearSelectionRowResultActions = QtGui.QAction(u'Снять выделение', self)
        self.tblResultActions.addPopupAction(self.actClearSelectionRowResultActions)
        self.connect(self.actClearSelectionRowResultActions, QtCore.SIGNAL('triggered()'), self.on_clearSelectionRowResultActions)

        self.actChangeValueResultActions = QtGui.QAction(u'Изменить данные', self)
        self.tblResultActions.addPopupAction(self.actChangeValueResultActions)
        self.connect(self.actChangeValueResultActions, QtCore.SIGNAL('triggered()'), self.on_changeValueResultActions)

        self.tblTissueJournal.addPopupSeparator()

        self.actOpenActionTableRedactorResultActions = QtGui.QAction(u'Табличный редактор действий', self)
        self.actOpenActionTableRedactorResultActions.setObjectName('actOpenActionTableRedactorResultActions')
        self.connect(self.actOpenActionTableRedactorResultActions, QtCore.SIGNAL('triggered()'), self.on_openActionTableRedactorResultActions)
        self.tblResultActions.addPopupAction(self.actOpenActionTableRedactorResultActions)

        self.actOpenPropertiesTableRedactorResultActions = QtGui.QAction(u'Табличный редактор свойств', self)
        self.actOpenPropertiesTableRedactorResultActions.setObjectName('actOpenPropertiesTableRedactorResultActions')
        self.connect(self.actOpenPropertiesTableRedactorResultActions, QtCore.SIGNAL('triggered()'), self.on_openPropertiesTableRedactorResultActions)
        self.tblResultActions.addPopupAction(self.actOpenPropertiesTableRedactorResultActions)

    def on_samplingPreparation(self):
        dlg = CSamplePreparationDialog(self)
        selectedTissueJournalIdList = self.getSelectedTissueJournalIdList()
        selectedTissueJournalIdCount = len(selectedTissueJournalIdList)

        if selectedTissueJournalIdCount > 1:
            self.connect(dlg, QtCore.SIGNAL('samplePreparationPassed()'), self.stepProgressBar)
            self.startProgressBar(selectedTissueJournalIdCount)
            dlg.automaticalSaveProbes(selectedTissueJournalIdList)
            self.disconnect(dlg, QtCore.SIGNAL('samplePreparationPassed()'), self.stepProgressBar)
            self.stopProgressBar()

        elif selectedTissueJournalIdCount == 1:
            tissueJournalId = selectedTissueJournalIdList[0]
            dlg.load(tissueJournalId)
            dlg.exec_()
            
    def getSelectedTissueJournalIdList(self):
        selectedRows = self.getSelectedRows(self.tblTissueJournal)
        idList       = self.modelTissueJournal.idList()
        return [idList[row] for row in selectedRows]

    def getServiceIdListByTissue(self, tissueTypeId=None):
        db =QtGui.qApp.db
        tableActionTypeTissueType = db.table('ActionType_TissueType')
        tableActionTypeService = db.table('ActionType_Service')
        queryTable = tableActionTypeService.innerJoin(tableActionTypeTissueType,
                                                      tableActionTypeTissueType['master_id'].eq(tableActionTypeService['master_id']))
        cond = tableActionTypeTissueType['tissueType_id'].eq(tissueTypeId) if tissueTypeId else '1'
        idList = db.getDistinctIdList(queryTable, tableActionTypeService['service_id'].name(), cond)
        return idList

    def setServiceStaticFilter(self):
        db =QtGui.qApp.db
        tableService = db.table('rbService')
        idList = self.getServiceIdListByTissue()
        staticFilter = tableService['id'].inlist(idList)
        self.cmbService.setStaticFilter(staticFilter)
        self.cmbResultService.setStaticFilter(staticFilter)

    def setServiceStaticFilterByTissue(self, need):
        if need:
            tissueTypeId = self.tblTissueTypes.currentItemId()
            idList = self.getServiceIdListByTissue(tissueTypeId)
        else:
            idList = self.getServiceIdListByTissue()
        filter = QtGui.qApp.db.table('rbService')['id'].inlist(idList)
        self.cmbService.setStaticFilter(filter)

    def isSelected(self, id, tableName):
        return self.itemsSelector.isSelected(id, tableName)

    def setSelected(self, id, value, tableName):
        self.itemsSelector.setSelected(id, value, tableName)

    def selectOnAllResultTissue(self):
        self.selectOnAllResultTable('rbTissueType')

    def selectOffAllResultTissue(self):
        self.selectOffAllResultTable('rbTissueType')

    def selectOnAllResultTests(self):
        self.selectOnAllResultTable('rbTest')

    def selectOffAllResultTests(self):
        self.selectOffAllResultTable('rbTest')

    def selectOnAllResultTable(self, tableName):
        if tableName == 'rbTest':
            idList = self.modelResultTests.idList()
        elif tableName == 'rbTissueType':
            idList = self.modelResultTissueType.idList()
        else:
            return
        self.itemsSelector.setAllSelectionOn(tableName, idList)

    def selectOffAllResultTable(self, tableName):
        self.itemsSelector.setAllSelectionOff(tableName)

    def getSelectedRows(self, tbl):
        result = [index.row() for index in tbl.selectedIndexes()]
        result = list( set(result) & set(result) )
        result.sort()
        return result

    def on_selectAllRowTissueJournal(self):
        self.tblTissueJournal.selectAll()

    def on_clearSelectionRowTissueJournal(self):
        self.tblTissueJournal.clearSelection()

    def on_changeValueTissueJournal(self):
        dlg = CTissueJournalTotalEditorDialog(self)
        if dlg.exec_():
            db = QtGui.qApp.db
            values                 = dlg.values()
            personIdInJournal      = values['personIdInJournal']
            personIdInAction       = values['personIdInAction']
            assistantIdInAction    = values['assistantIdInAction']
            status                 = values['status']
            makeChanges = not status is None or bool(assistantIdInAction) or bool(personIdInAction) or bool(personIdInJournal)
            cond   = []
            values = []
            tableTakenTissueJournal = db.table('TakenTissueJournal')
            if personIdInJournal:
                values.append(tableTakenTissueJournal['execPerson_id'].eq(personIdInJournal))
            if not status is None:
                values.append(tableTakenTissueJournal['status'].eq(status+1))
            if makeChanges:
                currentIndex = self.tblTissueJournal.currentIndex()
                selectedRows   = self.getSelectedRows(self.tblTissueJournal)
                selectedIdList = [self.modelTissueJournal.idList()[row] for row in selectedRows]
                if values:
                    stmt = 'UPDATE %s SET %s WHERE %s'
                    cond           = tableTakenTissueJournal['id'].inlist(selectedIdList)
                    db.query( stmt % ( tableTakenTissueJournal.name(), ', '.join(values), cond ) )
                if not status is None or bool(assistantIdInAction) or bool(personIdInAction):
                    tableAction = db.table('Action')
                    cond = [tableAction['takenTissueJournal_id'].inlist(selectedIdList)]
                    actionRecordList = db.getRecordList(tableAction, 'id, status, endDate, person_id', cond)
                    for record in actionRecordList:
                        if not status is None:
                            record.setValue('status', QtCore.QVariant(status))
                            if status in [2, 4]:
                                endDate = forceDate(record.value('endDate'))
                                if not endDate.isValid():
                                    record.setValue('endDate', QtCore.QVariant(QtCore.QDate.currentDate()))
                            else:
                                record.setValue('endDate', QtCore.QVariant(QtCore.QDate()))
                        if bool(personIdInAction):
                            record.setValue('person_id', QtCore.QVariant(personIdInAction))
                        if bool(assistantIdInAction):
                            actionId = forceRef(record.value('id'))
                            assistantsByCode = CAction.loadAssistants(actionId)
                            CAction.addAssistant(assistantsByCode, 'assistant', assistantIdInAction)
                            CAction.saveAssistants(actionId, assistantsByCode)
                        db.updateRecord(tableAction, record)
                self.updateTissueJournalList()
                self.tblTissueJournal.setCurrentIndex(currentIndex)

    def on_selectAllRowResultActions(self):
        self.tblResultActions.selectAll()

    def on_clearSelectionRowResultActions(self):
        self.tblResultActions.clearSelection()

    def on_changeValueResultActions(self):
        dlg = CTissueJournalTotalEditorDialog(self)
        dlg.setVisibleJournalWidgets(False)
        if dlg.exec_():
            db = QtGui.qApp.db
            values                 = dlg.values()
            personIdInAction       = values['personIdInAction']
            assistantIdInAction    = values['assistantIdInAction']
            status                 = values['status']
            makeChanges = not status is None or bool(assistantIdInAction) or bool(personIdInAction)
            if makeChanges:
                currentIndex = self.tblResultActions.currentIndex()
                selectedRows   = self.getSelectedRows(self.tblResultActions)
                selectedIdList = [self.modelResultActions.idList()[row] for row in selectedRows]
                tableAction = db.table('Action')
                cond = [tableAction['id'].inlist(selectedIdList)]
                actionRecordList = db.getRecordList(tableAction, 'id, status, endDate, person_id, actionType_id', cond)
                for record in actionRecordList:
                    if not status is None:
                        record.setValue('status', QtCore.QVariant(status))
                        if status in [2, 4]:
                            endDate = forceDate(record.value('endDate'))
                            if not endDate.isValid():
                                record.setValue('endDate', QtCore.QVariant(QtCore.QDate.currentDate()))
                        else:
                            record.setValue('endDate', QtCore.QVariant(QtCore.QDate()))
                    if bool(personIdInAction):
                        record.setValue('person_id', QtCore.QVariant(personIdInAction))
                    if bool(assistantIdInAction):
                        actionId = forceRef(record.value('id'))
                        assistantsByCode = CAction.loadAssistants(actionId)
                        CAction.addAssistant(assistantsByCode, 'assistant', assistantIdInAction)
                        CAction.saveAssistants(actionId, assistantsByCode)
                    db.updateRecord(tableAction, record)
                checkItems = [ (record, CAction(record=record)) for record in actionRecordList ]
                checkTissueJournalStatusByActions(checkItems)
                self.updateResultActionsFromAll()
                self.tblResultActions.setCurrentIndex(currentIndex)

    def tblTissueJournalPopupMenuAboutToShow(self):
        currentIndex = self.tblTissueJournal.currentIndex()
        curentIndexIsValid = currentIndex.isValid()
        self.actDeleteRow.setEnabled(curentIndexIsValid)
        self.actOpenActionTableRedactor.setEnabled(curentIndexIsValid)
        self.actOpenPropertiesTableRedactor.setEnabled(curentIndexIsValid)
        self.actOpenEvent.setEnabled(curentIndexIsValid)
        self.actSamplingPreparation.setEnabled(curentIndexIsValid)
        bSelectedRows = bool(self.getSelectedRows(self.tblTissueJournal))
        self.actClearSelectionRowTissueJournal.setEnabled(bSelectedRows)
        self.actChangeValueTissueJournal.setEnabled(bSelectedRows)

    def on_openActionTableRedactor(self):
        tableRedactor = CActionTableRedactor(self, tissueJournalModel=self.modelTissueJournal, onlyProperties=False)
        self.openTableRedactor(tableRedactor)

    def on_openPropertiesTableRedactor(self):
        tableRedactor = CActionTableRedactor(self, tissueJournalModel=self.modelTissueJournal, onlyProperties=True)
        self.openTableRedactor(tableRedactor)

    def openTableRedactor(self, tableRedactor):
        tissueJournalIdList = self.tblTissueJournal.selectedItemIdList()
        actionIdList = self.getActionIdList(tissueJournalIdList)
        QtGui.qApp.callWithWaitCursor(self, tableRedactor.setTissueJournalIdList, tissueJournalIdList, actionIdList)

        if tableRedactor.exec_():
            currentIndex = self.tblTissueJournal.currentIndex()
            self.updateTissueJournalList()
            self.tblTissueJournal.setCurrentIndex(currentIndex)

    def on_openActionTableRedactorResultActions(self):
        tableRedactor = CActionTableRedactor(self, tissueJournalModel=None, onlyProperties=False)
        self.openTableRedactorResultActions(tableRedactor)

    def on_openPropertiesTableRedactorResultActions(self):
        tableRedactor = CActionTableRedactor(self,
                                             tissueJournalModel=None,
                                             onlyProperties=True)
        self.openTableRedactorResultActions(tableRedactor)

    def openTableRedactorResultActions(self, tableRedactor):
        selectedRows   = self.getSelectedRows(self.tblResultActions)
        selectedIdList = [self.modelResultActions.idList()[row] for row in selectedRows]
        QtGui.qApp.callWithWaitCursor(self, tableRedactor.setActionIdList, selectedIdList)

        if tableRedactor.exec_():
            currentIndex = self.tblResultActions.currentIndex()
            self.updateResultActionsFromAll()
            self.tblResultActions.setCurrentIndex(currentIndex)

    def tblResultActionsPopupMenuAboutToShow(self):
        currentIndex = self.tblResultActions.currentIndex()
        curentIndexIsValid = currentIndex.isValid()
        self.actOpenActionTableRedactorResultActions.setEnabled(curentIndexIsValid)
        self.actOpenPropertiesTableRedactorResultActions.setEnabled(curentIndexIsValid)
        bSelectedRows = bool(self.getSelectedRows(self.tblResultActions))
        self.actClearSelectionRowResultActions.setEnabled(bSelectedRows)
        self.actChangeValueResultActions.setEnabled(bSelectedRows)

    def removeCurrentRow(self):
        NO  = 0
        YES = 1
        WITH_ACTIONS = 2
        def confirmRemoveRow(row):
            buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
            messageBox = QtGui.QMessageBox(QtGui.QMessageBox.Question, u'Внимание', u'Действительно удалить?', buttons, self)
            btnDeleteWithActions = QtGui.QPushButton(u'Удалить вместе с действиями', self)
            messageBox.addButton(btnDeleteWithActions, QtGui.QMessageBox.AcceptRole)
            messageBox.setDefaultButton(QtGui.QMessageBox.No)
            result = messageBox.exec_()
            if result == QtGui.QMessageBox.Yes:
                return YES
            elif result == QtGui.QMessageBox.No:
                return NO
            else:
                btn = messageBox.clickedButton()
                if btnDeleteWithActions == btn:
                    return WITH_ACTIONS
            return 0

        def removeCurrentRowInternal():
            tbl = self.tblTissueJournal
            index = tbl.currentIndex()
            row = tbl.currentIndex().row()
            if index.isValid():
                result = confirmRemoveRow(row)
                if bool(result):
                    if result == WITH_ACTIONS:
                        itemId = tbl.currentItemId()
                        if bool(itemId):
                            dependentEventList = getDependentEventIdList(itemId)
                            QtGui.qApp.db.deleteRecord('Action', 'Action.`takenTissueJournal_id`=%d'%itemId)
                            deleteEventsIfWithoutActions(dependentEventList)
                    tbl.model().removeRow(row)
                    tbl.setCurrentRow(row)
        QtGui.qApp.call(self, removeCurrentRowInternal)

    def getOrgStructureIdList(self, treeIndex):
        treeItem = treeIndex.internalPointer() if treeIndex.isValid() else None
        if treeItem:
            result = treeItem.getItemIdList()
            return result
        return []

    def getPersonIdList(self, orgStructureIdList):
        tOrgStructureIdList = tuple(orgStructureIdList)
        personIdList = self.mapPersonIdList.get(tOrgStructureIdList, None)
        if personIdList:
            pass
        else:
            table = self.tablePersonWithSpeciality
            cond = [table['orgStructure_id'].inlist(orgStructureIdList)]
            personIdList = QtGui.qApp.db.getIdList(table, 'id', cond)
            self.mapPersonIdList[tOrgStructureIdList] = personIdList
        return personIdList

    def getSetPersonIdList(self):
        treeIndex = self.treeOrgStructure.currentIndex()
        orgStructureIdList = self.getOrgStructureIdList(treeIndex)
        return self.getPersonIdList(orgStructureIdList)

    def getExecPersonIdList(self):
        treeIndex = self.cmbExecOrgStructure._popupView.currentIndex()
        orgStructureIdList = self.getOrgStructureIdList(treeIndex)
        return self.getPersonIdList(orgStructureIdList)

    def getTissueJournalIdList(self):
        db = QtGui.qApp.db
        tableAction      = self.tableAction
        tableJournal     = self.tableTissueJournal
        tableClient      = self.tableClient
        tableEvent       = db.table('Event')
        tableProbe       = db.table('Probe')
        tableActionTypeService = db.table('ActionType_Service')
        tableIdentification = db.table('ClientIdentification')

        execPersonIdList = self.tissueJournalFilter.get('execPersonIdList', None)
        execPersonId     = self.tissueJournalFilter.get('execPersonId', None)
        isChkTissueType  = self.tissueJournalFilter.get('isChkTissueType', False)
        eventTypeId      = self.tissueJournalFilter.get('eventTypeId', None)
        financeTypeId    = self.tissueJournalFilter.get('financeTypeId', None)
        actionTypeId     = self.tissueJournalFilter.get('actionTypeId', None)
        serviceId        = self.tissueJournalFilter.get('serviceId', None)
        isChkUrgent      = self.tissueJournalFilter.get('isChkUrgent', None)
        isChkClientSex   = self.tissueJournalFilter.get('isChkClientSex', None)
        clientSex        = self.tissueJournalFilter.get('clientSex', 0)+1
        execOrg          = self.tissueJournalFilter.get('execOrg', None)
        isChkStatus      = self.tissueJournalFilter.get('isChkStatus', None)
        chkStatus        = self.tissueJournalFilter.get('chkStatus', 0)
        isChkRelegateOrg = self.tissueJournalFilter.get('isChkRelegateOrg', False)
        relegateOrgId    = self.tissueJournalFilter.get('relegateOrgId', None)
        isChkPreliminaryResult = self.tissueJournalFilter.get('isChkPreliminaryResult', False)
        chkPreliminaryResult   = self.tissueJournalFilter.get('chkPreliminaryResult', 0)
        isChkWithoutSampling   = self.tissueJournalFilter.get('isChkWithoutSampling', False)
        
        queryTable = tableJournal.leftJoin(tableAction, tableAction['takenTissueJournal_id'].eq(tableJournal['id']))

        condJournal = [tableJournal['deleted'].eq(0)]
        condActionForAllActionsCountLabel = []

        order = []

        if self.chkIBM.isChecked():
            condJournal.append(tableJournal['externalId'].eq(forceStringEx(self.edtIBM.text())))
        else:
            if self.clientFilter or isChkClientSex:
                queryTable = queryTable.leftJoin(tableClient, tableClient['id'].eq(tableJournal['client_id']))
                if not QtGui.qApp.isDisplayStaff():
                    condJournal.append('NOT (%s)' % getStaffCondition(tableClient['id'].name()))

            if isChkClientSex:
                condJournal.append(tableClient['sex'].eq(clientSex))
            if self.clientFilter:
                clientId = self.clientFilter.get('clientId', None)
                if clientId:
                    accountingSystemId = self.clientFilter.get('accountingSystemId',  None)
                    if accountingSystemId:
                        queryTable = queryTable.innerJoin(tableIdentification,
                                                          tableIdentification['client_id'].eq(tableClient['id']))
                        condJournal.extend([
                            tableIdentification['accountingSystem_id'].eq(accountingSystemId),
                            tableIdentification['identifier'].eq(clientId)
                        ])
                    else:
                        condJournal.append(tableClient['id'].eq(clientId))
                else:
                    clientFirstName = self.clientFilter.get('clientFirstName', None)
                    clientLastName  = self.clientFilter.get('clientLastName', None)
                    clientPatrName  = self.clientFilter.get('clientPatrName', None)
                    clientBirthDay  = self.clientFilter.get('clientBirthDay', None)
                    if clientFirstName:
                        condJournal.append(tableClient['firstName'].eq(clientFirstName))
                    if clientLastName:
                        condJournal.append(tableClient['lastName'].eq(clientLastName))
                    if clientPatrName:
                        condJournal.append(tableClient['patrName'].eq(clientPatrName))
                    if clientBirthDay:
                        if clientBirthDay.isValid():
                            condJournal.append(tableClient['birthDate'].dateEq(clientBirthDay))
            else:
                if self.btnCalendar.isChecked():
                    condJournal.append(tableJournal['datetimeTaken'].dateEq(self.calendar.selectedDate()))
                else:
                    condJournal.append(tableJournal['datetimeTaken'].dateBetween(self.edtDateFrom.date(), 
                                                                                 self.edtDateTo.date()))
            if not isChkTissueType:
                condJournal.append(tableJournal['tissueType_id'].eq(self.tblTissueTypes.currentItemId()))
            setPersonIdList  = self.getSetPersonIdList()
            condJournal.append(tableAction['setPerson_id'].inlist(setPersonIdList))
            if execPersonId:
                if execPersonId == -1:
                    condJournal.append(tableJournal['execPerson_id'].isNull())
                else:
                    condJournal.append(tableJournal['execPerson_id'].eq(execPersonId))
            else:
                if execPersonIdList:
                    condJournal.append(tableJournal['execPerson_id'].inlist(execPersonIdList))
            if isChkStatus:
                value = tableAction['status'].eq(chkStatus)
                condJournal.append(value)
                condActionForAllActionsCountLabel.append(value)
            if isChkUrgent:
                value = tableAction['isUrgent'].eq(1)
                condJournal.append(value)
                condActionForAllActionsCountLabel.append(value)
                
            if eventTypeId or isChkRelegateOrg:
                queryTable = queryTable.innerJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
                if eventTypeId:
                    condJournal.append(tableEvent['eventType_id'].eq(eventTypeId))
                if isChkRelegateOrg:
                    orgId = self.tissueJournalFilter.get('relegateOrgId', None)
                    
                    if not orgId or orgId == QtGui.qApp.currentOrgId():
                        condJournal.append(db.joinOr([tableEvent['relegateOrg_id'].eq(QtGui.qApp.currentOrgId()),
                                                      tableEvent['relegateOrg_id'].isNull()]))
                    else:
                        condJournal.append(tableEvent['relegateOrg_id'].eq(orgId))
                
            if financeTypeId:
                value = tableAction['finance_id'].eq(financeTypeId)
                condJournal.append(value)
                condActionForAllActionsCountLabel.append(value)
            if actionTypeId:
                actualActionTypeIdList = db.getDescendants('ActionType', 'group_id', actionTypeId)
                value = tableAction['actionType_id'].inlist(actualActionTypeIdList)
                condJournal.append(value)
                condActionForAllActionsCountLabel.append(value)
            if serviceId:
                value = db.existsStmt(tableActionTypeService, [tableActionTypeService['service_id'].eq(serviceId),
                                                               tableActionTypeService['master_id'].eq(tableAction['actionType_id'])])
                condJournal.append(value)
                condActionForAllActionsCountLabel.append(value)
            if execOrg:
                execOrgCond = [tableAction['org_id'].eq(execOrg)]
                if execOrg == QtGui.qApp.currentOrgId():
                    execOrgCond.append(tableAction['org_id'].isNull())
                value = db.joinOr(execOrgCond)
                condJournal.append(value)
                condActionForAllActionsCountLabel.append(value)
            if isChkPreliminaryResult:
                value = tableAction['preliminaryResult'].eq(chkPreliminaryResult)
                condJournal.append(value)
                condActionForAllActionsCountLabel.append(value)
            if isChkWithoutSampling:
                condJournal.append(db.notExistsStmt(tableProbe, tableProbe['takenTissueJournal_id'].eq(tableJournal['id'])))

            order = [tableJournal['externalId']] if not isChkTissueType else []
            if self.clientFilter and order:
                order = [tableClient['lastName'], tableClient['firstName'], tableClient['patrName']]

        order.append(tableJournal['id'])

        fields = [tableJournal['id'], tableJournal['client_id']]

        stmt = db.selectStmt(queryTable, fields, condJournal, order=order, isDistinct=True)
        query = db.query(stmt)

        idList = []
        clientIdList = []
        while query.next():
            record = query.record()
            clientId = forceRef(record.value('client_id'))
            if not clientId in clientIdList:
                clientIdList.append(clientId)
            idList.append(forceRef(record.value('id')))
        self.updateClientCountLabel(len(clientIdList))
        self.updateAllActionsCountLabel(idList, condActionForAllActionsCountLabel)
        return idList

    def updateTissueJournalList(self):
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        self.tblTissueJournal.setIdList(self.getTissueJournalIdList())
        tissueJournalIdList = self.modelTissueJournal.idList()
        if not tissueJournalIdList:
            self.btnSend.setEnabled(False)
        elif not self.btnSend.isEnabled():
            self.btnSend.setEnabled(True)
        self.lblTissueJournalCount.setText(u'Количество записей в журнале биоматериалов: %d '%len(tissueJournalIdList))
        QtGui.qApp.restoreOverrideCursor()

    def updateClientCountLabel(self, clientCount):
        self.lblClientCount.setText(u' Количество пациентов: %d'%clientCount)

    def updateAllActionsCountLabel(self, tissueJournalIdList=None, condActionForAllActionsCountLabel=None):
        if not tissueJournalIdList:
            tissueJournalIdList = []
        if not condActionForAllActionsCountLabel:
            condActionForAllActionsCountLabel = []
        db = QtGui.qApp.db
        table = db.table('Action')
        cond = [table['takenTissueJournal_id'].inlist(tissueJournalIdList), table['deleted'].eq(0)]
        cond.extend(condActionForAllActionsCountLabel)
        amountsSum = forceDouble(db.getSum(table, 'amount', cond))
        self.lblAllActionsCount.setText(u'Число исследований: %.2f'%amountsSum)

    def updateTissueJournalFilter(self):
        self.tissueJournalFilter['execPersonIdList'] = self.getExecPersonIdList()
        self.tissueJournalFilter['isChkStatus']      = self.chkStatus.isChecked()
        self.tissueJournalFilter['isChkUrgent']      = self.chkUrgent.isChecked()
        self.tissueJournalFilter['chkStatus']        = self.cmbStatus.currentIndex()
        
        self.tissueJournalFilter['isChkPreliminaryResult'] = self.chkPreliminaryResult.isChecked()
        self.tissueJournalFilter['chkPreliminaryResult']   = self.cmbPreliminaryResult.currentIndex()
        
        self.tissueJournalFilter['isChkRelegateOrg'] = self.chkRelegateOrg.isChecked()
        self.tissueJournalFilter['relegateOrgId']    = self.cmbRelegateOrg.value()
        self.tissueJournalFilter['execPersonId']     = self.cmbExecPerson.value()
        self.tissueJournalFilter['eventTypeId']      = self.cmbEventType.value()
        self.tissueJournalFilter['isChkTissueType']  = self.chkTissueType.isChecked()
        self.tissueJournalFilter['financeTypeId']    = self.cmbFinanceType.value()
        self.tissueJournalFilter['actionTypeId']     = self.cmbActionType.value()
        self.tissueJournalFilter['serviceId']        = self.cmbService.value()
        self.tissueJournalFilter['isChkClientSex']   = self.chkClientSex.isChecked()
        self.tissueJournalFilter['clientSex']        = self.cmbClientSex.currentIndex()
        self.tissueJournalFilter['execOrg']          = self.cmbExecOrg.value()
        
        self.tissueJournalFilter['isChkWithoutSampling'] = self.chkWithoutSampling.isChecked()

    def updateResultFilter(self):
        self.resultActionsFilter['chkResultRelegateOrg'] =  self.chkResultRelegateOrg.isChecked()
        self.resultActionsFilter['resultRelegateOrgId'] =  self.cmbResultRelegateOrg.value()
        self.resultActionsFilter['resultDateFrom'] =  self.edtResultDateFrom.date()
        self.resultActionsFilter['resultDateTo'] = self.edtResultDateTo.date()
        self.resultActionsFilter['resultTissueIdentifierFrom'] = self.edtResultTissueIdentifierFrom.text()
        self.resultActionsFilter['resultTissueIdentifierTo'] = self.edtResultTissueIdentifierTo.text()
        self.resultActionsFilter['chkResultTissueRegistrator'] = self.chkResultTissueRegistrator.isChecked()
        self.resultActionsFilter['resultTissueRegistrator'] = self.cmbResultTissueRegistrator.value()
        self.resultActionsFilter['chkResultEventType'] = self.chkResultEventType.isChecked()
        self.resultActionsFilter['resultEventType'] = self.cmbResultEventType.value()
        self.resultActionsFilter['resultService'] = self.cmbResultService.value()
        self.resultActionsFilter['chkResultUrgent'] = self.chkResultUrgent.isChecked()
        self.resultActionsFilter['chkResultClientSex'] =  self.chkResultClientSex.isChecked()
        self.resultActionsFilter['resultClientSex'] = self.cmbResultClientSex.currentIndex()+1
        self.resultActionsFilter['chkResultStatus'] = self.chkResultStatus.isChecked()
        self.resultActionsFilter['resultStatus'] = self.cmbResultStatus.currentIndex()
        
        self.resultActionsFilter['chkResultPreliminaryResult'] = self.chkResultPreliminaryResult.isChecked()
        self.resultActionsFilter['resultPreliminaryResult']    = self.cmbResultPreliminaryResult.currentIndex()
        
        self.resultActionsFilter['chkResultFinance'] = self.chkResultFinance.isChecked()
        self.resultActionsFilter['resultFinanceType'] = self.cmbResultFinanceType.value()
        self.resultActionsFilter['chkResultOnlyTests'] = self.chkResultOnlyTests.isChecked()

        self.resultActionsFilter['chkResultActionSetPerson'] = self.chkResultActionSetPerson.isChecked()
        self.resultActionsFilter['resultActionSetPersonOrgStructure'] = self.cmbResultActionSetPersonOrgStructure.value()
        self.resultActionsFilter['resultActionSetPersonSpeciality'] = self.cmbResultActionSetPersonSpeciality.value()
        self.resultActionsFilter['chkResultActionExecPerson'] = self.chkResultActionExecPerson.isChecked()
        self.resultActionsFilter['resultActionExecPerson'] = self.cmbResultActionExecPerson.value()
        self.resultActionsFilter['chkResultActionAssistant'] = self.chkResultActionAssistant.isChecked()
        self.resultActionsFilter['resultActionAssistant'] = self.cmbResultActionAssistant.value()
        self.resultActionsFilter['chkResultClientId'] = self.chkResultClientId.isChecked()
        self.resultActionsFilter['resultClientIdAccountingSystem'] = self.cmbResultClientIdAccountingSystem.value()
        self.resultActionsFilter['resultClientId'] = self.edtResultClientId.text()

        self.resultActionsFilter['resultExecOrg'] = self.cmbResultExecOrg.value()
        
        self.resultActionsFilter['chkResultWithoutSampling'] = self.chkResultWithoutSampling.isChecked()

    def updateActionList(self, tissueJournalId):
        QtGui.qApp.callWithWaitCursor(self,
                                      self.tblTissueJournalActions.setIdList,
                                      self.getActionIdList(tissueJournalId))
        actionIdList = self.modelTissueJournaActions.idList()
        self.lblActionsCount.setText(u'Количество действий: %d'%len(actionIdList))

    def getActionIdList(self, tissueJournalIdList):
        if tissueJournalIdList:
            if type(tissueJournalIdList) == int:
                tissueJournalIdList = [tissueJournalIdList]
            db = QtGui.qApp.db
            tableAction = db.table('Action')
            tableActionTypeService = db.table('ActionType_Service')
            queryTable = tableAction

            cond = [
                tableAction['deleted'].eq(0),
                tableAction['takenTissueJournal_id'].inlist(tissueJournalIdList)
            ]

            actionTypeId = self.tissueJournalFilter.get('actionTypeId', None)
            if actionTypeId:
                actualActionTypeIdList = db.getDescendants('ActionType', 'group_id', actionTypeId)
                cond.append(tableAction['actionType_id'].inlist(actualActionTypeIdList))

            serviceId = self.tissueJournalFilter.get('serviceId', None)
            if serviceId:
                cond.append(db.existsStmt(tableActionTypeService, [tableActionTypeService['service_id'].eq(serviceId),
                                                                   tableActionTypeService['master_id'].eq(tableAction['actionType_id'])]))

            isChkStatus = self.tissueJournalFilter.get('isChkStatus', None)
            if isChkStatus:
                cond.append(tableAction['status'].eq(self.tissueJournalFilter.get('chkStatus', 0)))

            isChkUrgent = self.tissueJournalFilter.get('isChkUrgent', None)
            if isChkUrgent:
                cond.append(tableAction['isUrgent'].eq(1))

            financeTypeId = self.tissueJournalFilter.get('financeTypeId', None)
            if financeTypeId:
                cond.append(tableAction['finance_id'].eq(financeTypeId))
                
            isChkRelegateOrg = self.tissueJournalFilter.get('isChkRelegateOrg', False)
            if isChkRelegateOrg:
                orgId = self.tissueJournalFilter.get('relegateOrgId', None)
                tableEvent = db.table('Event')
                queryTable = queryTable.leftJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
                if not orgId or orgId == QtGui.qApp.currentOrgId():
                    cond.append(db.joinOr([tableEvent['relegateOrg_id'].eq(QtGui.qApp.currentOrgId()),
                                           tableEvent['relegateOrg_id'].isNull()]))
                else:
                    cond.append(tableEvent['relegateOrg_id'].eq(orgId))

            isChkPreliminaryResult = self.tissueJournalFilter.get('isChkPreliminaryResult', False)
            if isChkPreliminaryResult:
                chkPreliminaryResult = self.tissueJournalFilter.get('chkPreliminaryResult', 0)
                cond.append(tableAction['preliminaryResult'].eq(chkPreliminaryResult))

            actionIdList = db.getDistinctIdList(queryTable, tableAction['id'].name(), cond)
        else:
            actionIdList = []
        return actionIdList

    def resetFilter(self):
        self.tissueJournalFilter.clear()

        self.chkStatus.setChecked(False)
        self.chkUrgent.setChecked(False)
        self.chkTissueType.setChecked(False)
        self.cmbStatus.setEnabled(False)
        self.chkPreliminaryResult.setChecked(False)
        self.cmbPreliminaryResult.setEnabled(False)
        self.chkRelegateOrg.setChecked(False)
        self.cmbRelegateOrg.setValue(None)
        self.cmbRelegateOrg.setEnabled(False)
        self.cmbExecPerson.setValue(None)
        self.cmbEventType.setValue(None)
        self.cmbFinanceType.setValue(None)
        self.cmbActionType.setValue(None)
        self.cmbService.setValue(None)
        self.cmbExecOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.chkClientSex.setChecked(False)
        self.cmbClientSex.setEnabled(False)
        self.cmbExecOrg.setValue(QtGui.qApp.currentOrgId())
        self.chkWithoutSampling.setChecked(False)

    def emitChkWidgetClicked(self, widget, value=None):
        if value is None:
            value = widget.isChecked()
        widget.emit(QtCore.SIGNAL('clicked(bool)'), value)

    def resetResultFilter(self):
        self.resultActionsFilter.clear()

        self.edtResultDateFrom.setDate(QtCore.QDate.currentDate())
        self.edtResultDateTo.setDate(QtCore.QDate.currentDate())
        self.edtResultTissueIdentifierFrom.setText('')
        self.edtResultTissueIdentifierTo.setText('')

        self.chkResultTissueRegistrator.setChecked(False)
        self.emitChkWidgetClicked(self.chkResultTissueRegistrator)
        self.cmbResultTissueRegistrator.setValue(None)
        
        self.chkResultRelegateOrg.setChecked(False)
        self.emitChkWidgetClicked(self.chkResultRelegateOrg)
        self.cmbResultRelegateOrg.setValue(None)

        self.chkResultEventType.setChecked(False)
        self.emitChkWidgetClicked(self.chkResultEventType)
        self.cmbResultEventType.setValue(None)

        self.cmbResultService.setValue(None)

        self.chkResultUrgent.setChecked(False)
        self.emitChkWidgetClicked(self.chkResultUrgent)

        self.chkResultClientSex.setChecked(False)
        self.emitChkWidgetClicked(self.chkResultClientSex)
        self.cmbResultClientSex.setCurrentIndex(0)

        self.chkResultStatus.setChecked(False)
        self.emitChkWidgetClicked(self.chkResultStatus)
        self.cmbResultStatus.setCurrentIndex(0)
        
        self.chkResultPreliminaryResult.setChecked(False)
        self.emitChkWidgetClicked(self.chkResultPreliminaryResult)
        self.cmbResultPreliminaryResult.setCurrentIndex(0)

        self.chkResultFinance.setChecked(False)
        self.emitChkWidgetClicked(self.chkResultFinance)
        self.cmbResultFinanceType.setValue(None)

        self.chkResultOnlyTests.setChecked(False)
        self.emitChkWidgetClicked(self.chkResultOnlyTests)

        self.chkResultActionSetPerson.setChecked(False)
        self.emitChkWidgetClicked(self.chkResultActionSetPerson)
        self.cmbResultActionSetPersonOrgStructure.setValue(None)
        self.cmbResultActionSetPersonSpeciality.setValue(None)

        self.chkResultActionExecPerson.setChecked(False)
        self.emitChkWidgetClicked(self.chkResultActionExecPerson)
        self.cmbResultActionExecPerson.setValue(None)

        self.chkResultActionAssistant.setChecked(False)
        self.emitChkWidgetClicked(self.chkResultActionAssistant)
        self.cmbResultActionAssistant.setValue(None)

        self.chkResultClientId.setChecked(False)
        self.emitChkWidgetClicked(self.chkResultClientId)
        self.cmbResultClientIdAccountingSystem.setValue(None)
        self.edtResultClientId.setText('')

        self.cmbResultExecOrg.setValue(QtGui.qApp.currentOrgId())
        
        self.chkResultWithoutSampling.setChecked(False)

    def editAction(self, actionId):
        dialog = CActionEditDialog(self)
        dialog.load(actionId)
        if dialog.exec_():
            index = self.tblTissueJournal.currentIndex()
            self.on_selectionModelTissueJournal_currentChanged(index, index)
            self.updateResultActionsFromAll()
            return dialog.itemId()
        return None

    def showClientInfo(self, id):
        if id:
            self.currentClientInfo = getClientInfo(id)
            clientBanner = formatClientBanner(self.currentClientInfo)
            self.txtClientInfoBrowser.setHtml(clientBanner)
        else :
            self.txtClientInfoBrowser.setText('')
            self.currentClientInfo = None

    def makeClientFilter(self):
        self.clientFilter.clear()
        if self.chkFilterId.isChecked():
            txt = forceStringEx(self.edtFilterId.text())
            self.clientFilter['accountingSystemId'] = self.cmbFilterAccountingSystem.value()
            if txt:
                if self.clientFilter['accountingSystemId']:
                    self.clientFilter['clientId'] = txt
                else:
                    try:
                        self.clientFilter['clientId'] = int(txt)
                    except ValueError:
                        self.clientFilter['clientId'] = -1
            else:
                self.clientFilter['clientId'] = None
        else:
            if self.chkFilterLastName.isChecked():
                self.clientFilter['clientLastName'] = nameCase(forceStringEx(self.edtFilterLastName.text()))
            if self.chkFilterFirstName.isChecked():
                self.clientFilter['clientFirstName'] = nameCase(forceStringEx(self.edtFilterFirstName.text()))
            if self.chkFilterPatrName.isChecked():
                self.clientFilter['clientPatrName'] = nameCase(forceStringEx(self.edtFilterPatrName.text()))
            if self.chkFilterBirthDay.isChecked():
                self.clientFilter['clientBirthDay'] = self.edtFilterBirthDay.date()

    def resetClientFilter(self, all=False):
        self.clientFilter.clear()
        self.chkFilterLastName.setChecked(False)
        self.chkFilterFirstName.setChecked(False)
        self.chkFilterPatrName.setChecked(False)
        self.chkFilterBirthDay.setChecked(False)
        self.edtFilterLastName.setEnabled(False)
        self.edtFilterFirstName.setEnabled(False)
        self.edtFilterPatrName.setEnabled(False)
        self.edtFilterBirthDay.setEnabled(False)
        if all:
            self.chkFilterId.setChecked(False)
            self.edtFilterId.setEnabled(False)
            self.cmbFilterAccountingSystem.setEnabled(False)

    def updateResultActionTypes(self, dependentsTissueTypeIdList):
        db = QtGui.qApp.db
        currentIndex = self.tblResultActionType.currentIndex()
        if currentIndex.isValid() and currentIndex.internalPointer():
            currentId = currentIndex.internalPointer().id()
        else:
            currentId = None
        tableActionType           = db.table('ActionType')
        tableActionTypeTissueType = db.table('ActionType_TissueType')
        
        if bool(dependentsTissueTypeIdList):
            cond = [tableActionTypeTissueType['tissueType_id'].inlist(dependentsTissueTypeIdList)]
            idList = db.getDistinctIdList(tableActionTypeTissueType, tableActionTypeTissueType['master_id'], cond)
            idList = db.getTheseAndParents(tableActionType, 'group_id', idList)

            serviceId = self.cmbResultService.value()
            if serviceId != self._previousResultServiceId:
                tableActionTypeService = db.table('ActionType_Service')
                cond = [tableActionTypeService['service_id'].eq(serviceId)]
                idListByService = db.getDistinctIdList(tableActionTypeService, tableActionTypeService['master_id'], cond)
                self._previousResultActionTypeIdListByService = db.getTheseAndParents(tableActionType, 'group_id', idListByService)
            if serviceId:
                idList = list(set(idList) & set(self._previousResultActionTypeIdListByService))

            self.modelResultActionType.setEnabledActionTypeIdList(idList)
            self.modelResultActionType.setDisabledActionTypeIdList(None)
            self.tblResultActionType.expandAll()
        else:
            serviceId = self.cmbResultService.value()
            if serviceId != self._previousResultServiceId:
                tableActionTypeService = db.table('ActionType_Service')
                cond = [tableActionTypeService['service_id'].eq(serviceId)]
                idListByService = db.getDistinctIdList(tableActionTypeService, tableActionTypeService['master_id'], cond)
                self._previousResultActionTypeIdListByService = db.getTheseAndParents(tableActionType, 'group_id', idListByService)
            idList = self._previousResultActionTypeIdListByService if serviceId else None

            self.modelResultActionType.setEnabledActionTypeIdList(idList)
            if idList:
                self.tblResultActionType.expandAll()
            else:
                self.tblResultActionType.collapseAll()
                self.tblResultActionType.expand(self.modelResultActionType.index(0, 0))
        index = self.modelResultActionType.findItemId(currentId)
        if not index:
            index = self.modelResultActionType.index(0, 0, None)
        self.tblResultActionType.setCurrentIndex(index)

    def updateResultActionsFromAll(self):
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        dependentsTestIdList = self.itemsSelector.getSlectedTableItems('rbTest')
        self.updateResultActions(dependentsTestIdList)
        QtGui.qApp.restoreOverrideCursor()

    def updateResultActions(self, dependentsTestIdList):
        db = QtGui.qApp.db
        currentIndex = self.tblResultActionType.currentIndex()
        if currentIndex.isValid():
            actualActionTypeIdList = self.modelResultActionType.getItemIdList(currentIndex)
            currentItem            = currentIndex.internalPointer()
            if bool(currentItem):
                actionTypeClass    = currentItem.class_()
                actionTypeId       = currentItem.id()
        else:
            actionTypeClass        = None
            actionTypeId           = 0
            actualActionTypeIdList = []

        begDate = self.resultActionsFilter.get('resultDateFrom', QtCore.QDate.currentDate())
        endDate = self.resultActionsFilter.get('resultDateTo', QtCore.QDate.currentDate())
        chkResultRelegateOrg = self.resultActionsFilter.get('chkResultRelegateOrg', False)
        resultRelegateOrgId  = self.resultActionsFilter.get('resultRelegateOrgId', None)
        chkResultWithoutSampling = self.resultActionsFilter.get('chkResultWithoutSampling', False)

        tableClient               = db.table('Client')
        tableEvent                = db.table('Event')
        tableAction               = db.table('Action')
        tableProbe                = db.table('Probe')
        tableActionType           = db.table('ActionType')
        tableActionProperty       = db.table('ActionProperty')
        tableActionPropertyType   = db.table('ActionPropertyType')
        tableTakenTissueJournal   = db.table('TakenTissueJournal')
        tableActionPropertyString = db.table('ActionProperty_String')

        condTakenTissue = [
            tableTakenTissueJournal['deleted'].eq(0)
        ]

        if chkResultWithoutSampling:
            condTakenTissue.append(db.notExistsStmt(tableProbe, tableProbe['takenTissueJournal_id'].eq(tableTakenTissueJournal['id'])))

        if begDate.isValid():
            condTakenTissue.append(tableTakenTissueJournal['datetimeTaken'].dateGe(begDate))

        if endDate.isValid():
            condTakenTissue.append(tableTakenTissueJournal['datetimeTaken'].dateLe(endDate))

        if self.resultActionsFilter.get('chkResultTissueRegistrator', False):
            registratorId = self.cmbResultTissueRegistrator.value()
            if registratorId:
                condTakenTissue.append(tableTakenTissueJournal['execPerson_id'].eq(registratorId))

        tissueIdentifierFrom = forceStringEx(self.resultActionsFilter.get('resultTissueIdentifierFrom', ''))
        tissueIdentifierTo = forceStringEx(self.resultActionsFilter.get('resultTissueIdentifierTo', ''))
        if bool(tissueIdentifierFrom):
            if bool(tissueIdentifierTo):
                fullTissueIdentifierFrom = (6-len(tissueIdentifierFrom))*'0'+tissueIdentifierFrom
                fullTissueIdentifierTo   = (6-len(tissueIdentifierTo))*'0'+tissueIdentifierTo
                firstTypeCond = db.joinAnd([tableTakenTissueJournal['externalId'].ge(fullTissueIdentifierFrom),
                               tableTakenTissueJournal['externalId'].le(fullTissueIdentifierTo)])
                fullTissueIdentifierFrom = tissueIdentifierFrom+(6-len(tissueIdentifierFrom))*'0'
                fullTissueIdentifierTo   = tissueIdentifierTo+(6-len(tissueIdentifierTo))*'0'
                secondTypeCond = db.joinAnd([tableTakenTissueJournal['externalId'].ge(fullTissueIdentifierFrom),
                                  tableTakenTissueJournal['externalId'].le(fullTissueIdentifierTo)])
                condTakenTissue.append(firstTypeCond)
            else:
                condTakenTissue.append(tableTakenTissueJournal['externalId'].like('%'+tissueIdentifierFrom+'%'))

        takenTissueIdListByPeriod = db.getDistinctIdList(tableTakenTissueJournal, 'id', condTakenTissue)
        if bool(takenTissueIdListByPeriod):
            queryTable = tableAction.innerJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
            queryTable = queryTable.leftJoin(tableActionProperty, tableActionProperty['action_id'].eq(tableAction['id']))

            cond = [tableAction['takenTissueJournal_id'].inlist(takenTissueIdListByPeriod),
                    tableAction['deleted'].eq(0)]

            if chkResultRelegateOrg:
                if not resultRelegateOrgId or resultRelegateOrgId == QtGui.qApp.currentOrgId():
                    cond.append(db.joinOr([tableEvent['relegateOrg_id'].eq(QtGui.qApp.currentOrgId()),
                                           tableEvent['relegateOrg_id'].isNull()]))
                else:
                    cond.append(tableEvent['relegateOrg_id'].eq(resultRelegateOrgId))
                
                
            if self.resultActionsFilter.get('chkResultClientSex', False):
                queryTable = queryTable.innerJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))
                clientSex = self.resultActionsFilter.get('resultClientSex', 0)
                cond.append(tableClient['sex'].eq(clientSex))

            if self.resultActionsFilter.get('chkResultActionSetPerson', False):
                setPersonId = self.resultActionsFilter.get('resultActionSetPerson', None)
                if bool(setPersonId):
                    cond.append(tableAction['setPerson_id'].eq(setPersonId))
                else:
                    setPersonIdList = self.getResultSetPersonIdListByOrgStructure()
                    if bool(setPersonIdList):
                        cond.append(tableAction['setPerson_id'].inlist(setPersonIdList))
                    setPersonSprcialityId = self.resultActionsFilter.get('resultActionSetPersonSpeciality', None)
                    if setPersonSprcialityId:
                        tablePerson = db.table('Person')
                        queryTable = tableAction.innerJoin(tablePerson,
                                                           tablePerson['id'].eq(tableAction['setPerson_id']))
                        cond.append(tablePerson['speciality_id'].eq(setPersonSprcialityId))

            if self.resultActionsFilter.get('chkResultActionExecPerson', False):
                execPersonId = self.resultActionsFilter.get('resultActionExecPerson', None)
                if bool(execPersonId):
                    if execPersonId == -1:
                        cond.append(tableAction['person_id'].isNull())
                    else:
                        cond.append(tableAction['person_id'].eq(execPersonId))

            if self.resultActionsFilter.get('chkResultActionAssistant', False):
                assistantId = self.resultActionsFilter.get('resultActionAssistant', None)
                tableAssistant = db.table('Action_Assistant')
                tableAssistantType = db.table('rbActionAssistantType')
                if bool(assistantId):
                    if assistantId == -1:
                        cond.append(db.notExistsStmt(tableAssistant.innerJoin(tableAssistantType, tableAssistantType['id'].eq(tableAssistant['assistantType_id'])),
                                                     [tableAssistant['action_id'].eq(tableAction['id']),
                                                      tableAssistantType['code'].like('assistant')]))
                    else:
                        cond.append(db.existsStmt(tableAssistant.innerJoin(tableAssistantType, tableAssistantType['id'].eq(tableAssistant['assistantType_id'])),
                                                  [tableAssistant['action_id'].eq(tableAction['id']),
                                                   tableAssistant['person_id'].eq(assistantId),
                                                   tableAssistantType['code'].like('assistant')]))

            if self.resultActionsFilter.get('chkResultClientId', False):
                clientId = forceStringEx(self.resultActionsFilter.get('resultClientId', ''))
                if clientId:
                    accountingSystemId = self.resultActionsFilter.get('resultClientIdAccountingSystem', None)
                    if accountingSystemId:
                        tableIdentification = db.table('ClientIdentification')
                        cond.append(db.existsStmt(tableIdentification,
                            [tableIdentification['client_id'].eq(tableEvent['client_id']),
                             tableIdentification['accountingSystem_id'].eq(accountingSystemId),
                             tableIdentification['identifier'].eq(clientId)]))
                    else:
                        try:
                            clientId = int(clientId)
                        except:
                            return
                        cond.append(tableEvent['client_id'].eq(clientId))

            resultEventType = self.resultActionsFilter.get('resultEventType', None)
            if self.resultActionsFilter.get('chkResultEventType', False) and resultEventType:
                cond.append(tableEvent['eventType_id'].eq(resultEventType))

            if self.resultActionsFilter.get('chkResultUrgent', False):
                cond.append(tableAction['isUrgent'].eq(1))

            if self.resultActionsFilter.get('chkResultStatus', False):
                cond.append(tableAction['status'].eq(self.resultActionsFilter.get('resultStatus', 0)))

            resultFinanceType = self.resultActionsFilter.get('resultFinanceType', None)
            if self.resultActionsFilter.get('chkResultFinance', False) and resultFinanceType:
                cond.append(tableAction['finance_id'].eq(resultFinanceType))

            if bool(actualActionTypeIdList):
                cond.append(tableAction['actionType_id'].inlist(actualActionTypeIdList))

            elif bool(actionTypeId):
                cond.append(tableAction['actionType_id'].eq(actionTypeId))
            else:
                self.setModelResultActionsIdList([])
                return

            resultExecOrg = self.resultActionsFilter.get('resultExecOrg', None)
            if resultExecOrg:
                resultExecOrgCond = [tableAction['org_id'].eq(resultExecOrg)]
                if resultExecOrg == QtGui.qApp.currentOrgId():
                    resultExecOrgCond.append(tableAction['org_id'].isNull())
                cond.append(db.joinOr(resultExecOrgCond))

            if bool(dependentsTestIdList):
                cond.append(db.existsStmt(tableActionPropertyType, [tableActionPropertyType['id'].eq(tableActionProperty['type_id']),
                                                                    tableActionPropertyType['test_id'].inlist(dependentsTestIdList)]))
                
            if self.resultActionsFilter.get('chkResultPreliminaryResult', False):
                cond.append(tableAction['preliminaryResult'].eq(self.resultActionsFilter.get('resultPreliminaryResult')))

            samplingNumberFrom = self.resultActionsFilter.get('resultSamplingNumberFrom', 0)
            samplingNumberTo   = self.resultActionsFilter.get('resultSamplingNumberTo', 0)
            if samplingNumberFrom:
                if samplingNumberTo:
                    if samplingNumberTo >= samplingNumberFrom:
                        cond.append(db.existsStmt(tableActionPropertyString, [tableActionPropertyString['value'].ge(samplingNumberFrom),
                                                                              tableActionPropertyString['value'].le(samplingNumberTo),
                                                                              tableActionPropertyString['id'].eq(tableActionProperty['id'])]))
                else:
                    cond.append(db.existsStmt(tableActionPropertyString, [tableActionPropertyString['value'].eq(samplingNumberFrom),
                                                                          tableActionPropertyString['id'].eq(tableActionProperty['id'])]))
            idList = db.getDistinctIdList(queryTable, tableAction['id'], cond)
        else:
            idList = []

        currentId = self.tblResultActions.currentItemId()
        self.setModelResultActionsIdList(idList)
        if currentId and currentId in idList:
            self.tblResultActions.setCurrentIndex(self.modelResultActions.index(idList.index(currentId), 0))
        else:
            self.tblResultActions.setCurrentIndex(self.modelResultActions.index(0, 0))
        if not bool(idList):
            self.modelResultProperties.setAction(None, None, None, None)

    def getResultSetPersonIdListByOrgStructure(self):
        treeIndex = self.cmbResultActionSetPersonOrgStructure._popupView.currentIndex()
        orgStructureIdList = self.getOrgStructureIdList(treeIndex)
        return self.getPersonIdList(orgStructureIdList)

    def setModelResultActionsIdList(self, idList):
        self.modelResultActions.setIdList(idList)
        self.lblResultActionsCount.setText(u'Количество действий: %d'%len(idList))

    def on_changeTableSelectedItems(self, tableName):
        tableName = unicode(tableName)
        updates = {u'rbTest'      : self.updateResultActions,
                   u'rbTissueType': self.updateResultActionTypes}
        tableSelectedIdList = self.itemsSelector.getSlectedTableItems(tableName)
        QtGui.qApp.callWithWaitCursor(self, updates.get(tableName, lambda val: val), tableSelectedIdList)

    def updateResultProperties(self, actionIndex):
        clientSex = clientAge = None
        if not actionIndex.isValid():
            actionIndex = self.tblResultActions.currentIndex()
            if not actionIndex.isValid():
                return
        else:
            actionRecord = self.tblResultActions.currentItem()
            action = CAction(record=actionRecord)
            db = QtGui.qApp.db
            actionEventId = forceRef(actionRecord.value('event_id'))
            clientId = self.modelResultActions.getClientId(actionEventId)
            table  = db.table('Client')
            record = db.getRecord(table, 'sex, birthDate', clientId)
            if record:
                clientSex       = forceInt(record.value('sex'))
                clientBirthDate = forceDate(record.value('birthDate'))
                eventDate       = forceDate(db.translate('Event', 'id', actionEventId, 'setDate'))
                clientAge       = calcAgeTuple(clientBirthDate, eventDate)
        self.modelResultProperties.setAction(action, clientId, clientSex, clientAge)
        n = self.modelResultProperties.rowCount()
        self.lblResultPropertiesCount.setText(u'Количество свойств: %d'%n)

    def getReportTitle(self):
        main = u'Лабораторный журнал'
        if self.tissueJournalFilter.get('isChkTissueType', False):
            add = ''
        else:
            tissueRecord = self.tblTissueTypes.currentItem()
            tissueName = forceString(tissueRecord.value('name'))
            add = u': биоматериал - %s' % tissueName
        return main+add

    def getReportSubTitle(self):
        widget = self.tabWidgetFilter.currentWidget()
        if widget == self.tabClient:
            clientInfo = self.currentClientInfo
            if bool(clientInfo) and bool(self.currentClientId):
                fullClientName = formatNameInt(clientInfo.lastName, clientInfo.firstName, clientInfo.patrName)
                return u'На пациента: %s (id%d)' % (fullClientName, self.currentClientId)
            return u''
        elif widget == self.tabCalendar:
            if self.btnCalendar.isChecked():
                date = forceString(self.calendar.selectedDate())
                return u'На дату: %s' % date
            else:
                dateFrom = forceString(self.edtDateFrom.date())
                dateTo   = forceString(self.edtDateTo.date())
                return u'На период дат: от %s по %s' % (dateFrom, dateTo)
            
        else:
            return u''

    def getClientIdentifierTypesList(self):
        recordList = QtGui.qApp.db.getRecordList('rbAccountingSystem', '*')
        self.mapAccounSystemNameToId = {}
        res = [u'id клиента']
        self.mapAccounSystemNameToId[u'id клиента'] = None
        for record in recordList:
            accountSystemName = forceString(record.value('name'))
            accountSystemId   = forceRef(record.value('id'))
            res.append(accountSystemName)
            self.mapAccounSystemNameToId[accountSystemName] = accountSystemId
        return res

    def getClientIdentifier(self, tissueJournalId):
        record = self.modelTissueJournal.getRecordById(tissueJournalId)
        clientId = forceRef(record.value('client_id'))
        if clientId:
            accounSystemName = self.clientIdentifierTypesList[self.previousSelectedClientIdentifier]
            identifierId = self.mapAccounSystemNameToId.get(accounSystemName, None)
            if identifierId:
                db = QtGui.qApp.db
                table = db.table('ClientIdentification')
                cond = [table['client_id'].eq(clientId),
                        table['accountingSystem_id'].eq(identifierId)]
                record = db.getRecordEx(table, 'identifier', cond)
                if record:
                    return forceString(record.value('identifier'))
            return clientId
        return ''

    def getPrintQuery(self):
        db = QtGui.qApp.db

        tableTissueJournal = self.tableTissueJournal
        tableAction        = self.tableAction
        tableTissue        = db.table('rbTissueType')
        tableClient        = self.tableClient
        tableActionType    = db.table('ActionType')
        tableEvent         = db.table('Event')
        tableDiagnostic    = db.table('Diagnostic')
        tableDiagnosis     = db.table('Diagnosis')
        tablePerson        = db.table('vrbPersonWithSpeciality')

        lastDiagTypeId = forceRef(db.translate('rbDiagnosisType', 'code', '1', 'id'))
        mainDiagTypeId = forceRef(db.translate('rbDiagnosisType', 'code', '2', 'id'))

        subSelectCondDiagnostic = [tableDiagnostic['event_id'].eq(tableEvent['id']),
                                   tableDiagnostic['diagnosisType_id'].inlist([lastDiagTypeId, mainDiagTypeId])]
        subSelectDiagnostic = db.selectStmt(tableDiagnostic, tableDiagnostic['id'], subSelectCondDiagnostic, limit = 1)

        queryTable = tableTissueJournal.innerJoin(tableAction, tableAction['takenTissueJournal_id'].eq(tableTissueJournal['id']))
        queryTable = queryTable.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
        queryTable = queryTable.innerJoin(tableTissue, tableTissue['id'].eq(tableTissueJournal['tissueType_id']))
        queryTable = queryTable.innerJoin(tableClient, tableClient['id'].eq(tableTissueJournal['client_id']))
        queryTable = queryTable.innerJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
        queryTable = queryTable.leftJoin(tablePerson, tablePerson['id'].eq(tableEvent['setPerson_id']))
        queryTable = queryTable.leftJoin(tableDiagnostic, [tableDiagnostic['event_id'].eq(tableEvent['id']),
                                                           tableDiagnostic['id'].name()+'=('+subSelectDiagnostic+')'])
        queryTable = queryTable.leftJoin(tableDiagnosis, tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']))

        existsIdList = self.modelTissueJournal.idList()

        fields = [
                  tableTissueJournal['id'],
                  tableTissueJournal['externalId'],
                  'CONCAT('+', '.join([
                                      tableClient['lastName'].name(),
                                      tableClient['firstName'].name(),
                                      tableClient['patrName'].name()
                                      ])+') AS fullClientName',
                  tableTissue['name'].alias('tissueTypeName'),
                  tableActionType['code'].alias('actionTypeCode'),
                  tableActionType['name'].alias('actionTypeName'),
                  tableAction['note'].alias('actionNote'),
                  tableAction['MKB'].alias('actionMKB'),
                  tableAction['amount'].alias('actionAmount'),
                  tableDiagnosis['MKB'].alias('diagnosisMKB'),
                  tableEvent['id'].alias('eventId'),
                  tablePerson['name'].alias('eventSetPerson')
                  ]
        cond = [tableTissueJournal['id'].inlist(existsIdList)]
        actionTypeId = self.tissueJournalFilter.get('actionTypeId', None)
        if actionTypeId:
            actualActionTypeIdList = db.getDescendants('ActionType', 'group_id', actionTypeId)
            cond.append(tableAction['actionType_id'].inlist(actualActionTypeIdList))
        if not QtGui.qApp.isDisplayStaff():
            cond.append('NOT (%s)' % getStaffCondition(tableClient['id'].name()))
        if self.tabWidgetFilter.currentWidget() == self.tabClient:
            order = [tableTissueJournal['externalId'].name()]
        else:
            if self.clientIdentifierSelector.orderBy() == 0:
                order = [tableTissueJournal['externalId'].name()]
            else:
                order = ['fullClientName', tableTissueJournal['externalId'].name()]
        stmt = db.selectStmt(queryTable, fields, cond,  order = order)
        query = db.query(stmt)
        return query

    def getTableTissueJournalValues(self, tissueJournalId, maxClientIdentifier):
        model = self.modelTissueJournal
        modelIdList = model.idList()
        values = {}
        if tissueJournalId in modelIdList:
            row = modelIdList.index(tissueJournalId)
            columns = ['fio', 'tissueTypeName', 'externalId', 'status', 'datetime', 'person', 'note', 'amount', 'unit']
            for col, colName in enumerate(columns):
                value = forceString(model.data(model.createIndex(row, col+1)))
                if col == 0:
                    fioValueList = value.split(' ')
                    if len(fioValueList) > 1:
                        value = fioValueList[0] + ' \n' + ' '.join(fioValueList[1:])
                values[colName] = value
            identifier = self.getClientIdentifier(tissueJournalId)
            if isinstance(identifier, basestring):
                text = identifier
            elif isinstance(identifier, int):
                text = unicode(identifier)
                if self.previousSelectedClientIdentifier > 0:
                    text = u'(id)'+text
            else:
                text = ''
            localClientIdentifier = len(text)
            if localClientIdentifier > maxClientIdentifier:
                maxClientIdentifier = localClientIdentifier
            values['clientIdentifier'] = text
        return values, maxClientIdentifier

    def getPrintColums(self, maxClientIdentifier):
        # в принципе тоже самое что и во вьюшке + actions на каждую запись журнала
        notNeedCount = 0
        for smthNeed in [self.previousChkNeedMKB,
                         self.previousChkNeedPerson,
                         self.previousChkNeedDatetime,
                         self.previousChkNeedStatus,
                         self.tissueJournalFilter.get('isChkTissueType', False),
                         self.previousChkNeedAmountAndUnit,
                         self.tabWidgetFilter.currentWidget() != self.tabClient]:
            notNeedCount += 1 if not smthNeed else 0
        resultColumnPercent     = 12
        noteColumnPercent       = 8
        actionTypeColumnPercent = 10
        if notNeedCount > 0:
            resultColumnPercent += 8
        if notNeedCount > 1:
            noteColumnPercent *= 2
        if notNeedCount > 2:
            actionTypeColumnPercent *= 2
        tableColumns = [
            ('2%', [u'№'],  CReportBase.AlignLeft),
            ('11%', [u'ФИО'],  CReportBase.AlignLeft),
            ('%d='%maxClientIdentifier, [self.clientIdentifierTypesList[self.previousSelectedClientIdentifier]],  CReportBase.AlignLeft),
            ('7%', [u'Тип биоматериала'],  CReportBase.AlignLeft),
            ('7%', [u'ИБМ'], CReportBase.AlignLeft),
            ('5%', [u'Статус'], CReportBase.AlignLeft),
            ('3%', [u'Кол-во биоматериала'],  CReportBase.AlignLeft),
            ('4%', [u'Ед.изм.'],  CReportBase.AlignLeft),
            ('5%', [u'Время'],  CReportBase.AlignLeft),
            ('9%', [u'Ответственный'],  CReportBase.AlignLeft),
            ('3%', [u'МКБ'], CReportBase.AlignLeft),
            (('%d'%actionTypeColumnPercent)+'%', [u'Услуга'], CReportBase.AlignLeft),
            ('4%', [u'Кол-во'], CReportBase.AlignLeft),
            (('%d'%resultColumnPercent)+'%', [u'Результат'], CReportBase.AlignLeft),
            (('%d'%noteColumnPercent)+'%', [u'Примечание'], CReportBase.AlignLeft)
        ]

        # главное учитывать все эти съезды в translateToList в makeTable.
        if not self.previousChkNeedMKB:
            del tableColumns[10] # МКБ
        if not self.previousChkNeedPerson:
            del tableColumns[9]  # ответственный
        if not self.previousChkNeedDatetime:
            del tableColumns[8]  # время
        if not self.previousChkNeedAmountAndUnit:
            del tableColumns[6]  # Кол-во биоматериала
            del tableColumns[6]  # Ед.изм.
        if not self.previousChkNeedStatus:
            del tableColumns[5]  # статус
        if not self.tissueJournalFilter.get('isChkTissueType', False):
            del tableColumns[3]  # тип биоматериала
        if self.tabWidgetFilter.currentWidget() == self.tabClient:
            # если фильтрация по пациенту, то колонку 'ФИО' тю-тю и все съезжает на -1
            del tableColumns[1]

        return tableColumns

    def makeTable(self, cursor, doc):
        needFio = self.tabWidgetFilter.currentWidget() != self.tabClient
        def translateToList(tissueJournalData, boldChars):
            result = []
            if needFio:
                result.append((tissueJournalData.get('fio', ''), boldChars))
            result.append((tissueJournalData.get('clientIdentifier', ''), boldChars))
            if self.tissueJournalFilter.get('isChkTissueType', False):
                result.append((tissueJournalData.get('tissueTypeName', ''), None))
            result.append((tissueJournalData.get('externalId', ''), boldChars))
            if self.previousChkNeedStatus:
                result.append((tissueJournalData.get('status', ''), None))
            if self.previousChkNeedAmountAndUnit:
                result.append((tissueJournalData.get('amount', ''), None))
                result.append((tissueJournalData.get('unit', ''), None))
            if self.previousChkNeedDatetime:
                result.append((tissueJournalData.get('datetime', ''), None))
            if self.previousChkNeedPerson:
                result.append((tissueJournalData.get('person', ''), None))
            return result

        clientIdType = None
        if not self.clientIdentifierTypesList:
            self.clientIdentifierTypesList = self.getClientIdentifierTypesList()
            self.clientIdentifierSelector.setClientIdentifierTypesList(self.clientIdentifierTypesList)
        if self.previousSelectedClientIdentifier is None:
            clientIdType = forceString(self.modelTissueJournal.headerData(0, QtCore.Qt.Horizontal))
            if clientIdType in self.clientIdentifierTypesList:
                self.previousSelectedClientIdentifier = self.clientIdentifierTypesList.index(clientIdType)
            else:
                self.previousSelectedClientIdentifier = 0
            self.clientIdentifierSelector.setPreviousSelectedClientIdentifier(self.previousSelectedClientIdentifier)
        self.clientIdentifierSelector.setEnabledOrderBy(self.tabWidgetFilter.currentWidget() != self.tabClient)
        resultPreferences, ok = self.clientIdentifierSelector.getItem()
        if ok:
            self.previousChkNeedAmountAndUnit = resultPreferences.needAmountAndUnit
            self.previousChkNeedStatus = resultPreferences.chkNeedStatus
            self.previousChkNeedDatetime = resultPreferences.chkNeedDatetime
            self.previousChkNeedPerson = resultPreferences.chkNeedPerson
            self.previousChkNeedMKB = resultPreferences.chkNeedMKB

            clientIdType = resultPreferences.clientIdType
            clientIdType = unicode(clientIdType)
            if clientIdType in self.clientIdentifierTypesList:
                self.previousSelectedClientIdentifier = self.clientIdentifierTypesList.index(clientIdType)
            else:
                self.previousSelectedClientIdentifier = 0
        else:
            self.previousSelectedClientIdentifier = 0

        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

        info, order, maxClientIdentifier = self.getStructPrintInfo()
        tableColumns = self.getPrintColums(maxClientIdentifier)
        table = createTable(cursor, tableColumns)
        existsEventIdListByTissueId = {}
        tableColumnsCount = len(tableColumns)
        boldChars = QtGui.QTextCharFormat()
        boldChars.setFontWeight(QtGui.QFont.Bold)
        for idxOrder, iOrder in enumerate(order):
            QtGui.qApp.stepProgressBar()
            QtGui.qApp.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
            data = info.get(iOrder, None)
            if data:
                tissueJournalData, actionsData = data
                i = table.addRow()
                table.setText(i, 0, idxOrder+1)
                iLast = 0
                for iValue, (value, charFormat) in enumerate(translateToList(tissueJournalData, boldChars)):
                    iLast = iValue+1
                    table.setText(i, iLast, value, charFormat=charFormat)
                mkbPrefix = 1
                previuosI = i
                for iActions, actionData in enumerate(actionsData):
                    if iActions:
                        i = table.addRow()
                    prefix = str(iActions+1)+')'
                    actionColumn = iLast
                    if self.previousChkNeedMKB:
                        actionColumn += 1 # МКБ
                        MKBdata, eventId, eventSetPerson = actionData[0]
                        existsEventIdList = existsEventIdListByTissueId.setdefault(iOrder, [])
                        if not eventId in existsEventIdList:
                            data  = u'%s\n%s' %(MKBdata, eventSetPerson)
                            value = ' '.join([str(mkbPrefix)+')', data])+'\n'
                            table.setText(i, actionColumn, value)
                            existsEventIdList.append(eventId)
                            mkbPrefix += 1

                    actionColumn += 1 # услуга
                    data = ' | '.join([actionData[1], actionData[2]])
                    value = ' '.join([prefix, data])+'\n'
                    table.setText(i, actionColumn, value)

                    actionColumn += 1 # Количество
                    data = actionData[3]
                    value = ' '.join([prefix, data])+'\n'
                    table.setText(i, actionColumn, value)

                    actionColumn += 1 # результат
                    data = actionData[4]
                    if bool(data):
                        value = ' '.join([prefix, data])+'\n'
                        table.setText(i, actionColumn, value)
                for col in range(iLast+1)+[tableColumnsCount-1]:
                    table.mergeCells(previuosI, col, iActions+1, 1)
        QtGui.qApp.stopProgressBar()
        QtGui.qApp.restoreOverrideCursor()
        return True

    def getStructPrintInfo(self):
        query = self.getPrintQuery()
        structTissueJournalDictById = {}
        tissueJournalIdOrder = []
        maxClientIdentifier = 0
        while query.next():
            record = query.record()
            tissueJournalId = forceRef(record.value('id'))
            if not tissueJournalId:
                continue
#            MKB             = forceString(record.value('actionMKB'))
#            if not bool(MKB):
            MKBStr          = forceString(record.value('diagnosisMKB'))
            eventId         = forceRef(record.value('eventId'))
            eventSetPerson  = forceString(record.value('eventSetPerson'))
            MKB = (MKBStr, eventId, eventSetPerson)
            actionAmount    = forceString(record.value('actionAmount'))
            actionTypeCode  = forceString(record.value('actionTypeCode'))
            actionTypeName  = forceString(record.value('actionTypeName'))
            actionNote      = forceString(record.value('actionNote'))
            if not tissueJournalId in structTissueJournalDictById.keys():
                tissueJournalIdOrder.append(tissueJournalId)
                tableValues, maxClientIdentifier = self.getTableTissueJournalValues(tissueJournalId,
                                                                                          maxClientIdentifier)
                actionInfoTuplesList = [(MKB, actionTypeCode, actionTypeName, actionAmount, actionNote)]
                structTissueJournalDictById[tissueJournalId] = [tableValues, actionInfoTuplesList]
            else:
                actionInfoTuple = (MKB, actionTypeCode, actionTypeName, actionAmount, actionNote)
                structTissueJournalDictById[tissueJournalId][1].append(actionInfoTuple)
        return structTissueJournalDictById, tissueJournalIdOrder, maxClientIdentifier

    def updateActionTypeComboBox(self):
        allTissueTypes =  self.chkTissueType.isChecked()
        serviceId = self.cmbService.value()

        cond = []

        if allTissueTypes:
            cond.append('EXISTS (SELECT ActionType_TissueType.`id` FROM ActionType_TissueType WHERE ActionType_TissueType.`tissueType_id` IS NOT NULL AND ActionType_TissueType.`master_id`=ActionType.`id`)')
        else:
            tissueTypeId = forceInt(self.tblTissueTypes.currentItemId())
            cond.append('EXISTS (SELECT ActionType_TissueType.`id` FROM ActionType_TissueType WHERE ActionType_TissueType.`tissueType_id`=%d AND ActionType_TissueType.`master_id`=ActionType.`id`)' % tissueTypeId)
        if serviceId:
            cond.append('EXISTS (SELECT ActionType_Service.`id` FROM ActionType_Service WHERE ActionType_Service.`service_id`=%d AND ActionType_Service.`master_id`=ActionType.`id`)'%serviceId)

        enabledActionTypeIdList = QtGui.qApp.db.getIdList('ActionType', 'ActionType.`id`', cond)
        fullEnabledActionTypeIdList = QtGui.qApp.db.getTheseAndParents('ActionType', 'group_id', enabledActionTypeIdList)
        self.cmbActionType.model().setEnabledActionTypeIdList(fullEnabledActionTypeIdList)

    def updateFilterWidgetsByIBM(self, value):
        chkWidgets = [self.chkTissueType, 
                      self.chkWithoutSampling, 
                      self.chkUrgent, 
                      self.chkClientSex, 
                      self.chkRelegateOrg, 
                      self.chkStatus, 
                      self.chkPreliminaryResult 
                     ]
        widgets = [self.cmbEventType, 
                   self.cmbService, 
                   self.cmbActionType, 
                   self.cmbFinanceType, 
                   self.cmbExecOrgStructure, 
                   self.cmbExecPerson, 
                   self.cmbExecOrg
                  ]
        
        if not value:
            for wgt in chkWidgets:
                wgt.setChecked(value)
                wgt.emit(QtCore.SIGNAL('clicked(bool)'), value)
        
        for wgt in widgets:
            wgt.setEnabled(value)
    
    def updateIMBFilter(self, value):
        if not value:
            self.chkIBM.setChecked(value)
            self.chkIBM.emit(QtCore.SIGNAL('clicked(bool)'), value)
    
    def loadPreferences(self, preferences):
        self.chkStatus.setChecked(forceBool(getVal(preferences, 'chkstatus', QtCore.QVariant())))
        if self.chkStatus.isChecked():
            self.cmbStatus.setEnabled(True)
            self.cmbStatus.setCurrentIndex(forceInt(getVal(preferences, 'cmbstatus', QtCore.QVariant)))
        CDialogBase.loadPreferences(self, preferences)

    def savePreferences(self):
        result = CDialogBase.savePreferences(self)
        setPref(result, 'chkstatus', self.chkStatus.isChecked())
        setPref(result, 'cmbstatus', self.cmbStatus.currentIndex())
        return result
    
    @QtCore.pyqtSlot(int)
    def on_edtResultSamplingNumberFrom_valueChanged(self, value):
        self.edtResultSamplingNumberTo.setEnabled(bool(value))

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtResultTissueIdentifierFrom_textEdited(self, text):
        text = forceStringEx(text)
        self.edtResultTissueIdentifierTo.setEnabled(bool(text))

    @QtCore.pyqtSlot(int)
    def on_cmbResultService_currentIndexChanged(self, index):
        dependentsTissueTypeIdList = self.itemsSelector.getSlectedTableItems('rbTissueType')
        self.updateResultActionTypes(dependentsTissueTypeIdList)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblResultActions_doubleClicked(self, index):
        actionId = self.tblResultActions.itemId(index)
        self.editAction(actionId)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblResultProperties_doubleClicked(self, index):
        if index.isValid():
            actionId = self.tblResultActions.currentItemId()
            self.editAction(actionId)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblTissueJournalActions_doubleClicked(self, index):
        actionId = self.tblTissueJournalActions.itemId(index)
        self.editAction(actionId)

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBoxFilter_clicked(self, button):
        if not self._tissueScanBarcodeActive:
            buttonCode = self.buttonBoxFilter.standardButton(button)
            if buttonCode == QtGui.QDialogButtonBox.Apply:
                self.updateTissueJournalFilter()
                # это плохая идея. self.on_tabWidgetFilter_currentChanged оказывается
                # переусложнённым.
                self.on_tabWidgetFilter_currentChanged(self.tabWidgetFilter.currentIndex(), insertionId=False)
            elif buttonCode == QtGui.QDialogButtonBox.Reset:
                self.resetClientFilter(all=True)
                self.resetFilter()
                self.updateTissueJournalList()
        else:
            self.resetIbmSearch()

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBoxResult_clicked(self, button):
        buttonCode = self.buttonBoxResult.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.updateResultFilter()
            self.updateResultActionsFromAll()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.resetResultFilter()
            self.updateResultActionsFromAll()

    @QtCore.pyqtSlot()
    def on_calendar_selectionChanged(self):
        self.updateTissueJournalList()

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtDateFrom_dateChanged(self, date):
        self.updateTissueJournalList()

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtDateTo_dateChanged(self, date):
        self.updateTissueJournalList()

    @QtCore.pyqtSlot(bool)
    def on_btnCalendar_clicked(self, b):
        self.updateTissueJournalList()

    @QtCore.pyqtSlot(bool)
    def on_btnDateRange_clicked(self, b):
        self.updateTissueJournalList()

    @QtCore.pyqtSlot(bool)
    def on_chkIBM_clicked(self, b):
        self.updateFilterWidgetsByIBM(not b)

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelTissueTypes_currentChanged(self, current, previous):
        if not self.chkTissueType.isChecked():
            self.updateActionTypeComboBox()
            self.setServiceStaticFilterByTissue(True)
        self.updateTissueJournalList()

    @QtCore.pyqtSlot(bool)
    def on_chkTissueType_clicked(self, value):
        self.updateActionTypeComboBox()
        self.setServiceStaticFilterByTissue(not value)
        self.updateIMBFilter(not value)

    @QtCore.pyqtSlot(bool)
    def on_chkWithoutSampling_clicked(self, value):
        self.updateIMBFilter(not value)

    @QtCore.pyqtSlot(bool)
    def on_chkUrgent_clicked(self, value):
        self.updateIMBFilter(not value)
    
    @QtCore.pyqtSlot(bool)
    def on_chkPreliminaryResult_clicked(self, value):
        self.updateIMBFilter(not value)

    @QtCore.pyqtSlot(bool)
    def on_chkStatus_clicked(self, value):
        self.updateIMBFilter(not value)

    @QtCore.pyqtSlot(bool)
    def on_chkRelegateOrg_clicked(self, value):
        self.updateIMBFilter(not value)

    @QtCore.pyqtSlot(bool)
    def on_chkClientSex_clicked(self, value):
        self.updateIMBFilter(not value)

    @QtCore.pyqtSlot(int)
    def on_cmbService_currentIndexChanged(self, index):
        self.updateActionTypeComboBox()

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelOrgStructure_currentChanged(self, current, previous):
        self.updateTissueJournalList()

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelTissueJournal_currentChanged(self, current, previous):
        currentItem = self.tblTissueJournal.currentItem()
        if currentItem:
            tissueJournalId = forceRef(currentItem.value('id'))

            actionContextList = getActionContextListByTissue(tissueJournalId)

            clientId = forceRef(currentItem.value('client_id'))
            self.currentClientId = clientId
            self.updateActionList(tissueJournalId)
            self.showClientInfo(clientId)
            self.btnSend.setEnabled(True)
        else:
            self.currentClientId = None
            self.updateActionList(None)
            self.showClientInfo(None)
            actionContextList = []
            self.btnSend.setEnabled(False)

        additionalCustomizePrintButton(self, self.tissueTabBtnPrint, actionContextList, otherActions=self.otherTissueActions)

    @QtCore.pyqtSlot(int)
    def on_cmbExecOrgStructure_currentIndexChanged(self, index):
        value = self.cmbExecOrgStructure.value()
        self.cmbExecPerson.setOrgStructureId(value)

    @QtCore.pyqtSlot()
    def on_btnSend_clicked(self):
        dlg = CSamplePreparationDialog(self)
        selectedTissueJournalIdList = self.getSelectedTissueJournalIdList()
        selectedTissueJournalIdCount = len(selectedTissueJournalIdList)

        self.connect(dlg, QtCore.SIGNAL('samplePreparationPassed()'), self.stepProgressBar)
        self.startProgressBar(selectedTissueJournalIdCount)
        dlg.automaticalSaveProbes(selectedTissueJournalIdList, isSilent=True)
        self.disconnect(dlg, QtCore.SIGNAL('samplePreparationPassed()'), self.stepProgressBar)
        self.stopProgressBar()

    def on_tabTissuePrintByTemplate(self, templateId):
        context = CInfoContext()

        if templateId in [printAction.id for printAction in self.tissueTabBtnPrint.additionalActions()]:
            self.on_tabTissuePrintByTemplate_additionalPrintAction(context, templateId)

        else:
            takenTissueJournalIdList = self.tblTissueJournal.selectedItemIdList()
            actionTypeId = self.tissueJournalFilter.get('actionTypeId', None)
            actualActionTypeIdList = QtGui.qApp.db.getDescendants('ActionType', 'group_id', actionTypeId) if actionTypeId else []
            actionTypeInfo = context.getInstance(CActionTypeInfo, CActionType(QtGui.qApp.db.getRecord('ActionType', '*', actionTypeId)) if actionTypeId else None)
            makeDependentActionIdListByTissueJournal(takenTissueJournalIdList, actualActionTypeIdList)
            takenTissueJournalListInfo = context.getInstance(CTakenTissueJournalWithActionsInfoList, tuple(takenTissueJournalIdList))
            data = {
                'actionType': actionTypeInfo,
                'takenTissueJournalItems' : takenTissueJournalListInfo
            }
            applyTemplate(self, templateId, data)

    def on_tabResultPrintByTemplate(self, templateId):
        context = CInfoContext()
        if templateId in [printAction.id for printAction in self.resultTabBtnPrint.additionalActions()]:
            self.on_tabResultPrintByTemplate_additionalPrintAction(context, templateId)
        else:
            actionsIdList = self.tblResultActions.selectedItemIdList()
            actionsInfo = context.getInstance(CTakenTissueJournalActionInfoList, tuple(actionsIdList))
            actionTypeId = self.tblResultActionType.model().itemId(self.tblResultActionType.currentIndex())
            actionTypeInfo = context.getInstance(CActionTypeInfo, CActionType(QtGui.qApp.db.getRecord('ActionType', '*', actionTypeId)) if actionTypeId else None)
            data = {
                'actionType': actionTypeInfo,
                'actions' : actionsInfo
            }
            applyTemplate(self, templateId, data)

    def on_tabResultPrintByTemplate_additionalPrintAction(self, context, templateId):
        actionIdList = self.filterActionsByTemplate(self.tblResultActions.selectedItemIdList(), templateId)
        self.additionalPrint(context, templateId, actionIdList)

    def additionalPrint(self, context, templateId, actionIdList):
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        dataList = []
        for actionId in actionIdList:
            actionRecord = QtGui.qApp.db.getRecord('Action', '*', actionId)
            eventId = forceRef(actionRecord.value('event_id'))
            eventInfo = context.getInstance(CEventInfo, eventId)

            eventActions = eventInfo.actions
            eventActions._idList = [actionId]
            eventActions._items  = [CCookedActionInfo(context, actionRecord, CAction(record=actionRecord))]
            eventActions._loaded = True

            action = eventInfo.actions[0]
            data = { 'event' : eventInfo,
                     'action': action,
                     'client': eventInfo.client,
                     'actions':eventActions,
                     'currentActionIndex': 0,
                     'tempInvalid': None
                   }
            dataList.append(data)
        QtGui.qApp.restoreOverrideCursor()
        applyTemplateList(self, templateId, dataList)

    def on_tabTissuePrintByTemplate_additionalPrintAction(self, context, templateId):
        db = QtGui.qApp.db
        selectedTissueJournalIdList = self.tblTissueJournal.selectedItemIdList()
        cond = db.table('Action')['takenTissueJournal_id'].inlist(selectedTissueJournalIdList)
        actionIdList = db.getIdList('Action', 'id', cond)
        actionIdList = self.filterActionsByTemplate(actionIdList, templateId)
        self.additionalPrint(context, templateId, actionIdList)

    def filterActionsByTemplate(self, actionIdList, templateId):
        db = QtGui.qApp.db
        tableAction = db.table('Action')
        tableActionType = db.table('ActionType')
        tablePrintTemplate = db.table('rbPrintTemplate')

        queryTable = tableAction.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
        cond = [
            db.existsStmt(tablePrintTemplate, [tablePrintTemplate['context'].eq(tableActionType['context']),
                                               tablePrintTemplate['id'].eq(templateId),
                                               tablePrintTemplate['deleted'].eq(0)]),
            tableAction['id'].inlist(actionIdList)
        ]

        return db.getIdList(queryTable, 'Action.`id`', cond)

#    @QtCore.pyqtSlot()
    def on_btnPrint_tissueTabMainPrint(self):
        pageFormat = CPageFormat(pageSize=CPageFormat.A4,
                                     orientation=CPageFormat.Landscape,
                                     leftMargin=5,
                                     topMargin=5,
                                     rightMargin=5,
                                     bottomMargin=5)
        viewerGeometry = None
        while True:
            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)
            cursor.setCharFormat(CReportBase.ReportTitle)
            cursor.insertText(self.getReportTitle())
            cursor.insertBlock()
            cursor.setCharFormat(CReportBase.ReportSubTitle)
            cursor.insertText(self.getReportSubTitle())
            cursor.insertBlock()
            cursor.setCharFormat(CReportBase.ReportBody)
            result = self.makeTable(cursor, doc)
            if not result:
                return
            viewDialog = CReportViewDialog(self)
            viewDialog.setRepeatButtonVisible(True)
            viewDialog.setWindowTitle(u'Печать: Лабораторный журнал')
            viewDialog.setText(doc)
            viewDialog.setPageFormat(pageFormat)
            if viewerGeometry:
                viewDialog.restoreGeometry(viewerGeometry)
            else:
                viewDialog.setWindowState(QtCore.Qt.WindowMaximized)
            done = not viewDialog.exec_()
            viewerGeometry = viewDialog.saveGeometry()
            if done:
                break

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblTissueJournal_doubleClicked(self, index=None):
        if index is None:
            index = self.tblTissueJournal.currentIndex()
        tissueJournalId = self.tblTissueJournal.itemId(index)
        db = QtGui.qApp.db
        eventIdList = db.getDistinctIdList('Action', 'Action.`event_id`', 'Action.`takenTissueJournal_id`=%d'%tissueJournalId)
        if len(eventIdList) == 1:
            editEvent(self, eventIdList[0])
            self.updateTissueJournalList()
        elif len(eventIdList) > 1:
            dlg = CEventListDialog(self)
            dlg.loadEvents(eventIdList)
            dlg.exec_()
            self.updateTissueJournalList()
        else:
            QtGui.QMessageBox.information(self, u'Внимание!', u'Нет связанных событий', QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

    @QtCore.pyqtSlot(bool)
    def on_chkResultOnlyTests_clicked(self, value):
        self.modelResultProperties.setOnlyWithTests(value)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterId_clicked(self, value):
        self.edtFilterId.setEnabled(value)
        self.cmbFilterAccountingSystem.setEnabled(value)
        if value:
            self.resetClientFilter()

    @QtCore.pyqtSlot(bool)
    def on_chkFilterLastName_clicked(self, value):
        if value:
            self.chkFilterId.setChecked(False)
            self.edtFilterId.setEnabled(False)
            self.cmbFilterAccountingSystem.setEnabled(False)
        self.edtFilterLastName.setEnabled(value)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterFirstName_clicked(self, value):
        if value:
            self.chkFilterId.setChecked(False)
            self.edtFilterId.setEnabled(False)
            self.cmbFilterAccountingSystem.setEnabled(False)
        self.edtFilterFirstName.setEnabled(value)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterPatrName_clicked(self, value):
        if value:
            self.chkFilterId.setChecked(False)
            self.edtFilterId.setEnabled(False)
            self.cmbFilterAccountingSystem.setEnabled(False)
        self.edtFilterPatrName.setEnabled(value)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterBirthDay_clicked(self, value):
        if value:
            self.chkFilterId.setChecked(False)
            self.edtFilterId.setEnabled(False)
            self.cmbFilterAccountingSystem.setEnabled(False)
        self.edtFilterBirthDay.setEnabled(value)

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtFilterId_textEdited(self, txt):
        if txt:
            if self.clientFilter.get('accountingSystemId', None):
                self.clientFilter['clientId'] = txt
            else:
                try:
                    self.clientFilter['clientId'] = int(txt)
                except ValueError:
                    self.clientFilter['clientId'] = -1
        else:
            self.clientFilter['clientId'] = None

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtFilterLastName_textEdited(self, txt):
        self.clientFilter['clientLastName'] = nameCase(forceStringEx(txt))

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtFilterFirstName_textEdited(self, txt):
        self.clientFilter['clientFirstName'] = nameCase(forceStringEx(txt))

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtFilterPatrName_textEdited(self, txt):
        self.clientFilter['clientPatrName'] = nameCase(forceStringEx(txt))

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtFilterId_dateChanged(self, date):
        self.clientFilter['clientBirthDate'] = date

    @QtCore.pyqtSlot(int)
    def on_cmbFilterAccountingSystem_currentIndexChanged(self, index):
        self.clientFilter['accountingSystemId'] = self.cmbFilterAccountingSystem.value()

    @QtCore.pyqtSlot(int)
    def on_tabWidgetFilter_currentChanged(self, tabIndex, insertionId=True):
        if self.tabWidgetFilter.widget(tabIndex) == self.tabCalendar:
            self.clientFilter.clear()
        if self.tabWidgetFilter.widget(tabIndex) == self.tabClient:
            if self.currentClientId and insertionId:
                self.resetClientFilter(all=True)
                self.resetFilter()
                self.chkFilterId.setChecked(True)
                self.edtFilterId.setEnabled(True)
                self.cmbFilterAccountingSystem.setEnabled(True)
                self.cmbFilterAccountingSystem.setValue(None)
                self.edtFilterId.setText(unicode(self.currentClientId))
            self.makeClientFilter()
        self.updateTissueJournalList()

    @QtCore.pyqtSlot(int)
    def on_mainTabWidget_currentChanged(self, tabIndex):
        currentTab = self.mainTabWidget.widget(tabIndex)
        self.tissueTabBtnPrint.setVisible(currentTab == self.tabTissue)
        self.resultTabBtnPrint.setVisible(currentTab == self.tabResult)
        if currentTab == self.tabProbeWorkList:
            self.tabProbeWorkList.initializedProbeWorkList()
        elif currentTab == self.tabResult:
            self.tblResultActionType.setCurrentIndex(self.modelResultActionType.index(0, 0))

    def on_selectionModelResultActionsCurrentChanged(self, current, previous):
        QtGui.qApp.callWithWaitCursor(self, self.updateResultProperties, current)
        currentItem = self.tblResultActions.currentItem()
        context = forceString(QtGui.qApp.db.translate('ActionType', 'id', forceRef(currentItem.value('actionType_id')), 'context'))
        additionalCustomizePrintButton(self, self.resultTabBtnPrint, context)

    def on_selectionModelResultActionTypeCurrentChanged(self, current, previous):
        self.updateResultActionsFromAll()

#    @QtCore.pyqtSlot()
    def on_actResultScanBarcode_triggered(self):
        if self.mainTabWidget.currentWidget() == self.tabResult:
            self.edtResultTissueIdentifierFrom.setFocus(QtCore.Qt.OtherFocusReason)
            self.on_edtResultTissueIdentifierFrom_textEdited(self.edtResultTissueIdentifierFrom.text())


class CICDCol(CCol):
    def __init__(self, title, fields, defaultWidth, alignment):
        CCol.__init__(self, title, fields, defaultWidth, alignment)
        self.valuesCache = {}
    def format(self, values):
        id = forceRef(values[0])
        val = self.valuesCache.get(id)
        if val:
            return val
        else:
            stmt = 'SELECT Diagnosis.`MKB` from Diagnostic INNER JOIN Diagnosis ON Diagnosis.`id`=Diagnostic.`diagnosis_id` WHERE Diagnosis.`id` = (SELECT MAX(diagnosis_id) FROM Diagnostic WHERE event_id=%d AND deleted=0) AND Diagnosis.`deleted`=0' % id
            query = QtGui.qApp.db.query(stmt)
            if query.first():
                val = query.value(0)
            else:
                val = QtCore.QVariant()
            self.valuesCache[id] = val
            return val


class CEventListDialog(CDialogBase):
    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        self.setObjectName("EventListDialogFromTissueJournal")
        self.tblEvents = CTableView(self)
        self.setup( [
            CDateTimeFixedCol(u'Дата начала', ['setDate'],  10),
            CRefBookCol(u'Тип', ['eventType_id'], 'EventType', 40),
            CICDCol(u'МКБ', ['id'], 5, 'l'),
            CRefBookCol(u'Врач назначивший', ['setPerson_id'], 'vrbPersonWithSpeciality', 15),
            CRefBookCol(u'Врач выполнивший', ['execPerson_id'], 'vrbPersonWithSpeciality', 15),
            CEnumCol(u'Порядок', ['order'], [u'', u'плановый', u'экстренный', u'самотёком', u'принудительный'], 5),
            CTextCol(u'Примечания',     ['note'], 6)
            ], 'Event', ['id'])
        self.buttonBox  = QtGui.QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.vLayout = QtGui.QVBoxLayout()
        self.vLayout.addWidget(self.tblEvents)
        self.vLayout.addWidget(self.buttonBox)
        self.setLayout(self.vLayout)
        self.table = QtGui.qApp.db.table('Event')
        self.idByRow = {}
        self.setWindowTitle(u'Список событий')
        self.connect(self.tblEvents, QtCore.SIGNAL('doubleClicked(QModelIndex)'), self.on_tblEvents_doubleClicked)
        self.connect(self.buttonBox, QtCore.SIGNAL('clicked(QAbstractButton*)'), self.on_buttonBox_clicked)

    def setup(self, cols, tableName, order):
        self.model = CTableModel(self, cols, tableName)

    def loadEvents(self, eventListId):
        self.eventListId = eventListId
        self.model.setIdList(self.eventListId)
        self.tblEvents.setModel(self.model)

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Close:
            self.close()

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblEvents_doubleClicked(self, index):
        eventId = self.tblEvents.itemId(index)
        if eventId:
            editEvent(self, eventId)


class CTakenTissueJournalActionInfoList(CInfoList):
    def __init__(self, context, idList):
        CInfoList.__init__(self, context)
        self._idList = idList

    def _load(self):
        self._items = [ self.getInstance(CActionInfo, id) for id in self._idList ]
        return True


class CTakenTissueJournalWithActionsInfo(CTakenTissueJournalInfo):
    def _load(self):
        if CTakenTissueJournalInfo._load(self):
            actionIdList = CMapTissueJournalIdToActionsHelper.getActionIdList(self.id)
            self._actions = self.getInstance(CTakenTissueJournalActionInfoList, tuple(actionIdList))
            return True
        else:
            self._actions = []
            return False

    actions = property(lambda self: self.load()._actions)


class CTakenTissueJournalWithActionsInfoList(CInfoList):
    def __init__(self, context, idList):
        CInfoList.__init__(self, context)
        self._idList = idList

    def _load(self):
        self._items = [self.getInstance(CTakenTissueJournalWithActionsInfo, id) for id in self._idList]
        return True


class CMapTissueJournalIdToActionsHelper():
    mapTissueJournalIdToActionIdList = {}

    @classmethod
    def getActionIdList(cls, tissueJournalId):
        return cls.mapTissueJournalIdToActionIdList.get(tissueJournalId, [])

    @classmethod
    def setActionId(cls, tissueJournalId, actionId):
        actionIdList = cls.mapTissueJournalIdToActionIdList.setdefault(tissueJournalId, [])
        if not actionId in actionIdList:
            actionIdList.append(actionId)

    @classmethod
    def invalidate(cls):
        cls.mapTissueJournalIdToActionIdList.clear()


def makeDependentActionIdListByTissueJournal(tissueJournalIdList, actualActionTypeIdList):
    db = QtGui.qApp.db
    tableTTJ = db.table('TakenTissueJournal')
    tableAction = db.table('Action')

    queryTable = tableTTJ.leftJoin(tableAction, tableAction['takenTissueJournal_id'].eq(tableTTJ['id']))

    cond = [
        tableTTJ['id'].inlist(tissueJournalIdList),
        tableAction['deleted'].eq(0)
    ]
    if actualActionTypeIdList:
        cond.append(tableAction['actionType_id'].inlist(actualActionTypeIdList))

    fields = [
        tableTTJ['id'].alias('tissueJournalId'),
        tableAction['id'].alias('actionId')
    ]

    recordList = db.getRecordList(queryTable, fields, cond)

    CMapTissueJournalIdToActionsHelper.invalidate()
    for record in recordList:
        tissueJournalId = forceRef(record.value('tissueJournalId'))
        actionId    = forceRef(record.value('actionId'))
        CMapTissueJournalIdToActionsHelper.setActionId(tissueJournalId, actionId)

