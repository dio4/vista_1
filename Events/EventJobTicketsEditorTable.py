# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Events.Action import CActionPropertyDomainJobTicketInfo, CJobTicketActionPropertyValueType
from Resources.JobTicketChooser import CJobTicketChooserComboBox
from Resources.JobTicketProbeModel2 import TTJItem
from library.PreferencesMixin import CPreferencesMixin
from library.TreeModel import CTreeItem, CTreeModel
from library.TreeView import CTreeView
from library.Utils import forceBool, forceDate, forceDouble, forceInt, forceRef, forceString, forceTime, getPref, \
    setPref, toVariant


class CEventJobTicketsBaseItem(CTreeItem):
    def __init__(self, parent, model):
        self._model = model
        CTreeItem.__init__(self, parent, self._getName())

    def setCheckedValues(self):
        pass

    def changeCheckedValues(self):
        pass

    def loadChildren(self):
        return []

    def _getName(self):
        return ''

    def model(self):
        return self._model


class CEventJobTicketsItem(CEventJobTicketsBaseItem):
    nameColumn = 0
    jobTicketColumn = 1
    jobTicketLIDColumn = 2

    def __init__(self, parent, model):
        self._checked = False
        self._jobTicketId = None
        self._ttjRecord = None
        CEventJobTicketsBaseItem.__init__(self, parent, model)

    def setCheckedValues(self):
        for item in self.items():
            item.setCheckedValues()

    def changeCheckedValues(self):
        for item in self.items():
            item.changeCheckedValues()

    def saveLIDs(self):
        for item in self.items():
            item.saveLIDs()

    def jobTicketId(self):
        return self._jobTicketId

    def flags(self, column):
        flags = CEventJobTicketsBaseItem.flags(self)
        if column == CEventJobTicketsItem.nameColumn:
            flags = flags | QtCore.Qt.ItemIsUserCheckable
        elif column in (CEventJobTicketsItem.jobTicketColumn, CEventJobTicketsItem.jobTicketLIDColumn):
            flags = flags | QtCore.Qt.ItemIsEditable
        return flags

    def setChecked(self, value=None):
        if value is None:
            self._checked = not self._checked
        else:
            self._checked = value
        for item in self.items():
            item.setChecked(self._checked)

    @staticmethod
    def extractValues(value):
        # TODO: skkachaev: Что такое declinedActionTypeIdList? Давайте передавать его отдельным параметром
        # if isinstance(value, QtCore.QVariant):
        #     if value.type() == QtCore.QVariant.List:
        #         jobTicketId, declinedActionTypeIdList = value.toList()[:2]
        #     else:
        #         jobTicketId, declinedActionTypeIdList = value, []
        # else:
        #     if isinstance(value, (tuple, list)) and value:
        #         if len(value) > 1:
        #             jobTicketId, declinedActionTypeIdList = value[:2]
        #         else:
        #             jobTicketId, declinedActionTypeIdList = value[0], []
        #     else:
        #         jobTicketId, declinedActionTypeIdList = value, []
        # if isinstance(declinedActionTypeIdList, QtCore.QVariant):
        #     declinedActionTypeIdList = declinedActionTypeIdList.toList()
        return forceRef(value), []  #, [forceRef(v) for v in declinedActionTypeIdList]

    def setJobTicketId(self, value):
        jobTicketId, declinedActionTypeIdList = self.extractValues(value)
        self._jobTicketId = forceRef(jobTicketId)
        for item in self.items():
            item.setJobTicketId((self._jobTicketId, declinedActionTypeIdList))
            return True
        return False

    def checked(self):
        return self._checked

    def setLID(self, value):
        for item in self.items():
            item.setLID(value)

    def data(self, column):
        if column == 0:
            return toVariant(self._name)
        elif column == 1:
            return toVariant(CJobTicketChooserComboBox.getTicketAsText(self.jobTicketId()))
        elif column == 2:
            return toVariant(forceString(self._ttjRecord.value('externalId')) if self._ttjRecord else '')
        else:
            return QtCore.QVariant()

    def actionList(self):
        return [item.action() for item in self.items() if isinstance(item, CEventJobTicketsActionItem)]

    def action(self):
        return None


