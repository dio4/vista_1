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
from Orgs.Utils                     import getOrgStructureDescendants
from Reports.Report                 import normalizeMKB, CReport
from Reports.ReportAcuteInfections  import CReportAcuteInfectionsSetupDialog
from Reports.ReportBase             import createTable, CReportBase


MainRows = [
  (u'Всего,\nв том числе:', u'S00 - T98'),
  (u'поверхностные травмы', u'S00, S10, S20, S30, S40, S50, S60, S70, S80, S90, T00, T09.0, T11.0, T13.0, T14.0'),
  (u'открытые  раны, травмы кровеносных сосудов', u'S01, S09.0, S11, S15, S21, S25, S31, S35, S41, S45, S51, S55, S61, S65, S71, S75, S81, S85, S91, S95, T01, T06.3, T09.1, T11.1, T11.4, T13.1, T13.4, T14.1, T14.5'),
  (u'переломы черепа и лицевых костей', u'S02'),
  (u'травмы глаза  и глазницы', u'S05'),
  (u'внутричерепные травмы', u'S06'),
  (u'переломы костей верхней конечности', u'S42, S52, S62, T02.2, T02.4, T10'),
  (u'в том числе перелом нижнего конца лучевой кости, сочетанный перелом нижних концов локтевой и лучевой кости', u'S52.5, 6'),
  (u'переломы костей нижней конечности', u'S72, S82, S92, T02.3, T02.5, T12'),
  (u'в том числе перелом нижнего конца бедренной кости', u'S72.4'),
  (u'переломы позвоночника, костей туловища, других и неуточненных областей тела', u'S12, S22, S32, T02.0, T02.1, T02.7-9, T08, T14.2'),
  (u'вывихи, растяжения и перенапряжения капсульно-связочного аппарата суставов, травмы мышц и сухожилий', u'S03, S09.1, S13, S16, S23, S29.0, S33, S39.0, S43, S46, S53, S56, S63, S66, S73, S76, S83, S86, S93, S96, T03, T06.4, T09.2, T09.5, T11.2, T11.5, T13.2, T13.5, T14.3, T14.6'),
  (u'травмы нервов и спинного мозга', u'S04, S14, S24, S34, S44, S54, S64, S74, S84, S94, T06.0-T06.2, T09.3, T09.4, T11.3, T13.3, T14.4'),
  (u'размозжения (раздавливание), травматические ампутации', u'S07, S08, S17, S18, S28, S38, S47, S48, S57, S58, S67, S68, S77, S78, S87, S88, S97, S98, T04, T05, T09.6, T11.6, T13.6, T14.7'),
  (u'травмы внутренних органов грудной и брюшной областей, таза', u'S26, S27, S36, S37, S39.6-9, T06.5'),
  (u'термические и химические ожоги', u'T20 - T32'),
  (u'отравления лекарственными средствами, медикаментами и биологическими веществами, токсическое действие веществ, преимущественно немедицинского назначения', u'T36 - T65'),
  (u'осложнения хирургических и терапевтических вмешательств, не классифицированные в других рубриках', u'T80 - T88'),
  (u'последствия травм, отравлений, других воздействий внешних причин', u'T90 - T98'),
  (u'прочие', u'S09.2, 7-9, S19, S29.7 - 9, S49, S59, S69, S79, S89, S99, T02.6, T06.8, T07, T09.8 - 9, T11.8 - 9, T13.8 - 9, T14.8 - 9, T15 - T19, T33 - T35, T66 - T79'),
    ]


