# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtGui, QtCore

from Events.MKBInfo    import CMKBInfo

from Orgs.PersonInfo   import CPersonInfo

from library.PrintInfo import CInfo, CInfoList, CDateInfo, CRBInfo
from library.Utils     import forceBool, forceDate, forceInt, forceRef, forceString, formatSex, pyDate


class CTempInvalidRegimeInfo(CRBInfo):
    tableName = 'rbTempInvalidRegime'


class CTempInvalidBreakInfo(CRBInfo):
    tableName = 'rbTempInvalidBreak'


class CTempInvalidResultInfo(CRBInfo):
    tableName = 'rbTempInvalidResult'

    def _initByRecord(self, record):
        self._type = forceInt(record.value('type'))
        self._able = forceInt(record.value('able'))
        self._closed = forceInt(record.value('closed'))
        self._status = forceInt(record.value('status'))

    def _initByNull(self):
        self._type = -1
        self._able = -1
        self._closed = -1
        self._status = -1

    type = property(lambda self: self.load()._type)
    able = property(lambda self: self.load()._able)
    closed = property(lambda self: self.load()._closed)
    status = property(lambda self: self.load()._status)


class CTempInvalidPeriodInfo(CInfo):
    def __init__(self, context, id):
        CInfo.__init__(self, context)
        self.id = id
        self._begPerson = None
        self._begDate = CDateInfo()
        self._endPerson = None
        self._endDate = CDateInfo()
        self._numberPermit = ''
        self._begDatePermit = CDateInfo()
        self._endDatePermit = CDateInfo()
        self._isExternal = None
        self._regime = None
        self._break = None
        self._breakDate = CDateInfo()
        self._result = None
        self._note = ''
        self._directDateOnKAK = CDateInfo()
        self._expert = None
        self._dateKAK = CDateInfo()
        self._begDateHospital = CDateInfo()
        self._endDateHospital = CDateInfo()


    def _load(self):
        if self.id:
            db = QtGui.qApp.db
            table = db.table('TempInvalid_Period')
            record = db.getRecordEx(table, '*', table['id'].eq(self.id))
            if record:
                self.initByRecord(record)
                return True
        return False


    def initByRecord(self, record):
        self._begPerson  = self.getInstance(CPersonInfo, forceRef(record.value('begPerson_id')))
        self._begDate    = CDateInfo(forceDate(record.value('begDate')))
        self._endPerson  = self.getInstance(CPersonInfo, forceRef(record.value('endPerson_id')))
        self._endDate    = CDateInfo(forceDate(record.value('endDate')))
        self._numberPermit  = forceString(record.value('numberPermit'))
        self._begDatePermit = CDateInfo(forceDate(record.value('begDatePermit')))
        self._endDatePermit = CDateInfo(forceDate(record.value('endDatePermit')))
        self._isExternal = forceBool(record.value('isExternal'))
        self._regime     = self.getInstance(CTempInvalidRegimeInfo, forceRef(record.value('regime_id')))
        self._break      = self.getInstance(CTempInvalidBreakInfo, forceRef(record.value('break_id')))
        self._breakDate = CDateInfo(forceDate(record.value('breakDate')))
        self._note = forceString(record.value('note'))
        self._result     = self.getInstance(CTempInvalidResultInfo, forceRef(record.value('result_id')))
        self._directDateOnKAK = CDateInfo(forceDate(record.value('directDateOnKAK')))
        self._expert =  self.getInstance(CPersonInfo, forceRef(record.value('expert_id')))
        self._dateKAK = CDateInfo(forceDate(record.value('dateKAK')))
        self._begDateHospital = CDateInfo(forceDate(record.value('begDateHospital')))
        self._endDateHospital = CDateInfo(forceDate(record.value('endDateHospital')))


    begPerson   = property(lambda self: self.load()._begPerson,
                               doc = u"""
                                      Кто открыл период ВУТ (Начавшший).
                                      :rtype : CPersonInfo
                                  """)
    begDate     = property(lambda self: self.load()._begDate,
                               doc = u"""
                                      Дата открытия периода ВУТ.
                                      :rtype : CDateInfo
                                  """)
    endPerson   = property(lambda self: self.load()._endPerson,
                               doc = u"""
                                      Кто закрыл период ВУТ (Закончивший).
                                      :rtype : CPersonInfo
                                  """)
    endDate     = property(lambda self: self.load()._endDate,
                               doc = u"""
                                      Дата закрытия периода ВУТ.
                                      :rtype : CDateInfo
                                  """)
    numberPermit= property(lambda self: self.load()._numberPermit,
                           doc = u"""
                                      Номер путёвки
                                      :rtype : string
                                  """)
    begDatePermit= property(lambda self: self.load()._begDatePermit,
                               doc = u"""
                                      Дата начала путёвки.
                                      :rtype : CDateInfo
                                  """)
    endDatePermit= property(lambda self: self.load()._endDatePermit,
                               doc = u"""
                                      Дата окончания путёвки.
                                      :rtype : CDateInfo
                                  """)
    isExternal  = property(lambda self: self.load()._isExternal,
                                doc = u"""
                                      Внешний
                                      :rtype : bool
                                  """)
    regime      = property(lambda self: self.load()._regime,
                               doc = u"""
                                      Режим.
                                      :rtype : CTempInvalidRegimeInfo
                                  """)
    break_      = property(lambda self: self.load()._break,
                               doc = u"""
                                      Нарушение. Данные подгружаются из таблицы rbTempInvalidBreak
                                      :rtype : CTempInvalidBreakInfo
                                  """)
    breakDate   = property(lambda self: self.load()._breakDate,
                               doc = u"""
                                      Дата нарушения.
                                      :rtype : CDateInfo
                                  """)
    note   = property(lambda self: self.load()._note,
                               doc = u"""
                                      Примечание.
                                      :rtype : string
                                  """)
    result      = property(lambda self: self.load()._result,
                               doc = u"""
                                      Результат периода.
                                      :rtype : CTempInvalidResultInfo
                                  """)
