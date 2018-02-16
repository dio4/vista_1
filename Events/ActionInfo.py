# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Accounting.PayStatusInfo import CPayStatusInfo
from Events.Action import CAction, CActionTypeCache
from Events.ContractTariffCache import CContractTariffCache
from Events.MKBInfo import CMKBInfo, CMorphologyMKBInfo
from Events.MapActionTypeToServiceIdList import CMapActionTypeIdToServiceIdList
from Events.Service import CServiceInfo
from Orgs.PersonInfo import CPersonInfo
from Orgs.Utils import COrgInfo, COrgStructureInfo, getActionTypeOrgStructureIdList
from TissueJournal.TissueInfo import CTakenTissueJournalInfo, CTissueTypeInfo
from library.PrintInfo import CDateTimeInfo, CInfo, CInfoList, CInfoProxyList, CRBInfo, CTemplatableInfoMixin
from library.Utils import forceBool, forceDate, forceDateTime, forceDouble, forceInt, forceRef, forceString
from library.exception import CException


class CActionTypeTissueTypeInfoList(CInfoList):
    u""" Биоматериалы, связанные с типом действия """
    def __init__(self, context, actionTypeId):
        CInfoList.__init__(self, context)
        self._actionTypeId = actionTypeId

    def _load(self):
        db = QtGui.qApp.db
        tableATTT = db.table('ActionType_TissueType')
        idList = db.getIdList(tableATTT, tableATTT['tissueType_id'], tableATTT['master_id'].eq(self._actionTypeId)) if self._actionTypeId else []
        self._items = [self.getInstance(CTissueTypeInfo, id) for id in idList]
        return True


class CActionTypeInfo(CInfo):
    def __init__(self, context, actionType):
        CInfo.__init__(self, context)
        self._actionType = actionType
        self._loaded = True
        self._ok = True

    def _getGroup(self):
        groupId = self._actionType.groupId if self._actionType else None
        actionType = CActionTypeCache.getById(groupId) if groupId else None
        return self.getInstance(CActionTypeInfo, actionType)

    def __nonzero__(self):
        return bool(self._actionType)

    def __cmp__(self, other):
        selfKey = self._actionType.id if self._actionType else None
        otherKey = other._actionType.id if other._actionType else None if isinstance(other, CActionTypeInfo) else None
        return cmp(selfKey, otherKey)

    def getOrgStructures(self, includeInheritance=False):
        idList = getActionTypeOrgStructureIdList(self._actionType.id, includeInheritance) if self._actionType else []
        return [self.getInstance(COrgStructureInfo, id) for id in idList]

    group = property(_getGroup)
    id = property(lambda self: self._actionType.id if self._actionType else None)
    class_ = property(lambda self: self._actionType.class_ if self._actionType else None)
    code = property(lambda self: self._actionType.code if self._actionType else None)
    flatCode = property(lambda self: self._actionType.flatCode if self._actionType else None)
    name = property(lambda self: self._actionType.name if self._actionType else None)
    title = property(lambda self: self._actionType.title if self._actionType else None)
    showTime = property(lambda self: self._actionType.showTime if self._actionType else None)
    isMes = property(lambda self: self._actionType.isMes if self._actionType else None)
    isPrinted = property(lambda self: self._actionType.isPrinted if self._actionType else True)
    nomenclativeService = property(lambda self: self.getInstance(CServiceInfo, self._actionType.nomenclativeServiceId if self._actionType else None))
    tissueTypes = property(lambda self: self.getInstance(CActionTypeTissueTypeInfoList, self._actionType.id))
    isHtml = property(lambda self: self._actionType.isHtml() if self._actionType else None)
    hasAssistant = property(lambda self: self._actionType.hasAssistant if self._actionType else None)
    recommendationControl = property(lambda self: self._actionType.recommendationControl if self._actionType else None)
    orgStructures = property(getOrgStructures)
    contextName = property(lambda self: self._actionType.context if self._actionType else u'',
                           doc=u"""
                                      Имя контекста печати для типа действия
                                      :rtype : unicode
                                  """)


