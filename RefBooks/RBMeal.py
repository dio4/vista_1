# -*- coding: utf-8 -*-

from PyQt4 import QtCore

from library.ItemsListDialog    import CItemEditorBaseDialog, CItemsListDialogEx
from library.TableModel         import CTextCol
from library.Utils              import forceString, forceStringEx, toVariant

from RefBooks.Tables            import rbCode, rbName

from Ui_RBMealEditor                  import Ui_RBMealEditorDialog

# TODO: добавить в меню
class CRBMeal(CItemsListDialogEx):
    def __init__(self, parent):
        CItemsListDialogEx.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 100),
            CTextCol(u'Количество', ['amount'], 10),
            CTextCol(u'Единица измерения', ['unit'], 10),
            ], 'rbMeal', [rbCode, rbName, 'amount', 'unit'])
        self.setWindowTitleEx(u'Рацион')

    def getItemEditor(self):
        return CRBDietEditor(self)

#
# ##########################################################################
#

class CRBDietEditor(CItemEditorBaseDialog, Ui_RBMealEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rbMeal')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Пункт меню')
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        self.edtCode.setText(forceString(record.value(rbCode)))
        self.edtName.setText(forceString(record.value(rbName)))
        self.edtAmount.setText(forceString(record.value('amount')))
        self.edtUnit.setText(forceString(record.value('unit')))


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue(rbCode,       toVariant(forceStringEx(self.edtCode.text())))
        record.setValue(rbName,       toVariant(forceStringEx(self.edtName.text())))
        record.setValue('amount',     toVariant(forceStringEx(self.edtAmount.text())))
        record.setValue('unit',       toVariant(forceStringEx(self.edtUnit.text())))
        return record