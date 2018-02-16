# -*- coding: utf-8 -*-
import datetime
from collections import defaultdict
from decimal import Decimal

from PyQt4.QtCore import QDate, QDateTime

from library.Enum import CEnum
from library.Utils import forceString


class Base(object):
    def toJSON(self):
        return {}

    def fromJSON(self, dct):
        if dct is not None:
            self._fromJSON(dct)
        return self

    def _fromJSON(self, dct):
        pass

    @staticmethod
    def dateFromJSON(strDate):
        pyDate = datetime.datetime.strptime(strDate, "%Y-%m-%d").date() if strDate else None
        return QDate(pyDate.year, pyDate.month, pyDate.day) if pyDate else QDate()

    @staticmethod
    def dateToJSON(date):
        u"""
        :type date: QDate
        """
        return forceString(date.toString('yyyy-MM-dd'))

    @staticmethod
    def datetimeToJSON(datetime):
        u"""
        :type datetime: QDateTime
        """
        return forceString(datetime.toString('yyyy-MM-ddThh:mm:ss'))

    @staticmethod
    def datetimeFromJSON(strDatetime):
        try:
            pyDT = datetime.datetime.strptime(strDatetime, "%Y-%m-%dT%H:%M:%S.%fZ") if strDatetime else None
        except ValueError:
            pyDT = datetime.datetime.strptime(strDatetime, "%Y-%m-%dT%H:%M:%SZ") if strDatetime else None
        return QDateTime(pyDT.year, pyDT.month, pyDT.day, pyDT.hour, pyDT.minute, pyDT.second) if pyDT else QDateTime()

    @classmethod
    def createFromJSON(cls, dct):
        return cls().fromJSON(dct)


class Item(Base):
    def __init__(self, itemId=None):
        self.id = itemId

    @property
    def saved(self):
        return self.id is not None

    def _fromJSON(self, dct):
        self.id = dct.get('id')

    def toJSON(self):
        dct = {}
        if self.id:
            dct['id'] = self.id
        return dct


class UpdateableItem(Item):
    def __init__(self, *args, **kwargs):
        super(UpdateableItem, self).__init__(*args, **kwargs)
        self.changed = False
        self.markedToDelete = False

    def updateFrom(self, other):
        u"""
        :type other: UpdateableItem
        """
        pass


class RbItem(Item):
    reference = 'reference'
    displayName = u'Справочник'

    def __init__(self, itemId=None, code='', name=''):
        super(RbItem, self).__init__(itemId)
        self.code = code
        self.name = name

    @property
    def codeName(self):
        return u'{0} | {1}'.format(self.code, self.name) if self.code or self.name else u''

    def _fromJSON(self, dct):
        super(RbItem, self)._fromJSON(dct)
        self.code = dct.get('code')
        self.name = dct.get('name')

    def toJSON(self):
        res = super(RbItem, self).toJSON()
        if self.code:
            res['code'] = self.code
        if self.name:
            res['name'] = self.name
        return res

    def __repr__(self):
        return u'<RbItem({0}) {1}>'.format(self.reference, self.codeName)


class OrganisationType(RbItem):
    reference = 'organisation_type'
    displayName = u'Тип организации'


class MeasurementUnit(RbItem):
    reference = 'measurement_unit'
    displayName = u'Единица измерения'


class FundSource(RbItem):
    reference = 'fund_source'
    displayName = u'Тип финансирования'


class Catalog(Item):
    def __init__(self, itemId=None, name='', description='', nameTemplate='', fields=None):
        super(Catalog, self).__init__(itemId)
        self.name = name
        self.description = description
        self.nameTemplate = nameTemplate
        self.fields = fields or {}

    def _fromJSON(self, dct):
        super(Catalog, self)._fromJSON(dct)
        self.name = dct.get('name')
        self.description = dct.get('description')
        self.nameTemplate = dct.get('name_template')
        self.fields = dct.get('fields', {})

    def toJSON(self):
        res = super(Catalog, self).toJSON()
        res.update({
            'name'         : self.name,
            'desciption'   : self.description,
            'name_template': self.nameTemplate,
            'fields'       : self.fields
        })
        return res

    def __repr__(self):
        return u'<Catalog {0} ({1})>'.format(self.name, self.description, self.fields)


