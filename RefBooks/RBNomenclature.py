# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui, QtSql

from library.crbcombobox        import CRBComboBox
from library.InDocTable         import CRecordListModel
from library.interchange        import getLineEditValue, getRBComboBoxValue, getSpinBoxValue, setLineEditValue, \
                                       setSpinBoxValue
from library.ItemsListDialog    import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel         import CRefBookCol, CTextCol
from library.Utils              import forceRef, forceString, toVariant

from RefBooks.Tables            import rbCode, rbName

from Stock.NomenclatureComboBox import CNomenclatureInDocTableCol

from Ui_RBNomenclatureEditor    import Ui_ItemEditorDialog


class CRBNomenclatureList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CRefBookCol(u'Тип',   ['type_id'], 'rbNomenclatureType', 20),
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Региональный код',  ['regionalCode'], 20),
            CTextCol(u'Наименование', [rbName], 40),
            ], 'rbNomenclature', [rbCode, rbName])
        self.setWindowTitleEx(u'Номенклатура лекарственных средств и изделий медицинского назначения')


    def preSetupUi(self):
        CItemsListDialog.preSetupUi(self)
        self.actDuplicate = QtGui.QAction(u'Дублировать', self)
        self.actDuplicate.setObjectName('actDuplicate')
        self.actDelete =    QtGui.QAction(u'Удалить', self)
        self.actDelete.setObjectName('actDelete')


    def postSetupUi(self):
        CItemsListDialog.postSetupUi(self)
        self.tblItems.createPopupMenu([self.actDuplicate, '-', self.actDelete])
        self.connect(self.tblItems.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.popupMenuAboutToShow)


    def getItemEditor(self):
        return CRBNomenclatureEditor(self)


    def popupMenuAboutToShow(self):
        currentItemId = self.currentItemId()
        self.actDuplicate.setEnabled(bool(currentItemId))
        self.actDelete.setEnabled(bool(currentItemId))

    @QtCore.pyqtSlot()
    def on_actDuplicate_triggered(self):
        def duplicateCurrentInternal():
            currentItemId = self.currentItemId()
            if currentItemId :
                db = QtGui.qApp.db
                table = db.table('rbNomenclature')
                db.transaction()
                try:
                    record = db.getRecord(table, '*', currentItemId)
                    record.setValue('code', toVariant(forceString(record.value('code'))+'_1'))
                    record.setNull('id')
                    newItemId = db.insertRecord(table, record)
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
                table = db.table('rbNomenclature')
                db.deleteRecord(table, table['id'].eq(currentItemId))
                self.renewListAndSetTo()
                self.tblItems.setCurrentRow(row)
        QtGui.qApp.call(self, deleteCurrentInternal)


#
# ##########################################################################
#

class CRBNomenclatureEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rbNomenclature')
        self.addModels('Analogs', CAnalogsModel(self))
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Лекарственное средство или изделие медицинского назначения')
        self.cmbClass.setTable('rbNomenclatureClass', True)
        self.cmbKind.setTable('rbNomenclatureKind', True)
        self.cmbType.setTable('rbNomenclatureType', True)
        self.modelAnalogs.setEnableAppendLine(True)
        self.tblAnalogs.setModel(self.modelAnalogs)
        self.tblAnalogs.addPopupSelectAllRow()
        self.tblAnalogs.addPopupClearSelectionRow()
        self.tblAnalogs.addPopupSeparator()
        self.tblAnalogs.addPopupDelRow()

        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        typeId = forceRef(record.value('type_id'))
        kindId = forceRef(QtGui.qApp.db.translate('rbNomenclatureType', 'id', typeId, 'kind_id'))
        classId = forceRef(QtGui.qApp.db.translate('rbNomenclatureKind', 'id', kindId, 'class_id'))
        self.cmbClass.setValue(classId)
        self.cmbKind.setValue(kindId)
        self.cmbType.setValue(typeId)
        setLineEditValue(   self.edtCode,          record, 'code')
        setLineEditValue(   self.edtRegionalCode,  record, 'regionalCode')
        setLineEditValue(   self.edtName,          record, 'name')
        setLineEditValue(   self.edtProducer,      record, 'producer')
        setLineEditValue(   self.edtATC,           record, 'ATC')
        setSpinBoxValue(    self.spnPackSize,      record, 'packSize')
        self.modelAnalogs.loadItems(self.itemId(), forceRef(record.value('analog_id')))


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getRBComboBoxValue( self.cmbType,          record, 'type_id')
        getLineEditValue(   self.edtCode,          record, 'code')
        getLineEditValue(   self.edtRegionalCode,  record, 'regionalCode')
        getLineEditValue(   self.edtName,          record, 'name')
        getLineEditValue(   self.edtProducer,      record, 'producer')
        getLineEditValue(   self.edtATC,           record, 'ATC')
        getSpinBoxValue(    self.spnPackSize,      record, 'packSize')
        record.setValue('analog_id', toVariant(self.modelAnalogs.correctAlanogId()))
        return record


    def saveInternals(self, id):
        self.modelAnalogs.saveItems(id)


    @QtCore.pyqtSlot(int)
    def on_cmbClass_currentIndexChanged(self, index):
        classId = self.cmbClass.value()
        if classId:
            table = QtGui.qApp.db.table('rbNomenclatureKind')
            self.cmbKind.setFilter(table['class_id'].eq(classId))
        else:
            self.cmbKind.setFilter('')
        self.modelAnalogs.setDefaultClassId(classId)


    @QtCore.pyqtSlot(int)
    def on_cmbKind_currentIndexChanged(self, index):
        kindId = self.cmbKind.value()
        if kindId:
            table = QtGui.qApp.db.table('rbNomenclatureType')
            self.cmbType.setFilter(table['kind_id'].eq(kindId))
        else:
            self.cmbType.setFilter('')
        self.modelAnalogs.setDefaultKindId(kindId)


    @QtCore.pyqtSlot(int)
    def on_cmbType_currentIndexChanged(self, index):
        self.modelAnalogs.setDefaultTypeId(self.cmbType.value())


