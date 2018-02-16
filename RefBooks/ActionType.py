# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui, QtSql

from Events.Action import ActionPropertyCopyModifier, CActionPropertyValueTypeRegistry, CActionType, CActionTypeCache
from Events.ActionPropertyTemplateComboBox import CActionPropertyTemplateComboBox
from RefBooks.GroupActionTypeEditor import CGroupActionTypeEditor
from RefBooks.SelectService import selectService
from RefBooks.Utils import CServiceTypeModel
from Ui_ActionTypeEditor import Ui_ActionTypeEditorDialog
from Ui_ActionTypeFindDialog import Ui_ActionTypeFindDialog
from Ui_ActionTypeListDialog import Ui_ActionTypeListDialog
from Users.Rights import urActionTypeForceDelete, urAdmin
from library.AgeSelector import composeAgeSelector, parseAgeSelector
from library.DialogBase import CDialogBase
from library.HierarchicalItemsListDialog import CHierarchicalItemsListDialog
from library.InDocTable import CBackRelationInDockTableCol, CBoolInDocTableCol, CEnumInDocTableCol, CInDocTableCol, \
    CInDocTableModel, CIntInDocTableCol, \
    CRBInDocTableCol, CSelectStrInDocTableCol
from library.ItemsListDialog import CItemEditorBaseDialog
from library.TableModel import CDragDropTableModel, CEnumCol, CRefBookCol, CTableModel, CTextCol
from library.TreeModel import CDragDropDBTreeModelWithClassItems
from library.Utils import addDotsEx, forceBool, forceRef, forceString, forceStringEx, formatRecordsCount, getPref, \
    getPrefBool, setPref, toVariant
from library.crbcombobox import CRBComboBox, CRBModelDataCache
from library.interchange import getCheckBoxValue, getComboBoxValue, getLineEditValue, \
    getRBComboBoxValue, getSpinBoxValue, setCheckBoxValue, \
    setComboBoxValue, setLineEditValue, setRBComboBoxValue, \
    setSpinBoxValue

SexList = ['', u'М', u'Ж']


