# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from library.DateEdit import CDateEdit
from library.PreferencesMixin import CPreferencesMixin
from library.TreeModel import CTreeItem, CTreeModel
from library.Utils import calcAgeTuple, forceBool, forceDate, forceDouble, forceInt, forceRef, forceString, getPref, setPref

ITEM_CHECKED_COLUMN = 0
ITEM_TEXT_VALUE_COLUMN = 0
ITEM_BACKGROUND_COLUMN = 1
EXTERNAL_ID_COLUMN = 2
ITEM_AMOUNT_COLUMN = 3


class CJobTicketProbeBaseItem(CTreeItem):
    def __init__(self, parent, id, model, **kwargs):
        self._id = id
        self._model = model
        self._isChecked = False
        self._externalId = None
        self._canBeChecked = kwargs.get('canBeChecked', False)
        self._editableExternalId = kwargs.get('editableExternalId', False)
        CTreeItem.__init__(self, parent, self._getValue())

    def _getValue(self):
        assert False

    def columnCount(self):
        return 1

    def model(self):
        return self._model

    def id(self):
        return self._id

    def loadChildren(self):
        return []

    def background(self, column):
        return QtCore.QVariant()

    def amount(self, column):
        return QtCore.QVariant()

    def checked(self, column):
        if self.canBeChecked(column):
            return QtCore.QVariant(self._isChecked)
        return QtCore.QVariant()

    def canBeChecked(self, column):
        if column in self.model().checkableColumnList():
            return self._canBeChecked
        return False

    def editableExternalId(self, column):
        if column == EXTERNAL_ID_COLUMN:
            return self._editableExternalId
        return False

    def flags(self, index=None):
        flags = CTreeItem.flags(self)
        if not self.saved():
            if index and index.isValid() and self.canBeChecked(index.column()):
                flags |= QtCore.Qt.ItemIsUserCheckable
            if index and index.isValid() and self.editableExternalId(index.column()):
                flags |= QtCore.Qt.ItemIsEditable
        else:
            flags &= ~QtCore.Qt.ItemIsEnabled
        return flags

    def setChecked(self, value, setSame=True):
        if self.canSetExternalId():
            if value and not self.hasExternalId():
                self.setExternalId(self.model().currentEnteredTakenTissueExternalId())
            elif not value and self.hasExternalId():
                self.setExternalId('')
        if not self.saved():
            if setSame:
                self.setSameChecked(value)
            self._isChecked = value
        if self._items:
            for item in self._items:
                item.setChecked(value)

    def hasExternalId(self):
        return bool(self._externalId)

    def canSetExternalId(self):
        return self.editableExternalId(EXTERNAL_ID_COLUMN) and not self.saved()

    def setExternalId(self, value, depth=False, setSame=True):
        if self.canSetExternalId():
            if depth:
                if forceBool(self.checked(ITEM_CHECKED_COLUMN)):
                    self._externalId = value
            else:
                if setSame:
                    self.setSameExternalId(value)
                self._externalId = value
        if self._items:
            for item in self._items:
                CJobTicketProbeBaseItem.setExternalId(item, value, depth=True)

    def setSameChecked(self, value):
        pass

    def setSameExternalId(self, value):
        pass

    def absoluteItemList(self, lst):
        lst.append(self)
        if self._items:
            for item in self._items:
                item.absoluteItemList(lst)

    def resetItems(self):
        self._items = None

    def data(self, column):
        if column == EXTERNAL_ID_COLUMN:
            if self._externalId:
                return QtCore.QVariant(self._externalId)
            return QtCore.QVariant()
        elif column == ITEM_AMOUNT_COLUMN:
            return self.amount(column)
        else:
            return CTreeItem.data(self, column)

    def setEditorData(self, column, editor, value):
        pass

    def getEditorData(self, column, editor):
        assert False

    def createEditor(self, parent, column):
        assert False

    def saved(self):
        return False

    def containerTypeId(self):
        return None


