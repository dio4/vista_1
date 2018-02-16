# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Service     import CServiceInfo

from library.PrintInfo  import CInfo, CInfoList, CDateInfo, CRBInfo
from library.Utils      import forceDate, forceInt, forceRef, forceString, calcAgeTuple, formatAgeTuple, formatNameInt,\
                               formatSex, formatShortNameInt, formatSNILS

from Utils         import COrgInfo, COrgStructureInfo


gAcademicDegree = {1:u'к.м.н.',
                   2:u'д.м.н.',
                  }

class CPersonInfo(CInfo):
    def __init__(self, context, personId):
        CInfo.__init__(self, context)
        self.personId = personId
        self._code = ''
        self._federalCode = ''
        self._regionalCode = ''
        self._lastName = ''
        self._firstName = ''
        self._patrName = ''
        self._sexCode   = -1
        self._sex       = ''
        self._birthDate = CDateInfo(None)
        self._ageTuple  = None
        self._age       = ''
        self._SNILS     = ''
        self._office = ''
        self._office2 = ''
        self._post = self.getInstance(CPostInfo, None)
        self._speciality = self.getInstance(CSpecialityInfo, None)
        self._organisation = self.getInstance(COrgInfo, None)
        self._orgStructure = self.getInstance(COrgStructureInfo, None)
        self._academicDegree = 0
        self._tariffCategory = self.getInstance(CTariffCategoryInfo, None)
        self._login = ''
        self._orders = None
        self._maritalStatus = 0
        self._contactNumber = ''
        self._regType = 0
        self._regBegDate = None
        self._regEndDate = None
        self._isReservist = 0
        self._employmentType = 0
        self._occupationType = 0
        self._citizenship_id = None
        self._education = None
        self._INN = ''
        self._birthPlace = ''
        self._document = self.getInstance(CPersonDocumentInfo, None)
        self._addressRegistry = None
        self._addressResidentional = None
        self._finance_id = 0
        self._awards = None


    def _load(self):
        db = QtGui.qApp.db
        tablePerson  = db.table('Person')
        record = db.getRecord(tablePerson, '*', self.personId)
        if record:
            self._code = forceString(record.value('code'))
            self._federalCode = forceString(record.value('federalCode'))
            self._regionalCode = forceString(record.value('regionalCode'))
            self._lastName = forceString(record.value('lastName'))
            self._firstName = forceString(record.value('firstName'))
            self._patrName = forceString(record.value('patrName'))
            self._sexCode   = forceInt(record.value('sex'))
            self._sex       = formatSex(self._sexCode)
            self._birthDate = CDateInfo(record.value('birthDate'))
            self._birthPlace= forceString(record.value('birthPlace'))
            self._ageTuple  = calcAgeTuple(self._birthDate.date, QtCore.QDate.currentDate())
            self._age       = formatAgeTuple(self._ageTuple, self._birthDate.date, QtCore.QDate.currentDate())
            self._SNILS     = formatSNILS(forceString(record.value('SNILS')))
            self._office = forceString(record.value('office'))
            self._office2 = forceString(record.value('office2'))

            self._post = self.getInstance(CPostInfo, forceRef(record.value('post_id')))
            self._speciality = self.getInstance(CSpecialityInfo, forceRef(record.value('speciality_id')))
            self._organisation = self.getInstance(COrgInfo, forceRef(record.value('org_id')))
            self._orgStructure = self.getInstance(COrgStructureInfo, forceRef(record.value('orgStructure_id')))
            self._academicDegree = forceInt(record.value('academicDegree'))
            self._tariffCategory = self.getInstance(CTariffCategoryInfo, forceRef(record.value('tariffCategory_id')))
            self._login = forceString(record.value('login'))

            self._maritalStatus = forceInt(record.value('maritalStatus'))
            self._contactNumber = forceString(record.value('contactNumber'))
            self._regType = forceInt(record.value('regType'))
            self._regBegDate = forceDate(record.value('regBegDate'))
            self._regEndDate = forceDate(record.value('regEndDate'))
            self._isReservist = forceInt(record.value('isReservist'))
            self._employmentType = forceInt(record.value('employmentType'))
            self._occupationType = forceInt(record.value('occupationType'))
            self._citizenship_id = forceInt(record.value('citizenship_id'))
            self._education = self.getInstance(CPersonEducationItemInfoList, self.personId)

            self._INN = forceString(record.value('INN'))
            self._document = self.getInstance(CPersonDocumentInfo, self.personId)
            self._addressRegistry = self.getInstance(CPersonAddressRegistryInfoList, self.personId)
            self._addressResidentional = self.getInstance(CPersonAddressResidentionalInfoList, self.personId)
            self._finance_id = forceInt(record.value('finance_id'))
            self._awards = self.getInstance(CPersonAwardsInfoList, self.personId)

            return True
        else:
            return False


    def getShortName(self):
        self.load()
        return formatShortNameInt(self._lastName, self._firstName, self._patrName)


    def getFullName(self):
        self.load()
        return formatNameInt(self._lastName, self._firstName, self._patrName)


    def getOrders(self):
        self.load()
        if self._orders is None:
            self._orders = self.getInstance(CPersonOrderInfoList, self.personId)
        return self._orders


