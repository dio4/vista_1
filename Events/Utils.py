# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2016 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

import re
from PyQt4 import QtCore, QtGui, QtSql

from Events.ActionTemplateChoose import CActionTemplateModel
from Events.MapActionTypeToServiceIdList import CMapActionTypeIdToServiceIdList
from RefBooks.RBTissueType import TisssueTypeCounterResetType
from RefBooks.ServiceModifier import applyModifier
from Users.Rights import urCreateSeveralEvents, urCreateSeveralOMSEvents, urDisableCheckMKBInput, \
    urDisableCheckNewMKBWithOld, urNotAllowCreateManyEventsAtOneSetDate
from library.AgeSelector import checkAgeSelector, parseAgeSelector
from library.DbEntityCache import CDbEntityCache
from library.PrintInfo import CInfoContext
from library.Utils import CAgeTuple, MKBwithoutSubclassification, calcAgeInDays, countWorkDays, \
    firstHalfYearDay, firstMonthDay, firstQuarterDay, firstWeekDay, firstYearDay, forceBool, forceDate, \
    forceDouble, forceInt, forceRef, forceString, forceStringEx, forceTime, formatName, getPeriodLength, getVal, \
    lastHalfYearDay, lastMonthDay, lastQuarterDay, lastWeekDay, lastYearDay, toVariant, log
from library.constants import etcTimeTable
from library.database import CUnionTable, addDateInRange


class EventIsPrimary:
    NotSet = 0
    Primary = 1
    Secondary = 2
    Active = 3
    Transportation = 4
    Ambulatory = 5

    nameMap = {
        NotSet        : u'-',
        Primary       : u'Первичный',
        Secondary     : u'Повторный',
        Active        : u'Активное посещение',
        Transportation: u'Перевозка',
        Ambulatory    : u'Амбулаторно'
    }
    nameList = [nameMap[k] for k in sorted(nameMap.keys())]


class EventOrder:
    NotSet = 0
    Planned = 1
    Emergency = 2
    Itself = 3
    Forced = 4
    Urgent = 5

    nameMapOld = {
        NotSet   : u'-',
        Planned  : u'Плановый',
        Emergency: u'Экстренный',
        Itself   : u'Самотёком',
        Forced   : u'Принудительный',
        Urgent   : u'Неотложный',
        # u'из стационара',
        # u'из др. ЛПУ',
        # u'освидетельствование'
    }
    nameMap = dict()
    colNameMap = dict()
    nameList = [nameMapOld[k] for k in sorted(nameMapOld.keys())]

    @property
    def orderNameList(self):
        self.fillMap()
        return self.colNameMap

    @classmethod
    def fillCmb(cls, cmbOrder):
        if QtGui.qApp.region() == '23':
            cmbOrder.setTable(
                'rbEventOrder',
                filter='rbEventOrder.codeKK IS NOT NULL',
                codeFieldName='codeKK',
                addNone=False
            )
        else:
            cmbOrder.setTable('rbEventOrder', addNone=False)

    @classmethod
    def fillMap(cls):
        if not cls.nameMap:
            db = QtGui.qApp.db
            if QtGui.qApp.region() == '23':
                stmt = u'SELECT rbEventOrder.codeKK AS code, rbEventOrder.name AS name  from rbEventOrder ' \
                       u'WHERE rbEventOrder.codeKK IS NOT NULL'
            else:
                stmt = u'SELECT rbEventOrder.code AS code, rbEventOrder.name AS name  from rbEventOrder'

            records = db.getRecordList(stmt=stmt)
            for x in records:
                cls.nameMap[forceString(x.value('code'))] = forceString(x.value('name'))
                cls.colNameMap[forceInt(x.value('code'))] = forceString(x.value('name'))
            cls.nameList = [cls.nameMap[k] for k in sorted(cls.nameMap.keys())]

    @classmethod
    def getName(cls, order):
        if not cls.nameMap:
            cls.fillMap()
        return cls.nameMap.get(forceString(order), '{%s}' % order)


def getWorkEventTypeFilter(queryTable = None, cond = None):
    u"""Отфильтровывает эвенты так, чтобы туда не попали технические
        f(CJoin, []) -> CJoin
        @:param queryTable:
        @:param cond: Добавляет новое условие, если его ещё нет
        @:return: Джоинит rbEventTypePurpose, если нужно, к queryTable
        f(None, None) -> str. deprecated!
        @:return Выдаёт отвратительный запрос.
    """
    if queryTable is None or cond is None:
        return '(EventType.purpose_id NOT IN (SELECT rbEventTypePurpose.id from rbEventTypePurpose where rbEventTypePurpose.code = \'0\'))'
    else:
        db = QtGui.qApp.db
        tableEventType = db.table('EventType')
        tablePurpose = db.table('rbEventTypePurpose')
        if not queryTable.isTableJoin(tablePurpose):
            queryTable = queryTable.innerJoin(tablePurpose, tableEventType['purpose_id'].eq(tablePurpose['id']))
        if (not tablePurpose['code'].ne('0') in cond) or (not tablePurpose['code'].notlike('0') in cond):
            cond.append(tablePurpose['code'].ne('0'))
        return queryTable


def getClientEvents(clientId, begDateFrom=None, begDateTo=None, endDateFrom=None, endDateTo=None):
    u""" Список не технических обращений пациента """
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    tableEventPurpose = db.table('rbEventTypePurpose')
    tableEventType = db.table('EventType')

    table = tableEvent
    table = table.innerJoin(tableEventType, [tableEventType['id'].eq(tableEvent['eventType_id']),
                                             tableEventType['deleted'].eq(0)])
    table = table.innerJoin(tableEventPurpose, [tableEventPurpose['id'].eq(tableEventType['purpose_id']),
                                                tableEventPurpose['code'].ne('0')])
    cond = [
        tableEvent['client_id'].eq(clientId),
        tableEvent['deleted'].eq(0)
    ]
    if begDateFrom is not None:
        cond.append(tableEvent['setDate'].dateGe(begDateFrom))
    if begDateTo is not None:
        cond.append(tableEvent['setDate'].dateGe(begDateTo))
    if endDateFrom is not None:
        cond.append(tableEvent['execDate'].dateGe(endDateFrom))
    if endDateTo is not None:
        cond.append(tableEvent['execDate'].dateGe(endDateTo))

    return db.getIdList(table, tableEvent['id'], cond)


def getOrgStructureEventTypeFilter(orgStructureId):
    idSet = set()
    db = QtGui.qApp.db
    tableOrgStructure = db.table('OrgStructure')
    tableOSET = db.table('OrgStructure_EventType')
    while orgStructureId:
        idList = db.getIdList(tableOSET, idCol='eventType_id',  where=tableOSET['master_id'].eq(orgStructureId))
        idSet.update(set(idList))
        record = db.getRecord(tableOrgStructure, ['parent_id', 'inheritEventTypes'], orgStructureId)
        if record and forceBool(record.value('inheritEventTypes')):
            orgStructureId = forceRef(record.value('parent_id'))
        else:
            orgStructureId = None
    idList = list(idSet.difference(set([None])))
    if idList:
        return db.table('EventType')['id'].inlist(idList)
    else:
        return '1'


def getEventContextData(editor):
    from Events.TempInvalidInfo import CTempInvalidInfo
    context = CInfoContext()
    eventInfo = editor.getEventInfo(context)
    if hasattr(editor, 'getTempInvalidInfo'):
        tempInvalidInfo = editor.getTempInvalidInfo(context)
    else:
        tempInvalidInfo = context.getInstance(CTempInvalidInfo, None)
    if hasattr(editor, 'getAegrotatInfo'):
        aegrotatInfo = editor.getAegrotatInfo(context)
    else:
        aegrotatInfo = context.getInstance(CTempInvalidInfo, None)
    data = {
        'event'      : eventInfo,
        'client'     : eventInfo.client,
        'tempInvalid': tempInvalidInfo,
        'aegrotat'   : aegrotatInfo,
    }
    return data


def getActionTypeMesIdList(actionTypeId, financeId, mkb=None, date=None):
    db = QtGui.qApp.db
    defaultMes = forceInt(db.translate('ActionType', 'id', actionTypeId, 'defaultMES'))
    if defaultMes == 0:
        return []

    serviceIdList = CMapActionTypeIdToServiceIdList.getActionTypeServiceIdList(actionTypeId, financeId)

    tableMesService = db.table('mes.MES_service')
    tableMesRBService = db.table('mes.mrbService')
    tableService = db.table('rbService')

    queryTable = tableMesService.innerJoin(tableMesRBService, tableMesRBService['id'].eq(tableMesService['service_id']))
    queryTable = queryTable.innerJoin(tableService, tableService['code'].eq(tableMesRBService['code']))

    cond = []
    if serviceIdList:
        cond.append(tableService['id'].inlist(serviceIdList))
    if mkb:
        pass
    if date:
        dateStr = date.toString(QtCore.Qt.ISODate)
        cond.append('IF(mes.MES_service.begDate IS NULL, 1, mes.MES_service.begDate <= DATE(\'%s\'))' % dateStr)
        cond.append('IF(mes.MES_service.endDate IS NULL, 1, mes.MES_service.endDate >= DATE(\'%s\'))' % dateStr)
    return db.getDistinctIdList(table = queryTable,
                        idCol = 'master_id',
                        where = cond )


# коды типов финиасирования, должны соотв. кодам из rbFinance
class CFinanceType(CDbEntityCache):
    budget   = 1 # бюджет
    CMI      = 2 # ОМС
    VMI      = 3 # ДМС
    cash     = 4 # платный
    paid     = 4 # платный (устар.)
    targeted = 5 # целевой
    highTechCMI = 6 # ВМП из ОМС

    allCodes = (budget, CMI, VMI, cash, targeted)

    mapCodeToId = {}
    mapIdToCode = {}
    mapIdToName = {}

    @classmethod
    def purge(cls):
        cls.mapCodeToId.clear()
        cls.mapIdToCode.clear()
        cls.mapIdToName.clear()

    @classmethod
    def register(cls, record, code=0, id=None):
        if record:
            id   = forceRef(record.value('id'))
            code = forceInt(record.value('code'))
            name = forceString(record.value('name'))
        else:
            name = 'unknow finance code=%r, id=%r' % (code, id)
        cls.mapCodeToId[code] = id
        cls.mapIdToCode[id] = code
        cls.mapIdToName[id] = name
        return id, code, name

    @classmethod
    def getId(cls, code):
        code = forceInt(code)
        if code in cls.mapCodeToId:
            return cls.mapCodeToId[code]
        else:
            cls.connect()
            db = QtGui.qApp.db
            table = db.table('rbFinance')
            id, code, name = cls.register(db.getRecordEx(table, 'id, code, name', table['code'].eq(code)), code=code)
            return id

    @classmethod
    def getCode(cls, id):
        if id in cls.mapIdToCode:
            return cls.mapIdToCode[id]
        else:
            cls.connect()
            db = QtGui.qApp.db
            table = db.table('rbFinance')
            id, code, name = cls.register(db.getRecord(table, 'id, code, name', id), id=id)
            return code

    @classmethod
    def getNameById(cls, id):
        cls.getCode(id)
        return cls.mapIdToName[id]

    @classmethod
    def getNameByCode(cls, code):
        return cls.mapIdToName[cls.getId(code)]


