# -*- coding: utf-8 -*-

from Exchange.R23.attach.Utils import CAttachPolicyType


class AddressInfo(object):
    def __init__(self, district=None, city=None, locality=None, street=None, house=None, corpus=None, flat=None):
        self.district = district
        self.city = city
        self.locality = locality
        self.street = street
        self.house = house
        self.corpus = corpus
        self.flat = flat


class DocumentInfo(object):
    def __init__(self, serial=None, number=None, type=None):
        self.serial = serial
        self.number = number
        self.type = type or 0


class PolicyInfo(object):
    def __init__(self, serial=None, number=None, type=None, insuranceArea=None, insurerCode=None, insurerOKATO=None, enp=None):
        self.serial = serial
        self.number = number
        self.type = type or 0
        self.enp = enp if enp else (number if type == CAttachPolicyType.New else None)
        self.insuranceArea = insuranceArea
        self.insurerCode = insurerCode
        self.insurerOKATO = insurerOKATO


class AttachInfo(object):
    def __init__(self, orgCode=None, sectionCode=None, begDate=None, endDate=None, attachType=None, doctorSNILS=None,
                 attachReason=None, deattachReason=None, deattachQuery=None, id=None):
        self.id = id
        self.orgCode = orgCode
        self.sectionCode = sectionCode
        self.begDate = begDate
        self.endDate = endDate
        self.attachType = attachType
        self.doctorSNILS = doctorSNILS
        self.attachReason = attachReason
        self.deattachReason = deattachReason
        self.deattachQuery = deattachQuery or DeAttachQuery()


class AttachedClientInfo(object):
    def __init__(self, lastName=None, firstName=None, patrName=None, birthDate=None, sex=0, SNILS=None, id=None,
                 doc=None, policy=None, attach=None, attaches=None, regAddress=None, locAddress=None):
        self.id = id
        self.lastName = lastName
        self.firstName = firstName
        self.patrName = patrName
        self.birthDate = birthDate
        self.sex = sex
        self.SNILS = SNILS
        self.document = doc or DocumentInfo()
        self.policy = policy or PolicyInfo()
        self.attach = attach or AttachInfo()
        self.attaches = attaches or ([attach] if attach is not None else [])
        self.regAddress = regAddress or AddressInfo()
        self.locAddress = locAddress or AddressInfo()
        self.contacts = None  # stub


class PersonAttachInfo(object):
    def __init__(self, id=None, orgCode=None, sectionCode=None, begDate=None, lastName=None, firstName=None, patrName=None,
                 birthDate=None, SNILS=None, specialityCode=None, category=None, attaches=None):
        self.id = id
        self.orgCode = orgCode
        self.sectionCode = sectionCode
        self.begDate = begDate
        self.lastName = lastName
        self.firstName = firstName
        self.patrName = patrName
        self.birthDate = birthDate
        self.SNILS = SNILS
        self.specialityCode = specialityCode
        self.category = category
        self.attaches = attaches or []


class DoctorSectionInfo(object):
    def __init__(self, sectionCode=None, begDate=None, id=None, doctorSNILS=None):
        self.id = id
        self.sectionCode = sectionCode
        self.begDate = begDate
        self.doctorSNILS = doctorSNILS


class AttachError(object):
    AttachesNotFound = 500
    PolicyError = 508
    DocumentError = 509
    NoAttachDate = 512
    NoAttachType = 513
    SectionNotFound = 517
    AttachTwiceAYear = 531
    ClientHasActualAttach = 548
    ClientHasAttachForThisMO = 552

    CriticalErrorPackageRejected = 1000
    NoErrorsPackageAccepted = 2000

    def __init__(self, code=None, message=None):
        self.code = code
        self.message = message

    def __unicode__(self):
        return u'{0}: {1}'.format(self.code, self.message) if self.code > 0 else self.message


class AttachResult(object):
    def __init__(self, result=None, errors=None, attachId=None):
        self.result = result
        self.errors = errors or []
        self.attachId = attachId

    def __nonzero__(self):
        return not self.hasErrors()

    def hasErrors(self):
        return bool(self.errors)

    def errorMessage(self):
        return u', '.join(unicode(error) for error in sorted(self.errors, key=lambda error: error.code))


class DeAttachQuery(object):
    def __init__(self, number=None, date=None, id=None, srcOrgCode=None, destOrgCode=None, client=None):
        self.id = id
        self.number = number
        self.date = date
        self.srcOrgCode = srcOrgCode
        self.destOrgCode = destOrgCode
        self.client = client
