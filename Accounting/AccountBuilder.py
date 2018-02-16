# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Accounting.Utils import CTariff, createAccountRecord, getClientDiscountInfo, getNextAccountNumber, \
    getNextAccountNumberFromZero, getOrganisationHead, getRefuseTypeId, isTariffApplicable, \
    setActionPayStatus, setEventPayStatus, setEventVisitsPayStatus, setVisitPayStatus, unpackExposeDiscipline, \
    updateAccountRecord, updateDocsPayStatus, getIgnoredCsgList, getExportInfoOFComplexEvent, getMesAmount
from Events.EventInfo import CMesInfo
from Events.MapActionTypeToServiceIdList import CMapActionTypeIdToServiceIdList
from Events.Utils import CFinanceType, CPayStatus, getActionLengthDays, getEventBedProfilesList, getEventLengthDays, \
    getEventProfileId, getEventPurposeCode, getEventServiceId
from Registry.Utils import getClientPolicyByEventId
from library.DbComboBox import CDbDataCache
from library.Preferences import isPython27
from library.PrintInfo import CInfoContext
from library.Utils import addPeriod, calcAgeInYears, firstMonthDay, forceBool, forceDate, forceDateTime, forceDecimal, \
    forceDouble, forceInt, forceRef, forceString, forceStringEx, lastMonthDay, quote, \
    toVariant
from library.crbcombobox import CRBModelDataCache

u"""Утилиты формирования счёта"""

ClinicalExamServiceList = [
    u'B04.026.001.01', u'B04.026.001.02', u'B04.026.001.05', u'B04.026.001.06', u'B04.026.001.09',
    u'B04.026.001.10', u'B04.026.001.17', u'B04.026.001.18', u'B04.026.001.21', u'B04.026.001.22',
    u'B04.026.001.37', u'B04.026.001.38', u'B04.026.001.39', u'B04.026.001.40', u'B04.026.001.41',
    u'B04.026.001.42', u'B04.026.001.54', u'B04.026.001.56', u'B04.026.001.57', u'B04.026.001.60',
    u'B04.026.001.63', u'B04.026.001.64', u'B04.026.001.66', u'B04.026.001.67', u'B04.026.001.68',
    u'B04.026.001.69', u'B04.026.001.70', u'B04.026.001.71', u'B04.026.001.72', u'B04.026.001.73',
    u'B04.026.001.74', u'B04.026.001.75', u'B04.026.001.76', u'B04.026.001.77', u'B04.026.001.78',
    u'B04.026.001.79', u'B04.026.001.80', u'B04.026.001.81', u'B04.026.001.82', u'B04.026.001.83',
    u'B04.026.001.84', u'B04.047.001.01', u'B04.047.001.02', u'B04.047.001.05', u'B04.047.001.06',
    u'B04.047.001.09', u'B04.047.001.10', u'B04.047.001.17', u'B04.047.001.18', u'B04.047.001.21',
    u'B04.047.001.22', u'B04.047.001.37', u'B04.047.001.38', u'B04.047.001.39', u'B04.047.001.40',
    u'B04.047.001.41', u'B04.047.001.42', u'B04.047.001.53', u'B04.047.001.55', u'B04.047.001.56',
    u'B04.047.001.59', u'B04.047.001.62', u'B04.047.001.63', u'B04.047.001.65', u'B04.047.001.66',
    u'B04.047.001.67', u'B04.047.001.68', u'B04.047.001.69', u'B04.047.001.70', u'B04.047.001.71',
    u'B04.047.001.72', u'B04.047.001.73', u'B04.047.001.74', u'B04.047.001.75', u'B04.047.001.76',
    u'B04.047.001.77', u'B04.047.001.78'
]


class CAccountDetails:
    def __init__(self, contractInfo, orgId, orgStructureId, date, reexpose, payer=None, dbName=None):
        self.contractInfo = contractInfo
        self.date = date
        self.dbName = dbName if dbName else forceString(QtGui.qApp.db.db.databaseName())
        self.id, self.record = createAccountRecord(contractInfo, orgId, orgStructureId, date, payer, self.dbName)
        self.reexpose = reexpose
        self.totalAmount = forceDecimal(0)
        self.totalUet = 0
        self.totalSum = forceDecimal(0)

    def update(self, date, numberSuffix):
        updateAccountRecord(self.record, self.contractInfo, date, numberSuffix, self.totalAmount, self.totalUet,
                            self.totalSum, self.dbName)

    def changeNumber(self, number, step=False, fromZero=False):
        """Изменение номера счета.

        @param number: новый номер счета.
        @param step: при наличии счетов с таким же номером, указывать тираж
        @param fromZero: используется только при step = True. Если fromZero установлен, то первый счет идет как number, остальные - number-1, number-2 и т.д. В противном случае первый счет идет как number-1.
        """
        if step:
            if fromZero:
                number = getNextAccountNumberFromZero(number)
            else:
                number = getNextAccountNumber(number)
        self.record.setValue('number', number)
        QtGui.qApp.db.updateRecord(self.dbName + '.Account', self.record)


class CAccountPool:
    def __init__(self, contractInfo, orgId, orgStructureId, date, reexposeInSeparateAccount, dbName=None):
        self.contractInfo = contractInfo
        self.orgId = orgId
        self.orgStructureId = orgStructureId
        self.date = date
        self.reexposeInSeparateAccount = reexposeInSeparateAccount
        self.dbName = dbName if dbName else forceString(QtGui.qApp.db.db.databaseName())
        self.mapKeyExToDetails = {}
        self.mapInsurerIdToKey = {}

        self.exposeByEvent, self.exposeByEventType, self.exposeByMonth, self.exposeByClient, self.exposeByInsurer, self.exposeByServiceArea = unpackExposeDiscipline(
            self.contractInfo.exposeDiscipline)
        if self.contractInfo.exposeDiscipline == 0:
            self.getKey = self._getTrivialKey
            self.fixDate = self._trivialFixDate
        elif self.exposeByEvent:
            self.getKey = self._getEventKey
            self.fixDate = self._trivialFixDate
        elif self.exposeByMonth and not self.exposeByClient and not self.exposeByInsurer:
            self.getKey = self._getMonthKey
            self.fixDate = self._fixDate
        elif self.exposeByClient and not self.exposeByMonth:
            self.getKey = self._getClientKey
            self.fixDate = self._trivialFixDate
        elif self.exposeByInsurer and not self.exposeByMonth:
            self.getKey = self._getInsurerKey
            self.fixDate = self._trivialFixDate
        elif self.exposeByEventType or self.exposeByServiceArea or self.exposeByInsurer:
            keyList = []
            if self.exposeByEventType:
                keyList.append(self._getEventTypeKey)
            if self.exposeByServiceArea:
                keyList.append(self._getServiceAreaKey)
            if self.exposeByInsurer:
                keyList.append(self._getInsurerKey)
            self.getKey = self.makeComplexKey(keyList)
            self.fixDate = self._trivialFixDate
        else:
            self.getKey = self._getComplexKey
            self.fixDate = self._fixDateFromComplexKey

    def createAccount(self, reexpose, payer=None):
        return CAccountDetails(self.contractInfo, self.orgId, self.orgStructureId, self.date, reexpose, payer,
                               self.dbName)

    def _getAccount(self, key, reexpose, payer=None):
        reexpose = bool(self.reexposeInSeparateAccount and reexpose)
        result = self.mapKeyExToDetails.get((key, reexpose), None)
        if result is None:
            result = self.createAccount(reexpose, payer)
            self.mapKeyExToDetails[(key, reexpose)] = result
        return result

    def makeComplexKey(self, keyList):
        return lambda clientId, date, eventId, eventTypeId: tuple(
            [key(clientId, date, eventId, eventTypeId) for key in keyList])

    def _getTrivialKey(self, clientId, date, eventId, eventTypeId):
        return None

    def _getEventKey(self, clientId, date, eventId, eventTypeId):
        return eventId

    def _getEventTypeKey(self, clientId, date, eventId, eventTypeId):
        return eventTypeId

    def _getMonthKey(self, clientId, date, eventId, eventTypeId):
        return firstMonthDay(date).toPyDate()

    def _getClientKey(self, clientId, date, eventId, eventTypeId):
        return clientId

    def _getInsurerKey(self, clientId, date, eventId, eventTypeId):
        from Orgs.Utils import getOrganisationShortName

        def _getInsurerKeyByInsurerId(insurerId):
            result = self.mapInsurerIdToKey.get(insurerId, None)
            if result is None:
                if insurerId:
                    tmpInsurerId = insurerId
                    db = QtGui.qApp.db
                    table = db.table('Organisation')
                    if self.exposeByInsurer == 1:
                        while True:
                            headId = forceRef(db.translate(table, 'id', tmpInsurerId, 'head_id'))
                            if headId:
                                tmpInsurerId = headId
                            else:
                                break
                    result = forceString(db.translate(table, 'id', tmpInsurerId, 'infisCode'))
                    if not result:
                        result = getOrganisationShortName(tmpInsurerId)
                    if not result:
                        result = '{%d}' % tmpInsurerId
                else:
                    result = u'CK не указана'
                self.mapInsurerIdToKey[insurerId] = result
            return result

        if clientId:
            if self.contractInfo.financeType == CFinanceType.VMI:
                record = getClientPolicyByEventId(eventId, date)
            else:
                record = getClientPolicyByEventId(eventId, date)
            if record:
                insurerId = forceRef(record.value('insurer_id'))
                return _getInsurerKeyByInsurerId(insurerId)
        return u'нет полиса'

    # TODO: mdldml: наверное, кэш добавить
    def _getServiceAreaKey(self, clientId, date, eventId, eventTypeId):
        from Registry.Utils import getClientCompulsoryPolicy, getClientVoluntaryPolicy
        db = QtGui.qApp.db

        areaType = False
        if clientId:
            record = getClientVoluntaryPolicy(clientId,
                                              date) if self.contractInfo.financeType == CFinanceType.VMI else getClientCompulsoryPolicy(
                clientId, date)
            if record:
                insurerId = forceInt(record.value('insurer_id'))
                if insurerId:
                    query = db.query('SELECT insurerServiceAreaMatch(%d, %s, %s, %s)' % (
                        insurerId, 2, quote(QtGui.qApp.defaultKLADR()), quote(QtGui.qApp.provinceKLADR())))
                    if query.first():
                        areaType = forceBool(query.record().value(0))
        return u'краевые' if areaType else u'инокраевые'

    def _getComplexKey(self, clientId, date, eventId, eventTypeId):
        return (self._getMonthKey(clientId, date, eventId, eventTypeId) if self.exposeByMonth else None,
                self._getClientKey(clientId, date, eventId, eventTypeId) if self.exposeByClient else None,
                self._getInsurerKey(clientId, date, eventId, eventTypeId) if self.exposeByInsurer else None,
                )

    def _trivialFixDate(self, key):
        return self.date

    def _fixDate(self, key):
        return min(self.date, lastMonthDay(QtCore.QDate(key)))

    def _fixDateFromComplexKey(self, key):
        if self.exposeByMonth:
            return self._fixDate(key[0])
        else:
            return self._trivialFixDate(key)

    def getAccount(self, clientId, date, eventId, eventTypeId, reexpose=False):
        if self.exposeByInsurer:
            # if self.contractInfo.financeType == CFinanceType.VMI:
            #     record = getClientVoluntaryPolicy(clientId, date)
            # else:
            #     record = getClientCompulsoryPolicy(clientId, date)
            record = getClientPolicyByEventId(eventId, date)
            if record:
                insurerId = forceRef(record.value('insurer_id'))
            else:
                insurerId = None
        else:
            insurerId = None
        return self._getAccount(self.getKey(clientId, date, eventId, eventTypeId), reexpose,
                                getOrganisationHead(insurerId))

    def addAccountIfEmpty(self, reexpose=False):
        if not self.mapKeyExToDetails:
            self.getAccount(None, self.date, None, None, False)
            if reexpose and self.reexposeInSeparateAccount:
                self.getAccount(None, self.date, None, None, True)

    def getDetailsList(self):
        return [details for key, details in sorted(self.mapKeyExToDetails.iteritems())]

    def getAccountIdList(self):
        return [details.id for details in self.getDetailsList()]

    def updateDetails(self):
        for (key, reexpose), details in sorted(self.mapKeyExToDetails.iteritems()):
            details.update(self.fixDate(key), self.fixNumber(key, reexpose))

    def fixNumber(self, key, reexpose):
        result = ''
        if isinstance(key, tuple) and len(key) == 3 and self.exposeByMonth:
            date, clientId, insurer = key
            if self.exposeByClient and clientId:
                result += '/%s' % clientId
            if self.exposeByInsurer and insurer:
                result += '/%s' % insurer
        elif isinstance(key, tuple):
            for keyElement in key:
                if keyElement is not None:
                    result += '/%s' % forceString(keyElement)
        elif self.exposeByClient or self.exposeByEvent or self.exposeByInsurer:
            if key:
                result += '/%s' % key
        if reexpose:
            result += u'/П'
        return result


