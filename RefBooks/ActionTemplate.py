# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Events.Action import CAction, CActionTypeCache, CActionType
from Events.ActionPropertiesTable import CActionPropertiesTableModel
from RefBooks.Ui_ActionTemplateFindDialog import Ui_ActionTemplateFindDialog
from Ui_ActionTemplateEditor import Ui_ActionTemplateEditorDialog
from library.AgeSelector import composeAgeSelector, parseAgeSelector
from library.DialogBase import CDialogBase
from library.HierarchicalItemsListDialog import CHierarchicalItemsListDialog
from library.ItemsListDialog import CItemEditorBaseDialog
from library.TableModel import CCol, CEnumCol, CRefBookCol, CTextCol, CTableModel, CDragDropTableModel
from library.TreeModel import CDragDropDBTreeModel
from library.Utils import forceRef, forceString, forceStringEx, toVariant, formatRecordsCount
from library.database import CTableRecordCache
from library.interchange import getComboBoxValue, getLineEditValue, setComboBoxValue, setLineEditValue

SexList = ['', u'М', u'Ж']


class CActionTemplateList(CHierarchicalItemsListDialog):
    def __init__(self, parent, forSelect=False):
        CHierarchicalItemsListDialog.__init__(
            self,
            parent,
            [
                CTextCol(u'Наименование', ['name'], 40),
                CEnumCol(u'Пол', ['sex'], SexList, 10),
                CTextCol(u'Возраст', ['age'], 10),
                CRefBookCol(u'Врач', ['owner_id'], 'vrbPersonWithSpeciality', 10),
                CRefBookCol(u'Специальность', ['speciality_id'], 'rbSpeciality', 10),
                CActionTypeCol(u'Действие', ['action_id'], 10),
            ],
            'ActionTemplate',
            ['name', 'id'],
            forSelect=forSelect,
            where='ActionTemplate.deleted=0',
            findClass=CFindDialog
        )
        self.setWindowTitleEx(u'Шаблоны действий')

        # set drag-n-drop settings
        self.tblItems.setDragEnabled(True)
        self.treeItems.setAcceptDrops(True)
        self.tblItems.setDropIndicatorShown(True)
        self.treeItems.setDropIndicatorShown(True)

    def preSetupUi(self):
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        # drag-n-drop models
        self.addModels('Table', CDragDropTableModel(self, self.cols, self.tableName))
        self.addModels('Tree', CDragDropDBTreeModel(self, self.tableName, 'id', 'group_id', 'name', self.order))
        self.modelTree.setLeavesVisible(True)
        # self.modelTree.setOrder('code')
        self.actDelete = QtGui.QAction(u'Удалить', self)
        self.actDelete.setObjectName('actDelete')

    def postSetupUi(self):
        CHierarchicalItemsListDialog.postSetupUi(self)
        self.tblItems.createPopupMenu([self.actDelete])
        self.tblItems.setSelectionMode(QtGui.QTableView.ExtendedSelection)
        self.connect(self.tblItems.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.popupMenuAboutToShow)
        # drag-n-drop support
        self.treeItems.dragEnabled()
        self.treeItems.acceptDrops()
        self.treeItems.showDropIndicator()
        self.treeItems.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.connect(self.modelTree, QtCore.SIGNAL('saveExpandedState()'), self.saveExpandedState)
        self.connect(self.modelTree, QtCore.SIGNAL('restoreExpandedState()'), self.restoreExpandedState)

    def getItemEditor(self):
        return CActionTemplateEditor(self)

    def popupMenuAboutToShow(self):
        currentItemId = self.currentItemId()
        self.actDelete.setEnabled(bool(currentItemId))

    @QtCore.pyqtSlot()
    def on_actDelete_triggered(self):
        db = QtGui.qApp.db
        tbl = db.table('ActionTemplate')

        def delete_templates(tid):
            db.updateRecords(tbl, 'deleted=1', tbl['id'].inlist(tid))
            stmt = db.selectStmt(tbl, ['id'], tbl['group_id'].inlist(tid))
            q = db.query(stmt)
            id_list = []
            while q.next():
                id_list.append(q.record().value('id').toInt())
            if id_list:
                delete_templates(id_list)

        tid = self.tblItems.selectedItemIdList()
        if tid:
            row = self.tblItems.currentIndex().row()
            delete_templates(tid)
            self.renewListAndSetTo()
            self.tblItems.setCurrentRow(row)


class CActionTypeCol(CCol):
    def __init__(self, title, fields, defaultWidth, alignment='l'):
        CCol.__init__(self, title, fields, defaultWidth, alignment)
        db = QtGui.qApp.db
        self._cache = CTableRecordCache(db, db.table('Action'), 'actionType_id')

    def getActionTypeId(self, actionId):
        if actionId:
            record = self._cache.get(actionId)
            if record:
                return forceRef(record.value(0))
        return None

    def format(self, values):
        val = values[0]
        actionTypeId = self.getActionTypeId(forceRef(val))
        if actionTypeId:
            actionType = CActionTypeCache.getById(actionTypeId)
            if actionType:
                return QtCore.QVariant(actionType.code + ' | ' + actionType.name)
        return QtCore.QVariant()

    def invalidateRecordsCache(self):
        self._cache.invalidate()


