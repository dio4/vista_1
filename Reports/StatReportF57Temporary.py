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
    (u'Всего, из них:', u'S00 - T98'),
    (u'травмы головы, всего', u'S00 - S09'),
    (u'&nbsp;из них:<br/>перелом черепа и лицевых костей', u'S02'),
    (u'травма глаза и глазницы', u'S05'),
    (u'внутричерепная травма', u'S06'),
    (u'травмы шеи, всего', u'S10 - S19'),
    (u'&nbsp;из них:<br/>перелом шейного отдела позвоночника', u'S12'),
    (u'травма нервов и спинного мозга на уровне шеи', u'S14'),
    (u'травмы грудной клетки, всего', u'S20 - S29'),
    (u'&nbsp;из них:<br/>перелом ребра (ребер), грудины и грудного отдела позвоночника', u'S22'),
    (u'травма сердца', u'S26'),
    (u'травма других и неуточненных органов грудной полости', u'S27'),
    (u'травмы живота, нижней части спины, поясничного отдела позвоночника и таза, всего', u'S30 - S39'),
    (u'&nbsp;из них:<br/>перелом пояснично-крестцового отдела позвоночника и костей таза', u'S32'),
    (u'травма органов брюшной полости', u'S36'),
    (u'травма тазовых органов', u'S37'),
    (u'травмы плечевого пояса и плеча, всего', u'S40 - S49'),
    (u'&nbsp;из них:<br/>перелом на уровне плечевого пояса и плеча', u'S42'),
    (u'травмы локтя и предплечья, всего', u'S50 - S59'),
    (u'&nbsp;из них:<br/>перелом костей предплечья', u'S52'),
    (u'травмы запястья и кисти, всего', u'S60 - S69'),
    (u'&nbsp;из них:<br/>перелом на уровне запястья и кисти', u'S52'),
    (u'травмы области тазобедренного сустава и бедра, всего', u'S70 - S79'),
    (u'&nbsp;из них:<br/>перелом бедренной кости', u'S72'),
    (u'травмы колена и голени, всего', u'S80 - S89'),
    (u'&nbsp;из них:<br/>перелом костей голени, включая голеностопный сустав', u'S82'),
    (u'травмы области голеностопного сустава и стопы, всего', u'S90 - S99'),
    (u'&nbsp;из них:<br/>перелом стопы, исключая перелом голеностопного сустава', u'S92'),
    (u'травмы, захватывающие несколько областей тела, всего', u'T00 - T07'),
    (u'&nbsp;из них:<br/>переломы, захватывающие несколько областей тела', u'T02'),
    (u'травмы неуточненной части туловища, конечности или области тела', u'T08 - T14'),
    (u'последствия проникновения инородного тела через естественные отверстия', u'T15 - T19'),
    (u'термические и химические ожоги', u'T20 - T32'),
    (u'отморожение', u'T33 - T35'),
    (u'отравление лекарственными средствами, медикаментами и биологическими веществами, всего', u'T33 - T35'),
    (u'&nbsp;из них:<br/>отравление наркотиками', u'T40.0 - 6'),
    (u'отравление психотропными средствами', u'T43'),
    (u'токсическое действие веществ, преимущественно немедицинского назначения, всего', u'T51 - T65'),
    (u'&nbsp;из них:<br/>токсическое действие алкоголя', u'T51'),
    (u'другие и неуточненные эффекты воздействия внешних причин', u'T66 - T78'),
    (u'осложнения хирургических и терапевтических вмешательств', u'T80 - T88'),
    (u'последствия травм, отравлений и других последствий внешних причин', u'T90 - T98'),
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



class CStatReportF57Temporary(CReport):
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
        table = createTable(cursor, tableColumns)
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

