# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils      import forceBool, forceInt, forceRef, forceString, getVal
from Orgs.Utils         import getOrganisationInfo
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.StatReportDD2013Weekly import CReportDD2013WeeklySetupDialog


def selectData(params):
    sex = params.get('sex', 0)
    ageFrom = params.get('ageFrom', 0)
    ageTo = params.get('ageTo', 150)
    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)

    stmt = u'''
        SELECT DISTINCT Client.id as clientId, E.id as eventId, HG.code as hgCode, rbResult.code as resultCode,
                ActionPropertyType.idx, ActionProperty_String.value as aps_value, REK.code AS eventKindCode
        FROM Client
            LEFT JOIN EventType AS ET ON ET.deleted = 0
            LEFT JOIN rbEventKind AS REK ON ET.eventKind_id = REK.id AND REK.code IN ('01', '02', '04')
            LEFT JOIN Event AS E ON E.client_id = Client.id AND E.eventType_id = ET.id AND E.deleted = 0
            LEFT JOIN Diagnostic AS D ON D.event_id = E.id AND D.deleted = 0
            LEFT JOIN rbHealthGroup AS HG ON HG.id = D.healthGroup_id
            LEFT JOIN rbDiagnosisType AS DT ON DT.id = D.diagnosisType_id
            LEFT JOIN rbResult ON rbResult.id = E.result_id
            LEFT JOIN Action ON Action.event_id = E.id AND Action.deleted = 0
            LEFT JOIN ActionType ON Action.actionType_id = ActionType.id AND ActionType.code = 'ДДР' AND ActionType.deleted = 0
            LEFT JOIN ActionPropertyType ON ActionPropertyType.actionType_id = ActionType.id AND ActionPropertyType.deleted = 0
            LEFT JOIN ActionProperty ON ActionProperty.action_id = Action.id AND ActionProperty.type_id = ActionPropertyType.id AND ActionProperty.deleted = 0
            LEFT JOIN ActionProperty_String ON ActionProperty_String.id = ActionProperty.id AND ActionProperty_String.value = 'да'
        WHERE (D.id IS NULL OR DT.code IN ('1', '2')) %s
    '''

    db = QtGui.qApp.db
    tableEvent = db.table('Event').alias('E')
    #tableEventSS = db.table('Event').alias('E2')
    tableClient = db.table('Client')
    cond = []
    if not params.get('countUnfinished', False):
        cond = []
        cond.append(db.joinAnd([tableEvent['setDate'].dateGe(begDate), tableEvent['execDate'].dateLe(endDate)]))
    else:
        cond.append(db.joinAnd([tableEvent['setDate'].dateGe(begDate), tableEvent['setDate'].dateLe(endDate)]))

    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append(u'E.setDate >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)'%ageFrom)
        cond.append(u'E.setDate < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)'%(ageTo+1))
    return db.query(stmt % (u'AND ' + db.joinAnd(cond)) if cond else u'')

