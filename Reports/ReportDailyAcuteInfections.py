# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtGui, QtCore

from library.database               import addDateInRange
from library.Utils                  import forceBool, forceInt, forceString, forceDate
from Orgs.Utils                     import getOrgStructureDescendants
from Reports.Report                 import CReport
from Reports.ReportAcuteInfections  import CReportAcuteInfectionsSetupDialog
from Reports.ReportBase             import createTable, CReportBase


def selectData(params, MKBList):
    registeredInPeriod = params.get('registeredInPeriod', False)
    chkCreateDate = params.get('chkCreateDate', False)
    createBegDate = params.get('createBegDate', QtCore.QDate())
    createEndDate = params.get('createEndDate', QtCore.QDate())
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    eventPurposeIdList = params.get('eventPurposeIdList', [])
    eventTypeId = params.get('eventTypeId', None)
    orgStructureId = params.get('orgStructureId', None)
    personId = params.get('personId', None)
    sex = params.get('sex', 0)
    ageFrom = params.get('ageFrom', 0)
    ageTo = params.get('ageTo', 150)
    socStatusClassId = params.get('socStatusClassId', None)
    socStatusTypeId = params.get('socStatusTypeId', None)
    accountAccomp = params.get('accountAccomp', False)
    locality = params.get('locality', 0)
    isPrimary = params.get('isPrimary',  0)
    
    visitEmergency = params.get('visitEmergency', False)
    
    stmt=u"""
SELECT
   COUNT(*) AS cnt,
   MKB,
   clientAge,
   clientSex,
   isWorking,
   isPregnancy
   -- setDate,
   -- clientId,
   {regionAddictionMainField}
   FROM (
SELECT
    Diagnosis.MKB AS MKB,
    age(Client.birthDate, Diagnosis.setDate) AS clientAge,
    Client.sex AS clientSex,
    -- Diagnosis.client_id AS clientId,
    -- Diagnosis.setDate AS setDate,
    {regionAddictionOtherField}
    (rbPolicyType.code = '2') AS isWorking,
    (Client.sex = 2 AND
        EXISTS(SELECT Diagnostic.id
               FROM   Diagnostic
               INNER JOIN Event ON Event.id = Diagnostic.event_id
               WHERE Diagnostic.diagnosis_id = Diagnosis.id
                 AND Diagnostic.deleted = 0
                 AND Event.deleted = 0
                 AND Event.pregnancyWeek>0)) AS isPregnancy
FROM %s
WHERE %s
) AS T
GROUP BY MKB, {regionAddictionOrder} clientAge, clientSex, isWorking, isPregnancy
ORDER BY MKB
    """

    if QtGui.qApp.region() == '78':
        stmt = stmt.replace(u'{regionAddictionMainField}', u', isPregnancy, setDate, clientId')
        stmt = stmt.replace(u'{regionAddictionOtherField}', u'Diagnosis.client_id AS clientId, Diagnosis.setDate AS setDate,')
        stmt = stmt.replace(u'{regionAddictionOrder}', u'setDate, clientId,')
    else:
        stmt = stmt.replace(u'{regionAddictionMainField}', u'')
        stmt = stmt.replace(u'{regionAddictionOtherField}', u'')
        stmt = stmt.replace(u'{regionAddictionOrder}', u'')

    db = QtGui.qApp.db
    tableDiagnosis  = db.table('Diagnosis')
    tableClient = db.table('Client')
    tableDiagnostic = db.table('Diagnostic')
    tablePerson = db.table('Person')
    tableDiagnosisType = db.table('rbDiagnosisType')
    tableClientPolicy = db.table('ClientPolicy')
    tablePolicyType = db.table('rbPolicyType')
    tableClientAddress = db.table('ClientAddress')
    tableAddress = db.table('Address')
    tableAddressHouse = db.table('AddressHouse')
    queryTable = tableDiagnosis.leftJoin(tableClient, tableDiagnosis['client_id'].eq(tableClient['id']))
    queryTable = queryTable.leftJoin(tableDiagnosisType, tableDiagnosis['diagnosisType_id'].eq(tableDiagnosisType['id']))
    queryTable = queryTable.leftJoin(tableClientPolicy, '`ClientPolicy`.`id` = getClientPolicyId(`Client`.`id`,1)')
    queryTable = queryTable.leftJoin(tablePolicyType, tableClientPolicy['policyType_id'].eq(tablePolicyType['id']))

    cond = []
    cond.append(tableDiagnosis['deleted'].eq(0))
    cond.append(tableDiagnosis['mod_id'].isNull())
    addDateInRange(cond, tableDiagnosis['setDate'], begDate, endDate)
    if chkCreateDate:
        addDateInRange(cond, tableDiagnosis['createDatetime'], createBegDate, createEndDate)

