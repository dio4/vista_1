# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from Events.ActionTemplateChoose import CActionTemplateModel
from RefBooks.ActionTemplate import CActionTypeCol
from Registry.Utils import CCheckNetMixin
from Ui_ActionTemplateCreateDialog import Ui_ActionTemplateCreateDialog
from Ui_ActionTemplateSaveDialog import Ui_ActionTemplateSaveDialog
from library.AgeSelector import checkAgeSelector, composeAgeSelector, parseAgeSelector
from library.DialogBase import CDialogBase
from library.ItemsListDialog import CItemEditorBaseDialog
from library.TableModel import CEnumCol, CRefBookCol, CTableModel, CTextCol
from library.Utils import forceInt, forceRef, forceString, forceStringEx, toVariant
from library.interchange import getComboBoxValue, getLineEditValue


class CActionTemplateSaveDialog(CDialogBase, Ui_ActionTemplateSaveDialog):
    def __init__(self, parent, actionRecord, action, clientSex, clientAge, personId, specialityId, model=None):
        CDialogBase.__init__(self, parent)

        actionTypeId = action.getType().id
        self.addModels('Tree', CActionTemplateTreeModel(self, actionTypeId, personId, specialityId, clientSex, clientAge, removeEmptyNodes=False))
        self.modelTree.setRootItemVisible(True)

        self.addModels('Table', CActionTemplateTableModel(self, self.modelTree.filter()))

        self.btnCreateGroup = QtGui.QPushButton(u'Создать группу', self)
        self.btnCreateGroup.setObjectName('btnCreateGroup')
        self.btnCreateTemplate = QtGui.QPushButton(u'Создать шаблон', self)
        self.btnCreateTemplate.setObjectName('btnCreateTemplate')
        self.btnUpdateTemplate = QtGui.QPushButton(u'Обновить шаблон', self)
        self.btnUpdateTemplate.setObjectName('btnUpdateTemplate')
        self.setupUi(self)
        self.buttonBox.addButton(self.btnCreateGroup, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btnCreateTemplate, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btnUpdateTemplate, QtGui.QDialogButtonBox.ActionRole)
        self.setWindowTitleEx(u'Сохранение шаблона действия')
        self.treeItems.header().hide()

        self.setModels(self.treeItems, self.modelTree, self.selectionModelTree)
        self.setModels(self.tblItems, self.modelTable, self.selectionModelTable)

        self.treeItems.expandAll()
        idList = self.select()
        self.modelTable.setIdList(idList)

        self.action = action.clone()
        self.clientSex = clientSex
        self.clientAge = clientAge
        self.personId = personId
        self.specialityId = specialityId

    def currentGroupId(self):
        return self.modelTree.itemId(self.treeItems.currentIndex())

    def select(self):
        table = self.modelTable.table()
        groupId = self.currentGroupId()
        return QtGui.qApp.db.getIdList(table.name(), 'id', table['group_id'].eq(groupId), 'name')

    def renewListAndSetTo(self, itemId=None):
        if not itemId:
            itemId = self.tblItems.currentItemId()
        idList = self.select()
        self.tblItems.setIdList(idList, itemId)

    def updateButtons(self):
        index = self.tblItems.currentIndex()
        if index.isValid():
            flags = self.modelTable.flags(index)
            enabled = int(flags) & QtCore.Qt.ItemIsEnabled
        else:
            enabled = False
        self.btnUpdateTemplate.setEnabled(enabled)
        # Возможно, это как-то проще делается?
        self.btnCreateTemplate.setEnabled(self.modelTree.getRootItem().id() != self.modelTree.itemId(self.treeItems.currentIndex()))

    def updateTemplate(self):
        id = self.tblItems.currentItemId()
        if id:
            db = QtGui.qApp.db
            try:
                db.transaction()
                actionId = self.action.save(isActionTemplate=True) if self.action else None
                record = db.getRecord('ActionTemplate', '*', id)
                oldActionId = forceRef(record.value('action_id'))
                record.setValue('action_id', toVariant(actionId))
                db.updateRecord('ActionTemplate', record)
                if oldActionId:
                    db.deleteRecord('Action', 'id=%d' % oldActionId)
                db.commit()
            # self.renewListAndSetTo(id)
            except:
                db.rollback()
                QtGui.qApp.logCurrentException()
                raise

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelTree_currentChanged(self, current, previous):
        self.renewListAndSetTo(None)
        self.updateButtons()

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelTable_currentChanged(self, current, previous):
        self.updateButtons()

    @QtCore.pyqtSlot()
    def on_btnCreateGroup_clicked(self):
        name, ok = QtGui.QInputDialog.getText(self, u'Новая группа шаблонов действия', u'Наименование', QtGui.QLineEdit.Normal, '')
        name = forceStringEx(name)
        if name and ok:
            groupId = self.currentGroupId()
            db = QtGui.qApp.db
            record = db.record('ActionTemplate')
            record.setValue('group_id', toVariant(groupId))
            record.setValue('name', toVariant(name))
            id = db.insertRecord('ActionTemplate', record)
            if id:
                self.modelTree.updateItemById(groupId)
                index = self.modelTree.findItemId(id)
                self.treeItems.setCurrentIndex(index)
                self.renewListAndSetTo(None)

    @QtCore.pyqtSlot()
    def on_btnCreateTemplate_clicked(self):
        groupId = self.currentGroupId()
        dlg = CActionTemplateCreateDialog(self, groupId, self.action, self.clientSex, self.clientAge, self.personId, self.specialityId)
        if dlg.exec_():
            self.modelTree.updateItemById(groupId)
            self.renewListAndSetTo(dlg.itemId())
            self.accept()

    @QtCore.pyqtSlot()
    def on_btnUpdateTemplate_clicked(self):
        self.updateTemplate()
        self.accept()


