# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore
from library.Utils import forceTr

from library.interchange            import getLineEditValue, setLineEditValue, setCheckBoxValue, getCheckBoxValue
from library.ItemsListDialog        import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel             import CTextCol

from RefBooks.Tables                import rbCode, rbName

from Ui_RBMesSpecificationEditor    import Ui_ItemEditorDialog


class CRBMesSpecificationList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',              [rbCode],         20),
            CTextCol(u'Наименование',     [rbName],         40),
            CTextCol(u'Региональный код', ['regionalCode'], 40),
            ], 'rbMesSpecification', [rbCode, rbName])
        self.setWindowTitleEx(u'Особенности выполнения %s' % forceTr(u'МЭС', u'RBMesSpecification'))

    def getItemEditor(self):
        return CRBMesSpecificationEditor(self)


class CRBMesSpecificationEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rbMesSpecification')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Особенность выполнения МЭС')
        self.setupDirtyCather()

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(   self.edtCode,         record, 'code')
        setLineEditValue(   self.edtName,         record, 'name')
        setLineEditValue(   self.edtRegionalCode, record, 'regionalCode')
        setCheckBoxValue(   self.chkDone,         record, 'done')

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(   self.edtCode,         record, 'code')
        getLineEditValue(   self.edtName,         record, 'name')
        getLineEditValue(   self.edtRegionalCode, record, 'regionalCode')
        getCheckBoxValue(   self.chkDone,         record, 'done')
        return record
