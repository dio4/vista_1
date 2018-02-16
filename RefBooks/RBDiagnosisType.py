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

from RefBooks.Tables            import rbCode, rbName, rbDiagnosisType

from Ui_RBDiagnosisTypeEditor   import Ui_ItemEditorDialog


class CRBDiagnosisTypeList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 30),
            CTextCol(u'В диагнозе заменять на', ['replaceInDiagnosis'], 20),
            ], rbDiagnosisType, [rbCode, rbName])
        self.setWindowTitleEx(u'Типы диагнозов')

    def getItemEditor(self):
        return CRBDiagnosisTypeEditor(self)

#
# ##########################################################################
#

class CRBDiagnosisTypeEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, rbDiagnosisType)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Тип диагноза')
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(   self.edtCode,          record, 'code')
        setLineEditValue(   self.edtName,          record, 'name')
        setLineEditValue(   self.edtReplaceCode,   record, 'replaceInDiagnosis')


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(   self.edtCode,          record, 'code')
        getLineEditValue(   self.edtName,          record, 'name')
        getLineEditValue(   self.edtReplaceCode,   record, 'replaceInDiagnosis')
        return record
