# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from library.interchange        import getLineEditValue, setLineEditValue
from library.ItemsListDialog    import CItemsListDialog, CItemEditorDialog
from library.TableModel         import CTextCol

from RefBooks.Tables            import rbActivity, rbCode, rbName

from Ui_RBActivityEditor        import Ui_ItemEditorDialog


class CRBActivityList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 8),
            CTextCol(u'Региональный код', ['regionalCode'], 8),
            CTextCol(u'Наименование', [rbName], 40),
            ], rbActivity, [rbCode, rbName])
        self.setWindowTitleEx(u'Виды(типы) деятельности врача')
        self.tblItems.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.actSelectAllRow = QtGui.QAction(u'Выделить все строки', self)
        self.tblItems.addPopupAction(self.actSelectAllRow)
        self.connect(self.actSelectAllRow, QtCore.SIGNAL('triggered()'), self.selectAllRowTblItem)
        self.actClearSelectionRow = QtGui.QAction(u'Снять выделение', self)
        self.tblItems.addPopupAction(self.actClearSelectionRow)
        self.connect(self.actClearSelectionRow, QtCore.SIGNAL('triggered()'), self.clearSelectionRow)
        self.actDelete = QtGui.QAction(u'Удалить', self)
        self.tblItems.addPopupAction(self.actDelete)
        self.connect(self.actDelete, QtCore.SIGNAL('triggered()'), self.deleteSelected)

    def getItemEditor(self):
        return CRBActivityEditor(self)

    def selectAllRowTblItem(self):
        self.tblItems.selectAll()

    def clearSelectionRow(self):
        self.tblItems.clearSelection()

    def deleteSelected(self):
        db = QtGui.qApp.db
        selectedIdList = self.tblItems.selectedItemIdList()
        if QtGui.QMessageBox.question(self, u'Подтверждение удаления',
                                    u'Вы уверены что хотите удалить выделенные строки?(количество строк: %d)'% len(selectedIdList),
                                    QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
                                    QtGui.QMessageBox.No
                                    ) == QtGui.QMessageBox.Yes:
            for id in selectedIdList:
                tableActivity = db.table('rbActivity')
                tablePersonActivity = db.table('Person_Activity')
                db.deleteRecord(tableActivity, tableActivity['id'].eq(id))
                db.deleteRecord(tablePersonActivity, tablePersonActivity['activity_id'].eq(id))
                self.renewListAndSetTo(None)

class CRBActivityEditor(CItemEditorDialog, Ui_ItemEditorDialog):
    setupUi = Ui_ItemEditorDialog.setupUi
    retranslateUi = Ui_ItemEditorDialog.retranslateUi

    def __init__(self,  parent):
        CItemEditorDialog.__init__(self, parent, rbActivity)
        self.setWindowTitleEx(u'Вид(тип) деятельности врача')

    def setRecord(self, record):
        CItemEditorDialog.setRecord(self, record)
        setLineEditValue(self.edtRegionalCode, record, 'regionalCode')

    def getRecord(self):
        record = CItemEditorDialog.getRecord(self)
        getLineEditValue(self.edtRegionalCode, record, 'regionalCode')
        return record
