# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.database               import addDateInRange
from library.MapCode                import createMapCodeToRowIdx
from library.Utils                  import forceBool, forceInt, forceString
from Orgs.Utils                     import getOrgStructureDescendants, getOrgStructures
from Reports.Report                 import CReport, normalizeMKB
from Reports.ReportAcuteInfections  import CReportAcuteInfectionsSetupDialog
from Reports.ReportBase             import createTable, CReportBase


MainRows = [
    ( u'Синдром врождённой йодной недостаточности', '01', u'E00'),
    ( u'Диффузный (эндемический) зоб, связанный с йодной недостаточностью и другие формы диффузного нетоксического зоба', '02', u'E01.0, E01.2, E04.0'),
    ( u'Многоузловой (эндемический) зоб, связанный с йодной недостаточностью, другие формы нетоксического зоба', '03', u'E01.1, E04.1, E04.2, E04.8, E04.9'),
    ( u'Многоузловой (эндемический) зоб, связанный с йодной недостаточностью, нетоксический одноузловой, нетоксический многоузловой зоб', '03', u'E01.1, E04.1, E04.2'),
    ( u'Другие уточненные формы нетоксического зоба', '03.2', u'E04.8'),
    ( u'Нетоксический зоб неуточненный', '03.3', u'E04.9'),
    ( u'Субклинический гипотериоз вследствие йодной недостаточности, другие формы гипотериоза', '04', u'E02, E03'),
    ( u'Тиреотоксикоз (гипертериоз)', '05', u'E05'),
    ( u'Тиреоидит (гипертериоз)', '06', u'E06'),
    ]

def selectData(registeredInPeriod, begDate, endDate, eventPurposeIdList, eventTypeId, orgStructureId, personId, sex, ageFrom, ageTo, socStatusClassId, socStatusTypeId, areaIdEnabled, areaId, locality):
    stmt="""
SELECT
   age(Client.birthDate, Diagnosis.endDate) AS clientAge,
   Diagnosis.MKB AS MKB,
   (%s) AS firstInLife,
   COUNT(*) AS sickCount
FROM Diagnosis
LEFT JOIN Client ON Client.id = Diagnosis.client_id
LEFT JOIN ClientAddress ON ClientAddress.client_id = Diagnosis.client_id
                        AND ClientAddress.id = (SELECT MAX(id) FROM ClientAddress AS CA WHERE CA.Type=1 and CA.client_id = Diagnosis.client_id)
LEFT JOIN Address ON Address.id = ClientAddress.address_id
LEFT JOIN rbDiseaseCharacter ON rbDiseaseCharacter.id = Diagnosis.character_id
WHERE Diagnosis.MKB LIKE 'E0%%' AND %s
GROUP BY clientAge, MKB, firstInLife
    """

    db = QtGui.qApp.db
    tableDiagnosis  = db.table('Diagnosis')
    tableDiseaseCharacter = db.table('rbDiseaseCharacter')
    tableClient = db.table('Client')
    tableDiagnostic = db.table('Diagnostic')
    tablePerson = db.table('Person')

    cond = []
    cond.append(tableDiagnosis['deleted'].eq(0))
    cond.append(tableDiagnosis['mod_id'].isNull())
    cond.append(db.joinOr([tableDiagnosis['setDate'].isNull(), tableDiagnosis['setDate'].lt(endDate.addDays(1))]))
    cond.append(db.joinOr([tableDiagnosis['endDate'].ge(begDate), tableDiseaseCharacter['code'].eq('3')]))

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
    if eventTypeId:
        tableEvent = db.table('Event')
        diagnosticQuery = diagnosticQuery.leftJoin(tableEvent, tableEvent['id'].eq(tableDiagnostic['event_id']))
        diagnosticCond.append(tableEvent['eventType_id'].eq(eventTypeId))
    elif eventPurposeIdList:
        tableEvent = db.table('Event')
        tableEventType = db.table('EventType')
        diagnosticQuery = diagnosticQuery.leftJoin(tableEvent, tableEvent['id'].eq(tableDiagnostic['event_id']))
        diagnosticQuery = diagnosticQuery.leftJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
        diagnosticCond.append(tableEventType['purpose_id'].inlist(eventPurposeIdList))
    cond.append(db.existsStmt(diagnosticQuery, diagnosticCond))

    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append('Diagnosis.endDate >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)'%ageFrom)
        cond.append('Diagnosis.endDate < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)'%(ageTo+1))
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
    if areaIdEnabled:
        if areaId:
            orgStructureIdList = getOrgStructureDescendants(areaId)
        else:
            orgStructureIdList = getOrgStructures(QtGui.qApp.currentOrgId())
        tableOrgStructureAddress = db.table('OrgStructure_Address')
        tableAddress = db.table('Address')
        subCond = [ tableOrgStructureAddress['master_id'].inlist(orgStructureIdList),
                    tableOrgStructureAddress['house_id'].eq(tableAddress['house_id']),
                  ]
        cond.append(db.existsStmt(tableOrgStructureAddress, subCond))
#    return db.query(stmt % (db.joinOr([tableDiagnosis['setDate'].isNull(), tableDiagnosis['setDate'].lt(endDate.addDays(1))]),
    if locality:
        # 1: горожане, isClientVillager == 0 или NULL
        # 2: сельские жители, isClientVillager == 1
        cond.append('IFNULL(isClientVillager(Client.id), 0) = %d' % (locality-1))
    return db.query(stmt % (tableDiagnosis['setDate'].ge(begDate),
                            db.joinAnd(cond)))


