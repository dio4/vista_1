# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui
from library.database               import addDateInRange
from library.Utils                  import forceBool, forceInt, forceString, getVal
from Orgs.Utils                     import getOrganisationInfo
from Reports.Report                 import CReport
from Reports.ReportBase             import createTable, CReportBase
from Reports.StatReportDD2013Weekly import CReportDD2013WeeklySetupDialog
from StatReportDDFoundIllnesses     import MKBinString


def selectData(params, diseaseCharacterCodes):
    sex = params.get('sex', 0)
    ageFrom = params.get('ageFrom', 0)
    ageTo = params.get('ageTo', 150)
    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)
    payStatusCode = params.get('payStatusCode', None)
    eventTypeId  = params.get('eventTypeId', None)

    db = QtGui.qApp.db
    tableClient = db.table('Client')
    tableEvent = db.table('Event')
    tableEventKind = db.table('rbEventKind')
    tableAction = db.table('Action')
    tableEventType = db.table('EventType')
    tableDiagnostic = db.table('Diagnostic')
    tableDiagnosis = db.table('Diagnosis')
    tableDiseaseCharacter = db.table('rbDiseaseCharacter')
    tableDiagnosticResult = db.table('rbDiagnosticResult')
    tableDispanser = db.table('rbDispanser')

    queryTableForDiagMKB = tableClient.innerJoin(tableEventType, db.joinAnd([tableEventType['deleted'].eq(0), tableClient['deleted'].eq(0)]))
    queryTableForDiagMKB = queryTableForDiagMKB.innerJoin(tableEventKind, [tableEventType['eventKind_id'].eq(tableEventKind['id']), tableEventKind['code'].inlist(['01', '02'])])
    queryTableForDiagMKB = queryTableForDiagMKB.innerJoin(tableEvent, db.joinAnd([tableEvent['eventType_id'].eq(tableEventType['id']), tableEvent['deleted'].eq(0), tableEvent['client_id'].eq(tableClient['id'])]))
    queryTableForDiagMKB = queryTableForDiagMKB.innerJoin(tableDiagnostic, db.joinAnd([tableDiagnostic['event_id'].eq(tableEvent['id']), tableDiagnostic['deleted'].eq(0)]))
    queryTableForDiagMKB = queryTableForDiagMKB.innerJoin(tableDiseaseCharacter, db.joinAnd([tableDiseaseCharacter['id'].eq(tableDiagnostic['character_id']),  tableDiseaseCharacter['code'].inlist(diseaseCharacterCodes)]))
    queryTableForDiagMKB = queryTableForDiagMKB.leftJoin(tableDiagnosis, db.joinAnd([tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']), tableDiagnosis['deleted'].eq(0)]))
    queryTableForDiagMKB = queryTableForDiagMKB.leftJoin(tableDispanser, [tableDispanser['id'].eq(tableDiagnosis['dispanser_id']), tableDispanser['code'].inlist(['2', '6'])])

    queryTableForActionMKB = tableClient.innerJoin(tableEventType, db.joinAnd([tableEventType['deleted'].eq(0), tableClient['deleted'].eq(0)]))
    queryTableForActionMKB = queryTableForActionMKB.innerJoin(tableEventKind, [tableEventType['eventKind_id'].eq(tableEventKind['id']), tableEventKind['code'].inlist(['01', '02'])])
    queryTableForActionMKB = queryTableForActionMKB.innerJoin(tableEvent, db.joinAnd([tableEvent['eventType_id'].eq(tableEventType['id']), tableEvent['deleted'].eq(0), tableEvent['client_id'].eq(tableClient['id'])]))
    queryTableForActionMKB = queryTableForActionMKB.innerJoin(tableAction, [tableAction['event_id'].eq(tableEvent['id']), tableAction['deleted'].eq(0), tableAction['MKB'].ne('')])
    queryTableForActionMKB = queryTableForActionMKB.leftJoin(tableDiagnostic, db.joinAnd([tableDiagnostic['event_id'].eq(tableEvent['id']), tableDiagnostic['deleted'].eq(0)]))
    queryTableForActionMKB = queryTableForActionMKB.leftJoin(tableDiseaseCharacter, db.joinAnd([tableDiseaseCharacter['id'].eq(tableDiagnostic['character_id']),  tableDiseaseCharacter['code'].inlist(diseaseCharacterCodes)]))
    queryTableForActionMKB = queryTableForActionMKB.leftJoin(tableDiagnosis, db.joinAnd([tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']), tableDiagnosis['deleted'].eq(0)]))
    queryTableForActionMKB = queryTableForActionMKB.leftJoin(tableDispanser, [tableDispanser['id'].eq(tableDiagnosis['dispanser_id']), tableDispanser['code'].inlist(['2', '6'])])

    cols = [
        'Event.id as event_id',
        'age(Client.birthDate, Event.setDate) as clientAge',
        tableClient['sex'],
        tableDiagnostic['stage_id'],
        tableDispanser['code'].alias('dispanserCode')
    ]

    columnsForSelect = [
        'COUNT(DISTINCT t.event_id) as count,'
        't.clientAge',
        't.MKB',
        't.sex',
        't.stage_id',
        't.dispanserCode'
    ]

    group = [
        't.sex',
        't.clientAge',
        't.MKB',
        't.stage_id',
        't.dispanserCode'
    ]

    if diseaseCharacterCodes == [5]:
        cols.append(tableDiagnosticResult['id'].alias('diagnosticResultId'))
        columnsForSelect.append('t.diagnosticResultId')
        queryTableForDiagMKB = queryTableForDiagMKB.leftJoin(tableDiagnosticResult, [tableDiagnosticResult['id'].eq(tableDiagnostic['result_id']), tableDiagnosticResult['code'].eq('26')])
        queryTableForActionMKB = queryTableForActionMKB.leftJoin(tableDiagnosticResult, [tableDiagnosticResult['id'].eq(tableDiagnostic['result_id']), tableDiagnosticResult['code'].eq('26')])
        group.append('t.diagnosticResultId')

    cond = []
    if not params.get('countUnfinished', False):
        addDateInRange(cond, tableEvent['execDate'], begDate, endDate)
    else:
        addDateInRange(cond, tableEvent['setDate'], begDate, endDate)

    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append(u'Event.setDate >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)'%ageFrom)
        cond.append(u'Event.setDate < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)'%(ageTo+1))
    if payStatusCode is not None:
        tableContract = db.table('Contract')
        queryTableForDiagMKB = queryTableForDiagMKB.leftJoin(tableContract, tableContract['id'].eq(tableEvent['contract_id']))
        queryTableForActionMKB = queryTableForActionMKB.leftJoin(tableContract, tableContract['id'].eq(tableEvent['contract_id']))
        cond.append('getPayCode(%s, %s) = %d' % (tableContract['finance_id'],
                                                 tableEvent['payStatus'],
                                                 payStatusCode)
                    )
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    queryForDiagMKB = db.selectStmt(queryTableForDiagMKB, cols + [tableDiagnosis['MKB']], cond)
    queryForActionMKB = db.selectStmt(queryTableForActionMKB, cols + [tableAction['MKB']], cond)

    stmt = """
SELECT %(columnsForSelect)s
FROM ((%(queryForDiagMKB)s)
    UNION ALL
    (%(queryForActionMKB)s)
) t
GROUP BY %(groupBy)s
""" % {'columnsForSelect': ', '.join(columnsForSelect),
       'queryForDiagMKB': queryForDiagMKB,
       'queryForActionMKB': queryForActionMKB,
       'groupBy': ', '.join(group)
       }
    return db.query(stmt)


class CReportDD2015FoundIllnesses(CReport):
    def __init__(self, parent, diseaseCharacterCodes=None):
        CReport.__init__(self, parent)
        if not diseaseCharacterCodes:
            diseaseCharacterCodes = [3, 4]
        self.diseaseCharacterCodes = diseaseCharacterCodes
        self.setPayPeriodVisible(False)
        if diseaseCharacterCodes == [3, 4]:
            self.setTitle(u'Сведения о выявленных при проведении диспансеризации заболеваниях (случаев')
        elif diseaseCharacterCodes == [2]:
            self.setTitle(u'Сведения о впервые выявленных при проведении диспансеризации заболеваниях (случаев)')
        elif diseaseCharacterCodes == [5]:
            self.setTitle(u'Сведения о выявленных в ходе диспансеризации подозрениях на заболевание')
        else:
            self.setTitle(u'[ERROR]')

    def getSetupDialog(self, parent):
        result = CReportDD2013WeeklySetupDialog(parent)
        result.setTitle(self.title())
        return result

    def processRow(self, row, sex, age, dispanser, count):
        if 21 <= age <= 36 or 39 <= age:
            row[14] += count
            if dispanser:
                row[15] += count
            if sex == 1:
                row[6] += count
            elif sex == 2:
                row[10] += count
            if 21 <= age <= 36:
                row[11] += count
                if sex == 1:
                    row[3] += count
                elif sex == 2:
                    row[7] += count
            elif 39 <= age <= 60:
                row[12] += count
                if sex == 1:
                    row[4] += count
                elif sex == 2:
                    row[8] += count
            elif age > 60:
                row[13] += count
                if sex == 1:
                    row[5] += count
                elif sex == 2:
                    row[9] += count

    def processRecord(self, record):
        MKB = forceString(record.value('MKB'))
        sex = forceInt(record.value('sex'))
        count = forceInt(record.value('count'))
        age = forceInt(record.value('clientAge'))
        stage = forceInt(record.value('stage_id'))
        additionalDiagInfo = forceBool(record.value('diagnosticResultId')) if self.diseaseCharacterCodes == [5] else forceBool(record.value('dispanserCode'))

        MKBfound = False
        for rowInfo in self.resultSet[:-1]: # Итог здесь учитывать не надо
            row, checkStage = rowInfo
            if MKBinString(MKB, row[2]):
                MKBfound = True
                if not checkStage or stage in [1, 2]:
                    self.processRow(row, sex, age, additionalDiagInfo, count)
        if not MKBfound:
            self.processRow(self.resultSet[-2][0], sex, age, additionalDiagInfo, count)
        self.processRow(self.resultSet[-1][0], sex, age, additionalDiagInfo, count)

    def build(self, params):
        self.resultSet = [
            ([u'Некоторые инфекционные и паразитарные болезни', u'1', u'A00-B99', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\tв том числе: туберкулез', u'1.1', u'A15-A19', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'Новообразования', u'2', u'C00-D48', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\tв том числе:\n\tзлокачественные новообразования и новообразования in situ', u'2.1', u'C00-D09', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\tв том числе:\n\tпищевода', u'2.2', u'C15, D00.1', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\t\tиз них в 1-2 стадии', u'2.2.1', u'C15, D00.1', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], True),
            ([u'\tжелудка', u'2.3', u'C16, D00.2', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\t\tиз них в 1-2 стадии', u'2.3.1', u'C16, D00.2', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], True),
            ([u'\tободочной кишки', u'2.4', u'C18, D01.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\t\tиз них в 1-2 стадии', u'2.4.1', u'C18, D01.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], True),
            ([u'\tректосигмоидного соединения, прямой кишки, заднего прохода (ануса) и анального канала', u'2.5', u'C19-C21, D01.1-D01.3', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\t\tиз них в 1-2 стадии', u'2.5.1', u'C19-C21, D01.1-D01.3', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], True),
            ([u'\tподжелудочной железы', u'2.6', u'C25', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\t\tиз них в 1-2 стадии', u'2.6.1', u'C25', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], True),
            ([u'\tтрахеи, бронхов и легкого', u'2.7', u'C33, C34, D02.1-D02.2', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\t\tиз них в 1-2 стадии', u'2.7.1', u'C33-C34, D02.1-D02.2', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], True),
            ([u'\tмолочной железы', u'2.8', u'C50, D05', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\t\tиз них в 1-2 стадии', u'2.8.1', u'C50, D05', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], True),
            ([u'\tшейки матки', u'2.9', u'C53, D06', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\t\tиз них в 1-2 стадии', u'2.9.1', u'C53, D06', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], True),
            ([u'\tтела матки', u'2.10', u'C54', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\t\tиз них в 1-2 стадии', u'2.10.1', u'C54', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], True),
            ([u'\tяичника', u'2.11', u'C56', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\t\tиз них в 1-2 стадии', u'2.11.1', u'C56', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], True),
            ([u'\tпредстательной железы', u'2.12', u'C61, D07.5', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\t\tиз них в 1-2 стадии', u'2.12.1', u'C61, D07.5', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], True),
            ([u'\tпочки (кроме почечной лоханки)', u'2.13', u'C64', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\t\tиз них в 1-2 стадии', u'2.13.1', u'C64', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], True),
            ([u'Болезни крови, кроветворных органов и отдельные нарушения, вовлекающие иммунный механизм', u'3', u'D50-D89', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\tв том числе:\n\tв том числе: анемии, связанные с питанием, гемолитические анемии, апластические и другие анемии', u'3.1', u'D50-D64', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'Болезни эндокринной системы, расстройства питания и нарушения обмена веществ', u'4', u'E00-E90', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\tв том числе:\n\tсахарный диабет', u'4.1', u'E10-E14', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\tожирение', u'4.2', u'E66', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\tнарушения обмена липопротеинов и другие липидемии', u'4.3', u'E78', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'Болезни нервной системы', u'5', u'G00-G99', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\tв том числе:\n\tв том числе: преходящие церебральные ишемические приступы [атаки] и родственные синдромы', u'5.1', u'G45', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'Болезни глаза и его придаточного аппарата', u'6', u'H00-H59', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\tв том числе:\n\tстарческая катаракта и другие катаракты', u'6.1', u'H25, H26', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\tглаукома', u'6.2', u'H40', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\tслепота и пониженное зрение', u'6.3', u'H54', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'Болезни системы кровообращения', u'7', u'I00-I99', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\tв том числе:\n\tболезни, характеризующиеся повышенным кровяным давлением', u'7.1', u'I10-I15', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\tишемическая болезнь сердца', u'7.2', u'I20-I25', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\t\tв том числе:\n\t\tстенокардия (грудная жаба)', u'7.2.1', u'I20', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\t\tв том числе нестабильная стенокардия', u'7.2.2', u'I20.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\t\tхроническая ишемическая болезнь сердца', u'7.2.3', u'I25', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\t\t\tв том числе:\n\t\t\tперенесенный в прошлом инфаркт миокарда', u'7.2.4', u'I25.2', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\tдругие болезни сердца', u'7.3', u'I30-I52', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\tцереброваскулярные болезни', u'7.4', u'I60-I69', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\t\tв том числе:\n\t\tзакупорка и стеноз прецеребральных артерий, не приводящие к инфаркту мозга, и закупорка и стеноз церебральных артерий, не приводящие к инфаркту мозга', u'7.4.1', u'I65, I66', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\t\tдругие цереброваскулярные болезни', u'7.4.2', u'I67', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\t\tпоследствия субарахноидального кровоизлияния, последствия внутричерепного кровоизлияния, последствия другого нетравматического внутричерепного кровоизлияния, последствия инфаркта мозга, последствия инсульта, не уточненные как кровоизлияние или инфаркт мозга', u'7.4.3', u'I69.0-I69.4', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\tаневризма брюшной аорты', u'7.4.4', u'I71.3-I71.4', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'Болезни органов дыхания', u'8', u'J00-J98', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\tв том числе:\n\tвирусная пневмония, пневмония, вызванная Streptococcus pneumonia, пневмония, вызванная Haemophilus influenza, \
            бактериальная пневмония, пневмония, вызванная другими инфекционными возбудителями, пневмония при болезнях, классифицированных \
            в других рубриках, пневмония без уточнения возбудителя', u'8.1', u'J12-J18', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\tбронхит, не уточненный как острый и хронический, простой и слизисто-гнойный хронический бронхит, хронический бронхит неуточненный, эмфизема', u'8.2', u'J40-J43', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\tдругая хроническая обструктивная легочная болезнь, астма, астматический статус, бронхоэктатическая болезнь', u'8.3', u'J44-J47', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'Болезни органов пищеварения', u'9', u'K00-K93', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\tв том числе:\n\tязва желудка, язва двенадцатиперстной кишки', u'9.1', u'K25, K26', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\tгастрит и дуоденит', u'9.2', u'K29', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\tнеинфекционный энтерит и колит', u'9.3', u'K50-K52', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\tдругие болезни кишечника', u'9.4', u'K55-K63', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'Болезни мочеполовой системы', u'10', u'N00-N99', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\tв том числе:\n\tгиперплазия предстательной железы, воспалительные болезни предстательной железы, другие болезни предстательной железы', u'10.1', u'N40-N42', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\tдоброкачественная дисплазия молочной железы', u'10.2', u'N60', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'\tВоспалительные болезни женских тазовых органов', u'10.3', u'N70-N77', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'Прочие заболевания', u'11', u'', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False),
            ([u'ИТОГО', u'12', u'A00-T98', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], False)
        ]


        query = selectData(params, self.diseaseCharacterCodes)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            self.processRecord(query.record())

        # now text
        bf = QtGui.QTextBlockFormat()
        bf.setAlignment(QtCore.Qt.AlignCenter)

        orgId = QtGui.qApp.currentOrgId()
        orgInfo = getOrganisationInfo(orgId)
        if not orgInfo:
            QtGui.qApp.preferences.appPrefs['orgId'] = QtCore.QVariant()
        shortName = getVal(orgInfo, 'shortName', u'не задано')

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(bf)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertText(u'\nЛПУ: ' + shortName)
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ( '40%', [u'Заболевание (подозрение на заболевание)', u''], CReportBase.AlignLeft),
            ( '3%', [u'№ строки', u''], CReportBase.AlignCenter),
            ( '5%', [u'Код по МКБ-10', u''], CReportBase.AlignCenter),
            ( '4%', [u'Мужчины', u'21 - 36 лет'], CReportBase.AlignRight),
            ( '4%', [u'', u'39 - 60 лет'], CReportBase.AlignRight),
            ( '4%', [u'', u'Старше 60 лет'], CReportBase.AlignRight),
            ( '4%', [u'', u'Всего'], CReportBase.AlignRight),
            ( '4%', [u'Женщины', u'21 - 36 лет'], CReportBase.AlignRight),
            ( '4%', [u'', u'39 - 60 лет'], CReportBase.AlignRight),
            ( '4%', [u'', u'Старше 60 лет'], CReportBase.AlignRight),
            ( '4%', [u'', u'Всего'], CReportBase.AlignRight),
            ( '4%', [u'Всего', u'21 - 36 лет'], CReportBase.AlignRight),
            ( '4%', [u'', u'39 - 60 лет'], CReportBase.AlignRight),
            ( '4%', [u'', u'Старше 60 лет'], CReportBase.AlignRight),
            ( '4%', [u'', u'Всего'], CReportBase.AlignRight),
            ( '4%', [u'', u'Из них дано направление на дополнительное исследование, не входящее в объем диспансеризации' if self.diseaseCharacterCodes == [5] else u'Установлено диспансерное наблюдение'], CReportBase.AlignRight),
        ]

        rowSize = len(self.resultSet[0][0])
        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 1, 4)
        table.mergeCells(0, 7, 1, 4)
        table.mergeCells(0, 11, 1, 5)

        i = table.addRow()

        for j in xrange(rowSize):
            table.setText(i, j, j + 1, blockFormat=bf)

        # for z in range(len(self.resultSet)):
        #     row = self.resultSet[z][0]
        #     i = table.addRow()
        #     table.setText(i, 0, row[0], charFormat=(CReportBase.TableBody if row[0].startswith(u'\t') else CReportBase.TableTotal))
        #     table.setText(i, 1, row[1])
        #     if self.resultSet[z][1]:
        #         table.mergeCells(i - 1, 2, 2, 1)
        #     else:
        #         table.setText(i, 2, row[2])
        #     for j in range(3, rowSize):
        #         table.setText(i, j, row[j])

        for resultString in self.resultSet:
            row = resultString[0]
            i = table.addRow()
            table.setText(i, 0, row[0], charFormat=(CReportBase.TableBody if row[0].startswith(u'\t') else CReportBase.TableTotal))
            table.setText(i, 1, row[1])
            if resultString[1]:
                table.mergeCells(i - 1, 2, 2, 1)
            else:
                table.setText(i, 2, row[2])
            for j in range(3, rowSize):
                table.setText(i, j, row[j])

        return doc