class CActionTypeInfoList(CInfoList):
    def __init__(self, context):
        CInfoList.__init__(self, context)
        self._idList = []
        self._loaded = True
        self._ok = True

    def _setIdList(self, idList):
        db = QtGui.qApp.db
        self._idList = idList[:]
        self._items = [self.getInstance(CActionTypeInfo, CActionTypeCache.getById(id))
                       for id in self._idList
                       ]

    idList = property(lambda self: self._idList, _setIdList)


class CCookedActionInfo(CActionTypeInfo, CTemplatableInfoMixin):
    def __init__(self, context, record, action):
        CActionTypeInfo.__init__(self, context, action.getType() if action else None)
        self._record = record
        self._action = action
        self._eventInfo = None
        self._assistans = None
        self._loaded = True
        self._ok = True
        self._price = None
        self._servicesIdList = None
        from Events.EventInfo import CMesInfo
        if self._record:
            MES_id = forceRef(self._record.value('MES_id'))
            event_id = forceRef(self._record.value('event_id'))
        else:
            MES_id = None
            event_id = None
        self._mes = self.getInstance(CMesInfo, MES_id, event_id)
        self.currentPropertyIndex = -1

    def getPrintTemplateContext(self):
        return self._action.getType().context

    def getEventInfo(self):
        if not self._eventInfo:
            from Events.EventInfo import CEventInfo
            eventId = forceRef(self._record.value('event_id')) if self._record else None
            self._eventInfo = self.getInstance(CEventInfo, eventId)
        return self._eventInfo

    def getFinanceInfo(self):
        financeId = forceRef(self._record.value('finance_id')) if self._record else None
        if financeId:
            from Events.EventInfo import CFinanceInfo
            return self.getInstance(CFinanceInfo, financeId)
        elif self.getEventInfo():
            return self.getEventInfo().finance
        else:
            from Events.EventInfo import CFinanceInfo
            return self.getInstance(CFinanceInfo, None)

    def getContractInfo(self):
        from Events.EventInfo import CContractInfo
        contractId = forceRef(self._record.value('contract_id')) if self._record else None
        if contractId:
            return self.getInstance(CContractInfo, contractId)
        return self.getEventInfo().contract

    def _getTariffDescr(self):
        event = self.getEventInfo()
        return event.getTariffDescrEx(self.getContractInfo().id)

    def _getServicesIdList(self):
        if self._servicesIdList is None:
            if not hasattr(self.context, 'mapActionTypeIdToServiceIdList'):
                self.context.mapActionTypeIdToServiceIdList = CMapActionTypeIdToServiceIdList
            actionTypeId = self._actionType.id
            financeId = self.getFinanceInfo().id
            self._servicesIdList = self.context.mapActionTypeIdToServiceIdList.getActionTypeServiceIdList(actionTypeId, financeId)
        return self._servicesIdList

    def getServices(self):
        return [self.getInstance(CServiceInfo, serviceId) for serviceId in self._getServicesIdList()]

    def getService(self):
        servicesIdList = self._getServicesIdList()
        serviceId = servicesIdList[0] if servicesIdList else None
        return self.getInstance(CServiceInfo, serviceId)

    def getPrice(self):
        if self._price is None:
            tariffDescr = self._getTariffDescr()
            tariffMap = tariffDescr.actionTariffMap
            tariffCategoryId = self.person.tariffCategory.id
            self._price = CContractTariffCache.getPrice(tariffMap, self._getServicesIdList(), tariffCategoryId)
        return self._price

    def getOrgInfo(self):
        orgId = forceRef(self._record.value('org_id')) if self._record else None
        if not orgId:
            orgId = self._actionType.defaultOrgId
        return self.getInstance(COrgInfo, orgId)

    def getAssistants(self):
        if self._assistans is None:
            self._assistans = CAction.loadAssistants(self.id)
        return self._assistans

    def getData(self):
        itemId = forceRef(self._record.value('id')) if self._record else None
        eventInfo = self.getEventInfo()
        eventActions = eventInfo.actions
        eventActions._idList = [itemId]
        eventActions._items = [self]
        eventActions._loaded = True

        return {
            'event'             : eventInfo,
            'action'            : self,
            'client'            : eventInfo.client,
            'actions'           : eventActions,
            'currentActionIndex': 0,
            'tempInvalid'       : None
        }

    def setCurrentPropertyIndex(self, currentPropertyIndex):
        self.currentPropertyIndex = currentPropertyIndex

    def getRecommendationInfo(self):
        from Events.EventInfo import CRecommendationInfo
        db = QtGui.qApp.db
        idList = db.getIdList('Recommendation', where='execAction_id = %d' % forceInt(self._record.value('id')))
        recommendationId = idList[0] if self._record and len(idList) > 0 else None
        return self.getInstance(CRecommendationInfo, recommendationId)

    def getMKBName(self):
        MKB = forceString(self._record.value('MKB')) if self._record else ''
        return forceString(QtGui.qApp.db.translate('MKB_Tree', 'DiagID', MKB, 'DiagName')) if MKB else ''

    def getChildren(self):
        db = QtGui.qApp.db
        tableAction = db.table('Action')
        actionId = forceRef(self._record.value('id'))
        return [self.getInstance(CCookedActionInfo, record, CAction(record=record))
                for record in db.iterRecordList(tableAction, '*', [tableAction['parent_id'].eq(actionId),
                                                                   tableAction['deleted'].eq(0)])]

    id = property(lambda self: forceRef(self._record.value('id')))
    typeId = property(lambda self: self._actionType.id)
    type = property(lambda self: self._actionType)
    event = property(getEventInfo)
    directionDate = property(lambda self: CDateTimeInfo(forceDateTime(self._record.value('directionDate'))))
    begDate = property(lambda self: CDateTimeInfo(forceDateTime(self._record.value('begDate'))))
    plannedEndDate = property(lambda self: CDateTimeInfo(forceDateTime(self._record.value('plannedEndDate'))))
    endDate = property(lambda self: CDateTimeInfo(forceDateTime(self._record.value('endDate'))))
    isUrgent = property(lambda self: forceBool(self._record.value('isUrgent')))
    coordDate = property(lambda self: CDateTimeInfo(forceDate(self._record.value('coordDate'))))
    coordAgent = property(lambda self: forceString(self._record.value('coordAgent')))
    coordInspector = property(lambda self: forceString(self._record.value('coordInspector')))
    coordText = property(lambda self: forceString(self._record.value('coordText')))
    status = property(lambda self: forceInt(self._record.value('status')))
    office = property(lambda self: forceString(self._record.value('office')))
    note = property(lambda self: forceString(self._record.value('note')))
    amount = property(lambda self: forceDouble(self._record.value('amount')))
    uet = property(lambda self: forceDouble(self._record.value('uet')))
    setPerson = property(lambda self: self.getInstance(CPersonInfo, forceRef(self._record.value('setPerson_id'))))
    person = property(lambda self: self.getInstance(CPersonInfo, forceRef(self._record.value('person_id'))))
    assistants = property(lambda self: self.getAssistants())
    assistant = property(lambda self: self.getInstance(CPersonInfo,
                                                       self.assistants['assistant'].id if self.assistants.has_key('assistant') else None)
                                                       if self.hasAssistant else None)
    # expose = property(lambda self: forceBool(self._record.value('expose')))
    account = property(lambda self: forceBool(self._record.value('account')))
    MKB = property(lambda self: self.getInstance(CMKBInfo, forceString(self._record.value('MKB'))))
    MKBName = property(getMKBName)
    morphologyMKB = property(lambda self: self.getInstance(CMorphologyMKBInfo, forceString(self._record.value('morphologyMKB'))))
    mes = property(lambda self: self._mes)
    services = property(getServices)
    service = property(getService) ### kill it!
    price = property(getPrice)
    contract = property(getContractInfo)
    finance = property(getFinanceInfo)
    payStatus = property(lambda self: forceInt(self._record.value('payStatus')))
    payStatusInfo = property(lambda self: self.getInstance(CPayStatusInfo, forceInt(self._record.value('payStatus'))))
    takenTissueJournal = property(lambda self: self.getInstance(CTakenTissueJournalInfo, forceRef(self._record.value('takenTissueJournal_id'))))
    organization = property(getOrgInfo)
    deleted = property(lambda self: forceInt(self._record.value('deleted')))
    customSum = property(lambda self: forceDouble(self._record.value('customSum')))
    recommendation = property(getRecommendationInfo)
    children = property(getChildren)

    def __len__(self):
        self.load()
        return len(self._action.getProperties())

    def __getitem__(self, key):
        if isinstance(key, (basestring, QtCore.QString)):
            try:
                return self.getInstance(CPropertyInfo, self._action.getProperty(unicode(key)))
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
            yield self.getInstance(CPropertyInfo, property)

    def __contains__(self, key):
        if isinstance(key, (basestring, QtCore.QString)):
            return self._action.containsPropertyWithName(key)
        if isinstance(key, (int, long)):
            return 0 <= key < len(self._action.getPropertiesById())
        else:
            raise TypeError, u'Action property subscription must be string or integer'


