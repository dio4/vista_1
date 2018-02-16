# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Events.Utils import getWorkEventTypeFilter
from Orgs.Utils import getOrgStructureDescendants, getOrgStructureFullName
from Reports.Report import CReport
from Reports.ReportBase import CReportBase, createTable
from library.DialogBase import CDialogBase
from library.Utils import forceBool, forceInt, forceRef, forceString, formatShortName, getVal
from library.database import addDateInRange


def selectData(params):
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    eventPurposeId = params.get('eventPurposeId', None)
    eventTypeId = params.get('eventTypeId', None)
    orgStructureId = getVal(params, 'orgStructureId', None)
    socStatusClassId = params.get('socStatusClassId', None)
    socStatusTypeId = params.get('socStatusTypeId', None)
    typeFinanceId = params.get('typeFinanceId', None)
    tariff = params.get('tariff', 0)
    visitPayStatus = params.get('visitPayStatus', 0)
    visitPayStatus -= 1
    groupingRows = params.get('groupingRows', 0)
    visitHospital = params.get('visitHospital', False)
    visitEmergency = params.get('visitEmergency', False)
    visitDisp = params.get('visitDisp', False)
    sex = params.get('sex', 0)
    ageFrom = params.get('ageFrom', 0)
    ageTo = params.get('ageTo', 150)
    insurerId = params.get('insurerId', None)
    primaryStatus = params.get('primaryStatus', 0)

    stmt = u"""
SELECT
   person_id,
   %s AS whereId,
   COUNT(person_id) AS cnt,
   scene_id,
   illness,
   ageGroup,
   weekend,
   %s as specName,
   Person.lastName,
   Person.firstName,
   Person.patrName
   FROM (
SELECT
    Visit.person_id,
    Visit.scene_id,
    DAYOFWEEK(`Visit`.`date`) IN (1,7) as weekend,
    (FDiagnosis.id IS NULL OR FDiagnosis.MKB NOT LIKE 'Z%%') AS illness,
    IF( ADDDATE(Client.birthDate, INTERVAL 18 YEAR)<=Visit.date,
        2,
        IF ( ADDDATE(Client.birthDate, INTERVAL 15 YEAR)>Visit.date,
          0,
          1)
      ) AS ageGroup
FROM Visit
LEFT JOIN Event     ON Event.id = Visit.event_id
LEFT JOIN EventType ON EventType.id = Event.eventType_id
LEFT JOIN rbEventTypePurpose ON rbEventTypePurpose.id = EventType.purpose_id
LEFT JOIN Client    ON Client.id = Event.client_id
LEFT JOIN Person    ON Person.id = Visit.person_id
LEFT JOIN rbDiagnosisType FinalDT ON FinalDT.code = '1'
LEFT JOIN Diagnostic FDiagnostic ON FDiagnostic.event_id = Event.id AND FDiagnostic.diagnosisType_id = FinalDT.id AND FDiagnostic.deleted = 0
LEFT JOIN Diagnosis FDiagnosis ON FDiagnosis.id = FDiagnostic.diagnosis_id
%s
WHERE Visit.deleted = 0
AND Event.deleted = 0
AND %s
) AS T
LEFT JOIN Person ON Person.id = T.person_id
%s
GROUP BY person_id, scene_id, illness, ageGroup
ORDER BY %s, Person.lastName, Person.firstName, Person.patrName
    """
    db = QtGui.qApp.db
    tableVisit = db.table('Visit')
    tableVisit = db.table('Visit')
    tableEvent = db.table('Event')
    tableEventType = db.table('EventType')
    tableClient = db.table('Client')
    tablePerson = db.table('Person')
    cond = []
    addDateInRange(cond, tableVisit['date'], begDate, endDate)
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    elif eventPurposeId:
        tableEvent = db.table('Event')
        cond.append(tableEventType['purpose_id'].eq(eventPurposeId))
    cond.append(tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()))
    #    if eventTypeIdList:
    #        cond.append(tableEvent['eventType_id'].inlist(eventTypeIdList))
    if orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    if socStatusTypeId:
        subStmt = ('SELECT ClientSocStatus.id FROM ClientSocStatus WHERE '
                   + 'ClientSocStatus.deleted=0 AND ClientSocStatus.client_id=Client.id AND '
                   + 'ClientSocStatus.socStatusType_id=%d' % socStatusTypeId)
        cond.append('EXISTS(' + subStmt + ')')
    elif socStatusClassId:
        subStmt = ('SELECT ClientSocStatus.id FROM ClientSocStatus WHERE '
                   + 'ClientSocStatus.deleted=0 AND ClientSocStatus.client_id=Client.id AND '
                   + 'ClientSocStatus.socStatusClass_id=%d' % socStatusClassId)
        cond.append('EXISTS(' + subStmt + ')')
    if visitPayStatus >= 0:
        cond.append(u'getPayCode(Visit.finance_id, Visit.payStatus) = %d' % (visitPayStatus))
    if typeFinanceId:
        cond.append(tableVisit['finance_id'].eq(typeFinanceId))
    if tariff == 2:
        cond.append(tableVisit['service_id'].isNull())
    elif tariff == 1:
        cond.append(tableVisit['service_id'].isNotNull())
    if not visitHospital:
        cond.append(u'''EventType.medicalAidType_id IS NULL OR (EventType.medicalAidType_id NOT IN (SELECT rbMedicalAidType.id from rbMedicalAidType where rbMedicalAidType.code IN (\'7\')))''')
    if not visitEmergency:
        cond.append(u'''EventType.medicalAidType_id IS NULL OR (EventType.medicalAidType_id NOT IN (SELECT rbMedicalAidType.id from rbMedicalAidType where rbMedicalAidType.code IN (\'4\')))''''')
    if not visitDisp:
        cond.append(u'''EventType.code NOT IN ('dd2013_1', 'dd2013_2', 'ДДВет')''')
    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append('Visit.date >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)' % ageFrom)
        cond.append('Visit.date < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)' % (ageTo + 1))
    if insurerId:
        insurerJoin = ' LEFT JOIN ClientPolicy ON ClientPolicy.id = getClientPolicyId(Client.id, 1)'
        cond.append('ClientPolicy.insurer_id = %d' % insurerId)
    else:
        insurerJoin = ''
    if primaryStatus:
        cond.append('Event.isPrimary = %d' % primaryStatus)
    if groupingRows == 0:
        whereId = u'Person.speciality_id'
        whereName = u'rbSpeciality.name'
        whereLeft = u'LEFT JOIN rbSpeciality ON rbSpeciality.id = Person.speciality_id'
    elif groupingRows == 1:
        whereId = u'Person.post_id'
        whereName = u'rbPost.name'
        whereLeft = u'LEFT JOIN rbPost ON rbPost.id = Person.post_id'
    else:
        whereId = u'Person.orgStructure_id'
        whereName = u'OrgStructure.name'
        whereLeft = u'LEFT JOIN OrgStructure ON OrgStructure.id = Person.orgStructure_id'

    if params.get('isEventCreateParams', False):
        addDateInRange(cond, tableEvent['createDatetime'], params.get('eventBegDatetime', QtCore.QDate.currentDate()), params.get('eventEndDatetime', QtCore.QDate.currentDate()))

    stmt = stmt % (whereId, whereName, insurerJoin, db.joinAnd(cond), whereLeft, whereName)
    return db.query(stmt)


