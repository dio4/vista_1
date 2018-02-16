# -*- coding: utf-8 -*-

from PyQt4 import QtGui

from Accounting.Utils import CTariff, isTariffApplicable
from Events.Action import CActionTypeCache
from Events.ActionInfo import CActionInfoList
from Events.ContractTariffCache import CContractTariffCache
from Events.MKBInfo import CMKBInfo
from Events.Service import CMedicalAidKindInfo, CMedicalAidTypeInfo, CServiceInfo
from Events.TempInvalidInfo import CTempInvalidInfoList
from Events.Utils import EventIsPrimary, getEventShowTime, recordAcceptable
from Orgs.PersonInfo import CPersonInfo, CSpecialityInfo
from Orgs.Utils import COrgInfo
from Registry.Utils import CClientDocumentInfo, CClientInfo, CClientPolicyInfo, CQuotaTypeInfo
from library.PrintInfo import CDateInfo, CDateTimeInfo, CInfo, CInfoList, CInfoProxyList, CRBInfo, CTemplatableInfoMixin
from library.TNMS.Utils import convertTNMSStringToDict
from library.Utils import forceBool, forceDate, forceDouble, forceInt, forceRef, forceString, forceStringEx, formatSex


class CPurposeInfo(CRBInfo):
    tableName = 'rbEventTypePurpose'
    def __init__(self, context, id):
        CRBInfo.__init__(self, context, id)


class CFinanceInfo(CRBInfo):
    tableName = 'rbFinance'
    def __init__(self, context, id):
        CRBInfo.__init__(self, context, id)


class CEventTypeInfo(CRBInfo):
    tableName = 'EventType'

    def __init__(self, context, id):
        CRBInfo.__init__(self, context, id)

    def _initByRecord(self, record):
        self._purpose = self.getInstance(CPurposeInfo, forceRef(record.value('purpose_id')))
        self._finance = self.getInstance(CFinanceInfo, forceRef(record.value('finance_id')))
        self._service = self.getInstance(CServiceInfo, forceRef(record.value('service_id')))
        self._medicalAidType = self.getInstance(CMedicalAidTypeInfo, forceRef(record.value('medicalAidType_id')))
        self._medicalAidKind = self.getInstance(CMedicalAidKindInfo, forceRef(record.value('medicalAidKind_id')))
        self._printContext = forceString(record.value('context'))

    def _initByNull(self):
        self._purpose = self.getInstance(CPurposeInfo, None)
        self._finance = self.getInstance(CFinanceInfo, None)
        self._service = self.getInstance(CServiceInfo, None)
        self._medicalAidType = self.getInstance(CMedicalAidTypeInfo, None)
        self._medicalAidKind = self.getInstance(CMedicalAidKindInfo, None)
        self._printContext = ''

    purpose = property(lambda self: self.load()._purpose)
    finance = property(lambda self: self.load()._finance)
    service = property(lambda self: self.load()._service)
    medicalAidType = property(lambda self: self.load()._medicalAidType)
    medicalAidKind = property(lambda self: self.load()._medicalAidKind)
    printContext = property(lambda self: self.load()._printContext)


class CResultInfo(CRBInfo):
    tableName = 'rbResult'
    def __init__(self, context, id):
        CRBInfo.__init__(self, context, id)

    def _initByRecord(self, record):
        self._continued = forceBool(record.value('continued'))
        self._regionalCode = forceString(record.value('regionalCode'))
        self._federalCode = forceString(record.value('federalCode'))

    def _initByNull(self):
        self._continued = False
        self._regionalCode = self._federalCode = ''

    continued = property(lambda self: self.load()._continued)
    regionalCode = property(lambda self: self.load()._regionalCode)
    federalCode = property(lambda self: self.load()._federalCode)


class CReferralInfo(CRBInfo):
    tableName = 'Referral'
    def __init__(self, context, id):
        CRBInfo.__init__(self, context, id)

    def _initByRecord(self, record):
        self._type = forceRef(record.value('type'))
        self._clinicType = forceRef(record.value('clinicType'))
        self._number = forceString(record.value('number'))
        self._date = CDateInfo(forceDate(record.value('date')))
        self._planningDate = CDateInfo(forceDate(record.value('date')))
        relegateOrg_id = forceRef(record.value('relegateOrg_id'))
        self._MKB = forceString(record.value('MKB'))
        self._relegateOrgInfis = forceString(QtGui.qApp.db.translate('Organisation', 'id', relegateOrg_id, 'infisCode'))
        self._netricaId = forceString(record.value('netrica_id'))
        self._person = forceString(record.value('person'))
        self._notes = forceString(record.value('notes'))
        self._hospitalBedProfile = self.getInstance(
            CHospitalBedProfileInfo,
            forceRef(record.value('hospBedProfile_id'))
        )
        self._orgStructureProfile = self.getInstance(
            COrgStructureProfileInfo,
            forceRef(record.value('orgStructure'))
        )
        self._ticketNumber = forceString(record.value('ticketNumber'))

    def _initByNull(self):
        self._type = None
        self._clinicType = None
        self._MKB = u''
        self._number = u''
        self._date = CDateInfo()
        self._planningDate = CDateInfo()
        self._relegateOrgInfis = u''
        self._netricaId = u''
        self._person = u''
        self._notes = u''
        self._hospitalBedProfile = self.getInstance(CHospitalBedProfileInfo, None)
        self._orgStructureProfile = self.getInstance(COrgStructureProfileInfo, None)
        self._ticketNumber = u''

    type = property(lambda self: self.load()._type,
        doc=u'''
            Тип направления.
            :rtype : int
    ''')
    clinicType = property(lambda self: self.load()._clinicType,
        doc=u'''
            Тип стационара.
            :rtype : int
    ''')
    MKB = property(lambda self: self.load()._MKB,
        doc=u'''
            Код МКБ.
            :rtype : unicode
    ''')
    number = property(lambda self: self.load()._number,
        doc=u'''
            Номер направления.
            :rtype : unicode
    ''')
    date = property(lambda self: self.load()._date,
        doc=u'''
            Дата направления.
            :rtype : CDateInfo
    ''')
    planningDate = property(lambda self: self.load()._planningDate,
        doc=u'''
            Плановая дата консультации или госпитализации.
            :rtype : CDateInfo
    ''')
    relegateOrgInfis = property(lambda self: self.load()._relegateOrgInfis,
        doc=u'''
            Инфис код направителя.
            :rtype : unicode
    ''')
    netricaId = property(lambda self: self.load()._netricaId,
        doc = u'''
            Идентификатор направления в справочнике Нетрики.
            :rtype : unicode
    ''')
    person = property(lambda self: self.load()._person,
        doc=u'''
            Имя и специальность направившего врача.
            :rtype : unicode
    ''')
    notes = property(lambda self: self.load()._notes,
        doc=u'''
            Примечание.
            :rtype : unicode
    ''')
    hospitalBedProfile = property(lambda self: self.load()._hospitalBedProfile,
        doc=u'''
            Профиль койки.
            :rtype : CHospitalBedProfileInfo
    ''')
    orgStructureProfile = property(lambda self: self.load()._orgStructureProfile,
        doc=u'''
            Профиль подразделения.
            :rtype : COrgStructureProfileInfo
    ''')

    ticketNumber = property(lambda self: self.load()._ticketNumber,
        doc=u'''
            Предварительная запись
            :rtype : unicode
        ''')


class CEventHospTransferInfo(CInfo):
    tableName = '`logger`.`EventHospTransfer`'
    def __init__(self, context, eventId):
        CInfo.__init__(self, context)
        self.eventId = eventId

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecordEx(
            self.tableName, '*', where='event_id = %s' % self.eventId, order='id DESC'
        ) if self.eventId else None
        if record:
            self._dateFrom = CDateInfo(forceDate(record.value('dateFrom')))
            self._dateTo = CDateInfo(forceDate(record.value('dateTo')))
            self._person = self.getInstance(CPersonInfo, forceRef(record.value('person_id')))
            self._comment = forceString(record.value('comment'))
            self._diagnosis = forceString(record.value('diagnosis'))
            self._treatmentMethod = forceString(record.value('treatmentMethod'))
            self._recommendedTreatment = forceString(record.value('recommendedTreatment'))
            self._treatmentOrgStructure = forceString(record.value('treatmentOrgStructure'))

            return True
        else:
            self._dateFrom = CDateInfo()
            self._dateTo = CDateInfo()
            self._person = self.getInstance(CPersonInfo, None)
            self._comment = ''
            self._diagnosis = ''
            self._treatmentMethod = ''
            self._recommendedTreatment = ''
            self._treatmentOrgStructure = ''

            return False

    dateFrom = property(lambda self: self.load()._dateFrom,
                    doc=u'''
                        Дата с которой осуществлют перенос госпитализации.
                        :rtype : CDateInfo
                    ''')

    dateTo = property(lambda self: self.load()._dateTo,
                    doc=u'''
                        Дата с которую совершают перенос госпитализации.
                        :rtype : CDateInfo
                    ''')

    person = property(lambda self: self.load()._person,
                   doc=u'''
                        Пользователь, совершивший перенос.
                        :rtype : CPersonInfo
                    ''')

    comment = property(lambda self: self.load()._comment,
                   doc=u'''
                        Причина переноса.
                        :rtype : unicode
                    ''')

    diagnosis = property(lambda self: self.load()._diagnosis,
                   doc=u'''
                        Диагноз.
                        :rtype : unicode
                    ''')

    treatmentMethod = property(lambda self: self.load()._treatmentMethod,
                   doc=u'''
                        Метод лечения.
                        :rtype : unicode
                    ''')

    recommendedTreatment = property(lambda self: self.load()._recommendedTreatment,
                   doc=u'''
                        Рекомендуемое лечение.
                        :rtype : unicode
                    ''')

    treatmentOrgStructure = property(lambda self: self.load()._treatmentOrgStructure,
                   doc=u'''
                        Лечебное отделение.
                        :rtype : unicode
                    ''')