class CEventTypeDescription(CDbEntityCache):
    cache = {}
    mapCodeToId = {}

    def __init__(self, eventTypeId):
        db = QtGui.qApp.db
        eventTypeTable   = db.table('EventType')
        financeTable = db.table('rbFinance')
        aidKindTable = db.table('rbMedicalAidKind')
        aidTypeTable = db.table('rbMedicalAidType')
        eventTypePurposeTable = db.table('rbEventTypePurpose')
        table = eventTypeTable.leftJoin(financeTable, financeTable['id'].eq(eventTypeTable['finance_id']))
        table = table.leftJoin(aidKindTable, aidKindTable['id'].eq(eventTypeTable['medicalAidKind_id']))
        table = table.leftJoin(aidTypeTable, aidTypeTable['id'].eq(eventTypeTable['medicalAidType_id']))
        table = table.leftJoin(eventTypePurposeTable, eventTypePurposeTable['id'].eq(eventTypeTable['purpose_id']))
        counterTypeFieldName = 'counterType' if eventTypeTable.hasField('counterType') else 'generateExternalIdOnSave'
        cols = [
            'EventType.id as eventTypeId',
            'EventType.code as code',
            'EventType.name as name',
            'period',
            'singleInPeriod',
            'isLong',
            'dateInput',
            'form',
            'minDuration',
            'maxDuration',
            'finance_id',
            'scene_id',
            'visitServiceModifier',
            'visitServiceFilter',
            'visitFinance',
            'actionFinance',
            'actionContract',
            'rbFinance.code as financeCode',
            'showTime',
            'counter_id',
            'isExternal',
            'hasAssistant',
            'hasCurator',
            'hasVisitAssistant',
            'canHavePayableActions',
            'permitAnyActionDate',
            'rbMedicalAidKind.code as aidKindCode',
            'rbMedicalAidType.code as aidTypeCode',
            'showStatusActionsInPlanner',
            'showDiagnosticActionsInPlanner',
            'showCureActionsInPlanner',
            'showMiscActionsInPlanner',
            'purpose_id',
            'rbEventTypePurpose.code as purposeCode',
            'service_id',
            'context',
            'mesRequired',
            'defaultMesSpecification_id',
            'isTakenTissue',
            'mesCodeMask',
            'mesNameMask',
            'eventProfile_id',
            'isOrgStructurePriority',
            'prefix',
            'showLittleStranger',
            'uniqueExternalId',
            'inheritDiagnosis',
            'diagnosisSetDateVisible',
            'isResetSetDate',
            'defaultEndTime',
            'externalIdAsAccountNumber',
            'weekdays',
            'exposeConfirmation',
            'needMesPerformPercent',
            'showZNO',
            'goalFilter',
            'inheritResult',
            'inheritCheckupResult',
            'inheritGoal',
            'filterSpecialities',
            'filterPosts',
            '%s' % counterTypeFieldName
        ]
        if QtGui.qApp.region() == '23':
            cols.append('dispByMobileTeam')

        record = db.getRecordEx(table, cols, eventTypeTable['id'].eq(eventTypeId))
        if not record:
            record = QtSql.QSqlRecord()
        self.eventTypeId = forceRef(record.value('eventTypeId'))
        self.code = forceString(record.value('code'))
        self.name = forceString(record.value('name'))
        self.purposeId = forceRef(record.value('purpose_id'))
        self.purposeCode = forceString(record.value('purposeCode'))
        self.period = max(0, forceInt(record.value('period')))
        self.singleInPeriod = min(5, max(0, forceInt(record.value('singleInPeriod'))))
        self.periodEx = getEventPeriod(self.period, self.singleInPeriod)
        self.isLong = forceBool(record.value('isLong'))
        self.dateInput = forceInt(record.value('dateInput'))
        self.isUrgent = self.code == '22'
        self.isDeath  = self.purposeCode == '5'
        self.form = forceString(record.value('form'))
        self.financeId = forceRef(record.value('finance_id'))
        self.financeCode = forceInt(record.value('financeCode'))
        self.canHavePayableActions = forceBool(record.value('canHavePayableActions')) or self.financeCode == 4
        self.sceneId = forceRef(record.value('scene_id'))
        self.visitServiceModifier = forceString(record.value('visitServiceModifier'))
        self.visitServiceFilter = forceString(record.value('visitServiceFilter'))
        self.visitFinance = forceInt(record.value('visitFinance'))
        self.actionFinance = forceInt(record.value('actionFinance'))
        self.actionContract = forceInt(record.value('actionContract'))
        self.duration = (forceInt(record.value('minDuration')), forceInt(record.value('maxDuration')))
        self.showTime = forceBool(record.value('showTime'))
        self.counterId = forceRef(record.value('counter_id'))
        self.counterType = forceInt(record.value(counterTypeFieldName))
        self.counterTypeFieldName = counterTypeFieldName
        self.isExternal = forceInt(record.value('isExternal'))
        self.hasAssistant = forceBool(record.value('hasAssistant'))
        self.hasCurator = forceBool(record.value('hasCurator'))
        self.permitAnyActionDate = forceBool(record.value('permitAnyActionDate'))
        self.hasVisitAssistant = forceBool(record.value('hasVisitAssistant'))
        self.aidKindCode = forceString(record.value('aidKindCode'))
        self.aidTypeCode = forceString(record.value('aidTypeCode'))
        self.isStationary = self.aidTypeCode in ('1', '2', '3')
        self.isDayStationary = self.aidTypeCode in ('7')
        self.showStatusActionsInPlanner = forceBool(record.value('showStatusActionsInPlanner'))
        self.showDiagnosticActionsInPlanner = forceBool(record.value('showDiagnosticActionsInPlanner'))
        self.showCureActionsInPlanner = forceBool(record.value('showCureActionsInPlanner'))
        self.showMiscActionsInPlanner = forceBool(record.value('showMiscActionsInPlanner'))
        self.serviceId = forceRef(record.value('service_id'))
        self.context = forceString(record.value('context'))
        self.mesRequired = forceBool(record.value('mesRequired'))
        self.showAmountFromMes = bool(forceInt(record.value('mesRequired')) & 2)
        self.showMedicaments = bool(forceInt(record.value('mesRequired')) & 4)
        self.controlMesNecessityEqOne = bool(forceInt(record.value('mesRequired')) & 8)
        self.defaultMesSpecificationId = forceRef(record.value('defaultMesSpecification_id')) \
                                            if bool(forceInt(record.value('mesRequired')) & 16) \
                                            else None
        self.isTakenTissue = forceBool(record.value('isTakenTissue'))
        self.mesCodeMask = forceString(record.value('mesCodeMask'))
        self.mesNameMask = forceString(record.value('mesNameMask'))
        self.profileId   = forceRef(record.value('eventProfile_id'))
        self.isOrgStructurePriority = forceBool(record.value('isOrgStructurePriority'))
        self.prefix = forceString(record.value('prefix'))
        self.showLittleStranger = forceBool(record.value('showLittleStranger'))
        self.uniqueExternalId = forceBool(record.value('uniqueExternalId'))
        self.inheritDiagnosis = forceBool(record.value('inheritDiagnosis'))
        self.diagnosisSetDateVisible = forceInt(record.value('diagnosisSetDateVisible'))
        self.isResetSetDate = forceBool(record.value('isResetSetDate'))
        self.defaultEndTime = forceTime(record.value('defaultEndTime'))
        self.externalIdAsAccountNumber = forceBool(record.value('externalIdAsAccountNumber'))
        self.weekdays = forceInt(record.value('weekdays'))
        self.exposeConfirmation = forceInt(record.value('exposeConfirmation'))

        self.needMesPerformPercent = forceInt(record.value('needMesPerformPercent'))
        self.showZNO = forceBool(record.value('showZNO'))
        self.goalFilter = forceBool(record.value('goalFilter'))
        self.inheritResult = forceBool(record.value('inheritResult'))
        self.inheritCheckupResult = forceBool(record.value('inheritCheckupResult'))
        self.inheritGoal = forceBool(record.value('inheritGoal'))
        self.filterPosts = forceBool(record.value('filterPosts'))
        self.filterSpecialities = forceBool(record.value('filterSpecialities'))
        # i3757: Показывать чекбокс "Диспансеризация(проф.осмотр) проведена мобильной выездной бригадой"
        if QtGui.qApp.region() == '23':
            self.dispByMobileTeam = forceBool(record.value('dispByMobileTeam'))

    @classmethod
    def get(cls, eventTypeId, code = None):
        result = cls.cache.get(eventTypeId, None)
        if not result:
            cls.connect()
            result = CEventTypeDescription(eventTypeId)
            cls.cache[eventTypeId] = result
            cls.mapCodeToId[result.code] = eventTypeId
            if code is not None:
                cls.mapCodeToId[code] = eventTypeId
        return result

    @classmethod
    def getByCode(cls, eventTypeCode):
        eventTypeId = cls.mapCodeToId.get(eventTypeCode, False)
        if eventTypeId != False:
            return cls.get(eventTypeId, eventTypeCode)

        db = QtGui.qApp.db
        table = db.table('EventType')
        record = db.getRecordEx(table, [table['id']], [table['deleted'].eq(0), table['code'].eq(eventTypeCode)])
        eventTypeId = forceRef(record.value('id')) if record else None
        return cls.get(eventTypeId, eventTypeCode)

    @classmethod
    def purge(cls):
        cls.cache.clear()
        cls.mapCodeToId.clear()


def getEventType(eventTypeCode):
    return CEventTypeDescription.getByCode(eventTypeCode)


def getEventCode(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).code


def getEventName(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).name


def getEventPurposeId(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).purposeId


def getEventPurposeCode(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).purposeCode


def isEventDeath(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).isDeath


def isEventPeriodic(eventTypeId):
    description = CEventTypeDescription.get(eventTypeId)
    return description.period or description.singleInPeriod


def isEventLong(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).isLong


def getEventPeriodEx(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).periodEx


def getEventDateInput(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).dateInput


def isEventUrgent(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).isUrgent


def getEventTypeForm(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).form


def getEventFinanceCode(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).financeCode


def getEventFinanceId(eventTypeId):
    description = CEventTypeDescription.get(eventTypeId)
    return description.financeId


def getEventVisitServiceModifier(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).visitServiceModifier


def getEventVisitServiceFilter(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).visitServiceFilter


def getEventSceneId(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).sceneId


def getEventVisitFinance(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).visitFinance


def getEventActionFinance(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).actionFinance


def getEventActionContract(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).actionContract


def getEventDuration(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).duration


def getEventDurationRuleSamson(eventTypeId):
    # 0 : длительность определяется к-н
    # 1 : длительность определяется к-н+1
    return 0 if CEventTypeDescription.get(eventTypeId).isStationary else 1


def getEventDurationSamson(startDate, stopDate, weekProfile, eventTypeId):
    rule = getEventDurationRuleSamson(eventTypeId)
    result = countWorkDays(startDate, stopDate, weekProfile)
    if result == 1 and rule == 0 and forceDate(startDate) == forceDate(stopDate):
        return 1
    else:
        return max(1, result+rule-1)


def getEventShowTime(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).showTime


def getEventShowZNO(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).showZNO


def getEventGoalFilter(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).goalFilter


def getEventShowActionsInPlanner(eventTypeId):
    description = CEventTypeDescription.get(eventTypeId)
    return (description.showStatusActionsInPlanner,
            description.showDiagnosticActionsInPlanner,
            description.showCureActionsInPlanner,
            description.showMiscActionsInPlanner)


def getCounterType(eventTypeId):
    # 0 - счетчик не используется,
    # 1 - срабатывает при создании обращения,
    # 2 - срабатывает при сохранении обращения,
    # 3 - срабатывает при изменении результата обращения
    counterType = CEventTypeDescription.get(eventTypeId).counterType
    fieldName = CEventTypeDescription.get(eventTypeId).counterTypeFieldName
    if fieldName == 'counterType':
        return counterType
    else:
        return 2 if counterType == 1 else 1 if CEventTypeDescription.get(eventTypeId).counterId else 0


def getEventCounterId(eventTypeId):
    if getCounterType(eventTypeId) in (1, 2):
        return CEventTypeDescription.get(eventTypeId).counterId
    else:
        return None


def getEventPrefix(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).prefix


def getEventIsExternal(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).isExternal


def hasEventAssistant(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).hasAssistant


def hasEventCurator(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).hasCurator


def isEventAnyActionDatePermited(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).permitAnyActionDate


def hasEventVisitAssistant(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).hasVisitAssistant


def inheritDiagnosis(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).inheritDiagnosis


def getEventLengthRule(eventTypeId, isDayStationary, startDate, stopDate):
    # 0 : длительность определяется к-н
    # 1 : длительность определяется к-н+1
    if isDayStationary and isinstance(startDate, QtCore.QDateTime) and isinstance(stopDate, QtCore.QDateTime):
        return 1 if stopDate.time() > startDate.time() else 0
    else:
        return 0 if CEventTypeDescription.get(eventTypeId).isStationary else 1


def getEventWeekdays(eventTypeId):
    # Количество рабочих дней в неделе
    weekdays = CEventTypeDescription.get(eventTypeId).weekdays
    return weekdays if weekdays else 5


def getEventLengthDays(startDate, stopDate, countRedDays, eventTypeId, isDayStationary = False):
    rule = getEventLengthRule(eventTypeId, isDayStationary, startDate, stopDate)
    weekdays = getEventWeekdays(eventTypeId)
    periodLength = getPeriodLength(startDate, stopDate, countRedDays, weekdays)
    if periodLength == 1 and rule == 0 and forceDate(startDate) == forceDate(stopDate):
        return 1
    else:
        return max(1, periodLength+rule-1)


getActionLengthDays = getEventLengthDays


def getEventCanHavePayableActions(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).canHavePayableActions


def getEventAidKindCode(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).aidKindCode

def getEventAidTypeCode(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).aidTypeCode


def getEventServiceId(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).serviceId


def getEventContext(eventTypeId):
    eventDescr = CEventTypeDescription.get(eventTypeId)
    return eventDescr.context if eventDescr.context else 'f'+ eventDescr.form


def getEventMesRequired(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).mesRequired


def getDefaultMesSpecificationId(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).defaultMesSpecificationId


def getEventShowAmountFromMes(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).showAmountFromMes


def getEventShowMedicaments(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).showMedicaments


def getEventControlMesNecessityEqOne(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).controlMesNecessityEqOne


#Настройка, отвечающая за то, какой процент услуг должен быть обязательно выполнен для данного МЭС
def getNeedMesPerformPercent(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).needMesPerformPercent


def getEventIsTakenTissue(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).isTakenTissue


def getEventMesCodeMask(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).mesCodeMask


def getEventMesNameMask(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).mesNameMask


def getEventProfileId(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).profileId


def getEventLittleStranger(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).showLittleStranger


def getUniqueExternalIdRequired(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).uniqueExternalId


def getExternalIdAsAccountNumber(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).externalIdAsAccountNumber


def getDiagnosisSetDateVisible(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).diagnosisSetDateVisible


def isEventTypeResetSetDate(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).isResetSetDate


def isEventStationary(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).isStationary


def isEventDayStationary(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).isDayStationary


def getEventTypeDefaultEndTime(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).defaultEndTime


def getExposeConfirmation(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).exposeConfirmation


def getInheritResult(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).inheritResult


def getInheritCheckupResult(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).inheritCheckupResult


def getInheritGoal(eventTypeId):
    return CEventTypeDescription.get(eventTypeId).inheritGoal


def isDispByMobileTeam(eventTypeId):
    if hasattr(CEventTypeDescription.get(eventTypeId), 'dispByMobileTeam'):
        return CEventTypeDescription.get(eventTypeId).dispByMobileTeam
    else:
        return False


def getDeathDate(clientId):
    db = QtGui.qApp.db
    tableClientAttach = db.table('ClientAttach')
    tableRBAttachType = db.table('rbAttachType')
    table = tableClientAttach.leftJoin(tableRBAttachType, tableClientAttach['attachType_id'].eq(tableRBAttachType['id']))
    cond = [tableClientAttach['client_id'].eq(clientId), tableRBAttachType['code'].eq(8), tableClientAttach['deleted'].eq(0)]
    record = db.getRecordEx(table, 'begDate', cond)
    if record:
        return forceDate(record.value(0))
    else:
        return None


def isVisitDoctorBySetDate(setDate, execPerson_id, client_id):
    if QtGui.qApp.region() == '78' and QtGui.qApp.userHasRight(urNotAllowCreateManyEventsAtOneSetDate):
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        record = db.getRecordEx(
            tableEvent,
            '*',
            [
                tableEvent['setDate'].eq(setDate.toString('yyyy-MM-dd')),
                tableEvent['execPerson_id'].eq(execPerson_id),
                tableEvent['client_id'].eq(client_id),
                tableEvent['deleted'].eq(0)
            ]
        )
        if record:
            return forceInt(record.value('id'))
    return None


def getOutcomeDate(clientId):
    db = QtGui.qApp.db
    tableClientAttach = db.table('ClientAttach')
    tableRBAttachType = db.table('rbAttachType')
    table = tableClientAttach.innerJoin(tableRBAttachType, tableClientAttach['attachType_id'].eq(tableRBAttachType['id']))
    cond = [tableClientAttach['client_id'].eq(clientId), tableRBAttachType['outcome'].eq(1),
            tableClientAttach['deleted'].eq(0), tableClientAttach['endDate'].isNull()]
    record = db.getRecordEx(table, 'begDate', cond, 'begDate DESC')
    if record:
        return forceDate(record.value(0))
    else:
        return None


def checkEventPosibilityLetal(clientId, eventTypeId, eventDate):
    db = QtGui.qApp.db
    deathDate = getDeathDate(clientId)
    if deathDate and deathDate<eventDate:
        table = db.table('EventType')
        cond=[table['id'].eq(eventTypeId), table['purpose_id'].eq(6)]
        if not db.getRecordEx(table, '*', where=cond):
            return False
    return True


def checkEventPosibility(clientId, eventTypeId, personId, eventSetDate, eventDate):
    # Проверка возможности создания события
    if not checkEventPosibilityLetal(clientId, eventTypeId, eventDate):
        return False,  None
    description = CEventTypeDescription.get(eventTypeId)
    if description.period or description.singleInPeriod:
        posible, eventId = checkPeriodicEventPosibility(clientId, eventTypeId, eventDate if eventDate else eventSetDate, description.period, description.singleInPeriod)
    else:
        posible, eventId = checkNonPeriodicEventPosibility(clientId, eventTypeId, personId, eventSetDate, eventDate)
    return posible, eventId