#    def __unicode__(self):
    def __str__(self):
        self.load()
        result = formatShortNameInt(self._lastName, self._firstName, self._patrName)
        if self._speciality:
            result += ', '+self._speciality.name
        if self._academicDegree:
            result += ', '+gAcademicDegree.get(self._academicDegree, '')
        return unicode(result)

    id             = property(lambda self: self.load().personId)
    code           = property(lambda self: self.load()._code)
    federalCode    = property(lambda self: self.load()._federalCode)
    regionalCode   = property(lambda self: self.load()._regionalCode)
    lastName       = property(lambda self: self.load()._lastName)
    firstName      = property(lambda self: self.load()._firstName)
    patrName       = property(lambda self: self.load()._patrName)
    fullName       = property(getFullName)
    longName       = property(getFullName)
    shortName      = property(getShortName)
    name           = property(getShortName)
    sexCode        = property(lambda self: self.load()._sexCode)
    sex            = property(lambda self: self.load()._sex)
    birthDate      = property(lambda self: self.load()._birthDate)
    ageTuple       = property(lambda self: self.load()._ageTuple)
    age            = property(lambda self: self.load()._age)
    SNILS          = property(lambda self: self.load()._SNILS)
    office         = property(lambda self: self.load()._office)
    office2        = property(lambda self: self.load()._office2)
    post           = property(lambda self: self.load()._post)
    speciality     = property(lambda self: self.load()._speciality)
    organisation   = property(lambda self: self.load()._organisation)
    orgStructure   = property(lambda self: self.load()._orgStructure)
    academicDegree = property(lambda self: gAcademicDegree.get(self.load()._academicDegree, ''))
    tariffCategory = property(lambda self: self.load()._tariffCategory)
    login          = property(lambda self: self.load()._login)
    orders         = property(getOrders)
    maritalStatus  = property(lambda self: self.load()._maritalStatus)
    contactNumber  = property(lambda self: self.load()._contactNumber)
    regType        = property(lambda self: self.load()._regType)
    regBegDate     = property(lambda self: self.load()._regBegDate)
    regEndDate     = property(lambda self: self.load()._regEndDate)
    isReservist    = property(lambda self: self.load()._isReservist)
    employmentType = property(lambda self: self.load()._employmentType)
    occupationType = property(lambda self: self.load()._occupationType)
    citizenship_id = property(lambda self: self.load()._citizenship_id)
    education      = property(lambda self: self.load()._education)
    INN            = property(lambda self: self.load()._INN)
    birthPlace     = property(lambda self: self.load()._birthPlace)
    document       = property(lambda self: self.load()._document)
    addressRegistry = property(lambda self: self.load()._addressRegistry)
    addressResidentional = property(lambda self: self.load()._addressResidentional)
    finance_id     = property(lambda self: self.load()._finance_id)
    awards         = property(lambda self: self.load()._awards)

class CPersonDocumentInfo(CInfo):
    def __init__(self, context, personId):
        CInfo.__init__(self, context)
        self.personId = personId
        self._documentSerial = ''
        self._documentNumber = ''
        self._documentOrigin = ''
        self._documentDate = None

    def _load(self):
        db = QtGui.qApp.db
        tablePersonDocument  = db.table('Person_Document')
        record = db.getRecord(tablePersonDocument, '*', 'WHERE `master_id` = %s AND `documentType_id` = 1 AND `deleted` = 0' % self.personId)
        if record:
            self._documentSerial = forceString(record.value('serial'))
            self._documentNumber = forceString(record.value('number'))
            self._documentOrigin = forceString(record.value('origin'))
            self._documentDate = forceDate(record.value('date'))

    documentSerial         = property(lambda self: self.load()._documentSerial)
    documentNumber         = property(lambda self: self.load()._documentNumber)
    documentOrigin         = property(lambda self: self.load()._documentOrigin)
    documentDate           = property(lambda self: self.load()._documentDate)