class CPoliclinicReferralInfo(CInfo):
    def __init__(self, context, id):
        CInfo.__init__(self, context)
        self.id = id
        self.tableName = 'Referral'

    def _load(self):
        record = QtGui.qApp.db.getRecordEx(self.tableName, '*', 'client_id = %s AND isSend = 1 ORDER BY id DESC' % self.id) if self.id else None
        if record:
            self._number = forceString(record.value('number'))
            self._date = CDateInfo(forceDate(record.value('date')))
            insurerOrg_id = forceRef(record.value('relegateOrg_id'))
            self._MKB = forceString(record.value('MKB'))
            self._insurerOrg_name = forceString(QtGui.qApp.db.translate('Organisation', 'id', insurerOrg_id, 'fullName'))
            self._netricaId = forceString(record.value('netrica_id'))
            self._person = forceString(record.value('person'))
            self._notes = forceString(record.value('notes'))
            self._ticketNumber = forceString(record.value('ticketNumber'))
            return True
        else:
            self._number = ''
            self._date = ''
            self._MKB = ''
            self._insurerOrg_name = ''
            self._netricaId = ''
            self._person = ''
            self._notes = ''
            return False

    def __str__(self):
        return self.load()._number

    number = property(lambda self: self.load()._number,
                          doc=u'''
                        Номер направления.
                        :rtype : unicode
                    ''')

    date = property(lambda self: self.load()._date,
               doc=u'''
                        Дата направления.
                        :rtype : CDateInfo
                    ''')
    mkb = property(lambda self: self.load()._MKB,
                               doc=u'''
                        Код МКБ.
                        :rtype : unicode
                    ''')
    insurerOrg_name = property(lambda self: self.load()._insurerOrg_name,
                              doc=u'''
                        Куда направлен пациент.
                        :rtype : unicode
                    ''')
    netricaId = property(lambda self: self.load()._netricaId,
                               doc=u'''
        Идентификатор УО.
        :rtype : unicode
    ''')

    person = property(lambda  self: self.load()._person,
                            doc=u'''
                            Врач
                            :rtype : unicode
                            ''')
    notes = property(lambda self: self.load()._notes,
                            doc=u'''
                            Примечание
                            :rtype : unicode
                            ''')

    ticketNumber = property(lambda self: self.load._ticketNumber,
                            doc=u'''
                            Доп информация
                            :rtype : unicode
                            ''')


class COrgStructureProfileInfo(CRBInfo):
    tableName = 'rbOrgStructureProfile'


class CHospitalBedProfileInfo(CRBInfo):
    tableName = 'rbHospitalBedProfile'


class COutgoingReferralInfo(CInfo):
    """
        Информация о исходящем направлении (доступно из CEventInfo, связано с обращением).
    """
    def __init__(self, context, id):
        CInfo.__init__(self, context)
        self.id = id
        self.tableName = 'Event_OutgoingReferral'

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord(self.tableName, '*', self.id) if self.id else None
        if record:
            self._number = forceString(record.value('number'))
            self._org = self.getInstance(COrgInfo, forceString(record.value('org_id')))
            self._orgStructureProfile = self.getInstance(COrgStructureProfileInfo, forceRef(record.value('orgStructureProfile_id')))
            self._hospitalBedProfile = self.getInstance(CHospitalBedProfileInfo, forceRef(record.value('hospitalBedProfile_id')))
            return True
        else:
            self._number = ''
            self._org = self.getInstance(COrgInfo, None)
            self._orgStructureProfile = self.getInstance(COrgStructureProfileInfo, None)
            self._hospitalBedProfile  = self.getInstance(CHospitalBedProfileInfo, None)
            return False

    def __str__(self):
        return self.load()._number

    number = property(lambda self: self.load()._number,
                    doc=u'''
                        Номер исходящего направления.
                        :rtype : unicode
                    ''')
    org = property(lambda self: self.load()._org,
                   doc=u'''
                        Организация, в которую направлен пациент.
                        :rtype : COrgInfo
                    ''')
    orgStructureProfile = property(lambda self: self.load()._orgStructureProfile,
                    doc=u'''
                        Профиль подразделения.
                        :rtype : COrgStructureProfileInfo
                    ''')
    hospitalBedProfile = property(lambda self: self.load()._orgStructureProfile,
                    doc=u'''
                        Профиль койки.
                        :rtype : CHospitalBedProfileInfo
                    ''')


class CDiagnosticResultInfo(CResultInfo):
    tableName = 'rbDiagnosticResult'


class CContractInfo(CInfo):
    def __init__(self, context, id):
        CInfo.__init__(self, context)
        self.id = id

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('Contract', '*', self.id)
        if record:
            self._number = forceString(record.value('number'))
            self._date = CDateInfo(forceDate(record.value('date')))
            self._begDate = CDateInfo(forceDate(record.value('begDate')))
            self._endDate = CDateInfo(forceDate(record.value('endDate')))
            self._recipient = self.getInstance(COrgInfo, forceRef(record.value('recipient_id')))
            self._recipientAccount = self.getInstance(COrgAccountInfo, forceRef(record.value('recipientAccount_id')))
            self._recipientKBK = forceString(record.value('recipientKBK'))
            self._payer = self.getInstance(COrgInfo, forceRef(record.value('payer_id')))
            self._payerAccount = self.getInstance(COrgAccountInfo, forceRef(record.value('payerAccount_id')))
            self._payerKBK = forceString(record.value('payerKBK'))
            self._finance = self.getInstance(CFinanceInfo, forceRef(record.value('finance_id')))
            self._deposit = forceDouble(record.value('deposit'))
            self._maxClients = forceInt(record.value('maxClients'))
            self._counterValue = forceString(record.value('counterValue'))
            self._tariffs = self.getInstance(CTariffItemInfoList, self.id)
            self._grouping = forceString(record.value('grouping'))
            self._resolution = forceString(record.value('resolution'))
            self._ignorePayStatusForJobs = forceBool(record.value('ignorePayStatusForJobs'))
            return True
        else:
            self._number = ''
            self._date = CDateInfo()
            self._begDate = CDateInfo()
            self._endDate = CDateInfo()
            self._recipient = self.getInstance(COrgInfo, None)
            self._recipientAccount = self.getInstance(COrgAccountInfo, None)
            self._recipientKBK = ''
            self._payer = self.getInstance(COrgInfo, None)
            self._payerAccount = self.getInstance(COrgAccountInfo, None)
            self._payerKBK = ''
            self._finance = self.getInstance(CFinanceInfo, None)
            self._deposit = 0.0
            self._maxClients = 0
            self._counterValue = ''
            self._tariffs = self.getInstance(CTariffItemInfoList, None)
            self._grouping = ''
            self._resolution = ''
            self._ignorePayStatusForJobs = False
            return False

    def __str__(self):
        self.load()
        return self._number + ' ' + self._date

    begDate = property(lambda self: self.load()._begDate)
    counterValue = property(lambda self: self.load()._counterValue)
    date = property(lambda self: self.load()._date)
    deposit = property(lambda self: self.load()._deposit)
    endDate = property(lambda self: self.load()._endDate)
    finance = property(lambda self: self.load()._finance)
    grouping = property(lambda self: self.load()._grouping)
    ignorePayStatusForJobs = property(lambda self: self.load()._ignorePayStatusForJobs)
    maxClients = property(lambda self: self.load()._maxClients)
    number = property(lambda self: self.load()._number)
    payer = property(lambda self: self.load()._payer)
    payerAccount = property(lambda self: self.load()._payerAccount)
    payerKBK = property(lambda self: self.load()._payerKBK)
    recipient = property(lambda self: self.load()._recipient)
    recipientAccount = property(lambda self: self.load()._recipientAccount)
    recipientKBK = property(lambda self: self.load()._recipientKBK)
    resolution = property(lambda self: self.load()._resolution)
    tariffs = property(lambda self: self.load()._tariffs)


class CTariffItemInfoList(CInfoList):
    def __init__(self, context, contractId):
        CInfoList.__init__(self, context)
        self.contractId = contractId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('Contract_Tariff')
        idList = db.getIdList(table, 'id', db.joinAnd([table['master_id'].eq(self.contractId), table['deleted'].eq(0)]), 'id DESC')
        self._items = [ self.getInstance(CTariffItemInfo, id) for id in idList ]
        return True


class CTariffItemInfo(CInfo):
    def __init__(self, context, id):
        CInfo.__init__(self, context)
        self.id = id
        self._record = None

    def record(self):
        return self._record

    def _load(self):
        db = QtGui.qApp.db
        self._record = db.getRecord('Contract_Tariff', '*', self.id)
        if self._record:
            result = True
        else:
            self._record = db.table('Contract_Tariff').newRecord()
            result = False
        from Orgs.PersonInfo import CTariffCategoryInfo, CSpecialityInfo
        from Accounting.AccountInfo import CRBMedicalAidUnitInfo

        self._eventType   = self.getInstance(CEventTypeInfo, forceRef(self._record.value('eventType_id')))
        self._tariffType  = forceInt(self._record.value('tariffType'))
        self._service     = self.getInstance(CServiceInfo, forceRef(self._record.value('service_id')))
        self._tariffCategory = self.getInstance(CTariffCategoryInfo, forceRef(self._record.value('tariffCategory_id')))
        self._begDate     = CDateInfo(forceDate(self._record.value('begDate')))
        self._endDate     = CDateInfo(forceDate(self._record.value('endDate')))
        self._sexCode     = forceInt(self._record.value('sex'))
        self._sex         = formatSex(self._sexCode)
        self._age         = forceString(self._record.value('age'))
        self._attachLPU   = self.getInstance(COrgInfo, forceRef(self._record.value('attachLPU_id')))
        self._unit        = self.getInstance(CRBMedicalAidUnitInfo, forceRef(self._record.value('unit_id')))
        self._amount      = forceDouble(self._record.value('amount'))
        self._uet         = forceDouble(self._record.value('uet'))
        self._price       = forceDouble(self._record.value('price'))
        self._MKB         = forceString(self._record.value('MKB'))
        self._speciality  = self.getInstance(CSpecialityInfo, forceRef(self._record.value('speciality_id')))
        return result

    eventType = property(lambda self: self.load()._eventType)
    tariffType = property(lambda self: self.load()._tariffType)
    service = property(lambda self: self.load()._service)
    tariffCategory = property(lambda self: self.load()._tariffCategory)
    begDate = property(lambda self: self.load()._begDate)
    endDate = property(lambda self: self.load()._endDate)
    sexCode = property(lambda self: self.load()._sexCode)
    sex = property(lambda self: self.load()._sex)
    age = property(lambda self: self.load()._age)
    attachLPU = property(lambda self: self.load()._attachLPU)
    unit = property(lambda self: self.load()._unit)
    amount = property(lambda self: self.load()._amount)
    uet = property(lambda self: self.load()._uet)
    price = property(lambda self: self.load()._price)
    MKB = property(lambda self: self.load()._MKB)
    speciality = property(lambda self: self.load()._speciality)


