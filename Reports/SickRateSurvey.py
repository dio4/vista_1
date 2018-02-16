# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.database               import addDateInRange
from library.Utils                  import forceBool, forceInt, forceString, MKBwithoutSubclassification

from Orgs.Utils                     import getOrgStructureDescendants

from Reports.Report                 import CReport
from Reports.ReportAcuteInfections  import CReportAcuteInfectionsSetupDialog
from Reports.ReportBase             import createTable, CReportBase


MKB_INFO_STMT = '''
SELECT
  vMKBTree.ClassID AS ClassID,
  vMKBTree.ClassName AS ClassName,
  vMKBTree.BlockID AS BlockID,
  vMKBTree.BlockName AS BlockName,
  MKB_Tree.DiagName AS DiagName
FROM MKB_Tree
  LEFT JOIN vMKBTree ON MKB_Tree.DiagID IN (vMKBTree.BlockID, vMKBTree.ClassID, vMKBTree.Level1ID, vMKBTree.Level2ID)
WHERE MKB_Tree.DiagID = '%s'
LIMIT 0, 1;
'''


def selectData(params, countClientId = False):
# затея подсчитывать clientCount таким образом неверна.
# т.к. противоречит группировкам отличным от главной.
# но пока забъём
#    stmt="""
#SELECT
#   Diagnosis.MKB AS MKB,
#   COUNT(*) AS sickCount,
#   COUNT(DISTINCT Diagnosis.client_id) AS clientCount,
#   rbDiseaseCharacter.code AS diseaseCharacter,
#   (%s) AS firstInPeriod
#FROM Diagnosis
#LEFT JOIN Client ON Client.id = Diagnosis.client_id
#LEFT JOIN rbDiagnosisType    ON rbDiagnosisType.id = Diagnosis.diagnosisType_id
#LEFT JOIN rbDiseaseCharacter ON rbDiseaseCharacter.id = Diagnosis.character_id%s
#WHERE Diagnosis.deleted=0 AND Diagnosis.mod_id IS NULL AND %s
#GROUP BY MKB, diseaseCharacter, firstInPeriod
#    """
    isPrimary = params.get('isPrimary', 0)
    registeredInPeriod = params.get('registeredInPeriod', False)
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    eventPurposeIdList = params.get('eventPurposeIdList', [])
    eventTypeId = params.get('eventTypeId', None)
    specialityId = params.get('specialityId', None)
    hurtType = params.get('hurtType', None)
    orgStructureId = params.get('orgStructureId', None)
    personId = params.get('personId', None)
    sex = params.get('sex', 0)
    ageFrom = params.get('ageFrom', 0)
    ageTo = params.get('ageTo', 150)
    socStatusClassId = params.get('socStatusClassId', None)
    socStatusTypeId = params.get('socStatusTypeId', None)
    MKBFilter = params.get('MKBFilter', 0)
    MKBFrom   = params.get('MKBFrom', '')
    MKBTo     = params.get('MKBTo', '')
    MKBExFilter = params.get('MKBExFilter', 0)
    MKBExFrom   = params.get('MKBExFrom', '')
    MKBExTo     = params.get('MKBExTo', '')
    accountAccomp = params.get('accountAccomp', False)
    locality = params.get('locality', 0)
    db = QtGui.qApp.db
    tableDiagnosis  = db.table('Diagnosis')
    tableDiseaseCharacter = db.table('rbDiseaseCharacter')
    tableDiagnosisType = db.table('rbDiagnosisType')
    tableClient = db.table('Client')
    tableDiagnostic = db.table('Diagnostic')
    tablePerson = db.table('Person')
    tableClientAddress = db.table('ClientAddress')
    tableAddress = db.table('Address')
    tableAddressHouse = db.table('AddressHouse')
    tableEvent = db.table('Event')
    tableEventType = db.table('EventType')
    queryTable = tableDiagnosis.leftJoin(tableClient, tableDiagnosis['client_id'].eq(tableClient['id']))
    queryTable = queryTable.leftJoin(tableDiagnosisType, tableDiagnosis['diagnosisType_id'].eq(tableDiagnosisType['id']))
    queryTable = queryTable.leftJoin(tableDiseaseCharacter, tableDiagnosis['character_id'].eq(tableDiseaseCharacter['id']))
    cond = []
