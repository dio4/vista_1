# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore

from library.ItemsListDialog    import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel         import CTextCol
from library.Utils              import forceInt, forceString, forceStringEx, toVariant

from RefBooks.Tables            import rbCode, rbName, rbOKFS

from Ui_RBOKFSEditor            import Ui_ItemEditorDialog


class CRBOKFSList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            ], rbOKFS, [rbCode, rbName])
        self.setWindowTitleEx(u'ОКФС')

    def getItemEditor(self):
        return CRBOKFSEditor(self)

#
# ##########################################################################
#

class CRBOKFSEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, rbOKFS)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Элемент справочника ОКФС')


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        self.edtCode.setText(forceString(record.value(rbCode)))
        self.edtName.setText(forceString(record.value(rbName)))
        self.cmbOwnership.setCurrentIndex(forceInt(record.value('ownership')))


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue(rbCode,    toVariant(forceStringEx(self.edtCode.text())))
        record.setValue(rbName,    toVariant(forceStringEx(self.edtName.text())))
        record.setValue('ownership',toVariant(self.cmbOwnership.currentIndex()))
        return record