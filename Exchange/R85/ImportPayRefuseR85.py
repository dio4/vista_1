# -*- coding: utf-8 -*-

import logging
import os
import zipfile

from PyQt4 import QtCore, QtGui

from Accounting.Utils   import updateAccounts, updateDocsPayStatus
from Events.Utils       import CPayStatus, getPayStatusMask
from library.XML.XMLHelper import CXMLHelper
from library.database import CDatabase
from library.ProgressBar import CProgressBar
from library.ProgressInformer import CProgressInformer
from library.Utils      import forceInt, forceRef, forceStringEx, forceTr, toVariant, getClassName, getPref, setPref,\
                                CLogHandler, forceDate, forceDouble


from Exchange.R85.ExchangeEngine import CExchangeImportR85Engine

def importPayRefuseR85(widget, orgId, isFLC = False):
    importWindow = CImportPayRefuseR85Dialog(QtGui.qApp.db, orgId, parent=widget, isFLC = isFLC)
    params = getPref(QtGui.qApp.preferences.appPrefs, getClassName(importWindow), {})
    importWindow.setParams(params)
    importWindow.setLastExceptionHandler(QtGui.qApp.logCurrentException)
    importWindow.exec_()
    setPref(QtGui.qApp.preferences.appPrefs, getClassName(importWindow), importWindow.params())