class CAnalogsModel(CRecordListModel):
    def __init__(self, parent):
        CRecordListModel.__init__(self, parent)
        self.addExtCol(CNomenclatureInDocTableCol(u'ЛСиИМН', 'id', 50, showFields = CRBComboBox.showName),
                       QtCore.QVariant.Int
                      )
        self.masterId = None # в rbNomenclature
        self.analogId = None # в rbNomenclature_analog


    def setDefaultClassId(self, classId):
        self._cols[0].setDefaultClassId(classId)


    def setDefaultKindId(self, kindId):
        self._cols[0].setDefaultClassId(kindId)


    def setDefaultTypeId(self, typeId):
        self._cols[0].setDefaultClassId(typeId)


    def getEmptyRecord(self):
        record = CRecordListModel.getEmptyRecord(self)
        record.append(QtSql.QSqlField('id', QtCore.QVariant.Int))
        return record


    def getAnalogies(self, nomenclatureIdList, analogId):
        db = QtGui.qApp.db
        table = db.table('rbNomenclature')
        items = db.getRecordList(table,
                                 'id',
                                 [table['analog_id'].eq(analogId), table['id'].notInlist(nomenclatureIdList)],
                                 'name'
                                 )
        return items


    def loadItems(self, masterId, analogId):
        self.masterId = masterId
        self.analogId = analogId
        if analogId:
            db = QtGui.qApp.db
            table = db.table('rbNomenclature')
            items = self.getAnalogies([masterId], analogId)
            self.setItems(items)


    def getIdList(self):
        idlist = []
        for item in self.items():
            id = forceRef(item.value('id'))
            if id:
                idlist.append(id)
        if self.masterId:
            idlist.append(self.masterId)
        return idlist


    def newAnalogId(self):
        db = QtGui.qApp.db
        table = db.table('rbNomenclature_Analog')
        return db.insertRecord(table, table.newRecord())


    def correctAlanogId(self):
        idlist = self.getIdList()
        if idlist:
            idlist.sort()
            db = QtGui.qApp.db
            table = db.table('rbNomenclature')
            usedAnalogIdList = db.getIdList(table,
                                            idCol='DISTINCT analog_id',
                                            where=[table['id'].inlist(idlist), table['analog_id'].isNotNull()] )
            if len(usedAnalogIdList) == 1:
                memberIdList = db.getIdList(table,
                                     'id',
                                     [table['analog_id'].eq(usedAnalogIdList[0]), table['id'].ne(self.masterId)],
                                     'id'
                                     )
                if memberIdList == idlist:
                    self.analogId = usedAnalogIdList[0]
                else:
                    self.analogId = self.newAnalogId()
            else:
                self.analogId = self.newAnalogId()
        else:
            self.analogId = None
        return self.analogId


    def saveItems(self, masterId):
        if self.analogId:
            self.masterId = masterId
            idlist = self.getIdList()
            db = QtGui.qApp.db
            table = db.table('rbNomenclature')
            db.updateRecords(table, table['analog_id'].eq(self.analogId), table['id'].inlist(idlist))


    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role==QtCore.Qt.EditRole:
            id = forceRef(value)
            if not id: # не добавляем пустую строку
                return False
            idlist = self.getIdList()
            if id in idlist: # не добавляем повторы
                return False
            result = CRecordListModel.setData(self, index, value, role)
            if not result:
                return False
            # добавляем аналоги только что указанного
            idlist.append(id)
            db = QtGui.qApp.db
            table = db.table('rbNomenclature')
            newAnalogId = db.translate(table, 'id', value, 'analog_id')
            if newAnalogId:
                row = index.row()+1
                for record in self.getAnalogies(idlist, newAnalogId):
                    self.insertRecord(row, record)
                    row += 1
            return True
        else:
            return CRecordListModel.setData(self, index, value, role)
