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

from RefBooks.Tables            import rbCode, rbName, rbRegionalCode, rbCureType

from Ui_RBCureTypeEditor        import Ui_ItemEditorDialog


class CRBCureType(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            CTextCol(u'Региональный код', [rbRegionalCode], 20),
            CBoolCol(u'Устаревший', ['isObsolete'], 10),
            ], rbCureType, [rbCode, rbName])
        self.setWindowTitleEx(u'Виды лечения')

    def getItemEditor(self):
        return CRBCureTypeEditor(self)

#
# ##########################################################################
#

class CRBCureTypeEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, rbCureType)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Вид лечения')
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue( self.edtCode,              record, rbCode)
        setLineEditValue( self.edtName,              record, rbName)
        setLineEditValue( self.edtRegionalCode,      record, rbRegionalCode)
        setCheckBoxValue(self.chkIsObsolete, record, 'isObsolete')


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue( self.edtCode,              record, rbCode)
        getLineEditValue( self.edtName,              record, rbName)
        getLineEditValue( self.edtRegionalCode,      record, rbRegionalCode)
        getCheckBoxValue(self.chkIsObsolete, record, 'isObsolete')
        return record