def selectData_KK(params):
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    isEventTime = params.get('isEventCreateParams', False)
    eventDate = ((params.get('eventBegDatetime', QtCore.QDate.currentDate()),
                  params.get('eventEndDatetime', QtCore.QDate.currentDate())) if isEventTime else None)
    eventPurposeId = params.get('eventPurposeId', None)
    eventTypeId = params.get('eventTypeId', None)
    orgStructureId = getVal(params, 'orgStructureId', None)
    # socStatusClassId = params.get('socStatusClassId', None)
    # socStatusTypeId = params.get('socStatusTypeId', None)
    # typeFinanceId = params.get('typeFinanceId', None)
    # tariff = params.get('tariff', 0)
    visitPayStatus = params.get('visitPayStatus', 0)
    visitPayStatus -= 1
    groupingRows = params.get('groupingRows', 0)
    visitHospital = params.get('visitHospital', False)
    visitEmergency = params.get('visitEmergency', False)
    visitDisp = params.get('visitDisp', False)
    sex = params.get('sex', 0)
    ageFrom = params.get('ageFrom', 0)
    ageTo = params.get('ageTo', 150)
    # insurerId = params.get('insurerId', None)
    # primaryStatus = params.get('primaryStatus', 0)

    db = QtGui.qApp.db
    Action = db.table('Action')
    ActionByIllness = db.table('Action').alias('ByIllness')
    ActionType = db.table('ActionType')
    Client = db.table('Client')
    ClientLocAddress = db.table('ClientAddress').alias('LocAddress')
    ClientRegAddress = db.table('ClientAddress').alias('RegAddress')
    Event = db.table('Event')
    EventKind = db.table('rbEventKind')
    EventType = db.table('EventType')
    Person = db.table('Person')
    Service = db.table('rbService')
    ServiceCategory = db.table('rbServiceCategory')

    KLADR = db.table('kladr.KLADR')
    SOCRBASE = db.table('kladr.SOCRBASE')

    ClientLocAddress = db.table('ClientAddress').alias('ClientLocAddress')
    LocAddress = db.table('Address').alias('LocAddress')
    LocAddressHouse = db.table('AddressHouse').alias('LocAddressHouse')
    LocKLADR = KLADR.alias('LocKLADR')
    LocSOCR = SOCRBASE.alias('LocSOCR')

    ClientRegAddress = db.table('ClientAddress').alias('ClientRegAddress')
    RegAddress = db.table('Address').alias('RegAddress')
    RegAddressHouse = db.table('AddressHouse').alias('RegAddressHouse')
    RegKLADR = KLADR.alias('RegKLADR')
    RegSOCR = SOCRBASE.alias('RegSOCR')

    subTable = Event.innerJoin(Action, [Action['event_id'].eq(Event['id']), Action['endDate'].ge(begDate), Action['endDate'].lt(endDate.addDays(1)), Action['deleted'].eq(0)])
    subTable = subTable.innerJoin(Client, [Client['id'].eq(Event['client_id']), Client['deleted'].eq(0)])
    subTable = subTable.innerJoin(ActionType, [ActionType['id'].eq(Action['actionType_id']), ActionType['deleted'].eq(0)])
    subTable = subTable.innerJoin(Service, Service['id'].eq(ActionType['nomenclativeService_id']))
    subTable = subTable.innerJoin(ServiceCategory, ServiceCategory['id'].eq(Service['category_id']))
    subTable = subTable.innerJoin(Person, [Person['id'].eq(Action['person_id']), Person['deleted'].eq(0)])

    groupFields = {
        0: Person['speciality_id'].name(),
        1: Person['post_id'].name(),
        2: Person['orgStructure_id'].name()
    }
    if groupingRows not in groupFields:
        groupingRows = 2

    rowKey = groupFields[groupingRows]

    subQueryCond = [
        Event['deleted'].eq(0)
    ]

    if orgStructureId:
        subQueryCond.append(Person['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    else:
        subQueryCond.append(Person['org_id'].eq(QtGui.qApp.currentOrgId()))

    if ageFrom <= ageTo and (ageFrom > 0 or ageTo < 150):
        subQueryCond.append('Action.endDate >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)' % ageFrom)
        subQueryCond.append('Action.endDate < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)' % (ageTo + 1))

    if visitPayStatus >= 0:
        subQueryCond.append('getPayCode(%s, %s) = %d' % (Action['finance_id'].name(), Action['payStatus'].name(), visitPayStatus))

    tableCountByCategory = db.table(
        db.selectStmt(subTable,
                      fields=[
                          Event['id'].alias('eventId'),
                          db.makeField(rowKey).alias('rowKey'),
                          db.func.age(Client['birthDate'], Action['endDate']).alias('clientAge'),
                          ServiceCategory['code'].alias('category'),
                          db.count('*').alias('cnt')
                      ],
                      where=subQueryCond,
                      group=['eventId', 'rowKey', 'clientAge', 'category'])
    ).alias('countByCategory')

    byIllnessTable = Action.innerJoin(ActionType, [ActionType['id'].eq(Action['actionType_id']), ActionType['deleted'].eq(0)])
    byIllnessTable = byIllnessTable.innerJoin(Service, Service['id'].eq(ActionType['nomenclativeService_id']))
    byIllnessTable = byIllnessTable.innerJoin(ServiceCategory, [ServiceCategory['id'].eq(Service['category_id']), ServiceCategory['code'].eq('1')])
    byIllnessStmt = db.selectStmt(byIllnessTable,
                                  fields=db.max(Action['id']),
                                  where=[Action['event_id'].eq(Event['id']), Action['deleted'].eq(0)])

    table = Event.innerJoin(EventType, [EventType['id'].eq(Event['eventType_id']), EventType['deleted'].eq(0)])
    table = table.leftJoin(EventKind, EventKind['id'].eq(EventType['eventKind_id']))
    table = table.innerJoin(tableCountByCategory, tableCountByCategory['eventId'].eq(Event['id']))
    table = table.innerJoin(Client, [Client['id'].eq(Event['client_id']), Client['deleted'].eq(0)])

    table = table.leftJoin(ClientRegAddress, ClientRegAddress['id'].eq(db.func.getClientRegAddressId(Client['id'])))
    table = table.leftJoin(RegAddress, RegAddress['id'].eq(ClientRegAddress['address_id']))
    table = table.leftJoin(RegAddressHouse, RegAddressHouse['id'].eq(RegAddress['house_id']))
    table = table.leftJoin(RegKLADR, RegKLADR['CODE'].eq(RegAddressHouse['KLADRCode']))
    table = table.leftJoin(RegSOCR, '{field} = ({stmt})'.format(field=RegSOCR['KOD_T_ST'],
                                                                stmt=db.selectStmt(SOCRBASE, 'KOD_T_ST', SOCRBASE['SCNAME'].eq(RegKLADR['SOCR']), limit=1)))

    table = table.leftJoin(ClientLocAddress, ClientLocAddress['id'].eq(db.func.getClientLocAddressId(Client['id'])))
    table = table.leftJoin(LocAddress, LocAddress['id'].eq(ClientLocAddress['address_id']))
    table = table.leftJoin(LocAddressHouse, LocAddressHouse['id'].eq(LocAddress['house_id']))
    table = table.leftJoin(LocKLADR, LocKLADR['CODE'].eq(LocAddressHouse['KLADRCode']))
    table = table.leftJoin(LocSOCR, '{field} = ({stmt})'.format(field=LocSOCR['KOD_T_ST'],
                                                                stmt=db.selectStmt(SOCRBASE, 'KOD_T_ST', SOCRBASE['SCNAME'].eq(LocKLADR['SOCR']), limit=1)))

    table = table.leftJoin(ActionByIllness, '{id} = ({stmt})'.format(id=ActionByIllness['id'], stmt=byIllnessStmt))

    villagerSOCRBASE = ('206', '302', '303', '304', '305', '310', '316', '317', '402', '403', '404', '406', '407', '414', '416', '417', '419', '421', '423', '424', '425', '429', '430', '431', '433', '435', '443', '447', '448', '449', '521', '533', '534', '536', '544', '546', '548', '551', '553', '555', '556', '558', '567', '568', '569', '573', '580', '586', '587', '589')

    cols = [
        db.sum(tableCountByCategory['cnt']).alias('cnt'),
        tableCountByCategory['rowKey'].alias('rowKey'),
        tableCountByCategory['clientAge'].alias('clientAge'),
        tableCountByCategory['category'].alias('category'),
        db.makeField(ActionByIllness['id'].isNotNull()).alias('hasActionByIllness'),
        db.makeField(db.joinOr([
            ClientRegAddress['isVillager'].eq(1),
            RegSOCR['KOD_T_ST'].inlist(villagerSOCRBASE),
            ClientLocAddress['isVillager'].eq(1),
            LocSOCR['KOD_T_ST'].inlist(villagerSOCRBASE)
        ])).alias('isVillager')
    ]

    group = [
        'rowKey',
        'clientAge',
        'category',
        'hasActionByIllness',
        'isVillager'
    ]

    cond = [
        Event['deleted'].eq(0)
    ]

    if eventDate:
        eventBegDatetime, eventEndDatetime = eventDate
        addDateInRange(cond, Event['createDatetime'], eventBegDatetime, eventEndDatetime)

    if not visitHospital:
        MedicalAidType = db.table('rbMedicalAidType')
        hospitalMAT_ids = db.getIdList(MedicalAidType, MedicalAidType['id'], MedicalAidType['code'].eq('7'))
        cond.append(EventType['medicalAidType_id'].notInlist(hospitalMAT_ids))

    if not visitEmergency:
        MedicalAidType = db.table('rbMedicalAidType')
        hospitalMAT_ids = db.getIdList(MedicalAidType, MedicalAidType['id'], MedicalAidType['code'].eq('4'))
        cond.append(EventType['medicalAidType_id'].notInlist(hospitalMAT_ids))

    if not visitDisp:
        cond.append(db.joinOr([EventKind['code'].notInlist([u'01', u'02', u'04']),
                               EventKind['code'].isNull()]))

    if eventTypeId:
        cond.append(Event['eventType_id'].eq(eventTypeId))

    if eventPurposeId:
        cond.append(EventType['purpose_id'].eq(eventPurposeId))

    if sex:
        cond.append(Client['sex'].eq(sex))

    return db.query(db.selectStmt(table, cols, cond, group))


class CReportF30(CReport):
    primaryMap = {1: u'первичные',
                  2: u'повторные',
                  3: u'активные посещения',
                  4: u'перевозки',
                  5: u'амбулаторные'}

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Форма 30', u'Форма 30')

    def getSetupDialog(self, parent):
        result = CReportF30SetupDialog(parent)
        result.setTitle(self.title())
        return result

    def getDescription(self, params):
        rows = CReport.getDescription(self, params)
        primary = params.get('primaryStatus', 0)
        if primary:
            rows.append(u'Признак первичности: ' + self.primaryMap[primary])
        return rows

    def build(self, params):
        visitPayStatus = params.get('visitPayStatus', 0)
        visitPayStatus -= 1
        detailChildren = params.get('detailChildren', False)
        divideWeekdays = params.get('divideWeekdays', False)

        db = QtGui.qApp.db
        sceneNames = [u'Поликлиника', u'На дому', u'Актив на дому']
        sceneIndexes = {}
        for index, record in enumerate(db.getRecordList('rbScene', 'id, code', '', 'code')):
            sceneId = forceRef(record.value(0))
            if forceString(record.value(1)) == '1':
                sceneIndexes[sceneId] = 0
            elif forceString(record.value(1)) == '2':
                sceneIndexes[sceneId] = 1
            elif forceString(record.value(1)) == '3':
                sceneIndexes[sceneId] = 2

        if not divideWeekdays:
            reportRowSize = 1 + 4 + 2 * len(sceneNames)
            reportRowSize = reportRowSize if detailChildren else reportRowSize - 1
        else:
            reportRowSize = 2 + 8 + 4 * len(sceneNames)
            reportRowSize = reportRowSize if detailChildren else reportRowSize - 2

        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        columnShift = 0 if detailChildren else 1

        if not divideWeekdays:
            reportData, personInfoList = self.produceReportData(query, reportRowSize, detailChildren, sceneIndexes, params)
        else:
            reportData, personInfoList = self.produceReportDataDivided(query, reportRowSize, detailChildren, sceneIndexes, params)

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        if not divideWeekdays:
            table = self.makeTable(detailChildren, sceneNames, columnShift, cursor)
        else:
            table = self.makeTableDivided(detailChildren, sceneNames, columnShift, cursor)

        prevSpecName = None
        total = None
        grandTotal = [0] * reportRowSize
        for personId, specName, personName in personInfoList:
            if prevSpecName != specName:
                if total:
                    self.produceTotalLine(table, u'всего', total)
                total = [0] * reportRowSize
                i = table.addRow()
                table.mergeCells(i, 0, 1, reportRowSize + 1)
                table.setText(i, 0, specName, CReportBase.TableHeader)
                prevSpecName = specName
            row = reportData[personId]
            i = table.addRow()
            table.setText(i, 0, personName)
            for j in xrange(reportRowSize):
                table.setText(i, j + 1, row[j])
                total[j] += row[j]
                grandTotal[j] += row[j]
        if total:
            self.produceTotalLine(table, u'всего', total)
        self.produceTotalLine(table, u'итого', grandTotal)
        return doc

    def produceReportData(self, query, reportRowSize, detailChildren, sceneIndexes, params):
        columnShift = 0 if detailChildren else 1
        reportData = {}
        personInfoList = []
        while query.next():
            record = query.record()
            personId = forceRef(record.value('person_id'))
            cnt = forceInt(record.value('cnt'))
            sceneId = forceInt(record.value('scene_id'))
            illness = forceBool(record.value('illness'))
            ageGroup = forceInt(record.value('ageGroup'))
            reportRow = reportData.get(personId, None)
            if not reportRow:
                reportRow = [0] * reportRowSize
                reportData[personId] = reportRow
                groupingRows = params.get('groupingRows', 0)
                specName = forceString(record.value('specName')) if groupingRows != 2 \
                    else getOrgStructureFullName(forceRef(record.value('whereId')))
                lastName = forceString(record.value('lastName'))
                firstName = forceString(record.value('firstName'))
                patrName = forceString(record.value('patrName'))
                personName = formatShortName(lastName, firstName, patrName)
                personInfoList.append((personId, specName, personName))
            reportRow[0] += cnt
            if illness:
                reportRow[1] += cnt
                if not detailChildren:
                    if ageGroup in [0, 1]:
                        ageGroup = 0
                    else:
                        ageGroup = 1
                reportRow[2 + ageGroup] += cnt
            sceneIndex = sceneIndexes.get(sceneId, 0)
            reportRow[5 + sceneIndex * 2 - columnShift] += cnt
            if illness:
                reportRow[6 + sceneIndex * 2 - columnShift] += cnt

        return reportData, personInfoList

    def produceReportDataDivided(self, query, reportRowSize, detailChildren, sceneIndexes, params):
        columnShift = 0 if detailChildren else 1
        reportData = {}
        personInfoList = []
        while query.next():
            record = query.record()
            personId = forceRef(record.value('person_id'))
            cnt = forceInt(record.value('cnt'))
            sceneId = forceInt(record.value('scene_id'))
            illness = forceBool(record.value('illness'))
            ageGroup = forceInt(record.value('ageGroup'))
            isWeekend = forceInt(record.value('weekend'))
            reportRow = reportData.get(personId, [])
            if not reportRow:
                reportRow = [0] * reportRowSize
                reportData[personId] = reportRow
                groupingRows = params.get('groupingRows', 0)
                specName = forceString(record.value('specName')) if groupingRows != 2 \
                    else getOrgStructureFullName(forceRef(record.value('whereId')))
                lastName = forceString(record.value('lastName'))
                firstName = forceString(record.value('firstName'))
                patrName = forceString(record.value('patrName'))
                personName = formatShortName(lastName, firstName, patrName)
                personInfoList.append((personId, specName, personName))
            if isWeekend:
                reportRow[1] += cnt
                if illness:
                    reportRow[3] += cnt
                    if not detailChildren:
                        if ageGroup in [0, 1]:
                            ageGroup = 0
                        else:
                            ageGroup = 1
                    reportRow[5 + ageGroup * 2] += cnt
                sceneIndex = sceneIndexes.get(sceneId, 0)
                reportRow[11 + sceneIndex * 4 - columnShift * 2] += cnt
                if illness:
                    reportRow[13 + sceneIndex * 4 - columnShift * 2] += cnt
            else:
                reportRow[0] += cnt
                if illness:
                    reportRow[2] += cnt
                    if not detailChildren:
                        if ageGroup in [0, 1]:
                            ageGroup = 0
                        else:
                            ageGroup = 1
                    reportRow[4 + ageGroup * 2] += cnt
                sceneIndex = sceneIndexes.get(sceneId, 0)
                reportRow[10 + sceneIndex * 4 - columnShift * 2] += cnt
                if illness:
                    reportRow[12 + sceneIndex * 4 - columnShift * 2] += cnt

        return reportData, personInfoList

    def produceTotalLine(self, table, title, total):
        i = table.addRow()
        table.setText(i, 0, title, CReportBase.TableTotal)
        for j in xrange(len(total)):
            table.setText(i, j + 1, total[j], CReportBase.TableTotal)

    def makeTable(self, detailChildren, sceneNames, columnShift, cursor):
        tableColumns = [
            ('30%', [u'ФИО врача', u''], CReportBase.AlignLeft),
            ('5%', [u'всего посещений', u''], CReportBase.AlignRight),
            ('5%', [u'по поводу заболеваний', u'всего'], CReportBase.AlignRight),
            ('5%', [u'', u'дети'], CReportBase.AlignRight),
            ('5%', [u'', u'взр.'], CReportBase.AlignRight),
        ]

        if detailChildren:
            tableColumns.insert(4, ('5%', [u'', u'подр.'], CReportBase.AlignRight))

        for sceneName in sceneNames:
            tableColumns.append(('5%', [sceneName, u'всего'], CReportBase.AlignRight))
            tableColumns.append(('5%', [u'', u'по заб.'], CReportBase.AlignRight))

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        ageLength = 4 if detailChildren else 3
        table.mergeCells(0, 2, 1, ageLength)
        for sceneIndex in xrange(len(sceneNames)):
            table.mergeCells(0, 6 + sceneIndex * 2 - columnShift, 1, 2)
        return table

    def makeTableDivided(self, detailChildren, sceneNames, columnShift, cursor):
        tableColumns = [
            ('30%', [u'ФИО врача', u'', u''], CReportBase.AlignLeft),
            ('3%', [u'всего посещений', u'', u'буд.'], CReportBase.AlignRight),
            ('3%', [u'', u'', u'вых.'], CReportBase.AlignLeft),
            ('3%', [u'по поводу заболеваний', u'всего', u'буд.'], CReportBase.AlignRight),
            ('3%', [u'', u'', u'вых.'], CReportBase.AlignRight),
            ('3%', [u'', u'дети', u'буд.'], CReportBase.AlignRight),
            ('3%', [u'', u'', u'вых.'], CReportBase.AlignRight),
            ('3%', [u'', u'взр.', u'буд.'], CReportBase.AlignRight),
            ('3%', [u'', u'', u'вых.'], CReportBase.AlignRight),
        ]

        if detailChildren:
            tableColumns.insert(7, ('3%', [u'', u'подр.', u'буд.'], CReportBase.AlignRight))
            tableColumns.insert(8, ('3%', [u'', u'', u'вых.'], CReportBase.AlignRight))

        for sceneName in sceneNames:
            tableColumns.append(('3%', [sceneName, u'всего', u'буд.'], CReportBase.AlignRight))
            tableColumns.append(('3%', [u'', u'', u'вых.'], CReportBase.AlignRight))
            tableColumns.append(('3%', [u'', u'по заб.', u'буд.'], CReportBase.AlignRight))
            tableColumns.append(('3%', [u'', u'', u'вых.'], CReportBase.AlignRight))
        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 2, 2)
        ageLength = 4 if detailChildren else 3
        table.mergeCells(0, 3, 1, ageLength * 2)
        for i in range(ageLength):
            table.mergeCells(1, 3 + i * 2, 1, 2)
        for sceneIndex in xrange(len(sceneNames)):
            table.mergeCells(0, 11 + sceneIndex * 4 - columnShift * 2, 1, 4)
            table.mergeCells(1, 11 + sceneIndex * 4 - columnShift * 2, 1, 2)
            table.mergeCells(1, 13 + sceneIndex * 4 - columnShift * 2, 1, 2)

        return table


class CReportF30_KK(CReportF30):
    def createTable(self, cursor, keyName):
        keyColumnWidth = 10.0
        keyColumn = ('%.4f%%' % keyColumnWidth, [keyName], CReportBase.AlignLeft)
        columnDescr = [
            [u'№ стр'],
            [u'Число посещений', u'Врачей, включая профилактические - всего'],
            [u'', u'Из них:', u'Сельскими жителями'],
            [u'', u'', u'Детьми 0-17 лет'],
            [u'Из общего числа посещений (из гр.3) сделано по поводу заболеаний', u'Сельскими жителями'],
            [u'', u'Взрослыми 18 лет и старше'],
            [u'', u'Детьми 0-17 лет'],
            [u'Число посещений врачами на дому', u'Всего'],
            [u'', u'Из них сельских жителей'],
            [u'', u'Из гр.9', u'По поводу заболеваний'],
            [u'', u'', u'Детей 0-17 лет'],
            [u'', u'Из гр. 12 по поводу заболеваний'],
        ]
        columnWidth = '%.4f%%' % ((100.0 - keyColumnWidth) / len(columnDescr))
        tableColumns = [keyColumn] + [(columnWidth, descr, CReportBase.AlignCenter) for descr in columnDescr]
        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 3, 1)
        table.mergeCells(0, 2, 1, 3)
        table.mergeCells(1, 2, 2, 1)
        table.mergeCells(1, 3, 1, 2)
        table.mergeCells(0, 5, 1, 3)
        table.mergeCells(1, 5, 2, 1)
        table.mergeCells(1, 6, 2, 1)
        table.mergeCells(1, 7, 2, 1)
        table.mergeCells(0, 8, 1, 5)
        table.mergeCells(1, 8, 2, 1)
        table.mergeCells(1, 9, 2, 1)
        table.mergeCells(1, 10, 1, 2)
        table.mergeCells(1, 12, 2, 1)

        i = table.addRow()
        for col in xrange(len(tableColumns)):
            table.setText(i, col, col + 1, blockFormat=CReportBase.AlignCenter)

        return table

    def processRecord(self, record, reportData, forcekeyVal, rowSize):
        rowKey = forcekeyVal(record.value('rowKey'))
        clientAge = forceInt(record.value('clientAge'))
        isVillager = forceBool(record.value('isVillager'))
        category = forceInt(record.value('category'))
        hasActionByIllness = forceBool(record.value('hasActionByIllness'))
        cnt = forceInt(record.value('cnt'))

        row = reportData.setdefault(rowKey, [0] * rowSize)
        if category in [2, 3, 4, 5]:
            row[0] += cnt
            if isVillager:
                row[1] += cnt
            if clientAge < 18:
                row[2] += cnt
            if category == 2 and hasActionByIllness:
                if isVillager:
                    row[3] += cnt
                if clientAge >= 18:
                    row[4] += cnt
                else:
                    row[5] += cnt
        elif category in [6, 7, 8]:
            row[6] += cnt
            if isVillager:
                row[7] += cnt
            if clientAge < 18:
                row[9] += cnt
            if category in [6, 7] and hasActionByIllness:
                row[8] += cnt
                if clientAge < 18:
                    row[10] += cnt

    def build(self, params):
        groupingRows = params.get('groupingRows', 0)
        if groupingRows == 0:
            forceKeyVal = forceRef
            keyValToString = lambda specialityId: forceString(QtGui.qApp.db.translate('rbSpeciality', 'id', specialityId, 'name'))
            keyValToSort = keyValToString
            keyName = u'Специальность'
        elif groupingRows == 1:
            forceKeyVal = forceRef
            keyValToString = lambda postId: forceString(QtGui.qApp.db.translate('rbPost', 'id', postId, 'name'))
            keyValToSort = keyValToString
            keyName = u'Должность'
        else:
            forceKeyVal = forceRef
            keyValToString = lambda orgStructureId: forceString(QtGui.qApp.db.translate('OrgStructure', 'id', orgStructureId, 'name'))
            keyValToSort = keyValToString
            keyName = u'Подразделение'

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        cursor.setCharFormat(QtGui.QTextCharFormat())
        query = selectData_KK(params)
        self.setQueryText(forceString(query.lastQuery()))
        rowSize = 11

        reportData = {}
        while query.next():
            record = query.record()
            self.processRecord(record, reportData, forceKeyVal, rowSize)

        table = self.createTable(cursor, keyName)

        total = [0] * rowSize
        for rowNum, key in enumerate(sorted(reportData.keys(), key=keyValToSort)):
            row = reportData[key]
            i = table.addRow()
            table.setText(i, 0, keyValToString(key))
            table.setText(i, 1, rowNum + 1)
            for j in xrange(rowSize):
                table.setText(i, j + 2, row[j])
                total[j] += row[j]
        i = table.addRow()
        table.setText(i, 0, u'Всего', CReportBase.TableTotal)
        table.setText(i, 1, len(reportData) + 1, CReportBase.TableTotal)
        for j in xrange(rowSize):
            table.setText(i, j + 2, total[j], CReportBase.TableTotal)

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        #
        return doc


