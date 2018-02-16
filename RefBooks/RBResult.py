# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore
from PyQt4 import QtGui

from library.ItemsListDialog    import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel         import CBoolCol, CDateCol, CRefBookCol, CTextCol
from library.Utils              import forceBool, forceDate, forceInt, forceRef, forceString, forceStringEx, toVariant

from RefBooks.Tables            import rbCode, rbName, rbEventTypePurpose, rbResult

from Ui_RBResultEditor          import Ui_ItemEditorDialog


class CRBResultList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CRefBookCol(u'Цель визита', ['eventPurpose_id'], rbEventTypePurpose, 30),
            CTextCol(   u'Код',         [rbCode], 10),
            CTextCol(   u'Региональный код', ['regionalCode'], 10),
            CTextCol(   u'Наименование',[rbName], 30),
            CBoolCol(   u'Не закончен', ['continued'], 10),
            CBoolCol(   u'Признак смерти', ['isDeath'], 10),
            CTextCol(   u'Федеральный код', ['federalCode'], 10),
            CBoolCol(   u'Не выставлять счет', ['notAccount'], 10),
            CDateCol(   u'Дата начала', ['begDate'], 10),
            CDateCol(   u'Дата окончания', ['endDate'], 10),
            ], rbResult, ['eventPurpose_id', rbCode, rbName])
        self.setWindowTitleEx(u'Результаты обращения')

    def getItemEditor(self):
        return CRBResultEditor(self)
#
# ##########################################################################
#

class CRBResultEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, rbResult)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Результат обращения')
        self.cmbCounter.setTable('rbCounter', True)
        self.cmbAttachType.setTable('rbAttachType', True)
        self.cmbSocStatusClass.setTable('rbSocStatusClass', True)
        self.cmbSocStatusType.setTable('rbSocStatusType', True)
        self.cmbEventPurpose.setTable(rbEventTypePurpose, False)
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        self.cmbEventPurpose.setValue(forceInt(record.value('eventPurpose_id')))
        self.edtCode.setText(forceString(record.value(rbCode)))
        self.edtRegionalCode.setText(forceString(record.value('regionalCode')))
        self.edtName.setText(forceString(record.value(rbName)))
        self.chkContinued.setChecked(forceBool(record.value('continued')))
        self.chkIsDeath.setChecked(forceBool(record.value('isDeath')))
        self.edtFederalCode.setText(forceString(record.value('federalCode')))
        self.chkNotAccount.setChecked(forceBool(record.value('notAccount')))
        self.cmbCounter.setValue(forceRef(record.value('counter_id')))
        self.edtBegDate.setDate(forceDate(record.value('begDate')))
        self.edtEndDate.setDate(forceDate(record.value('endDate')))
        self.cmbAttachType.setValue(forceRef(record.value('attachType')))
        self.cmbSocStatusClass.setValue(forceRef(record.value('socStatusClass')))
        self.cmbSocStatusType.setValue(forceRef(record.value('socStatusType')))


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue('eventPurpose_id', toVariant(self.cmbEventPurpose.value()))
        record.setValue(rbCode,       toVariant(forceStringEx(self.edtCode.text())))
        record.setValue('regionalCode', toVariant(forceStringEx(self.edtRegionalCode.text())))
        record.setValue(rbName,       toVariant(forceStringEx(self.edtName.text())))
        record.setValue('continued',  toVariant(self.chkContinued.isChecked()))
        record.setValue('isDeath', toVariant(self.chkIsDeath.isChecked()))
        record.setValue('federalCode', toVariant(forceStringEx(self.edtFederalCode.text())))
        record.setValue('notAccount', toVariant(self.chkNotAccount.isChecked()))
        record.setValue('counter_id', toVariant(self.cmbCounter.value()))
        record.setValue('begDate', toVariant(self.edtBegDate.date()))
        record.setValue('endDate', toVariant(self.edtEndDate.date()))
        record.setValue('attachType', toVariant(self.cmbAttachType.value()))
        record.setValue('socStatusClass', toVariant(self.cmbSocStatusClass.value()))
        record.setValue('socStatusType', toVariant(self.cmbSocStatusType.value()))
        return record

    @QtCore.pyqtSlot(int)
    def on_cmbSocStatusClass_currentIndexChanged(self, index):
        socStatusClassId = self.cmbSocStatusClass.value()
        typesList = QtGui.qApp.db.getIdList('rbSocStatusClassTypeAssoc', idCol='type_id', where='class_id = %d' % forceInt(socStatusClassId))
        if typesList:
            filter = ('id IN (%s)' % u','.join(forceString(socStatusType) for socStatusType in typesList))
            self.cmbSocStatusType.setFilter(filter)
