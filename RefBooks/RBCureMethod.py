# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore

from library.interchange        import getCheckBoxValue, getLineEditValue, setCheckBoxValue, setLineEditValue
from library.ItemsListDialog    import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel         import CBoolCol, CTextCol

from RefBooks.Tables            import rbCode, rbName, rbRegionalCode, rbCureMethod

from Ui_RBCureMethodEditor      import Ui_ItemEditorDialog


class CRBCureMethod(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            CTextCol(u'Региональный код', [rbRegionalCode], 20),
            CBoolCol(u'Устаревший', ['isObsolete'], 10),
            ], rbCureMethod, [rbCode, rbName])
        self.setWindowTitleEx(u'Методы лечения')

    def getItemEditor(self):
        return CRBMethodCureEditor(self)

#
# ##########################################################################
#

class CRBMethodCureEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, rbCureMethod)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Метод лечения')
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue( self.edtCode,              record, 'code')
        setLineEditValue( self.edtName,              record, 'name')
        setLineEditValue( self.edtRegionalCode,      record, 'regionalCode')
        setCheckBoxValue(self.chkIsObsolete, record, 'isObsolete')


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue( self.edtCode,              record, 'code')
        getLineEditValue( self.edtName,              record, 'name')
        getLineEditValue( self.edtRegionalCode,      record, 'regionalCode')
        getCheckBoxValue(self.chkIsObsolete, record, 'isObsolete')
        return record