#    cond.append(db.joinOr([tableDiagnosis['setDate'].isNull(), tableDiagnosis['setDate'].le(endDate)]))
#    cond.append(tableDiagnosis['endDate'].ge(begDate))

    tableEvent = None

    diagnosticQuery = tableDiagnostic
    diagnosticCond = [ tableDiagnostic['diagnosis_id'].eq(tableDiagnosis['id']),
                       tableDiagnostic['deleted'].eq(0)
                     ]
    if registeredInPeriod:
        addDateInRange(diagnosticCond, tableDiagnostic['setDate'], begDate, endDate)
    if personId:
        diagnosticCond.append(tableDiagnostic['person_id'].eq(personId))
    elif orgStructureId:
        diagnosticQuery = diagnosticQuery.leftJoin(tablePerson, tablePerson['id'].eq(tableDiagnostic['person_id']))
        diagnosticCond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    else:
        diagnosticQuery = diagnosticQuery.leftJoin(tablePerson, tablePerson['id'].eq(tableDiagnostic['person_id']))
        diagnosticCond.append(tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()))
    
    # Если задействован хотя бы один ищ фильтров, связанных с типом обращения, то приджойнить тип обращения.
    if eventTypeId or (not visitEmergency) or eventPurposeIdList:
        tableEvent = db.table('Event')
        tableEventType = db.table('EventType')
        diagnosticQuery = diagnosticQuery.leftJoin(tableEvent, tableEvent['id'].eq(tableDiagnostic['event_id']))
        diagnosticQuery = diagnosticQuery.leftJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
    
    if eventTypeId:
        diagnosticCond.append(tableEventType['id'].eq(eventTypeId))
    elif eventPurposeIdList:
        diagnosticCond.append(tableEventType['purpose_id'].inlist(eventPurposeIdList))
    
    if isPrimary:
        if not tableEvent:
            tableEvent = db.table('Event')
            diagnosticQuery = diagnosticQuery.leftJoin(tableEvent, tableEvent['id'].eq(tableDiagnostic['event_id']))
        diagnosticCond.append(tableEvent['isPrimary'].eq(isPrimary))
    
    if not visitEmergency:
        tableMedicalAidType = db.table('rbMedicalAidType')
        diagnosticQuery = diagnosticQuery.leftJoin(tableMedicalAidType, tableMedicalAidType['id'].eq(tableEventType['medicalAidType_id']))
        diagnosticCond.append(db.joinOr([tableMedicalAidType['code'].isNull(), tableMedicalAidType['code'].ne('4')]))    
    
    cond.append(db.existsStmt(diagnosticQuery, diagnosticCond))

    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append('(Diagnosis.endDate >= ADDDATE(Client.birthDate, INTERVAL %d YEAR) OR Diagnosis.endDate IS NULL)'%ageFrom)
        cond.append('(Diagnosis.endDate < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1) OR Diagnosis.endDate IS NULL)'%(ageTo+1))
    if socStatusTypeId:
        subStmt = ('SELECT ClientSocStatus.id FROM ClientSocStatus WHERE '
                  +'ClientSocStatus.deleted=0 AND ClientSocStatus.client_id=Client.id AND '
                  +'ClientSocStatus.socStatusType_id=%d' % socStatusTypeId)
        cond.append('EXISTS('+subStmt+')')
    elif socStatusClassId:
        subStmt = ('SELECT ClientSocStatus.id FROM ClientSocStatus WHERE '
                  +'ClientSocStatus.deleted=0 AND ClientSocStatus.client_id=Client.id AND '
                  +'ClientSocStatus.socStatusClass_id=%d' % socStatusClassId)
        cond.append('EXISTS('+subStmt+')')
    MKBCond = []
    for MKB in MKBList:
        MKBCond.append( tableDiagnosis['MKB'].like(MKB+'%') )
    cond.append(db.joinOr(MKBCond))
    if not accountAccomp:
        cond.append(tableDiagnosisType['code'].inlist(['1', '2', '4']))
    if locality:
        # 1: горожане, isClientVillager == 0 или NULL
        # 2: сельские жители, isClientVillager == 1
        cond.append('IFNULL(isClientVillager(Client.id), 0) = %d' % (locality-1))
    filterAddress = params.get('isFilterAddress', False)
    if filterAddress:
        filterAddressType = params.get('filterAddressType', 0)
        filterAddressCity = params.get('filterAddressCity', None)
        filterAddressStreet = params.get('filterAddressStreet', None)
        filterAddressHouse = params.get('filterAddressHouse', u'')
        filterAddressCorpus = params.get('filterAddressCorpus', u'')
        filterAddressFlat = params.get('filterAddressFlat', u'')
        queryTable = queryTable.leftJoin(tableClientAddress, tableClient['id'].eq(tableClientAddress['client_id']))
        cond.append(tableClientAddress['type'].eq(filterAddressType))
        cond.append(db.joinOr([tableClientAddress['id'].isNull(), tableClientAddress['deleted'].eq(0)]))
        if filterAddressCity or filterAddressStreet or filterAddressHouse or filterAddressCorpus or filterAddressFlat:
            queryTable = queryTable.leftJoin(tableAddress, tableClientAddress['address_id'].eq(tableAddress['id']))
            queryTable = queryTable.leftJoin(tableAddressHouse, tableAddress['house_id'].eq(tableAddressHouse['id']))
            cond.append(db.joinOr([tableAddress['id'].isNull(), tableAddress['deleted'].eq(0)]))
            cond.append(db.joinOr([tableAddressHouse['id'].isNull(), tableAddressHouse['deleted'].eq(0)]))

        if filterAddressCity:
            cond.append(tableAddressHouse['KLADRCode'].like(filterAddressCity))
        if filterAddressStreet:
            cond.append(tableAddressHouse['KLADRStreetCode'].like(filterAddressStreet))
        if filterAddressHouse:
            cond.append(tableAddressHouse['number'].eq(filterAddressHouse))
        if filterAddressCorpus:
            cond.append(tableAddressHouse['corpus'].eq(filterAddressCorpus))
        if filterAddressFlat:
            cond.append(tableAddress['flat'].eq(filterAddressFlat))
    
    return db.query(stmt % (db.getTableName(queryTable), db.joinAnd(cond)))


