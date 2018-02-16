# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui, QtSql

from Events.Utils import checkTissueJournalStatus
from library.Action import CAction, CActionType
from library.DateEdit import CDateEdit
from library.PreferencesMixin import CPreferencesMixin
from library.TreeModel import CTreeModel, CTreeItem, CTreeItemWithId
from library.Utils import forceBool, forceDateTime, forceDouble, forceInt, forceRef, forceString, getPref, \
    setPref, calcAgeTuple
from library.crbcombobox import CRBComboBox


class TreeColumns:
    NAME = 0
    EXTERNAL_ID = 1
    TISSUE_TYPE = 2
    CONTAINER_TYPE = 3

r = None


class EditableRowMixin:
    def createEditor(self, parent, column):
        editor = QtGui.QLineEdit(parent)
        return editor

    def setEditorData(self, column, editor, value):
        editor.setText(forceString(value))

    def getEditorData(self, column, editor):
        return unicode(editor.text())

    def setExternalId(self, value):
        raise NotImplementedError

    def containerColor(self):
        return QtCore.QVariant()


class TTJItem:
    def __init__(self, model, record=None):
        self._model = model  # type: CJobTicketProbeModel
        self._record = record
        if record:
            self.tissueType = forceRef(record.value('tissueType_id'))
            self.externalID = forceString(record.value('externalId'))
            # self.unit = forceRef(record.value('unit_id'))
            self.datetimeTaken = forceDateTime(record.value('datetimeTaken'))
            self.execPerson = forceRef(record.value('execPerson_id'))
        else:
            self.tissueType = self.execPerson = None
            self.externalID = u''
            # self.unit
            # self.datetimeTaken

    @staticmethod
    def fromAction(model, action):
        return TTJItem(model, QtGui.qApp.db.getRecord('TakenTissueJournal', '*',
                                                      forceRef(action.getRecord().value('takenTissueJournal_id'))))

    def isEditable(self, action):
        return forceInt(action.getRecord().value('status')) < 2

    def save(self, client_id, number, status, action, datetime):
        """
        :type status: int
        :type number: int
        :type client_id: int
        :type action: CAction
        """
        ttj = QtGui.qApp.db.table('TakenTissueJournal')
        new = False
        rec = self._record
        if not rec or forceString(rec.value('externalId') != self.externalID):
            extid_rec = QtGui.qApp.db.getRecordEx(ttj, '*', [ttj['client_id'].eq(client_id),
                                                             ttj['number'].eq(number),
                                                             ttj['externalId'].eq(self.externalID),
                                                             ttj['tissueType_id'].eq(self.tissueType)])
            self._record = rec = extid_rec if extid_rec else TTJItem.getNewRecord()
            rec.setValue('client_id', client_id)
            rec.setValue('amount', 1)
            rec.setValue('note', '')
            rec.setValue('unit_id', QtGui.qApp.db.translate('ActionType_TissueType', 'master_id', action.getType().id, 'unit_id'))
            new = True
        rec.setValue('tissueType_id', self.tissueType)
        rec.setValue('externalId', self.externalID)
        rec.setValue('number', number)
        if status > 0:  # не "ожидание"
            rec.setValue('datetimeTaken', datetime)
            rec.setValue('execPerson_id', QtGui.qApp.userId)
        QtGui.qApp.db.insertOrUpdate('TakenTissueJournal', rec)
        if new:
            action_rec = action.getRecord()
            action_rec.setValue('takenTissueJournal_id', rec.value('id'))
            action_rec.setValue('status', status)
            QtGui.qApp.db.updateRecord('Action', action_rec)
        checkTissueJournalStatus(forceRef(rec.value('id')), fromJobTicketEditor=True)

    @staticmethod
    def getNewRecord():
        rec = QtSql.QSqlRecord()

        id_field = QtSql.QSqlField('id', QtCore.QVariant.ULongLong)
        id_field.setAutoValue(True)
        rec.append(id_field)

        rec.append(QtSql.QSqlField('client_id', QtCore.QVariant.ULongLong))
        rec.append(QtSql.QSqlField('amount', QtCore.QVariant.ULongLong))
        rec.append(QtSql.QSqlField('note', QtCore.QVariant.String))
        rec.append(QtSql.QSqlField('tissueType_id', QtCore.QVariant.ULongLong))
        rec.append(QtSql.QSqlField('unit_id', QtCore.QVariant.ULongLong))
        rec.append(QtSql.QSqlField('number', QtCore.QVariant.String))
        rec.append(QtSql.QSqlField('status', QtCore.QVariant.ULongLong))
        rec.append(QtSql.QSqlField('datetimeTaken', QtCore.QVariant.DateTime))
        rec.append(QtSql.QSqlField('execPerson_id', QtCore.QVariant.ULongLong))
        rec.append(QtSql.QSqlField('externalId', QtCore.QVariant.String))
        return rec