#
# ##########################################################################
#

class CActionTemplateEditor(CItemEditorBaseDialog, Ui_ActionTemplateEditorDialog):
    def __init__(self, parent):
        CItemEditorBaseDialog.__init__(self, parent, 'ActionTemplate')
        self.addModels('ActionProperties', CActionPropertiesTableModel(self))
        self.setupUi(self)
        # Заполнение элементов комбобокса переведенными значениями из первоисточника
        self.cmbStatus.clear()
        self.cmbStatus.addItems(CActionType.retranslateClass(False).statusNames)
        self.setWindowTitleEx(u'Шаблон действия')
        self.cmbActionType.setClasses([0, 1, 2, 3])

        self.cmbSpeciality.setTable('rbSpeciality')
        self.setModels(self.tblProps, self.modelActionProperties, self.selectionModelActionProperties)
        self.groupId = None
        self.action = None
        self.actionId = None
        self.setupDirtyCather()

    def setGroupId(self, id):
        self.groupId = id

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        self.setGroupId(forceRef(record.value('group_id')))
        setLineEditValue(self.edtName, record, 'name')
        setComboBoxValue(self.cmbSex, record, 'sex')
        (begUnit, begCount, endUnit, endCount) = parseAgeSelector(forceString(record.value('age')))
        self.cmbBegAgeUnit.setCurrentIndex(begUnit)
        self.edtBegAgeCount.setText(str(begCount))
        self.cmbEndAgeUnit.setCurrentIndex(endUnit)
        self.edtEndAgeCount.setText(str(endCount))

        ownerId = forceRef(record.value('owner_id'))
        specialityId = forceRef(record.value('speciality_id'))
        if ownerId:
            self.rbVisibleToOwner.setChecked(True)
            self.cmbOwner.setValue(ownerId)
        elif specialityId:
            self.rbVisibleToSpeciality.setChecked(True)
            self.cmbSpeciality.setValue(specialityId)
        else:
            self.rbVisibleToAll.setChecked(True)
        self.setActionId(forceRef(record.value('action_id')))
        self.setIsDirty(False)

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue('group_id', toVariant(self.groupId))
        getLineEditValue(self.edtName, record, 'name')
        getComboBoxValue(self.cmbSex, record, 'sex')
        record.setValue('age', toVariant(composeAgeSelector(
            self.cmbBegAgeUnit.currentIndex(), forceStringEx(self.edtBegAgeCount.text()),
            self.cmbEndAgeUnit.currentIndex(), forceStringEx(self.edtEndAgeCount.text())
        )))
        record.setValue(
            'owner_id', toVariant(self.cmbOwner.value() if self.rbVisibleToOwner.isChecked() else None)
        )
        record.setValue(
            'speciality_id', toVariant(self.cmbSpeciality.value() if self.rbVisibleToSpeciality.isChecked() else None)
        )
        record.setValue('action_id', toVariant(self.saveAction()))
        return record

    def checkDataEntered(self):
        result = True
        result = result and (forceStringEx(self.edtName.text()) or self.checkInputMessage(u'наименование', False, self.edtName))
        result = result and (not self.rbVisibleToOwner.isChecked() or self.cmbOwner.value() or self.checkInputMessage(u'врача', False, self.cmbOwner))
        result = result and (not self.rbVisibleToSpeciality.isChecked() or self.cmbSpeciality.value() or self.checkInputMessage(u'специальность', False, self.cmbSpeciality))
        return result

    def setActionId(self, actionId):
        self.actionId = actionId
        if actionId:
            db = QtGui.qApp.db
            record = db.getRecord('Action', '*', actionId)
        else:
            record = None

        if record:
            self.setAction(CAction(record=record))
        else:
            self.setAction(None)

    def setAction(self, action):
        self.action = action
        if action:
            actionTypeId = action.getType().id
        else:
            actionTypeId = None
        self.setActionTypeId(actionTypeId)
        if self.action:
            self.tblProps.model().setAction(self.action, None, 0, None)
            self.tblProps.resizeRowsToContents()

    def setActionTypeId(self, actionTypeId):
        self.cmbActionType.setValue(actionTypeId)
        self.tabWidget.setTabEnabled(1, bool(actionTypeId))
        old_props = dict()
        if self.action:
            old_props = self.action._propertiesByName
        if actionTypeId:
            if (not self.action or self.action.getType().id != actionTypeId):
                self.action = CAction.createByTypeId(actionTypeId)
                self.tblProps.model().setAction(self.action, None, 0, None)
                self.tblProps.resizeRowsToContents()
        else:
            self.action = None
            self.tblProps.model().setAction(self.action, None, 0, None)
            self.tblProps.resizeRowsToContents()
        if self.action:
            new_props = self.action._propertiesByName
            for prop in old_props:
                if prop in self.action._propertiesByName and \
                                new_props[prop]._type.getValueType() == old_props[prop]._type.getValueType():
                    new_props[prop]._changed = True
                    new_props[prop]._evaluation = old_props[prop]._evaluation
                    new_props[prop]._isAssigned = old_props[prop]._isAssigned
                    new_props[prop]._norm = old_props[prop]._norm
                    new_props[prop]._unitId = old_props[prop]._unitId
                    new_props[prop]._value = old_props[prop]._value

    def saveAction(self):
        if self.action:
            actionId = self.action.save()
        else:
            actionId = None
        if self.actionId and self.actionId != actionId:
            db = QtGui.qApp.db
            table = db.table('Action')
            db.deleteRecord(table, table['id'].eq(self.actionId))
            self.actionId = actionId
        return actionId

    @QtCore.pyqtSlot(int)
    def on_cmbActionType_currentIndexChanged(self, index):
        self.setActionTypeId(self.cmbActionType.value())