class CPersonAddressRegistryInfoList(CInfoList):
    def __init__(self, context, personId):
        CInfoList.__init__(self, context)
        self.personId = personId

    def _load(self):
        from Registry.Utils import CAddressInfo
        db = QtGui.qApp.db
        tablePersonAddress = db.table('Person_Address')
        idList = db.getIdList(tablePersonAddress, 'address_id', db.joinAnd([tablePersonAddress['master_id'].eq(self.personId), tablePersonAddress['type'].eq(0), tablePersonAddress['deleted'].eq(0)]), 'address_id')
        self._items = [ self.getInstance(CAddressInfo, address_id) for address_id in idList ]
        return True

class CPersonAddressResidentionalInfoList(CInfoList):
    def __init__(self, context, personId):
        CInfoList.__init__(self, context)
        self.personId = personId

    def _load(self):
        from Registry.Utils import CAddressInfo
        db = QtGui.qApp.db
        tablePersonAddress = db.table('Person_Address')
        idList = db.getIdList(tablePersonAddress, 'address_id', db.joinAnd([tablePersonAddress['master_id'].eq(self.personId), tablePersonAddress['type'].eq(1), tablePersonAddress['deleted'].eq(0)]), 'address_id')
        self._items = [ self.getInstance(CAddressInfo, address_id) for address_id in idList ]
        return True

class CPersonEducationItemInfoList(CInfoList):
    def __init__(self, context, masterId):
        CInfoList.__init__(self, context)
        self.masterId = masterId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('Person_Education')
        idList = db.getIdList(table, 'id', db.joinAnd([table['master_id'].eq(self.masterId), table['deleted'].eq(0)]), 'id')
        self._items = [ self.getInstance(CPersonEducationItemInfo, id) for id in idList ]
        return True

class CPersonEducationItemInfo(CInfo):
    def __init__(self, context, masterId):
        CInfo.__init__(self, context)
        self.masterId = masterId
        self._org_id = None
        self._educationType = 0
        self._cycle = ''
        self._hours = 0
        self._category_id = None
        self._speciality_id = 0
        self._status = ''
        self._documentType_id = 0
        self._educationDocumentSerial = ''
        self._educationDocumentNumber = ''
        self._educationDocumentOrigin = ''
        self._validFromDate = None
        self._validToDate = None

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('Person_Education', '*', self.masterId)
        if record:
            self._org_id = forceInt(record.value('org_id'))
            self._educationType = forceInt(record.value('educationType'))
            self._cycle = forceString(record.value('cycle'))
            self._hours = forceInt(record.value('hourse'))
            self._category_id = forceInt(record.value('category_id'))
            self._speciality = forceInt(record.value('speciality_id'))
            self._status = forceString(record.value('status'))
            self._documentType_id = forceInt(record.value('documentType_id'))
            self._educationDocumentSerial = forceString(record.value('serial'))
            self._educationDocumentNumber = forceString(record.value('number'))
            self._educationDocumentOrigin = forceString(record.value('origin'))
            self._validFromDate = forceDate(record.value('validFromDate'))
            self._validToDate = forceDate(record.value('validToDate'))


    org_id         = property(lambda self: self.load()._org_id)
    educationType  = property(lambda self: self.load()._educationType)
    cycle          = property(lambda self: self.load()._cycle)
    hours          = property(lambda self: self.load()._hours)
    category_id    = property(lambda self: self.load()._category_id)
    speciality_id  = property(lambda self: self.load()._speciality_id)
    status         = property(lambda self: self.load()._status)
    documentType_id = property(lambda self: self.load()._documentType_id)
    educationDocumentSerial = property(lambda self: self.load()._educationDocumentSerial)
    educationDocumentNumber = property(lambda self: self.load()._educationDocumentNumber)
    educationDocumentOrigin = property(lambda self: self.load()._educationDocumentOrigin)
    validFromDate  = property(lambda self: self.load()._validFromDate)
    validToDate    = property(lambda self: self.load()._validToDate)


class CPersonAwardsInfoList(CInfoList):
    def __init__(self, context, masterId):
        CInfoList.__init__(self, context)
        self.masterId = masterId

    def _load(self):
        db = QtGui.qApp.db
        tablePersonAwards = db.table('Person_Awards')
        idList = db.getIdList(tablePersonAwards, 'id', db.joinAnd([tablePersonAwards['master_id'].eq(self.masterId), tablePersonAwards['deleted'].eq(0)]), 'id')
        self._items = [ self.getInstance(CPersonAwardsInfo, id) for id in idList ]
        return True


class CPersonAwardsInfo(CInfo):
    def __init__(self, context, awardId):
        CInfo.__init__(self, context)
        self.awardId = awardId
        self._awardNumber = None
        self._awardName = ''
        self._awardDate = None

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('Person_Awards', '*', 'WHERE id = %s AND `deleted` = 0' % self.awardId)
        if record:
            self._awardNumber = forceString(record.value('namber'))
            self._awardName = forceString(record.value('name'))
            self._awardDate = forceDate(record.value('date'))

    awardNumber        = property(lambda self: self.load()._awardNumber)
    awardName          = property(lambda self: self.load()._awardName)
    awardDate          = property(lambda self: self.load()._awardDate)

