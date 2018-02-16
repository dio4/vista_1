# -*- coding: utf-8 -*-
import json
import logging
import requests
from collections import defaultdict
from functools import wraps
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, InvalidURL, MissingSchema

# from pympler import asizeof
from Types import Catalog, CatalogField, CatalogItem, CatalogItemShippingInfo, FundSource, InventoryDocument, InventoryItem, Item, ItemList, \
    LiteDocumentPosition, M11Document, M11DocumentPosition, MeasurementUnit, Organisation, OrganisationType, RequestDocument, RequestDocumentPosition, \
    ResultList, ShippingDocument, ShippingDocumentPosition, Store, StoreItem, StoreStockItem, UpdateableItem, User, WriteOffDocument
from library.Enum import CEnum
from library.Utils import forceString


class UserPermission(CEnum):
    EditInventory = 'pharmacy.edit_inventory'
    EditM11 = 'pharmacy.edit_m11'
    EditRequest = 'pharmacy.edit_request'
    EditShipping = 'pharmacy.edit_shipping'
    EditSavedShipping = 'pharmacy.edit_saved_shipping'
    EditWriteOff = 'pharmacy.edit_writeoff'
    FinalizeInventory = 'pharmacy.finalize_inventory'
    FinalizeM11 = 'pharmacy.finalize_m11'
    FinalizeRequest = 'pharmacy.finalize_request'
    FinalizeShipping = 'pharmacy.finalize_shipping'
    FinalizeWriteOff = 'pharmacy.finalize_writeoff'

    nameMap = {
        EditInventory    : u'Может создавать, изменять и удалять инвентаризации',
        EditM11          : u'Может создавать, изменять и удалять М11',
        EditRequest      : u'Может создавать, изменять и удалять требования',
        EditShipping     : u'Может создавать, изменять и удалять накладные',
        EditSavedShipping: u'Может редактировать количество и срок годности',
        EditWriteOff     : u'Может создавать, изменять и удалять списания',
        FinalizeInventory: u'Может закреплять инвентаризации',
        FinalizeM11      : u'Может закреплять М11',
        FinalizeRequest  : u'Может закреплять требования',
        FinalizeShipping : u'Может закреплять накладные',
        FinalizeWriteOff : u'Может закреплять списания'
    }


def prettyJson(obj):
    return json.dumps(obj, ensure_ascii=False, indent=4)


def cached(itemType=None):
    def decorator(getItemListMethod):
        @wraps(getItemListMethod)
        def wrapper(*args, **kwargs):
            key = args[1:] + tuple(kwargs.items())
            result = CServiceDataCache.get(itemType, key)
            if result is not None:
                return result
            else:
                result = getItemListMethod(*args, **kwargs)
                if result is not None:
                    CServiceDataCache.set(itemType, key, result)
                return result

        return wrapper

    return decorator


def itemCached(getItemMethod):
    @wraps(getItemMethod)
    def wrapper(self, itemType, itemId):
        item = CServiceDataCache.getItem(itemType, itemId, defaultEmpty=False)
        if item is None:
            item = getItemMethod(self, itemType, itemId)
            if item and item.id:
                CServiceDataCache.put(item)
        return item

    return wrapper


def resetCacheOnSuccess(postItemMethod):
    @wraps(postItemMethod)
    def wrapper(self, item):
        createdItem = postItemMethod(self, item)
        if createdItem:
            CServiceDataCache.reset(item.__class__)
        return createdItem

    return wrapper


def resetCache(itemType=None):
    def decorator(serviceMethod):
        @wraps(serviceMethod)
        def wrapper(*args, **kwargs):
            result = serviceMethod(*args, **kwargs)
            if result:
                CServiceDataCache.reset(itemType)
            return result

        return wrapper

    return decorator


