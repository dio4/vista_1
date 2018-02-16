# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
import collections
from PyQt4 import QtCore, QtGui

from Events.Utils import getWorkEventTypeFilter
from Orgs.Utils import getOrgStructureDescendants
from RefBooks.Utils import CServiceTypeModel
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Ui_FinanceSummarySetupDialog import Ui_FinanceSummarySetupDialog
from library.DbComboBox import CDbModel
from library.DialogBase import CDialogBase
from library.Utils import forceBool, forceDouble, forceInt, forceRef, forceString, forceStringEx, firstMonthDay, \
    lastMonthDay, formatName


def getCond(params, additionalCondType=0):
    db = QtGui.qApp.db
    tableAccount = db.table('Account')
    tableAccountItem = db.table('Account_Item')
    tablePerson = db.table('Person')
    tableClientWork = db.table('ClientWork')
    tableAction = db.table('Action')
    tableVisit = db.table('Visit')
    tableEvent = db.table('Event')
    tableActionType = db.table('ActionType')
    tableOrgStructure_ActionType = db.table('OrgStructure_ActionType')

    cond = [tableAccountItem['reexposeItem_id'].isNull()]
    if params.get('accountItemIdList', None) is not None:
        cond.append(tableAccountItem['id'].inlist(params['accountItemIdList']))
    else:
        if params.get('accountIdList', None) is not None:
            cond.append(tableAccountItem['master_id'].inlist(params['accountIdList']))
        elif params.get('accountId', None):
            cond.append(tableAccountItem['master_id'].eq(params['accountId']))

        begDate = params.get('begDate', None)
        endDate = params.get('endDate', None)
        # Если выбран учет периода для даты выполнения услуг и тип условия соответствует условию для Actions
        if params.get('byActionEndDate', False):
            if additionalCondType == 2:  # Услуги
                if begDate:
                    cond.append(tableAction['endDate'].ge(params['begDate']))
                if endDate:
                    cond.append(tableAction['endDate'].lt(params['endDate'].addDays(1)))
            elif additionalCondType == 1:  # Посещения
                if begDate:
                    cond.append(tableVisit['date'].ge(params['begDate']))
                if endDate:
                    cond.append(tableVisit['date'].lt(params['endDate'].addDays(1)))
            else:
                if begDate:
                    cond.append(tableEvent['execDate'].ge(params['begDate']))
                if endDate:
                    cond.append(tableEvent['execDate'].lt(params['endDate'].addDays(1)))
        else:
            if begDate:
                cond.append(tableAccount['settleDate'].ge(params['begDate']))
            if endDate:
                cond.append(tableAccount['settleDate'].lt(params['endDate'].addDays(1)))

        if params.get('lstInsurer', None) and params.get('chkInsurer', False):
            cond.append(tableAccount['payer_id'].inlist(params['lstInsurer']))
        elif params.get('insurerId', None):
            cond.append(tableAccount['payer_id'].eq(params['insurerId']))

    if params.get('personId', None):
        cond.append(tablePerson['id'].eq(params['personId']))
    elif params.get('assistantId', None) and additionalCondType == 2:
        cond.append('Assistant.id = %d' % params.get('assistantId'))
    else:
        # Достаточно проверять только параментр byOrgStructAction и не проверять, действительно ли у нас "формирование счёта", потому что
        # при выборе "выполнения услуги", параметр bOSA будет сбрасываться автоматически.
        # т.е невозможна ситуация (params['byOrgStructAction'] && rbtnByFormingAccountDate.isChecked())
        if additionalCondType == 2 and params.get('byOrgStructAction', False):
            if params.get('orgStructureId', None):
                if params.get('withoutDescendants', False):
                    cond.append(tableOrgStructure_ActionType['master_id'].eq(params['orgStructureId']))
                else:
                    cond.append(tableOrgStructure_ActionType['master_id'].inlist(
                        getOrgStructureDescendants(params['orgStructureId'])))
        if params.get('orgStructureId', None):
            if params.get('withoutDescendants', False):
                cond.append(tablePerson['orgStructure_id'].eq(params['orgStructureId']))
            else:
                cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(params['orgStructureId'])))
        else:
            cond.append(db.joinOr([tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()),
                                   tablePerson['org_id'].isNull()]))
        if params.get('specialityId', None):
            cond.append(tablePerson['speciality_id'].eq(params['specialityId']))

    if params.get('podtver', None):
        if params.get('podtverType', 0) == 1:
            cond.append(tableAccountItem['date'].isNotNull())
            #            cond.append(tableAccountItem['number'].ne(''))
            cond.append(tableAccountItem['refuseType_id'].isNull())
        elif params.get('podtverType', 0) == 2:
            cond.append(tableAccountItem['date'].isNotNull())
            #            cond.append(tableAccountItem['number'].ne(''))
            cond.append(tableAccountItem['refuseType_id'].isNotNull())

        if params.get('podtverType', 0) != 0:
            if params.get('begDatePodtver', None):
                cond.append(tableAccountItem['date'].ge(params['begDatePodtver']))
            if params.get('endDatePodtver', None):
                cond.append(tableAccountItem['date'].lt(params['endDatePodtver'].addDays(1)))

            if params.get('refuseType', None) == 2:
                cond.append(tableAccountItem['refuseType_id'].eq(params['refuseType']))

    clientOrganisationId = params.get('clientOrganisationId', None)
    freeInputWork = params.get('freeInputWork', False)
    freeInputWorkValue = params.get('freeInputWorkValue', '')
    if clientOrganisationId or (freeInputWork and freeInputWorkValue):
        workCond = [tableAccountItem['master_id'].eq(tableAccount['id'])]
        additionalCond = {0: None,
                          1: tableVisit['event_id'].eq(tableEvent['id']),
                          2: tableAction['event_id'].eq(tableEvent['id'])}.get(additionalCondType, None)
        if additionalCond:
            workCond.append(additionalCond)
        workSubCond = []
        if clientOrganisationId:
            workSubCond.append(tableClientWork['org_id'].eq(clientOrganisationId))
        if (freeInputWork and freeInputWorkValue):
            workSubCond.append(tableClientWork['freeInput'].like(freeInputWorkValue))
        workCond.append(db.joinOr(workSubCond))
        cond.append(
            '''EXISTS(
            SELECT ClientWork.`client_id`
            FROM ClientWork
            LEFT JOIN Event ON Event.`client_id`=ClientWork.`client_id`
            LEFT JOIN Account_Item ON Account_Item.`event_id`=Event.`id` AND Account_Item.deleted = 0
            WHERE %s
            )''' % db.joinAnd(workCond)
        )

    financeId = params.get('typeFinanceId', None)
    if financeId:
        tableContract = db.table('Contract')
        if additionalCondType == 0:
            cond.append(tableContract['finance_id'].eq(financeId))
        elif additionalCondType == 1:
            cond.append(tableVisit['finance_id'].eq(financeId))
        elif additionalCondType == 2:
            cond.append(tableContract['finance_id'].eq(financeId))
    eventPurposeId = params.get('eventPurposeId', None)
    eventTypeId = params.get('eventTypeId', None)
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if eventPurposeId:
        cond.append(db.table('EventType')['purpose_id'].eq(eventPurposeId))

    detailServiceTypes = params.get('detailServiceTypes', False)
    serviceTypes = params.get('serviceTypes', None)
    if additionalCondType == 2 and detailServiceTypes and serviceTypes and len(serviceTypes) > 0:
        serviceTypesCond = tableActionType['serviceType'].inlist([str(t) for t in serviceTypes])
        cond.append(serviceTypesCond)

    return db.joinAnd(cond)


