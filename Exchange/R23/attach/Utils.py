# -*- coding: utf-8 -*-

from PyQt4 import QtGui

from library.Enum import CEnum
from library.LoggingModule.Logger import getLoggerDbName
from library.Utils import forceBool, forceInt, forceRef, forceString, nameCase, unformatSNILS


class CInsuranceArea(CEnum):
    u""" Территория страхования (по ClientPolicy.insuranceArea) """
    Any = 0
    Krasnodar = 1
    NonKrasnodar = 2

    nameMap = {
        Any         : u'Не задано',
        Krasnodar   : u'Краевые',
        NonKrasnodar: u'Инокраевые'
    }


class CAttachType(CEnum):
    u""" Тип прикрепления (rbAttachType.code) """
    Any = 0
    byResidentPlace = 1
    byApplication = 2

    nameMap = {
        Any            : u'',
        byResidentPlace: u'Первичное',
        byApplication  : u'По заявлению'
    }


class CAttachPolicyType(CEnum):
    u""" Тип полиса (по rbPolicyKind.code, rbPolicyType.code) """
    NotSet = 0
    Old = 1
    Temporary = 2
    New = 3
    Electronic = 4
    UEK = 5

    nameMap = {
        NotSet    : u'',
        Old       : u'Полис ОМС старого образца',
        Temporary : u'Временное свидетельство',
        New       : u'Полис ОМС единого образца',
        Electronic: u'Электронный полис ОМС единого образца',
        UEK       : u'Полис ОМС в составе УЭК'
    }


class CDocumentType(object):
    _codeNameMap = {}

    @classmethod
    def getCodeNameMap(cls):
        if cls._codeNameMap:
            return cls._codeNameMap

        cls._codeNameMap = {}
        db = QtGui.qApp.db
        DocType = db.table('rbDocumentType')
        DocTypeGroup = db.table('rbDocumentTypeGroup')

        table = DocType.innerJoin(DocTypeGroup, DocTypeGroup['id'].eq(DocType['group_id']))

        for rec in QtGui.qApp.db.getRecordList(table, [DocType['code'], DocType['name']], DocTypeGroup['code'].eq('1')):
            cls._codeNameMap[forceInt(rec.value('code'))] = forceString(rec.value('name'))

        return cls._codeNameMap


class CAttachedClientInfoSyncStatus(CEnum):
    u""" Статус синхронизации прикрепления пациента (импорт из ТФОМС) """
    Loaded = 0
    Deattach_Synced = 1
    Deattach_AlreadyDeattached = 2
    Deattach_NoAttach = 3
    Attach_Synced = 4
    Attach_NotMatch = 5
    Attach_Created = 6
    Attach_Deattached = 7
    Deattach_NotDeattached = 8
    Client_NotFound = 9
    Client_FoundDouble = 10

    NotSynced = 11  # Для того, чтобы выбрать записи с несколькими статусами:
    notSyncedList = [
        Loaded,
        Deattach_NoAttach,
        Attach_NotMatch,
        Deattach_NotDeattached,
        Client_NotFound,
        Client_FoundDouble
    ]

    nameMap = {
        Loaded                    : u'Загружено, не синхронизировано',
        Deattach_Synced           : u'Открепление синхронизировано',
        Deattach_AlreadyDeattached: u'Пациент уже откреплен',
        Deattach_NoAttach         : u'Не откреплен: нет прикрепления',
        Attach_Synced             : u'Прикрепление синхронизировано',
        Attach_NotMatch           : u'Прикрепление в БД не соотвествует присланному',
        Attach_Created            : u'Прикрепление создано (по данным ТФОМС)',
        Attach_Deattached         : u'Пациент откреплен (по данным ТФОМС)',
        Deattach_NotDeattached    : u'Пациент не откреплен',  # (причина != смерть, при выставленном чекбоксе "откреплять только умерших")
        Client_NotFound           : u'Пациент не найден в БД',
        Client_FoundDouble        : u'Пациент не найден: есть двойник',
        NotSynced                 : u'Все несинхронизированные'
    }


class CClientAttachFound(CEnum):
    u""" Пациент/прикрепление найдены в БД (импорт из ТФОМС) """
    Any = 0
    Found = 1
    NotFound = 2

    nameMap = {
        Any     : u'Не задано',
        Found   : u'Есть в БД',
        NotFound: u'Нет в БД'
    }