class CServiceDataCache(object):
    __itemTypeCache = defaultdict(lambda: defaultdict(dict))  # cache[itemType][tuple of params] = result
    __itemCache = defaultdict(dict)  # cache[itemType][itemId] = item

    # @classmethod
    # def printCacheSize(cls):
    #     print(u'cache size: %.1fkb' % (asizeof.asizeof(cls.__itemCache, cls.__itemTypeCache) / 1024.0))

    @classmethod
    def getItem(cls, itemType, itemId, defaultEmpty=True):
        u"""
        :param itemType: Item subclass
        :param itemId: Item.id
        :param defaultEmpty: возвращать пустой Item(), если нет в кэше или None
        :rtype: Item
        """
        return cls.__itemCache[itemType].get(itemId, itemType() if defaultEmpty else None)

    @classmethod
    def get(cls, itemType, key=()):
        return cls.__itemTypeCache.get(itemType, {}).get(key)

    @classmethod
    def set(cls, itemType, key, items):
        u"""
        :type itemType: type
        :type key: tuple
        :type items: iterable of Item
        """
        cls.__itemTypeCache[itemType][key] = items
        for item in items:
            cls.__itemCache[itemType][item.id] = item
        # cls.printCacheSize()

    @classmethod
    def put(cls, item):
        u"""
        :type item: Item
        """
        cls.__itemCache[item.__class__][item.id] = item
        # cls.printCacheSize()

    @classmethod
    def reset(cls, itemType=None):
        u"""
        :type itemType: list of types
        """
        if itemType is None:
            cls.__itemTypeCache.clear()
            cls.__itemCache.clear()
        else:
            if not isinstance(itemType, (tuple, list)):
                itemType = [itemType]
            for _itemType in itemType:
                cls.__itemTypeCache[_itemType].clear()
                cls.__itemCache.pop(_itemType, None)


class CPharmacyServiceException(Exception):
    def __init__(self, message=u'', resp=None):
        self.message = message
        self.resp = resp

    @property
    def errorMessage(self):
        return self.resp.text if self.resp is not None and self.resp.text else self.message


