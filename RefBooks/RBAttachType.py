# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from library.interchange import *
from library.TableModel import *
from library.ItemsListDialog import CItemsListDialog, CItemEditorBaseDialog

from RefBooks.Tables import *
from Ui_RBAttachTypeEditor import Ui_ItemEditorDialog


class CRBAttachTypeList(CItemsListDialog):
    def __init__(self, parent):
        groupCol = CIntCol(u'Группа',       ['grp'], 7)
        groupCol.setToolTip(u'Прикрепления с одинаковым номером группы являются взаимоисключающими. При создании нового '
                            u'прикрепления предыдущие действующие прикрепления автоматически открепляются с датой открепления, равной дате нового прикрепления.')
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',                     [rbCode], 10),
            CTextCol(u'Наименование',            [rbName], 30),
            CBoolCol(u'Временно',                ['temporary'], 7),
            CBoolCol(u'Выбытие',                 ['outcome'],   6),
            groupCol,
            CRefBookCol(u'Источник финансирования', ['finance_id'], rbFinance, 30),
            ], rbAttachType, [rbCode, rbName])
        self.setWindowTitleEx(u'Типы прикрепления')

    def getItemEditor(self):
        return CRBAttachTypeEditor(self)
#
# ##########################################################################
#

class CRBAttachTypeEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, rbAttachType)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Тип прикрепления')
        self.cmbFinance.setTable(rbFinance, False)
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(   self.edtCode,          record, 'code')
        setLineEditValue(   self.edtName,          record, 'name')
        setCheckBoxValue(   self.checkBox,         record, 'temporary')
        setCheckBoxValue(   self.chkOutcome,       record, 'outcome')
        setRBComboBoxValue( self.cmbFinance,       record, 'finance_id')
        setSpinBoxValue(    self.edtGroup,         record, 'grp')



    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(   self.edtCode,          record, 'code')
        getLineEditValue(   self.edtName,          record, 'name')
        getCheckBoxValue(   self.checkBox,         record, 'temporary')
        getCheckBoxValue(   self.chkOutcome,       record, 'outcome')
        getRBComboBoxValue( self.cmbFinance,       record, 'finance_id')
        getSpinBoxValue(    self.edtGroup,         record, 'grp')
        return record

    def checkDataEntered(self):
        result = True
        financeId = forceInt(self.cmbFinance.value())
        result = result and (financeId or self.checkInputMessage(u'источник финансирования', False, self.cmbFinance))
        return result and super(CRBAttachTypeEditor, self).checkDataEntered()