class CatalogField(Item):
    def __init__(self, fieldId=None, code='', name='', catalog=None, fieldType=None, isPrimary=False, valueDomain=''):
        super(CatalogField, self).__init__(fieldId)
        self.code = code
        self.name = name
        self.catalog = catalog
        self.type = fieldType
        self.isPrimary = isPrimary
        self.valueDomain = valueDomain

    def _fromJSON(self, dct):
        super(CatalogField, self)._fromJSON(dct)
        self.code = dct.get('code')
        self.name = dct.get('name')
        self.catalog = dct.get('catalog')
        self.type = dct.get('type')
        self.isPrimary = dct.get('is_primary', False)
        self.valueDomain = dct.get('value_domain', '')

    def toJSON(self):
        res = super(CatalogField, self).toJSON()
        res.update({
            'code'        : self.code,
            'name'        : self.name,
            'catalog'     : self.catalog,
            'type'        : self.type,
            'is_primary'  : self.isPrimary,
            'value_domain': self.valueDomain
        })
        return res

    def __repr__(self):
        return u'<CatalogField {0}|{1}, type: {2}, isPrimary: {3}, valueDomain: {4}>'.format(
            self.code, self.name, self.type, self.isPrimary, self.valueDomain
        )


class Field(CEnum):
    INN = 'INN'
    ATC = 'ATC'
    Manufacturer = 'Manufacturer'
    Dosage = 'Dosage'
    # TradeName = 'TradeName'
    # Class = 'Class'

    nameMap = {
        INN         : u'МНН',  # Международное непатентованное наименование
        ATC         : u'АТХ',  # Анатомо-терапевтическо-химическая классификация
        Manufacturer: u'Фирма-производитель',
        Dosage      : u'Дозировка',
        # TradeName   : u'Торговое наименование',
        # Class       : u'Класс товара',
    }


class CatalogItem(Item):
    u""" Запись в каталоге """

    def __init__(self, catalogItemId=None, catalog=None, name=None, unit=None, fields=None):
        super(CatalogItem, self).__init__(catalogItemId)
        self.catalog = catalog
        self.name = name
        self.unit = unit
        self.fields = fields or {}

    @property
    def tradeName(self):
        return self.name  # self.fields.get(Field.TradeName, u'')

    @property
    def INN(self):
        return self.fields.get(Field.INN) or u''

    @property
    def ATC(self):
        return self.fields.get(Field.ATC) or u''

    @property
    def manufacturer(self):
        return self.fields.get(Field.Manufacturer) or u''

    @property
    def dosage(self):
        return self.fields.get(Field.Dosage) or u''

    def _fromJSON(self, dct):
        super(CatalogItem, self)._fromJSON(dct)
        self.catalog = dct.get('catalog')
        self.name = dct.get('name')
        self.unit = dct.get('unit')
        self.fields = dct.get('fields', {})

    def toJSON(self):
        res = super(CatalogItem, self).toJSON()
        res.update({
            'catalog': self.catalog,
            'name'   : self.name,
            'unit'   : self.unit,
            'fields' : self.fields
        })
        return res

    def __repr__(self):
        return u'<CatalogItem "{0}", unit: {1}, catalog: {2}>'.format(self.name, self.unit, self.catalog)


class Store(Item):
    u""" Склад """

    def __init__(self, storeId=None, name=u''):
        super(Store, self).__init__(storeId)
        self.name = name

    def _fromJSON(self, dct):
        super(Store, self)._fromJSON(dct)
        self.name = dct.get('name', u'')

    def toJSON(self):
        res = super(Store, self).toJSON()
        res['name'] = self.name
        return res

    def __repr__(self):
        return u'<Store {0}: "{1}">'.format(self.id, self.name)