def checkOMS(eventTypeId):
    db = QtGui.qApp.db
    tableEventType = db.table('EventType')
    tableFinance = db.table('rbFinance')
    table = tableEventType.leftJoin(tableFinance, tableEventType['finance_id'].eq(tableFinance['id']))
    cond = [tableEventType['deleted'].eq(0),
            tableFinance['code'].eq(2),
            tableEventType['id'].eq(eventTypeId)
            ]
    idList = db.getIdList(table, idCol=tableEventType['id'].name(),  where=cond, order=tableEventType['id'].name(), limit=1)
    if idList:
        return True
    return False


# TODO: 1) Проверить, нужна ли отдельная проверка для 30 формы. Если нет - объединить в 1 функцию
# TODO: 2) В утилитах импорта используется проверка для ф. 30 и переопределены две следующие функции. Необходимо изменить переопределенные функции согласно последним изменениям в данном файле?
def checkF030EventPosibility(clientId, eventTypeId, personId, eventSetDate, eventDate):
    # Проверка возможности создания события c формой 030
    hasRight = QtGui.qApp.userHasRight(urCreateSeveralEvents)
    hasRightOMS = QtGui.qApp.userHasRight(urCreateSeveralOMSEvents)
    if not hasRight and not hasRightOMS:
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        tablePerson = db.table('Person')
        tableEventType = db.table('EventType')
        tableFinance = db.table('rbFinance')
        tableP1 = tablePerson.alias('p1')
        tableP2 = tablePerson.alias('p2')
        table1 = tableEvent.leftJoin(tableP1, tableP1['id'].eq(tableEvent['execPerson_id']))
        table1 = table1.leftJoin(tableP2, tableP1['speciality_id'].eq(tableP2['speciality_id']))
        table2 = table1
        table1 = table1.leftJoin(tableEventType, tableEvent['eventType_id'].eq(tableEventType['id']))
        table1 = table1.leftJoin(tableFinance, tableEventType['finance_id'].eq(tableFinance['id']))
        cond2 = [tableEvent['deleted'].eq(0),
                tableEvent['client_id'].eq(clientId),
                tableEvent['eventType_id'].eq(eventTypeId),
                tableEvent['setDate'].dateEq(eventSetDate),
                tableP2['id'].eq(personId)
                ]
        cond1 = [tableEvent['deleted'].eq(0),
                tableEvent['client_id'].eq(clientId),
                tableFinance['code'].eq(2),
                tableEvent['setDate'].dateEq(eventSetDate),
                tableP2['id'].eq(personId),
                tableEventType['deleted'].eq(0)
                ]
        idList2 = db.getIdList(table2, idCol=tableEvent['id'].name(), where=cond2, order=tableEvent['id'].name(), limit=1)
        if idList2:
            return False, idList2[0]
        idList1 = db.getIdList(table1, idCol=tableEvent['id'].name(), where=cond1, order=tableEvent['id'].name(), limit=1)
        if idList1 and checkOMS(eventTypeId):
            return False, idList1[0]

    if not hasRight and hasRightOMS:
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        tablePerson = db.table('Person')
        tableP1 = tablePerson.alias('p1')
        tableP2 = tablePerson.alias('p2')
        table = tableEvent.leftJoin(tableP1, tableP1['id'].eq(tableEvent['execPerson_id']))
        table = table.leftJoin(tableP2, tableP1['speciality_id'].eq(tableP2['speciality_id']))
        cond = [tableEvent['deleted'].eq(0),
                tableEvent['client_id'].eq(clientId),
                tableEvent['eventType_id'].eq(eventTypeId),
                tableEvent['setDate'].dateEq(eventSetDate),
                tableP2['id'].eq(personId)
                ]
        idList = db.getIdList(table, idCol=tableEvent['id'].name(),  where=cond, order=tableEvent['id'].name(), limit=1)
        if idList and not checkOMS(eventTypeId):
            return False, idList[0]

    if hasRight and not hasRightOMS:
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        tablePerson = db.table('Person')
        tableEventType = db.table('EventType')
        tableFinance = db.table('rbFinance')
        tableP1 = tablePerson.alias('p1')
        tableP2 = tablePerson.alias('p2')
        table = tableEvent.leftJoin(tableP1, tableP1['id'].eq(tableEvent['execPerson_id']))
        table = table.leftJoin(tableP2, tableP1['speciality_id'].eq(tableP2['speciality_id']))
        table = table.leftJoin(tableEventType, tableEvent['eventType_id'].eq(tableEventType['id']))
        table = table.leftJoin(tableFinance, tableEventType['finance_id'].eq(tableFinance['id']))
        cond = [tableEvent['deleted'].eq(0),
                tableEvent['client_id'].eq(clientId),
                tableFinance['code'].eq(2),
                tableEvent['setDate'].dateEq(eventSetDate),
                tableP2['id'].eq(personId),
                tableEventType['deleted'].eq(0),
                tableEvent['eventType_id'].ne(eventTypeId)
                ]
        idList = db.getIdList(table, idCol=tableEventType['id'].name(), where=cond, order=tableEventType['id'].name(), limit=1)
        if idList and checkOMS(eventTypeId):
            return False, idList[0]

    return True, None


def checkNonPeriodicEventPosibility(clientId, eventTypeId, personId, eventSetDate, eventDate):
    # Проверка возможности создания непериодического события
    hasRight = QtGui.qApp.userHasRight(urCreateSeveralEvents)
    hasRightOMS = QtGui.qApp.userHasRight(urCreateSeveralOMSEvents)
    if not hasRight and not hasRightOMS:
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        tablePerson = db.table('Person')
        tableEventType = db.table('EventType')
        tableFinance = db.table('rbFinance')
        tableP1 = tablePerson.alias('p1')
        tableP2 = tablePerson.alias('p2')
        table1 = tableEvent.leftJoin(tableP1, tableP1['id'].eq(tableEvent['execPerson_id']))
        table1 = table1.leftJoin(tableP2, tableP1['speciality_id'].eq(tableP2['speciality_id']))
        table2 = table1
        table1 = table1.leftJoin(tableEventType, tableEvent['eventType_id'].eq(tableEventType['id']))
        table1 = table1.leftJoin(tableFinance, tableEventType['finance_id'].eq(tableFinance['id']))
        cond2 = [tableEvent['deleted'].eq(0),
                tableEvent['client_id'].eq(clientId),
                tableEvent['eventType_id'].eq(eventTypeId),
                tableEvent['setDate'].dateEq(eventSetDate),
                tableP2['id'].eq(personId)
                ]
        cond1 = [tableEvent['deleted'].eq(0),
                tableEvent['client_id'].eq(clientId),
                tableFinance['code'].eq(2),
                tableEvent['setDate'].dateEq(eventSetDate),
                tableP2['id'].eq(personId),
                tableEventType['deleted'].eq(0)
                ]
        idList2 = db.getIdList(table2, idCol=tableEvent['id'].name(), where=cond2, order=tableEvent['id'].name(), limit=1)
        if idList2:
            return False, idList2[0]
        idList1 = db.getIdList(table1, idCol=tableEvent['id'].name(), where=cond1, order=tableEvent['id'].name(), limit=1)
        if idList1 and checkOMS(eventTypeId):
            return False, idList1[0]

    if not hasRight and hasRightOMS:
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        tablePerson = db.table('Person')
        tableP1 = tablePerson.alias('p1')
        tableP2 = tablePerson.alias('p2')
        table = tableEvent.leftJoin(tableP1, tableP1['id'].eq(tableEvent['execPerson_id']))
        table = table.leftJoin(tableP2, tableP1['speciality_id'].eq(tableP2['speciality_id']))
        cond = [tableEvent['deleted'].eq(0),
                tableEvent['client_id'].eq(clientId),
                tableEvent['eventType_id'].eq(eventTypeId),
                tableEvent['setDate'].dateEq(eventSetDate),
                tableP2['id'].eq(personId)
                ]
        idList = db.getIdList(table, idCol=tableEvent['id'].name(), where=cond, order=tableEvent['id'].name(), limit=1)
        if idList and not checkOMS(eventTypeId):
            return False, idList[0]

    if hasRight and not hasRightOMS:
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        tablePerson = db.table('Person')
        tableEventType = db.table('EventType')
        tableFinance = db.table('rbFinance')
        tableP1 = tablePerson.alias('p1')
        tableP2 = tablePerson.alias('p2')
        table = tableEvent.leftJoin(tableP1, tableP1['id'].eq(tableEvent['execPerson_id']))
        table = table.leftJoin(tableP2, tableP1['speciality_id'].eq(tableP2['speciality_id']))
        table = table.leftJoin(tableEventType, tableEvent['eventType_id'].eq(tableEventType['id']))
        table = table.leftJoin(tableFinance, tableEventType['finance_id'].eq(tableFinance['id']))
        cond = [tableEvent['deleted'].eq(0),
                tableEvent['client_id'].eq(clientId),
                tableFinance['code'].eq(2),
                tableEvent['setDate'].dateEq(eventSetDate),
                tableP2['id'].eq(personId),
                tableEventType['deleted'].eq(0),
                tableEvent['eventType_id'].ne(eventTypeId)
                ]
        idList = db.getIdList(table, idCol=tableEvent['id'].name(), where=cond, order=tableEventType['id'].name(), limit=1)
        if idList and checkOMS(eventTypeId):
            return False, idList[0]

    return True, None


def checkPeriodicEventPosibility(clientId, eventTypeId, eventDate, period, singleInPeriod):
    # Проверка возможности создания периодического события
    db = QtGui.qApp.db
    table = db.table('Event')
    cond = [table['client_id'].eq(clientId), table['eventType_id'].eq(eventTypeId), table['deleted'].eq(0)]
    if period != 0:
        lowDate  = eventDate.addMonths(-period)
        highDate = eventDate.addMonths(+period)
        cond.append(table['setDate'].between(lowDate,  highDate))
    if singleInPeriod:
        if singleInPeriod == 1:
            lowDate  = firstWeekDay(eventDate)
            highDate = lastWeekDay(eventDate)
        elif singleInPeriod == 2:
            lowDate  = firstMonthDay(eventDate)
            highDate = lastMonthDay(eventDate)
        elif singleInPeriod == 3:
            lowDate  = firstQuarterDay(eventDate)
            highDate = lastQuarterDay(eventDate)
        elif singleInPeriod == 4:
            lowDate  = firstHalfYearDay(eventDate)
            highDate = lastHalfYearDay(eventDate)
        elif singleInPeriod == 5:
            lowDate  = firstYearDay(eventDate)
            highDate = lastYearDay(eventDate)
        else:
            lowDate  = eventDate
            highDate = eventDate
        cond.append(table['setDate'].between(lowDate,  highDate))
    idList = db.getIdList(table, where=cond, order='id')
    if idList:
        return False, idList[0]
    else:
        return True, None


def getEventPeriod(period, singleInPeriod):
    # вычисление периода события по интервалу и периоду однократности
    if singleInPeriod == 1:
        periodBySingle = 0.25 # неделя
    elif singleInPeriod == 2:
        periodBySingle = 1
    elif singleInPeriod == 3:
        periodBySingle = 3
    elif singleInPeriod == 4:
        periodBySingle = 6
    elif singleInPeriod == 5:
        periodBySingle = 12
    else:
        periodBySingle = 0
    return max(period, periodBySingle)


def countNextDate(setDate, eventPeriod, defaultDate=QtCore.QDate()):
    nextDate = defaultDate
    if eventPeriod == 0.25:
        nextDate = setDate.addDays(7)
    elif eventPeriod:
        nextDate = setDate.addMonths(eventPeriod)
    return nextDate


# FIXME: atronah: имя функции не отражает ее функционала.
def recordAcceptable(clientSex, clientAge, record):
    if clientSex:
        sex = forceInt(record.value('sex'))
        if sex and sex != clientSex:
            return False
    if clientAge:
        age = forceStringEx(record.value('age'))
        if age:
            result = False
            ageSelectors = parseAgeSelector(age, isExtend=True)
            for ageSelector in ageSelectors:
                begUnit, begCount, endUnit, endCount, step, useCalendarYear, useExclusion = ageSelector
                checkClientAge = clientAge
                if useCalendarYear and isinstance(checkClientAge, CAgeTuple):
                    birthDate = checkClientAge.birthDate
                    eventDate = checkClientAge.checkDate
                    checkClientAge = CAgeTuple((checkClientAge[0], checkClientAge[1], checkClientAge[2],
                                                eventDate.year() - birthDate.year()),
                                               birthDate,
                                               eventDate)
                result = checkAgeSelector((begUnit, begCount, endUnit, endCount), checkClientAge)
                if result:
                    if step:
                        unit = begUnit if begUnit else endUnit
                        if (checkClientAge[unit - 1] - begCount) % step != 0:
                            result = False
                    if result:
                        result = not useExclusion
                        break
            return result
    return True


