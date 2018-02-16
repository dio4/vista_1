# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from library.database               import addDateInRange
from library.Utils                  import forceInt, forceString, getVal
from Orgs.Utils                     import getOrganisationInfo
from Reports.Report                 import CReport
from Reports.ReportBase             import createTable, CReportBase
from Reports.StatReportDD2013Weekly import CReportDD2013WeeklySetupDialog


def selectData(params):
    sex = params.get('sex', 0)
    ageFrom = params.get('ageFrom', 0)
    ageTo = params.get('ageTo', 150)
    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)
    eventTypeId  = params.get('eventTypeId', None)

    db = QtGui.qApp.db
    tableClient = db.table('Client')
    tableEvent = db.table('Event')
    tableEventType = db.table('EventType')
    tableEventKind = db.table('rbEventKind')
    tableAction = db.table('Action')
    tableActionType = db.table('ActionType')
    tableActionPropertyType = db.table('ActionPropertyType')
    tableActionProperty = db.table('ActionProperty')
    tableAPS = db.table('ActionProperty_String')
    tableDiagnostic = db.table('Diagnostic')
    tableDiagnosis = db.table('Diagnosis')
    tableRBDR = db.table('rbDiagnosticResult')
    tableDispanser = db.table('rbDispanser')
    tablePerson = db.table('Person')
    tableOrgStructure = db.table('OrgStructure')

    queryTable = tableClient.innerJoin(tableEventType, db.joinAnd([tableEventType['deleted'].eq(0), tableClient['deleted'].eq(0)]))
    queryTable = queryTable.innerJoin(tableEventKind, db.joinAnd([tableEventType['eventKind_id'].eq(tableEventKind['id']), tableEventKind['code'].inlist(['01', '02'])]))
    queryTable = queryTable.innerJoin(tableEvent, db.joinAnd([tableEvent['eventType_id'].eq(tableEventType['id']), tableEvent['deleted'].eq(0), tableEvent['client_id'].eq(tableClient['id'])]))
    queryTable = queryTable.leftJoin(tableActionType, db.joinAnd([tableActionType['code'].eq(u'др'), tableActionType['deleted'].eq(0)]))
    queryTable = queryTable.leftJoin(tableAction, db.joinAnd([tableAction['event_id'].eq(tableEvent['id']), tableAction['actionType_id'].eq(tableActionType['id']), tableAction['deleted'].eq(0)]))
    queryTable = queryTable.leftJoin(tableActionProperty, db.joinAnd([tableActionProperty['action_id'].eq(tableAction['id']), tableActionProperty['deleted'].eq(0)]))
    queryTable = queryTable.leftJoin(tableActionPropertyType, db.joinAnd([tableActionPropertyType['id'].eq(tableActionProperty['type_id']), tableActionPropertyType['deleted'].eq(0), tableActionPropertyType['actionType_id'].eq(tableActionType['id'])]))
    queryTable = queryTable.leftJoin(tableAPS, tableAPS['id'].eq(tableActionProperty['id']))
    queryTable = queryTable.leftJoin(tableDiagnostic, db.joinAnd([tableDiagnostic['event_id'].eq(tableEvent['id']), tableDiagnostic['deleted'].eq(0)]))
    queryTable = queryTable.leftJoin(tableDiagnosis, db.joinAnd([tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']), tableDiagnosis['deleted'].eq(0)]))
    queryTable = queryTable.leftJoin(tableRBDR, tableDiagnostic['result_id'].eq(tableRBDR['id']))
    queryTable = queryTable.leftJoin(tableDispanser, [tableDispanser['id'].eq(tableDiagnosis['dispanser_id']), tableDispanser['code'].inlist(['2', '6'])])
    queryTable = queryTable.leftJoin(tablePerson, tablePerson['id'].eq(tableDiagnosis['person_id']))
    queryTable = queryTable.leftJoin(tableOrgStructure, tableOrgStructure['id'].eq(tablePerson['orgStructure_id']))

    cols = [
        tableClient['id'].alias('client_id'),
        tableClient['sex'],
        'age(Client.birthDate, Event.setDate) as clientAge',
        tableActionPropertyType['idx'],
        tableAPS['value'].alias('APS_value'),
        tableRBDR['code'].alias('resultCode'),
        u'IF(rbDispanser.id IS NOT NULL, IF(OrgStructure.name LIKE \'%%профилактик%%\', 1, IF(OrgStructure.name = \'Центр здоровья\', 2, 0)), 0) AS cab'
    ]
    columnsForSelect = [
        't.sex',
        't.clientAge',
        't.idx',
        't.APS_value',
        't.MKB',
        'resultCode',
        'COUNT(DISTINCT t.client_id) as cnt',
        't.cab',
    ]

    group = [
        't.sex',
        't.clientAge',
        't.idx',
        't.APS_value',
        't.MKB',
        't.resultCode',
        't.cab'
    ]

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
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))

    # Добавление этого условия может ускорить работу запроса. А может и не ускорить.
    # cond.append(db.joinOr([
    #     tableDiagnosis['MKB'].isNull(),
    #     tableDiagnosis['MKB'].inlist(CReportDD2015RiskFactors.mapMKBToRow.keys()),
    #     tableActionPropertyType['idx'].inlist(CReportDD2015RiskFactors.mapIdxToRow.keys()),
    #     tableActionPropertyType['idx'].inlist([15, 16])
    # ])) # u'Diagnosis.MKB in (R03.0, R73.9, R63.5, Z72.0, Z72.1, Z72.2, Z72.3, Z72.4, Z80, Z82.3, Z82.5, Z83.3)')

    queryForDiagMKB = db.selectStmt(queryTable, cols + [tableDiagnosis['MKB']], cond)
    queryForActionMKB = db.selectStmt(queryTable, cols + [tableAction['MKB']], cond + [tableAction['MKB'].ne('')])
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


class CReportDD2017RiskFactors(CReport):

    mapIdxToRow = {
        9: 0,
        7: 1,
        10: 3,
        11: 6,
        12: 7,
        13: 4,
        14: 5,
        3: 2
    }

    mapMKBToRow = {
        u'R03.0': 0,
        u'R73.9': 1,
        u'R63.5': 2,
        u'Z72.0': 3,
        u'Z72.1': 4,
        u'Z72.2': 5,
        u'Z72.3': 6,
        u'Z72.4': 7,
        u'Z80': 8, u'Z82.3': 8, u'Z82.4': 8, u'Z82.5': 8, u'Z83.3': 8
    }

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Сведения о выявленных отдельных факторах риска развития хронических неинфекционных заболеваний, не являющихся заболеваниями, в соответствии с кодами МКБ-10')
        self.resultSet = []
        self.count4002_1 = 0
        self.count4002_2 = 0

    def getSetupDialog(self, parent):
        result = CReportDD2013WeeklySetupDialog(parent)
        result.setTitle(self.title())
        result.setPayStatusVisible(False)
        return result

    def getRow(self, MKB, idx, apsValue):
        if MKB in self.mapMKBToRow:
            return self.mapMKBToRow[MKB]
        if idx in self.mapIdxToRow and apsValue == u'да':
            return self.mapIdxToRow[idx]
        if idx == 16 and len(apsValue) > 0:
            return 8        # Отягощенная наследственность по хроническим неинфекционным заболеваниям
        if idx == 15:
            if apsValue == u'высокий':
                return 12
            if apsValue == u'очень высокий':
                return 13
        return None

    def processRecord(self, record):
        idx = forceInt(record.value('idx'))
        apsValue = forceString(record.value('APS_value')).lower()
        age = forceInt(record.value('clientAge'))
        cnt = forceInt(record.value('cnt'))
        sex = forceInt(record.value('sex'))
        MKB = forceString(record.value('MKB'))
        resultCode = forceString(record.value('resultCode'))  # 07 -- Направлен на консультацию
        cab = forceInt(record.value('cab'))
        if MKB == u'Z72.1' and resultCode == '07':
            self.count4002_1 += cnt
        if MKB == u'Z72.2' and resultCode == '07':
            self.count4002_2 += cnt
        if cab == 1:
            self.count4001_1 += cnt
        elif cab == 2:
            self.count4001_2 += cnt

        rowNum = self.getRow(MKB, idx, apsValue)
        if rowNum is None:
            return

        # TODO: подумать, как писать такие штуки менее безумно. Возможно, квадродеревья?
        row = self.resultSet[rowNum]
        if 21 <= age <= 36 or 39 <= age:
            row[14] += cnt
            if sex == 1:
                row[6] += cnt
            if sex == 2:
                row[10] += cnt
            if 21 <= age <= 36:
                row[11] += cnt
                if sex == 1:
                    row[3] += cnt
                elif sex == 2:
                    row[7] += cnt
            elif 39 <= age <= 60:
                row[12] += cnt
                if sex == 1:
                    row[4] += cnt
                elif sex == 2:
                    row[8] += cnt
            elif age > 60:
                row[13] += cnt
                if sex == 1:
                    row[5] += cnt
                elif sex == 2:
                    row[9] += cnt

    def build(self, params):
        self.count4002_1 = 0
        self.count4002_2 = 0
        self.count4001_1 = 0
        self.count4001_2 = 0
        self.resultSet = [
            [u'Повышенный уровень артериального давления (Повышенное кровяное давление при отсутствии диагноза гипертензии)', u'01', u'R03.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'Гипергликемия неуточненная (Повышенное содержание глюкозы в крови)', u'02', u'R73.9', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'Избыточная масса тела (Анормальная прибавка массы тела)', u'03', u'R63.5', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'Курение табака (Употребление табака)', u'04', u'Z72.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'Риск пагубного потребления алкоголя (Употребление алкоголя)', u'05', u'Z72.1', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'Риск потребления наркотических средств и психотропных веществ без назначения врача (Употребление наркотиков)', u'06', u'Z72.2', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'Низкая физическая активность (Недостаток физической активности)', u'07', u'Z72.3', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'Нерациональное питание (Неприемлемая диета и вредные привычки питания)', u'08', u'Z72.4', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'Отягощенная наследственность по злокачественным новообразованиям (в семейном анамнезе злокачественное новообразование)', u'09', u'Z80', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'отягощенная наследственность по сердечно-сосудистым заболеваниям (в семейном анамнезе инсульт, в семейном анамнезе ишемическая болезнь сердца и другие болезни сердечно-сосудистой системы)', u'', u'Z82.3, Z82.4', '', '', '', '', '', '', '', '', '', 0, '', ''],
            [u'отягощенная наследственность по хроническим болезням нижних дыхательных путей (в семейном анамнезе астма и другие хронические болезни нижних дыхательных путей),', u'', u'Z82.5', '', '', '', '', '', '', '', '', '', 0, '', ''],
            [u'отягощенная наследственность по сахарному диабету (в семейном анамнезе сахарный диабет).', u'', u'Z83.3', '', '', '', '', '', '', '', '', '', 0, '', ''],
            [u'Высокий абсолютный суммарный сердечно-сосудистый риск', u'10', u'', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'Очень высокий абсолютный суммарный сердечно-сосудистый риск', u'11', u'', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]

        query = selectData(params)
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
            ('20%', [u'Факторы риска (наименование по МКБ-10)', u''], CReportBase.AlignCenter),
            ('4%', [u'№ строки', u''], CReportBase.AlignCenter),
            ('5%', [u'Код МКБ-10', u''], CReportBase.AlignCenter),
            ('5.9%', [u'Мужчины', u'21 - 36 лет'], CReportBase.AlignRight),
            ('5.9%', [u'', u'39 - 60 лет'], CReportBase.AlignRight),
            ('5.9%', [u'', u'Старше 60 лет'], CReportBase.AlignRight),
            ('5.9%', [u'', u'Всего'], CReportBase.AlignRight),
            ('5.9%', [u'Женщины', u'21 - 36 лет'], CReportBase.AlignRight),
            ('5.9%', [u'', u'39 - 60 лет'], CReportBase.AlignRight),
            ('5.9%', [u'', u'Старше 60 лет'], CReportBase.AlignRight),
            ('5.9%', [u'', u'Всего'], CReportBase.AlignRight),
            ('5.9%', [u'Всего', u'21 - 36 лет'], CReportBase.AlignRight),
            ('5.9%', [u'', u'39 - 60 лет'], CReportBase.AlignRight),
            ('5.9%', [u'', u'Старше 60 лет'], CReportBase.AlignRight),
            ('5.9%', [u'', u'Всего'], CReportBase.AlignRight),
        ]

        cursor.movePosition(cursor.End)
        cursor.insertText(u'4000')

        rowSize = len(tableColumns)
        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 1, 4)
        table.mergeCells(0, 7, 1, 4)
        table.mergeCells(0, 11, 1, 4)

        i = table.addRow()

        for j in xrange(rowSize):
            table.setText(i, j, j + 1, blockFormat=bf)

        for resultRow in self.resultSet:
            i = table.addRow()
            for j in xrange(rowSize):
                table.setText(i, j, resultRow[j])

        for c in [1] + range(3, 12) + [13, 14]:
            table.mergeCells(11, c, 4, 1)

        cursor.movePosition(cursor.End)
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertBlock()
        ps4001 = u'4001 Установлено диспансерное наблюдение врачом (фельдшером): кабинета или отделения медицинской профилактики: %s чел.; ' \
                 u'центра здоровья: %s чел.'
        ps4002 = u'4002 Направлено к врачу-психиатру (врачу-психиатру-наркологу) в связи с выявленным риском пагубного потребления алкоголя: %s человек; ' \
                 u'в связи с выявленным риском потребления наркотических средств и психотропных веществ без назначения врача: %s человек.'
        cursor.insertText(ps4001 % (self.count4001_1, self.count4001_2))
        cursor.insertBlock()
        cursor.insertText(ps4002 % (self.count4002_1, self.count4002_2))

        return doc
