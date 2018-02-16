# -*- coding: utf-8 -*-
from Exchange.R23.TFOMS.Types import PersonItem
from library.Utils import forceDate, forceInt, forceString, formatSNILS, nameCase
from library.database import CDatabase


class CTFOMSData(object):
    u""" Базовый класс для экспорта/импорта инофрмации из ТФОМС в БД """

    def __init__(self, db):
        self.db = db  # type: CDatabase
        self._attachTypeIdMap = {}

    def currentOrgId(self):
        tableOrgStructure = self.db.table('OrgStructure')
        idList = self.db.getDistinctIdList(tableOrgStructure,
                                           tableOrgStructure['organisation_id'],
                                           [tableOrgStructure['deleted'].eq(0),
                                            tableOrgStructure['organisation_id'].isNotNull()])
        return idList[0] if idList else None

    def getAttachTypeIds(self, attachTypes):
        tableAttachType = self.db.table('rbAttachType')
        return self.db.getIdList(tableAttachType,
                                 tableAttachType['id'],
                                 tableAttachType['code'].inlist(attachTypes))

    def getPersonItem(self, clientId):
        u"""
        :param clientId: Client.id
        :rtype: PersonItem
        """
        db = self.db
        tableClient = db.table('Client')
        tableDocument = db.table('ClientDocument')
        tableDocumentType = db.table('rbDocumentType')
        tablePolicy = db.table('ClientPolicy')
        tablePolicyKind = db.table('rbPolicyKind')
        tableInsurer = db.table('Organisation').alias('Ins')
        tableInsurerHead = db.table('Organisation').alias('InsHead')

        table = tableClient
        table = table.leftJoin(tableDocument, tableDocument['id'].eq(db.func.getClientDocumentId(tableClient['id'])))
        table = table.leftJoin(tableDocumentType, tableDocumentType['id'].eq(tableDocument['documentType_id']))
        table = table.leftJoin(tablePolicy, tablePolicy['id'].eq(db.func.getClientPolicyId(tableClient['id'], 1)))
        table = table.leftJoin(tablePolicyKind, tablePolicyKind['id'].eq(tablePolicy['policyKind_id']))
        table = table.leftJoin(tableInsurer, tableInsurer['id'].eq(tablePolicy['insurer_id']))
        table = table.leftJoin(tableInsurerHead, tableInsurerHead['id'].eq(tableInsurer['head_id']))

        cols = [
            tableClient['lastName'],
            tableClient['firstName'],
            tableClient['patrName'],
            tableClient['sex'],
            tableClient['birthDate'],
            tableClient['SNILS'],
            tableDocument['serial'].alias('docSerial'),
            tableDocument['number'].alias('docNumber'),
            tableDocumentType['code'].alias('docType'),
            tablePolicy['serial'].alias('policySerial'),
            tablePolicy['number'].alias('policyNumber'),
            tablePolicyKind['regionalCode'].alias('policyType'),
            db.ifnull(tableInsurerHead['miacCode'], tableInsurer['miacCode']).alias('insurerCode'),
            db.ifnull(tableInsurerHead['OKATO'], tableInsurer['OKATO']).alias('insurerOKATO')
        ]

        rec = self.db.getRecordEx(table, cols, tableClient['id'].eq(clientId))
        if rec:
            policyNumber = forceString(rec.value('policyNumber'))
            policyType = forceInt(rec.value('policyType'))
            return PersonItem(
                lastName=nameCase(forceString(rec.value('lastName'))),
                firstName=nameCase(forceString(rec.value('firstName'))),
                patrName=nameCase(forceString(rec.value('patrName'))),
                sex=forceInt(rec.value('sex')),
                birthDate=forceDate(rec.value('birthDate')),
                SNILS=formatSNILS(forceString(rec.value('SNILS'))),
                docSerial=forceString(rec.value('docSerial')),
                docNumber=forceString(rec.value('docNumber')),
                docType=forceInt(rec.value('docType')),
                policySerial=forceString(rec.value('policySerial')),
                policyNumber=policyNumber,
                policyType=policyType,
                insurerCode=forceString(rec.value('insurerCode')),
                insuranceArea=forceString(rec.value('insurerOKATO')),
            )

        return PersonItem()
