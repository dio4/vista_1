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

from RefBooks.Tables            import rbCode, rbName

from Ui_RBMedicalAidKindEditor  import Ui_ItemEditorDialog


class CRBMedicalAidKindList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            CTextCol(u'Федеральный код', ['federalCode'], 10),
            CTextCol(u'Региональный код', ['regionalCode'], 10),
            ], 'rbMedicalAidKind', [rbCode, rbName])
        self.setWindowTitleEx(u'Виды медицинской помощи')


    def getItemEditor(self):
        return CRBMedicalAidKindEditor(self)

#
# ##########################################################################
#

class CRBMedicalAidKindEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rbMedicalAidKind')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Вид медицинской помощи')
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(self.edtCode,         record, 'code')
        setLineEditValue(self.edtName,         record, 'name')
        setLineEditValue(self.edtFederalCode, record,  'federalCode')
        setLineEditValue(self.edtRegionalCode, record, 'regionalCode')


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(self.edtCode,         record, 'code')
        getLineEditValue(self.edtName,         record, 'name')
        getLineEditValue(self.edtFederalCode, record,  'federalCode')
        getLineEditValue(self.edtRegionalCode, record, 'regionalCode')
        return record