class StoreItem(Item):
    u""" Партия на складе """

    def __init__(self, itemId=None, catalogItem=None, productionDate=None, arrivalDate=None, expiryDate=None, price=None, serial=''):
        super(StoreItem, self).__init__(itemId)
        self.catalogItem = catalogItem  # type: CatalogItem
        self.productionDate = productionDate
        self.arrivalDate = arrivalDate
        self.expiryDate = expiryDate
        self.price = price
        self.serial = serial

    @property
    def tradeName(self):
        return self.catalogItem.tradeName if self.catalogItem else u''

    @property
    def INN(self):
        return self.catalogItem.INN if self.catalogItem else u''

    @property
    def dosage(self):
        return self.catalogItem.dosage if self.catalogItem else u''

    @property
    def ATC(self):
        return self.catalogItem.ATC if self.catalogItem else u''

    @property
    def manufacturer(self):
        return self.catalogItem.manufacturer if self.catalogItem else None

    @property
    def unit(self):
        return self.catalogItem.unit if self.catalogItem else None

    def _fromJSON(self, dct):
        super(StoreItem, self)._fromJSON(dct)
        self.catalogItem = CatalogItem().fromJSON(dct.get('catalog_item', {}))
        self.productionDate = self.dateFromJSON(dct.get('production_date'))
        self.arrivalDate = self.dateFromJSON(dct.get('arrival_date'))
        self.expiryDate = self.dateFromJSON(dct.get('expiry_date'))
        self.price = Decimal(dct.get('price') or 0)
        self.serial = dct.get('serial', '')

    def toJSON(self):
        res = super(StoreItem, self).toJSON()
        res.update({
        })
        # TODO: fill

    def __repr__(self):
        return u'<StoreItem price: {0}, catalog item: {1}>'.format(self.price, self.catalogItem)


class StoreStockItem(Item):
    def __init__(self, itemId=None, store=None, amount=0, storeItem=None):
        super(StoreStockItem, self).__init__(itemId)
        self.store = store
        self.amount = amount
        self.item = storeItem  # type: StoreItem

    @property
    def itemId(self):
        return self.item.id if self.item else None

    @property
    def tradeName(self):
        return self.item.tradeName if self.item else u''

    @property
    def dosage(self):
        return self.item.dosage if self.item else u''

    @property
    def INN(self):
        return self.item.INN if self.item else u''

    @property
    def ATC(self):
        return self.item.ATC if self.item else u''

    @property
    def manufacturer(self):
        return self.item.manufacturer if self.item else None

    @property
    def catalogFields(self):
        fields = self.item.catalogItem.fields if self.item and self.item.catalogItem else {}
        return unicode(fields) if fields else u''

    @property
    def catalogItemId(self):
        return self.item.catalogItem.id if self.item and self.item.catalogItem else None

    @property
    def expiryDate(self):
        return self.item.expiryDate if self.item else None

    @property
    def unit(self):
        return self.item.unit if self.item else None

    def _fromJSON(self, dct):
        super(StoreStockItem, self)._fromJSON(dct)
        self.store = int(dct.get('store', 0))
        self.amount = dct.get('amount', 0)
        self.item = StoreItem().fromJSON(dct.get('item', {}))

    def __repr__(self):
        return u'<StoreStockItem store: {0}, amount: {1}, item: {2}>'.format(self.store, self.amount, self.item)


class Organisation(Item):
    def __init__(self, orgId=None, fullName=u'', shortName=u'', INN=u'', infis=u'', address=u'', phone=u'', orgType=None):
        super(Organisation, self).__init__(orgId)
        self.fullName = fullName
        self.shortName = shortName
        self.INN = INN
        self.infis = infis
        self.address = address
        self.phone = phone
        self.type = orgType  # type: OrganisationType

    def _fromJSON(self, dct):
        super(Organisation, self)._fromJSON(dct)
        self.fullName = dct.get('full_name', u'')
        self.shortName = dct.get('short_name', u'')
        self.INN = dct.get('inn', u'')
        self.infis = dct.get('infis', u'')
        self.address = dct.get('address', u'')
        self.phone = dct.get('phone', u'')
        self.type = OrganisationType().fromJSON(dct.get('type', {}))

    def toJSON(self):
        dct = super(Organisation, self).toJSON()
        dct.update({
            'full_name' : self.fullName,
            'short_name': self.shortName,
            'inn'       : self.INN,
            'infis'     : self.infis,
            'address'   : self.address,
            'phone'     : self.phone,
            'type_id'   : self.type.id
        })
        return dct

    @property
    def typeName(self):
        return self.type.name if self.type else u''

    def __repr__(self):
        return u'<Organisation "{0}", inn: {1}, type: {2}>'.format(self.shortName, self.INN, self.type.name)


class ItemList(Base):
    def __init__(self, itemType):
        self._itemType = itemType
        self._values = []

    def _fromJSON(self, dct):
        self._values = [self._itemType().fromJSON(item) for item in dct] if dct else []

    def toJSON(self):
        return [item.toJSON() for item in self._values]

    def values(self):
        return self._values

    def __iter__(self):
        return iter(self._values)

    def __len__(self):
        return len(self._values)

    def __getitem__(self, item):
        return self._values[item]

    def __repr__(self):
        return u'<ItemList({0}): {1} items>'.format(self._itemType.__name__, len(self))