class CEventJobTicketsJobTypeItem(CEventJobTicketsItem):
    def __init__(self, parent, jobTypeId, domain, model):
        self._jobTypeId = jobTypeId
        self._domain = domain
        CEventJobTicketsItem.__init__(self, parent, model)

    def domain(self):
        return self._domain

    def _getName(self):
        result = forceString(QtGui.qApp.db.translate('rbJobType', 'id', self._jobTypeId, 'CONCAT_WS(\' | \', code, name)'))
        if not result:
            result = u'----'
        return result

    def addItem(self, actionItem, jobTicketId=None):
        if self._items is None:
            self._items = []
        self._items.append(CEventJobTicketsActionItem(self, actionItem, jobTicketId, self.model()))

    def jobTypeId(self):
        return self._jobTypeId

    def loadChildren(self):
        return self._item

    @staticmethod
    def checkServiceUnitLimits(jobTicketId, action, usedBySiblingsItems=None):
        if not usedBySiblingsItems:
            usedBySiblingsItems = []
        currentSuperviseUnit = 0.0
        if jobTicketId:
            db = QtGui.qApp.db
            tableJobTicket = db.table('Job_Ticket')
            tableJob = db.table('Job')
            tableService = db.table('rbService')
            tableActionPropertyJobTicket = db.table('ActionProperty_Job_Ticket')
            tableActionProperty = db.table('ActionProperty')
            tableActionType = db.table('ActionType')
            tableAction = db.table('Action')

            jobTicketTime = forceTime(db.translate(tableJobTicket, tableJobTicket['id'], jobTicketId, tableJobTicket['datetime']))
            jobId = db.translate(tableJobTicket, tableJobTicket['id'], jobTicketId, tableJobTicket['master_id'])

            if jobTicketTime != QtCore.QTime(0, 0, 0):
                jobLimit = forceDouble(db.translate(tableJob, tableJob['id'], jobId, tableJob['limitSuperviseUnit']))
                if jobLimit > CJobTicketChooserComboBox.superviseUnitLimitPrecision:
                    if action:
                        serviceCode = action.getType().code
                        currentSuperviseUnit = forceDouble(db.translate(tableService, tableService['code'], serviceCode, tableService['superviseComplexityFactor']))
                    else:
                        currentSuperviseUnit = 0.0

                    tableEx = tableJobTicket.leftJoin(tableJob, tableJob['id'].eq(tableJobTicket['master_id']))
                    tableEx = tableEx.leftJoin(tableActionPropertyJobTicket, tableActionPropertyJobTicket['value'].eq(tableJobTicket['id']))
                    tableEx = tableEx.leftJoin(tableActionProperty, tableActionProperty['id'].eq(tableActionPropertyJobTicket['id']))
                    tableEx = tableEx.leftJoin(tableAction, tableAction['id'].eq(tableActionProperty['action_id']))
                    tableEx = tableEx.leftJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
                    tableEx = tableEx.leftJoin(tableService, tableService['code'].eq(tableActionType['code']))
                    cols = [
                        tableService['superviseComplexityFactor']
                    ]
                    cond = [
                        tableJob['deleted'].eq(0),
                        tableJob['id'].eq(jobId),
                        tableAction['deleted'].eq(0)
                    ]
                    used = 0.0
                    for record in db.getRecordListGroupBy(tableEx, cols, cond, group=tableJobTicket['id']):
                        used += forceDouble(record.value('superviseComplexityFactor'))
                    if (currentSuperviseUnit + used + sum(usedBySiblingsItems) - jobLimit) > CJobTicketChooserComboBox.superviseUnitLimitPrecision:
                        return False, currentSuperviseUnit

            else:
                jobIsOvertime = forceBool(db.translate(tableJob, tableJob['id'], jobId, tableJob['isOvertime']))
                if not jobIsOvertime:
                    return False, currentSuperviseUnit
        return True, currentSuperviseUnit

    def setJobTicketId(self, value):
        jobTicketId, declinedActionTypeIdList = self.extractValues(value)
        isSuccess = False
        usedBySiblingsItems = []
        for item in self.items():
            isMayBeAdded, currentSuperviseUnit = self.checkServiceUnitLimits(jobTicketId, item.action(), usedBySiblingsItems)
            for action in item.actionList():
                if action and action.getType().id in declinedActionTypeIdList:
                    isMayBeAdded = False
                    break
            if isMayBeAdded:
                if item.setJobTicketId((jobTicketId, declinedActionTypeIdList)):
                    usedBySiblingsItems.append(currentSuperviseUnit)
                    isSuccess = True

        if isSuccess:
            self._jobTicketId = forceRef(jobTicketId)
        return isSuccess