#    SUM(Account_Item.amount/(SELECT
#                            COUNT(D.id)
#                          FROM Diagnostic AS D
#                          LEFT JOIN rbDiagnosisType AS DT ON DT.id = D.diagnosisType_id
#                          WHERE DT.code in ('1','2') AND D.event_id = Event.id AND D.deleted=0
#                         )) AS amount,
#    SUM(Account_Item.sum/(SELECT
#                            COUNT(D.id)
#                          FROM Diagnostic AS D
#                          LEFT JOIN rbDiagnosisType AS DT ON DT.id = D.diagnosisType_id
#                          WHERE DT.code in ('1','2') AND D.event_id = Event.id AND D.deleted=0
#                         )) AS sum,

def getOrder(params):
    orderList = []
    db = QtGui.qApp.db
    tableAccount = db.table('Account')
    if params.get('insurerId') or (params.get('lstInsurer') and params.get('chkInsurer')):
        orderList.append(forceString(tableAccount['payer_id']))
    order = u'Order by %s' % (u', '.join(orderList)) if orderList else u''
    return order


def selectDataByEvents(params):
    stmt = """
SELECT
    rbSpeciality.name as specialityName,
    Person.speciality_id as speciality_id,
    Person.lastName, Person.firstName, Person.patrName, Person.code,
    CONCAT_WS(' ', Client.lastName, Client.firstName, Client.patrName) AS clientName,
    rbService.id AS serviceId, rbService.name AS serviceName, rbService.code AS serviceCode,
    IF(Visit.id IS NULL, 1, (SELECT COUNT(1) FROM Visit WHERE Visit.event_id = Event.id AND Visit.deleted=0 )) as sumDivider,
    Account_Item.amount AS amount,
    Account_Item.sum AS sum,
    LEAST(tariff.federalPrice * IF(tariff.federalLimitation = 0,
                                   Account_Item.amount,
                                   LEAST(tariff.federalLimitation, Account_Item.amount)),
          Account_Item.sum) AS federalSum,
    Account_Item.uet AS uet,
    (Account_Item.date IS NOT NULL AND Account_Item.number != '' AND Account_Item.refuseType_id IS NULL) AS exposed,
    (Account_Item.date IS NOT NULL AND Account_Item.number != '' AND Account_Item.refuseType_id IS NOT NULL) AS refused
    , OrgStructure.id AS orgStructureId
    , OrgStructure.name AS orgStructureName
FROM Account_Item
LEFT JOIN Account         ON Account.id = Account_Item.master_id AND Account.deleted = 0
LEFT JOIN rbService       ON rbService.id = Account_Item.service_id
LEFT JOIN Event           ON Event.id = Account_Item.event_id
LEFT JOIN EventType       ON EventType.id = Event.eventType_id
LEFT JOIN Client          ON Client.id = Event.client_id
LEFT JOIN Visit           ON Visit.event_id = Event.id AND Visit.deleted = 0
LEFT JOIN Person          ON Person.id = IF(Visit.id IS NULL, Event.execPerson_id, Visit.person_id) AND Person.retired = 0
LEFT JOIN rbSpeciality    ON rbSpeciality.id = Person.speciality_id
LEFT JOIN Contract_Tariff
            AS tariff     ON tariff.id = Account_Item.tariff_id
LEFT JOIN Contract ON Contract.id = Event.contract_id
LEFT JOIN OrgStructure ON OrgStructure.id = Person.orgStructure_id
WHERE
    Account_Item.visit_id IS NULL
    AND Account_Item.deleted = 0
    AND Account_Item.action_id IS NULL
    AND %s
    """
    db = QtGui.qApp.db
    return db.query(stmt % getCond(params))