class ResultList(ItemList):
    def __init__(self, itemType, count=0, nxt=None, prev=None, pageCount=0):
        super(ResultList, self).__init__(itemType)
        self.count = count
        self.next = nxt
        self.prev = prev
        self.pageCount = pageCount

    def _fromJSON(self, dct):
        super(ResultList, self)._fromJSON(dct.get('results', []))
        self.count = dct.get('count', 0)
        self.next = dct.get('next')
        self.prev = dct.get('previous')
        self.pageCount = dct.get('page_count', 0)

    def __repr__(self):
        return u'<ResultList({0}), count: {1}, pageCount: {2}, prev: {3}, next: {4}>'.format(
            self._itemType.__name__, self.count, self.pageCount, self.prev, self.next
        )


class User(Item):
    def __init__(self, userId=None, username='', lastName='', firstName='', patrName='', isActive=False):
        super(User, self).__init__(userId)
        self.username = username
        self.lastName = lastName
        self.firstName = firstName
        self.patrName = patrName
        self.isActive = isActive
        self.permissions = set()

    def hasPermission(self, permission):
        return permission in self.permissions

    def hasAnyPermission(self, permissions):
        return bool(set(permissions).intersection(self.permissions))

    @property
    def shortName(self):
        return u'{0} {1}.{2}.'.format(self.lastName, self.firstName[:1], self.patrName[:1])

    @property
    def fullName(self):
        return u' '.join(filter(bool, [self.lastName, self.firstName, self.patrName])) or u'ФИО не заданы'

    def toJSON(self):
        return {}

    def _fromJSON(self, dct):
        super(User, self)._fromJSON(dct)
        self.username = dct.get('username', '')
        self.lastName = dct.get('last_name', '')
        self.firstName = dct.get('first_name', '')
        self.patrName = dct.get('patr_name', '')
        self.isActive = dct.get('is_active', False)
        self.permissions = set(dct.get('user_permissions', []))

    def __repr__(self):
        return u'<User {0}, {1} {2} {3}>'.format(self.username, self.lastName, self.firstName, self.patrName)


class BaseDocument(UpdateableItem):
    def __init__(self, docId=None, date=None, user=None, finalized=False, finalizeDate=None, finalizeUser=None):
        super(BaseDocument, self).__init__(docId)
        self.date = date  # type: QDateTime
        self.user = user
        self.finalized = finalized
        self.finalizeDate = finalizeDate
        self.finalizeUser = finalizeUser
        self.items = []

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, idx):
        return self.items[idx]

    def getStoreItemDelta(self, storeId=None):
        u"""
        Изменения на складе по каждой партии товара
        :param storeId: Склад, для которого подсчитываются изменения (если не задано, подразумевается склад-источник)
        :rtype: defaultdict
        """
        raise NotImplementedError

    def _fromJSON(self, dct):
        super(BaseDocument, self)._fromJSON(dct)
        self.date = self.datetimeFromJSON(dct.get('date'))
        self.user = dct.get('user')
        self.finalized = dct.get('finalized', False)
        self.finalizeUser = dct.get('finalize_user')
        self.finalizeDate = self.datetimeFromJSON(dct.get('finalize_date'))

    def toJSON(self):
        res = super(BaseDocument, self).toJSON()
        if self.date:
            res['date'] = self.datetimeToJSON(self.date)
        res['user'] = self.user
        res['finalized'] = self.finalized
        res['finalize_user'] = self.finalizeUser
        if self.finalizeDate:
            res['finalize_date'] = self.datetimeToJSON(self.finalizeDate)
        return res