class CJobTicketProbeTestItem(CJobTicketProbeBaseItem):
    cacheValuesById = {}
    cacheSavedValues = {}

    def __init__(self, parent, propertyType, model):
        self._propertyType = propertyType
        self._isChecked = False
        self._probeId = None
        self._saved = False
        CJobTicketProbeBaseItem.__init__(self, parent, propertyType.id, model, canBeChecked=True, editableExternalId=True)
        self._saved = self._isItemSaved()

    def containerTypeId(self):
        return self.parent().containerTypeId()

    def _isItemSaved(self):
        if self.model().hasSavedTakenTissue():
            takenTissueId = self.model().takenTissueId()
            testId = self.testId()
            saved, self._probeId, externalId = self.__isItemSaved(takenTissueId, testId)
            if saved:
                self.setExternalId(externalId)
            self.setChecked(saved)
            return saved

    @classmethod
    def __isItemSaved(cls, takenTissueId, testId):
        savedValues = cls.cacheSavedValues.get((takenTissueId, testId), None)
        if savedValues is None:
            db = QtGui.qApp.db
            tableProbe = db.table('Probe')
            cond = [
                tableProbe['test_id'].eq(testId),
                tableProbe['takenTissueJournal_id'].eq(takenTissueId)
            ]
            record = db.getRecordEx(tableProbe, ['id', 'externalId'], cond)
            if record:
                probeId = forceRef(record.value('id'))
                externalId = forceString(record.value('externalId'))
            else:
                probeId = externalId = None
            savedValues = bool(probeId), probeId, externalId
            cls.cacheSavedValues[(takenTissueId, testId)] = savedValues

        return savedValues

    def saved(self):
        return self._saved

    def probeId(self):
        return self._probeId

    def setSaved(self, value, probeId):
        self._saved = value
        self._probeId = probeId

    def getAction(self):
        return self.parent().action()

    def testId(self):
        return self._propertyType.testId

    def propertyType(self):
        return self._propertyType

    def createEditor(self, parent, column):
        editor = QtGui.QLineEdit(parent)
        return editor

    def setEditorData(self, column, editor, value):
        editor.setText(forceString(value))

    def getEditorData(self, column, editor):
        return unicode(editor.text())

    def _getValue(self):
        testId = self._propertyType.testId
        mapItemByTestId(testId, self)
        return self.__getValue(testId)

    def setSameChecked(self, value):
        sameItems = self.getSameItems()
        for item in sameItems:
            item.setChecked(value, setSame=False)

    def setSameExternalId(self, value):
        sameItems = self.getSameItems()
        for item in sameItems:
            item.setExternalId(value, setSame=False)

    def getSameItems(self):
        items = getItemsByTestId(self.testId())
        return [item for item in items if item._id != self._id]

    @classmethod
    def __getValue(cls, testId):
        value = cls.cacheValuesById.get(testId, None)
        if value is None:
            value = forceString(QtGui.qApp.db.translate('rbTest', 'id', testId, 'CONCAT_WS(\' | \', code, name)'))
            if not value:
                value = '_invalid_'
            cls.cacheValuesById[testId] = value
        return value

    @classmethod
    def reset(cls):
        cls.cacheValuesById.clear()
        cls.cacheSavedValues.clear()


class CJobTicketProbeActionItem(CJobTicketProbeBaseItem):
    def __init__(self, parent, action, model):
        self._action = action
        actionRecord = action.getRecord()
        actionId = forceRef(actionRecord.value('id'))
        self._actionTypeId = forceRef(actionRecord.value('actionType_id'))
        CJobTicketProbeBaseItem.__init__(self, parent, actionId, model)

    def _getValue(self):
        actionType = self._action.getType()
        return u' | '.join([actionType.code, actionType.name])

    def loadChildren(self):
        result = []
        actionType = self._action.getType()
        propertyTypeList = actionType.getPropertiesById().items()
        propertyTypeList.sort(key=lambda x: (x[1].idx, x[0]))
        clientSex, clientAge = getClientInfoByAction(self._action)
        propertyTypeList = [x[1] for x in propertyTypeList if x[1].applicable(clientSex, clientAge)]
        for propertyType in propertyTypeList:
            if propertyType.testId:
                testItem = CJobTicketProbeTestItem(self, propertyType, self.model())
                result.append(testItem)
        return result

    def containerTypeId(self):
        return self.parent().containerTypeId()

    def action(self):
        return self._action


