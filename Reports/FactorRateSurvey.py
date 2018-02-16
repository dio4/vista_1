# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Orgs.Utils import getOrgStructureDescendants
from Reports.Report import CReport
from Reports.ReportAcuteInfections import CReportAcuteInfectionsSetupDialog
from Reports.ReportBase import createTable, CReportBase
from library.Utils import forceInt, forceString, MKBwithoutSubclassification
from library.database import addDateInRange


def selectData(params):
    #TODO:skkachaev >неверно >пока забьём >2008г okay
# затея подсчитывать clientCount таким образом неверна.
# т.к. противоречит группировкам отличным от главной.
# но пока забъём
    isPrimary = params.get('isPrimary', 0)
    registeredInPeriod = params.get('registeredInPeriod', False)
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
    MKBFilter = params.get('MKBFilter', 0)
    MKBFrom   = params.get('MKBFrom', '')
    MKBTo     = params.get('MKBTo', '')
    MKBExFilter = params.get('MKBExFilter', 0)
    MKBExFrom   = params.get('MKBExFrom', '')
    MKBExTo     = params.get('MKBExTo', '')
    locality    = params.get('locality', 0)
    stmt="""
SELECT
   Diagnosis.MKB AS MKB,
   COUNT(*) AS sickCount,
   COUNT(DISTINCT Diagnosis.client_id) AS clientCount
FROM Diagnosis
LEFT JOIN Client ON Client.id = Diagnosis.client_id
LEFT JOIN rbDiagnosisType    ON rbDiagnosisType.id = Diagnosis.diagnosisType_id
WHERE %s
GROUP BY MKB
    """
    db = QtGui.qApp.db
    tableDiagnosis  = db.table('Diagnosis')
    tablePerson = db.table('Person')
    tableDiseaseCharacter = db.table('rbDiseaseCharacter')
    tableClient = db.table('Client')
    tableDiagnostic = db.table('Diagnostic')
    tablePerson = db.table('Person')
    tableEvent = db.table('Event')
    tableEventType = db.table('EventType')

    cond = []
    cond.append(tableDiagnosis['deleted'].eq(0))
    cond.append(tableDiagnosis['mod_id'].isNull())
    cond.append(tableDiagnosis['MKB'].ge('Z'))
    cond.append(tableDiagnosis['setDate'].le(endDate))

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
    if eventTypeId:
        diagnosticCond.append(tableEvent['eventType_id'].eq(eventTypeId))
    elif eventPurposeIdList:
        diagnosticCond.append(tableEventType['purpose_id'].inlist(eventPurposeIdList))
    cond.append(db.existsStmt(diagnosticQuery, diagnosticCond, limit='1'))

    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append('Diagnosis.endDate >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)'%ageFrom)
        cond.append('Diagnosis.endDate < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)'%(ageTo+1))
    if socStatusTypeId:
        subStmt = ('SELECT ClientSocStatus.id FROM ClientSocStatus WHERE '
                  +'ClientSocStatus.deleted=0 AND ClientSocStatus.client_id=Client.id AND '
                  +'ClientSocStatus.socStatusType_id=%d LIMIT 1 ' % socStatusTypeId)
        cond.append('EXISTS('+subStmt+')')
    elif socStatusClassId:
        subStmt = ('SELECT ClientSocStatus.id FROM ClientSocStatus WHERE '
                  +'ClientSocStatus.deleted=0 AND ClientSocStatus.client_id=Client.id AND '
                  +'ClientSocStatus.socStatusClass_id=%d LIMIT 1 ' % socStatusClassId)
        cond.append('EXISTS('+subStmt+')')
    if MKBFilter == 1:
        cond.append(tableDiagnosis['MKB'].ge(MKBFrom))
        cond.append(tableDiagnosis['MKB'].le(MKBTo))
    if MKBExFilter == 1:
        cond.append(tableDiagnosis['MKBEx'].ge(MKBExFrom))
        cond.append(tableDiagnosis['MKBEx'].le(MKBExTo))
    if locality:
        # 1: горожане, isClientVillager == 0 или NULL
        # 2: сельские жители, isClientVillager == 1
        cond.append('IFNULL(isClientVillager(Client.id), 0) = %d' % (locality-1))
    return db.query(stmt % (db.joinAnd(cond)))


