#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2016 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4.QtCore import QModelIndex, QObject, QString

from Ui_ItemEditorDialog import Ui_ItemEditorDialog
from Ui_ItemsListDialog import Ui_ItemsListDialog
from Ui_ItemsSplitListDialog import Ui_ItemsSplitListDialog
from library.DialogBase import CDialogBase
from library.RecordLock import CRecordLockMixin
from library.TableView import *
from library.Utils import forceBool, forceRef, forceStringEx
from library.exception import CDatabaseException


class CItemsListDialog(CDialogBase, Ui_ItemsListDialog):
    # idFieldName = 'id'
    def __init__(self, parent, cols, tableName, order, forSelect=False, filterClass=None, allowColumnsHiding=False, idFieldName='id'):
        u"""
        order - column to sort by
        forSelect = True - records from query
        forSelect = False - recods from table
        filterClass - class for filter dialog
        """
        self.idFieldName = idFieldName
        CDialogBase.__init__(self, parent)
        self._allowColumnsHiding = allowColumnsHiding
        self.preSetupUi()
        self.setupUi(self)
        self.postSetupUi()
        self.setup(cols, tableName, order, forSelect, filterClass, allowColumnsHiding)

        self.orderAscending = True

    def preSetupUi(self):
        self.btnPrint =  QtGui.QPushButton(u'Печать F6', self)
        self.btnPrint.setObjectName('btnPrint')
        self.btnNew =  QtGui.QPushButton(u'Вставка F9', self)
        self.btnNew.setObjectName('btnNew')
        self.btnEdit =  QtGui.QPushButton(u'Правка F4', self)
        self.btnEdit.setObjectName('btnEdit')
        self.btnFilter =  QtGui.QPushButton(u'Фильтр', self)
        self.btnFilter.setObjectName('btnFilter')
        self.btnSelect =  QtGui.QPushButton(u'Выбор', self)
        self.btnSelect.setObjectName('btnSelect')

    def postSetupUi(self):
        self.buttonBox.addButton(self.btnSelect, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btnFilter, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btnEdit, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btnNew, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btnPrint, QtGui.QDialogButtonBox.ActionRole)

    def setup(self, cols, tableName, order, forSelect=False, filterClass=None, allowColumnsHiding=False):
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.forSelect = forSelect
        self.filterClass = filterClass
        self.props = {}
        self.order = order
        self.model = CTableModel(self, cols, allowColumnsHiding=allowColumnsHiding)
        self.model.idFieldName = self.idFieldName
        self.model.setTable(tableName)
        self.tblItems.setModel(self.model)
        self.btnSelect.setEnabled(self.forSelect)
        self.btnSelect.setVisible(self.forSelect)
        self.btnSelect.setDefault(self.forSelect)
        self.btnFilter.setEnabled(self.forSelect and bool(self.filterClass))
        self.btnFilter.setEnabled(bool(self.filterClass))
        self.btnFilter.setVisible(bool(self.filterClass))
        self.btnEdit.setDefault(not self.forSelect)
        self.tblItems.setFocus(Qt.OtherFocusReason)

        self.btnNew.setShortcut(Qt.Key_F9)
        self.btnEdit.setShortcut(Qt.Key_F4)
        self.btnPrint.setShortcut(Qt.Key_F6)
        QtCore.QObject.connect(
            self.tblItems.horizontalHeader(), QtCore.SIGNAL('sectionClicked(int)'), self.setSort)

    def loadMyPreferences(self):
        userId = QtGui.qApp.userId
        windowName = self.objectName()
        if windowName != '':
            db = QtGui.qApp.db
            table = db.table('Person_Preferences')

            for colNo in xrange(len(self.model._cols)):
                where = "master_id=%d AND name = '%s_col%d'" % (userId, windowName, colNo)
                record = db.getRecordEx(table, '*', where)
                if record:
                    isVisible = forceBool(record.value('value'))
                    self.model._cols[colNo].setVisible(isVisible)

    def saveMyPreferences(self):
        userId = QtGui.qApp.userId
        windowName = self.objectName()
        if windowName != '':
            db = QtGui.qApp.db
            table = db.table('Person_Preferences')

            for colNo in xrange(len(self.model._cols)):
                where = "master_id=%d AND name = '%s_col%d'" % (userId, windowName, colNo)
                record = db.getRecordEx(table, '*', where)
                if not record:
                    record = table.newRecord()
                    record.setValue('master_id', userId)
                    record.setValue('name', windowName + '_col' + str(colNo))
                record.setValue('value', toVariant(self.model._cols[colNo].isVisible()))
                db.insertOrUpdate(table, record)

    def exec_(self):
        idList = self.select(self.props)
        self.model.setIdList(idList)
        if idList:
            self.tblItems.selectRow(0)
        self.label.setText(u'всего: %d' % len(idList))
        return CDialogBase.exec_(self)

    def select(self, props):
        table = self.model.table()
        where = ''
        if table.hasField('deleted'):
            where = 'deleted = 0'
        return QtGui.qApp.db.getIdList(table.name(), self.idFieldName, where, self.order)

    def selectItem(self):
        return self.exec_()

    def setCurrentItemId(self, itemId):
        self.tblItems.setCurrentItemId(itemId)

    def currentItemId(self):
        return self.tblItems.currentItemId()

    def renewListAndSetTo(self, itemId=None):
        idList = self.select(self.props)
        self.tblItems.setIdList(idList, itemId)
        self.label.setText(u'всего: %d' % len(idList))

    @QtCore.pyqtSlot(QModelIndex)
    def on_tblItems_doubleClicked(self, index):
        if self.forSelect:
            self.on_btnSelect_clicked()
        else:
            self.on_btnEdit_clicked()

    @QtCore.pyqtSlot()
    def on_btnFilter_clicked(self):
        if self.filterClass:
            dialog = self.filterClass(self)
            dialog.setProps(self.props)
            if dialog.exec_() :
                self.props = dialog.props()
                self.renewListAndSetTo(None)

    @QtCore.pyqtSlot()
    def on_btnSelect_clicked(self):
        self.accept()

    @QtCore.pyqtSlot()
    def on_btnNew_clicked(self):
        dialog = self.getItemEditor()
        if dialog.exec_():
            itemId = dialog.itemId()
            self.renewListAndSetTo(itemId)

    @QtCore.pyqtSlot()
    def on_btnEdit_clicked(self):
        itemId = self.currentItemId()
        if itemId:
            dialog = self.getItemEditor()
            dialog.load(itemId)
            if dialog.exec_():
                itemId = dialog.itemId()
                self.renewListAndSetTo(itemId)
        else:
            self.on_btnNew_clicked()

    def getReportHeader(self):
        return self.objectName()

    def getFilterAsText(self):
        return u''

    def contentToHTML(self):
        reportHeader = self.getReportHeader()
        self.tblItems.setReportHeader(reportHeader)
        reportDescription = self.getFilterAsText()
        self.tblItems.setReportDescription(reportDescription)
        return self.tblItems.contentToHTML()

    @QtCore.pyqtSlot()
    def on_btnPrint_clicked(self):
        html = self.contentToHTML()
        view = CReportViewDialog(self)
        view.setText(html)
        view.exec_()

    def setSort(self, col):
        name = self.model.cols()[col].fields()[0]
        self.order = name
        header = self.tblItems.horizontalHeader()
        header.setSortIndicatorShown(True)
        self.orderAscending = not self.orderAscending
        header.setSortIndicator(col, Qt.AscendingOrder if self.orderAscending else Qt.DescendingOrder)
        self.renewListAndSetTo(self.currentItemId())