class CActionTypeList(CHierarchicalItemsListDialog, Ui_ActionTypeListDialog):

    setupUi = Ui_ActionTypeListDialog.setupUi
    retranslateUi = Ui_ActionTypeListDialog.retranslateUi
    mimeTypeActionPropertyIdList = 'application/x-s11/actionpropertyidlist'

    def __init__(self, parent):
        CHierarchicalItemsListDialog.__init__(self, parent, [
            CEnumCol(u'Класс', ['class'], [u'статус', u'диагностика', u'лечение', u'прочие мероприятия', u'анализы'], 10),
            CRefBookCol(u'Группа',   ['group_id'], 'ActionType', 10),
            CTextCol(   u'Код',          ['code'], 20),
            CTextCol(   u'Наименование', ['name'], 40),
            CEnumCol(   u'Пол',          ['sex'], SexList, 10),
            CTextCol(   u'Возраст',      ['age'], 10),
            CTextCol(   u'Каб',          ['office'], 5),
            CTextCol(   u'Код для отчётов', ['flatCode'], 20),
            CTextCol(   u'Код в ЛИС',    ['lis_code'], 20),
            ], 'ActionType', ['class', 'group_id', 'code', 'name', 'id'], findClass=CFindDialog)
        self.setWindowTitleEx(u'Типы действий')
        self.actDuplicate = QtGui.QAction(u'Дублировать', self)
        self.connect(self.actDuplicate, QtCore.SIGNAL('triggered()'), self.duplicateCurrentRow)
        self.expandedItemsState = {}
        self.setSettingsTblItems()
        self.additionalPostSetupUi()

        self.tblItems.setDragEnabled(True)
        self.treeItems.setAcceptDrops(True)
        self.tblItems.setDropIndicatorShown(True)
        self.treeItems.setDropIndicatorShown(True)

        self.addModels('ServiceType', CServiceTypeModel(0))
        self.cmbServiceType.setModel(self.modelServiceType)

    def tree_ids(self, root_id):
        id_list = []
        db = QtGui.qApp.db
        tbl = db.table('ActionType')
        if root_id:
            id_list.append(root_id)
            stmt = db.selectStmt(tbl, ['id'], tbl['group_id'].eq(root_id))
            q = db.query(stmt)
            while q.next():
                id_list += self.tree_ids(q.record().value('id').toInt()[0])
        return id_list

    def can_force_delete(self):
        return QtGui.qApp.userHasAnyRight((urAdmin, urActionTypeForceDelete))

    def setSettingsTblItems(self):
        self.tblItems.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

    def preSetupUi(self):
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.addModels('Tree', CDragDropDBTreeModelWithClassItems(self, self.tableName, 'id', 'group_id', 'name', 'class', self.order, dropToRootItem=False))
        self.addModels('Table', CDragDropTableModel(self, self.cols, self.tableName))
        self.modelTree.setLeavesVisible(True)
        self.modelTree.setClassItems((
                                     (u'Статус', 0),
                                     (u'Диагностика', 1),
                                     (u'Лечение', 2),
                                     (u'Прочие мероприятия', 3),
                                     (u'Анализы', 4)))
        self.actDelete =    QtGui.QAction(u'Удалить', self)
        self.actDelete.setObjectName('actDelete')

    def postSetupUi(self):
        #comboboxes
        self.activeActionTypeIdList = []
        specialValues = [(-2, u'не определен', u'не определен'),
                         (-1, u'определен',    u'определен')]
        self.cmbService.setTable('rbService', addNone=True, specialValues=specialValues)
        self.cmbQuotaType.setTable('QuotaType', addNone=True, specialValues=specialValues)
        self.cmbTissueType.setTable('rbTissueType', addNone=True, specialValues=specialValues)
        CHierarchicalItemsListDialog.postSetupUi(self)
        self.getDefaultParams()

    def additionalPostSetupUi(self):
        self.treeItems.expand(self.modelTree.index(0, 0))
        self.setPopupMenu()
        #drag-n-drop support
        self.treeItems.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        # tree popup menu
        self.treeItems.createPopupMenu([self.actDelete])
        self.connect(self.treeItems.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.popupMenuAboutToShow)
        self.connect(self.tblItems.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.itemsPopupMenuAboutToShow)
        self.connect(self.modelTree, QtCore.SIGNAL('saveExpandedState()'),  self.saveExpandedState)
        self.connect(self.modelTree, QtCore.SIGNAL('restoreExpandedState()'),  self.restoreExpandedState)

    def setPopupMenu(self):
        self.actSelectAllRow = QtGui.QAction(u'Выделить все строки', self)
        self.tblItems.addPopupAction(self.actSelectAllRow)
        self.connect(self.actSelectAllRow, QtCore.SIGNAL('triggered()'), self.selectAllRowTblItem)

        self.actClearSelectionRow = QtGui.QAction(u'Снять выделение', self)
        self.tblItems.addPopupAction(self.actClearSelectionRow)
        self.connect(self.actClearSelectionRow, QtCore.SIGNAL('triggered()'), self.clearSelectionRow)

        self.actDelSelectedRows = QtGui.QAction(u'Удалить выделенные строки', self)
        self.tblItems.addPopupAction(self.actDelSelectedRows)
        self.connect(self.actDelSelectedRows, QtCore.SIGNAL('triggered()'), self.delSelectedRows)

        self.tblItems.addPopupAction(self.actDuplicate)

        self.tblItems.addPopupSeparator()

        self.actCopyCurrentItemProperties = QtGui.QAction(u'Копировать все свойства', self)
        self.tblItems.addPopupAction(self.actCopyCurrentItemProperties)
        self.connect(self.actCopyCurrentItemProperties, QtCore.SIGNAL('triggered()'), self.copyCurrentItemProperties)

        self.actPasteProperties = QtGui.QAction(u'Вставить свойства', self)
        self.actPasteProperties.setEnabled(False)
        self.tblItems.addPopupAction(self.actPasteProperties)
        self.connect(self.actPasteProperties, QtCore.SIGNAL('triggered()'), self.pasteProperties)

        self.tblItems.addPopupSeparator()

        self.actGroupEditor = QtGui.QAction(u'Групповой редактор', self)
        self.tblItems.addPopupAction(self.actGroupEditor)
        self.connect(self.actGroupEditor, QtCore.SIGNAL('triggered()'), self.on_actGroupEditor)

    def on_actGroupEditor(self):
        selectedIdList = self.tblItems.selectedItemIdList()
        itemId = self.tblItems.currentItemId()
        if CGroupActionTypeEditor(self, selectedIdList, itemId).exec_():
            self.renewListAndSetTo(itemId)

    def copyCurrentItemProperties(self):
        currentItemId = self.tblItems.currentItemId()

        if currentItemId:
            db = QtGui.qApp.db
            tableActionPropertyType = db.table('ActionPropertyType')
            idList= db.getIdList(tableActionPropertyType, '*',
                        [tableActionPropertyType['actionType_id'].eq(currentItemId),
                         tableActionPropertyType['deleted'].eq(0)])
            if idList != []:
                strList = ','.join(str(id) for id in idList if id)
                mimeData = QtCore.QMimeData()
                v = toVariant(strList)
                mimeData.setData(self.mimeTypeActionPropertyIdList, v.toByteArray())
                QtGui.qApp.clipboard().setMimeData(mimeData)
                self.statusBar.showMessage(u'Скопировано свойств: %d.' % len(idList),  5000)
                self.actPasteProperties.setEnabled(True)
            else:
                self.statusBar.showMessage(u'Нет свойств для копирования.',  5000)

    def pasteProperties(self):
        def propertiesAreEqualInternal(x,  y):
            if x.count() == y.count():
                # сравниваем только имя, пол и возраст
                for name in ('name',  'sex',  'age'):
                    if x.value(name) != y.value(name):
                        return False

            return True

        def propertyExistInListInternal(property, propertyList):
            for x in propertyList:
                if propertiesAreEqualInternal(property,  x):
                    return True
            return False

        selectedIdList = self.tblItems.selectedItemIdList()

        if selectedIdList != []:
            mimeData = QtGui.qApp.clipboard().mimeData()
            if mimeData.hasFormat(self.mimeTypeActionPropertyIdList):
                strList = forceString(mimeData.data(self.mimeTypeActionPropertyIdList)).split(',')
                db = QtGui.qApp.db
                tableActionPropertyType = db.table('ActionPropertyType')

                propertyList = db.getRecordList(tableActionPropertyType, where=[
                        tableActionPropertyType['id'].inlist(strList), tableActionPropertyType['deleted'].eq(0)])
                nInsert = 0
                nTotal = len(strList)*len(selectedIdList)

                if propertyList != []:
                    for currentItemId in selectedIdList:
                        currentPropertyList= db.getRecordList(tableActionPropertyType, '*',
                            [tableActionPropertyType['actionType_id'].eq(currentItemId),
                             tableActionPropertyType['deleted'].eq(0)])

                        for newProperty in propertyList:
                            if not propertyExistInListInternal(newProperty,  currentPropertyList):
                                newProperty.setNull('id')
                                newProperty.setValue('actionType_id', toVariant(currentItemId))
                                db.insertRecord(tableActionPropertyType, newProperty)
                                nInsert += 1

                    self.statusBar.showMessage(u'Вставлено свойств: %d из %d возможных.' % (nInsert, nTotal),  5000)
                else:
                    self.statusBar.showMessage(u'Нечего вставлять.',  5000)
            else:
                self.statusBar.showMessage(u'Ошибка: неизвестный формат данных в буфере обмена.',  5000)

        self.actPasteProperties.setEnabled(False)

    def selectAllRowTblItem(self):
        self.tblItems.selectAll()

    def clearSelectionRow(self):
        self.tblItems.clearSelection()

    def delSelectedRows(self):
        db = QtGui.qApp.db
        selectedIdList = self.tblItems.selectedItemIdList()
        tableActionType = db.table('ActionType')
        if QtGui.QMessageBox.question(self, u'Подтверждение удаления',
                                      u'Вы уверены что хотите удалить выделенные строки? (количество строк: %d)' % len(selectedIdList),
                                      QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                      QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            if db.getCount(tableActionType, where=db.joinAnd((
                                                        tableActionType['locked'].eq(1),  # upd 17.10.2016/i3418
                                                        tableActionType['id'].inlist(selectedIdList)
                                                    ))) > 0 and not self.can_force_delete():
                QtGui.QMessageBox.warning(self, u'Внимание!',
                                          u'Вы не имеете права на удаление одного или нескольких выбранных типов')
                return
            actionTable = db.table('Action')
            for id in selectedIdList:
                tree = self.tree_ids(id)
                if db.getCount(tableActionType, where=db.joinAnd((
                                                                        tableActionType['id'].inlist(tree),
                                                                        tableActionType['locked'].eq(1)
                                                                ))) > 0 and not self.can_force_delete():
                    QtGui.QMessageBox.warning(self, u'Внимание!',
                                              u'Вы не имеете права на удаление одного или нескольких дочерних '
                                              u'элементов выбранных типов')
                    self.modelTree.update()
                    self.modelTable.setIdList(self.select())
                    return
                for tree_id in tree:
                    if db.getCount(actionTable, where='actionType_id=' + str(tree_id)) > 0:
                        record = db.getRecord('ActionType', 'name', tree_id)
                        QtGui.QMessageBox.warning(self, u'Внимание!',
                                                  u'Нельзя удалить тип ' + record.field('name').value().toString() +
                                                  u', записи с которым есть в базе. Сначала удалите записи')
                    else:
                        record = db.getRecord(tableActionType, ['id', 'deleted'], tree_id)
                        record.setValue('deleted', QtCore.QVariant(1))
                        db.updateRecord(tableActionType, record)
        self.modelTree.update()
        self.modelTable.setIdList(self.select())

    def select(self, props=None):
        table = self.modelTable.table()
        groupId = self.currentGroupId()
        className = self.currentClass()
        cond = [table['group_id'].eq(groupId)]
        cond.append(table['deleted'].eq(0))
        cond.append(table['class'].eq(className))

        filterCond = self.filterConditions()
        if filterCond:
            cond.extend(filterCond)
        if self.activeActionTypeIdList:
            cond.append(table['id'].inlist(self.activeActionTypeIdList))
        list = QtGui.qApp.db.getIdList(table.name(),
                           'id',
                           cond,
                           self.order)
        self.lblCountRows.setText(formatRecordsCount(len(list)))
        return list

    def updateAvailableTreeIdList(self):
        table = self.modelTable.table()
        filterCond = self.filterConditions()
        cond = filterCond if filterCond else ['1']
        if self.activeActionTypeIdList:
            cond.append(table['id'].inlist(self.activeActionTypeIdList))
        list = QtGui.qApp.db.getIdList(table.name(),
                          'id',
                           cond)
        allList = QtGui.qApp.db.getTheseAndParents(table, 'group_id', list)
        self.modelTree.setAvailableItemIdList(allList)

    def getActiveActionTypeId(self):
        db = QtGui.qApp.db
        tableActionType = db.table('ActionType')
        tableService = db.table('rbService')

        queryTable = tableActionType.leftJoin(tableService, tableService['code'].eq(tableActionType['code']))

        cond = [db.joinOr([tableService['id'].isNull(),
                           tableService['endDate'].dateGe(QtCore.QDate.currentDate())]),
                tableActionType['deleted'].eq(0)]
        return db.getIdList(queryTable, tableActionType['id'], where=cond)

    def filterConditions(self):
        db = QtGui.qApp.db
        tables = [(db.table('ActionType_Service'), 'service_id'),
                  (db.table('ActionType_QuotaType'), 'quotaType_id'),
                  (db.table('ActionType_TissueType'), 'tissueType_id')]
        serviceId = self.cmbService.value()
        quotaTypeId = self.cmbQuotaType.value()
        tissueTypeId = self.cmbTissueType.value()

        tableActionType = db.table('ActionType')
        cond = []
        for idx, id in enumerate([serviceId, quotaTypeId, tissueTypeId]):
            table, fieldName = tables[idx]
            condTmp = [table['master_id'].eq(tableActionType['id'])]
            if id > 0:
                condTmp.append(table[fieldName].eq(id))
                cond.append(db.existsStmt(table, condTmp))
            elif id == -1:
                cond.append(db.existsStmt(table, condTmp))
            elif id == -2:
                cond.append(db.notExistsStmt(table, condTmp))

        serviceTypeIndex = self.cmbServiceType.currentIndex()
        if serviceTypeIndex:
            cond.append(self.modelTable.table()['serviceType'].eq(serviceTypeIndex-1))

        return cond

    def currentClass(self):
        return self.modelTree.itemClass(self.treeItems.currentIndex())

    def currentItem(self):
        return self.treeItems.currentIndex().internalPointer()

    def popupMenuAboutToShow(self):
        currentItemId = self.currentTreeItemId()
        self.actDelete.setEnabled(bool(currentItemId))

    def itemsPopupMenuAboutToShow(self):
        b = len(self.tblItems.selectedItemIdList()) > 1
        self.actGroupEditor.setEnabled(b)

    def currentTreeItemId(self):
        idx = self.treeItems.currentIndex()
        if idx.isValid():
            return self.modelTree.itemId(idx)
        return None

    def getItemEditor(self):
        return CActionTypeEditor(self)

    def duplicateCurrentRow(self):
        def duplicateCurrentInternal():
#            currentItemId = self.currentTreeItemId()
            currentItemId = self.tblItems.currentItemId()
            if currentItemId:
                db = QtGui.qApp.db
                tableActionType = db.table('ActionType')
                tableActionPropertyType = db.table('ActionPropertyType')
                tableActionTypeService = db.table('ActionType_Service')
                db.transaction()
                try:
                    recordActionType = db.getRecord(tableActionType, '*', currentItemId)
                    recordActionType.setNull('id')
                    currentCode = forceString(recordActionType.value('code'))
                    recordActionType.setValue('code', toVariant(currentCode+'_1'))
                    newItemId = db.insertRecord(tableActionType, recordActionType)
                    records = db.getRecordList(
                        tableActionPropertyType, '*',
                        tableActionPropertyType['actionType_id'].eq(currentItemId))
                    for record in records:
                        record.setNull('id')
                        record.setValue('actionType_id', toVariant(newItemId))
                        db.insertRecord(tableActionPropertyType, record)
                    records = db.getRecordList(
                        tableActionTypeService, '*',
                        tableActionTypeService['master_id'].eq(currentItemId))
                    for record in records:
                        record.setNull('id')
                        record.setValue('master_id', toVariant(newItemId))
                        db.insertRecord(tableActionTypeService, record)
                    db.commit()
                except:
                    db.rollback()
                    QtGui.qApp.logCurrentException()
                    raise
#                self.modelTree.update()
                self.renewListAndSetTo(newItemId)
        QtGui.qApp.call(self, duplicateCurrentInternal)

    def filterCmbCurrentIndexChanged(self):
        id = self.currentItemId()
        self.updateAvailableTreeIdList()
        self.findById(id)

    def getDefaultParams(self):
        prefs = getPref(QtGui.qApp.preferences.reportPrefs, 'RefBook_ActionType', {})
        self.chkActiveActionType.setChecked(getPrefBool(prefs, 'activeActionType', None))

    def saveDefaultParams(self):
        prefs = {}
        setPref(prefs, 'activeActionType', self.chkActiveActionType.isChecked())
        setPref(QtGui.qApp.preferences.reportPrefs, 'RefBook_ActionType', prefs)

    @QtCore.pyqtSlot(int)
    def on_cmbService_currentIndexChanged(self, index):
        self.filterCmbCurrentIndexChanged()

    @QtCore.pyqtSlot(int)
    def on_cmbQuotaType_currentIndexChanged(self, index):
        self.filterCmbCurrentIndexChanged()

    @QtCore.pyqtSlot(int)
    def on_cmbTissueType_currentIndexChanged(self, index):
        self.filterCmbCurrentIndexChanged()

    @QtCore.pyqtSlot(int)
    def on_cmbServiceType_currentIndexChanged(self, index):
        self.filterCmbCurrentIndexChanged()

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_treeItems_doubleClicked(self, index):
        item = self.currentItem()
        if not (item and item.isClass):
            itemId = item._id if item else None
            if itemId:
                dialog = self.getItemEditor()
                dialog.load(itemId)
                if dialog.exec_():
                    itemId = dialog.itemId()
#                        self.modelTree.update()
                    self.renewListAndSetTo(itemId)
            else:
                self.on_btnNew_clicked()

    @QtCore.pyqtSlot()
    def on_btnNew_clicked(self):
        dialog = self.getItemEditor()
        dialog.setClass(self.currentClass())
        dialog.setGroupId(self.currentGroupId())
        if dialog.exec_() :
            itemId = dialog.itemId()
#                self.modelTree.update()
            self.renewListAndSetTo(itemId)

    @QtCore.pyqtSlot()
    def on_actDelete_triggered(self):
        def deleteCurrentWithChilds(item):
            db = QtGui.qApp.db
            tableActionType = db.table('ActionType')
            if item:
                tree = self.tree_ids(item.id())
                if db.getCount(tableActionType, where=db.joinAnd((
                                                            tableActionType['id'].inlist(tree),
                                                            tableActionType['locked'].eq(1)  # upd 17.10.2016/i3418
                                                        ))) > 0 and not self.can_force_delete():
                    QtGui.QMessageBox.warning(self, u'Внимание!',
                                              u'Вы не имеете права на удаление одного или нескольких выбранных типов')
                    return
                for tree_id in tree:
                    record = db.getRecord(tableActionType, ['id', 'deleted'], tree_id)

                    record.setValue('deleted', QtCore.QVariant(1))
                    db.updateRecord(tableActionType, record)

        answer = QtGui.QMessageBox.question(self, u'Подтверждение удаления',
                                    u'Вы уверены, что хотите удалить данную группу действий?',
                                    QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                    QtGui.QMessageBox.No
                                    )
        if answer == QtGui.QMessageBox.Yes:
            currentIndex = self.treeItems.currentIndex()
            item = currentIndex.internalPointer()
            child = self.checkItemChilds(item)
            idx = self.modelTree.parent(currentIndex)
            self.saveExpandedState()
            rc = None
            if child:
                if QtGui.QMessageBox.question(self, u'Подтверждение удаления',
                                    u'Данная группа содержит элементы. \nУдаление группы приведет к удалению всех входящих в нее элементов. \nВыполнить удаление группы и всех входящих в нее элементов?(Количество элементов: %d)'%(child+1),
                                    QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
                                    QtGui.QMessageBox.No
                                    ) == QtGui.QMessageBox.Yes:
                    rc = self.delGroup(deleteCurrentWithChilds, item)
            else:
                rc = self.delGroup(deleteCurrentWithChilds, item)
            if rc:
                self.modelTree.reset()
                self.renewListAndSetTo()
                self.restoreExpandedState()
                self.treeItems.setCurrentIndex(idx)

    @QtCore.pyqtSlot(bool)
    def on_chkActiveActionType_toggled(self, checked):
        self.activeActionTypeIdList = self.getActiveActionTypeId() if checked else []
        self.updateAvailableTreeIdList()
        self.renewListAndSetToWithoutUpdate()
        self.saveDefaultParams()

    def delGroup(self, deleteCurrentWithChilds, item):
        return QtGui.qApp.call(self, deleteCurrentWithChilds,
                (item, ))[0]

    def checkItemChilds(self, item):
        count = 0
        list = item.items()
        for x in list:
            count += self.checkItemChilds(x)
        count += len(list)
        return count


class CActionTypeEditor(CItemEditorBaseDialog, Ui_ActionTypeEditorDialog):

    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'ActionType')
        self.parent = parent

        self.addModels('Specialities', CSpecialitiesModel(self))
        self.addModels('Properties', CPropertiesModel(self))
        self.addModels('ServiceByFinanceType', CServiceByFinanceTypeModel(self))
        self.addModels('QuotaType', CQuotaTypeModel(self))
        self.addModels('TissueType', CTissueTypeModel(self))

        self.actDuplicate = QtGui.QAction(u'Дублировать', self)

        self.actDuplicate.setObjectName('actDuplicate')
        self.actCopy = QtGui.QAction(u'Копировать выделенные свойства', self)
        self.actCopy.setObjectName('actCopy')

        self.setupUi(self)
        self.cmbAmountEvaluation.addItems(CActionType.amountEvaluation)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Тип действия')
        self.cmbGroup.setTable('ActionType')
        self.cmbNomenclativeService.setTable('rbService')
        self.cmbNomenclativeService.setShowFields(CRBComboBox.showCodeAndName)
        self.cmbQuotaType.setTable('QuotaType')
        self.cmbQuotaType.setShowFields(CRBComboBox.showCodeAndName)
        self.cmbPrescribedType.setTable('ActionType')
        self.cmbShedule.setTable('rbActionShedule')
        self.cmbCounter.setTable('rbCounter')
        self.on_cmbClass_currentIndexChanged(self.cmbClass.currentIndex())
        self.setupDirtyCather()

        self.tblActionSpecialities.setModel(self.modelSpecialities)
        self.tblActionSpecialities.addMoveRow()
        self.tblActionSpecialities.addPopupDelRow()

        # self.tblProperties.dragEnabled()
        # self.tblProperties.acceptDrops()
        # self.tblProperties.showDropIndicator()
        # self.tblProperties.setDragDropMode(QtGui.QAbstractItemView.InternalMove)

        self.tblProperties.setDragEnabled(True)
        self.tblProperties.setAcceptDrops(True)
        self.tblProperties.viewport().setAcceptDrops(True)
        self.tblProperties.setDragDropOverwriteMode(False)
        self.tblProperties.setDropIndicatorShown(True)

        self.tblProperties.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tblProperties.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblProperties.setDragDropMode(QtGui.QAbstractItemView.InternalMove)

        self.tblProperties.setModel(self.modelProperties)
        self.tblProperties.createPopupMenu(['-'])
        self.tblProperties.addPopupSelectAllRow()
        self.tblProperties.addPopupClearSelectionRow()
        self.tblProperties.popupMenu().addAction(self.actCopy)
        self.tblProperties.popupMenu().addSeparator()
        self.tblProperties.addMoveRow()
        self.tblProperties.addSpecialMoveRow()
        self.tblProperties.popupMenu().addAction(self.actDuplicate)
        self.tblProperties.popupMenu().addSeparator()
        self.tblProperties.addPopupDelRow()
        self.tblProperties.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tblProperties.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        self.tblServiceByFinanceType.setModel(self.modelServiceByFinanceType)
        self.tblServiceByFinanceType.addMoveRow()
        self.tblServiceByFinanceType.addPopupDelRow()

        self.tblQuotaType.setModel(self.modelQuotaType)
        self.tblQuotaType.addMoveRow()
        self.tblQuotaType.addPopupDelRow()

        self.tblTissueType.setModel(self.modelTissueType)
        self.tblTissueType.addPopupDelRow()

        self.cmbGroup.setEnabled(False)
        self.cmbClass.setEnabled(False)

        # Заполнение элементов комбобокса переведенными значениями из первоисточника
        self.cmbDefaultStatus.clear()
        self.cmbDefaultStatus.addItems(CActionType.retranslateClass(False).statusNames)

        self.addModels('ServiceType', CServiceTypeModel(1))
        self.cmbServiceType.setModel(self.modelServiceType)

        self.btnClearDefaultSetPerson.clicked.connect(self.clearCmbDefaultSetPerson)
        self.btnClearDefaultExecPerson.clicked.connect(self.clearCmbDefaultExecPerson)

        if QtGui.qApp.userHasRight(urAdmin):
            self.lblLock.setEnabled(True)
            self.chkLock.setEnabled(True)

        self.tblPostsFilter.setTable('rbPost')
        self.tblPostsFilter.setDisabled(True)
        self.tblSpecialitiesFilter.setTable('rbSpeciality')
        self.tblSpecialitiesFilter.setDisabled(True)

    def clearCmbDefaultSetPerson(self):
        self.cmbDefaultSetPerson.setValue(None)

    def clearCmbDefaultExecPerson(self):
        self.cmbDefaultExecPerson.setValue(None)

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(   self.edtCode,                      record, 'code')
        setLineEditValue(   self.edtName,                      record, 'name')
        setLineEditValue(   self.edtTitle,                     record, 'title')
        setLineEditValue(   self.edtFlatCode,                  record, 'flatCode')
        setCheckBoxValue(   self.chkIsMES,                     record, 'isMES')
        setCheckBoxValue(   self.chkIsPreferable,              record, 'isPreferable')
        setRBComboBoxValue( self.cmbNomenclativeService,       record, 'nomenclativeService_id')
        setRBComboBoxValue( self.cmbPrescribedType,            record, 'prescribedType_id')
        setRBComboBoxValue( self.cmbShedule,                   record, 'shedule_id')
        setComboBoxValue(   self.cmbServiceType,               record, 'serviceType')
        setComboBoxValue(   self.cmbSex,                       record, 'sex')
        setCheckBoxValue(   self.chkNomenclatureExpense,       record, 'isNomenclatureExpense')
        setComboBoxValue(   self.cmbDefaultStatus,             record, 'defaultStatus')
        setComboBoxValue(   self.cmbDefaultDirectionDate,      record, 'defaultDirectionDate')
        setComboBoxValue(   self.cmbDefaultBeginDate,          record, 'defaultBeginDate')
        setComboBoxValue(   self.cmbDefaultPlannedEndDate,     record, 'defaultPlannedEndDate')
        setComboBoxValue(   self.cmbDefaultEndDate,            record, 'defaultEndDate')
        setRBComboBoxValue( self.cmbDefaultExecPerson,         record, 'defaultExecPerson_id')
        setComboBoxValue(   self.cmbDefaultPersonInEvent,      record, 'defaultPersonInEvent')
        setComboBoxValue(   self.cmbDefaultPersonInEditor,     record, 'defaultPersonInEditor')
        setComboBoxValue(   self.cmbDefaultMKB,                record, 'defaultMKB')
        setComboBoxValue(   self.cmbDefaultMorphology,         record, 'defaultMorphology')
        setComboBoxValue(   self.cmbDefaultMES,                record, 'defaultMES')
        setComboBoxValue(   self.cmbIsMorphologyRequired,      record, 'isMorphologyRequired')
        setLineEditValue(   self.edtOffice,                    record, 'office')
        setSpinBoxValue(    self.edtActualAppointmentDuration, record, 'actualAppointmentDuration')
        setCheckBoxValue(   self.chkShowInForm,                record, 'showInForm')
        setCheckBoxValue(   self.chkGenTimetable,              record, 'genTimetable')
        setCheckBoxValue(   self.chkShowTime,                  record, 'showTime')
        setCheckBoxValue(   self.chkShowAPOrg,                 record, 'showAPOrg')
        setCheckBoxValue(   self.chkShowAPNotes,                 record, 'showAPNotes')
        setCheckBoxValue(   self.chkRequiredCoordination,      record, 'isRequiredCoordination')
        setComboBoxValue(   self.cmbAssistantRequired,         record, 'hasAssistant')
        setCheckBoxValue(   self.chkIsPrinted,                 record, 'isPrinted')
        self.edtContext.setEnabled(self.chkIsPrinted.isChecked())
        self.lblContext.setEnabled(self.chkIsPrinted.isChecked())
        setLineEditValue(   self.edtContext,                    record, 'context')
        setSpinBoxValue(    self.edtAmount,                     record, 'amount')
        setComboBoxValue(   self.cmbAmountEvaluation,           record, 'amountEvaluation')
        setSpinBoxValue(    self.edtMaxOccursInEvent,           record, 'maxOccursInEvent')
        setCheckBoxValue(   self.chkPropertyAssignedVisible,    record, 'propertyAssignedVisible')
        setCheckBoxValue(   self.chkPropertyUnitVisible,        record, 'propertyUnitVisible')
        setCheckBoxValue(   self.chkPropertyNormVisible,        record, 'propertyNormVisible')
        setCheckBoxValue(   self.chkPropertyEvaluationVisible,  record, 'propertyEvaluationVisible')
        setCheckBoxValue(   self.chkIsSubstituteEndDateToEvent, record, 'isSubstituteEndDateToEvent')
        setCheckBoxValue(   self.chkIsCustomSum,                record, 'isCustomSum')
        setComboBoxValue(   self.cmbClass,                      record, 'class')
        setSpinBoxValue(    self.edtRecommendationExpirePeriod, record, 'recommendationExpirePeriod')
        setCheckBoxValue(   self.chkRecommendationControl,      record, 'recommendationControl')
        setCheckBoxValue(   self.chkExecRequiredForEventExec,   record, 'isExecRequiredForEventExec')
        setCheckBoxValue(   self.chkIgnoreEventExecDate,        record, 'isIgnoreEventExecDate')

        setSpinBoxValue(self.edtFrequencyCount, record, 'frequencyCount')
        setSpinBoxValue(self.edtFrequencyPeriod, record, 'frequencyPeriod')
        setComboBoxValue(self.cmbFrequencyPeriodType, record, 'frequencyPeriodType')
        setCheckBoxValue(self.chkStrictFrequency, record, 'isStrictFrequency')
        setCheckBoxValue(self.chkFrequencyPeriodByCalendar, record, 'isFrequencyPeriodByCalendar')
        setRBComboBoxValue(self.cmbCounter, record, 'counter_id')

        setCheckBoxValue(self.chkLock, record, 'locked')
        setCheckBoxValue(self.chkFilledLock, record, 'filledLock')

        self.on_cmbClass_currentIndexChanged(self.cmbClass.currentIndex())
        setRBComboBoxValue( self.cmbGroup,                     record, 'group_id')
        self.cmbDefaultOrg.setValue(forceRef(record.value('defaultOrg_id')))
        (begUnit, begCount, endUnit, endCount) = parseAgeSelector(forceString(record.value('age')))
        self.cmbBegAgeUnit.setCurrentIndex(begUnit)
        self.edtBegAgeCount.setText(str(begCount))
        self.cmbEndAgeUnit.setCurrentIndex(endUnit)
        self.edtEndAgeCount.setText(str(endCount))

        self.modelSpecialities.loadItems(self.itemId())
        self.modelProperties.loadItems(self.itemId())
        setRBComboBoxValue( self.cmbQuotaType,      record, 'quotaType_id')
        self.modelServiceByFinanceType.loadItems(self.itemId())
        self.modelQuotaType.loadItems(self.itemId())
        self.modelTissueType.loadItems(self.itemId())

        setCheckBoxValue(self.chkPostsFilter, record, 'filterPosts')
        self.tblPostsFilter.setValues(QtGui.qApp.db.getIdList('ActionType_PersonPost', 'post_id',
                                                              'actionType_id = %d' % self.itemId()))
        setCheckBoxValue(self.chkSpecialitiesFilter, record, 'filterSpecialities')
        self.tblSpecialitiesFilter.setValues(QtGui.qApp.db.getIdList('ActionType_PersonSpeciality', 'speciality_id',
                                                                     'actionType_id = %d' % self.itemId()))
        self.setIsDirty(False)

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(   self.edtCode,                      record, 'code')
        getLineEditValue(   self.edtName,                      record, 'name')
        getLineEditValue(   self.edtTitle,                     record, 'title')
        getComboBoxValue(   self.cmbClass,                     record, 'class')
        getRBComboBoxValue( self.cmbGroup,                     record, 'group_id')
        getLineEditValue(   self.edtFlatCode,                  record, 'flatCode')
        getCheckBoxValue(   self.chkIsMES,                     record, 'isMES')
        getCheckBoxValue(   self.chkIsPreferable,              record, 'isPreferable')
        getRBComboBoxValue( self.cmbNomenclativeService,       record, 'nomenclativeService_id')
        getRBComboBoxValue( self.cmbPrescribedType,            record, 'prescribedType_id')
        getRBComboBoxValue( self.cmbShedule,                   record, 'shedule_id')
        getComboBoxValue(   self.cmbServiceType,               record, 'serviceType')
        getComboBoxValue(   self.cmbSex,                       record, 'sex')
        getCheckBoxValue(   self.chkNomenclatureExpense,       record, 'isNomenclatureExpense')
        getComboBoxValue(   self.cmbDefaultStatus,             record, 'defaultStatus')
        getComboBoxValue(   self.cmbDefaultDirectionDate,      record, 'defaultDirectionDate')
        getComboBoxValue(self.cmbDefaultBeginDate, record, 'defaultBeginDate')
        getComboBoxValue(   self.cmbDefaultPlannedEndDate,     record, 'defaultPlannedEndDate')
        getComboBoxValue(   self.cmbDefaultEndDate,            record, 'defaultEndDate')
        getRBComboBoxValue( self.cmbDefaultExecPerson,         record, 'defaultExecPerson_id')
        getComboBoxValue(   self.cmbDefaultPersonInEvent,      record, 'defaultPersonInEvent')
        getComboBoxValue(   self.cmbDefaultPersonInEditor,     record, 'defaultPersonInEditor')
        getComboBoxValue(   self.cmbDefaultMKB,                record, 'defaultMKB')
        getComboBoxValue(   self.cmbDefaultMorphology,         record, 'defaultMorphology')
        getComboBoxValue(   self.cmbDefaultMES,                record, 'defaultMES')
        getComboBoxValue(   self.cmbIsMorphologyRequired,      record, 'isMorphologyRequired')
        getLineEditValue(   self.edtOffice,                    record, 'office')
        getSpinBoxValue(    self.edtActualAppointmentDuration, record, 'actualAppointmentDuration')
        getCheckBoxValue(   self.chkShowInForm,                record, 'showInForm')
        getCheckBoxValue(   self.chkGenTimetable,              record, 'genTimetable')
        getCheckBoxValue(   self.chkShowTime,                  record, 'showTime')
        getCheckBoxValue(   self.chkShowAPOrg,                 record, 'showAPOrg')
        getCheckBoxValue(   self.chkShowAPNotes,                 record, 'showAPNotes')
        getCheckBoxValue(   self.chkRequiredCoordination,      record, 'isRequiredCoordination')
        getComboBoxValue(   self.cmbAssistantRequired,         record, 'hasAssistant')
        getCheckBoxValue(   self.chkIsPrinted,                 record, 'isPrinted')
        getLineEditValue(   self.edtContext,                   record, 'context')
        getSpinBoxValue(    self.edtAmount,                    record, 'amount')
        getComboBoxValue(   self.cmbAmountEvaluation,          record, 'amountEvaluation')
        getSpinBoxValue(    self.edtMaxOccursInEvent,          record, 'maxOccursInEvent')
        getRBComboBoxValue( self.cmbQuotaType,                 record, 'quotaType_id')
        getCheckBoxValue(   self.chkPropertyAssignedVisible,   record, 'propertyAssignedVisible')
        getCheckBoxValue(   self.chkPropertyUnitVisible,       record, 'propertyUnitVisible')
        getCheckBoxValue(   self.chkPropertyNormVisible,       record, 'propertyNormVisible')
        getCheckBoxValue(   self.chkPropertyEvaluationVisible, record, 'propertyEvaluationVisible')
        getCheckBoxValue(   self.chkIsSubstituteEndDateToEvent, record, 'isSubstituteEndDateToEvent')
        getCheckBoxValue(   self.chkIsCustomSum,                record, 'isCustomSum')
        getSpinBoxValue(    self.edtRecommendationExpirePeriod, record, 'recommendationExpirePeriod')
        getCheckBoxValue(   self.chkRecommendationControl,      record, 'recommendationControl')
        getCheckBoxValue(   self.chkExecRequiredForEventExec,   record, 'isExecRequiredForEventExec')
        getCheckBoxValue(   self.chkIgnoreEventExecDate,        record, 'isIgnoreEventExecDate')

        getSpinBoxValue(self.edtFrequencyCount, record, 'frequencyCount')
        getSpinBoxValue(self.edtFrequencyPeriod, record, 'frequencyPeriod')
        getComboBoxValue(self.cmbFrequencyPeriodType, record, 'frequencyPeriodType')
        getCheckBoxValue(self.chkStrictFrequency, record, 'isStrictFrequency')
        getCheckBoxValue(self.chkFrequencyPeriodByCalendar, record, 'isFrequencyPeriodByCalendar')
        getRBComboBoxValue(self.cmbCounter, record, 'counter_id')

        getCheckBoxValue(self.chkLock, record, 'locked')
        getCheckBoxValue(self.chkFilledLock, record, 'filledLock')

        record.setValue('defaultOrg_id', QtCore.QVariant(self.cmbDefaultOrg.value()))

        record.setValue('age',        toVariant(composeAgeSelector(
                    self.cmbBegAgeUnit.currentIndex(),  forceStringEx(self.edtBegAgeCount.text()),
                    self.cmbEndAgeUnit.currentIndex(),  forceStringEx(self.edtEndAgeCount.text())
                        )))

        getCheckBoxValue(self.chkPostsFilter, record, 'filterPosts')
        getCheckBoxValue(self.chkSpecialitiesFilter, record, 'filterSpecialities')

        return record

    def afterSave(self):
        CActionTypeCache.purge()

    def saveInternals(self, id):
        self.modelSpecialities.saveItems(id)
        self.modelProperties.saveItems(id)
        self.modelServiceByFinanceType.saveItems(id)
        self.modelQuotaType.saveItems(id)
        self.modelTissueType.saveItems(id)

        if self.itemId():
            QtGui.qApp.db.deleteRecord('ActionType_PersonPost', 'actionType_id = %d' % self.itemId())
            QtGui.qApp.db.insertMultipleFromDict('ActionType_PersonPost', [{
                'actionType_id': self.itemId(),
                'post_id': pid
            } for pid in self.tblPostsFilter.values()])
            QtGui.qApp.db.deleteRecord('ActionType_PersonSpeciality', 'actionType_id = %d' % self.itemId())
            QtGui.qApp.db.insertMultipleFromDict('ActionType_PersonSpeciality', [{
                'actionType_id': self.itemId(),
                'speciality_id': sid
            } for sid in self.tblSpecialitiesFilter.values()])

    def setClass(self, _class):
        self.cmbClass.setCurrentIndex(_class)

    def setGroupId(self, groupId):
        self.cmbGroup.setValue(groupId)

    def checkDataEntered(self):
        result = CItemEditorBaseDialog.checkDataEntered(self)
        result = result and self.checkPropertiesDataEntered()
        result = result and self.checkActionsInSimilarity()
        return result

    def checkActionsInSimilarity(self):
        if self.itemId():
            itemId = self.itemId()
            firstList = QtGui.qApp.db.getIdList('rbActionTypeSimilarity', 'firstActionType_id', where=['secondActionType_id = %s' % self.itemId(), 'similarityType=0'])
            secondList = QtGui.qApp.db.getIdList('rbActionTypeSimilarity', 'secondActionType_id', where=['firstActionType_id = %s' % self.itemId(), 'similarityType=0'])
            currentActionType = CActionType(self.getRecord())
            currentActionType.initPropertiesByRecords(self.modelProperties.items(), clear=True)
            differentActionTypesNames = []
            differentActionTypes = []
            for atId in firstList:
                actionType = CActionTypeCache.getById(atId)
                if not currentActionType.isSimilar(actionType):
                    differentActionTypesNames.append(actionType.name)
                    differentActionTypes.append((atId, itemId))
            for atId in secondList:
                actionType = CActionTypeCache.getById(atId)
                if not currentActionType.isSimilar(actionType):
                    differentActionTypesNames.append(actionType.code + ' | ' + actionType.name)
                    differentActionTypes.append((itemId, atId))
            if differentActionTypesNames:
                message = u'Текущий тип действия имеет схожие типы. После внесенных изменений требования схожести ' \
                          u'перестали выполняться для следующих типов действий: <ul>%s</ul><br>Удалить связь с указанными типами ' \
                          u'действий?' % u''.join(u'<li>%s</li>' % atName for atName in differentActionTypesNames)
                result = QtGui.QMessageBox.warning(self, u'Внимание!', message,
                                        QtGui.QMessageBox.Yes|QtGui.QMessageBox.Cancel,
                                        QtGui.QMessageBox.Cancel)
                if result == QtGui.QMessageBox.Yes:
                    for firstATid, secondATid in differentActionTypes:
                        QtGui.qApp.db.deleteRecord('rbActionTypeSimilarity', 'similarityType=0 AND firstActionType_id = %s AND secondActionType_id = %s' % (firstATid, secondATid))
                    return True
                return False
        return True

    def checkPropertiesDataEntered(self):
        for row, item in enumerate(self.modelProperties.items()):
            if not self.checkPropertyDataEntered(row, item):
                return False
        return True

    def checkPropertyDataEntered(self, row, item):
        name = forceString(item.value('name'))
        typeName = forceString(item.value('typeName'))

        result = name or self.checkInputMessage(u'наименование свойства', False, self.tblProperties, row, item.indexOf('name'))
        result = result and (typeName or self.checkInputMessage(u'тип свойства', False, self.tblProperties, row, item.indexOf('typeName')))
        return result

    @QtCore.pyqtSlot()
    def on_btnSelectService_clicked(self):
        serviceId = selectService(self, self.cmbNomenclativeService)
        self.cmbNomenclativeService.update()
        if serviceId:
            self.cmbNomenclativeService.setValue(serviceId)

    @QtCore.pyqtSlot(int)
    def on_cmbNomenclativeService_currentIndexChanged(self, index):
        self.btnSetName.setEnabled(bool(self.cmbNomenclativeService.value()))

    @QtCore.pyqtSlot()
    def on_btnSetName_pressed(self):
        index = self.cmbNomenclativeService.currentIndex()
        name = self.cmbNomenclativeService.model().getName(index)
        self.edtName.setText(name)
        self.edtTitle.setText(name)

    @QtCore.pyqtSlot(int)
    def on_cmbClass_currentIndexChanged(self, classCode):
        actionFilter = 'class=%d and deleted = 0' % classCode
        self.cmbGroup.setFilter(actionFilter)
        self.cmbPrescribedType.setFilter(actionFilter)

    @QtCore.pyqtSlot(int)
    def on_cmbPrescribedType_currentIndexChanged(self, index):
        self.cmbShedule.setEnabled(bool(self.cmbPrescribedType.value()))

    @QtCore.pyqtSlot()
    def on_actDuplicate_triggered(self):
        def getUniqueName(number, name, items):
            for x in items:
                if u'%s_%s' % (name, str(number)) == forceString(x.value('name')):
                    return getUniqueName(number + 1, name, items)
            return u'%s_%s' % (name, str(number))

        index = self.tblProperties.currentIndex()
        row = index.row()
        items = self.modelProperties.items()
        if 0<=row<len(items):
            newItem = QtSql.QSqlRecord(items[row])
            newItem.setValue('id', QtCore.QVariant())

            oldName = forceString(newItem.value('name'))

            newItem.setValue('name', QtCore.QVariant(getUniqueName(1, oldName, items)))
            self.modelProperties.insertRecord(row+1, newItem)

    @QtCore.pyqtSlot()
    def on_actCopy_triggered(self):
        rows = self.tblProperties.getSelectedRows()

        if rows:
            strList = ','.join(forceString(self.modelProperties.value(row, 'id')) for row in rows)
            mimeData = QtCore.QMimeData()
            v = toVariant(strList)
            mimeData.setData(self.parent.mimeTypeActionPropertyIdList, v.toByteArray())
            QtGui.qApp.clipboard().setMimeData(mimeData)
            self.parent.actPasteProperties.setEnabled(True)

    @QtCore.pyqtSlot()
    def on_actSelectAll_triggered(self):
        self.tblProperties.selectAll()

    @QtCore.pyqtSlot()
    def on_actClearSelection_triggered(self):
        self.tblProperties.clearSelection()


