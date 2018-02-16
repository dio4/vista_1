# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore

from library.interchange            import getComboBoxValue, getLineEditValue, setComboBoxValue, setLineEditValue
from library.ItemsListDialog        import CItemsListDialog,  CItemEditorBaseDialog
from library.TableModel             import CEnumCol, CTextCol

from RefBooks.Tables                import rbCode, rbName, TempInvalidTypeList

from Ui_RBTempInvalidResultEditor   import Ui_ItemEditorDialog


class CRBTempInvalidResultList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CEnumCol(u'Класс',                   ['type'], TempInvalidTypeList, 10),
            CTextCol(u'Код',                     [rbCode], 10),
            CTextCol(u'Наименование',            [rbName], 30),
#            CBoolCol(u'Трудоспособен',           ['able'], 10),
#            CBoolCol(u'Случай закрыт',           ['closed'], 10),
            CEnumCol(u'Состояние',               ['closed'], [u'открыт', u'закрыт', u'продлён', u'передан'], 4),
            CEnumCol(u'Статус',                  ['status'], [u'', u'Направление на КЭК', u'Решение КЭК', u'Направление на МСЭ', u'Решение МСЭ', u'Госпитализация', u'Сан.кур.лечение'], 30),
            ], 'rbTempInvalidResult', ['type', rbCode, rbName])
        self.setWindowTitleEx(u'Результаты периода ВУТ, инвалидности или ограничения жизнедеятельности')

    def getItemEditor(self):
        return CRBTempInvalidResultEditor(self)
#
# ##########################################################################
#

class CRBTempInvalidResultEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rbTempInvalidResult')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Результат периода ВУТ, инвалидности или ограничения жизнедеятельности')
        self.cmbType.addItems(TempInvalidTypeList)


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setComboBoxValue(self.cmbType, record, 'type')
        setLineEditValue(self.edtCode, record, rbCode)
        setLineEditValue(self.edtName, record, rbName)
#        setCheckBoxValue(self.chkAble, record, 'able')
        setComboBoxValue(self.cmbClosed, record, 'closed')
        setComboBoxValue(self.cmbStatus,record, 'status')


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getComboBoxValue(self.cmbType, record, 'type')
        getLineEditValue(self.edtCode, record, rbCode)
        getLineEditValue(self.edtName, record, rbName)
#        getCheckBoxValue(self.chkAble, record, 'able')
        getComboBoxValue(self.cmbClosed, record, 'closed')
        getComboBoxValue(self.cmbStatus,record, 'status')
        return record
