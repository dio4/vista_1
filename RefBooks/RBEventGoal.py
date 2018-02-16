# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore
from library.Utils import forceStringEx, forceInt

from library.interchange        import getLineEditValue, getRBComboBoxValue, setLineEditValue, setRBComboBoxValue
from library.ItemsListDialog    import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel         import CRefBookCol, CTextCol, CIntCol

from RefBooks.Tables            import rbCode, rbName, rbEventGoal

from Ui_RBEventGoalEditor       import Ui_ItemEditorDialog


class CRBEventGoalList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',              [rbCode], 20),
            CTextCol(u'Региональный код', ['regionalCode'], 20),
            CTextCol(u'Наименование',     [rbName], 40),
            CTextCol(u'Федеральный код', ['federalCode'], 8),
            CRefBookCol(u'Назначение типа события', ['eventTypePurpose_id'], 'rbEventTypePurpose', 12),
            CIntCol(u'Кол-во посещений', ['visitCount'], 10)
            ], rbEventGoal, [rbCode, rbName])
        self.setWindowTitleEx(u'Цель события')

    def getItemEditor(self):
        return CRBEventGoalEditor(self)



class CRBEventGoalEditor( CItemEditorBaseDialog, Ui_ItemEditorDialog):
#    setupUi = Ui_ItemEditorDialog.setupUi
#    retranslateUi = Ui_ItemEditorDialog.retranslateUi

    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, rbEventGoal)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Цель события')
        self.cmbPurpose.setTable('rbEventTypePurpose', False)
        self.cmbPurpose.setCurrentIndex(0)
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(self.edtCode, record, 'code')
        setLineEditValue(self.edtRegionalCode, record, 'regionalCode')
        setLineEditValue(self.edtFederalCode, record, 'federalCode')
        setLineEditValue(self.edtName, record, 'name')
        setRBComboBoxValue(self.cmbPurpose, record, 'eventTypePurpose_id')
        setLineEditValue(self.edtVisitCount, record, 'visitCount')


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(self.edtCode, record, 'code')
        getLineEditValue(self.edtRegionalCode, record, 'regionalCode')
        getLineEditValue(self.edtFederalCode, record, 'federalCode')
        getLineEditValue(self.edtName, record, 'name')
        getRBComboBoxValue(self.cmbPurpose, record, 'eventTypePurpose_id')

        leftCount, rightCount = forceStringEx(self.edtVisitCount.text()).split(u'-')
        leftCount = leftCount.strip()
        rightCount = rightCount.strip()
        if leftCount and rightCount:
            if forceInt(leftCount) > forceInt(rightCount):
                leftCount, rightCount = rightCount, leftCount
        record.setValue('visitCount', QtCore.QVariant(leftCount + u'-' + rightCount if leftCount or rightCount else u''))
        return record