class ShippingDocument(BaseDocument):
    def __init__(self, docId=None, date=None, user=None, finalized=False, finalizeDate=None, finalizeUser=None,
                 internalNumber=None, externalNumber=None, invoiceNumber=None, supplier=None, shipper=None, reason=None,
                 fundSource=None, organisation=None, store=None):
        super(ShippingDocument, self).__init__(docId, date, user, finalized, finalizeDate, finalizeUser)
        self.internalNumber = internalNumber
        self.externalNumber = externalNumber
        self.invoiceNumber = invoiceNumber
        self.supplier = supplier
        self.shipper = shipper
        self.reason = reason
        self.fundSource = fundSource
        self.organisation = organisation
        self.store = store

    def getStoreItemDelta(self, storeId=None):
        result = defaultdict(int)
        if storeId and storeId != self.store:
            return result

        for item in self.items:  # type: DocumentPosition
            result[item.itemId] += item.amount
        return result

    def _fromJSON(self, dct):
        super(ShippingDocument, self)._fromJSON(dct)
        self.internalNumber = dct.get('internal_number')
        self.externalNumber = dct.get('external_number')
        self.invoiceNumber = dct.get('invoice_number')
        self.supplier = dct.get('supplier')
        self.shipper = dct.get('shipper')
        self.reason = dct.get('reason')
        self.fundSource = dct.get('fund_source')
        self.organisation = dct.get('organisation')
        self.store = dct.get('store')

    def toJSON(self):
        res = super(ShippingDocument, self).toJSON()
        res.update({
            'internal_number': self.internalNumber,
            'external_number': self.externalNumber,
            'invoice_number' : self.invoiceNumber,
            'supplier'       : self.supplier,
            'shipper'        : self.shipper,
            'reason'         : self.reason,
            'fund_source'    : self.fundSource,
            'organisation'   : self.organisation,
            'store'          : self.store
        })
        return res

    def __repr__(self):
        return u'<ShippingDocument int: {0}, ext: {1}, inv: {2}, date: {3}>'.format(
            self.internalNumber, self.externalNumber, self.invoiceNumber, self.date.toString('dd.MM.yyyy') if self.date else ''
        )


class StockItemInfo(Base):
    def __init__(self, expiryDate=None, amount=0, unitId=None, price=None):
        super(StockItemInfo, self).__init__()
        self.expiryDate = expiryDate
        self.amount = amount
        self.unitId = unitId
        self.price = price
        self.internalNumber = None
        self.documentId = None

    def _fromJSON(self, dct):
        self.expiryDate = self.dateFromJSON(dct.get('date'))
        self.amount = dct.get('amount', 0)
        self.unitId = dct.get('unit_id')
        self.price = Decimal(dct.get('price') or 0)


class CatalogItemShippingInfo(Base):
    u""" Возвращается по /by_catalog_item """

    def __init__(self, internalNumber=u'', documentId=None, items=None):
        super(CatalogItemShippingInfo, self).__init__()
        self.internalNumber = internalNumber
        self.documentId = documentId
        self.items = items or []

    def _fromJSON(self, dct):
        self.internalNumber = dct.get('internal_number', u'')
        self.documentId = dct.get('document_id')
        self.items = ItemList(StockItemInfo).fromJSON(dct.get('items'))


class DocumentPosition(UpdateableItem):
    def __init__(self, posId=None, amount=0, itemId=None, catalogItem=None, catalogItemId=None, productionDate=None,
                 arrivalDate=None, expiryDate=None, price=None, serial=''):
        super(DocumentPosition, self).__init__(posId)
        self.amount = amount
        self.itemId = itemId
        self.catalogItem = catalogItem  # type: CatalogItem
        self.catalogItemId = catalogItemId
        self.productionDate = productionDate
        self.arrivalDate = arrivalDate
        self.expiryDate = expiryDate
        self.price = price
        self.serial = serial

    def lite(self):
        return LiteDocumentPosition(itemId=self.itemId, amount=self.amount)

    @property
    def catalogItemName(self):
        return self.catalogItem.name if self.catalogItem else u''

    @property
    def tradeName(self):
        return self.catalogItem.tradeName if self.catalogItem else u''

    @property
    def INN(self):
        return self.catalogItem.INN if self.catalogItem else u''

    @property
    def dosage(self):
        return self.catalogItem.dosage if self.catalogItem else u''

    @property
    def unit(self):
        return self.catalogItem.unit if self.catalogItem else u''

    @property
    def sum(self):
        return self.price * self.amount if self.price and self.amount else 0

    def _fromJSON(self, dct):
        super(DocumentPosition, self)._fromJSON(dct)
        self.amount = dct.get('amount') or 0
        self.itemId = dct.get('item_id')
        self.catalogItem = CatalogItem().fromJSON(dct.get('catalog_item'))
        self.catalogItemId = dct.get('catalog_item_id')
        self.productionDate = self.dateFromJSON(dct.get('production_date'))
        self.arrivalDate = self.dateFromJSON(dct.get('arrival_date'))
        self.expiryDate = self.dateFromJSON(dct.get('expiry_date'))
        self.price = Decimal(dct.get('price') or 0)
        self.serial = dct.get('serial', '')

    def toJSON(self):
        dct = super(DocumentPosition, self).toJSON()
        dct['amount'] = self.amount
        dct['catalog_item_id'] = self.catalogItemId
        dct['price'] = unicode(self.price)
        dct['serial'] = self.serial
        if self.productionDate:
            dct['production_date'] = self.dateToJSON(self.productionDate)
        if self.arrivalDate:
            dct['arrival_date'] = self.dateToJSON(self.arrivalDate)
        if self.expiryDate:
            dct['expiry_date'] = self.dateToJSON(self.expiryDate)
        return dct

    def __repr__(self):
        return u'<DocumentPosition name: "{0}", price: {1}, amount: {2}>'.format(
            self.catalogItemName, self.price, self.amount
        )


