# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2017 Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from RefBooks.ItemListColumnsEditor import CItemListColumnsEditor
from Ui_RBMedicineEditor import Ui_ItemEditorDialog
from library.ItemsListDialog import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel import CRefBookCol, CTextCol, CBoolCol
from library.Utils import forceString, toVariant, forceBool
from library.interchange import getLineEditValue, getRBComboBoxValue, setLineEditValue, setRBComboBoxValue


class CRBMedicinesList(CItemsListDialog):
    def __init__(self, parent):
        self.otherTable = False
        try:
            cols = []
            cols.append(CTextCol(u'Код', ['code'], 20))
            cols.append(CTextCol(u'Наименование', ['name'], 80))
            cols.append(CRefBookCol(u'Ед.изм.', ['unit_id'], 'rbUnit', 30))
            cols.append(CRefBookCol(u'Группа', ['group_id'], 'rbMedicinesGroup', 30))
            cols.append(CTextCol(u'МНН', ['mnn'], 50))
            cols.append(CTextCol(u'Лат. МНН', ['latinMnn'], 50))
            cols.append(CTextCol(u'Торговое наименование', ['tradeName'], 50))
            cols.append(CTextCol(u'Форма выпуска', ['issueForm'], 50))
            cols.append(CTextCol(u'Лат. форма выпуска', ['latinIssueForm'], 50))
            cols.append(CTextCol(u'Концентрация', ['concentration'], 50))
            cols.append(CBoolCol(u'Наркотик?', ['isDrugs'], 50))
            cols.append(CRefBookCol(u'Базовая\nед.изм.', ['baseUnit_id'], 'rbUnit', 30))
            cols.append(CRefBookCol(u'Мин.неделим.\nед.изм.', ['minIndivisibleUnit_id'], 'rbUnit', 30))
            cols.append(CRefBookCol(u'Упаковки\nед.изм.', ['packingUnit_id'], 'rbUnit', 30))
            cols.append(CTextCol(u'Базовых ед.\nв мин.неделим.', ['baseUnitsInMinIndivisibleUnit'], 30))
            cols.append(CTextCol(u'Мин.неделим ед.\nв ед.упаковки', ['minIndivisibleUnitsInPackingUnit'], 30))

            CItemsListDialog.__init__(self, parent, cols, 'rbMedicines', 'name', allowColumnsHiding=True)
        except Exception as e:
            self.otherTable = True
            print u'[RBMedicines.py] %s' % e

            cols = []
            cols.append(CTextCol(u'Код', ['code'], 20))
            cols.append(CTextCol(u'Наименование', ['name'], 80))
            cols.append(CRefBookCol(u'Ед.изм.', ['unit_id'], 'rbUnit', 30))
            cols.append(CRefBookCol(u'Группа', ['group_id'], 'rbMedicinesGroup', 30))
            cols.append(CTextCol(u'МНН', ['MNN'], 50))
            cols.append(CTextCol(u'Лат. МНН', ['latinMNN'], 50))
            cols.append(CTextCol(u'Торговое наименование', ['tradeName'], 50))
            cols.append(CTextCol(u'Форма выпуска', ['issueForm'], 50))
            cols.append(CTextCol(u'Лат. форма выпуска', ['latinIssueForm'], 50))
            cols.append(CTextCol(u'Концентрация', ['concentration'], 50))
            cols.append(CBoolCol(u'Наркотик?', ['isDrugs'], 50))
            cols.append(CRefBookCol(u'Базовая\nед.изм.', ['baseUnit_id'], 'rbUnit', 30))
            cols.append(CRefBookCol(u'Мин.неделим.\nед.изм.', ['minIndivisibleUnit_id'], 'rbUnit', 30))
            cols.append(CRefBookCol(u'Упаковки\nед.изм.', ['packingUnit_id'], 'rbUnit', 30))
            cols.append(CTextCol(u'Базовых ед.\nв мин.неделим.', ['baseUnitsInMinIndivisibleUnit'], 30))
            cols.append(CTextCol(u'Мин.неделим ед.\nв ед.упаковки', ['minIndivisibleUnitsInPackingUnit'], 30))

            CItemsListDialog.__init__(self, parent, cols, 'rbMedicines', 'name', allowColumnsHiding=True)

        self.setWindowTitle(u'Лекарственные препараты для формуляров')
        self.setObjectName('CRBMedicinesList')
        self.loadMyPreferences()

    def closeEvent(self, event):
        self.saveMyPreferences()

    def preSetupUi(self):
        CItemsListDialog.preSetupUi(self)
        self.actDuplicate = QtGui.QAction(u'Дублировать', self)
        self.actDuplicate.setObjectName('actDuplicate')
        self.actDelete = QtGui.QAction(u'Удалить', self)
        self.actDelete.setObjectName('actDelete')
        self.actChooseColumns = QtGui.QAction(u'Выбрать колонки...', self)
        self.actChooseColumns.setObjectName('actChooseColumns')

    def postSetupUi(self):
        CItemsListDialog.postSetupUi(self)
        self.tblItems.createPopupMenu([self.actDuplicate, self.actDelete, '-', self.actChooseColumns])
        self.connect(self.tblItems.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.popupMenuAboutToShow)

    def getItemEditor(self):
        return CRBMedicineEditor(self, self.otherTable)

    def popupMenuAboutToShow(self):
        currentItemId = self.currentItemId()
        self.actDuplicate.setEnabled(bool(currentItemId))
        self.actDelete.setEnabled(bool(currentItemId))

    @QtCore.pyqtSlot()
    def on_actDuplicate_triggered(self):
        def duplicateCurrentInternal():
            currentItemId = self.currentItemId()
            if currentItemId:
                db = QtGui.qApp.db
                table = db.table('rbMedicines')
                db.transaction()
                try:
                    record = db.getRecord(table, '*', currentItemId)
                    record.setValue('code', toVariant(forceString(record.value('code')) + '_1'))
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
            if currentItemId:
                row = self.tblItems.currentIndex().row()
                db = QtGui.qApp.db
                table = db.table('rbMedicines')
                db.deleteRecord(table, table['id'].eq(currentItemId))
                self.renewListAndSetTo()
                self.tblItems.setCurrentRow(row)

        QtGui.qApp.call(self, deleteCurrentInternal)

    @QtCore.pyqtSlot()
    def on_actChooseColumns_triggered(self):
        def chooseColumnsInternal():
            dlg = CItemListColumnsEditor(itemListDialog=self, parent=self)
            dlg.exec_()
            self.model.reset()

        QtGui.qApp.call(self, chooseColumnsInternal)


