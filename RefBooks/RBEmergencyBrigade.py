# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore

from library.InDocTable         import CInDocTableModel, CRBInDocTableCol
from library.ItemsListDialog    import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel         import CTextCol
from library.Utils              import forceString, forceStringEx, toVariant

from RefBooks.Tables            import rbCode, rbName, rbCodeRegional, rbEmergencyBrigade

from Ui_RBEmergencyBrigade      import Ui_ItemEditorDialog


class CRBEmergencyBrigadeList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            CTextCol(u'Региональный код', [rbCodeRegional], 20),
            ], rbEmergencyBrigade, [rbCode, rbName])
        self.setWindowTitleEx(u'Бригады')

    def getItemEditor(self):
        return CRBEmergencyBrigadeEditor(self)


class CRBEmergencyBrigadeEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, rbEmergencyBrigade)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Бригада')
        self.setupDirtyCather()
        self.addModels('PersonnelBrigade',  CPersonnelBrigadeModel(self))
        self.setModels(self.tblPersonnelBrigade, self.modelPersonnelBrigade, self.selectionModelPersonnelBrigade)
        self.tblPersonnelBrigade.addMoveRow()
        self.tblPersonnelBrigade.popupMenu().addSeparator()
        self.tblPersonnelBrigade.addPopupDelRow()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        self.edtCode.setText(forceString(record.value(rbCode)))
        self.edtName.setText(forceString(record.value(rbName)))
        self.modelPersonnelBrigade.loadItems(self.itemId())


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue(rbCode,       toVariant(forceStringEx(self.edtCode.text())))
        record.setValue(rbName,       toVariant(forceStringEx(self.edtName.text())))
        return record


    def saveInternals(self, id):
        self.modelPersonnelBrigade.saveItems(id)


class CPersonnelBrigadeModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'EmergencyBrigade_Personnel', 'id', 'master_id', parent)
        self.addCol(CRBInDocTableCol(u'ФИО', 'person_id', 10, 'vrbPersonWithSpeciality', order = 'name', prefferedWidth=150))