def checkDiagnosis(parentWidget, MKB, diagFilter, clientId, clientSex, clientAge, begDate, endDate, eventTypeId=None, isEx=False):
    db = QtGui.qApp.db
    # 1) диагноз должен существовать
    if (QtGui.qApp.isAllowedExtendedMKB() and len(MKB) > 5) or QtGui.qApp.userHasRight(urDisableCheckMKBInput):
        return True
    tableMKB = db.table('MKB_Tree')
    record  = db.getRecordEx(tableMKB, 'DiagName, sex, age, MKBSubclass_id, Prim, begDate, endDate, OMS, MTR', tableMKB['DiagID'].eq((MKB)))
    if not record:
        message = u'Кода %s не существует' % (MKB)
        QtGui.QMessageBox.critical(parentWidget, u'Внимание!', message)
        return False

    skipCheck = (isEx and MKB[0] in 'VWXY' and QtGui.qApp.region() == '23')
    if QtGui.qApp.isCheckMKB() and not skipCheck:
        begDateMKB = forceDate(record.value('begDate'))
        endDateMKB = forceDate(record.value('endDate'))
        begDate = forceDate(begDate)

        # Если событие финансируется из ОМС (код 2), то и диагноз тоже должен финансироваться из ОМС
        if eventTypeId:
            finance_id = db.translate('EventType', 'id', eventTypeId, 'finance_id')
            finance_code = db.translate('rbFinance', 'id', finance_id, 'code')
            if forceString(finance_code) == '2' and not forceBool(record.value('OMS')):
                message = u'Выбранный диагноз (%s) не оплачивается из ОМС' % MKB
                QtGui.QMessageBox().critical(parentWidget, u'Внимание!', message)
                return False

        isClientRegional = None
        recordRegional = QtGui.qApp.db.getRecordEx('''ClientPolicy
                                                      INNER JOIN Organisation policyOKATO ON ClientPolicy.insurer_id = policyOKATO.id
                                                      LEFT JOIN kladr.KLADR kladr ON ClientPolicy.insuranceArea =  kladr.CODE
                                                      JOIN Organisation ON Organisation.id = %s''' % QtGui.qApp.currentOrgId(),
                                                      'if(Organisation.OKATO = policyOKATO.OKATO, 1, if(policyOKATO.OKATO = LEFT(kladr.OCATD, LENGTH(policyOKATO.OKATO)), 1, 0)) AS isClientRegional',
                                                      u'''ClientPolicy.id = (SELECT MAX(tmpCP.id)
                                                         FROM ClientPolicy tmpCP
                                                            LEFT JOIN rbPolicyType tmpPT ON tmpPT.id = tmpCP.policyType_id
                                                        WHERE tmpPT.name LIKE 'ОМС%%'
                                                            AND tmpCP.client_id = %(clientId)s
                                                            AND tmpCP.deleted = 0
                                                            AND tmpCP.begDate <= DATE('%(date)s')
                                                            AND (tmpCP.endDate IS NULL OR DATE('%(date)s') <= tmpCP.endDate)) AND (policyOKATO.OKATO OR ClientPolicy.insuranceArea)''' % {'clientId' : clientId, 'date': begDate.toString(QtCore.Qt.ISODate)})
        if recordRegional:
            isClientRegional = forceBool(recordRegional.value('isClientRegional'))
        if not forceBool(record.value('MTR')) and forceBool(record.value('OMS')) and not isClientRegional and isClientRegional is not None:
            message = u'Выбранный диагноз (%s) только для краевых.' % (MKB)
            QtGui.QMessageBox.critical(parentWidget, u'Внимание!', message)
            return False
        elif not forceBool(record.value('OMS')) and forceBool(record.value('MTR')) and isClientRegional and isClientRegional is not None:
            message = u'Выбранный диагноз (%s) только для инокраевых.' % (MKB)
            QtGui.QMessageBox.critical(parentWidget, u'Внимание!', message)
            return False
        elif not forceBool(record.value('MTR')) and not forceBool(record.value('OMS')):
            message = u'У выбранного диагноза (%s) не задана территория.' % (MKB)
            QtGui.QMessageBox.critical(parentWidget, u'Внимание!', message)
            return False
        if not(begDate >= begDateMKB and begDate <= endDateMKB):
            message = u'Выбранный диагноз (%s) не действителен на дату начала обращения.' % (MKB)
            QtGui.QMessageBox.critical(parentWidget, u'Внимание!', message)
            return False
        if endDate != QtCore.QDate():
            if not (endDate <= endDateMKB):
                message = u'Выбранный диагноз (%s) не действителен на дату окончания обращения.' % (MKB)
                QtGui.QMessageBox.critical(parentWidget, u'Внимание!', message)
                return False

    subclassMKB = MKB[5:]
    # 1.2) Если диагноз должен иметь уточнение, но не имеет его
    if QtGui.qApp.isSelectOnlyLeafOfMKBTree() and not subclassMKB and not skipCheck:
        subRecord = db.getRecordEx(tableMKB, 'DiagID', 'DiagID LIKE \'%s.%%\'' % MKBwithoutSubclassification(MKB), 'DiagID')
        if subRecord:
            message = u'Выбранный диагноз (%s) должен быть уточнён.' % (MKB)
            QtGui.QMessageBox.critical(parentWidget, u'Внимание!', message)
            return False
    # 1.1) и субклассификация - тоже
    if subclassMKB:
        subclassId = forceInt(record.value('MKBSubclass_id'))
        tableSubclass = db.table('rbMKBSubclass_Item')
        record  = db.getRecordEx(tableSubclass, 'id', [tableSubclass['master_id'].eq(subclassId), tableSubclass['code'].eq(subclassMKB)])
        if not record:
            message = u'В коде %s указана недопустимая субклассификация' % (MKB)
            QtGui.QMessageBox.critical(parentWidget, u'Внимание!', message)
            return False
    # 2) диагноз должен быть применим по полу и возрасту
    elif not recordAcceptable(clientSex, clientAge, record) and not skipCheck:
        message = u'Код %s (%s)\n в данном случае не применим' % (MKB, forceString(record.value('DiagName')))
        QtGui.QMessageBox.critical(parentWidget, u'Внимание!', message)
        return False
    # 3) диагноз должен быть применим по специалисту
    if diagFilter and diagFilter.find(MKB[:1])>=0 :
        message = u'Код %s (%s)\nпо правилам контроля не должен применяться данным специалистом\nВвод верен?' % (MKB, forceString(record.value('DiagName')))
        if QtGui.QMessageBox.Yes != QtGui.QMessageBox.question(parentWidget, u'Внимание!', message, QtGui.QMessageBox.Yes|QtGui.QMessageBox.No, QtGui.QMessageBox.Yes):
            return False
    # 4) коды с примечанием не должны вводиться.
    if forceString(record.value('Prim')) == '*' and not skipCheck:
        message = u'Вы ввели код %s (%s) со *.\nХотите заменить его на другой?' % (MKB,  forceString(record.value('DiagName')))
        if QtGui.QMessageBox.No != QtGui.QMessageBox.question(parentWidget, u'Внимание!', message, QtGui.QMessageBox.Yes|QtGui.QMessageBox.No, QtGui.QMessageBox.Yes):
            return False
    return True


def specifyDiagnosis(parentWidget, MKB, diagFilter, clientId, clientSex, clientAge, date, endDate=QtCore.QDate(), eventTypeId=None):
    specifiedMKB = MKB
    specifiedMKBEx = ''
    specifiedCharacterId = None
    specifiedTraumaTypeId = None
    modifiableDiagnosisId = None
    acceptable = checkDiagnosis(parentWidget, MKB, diagFilter, clientId, clientSex, clientAge, date, endDate, eventTypeId)
    ignoreList = ['Z']
    if QtGui.qApp.userHasRight(urDisableCheckNewMKBWithOld):
        ignoreList.append('K')

    if acceptable and MKB[:1] not in ignoreList:
        # 4) диагноз должен быть подтверждён, если есть похожий
        db = QtGui.qApp.db
        table = db.table('Diagnosis')
        tableCharacter = db.table('rbDiseaseCharacter')
        tableMKB = db.table('MKB_Tree')
        queryTable = table.join(tableCharacter, tableCharacter['id'].eq(table['character_id']))
        queryTable = queryTable.join(tableMKB, 'MKB_Tree.DiagID=LEFT(Diagnosis.MKB,5)')
        cols = 'Diagnosis.id, Diagnosis.MKB, Diagnosis.MKBEx, Diagnosis.character_id, Diagnosis.traumaType_id'
        cond = db.joinAnd([table['client_id'].eq(clientId), table['deleted'].eq(0), table['mod_id'].isNull(),
                           db.joinOr([tableCharacter['code'].ne('1'),
                                      'ADDDATE(Diagnosis.endDate, IF(MKB_Tree.duration,MKB_Tree.duration,%d))>=%s'%(QtGui.qApp.averageDuration(), db.formatDate(date))
                                     ])
                          ])
        record = db.getRecordEx(queryTable, cols, [cond, table['MKB'].eq(MKB)]) # точно такой
        if not record:
            record = db.getRecordEx(queryTable, cols, [cond, table['MKB'].like(MKB+'%')]) # такой, но с субклассификацией
        if not record:
            record = db.getRecordEx(queryTable, cols, [cond, table['MKB'].like(MKBwithoutSubclassification(MKB)+'%')]) # такой, без субклассификацией (другой субклассификацией)
        if not record:
            record = db.getRecordEx(queryTable, cols, [cond, table['MKB'].like(MKB[:3]+'%')]) # такой, без классификации (другой классификацией)
        if not record:# другой в этом-же блоке
            tableMKB = db.table('MKB_Tree')
            tableMKB1 = db.table('MKB_Tree').alias('MKB1')
            condMKBInBlock = db.existsStmt(tableMKB.leftJoin(tableMKB1, 'getMKBBlockID(%s) = getMKBBlockID(%s)' % (tableMKB['DiagID'], tableMKB1['DiagID'])),
                                           [tableMKB1['DiagID'].eq(MKB[:3]),
                                           'LEFT('+table['MKB'].name()+', 3)='+tableMKB['DiagID'].name()])
            record = db.getRecordEx(queryTable, cols, [cond, condMKBInBlock]) # другой в этом-же блоке
        if record:
            suggestedMKB = forceString(record.value('MKB'))
            suggestedMKBEx = forceString(record.value('MKBEx'))
            suggestedCharacterId = forceRef(record.value('character_id'))
            suggestedTraumaTypeId = forceRef(record.value('traumaType_id'))
            if suggestedMKB != MKB :
                from DiagnosisConfirmationDialog import CDiagnosisConfirmationDialog
                dlg = CDiagnosisConfirmationDialog(parentWidget, suggestedMKB, MKB)
                choise = dlg.exec_()
                if choise == dlg.acceptNew:
                    pass
                elif choise == dlg.accentNewAndModifyOld:
                    modifiableDiagnosisId = forceRef(record.value('id'))
                else: # acceptOld or Esc
                    specifiedMKB = suggestedMKB
                    specifiedMKBEx = suggestedMKBEx
                    specifiedCharacterId = suggestedCharacterId
                    specifiedTraumaTypeId = suggestedTraumaTypeId
            else:
                specifiedMKB = suggestedMKB
                specifiedMKBEx = suggestedMKBEx
                specifiedCharacterId = suggestedCharacterId
                specifiedTraumaTypeId = suggestedTraumaTypeId
    return (acceptable, specifiedMKB, specifiedMKBEx, specifiedCharacterId, specifiedTraumaTypeId, modifiableDiagnosisId)


def getDiagnosisPrimacy(clientId, date, MKB, characterId):
    db = QtGui.qApp.db
    table = db.table('Diagnosis')
    cond  = [table['client_id'].eq(clientId), table['MKB'].eq(MKB), table['endDate'].le(date)]
    characterCode = forceString(db.translate('rbDiseaseCharacter', 'id', characterId, 'code'))
    if characterCode == '1':
        duration = forceInt(db.translate('MKB_Tree', 'DiagID', MKBwithoutSubclassification(MKB), 'duration'))
        if not duration:
            duration = QtGui.qApp.averageDuration()
        cond.append(table['endDate'].ge(date.addDays(-duration)))
    else:
        cond.append(table['endDate'].ge(firstYearDay(date)))
    record = db.getRecordEx(table, 'id', cond)
    return not record


#######################################################################
#
# второй подход к ведению ЛУД
#
#######################################################################

# считаем количество Diagnostic, Diagnosis, TempInvalid и TempInvalid_Period ссылающихся на данный diagnosis
def countUsageDiagnosis(diagnosisId, excludeDiagnosticId, countTempInvalid):
    result = 0
    if diagnosisId:
        db = QtGui.qApp.db
        table = db.table('Diagnostic')
        cond = [table['diagnosis_id'].eq(diagnosisId)]
        if excludeDiagnosticId:
            cond.append(table['id'].ne(excludeDiagnosticId))
        record = db.getRecordEx(table, 'COUNT(id)', cond)
        if record:
            result += forceInt(record.value(0))

        table = db.table('Diagnosis')
        cond = [table['mod_id'].eq(diagnosisId)]
        record = db.getRecordEx(table, 'COUNT(id)', cond)
        if record:
            result += forceInt(record.value(0))

        if countTempInvalid:
            for tableName in ['TempInvalid', 'TempInvalid_Period']:
                table = db.table(tableName)
                cond = [table['diagnosis_id'].eq(diagnosisId)]
                record = db.getRecordEx(table, 'COUNT(id)', cond)
                if record:
                    result += forceInt(record.value(0))
    return result


def createDiagnosisRecord(clientId, diagnosisTypeCode, characterCode, MKB, MKBEx, dispanserId, traumaTypeId, setDate, endDate, personId, morphologyMKB, TNMS):
    # создаём новую запись Diagnosis
    db = QtGui.qApp.db
    diagnosisTypeId = db.translate('rbDiagnosisType', 'code', diagnosisTypeCode, 'id')
    characterId = db.translate('rbDiseaseCharacter', 'code', characterCode, 'id')

    table = db.table('Diagnosis')
    record = table.newRecord()
    record.setValue('client_id',        toVariant(clientId))
    record.setValue('diagnosisType_id', toVariant(diagnosisTypeId))
    record.setValue('character_id',     toVariant(characterId))
    record.setValue('MKB',              toVariant(MKB))
    record.setValue('MKBEx',            toVariant(MKBEx))
    if QtGui.qApp.isTNMSVisible():
        record.setValue('TNMS',         toVariant(TNMS))
    if QtGui.qApp.defaultMorphologyMKBIsVisible():
        record.setValue('morphologyMKB',    toVariant(morphologyMKB))
    record.setValue('dispanser_id',     toVariant(dispanserId))
    record.setValue('traumaType_id',    toVariant(traumaTypeId))
    record.setValue('setDate',          toVariant(setDate))
    record.setValue('endDate',          toVariant(endDate))
    record.setValue('person_id',        toVariant(personId))
    return db.insertRecord(table, record)


def modifyDiagnosisRecord(record, diagnosisTypeCode, characterCode, MKB, MKBEx, dispanserId, traumaTypeId, setDate, endDate, personId, morphologyMKB, TNMS):
    # меняем существующую запись Diagnosis, из предположения что она использована только в одном
    # месте и при этом исправляется ошибочный ввод.
    db = QtGui.qApp.db
    diagnosisTypeId = db.translate('rbDiagnosisType', 'code', diagnosisTypeCode, 'id')
    characterId = db.translate('rbDiseaseCharacter', 'code', characterCode, 'id')
    table = db.table('Diagnosis')
    record.setValue('diagnosisType_id', toVariant(diagnosisTypeId))
    record.setValue('character_id',     toVariant(characterId))
    record.setValue('MKB',              toVariant(MKB))
    record.setValue('MKBEx',            toVariant(MKBEx))
    if QtGui.qApp.isTNMSVisible():
        record.setValue('TNMS',         toVariant(TNMS))
    if QtGui.qApp.defaultMorphologyMKBIsVisible():
        record.setValue('morphologyMKB',    toVariant(morphologyMKB))
    record.setValue('dispanser_id',     toVariant(dispanserId))
    record.setValue('traumaType_id',    toVariant(traumaTypeId))
    if not QtGui.qApp.isPNDDiagnosisMode():
        record.setValue('setDate',          toVariant(setDate))
        record.setValue('endDate',          toVariant(endDate))
    record.setValue('person_id',        toVariant(personId))
    return db.updateRecord(table, record)