class CAttachSentToTFOMS(CEnum):
    u""" Статус синхронизации прикрепления с ТФОМС (экспорт в ТФОМС) (ClientAttach.sentToTFOMS / PersonAttach.sentToTFOMS) """
    NotSynced = 0
    Synced = 1
    Deattach_OnCreate = 2
    Deattach_ByTFOMS = 3

    visibleInClientBanner = (NotSynced, Synced, Deattach_ByTFOMS)

    nameMap = {
        NotSynced        : u'Не синхронизировано',
        Synced           : u'Синхронизировано',
        Deattach_OnCreate: u'Закрыто при добавлении нового прикрепления',
        Deattach_ByTFOMS : u'Закрыто по информации из ТФОМС'
    }

    @staticmethod
    def getBannerMessage(sentToTFOMS):
        return CAttachSentToTFOMS.nameMap[sentToTFOMS] if sentToTFOMS in CAttachSentToTFOMS.visibleInClientBanner else u''


class CAttachReason(CEnum):
    u""" Признак прикрепления """
    ByApplication = 0
    ByResidentPlace = 1

    nameMap = {
        ByApplication  : u'По заявлению',
        ByResidentPlace: u'По месту жительства'
    }


class CDeAttachReason(CEnum):
    u""" Причина открепления (rbDetachmentReason.code) """
    ChangeAddress = 1
    ClientDeath = 2
    ChangeOrg = 3
    ChangeSection = 4
    ChangeOrgByAge = 11
    DeattachQuery = 12

    nameMap = {
        ChangeAddress : u'Cмена места жительства',
        ClientDeath   : u'Смерть',
        ChangeOrg     : u'Замена МО',
        ChangeSection : u'Смена участка внутри МО',
        ChangeOrgByAge: u'Смена МО в связи с возрастом',
        DeattachQuery : u'Уведомление о прикреплении к МО другого субъекта РФ'
    }


class CPersonCategory(CEnum):
    u""" Категория персонала (по rbSpeciality.federalCode) """
    Any = 0
    Doctor = 1
    NursingStaff = 2

    nameMap = {
        Any         : u'',
        Doctor      : u'Врач',
        NursingStaff: u'Средний медицинский персонал'
    }


class CDeAttachQueryCounter(object):
    code = 'deattach'
    counterId = None

    @classmethod
    def getId(cls):
        if cls.counterId is None:
            cls.counterId = forceRef(QtGui.qApp.db.translate('rbCounter', 'code', cls.code, 'id'))
        return cls.counterId

    @classmethod
    def getValue(cls):
        db = QtGui.qApp.db
        rec = db.selectExpr(db.func.getCounterValue(cls.getId()))
        return forceInt(rec.value(0)) if rec else 0


class CTemporaryTable(object):
    _tableName = 'tmp_table'
    _tableInitialized = False

    @classmethod
    def getTableName(cls):
        return cls._tableName

    @classmethod
    def initTable(cls):
        raise NotImplementedError

    @classmethod
    def clear(cls, *args):
        if cls._tableInitialized:
            db = QtGui.qApp.db
            db.deleteRecord(db.table(cls._tableName), None)
        else:
            cls.initTable()


