# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore

from library.crbcombobox        import CRBComboBox
from library.interchange        import getRBComboBoxValue, getTextEditValue, setRBComboBoxValue, setTextEditValue
from library.ItemsListDialog    import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel         import CRefBookCol, CTextCol
from library.Utils              import forceRef, forceString

from RefBooks.Tables            import rbActionTypeIncompatibility

from Ui_RBActionTypeIncompatibilityEditor import Ui_ItemEditorDialog


class CRBActionTypeIncompatibilitiesList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CRefBookCol(    u'Код',              ['firstActionType_id'], 'ActionType', 30, CRBComboBox.showCodeAndName),
            CRefBookCol(    u'Код',              ['secondActionType_id'], 'ActionType', 30, CRBComboBox.showCodeAndName),
            CTextCol(       u'Последствия',     ['reason'], 40),
            ], rbActionTypeIncompatibility, [])
        self.setWindowTitleEx(u'Совместимость типов действий')

    def getItemEditor(self):
        return CRBActionTypeIncompatibilitiesEditor(self)

#
# ##########################################################################
#

class CRBActionTypeIncompatibilitiesEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, rbActionTypeIncompatibility)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Совместимость типов действий')
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setRBComboBoxValue(   self.cmbFirstActionType,   record, 'firstActionType_id')
        setRBComboBoxValue(   self.cmbSecondActionType,  record, 'secondActionType_id')
        setTextEditValue(   self.edtReason,            record, 'reason')
        self.setIsDirty(False)


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getRBComboBoxValue(   self.cmbFirstActionType,   record, 'firstActionType_id')
        getRBComboBoxValue(   self.cmbSecondActionType,  record, 'secondActionType_id')
        getTextEditValue(   self.edtReason,            record, 'reason')
        return record

    def checkDataEntered(self):
        result = True
        firstActionTypeId = forceRef(self.cmbFirstActionType.value())
        secondActionTypeId = forceRef(self.cmbSecondActionType.value())
        reason = forceString(self.edtReason.toPlainText())
        result = result and (firstActionTypeId or self.checkInputMessage(u'тип действия', False, self.cmbFirstActionType))
        result = result and (secondActionTypeId or self.checkInputMessage(u'тип действия', False, self.cmbSecondActionType))
        result = result and (reason or self.checkInputMessage(u'последствия', False, self.edtReason))
        return result