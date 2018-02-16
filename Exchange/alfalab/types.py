# -*- coding: utf-8 -*-

import itertools
from PyQt4 import QtCore
from xml.etree import ElementTree

from library.Utils import forceDouble, forceInt, forceString, nameCase


class attrType(object):
    def __init__(self, value=None):
        self._value = value

    def fromXML(self, value):
        self._value = self.toPyValue(value)

    def toXML(self):
        return self.toXMLValue(self._value)

    @staticmethod
    def toXMLValue(value):
        return value

    @staticmethod
    def toPyValue(value):
        return value

    @classmethod
    def createFromElement(cls, value):
        return cls(cls.toPyValue(value))


class attrString(attrType):
    @staticmethod
    def toPyValue(value):
        return forceString(value)

    @staticmethod
    def toXMLValue(value):
        return forceString(value)


class attrName(attrType):
    @staticmethod
    def toPyValue(value):
        return nameCase(forceString(value))

    @staticmethod
    def toXMLValue(value):
        return nameCase(forceString(value))


class attrInt(attrType):
    @staticmethod
    def toPyValue(value):
        return forceInt(value)

    @staticmethod
    def toXMLValue(value):
        return forceString(value)


class attrFloat(attrType):
    @staticmethod
    def toPyValue(value):
        return forceDouble(value)

    @staticmethod
    def toXMLValue(value):
        return forceString(value)


class attrBool(attrType):
    @staticmethod
    def toPyValue(value):
        return forceString(value) == 'true'

    @staticmethod
    def toXMLValue(value):
        return 'true' if value else 'false'


class attrDate(attrType):
    format = 'dd.MM.yyyy 00:00:00'

    @staticmethod
    def toPyValue(value):
        return QtCore.QDate.fromString(value, attrDate.format) if value else QtCore.QDate()

    @staticmethod
    def toXMLValue(value):
        return forceString(value.toString(attrDate.format)) if value else ''


class attrDatetime(attrType):
    format = 'dd.MM.yyyy hh:mm:ss'

    @staticmethod
    def toPyValue(value):
        return QtCore.QDateTime.fromString(value, attrDatetime.format) if value else QtCore.QDateTime()

    @staticmethod
    def toXMLValue(value):
        return forceString(value.toString(attrDatetime.format)) if value else ''


class alfaType(object):
    attribs = {}
    children = {}

    def __init__(self, name=None, *args, **kwargs):
        self._name = name
        self._avalues = dict((aname, kwargs.get(aname, None)) for aname in self.attribs)
        self._cvalues = dict((cname, kwargs.get(cname, None) or ctype()) for cname, ctype in self.children.iteritems())

    def fromElement(self, element):
        avalues = {}
        for aname, atype in self.attribs.iteritems():
            attrValue = element.get(aname)
            avalues[aname] = atype.toPyValue(attrValue) if attrValue is not None else None
        self._avalues = avalues
        self._cvalues = dict((cname, ctype.createFromElement(element.find(cname)))
                             for cname, ctype in self.children.iteritems())

    def toElement(self):
        attrib = {}
        for aname, atype in self.attribs.iteritems():
            attrValue = self._avalues.get(aname)
            if attrValue is not None:
                attrib[aname] = atype.toXMLValue(attrValue)

        element = ElementTree.Element(self._name, attrib=attrib)
        for ename, etype in self.children.iteritems():
            elemValue = self._cvalues.get(ename)
            if elemValue:
                element.append(elemValue.toElement())

        return element

    def toString(self):
        return ElementTree.tostring(self.toElement(), 'utf-8')

    def __str__(self):
        return str(self.toString())

    def __unicode__(self):
        return unicode(self.toString())

    @classmethod
    def createFromElement(cls, element):
        result = cls()
        if element is not None:
            result.fromElement(element)
        return result

    def __getattr__(self, item):
        if item in self._avalues:
            return self._avalues.get(item)
        if item in self._cvalues:
            return self._cvalues.get(item)
        return self.__dict__.get(item, None)

    def __setattr__(self, key, value):
        if key in self.attribs:
            self._avalues[key] = value
        if key in self.children:
            self._cvalues[key] = value
        self.__dict__[key] = value

    def __nonzero__(self):
        return any(itertools.imap(bool, self._avalues.itervalues())) or \
               any(itertools.imap(bool, self._cvalues.itervalues()))


class Message(alfaType):
    attribs = {
        'Date'       : attrDatetime,
        'MessageType': attrString,
        'Receiver'   : attrString,
        'Sender'     : attrString,
        'Password'   : attrString,
        'Error'      : attrString
    }

    def __init__(self, messageType=None, **kwargs):
        alfaType.__init__(self, 'Message', MessageType=messageType, Date=QtCore.QDateTime.currentDateTime(), **kwargs)


class ReferralQuery(alfaType):
    attribs = {
        'LisId': attrInt,
        'Nr'   : attrString,
        'MisId': attrString
    }

    def __init__(self, num=None, id=None, lisId=None):
        alfaType.__init__(self, 'Query', LisId=lisId, Nr=num, MisId=id)