class COrgAccountInfo(CInfo):
    def __init__(self, context, id):
        CInfo.__init__(self, context)
        self.id = id

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('Organisation_Account', '*', self.id)
        if record:
            self._org = self.getInstance(COrgInfo, forceRef(record.value('organisation_id')))
            self._bankName = forceString(record.value('bankName'))
            self._name = forceString(record.value('name'))
            self._notes = forceString(record.value('notes'))
            self._bank = self.getInstance(CBankInfo, forceRef(record.value('bank_id')))
            self._cash = forceBool(record.value('cash'))
            return True
        else:
            self._org = self.getInstance(COrgInfo, None)
            self._bankName = ''
            self._name = ''
            self._notes = ''
            self._bank = self.getInstance(CBankInfo, None)
            self._cash = False
            return False

    def __str__(self):
        self.load()
        return self._name

    organisation = property(lambda self: self.load()._org)
    org          = property(lambda self: self.load()._org)
    bankName     = property(lambda self: self.load()._bankName)
    name         = property(lambda self: self.load()._name)
    notes        = property(lambda self: self.load()._notes)
    bank         = property(lambda self: self.load()._bank)
    cash         = property(lambda self: self.load()._cash)


class CBankInfo(CInfo):
    def __init__(self, context, id):
        CInfo.__init__(self, context)
        self.id = id

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('Bank', '*', self.id)
        if record:
            self._BIK = forceString(record.value('BIK'))
            self._name = forceString(record.value('name'))
            self._branchName = forceString(record.value('branchName'))
            self._corrAccount = forceString(record.value('corrAccount'))
            self._subAccount = forceString(record.value('subAccount'))
            return True
        else:
            self._BIK = ''
            self._name = ''
            self._branchName = ''
            self._corrAccount = ''
            self._subAccount = ''
            return False

    def __str__(self):
        self.load()
        return self._name

    BIK        = property(lambda self: self.load()._BIK)
    name       = property(lambda self: self.load()._name)
    branchName = property(lambda self: self.load()._branchName)
    corrAccount= property(lambda self: self.load()._corrAccount)
    subAccount = property(lambda self: self.load()._subAccount)


class CMesSpecificationInfo(CRBInfo):
    tableName = 'rbMesSpecification'
    def __init__(self, context, id):
        CRBInfo.__init__(self, context, id)

    def _initByRecord(self, record):
        self._done = forceBool(record.value('done'))
        self._regionalCode = forceString(record.value('regionalCode'))

    def _initByNull(self):
        self._done = False
        self._regionalCode = ''

    done = property(lambda self: self.load()._done)
    regionalCode = property(lambda self: self.load()._done)


class CMesServiceInfoList(CInfoList):
    def __init__(self, context, mesId):
        CInfoList.__init__(self, context)
        self.mesId = mesId

    def _load(self):
        db = QtGui.qApp.db
        tblMesService = db.table('mes.MES_service')
        tblMRBservice = db.table('mes.mrbService')
        tblRBService = db.table('rbService')

        queryTable = tblMesService.innerJoin(tblMRBservice, tblMRBservice['id'].eq(tblMesService['service_id']))
        queryTable = queryTable.innerJoin(tblRBService, tblRBService['code'].eq(tblMRBservice['code']))

        cond = [tblMesService['master_id'].eq(self.mesId),
                tblMesService['deleted'].eq(0),
                tblMRBservice['deleted'].eq(0)]
        idList = db.getIdList(queryTable, tblRBService['id'], cond, 'id')

        self._items = [ self.getInstance(CServiceInfo, id) for id in idList ]
        return True


class CMesInfo(CInfo):
    def __init__(self, context, itemId, eventId = None):
        CInfo.__init__(self, context)
        self.id = itemId
        self._eventId = eventId
        self._tariffInfo = None
        self._serviceId = None

        self._deleted = True
        self._code = ''
        self._name = ''
        self._descr = ''
        self._minDuration = 0
        self._maxDuration = 0
        self._avgDuration =  0
        self._KSGNorm = 0
        self._isUltraShort = 0
        self._isExtraLong = 0
        self._services = self.getInstance(CMesServiceInfoList, None)

    def setRecord(self, record):
        self._deleted = forceBool(record.value('deleted')) if record else True
        self._code = forceString(record.value('code')) if record else ''
        self._name = forceString(record.value('name')) if record else ''
        self._descr = forceString(record.value('descr')) if record else ''
        self._minDuration = forceInt(record.value('minDuration')) if record else 0 
        self._maxDuration = forceInt(record.value('maxDuration')) if record else 0
        self._avgDuration = forceInt(record.value('avgDuration')) if record else 0
        self._KSGNorm = forceDouble(record.value('KSGNorm')) if record else 0
        self._services = self.getInstance(CMesServiceInfoList, self.id) if record else self.getInstance(CMesServiceInfoList, None)

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('mes.MES', '*', self.id)
        self.setRecord(record)
        return bool(record)

    def _getTariffInfo(self):
        if not self._eventId:
            return None

        if self._serviceId is None:
            code = QtGui.qApp.db.translate('mes.MES', 'id', self.id, 'code')
            self._serviceId = forceRef(QtGui.qApp.db.translate('rbService', 'code', code, 'id'))
        if self._tariffInfo is None:
            eventInfo = self.getInstance(CEventInfo, self._eventId)
            #FIXME: Возможно, стоит добавить проверку хотя бы даты
            for tariffInfo in eventInfo.contract.tariffs:
                if not tariffInfo.service.id == self._serviceId:
                    continue

                tariff = CTariff(tariffInfo._record)
                if isTariffApplicable(tariff,
                                      self._eventId,
                                      eventInfo.execPerson.tariffCategory.id,
                                      eventInfo.execDate.date):
                    self._tariffInfo = tariffInfo
                    break
        if self._tariffInfo is None:
            self._tariffInfo = CTariff(None)
        return self._tariffInfo

    deleted = property(lambda self: self.load()._deleted)
    code  = property(lambda self: self.load()._code)
    name  = property(lambda self: self.load()._name)
    descr = property(lambda self: self.load()._descr)
    minDuration = property(lambda self: self.load()._minDuration)
    maxDuration = property(lambda self: self.load()._maxDuration)
    avgDuration = property(lambda self: self.load()._avgDuration)
    tariff = property(lambda self: self.load()._getTariffInfo())
    KSGNorm = property(lambda self: self.load()._KSGNorm)
    services = property(lambda self: self.load()._services)


class CPatientModelInfo(CRBInfo):
    tableName = 'rbPatientModel'
    def __init__(self, context, id):
        CRBInfo.__init__(self, context, id)

    def _initByRecord(self, record):
        self._MKB = forceString(record.value('MKB'))
        self._quotaType = self.getInstance(CQuotaTypeInfo, forceRef(record.value('quotaType_id')))

    def _initByNull(self):
        self._MKB = ''
        self._quotaType = self.getInstance(CQuotaTypeInfo, None)

    MKB       = property(lambda self: self.load()._MKB)
    quotaType = property(lambda self: self.load()._quotaType)


class CCureTypeInfo(CRBInfo):
    tableName = 'rbCureType'
    def __init__(self, context, id):
        CRBInfo.__init__(self, context, id)

    def _initByRecord(self, record):
        self._regionalCode = forceString(record.value('regionalCode'))

    def _initByNull(self):
        self._regionalCode = ''

    regionalCode = property(lambda self: self.load()._regionalCode)


class CCureMethodInfo(CRBInfo):
    tableName = 'rbCureMethod'
    def __init__(self, context, id):
        CRBInfo.__init__(self, context, id)

    def _initByRecord(self, record):
        self._regionalCode = forceString(record.value('regionalCode'))

    def _initByNull(self):
        self._regionalCode = ''

    regionalCode = property(lambda self: self.load()._regionalCode)


class CEventCashPageInfo(CInfo):
    u"""
        Информация с вкладки Обращение->Оплата->Услуги:
        всего к оплате, оплачено, долг.
    """

    def __init__(self, context, eventId):
        CInfo.__init__(self, context)
        self.eventId = eventId

    def _load(self):
        db = QtGui.qApp.db
        tableEventPayment = db.table('Event_Payment')
        cond = [
            tableEventPayment['master_id'].eq(self.eventId),
            tableEventPayment['deleted'].eq(0)
        ]
        self._chequeList = [forceString(record.value('cheque'))
                            for record in db.iterRecordList(tableEventPayment, tableEventPayment['cheque'], cond)]
        return True

    accValue = property(lambda self: self.load()._accValue)
    payedValue = property(lambda self: self.load()._payedValue)
    totalValue = property(lambda self: self.load()._totalValue)
    chequeList = property(lambda  self: self.load()._chequeList)


class CEventGoalInfo(CRBInfo):
    tableName = 'rbEventGoal'