class CAccountBuilder:
    def __init__(self, accountingDBName=None):
        self.mapHtgIdToServiceId = {}
        self.mapMesIdToServiceId = {}
        self.mapMesIdToNorm = {}
        self.semifinishedMesRefuseTypeId = None
        self.mapEventIdToMKB = {}
        self.mapEventIdToRelatedEventInfo = {}
        self.missedEventInfo = {}
        self.infoContext = CInfoContext()
        # i2776: список КСГ, которые не стоит учитывать при формировании счета
        self.ignoredCsg = None
        self.accountingDBName = accountingDBName if accountingDBName else forceString(QtGui.qApp.db.db.databaseName())
        self.accountingDBName = '`' + self.accountingDBName + '`'

    def isCompletenessAllRelatedEvent(self, eventId):
        if not self.mapEventIdToRelatedEventInfo.has_key(eventId):
            tableEvent = QtGui.qApp.db.table('Event')
            relateEventIdSet = set(QtGui.qApp.db.getAllRelated(table=tableEvent,
                                                               idList=[eventId],
                                                               groupCol=tableEvent['prevEvent_id'],
                                                               idCol=tableEvent['id'],
                                                               maxLevels=32))
            # Создаем словарь, содержащий информацию (список id и признак законченности группы) о всей группе связанных событий
            # Считая изначально, что группа завершена
            eventRelatedInfo = {'eventIdSet': relateEventIdSet,
                                'isCompleteness': True}

            # Не проверять законченность связанных событий, если в этом списке только одно, текущее событие (т.е. у него нет связанных)
            if len(relateEventIdSet) == 1:
                self.mapEventIdToRelatedEventInfo[eventId] = eventRelatedInfo
            else:
                for eventId in relateEventIdSet:
                    # Корректируем данные по флагу завершенности на основе даты окончания каждого элемента группы
                    eventRecord = QtGui.qApp.db.getRecord(tableEvent, 'execDate', eventId)
                    isEventComplete = (not eventRecord.value(0).isNull()) if eventRecord else True
                    eventRelatedInfo['isCompleteness'] &= isEventComplete
                    # Связываем id текущего события с информацией о группе
                    self.mapEventIdToRelatedEventInfo[eventId] = eventRelatedInfo

        return self.mapEventIdToRelatedEventInfo.get(eventId, {}).get('isCompleteness', True)

    def resetBuilder(self):
        self.mapHtgIdToServiceId.clear()
        self.mapMesIdToServiceId.clear()
        self.mapMesIdToNorm.clear()
        self.mapEventIdToMKB.clear()
        self.semifinishedMesRefuseTypeId = None
        self.mapEventIdToRelatedEventInfo = {}
        self.missedEventInfo = {}
        del self.infoContext
        self.infoContext = CInfoContext()

    def exposeByEvents(self, progressDialog, contractInfo, accountFactory, eventIdList, checkMes,
                       acceptNewKSLPForChild=False
                       ):
        for eventId in eventIdList:
            if progressDialog:
                progressDialog.step()
                QtGui.qApp.processEvents()
            self.exposeEvent(contractInfo, accountFactory, eventId)
            self.exposeEventAsCoupleVisit(contractInfo, accountFactory, eventId)
            self.exposeEventByHospitalBedDay(contractInfo, accountFactory, eventId)
            self.exposeVisitsByMes(contractInfo, accountFactory, eventId, checkMes)
            self.exposeEventByHTG(contractInfo, accountFactory, eventId)
            isExposed = self.exposeEventByCsg(contractInfo, accountFactory, eventId, acceptNewKSLPForChild)
            if not isExposed:
                self.exposeEventByMes(contractInfo, accountFactory, eventId)

    def exposeByVisitsByActionServices(self, progressDialog, contractInfo, accountFactory, mapServiceIdToVisitIdList):
        for serviceId, visitIdList in mapServiceIdToVisitIdList.items():
            for visitId in visitIdList:
                if progressDialog:
                    progressDialog.step()
                    QtGui.qApp.processEvents()
                self.exposeVisitByActionService(contractInfo, accountFactory, serviceId, visitId)

    def exposeByVisits(self, progressDialog, contractInfo, accountFactory, visitIdList):
        for visitId in visitIdList:
            if progressDialog:
                progressDialog.step()
                QtGui.qApp.processEvents()
            self.exposeVisit(contractInfo, accountFactory, visitId)
            self.exposeVisitByActionUET(contractInfo, accountFactory, visitId)
            self.exposeVisitByClinicalExamService(contractInfo, accountFactory, visitId)

    def exposeByActions(self, progressDialog, contractInfo, accountFactory, actionIdList, date=None, checkMes=False,
                        franchisePercent=0):
        for actionId in actionIdList:
            if progressDialog:
                progressDialog.step()
                QtGui.qApp.processEvents()
            self.exposeActionsByMes(contractInfo, accountFactory, actionId, date, checkMes,
                                    franchisePercent=franchisePercent)
            self.exposeAction(contractInfo, accountFactory, actionId, date, franchisePercent=franchisePercent)
            self.exposeActionByClinicalExam(contractInfo, accountFactory, actionId, date,
                                            franchisePercent=franchisePercent)

    def exposeByHospitalBedActionProperties(self, progressDialog, contractInfo, accountFactory, actionPropertyIdList,
                                            checkCalendarDaysLength):
        for actionPropertyId in actionPropertyIdList:
            if progressDialog:
                progressDialog.step()
                QtGui.qApp.processEvents()
            self.exposeHospitalBedActionProperty(contractInfo, accountFactory, actionPropertyId,
                                                 checkCalendarDaysLength)

    def exposeEvent(self, contractInfo, accountFactory, eventId):
        db = QtGui.qApp.db

        if not self.isCompletenessAllRelatedEvent(eventId):
            self.missedEventInfo.setdefault(eventId, {}).setdefault('errorMesages', []).append(
                u'Найдены незакрытые связанные обращения')
            return

        event = db.getRecord(table='Event '
                                   ' LEFT JOIN Person ON Person.id = Event.execPerson_id',
                             cols=['Event.client_id',
                                   'Event.execDate',
                                   'Event.eventType_id',
                                   'Person.tariffCategory_id',
                                   ],
                             itemId=eventId)

        eventEndDate = forceDate(event.value('execDate'))
        eventTypeId = forceRef(event.value('eventType_id'))
        tariffCategoryId = forceRef(event.value('tariffCategory_id'))
        tariffList = contractInfo.tariffByEventType.get(eventTypeId, None)
        if tariffList:
            for tariff in tariffList:
                if isTariffApplicable(tariff, eventId, tariffCategoryId, eventEndDate,
                                      mapEventIdToMKB=self.mapEventIdToMKB):
                    groupInOneAccount = forceInt(
                        CDbDataCache.getData('EventType', 'exposeGrouped', 'id = %d' % eventTypeId, None, None).strList[
                            0])
                    clientId = forceRef(event.value('client_id'))
                    serviceId = getEventServiceId(eventTypeId)
                    price = forceDecimal(tariff.price)
                    federalPrice = forceDecimal(0)
                    if contractInfo.isConsiderFederalPrice:
                        federalPrice = forceDecimal(tariff.federalPrice)
                    discount = getClientDiscountInfo(clientId)[0]
                    price *= forceDecimal(1.0) - discount
                    amount = forceDecimal(1.0)
                    sum = (forceDecimal(price) + forceDecimal(federalPrice)) * forceDecimal(amount)
                    account = accountFactory(clientId, eventEndDate, eventId,
                                             eventTypeId if not groupInOneAccount else groupInOneAccount)
                    tableAccountItem = db.table(self.accountingDBName + '.Account_Item')
                    accountItem = tableAccountItem.newRecord()
                    accountItem.setValue('master_id', toVariant(account.id))
                    accountItem.setValue('serviceDate', toVariant(eventEndDate))
                    accountItem.setValue('event_id', toVariant(eventId))
                    accountItem.setValue('price', toVariant(price))
                    accountItem.setValue('unit_id', toVariant(tariff.unitId))
                    accountItem.setValue('amount', toVariant(amount))
                    accountItem.setValue('sum', toVariant(sum))
                    accountItem.setValue('tariff_id', toVariant(tariff.id))
                    accountItem.setValue('service_id', toVariant(serviceId))
                    db.insertRecord(tableAccountItem, accountItem)
                    account.totalAmount += amount
                    account.totalSum += sum
                    setEventPayStatus(eventId, contractInfo.payStatusMask, CPayStatus.exposedBits)
                    return

    def exposeEventAsCoupleVisit(self, contractInfo, accountFactory, eventId):
        db = QtGui.qApp.db

        if not self.isCompletenessAllRelatedEvent(eventId):
            self.missedEventInfo.setdefault(eventId, {}).setdefault('errorMesages').append(
                u'Найдены незакрытые связанные обращения')
            return

        event = db.getRecord(table='Event '
                                   ' LEFT JOIN Person ON Person.id = Event.execPerson_id',
                             cols=['Event.client_id',
                                   'Event.execDate',
                                   'Event.eventType_id',
                                   'Person.tariffCategory_id',
                                   ],
                             itemId=eventId)
        eventEndDate = forceDate(event.value('execDate'))
        eventTypeId = forceRef(event.value('eventType_id'))
        tariffCategoryId = forceRef(event.value('tariffCategory_id'))
        tariffList = contractInfo.tariffByCoupleVisitEventType.get(eventTypeId, None)
        if tariffList:
            for tariff in tariffList:
                if isTariffApplicable(tariff, eventId, tariffCategoryId, eventEndDate,
                                      mapEventIdToMKB=self.mapEventIdToMKB):
                    groupInOneAccount = forceInt(
                        CDbDataCache.getData('EventType', 'exposeGrouped', 'id = %d' % eventTypeId, None, None).strList[
                            0])
                    serviceId = tariff.serviceId
                    count = db.getCount('Visit', '1',
                                        'event_id=%d AND service_id=%d AND deleted=0' % (eventId, serviceId))
                    if count == 0:
                        continue
                    amount = forceDecimal(count)
                    clientId = forceRef(event.value('client_id'))
                    federalPrice = forceDecimal(0)
                    if contractInfo.isConsiderFederalPrice:
                        federalPrice = forceDecimal(tariff.federalPrice)
                    amount, price, sum = tariff.evalAmountPriceSum(amount, clientId)
                    sum += federalPrice * amount
                    account = accountFactory(clientId, eventEndDate, eventId,
                                             eventTypeId if not groupInOneAccount else groupInOneAccount)
                    tableAccountItem = db.table(self.accountingDBName + '.Account_Item')
                    accountItem = tableAccountItem.newRecord()
                    accountItem.setValue('master_id', toVariant(account.id))
                    accountItem.setValue('serviceDate', toVariant(eventEndDate))
                    accountItem.setValue('event_id', toVariant(eventId))
                    accountItem.setValue('price', toVariant(price))
                    accountItem.setValue('unit_id', toVariant(tariff.unitId))
                    accountItem.setValue('amount', toVariant(amount))
                    accountItem.setValue('sum', toVariant(sum))
                    accountItem.setValue('tariff_id', toVariant(tariff.id))
                    accountItem.setValue('service_id', toVariant(serviceId))
                    db.insertRecord(tableAccountItem, accountItem)
                    account.totalAmount += amount
                    account.totalSum += sum
                    setEventPayStatus(eventId, contractInfo.payStatusMask, CPayStatus.exposedBits)

    def exposeEventByHospitalBedDay(self, contractInfo, accountFactory, eventId):
        db = QtGui.qApp.db

        if not self.isCompletenessAllRelatedEvent(eventId):
            self.missedEventInfo.setdefault(eventId, {}).setdefault('errorMesages').append(
                u'Найдены незакрытые связанные обращения')
            return

        event = db.getRecord(table='Event'
                                   ' LEFT JOIN Person ON Person.id = Event.execPerson_id',
                             cols=['Event.client_id',
                                   'Event.setDate',
                                   'Event.execDate',
                                   'Event.eventType_id',
                                   'Person.tariffCategory_id',
                                   ],
                             itemId=eventId)

        eventBegDate = forceDate(event.value('setDate'))
        eventEndDate = forceDate(event.value('execDate'))
        eventTypeId = forceRef(event.value('eventType_id'))
        tariffCategoryId = forceRef(event.value('tariffCategory_id'))
        if eventBegDate.isValid() and eventEndDate.isValid() and eventBegDate <= eventEndDate:
            tariffList = contractInfo.tariffByHospitalBedDay.get(eventTypeId, None)
            if tariffList:
                for tariff in tariffList:
                    if isTariffApplicable(tariff, eventId, tariffCategoryId, eventEndDate,
                                          mapEventIdToMKB=self.mapEventIdToMKB):
                        groupInOneAccount = forceInt(
                            CDbDataCache.getData('EventType', 'exposeGrouped', 'id = %d' % eventTypeId, None,
                                                 None).strList[0])
                        count = eventBegDate.daysTo(eventEndDate) + 1
                        amount = forceDecimal(count)
                        clientId = forceRef(event.value('client_id'))
                        federalPrice = forceDecimal(0)
                        if contractInfo.isConsiderFederalPrice:
                            federalPrice = forceDecimal(tariff.federalPrice)
                        amount, price, sum = tariff.evalAmountPriceSum(amount, clientId)
                        sum += federalPrice * amount
                        account = accountFactory(clientId, eventEndDate, eventId,
                                                 eventTypeId if not groupInOneAccount else groupInOneAccount)
                        tableAccountItem = db.table(self.accountingDBName + '.Account_Item')
                        accountItem = tableAccountItem.newRecord()
                        accountItem.setValue('master_id', toVariant(account.id))
                        accountItem.setValue('serviceDate', toVariant(eventEndDate))
                        accountItem.setValue('event_id', toVariant(eventId))
                        accountItem.setValue('price', toVariant(price))
                        accountItem.setValue('unit_id', toVariant(tariff.unitId))
                        accountItem.setValue('amount', toVariant(amount))
                        accountItem.setValue('sum', toVariant(sum))
                        accountItem.setValue('tariff_id', toVariant(tariff.id))
                        db.insertRecord(tableAccountItem, accountItem)
                        account.totalAmount += amount
                        account.totalSum += sum
                        setEventPayStatus(eventId, contractInfo.payStatusMask, CPayStatus.exposedBits)
                        return

    def exposeVisitsByMes(self, contractInfo, accountFactory, eventId, checkMes):
        db = QtGui.qApp.db

        if not self.isCompletenessAllRelatedEvent(eventId):
            self.missedEventInfo.setdefault(eventId, {}).setdefault('errorMesages').append(
                u'Найдены незакрытые связанные обращения')
            return

        event = db.getRecord(table='Event '
                                   ' LEFT JOIN Person ON Person.id = Event.execPerson_id',
                             cols=['Event.client_id',
                                   'Event.execDate',
                                   'Event.eventType_id',
                                   'Event.MES_id',
                                   'Person.tariffCategory_id',
                                   ],
                             itemId=eventId)
        eventEndDate = forceDate(event.value('execDate'))
        eventTypeId = forceRef(event.value('eventType_id'))
        mesId = forceRef(event.value('MES_id'))
        serviceId = self.getMesService(mesId)
        tariffCategoryId = forceRef(event.value('tariffCategory_id'))
        tariffList = contractInfo.tariffVisitsByMES.get((eventTypeId, serviceId), None)
        if tariffList and mesId:
            for tariff in tariffList:
                if isTariffApplicable(tariff, eventId, tariffCategoryId, eventEndDate,
                                      mapEventIdToMKB=self.mapEventIdToMKB):
                    groupInOneAccount = forceInt(
                        CDbDataCache.getData('EventType', 'exposeGrouped', 'id = %d' % eventTypeId, None, None).strList[
                            0])
                    amount, realAmount = getMesAmount(eventId, mesId)
                    amount, realAmount = forceDecimal(amount), forceDecimal(realAmount)
                    clientId = forceRef(event.value('client_id'))
                    federalPrice = forceDecimal(0)
                    if contractInfo.isConsiderFederalPrice:
                        federalPrice = forceDecimal(tariff.federalPrice)
                    amount, price, sum = tariff.evalAmountPriceSum(amount, clientId)
                    sum = (price + federalPrice) * amount
                    uet = amount * forceDecimal(tariff.uet)
                    account = accountFactory(clientId, eventEndDate, eventId,
                                             eventTypeId if not groupInOneAccount else groupInOneAccount)
                    tableAccountItem = db.table(self.accountingDBName + '.Account_Item')
                    accountItem = tableAccountItem.newRecord()
                    accountItem.setValue('master_id', toVariant(account.id))
                    accountItem.setValue('serviceDate', toVariant(eventEndDate))
                    accountItem.setValue('event_id', toVariant(eventId))
                    accountItem.setValue('price', toVariant(price))
                    accountItem.setValue('unit_id', toVariant(tariff.unitId))
                    accountItem.setValue('amount', toVariant(realAmount))  # amount
                    accountItem.setValue('sum', toVariant(sum))
                    accountItem.setValue('uet', toVariant(uet))
                    accountItem.setValue('tariff_id', toVariant(tariff.id))
                    accountItem.setValue('service_id', toVariant(serviceId))
                    if checkMes:
                        norm = self.getMesNorm(mesId)
                        if amount < norm:
                            self.rejectAccountItemBySemifinishedMes(accountItem, contractInfo.finance_id)
                    db.insertRecord(tableAccountItem, accountItem)
                    account.totalAmount += realAmount  # amount
                    account.totalSum += sum
                    account.totalUet += uet
                    setEventPayStatus(eventId, contractInfo.payStatusMask, CPayStatus.exposedBits)
                    setEventVisitsPayStatus(eventId, contractInfo.payStatusMask, CPayStatus.exposedBits)
                    return

    def exposeEventByCsg(self, contractInfo, accountFactory, eventId, acceptNewKSLPForChild=False):
        isPregnancyPathology = False
        isPregnancy = False
        # realKD = None
        # i2776: beg
        if self.ignoredCsg is None:
            self.ignoredCsg = getIgnoredCsgList()

        for x in self.ignoredCsg:
            if eventId == x['idIgnoredCsg']:
                # if not (x['diagnosis'] == u'O34.2' and 2 <= x['duration'] < 6):
                return False
        # i2776: end

        # i3894c16197: beg
        if QtGui.qApp.currentOrgInfis() in (u'07112', u'07108', u'07526'):
            exportInfo = getExportInfoOFComplexEvent(eventId)
            if exportInfo:
                curDate = self.date  # дата формирования счета
                if curDate.year() < exportInfo['exportYear'] or curDate.month() < exportInfo['exportMonth']:
                    return False
        # i3894c16197: beg

        oncoMKBList = ['C81.0', 'C81.1', 'C81.2', 'C81.3', 'C81.7', 'C81.9',
                       'C83.0', 'C83.1', 'C83.3', 'C83.4', 'C83.5', 'C83.7', 'C83.8', 'C83.9',
                       'C84.1', 'C84.4', 'C85.7', 'C85.9', 'C91.0', 'C91.1', 'C91.4',
                       'C92.0', 'C92.1', 'C93.0', 'C96.1', 'C96.2',
                       'D53.1', 'D56.0', 'D56.1', 'D58.0', 'D58.8', 'D58.9',
                       'D59.0', 'D59.1', 'D59.8', 'D60.9', 'D61.0', 'D61.3', 'D61.8', 'D61.9',
                       'D66', 'D67', 'D68.0', 'D69.1', 'D69.2', 'D69.3', 'D69.8', 'D70', 'D71',
                       'D72.0', 'D72.8', 'D72.9', 'D75.8', 'D75.9', 'D80.0', 'D81.0', 'D81.1',
                       'D82.0', 'D84.0', 'D89.0', 'D89.9']

        def getServiceList():
            return db.getColumnValues(table=u'''Action INNER JOIN ActionType ON ActionType.id = Action.actionType_id''',
                                      column='code',
                                      where=u'''Action.event_id = %s AND Action.deleted = 0 AND ActionType.deleted = 0''' % eventId)

        def hasComlexService():
            codes = getServiceList()
            spr73 = [[forceString(record.value('CODE')), forceString(record.value('CODE2'))] for record in
                     db.getRecordList('mes.SPR73', '*')]
            for r in spr73:
                if r[0] in codes:
                    # TODO:skkachaev: здесть должен быть multiset, но его нет :(
                    flag = False
                    codes1 = []
                    for c in codes:
                        if (c != r[0]) or flag:
                            codes1.append(c)
                        else:
                            flag = True
                    if r[1] in codes1: return True

            return False

        def hasMesService(serviceList, KSG):
            t = db.table('mes.SPR69')
            return bool(db.getCount(table=t,
                                    countCol=t['id'],
                                    where=db.joinAnd([
                                        t['KUSL'].inlist(serviceList),
                                        t['KSG'].eq(KSG),
                                        db.joinOr([
                                            t['KUSL'].like(u'A03%%'),
                                            t['KUSL'].like(u'A11%%'),
                                            t['KUSL'].like(u'A14%%'),
                                            t['KUSL'].like(u'A16%%'),
                                            t['KUSL'].like(u'A22%%')
                                        ])
                                    ])))

        def isExtraLong(endDate, CSG):
            t = db.table('mes.SPR72')
            return bool(db.getCount(table=t,
                                    countCol=t['id'],
                                    where=db.joinAnd([
                                        t['CODE'].eq(CSG),
                                        t['begDate'].le(endDate),
                                        t['endDate'].ge(endDate)
                                    ])))

        def isUltraShort(endDate, CSG):
            t = db.table('mes.SPR71')
            return bool(db.getCount(table=t,
                                    countCol=t['id'],
                                    where=db.joinAnd([
                                        t['CODE'].eq(CSG),
                                        t['begDate'].le(endDate),
                                        t['endDate'].ge(endDate)
                                    ])))

        # оплата ЭКО по законченному случаю в размере 100 % действует с 01.03.2016, согласно доп.соглашению от 31.03.16 №2 к ТС КК от 28.01.16.
        def isEKO(serviceList, endDate, mesCode):
            return u'A11.20.027' in serviceList and endDate.date() >= QtCore.QDate(2016, 3, 1) and (
                mesCode.startswith('g40') or mesCode.startswith('g50'))

        def isOncoOperation(serviceList):
            return u'A25.05.001' in serviceList \
                   or u'A25.05.002' in serviceList \
                   or u'A25.05.003' in serviceList \
                   or u'A25.05.004' in serviceList \
                   or u'A25.05.005' in serviceList \
                   or u'A25.30.033' in serviceList \
                   or u'A25.30.033.001' in serviceList \
                   or u'A25.30.033.002' in serviceList \
                   or u'A25.30.033.007' in serviceList \
                   or u'A25.30.038' in serviceList

        def isNotForKSLPForChild(code):
            return code.startswith('g10') and (
                code.endswith('.105')
                or code.endswith('.106')
                or code.endswith('.107')
                or code.endswith('.108')
                or code.endswith('.109')
                or code.endswith('.110')
                or code.endswith('.111')
            )

        def getVMP32StentCoeff(eventTypeId):
            """
            Логика для оплаты случаев лечения при оказании высокотехнологичной мед.помощи (ВМП) по профилю
            "сердечно-сосудистая хирургия" с учетом количества устанавливаемых стентов.

            При формировании счета для экшенов, у которых указано количество стентов, применяем соответствующие
            коэффициенты к тарифу:
            * 1 стент - коэф. 0,8;
            * 2 - 1,1;
            * 3 - 1,4.

            :param eventTypeId: тип события
            :return: значение кэффициента
            """
            stent = forceDecimal(1)

            # vmp = forceString(db.translate(
            #     'EventType INNER JOIN rbMedicalAidKind rbm ON rbm.id = EventType.medicalAidKind_id',
            #     'rbm.federalCode',
            #     eventTypeId,
            #     'EventType.medicalAidKind_id'
            # ))
            # if vmp == '32':
            #     record = db.getRecordEx(stmt=u"""
            #     SELECT
            #         aps.value AS stent
            #     FROM
            #         Action a
            #         JOIN ActionPropertyType apt ON a.actionType_id = apt.actionType_id
            #         JOIN ActionProperty ap ON a.id = ap.action_id AND apt.id = ap.type_id
            #         JOIN ActionProperty_String aps ON ap.id = aps.id
            #     WHERE
            #     a.deleted = 0
            #     AND a.event_id = {eventId}
            #     AND a.id = {actionId}
            #     AND apt.shortName = 'stent'
            #     """.format(eventId=eventId, actionId=forceInt(record.value('action_id'))))
            #
            #     if record:
            #         stentCount = forceRef(record.value('stent'))
            #
            #         if stentCount == 1:
            #             stent = forceDecimal(0.8)
            #         elif stentCount == 2:
            #             stent = forceDecimal(1.1)
            #         elif stentCount == 3:
            #             stent = forceDecimal(1.4)

            return stent

        db = QtGui.qApp.db

        if not contractInfo.tariffEventByCSG:
            return False
        if not self.isCompletenessAllRelatedEvent(eventId):
            self.missedEventInfo.setdefault(eventId, {}).setdefault('errorMesages').append(
                u'Найдены незакрытые связанные обращения')
            return False

        event = db.getRecord(table=u'Event'
                                   # u' INNER JOIN EventType ON EventType.id = Event.eventType_id'
                                   # u' INNER JOIN rbEventTypePurpose ON rbEventTypePurpose.id = EventType.purpose_id'
                                   u' LEFT JOIN Person ON Person.id = Event.execPerson_id'
                                   u' LEFT JOIN Client ON Client.id = Event.client_id'
                                   u' LEFT JOIN mes.MES ON MES.id = Event.MES_id'
                                   u' LEFT JOIN mes.MES CSG ON CSG.id = Event.KSG_id'
                                   u' LEFT JOIN Diagnostic ON Event.id = Diagnostic.event_id'
                                   u' LEFT JOIN Diagnosis ON Diagnostic.diagnosis_id = Diagnosis.id',
                             cols=[u'Event.client_id',
                                   u'Event.setDate',
                                   u'Event.execDate',
                                   u'Event.eventType_id',
                                   u'Event.MES_id',
                                   u'Event.KSG_id',
                                   u'Event.hospParent',
                                   # u'rbEventTypePurpose.regionalCode AS purposeRegionalCode',
                                   u'MES.code AS mesCode',
                                   u'CSG.code AS csgCode',
                                   u'Person.tariffCategory_id',
                                   u'Client.birthDate',
                                   u'Diagnosis.MKB',
                                   ],
                             itemId=eventId)
        eventBegDate = forceDateTime(event.value('setDate'))
        # i2776: задаем начальную дату от проигнорированного ксг
        for x in self.ignoredCsg:
            if eventId == x['idCsg']:
                isPregnancyPathology = True and x['duration'] >= 2
                isPregnancy = True
                # realKD = x['kd']
                eventBegDate = forceDateTime(x['date'])
                break

        eventEndDate = forceDateTime(event.value('execDate'))
        eventTypeId = forceRef(event.value('eventType_id'))
        isHospWithParent = forceBool(event.value('hospParent'))

        mesId = forceRef(event.value('MES_id'))
        mesCode = forceString(event.value('mesCode')).lower()

        if QtGui.qApp.region() == '23':
            csgId = forceRef(event.value('KSG_id'))
            csgCode = forceString(event.value('csgCode')).lower()
            if csgId:
                mesId = csgId
                mesCode = csgCode

        serviceId = self.getMesService(mesId)
        serviceList = getServiceList()

        tariffDate = eventEndDate  # Дата для выбора подходящего тарифа
        tariffCategoryId = forceRef(event.value('tariffCategory_id'))
        tariffList = contractInfo.tariffEventByCSG.get(serviceId, None)

        clientBirthDate = forceDate(event.value('birthDate'))
        bedProfileCodes = getEventBedProfilesList(eventId)

        if not mesCode.startswith('g70'):
            if mesCode.startswith('g40') or mesCode.startswith('g50'):
                countRedDays = False
            else:
                countRedDays = True
            eventLengthDays = getEventLengthDays(eventBegDate, eventEndDate, countRedDays, eventTypeId)
        else:
            eventLengthDays = db.getCount(table=None,
                                          stmt=u'''SELECT count(Visit.id) FROM Event INNER JOIN Visit ON Visit.event_id = Event.id WHERE Event.id = %i''' % eventId)

        # FIXM: костыль, нужно разобраться с подсчетом к/д
        # if realKD is not None and realKD != eventLengthDays:
        #     eventLengthDays = realKD

        mkb = forceString(event.value('MKB'))

        isExtraLong = isExtraLong(eventEndDate, mesCode)
        isUltraShort = isUltraShort(eventEndDate, mesCode)

        if tariffList and mesId:
            for tariff in tariffList:
                if isTariffApplicable(tariff, eventId, tariffCategoryId, tariffDate,
                                      mapEventIdToMKB=self.mapEventIdToMKB):
                    groupInOneAccount = forceInt(
                        CDbDataCache.getData('EventType', 'exposeGrouped', 'id = %d' % eventTypeId, None, None).strList[
                            0])
                    age = calcAgeInYears(clientBirthDate, forceDate(eventBegDate))
                    clientId = forceRef(event.value('client_id'))

                    # Переменная "p" необходима для решения проблем с округлением
                    # Например: round(0.575, 2) == 0.57; round(0.5750000001, 2) == 0.58
                    p = forceDecimal(0.0000000001)

                    coeffLong = forceDecimal(1)
                    coeffShort = forceDecimal(1)
                    coeffStent = getVMP32StentCoeff(eventTypeId)

                    if acceptNewKSLPForChild \
                            and getEventPurposeCode(eventTypeId) == '101' \
                            and not isNotForKSLPForChild(mesCode) \
                            and eventBegDate.date() >= QtCore.QDate(2017, 7, 1) \
                            and age < 1:
                        coeffCur = forceDecimal(1.8)
                    else:
                        coeffCur = forceDecimal(1.1) if (age < 4 and mesCode.startswith('g10')) or \
                                                        (4 <= age < 18 and mesCode.startswith(
                                                            'g10') and isHospWithParent) else forceDecimal(1.0)
                    coeffOnco = forceDecimal(1.8) if age < 18 and mkb in oncoMKBList and mesCode.startswith(
                        'g10') else forceDecimal(1.0)

                    # Только последняя койка. Иначе под коэффициент попадёт случай, когда женщина лежала сначала на патологии беременности <6 дней, а потом родила (у нас это будет один случай)
                    if isPregnancy:
                        coeffProfile = forceDecimal(0.2) \
                            if eventLengthDays < 6 and (
                            bool(bedProfileCodes) and (u'39' == bedProfileCodes[-1] or u'1A' == bedProfileCodes[-1])) \
                            else forceDecimal(1.0)
                    else:
                        coeffProfile = forceDecimal(1.0)

                    if mesCode.startswith('g10') and not isPregnancyPathology:
                        hasComplexService = hasComlexService()
                        if ((eventLengthDays > 30 and not isExtraLong)
                            or (eventLengthDays > 45 and isExtraLong)) \
                                and eventEndDate.date() < QtCore.QDate(2017, 3, 1):
                            coeffLong += forceDecimal(0.2)
                        elif (eventLengthDays > 30 and not isExtraLong) \
                                and eventEndDate.date() >= QtCore.QDate(2017, 3, 1):
                            temp_a = ((eventLengthDays - 30) / forceDecimal(30.0)) + p
                            temp_a = forceDecimal(round(temp_a, 2))
                            temp_b = (temp_a * forceDecimal(0.25)) + p

                            coeffLong += forceDecimal(round(temp_b, 2))
                        elif (eventLengthDays > 45 and isExtraLong) and eventEndDate.date() >= QtCore.QDate(2017, 3, 1):
                            temp_a = ((eventLengthDays - 45) / forceDecimal(45.0)) + p
                            temp_a = forceDecimal(round(temp_a, 2))
                            temp_b = (temp_a * forceDecimal(0.25)) + p

                            coeffLong += forceDecimal(round(temp_b, 2))
                        elif hasComplexService:
                            coeffLong += forceDecimal(0.2)
                        # i4027:
                        # Убрать из списка коэффициентов сложности лечения КСЛП=1.3,
                        # применявшийся при проведении парных и сочетанных хирург.вмешательств.
                        # Коэффициент не должен применяться для случаев лечения, закончившихся с 01.01.2017.
                        if ((eventLengthDays > 30 and not isExtraLong) or (eventLengthDays > 45 and isExtraLong)) \
                                and hasComplexService \
                                and eventEndDate.date() < QtCore.QDate(2017, 1, 1):
                            coeffLong += forceDecimal(0.1)

                    hasMesService = hasMesService(serviceList, mesCode)
                    if QtCore.QDate(2016, 9, 1) <= eventEndDate.date() < QtCore.QDate(2017, 1, 1):
                        if eventLengthDays < 3 and not isUltraShort:
                            if hasMesService:
                                coeffShort = forceDecimal(0.80)
                            else:
                                if isOncoOperation(serviceList):
                                    coeffShort = forceDecimal(0.40)
                                else:
                                    coeffShort = forceDecimal(0.20)

                        if mesCode.startswith('g10') and eventLengthDays == 3 and not isUltraShort:
                            if hasMesService:
                                coeffShort = forceDecimal(0.80)
                            else:
                                coeffShort = forceDecimal(0.50)
                    else:
                        if eventLengthDays <= 3 and not isUltraShort:
                            if hasMesService or isOncoOperation(serviceList):
                                coeffShort = forceDecimal(0.8)
                            else:
                                coeffShort = forceDecimal(0.2)

                    if isEKO(serviceList, eventEndDate, mesCode):
                        coeffShort = forceDecimal(1.0)

                    # i4145: beg
                    if eventEndDate.date() < QtCore.QDate(2017, 5, 1) or not isPython27():
                        sum = forceDecimal(tariff.price) * coeffCur * coeffOnco * coeffLong * coeffShort * coeffProfile
                    else:
                        total = forceDecimal(1.0)
                        for x in [coeffCur, coeffOnco, coeffProfile, coeffStent]:
                            total += x - forceDecimal(1.0)

                        if total > 1.8:
                            total = forceDecimal(1.8)

                        if coeffLong > forceDecimal(1.0):
                            total += (coeffLong - forceDecimal(1.0)) + p
                        else:
                            total *= coeffShort
                        total = forceDecimal(round(total, 2))
                        sum = forceDecimal(tariff.price) * total
                    # i4145: end

                    account = accountFactory(clientId, eventEndDate, eventId,
                                             eventTypeId if not groupInOneAccount else groupInOneAccount)
                    tableAccountItem = db.table(self.accountingDBName + '.Account_Item')
                    accountItem = tableAccountItem.newRecord()
                    accountItem.setValue('master_id', toVariant(account.id))
                    accountItem.setValue('serviceDate', toVariant(eventEndDate))
                    accountItem.setValue('event_id', toVariant(eventId))
                    accountItem.setValue('price', toVariant(sum))
                    accountItem.setValue('unit_id', toVariant(tariff.unitId))
                    accountItem.setValue('amount', toVariant(eventLengthDays))
                    accountItem.setValue('sum', toVariant(sum))
                    accountItem.setValue('tariff_id', toVariant(tariff.id))
                    accountItem.setValue('service_id', toVariant(serviceId))
                    db.insertRecord(tableAccountItem, accountItem)
                    account.totalAmount += eventLengthDays
                    account.totalSum += sum
                    setEventPayStatus(eventId, contractInfo.payStatusMask, CPayStatus.exposedBits)
                    return True
        return False

    def exposeEventByHTG(self, contractInfo, accountFactory, eventId):
        db = QtGui.qApp.db

        def getVMP32StentCoeff(eventTypeId):
            """
            Логика для оплаты случаев лечения при оказании высокотехнологичной мед.помощи (ВМП) по профилю
            "сердечно-сосудистая хирургия" с учетом количества устанавливаемых стентов.

            При формировании счета для экшенов, у которых указано количество стентов, применяем соответствующие
            коэффициенты к тарифу:
            * 1 стент - коэф. 0,8;
            * 2 - 1,1;
            * 3 - 1,4.

            :param eventTypeId: тип события
            :return: значение кэффициента
            """
            stent = forceDecimal(1)
            stentCount = None

            vmpRec = db.getRecordEx(stmt=u"""
            SELECT 
                rbm.federalCode AS VMP
            FROM
                EventType INNER JOIN rbMedicalAidKind rbm ON rbm.id = EventType.medicalAidKind_id
            WHERE
                EventType.id = {eventTypeId}
            """.format(eventTypeId=eventTypeId))

            if vmpRec and forceString(vmpRec.value('VMP')) == '32':
                record = db.getRecordEx(stmt=u"""
                SELECT 
                    aps.value AS stent
                FROM
                    Action a
                    JOIN ActionPropertyType apt ON a.actionType_id = apt.actionType_id 
                    JOIN ActionProperty ap ON a.id = ap.action_id AND apt.id = ap.type_id
                    JOIN ActionProperty_String aps ON ap.id = aps.id
                WHERE
                a.deleted = 0
                AND a.event_id = {eventId}
                # AND a.id = actionId
                AND apt.shortName = 'stent'
                """.format(eventId=eventId))

                if record:
                    stentCount = forceRef(record.value('stent'))

                    if stentCount == 1:
                        stent = forceDecimal(0.8)
                    elif stentCount == 2:
                        stent = forceDecimal(1.1)
                    elif stentCount == 3:
                        stent = forceDecimal(1.4)

            return stent, stentCount


        if not contractInfo.tariffEventByHTG:
            return False

        if not self.isCompletenessAllRelatedEvent(eventId):
            self.missedEventInfo.setdefault(eventId, {}).setdefault('errorMesages').append(
                u'Найдены незакрытые связанные обращения')
            return False

        if QtGui.qApp.defaultKLADR().startswith('91'):
            event = db.getRecord(table='Event'
                                       ' INNER JOIN rbHighTechCureKind htck ON htck.id = Event.hmpKind_id'
                                       ' INNER JOIN rbService ON rbService.code = htck.code'
                                       ' LEFT JOIN Person ON Person.id = Event.execPerson_id',
                                 cols=['Event.client_id',
                                       'Event.setDate',
                                       'Event.execDate',
                                       'Event.eventType_id',
                                       'Person.tariffCategory_id',
                                       'rbService.id AS serviceId', ],
                                 itemId=eventId
                                 )
            serviceId = forceRef(event.value('serviceId'))
        else:
            event = db.getRecord(table='Event'
                                       ' LEFT JOIN Person ON Person.id = Event.execPerson_id',
                                 cols=['Event.client_id',
                                       'Event.setDate',
                                       'Event.execDate',
                                       'Event.eventType_id',
                                       'Event.HTG_id',
                                       'Person.tariffCategory_id',
                                       ],
                                 itemId=eventId)
            htgId = forceRef(event.value('HTG_id'))
            serviceId = self.getHtgService(htgId)

        eventBegDate = forceDateTime(event.value('setDate'))
        eventEndDate = forceDateTime(event.value('execDate'))
        eventTypeId = forceRef(event.value('eventType_id'))
        tariffDate = eventEndDate  # Дата для выбора подходящего тарифа
        tariffCategoryId = forceRef(event.value('tariffCategory_id'))
        tariffList = contractInfo.tariffEventByHTG.get(serviceId, None)
        eventLengthDays = getEventLengthDays(eventBegDate, eventEndDate, False, eventTypeId)

        if tariffList and serviceId:
            for tariff in tariffList:
                if isTariffApplicable(tariff, eventId, tariffCategoryId, tariffDate,
                                      mapEventIdToMKB=self.mapEventIdToMKB):
                    groupInOneAccount = forceInt(
                        CDbDataCache.getData('EventType', 'exposeGrouped', 'id = %d' % eventTypeId, None, None).strList[
                            0])
                    amount = forceDecimal(eventLengthDays)
                    clientId = forceRef(event.value('client_id'))
                    # if tariff.amount:
                    #     amount = tariff.amount

                    coeff, stentCount = getVMP32StentCoeff(eventTypeId)

                    price = forceDecimal(tariff.price) * coeff
                    sum = forceDecimal(price)

                    # if stentCount is not None:
                    #     amount = forceDecimal(stentCount)

                    account = accountFactory(clientId, eventEndDate, eventId,
                                             eventTypeId if not groupInOneAccount else groupInOneAccount)
                    tableAccountItem = db.table(self.accountingDBName + '.Account_Item')
                    accountItem = tableAccountItem.newRecord()
                    accountItem.setValue('master_id', toVariant(account.id))
                    accountItem.setValue('serviceDate', toVariant(eventEndDate))
                    accountItem.setValue('event_id', toVariant(eventId))
                    accountItem.setValue('price', toVariant(tariff.price))
                    accountItem.setValue('unit_id', toVariant(tariff.unitId))
                    accountItem.setValue('amount', toVariant(amount))
                    accountItem.setValue('sum', toVariant(price))
                    accountItem.setValue('tariff_id', toVariant(tariff.id))
                    accountItem.setValue('service_id', toVariant(serviceId))
                    db.insertRecord(tableAccountItem, accountItem)
                    account.totalAmount += amount
                    account.totalSum += sum
                    setEventPayStatus(eventId, contractInfo.payStatusMask, CPayStatus.exposedBits)
                    return True
        return False

    def exposeEventByMes(self, contractInfo, accountFactory, eventId):
        db = QtGui.qApp.db

        if not self.isCompletenessAllRelatedEvent(eventId):
            self.missedEventInfo.setdefault(eventId, {}).setdefault('errorMesages').append(
                u'Найдены незакрытые связанные обращения')
            return False

        event = db.getRecord(table='Event'
                                   ' LEFT JOIN Person ON Person.id = Event.execPerson_id',
                             cols=['Event.client_id',
                                   'Event.setDate',
                                   'Event.execDate',
                                   'Event.eventType_id',
                                   'Event.MES_id',
                                   'Person.tariffCategory_id',
                                   ],
                             itemId=eventId)

        eventBegDate = forceDateTime(event.value('setDate'))
        eventEndDate = forceDateTime(event.value('execDate'))
        eventTypeId = forceRef(event.value('eventType_id'))
        mesId = forceRef(event.value('MES_id'))
        serviceId = self.getMesService(mesId)
        tariffDate = eventEndDate  # Дата для выбора подходящего тарифа
        tariffCategoryId = forceRef(event.value('tariffCategory_id'))
        tariffList = contractInfo.tariffEventByMES.get((eventTypeId, serviceId), None)
        eventLengthDays = getEventLengthDays(eventBegDate, eventEndDate, False, eventTypeId)

        # Если включена опция "Учитывать максимальную длительность по стандарту"
        if contractInfo.exposeByMESMaxDuration:
            # Получаем максимальную длительность текущего МЭС
            mesMaxDuration = CMesInfo(self.infoContext, mesId).maxDuration
        else:
            # В качестве максимальной используем реальную длительность события
            mesMaxDuration = eventLengthDays
        # Если максимальная длительность события по МЭС меньше реальной
        if mesMaxDuration < eventLengthDays:
            purposeCode = getEventPurposeCode(eventTypeId)
            # Для обращений с типом назначения "заболевание", "профилактика" или "патронаж"
            if purposeCode in ['1', '2', '3']:
                # Дата, по которой ищется нужный тариф, получается путем добавления к дате начала обращения максимальной длительности с учетом выходных
                tariffDate = addPeriod(eventBegDate, mesMaxDuration, True)
            # Для обращений с типом назначения "Реабилитация" или "Стационар"
            elif purposeCode in ['7', '10']:
                # Дата, по которой ищется нужный тариф, получается путем добавления к дате начала обращения максимальной длительности без учета выходных
                tariffDate = addPeriod(eventBegDate, mesMaxDuration, False)

        if tariffList and mesId:
            for tariff in tariffList:
                if isTariffApplicable(tariff, eventId, tariffCategoryId, tariffDate,
                                      mapEventIdToMKB=self.mapEventIdToMKB):
                    groupInOneAccount = forceInt(
                        CDbDataCache.getData('EventType', 'exposeGrouped', 'id = %d' % eventTypeId, None, None).strList[
                            0])
                    if tariff.tariffType == CTariff.ttEventByMESLen:
                        amount = eventLengthDays
                    else:
                        amount = 1
                    clientId = forceRef(event.value('client_id'))
                    federalPrice = forceDecimal(0)
                    if contractInfo.isConsiderFederalPrice:
                        federalPrice = forceDecimal(tariff.federalPrice)
                    amount, price, sum = tariff.evalAmountPriceSum(amount, clientId)
                    sum = (price + federalPrice) * amount
                    account = accountFactory(clientId, eventEndDate, eventId,
                                             eventTypeId if not groupInOneAccount else groupInOneAccount)
                    uet = tariff.uet
                    tableAccountItem = db.table(self.accountingDBName + '.Account_Item')
                    accountItem = tableAccountItem.newRecord()
                    accountItem.setValue('master_id', toVariant(account.id))
                    accountItem.setValue('serviceDate', toVariant(eventEndDate))
                    accountItem.setValue('event_id', toVariant(eventId))
                    accountItem.setValue('price', toVariant(price))
                    accountItem.setValue('unit_id', toVariant(tariff.unitId))
                    accountItem.setValue('amount', toVariant(amount))
                    accountItem.setValue('sum', toVariant(sum))
                    accountItem.setValue('uet', toVariant(uet))
                    accountItem.setValue('tariff_id', toVariant(tariff.id))
                    accountItem.setValue('service_id', toVariant(serviceId))
                    db.insertRecord(tableAccountItem, accountItem)
                    account.totalAmount += amount
                    account.totalSum += sum
                    account.totalUet += uet
                    setEventPayStatus(eventId, contractInfo.payStatusMask, CPayStatus.exposedBits)
                    return True
        return False

    def exposeVisitByActionService(self, contractInfo, accountFactory, serviceId, visitId):
        db = QtGui.qApp.db

        visit = db.getRecord(table='Visit '
                                   ' LEFT JOIN Person ON Person.id = Visit.person_id '
                                   ' LEFT JOIN Event ON Event.id=Visit.event_id',
                             cols=['Event.client_id',
                                   'Visit.id',
                                   'Visit.event_id',
                                   'Visit.date',
                                   'Event.execDate as eventExecDate',
                                   'Person.tariffCategory_id',
                                   'Event.eventType_id',
                                   u"(SELECT d.status FROM Diagnostic d WHERE d.id = Visit.diagnostic_id) AS status"
                                   ],
                             itemId=visitId)

        eventId = forceRef(visit.value('event_id'))
        if not self.isCompletenessAllRelatedEvent(eventId):
            self.missedEventInfo.setdefault(eventId, {}).setdefault('errorMesages').append(
                u'Найдены незакрытые связанные обращения')
            return

        tariffList = contractInfo.tariffVisitByActionService.get(serviceId, None)
        if tariffList:
            visitDate = forceDate(visit.value('date'))
            tariffCategoryId = forceRef(visit.value('tariffCategory_id'))
            for tariff in tariffList:
                if isTariffApplicable(tariff, eventId, tariffCategoryId, visitDate,
                                      mapEventIdToMKB=self.mapEventIdToMKB):
                    eventTypeId = forceRef(visit.value('eventType_id'))
                    groupInOneAccount = forceInt(
                        CDbDataCache.getData('EventType', 'exposeGrouped', 'id = %d' % eventTypeId, None, None).strList[
                            0])
                    clientId = forceRef(visit.value('client_id'))
                    price = forceDecimal(tariff.price)
                    federalPrice = forceDecimal(0)
                    if contractInfo.isConsiderFederalPrice:
                        federalPrice = forceDecimal(tariff.federalPrice)
                    discount = forceDecimal(getClientDiscountInfo(clientId)[0])
                    price *= forceDecimal(1.0) - discount
                    amount = forceDecimal(1.0)
                    sum = (price + federalPrice) * amount
                    account = accountFactory(clientId, forceDate(visit.value('eventExecDate')), eventId,
                                             eventTypeId if not groupInOneAccount else groupInOneAccount)

                    sum = self.checkItemStatus(visit, sum)

                    tableAccountItem = db.table(self.accountingDBName + '.Account_Item')
                    accountItem = tableAccountItem.newRecord()
                    accountItem.setValue('master_id', toVariant(account.id))
                    accountItem.setValue('serviceDate', toVariant(visitDate))
                    accountItem.setValue('event_id', visit.value('event_id'))
                    accountItem.setValue('visit_id', toVariant(visitId))
                    accountItem.setValue('price', toVariant(price))
                    accountItem.setValue('unit_id', toVariant(tariff.unitId))
                    accountItem.setValue('amount', toVariant(amount))
                    accountItem.setValue('sum', toVariant(sum))
                    accountItem.setValue('tariff_id', toVariant(tariff.id))
                    accountItem.setValue('service_id', toVariant(serviceId))
                    db.insertRecord(tableAccountItem, accountItem)
                    account.totalAmount += amount
                    account.totalSum += sum
                    setVisitPayStatus(visitId, contractInfo.payStatusMask, CPayStatus.exposedBits)
                    return

    def exposeVisit(self, contractInfo, accountFactory, visitId):
        db = QtGui.qApp.db

        visit = db.getRecord(table='Visit'
                                   ' LEFT JOIN Person ON Person.id = Visit.person_id'
                                   ' LEFT JOIN Event ON Event.id = Visit.event_id',
                             cols=['Event.client_id',
                                   'Visit.id',
                                   'Visit.event_id',
                                   'Visit.date',
                                   'Visit.service_id',
                                   'Person.tariffCategory_id',
                                   'Person.speciality_id',
                                   'Event.eventType_id',
                                   'Event.execDate as eventExecDate',
                                   u"(SELECT d.status FROM Diagnostic d WHERE d.id = Visit.diagnostic_id) AS status"
                                   ],
                             itemId=visitId)

        eventId = forceRef(visit.value('event_id'))
        if not self.isCompletenessAllRelatedEvent(eventId):
            self.missedEventInfo.setdefault(eventId, {}).setdefault('errorMesages').append(
                u'Найдены незакрытые связанные обращения')
            return

        serviceId = forceRef(visit.value('service_id'))
        tariffList = contractInfo.tariffByVisitService.get(serviceId, None)
        if tariffList:
            visitDate = forceDate(visit.value('date'))
            specialityId = forceRef(visit.value('speciality_id'))
            tariffCategoryId = forceRef(visit.value('tariffCategory_id'))
            for tariff in tariffList:
                if isTariffApplicable(tariff, eventId, tariffCategoryId, visitDate,
                                      mapEventIdToMKB=self.mapEventIdToMKB):
                    if not tariff.specialityId or specialityId == tariff.specialityId:
                        eventTypeId = forceRef(visit.value('eventType_id'))
                        groupInOneAccount = forceInt(
                            CDbDataCache.getData('EventType', 'exposeGrouped', 'id = %d' % eventTypeId, None,
                                                 None).strList[0])
                        clientId = forceRef(visit.value('client_id'))
                        price = forceDecimal(tariff.price)
                        federalPrice = forceDecimal(0)
                        if contractInfo.isConsiderFederalPrice:
                            federalPrice = forceDecimal(tariff.federalPrice)
                        discount = forceDecimal(getClientDiscountInfo(clientId)[0])
                        price *= forceDecimal(1.0) - discount
                        amount = forceDecimal(1.0)
                        sum = (price + federalPrice) * amount
                        account = accountFactory(clientId, forceDate(visit.value('eventExecDate')), eventId,
                                                 eventTypeId if not groupInOneAccount else groupInOneAccount)

                        sum = self.checkItemStatus(visit, sum)

                        tableAccountItem = db.table(self.accountingDBName + '.Account_Item')
                        accountItem = tableAccountItem.newRecord()
                        accountItem.setValue('master_id', toVariant(account.id))
                        accountItem.setValue('serviceDate', toVariant(visitDate))
                        accountItem.setValue('event_id', visit.value('event_id'))
                        accountItem.setValue('visit_id', toVariant(visitId))
                        accountItem.setValue('price', toVariant(price))
                        accountItem.setValue('unit_id', toVariant(tariff.unitId))
                        accountItem.setValue('amount', toVariant(amount))
                        accountItem.setValue('sum', toVariant(sum))
                        accountItem.setValue('tariff_id', toVariant(tariff.id))
                        accountItem.setValue('service_id', toVariant(serviceId))
                        db.insertRecord(tableAccountItem, accountItem)
                        account.totalAmount += amount
                        account.totalSum += sum
                        setVisitPayStatus(visitId, contractInfo.payStatusMask, CPayStatus.exposedBits)
                        return

    def exposeVisitByClinicalExamService(self, contractInfo, accountFactory, visitId):
        u"""Тут все плохо. Обновлено положение по диспансеризации. В связи с этим все обращения,
         ОТКРЫТЫЕ до 01.04.2015, тарифицируются по обычной логике (цена берется напрямую из тарифа),
         а после этой даты мы вынуждены проверять наличие определенных услуг в данном обращении и ставить нормальные
         цены только если другая услуга не найдена. На момент написания актуально только для Краснодарского края,
         так как в остальных регионах диспансеризация настроена через МЭС и мероприятия."""
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        tablePerson = db.table('Person')
        tableService = db.table('rbService')
        tableVisit = db.table('Visit')

        table = tableVisit.leftJoin(tablePerson, tablePerson['id'].eq(tableVisit['person_id']))
        table = table.leftJoin(tableEvent, tableEvent['id'].eq(tableVisit['event_id']))
        table = table.leftJoin(tableService, tableService['id'].eq(tableVisit['service_id']))
        cols = [
            tableVisit['id'],
            tableVisit['event_id'],
            tableVisit['date'],
            tableVisit['service_id'],
            tablePerson['tariffCategory_id'],
            tablePerson['speciality_id'],
            tableEvent['client_id'],
            tableEvent['setDate'],
            tableEvent['execDate'],
            tableEvent['eventType_id'],
            tableService['code'].alias('serviceCode'),
            u"(SELECT d.status FROM Diagnostic d WHERE d.id = Visit.diagnostic_id) AS status"
        ]
        visit = db.getRecordEx(table, cols, tableVisit['id'].eq(visitId))

        # Услуги, при наличии которых в обращении цена данного обращения = 0
        superServiceList = ClinicalExamServiceList[:]

        # i3122. В новых услугах добавился ноль в четвётом разряде
        newSuperServiceList = []
        for code in superServiceList:
            pointIdx = code.rfind(u'.')
            newSuperServiceList.append(code[:pointIdx] + u'.0' + code[pointIdx + 1:])
        superServiceList.extend(newSuperServiceList)

        eventId = forceRef(visit.value('event_id'))
        if not self.isCompletenessAllRelatedEvent(eventId):
            self.missedEventInfo.setdefault(eventId, {}).setdefault('errorMesages').append(
                u'Найдены незакрытые связанные обращения')
            return

        serviceId = forceRef(visit.value('service_id'))
        tariffList = contractInfo.tariffByClinicalExamService.get(serviceId, None)
        eventSetDate = forceDate(visit.value('setDate'))
        eventExecDate = forceDate(visit.value('execDate'))
        serviceCode = forceStringEx(visit.value('serviceCode')).lower()
        visitDate = forceDate(visit.value('date'))
        # КОСТЫЛЬ, из-за которого это вынесено в отдельную функцию. Со временем можно будет объеденить все в exposeVisit
        if eventSetDate < QtCore.QDate(2015, 4, 1):
            checkDate = QtCore.QDate(2015, 3, 30)
        else:
            checkDate = eventExecDate if serviceCode.startswith('b04.047') or serviceCode.startswith(
                'b04.026') else visitDate
        # Конец костыля
        if tariffList:
            specialityId = forceRef(visit.value('speciality_id'))
            tariffCategoryId = forceRef(visit.value('tariffCategory_id'))
            for tariff in tariffList:
                if isTariffApplicable(tariff, eventId, tariffCategoryId, checkDate,
                                      mapEventIdToMKB=self.mapEventIdToMKB):
                    if not tariff.specialityId or specialityId == tariff.specialityId:
                        eventTypeId = forceRef(visit.value('eventType_id'))
                        groupInOneAccount = forceInt(
                            CDbDataCache.getData('EventType', 'exposeGrouped', 'id = %d' % eventTypeId, None,
                                                 None).strList[0])
                        eventProfileCache = CRBModelDataCache.getData('rbEventProfile')
                        eventProfileRCode = eventProfileCache.getRegionalCode(
                            eventProfileCache.getIndexById(getEventProfileId(eventTypeId)))
                        clientId = forceRef(visit.value('client_id'))
                        price = forceDecimal(tariff.price)
                        federalPrice = forceDecimal(0)
                        if contractInfo.isConsiderFederalPrice:
                            federalPrice = forceDecimal(tariff.federalPrice)
                        discount = forceDecimal(getClientDiscountInfo(clientId)[0])
                        price *= forceDecimal(1.0) - discount
                        amount = forceDecimal(1.0)
                        if eventProfileRCode in ('261', '211') and \
                                not (serviceCode.startswith('b04.047') or serviceCode.startswith(
                                    'b04.026')):  # Общее условие. Проверяем, что это профосмотр или диспансеризация, и услуга - не "B04.047%"....
                            table = tableVisit.innerJoin(tableService, tableService['id'].eq(tableVisit['service_id']))
                            idList = db.getIdList(table, tableVisit['id'], [tableVisit['event_id'].eq(eventId),
                                                                            tableVisit['deleted'].eq(0),
                                                                            tableService['code'].inlist(
                                                                                superServiceList)])
                            if eventProfileRCode == '261' or (eventSetDate >= QtCore.QDate(2015, 4,
                                                                                           1) and idList):  # На данный момент для диспанеризации (211) мы дополнительно проверяем, что в случае нет услуги "Законченный случай.." (см. задачу 2026)
                                sum = forceDecimal(0.0)
                                price = forceDecimal(0.0)
                            else:
                                sum = (price + federalPrice) * amount
                        else:
                            sum = (price + federalPrice) * amount
                        account = accountFactory(clientId, eventExecDate, eventId,
                                                 eventTypeId if not groupInOneAccount else groupInOneAccount)

                        sum = self.checkItemStatus(visit, sum)

                        tableAccountItem = db.table(self.accountingDBName + '.Account_Item')
                        accountItem = tableAccountItem.newRecord()
                        accountItem.setValue('master_id', toVariant(account.id))
                        accountItem.setValue('serviceDate', toVariant(visitDate))
                        accountItem.setValue('event_id', visit.value('event_id'))
                        accountItem.setValue('visit_id', toVariant(visitId))
                        accountItem.setValue('price', toVariant(price))
                        accountItem.setValue('unit_id', toVariant(tariff.unitId))
                        accountItem.setValue('amount', toVariant(amount))
                        accountItem.setValue('sum', toVariant(sum))
                        accountItem.setValue('tariff_id', toVariant(tariff.id))
                        accountItem.setValue('service_id', toVariant(serviceId))
                        db.insertRecord(tableAccountItem, accountItem)
                        account.totalAmount += amount
                        account.totalSum += sum
                        setVisitPayStatus(visitId, contractInfo.payStatusMask, CPayStatus.exposedBits)
                        return

    def exposeVisitByActionUET(self, contractInfo, accountFactory, visitId):
        db = QtGui.qApp.db

        visit = db.getRecord(table='Visit'
                                   ' LEFT JOIN Person ON Person.id = Visit.person_id'
                                   ' LEFT JOIN Event ON Event.id = Visit.event_id',
                             cols=['Event.client_id',
                                   'Visit.id',
                                   'Visit.event_id',
                                   'Visit.date',
                                   'Visit.service_id',
                                   'Person.tariffCategory_id',
                                   'Person.speciality_id',
                                   'Event.eventType_id',
                                   'Event.execDate as eventExecDate',
                                   u"(SELECT d.status FROM Diagnostic d WHERE d.id = Visit.diagnostic_id) AS status"
                                   ],
                             itemId=visitId)

        eventId = forceRef(visit.value('event_id'))
        if not self.isCompletenessAllRelatedEvent(eventId):
            self.missedEventInfo.setdefault(eventId, {}).setdefault('errorMesages').append(
                u'Найдены незакрытые связанные обращения')
            return

        serviceId = forceRef(visit.value('service_id'))
        tariffList = contractInfo.tariffVisitByActionUET.get(serviceId, None)
        if tariffList:
            visitDate = forceDate(visit.value('date'))
            specialityId = forceRef(visit.value('speciality_id'))
            tariffCategoryId = forceRef(visit.value('tariffCategory_id'))
            tblAction = db.table('Action')
            actions = db.getRecordList(table='Action'
                                             ' INNER JOIN ActionType_Service ON Action.actionType_id = ActionType_Service.master_id'
                                             ' INNER JOIN rbService ON rbService.id = ActionType_Service.service_id',
                                       cols=['Action.amount',
                                             'rbService.adultUetDoctor as uet'],
                                       where=[tblAction['endDate'].dateEq(visitDate),
                                              tblAction['event_id'].eq(eventId),
                                              tblAction['deleted'].eq(0)])
            if actions:
                for tariff in tariffList:
                    if isTariffApplicable(tariff, eventId, tariffCategoryId, visitDate,
                                          mapEventIdToMKB=self.mapEventIdToMKB):
                        if not tariff.specialityId or specialityId == tariff.specialityId:
                            eventTypeId = forceRef(visit.value('eventType_id'))
                            groupInOneAccount = forceInt(
                                CDbDataCache.getData('EventType', 'exposeGrouped', 'id = %d' % eventTypeId, None,
                                                     None).strList[0])
                            clientId = forceRef(visit.value('client_id'))
                            price = forceDecimal(tariff.price)
                            federalPrice = forceDecimal(0)
                            if contractInfo.isConsiderFederalPrice:
                                federalPrice = forceDecimal(tariff.federalPrice)
                            discount = forceDecimal(getClientDiscountInfo(clientId)[0])
                            price *= forceDecimal(1.0) - discount
                            amount = forceDecimal(1.0)
                            uet = forceDecimal(0.0)
                            for action in actions:
                                uet += forceDecimal(action.value('amount')) * forceDecimal(action.value('uet'))
                            sum = (price + federalPrice) * amount
                            account = accountFactory(clientId, forceDate(visit.value('eventExecDate')), eventId,
                                                     eventTypeId if not groupInOneAccount else groupInOneAccount)

                            sum = self.checkItemStatus(visit, sum)

                            tableAccountItem = db.table(self.accountingDBName + '.Account_Item')
                            accountItem = tableAccountItem.newRecord()
                            accountItem.setValue('master_id', toVariant(account.id))
                            accountItem.setValue('serviceDate', toVariant(visitDate))
                            accountItem.setValue('event_id', visit.value('event_id'))
                            accountItem.setValue('visit_id', toVariant(visitId))
                            accountItem.setValue('price', toVariant(price))
                            accountItem.setValue('unit_id', toVariant(tariff.unitId))
                            accountItem.setValue('amount', toVariant(amount))
                            accountItem.setValue('uet', toVariant(uet))
                            accountItem.setValue('sum', toVariant(sum))
                            accountItem.setValue('tariff_id', toVariant(tariff.id))
                            accountItem.setValue('service_id', toVariant(serviceId))
                            db.insertRecord(tableAccountItem, accountItem)
                            account.totalAmount += amount
                            account.totalSum += sum
                            account.totalUet += uet
                            setVisitPayStatus(visitId, contractInfo.payStatusMask, CPayStatus.exposedBits)
                            return

    def checkItemStatus(self, rec, sum):
        if forceRef(rec.value('status')) in [7, 8, 9, 10, 11]:
            return forceDecimal(0.0)
        return sum

    def exposeActionsByMes(self, contractInfo, accountFactory, actionId, date, checkMes, franchisePercent=0):
        db = QtGui.qApp.db

        action = db.getRecord(table=u'''
        Action
        LEFT JOIN Person ON Person.id = Action.person_id
        LEFT JOIN Event ON Event.id = Action.event_id
        LEFT JOIN ActionPropertyType ON Action.actionType_id = ActionPropertyType.actionType_id AND ActionPropertyType.name = 'Отделение пребывания'
        LEFT JOIN ActionProperty ON Action.id = ActionProperty.action_id AND ActionPropertyType.id = ActionProperty.type_id
        LEFT JOIN ActionProperty_OrgStructure ON ActionProperty.id = ActionProperty_OrgStructure.id
        LEFT JOIN OrgStructure ON ActionProperty_OrgStructure.value = OrgStructure.id
                                         ''',
                              cols=['Event.client_id',
                                    'Action.id',
                                    'Action.actionType_id',
                                    'Event.execDate as eventEndDate',
                                    'Action.event_id, Action.begDate',
                                    'Action.endDate',
                                    'Action.amount',
                                    'Action.status',
                                    'Action.MKB',
                                    'Person.tariffCategory_id',
                                    'Event.eventType_id',
                                    'Action.MES_id',
                                    'OrgStructure.hasDayStationary'
                                    ],
                              itemId=actionId)

        eventId = forceRef(action.value('event_id'))
        if not self.isCompletenessAllRelatedEvent(eventId):
            self.missedEventInfo.setdefault(eventId, {}).setdefault('errorMesages', []).append(
                u'Найдены незакрытые связанные обращения')
            return

        eventTypeId = forceRef(action.value('eventType_id'))
        mesId = forceRef(action.value('MES_id'))
        serviceId = self.getMesService(mesId)
        tariffList = contractInfo.tariffActionsByMES.get((eventTypeId, serviceId), None)

        amount = getActionLengthDays(forceDateTime(action.value('begDate')), forceDateTime(action.value('endDate')),
                                     True, eventTypeId, forceBool(action.value('hasDayStationary')))

        if tariffList:
            endDate = forceDate(action.value('endDate')) or date
            eventEndDate = forceDate(action.value('eventEndDate'))
            MKB = forceString(action.value('MKB'))
            tariffCategoryId = forceRef(action.value('tariffCategory_id'))
            for tariff in tariffList:
                if isTariffApplicable(tariff, eventId, tariffCategoryId, endDate, MKB,
                                      mapEventIdToMKB=self.mapEventIdToMKB):
                    groupInOneAccount = forceInt(
                        CDbDataCache.getData('EventType', 'exposeGrouped', 'id = %d' % eventTypeId, None, None).strList[
                            0])
                    clientId = forceRef(action.value('client_id'))
                    amount, price, sum = tariff.evalAmountPriceSum(amount, clientId)
                    # sum += round(tariff.price * amount, 2)
                    account = accountFactory(clientId, eventEndDate, eventId,
                                             eventTypeId if not groupInOneAccount else groupInOneAccount)

                    sum = self.checkItemStatus(action, sum)

                    tableAccountItem = db.table(self.accountingDBName + '.Account_Item')
                    accountItem = tableAccountItem.newRecord()
                    accountItem.setValue('master_id', toVariant(account.id))
                    accountItem.setValue('serviceDate', toVariant(endDate))
                    accountItem.setValue('event_id', action.value('event_id'))
                    accountItem.setValue('action_id', toVariant(actionId))
                    accountItem.setValue('price', toVariant(price))
                    accountItem.setValue('unit_id', toVariant(tariff.unitId))
                    accountItem.setValue('amount', toVariant(amount))
                    accountItem.setValue('sum', toVariant(sum))
                    accountItem.setValue('tariff_id', toVariant(tariff.id))
                    accountItem.setValue('service_id', toVariant(serviceId))
                    if checkMes:
                        norm = self.getMesNorm(mesId)
                        if amount < norm:
                            self.rejectAccountItemBySemifinishedMes(accountItem, contractInfo.finance_id)
                    db.insertRecord(tableAccountItem, accountItem)
                    account.totalAmount += amount
                    if franchisePercent:
                        account.totalSum += sum * (forceDecimal(franchisePercent) / forceDecimal(100.0))
                    else:
                        account.totalSum += sum
                    setActionPayStatus(actionId, contractInfo.payStatusMask, CPayStatus.exposedBits)
                    break

    def exposeAction(self, contractInfo, accountFactory, actionId, date, franchisePercent=0):
        def getVMP32StentCoeff(eventTypeId, actionId):
            """
            Логика для оплаты случаев лечения при оказании высокотехнологичной мед.помощи (ВМП) по профилю
            "сердечно-сосудистая хирургия" с учетом количества устанавливаемых стентов.

            При формировании счета для экшенов, у которых указано количество стентов, применяем соответствующие
            коэффициенты к тарифу:
            * 1 стент - коэф. 0,8;
            * 2 - 1,1;
            * 3 - 1,4.

            :param eventTypeId: тип события
            :return: значение кэффициента
            """
            stent = forceDecimal(1)
            stentCount = None

            vmpRec = db.getRecordEx(stmt=u"""
            SELECT 
                rbm.federalCode AS VMP
            FROM
                EventType INNER JOIN rbMedicalAidKind rbm ON rbm.id = EventType.medicalAidKind_id
            WHERE
                EventType.id = {eventTypeId}
            """.format(eventTypeId=eventTypeId))

            if vmpRec and forceString(vmpRec.value('VMP')) == '32':
                record = db.getRecordEx(stmt=u"""
                SELECT 
                    aps.value AS stent
                FROM
                    Action a
                    JOIN ActionPropertyType apt ON a.actionType_id = apt.actionType_id 
                    JOIN ActionProperty ap ON a.id = ap.action_id AND apt.id = ap.type_id
                    JOIN ActionProperty_String aps ON ap.id = aps.id
                WHERE
                a.deleted = 0
                AND a.event_id = {eventId}
                AND a.id = {actionId}
                AND apt.shortName = 'stent'
                """.format(eventId=eventId, actionId=actionId))

                if record:
                    stentCount = forceRef(record.value('stent'))

                    if stentCount == 1:
                        stent = forceDecimal(0.8)
                    elif stentCount == 2:
                        stent = forceDecimal(1.1)
                    elif stentCount == 3:
                        stent = forceDecimal(1.4)

            return stent, stentCount


        db = QtGui.qApp.db

        action = db.getRecord(table='Action'
                                    ' LEFT JOIN Person ON Person.id = Action.person_id'
                                    ' LEFT JOIN Event ON Event.id = Action.event_id',
                              cols=['Event.client_id',
                                    'Action.id',
                                    'Action.actionType_id',
                                    'Action.event_id',
                                    'Action.begDate',
                                    'Action.endDate',
                                    'Action.amount',
                                    'Action.status',
                                    'Action.customSum',
                                    'Action.MKB',
                                    'Person.tariffCategory_id',
                                    'Event.eventType_id',
                                    'Event.execDate as eventExecDate',
                                    ],
                              itemId=actionId)

        eventId = forceRef(action.value('event_id'))
        if not self.isCompletenessAllRelatedEvent(eventId):
            self.missedEventInfo.setdefault(eventId, {}).setdefault('errorMesages', []).append(
                u'Найдены незакрытые связанные обращения')
            return

        serviceIdList = CMapActionTypeIdToServiceIdList.getActionTypeServiceIdList(
            forceRef(action.value('actionType_id')), contractInfo.finance_id)
        origAmount = forceDecimal(action.value('amount'))
        for serviceId in serviceIdList:
            tariffList = contractInfo.tariffByActionService.get(serviceId, None)
            if tariffList:
                begDate = forceDate(action.value('begDate'))
                endDate = forceDate(action.value('endDate')) or date
                MKB = forceString(action.value('MKB'))
                tariffCategoryId = forceRef(action.value('tariffCategory_id'))
                for tariff in tariffList:
                    if isTariffApplicable(tariff, eventId, tariffCategoryId, endDate, MKB,
                                          mapEventIdToMKB=self.mapEventIdToMKB):
                        eventTypeId = forceRef(action.value('eventType_id'))
                        groupInOneAccount = forceInt(
                            CDbDataCache.getData('EventType', 'exposeGrouped', 'id = %d' % eventTypeId, None,
                                                 None).strList[0])
                        clientId = forceRef(action.value('client_id'))
                        federalPrice = forceDecimal(0)
                        if contractInfo.isConsiderFederalPrice:
                            federalPrice = forceDecimal(tariff.federalPrice)
                        amount, price, sum = tariff.evalAmountPriceSum(origAmount, clientId)

                        coeff, stentCount = getVMP32StentCoeff(eventTypeId, actionId)

                        sum = sum * coeff
                        price = price * coeff
                        if stentCount is not None:
                            amount = forceDecimal(stentCount)

                        # Жирный Краснодарский костыль
                        if QtGui.qApp.defaultKLADR().startswith('23'):
                            tblClient = db.table('Client')
                            tblEventType = db.table('EventType')
                            tblRbService = db.table('rbService')
                            tblUnit = db.table('rbMedicalAidUnit')
                            tblKind = db.table('rbMedicalAidKind')
                            serviceCode = forceString(
                                db.translate(tblRbService, tblRbService['id'], serviceId, tblRbService['infis'])
                            )
                            recClient = db.getRecordEx(
                                tblClient,
                                tblClient['birthDate'],
                                tblClient['id'].eq(forceInt(clientId))
                            )
                            medicalAidKindId = forceInt(
                                db.translate(
                                    tblEventType,
                                    tblEventType['id'],
                                    forceInt(eventTypeId),
                                    tblEventType['medicalAidKind_id']
                                )
                            )
                            age = calcAgeInYears(forceDate(recClient.value('birthDate')), begDate)
                            kso = forceString(
                                db.translate(
                                    tblUnit,
                                    tblUnit['id'],
                                    forceInt(tariff.unitId),
                                    tblUnit['federalCode'])
                            )
                            vmp = forceString(
                                db.translate(
                                    tblKind,
                                    tblKind['id'],
                                    medicalAidKindId,
                                    tblKind['federalCode'])
                            )
                            serviceIgnoreList = [
                                'B01.064.003',
                                'B01.064.004',
                                'B04.064.001',
                                'B04.064.002'
                            ]
                            if serviceCode in serviceIgnoreList and endDate >= QtCore.QDate(2017, 3,
                                                                                            1) and age < 18 and kso == '9' and vmp == '13':
                                amount, price, sum = tariff.evalAmountPriceSum(origAmount, clientId, True)
                                sum += federalPrice * amount
                            elif endDate >= QtCore.QDate(2017, 1, 1) and age < 18 and kso == '9' and vmp == '13':
                                amount, price, sum = tariff.evalAmountPriceSum(origAmount, clientId, True,
                                                                               forceDecimal(1.3))
                                sum += federalPrice * amount
                            else:
                                sum += federalPrice * amount
                        else:
                            sum += federalPrice * amount
                        # Конец

                        customSum = forceDecimal(action.value('customSum'))
                        uet = forceDecimal(amount) * forceDecimal(
                            tariff.uet) if tariff.tariffType == CTariff.ttActionUET else 0
                        account = accountFactory(clientId, forceDate(action.value('eventExecDate')), eventId,
                                                 eventTypeId if not groupInOneAccount else groupInOneAccount)

                        sum = self.checkItemStatus(action, sum)

                        tableAccountItem = db.table(self.accountingDBName + '.Account_Item')
                        accountItem = tableAccountItem.newRecord()
                        accountItem.setValue('master_id', toVariant(account.id))
                        accountItem.setValue('serviceDate', toVariant(endDate))
                        accountItem.setValue('event_id', action.value('event_id'))
                        accountItem.setValue('action_id', toVariant(actionId))
                        accountItem.setValue('price', toVariant(price))
                        accountItem.setValue('unit_id', toVariant(tariff.unitId))
                        accountItem.setValue('amount', toVariant(amount))
                        accountItem.setValue('uet', toVariant(uet))
                        accountItem.setValue('sum', toVariant(customSum if customSum else sum))
                        accountItem.setValue('tariff_id', toVariant(tariff.id))
                        accountItem.setValue('service_id', toVariant(serviceId))
                        db.insertRecord(tableAccountItem, accountItem)
                        account.totalAmount += amount
                        account.totalUet += uet
                        if franchisePercent:
                            account.totalSum += (customSum if customSum else sum) * (forceDecimal(franchisePercent) / forceDecimal(100.0))
                        else:
                            account.totalSum += customSum if customSum else sum
                        setActionPayStatus(actionId, contractInfo.payStatusMask, CPayStatus.exposedBits)
                        break

    def exposeActionByClinicalExam(self, contractInfo, accountFactory, actionId, date, franchisePercent=0):
        u"""Тут все плохо. Обновлено положение по диспансеризации. В связи с этим все обращения,
         ОТКРЫТЫЕ до 01.04.2015, тарифицируются по обычной логике (цена берется напрямую из тарифа),
         а после этой даты мы вынуждены проверять наличие определенных услуг в данном обращении и ставить нормальные
         цены только если другая услуга не найдена. """

        db = QtGui.qApp.db
        tableAction = db.table('Action')
        tableActionType = db.table('ActionType')
        tableEvent = db.table('Event')
        tablePerson = db.table('Person')
        tableService = db.table('rbService')
        tableVisit = db.table('Visit')

        table = tableAction.leftJoin(tablePerson, tablePerson['id'].eq(tableAction['person_id']))
        table = table.leftJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
        table = table.leftJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
        cols = [
            tableAction['id'],
            tableAction['actionType_id'],
            tableAction['event_id'],
            tableAction['endDate'],
            tableAction['amount'],
            tableAction['status'],
            tableAction['customSum'],
            tableAction['MKB'],
            tablePerson['tariffCategory_id'],
            tableEvent['client_id'],
            tableEvent['setDate'],
            tableEvent['execDate'],
            tableEvent['eventType_id'],
            tableActionType['code'].alias('actionTypeCode')
        ]
        action = db.getRecordEx(table, cols, tableAction['id'].eq(actionId))

        eventId = forceRef(action.value('event_id'))
        if not self.isCompletenessAllRelatedEvent(eventId):
            self.missedEventInfo.setdefault(eventId, {}).setdefault('errorMesages', []).append(
                u'Найдены незакрытые связанные обращения')
            return

        # Услуги, при наличии которых в обращении цена данного обращения = 0
        superServiceList = ClinicalExamServiceList[:]

        # i3122. В новых услугах добавился ноль в четвётом разряде
        newSuperServiceList = []
        for code in superServiceList:
            pointIdx = code.rfind(u'.')
            newSuperServiceList.append(code[:pointIdx] + u'.0' + code[pointIdx + 1:])
        superServiceList.extend(newSuperServiceList)

        serviceIdList = CMapActionTypeIdToServiceIdList.getActionTypeServiceIdList(
            forceRef(action.value('actionType_id')), contractInfo.finance_id)
        origAmount = forceDecimal(action.value('amount'))
        for serviceId in serviceIdList:
            tariffList = contractInfo.tariffByClinicalExamService.get(serviceId, None)
            if tariffList:
                endDate = forceDate(action.value('endDate')) or date

                # КОСТЫЛЬ 1
                checkDate = endDate
                eventSetDate = forceDate(action.value('setDate'))
                eventExecDate = forceDate(action.value('execDate'))
                if QtGui.qApp.defaultKLADR().startswith('23'):
                    if eventSetDate < QtCore.QDate(2015, 4, 1):
                        checkDate = QtCore.QDate(2015, 3, 30)
                    else:
                        checkDate = endDate  # eventExecDate
                # Конец костыля

                MKB = forceString(action.value('MKB'))
                tariffCategoryId = forceRef(action.value('tariffCategory_id'))
                for tariff in tariffList:
                    if isTariffApplicable(tariff, eventId, tariffCategoryId, checkDate, MKB,
                                          mapEventIdToMKB=self.mapEventIdToMKB):
                        eventTypeId = forceRef(action.value('eventType_id'))
                        groupInOneAccount = forceInt(
                            CDbDataCache.getData('EventType', 'exposeGrouped', 'id = %d' % eventTypeId, None,
                                                 None).strList[0])
                        clientId = forceRef(action.value('client_id'))
                        federalPrice = forceDecimal(0)
                        if contractInfo.isConsiderFederalPrice:
                            federalPrice = forceDecimal(tariff.federalPrice)
                        amount, price, sum = tariff.evalAmountPriceSum(origAmount, clientId)
                        sum += federalPrice * amount
                        customSum = forceDecimal(action.value('customSum'))
                        # КОСТЫЛЬ 2
                        eventProfileCache = CRBModelDataCache.getData('rbEventProfile')
                        eventProfileRCode = eventProfileCache.getRegionalCode(
                            eventProfileCache.getIndexById(getEventProfileId(eventTypeId)))
                        # В общем случае это неправильно. Но в контексте данного типа действия мы считаем, что
                        # ActionType.code всегда равен rbService.code и услуга не является комплексной.
                        # По крайней мере пока.
                        serviceCode = forceStringEx(action.value('actionTypeCode'))
                        if QtGui.qApp.defaultKLADR().startswith('23'):
                            table = tableVisit.innerJoin(tableService, tableService['id'].eq(tableVisit['service_id']))
                            idList = db.getIdList(table, tableVisit['id'], [tableVisit['event_id'].eq(eventId),
                                                                            tableVisit['deleted'].eq(0),
                                                                            tableService['code'].inlist(
                                                                                superServiceList)])
                            if (eventSetDate >= QtCore.QDate(2015, 4, 1) and idList) \
                                    or (eventProfileRCode in ('261',) and not \
                                            (serviceCode.startswith('b04.047') or serviceCode.startswith('b04.026'))):
                                sum = forceDecimal(0)
                                price = forceDecimal(0)
                        # Конец костыля
                        uet = amount * tariff.uet if tariff.tariffType == CTariff.ttActionUET else 0
                        account = accountFactory(clientId, eventExecDate, eventId,
                                                 eventTypeId if not groupInOneAccount else groupInOneAccount)

                        sum = self.checkItemStatus(action, sum)

                        tableAccountItem = db.table(self.accountingDBName + '.Account_Item')
                        accountItem = tableAccountItem.newRecord()
                        accountItem.setValue('master_id', toVariant(account.id))
                        accountItem.setValue('serviceDate', toVariant(endDate))
                        accountItem.setValue('event_id', action.value('event_id'))
                        accountItem.setValue('action_id', toVariant(actionId))
                        accountItem.setValue('price', toVariant(price))
                        accountItem.setValue('unit_id', toVariant(tariff.unitId))
                        accountItem.setValue('amount', toVariant(amount))
                        accountItem.setValue('uet', toVariant(uet))
                        accountItem.setValue('sum', toVariant(customSum if customSum else sum))
                        accountItem.setValue('tariff_id', toVariant(tariff.id))
                        accountItem.setValue('service_id', toVariant(serviceId))
                        db.insertRecord(tableAccountItem, accountItem)
                        account.totalAmount += amount
                        account.totalUet += uet
                        if franchisePercent:
                            account.totalSum += (customSum if customSum else sum) * (forceDecimal(franchisePercent) / forceDecimal(100.0))
                        else:
                            account.totalSum += customSum if customSum else sum
                        setActionPayStatus(actionId, contractInfo.payStatusMask, CPayStatus.exposedBits)
                        break

    def exposeHospitalBedActionProperty(self, contractInfo, accountFactory, actionPropertyId, checkCalendarDaysLength):
        db = QtGui.qApp.db

        record = db.getRecord(
            table='ActionProperty' \
                  ' LEFT JOIN Action ON Action.id = ActionProperty.action_id' \
                  ' LEFT JOIN Person ON Person.id = Action.person_id' \
                  ' LEFT JOIN ActionProperty_HospitalBed ON ActionProperty_HospitalBed.id = ActionProperty.id' \
                  ' LEFT JOIN OrgStructure_HospitalBed ON OrgStructure_HospitalBed.id = ActionProperty_HospitalBed.value' \
                  ' LEFT JOIN rbHospitalBedProfile ON rbHospitalBedProfile.id = OrgStructure_HospitalBed.profile_id' \
                  ' LEFT JOIN Event ON Event.id = Action.event_id',
            cols=[
                'Event.client_id',
                'ActionProperty.action_id',
                'Action.event_id',
                'Action.amount',
                'Action.status',
                'Action.MKB',
                'Action.begDate',
                'Action.endDate',
                'Person.tariffCategory_id',
                'rbHospitalBedProfile.service_id',
                'Event.eventType_id',
                'Event.execDate as eventExecDate',
            ],
            itemId=actionPropertyId
        )

        eventId = forceRef(record.value('event_id'))
        if not self.isCompletenessAllRelatedEvent(eventId):
            self.missedEventInfo.setdefault(eventId, {}).setdefault('errorMesages').append(
                u'Найдены незакрытые связанные обращения')
            return

        eventTypeId = forceRef(record.value('eventType_id'))
        tariffList = contractInfo.tariffByHospitalBedService.get(eventTypeId, None)
        if not tariffList:
            tariffList = contractInfo.tariffByHospitalBedService.get(None, None)
        if tariffList:
            endDate = forceDate(record.value('endDate'))
            MKB = forceString(record.value('MKB'))
            tariffCategoryId = forceRef(record.value('tariffCategory_id'))
            actionId = forceRef(record.value('action_id'))
            serviceId = forceRef(record.value('service_id'))

            amount = forceDecimal(record.value('amount'))

            if checkCalendarDaysLength:
                medicalTypeId = forceRef(db.translate('EventType', 'id', eventTypeId, 'medicalAidType_id'))
                federalCode = forceInt(db.translate('rbMedicalAidType', 'id', medicalTypeId, 'federalCode'))
                if federalCode == 1:
                    begDate = forceDate(record.value('begDate'))
                    endDate = forceDate(record.value('endDate'))
                    if begDate == endDate:
                        amount = 1
                    else:
                        amount += 1

            for tariff in tariffList:
                if tariff.serviceId == serviceId and isTariffApplicable(tariff, eventId, tariffCategoryId, endDate, MKB,
                                                                        mapEventIdToMKB=self.mapEventIdToMKB):
                    groupInOneAccount = forceInt(
                        CDbDataCache.getData('EventType', 'exposeGrouped', 'id = %d' % eventTypeId, None, None).strList[
                            0])
                    clientId = forceRef(record.value('client_id'))
                    federalPrice = forceDecimal(0)
                    if contractInfo.isConsiderFederalPrice:
                        federalPrice = forceDecimal(tariff.federalPrice)
                    amount, price, sum = tariff.evalAmountPriceSum(amount, clientId)
                    sum += federalPrice * amount
                    uet = amount * tariff.uet if tariff.tariffType == CTariff.ttActionUET else 0
                    account = accountFactory(clientId, forceDate(record.value('eventExecDate')), eventId,
                                             eventTypeId if not groupInOneAccount else groupInOneAccount)

                    sum = self.checkItemStatus(record, sum)

                    tableAccountItem = db.table(self.accountingDBName + '.Account_Item')
                    accountItem = tableAccountItem.newRecord()
                    accountItem.setValue('master_id', toVariant(account.id))
                    accountItem.setValue('serviceDate', toVariant(endDate))
                    accountItem.setValue('event_id', record.value('event_id'))
                    accountItem.setValue('action_id', toVariant(actionId))
                    accountItem.setValue('price', toVariant(price))
                    accountItem.setValue('unit_id', toVariant(tariff.unitId))
                    accountItem.setValue('amount', toVariant(amount))
                    accountItem.setValue('uet', toVariant(uet))
                    accountItem.setValue('sum', toVariant(sum))
                    accountItem.setValue('tariff_id', toVariant(tariff.id))
                    accountItem.setValue('service_id', toVariant(serviceId))
                    db.insertRecord(tableAccountItem, accountItem)
                    account.totalAmount += amount
                    account.totalUet += uet
                    account.totalSum += sum
                    setActionPayStatus(actionId, contractInfo.payStatusMask, CPayStatus.exposedBits)
                    return

    def getHtgService(self, hmpId):
        result = self.mapHtgIdToServiceId.get(hmpId, False)
        if result == False:
            db = QtGui.qApp.db
            code = db.translate('mes.mrbHighTechMedicalGroups', 'id', hmpId, 'code')
            result = forceRef(db.translate('rbService', 'code', code, 'id'))
            self.mapHtgIdToServiceId[hmpId] = result
        return result

    def getMesService(self, mesId):
        result = self.mapMesIdToServiceId.get(mesId, False)
        if not result:
            db = QtGui.qApp.db
            code = db.translate('mes.MES', 'id', mesId, 'code')
            result = forceRef(db.translate('rbService', 'code', code, 'id'))
            self.mapMesIdToServiceId[mesId] = result
        return result

    def getMesNorm(self, mesId):
        result = self.mapMesIdToNorm.get(mesId, False)
        if result == False:
            db = QtGui.qApp.db
            result = forceDouble(db.translate('mes.MES', 'id', mesId, 'KSGNorm'))
            self.mapMesIdToNorm[mesId] = result
        return result

    def getSemifinishedMesRefuseTypeId(self, financeId):
        return getRefuseTypeId(u'МЭС не выполнен полностью', True, financeId, True)

    def rejectAccountItemBySemifinishedMes(self, accountItem, financeId):
        if self.semifinishedMesRefuseTypeId is None:
            self.semifinishedMesRefuseTypeId = self.getSemifinishedMesRefuseTypeId(financeId)
        accountItem.setValue('date', QtCore.QVariant(QtCore.QDate.currentDate()))
        accountItem.setValue('refuseType_id', toVariant(self.semifinishedMesRefuseTypeId))
        accountItem.setValue('number', QtCore.QVariant(u'Проверка МЭС'))

    def reexpose(self, progressDialog, contractInfo, accountFactory, idList):
        db = QtGui.qApp.db
        tableAccountItem = db.table(self.accountingDBName + '.Account_Item')
        for oldId in idList:
            progressDialog.step()
            oldAccountItem = db.getRecord(tableAccountItem, '*', oldId)
            qvDate = oldAccountItem.value('serviceDate')
            qvEventId = oldAccountItem.value('event_id')
            qvEventTypeId = db.translate('Event', 'id', qvEventId, 'eventType_id')
            qvEventExecDate = db.translate('Event', 'id', qvEventId, 'execDate')
            clientId = forceRef(db.translate('Event', 'id', qvEventId, 'client_id'))
            account = accountFactory(clientId,
                                     forceDate(qvEventExecDate),
                                     forceRef(qvEventId),
                                     forceRef(qvEventTypeId),
                                     1)
            newaccountItem = tableAccountItem.newRecord()
            newaccountItem.setValue('master_id', toVariant(account.id))
            newaccountItem.setValue('serviceDate', qvDate)
            newaccountItem.setValue('event_id', qvEventId)
            newaccountItem.setValue('visit_id', oldAccountItem.value('visit_id'))
            newaccountItem.setValue('action_id', oldAccountItem.value('action_id'))
            newaccountItem.setValue('price', oldAccountItem.value('price'))
            newaccountItem.setValue('unit_id', oldAccountItem.value('unit_id'))
            # SS: добавлено 2012-05-18, т.к. в противном случае получаем не заполненный ИНФИС код в реестре счетов
            newaccountItem.setValue('service_id', oldAccountItem.value('service_id'))
            self.updateDocsPayStatus(oldAccountItem, contractInfo, CPayStatus.exposedBits)
            qvAmount = oldAccountItem.value('amount')
            qvUet = oldAccountItem.value('uet')
            qvSum = oldAccountItem.value('sum')
            newaccountItem.setValue('amount', qvAmount)
            newaccountItem.setValue('uet', qvUet)
            newaccountItem.setValue('sum', qvSum)
            newaccountItem.setValue('tariff_id', oldAccountItem.value('tariff_id'))
            newId = db.insertRecord(tableAccountItem, newaccountItem)
            oldAccountItem.setValue('reexposeItem_id', toVariant(newId))
            db.updateRecord(tableAccountItem, oldAccountItem)
            account.totalAmount += forceDecimal(qvAmount)
            account.totalUet += forceDecimal(qvUet)
            account.totalSum += forceDecimal(qvSum)

    def updateDocsPayStatus(self, accountItem, contractInfo, bits):
        updateDocsPayStatus(accountItem, contractInfo.payStatusMask, bits)

    def getEventRecord(self, eventId):
        # we need eventType_id, client_id, execDate
        return QtGui.qApp.db.getRecord('Event', ['eventType_id', 'client_id', 'execDate'], eventId)

    def getClientRecord(self, clientId):
        # sex and birthDate
        return QtGui.qApp.db.getRecord('Client', ['sex', 'birthDate'], clientId)
