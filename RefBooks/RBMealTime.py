# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore

from library.ItemsListDialog    import CItemEditorBaseDialog, CItemsListDialogEx
from library.TableModel         import CTextCol, CTimeCol
from library.Utils              import forceString, forceStringEx, forceTime, toVariant

from RefBooks.Tables            import rbCode, rbName

from Ui_RBMealTime              import Ui_RBMealTime


class CRBMealTime(CItemsListDialogEx):
    def __init__(self, parent):
        CItemsListDialogEx.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            CTimeCol(u'с', ['begTime'], 40),
            CTimeCol(u'по', ['endTime'], 40)
            ], 'rbMealTime', [rbCode, rbName, 'begTime', 'endTime'])
        self.setWindowTitleEx(u'Периоды питания')

    def getItemEditor(self):
        return CRBMealTimeEditor(self)

#
# ##########################################################################
#

class CRBMealTimeEditor(CItemEditorBaseDialog, Ui_RBMealTime):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rbMealTime')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Период питания')
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        self.edtCode.setText(forceString(record.value(rbCode)))
        self.edtName.setText(forceString(record.value(rbName)))
        timeRange = forceTime(record.value('begTime')), forceTime(record.value('endTime'))
        self.edtRangeTime.setTimeRange(timeRange)


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue(rbCode,    toVariant(forceStringEx(self.edtCode.text())))
        record.setValue(rbName,    toVariant(forceStringEx(self.edtName.text())))
        begTime, endTime = self.edtRangeTime.timeRange() if self.edtRangeTime else (None, None)
        record.setValue('begTime', toVariant(forceTime(begTime)))
        record.setValue('endTime', toVariant(forceTime(endTime)))
        return record