class CJobTicketRealRootItem(CTreeItem):
    def __init__(self, model):
        self._model = model  # type: CJobTicketProbeModel
        CTreeItem.__init__(self, None, u'')

    def getRoot(self):
        return CJobTicketTreeVisibleRootItem(self._model)

    def loadChildren(self, actionList=None):
        return [self.getRoot()]

    def updateChildren(self):
        self._items = [self.getRoot()]


class CJobTicketTreeVisibleRootItem(EditableRowMixin, CTreeItem):
    def __init__(self, model):
        self._model = model  # type: CJobTicketProbeModel
        self._items = []
        CTreeItem.__init__(self, None, u'')

    def loadChildren(self):
        self._items = [CJobTicketTreeTissueTypeItem(self, self._model, self._model.tissueTypes()[tt_id])
                       for tt_id in self._model.actionTree().keys()]
        return self._items

    def data(self, column):
        if column == TreeColumns.NAME:
            return QtCore.QVariant(u'Биоматериал')
        return QtCore.QVariant()

    def setExternalId(self, value):
        for item in self._items:
            item.setExternalId(value)


class CJobTicketTreeTissueTypeItem(EditableRowMixin, CTreeItem):
    def __init__(self, parent, model, record):
        self._model = model  # type: CJobTicketProbeModel
        self._record = record  # type: QtSql.QSqlRecord
        self._id = forceRef(record.value('id'))
        CTreeItem.__init__(self, parent, u'')

    def data(self, column):
        if column == TreeColumns.NAME:
            return QtCore.QVariant(self.tissueTypeName())
        return QtCore.QVariant()

    def tissueTypeName(self):
        return self._record.value('name')

    def tissueTypeID(self):
        return forceRef(self._record.value('id'))

    def loadChildren(self):
        self._items = [CJobTicketTreeActionItem(self, self._model, a) for a in self._model.actionTree()[self._id]]
        return self._items

    def setExternalId(self, value):
        for item in self._items:
            item.setExternalId(value)


