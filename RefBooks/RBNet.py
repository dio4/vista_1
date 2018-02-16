# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from library.Utils              import forceString, forceStringEx, toVariant
from library.interchange        import getCheckBoxValue, setCheckBoxValue, getComboBoxValue, getLineEditValue, \
                                       setComboBoxValue, setLineEditValue
from library.TableModel         import CBoolCol, CEnumCol, CTextCol
from library.ItemsListDialog    import CItemsListDialog, CItemEditorBaseDialog
from library.AgeSelector        import composeAgeSelector, parseAgeSelector

from RefBooks.Tables            import rbCode, rbName, rbNet

from Ui_RBNetEditor             import Ui_RBNetEditorDialog


SexList = ['', u'М', u'Ж']


class CRBNetList(CItemsListDialog):
    def __init__(self, parent):
        flagsCol = CBoolCol(u'Ограничения',  ['flags'], 7)
        flagsCol.setToolTip(u'Применять ограничения при регистрации пациента')
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 18),
            CTextCol(u'Наименование', [rbName], 35),
            CEnumCol(u'Пол',          ['sex'], SexList, 10),
            CTextCol(u'Возраст',      ['age'], 10),
            flagsCol,
            ], rbNet, [rbCode, rbName])
        self.setWindowTitleEx(u'Сети')


    def getItemEditor(self):
        return CRBNetEditor(self)


class CRBNetEditor(CItemEditorBaseDialog, Ui_RBNetEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rbNet')
        self.setupUi(self)
        self.setWindowTitleEx(u'Сеть')


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(   self.edtCode,           record, 'code')
        setLineEditValue(   self.edtName,           record, 'name')
        setComboBoxValue(   self.cmbSex,            record, 'sex')
        (begUnit, begCount, endUnit, endCount) = parseAgeSelector(forceString(record.value('age')))
        self.cmbBegAgeUnit.setCurrentIndex(begUnit)
        self.edtBegAgeCount.setText(str(begCount))
        self.cmbEndAgeUnit.setCurrentIndex(endUnit)
        self.edtEndAgeCount.setText(str(endCount))
        # Полю flags можно сделать битовым и хранить в нем несколько разных состояний. Пока там одно, поэтому работаем
        # как с обычным полем со значениями 0-1
        setCheckBoxValue(  self.chkUseInCreateClients, record, 'flags')

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(   self.edtCode,           record, 'code')
        getLineEditValue(   self.edtName,           record, 'name')
        getComboBoxValue(   self.cmbSex,            record, 'sex')
        record.setValue('age',        toVariant(composeAgeSelector(
                    self.cmbBegAgeUnit.currentIndex(),  forceStringEx(self.edtBegAgeCount.text()),
                    self.cmbEndAgeUnit.currentIndex(),  forceStringEx(self.edtEndAgeCount.text())
                        )))
        getCheckBoxValue(  self.chkUseInCreateClients, record, 'flags')
        return record
