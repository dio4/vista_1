# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

import sys

from PyQt4 import QtCore, QtGui

import library.exception
from Events.Action      import CAction

from Exchange.Utils     import prepareRefBooksCacheByCode
from Exchange.reg_iemk.iemc_settings    import CRegIemcSettings

from library            import database
from library.Utils      import forceDate, forceRef, forceString, toVariant, smartDict, formatName

from Registry.Utils     import getClientAddress, getClientDocument, getClientPolicy

# from Ui_ImportR67XML_VM import Ui_Dialog

# class IncompleteNSIException(Exception):
#     pass
#
# class EventTypeNotFoundException(IncompleteNSIException):
#     pass
#
# class ActionTypeNotFoundException(IncompleteNSIException):
#     pass
#
# class ActionPropertyTypeNotFoundException(IncompleteNSIException):
#     pass
# TODO: Добавить Event.orgId

class CErrorLevel(object):
    fatal = 0
    error = 1
    warning = 2
    info = 3
    debug = 4

# def importR67XML_VM(widget):
#     dlg = CImportR67XML_VM_GUI()
#     dlg.edtFileName.setText(forceString(getVal(
#         QtGui.qApp.preferences.appPrefs, 'ImportR67XML_VMFileName', '')))
#     dlg.exec_()
#     QtGui.qApp.preferences.appPrefs['ImportR67XML_VMFileName'] = toVariant(dlg.edtFileName.text())



class CImportR67XML_VM(object):
    """Импорт ИЭМК пациента из XML-файла, созданного с помощью ВистаМед.

    Класс предназначен для занесения в базу всех доступных в XML-файле данных о пациенте.
    Предполагается возможность работы как с одним импортируемым файлом, так и с целой директорией.
    После обработки файлы переносятся в поддиректорию <import_dir>/done, имя сохраняется.
    Информация об ошибках в записях заносится в XML-файл c названием err_<input_file_name>.xml
    По умолчанию файл с ошибками размещается в поддиректории <import_dir>/err, если не указано иное.
    Для корректной работы все используемые при передаче данных справочники должны быть идентичны со справочниками
    экспортирующего учреждения.
    Данный класс рассчитан на запуск из командной строки. Для использования графического интерфейса необходимо
    унаследоваться от данного класса.
    """

    clientAttrs = ['id', 'modifyDatetime', 'lastName', 'firstName', 'patrName', 'sex', 'birthDate', 'birthPlace', 'SNILS']
    clientPolicyAttrs = ['serial', 'number', 'begDate', 'endDate', 'name', 'policyTypeCode', 'policyKindCode', 'insurerCode']
    clientDocumentAttrs = ['serial', 'number', 'date', 'origin', 'documentTypeCode']
    eventAttrs = ['modifyDatetime', 'setDate', 'execDate', 'externalId', 'isPrimary', 'order', 'eventTypeCode', 'execPersonCode', 'resultCode', 'MESCode', 'orgCode']
    diagnosticAttrs = ['diagnosticSetDate', 'diagnosticEndDate', 'MKB', 'diagnosisSetDate', 'diagnosisEndDate', 'diagnosticTypeCode', 'diagnosticCharacterCode', 'diagnosticStageCode', 'diagnosticPhaseCode', 'diagnosticPersonCode', 'diagnosticResultCode', 'diagnosisTypeCode', 'diagnosisCharacterCode', 'diagnosisPersonCode']
    visitAttrs = ['isPrimary', 'date', 'sceneCode', 'visitTypeCode', 'personCode', 'serviceCode', 'financeCode']
    actionAttrs = ['actionTypeCode', 'status', 'begDate', 'endDate', 'amount', 'uet', 'MKB', 'duration', 'personCode', 'orgCode']
    actionPropertyAttrs = ['actionPropertyType', 'actionPropertyValue']

    def __init__(self, config_name='reg_iemc'):
        self.settings = CRegIemcSettings(config_name)
        self.prepareDatabase()

        self.tableClient = self.db.table('Client')
        self.tableClientAddress = self.db.table('ClientAddress')
        self.tableClientPolicy = self.db.table('ClientPolicy')
        self.tableClientDocument = self.db.table('ClientDocument')
        self.tableEvent = self.db.table('Event')
        self.tableAction = self.db.table('Action')
        self.tableDiagnostic = self.db.table('Diagnostic')
        self.tableDiagnosis = self.db.table('Diagnosis')
        self.tableVisit = self.db.table('Visit')

        self._updateRegData = False
        self.nProcessed = 0
        self.nUpdated = 0
        self.nAdded = 0
        self._depth = 0     # Глубина: 0 - ничего, 1 - IEMC, 2 - ORG/PERS_LIST, 3 - ZGLV/Client, 4 - Event, 5 - Action.
                            # Остальное не может иметь ветвей и не считается
        self.exporterOrgCode = ''
        self._cache = smartDict()   # Кэш справочников
        self._mapOrgCodeToId = {}
        self._mapPersonCodeToId = {}
        self._mapEventTypeCodeToId = {}
        self._mapEventTypeCodeToPurposeId = {}
        self._mapMesCodeToId = {}
        self._mapServiceCodeToId = {}
        self._mapPersonIdToSpecialityId = {}

        self.logs = {CErrorLevel.fatal: [],
                     CErrorLevel.error: [],
                     CErrorLevel.warning: [],
                     CErrorLevel.debug: [],
                     CErrorLevel.info: []}
        self.inFile = None
        self.processedEvents = []