def selectData(registeredInPeriod, begDate, endDate, eventPurposeIdList, eventTypeId, specialityId, hurtType, orgStructureId, personId, ageFrom, ageTo, socStatusClassId, socStatusTypeId, onlyFirstTime, notNullTraumaType, accountAccomp, locality, isPrimary):
    stmt="""
SELECT
   COUNT(*) AS sickCount,
   Diagnosis.MKB AS MKB,
   Client.sex AS sex,
   rbTraumaType.code AS traumaType,
   (ADDDATE(Client.birthDate, INTERVAL 18 YEAR) <= Diagnosis.endDate) AS adult
FROM Diagnosis
LEFT JOIN Client ON Client.id = Diagnosis.client_id
LEFT JOIN rbDiagnosisType    ON rbDiagnosisType.id = Diagnosis.diagnosisType_id
LEFT JOIN rbDiseaseCharacter ON rbDiseaseCharacter.id = Diagnosis.character_id
LEFT JOIN rbTraumaType       ON rbTraumaType.id = Diagnosis.traumaType_id
WHERE
%s
GROUP BY MKB, sex, traumaType, adult
    """
    # Какой-то из params скрыт на форме, но используется. Может привести к случайным багам.
    db = QtGui.qApp.db
    tableDiagnosis  = db.table('Diagnosis')
    tableDiseaseCharacter = db.table('rbDiseaseCharacter')
    tableClient = db.table('Client')
    tableDiagnostic = db.table('Diagnostic')
    tablePerson = db.table('Person')
    tableDiagnosisType = db.table('rbDiagnosisType')

    cond = []
    cond.append(tableDiagnosis['deleted'].eq(0))
    cond.append(tableDiagnosis['mod_id'].isNull())

#    cond.append(tableDiagnosis['traumaType_id'].isNotNull())
    cond.append(tableDiagnosis['MKB'].gt('S'))
    cond.append(tableDiagnosis['MKB'].lt('U'))

#    cond.append(db.joinOr([tableDiagnosis['setDate'].isNull(), tableDiagnosis['setDate'].le(endDate)]))
#    cond.append(db.joinOr([tableDiagnosis['endDate'].ge(begDate), tableDiseaseCharacter['code'].eq('3')]))

    if onlyFirstTime:
        cond.append(tableDiagnosis['setDate'].le(endDate))
        cond.append(tableDiagnosis['setDate'].ge(begDate))
    else:
        cond.append(db.joinOr([tableDiagnosis['setDate'].isNull(), tableDiagnosis['setDate'].lt(endDate.addDays(1))]))
        cond.append(db.joinOr([tableDiagnosis['endDate'].ge(begDate), tableDiseaseCharacter['code'].eq('3')]))

    if notNullTraumaType:
        cond.append(tableDiagnosis['traumaType_id'].isNotNull())

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
    if specialityId and not personId:
        diagnosticCond.append(tablePerson['speciality_id'].eq(specialityId))
    if hurtType:
        tableClientWorkHurt = db.table('ClientWork_Hurt')
        tableClientWork = db.table('ClientWork')
        diagnosticQuery = diagnosticQuery.leftJoin(tableClientWorkHurt, tableClientWorkHurt['master_id'].eq(tableClientWork['client_id'].eq(tableClient['id'])))
        diagnosticCond.append(tableClientWorkHurt['hurtType_id'].eq(hurtType))
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
    if isPrimary:
        tableEvent = db.table('Event')
        if not (eventTypeId or eventPurposeIdList):
            diagnosticQuery = diagnosticQuery.leftJoin(tableEvent, tableEvent['id'].eq(tableDiagnostic['event_id']))
            diagnosticCond.append(tableEvent['isPrimary'].eq(isPrimary))
    cond.append(db.existsStmt(diagnosticQuery, diagnosticCond))

#    if sex:
#        cond.append(tableClient['sex'].eq(sex))
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
    if not accountAccomp:
        cond.append(tableDiagnosisType['code'].inlist(['1', '2', '4']))
    if locality:
        # 1: горожане, isClientVillager == 0 или NULL
        # 2: сельские жители, isClientVillager == 1
        cond.append('IFNULL(isClientVillager(Client.id), 0) = %d' % (locality-1))
    return db.query(stmt % db.joinAnd(cond))


mapAdultTraumaTypeToColumns = {
'01' : [0, 11, 20],    # Промышленная
'04' : [1, 11, 20],    # Сельскохозяйственная
'02' : [4, 11, 20],    # Строительная
'03' : [2, 3, 11, 20], # Дорожно-транспортная
'05' : [4, 11, 20],    # Прочая
'06' : [5, 11, 20],    # Бытовая
'07' : [6, 11, 20],    # Уличная
'08' : [7, 8, 11, 20], # Дорожно-транспортная
#9 Школьная
'10': [9, 11, 20],     # Спортивная
'12': [10, 20, 21, 22],# Т.а.
''  : [10, 11, 20]     # Прочая
}

