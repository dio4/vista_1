# -*- coding: utf-8 -*-
import re
from PyQt4 import QtGui, QtCore

from RCReport import CRCReport
from Reports.ReportsConstructor.RCExchange import CRCReportExportDialog, CRCReportImportDialog
from Reports.ReportsConstructor.RCFieldList import CRCTableList
from Reports.ReportsConstructor.RCFunctionList import CRCFunctionList
from Reports.ReportsConstructor.RCInfo import CRCReportInfo
from Reports.ReportsConstructor.RCParamList import CRCParamList
from Ui_ConstructorDialog import Ui_ConstructorDialog
from Ui_ConstructorDialogExtended import Ui_ConstructorDialogExtended
from Users.Rights import urAccessReportConstructorEdit
from library.ItemsListDialog import CItemEditorBaseDialog, CItemsListDialogEx
from library.TableModel import CTextCol
from library.Utils import forceRef, forceString, forceStringEx, toVariant, forceInt
from library.interchange import setLineEditValue, getLineEditValue
from models.RCConditionTreeModel import CRCConditionTreeModel
from models.RCFieldsTreeModel import CQueryFieldsTreeModel
from models.RCTableModel import CRCColsModel, CRCTableCapModel, CRCParamsModel, CRCColsItemModel, CRCItemModel, \
    CRCGroupsModel, CRCOrdersModel, CRCGroupItemModel
from s11main import CS11mainApp