class CEventInfo(CInfo, CTemplatableInfoMixin):
    def __init__(self, context, id):
        CInfo.__init__(self, context)
        self.id = id
        self._localContract = None
        self._contractTariffCache = None

    def _load(self):
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        record = db.getRecord(tableEvent, '*', self.id)
        if record:
            self._eventType = self.getInstance(CEventTypeInfo, forceRef(record.value('eventType_id')))
            self._externalId = forceString(record.value('externalId'))
            self._org = self.getInstance(COrgInfo, forceRef(record.value('org_id')))
            self._relegateOrg = self.getInstance(COrgInfo, forceRef(record.value('relegateOrg_id')))
            self._client = self.getInstance(CClientInfo, forceRef(record.value('client_id')))
            self._contract = self.getInstance(CContractInfo, forceRef(record.value('contract_id')))
            self._prevEventDate = CDateInfo(forceDate(record.value('prevEventDate')))
            self._setDate = CDateInfo(forceDate(record.value('setDate')))
            self._setPerson = self.getInstance(CPersonInfo, forceRef(record.value('setPerson_id')))
            self._execDate = CDateInfo(forceDate(record.value('execDate')))
            self._execPerson = self.getInstance(CPersonInfo, forceRef(record.value('execPerson_id')))
            self._isPrimary = forceInt(record.value('isPrimary')) == EventIsPrimary.Primary
            self._order = forceInt(record.value('order'))
            self._result = self.getInstance(CResultInfo, forceRef(record.value('result_id')))
            self._nextEventDate = CDateInfo(forceDate(record.value('nextEventDate')))
            self._payStatus = forceInt(record.value('payStatus'))
            self._typeAsset = self.getInstance(CEmergencyTypeAssetInfo, forceRef(record.value('typeAsset_id')))
            self._note = forceString(record.value('note'))
            self._curator = self.getInstance(CPersonInfo, forceRef(record.value('curator_id')))
            self._assistant = self.getInstance(CPersonInfo, forceRef(record.value('assistant_id')))
            self._actions = self.getInstance(CActionInfoList, self.id)
            self._diagnosises = self.getInstance(CDiagnosticInfoList, self.id)
            self._visits = self.getInstance(CVisitInfoList, self.id)
            self._localContract = self.getInstance(CEventLocalContractInfo, self.id)
            self._mes = self.getInstance(CMesInfo, forceRef(record.value('MES_id')), self.id)
            self._mesSpecification = self.getInstance(CMesSpecificationInfo, forceRef(record.value('mesSpecification_id')))
            self._patientModel = self.getInstance(CPatientModelInfo, forceRef(record.value('patientModel_id')))
            self._quotaType = self.getInstance(CQuotaTypeInfo, None)
            self._cureType     = self.getInstance(CCureTypeInfo, forceRef(record.value('cureType_id')))
            self._cureMethod   = self.getInstance(CCureMethodInfo, forceRef(record.value('cureMethod_id')))
            self._referral     = self.getInstance(CReferralInfo, forceRef(record.value('referral_id')))
            self._policlinicReferral = self.getInstance(CPoliclinicReferralInfo, forceRef(record.value('client_id')))
            self._armyReferral     = self.getInstance(CReferralInfo, forceRef(record.value('armyReferral_id')))
            outgoingRefId = QtGui.qApp.db.translate('Event_OutgoingReferral', 'master_id', self.id, 'id')
            self._outgoingRef = self.getInstance(COutgoingReferralInfo, forceRef(outgoingRefId))
            self._outgoingOrg = self._outgoingRef.org
            self._outgoingRefNumber = self._outgoingRef.number
            self._createPerson = self.getInstance(CPersonInfo, forceRef(record.value('createPerson_id')))
            self._recommendations = self.getInstance(CRecommendationInfoList, self.id)

            self._relatedEvents = self.getInstance(CRelatedEventInfoList, self.id)
            self._ksg = self.getInstance(CKSGInfo, forceRef(record.value('KSG_id')), self.id)
            self._htg = self.getInstance(CHTGInfo, forceRef(record.value('HTG_id')), self.id)
            self._cashPage = self.getInstance(CEventCashPageInfo, self.id)
            self._policy = self.getInstance(CClientPolicyInfo, forceRef(record.value('client_id')), policyId=forceRef(record.value('clientPolicy_id')))
            self._directionDate = CDateInfo(forceDate(record.value('directionDate')))
            self._goal = self.getInstance(CEventGoalInfo, forceRef(record.value('goal_id')))

            return True
        else:
            self._eventType = self.getInstance(CEventTypeInfo, None)
            self._externalId = ''
            self._org = self.getInstance(COrgInfo, None)
            self._relegateOrg = self.getInstance(COrgInfo, None)
            self._contract = self.getInstance(CContractInfo, None)
            self._prevEventDate = CDateInfo()
            self._setDate = CDateInfo()
            self._setPerson = self.getInstance(CPersonInfo, None)
            self._execDate = CDateInfo()
            self._execPerson = self.getInstance(CPersonInfo, None)
            self._isPrimary = 0
            self._order = 0
            self._result = self.getInstance(CResultInfo, None)
            self._nextEventDate = CDateInfo()
            self._payStatus = 0
            self._typeAsset = self.getInstance(CEmergencyTypeAssetInfo, None)
            self.note = ''
            self._curator = self.getInstance(CPersonInfo, None)
            self._assistant = self.getInstance(CPersonInfo, None)
            self._actions = self.getInstance(CActionInfoList, None)
            self._diagnosises = self.getInstance(CDiagnosticInfoList, None)
            self._visits = self.getInstance(CVisitInfoList, None)
            self._localContract = self.getInstance(CEventLocalContractInfo, None)
            self._mes = self.getInstance(CMesInfo, None)
            self._mesSpecification = self.getInstance(CMesSpecificationInfo, None)
            self._patientModel = self.getInstance(CPatientModelInfo, None)
            self._quotaType = self.getInstance(CQuotaTypeInfo, None)
            self._cureType     = self.getInstance(CCureTypeInfo, None)
            self._cureMethod   = self.getInstance(CCureMethodInfo, None)
            self._referral     = self.getInstance(CReferralInfo, None)
            self._policlinicReferral = self.getInstance(CPoliclinicReferralInfo, None)
            self._armyReferral = self.getInstance(CReferralInfo, None)
            self._outgoingOrg = self.getInstance(COrgInfo, None)
            self._outgoingRefNumber = ''
            self._outgoingRef  = self.getInstance(COutgoingReferralInfo, None)
            self._createPerson = self.getInstance(CPersonInfo, None)
            self._recommendations = self.getInstance(CRecommendationInfoList, None)
            self._relatedEvents = self.getInstance(CRelatedEventInfoList, None)
            self._ksg = self.getInstance(CKSGInfo, None)
            self._htg = self.getInstance(CHTGInfo, None)
            self._cashPage = self.getInstance(CEventCashPageInfo, None)
            self._policy = self.getInstance(CClientPolicyInfo, None, None)
            self._directionDate = CDateInfo()
            self._goal = self.getInstance(CEventGoalInfo, None)
            return False

    def getEventTypeId(self):
        return self.eventType.id

    def recordAcceptable(self, record):
        client = self.client
        if client:
            return recordAcceptable(client.sexCode, client.ageTuple, record)
        else:
            return True

    def getTariffDescrEx(self, contractId):
        if not self._contractTariffCache:
            self._contractTariffCache = CContractTariffCache()
        return self._contractTariffCache.getTariffDescr(contractId, self)

    def getTariffDescr(self):
        return self.getTariffDescrEx(self.contract.id)

    def getPrintTemplateContext(self):
        return self.eventType.printContext

    def getData(self):
        return {
            'event'      : self,
            'client'     : self.client,
            'tempInvalid': None
        }

    def __str__(self):
        self.load()
        return unicode(self._eventType)

    def getTempInvalidList(self, begDate=None, endDate=None, types=None, currentTempInvalid = None):
        if endDate is None:
            endDate = self.execDate
        if isinstance(endDate, CDateInfo):
            endDate = endDate.date
        if begDate is None:
            begDate = endDate.addMonths(-12)
        elif isinstance(begDate, CDateInfo):
            begDate = begDate.date
        result = CTempInvalidInfoList._get(self.context, self.client._id, begDate, endDate, types)
        if currentTempInvalid:
            if currentTempInvalid.id:
                for (i, tempInvalid) in enumerate(result):
                    if tempInvalid.id == currentTempInvalid.id:
                        result._items[i] = currentTempInvalid
            else:
                result = result + [currentTempInvalid, ]
        return result

    referral    = property(lambda self: self.load()._referral)
    policlinicReferral = property(lambda self: self.load()._policlinicReferral)
    armyReferral= property(lambda self: self.load()._armyReferral)
    eventType   = property(lambda self: self.load()._eventType)
    externalId  = property(lambda self: self.load()._externalId)
    org         = property(lambda self: self.load()._org)
    relegateOrg = property(lambda self: self.load()._relegateOrg)
    client      = property(lambda self: self.load()._client)
    contract    = property(lambda self: self.load()._contract)
    prevEventDate= property(lambda self: self.load()._prevEventDate)
    setDate     = property(lambda self: self.load()._setDate)
    setPerson   = property(lambda self: self.load()._setPerson)
    execDate    = property(lambda self: self.load()._execDate)
    execPerson  = property(lambda self: self.load()._execPerson)
    isPrimary   = property(lambda self: self.load()._isPrimary)
    order       = property(lambda self: self.load()._order)
    result      = property(lambda self: self.load()._result)
    nextEventDate= property(lambda self: self.load()._nextEventDate)
    payStatus   = property(lambda self: self.load()._payStatus)
    typeAsset   = property(lambda self: self.load()._typeAsset)
    notes       = property(lambda self: self.load()._note)
    curator     = property(lambda self: self.load()._curator)
    assistant   = property(lambda self: self.load()._assistant)
    finance     = property(lambda self: self.contract.finance)
    actions     = property(lambda self: self.load()._actions)
    diagnosises = property(lambda self: self.load()._diagnosises)
    visits      = property(lambda self: self.load()._visits)
    localContract = property(lambda self: self.load()._localContract)
    mes         = property(lambda self: self.load()._mes)
    mesSpecification = property(lambda self: self.load()._mesSpecification)
    patientModel= property(lambda self: self.load()._patientModel)
    quotaType = property(lambda self: self.load()._quotaType)
    cureType    = property(lambda self: self.load()._cureType)
    cureMethod  = property(lambda self: self.load()._cureMethod)
    createPerson = property(lambda self: self.load()._createPerson)
    outgoingOrg = property(lambda self: self.load()._outgoingOrg)
    outgoingRefNumber = property(lambda self: self.load()._outgoingRefNumber)
    outgoingRef  = property(lambda self: self.load()._outgoingRef)
    recommendations = property(lambda self: self.load()._recommendations)
    relatedEvents = property(lambda self: self.load()._relatedEvents)
    ksg         = property(lambda self: self.load()._ksg)
    htg         = property(lambda self: self.load()._htg)
    cashPage = property(lambda self: self.load()._cashPage)
    policy = property(lambda self: self.load()._policy)
    directionDate = property(lambda self: self.load()._directionDate)
    goal = property(lambda self: self.load()._goal)


