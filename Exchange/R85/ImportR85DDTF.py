# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
#############################################################################


"""
Created on 18/06/15

@author: craz
"""

# TODO: reexposed
# FIXME: поправить комментарии
# FIXME: craz: DISP tag
# FIXME: craz: multiple files

import calendar
import logging
import os
import zipfile

from PyQt4 import QtCore, QtGui
from Accounting.Utils import updateAccount
from Events.Utils import CFinanceType
from Exchange.R85.ExchangeEngine import CExchangeImportR85Engine
from library.AgeSelector import parseAgeSelector, checkAgeSelector
from library.ProgressBar import CProgressBar
from library.ProgressInformer import CProgressInformer

from library.Utils import getPref, getClassName, setPref, forceRef, forceDate, forceStringEx, toVariant, forceDouble, \
    forceInt, unformatSNILS, CLogHandler, forceTr, calcAge, MKBwithoutSubclassification, forceBool
from library.XML.XMLHelper import CXMLHelper
from library.database import CDatabase
from library.exception import CDatabaseException

from Registry.Utils import selectLatestRecord


def importR85DDTF(widget, orgId):
    importWindow = CImportDialog(QtGui.qApp.db, orgId, parent=widget)
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

class CImportR85DDTFEngine(CExchangeImportR85Engine):
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
        # 'purpose': {'tagName': 'USL_OK',
        #             'tableName': 'rbEventTypePurpose',
        #             'key': ('federalCode', 'str'),
        #             'value': ('id', 'ref'),
        #             'createIfNotExists': False},
        'aidKind': {'tagName': 'VIDPOM',
                    'tableName': 'rbMedicalAidKind',
                    'key': ('federalCode', 'str'),
                    'value': ('id', 'ref'),
                    'createIfNotExists': False},
        'result': {'tagName': 'RSLT_D',
                   'tableName': 'rbResult',
                   'key': ('federalCode', 'str'),
                   'value': ('id', 'ref'),
                   'createIfNotExists': False},
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
        # 'diagResult': {'tagName': 'ISHOD',
        #                'tableName': 'rbDiagnosticResult',
        #                'key': ('federalCode', 'str'),
        #                'value': ('id', 'ref'),
        #                'createIfNotExists': False},
        # 'aidUnit': {'tagName': 'IDSP',
        #             'tableName': 'rbMedicalAidUnit',
        #             'key': ('federalCode', 'str'),
        #             'value': ('id', 'ref')},
        'lpu': {'tagName': 'LPU',
                'tableName': 'Organisation',
                'key': ('infisCode', 'str'),
                'value': ('id', 'ref'),
                'createIfNotExists': False},
        # 'actionType': {'tagName': 'CODE_USL',
        #                'tableName': 'ActionType',
        #                'key': ('code', 'str'),
        #                'value': ('id', 'ref'),
        #                'createIfNotExists': False},
        'diagnosisType': {'tableName': 'rbDiagnosisType',
                          'key': ('code', 'str'),
                          'value': ('id', 'ref'),
                          'createIfNotExists': False},
    }
    IS_MO = 'm'
    IS_FUND = 't'
    IS_INSURER = 's'

    def __init__(self, db, orgId, progressInformer = None, format=None):
        super(CImportR85DDTFEngine, self).__init__(progressInformer)
        self._db = db if isinstance(db, CDatabase) else None
        self._logDBName = db.db.databaseName() + u'_276'

        self._orgId = orgId
        self._orgInfis = None
        # self._currentOKATO = None
        self._refuseEventTypeId = None # ID типа действия, который используется в случае невозможности определить корректный тип
        self._policyTypeId = None # Тип полиса для всех создаваемых полисов (ОМС)

        # self._contractIdByInfis = {}
        self._personIdBySpeciality = {}

        self._insurerCache = {}
        # Справочник именованных кешей, описанных в атрибуте класса .rbCaches
        self._rbCaches = {}
        self._refuseIdCache = {}
        self._mkbCache = {}

        self._eventTypeCache = {}
        self._policyKindIdByCode = {}
        self._documentTypeIdByCode = {}
        self._specialityCache = {}
        self._dummyPersonCache = {}
        self._mesInfoCache = {}
        self._serviceInfoCache = {}
        self._tariffInfoCache = {}
        self._eventTypeId = None
        self._diagnosticResultId = None

        #document-dependent caches:
        self._personCache = {}
        self._persData = {} # словарь с обработанными, но не сохраненными регистрационными данными. Использыется для доп. проверок на этапе обработки H-файла и группового сохранения всех данных о пациенте.
        self._logger.setLevel(logging.INFO)
        self._format = format
        self._logDBExists = False # Если настроена база для "лога", в нее сохраняется импортированный файл в виде, максимально приближенном к оригиналу.

    def prepareDefaults(self):
        tblEventType = self._db.table('EventType')
        # tblPurpose = self._db.table('rbEventTypePurpose')
        tblDiagnosticResult = self._db.table('rbDiagnosticResult')
        # queryTable = tblEventType.innerJoin(tblPurpose, tblPurpose['id'].eq(tblEventType['purpose_id']))
        record = self._db.getRecordEx(table=tblEventType.leftJoin(
                        tblDiagnosticResult, tblDiagnosticResult['eventPurpose_id'].eq(tblEventType['purpose_id'])),
                                      cols=[tblEventType['id'].alias('eventType_id'),
                                            tblDiagnosticResult['id'].alias('result_id')],
                                      where=[tblEventType['code'].eq(u'ДВ1')])
        if record:
            self._eventTypeId = forceRef(record.value('eventType_id'))
            self._diagnosticResultId = forceRef(record.value('diagnosticResult_id'))


    def logDBTable(self, tableName):
        return self._db.table(self._logDBName + u'.' + tableName)

    # ---- load\init\clear caches
    # def initContractIdInfo(self):
    #     """Формирует кэш идентификаторов договоров для всех ТФ с учетом года действия.
    #     Делается выборка по всем договорам, дата окончания которых в этом или в предыдущем году,
    #     а также, у которых получателем является ТФ (5ти значный инфис код с 3 нулями на конце).
    #     Результаты выборки (id договоров) помещаются в словарь с ключом (инфис_код, год).
    #
    #     Если год начала отличается от года окончания договора, то данный договор попадает в словарь столько раз,
    #     сколько лет охватывает его период действия.
    #     """
    #     self.nextPhase(1, u'Загрузка данных по договорам')
    #     # self._contractIdByInfis.clear()
    #     tableContract = self._db.table('Contract')
    #     tableOrganisation = self._db.table('Organisation')
    #     queryTable = tableContract.innerJoin(tableOrganisation,
    #                                          tableOrganisation['id'].eq(tableContract['recipient_id']))
    #
    #     recordList = self._db.getRecordList(table=queryTable,
    #                                         cols=[tableContract['id'].alias('contractId'),
    #                                               tableContract['begDate'].alias('contractBegDate'),
    #                                               tableContract['endDate'].alias('contractEndDate'),
    #                                               tableOrganisation['infisCode']],
    #                                         where=[tableContract['deleted'].eq(0),
    #                                                'YEAR(%s) >= (YEAR(CURRENT_DATE) - 1)' % tableContract['endDate'],
    #                                                tableOrganisation['infisCode'].regexp('^[[:digit:]]{2}0{0,3}$')],
    #                                         order=tableContract['endDate'])
    #     self.nextPhase(len(recordList), u'Обработка данных по договорам ТФ')
    #     for record in recordList:
    #         sourceInfis = forceStringEx(record.value('infisCode'))[:2]
    #         begDate = forceDate(record.value('contractBegDate'))
    #         endDate = forceDate(record.value('contractEndDate'))
    #         contractId = forceRef(record.value('contractId'))
    #         for year in xrange(begDate.year(), endDate.year() + 1):
    #             self._contractIdByInfis[sourceInfis, year] = contractId
    #     self.finishPhase()

    def loadCurrentOrgInfo(self):
        """Загружает информацию о текущем Фонде.

        """
        self.nextPhase(1, u'Получение данных по текущему ТФ')
        tableOrganisation = self._db.table('Organisation')
        record = self._db.getRecord(tableOrganisation,
                                    cols=[tableOrganisation['infisCode'],
                                          #tableOrganisation['OKATO']
                                          ],
                                    itemId=self._orgId)
        self._orgInfis = forceStringEx(record.value('infisCode'))
        if self._orgInfis == '85': self._orgInfis = '85000'
        if not self._orgInfis:
            self.logger().warning(u'Не удалось получить инфис код текущего ТФ {%s}' % self._orgId)
        # self._currentOKATO = self.formatOKATO(record.value('OKATO'), 2)
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
            tagName = cacheInfo.get('tagName', None)
            tableName = cacheInfo['tableName']
            keyName, keyType = cacheInfo['key']
            valueName, valueType = cacheInfo['value']
            table = self._db.table(tableName)
            cond = []
            if tagName:
                nodeList = doc.elementsByTagName(tagName)
                for elementIdx in xrange(nodeList.length()):
                    element = nodeList.item(elementIdx).toElement()
                    keyValue = self.convertValue(element.text(), keyType)
                    if not cache.has_key(keyValue):
                        keyForLoading.append(keyValue)
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
        for tagName in ['DS1']: #['DS0', 'DS1', 'DS2', 'DS3']:
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
                                                  tablePerson['federalCode']],
                                            where=[tablePerson['org_id'].eq(orgId)],
                                            )
        for record in recordList:
            self._personCache[orgId][forceStringEx(record.value('federalCode'))] = forceRef(record.value('id'))

    def updateSpecialityCache(self):
        """Обновляет кэш специальностей.

        @return:
        """

        # TODO: сделать по аналогии с кэшэм МКБ - тянуть только те специальности, которые встречаются в документе
        self._specialityCache.clear()
        tableSpeciality = self._db.table('rbSpeciality')
        recordList = self._db.getRecordList(tableSpeciality,
                                            cols=[tableSpeciality['id'],
                                                  tableSpeciality['federalCode'],
                                                  ])
        for record in recordList:
            # По умолчанию у нас везде используется V015. V004 является исключением от одного-двух регионов.
            self._specialityCache[forceInt(record.value('federalCode'))] = forceRef(record.value('id'))

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
        # self._contractIdByInfis.clear()

        for cacheInfo in self.rbCaches.values():
            cacheInfo.get('cache', {}).clear()
        self._mkbCache.clear()

        self._refuseIdCache.clear()
        self._policyKindIdByCode.clear()
        self._documentTypeIdByCode.clear()
        self._serviceInfoCache.clear()
        self._mesInfoCache.clear()
        self._tariffInfoCache.clear()
        self._dummyPersonCache.clear()

        self._insurerCache.clear()

        self.clearDocumentCache()

        self._policyTypeId = None
        self._refuseEventTypeId = None


    # ---- checkers
    def checkMKB(self, mkb, patientInfo, checkDate, mekErrorList):
        """Проверяет соответствие переданного диагноза *mkb* органичениям, описанным в базе данных.
        Проверяет, является ли переданный диагноз подходящим для ОМС и МТР, а так же сверяет, подходит ли он для
        переданного пациента *patientInfo*. В случае успеха всех проверок возвращает истину, в случае обнаружения проблем
        возвращает False и добавляет в mekErrorList данные по найденным ошибкам.

        :param mkb: Проверяемый диагноз в виде строки с кодом МКБ-10
        :param patientInfo: Информация о пациенте, необходимая для проверки (словарь с ключами "sex" (числовое обозначение пола)
        и "birthDate" (QDate() с датой рождения))
        :param checkDate: дата проверки для корректного определения возраста пациента.
        :param mekErrorList: список для внесения в него данных о найденных ошибках в формате кортежа
        (код ошибки МЭК, Описание ошибки МЭК, Имя узла документа с ошибочным узлом, Имя узла с ошибкой)
        :return: True, если ошибок выявленно не было, иначе False
        """
        mkbInfo = self._mkbCache.get(MKBwithoutSubclassification(mkb), None)

        if not (mkbInfo and
                mkbInfo['OMS' if patientInfo['insurer'].startswith('85') else 'MTR']):
            mekErrorList.append((u'5.3.3', u'Включение в реестр счетов случаев, не входящих в терр. программу ОМС', None, None))
            return False
        if mkbInfo['sex'] and patientInfo['sex'] != mkbInfo['sex'] \
                or mkbInfo['age'] and not checkAgeSelector(mkbInfo['age'], calcAge(patientInfo['birthDate'], checkDate)):
            mekErrorList.append((u'5.1.4', u'Некорректное заполнение полей реестра счетов', 'PATIENT', 'DR' if patientInfo['sex'] == mkbInfo['sex'] else 'W'))
            return False

        return True


    # ---- getters


    def getContractId(self, infisCode):
        """Возвращает ID договора, используемого для импорта по территории с указанным инфис кодом.

        :param infisCode: инфис территории, по которой производится импорт.
        :return: ID договора, используемого для импорта указанной территории.
        """
        # infisCode = forceStringEx(infisCode)[:2]
        tableContract = self._db.table('Contract')
        tableOrganisation = self._db.table('Organisation')
        # noinspection PyArgumentList
        record = self._db.getRecordEx(table=tableContract.innerJoin(tableOrganisation,
                                                          tableOrganisation['id'].eq(tableContract['recipient_id'])),
                            cols='Contract.id',
                            where=[tableContract['endDate'].dateGt(QtCore.QDate.currentDate()),
                                    tableOrganisation['infisCode'].eq(infisCode)])
        if record: return forceRef(record.value('id'))
        # contractId = self._contractIdByInfis.get(infisCode, None)
        # if not contractId:
        self.logger().warning(u'Не удалось найти договор для импорта данных от организации с инфис "%s"' % infisCode)
        return None
        # return contractId


    def getRefuseEventTypeId(self):
        """Возвращает резервного ID типа события, используемого для создания отказных обращений, корректный тип для которых не удалось определить.

        :return: ID типа события для создания отказного обращения.
        """
        if not self._refuseEventTypeId:
            refuseEventTypeCode = u'tfRefuse'
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
                mekErrorList.append((u'1.1.1', u'Пустые значения идентификаторов назначения обращения и/или вида мед.помощи', None, None))
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
            # noinspection PyTypeChecker
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

    def getDocumentTypeByCode(self, code):
        if not self._documentTypeIdByCode.has_key(code):
            self._documentTypeIdByCode[code] = forceRef(self._db.translate('rbDocumentType', 'federalCode', code, 'id'))
        return self._documentTypeIdByCode[code]

    def getDummyPersonId(self, orgId, specialityCode):
        if not self._dummyPersonCache.has_key((orgId, specialityCode)):
            tblPerson = self._db.table('Person')
            specialityId = self._specialityCache.get(forceInt(specialityCode), None)
            resultIdList = self._db.getIdList('Person',
                                              'id',
                                              'org_id = %s and speciality_id = %s' % (orgId, specialityId),
                                              '')
            if resultIdList:
                personId = resultIdList[0]
            else:
                record = tblPerson.newRecord()
                record.setValue('org_id', toVariant(orgId))
                record.setValue('speciality_id', toVariant(specialityId))
                record.setValue('code', toVariant('-1'))
                record.setValue('federalCode', toVariant('-1'))
                record.setValue('lastName', toVariant(u'Врач не задан'))
                personId = self._db.insertRecord(tblPerson, record)
            self._dummyPersonCache[(orgId, specialityCode)] = personId
        return self._dummyPersonCache[(orgId, specialityCode)]

    def getPersonId(self, orgId, personCode, specialityCode=None):
        """Возвращает ID врача с указанной специальностью *specialityCode* и организацией *orgId*.
        При необходимости создает его в базе и кеширует данные.

        :param orgId: ID ЛПУ, врач для которой ищется в базе
        :param personCode: федеральный код искомого врача
        :return: ID врача
        """

        if orgId not in self._personCache.keys():
            self.updatePersonCache(orgId)
        orgPersonCache = self._personCache[orgId]
        personId = orgPersonCache.get(personCode, None)
        # isOk = True
        # if personId is None:
        #     isOk = False
        #     personId = orgPersonCache.get('-1', None)
        # if personId is None:
        #     personId = orgPersonCache.get('', None)
        if personId is None:
            personId = self.getDummyPersonId(orgId, specialityCode)
        if not personId:
            self.logger().warning(u'Не удалось получить ID врача по указанным ID ЛПУ {%s} и федеральному коду врача {%s}' % (orgId, personCode))
        return personId

    def getServiceInfo(self, code):
        if not self._serviceInfoCache.has_key(code):
            r = self._db.getRecordEx('rbService',
                                     u'id, adultUetDoctor',
                                     u'code = \'%s\'' % code)
            if r: self._serviceInfoCache[code] = (forceRef(r.value('id')), forceDouble(r.value('adultUetDoctor')))
            else: self._serviceInfoCache[code] = (None, None)
        return self._serviceInfoCache[code]

    def getMesInfo(self, code):
        if not self._mesInfoCache.has_key(code):
            r = self._db.getRecordEx('mes.MES',
                                     u'id, avgDuration',
                                     u'code = \'%s\' and deleted = 0' % code)
            if r: self._mesInfoCache[code] = (forceRef(r.value('id')), forceDouble(r.value('avgDuration')))
            else: self._mesInfoCache[code] = (None, None)
        return self._mesInfoCache[code]

    def getTariffInfo(self, serviceId, contractId):
        if not self._tariffInfoCache.has_key((serviceId, contractId)):
            r = None
            if serviceId and contractId:
                r = self._db.getRecordEx('Contract_Tariff',
                                     'id, tariffType, price, federalPrice, unit_id',
                                     'master_id = %s and service_id = %s and deleted = 0' % (contractId, serviceId))
            if r:
                self._tariffInfoCache[serviceId, contractId] = (forceRef(r.value('id')),
                                                                forceInt(r.value('tariffType')),
                                                                forceDouble(r.value('price')),
                                                                forceDouble(r.value('federalPrice')),
                                                                forceRef(r.value('unit_id')))
            else: self._tariffInfoCache[serviceId, contractId] = (None, None, None, None, None)
        return self._tariffInfoCache[serviceId, contractId]

    # ---- processing


    def process(self, fileName):
        """Запускает процесс импорта.

        :param fileName: имя файла для импорта
        :return: True
        """
        self.isAbort = False
        self.phaseReset(3)
        # self.initContractIdInfo()
        self.loadCurrentOrgInfo()
        self.preloadInsurerCache()
        self.prepareDefaults()
        self._policyTypeId = forceRef(self._db.translate('rbPolicyType', 'code', '1', 'id'))
        # noinspection PyAttributeOutsideInit
        self._mesSpecificationId = forceRef(self._db.translate('rbMesSpecification', 'code', '0', 'id'))
        try:
            self._logDBExists = bool(self._db.table(self._logDBName+'.DDFile'))
        except CDatabaseException:
            self._logDBExists = False
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
            fullName = os.path.splitext(os.path.basename(fileName))[0].lower()
            if fullName.startswith(self._format.lower()):
                name = fullName[2:]
                docType = self._format
            elif fullName.startswith('l'):
                name = fullName[1:]
                docType = 'l'
            else:
                raise Exception

            nameParts = name.split('_')
            if len(nameParts) != 2: raise Exception
            orgs, account = nameParts
            if len(orgs) < 13: raise Exception
            if len(account) < 5: raise Exception

            # docType = orgs[0]
            sourceType = orgs[0]
            sourceCodeLength = 6 if sourceType == self.IS_MO else 5
            sourceCode = orgs[1:1+sourceCodeLength]
            destType = orgs[1+sourceCodeLength]
            destCodeLength = 6 if destType == self.IS_MO else 5
            destCode = orgs[2+sourceCodeLength:2+sourceCodeLength+destCodeLength]

            year = 2000 + forceInt(account[:2])
            month = account[2:4]
            number = account[4:]

            return True, docType == 'l', sourceType, sourceCode, destType, destCode, year, month, number
        except Exception, e:
            self.logger().critical(u'Некорректное имя файла "%s" (%s)' % (fileName, e.message))
            self.onException()

        return False, False, u'', u'', u'', u'', 0, 0, None


    def processFile(self, fullFileName):
        """Импортирует набор документов, соответствующий указанному файлу. Набор должен состоять из HM-архива со
        сведениями о проведенном лечении и сооветствующего LM-архива с персональными данными.

        :param fullFileName: имя файла со сведениями о лечении. (HM*.xml) (описание имени см в `parseFileName`)
        :return: True, если импорт файла прошел успешно, False в ином случа
        :raise: Exception("архив пуст"), если архив пуст
        """
        docFile = None
        persFile = None
        try:
            dirName = os.path.dirname(fullFileName)
            fileName, ext = os.path.splitext(os.path.basename(fullFileName))
            persFileName = 'L'+fileName[2:] + '.zip'
            fullPersFileName = os.path.join(dirName, persFileName)
            logFileTable = self.logDBTable('DDFile') if self._logDBExists else None
            logFileRecord = logFileTable.newRecord() if logFileTable else None
            isOk, isPersData, sourceType, sourceInfis, destType, destInfis, year, month, number = self.parseFileName(fullFileName)
            if not isOk:
                return False
            if logFileRecord:
                logFileRecord.setValue('sourceType', toVariant(sourceType))
                logFileRecord.setValue('sourceInfis', toVariant(sourceInfis))
                logFileRecord.setValue('destType', toVariant(destType))
                logFileRecord.setValue('destInfis', toVariant(destInfis))
                logFileRecord.setValue('year', toVariant(year))
                logFileRecord.setValue('month', toVariant(month))
                logFileRecord.setValue('number', toVariant(number))
                logFileId = self._db.insertRecord(self.logDBTable('DDFile'), logFileRecord) if logFileRecord else None
            if destInfis != self._orgInfis:
                self.logger().info(u'Пропуск обработки файла "%s": получатель (%s) не соответствует текущей организации (%s)' % (fileName, destInfis, self._orgInfis))
                return False

            if not os.path.exists(fullPersFileName):
                raise Exception(u'Не найден файл с персональными данными %s' % fullPersFileName)
            if not zipfile.is_zipfile(fullFileName):
                raise Exception(u'Файл %s не является zip-архивом' % fullFileName)
            if not zipfile.is_zipfile(fullPersFileName):
                raise Exception(u'Файл %s не является zip-архивом' % fullPersFileName)

            persZipFile = zipfile.ZipFile(fullPersFileName, 'r')
            zipItems = persZipFile.namelist()
            if not zipItems:
                raise Exception(u'zip-архив "%s" пуст' % fullPersFileName)
            persFile = persZipFile.open(zipItems[0])
            self.processPersDocument(CXMLHelper.loadDocument(QtCore.QString(persFile.read().decode(self.encoding))), logFileRecord)


            zipFile = zipfile.ZipFile(fullFileName, 'r')
            zipItems = zipFile.namelist()
            if not zipItems:
                raise Exception(u'zip-архив "%s" пуст' % fullFileName)
            docFile = zipFile.open(zipItems[0])

            self.processDocument(CXMLHelper.loadDocument(QtCore.QString(docFile.read().decode(self.encoding))),
                                 sourceInfis,
                                 year,
                                 month,
                                 logFileRecord)


        except Exception, e:
            self.logger().warning(u'Не удалось провести импорт (%s)' % e.message)
            self.onException()
            return False
        finally:
            if docFile:
                docFile.close()
            if persFile:
                persFile.close()

        return True

    def processPersDocument(self, document, logFileRecord=None):
        """Анализирует и импортирует DOM-документ с персональными данными
        """
        self.nextPhase(document.elementsByTagName('PERS').length(), u'Обработка персональных данных')
        self.clearDocumentCache()

        rootElement = self.getElement(document, 'PERS_LIST', isRequired=True)
        if not rootElement:
            return False

        headerElement = self.getElement(rootElement, 'ZGLV', isRequired=True)
        if not headerElement:
            return False

        if not self.parseHeaderElement(headerElement, isPersDocument=True, logFileRecord=logFileRecord):
            return False

        logFileId = forceRef(logFileRecord.value('id')) if logFileRecord else None
        try:
            persElement = self.getElement(rootElement, 'PERS', isRequired=True)
            while not persElement.isNull():
                self.processPersElement(persElement, logFileId)
                persElement = persElement.nextSiblingElement('PERS')
                self.nextPhaseStep()
        finally:
            self.finishPhase()

        return True

    def processDocument(self, document, sourceInfis, year, month, logFileRecord=None):
        """Анализирует и импортирует DOM-документ.

        :param document: документ, подлежащий анализу и импорту (QDomDocument)
        :param sourceInfis: инфис тер. фонда, предоставившего данные
        :param year: год формирования данного документа
        :return: True в случае успеха и False в ином случае
        """
        self.nextPhase(document.elementsByTagName('SLUCH').length(), u'Обработка случаев лечения')
        # self.clearDocumentCache()
        self.updateRBCaches(document)
        self.updateMKBCache(document)
        self.updateSpecialityCache()

        rootElement = self.getElement(document, 'ZL_LIST', isRequired=True)
        if not rootElement:
            return False

        headerElement = self.getElement(rootElement, 'ZGLV', isRequired=True)
        if not headerElement:
            return False


        if not self.parseHeaderElement(headerElement, logFileRecord=logFileRecord):
            return False

        self._db.transaction(checkIsInit=True)
        try:
            accInfo = {}#{'isUpdate' : isUpdateFile}
            accountElement = self.getElement(rootElement, 'SCHET', isRequired=True)
            self.processAccountElement(accountElement, sourceInfis, year, accInfo, logFileRecord=logFileRecord)
            logFileId = self._db.updateRecord(self.logDBTable('DDFile'), logFileRecord) if logFileRecord else None

            entityElement = accountElement.nextSiblingElement('ZAP')
            while not entityElement.isNull():
                self.processEntity(entityElement, accInfo, logFileId)
                entityElement = entityElement.nextSiblingElement('ZAP')
            updateAccount(accInfo['id'])
            self._db.commit()
        except:
            self._db.rollback()
            raise
        finally:
            self.finishPhase()

        return True


    def processPersElement(self, persElement, logFileId = None):
        patientInfo = {}
        #TODO: atronah: обработка новорожденных
        # tableClient = self._db.table('Client')
        # cols = [tableClient['id'],
        #         tableClient['lastName'],
        #         tableClient['firstName'],
        #         tableClient['patrName'],
        #         tableClient['sex'],
        #         tableClient['birthDate'],
        #         tableClient['birthPlace'],
        #         tableClient['SNILS'],
        #         ]
        #
        # mekErrorList = []
        # clientRecord = self._db.getRecordEx(tableClient, cols, tableClient['SNILS'].eq(SNILS)) if SNILS else None

        # littleStranger = self.getElementValue(patientElement, 'NOVOR', isRequired=True, mekErrorList=mekErrorList)

        #TODO: craz: добавить использование mekErrorList и для файла персональных данных.
        mekErrorList = []
        idPac = self.getElementValue(persElement, 'ID_PAC')
        # if not clientRecord:
        patientInfo['lastName'] = self.getElementValue(persElement, 'FAM')
        patientInfo['firstName'] = self.getElementValue(persElement, 'IM')
        patientInfo['patrName'] = self.getElementValue(persElement, 'OT')
        patientInfo['birthDate'] = self.getElementValue(persElement, 'DR', typeName='date', isRequired=True, mekErrorList=mekErrorList)
        patientInfo['sex'] = self.getElementValue(persElement, 'W', typeName='int', isRequired=True, mekErrorList=mekErrorList)
        patientInfo['SNILS'] = unformatSNILS(self.getElementValue(persElement, 'SNILS'))
        patientInfo['birthPlace'] = self.getElementValue(persElement, 'MR')

        patientInfo['reprLastName'] = self.getElementValue(persElement, 'FAM_P')
        patientInfo['reprFirstName'] = self.getElementValue(persElement, 'IM_P')
        patientInfo['reprPatrName'] = self.getElementValue(persElement, 'OT_P')
        patientInfo['reprBirthDate'] = self.getElementValue(persElement, 'DR_P', typeName='date')
        patientInfo['reprSex'] = self.getElementValue(persElement, 'W_P', typeName='int')

        # PATR_NAME_MISSED = 1
        # LAST_NAME_MISSED = 2
        # FIRST_NAME_MISSED = 3
        # DAY_OF_BIRTH_MISSED = 4
        # ONLY_YEAR_OF_BIRTH = 5
        # BIRTHDATE_NO_MATCH_CALENDAR = 6
        reliabilityElement = persElement.firstChildElement('DOST')
        reliabilityList = []
        while not reliabilityElement.isNull():
            reliabilityList.append(forceInt(reliabilityElement.text()))
            reliabilityElement = reliabilityElement.nextSiblingElement('DOST')
        patientInfo['reliabilityList'] = reliabilityList
        reprReliabilityElement = persElement.firstChildElement('DOST_P')
        reprReliabilityList = []
        while not reprReliabilityElement.isNull():
            reprReliabilityList.append(forceInt(reprReliabilityElement.text()))
            reprReliabilityElement = reprReliabilityElement.nextSiblingElement('DOST_P')
        patientInfo['reprReliabilityList'] = reprReliabilityList

        # cond = []
        # if PATR_NAME_MISSED not in reliabilityList:
        #     cond.append(tableClient['patrName'].eq(patrName))
        # if LAST_NAME_MISSED not in reliabilityList:
        #     cond.append(tableClient['lastName'].eq(lastName))
        # if FIRST_NAME_MISSED not in reliabilityList:
        #     cond.append(tableClient['firstName'].eq(firstName))
        # if BIRTHDATE_NO_MATCH_CALENDAR not in reliabilityList:
        #     if ONLY_YEAR_OF_BIRTH in reliabilityList:
        #         cond.append('YEAR(%s) = %s' % (tableClient['birthDate'], birthDate.year()))
        #     elif DAY_OF_BIRTH_MISSED in reliabilityList:
        #         cond.append('MONTH(%s) = %s' % (tableClient['birthDate'], birthDate.month()))
        #         cond.append('YEAR(%s) = %s' % (tableClient['birthDate'], birthDate.year()))
        #     else:
        #         cond.append(tableClient['birthDate'].eq(birthDate))

        # if sex != 0: #TODO: atronah: допустимо ли наличие пола = 0 (неопределенно) или пол всегда должен быть вменяемым?
        #     cond.append(tableClient['sex'].eq(sex))
        # clientRecordList = self._db.getRecordList(tableClient, cols, cond)
        # if len(clientRecordList) == 1:
        #     clientRecord = clientRecordList[0]
        #     clientId = forceRef(clientRecord.value('id'))
        # else:
        #     if sex \
        #             and LAST_NAME_MISSED not in reliabilityList \
        #             and FIRST_NAME_MISSED not in reliabilityList \
        #             and ONLY_YEAR_OF_BIRTH not in reliabilityList \
        #             and BIRTHDATE_NO_MATCH_CALENDAR not in reliabilityList:
        #         clientRecord = tableClient.newRecord()
        #         clientRecord.setValue('lastName', toVariant(lastName))
        #         clientRecord.setValue('firstName', toVariant(firstName))
        #         clientRecord.setValue('patrName', toVariant(patrName))
        #         clientRecord.setValue('birthDate', toVariant(birthDate))
        #         clientRecord.setValue('birthPlace', toVariant(self.getElementValue(patientElement, 'MR')))
        #         clientRecord.setValue('sex', toVariant(sex))
        #         clientRecord.setValue('SNILS', toVariant(SNILS))
        #         clientId = self._db.insertRecord('Client', clientRecord)
        #     else:
        #         mekErrorList.append((u'5.2.2',
        #                             u'Ошибки в персональных данных ЗЛ, приводящие к невозможности его идентификации',
        #                             forceStringEx(patientElement.nodeName()),
        #                             u'DOST'))
        #         return patientInfo
        # # else:
        # #     clientId = forceRef(clientRecord.value('id'))



        patientInfo['docType'] = self.getElementValue(persElement, 'DOCTYPE')
        patientInfo['docSerial'] = self.getElementValue(persElement, 'DOCSER')
        patientInfo['docNumber'] = self.getElementValue(persElement, 'DOCNUM')
        #TODO: atronah: обработка документов на основе ЕРЗ
        #TODO: atronah: необходимо проверить соответствие маске для типа документа.
        patientInfo['mekErrorList'] = mekErrorList

        self._persData[idPac] = patientInfo

        if logFileId:
            table = self.logDBTable('DDPers')
            record = table.newRecord()
            record.setValue('file_id', toVariant(logFileId))
            record.setValue('id_pac', toVariant(idPac))
            record.setValue('fam', toVariant(self.getElementValue(persElement, 'FAM', return_null=True)))
            record.setValue('im', toVariant(self.getElementValue(persElement, 'IM', return_null=True)))
            record.setValue('ot', toVariant(self.getElementValue(persElement, 'OT', return_null=True)))
            record.setValue('w', toVariant(self.getElementValue(persElement, 'W', typeName='n')))
            record.setValue('dr', toVariant(self.getElementValue(persElement, 'DR', typeName='d')))
            record.setValue('dost', toVariant(u'#'.join([unicode(r) for r in patientInfo['reliabilityList']])))
            record.setValue('fam_p', toVariant(self.getElementValue(persElement, 'FAM_P', return_null=True)))
            record.setValue('im_p', toVariant(self.getElementValue(persElement, 'IM_P', return_null=True)))
            record.setValue('ot_p', toVariant(self.getElementValue(persElement, 'OT_P', return_null=True)))
            record.setValue('w_p', toVariant(self.getElementValue(persElement, 'W_P', typeName='n', return_null=True)))
            record.setValue('dr_p', toVariant(self.getElementValue(persElement, 'DR_P', typeName='d', return_null=True)))
            record.setValue('dost_p', toVariant(u'#'.join([unicode(r) for r in patientInfo['reprReliabilityList']])))
            record.setValue('mr', toVariant(self.getElementValue(persElement, 'MR', return_null=True)))
            record.setValue('doctype', toVariant(self.getElementValue(persElement, 'DOCTYPE', return_null=True)))
            record.setValue('docser', toVariant(self.getElementValue(persElement, 'DOCSER', return_null=True)))
            record.setValue('docnum', toVariant(self.getElementValue(persElement, 'DOCNUM', return_null=True)))
            record.setValue('snils', toVariant(self.getElementValue(persElement, 'SNILS', return_null=True)))
            record.setValue('okatog', toVariant(self.getElementValue(persElement, 'OKATOG', return_null=True)))
            record.setValue('okatop', toVariant(self.getElementValue(persElement, 'OKATOP', return_null=True)))
            record.setValue('comentp', toVariant(self.getElementValue(persElement, 'COMENTP', return_null=True)))
            self._db.insertRecord(table, record)

        # policyKindCode = self.getElementValue(patientElement, 'VPOLIS', isRequired=True, mekErrorList=mekErrorList)
        # policySerial = u'еп'
        # policyNumber = self.getElementValue(patientElement, 'ENP', isRequired=True, mekErrorList=mekErrorList)
        # if forceStringEx(policyNumber) == '0' * 16:
        #     policySerial = self.getElementValue(patientElement, 'SPOLIS')
        #     policyNumber = self.getElementValue(patientElement, 'NPOLIS')
        #
        # tablePolicy = self._db.table('ClientPolicy')
        # policyKindId = self.getPolicyKindByCode(policyKindCode)
        # policyCond = [tablePolicy['client_id'].eq(clientId),
        #               tablePolicy['serial'].like(policySerial),
        #               tablePolicy['number'].like(policyNumber),
        #               tablePolicy['policyKind_id'].eq(policyKindId)]
        # policyRecord = self._db.getRecordEx(tablePolicy,
        #                                     cols=tablePolicy['id'],
        #                                     where=policyCond)
        #
        # if not policyRecord:
        #     policyRecord = tablePolicy.newRecord()
        #     policyRecord.setValue('serial', toVariant(policySerial))
        #     policyRecord.setValue('number', toVariant(policyNumber))
        #     policyRecord.setValue('policyKind_id', toVariant(policyKindId))
        #     policyRecord.setValue('policyType_id', toVariant(self._policyTypeId))
        #     policyRecord.setValue('begDate', toVariant(QtCore.QDate.currentDate()))
        #     policyRecord.setValue('client_id', toVariant(clientId))
        #     self._db.insertRecord(tablePolicy, policyRecord)
        #
        # # FIXME: craz: перенесено временно из ImportR46XML. Переписать.
        # if not self.processClientPolicyERZ(clientId):
        #     mekErrorList.append((u'5.2.2', u'Ошибки в персональных данных ЗЛ, приводящие к невозможности его идентификации', None, None))
        # patientInfo['id'] = clientId
        # patientInfo['sex'] = sex
        # patientInfo['birthDate'] = birthDate


        # return patientInfo

    def parseHeaderElement(self, headerElement, isPersDocument=False, logFileRecord=None):#sourceInfis):
        """Анализирует заголовочный узел импортируемого документа.
        Производит проверку ОКАТО фондов отправления и назначения.

        :param headerElement: DOM-узел заголовочных данных (<ZGLV>).
        :return: True в случае успеха и False в ином случае
        """
        ver = self.getElementValue(headerElement, 'VERSION', isRequired=True)
        if ver != self.version:
            self.logger().error(u'Формат версии `%s` не поддерживается. Должен быть `%s`.' % (ver, self.version))
            return False

        if logFileRecord:
            if isPersDocument:
                logFileRecord.setValue('lFilename', toVariant(self.getElementValue(headerElement, 'FILENAME', isRequired=True)))
                logFileRecord.setValue('lFilename1', toVariant(self.getElementValue(headerElement, 'FILENAME1', isRequired=True)))
                logFileRecord.setValue('lVersion', toVariant(ver))
                logFileRecord.setValue('lData', toVariant(self.getElementValue(headerElement, 'DATA', typeName='d', isRequired=True)))
            else:
                logFileRecord.setValue('hFilename', toVariant(self.getElementValue(headerElement, 'FILENAME', isRequired=True)))
                logFileRecord.setValue('hVersion', toVariant(ver))
                logFileRecord.setValue('hData', toVariant(self.getElementValue(headerElement, 'DATA', typeName='d', isRequired=True)))

        # TODO: craz: проверка наличия и корректности FILENAME/FILENAME1, вывод ошибки по ФЛК
        if isPersDocument: pass

        return True


    def processAccountElement(self, accountElement, sourceInfis, year, accInfo, logFileRecord):
        """Обрабатывает узел с описанием импортируемого счета.

        :param accountElement: узел с описанием импортируемого счета.
        :param sourceInfis: инфис код фонда, приславшего данные
        :param year: год счета
        :param accInfo: словарь для сохранения некоторых данных по счету.
        :return: результат обработки (True или False)
        :raise Exception:
        """

        mekErrorList = []
        accNumber = self.getElementValue(accountElement, 'NSCHET', isRequired=True, mekErrorList=mekErrorList)
        accExposeDateString = self.getElementValue(accountElement, 'DSCHET', isRequired=True, mekErrorList=mekErrorList)
        contractId = self.getContractId(sourceInfis)
        if not contractId:
            raise Exception(u'Обработка счета %s от %s не удалась:'
                            u' не найден договор для организации с инфис-кодом "%s"' % (accNumber, accExposeDateString, sourceInfis))

        # Модифицировать номер договора здесь, или раньше?
        if self._format:
            accNumber = u'%s-%s' % (self._format, accNumber)
        payerInfis = self.getElementValue(accountElement, 'PLAT')
        if not payerInfis: payerInfis = u'85'


        accExposeDate = self.convertValue(accExposeDateString, 'date')

        accInfo.setdefault('mekErrorList', []).extend(mekErrorList)

        tableAccount = self._db.table('Account')
        record = self._db.getRecordEx(tableAccount,
                                      cols='*',
                                      where=[tableAccount['number'].like(accNumber),
                                             tableAccount['exposeDate'].eq(accExposeDate),
                                             'YEAR(%s) = %s' % (tableAccount['settleDate'], year),
                                             tableAccount['contract_id'].eq(contractId)])
        if record:
            if self.getUserConfirmation(u'Подтвердите удаление',
                                        u'Данный счет (%s от %s) уже был загружен ранее.\n'
                                        u'Удалить ранее загруженный счет?' % (accNumber, accExposeDateString)):
                self._db.deleteRecord(tableAccount, tableAccount['id'].eq(forceRef(record.value('id'))))
            else:
                raise Exception(u'Обработка счета %s от %s отменена пользователем' % (accNumber, accExposeDateString))

        payerId = forceRef(self._db.translate('Organisation', 'infisCode', payerInfis, 'id'))
        # contractInfo = getContractInfo(contractId)

        record = tableAccount.newRecord()
        record.setValue('number', toVariant(accNumber))
        record.setValue('exposeDate', toVariant(accExposeDate))
        settleMonth = self.getElementValue(accountElement, 'MONTH', typeName='int', isRequired=True, mekErrorList=mekErrorList)
        record.setValue('settleDate',
                        toVariant(QtCore.QDate(year, settleMonth, calendar.monthrange(year, settleMonth)[1])))
        record.setValue('date', toVariant(accExposeDate))
        record.setValue('amount', toVariant(self.dummyN))
        exposeTotal = self.getElementValue(accountElement, 'SUMMAV', typeName='double', isRequired=True, mekErrorList=mekErrorList)
        record.setValue('sum', toVariant(exposeTotal))
        exposePayed = self.getElementValue(accountElement, 'SUMMAP', typeName='double')
        record.setValue('payedSum', toVariant(exposePayed))
        record.setValue('contract_id', toVariant(contractId))
        record.setValue('payer_id', toVariant(payerId)) # Теоретически может получиться расхождение плательщика в договоре и счете
        self._db.insertRecord('Account', record)

        accountId = forceRef(record.value('id'))
        accInfo['id'] = accountId
        accInfo['record'] = record
        accInfo['recipient_id'] = self.getCachedRBValue('lpu', sourceInfis)
        accInfo['contract_id'] = contractId
        # accInfo['contractInfo'] = contractInfo
        accInfo['entities'] = {}
        if logFileRecord:
            logFileRecord.setValue('account_id', toVariant(accountId))
            logFileRecord.setValue('schet_code',
                                   toVariant(self.getElementValue(accountElement, 'CODE', typeName='n', isRequired=True,
                                                                  mekErrorList=mekErrorList)))
            logFileRecord.setValue('schet_code_mo',
                                   toVariant(self.getElementValue(accountElement, 'CODE_MO', isRequired=True,
                                                                   mekErrorList=mekErrorList)))
            logFileRecord.setValue('schet_year',
                                   toVariant(self.getElementValue(accountElement, 'YEAR', typeName='n', isRequired=True,
                                                                  mekErrorList=mekErrorList)))
            logFileRecord.setValue('schet_month',
                                   toVariant(self.getElementValue(accountElement, 'MONTH', typeName='n', isRequired=True,
                                                                  mekErrorList=mekErrorList)))
            logFileRecord.setValue('schet_nschet', toVariant(accNumber))
            logFileRecord.setValue('schet_dschet', toVariant(accExposeDate))
            logFileRecord.setValue('schet_plat',
                                   toVariant(self.getElementValue(accountElement, 'PLAT', return_null=True)))
            logFileRecord.setValue('schet_summav', toVariant(exposeTotal))
            logFileRecord.setValue('schet_summap',
                                   toVariant(self.getElementValue(accountElement, 'SUMMA_P', return_null=True)))

        return True


    def processEntity(self, entityElement, accInfo, logFileId = None):
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
            if logFileId:
                tableZap = self.logDBTable('DDZap')
                zapRecord = tableZap.newRecord()
                zapRecord.setValue('file_id', toVariant(logFileId))
                zapRecord.setValue('n_zap', toVariant(entityKey))
                zapRecord.setValue('pr_nov', toVariant(self.getElementValue(entityElement, 'PR_NOV',
                                                                            typeName='n', return_null=True)))
            else:
                tableZap = None
                zapRecord = None
            patientElement = self.getElement(entityElement, 'PACIENT', isRequired=True, mekErrorList=MEKErrorList)
            patientInfo = self.processPatient(patientElement, MEKErrorList, zapRecord)
            zapId = self._db.insertRecord(tableZap, zapRecord) if logFileId else None
            patientId = patientInfo.get('id', None)
            if not patientId:
                raise Exception(' '.join(MEKErrorList[-1][:2]) if MEKErrorList else u'Проблема идентификации пациента')
            eventElement = patientElement.nextSiblingElement('SLUCH')
            processedEventKeys = []
            while not eventElement.isNull():
                eventKey = self.getElementValue(eventElement, 'IDCASE', isRequired=True, mekErrorList=MEKErrorList)
                if eventKey and eventKey not in processedEventKeys:
                    self.processEvent(eventElement, patientInfo, accInfo, MEKErrorList, zapId=zapId, logFileId=logFileId)
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


    def processEvent(self, eventElement, patientInfo, accInfo, entityMekErrorList, zapId = None, logFileId = None):

        # TODO: craz: поиск существующих записей.
        # TODO: craz: проработать логику внешних идентификаторов (какие используем, где храним)

        eventKey = self.getElementValue(eventElement, 'IDCASE')
        patientId = patientInfo['id']


        mekErrorList = entityMekErrorList[:] #скопировать уже имеющиеся ошибки по записи.

        aidKindCode = self.getElementValue(eventElement, 'VIDPOM', isRequired=True, mekErrorList=mekErrorList)
        lpuCode = self.getElementValue(eventElement, 'LPU', isRequired=True, mekErrorList=mekErrorList)
        nhistory = self.getElementValue(eventElement, 'NHISTORY',
                                            isRequired=True, mekErrorList=mekErrorList)
        eventSetDate = self.getElementValue(eventElement, 'DATE_1', typeName='date',
                                            isRequired=True, mekErrorList=mekErrorList)
        eventExecDate = self.getElementValue(eventElement, 'DATE_2', typeName=  'date',
                                             isRequired=True, mekErrorList=mekErrorList)
        rsltCode = self.getElementValue(eventElement, 'RSLT_D', isRequired=True, mekErrorList=mekErrorList)
        idsp = self.getElementValue(eventElement, 'IDSP', typeName='int', isRequired=True, mekErrorList=mekErrorList)
        sluchId = None
        if zapId:
            sluchTable = self.logDBTable('DDSluch')
            sluchRecord = sluchTable.newRecord()
            sluchRecord.setValue('file_id', toVariant(logFileId))
            sluchRecord.setValue('zap_id', toVariant(zapId))
            sluchRecord.setValue('id_case', toVariant(self.convertValue(eventKey, 'n')))
            sluchRecord.setValue('vidpom', toVariant(self.convertValue(aidKindCode, 'n')))
            sluchRecord.setValue('lpu', toVariant(lpuCode))
            sluchRecord.setValue('lpu_1', toVariant(self.getElementValue(eventElement, 'LPU_1', return_null=True)))
            sluchRecord.setValue('nhistory', toVariant(nhistory))
            sluchRecord.setValue('date_1', toVariant(eventSetDate))
            sluchRecord.setValue('date_2', toVariant(eventExecDate))
            sluchRecord.setValue('ds1', toVariant(self.getElementValue(eventElement, 'DS1',
                                                                       isRequired=True, mekErrorList=mekErrorList)))
            sluchRecord.setValue('rslt_d', toVariant(rsltCode))
            sluchRecord.setValue('idsp', toVariant(idsp))
            sluchRecord.setValue('ed_col', toVariant(self.getElementValue(eventElement, 'ED_COL', typeName='float',
                                                                          return_null=True)))
            sluchRecord.setValue('tarif', toVariant(self.getElementValue(eventElement, 'TARIF', typeName='float',
                                                                         return_null=True)))
            sluchRecord.setValue('sumv', toVariant(self.getElementValue(eventElement, 'SUMV', typeName='float',
                                                                        isRequired=True, mekErrorList=mekErrorList)))
            sluchRecord.setValue('oplata', toVariant(self.getElementValue(eventElement, 'OPLATA', typeName='n',
                                                                          isRequired=True, mekErrorList=mekErrorList)))
            sluchRecord.setValue('sump', toVariant(self.getElementValue(eventElement, 'SUMP', typeName='float',
                                                                        return_null=True)))
            sluchRecord.setValue('sank_it', toVariant(self.getElementValue(eventElement, 'SANK_IT', typeName='float',
                                                                           return_null=True)))
            sluchRecord.setValue('comentsl', toVariant(self.getElementValue(eventElement, 'COMENTSL', return_null=True)))
            sluchId = self._db.insertRecord(sluchTable, sluchRecord)

            sankElement = self.getElement(eventElement, 'SANK')
            if not sankElement.isNull():
                sankTable = self.logDBTable('DDSank')
                sankRecord = sankTable.newRecord()
                sankRecord.setValue('file_id', toVariant(logFileId))
                sankRecord.setValue('sluch_id', toVariant(sluchId))
                sankRecord.setValue('s_code', toVariant(self.getElementValue(sankElement, 'S_CODE',
                                                                             isRequired=True, mekErrorList=mekErrorList)))
                sankRecord.setValue('s_sum', toVariant(self.getElementValue(sankElement, 'S_SUM', typeName='float',
                                                                            isRequired=True, mekErrorList=mekErrorList)))
                sankRecord.setValue('s_tip', toVariant(self.getElementValue(sankElement, 'S_TIP', typeName='n',
                                                                            isRequired=True, mekErrorList=mekErrorList)))
                sankRecord.setValue('s_osn', toVariant(self.getElementValue(sankElement, 'S_OSN', typeName='n',
                                                                            isRequired=True, mekErrorList=mekErrorList)))
                sankRecord.setValue('s_com', toVariant(self.getElementValue(sankElement, 'S_COM',
                                                                            isRequired=True, mekErrorList=mekErrorList)))
                sankRecord.setValue('s_ist', toVariant(self.getElementValue(sankElement, 'S_IST', typeName='n',
                                                                            isRequired=True, mekErrorList=mekErrorList)))
                self._db.insertRecord(sankTable, sankRecord)

        # Предварительная обработка услуг
        personCode = None
        specialityCode = None
        serviceList = []
        serviceElement = self.getElement(eventElement, 'USL', isRequired=True, mekErrorList=mekErrorList)
        while not serviceElement.isNull():
            serviceInfo = self.prepareService(serviceElement, accInfo, mekErrorList, sluchId=sluchId, logFileId=logFileId)
            serviceList.append(serviceInfo)
            if serviceInfo['code'].startswith('508'):
                personCode = serviceInfo['doctorCode']
                specialityCode = serviceInfo['specialityCode']
            serviceElement = serviceElement.nextSiblingElement('USL')


        tableEvent = self._db.table('Event')
        tableAccountItem = self._db.table('Account_Item')

        self._db.transaction()
        try:
            # purposeCode = self.getElementValue(eventElement, 'USL_OK', isRequired=True, mekErrorList=mekErrorList)
            # purposeId = self.getCachedRBValue('purpose', purposeCode) # self._purposeCache.get(purposeCode, None)

            # if purposeId is None:
            #     self.logger().info(u'Не удалось найти назначение обращения с кодом "%s" для случая с IDCASE = %s' % (purposeCode, eventKey))
            # #     return False

            aidKindId = self.getCachedRBValue('aidKind', aidKindCode) #self._aidKindCache.get(aidKindCode, None)
            if aidKindId is None:
                self.logger().info(u'Не удалось найти вид медицинской помощи с кодом "%s" для случая с IDCASE = "%s"' % (aidKindCode, eventKey))

            eventTypeId = self._eventTypeId
            # eventTypeId = self.getEventTypeId(purposeId, aidKindId, mekErrorList)
            if eventTypeId is None:
                raise Exception(u'Не удалось определить тип обращения для IDCASE = %s' % eventKey)

            lpuId = self.getCachedRBValue('lpu', lpuCode)#self._lpuCache.get(self.getElementValue(eventElement, 'LPU', isRequired=True, mekErrorList=mekErrorList), None)
            if lpuId is None:
                lpuId = accInfo['recipient_id']
            if lpuId is None:
                self.logger().warning(u'Не удалось найти организацию, в которой был проведен случай с IDCASE = "%s"' % eventKey)

            # TODO: craz: значение по умолчанию на основе purpose_id
            resultId = self.getCachedRBValue('result', rsltCode) #self._resultCache.get(self.getElementValue(eventElement, 'RSLT', isRequired=True, mekErrorList=mekErrorList), None)

            # contractId = forceRef(accInfo['record'].value('contract_id'))

            # specialityCode = self.getElementValue(eventElement, 'PRVS', isRequired=True, mekErrorList=mekErrorList)
            eventExecPersonId = self.getPersonId(lpuId,
                                                 personCode,
                                                 specialityCode)
            # if not personFound:
            #     mekErrorList.append((u'5.1.4',
            #                         u'Некорректное заполнение полей реестра счетов',
            #                         forceStringEx(eventElement.nodeName()),
            #                         'IDDOKT')
            #     )

            externalId = 'nhistory:%s#idpac:%s' % (nhistory,
                                                   patientInfo['idPac'])

            isUpdate = accInfo.get('isUpdate', False)
            accountId = forceRef(accInfo['record'].value('id'))
            eventRecordList = self._db.getRecordList(tableEvent,
                                                     cols=tableEvent['id'],
                                                     where=[tableEvent['client_id'].eq(patientId),
                                                            tableEvent['externalId'].inlist([externalId, nhistory]),
                                                            tableEvent['org_id'].eq(lpuId),
                                                            tableEvent['deleted'].eq(0),
                                                            ])


            is_new = True
            eventRecord = None
            for eventRecord in eventRecordList:
                if eventRecord:
                    accountItemList = self._db.getRecordList(tableAccountItem,
                                                             'master_id, refuseType_id',
                                                             where=[tableAccountItem['event_id'].eq(eventRecord.value('id'))])
                    for ai in accountItemList:
                        accId = forceRef(ai.value('master_id'))
                        refuseTypeId = forceRef(ai.value('refuseType_id'))
                        if accId == accountId and not refuseTypeId:
                            self.logger().warning(u'Случай IDCASE=%s уже был импортирован в текущий счет' % eventKey)
                        elif not refuseTypeId:
                            mekErrorList.append((u'5.7.1', u'Повторное выставление счета за уже оплаченную МП', None, None))
                        eventRecord = None
                    #Если найденное обращение находится в другом счете,
                    # if accountIdList:
                    #     if accountId in accountIdList:
                    #         self.logger().warning(u'Случай IDCASE=%s уже был импортирован в текущий счет' % (eventKey))
                    #     # то созадть новое и пометить счет по нему отказанным
                    #     eventRecord = None
                    #     mekErrorList.append((u'5.7.1', u'Повторное выставление счета за уже оплаченную МП', None, None))
                    # else:
                    if not accountItemList:
                        if not isUpdate:
                            self._db.deleteRecord(tableEvent, tableEvent['id'].eq(eventRecord.value('id')))
                            eventRecord = None
                        else:
                            is_new = False

            if not eventRecord:
                eventRecord = tableEvent.newRecord()
                # littleStranger = patientInfo['littleStranger']
                # if littleStranger:
                #     tableLittleStranger = self._db.table('Event_LittleStranger')
                #     lsRecord = tableLittleStranger.newRecord()
                #     lsRecord.setValue('sex', toVariant(forceInt(littleStranger[0])))
                #     year = 2000 + forceInt(littleStranger[5:7])
                #     month = forceInt(littleStranger[3:5])
                #     day = forceInt(littleStranger[1:3])
                #     lsRecord.setValue('birthDate', toVariant(QtCore.QDate(year, month, day)))
                #     lsRecord.setValue('currentNumber', toVariant(forceInt(littleStranger[7])))
                #     lsId = self._db.insertRecord(tableLittleStranger, lsRecord)
                #     eventRecord.setValue('littleStranger_id', toVariant(lsId))

            eventRecord.setValue('client_id', toVariant(patientId))
            eventRecord.setValue('contract_id', accInfo['record'].value('contract_id'))
            eventRecord.setValue('eventType_id', toVariant(eventTypeId))
            eventRecord.setValue('setDate', toVariant(eventSetDate))
            eventRecord.setValue('execDate', toVariant(eventExecDate))
            eventRecord.setValue('org_id', toVariant(lpuId))
            eventRecord.setValue('isPrimary', toVariant(1))
            eventRecord.setValue('externalId', toVariant(externalId))
            eventRecord.setValue('order', toVariant(1))
            # {
            #                                3: 1,    # Плановая
            #                                1: 2,    # Экстренная
            #                                2: 6,    # Неотложная
            #                                }.get(self.getElementValue(eventElement, 'FOR_POM', typeName='int', isRequired=True, mekErrorList=mekErrorList), 1)))
            if resultId:
                eventRecord.setValue('result_id', toVariant(resultId))
            eventRecord.setValue('pregnancyWeek', toVariant(0))
            eventRecord.setValue('totalCost', toVariant(0))
            eventRecord.setValue('execPerson_id', toVariant(eventExecPersonId))
            eventId = self._db.insertOrUpdate(tableEvent, eventRecord)


            #Обработка диагнозов
            #Возможно стоит использовать Events.Utils.getDiagnosisId2, но там жесткая завязка на QtGui.qApp.db и "больная" логика
            PRIMARY_DIAGTYPE_CODE = '2' # основной диагноз
            # SECONDARY_DIAGTYPE_CODE = '9' # сопутствующий диагноз
            # ADVERSE_DIAGTYPE_CODE = '3' # осложнение основного


            #TODO: craz: process other DS* tags, VNOV_M, CODE_MES*
            #TODO: craz: process ED_COL
            # FIXME: craz: client_id - обязательное поля для Diagnosis. При этом для обращения все не так критично. Поэтому проверяем пока что только здесь, а обращение и Account_Item с ошибкой все равно создаем.
            if patientId:
                tableDiagnostic = self._db.table('Diagnostic')
                tableDiagnosis = self._db.table('Diagnosis')
                # queryTable = tableDiagnostic.innerJoin(tableDiagnosis,
                #                                        tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']))
                self._db.deleteRecord(tableDiagnostic,tableDiagnostic['event_id'].eq(eventId))
                for tagName, typeCode, isRequired in [('DS1', PRIMARY_DIAGTYPE_CODE, True),
                                                      #('DS2', SECONDARY_DIAGTYPE_CODE, False),
                                                      #('DS3', ADVERSE_DIAGTYPE_CODE, False)
                                                      ]:
                    diagElement = self.getElement(eventElement, tagName, isRequired=isRequired, mekErrorList=mekErrorList)
                    if not diagElement.isNull():
                        MKB = forceStringEx(diagElement.text())
                        self.checkMKB(MKB, patientInfo, eventExecDate, mekErrorList)

                        # TODO: craz: add cache
                        diagnosisTypeId = self.getCachedRBValue('diagnosisType', typeCode) #db.translate('rbDiagnosisType', 'code', diagnosisTypeCode, 'id')
                        # characterId = db.translate('rbDiseaseCharacter', 'code', characterCode, 'id')

                        record = self._db.getRecordEx(tableDiagnosis,
                                                      'id',
                                                      [tableDiagnosis['client_id'].eq(patientId),
                                                       tableDiagnosis['MKB'].eq(MKB),
                                                       tableDiagnosis['setDate'].dateEq(eventSetDate),
                                                       tableDiagnosis['endDate'].dateEq(eventExecDate),
                                                       tableDiagnosis['person_id'].eq(eventExecPersonId),
                                                       tableDiagnosis['diagnosisType_id'].eq(diagnosisTypeId)],
                                                      'endDate DESC')
                        if not record:
                            record = tableDiagnosis.newRecord()
                            record.setValue('client_id',        toVariant(patientId))
                            record.setValue('diagnosisType_id', toVariant(diagnosisTypeId))
                            record.setValue('character_id',     QtCore.QVariant())
                            record.setValue('MKB',              toVariant(MKB))
                            record.setValue('setDate',          toVariant(eventSetDate))
                            record.setValue('endDate',          toVariant(eventExecDate))
                            record.setValue('person_id',        toVariant(eventExecPersonId))
                            diagnosisId =  self._db.insertRecord(tableDiagnosis, record)
                        else:
                            diagnosisId = forceRef(record.value('id'))

                        diagnosticRecord = tableDiagnostic.newRecord()
                        if diagnosisId:
                            diagnosticRecord.setValue('event_id', toVariant(eventId))
                            diagnosticRecord.setValue('diagnosis_id', toVariant(diagnosisId))
                            diagnosticRecord.setValue('sanatorium', toVariant(0))
                            diagnosticRecord.setValue('hospital', toVariant(0))
                            diagnosticRecord.setValue('setDatetime', toVariant(eventSetDate))
                            diagnosticRecord.setValue('diagnosisType_id', toVariant(self.getCachedRBValue('diagnosisType', typeCode)))
                            # diagnosticResultId = self.getCachedRBValue('diagResult',
                            #                                            self.getElementValue(eventElement, 'ISHOD', isRequired=True, mekErrorList=mekErrorList))
                            diagnosticRecord.setValue('result_id', toVariant(self._diagnosticResultId))
                            diagnosticRecord.setValue('speciality_id',
                                                      toVariant(self._specialityCache.get(specialityCode)))
                            self._db.insertRecord(tableDiagnostic, diagnosticRecord)






            # closedEventProcessed = False # Была добавлена услуга с кодом 3._.1._; для последующих с таким шаблоном обнуляется цена и сумма.
            # firstVisitProcessed = False # Был обработан первый визит - в него сводится сумма и стоимость всех УЕТ
            # hasVisit = False # Если нет ни одного визита, добавляем заглушки

            # Обработка услуг
            tableAction = self._db.table('Action')
            tableVisit = self._db.table('Visit')
            tableAccountItem = self._db.table('Account_Item')
            for service in serviceList:
                finalMekErrorList = mekErrorList + service['mekErrorList']
                # Очередной МЭК
                # ageDays = calcAgeInDays(patientInfo['birthDate'], service['begDate'])
                # if ageDays > 28 and service['code'] == '1.2.0550' \
                #     or ageDays <= 28 and service['code'] == '1.2.0680':
                #     finalMekErrorList.append((u'6.18.7',
                #                                     u'Несоответствие кода услуги диагнозу, полу, возрасту, профилю отделения',
                #                                     forceStringEx(serviceElement.nodeName()),
                #                                     'CODE_USL'))

                if service['tariff_id']:
                    if patientInfo['insurer'].startswith('85') \
                            and idsp in ('25', '26', '27', '31', '35', '36', '37', '38', '39'):
                        price = service['tariffFederalPrice']
                    else:
                        price = service['tariffPrice']

                    personId = self.getPersonId(lpuId, service['doctorCode'], service['specialityCode'])
                    # if not personFound:
                    #     finalMekErrorList.append((u'5.1.4',
                    #                         u'Некорректное заполнение полей реестра счетов',
                    #                         forceStringEx(serviceElement.nodeName()),
                    #                         'CODE_MD'))

                    amount = 1#service['amount']
                    # serviceCode = service['code']
                    # begDate = service['begDate']
                    # endDate = service['endDate']
                    actionId = None
                    visitId = None
                    tariffType = service['tariffType']
                    uet = service['uet']
                    if tariffType in (2,): # 5):
                        actionTypeId = forceRef(self._db.translate('ActionType', 'code', service['code'], 'id')) #self.getCachedRBValue('actionType', service['code'])
                        if not actionTypeId: return False
                        # if serviceCode.startswith('3.'):
                        #     sum = price
                        # else:
                        #     sum = round(price * amount, 2)
                        sum = price = 0.0
                        old_action = None
                        if not is_new:
                            old_action = self._db.getRecordEx(tableAction,
                                                              'id, begDate, directionDate, person_id, setPerson_id, amount',
                                                              [tableAction['event_id'].eq(eventId),
                                                               tableAction['actionType_id'].eq(actionTypeId),
                                                               tableAction['endDate'].dateEq(service['endDate']),
                                                               tableAction['deleted'].eq(0)])
                            if old_action:
                                actionId = forceRef(old_action.value('id'))
                                old_action.setValue('begDate', toVariant(service['begDate']))
                                old_action.serValue('directionDate', toVariant(service['begDate']))
                                old_action.setValue('person_id', toVariant(personId))
                                old_action.setValue('setPerson_id', toVariant(personId))
                                old_action.setValue('amount', toVariant(service['amount']))
                                self._db.updateRecord(tableAction, old_action)

                        if not old_action:
                            actionRecord = tableAction.newRecord()
                            actionRecord.setValue('actionType_id', toVariant(actionTypeId))
                            actionRecord.setValue('event_id', toVariant(eventId))
                            actionRecord.setValue('directionDate', toVariant(service['begDate']))
                            actionRecord.setValue('status', toVariant(service['status']))
                            actionRecord.setValue('setPerson_id', toVariant(personId))
                            actionRecord.setValue('begDate', toVariant(service['begDate']))
                            actionRecord.setValue('endDate', toVariant(service['endDate']))
                            actionRecord.setValue('person_id', toVariant(personId))
                            actionRecord.setValue('amount', toVariant(service['amount']))
                            actionRecord.setValue('uet', toVariant(service['uet']))
                            actionRecord.setValue('expose', toVariant(1))
                            actionRecord.setValue('account', toVariant(0))
                            # actionRecord.setValue('MKB', toVariant(service['MKB']))
                            actionRecord.setValue('finance_id', toVariant(CFinanceType.getId(CFinanceType.CMI)))
                            actionRecord.setValue('contract_id', toVariant(accInfo['contract_id']))
                            actionRecord.setValue('org_id', toVariant(lpuId))
                            actionId = self._db.insertRecord(tableAction, actionRecord)

                    # elif tariffType in (0, 14):
                    #     hasVisit = True
                    #     old_visit = None
                    #     if serviceCode.startswith('3.') and serviceCode not in ('3.1.0562', '3.1.0562'):
                    #         sum = price
                    #     else:
                    #         sum = round(price * amount, 2)
                    #
                    #     if filter(lambda x: x['uet'] != 0, serviceList):
                    #         if not firstVisitProcessed:
                    #             firstVisitProcessed = True
                    #             uet = reduce(lambda x, y: x + y['uet']*y['amount'], serviceList, 0.0)
                    #             sum = uet * price
                    #         else:
                    #             uet = 0
                    #             sum = 0
                    #
                    #     if not is_new:
                    #         old_visit = self._db.getRecordEx(tableVisit,
                    #                                          'id, person_id',
                    #                                          [tableVisit['event_id'].eq(eventId),
                    #                                           self._db.joinOr([tableVisit['service_id'].eq(service['service_id']),
                    #                                                            tableVisit['service_id'].isNull()]),
                    #                                           tableVisit['date'].dateEq(service['begDate']),
                    #                                           tableVisit['deleted'].eq(0)])
                    #         if old_visit:
                    #             visitId = forceRef(old_visit.value('id'))
                    #             old_visit.setValue('person_id', toVariant(personId))
                    #             self._db.updateRecord(tableVisit, old_visit)
                    #     if not old_visit:
                    #         visitRecord = tableVisit.newRecord()
                    #         visitRecord.setValue('event_id', toVariant(eventId))
                    #         visitRecord.setValue('scene_id', toVariant(1)) # FIXME
                    #         visitRecord.setValue('date', toVariant(service['begDate']))
                    #         visitRecord.setValue('visitType_id', toVariant(1)) # FIXME
                    #         visitRecord.setValue('person_id', toVariant(personId))
                    #         visitRecord.setValue('isPrimary', toVariant(1))
                    #         visitRecord.setValue('finance_id', toVariant(CFinanceType.getId(CFinanceType.CMI)))
                    #         visitRecord.setValue('service_id', toVariant(service['service_id']))
                    #         # visitRecord.setValue('MKB', toVariant(service['MKB']))
                    #         visitId = self._db.insertRecord(tableVisit, visitRecord)
                    elif tariffType == 10:
                        mesId, avgDuration = self.getMesInfo(service['code'])
                        sum = price = reduce(lambda x, y: x + y['tariffPrice'], serviceList, 0.0)
                        if mesId:
                            self._db.query('UPDATE Event SET MES_id = %s, mesSpecification_id = %s WHERE id = %s'
                                           % (mesId, self._mesSpecificationId, eventId))
                            # eventRecord = tableEvent.newRecord()
                            # eventRecord.setValue('id', toVariant(eventId))
                            # eventRecord.setValue('MES_id', toVariant(mesId))
                            # eventRecord.setValue('mesSpecification_id', toVariant(self._mesSpecificationId))
                            # self._db.updateRecord(tableEvent, eventRecord)
                            # countRedDays = serviceCode == '2.1.0562' # Для гемодиализа нужно учитывать выходные даже по ДС
                            # eventLength = getEventLengthDays(begDate, endDate, countRedDays, eventTypeId)
                            # if avgDuration:
                            #     if serviceCode in ('2.1.1361', '2.2.1361', '2.1.1364', '2.2.1364') and \
                            #         filter(lambda x: x['code'] in ('A11.20.008', 'A16.20.036.001', 'A16.20.037', 'A16.20.079'), serviceList):
                            #         if eventLength <= round(avgDuration * 0.3, 0):
                            #             sum = round(sum * 0.5, 2)
                            #     elif ((serviceCode.startswith('1') and eventLength < round(avgDuration * 0.7, 0)) or
                            #              (serviceCode.startswith('2') and eventLength < round(avgDuration * 0.9, 0))) and \
                            #             serviceCode not in ('1.1.1362', '1.2.1362'):
                            #         price = round(price/avgDuration, 2)
                            #         sum = round(price * eventLength, 2)
                            # if serviceCode.startswith('1.'):
                            #     coeff = 1
                            #     age = calcAgeInYears(patientInfo['birthDate'], eventSetDate)
                            #     if age >= 0:
                            #         if age < 5:
                            #             coeff += 0.2
                            #         elif age >= 75:
                            #             coeff += 0.3
                            #     if filter(lambda x: x['code'] in ('1.1.0050','1.2.0050'), serviceList):
                            #         coeff += 0.1
                            #     if filter(lambda x: x['code'].lower().startswith('a16.') or x['code'] in ('1.1.1121', '1.2.1121'), serviceList): #AZ
                            #         coeff += 0.05
                            #     sum = sum * coeff
                            # if purposeCode == '2': # Дневной стационар
                            #     amount = eventLength

                    # # Оставляем цену только для первой услуги по данному шаблону, остальные обнуляем
                    # if re.match('^3\..\.1\.', serviceCode) and serviceCode not in ('3.1.1.171', '3.2.1.171', '3.1.1.089', '3.1.1.090'):
                    #     if closedEventProcessed:
                    #         sum = 0
                    #         price = 0
                    #     else:
                    #         closedEventProcessed = True

                    if tariffType in (2, 10):# 0, 2, 5, 10, 14):
                        aiRecord = tableAccountItem.newRecord()
                        aiRecord.setValue('master_id', toVariant(accInfo['id']))
                        aiRecord.setValue('event_id', toVariant(eventId))
                        aiRecord.setValue('visit_id', toVariant(visitId))
                        aiRecord.setValue('action_id', toVariant(actionId))
                        aiRecord.setValue('tariff_id', toVariant(service['tariff_id']))
                        aiRecord.setValue('price', toVariant(price))
                        # noinspection PyUnboundLocalVariable
                        aiRecord.setValue('sum', toVariant(sum))
                        aiRecord.setValue('amount', toVariant(amount))
                        aiRecord.setValue('service_id', toVariant(service['service_id']))
                        aiRecord.setValue('uet', toVariant(uet))
                        aiRecord.setValue('unit_id', toVariant(self.getCachedRBValue('aidUnit', idsp) if idsp else service['tariffUnit_id']))
                        # noinspection PyArgumentList
                        aiRecord.setValue('date', toVariant(QtCore.QDate.currentDate()))
                        if finalMekErrorList:
                            aiRecord.setValue('number', toVariant(u'Отказ по МЭК'))
                            refuseCode = finalMekErrorList[-1][0]
                            if refuseCode == u'6.18.7':
                                aiRecord.setValue('refuseType_id', toVariant(self.getPayRefuseId(u'5.1.4')))
                                aiRecord.setValue('note', toVariant(finalMekErrorList[-1][1]))
                            else:
                                aiRecord.setValue('refuseType_id', toVariant(self.getPayRefuseId(finalMekErrorList[-1][0])))
                                if refuseCode in (u'5.1.3'):
                                    aiRecord.setValue('note', toVariant(u'Отсутствует поле [%s:%s]' % (finalMekErrorList[-1][2], finalMekErrorList[-1][3])))
                                elif refuseCode in (u'5.1.4'):
                                    aiRecord.setValue('note', toVariant(u'Некорректно заполнено поле [%s:%s]' % (finalMekErrorList[-1][2], finalMekErrorList[-1][3])))
                        else:
                            aiRecord.setValue('number', toVariant(u'Оплачено'))
                        # noinspection PyUnusedLocal
                        aiId = self._db.insertRecord(tableAccountItem, aiRecord)


            # if not hasVisit:
            dummyVisitRecord = tableVisit.newRecord()
            dummyVisitRecord.setValue('event_id', toVariant(eventId))
            dummyVisitRecord.setValue('scene_id', toVariant(1)) # FIXME
            dummyVisitRecord.setValue('date', toVariant(eventSetDate))
            dummyVisitRecord.setValue('visitType_id', toVariant(1)) # FIXME
            dummyVisitRecord.setValue('person_id', toVariant(eventExecPersonId))
            dummyVisitRecord.setValue('isPrimary', toVariant(1))
            dummyVisitRecord.setValue('finance_id', toVariant(CFinanceType.getId(CFinanceType.CMI)))
            # noinspection PyUnusedLocal
            dummyVisitId = self._db.insertRecord(tableVisit, dummyVisitRecord)

            self._db.commit()
        except:
            self._db.rollback()
            raise

        return True

    def prepareService(self, serviceElement, accInfo, eventMekErrorList, sluchId=None, logFileId=None):
        service = {}
        # Копируем существующий список ошибок
        mekErrorList = eventMekErrorList[:]
        service['key'] = self.getElementValue(serviceElement, 'IDSERV', isRequired=True, mekErrorList=mekErrorList)
        service['lpu'] = self.getElementValue(serviceElement, 'LPU', isRequired=True, mekErrorList=mekErrorList)
        # service['profileCode'] = self.getElementValue(serviceElement, 'PROFIL', typeName='int', isRequired=True, mekErrorList=mekErrorList)
        # service['child'] = self.getElementValue(serviceElement, 'DET', typeName='int', isRequired=True, mekErrorList=mekErrorList)
        service['begDate'] = self.getElementValue(serviceElement, 'DATE_IN', typeName='d', isRequired=True, mekErrorList=mekErrorList)
        service['endDate'] = self.getElementValue(serviceElement, 'DATE_OUT', typeName='d', isRequired=True, mekErrorList=mekErrorList)
        comentu = self.getElementValue(serviceElement, 'COMENTU', mekErrorList=mekErrorList)
        # В перспективе возможна работа с этими значениями как со словарем, но пока формат такой.
        serviceCodeDesc, serviceStatusDesc = comentu.split('#')
        serviceCode = serviceCodeDesc.split(':')[1]
        serviceStatus = serviceStatusDesc.split(':')[1]
        # service['MKB'] = self.getElementValue(serviceElement, 'DS', isRequired=True, mekErrorList=mekErrorList)
        service['code'] = serviceCode #self.getElementValue(serviceElement, 'CODE_USL', isRequired=True, mekErrorList=mekErrorList)
        service['status'] = serviceStatus
        service['amount'] = 1 #self.getElementValue(serviceElement, 'KOL_USL', typeName='double', isRequired=True, mekErrorList=mekErrorList)
        service['price'] = self.getElementValue(serviceElement, 'TARIF', typeName='double')
        service['sum'] = self.getElementValue(serviceElement, 'SUMV_USL', typeName='double', isRequired=True, mekErrorList=mekErrorList)
        service['specialityCode'] = self.getElementValue(serviceElement, 'PRVS', typeName='int', isRequired=True, mekErrorList=mekErrorList)
        service['doctorCode'] = self.getElementValue(serviceElement, 'CODE_MD', isRequired=True, mekErrorList=mekErrorList)
        service['mekErrorList'] = mekErrorList

        if sluchId:
            uslTable = self.logDBTable('DDUsl')
            uslRecord = uslTable.newRecord()
            uslRecord.setValue('file_id', toVariant(logFileId))
            uslRecord.setValue('sluch_id', toVariant(sluchId))
            uslRecord.setValue('idserv', toVariant(service['key']))
            uslRecord.setValue('lpu', toVariant(service['lpu']))
            uslRecord.setValue('lpu_1', toVariant(self.getElementValue(serviceElement, 'LPU_1', return_null=True)))
            uslRecord.setValue('date_in', toVariant(service['begDate']))
            uslRecord.setValue('date_out', toVariant(service['endDate']))
            uslRecord.setValue('tarif', toVariant(service['price']))
            uslRecord.setValue('sumv_usl', toVariant(service['sum']))
            uslRecord.setValue('prvs', toVariant(service['specialityCode']))
            uslRecord.setValue('code_md', toVariant(service['doctorCode']))
            uslRecord.setValue('comentu', toVariant(self.getElementValue(serviceElement, 'COMENTU', return_null=True)))
            self._db.insertRecord(uslTable, uslRecord)

        serviceId, uet = self.getServiceInfo(service['code'])
        service['service_id'] = serviceId
        service['uet'] = uet
        tariffId, tariffType, tariffPrice, federalPrice, unitId = self.getTariffInfo(serviceId, accInfo['contract_id'])
        service['tariff_id'] = tariffId
        service['tariffType'] = tariffType
        service['tariffPrice'] = tariffPrice
        service['tariffFederalPrice'] = federalPrice
        service['tariffUnit_id'] = unitId
        return service

    def processPatient(self, patientElement, mekErrorList, zapRecord):
        patientInfo = {}
        idPac = self.getElementValue(patientElement, 'ID_PAC', isRequired=True, mekErrorList=mekErrorList)
        if zapRecord:
            zapRecord.setValue('pacient_id_pac', toVariant(idPac))
            zapRecord.setValue('pacient_vpolis', toVariant(self.getElementValue(patientElement, 'VPOLIS', typeName='n')))
            zapRecord.setValue('pacient_spolis', toVariant(self.getElementValue(patientElement, 'SPOLIS', return_null=True)))
            zapRecord.setValue('pacient_npolis', toVariant(self.getElementValue(patientElement, 'NPOLIS')))
            zapRecord.setValue('pacient_st_okato',
                               toVariant(self.getElementValue(patientElement, 'ST_OKATO', return_null=True)))
            zapRecord.setValue('pacient_smo', toVariant(self.getElementValue(patientElement, 'SMO', return_null=True)))
            zapRecord.setValue('pacient_smo_ogrn',
                               toVariant(self.getElementValue(patientElement, 'SMO_OGRN', return_null=True)))
            zapRecord.setValue('pacient_smo_ok',
                               toVariant(self.getElementValue(patientElement, 'SMO_OK', return_null=True)))
            zapRecord.setValue('pacient_smo_nam',
                               toVariant(self.getElementValue(patientElement, 'SMO_NAM', return_null=True)))
        persData = self._persData.get(idPac, None) # Данные из файла L
        if not persData:
            mekErrorList.append((u'5.2.4',
                                u'В файле L не обнаружен пациент с ID_PAC = %s' % idPac,
                                forceStringEx(patientElement.nodeName()),
                                u'ID_PAC'))
            return patientInfo

        # novor = self.getElementValue(patientElement, 'NOVOR', isRequired=True, mekErrorList=mekErrorList)
        #
        # if novor == '0':
        lastName = persData['lastName']
        firstName = persData['firstName']
        patrName = persData['patrName']
        birthDate = persData['birthDate']
        sex = persData['sex']
        reliabilityList = persData['reliabilityList']
        # novor = None
        # else:
        #     lastName = persData['reprLastName']
        #     firstName = persData['reprFirstName']
        #     patrName = persData['reprPatrName']
        #     birthDate = persData['reprBirthDate']
        #     sex = persData['reprSex']
        #     reliabilityList = persData['reprReliabilityList']

        tableClient = self._db.table('Client')
        # tableClientPolicy = self._db.table('ClientPolicy')
        # tableClientDocument = self._db.table('ClientDocument')
        cols = [tableClient['id'],
                # tableClient['lastName'],
                # tableClient['firstName'],
                # tableClient['patrName'],
                # tableClient['sex'],
                # tableClient['birthDate'],
                # tableClient['birthPlace'],
                # tableClient['SNILS'],
                ]


        # littleStranger = self.getElementValue(patientElement, 'NOVOR', isRequired=True, mekErrorList=mekErrorList)



        PATR_NAME_MISSED = 1
        LAST_NAME_MISSED = 2
        FIRST_NAME_MISSED = 3
        DAY_OF_BIRTH_MISSED = 4
        ONLY_YEAR_OF_BIRTH = 5
        BIRTHDATE_NO_MATCH_CALENDAR = 6

        cond = [tableClient['deleted'].eq(0)]
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
        if len(clientRecordList) >= 1:  # TODO: craz: имхо все же стоит добавить уточняющие проверки
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
                clientRecord.setValue('birthPlace', toVariant(persData['birthPlace']))
                clientRecord.setValue('sex', toVariant(sex))
                clientRecord.setValue('SNILS', toVariant(persData['SNILS']))
                clientId = self._db.insertRecord('Client', clientRecord)

                # FIXME: craz: раньше почему-то документ обрабатывался только для новых пациентов. Пока так же.

                docTypeId = self.getDocumentTypeByCode(persData['docType'])
                if docTypeId:
                    tableClientDocument = self._db.table('ClientDocument')
                    docRecord = tableClientDocument.newRecord()
                    docRecord.setValue('documentType_id', toVariant(docTypeId))
                    docRecord.setValue('serial', toVariant(persData['docSerial']))
                    docRecord.setValue('number', toVariant(persData['docNumber']))
                    docRecord.setValue('client_id', toVariant(clientId))
                    self._db.insertRecord(tableClientDocument, docRecord)
            else:
                mekErrorList.append((u'5.2.2',
                                     u'Ошибки в персональных данных ЗЛ, приводящие к невозможности его идентификации',
                                     forceStringEx(patientElement.nodeName()),
                                     u'DOST'))
                return patientInfo

        policyKindCode = self.getElementValue(patientElement, 'VPOLIS', isRequired=True, mekErrorList=mekErrorList)
        policyNumber = self.getElementValue(patientElement, 'NPOLIS')
        policySerial = self.getElementValue(patientElement, 'SPOLIS')

        tablePolicy = self._db.table('ClientPolicy')
        policyKindId = self.getPolicyKindByCode(policyKindCode)
        insurerInfis = self.getElementValue(patientElement, 'SMO')
        insurerId = self._insurerCache.get(insurerInfis)
        # TODO: craz: очень хочется избавиться от этих костылей. Нормально настроенный ВМ сейчас не позволяет сохранить некорректные данные.
        if policyKindCode == '2' or len(policyNumber) == 9:
            policyNumber = policySerial + policyNumber
            policySerial = ''
        policyCond = [tablePolicy['client_id'].eq(clientId),
                      tablePolicy['serial'].like(policySerial),
                      tablePolicy['number'].like(policyNumber),
                      tablePolicy['policyKind_id'].eq(policyKindId),
                      tablePolicy['insurer_id'].eq(insurerId),
                      tablePolicy['policyType_id'].eq(self._policyTypeId)]

        policyRecord = self._db.getRecordEx(tablePolicy,
                                            cols=[tablePolicy['id'], tablePolicy['serial']],
                                            where=policyCond,
                                            order='id DESC')

        if not policyRecord:
            policyRecord = tablePolicy.newRecord()
            policyRecord.setValue('serial', toVariant(policySerial))
            policyRecord.setValue('number', toVariant(policyNumber))
            policyRecord.setValue('policyKind_id', toVariant(policyKindId))
            policyRecord.setValue('policyType_id', toVariant(self._policyTypeId))
            # noinspection PyArgumentList
            policyRecord.setValue('begDate', toVariant(QtCore.QDate.currentDate()))
            policyRecord.setValue('insurer_id', toVariant(insurerId))
            policyRecord.setValue('client_id', toVariant(clientId))
            self._db.insertRecord(tablePolicy, policyRecord)

        patientInfo['insurer'] = insurerInfis
        # FIXME: craz: перенесено временно из ImportR46XML. Переписать.
        self.processClientPolicyERZ(clientId, patientInfo)
            # mekErrorList.append((u'5.2.2', u'Ошибки в персональных данных ЗЛ, приводящие к невозможности его идентификации', None, None))
        mekErrorList.extend(persData['mekErrorList'])
        patientInfo['id'] = clientId
        patientInfo['sex'] = sex
        patientInfo['birthDate'] = birthDate
        patientInfo['idPac'] = idPac
        # patientInfo['littleStranger'] = novor

        return patientInfo


    def processClientPolicyERZ(self, clientId, patientInfo):
        record = selectLatestRecord('ClientPolicy', clientId)
        if not record:
            # self.logger().warning(u'Не удалось найти полис пациента {%s}' % clientId)
            return False

        # if forceString(record.value('note')) == 'erz':
        #     return 1

        db = self._db
        tableERZ = db.table('erz.erz')
        erzFields = [tableERZ['ENP'], tableERZ['OPDOC'], tableERZ['Q']]
        erzRecord = db.getRecordEx(tableERZ,
                                   cols=erzFields,
                                   where=tableERZ['ENP'].eq(record.value('number')))
        if erzRecord:
            record.setValue('note', toVariant('erz'))
            record.setValue('policyKind_id', toVariant(self.getPolicyKindByCode(forceStringEx(erzRecord.value('OPDOC')))))
            q = forceStringEx(erzRecord.value('Q'))
            if q:
                record.setValue('insurer_id', toVariant(self._insurerCache.get(q.strip(), None)))
            db.updateRecord('ClientPolicy', record)
            return 1

        client = db.table('Client')
        cd = db.table('ClientDocument')
        tbl = client.leftJoin(cd, cd['id'].eq('getClientDocumentId(Client.id)'))
        clientInfo = db.getRecordEx(tbl, [client['id'], client['notes'], client['lastName'], client['firstName'],
                                               client['patrName'], client['birthDate'], client['SNILS'], cd['serial'],
                                               cd['number']],
                                    client['id'].eq(clientId))
        found = False
        if forceStringEx(clientInfo.value('SNILS')):
            erzRecord = db.getRecordEx(tableERZ, erzFields, tableERZ['SS'].eq(clientInfo.value('SNILS')))
            if erzRecord: found = True

        if not found and not forceDate(clientInfo.value('birthDate')).isNull():
            erzRecord = db.getRecordEx(tableERZ, erzFields, [tableERZ['FAM'].eq(clientInfo.value('lastName')),
                                                        tableERZ['IM'].eq(clientInfo.value('firstName')),
                                                        tableERZ['OT'].eq(clientInfo.value('patrName')),
                                                        tableERZ['DR'].eq(clientInfo.value('birthDate'))])
            if erzRecord: found = True

        docs = forceStringEx(clientInfo.value('serial'))
        docn = forceStringEx(clientInfo.value('number'))
        if not found and forceStringEx(clientInfo.value('number')):
            erzRecord = db.getRecordEx(tableERZ, erzFields, [tableERZ['DOCN'].eq(docn),
                                                        tableERZ['DOCS'].eq(docs)])
            if erzRecord: found = True

        if not found and docn and docs:
            erzRecord = db.getRecordEx(tableERZ, erzFields, [tableERZ['DOCN'].eq(docs+docn),
                                                        tableERZ['DOCS'].isNotNull()])
            if erzRecord: found = True

        pols = forceStringEx(record.value('serial'))
        poln = forceStringEx(record.value('number'))

        if not found and pols and poln:
            erzRecord = db.getRecordEx(tableERZ, erzFields, [tableERZ['NPOL'].eq(pols + poln),
                                                        tableERZ['SPOL'].isNull()])
            if erzRecord: found = True

        if not found:
            # self.logger().warning(u'Не удалось найти пациента {%s} в ЕРЗ.' % clientId)
            return False

        insurerInfis = forceStringEx(erzRecord.value('Q'))
        insurerId = self._insurerCache.get(insurerInfis,
                                           0)
        newRecord = db.table('ClientPolicy').newRecord()
        newRecord.setValue('client_id', toVariant(clientId))
        newRecord.setValue('insurer_id', toVariant(insurerId))
        newRecord.setValue('policyKind_id', toVariant(self.getPolicyKindByCode(forceStringEx(erzRecord.value('OPDOC')))))
        newRecord.setValue('policyType_id', toVariant(self._policyTypeId)) #self.policyTypeTerritorial))
        newRecord.setValue('serial', toVariant(''))
        newRecord.setValue('number', erzRecord.value('ENP'))
        newRecord.setValue('note', toVariant('erz'))
        db.insertRecord('ClientPolicy', newRecord)

        patientInfo['insurer'] = insurerInfis
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
        super(CImportDialog, self).__init__(parent)
        self._db = db
        self._pi = CProgressInformer(processEventsFlag=QtCore.QEventLoop.AllEvents)
        self._engine = CImportR85DDTFEngine(db, orgId, progressInformer=self._pi) #TODO?
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
        self._loggerHandler.logged.connect(self.logInfo.append)

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
        self.setWindowTitle(forceTr(u'Импорт. Крым. ТФОМС. Диспансеризация.', context))
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
            except:
                self.currentState = self.InitState
                raise
            self.currentState = self.InitState

        elif self.currentState == self.ImportState:
            self._engine.abort()
            self.currentState = self.InitState
        self.onStateChanged()


    # noinspection PyMethodMayBeStatic
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


    # noinspection PyTypeChecker
    @QtCore.pyqtSlot()
    def onBrowseFileClicked(self):
        fileName = forceStringEx(QtGui.QFileDialog.getOpenFileName(self,
                                                                       u'Укажите директорию для сохранения файлов выгрузки',
                                                                       self.edtFileName.text(),
                                                                       u'Файлы (DP*.zip)'))
        if os.path.isfile(fileName):
            self.edtFileName.setText(fileName)