class CJobTicketTreeActionItem(EditableRowMixin, CTreeItem):
    def __init__(self, parent, model, action):
        CTreeItem.__init__(self, parent, u'')
        self._model = model  # type: CJobTicketProbeModel
        self._action = action  # type: CAction

        self._ttj = action.takenTissueJournal

        if not self._ttj.tissueType:
            self._ttj.tissueType = self._parent.tissueTypeID()

        self._actionType = action.getType()  # type: CActionType
        self._tissueTypes = self.loadTissueTypes()

    def data(self, column):
        if column == TreeColumns.NAME:
            return self._actionType.name
        elif column == TreeColumns.EXTERNAL_ID:
            return self._ttj.externalID
        elif column == TreeColumns.TISSUE_TYPE:
            tt = self._model.tissueTypes()  # type: dict
            return tt[self._ttj.tissueType].value('name')
        elif column == TreeColumns.CONTAINER_TYPE:
            if self._tissueTypes[self._ttj.tissueType]['container']:
                return self._tissueTypes[self._ttj.tissueType]['container'].value('name')
        return QtCore.QVariant()

    def containerColor(self):
        if self._tissueTypes[self._ttj.tissueType]['container']:
            return QtGui.QColor(forceString(self._tissueTypes[self._ttj.tissueType]['container'].value('color')))
        return QtCore.QVariant()

    def loadChildren(self):
        return []

    def action(self):
        return self._action

    def setExternalId(self, value):
        self._ttj.externalID = value

    def setTissueType(self, value):
        self._ttj.tissueType = value

    def loadTissueTypes(self):
        out = {}
        db = QtGui.qApp.db
        attt_tbl = db.table('ActionType_TissueType')
        container_tbl = db.table('rbContainerType')
        for rec in db.getRecordList(attt_tbl, '*', attt_tbl['master_id'].eq(self._actionType.id), attt_tbl['idx']):
            out[forceRef(rec.value('tissueType_id'))] = {
                'attt': rec,
                'container': db.getRecord(container_tbl, '*', forceRef(rec.value('containerType_id')))
            }
        return out
    
    def createEditor(self, parent, column):
        if column == TreeColumns.TISSUE_TYPE:
            editor = CRBComboBox(parent)
            tbl = QtGui.qApp.db.table('rbTissueType')
            editor.setTable('rbTissueType', False, tbl['id'].inlist(self._tissueTypes.keys()))
            return editor
        else:
            return super(CJobTicketTreeActionItem, self).createEditor(parent, column)

    def setEditorData(self, column, editor, value):
        if column == TreeColumns.TISSUE_TYPE:
            editor.setValue(self._ttj.tissueType)
        else:
            return super(CJobTicketTreeActionItem, self).setEditorData(column, editor, value)

    def getEditorData(self, column, editor):
        if column == TreeColumns.TISSUE_TYPE:
            return editor.value()
        else:
            return super(CJobTicketTreeActionItem, self).getEditorData(column, editor)


class CJobTicketProbeModel(CTreeModel):
    externalIdChanged = QtCore.pyqtSignal()

    def __init__(self, parent, view):
        self._root = CJobTicketRealRootItem(self)
        CTreeModel.__init__(self, parent, self._root)
        self.rootItemVisible = False
        self._actionList = []
        self._tissueTypes = dict()
        self._actionTree = dict()
        self._parent = parent
        self._view = view  # type: CJobTicketProbeTreeView2
        self._editable = True

        for record in QtGui.qApp.db.getRecordList('rbTissueType', '*'):
            self._tissueTypes[forceRef(record.value('id'))] = record

    def setEditable(self, editable):
        self._editable = editable

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 4

    @staticmethod
    def getTissueTypeIdByAction(action):
        if action.takenTissueJournal.tissueType:
            return action.takenTissueJournal.tissueType

        ttj_id = forceRef(action.getRecord().value('takenTissueJournal_id'))
        if ttj_id:
            return forceRef(QtGui.qApp.db.translate('TakenTissueJournal', 'id', ttj_id, 'tissueType_id'))
        else:
            at_id = action.getType().id
            return forceRef(QtGui.qApp.db.translate('ActionType_TissueType', 'master_id', at_id, 'tissueType_id'))

    def buildActionTree(self):
        self._actionTree = {}
        for a in self._actionList:
            self._actionTree.setdefault(self.getTissueTypeIdByAction(a), []).append(a)

    def reset(self):
        self.buildActionTree()
        self._root.updateChildren()
        CTreeModel.reset(self)
        self._view.expandAll()

    def setActionIdList(self, lst):
        for aid in lst:
            action = CAction.getActionById(aid)
            action.takenTissueJournal = TTJItem.fromAction(self, action)
            self._actionList.append(action)
        self.reset()

    def actionList(self):
        return self._actionList

    def actionTree(self):
        return self._actionTree

    def tissueTypes(self):
        return self._tissueTypes

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                if section == TreeColumns.NAME:
                    return QtCore.QVariant(u'Анализы')
                elif section == TreeColumns.EXTERNAL_ID:
                    return QtCore.QVariant(u'Идентификатор')
                elif section == TreeColumns.TISSUE_TYPE:
                    return QtCore.QVariant(u'Биоматериал')
                elif section == TreeColumns.CONTAINER_TYPE:
                    return QtCore.QVariant(u'Контейнер')
        return QtCore.QVariant()

    def flags(self, index):
        column = index.column()
        flags = CTreeModel.flags(self, index)
        item = index.internalPointer()
        if self._editable and (column == TreeColumns.EXTERNAL_ID or
                               column == TreeColumns.TISSUE_TYPE and isinstance(item, CJobTicketTreeActionItem)):
            return flags | QtCore.Qt.ItemIsEditable
        else:
            return flags

    def data(self, index, role):
        if index.column() == TreeColumns.CONTAINER_TYPE:
            bg = index.internalPointer().containerColor()
            if isinstance(bg, QtGui.QColor):
                if role == QtCore.Qt.BackgroundRole:
                    return QtGui.QBrush(bg)
                elif role == QtCore.Qt.ForegroundRole:
                    # http://stackoverflow.com/a/1855903/5139327
                    a = 1 - (.299 * bg.red() + .587 * bg.green() + .114 * bg.blue()) / 255
                    return QtGui.QBrush(QtCore.Qt.black if a < .5 else QtCore.Qt.white)
        return CTreeModel.data(self, index, role)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            column = index.column()
            if column == TreeColumns.EXTERNAL_ID:
                item = index.internalPointer()
                if item:
                    item.setExternalId(forceString(value))
                    self.externalIdChanged.emit()
                    self.emitAllChanged()
                    return True
            elif column == TreeColumns.TISSUE_TYPE:
                item = index.internalPointer()
                if item:
                    item.setTissueType(value)
                    self.reset()
                    return True
        return False

    def emitAllChanged(self):
        index1 = self.index(0, 0)
        index2 = self.index(self.rowCount(), self.columnCount())
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index1, index2)

    # noinspection PyUnresolvedReferences
    def save(self, client_id, number, status, datetime):
        for a in self._actionList:  # type: CAction
            a.takenTissueJournal.save(client_id, number, status, a, datetime)
            a.save()


class CItemDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, parent):
        QtGui.QStyledItemDelegate.__init__(self, parent)
        self.row = self.last_row = self.column = self.row_count = 0
        self.editor = None

    def createEditor(self, parent, option, index):
        item = index.internalPointer()
        column = index.column()
        editor = item.createEditor(parent, column)
        self.connect(editor, QtCore.SIGNAL('commit()'), self.emitCommitData)
        self.connect(editor, QtCore.SIGNAL('editingFinished()'), self.commitAndCloseEditor)
        self.editor = editor
        self.row = index.row()
        self.row_count = index.model().rowCount()
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
        self.emit(QtCore.SIGNAL('closeEditor(QWidget *,QAbstractItemDelegate::EndEditHint)'), editor,
                  QtGui.QAbstractItemDelegate.NoHint)

    def eventFilter(self, obj, event):

        def editorCanEatTab():
            if isinstance(self.editor, QtGui.QDateEdit):
                return self.editor.currentSection() != QtGui.QDateTimeEdit.YearSection
            return False

        def editorCanEatBackTab():
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
                if editorCanEatBackTab():
                    self.editor.keyPressEvent(event)
                    return True
                if self.editor is not None:
                    self.parent().commitData(self.editor)
                self.parent().keyPressEvent(event)
                return True
            elif event.key() == QtCore.Qt.Key_Return:
                return True
        return QtGui.QStyledItemDelegate.eventFilter(self, obj, event)


class CJobTicketProbeTreeView2(QtGui.QTreeView, CPreferencesMixin):
    def __init__(self, parent):
        QtGui.QTreeView.__init__(self, parent)
        self.setItemDelegateForColumn(TreeColumns.EXTERNAL_ID, CItemDelegate(self))
        self.setItemDelegateForColumn(TreeColumns.TISSUE_TYPE, CItemDelegate(self))

    def loadPreferences(self, preferences):
        model = self.model()
        for i in xrange(model.columnCount()):
            width = forceInt(getPref(preferences, 'col_'+str(i), None))
            if width:
                self.setColumnWidth(i, width)

    def savePreferences(self):
        preferences = {}
        model = self.model()
        if model:
            for i in xrange(model.columnCount()):
                width = self.columnWidth(i)
                setPref(preferences, 'col_'+str(i), QtCore.QVariant(width))
        return preferences