class CImportPayRefuseR85EngineFLC(CExchangeImportR85Engine):
    sexMap = {u'Ж': 2, u'ж': 2, u'М': 1, u'м': 1}

    def __init__(self, db, orgId, progressInformer = None, format=None):
        # FIXME: orgId здесь не нужен, скопипасчен из нормального импорта новых счетов.
        super(CImportPayRefuseR85EngineFLC, self).__init__(progressInformer)
        self._db = db if isinstance(db, CDatabase) else None
        self._orgId = orgId
        self._orgInfis = None
        self._skipped = 0

        self._refuseTypeIdCache = {}
        self._mapAccountIdToPayStatusMask = {}
        self._processedAccountIdSet = set()
        self._processedAccountItems = set()
        self.logger().setLevel(logging.INFO)


    def process(self, fileName):
        self.isAbort = False
        self._refuseTypeIdCache.clear()
        self._mapAccountIdToPayStatusMask.clear()
        self._processedAccountIdSet.clear()
        self._processedAccountItems.clear()
        self._skipped = 0

        self.phaseReset(1)
        self.processFile(fileName)
        updateAccounts(self._processedAccountIdSet)
        self.logger().info(u'Импорт завершен успешно.')
        return True

    def processFile(self, fileName):
        docFile = None
        try:
            isOk, sourceType, sourceInfis, destType, destInfis, year, month, number = self.parseFileName(fileName)
            if not isOk:
                return False

            if zipfile.is_zipfile(fileName):
                zipFile = zipfile.ZipFile(fileName, 'r')
                zipItems = zipFile.namelist()
                if not zipItems:
                    raise Exception(u'Zip-архив "%s" пуст' % fileName)
                zipItem = next((item for item in zipItems if not item.startswith('L')), None)
                if zipItem is None:
                    raise Exception(u'Необходимый файл в zip-архиве не найден' % fileName)
                docFile = zipFile.open(zipItem)
            else:
                docFile = open(fileName, 'r')

            self.processDocument(CXMLHelper.loadDocument(QtCore.QString(docFile.read().decode(self.encoding))), sourceInfis)
        except Exception, e:
            self.logger().warning(u'Не удалось провести импорт (%s)' % e.message)
            self.onException()
            return False
        finally:
            if docFile:
                docFile.close()

    def processDocument(self, document, insurerInfis):
        self.nextPhase(document.elementsByTagName('SLUCH').length(), u'Обработка случаев лечения')

        rootElement = self.getElement(document, 'ZL_LIST', isRequired=True)
        if not rootElement:
            return False

        headerElement = self.getElement(rootElement, 'ZGLV', isRequired=True)
        if not headerElement:
            return False

        version = self.getElementValue(headerElement, 'VERSION', isRequired=True)
        if version != '2.1':
            return False

        date = self.getElementValue(headerElement, 'DATA', typeName='d')
        if not date.isValid():
            date = QtCore.QDate.currentDate()

        self._db.transaction(checkIsInit=True)
        try:
            entityElement = self.getElement(rootElement, 'ZAP')
            while not entityElement.isNull():
                self.processEntity(entityElement, date, insurerInfis)
                entityElement = entityElement.nextSiblingElement('ZAP')
            self._db.commit()
        except Exception, e:
            self._db.rollback()
            raise
        finally:
            self.finishPhase()

        return True

    def processEntity(self, entityElement, date, insurerInfis):
        entityKey = self.getElementValue(entityElement, 'N_ZAP')
        if not entityKey:
            return False

        try:
            patientElement = self.getElement(entityElement, 'PACIENT', isRequired=True)
            clientId = self.getElementValue(patientElement, 'ID_PAC', isRequired = True) # Применимо только в МО

            eventElement = patientElement.nextSiblingElement('SLUCH')
            while not eventElement.isNull():
                self.processEvent(eventElement, clientId, date, insurerInfis)
                eventElement = eventElement.nextSiblingElement('SLUCH')
                self.nextPhaseStep()


        except Exception, e:
            self.onException()
            self.logger().warning(u'Не удалось обработать запись N_ZAP=%s (%s)' % (entityKey, e.message))
            return False
        if self.isAbort:
            raise Exception(u'Прервано пользователем')
        return True

    def processEvent(self, eventElement, clientId, date, insurerInfis):
        eventId = self.getElementValue(eventElement, 'NHISTORY', isRequired=True) # Применимо только в МО

        tblEvent = self._db.table('Event')
        eventRecord = self._db.getRecordEx(table=tblEvent,
                                           cols=[tblEvent['id'].eq(eventId),
                                                 tblEvent['client_id'].eq(clientId),
                                                 tblEvent['deleted'].eq(0)])

        if not eventRecord:
            self.logger().warning(u'Не найден случай лечения NHISTORY=%s для пациента ID_PAC=%s' % (eventId, clientId))
            return False

        eventSetDate = self.getElementValue(eventElement, 'DATE_1', typeName='d')
        eventExecDate = self.getElementValue(eventElement, 'DATE_2', typeName='d')

        tblAccountItem = self._db.table('Account_Item')
        tblVisit = self._db.table('Visit')
        tblAction = self._db.table('Action')
        tblService = self._db.table('rbService')
        queryTable = tblAccountItem.innerJoin(tblEvent, tblEvent['id'].eq(tblAccountItem['event_id']))
        queryTable = queryTable.leftJoin(tblVisit, tblVisit['id'].eq(tblAccountItem['visit_id']))
        queryTable = queryTable.leftJoin(tblAction, tblAction['id'].eq(tblAccountItem['action_id']))
        queryTable = queryTable.leftJoin(tblService, tblService['id'].eq(tblAccountItem['service_id']))
        fields = [tblAccountItem['id'],
                      tblAccountItem['date'],
                      tblAccountItem['action_id'],
                      tblAccountItem['visit_id'],
                      tblAccountItem['event_id'],
                      tblAccountItem['master_id'],
                      tblAccountItem['refuseType_id'],
                      tblAccountItem['number'],
                      tblAccountItem['note'],
                      tblAccountItem['service_id'],
                      # tblAccountItem['insurer_sum'],
                      tblAccountItem['sum'],
                      tblAccountItem['price'],
                      tblAccountItem['amount'],
                      tblAction['begDate'].alias('actionBegDate'),
                      tblAction['endDate'].alias('actionEndDate'),
                      tblVisit['date'].alias('visitDate'),
                      tblEvent['setDate'].alias('eventSetDate'),
                      tblEvent['execDate'].alias('eventExecDate'),
                      tblService['code'].alias('serviceCode'),
                      ]

        accountItemList = self._db.getRecordList(queryTable,
                                                 cols=fields,
                                                 where=[tblEvent['id'].eq(eventId)
                                                        ])
        if not accountItemList:
            self._skipped += 1
            self.logger().warning(u'Не найден случай лечения NHISTORY=%s для пациента ID_PAC=%s' % (eventId, clientId))
            return False

        self._db.transaction()
        try:
            self._db.query('UPDATE Event SET FLCStatus = 2 WHERE id = %s' % eventId)

            oplata = self.getElementValue(eventElement, 'OPLATA', typeName='n')
            for accountItem in accountItemList:
                accountItem.setValue('date', toVariant(date))
                accountNote = forceStringEx(accountItem.value('note'))
                if insurerInfis:
                    accountNote += '\n$$insurer:%s$$' % insurerInfis
                sankElement = self.getElement(eventElement, 'SANK')
                if not sankElement.isNull():
                    refReason = self.getElementValue(sankElement, 'S_OSN')
                    accountNote += '\nS_COM: %s' % self.getElementValue(sankElement, 'S_COM')
                else:
                    refReason = '' if oplata != 0 else '53'  # mdldml: 53 -- flatCode "Некорректного заполнения полей реестра"
                accountId = forceRef(accountItem.value('master_id'))
                payStatusMask = self.getPayStatusMask(accountId)

                accountItem.setValue('note', toVariant(accountNote))
                if oplata != 1 and refReason:
                    refuseTypeId = self.getRefuseTypeId(refReason)
                    accountItem.setValue('refuseType_id', toVariant(refuseTypeId))
                    accountItem.setValue('number', toVariant(u'Отказ по МЭК'))
                    updateDocsPayStatus(accountItem, payStatusMask, CPayStatus.refusedBits)
                else:
                    accountItem.setValue('number', toVariant(u'Оплачено'))
                    accountItem.setValue('refuseType_id', toVariant(None))
                    updateDocsPayStatus(accountItem, payStatusMask, CPayStatus.payedBits)

            eventLevelAccountItems = [ai for ai in accountItemList if ai.value('action_id').isNull() and ai.value('visit_id').isNull()]
            if not eventLevelAccountItems:
                serviceList = []
                serviceElement = eventElement.firstChildElement('USL')
                while not serviceElement.isNull():
                    serviceList.append(self._get_service_info(serviceElement))
                    serviceElement = serviceElement.nextSiblingElement('USL')

                for accountItem in accountItemList:
                    if forceRef(accountItem.value('action_id')):
                        begDate = forceDate(accountItem.value('actionBegDate'))
                        endDate = forceDate(accountItem.value('actionEndDate'))
                    elif forceRef(accountItem.value('visit_id')):
                        begDate = endDate = forceDate(accountItem.value('visitDate'))
                    else:
                        begDate = forceDate(accountItem.value('eventSetDate'))
                        endDate = forceDate(accountItem.value('eventExecDate'))

                    filtered_list = sorted(filter(lambda x: x['code'] == forceStringEx(accountItem.value('serviceCode')) and \
                                     x['begDate'] == begDate and x['endDate'] == endDate and \
                                     x['amount'] == forceDouble(accountItem.value('amount'))
                                    , serviceList), key=lambda x: abs(x['sum'] - forceDouble(accountItem.value('sum'))))

                    if filtered_list:
                        service_info = filtered_list[0]
                        accountItem.setValue('sum', toVariant(service_info['sum']))
                        accountItem.setValue('price', toVariant(service_info['price']))
                        serviceList.remove(service_info)

            else:
                eventServiceInfo = self._get_event_service_info(eventElement)
                # проверить, что это действительно та услуга: как минимум,
                # code_mes должен совпадать с Account.event_id -> Event.mes_id -> mes.MES.code,
                # даты должны совпадать с датами обращения
                otherAccountItems = [item for item in accountItemList if item not in eventLevelAccountItems]
                tableEvent = self._db.table('Event')
                tableMes = self._db.table('mes.MES')
                eventData = self._db.getRecordList(
                    tableEvent.leftJoin(tableMes, tableEvent['MES_id'].eq(tableMes['id'])),
                    [tableEvent['id'], tableEvent['setDate'], tableEvent['execDate'], tableMes['code']],
                    tableEvent['id'].inlist([forceRef(item.value('event_id')) for item in eventLevelAccountItems])
                )
                eventMap = {}
                for eventRecord in eventData:
                    eventMap[forceRef(eventRecord.value('id'))] = {
                        'setDate': forceDate(eventRecord.value('setDate')),
                        'execDate': forceDate(eventRecord.value('execDate')),
                        'code': forceStringEx(eventRecord.value('code'))
                    }
                accountsChanged = set()
                for accountItem in eventLevelAccountItems:
                    # accountId = forceRef(accountItem.value('master_id'))
                    eventInfo = eventMap[forceRef(accountItem.value('event_id'))]
                    if forceRef(accountItem.value('master_id')) not in accountsChanged and \
                                    eventServiceInfo['code'] == eventInfo['code'] and \
                                    eventServiceInfo['begDate'] == eventInfo['setDate'] and \
                                    eventServiceInfo['endDate'] == eventInfo['execDate']:
                        accountItem.setValue('sum', toVariant(eventServiceInfo['sum']))
                        accountItem.setValue('price', toVariant(eventServiceInfo['price']))
                        accountsChanged.add(forceRef(accountItem.value('master_id')))
                for accountItem in otherAccountItems:
                    if forceRef(accountItem.value('master_id')) in accountsChanged:
                        accountItem.setValue('sum', toVariant(0))
                        accountItem.setValue('price', toVariant(0))

            for accountItem in accountItemList:
                accountId = forceRef(accountItem.value('master_id'))
                for field in ('actionBegDate', 'actionEndDate', 'visitDate', 'eventSetDate', 'eventExecDate', 'serviceCode'):
                    accountItem.remove(accountItem.indexOf(field))

                self._db.updateRecord(tblAccountItem, accountItem)
                self._processedAccountIdSet.add(accountId)
                self._processedAccountItems.add(forceRef(accountItem.value('id')))

            self._db.commit()
        except:
            self._db.rollback()

    # Helpers
    def getPayStatusMask(self, accountId):
        result = self._mapAccountIdToPayStatusMask.get(accountId, None)
        if result is None:
            tblAccount = self._db.table('Account')
            tblContract = self._db.table('Contract')
            tbl = tblAccount.join(tblContract, tblContract['id'].eq(tblAccount['contract_id']))
            record = self._db.getRecordEx(tbl, tblContract['finance_id'], tblAccount['id'].eq(accountId))
            if record:
                result = getPayStatusMask(forceRef(record.value('finance_id')))
            self._mapAccountIdToPayStatusMask[accountId] = result
        return result

    def getRefuseTypeId(self, code):
        result = self._refuseTypeIdCache.get(code, -1)

        if result == -1:
            result = forceRef(self._db.translate(
                'rbPayRefuseType', 'flatCode', code, 'id'
            ))
            self._refuseTypeIdCache[code] = result

        return result

    def parseFileName(self, fileName):
        """
        Вычленяет из имени файла важную информацию.
        Предполагается, что имя файла представлено в формате:
            H + тип учреждения-отправителя
            + код в системе ОМС учреждения-отправителя
            + тип учреждения-получателя
            + код в системе ОМС учреждения-получателя
            + две последние цифры года + две цифры месяца
            + четырехзначный порядковый номер представления основной части в текущем году
        :param fileName: имя обрабатываемого файла
        :return: isOk, sourceType, sourceCode, destType, descCode, year, month, number
        """
        try:
            name = os.path.splitext(os.path.basename(fileName))[0].lower()
            # if name.startswith('flk_'):
            #     name = name[4:]
            name = name[1:]
            if name[0] in ['h', 'd', 't']:
                nameParts = name.split('_')
                if len(nameParts) != 2: raise
                orgs, account = nameParts
                if len(orgs) < 11: raise
                if len(account) < 5: raise

                shifter = 0 if name[0] in ('h', 't') else 1
                sourceType = orgs[shifter+1]
                m_index = orgs.find('m')
                if m_index < 0:
                    raise
                sourceCodeLength = m_index - 2 - shifter
                sourceCode = orgs[shifter+2:shifter+2+sourceCodeLength]
                destType = orgs[shifter+2+sourceCodeLength]
                destCodeLength = 6
                destCode = orgs[shifter+3+sourceCodeLength:shifter+3+sourceCodeLength+destCodeLength]

                year = 2000 + forceInt(account[:2])
                month = account[2:4]
                number = account[4:]

                return True, sourceType, sourceCode, destType, destCode, year, month, number
            raise
        except Exception, e:
            self.logger().critical(u'Некорректное имя файла "%s" (%s)' % (fileName, e.message))
            self.onException()

        return False, u'', u'', u'', u'', 0, 0, None

    def _get_service_info(self, serviceElement):
        """ Обработка узла sluch

        :param serviceElement: DOMElement соответствующий узлу USL
        :return: словарь с основными данными об услуге
        """
        service = {}
        # Копируем существующий список ошибок
        service['key'] = self.getElementValue(serviceElement, 'IDSERV')
        service['begDate'] = self.getElementValue(serviceElement, 'DATE_IN', typeName='d')
        service['endDate'] = self.getElementValue(serviceElement, 'DATE_OUT', typeName='d')
        service['code'] = self.getElementValue(serviceElement, 'CODE_USL')
        service['amount'] = self.getElementValue(serviceElement, 'KOL_USL', typeName='double')
        service['price'] = self.getElementValue(serviceElement, 'TARIF', typeName='double', return_null=True)
        service['sum'] = self.getElementValue(serviceElement, 'SUMV_USL', typeName='double')

        return service

    def _get_event_service_info(self, eventElement):
        """ Обработка узла sluch (необходимо для обновления сумм КПГ-услуг, которые не идут в USL)

        :param serviceElement: DOMElement соответствующий узлу SLUCH
        :return: словарь с основными данными об услуге
        """
        service = {}
        # Копируем существующий список ошибок
        service['begDate'] = self.getElementValue(eventElement, 'DATE_1', typeName='d')
        service['endDate'] = self.getElementValue(eventElement, 'DATE_2', typeName='d')
        service['code'] = self.getElementValue(eventElement, 'CODE_MES1')
        service['price'] = self.getElementValue(eventElement, 'TARIF', typeName='double', return_null=True)
        service['sum'] = self.getElementValue(eventElement, 'SUMV', typeName='double')

        return service


