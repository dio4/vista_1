# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from library.TableModel         import *
from library.ItemsListDialog    import CItemsListDialog, CItemEditorBaseDialog
from library.interchange        import *

from Tables import *
from Ui_RBDiseaseStageEditor import Ui_ItemEditorDialog


class CRBDiseaseStageList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            CEnumCol(u'Связь с характером', ['characterRelation'],
                     [u'нет связи',  u'только для острых',  u'только для хронических', u'для острых и хронических (но не для Z-к)', u'только для Z-к'],
                     20)
            ], rbDiseaseStage, [rbCode, rbName])
        self.setWindowTitleEx(u'Стадии заболевания')

    def getItemEditor(self):
        return CRBDiseaseStageEditor(self)


class CRBDiseaseStageEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, rbDiseaseStage)
        self.setupUi(self)
        self.setWindowTitleEx(u'Стадия заболевания')
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue( self.edtCode,              record, 'code')
        setLineEditValue( self.edtName,              record, 'name')
        setComboBoxValue( self.cmbCharacterRelation, record, 'characterRelation')


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue( self.edtCode,              record, 'code')
        getLineEditValue( self.edtName,              record, 'name')
        getComboBoxValue( self.cmbCharacterRelation, record, 'characterRelation')
        return record