# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

from library.crbcombobox import CRBComboBox
from library.HierarchicalItemsListDialog import CHierarchicalItemsListDialog
from library.InDocTable import CRBInDocTableCol, CInDocTableModel, CBoolInDocTableCol
from library.interchange import getCheckBoxValue, getLineEditValue, setCheckBoxValue, setLineEditValue
from library.ItemsListDialog import CItemEditorBaseDialog
from library.TableModel import CTextCol
from library.Utils import forceBool, forceRef, toVariant, forceString

from Ui_RBSocStatusClassItemEditor import Ui_SocStatusClassItemEditorDialog


class CRBSocStatusClassList(CHierarchicalItemsListDialog):
    def __init__(self, parent):
        CHierarchicalItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код', ['code'], 20),
            CTextCol(u'Наименование', ['name'], 40),
        ], 'rbSocStatusClass', ['code', 'name', 'id'])
        self.setWindowTitleEx(u'Классы социального статуса')

    def preSetupUi(self):
        CHierarchicalItemsListDialog.preSetupUi(self)
        self.modelTree.setLeavesVisible(True)
        self.modelTree.setOrder('code')
        #        self.addObject('actDuplicate', QtGui.QAction(u'Дублировать', self))
        self.actDelete = QtGui.QAction(u'Удалить', self)
        self.actDelete.setObjectName('actDelete')

    def postSetupUi(self):
        CHierarchicalItemsListDialog.postSetupUi(self)
        #        self.tblItems.createPopupMenu([self.actDuplicate, '-', self.actDelete])
        self.tblItems.createPopupMenu([self.actDelete])
        self.connect(self.tblItems.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.popupMenuAboutToShow)

    def getItemEditor(self):
        editor = CSocStatusClassItemEditor(self)
        editor.setGroupId(self.currentGroupId())
        return editor

    def popupMenuAboutToShow(self):
        currentItemId = self.currentItemId()
        #        self.actDuplicate.setEnabled(bool(currentItemId))
        self.actDelete.setEnabled(bool(currentItemId))




    @QtCore.pyqtSlot()
    def on_actDelete_triggered(self):
        def deleteCurrentInternal():
            currentItemId = self.currentItemId()
            if currentItemId:
                row = self.tblItems.currentIndex().row()
                db = QtGui.qApp.db
                table = db.table('rbSocStatusClass')
                db.deleteRecord(table, table['id'].eq(currentItemId))
                self.renewListAndSetTo()
                self.tblItems.setCurrentRow(row)

        QtGui.qApp.call(self, deleteCurrentInternal)


#
# ##########################################################################
#

class CSocStatusClassItemEditor(CItemEditorBaseDialog, Ui_SocStatusClassItemEditorDialog):
    def __init__(self, parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rbSocStatusClass')
        self.addModels('Types', CTypesModel(self))
        self.setupUi(self)
        self.setModels(self.tblTypes, self.modelTypes, self.selectionModelTypes)
        self.tblTypes.addPopupDelRow()
        self.setWindowTitleEx(u'Класс социального статуса')
        self.setupDirtyCather()
        self.groupId = None

    def setGroupId(self, id):
        self.groupId = id

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(self.edtCode, record, 'code')
        setLineEditValue(self.edtName, record, 'name')
        setCheckBoxValue(self.chkShowInClientInfo, record, 'isShowInClientInfo')
        setCheckBoxValue(self.chkTightControl, record, 'tightControl')
        if u'онко' in QtGui.qApp.currentOrgInfis():
            setCheckBoxValue(self.chkSoftControl, record, 'softControl')
        else:
            self.chkSoftControl.setVisible(False)
        setCheckBoxValue(self.chkAutoDateClose, record, 'autoCloseDate')
        self.groupId = forceRef(record.value('group_id'))
        self.modelTypes.loadItems(self.itemId())
        self.setIsDirty(False)

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(self.edtCode, record, 'code')
        getLineEditValue(self.edtName, record, 'name')
        getCheckBoxValue(self.chkShowInClientInfo, record, 'isShowInClientInfo')
        getCheckBoxValue(self.chkTightControl, record, 'tightControl')
        if u'онко' in QtGui.qApp.currentOrgInfis():
            getCheckBoxValue(self.chkSoftControl, record, 'softControl')
        getCheckBoxValue(self.chkAutoDateClose, record, 'autoCloseDate')
        record.setValue('group_id', toVariant(self.groupId))
        return record

    def saveInternals(self, id):
        self.modelTypes.saveItems(id)

    def checkDataEntered(self):
        result = CItemEditorBaseDialog.checkDataEntered(self)
        #        result = result and (self.checkRecursion(self.cmbGroup.value()) or self.checkValueMessage(u'попытка создания циклической группировки', False, self.cmbGroup))
        return result


class CTypesModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'rbSocStatusClassTypeAssoc', 'id', 'class_id', parent)
        self.addCol(
            CRBInDocTableCol(u'Наименование', 'type_id', 20, 'rbSocStatusType', showFields=CRBComboBox.showNameAndCode))
        self.addCol(CBoolInDocTableCol(u'По умолчанию', 'isDefault', 20))

    #        self.setEnableAppendLine(True)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        result = CInDocTableModel.setData(self, index, value, role)
        if result and role == QtCore.Qt.CheckStateRole and index.column() == 1 and forceBool(value):
            for row, record in enumerate(self._items):
                if row != index.row():
                    record.setValue('isDefault', toVariant(False))
                    self.emitCellChanged(row, 1)
        return result