#    MKB         = property(lambda self: self.load()._MKB)
#    MKBEx       = property(lambda self: self.load()._MKBEx)
    directDateOnKAK= property(lambda self: self.load()._directDateOnKAK,
                               doc = u"""
                                      Дата назначения КЭК.
                                      :rtype : CDateInfo
                                  """)
    expert      = property(lambda self: self.load()._expert,
                               doc = u"""
                                      Эксперт.
                                      :rtype : CPersonInfo
                                  """)
    dateKAK     = property(lambda self: self.load()._dateKAK,
                               doc = u"""
                                      Дата прохождения КЭК.
                                      :rtype : CDateInfo
                                  """)
    begDateHospital = property(lambda  self: self.load()._begDateHospital,
                               doc = u"""
                                      Дата поступления в стационар.
                                      :rtype : CDateInfo
                                  """)
    endDateHospital = property(lambda  self: self.load()._endDateHospital,
                               doc = u"""
                                      Дата выписки из стационара.
                                      :rtype : CDateInfo
                                  """)


class CTempInvalidPeriodInfoList(CInfoList):
    def __init__(self, context, tempInvalidId):
        CInfoList.__init__(self, context)
        self.tempInvalidId = tempInvalidId


    def addItem(self, id, record=None):
        item = self.getInstance(CTempInvalidPeriodInfo, id)
        if record:
            item.initByRecord(record)
            item.setOkLoaded()
        self._items.append(item)


    def _load(self):
        db = QtGui.qApp.db
        table = db.table('TempInvalid_Period')
        stmt = db.selectStmt(table, fields='id', where=table['master_id'].eq(self.tempInvalidId), order='begDate, id')
        result = db.query(stmt)
        while result.next():
            record = result.record()
            id = forceRef(record.value('id'))
            self.addItem(id)
        return True


