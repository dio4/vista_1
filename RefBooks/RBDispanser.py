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

from RefBooks.Tables            import rbCode, rbName, rbDispanser
from Ui_RBDispanserEditor       import Ui_ItemEditorDialog



class CRBDispanserList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            CBoolCol(u'Наблюдается',  ['observed'], 10),
            ], rbDispanser, [rbCode, rbName])
        self.setWindowTitleEx(u'Отметки диспансерного наблюдения')

    def getItemEditor(self):
        return CRBDispanserEditor(self)


#
# ##########################################################################
#

class CRBDispanserEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, rbDispanser)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Отметка диспансерного наблюдения')
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(   self.edtCode,          record, 'code')
        setLineEditValue(   self.edtName,          record, 'name')
        setCheckBoxValue(   self.chkObserved,      record, 'observed')


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(   self.edtCode,          record, 'code')
        getLineEditValue(   self.edtName,          record, 'name')
        getCheckBoxValue(   self.chkObserved,      record, 'observed')
        return record