def updateDiagnosisRecord(record, setDate, endDate, MKBEx, dispanserId, traumaTypeId, personId, morphologyMKB, TNMS):
    # меняем существующую запись Diagnosis, из предположения что она использована во многих
    # местах и при этом "расширяется"
    oldSetDate = forceDate(record.value('setDate'))
    oldEndDate = forceDate(record.value('endDate'))
    if oldEndDate<=endDate and not QtGui.qApp.isPNDDiagnosisMode():
        record.setValue('endDate', toVariant(endDate))
        record.setValue('MKBEx', toVariant(MKBEx))
        if QtGui.qApp.isTNMSVisible():
            record.setValue('TNMS', toVariant(TNMS))
        if QtGui.qApp.defaultMorphologyMKBIsVisible():
            record.setValue('morphologyMKB', toVariant(morphologyMKB))
        if dispanserId:
            record.setValue('dispanser_id', toVariant(dispanserId))
        if traumaTypeId:
            record.setValue('traumaType_id',toVariant(traumaTypeId))
        if personId:
            record.setValue('person_id',toVariant(personId))

    if not setDate.isNull():
        if oldSetDate.isNull():
#            if setDate<oldEndDate:
#                record.setValue('setDate', QVariant(setDate))
            pass
        else:
            if setDate<oldSetDate:
                record.setValue('setDate', toVariant(setDate))
    QtGui.qApp.db.updateRecord('Diagnosis', record)


def findDiagnosisRecord(db, table, permanentCond, date, delta):
    delta = forceInt(delta)
    # ищем в периоде
    record = db.getRecordEx(table, '*', [permanentCond,
                                         db.joinOr([table['setDate'].isNull(), table['setDate'].le(date.addDays(delta))]),
                                         table['endDate'].ge(date.addDays(-delta))], 'endDate DESC')
    if not record:
        # ищем после периода
        record = db.getRecordEx(table, '*', [permanentCond, table['endDate'].le(date)], 'endDate DESC')
    if not record:
        # ищем до периода
        record = db.getRecordEx(table, '*', [permanentCond], 'endDate DESC')
    return record


def findLastDiagnosisRecord(clientId):
    tableDiag = QtGui.qApp.db.table('Diagnosis')
    tableType = QtGui.qApp.db.table('rbDiagnosisType')
    table = tableDiag.innerJoin(tableType, [tableType['id'].eq(tableDiag['diagnosisType_id']), tableType['code'].inlist(['2', '1'])])
    return QtGui.qApp.db.getRecordEx(table, 'Diagnosis.*', [tableDiag['client_id'].eq(clientId), tableDiag['deleted'].eq(0)], 'setDate DESC')


def getDiagnosisId2(
            date,
            personId,
            clientId,
            diagnosisTypeId,
            MKB,
            MKBEx,
            characterId,
            dispanserId,
            traumaTypeId,
            suggestedDiagnosisId=None,
            ownerId=None,
            isDiagnosisManualSwitch = None,
            handleDiagnosis=None,
            TNMS=None,
            morphologyMKB=None,
            newSetDate=None
            ):
    db = QtGui.qApp.db
    if MKB[:1] == 'Z':
        diagnosisTypeCode = '98' # magic!!!
    else:
        diagnosisTypeCode = forceString(db.translate('rbDiagnosisType', 'id', diagnosisTypeId, 'replaceInDiagnosis'))
    characterCode = forceString(db.translate('rbDiseaseCharacter', 'id', characterId, 'replaceInDiagnosis'))
    table = db.table('Diagnosis')
    result = None

    if diagnosisTypeCode == '98':
        result = createDiagnosisRecord(clientId, diagnosisTypeCode, characterCode, MKB, MKBEx, dispanserId, traumaTypeId, date, date, personId, morphologyMKB, TNMS)
    else:
        assert diagnosisTypeCode in ['2', '9'], 'diagnosisTypeCode is "%s", expected "2" or "9"' % diagnosisTypeCode

        clientCond = table['client_id'].eq(clientId)
        diagCond = table['MKB'].eq(MKB)
        commonCond = db.joinAnd([table['deleted'].eq(0), table['mod_id'].isNull(), clientCond, diagCond])
        setDate = date

        if characterCode == '3' : # хроническое
            record = findDiagnosisRecord(db, table, commonCond, date, 0)
            docCharacterCode = forceString(db.translate('rbDiseaseCharacter', 'id', characterId, 'code'))
            if docCharacterCode in ['3', '4']: # "хроническое" или "обострение хронического"
                setDate = QtCore.QDate()
            if record:
                oldCharacterId = forceRef(record.value('character_id'))
                oldCharacterCode = forceString(db.translate('rbDiseaseCharacter', 'id', oldCharacterId, 'code'))
                oldSetDate = forceDate(record.value('setDate'))
                oldEndDate = forceDate(record.value('endDate'))
#                countUsage = countUsageDiagnosis(suggestedDiagnosisId, ownerId, False)
                countUsage = countUsageDiagnosis(forceRef(record.value('id')), ownerId, False)
                if countUsage:
                    if oldCharacterCode == '3':
                        # и раньше было хроническим, обновляем документ
                        if (oldSetDate.isNull() or oldSetDate<date) and docCharacterCode == '2':
                            # при наличии уже установленного хрон. и выставлении впервые установленного
                            characterId = oldCharacterId # меняем в документе на хроническое
                    else:
                        # раньше было острым
                        if oldEndDate.year()>=date.year():
                            # меняем на хроническое
                            characterId = db.translate('rbDiseaseCharacter', 'code', characterCode, 'id')
                            record.setValue('character_id', toVariant(characterId))
                            characterId = db.translate('rbDiseaseCharacter', 'code', '4', 'id') # меняем в документе на обострение
                        else:
                            # прошлогодние данные не меняем.
                            result = createDiagnosisRecord(clientId, diagnosisTypeCode, characterCode, MKB, MKBEx, dispanserId, traumaTypeId, setDate, date, personId, morphologyMKB, TNMS)
                else:
                    result = modifyDiagnosisRecord(record, diagnosisTypeCode, characterCode, MKB, MKBEx, dispanserId, traumaTypeId, setDate, date, personId, morphologyMKB, TNMS)
            else:
                result = createDiagnosisRecord(clientId, diagnosisTypeCode, characterCode, MKB, MKBEx, dispanserId, traumaTypeId, setDate, date, personId, morphologyMKB, TNMS)
        else: # это острое заболевание
            if isDiagnosisManualSwitch:
                return getDiagnosisIdByManualSwitch(
                       handleDiagnosis,
                       date,
                       personId,
                       clientId,
                       diagnosisTypeId,
                       MKB,
                       MKBEx,
                       characterId,
                       dispanserId,
                       traumaTypeId,
                       suggestedDiagnosisId,
                       ownerId,
                       morphologyMKB,
                       TNMS)
            duration = forceInt(db.translate('MKB_Tree', 'DiagID', MKBwithoutSubclassification(MKB), 'duration'))
            if not duration:
                duration = QtGui.qApp.averageDuration()
            record = findDiagnosisRecord(db, table, commonCond, date, duration)
            if record:
                oldCharacterId = forceRef(record.value('character_id'))
                oldCharacterCode = forceString(db.translate('rbDiseaseCharacter', 'id', oldCharacterId, 'code'))
#                countUsage = countUsageDiagnosis(suggestedDiagnosisId, ownerId, False)
                countUsage = countUsageDiagnosis(forceRef(record.value('id')), ownerId, False)
                if countUsage:
                    if oldCharacterCode == '3':
                        # раньше было хроническим, обновляем в документе на обострение
                        characterId = db.translate('rbDiseaseCharacter', 'code', '4', 'id') # меняем в документе на обострение
                        updateDiagnosisRecord(record, date, date, MKBEx, dispanserId, traumaTypeId, personId, morphologyMKB, TNMS)
                    else:
                        oldSetDate = forceDate(record.value('setDate'))
                        oldEndDate = forceDate(record.value('endDate'))
                        if oldSetDate.addDays(-duration)>date or date>oldEndDate.addDays(duration):
                            result = createDiagnosisRecord(clientId, diagnosisTypeCode, characterCode, MKB, MKBEx, dispanserId, traumaTypeId, date, date, personId, morphologyMKB, TNMS)
                else:
                    result = modifyDiagnosisRecord(record, diagnosisTypeCode, characterCode, MKB, MKBEx, dispanserId, traumaTypeId, setDate, date, personId, morphologyMKB, TNMS)
            else:
                result = createDiagnosisRecord(clientId, diagnosisTypeCode, characterCode, MKB, MKBEx, dispanserId, traumaTypeId, newSetDate if newSetDate else date, date, personId, morphologyMKB, TNMS)
        if result is None:
            if diagnosisTypeCode == '2':
                diagnosisTypeId = db.translate('rbDiagnosisType', 'code', diagnosisTypeCode, 'id')
                record.setValue('diagnosisType_id', diagnosisTypeId)
            updateDiagnosisRecord(record, setDate, date, MKBEx, dispanserId, traumaTypeId, personId, morphologyMKB, TNMS)
            result = forceRef(record.value('id'))
    if suggestedDiagnosisId and suggestedDiagnosisId != result:
        if countUsageDiagnosis(suggestedDiagnosisId, ownerId, True) == 0:
            db.deleteRecord(table, table['id'].eq(suggestedDiagnosisId))
    return result, characterId


def getDiagnosisIdByManualSwitch(
            handleDiagnosis,
            date,
            personId,
            clientId,
            diagnosisTypeId,
            MKB,
            MKBEx,
            characterId,
            dispanserId,
            traumaTypeId,
            suggestedDiagnosisId=None,
            ownerId=None,
            TNMS=None,
            morphologyMKB=None
            ):
    db = QtGui.qApp.db
    if MKB[:1] == 'Z':
        diagnosisTypeCode = '98' # magic from getDiagnosisId2 :-)
    else:
        diagnosisTypeCode = forceString(db.translate('rbDiagnosisType', 'id', diagnosisTypeId, 'replaceInDiagnosis'))
    characterCode = forceString(db.translate('rbDiseaseCharacter', 'id', characterId, 'replaceInDiagnosis'))
    tableDiagnosis = db.table('Diagnosis')
    result = None
    clientCond = tableDiagnosis['client_id'].eq(clientId)
    diagCond = tableDiagnosis['MKB'].eq(MKB)
    commonCond = db.joinAnd([tableDiagnosis['deleted'].eq(0),
                             tableDiagnosis['mod_id'].isNull(), clientCond, diagCond])
    if handleDiagnosis:
        if not bool(ownerId):
            result = createDiagnosisRecord(clientId, diagnosisTypeCode, characterCode, MKB, MKBEx, dispanserId, traumaTypeId, date, date, personId, morphologyMKB, TNMS)
        else:
            wasCheckedHandleDiagnosis = checkIsHandleDiagnosisIsChecked(date,
                                                                        clientId,
                                                                        suggestedDiagnosisId)
            if wasCheckedHandleDiagnosis:
                diagnosisId = forceRef(db.translate('Diagnostic', 'id', ownerId, 'diagnosis_id'))
                checkRecord = db.getRecord(tableDiagnosis, '*', diagnosisId)
                if bool(checkRecord):
                    modifySetDate = forceDate(checkRecord.value('setDate'))
                    modifyEndDate = forceDate(checkRecord.value('endDate'))
                    result = modifyDiagnosisRecord(checkRecord, diagnosisTypeCode, characterCode, MKB, MKBEx, dispanserId, traumaTypeId, modifySetDate, modifyEndDate, personId, morphologyMKB, TNMS)
                else:
                    result = createDiagnosisRecord(clientId, diagnosisTypeCode, characterCode, MKB, MKBEx, dispanserId, traumaTypeId, date, date, personId, morphologyMKB, TNMS)
            else:
                result = createDiagnosisRecord(clientId, diagnosisTypeCode, characterCode, MKB, MKBEx, dispanserId, traumaTypeId, date, date, personId, morphologyMKB, TNMS)
    else:
        duration = forceInt(db.translate('MKB_Tree', 'DiagID', MKBwithoutSubclassification(MKB), 'duration'))
        if not duration:
            duration = QtGui.qApp.averageDuration()
        record = findDiagnosisRecord(db, tableDiagnosis, commonCond, date, duration)
        if record:
            oldCharacterId = forceRef(record.value('character_id'))
            oldCharacterCode = forceString(db.translate('rbDiseaseCharacter', 'id', oldCharacterId, 'code'))
            countUsage = countUsageDiagnosis(forceRef(record.value('id')), ownerId, False)
            if countUsage:
                if oldCharacterCode == '3':
                    characterId = db.translate('rbDiseaseCharacter', 'code', '4', 'id')
                oldSetDate = forceDate(record.value('setDate'))
                oldEndDate = forceDate(record.value('endDate'))
                if oldSetDate.addDays(-duration*2)>date or date>oldEndDate.addDays(duration*2):
                    if CAskedValueForDiagnosisManualSwitch.ask():
                        updateDiagnosisRecord(record, date, date, MKBEx, dispanserId, traumaTypeId, personId, morphologyMKB, TNMS)
                        result = forceRef(record.value('id'))
                    else:
                        result = createDiagnosisRecord(clientId, diagnosisTypeCode, characterCode, MKB, MKBEx, dispanserId, traumaTypeId, date, date, personId, morphologyMKB, TNMS)
                else:
                    updateDiagnosisRecord(record, date, date, MKBEx, dispanserId, traumaTypeId, personId, morphologyMKB, TNMS)
                    result = forceRef(record.value('id'))
            else:
                result = createDiagnosisRecord(clientId, diagnosisTypeCode, characterCode, MKB, MKBEx, dispanserId, traumaTypeId, date, date, personId, morphologyMKB, TNMS)
        else:
            result = createDiagnosisRecord(clientId, diagnosisTypeCode, characterCode, MKB, MKBEx, dispanserId, traumaTypeId, date, date, personId, morphologyMKB, TNMS)
    if suggestedDiagnosisId and suggestedDiagnosisId != result:
        if countUsageDiagnosis(suggestedDiagnosisId, ownerId, True) == 0:
            db.deleteRecord(tableDiagnosis, tableDiagnosis['id'].eq(suggestedDiagnosisId))
    return result, characterId


def checkIsHandleDiagnosisIsChecked(setDate, clientId, diagnosisId):
    if bool(diagnosisId):
        db = QtGui.qApp.db
        tableDiagnosis = db.table('Diagnosis')
        cond = [tableDiagnosis['setDate'].dateEq(setDate),
                tableDiagnosis['client_id'].eq(clientId),
                tableDiagnosis['id'].eq(diagnosisId)]
        recordCheck = db.getRecordEx(tableDiagnosis, 'id', cond)
        return int(bool(recordCheck)) #atronah: Fuck my brain!!!
    return 0


def setAskedClassValueForDiagnosisManualSwitch(val):
    CAskedValueForDiagnosisManualSwitch.setValue(val)