class CJobTicketProbeContainerItem(CJobTicketProbeBaseItem):
    def __init__(self, parent, containerTypeId, model):
        self._capacity = None
        self._amount = None
        CJobTicketProbeBaseItem.__init__(self, parent, containerTypeId, model, canBeChecked=True, editableExternalId=True)

    def _getValue(self):
        record = QtGui.qApp.db.getRecord('rbContainerType',
                                         'CONCAT_WS(\' | \', code, name) AS val, color, amount', self._id)
        if record:
            self._color = QtGui.QColor(forceString(record.value('color')))
            self._capacity = forceDouble(record.value('amount'))
            return forceString(record.value('val'))
        else:
            self._color = QtGui.QColor()
            return ''

    def createEditor(self, parent, column):
        editor = QtGui.QLineEdit(parent)
        return editor

    def setEditorData(self, column, editor, value):
        editor.setText(forceString(value))

    def getEditorData(self, column, editor):
        return unicode(editor.text())

    def loadChildren(self):
        return [CJobTicketProbeActionItem(self, action, self.model())
                for action in self.getActionListByContainerTypeId(self._id)]

    def containerTypeId(self):
        return self._id

    def getActionListByContainerTypeId(self, containerTypeId):
        return self.model().getActionListByContainerTypeId(containerTypeId)

    def columnCount(self):
        return 4

    def background(self, column):
        if column == ITEM_BACKGROUND_COLUMN:
            return QtCore.QVariant(self._color)
        return CJobTicketProbeBaseItem.background(self, column)

    def amount(self, column):
        if column == ITEM_AMOUNT_COLUMN:
            if self._capacity:
                if self._amount is None:
                    amountForCaontainerTypeId = getAmountForAcontainerTypeId(self._id)
                    self._amount = QtCore.QVariant(round(amountForCaontainerTypeId / self._capacity, 1))
                return self._amount
        return QtCore.QVariant()


class CJobTicketProbeRootItem(CJobTicketProbeBaseItem):
    def __init__(self, model):
        CJobTicketProbeBaseItem.__init__(self, None, None, model)

    def _getValue(self):
        return u'Все'

    def loadChildren(self, actionList=None):
        if actionList is None:
            actionList = self.model().actionList()
        result = []
        existsContainerTypeId = []
        CTissueAmountForContainerType.reset()
        db = QtGui.qApp.db
        for action in actionList:
            mapClientInfoByAction(action)
            actionRecord = action.getRecord()
            tissueJournalId = forceRef(actionRecord.value('takenTissueJournal_id'))
            tissueTypeId = self.model().suggestedTissueTypeId() if not tissueJournalId else None
            # if tissueJournalId or tissueTypeId:
            if not tissueTypeId and tissueJournalId:
                tissueTypeId = forceRef(db.translate('TakenTissueJournal', 'id',
                                                     tissueJournalId, 'tissueType_id'))
            actionTypeId = forceRef(actionRecord.value('actionType_id'))

            cond = 'master_id=%d' % actionTypeId
            if tissueTypeId:
                cond += ' AND tissueType_id=%d' % tissueTypeId

            containerTypeId = self._getContainerTypeId(cond)
            if containerTypeId:
                if containerTypeId not in existsContainerTypeId:
                    existsContainerTypeId.append(containerTypeId)
                    containerItem = CJobTicketProbeContainerItem(self, containerTypeId, self.model())
                    result.append(containerItem)
                self.mapContainerTypeIdToActionList(containerTypeId, action)
        return result

    def _getContainerTypeId(self, cond):
        db = QtGui.qApp.db
        record = db.getRecordEx('ActionType_TissueType', 'containerType_id, amount', cond)
        if record:
            amount = forceDouble(record.value('amount'))
            containerTypeId = forceRef(record.value('containerType_id'))
            calcAmountForContainerTypeId(containerTypeId, amount)
            return containerTypeId
        return None

    def mapContainerTypeIdToActionList(self, containerTypeId, action):
        self.model().mapContainerTypeIdToActionRecordList(containerTypeId, action)


