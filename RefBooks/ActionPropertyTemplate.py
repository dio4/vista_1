# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from Ui_ActionPropertyTemplateEditor import Ui_ActionPropertyTemplateEditorDialog
from library.AgeSelector import composeAgeSelector, parseAgeSelector
from library.HierarchicalItemsListDialog import CHierarchicalItemsListDialog
from library.ItemsListDialog import CItemEditorBaseDialog
from library.TableModel import CEnumCol, CTextCol
from library.Utils import forceString, forceStringEx, toVariant
from library.interchange import getComboBoxValue, getLineEditValue, getRBComboBoxValue, \
    setComboBoxValue, setLineEditValue, setRBComboBoxValue

SexList = ['', u'М', u'Ж']

class CActionPropertyTemplateList(CHierarchicalItemsListDialog):
    def __init__(self, parent, forSelect=False):
        CHierarchicalItemsListDialog.__init__(self, parent, [
#            CRefBookCol(u'Группа',   ['group_id'], 'ActionPropertyTemplate', 10),
            CTextCol(   u'Код',          ['code'], 20),
            CTextCol(   u'Фед.код',      ['federalCode'], 20),
            CTextCol(   u'Рег.код',      ['regionalCode'], 20),
            CTextCol(   u'Наименование', ['name'],   40),
            CTextCol(   u'Сокращение',   ['abbrev'], 20),
            CEnumCol(   u'Пол',          ['sex'], SexList, 10),
            CTextCol(   u'Возраст',      ['age'], 10),
            ], 'ActionPropertyTemplate', ['name', 'id'], forSelect=forSelect)
        self.setWindowTitleEx(u'Библиотека свойств действий')
        self.actDuplicate = QtGui.QAction(u'Дублировать', self)
        self.actDuplicate.setObjectName('actDuplicate')
        self.connect(self.actDuplicate, QtCore.SIGNAL('triggered()'), self.duplicateCurrentRow)
        self.tblItems.createPopupMenu([self.actDuplicate])
        self.tblItems.addPopupDelSelectedRow()


    def getItemEditor(self):
        return CActionPropertyTemplateEditor(self)


    def duplicateCurrentRow(self):
        def duplicateCurrentInternal():
            currentItemId = self.currentItemId()
            if currentItemId :
                db = QtGui.qApp.db
                table = db.table('ActionPropertyTemplate')
                db.transaction()
                try:
                    record = db.getRecord(table, '*', currentItemId)
                    record.setValue('code', toVariant(forceString(record.value('code'))+'_1'))
                    record.setValue('name', toVariant(forceString(record.value('name'))+'_1'))
                    record.setNull('id')
                    newItemId = db.insertRecord(table, record)
                    db.commit()
                except:
                    db.rollback()
                    QtGui.qApp.logCurrentException()
                    raise
                self.renewListAndSetTo(newItemId)
        QtGui.qApp.call(self, duplicateCurrentInternal)

#
# ##########################################################################
#

class CActionPropertyTemplateEditor(CItemEditorBaseDialog, Ui_ActionPropertyTemplateEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'ActionPropertyTemplate')
        self.setupUi(self)
        self.setWindowTitleEx(u'Шаблон свойства')
###        self.cmbGroup.setTable('ActionPropertyTemplate')
        self.cmbService.setTable('rbService')
        self.setupDirtyCather()


    def setGroupId(self, id):
        self.cmbGroup.setValue(id)
        self.setIsDirty(False)


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(   self.edtCode,           record, 'code')
        setLineEditValue(   self.edtFederalCode,    record, 'federalCode')
        setLineEditValue(   self.edtRegionalCode,   record, 'regionalCode')
        setLineEditValue(   self.edtName,           record, 'name')
        setLineEditValue(   self.edtAbbrev,         record, 'abbrev')
        setRBComboBoxValue( self.cmbGroup,          record, 'group_id')
        setComboBoxValue(   self.cmbSex,            record, 'sex')
        (begUnit, begCount, endUnit, endCount) = parseAgeSelector(forceString(record.value('age')))
        self.cmbBegAgeUnit.setCurrentIndex(begUnit)
        self.edtBegAgeCount.setText(str(begCount))
        self.cmbEndAgeUnit.setCurrentIndex(endUnit)
        self.edtEndAgeCount.setText(str(endCount))
        setRBComboBoxValue( self.cmbService,        record, 'service_id')
        self.setIsDirty(False)


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(   self.edtCode,           record, 'code')
        getLineEditValue(   self.edtFederalCode,    record, 'federalCode')
        getLineEditValue(   self.edtRegionalCode,   record, 'regionalCode')
        getLineEditValue(   self.edtName,           record, 'name')
        getLineEditValue(   self.edtAbbrev,         record, 'abbrev')
        getRBComboBoxValue( self.cmbGroup,          record, 'group_id')
        getComboBoxValue(   self.cmbSex,            record, 'sex')
        record.setValue('age',        toVariant(composeAgeSelector(
                    self.cmbBegAgeUnit.currentIndex(),  forceStringEx(self.edtBegAgeCount.text()),
                    self.cmbEndAgeUnit.currentIndex(),  forceStringEx(self.edtEndAgeCount.text())
                        )))
        getRBComboBoxValue( self.cmbService,        record, 'service_id')
        return record


    def checkDataEntered(self):
        result = CItemEditorBaseDialog.checkDataEntered(self)
        result = result and (self.checkRecursion(self.cmbGroup.value()) or self.checkValueMessage(u'попытка создания циклической группировки', False, self.cmbGroup))
#        result = result and (self.cmbPurpose.value() or self.checkInputMessage(u'назначение', False, self.cmbPurpose))
        return result