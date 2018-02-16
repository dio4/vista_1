# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore
from PyQt4 import QtGui

from library.ItemsListDialog        import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel             import CRefBookCol, CTextCol, CDateCol
from library.Utils                  import forceInt, forceRef, forceString, forceStringEx, toVariant, forceDate, \
    forceBool

from RefBooks.Tables                import rbCode, rbName, rbDiagnosticResult, rbEventTypePurpose, rbResult

from Ui_RBDiagnosticResultEditor    import Ui_ItemEditorDialog


class CRBDiagnosticResultList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CRefBookCol(u'Цель визита', ['eventPurpose_id'], rbEventTypePurpose, 30),
            CTextCol(   u'Код',         [rbCode], 10),
            CTextCol(   u'Региональный код', ['regionalCode'], 10),
            CTextCol(   u'Наименование',[rbName], 30),
            CTextCol(   u'Федеральный код', ['federalCode'], 10),
            # CRefBookCol(u'Результат обращения', ['result_id'], rbResult, 30),
            CDateCol(   u'Дата начала', ['begDate'], 10),
            CDateCol(   u'Дата окончания', ['endDate'], 10),
            ], rbDiagnosticResult, ['eventPurpose_id', rbCode, rbName])
        self.setWindowTitleEx(u'Результаты осмотра')

    def getItemEditor(self):
        return CRBDiagnosticResultEditor(self)
#
# ##########################################################################
#


class CRBDiagnosticResultEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    RESULT_LINK_TABLE = 'rbDiagnosticResult_rbResult'

    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, rbDiagnosticResult)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Результат осмотра')
        self.cmbEventPurpose.setTable(rbEventTypePurpose, False)
        self.setupDirtyCather()
        self._id = None
        self.tblRBResult.setTable(rbResult)

    def results(self):
        db = QtGui.qApp.db
        return db.getIdList(self.RESULT_LINK_TABLE, idCol='result_id', where='diagnosticResult_id=%d' % self._id)

    def setResults(self, itemIds):
        if not self._id:
            return
        db = QtGui.qApp.db
        db.deleteRecord(self.RESULT_LINK_TABLE, where='diagnosticResult_id=%d' % self._id)
        if itemIds:
            stmt = u'INSERT INTO %s (diagnosticResult_id, result_id) VALUES ' % self.RESULT_LINK_TABLE
            items = []
            for itemId in itemIds:
                items.append(u'(%d, %d)' % (self._id, itemId))
            db.query(stmt + ', '.join(items))

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        self._id = forceRef(record.value('id'))
        self.cmbEventPurpose.setValue(forceInt(record.value('eventPurpose_id')))
        self.edtCode.setText(forceString(record.value(rbCode)))
        self.edtRegionalCode.setText(forceString(record.value('regionalCode')))
        self.edtName.setText(forceString(record.value(rbName)))
        self.edtFederalCode.setText(forceString(record.value('federalCode')))
        # self.cmbResult.setValue(forceRef(record.value('result_id')))
        self.tblRBResult.setValues(self.results())
        self.chkFilterResults.setChecked(forceBool(record.value('filterResults')))
        self.edtBegDate.setDate(forceDate(record.value('begDate')))
        self.edtEndDate.setDate(forceDate(record.value('endDate')))

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue('eventPurpose_id', toVariant(self.cmbEventPurpose.value()))
        record.setValue(rbCode,       toVariant(forceStringEx(self.edtCode.text())))
        record.setValue('regionalCode', toVariant(forceStringEx(self.edtRegionalCode.text())))
        record.setValue(rbName,       toVariant(forceStringEx(self.edtName.text())))
        record.setValue('federalCode', toVariant(forceStringEx(self.edtFederalCode.text())))
        # record.setValue('result_id', toVariant(self.cmbResult.value()))
        record.setValue('filterResults', toVariant(self.chkFilterResults.isChecked()))
        record.setValue('begDate', toVariant(self.edtBegDate.date()))
        record.setValue('endDate', toVariant(self.edtEndDate.date()))
        return record

    def save(self):
        _id = super(CRBDiagnosticResultEditor, self).save()
        if _id:
            self._id = _id
            self.setResults(self.tblRBResult.values())
        return _id

    @QtCore.pyqtSlot(int)
    def on_cmbEventPurpose_currentIndexChanged(self, index):
        filter = 'eventPurpose_id=%d' % self.cmbEventPurpose.value() if self.cmbEventPurpose.value() else ''
        values = self.tblRBResult.values()
        self.tblRBResult.setFilter(filter)
        if values:
            self.tblRBResult.setValues(values)