class CItemsSplitListDialog(CItemsListDialog, Ui_ItemsSplitListDialog):
    setupUi = Ui_ItemsSplitListDialog.setupUi
    retranslateUi = Ui_ItemsSplitListDialog.retranslateUi

    # Окно со сплиттером для элементов, связанных направленными соответствиями (не обязательно иерархическими)
    # Вверху - список элементов, внизу - соответствия каждого элемента
    def __init__(self, parent, tableName, cols, order, subTableName, subCols, mainColName, linkColName, forSelect=False, filterClass=None):
        CItemsListDialog.__init__(self, parent, cols, tableName, order, forSelect, filterClass)
        self.setupSubTable(subTableName, subCols, mainColName, linkColName)
        QObject.connect(self.tblItemGroups, QtCore.SIGNAL('doubleClicked(QModelIndex)'), self.on_tblItemGroups_doubleClicked)

    def setupSubTable(self, subTableName, subCols, mainColName, linkColName):
        self.subModel = CTableModel(self, subCols)
        self.subModel.idFieldName = 'id'
        self.subModel.setTable(subTableName)
        self.mainColName = mainColName
        self.linkColName = linkColName
        self.updateSubTable()
        QObject.connect(self.tblItems.selectionModel(), QtCore.SIGNAL('currentRowChanged(QModelIndex, QModelIndex)'), self.updateSubTable)

    def updateSubTable(self):
        current = self.tblItems.currentItemId()
        if current:
            idList = QtGui.qApp.db.getIdList(table=self.subModel.table(), where='%s = %d' % (self.mainColName, current))
            self.subModel.setIdList(idList)
            self.tblItemGroups.setModel(self.subModel)
            if len(idList):
                self.tblItemGroups.selectRow(0)

    def on_tblItemGroups_doubleClicked(self, index):
        id = self.tblItemGroups.itemId(index)
        record = QtGui.qApp.db.getRecord(self.subModel.table(), self.linkColName, id)
        main_id = forceRef(record.value(self.linkColName))
        self.tblItems.setCurrentItemId(main_id)


