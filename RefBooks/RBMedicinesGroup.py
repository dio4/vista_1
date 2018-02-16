# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from library.interchange        import getLineEditValue, setLineEditValue
from library.ItemsListDialog    import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel         import CTextCol
from library.Utils              import forceString, toVariant

from Ui_RBMedicinesGroupEditor    import Ui_ItemEditorDialog


class CRBMedicinesGroupsList(CItemsListDialog):
    def __init__(self, parent):
        cols = []
        cols.append(CTextCol(u'Код',                   ['code'], 20))
        cols.append(CTextCol(u'Наименование',          ['name'], 80))

        CItemsListDialog.__init__(self, parent, cols, 'rbMedicinesGroup', 'name')
        self.setWindowTitle(u'Группы лекарственных препаратов')
        self.setObjectName('CRBMedicinesGroupsList')

    def preSetupUi(self):
        CItemsListDialog.preSetupUi(self)
        self.actDuplicate =      QtGui.QAction(u'Дублировать', self)
        self.actDuplicate.setObjectName('actDuplicate')
        self.actDelete =         QtGui.QAction(u'Удалить', self)
        self.actDelete.setObjectName('actDelete')

    def postSetupUi(self):
        CItemsListDialog.postSetupUi(self)
        self.tblItems.createPopupMenu([ self.actDuplicate, self.actDelete ])
        self.connect(self.tblItems.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.popupMenuAboutToShow)


    def getItemEditor(self):
        return CRBMedicinesGroupEditor(self)


    def popupMenuAboutToShow(self):
        currentItemId = self.currentItemId()
        self.actDuplicate.setEnabled(bool(currentItemId))
        self.actDelete.setEnabled(bool(currentItemId))

    @QtCore.pyqtSlot()
    def on_actDuplicate_triggered(self):
        def duplicateCurrentInternal():
            currentItemId = self.currentItemId()
            if currentItemId :
                db = QtGui.qApp.db
                table = db.table('rbMedicinesGroup')
                db.transaction()
                try:
                    record = db.getRecord(table, '*', currentItemId)
                    record.setValue('code', toVariant(forceString(record.value('code'))+'_1'))
                    record.setNull('id')
                    newItemId = db.insertRecord(table, record)
                    db.commit()
                except:
                    db.rollback()
                    QtGui.qApp.logCurrentException()
                    raise
                self.renewListAndSetTo(newItemId)
        QtGui.qApp.call(self, duplicateCurrentInternal)


    @QtCore.pyqtSlot()
    def on_actDelete_triggered(self):
        def deleteCurrentInternal():
            currentItemId = self.currentItemId()
            if currentItemId :
                row = self.tblItems.currentIndex().row()
                db = QtGui.qApp.db
                table = db.table('rbMedicinesGroup')
                db.deleteRecord(table, table['id'].eq(currentItemId))
                self.renewListAndSetTo()
                self.tblItems.setCurrentRow(row)
        QtGui.qApp.call(self, deleteCurrentInternal)

#
# ##########################################################################
#

class CRBMedicinesGroupEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rbMedicinesGroup')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Группа лекарственных препаратов')
        self.setupDirtyCather()
        self.edtCode.setFocus()

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(   self.edtCode,                  record, 'code')
        setLineEditValue(   self.edtName,                  record, 'name')


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(   self.edtCode,                  record, 'code')
        getLineEditValue(   self.edtName,                  record, 'name')
        return record
