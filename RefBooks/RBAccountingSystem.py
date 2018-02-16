# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from library.crbcombobox        import CRBComboBox
from library.interchange        import getCheckBoxValue, getLineEditValue, getRBComboBoxValue, setCheckBoxValue, \
                                       setLineEditValue, setRBComboBoxValue
from library.ItemsListDialog    import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel         import CBoolCol, CTextCol, CRefBookCol

from RefBooks.Tables            import rbAccountingSystem, rbCode, rbName

from Ui_RBAccountingSystemEditor import Ui_ItemEditorDialog

class CRBAccountingSystemList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 10),
            CTextCol(u'Наименование', [rbName], 50),
            CBoolCol( u'Разрешать изменение',         ['isEditable'], 20),
            CBoolCol( u'Отображать в информации о пациенте',         ['showInClientInfo'], 15),
            CBoolCol( u'Требует ввода уникального значения',         ['isUnique'], 15),
            CBoolCol( u'Автоматическое добавление идентификатора',   ['autoIdentificator'], 20),
            CRefBookCol( u'Счетчик',                                 ['counter_id'], 'rbCounter', 20, CRBComboBox.showCodeAndName)
            ], rbAccountingSystem, [rbCode, rbName])
        self.setWindowTitleEx(u'Внешние учётные системы')

    def getItemEditor(self):
        return CRBAccountingSystemEditor(self)

class CRBAccountingSystemEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, rbAccountingSystem)
        self.setupUi(self)
        self.setWindowTitleEx(u'')
        self.cmbCounter.setTable('rbCounter')
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(self.edtCode,             record, 'code')
        setLineEditValue(self.edtName,             record, 'name')
        setCheckBoxValue(self.chkEditable,         record, 'isEditable')
        setCheckBoxValue(self.chkShowInClientInfo, record, 'showInClientInfo')
        setCheckBoxValue(self.chkIsUnique,         record, 'isUnique')
        setCheckBoxValue(self.chkAutoIdentificator, record, 'autoIdentificator')
        setRBComboBoxValue(self.cmbCounter,        record, 'counter_id')


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(self.edtCode,             record, 'code')
        getLineEditValue(self.edtName,             record, 'name')
        getCheckBoxValue(self.chkEditable,         record, 'isEditable')
        getCheckBoxValue(self.chkShowInClientInfo, record, 'showInClientInfo')
        getCheckBoxValue(self.chkIsUnique,         record, 'isUnique')
        getCheckBoxValue(self.chkAutoIdentificator, record, 'autoIdentificator')
        getRBComboBoxValue(self.cmbCounter,        record, 'counter_id')
        return record