class CActionTemplateTreeModel(CActionTemplateModel):
    pass


class CActionTemplateTableModel(CTableModel):
    def __init__(self, parent, filter):
        actionCol = CActionTypeCol(u'Действие', ['action_id'], 10)
        CTableModel.__init__(self, parent, [
            CTextCol(u'Наименование', ['name'], 40),
            CEnumCol(u'Пол', ['sex'], ['', u'М', u'Ж'], 10),
            CTextCol(u'Возраст', ['age'], 10),
            CRefBookCol(u'Врач', ['owner_id'], 'vrbPersonWithSpeciality', 10),
            CRefBookCol(u'Специальность', ['speciality_id'], 'rbSpeciality', 10),
            actionCol,
        ], 'ActionTemplate')
        self.actionCol = actionCol
        self.filter = filter
        self.enabled = []

    def setIdList(self, idList, realItemCount=None):
        CTableModel.setIdList(self, idList, realItemCount)
        self.enabled = [None] * len(idList)

    def _isEnabled(self, item):
        actionTypeId = self.actionCol.getActionTypeId(forceRef(item.value('action_id')))
        sex = forceInt(item.value('sex'))
        age = forceString(item.value('age'))
        personId = forceRef(item.value('owner_id'))
        specialityId = forceRef(item.value('speciality_id'))

        if self.filter.actionTypeId and (actionTypeId is None or (actionTypeId and self.filter.actionTypeId != actionTypeId)):
            return False
        if self.filter.personId and personId and self.filter.personId != personId:
            return False
        if self.filter.specialityId and specialityId and self.filter.specialityId != specialityId:
            return False
        if self.filter.clientSex and sex and self.filter.clientSex != sex:
            return False
        if self.filter.clientAge and age and not checkAgeSelector(parseAgeSelector(age), self.filter.clientAge):
            return False
        return True

    def flags(self, index):
        row = index.row()
        if self.enabled[row] is None:
            self.enabled[row] = self._isEnabled(self.getRecordByRow(row))
        return (QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled) if self.enabled[row] else QtCore.Qt.NoItemFlags


class CActionTemplateCreateDialog(CItemEditorBaseDialog, Ui_ActionTemplateCreateDialog, CCheckNetMixin):
    def __init__(self, parent, groupId, action, clientSex, clientAge, personId, specialityId):
        CItemEditorBaseDialog.__init__(self, parent, 'ActionTemplate')
        CCheckNetMixin.__init__(self)
        self.setupUi(self)
        self.setWindowTitleEx(u'Создание шаблона действия')

        self.groupId = groupId
        self.cmbSpeciality.setTable('rbSpeciality')
        self.cmbSex.setCurrentIndex(clientSex)
        ageConstraint = self.getSpecialityConstraint(specialityId).age
        if not ageConstraint:
            ageConstraint = self.getPersonNet(personId).age
        if ageConstraint:
            (begUnit, begCount, endUnit, endCount) = ageConstraint
            self.cmbBegAgeUnit.setCurrentIndex(begUnit)
            self.edtBegAgeCount.setText(str(begCount))
            self.cmbEndAgeUnit.setCurrentIndex(endUnit)
            self.edtEndAgeCount.setText(str(endCount))
        self.cmbOwner.setValue(personId)
        self.cmbSpeciality.setValue(specialityId)
        self.action = action.clone()
        self.setupDirtyCather()

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue('group_id', toVariant(self.groupId))
        getLineEditValue(self.edtName, record, 'name')
        getComboBoxValue(self.cmbSex, record, 'sex')
        record.setValue('age', toVariant(composeAgeSelector(self.cmbBegAgeUnit.currentIndex(),
                                                            forceStringEx(self.edtBegAgeCount.text()),
                                                            self.cmbEndAgeUnit.currentIndex(),
                                                            forceStringEx(self.edtEndAgeCount.text()))))
        record.setValue('owner_id', toVariant(self.cmbOwner.value() if self.rbVisibleToOwner.isChecked() else None))
        record.setValue('speciality_id', toVariant(self.cmbSpeciality.value() if self.rbVisibleToSpeciality.isChecked() else None))
        record.setValue('action_id', toVariant(self.saveAction()))
        return record

    def checkDataEntered(self):
        result = True
        result = result and (forceStringEx(self.edtName.text()) or
                             self.checkInputMessage(u'наименование', False, self.edtName))
        result = result and (not self.rbVisibleToOwner.isChecked() or
                             self.cmbOwner.value() or
                             self.checkInputMessage(u'врача', False, self.cmbOwner))
        result = result and (not self.rbVisibleToSpeciality.isChecked() or
                             self.cmbSpeciality.value() or
                             self.checkInputMessage(u'специальность', False, self.cmbSpeciality))
        return result

    def saveAction(self):
        if self.action:
            return self.action.save(isActionTemplate=True)
        else:
            return None