class CJobTicketProbeModel(CTreeModel):
    def __init__(self, parent):
        CTreeModel.__init__(self, parent, CJobTicketProbeRootItem(self))
        self.rootItemVisible = False
        self._actionList = []
        self._mapContainerTypeIdToActionList = {}
        self._parent = parent
        self.resetCache()
        self._currentTakenTissueExternalId = None

    def resetCache(self):
        resetCache()

    def checkableColumnList(self):
        return [ITEM_CHECKED_COLUMN]

    def currentEnteredTakenTissueExternalId(self):
        return self._parent.edtTissueExternalId.text()

    def suggestedTissueTypeId(self):
        return self._parent.cmbTissueType.value()

    def hasSavedTakenTissue(self):
        return bool(self._parent.takenTissueRecord)

    def saveTakenTissueRecord(self):
        self._parent.saveTakenTissueRecord()

    def takenTissueRecord(self):
        if not self.hasSavedTakenTissue():
            if self.askOkOrCancel(u'Необходимо сохранить забор ткани. Сохранить?'):
                self.saveTakenTissueRecord()
        return self._parent.takenTissueRecord

    def takenTissueId(self):
        takenTissueRecord = self.takenTissueRecord()
        return forceRef(takenTissueRecord.value('id')) if takenTissueRecord else None

    def mapContainerTypeIdToActionRecordList(self, containerTypeId, action):
        actionList = self._mapContainerTypeIdToActionList.setdefault(containerTypeId, [])
        if not self.isActionInActionList(action, actionList):
            actionList.append(action)

    def isActionInActionList(self, action, actionList):
        actionId = forceRef(action.getRecord().value('id'))
        actionIdList = [forceRef(action.getRecord().value('id')) for action in actionList]
        return actionId in actionIdList

    def getActionListByContainerTypeId(self, containerTypeId):
        return self._mapContainerTypeIdToActionList.get(containerTypeId, [])

    def columnCount(self, index=QtCore.QModelIndex()):
        return 4

    def rowCount(self, parent=QtCore.QModelIndex()):
        return CTreeModel.rowCount(self, parent)

    def setActionList(self, actionList, force=False):
        if actionList != self._actionList or force:
            self._actionList = actionList
            self.reset()

    def loadChildrenItems(self):
        self._rootItem.loadChildren(self._actionList)
        self.reset()

    def actionList(self):
        return self._actionList

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()
        if role == QtCore.Qt.DisplayRole:
            item = index.internalPointer()
            if item:
                return item.data(index.column())
        elif role == QtCore.Qt.BackgroundRole:
            item = index.internalPointer()
            if item:
                return item.background(index.column())
        elif role == QtCore.Qt.CheckStateRole:
            item = index.internalPointer()
            if item:
                return item.checked(index.column())
        return QtCore.QVariant()

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                if section == ITEM_TEXT_VALUE_COLUMN:
                    return QtCore.QVariant(u'Пробы')
                elif section == ITEM_BACKGROUND_COLUMN:
                    return QtCore.QVariant(u'Цветовая маркировка')
                elif section == EXTERNAL_ID_COLUMN:
                    return QtCore.QVariant(u'Идентификатор')
                elif section == ITEM_AMOUNT_COLUMN:
                    return QtCore.QVariant(u'Количество')
        return QtCore.QVariant()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid():
            return False
        if role == QtCore.Qt.CheckStateRole:
            column = index.column()
            if column == ITEM_CHECKED_COLUMN:
                item = index.internalPointer()
                if item and item.canBeChecked(column):
                    item.setChecked(not forceBool(item.checked(column)))
                    self.emitAllChanged()
                    return True
        if role == QtCore.Qt.EditRole:
            column = index.column()
            if column == EXTERNAL_ID_COLUMN:
                item = index.internalPointer()
                if item and item.editableExternalId(column):
                    item.setExternalId(forceString(value))
                    self.emitAllChanged()
                    return True
        return False

    def emitAllChanged(self):
        index1 = self.index(0, 0)
        index2 = self.index(self.rowCount(), self.columnCount())
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index1, index2)

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags
        item = index.internalPointer()
        if not item:
            return QtCore.Qt.NoItemFlags
        return item.flags(index)

    def absoluteItemList(self):
        result = []
        self.getRootItem().absoluteItemList(result)
        return result

    def resetItems(self):
        for item in self.absoluteItemList():
            item.resetItems()
        self._mapContainerTypeIdToActionList.clear()
        self.loadChildrenItems()

    def existCheckedProbeItems(self, notSaved=False):
        def filterFunc(item):
            result = isinstance(item, CJobTicketProbeTestItem) and forceBool(item.checked(ITEM_CHECKED_COLUMN))
            if result and notSaved:
                result = not item.saved()
            return result

        allItems = self.absoluteItemList()
        return filter(filterFunc, allItems)

    def askOkOrCancel(self, message):
        result = QtGui.QMessageBox.warning(self._parent,
                                           u'Внимание!',
                                           message,
                                           QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                                           QtGui.QMessageBox.Cancel)
        return result == QtGui.QMessageBox.Ok

    def existsNotCheckedItems(self):
        def filterFunc(item):
            result = isinstance(item, CJobTicketProbeTestItem) and not forceBool(item.checked(ITEM_CHECKED_COLUMN))
            if result:
                result = not item.saved()
            return result

        allItems = self.absoluteItemList()
        return filter(filterFunc, allItems)

    def isExistsNotCheckedItems(self):
        return bool(self.existsNotCheckedItems())

    def registrateProbe(self, forceCheck=False):
        takenTissueId = self.takenTissueId()
        if not takenTissueId:
            return

        if forceCheck:
            self.getRootItem().setChecked(True)

        db = QtGui.qApp.db
        db.transaction()

        try:
            testItems = self.existCheckedProbeItems(notSaved=True)
            testActionList = []
            testIdToProbeId = {}
            for item in testItems:

                testAction = item.getAction()

                if testAction not in testActionList:
                    testActionList.append(testAction)

                testActionRecord = testAction.getRecord()
                testActionRecord.setValue('takenTissueJournal_id', QtCore.QVariant(takenTissueId))

                probeId = self.saveProbe(takenTissueId,
                                         item.propertyType(),
                                         forceString(item.data(EXTERNAL_ID_COLUMN)),
                                         testActionList,
                                         testIdToProbeId,
                                         item.containerTypeId())
                item.setSaved(True, probeId)

            for testAction in testActionList:
                testActionRecord = testAction.getRecord()
                testAction.save(idx=forceInt(testActionRecord.value('idx')))

            db.commit()

        except Exception, e:
            db.rollback()
            QtGui.qApp.logCurrentException()
            QtGui.QMessageBox.critical(self._parent,
                                       u'Внимание!',
                                       ''.join([u'Произошла ошибка!\n', unicode(e)]),
                                       QtGui.QMessageBox.Ok,
                                       QtGui.QMessageBox.Ok)

    def saveProbe(self, takenTissueId, propertyType, externalId, testActionList, testIdToProbeId, containerTypeId):
        testId = propertyType.testId
        equipmentId = QtGui.qApp.db.translate('rbEquipment_Test', 'test_id', testId, 'equipment_id')
        probeId = testIdToProbeId.get(testId, None)
        if not externalId:
            if self._currentTakenTissueExternalId is None:
                self._currentTakenTissueExternalId = forceString(QtGui.qApp.db.translate('TakenTissueJournal', 'id', takenTissueId, 'externalId'))
            externalId = self._currentTakenTissueExternalId
        if not probeId:
            db = QtGui.qApp.db
            tableProbe = db.table('Probe')

            probe = tableProbe.newRecord()
            probe.setValue('status', QtCore.QVariant(1))  # ожидание
            probe.setValue('test_id', QtCore.QVariant(testId))
            probe.setValue('workTest_id', QtCore.QVariant(testId))
            probe.setValue('takenTissueJournal_id', QtCore.QVariant(takenTissueId))
            probe.setValue('typeName', QtCore.QVariant(propertyType.typeName))
            probe.setValue('norm', QtCore.QVariant(propertyType.norm))
            probe.setValue('unit_id', QtCore.QVariant(propertyType.unitId))
            probe.setValue('externalId', QtCore.QVariant(externalId))
            probe.setValue('containerType_id', QtCore.QVariant(containerTypeId))
            if equipmentId:
                probe.setValue('equipment_id', equipmentId)
            probeId = db.insertOrUpdate(tableProbe, probe)

            testIdToProbeId[testId] = probeId

        self.syncItemsForSaving(testId, externalId, probeId, testActionList)
        return probeId

    def syncItemsForSaving(self, testId, externalId, probeId, testActionList):
        sameTestItems = getItemsByTestId(testId)
        for sameTestItem in sameTestItems:
            testAction = sameTestItem.getAction()
            if testAction not in testActionList:
                testActionList.append(testAction)

            sameTestItem.setChecked(True)
            sameTestItem.setExternalId(externalId)
            sameTestItem.setSaved(True, probeId)


class CItemDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, parent):
        QtGui.QStyledItemDelegate.__init__(self, parent)
        self.row = 0
        self.lastrow = 0
        self.column = 0
        self.editor = None

    def createEditor(self, parent, option, index):
        item = index.internalPointer()
        column = index.column()
        editor = item.createEditor(parent, column)
        self.connect(editor, QtCore.SIGNAL('commit()'), self.emitCommitData)
        self.connect(editor, QtCore.SIGNAL('editingFinished()'), self.commitAndCloseEditor)
        self.editor = editor
        self.row = index.row()
        self.rowcount = index.model().rowCount()
        self.column = column
        return editor

    def setEditorData(self, editor, index):
        if editor is not None:
            item = index.internalPointer()
            if item:
                column = index.column()
                item.setEditorData(column, editor, item.data(column))

    def setModelData(self, editor, model, index):
        if editor is not None:
            item = index.internalPointer()
            column = index.column()
            model.setData(index, item.getEditorData(column, editor))

    def emitCommitData(self):
        self.emit(QtCore.SIGNAL('commitData(QWidget *)'), self.sender())

    def commitAndCloseEditor(self):
        editor = self.sender()
        self.emit(QtCore.SIGNAL('commitData(QWidget *)'), editor)
        self.emit(QtCore.SIGNAL('closeEditor(QWidget *,QAbstractItemDelegate::EndEditHint)'), editor, QtGui.QAbstractItemDelegate.NoHint)

    def eventFilter(self, object, event):
        def editorIsEmpty():
            if isinstance(self.editor, QtGui.QLineEdit):
                return self.editor.text() == ''
            if isinstance(self.editor, QtGui.QComboBox):
                return self.editor.currentIndex() == 0
            if isinstance(self.editor, CDateEdit):
                return not self.editor.dateIsChanged()
            if isinstance(self.editor, QtGui.QDateEdit):
                return not self.editor.date().isValid()
            return False

        def editorCanEatTab():
            if isinstance(self.editor, QtGui.QDateEdit):
                return self.editor.currentSection() != QtGui.QDateTimeEdit.YearSection
            return False

        def editorCanEatBacktab():
            if isinstance(self.editor, QtGui.QDateEdit):
                return self.editor.currentSection() != QtGui.QDateTimeEdit.DaySection
            return False

        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Tab:
                if editorCanEatTab():
                    self.editor.keyPressEvent(event)
                    return True
                if self.editor is not None:
                    self.parent().commitData(self.editor)
                self.parent().keyPressEvent(event)
                return True
            elif event.key() == QtCore.Qt.Key_Backtab:
                if editorCanEatBacktab():
                    self.editor.keyPressEvent(event)
                    return True
                if self.editor is not None:
                    self.parent().commitData(self.editor)
                self.parent().keyPressEvent(event)
                return True
            elif event.key() == QtCore.Qt.Key_Return:
                return True
        return QtGui.QStyledItemDelegate.eventFilter(self, object, event)


