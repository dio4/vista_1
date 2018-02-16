# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore

from library.interchange        import getComboBoxValue, getLineEditValue, setComboBoxValue, setLineEditValue
from library.ItemsListDialog    import CItemsListDialog,  CItemEditorBaseDialog
from library.TableModel         import CEnumCol, CTextCol

from RefBooks.Tables            import rbCode, rbName, rbTempInvalidExtraReason, TempInvalidTypeList

from Ui_RBTempInvalidExtraReasonEditor import Ui_ItemEditorDialog


class CRBTempInvalidExtraReasonList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CEnumCol(u'Класс',                   ['type'], TempInvalidTypeList, 10),
            CTextCol(u'Код',                     [rbCode], 10),
            CTextCol(u'Наименование',            [rbName], 30),
            ], rbTempInvalidExtraReason, ['type', rbCode, rbName])
        self.setWindowTitleEx(u'Дополнительные причины ВУТ, инвалидности или ограничения жизнедеятельности')

    def getItemEditor(self):
        return CRBTempInvalidExtraReasonEditor(self)
#
# ##########################################################################
#

class CRBTempInvalidExtraReasonEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, rbTempInvalidExtraReason)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Дополнительная причина ВУТ, инвалидности или ограничения жизнедеятельности')
        self.cmbType.addItems(TempInvalidTypeList)
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setComboBoxValue(self.cmbType, record, 'type')
        setLineEditValue(self.edtCode, record, 'code')
        setLineEditValue(self.edtName, record, 'name')


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getComboBoxValue(self.cmbType, record, 'type')
        getLineEditValue(self.edtCode, record, 'code')
        getLineEditValue(self.edtName, record, 'name')
        return record