class CBookkeeperCode(CTemporaryTable):
    _tableName = 'tmp_orgStructure_bookkeeperCode'
    _tableInitialized = False
    _codeMap = {}  # orgStructureId -> (orgCode, sectionCode)
    _internalCodes = set()
    _orgStructureMap = {}  # (orgCode, sectionCode) -> (orgId, orgStructureId)

    @classmethod
    def getTableName(cls):
        if not cls._tableInitialized:
            cls.initTable()
        return cls._tableName

    @classmethod
    def getOrgCode(cls, orgStructureId):
        if not cls._tableInitialized:
            cls.initTable()
        return cls._codeMap.get(orgStructureId, (None, None))

    @classmethod
    def getInternalCodes(cls):
        if not cls._tableInitialized:
            cls.initTable()
        return cls._internalCodes

    @classmethod
    def isExternalOrgCode(cls, orgCode):
        if not cls._tableInitialized:
            cls.initTable()
        return orgCode not in cls._internalCodes

    @classmethod
    def getOrgStructure(cls, orgCode, sectionCode):
        if not cls._tableInitialized:
            cls.initTable()
        return cls._orgStructureMap.get((orgCode, sectionCode), (None, None))

    @classmethod
    def initTable(cls):
        db = QtGui.qApp.db

        createStmt = u"""
        DROP TABLE IF EXISTS {tableName};
        CREATE TABLE IF NOT EXISTS {tableName} AS (
          SELECT
            id             AS id,
            parent_id      AS master_id,
            bookkeeperCode AS orgCode
          FROM OrgStructure
          WHERE deleted = 0 AND organisation_id = {orgId}
        );
        ALTER TABLE {tableName} ADD UNIQUE INDEX (`id`), ADD INDEX (`master_id`);
        """.format(tableName=cls._tableName,
                   orgId=QtGui.qApp.currentOrgId())

        updateStmt = u"""
        UPDATE {tableName} t
        LEFT JOIN {tableName} t1 ON t1.id = t.master_id
        LEFT JOIN {tableName} t2 ON t2.id = t1.master_id
        SET t.orgCode = IF(t1.orgCode = "", t2.orgCode, t1.orgCode),
            t.master_id = IF(t1.orgCode = "", t2.id, t1.id)
        WHERE t.orgCode = ""
        """.format(tableName=cls._tableName)

        db.query(createStmt)
        updated = -1
        while updated != 0:
            query = db.query(updateStmt)
            updated = query.numRowsAffected()
        cls._tableInitialized = True

        tableBookkeeper = db.table(cls._tableName)
        tableOrgStructure = db.table('OrgStructure')

        queryTable = tableOrgStructure.innerJoin(tableBookkeeper, tableBookkeeper['id'].eq(tableOrgStructure['id']))
        cols = [
            tableBookkeeper['id'].alias('id'),
            tableBookkeeper['orgCode'].alias('orgCode'),
            tableOrgStructure['infisInternalCode'].alias('sectionCode'),
            tableOrgStructure['organisation_id'].alias('orgId')
        ]

        cls._codeMap = {}
        cls._orgStructureMap = {}
        for rec in db.iterRecordList(queryTable, cols):
            cls._codeMap[forceRef(rec.value('id'))] = (forceString(rec.value('orgCode')), forceString(rec.value('sectionCode')))
            cls._orgStructureMap[(forceString(rec.value('orgCode')),
                                  forceString(rec.value('sectionCode')))] = (forceRef(rec.value('orgId')),
                                                                             forceRef(rec.value('id')))

        cls._internalCodes = set(orgCode for orgCode, sectionCode in cls._codeMap.itervalues())


