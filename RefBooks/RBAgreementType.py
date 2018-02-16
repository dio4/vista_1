# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore

from library.interchange        import getComboBoxValue, getLineEditValue, setComboBoxValue, setLineEditValue
from library.ItemsListDialog    import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel         import CEnumCol, CTextCol

from RefBooks.Tables            import rbCode, rbName

from Ui_RBAgreementTypeEditor   import Ui_RBAgreementTypeEditor


class CRBAgreementTypeList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            CEnumCol(u'Модификатор статуса', ['quotaStatusModifier'], 
                                             [u'Не меняет', 
                                              u'Отменено', 
                                              u'Ожидание', 
                                              u'Активный талон', 
                                              u'Талон для заполнения', 
                                              u'Заблокированный талон',
                                              u'Отказано',
                                              u'Необходимо согласовать дату обслуживания',
                                              u'Дата обслуживания на согласовании', 
                                              u'Дата обслуживания согласована', 
                                              u'Пролечен', 
                                              u'Обслуживание отложено', 
                                              u'Отказ пациента', 
                                              u'Импортировано из ВТМП'], 40)
            ], 'rbAgreementType', [rbCode, rbName])
        self.setWindowTitleEx(u'Типы согласования')
        
    def getItemEditor(self):
        return CRBAgreementTypeEditor(self)
        
class CRBAgreementTypeEditor(CItemEditorBaseDialog, Ui_RBAgreementTypeEditor):
    def __init__(self, parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rbAgreementType')
        self.setupUi(self)
        self.setWindowTitleEx(u'Тип согласования')
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        
    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(self.edtCode,                record, 'code' )
        setLineEditValue(self.edtName,                record, 'name' )
        setComboBoxValue(self.cmbQuotaStatusModifier, record, 'quotaStatusModifier')
        
    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(self.edtCode,                record, 'code' )
        getLineEditValue(self.edtName,                record, 'name' )
        getComboBoxValue(self.cmbQuotaStatusModifier, record, 'quotaStatusModifier')
        return record
        