class CFindDialog(CDialogBase, Ui_ActionTemplateFindDialog):
    def __init__(self, parent):
        cols = [
            CTextCol(u'Наименование', ['name'], 40),
            CEnumCol(u'Пол', ['sex'], SexList, 10),
            CTextCol(u'Возраст', ['age'], 10),
            CRefBookCol(u'Врач', ['owner_id'], 'vrbPersonWithSpeciality', 10),
            CRefBookCol(u'Специальность', ['speciality_id'], 'rbSpeciality', 10),
            CActionTypeCol(u'Действие', ['action_id'], 10),
        ]

        super(CFindDialog, self).__init__(parent)

        self.addModels('ActionTemplateFound', CTableModel(self, cols, 'ActionTemplate'))
        self.setupUi(self)
        self.setModels(self.tblRecords, self.modelActionTemplateFound, self.selectionModelActionTemplateFound)

        self.cmbSpeciality.setTable('rbSpeciality')
        self.setWindowTitle(u'Поиск шаблона действия')

        self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setShortcut(QtCore.Qt.Key_Return)
        self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setDefault(True)
        self.cmbActionType.setClasses([0, 1, 2, 3])

        self.props = {}

    def setProps(self, props):
        self.props = props
        self.edtName.setText(props.get('name', ''))
        self.cmbActionType.setValue(props.get('action_type', None))
        self.cmbSex.setCurrentIndex(props.get('sex', 0))
        self.cmbSpeciality.setValue(props.get('speciality', None))
        self.cmbPerson.setValue(props.get('person', QtGui.qApp.userId))

    def getProps(self):
        return self.props

    def saveProps(self):
        self.props['name'] = unicode(self.edtName.text()).strip()
        self.props['action_type'] = self.cmbActionType.value()
        self.props['sex'] = self.cmbSex.currentIndex()
        self.props['speciality'] = self.cmbSpeciality.value()
        self.props['person'] = self.cmbPerson.value()

    def search(self):
        db = QtGui.qApp.db
        action_tbl = db.table('Action')
        action_template_tbl = db.table('ActionTemplate')
        tbl = action_template_tbl.leftJoin(action_tbl, action_template_tbl['action_id'].eq(action_tbl['id']))
        cond = [
            action_template_tbl['deleted'].eq(0)
        ]
        if self.props['name']:
            cond.append(action_template_tbl['name'].like('%%%s%%' % self.props['name']))
        if self.props['action_type']:
            cond.append(tbl[''])
        if self.props['sex']:
            cond.append(action_template_tbl['sex'].eq(self.props['sex']))
        if self.props['speciality']:
            cond.append(action_template_tbl['speciality_id'].eq(self.props['speciality']))
        if self.props['person']:
            cond.append(action_template_tbl['owner_id'].eq(self.props['person']))

        idList = QtGui.qApp.db.getIdList(tbl, action_template_tbl['id'], cond)
        idCount = len(idList)
        self.tblRecords.setIdList(idList)
        self.lblRecordsCount.setText(formatRecordsCount(idCount))
        if idCount == 0:
            self.setFocusToWidget(self.edtCode)
        elif idCount == 1:
            self.foundId = idList[0]
            self.accept()

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Close:
            self.reject()
        elif buttonCode == QtGui.QDialogButtonBox.Apply:
            self.saveProps()
            self.search()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.setProps({})

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblRecords_doubleClicked(self, index=None):
        index = self.tblRecords.currentIndex()
        self.foundId = self.tblRecords.itemId(index)
        self.accept()

    def id(self):
        return self.foundId