def selectExtraData(params):
    sex = params.get('sex', 0)
    ageFrom = params.get('ageFrom', 0)
    ageTo = params.get('ageTo', 150)
    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)

    stmt = u'''
    SELECT
        COUNT(DISTINCT IF(T.hg2_code != '6' AND ActionType.code = '061028', T.client_id, NULL)) as deep_hg2,
        COUNT(DISTINCT IF(T.hg2_code != '6' AND ActionType.code = '061029', T.client_id, NULL)) as group_hg2,
        COUNT(DISTINCT IF(T.hg2_code = '6' AND ActionType.code = '061028', T.client_id, NULL)) as deep_hg3,
        COUNT(DISTINCT IF(T.hg2_code = '6' AND ActionType.code = '061029', T.client_id, NULL)) as group_hg3
    FROM
        (SELECT Client.id as client_id, E1.id AS e1_id, E2.id AS e2_id, HG2.code AS hg2_code
            FROM
                Client
                INNER JOIN Event AS E1 ON E1.client_id = Client.id AND E1.deleted = 0
                INNER JOIN EventType AS ET1 ON E1.eventType_id = ET1.id AND ET1.deleted = 0
                INNER JOIN rbEventKind AS REK1 ON ET1.eventKind_id = REK1.id AND REK1.code IN ('01', '04')

                INNER JOIN Event AS E2 ON E2.client_id = Client.id AND E2.deleted = 0
                INNER JOIN EventType AS ET2 ON E2.eventType_id = ET2.id AND ET2.deleted = 0
                INNER JOIN rbEventKind AS REK2 ON ET2.eventKind_id = REK2.id AND REK2.code = '02'
                INNER JOIN Diagnostic AS D2 ON D2.event_id = E2.id AND D2.deleted = 0
                INNER JOIN rbHealthGroup as HG2 ON HG2.id = D2.healthGroup_id AND HG2.code != '1'
            WHERE %s) AS T
        INNER JOIN Action ON Action.event_id IN (T.e1_id, T.e2_id) and Action.deleted = 0
        INNER JOIN ActionType ON Action.actionType_id = ActionType.id AND ActionType.code IN ('061029', '061028') AND ActionType.deleted = 0
    '''
    db = QtGui.qApp.db
    tableEventFS = db.table('Event').alias('E1')
    tableEventSS = db.table('Event').alias('E2')
    tableClient = db.table('Client')
    cond = []
    cond.append(tableEventFS['setDate'].dateGe(begDate))
    cond.append(tableEventFS['execDate'].dateGe(endDate))
    cond.append(tableEventSS['setDate'].dateGe(begDate))
    cond.append(tableEventSS['execDate'].dateGe(endDate))
    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append(u'E1.setDate >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)'%ageFrom)
        cond.append(u'E1.setDate < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)'%(ageTo+1))
    return db.query(stmt % db.joinAnd(cond))