class CRCReportList(CItemsListDialogEx):
    def __init__(self, parent):
        CItemsListDialogEx.__init__(
            self, parent,
            [
                CTextCol(u'Наименование', ['name'], 50),
                CTextCol(u'Описание', ['description'], 10),
            ],
            'rcReport',
            ['name'],
            uniqueCode=False
        )
        self.setWindowTitleEx(u'Список отчётов')

    def preSetupUi(self):
        CItemsListDialogEx.preSetupUi(self)
        self.btnSettings = QtGui.QPushButton(u'Настройки', self)
        self.btnSettings.setObjectName('btnSettings')
        self.btnBuildReport = QtGui.QPushButton(u'Построить отчёт', self)
        self.btnBuildReport.setObjectName('btnBuildReport')
        self.btnExchange = QtGui.QPushButton(u'Обмен', self)
        self.btnExchange.setObjectName('btnExchange')

        self.mnuBtnSettings = QtGui.QMenu(self)

        self.mnuBtnSettings.setObjectName('mnuBtnSettings')
        self.mnuBtnExchange = QtGui.QMenu(self)
        self.mnuBtnExchange.setObjectName('mnuBtnExchange')

        self.actSettingsInit = QtGui.QAction(u'Сгенерировать поля', self)

        self.actSettingsInit.setObjectName('actSettingsInit')
        self.actSettingsParams = QtGui.QAction(u'Список параметров', self)
        self.actSettingsParams.setObjectName('actSettingsParams')
        self.actSettingsFields = QtGui.QAction(u'Список полей', self)
        self.actSettingsFields.setObjectName('actSettingsFields')
        self.actSettingsFunctions = QtGui.QAction(u'Список функций', self)
        self.actSettingsFunctions.setObjectName('actSettingsFunctions')
        self.actExchangeExport = QtGui.QAction(u'Экспорт', self)
        self.actExchangeExport.setObjectName('actExchangeExport')
        self.actExchangeImport = QtGui.QAction(u'Импорт', self)
        self.actExchangeImport.setObjectName('actExchangeImport')

    def setBtnSettingsMenu(self):
        self.mnuBtnSettings.addAction(self.actSettingsInit)
        self.mnuBtnSettings.addAction(self.actSettingsParams)
        self.mnuBtnSettings.addAction(self.actSettingsFields)
        self.mnuBtnSettings.addAction(self.actSettingsFunctions)

    def setBtnExchangeMenu(self):
        self.mnuBtnExchange.addAction(self.actExchangeExport)
        self.mnuBtnExchange.addAction(self.actExchangeImport)

    def postSetupUi(self):
        CItemsListDialogEx.postSetupUi(self)
        hasRightEdit = QtGui.qApp.userHasRight(urAccessReportConstructorEdit)

        hasRightEdit = True
        self.buttonBox.addButton(self.btnBuildReport, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btnSettings, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btnExchange, QtGui.QDialogButtonBox.ActionRole)
        self.setBtnSettingsMenu()
        self.setBtnExchangeMenu()
        self.btnSettings.setMenu(self.mnuBtnSettings)
        self.btnExchange.setMenu(self.mnuBtnExchange)

        self.btnEdit.setVisible(hasRightEdit)
        self.btnNew.setVisible(hasRightEdit)
        self.btnSettings.setVisible(hasRightEdit)
        self.btnExchange.setVisible(hasRightEdit)
        self.btnPrint.setVisible(False)

    def getItemEditor(self):
        selectedId = self.select()
        if len(selectedId):
            ids = []
            for row in self.tblItems.selectedRowList():
                ids.append(selectedId[row])
            if ids:
                editionMode = QtGui.qApp.db.translate('rcReport', 'id', ids[0], 'editionMode')
                if editionMode == 0:
                    return CRCReportEditor(self)
                elif editionMode == 1:
                    return CRCReportEditorExtended(self)
        return CRCReportEditor(self)

    def duplicateCurrentRow(self):
        db = QtGui.qApp.db
        reportRecord = db.getRecordEx(
            'rcReport',
            '*',
            'id = %s and deleted = 0' % forceString(self.tblItems.currentItemId())
        )
        translateQuery, translateField = self.duplicateQuery(forceString(reportRecord.value('query_id')))
        for id in translateQuery.values():
            self.updateNewQuery(id, translateQuery, translateField)
        reportRecord.setValue('query_id', toVariant(translateQuery[forceString(reportRecord.value('query_id'))]))
        reportRecord.setValue('name', toVariant(forceString(reportRecord.value('name')) + u' копия'))
        curId = self.tblItems.currentItemId()
        newId = self.insertRecord('rcReport', reportRecord)
        self.duplicateRb('rcReport_Group', curId, newId, translateQuery, [])
        self.duplicateRb('rcReport_Params', curId, newId, translateQuery, [])
        self.duplicateRb('rcReport_TableCapCells', curId, newId, translateQuery, ['name'])

        self.model.setIdList(self.select())
        return newId

    def duplicateQuery(self, queryId):
        db = QtGui.qApp.db
        queryRecord = db.getRecordEx('rcQuery', '*', 'id = %s and deleted = 0' % forceString(queryId))
        state = forceString(queryRecord.value('stateTree'))
        # referenceField = forceString(queryRecord.value('referenceField'))
        translateQuery = {}
        translateField = {}
        for subQueryId in re.findall('q\d+', state):
            translateSubQuery, translateSubField = self.duplicateQuery(subQueryId[1:])
            translateQuery.update(translateSubQuery)
            translateField.update(translateSubField)
        curId = forceString(queryRecord.value('id'))
        newId = forceString(self.insertRecord('rcQuery', queryRecord))

        translateField.update(self.duplicateRb('rcQuery_Cols', curId, newId, translateQuery, ['field'], translateField))
        self.duplicateRb('rcQuery_Group', curId, newId, translateQuery, ['field'], translateField)
        self.duplicateRb('rcQuery_Order', curId, newId, translateQuery, ['field'], translateField)
        self.duplicateConditions(
            'rcQuery_Conditions',
            curId,
            newId,
            None,
            None,
            translateQuery,
            ['field', 'value'],
            translateField
        )
        translateQuery.update({forceString(curId): forceString(newId)})
        return translateQuery, translateField

    def updateNewQuery(self, queryId, translateQuery, translateField):
        db = QtGui.qApp.db
        queryRecord = db.getRecordEx('rcQuery', '*', 'id = %s and deleted = 0' % forceString(queryId))
        referenceField = forceString(queryRecord.value('referencedField'))
        state = forceString(queryRecord.value('stateTree'))
        for curId, newId in translateQuery.items():
            referenceField = referenceField.replace(u'q%s' % forceString(curId), u'q%s' % forceString(newId))
            state = state.replace(u'q%s' % forceString(curId), u'q%s' % forceString(newId))
        for curId, newId in translateField.items():
            referenceField = referenceField.replace(u'f%s' % forceString(curId), u'f%s' % forceString(newId))
        queryRecord.setValue('referencedField', toVariant(referenceField))
        queryRecord.setValue('stateTree', toVariant(state))
        db.updateRecord('rcQuery', queryRecord)

    def duplicateRb(self, tableName, curId, newId, translateQuery, fieldListToTranslate, translateField={}):
        db = QtGui.qApp.db
        table = db.table(tableName)
        translate = {}
        for record in db.getRecordList(
                table,
                '*',
                'master_id = %s' % forceString(curId) + (' and deleted = 0' if table.hasField('deleted') else u'')
        ):
            for fieldName in fieldListToTranslate:
                value = forceString(record.value(fieldName))
                for curQueryId, newQueryId in translateQuery.items():
                    value = value.replace(u'q%s' % forceString(curQueryId), u'q%s' % forceString(newQueryId))
                for curFieldId, newFieldId in translateField.items():
                    value = value.replace(u'f%s' % forceString(curFieldId), u'f%s' % forceString(newFieldId))
                record.setValue(fieldName, toVariant(value))
            record.setValue('master_id', toVariant(newId))
            curRbId = forceString(record.value('id'))
            newRbId = forceString(self.insertRecord(tableName, record))
            translate[forceString(curRbId)] = forceString(newRbId)
        return translate

    def duplicateConditions(
            self,
            tableName,
            curId,
            newId,
            curParentId,
            newParentId,
            translateQuery,
            fieldListToTranslate,
            translateField={}
    ):
        db = QtGui.qApp.db
        table = db.table(tableName)
        translate = {}
        whereBlock = 'master_id = %s' % forceString(curId)
        whereBlock += (' and deleted = 0' if table.hasField('deleted') else u'')
        whereBlock += (
        (u' and parentCondition_id = %s ' % curParentId) if curParentId else ' and isNull(parentCondition_id)')
        for record in db.getRecordList(table, '*', whereBlock):
            for fieldName in fieldListToTranslate:
                value = forceString(record.value(fieldName))
                for curQueryId, newQueryId in translateQuery.items():
                    value = value.replace(u'q%s' % forceString(curQueryId), u'q%s' % forceString(newQueryId))
                for curFieldId, newFieldId in translateField.items():
                    value = value.replace(u'f%s' % forceString(curFieldId), u'f%s' % forceString(newFieldId))
                record.setValue(fieldName, toVariant(value))
            record.setValue('master_id', toVariant(newId))
            record.setValue('parentCondition_id', toVariant(newParentId))
            curRbId = forceString(record.value('id'))
            newRbId = forceString(self.insertRecord(tableName, record))
            translate[forceString(curRbId)] = forceString(newRbId)
            self.duplicateConditions(
                tableName,
                curId,
                newId,
                curRbId,
                newRbId,
                translateQuery,
                fieldListToTranslate,
                translateField
            )
        return translate

    def insertRecord(self, tableName, record):
        record.setValue('id', toVariant(None))
        return QtGui.qApp.db.insertRecord(tableName, record)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblItems_doubleClicked(self, index):
        self.on_btnBuildReport_clicked()

    @QtCore.pyqtSlot()
    def on_actSettingsInit_triggered(self):
        from Reports.ReportsConstructor.RCFieldList import CRCInitFields
        ok = QtGui.QMessageBox.question(
            self,
            u'Внимание!',
            u'Вся текущая таблица rcField удет удалена и заполнена новыми данными.'
            u'Все отчёты перестанут работа.'
            u'Уверены что хотите продолжить?',
            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Close,
            QtGui.QMessageBox.Close
        )
        if ok == QtGui.QMessageBox.Ok:
            CRCInitFields(self).process()

    @QtCore.pyqtSlot()
    def on_actSettingsParams_triggered(self):
        CRCParamList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actSettingsFunctions_triggered(self):
        CRCFunctionList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actSettingsFields_triggered(self):
        CRCTableList(self).exec_()

    @QtCore.pyqtSlot()
    def on_btnBuildReport_clicked(self):
        selectedId = self.select()
        if len(selectedId):
            ids = []
            for row in self.tblItems.selectedRowList():
                ids.append(selectedId[row])
            if len(ids):
                report = CRCReport(self, CRCReportInfo(self, ids[0]))
                report.exec_()

    @QtCore.pyqtSlot()
    def on_actExchangeExport_triggered(self):
        selectedId = self.select()
        if len(selectedId):
            ids = []
            for row in self.tblItems.selectedRowList():
                ids.append(selectedId[row])
            if len(ids):
                dialog = CRCReportExportDialog(self, ids)
                dialog.export()
                dialog.save()

    @QtCore.pyqtSlot()
    def on_actExchangeImport_triggered(self):
        dialog = CRCReportImportDialog(self)
        dialog._import()
        self.renewListAndSetTo()