class CItemsListDialogEx(CItemsListDialog):
    u"""Справочник с возможностью выделения, дублирования и удаления строчек
    и контроля уникальности кода"""
    def __init__(self, parent, cols, tableName, order, forSelect=False, filterClass=None, multiSelect=True, uniqueCode=False, duplicateEnabled = True, deletedEnabled = True):
        CItemsListDialog.__init__(self, parent, cols, tableName, order, forSelect, filterClass)
        self.uniqueCode = uniqueCode
        if multiSelect:
            self.tblItems.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
            self.addPopupAction('actSelectAllRow', u'Выделить все строки', self.selectAllRowTblItem)
            self.addPopupAction('actClearSelectionRow', u'Снять выделение', self.clearSelectionRow)
        if duplicateEnabled:
            self.addPopupAction('actDuplicate', u'Дублировать', self.duplicateCurrentRow)
        if deletedEnabled:
            self.addPopupAction('actDelSelectedRows', u'Удалить выделенные строки', self.delSelectedRows)

    def addPopupAction(self, name, title, method):
        setattr(self, name, QtGui.QAction(title, self))
        self.tblItems.addPopupAction(getattr(self, name))
        self.connect(getattr(self, name), QtCore.SIGNAL('triggered()'), method)

    def select(self, props=None):
        if not props:
            props = {}
        table = self.model.table()
        return QtGui.qApp.db.getIdList(table.name(),
                                       'id',
                                       table['deleted'].eq(0) if table.hasField('deleted') else '',
                                       self.order)

    def duplicateCurrentRow(self):
        record = self.model.getRecordById(self.tblItems.currentItemId())
        code = forceString(record.value('code'))
        if self.uniqueCode:
            record.setValue('code', toVariant(code + '*'))  # чтобы не дублировался код
        for index in xrange(record.count()):
            if forceString(record.fieldName(index)) == 'id':
                record.setValue(index, toVariant(None))  # чтобы не дублировался id
        sourceName = forceString(record.value('name'))
        record.setValue('name', toVariant(sourceName + u' копия'))
        newItemId = QtGui.qApp.db.insertRecord(self.model.table(), record)
        self.model.setIdList(self.select())
        return newItemId

    def selectAllRowTblItem(self):
        self.tblItems.selectAll()

    def clearSelectionRow(self):
        self.tblItems.clearSelection()

    def delSelectedRows(self):
        db = QtGui.qApp.db
        selectedRowList = self.tblItems.selectedRowList()
        table = self.model.table()
        if QtGui.QMessageBox.question(self, u'Подтверждение удаления',
                                    u'Вы уверены что хотите удалить выделенные строки?(количество строк: %d)'% len(selectedRowList),
                                    QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
                                    QtGui.QMessageBox.No
                                    ) == QtGui.QMessageBox.Yes:
            try:
                self.model.removeRowList(selectedRowList[::-1], raiseExceptions=True)
            except CDatabaseException, e:
                if e.sqlError.number() == 1451:  # Cannot delete or update a parent row: a foreign key constraint fails
                    QtGui.QMessageBox.critical(
                        self,
                        u'Ошибка при удалении',
                        u'Одна или более строк не были удалены, так как используются в существующих данных.',
                        QtGui.QMessageBox.Close
                    )
        self.model.setIdList(self.select())