def main():
    import sys
    from library.database import connectDataBaseByInfo
    app = QtGui.QApplication(sys.argv)
    # noinspection PyCallByClass
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    # isTestExport = False

    connectionInfo = {'driverName' : 'mysql',
                      'host' : '192.168.0.3',
                      'port' : 3306,
                      'database' : 'crimeaMar_2405',
                      'user' : 'dbuser',
                      'password' : 'dbpassword',
                      'connectionName' : 'vista-med',
                      'compressData' : True,
                      'afterConnectFunc' : None}
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)
    db = QtGui.qApp.db
    tblAccount = db.table('Account')
    accounts = db.getIdList('Account', where=tblAccount['settleDate'].dateGe(QtCore.QDate(2015, 5, 15)))
    from Accounting.Utils import updateAccounts
    updateAccounts(accounts)
    # if isTestExport:
    #     accountId = 248 #253
    #     w = CExportDialog(QtGui.qApp.db, accountId)
    #     w.show()
    # else:
    #     from Exchange.R85.ImportR85MTR import CImportR85MTREngine
    #     e = CImportR85MTREngine(QtGui.qApp.db)
    #     e.processFile(u'/home/atronah/R2285152908.XML')
    # d = CImportDialog(QtGui.qApp.db, 0)
    # d.exec_()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()