def selectDataByVisits(params):
    stmt = """
SELECT
    rbSpeciality.name as specialityName,
    Person.speciality_id as speciality_id,
    Person.lastName, Person.firstName, Person.patrName, Person.code,
    CONCAT_WS(' ', Client.lastName, Client.firstName, Client.patrName) AS clientName,
    rbService.id AS serviceId, rbService.name AS serviceName, rbService.code AS serviceCode,
    1 AS sumDivider,
    Account_Item.amount AS amount,
    Account_Item.sum AS sum,
    LEAST(tariff.federalPrice * IF(tariff.federalLimitation = 0,
                                   Account_Item.amount,
                                   LEAST(tariff.federalLimitation, Account_Item.amount)),
          Account_Item.sum) AS federalSum,
    Account_Item.uet AS uet,
    (Account_Item.date IS NOT NULL AND Account_Item.number != '' AND Account_Item.refuseType_id IS NULL) AS exposed,
    (Account_Item.date IS NOT NULL AND Account_Item.number != '' AND Account_Item.refuseType_id IS NOT NULL) as refused
    , OrgStructure.id AS orgStructureId
    , OrgStructure.name AS orgStructureName
FROM Account_Item
LEFT JOIN Account      ON Account.id = Account_Item.master_id AND Account.deleted = 0
LEFT JOIN rbService    ON rbService.id = Account_Item.service_id
LEFT JOIN Visit        ON Visit.id = Account_Item.visit_id
LEFT JOIN Person       ON Person.id = Visit.person_id AND Person.retired = 0
LEFT JOIN rbSpeciality ON rbSpeciality.id = Person.speciality_id
LEFT JOIN Contract_Tariff AS tariff ON tariff.id = Account_Item.tariff_id
LEFT JOIN Event        ON Event.id = Visit.event_id
LEFT JOIN EventType    ON EventType.id = Event.eventType_id
LEFT JOIN Client       ON Client.id = Event.client_id
LEFT JOIN Contract     ON Contract.id = Event.contract_id
LEFT JOIN OrgStructure ON OrgStructure.id = Person.orgStructure_id
WHERE
    Account_Item.visit_id IS NOT NULL
    AND Account_Item.deleted = 0
    AND Account_Item.action_id IS NULL
    AND Visit.deleted = 0
    AND %s
    """
    db = QtGui.qApp.db
    return db.query(stmt % getCond(params, 1))


def selectDataByActions(params):
    stmt = """
SELECT
    rbSpeciality.name as specialityName,
    Person.speciality_id as speciality_id,
    Person.lastName, Person.firstName, Person.patrName, Person.code,
    CONCAT_WS(' ', Client.lastName, Client.firstName, Client.patrName) AS clientName,
    rbService.id AS serviceId, rbService.name AS serviceName, rbService.code AS serviceCode,
    1 AS sumDivider,
    Account_Item.amount AS amount,
    Account_Item.sum AS sum,
    LEAST(tariff.federalPrice * IF(tariff.federalLimitation = 0,
                                   Account_Item.amount,
                                   LEAST(tariff.federalLimitation, Account_Item.amount)),
          Account_Item.sum) AS federalSum,
    Account_Item.uet AS uet,
    (Account_Item.date IS NOT NULL AND Account_Item.number != '' AND Account_Item.refuseType_id IS NULL) AS exposed,
    (Account_Item.date IS NOT NULL AND Account_Item.number != '' AND Account_Item.refuseType_id IS NOT NULL) as refused,
    Assistant.lastName AS assistantLastName, Assistant.firstName AS assistantFirstName, Assistant.patrName AS assistantPatrName, Assistant.code AS assistantCode
    , OrgStructure.id AS orgStructureId
    , OrgStructure.name AS orgStructureName
    , ActionType.serviceType AS serviceType
FROM Account_Item
LEFT JOIN Account      ON Account.id = Account_Item.master_id AND Account.deleted = 0
LEFT JOIN rbService    ON rbService.id = Account_Item.service_id
LEFT JOIN Action       ON Action.id = Account_Item.action_id
LEFT JOIN ActionType   ON Action.actionType_id = ActionType.id
LEFT JOIN Person       ON Person.id = Action.person_id AND Person.retired = 0
LEFT JOIN Person
            AS Assistant  ON Assistant.id = (SELECT A_A.person_id
                                             FROM Action_Assistant AS A_A
                                             INNER JOIN rbActionAssistantType AS rbAAT ON rbAAT.id = A_A.assistantType_id
                                             WHERE A_A.action_id = Action.id AND rbAAT.code like 'assistant'
                                             LIMIT 1) AND Assistant.retired = 0
LEFT JOIN rbSpeciality ON rbSpeciality.id = Person.speciality_id
LEFT JOIN Contract_Tariff AS tariff ON tariff.id = Account_Item.tariff_id
LEFT JOIN Event ON Event.id = Action.event_id
LEFT JOIN EventType ON EventType.id = Event.eventType_id
LEFT JOIN Client ON Client.id = Event.client_id
LEFT JOIN Contract ON Contract.id = IF(Action.contract_id IS NULL, Event.contract_id, Action.contract_id)
LEFT JOIN OrgStructure ON OrgStructure.id = Person.orgStructure_id
WHERE
    Account_Item.visit_id IS NULL
    AND Account_Item.deleted = 0
    AND Account_Item.action_id IS NOT NULL
    AND %s
    """
    db = QtGui.qApp.db
    return db.query(stmt % getCond(params, 2))