class CItemsSplitListDialogEx(CItemsSplitListDialog):
    # поскольку виртуальное наследование не поддерживается,
    # наследуем от одного класса, а методы второго просто копируем
    def __init__(self, parent, tableName, cols, order, subTableName, subCols, mainColName, linkColName, forSelect=False, filterClass=None, multiSelect=True, uniqueCode=False):
        CItemsSplitListDialog.__init__(self, parent, tableName, cols, order, subTableName, subCols, mainColName, linkColName, forSelect, filterClass)
        self.uniqueCode = uniqueCode
        if multiSelect:
            self.tblItems.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
            self.tblItemGroups.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
            self.setPopupMenu()

    def addPopupAction(self, name, title, method):
        setattr(self, name, QtGui.QAction(title, self))
        self.tblItems.addPopupAction(getattr(self, name))
        self.connect(getattr(self, name), QtCore.SIGNAL('triggered()'), method)

    def setPopupMenu(self):
        self.addPopupAction('actSelectAllRow', u'Выделить все строки', self.selectAllRowTblItem)
        self.addPopupAction('actClearSelectionRow', u'Снять выделение', self.clearSelectionRow)
        self.addPopupAction('actDelSelectedRows', u'Удалить выделенные строки', self.delSelectedRows)
        self.addPopupAction('actDuplicate', u'Дублировать', self.duplicateCurrentRow)

    def select(self, props=None):
        if not props:
            props = {}
        table = self.model.table()
        return QtGui.qApp.db.getIdList(table.name(),
                                       'id',
                                       table['deleted'].eq(0),
                                       self.order)

    def duplicateCurrentRow(self):
        record = self.model.getRecordById(self.tblItems.currentItemId())
        code = forceString(record.value('code'))
        if self.uniqueCode:
            record.setValue('code', toVariant(code + '*')) # чтобы не дублировался код
        record.setValue('id', toVariant(0)) # чтобы не дублировался id
        newItemId = QtGui.qApp.db.insertRecord(self.model.table(), record)
        self.model.setIdList(self.select({}))
        return newItemId

    def selectAllRowTblItem(self):
        self.tblItems.selectAll()

    def clearSelectionRow(self):
        self.tblItems.clearSelection()

    def delSelectedRows(self):
        db = QtGui.qApp.db
        selectedRowList = self.tblItems.selectedRowList()
        table = self.model.table()
        if QtGui.QMessageBox.question(self, u'Подтверждение удаления',
                                    u'Вы уверены что хотите удалить выделенные строки?(количество строк: %d)'% len(selectedRowList),
                                    QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
                                    QtGui.QMessageBox.No
                                    ) == QtGui.QMessageBox.Yes:
            for row in selectedRowList[::-1]: # удаляем в обратном порядке, чтобы избежать сдвигов
                try:
                    self.model.removeRow(row)
                except CDatabaseException:
                    pass
        self.model.setIdList(self.select({}))