#    cond.append(tableDiagnosis['MKB'].lt('Z'))
    cond.append(db.joinOr([tableDiagnosis['setDate'].isNull(), tableDiagnosis['setDate'].le(endDate)]))
    cond.append(db.joinOr([tableDiagnosis['endDate'].ge(begDate), tableDiseaseCharacter['code'].eq('3')]))

    diagnosticQuery = tableDiagnostic
    diagnosticQuery = diagnosticQuery.leftJoin(tableEvent, tableEvent['id'].eq(tableDiagnostic['event_id']))
    diagnosticQuery = diagnosticQuery.leftJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
    diagnosticCond = [ tableDiagnostic['diagnosis_id'].eq(tableDiagnosis['id']),
                       tableDiagnostic['deleted'].eq(0)
                     ]
    if isPrimary:
        diagnosticCond.append(tableEvent['isPrimary'].eq(isPrimary))
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
    if specialityId and not personId:
        diagnosticCond.append(tablePerson['speciality_id'].eq(specialityId))
    if hurtType:
        tableClientWorkHurt = db.table('ClientWork_Hurt')
        tableClientWork = db.table('ClientWork')
        diagnosticQuery = diagnosticQuery.leftJoin(tableClientWorkHurt, tableClientWorkHurt['master_id'].eq(tableClientWork['client_id'].eq(tableClient['id'])))
        diagnosticCond.append(tableClientWorkHurt['hurtType_id'].eq(hurtType))
    if eventTypeId:
        diagnosticCond.append(tableEvent['eventType_id'].eq(eventTypeId))
    elif eventPurposeIdList:
        diagnosticCond.append(tableEventType['purpose_id'].inlist(eventPurposeIdList))
    cond.append(db.existsStmt(diagnosticQuery, diagnosticCond))

    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append('\'%s\' >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)' % (begDate.toString('yyyy-MM-dd'), ageFrom))
        cond.append('\'%s\' < ADDDATE(Client.birthDate, INTERVAL %d YEAR)' % (endDate.toString('yyyy-MM-dd'), ageTo))
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
    if MKBFilter == 1:
        cond.append(tableDiagnosis['MKB'].ge(MKBFrom))
        cond.append(tableDiagnosis['MKB'].le(MKBTo))
    else:
        cond.append(tableDiagnosis['MKB'].lt('Z'))
    if MKBExFilter == 1:
        cond.append(tableDiagnosis['MKBEx'].ge(MKBExFrom))
        cond.append(tableDiagnosis['MKBEx'].le(MKBExTo))
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

    if countClientId:
        stmt="""
    SELECT
       COUNT(DISTINCT Diagnosis.client_id) AS clientCount
    FROM %s
    WHERE Diagnosis.deleted=0 AND Diagnosis.mod_id IS NULL AND %s
        """ % (db.getTableName(queryTable),
               db.joinAnd(cond))
    else:
        stmt="""
    SELECT
       Diagnosis.MKB AS MKB,
       COUNT(*) AS sickCount,
       COUNT(DISTINCT Diagnosis.client_id) AS clientCount,
       rbDiseaseCharacter.code AS diseaseCharacter,
       (%s) AS firstInPeriod
    FROM %s
    WHERE Diagnosis.deleted=0 AND Diagnosis.mod_id IS NULL AND %s
    GROUP BY MKB, diseaseCharacter, firstInPeriod
        """ % (db.joinAnd([tableDiagnosis['setDate'].le(endDate),
                                        tableDiagnosis['setDate'].ge(begDate)]),
                            db.getTableName(queryTable),
                            db.joinAnd(cond))
    return db.query(stmt)


