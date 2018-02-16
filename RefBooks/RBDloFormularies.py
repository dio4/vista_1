# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QVariant, QDate

from library.InDocTable                  import CInDocTableModel, CInDocTableCol, CBoolInDocTableCol, CRBInDocTableCol
from library.interchange                 import setComboBoxValue, setDateEditValue, getDateEditValue, \
    getComboBoxValue, setCheckBoxValue, getCheckBoxValue
from library.ItemsListDialog             import CItemEditorBaseDialog, CItemsListDialog
from library.TableModel                  import CTextCol, CEnumCol
from library.Utils                       import forceRef, forceString, toVariant, forceDate, forceInt

from Ui_RBFormularyEditor              import Ui_ItemEditorDialog


class CRBDloFormulariesList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CEnumCol(u'Тип',            [ 'type' ], [ u'Справочник лекарственных средств (ДЛО)' ], 40),
            CTextCol(u'Дата начала',    [ 'begDate' ], 20),
            CTextCol(u'Дата окончания', [ 'endDate' ], 20),
            CTextCol(u'Активен',        [ 'isActive' ], 20)
            ], 'DloDrugFormulary', [ 'endDate', 'type' ])
        self.setWindowTitleEx(u'Лекарственные формуляры ДЛО')


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
        return CDloFormularyEditor(self)


    def popupMenuAboutToShow(self):
        currentItemId = self.currentItemId()
        self.actDuplicate.setEnabled(bool(currentItemId))
        self.actDelete.setEnabled(bool(currentItemId))

    @QtCore.pyqtSlot()
    def on_actDuplicate_triggered(self):
        def duplicateContent(currentId, newId):
            db = QtGui.qApp.db
            table = db.table('DloDrugFormulary_Item')
            records = db.getRecordList(table, '*', table['master_id'].eq(currentId))
            for record in records:
                record.setValue('master_id', toVariant(newId))
                record.setNull('id')
                db.insertRecord(table, record)

        def duplicateGroup(currentGroupId, newGroupId):
            db = QtGui.qApp.db
            table = db.table('DloDrugFormulary')
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
                table = db.table('DloDrugFormulary')
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
                table = db.table('DloDrugFormulary')
                db.deleteRecord(table, table['id'].eq(currentItemId))
                self.renewListAndSetTo()
                self.tblItems.setCurrentRow(row)
        QtGui.qApp.call(self, deleteCurrentInternal)


class CDloFormularyEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'DloDrugFormulary')
        self.addModels('Items', CItemsModel(self))
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Лекарственный формуляр ДЛО')
        self.prepareTable(self.tblItems, self.modelItems)
        self.cmbType.addItem(u'Справочник лекарственных средств (ДЛО)')

        tmpDate = QDate().currentDate().addMonths(1)
        begDate = (QDate(tmpDate.year(), tmpDate.month(), 1))
        self.edtBegDate.setDate(begDate)
        self.edtEndDate.setDate(begDate.addMonths(1).addDays(-1))

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
        mnn = forceString(item.value('mnn'))
        latinMnn = forceString(item.value('latinMnn'))
        issueForm = forceString(item.value('issueForm'))
        latinIssueForm = forceString(item.value('latinIssueForm'))
        unitId = forceRef(item.value('baseUnit_id'))
        dosage = forceString(item.value('dosage'))
        qnt = forceInt(item.value('qnt'))
        result = result and (mnn or self.checkInputMessage(u'МНН', False, self.tblItems, row, 0))
        result = result and (latinMnn or self.checkInputMessage(u'МНН на латинском языке', False, self.tblItems, row, 1))
        result = result and (issueForm or self.checkInputMessage(u'форму выпуска', False, self.tblItems, row, 2))
        result = result and (latinIssueForm or self.checkInputMessage(u'форму выпуска на латинском языке', False, self.tblItems, row, 3))
        result = result and (dosage or self.checkInputMessage(u'дозировку препарата', False, self.tblItems, 4))
        result = result and (qnt or self.checkInputMessage(u'количество единиц', False, self.tblItems, 5))
        result = result and (unitId or self.checkInputMessage(u'базовую единицу измерения', False, self.tblItems, row, 7))
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
        record.setValue('orgStructure_id', toVariant(QtGui.qApp.currentOrgStructureId()))
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
        CInDocTableModel.__init__(self, 'DloDrugFormulary_Item', 'id', 'master_id', parent)
        self.addCol(CInDocTableCol(u'Код', 'code', 50)).setValueType(QVariant.Int)
        self.addCol(CRBInDocTableCol(u'МНН', 'mnn_id', 200, 'dlo_rbMNN')).setValueType(QVariant.String)
        self.addCol(CInDocTableCol(u'Наименование', 'name', 500)).setValueType(QVariant.String)
        self.addCol(CRBInDocTableCol(u'Форма выпуска', 'issueForm_id', 400, 'dlo_rbIssueForm')).setValueType(QVariant.String)
        self.addCol(CRBInDocTableCol(u'Торговое наименование', 'tradeName_id', 400, 'dlo_rbTradeName')).setValueType(QVariant.String)
        self.addCol(CInDocTableCol(u'Дозировка кол.', 'dosageQnt', 50)).setValueType(QVariant.Int)
        self.addCol(CRBInDocTableCol(u'Дозировка (ед.)', 'dosage_id', 200, 'dlo_rbDosage')).setValueType(QVariant.String)
        self.addCol(CInDocTableCol(u'Кол.ед.', 'qnt', 50)).setValueType(QVariant.Int)
        self.addCol(CBoolInDocTableCol(u'Наркотик?', 'isDrugs', 400)).setValueType(QVariant.Bool)
        self.addCol(CRBInDocTableCol(u'Единица измерения (базовая)', 'baseUnit_id', 100, 'rbUnit')).setValueType(QVariant.Int)

        self._idxFieldName = 'name'