class CItemEditorBaseDialog(CDialogBase, CRecordLockMixin):
    idFieldName = 'id'

    def __init__(self, parent, tableName):
        CDialogBase.__init__(self, parent)
        CRecordLockMixin.__init__(self)
        self._id = None
        self._tableName = tableName
        self._record = None

    def exec_(self):
        if self.lock(self._tableName, self._id):
            try:
                result = CDialogBase.exec_(self)
            finally:
                self.releaseLock()
        else:
            result = QtGui.QDialog.Rejected
            self.setResult(result)
        return result

    def saveData(self):
        return self.checkDataEntered() and self.save()

    def load(self, id):
        db = QtGui.qApp.db
        record = db.getRecord(db.table(self._tableName), '*', id)
        assert record
        self.setRecord(record)
        self.setIsDirty(False)

    def setRecord(self, record):
        self._record = record
        self._id = forceRef(record.value(self.idFieldName)) if record else None

    def setGroupId(self, id):
        pass

    def record(self):
        return self._record

    def getRecord(self):
        if not self._record:
            db = QtGui.qApp.db
            record = db.record(self._tableName)
            if self._id:
                record.setValue(self.idFieldName, toVariant(self._id))
            self._record = record
        return self._record

    def tableName(self):
        return self._tableName

    def itemId(self):
        return self._id

    def setItemId(self, itemId):
        self._id = itemId
        if self._record:
            self._record.setValue(self.idFieldName, toVariant(self._id))

    def checkDataEntered(self):
        result = True
        code = forceStringEx(self.edtCode.text())
        name = forceStringEx(self.edtName.text())
        result = result and (code or self.checkInputMessage(u'код', False, self.edtCode))
        result = result and (name or self.checkInputMessage(u'наименование', False, self.edtName))
        return result

    def checkRecursion(self, newGroupId, groupIdFieldName='group_id'):
        if self._id:
            groupId = newGroupId
            db = QtGui.qApp.db
            table = db.table(self._tableName)
            while groupId and self._id != groupId:
                groupId = forceRef(db.translate(table, self.idFieldName, groupId, groupIdFieldName))
            return not groupId
        else:
            return True

    def save(self):
        try:
            prevId = self.itemId()
            db = QtGui.qApp.db
            db.transaction()
            try:
                record = self.getRecord()
                id = db.insertOrUpdate(db.table(self._tableName), record)
                self.saveInternals(id)
                db.commit()
            except:
                db.rollback()
                self.setItemId(prevId)
                raise
            self.setItemId(id)
            self.afterSave()
            return id
        except Exception, e:
            QtGui.qApp.logCurrentException()
            QtGui.QMessageBox.critical( self,
                                        u'Ошибка',
                                        unicode(e),
                                        QtGui.QMessageBox.Close)
            return None

    def saveInternals(self, id):
        return

    def afterSave(self):
        self.setIsDirty(False)


class CItemEditorDialog(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self, parent, tableName):
        CItemEditorBaseDialog.__init__(self, parent, tableName)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        self.edtCode.setText(forceString(record.value('code')))
        self.edtName.setText(forceString(record.value('name')))

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue('code', toVariant(forceStringEx(self.edtCode.text())))
        record.setValue('name', toVariant(forceStringEx(self.edtName.text())))
        return record

    @QtCore.pyqtSlot(QString)
    def on_edtCode_textEdited(self, text):
        self.setIsDirty()

    @QtCore.pyqtSlot(QString)
    def on_edtName_textEdited(self, text):
        self.setIsDirty()


class CRBItemsSplitListDialogEx(CItemsSplitListDialogEx):
    def duplicateCurrentRow(self):
        currentId = self.tblItems.currentItemId()
        record = self.model.getRecordById(currentId)
        code = forceString(record.value('code'))
        if self.uniqueCode:
            record.setValue('code', toVariant(code + '*')) # чтобы не дублировался код
        record.setValue('id', toVariant(0)) # чтобы не дублировался id
        db = QtGui.qApp.db
        newId = db.insertRecord(self.model.table(), record)
        if newId and QtGui.QMessageBox.question( self,
                                       u'Внимание!',
                                       u'Копировать данные подчиненной таблицы?',
                                       QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
                                       QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            subTable = self.subModel.table()
            secondaryRecords = db.getRecordList(subTable, '*', [subTable['master_id'].eq(currentId)])
            for secondaryRecord in secondaryRecords:
                secondaryRecord.setValue('id', toVariant(0))
                secondaryRecord.setValue('master_id', toVariant(newId))
                db.insertRecord(subTable, secondaryRecord)
        self.model.setIdList(self.select({}))
        return newId

    def delSelectedRows(self):
        db = QtGui.qApp.db
        selectedRowList = self.tblItems.selectedRowList()
        table = self.model.table()
        if QtGui.QMessageBox.question(self, u'Подтверждение удаления',
                                    u'Вы уверены что хотите удалить выделенные строки?(количество строк: %d)'% len(selectedRowList),
                                    QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
                                    QtGui.QMessageBox.No
                                    ) == QtGui.QMessageBox.Yes:
            for row in selectedRowList[::-1]: # удаляем в обратном порядке, чтобы избежать сдвигов
                try:
                    currentId = self.model._idList[row]
                    if currentId:
                        subTable = self.subModel.table()
                        secondaryIdList = db.getDistinctIdList(subTable, 'id', subTable['master_id'].eq(currentId))
                        for secondaryId in secondaryIdList:
                            db.deleteRecord(subTable, subTable['id'].eq(secondaryId))
                    self.model.removeRow(row)
                except CDatabaseException:
                    pass
        self.model.setIdList(self.select())