class CJobTicketProbeTreeView(QtGui.QTreeView, CPreferencesMixin):
    def __init__(self, parent):
        QtGui.QTreeView.__init__(self, parent)
        self.setItemDelegateForColumn(EXTERNAL_ID_COLUMN, CItemDelegate(self))
        self._popupMenu = QtGui.QMenu(self)
        self.connect(self._popupMenu, QtCore.SIGNAL('aboutToShow()'), self.popupMenuAboutToShow)
        self._actRegistrateProbe = QtGui.QAction(u'Зарегистрировать пробы', self)
        self.connect(self._actRegistrateProbe, QtCore.SIGNAL('triggered()'), self.registrateProbe)
        self._popupMenu.addAction(self._actRegistrateProbe)

    def registrateProbe(self):
        self.model().registrateProbe()

    def contextMenuEvent(self, event):  # event: QContextMenuEvent
        self._popupMenu.exec_(event.globalPos())
        event.accept()

    def popupMenuAboutToShow(self):
        existCheckedProbeItems = self.model().existCheckedProbeItems(notSaved=True)
        self._actRegistrateProbe.setEnabled(bool(existCheckedProbeItems))

    def loadPreferences(self, preferences):
        model = self.model()
        for i in xrange(model.columnCount()):
            width = forceInt(getPref(preferences, 'col_' + str(i), None))
            if width:
                self.setColumnWidth(i, width)

    def savePreferences(self):
        preferences = {}
        model = self.model()
        if model:
            for i in xrange(model.columnCount()):
                width = self.columnWidth(i)
                setPref(preferences, 'col_' + str(i), QtCore.QVariant(width))
        return preferences


