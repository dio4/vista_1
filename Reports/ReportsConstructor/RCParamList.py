# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

from library.Utils import forceString, forceBool, forceStringEx, toVariant

from library.TableModel                  import CTextCol
from library.ItemsListDialog             import CItemEditorBaseDialog, CItemsListDialogEx
from library.interchange                 import setLineEditValue, getLineEditValue, getRBComboBoxValue, setRBComboBoxValue

from Reports.ReportsConstructor.models.RCTableModel import CRCParamValueModel

from Reports.ReportsConstructor.Ui_ParamEditorDialog import Ui_ParamDialog


class CRCParamList(CItemsListDialogEx):
    def __init__(self, parent):
        CItemsListDialogEx.__init__(self, parent,
            [
            CTextCol(u'Код', ['code'], 50),
            CTextCol(u'Имя в списке параметров',     ['name'], 10),
            CTextCol(u'Текст в интерфейсе',          ['title'], 10),
            ], 'rcParam', ['name'], uniqueCode=False)
        self.setWindowTitleEx(u'Список параметров')

    def getItemEditor(self):
        return CRCParamEditor(self)

class CRCParamEditor(CItemEditorBaseDialog, Ui_ParamDialog):
    def __init__(self, parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rcParam')
        self.preSetupUi()
        self.setupUi(self)
        self.postSetupUi()
        self.setWindowTitleEx(u'Редактирование параметра')

    def preSetupUi(self):
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMaximizeButtonHint)
        self.addModels('CmbValue', CRCParamValueModel(self))

    def postSetupUi(self):
        self.cmbValueType.setTable('rcValueType')
        self.cmbParamType.setTable('rcParamType')
        self.setModels(self.tblCmbValue, self.modelCmbValue, self.selectionModelCmbValue)
        self.setAllGroupVisible(False)

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(self.edtName, record, 'name')
        setLineEditValue(self.edtCode, record, 'code')
        setLineEditValue(self.edtText, record, 'title')
        setLineEditValue(self.edtRbTableName, record, 'tableName')
        setRBComboBoxValue(self.cmbValueType, record, 'valueType_id')
        setRBComboBoxValue(self.cmbParamType, record, 'type_id')
        self.modelCmbValue.loadItems(self.itemId())

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(self.edtName, record, 'name')
        getLineEditValue(self.edtCode, record, 'code')
        getLineEditValue(self.edtText, record, 'title')
        if self.edtRbTableName.isVisible():
            getLineEditValue(self.edtRbTableName, record, 'tableName')
        else:
            record.setValue('tableName', toVariant(u''))
        getRBComboBoxValue(self.cmbValueType, record, 'valueType_id')
        getRBComboBoxValue(self.cmbParamType, record, 'type_id')
        return record

    def saveInternals(self, id):
        self.modelCmbValue.saveItems(id)

    def checkDataEntered(self):
        result = True
        name = forceStringEx(self.edtName.text())
        code = forceStringEx(self.edtCode.text())
        text = forceStringEx(self.edtText.text())
        isAvailableTable = False
        try:
            if self.edtRbTableName.isVisible() and forceString(self.edtRbTableName.text()):
                isAvailableTable = forceBool(QtGui.qApp.db.table(forceString(self.edtRbTableName.text())))
            else:
                isAvailableTable = True
        except Exception:
            pass
        result = result \
                 and (name or self.checkInputMessage(u'наименование', False, self.edtName))\
                 and (code or self.checkInputMessage(u'код', False, self.edtCode))\
                 and (text or self.checkInputMessage(u'имя в интрефейсе', False, self.edtText))\
                 and (isAvailableTable or self.checkValueMessage(u'Таблица с таким именем не существует.', False, self.edtRbTableName))
        return result

    def setAllGroupVisible(self, value):
        self.groupCmb.setVisible(value)
        self.groupRb.setVisible(value)

    def on_cmbParamType_currentIndexChanged(self, value):
        index = self.cmbParamType._model.searchId(self.cmbParamType.value())
        code = self.cmbParamType._model.getCode(index)
        self.cmbValueType.setEnabled(True)
        self.setAllGroupVisible(False)
        if code in ['cmb', 'list', 'mixCmb']:
            self.groupRb.setVisible(True)
        elif code in ['customCmb']:
            self.groupCmb.setVisible(True)
            self.cmbValueType.setCode('unicode')
            self.cmbValueType.setEnabled(False)

    def on_edtName_textEdited(self, text):
        self.edtName.setText(text.replace(' ', '_'))