class CLocEventInfoList(CInfoProxyList):
    def __init__(self, context, idList):
        CInfoProxyList.__init__(self, context)
        self.idList = idList
        self._items = [ None ]*len(self.idList)

    def __getitem__(self, key):
        v = self._items[key]
        if v is None:
            v = self.getInstance(CEventInfo, self.idList[key])
            self._items[key] = v
        return v


class CRelatedEventInfoList(CLocEventInfoList):
    def __init__(self, context, eventId):
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        relatedEventIdList = QtGui.qApp.db.getAllRelated(table = tableEvent, 
                                                         idList = [eventId],
                                                         groupCol = tableEvent['prevEvent_id'],
                                                         idCol = tableEvent['id'],
                                                         maxLevels = 32)
        CLocEventInfoList.__init__(self, context, relatedEventIdList)


class CEmergencyEventInfo(CEventInfo):
    def __init__(self, context, id):
        CEventInfo.__init__(self, context, id)

    def _load(self):
        db = QtGui.qApp.db
        if CEventInfo._load(self):
            tableEmergency = db.table('EmergencyCall')
            recordEmergency = db.getRecordEx('EmergencyCall', '*', tableEmergency['event_id'].eq(self.id))
        else:
            recordEmergency = None
        if recordEmergency:
            self._numberCardCall = forceString(recordEmergency.value('numberCardCall'))
            self._brigade = self.getInstance(CEmergencyBrigadeInfo, forceRef(recordEmergency.value('brigade_id')))
            self._causeCall = self.getInstance(CEmergencyCauseCallInfo, forceRef(recordEmergency.value('causeCall_id')))
            self._whoCallOnPhone = forceString(recordEmergency.value('whoCallOnPhone'))
            self._numberPhone = forceString(recordEmergency.value('numberPhone'))
            if getEventShowTime(self._eventType.id):
                self._begDate = CDateTimeInfo(forceDate(recordEmergency.value('begDate')))
                self._passDate = CDateTimeInfo(forceDate(recordEmergency.value('passDate')))
                self._departureDate = CDateTimeInfo(forceDate(recordEmergency.value('departureDate')))
                self._arrivalDate = CDateTimeInfo(forceDate(recordEmergency.value('arrivalDate')))
                self._finishServiceDate = CDateTimeInfo(forceDate(recordEmergency.value('finishServiceDate')))
                self._endDate = CDateTimeInfo(forceDate(recordEmergency.value('endDate')))
            else:
                self._begDate = CDateInfo(forceDate(recordEmergency.value('begDate')))
                self._passDate = CDateInfo(forceDate(recordEmergency.value('passDate')))
                self._departureDate = CDateInfo(forceDate(recordEmergency.value('departureDate')))
                self._arrivalDate = CDateInfo(forceDate(recordEmergency.value('arrivalDate')))
                self._finishServiceDate = CDateInfo(forceDate(recordEmergency.value('finishServiceDate')))
                self._endDate = CDateInfo(forceDate(recordEmergency.value('endDate')))

            self._placeReceptionCall = self.getInstance(CEmergencyPlaceReceptionCallInfo, forceRef(recordEmergency.value('placeReceptionCall_id')))
            self._receivedCall = self.getInstance(CEmergencyReceivedCallInfo, forceRef(recordEmergency.value('receivedCall_id')))
            self._reasondDelays = self.getInstance(CEmergencyReasondDelaysInfo, forceRef(recordEmergency.value('reasondDelays_id')))
            self._resultCall = self.getInstance(CEmergencyResultInfo, forceRef(recordEmergency.value('resultCall_id')))
            self._accident = self.getInstance(CEmergencyAccidentInfo, forceRef(recordEmergency.value('accident_id')))
            self._death = self.getInstance(CEmergencyDeathInfo, forceRef(recordEmergency.value('death_id')))
            self._ebriety = self.getInstance(CEmergencyEbrietyInfo, forceRef(recordEmergency.value('ebriety_id')))
            self._diseased = self.getInstance(CEmergencyDiseasedInfo, forceRef(recordEmergency.value('diseased_id')))
            self._placeCall = self.getInstance(CEmergencyPlaceCallInfo, forceRef(recordEmergency.value('placeCall_id')))
            self._methodTransport = self.getInstance(CEmergencyMethodTransportInfo, forceRef(recordEmergency.value('methodTransport_id')))
            self._transfTransport = self.getInstance(CEmergencyTransferTransportInfo, forceRef(recordEmergency.value('transfTransport_id')))
            self._renunOfHospital = forceInt(recordEmergency.value('renunOfHospital'))
            self._faceRenunOfHospital = forceString(recordEmergency.value('faceRenunOfHospital'))
            self._disease = forceInt(recordEmergency.value('disease'))
            self._birth = forceInt(recordEmergency.value('birth'))
            self._pregnancyFailure = forceInt(recordEmergency.value('pregnancyFailure'))
            self._noteCall = forceString(recordEmergency.value('noteCall'))
            return True
        else:
            self._numberCardCall = ''
            self._brigade = self.getInstance(CEmergencyBrigadeInfo, None)
            self._causeCall = self.getInstance(CEmergencyCauseCallInfo, None)
            self._whoCallOnPhone = ''
            self._numberPhone = ''
            self._begDate = CDateTimeInfo()
            self._passDate = CDateTimeInfo()
            self._departureDate = CDateTimeInfo()
            self._arrivalDate = CDateTimeInfo()
            self._finishServiceDate = CDateTimeInfo()
            self._endDate = CDateTimeInfo()
            self._placeReceptionCall = self.getInstance(CEmergencyPlaceReceptionCallInfo, None)
            self._receivedCall = self.getInstance(CEmergencyReceivedCallInfo, None)
            self._reasondDelays = self.getInstance(CEmergencyReasondDelaysInfo, None)
            self._resultCall = self.getInstance(CEmergencyResultInfo, None)
            self._accident = self.getInstance(CEmergencyAccidentInfo, None)
            self._death = self.getInstance(CEmergencyDeathInfo, None)
            self._ebriety = self.getInstance(CEmergencyEbrietyInfo, None)
            self._diseased = self.getInstance(CEmergencyDiseasedInfo, None)
            self._placeCall = self.getInstance(CEmergencyPlaceCallInfo, None)
            self._methodTransport = self.getInstance(CEmergencyMethodTransportInfo, None)
            self._transfTransport = self.getInstance(CEmergencyTransferTransportInfo, None)
            self._renunOfHospital = 0
            self._faceRenunOfHospital = ''
            self._disease = 0
            self._birth = 0
            self._pregnancyFailure = 0
            self._noteCall = ''
            return False

    numberCardCall      = property(lambda self: self.load()._numberCardCall)
    brigade             = property(lambda self: self.load()._brigade)
    causeCall           = property(lambda self: self.load()._causeCall)
    whoCallOnPhone      = property(lambda self: self.load()._whoCallOnPhone)
    numberPhone         = property(lambda self: self.load()._numberPhone)
    begDate             = property(lambda self: self.load()._begDate)
    passDate            = property(lambda self: self.load()._passDate)
    departureDate       = property(lambda self: self.load()._departureDate)
    arrivalDate         = property(lambda self: self.load()._arrivalDate)
    finishServiceDate   = property(lambda self: self.load()._finishServiceDate)
    endDate             = property(lambda self: self.load()._endDate)
    placeReceptionCall  = property(lambda self: self.load()._placeReceptionCall)
    receivedCall        = property(lambda self: self.load()._receivedCall)
    reasondDelays       = property(lambda self: self.load()._reasondDelays)
    resultCall          = property(lambda self: self.load()._resultCall)
    accident            = property(lambda self: self.load()._accident)
    death               = property(lambda self: self.load()._death)
    ebriety             = property(lambda self: self.load()._ebriety)
    diseased            = property(lambda self: self.load()._diseased)
    placeCall           = property(lambda self: self.load()._placeCall)
    methodTransport     = property(lambda self: self.load()._methodTransport)
    transfTransport     = property(lambda self: self.load()._transfTransport)
    renunOfHospital     = property(lambda self: self.load()._renunOfHospital)
    faceRenunOfHospital = property(lambda self: self.load()._faceRenunOfHospital)
    disease             = property(lambda self: self.load()._disease)
    birth               = property(lambda self: self.load()._birth)
    pregnancyFailure    = property(lambda self: self.load()._pregnancyFailure)
    noteCall            = property(lambda self: self.load()._noteCall)


