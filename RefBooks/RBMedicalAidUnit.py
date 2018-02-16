# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore

from library.interchange        import getLineEditValue, setLineEditValue
from library.ItemsListDialog    import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel         import CTextCol

from RefBooks.Tables            import rbCode, rbName, rbMedicalAidUnit

from Ui_RBMedicalAidUnitEditor  import Ui_ItemEditorDialog


class CRBMedicalAidUnitList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode],   8),
            CTextCol(u'Наименование', [rbName],   8),
            CTextCol(u'Описание',     ['descr'], 64),
            CTextCol(u'Региональный код',     ['regionalCode'], 64),
            CTextCol(u'Федеральный код',     ['federalCode'], 8),
            ], rbMedicalAidUnit, [rbCode, rbName])
        self.setWindowTitleEx(u'Единицы учета медицинской помощи')

    def getItemEditor(self):
        return CRBMedicalAidUnitEditor(self)


class CRBMedicalAidUnitEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, rbMedicalAidUnit)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Единица учета медицинской помощи')
        self.setupDirtyCather()

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(self.edtCode, record, 'code')
        setLineEditValue(self.edtName, record, 'name')
        setLineEditValue(self.edtDescr, record, 'descr')
        setLineEditValue(self.edtRegionalCode, record, 'regionalCode')
        setLineEditValue(self.edtFederalCode, record, 'federalCode')

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(self.edtCode, record, 'code')
        getLineEditValue(self.edtName, record, 'name')
        getLineEditValue(self.edtDescr, record, 'descr')
        getLineEditValue(self.edtRegionalCode, record, 'regionalCode')
        getLineEditValue(self.edtFederalCode, record, 'federalCode')
        return record
