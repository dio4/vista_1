# -*- coding: utf-8 -*-

from PyQt4 import QtCore

from library.ItemsListDialog import CItemEditorBaseDialog, CItemsListDialogEx
from library.TableModel import CTextCol
from library.Utils import forceString, forceStringEx, toVariant, forceBool
from RefBooks.Tables import rbCode, rbName
from Ui_RBDiet import Ui_RBDiet


class CRBDiet(CItemsListDialogEx):
    def __init__(self, parent):
        CItemsListDialogEx.__init__(self, parent, [
            CTextCol(u'Код', [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
        ], 'rbDiet', [rbCode, rbName])
        self.setWindowTitleEx(u'Столы питания')

    def getItemEditor(self):
        return CRBDietEditor(self)


class CRBDietEditor(CItemEditorBaseDialog, Ui_RBDiet):
    def __init__(self, parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rbDiet')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Стол питания')
        self.setupDirtyCather()

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        self.edtCode.setText(forceString(record.value(rbCode)))
        self.edtName.setText(forceString(record.value(rbName)))
        self.chkAllowMeals.setChecked(forceBool(record.value('allow_meals')))
        self.chkNoCourting.setChecked(forceBool(record.value('noCourtingAtReanimation')))

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue(rbCode, toVariant(forceStringEx(self.edtCode.text())))
        record.setValue(rbName, toVariant(forceStringEx(self.edtName.text())))
        record.setValue('allow_meals', toVariant(self.chkAllowMeals.isChecked()))
        record.setValue('noCourtingAtReanimation', toVariant(self.chkNoCourting.isChecked()))
        return record