class CActionInfo(CCookedActionInfo):
    def __init__(self, context, actionId):
        db = QtGui.qApp.db
        record = db.getRecord('Action', '*', actionId)
        action = CAction(record=record)
        CCookedActionInfo.__init__(self, context, record, action)


class CUnitInfo(CRBInfo):
    tableName = 'rbUnit'


class CPropertyInfo(CInfo):
    def __init__(self, context, property):
        CInfo.__init__(self, context)
        self._property = property
        self._loaded = True
        self._ok = True

    value = property(lambda self: self._property.getInfo(self.context))
    shortName = property(lambda self: self._property._type.shortName)
    name = property(lambda self: self._property._type.name)
    descr = property(lambda self: self._property._type.descr)
    unit = property(lambda self: self.getInstance(CUnitInfo, self._property.getUnitId()))
    norm = property(lambda self: self._property.getNorm())
    isAssigned = property(lambda self: self._property.isAssigned())
    evaluation = property(lambda self: self._property.getEvaluation())
    visibleInJobTicket = property(lambda self: self._property._type.visibleInJobTicket)
    visibleInTableRedactor = property(lambda self: self._property._type.visibleInTableRedactor)

    def __str__(self):
        return forceString(self.value)


class CActionInfoList(CInfoList):
    def __init__(self, context, eventId):
        CInfoList.__init__(self, context)
        self.eventId = eventId
        self._idList = []

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('Action')
        self._idList = db.getIdList(table, 'id', table['event_id'].eq(self.eventId), 'id')
        self._items = [self.getInstance(CActionInfo, id) for id in self._idList]
        return True


class CActionInfoProxyList(CInfoProxyList):
    def __init__(self, context, models, eventInfo):
        CInfoProxyList.__init__(self, context)
        self._rawItems = []
        for model in models:
            self._rawItems.extend(model.items())
        self._items = [None] * len(self._rawItems)
        self._eventInfo = eventInfo

    def __getitem__(self, key):
        v = self._items[key]
        if v is None:
            record, action = self._rawItems[key]
            v = self.getInstance(CCookedActionInfo, record, action)
            v._eventInfo = self._eventInfo
            self._items[key] = v
        return v


# TODO: не должен ли этот класс наследоваться от CActionInfoProxyList???
class CLocActionInfoList(CInfoProxyList):
    def __init__(self, context, idList, clientSex, clientAge):
        CInfoProxyList.__init__(self, context)
        self.idList = idList
        self._items = [None] * len(self.idList)
        self.clientSex = clientSex
        self.clientAge = clientAge

    def __getitem__(self, key):
        v = self._items[key]
        if v is None:
            record = QtGui.qApp.db.getRecord('Action', '*', self.idList[key])
            action = CAction(record=record)
            v = self.getInstance(CCookedActionInfo, record, action)
            self._items[key] = v
        return v