class ShippingDocumentPosition(DocumentPosition):
    pass


class RequestDocumentPosition(DocumentPosition):
    pass


class M11DocumentPosition(DocumentPosition):
    def __init__(self, *args, **kwargs):
        super(M11DocumentPosition, self).__init__(*args, **kwargs)
        self.maxAmount = self.amount


class LiteDocumentPosition(Base):
    def __init__(self, itemId=None, amount=0):
        super(LiteDocumentPosition, self).__init__()
        self.itemId = itemId
        self.amount = amount
        self.saved = False

    def _fromJSON(self, dct):
        self.itemId = dct.get('item_id')
        self.amount = dct.get('amount', 0)

    def toJSON(self):
        return {
            'item_id': self.itemId,
            'amount' : self.amount
        }

    def __repr__(self):
        return u'<LiteDocumentPosition itemId={0}, amount={1}>'.format(self.itemId, self.amount)


class RequestDocument(BaseDocument):
    def __init__(self, docId=None, number='', date=None, storeFrom=None, storeTo=None, user=None, historyNumber='',
                 finalized=False, finalizeDate=None, finalizeUser=None, docType=None, m11List=None, transferFinished=False):
        super(RequestDocument, self).__init__(docId, date, user, finalized, finalizeDate, finalizeUser)
        self.number = number
        self.storeFrom = storeFrom
        self.storeTo = storeTo
        self.historyNumber = historyNumber
        self.type = docType
        self.m11List = m11List or []
        self.transferFinished = transferFinished

    def _fromJSON(self, dct):
        super(RequestDocument, self)._fromJSON(dct)
        self.number = dct.get('number', '')
        self.storeFrom = dct.get('store_from')
        self.storeTo = dct.get('store_to')
        self.historyNumber = dct.get('history_number')
        self.type = dct.get('type', '')
        self.m11List = dct.get('m11_list', [])
        self.transferFinished = dct.get('transfer_finished', False)

    def toJSON(self):
        res = super(RequestDocument, self).toJSON()
        res.update({
            'number'        : self.number,
            'store_from'    : self.storeFrom,
            'store_to'      : self.storeTo,
            'history_number': self.historyNumber,
            'type'          : self.type
        })
        return res

    def __repr__(self):
        return u'<RequestDocument {0}, date: {1}, from: {2} to {3}>'.format(
            self.number, self.date.toString('dd.MM.yyyy') if self.date else '', self.storeFrom, self.storeTo
        )


class M11Document(BaseDocument):
    def __init__(self, docId=None, number=u'', date=None, storeFrom=None, storeTo=None, user=None,
                 finalized=False, finalizeUser=None, finalizeDate=None, request=None, requestId=None):
        super(M11Document, self).__init__(docId, date, user, finalized, finalizeDate, finalizeUser)
        self.number = number
        self.storeFrom = storeFrom
        self.storeTo = storeTo
        self.request = request
        self.requestId = requestId

    def getStoreItemDelta(self, storeId=None):
        result = defaultdict(int)
        if storeId and storeId not in (self.storeFrom, self.storeTo):
            return result

        if storeId is None:
            storeId = self.storeFrom

        sign = {self.storeFrom: -1, self.storeTo: +1}.get(storeId)
        for item in self.items:  # type: DocumentPosition
            result[item.itemId] += sign * item.amount
        return result

    def _fromJSON(self, dct):
        super(M11Document, self)._fromJSON(dct)
        self.number = dct.get('number', u'')
        self.storeFrom = dct.get('store_from')
        self.storeTo = dct.get('store_to')
        self.request = RequestDocument().fromJSON(dct.get('request', {}))
        self.requestId = dct.get('request_id')

    def toJSON(self):
        dct = super(M11Document, self).toJSON()
        dct.update({
            'number'    : self.number,
            'store_from': self.storeFrom,
            'store_to'  : self.storeTo,
            'request_id': self.requestId
        })
        return dct

    def __repr__(self):
        return u'<M11Document {0}, date: {1}, {2} -> {3}'.format(
            self.number, self.date.toString('dd.MM.yyyy') if self.date else '', self.storeFrom, self.storeTo
        )