class CReportDailyAcuteInfections(CReport):
    rowTypes = [ (u'J10', u'Грипп, вызванный идентифицированным вирусом гриппа' ),
                 (u'J11', u'Грипп, вирус не идентифицирован' ),
                 (u'J03', u'Ангины'),
                 (u'J06', u'ОРВИ'  ),
                 (u'J18', u'Пневмония'),
                 (u'J20', u'Бронхит'),
               ]

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Ежедневный отчёт по выявленным острым инфекционным заболеваниям')


    def getSetupDialog(self, parent):
        result = CReportAcuteInfectionsSetupDialog(parent)
        result.setIsPrimaryVisible(True)
        result.setAccountAccompEnabled(True)
        result.setCreateDateEnabled(True)
        result.setTitle(self.title())
        result.adjustSize()
        return result


    def build(self, params):
        db = QtGui.qApp.db

        reportRowSize = 11

        mapMKBToTypeIndex = {}
        for index, rowType in enumerate(self.rowTypes):
            mapMKBToTypeIndex[rowType[0]] = index

        reportData = {}
        MKBList = []

        # i3805
        # словарь с ключом '%clientId%_%MKB%', в котором хранится
        # список дат начала первых попавшихся обращений с МКВ = %МКВ%
        reportConvertation = {}

        query = selectData(params, [t[0] for t in self.rowTypes])
        self.setQueryText(forceString(query.lastQuery()))
        while query.next() :
            record    = query.record()
            cnt       = forceInt(record.value('cnt'))
            MKB       = forceString(record.value('MKB'))
            age       = forceInt(record.value('clientAge'))
            sex       = forceInt(record.value('clientSex'))
            isWorking = forceBool(record.value('isWorking'))
            isPregnancy = forceBool(record.value('isPregnancy'))

            if QtGui.qApp.region() == '78':
                # i3805
                setDate = forceDate(record.value('setDate'))
                clientId = forceInt(record.value('clientId'))

                key = u'%s_%s' % (clientId, MKB)
                temp = reportConvertation.get(key, None)

                if not temp:
                    reportConvertation[key] = [setDate]
                else:
                    drop = False
                    for x in temp:
                        if x.daysTo(setDate) <= QtGui.qApp.getGlobalPreferenceAverangeDuration() and x != setDate:
                            drop = True
                            break
                    if drop:
                        continue

            reportRow = reportData.get(MKB, None)
            if not reportRow:
                reportRow = [0]*reportRowSize
                reportData[MKB] = reportRow
                MKBList.append(MKB)

            if age<3:
                cols = [0, 1, 2]
            elif age<5:
                cols = [0, 1, 3]
            elif age<7:
                cols = [0, 1, 4]
            elif age<15:
                cols = [0, 1, 5]
            elif age<65:
                cols = [0, 6]
            else:
                cols = [0, 6, 7]
            if age>=15:
                if isWorking:
                    cols += [8]
                else:
                    cols += [9]
                if isPregnancy:
                    cols += [10]

            for col in cols:
                reportRow[col] += cnt