docServiceTypeName = [
    u'прочие',
    u'консультация',
    u'консультация',
    u'процедуры',
    u'операция',
    u'анализы',
    u'лечение',
    u'расходники',
    u'оплата палат',
    u'реанимация',
    u'профиль',
    u'лабораторные исследования',
]


class CFinanceSummaryByDoctors(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Финансовая сводка по врачам/ассистентам')

    def build(self, description, params):
        def zip_dicts(obj):
            def update(d, u):
                for k, v in u.iteritems():
                    if isinstance(v, collections.Mapping):
                        r = update(d.get(k, {}), v)
                        d[k] = r
                    else:
                        d[k] = u[k]
                return d

            return reduce(update, obj.values(), {})

        def sum_lists(l, r):
            out = [0] * reportRowSize
            for i in xrange(reportRowSize):
                out[i] = l[i] + r[i]
            return out

        def printAll(table, reportData, indent, locale):
            totalByReport = printDoctorGroups(table, reportData, indent, locale)
            self.addTotal(table, u'Всего', totalByReport, locale)

        def printDoctorGroups(table, reportData, indent, locale):
            printHeadAndTotal = expandDoctorGroups
            printLeaf = not expandDoctorGroups
            groupTotalText = indent + u'всего по %s' % (
            u'специальности' if groupBy == CFinanceSummarySetupDialog.groupBySpeciality else u'отделению')
            total = [0] * reportRowSize

            if printLeaf or printHeadAndTotal:
                doctorGroups = reportData.keys()
                doctorGroups.sort()
                for doctorGroup in doctorGroups:
                    if printHeadAndTotal:
                        self.addHeader(table, 0, 8, doctorGroup)
                    totalByDoctorGroup = printDoctors(table, reportData[doctorGroup], indent + '    ', locale)
                    total = sum_lists(total, totalByDoctorGroup)
                    if printLeaf:
                        self.addLine(table, indent + doctorGroup, None, totalByDoctorGroup, locale)
                    if printHeadAndTotal:
                        self.addTotal(table, groupTotalText, totalByDoctorGroup, locale)
            else:
                total = printDoctors(table, zip_dicts(reportData), indent + '    ', locale)

            return total

        def printDoctors(table, reportData, indent, locale):
            isLeaf = not detailService and not detailServiceTypes and not detailPatients
            printHeadAndTotal = expandDoctorGroups and not isLeaf
            printLeaf = expandDoctorGroups and isLeaf
            doctorTotalText = indent + u'всего по %s' % (
            u'врачу' if (isByDoctorReport and not groupAssistant) else u'ассистенту')
            total = [0] * reportRowSize

            if printLeaf or printHeadAndTotal:
                doctors = reportData.keys()
                doctors.sort()
                for doctorName, doctorCode in doctors:
                    if printHeadAndTotal:
                        self.addHeader(table, 2, 7, indent + doctorName, doctorCode)
                    totalByDoctor = printPatients(table, reportData[(doctorName, doctorCode)], indent + '    ', locale)
                    total = sum_lists(total, totalByDoctor)
                    if printLeaf:
                        self.addLine(table, indent + doctorName, doctorCode, totalByDoctor, locale)
                    if printHeadAndTotal:
                        self.addTotal(table, doctorTotalText, totalByDoctor, locale)
            else:
                total = printPatients(table, zip_dicts(reportData), indent + '    ', locale)
            return total

        def printPatients(table, reportData, indent, locale):
            isLeaf = not detailService and not detailServiceTypes
            printHeadAndTotal = expandDoctorGroups and detailPatients and not isLeaf
            printLeaf = expandDoctorGroups and detailPatients and isLeaf
            patientTotalText = indent + u'всего по пациенту'
            total = [0] * reportRowSize

            if printHeadAndTotal or printLeaf:
                patients = reportData.keys()
                patients.sort()
                for patient in patients:
                    if printHeadAndTotal:
                        self.addHeader(table, 2, 7, indent + u'Пациент: ' + patient, None)
                    totalByPatient = printServiceTypes(table, reportData[patient], indent + '    ', locale)
                    total = sum_lists(total, totalByPatient)
                    if printLeaf:
                        self.addLine(table, indent + u'Пациент: ' + patient, None, totalByPatient, locale)
                    if printHeadAndTotal:
                        self.addTotal(table, patientTotalText, totalByPatient, locale)
            else:
                total = printServiceTypes(table, zip_dicts(reportData), indent + '    ', locale)
            return total

        def printServiceTypes(table, reportData, indent, locale):
            isLeaf = not detailService
            printHeadAndTotal = expandDoctorGroups and detailServiceTypes and not isLeaf
            printLeaf = expandDoctorGroups and detailServiceTypes and isLeaf
            serviceTypeTotalText = indent + u'всего по виду услуги'
            total = [0] * reportRowSize
            addIndent = '    ' if detailServiceTypes else ''

            if printHeadAndTotal or printLeaf:
                serviceTypes = reportData.keys()
                serviceTypes.sort()
                for serviceType in serviceTypes:
                    if printHeadAndTotal:
                        self.addHeader(table, 0, 10, indent + u'Вид услуги: ' + docServiceTypeName[serviceType])
                    totalByServiceType = printServices(table, reportData[serviceType], indent + addIndent, locale)
                    total = sum_lists(total, totalByServiceType)
                    if printLeaf:
                        self.addLine(table, indent + u'Вид услуги: ' + docServiceTypeName[serviceType], None,
                                     totalByServiceType, locale)
                    if printHeadAndTotal:
                        self.addTotal(table, serviceTypeTotalText, totalByServiceType, locale)
            else:
                total = printServices(table, zip_dicts(reportData), indent + addIndent, locale)
            return total

        def printServices(table, reportData, indent, locale):
            printLeaf = expandDoctorGroups and detailService
            total = [0] * reportRowSize

            # "склеиваем" одинаковые сервисы
            # (пришлось добавить четвертый уникальный элемент в ключ, чтобы они не перекрывались)
            serviceKeys = set(x[:3] for x in reportData.keys())
            reportData = dict(
                (key, reduce(sum_lists, [v for (k, v) in reportData.iteritems() if k[:3] == key], [0] * reportRowSize))
                for key in serviceKeys)
            services = reportData.keys()
            services.sort()
            for serviceKey in services:
                reportLine = reportData[serviceKey]
                for j in xrange(reportRowSize):
                    total[j] += reportLine[j]
                if printLeaf:
                    serviceId, serviceCode, serviceName = serviceKey
                    self.addLine(table, indent + serviceName, serviceCode, reportLine, locale)
            return total

        reportRowSize = 9
        reportData = {}
        detailService = params.get('detailService', False)
        detailServiceTypes = params.get('detailServiceTypes', False)
        isByDoctorReport = params.get('assistantId', None) is None
        groupBy = params.get('groupBy', CFinanceSummarySetupDialog.groupBySpeciality)
        groupAssistant = params.get('groupAssistant', False)
        expandDoctorGroups = params.get('expandDoctorGroups', True)
        detailPatients = params.get('detailPatients', False)

        def processQuery(query, isByDoctorReport=True, groupBy=CFinanceSummarySetupDialog.groupBySpeciality):
            self.addQueryText(forceString(query.lastQuery()))
            i = 0
            while query.next():
                record = query.record()
                groupByName = forceString(record.value(
                    'specialityName')) if groupBy == CFinanceSummarySetupDialog.groupBySpeciality else forceString(
                    record.value('orgStructureName'))
                lastName = forceString(
                    record.value('lastName')) if isByDoctorReport and not groupAssistant else forceString(
                    record.value('assistantLastName'))
                firstName = forceString(
                    record.value('firstName')) if isByDoctorReport and not groupAssistant else forceString(
                    record.value('assistantFirstName'))
                patrName = forceString(
                    record.value('patrName')) if isByDoctorReport and not groupAssistant else forceString(
                    record.value('assistantPatrName'))
                doctorCode = forceString(
                    record.value('code')) if isByDoctorReport and not groupAssistant else forceString(
                    record.value('assistantCode'))
                clientName = forceString(record.value('clientName'))
                serviceId = forceRef(record.value('serviceId'))
                serviceName = forceString(record.value('serviceName'))
                serviceCode = forceString(record.value('serviceCode'))
                sumDivider = forceInt(record.value('sumDivider'))

                amount = forceDouble(record.value('amount')) / sumDivider
                if amount == int(amount):
                    amount = int(amount)
                sum = forceDouble(record.value('sum')) / sumDivider
                isWithoutModernisation = params.get('withoutModernisation', False)
                if isWithoutModernisation:
                    federalSum = forceDouble(record.value('federalSum')) / sumDivider
                    sum = sum - federalSum
                uet = forceDouble(record.value('uet')) / sumDivider
                exposed = forceBool(record.value('exposed'))
                refused = forceBool(record.value('refused'))

                doctorGroup = groupByName if groupByName else (u'Без указания %s' % (
                u'специальности' if groupBy == CFinanceSummarySetupDialog.groupBySpeciality else u'отделения'))
                name = formatName(lastName, firstName, patrName)
                doctorName = name if name else u'Без указания врача/ассистента'
                serviceType = forceInt(record.value('serviceType')) if detailServiceTypes else None
                serviceKey = (serviceId, serviceCode, serviceName if serviceId else u'Услуга не указана', i)
                # if detailService else None
                reportLine = reportData.setdefault(doctorGroup, {}).setdefault((doctorName, doctorCode), {}).setdefault(
                    clientName, {}).setdefault(serviceType, {}).setdefault(serviceKey, [0] * reportRowSize)

                reportLine[0] += amount
                reportLine[1] += uet
                reportLine[2] += sum
                if exposed:
                    reportLine[3] += amount
                    reportLine[4] += uet
                    reportLine[5] += sum
                if refused:
                    reportLine[6] += amount
                    reportLine[7] += uet
                    reportLine[8] += sum

                i += 1

        query = selectDataByEvents(params)
        processQuery(query, isByDoctorReport, groupBy)
        query = selectDataByVisits(params)
        processQuery(query, isByDoctorReport, groupBy)
        query = selectDataByActions(params)
        processQuery(query, isByDoctorReport, groupBy)

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)

        tableColumns = [
            ('40%', [u'Врач' if isByDoctorReport and not groupAssistant
                     else u'Ассистент', u'ФИО'], CReportBase.AlignLeft),
            ('6%', [u'', u'код'], CReportBase.AlignLeft),
            ('6%', [u'Всего', u'кол-во'], CReportBase.AlignRight),
            ('6%', [u'', u'УЕТ'], CReportBase.AlignRight),
            ('6%', [u'', u'руб'], CReportBase.AlignRight),
            ('6%', [u'Оплачено', u'кол-во'], CReportBase.AlignRight),
            ('6%', [u'', u'УЕТ'], CReportBase.AlignRight),
            ('6%', [u'', u'руб'], CReportBase.AlignRight),
            ('6%', [u'Отказано', u'кол-во'], CReportBase.AlignRight),
            ('6%', [u'', u'УЕТ'], CReportBase.AlignRight),
            ('6%', [u'', u'руб'], CReportBase.AlignRight),
        ]
        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 1, 2)
        table.mergeCells(0, 2, 1, 3)
        table.mergeCells(0, 5, 1, 3)
        table.mergeCells(0, 8, 1, 3)

        locale = QtCore.QLocale()

        printAll(table, reportData, '', locale)

        return doc

    def addHeader(self, table, mergeFrom, mergeNum, title, code=None):
        i = table.addRow()
        table.setText(i, 0, title, CReportBase.TableHeader)
        if code is not None:
            table.setText(i, 1, code, CReportBase.TableHeader)
        table.mergeCells(i, mergeFrom, 1, mergeNum)

    def addLine(self, table, title, code, reportLine, locale):
        i = table.addRow()
        table.setText(i, 0, title)
        if code is None:
            table.mergeCells(i, 0, 1, 2)
        else:
            table.setText(i, 1, code)
        for j in xrange(0, len(reportLine), 3):
            table.setText(i, j + 2, self.formatDouble(float(reportLine[j]), locale))
        for j in xrange(1, len(reportLine), 3):
            table.setText(i, j + 2, self.formatDouble(float(reportLine[j]), locale))
        for j in xrange(2, len(reportLine), 3):
            table.setText(i, j + 2, self.formatDouble(float(reportLine[j]), locale))

    def addTotal(self, table, title, reportLine, locale):
        i = table.addRow()
        table.mergeCells(i, 0, 1, 2)
        table.setText(i, 0, title, CReportBase.TableTotal)
        for j in xrange(0, len(reportLine), 3):
            table.setText(i, j + 2, self.formatDouble(float(reportLine[j]), locale))
        for j in xrange(1, len(reportLine), 3):
            table.setText(i, j + 2, self.formatDouble(float(reportLine[j]), locale))
        for j in xrange(2, len(reportLine), 3):
            table.setText(i, j + 2, self.formatDouble(float(reportLine[j]), locale))

    def formatDouble(self, value, locale):
        if QtGui.qApp.region() == '23':
            return u'{0:.2f}'.format(value).replace(',', ' ').replace('.', ',')
        else:
            return locale.toString(value, 'f', 2)