class CAttachedInfoTable(CTemporaryTable):
    _tableName = 'AttachedClientInfo'
    _tableInitialized = False

    @classmethod
    def initTable(cls, senderCode=None):
        db = QtGui.qApp.db
        table = db.table(cls._tableName)
        if senderCode:
            cond = db.joinOr([
                table['senderCode'].eq(''),
                table['senderCode'].eq(senderCode)
            ])
        else:
            cond = [
                table['senderCode'].eq('')
            ]
        db.deleteRecord(table, cond)

        cls._tableInitialized = True

    @classmethod
    def insertAttaches(cls, attachInfoList, senderCode):
        u"""
        Вставка в AttachedClientInfo списков прикрепленных/открепленных из ТФОМС
        :param attachInfoList: [list of AttachedClientIfno]
        :param senderCode: OrgStructure.bookkeeperCode подраздления, загружающего списки
        """

        if not cls._tableInitialized:
            cls.initTable()

        def formatAddr(a):
            if not a: return u''
            l = a.split()
            if len(l) > 1:
                return u' '.join(map(nameCase, l[:-1]) + [l[-1].lower()])
            return nameCase(a)

        def asDict(c):
            u"""
            :type c: Exchange.R23.attach.Types.AttachedClientInfo
            :rtype: dict
            """
            ra = c.regAddress
            la = c.locAddress
            return {
                'senderCode'    : senderCode,

                'lastName'      : c.lastName,
                'firstName'     : c.firstName,
                'patrName'      : c.patrName,
                'birthDate'     : c.birthDate,
                'SNILS'         : unformatSNILS(c.SNILS),

                'docType'       : c.document.type,
                'docSerial'     : c.document.serial,
                'docNumber'     : c.document.number,

                'policyType'    : c.policy.type,
                'policySerial'  : c.policy.serial,
                'policyNumber'  : c.policy.number,
                'insurerCode'   : c.policy.insurerCode,

                'begDate'       : c.attach.begDate,
                'endDate'       : c.attach.endDate,
                'orgCode'       : c.attach.orgCode,
                'sectionCode'   : c.attach.sectionCode,
                'doctorSNILS'   : unformatSNILS(c.attach.doctorSNILS),
                'attachType'    : c.attach.attachType or 0,
                'deattachReason': c.attach.deattachReason or 0,

                'regDistrict'   : formatAddr(ra.district),
                'regCity'       : formatAddr(ra.city),
                'regLocality'   : formatAddr(ra.locality),
                'regStreet'     : formatAddr(ra.street),
                'regHouse'      : formatAddr(ra.house.upper()),
                'regCorpus'     : formatAddr(ra.corpus.upper()),
                'regFlat'       : ra.flat,

                'locDistrict'   : formatAddr(la.district),
                'locCity'       : formatAddr(la.city),
                'locLocality'   : formatAddr(la.locality),
                'locStreet'     : formatAddr(la.street),
                'locHouse'      : formatAddr(la.house.upper()),
                'locCorpus'     : formatAddr(la.corpus.upper()),
                'locFlat'       : la.flat
            }

        QtGui.qApp.db.insertFromDictList(cls._tableName, map(asDict, attachInfoList), chunkSize=500)

    @classmethod
    def updateField(cls, values, fieldName):
        u"""
        Обновляем AttachedClientInfo.fieldName
        :param values: [list of tuple(id, fieldValue)]
        :param fieldName: обновляемое поле
        """
        updFields = [fieldName]
        QtGui.qApp.db.insertValues(cls._tableName, ['id'] + updFields, values, updateFields=updFields)

    @classmethod
    def closeAttaches(cls, idList, closeAll=True):
        u"""
        Закрывем ВСЕ действующие прикрепления пациента датой MAX((дата нового прикрепления - 1 день), (датой старого прикрепления))
        :param idList: [list of AttachedClientInfo.id]
        :param closeAll: закрываем все прикрепления (при добавлении нового из ТФОМС)
                         или все кроме AttachedClientInfo.attach_id (прикрепление из ТФОМС найдено в БД)
        """
        if not idList: return

        db = QtGui.qApp.db
        tableACI = db.table('AttachedClientInfo')
        tableClientAttach = db.table('ClientAttach')

        attachCond = [
            tableClientAttach['client_id'].eq(tableACI['client_id']),
            tableClientAttach['endDate'].isNull(),
            tableClientAttach['deleted'].eq(0)
        ]
        if not closeAll:
            attachCond.append(tableClientAttach['id'].ne(tableACI['attach_id']))

        table = tableACI.innerJoin(tableClientAttach, attachCond)
        db.insertFromSelect(tableClientAttach,
                            table,
                            {
                                'id'         : tableClientAttach['id'],
                                'sentToTFOMS': db.valueField(CAttachSentToTFOMS.Deattach_OnCreate),
                                'errorCode'  : db.valueField(''),
                                'endDate'    : db.if_(tableClientAttach['begDate'].lt(tableACI['begDate']),
                                                      db.subDate(tableACI['begDate'], 1, 'DAY'),
                                                      tableClientAttach['begDate'])
                            },
                            tableACI['id'].inlist(idList),
                            excludeFields=['id'])

    @classmethod
    def createAttaches(cls, idList):
        u"""
        Добавляем прикрепления в БД (по информации из ТФОМС)
        :param idList: [list of AttachedClientInfo.id]
        """
        if not idList: return

        db = QtGui.qApp.db
        tableACI = db.table('AttachedClientInfo')
        tableClientAttach = db.table('ClientAttach')
        tableAttachType = db.table('rbAttachType')
        tableOrgStructure = db.table('OrgStructure')

        table = tableACI.leftJoin(tableAttachType, tableAttachType['code'].eq(tableACI['attachType']))
        table = table.leftJoin(tableOrgStructure, tableOrgStructure['id'].eq(tableACI['orgStructure_id']))

        db.insertFromSelect(tableClientAttach,
                            table,
                            {
                                'client_id'      : tableACI['client_id'],
                                'begDate'        : tableACI['begDate'],
                                'orgStructure_id': tableACI['orgStructure_id'],
                                'attachType_id'  : tableAttachType['id'],
                                'LPU_id'         : tableOrgStructure['organisation_id'],
                                'sentToTFOMS'    : db.valueField(CAttachSentToTFOMS.Synced)
                            },
                            tableACI['id'].inlist(idList))

    @classmethod
    def attachByTFOMS(cls, idList):
        u"""
        Добавляем прикрепления в БД (по информации из ТФОМС), закрываем существующие
        :param idList: [list of AttachedClientInfo.id]
        """
        if not idList: return
        cls.closeAttaches(idList)
        cls.createAttaches(idList)

    @classmethod
    def deattachByTFOMS(cls, idList):
        u"""
        Открепляем пациентов по данным ТФОМС
        :param idList: [list of AttachedClientInfo.id]
        """
        if not idList: return

        db = QtGui.qApp.db
        tableACI = db.table('AttachedClientInfo')
        tableClientAttach = db.table('ClientAttach')

        table = tableACI.innerJoin(tableClientAttach, [tableClientAttach['id'].eq(tableACI['attach_id']),
                                                       tableClientAttach['deleted'].eq(0)])
        db.insertFromSelect(tableClientAttach,
                            table,
                            {
                                'id'         : tableClientAttach['id'],
                                'endDate'    : tableACI['endDate'],
                                'sentToTFOMS': db.valueField(CAttachSentToTFOMS.Deattach_ByTFOMS),
                                'errorCode'  : db.valueField('')
                            },
                            tableACI['id'].inlist(idList),
                            excludeFields=['id'])


    @classmethod
    def deattachOnDeath(cls, idList, deathAttachTypeId):
        u"""
        Открепляем пациентов (по причине смерти):
        :param idList: [list of AttachedClientInfo.id]
        :param deathAttachTypeId: rbAttachType.id (смерть)
        """
        if not idList: return

        db = QtGui.qApp.db
        tableACI = db.table('AttachedClientInfo')
        tableAttachType = db.table('rbAttachType')
        tableClientAttach = db.table('ClientAttach')
        tableOrgStructure = db.table('OrgStructure')

        cond = db.joinAnd([
            tableACI['id'].inlist(idList),
            tableACI['client_id'].isNotNull()
        ])

        # 1. Закрываем существующие открытые прикрепления полученной датой открепления
        table = tableACI.innerJoin(tableClientAttach, [tableClientAttach['client_id'].eq(tableACI['client_id']),
                                                       tableClientAttach['endDate'].isNull(),
                                                       tableClientAttach['deleted'].eq(0)])
        db.insertFromSelect(tableClientAttach,
                            table,
                            {
                                'id'     : tableClientAttach['id'],
                                'endDate': tableACI['endDate'],
                            },
                            cond)

        # 2. Все закрытые прикрепления отмечаем как синхронизированные
        table = tableACI.innerJoin(tableClientAttach, [tableClientAttach['client_id'].eq(tableACI['client_id']),
                                                       tableClientAttach['endDate'].isNotNull(),
                                                       tableClientAttach['deleted'].eq(0)])
        table = table.innerJoin(tableAttachType, [tableAttachType['id'].eq(tableClientAttach['attachType_id']),
                                                  tableAttachType['code'].inlist(['1', '2'])])

        db.insertFromSelect(tableClientAttach,
                            table,
                            {
                                'id'         : tableClientAttach['id'],
                                'sentToTFOMS': CAttachSentToTFOMS.Synced,
                                'errorCode'  : db.valueField('')
                            },
                            cond)

        # 3. Добавляем прикрепление с типом "Смерть"
        table = tableACI.leftJoin(tableOrgStructure, tableOrgStructure['id'].eq(tableACI['orgStructure_id']))

        db.insertFromSelect(tableClientAttach,
                            table,
                            {
                                'client_id'      : tableACI['client_id'],
                                'attachType_id'  : db.valueField(deathAttachTypeId),
                                'begDate'        : tableACI['begDate'],
                                'endDate'        : tableACI['endDate'],
                                'orgStructure_id': tableACI['orgStructure_id'],
                                'LPU_id'         : tableOrgStructure['organisation_id'],
                                'sentToTFOMS'    : db.valueField(CAttachSentToTFOMS.Synced)
                            },
                            cond)