class CActionPropertyTemplateCol(CInDocTableCol):
    tableName = 'ActionPropertyTemplate'

    def toString(self, val, record):
        cache = CRBModelDataCache.getData(self.tableName, True)
        id = forceRef(val)
        if id:
            text = cache.getStringById(id, CRBComboBox.showName)
        else:
            text = ''
        return toVariant(text)

    def toStatusTip(self, val, record):
        cache = CRBModelDataCache.getData(self.tableName, True)
        id = forceRef(val)
        if id:
            code = cache.getStringById(id, CRBComboBox.showCode)
            name = cache.getStringById(id, CRBComboBox.showName)
            text = name + ' ('+code+')'
        else:
            text = ''
        return toVariant(text)

    def createEditor(self, parent):
        editor = CActionPropertyTemplateComboBox(parent)
        return editor

    def setEditorData(self, editor, value, record):
        editor.setValue(forceRef(value))

    def getEditorData(self, editor):
        return toVariant(editor.value())


class CSpecialitiesModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'ActionType_Speciality', 'id', 'master_id', parent)
        self.addCol(CRBInDocTableCol(u'Специальность', 'speciality_id', 10, 'rbSpeciality', addNone = False))


class CPropertiesModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'ActionPropertyType', 'id', 'actionType_id', parent)
        self.addCol(CActionPropertyTemplateCol(u'Шаблон', 'template_id', 40))
        self.addCol(CInDocTableCol(u'Наименование', 'name', 12))
        self.addCol(CInDocTableCol(u'Короткое наименование', 'shortName', 16, maxLength=16))
        self.addCol(CRBInDocTableCol(u'Профиль прав', 'userProfile_id', 16, 'rbUserProfile'))
        self.addCol(CEnumInDocTableCol(u'Если нет прав', 'userProfileBehaviour', 16, [u'Отключать редакт-е',
                                                                                      u'Скрывать'],
                                       toolTip=u'Определяет, что делать со свойством, если у пользователя нет выбранного профиля прав'))
        self.addCol(CInDocTableCol(u'Описание', 'descr', 12))
        self.addCol(CRBInDocTableCol(u'Ед.изм.', 'unit_id', 6, 'rbUnit', isRTF=True))
        self.addCol(CBoolInDocTableCol(u'Закреплено', 'isFrozen', 10))
        self.addCol(CBoolInDocTableCol(u'Редактируем (конструктор)', 'typeEditable', 10))
        self.addCol(CSelectStrInDocTableCol(u'Тип', 'typeName', 9, CActionPropertyValueTypeRegistry.nameList))
        self.addCol(CInDocTableCol(u'Область', 'valueDomain', 12))
        self.addCol(CInDocTableCol(u'Штраф', 'penalty', 4))
        self.addCol(CInDocTableCol(u'Значение по умолчанию', 'defaultValue', 25))
        self.addCol(CBoolInDocTableCol(u'Вектор', 'isVector', 6))
        self.addCol(CInDocTableCol(u'Норматив', 'norm', 12))
        self.addCol(CEnumInDocTableCol(u'Пол', 'sex', 5, SexList))
        self.addCol(CInDocTableCol(u'Возраст', 'age', 12))
        self.addCol(CBoolInDocTableCol(u'Видимость при выполнении работ', 'visibleInJobTicket', 12))
        self.addCol(CEnumInDocTableCol(u'Видимость в табличном редакторе', 'visibleInTableRedactor', 12, [u'Не видно',
                                                                                                          u'Режим редактирования',
                                                                                                          u'Без редактирования']))
        self.addCol(CEnumInDocTableCol(u'Право редактирования', 'canChangeOnlyOwner', 12, [u'Все',
                                                                                           u'Назначивший действие',
                                                                                           u'Никто']))
        self.addCol(CBoolInDocTableCol(u'Назначаемый', 'isAssignable', 6))
        self.addCol(CRBInDocTableCol(u'Тест', 'test_id', 20, 'rbTest', showFields=CRBComboBox.showNameAndCode))
        self.addCol(CEnumInDocTableCol(u'Оценка', 'defaultEvaluation', 10, [u'не определять',
                                                                            u'автомат',
                                                                            u'полуавтомат',
                                                                            u'ручное']))
        self.addCol(CEnumInDocTableCol(u'Модификатор копирования', 'copyModifier', 10, ActionPropertyCopyModifier.getNameList()))
        self.addCol(CBoolInDocTableCol(u'Задаёт наименование действия', 'isActionNameSpecifier', 10))
        self.addCol(CInDocTableCol(u'Лаб. Калькулятор', 'laboratoryCalculator', 5))
        self.addCol(CEnumInDocTableCol(u'В таблице выбираемых Действий', 'inActionsSelectionTable', 15, [u'Не определено',
                                                                                                         u'Recipe',
                                                                                                         u'Doses',
                                                                                                         u'Signa']))
        self.addCol(CIntInDocTableCol(u'Коэффициент размера', 'redactorSizeFactor', 10, low=-5, high=5))
        self.addCol(CBoolInDocTableCol(u'Видимость в DR', 'visibleInDR', 12))

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        result = CInDocTableModel.setData(self, index, value, role)
        if result and role == QtCore.Qt.EditRole:
            column = index.column()
            row = index.row()
            if column == self.getColIndex('template_id'):
                nameIdx = self.getColIndex('name')
                name     = forceStringEx(self.data(index.sibling(row, nameIdx)))
                if not name:
                    shortNameIdx = self.getColIndex('shortName')
                    template = forceStringEx(self.data(index))
                    CInDocTableModel.setData(self, index.sibling(row, nameIdx), QtCore.QVariant(template))
                    CInDocTableModel.setData(self, index.sibling(row, shortNameIdx), QtCore.QVariant(template))
                    self.emitCellChanged(row, nameIdx)
                    self.emitCellChanged(row, shortNameIdx)
        return result


class CServiceByFinanceTypeModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'ActionType_Service', 'id', 'master_id', parent)
        self.addCol(CRBInDocTableCol(   u'Тип финансирования', 'finance_id', 15, 'rbFinance'))
        self.addCol(CRBInDocTableCol(   u'Услуга',             'service_id', 15, 'rbService', showFields=CRBComboBox.showNameAndCode))


class CQuotaTypeModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'ActionType_QuotaType', 'id', 'master_id', parent)
        self.addCol(CRBInDocTableCol(   u'Тип финансирования',  'finance_id',   15, 'rbFinance'))
        self.addCol(CEnumInDocTableCol( u'Класс квоты',           'quotaClass', 10, [u'ВТМП']))
        self.addCol(CRBInDocTableCol(   u'Вид квоты',           'quotaType_id', 15, 'QuotaType'))


class CTissueTypeModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'ActionType_TissueType', 'id', 'master_id', parent)
        self.addCol(CRBInDocTableCol(u'Тип биоматериала', 'tissueType_id', 15, 'rbTissueType'))
        self.addCol(CIntInDocTableCol(u'Количество', 'amount', 10))
        self.addCol(CRBInDocTableCol(u'Ед. измерения', 'unit_id', 13, 'rbUnit', isRTF=True))
        self.addCol(CRBInDocTableCol(u'Тип контейнера', 'containerType_id', 10, 'rbContainerType', showFields=CRBComboBox.showNameAndCode))
        self.addCol(CActionTypeActiveGroupInDocTableCol(u'Главное действие', 'isActiveGroup', 10))
        self._parent = parent
        db = QtGui.qApp.db
        tableAT = db.table('ActionType_TissueType')
        tableActionType = db.table('ActionType')
        table = tableAT.innerJoin(tableActionType, [tableAT['master_id'].eq(tableActionType['id'])])
        records = db.getRecordList(table, [tableAT['master_id'].name(), tableAT['tissueType_id'].name(),
                                           tableActionType['name'].name(), tableActionType['code'].name()],
                                   [tableAT['isActiveGroup'].eq(1)])
        self.cacheMainActionsByTissueType = dict([(forceRef(record.value('tissueType_id')),
                                                   (forceRef(record.value('master_id')),
                                                    forceString(record.value('code')),
                                                    forceString(record.value('name')))) for record in records])

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        column = index.column()
        row = index.row()
        if role == QtCore.Qt.CheckStateRole and column == self.getColIndex('isActiveGroup'):
            record = self._items[row]
            currentTissueType = forceRef(record.value('tissueType_id'))
            currentActionType = forceRef(record.value('master_id'))
            if forceBool(value):
                mainActionTypeForCurrentTissueType = self.cacheMainActionsByTissueType.get(currentTissueType, None)
                if mainActionTypeForCurrentTissueType:
                    mainActionTypeId, mainActionTypeCode, mainActionTypeName = mainActionTypeForCurrentTissueType
                    if mainActionTypeId != currentActionType:
                        answer = QtGui.QMessageBox.warning(self._parent,
                                               u'Внимание!',
                                               u'Тип действия %s "%s" уже выбран главным. Заменить на текущий?' % (mainActionTypeCode,
                                                                                                                  mainActionTypeName),
                                               QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel,
                                               QtGui.QMessageBox.Cancel)
                        if answer == QtGui.QMessageBox.Ok:
                            self.updateMainActionType(currentActionType, currentTissueType)
                        else:
                            return False
                else:
                    self.updateMainActionType(currentActionType, currentTissueType)

        return CInDocTableModel.setData(self, index, value, role)

    def updateMainActionType(self, currentActionType, currentTissueType):
        db = QtGui.qApp.db
        table = db.table('ActionType_TissueType')
        db.updateRecords(table, [table['isActiveGroup'].eq(0)], [table['tissueType_id'].eq(currentTissueType)])
        db.updateRecords(table, [table['isActiveGroup'].eq(1)],
                         [table['master_id'].eq(currentActionType), table['tissueType_id'].eq(currentTissueType)])
        self.cacheMainActionsByTissueType[currentTissueType] = ()


