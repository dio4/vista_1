# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
#############################################################################


"""
Created on 27/04/15

@author: atronah
"""
import logging
import os
import zipfile

from PyQt4 import QtCore, QtGui
from Accounting.Utils import getContractInfo
from Events.Utils import createDiagnosisRecord
from Exchange.R85.ExchangeEngine import CExchangeImportR85Engine
from library.AgeSelector import parseAgeSelector, checkAgeSelector
from library.ProgressBar import CProgressBar
from library.ProgressInformer import CProgressInformer

from library.Utils import getPref, getClassName, setPref, forceRef, forceDate, forceStringEx, toVariant, \
    forceInt, unformatSNILS, CLogHandler, forceTr, calcAge, MKBwithoutSubclassification, forceBool
from library.XML.XMLHelper import CXMLHelper
from library.database import CDatabase

from Registry.Utils import selectLatestRecord


def importR85MTR(widget, orgId):
    importWindow = CImportDialog(QtGui.qApp.db, orgId)
    params = getPref(QtGui.qApp.preferences.appPrefs, getClassName(importWindow), {})
    importWindow.setParams(params)
    importWindow.engine().setLastExceptionHandler(QtGui.qApp.logCurrentException)
    importWindow.exec_()
    setPref(QtGui.qApp.preferences.appPrefs, getClassName(importWindow), importWindow.params())


#atronah: В идеале должно работать так:
# С помощью "умного" парсера XML пробегаемся первый раз по всему файлу (желательно без полной его загрузки в оперативку),
# проверяем на наличие данных, необходимых для создания счета и элементов и запоминаем их позицию (или ссылки на них).
# Все записи (sluch), не проедшие проверку исключаются из дальнейшего анализа
# (и, возможно, помечаются отказанными либо в файле либо в доп. месте в базе).
# Второй пробег определяет, какие данные необходимо закэшировать (чтобы потом исключить чтение из базы)
# (серии+номера полисов/документов, коды ЛПУ, коды назначений событий и видов помощи и т.п.) ....
# После формируются/обновляются кэши. Третий пробег анализирует данные порционно (например, по ZAP) и, используя кэши,
# формирует порцию данных для записи в базу (записи в несколько этапов, так как потребуется получать id-шки
# и дозаписывать их в другие данные перед их вставкой).