class CEventJobTicketsActionItem(CEventJobTicketsItem):
    def __init__(self, parent, actionItem, jobTicketId, model):
        self._actionItem = actionItem
        CEventJobTicketsItem.__init__(self, parent, model)
        self.setJobTicketId(jobTicketId)
        ttj_id = self.record().value('takenTissueJournal_id')
        if not ttj_id.isNull():
            self._ttjRecord = QtGui.qApp.db.getRecord('TakenTissueJournal', '*', ttj_id)

    def setCheckedValues(self):
        if self.checked() and self.jobTicketId():
            self.setCheckedValuesEx()

    def changeCheckedValues(self):
        if self.checked():
            self.setCheckedValuesEx()

    def saveLIDs(self):
        if self.checked() and self._ttjRecord:
            QtGui.qApp.db.insertOrUpdate('TakenTissueJournal', self._ttjRecord)
            self.record().setValue('takenTissueJournal_id', self._ttjRecord.value('id'))

    def setCheckedValuesEx(self):
        action = self.action()
        actionType = action.getType()
        propertyTypeList = actionType.getPropertiesById().values()
        jobTicketId = self.jobTicketId()
        for propertyType in propertyTypeList:
            property = action.getPropertyById(propertyType.id)
            if type(property.type().valueType) == CJobTicketActionPropertyValueType:
                property.setValue(jobTicketId)
                date = forceDate(QtGui.qApp.db.translate('Job_Ticket', 'id', jobTicketId, 'datetime'))
                date = date.addDays(self.model().getTicketDuration(jobTicketId))
                action.getRecord().setValue('plannedEndDate', QtCore.QVariant(date))

    def setJobTicketId(self, value, force=True):
        jobTicketId, declinedActionTypeIdList = self.extractValues(value)
        if self.action() and self.action().getType().id in declinedActionTypeIdList:
            return False
        if force or not self._jobTicketId:
            self._jobTicketId = jobTicketId
            return True
        return False

    def setLID(self, value):
        if not self._ttjRecord:
            self._ttjRecord = TTJItem.getNewRecord()
        self._ttjRecord.setValue('externalId', toVariant(value))

    def actionList(self):
        return [self.action()]

    def action(self):
        return self.actionItem()[1]

    def record(self):
        return self.actionItem()[0]

    def actionItem(self):
        return self._actionItem

    def _getName(self):
        return self.action().getType().name

    def domain(self):
        return self.parent().domain()

    def jobTypeId(self):
        return self.parent().jobTypeId()


class CEventJobTicketsRootItem(CEventJobTicketsItem):
    def __init__(self, model):
        CEventJobTicketsItem.__init__(self, None, model)
        self._mapJobTypeIdToItem = {}

    def getJobTypeItem(self, jobTypeId, domain):
        result = self._mapJobTypeIdToItem.get(jobTypeId, None)
        if not result:
            result = CEventJobTicketsJobTypeItem(self, jobTypeId, domain, self.model())
            self._mapJobTypeIdToItem[jobTypeId] = result
        return result

    def loadChildren(self):
        def getJobTypeId(domain, map):
            result = map.get(domain, None)
            if not result:
                jobTypeCode = CActionPropertyDomainJobTicketInfo(domain).jobTypeCode
                result = forceRef(QtGui.qApp.db.translate('rbJobType', 'code', jobTypeCode, 'id'))
                map[domain] = result
            return result

        mapDomainToJobTypeId = {}
        modelItems = self.model().actionModelsItemList()
        for item in modelItems:
            record, action = item
            actionType = action.getType()
            propertyTypeList = actionType.getPropertiesById().items()
            for propertyTypeId, propertyType in propertyTypeList:
                if type(propertyType.valueType) == CJobTicketActionPropertyValueType:
                    domain = propertyType.valueDomain
                    jobTypeId = getJobTypeId(domain, mapDomainToJobTypeId)
                    jobTypeItem = self.getJobTypeItem(jobTypeId, domain)

                    property = action.getPropertyById(propertyType.id)
                    jobTicketId = property.getValue()

                    jobTypeItem.addItem(item, jobTicketId)
                    break

        return self._mapJobTypeIdToItem.values()