class CAskedValueForDiagnosisManualSwitch(object):
    # не забыть после всего установить
    # `value` в значение None

    u"""0 - `да` только для текущего
        1 - `нет` только для текущего
        2 - `да` для всех
        3 - `нет` для всех"""

    value = None
    messageBox = None
    buttons = []

    @classmethod
    def setValue(cls, value):
        cls.value = value

    @classmethod
    def ask(cls):
        val = cls.value
        if val in [None, 0, 1]:# еще не было вопроса, либо ответ не распространялся на все
            messageBox = cls.getMessageBox()
            messageBox.exec_()
            button = messageBox.clickedButton()
            if button in cls.buttons:
                cls.setValue(cls.buttons.index(button))
                return cls.getResult()
        else:
            return cls.getResult()

    @classmethod
    def getResult(cls):
        if cls.value in [0, 2]:
            return True
        elif cls.value in [1, 3]:
            return False
        return False

    @classmethod
    def getMessageBox(cls):
        if not cls.messageBox:
            buttonYes = QtGui.QPushButton(u'да')
            buttonNo = QtGui.QPushButton(u'нет')
            buttonYesForAll = QtGui.QPushButton(u'да для всех')
            buttonNoForAll = QtGui.QPushButton(u'нет для всех')
            cls.buttons = [buttonYes, buttonNo, buttonYesForAll, buttonNoForAll]
            messageBox = QtGui.QMessageBox()
            messageBox.setWindowTitle(u'Внимание!')
            messageBox.setText(u'Слишком большой временной промежуток между датами \nв однотипных заболеваниях\n\nСчитать одним заболеванием?')
            messageBox.addButton(buttonYes,       QtGui.QMessageBox.ActionRole)
            messageBox.addButton(buttonNo,        QtGui.QMessageBox.ActionRole)
            messageBox.addButton(buttonYesForAll, QtGui.QMessageBox.ActionRole)
            messageBox.addButton(buttonNoForAll,  QtGui.QMessageBox.ActionRole)
            cls.messageBox = messageBox
        return cls.messageBox


def getEventDiagnosis(eventId):
    stmt = 'SELECT MKB from Diagnosis WHERE id=getEventDiagnosis(%d) LIMIT 1' % eventId
    query = QtGui.qApp.db.query(stmt)
    if query.first():
        return forceString(query.record().value(0))
    else:
        return None


MapMKBCharactersToCharacterID = None
MapMKBCharactersToCharacterIDForDiagnosis = None


# mdldml: очень сомнительная функция
def getEventBedProfilesList(eventId):
    db = QtGui.qApp.db
    stmt = u'''
    SELECT
        rbHPB.code
    FROM
        Action A
        INNER JOIN ActionType AT ON A.actionType_id = AT.id
        INNER JOIN ActionProperty AP ON AP.action_id = A.id
        INNER JOIN ActionPropertyType APT ON AP.type_id = APT.id
        INNER JOIN ActionProperty_HospitalBed APHB ON AP.id = APHB.id
        INNER JOIN OrgStructure_HospitalBed OSHB ON APHB.value = OSHB.id
        INNER JOIN rbHospitalBedProfile rbHPB ON OSHB.profile_id = rbHPB.id
    WHERE
        A.event_id = %i
        AND AT.flatCode LIKE 'moving%%'
        AND APT.name = 'койка'
    ORDER BY
        A.idx''' % eventId
    query = db.query(stmt)
    result = []
    while query.next():
        result.append(forceString(query.record().value('code')))
    return result


def getMapMKBCharactersToCharacterID():
    u"""
        получить список id записей характеров в соответствии с
        характером указанным в МКБ
    """
    global MapMKBCharactersToCharacterID
    from RefBooks.MKB import MapMKBCharactersToCharacterCode

    if not MapMKBCharactersToCharacterID:
        db = QtGui.qApp.db
        mapCodeToId = {}
        for record in db.getRecordList('rbDiseaseCharacter', 'id, code'):
            id   = forceRef(record.value(0))
            code = forceString(record.value(1))
            mapCodeToId[code] = id
        result = []
        for (title,  codes) in MapMKBCharactersToCharacterCode:
            idList = []
            for code in codes:
                if code in mapCodeToId:
                    idList.append(mapCodeToId[code])
            result.append(idList)
        MapMKBCharactersToCharacterID = result
    return MapMKBCharactersToCharacterID


def getMapMKBCharactersToCharacterIDForDiagnosis():
    u"""
        получить список id записей характеров в соответствии с
        характером указанным в МКБ с учетом поля replaceInDiagnosis
    """
    global MapMKBCharactersToCharacterIDForDiagnosis
    from RefBooks.MKB import MapMKBCharactersToCharacterCodeForDiagnosis

    if not MapMKBCharactersToCharacterIDForDiagnosis:
        db = QtGui.qApp.db
        mapCodeToId = {}
        for record in db.getRecordList('rbDiseaseCharacter', 'id, code'):
            id   = forceRef(record.value(0))
            code = forceString(record.value(1))
            mapCodeToId[code] = id
        result = []
        for (title,  codes) in MapMKBCharactersToCharacterCodeForDiagnosis:
            idList = []
            for code in codes:
                if code in mapCodeToId:
                    idList.append(mapCodeToId[code])
            result.append(idList)
        MapMKBCharactersToCharacterIDForDiagnosis = result
    return MapMKBCharactersToCharacterIDForDiagnosis


def getAvailableCharacterIdByMKB(MKB):
    u"""
        получить список id записей характеров в соответствии с кодом МКБ
    """
# in RefBooks/MKB.py:
#MKBCharacters = [   u'нет',                             #0
#                    u'острое',                          #1
#                    u'хроническое впервые выявленное',  #2
#                    u'хроническое ранее известное',     #3
#                    u'обострение хронического',         #4
#                    u'хроническое',                     #5
#                    u'хроническое или острое',          #6
#                ]
    fixedMKB = MKBwithoutSubclassification(MKB)
    MKBCharacters = forceInt(QtGui.qApp.db.translate('MKB_Tree', 'DiagID', fixedMKB, 'characters'))
    return getMapMKBCharactersToCharacterID()[MKBCharacters]


def getAvailableCharacterIdByMKBForDiagnosis(MKB):
    u"""
        Получить список id записей характеров в соответствии с кодом МКБ с учетом replaceInDiagnosis
        (проходят только характеры, у которых code == replaceInDiagnosis
    """
    fixedMKB = MKBwithoutSubclassification(MKB)
    MKBCharacters = forceInt(QtGui.qApp.db.translate('MKB_Tree', 'DiagID', fixedMKB, 'characters'))
    return getMapMKBCharactersToCharacterIDForDiagnosis()[MKBCharacters]


def getExactServiceId(diagnosisServiceId, eventServiceId, personServiceId, eventTypeId, visitTypeId, sceneId):
    u"""получить id услуги с учётом дополнительных факторов"""
    db = QtGui.qApp.db
    baseServiceId = diagnosisServiceId or personServiceId or eventServiceId
    baseServiceCode = forceString(db.translate('rbService', 'id', baseServiceId, 'code'))
    serviceCode = baseServiceCode

    try:
        serviceCode = applyModifier(serviceCode, forceStringEx(getEventVisitServiceModifier(eventTypeId)))
    except ValueError:
        QtGui.qApp.logCurrentException()

    try:
        serviceCode = applyModifier(serviceCode, forceStringEx(db.translate('rbVisitType', 'id', visitTypeId, 'serviceModifier')))
    except ValueError:
        QtGui.qApp.logCurrentException()

    try:
        serviceCode = applyModifier(serviceCode, forceStringEx(db.translate('rbScene', 'id', sceneId, 'serviceModifier')))
    except ValueError:
        QtGui.qApp.logCurrentException()

    if serviceCode == baseServiceCode:
        return baseServiceId
    elif serviceCode:
        return forceRef(db.translate('rbService', 'code', serviceCode, 'id'))
    else:
        return None


def createVisits(eventId, eventTypeId=None):
    db = QtGui.qApp.db
    sceneId = forceRef(db.translate('rbScene', 'code',  '1', 'id'))
    if not eventTypeId:
        eventTypeId = forceRef(db.translate('Event', 'id',  eventId, 'eventType_id'))
    eventServiceId = getEventServiceId(eventTypeId)

    tableDiagnostic = db.table('Diagnostic')
    tableVisit      = db.table('Visit')
    tableEventTypeDiagnostic = db.table('EventType_Diagnostic')
    diagnosisTypes  = db.getIdList('rbDiagnosisType', where='code in (1, 2)') # magic
    diagnostics     = db.getRecordList(tableDiagnostic, '*', where=tableDiagnostic['event_id'].eq(eventId))
    db.deleteRecord(tableVisit, where=tableVisit['event_id'].eq(eventId))
    if sceneId and eventTypeId:
        for diagnostic in diagnostics:
            diagnosisTypeId = forceRef(diagnostic.value('diagnosisType_id'))
            if diagnosisTypeId in  diagnosisTypes:
                setDate = forceDate(diagnostic.value('setDate'))
                endDate = forceDate(diagnostic.value('endDate'))
                specialityId = forceRef(diagnostic.value('speciality_id'))
                personId     = forceRef(diagnostic.value('person_id'))
                financeId    = forceRef(db.translate('Person', 'id', personId, 'finance_id'))
                serviceId    = forceRef(db.translate('rbSpeciality', 'id', specialityId, 'service_id'))
                visitTypeCond = [tableEventTypeDiagnostic['eventType_id'].eq(eventTypeId),
                                 tableEventTypeDiagnostic['speciality_id'].eq(specialityId)]
                visitTypeIdList  = db.getIdList(tableEventTypeDiagnostic, 'visitType_id', where=visitTypeCond)
                if visitTypeIdList:
                    visitTypeId = visitTypeIdList[0]
                else:
                    visitTypeId = None
                serviceId    = getExactServiceId(None, eventServiceId, serviceId, visitTypeId, sceneId)
                if not endDate.isNull() and (setDate.isNull() or setDate<=endDate) \
                   and personId     \
                   and financeId    \
                   and serviceId    \
                   and visitTypeId:
                    record = tableVisit.newRecord()
                    record.setValue('event_id',     toVariant(eventId))
                    record.setValue('scene_id',     toVariant(sceneId))
                    record.setValue('date',         toVariant(endDate))
                    record.setValue('visitType_id', toVariant(visitTypeId))
                    record.setValue('person_id',    toVariant(personId))
                    record.setValue('isPrimary',    toVariant(1))
                    record.setValue('finance_id',   toVariant(financeId))
                    record.setValue('service_id',   toVariant(serviceId))
                    record.setValue('payStatus',    toVariant(0))
                    db.insertRecord(tableVisit, record)


# TODO: Перенести в /library
def getMKBName(MKB):
    db = QtGui.qApp.db
    table = db.table('MKB_Tree')
    return forceString(db.translate(table, 'DiagID', MKB, 'DiagName'))


def getMKBBlockName(MKB):
    mainCode = MKBwithoutSubclassification(MKB)
    db = QtGui.qApp.db
    table = db.table('MKB_Tree')
    record = db.getRecordEx(table, 'DiagName', table['DiagID'].eq(u"getMKBBlockID('%s')" % mainCode))
    if record:
        result = forceString(record.value(0))
    else:
        result = ''
    return result


def getMKBClassName(MKB):
    mainCode = MKBwithoutSubclassification(MKB)
    db = QtGui.qApp.db
    table = db.table('MKB_Tree')
    record = db.getRecordEx(table, 'DiagName', table['DiagID'].eq(u"getMKBClassID('%s')" % mainCode))
    if record:
        result = forceString(record.value(0))
    else:
        result = ''
    return result


def getMKBList(begDate, endDate):
    mkbList = []
    db = QtGui.qApp.db
    tableEvent                = db.table('Event')
    tableDiagnosis            = db.table('Diagnosis')
    tableDiagnostic           = db.table('Diagnostic')
    queryTable = tableEvent.innerJoin(tableDiagnostic, ['%s = getEventDiagnostic(%s)' % (tableDiagnostic['id'].name(),
                                                                                        tableEvent['id'].name()),
                                                        tableDiagnostic['event_id'].eq(tableEvent['id']),
                                                        tableDiagnostic['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(tableDiagnosis, tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']))
    cond = [tableEvent['deleted'].eq(0),
            tableEvent['client_id'].eq(QtGui.qApp.currentClientId())
            ]
#       addDateInRange(cond, tableDiagnosis['setDate'], begDate, endDate)
    addDateInRange(cond, tableEvent['setDate'], begDate, endDate)
    records = db.getRecordList(queryTable, [tableDiagnosis['MKB']], cond, isDistinct = True, order = tableDiagnosis['MKB'])
    for record in records:
        mkb = forceString(record.value('MKB'))
        if mkb:
            mkbList.append(mkb)
    return mkbList


class CPayStatus:
    initial    = 0 # ни выставления, ни оплаты, ни отказа
    exposed    = 1 # выставлено, но не оплачено и не отказано
    refused    = 2 # отказано
    payed      = 3 # оплачено

    names      = (u'не выставлено', u'выставлено', u'отказано', u'оплачено')

    exposedBits = 0x55555555
    refusedBits = 0xAAAAAAAA
    payedBits   = 0xFFFFFFFF


def getPayStatusValueByCode(status, financeCode):
    return status << (2*financeCode)


def getPayStatusMaskByCode(financeCode):
    return 3 << (2*financeCode)


def extractLonePayStaus(payStatus, financeCode):
    return  (payStatus >> (2*financeCode)) & 3


def getPayStatusMask(financeId):
    code = CFinanceType.getCode(financeId)
    return 3 << (2*code)


def getExposed(payStatusMask):
    return CPayStatus.exposedBits & payStatusMask

#Возвращает число, соответствующее отказу при заданной маске статуса (на заданные типы финансирования)
def getRefused(payStatusMask):
    return CPayStatus.refusedBits & payStatusMask


def getPayed(payStatusMask):
    return payStatusMask


def getWorstPayStatus(payStatus):
    statusSet = set([CPayStatus.initial])
    while payStatus>0:
        status = payStatus & 0x3
        statusSet.add(status)
        payStatus = payStatus >> 2
    for status in [ CPayStatus.exposed, CPayStatus.payed, CPayStatus.refused, CPayStatus.initial]:
        if status in statusSet:
            return status


def payStatusText(payStatus):
    resultList = []
    for code in CFinanceType.allCodes:
        status = extractLonePayStaus(payStatus, code)
        if status:
            name = forceString(CFinanceType.getNameByCode(code))
            resultList.append( name + ': ' + CPayStatus.names[status] )
    return ', '.join(resultList)


def getRealPayed(payStatus):
    for code in CFinanceType.allCodes:
        status = extractLonePayStaus(payStatus, code)
        if status == CPayStatus.payed:
            return True
    return False


def getStatusRefused(payStatus):
    for code in CFinanceType.allCodes:
        status = extractLonePayStaus(payStatus, code)
        if status == CPayStatus.refused:
            return True
    return False


def getActionTypeDescendants(actionTypeId, class_=None):
    db = QtGui.qApp.db
    tableActionType = db.table('ActionType')

    result = set([actionTypeId])
    parents = [actionTypeId]

    if actionTypeId and class_ is None:
        class_ = db.translate(tableActionType, 'id', actionTypeId, 'class')
    if class_:
        classCond = tableActionType['class'].eq(class_)
    else:
        classCond = None
    while parents:
        cond = tableActionType['group_id'].inlist(parents)
        if classCond:
            cond = [cond, classCond]
        children = set(db.getIdList(tableActionType, where=cond))
        newChildren = children-result
        result |= newChildren
        parents = newChildren
    return list(result)