class CFindDialog(CDialogBase, Ui_ActionTypeFindDialog):
    def __init__(self, parent):

        cols = [CEnumCol(   u'Класс',              ['class'], [u'статус', u'диагностика', u'лечение', u'прочие мероприятия', u'анализы'], 10),
                CTextCol(   u'Код',                ['code'], 20),
                CTextCol(   u'Наименование',       ['name'], 40),
                CRefBookCol(u'Номенклатурный код', ['nomenclativeService_id'], 'rbService', 10, 2),
                CRefBookCol(u'Группа',             ['group_id'], 'ActionType', 10)]

        CDialogBase.__init__(self, parent)
        self.addModels('ActionTypeFound', CTableModel(self, cols, 'ActionType'))

        self.setupUi(self)

        self.setModels(self.tblActionTypeFound,   self.modelActionTypeFound, self.selectionModelActionTypeFound)

        self.cmbService.setTable('rbService')
        self.cmbTissueType.setTable('rbTissueType')
        self.setWindowTitle(u'Поиск типа действия')

        self.foundId = None
        self.props = {}

        self.tableActionType = QtGui.qApp.db.table('ActionType')
        self.tableService    = QtGui.qApp.db.table('rbService')

        self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setShortcut(QtCore.Qt.Key_Return)
        self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setDefault(True)

    def id(self):
        return self.foundId

    def findActionType(self):
        tableActionType  = self.tableActionType
        tableService     = self.tableService
        code             = forceStringEx(self.edtCode.text())
        # lisCode          = forceStringEx(self.edtLisCode.text())
        nomenclativeCode = forceStringEx(self.edtNomenclativeCode.text())
        name             = forceStringEx(self.edtName.text())
        tissyeTypeId     = self.cmbTissueType.value()
        serviceId        = self.cmbService.value()

        table = tableActionType
        cond = [tableActionType['deleted'].eq(0)]
        if code:
            cond.append(tableActionType['code'].like(addDotsEx(code)))
        if name:
            cond.append(tableActionType['name'].like(addDotsEx(name)))
        if nomenclativeCode:
            cond.append(tableService['code'].like(addDotsEx(nomenclativeCode)))
            table = tableActionType.innerJoin(tableService, tableActionType['nomenclativeService_id'].eq(tableService['id']))
        if tissyeTypeId:
            cond.append('EXISTS (SELECT id FROM ActionType_TissueType WHERE master_id=ActionType.`id` AND tissueType_id=%d)'%tissyeTypeId)
        if serviceId:
            cond.append('EXISTS (SELECT * FROM ActionType_Service WHERE master_id=ActionType.`id` AND service_id=%d)'%serviceId)
        idList = QtGui.qApp.db.getIdList(table, 'ActionType.`id`', cond, 'ActionType.`class`, ActionType.`code`, ActionType.`name`')
        idCount = len(idList)
        self.tblActionTypeFound.setIdList(idList)
        self.lblRecordsCount.setText(formatRecordsCount(idCount))
        if idCount == 0:
            self.setFocusToWidget(self.edtCode)
        elif idCount == 1:
            self.foundId = idList[0]
            self.accept()

    def setProps(self, props):
        self.props = props
        self.edtCode.setText(props.get('code', ''))
        # self.edtLisCode.setText(props.get('lisCode', ''))
        self.edtNomenclativeCode.setText(props.get('nomenclativeCode', ''))
        self.edtName.setText(props.get('name', ''))
        self.cmbTissueType.setValue(props.get('tissueType', None))
        self.cmbService.setValue(props.get('service', None))

    def getProps(self):
        return self.props

    def saveProps(self):
        self.props['code'] = forceStringEx(self.edtCode.text())
        # self.props['lis_code'] = forceStringEx(self.edtLisCode.text())
        self.props['nomenclativeCode'] = forceStringEx(self.edtNomenclativeCode.text())
        self.props['name'] = forceStringEx(self.edtName.text())
        self.props['tissueType'] = self.cmbTissueType.value()
        self.props['service'] = self.cmbService.value()

    def resetFindingValues(self):
        self.edtCode.clear()
        # self.edtLisCode.clear()
        self.edtNomenclativeCode.clear()
        self.edtName.clear()
        self.cmbTissueType.setValue(None)
        self.cmbService.setValue(None)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblActionTypeFound_doubleClicked(self, index=None):
        index = self.tblActionTypeFound.currentIndex()
        self.foundId = self.tblActionTypeFound.itemId(index)
        self.accept()

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Close:
            self.reject()
        elif buttonCode == QtGui.QDialogButtonBox.Apply:
            self.saveProps()
            self.findActionType()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.resetFindingValues()

    @QtCore.pyqtSlot()
    def on_btnSelectService_clicked(self):
        serviceId = selectService(self, self.cmbService)
        self.cmbService.update()
        if serviceId:
            self.cmbService.setValue(serviceId)


