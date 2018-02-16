# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore

from library.interchange            import getLineEditValue, getRBComboBoxValue, setLineEditValue, setRBComboBoxValue
from library.ItemsListDialog        import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel             import CRefBookCol, CTextCol

from Ui_RBHospitalBedProfileEditor  import Ui_ItemEditorDialog


class CRBHospitalBedProfileList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          ['code'], 20),
            CTextCol(u'Региональный код', ['regionalCode'], 20),
            CTextCol(u'Региональный код ЕИС', ['eisCode'], 20),
            CTextCol(u'Наименование', ['name'], 40),
            CRefBookCol(u'Сервис ОМС',   ['service_id'], 'rbService', 10),
            ], 'rbHospitalBedProfile', ['code', 'regionalCode', 'name', 'id'])
        self.setWindowTitleEx(u'Профили коек')

    def getItemEditor(self):
        return CRBHospitalBedProfileEditor(self)


class CRBHospitalBedProfileEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rbHospitalBedProfile')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Профиль койки')
        self.cmbService.setTable('rbService', True)
        self.cmbService.setCurrentIndex(0)
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(   self.edtCode,               record, 'code')
        setLineEditValue(   self.edtRegionalCode,       record, 'regionalCode')
        setLineEditValue(   self.edtEISRegionalCode,    record, 'eisCode')
        setLineEditValue(   self.edtName,               record, 'name')
        setRBComboBoxValue( self.cmbService,            record, 'service_id')


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(   self.edtCode,           record, 'code')
        getLineEditValue(   self.edtRegionalCode,   record, 'regionalCode')
        getLineEditValue(   self.edtEISRegionalCode,   record, 'eisCode')
        getLineEditValue(   self.edtName,           record, 'name')
        getRBComboBoxValue( self.cmbService,        record, 'service_id')
        return record