class CEventLocalContractInfo(CInfo):
    def __init__(self, context, eventId):
        CInfo.__init__(self, context)
        self.eventId = eventId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('Event_LocalContract')
        record = db.getRecordEx(table, '*', [table['master_id'].eq(self.eventId),
                                             table['deleted'].eq(0)]) if self.eventId else None
        if record:
            self.initByRecord(record)
            return True
        else:
            self.initByRecord(db.dummyRecord())
            return False

    def initByRecord(self, record):
        db = QtGui.qApp.db
        tableOrgAccount = db.table('Organisation_Account')
        orgId = forceRef(record.value('org_id'))
        lastOrgAccountRec = db.getRecordEx(tableOrgAccount, tableOrgAccount['id'],
                                           tableOrgAccount['organisation_id'].eq(orgId),
                                           tableOrgAccount['id'].name() + ' DESC') if orgId else None
        lastOrgAccountId = forceRef(lastOrgAccountRec.value('id')) if lastOrgAccountRec else None
        self._coordDate = CDateInfo(forceDate(record.value('coordDate')))
        self._coordAgent = forceString(record.value('coordAgent'))
        self._coordInspector = forceString(record.value('coordInspector'))
        self._coordText = forceString(record.value('coordText'))
        self._date   = CDateInfo(forceDate(record.value('dateContract')))
        self._number = forceString(record.value('numberContract'))
        self._sumLimit = forceDouble(record.value('sumLimit'))
        self._org = self.getInstance(COrgInfo, orgId)
        self._payerAccount = self.getInstance(COrgAccountInfo, lastOrgAccountId)
        self._lastName = forceString(record.value('lastName'))
        self._firstName = forceString(record.value('firstName'))
        self._patrName = forceString(record.value('patrName'))
        self._birthDate = CDateInfo(forceDate(record.value('birthDate')))
        self._document = self.getInstance(CClientDocumentInfo)
        self._document._documentType = forceString(QtGui.qApp.db.translate('rbDocumentType', 'id', record.value('documentType_id'), 'name'))
        self._document._serial = forceStringEx(record.value('serialLeft'))+' '+forceStringEx(record.value('serialRight'))
        self._document._number = forceString(record.value('number'))
        self._document._date = CDateInfo()
        self._document._origin = ''
        self._address = forceString(record.value('regAddress'))

    coordDate   = property(lambda self: self.load()._coordDate)
    coordAgent  = property(lambda self: self.load()._coordAgent)
    coordInspector = property(lambda self: self.load()._coordInspector)
    coordText   = property(lambda self: self.load()._coordText)
    date        = property(lambda self: self.load()._date)
    number      = property(lambda self: self.load()._number)
    sumLimit    = property(lambda self: self.load()._sumLimit)
    lastName    = property(lambda self: self.load()._lastName)
    firstName   = property(lambda self: self.load()._firstName)
    patrName    = property(lambda self: self.load()._patrName)
    birthDate   = property(lambda self: self.load()._birthDate)
    document    = property(lambda self: self.load()._document)
    address     = property(lambda self: self.load()._address)
    org         = property(lambda self: self.load()._org)
    payerAccount = property(lambda self: self.load()._payerAccount)

    def __str__(self):
        if self.load():
            parts = []
            if self._coordDate:
                parts.append(u'согласовано ' + self._coordDate)
            if self._coordText:
                parts.append(self._coordText)
            if self._number:
                parts.append(u'№ ' + self._number)
            if self._date:
                parts.append(u'от ' + forceString(self._date))
            if self._org:
                parts.append(unicode(self._org))
            else:
                parts.append(self._lastName)
                parts.append(self._firstName)
                parts.append(self._patrName)
            return ' '.join(parts)
        else:
            return ''


class CDagnosisTypeInfo(CRBInfo):
    tableName = 'rbDiagnosisType'


class CCharacterInfo(CRBInfo):
    tableName = 'rbDiseaseCharacter'


class CStageInfo(CRBInfo):
    tableName = 'rbDiseaseStage'


class CDispanserInfo(CRBInfo):
    tableName = 'rbDispanser'

    def _initByRecord(self, record):
        self._observed = forceBool(record.value('observed'))

    def _initByNull(self):
        self._observed = False

    observed = property(lambda self: self.load()._observed)


class CHospitalInfo(CInfo):
    names = [u'не требуется', u'требуется', u'направлен', u'пролечен']

    def __init__(self, context, code):
        CInfo.__init__(self, context)
        self.code = code
        self.name = self.names[code] if 0<=code<len(self.names) else ('{%s}' % code)
        self._ok = True
        self._loaded = True

    def __str__(self):
        return self.name


class CTraumaTypeInfo(CRBInfo):
    tableName = 'rbTraumaType'


class CHealthGroupInfo(CRBInfo):
    tableName = 'rbHealthGroup'


class CMedicalGroupInfo(CRBInfo):
    tableName = 'rbMedicalGroup'