class Query(alfaType):
    attribs = {
        'LisId': attrInt,
        'Nr'   : attrString,
        'MisId': attrString
    }

    def __init__(self, num=None, id=None, lisId=None):
        alfaType.__init__(self, 'Query', LisId=lisId, Nr=num, MisId=id)


class Version(alfaType):
    attribs = {
        'Version': attrInt
    }

    def __init__(self, version=None):
        alfaType.__init__(self, 'Version', Version=version)


class Patient(alfaType):
    attribs = {
        'LastName'  : attrName,
        'FirstName' : attrName,
        'MiddleName': attrName,
        'BirthDate' : attrDate,
        'Gender'    : attrInt,
        'MisId'     : attrString,
        'Code1'     : attrString
    }

    def __init__(self, lastName=None, firstName=None, patrName=None, birthDate=None, sex=None, id=None):
        alfaType.__init__(self, 'Patient',
                          LastName=lastName, FirstName=firstName, MiddleName=patrName,
                          BirthDate=birthDate, Gender=sex, MisId=id, Code1=id)


class Item(alfaType):
    def __init__(self, *args, **kwargs):
        alfaType.__init__(self, 'Item', *args, **kwargs)


class ItemList(alfaType):
    itemType = Item

    def __init__(self, name=None, items=None, *args, **kwargs):
        alfaType.__init__(self, name, *args, **kwargs)
        self._items = items if items is not None else []

    def fromElement(self, element):
        alfaType.fromElement(self, element)
        self._items = map(self.itemType.createFromElement, element)

    def toElement(self):
        element = alfaType.toElement(self)
        element.extend(item.toElement() for item in self._items)
        return element

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return self._items.__iter__()

    def __getitem__(self, index):
        return self._items[index]

    def __nonzero__(self):
        return bool(self._items)


class OrdersItem(Item):
    attribs = {
        'BiomaterialCode': attrString,
        'Code'           : attrString,
        'PlaceCode'      : attrString,
        'State'          : attrInt
    }

    def __init__(self, bmCode=None, code=None, state=None):
        Item.__init__(self, BiomaterialCode=bmCode, Code=code, State=state)


class OrdersList(ItemList):
    itemType = OrdersItem

    def __init__(self, *args, **kwargs):
        ItemList.__init__(self, 'Orders', *args, **kwargs)


class ReferralResult(alfaType):
    attribs = {
        'LisId'         : attrInt,
        'Nr'            : attrString,
        'MisId'         : attrString,
        'Activated'     : attrInt,
        'CreateDate'    : attrDatetime,
        'Date'          : attrDatetime,
        'DeliveryDate'  : attrDatetime,
        'DepartmentCode': attrString,
        'DepartmentName': attrString,
        'DoctorCode'    : attrString,
        'DoctorName'    : attrString,
        'Done'          : attrBool,
        'DoneDate'      : attrDatetime,
        'HospitalCode'  : attrString,
        'Manual'        : attrBool,
        'SamplingDate'  : attrDatetime
    }
    children = {
        'Orders': OrdersList
    }

    def __init__(self, *args, **kwargs):
        alfaType.__init__(self, 'Referral', *args, **kwargs)


class DrugsItem(Item):
    attribs = {
        'Code'     : attrString,
        'MIC'      : attrString,
        'Name'     : attrString,
        'Value'    : attrString,
        'ValueDate': attrDatetime
    }


class DrugsList(ItemList):
    itemType = DrugsItem

    def __init__(self, *args, **kwargs):
        ItemList.__init__(self, 'Drugs', *args, **kwargs)


class MicroorganismsItem(Item):
    attribs = {
        'Code' : attrString,
        'Name' : attrString,
        'Value': attrString
    }
    children = {
        'Drugs': DrugsList
    }


class MicroorganismsList(ItemList):
    itemType = MicroorganismsItem

    def __init__(self, *args, **kwargs):
        ItemList.__init__(self, 'Microorganisms', *args, **kwargs)


class TestsItem(Item):
    attribs = {
        'AssistantCode'  : attrString,
        'AssistantName'  : attrString,
        'Barcode'        : attrString,
        'BiomaterialCode': attrString,
        'Code'           : attrString,
        'Comment'        : attrString,
        'Defects'        : attrString,
        'DoctorCode'     : attrString,
        'DoctorName'     : attrString,
        'Name'           : attrString,
        'Norms'          : attrString,
        'NormsComment'   : attrString,
        'NormsFlag'      : attrInt,
        'OrderCode'      : attrString,
        'Source'         : attrString,
        'UnitName'       : attrString,
        'Value'          : attrString,
        'ValueDate'      : attrDatetime
    }
    children = {
        'Microorganisms': MicroorganismsList
    }


class TestsList(ItemList):
    itemType = TestsItem

    def __init__(self, *args, **kwargs):
        ItemList.__init__(self, 'Tests', *args, **kwargs)