from Ui_ReportF30Setup import Ui_ReportF30SetupDialog


class CReportF30SetupDialog(CDialogBase, Ui_ReportF30SetupDialog):
    def __init__(self, parent=None):
        super(CReportF30SetupDialog, self).__init__(parent)
        self.patientRequired = False
        self.setupUi(self)
        self.cmbEventPurpose.setTable('rbEventTypePurpose', True, filter='code != \'0\'')
        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbSocStatusType.setTable('vrbSocStatusType', True)
        self.cmbTypeFinance.setTable('rbFinance', True)
        self.cmbTariff.setCurrentIndex(0)
        self.cmbVisitPayStatus.setCurrentIndex(0)
        self.cmbGrouping.setCurrentIndex(0)
        self.cmbInsurer.setAddNone(True)
        self.edtEventBegDatetime.setCalendarPopup(True)
        self.edtEventBegDatetime.calendarWidget().setFirstDayOfWeek(QtCore.Qt.Monday)
        self.edtEventEndDatetime.setCalendarPopup(True)
        self.edtEventEndDatetime.calendarWidget().setFirstDayOfWeek(QtCore.Qt.Monday)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)

    def setPayPeriodVisible(self, value):
        pass

    def setWorkTypeVisible(self, value):
        pass

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setEventTypeVisible(self, visible=True):
        pass

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbEventPurpose.setValue(params.get('eventPurposeId', None))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbOrgStructure.setValue(getVal(params, 'orgStructureId', None))
        self.cmbTypeFinance.setValue(params.get('typeFinanceId', None))
        self.cmbTariff.setCurrentIndex(params.get('tariff', 0))
        self.cmbSocStatusClass.setValue(params.get('socStatusClassId', None))
        self.cmbSocStatusType.setValue(params.get('socStatusTypeId', None))
        self.cmbVisitPayStatus.setCurrentIndex(params.get('visitPayStatus', 0))
        self.cmbGrouping.setCurrentIndex(params.get('groupingRows', 0))
        self.chkDetailChildren.setChecked(params.get('detailChildren', False))
        self.chkVisitHospital.setChecked(params.get('visitHospital', False))
        self.chkVisitEmergency.setChecked(params.get('visitEmergency', False))
        self.chkVisitDisp.setChecked(params.get('visitDisp', False))
        self.cmbSex.setCurrentIndex(params.get('sex', 0))
        self.edtAgeFrom.setValue(params.get('ageFrom', 0))
        self.edtAgeTo.setValue(params.get('ageTo', 150))
        self.chkDivideWeekdays.setChecked(bool(params.get('divideWeekdays', False)))
        self.cmbInsurer.setValue(params.get('insurerId', None))
        self.cmbPrimary.setCurrentIndex(params.get('primaryStatus', 0))
        self.edtEventBegDatetime.setDateTime(params.get('eventBegDatetime', QtCore.QDateTime.currentDateTime()))
        self.edtEventEndDatetime.setDateTime(params.get('eventEndDatetime', QtCore.QDateTime.currentDateTime()))
        self.gbEventDatetimeParams.setChecked(params.get('isEventCreateParams', False))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['eventPurposeId'] = self.cmbEventPurpose.value()
        result['eventTypeId'] = self.cmbEventType.value()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['socStatusClassId'] = self.cmbSocStatusClass.value()
        result['socStatusTypeId'] = self.cmbSocStatusType.value()
        result['typeFinanceId'] = self.cmbTypeFinance.value()
        result['tariff'] = self.cmbTariff.currentIndex()
        result['visitPayStatus'] = self.cmbVisitPayStatus.currentIndex()
        result['groupingRows'] = self.cmbGrouping.currentIndex()
        result['detailChildren'] = self.chkDetailChildren.isChecked()
        result['visitHospital'] = self.chkVisitHospital.isChecked()
        result['visitEmergency'] = self.chkVisitEmergency.isChecked()
        result['visitDisp'] = self.chkVisitDisp.isChecked()
        result['sex'] = self.cmbSex.currentIndex()
        result['ageFrom'] = self.edtAgeFrom.value()
        result['ageTo'] = self.edtAgeTo.value()
        result['divideWeekdays'] = self.chkDivideWeekdays.isChecked()
        result['insurerId'] = self.cmbInsurer.value()
        result['primaryStatus'] = self.cmbPrimary.currentIndex()
        result['isEventCreateParams'] = self.gbEventDatetimeParams.isChecked()
        result['eventBegDatetime'] = self.edtEventBegDatetime.dateTime()
        result['eventEndDatetime'] = self.edtEventEndDatetime.dateTime()
        return result

    @QtCore.pyqtSlot(int)
    def on_cmbEventPurpose_currentIndexChanged(self, index):
        eventPurposeId = self.cmbEventPurpose.value()
        if eventPurposeId:
            filter = 'EventType.purpose_id =%d' % eventPurposeId
        else:
            filter = getWorkEventTypeFilter()
        self.cmbEventType.setFilter(filter)

    @QtCore.pyqtSlot(int)
    def on_cmbSocStatusClass_currentIndexChanged(self, index):
        socStatusClassId = self.cmbSocStatusClass.value()
        filter = ('class_id=%d' % socStatusClassId) if socStatusClassId else ''
        self.cmbSocStatusType.setFilter(filter)


def main():
    import sys
    from s11main import CS11mainApp
    from library.database import connectDataBaseByInfo

    QtGui.qApp = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    connectionInfo = {
        'driverName': 'mysql',
        'host': 'p21',
        'port': 3306,
        'database': 's11',
        'user': 'dbuser',
        'password': 'dbpassword',
        'connectionName': 'vista-med',
        'compressData': True,
        'afterConnectFunc': None
    }
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    w = CReportF30(None)
    w.exec_()


if __name__ == '__main__':
    main()
