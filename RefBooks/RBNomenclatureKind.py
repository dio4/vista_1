# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore

from library.interchange            import getLineEditValue, getRBComboBoxValue, setLineEditValue, setRBComboBoxValue
from library.ItemsListDialog        import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel             import CRefBookCol, CTextCol

from RefBooks.Tables                import rbCode, rbName

from Ui_RBNomenclatureKindEditor    import Ui_ItemEditorDialog


class CRBNomenclatureKindList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CRefBookCol(u'Класс',     ['class_id'], 'rbNomenclatureClass', 20),
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            ], 'rbNomenclatureKind', [rbCode, rbName])
        self.setWindowTitleEx(u'Виды ЛСиИМН')


    def getItemEditor(self):
        return CRBNomenclatureKindEditor(self)


#
# ##########################################################################
#

class CRBNomenclatureKindEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rbNomenclatureKind')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Вид ЛСиИМН')
        self.cmbClass.setTable('rbNomenclatureClass', True)
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(   self.edtCode,          record, 'code')
        setLineEditValue(   self.edtName,          record, 'name')
        setRBComboBoxValue( self.cmbClass,         record, 'class_id')


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(   self.edtCode,          record, 'code')
        getLineEditValue(   self.edtName,          record, 'name')
        getRBComboBoxValue( self.cmbClass,         record, 'class_id')
        return record