class CActionTypeActiveGroupInDocTableCol(CBoolInDocTableCol):

    def __init__(self, title, fieldName, width, **params):
        CBoolInDocTableCol.__init__(self, title, fieldName, width, **params)


class CMasterInDocTableCol(CBackRelationInDockTableCol):

    def __init__(self,
                 interfaceCol,
                 foreignKey,
                 surrogateFieldName,
                 subTableName,
                 subTablePrimaryKey,
                 parentModel,
                 **params):
        super(CMasterInDocTableCol, self).__init__(interfaceCol,
                                                   foreignKey,
                                                   surrogateFieldName,
                                                   subTableName,
                                                   subTablePrimaryKey,
                                                   [],
                                                   None,
                                                   **params)
        self._parentModel = parentModel

    def saveExternalData(self, rowRecord):
        subRecord = self._parentModel.getRecord()
        #masterId = forceRef(rowRecord.value(self._primaryKey))
        value = rowRecord.value(self._surrogateFieldName)
        #subRecord = self._getSubRecord(masterId)
       # rowRecord
        rowRecord.setValue(self._subCol.fieldName(), value)

        #subRecord.setValue(self._subTableForeignKey, QtCore.QVariant(masterId))
        subRecordId = QtGui.qApp.db.insertOrUpdate(self._subTable, subRecord)
        #subRecord.setValue(self._subTable.idField().name(), QtCore.QVariant(subRecordId))


class CMainActionTypeInDocTable(CBoolInDocTableCol):

    def __init__(self, title, fieldName, width, parent, **params):
        CBoolInDocTableCol.__init__(self, title, fieldName, width, **params)
        self._parent = parent
        self.state = None

    def flags(self, index=None):
        result = CInDocTableCol.flags(self)
        if result & QtCore.Qt.ItemIsEditable:
            result = (result & ~QtCore.Qt.ItemIsEditable) | QtCore.Qt.ItemIsUserCheckable
        return result

    def toCheckState(self, val, record):
        self.state = record.value('masterActionType_id')
        if self.state.isNull() or self.state != record.value('master_id'):
            return QtCore.QVariant(QtCore.Qt.Unchecked)
        else:
            return QtCore.QVariant(QtCore.Qt.Checked)

    def setEditorData(self, editor, value, record):
        masterId = record.value('masterActionType_id')
        editor.setChecked(masterId == record.value('id') and not masterId.isNull())

    def getEditorData(self, editor):
        # if editor.isChecked():
        #     result = None
        # else: result = 123
        return self.state