def attachServiceEnabled():
    u""" Сервис 'Прикрепленное население' автивирован в настройках """
    return forceBool(QtGui.qApp.preferences.appPrefs.get('AttachCheckPolicy', 'False'))


def syncAttachesOnSave():
    u""" Отправлять прикрепления пациентов/врачей при сохранении амб. карты/карты сотрудника """
    return attachServiceEnabled() and \
           forceBool(QtGui.qApp.preferences.appPrefs.get('TransmitAttachData', 'False'))


def getAttachLogTable():
    u""" Таблица для логгирования статусов синхронизации прикреплений с ТФОМС """
    return '{logger}.AttachLog'.format(logger=getLoggerDbName())


def getDeAttachQueryLogTable():
    u""" Таблица для логгирования исходящих запросов на открепление (от одного МО к другому) """
    return '{logger}.DeAttachQueryLog'.format(logger=getLoggerDbName())


def insertDeAttachQueryLog(values):
    fields = ['client_id', 'attach_id', 'number', 'srcMO', 'destMO', 'date', 'sentToTFOMS']
    QtGui.qApp.db.insertValues(getDeAttachQueryLogTable(), fields, values)


def insertAttachLog(clientId, status, datetime):
    db = QtGui.qApp.db
    table = db.table(getAttachLogTable())
    db.insertValues(table, fields=['client_id', 'sendDate', 'status'], values=[(clientId, datetime, status)])