class CImportPayRefuseR85Engine(CExchangeImportR85Engine):
    sexMap = {u'Ж': 2, u'ж': 2, u'М': 1, u'м': 1}

    def __init__(self, db, orgId, progressInformer = None, format=None):
        # FIXME: orgId здесь не нужен, скопипасчен из нормального импорта новых счетов.
        super(CImportPayRefuseR85Engine, self).__init__(progressInformer)
        self._db = db if isinstance(db, CDatabase) else None
        self._orgId = orgId
        self._orgInfis = None

        self._refuseTypeIdCache = {}
        self._mapAccountIdToPayStatusMask = {}
        self._processedAccountIdSet = set()
        self.logger().setLevel(logging.INFO)


    def process(self, fileName):
        self.isAbort = False
        self._refuseTypeIdCache.clear()
        self._mapAccountIdToPayStatusMask.clear()
        self._processedAccountIdSet.clear()

        self.phaseReset(1)
        self.processFile(fileName)
        updateAccounts(self._processedAccountIdSet)
        self.logger().info(u'Импорт завершен успешно.')
        return True

    def processFile(self, fileName):
        docFile = None
        try:
            isOk, sourceType, sourceInfis, destType, destInfis, year, month, number = self.parseFileName(fileName)
            if not isOk:
                return False

            if not zipfile.is_zipfile(fileName):
                raise Exception(u'Файл %s не является zip-архивом' % fileName)

            zipFile = zipfile.ZipFile(fileName, 'r')
            zipItems = zipFile.namelist()
            if not zipItems:
                raise Exception(u'Zip-архив "%s" пуст' % fileName)
            zipItem = next((item for item in zipItems if not item.startswith('L')), None)
            if zipItem is None:
                raise Exception(u'Необходимый файл в zip-архиве не найден' % fileName)

            docFile = zipFile.open(zipItem)

            self.processDocument(CXMLHelper.loadDocument(QtCore.QString(docFile.read().decode(self.encoding))), sourceInfis)
        except Exception, e:
            self.logger().warning(u'Не удалось провести импорт (%s)' % e.message)
            self.onException()
            return False
        finally:
            if docFile:
                docFile.close()

    def processDocument(self, document, insurerInfis):
        self.nextPhase(document.elementsByTagName('SLUCH').length(), u'Обработка случаев лечения')

        rootElement = self.getElement(document, 'ZL_LIST', isRequired=True)
        if not rootElement:
            return False

        headerElement = self.getElement(rootElement, 'ZGLV', isRequired=True)
        if not headerElement:
            return False

        version = self.getElementValue(headerElement, 'VERSION', isRequired=True)
        if version != '2.1':
            return False

        date = self.getElementValue(headerElement, 'DATA', typeName='d')
        if not date.isValid():
            date = QtCore.QDate.currentDate()

        self._db.transaction(checkIsInit=True)
        try:
            entityElement = self.getElement(rootElement, 'ZAP')
            while not entityElement.isNull():
                self.processEntity(entityElement, date, insurerInfis)
                entityElement = entityElement.nextSiblingElement('ZAP')
            self._db.commit()
        except Exception, e:
            self._db.rollback()
            raise
        finally:
            self.finishPhase()

        return True

    def processEntity(self, entityElement, date, insurerInfis):
        entityKey = self.getElementValue(entityElement, 'N_ZAP')
        if not entityKey:
            return False

        try:
            patientElement = self.getElement(entityElement, 'PACIENT', isRequired=True)
            clientId = self.getElementValue(patientElement, 'ID_PAC', isRequired = True) # Применимо только в МО

            eventElement = patientElement.nextSiblingElement('SLUCH')
            while not eventElement.isNull():
                self.processEvent(eventElement, clientId, date, insurerInfis)
                eventElement = eventElement.nextSiblingElement('SLUCH')
                self.nextPhaseStep()


        except Exception, e:
            self.onException()
            self.logger().warning(u'Не удалось обработать запись N_ZAP=%s (%s)' % (entityKey, e.message))
            return False
        if self.isAbort:
            raise Exception(u'Прервано пользователем')
        return True

    def processEvent(self, eventElement, clientId, date, insurerInfis):
        eventId = self.getElementValue(eventElement, 'NHISTORY', isRequired=True) # Применимо только в МО

        tblEvent = self._db.table('Event')
        eventRecord = self._db.getRecordEx(table=tblEvent,
                                           cols=[tblEvent['id'].eq(eventId),
                                                 tblEvent['client_id'].eq(clientId),
                                                 tblEvent['deleted'].eq(0)])

        if not eventRecord:
            self.logger().warning(u'Не найден случай лечения NHISTORY=%s для пациента ID_PAC=%s' % (eventId, clientId))
            return False

        tblAccountItem = self._db.table('Account_Item')
        fields = [tblAccountItem['id'],
                      tblAccountItem['date'],
                      tblAccountItem['action_id'],
                      tblAccountItem['visit_id'],
                      tblAccountItem['event_id'],
                      tblAccountItem['master_id'],
                      tblAccountItem['refuseType_id'],
                      tblAccountItem['number'],
                      tblAccountItem['note']]
        accountItemList = self._db.getRecordList(tblAccountItem,
                                                 cols=fields,
                                                 where=[tblAccountItem['event_id'].eq(eventId)])
        self._db.transaction()
        try:
            for accountItem in accountItemList:
                oplata = self.getElementValue(eventElement, 'OPLATA', typeName='n')
                accountItem.setValue('date', toVariant(date))
                accountNote = forceStringEx(accountItem.value('note'))
                if insurerInfis:
                    accountNote += '$$insurer:%s$$' % insurerInfis
                sankElement = self.getElement(eventElement, 'SANK')
                if not sankElement.isNull():
                    refReason = self.getElementValue(sankElement, 'S_OSN')
                    accountNote += '\nS_COM: %s' % self.getElementValue(sankElement, 'S_COM')
                else:
                    refReason = '' if oplata != 0 else '53'  # mdldml: 53 -- flatCode "Некорректного заполнения полей реестра"

                accountItem.setValue('note', toVariant(accountNote))

                accountId = forceRef(accountItem.value('master_id'))
                payStatusMask = self.getPayStatusMask(accountId)
                if oplata != 1 and refReason:
                    refuseTypeId = self.getRefuseTypeId(refReason)
                    accountItem.setValue('refuseType_id', toVariant(refuseTypeId))
                    accountItem.setValue('number', toVariant(u'Отказ по МЭК'))
                    updateDocsPayStatus(accountItem, payStatusMask, CPayStatus.refusedBits)
                else:
                    accountItem.setValue('number', toVariant(u'Оплачено'))
                    accountItem.setValue('refuseType_id', toVariant(None))
                    updateDocsPayStatus(accountItem, payStatusMask, CPayStatus.payedBits)
                self._db.updateRecord(tblAccountItem, accountItem)
                self._processedAccountIdSet.add(accountId)

            self._db.commit()
        except:
            self._db.rollback()

    # Helpers
    def getPayStatusMask(self, accountId):
        result = self._mapAccountIdToPayStatusMask.get(accountId, None)
        if result is None:
            tblAccount = self._db.table('Account')
            tblContract = self._db.table('Contract')
            tbl = tblAccount.join(tblContract, tblContract['id'].eq(tblAccount['contract_id']))
            record = self._db.getRecordEx(tbl, tblContract['finance_id'], tblAccount['id'].eq(accountId))
            if record:
                result = getPayStatusMask(forceRef(record.value('finance_id')))
            self._mapAccountIdToPayStatusMask[accountId] = result
        return result

    def getRefuseTypeId(self, code):
        result = self._refuseTypeIdCache.get(code, -1)

        if result == -1:
            result = forceRef(self._db.translate(
                'rbPayRefuseType', 'flatCode', code, 'id'
            ))
            self._refuseTypeIdCache[code] = result

        return result

    def parseFileName(self, fileName):
        """
        Вычленяет из имени файла важную информацию.
        Предполагается, что имя файла представлено в формате:
            H + тип учреждения-отправителя
            + код в системе ОМС учреждения-отправителя
            + тип учреждения-получателя
            + код в системе ОМС учреждения-получателя
            + две последние цифры года + две цифры месяца
            + четырехзначный порядковый номер представления основной части в текущем году
        :param fileName: имя обрабатываемого файла
        :return: isOk, sourceType, sourceCode, destType, descCode, year, month, number
        """
        try:
            name = os.path.splitext(os.path.basename(fileName))[0].lower()
            if name[0] in ['h', 'd', 't']:
                nameParts = name.split('_')
                if len(nameParts) != 2: raise
                orgs, account = nameParts
                if len(orgs) < 11: raise
                if len(account) < 5: raise

                shifter = 0 if name[0] in ('h', 't') else 1
                sourceType = orgs[shifter+1]
                m_index = orgs.find('m')
                if m_index < 0:
                    raise
                sourceCodeLength = m_index - 2 - shifter
                sourceCode = orgs[shifter+2:shifter+2+sourceCodeLength]
                destType = orgs[shifter+2+sourceCodeLength]
                destCodeLength = 6
                destCode = orgs[shifter+3+sourceCodeLength:shifter+3+sourceCodeLength+destCodeLength]

                year = 2000 + forceInt(account[:2])
                month = account[2:4]
                number = account[4:]

                return True, sourceType, sourceCode, destType, destCode, year, month, number
            raise
        except Exception, e:
            self.logger().critical(u'Некорректное имя файла "%s" (%s)' % (fileName, e.message))
            self.onException()

        return False, u'', u'', u'', u'', 0, 0, None

