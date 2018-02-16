# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

from library.interchange            import getLineEditValue, getRBComboBoxValue, setLineEditValue
from library.ItemsListDialog        import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel             import CRefBookCol, CTextCol
from library.Utils                  import forceRef

from RefBooks.Tables                import rbCode, rbName

from Ui_RBNomenclatureTypeEditor    import Ui_ItemEditorDialog


class CRBNomenclatureTypeList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CRefBookCol(u'Вид',   ['kind_id'], 'rbNomenclatureKind', 20),
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            ], 'rbNomenclatureType', [rbCode, rbName])
        self.setWindowTitleEx(u'Типы ЛСиИМН')


    def getItemEditor(self):
        return CRBNomenclatureTypeEditor(self)


#
# ##########################################################################
#

class CRBNomenclatureTypeEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rbNomenclatureType')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Тип ЛСиИМН')
        self.cmbClass.setTable('rbNomenclatureClass', True)
        self.cmbKind.setTable('rbNomenclatureKind', True)
        self.setKindFilter(None)
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(   self.edtCode,          record, 'code')
        setLineEditValue(   self.edtName,          record, 'name')
        kindId = forceRef(record.value('kind_id'))
        classId = forceRef(QtGui.qApp.db.translate('rbNomenclatureKind', 'id', kindId, 'class_id'))
        self.cmbClass.setValue(classId)
        self.cmbKind.setValue(kindId)


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(   self.edtCode,          record, 'code')
        getLineEditValue(   self.edtName,          record, 'name')
        getRBComboBoxValue( self.cmbKind,          record, 'kind_id')
        return record


    def setKindFilter(self, classId):
        table = QtGui.qApp.db.table('rbNomenclatureKind')
        self.cmbKind.setFilter(table['class_id'].eq(classId))


    @QtCore.pyqtSlot(int)
    def on_cmbClass_currentIndexChanged(self, index):
        self.setKindFilter(self.cmbClass.value())
