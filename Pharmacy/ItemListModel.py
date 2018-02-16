# -*- coding: utf-8 -*-

from Pharmacy.Service import CPharmacyService
from library.ItemListModel import CItemAttribCol


class CReferenceAttribCol(CItemAttribCol):
    u""" Столбец: значение аттрибута объекта, на который ссылается данный аттрибут """

    def __init__(self, title, attribName, itemType, refAttribName, default=None, **params):
        super(CReferenceAttribCol, self).__init__(title, attribName, default, **params)
        self._itemType = itemType
        self._refAttribName = refAttribName

    def displayValue(self, item, **params):
        itemId = super(CReferenceAttribCol, self).displayValue(item, **params)
        refItem = CPharmacyService.getInstance().getItem(self._itemType, itemId)
        return getattr(refItem, self._refAttribName, self._default)


class CRbItemRefAttribCol(CItemAttribCol):
    u""" Столбец: значение из справочника по id """

    def __init__(self, title, attribName, itemType, default=None, **params):
        super(CRbItemRefAttribCol, self).__init__(title, attribName, default, **params)
        self._itemType = itemType

    def displayValue(self, item, **params):
        itemId = super(CRbItemRefAttribCol, self).displayValue(item, **params)
        item = CPharmacyService.getInstance().getItem(self._itemType, itemId)
        return item.codeName if item else None
