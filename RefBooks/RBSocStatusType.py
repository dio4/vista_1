# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore

from library.interchange import getLineEditValue, getRBComboBoxValue, setLineEditValue, setRBComboBoxValue
from library.ItemsListDialog import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel import CRefBookCol, CTextCol

from RefBooks.Tables import rbCode, rbName, rbSocStatusType

from Ui_RBSocStatusTypeItemEditor import Ui_SocStatusTypeItemEditorDialog


class CRBSocStatusTypeList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            CTextCol(u'Региональный код', ['regionalCode'], 20),
            CRefBookCol(u'Тип документа',['documentType_id'], 'rbDocumentType', 20)
            ], rbSocStatusType, [rbCode, rbName])
        self.setWindowTitleEx(u'Типы социального статуса')

    def getItemEditor(self):
        return CRBSocStatusTypeEditor(self)


class CRBSocStatusTypeEditor(CItemEditorBaseDialog,  Ui_SocStatusTypeItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, rbSocStatusType)
        self.setupUi(self)
        self.setWindowTitleEx(u'Тип социального статуса')
        self.setupDirtyCather()
        self.cmbDocumentType.setTable('rbDocumentType')


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(self.edtCode, record, 'code')
        setLineEditValue(self.edtName, record, 'name')
        setLineEditValue( self.edtRegionalCode, record, 'regionalCode')
        setRBComboBoxValue(self.cmbDocumentType, record, 'documentType_id')
        self.setIsDirty(False)


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue( self.edtCode,     record, 'code')
        getLineEditValue( self.edtName,     record, 'name')
        getLineEditValue( self.edtRegionalCode,     record, 'regionalCode')
        getRBComboBoxValue(self.cmbDocumentType, record, 'documentType_id')
        return record


    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtCode_textEdited(self, text):
        self.setIsDirty()


    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtName_textEdited(self, text):
        self.setIsDirty()


    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtRegionalCode_textEdited(self, text):
        self.setIsDirty()