#---------------------- Utils ----------------------------
    def prepareDatabase(self):
        connectionInfo = self.settings.getConnectionInfo()
        self.db = database.connectDataBaseByInfo(connectionInfo)
        QtGui.qApp.db = self.db

    def closeDatabase(self):
        self.db.close()
    # def attributes(self):
    #     return self._xmlReader.attributes()

    # def processPlainAttrs(self, entity, attrNames):
    #     '''
    #         Поиск всех полей attrNames в атрибутах текущего элемента
    #     '''
    #     result = {}
    #     for name in attrNames:
    #         if entity.hasAttribute(name):
    #             result[name] = forceString(entity.attribute(name))
    #         else:
    #             result[name] = u''
    #     return result

    def prepareRefBooks(self):
        """
            Кэшируем все небольшие справочники, чтобы не плодить массу одинаковых запросов.
            Исходим из допущения, что коды уникальны.
        """
        self._cache = prepareRefBooksCacheByCode()

    def getOrgIdByCode(self, code):
        orgId = self._mapOrgCodeToId.get(code, None)
        if not orgId:
            orgId = forceRef(self.db.translate('Organisation', 'miacCode', code, 'id'))
            self._mapOrgCodeToId[code] = orgId
        return orgId

    def getPersonIdByCode(self, code):
        personId = self._mapPersonCodeToId.get(code, None)
        if not personId:
            personId = forceRef(self.db.translate('Person', 'code', code, 'id'))
            specialityId = forceRef(self.db.translate('Person', 'id', personId, 'speciality_id'))
            self._mapPersonCodeToId[code] = personId
            self._mapPersonIdToSpecialityId[personId] = specialityId
        return personId

    def getSpecialityIdByPersonId(self, personId):
        return self._mapPersonIdToSpecialityId.get(personId, None)

    def getEventTypeIdByCode(self, code):
        eventTypeId = self._mapEventTypeCodeToId.get(code, None)
        if not eventTypeId:
            eventTypeRecord = self.db.getRecordEx('EventType', 'id, purpose_id', 'code = \'%s\'' % code)
            if eventTypeRecord:
                eventTypeId = forceRef(eventTypeRecord.value('id'))
                self._mapEventTypeCodeToId[code] = eventTypeId
                self._mapEventTypeCodeToPurposeId[code] = forceRef(eventTypeRecord.value('purpose_id'))
        return eventTypeId

    def getEventTypePurposeIdByCode(self, code):
        eventTypePurposeId = self._mapEventTypeCodeToPurposeId.get(code, None)
        if not eventTypePurposeId:
            eventTypeRecord = self.db.getRecordEx('EventType', 'id, purpose_id', 'code = \'%s\'' % code)
            eventTypePurposeId = forceRef(eventTypeRecord.value('purpose_id'))
            self._mapEventTypeCodeToId[code] = forceRef(eventTypeRecord.value('id'))
            self._mapEventTypeCodeToPurposeId[code] = eventTypePurposeId
        return eventTypePurposeId

    def getMesIdByCode(self, code):
        mesId = self._mapMesCodeToId.get(code, None)
        if not mesId:
            mesId = self.db.translate('mes.MES', 'code', code, 'id')
            self._mapMesCodeToId[code] = mesId
        return mesId

    def getServiceIdByCode(self, code):
        serviceId = self._mapServiceCodeToId.get(code, None)
        if not serviceId:
            serviceId = self.db.translate('rbService', 'code', code, 'id')
            self._mapServiceCodeToId[code] = serviceId
        return serviceId

    def err2log(self, errorLevel, message, recordType=None, recordId=None):
        """Лог ошибок импорта.

        @param errorLevel: уровень ошибки. Ошибки уровня error экспортируются обратно отправителю данных. Все остальные обрабатываются локально.
        @param message: В идеале - сообщение об ошибке.
        @param recordType: Ошибка в рег. данных или в обращении?
        @param recordId: Идентификатор записи в файле импорта (следовательно, и в базе отправителя)
        """

        log = self.logs.setdefault(errorLevel, [])
        log.append((message, recordType, recordId))
        # if self.log:
        #     self.log.append((message, recordType, recordId))

    def getEventsLog(self):
        """Возвращает лог всех обработанных обращений - удачных и не очень

        @return:
        """
        log = self.logs.get(CErrorLevel.error, [])[:]
        for eventId in self.processedEvents:
            log.append(('Success', 'Event', eventId))
        self.logs[CErrorLevel.error] = []
        return log

    # def processIntermediateErrors(self):
    #     errors = self.logs.get(CErrorLevel.error, [])
    #
    #     if errors:
    #         errDoc = CXmlErrorWriter.fillDocument(errors, self.exporterOrgCode)
    #         stream = QtCore.QTextStream()
    #         stream.setDevice(self.errFile)
    #         errDoc.save(stream, 4)
    #         self.logs[CErrorLevel.error] = []

    def processErrors(self):
        """Вывод сообщений в поток вывода ошибок.

        @return:
        """
        verbosity = self.settings.getVerbose()
        for level, items in self.logs.items():
            if level <= verbosity and level != 1:
                for message, type, recordId in items:
                    print >> sys.stderr, items[0]


    def startImport(self, request):
        """Запуск процедуры импорта.

        Если в настройках указано имя конкретного файла, используем для импорта только этот файл.
        Если указана только входная директория, ищем в ней все подходящие файлы и пытаемся произвести импорт.
        """
        self.prepareRefBooks()
        self.processedEvents = []
        # self.doc = QtXml.QDomDocument()
        # root = self.doc.documentElement()

        self.exporterOrgCode = request.Org

        self.readClients(request.Clients.Client)
        # self.cleanup()
        self.processErrors()

    #----------------- Parsing xml file ------------------------
    def readClients(self, clients):
        for client in clients:
            correctEvents = []
            for event in client.Event:
                if self.checkEventData(event) == 0:
                    correctEvents.append(event)
            client.Event = correctEvents
            self.processClientData(client)
