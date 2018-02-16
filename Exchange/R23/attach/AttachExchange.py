# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Exchange.R23.attach.Service import CR23ClientAttachService
from Exchange.R23.attach.Types import AttachError, AttachInfo, AttachResult, AttachedClientInfo, DeAttachQuery, \
    DoctorSectionInfo, DocumentInfo, \
    PersonAttachInfo, PolicyInfo
from Exchange.R23.attach.Utils import CAttachSentToTFOMS, CAttachedClientInfoSyncStatus, CAttachedInfoTable, \
    CBookkeeperCode, \
    CDeAttachQueryCounter, CDeAttachReason, insertDeAttachQueryLog
from Orgs.Utils import getOrgStructureDescendants, CAttachType
from library.Utils import CChunkProcessor, forceBool, forceDate, forceInt, forceRef, forceString, formatSNILS, nameCase, formatSex
from library.exception import CSynchronizeAttachException


class CR23AttachExchange(object):
    SyncChunkSize = 500  # Груупировка запросов к ТФОМС на прикрепление/открепление
    InsertChunkSize = 500  # Группировка запросов к БД

    def __init__(self, db):
        super(CR23AttachExchange, self).__init__()
        self.db = db
        self.orgId = QtGui.qApp.currentOrgId()
        self.userId = QtGui.qApp.userId

    def getAttachedToOrgStructure(self, orgStructureId, sex=None, ageCategory=None, limit=None, withDescendants=False):
        u""" Список пациентов, прикрепленных к подразделению """
        db = self.db
        tableAttachType = db.table('rbAttachType')
        tableClient = db.table('Client')
        tableClientAttach = db.table('ClientAttach')

        table = tableClientAttach.innerJoin(tableAttachType, tableAttachType['id'].eq(tableClientAttach['attachType_id']))
        table = table.innerJoin(tableClient, [tableClient['id'].eq(tableClientAttach['client_id']),
                                              tableClient['deleted'].eq(0)])
        cond = [
            tableClientAttach['endDate'].isNull(),
            tableClientAttach['deleted'].eq(0),
            tableAttachType['code'].eq(CAttachType.Territorial),
        ]
        if withDescendants:
            cond.append(tableClientAttach['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
        else:
            cond.append(tableClientAttach['orgStructure_id'].eq(orgStructureId))
        if sex:
            cond.append(tableClient['sex'].eq(sex))
        if ageCategory:
            clientAge = db.func.age(tableClient['birthDate'], db.curdate())
            if ageCategory == 1:
                cond.append(clientAge < 18)
            elif ageCategory == 2:
                cond.append(clientAge >= 18)
        order = [
            tableClientAttach['id']
        ]
        return db.getDistinctIdList(table, tableClient['id'], cond, order=order, limit=limit)

    def _closeAttaches(self, clientIdList, date=None):
        u""" Закрытие открытых прикреплений пациентов """
        tableClientAttach = self.db.table('ClientAttach')
        cond = [
            tableClientAttach['client_id'].inlist(clientIdList),
            tableClientAttach['deleted'].eq(0),
            tableClientAttach['endDate'].isNull()
        ]
        expr = [
            tableClientAttach['endDate'].eq(date if date is not None else QtCore.QDate.currentDate().addDays(-1)),
            tableClientAttach['sentToTFOMS'].eq(CAttachSentToTFOMS.NotSynced)
        ]
        self.db.updateRecords(tableClientAttach, expr=expr, where=cond)

    def _attachClientsToOrgStructure(self, clientIdList, orgStructureId, attachTypeId):
        u""" Создание новых прикреплений к участку """
        tableClientAttach = self.db.table('ClientAttach')
        newAttaches = [{
            'createDatetime' : self.db.now(),
            'createPerson_id': self.userId,
            'client_id'      : clientId,
            'attachType_id'  : attachTypeId,
            'LPU_id'         : self.orgId,
            'orgStructure_id': orgStructureId,
            'begDate'        : self.db.curdate(),
            'sentToTFOMS'    : CAttachSentToTFOMS.NotSynced
        } for clientId in clientIdList]
        self.db.insertFromDictList(tableClientAttach, newAttaches)

    def moveAttachesToOrgStructure(self, clientIdList, orgStructureId):
        u""" Перенос прикреплений на участок """
        chunkSize = 500
        attachTypeId = CAttachType.getAttachTypeId(CAttachType.Territorial)

        for offset in range(0, len(clientIdList), chunkSize):
            idList = clientIdList[offset: offset + chunkSize]
            self._closeAttaches(idList)
            self._attachClientsToOrgStructure(idList, orgStructureId, attachTypeId)

    @classmethod
    def getPolicyType(cls, policyKindId):
        u""" ClientPolicy.policyKind_id -> PolicyInfo.type """
        return forceInt(QtGui.qApp.db.translate('rbPolicyKind', 'id', policyKindId, 'regionalCode'))

    @classmethod
    def getDocumentType(cls, documentTypeId):
        u""" ClientDocument.documentType_id -> DocumentInfo.type """
        return forceInt(QtGui.qApp.db.translate('rbDocumentType', 'id', documentTypeId, 'code'))

    @classmethod
    def getInsurerInfo(cls, insurerId):
        u""" ClientPolicy.insurer_id -> (PolicyInfo.insurerCode, PolicyInfo.insurerOKATO) """
        db = QtGui.qApp.db
        tableInsurer = db.table('Organisation').alias('Insurer')
        tableInsurerHead = db.table('Organisation').alias('InsurerHead')

        rec = db.getRecordEx(table=tableInsurer.leftJoin(tableInsurerHead, [tableInsurerHead['id'].eq(tableInsurer['head_id']),
                                                                            tableInsurerHead['deleted'].eq(0)]),
                             cols=[
                                 tableInsurer['miacCode'].alias('insurerCode'),
                                 db.if_(tableInsurer['head_id'].isNull(),
                                        tableInsurer['OKATO'],
                                        tableInsurerHead['OKATO']).alias('insurerOKATO')
                             ],
                             where=tableInsurer['id'].eq(insurerId))

        return (forceString(rec.value('insurerCode')), forceString(rec.value('insurerOKATO'))) if rec is not None else (None, None)

    @classmethod
    def getAttachTypeInfo(cls, attachTypeId):
        u""" ClientAttach.attachType_id -> (AttachInfo.attachType, AttachInfo.attachReason) """
        rec = QtGui.qApp.db.getRecord('rbAttachType', ['code', 'name'], attachTypeId)
        if rec is not None:
            typeCode = forceInt(rec.value('code'))
            reason = 1 if (u'по месту жительства' in forceString(rec.value('name')).lower()) else 0
            return typeCode, reason

        return None, None

    @classmethod
    def getDeAttachReason(cls, detachmentId):
        u""" ClientAttach.detachment_id -> AttachType.deattachReason """
        deattachReasonCode = forceInt(QtGui.qApp.db.translate('rbDetachmentReason', 'id', detachmentId, 'code'))
        return deattachReasonCode if deattachReasonCode in CDeAttachReason.nameMap else CDeAttachReason.ChangeOrg

    @classmethod
    def getDoctorSectionInfo(cls, orgStructureId):
        u"""
        Текущий сотрудник на участке
        :param orgStructureId: OrgStructure.id
        :return: DoctorSectionInfo
        """
        db = QtGui.qApp.db
        tablePerson = db.table('Person')
        tablePersonAttach = db.table('PersonAttach')
        tableOrgStructure = db.table('OrgStructure')

        queryTable = tableOrgStructure.innerJoin(tablePersonAttach, [tablePersonAttach['orgStructure_id'].eq(tableOrgStructure['id']),
                                                                     tablePersonAttach['endDate'].isNull(),
                                                                     tablePersonAttach['deleted'].eq(0)])
        queryTable = queryTable.innerJoin(tablePerson, [tablePerson['id'].eq(tablePersonAttach['master_id']),
                                                        tablePerson['deleted'].eq(0)])

        cols = [
            tablePerson['id'].alias('doctorId'),
            tablePerson['SNILS'].alias('doctorSNILS'),
            tablePersonAttach['id'].alias('id'),
            tablePersonAttach['begDate'].alias('begDate'),
            tableOrgStructure['infisInternalCode'].alias('sectionCode')
        ]
        cond = [
            tableOrgStructure['id'].eq(orgStructureId)
        ]

        rec = db.getRecordEx(queryTable, cols, cond, order=tablePersonAttach['begDate'].desc())
        if rec is not None:
            return DoctorSectionInfo(id=forceRef(rec.value('id')),
                                     sectionCode=forceString(rec.value('sectionCode')) or None,
                                     begDate=forceDate(rec.value('begDate')),
                                     doctorSNILS=formatSNILS(forceString(rec.value('doctorSNILS')) or None))

        return DoctorSectionInfo()

    @classmethod
    def makeClientAttachInfo(cls, attachRecord, deattachQuery=None):
        u"""
        Информация о прикреплении для синхронизации с ТФОМС
        :param attachRecord: QSqlRecord (ClientAttach)
        :param deattachQuery: DeAttachQuery
        :return: AttachInfo
        """
        attachType, attachReason = cls.getAttachTypeInfo(forceRef(attachRecord.value('attachType_id')))
        deattachReason = cls.getDeAttachReason(forceRef(attachRecord.value('detachment_id')))
        orgStructureId = forceRef(attachRecord.value('orgStructure_id'))
        orgCode, sectionCode = CBookkeeperCode.getOrgCode(orgStructureId)

        return AttachInfo(id=forceRef(attachRecord.value('id')),
                          orgCode=orgCode,
                          sectionCode=sectionCode,
                          begDate=forceDate(attachRecord.value('begDate')) or None,
                          endDate=forceDate(attachRecord.value('endDate')) or None,
                          doctorSNILS=cls.getDoctorSectionInfo(orgStructureId).doctorSNILS,
                          attachType=attachType,
                          attachReason=attachReason,
                          deattachReason=deattachReason,
                          deattachQuery=deattachQuery)

    @classmethod
    def makeClientInfoById(cls, clientId):
        u"""
        Информация о прикреплении пациента
        :param clientId: Client.id
        :return: AttachedClientInfo
        """
        db = QtGui.qApp.db
        tableClient = db.table('Client')
        tableClientDocument = db.table('ClientDocument')
        tableClientPolicy = db.table('ClientPolicy')
        tableDocumentType = db.table('rbDocumentType')
        tablePolicyKind = db.table('rbPolicyKind')
        tableInsurer = db.table('Organisation').alias('Ins')
        tableInsurerHead = db.table('Organisation').alias('InsHead')

        table = tableClient.leftJoin(tableClientDocument, tableClientDocument['id'].eq(db.func.getClientDocumentId(tableClient['id'])))
        table = table.leftJoin(tableDocumentType, tableDocumentType['id'].eq(tableClientDocument['documentType_id']))
        table = table.leftJoin(tableClientPolicy, tableClientPolicy['id'].eq(db.func.getClientPolicyId(tableClient['id'], 1)))
        table = table.leftJoin(tablePolicyKind, tablePolicyKind['id'].eq(tableClientPolicy['policyKind_id']))
        table = table.leftJoin(tableInsurer, tableInsurer['id'].eq(tableClientPolicy['insurer_id']))
        table = table.leftJoin(tableInsurerHead, tableInsurerHead['id'].eq(tableInsurer['head_id']))

        cols = [
            tableClient['id'].alias('clientId'),
            tableClient['lastName'],
            tableClient['firstName'],
            tableClient['patrName'],
            tableClient['birthDate'],
            tableClient['sex'],
            tableClient['SNILS'],
            tableClientDocument['serial'].alias('docSerial'),
            tableClientDocument['number'].alias('docNumber'),
            tableDocumentType['code'].alias('docType'),
            tableClientPolicy['serial'].alias('policySerial'),
            tableClientPolicy['number'].alias('policyNumber'),
            tablePolicyKind['regionalCode'].alias('policyType'),
            tableInsurer['miacCode'].alias('insurerCode'),
            db.if_(tableInsurer['head_id'].isNull(),
                   tableInsurer['OKATO'],
                   tableInsurerHead['OKATO']).alias('insurerOKATO')
        ]
        rec = db.getRecordEx(table, cols, tableClient['id'].eq(clientId))
        if rec is not None:
            return AttachedClientInfo(
                nameCase(forceString(rec.value('lastName'))),
                nameCase(forceString(rec.value('firstName'))),
                nameCase(forceString(rec.value('patrName'))),
                forceDate(rec.value('forceDate')),
                formatSex(rec.value('sex')),
                formatSNILS(forceString(rec.value('SNILS')).replace('-', '').replace(' ', '')) or None,
                id=forceRef(rec.value('clientId')),
                doc=DocumentInfo(
                    forceString(rec.value('docSerial')) or None,
                    forceString(rec.value('docNumber')) or None,
                    forceInt(rec.value('docType'))
                ),
                policy=PolicyInfo(
                    forceString(rec.value('policySerial')) or None,
                    forceString(rec.value('policyNumber')) or None,
                    forceInt(rec.value('policyType')),
                    forceString(rec.value('insurerCode')) or None,
                    forceString(rec.value('insurerOKATO')) or None
                )
            )

        return AttachedClientInfo()

    @classmethod
    def makeClientInfo(cls, clientRecord, documentRecord, policyRecord):
        u"""
        Информация о пациенте и прикреплениях (для синхронизации из карточки пациента)
        :param clientRecord: QSqlRecord (Client)
        :param documentRecord: QSqlRecord (ClientDocument)
        :param policyRecord: QSqlRecord (ClientPolicy)
        :return: AttachedClientInfo
        """
        if documentRecord is not None:
            doc = DocumentInfo(forceString(documentRecord.value('serial')) or None,
                               forceString(documentRecord.value('number')) or None,
                               cls.getDocumentType(forceRef(documentRecord.value('documentType_id'))) or None)
        else:
            doc = DocumentInfo()

        if policyRecord is not None:
            insurerCode, insurerOKATO = cls.getInsurerInfo(forceRef(policyRecord.value('insurer_id')))
            policy = PolicyInfo(forceString(policyRecord.value('serial')) or None,
                                forceString(policyRecord.value('number')) or None,
                                cls.getPolicyType(forceRef(policyRecord.value('policyKind_id'))) or None,
                                insurerCode=insurerCode or None,
                                insurerOKATO=insurerOKATO or None)
        else:
            policy = PolicyInfo()

        return AttachedClientInfo(
            lastName=nameCase(forceString(clientRecord.value('lastName'))),
            firstName=nameCase(forceString(clientRecord.value('firstName'))),
            patrName=nameCase(forceString(clientRecord.value('patrName'))),
            birthDate=forceDate(clientRecord.value('birthDate')),
            sex=formatSex(clientRecord.value('sex')),
            SNILS=formatSNILS(forceString(clientRecord.value('SNILS')).replace('-', '').replace(' ', '')) or None,
            id=forceRef(clientRecord.value('id')),
            doc=doc,
            policy=policy
        )

    @classmethod
    def makePersonAttachInfo(cls, personRecord, attachRecord, workerCategory):
        u"""
        Информация о прикреплении сотрудника
        :param personRecord: QSqlRecord (Person)
        :param attachRecord: QSqlRecord (PersonAttach)
        :param workerCategory: PersonAttachInfo.category
        :return: PersonAttachInfo
        """
        db = QtGui.qApp.db
        orgCode, sectionCode = CBookkeeperCode.getOrgCode(forceRef(attachRecord.value('orgStructure_id')))
        return PersonAttachInfo(
            id=forceRef(attachRecord.value('id')),
            orgCode=orgCode,
            sectionCode=sectionCode,
            begDate=forceDate(attachRecord.value('begDate')),
            lastName=nameCase(forceString(personRecord.value('lastName'))),
            firstName=nameCase(forceString(personRecord.value('firstName'))),
            patrName=nameCase(forceString(personRecord.value('patrName'))),
            birthDate=forceDate(personRecord.value('birthDate')),
            SNILS=formatSNILS(forceString(personRecord.value('SNILS')).replace('-', '').replace(' ', '')) or None,
            specialityCode=forceInt(db.translate('rbSpeciality', 'id', personRecord.value('speciality_id'), 'regionalCode')) or None,
            category=forceInt(workerCategory)
        )

    @classmethod
    def updateAttaches(cls, syncedIdList, errorMap, tableName='ClientAttach'):
        u"""
        Обновить состояние прикреплений в БД
        :param syncedIdList: список ClientAttach.id (PersonAttach.id)_
        :type: list
        :param errorMap: {id: unicode} - ошибки в прикеплениях
        :type: dict
        :param tableName: 'ClientAttach' или 'PersonAttach' 
        """
        db = QtGui.qApp.db
        table = db.table(tableName)

        if syncedIdList:
            db.updateRecords(table,
                             expr=[table['sentToTFOMS'].eq(CAttachSentToTFOMS.Synced),
                                   table['errorCode'].eq('')],
                             where=table['id'].inlist(syncedIdList))

        if errorMap:
            for attachId, error in errorMap.iteritems():
                db.updateRecords(table,
                                 expr=[table['sentToTFOMS'].eq(CAttachSentToTFOMS.NotSynced),
                                       table['errorCode'].eq(error)],
                                 where=table['id'].eq(attachId))

    @classmethod
    def findAttachedClientInfo(cls, senderCode='', idList=None):
        u"""
        Ищем в БД полученные из ТФОМС прикрепления пациентов:
        1. Проставляем AttachedClientInfo.orgStructure_id (для фильтрации по подразделению)
        2. Проставляем AttachedClientInfo.client_id, если не найден - обновляем статус AttachedClientInfo.syncStatus = ClientNotFound
        3. Проставляем AttachedClientInfo.syncStatus = FoundDouble для записей с коллизией по Client.id среди тех, кто не найден на первом этапе
        4. Проставляем AttachedClientInfo.attach_id для тех записей, где client_id != NULL, если не найден - обновляем syncStatus (Deattach_NoAttach или Attach_NotMatch соответственно)
        :param senderCode: код МО, запросившего списки
        :param idList: [list of AttachedClientInfo.id]: список прикреплений, по которым производится поиск
        """
        cls.findOrgStructures(senderCode, idList)
        cls.findClients(senderCode, idList)
        cls.findClientDoubles(senderCode, idList)
        cls.findAttaches(senderCode, idList)

    @classmethod
    def findOrgStructures(cls, senderCode, idList=None):
        u""" В AttachedClientInfo.orgStructure_id проставляем OrgStructure.id, где bookkeeperCode = orgCode и infisInternalCode = sectionCode """
        db = QtGui.qApp.db
        tableACI = db.table(CAttachedInfoTable.getTableName())
        tableBK = db.table(CBookkeeperCode.getTableName())
        tableOrgStructure = db.table('OrgStructure')

        table = tableACI.innerJoin(tableBK, tableBK['orgCode'].eq(tableACI['orgCode']))
        table = table.innerJoin(tableOrgStructure, [tableOrgStructure['id'].eq(tableBK['id']),
                                                    tableOrgStructure['infisInternalCode'].eq(tableACI['sectionCode']),
                                                    tableOrgStructure['deleted'].eq(0)])
        cond = [
            tableACI['orgStructure_id'].isNull()
        ]
        if idList:
            cond.append(tableACI['id'].inlist(idList))
        elif senderCode:
            cond.append(tableACI['senderCode'].eq(senderCode))
        else:
            return

        db.insertFromSelect(tableACI,
                            table,
                            {
                                'id'             : tableACI['id'],
                                'orgStructure_id': tableOrgStructure['id']
                            },
                            cond,
                            excludeFields=['id'])

    @classmethod
    def findClients(cls, senderCode='', idList=None):
        u""" По ФИО + ДР [+документ +полис] из AttachedClientInfo ищем Client.id и проставляем в AttachedClientInfo.client_id """
        db = QtGui.qApp.db
        tableACI = db.table(CAttachedInfoTable.getTableName())
        tableClient = db.table('Client')
        tableCD = db.table('ClientDocument')
        tableCP = db.table('ClientPolicy')

        table = tableACI
        table = table.leftJoin(tableClient, [tableClient['lastName'].eq(tableACI['lastName']),
                                             tableClient['firstName'].eq(tableACI['firstName']),
                                             tableClient['birthDate'].eq(tableACI['birthDate']),
                                             db.joinOr([
                                                 tableClient['patrName'].eq(''),
                                                 tableACI['patrName'].eq(''),
                                                 tableClient['patrName'].eq(tableACI['patrName'])
                                             ]),
                                             db.joinOr([
                                                 tableClient['SNILS'].eq(''),
                                                 tableACI['SNILS'].eq(''),
                                                 tableClient['SNILS'].eq(tableACI['SNILS'])
                                             ]),
                                             tableClient['deleted'].eq(0)])
        table = table.leftJoin(tableCD, [tableCD['client_id'].eq(tableClient['id']),
                                         tableCD['serial'].eq(tableACI['docSerial']),
                                         tableCD['number'].eq(tableACI['docNumber']),
                                         tableCD['deleted'].eq(0)])
        table = table.leftJoin(tableCP, [tableCP['client_id'].eq(tableClient['id']),
                                         tableCP['serial'].eq(tableACI['policySerial']),
                                         tableCP['number'].eq(tableACI['policyNumber']),
                                         tableCP['deleted'].eq(0)])
        cols = [
            tableACI['id'].alias('id'),
            tableClient['id'].alias('clientId'),
            db.makeField(tableCD['id'].isNotNull()).alias('docFound'),
            db.makeField(tableCP['id'].isNotNull()).alias('policyFound')
        ]
        cond = [
            tableACI['client_id'].isNull()
        ]
        if idList:
            cond.extend([
                tableACI['id'].inlist(idList)
            ])
        elif senderCode:
            cond.extend([
                tableACI['senderCode'].eq(senderCode)
            ])
        else:
            return

        order = [
            tableACI['id'],
            db.makeField(db.joinAnd(['docFound', 'policyFound'])).desc(),
            db.makeField('docFound').desc(),
            db.makeField('policyFound').desc()
        ]

        updateClientId = CChunkProcessor(CAttachedInfoTable.updateField, cls.InsertChunkSize, 'client_id')
        updateSyncStatus = CChunkProcessor(CAttachedInfoTable.updateField, cls.InsertChunkSize, 'syncStatus')

        prevId = None
        for rec in db.iterRecordList(table, cols, cond, order=order):
            id = forceRef(rec.value('id'))
            if id != prevId:
                prevId = id
                clientId = forceRef(rec.value('clientId'))
                if clientId:
                    updateClientId(id, clientId)
                else:
                    updateSyncStatus(id, CAttachedClientInfoSyncStatus.Client_NotFound)

        updateClientId.process()
        updateSyncStatus.process()

    @classmethod
    def findClientDoubles(cls, senderCode='', idList=None):
        u""" Нашли больше 1 пациента по полученной информации => проставляем соответствующий статус """
        if not (idList or senderCode): return

        db = QtGui.qApp.db
        tableACI = db.table(CAttachedInfoTable.getTableName())
        tableClient = db.table('Client')

        table = tableACI.innerJoin(tableClient, [tableClient['lastName'].eq(tableACI['lastName']),
                                                 tableClient['firstName'].eq(tableACI['firstName']),
                                                 tableClient['birthDate'].eq(tableACI['birthDate']),
                                                 db.joinOr([
                                                     tableClient['patrName'].eq(''),
                                                     tableACI['patrName'].eq(''),
                                                     tableClient['patrName'].eq(tableACI['patrName'])
                                                 ]),
                                                 db.joinOr([
                                                     tableClient['SNILS'].eq(''),
                                                     tableACI['SNILS'].eq(''),
                                                     tableClient['SNILS'].eq(tableACI['SNILS'])
                                                 ]),
                                                 tableClient['deleted'].eq(0)])
        cols = [
            tableACI['id'].alias('id'),
        ]
        cond = [
            tableACI['client_id'].isNull()
        ]
        if idList:
            cond.append(tableACI['id'].inlist(idList))
        elif senderCode:
            cond.append(tableACI['senderCode'].eq(senderCode))
        group = [
            tableACI['id']
        ]
        having = [
            db.count(tableClient['id']).gt(1)
        ]

        with CChunkProcessor(CAttachedInfoTable.updateField, cls.InsertChunkSize, 'syncStatus') as updateSyncStatus:
            for rec in db.iterRecordList(table, cols, cond, group=group, having=having):
                updateSyncStatus(forceRef(rec.value('id')),
                                 CAttachedClientInfoSyncStatus.Client_FoundDouble)

    @classmethod
    def findAttaches(cls, senderCode='', idList=None):
        u""" По коду МО + коду участка [+дате] из AttachedClientInfo ищем ClientAttach.id и проставляем AttachedClientInfo.attach_id
        :param senderCode: код участника обмена
        :param idList: list of AttachedClientInfo.id (если указано, то senderCode игнорируем)
        """
        db = QtGui.qApp.db
        tableACI = db.table(CAttachedInfoTable.getTableName())
        tableAttachType = db.table('rbAttachType')
        tableClientAttach = db.table('ClientAttach')

        table = tableACI
        table = table.leftJoin(tableClientAttach, [tableClientAttach['client_id'].eq(tableACI['client_id']),
                                                   tableClientAttach['deleted'].eq(0)])
        table = table.leftJoin(tableAttachType, [tableAttachType['id'].eq(tableClientAttach['attachType_id']),
                                                 tableAttachType['code'].eq(tableACI['attachType'])])

        cols = [
            tableACI['id'].alias('id'),
            tableClientAttach['id'].alias('attachId'),
            db.makeField(tableACI['endDate'].isNull()).alias('toAttach'),
            db.makeField(
                db.joinAnd([
                    tableClientAttach['orgStructure_id'].eq(tableACI['orgStructure_id']),
                    tableClientAttach['id'].isNotNull(),
                    tableAttachType['id'].isNotNull(),
                    db.if_(
                        tableACI['endDate'].isNull(),
                        tableClientAttach['endDate'].isNull(),
                        tableClientAttach['begDate'].dateLe(tableACI['endDate'])
                    )
                ])
            ).alias('attachFound')
        ]

        cond = [
            tableACI['client_id'].isNotNull()
        ]
        if idList:
            cond.append(tableACI['id'].inlist(idList))
        elif senderCode:
            cond.append(tableACI['senderCode'].eq(senderCode))
        else:
            return

        order = [
            tableACI['id'],
            db.makeField('attachFound').desc()
        ]

        # Находим прикрепления в БД по коду МО (bookkeeperCode), коду участка (infisInternalCode), датам
        # Проставляем в AttachedClientInfo.attach_id
        updateAttachId = CChunkProcessor(CAttachedInfoTable.updateField, cls.InsertChunkSize, 'attach_id')
        updateStatus = CChunkProcessor(CAttachedInfoTable.updateField, cls.InsertChunkSize, 'syncStatus')

        prevId = None
        for rec in db.iterRecordList(table, cols, cond, order=order):
            id = forceRef(rec.value('id'))
            if id != prevId:
                attachId = forceRef(rec.value('attachId'))
                toAttach = forceBool(rec.value('toAttach'))
                attachFound = forceBool(rec.value('attachFound'))

                if attachFound and attachId:
                    updateAttachId(id, attachId)
                else:
                    updateStatus(id,
                                 CAttachedClientInfoSyncStatus.Attach_NotMatch if toAttach
                                 else CAttachedClientInfoSyncStatus.Deattach_NoAttach)

        updateAttachId.process()
        updateStatus.process()

    @classmethod
    def createClients(cls, idList):
        u"""
        Пациент не найден в БД - создаем по информации из ТФОМС
        (ФИО + ДР + СНИЛС + документ + полис + адреса + прикрепление)
        :param idList: [list of AttachedClientInfo.id]
        """
        if not idList: return

        db = QtGui.qApp.db
        tableACI = db.table('AttachedClientInfo')
        tableClient = db.table('Client')

        db.insertFromSelect(tableClient,
                            tableACI,
                            {
                                'createDatetime' : 'NOW()',
                                'createPerson_id': db.valueField(QtGui.qApp.userId),
                                'lastName'       : tableACI['lastName'],
                                'firstName'      : tableACI['firstName'],
                                'patrName'       : tableACI['patrName'],
                                'sex'            : tableACI['sex'],
                                'birthDate'      : tableACI['birthDate'],
                                'SNILS'          : tableACI['SNILS']
                            },
                            tableACI['id'].inlist(idList))

        cls.findClients(idList=idList)
        cls.createClientPolicy(idList)
        cls.createClientDocument(idList)
        cls.createClientAddress(idList)
        CAttachedInfoTable.attachByTFOMS(idList)

    @classmethod
    def createClientPolicy(cls, idList):
        u""" Создаем полисы для созданных пациентов по информации из ТФОМС
        :param idList: [list of AttachedClientInfo.id]
        """
        db = QtGui.qApp.db
        tableACI = db.table('AttachedClientInfo')
        tableClientPolicy = db.table('ClientPolicy')
        tablePolicyKind = db.table('rbPolicyKind')
        tablePolicyType = db.table('rbPolicyType')
        tableInsurer = db.table('Organisation')

        table = tableACI.leftJoin(tablePolicyKind, tablePolicyKind['code'].eq(tableACI['policyType']))
        table = table.leftJoin(tablePolicyType, tablePolicyType['code'].eq('1'))  # ОМС
        table = table.leftJoin(tableInsurer, [tableInsurer['smoCode'].eq(tableACI['insurerCode']),
                                              tableInsurer['isInsurer'].eq(1),
                                              tableInsurer['deleted'].eq(0)])
        cond = [
            tableACI['id'].inlist(idList),
            tableACI['client_id'].isNotNull(),
            tableACI['policyNumber'].ne('')
        ]

        db.insertFromSelect(tableClientPolicy,
                            table,
                            {
                                'createDatetime' : 'NOW()',
                                'createPerson_id': db.valueField(QtGui.qApp.userId),
                                'client_id'      : tableACI['client_id'],
                                'serial'         : tableACI['policySerial'],
                                'number'         : tableACI['policyNumber'],
                                'policyType_id'  : tablePolicyType['id'],
                                'policyKind_id'  : tablePolicyKind['id'],
                                'insurer_id'     : tableInsurer['id']
                            },
                            cond,
                            group=tableACI['id'])

    @classmethod
    def createClientDocument(cls, idList):
        u"""
        Создаем документы для созданных пациентов по информации из ТФОМС
        :param idList: [list of AttachedClientInfo.id]
        """
        db = QtGui.qApp.db
        tableACI = db.table('AttachedClientInfo')
        tableClientDocument = db.table('ClientDocument')
        tableDocumentType = db.table('rbDocumentType')

        table = tableACI.leftJoin(tableDocumentType, tableDocumentType['code'].eq(tableACI['docType']))
        cond = [
            tableACI['id'].inlist(idList),
            tableACI['client_id'].isNotNull(),
            tableACI['docNumber'].ne('')
        ]
        db.insertFromSelect(tableClientDocument,
                            table,
                            {
                                'createDatetime' : 'NOW()',
                                'createPerson_id': db.valueField(QtGui.qApp.userId),
                                'client_id'      : tableACI['client_id'],
                                'serial'         : tableACI['docSerial'],
                                'number'         : tableACI['docNumber'],
                                'documentType_id': tableDocumentType['id']
                            },
                            cond,
                            group=tableACI['id'])

    @classmethod
    def createClientAddress(cls, idLst):
        u"""
        Создаем адреса для созданных пациентов по информации из ТФОМС
        :param idLst: [list of AttachedClientInfo.id]
        """
        db = QtGui.qApp.db
        tableACI = db.table('AttachedClientInfo')
        tableClientAddress = db.table('ClientAddress')

        for addressType, district, city, locality, street, house, corpus, flat in (
                (0, 'regDistrict', 'regCity', 'regLocality', 'regStreet', 'regHouse', 'regCorpus', 'regFlat'),
                (1, 'locDistrict', 'locCity', 'locLocality', 'locStreet', 'locHouse', 'locCorpus', 'locFlat')
        ):
            table = tableACI.leftJoin(tableClientAddress, [tableClientAddress['client_id'].eq(tableACI['client_id']),
                                                           tableClientAddress['type'].eq(addressType),
                                                           tableClientAddress['deleted'].eq(0)])
            cond = [
                tableACI['id'].inlist(idLst),
                tableACI['client_id'].isNotNull(),
                tableClientAddress['id'].isNull(),
                db.joinOr([
                    tableACI[district].ne(''),
                    tableACI[city].ne(''),
                    tableACI[locality].ne(''),
                    tableACI[street].ne(''),
                    tableACI[house].ne(''),
                    tableACI[corpus].ne(''),
                    tableACI[flat].ne('')
                ])
            ]
            db.insertFromSelect(tableClientAddress,
                                table,
                                {
                                    'createDatetime' : 'NOW()',
                                    'createPerson_id': db.valueField(QtGui.qApp.userId),
                                    'client_id'      : tableACI['client_id'],
                                    'type'           : db.valueField(addressType),
                                    'isVillager'     : db.valueField(0),
                                    'freeInput'      : db.concat_ws(u', ',
                                                                    db.if_(tableACI[district].ne(''), tableACI[district], db.NULL),
                                                                    db.if_(tableACI[city].ne(''), tableACI[city], db.NULL),
                                                                    db.if_(tableACI[locality].ne(''), tableACI[locality], db.NULL),
                                                                    db.if_(tableACI[street].ne(''), tableACI[street], db.NULL),
                                                                    db.if_(tableACI[house].ne(''), db.concat(u'д. ', tableACI[house]), db.NULL),
                                                                    db.if_(tableACI[corpus].ne(''), db.concat(u'к. ', tableACI[corpus]), db.NULL),
                                                                    db.if_(tableACI[flat].ne(''), db.concat(u'кв. ', tableACI[flat]), db.NULL)
                                                                    )
                                },
                                cond)

    @classmethod
    def getClientAttaches(cls, connection, attachedClientInfo):
        u""" Запрашиваем текущее прикрепление пациента
        :param connection: CR23ClientAttachService
        :param attachedClientInfo: AttachedClientInfo
        :return: AttachResult
        """
        try:
            return connection.getAttachInformation(attachedClientInfo)
        except Exception as e:
            QtGui.qApp.logCurrentException()
            return AttachResult(errors=[AttachError(message=forceString(e))])

    @classmethod
    def sendDeAttachQueries(cls, connection, queries):
        u"""
        Оправляем уведомления о прикреплении
        :param connection: CR23ClientAttachService
        :param queries: [list of DeAttachQuery]
        :return: tuple([list of str], {ClientAttach.id: str}) : (список общих ошибок, ошибки в прикреплениях)
        """
        try:
            results = connection.sendDeAttachQuery(queries)
        except Exception as e:
            QtGui.qApp.logCurrentException()
            results = [AttachResult(errors=[AttachError(message=forceString(e))])]

        errors = []
        errorMap = {}

        for result in results:
            if result.hasErrors():
                msg = result.errorMessage()
                if result.attachId is not None:
                    errorMap[result.attachId] = msg
                else:
                    errors.append(msg)

        return errors, errorMap

    @classmethod
    def syncClientAttaches(cls, connection, clientAttachInfoList, changeSection=False):  # 1 attach per 1 client
        u"""
        Синхронизация прикреплений пациента
        :param connection: CR23ClientAttachService
        :param clientAttachInfoList: [list of AttachedClientInfo]
        :param changeSection: признак смены участка (параметр MakeAttachAction для переноса пациентов с участка на участок без отправки открепления)
        :return: tuple(
            [list of ClientAttach.id] - синхронизированные прикрепления,
            [list of unicode] - общие ошибки (нет соединения, неверный логин/пароль, etc.),
            {ClientAttach.id: unicode} - ошибки в прикреплениях
        )
        """
        syncErrors = []
        attachErrorMap = {}

        toDeAttach = filter(lambda c: c.attach.endDate is not None, clientAttachInfoList)
        if toDeAttach:
            for i in xrange(0, len(toDeAttach), cls.SyncChunkSize):
                try:
                    badResults = connection.makeDeAttach(toDeAttach[i: i + cls.SyncChunkSize])
                except CSynchronizeAttachException as e:
                    syncErrors.append(forceString(e))
                except Exception as e:
                    QtGui.qApp.logCurrentException()
                    syncErrors.append(forceString(e))
                else:
                    for result in badResults:
                        errorMsg = result.errorMessage()
                        if result.attachId is not None:
                            attachErrorMap[result.attachId] = errorMsg
                        else:
                            syncErrors.append(errorMsg)

        toAttach = filter(lambda c: c.attach.endDate is None, clientAttachInfoList)
        if toAttach:
            for i in xrange(0, len(toAttach), cls.SyncChunkSize):
                attachChunk = toAttach[i: i + cls.SyncChunkSize]
                errors, errorMap = cls.syncToAttachChunk(connection, attachChunk, changeSection)
                syncErrors.extend(errors)
                attachErrorMap.update(errorMap)

        idList = [clientAttachInfo.attach.id for clientAttachInfo in clientAttachInfoList]
        syncedIdList = list(set(idList).difference(set(attachErrorMap.keys()))) if not syncErrors else []
        cls.updateAttaches(syncedIdList, attachErrorMap, 'ClientAttach')
        cls.setSyncedClientAttaches(syncedIdList)

        return syncedIdList, syncErrors, attachErrorMap

    @classmethod
    def createDeAttachQuery(cls, clientInfo, srcAttach, destAttach):
        u"""
        Уведомление о прикреплении
        :param clientInfo: AttachedClientInfo
        :param srcAttach: AttachInfo: прикрепление в БД
        :param destAttach: AttachInfo: прикрепление в ТФОМС
        :return: DeAttachQuery
        """
        return DeAttachQuery(
            id=srcAttach.id,
            number=srcAttach.deattachQuery.number or CDeAttachQueryCounter.getValue(),
            date=srcAttach.deattachQuery.date or QtCore.QDate.currentDate(),
            srcOrgCode=srcAttach.orgCode,
            destOrgCode=destAttach.orgCode,
            client=clientInfo
        )

    @classmethod
    def syncToAttachChunk(cls, connection, attachChunk, changeSection=False):
        u"""
        Для прикреплении по заявлению
        :param connection: CR23ClientAttachService
        :param attachChunk: [list of AttachInfo]
        :param changeSection: bool: флаг смены участка (смена прикрепления внутри МО без открепления)
        :return: tuple([list of str], {ClientAttach.id: str}) : (общие ошибки, ошибки в прикреплениях)
        """
        syncErrors = []
        attachErrorMap = {}

        deattachQueries = []
        for clientInfo in filter(lambda c: c.attach.attachType == CAttachType.Attached, attachChunk):
            attachDB = clientInfo.attach
            infoTFOMSResult = cls.getClientAttaches(connection, clientInfo)
            if not infoTFOMSResult.hasErrors():
                attachesTFOMS = infoTFOMSResult.result.attaches
                if attachesTFOMS:
                    attachTF = attachesTFOMS[0]
                    if CBookkeeperCode.isExternalOrgCode(attachTF.orgCode):
                        deattachQueries.append(cls.createDeAttachQuery(clientInfo, attachDB, attachTF))

        try:
            results = connection.sendDeAttachQuery(deattachQueries)
            errorIds = set(result.attachId for result in results)

            deattachQueryLogValues = []
            for deattachQuery in deattachQueries:
                deattachQueryLogValues.append((
                    deattachQuery.client.id,
                    deattachQuery.id,
                    deattachQuery.srcOrgCode,
                    deattachQuery.destOrgCode,
                    deattachQuery.number,
                    deattachQuery.date,
                    0 if deattachQuery.id in errorIds else 1
                ))
            if deattachQueryLogValues:
                insertDeAttachQueryLog(deattachQueryLogValues)

        except Exception:
            QtGui.qApp.logCurrentException()

        try:
            badResults = connection.makeAttach(attachChunk, changeSection)  # TODO: group by attach.attachType
        except CSynchronizeAttachException as e:
            syncErrors.append(forceString(e))
        except Exception as e:
            QtGui.qApp.logCurrentException()
            syncErrors.append(forceString(e))
        else:
            for result in badResults:
                errorMsg = result.errorMessage()
                if result.attachId is not None:
                    attachErrorMap[result.attachId] = errorMsg
                else:
                    syncErrors.append(errorMsg)

        return syncErrors, attachErrorMap

    @classmethod
    def syncClientAttach(cls, connection, clientInfo, attaches):
        u"""
        Синхронизация прикреплении из карточки пациента
        :type connection: CR23ClientAttachService
        :type clientInfo: AttachedClientInfo
        :type attaches: list of AttachInfo
        :return: tuple : ([list of ClientAttach.id], : Синхронизированные прикрепления
                          [list of str],             : Общие ошибки
                          {ClientAttach.id: str},    : Ошибки прикреплений
                          {DeAttachQuery: bool}      : Уведомления о прикреплении (статус отправки)
                          )
        """
        syncErrors = []
        attachErrorMap = {}

        badResults, deattachQueryResult = cls.trySyncClientAttach(connection, clientInfo, attaches)
        for result in badResults:
            errorMsg = result.errorMessage()
            if result.attachId is not None:
                attachErrorMap[result.attachId] = errorMsg
            else:
                syncErrors.append(errorMsg)

        idList = [attach.id for attach in attaches]
        syncedList = list(set(idList).difference(set(attachErrorMap.iterkeys()))) if not syncErrors else []

        return syncedList, syncErrors, attachErrorMap, deattachQueryResult

    @classmethod
    def trySyncClientAttach(cls, connection, clientInfo, attaches):  # 1 client, N attaches
        u"""
        :type connection: CR23ClientAttachService
        :type clientInfo: AttachedClientInfo
        :type attaches: list of AttachInfo
        :return: tuple([list of AttachResult],
                       {DeAttachQuery: bool})
        """
        toDeAttach = filter(lambda a: a.endDate is not None, attaches)
        toAttach = filter(lambda a: a.endDate is None, attaches)
        toDeAttachQuery = filter(lambda a: a.attachType == CAttachType.Attached, toAttach)

        deattachQueryResult = {}  # { DeAttachQuery: bool } - запрос на открепление и статус отправки

        # запрашиваем прикрепления из ТФОМС
        attachResult = cls.getClientAttaches(connection, clientInfo)
        if attachResult.hasErrors():
            return [attachResult], deattachQueryResult

        attachInfoTFOMS = attachResult.result  # прикрепления из ТФОМС
        internalAttaches = filter(lambda a: not CBookkeeperCode.isExternalOrgCode(a.orgCode), attachInfoTFOMS.attaches)  # прикрепления к текущему МО
        externalAttaches = filter(lambda a: CBookkeeperCode.isExternalOrgCode(a.orgCode), attachInfoTFOMS.attaches)  # прикрепления к внешним МО

        # отправляем открепления
        for attach in toDeAttach:
            if attach.orgCode in [a.orgCode for a in internalAttaches]:
                try:
                    clientInfo.attach = attach
                    badResults = connection.makeDeAttach([clientInfo])
                    if badResults:
                        return badResults, deattachQueryResult
                except Exception as e:
                    return [AttachResult(errors=[AttachError(message=forceString(e))])], deattachQueryResult

        # отправляем уведомления о прикреплении
        deattachQueryLogValues = []
        for attach in toDeAttachQuery:
            for externalAttach in externalAttaches:
                deattachQuery = cls.createDeAttachQuery(clientInfo, attach, externalAttach)
                try:
                    results = connection.sendDeAttachQuery([deattachQuery])
                    sendStatus = 0 if results[0].hasErrors() else 1
                    deattachQueryLogValues.append((clientInfo.id, deattachQuery.id, deattachQuery.srcOrgCode, deattachQuery.destOrgCode, deattachQuery.number, deattachQuery.date, sendStatus))
                    if results[0].hasErrors():
                        deattachQueryResult[deattachQuery] = True
                        return results, deattachQueryResult
                    else:
                        deattachQueryResult[deattachQuery] = False
                except Exception as e:
                    return [AttachResult(errors=[AttachError(message=forceString(e))])], deattachQueryResult
        if deattachQueryLogValues:
            insertDeAttachQueryLog(deattachQueryLogValues)

        # отправляем прикрепления
        for attach in toAttach:
            sameAttaches = filter(lambda a: (a.orgCode == attach.orgCode and
                                             a.sectionCode == attach.sectionCode and
                                             a.attachType == attach.attachType), internalAttaches)
            if not sameAttaches:
                try:
                    clientInfo.attach = attach
                    badResults = connection.makeAttach([clientInfo])
                except CSynchronizeAttachException as e:
                    return [AttachResult(attachId=attach.id,
                                         errors=[AttachError(message=forceString(e))])], deattachQueryResult
                else:
                    if badResults:
                        return badResults, deattachQueryResult

        return [], deattachQueryResult

    @classmethod
    def setSyncedClientAttaches(cls, clientAttachIdList):
        if not clientAttachIdList: return
        db = QtGui.qApp.db
        tableClientAttach = db.table('ClientAttach')
        expr = [
            tableClientAttach['errorCode'].eq(''),
            tableClientAttach['sentToTFOMS'].eq(CAttachSentToTFOMS.Synced)
        ]
        cond = [
            tableClientAttach['id'].inlist(clientAttachIdList)
        ]
        db.updateRecords(tableClientAttach, expr, cond)

    @classmethod
    def setSyncedPersonAttaches(cls, personAttachIdList):
        u"""
        После синхронизации текущего прикрепления сотрудника считаем предыдущие (закрытые) прикрепления синхронизированными
        :param personAttachIdList: Текущие (синхронизированные с ТФОМС) прикрепления сотрудников
        """
        if not personAttachIdList: return
        db = QtGui.qApp.db
        tablePersonAttach = db.table('PersonAttach')

        personIdList = db.getIdList(tablePersonAttach, tablePersonAttach['master_id'], tablePersonAttach['id'].inlist(personAttachIdList))
        cond = [
            tablePersonAttach['endDate'].isNotNull(),
            tablePersonAttach['deleted'].eq(0),
            tablePersonAttach['master_id'].inlist(personIdList)
        ]
        expr = [
            tablePersonAttach['errorCode'].eq(''),
            tablePersonAttach['sentToTFOMS'].eq(CAttachSentToTFOMS.Synced)
        ]
        db.updateRecords(tablePersonAttach, expr, cond)

    @classmethod
    def syncPersonAttaches(cls, connection, personAttachInfoList):
        u"""
        Синхронизация прикреплений сотрудников
        :param connection: CR23PersonAttachService
        :param personAttachInfoList: [list of PersonAttachInfo]
        :return: tuple: ([list of PersonAttach.id], : Синхронизированные прикрепления
                         [list of str],             : Общие ошибки
                         {PersonAttach.id: str})    : Ошибки в прикреплениях
        """
        syncErrors = []
        attachErrorMap = {}

        for i in xrange(0, len(personAttachInfoList), cls.SyncChunkSize):
            try:
                badResults = connection.sendAttachDoctorSectionInfo(personAttachInfoList[i: i + cls.SyncChunkSize])
            except Exception as e:
                QtGui.qApp.logCurrentException()
                syncErrors.append(forceString(e))
            else:
                for result in badResults:
                    errorMsg = result.errorMessage()
                    if result.attachId is not None:
                        attachErrorMap[result.attachId] = errorMsg
                    else:
                        syncErrors.append(errorMsg)

        idList = [personAttachInfo.id for personAttachInfo in personAttachInfoList]
        syncedIdList = list(set(idList).difference(set(attachErrorMap.keys()))) if not syncErrors else []
        cls.updateAttaches(syncedIdList, attachErrorMap, 'PersonAttach')
        cls.setSyncedPersonAttaches(syncedIdList)

        return syncedIdList, syncErrors, attachErrorMap