mapChildTraumaTypeToColumns = {
'06' : [12, 19, 20],    # Бытовая
'07' : [13, 19, 20],    # Уличная
'03' : [14, 15, 19, 20],# Дорожно-транспортная
'08' : [14, 15, 19, 20],# Дорожно-транспортная
'09' : [16, 19, 20],    # Школьная
'10': [17, 19, 20],     # Спортивная
'12': [19, 20, 21, 23], # Т.а.
''  : [18, 19, 20]      # Прочая
}

# столбики -
# взрослые
# 0 в промышленности
# 1 в с/х
# 2 транспортные - всего
# 3 транспортные - в т.ч. а/дор
# 4 прочие
# 5 бытовые
# 6 уличные
# 7 транспортные - всего
# 8 транспортные - в т.ч. а/дор
# 9 спортивные
#10  прочие
#11  итого
# дети и подростки
#12 бытовые
#13 уличные
#14 транспортные - всего
#15 транспортные - в т.ч. а/дор
#16 школьные
#17 спортивные
#18 прочие
#19 итого
#20 всего
#21 т.а.
#22 т.а. - взрослые
#23 т.а. - дети



class CStatReportF57(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Сведения о травмах, отравлениях и др. (Ф57)')


    def getDefaultParams(self):
        result = CReport.getDefaultParams(self)
        result['onlyFirstTime'] = True
        result['notNullTraumaType'] = False
        return result


    def getSetupDialog(self, parent):
        result = CReportAcuteInfectionsSetupDialog(parent)
        result.setMKBFilterEnabled(False)
        result.setAccountAccompEnabled(True)
        result.setOnlyFirstTimeEnabled(True)
        result.setNotNullTraumaTypeEnabled(True)
        result.setSpecialityPersonEnabled(True)
        result.setHurt(True)
        result.setIsPrimaryVisible(True)
        result.setTitle(self.title())
        return result


    def build(self, params):
        mapMainRows = createMapCodeToRowIdx( [row[1] for row in MainRows if row[1]] )
        registeredInPeriod = params.get('registeredInPeriod', False)
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        eventPurposeIdList = params.get('eventPurposeIdList', [])
        eventTypeId = params.get('eventTypeId', None)
        specialityId = params.get('specialityId', None)
        hurtType = params.get('hurtType', None)
        orgStructureId = params.get('orgStructureId', None)
        personId = params.get('personId', None)
        ageFrom = params.get('ageFrom', 0)
        ageTo = params.get('ageTo', 150)
        socStatusClassId = params.get('socStatusClassId', None)
        socStatusTypeId = params.get('socStatusTypeId', None)
        onlyFirstTime = params.get('onlyFirstTime', False)
        notNullTraumaType = params.get('notNullTraumaType', False)
        accountAccomp = params.get('accountAccomp', False)
        locality = params.get('locality', 0)
        onlyChilds = params.get('onlyChilds', False)
        isPrimary = params.get('isPrimary', 0)
        
        cutAdultColumnsCount = 12 if onlyChilds else 0
        rowSize = 24
        reportMainData = [ [0]*rowSize for row in xrange(len(MainRows)*2) ]

        query = selectData(registeredInPeriod, begDate, endDate, eventPurposeIdList, eventTypeId, specialityId, hurtType, orgStructureId, personId, ageFrom, ageTo, socStatusClassId, socStatusTypeId, onlyFirstTime, notNullTraumaType, accountAccomp, locality, isPrimary)
        while query.next():
            record   = query.record()
            sickCount = forceInt(record.value('sickCount'))
            MKB   = normalizeMKB(forceString(record.value('MKB')))
            sex   = forceInt(record.value('sex'))
            adult = forceBool(record.value('adult'))
            traumaType  = forceString(record.value('traumaType'))

            mapTraumaTypeToColumns = mapAdultTraumaTypeToColumns if adult else mapChildTraumaTypeToColumns
            columns = mapTraumaTypeToColumns.get(traumaType, None)
            if not columns:
                columns = mapTraumaTypeToColumns['']
                mapTraumaTypeToColumns[traumaType] = columns


            baseIndex = (0 if sex == 1 else 1)
            rows = mapMainRows.get(MKB, [])
            for row in rows:
                reportLine = reportMainData[baseIndex+row*2]
                for column in columns:
                    reportLine[column] += sickCount

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

#        cursor.setCharFormat(CReportBase.ReportTitle)
#        cursor.insertText(u'Сведения о травмах, отравлениях и некоторых других последствиях воздействия внешних причин (Ф57)')
#        cursor.insertBlock()
#        cursor.setCharFormat(CReportBase.ReportBody)
#        cursor.insertText(u'за период с %s по %s' % (forceString(begDate), forceString(endDate)))
#        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        
        tableColumns = [
            ('15%', [u'Травмы, отравления и некоторые другие последствия воздействия внешних причин',            u'', u'', u'',       u'1' ], CReportBase.AlignLeft),
            ('15%', [u'Код по МКБ X',                               u'',                             u'',                  u'',       u'2' ], CReportBase.AlignLeft),
            ( '3%', [u'Пол',                                        u'',                             u'',                  u'',       u'3' ], CReportBase.AlignCenter),
            ( '3%', [u'№ стр.',                                     u'',                             u'',                  u'',       u'4' ], CReportBase.AlignRight),
            ]
        if not onlyChilds:
            tableColumns.extend([
            ( '3%', [u'У взрослых (18 лет и старше)',               u'связанные с производством',    u'пром',              u'',       u'5' ], CReportBase.AlignRight),
            ( '3%', [u'',                                           u'',                             u'с/х',               u'',       u'6' ], CReportBase.AlignRight),
            ( '3%', [u'',                                           u'',                             u'трансп.',           u'вс',     u'7' ], CReportBase.AlignRight),
            ( '3%', [u'',                                           u'',                             u'',                  u'авт',    u'8' ], CReportBase.AlignRight),
            ( '3%', [u'',                                           u'',                             u'пр',                u'',       u'9' ], CReportBase.AlignRight),
            ( '3%', [u'',                                           u'быт',                          u'',                  u'',       u'10'], CReportBase.AlignRight),
            ( '3%', [u'',                                           u'не связанные с производством', u'ул',                u'',       u'11'], CReportBase.AlignRight),
            ( '3%', [u'',                                           u'',                             u'трансп.',           u'вс',     u'12'], CReportBase.AlignRight),
            ( '3%', [u'',                                           u'',                             u'',                  u'авт',    u'13'], CReportBase.AlignRight),
            ( '3%', [u'',                                           u'',                             u'спорт',             u'',       u'14'], CReportBase.AlignRight),
            ( '3%', [u'',                                           u'',                             u'пр',                u'',       u'15'], CReportBase.AlignRight),
            ( '3%', [u'',                                           u'ИТОГО',                        u'',                  u'',       u'16'], CReportBase.AlignRight),
            ])
        tableColumns.extend([
            ( '3%', [u'У детей (0 - 17 лет включительно)',          u'быт',                          u'',                  u'',       '%d' % (17 - cutAdultColumnsCount)], CReportBase.AlignRight),
            ( '3%', [u'',                                           u'ул',                           u'',                  u'',       '%d' % (18 - cutAdultColumnsCount)], CReportBase.AlignRight),
            ( '3%', [u'',                                           u'трансп.',                      u'вс',                u'',       '%d' % (19 - cutAdultColumnsCount)], CReportBase.AlignRight),
            ( '3%', [u'',                                           u'',                             u'авт',               u'',       '%d' % (20 - cutAdultColumnsCount)], CReportBase.AlignRight),
            ( '3%', [u'',                                           u'шк',                           u'',                  u'',       '%d' % (21 - cutAdultColumnsCount)], CReportBase.AlignRight),
            ( '3%', [u'',                                           u'спорт',                        u'',                  u'',       '%d' % (22 - cutAdultColumnsCount)], CReportBase.AlignRight),
            ( '3%', [u'',                                           u'пр',                           u'',                  u'',       '%d' % (23 - cutAdultColumnsCount)], CReportBase.AlignRight),
            ( '3%', [u'',                                           u'ИТОГО',                        u'',                  u'',       '%d' % (24 - cutAdultColumnsCount)], CReportBase.AlignRight),
            ( '3%', [u'ВСЕГО',                                      u'',                             u'',                  u'',       '%d' % (25 - cutAdultColumnsCount)], CReportBase.AlignRight),
            ( '3%', [u'Из гр.25',                                   u'в рез. терр. дей-\nствий',     u'',                  u'',       '%d' % (26 - cutAdultColumnsCount)], CReportBase.AlignRight),
            ( '3%', [u'Из гр.26',                                   u'у взро-\nслых',                u'',                  u'',       '%d' % (27 - cutAdultColumnsCount)], CReportBase.AlignRight),
            ( '3%', [u'',                                           u'у детей',                      u'',                  u'',       '%d' % (28 - cutAdultColumnsCount)], CReportBase.AlignRight),
            ])
        table = createTable(cursor, tableColumns, repeatHeader=False)
        table.mergeCells(0, 0, 4, 1) # п.н.
        table.mergeCells(0, 1, 4, 1) # мкб
        table.mergeCells(0, 2, 4, 1) # пол
        table.mergeCells(0, 3, 4, 1) # N
        if not onlyChilds:
            table.mergeCells(0, 4, 1,12) # взрослые
            table.mergeCells(1, 4, 1, 5) # произв.
            table.mergeCells(2, 4, 2, 1) # пром
            table.mergeCells(2, 5, 2, 1) # сх
            table.mergeCells(2, 6, 1, 2) # тр
            table.mergeCells(2, 8, 2, 1) # проч
            table.mergeCells(1, 9, 3, 1) # быт
            table.mergeCells(1, 10, 1, 5) # непроизв.
            table.mergeCells(2, 10, 2, 1) # ул
            table.mergeCells(2, 11, 1, 2) # тр
            table.mergeCells(2, 13, 2, 1) # сп
            table.mergeCells(2, 14, 2, 1) # пр
            table.mergeCells(1, 15, 3, 1) # итого
        table.mergeCells(0, 16 - cutAdultColumnsCount, 1, 8) # дети
        table.mergeCells(1, 16 - cutAdultColumnsCount, 3, 1) # быт
        table.mergeCells(1, 17 - cutAdultColumnsCount, 3, 1) # ул
        table.mergeCells(1, 18 - cutAdultColumnsCount, 1, 2) # трансп
        table.mergeCells(2, 18 - cutAdultColumnsCount, 2, 1) # всего
        table.mergeCells(2, 19 - cutAdultColumnsCount, 2, 1) # авт
        table.mergeCells(1, 20 - cutAdultColumnsCount, 3, 1) # шк
        table.mergeCells(1, 21 - cutAdultColumnsCount, 3, 1) # сп
        table.mergeCells(1, 22 - cutAdultColumnsCount, 3, 1) # пр
        table.mergeCells(1, 23 - cutAdultColumnsCount, 3, 1) # итого
        table.mergeCells(0, 24 - cutAdultColumnsCount, 4, 1) # ВСЕГО
        table.mergeCells(1, 25 - cutAdultColumnsCount, 3, 1) # т.а.
        table.mergeCells(0, 26 - cutAdultColumnsCount, 1, 2) # т.а. - по возр.
        table.mergeCells(1, 26 - cutAdultColumnsCount, 3, 1) # т.а. - взрослые
        table.mergeCells(1, 27 - cutAdultColumnsCount, 3, 1) # т.а. - дети

        for row, rowDescr in enumerate(MainRows) :
            man   = table.addRow()
            woman = table.addRow()
            table.setText(man, 0, rowDescr[0])
            table.setText(man, 1, rowDescr[1])
            table.mergeCells(man, 0, 2, 1) # п.н.
            table.mergeCells(man, 1, 2, 1) # мкб
            table.setText(man,   2, u'М')
            table.setText(man,   3, row*2+1)
            reportLine = reportMainData[row*2]
            for column in xrange(rowSize):
                if onlyChilds and (0 <= column <= 11):
                    continue
                table.setText(man, 4 + column - cutAdultColumnsCount, reportLine[column])

            table.setText(woman,   2, u'Ж')
            table.setText(woman,   3, row*2+2)
            reportLine = reportMainData[row*2+1]
            for column in xrange(rowSize):
                if onlyChilds and (0 <= column <= 11):
                    continue
                table.setText(woman, 4 + column - cutAdultColumnsCount, reportLine[column])
        return doc

