# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Exchange.R23.ExamPlan.Types import FactExec, FactInfo, FactInvoice, PersonItem, PlanItem
from Exchange.R23.ExamPlan.Utils import ExamKind, ExamKindSpecials, ExamStatus, ExamStep, PersonCategory, Quarter
from Exchange.R23.TFOMS.Data import CTFOMSData
from Exchange.R23.TFOMS.Types import OrderError
from Exchange.R23.attach.Utils import CAttachSentToTFOMS, CBookkeeperCode
from Orgs.Utils import CAttachType, getOrgStructureDescendants, getOrganisationDescendants
from library.Utils import forceDate, forceInt, forceRef, forceString, formatSNILS, nameCase


class CExamPlanData(CTFOMSData):
    def __init__(self, db, orgId=None):
        super(CExamPlanData, self).__init__(db)
        self.tableExamPlan = self.db.table('ClientExaminationPlan')
        self._examKindEventTypes = {}
        self._attachedAttachTypes = None
        self._orgId = orgId
        self._orgCode = None

    @staticmethod
    def getExamAges(ageFrom=18, ageTo=99):
        u""" Список возрастов пациентов, проходящих ДД """
        return [x for x in xrange(21, 100, 3) if ageFrom <= x <= ageTo]

    @staticmethod
    def getExamBirthYears(year, ageFrom=18, ageTo=99):
        u""" Список годов рождения пациентов, проходящих ДД """
        return list(reversed([year - age for age in CExamPlanData.getExamAges(ageFrom, ageTo)]))

    def getConditionList(self, year=None, quarter=None, month=None, kind=None, category=None, step=None):
        cond = []
        if year is not None:
            cond.append(self.tableExamPlan['year'].eq(year))
        if quarter is not None:
            cond.append(self.tableExamPlan['month'].inlist(Quarter.monthMap[quarter]))
        if month is not None:
            cond.append(self.tableExamPlan['month'].eq(month))
        if kind is not None:
            cond.append(self.tableExamPlan['kind'].eq(kind))
        if category is not None:
            cond.append(self.tableExamPlan['category'].eq(category))
        if step is not None:
            cond.append(self.tableExamPlan['step'].eq(step))
        return cond

    def getClientBirthMonths(self, clientIdList):
        u"""
        :param clientIdList: list of Client.id
        :return: generator of tuples: (Client.id, birth month)
        """
        db = self.db
        tableClient = db.table('Client')
        cols = [
            tableClient['id'],
            db.dateMonth(tableClient['birthDate']).alias('quarter')
        ]
        for rec in db.iterRecordList(tableClient, cols, tableClient['id'].inlist(clientIdList)):
            yield (forceRef(rec.value('id')),
                   forceInt(rec.value('quarter')))

    @property
    def orgId(self):
        if self._orgId is None:
            tableOrgStructure = self.db.table('OrgStructure')
            idList = self.db.getDistinctIdList(tableOrgStructure, tableOrgStructure['organisation_id'], tableOrgStructure['deleted'].eq(0))
            self._orgId = idList[0]
        return self._orgId

    @property
    def orgCode(self):
        if self._orgCode is None:
            self._orgCode = forceString(self.db.translate('Organisation', 'id', self.orgId, 'infisCode'))
        return self._orgCode

    @property
    def attachedAttachTypes(self):
        if self._attachedAttachTypes is None:
            self._attachedAttachTypes = self.getAttachTypeIds(CAttachType.allAttached)
        return self._attachedAttachTypes

    def getClientsCount(self, year, quarter=None, month=None, kind=None, category=None):
        tableClientExamPlan = self.db.table('ClientExaminationPlan')
        cond = self.getConditionList(year=year, quarter=quarter, month=month, kind=kind, category=category)
        # cond = [
        #     tableClientExamPlan['year'].eq(year)
        # ]
        # if quarter is not None:
        #     cond.append(tableClientExamPlan['month'].inlist(Quarter.monthMap[quarter]))
        # if month is not None:
        #     cond.append(tableClientExamPlan['month'].eq(month))
        # if examKind is not None:
        #     cond.append(tableClientExamPlan['kind'].eq(examKind))
        # if category is not None:
        #     cond.append(tableClientExamPlan['category'].eq(category))
        return self.db.getDistinctCount(tableClientExamPlan, tableClientExamPlan['client_id'], cond)

    def updatePlanItem(self, idList, status=None, stepStatus=None, step=None, orgCode=None, date=None,
                       infoDate=None, infoMethod=None, infoStep=None, error=None, sendDate=None):
        u""" Обновление запис[и|ей] о плановом проф. мероприятии """
        if not idList:
            return
        elif not isinstance(idList, list):
            idList = [idList]

        tableClientExamPlan = self.db.table('ClientExaminationPlan')
        expr = []
        if status is not None:
            expr.append(tableClientExamPlan['status'].eq(status))
        if stepStatus is not None:
            expr.append(tableClientExamPlan['stepStatus'].eq(stepStatus))
        if step is not None:
            expr.append(tableClientExamPlan['step'].eq(step))
        if orgCode is not None:
            expr.append(tableClientExamPlan['orgCode'].eq(orgCode))
        if date is not None:
            expr.append(tableClientExamPlan['date'].eq(date))
        if infoDate is not None:
            expr.append(tableClientExamPlan['infoDate'].eq(infoDate))
        if infoMethod is not None:
            expr.append(tableClientExamPlan['infoMethod'].eq(infoMethod))
        if infoStep is not None:
            expr.append(tableClientExamPlan['infoStep'].eq(infoStep))
        if error is not None:
            expr.append(tableClientExamPlan['error'].eq(error))
        if sendDate is not None:
            expr.append(tableClientExamPlan['sendDate'].eq(sendDate))
        cond = [
            tableClientExamPlan['id'].inlist(idList)
        ]
        self.db.updateRecords(tableClientExamPlan, expr=expr, where=cond)

    def updatePlanItemErrors(self, errorList):
        u"""
        :type errorList: list of OrderError
        """
        tableClientExamPlan = self.db.table('ClientExaminationPlan')
        self.db.insertFromDictList(
            tableClientExamPlan,
            dctList=[{'id'   : orderError.id,
                      'error': orderError.flkErrors}
                     for orderError in errorList if orderError.id > 0],
            keepOldFields=['id'],
            chunkSize=100
        )

    def getEventTypes(self, examKind):
        u""" Типы обращений по виду проф. мероприятия """
        if examKind not in self._examKindEventTypes:
            eventProfileCodes = ExamKind.getEventProfileCodes(examKind)
            if eventProfileCodes:
                tableEventType = self.db.table('EventType')
                tableEventProfile = self.db.table('rbEventProfile')

                table = tableEventProfile.innerJoin(tableEventType, [tableEventType['eventProfile_id'].eq(tableEventProfile['id']),
                                                                     tableEventType['deleted'].eq(0)])
                cond = [
                    tableEventProfile['regionalCode'].inlist(eventProfileCodes)
                ]
                eventTypes = self.db.getIdList(table, tableEventType['id'], cond)
            else:
                eventTypes = []

            self._examKindEventTypes[examKind] = eventTypes
        return self._examKindEventTypes[examKind]

    def getPlanItem(self, examPlanId):
        u"""
        :param examPlanId: ClientExaminationPlan.id
        :rtype: PlanItem
        """
        db = self.db
        tableAttach = db.table('ClientAttach')
        tableLastAttach = tableAttach.alias('LastAttach')
        tableExamPlan = db.table('ClientExaminationPlan')

        table = tableExamPlan
        table = table.leftJoin(tableLastAttach,
                               tableLastAttach['id'].eqStmt(db.selectMax(
                                   table=tableAttach,
                                   col=tableAttach['id'],
                                   where=[
                                       tableAttach['client_id'].eq(tableExamPlan['client_id']),
                                       tableAttach['attachType_id'].inlist(self.attachedAttachTypes),
                                       tableAttach['endDate'].isNull(),
                                       tableAttach['deleted'].eq(0)
                                   ])))
        cols = [
            tableExamPlan['*'],
            tableAttach['orgStructure_id'].alias('attachOrgStructureId')
        ]
        rec = db.getRecordEx(table, cols, tableExamPlan['id'].eq(examPlanId))
        if rec:
            attachOrgCode, attachSectionCode = CBookkeeperCode.getOrgCode(forceRef(rec.value('attachOrgStructureId')))
            return PlanItem(
                rid=forceRef(rec.value('id')),
                year=forceInt(rec.value('year')),
                month=forceInt(rec.value('month')),
                category=forceInt(rec.value('category')),
                orgCode=attachOrgCode,
                sectionCode=attachSectionCode,
                person=self.getPersonItem(forceRef(rec.value('client_id')))
            )

        return PlanItem()

    def toFactExecList(self, idList):
        u"""
        Список проведенных проф. мероприятий
        :param idList: [list of ClientExaminationPlan.id]
        :rtype: list of FactExec
        """
        db = self.db
        tableClient = db.table('Client')
        tableClientExamPlan = db.table('ClientExaminationPlan')
        tableDocument = db.table('ClientDocument')
        tableDocumentType = db.table('rbDocumentType')
        tableEvent = db.table('Event')
        tableOrganisation = db.table('Organisation')
        tableInsurer = db.table('Organisation').alias('Ins')
        tableInsurerHead = db.table('Organisation').alias('InsHead')
        tablePolicy = db.table('ClientPolicy')
        tablePolicyKind = db.table('rbPolicyKind')

        table = tableClientExamPlan
        table = table.innerJoin(tableClient, tableClient['id'].eq(tableClientExamPlan['client_id']))
        table = table.leftJoin(tableDocument, tableDocument['id'].eq(db.func.getClientDocumentId(tableClient['id'])))
        table = table.leftJoin(tableDocumentType, tableDocumentType['id'].eq(tableDocument['documentType_id']))
        table = table.leftJoin(tablePolicy, tablePolicy['id'].eq(db.func.getClientPolicyId(tableClient['id'], 1)))
        table = table.leftJoin(tablePolicyKind, tablePolicyKind['id'].eq(tablePolicy['policyKind_id']))
        table = table.leftJoin(tableInsurer, tableInsurer['id'].eq(tablePolicy['insurer_id']))
        table = table.leftJoin(tableInsurerHead, tableInsurerHead['id'].eq(tableInsurer['head_id']))
        table = table.leftJoin(tableEvent, tableEvent['id'].eq(tableClientExamPlan['event_id']))
        table = table.leftJoin(tableOrganisation, tableOrganisation['id'].eq(tableEvent['org_id']))

        cols = [
            tableClientExamPlan['id'],
            tableClientExamPlan['year'],
            tableClientExamPlan['month'],
            tableClientExamPlan['kind'],
            tableClientExamPlan['category'],
            tableClientExamPlan['step'],
            tableClientExamPlan['date'],

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
            db.ifnull(tableInsurerHead['OKATO'], tableInsurer['OKATO']).alias('insurerOKATO'),

            tableOrganisation['infisCode'].alias('orgCode')
        ]
        cond = [
            tableClientExamPlan['id'].inlist(idList)
        ]

        factExecs = []
        for rec in db.iterRecordList(table, cols, cond):
            person = PersonItem(
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
                policyNumber=forceString(rec.value('policyNumber')),
                policyType=forceInt(rec.value('policyType')),
                insurerCode=forceString(rec.value('insurerCode')),
                insuranceArea=forceString(rec.value('insurerOKATO')),
            )
            factExec = FactExec(
                rid=forceRef(rec.value('id')),
                orgCode=forceString(rec.value('orgCode')) or self.orgCode,
                date=forceDate(rec.value('date')),
                step=forceInt(rec.value('step')),
                person=person
            )
            factExecs.append(factExec)

        return factExecs

    def toPlanItemList(self, idList):
        u"""
        Персонализированный список лиц, подлежажих проф. мероприятиям
        :param idList: [list of ClientExaminationPlan.id]
        :rtype: list of PlanItem
        """
        db = self.db
        tableAttach = db.table('ClientAttach')
        tableLastAttach = tableAttach.alias('LastAttach')
        tableClientExamPlan = db.table('ClientExaminationPlan')
        tableClient = db.table('Client')
        tableDocument = db.table('ClientDocument')
        tableDocumentType = db.table('rbDocumentType')
        tableEvent = db.table('Event')
        tableEventType = db.table('EventType')
        tableEventProfile = db.table('rbEventProfile')
        tableEventResult = db.table('rbResult')
        tablePolicy = db.table('ClientPolicy')
        tablePolicyKind = db.table('rbPolicyKind')
        tableInsurer = db.table('Organisation').alias('Ins')
        tableInsurerHead = db.table('Organisation').alias('InsHead')

        table = tableClientExamPlan

        table = table.innerJoin(tableClient, tableClient['id'].eq(tableClientExamPlan['client_id']))
        table = table.leftJoin(tableDocument, tableDocument['id'].eq(db.func.getClientDocumentId(tableClient['id'])))
        table = table.leftJoin(tableDocumentType, tableDocumentType['id'].eq(tableDocument['documentType_id']))
        table = table.leftJoin(tablePolicy, tablePolicy['id'].eq(db.func.getClientPolicyId(tableClient['id'], 1)))
        table = table.leftJoin(tablePolicyKind, tablePolicyKind['id'].eq(tablePolicy['policyKind_id']))
        table = table.leftJoin(tableInsurer, tableInsurer['id'].eq(tablePolicy['insurer_id']))
        table = table.leftJoin(tableInsurerHead, tableInsurerHead['id'].eq(tableInsurer['head_id']))

        table = table.leftJoin(tableLastAttach,
                               tableLastAttach['id'].eqStmt(db.selectMax(tableAttach,
                                                                         tableAttach['id'],
                                                                         [tableAttach['client_id'].eq(tableClient['id']),
                                                                          tableAttach['attachType_id'].inlist(self.attachedAttachTypes),
                                                                          tableAttach['endDate'].isNull(),
                                                                          tableAttach['deleted'].eq(0)])))

        table = table.leftJoin(tableEvent, tableEvent['id'].eq(tableClientExamPlan['event_id']))
        table = table.leftJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
        table = table.leftJoin(tableEventProfile, tableEventProfile['id'].eq(tableEventType['eventProfile_id']))
        table = table.leftJoin(tableEventResult, tableEventResult['id'].eq(tableEvent['result_id']))

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
            db.ifnull(tableInsurerHead['OKATO'], tableInsurer['OKATO']).alias('insurerOKATO'),

            tableClientExamPlan['id'],
            tableClientExamPlan['year'],
            tableClientExamPlan['month'],
            tableClientExamPlan['kind'],
            tableClientExamPlan['category'],

            tableLastAttach['orgStructure_id'].alias('attachOrgStructureId'),

            tableEvent['execDate'],
            tableEventProfile['regionalCode'].alias('eventProfileCode')
        ]
        cond = [
            tableClientExamPlan['id'].inlist(idList)
        ]

        planItems = []
        for rec in db.iterRecordList(table, cols, cond):
            attachOrgCode, attachSectionCode = CBookkeeperCode.getOrgCode(forceRef(rec.value('attachOrgStructureId')))
            person = PersonItem(
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
                policyNumber=forceString(rec.value('policyNumber')),
                policyType=forceInt(rec.value('policyType')),
                insurerCode=forceString(rec.value('insurerCode')),
                insuranceArea=forceString(rec.value('insurerOKATO')),
            )
            planItem = PlanItem(
                rid=forceRef(rec.value('id')),
                kind=forceInt(rec.value('kind')),
                year=forceInt(rec.value('year')),
                month=forceInt(rec.value('month')),
                category=forceInt(rec.value('category')),
                orgCode=attachOrgCode,
                sectionCode=attachSectionCode,
                person=person
            )
            planItems.append(planItem)

        return planItems

    def selectClients(self, examKind, year, quarter=None, month=None, birthYearList=None, isDisabled=False,
                      socStatusClasses=None, socStatusTypes=None, excludeClients=None, notExists=True, attachSynced=True):
        u"""
        Отбор пациентов на диспансеризацию
        :param examKind: Тип диспансеризации
        :param year: Год планируемого проф. мероприятия
        :param quarter: Квартал
        :param month: Месяц
        :param birthYearList: Года рождения
        :param isDisabled: Признак инвалида
        :param socStatusClasses: [list of rbSoscStatusClass.id]
        :param socStatusTypes: [list of rbSocStatusType.id]
        :param excludeClients: [list of Client.id]: Исключить данных пациентов
        :param notExists: Исключить уже существующих в списке на этот год/квартал
        :param attachSynced: Прикрепление синхронизировано с ТФОМС
        :return: [list of Client.id]
        """
        db = self.db
        tableAttachType = db.table('rbAttachType')
        tableClient = db.table('Client')
        tableClientAttach = db.table('ClientAttach')
        tableClientDisability = db.table('ClientDisability')
        tableClientExamPlan = db.table('ClientExaminationPlan')
        tableClientSocStatus = db.table('ClientSocStatus')
        tableEvent = db.table('Event')

        attachCond = [
            tableClientAttach['deleted'].eq(0)
        ]

        curOrgStructureId = QtGui.qApp.currentOrgStructureId()
        if curOrgStructureId is not None:
            attachCond.append(tableClientAttach['orgStructure_id'].eq(curOrgStructureId))
        else:
            attachCond.append(tableClientAttach['LPU_id'].inlist(getOrganisationDescendants(QtGui.qApp.currentOrgId())))

        tableLastAttach = db.subQueryTable(
            db.selectStmt(tableClientAttach,
                          fields=[tableClientAttach['client_id'],
                                  db.max(tableClientAttach['id']).alias('attach_id')],
                          where=attachCond,
                          group=tableClientAttach['client_id']),
            alias='LastAttach'
        )  # TODO: последнее по id может не быть актуальным

        table = tableLastAttach
        table = table.innerJoin(tableClient, [tableClient['id'].eq(tableLastAttach['client_id']),
                                              tableClient['deleted'].eq(0)])
        table = table.innerJoin(tableClientAttach, tableClientAttach['id'].eq(tableLastAttach['attach_id']))
        table = table.innerJoin(tableAttachType, tableAttachType['id'].eq(tableClientAttach['attachType_id']))
        table = table.leftJoin(tableClientDisability, tableClientDisability['client_id'].eq(tableClient['id']))

        # Действующее прикрепление
        cond = [
            tableClientAttach['endDate'].isNull(),
            tableAttachType['code'].inlist([CAttachType.Territorial,
                                            CAttachType.Attached])
        ]
        if attachSynced:
            cond.append(tableClientAttach['sentToTFOMS'].eq(CAttachSentToTFOMS.Synced))

        # Исключить уже включенных в список
        if notExists:
            table = table.leftJoin(tableClientExamPlan, [tableClientExamPlan['client_id'].eq(tableClient['id']),
                                                         tableClientExamPlan['year'].eq(year)])
            cond.append(tableClientExamPlan['id'].isNull())

        # Год рождения
        if birthYearList:
            cond.append(db.dateYear(tableClient['birthDate']).inlist(birthYearList))
        else:
            cond.append(db.dateYear(tableClient['birthDate']).le(year - 18))
            if examKind == ExamKind.Preventive:
                birthYearList = self.getExamBirthYears(year)
                cond.append(db.dateYear(tableClient['birthDate']).notInlist(birthYearList))

        # Квартал
        if quarter is not None:
            cond.append(db.dateQuarter(tableClient['birthDate']).eq(quarter))

        # Месяц
        if month is not None:
            cond.append(db.dateMonth(tableClient['birthDate']).eq(month))

        # Включить/исключить из списка инвалидов
        if isDisabled and examKind == ExamKind.Dispensary:
            cond.append(tableClientDisability['id'].isNotNull())
            if socStatusClasses or socStatusTypes:
                table = table.innerJoin(tableClientSocStatus, [tableClientSocStatus['client_id'].eq(tableClient['id']),
                                                               tableClientSocStatus['deleted'].eq(0)])
                if socStatusClasses:
                    cond.append(tableClientSocStatus['socStatusClass_id'].inlist(socStatusClasses))
                if socStatusTypes:
                    cond.append(tableClientSocStatus['socStatusType_id'].inlist(socStatusTypes))
        else:
            cond.append(tableClientDisability['id'].isNull())

        # Для списков на ПО - исключить прошедших в предыдущем году
        if examKind == ExamKind.Preventive:
            eventTypeIdList = self.getEventTypes(examKind)
            if eventTypeIdList:
                cond.append(db.notExistsStmt(
                    table=tableEvent,
                    where=[
                        tableEvent['client_id'].eq(tableClient['id']),
                        tableEvent['eventType_id'].inlist(eventTypeIdList),
                        db.dateYear(tableEvent['execDate']).eq(year - 1),
                        tableEvent['deleted'].eq(0)
                    ]))

        idList = db.getDistinctIdList(table, tableClient['id'], cond)
        return list(set(idList).difference(set(excludeClients))) if excludeClients else idList

    def selectClientExamPlan(self, year, quarter=None, month=None, examKind=None, steps=None,
                             statuses=None, stepStatuses=None, notFinished=None, orgStructureId=None,
                             hasErrors=False, order=None):
        u"""
        Выборка из списков на проф. мероприятия
        :return: [list of ClientExamination.id]
        """
        db = self.db
        tableClient = db.table('Client')
        tableClientAttach = db.table('ClientAttach')
        tableClientExamPlan = db.table('ClientExaminationPlan')

        table = tableClientExamPlan
        table = table.innerJoin(tableClient, tableClient['id'].eq(tableClientExamPlan['client_id']))

        cond = [
            tableClientExamPlan['year'].eq(year),
            # tableClientExamPlan['status'].eq(ExamStatus.NotSent)
        ]
        if quarter is not None:
            cond.append(tableClientExamPlan['month'].inlist(Quarter.months(quarter)))
        if month is not None:
            cond.append(tableClientExamPlan['month'].eq(month))
        if examKind == ExamKindSpecials.DispExamDisabled:
            cond.extend([
                tableClientExamPlan['kind'].eq(ExamKind.Dispensary),
                tableClientExamPlan['category'].eq(PersonCategory.HasBenefits)
            ])
        elif examKind is not None:
            cond.append(tableClientExamPlan['kind'].eq(examKind))
        if steps:
            cond.append(tableClientExamPlan['step'].inlist(steps))
        if statuses:
            cond.append(tableClientExamPlan['status'].inlist(statuses))
        if stepStatuses:
            cond.append(tableClientExamPlan['stepStatus'].inlist(stepStatuses))
        if notFinished:
            cond.append(db.joinOr([
                tableClientExamPlan['step'].isNull(),
                tableClientExamPlan['step'].inlist(ExamStep.startingSteps)
            ]))
        if orgStructureId is not None:
            table = table.innerJoin(tableClientAttach, [
                tableClientAttach['client_id'].eq(tableClient['id']),
                tableClientAttach['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)),
                tableClientAttach['attachType_id'].inlist(self.attachedAttachTypes),
                tableClientAttach['endDate'].isNull(),
                tableClientAttach['deleted'].eq(0)
            ])
        if hasErrors:
            cond.append(tableClientExamPlan['error'].ne(''))

        if order is None:
            order = [
                tableClient['lastName'],
                tableClient['firstName'],
                tableClient['patrName']
            ]

        return db.getDistinctIdList(table, tableClientExamPlan['id'], cond, order)

    def createClientExamPlan(self, year, quarter, selectedMap):
        tableClientExamPlan = self.db.table('ClientExaminationPlan')
        fields = ['client_id', 'year', 'month', 'kind', 'category']

        chunkSize = 2000
        addedCount = 0
        for (examKind, category), clientIdList in selectedMap.items():
            for offset in xrange(0, len(clientIdList), chunkSize):
                idList = clientIdList[offset: offset + chunkSize]
                values = [(clientId, year, birthMonth, examKind, category)
                          for clientId, birthMonth in self.getClientBirthMonths(idList)]
                self.db.insertValues(tableClientExamPlan, fields, values)
                addedCount += len(idList)
        return addedCount

    def updateClientExaminationPlan(self, year, quarter=None):
        deleted = self.deleteIncorrectClients(year, quarter)
        started = {}
        finished = {}
        for kind in ExamKind.keys():
            started[kind] = self.updateExaminations(kind, finished=False, year=year, quarter=quarter)
            finished[kind] = self.updateExaminations(kind, finished=True, year=year, quarter=quarter)
        return deleted, started, finished

    def deleteIncorrectClients(self, year, quarter=None):
        u"""
        Удаление из списков удаленных, открепленных, умерших пациентов
        :return: кол-во удаленных
        """
        curDate = QtCore.QDate.currentDate()
        curOrgId = QtGui.qApp.currentOrgId()

        db = self.db
        tableAttachType = db.table('rbAttachType')
        tableClient = db.table('Client')
        tableClientAttach = db.table('ClientAttach')
        tableClientExamPlan = db.table('ClientExaminationPlan')

        table = tableClientExamPlan
        table = table.leftJoin(tableClient, [tableClient['id'].eq(tableClientExamPlan['client_id']),
                                             tableClient['deleted'].eq(0)])
        table = table.leftJoin(tableClientAttach, tableClientAttach['id'].eqStmt(
            db.selectMax(tableClientAttach,
                         tableClientAttach['id'],
                         [tableClientAttach['client_id'].eq(tableClient['id']),
                          tableClientAttach['LPU_id'].eq(curOrgId),
                          tableClientAttach['deleted'].eq(0)])
        ))
        table = table.leftJoin(tableAttachType, tableAttachType['id'].eq(tableClientAttach['attachType_id']))

        cond = [
            tableClientExamPlan['year'],
            db.joinOr([
                tableClient['id'].isNull(),
                tableClientAttach['id'].isNull(),
                tableClientAttach['endDate'].dateLe(curDate),
                tableAttachType['code'].eq(CAttachType.Dead)
            ])
        ]
        if quarter is not None:
            cond.append(tableClientExamPlan['month'].inlist(Quarter.months(quarter)))

        idList = db.getDistinctIdList(table, tableClientExamPlan['id'], cond)
        if idList:
            db.deleteRecord(tableClientExamPlan,
                            tableClientExamPlan['id'].inlist(idList))

        return len(idList)

    def updateExaminations(self, kind, finished=False, year=None, quarter=None, month=None):
        u""" Для пациентов в списках ищем законченные обращения по проф. мероприятиям и обновляем текущее состояние """
        eventTypes = self.getEventTypes(kind)
        if not eventTypes: return

        db = self.db
        tableEvent = db.table('Event')
        tableEventProfile = db.table('rbEventProfile')
        tableEventType = db.table('EventType')
        tableExamPlan = db.table('ClientExaminationPlan')
        tableMeidicalAidType = db.table('rbMedicalAidType')
        tableOrganisation = db.table('Organisation')
        tableResult = db.table('rbResult')

        table = tableExamPlan
        table = table.innerJoin(tableEvent, [tableEvent['client_id'].eq(tableExamPlan['client_id']),
                                             tableEvent['eventType_id'].inlist(eventTypes),
                                             tableEvent['deleted'].eq(0)])
        table = table.innerJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
        table = table.innerJoin(tableEventProfile, tableEventProfile['id'].eq(tableEventType['eventProfile_id']))
        table = table.innerJoin(tableMeidicalAidType, tableMeidicalAidType['id'].eq(tableEventType['medicalAidType_id']))
        table = table.leftJoin(tableOrganisation, tableOrganisation['id'].eq(tableEvent['org_id']))

        cols = [
            tableExamPlan['id'],
            tableEvent['id'].alias('eventId'),
            tableEvent['execDate' if finished else 'setDate'].alias('date'),
            tableEventProfile['regionalCode'].alias('profileCode'),
            tableMeidicalAidType['dispStage'],
            tableOrganisation['infisCode'].alias('orgCode')
        ]

        cond = [
            db.dateYear(tableEvent['setDate']).eq(tableExamPlan['year'])
        ]
        if finished:
            table = table.innerJoin(tableResult, tableResult['id'].eq(tableEvent['result_id']))
            cols.extend([
                tableResult['regionalCode'].alias('resultCode')
            ])
            cond.extend([
                tableEvent['execDate'].isNotNull(),
                db.joinOr([tableExamPlan['date'].isNull(),
                           tableExamPlan['step'].isNull(),
                           tableExamPlan['step'].notInlist(ExamStep.finishingSteps)])
            ])
        else:
            cond.extend([
                tableEvent['execDate'].isNull(),
                tableExamPlan['step'].isNull()
            ])
        cond.extend(self.getConditionList(year=year, quarter=quarter, month=month, kind=kind))

        updated = []
        for rec in db.iterRecordList(table, cols, cond):
            dispStage = forceInt(rec.value('dispStage'))
            resultCode = forceString(rec.value('resultCode'))
            step = ExamStep.getStep(kind, dispStage, resultCode)
            if step:
                updated.append({
                    'id'        : forceRef(rec.value('id')),
                    'event_id'  : forceRef(rec.value('eventId')),
                    'orgCode'   : forceString(rec.value('orgCode')) or self.orgCode,
                    'date'      : forceDate(rec.value('date')),
                    'step'      : step,
                    'stepStatus': ExamStatus.NotSent,
                    'sendDate'  : None
                })
        db.insertFromDictList(tableExamPlan, updated, keepOldFields=['id'], chunkSize=100)
        return len(updated)

    def processFactInvoices(self, factInvoices):
        u"""
        Обработка информации о фактически принятых к оплате счетах по проф. мероприятиям
        :type factInvoices: list of FactInvoice
        """
        updated = 0
        for invoice in factInvoices:  # type: FactInvoice
            planId = self._findPlanItem(invoice.person, year=invoice.year)
            if planId:
                self.updatePlanItem([planId],
                                    stepStatus=ExamStatus.UpdatedByTFOMS,
                                    orgCode=invoice.orgCode,
                                    step=ExamStep.getInvoiceStep(invoice.invoiceStatus, invoice.resultCode),
                                    date=invoice.endDate or invoice.begDate)
                updated += 1

        return updated

    def processFactInfos(self, factInfos):
        u"""
        Обработка информации об информировании граждан
        :type factInfos: list of FactInfo
        """
        updated = 0
        for factInfo in factInfos:  # type: FactInfo
            planId = self._findPlanItem(factInfo.person)
            if planId:
                self.updatePlanItem([planId],
                                    infoDate=factInfo.date,
                                    infoMethod=factInfo.method,
                                    infoStep=factInfo.step)
                updated += 1

        return updated

    def _findPlanItem(self, person, year=None, month=None):
        u"""
        Поиск планового пациента по информации о принятом к оплате счете
        :type person: PersonItem
        :return: ClientExaminationPlan.id
        """
        db = self.db
        tableClient = db.table('Client')
        tableExamPlan = db.table('ClientExaminationPlan')

        table = tableExamPlan
        table = table.innerJoin(tableClient, tableClient['id'].eq(tableExamPlan['client_id']))
        cols = [
            tableExamPlan['id']
        ]
        cond = [
            tableClient['lastName'].eq(person.lastName),
            tableClient['firstName'].eq(person.firstName),
            tableClient['birthDate'].eq(person.birthDate),
        ]
        if year is not None:
            cond.append(tableExamPlan['year'].eq(year))
        if month is not None:
            cond.append(tableExamPlan['month'].eq(month))
        if person.SNILS:
            cond.append(db.joinOr([tableClient['SNILS'].isNull(),
                                   tableClient['SNILS'].eq(person.SNILS)]))

        rec = db.getRecordEx(table, cols, cond)
        return forceRef(rec.value('id')) if rec else None

    def getNotSentPlanItems(self, selectedIds=None):
        u"""
        Список неотправленных в списках на плановые проф. мероприятия
        :return: [list of ClientExaminationPlan.id]
        """
        curDate = QtCore.QDate.currentDate()
        curMonth, curYear = curDate.month(), curDate.year()
        minYear = curYear if curMonth != 12 else curYear + 1
        minMonth = 1 if curMonth == 1 else curMonth % 12 + 1

        db = self.db
        tableClientExamPlan = db.table('ClientExaminationPlan')
        cond = [
            tableClientExamPlan['status'].eq(ExamStatus.NotSent)
        ]
        if selectedIds:
            cond.append(tableClientExamPlan['id'].inlist(selectedIds))
        else:
            cond.append(db.joinOr([
                tableClientExamPlan['year'].gt(minYear),
                db.joinAnd([
                    tableClientExamPlan['year'].eq(minYear),
                    tableClientExamPlan['month'].ge(minMonth)
                ])
            ]))

        return db.getIdList(tableClientExamPlan, tableClientExamPlan['id'], cond)

    def getNotSentFactExecs(self, selectedIds=None):
        u"""
        Список неотправленных изменений в проведении проф. мероприятий
        :return: [list of ClientExaminationPlan.id]
        """
        tableClientExamPlan = self.db.table('ClientExaminationPlan')
        cond = [
            tableClientExamPlan['status'].eq(ExamStatus.Sent),
            tableClientExamPlan['step'].isNotNull(),
            tableClientExamPlan['stepStatus'].eq(ExamStatus.NotSent)
        ]
        if selectedIds:
            cond.append(tableClientExamPlan['id'].inlist(selectedIds))
        return self.db.getIdList(tableClientExamPlan, tableClientExamPlan['id'], cond)

    def getClientExamInsurerList(self, year=None, quarter=None, month=None):
        u""" Список СМО для пациентов в списках
        :rtype: list[(unicode,unicode)]
        """
        db = self.db
        tableExamPlan = db.table('ClientExaminationPlan')
        tablePolicy = db.table('ClientPolicy')
        tableInsurer = db.table('Organisation')

        table = tableExamPlan
        table = table.innerJoin(tablePolicy, tablePolicy['id'].eq(db.func.getClientPolicyId(tableExamPlan['client_id'], 1)))
        table = table.innerJoin(tableInsurer, tableInsurer['id'].eq(tablePolicy['insurer_id']))
        cols = [
            tableInsurer['miacCode'].alias('code'),
            tableInsurer['shortName'].alias('name'),
        ]
        cond = self.getConditionList(year=year, quarter=quarter, month=month)
        cond.extend([
            tableInsurer['miacCode'].ne('')
        ])

        return [(forceString(rec.value('code')),
                 forceString(rec.value('name')))
                for rec in db.iterRecordList(table, cols, cond, isDistinct=True)]

    def toExportData(self, idList):
        u""" Экспорт в csv/xls
        :param idList: [list of ClientExaminationPlan.id]
        """
        tableClient = self.db.table('Client')
        tableExamPlan = self.db.table('ClientExaminationPlan')

        table = tableExamPlan
        table = table.innerJoin(tableClient, tableClient['id'].eq(tableExamPlan['client_id']))
        cols = [
            tableClient['id'].alias('clientId'),
            tableClient['lastName'],
            tableClient['firstName'],
            tableClient['patrName'],
            tableClient['birthDate'],
            tableExamPlan['kind'],
            tableExamPlan['year'],
            tableExamPlan['month'],
            tableExamPlan['error']
        ]
        cond = [
            tableExamPlan['id'].inlist(idList)
        ]
        order = [
            tableClient['lastName'],
            tableClient['firstName'],
            tableClient['patrName']
        ]
        return self.db.iterRecordList(table, cols, cond, order=order)
