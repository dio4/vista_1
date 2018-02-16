# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4                      import QtCore

from library.interchange        import getDoubleBoxValue, getLineEditValue, getRBComboBoxValue, setDoubleBoxValue, setLineEditValue, setRBComboBoxValue
from library.ItemsListDialog    import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel         import CColorCol, CRefBookCol, CSumCol, CTextCol
from library.Utils              import forceString

from RefBooks.Tables            import rbCode, rbName

from Ui_RBContainerTypeEditor   import Ui_RBContainerTypeEditor


CAmountCol = CSumCol

class CRBContainerTypeList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            CColorCol(u'Цветовая маркеровка', ['color'], 10, 'r'),
            CAmountCol(u'Объем', ['amount'], 10),
            CRefBookCol(u'Ед.изм.', ['unit_id'], 'rbUnit', 10, showFields=2, isRTF=True)
            ], 'rbContainerType', [rbCode, rbName])
        self.setWindowTitleEx(u'Типы контейнеров')

    def getItemEditor(self):
        return CRBContainerTypeEditor(self)


class CRBContainerTypeEditor(CItemEditorBaseDialog, Ui_RBContainerTypeEditor):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rbContainerType')
        self.setupUi(self)
        self.cmbUnit.setTable('rbUnit', addNone=True)
        self.cmbUnit.setRTF(True)

        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Тип контейнера')
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(     self.edtCode,   record, rbCode)
        setLineEditValue(     self.edtName,   record, rbName)
        self.cmbColor.setColor(forceString(record.value('color')))
        setDoubleBoxValue(self.edtAmount, record, 'amount')
        setRBComboBoxValue(   self.cmbUnit,   record, 'unit_id')

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(  self.edtCode,                      record, rbCode)
        getLineEditValue(  self.edtName,                      record, rbName)
        record.setValue('color', QtCore.QVariant(self.cmbColor.colorName()))
        getDoubleBoxValue(self.edtAmount, record, 'amount')
        getRBComboBoxValue(   self.cmbUnit,   record, 'unit_id')

        return record