class CPersonOrderInfoList(CInfoList):
    def __init__(self, context, personId):
        CInfoList.__init__(self, context)
        self.personId = personId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('Person_Order')
        idList = db.getIdList(table, 'id',
                              db.joinAnd([table['master_id'].eq(self.personId),
                                          table['deleted'].eq(0)
                                         ]),
                              'id')
        self._items = [ self.getInstance(CPersonOrderInfo, id) for id in idList ]


class CPersonOrderInfo(CInfo):
    def __init__(self, context, orderId):
        CInfo.__init__(self, context)
        self.orderId = orderId
        self._date = CDateInfo()
        self._documentDate = CDateInfo()
        self._documentNumber = ''
        self._documentType = None
        self._validFromDate = CDateInfo()
        self._validToDate = CDateInfo()
        self._orgStructure = None
        self._post = None
        self._salary = ''

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('Person_Order')
        record = db.getRecord(table, '*', self.orderId)
        if record:
            self._date = CDateInfo(forceDate(record.value('date')))
            self._type = forceInt(record.value('type'))
            self._documentDate = CDateInfo(forceDate(record.value('documentDate')))
            self._documentNumber = forceString(record.value('documentNumber'))
            self._documentType = self.getInstance(CDocumentTypeInfo, forceRef(record.value('documentType_id')))
            self._validFromDate = CDateInfo(forceDate(record.value('validFromDate')))
            self._validToDate = CDateInfo(forceDate(record.value('validToDate')))
            self._orgStructure = self.getInstance(COrgStructureInfo, forceRef(record.value('orgStructure_id')))
            self._post = self.getInstance(CPostInfo, forceRef(record.value('post_id')))
            self._salary = forceString(record.value('salary'))
            return True
        return False


    def getTypeAsString(self):
        self.load()
        return (u'Приём на работу', u'Увольнение', u'Назначение на должность', u'Отпуск', u'Учёба', u'Командировка')[self._type]

#    def __unicode__(self):
    def __str__(self):
        self.load()
        return u'%s %s' % (self._date + self.getTypeAsString())


    date = property(lambda self: self.load()._date)
    type = property(lambda self: self.load()._type)
    typeAsString = property(getTypeAsString)
    documentDate = property(lambda self: self.load()._documentDate)
    documentNumber = property(lambda self: self.load()._documentNumber)
    documentType = property(lambda self: self.load()._documentType)
    validFromDate = property(lambda self: self.load()._validFromDate)
    validToDate = property(lambda self: self.load()._validToDate)
    orgStructure = property(lambda self: self.load()._orgStructure)
    post = property(lambda self: self.load()._post)
    salary = property(lambda self: self.load()._salary)


# NB! если CDocumentTypeInfo понадобится не только для врача, но и для пациента,
# то нужно будет создать подходящий модуль (что-нибуть типа Registry.CommonInfo) и перенести его туда.
class CDocumentTypeInfo(CRBInfo):
    tableName = 'rbDocumentType'
    def __init__(self, context, id):
        CRBInfo.__init__(self, context, id)


class CSpecialityInfo(CInfo):
    def __init__(self, context, specialityId):
        CInfo.__init__(self, context)
        self.specialityId = specialityId
        self._code = ''
        self._name = ''
        self._shortName = ''
        self._OKSOName = ''
        self._OKSOCode = ''
        self._service = self.getInstance(CServiceInfo, None)


    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('rbSpeciality', '*', self.specialityId)
        if record:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            self._shortName = forceString(record.value('shortName'))
            self._OKSOName = forceString(record.value('OKSOName'))
            self._OKSOCode = forceString(record.value('OKSOCode'))
            self._service = self.getInstance(CServiceInfo, forceRef(record.value('service_id')))
            return True
        else:
            return False


    def __str__(self):
        return self.load()._name

    code     = property(lambda self: self.load()._code)
    name     = property(lambda self: self.load()._name)
    shortName = property(lambda self: self.load()._shortName)
    OKSOName = property(lambda self: self.load()._OKSOName)
    OKSOCode = property(lambda self: self.load()._OKSOCode)
    service  = property(lambda self: self.load()._service)


class CPostInfo(CInfo):
    def __init__(self, context, postId):
        CInfo.__init__(self, context)
        self.postId = postId
        self._code = ''
        self._name = ''
        self._regionalCode = ''


    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('rbPost', '*', self.postId)
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


class CTariffCategoryInfo(CRBInfo):
    tableName = 'rbTariffCategory'
    def __init__(self, context, id):
        CRBInfo.__init__(self, context, id)