class CSickRateSurvey(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
#        self.setPayPeriodVisible(False)
        self.setTitle(u'Общая сводка по заболеваемости')


    def getSetupDialog(self, parent):
        result = CReportAcuteInfectionsSetupDialog(parent)
        result.setMKBFilterEnabled(True)
        result.setAccountAccompEnabled(True)
        result.setSpecialityPersonEnabled(True)
        result.setIsPrimaryVisible(True)
        result.setHurt(True)
        result.setTitle(self.title())
        return result


    def build(self, params):
        db = QtGui.qApp.db
        reportRowSize = 6
        reportData = {}
        records = selectData(params, True)
        query = selectData(params)
        countClientId = 0
        while records.next():
            record = records.record()
            countClientId = forceInt(record.value('clientCount'))
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record    = query.record()
            MKB       = forceString(record.value('MKB'))
            sickCount = forceInt(record.value('sickCount'))
            clientCount = forceInt(record.value('clientCount'))
            diseaseCharacter = forceString(record.value('diseaseCharacter'))
            firstInPeriod = forceBool(record.value('firstInPeriod'))

            reportRow = reportData.get(MKB, None)
            if not reportRow:
                reportRow = [0]*reportRowSize
                reportData[MKB] = reportRow
            reportRow[0] += sickCount
            if diseaseCharacter == '1': # острое
                reportRow[1] += sickCount
                reportRow[2] += sickCount
            else:
                if firstInPeriod:
                    reportRow[1] += sickCount
                    reportRow[3] += sickCount
                else:
                    reportRow[4] += sickCount
            reportRow[5] += clientCount


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
            ('25%', [u'Наименование',   u''], CReportBase.AlignLeft),
            ('5%',  [u'Код МКБ',        u''], CReportBase.AlignLeft),
            ('10%', [u'Всего',          u''], CReportBase.AlignRight),
            ('10%', [u'Впервые',        u'всего'], CReportBase.AlignRight),
            ('10%', [u'',               u'острые'], CReportBase.AlignRight),
            ('10%', [u'',               u'хрон.'], CReportBase.AlignRight),
            ('10%', [u'Хрон.',          u''], CReportBase.AlignRight),
            ('10%', [u'Чел',            u''], CReportBase.AlignRight),
            ]

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 2, 1) # Наименование
        table.mergeCells(0, 1, 2, 1) # Код МКБ
        table.mergeCells(0, 2, 2, 1) # Всего
        table.mergeCells(0, 3, 1, 3) # Впервые
        table.mergeCells(0, 6, 2, 1) # Хрон.
        table.mergeCells(0, 7, 2, 1) # Чел

        total = [0]*reportRowSize
        blockTotal = [0]*reportRowSize
        classTotal = [0]*reportRowSize
        MKBList = reportData.keys()
        MKBList.sort()
        prevBlockId = ''
        prevClassId = ''
        for MKB in MKBList:
            MKBRecord = db.getRecordEx(stmt=MKB_INFO_STMT % MKBwithoutSubclassification(MKB))
            if MKBRecord:
                classId   = forceString(MKBRecord.value('ClassID')) or 'Error'
                className = forceString(MKBRecord.value('ClassName')) or 'Error'
                blockId   = forceString(MKBRecord.value('BlockID')) or 'Error'
                blockName = forceString(MKBRecord.value('BlockName')) or 'Error'
                MKBName   = forceString(MKBRecord.value('DiagName')) or 'Error'
            else:
                classId   = '-'
                className = '-'
                blockId   = '-'
                blockName = '-'
                MKBName   = '-'

            if prevBlockId and prevBlockId != blockId:
                self.produceTotalLine(table, u'всего по блоку '+prevBlockId, blockTotal)
                blockTotal = [0]*reportRowSize
            if prevClassId and prevClassId != classId:
                self.produceTotalLine(table, u'всего по классу '+ prevClassId, classTotal)
                classTotal = [0]*reportRowSize
            if  prevClassId != classId:
                i = table.addRow()
                table.setText(i, 0, classId + '. ' +className)
                table.mergeCells(i, 0, 1, 8)
                prevClassId = classId
            if  prevBlockId != blockId:
                i = table.addRow()
                table.setText(i, 0, blockId+ ' '+blockName)
                table.mergeCells(i, 0, 1, 8)
                prevBlockId = blockId
            row = reportData[MKB]
            i = table.addRow()
            table.setText(i, 0, MKBName)
            table.setText(i, 1, MKB)
            for j in xrange(reportRowSize):
                table.setText(i, j+2, row[j])
                total[j] += row[j]
                blockTotal[j] += row[j]
                classTotal[j] += row[j]
        if prevBlockId:
            self.produceTotalLine(table, u'всего по блоку '+prevBlockId, blockTotal)
        if prevClassId:
            self.produceTotalLine(table, u'всего по классу '+prevClassId, classTotal)
        total[reportRowSize-1] = countClientId
        self.produceTotalLine(table, u'ВСЕГО', total)
        return doc


    def produceTotalLine(self, table, title, total):
        i = table.addRow()
        table.setText(i, 0, title, CReportBase.TableTotal)
        for j in xrange(len(total)):
            table.setText(i, j+2, total[j], CReportBase.TableTotal)