class CTempInvalidInfo(CInfo):
    def __init__(self, context, id):
        CInfo.__init__(self, context)
        self.id = id
        self._type    = None
        self._doctype = context.getInstance(CTempInvalidDocTypeInfo, None)
        self._reason  = context.getInstance(CTempInvalidReasonInfo, None)
        self._extraReason = context.getInstance(CTempInvalidExtraReasonInfo, None)
        self._busyness = 0
        self._placeWork = ''
        self._serial  = ''
        self._number  = ''
        self._sex     = ''
        self._age     = ''
        self._duration = 0
        self._externalDuration = 0
        self._begDate = CDateInfo()
        self._endDate = CDateInfo()
        self._person = context.getInstance(CPersonInfo, None)
        self._closed = 0
        self._prev  = None
        self._MKB   = self.getInstance(CMKBInfo, '')
        self._MKBEx = self.getInstance(CMKBInfo, '')
        self._periods = []
        self._employmentService = False;


    def _load(self):
        if self.id:
            db = QtGui.qApp.db
            table = db.table('TempInvalid')
            tableDiagnosis = db.table('Diagnosis')
            tableEx = table.leftJoin(tableDiagnosis, tableDiagnosis['id'].eq(table['diagnosis_id']))
            record = db.getRecordEx(tableEx, 'TempInvalid.*, Diagnosis.MKB, Diagnosis.MKBEx', table['id'].eq(self.id))
            if record:
                self.initByRecord(record)
                return True
        return False


    def initByRecord(self, record):
        self._type    = forceInt(record.value('type'))
        self._doctype = self.getInstance(CTempInvalidDocTypeInfo, forceRef(record.value('doctype_id')))
        self._reason  = self.getInstance(CTempInvalidReasonInfo,  forceRef(record.value('tempInvalidReason_id')))
        self._extraReason  = self.getInstance(CTempInvalidExtraReasonInfo, forceRef(record.value('tempInvalidExtraReason_id')))
        self._busyness = forceInt(record.value('busyness'))
        self._placeWork = forceString(record.value('placeWork'))
        self._serial  = forceString(record.value('serial'))
        self._number  = forceString(record.value('number'))
        self._sex     = formatSex(forceInt(record.value('sex')))
        self._age     = forceInt(record.value('age'))
        self._employmentService = forceBool(record.value('employmentService'))
        self._duration= forceInt(record.value('duration'))
        self._externalDuration = 0
        self._begDate = CDateInfo(forceDate(record.value('begDate')))
        self._endDate = CDateInfo(forceDate(record.value('endDate')))
        self._person = self.getInstance(CPersonInfo, forceRef(record.value('person_id')))
        self._closed  = forceInt(record.value('closed'))
        self._MKB = self.getInstance(CMKBInfo, forceString(record.value('MKB')))
        self._MKBEx = self.getInstance(CMKBInfo, forceString(record.value('MKBEx')))
        prev_id = forceRef(record.value('prev_id'))
        if prev_id:
            self._prev = self.getInstance(CTempInvalidInfo, prev_id)
        self._periods = self.getInstance(CTempInvalidPeriodInfoList, self.id)


    type        = property(lambda self: self.load()._type)
    doctype     = property(lambda self: self.load()._doctype,
                               doc = u"""
                                      Тип документа нетрудоспособности.
                                      :rtype : CTempInvalidDocTypeInfo
                                  """)
    reason      = property(lambda self: self.load()._reason,
                               doc = u"""
                                      Причина нетрудоспособности.
                                      :rtype : CTempInvalidReasonInfo
                                  """)
    extraReason = property(lambda self: self.load()._extraReason,
                               doc = u"""
                                      Дополнительная причина нетрудоспособности.
                                      :rtype : CTempInvalidExtraReasonInfo
                                  """)
    busyness    = property(lambda self: self.load()._busyness,
                               doc = u"""
                                      Тип занятости (тут лежит id типа).
                                      :rtype : int
                                  """)
    placeWork   = property(lambda self: self.load()._placeWork,
                               doc = u"""
                                      Место работы.
                                      :rtype : string
                                  """)
    serial      = property(lambda self: self.load()._serial,
                               doc = u"""
                                      Серия документа ВУТ.
                                      :rtype : string
                                  """)
    number      = property(lambda self: self.load()._number,
                               doc = u"""
                                      Номер документа ВУТ.
                                      :rtype : string
                                  """)
    sex         = property(lambda self: self.load()._sex,
                               doc = u"""
                                      Пол.
                                      :rtype : string
                                  """)
    age         = property(lambda self: self.load()._age,
                               doc = u"""
                                      Возраст.
                                      :rtype : int
                                  """)
    employmentService = property(lambda self: self.load()._employmentService,
                               doc = u"""
                                      Состоит ли на учёте в государственных учереждениях службы занятости.
                                      :rtype : bool
                                  """)
    duration    = property(lambda self: self.load()._duration,
                               doc = u"""
                                      Длительность.
                                      :rtype : int
                                  """)
    externalDuration = property(lambda self: self.load()._externalDuration,
                               doc = u"""
                                      Длительность вне ЛПУ.
                                      :rtype : int
                                  """)
    begDate     = property(lambda self: self.load()._begDate,
                               doc = u"""
                                      Дата начала.
                                      :rtype : CDateInfo
                                  """)
    endDate     = property(lambda self: self.load()._endDate,
                               doc = u"""
                                      Дата окончания.
                                      :rtype : CDateInfo
                                  """)
    person      = property(lambda self: self.load()._person,
                               doc = u"""
                                      Врач последнего периода.
                                      :rtype : CPersonInfo
                                  """)
    MKB         = property(lambda self: self.load()._MKB,
                               doc = u"""
                                      Диагноз.
                                      :rtype : CMKBInfo
                                  """)
    MKBEx       = property(lambda self: self.load()._MKBEx,
                               doc = u"""
                                      Характер.
                                      :rtype : CMKBInfo
                                  """)
    periods     = property(lambda self: self.load()._periods,
                               doc = u"""
                                      Период листка временной нетрудоспособности
                                      :rtype : CTempInvalidPeriodInfoList
                                  """)
    closed      = property(lambda self: self.load()._closed,
                               doc = u"""
                                      0-Открыт, 1-Закрыт, 2-Продлён, 3-Передан.
                                      :rtype : CTempInvalidPeriodInfoList
                                  """)
    prev        = property(lambda self: self.load()._prev,
                               doc = u"""
                                      Предыдущий документ.
                                      :rtype : CTempInvalidInfo
                                  """)