class CStatReportF63(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Сведения о заболеваниях, связанных с микронутриентной недостаточностью (Ф63)')


    def getDefaultParams(self):
        result = CReport.getDefaultParams(self)
        result['ageFrom']     = 0
        result['ageTo']       = 150
        return result


    def getSetupDialog(self, parent):
        result = CReportAcuteInfectionsSetupDialog(parent)
        result.setAreaEnabled(True)
#        result.setMKBFilterEnabled(False)
#        result.setAccountAccompEnabled(False)
        result.setTitle(self.title())
        return result


    def build(self, params):
        mapMainRows = createMapCodeToRowIdx( [row[2] for row in MainRows] )
        registeredInPeriod = params.get('registeredInPeriod', False)
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        eventPurposeIdList = params.get('eventPurposeIdlist', [])
        eventTypeId = params.get('eventTypeId', None)
        orgStructureId = params.get('orgStructureId', None)
        personId = params.get('personId', None)
        sex = params.get('sex', 0)
        ageFrom = params.get('ageFrom', 0)
        ageTo = params.get('ageTo', 150)
        socStatusClassId = params.get('socStatusClassId', None)
        socStatusTypeId = params.get('socStatusTypeId', None)
        areaIdEnabled = params.get('areaIdEnabled', None)
        areaId = params.get('areaId', None)
        locality = params.get('locality', 0)
        reportData = []
        reportLine = None
        prevDoctorId = None

        query = selectData(registeredInPeriod, begDate, endDate, eventPurposeIdList, eventTypeId, orgStructureId, personId, sex, ageFrom, ageTo, socStatusClassId, socStatusTypeId, areaIdEnabled, areaId, locality)

        rowSize = 15
        report1000Data = [ [0]*rowSize for row in xrange(len(MainRows)) ]
        report2000Data = [ [0]*rowSize for row in xrange(len(MainRows)) ]

        while query.next() :
            record    = query.record()
            age       = forceInt(record.value('clientAge'))
            MKB       = normalizeMKB(forceString(record.value('MKB')))
            firstInLife = forceBool(record.value('firstInLife'))
            sickCount = forceInt(record.value('sickCount'))

            ageCol = min(max(age, 0), 60)/5 + (1 if age >= 18 else 0) + 1
            for row in mapMainRows.get(MKB, []):
                reportLine = report1000Data[row]
                reportLine[0] += sickCount
                reportLine[ageCol] += sickCount
                if firstInLife:
                    reportLine = report2000Data[row]
                    reportLine[0] += sickCount
                    reportLine[ageCol] += sickCount

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('15%', [u'Наименование болезни',          u'',            u'1' ], CReportBase.AlignLeft),
            ( '5%', [u'№ строки',                      u'',            u'2' ], CReportBase.AlignRight),
            ( '5%', [u'Код по МКБ X',                  u'',            u'3' ], CReportBase.AlignLeft),
            ( '5%', [u'Всего',                         u'',            u'4' ], CReportBase.AlignRight),
            ( '5%', [u'в т.ч. у больных в возрасте (лет)', u'0-4',     u'5' ], CReportBase.AlignRight),
            ( '5%', [u'',                              u'5-9',         u'6' ], CReportBase.AlignRight),
            ( '5%', [u'',                              u'10-14',       u'7' ], CReportBase.AlignRight),
            ( '5%', [u'',                              u'15-17',       u'8' ], CReportBase.AlignRight),
            ( '5%', [u'',                              u'18-19',       u'9' ], CReportBase.AlignRight),
            ( '5%', [u'',                              u'20-24',       u'10'], CReportBase.AlignRight),
            ( '5%', [u'',                              u'25-29',       u'11'], CReportBase.AlignRight),
            ( '5%', [u'',                              u'30-34',       u'12'], CReportBase.AlignRight),
            ( '5%', [u'',                              u'35-39',       u'13'], CReportBase.AlignRight),
            ( '5%', [u'',                              u'40-44',       u'14'], CReportBase.AlignRight),
            ( '5%', [u'',                              u'45-49',       u'15'], CReportBase.AlignRight),
            ( '5%', [u'',                              u'50-54',       u'16'], CReportBase.AlignRight),
            ( '5%', [u'',                              u'55-59',       u'17'], CReportBase.AlignRight),
            ( '5%', [u'',                              u'60 и старше', u'18'], CReportBase.AlignRight),
            ]

        cursor.insertText(u'(1000) Зарегистрировано заболеваний')
        cursor.insertBlock()
        self.addTable(cursor, tableColumns, report1000Data)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertText(u'(2000) Зарегистрировано заболеваний c впервые в жизни установленным диагнозом')
        cursor.insertBlock()
        self.addTable(cursor, tableColumns, report2000Data)
        return doc


    def addTable(self, cursor, tableColumns, tableData):
        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 2, 1) # п.н.
        table.mergeCells(0, 1, 2, 1) # N
        table.mergeCells(0, 2, 2, 1) # мкб
        table.mergeCells(0, 3, 2, 1) # всего
        table.mergeCells(0, 4, 1, 14) # по возрастам

        for row, rowDescr in enumerate(MainRows) :
            i = table.addRow()
            table.setText(i, 0, rowDescr[0])
            table.setText(i, 1, rowDescr[1])
            table.setText(i, 2, rowDescr[2])
            reportLine = tableData[row]
            for col in xrange(len(reportLine)):
                table.setText(i, 3+col, reportLine[col])

