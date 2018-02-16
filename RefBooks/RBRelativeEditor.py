# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore

from library.interchange        import getCheckBoxValue, getComboBoxValue, getLineEditValue, setCheckBoxValue, \
                                       setComboBoxValue, setLineEditValue
from library.ItemsListDialog    import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel         import CTextCol
from library.Utils              import forceStringEx

from RefBooks.Tables            import rbCode, rbRelationType

from Ui_RBRelative              import Ui_ItemEditorDialog


class CRBRelativeList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',              [rbCode], 20),
            CTextCol(u'Региональный код', ['regionalCode'], 20),
            CTextCol(u'Субъект',          ['leftName'], 40),
            CTextCol(u'Объект',           ['rightName'], 40),
            ], rbRelationType, [rbCode, 'regionalCode', 'leftName', 'rightName', ])
        self.setWindowTitleEx(u'Типы связей пациента')

    def getItemEditor(self):
        return CRBRelativeEditor(self)

#
# ##########################################################################
#

class CRBRelativeEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, rbRelationType)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Тип связи пациента')
        self.setupDirtyCather()


    def checkDataEntered(self):
        result = True
        result = result and (forceStringEx(self.edtCode.text()) or self.checkInputMessage(u'код', False, self.edtCode))
        result = result and (forceStringEx(self.edtLeftName.text()) or self.checkInputMessage(u'субъекта отношения', False, self.edtLeftName))
        result = result and (forceStringEx(self.edtRightName.text()) or self.checkInputMessage(u'объекта отношения', False, self.edtRightName))
        return result


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(self.edtCode,         record, 'code')
        setLineEditValue(self.edtRegionalCode, record, 'regionalCode')
        setLineEditValue(self.edtRegionalReverseCode, record, 'regionalReverseCode')
        setLineEditValue(self.edtLeftName,     record, 'leftName')
        setLineEditValue(self.edtRightName,    record, 'rightName')
        setCheckBoxValue(self.chkDirectGeneticRelation,          record, 'isDirectGenetic')
        setCheckBoxValue(self.chkBackwardGeneticRelation,        record, 'isBackwardGenetic')
        setCheckBoxValue(self.chkDirectRepresentativeRelation,   record, 'isDirectRepresentative')
        setCheckBoxValue(self.chkBackwardRepresentativeRelation, record, 'isBackwardRepresentative')
        setCheckBoxValue(self.chkDirectEpidemicRelation,         record, 'isDirectEpidemic')
        setCheckBoxValue(self.chkBackwardEpidemicRelation,       record, 'isBackwardEpidemic')
        setCheckBoxValue(self.chkDirectDonationRelation,         record, 'isDirectDonation')
        setCheckBoxValue(self.chkBackwardDonationRelation,       record, 'isBackwardDonation')
        setComboBoxValue(self.cmbLeftSex, record, 'leftSex')
        setComboBoxValue(self.cmbRightSex, record, 'rightSex')


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(self.edtCode,         record, 'code')
        getLineEditValue(self.edtRegionalCode, record, 'regionalCode')
        getLineEditValue(self.edtRegionalReverseCode, record, 'regionalReverseCode')
        getLineEditValue(self.edtLeftName,     record, 'leftName')
        getLineEditValue(self.edtRightName,    record, 'rightName')
        getCheckBoxValue(self.chkDirectGeneticRelation,          record, 'isDirectGenetic')
        getCheckBoxValue(self.chkBackwardGeneticRelation,        record, 'isBackwardGenetic')
        getCheckBoxValue(self.chkDirectRepresentativeRelation,   record, 'isDirectRepresentative')
        getCheckBoxValue(self.chkBackwardRepresentativeRelation, record, 'isBackwardRepresentative')
        getCheckBoxValue(self.chkDirectEpidemicRelation,         record, 'isDirectEpidemic')
        getCheckBoxValue(self.chkBackwardEpidemicRelation,       record, 'isBackwardEpidemic')
        getCheckBoxValue(self.chkDirectDonationRelation,         record, 'isDirectDonation')
        getCheckBoxValue(self.chkBackwardDonationRelation,       record, 'isBackwardDonation')
        getComboBoxValue(self.cmbLeftSex, record, 'leftSex')
        getComboBoxValue(self.cmbRightSex, record, 'rightSex')
        return record