class CTempInvalidDocTypeInfo(CRBInfo):
    tableName = 'rbTempInvalidDocument'


class CTempInvalidReasonInfo(CRBInfo):
    tableName = 'rbTempInvalidReason'

    def _initByRecord(self, record):
        self._grouping = forceInt(record.value('grouping'))


    def _initByNull(self):
        self._grouping = None

    grouping = property(lambda self: self.load()._grouping)


class CTempInvalidExtraReasonInfo(CRBInfo):
    tableName = 'rbTempInvalidExtraReason'



class CTempInvalidInfoList(CInfoList):
    def __init__(self, context, clientId, begDate, endDate, types=(0, )):
        CInfoList.__init__(self, context)
        self.clientId = clientId
        self.begDate  = QtCore.QDate(begDate) if begDate else None
        self.endDate  = QtCore.QDate(endDate) if endDate else None
        self.types    = types
        self._idList = []


    def _load(self):
        db = QtGui.qApp.db
        table = db.table('TempInvalid')
        cond = [ table['client_id'].eq(self.clientId),
                 table['deleted'].eq(0),
                 table['type'].inlist(self.types)]
        if self.begDate:
            cond.append(table['endDate'].ge(self.begDate))
        if self.endDate:
            cond.append(table['begDate'].le(self.endDate))
        self._idList = db.getIdList(table, 'id', cond, 'begDate')
        self._items = [ self.getInstance(CTempInvalidInfo, id) for id in self._idList ]
        return True


    @staticmethod
    def _get(context, clientId, begDate, endDate, types=None):
        if isinstance(endDate, CDateInfo):
            endDate = endDate.date
        if isinstance(begDate, CDateInfo):
            begDate = begDate.date
        if isinstance(types, (set, frozenset, list, tuple)):
            types = tuple(types)
        elif isinstance(types, (int, long, basestring)):
            types = (types, )
        elif types is None:
            types = (0, )
        else:
            raise ValueError('parameter "types" must be list, tuple, set or int')
        # потребность в pyDate обусловлена использованием дат в ключе кеша объектов.
        return context.getInstance(CTempInvalidInfoList, clientId, pyDate(begDate), pyDate(endDate), types)
        
        
        
class CTempInvalidDuplicateReasonInfo(CRBInfo):
    tableName = 'rbTempInvalidDuplicateReason'        

class CTempInvalidDuplicateInfo(CTempInvalidInfo):
    def __init__(self, context, tempInvalid_id, id):
        CTempInvalidInfo.__init__(self, context, tempInvalid_id)
        self.duplicate_id = id
        self._person = context.getInstance(CPersonInfo, None)
        self._date = CDateInfo()
        self._duplicateSerial = ''
        self._duplicateNumber = ''
        self._destination = ''
        self._duplicateReason = context.getInstance(CTempInvalidDuplicateReasonInfo, None)
        self._insuranceOfficeMark = -1
        self._duplicatePlaceWork = ''
        self._note = ''

    def _load(self):
        if CTempInvalidInfo._load(self) and self.duplicate_id:
            db = QtGui.qApp.db
            table = db.table('TempInvalidDuplicate')
            record = db.getRecordEx(table, '*', table['id'].eq(self.duplicate_id))
            if record:
                self.initDuplicateByRecord(record)
                return True
        return False


    def initDuplicateByRecord(self, record):
        self._person = self.getInstance(CPersonInfo, forceRef(record.value('person_id')))
        self._date = CDateInfo(forceDate(record.value('date')))
        self._duplicateSerial = forceString(record.value('serial'))
        self._duplicateNumber = forceString(record.value('number'))
        self._destination = forceString(record.value('destination'))
        self._duplicateReason = self.getInstance(CTempInvalidDuplicateReasonInfo, forceRef(record.value('reason_id')))
        self._insuranceOfficeMark = forceInt(record.value('insuranceOfficeMark'))
        self._duplicatePlaceWork = forceString(record.value('placeWork'))
        self._note = forceString(record.value('note'))      


    person      = property(lambda self: self.load()._person)
    date        = property(lambda self: self.load()._date)
    duplicateSerial  = property(lambda self: self.load()._duplicateSerial)
    duplicateNumber  = property(lambda self: self.load()._duplicateNumber)
    destination = property(lambda self: self.load()._destination)
    duplicateReason      = property(lambda self: self.load()._duplicateReason)
    insuranceOfficeMark  = property(lambda self: self.load()._insuranceOfficeMark)
    duplicatePlaceWork   = property(lambda self: self.load()._duplicatePlaceWork)
