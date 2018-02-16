# -*- coding: utf-8 -*-
from collections import defaultdict

from PyQt4 import QtCore, QtGui

from Events.Action import CAction
from Events.ActionInfo import CActionInfo, CCookedActionInfo, CPropertyInfo
from Orgs.Utils import COrgStructureInfo
from Resources.JobTicketChooser import CJobTicketChooserComboBox
from library.ElectronicQueue.EQueueTicket import CEQTicketInfo
from library.PrintInfo import CDateTimeInfo, CInfo, CInfoList, CRBInfo
from library.Utils import forceDateTime, forceInt, forceRef, forceString
from library.exception import CException


class CJobTypeInfo(CRBInfo):
    tableName = 'rbJobType'

    def __init__(self, context, id):
        CRBInfo.__init__(self, context, id)


class CJobTicketInfo(CInfo):
    u""" Сокращённый вариант используется при печати action """

    def __init__(self, context, id):
        CInfo.__init__(self, context)
        self.id = id

    def _load(self):
        record = CJobTicketChooserComboBox.getTicketRecord(self.id) if self.id else None
        if record:
            self._initByRecord(record)
            return True
        else:
            self._initByNull()
            return False

    def _initByRecord(self, record):
        self._datetime = CDateTimeInfo(forceDateTime(record.value('datetime')))
        self._idx = forceInt(record.value('idx'))
        self._jobType = self.getInstance(CJobTypeInfo, forceRef(record.value('jobType_id')))
        self._orgStructure = self.getInstance(COrgStructureInfo, forceRef(record.value('orgStructure_id')))
        self._status = forceInt(record.value('status'))
        self._label = forceString(record.value('label'))
        self._note = forceString(record.value('note'))
        self._begDateTime = CDateTimeInfo(forceDateTime(record.value('begDateTime')))
        self._endDateTime = CDateTimeInfo(forceDateTime(record.value('endDateTime')))
        self._eQueueTicket = self.getInstance(CEQTicketInfo, forceDateTime(record.value('eQueueTicket_id')))

    def _initByNull(self):
        self._datetime = CDateTimeInfo()
        self._idx = None
        self._jobType = self.getInstance(CJobTypeInfo, None)
        self._orgStructure = self.getInstance(COrgStructureInfo, None)
        self._status = 0
        self._label = ''
        self._note = ''
        self._begDateTime = CDateTimeInfo()
        self._endDateTime = CDateTimeInfo()
        self._eQueueTicket = self.getInstance(CEQTicketInfo, None)

    def __str__(self):
        self.load()
        if self._ok:
            return u'%s, %s, %s' % (unicode(self._jobType),
                                    unicode(self._datetime),
                                    unicode(self._orgStructure))
        else:
            return ''

    begDateTime = property(lambda self: self.load()._begDateTime)
    datetime = property(lambda self: self.load()._datetime)
    endDateTime = property(lambda self: self.load()._endDateTime)
    eQueueTicket = property(lambda self: self.load()._eQueueTicket)
    idx = property(lambda self: self.load()._idx)
    jobType = property(lambda self: self.load()._jobType)
    label = property(lambda self: self.load()._label)
    note = property(lambda self: self.load()._note)
    orgStructure = property(lambda self: self.load()._orgStructure)
    status = property(lambda self: self.load()._status)


class CJobTicketsActionInfo(CActionInfo):
    def __init__(self, context, actionId, action=None):
        db = QtGui.qApp.db
        if not action:
            record = db.getRecord('Action', '*', actionId)
            action = CAction(record=record)
        else:
            record = action.getRecord()
        CCookedActionInfo.__init__(self, context, record, action)

    def isVisible(self, propertyType):
        return propertyType.visibleInJobTicket

    def __getitem__(self, key):
        if isinstance(key, (basestring, QtCore.QString)):
            try:
                property = self._action.getProperty(unicode(key))
                propertyType = property.type()
                if self.isVisible(propertyType):
                    return self.getInstance(CPropertyInfo, property)
                else:
                    actionType = self._action.getType()
                    raise CException(u'У действия типа "%s" свойство "%s" не выводится в выполнении работ' % (
                        actionType.name, unicode(key)
                    ))
            except KeyError:
                actionType = self._action.getType()
                raise CException(u'Действие типа "%s" не имеет свойства "%s"' % (actionType.name, unicode(key)))
        if isinstance(key, (int, long)):
            try:
                return self.getInstance(CPropertyInfo, self._action.getPropertyByIndex(key))
            except IndexError:
                actionType = self._action.getType()
                raise CException(u'Действие типа "%s" не имеет свойства c индексом "%s"' % (actionType.name, unicode(key)))
        else:
            raise TypeError, u'Action property subscription must be string or integer'

    def __iter__(self):
        for property in self._action.getProperties():
            if self.isVisible(property.type()):
                yield self.getInstance(CPropertyInfo, property)


