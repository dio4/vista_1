# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore

from library.interchange        import getCheckBoxValue, getCheckBoxUniqueValue, getComboBoxValue, getLineEditValue, getRBComboBoxValue, setCheckBoxValue, setComboBoxValue, \
                                       setLineEditValue, setRBComboBoxValue
from library.ItemsListDialog    import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel         import CRefBookCol, CTextCol

from RefBooks.Tables            import rbCode, rbName, rbDocumentType, rbDocumentTypeGroup

from Ui_RBDocumentTypeEditor import Ui_ItemEditorDialog


class CRBDocumentTypeList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(    u'Код',              [rbCode], 20),
            CTextCol(    u'Федеральный код',  ['federalCode'], 20),
            CTextCol(    u'Региональный код', ['regionalCode'], 20),
            CTextCol(    u'Наименование',     [rbName], 40),
            CRefBookCol( u'Группа документов',       ['group_id'], rbDocumentTypeGroup, 30),

            ], rbDocumentType, [rbCode, rbName])
        self.setWindowTitleEx(u'Типы документов')

    def getItemEditor(self):
        return CRBDocumentTypeEditor(self)

#
# ##########################################################################
#

class CRBDocumentTypeEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, rbDocumentType)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Тип документа')
        self.cmbGroup.setTable(rbDocumentTypeGroup, False)
        self.edtCode.setFocus(QtCore.Qt.OtherFocusReason)
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(   self.edtCode,           record, 'code')
        setLineEditValue(   self.edtFederalCode,    record, 'federalCode')
        setLineEditValue(   self.edtRegionalCode,   record, 'regionalCode')
        setLineEditValue(   self.edtName,           record, 'name')
        setRBComboBoxValue( self.cmbGroup,          record, 'group_id')
        setComboBoxValue(   self.cmbSerialFormat,   record, 'serial_format')
        setCheckBoxValue(   self.chkDefault,        record, 'isDefault')
        setCheckBoxValue(   self.chkForeigner,      record, 'isForeigner')
        self.setIsDirty(False)


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(   self.edtCode,           record, 'code')
        getLineEditValue(   self.edtFederalCode,    record, 'federalCode')
        getLineEditValue(   self.edtRegionalCode,   record, 'regionalCode')
        getLineEditValue(   self.edtName,           record, 'name')
        getRBComboBoxValue( self.cmbGroup,          record, 'group_id')
        getComboBoxValue(   self.cmbSerialFormat,   record, 'serial_format')
        getCheckBoxUniqueValue(   self.chkDefault,  record, rbDocumentType, 'isDefault')
        getCheckBoxValue(   self.chkForeigner,      record, 'isForeigner')
        return record