class CEventJobTicketsModel(CTreeModel):
    names = [u'Наименование', u'Номерок', u'LID']

    def __init__(self, parent, actionModelsItemList, clientId):
        self._actionModelsItemList = actionModelsItemList
        self._clientId = clientId
        CTreeModel.__init__(self, parent, CEventJobTicketsRootItem(self))
        self.rootItemVisible = False
        self._jobIdToTicketDuration = {}
        self.getRootItem().setChecked(True)
        self.fromEvent = False

    def getTicketDuration(self, jobTicketId):
        db = QtGui.qApp.db
        jobId = forceRef(db.translate('Job_Ticket', 'id', jobTicketId, 'master_id'))
        result = self._jobIdToTicketDuration.get(jobId, None)
        if result is None:
            jobTypeId = forceRef(db.translate('Job', 'id', jobId, 'jobType_id'))
            result = forceInt(db.translate('rbJobType', 'id', jobTypeId, 'ticketDuration'))
            self._jobIdToTicketDuration[jobId] = result
        return result

    def setCheckedValues(self):
        self.getRootItem().setCheckedValues()

    def changeCheckedValues(self):
        self.getRootItem().changeCheckedValues()

    def saveLIDs(self):
        self.getRootItem().saveLIDs()

    def actionModelsItemList(self):
        return self._actionModelsItemList

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 3

    def clientId(self):
        return self._clientId

    def getEditorInitValues(self, index):
        item = index.internalPointer()
        clientId = self.clientId()
        if item:
            actionList = item.actionList()
            domain = item.domain()
            return actionList, domain, clientId
        return [], None, clientId

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and section in range(0, self.columnCount()) and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(CEventJobTicketsModel.names[section])
        return QtCore.QVariant()

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags
        item = index.internalPointer()
        if not item:
            return QtCore.Qt.NoItemFlags
        return item.flags(index.column())

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()

        column = index.column()
        if role == QtCore.Qt.CheckStateRole and column == CEventJobTicketsItem.nameColumn:
            item = index.internalPointer()
            if item:
                return QtCore.QVariant(QtCore.Qt.Checked if item.checked() else QtCore.Qt.Unchecked)
        elif role == QtCore.Qt.EditRole:
            item = index.internalPointer()
            if item:
                if column == CEventJobTicketsItem.jobTicketColumn:
                    return QtCore.QVariant(item.jobTicketId())
                elif column == CEventJobTicketsItem.jobTicketLIDColumn and item._ttjRecord:
                    return toVariant(forceString(item._ttjRecord.value('externalId')))
        return CTreeModel.data(self, index, role)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid():
            return False

        if role == QtCore.Qt.CheckStateRole:
            item = index.internalPointer()
            if item:
                item.setChecked()
                self.emitColumnChanged(index.column())
                return True

        elif role == QtCore.Qt.EditRole:
            col = index.column()
            item = index.internalPointer()
            if item:
                if col == CEventJobTicketsView.jobTicketColumn:
                    record = index.internalPointer().items()
                    if record:
                        record = record[0].record()
                        if forceString(record.value('status')) == u'2':
                            return False
                        if forceRef(value):
                            for ticket in item._items:
                                ticket.setJobTicketId(value)
                    elif forceRef(value):
                        item.setJobTicketId(value)
                    self.emitColumnChanged(col)
                    return True
                elif col == CEventJobTicketsView.jobTicketLIDColumn:
                    item.setLID(value)
                    self.emitColumnChanged(col)
                    return True
        return False

    def emitCellChanged(self, row, column):
        index = self.index(row, column)
        self.emitIndexChanged(index)

    def emitRowChanged(self, row):
        self.emitRowsChanged(row, row)

    def emitRowsChanged(self, begRow, endRow):
        index1 = self.index(begRow, 0)
        index2 = self.index(endRow, self.columnCount())
        self.emitIndexChanged(index1, index2)

    def emitColumnChanged(self, column):
        index1 = self.index(0, column)
        index2 = self.index(self.rowCount(), column)
        self.emitIndexChanged(index1, index2)

    def emitIndexChanged(self, index1, index2=None):
        index2 = index1 if index2 is None else index2
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index1, index2)


