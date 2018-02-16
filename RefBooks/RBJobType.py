# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Events.ActionTypeComboBox import CActionTypeTableCol
from Orgs.PersonComboBoxEx import CPersonFindInDocTableCol
from RefBooks.Person import COrgStructureInDocTableCol
from RefBooks.Tables import rbCode, rbName
from Ui_RBJobTypeEditor import Ui_ItemEditorDialog
from library.HierarchicalItemsListDialog import CHierarchicalItemsListDialog
from library.InDocTable import CInDocTableModel, CIntInDocTableCol, CRBInDocTableCol
from library.ItemsListDialog import CItemEditorBaseDialog
from library.TableModel import CEnumCol, CTextCol
from library.Utils import forceRef, forceString, toVariant
from library.interchange import getCheckBoxValue, getComboBoxValue, getLineEditValue, getSpinBoxValue, \
    setCheckBoxValue, setComboBoxValue, setLineEditValue, setSpinBoxValue

actionStatusChangerValues = [u'Не меняется',
                             u'Начато',
                             u'Ожидание',
                             u'Закончено',
                             u'Отменено',
                             u'Без результата',
                             u'Назначено']
actionPersonChangerValues = [u'Не меняется',
                             u'Пользователь',
                             u'Назначивший действие',
                             u'Ответственный за событие']
actionDateChagerValues = [u'Не меняется',
                          u'Дата окончания']


class CRBJobTypeList(CHierarchicalItemsListDialog):
    def __init__(self, parent):
        CHierarchicalItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код', [rbCode], 20),
            CTextCol(u'Региональный код', ['regionalCode'], 20),
            CTextCol(u'Наименование', [rbName], 40),
            CEnumCol(u'Модификатор статуса действия', ['actionStatusChanger'], actionStatusChangerValues, 30),
            CEnumCol(u'Модификатор исполнителя действия', ['actionPersonChanger'], actionPersonChangerValues, 30),
            CEnumCol(u'Модификатор даты действия', ['actionDateChanger'], actionDateChagerValues, 30)
        ], 'rbJobType', [rbCode, rbName])
        self.setWindowTitleEx(u'Типы работ')

    def preSetupUi(self):
        CHierarchicalItemsListDialog.preSetupUi(self)
        self.modelTree.setLeavesVisible(True)
        self.modelTree.setOrder('code')
        self.actDuplicate = QtGui.QAction(u'Дублировать', self)
        self.actDuplicate.setObjectName('actDuplicate')
        self.actDelete = QtGui.QAction(u'Удалить', self)
        self.actDelete.setObjectName('actDelete')

    def postSetupUi(self):
        CHierarchicalItemsListDialog.postSetupUi(self)
        self.tblItems.createPopupMenu([self.actDuplicate, '-', self.actDelete])
        self.connect(self.tblItems.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.popupMenuAboutToShow)

    def getItemEditor(self):
        return CRBJobTypeEditor(self)

    def popupMenuAboutToShow(self):
        currentItemId = self.currentItemId()
        self.actDuplicate.setEnabled(bool(currentItemId))
        self.actDelete.setEnabled(bool(currentItemId))

    @QtCore.pyqtSlot()
    def on_actDuplicate_triggered(self):
        def duplicateGroup(currentGroupId, newGroupId):
            db = QtGui.qApp.db
            table = db.table('rbJobType')
            records = db.getRecordList(table, '*', table['group_id'].eq(currentGroupId))
            for record in records:
                currentItemId = record.value('id')
                record.setValue('group_id', toVariant(newGroupId))
                record.setNull('id')
                newItemId = db.insertRecord(table, record)
                duplicateGroup(currentItemId, newItemId)

        def duplicateCurrentInternal():
            currentItemId = self.currentItemId()
            if currentItemId:
                db = QtGui.qApp.db
                table = db.table('rbJobType')
                db.transaction()
                try:
                    record = db.getRecord(table, '*', currentItemId)
                    record.setValue('code', toVariant(forceString(record.value('code')) + '_1'))
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
            if currentItemId:
                row = self.tblItems.currentIndex().row()
                db = QtGui.qApp.db
                table = db.table('rbJobType')
                tableJob = db.table('Job')
                if db.getCount(tableJob, where=tableJob['jobType_id'].eq(currentItemId)) > 0:
                    QtGui.QMessageBox.warning(self, u'Внимание!',
                                              u'Нельзя удалить тип, записи с которым есть в базе. Сначала удалите записи')
                else:
                    db.deleteRecord(table, table['id'].eq(currentItemId))
                    self.renewListAndSetTo()
                    self.tblItems.setCurrentRow(row)

        QtGui.qApp.call(self, deleteCurrentInternal)


class CRBJobTypeEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self, parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rbJobType')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Тип работы')
        self.setupDirtyCather()
        self.groupId = None

        self.modelJobTypeQuotes = None  # type: CJobTypeQuotesModel
        self.modelJobTypeQuotes = None  # type: CJobTypeActionsModel
        self.addModels('JobTypeActions', CJobTypeActionsModel(self))
        self.addModels('JobTypeQuotes', CJobTypeQuotesModel(self))
        self.setModels(self.tblJobTypeActions, self.modelJobTypeActions, self.selectionModelJobTypeActions)
        self.setModels(self.tblQuota, self.modelJobTypeQuotes, self.selectionModelJobTypeQuotes)
        self.prepareTable(self.tblJobTypeActions, self.modelJobTypeActions)
        self.prepareTable(self.tblQuota, self.modelJobTypeQuotes)

    def setGroupId(self, id):
        self.groupId = id

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        self.groupId = forceRef(record.value('group_id'))
        setLineEditValue(self.edtCode, record, 'code')
        setLineEditValue(self.edtRegionalCode, record, 'regionalCode')
        setLineEditValue(self.edtName, record, 'name')
        setLineEditValue(self.edtListContext, record, 'listContext')
        setComboBoxValue(self.cmbActionStatusChanger, record, 'actionStatusChanger')
        setComboBoxValue(self.cmbActionPersonChanger, record, 'actionPersonChanger')
        setComboBoxValue(self.cmbActionDateChanger, record, 'actionDateChanger')
        setSpinBoxValue(self.edtTicketDuration, record, 'ticketDuration')
        self.modelJobTypeActions.loadItems(self.itemId())
        self.modelJobTypeQuotes.loadItems(self.itemId())
        setCheckBoxValue(self.chkShowOnlyPayed, record, 'showOnlyPayed')  # atronah for issue 317
        setSpinBoxValue(self.edtDurationVisibility, record, 'durationVisibility')
        setComboBoxValue(self.cmbTicketAssignWay, record, 'ticketAssignWay')
        setComboBoxValue(self.cmbJobStatusModifier, record, 'jobStatusModifier')

    def prepareTable(self, tblWidget, model):
        tblWidget.setModel(model)
        tblWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        tblWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        tblWidget.addPopupDuplicateCurrentRow()
        tblWidget.addPopupSeparator()
        tblWidget.addMoveRow()
        tblWidget.addPopupDelRow()

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue('group_id', toVariant(self.groupId))
        getLineEditValue(self.edtCode, record, 'code')
        getLineEditValue(self.edtRegionalCode, record, 'regionalCode')
        getLineEditValue(self.edtName, record, 'name')
        getLineEditValue(self.edtListContext, record, 'listContext')
        getComboBoxValue(self.cmbActionStatusChanger, record, 'actionStatusChanger')
        getComboBoxValue(self.cmbActionPersonChanger, record, 'actionPersonChanger')
        getComboBoxValue(self.cmbActionDateChanger, record, 'actionDateChanger')
        getSpinBoxValue(self.edtTicketDuration, record, 'ticketDuration')
        getCheckBoxValue(self.chkShowOnlyPayed, record, 'showOnlyPayed')  # atronah for issue 317
        getSpinBoxValue(self.edtDurationVisibility, record, 'durationVisibility')
        getComboBoxValue(self.cmbTicketAssignWay, record, 'ticketAssignWay')
        getComboBoxValue(self.cmbJobStatusModifier, record, 'jobStatusModifier')
        return record

    def saveInternals(self, id):
        self.modelJobTypeActions.saveItems(id)
        self.modelJobTypeQuotes.saveItems(id)


class CJobTypeActionsCol(CActionTypeTableCol):
    def __init__(self, *args, **kwargs):
        super(CJobTypeActionsCol, self).__init__(*args, **kwargs)
        self._disabledActionTypeIdList = self.getActionTypesWithOutdatedServices()

    @staticmethod
    def getActionTypesWithOutdatedServices():
        u"""
        Типы действий, связанные с услугами с датой окончания < текущей
        :return: [list of ActionType.id]
        """
        db = QtGui.qApp.db
        tableAT = db.table('ActionType')
        tableATS = db.table('ActionType_Service')
        tableService = db.table('rbService')

        table = tableAT.innerJoin(tableATS, tableATS['master_id'].eq(tableAT['id']))
        table = table.innerJoin(tableService, tableService['id'].eq(tableATS['service_id']))
        cond = [
            tableAT['deleted'].eq(0),
            tableService['endDate'].dateLt(QtCore.QDate().currentDate())
        ]
        idList1 = db.getDistinctIdList(table, tableAT['id'], cond)

        table = tableAT.innerJoin(tableService, tableService['id'].eq(tableAT['nomenclativeService_id']))
        cond = [
            tableAT['deleted'].eq(0),
            tableService['endDate'].dateLt(QtCore.QDate().currentDate())
        ]
        idList2 = db.getDistinctIdList(table, tableAT['id'], cond)

        return list(set(idList1).union(set(idList2)))

    def createEditor(self, parent):
        editor = super(CJobTypeActionsCol, self).createEditor(parent)
        editor.setDisabledActionTypeIdList(self._disabledActionTypeIdList)
        return editor


class CJobTypeActionsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'rbJobType_ActionType', 'id', 'master_id', parent)
        self.addCol(CJobTypeActionsCol(u'Действие', 'actionType_id', 10, None, classesVisible=True, descendants=True, model=self))
        self.addCol(CIntInDocTableCol(u'Группа выбора', 'selectionGroup', 12))
        self.addCol(CIntInDocTableCol(u'Суточная квота', 'onDayLimit', 12, high=999))

    def getEmptyRecord(self):
        result = CInDocTableModel.getEmptyRecord(self)
        result.setValue('selectionGroup', QtCore.QVariant(0))
        return result


class CJobTypeQuotesModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'rbJobType_Quota', 'id', 'master_id', parent)
        self.addCol(CIntInDocTableCol(u'Количество', 'count', 12))
        self.addCol(COrgStructureInDocTableCol(u'Отделение', 'orgStructure_id', 12))
        self.addCol(CRBInDocTableCol(u'Специальность', 'speciality_id', 12, 'rbSpeciality'))
        self.addCol(CRBInDocTableCol(u'Должность', 'post_id', 12, 'rbPost'))
        self.addCol(CPersonFindInDocTableCol(u'Врач', 'person_id', 12))