class CImportR85MTREngine(CExchangeImportR85Engine):
    """"Движок" для импорта счетов по программе Межтерриториального обмена фондов.

        Описание формата импорта содержится в приложении
        "Информационное взаимодействие при осуществлении расчетов за медицинскую помощь, оказанную застрахованным лицам
        за пределами субъекта Российской Федерации, на территории которого выдан полис обязательного медицинского
        страхования, в формате XML"
        документа
        "ОБЩИЕ ПРИНЦИПЫ
        построения и функционирования информационных систем
        и порядок информационного взаимодействия
        в сфере обязательного медицинского страхования"
        утвержденного приказом ФОМС от "07" апреля 2011 г. №79 (в редакции приказа ФОМС от "26" декабря 2013 г. №276)

        :param db: экземпляр CDatabase, предоставляющий доступ к базе данных для импорта
        :param orgId: ID текущей организации (Тер.Фонда) для загрузки основных данных по ней.
        :param progressInformer: (опционально) ссылка на объект CProgressInformer для ифнормирования пользователя о прогресе импорта.
        """
    rbCaches = {
        'purpose': {'tagName': 'USL_OK',
                    'tableName': 'rbEventTypePurpose',
                    'key': ('federalCode', 'str'),
                    'value': ('id', 'ref')},
        'aidKind': {'tagName': 'VIDPOM',
                    'tableName': 'rbMedicalAidKind',
                    'key': ('federalCode', 'str'),
                    'value': ('id', 'ref')},
        'result': {'tagName': 'RSLT',
                   'tableName': 'rbResult',
                   'key': ('federalCode', 'str'),
                   'value': ('id', 'ref')},
        # 'speciality': {'tagName': 'PRVS',
        #                'tableName': 'rbSpeciality',
        #                'key': ('federalCode', 'str'),
        #                'value': ('id', 'ref'),
        #                'createIfNotExists': False},
        'aidUnit': {'tagName' : 'IDSP',
                    'tableName': 'rbMedicalAidUnit',
                    'key': ('federalCode', 'str'),
                    'value': ('id', 'ref'),
                    'createIfNotExists': False},
        'diagResult': {'tagName': 'ISHOD',
                       'tableName': 'rbDiagnosticResult',
                       'key': ('federalCode', 'str'),
                       'value': ('id', 'ref')},
        # 'aidUnit': {'tagName': 'IDSP',
        #             'tableName': 'rbMedicalAidUnit',
        #             'key': ('federalCode', 'str'),
        #             'value': ('id', 'ref')},
        'lpu': {'tagName': 'LPU',
                'tableName': 'Organisation',
                'key': ('infisCode', 'str'),
                'value': ('id', 'ref'),
                'createIfNotExists': False}
    }

    def __init__(self, db, orgId, progressInformer = None):
        super(CImportR85MTREngine, self).__init__(progressInformer)
        self._db = db if isinstance(db, CDatabase) else None

        self._orgId = orgId
        self._orgInfis = None
        self._currentOKATO = None
        self._refuseEventTypeId = None # ID типа действия, который используется в случае невозможности определить корректный тип
        self._policyTypeId = None # Тип полиса для всех создаваемых полисов (ОМС)

        self._contractIdByInfis = {}
        self._personIdBySpeciality = {}

        self._insurerCache = {}
        # Справочник именованных кешей, описанных в атрибуте класса .rbCaches
        self._rbCaches = {}
        self._refuseIdCache = {}
        self._refuseIdByFlatCodeCache = {}
        self._mkbCache = {}

        self._eventTypeCache = {}
        self._policyKindIdByCode = {}
        self._specialityCache = {}


        #document-dependent caches:
        self._personCache = {}


    # ---- load\init\clear caches
    def initContractIdInfo(self):
        """Формирует кэш идентификаторов договоров для всех ТФ с учетом года действия.
        Делается выборка по всем договорам, дата окончания которых в этом или в предыдущем году,
        а также, у которых получателем является ТФ (5ти значный инфис код с 3 нулями на конце).
        Результаты выборки (id договоров) помещаются в словарь с ключом (инфис_код, год).

        Если год начала отличается от года окончания договора, то данный договор попадает в словарь столько раз,
        сколько лет охватывает его период действия.
        """
        self.nextPhase(1, u'Загрузка данных по договорам ТФ')
        self._contractIdByInfis.clear()
        tableContract = self._db.table('Contract')
        tableOrganisation = self._db.table('Organisation')
        queryTable = tableContract.innerJoin(tableOrganisation,
                                             tableOrganisation['id'].eq(tableContract['recipient_id']))

        recordList = self._db.getRecordList(table=queryTable,
                                            cols=[tableContract['id'].alias('contractId'),
                                                  tableContract['begDate'].alias('contractBegDate'),
                                                  tableContract['endDate'].alias('contractEndDate'),
                                                  tableOrganisation['infisCode']],
                                            where=[tableContract['deleted'].eq(0),
                                                   'YEAR(%s) >= (YEAR(CURRENT_DATE) - 1)' % tableContract['endDate'],
                                                   tableOrganisation['infisCode'].regexp('^[[:digit:]]{2}0{0,3}$')],
                                            order=tableContract['endDate'])
        self.nextPhase(len(recordList), u'Обработка данных по договорам ТФ')
        for record in recordList:
            sourceInfis = forceStringEx(record.value('infisCode'))[:2]
            begDate = forceDate(record.value('contractBegDate'))
            endDate = forceDate(record.value('contractEndDate'))
            contractId = forceRef(record.value('contractId'))
            for year in xrange(begDate.year(), endDate.year() + 1):
                self._contractIdByInfis[sourceInfis, year] = contractId
        self.finishPhase()


    def loadCurrentFundInfo(self):
        """Загружает информацию о текущем Фонде.

        """
        self.nextPhase(1, u'Получение данных по текущему ТФ')
        tableOrganisation = self._db.table('Organisation')
        record = self._db.getRecord(tableOrganisation,
                                    cols=[tableOrganisation['infisCode'],
                                          tableOrganisation['OKATO']],
                                    itemId=self._orgId)
        self._orgInfis = forceStringEx(record.value('infisCode'))
        if not self._orgInfis:
            self.logger().warning(u'Не удалось получить инфис код текущего ТФ {%s}' % self._orgId)
        self._currentOKATO = self.formatOKATO(record.value('OKATO'), 2)
        self.finishPhase()


    def updateRBCaches(self, doc):
        """
        Добавляет в кэши значения из базы, связанные со значениями в переданном документе doc.
        Анализирует переданный DOM-документ на значение узлов: "", "", "", "", ""
        и подгружает связанные с ними значения в базе в соответствующие кэши.

        :param doc: DOM-документ, который анализируется на предмет кешируемых значений
        """
        for cacheInfo in self.rbCaches.values():
            keyForLoading = []
            cache = cacheInfo.setdefault('cache', {})
            tagName = cacheInfo['tagName']
            tableName = cacheInfo['tableName']
            keyName, keyType = cacheInfo['key']
            valueName, valueType = cacheInfo['value']
            nodeList = doc.elementsByTagName(tagName)
            for elementIdx in xrange(nodeList.length()):
                element = nodeList.item(elementIdx).toElement()
                keyValue = self.convertValue(element.text(), keyType)
                if not cache.has_key(keyValue):
                    keyForLoading.append(keyValue)
            table = self._db.table(tableName)
            cond = [table[keyName].inlist(keyForLoading)]
            recordList = self._db.getRecordList(table,
                                                [table[keyName], table[valueName]],
                                                cond)
            for record in recordList:
                key = self.convertValue(record.value(keyName), keyType)
                value = self.convertValue(record.value(valueName), valueType)
                cache[key] = value


    def updateMKBCache(self, doc):
        """Обновляет содержимое кеша с данными по ограничениям диагнозов.
        Ищет в переданном DOM-документе *doc* значения диагнозов (значения узлов 'DS0', 'DS1', 'DS2', 'DS3') и подгружает
        из базы данных (таблица *MKB*) ограничения по каждому из найденных диагнозов для последующего использования в процессе импорта
        данного документа. Все загруженные данные **добавляются** к уже имеющимся в кеше.

        :param doc: DOM-документ, данные по диагнозам которого необходимо добавить в кеш
        """
        mkbForLoad = []
        for tagName in ['DS0', 'DS1', 'DS2', 'DS3']:
            nodeList = doc.elementsByTagName(tagName)
            for elementIdx in xrange(nodeList.length()):
                mkb = MKBwithoutSubclassification(forceStringEx(nodeList.item(elementIdx).toElement().text()))
                if mkb not in self._mkbCache.keys():
                    mkbForLoad.append(mkb)
        tableMKB = self._db.table('MKB_Tree')
        for record in self._db.getRecordList(tableMKB,
                                             cols=[tableMKB['DiagID'],
                                                   tableMKB['sex'],
                                                   tableMKB['age'],
                                                   tableMKB['OMS'],
                                                   tableMKB['MTR']],
                                             where=[tableMKB['DiagID'].inlist(mkbForLoad)]):
            mkb = forceStringEx(record.value('DiagID'))
            age = forceStringEx(record.value('age'))
            self._mkbCache[mkb] = {'sex' : forceInt(record.value('sex')),
                                   'age' : parseAgeSelector(age) if age else None,
                                   'OMS' : forceBool(record.value('OMS')),
                                   'MTR' : forceBool(record.value('MTR'))}


    def updatePersonCache(self, orgId):
        """Обновляет кеш врачей для указанной организации.
        Ищет всех врачей для указанной организации *orgId* и, группируя их по специальности, заносит в раздел кеша
        по данной организации в виде *ID специальности* = *ID врача*.
        *Прим.: Перед занесением данных раздел кеша указанной организации очищается (но не весь кеш,
        данные по другим организациям не трогаются).*

        :param orgId: Организация, врачей которой необходимо добавить в кеш
        """
        self._personCache.setdefault(orgId, {}).clear()
        tablePerson = self._db.table('Person')
        recordList = self._db.getRecordList(tablePerson,
                                            cols=[tablePerson['id'],
                                                  tablePerson['speciality_id']],
                                            where=[tablePerson['org_id'].eq(orgId)],
                                            group='speciality_id')
        for record in recordList:
            self._personCache[orgId][forceRef(record.value('speciality_id'))] = forceRef(record.value('id'))

    def updateSpecialityCache(self):
        """Обновляет кэш специальностей.

        @return:
        """

        # TODO: сделать по аналогии с кэшэм МКБ - тянуть только те специальности, которые встречаются в документе
        self._specialityCache.clear()
        self._specialityCache.setdefault(u'v015', {})
        self._specialityCache.setdefault(u'v004', {})
        tableSpeciality = self._db.table('rbSpeciality')
        recordList = self._db.getRecordList(tableSpeciality,
                                            cols=[tableSpeciality['id'],
                                                  tableSpeciality['federalCode'],
                                                  tableSpeciality['versSpec']])
        for record in recordList:
            versSpec = forceStringEx(record.value('versSpec')).lower()
            # По умолчанию у нас везде используется V015. V004 является исключением от одного-двух регионов.
            if not versSpec: versSpec = u'v015'
            self._specialityCache[versSpec][forceInt(record.value('federalCode'))] = forceRef(record.value('id'))

    def preloadInsurerCache(self):
        """Предварительная загрузка данных по Страховым компаниям.
        Формирует (обновляет) кэш страховых элементами вида *"Инфис код страховой"* = *ID страховой*


        """
        tableInsurer = self._db.table('Organisation')
        self._insurerCache.update([(forceStringEx(record.value('infisCode')), forceRef(record.value('id')))
                                   for record in self._db.getRecordList(tableInsurer,
                                                                        cols=[tableInsurer['id'],
                                                                              tableInsurer['infisCode']],
                                                                        where=[tableInsurer['isInsurer'].eq(1)],
                                                                        # limit=1000,
                                                                        group='infisCode')
                                   ])



    def clearDocumentCache(self):
        """Очищает кеши, данные которых относятся к конкретному импортируемому документу.
        Производит очистку кешей, данные в которых будут не актуальны для других импортов.

        """
        for orgPersonCache in self._personCache.values():
            orgPersonCache.clear()
        self._personCache.clear()


    def clearAll(self):
        """Очищает все временные хранилища данных.
        """
        self._contractIdByInfis.clear()

        for cacheInfo in self.rbCaches.values():
            cacheInfo.get('cache', {}).clear()
        self._mkbCache.clear()

        self._refuseIdCache.clear()
        self._refuseIdByFlatCodeCache.clear()
        self._policyKindIdByCode.clear()

        self._insurerCache.clear()

        self.clearDocumentCache()

        self._policyTypeId = None
        self._refuseEventTypeId = None


    # ---- checkers
    def checkMKB(self, mkb, patientInfo, checkData, mekErrorList):
        """Проверяет соответствие переданного диагноза *mkb* органичениям, описанным в базе данных.
        Проверяет, является ли переданный диагноз подходящим для ОМС и МТР, а так же сверяет, подходит ли он для
        переданного пациента *patientInfo*. В случае успеха всех проверок возвращает истину, в случае обнаружения проблем
        возвращает False и добавляет в mekErrorList данные по найденным ошибкам.

        :param mkb: Проверяемый диагноз в виде строки с кодом МКБ-10
        :param patientInfo: Информация о пациенте, необходимая для проверки (словарь с ключами "sex" (числовое обозначение пола)
        и "birthDate" (QDate() с датой рождения))
        :param checkData: дата проверки для корректного определения возраста пациента.
        :param mekErrorList: список для внесения в него данных о найденных ошибках в формате кортежа
        (код ошибки МЭК, Описание ошибки МЭК, Имя узла документа с ошибочным узлом, Имя узла с ошибкой)
        :return: True, если ошибок выявленно не было, иначе False
        """
        mkbInfo = self._mkbCache.get(MKBwithoutSubclassification(mkb), None)

        if not (mkbInfo
                and mkbInfo['MTR']
                and mkbInfo['OMS']):
            mekErrorList.append((u'5.3.3', u'Включение в реестр счетов случаев, не входящих в терр. программу ОМС', None, None))
            return False
        if mkbInfo['sex'] and patientInfo['sex'] != mkbInfo['sex'] \
                or mkbInfo['age'] and not checkAgeSelector(mkbInfo['age'], calcAge(patientInfo['birthDate'], checkData)):
            mekErrorList.append((u'5.1.4', u'Некорректное заполнение полей реестра счетов', 'PATIENT', 'DR' if patientInfo['sex'] == mkbInfo['sex'] else 'W'))
            return False

        return True


    # ---- getters

    def getContractId(self, infisCode, year):
        """Возвращает ID договора, используемого для импорта по территории с указанным инфос кодом и на указанный год.
        Обрезает указанный инфис код до первых двух символов и ищет в кеше ID договора для такого инфис и года.

        :param infisCode: инфис территории, по которой производится импорт.
        :param year: год импорта.
        :return: ID договора, используемого для импорта указанной территории.
        """
        infisCode = forceStringEx(infisCode)[:2]
        contractId = self._contractIdByInfis.get((infisCode, year), None)
        if not contractId:
            self.logger().warning(u'Не удалось найти договор для импорта данных по территории с инфис "%s"' % infisCode)

        return contractId


    def getRefuseEventTypeId(self):
        """Возвращает резервного ID типа события, используемого для создания отказных обращений, корректный тип для которых не удалось определить.

        :return: ID типа события для создания отказного обращения.
        """
        if not self._refuseEventTypeId:
            refuseEventTypeCode = u'mtrRefuse'
            tableEventType = self._db.table('EventType')
            self._refuseEventTypeId = forceRef(self._db.translate(tableEventType, 'code', refuseEventTypeCode, 'id'))

            if not self._refuseEventTypeId:
                record = tableEventType.newRecord()
                record.setValue('code', toVariant(refuseEventTypeCode))
                record.setValue('name', toVariant(u'Авто:Неизвестный тип события'))
                self._refuseEventTypeId = self._db.insertRecord(tableEventType, record)

        return self._refuseEventTypeId


    def getEventTypeId(self, purposeId, aidKindId, mekErrorList):
        """Возвращает ID типа события для указанных назначения и вида мед. помощи.

        :param purposeId: ID назначения обращения (rbEventTypePurpose).
        :param aidKindId: ID вида мед. помощи (rbMedicalAidKond)
        :param mekErrorList: список для занесения ошибок по определения типа события.
        :return: ID типа события по указанным критериям.
        """
        if not self._eventTypeCache.has_key((purposeId, aidKindId)):
            table = self._db.table('EventType')
            cond = [table['purpose_id'].eq(purposeId),
                    table['medicalAidKind_id'].eq(aidKindId)]
            record = self._db.getRecordEx(table, 'id', cond)

            eventTypeId = None
            if record:
                eventTypeId = forceRef(record.value('id'))
                self._eventTypeCache[(purposeId, aidKindId)] = eventTypeId
            # elif purposeId and aidKindId:
            #     record = table.newRecord()
            #     record.setValue('purpose_id', toVariant(purposeId))
            #     record.setValue('medicalAidKind_id', toVariant(aidKindId))
            #     record.setValue('name', toVariant(u'Авто:{%s,%s}' % (purposeId, aidKindId)))
            #     eventTypeId = self._db.insertRecord(table, record)
            # else:
            #     message = u'Пустые значения идентификаторов назначения обращения и/или вида мед.помощи'
            #     self.logger().critical(message)
            #     eventTypeId = None

            if eventTypeId:
                self._eventTypeCache[(purposeId, aidKindId)] = eventTypeId
            else:
                # mekErrorList.append((u'1.1.1', u'Пустые значения идентификаторов назначения обращения и/или вида мед.помощи', None, None))
                return self.getRefuseEventTypeId()

        return self._eventTypeCache.get((purposeId, aidKindId), None)


    def getCachedRBValue(self, cacheName, keyValue):
        """
        Попытка получить данные для указанных кэша (cacheName) и ключа (keyValue). Либо создать их в базе при отсутствии.
        Для указанного имени кэша и значения ключа производится поиск значения сначала в кэше, потом в базе.
        Если значение не было найдено, то оно создается в базе и добавляется в кэш

        :param cacheName: имя кэша, в котором будет произведен поиск значения
        :param keyValue: значение ключа, по которому будет произведен поиск данных в кэше
        :return: :raise Exception: ошибка в случае невозможности создать новое непустое значение в базе
        """
        cacheInfo = self.rbCaches[cacheName]
        cache = cacheInfo['cache']

        if not cache.has_key(keyValue):
            keyName, keyType = cacheInfo['key']
            keyValue = self.convertValue(keyValue, keyType)
            valueName, valueType = cacheInfo['value']
            table = self._db.table(cacheInfo['tableName'])
            resultValue = self._db.translate(table, keyName, keyValue, valueName)
            if resultValue is None and cacheInfo.get('createIfNotExists', True):
                record = table.newRecord()
                record.setValue(keyName, toVariant(keyValue))
                record.setValue(valueName, toVariant(cacheInfo.get('defaultValue', None))) #Заполнение значением по умолчанию поля базы, из которого требуется брать значение в дальнейшем
                if record.contains('name'):
                    record.setValue('name', toVariant(u'Авто:%s:%s' % (cacheInfo['tagName'], keyValue)))
                recordId = forceRef(self._db.insertRecord(table, record))
                resultValue = self._db.translate(table, table.idField(), recordId, valueName)
            if resultValue is None:
                message = u'Не удалось получить/сформировать значение для справочника %s по ключу %s=%s (%s)' % (cacheInfo['tableName'], keyName, keyValue, cacheInfo['tagName'])
                self.logger().warning(message)
                return None
            cache[keyValue] = self.convertValue(resultValue, valueType)

        return cache[keyValue]


    def getPayRefuseId(self, code):
        """Возвращает ID причины отказа {rbPayRefuseType}, соответсвующей указанному коду.
        Ищет в кеше или базе данных ID причины отказа, код которой соответствует указанному в *code*,
        после чего возвращает и кеширует это значение.
        Поиск производится по полю rbPayRefuseType.code.

        :param code: код отказа.
        :return: ID причины отказа {rbPayRefuseType}
        """
        if not code.endswith('.'):
            code += '.'
        if not self._refuseIdCache.has_key(code):
            refuseId = forceRef(self._db.translate('rbPayRefuseType', 'code', code, 'id'))
            self._refuseIdCache[code] = refuseId
        return self._refuseIdCache[code]

    def getPayRefuseIdByFlatCode(self, flatCode):
        """Возвращает ID причины отказа {rbPayRefuseType}, соответсвующей указанному коду.
        Ищет в кеше или базе данных ID причины отказа, код которой соответствует указанному в *flatCode*,
        после чего возвращает и кеширует это значение.
        Поиск производится по полю rbPayRefuseType.flatCode.

        :param flatCode: код отказа.
        :return: ID причины отказа {rbPayRefuseType}
        """
        if not self._refuseIdByFlatCodeCache.has_key(flatCode):
            refuseId = forceRef(self._db.translate('rbPayRefuseType', 'code', flatCode, 'id'))
            self._refuseIdByFlatCodeCache[flatCode] = refuseId
        return self._refuseIdByFlatCodeCache[flatCode]


    def getPolicyKindByCode(self, code):
        """Возвращает ID вида полиса {rbPolicyKind}, соответствующего коду *code*
        Ищет в кеше или базе данных ID причины отказа, код которой соответствует указанному в *code*,
        после чего возвращает и кеширует это значение.
        Поиск производится по полю rbPolicyKind.federalCode.

        :param code: код вида полиса.
        :return: ID вида полиса {rbPolicyKind}
        """
        if not self._policyKindIdByCode.has_key(code):
            self._policyKindIdByCode[code] = forceRef(self._db.translate('rbPolicyKind', 'federalCode', code, 'id'))
        return self._policyKindIdByCode[code]


    def getPersonId(self, orgId, specialityCode, versSpec):
        """Возвращает ID врача с указанной специальностью *specialityCode* и организацией *orgId*.
        При необходимости создает его в базе и кеширует данные.

        :param orgId: ID ЛПУ, врач для которой ищется в базе
        :param specialityCode: код специальности искомого врача
        :return: ID врача
        """
        if not versSpec:
            versSpec = u'v004'
        specialityId = self._specialityCache.get(versSpec, {}).get(specialityCode, None)
        if specialityId:
            if orgId not in self._personCache.keys():
                self.updatePersonCache(orgId)
            orgPersonCache = self._personCache[orgId]
            if not orgPersonCache.has_key(specialityId):
                tablePerson = self._db.table('Person')
                specialityName = self._db.translate('rbSpeciality', 'id', specialityId, 'name')
                record = tablePerson.newRecord()
                record.setValue('code', toVariant(specialityCode))
                record.setValue('federalCode', toVariant(specialityCode))
                record.setValue('speciality_id', toVariant(specialityId))
                record.setValue('lastName', specialityName)
                record.setValue('org_id', toVariant(orgId))
                orgPersonCache[specialityId] = self._db.insertRecord(tablePerson, record)

            result = orgPersonCache.get(specialityId, None)
        else:
            result = None
        if not result:
            self.logger().warning(u'Не удалось получить ID врача по указанным ID ЛПУ {%s} и коду специальности {%s}' % (orgId, specialityCode))
        return result

    # ---- processing


    def process(self, fileName):
        """Запускает процесс импорта.

        :param fileName: имя файла для импорта
        :return: True
        """
        self.isAbort = False
        self.phaseReset(4)
        self.initContractIdInfo()
        self.loadCurrentFundInfo()
        self.preloadInsurerCache()
        self._policyTypeId = forceRef(self._db.translate('rbPolicyType', 'code', '1', 'id'))
        self.processFile(fileName)
        return True


    def parseFileName(self, fileName):
        """
        Вычленяет из имени файла важную информацию.
        Предполагается, что имя файла представлено в формате:
            R + код территориального фонда обязательного медицинского страхования, выставившего счет
            + код территориального фонда обязательного медицинского страхования, которому предъявлен счет
            + две последние цифры года
            + четырехзначный порядковый номер представления основной части в текущем году
        :param fileName: имя обрабатываемого файла
        :return: isOk, isUpdate, sourceInfis, destInfis, year, number
        """
        try:
            name = os.path.splitext(os.path.basename(fileName))[0].lower()
            if name[0] in ['r', 'd'] and len(name) == 11:
                return True, name.startswith('d'), forceStringEx(name[1:3]), forceStringEx(name[3:5]), 2000 + int(name[5:7], 10), int(name[7:11], 10)
        except Exception, e:
            self.logger().critical(u'Некорректное имя файла "%s" (%s)' % (fileName, e.message))
            self.onException()

        return False, False, u'', u'', None, None


    def processFile(self, fileName):
        """Импортирует указанный файл

        :param fileName: имя файла для импорта (R|D)<SS><DD><YY><NNNN>.(oms|xml) (описание имени см в `parseFileName`)
        :return: True, если импорт файла прошел успешно, False в ином случа
        :raise: Exception("архив пуст"), если архив пуст
        """
        docFile = None
        try:
            isOk, isUpdateFile, sourceInfis, destInfis, year, number = self.parseFileName(fileName)
            if destInfis[:2] != self._orgInfis[:2]:
                self.logger().info(u'Пропуск обработки файла "%s": территория назначения (%s) не соответствует текущей (%s)' % (fileName, destInfis, self._orgInfis))
                return False

            if zipfile.is_zipfile(fileName):
                zipFile = zipfile.ZipFile(fileName, 'r')
                zipItems = zipFile.namelist()
                if not zipItems:
                    raise Exception(u'zip-архив "%s" пуст' % fileName)
                docFile = zipFile.open(zipItems[0])
            else:
                docFile = open(fileName, 'r')

            self.processDocument(CXMLHelper.loadDocument(QtCore.QString(docFile.read().decode(self.encoding))),
                                 sourceInfis,
                                 year,
                                 isUpdateFile)


        except Exception, e:
            self.logger().warning(u'Не удалось импортировать файл "%s" (%s)' % (fileName, e.message))
            self.onException()
            return False
        finally:
            if docFile:
                docFile.close()

        return True


    def processDocument(self, document, sourceInfis, year, isUpdateFile):
        """Анализирует и импортирует DOM-документ.

        :param document: документ, подлежащий анализу и импорту (QDomDocuement)
        :param sourceInfis: инфис тер. фонда, предоставившего данные
        :param year: год формирования данного документа
        :param isUpdateFile: пометка о том, что документ является измененной версией ранее загруженного
        :return: True в случае успеха и False в ином случае
        """
        self.nextPhase(document.elementsByTagName('SLUCH').length(), u'Обработка файла')
        self.clearDocumentCache()
        self.updateRBCaches(document)
        self.updateMKBCache(document)
        self.updateSpecialityCache()

        rootElement = self.getElement(document, 'ZL_LIST', isRequired=True)
        if not rootElement:
            return False

        headerElement = self.getElement(rootElement, 'ZGLV', isRequired=True)
        if not headerElement:
            return False


        if not self.parseHeaderElement(headerElement, sourceInfis):
            return False

        self._db.transaction(checkIsInit=True)
        try:
            accInfo = {'isUpdate' : isUpdateFile}
            accountElement = self.getElement(rootElement, 'SCHET', isRequired=True)
            self.processAccountElement(accountElement, sourceInfis, year, accInfo)

            entityElement = accountElement.nextSiblingElement('ZAP')
            while not entityElement.isNull():
                self.processEntity(entityElement, accInfo)
                entityElement = entityElement.nextSiblingElement('ZAP')

            self._db.commit()
        except Exception, e:
            self._db.rollback()
            raise
        finally:
            self.finishPhase()

        return True


    def parseHeaderElement(self, headerElement, sourceInfis):
        """Анализирует заголовочный узел импортируемого документа.
        Производит проверку ОКАТО фондов отправления и назначения.

        :param headerElement: DOM-узел заголовочных данных (<ZGLV>).
        :param sourceInfis: не используется
        :return: True в случае успеха и False в ином случае
        """
        targetOKATO = self.formatOKATO(self.getElementValue(headerElement,
                                                            'OKATO_OMS',
                                                            isRequired=True),
                                       2)
        if targetOKATO != self._currentOKATO:
            self.logger().warning(u'Целевой ОКАТО (OKATO_OMS) {%s} файла не соответствует ОКАТО текущего ТФ {%s}' % (targetOKATO, self._currentOKATO))
            #TODO: atronah: надо ли делать отказ в таком случае или просто не импортировать счет? Если отказ, то надо ли создавать счет под него или писать инфу об отказе в файл (еще куда-то)
            # mekErrorList.append(('5.1.1', u'Ошибки в реквизитах при оформлении и предъявлении счетов', forceStringEx(headerElement.nodeName()), 'OKATO_OMS'))
            return False

        # sourceOKATO = self.formatOKATO(self.getElementValue(headerElement, 'C_OKATO1', isRequired=True, mekErrorList=mekErrorList))
        return True


    def processAccountElement(self, accountElement, sourceInfis, year, accInfo):
        """Обрабатывает узел с описанием импортируемого счета.

        :param accountElement: узел с описанием импортируемого счета.
        :param sourceInfis: инфис код фонда, приславшего данные
        :param year: год счета
        :param accInfo: словарь для сохранения некоторых данных по счету.
        :return: результат обработки (True или False)
        :raise Exception:
        """
        contractId = self.getContractId(sourceInfis, year)
        if not contractId:
            return False

        mekErrorList = []

        accNumber = self.getElementValue(accountElement, 'NSCHET', isRequired=True, mekErrorList=mekErrorList)
        accExposeDateString = self.getElementValue(accountElement, 'DSCHET', isRequired=True, mekErrorList=mekErrorList)
        accExposeDate = self.convertValue(accExposeDateString, 'date')

        accInfo.setdefault('mekErrorList', []).extend(mekErrorList)

        isUpdate = accInfo.get('isUpdate', False)

        tableAccount = self._db.table('Account')
        cond = ['YEAR(%s) = %s' % (tableAccount['settleDate'], year)]
        if isUpdate:
            cond += [tableAccount['number'].like(accNumber + u'/п%'),
                    ]
        else:
            cond += [tableAccount['number'].like(accNumber),
                    tableAccount['exposeDate'].eq(accExposeDate),
                    ]
        #TODO: atronah: такое определение повторного счета норм?
        record = self._db.getRecordEx(tableAccount,
                                      cols='*',
                                      where=cond,
                                      order='id DESC')
        previous = 0
        if record:
            if isUpdate:
                old_number = forceStringEx(record.value('number'))
                parts = old_number.split(u'/п')
                if len(parts) > 1:
                    previous = forceInt(parts[-1])
            else:
                if self.getUserConfirmation(u'Подтвердите удаление',
                                            u'Данный счет (%s от %s) уже был загружен ранее.\n'
                                            u'Удалить ранее загруженный счет?' % (accNumber, accExposeDateString)):
                    self._db.deleteRecord(tableAccount, tableAccount['id'].eq(forceRef(record.value('id'))))
                else:
                    raise Exception(u'Обработка счета %s от %s отменена пользователем' % (accNumber, accExposeDateString))

        contractInfo = getContractInfo(contractId)

        postfix = ''
        if isUpdate:
            postfix = u'/п{0}'.format(previous+1)

        record = tableAccount.newRecord()
        record.setValue('number', toVariant(accNumber + postfix))
        record.setValue('exposeDate', toVariant(accExposeDate))
        settleMonth = self.getElementValue(accountElement, 'MONTH', typeName='int', isRequired=True, mekErrorList=mekErrorList)
        record.setValue('settleDate', toVariant(QtCore.QDate(year, settleMonth, 1)))
        record.setValue('date', toVariant(accExposeDate))
        record.setValue('amount', toVariant(self.dummyN))
        exposeTotal = self.getElementValue(accountElement, 'SUMMAV', typeName='double', isRequired=True, mekErrorList=mekErrorList)
        record.setValue('sum', toVariant(exposeTotal))
        record.setValue('contract_id', toVariant(contractId))
        record.setValue('payer_id', toVariant(contractInfo.payer_id))
        self._db.insertRecord('Account', record)


        accInfo['record'] = record
        accInfo['contractInfo'] = contractInfo
        accInfo['entities'] = {}

        return True


    def processEntity(self, entityElement, accInfo):
        """Обрабывает узел с данными о случаях обращения конкретного пациента.

        :param entityElement: узел с данными о случаях обращения конкретного пациента (<ZAP>).
        :param accInfo: словарь с данными по обрабатываемому счету
        :return: результат обработки (True или False)
        :raise Exception:
        """
        entityKey = self.getElementValue(entityElement, 'N_ZAP', isRequired=True)
        if not entityKey:
            return False

        # entityInfo = accInfo['entities'].setdefault(entityKey, {})
        self._db.transaction()
        try:
            MEKErrorList = []
            patientElement = self.getElement(entityElement, 'PACIENT', isRequired=True, mekErrorList=MEKErrorList)
            patientInfo = self.processPatient(patientElement, MEKErrorList)
            patientId = patientInfo.get('id', None)
            if not patientId:
                raise Exception(' '.join(MEKErrorList[-1][:2]) if MEKErrorList else u'Проблема идентификации пациента')
            eventElement = patientElement.nextSiblingElement('SLUCH')
            processedEventKeys = []
            while not eventElement.isNull():
                eventKey = self.getElementValue(eventElement, 'IDCASE', isRequired=True, mekErrorList=MEKErrorList)
                if eventKey and eventKey not in processedEventKeys:
                    self.processEvent(eventElement, patientInfo, accInfo, MEKErrorList)
                    processedEventKeys.append(eventKey)
                eventElement = eventElement.nextSiblingElement('SLUCH')
                self.nextPhaseStep()
            self._db.commit()
        except Exception, e:
            self._db.rollback()
            self.onException()
            self.logger().warning(u'Не удалось обработать запись N_ZAP=%s (%s)' % (entityKey, e.message))
            return False
        if self.isAbort:
            raise Exception(u'Прервано пользователем')
        return True


    def processEvent(self, eventElement, patientInfo, accInfo, entityMekErrorList):

        # TODO: craz: поиск существующих записей.
        # TODO: craz: проработать логику внешних идентификаторов (какие используем, где храним)

        eventKey = self.getElementValue(eventElement, 'IDCASE')
        patientId = patientInfo['id']

        tableEvent = self._db.table('Event')
        tableAccountItem = self._db.table('Account_Item')

        self._db.transaction()
        try:
            mekErrorList = entityMekErrorList[:] #скопировать уже имеющиеся ошибки по записи.
            diagnosticResultCode = self.getElementValue(eventElement, 'ISHOD', isRequired=True, mekErrorList=mekErrorList)
            purposeCode = self.getElementValue(eventElement, 'USL_OK', isRequired=True, mekErrorList=mekErrorList)
            purposeId = self.getCachedRBValue('purpose', purposeCode) # self._purposeCache.get(purposeCode, None)

            # if purposeId is None:
            #     self.logger().info(u'Не удалось найти назначение обращения с кодом "%s" для случая с IDCASE = %s' % (purposeCode, eventKey))
            #     return False

            aidKindCode = self.getElementValue(eventElement, 'VIDPOM', isRequired=True, mekErrorList=mekErrorList)
            aidKindId = self.getCachedRBValue('aidKind', aidKindCode) #self._aidKindCache.get(aidKindCode, None)

            eventTypeId = self.getEventTypeId(purposeId, aidKindId, mekErrorList)
            if eventTypeId is None:
                raise Exception(u'Не удалось определить тип обращения для IDCASE = %s' % eventKey)

            lpuId = self.getCachedRBValue('lpu', self.getElementValue(eventElement, 'LPU', isRequired=True, mekErrorList=mekErrorList))#self._lpuCache.get(self.getElementValue(eventElement, 'LPU', isRequired=True, mekErrorList=mekErrorList), None)
            if lpuId is None:
                lpuId = accInfo['contractInfo'].recipient_id
            resultId = self.getCachedRBValue('result', self.getElementValue(eventElement, 'RSLT', isRequired=True, mekErrorList=mekErrorList)) #self._resultCache.get(self.getElementValue(eventElement, 'RSLT', isRequired=True, mekErrorList=mekErrorList), None)

            contractId = forceRef(accInfo['record'].value('contract_id'))

            eventSetDate = self.getElementValue(eventElement, 'DATE_1', typeName='date',
                                                isRequired=True, mekErrorList=mekErrorList)
            eventExecDate = self.getElementValue(eventElement, 'DATE_2', typeName='date',
                                                 isRequired=True, mekErrorList=mekErrorList)
            eventExecPersonId = self.getPersonId(lpuId,
                                                 self.getElementValue(eventElement, 'PRVS', typeName='int', isRequired=True, mekErrorList=mekErrorList),
                                                 self.getElementValue(eventElement, 'VERS_SPEC', typeName='str', isRequired=False, mekErrorList=mekErrorList))

            externalId = self.getElementValue(eventElement, 'NHISTORY',
                                              isRequired=True, mekErrorList=mekErrorList)

            isUpdate = accInfo.get('isUpdate', False)
            accountId = forceRef(accInfo['record'].value('id'))
            eventRecord = self._db.getRecordEx(tableEvent, cols=tableEvent['id'], where=[tableEvent['externalId'].like('%#' + externalId + '%'),
                                                                                         tableEvent['client_id'].eq(patientId),
                                                                                         tableEvent['org_id'].eq(lpuId),
                                                                                         tableEvent['eventType_id'].eq(eventTypeId),
                                                                                         tableEvent['setDate'].eq(eventSetDate),
                                                                                         tableEvent['execDate'].eq(eventExecDate)])



            if eventRecord:
                accountIdList = self._db.getIdList(tableAccountItem,
                                      idCol='master_id',
                                      where=[tableAccountItem['event_id'].eq(eventRecord.value('id'))])
                #Если найденное обращение находится в другом счете,
                if accountIdList:
                    if accountId in accountIdList:
                        self.logger().warning(u'Случай IDCASE=%s уже был импортирован в текущий счет' % eventKey)
                    # то создать новое и пометить счет по нему отказанным
                    eventRecord = None
                    mekErrorList.append((u'5.7.1', u'Повторное выставление счета за уже оплаченную МП', None, None))
                else:
                    if not isUpdate:
                        self._db.deleteRecord(tableEvent, tableEvent['id'].eq(eventRecord.value('id')))
                    # На каждый импорт все равно создаем новое обращение. Старое, при этом, может быть удалено.
                    eventRecord = None

            if not eventRecord:
                eventRecord = tableEvent.newRecord()
                littleStranger = patientInfo['littleStranger']
                if littleStranger:
                    tableLittleStranger = self._db.table('Event_LittleStranger')
                    lsRecord = tableLittleStranger.newRecord()
                    lsRecord.setValue('sex', toVariant(forceInt(littleStranger[0])))
                    year = 2000 + forceInt(littleStranger[5:7])
                    month = forceInt(littleStranger[3:5])
                    day = forceInt(littleStranger[1:3])
                    lsRecord.setValue('birthDate', toVariant(QtCore.QDate(year, month, day)))
                    lsRecord.setValue('currentNumber', toVariant(forceInt(littleStranger[7])))
                    lsId = self._db.insertRecord(tableLittleStranger, lsRecord)
                    eventRecord.setValue('littleStranger_id', toVariant(lsId))


            partsExternalId = externalId.strip().split('#')
            if len(partsExternalId) == 0:
                partsExternalId = [""] * 3
            if len(partsExternalId) == 1:
                partsExternalId.extend([""] * 2)
            partsExternalId[0] = externalId
            partsExternalId[2] = eventKey

            eventRecord.setValue('client_id', toVariant(patientId))
            eventRecord.setValue('contract_id', contractId)
            eventRecord.setValue('eventType_id', toVariant(eventTypeId))
            eventRecord.setValue('setDate', toVariant(eventSetDate))
            eventRecord.setValue('execDate', toVariant(eventExecDate))
            eventRecord.setValue('org_id', toVariant(lpuId))
            eventRecord.setValue('isPrimary', toVariant(1))
            eventRecord.setValue('externalId', toVariant("#".join([forceStringEx(part) for part in partsExternalId])))
            eventRecord.setValue('order', toVariant({
                                           3: 1,    # Плановая
                                           1: 2,    # Экстренная
                                           2: 6,    # Неотложная
                                           }.get(self.getElementValue(eventElement, 'FOR_POM', typeName='int', isRequired=True, mekErrorList=mekErrorList), 1)))
            if resultId:
                eventRecord.setValue('result_id', toVariant(resultId))
            eventRecord.setValue('pregnancyWeek', toVariant(0))
            eventRecord.setValue('totalCost', toVariant(0))
            eventRecord.setValue('execPerson_id', toVariant(eventExecPersonId))
            eventId = self._db.insertOrUpdate(tableEvent, eventRecord)

            #Обработка диагнозов
            #Возможно стоит использовать Events.Utils.getDiagnosisId2, но там жесткая завязка на QtGui.qApp.db и "больная" логика
            PRIMARY_DIAGTYPE_CODE = '2' # основной диагноз
            SECONDARY_DIAGTYPE_CODE = '9' # сопутствующий диагноз
            ADVERSE_DIAGTYPE_CODE = '3' # осложнение основного


            #TODO: craz: process other DS* tags, VNOV_M, CODE_MES*
            #TODO: craz: process ED_COL
            # FIXME: craz: client_id - обязательное поля для Diagnosis. При этом для обращения все не так критично. Поэтому проверяем пока что только здесь, а обращение и Account_Item с ошибкой все равно создаем.
            if patientId:
                tableDiagnostic = self._db.table('Diagnostic')
                # tableDiagnosis = self._db.table('Diagnosis')
                # queryTable = tableDiagnostic.innerJoin(tableDiagnosis,
                #                                        tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']))
                self._db.deleteRecord(tableDiagnostic,tableDiagnostic['event_id'].eq(eventId))
                for tagName, typeCode, isRequired in [('DS1', PRIMARY_DIAGTYPE_CODE, True),
                                                      ('DS2', SECONDARY_DIAGTYPE_CODE, False),
                                                      ('DS3', ADVERSE_DIAGTYPE_CODE, False)]:
                    diagElement = self.getElement(eventElement, tagName, isRequired=isRequired, mekErrorList=mekErrorList)
                    if not diagElement.isNull():
                        MKB = forceStringEx(diagElement.text())
                        self.checkMKB(MKB, patientInfo, eventExecDate, mekErrorList)
                        diagnosisId = createDiagnosisRecord(patientId, typeCode, None, MKB, '', None, None, eventSetDate, eventExecDate, eventExecPersonId, '', '')
                        diagnosticRecord = tableDiagnostic.newRecord()
                        if diagnosisId:
                            diagnosticRecord.setValue('event_id', toVariant(eventId))
                            diagnosticRecord.setValue('diagnosis_id', toVariant(diagnosisId))
                            diagnosticRecord.setValue('sanatorium', toVariant(0))
                            diagnosticRecord.setValue('hospital', toVariant(0))
                            diagnosticRecord.setValue('setDatetime', toVariant(eventSetDate))
                            diagnosticRecord.setValue('diagnosisType_id', toVariant(self._db.translate('rbDiagnosisType', 'code', typeCode, 'id')))
                            diagnosticResultId = self.getCachedRBValue('diagResult',
                                                                       diagnosticResultCode)
                            diagnosticRecord.setValue('result_id', toVariant(diagnosticResultId))
                            self._db.insertRecord(tableDiagnostic, diagnosticRecord)



            #Обработка услуг
            profileCode = self.getElementValue(eventElement, 'PROFIL', isRequired=True, mekErrorList=mekErrorList)
            tableService = self._db.table('rbService')
            serviceId = forceRef(self._db.translate(tableService, tableService['code'], profileCode, tableService['id']))
            if not serviceId:
                mekErrorList.append((u'5.1.4',
                                     u'Некорректное заполнение полей реестра счетов',
                                     forceStringEx(eventElement.nodeName()),
                                     'PROFIL'))


            # TODO: craz: обработка диагнозов и услуг
            sank = eventElement.firstChildElement('SANK')
            refReason = None
            if sank and not sank.isNull():
                refReason = self.getElementValue(sank, 'S_OSN')#forceStringEx(sank.firstChildElement('S_OSN').text())
            # refReason = forceString(sluch.firstChildElement('REFREASON').text())
            oplata = self.getElementValue(eventElement, 'OPLATA', typeName='n')

            aiRecord = tableAccountItem.newRecord()
            aiRecord.setValue('master_id', toVariant(accountId))
            aiRecord.setValue('event_id', toVariant(eventId))
            aiRecord.setValue('price', toVariant(self.getElementValue(eventElement, 'TARIF', typeName='double')))
            unitCode = self.getElementValue(eventElement, 'IDSP', isRequired=True, mekErrorList=mekErrorList)
            aiRecord.setValue('unit_id', toVariant(self.getCachedRBValue('aidUnit', unitCode)))
            aiRecord.setValue('amount', toVariant(1))
            aiRecord.setValue('sum', toVariant(self.getElementValue(eventElement, 'SUMV', typeName='double', isRequired=True, mekErrorList=mekErrorList)))
            aiRecord.setValue('service_id', toVariant(serviceId))
            aiRecord.setValue('date', toVariant(QtCore.QDate.currentDate()))
            if mekErrorList:
                aiRecord.setValue('number', toVariant(u'Отказ по МЭК'))
                aiRecord.setValue('refuseType_id', toVariant(self.getPayRefuseId(mekErrorList[0][0])))
            elif oplata > 1 and refReason:
                refuseTypeId = self.getPayRefuseIdByFlatCode(refReason)
                aiRecord.setValue('refuseType_id', toVariant(refuseTypeId))
                aiRecord.setValue('number', toVariant(u'Отказ'))
            else:
                aiRecord.setValue('number', toVariant(u'Оплачено'))
            aiId = self._db.insertRecord(tableAccountItem, aiRecord)
            self._db.commit()
        except:
            self._db.rollback()
            raise

        return True


    #TODO: craz: process OKATO_* and NOVOR tags

    def processPatient(self, patientElement, mekErrorList):
        patientInfo = {}
        #TODO: atronah: обработка новорожденных
        tableClient = self._db.table('Client')
        # tableClientPolicy = self._db.table('ClientPolicy')
        # tableClientDocument = self._db.table('ClientDocument')
        cols = [tableClient['id'],
                tableClient['lastName'],
                tableClient['firstName'],
                tableClient['patrName'],
                tableClient['sex'],
                tableClient['birthDate'],
                tableClient['birthPlace'],
                tableClient['SNILS'],
                ]

        novor = self.getElementValue(patientElement, 'NOVOR', isRequired=True, mekErrorList=mekErrorList)
        if novor == '0':
            lastName = self.getElementValue(patientElement, 'FAM')
            firstName = self.getElementValue(patientElement, 'IM')
            patrName = self.getElementValue(patientElement, 'OT')
            birthDate = self.getElementValue(patientElement, 'DR', typeName='date', isRequired=True, mekErrorList=mekErrorList)
            sex = self.getElementValue(patientElement, 'W', typeName='int', isRequired=True, mekErrorList=mekErrorList)
            reliabilityTag = 'DOST'
        else:
            lastName = self.getElementValue(patientElement, 'FAM_P')
            firstName = self.getElementValue(patientElement, 'IM_P')
            patrName = self.getElementValue(patientElement, 'OT_P')
            birthDate = self.getElementValue(patientElement, 'DR_P', typeName='date')
            sex = self.getElementValue(patientElement, 'W_P', typeName='int', isRequired=True, mekErrorList=mekErrorList)
            reliabilityTag = 'DOST_P'
        SNILS = unformatSNILS(self.getElementValue(patientElement, 'SNILS'))
        clientRecord = self._db.getRecordEx(tableClient, cols, [tableClient['lastName'].eq(lastName),
                                                                tableClient['firstName'].eq(firstName),
                                                                tableClient['patrName'].eq(patrName),
                                                                tableClient['birthDate'].dateEq(birthDate),
                                                                tableClient['SNILS'].eq(SNILS)]) if SNILS else None

        # littleStranger = self.getElementValue(patientElement, 'NOVOR', isRequired=True, mekErrorList=mekErrorList)



        lastName = self.getElementValue(patientElement, 'FAM')
        firstName = self.getElementValue(patientElement, 'IM')
        patrName = self.getElementValue(patientElement, 'OT')
        birthDate = self.getElementValue(patientElement, 'DR', typeName='date', isRequired=True, mekErrorList=mekErrorList)

        if not clientRecord:
            PATR_NAME_MISSED = 1
            LAST_NAME_MISSED = 2
            FIRST_NAME_MISSED = 3
            DAY_OF_BIRTH_MISSED = 4
            ONLY_YEAR_OF_BIRTH = 5
            BIRTHDATE_NO_MATCH_CALENDAR = 6
            reliabilityElement = patientElement.firstChildElement(reliabilityTag)
            reliabilityList = []
            while not reliabilityElement.isNull():
                reliabilityList.append(forceInt(reliabilityElement.text()))
                reliabilityElement = reliabilityElement.nextSiblingElement(reliabilityTag)

            cond = []
            if PATR_NAME_MISSED not in reliabilityList:
                cond.append(tableClient['patrName'].eq(patrName))
            if LAST_NAME_MISSED not in reliabilityList:
                cond.append(tableClient['lastName'].eq(lastName))
            if FIRST_NAME_MISSED not in reliabilityList:
                cond.append(tableClient['firstName'].eq(firstName))
            if BIRTHDATE_NO_MATCH_CALENDAR not in reliabilityList:
                if ONLY_YEAR_OF_BIRTH in reliabilityList:
                    cond.append('YEAR(%s) = %s' % (tableClient['birthDate'], birthDate.year()))
                elif DAY_OF_BIRTH_MISSED in reliabilityList:
                    cond.append('MONTH(%s) = %s' % (tableClient['birthDate'], birthDate.month()))
                    cond.append('YEAR(%s) = %s' % (tableClient['birthDate'], birthDate.year()))
                else:
                    cond.append(tableClient['birthDate'].eq(birthDate))


            if sex != 0: #TODO: atronah: допустимо ли наличие пола = 0 (неопределенно) или пол всегда должен быть вменяемым?
                cond.append(tableClient['sex'].eq(sex))
            clientRecordList = self._db.getRecordList(tableClient, cols, cond)
            if len(clientRecordList) == 1:
                clientRecord = clientRecordList[0]
                clientId = forceRef(clientRecord.value('id'))
            else:
                if sex \
                        and LAST_NAME_MISSED not in reliabilityList \
                        and FIRST_NAME_MISSED not in reliabilityList \
                        and ONLY_YEAR_OF_BIRTH not in reliabilityList \
                        and BIRTHDATE_NO_MATCH_CALENDAR not in reliabilityList:
                    clientRecord = tableClient.newRecord()
                    clientRecord.setValue('lastName', toVariant(lastName))
                    clientRecord.setValue('firstName', toVariant(firstName))
                    clientRecord.setValue('patrName', toVariant(patrName))
                    clientRecord.setValue('birthDate', toVariant(birthDate))
                    clientRecord.setValue('birthPlace', toVariant(self.getElementValue(patientElement, 'MR')))
                    clientRecord.setValue('sex', toVariant(sex))
                    clientRecord.setValue('SNILS', toVariant(SNILS))
                    clientId = self._db.insertRecord('Client', clientRecord)
                else:
                    mekErrorList.append((u'5.2.2',
                                        u'Ошибки в персональных данных ЗЛ, приводящие к невозможности его идентификации',
                                        forceStringEx(patientElement.nodeName()),
                                        u'DOST'))
                    return patientInfo
        else:
            clientId = forceRef(clientRecord.value('id'))



        # docType = self.getElementValue(patientElement, 'DOCTYPE')
        # docSerial = self.getElementValue(patientElement, 'DOCSER')
        # docNumber = self.getElementValue(patientElement, 'DOCNUM')
        #TODO: atronah: обработка документов на основе ЕРЗ
        #TODO: atronah: необходимо проверить соответствие маске для типа документа.

        policyKindCode = self.getElementValue(patientElement, 'VPOLIS', isRequired=True, mekErrorList=mekErrorList)
        policySerial = u'еп'
        policyNumber = self.getElementValue(patientElement, 'ENP', isRequired=True, mekErrorList=mekErrorList)
        if forceStringEx(policyNumber) == '0' * 16:
            policySerial = self.getElementValue(patientElement, 'SPOLIS')
            policyNumber = self.getElementValue(patientElement, 'NPOLIS')
        elif forceInt(policyKindCode) != 3:
            policyKindCode = forceStringEx(3) # федеральный код единого полиса

        tablePolicy = self._db.table('ClientPolicy')
        policyKindId = self.getPolicyKindByCode(policyKindCode)
        policyCond = [tablePolicy['client_id'].eq(clientId),
                      tablePolicy['serial'].like(policySerial),
                      tablePolicy['number'].like(policyNumber),
                      tablePolicy['policyKind_id'].eq(policyKindId)]
        policyRecord = self._db.getRecordEx(tablePolicy,
                                            cols=tablePolicy['id'],
                                            where=policyCond)

        if not policyRecord:
            policyRecord = tablePolicy.newRecord()
            policyRecord.setValue('serial', toVariant(policySerial))
            policyRecord.setValue('number', toVariant(policyNumber))
            policyRecord.setValue('policyKind_id', toVariant(policyKindId))
            policyRecord.setValue('policyType_id', toVariant(self._policyTypeId))
            policyRecord.setValue('begDate', toVariant(QtCore.QDate.currentDate()))
            policyRecord.setValue('client_id', toVariant(clientId))
            self._db.insertRecord(tablePolicy, policyRecord)

        # FIXME: craz: перенесено временно из ImportR46XML. Переписать.
        if not self.processClientPolicyERZ(clientId):
            mekErrorList.append((u'5.2.3', u'Оказание МП ЗЛ, получившему полис ОМС на территории другого субъекта РФ', None, None))
        patientInfo['id'] = clientId
        # Чьи пол и возраст заполнять для новорожденного?
        patientInfo['sex'] = sex
        patientInfo['birthDate'] = birthDate
        patientInfo['littleStranger'] = novor if novor != '0' else None

        return patientInfo


    def processClientPolicyERZ(self, clientId):
        record = selectLatestRecord('ClientPolicy', clientId)
        if not record:
            self.logger().warning(u'Не удалось найти полис пациента {%s}' % clientId)
            return False

        # if forceString(record.value('note')) == 'erz':
        #     return 1

        db = self._db
        tableERZ = db.table('erz.erz')
        erzFields = [tableERZ['ENP'], tableERZ['OPDOC'], tableERZ['Q']]
        # erzRecord = db.getRecordEx(tableERZ,
        #                            cols=erzFields,
        #                            where=tableERZ['ENP'].eq(record.value('number')))
        # if erzRecord:
        #     record.setValue('note', toVariant('erz'))
        #     record.setValue('policyKind_id', toVariant(self.getPolicyKindByCode(forceStringEx(erzRecord.value('OPDOC')))))
        #     q = forceStringEx(erzRecord.value('Q'))
        #     if q:
        #         record.setValue('insurer_id', toVariant(self._insurerCache.get(q.strip(), None)))
        #     db.updateRecord('ClientPolicy', record)
        #     return 1

        client = db.table('Client')
        cd = db.table('ClientDocument')
        tbl = client.leftJoin(cd, cd['id'].eq('getClientDocumentId(Client.id)'))
        clientInfo = db.getRecordEx(tbl, [client['id'], client['notes'], client['lastName'], client['firstName'],
                                               client['patrName'], client['birthDate'], client['SNILS'], cd['serial'],
                                               cd['number']],
                                    client['id'].eq(clientId))
        found = False
        # if forceStringEx(clientInfo.value('SNILS')):
        #     erzRecord = db.getRecordEx(tableERZ, erzFields, tableERZ['SS'].eq(clientInfo.value('SNILS')))
        #     if erzRecord: found = True

        lastName = forceStringEx(clientInfo.value('lastName'))
        firstName = forceStringEx(clientInfo.value('firstName'))
        patrName = forceStringEx(clientInfo.value('patrName'))
        if not found and not forceDate(clientInfo.value('birthDate')).isNull():
            cond = [tableERZ['DR'].eq(clientInfo.value('birthDate'))]
            if lastName: cond.append(tableERZ['FAM'].eq(lastName))
            else: cond.append(tableERZ['FAM'].isNull())
            if firstName: cond.append(tableERZ['IM'].eq(firstName))
            else: cond.append(tableERZ['IM'].isNull())
            if patrName: cond.append(tableERZ['OT'].eq(patrName))
            else: cond.append(tableERZ['OT'].isNull())
            erzRecord = db.getRecordEx(tableERZ, erzFields, cond)
            if erzRecord: found = True

        # docs = forceStringEx(clientInfo.value('serial'))
        # docn = forceStringEx(clientInfo.value('number'))
        # if not found and forceStringEx(clientInfo.value('number')):
        #     erzRecord = db.getRecordEx(tableERZ, erzFields, [tableERZ['DOCN'].eq(docn),
        #                                                 tableERZ['DOCS'].eq(docs)])
        #     if erzRecord: found = True
        #
        # if not found and docn and docs:
        #     erzRecord = db.getRecordEx(tableERZ, erzFields, [tableERZ['DOCN'].eq(docs+docn),
        #                                                 tableERZ['DOCS'].isNotNull()])
        #     if erzRecord: found = True
        #
        # pols = forceStringEx(record.value('serial'))
        # poln = forceStringEx(record.value('number'))
        #
        # if not found and pols and poln:
        #     erzRecord = db.getRecordEx(tableERZ, erzFields, [tableERZ['NPOL'].eq(pols + poln),
        #                                                 tableERZ['SPOL'].isNull()])
        #     if erzRecord: found = True

        if not found:
            self.logger().warning(u'Не удалось найти пациента {%s} в ЕРЗ.' % clientId)
            return False

        # insurerId = self._insurerCache.get(forceStringEx(erzRecord.value('Q')),
        #                                    0)
        # newRecord = db.table('ClientPolicy').newRecord()
        # newRecord.setValue('client_id', toVariant(clientId))
        # newRecord.setValue('insurer_id', toVariant(insurerId))
        # newRecord.setValue('policyKind_id', toVariant(self.getPolicyKindByCode(forceStringEx(erzRecord.value('OPDOC')))))
        # newRecord.setValue('policyType_id', toVariant(self._policyTypeId)) #self.policyTypeTerritorial))
        # newRecord.setValue('serial', toVariant(''))
        # newRecord.setValue('number', erzRecord.value('ENP'))
        # newRecord.setValue('note', toVariant('erz'))
        # db.insertRecord('ClientPolicy', newRecord)

        #TODO: заполнять Client.notes

        return True





    # def loadRefBooks(self):
    #     self.loadPurposeCache()
    #     self.loadAidKindCache()
    #     self.loadResultCache()
    #     self.loadDiagnosticResultCache()
    #     self.loadUnitCache()
    #     self.loadLpuCache()
    #
    #
    # def loadPurposeCache(self):
    #     self.loadRefBookCache('rbEventTypePurpose', 'federalCode', self._purposeCache)
    #
    #
    # def loadAidKindCache(self):
    #     self.loadRefBookCache('rbMedicalAidKind', 'federalCode', self._aidKindCache)
    #
    #
    # def loadResultCache(self):
    #     self.loadRefBookCache('rbResult', 'federalCode', self._resultCache)
    #
    #
    # def loadDiagnosticResultCache(self):
    #     self.loadRefBookCache('rbDiagnosticResult', 'federalCode', self._diagnosticResultCache)
    #
    #
    # def loadUnitCache(self):
    #     self.loadRefBookCache('rbMedicalAidUnit', 'federalCode', self._unitCache)
    #
    #
    # def loadLpuCache(self):
    #     self.loadRefBookCache('Organisation', 'infisCode', self._lpuCache)
    #
    #
    # def loadRefBookCache(self, tableName, keyField, cache):
    #     table = self._db.table(tableName)
    #     cond = [table[keyField].inlist(cache.keys())]
    #     recordList = self._db.getRecordList(table,
    #                                         [table.idField(), table[keyField]],
    #                                         cond)
    #     for record in recordList:
    #         key = forceStringEx(record.value(keyField))
    #         value = forceRef(record.value(table.idFieldName()))
    #         cache[key] = value


