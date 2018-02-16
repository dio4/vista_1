# -*- coding: utf-8 -*-
import datetime

from PyQt4.QtCore import QDate, QDateTime, QTime

from Exchange.R23.TFOMS.Utils import PolicyType, ResponsePackageCode
from library.Utils import databaseFormatSex, formatSex


class Serializeable(object):
    @staticmethod
    def toQDate(dt):
        if isinstance(dt, datetime.date):
            return QDate(dt.year, dt.month, dt.day) if dt else QDate()
        elif isinstance(dt, datetime.datetime):
            return Serializeable.toQDate(dt.date())
        return QDate()

    @staticmethod
    def toQDateTime(dt):
        if isinstance(dt, datetime.date):
            return QDateTime(Serializeable.toQDate(dt), QTime())
        elif isinstance(dt, datetime.datetime):
            return QDateTime(Serializeable.toQDate(dt), QTime(dt.hour, dt.minute, dt.second))
        return QDateTime()

    @staticmethod
    def toPyDate(dt):
        if isinstance(dt, QDate):
            return dt.toPyDate() if dt and dt.isValid() else None
        elif isinstance(dt, QDateTime):
            return Serializeable.toPyDate(dt.date())
        else:
            return None

    @staticmethod
    def toPyDateTime(dt):
        if isinstance(dt, QDate):
            d = dt.toPyDate() if dt and dt.isValid() else None
            return datetime.datetime.combine(d, datetime.time.min) if d else None
        elif isinstance(dt, QDateTime):
            return dt.toPyDateTime() if dt and dt.isValid() else None
        return None

    def serialize(self, factory):
        u"""
        :type factory: suds.client.Factory
        :rtype: suds.sudsobject.Object
        """
        raise NotImplementedError

    def deserialize(self, obj):
        u"""
        :type obj: suds.sudsobject.Object
        :rtype: cls
        """
        raise NotImplementedError


class ComplexType(Serializeable):
    _typeName = None

    def serialize(self, factory):
        u"""
        :type factory: suds.client.Factory
        :rtype: suds.sudsobject.Object
        """
        obj = self.createObject(factory)
        self.toSOAP(obj, factory)
        return obj

    def createObject(self, factory):
        return factory.create(self._typeName)

    def toSOAP(self, obj, factory):
        pass


class ItemList(ComplexType):
    itemType = Serializeable

    def __init__(self, attrName='', itemList=None):
        self._attrName = attrName
        self._items = itemList or []  # type: list[Serializeable]

    def toSOAP(self, obj, factory):
        setattr(obj, self._attrName, [item.serialize(factory) for item in self._items])

    def deserialize(self, obj):
        self._items = [
            self.itemType.deserialize(item)
            for item in getattr(obj, self._attrName, [])
        ]


class Identifiable(ComplexType):
    def __init__(self, rid=None):
        self.rid = rid

    def toSOAP(self, obj, factory):
        obj.rid = self.rid

    def deserialize(self, obj):
        self.rid = obj.rid


class Field(Serializeable):
    def __init__(self, fieldName):
        self._fieldName = fieldName


class LazyComplexType(Serializeable):
    fields = {}


class PersonItem(ComplexType):
    _typeName = 'cPerson'

    def __init__(self, lastName=u'', firstName=u'', patrName=u'', sex=None, birthDate=None, contacts=None,
                 policyType=None, policySerial=None, policyNumber=None, insurerCode=u'', insuranceArea=u'',
                 docType=None, docSerial=None, docNumber=u'', SNILS=None, ENP=None):
        self.lastName = lastName
        self.firstName = firstName
        self.patrName = patrName
        self.sex = sex
        self.birthDate = birthDate
        self.contacts = contacts
        self.policyType = policyType
        self.policySerial = policySerial
        self.policyNumber = policyNumber
        self.insurerCode = insurerCode
        self.insuranceArea = insuranceArea
        self.docType = docType
        self.docSerial = docSerial
        self.docNumber = docNumber
        self.SNILS = SNILS
        self.ENP = ENP or (policyNumber if policyNumber and policyType == PolicyType.New else None)

    @property
    def name(self):
        return u' '.join([self.lastName, self.firstName, self.patrName])

    def toSOAP(self, p, factory):
        p.a10_dct = self.policyType
        p.a11_dcs = self.policySerial
        p.a12_dcn = self.policyNumber
        p.a13_smcd = self.insurerCode
        p.a14_trcd = self.insuranceArea
        p.a15_pfio = self.lastName
        p.a16_pnm = self.firstName
        p.a17_pln = self.patrName
        p.a18_ps = formatSex(self.sex)
        p.a19_pbd = self.toPyDateTime(self.birthDate)
        p.a20_pph = self.contacts
        p.a21_ps = self.docSerial
        p.a22_pn = self.docNumber
        p.a23_dt = self.docType
        p.a24_sl = self.SNILS
        p.a25_enp = self.ENP

    @classmethod
    def deserialize(cls, obj):
        return cls(lastName=unicode(obj.a15_pfio),
                   firstName=unicode(obj.a16_pnm),
                   patrName=unicode(obj.a17_pln),
                   sex=databaseFormatSex(obj.a18_ps),
                   birthDate=cls.toQDate(obj.a19_pbd),
                   policyType=obj.a10_dct,
                   policySerial=unicode(obj.a11_dcs) or None,
                   policyNumber=unicode(obj.a12_dcn) or None,
                   insurerCode=unicode(obj.a13_smcd),
                   insuranceArea=unicode(obj.a14_trcd),
                   docType=obj.a23_dt,
                   docSerial=unicode(obj.a24_sl),
                   docNumber=unicode(obj.a22_pn),
                   SNILS=unicode(obj.a24_sl),
                   ENP=unicode(obj.a25_enp))

    def __repr__(self):
        return u'<PersonItem {0} {1} {2}>'.format(self.lastName, self.firstName, self.patrName)