class CJobTicketsActionInfoList(CInfoList):
    def __init__(self, context, idList, **kwargs):
        CInfoList.__init__(self, context)
        self._idList = idList
        self._presetActions = kwargs.get('presetActions', None)

    def _load(self):
        if self._presetActions:
            self._items = [self.getInstance(CJobTicketsActionInfo, None, action=action) for action in self._presetActions]
        else:
            self._items = [self.getInstance(CJobTicketsActionInfo, id) for id in self._idList]
        return True


class CJobTicketWithActionsInfo(CJobTicketInfo):
    u""" Расширенный вариант используется при печати из выполнения работ (список, редактор одного jobTicket) """

    def __init__(self, context, id, **kwargs):
        CJobTicketInfo.__init__(self, context, id)
        self._presetActions = kwargs.get('presetActions', None)

    def _initByRecord(self, record):
        CJobTicketInfo._initByRecord(self, record)
        if self._presetActions:
            actionIdList = []
        else:
            actionIdList = CMapJobTicketsToActionsHelper.getActionIdList(self.id)
        self._actions = self.getInstance(CJobTicketsActionInfoList, tuple(actionIdList), presetActions=self._presetActions)

    def _initByNull(self):
        CJobTicketInfo._initByNull(self)
        self._actions = []

    actions = property(lambda self: self.load()._actions)


class CJobTicketsWithActionsInfoList(CInfoList):
    def __init__(self, context, idList):
        CInfoList.__init__(self, context)
        self._idList = idList

    def _load(self):
        self._items = [self.getInstance(CJobTicketWithActionsInfo, id) for id in self._idList]
        return True


class CMapJobTicketsToActionsHelper():
    mapJobTicketToActionIdList = defaultdict(list)

    @classmethod
    def getActionIdList(cls, jobTicketId):
        return cls.mapJobTicketToActionIdList.get(jobTicketId, [])

    @classmethod
    def setActionId(cls, jobTicketId, actionId):
        actionIdList = cls.mapJobTicketToActionIdList[jobTicketId]
        if actionId not in actionIdList:
            actionIdList.append(actionId)

    @classmethod
    def invalidate(cls):
        cls.mapJobTicketToActionIdList.clear()


def makeDependentActionIdList(jobTicketIdList):
    db = QtGui.qApp.db
    tableAction = db.table('Action')
    tableAP = db.table('ActionProperty')
    tableAPJT = db.table('ActionProperty_Job_Ticket')
    tableJT = db.table('Job_Ticket')

    queryTable = tableJT.leftJoin(tableAPJT, tableAPJT['value'].eq(tableJT['id']))
    queryTable = queryTable.leftJoin(tableAP, [tableAP['id'].eq(tableAPJT['id']),
                                               tableAP['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(tableAction, [tableAction['id'].eq(tableAP['action_id']),
                                                   tableAction['deleted'].eq(0)])
    fields = [
        tableJT['id'].alias('jobTicketId'),
        tableAction['id'].alias('actionId')
    ]
    cond = [
        tableJT['id'].inlist(jobTicketIdList)
    ]

    CMapJobTicketsToActionsHelper.invalidate()
    for record in db.iterRecordList(queryTable, fields, cond):
        jobTicketId = forceRef(record.value('jobTicketId'))
        actionId = forceRef(record.value('actionId'))
        CMapJobTicketsToActionsHelper.setActionId(jobTicketId, actionId)


def getJobTicketClientIdList(jobTicketIdList):
    db = QtGui.qApp.db
    tableAction = db.table('Action')
    tableAP = db.table('ActionProperty')
    tableAPJT = db.table('ActionProperty_Job_Ticket')
    tableEvent = db.table('Event')
    tableJT = db.table('Job_Ticket')

    table = tableAPJT.innerJoin(tableAP, [tableAP['id'].eq(tableAPJT['id']),
                                          tableAP['deleted'].eq(0)])
    table = table.innerJoin(tableAction, [tableAction['id'].eq(tableAP['action_id']),
                                          tableAction['deleted'].eq(0)])
    table = table.innerJoin(tableEvent, [tableEvent['id'].eq(tableAction['event_id']),
                                         tableEvent['deleted'].eq(0)])
    cond = [
        tableAPJT['value'].inlist(jobTicketIdList)
    ]

    return db.getDistinctIdList(table, tableEvent['client_id'], cond)