class CReportDD2013Monthly(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Сведения об объемах производства диспансеризации за месяц')


    def getSetupDialog(self, parent):
        result = CReportDD2013WeeklySetupDialog(parent)
        result.setTitle(self.title())
        result.setPayStatusVisible(False)
        result.setEventTypeVisible(False)
        return result



    def build(self, params):
        rowSize = 49

        query = selectData(params)
        totalFS = set()
        totalSS = set()
        totalFull = set()
        totalHG1 = set()
        totalHG2 = set()
        totalHG3 = set()
        totalChronic = {'total': set(),
                        0: set(),
                        1: set(),
                        2: set(),
                        3: set(),
                        4: set(),
                        5: set(),
                        6: set(),
                        7: set(),
                        8: set(),
                        9: set(),
                        10: set(),
                        11: set(),
                        12: set(),
                        13: set(),
                        14: set(),
                        15: set(),
                        16: set(),
                        17: set(),
                        18: set(),
                        19: set(),
                        20: set(),
                        21: set()}

        totalRisky = {'total': set(),
                      22: set(),
                      23: set(),
                      24: set(),
                      25: set(),
                      26: set(),
                      27: set(),
                      28: set(),
                      29: set(),
                      30: set()}
        alcoholic = {31: set(),
                     32: set()}
        multiRiskClients = {}

        i = 0
        while query.next():
            i += 1
            record = query.record()
            clientId = forceRef(record.value('clientId'))
            eventId = forceRef(record.value('eventId'))
            eventKindCode = forceString(record.value('eventKindCode'))
            hg = forceString(record.value('hgCode'))
            resultCode = forceString(record.value('resultCode'))
            APS_idx = forceString(record.value('idx'))
            APS_value = forceBool(record.value('aps_value'))

            if eventKindCode == '01':
                totalFS.add(clientId)
                if resultCode != '49':
                    totalFull.add(clientId)
                    if hg == '1':
                        totalHG1.add(clientId)
                    elif hg in ['2', '3', '4', '5']:
                        totalHG2.add(clientId)
                    elif hg == '6':
                        totalHG3.add(clientId)
            elif eventKindCode == '02':
                totalSS.add(clientId)
                totalFull.add(clientId)
                if hg == '1':
                    totalHG1.add(clientId)
                elif hg in ['2', '3', '4', '5']:
                    totalHG2.add(clientId)
                elif hg == '6':
                    totalHG3.add(clientId)

            if APS_idx != '' and APS_value:
                idx = forceInt(APS_idx)
                if idx <= 21:
                    totalChronic['total'].add(clientId)
                    totalChronic[idx].add(clientId)
                elif idx > 21 and idx <= 30:
                    totalRisky['total'].add(clientId)
                    totalRisky[idx].add(clientId)
                    if clientId in multiRiskClients:
                        multiRiskClients[clientId].add(idx)
                    else:
                        multiRiskClients[clientId] = set([idx])
                elif idx > 30:
                    alcoholic[idx].add(clientId)

        multiRiskTotal = 0
        for i in multiRiskClients:
            if len(multiRiskClients[i]) > 1:
                multiRiskTotal += 1
        query = selectExtraData(params)
        query.first()
        record = query.record()

        tc = totalChronic
        reportRow = [u'', u'', len(totalFS), len(totalSS), len(totalFull), len(totalHG1), len(totalHG2), len(totalHG3)]
        # Порядок свойств у нас в одном месте отличается от оного в отчете, поэтому следующая строчка столь пугающая
        reportRow += [len(totalChronic['total'])] + [len(tc[0]), len(tc[1]), len(tc[2]), len(tc[4]), len(tc[3])] + [len(totalChronic[i]) for i in range(5, 22)]
        reportRow += [len(totalRisky['total'])] + [len(totalRisky[i]) for i in range(22, 31)]
        reportRow += [multiRiskTotal, len(alcoholic[31]), len(alcoholic[32])]
        reportRow += [forceInt(record.value('deep_hg2')), forceInt(record.value('group_hg2'))]
        reportRow += [forceInt(record.value('deep_hg3')), forceInt(record.value('group_hg3'))]
        reportRow += [u'']

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
            ( '2%', [u'Численность взрослого населения района', u''], CReportBase.AlignRight),
            ( '2%', [u'Общее количество гражден, подлежаших диспансеризации в текущем году', u'1.'], CReportBase.AlignRight),
            ( '2%', [u'Количество граждан, прошедших 1-й этап диспансеризации за отчетный период', u'2.'], CReportBase.AlignRight),
            ( '2%', [u'Количество граждан, прошедших 2-й этап диспансеризации за отчетный период', u'3.'], CReportBase.AlignRight),
            ( '2%', [u'Количество граждан, полностью завершивших диспансеризацию за отчетный период, в том числе:', u'4.'], CReportBase.AlignRight),
            ( '2%', [u'- имеют 1-ю группу здоровья', u'4.1'], CReportBase.AlignRight),
            ( '2%', [u'- имеют 2-ю группу здоровья', u'4.2'], CReportBase.AlignRight),
            ( '2%', [u'- имеют 3-ю группу здоровья', u'4.3'], CReportBase.AlignRight),
            ( '2%', [u'Количество граждан с впервые выявленными хроническими инфекционными заболеваниями, из них:', u'5.'], CReportBase.AlignRight),
            ( '2%', [u'- со стенокардией', u'5.1'], CReportBase.AlignRight),
            ( '2%', [u'- с хронической ишемической болезнью сердца', u'5.2'], CReportBase.AlignRight),
            ( '2%', [u'- с артериальной гипертонией', u'5.3'], CReportBase.AlignRight),
            ( '2%', [u'- со стенозом сонных артерий >50%', u'5.4'], CReportBase.AlignRight),
            ( '2%', [u'- с острым нарушением мозгового кровообращения в анамнезе', u'5.5'], CReportBase.AlignRight),
            ( '2%', [u'- с подозрением на злокачественное новообразование желудка по результатам фиброгастроскопии, из них', u'5.6'], CReportBase.AlignRight),
            ( '2%', [u'на ранней стадии', u'5.7'], CReportBase.AlignRight),
            ( '2%', [u'- с подозрением на злокачественное образование матки и ее придатков', u'5.8'], CReportBase.AlignRight),
            ( '2%', [u'на ранней стадии', u'5.9'], CReportBase.AlignRight),
            ( '2%', [u'- с подозрением на злокачественное новообразование простаты по данным осмотра врача-хирурга (уролога) и теста на простатспецифический антиген, из них', u'5.10'], CReportBase.AlignRight),
            ( '2%', [u'на ранней стадии', u'5.11'], CReportBase.AlignRight),
            ( '2%', [u'- с подозрением на злокачественное новообразование грудной железы по данным маммографии, из них', u'5.12'], CReportBase.AlignRight),
            ( '2%', [u'на ранней стадии', u'5.13'], CReportBase.AlignRight),
            ( '2%', [u'- с подозрением на колоректальный рак по данным ректоромано- и колоноскопии, из них', u'5.14'], CReportBase.AlignRight),
            ( '2%', [u'на ранней стадии', u'5.15'], CReportBase.AlignRight),
            ( '2%', [u'- с подозрением на злокачественные заболевания других локализаций, из них', u'5.16'], CReportBase.AlignRight),
            ( '2%', [u'на ранней стадии', u'5.17'], CReportBase.AlignRight),
            ( '2%', [u'- с сахарным диабетом', u'5.18'], CReportBase.AlignRight),
            ( '2%', [u'Количество граждан с впервые выявленным туберкулезом легких', u'6.'], CReportBase.AlignRight),
            ( '2%', [u'Количество граждан с впервые выявленной глаукомой', u'7.'], CReportBase.AlignRight),
            ( '2%', [u'на ранней стадии', u''], CReportBase.AlignRight),
            ( '2%', [u'Количество граждан с впервые выявленными заболеваниями других органов и систем', u'8.'], CReportBase.AlignRight),
            ( '2%', [u'Количество граждан, имеющих факторы риска хронических неинфекционных заболеваний, из них:', u'9.'], CReportBase.AlignRight),
            ( '2%', [u'- потребляют табак (курение)', u'9.1'], CReportBase.AlignRight),
            ( '2%', [u'- повышенное АД', u'9.2'], CReportBase.AlignRight),
            ( '2%', [u'- избыточная масса тела', u'9.3'], CReportBase.AlignRight),
            ( '2%', [u'- ожирение', u'9.4'], CReportBase.AlignRight),
            ( '2%', [u'- гиперхолистеринемия, дислипидемия', u'9.5'], CReportBase.AlignRight),
            ( '2%', [u'- гипергликемия', u'9.6'], CReportBase.AlignRight),
            ( '2%', [u'- недостаточная физическая активность', u'9.7'], CReportBase.AlignRight),
            ( '2%', [u'- нерациональное питание', u'9.8'], CReportBase.AlignRight),
            ( '2%', [u'- подозрение на пагубное потребление алкоголя', u'9.9'], CReportBase.AlignRight),
            ( '2%', [u'- имеющие 2 фактора риска и более', u'9.10'], CReportBase.AlignRight),
            ( '2%', [u'Количество граждан с подозрением на зависимость от алкоголя, наркотиков и психотропных средств, из них', u'10.'], CReportBase.AlignRight),
            ( '2%', [u'число граждан, направленных к психиатру-наркологу', u'11.'], CReportBase.AlignRight),
            ( '2%', [u'Количество граждан 2-й группы здоровья, прошедших углубленное профилактическое консультирование', u'12.'], CReportBase.AlignRight),
            ( '2%', [u'Количество граждан 2-й группы здоровья, прошедших групповое профилактическое консультирование', u'13.'], CReportBase.AlignRight),
            ( '2%', [u'Количество граждан 3-й группы здоровья, прошедших углубленное профилактическое консультирование', u'14.'], CReportBase.AlignRight),
            ( '2%', [u'Количество граждан 3-й группы здоровья, прошедших групповое профилактическое консультирование', u'15.'], CReportBase.AlignRight),
            ( '2%', [u'Численность прикрепленного взрослого контингента', u''], CReportBase.AlignRight)
        ]

        table = createTable(cursor, tableColumns)

        i = table.addRow()
        for j in xrange(rowSize):
            table.setText(i, j, reportRow[j])
        return doc

