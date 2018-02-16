# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.crbcombobox        import CRBComboBox
from library.InDocTable         import CInDocTableModel, CRBInDocTableCol
from library.interchange        import getCheckBoxValue, getLineEditValue, getRBComboBoxValue, setCheckBoxValue, \
                                       setLineEditValue, setRBComboBoxValue
from library.ItemsListDialog    import CItemEditorBaseDialog, CRBItemsSplitListDialogEx
from library.TableModel         import CBoolCol, CRefBookCol, CTextCol

from RefBooks.Tables            import rbCode, rbName, rbPatientModel

from Ui_RBPatientModelEditor    import Ui_ItemEditorDialog


class CRBPatientModel(CRBItemsSplitListDialogEx):
    def __init__(self, parent):
        CRBItemsSplitListDialogEx.__init__(self, parent, rbPatientModel, [
            CTextCol(u'Код',          [rbCode], 20),
            CBoolCol(u'Устаревший', ['isObsolete'], 10),
            CTextCol(u'Наименование', [rbName], 20),
            CTextCol(u'Диагноз', ['MKB'], 20),
            CRefBookCol(u'Вид ВТМП', ['quotaType_id'], 'QuotaType', 40)
            ],
            [rbCode, rbName],
            'rbPatientModel_Item',
            [
            CRefBookCol(u'Вид лечения', ['cureType_id'], 'rbCureType', 40),
            CRefBookCol(u'Метод лечения', ['cureMethod_id'], 'rbCureMethod', 40)
            ],
            'master_id', 'id'
            )
        self.setWindowTitleEx(u'Модели пациента')


    def getItemEditor(self):
        return CRBPatientModelEditor(self)


    def select(self, props=None):
        if not props:
            props = {}
        table = self.model.table()
        return QtGui.qApp.db.getIdList(table.name(), 'id')

#
# ##########################################################################
#

class CRBPatientModelEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, rbPatientModel)
        self.addModels('TypeMetodCure', CTypeMetodCureModel(self))
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Модель пациента')
        self.setModels(self.tblItems, self.modelTypeMetodCure, self.selectionModelTypeMetodCure)
        self.tblItems.addMoveRow()
        self.tblItems.addPopupDelRow()
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(self.edtCode,        record, 'code')
        setLineEditValue(self.edtName,        record, 'name')
        setLineEditValue(self.edtMKB,         record, 'MKB')
        setRBComboBoxValue(self.cmbQuotaType, record, 'quotaType_id')
        setCheckBoxValue(self.chkIsObsolete, record, 'isObsolete')
        self.modelTypeMetodCure.loadItems(self.itemId())


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(self.edtCode,        record, 'code')
        getLineEditValue(self.edtName,        record, 'name')
        getLineEditValue(self.edtMKB,         record, 'MKB')
        getRBComboBoxValue(self.cmbQuotaType, record, 'quotaType_id')
        getCheckBoxValue(self.chkIsObsolete, record, 'isObsolete')
        return record


    def saveInternals(self, id):
        self.modelTypeMetodCure.saveItems(id)


class CTypeMetodCureModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'rbPatientModel_Item', 'id', 'master_id', parent)
        self.addCol(CRBInDocTableCol(u'Вид лечения',  'cureType_id', 20, 'rbCureType', showFields = CRBComboBox.showName, filter = 'isObsolete = 0'))
        self.addCol(CRBInDocTableCol(u'Метод лечения', 'cureMethod_id', 20, 'rbCureMethod', showFields = CRBComboBox.showName, filter = 'isObsolete = 0'))