class CEventJobTicketsDelegate(QtGui.QItemDelegate):
    def __init__(self, parent=None):
        QtGui.QItemDelegate.__init__(self, parent)

    def commit(self):
        editor = self.sender()
        self.emit(QtCore.SIGNAL('commitData(QWidget *)'), editor)

    def commitAndCloseEditor(self):
        editor = self.sender()
        self.emit(QtCore.SIGNAL('commitData(QWidget *)'), editor)
        self.emit(QtCore.SIGNAL('closeEditor(QWidget *,QAbstractItemDelegate::EndEditHint)'), editor, QtGui.QAbstractItemDelegate.NoHint)

    def createEditor(self, parent, option, index):
        model = index.model()
        actionList, domain, clientId = model.getEditorInitValues(index)
        editor = CJobTicketActionPropertyValueType.CPropEditor(actionList, domain, parent, clientId)
        self.connect(editor, QtCore.SIGNAL('commit()'), self.commit)
        self.connect(editor, QtCore.SIGNAL('editingFinished()'), self.commitAndCloseEditor)
        return editor

    def setEditorData(self, editor, index):
        model = index.model()
        value = model.data(index, QtCore.Qt.EditRole)
        if index.internalPointer():
            if 'record' in dir(index.internalPointer()):
                record = index.internalPointer().record()
            elif 'items' in dir(index.internalPointer()) and index.internalPointer().items():
                record = index.internalPointer().items()[0].record()
            else:
                record = None

            # if record and forceString(record.value('status')) == u'2' and self._jobTicketId:
            #      editor.setEnabled(False)

            if index.internalPointer()._jobTicketId:
                status = forceString(QtGui.qApp.db.translate('Job_Ticket', 'id', index.internalPointer()._jobTicketId, 'status'))
                if status == '2':
                    editor.setEnabled(False)

        editor.setValue(value)

    def setModelData(self, editor, model, index):
        model = index.model()
        value = editor.value()
        declinedActionTypeIdList = []
        for info in editor.actionTypeLimitInfo.values():
            if info['available'] < info['required']:
                declinedActionTypeIdList.extend(info['childrenIdList'])
        model.setData(index, toVariant(value))

    def sizeHint(self, option, index):
        return QtCore.QSize(self.parent().columnWidth(index.column()), 25)

    def paint(self, painter, option, index):
        rect = self.parent().visualRect(index)
        painter.setPen(QtGui.QColor(192, 192, 192))
        painter.drawLine(rect.left(), rect.bottom(), rect.right(), rect.bottom())
        QtGui.QItemDelegate.paint(self, painter, option, index)


class CEventJobTicketsDelimiterPainterDelegate(QtGui.QItemDelegate):
    def paint(self, painter, option, index):
        rect = self.parent().visualRect(index)
        painter.setPen(QtGui.QColor(192, 192, 192))
        painter.drawLine(rect.left() + 6, rect.bottom(), rect.right(), rect.bottom())
        QtGui.QItemDelegate.paint(self, painter, option, index)


class CEventJobTicketsLIDDelegate(QtGui.QItemDelegate):
    def createEditor(self, parent, option, index):
        return QtGui.QLineEdit(parent)

    def setEditorData(self, editor, index):
        model = index.model()
        value = model.data(index, QtCore.Qt.EditRole)
        editor.setText(forceString(value))

    def setModelData(self, editor, model, index):
        model = index.model()
        value = editor.text()
        model.setData(index, toVariant(value))

    def paint(self, painter, option, index):
        rect = self.parent().visualRect(index)
        painter.setPen(QtGui.QColor(192, 192, 192))
        painter.drawLine(rect.left(), rect.bottom(), rect.right(), rect.bottom())
        QtGui.QItemDelegate.paint(self, painter, option, index)


class CEventJobTicketsView(CTreeView, CPreferencesMixin):
    jobTicketNameColumn = 0
    jobTicketColumn = 1
    jobTicketLIDColumn = 2

    def __init__(self, parent):
        CTreeView.__init__(self, parent)
        self.setItemDelegateForColumn(CEventJobTicketsView.jobTicketColumn, CEventJobTicketsDelegate(self))
        self.setItemDelegateForColumn(CEventJobTicketsView.jobTicketNameColumn, CEventJobTicketsDelimiterPainterDelegate(self))
        self.setItemDelegateForColumn(CEventJobTicketsView.jobTicketLIDColumn, CEventJobTicketsLIDDelegate(self))

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