class CRCReportEditorBase(CItemEditorBaseDialog):
    def __init__(self, parent, table):
        CItemEditorBaseDialog.__init__(self, parent, table)

    def postSetupUi(self):
        self.connect(self.modelCols, QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), self.updateCmbGroupField)
        self.cmbGroupField.view().setMinimumWidth(400)

    def on_selectionModelTableCap_selectionChanged(self, current, previos):
        self.cmbAlignmentCapItem.setEnabled(bool(current))
        indexes = self.selectionModelTableCap.selectedIndexes()
        if not indexes:
            return
        item = self.modelTableCap.getItem(indexes[0])
        self.cmbAlignmentCapItem.setCurrentIndex(item._alignment)
        self.chkBoldCapItem.setChecked(item._bold)
        self.cmbGroupField.setEnabled(bool(item.isGroup()))
        self.cmbGroupField.setIndex(self.modelTableCap.getGroupFieldValue(indexes[0]) - 1)

    def on_cmbAlignmentCapItem_currentIndexChanged(self, value):
        if self.cmbAlignmentCapItem.hasFocus():
            indexes = self.selectionModelTableCap.selectedIndexes()
            for index in indexes:
                item = self.modelTableCap.getItem(index)
                item.setAlignment(self.cmbAlignmentCapItem.currentIndex())

        selection = self.selectionModelTableCap.selection()
        self.tblCap.reset()
        self.selectionModelTableCap.select(selection, QtGui.QItemSelectionModel.Select)

    def on_chkBoldCapItem_clicked(self, checked):
        if self.chkBoldCapItem.hasFocus():
            indexes = self.selectionModelTableCap.selectedIndexes()
            for index in indexes:
                item = self.modelTableCap.getItem(index)
                item.setBold(forceInt(checked))

        selection = self.selectionModelTableCap.selection()
        self.tblCap.reset()
        self.selectionModelTableCap.select(selection, QtGui.QItemSelectionModel.Select)

    def on_cmbGroupField_currentIndexChanged(self, value):
        if self.cmbGroupField.hasFocus():
            indexes = self.selectionModelTableCap.selectedIndexes()
            if indexes:
                index = indexes[0]
                self.modelTableCap.setGroupFieldValue(index, self.cmbGroupField.index() + 1)

    def updateCmbGroupField(self):
        if hasattr(self, 'modelCols'):
            currentIndex = self.cmbGroupField.index()
            self.cmbGroupField.setModel(CRCColsItemModel(self, modelCols=self.modelCols, addNone=True))
            # self.cmbGroupField.reset()
            self.cmbGroupField.setIndex(currentIndex)
            self.setIsDirty(True)

    @QtCore.pyqtSlot()
    def on_btnClearTableCap_clicked(self):
        if self.createSimpleMessageBox(u'Существующая таблица будет очищена. Продолжить?'):
            self.modelTableCap.clearTable()
        self.setIsDirty(True)

    @QtCore.pyqtSlot()
    def on_btnCreateTableCap_clicked(self):
        rowCount = self.spinBoxRowCount.value()
        columnCount = self.spinBoxColumnCount.value()
        if self.createSimpleMessageBox(u'Существующая таблица будет удалена. Продолжить?'):
            self.modelTableCap.createTable(rowCount, columnCount)
        self.setIsDirty(True)

    @QtCore.pyqtSlot()
    def on_btnDeleteTableCap_clicked(self):
        if self.createSimpleMessageBox(u'Существующая таблица будет удалена. Продолжить?'):
            self.modelTableCap.deleteTable()
        self.setIsDirty(True)

    @QtCore.pyqtSlot()
    def on_btnFillTableCap_clicked(self):
        if self.createSimpleMessageBox(
                u'Последний ряд таблицы будет заполнен в соответствии с таблицей "поля таблицы". Продолжить?'):
            self.modelTableCap.fillFields()
        self.setIsDirty(True)

    @QtCore.pyqtSlot()
    def on_btnCreateReport_clicked(self):
        report = CRCReport(
            self,
            self.edtReportName.text(),
            self.modelCols,
            self.modelTableCap,
            self.modelConditions,
            self.modelParams,
            self.modelFunctions
        )
        report.exec_()

    def createSimpleMessageBox(self, message):
        ok = QtGui.QMessageBox.question(self, u'Внимание!', message, QtGui.QMessageBox.Ok | QtGui.QMessageBox.Close,
                                        QtGui.QMessageBox.Ok)
        if ok == QtGui.QMessageBox.Ok:
            return True
        return False

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.saveData()


