# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore

from RefBooks.Tables import rbCode, rbName, rbDeferredQueueStatus
from library.ItemsListDialog import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel import CTextCol, CBoolCol
from library.Utils import toVariant
from library.interchange import getLineEditValue, setLineEditValue, getCheckBoxValue, setCheckBoxValue

from Ui_RBDeferredQueueStatusEditor import Ui_ItemEditorDialog


class CRBDeferredQueueStatus(CItemsListDialog):

    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код', [rbCode], 20),
            CTextCol(u'Flatсode', ['flatCode'], 20),
            CTextCol(u'Наименование', [rbName], 40),
            CBoolCol(u'Разрешается выбор в ЖОС', ['isSelectable'], 10)
        ], rbDeferredQueueStatus, [rbCode, rbName])
        self.setWindowTitleEx(u'Статусы записей в ЖОС')

    def preSetupUi(self):
        CItemsListDialog.preSetupUi(self)
        self.actCopy = QtGui.QAction(u'Дублировать', self)
        self.actCopy.setObjectName('actCopy')
        self.actEdit = QtGui.QAction(u'Редактировать', self)
        self.actEdit.setObjectName('actEdit')
        self.actDelete = QtGui.QAction(u'Удалить', self)
        self.actDelete.setObjectName('actDelete')
        self.connect(self.actEdit, QtCore.SIGNAL('triggered()'), self.on_btnEdit_clicked)

    def postSetupUi(self):
        CItemsListDialog.postSetupUi(self)
        self.tblItems.createPopupMenu([self.actCopy, self.actEdit, self.actDelete])

    @QtCore.pyqtSlot()
    def on_actCopy_triggered(self):
        def copyCurrentInternal():
            currentItemId = self.currentItemId()
            if currentItemId:
                row = self.tblItems.currentIndex().row()
                db = QtGui.qApp.db
                table = db.table(rbDeferredQueueStatus)
                newRecord = table.newRecord(otherRecord=db.getRecord(table, '*', currentItemId))
                db.insertRecord(table, newRecord)
                self.renewListAndSetTo()
                self.tblItems.setCurrentRow(row)
        QtGui.qApp.call(self, copyCurrentInternal)

    @QtCore.pyqtSlot()
    def on_actDelete_triggered(self):
        def deleteCurrentInternal():
            currentItemId = self.currentItemId()
            if currentItemId:
                row = self.tblItems.currentIndex().row()
                db = QtGui.qApp.db
                table = db.table(rbDeferredQueueStatus)
                record = db.getRecord(table, '*', currentItemId)
                record.setValue('deleted', toVariant(1))
                db.updateRecord(table, record)
                self.renewListAndSetTo()
                self.tblItems.setCurrentRow(row)
        QtGui.qApp.call(self, deleteCurrentInternal)

    def getItemEditor(self):
        return CRBDeferredQueueStatusEditor(self)


class CRBDeferredQueueStatusEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):

    flatCodeToolTipText = u"""Поле регламентирует настройку "автоматического проставления статуса" для записей в журнале отложенного спроса:
"onExpired" - запись обрабатывается автоматически при истекшем сроке ожидания пациента (текущая дата > максимальной даты в ЖОС).
"onEnqueued" - запись обрабатывается автоматически при постановки пациента в очередь к врачу ожидающей специальности.
"onEventCreated" - запись обрабатывается автоматически при создании обращения на прием к врачу ожидающей специальности.
Автоматическая настройка сработает только при включении 56 глобальной настройки (56 - ЖОС. Автоматическая обработка записей)'"""

    def __init__(self, parent):
        CItemEditorBaseDialog.__init__(self, parent, rbDeferredQueueStatus)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Статус записи в ЖОС')
        self.setupDirtyCather()
        self.lblFlatCodeAbout.setToolTip(CRBDeferredQueueStatusEditor.flatCodeToolTipText)

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(self.edtCode, record, rbCode)
        setLineEditValue(self.edtFlatCode, record, 'flatCode')
        setLineEditValue(self.edtName, record, rbName)
        setCheckBoxValue(self.chkIsSelectable, record, 'isSelectable')

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(self.edtCode, record, rbCode)
        getLineEditValue(self.edtFlatCode, record, 'flatCode')
        getLineEditValue(self.edtName, record, rbName)
        getCheckBoxValue(self.chkIsSelectable, record, 'isSelectable')
        return record