def getClosingMKBValueForAction(diagnosticsRecordList, diagnosisTypeIdList):
    for diagnosisTypeId in diagnosisTypeIdList:
        for record in diagnosticsRecordList:
            if forceRef(record.value('diagnosisType_id')) == diagnosisTypeId:
                return forceString(record.value('MKB'))
    return ''


def getClosingMorphologyValueForAction(diagnosticsRecordList, diagnosisTypeIdList):
    for diagnosisTypeId in diagnosisTypeIdList:
        for record in diagnosticsRecordList:
            if forceRef(record.value('diagnosisType_id')) == diagnosisTypeId:
                return forceString(record.value('morphologyMKB'))
    return ''


def getMKBValueBySetPerson(diagnosticsRecordList, setPersonId, diagnosisTypeIdList, eventPersonId):
    for diagnosisTypeId in diagnosisTypeIdList:
        for record in diagnosticsRecordList:
            if not record.value('person_id').isNull():
                diagnosticsPersonId = forceRef(record.value('person_id'))
                if diagnosticsPersonId == setPersonId:
                    if forceRef(record.value('diagnosisType_id')) == diagnosisTypeId:
                        return forceString(record.value('MKB'))
    for diagnosisTypeId in diagnosisTypeIdList:
        for record in diagnosticsRecordList:
            if eventPersonId == setPersonId:
                if forceRef(record.value('diagnosisType_id')) == diagnosisTypeId:
                    return forceString(record.value('MKB'))
    return ''


def getMorphologyValueBySetPerson(diagnosticsRecordList, setPersonId, diagnosisTypeIdList, eventPersonId):
    for diagnosisTypeId in diagnosisTypeIdList:
        for record in diagnosticsRecordList:
            if not record.value('person_id').isNull():
                diagnosticsPersonId = forceRef(record.value('person_id'))
                if diagnosticsPersonId == setPersonId:
                    if forceRef(record.value('diagnosisType_id')) == diagnosisTypeId:
                        return forceString(record.value('morphologyMKB'))
    for diagnosisTypeId in diagnosisTypeIdList:
        for record in diagnosticsRecordList:
            if eventPersonId == setPersonId:
                if forceRef(record.value('diagnosisType_id')) == diagnosisTypeId:
                    return forceString(record.value('morphologyMKB'))
    return ''


class CTableSummaryActionsMenuMixin():
    u"""
    Реализация контекстного меню
    таблицы "Мероприятия" вкладки
    "Стат.учет" форм ввода (ф.000,ф.003,ф.025,ф.030)
    """
    def __init__(self, tabsTableList=None):
        self.tabsTableList = tabsTableList or [
            self.tabStatus.tblAPActions,
            self.tabDiagnostic.tblAPActions,
            self.tabCure.tblAPActions,
            self.tabMisc.tblAPActions,
            # self.tabAnalyses.tblAPActions
        ]
        self.tabsTableParentList = [item.parent() for item in self.tabsTableList]
        self.setupActionsMenu()
        self.tblActions.setPopupMenu(self.mnuAction)

        self.qshcActionsEdit = QtGui.QShortcut(QtGui.QKeySequence('F4'), self.tblActions, self.on_actActionEdit_triggered)

        self.qshcActionsEdit.setObjectName('qshcActionsEdit')
        self.qshcActionsEdit.setContext(QtCore.Qt.WidgetShortcut)
        QtCore.QObject.connect(self.actActionEdit, QtCore.SIGNAL('triggered()'), self.on_actActionEdit_triggered)

        self.qshcAPActionAddSuchAs = QtGui.QShortcut(QtGui.QKeySequence('F2'), self.tblActions, self.on_actAPActionAddSuchAs_triggered)

        self.qshcAPActionAddSuchAs.setObjectName('qshcAPActionAddSuchAs')
        self.qshcAPActionAddSuchAs.setContext(QtCore.Qt.WidgetShortcut)
        QtCore.QObject.connect(self.actActionAddSuchAs, QtCore.SIGNAL('triggered()'), self.on_actAPActionAddSuchAs_triggered)
        QtCore.QObject.connect(self.actDeleteRow, QtCore.SIGNAL('triggered()'), self.on_actDeleteRow_triggered)
        QtCore.QObject.connect(self.tblActions.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.onAboutToShow)

    def setupActionsMenu(self):
        self.mnuAction = QtGui.QMenu(self)
        self.mnuAction.setObjectName('mnuAction')

        self.actActionEdit = QtGui.QAction(u'Перейти к редактированию', self)

        self.actActionEdit.setObjectName('actActionEdit')
        self.actActionEdit.setShortcut(QtCore.Qt.Key_F4)
        self.mnuAction.addAction(self.actActionEdit)

        self.actActionAddSuchAs = QtGui.QAction(u'Добавить такой же', self)

        self.actActionAddSuchAs.setObjectName('actActionAddSuchAs')
        self.actActionAddSuchAs.setShortcut(QtCore.Qt.Key_F2)
        self.mnuAction.addAction(self.actActionAddSuchAs)

        self.actDeleteRow = QtGui.QAction(u'Удалить запись', self)

        self.actDeleteRow.setObjectName('actDeleteRow')
        self.mnuAction.addAction(self.actDeleteRow)

    def getPageAndRow(self):
        index = self.tblActions.currentIndex()
        row = index.row()
        #atronah: я просто молча тут повздыхаю...
        if 0 <= row < len(self.modelActionsSummary.itemIndex):
            return self.modelActionsSummary.itemIndex[row]
        else:
            return None, None

    def onAboutToShow(self):
        row = self.tblActions.currentIndex().row()
        rows = self.tblActions.getSelectedRows()
        canDeleteRow = any(map(self.modelActionsSummary.isDeletable, rows)) if rows else False
        if len(rows) == 1 and rows[0] == row:
            self.actDeleteRow.setText(u'Удалить текущую строку')
        elif len(rows) == 1:
            self.actDeleteRow.setText(u'Удалить выделенную строку')
        else:
            self.actDeleteRow.setText(u'Удалить выделенные строки')
        self.actDeleteRow.setEnabled(canDeleteRow)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblActions_doubleClicked(self, index):
        # TODO:skkachaev: Тут происходит что-то странное в МСЧ3 при работе с кассой. А может и не при работе с кассой
        # (list index out of range) File "src\Events\Utils.py", line 2164, in on_tblActions_doubleClicked
        # Трэйс обрезанный, да.
        # В индексе приходит что-то совсем-совсем не то, но воспроизвести непосредственно ни разу не получилось
        tabTokenRow = index.row()
        if 0 <= tabTokenRow < len(self.modelActionsSummary.itemIndex):
            page, row = self.modelActionsSummary.itemIndex[tabTokenRow]
            model = self.modelActionsSummary.models[page]
            rowIndex = model.index(row, 0)
            tabs = [item for item in self.tabsTableParentList if hasattr(item, 'tblAPActions') and item.tblAPActions.model() is model]
            if tabs:
                tab = tabs[0]
            else:
                import traceback
                log(logDir=QtGui.qApp.logDir,
                    title=u'Events\\Utils\\on_tblActions_doubleClicked произошло что-то странное.',
                    message=u'tabsTableParentList: %s' % unicode(self.tabsTableParentList),
                    stack=traceback.format_stack())
                return
            self.tabWidget.setCurrentWidget(tab)
            tab.tblAPActions.setCurrentIndex(rowIndex)

    @QtCore.pyqtSlot()
    def on_actActionEdit_triggered(self):
        self.on_tblActions_doubleClicked(self.tblActions.currentIndex())

    @QtCore.pyqtSlot()
    def on_actAPActionAddSuchAs_triggered(self):
        index = self.tblActions.currentIndex()
        rowSummary = index.row()
        columnSummary = index.column()
        if 0 <= rowSummary < len(self.modelActionsSummary.itemIndex):
            page, row = self.modelActionsSummary.itemIndex[rowSummary]
            tbl = self.tabsTableList[page]
            model = tbl.model()
            if 0 <= row < model.rowCount() - 1:
                record = model._items[row][0]
                actionTypeId = forceRef(record.value('actionType_id'))
                index = model.index(model.rowCount() - 1, 0)
                if model.setData(index, toVariant(actionTypeId)):
                    newRowSummary = len(model.items()) - row + rowSummary - 1
                    indexSummary = self.tblActions.model().index(newRowSummary, columnSummary)
                    self.tblActions.setCurrentIndex(indexSummary)

    @QtCore.pyqtSlot()
    def on_actDeleteRow_triggered(self):
        rowsSortByPagesTables = {}
        rows = self.tblActions.getSelectedRows()

        # for x in self.tabsTableParentList:
        #     x.loadActionsLite(self.itemId())
        # self.modelActionsSummary.regenerate()

        tabsTableList = [
            self.tabStatus.tblAPActions,
            self.tabDiagnostic.tblAPActions,
            self.tabCure.tblAPActions,
            self.tabMisc.tblAPActions,
            # self.tabAnalyses.tblAPActions
        ]

        tbl = None
        for row in rows:
            if 0 <= row < len(self.modelActionsSummary.itemIndex):
                item = self.modelActionsSummary.items()[row]
                if forceRef(item.value('actionType_id')) in self.modelActionsSummary.notDeletedActionTypes.keys():
                    QtGui.QMessageBox.critical(self, u'Ошибка', u'Невозможно удалить обязательные услуги: \'%s\'.' % ', '.join(self.modelActionsSummary.notDeletedActionTypes.values()),
                                               QtGui.QMessageBox.Ok)
                    continue
                page, row = self.modelActionsSummary.itemIndex[row]

                try:
                    tbl = tabsTableList[page]
                except:
                    tbl = self.tabsTableParentList[1].tblAPActions

                if not tbl.model().isLockedOrExposed(row):
                    rowsList = rowsSortByPagesTables.get(tbl, None)
                    if rowsList:
                        rowsList.append(row)
                    else:
                        rowsSortByPagesTables[tbl] = [row]
        for tbl in rowsSortByPagesTables:
            rows = rowsSortByPagesTables.get(tbl, [])
            rows.sort(reverse=True)
            for row in rows:
                tbl.model().removeRow(row)
            tbl.emitDelRows()

def checkTissueJournalStatusByActions(actionModelItemsList):
    ttjIdList = []
    for record, action in actionModelItemsList:
        ttjId = forceRef(record.value('takenTissueJournal_id'))
        if ttjId and not ttjId in ttjIdList:
            ttjIdList.append(ttjId)
            checkTissueJournalStatus(ttjId)


def checkTissueJournalStatus(ttjId, fromJobTicketEditor=False):
    db = QtGui.qApp.db
    tableAction = db.table('Action')
    tableTTJ = db.table('TakenTissueJournal')

    cond = [
        tableAction['takenTissueJournal_id'].eq(ttjId),
        tableAction['deleted'].eq(0)
    ]
    actionStatusList = db.getColumnValues(tableAction, tableAction['status'], cond, isDistinct=True, handler=forceInt)
    if len(actionStatusList) > 1:
        db.updateRecords(tableTTJ, tableTTJ['status'].eq(0), tableTTJ['id'].eq(ttjId))
    elif len(actionStatusList) == 1:
        if QtGui.qApp.defaultRegProbsWhithoutTissueJournal() and fromJobTicketEditor:
            ttjStatus = 2
        else:
            # в журнале забора биоматериалов теже статусы что и в действиях но со сдвигом на еденицу
            # статус 0 в журнале - 'в работе'
            actionsStatus = actionStatusList[0]
            ttjStatus = actionsStatus + 1
        db.updateRecords(tableTTJ, tableTTJ['status'].eq(ttjStatus), tableTTJ['id'].eq(ttjId))


def getExternalIdDateCond(tissueType, date):
    db = QtGui.qApp.db
    table = db.table('TakenTissueJournal')
    counterResetType = forceInt(db.translate('rbTissueType', 'id', tissueType, 'counterResetType'))
    if counterResetType == TisssueTypeCounterResetType.Daily:
        return table['datetimeTaken'].dateEq(date)
    elif counterResetType == TisssueTypeCounterResetType.Weekly:
        begDate = QtCore.QDate(date.year(), date.month(), QtCore.QDate(date).addDays(-(date.dayOfWeek()-1)).day())
        endDate = QtCore.QDate(begDate).addDays(6)
    elif counterResetType == TisssueTypeCounterResetType.Monthly:
        begDate = QtCore.QDate(date.year(), date.month(), 1)
        endDate = QtCore.QDate(date.year(), date.month(), date.daysInMonth())
    elif counterResetType == TisssueTypeCounterResetType.HalfYearly:
        begMonth = 1 if date.month() <= 6 else 7
        endDays = 30 if begMonth == 1 else 31
        begDate = QtCore.QDate(date.year(), begMonth, 1)
        endDate = QtCore.QDate(date.year(), begMonth+5, endDays)
    elif counterResetType == TisssueTypeCounterResetType.Yearly:
        begDate = QtCore.QDate(date.year(), 1, 1)
        endDate = QtCore.QDate(date.year(), 12, 31)
    else:
        return None # никогда
    return db.joinAnd([table['datetimeTaken'].dateGe(begDate),
                       table['datetimeTaken'].dateLe(endDate)])


def checkUniqueEventExternalId(externalId, eventId=None):
    db = QtGui.qApp.db
    tableClient = db.table('Client')
    tableEvent = db.table('Event')
    table = tableEvent.innerJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))
    cond = [
        tableEvent['externalId'].eq(externalId),
        tableEvent['deleted'].eq(0)
    ]
    if eventId:
        cond.append(tableEvent['id'].ne(eventId))
    cols = [
        tableEvent['id'].alias('eventId'),
        tableEvent['eventType_id'],
        tableEvent['setDate'],
        tableEvent['client_id'],
        tableClient['lastName'],
        tableClient['firstName'],
        tableClient['patrName'],
    ]
    result = []
    for record in db.iterRecordList(table, cols, cond):
        id = forceRef(record.value('eventId'))
        eventType = getEventName(forceRef(record.value('eventType_id')))
        setDate = forceString(record.value('setDate'))
        clientName = formatName(record.value('lastName'), record.value('firstName'), record.value('patrName'))
        resultValue = u'Событие(%s): %d от %s, пациент \'%s\'' % (eventType, id, setDate, clientName)
        result.append(resultValue)
    return result


## Возвращает id результата обращения на основании id результата осмотра.
def getEventResultId(diagnosticResultId):
    if diagnosticResultId:
        return forceRef(QtGui.qApp.db.translate('rbDiagnosticResult', 'id', diagnosticResultId, 'result_id'))
    return None