class CRCReportEditor(CRCReportEditorBase, Ui_ConstructorDialog):
    def __init__(self, parent):
        CRCReportEditorBase.__init__(self, parent, 'rcReport')
        self.preSetupUi()
        self.setupUi(self)
        self.postSetupUi()
        self.setWindowTitleEx(u'Отчёт')
        self._recordQuery = None
        self.queryTable = 'rcQuery'

    def preSetupUi(self):
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMaximizeButtonHint)
        self.addModels('Tree', CQueryFieldsTreeModel(self))
        self.addModels('Cols', CRCColsModel(self, self.modelTree))
        self.addModels('Groups', CRCGroupsModel(self, self.modelTree))
        self.addModels('Orders', CRCOrdersModel(self, self.modelTree))
        self.addModels('Params', CRCParamsModel(self))
        self.addModels('Conditions', CRCConditionTreeModel(self, self.modelTree, self.modelParams))
        self.addModels('TableCapGroups', CRCGroupItemModel(self))
        self.addModels('TableCap', CRCTableCapModel(self, self.modelCols, self.modelTableCapGroups, self.modelTree))
        self.addModels('Functions', CRCItemModel(self, ['name', 'function', 'description', 'hasSpace'], 'rcFunction'))
        self.addModels('Tables', CRCItemModel(self, ['name'], 'rcTable'))

    def postSetupUi(self):
        CRCReportEditorBase.postSetupUi(self)
        self.setModels(self.tableFields, self.modelCols, self.selectionModelCols)
        self.setModels(self.tableGroups, self.modelGroups, self.selectionModelGroups)
        self.setModels(self.tableOrders, self.modelOrders, self.selectionModelOrders)
        self.tableFields.setColSize()

        self.tableFields.setSortingEnabled(True)
        self.tableGroups.setSortingEnabled(True)
        self.tableOrders.setSortingEnabled(True)

        self.cmbMainTable.setModel(self.modelTables)
        self.cmbGroupField.setModel(CRCColsItemModel(self, modelCols=self.modelCols, addNone=True))
        self.setModels(self.tblCap, self.modelTableCap, self.selectionModelTableCap)
        self.setModels(self.treeConds, self.modelConditions, self.selectionModelConditions)
        self.setModels(self.tableParams, self.modelParams, self.selectionModelParams)

        self.tableParams.setSortingEnabled(True)

        self.connect(self.modelTableCap, QtCore.SIGNAL('needSpanUpdate()'), self.tblCap.spanUpdate)
        self.modelTables.loadItems()
        self.modelFunctions.loadItems()
        self.modelTree.loadItems()
        self.modelTree.setModelParams(self.modelParams)
        self.modelTree.setModelFunctions(self.modelFunctions)

        self.connect(self.modelGroups, QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), self.setDirty)
        self.connect(self.modelOrders, QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), self.setDirty)
        self.connect(self.modelTableCap, QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), self.setDirty)
        self.connect(self.modelParams, QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), self.setDirty)
        self.connect(self.modelConditions, QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), self.setDirty)

    def setQueryRecord(self, queryId):
        result = None
        db = QtGui.qApp.db
        if queryId:
            list = db.getRecordList(self.queryTable, where='id = %s' % forceString(queryId))
            if list:
                result = list[0]
        self._recordQuery = result

    def getQueryRecord(self):
        db = QtGui.qApp.db
        if not self._recordQuery:
            self._recordQuery = db.record(self.queryTable)

    def saveQueryRecord(self):
        db = QtGui.qApp.db
        if not self._recordQuery:
            return None
        return db.insertOrUpdate(self.queryTable, self._recordQuery)

    def setRecord(self, record):
        CRCReportEditorBase.setRecord(self, record)
        setLineEditValue(self.edtReportName, record, 'name')
        queryId = forceRef(record.value('query_id'))

        self.modelParams.loadItems(self.itemId())

        self.setQueryRecord(queryId)

        if not self._recordQuery:
            return
        self.cmbMainTable.setValue(forceInt(self._recordQuery.value('mainTable_id')))
        self.modelTree.setMainTableId(self.cmbMainTable.value())
        self.modelTree.setState('')
        self.modelCols.loadItems(queryId)
        self.modelGroups.loadItems(queryId)
        self.modelOrders.loadItems(queryId)
        self.modelConditions.loadItems(queryId)
        self.modelTree.setState(forceString(self._recordQuery.value('stateTree')))
        self.modelTableCapGroups.loadItems(self.itemId())
        self.modelTableCap.loadItems(self.itemId())
        self.treeConds.expandAll()

    def getRecord(self):
        self.getQueryRecord()
        self._recordQuery.setValue('mainTable_id', toVariant(self.cmbMainTable.value()))
        self._recordQuery.setValue('stateTree', toVariant(self.modelTree.getState()))
        queryId = self.saveQueryRecord()
        self.modelCols.saveItems(queryId)
        self.modelGroups.saveItems(queryId)
        self.modelOrders.saveItems(queryId)
        self.modelConditions.saveItems(queryId)

        record = CRCReportEditorBase.getRecord(self)
        getLineEditValue(self.edtReportName, record, 'name')
        record.setValue('query_id', toVariant(queryId))
        return record

    def saveInternals(self, id):
        self.modelTableCap.saveItems(id)
        self.modelParams.saveItems(id)
        self.modelTableCapGroups.saveItems(id)

    def checkDataEntered(self):
        result = True
        name = forceStringEx(self.edtReportName.text())
        result = result and (name or self.checkInputMessage(u'наименование', False, self.edtReportName))
        return result

    def setDirty(self):
        self.setIsDirty(True)

    @QtCore.pyqtSlot()
    def on_btnCreateReport_clicked(self):
        report = CRCReport(self, CRCReportInfo(self, self._id))
        report.exec_()

    @QtCore.pyqtSlot(int)
    def on_cmbMainTable_currentIndexChanged(self, value):
        self.modelTree.setMainTableId(self.cmbMainTable.value())
        self.setIsDirty(True)