class CImportPayRefuseR85Dialog(QtGui.QDialog):
    InitState = 0
    ImportState = 1

    MainEngine = CImportPayRefuseR85Engine
    # DDEngine = CImportR85DDTFEngine
    # TODO: Возможно, стоит отсюда выпилить эту разбивку, если принципиальных различий не появится
    engineByFormat = {'HS': MainEngine,
                      'HT': MainEngine,
                      'DP': MainEngine,
                      'DV': MainEngine,
                      'DO': MainEngine,
                      'DS': MainEngine,
                      'DU': MainEngine,
                      'DF': MainEngine,
                      'DD': MainEngine,
                      'DR': MainEngine,
                      'TS': MainEngine,
                      'TT': MainEngine,
                      }

    def __init__(self, db, orgId, parent = None, isFLC = False):
        super(CImportPayRefuseR85Dialog, self).__init__(parent)
        if isFLC:
            self.MainEngine = CImportPayRefuseR85EngineFLC
        self._db = db
        self._orgId = orgId
        self._pi = CProgressInformer(processEventsFlag=QtCore.QEventLoop.AllEvents)
        # self._engine = CImportR85TFEngine(db, orgId, progressInformer=self._pi) #TODO?
        # self._engine.setUserConfirmationFunction(self.userConfirmation)
        self._lastExceptionHandler = None
        # self._loggerHandler = CLogHandler(self._engine.logger(), self)
        # self._loggerHandler.setLevel(logging.INFO)
        self._currentState = self.InitState

        self.setupUi()

        self.onStateChanged()
        self._engines = {}
        self._isFLC = isFLC


    def setLastExceptionHandler(self, handler):
        self._lastExceptionHandler = handler

    def setParams(self, params):
        if isinstance(params, dict):
            fileName = forceStringEx(getPref(params, 'inputFile', u''))
            if os.path.isfile(fileName):
                self.edtFileName.setText(fileName)


    def engine(self, format):
        engine = self._engines.get(format, None) # self._engine
        if engine is None:
            engine = self.engineByFormat.get(format, self.MainEngine)(self._db, self._orgId, progressInformer=self._pi, format=format)
            engine.setLastExceptionHandler(self._lastExceptionHandler)
            engine.setUserConfirmationFunction(self.userConfirmation)
            loggerHandler = CLogHandler(engine.logger(), self)
            loggerHandler.setLevel(logging.INFO)
            loggerHandler.logged.connect(self.logInfo.append)
            self._engines[format] = engine
        return engine



    def params(self):
        params = {}
        setPref(params, 'inputFile', forceStringEx(self.edtFileName.text()))
        return params


    @property
    def currentState(self):
        return self._currentState


    @currentState.setter
    def currentState(self, value):
        if value in [self.InitState, self.ImportState]:
            self._currentState = value
            self.onStateChanged()


    def onStateChanged(self):
        self.btnNextAction.setText(self._actionNames.get(self.currentState, u'<Error>'))
        self.btnClose.setEnabled(self.currentState != self.ImportState)
        self.gbInit.setEnabled(self.currentState == self.InitState)
        self.gbImport.setEnabled(self.currentState == self.ImportState)
        # self.btnSave.setEnabled(bool(self._engine.documents))
        QtCore.QCoreApplication.processEvents()


    # noinspection PyAttributeOutsideInit
    def setupUi(self):
        layout = QtGui.QVBoxLayout()
        # init block
        self.gbInit = QtGui.QGroupBox()
        gbLayout = QtGui.QVBoxLayout()
        lineLayout = QtGui.QHBoxLayout()
        self.edtFileName = QtGui.QLineEdit()
        self.edtFileName.setReadOnly(True)
        self.edtFileName.textChanged.connect(self.onFileNameChanged)
        lineLayout.addWidget(self.edtFileName)
        self.btnBrowseFile = QtGui.QToolButton()
        # noinspection PyUnresolvedReferences
        self.btnBrowseFile.clicked.connect(self.onBrowseFileClicked)
        lineLayout.addWidget(self.btnBrowseFile)
        gbLayout.addLayout(lineLayout)
        self.gbInit.setLayout(gbLayout)
        layout.addWidget(self.gbInit)

        # import block
        self.gbImport = QtGui.QGroupBox()
        gbLayout = QtGui.QVBoxLayout()
        self.progressBar = CProgressBar()
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar.setRange(0, 0)
        self.progressBar.setProgressFormat(u'(%v/%m)')
        self._pi.progressChanged.connect(self.progressBar.setProgress)
        gbLayout.addWidget(self.progressBar)
        self.gbImport.setLayout(gbLayout)
        layout.addWidget(self.gbImport)

        # log block
        self.logInfo = QtGui.QTextEdit()
        layout.addWidget(self.logInfo)
        # self._loggerHandler.logged.connect(self.logInfo.append)

        # buttons block
        subLayout = QtGui.QHBoxLayout()
        self.btnNextAction = QtGui.QPushButton()
        # noinspection PyUnresolvedReferences
        self.btnNextAction.clicked.connect(self.onNextActionClicked)
        subLayout.addStretch()
        subLayout.addWidget(self.btnNextAction)
        self.btnClose = QtGui.QPushButton()
        # noinspection PyUnresolvedReferences
        self.btnClose.clicked.connect(self.onCloseClicked)
        subLayout.addWidget(self.btnClose)
        layout.addLayout(subLayout)

        self.setLayout(layout)
        self.setMinimumWidth(512)
        self.retranslateUi()


    # noinspection PyAttributeOutsideInit
    def retranslateUi(self):
        context = unicode(getClassName(self))
        self.setWindowTitle(forceTr(u'Импорт отказов. Крым. ТФОМС.', context))
        self.gbInit.setTitle(forceTr(u'Параметры импорта', context))

        self.gbImport.setTitle(forceTr(u'Импорт', context))

        self._actionNames = {self.InitState: forceTr(u'Импорт',context),
                             self.ImportState: forceTr(u'Прервать', context)}
        self.btnClose.setText(forceTr(u'Закрыть', context))


    def userConfirmation(self, title, message):
        return QtGui.QMessageBox.Yes == QtGui.QMessageBox.question(self,
                                                                   title,
                                                                   message,
                                                                   QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                                                   QtGui.QMessageBox.No)



    @QtCore.pyqtSlot()
    def onNextActionClicked(self):
        if self.currentState == self.InitState:
            self.currentState = self.ImportState
            try:
                self.engine(self._currentFormat).process(forceStringEx(self.edtFileName.text()))
            except Exception, e:
                self.currentState = self.InitState
                raise
            self.currentState = self.InitState

        elif self.currentState == self.ImportState:
            self.engine(self._currentFormat).abort()
            self.currentState = self.InitState
        self.onStateChanged()


    def canClose(self):
        return True
        # not self._engine.documents or \
        #        QtGui.QMessageBox.warning(self,
        #                                  u'Внимание',
        #                                  u'Остались несохраненные файлы выгрузок,\n'
        #                                  u'которые будут утеряны.\n'
        #                                  u'Уверены, что хотить выйти из экспорта?\n',
        #                                  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
        #                                  QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes


    def closeEvent(self, event):
        if self.canClose():
            event.accept()
        else:
            event.ignore()


    def done(self, result):
        if self.canClose():
            super(CImportPayRefuseR85Dialog, self).done(result)



    @QtCore.pyqtSlot()
    def onCloseClicked(self):
        self.accept()


    @QtCore.pyqtSlot()
    def onBrowseFileClicked(self):
        if self._isFLC:
            fileName = forceStringEx(QtGui.QFileDialog.getOpenFileName(self,
                                                                       u'Укажите файл для импорта',
                                                                       self.edtFileName.text(),
                                                                       u'Файлы (HS*.zip HT*.zip DP*.zip DV*.zip DO*.zip '
                                                                       u'DS*.zip DU*.zip DF*.zip DD*.zip DR*.zip '
                                                                       u'TS*.zip TT*.zip '
                                                                       u'PHS*.zip PHT*.zip PDP*.zip PDV*.zip '
                                                                       u'PDO*.zip PDS*.zip PDU*.zip PDF*.zip PDD*.zip '
                                                                       u'PDR*.zip PHM*.zip PTS*.zip PTT*.zip'
                                                                       u'VHS*.zip VHT*.zip VDP*.zip VDV*.zip '
                                                                       u'VDO*.zip VDS*.zip VDU*.zip VDF*.zip VDD*.zip '
                                                                       u'VDR*.zip VHM*.zip VTS*.zip VTT*.zip'
                                                                       u'VHS*.xml VHT*.xml VDP*.xml VDV*.xml '
                                                                       u'VDO*.xml VDS*.xml VDU*.xml VDF*.xml VDD*.xml '
                                                                       u'VDR*.xml VHM*.xml VTS*.xml VTT*.xml )'))
        else:
            fileName = forceStringEx(QtGui.QFileDialog.getOpenFileName(self,
                                                                       u'Укажите файл для импорта',
                                                                       self.edtFileName.text(),
                                                                       u'Файлы (HS*.zip HT*.zip DP*.zip DV*.zip DO*.zip '
                                                                       u'DS*.zip DU*.zip DF*.zip DD*.zip DR*.zip '
                                                                       u'TS*.zip TT*.zip '))

        if os.path.isfile(fileName):
            self.edtFileName.setText(fileName)

    @QtCore.pyqtSlot(QtCore.QString)
    def onFileNameChanged(self, text):
        self._currentFormat = os.path.basename(forceStringEx(text))[:2]


