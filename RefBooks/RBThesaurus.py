# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.HierarchicalItemsListDialog    import CHierarchicalItemsListDialog
from library.interchange                    import getLineEditValue, setLineEditValue
from library.ItemsListDialog                import CItemEditorBaseDialog
from library.TableModel                     import CTextCol
from library.Utils                          import forceRef, forceString, toVariant

from Ui_RBThesaurusItemEditor               import Ui_ThesaurusItemEditorDialog


class CRBThesaurus(CHierarchicalItemsListDialog):
    def __init__(self, parent):
        CHierarchicalItemsListDialog.__init__(self, parent, [
#            CRefBookCol(u'Группа',   ['group_id'], 'rbComplain', 10),
            CTextCol(   u'Код',          ['code'], 20),
            CTextCol(   u'Наименование', ['name'],   40),
#            CEnumCol(   u'Пол',          ['sex'], SexList, 10),
#            CTextCol(   u'Возраст',      ['age'], 10),
            ], 'rbThesaurus', ['code', 'name', 'id'])
        self.setWindowTitleEx(u'Тезаурус')
#        self.connect(self.actDuplicate, QtCore.SIGNAL('triggered()'), self.duplicateCurrentRow)


    def preSetupUi(self):
        CHierarchicalItemsListDialog.preSetupUi(self)
        self.modelTree.setLeavesVisible(True)
        self.modelTree.setOrder('code')
        self.actDuplicate = QtGui.QAction(u'Дублировать', self)
        self.actDuplicate.setObjectName('actDuplicate')
        self.actDelete =    QtGui.QAction(u'Удалить', self)
        self.actDelete.setObjectName('actDelete')


    def postSetupUi(self):
        CHierarchicalItemsListDialog.postSetupUi(self)
        self.tblItems.createPopupMenu([self.actDuplicate, '-', self.actDelete])
        self.connect(self.tblItems.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.popupMenuAboutToShow)


    def getItemEditor(self):
        editor = CThesaurusItemEditor(self)
        editor.setGroupId(self.currentGroupId())
        return editor


    def popupMenuAboutToShow(self):
        currentItemId = self.currentItemId()
        self.actDuplicate.setEnabled(bool(currentItemId))
        self.actDelete.setEnabled(bool(currentItemId))


    @QtCore.pyqtSlot()
    def on_actDuplicate_triggered(self):
        def duplicateGroup(currentGroupId, newGroupId):
            db = QtGui.qApp.db
            table = db.table('rbThesaurus')
            records = db.getRecordList(table, '*', table['group_id'].eq(currentGroupId))
            for record in records:
                currentItemId = record.value('id')
                record.setValue('group_id', toVariant(newGroupId))
                record.setNull('id')
                newItemId = db.insertRecord(table, record)
                duplicateGroup(currentItemId, newItemId)

        def duplicateCurrentInternal():
            currentItemId = self.currentItemId()
            if currentItemId :
                db = QtGui.qApp.db
                table = db.table('rbThesaurus')
                db.transaction()
                try:
                    record = db.getRecord(table, '*', currentItemId)
                    record.setValue('code', toVariant(forceString(record.value('code'))+'_1'))
                    record.setNull('id')
                    newItemId = db.insertRecord(table, record)
                    duplicateGroup(currentItemId, newItemId)
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
                table = db.table('rbThesaurus')
                db.deleteRecord(table, table['id'].eq(currentItemId))
                self.renewListAndSetTo()
                self.tblItems.setCurrentRow(row)
        QtGui.qApp.call(self, deleteCurrentInternal)

#
# ##########################################################################
#

class CThesaurusItemEditor(CItemEditorBaseDialog, Ui_ThesaurusItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rbThesaurus')
        self.setupUi(self)
        self.setWindowTitleEx(u'Жалоба')
        self.setupDirtyCather()
        self.groupId = None
        self.prevName = self.edtName.text()
        self.edtTemplate.setText(self.autoTemplate(self.prevName))


    def setGroupId(self, id):
        self.groupId = id


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(   self.edtCode,           record, 'code')
        setLineEditValue(   self.edtName,           record, 'name')
        setLineEditValue(   self.edtTemplate,       record, 'template')
        self.groupId = forceRef(record.value('group_id'))
#        record.setValue('group_id', toVariant(self.groupId))

#        setRBComboBoxValue( self.cmbGroup,          record, 'group_id')
#        setComboBoxValue(   self.cmbSex,            record, 'sex')
#        (begUnit, begCount, endUnit, endCount) = parseAgeSelector(forceString(record.value('age')))
#        self.cmbBegAgeUnit.setCurrentIndex(begUnit)
#        self.edtBegAgeCount.setText(str(begCount))
#        self.cmbEndAgeUnit.setCurrentIndex(endUnit)
#        self.edtEndAgeCount.setText(str(endCount))

        self.prevName = self.edtName.text()
        self.setIsDirty(False)

    def getRecord(self):
        db = QtGui.qApp.db
        stmn = "SELECT * FROM rbThesaurus WHERE code = '%s'" % self.edtCode.text()
        q = db.query(stmn)
        if q.first():
            record = q.record()
            if forceRef(record.value('id')) != self.itemId():
                raise Exception(u"Данный код уже используется для %s" % forceString(record.value('name')))
        else:
            record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue( self.edtCode,     record, 'code')
        getLineEditValue( self.edtName,     record, 'name')
        getLineEditValue( self.edtTemplate, record, 'template')
        record.setValue('group_id', toVariant(self.groupId))
        return record
#        getRBComboBoxValue( self.cmbGroup,          record, 'group_id')
#        getComboBoxValue(   self.cmbSex,            record, 'sex')
#        record.setValue('age',        toVariant(composeAgeSelector(
#                    self.cmbBegAgeUnit.currentIndex(),  forceStringEx(self.edtBegAgeCount.text()),
#                    self.cmbEndAgeUnit.currentIndex(),  forceStringEx(self.edtEndAgeCount.text())
#                        )))



    def checkDataEntered(self):
        result = CItemEditorBaseDialog.checkDataEntered(self)
#        result = result and (self.checkRecursion(self.cmbGroup.value()) or self.checkValueMessage(u'попытка создания циклической группировки', False, self.cmbGroup))
#        result = result and (self.cmbPurpose.value() or self.checkInputMessage(u'назначение', False, self.cmbPurpose))
        return result


    def autoTemplate(self, name):
        return '%s: '+name


    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtName_textEdited(self, text):
        if self.autoTemplate(self.prevName) == self.edtTemplate.text():
            self.edtTemplate.setText(self.autoTemplate(text))
            self.prevName = self.edtName.text()