class CFactorRateSurvey(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
#        self.setPayPeriodVisible(False)
        self.setTitle(u'Общая сводка по факторам')


    def getSetupDialog(self, parent):
        result = CReportAcuteInfectionsSetupDialog(parent)
        result.setMKBFilterEnabled(True)
        result.setIsPrimaryVisible(True)
        result.setTitle(self.title())
        return result


    def build(self, params):
        db = QtGui.qApp.db
        reportRowSize = 2
        reportData = {}
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next() :
            record    = query.record()
            MKB       = forceString(record.value('MKB'))
            sickCount = forceInt(record.value('sickCount'))
            clientCount = forceInt(record.value('clientCount'))

            reportRow = reportData.get(MKB, None)
            if not reportRow:
                reportRow = [0]*reportRowSize
                reportData[MKB] = reportRow
            reportRow[0] += sickCount
            reportRow[1] += clientCount


        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('25%', [u'Наименование'], CReportBase.AlignLeft),
            ('5%',  [u'Код МКБ'     ], CReportBase.AlignLeft),
            ('10%', [u'Всего'       ], CReportBase.AlignRight),
            ('10%', [u'Чел'         ], CReportBase.AlignRight),
            ]

        table = createTable(cursor, tableColumns)
#        table.mergeCells(0, 0, 2, 1) # Наименование
#        table.mergeCells(0, 1, 2, 1) # Код МКБ
#        table.mergeCells(0, 2, 2, 1) # Всего
#        table.mergeCells(0, 7, 2, 1) # Чел

        total = [0]*reportRowSize
        blockTotal = [0]*reportRowSize
        classTotal = [0]*reportRowSize
        MKBList = reportData.keys()
        MKBList.sort()
        MKBTable = db.table('MKB_Tree')
        prevBlockId = ''
        prevClassId = ''
        for MKB in MKBList:
            MKBRecord = db.getRecordEx(MKBTable, 'getMKBClassID(MKB_Tree.DiagID) as ClassID, '
                                                 '(Select MKB2.DiagName From MKB_Tree as MKB2 Where MKB2.DiagID = getMKBClassID(MKB_Tree.DiagID)) as ClassName, '
                                                 'getMKBBlockID(MKB_Tree.DiagID) as BlockID, '
                                                 '(Select MKB2.DiagName From MKB_Tree as MKB2 Where MKB2.DiagID = getMKBBlockID(MKB_Tree.DiagID)) as BlockName, '
                                                 'DiagName', MKBTable['DiagID'].eq(MKBwithoutSubclassification(MKB)))
            if MKBRecord:
                classId   = forceString(MKBRecord.value('ClassID'))
                className = forceString(MKBRecord.value('ClassName'))
                blockId   = forceString(MKBRecord.value('BlockID'))
                blockName = forceString(MKBRecord.value('BlockName'))
                MKBName   = forceString(MKBRecord.value('DiagName'))
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
                table.mergeCells(i, 0, 1, 4)
                prevClassId = classId
            if  prevBlockId != blockId:
                i = table.addRow()
                table.setText(i, 0, blockId+ ' '+blockName)
                table.mergeCells(i, 0, 1, 4)
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
        self.produceTotalLine(table, u'ВСЕГО', total)
        return doc


    def produceTotalLine(self, table, title, total):
        i = table.addRow()
        table.setText(i, 0, title, CReportBase.TableTotal)
        for j in xrange(len(total)):
            table.setText(i, j+2, total[j], CReportBase.TableTotal)
