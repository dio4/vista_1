# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore

from library.InDocTable         import CInDocTableModel, CIntInDocTableCol, CTimeInDocTableCol
from library.interchange        import getLineEditValue, getSpinBoxValue, setLineEditValue, setSpinBoxValue
from library.ItemsListDialog    import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel         import CTextCol
from library.Utils              import forceInt, toVariant

from RefBooks.Tables            import rbCode, rbName

from Ui_RBActionShedule         import Ui_ItemEditorDialog


class CRBActionSheduleList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            CTextCol(u'Период',       ['period'], 20),
            ], 'rbActionShedule', [rbCode, rbName])
        self.setWindowTitleEx(u'Графики выполнения назначения')

    def getItemEditor(self):
        return CRBActionSheduleEditor(self)


class CRBActionSheduleEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rbActionShedule')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'График выполнения назначения')
        self.setupDirtyCather()
        self.addModels('Items',  CItemsModel(self))
        self.setModels(self.tblItems, self.modelItems, self.selectionModelItems)
        self.tblItems.addMoveRow()
        self.tblItems.popupMenu().addSeparator()
        self.tblItems.addPopupDelRow()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(self.edtCode, record, rbCode)
        setLineEditValue(self.edtName, record, rbName)
        setSpinBoxValue(self.edtPeriod, record, 'period')
        self.modelItems.loadItems(self.itemId())


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(self.edtCode, record, rbCode)
        getLineEditValue(self.edtName, record, rbName)
        getSpinBoxValue(self.edtPeriod, record, 'period')
        return record


    def saveInternals(self, id):
        self.modelItems.saveItems(id)


    @QtCore.pyqtSlot(int)
    def on_edtPeriod_valueChanged(self, period):
        if period>0:
            self.modelItems.setPeriod(period)


class CItemsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'rbActionShedule_Item', 'id', 'master_id', parent)
        self.colOffset = self.addCol(CIntInDocTableCol(u'День',   'offset', 10, low=1, high=7))
        self.colOffset.setSortable(True)
        self.addCol(CTimeInDocTableCol(u'Время', 'time', 20)).setSortable(True)


    def setPeriod(self, period):
        for i, item in enumerate(self.items()):
            offset = forceInt(item.value('offset'))
            if offset>=period:
                item.setValue('offset', toVariant(offset%period))
                self.emitCellChanged(i, 0)
        self.colOffset.high = period


    def data(self, index, role=QtCore.Qt.DisplayRole):
        v = CInDocTableModel.data(self, index, role)
        if index.column() == 0 and role in [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole]:
           if not v.isNull():
               v = QtCore.QVariant(forceInt(v)%self.colOffset.high+1)
        return v


    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.column() == 0 and role == QtCore.Qt.EditRole:
            value = QtCore.QVariant(max(0, forceInt(value)-1)%self.colOffset.high)
        return CInDocTableModel.setData(self, index, value, role)