class BlanksItem(Item):
    attribs = {
        'BlankGUID': attrString,
        'BlankId'  : attrString,
        'BlankType': attrInt,
        'Comment'  : attrString,
        'Done'     : attrBool,
        'DoneDate' : attrDatetime,
        'FileName' : attrString,
        'Groups'   : attrString,
        'Name'     : attrString,
        'Version'  : attrInt
    }
    children = {
        'Tests': TestsList
    }


class Blanks(ItemList):
    itemType = BlanksItem

    def __init__(self, *args, **kwargs):
        ItemList.__init__(self, 'Blanks', *args, **kwargs)


class ReferralResultsRequest(Message):
    children = {
        'Query': Query
    }

    def __init__(self, referral=None, **kwargs):
        Message.__init__(self, 'query-referral-results', Query=referral, **kwargs)


class ReferralResultsResponse(Message):
    children = {
        'Version' : Version,
        'Patient' : Patient,
        'Referral': ReferralResult,
        'Blanks'  : Blanks
    }


class NextReferralRequest(Message):
    def __init__(self, **kwargs):
        Message.__init__(self, 'query-next-referral-results', **kwargs)


class WarningsItem(Item):
    attribs = {
        'Text': attrString
    }


class WarningsList(ItemList):
    itemType = WarningsItem

    def __init__(self, *args, **kwargs):
        ItemList.__init__(self, 'Warnings', *args, **kwargs)


class ImportReferralResponse(Message):
    children = {
        'Referral': ReferralQuery,
        'Warnings': WarningsList
    }


class Referral(alfaType):
    attribs = {
        'MisId'            : attrString,
        'LisId'            : attrInt,
        'Nr'               : attrString,
        'Date'             : attrDatetime,
        'SamplingDate'     : attrDatetime,
        'DeliveryDate'     : attrDate,
        'HospitalCode'     : attrString,
        'DepartmentCode'   : attrString,
        'DepartmentName'   : attrString,
        'DoctorCode'       : attrString,
        'DoctorName'       : attrString,
        'Cito'             : attrBool,
        'DiagnosisCode'    : attrString,
        'DiagnosisName'    : attrString,
        'Comment'          : attrString,
        'PregnancyWeek'    : attrInt,
        'CyclePeriod'      : attrInt,
        'LastMenstruation' : attrDate,
        'DiuresisMl'       : attrInt,
        'WeightKg'         : attrFloat,
        'HeightCm'         : attrInt,
        'PayCategoryCode'  : attrString,
        'PayCategoryName'  : attrString,
        'pay_category_code': attrString
    }
    children = {
        'Orders': OrdersList
    }

    def __init__(self, *args, **kwargs):
        alfaType.__init__(self, 'Referral', *args, **kwargs)


class AssaysItem(Item):
    attribs = {
        'Barcode'        : attrString,
        'BiomaterialCode': attrString
    }
    children = {
        'Orders': OrdersList
    }


class AssaysList(ItemList):
    itemType = AssaysItem

    def __init__(self, *args, **kwargs):
        ItemList.__init__(self, 'Assays', *args, **kwargs)


class CreateReferralRequest(Message):
    children = {
        'Patient' : Patient,
        'Referral': Referral,
        'Assays'  : AssaysList
    }

    def __init__(self, patient=None, referral=None, **kwargs):
        Message.__init__(self, 'query-create-referral', Patient=patient, Referral=referral, **kwargs)


class EditReferralRequest(Message):
    children = {
        'Patient' : Patient,
        'Referral': Referral,
        'Assays'  : AssaysList
    }

    def __init__(self, patient=None, referral=None, assays=None, **kwargs):
        Message.__init__(self, 'query-edit-referral', Patient=patient, Referral=referral, Assays=assays, **kwargs)


class RemoveReferralRequest(Message):
    children = {
        'Query': ReferralQuery
    }

    def __init__(self, query=None, **kwargs):
        Message.__init__(self, 'query-referral-remove', Query=query, **kwargs)


class BlankFileQuery(alfaType):
    attribs = {
        'BlankId'  : attrString,
        'BlankGUID': attrString
    }

    def __init__(self, **kwargs):
        alfaType.__init__(self, 'Query', **kwargs)


class BlankFileQueryRequest(Message):
    children = {
        'Query': BlankFileQuery
    }

    def __init__(self, blank=None, **kwargs):
        Message.__init__(self, 'query-blank-file', Query=blank, **kwargs)


class ConfirmReferralResultsRequest(Message):
    children = {
        'Query'  : ReferralQuery,
        'Version': Version
    }

    def __init__(self, **kwargs):
        Message.__init__(self, 'result-referral-results-import', **kwargs)


class DictionariesVersionRequest(Message):
    def __init__(self, **kwargs):
        Message.__init__(self, 'query-dictionaries-version', **kwargs)


class DictionariesVersionResponse(Message):
    children = {
        'Version': Version
    }


class DictionariesRequest(Message):
    def __init__(self, **kwargs):
        Message.__init__(self, 'query-dictionaries', **kwargs)


class DictionariesResponse(Message):
    # не загружаем номенклатуру из ЛИС
    pass