class InventoryItem(Base):
    def __init__(self, item=None, itemId=None, stockAmount=0, expectedAmount=0, explanation=u'', notes=u''):
        super(InventoryItem, self).__init__()
        self.item = item  # type: StoreItem
        self.itemId = itemId
        self.stockAmount = stockAmount
        self.expectedAmount = expectedAmount
        self.explanation = explanation
        self.notes = notes
        self.saved = False

    @property
    def tradeName(self):
        return self.item.tradeName if self.item else u''

    @property
    def INN(self):
        return self.item.INN if self.item else u''

    @property
    def ATC(self):
        return self.item.ATC if self.item else u''

    @property
    def manufacturer(self):
        return self.item.manufacturer if self.item else None

    @property
    def expiryDate(self):
        return self.item.expiryDate if self.item else None

    @property
    def unit(self):
        return self.item.unit if self.item else None

    def toJSON(self):
        dct = super(InventoryItem, self).toJSON()
        dct.update({
            'stock_amount'   : self.stockAmount,
            'expected_amount': self.expectedAmount,
            'explanation'    : self.explanation,
            'notes'          : self.notes,
            'item_id'        : self.itemId
        })
        return dct

    def _fromJSON(self, dct):
        self.item = StoreItem().fromJSON(dct.get('item', {}))
        self.itemId = dct.get('item_id')
        self.stockAmount = dct.get('stock_amount', 0)
        self.expectedAmount = dct.get('expected_amount', 0)
        self.notes = dct.get('notes', u'')
        self.explanation = dct.get('explanation', u'')

    def __repr__(self):
        return u'<InventoryItem: itemId: {0}, expected amount: {1}, stock amount: {2}'.format(
            self.itemId, self.expectedAmount, self.stockAmount
        )


class InventoryDocument(BaseDocument):
    def __init__(self, docId=None, number=u'', date=None, store=None, user=None, finalized=False, finalizeUser=None, finalizeDate=None):
        super(InventoryDocument, self).__init__(docId, date, user, finalized, finalizeDate, finalizeUser)
        self.number = number
        self.store = store

    def getStoreItemDelta(self, storeId=None):
        result = defaultdict(int)
        if storeId and storeId != self.store:
            return result

        for item in self.items:  # type: InventoryItem
            result[item.itemId] = item.stockAmount - item.expectedAmount
        return result

    def _fromJSON(self, dct):
        super(InventoryDocument, self)._fromJSON(dct)
        self.number = dct.get('number', u'')
        self.store = dct.get('store')

    def toJSON(self):
        res = super(InventoryDocument, self).toJSON()
        res['number'] = self.number
        res['store'] = self.store
        return res

    def __repr__(self):
        return u'<InventoryDocument {0}, date: {1}, store: {2}'.format(
            self.number, self.date.toString('dd.MM.yyyy') if self.date else '', self.store
        )


class WriteOffDocument(BaseDocument):
    def __init__(self, docId=None, number=u'', date=None, store=None, user=None, finalized=False, finalizeUser=None, finalizeDate=None, reason=u''):
        super(WriteOffDocument, self).__init__(docId, date, user, finalized, finalizeDate, finalizeUser)
        self.number = number
        self.store = store
        self.reason = reason

    def _fromJSON(self, dct):
        super(WriteOffDocument, self)._fromJSON(dct)
        self.number = dct.get('number', u'')
        self.store = dct.get('store')
        self.reason = dct.get('reason', u'')

    def __repr__(self):
        return u'<WriteOffDocument "{0}", date: {1}, store: {2}>'.format(self.number, self.date, self.store)
