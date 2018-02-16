# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

from Accounting.Utils           import CTariff
from library.Utils              import forceDate, forceDouble, forceInt, forceRef


class CContractTariffDescr:
    def __init__(self, contractId, tariffChecker, date = None):
        # tariffChecker должен предоставить 2 метода:
        # getEventTypeId() -> id типа события
        # recordAcceptable(record) -> запись подходит по полу и возрасту
        self.visitTariffMap = {}
        self.actionTariffMap = {}
        self.financeId = None

        if contractId:
            eventTypeId = tariffChecker.getEventTypeId() if tariffChecker else None
            db = QtGui.qApp.db
            self.financeId = forceRef(db.translate('Contract', 'id', contractId, 'finance_id'))
            table = db.table('Contract_Tariff')
            cond = [table['master_id'].eq(contractId), table['deleted'].eq(0)]
            if eventTypeId:
                cond.append(db.joinOr([table['eventType_id'].eq(eventTypeId),
                                       table['eventType_id'].isNull()
                                      ]))
            records = db.getRecordList(table, 'tariffType, service_id, tariffCategory_id, begDate, endDate, sex, age, price, uet', cond, 'id')
            if date is None:
                date = QtCore.QDate.currentDate()
            for record in records:
                if not tariffChecker or tariffChecker.recordAcceptable(record):
                    begDate = forceDate(record.value('begDate'))
                    endDate = forceDate(record.value('endDate'))
                    if (begDate.isNull() or begDate<=date) and (endDate.isNull() or date<=endDate):
                        tariffType = forceInt(record.value('tariffType'))
                        serviceId = forceRef(record.value('service_id'))
                        tariffCategoryId = forceRef(record.value('tariffCategory_id'))
                        price = forceDouble(record.value('price'))
                        uet = forceDouble(record.value('uet'))
                        # TODO: skkachaev: Что это?
                        if tariffType in (CTariff.ttVisit, CTariff.ttVisit):
                            self._register(self.visitTariffMap, serviceId, tariffCategoryId, price, uet)
                        elif tariffType in (CTariff.ttActionAmount, CTariff.ttActionUET,  CTariff.ttHospitalBedService):
                            self._register(self.actionTariffMap, serviceId, tariffCategoryId, price, uet)


    @staticmethod
    def _register(dataMap, serviceId, tariffCategoryId, price, uet):
        mapTariffCategoryToPriceAndUet = dataMap.setdefault(serviceId, {})
        price_, uet_ = mapTariffCategoryToPriceAndUet.get(tariffCategoryId, (0, 0))
        mapTariffCategoryToPriceAndUet[tariffCategoryId] = price_ + price, uet_ + uet


class CContractTariffCache:
    def __init__(self):
        self.mapContractIdToDecr = {}

    def getTariffDescr(self, contractId, tariffChecker, begDate = None):
        if contractId in self.mapContractIdToDecr:
            return self.mapContractIdToDecr[contractId]
        else:
            result = CContractTariffDescr(contractId, tariffChecker, begDate)
            self.mapContractIdToDecr[contractId] = result
            return result


    @staticmethod
    def getServiceIdList(tariffMap):
         return tariffMap.keys()


    @staticmethod
    def getPriceAndUet(tariffMap, serviceIdList, tariffCategoryId):
        resultPrice = 0.0
        resultUet = 0.0
        for serviceId in serviceIdList:
            mapTariffCategoryToPriceAndUet = tariffMap.get(serviceId, None)
            if mapTariffCategoryToPriceAndUet:
                if tariffCategoryId in mapTariffCategoryToPriceAndUet:
                    priceAndUet = mapTariffCategoryToPriceAndUet.get(tariffCategoryId, None)
                    if priceAndUet:
                        resultPrice += priceAndUet[0]
                        resultUet += priceAndUet[1]
                    if tariffCategoryId:
                        priceAndUet = mapTariffCategoryToPriceAndUet.get(None, None)
                        if priceAndUet:
                            resultPrice += priceAndUet[0]
                            resultUet += priceAndUet[1]
        return resultPrice, resultUet


    @staticmethod
    def getPrice(tariffMap, serviceIdList, tariffCategoryId):
        return CContractTariffCache.getPriceAndUet(tariffMap, serviceIdList, tariffCategoryId)[0]


    @staticmethod
    def getUet(tariffMap, serviceIdList, tariffCategoryId):
        return CContractTariffCache.getPriceAndUet(tariffMap, serviceIdList, tariffCategoryId)[1]