#
# ##########################################################################
#

class CRBMedicineEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self, parent, otherTable):
        self.otherTable = otherTable
        CItemEditorBaseDialog.__init__(self, parent, 'rbMedicines')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Лекарственный препарат')
        self.cmbUnit.setTable('rbUnit')
        self.cmbGroup.setTable('rbMedicinesGroup')
        self.cmbBaseUnit.setTable('rbUnit')
        self.cmbMinIndivUnit.setTable('rbUnit')
        self.cmbPackingUnit.setTable('rbUnit')
        self.setupDirtyCather()
        self.edtCode.setFocus()

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(self.edtCode, record, 'code')
        setLineEditValue(self.edtName, record, 'name')
        setRBComboBoxValue(self.cmbUnit, record, 'unit_id')
        setRBComboBoxValue(self.cmbGroup, record, 'group_id')

        if self.otherTable:
            setLineEditValue(self.edtMnn, record, 'MNN')
            setLineEditValue(self.edtMnnLat, record, 'latinMNN')
        else:
            setLineEditValue(self.edtMnn, record, 'mnn')
            setLineEditValue(self.edtMnnLat, record, 'latinMnn')

        setLineEditValue(self.edtTradeName, record, 'tradeName')
        setLineEditValue(self.edtIssueForm, record, 'issueForm')
        setLineEditValue(self.edtIssueFormLat, record, 'latinIssueForm')
        setLineEditValue(self.edtConcentration, record, 'concentration')
        if forceBool(record.value('isDrugs')):
            self.rbtnIsDrugYes.setChecked(True)
        else:
            self.rbtnIsDrugNo.setChecked(True)
        setRBComboBoxValue(self.cmbBaseUnit, record, 'baseUnit_id')
        setRBComboBoxValue(self.cmbMinIndivUnit, record, 'minIndivisibleUnit_id')
        setLineEditValue(self.edtBaseUnitsInMinIndiv, record, 'baseUnitsInMinIndivisibleUnit')
        setLineEditValue(self.edtMinIndivInPacking, record, 'minIndivisibleUnitsInPackingUnit')
        setRBComboBoxValue(self.cmbPackingUnit, record, 'packingUnit_id')

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(self.edtCode, record, 'code')
        getLineEditValue(self.edtName, record, 'name')
        getRBComboBoxValue(self.cmbUnit, record, 'unit_id')
        getRBComboBoxValue(self.cmbGroup, record, 'group_id')

        if self.otherTable:
            getLineEditValue(self.edtMnn, record, 'MNN')
            getLineEditValue(self.edtMnnLat, record, 'latinMNN')
        else:
            getLineEditValue(self.edtMnn, record, 'mnn')
            getLineEditValue(self.edtMnnLat, record, 'latinMnn')

        getLineEditValue(self.edtTradeName, record, 'tradeName')
        getLineEditValue(self.edtIssueForm, record, 'issueForm')
        getLineEditValue(self.edtIssueFormLat, record, 'latinIssueForm')
        getLineEditValue(self.edtConcentration, record, 'concentration')
        record.setValue('isDrugs', self.rbtnIsDrugYes.isChecked())
        getRBComboBoxValue(self.cmbBaseUnit, record, 'baseUnit_id')
        getRBComboBoxValue(self.cmbMinIndivUnit, record, 'minIndivisibleUnit_id')
        getLineEditValue(self.edtBaseUnitsInMinIndiv, record, 'baseUnitsInMinIndivisibleUnit')
        getLineEditValue(self.edtMinIndivInPacking, record, 'minIndivisibleUnitsInPackingUnit')
        getRBComboBoxValue(self.cmbPackingUnit, record, 'packingUnit_id')
        return record