#            if sex in [1, 2]:
#                reportRow[ageGroup*2+sex-1] += cnt
#                reportRow[5+sex] += cnt
#                reportRow[8] += cnt

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        if params.get('isFilterAddress', False):
            self.dumpParamsAdress(cursor, params)
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('15%', [u'диагноз'], CReportBase.AlignLeft),
            ( '7%', [u'всего'  ], CReportBase.AlignRight),
            ( '7%', [u'дети (0-14 лет)',     u'всего'], CReportBase.AlignRight),
            ( '7%', [u'',                    u'в т.ч.', u'0-2 года'], CReportBase.AlignRight),
            ( '7%', [u'',                    u'',       u'3-4 года'], CReportBase.AlignRight),
            ( '7%', [u'',                    u'',       u'5-6 лет'], CReportBase.AlignRight),
            ( '7%', [u'',                    u'',       u'7-14 лет'], CReportBase.AlignRight),
            ( '7%', [u'взрослые (15 лет и старше)', u'всего'], CReportBase.AlignRight),
            ( '7%', [u'',                          u'в т.ч.', u'65 лет и старше'], CReportBase.AlignRight),
            ( '7%', [u'',                          u'',       u'рабо-\nтающие'], CReportBase.AlignRight),
            ( '7%', [u'',                          u'',       u'не рабо-\nтающие'], CReportBase.AlignRight),
            ( '7%', [u'',                          u'',       u'бере-\nмен-\nные'], CReportBase.AlignRight),
            ]

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 3, 1) # ДЗ
        table.mergeCells(0, 1, 3, 1) # всего
        table.mergeCells(0, 2, 1, 5)
        table.mergeCells(1, 2, 2, 1)
        table.mergeCells(1, 3, 1, 4)
        table.mergeCells(0, 7, 1, 5)
        table.mergeCells(1, 7, 2, 1)
        table.mergeCells(1, 8, 1, 4)

        prevTypeIndex = None
        total = [0]*reportRowSize
        for MKB in MKBList:
            typeIndex = mapMKBToTypeIndex[MKB[:3]]
            if typeIndex != prevTypeIndex:
                if prevTypeIndex != None:
                    self.produceTotalLine(table, u'всего', total)
                i = table.addRow()
                table.mergeCells(i, 0, 1, reportRowSize+1)
                table.setText(i, 0, self.rowTypes[typeIndex][1])
                prevTypeIndex = typeIndex
                total = [0]*reportRowSize
            row = reportData[MKB]
            i = table.addRow()
            table.setText(i, 0, MKB)
            for j in xrange(reportRowSize):
                table.setText(i, j+1, row[j])
                total[j] += row[j]
        if prevTypeIndex != None:
            self.produceTotalLine(table, u'всего', total)
        return doc


    def produceTotalLine(self, table, title, total):
        i = table.addRow()
        table.setText(i, 0, title, CReportBase.TableTotal)
        for j in xrange(len(total)):
            table.setText(i, j+1, total[j], CReportBase.TableTotal)
