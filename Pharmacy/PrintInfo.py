# -*- coding: utf-8 -*-

from Pharmacy.RequestDocument import RequestDocumentType
from Pharmacy.Service import CPharmacyService
from Pharmacy.StoreItem import ExpirationClass
from Pharmacy.Types import Catalog, DocumentPosition, MeasurementUnit, RequestDocument, Store
from library.PrintInfo import CDateInfo, CDateTimeInfo, CInfo


class CDocumentPositionInfo(CInfo):
    def __init__(self, context, position):
        super(CDocumentPositionInfo, self).__init__(context)
        self._pos = position  # type: DocumentPosition

    def _load(self):
        pass

    amount = property(lambda self: self._pos.amount)
    dosage = property(lambda self: self._pos.dosage)
    INN = property(lambda self: self._pos.INN)
    price = property(lambda self: self._pos.price)
    serial = property(lambda self: self._pos.serial)
    sum = property(lambda self: self._pos.sum)
    tradeName = property(lambda self: self._pos.tradeName)
    unit = property(lambda self: self._pos.unit)


class CItemInfo(CInfo):
    def __init__(self, context, itemId=None, item=None):
        super(CItemInfo, self).__init__(context)
        self._itemId = itemId
        self._item = item

    def _load(self):
        return True


class CRbItemInfo(CItemInfo):
    code = property(lambda self: self._item.code)
    name = property(lambda self: self._item.name)
    codeName = property(lambda self: self._item.codeName)

    def __str__(self):
        return self.name


class CStoreInfo(CItemInfo):
    def _load(self):
        if not self._item:
            self._item = CPharmacyService.getInstance().getItem(Store, self._itemId)

    name = property(lambda self: self.load()._item.name)

    def __str__(self):
        return self.name


class CCatalogInfo(CItemInfo):
    name = property(lambda self: self._item.name)
    description = property(lambda self: self._item.description)
    fields = property(lambda self: self._item.fields)

    def __str__(self):
        return self.name


class CCatalogItemInfo(CItemInfo):
    def __init__(self, *args, **kwargs):
        super(CCatalogItemInfo, self).__init__(*args, **kwargs)
        self._unit = None
        self._catalog = None

    def _load(self):
        self._unit = CRbItemInfo(context=self.context,
                                 item=CPharmacyService.getInstance().getItem(MeasurementUnit, self._item.unit))
        self._catalog = CCatalogInfo(context=self.context,
                                     item=CPharmacyService.getInstance().getItem(Catalog, self._item.catalog))
        return True

    name = property(lambda self: self._item.name)
    catalog = property(lambda self: self.load()._catalog)
    fields = property(lambda self: self._item.fields)
    tradeName = property(lambda self: self._item.tradeName)
    INN = property(lambda self: self._item.INN)
    ATC = property(lambda self: self._item.ATC)
    manufacturer = property(lambda self: self._item.manufacturer)
    dosage = property(lambda self: self._item.dosage)
    unit = property(lambda self: self.load()._unit)

    def __str__(self):
        return self.name


class CStoreStockItemInfo(CItemInfo):
    def __init__(self, context, itemId=None, item=None):
        super(CStoreStockItemInfo, self).__init__(context, itemId, item)
        self._store = None
        self._unit = None
        self._itemClass = u''

    def _load(self):
        srv = CPharmacyService.getInstance()
        self._unit = CRbItemInfo(self.context, item=srv.getItem(MeasurementUnit, self._item.unit))
        self._store = CStoreInfo(self.context, item=srv.getItem(Store, self._item.store))
        self._itemClass = ExpirationClass.getDateClassName(self._item.expiryDate)
        return True

    amount = property(lambda self: self._item.amount)
    arrivalDate = property(lambda self: CDateInfo(self._item.arrivalDate))
    ATC = property(lambda self: self._item.ATC)
    expiryDate = property(lambda self: CDateInfo(self._item.expiryDate))
    INN = property(lambda self: self._item.INN)
    itemClass = property(lambda self: self.load()._itemClass)
    manufacturer = property(lambda self: self._item.manufacturer)
    productionDate = property(lambda self: CDateInfo(self._item.productionDate))
    store = property(lambda self: self.load()._store)
    tradeName = property(lambda self: self._item.tradeName)
    unit = property(lambda self: self.load()._unit)


class CRequestDocumentInfo(CInfo):
    def __init__(self, context, itemId=None, doc=None, positions=None):
        super(CRequestDocumentInfo, self).__init__(context)
        self._itemId = itemId
        self._doc = doc  # type: RequestDocument

        self._date = None
        self._datetime = None
        self._finalizeDate = None
        self._type = u''
        self._storeFrom = None
        self._storeTo = None
        self._positions = positions or []

    def _load(self):
        if not self._doc:
            try:
                self._doc = CPharmacyService.getInstance().getItem(RequestDocument, self._itemId)
            except Exception:
                self._doc = RequestDocument()

        self._datetime = CDateTimeInfo(self._doc.date)
        self._date = CDateInfo(self._doc.date.date())
        self._finalizeDate = CDateInfo(self._doc.finalizeDate.date())
        self._type = RequestDocumentType.getName(self._doc.type)
        self._storeFrom = CStoreInfo(self.context, itemId=self._doc.storeTo)
        self._storeTo = CStoreInfo(self.context, itemId=self._doc.storeFrom)
        self._positions = [CDocumentPositionInfo(self.context, position) for position in self._positions]

    date = property(lambda self: self.load()._date)
    datetime = property(lambda self: self.load()._datetime)
    finalizeDate = property(lambda self: self.load()._finalizeDate)
    number = property(lambda self: self.load()._doc.number)
    positions = property(lambda self: self.load()._positions)
    storeFrom = property(lambda self: self.load()._storeFrom)
    storeTo = property(lambda self: self.load()._storeTo)
    type = property(lambda self: self.load()._type)