class CPharmacyService(object):
    __instance = None  # type: CPharmacyService
    __itemReferenceMap = {
        Catalog                 : '/api/catalogs/catalog/',
        CatalogField            : '/api/catalogs/catalog_field/',
        CatalogItem             : '/api/catalogs/catalog_item/',
        InventoryDocument       : '/api/pharmacy/docs.inventory/',
        InventoryItem           : '/api/pharmacy/docs.inventory/{docId}/items/',
        M11Document             : '/api/pharmacy/docs.m11/',
        M11DocumentPosition     : '/api/pharmacy/docs.m11/{docId}/items/',
        RequestDocument         : '/api/pharmacy/docs.request/',
        RequestDocumentPosition : '/api/pharmacy/docs.request/{docId}/items/',
        ShippingDocument        : '/api/pharmacy/docs.shipping/',
        ShippingDocumentPosition: '/api/pharmacy/docs.shipping/{docId}/items/',
        WriteOffDocument        : '/api/pharmacy/docs.writeoff/',
        Store                   : '/api/pharmacy/store/',
        StoreItem               : '/api/pharmacy/store_item/',
        User                    : '/api/profiles/user/',
        FundSource              : '/api/reference/fund_source/',
        MeasurementUnit         : '/api/reference/measurement_unit/',
        Organisation            : '/api/reference/organisation/',
        OrganisationType        : '/api/reference/organisation_type/',
    }

    @classmethod
    def getInstance(cls):
        return cls.__instance

    @classmethod
    def reset(cls):
        cls.__instance = None
        CServiceDataCache.reset()

    def __init__(self, url, user=None, password=None):
        self._url = url
        self._auth = (user, password)
        self._session = requests.session()
        self._session.mount(url, HTTPAdapter(max_retries=20))
        self._session.auth = (user, password)
        self._currentUser = None
        self.logger = logging.getLogger('requests.packages.urllib3')

        CServiceDataCache.reset()
        CPharmacyService.__instance = self

    def send(self, url, asJson=True, params=None, method='GET', jsonData=None):
        try:
            resp = self._session.request(method, '{0}{1}'.format(self._url, url), params=params, json=jsonData)
            if resp.status_code == 400:
                raise CPharmacyServiceException(resp=resp)
            elif resp.status_code == 401:
                raise CPharmacyServiceException(resp=resp)
            elif resp.status_code == 404:
                raise CPharmacyServiceException(resp=resp)

            self.logger.debug(u'\nREQUEST URL: %s\nREQUEST BODY: %s\nRESPONSE BODY:\n%s' % (
                resp.request.url,
                resp.request.body if resp.request.body else u'',
                prettyJson(resp.json()) if resp.content else u''
            ))
            return resp.json() if asJson else resp

        except InvalidURL as e:
            raise CPharmacyServiceException(e.message)

        except MissingSchema as e:
            raise CPharmacyServiceException(e.message)

        except ConnectionError as e:
            raise CPharmacyServiceException(e.message)

        except CPharmacyServiceException:
            raise

        except Exception as e:
            self.logger.exception(e)
            return None

    @staticmethod
    def formatBool(v):
        return None if v is None else str(bool(v))

    @staticmethod
    def formatFlag(v):
        return {True: 1, False: 0}.get(v)

    @staticmethod
    def formatDate(date):
        u"""
        :type date: QtCore.QDate
        :rtype: str
        """
        return forceString(date.toString('yyyy-MM-dd')) if date and date.isValid() else None

    @itemCached
    def getItem(self, itemType, itemId):
        url = '{ref}{itemId}/'.format(ref=self.__itemReferenceMap[itemType], itemId=itemId)
        return itemType().fromJSON(self.send(url)) if itemId else itemType()

    @resetCacheOnSuccess
    def postItem(self, item):
        u"""
        :type item: Item
        :rtype: Item
        """
        itemType = item.__class__
        url = self.__itemReferenceMap[itemType]
        resp = self.send(url, asJson=False, method='POST', jsonData=item.toJSON())
        return itemType().fromJSON(resp.json()) if resp.status_code == 201 else None

    @resetCacheOnSuccess
    def putItem(self, item):
        u"""
        :type item: UpdateableItem
        :rtype: UpdateableItem
        """
        itemType = item.__class__
        resp = self.send(url='{ref}{itemId}/'.format(ref=self.__itemReferenceMap[itemType], itemId=item.id),
                         asJson=False,
                         method='PUT',
                         jsonData=item.toJSON())
        return itemType().fromJSON(resp.json()) if resp.status_code == 200 else None

    def getItemList(self, itemType):
        u"""
        :rtype: ItemList
        """
        return ItemList(itemType).fromJSON(self.send(url=self.__itemReferenceMap[itemType]))

    def getResultListPage(self, itemType, url=None, pageSize=None, page=None, **params):
        u"""
        :rtype: ResultList
        """
        params.update({'page_size': pageSize, 'page': page})
        return ResultList(itemType).fromJSON(self.send(
            url=url or self.__itemReferenceMap[itemType],
            params=params
        ))

    def getFlatResultList(self, itemType=None, url=None, **params):
        page, pageSize = 1, 100
        resultList = self.getResultListPage(itemType, url, pageSize=pageSize, page=page, **params)
        result = list(resultList)
        while page < resultList.pageCount:
            resultList = self.getResultListPage(itemType, url, pageSize=pageSize, page=page + 1, **params)
            result.extend(resultList)
            page += 1
        return result

    def testConnect(self):
        u"""
        :return: (current User, error message)
        :rtype: (User,unicode)
        """
        try:
            currentUser = self.getCurrentUser()
        except CPharmacyServiceException as e:
            currentUser = None
            error = e.errorMessage
        except Exception as e:
            currentUser = None
            error = unicode(e)
        else:
            error = None

        return currentUser, error

    def getCurrentUser(self):
        if self._currentUser is None:
            self._currentUser = User().fromJSON(self.send('/api/profiles/current/'))
        return self._currentUser

    @cached(User)
    def getUsers(self, pageSize=None, page=None):
        return self.getResultListPage(User, pageSize=pageSize, page=page)

    @cached(User)
    def getFlatUserList(self):
        return self.getFlatResultList(User)

    @cached(Catalog)
    def getCatalogs(self):
        return ItemList(Catalog).fromJSON(self.send('/api/catalogs/catalog/'))

    @cached(CatalogField)
    def getCatalogFields(self):
        return ItemList(CatalogField).fromJSON(self.send('/api/catalogs/catalog_field/'))

    @cached(CatalogItem)
    def getCatalogItems(self, catalogId=None, pageSize=None, page=None, flat=False):
        return self.getFlatResultList(CatalogItem) if flat else self.getResultListPage(CatalogItem, pageSize=pageSize, page=page, catalog=catalogId)

    @cached(OrganisationType)
    def getOrganisationTypes(self):
        return self.getItemList(OrganisationType)

    @cached(Organisation)
    def getOrganisations(self):
        return self.getItemList(Organisation)

    @cached(MeasurementUnit)
    def getMeasurementUnits(self):
        return self.getItemList(MeasurementUnit)

    @cached(FundSource)
    def getFundSources(self):
        return self.getItemList(FundSource)

    @cached(Store)
    def getStores(self, pageSize=None, page=None):
        return self.getItemList(Store)

    @cached(StoreItem)
    def getStoreItems(self):
        u""" Все партии товаров """
        return self.getItemList(StoreItem)

    @cached(StoreStockItem)
    def getStoreStockItems(self, storeId, catalogId=None, pageSize=None, page=None, name=None, fields=None, arrivalDate=None, expiryDays=None, detailed=None):
        u"""
        Остатки товаров на складе
        :type arrivalDate: QtCore.QDate
        """
        return self.getResultListPage(
            StoreStockItem,
            url='{store}{storeId}/stock/'.format(store=self.__itemReferenceMap[Store], storeId=storeId),
            pageSize=pageSize, page=page,
            **{
                'catalog'     : catalogId,
                'name'        : name or None,
                'contains'    : fields or None,
                'arrival_date': self.formatDate(arrivalDate),
                'expiry_days' : expiryDays or None,
                'detailed'    : 1 if detailed else 0
            }
        )

    @cached(StoreStockItem)
    def getFlatStoreItems(self, storeId, catalogId=None, name=None, arrivalDate=None, expiryDays=None, detailed=None):
        u"""
        :rtype: list[StoreStockItem]
        """
        return self.getFlatResultList(
            StoreStockItem,
            url='{store}{storeId}/stock/'.format(store=self.__itemReferenceMap[Store], storeId=storeId),
            **{
                'name'        : name,
                'catalog'     : catalogId,
                'arrival_date': self.formatDate(arrivalDate),
                'expiry_days' : expiryDays,
                'detailed'    : 1 if detailed else 0
            }
        )

    def getStoreItemAmountMap(self, storeId):
        if not storeId: return {}
        try:
            items = self.getFlatStoreItems(storeId=storeId, detailed=True)
        except CPharmacyServiceException:
            items = []
        return dict((item.item.id, item.amount) for item in items)

    def rebuildItemNames(self, storeId):
        resp = self.send(url='{store}{storeId}/rebuild_names/'.format(store=self.__itemReferenceMap[Store], storeId=storeId), method='POST', asJson=False)
        return resp.status_code == 200

    @cached(ShippingDocument)
    def getShippingDocuments(self, pageSize=None, page=None, store=None, supplier=None, user=None, date=None, fundSource=None):
        return self.getResultListPage(
            ShippingDocument,
            pageSize=pageSize, page=page,
            **{
                'store'      : store,
                'supplier'   : supplier,
                'user'       : user,
                'date'       : self.formatDate(date),
                'fund_source': fundSource
            }
        )

    @cached(ShippingDocument)
    def getFlatShippingDocuments(self, storeId=None, supplierId=None, userId=None,
                                 date=None, dateFrom=None, dateTo=None,
                                 finDate=None, finDateFrom=None, finDateTo=None,
                                 finalized=None, fundSource=None, items=False):
        u"""
        :rtype: list[ShippingDocument]
        """
        docs = self.getFlatResultList(ShippingDocument, **{
            'store'        : storeId,
            'supplier'     : supplierId,
            'user'         : userId,
            'fund_source'  : fundSource,
            'date'         : self.formatDate(date),
            'date_from'    : self.formatDate(dateFrom),
            'date_to'      : self.formatDate(dateTo),
            'finalized'    : self.formatFlag(finalized),
            'fin_date'     : self.formatDate(finDate),
            'fin_date_from': self.formatDate(finDateFrom),
            'fin_date_to'  : self.formatDate(finDateTo)
        })
        if items:
            for doc in docs:  # type: ShippingDocument
                doc.items = self.getFlatShippingDocumentPositions(doc.id)
        return docs

    def getShippingDocumentPositions(self, docId, pageSize=None, page=None):
        url = self.__itemReferenceMap[ShippingDocumentPosition].format(docId=docId)
        return self.getResultListPage(ShippingDocumentPosition, url, pageSize=pageSize, page=page)

    @cached(ShippingDocumentPosition)
    def getFlatShippingDocumentPositions(self, docId):
        return self.getFlatResultList(ShippingDocumentPosition,
                                      url=self.__itemReferenceMap[ShippingDocumentPosition].format(docId=docId))

    @resetCache(ShippingDocumentPosition)
    def addShippingDocumentPosition(self, docId, position):
        u"""
        :param docId: ShippingDocument.id
        :type position: ShippingDocumentPosition
        :rtype: ShippingDocumentPosition
        """
        resp = self.send(url=self.__itemReferenceMap[ShippingDocumentPosition].format(docId=docId),
                         asJson=False, method='POST', jsonData=position.toJSON())
        return ShippingDocumentPosition().fromJSON(resp.json()) if resp.status_code == 200 else None

    @resetCache((ShippingDocument, StoreStockItem))
    def finalizeShippingDocument(self, docId):
        resp = self.send(url='{doc}{docId}/finalize/'.format(doc=self.__itemReferenceMap[ShippingDocument], docId=docId),
                         asJson=False, method='POST')
        return resp.status_code == 200

    def getCatalogItemShippingDocuments(self, catalogItemId, storeId):
        resultList = ItemList(CatalogItemShippingInfo).fromJSON(self.send('/api/pharmacy/docs.shipping/by_catalog_item/', params={
            'catalog_item': catalogItemId, 'store': storeId
        }))
        result = []
        for shippingInfo in resultList:
            for stockItemInfo in shippingInfo.items:
                stockItemInfo.documentId = shippingInfo.documentId
                stockItemInfo.internalNumber = shippingInfo.internalNumber
                result.append(stockItemInfo)
        return result

    @cached(RequestDocument)
    def getRequestDocuments(self, pageSize=None, page=None, storeFrom=None, storeTo=None, docType=None, finalized=None, transferFinished=None,
                            date=None, dateFrom=None, dateTo=None):
        u"""
        :rtype: ResultList
        """
        return self.getResultListPage(RequestDocument, pageSize=pageSize, page=page, **{
            'store_from'       : storeFrom,
            'store_to'         : storeTo,
            'type'             : docType,
            'finalized'        : self.formatFlag(finalized),
            'transfer_finished': self.formatFlag(transferFinished),
            'date'             : self.formatDate(date),
            'date_from'        : self.formatDate(dateFrom),
            'date_to'          : self.formatDate(dateTo),
        })

    @cached(RequestDocument)
    def getFlatRequestDocuments(self, storeFrom=None, storeTo=None, docType=None, finalized=None, transferFinished=None,
                                date=None, dateFrom=None, dateTo=None, positions=False):
        u"""
        :param storeFrom: Store.id
        :param storeTo:  Store.id
        :param docType: RequestDocument.type
        :param finalized: RequestDocument.finalized
        :param transferFinished: RequestDocument.transferFinished
        :type date: QtCore.QDate
        :type dateFrom: QtCore.QDate
        :type dateTo: QtCore.QDate
        :param positions: Загружать содержимое требования
        :rtype: list[RequestDocument]
        """
        docs = self.getFlatResultList(RequestDocument, **{
            'store_from'       : storeFrom,
            'store_to'         : storeTo,
            'type'             : docType,
            'finalized'        : self.formatFlag(finalized),
            'transfer_finished': self.formatFlag(transferFinished),
            'date'             : self.formatDate(date),
            'date_from'        : self.formatDate(dateFrom),
            'date_to'          : self.formatDate(dateTo)
        })
        if positions:
            for doc in docs:  # type: RequestDocument
                doc.items = self.getFlatRequestDocumentPositions(doc.id)

        return docs

    @resetCache((RequestDocumentPosition, RequestDocument))
    def addRequestDocumentPosition(self, docId, position):
        u"""
        :param docId: RequestDocument.id
        :type position: LiteDocumentPosition
        :rtype: RequestDocumentPosition
        """
        resp = self.send(url=self.__itemReferenceMap[RequestDocumentPosition].format(docId=docId),
                         asJson=False, method='POST', jsonData=position.toJSON())
        return RequestDocumentPosition().fromJSON(resp.json()) if resp.status_code == 200 else None

    def getRequestDocumentPositions(self, docId, pageSize=None, page=None):
        return self.getResultListPage(RequestDocumentPosition,
                                      url=self.__itemReferenceMap[RequestDocumentPosition].format(docId=docId),
                                      pageSize=pageSize, page=page)

    @cached(RequestDocumentPosition)
    def getFlatRequestDocumentPositions(self, docId):
        return self.getFlatResultList(RequestDocumentPosition,
                                      url=self.__itemReferenceMap[RequestDocumentPosition].format(docId=docId))

    @resetCache((RequestDocument, StoreStockItem))
    def finalizeRequestDocument(self, docId):
        resp = self.send('/api/pharmacy/docs.request/{docId}/finalize/'.format(docId=docId), asJson=False, method='POST')
        return resp.status_code == 200

    @resetCache(RequestDocument)
    def finishTransferRequestDocument(self, docId):
        resp = self.send('/api/pharmacy/docs.request/{docId}/finish_transfer/'.format(docId=docId), asJson=False, method='POST')
        return resp.status_code == 200

    # M11
    def getM11DocumentPositions(self, docId, pageSize=None, page=None):
        return self.getResultListPage(M11DocumentPosition,
                                      url=self.__itemReferenceMap[M11DocumentPosition].format(docId=docId),
                                      pageSize=pageSize, page=page)

    @cached(M11DocumentPosition)
    def getFlatM11DocumentPositions(self, docId):
        return self.getFlatResultList(M11DocumentPosition,
                                      url=self.__itemReferenceMap[M11DocumentPosition].format(docId=docId))

    @resetCache(M11DocumentPosition)
    def addM11DocumentPosition(self, docId, position):
        u"""
        :param docId: M11Document.id
        :type position: LiteDocumentPosition
        :rtype: M11DocumentPosition
        """
        resp = self.send(url=self.__itemReferenceMap[M11DocumentPosition].format(docId=docId),
                         asJson=False, method='POST', jsonData=position.toJSON())
        return M11DocumentPosition().fromJSON(resp.json()) if resp.status_code == 200 else None

    @resetCache((M11Document, StoreStockItem))
    def finalizeM11Document(self, docId):
        resp = self.send('/api/pharmacy/docs.m11/{docId}/finalize/'.format(docId=docId), asJson=False, method='POST')
        return resp.status_code == 200

    def getM11Documents(self, pageSize=None, page=None):
        return ResultList(M11Document).fromJSON(self.send('/api/pharmacy/docs.m11/', params={
            'page_size': pageSize, 'page': page
        }))

    @cached(M11Document)
    def getFlatM11Documents(self, storeFrom=None, storeTo=None, date=None, dateFrom=None, dateTo=None,
                            finalized=None, finDate=None, finDateFrom=None, finDateTo=None, items=False):
        u"""
        :rtype: list[M11Document]
        """
        docs = self.getFlatResultList(M11Document, **{
            'store_from'   : storeFrom,
            'store_to'     : storeTo,
            'date'         : self.formatDate(date),
            'date_from'    : self.formatDate(dateFrom),
            'date_to'      : self.formatDate(dateTo),
            'finalized'    : self.formatFlag(finalized),
            'fin_date'     : self.formatDate(finDate),
            'fin_date_from': self.formatDate(finDateFrom),
            'fin_date_to'  : self.formatDate(finDateTo)
        })
        if items:
            for doc in docs:  # type: M11Document
                doc.items = self.getFlatM11DocumentPositions(doc.id)
        return docs

    # Inventory
    @cached(InventoryDocument)
    def getInventoryDocuments(self, store=None, pageSize=None, page=None):
        return self.getResultListPage(InventoryDocument, pageSize=pageSize, page=page, store=store)

    @cached(InventoryDocument)
    def getFlatInventoryDocuments(self, storeId=None, date=None, dateFrom=None, dateTo=None, finalized=None,
                                  finDate=None, finDateFrom=None, finDateTo=None, items=False):
        u"""
        :rtype: list[InventoryDocument]
        """
        docs = self.getFlatResultList(InventoryDocument, **{
            'store'        : storeId,
            'date'         : self.formatDate(date),
            'date_from'    : self.formatDate(dateFrom),
            'date_to'      : self.formatDate(dateTo),
            'finalized'    : self.formatFlag(finalized),
            'fin_date'     : self.formatDate(finDate),
            'fin_date_from': self.formatDate(finDateFrom),
            'fin_date_to'  : self.formatDate(finDateTo),
        })
        if items:
            for doc in docs:  # type: InventoryDocument
                doc.items = self.getFlatInventoryItems(doc.id)
        return docs

    def getInventoryItems(self, docId, pageSize=None, page=None):
        url = '/api/pharmacy/docs.inventory/{docId}/items/'.format(docId=docId)
        return self.getResultListPage(InventoryItem, url, pageSize=pageSize, page=page)

    def getFlatInventoryItems(self, docId):
        return self.getFlatResultList(InventoryItem, url='/api/pharmacy/docs.inventory/{docId}/items/'.format(docId=docId))

    def addInventoryDocumentItem(self, docId, item):
        u"""
        :param docId: InventooryDocument.id
        :type item: InventoryItem
        :rtype: InventoryItem
        """
        resp = self.send('/api/pharmacy/docs.inventory/{docId}/items/'.format(docId=docId), asJson=False, method='POST', jsonData=item.toJSON())
        return InventoryItem().fromJSON(resp.json()) if resp.status_code == 200 else None

    @resetCache((StoreStockItem, InventoryDocument))
    def finalizeInventoryDocument(self, docId):
        resp = self.send('/api/pharmacy/docs.inventory/{docId}/finalize/'.format(docId=docId), asJson=False, method='POST')
        return resp.status_code == 200

    # WriteOff
    # def getWriteOffDocument(self, docId):
    #     return WriteOffDocument().fromJSON('/api/pharmacy/docs.writeoff/{docId}/'.format(docId=docId))
    #
    # def getWriteOffDocuments(self, pageSize=None, page=None, store=None, user=None, date=None):
    #     return ResultList(WriteOffDocument).fromJSON(self.send('/api/pharmacy/docs.writeoff/', params={
    #         'page_size': pageSize, 'page': page, 'store': store, 'user': user, 'date': date
    #     }))
    #
    # def getWriteOffDocumentItems(self, docId, pageSize=None, page=None):
    #     return ResultList(DocumentPosition).fromJSON(self.send('/api/pharmacy/docs.writeoff/{docId}/items/'.format(docId=docId), params={
    #         'page_size': pageSize, 'page': page
    #     }))
    #
    # def finalizeWriteOffDocument(self, docId):
    #     resp = self.send('/api/pharmacy/docs.writeoff/{docId}/finalize/'.format(docId=docId), asJson=False, method='POST')
    #     return resp.status_code == 200