class CImportDialog(QtGui.QDialog):
    InitState = 0
    ImportState = 1

    def __init__(self, db, orgId, parent = None):
        super(CImportDialog, self).__init__(parent = parent)
        self._db = db
        self._pi = CProgressInformer(processEventsFlag=QtCore.QEventLoop.AllEvents)
        self._engine = CImportR85MTREngine(db, orgId, progressInformer=self._pi)
        self._engine.setUserConfirmationFunction(self.userConfirmation)
        self._loggerHandler = CLogHandler(self._engine.logger(), self)
        self._loggerHandler.setLevel(logging.INFO)
        self._currentState = self.InitState

        self.setupUi()

        self.onStateChanged()


    def setParams(self, params):
        if isinstance(params, dict):
            fileName = forceStringEx(getPref(params, 'inputFile', u''))
            if os.path.isfile(fileName):
                self.edtFileName.setText(fileName)


    def engine(self):
        return self._engine


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
        lineLayout.addWidget(self.edtFileName)
        self.btnBrowseFile = QtGui.QToolButton()
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
        self._loggerHandler.logged.connect(self.logInfo.append)

        # buttons block
        subLayout = QtGui.QHBoxLayout()
        self.btnNextAction = QtGui.QPushButton()
        self.btnNextAction.clicked.connect(self.onNextActionClicked)
        subLayout.addStretch()
        subLayout.addWidget(self.btnNextAction)
        self.btnClose = QtGui.QPushButton()
        self.btnClose.clicked.connect(self.onCloseClicked)
        subLayout.addWidget(self.btnClose)
        layout.addLayout(subLayout)

        self.setLayout(layout)
        self.setMinimumWidth(512)
        self.retranslateUi()


    # noinspection PyAttributeOutsideInit
    def retranslateUi(self):
        context = unicode(getClassName(self))
        self.setWindowTitle(forceTr(u'Импорт. Крым. МежТер.', context))
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
                self._engine.process(forceStringEx(self.edtFileName.text()))
            except Exception, e:
                self.currentState = self.InitState
                raise
            self.currentState = self.InitState

        elif self.currentState == self.ImportState:
            self._engine.abort()
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
            super(CImportDialog, self).done(result)



    @QtCore.pyqtSlot()
    def onCloseClicked(self):
        self.accept()


    @QtCore.pyqtSlot()
    def onBrowseFileClicked(self):
        fileName = forceStringEx(QtGui.QFileDialog.getOpenFileName(self,
                                                                       u'Укажите директорию для сохранения файлов выгрузки',
                                                                       self.edtFileName.text(),
                                                                       u'Файлы (*.xml *.oms)'))
        if os.path.isfile(fileName):
            self.edtFileName.setText(fileName)

