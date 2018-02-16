# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore

from library.ItemsListDialog    import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel         import CColorCol, CTextCol
from library.Utils              import forceString, forceStringEx, toVariant

from RefBooks.Tables            import rbCode, rbName

from Ui_RBStatusObservationClientEditor import Ui_ItemEditorDialog


class CRBStatusObservationClientTypeList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            CColorCol(u'Цветовая маркеровка', ['color'], 10, 'r')
            ], 'rbStatusObservationClientType', [rbCode, rbName])
        self.setWindowTitleEx(u'Статус наблюдения пациента')

    def getItemEditor(self):
        return CRBStatusObservationClientEditor(self)


class CRBStatusObservationClientEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rbStatusObservationClientType')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Статус наблюдения пациента')
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        self.edtCode.setText(forceString(record.value(rbCode)))
        self.edtName.setText(forceString(record.value(rbName)))
        self.cmbColor.setColor(forceString(record.value('color')))


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue(rbCode,       toVariant(forceStringEx(self.edtCode.text())))
        record.setValue(rbName,       toVariant(forceStringEx(self.edtName.text())))
        record.setValue('color',      QtCore.QVariant(self.cmbColor.colorName()))
        return record