class CMapActionIdToClientInfo():
    cache = {}
    cacheByEventId = {}
    existsEventIdList = []

    @classmethod
    def update(cls, action):
        actionRecord = action.getRecord()
        eventId = forceRef(actionRecord.value('event_id'))
        actionId = forceRef(actionRecord.value('id'))
        if eventId not in cls.existsEventIdList:
            cls.existsEventIdList.append(eventId)
            db = QtGui.qApp.db
            clientId = forceRef(db.translate('Event', 'id', eventId, 'client_id'))
            clientRecord = db.getRecord('Client', '*', clientId)
            if clientRecord:
                directionDate = forceDate(actionRecord.value('directionDate'))
                clientSex = forceInt(clientRecord.value('sex'))
                clientBirthDate = forceDate(clientRecord.value('birthDate'))
                clientAge = calcAgeTuple(clientBirthDate, directionDate)
            else:
                clientSex = clientAge = None
            cls.cache[actionId] = (clientSex, clientAge)
            cls.cacheByEventId[eventId] = (clientSex, clientAge)
        else:
            cls.cache[actionId] = cls.cacheByEventId[eventId]

    @classmethod
    def get(cls, action):
        actionRecord = action.getRecord()
        actionId = forceRef(actionRecord.value('id'))
        return cls.cache.get(actionId, (None, None))

    @classmethod
    def reset(cls):
        cls.cache.clear()
        cls.cacheByEventId.clear()
        cls.existsEventIdList = []


class CMapTestIdToItems():
    cache = {}

    @classmethod
    def update(cls, testId, item):
        itemList = cls.cache.setdefault(testId, [])
        if item not in itemList:
            itemList.append(item)

    @classmethod
    def getItems(cls, testId):
        return cls.cache.get(testId, [])

    @classmethod
    def reset(cls):
        cls.cache.clear()


class CTissueAmountForContainerType():
    cache = {}

    @classmethod
    def update(cls, containerTypeId, amount):
        existAmount = cls.cache.get(containerTypeId, 0.0)
        cls.cache[containerTypeId] = amount + existAmount

    @classmethod
    def get(cls, containerTypeId):
        return cls.cache.get(containerTypeId, 0.0)

    @classmethod
    def reset(cls):
        cls.cache.clear()


def resetCache():
    CMapActionIdToClientInfo.reset()
    CJobTicketProbeTestItem.reset()
    CMapTestIdToItems.reset()
    CTissueAmountForContainerType.reset()


def getClientInfoByAction(action):
    return CMapActionIdToClientInfo.get(action)


def mapClientInfoByAction(action):
    CMapActionIdToClientInfo.update(action)


def getItemsByTestId(testId):
    return CMapTestIdToItems.getItems(testId)


def mapItemByTestId(testId, item):
    CMapTestIdToItems.update(testId, item)


def calcAmountForContainerTypeId(containerTypeId, amount):
    CTissueAmountForContainerType.update(containerTypeId, amount)


def getAmountForAcontainerTypeId(containerTypeId):
    return CTissueAmountForContainerType.get(containerTypeId)
