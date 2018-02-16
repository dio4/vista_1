# -*- coding: utf-8 -*-
from Events.Service import CServiceInfo
from Orgs.Utils import COrgInfo, COrgStructureInfo
from library.PrintInfo import CInfo, CInfoList, CDateInfo, CRBInfo
from library.Utils import *


class CRBMedicalAidUnitInfo(CRBInfo):
    tableName = 'rbMedicalAidUnitInfo'


class CRBPayRefuseTypeInfo(CRBInfo):
    tableName = 'rbPayRefuseType'

    def __init__(self, context, id):
        CRBInfo.__init__(self, context, id)

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord(self.tableName, '*', self.id) if self.id else None
        if record:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            self._OSN = forceString(record.value('OSN'))
            self._initByRecord(record)
            return True
        else:
            self._code = ''
            self._name = ''
            self._OSN = ''
            self._initByNull()
            return False

    OSN = property(lambda self: self.load()._OSN)


class CAccountItemInfo(CInfo):
    def __init__(self, context, id):
        CInfo.__init__(self, context)
        self.id = id

    def _load(self):
        from Events.EventInfo import CEventInfo, CVisitInfo
        from Events.ActionInfo import CActionInfo

        db = QtGui.qApp.db
        record = db.getRecord('Account_Item', '*', self.id)
        if record:
            result = True
        else:
            record = db.table('Account_Item').newRecord()
            result = False

        self._serviceDate = CDateInfo(forceDate(record.value('serviceDate')))
        self._event = self.getInstance(CEventInfo, forceRef(record.value('event_id')))
        self._visit = self.getInstance(CVisitInfo, forceRef(record.value('visit_id')))
        self._action = self.getInstance(CActionInfo, forceRef(record.value('action_id')))
        self._price = forceDecimal(record.value('price'))
        self._unit = self.getInstance(CRBMedicalAidUnitInfo, forceRef(record.value('unit_id')))
        self._amount = forceDecimal(record.value('amount'))
        self._uet = forceDecimal(record.value('uet'))
        self._sum = forceDecimal(record.value('sum'))
        self._date = CDateInfo(forceDate(record.value('date')))
        self._number = forceString(record.value('number'))
        self._refuseType = self.getInstance(CRBPayRefuseTypeInfo, forceRef(record.value('refuseType_id')))
        self._reexposeItem = self.getInstance(CAccountItemInfo, forceRef(record.value('reexposeItem_id')))
        self._note = forceString(record.value('note'))
        self._service = self.getInstance(CServiceInfo, forceRef(record.value('service_id')))
        self._tariff_id = forceRef(record.value('tariff_id'))
        self._vat = forceDecimal(record.value('vat'))
        return result

    def __str__(self):
        self.load()
        return u'%s %s %s' % (self._serviceDate, self.event.client, self._sum)

    serviceDate = property(lambda self: self.load()._serviceDate)
    event = property(lambda self: self.load()._event)
    visit = property(lambda self: self.load()._visit)
    action = property(lambda self: self.load()._action)
    price = property(lambda self: self.load()._price)
    unit = property(lambda self: self.load()._unit)
    amount = property(lambda self: self.load()._amount)
    uet = property(lambda self: self.load()._uet)
    sum = property(lambda self: self.load()._sum)
    date = property(lambda self: self.load()._date)
    number = property(lambda self: self.load()._number)
    refuseType = property(lambda self: self.load()._refuseType)
    reexposeItem = property(lambda self: self.load()._reexposeItem)
    note = property(lambda self: self.load()._note)
    service = property(lambda self: self.load()._service)
    tariff_id = property(lambda self: self.load()._tariff_id)


class CRBAccountFormatInfo(CRBInfo):
    tableName = 'rbAccountExportFormat'

    def __init__(self, context, id):
        CRBInfo.__init__(self, context, id)

    def _initByRecord(self, record):
        self._prog = forceString(record.value('prog'))

    def _initByNull(self):
        self._prog = ''

    prog = property(lambda self: self.load()._prog)


class CAccountItemInfoList(CInfoList):
    def __init__(self, context, accountId):
        CInfoList.__init__(self, context)
        self.accountId = accountId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('Account_Item')
        idList = db.getIdList(table, 'id', [table['master_id'].eq(self.accountId),
                                            table['deleted'].eq(0)], 'id')
        self._items = [self.getInstance(CAccountItemInfo, id) for id in idList]
        return True


class CAccountInfo(CInfo):
    def __init__(self, context, id):
        CInfo.__init__(self, context)
        self.id = id
        self.selectedItemIdList = []

    def _load(self):
        from Events.EventInfo import CContractInfo

        db = QtGui.qApp.db
        record = db.getRecord('Account', '*', self.id)
        if record:
            result = True
        else:
            record = db.table('Account').newRecord()
            result = False
        self._contract = self.getInstance(CContractInfo, forceRef(record.value('contract_id')))
        self._orgStructure = self.getInstance(COrgStructureInfo, forceRef(record.value('orgStructure_id')))
        self._payer = self.getInstance(COrgInfo, forceRef(record.value('payer_id')))
        self._settleDate = CDateInfo(forceDate(record.value('settleDate')))
        self._number = forceString(record.value('number'))
        self._date = CDateInfo(forceDate(record.value('date')))
        self._amount = forceDecimal(record.value('amount'))
        self._uet = forceDecimal(record.value('uet'))
        self._sum = forceDecimal(record.value('sum'))
        self._exposeDate = CDateInfo(forceDate(record.value('exposeDate')))
        self._payedAmount = forceDecimal(record.value('payedAmount'))
        self._payedSum = forceDecimal(record.value('payedSum'))
        self._refusedAmount = forceDecimal(record.value('refusedAmount'))
        self._refusedSum = forceDecimal(record.value('refusedSum'))
        self._format = self.getInstance(CRBAccountFormatInfo, forceRef(record.value('format_id')))
        self._items = self.getInstance(CAccountItemInfoList, self.id)
        return result

    def __str__(self):
        self.load()
        return u'%s от %s' % (self._number, self._date)

    contract = property(lambda self: self.load()._contract)
    orgStructure = property(lambda self: self.load()._orgStructure)
    payer = property(lambda self: self.load()._payer)
    settleDate = property(lambda self: self.load()._settleDate)
    number = property(lambda self: self.load()._number)
    date = property(lambda self: self.load()._date)
    uet = property(lambda self: self.load()._uet)
    sum = property(lambda self: self.load()._sum)
    exposeDate = property(lambda self: self.load()._exposeDate)
    payedAmount = property(lambda self: self.load()._payedAmount)
    payedSum = property(lambda self: self.load()._payedSum)
    refusedAmount = property(lambda self: self.load()._refusedAmount)
    refusedSum = property(lambda self: self.load()._refusedSum)
    format = property(lambda self: self.load()._format)
    items = property(lambda self: self.load()._items)