## Возвращает id результата осмотра на основании id результата обращения.
def getResultIdByDiagnosticResultId(eventResultId):
    if eventResultId:
        return forceRef(QtGui.qApp.db.translate('rbDiagnosticResult', 'result_id', eventResultId, 'id'))
    return None


def setActionPropertiesColumnVisible(actionType, propertiesView):
    propertiesView.setColumnHidden(0, not actionType.propertyAssignedVisible)
    propertiesView.setColumnHidden(2, not actionType.propertyUnitVisible)
    propertiesView.setColumnHidden(3, not actionType.propertyNormVisible)
    propertiesView.setColumnHidden(4, not actionType.propertyEvaluationVisible)


def validCalculatorSettings(value):
    return bool(re.match('^[0-9/*-+][A%][0-9A-D]$', value))


def checkSpeciality(personId, actionTypeId):
    db = QtGui.qApp.db
    specialityId = forceRef(db.translate('Person', 'id', personId, 'speciality_id'))
    records = db.getRecordList('ActionType_Speciality', 'speciality_id', 'master_id=%s' % actionTypeId)
    specialities = []
    for record in records:
        specialities.append(forceRef(record.value('speciality_id')))
    if specialities and not specialityId in specialities:
        return False
    return True


def getTimeTableEventByPersonAndDate(date, personId):
    if date and personId:
        db = QtGui.qApp.db
        eventTypeId = getEventType(etcTimeTable).eventTypeId
        eventTable = db.table('Event')
        personTable = db.table('Person')
        cond = [eventTable['eventType_id'].eq(eventTypeId),
                eventTable['setDate'].eq(date),
                eventTable['execPerson_id'].eq(personId),
                '(Person.lastAccessibleTimelineDate IS NULL OR Person.lastAccessibleTimelineDate = \'0000-00-00\' OR DATE(Event.setDate)<=Person.lastAccessibleTimelineDate)'
               ]
        return db.getRecordEx(eventTable.leftJoin(personTable, personTable['id'].eq(eventTable['execPerson_id'])), [eventTable['id'], eventTable['setDate']], cond)
    else:
        return None


class CRadiationDoseSumLabel(QtGui.QLabel):
    def __init__(self, parent):
        QtGui.QLabel.__init__(self, parent)
        self._onlyTotalDoseInfo = True
        self._info = None

    def setRadiationDoseInfo(self, info):
        if info:
            self._info = info
            if self._onlyTotalDoseInfo:
                value = u'Сумма доз: %.2f'%info['total']
            else:
                value = '\n'.join(['%s: %s' % (key, item) for key, item in info.items() if key != 'total']+[u'Всего: %s'%info['total']])
            self.setText(value)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._onlyTotalDoseInfo = not self._onlyTotalDoseInfo
            self.setRadiationDoseInfo(self._info)
        QtGui.QLabel.mousePressEvent(self, event)


class CActionTemplateCache(object):
    def __init__(self, eventEditor):
        self.eventEditor = eventEditor
        self.data = {}

    def reset(self, actionTypeId=None):
        if actionTypeId:
            if actionTypeId in self.data:
                del self.data[actionTypeId]
        else:
            self.data = {}

    def getModel(self, actionTypeId, actionPersonId):
        if actionTypeId in self.data:
            result = self.data[actionTypeId]
        else:
            result = self.createModel(actionTypeId, actionPersonId)
            self.data[actionTypeId] = result
        return result

    def createModel(self, actionTypeId, actionPersonId):
        result = CActionTemplateModel(self.eventEditor,
                                      actionTypeId,
                                      actionPersonId,
                                      self.eventEditor.personSpecialityId,
                                      self.eventEditor.clientSex, self.eventEditor.clientAge, removeEmptyNodes=True)
        return result


# TODO: atronah: создать класс CAutoPrintTemplate и объединить в нем логику автопечати для событий и действий.
# TODO: atronah: создать именованные константы для типов сброса.
def getExpiredDate(repeatResetType, repeatResetDate = None):
    u"""
        Рассчитывает дату истечения срока действия запрета на автопечать на основании типа сброса.

    :rtype : QDate
    :param repeatResetType: - тип сброса:
            1 - сбрасывать в указанную дату (repeatResetDate)
            2 - cбрасывать в конце текущего месяца
            3 - cбрасывать в конце текущего года
    :param repeatResetDate: - пользовательская (произвольная) дата сброса при типе repeatResetType = 1
    :return: дату сброса запрета на автопечать
    """
    if repeatResetType == 1 and repeatResetDate: # Сбрасывать в указанную дату
        return repeatResetDate
    elif repeatResetType == 2: # Сбрасывать в конце месяца
        currentDate = QtCore.QDate.currentDate()
        return QtCore.QDate(currentDate.year(),
                     currentDate.month(),
                     currentDate.daysInMonth())
    elif repeatResetType == 3: # Сбрасывать в конце года
        currentDate = QtCore.QDate.currentDate()
        return QtCore.QDate(currentDate.year(),
                            12,
                            31)
    return QtCore.QDate()


class CActionWidgetVisibilityButton(QtGui.QToolButton):
    __pyqtSignals__ = ('arrowTypeChanged(bool)',
                      )
    arrowType = None
    def __init__(self, parent=None):
        QtGui.QToolButton.__init__(self, parent)
        self._arrowType = self.getArrowType()
        self.connect(self, QtCore.SIGNAL('released()'), self.on_arrowChanged)

    def on_arrowChanged(self):
        self.applayArrow(self.changeArrowType())

    def emitArrowTypeChanged(self):
        self.emit(QtCore.SIGNAL('arrowTypeChanged(bool)'), self._arrowType==QtCore.Qt.UpArrow)

    def applayArrow(self, arrowType=None):
        if arrowType is None:
            arrowType = self.getArrowType() if self.getArrowType() else self.changeArrowType()
        self._arrowType = arrowType
        self.setArrowType(self._arrowType)
        self.emitArrowTypeChanged()

    @classmethod
    def changeArrowType(cls):
        cls.arrowType = {False: QtCore.Qt.UpArrow, True:QtCore.Qt.DownArrow}.get(cls.arrowType==QtCore.Qt.UpArrow, QtCore.Qt.UpArrow)
        return cls.arrowType

    @classmethod
    def getArrowType(cls):
        return cls.arrowType


def recommendationIsActual(recommendationRecord):
    expireDate = forceDate(recommendationRecord.value('expireDate'))
    currentDate = QtCore.QDate.currentDate()
    amountLeft = forceDouble(recommendationRecord.value('amount_left'))
    person2 = forceRef(recommendationRecord.value('person2_id'))
    return currentDate <= expireDate and amountLeft > 0.0 and not person2


def setOrgStructureIdToCmbPerson(cmb):
    if forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'linkingPerson', None)):
        orgStructureId = forceInt(getVal(QtGui.qApp.preferences.appPrefs, 'orgStructureId', None))
        if forceInt(cmb.personId):
            db = QtGui.qApp.db
            tblPerson = db.table('Person')
            recOrgStruct = db.translate(tblPerson, tblPerson['id'], forceInt(cmb.personId), tblPerson['orgStructure_id'])
            if recOrgStruct:
                if forceInt(recOrgStruct) == orgStructureId:
                    cmb.setOrgStructureId(orgStructureId)
        elif orgStructureId:
            cmb.setOrgStructureId(orgStructureId)


def getMainActionTypesAnalyses():
    u""" Список главных действий (по которым группируются анализы) """
    db = QtGui.qApp.db
    tableATTT = db.table('ActionType_TissueType')
    return db.getIdList(tableATTT, tableATTT['master_id'], tableATTT['isActiveGroup'].eq(1))


def getMainActionTypeAnalyses(actionTypeId):
    if actionTypeId is None: return None
    db = QtGui.qApp.db
    ActionType = db.table('ActionType')
    ATTT = db.table('ActionType_TissueType')

    idList = db.getIdList(ActionType.innerJoin(ATTT, [ATTT['master_id'].eq(ActionType['group_id']),
                                                      ATTT['isActiveGroup'].eq(1)]),
                          idCol=ATTT['master_id'],
                          where=ActionType['id'].eq(actionTypeId),
                          limit=1)
    return idList[0] if idList else None


def isLittleStranger(clientId, begDate, endDate):
    u"""
    Для привязки полисов в обращениях:
    Считаем пациента новорожденным, если возраст на дату начала лечения < 90 дней и нет действующего полиса на дату окончания лечения
    """
    db = QtGui.qApp.db
    ClientPolicy = db.table('ClientPolicy')

    policyCond = [
        ClientPolicy['client_id'].eq(clientId),
        ClientPolicy['deleted'].eq(0)
    ]
    if endDate and not endDate.isNull():
        policyCond.extend([
            db.joinOr([ClientPolicy['begDate'].isNull(),
                       ClientPolicy['begDate'].dateLe(endDate)]),
            db.joinOr([ClientPolicy['endDate'].isNull(),
                       ClientPolicy['endDate'].dateGe(endDate)])
        ])

    age = calcAgeInDays(forceDate(db.getRecord('Client', 'birthDate', clientId).value('birthDate')), begDate)
    return age < 90 and db.getRecordEx(ClientPolicy, ClientPolicy['id'], policyCond) is None


def getEventAcceptablePolicyList(clientId, policyTypeId=None, policyKindId=None, date=None, eventIsClosed=False):
    u"""
    Список полисов пациента, подходящих для привязки к обращению:
    при привязке к обращению временных свидетельств, полученных после окончания лечения в течение 30 дней
    используюется расширенный диапазон для поиска по дате начала полиса: (..., Event.execDate + 30 дней]
    """
    db = QtGui.qApp.db
    tableCP = db.table('ClientPolicy')
    tablePK = db.table('rbPolicyKind')

    TmpPolicyKindCode = '2'

    table = tableCP.leftJoin(tablePK, tablePK['id'].eq(tableCP['policyKind_id']))

    cond = [
        tableCP['client_id'].eq(clientId),
        tableCP['deleted'].eq(0)
    ]

    if policyTypeId is not None:
        cond.append(tableCP['policyType_id'].eq(policyTypeId))

    if policyKindId is not None:
        cond.append(tableCP['policyKind_id'].eq(policyKindId))

    if not (date is None or date.isNull()):
        cond.extend([
            db.joinOr([
                tableCP['begDate'].isNull(),
                db.if_(tablePK['code'].eq(TmpPolicyKindCode),
                       tableCP['begDate'].dateLe(date.addDays(30)),
                       tableCP['begDate'].dateLe(date)) if eventIsClosed else tableCP['begDate'].dateLe(date)
            ]),
            db.joinOr([
                tableCP['endDate'].isNull(),
                tableCP['endDate'].dateGe(date)
            ])
        ])

    order = [
        db.makeField(db.joinAnd([
            tablePK['id'].isNotNull(),
            tablePK['code'].eq(TmpPolicyKindCode),
            tableCP['begDate'].dateGt(date)
        ])).desc(),  # временные свидельства - в начале списка (наименьший приоритет), если таких несколько - приоритет выше у полиса с меньшим begDate
        tableCP['begDate'],
        tableCP['endDate'],
        tableCP['id']
    ]

    return db.getIdList(table, tableCP['id'], cond, order=order) if clientId else []


def getClientRepresentativePolicyList(clientId, policyTypeId=None, policyKindId=None, date=None):
    db = QtGui.qApp.db
    Client = db.table('Client')
    ClientPolicy = db.table('ClientPolicy')
    ClientRelation = db.table('ClientRelation')
    RelationType = db.table('rbRelationType')

    backwardRelStmt = db.selectStmt(
        table=ClientRelation.innerJoin(RelationType, [RelationType['id'].eq(ClientRelation['relativeType_id']),
                                                      RelationType['isBackwardRepresentative'].eq(1)]),
        fields=[
            ClientRelation['relative_id'].alias('relativeId'),
            ClientRelation['relativeType_id'].alias('relTypeId')
        ],
        where=[
            ClientRelation['client_id'].eq(clientId),
            ClientRelation['deleted'].eq(0)
        ]
    )
    directRelStmt = db.selectStmt(
        table=ClientRelation.innerJoin(RelationType, [RelationType['id'].eq(ClientRelation['relativeType_id']),
                                                      RelationType['isDirectRepresentative'].eq(1)]),
        fields=[
            ClientRelation['client_id'].alias('relativeId'),
            ClientRelation['relativeType_id'].alias('relTypeId')
        ],
        where=[
            ClientRelation['relative_id'].eq(clientId),
            ClientRelation['deleted'].eq(0)
        ]
    )
    Relation = CUnionTable(db, backwardRelStmt, directRelStmt, 'Relation')

    table = Relation.innerJoin(Client, [Client['id'].eq(Relation['relativeId']),
                                        Client['deleted'].eq(0)])
    table = table.innerJoin(ClientPolicy, ClientPolicy['client_id'].eq(Client['id']))

    cond = [
        ClientPolicy['deleted'].eq(0)
    ]

    if policyTypeId is not None:
        cond.append(ClientPolicy['policyType_id'].eq(policyTypeId))

    if policyKindId is not None:
        cond.append(ClientPolicy['policyKind_id'].eq(policyKindId))

    if not (date is None or date.isNull()):
        cond.extend([
            db.joinOr([ClientPolicy['begDate'].isNull(),
                       ClientPolicy['begDate'].dateLe(date)]),
            db.joinOr([ClientPolicy['endDate'].isNull(),
                       ClientPolicy['endDate'].dateGe(date)])
        ])

    order = [
        ClientPolicy['begDate'],
        ClientPolicy['endDate'],
        ClientPolicy['id']
    ]
    return db.getIdList(table, ClientPolicy['id'], cond, order=order) if clientId else []


def getDiagnosisService(mkbCode, personId=None, specialityId=None):
    db = QtGui.qApp.db
    tableMkbSS = db.table('MKBServiceSpeciality')
    tableMkbTree = db.table('MKB_Tree')
    tablePerson = db.table('Person')

    table = tableMkbTree
    table = table.innerJoin(tableMkbSS, tableMkbSS['mkb_id'].eq(tableMkbTree['id']))
    cols = [
        tableMkbSS['service_id']
    ]
    cond = [
        tableMkbTree['DiagID'].eq(mkbCode)
    ]
    if personId or specialityId:
        if personId:
            table = table.innerJoin(tablePerson, tablePerson['speciality_id'].eq(tableMkbSS['speciality_id']))
            cond.append(tablePerson['id'].eq(personId))
        elif specialityId:
            cond.append(tableMkbSS['speciality_id'].eq(specialityId))
    else:
        cond.append(tableMkbSS['speciality_id'].isNull())

    rec = db.getRecordEx(table, cols, cond)
    return forceRef(rec.value('service_id')) if rec else None


class CDiagnosisServiceMap(object):
    serviceMap = {}

    @classmethod
    def get(cls, mkbCode):
        if mkbCode not in cls.serviceMap:
            cls.serviceMap[mkbCode] = getDiagnosisService(mkbCode)
        return cls.serviceMap[mkbCode]