#        self.processIntermediateErrors()


    def checkEventData(self, eventData):
        """Проверяет наличие требуемых полей в импортируемых данных, а также соответствий в БД, куда производится импорт.
        Для устранения дублирующихся вызовов идентификаторы записей в справочниках БД также заносятся в поля экземпляра
        обращения.

        @param eventData: экземпляр обращения
        """
        eventId = eventData.ExternalId
        eventTypeCode = eventData.EventTypeCode
        if not eventTypeCode:
            self.err2log(CErrorLevel.error,
                         'Event type code not specified',
                         'Event',
                         eventId
                         )
            return -1
        eventTypeId = self.getEventTypeIdByCode(eventTypeCode)
        if not eventTypeId:
            self.err2log(CErrorLevel.error,
                         'Event type with code %s was not found in target database' % eventTypeCode,
                         'Event',
                         eventId)
            return -2
        eventData.eventTypeId = eventTypeId
        for actionData in eventData.Action:
            actionTypeCode = actionData.ActionTypeCode
            if not actionTypeCode:
                self.err2log(CErrorLevel.error,
                             'Action type code not specified',
                             'Event',
                             eventId)
                return -3
            try:
                action = CAction.createByTypeCode(actionTypeCode)
            except AssertionError:
                self.err2log(CErrorLevel.error,
                             'Action type with code %s was not found in target database' % actionData.actionTypeCode,
                             'Event',
                             eventId)
                return -4
            actionData.instance = action
            for ap in actionData.ActionProperty:
                apType = ap.ActionPropertyType
                if not apType:
                    self.err2log(CErrorLevel.error,
                                 u'Action property type not specified in action with action type code "%s"' % actionTypeCode,
                                 'Event',
                                 eventId)
                    return -5
                try:
                    action[apType] = ap.ActionPropertyValue
                except KeyError:
                    self.err2log(CErrorLevel.error,
                                 u'Action property with type "%s" not found in description of ActionType with code "%s"' % (ap.ActionPropertyType, actionTypeCode),
                                 'Event',
                                 eventId)
                    return -6
        return 0


    #------------- Processing client data -----------------------

    def isClientExisting(self, client):
        db = self.db

        externalId = '.'.join([self.exporterOrgCode, forceString(client.ClientId)])
        tableClientIdentification = db.table('ClientIdentification')
        tableAccountingSystem = db.table('rbAccountingSystem')
        queryTable = tableClientIdentification.join(tableAccountingSystem, tableAccountingSystem['id'].eq(tableClientIdentification['accountingSystem_id']))
        clientRecord = db.getRecordEx(queryTable, tableClientIdentification['client_id'],
                         [tableAccountingSystem['code'].eq('67VM'), tableClientIdentification['identifier'].eq(externalId)])
        if clientRecord:
            clientId = forceRef(clientRecord.value('client_id'))
            if clientId:
                return clientId, True

        if client.SNILS:
            clientId = forceRef(db.translate(self.tableClient, 'SNILS', client.SNILS, 'id'))
            if clientId:
                return clientId, False

        if client.Policy:
            policyKind = self._cache.policyKind.get(client.Policy.PolicyKindCode, '')
            policyKindId = policyKind['id'] if policyKind else None

            if policyKindId and client.Policy.Serial and client.Policy.Number:
                policyCond = [self.tableClientPolicy['serial'].eq(client.Policy.Serial),
                              self.tableClientPolicy['number'].eq(client.Policy.Number),
                              self.tableClientPolicy['policyKind_id'].eq(policyKindId),
                              self.tableClientPolicy['deleted'].eq(0)]

                policyRecord = db.getRecordEx(self.tableClientPolicy, 'client_id', policyCond)
                if policyRecord:
                    return forceRef(policyRecord.value('client_id')), False

        if client.Document:
            documentType = self._cache.documentType.get(client.Document.DocumentTypeCode, None)
            documentTypeId = documentType['id'] if documentType else None

            if documentTypeId and client.Document.Serial and client.Document.Number:
                documentCond = [self.tableClientDocument['serial'].eq(client.Document.Serial),
                                self.tableClientDocument['number'].eq(client.Document.Number),
                                self.tableClientDocument['documentType_id'].eq(documentTypeId),
                                self.tableClientDocument['deleted'].eq(0)]
                documentRecord = db.getRecordEx(self.tableClientDocument, 'client_id', documentCond)
                if documentRecord:
                    return forceRef(documentRecord.value('client_id')), False

        clientCond = [self.tableClient['lastName'].eq(client.LastName),
                      self.tableClient['firstName'].eq(client.FirstName),
                      self.tableClient['patrName'].eq(client.PatrName),
                      self.tableClient['birthDate'].eq(QtCore.QDate.fromString(client.BirthDate, QtCore.Qt.ISODate)),
                      self.tableClient['sex'].eq(client.Sex)]
        clientRecord = db.getRecordEx(self.tableClient, 'id', clientCond)
        if clientRecord:
            return forceRef(clientRecord.value('id')), False

        return None, False

    #--------------- Writing to database -----------------------
    def processClientData(self, client):
        """
            Добавление/изменение данных о пациенте в БД.
        """
        clientId, hasLocalIdentifier = self.isClientExisting(client)
        db = self.db
        updatePersonalData = True
        isNew = not clientId
        if clientId:
            modifyDatetime = QtCore.QDateTime.fromString(forceString(db.translate(self.tableClient, 'id', clientId, 'notes')), QtCore.Qt.ISODate)
            newModifyDatetime = QtCore.QDateTime.fromString(client.ModifyDatetime, QtCore.Qt.ISODate)
            if modifyDatetime >= newModifyDatetime:
                updatePersonalData = False
            else:
                clientRecord = db.getRecordEx('Client', 'lastName, firstName, patrName, birthDate, birthPlace, sex, SNILS, notes', where=[self.tableClient['id'].eq(clientId)])
        else:
            clientRecord = self.tableClient.newRecord()

        db.transaction()
        try:
            if self._updateRegData or not clientId:
                if updatePersonalData:
                    clientRecord.setValue('lastName', toVariant(client.LastName))
                    clientRecord.setValue('firstName', toVariant(client.FirstName))
                    clientRecord.setValue('patrName', toVariant(client.PatrName))
                    clientRecord.setValue('birthDate', toVariant(client.BirthDate))
                    clientRecord.setValue('birthPlace', toVariant(client.BirthPlace))
                    clientRecord.setValue('sex', toVariant(client.Sex))
                    clientRecord.setValue('SNILS', toVariant(client.SNILS))
                    clientRecord.setValue('notes', toVariant(client.ModifyDatetime))
                    clientId = db.insertOrUpdate(self.tableClient, clientRecord)
                    if not hasLocalIdentifier:
                        tableClientIdentification = db.table('ClientIdentification')
                        clientIdentificationRecord = tableClientIdentification.newRecord()
                        accSystemId = db.translate('rbAccountingSystem', 'code', '67VM', 'id') #FIXME: вынести в атрибуты класса
                        clientIdentificationRecord.setValue('client_id', toVariant(clientId))
                        clientIdentificationRecord.setValue('accountingSystem_id', accSystemId)
                        clientIdentificationRecord.setValue('identifier', toVariant('.'.join([self.exporterOrgCode, forceString(client.ClientId)])))
                        db.insertRecord(tableClientIdentification, clientIdentificationRecord)

                    self.processPolicy(isNew, clientId, client.Policy)
                    self.processDocument(isNew, clientId, client.Document)

                    self.processAddress(isNew, clientId, 0, client.RegAddress)
                    self.processAddress(isNew, clientId, 1, client.LocAddress)

                    # self.currentClientData.isUpdated = True
                else:
                    self.err2log(CErrorLevel.info,
                                 u'В базе содержатся актуальные персональные данные пациента %s, пропускаем.' % formatName(
                                        client.LastName, client.FirstName, client.PatrName),
                    )

            if not self._updateRegData:
                for event in client.Event:
                    db.transaction()
                    try:
                        self.processEvent(isNew, clientId, event)
                        self.processedEvents.append(event.ExternalId)
                        db.commit()
                    except library.exception.CDatabaseException as e:
                        db.rollback()
                        self.err2log(CErrorLevel.error,
                                     'Database error: %s' % e,
                                     'Event',
                                     event.ExternalId)
                    except Exception as e:
                        db.rollback()
                        self.err2log(CErrorLevel.error,
                                     'Unexpected error: %s at line %s' % (e, sys.exc_info()[2].tb_lineno),
                                     'Event',
                                     event.ExternalId)
            db.commit()
        except library.exception.CDatabaseException as e:
            db.rollback()
            self.err2log(CErrorLevel.error,
                         'Database error: %s' % e,
                         'Client',
                         client.ClientId)
            raise e
        except Exception as e:
            db.rollback()
            self.err2log(CErrorLevel.error,
                         'Unexpected error: %s at line %s' % (e, sys.exc_info()[2].tb_lineno))
            raise e

        # self.nProcessed += 1
        # if self.currentClientData.isUpdated:
        #     if isNew:
        #         self.nAdded += 1
        #     else:
        #         self.nUpdated += 1

    def processPolicy(self, isNew, clientId, policy):
        """Запись данных о полисе пациента. Если не совпадает со старым - добавляем новую запись.

        @param isNew: пациент отсутствует в базе. Если это не так, то производится поиск полиса и определение необходимости изменения данных.
        @param clientId: id пациента
        @param policy: данные о полисе.
        @return: None
        """
        if policy:
            db = self.db
            policyType = self._cache.policyType.get(policy.PolicyTypeCode, None)
            policyTypeId = policyType['id'] if policyType else None
            policyKind = self._cache.policyKind.get(policy.PolicyKindCode, '')
            policyKindId = policyKind['id'] if policyKind else None
            insurerId = self.getOrgIdByCode(policy.InsurerCode)

            if isNew:
                clientPolicyRecord = self.tableClientPolicy.newRecord()
            else:
                clientPolicyRecord = getClientPolicy(clientId)
                if clientPolicyRecord is None or \
                    forceString(clientPolicyRecord.value('serial')) != policy.Serial or \
                    forceString(clientPolicyRecord.value('number')) != policy.Number or \
                    forceDate(clientPolicyRecord.value('begDate')).toString(QtCore.Qt.ISODate) != policy.BegDate or \
                    forceDate(clientPolicyRecord.value('endDate')).toString(QtCore.Qt.ISODate) != policy.EndDate or \
                    forceString(clientPolicyRecord.value('name')) != policy.Name or \
                    forceRef(clientPolicyRecord.value('policyType_id')) != policyTypeId or \
                    forceRef(clientPolicyRecord.value('policyKind_id')) != policyKindId or \
                    forceRef(clientPolicyRecord.value('insurer_id')) != insurerId:

                    clientPolicyRecord = self.tableClientPolicy.newRecord()
                else:
                    return

            clientPolicyRecord.setValue('serial', toVariant(policy.Serial))
            clientPolicyRecord.setValue('number', toVariant(policy.Number))
            clientPolicyRecord.setValue('begDate', toVariant(QtCore.QDate.fromString(policy.BegDate, QtCore.Qt.ISODate)))
            clientPolicyRecord.setValue('endDate', toVariant(QtCore.QDate.fromString(policy.EndDate, QtCore.Qt.ISODate)))
            clientPolicyRecord.setValue('name', toVariant(policy.Name))
            clientPolicyRecord.setValue('insurer_id', toVariant(insurerId))
            if policyTypeId:
                clientPolicyRecord.setValue('policyType_id', toVariant(policyTypeId))
            if policyKindId:
                clientPolicyRecord.setValue('policyKind_id', toVariant(policyKindId))
            clientPolicyRecord.setValue('client_id', toVariant(clientId))

            db.insertOrUpdate(self.tableClientPolicy, clientPolicyRecord)

    def processDocument(self, isNew, clientId, document):
        """Запись данных о документе, удостоверяющем личность пациента. Если не совпадает со старым - добавляем новую запись

        @param isNew: пациент отсутствует в базе. Если это не так, то производится поиск полиса и определение необходимости изменения данных.
        @param clientId: id пациента.
        @param document: данные о документе.
        @return: None
        """
        if document:
            db = self.db
            documentType = self._cache.documentType.get(document.DocumentTypeCode, None)
            documentTypeId = documentType['id'] if documentType else None

            # Возможно, следует возвращать ошибку.
            if not documentTypeId:
                return

            if isNew:
                clientDocumentRecord = self.tableClientDocument.newRecord()
            else:
                clientDocumentRecord = getClientDocument(clientId)
                if clientDocumentRecord is None or \
                    forceString(clientDocumentRecord.value('serial')) != document.Serial or \
                    forceString(clientDocumentRecord.value('number')) != document.Number or \
                    forceDate(clientDocumentRecord.value('date')).toString(QtCore.Qt.ISODate) != document.Date or \
                    forceString(clientDocumentRecord.value('origin')) != document.Origin or \
                    forceRef(clientDocumentRecord.value('documentType_id')) != documentTypeId:

                    clientDocumentRecord = self.tableClientDocument.newRecord()
                else:
                    return

            clientDocumentRecord.setValue('serial', toVariant(document.Serial))
            clientDocumentRecord.setValue('number', toVariant(document.Number))
            clientDocumentRecord.setValue('date', toVariant(QtCore.QDate.fromString(document.Date, QtCore.Qt.ISODate)))
            clientDocumentRecord.setValue('origin', toVariant(document.Origin))
            clientDocumentRecord.setValue('documentType_id', toVariant(documentTypeId))
            clientDocumentRecord.setValue('client_id', toVariant(clientId))

            db.insertOrUpdate(self.tableClientDocument, clientDocumentRecord)

    def processAddress(self, isNew, clientId, type, addr):
        # Если не совпадает со старым - добавляем новую запись
        if addr:
            db = self.db
            if not isNew:
                addrRecord = getClientAddress(clientId, type)
                if addrRecord and forceString(addrRecord.value('freeInput')) == addr:
                    return
            newAddrRecord = self.tableClientAddress.newRecord()
            newAddrRecord.setValue('freeInput', toVariant(addr))
            newAddrRecord.setValue('type', toVariant(type))
            newAddrRecord.setValue('client_id', toVariant(clientId))
            db.insertRecord(self.tableClientAddress, newAddrRecord)

    def processEvent(self, isNew, clientId, event):
        # Если есть старая версия обращения - полностью удаляется все, с ней связанное и формируется с нуля
        db = self.db
        if isNew:
            record = self.tableEvent.newRecord()
        else:
            cond = [self.tableEvent['client_id'].eq(clientId),
                    self.tableEvent['externalId'].eq(event.ExternalId)]
            record = db.getRecordEx(self.tableEvent, '*', where=db.joinAnd(cond))
            if record:
                modifyDatetime = QtCore.QDateTime.fromString(forceString(record.value('note')), QtCore.Qt.ISODate)
                newModifyDatetime = QtCore.QDateTime.fromString(event.ModifyDatetime, QtCore.Qt.ISODate)
                if modifyDatetime >= newModifyDatetime:
                    return

                self.prepareOldEvent(forceRef(record.value('id')))
            else:
                record = self.tableEvent.newRecord()

        eventTypePurposeId = self.getEventTypePurposeIdByCode(event.EventTypeCode)
        execPersonId = self.getPersonIdByCode(event.ExecPersonCode)
        mesId = self.getMesIdByCode(event.MESCode)
        result = self._cache.result.get((event.ResultCode, eventTypePurposeId), None)
        resultId = result['id'] if result else None
        orgId = self.getOrgIdByCode(event.OrgCode)

        record.setValue('client_id', toVariant(clientId))
        record.setValue('setDate', toVariant(QtCore.QDate.fromString(event.SetDate, QtCore.Qt.ISODate)))
        record.setValue('execDate', toVariant(QtCore.QDate.fromString(event.ExecDate, QtCore.Qt.ISODate)))
        record.setValue('externalId', toVariant(event.ExternalId))
        record.setValue('order', toVariant(event.Order))
        record.setValue('isPrimary', toVariant(event.IsPrimary))
        record.setValue('execPerson_id', toVariant(execPersonId))
        record.setValue('eventType_id', toVariant(event.eventTypeId))
        record.setValue('mes_id', toVariant(mesId))
        record.setValue('result_id', toVariant(resultId))
        record.setValue('org_id', toVariant(orgId))
        record.setValue('note', toVariant(event.ModifyDatetime))
        eventId = db.insertOrUpdate(self.tableEvent, record)

        for visit in event.Visit:
            scene = self._cache.scene.get(visit.SceneCode, None)
            sceneId = scene['id'] if scene else None
            visitType = self._cache.visitType.get(visit.VisitTypeCode, None)
            visitTypeId = visitType['id'] if visitType else None
            personId = self.getPersonIdByCode(visit.PersonCode)
            serviceId = self.getServiceIdByCode(visit.ServiceCode)
            finance = self._cache.finance.get(visit.FinanceCode, None)
            financeId = finance['id'] if finance else None

            visitRecord = self.tableVisit.newRecord()
            visitRecord.setValue('event_id', toVariant(eventId))
            visitRecord.setValue('isPrimary', toVariant(visit.IsPrimary))
            visitRecord.setValue('date', toVariant(QtCore.QDate.fromString(visit.Date, QtCore.Qt.ISODate)))
            if sceneId:
                visitRecord.setValue('scene_id', toVariant(sceneId))
            if visitTypeId:
                visitRecord.setValue('visitType_id', toVariant(visitTypeId))
            visitRecord.setValue('person_id', toVariant(personId))
            visitRecord.setValue('service_id', toVariant(serviceId))
            visitRecord.setValue('finance_id', toVariant(financeId))
            db.insertRecord(self.tableVisit, visitRecord)

        for actionData in event.Action:
            personId = self.getPersonIdByCode(actionData.PersonCode)
            orgId = self.getOrgIdByCode(actionData.OrgCode)
            action = actionData.instance
            actionRecord = action.getRecord()
            if not actionRecord:
                actionRecord = self.tableAction.newRecord()
                actionRecord.setValue('actionType_id', toVariant(action.getType().id))
            actionRecord.setValue('status', toVariant(actionData.Status))
            if actionData.BegDate:
                actionRecord.setValue('begDate', toVariant(QtCore.QDate.fromString(actionData.BegDate, QtCore.Qt.ISODate)))
            if actionData.EndDate:
                actionRecord.setValue('endDate', toVariant(QtCore.QDate.fromString(actionData.EndDate, QtCore.Qt.ISODate)))
            actionRecord.setValue('amount', toVariant(actionData.Amount))
            actionRecord.setValue('uet', toVariant(actionData.Uet))
            actionRecord.setValue('MKB', toVariant(actionData.MKB))
            actionRecord.setValue('duration', toVariant(actionData.Duration))
            actionRecord.setValue('person_id', toVariant(personId))
            actionRecord.setValue('org_id', toVariant(orgId))
            action.setRecord(actionRecord)
            # Свойства установлены в методе checkEventData
            action.save(eventId)

        for diagnosticData in event.Diagnosis:
            diagnosticType  = self._cache.diagnosisType.get(diagnosticData.DiagnosticTypeCode, None)
            diagnosticCharacter = self._cache.diseaseCharacter.get(diagnosticData.DiagnosticCharacterCode, None)
            diagnosticStage = self._cache.diseaseStage.get(diagnosticData.DiagnosticStageCode, None)
            diagnosticPhase = self._cache.diseasePhases.get(diagnosticData.DiagnosticPhaseCode, None)
            diagnosticResult = self._cache.diagnosticResult.get(diagnosticData.DiagnosticResultCode, None)

            diagnosisTypeCode = diagnosticType['replace'] if diagnosticType else None
            diagnosisType = self._cache.diagnosisType.get(diagnosisTypeCode, None)
            diagnosisTypeId = diagnosisType['id'] if diagnosisType else None

            diagnosisCharacterCode = diagnosticCharacter['replaceInDiagnosis'] if diagnosticCharacter else None
            diagnosisCharacter = self._cache.diseaseCharacter.get(diagnosisCharacterCode, None)
            diagnosisCharacterId = diagnosisCharacter['id'] if diagnosisCharacter else None

            diagnosticTypeId = diagnosticType['id'] if diagnosticType else None
            diagnosticCharacterId = diagnosticCharacter['id'] if diagnosticCharacter else None
            diagnosticPhaseId = diagnosticPhase['id'] if diagnosticPhase else None
            diagnosticStageId = diagnosticStage['id'] if diagnosticStage else None
            diagnosticResultId = diagnosticResult['id'] if diagnosticResult else None
            personId = self.getPersonIdByCode(diagnosticData.DiagnosticPersonCode)

            diagnosisRecord = self.tableDiagnosis.newRecord()
            diagnosisRecord.setValue('client_id', toVariant(clientId))
            diagnosisRecord.setValue('setDate', toVariant(QtCore.QDate.fromString(diagnosticData.DiagnosticSetDate, QtCore.Qt.ISODate)))
            diagnosisRecord.setValue('endDate', toVariant(QtCore.QDate.fromString(diagnosticData.DiagnosticEndDate, QtCore.Qt.ISODate)))
            diagnosisRecord.setValue('MKB', toVariant(diagnosticData.MKB))
            diagnosisRecord.setValue('diagnosisType_id', toVariant(diagnosisTypeId))
            diagnosisRecord.setValue('character_id', toVariant(diagnosisCharacterId))
            diagnosisRecord.setValue('person_id', toVariant(personId))
            diagnosisId = db.insertRecord('Diagnosis', diagnosisRecord)

            diagnosticRecord = self.tableDiagnostic.newRecord()
            diagnosticRecord.setValue('event_id', toVariant(eventId))
            diagnosticRecord.setValue('diagnosis_id', toVariant(diagnosisId))
            diagnosticRecord.setValue('diagnosisType_id', toVariant(diagnosticTypeId))
            diagnosticRecord.setValue('character_id', toVariant(diagnosticCharacterId))
            diagnosticRecord.setValue('stage_id', toVariant(diagnosticStageId))
            diagnosticRecord.setValue('phase_id', toVariant(diagnosticPhaseId))
            diagnosticRecord.setValue('person_id', toVariant(personId))
            diagnosticRecord.setValue('setDate', toVariant(QtCore.QDate.fromString(diagnosticData.DiagnosticSetDate, QtCore.Qt.ISODate)))
            diagnosticRecord.setValue('endDate', toVariant(QtCore.QDate.fromString(diagnosticData.DiagnosticEndDate, QtCore.Qt.ISODate)))
            diagnosticRecord.setValue('result_id', toVariant(diagnosticResultId))
            diagnosticRecord.setValue('speciality_id', toVariant(self.getSpecialityIdByPersonId(personId)))
            db.insertRecord('Diagnostic', diagnosticRecord)

    def prepareOldEvent(self, eventId):
        db = self.db
        db.deleteRecord(self.tableDiagnostic, 'event_id = %s' % eventId)
        db.deleteRecord(self.tableAction, 'event_id = %s' % eventId)
        db.deleteRecord(self.tableVisit, 'event_id = %s' % eventId)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Import IEMC or Reg Data to to specified database.')
    parser.add_argument('-c', dest='config', type=str, default='reg_iemc',
                        help='name of config file without extension. reg_iemc by default')

    args = vars(parser.parse_args(sys.argv[1:]))

    app = QtCore.QCoreApplication(sys.argv)
    proc = CImportR67XML_VM(args.get('config'))

    #proc._updateRegData = not args['mode']
    proc.startImport()
    proc.closeDatabase()

if __name__ == '__main__':
    main()