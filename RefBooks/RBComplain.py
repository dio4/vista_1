# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore

from Ui_RBComplainEditor import Ui_ComplainEditorDialog
from library.HierarchicalItemsListDialog import CHierarchicalItemsListDialog
from library.ItemsListDialog import CItemEditorBaseDialog
from library.TableModel import CTextCol
from library.Utils import forceString, toVariant
from library.interchange import getLineEditValue, getRBComboBoxValue, setLineEditValue, setRBComboBoxValue


class CRBComplainList(CHierarchicalItemsListDialog):
    def __init__(self, parent):
        CHierarchicalItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код', ['code'], 20),
            CTextCol(u'Наименование', ['name'], 40),
        ], 'rbComplain', ['code', 'name', 'id'])
        self.setWindowTitleEx(u'Жалобы')
        self.modelTree.setLeavesVisible(True)
        self.actDuplicate = QtGui.QAction(u'Дублировать', self)
        self.actDuplicate.setObjectName('actDuplicate')
        self.connect(self.actDuplicate, QtCore.SIGNAL('triggered()'), self.duplicateCurrentRow)
        self.tblItems.createPopupMenu([self.actDuplicate])
        self.tblItems.addPopupDelSelectedRow()

    def getItemEditor(self):
        return CComplainEditor(self)

    def duplicateCurrentRow(self):
        def duplicateCurrentInternal():
            currentItemId = self.currentItemId()
            if currentItemId:
                db = QtGui.qApp.db
                table = db.table('Complain')
                db.transaction()
                try:
                    record = db.getRecord(table, '*', currentItemId)
                    record.setValue('code', toVariant(forceString(record.value('code')) + '_1'))
                    record.setValue('name', toVariant(forceString(record.value('name')) + '_1'))
                    record.setNull('id')
                    newItemId = db.insertRecord(table, record)
                    db.commit()
                except:
                    db.rollback()
                    QtGui.qApp.logCurrentException()
                    raise
                self.renewListAndSetTo(newItemId)

        QtGui.qApp.call(self, duplicateCurrentInternal)


class CComplainEditor(CItemEditorBaseDialog, Ui_ComplainEditorDialog):
    def __init__(self, parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rbComplain')
        self.setupUi(self)
        self.setWindowTitleEx(u'Жалоба')
        self.cmbGroup.setTable('rbComplain')
        self.setupDirtyCather()

    def setGroupId(self, id):
        self.cmbGroup.setValue(id)
        self.setIsDirty(False)

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(self.edtCode, record, 'code')
        setLineEditValue(self.edtName, record, 'name')
        setRBComboBoxValue(self.cmbGroup, record, 'group_id')
        self.setIsDirty(False)

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(self.edtCode, record, 'code')
        getLineEditValue(self.edtName, record, 'name')
        getRBComboBoxValue(self.cmbGroup, record, 'group_id')
        return record

    def checkDataEntered(self):
        result = CItemEditorBaseDialog.checkDataEntered(self)
        return result