class CRCReportEditorExtended(CRCReportEditorBase, Ui_ConstructorDialogExtended):
    def __init__(self, parent):
        CRCReportEditorBase.__init__(self, parent, 'rcReport')
        self.preSetupUi()
        self.setupUi(self)
        self.postSetupUi()
        self.setWindowTitleEx(u'Отчёт')

    def preSetupUi(self):
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMaximizeButtonHint)
        self.addModels('Cols', CRCColsItemModel(self, ['field'], 'rcQuery_Cols'))
        self.addModels('Params', CRCParamsModel(self))
        self.addModels('TableCap', CRCTableCapModel(self, self.modelCols))

    def postSetupUi(self):
        CRCReportEditorBase.postSetupUi(self)
        self.setModels(self.tblCap, self.modelTableCap, self.selectionModelTableCap)
        self.setModels(self.tableParams, self.modelParams, self.selectionModelParams)
        self.connect(self.modelTableCap, QtCore.SIGNAL('needSpanUpdate()'), self.tblCap.spanUpdate)
        self.connect(self.btnApplySql, QtCore.SIGNAL('clicked()'), self.btnApplySql_clicked)

    def setRecord(self, record):
        CRCReportEditorBase.setRecord(self, record)
        setLineEditValue(self.edtReportName, record, 'name')
        # setTextEditValue(self.textSQL, record, 'sql')
        self.modelCols.loadItems(self.itemId())
        self.modelTableCap.loadItems(self.itemId())
        self.modelParams.loadItems(self.itemId())

    def getRecord(self):
        record = CRCReportEditorBase.getRecord(self)
        getLineEditValue(self.edtReportName, record, 'name')
        # getTextEditValue(self.textSQL, record, 'sql')
        self.modelTableCap.saveItems(self.itemId())
        self.modelParams.saveItems(self.itemId())
        return record

    def checkDataEntered(self):
        result = True
        name = forceStringEx(self.edtReportName.text())
        result = result and (name or self.checkInputMessage(u'наименование', False, self.edtName))
        return result

    def btnApplySql_clicked(self):
        fullSqlText = forceString(self.textSql.toPlainText())
        preSqlText = list(fullSqlText.split('#@main'))[0]
        sqlText = list(fullSqlText.split('#@main'))[1].split(';')[0]
        postSqlText = list(fullSqlText.split('#@main'))[1].split(';')[1:]

        self.parceSqlText(sqlText)

    def parceSqlText(self, sqlText):
        sqlText = u' %s ' % sqlText.replace(u'\n', ' ')
        sqlText = u' %s ' % sqlText.replace(u'(', ' ( ')
        sqlText = u' %s ' % sqlText.replace(u')', ' ) ')
        sqlText = u' %s ' % sqlText.replace(u',', ' , ')
        sqlText = re.compile('[\n ]select[\n ]', re.IGNORECASE).sub(' SELECT ', sqlText)
        sqlText = re.compile('[\n ]from[\n ]', re.IGNORECASE).sub(' FROM ', sqlText)
        wordList = [word for word in sqlText.split(' ') if word]
        cols = self.parceSql(wordList)
        self.modelCols.setItems(cols)

    def parceSql(self, list):
        enter = 0
        mainFromIndex = -1
        firstSelect = 0
        for index, value in enumerate(list):
            if value == 'SELECT':
                enter += 1
                firstSelect = 1
            elif value == 'FROM':
                enter -= 1
            if enter == 0 and firstSelect:
                mainFromIndex = index
                break
        if mainFromIndex > 0:
            list = list[:mainFromIndex]

        enter = 0
        commaIndexList = []
        for index, value in enumerate(list):
            if value == '(':
                enter += 1
            elif value == ')':
                enter -= 1
            elif value == ',' and enter == 0:
                commaIndexList.append(index)
        cols = []
        for index in commaIndexList:
            cols.append(list[index - 1])
        cols.append(list[-1])
        return cols


def main():
    import sys
    from library.database import connectDataBaseByInfo
    app = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtGui.qApp = app
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    connectionInfo = {
        'driverName': 'mysql',
        'host': 'pes',
        'port': 3306,
        'database': 's12',
        'user': 'dbuser',
        'password': 'dbpassword',
        'connectionName': 'vista-med',
        'compressData': True,
        'afterConnectFunc': None
    }
    db = connectDataBaseByInfo(connectionInfo)
    query = db.query(u'''
    SELECT o.organisation_id
    FROM OrgStructure o
    INNER JOIN Person p ON p.orgStructure_id = o.id
    ''')
    if query.first():
        record = query.record()
        print forceStringEx(record.value('organisation_id').toString()), type(
            int(forceStringEx(record.value('organisation_id').toString())))

        QtGui.qApp.currentOrgId = lambda: int(forceStringEx(record.value('organisation_id').toString()))
    print '229638_4'

    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)
    sys.exit(CRCReportList(None).exec_())


if __name__ == '__main__':
    main()