class FLKError(ComplexType):
    _typeName = 'cflkError'

    def __init__(self, code=None, message=None, guid=None):
        self.code = code  # type: int
        self.message = message
        self.guid = guid

    @classmethod
    def deserialize(cls, obj):
        return cls(
            code=obj.e10_ecd,
            message=unicode(obj.e11_ems),
            guid=unicode(obj.e12_iguid)
        )

    @property
    def text(self):
        return u'{0}: {1}'.format(self.code, self.message)

    def __repr__(self):
        return u'<FLKError {0}>'.format(self.text)


class OrderError(ComplexType):
    _typeName = 'cOrdersFLKError'

    def __init__(self, orderId=None, errorList=None):
        self.id = orderId
        self.errorList = errorList  # type: list[FLKError]

    @property
    def flkErrors(self):
        return u','.join(error.text for error in self.errorList)

    @property
    def text(self):
        return u'{0}{1}'.format(u'[%s]: ' % self.id if (self.id is not None and self.id > 0) else u'',
                                u', '.join(error.text for error in self.errorList))

    @classmethod
    def deserialize(cls, obj):
        return cls(
            orderId=obj.f10_nzap,
            errorList=[FLKError.deserialize(error) for error in obj.f11_flkerrorList.f10_flkerror] if obj.f11_flkerrorList else []
        )

    def __repr__(self):
        return u'<OrderError id:{0}, {1} errors>'.format(self.id, len(self.errorList))


class PackageInfo(ComplexType):
    _typeName = 'cPackageInformation'


class ResponseInfo(ComplexType):
    _typeName = 'cResponceInformation'

    def __init__(self, srcGUID=None, responseCode=None, responseMsg=None):
        self.srcGUID = srcGUID
        self.responseCode = responseCode
        self.responseMsg = responseMsg

    @property
    def codeMessage(self):
        return u'{0}: {1}'.format(self.responseCode, self.responseMsg)

    @classmethod
    def deserialize(cls, obj):
        return cls(
            srcGUID=unicode(obj.pakageGUIDSrc),
            responseCode=obj.r10_responcecode,
            responseMsg=unicode(obj.responceMessage)
        )

    def __repr__(self):
        return u'<ResponseInfo {0}>'.format(self.codeMessage)


class ResponsePackage(ComplexType):
    _typeName = 'cResponceOrdersPackage'

    def __init__(self, packageInfo=None, responseInfo=None, orderErrors=None):
        self.packageInfo = packageInfo
        self.responseInfo = responseInfo  # type: ResponseInfo
        self.orderErrors = orderErrors or []  # type: list[OrderError]

    @classmethod
    def deserialize(cls, obj):
        return cls(
            packageInfo=None,
            responseInfo=ResponseInfo.deserialize(obj.r11_rsinf),
            orderErrors=[OrderError.deserialize(error) for error in obj.r12_orerl.f10_orflker] if obj.r12_orerl else []
        )

    @property
    def rejectedOrders(self):
        return [order.id for order in self.orderErrors if order.id > 0]

    @property
    def errorMessage(self):
        return u';\n'.join([self.responseInfo.codeMessage] +
                           [orderError.text for orderError in self.orderErrors])

    @property
    def accepted(self):
        return self.responseInfo.responseCode == ResponsePackageCode.Accepted

    @property
    def hasErrors(self):
        return self.responseInfo.responseCode == ResponsePackageCode.HasErrors

    @property
    def rejected(self):
        return self.responseInfo.responseCode in (ResponsePackageCode.Rejected,
                                                  ResponsePackageCode.UnknownPackageError)

    def __repr__(self):
        return u'<ResponsePackage: {0}, {1} errors>'.format(self.responseInfo, len(self.orderErrors))
