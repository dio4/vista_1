# -*- coding: utf-8 -*-

from library.Utils import forceRef, forceString
from library.exception import CException


class CAlfalabException(CException):
    pass


class TTJStatus:
    InJob = 0
    Awaiting = 1
    ToSend = 2
    Finished = 3
    WithoutResult = 4


class OrderStatus:
    NotSent = 0
    Awaiting = 1
    Finished = 2
    Outdated = 3

    nameMap = {
        NotSent : 'NOT SENT',
        Awaiting: 'AWAITING',
        Finished: 'FINISHED',
        Outdated: 'OUTDATED'
    }


class OrderSyncStatus:
    # SUCCESS
    OrderSent = 0
    ResultReceived = 1
    # FAILURE
    NoData = 2
    ResultNotReceived = 3
    PartialResultReceived = 4
    RequestError = 5
    NoOrderCodes = 6
    # EXCEPTION
    OtherError = 99

    nameMap = {
        OrderSent            : 'ORDER SUCCESSFULLY SENT',
        ResultReceived       : 'RESULT SUCCESSFULLY RECEIVED',

        NoData               : 'NO ORDER DATA',
        ResultNotReceived    : 'NO RESULT',
        PartialResultReceived: 'PARTIAL RESULT RECEIVED',
        RequestError         : 'REQUEST ERROR',
        NoOrderCodes         : 'NO ORDER CODES',

        OtherError           : 'OTHER ERROR'
    }


class ActionClass:
    Analyses = 4


class ActionStatus:
    Finished = 6


class JobTicketStatus:
    Finished = 2


class AlfalabNormsFlag:
    NotAvailable = 0
    Norm = 1
    NotNorm = 2
    BelowCriticalNorm = 3
    BelowNorm = 4
    WTF = 5
    AboveNorm = 6
    AboveCriticalNorm = 7

    nameMap = {
        NotAvailable     : u'нет данных',
        Norm             : u'норма',
        NotNorm          : u'не в норме',
        BelowCriticalNorm: u'ниже критической нормы',
        BelowNorm        : u'ниже нормы',
        WTF              : u'',
        AboveNorm        : u'выше нормы',
        AboveCriticalNorm: u'выше критической нормы'
    }

    # Отоборажение на ActionProperty.evaluation
    evaluationMap = {
        NotAvailable     : None,
        BelowCriticalNorm: -2,
        BelowNorm        : -1,
        Norm             : 0,
        AboveNorm        : 1,
        AboveCriticalNorm: 2
    }


class CFinanceMap(object):
    Budget = 1
    CMI = 2
    VMI = 3
    PaidStationary = 4
    SMP = 5
    HighTech_CMI = 6
    PaidAmbulatory = 7
    AKI = 10
    CMI_BT = 11
    Protocol = 44
    Other = 66

    nameMapLIS = {
        Budget        : u'Бюджет',
        CMI           : u'ОМС',
        VMI           : u'ДМС',
        PaidStationary: u'ПМУ (стационар)',
        SMP           : u'СМП',
        HighTech_CMI  : u'ВМП из ОМС',
        PaidAmbulatory: u'ПМУ (амб.)',
        AKI           : u'АКИ',
        CMI_BT        : u'ОМС ЛТ',
        Protocol      : u'Протокол',
        Other         : u'Прочее',
    }

    idMIS2LIS = {
        2 : CMI,
        3 : VMI,
        6 : HighTech_CMI,
        10: AKI,
        11: CMI_BT
    }

    @classmethod
    def getCodeLIS(cls, financeId, isStationary=False):
        if financeId in cls.idMIS2LIS:
            lisId = cls.idMIS2LIS[financeId]
        elif financeId == 4:  # ПМУ
            lisId = cls.PaidStationary if isStationary else cls.PaidAmbulatory
        else:
            lisId = cls.Other
        return lisId

    @classmethod
    def getCodeNameLIS(cls, financeId, isStationary=False):
        lisId = cls.getCodeLIS(financeId, isStationary)
        return lisId, cls.nameMapLIS[lisId]


class COrgStructureMap(object):
    u"""
    Для нестационарных обращений:
        для подразделений МЦ И ЦЛиП - головное подразделение;
        для подразделений Института - КДО
    """

    KDO_id = 152
    Institut_id = 430
    MedCenter_id = 414
    TnPCenter_id = 576

    def __init__(self, db):
        self._db = db
        self._orgStructureMap = {}
        self.update(self.Institut_id, self.KDO_id)
        self.update(self.MedCenter_id, self.MedCenter_id)
        self.update(self.TnPCenter_id, self.TnPCenter_id)

        OrgStructure = db.table('OrgStructure')
        self._codeNameMap = dict((forceRef(rec.value('id')),
                                  (forceString(rec.value('code')),
                                   forceString(rec.value('name'))))
                                 for rec in db.iterRecordList(OrgStructure, ['id', 'code', 'name'], OrgStructure['deleted'].eq(0)))

    def update(self, parentId, valueId):
        self._orgStructureMap.update(dict.fromkeys(self._db.getDescendants('OrgStructure', 'parent_id', parentId), valueId))

    def getHeadId(self, orgStructureId):
        return self._orgStructureMap.get(orgStructureId)

    def getCodeName(self, orgStructureId):
        return self._codeNameMap.get(orgStructureId, (None, None))
