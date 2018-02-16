# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore

from library.Utils import forceString, forceStringEx, toVariant

from library.TableModel                  import CTextCol
from library.ItemsListDialog             import CItemEditorBaseDialog, CItemsListDialogEx
from library.interchange                 import setLineEditValue, getTextEditValue, setTextEditValue, getCheckBoxValue, setCheckBoxValue

from Reports.ReportsConstructor.Ui_FunctionEditorDialog import Ui_FunctionDialog


class CRCFunctionList(CItemsListDialogEx):
    def __init__(self, parent):
        CItemsListDialogEx.__init__(self, parent,
            [
            CTextCol(u'Наименование', ['name'], 50),
            CTextCol(u'Функция',     ['function'], 10),
            CTextCol(u'Описание',          ['description'], 10),
            ], 'rcFunction', ['name'], uniqueCode=False)
        self.setWindowTitleEx(u'Список функций')

    def getItemEditor(self):
        return CRCFunctionEditor(self)

class CRCFunctionEditor(CItemEditorBaseDialog, Ui_FunctionDialog):
    def __init__(self, parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rcFunction')
        self.preSetupUi()
        self.setupUi(self)
        self.postSetupUi()
        self.setWindowTitleEx(u'Редактирование функции')

    def preSetupUi(self):
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMaximizeButtonHint)

    def postSetupUi(self):
        pass

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(self.edtName, record, 'name')
        setLineEditValue(self.edtFunction, record, 'function')
        setTextEditValue(self.edtDescription, record, 'description')
        setCheckBoxValue(self.chkHasSpace, record, 'hasSpace')

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getCheckBoxValue(self.chkHasSpace, record, 'hasSpace')
        addSpace = u' ' if self.chkHasSpace.isChecked() else u''
        record.setValue('name', toVariant(u'%s%s' % (forceString(self.edtName.text()).strip(), addSpace)))
        record.setValue('function', toVariant(u'%s%s' % (forceString(self.edtFunction.text()).strip(), addSpace)))
        getTextEditValue(self.edtDescription, record, 'description')
        return record

    def saveInternals(self, id):
        pass

    def checkDataEntered(self):
        result = True
        name = forceStringEx(self.edtName.text())
        function = forceStringEx(self.edtFunction.text())
        description = forceStringEx(self.edtDescription.toPlainText())
        result = result \
                 and (name or self.checkInputMessage(u'наименование', False, self.edtName))\
                 and (function or self.checkInputMessage(u'функция', False, self.edtFunction))\
                 and (description or self.checkInputMessage(u'описание', False, self.edtDescription))
        return result


    def on_edtName_textEdited(self, text):
        self.edtName.setText(forceString(text).upper())

    def on_edtFunction_textEdited(self, text):
        self.edtFunction.setText(forceString(text).upper())