class CDiagnosticInfo(CInfo):
    def __init__(self, context, id):
        CInfo.__init__(self, context)
        self.id = id

    def _load(self):
        db = QtGui.qApp.db
        tableDiagnostic = db.table('Diagnostic')
        tableDiagnosis = db.table('Diagnosis')
        record = db.getRecord(tableDiagnostic.leftJoin(tableDiagnosis, tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id'])),
                              'Diagnostic.*, Diagnosis.MKB, Diagnosis.MKBEx, Diagnosis.morphologyMKB, Diagnosis.mod_id',
                              self.id)
        if record:
            self.initByRecord(record)
            return True
        else:
            self.initByRecord(db.dummyRecord())
            return False

    def initByRecord(self, record):
        self._type = self.getInstance(CDagnosisTypeInfo, forceRef(record.value('diagnosisType_id')))
        self._MKB = self.getInstance(CMKBInfo, forceString(record.value('MKB')))
        self._MKBEx = self.getInstance(CMKBInfo, forceString(record.value('MKBEx')))
        self._morphologyMKB = forceString(record.value('morphologyMKB'))
        self._character = self.getInstance(CCharacterInfo, forceRef(record.value('character_id')))
        self._stage = self.getInstance(CStageInfo, forceRef(record.value('stage_id')))
        self._dispanser = self.getInstance(CDispanserInfo, forceRef(record.value('dispanser_id')))
        self._sanatorium = self.getInstance(CHospitalInfo, forceInt(record.value('sanatorium')))
        self._hospital = self.getInstance(CHospitalInfo, forceInt(record.value('hospital')))
        self._traumaType = self.getInstance(CTraumaTypeInfo, forceRef(record.value('traumaType_id')))
        self._speciality = self.getInstance(CSpecialityInfo, forceRef(record.value('speciality_id')))
        self._person = self.getInstance(CPersonInfo, forceRef(record.value('person_id')))
        self._healthGroup = self.getInstance(CHealthGroupInfo, forceRef(record.value('healthGroup_id')))
        self._result = self.getInstance(CDiagnosticResultInfo, forceRef(record.value('result_id')))
        self._setDate = CDateInfo(forceDate(record.value('setDate')))
        self._endDate = CDateInfo(forceDate(record.value('endDate')))
        self._notes = forceString(record.value('notes'))
        self._mod = self.getInstance(CDiagnosisInfo, forceRef(record.value('mod_id')))
        self._TNMS = self.getInstance(CTNMSInfo, forceString(record.value('TNMS')))

    type          = property(lambda self: self.load()._type)
    MKB           = property(lambda self: self.load()._MKB)
    MKBEx         = property(lambda self: self.load()._MKBEx)
    morphologyMKB = property(lambda self: self.load()._morphologyMKB)
    character     = property(lambda self: self.load()._character)
    stage         = property(lambda self: self.load()._stage)
    dispanser     = property(lambda self: self.load()._dispanser)
    sanatorium    = property(lambda self: self.load()._sanatorium)
    hospital      = property(lambda self: self.load()._hospital)
    traumaType    = property(lambda self: self.load()._traumaType)
    speciality    = property(lambda self: self.load()._speciality)
    person        = property(lambda self: self.load()._person)
    healthGroup   = property(lambda self: self.load()._healthGroup)
    medicalGroup  = property(lambda self: self.load()._medicalGroup)
    result        = property(lambda self: self.load()._result)
    setDate       = property(lambda self: self.load()._setDate)
    endDate       = property(lambda self: self.load()._endDate)
    notes         = property(lambda self: self.load()._notes)
    mod           = property(lambda self: self.load()._mod)
    TNMS          = property(lambda self: self.load()._TNMS)


class CDiagnosticInfoList(CInfoList):
    def __init__(self, context, eventId):
        CInfoList.__init__(self, context)
        self.eventId = eventId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('Diagnostic')
        idList = db.getIdList(table, 'id', table['event_id'].eq(self.eventId), 'id')
        self._items = [ self.getInstance(CDiagnosticInfo, id) for id in idList ]
        return True


class CDiagnosisInfo(CInfo):
    def __init__(self, context, id):
        CInfo.__init__(self, context)
        self.id = id

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('Diagnosis')
        record = db.getRecord(table, '*', self.id)
        if record:
            self.initByRecord(record)
            return True
        else:
            self.initByRecord(db.dummyRecord())
            return False

    def initByRecord(self, record):
        self._type = self.getInstance(CDagnosisTypeInfo, forceRef(record.value('diagnosisType_id')))
        self._MKB = self.getInstance(CMKBInfo, forceString(record.value('MKB')))
        self._MKBEx = self.getInstance(CMKBInfo, forceString(record.value('MKBEx')))
        self._morphologyMKB = forceString(record.value('morphologyMKB'))
        self._character = self.getInstance(CCharacterInfo, forceRef(record.value('character_id')))
        self._dispanser = self.getInstance(CDispanserInfo, forceRef(record.value('dispanser_id')))
        self._traumaType = self.getInstance(CTraumaTypeInfo, forceRef(record.value('traumaType_id')))
        self._person = self.getInstance(CPersonInfo, forceRef(record.value('person_id')))
        self._setDate = CDateInfo(forceDate(record.value('setDate')))
        self._endDate = CDateInfo(forceDate(record.value('endDate')))
        self._mod = self.getInstance(CDiagnosisInfo, forceRef(record.value('mod_id')))

    type          = property(lambda self: self.load()._type)
    MKB           = property(lambda self: self.load()._MKB)
    MKBEx         = property(lambda self: self.load()._MKBEx)
    morphologyMKB = property(lambda self: self.load()._morphologyMKB)
    character     = property(lambda self: self.load()._character)
    dispanser     = property(lambda self: self.load()._dispanser)
    traumaType    = property(lambda self: self.load()._traumaType)
    person        = property(lambda self: self.load()._person)
    setDate       = property(lambda self: self.load()._setDate)
    endDate       = property(lambda self: self.load()._endDate)
    mod           = property(lambda self: self.load()._mod)


class CDiagnosisInfoList(CInfoList):
    def __init__(self, context, clientId):
        CInfoList.__init__(self, context)
        self.clientId = clientId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('Diagnosis')
        idList = db.getIdList(table,
                              'id',
                              [table['client_id'].eq(self.clientId), table['deleted'].eq(0), table['mod_id'].isNull()],
                              'endDate')
        self._items = [ self.getInstance(CDiagnosisInfo, id) for id in idList ]
        return True


class CTNMSInfo(CInfo):
    def __init__(self, context, tnmsString):
        CInfo.__init__(self, context)
        self._tnmsString = tnmsString
        self._tnmsDict = convertTNMSStringToDict(tnmsString)
        self._loaded = True

    def __getitem__(self, item):
        return self._tnmsDict.get(item, '--')

    def __str__(self):
        return self._tnmsString


class CSceneInfo(CRBInfo):
    tableName = 'rbScene'


class CVisitTypeInfo(CRBInfo):
    tableName = 'rbVisitType'


class CVisitInfo(CInfo):
    def __init__(self, context, id):
        CInfo.__init__(self, context)
        self.id = id

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('Visit', '*', self.id)
        if record:
            self.initByRecord(record)
            return True
        else:
            self.initByRecord(db.dummyRecord())
            return False

    def initByRecord(self, record):
        self._scene = self.getInstance(CSceneInfo, forceRef(record.value('scene_id')))
        self._date = CDateInfo(forceDate(record.value('date')))
        self._type = self.getInstance(CVisitTypeInfo, forceRef(record.value('visitType_id')))
        self._person = self.getInstance(CPersonInfo, forceRef(record.value('person_id')))
        self._assistant = self.getInstance(CPersonInfo, forceRef(record.value('assistant_id')))
        self._isPrimary = forceBool(record.value('isPrimary'))
        self._finance = self.getInstance(CFinanceInfo, forceRef(record.value('finance_id')))
        self._service = self.getInstance(CServiceInfo, forceRef(record.value('service_id')))
        self._payStatus = forceInt(record.value('payStatus'))

    scene       = property(lambda self: self.load()._scene)
    date        = property(lambda self: self.load()._date)
    type        = property(lambda self: self.load()._type)
    person      = property(lambda self: self.load()._person)
    assistant   = property(lambda self: self.load()._assistant)
    isPrimary   = property(lambda self: self.load()._isPrimary)
    finance     = property(lambda self: self.load()._finance)
    service     = property(lambda self: self.load()._service)
    payStatus   = property(lambda self: self.load()._payStatus)


class CVisitInfoList(CInfoList):
    def __init__(self, context, eventId):
        CInfoList.__init__(self, context)
        self.eventId = eventId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('Visit')
        idList = db.getIdList(table, 'id', table['event_id'].eq(self.eventId), 'id')
        self._items = [ self.getInstance(CVisitInfo, id) for id in idList ]
        return True


class CDiagnosticInfoProxyList(CInfoProxyList):
    def __init__(self, context, models):
        CInfoProxyList.__init__(self, context)
        self._rawItems = []
        for model in models:
            self._rawItems.extend(model.items())
        self._items = [ None ] * len(self._rawItems)

    def __getitem__(self, key):
        v = self._items[key]
        if v is None:
            record = self._rawItems[key]
            v = self.getInstance(CDiagnosticInfo, 'tmp_%d'%key)
            v.initByRecord(record)
            v.setOkLoaded()
            self._items[key] = v
        return v


class CVisitInfoProxyList(CInfoProxyList):
    def __init__(self, context, modelVisits):
        CInfoProxyList.__init__(self, context)
        self._items = [ None ] * len(modelVisits.items())
        self.model = modelVisits

    def __getitem__(self, key):
        v = self._items[key]
        if v is None:
            record = self.model.items()[key]
            v = self.getInstance(CVisitInfo, 'tmp_%d'%key)
            v.initByRecord(record)
            v.setOkLoaded()
            self._items[key] = v
        return v


class CVisitPersonallInfo(CInfo):
    def __init__(self, context, item=None):
        if not item:
            item = []
        CInfo.__init__(self, context)
        self.item = item

    def _load(self):
        if self.item:
            self._scene = self.getInstance(CSceneInfo, self.item[0])
            self._date = CDateTimeInfo(self.item[1])
            self._type = self.getInstance(CVisitTypeInfo, self.item[2])
            self._person = self.getInstance(CPersonInfo, self.item[3])
            self._isPrimary = forceBool(self.item[4])
            self._finance = self.getInstance(CFinanceInfo, self.item[5])
            self._service = self.getInstance(CServiceInfo, self.item[6])
            self._payStatus = self.item[7]

    scene       = property(lambda self: self.load()._scene)
    date        = property(lambda self: self.load()._date)
    type        = property(lambda self: self.load()._type)
    person      = property(lambda self: self.load()._person)
    isPrimary   = property(lambda self: self.load()._isPrimary)
    finance     = property(lambda self: self.load()._finance)
    service     = property(lambda self: self.load()._service)
    payStatus   = property(lambda self: self.load()._payStatus)


class CEmergencyBrigadeInfo(CInfo):
    def __init__(self, context, brigadeId):
        CInfo.__init__(self, context)
        self.brigadeId = brigadeId
        self._code = ''
        self._name = ''
        self._regionalCode = ''

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('EmergencyBrigade', '*', self.brigadeId)
        if record:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            self._regionalCode = forceString(record.value('regionalCode'))
            return True
        else:
            return False

    def __str__(self):
        return self.load()._name

    code     = property(lambda self: self.load()._code)
    name     = property(lambda self: self.load()._name)
    regionalCode = property(lambda self: self.load()._regionalCode)


class CEmergencyCauseCallInfo(CInfo):
    def __init__(self, context, causeCallId):
        CInfo.__init__(self, context)
        self.causeCallId = causeCallId
        self._code = ''
        self._name = ''
        self._regionalCode = ''

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('rbEmergencyCauseCall', '*', self.causeCallId)
        if record:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            self._regionalCode = forceString(record.value('regionalCode'))
            return True
        else:
            return False

    def __str__(self):
        return self.load()._name

    code     = property(lambda self: self.load()._code)
    name     = property(lambda self: self.load()._name)
    regionalCode = property(lambda self: self.load()._regionalCode)


class CEmergencyTransferTransportInfo(CInfo):
    def __init__(self, context, transfTranspId):
        CInfo.__init__(self, context)
        self.transfTranspId = transfTranspId
        self._code = ''
        self._name = ''
        self._regionalCode = ''

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('rbEmergencyTransferredTransportation', '*', self.transfTranspId)
        if record:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            self._regionalCode = forceString(record.value('regionalCode'))
            return True
        else:
            return False

    def __str__(self):
        return self.load()._name

    code     = property(lambda self: self.load()._code)
    name     = property(lambda self: self.load()._name)
    regionalCode = property(lambda self: self.load()._regionalCode)


class CEmergencyPlaceReceptionCallInfo(CInfo):
    def __init__(self, context, placeReceptionCallId):
        CInfo.__init__(self, context)
        self.placeReceptionCallId = placeReceptionCallId
        self._code = ''
        self._name = ''
        self._regionalCode = ''

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('rbEmergencyPlaceReceptionCall', '*', self.placeReceptionCallId)
        if record:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            self._regionalCode = forceString(record.value('regionalCode'))
            return True
        else:
            return False

    def __str__(self):
        return self.load()._name

    code     = property(lambda self: self.load()._code)
    name     = property(lambda self: self.load()._name)
    regionalCode = property(lambda self: self.load()._regionalCode)


class CEmergencyReceivedCallInfo(CInfo):
    def __init__(self, context, receivedCallId):
        CInfo.__init__(self, context)
        self.receivedCallId = receivedCallId
        self._code = ''
        self._name = ''
        self._regionalCode = ''

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('rbEmergencyReceivedCall', '*', self.receivedCallId)
        if record:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            self._regionalCode = forceString(record.value('regionalCode'))
            return True
        else:
            return False

    def __str__(self):
        return self.load()._name

    code     = property(lambda self: self.load()._code)
    name     = property(lambda self: self.load()._name)
    regionalCode = property(lambda self: self.load()._regionalCode)


class CEmergencyReasondDelaysInfo(CInfo):
    def __init__(self, context, emergencyReasondDelaysId):
        CInfo.__init__(self, context)
        self.emergencyReasondDelaysId = emergencyReasondDelaysId
        self._code = ''
        self._name = ''
        self._regionalCode = ''

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('rbEmergencyReasondDelays', '*', self.emergencyReasondDelaysId)
        if record:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            self._regionalCode = forceString(record.value('regionalCode'))
            return True
        else:
            return False

    def __str__(self):
        return self.load()._name

    code     = property(lambda self: self.load()._code)
    name     = property(lambda self: self.load()._name)
    regionalCode = property(lambda self: self.load()._regionalCode)


class CEmergencyResultInfo(CInfo):
    def __init__(self, context, emergencyResultId):
        CInfo.__init__(self, context)
        self.emergencyResultId = emergencyResultId
        self._code = ''
        self._name = ''
        self._regionalCode = ''

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('rbEmergencyResult', '*', self.emergencyResultId)
        if record:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            self._regionalCode = forceString(record.value('regionalCode'))
            return True
        else:
            return False

    def __str__(self):
        return self.load()._name

    code     = property(lambda self: self.load()._code)
    name     = property(lambda self: self.load()._name)
    regionalCode = property(lambda self: self.load()._regionalCode)


class CEmergencyAccidentInfo(CInfo):
    def __init__(self, context, accidentId):
        CInfo.__init__(self, context)
        self.accidentId = accidentId
        self._code = ''
        self._name = ''
        self._regionalCode = ''

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('rbEmergencyAccident', '*', self.accidentId)
        if record:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            self._regionalCode = forceString(record.value('regionalCode'))
            return True
        else:
            return False

    def __str__(self):
        return self.load()._name

    code     = property(lambda self: self.load()._code)
    name     = property(lambda self: self.load()._name)
    regionalCode = property(lambda self: self.load()._regionalCode)


class CEmergencyDeathInfo(CInfo):
    def __init__(self, context, emergencyDeathId):
        CInfo.__init__(self, context)
        self.emergencyDeathId = emergencyDeathId
        self._code = ''
        self._name = ''
        self._regionalCode = ''

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('rbEmergencyDeath', '*', self.emergencyDeathId)
        if record:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            self._regionalCode = forceString(record.value('regionalCode'))
            return True
        else:
            return False

    def __str__(self):
        return self.load()._name

    code     = property(lambda self: self.load()._code)
    name     = property(lambda self: self.load()._name)
    regionalCode = property(lambda self: self.load()._regionalCode)


class CEmergencyEbrietyInfo(CInfo):
    def __init__(self, context, ebrietyId):
        CInfo.__init__(self, context)
        self.ebrietyId = ebrietyId
        self._code = ''
        self._name = ''
        self._regionalCode = ''

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('rbEmergencyEbriety', '*', self.ebrietyId)
        if record:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            self._regionalCode = forceString(record.value('regionalCode'))
            return True
        else:
            return False

    def __str__(self):
        return self.load()._name

    code     = property(lambda self: self.load()._code)
    name     = property(lambda self: self.load()._name)
    regionalCode = property(lambda self: self.load()._regionalCode)


class CEmergencyDiseasedInfo(CInfo):
    def __init__(self, context, emergencyDiseasedId):
        CInfo.__init__(self, context)
        self.emergencyDiseasedId = emergencyDiseasedId
        self._code = ''
        self._name = ''
        self._regionalCode = ''

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('rbEmergencyDiseased', '*', self.emergencyDiseasedId)
        if record:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            self._regionalCode = forceString(record.value('regionalCode'))
            return True
        else:
            return False

    def __str__(self):
        return self.load()._name

    code     = property(lambda self: self.load()._code)
    name     = property(lambda self: self.load()._name)
    regionalCode = property(lambda self: self.load()._regionalCode)


class CEmergencyPlaceCallInfo(CInfo):
    def __init__(self, context, placeCallId):
        CInfo.__init__(self, context)
        self.placeCallId = placeCallId
        self._code = ''
        self._name = ''
        self._regionalCode = ''

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('rbEmergencyPlaceCall', '*', self.placeCallId)
        if record:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            self._regionalCode = forceString(record.value('regionalCode'))
            return True
        else:
            return False

    def __str__(self):
        return self.load()._name

    code     = property(lambda self: self.load()._code)
    name     = property(lambda self: self.load()._name)
    regionalCode = property(lambda self: self.load()._regionalCode)


class CEmergencyMethodTransportInfo(CInfo):
    def __init__(self, context, methodTransportId):
        CInfo.__init__(self, context)
        self.methodTransportId = methodTransportId
        self._code = ''
        self._name = ''
        self._regionalCode = ''

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('rbEmergencyMethodTransportation', '*', self.methodTransportId)
        if record:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            self._regionalCode = forceString(record.value('regionalCode'))
            return True
        else:
            return False

    def __str__(self):
        return self.load()._name

    code     = property(lambda self: self.load()._code)
    name     = property(lambda self: self.load()._name)
    regionalCode = property(lambda self: self.load()._regionalCode)


class CEmergencyTypeAssetInfo(CInfo):
    def __init__(self, context, typeAssetId):
        CInfo.__init__(self, context)
        self.typeAssetId = typeAssetId
        self._code = ''
        self._name = ''
        self._regionalCode = ''

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('rbEmergencyTypeAsset', '*', self.typeAssetId)
        if record:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            self._regionalCode = forceString(record.value('regionalCode'))
            return True
        else:
            return False

    def __str__(self):
        return self.load()._name

    code     = property(lambda self: self.load()._code)
    name     = property(lambda self: self.load()._name)
    regionalCode = property(lambda self: self.load()._regionalCode)


class CCashOperationInfo(CRBInfo):
    tableName = 'rbCashOperation'


class CKSGInfo(CInfo):
    def __init__(self, context, itemId, eventId = None):
        CInfo.__init__(self, context)
        self.id = itemId
        self._eventId = eventId
        self._tariffInfo = None
        self._serviceId = None
        self._code = ''
        self._name = ''
        self._duration = 0

    def setRecord(self, record):
        self._code = forceString(record.value('code')) if record else ''
        self._name = forceString(record.value('name')) if record else ''
        self._duration = forceInt(record.value('duration')) if record else 0

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('mes.mrbClinicalStatisticalGroups', '*', self.id)
        self.setRecord(record)
        return bool(record)

    def _getTariffInfo(self):
        if not self._eventId:
            return None

        if self._serviceId is None:
            code = QtGui.qApp.db.translate('mes.mrbClinicalStatisticalGroups', 'id', self.id, 'code')
            self._serviceId = forceRef(QtGui.qApp.db.translate('rbService', 'code', code, 'id'))

        if self._tariffInfo is None:
            eventInfo = self.getInstance(CEventInfo, self._eventId)
            for tariffInfo in eventInfo.contract.tariffs:
                if not tariffInfo.service.id == self._serviceId:
                    continue

                tariff = CTariff(tariffInfo._record)
                if isTariffApplicable(tariff,
                                      self._eventId,
                                      eventInfo.execPerson.tariffCategory.id,
                                      eventInfo.execDate.date):
                    self._tariffInfo = tariffInfo
                    break
        if self._tariffInfo is None:
            self._tariffInfo = CTariff(None)
        return self._tariffInfo

    code  = property(lambda self: self.load()._code)
    name  = property(lambda self: self.load()._name)
    duration = property(lambda self: self.load()._duration)
    tariff = property(lambda self: self.load()._getTariffInfo())


class CHTGInfo(CInfo):
    def __init__(self, context, itemId, eventId = None):
        CInfo.__init__(self, context)
        self.id = itemId
        self._eventId = eventId
        self._tariffInfo = None
        self._serviceId = None
        self._code = ''
        self._name = ''

    def setRecord(self, record):
        self._code = forceString(record.value('code')) if record else ''
        self._name = forceString(record.value('name')) if record else ''

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('mes.mrbHighTechMedicalGroups', '*', self.id)
        self.setRecord(record)
        return bool(record)

    def _getTariffInfo(self):
        if not self._eventId:
            return None

        if self._serviceId is None:
            code = QtGui.qApp.db.translate('mes.mrbHighTechMedicalGroups', 'id', self.id, 'code')
            self._serviceId = forceRef(QtGui.qApp.db.translate('rbService', 'code', code, 'id'))

        if self._tariffInfo is None:
            eventInfo = self.getInstance(CEventInfo, self._eventId)
            for tariffInfo in eventInfo.contract.tariffs:
                if not tariffInfo.service.id == self._serviceId:
                    continue

                tariff = CTariff(tariffInfo._record)
                if isTariffApplicable(tariff,
                                      self._eventId,
                                      eventInfo.execPerson.tariffCategory.id,
                                      eventInfo.execDate.date):
                    self._tariffInfo = tariffInfo
                    break
        if self._tariffInfo is None:
            self._tariffInfo = CTariff(None)
        return self._tariffInfo

    code  = property(lambda self: self.load()._code)
    name  = property(lambda self: self.load()._name)
    tariff = property(lambda self: self.load()._getTariffInfo())


class CRecommendationInfo(CRBInfo):
    tableName = 'Recommendation'
    def __init__(self, context, recommendationId):
        CRBInfo.__init__(self, context, recommendationId)

    def _initByRecord(self, record):
        from Events.ActionInfo import CActionInfo, CActionTypeInfo
        self._person = self.getInstance(CPersonInfo, forceRef(record.value('person_id')))
        self._actionType = self.getInstance(CActionTypeInfo, CActionTypeCache.getById(forceRef(record.value('actionType_id'))))
        self._setDate = CDateInfo(forceDate(record.value('setDate')))
        self._expireDate = CDateInfo(forceDate(record.value('expireDate')))
        self._execDate = CDateInfo(forceDate(record.value('expireDate')))
        self._setEvent = self.getInstance(CEventInfo, forceRef(record.value('setEvent_id')))
        self._execAction = self.getInstance(CActionInfo, forceRef(record.value('execAction_id')))

    def _initByNull(self):
        from Events.ActionInfo import CActionInfo, CActionTypeInfo
        self._person = self.getInstance(CPersonInfo, None)
        self._actionType = self.getInstance(CActionTypeInfo, None)
        self._setDate = CDateInfo()
        self._expireDate = CDateInfo()
        self._execDate = CDateInfo()
        self._setEvent = self.getInstance(CEventInfo, None)
        self._execAction = self.getInstance(CActionInfo, None)

    person = property(lambda self: self.load()._person)
    actionType = property(lambda self: self.load()._actionType)
    setDate = property(lambda self: self.load()._setDate)
    expireDate = property(lambda self: self.load()._expireDate)
    execDate = property(lambda self: self.load()._execDate)
    setEvent = property(lambda self: self.load()._setEvent)
    execAction = property(lambda self: self.load()._execAction)


class CRecommendationInfoList(CInfoList):
    def __init__(self, context, eventId):
        CInfoList.__init__(self, context)
        self.eventId = eventId
        self._idList = []

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('Recommendation')
        self._idList = db.getIdList(table, 'id', [table['setEvent_id'].eq(self.eventId), table['deleted'].eq(0)])
        self._items = [self.getInstance(CRecommendationInfo, id) for id in self._idList]
        return True
