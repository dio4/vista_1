# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2015 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QVariant, QDate
from Events.FormularyItemComboBox import CFormularyItemInDocTableCol

from library.InDocTable                  import CInDocTableModel, CInDocTableCol
from library.interchange                 import setComboBoxValue, setDateEditValue, getDateEditValue, \
    getComboBoxValue, setCheckBoxValue, getCheckBoxValue
from library.ItemsListDialog             import CItemEditorBaseDialog, CItemsListDialog
from library.TableModel                  import CTextCol, CEnumCol
from library.Utils                       import toVariant, forceDate, forceInt

from Ui_RBFormularyEditor              import Ui_ItemEditorDialog


class CRBFormulariesList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CEnumCol(u'Тип',            [ 'type' ], [ u'Формуляр отделение', u'Наркотики', u'Расходные материалы' ], 40),
            CTextCol(u'Дата начала',    [ 'begDate' ], 20),
            CTextCol(u'Дата окончания', [ 'endDate' ], 20),
            CTextCol(u'Активен',        [ 'isActive' ], 20)
            ], 'DrugFormulary', [ 'endDate', 'type' ])
        self.setWindowTitleEx(u'Лекарственные формуляры')


    def preSetupUi(self):
        CItemsListDialog.preSetupUi(self)
        self.actDuplicate = QtGui.QAction(u'Дублировать', self)
        self.actDuplicate.setObjectName('actDuplicate')
        self.actDelete =    QtGui.QAction(u'Удалить', self)
        self.actDelete.setObjectName('actDelete')
        #self.addObject('btnImport',  QtGui.QPushButton(u'Импорт F2', self))

    def postSetupUi(self):
        #self.buttonBox.addButton(self.btnImport, QtGui.QDialogButtonBox.ActionRole)
        CItemsListDialog.postSetupUi(self)
        self.tblItems.createPopupMenu([self.actDuplicate, '-', self.actDelete])
        self.connect(self.tblItems.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.popupMenuAboutToShow)

    #def setup(self, cols, tableName, order, forSelect=False, filterClass=None):
    #    CItemsListDialog.setup(self, cols, tableName, order, forSelect, filterClass)
    #    self.btnImport.setShortcut(Qt.Key_F2)

    def getItemEditor(self):
        return CFormularyEditor(self)


    def popupMenuAboutToShow(self):
        currentItemId = self.currentItemId()
        self.actDuplicate.setEnabled(bool(currentItemId))
        self.actDelete.setEnabled(bool(currentItemId))

    @QtCore.pyqtSlot()
    def on_actDuplicate_triggered(self):
        def duplicateContent(currentId, newId):
            db = QtGui.qApp.db
            table = db.table('DrugFormulary_Item')
            records = db.getRecordList(table, '*', table['master_id'].eq(currentId))
            for record in records:
                record.setValue('master_id', toVariant(newId))
                record.setNull('id')
                db.insertRecord(table, record)

        def duplicateGroup(currentGroupId, newGroupId):
            db = QtGui.qApp.db
            table = db.table('DrugFormulary')
            records = db.getRecordList(table, '*', table['group_id'].eq(currentGroupId))
            for record in records:
                currentItemId = record.value('id')
                record.setValue('id', toVariant(newGroupId))
                newItemId = db.insertRecord(table, record)
                duplicateGroup(currentItemId, newItemId)
                duplicateContent(currentItemId, newItemId)

        def duplicateCurrentInternal():
            currentItemId = self.currentItemId()
            if currentItemId :
                db = QtGui.qApp.db
                table = db.table('DrugFormulary')
                db.transaction()
                try:
                    record = db.getRecord(table, '*', currentItemId)
                    record.setNull('id')
                    newItemId = db.insertRecord(table, record)
                    duplicateGroup(currentItemId, newItemId)
                    duplicateContent(currentItemId, newItemId)
                    db.commit()
                except:
                    db.rollback()
                    QtGui.qApp.logCurrentException()
                    raise
                self.renewListAndSetTo(newItemId)
        QtGui.qApp.call(self, duplicateCurrentInternal)

    @QtCore.pyqtSlot()
    def on_actDelete_triggered(self):
        def deleteCurrentInternal():
            currentItemId = self.currentItemId()
            if currentItemId :
                row = self.tblItems.currentIndex().row()
                db = QtGui.qApp.db
                table = db.table('DrugFormulary')
                db.deleteRecord(table, table['id'].eq(currentItemId))
                self.renewListAndSetTo()
                self.tblItems.setCurrentRow(row)
        QtGui.qApp.call(self, deleteCurrentInternal)


class CFormularyEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'DrugFormulary')
        self.addModels('Items', CItemsModel(self))
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Лекарственный формуляр')
        self.prepareTable(self.tblItems, self.modelItems)
        self.cmbType.addItems([ u'Формуляр отделение', u'Наркотики', u'Расходные материалы' ])

        tmpDate = QDate().currentDate().addMonths(1)
        begDate = (QDate(tmpDate.year(), tmpDate.month(), 1))
        self.edtBegDate.setDate(begDate)
        self.edtEndDate.setDate(begDate.addMonths(1).addDays(-1))
        self.chkIsActive.setChecked(True)

        self.setupDirtyCather()


    def prepareTable(self, tblWidget, model):
        tblWidget.setModel(model)
        tblWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        tblWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        tblWidget.addPopupDuplicateCurrentRow()
        tblWidget.addPopupSeparator()
        tblWidget.addMoveRow()
        tblWidget.addPopupDelRow()


    def checkDataEntered(self):
        result = True
        begDate = forceDate(self.edtBegDate.date())
        endDate = forceDate(self.edtEndDate.date())
        itemsCnt = len(self.modelItems._items)
        result = result and (begDate < endDate or self.checkValueMessage(u'Дата начала должна быть меньше даты окончания!', False, self, None, None))
        result = result and (itemsCnt > 0 or self.checkValueMessage(u'Необходимо заполнить табличную часть формуляра!', False, self, None, None))
        for row, item in enumerate(self.modelItems.items()):
           if not self.checkItemDataEntered(row, item):
               return False
        return result


    def checkItemDataEntered(self, row, item):
        result = True
        drugId = forceInt(item.value('drug_id'))
        limit = forceInt(item.value('limit'))
        result = result and (drugId or self.checkInputMessage(u'препарат', False, self.tblItems, row, 0))
        result = result and (limit or self.checkInputMessage(u'количество', False, self.tblItems, row, 1))
        return result


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setComboBoxValue(   self.cmbType,          record, 'type')
        setDateEditValue(   self.edtBegDate,       record, 'begDate')
        setDateEditValue(   self.edtEndDate,       record, 'endDate')
        setCheckBoxValue(   self.chkIsActive,      record, 'isActive')
        if forceInt(record.value('isReadOnly')):
            self.tblItems.model().setEditable(False)
        self.modelItems.loadItems(self.itemId())


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue('orgStructure_id', toVariant(QtGui.qApp.currentOrgStructureId() if QtGui.qApp.currentOrgStructureId() else QtGui.qApp.currentOrgId()))
        getComboBoxValue(   self.cmbType,          record, 'type')
        getDateEditValue(   self.edtBegDate,       record, 'begDate')
        getDateEditValue(   self.edtEndDate,       record, 'endDate')
        getCheckBoxValue(   self.chkIsActive,      record, 'isActive')
        record.setValue('deleted', toVariant(0))
        return record


    def saveInternals(self, id):
        self.modelItems.saveItems(id)


class CItemsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'DrugFormulary_Item', 'id', 'master_id', parent)
        self.addCol(CFormularyItemInDocTableCol(u'Препарат', 'drug_id', 400, order='name ASC')).setValueType(QVariant.Int)
        self.addCol(CInDocTableCol(u'Кол.ед.', 'limit', 50)).setValueType(QVariant.Int)