def insertAttachLogValues(values, syncDatetime):
    u""" Логгирование статусов синхронизации прикреплений в logger.AttachLog
    :param values: list of tuple(clientId, status)
    :param syncDatetime: QDateTime - дата-время синхронизации
    """
    db = QtGui.qApp.db
    table = db.table(getAttachLogTable())
    db.insertValues(table,
                    fields=['client_id', 'sendDate', 'status'],
                    values=[(clientId, syncDatetime, status) for (clientId, status) in values])


def setClientAttachesSynced(idList):
    u"""
    Пометить прикрепления как синхронизированные с ТФОМС
    :param idList: list of ClientAttach.id
    """
    if not idList: return
    db = QtGui.qApp.db
    table = db.table('ClientAttach')
    db.updateRecords(table,
                     expr=[
                         table['sentToTFOMS'].eq(CAttachSentToTFOMS.Synced),
                         table['errorCode'].eq('')
                     ],
                     where=table['id'].inlist(idList))


def findClient(client):
    u"""
    Поиск пациента в БД по информации, полученной от ТФОМС
    :param client: AttachedClientInfo
    :return: tuple(bool, [list of Client.id])
    """
    db = QtGui.qApp.db
    Client = db.table('Client')
    ClientDocument = db.table('ClientDocument')
    ClientPolicy = db.table('ClientPolicy')

    table = Client
    cond = [
        Client['lastName'].eq(client.lastName),
        Client['firstName'].eq(client.firstName),
        Client['birthDate'].eq(client.birthDate),
        Client['deleted'].eq(0)
    ]
    additionaLCond = [
        Client['patrName'].eq(client.patrName),
        db.joinOr([
            ClientDocument['number'].eq(client.document.number),
            ClientPolicy['number'].eq(client.policy.number)
        ])
    ]

    idList = db.getDistinctIdList(table, Client['id'], cond)
    if len(idList) > 1:
        table = table.leftJoin(ClientDocument, [ClientDocument['client_id'].eq(Client['id']), ClientDocument['deleted'].eq(0)])
        table = table.leftJoin(ClientPolicy, [ClientPolicy['client_id'].eq(Client['id']), ClientPolicy['deleted'].eq(0)])
        for addCond in additionaLCond:
            cond.append(addCond)
            idList = db.getDistinctIdList(table, Client['id'], cond)
            if len(idList) <= 1:
                break

    return (True, idList) if len(idList) == 1 else (False, idList)


def findClientAttach(clientId, orgCode=None, sectionCode=None, endDate=None, attachType=None, toDeAttach=False):
    db = QtGui.qApp.db
    ClientAttach = db.table('ClientAttach')
    AttachType = db.table('rbAttachType')

    table = ClientAttach.leftJoin(AttachType, AttachType['id'].eq(ClientAttach['attachType_id']))

    cond = [
        ClientAttach['client_id'].eq(clientId),
        ClientAttach['deleted'].eq(0)
    ]
    orgId, orgStructureId = CBookkeeperCode.getOrgStructure(orgCode, sectionCode)
    if orgStructureId:
        cond.append(ClientAttach['orgStructure_id'].eq(orgStructureId))

    if toDeAttach and endDate is not None:
        cond.append(ClientAttach['begDate'].dateLe(endDate))
    else:
        cond.extend([
            ClientAttach['endDate'].isNull(),
            AttachType['code'].eq(attachType)
        ])

    record = db.getRecordEx(table, ClientAttach['id'].alias('id'), cond)
    return forceRef(record.value('id')) if record else None