class CFinanceSummaryByDoctorsEx(CFinanceSummaryByDoctors):
    def exec_(self, accountIdList=None):
        self.accountIdList = accountIdList
        CFinanceSummaryByDoctors.exec_(self)

    def getSetupDialog(self, parent):
        result = CFinanceSummarySetupDialog(parent)
        result.setVisibleGroupBy(True)
        result.setVisibleDetailService(True)
        result.setVisibleClientOrganisation(True)
        result.setVisibleAssistant(True)
        result.setVisibleFinance(True)
        result.chkGroupAssistant.setVisible(True)
        result.setTitle(self.title())
        return result

    def build(self, params):
        params['accountIdList'] = self.accountIdList
        return CFinanceSummaryByDoctors.build(self, '\n'.join(self.getDescription(params)), params)


class CFinanceSummarySetupDialog(CDialogBase, Ui_FinanceSummarySetupDialog):
    groupBySpeciality = 0
    groupByOrgStructure = 1

    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.cmbEventPurpose.setTable('rbEventTypePurpose', True, filter='code != \'0\'')
        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())
        self.cmbSpeciality.setTable('rbSpeciality', True)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbInsurerDoctors.setAddNone(True)
        self.cmbRefuseType.setTable('rbPayRefuseType', True)
        self.cmbPodtver.addItem(u'без подтверждения')
        self.cmbPodtver.addItem(u'оплаченные')
        self.cmbPodtver.addItem(u'отказанные')
        self.setVisibleGroupBy(False)
        self.setVisibleDetailService(False)
        self.setVisibleClientOrganisation(False)
        self.setVisibleAssistant(False)
        self.setVisibleFinance(False)
        self.setVisibleInsurerList(False)
        self.setVisibleByOrgStructAction(False)
        self.cmbFinance.setTable('rbFinance', True)
        self.chkGroupAssistant.setVisible(False)
        self.chkGroupAssistant.setEnabled(False)
        if self.rbtnByActionEndDate.isChecked() and self.chkDetailService.isChecked():
            self.chkGroupAssistant.setEnabled(True)
            self.cmbPerson.setEnabled(False)
            self.on_chkGroupAssistant_clicked(False)
        if not self.rbtnByFormingAccountDate.isChecked():
            self.chkByOrgStructAction.setEnabled(False)
        self.addModels('ServiceType', CServiceTypeModel(1, 10))
        self.lstServiceTypes.setModel(self.modelServiceType)
        self.lstServiceTypes.selectAll()
        self.addModels('Insurer', CDbModel(self))
        self.modelInsurer.setTable('Organisation')
        self.modelInsurer.setAddNone(False)
        self.modelInsurer.setNameField('CONCAT(infisCode,\'| \', shortName)')
        self.modelInsurer.setFilter('isInsurer = 1 AND deleted = 0')
        self.setModels(self.lstInsurerDoctors, self.modelInsurer, self.selectionModelInsurer)

    def setVisibleGroupBy(self, value):
        self.lblGroupBy.setVisible(value)
        self.cmbGroupBy.setVisible(value)

    def setVisibleDetailService(self, value):
        self.chkDetailService.setVisible(value)

    def setVisibleClientOrganisation(self, value):
        self._clientOrganisationAvailable = value
        self.cmbClientOrganisation.setVisible(value)
        self.lblClientOrganisation.setVisible(value)

    def setVisibleAssistant(self, value):
        self._assistantAvailable = value
        self.cmbAssistant.setVisible(value)
        self.lblAssistant.setVisible(value)

    def setVisibleDescendants(self, value):
        self.chkWithoutDescendants.setVisible(value)

    def setVisibleFinance(self, value):
        self.lblFinance.setVisible(value)
        self.cmbFinance.setVisible(value)

    def setVisibleInsurerList(self, value):
        self.chkInsurerDoctors.setEnabled(value)
        self.lstInsurerDoctors.setVisible(value)

    def setVisibleByOrgStructAction(self, value):
        self.chkByOrgStructAction.setEnabled(value)
        self.chkByOrgStructAction.setVisible(value)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        date = QtCore.QDate.currentDate().addDays(-3)
        self.chkExpandDoctorGroups.setChecked(params.get('expandDoctorGroups', True))
        self.edtBegDate.setDate(params.get('begDate', firstMonthDay(date)))
        self.edtEndDate.setDate(params.get('endDate', lastMonthDay(date)))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.chkWithoutDescendants.setChecked(params.get('withoutDescendants', False))
        self.cmbSpeciality.setValue(params.get('specialityId', None))
        self.cmbPerson.setValue(params.get('personId', None))
        if self.cmbAssistant.isEnabled() and self._assistantAvailable:
            self.cmbAssistant.setValue(params.get('assistantId', None))
        self.chkInsurerDoctors.setChecked(params.get('chkInsurer', False))
        self.on_chkInsurerDoctors_clicked(params.get('chkInsurer', False))
        self.cmbInsurerDoctors.setValue(params.get('insurerId', None))
        self.chkPodtver.setChecked(params.get('podtver', False))
        self.edtBegDatePodtver.setDate(params.get('begDatePodtver', firstMonthDay(date)))
        self.edtEndDatePodtver.setDate(params.get('endDatePodtver', lastMonthDay(date)))
        self.cmbPodtver.setCurrentIndex(params.get('podtverType', 0))
        self.cmbRefuseType.setValue(params.get('refuseType', None))
        self.chkWithoutModernisation.setChecked(params.get('withoutModernisation', False))
        self.chkDetailService.setChecked(params.get('detailService', False))
        self.chkDetailService.setEnabled(self.chkExpandDoctorGroups.isChecked())
        self.chkDetailServiceTypes.setChecked(params.get('detailServiceTypes', False))
        self.chkDetailServiceTypes.setEnabled(self.chkExpandDoctorGroups.isChecked())
        self.chkDetailPatients.setChecked(params.get('detailPatients', False))
        self.chkDetailPatients.setEnabled(self.chkExpandDoctorGroups.isChecked())
        self.lstServiceTypes.setEnabled(
            self.chkDetailServiceTypes.isChecked() and self.chkExpandDoctorGroups.isChecked())
        self.cmbClientOrganisation.setValue(params.get('clientOrganisationId', None))
        self.chkFreeInputWork.setChecked(params.get('freeInputWork', False))
        self.edtFreeInputWork.setText(params.get('freeInputWorkValue', ''))
        self.rbtnByActionEndDate.setChecked(params.get('byActionEndDate', False))
        self.cmbGroupBy.setCurrentIndex(params.get('groupBy', self.groupBySpeciality))
        self.cmbFinance.setValue(params.get('typeFinanceId', None))
        self.chkGroupAssistant.setChecked(params.get('groupAssistant', False))
        self.cmbEventPurpose.setValue(params.get('eventPurposeId', None))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.chkByOrgStructAction.setChecked(params.get('byOrgStructAction', False))

        selectedServiceTypes = params.get('serviceTypes')
        if selectedServiceTypes is not None:
            flags = self.lstServiceTypes.selectionCommand(QtCore.QModelIndex())
            selectionModel = self.lstServiceTypes.selectionModel()
            model = self.lstServiceTypes.model()
            self.lstServiceTypes.clearSelection()
            for idx in selectedServiceTypes:
                selectionModel.select(model.index(idx), flags)

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['withoutDescendants'] = self.chkWithoutDescendants.isChecked()
        result['specialityId'] = self.cmbSpeciality.value()
        result['personId'] = self.cmbPerson.value() if self.cmbPerson.isEnabled() else None
        result['assistantId'] = self.cmbAssistant.value() if self.cmbAssistant.isEnabled() else None
        result['chkInsurer'] = self.chkInsurerDoctors.isChecked()
        result['insurerId'] = self.cmbInsurerDoctors.value()
        result['lstInsurer'] = [self.modelInsurer.getId(index.row()) for index in
                                self.lstInsurerDoctors.selectedIndexes()]
        result['podtver'] = self.chkPodtver.isChecked()
        result['podtverType'] = self.cmbPodtver.currentIndex()
        result['begDatePodtver'] = self.edtBegDatePodtver.date()
        result['endDatePodtver'] = self.edtEndDatePodtver.date()
        result['refuseType'] = self.cmbRefuseType.value()
        result['freeInputWork'] = self.chkFreeInputWork.isChecked()
        result['freeInputWorkValue'] = forceStringEx(self.edtFreeInputWork.text())
        result['withoutModernisation'] = self.chkWithoutModernisation.isChecked()
        result['eventPurposeId'] = self.cmbEventPurpose.value()
        result['eventTypeId'] = self.cmbEventType.value()
        result['serviceTypes'] = [idx.row() for idx in self.lstServiceTypes.selectionModel().selectedIndexes()]
        result['detailService'] = self.chkDetailService.isChecked()
        result['detailServiceTypes'] = self.chkDetailServiceTypes.isChecked()
        result['byOrgStructAction'] = self.chkByOrgStructAction.isChecked()
        result['expandDoctorGroups'] = self.chkExpandDoctorGroups.isChecked()
        result['detailPatients'] = self.chkDetailPatients.isChecked()

        if self._clientOrganisationAvailable:
            result['clientOrganisationId'] = self.cmbClientOrganisation.value()

        result['typeFinanceId'] = self.cmbFinance.value()

        result['byActionEndDate'] = self.rbtnByActionEndDate.isChecked()

        result['groupBy'] = self.cmbGroupBy.currentIndex()
        result['groupAssistant'] = self.chkGroupAssistant.isChecked()

        return result

    def onStateChanged(self, state):
        self.lblPodtver.setEnabled(state)
        self.lblBegDatePodtver.setEnabled(state)
        self.lblEndDatePodtver.setEnabled(state)
        self.lblRefuseType.setEnabled(state)
        self.cmbPodtver.setEnabled(state)
        self.edtBegDatePodtver.setEnabled(state)
        self.edtEndDatePodtver.setEnabled(state)
        self.cmbRefuseType.setEnabled(state)

    @QtCore.pyqtSlot(bool)
    def on_chkInsurerDoctors_clicked(self, checked):
        self.lstInsurerDoctors.setVisible(checked)
        self.cmbInsurerDoctors.setVisible(not checked)

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.cmbPerson.setEndDate(QtCore.QDate(date))
        self.cmbAssistant.setEndDate(QtCore.QDate(date))

    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)
        self.cmbAssistant.setOrgStructureId(orgStructureId)

    @QtCore.pyqtSlot(int)
    def on_cmbSpeciality_currentIndexChanged(self, index):
        specialityId = self.cmbSpeciality.value()
        self.cmbPerson.setSpecialityId(specialityId)

    @QtCore.pyqtSlot(int)
    def on_cmbPerson_currentIndexChanged(self, index):
        isEnabled = self.cmbPerson.value() is None
        self.cmbAssistant.setEnabled(isEnabled)
        self.lblAssistant.setEnabled(isEnabled)

    @QtCore.pyqtSlot(int)
    def on_cmbAssistant_currentIndexChanged(self, index):
        isEnabled = self.cmbAssistant.value() is None
        self.cmbPerson.setEnabled(isEnabled)
        self.lblPerson.setEnabled(isEnabled)

    @QtCore.pyqtSlot(bool)
    def on_chkDetailServiceTypes_clicked(self, checked):
        self.lstServiceTypes.setEnabled(
            self.chkDetailServiceTypes.isChecked() and self.chkExpandDoctorGroups.isChecked())

    @QtCore.pyqtSlot(bool)
    def on_chkDetailService_clicked(self, checked):
        if self.rbtnByActionEndDate.isChecked():
            self.chkGroupAssistant.setEnabled(self.chkDetailService.isChecked())
            if not self.chkDetailService.isChecked():
                self.chkGroupAssistant.setChecked(False)
                self.cmbAssistant.setEnabled(True)
                self.cmbPerson.setEnabled(True)
            else:
                self.on_chkGroupAssistant_clicked(False)

    @QtCore.pyqtSlot(bool)
    def on_chkExpandDoctorGroups_clicked(self, checked):
        self.chkDetailService.setEnabled(self.chkExpandDoctorGroups.isChecked())
        self.chkDetailServiceTypes.setEnabled(self.chkExpandDoctorGroups.isChecked())
        self.lstServiceTypes.setEnabled(
            self.chkDetailServiceTypes.isChecked() and self.chkExpandDoctorGroups.isChecked())
        self.chkDetailPatients.setEnabled(self.chkExpandDoctorGroups.isChecked())

    @QtCore.pyqtSlot(bool)
    def on_rbtnByActionEndDate_clicked(self, checked):
        if self.chkDetailService.isChecked():
            self.chkGroupAssistant.setEnabled(True)
            if self.rbtnByActionEndDate.isChecked():
                self.on_chkGroupAssistant_clicked(False)
        self.chkByOrgStructAction.setEnabled(False)
        self.chkByOrgStructAction.setChecked(False)

    @QtCore.pyqtSlot(bool)
    def on_rbtnByFormingAccountDate_clicked(self, checked):
        self.chkGroupAssistant.setEnabled(False)
        self.chkGroupAssistant.setChecked(False)
        self.cmbAssistant.setEnabled(True)
        self.cmbPerson.setEnabled(True)
        self.chkByOrgStructAction.setEnabled(True)

    @QtCore.pyqtSlot(bool)
    def on_chkGroupAssistant_clicked(self, checked):
        self.cmbPerson.setEnabled(not self.chkGroupAssistant.isChecked())
        self.cmbAssistant.setEnabled(self.chkGroupAssistant.isChecked())

    @QtCore.pyqtSlot(int)
    def on_cmbEventPurpose_currentIndexChanged(self, index):
        eventPurposeId = self.cmbEventPurpose.value()
        if eventPurposeId:
            filter = 'EventType.purpose_id =%d' % eventPurposeId
            self.cmbResult.setFilter('eventPurpose_id=%d' % eventPurposeId)
        else:
            filter = getWorkEventTypeFilter()
        self.cmbEventType.setFilter(filter)

