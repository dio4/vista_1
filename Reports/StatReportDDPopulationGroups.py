# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

from Orgs.Utils import getOrganisationInfo
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.StatReportDD2013Weekly import CReportDD2013WeeklySetupDialog
from library.Utils import forceInt, forceString, getVal
from library.database import addDateInRange

DDREPORT_2013 = 0
DDREPORT_2015 = 1
DDREPORT_2017 = 2

def selectData(params, actionTypes, stage = 1, version = DDREPORT_2013):
    sex = params.get('sex', 0)
    ageFrom = params.get('ageFrom', 0)
    ageTo = params.get('ageTo', 150)
    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)
    payStatusCode = params.get('payStatusCode', None)
    eventTypeId  = params.get('eventTypeId', None)
    socStatusClassId = params.get('socStatusClassId', None)
    socStatusTypeId  = params.get('socStatusTypeId', None)

    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    tableEventType = db.table('EventType')
    tableEventKind = db.table('rbEventKind')
    tableAction = db.table('Action')
    tableActionPropertyType = db.table('ActionPropertyType')
    tableActionType = db.table('ActionType')
    tableClient = db.table('Client')

    cond = []

    addDateInRange(cond, tableEvent['execDate'] if not params.get('countUnfinished', False) else tableEvent['setDate'], begDate, endDate)
    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append(u'Event.setDate >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)' % ageFrom)
        cond.append(u'Event.setDate < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)' % (ageTo + 1))

    if payStatusCode is not None:
        tableContract = db.table('Contract')
        cond.append('getPayCode(IF(%s, %s, %s), %s) = %d' % (tableAction['finance_id'],
                                                             tableAction['finance_id'],
                                                             tableContract['finance_id'],
                                                             tableAction['payStatus'],
                                                             payStatusCode))
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if stage == 2:
        # cond.append(tableAction['status'].ne('3'))
        cond.append(tableAction['status'].ne('6'))

    if socStatusTypeId:
        subStatusTypeStmt = ('SELECT ClientSocStatus.id FROM ClientSocStatus WHERE '
                            +'ClientSocStatus.deleted=0 AND ClientSocStatus.client_id=Client.id AND '
                            +'ClientSocStatus.socStatusType_id=%d' % socStatusTypeId)
        cond.append('EXISTS(' + subStatusTypeStmt + ')')
    elif socStatusClassId:
        subStatusClassStmt = ('SELECT ClientSocStatus.id FROM ClientSocStatus WHERE '
                             +'ClientSocStatus.deleted=0 AND ClientSocStatus.client_id=Client.id AND '
                             +'ClientSocStatus.socStatusClass_id=%d' % socStatusClassId)
        cond.append('EXISTS(' + subStatusClassStmt + ')')

    if version == DDREPORT_2015 or version == DDREPORT_2017:
        isLeningrade = QtGui.qApp.region() == '78'
        conditions = {
            'flatCode': ', '.join(["'%s'" % forceString(code) for code in actionTypes]),
            'cond': db.joinAnd(cond),
            'code':'0%s' % stage,
            'firstStepDDEventCond': tableEventKind['code'].eq('01'),
            'secondStepDDEventCond': tableEventKind['code'].eq('02'),
            'actionTypeCode': 'ActionType.flatCode' if isLeningrade else 'ActionType.code',
            'actionTypeDD1Cond': tableActionType['code'].inlist([u'ДДР', u'Осмотр ДД']),
            'actionPropertyTypeIdentifiedCond': tableActionPropertyType['name'].inlist([u'Выявлено показание к исследованию', u'(Не) направлен на II этап'])
        }
        if isLeningrade:
            stmt = u'''
SELECT dd_second.countClients,
          dd_second.countEvents,
          dd_second.countFinished,
          dd_second.countOld,
          dd_second.countCanceled,
          dd_first.countIdentified,
          %(actionTypeCode)s AS ddcode
 FROM ActionType
    LEFT JOIN (
        SELECT
            COUNT(DISTINCT Event.client_id) as countClients,
            COUNT(DISTINCT IF(Action.MKB != '', Event.id, NULL)) as countEvents,
            %(actionTypeCode)s AS ddcode,
            COUNT(DISTINCT IF(Action.status = 2 AND Action.endDate >= Event.setDate, Action.id, NULL)) AS countFinished,
            COUNT(DISTINCT IF(Action.endDate < Event.setDate, Action.id, NULL)) as countOld,
            COUNT(DISTINCT IF(Action.status = 3, Action.id, NULL)) AS countCanceled
        FROM Event
            INNER JOIN EventType ON (Event.`deleted` = 0) AND (EventType.`id` = Event.`eventType_id`) AND (EventType.`deleted` = 0)
            LEFT JOIN rbEventKind ON (EventType.eventKind_id = rbEventKind.id) AND (%(secondStepDDEventCond)s)
            LEFT JOIN ActionType ON (ActionType.`deleted` = 0) AND (%(actionTypeCode)s IN (%(flatCode)s))
            LEFT JOIN Action ON (Action.`deleted` = 0) AND (Action.`event_id` = Event.`id`) AND (Action.`actionType_id` = ActionType.`id`)
            INNER JOIN Client ON (Client.`deleted` = 0) AND (Client.`id` = Event.`client_id`)
        WHERE %(cond)s
        GROUP BY ddcode
    ) dd_second ON %(actionTypeCode)s = dd_second.ddcode
    LEFT JOIN (
        SELECT COUNT(rbThesaurus.id) AS countIdentified,
              rbThesaurus.code AS ddcode
        FROM Event AS Event
        INNER JOIN EventType ON EventType.`id` = Event.`eventType_id` AND Event.deleted = 0
        LEFT JOIN rbEventKind ON (EventType.eventKind_id = rbEventKind.id) AND (%(firstStepDDEventCond)s)
        LEFT JOIN Action ON (Action.`event_id` = Event.`id`) AND (Action.`deleted` = 0)
        LEFT JOIN ActionType ON (ActionType.`id` = Action.`actionType_id`) AND (%(actionTypeDD1Cond)s)
        LEFT JOIN ActionPropertyType ON (ActionPropertyType.`actionType_id` = ActionType.`id`) AND (%(actionPropertyTypeIdentifiedCond)s)
        LEFT JOIN ActionProperty ON (ActionProperty.`action_id` = Action.`id`) AND (ActionProperty.`type_id` = ActionPropertyType.`id`) AND (ActionProperty.`deleted` = 0)
        LEFT JOIN ActionProperty_String ON ActionProperty_String.`id` = ActionProperty.`id`
        LEFT JOIN rbThesaurus ON INSTR(ActionProperty_String.value, rbThesaurus.name) > 0 AND rbThesaurus.code IN (%(flatCode)s)
        INNER JOIN Client ON Client.`id` = Event.`client_id`
    WHERE %(cond)s
    GROUP BY ddcode
    ) dd_first ON dd_first.ddcode = %(actionTypeCode)s
 WHERE %(actionTypeCode)s IN (%(flatCode)s)
 GROUP BY %(actionTypeCode)s''' % conditions
        else:
            createViewStatement = u'''
DROP TEMPORARY TABLE IF EXISTS tempActionsVisits;
CREATE TEMPORARY TABLE tempActionsVisits (INDEX(code), INDEX(event_id), INDEX(act_id))
(SELECT ActionType.code
     , Action.event_id
     , Action.endDate AS date
     , Action.MKB
     , Action.status
     , Action.id AS act_id
FROM Action
INNER JOIN ActionType ON (Action.`deleted` = 0) AND Action.actionType_id = ActionType.id AND ActionType.code IN (%(flatCode)s)
LEFT JOIN Event ON (Event.`deleted` = 0) AND Action.event_id = Event.id
LEFT JOIN EventType ON Event.eventType_id = EventType.id
LEFT JOIN rbEventKind ON EventType.eventKind_id = rbEventKind.id AND rbEventKind.code = '%(code)s'
INNER JOIN Client ON Event.client_id = Client.id
WHERE %(cond)s
  ) UNION ALL (
SELECT rbService.code
  , Visit.event_id
  , Visit.`date`
  , Visit.MKB
  , 2 AS status
  , Visit.id AS act_id
FROM Visit
INNER JOIN rbService ON Visit.service_id = rbService.id AND rbService.code IN (%(flatCode)s)
LEFT JOIN Event ON (Event.`deleted` = 0) AND Visit.event_id = Event.id
LEFT JOIN EventType ON Event.eventType_id = EventType.id
LEFT JOIN rbEventKind ON EventType.eventKind_id = rbEventKind.id AND rbEventKind.code = '%(code)s'
INNER JOIN Client ON Event.client_id = Client.id
LEFT JOIN Action ON (Action.`deleted` = 0) AND Action.event_id = Event.id
WHERE %(cond)s);''' % conditions

            db.query(createViewStatement)
            stmt = u'''
SELECT count(DISTINCT Event.client_id) AS countClients
     , count(DISTINCT if(t.MKB != '', t.event_id, NULL)) AS countEvents
     , t.code AS ddcode
     , count(DISTINCT if(t.status = 2 AND t.date >= Event.setDate, t.act_id, NULL)) AS countFinished
     , count(DISTINCT if(t.date < Event.setDate, t.act_id, NULL)) AS countOld
     , count(DISTINCT if(t.status = 3, t.act_id, NULL)) AS countCanceled
     , count(DISTINCT IF(ActionPropertyType.id IS NULL, NULL, Action.id)) AS countIdentified
FROM
    tempActionsVisits t
    INNER JOIN Event ON (Event.`deleted` = 0) AND t.event_id = Event.id
    LEFT JOIN EventType ON (EventType.`id` = Event.`eventType_id`) AND (EventType.`deleted` = 0)
    LEFT JOIN rbEventKind ON (rbEventKind.`code` = '%(code)s') AND (EventType.eventKind_id = rbEventKind.id)
    INNER JOIN Client ON (Client.`deleted` = 0) AND (Client.`id` = Event.`client_id`)
    LEFT JOIN Action ON (Action.`deleted` = 0) AND Event.id = Action.event_id AND Action.id = t.act_id
    LEFT JOIN ActionType ON Action.actionType_id = ActionType.id
    LEFT JOIN ActionPropertyType  ON (ActionPropertyType.`actionType_id` = ActionType.`id`) AND (%(actionPropertyTypeIdentifiedCond)s)
    LEFT JOIN ActionProperty ON (ActionProperty.`action_id` = Action.`id`) AND (ActionProperty.`type_id` = ActionPropertyType.`id`) AND (ActionProperty.`deleted` = 0)
WHERE %(cond)s
GROUP BY t.code
''' % conditions
    else:
        eventKindCodes = ['01', '04'] if stage == 1 else ['02']

        queryTable = tableEvent.innerJoin(tableEventType, db.joinAnd([tableEvent['deleted'].eq(0), tableEventType['id'].eq(tableEvent['eventType_id']), tableEventType['deleted'].eq(0)]))
        queryTable = queryTable.innerJoin(tableEventKind, db.joinAnd([tableEventType['eventKind_id'].eq(tableEventKind['id']), tableEventKind['code'].inlist(eventKindCodes)]))
        queryTable = queryTable.innerJoin(tableActionType, db.joinAnd([tableActionType['deleted'].eq(0), tableActionType['flatCode'].inlist(actionTypes)]))
        queryTable = queryTable.innerJoin(tableAction, db.joinAnd([tableAction['deleted'].eq(0), tableAction['status'].ne(3) if DDREPORT_2013 else '1', tableAction['event_id'].eq(tableEvent['id']), tableAction['actionType_id'].eq(tableActionType['id'])]))
        queryTable = queryTable.innerJoin(tableClient, db.joinAnd([tableClient['deleted'].eq(0), tableClient['id'].eq(tableEvent['client_id'])]))
        cols = ['COUNT(DISTINCT Event.client_id) as countClients',
                'COUNT(DISTINCT IF(Action.MKB != "", Event.id, NULL)) as countEvents',
                tableActionType['flatCode']]

        group = [tableActionType['flatCode']]

        stmt = db.selectStmt(queryTable, cols, cond, group=group)
    return db.query(stmt)


class CReportDDPopulationGroups(CReport):
    def __init__(self, parent, stage = 1):
        CReport.__init__(self, parent)
        self.stage = stage
        self.setPayPeriodVisible(False)
        if stage == 1:
            self.setTitle(u'Сведения о первом этапе диспансеризации определенных групп взрослого населения (далее - диспансеризация)')
        else:
            self.setTitle(u'Сведения о втором этапе диспансеризации определенных групп взрослого населения')



    def getSetupDialog(self, parent):
        result = CReportDD2013WeeklySetupDialog(parent)
        result.setSocStatusVisible(True)
        result.setTitle(self.title())
        return result

    def processRow(self, row, sex, age, count):
        if 21  <= age <= 36:
            row[9] += count
            if sex:
                row[sex*3] += count
        elif 39 <= age <= 60:
            row[10] += count
            if sex:
                row[sex*3 + 1] += count
        elif age > 60:
            row[11] += count
            if sex:
                row[sex*3 + 2] += count

    def processRecord(self, record):
        if self.stage == 1:
            clients = 2
            events = 3
        else:
            clients = 3
            events = 4

        countClients = forceInt(record.value('countClients'))
        countEvents = forceInt(record.value('countEvents'))
        code = forceString(record.value('ddcode'))

        if code in self.mapActionTypeRow:
            i = self.mapActionTypeRow[code]
            self.resultSet[i][clients] += countClients
            self.resultSet[i][events] += countEvents

        if code in self.extraMaps:
            for i in self.extraMaps[code]:
                self.resultSet[i][clients] += countClients
                self.resultSet[i][events] += countEvents

        self.resultSet[-1][clients] += countClients
        self.resultSet[-1][events] += countEvents

    def makeFSResultSet(self):
        self.resultSet = [[u'Приём (осмотр, консультация) фельдшера отделения (кабинета) медицинской профилактики', u'01', 0, 0], # 0
                          [u'Опрос (анкетирование), направленный на выявление хронических неинфекционных заболевания, факторов риска их развития, потребления наркотических средств и психотропных веществ без назначения врача', u'02', 0, 0], # 1
                          [u'Антропометрия (измерение роста стоя, массы тела, окружности талии), расчет индекса массы тела', u'03', 0, 0], # 2
                          [u'Измерение артериального давления', u'04', 0, 0], # 3
                          [u'Определение уровня общего холестерина в крови', u'06', 0, 0], # 4
                          [u'Определение уровня глюкозы в крови', u'07', 0, 0], # 5
                          [u'Определение суммарного сердечно-сосудистого риска', u'08', 0, 0], # 6
                          [u'Электрокардиография в покое', u'09', 0, 0], # 7
                          [u'Осмотр фельдшера (акушерки)(для женщин)', u'10', 0, 0], # 8
                          [u'Взятие мазка с шейки матки на цитологическое исследование (для женщин)', u'11', 0, 0], # 9
                          [u'Флюорография легких', u'12', 0, 0], # 10
                          [u'Маммография (для женщин)', u'13', 0, 0], # 11
                          [u'Клинический анализ крови', u'14', 0, 0], # 12
                          [u'Клинический анализ крови развернутый', u'15', 0, 0], # 13
                          [u'Анализ крови биохимический общетерапевтический', u'16', 0, 0], # 14
                          [u'Общий анализ мочи', u'17', 0, 0], # 15
                          [u'Исследование кала на скрытую кровь', u'18', 0, 0], # 16
                          [u'Определение уровня простат-специфического антигена в крови (для мужчин)', u'19', 0, 0], # 17
                          [u'Ультразвуковое исследование органов брюшной полости', u'20', 0, 0], # 18
                          [u'Измерение внутриглазного давления', u'21', 0, 0], # 19
                          [u'Профилактический прием (осмотр, консультация) врача-невролога', u'22', 0, 0], # 20
                          [u'Краткое профилактическое консультирование', u'23', 0, 0], # 21
                          [u'ИТОГО', u'24', 0, 0],
                     ]

        # Код 061021 используется как в строке 9, так и в строке 10!
        self.mapActionTypeRow = {u'062014': 0, u'061004': 1, u'061006': 2, u'061005': 3, u'061007': 4, u'061008': 5,
                                 u'061036': 6, u'061018': 7, u'061021': 8, u'061017': 10,
                                 u'061022': 11, u'061010': 12, u'061011': 13, u'061013': 14, u'061012': 15,
                                 u'061015': 16, u'061014': 17, u'061016': 18, u'061009': 19, u'061019': 20,
                                 u'061020': 21}

        self.extraMaps = {u'061021': [9]}



    def makeSSResultSet(self):
        self.resultSet = [[u'Дуплексное сканирование брахицефальных артерий', u'01', u'', 0, 0],
                          [u'Эзофагогастродуоденоскопия', u'02', u'', 0, 0],
                          [u'Осмотр (консультация) врача-невролога', u'03', u'', 0, 0],
                          [u'Осмотр (консультация) врача-хирурга (врача-уролога) (для мужчин)', u'04', u'', 0, 0],
                          [u'Осмотр (консультация) врача-хирурга (врача-колопроктолога)', u'05', u'', 0, 0],
                          [u'Колоноскопия (ректороманоскопия)', u'06', u'', 0, 0],
                          [u'Определение липидного спектра крови', u'07', u'', 0, 0],
                          [u'Осмотр (консультация) врача-акушера-гинеколога (для женщин)', u'08', u'', 0, 0],
                          [u'Определение концентрации гликированного гемоглобина в крови (тест на толерантность к глюкозе)', u'09', u'', 0, 0],
                          [u'Осмотр (консультация) врача-офтальмолога', u'10', u'', 0, 0],
                          [u'Прием (осмотр) врача-терапевта (врача-терапевта участкового, врача-терапевта цехового врачебного участка, врача общей практики (семейного врача)', u'11', u'', 0, 0],
                          [u'Углубленное профилактическое консультирование индивидуальное', u'12', u'', 0, 0],
                          [u'Профилактическое консультирование групповое', u'13', u'', 0, 0],
                          [u'ИТОГО', u'14', u'', 0, 0],
                         ]
        self.mapActionTypeRow = {u'061032': 0, u'061033': 1, u'061023': 2, u'061026': 3, u'061024': 4,
                                 u'061034': 5, u'061030': 6, u'061035': 7, u'061031': 8, u'061025': 9,
                                 u'061027': 10, u'061028': 11, u'061029': 12}
        self.extraMaps = {}


    def build(self, params):
        if self.stage == 1:
            self.makeFSResultSet() 
        else: 
            self.makeSSResultSet()

        query = selectData(params, self.mapActionTypeRow.keys(), self.stage)
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


        if self.stage == 1:
            tableColumns = [
                ( '45%', [u'Осмотр (консультация), исследование', u'1'], CReportBase.AlignLeft),
                ( '5%', [u'№ строки', u'2'], CReportBase.AlignCenter),
                ( '25%', [u'Прошли первый этап диспансеризации (человек)', u'3'], CReportBase.AlignRight),
                ( '25%', [u'Выявлены заболевания (подозрение на наличие заболевания) (случаев)', u'4'], CReportBase.AlignRight),
            ]
            rowSize = 4

        else:
            tableColumns = [
                ( '35%', [u'Осмотр (консультация), исследование', u'1'], CReportBase.AlignLeft),
                ( '5%',  [u'№ строки', u'2'], CReportBase.AlignCenter),
                ( '20%', [u'Выявлены показания по результатам первого этапа диспансеризации (человек)', u'3'], CReportBase.AlignCenter),
                ( '20%', [u'Обследовано (человек)', u'4'], CReportBase.AlignRight),
                ( '20%', [u'Выявлены заболевания (подозрение на наличие заболевания) (случаев)', u'5'], CReportBase.AlignRight),
            ]
            rowSize = 5
        table = createTable(cursor, tableColumns)

        for z in range(len(self.resultSet)):
            row = self.resultSet[z]
            i = table.addRow()
            for j in range(rowSize):
                table.setText(i, j, row[j])

        return doc


class CReportDDPopulationGroups2015(CReport):

    def __init__(self, parent, stage = 1):
        CReport.__init__(self, parent)
        self.stage = stage
        self.setPayPeriodVisible(False)
        if stage == 1:
            self.setTitle(u'Сведения о первом этапе диспансеризации определенных групп взрослого населения')
        else:
            self.setTitle(u'Сведения о втором этапе диспансеризации определенных групп взрослого населения')

    def getSetupDialog(self, parent):
        result = CReportDD2013WeeklySetupDialog(parent)
        result.setSocStatusVisible(True)
        result.setTitle(self.title())
        return result

    def processRow(self, row, sex, age, count):
        if 21 <= age <= 36:
            row[9] += count
            if sex:
                row[sex*3] += count
        elif 39 <= age <= 60:
            row[10] += count
            if sex:
                row[sex*3 + 1] += count
        elif age > 60:
            row[11] += count
            if sex:
                row[sex*3 + 2] += count

    def processRecord(self, record):
        if self.stage == 1:
            finished = 2
            old = 3
            canceled = 4
            ill = 5
        else:
            identified = 2
            finished = 3
            old = 4
            canceled = 5
            ill = 6

        countFinished = forceInt(record.value('countFinished'))
        countOld = forceInt(record.value('countOld'))
        countCanceled = forceInt(record.value('countCanceled'))
        countIll = forceInt(record.value('countEvents'))
        countIdentified = forceInt(record.value('countIdentified'))
        code = forceString(record.value('ddcode'))

        if code in self.mapActionTypeRow:
            i = self.mapActionTypeRow[code]
            if self.stage == 2:
                self.resultSet[i][identified] += countIdentified
            self.resultSet[i][finished] += countFinished
            self.resultSet[i][old] += countOld
            self.resultSet[i][canceled] += countCanceled
            self.resultSet[i][ill] += countIll
        if code in self.extraMaps:
            for i in self.extraMaps[code]:
                if self.stage == 2:
                    self.resultSet[i][identified] += countIdentified
                self.resultSet[i][finished] += countFinished
                self.resultSet[i][old] += countOld
                self.resultSet[i][canceled] += countCanceled
                self.resultSet[i][ill] += countIll
        if QtGui.qApp.region() == '78':
            toSurgeonCond = [u'А04.12.005', u'В04.023.01']
        else:
            toSurgeonCond = [u'A04.12.005.003', u'B04.023.001']
        if self.stage == 2 and code in toSurgeonCond:
            self.countResult += countIll  # направлено к сердечно-сосудистому хирургу

        if self.stage == 2:
            self.resultSet[-1][identified] += countIdentified
        self.resultSet[-1][finished] += countFinished
        self.resultSet[-1][old] += countOld
        self.resultSet[-1][canceled] += countCanceled
        self.resultSet[-1][ill] += countIll

    def makeFSResultSet(self):
        self.resultSet = [
            [u'Опрос (анкетирование) на выявление хронических неинфекционных заболеваний, факторов риска их развития,'
             u' потребления наркотических средств и психотропных веществ без назначения врача', u'01', 0, 0, 0, 0],
            [u'Антропометрия (измерение роста стоя, массы тела, окружности талии), расчет индекса массы тела', u'02', 0, 0, 0, 0],
            [u'Измерение артериального давления', u'03', 0, 0, 0, 0],
            [u'Определение уровня общего холестерина в крови', u'04', 0, 0, 0, 0],
            [u'Определение уровня глюкозы в крови экспресс-методом', u'05', 0, 0, 0, 0],
            [u'Определение относительного суммарного сердечно-сосудистого риска', u'06', 0, 0, 0, 0],
            [u'Определение абсолютного суммарного сердечно-сосудистого риска', u'07', 0, 0, 0, 0],
            [u'Электрокардиография в покое', u'08', 0, 0, 0, 0],
            [u'Осмотр фельдшером (акушеркой), включая взятие мазка (соскоба) с поверхности шейки матки (наружного маточного зева) '
             u'и цервикального канала на цитологическое исследование', u'09', 0, 0, 0, 0],
            [u'Флюорография легких', u'10', 0, 0, 0, 0],
            [u'Маммография обеих молочных желез', u'11', 0, 0, 0, 0],
            [u'Клинический анализ крови', u'12', 0, 0, 0, 0],
            [u'Клинический анализ крови развернутый', u'13', 0, 0, 0, 0],
            [u'Анализ крови биохимический общетерапевтический', u'14', 0, 0, 0, 0],
            [u'Общий анализ мочи', u'15', 0, 0, 0, 0],
            [u'Исследование кала на скрытую кровь иммунохимическим методом', u'16', 0, 0, 0, 0],
            [u'Ультразвуковое исследование (УЗИ) на предмет исключения новообразований органов брюшной полости, '
             u'малого таза и аневризмы брюшной аорты', u'17', 0, 0, 0, 0],
            [u'Ультразвуковое исследование (УЗИ) в целях исключения аневризмы брюшной аорты', u'18', 0, 0, 0, 0],
            [u'Измерение внутриглазного давления', u'19', 0, 0, 0, 0],
            [u'Прием (осмотр) врача-терапевта', u'20', 0, 0, 0, 0],
            [u'Всего', u'21', 0, 0, 0, 0],
        ]
        if QtGui.qApp.region() == '78':
            self.mapActionTypeRow = {
                 u'061004': 0, u'А01.31.024*': 0, u'А01.31.025*': 0,
                 u'061006': 1, u'А02.07.004': 1,
                 u'061005': 2, u'А01.31.024.001': 2,
                 u'061007':3, u'А09.05.026 ': 3, u'А09.05.026': 3,
                 u'061008':4, u'А09.05.023': 4,
                 u'А25.12.004': 5,
                 u'А25.12.004.86': 6,
                 u'061018': 7, u'А05.10.001.003*': 7,
                 u'061021': 8,
                 u'061035': 8, u'В01.001.06*': 8, u'В01.001.01*Д': 8, u'А08.20.019*': 8, u'А08.20.019': 8,
                 u'061017': 9, u'А06.09.007.001': 9, u'А06.09.007.001.': 9,
                 u'А06.09.007.002*': 9, u'А06.09.007.003*': 9, u'А06.09.007*Д': 9,
                 u'061022': 10, u'А06.20.006': 10,
                 u'061010': 11, u'В03.016.02': 11, u'В03.016.02*Д': 11,
                 u'061011': 12, u'В03.016.03': 12,
                 u'061013': 13, u'В03.016.04': 13,
                 u'061012': 14, u'В03.016.06': 14,
                 u'061015': 15, u'А09.19.002': 15,
                 u'061016': 16, u'А04.16.001': 16, u'В03.052.02*': 16, u'В03.052.03': 16,
                 u'061037': 17,  u'A04.12.003': 17, u'А04.12.003': 17,
                 u'061009': 18, u'А02.26.015.001*': 18, u'А02.26.015': 18,
                 u'061027': 19, u'В01.047.01': 19
            }
            self.extraMaps = {u'061036': [5, 6]}
        else:
            self.mapActionTypeRow = {
                u'A01.30.009': 0,
                # u'B03.069.003': 1, u'A02.07.004': 1, u'A01.30.028': 1, u'A02.01.001': 1, u'A02.03.005': 1, u'A02.03.007.004': 1,
                # u'B03.069.003': 1,
                u'A02.12.002': 2,
                u'A09.05.026': 3, u'A09.05.026.005': 3,
                u'A09.05.023': 4, u'A09.05.023.007': 4,
                u'B04.015.008': 5,
                u'B04.015.007': 6,
                u'A05.10.002': 7, u'A05.10.002.003': 7,
                u'A11.20.024': 8, u'B04.001.009': 8,
                u'A06.09.006': 9,
                u'A06.20.004': 10,
                u'B03.016.002': 11,
                u'B03.016.003': 12,
                u'B03.016.004': 13,
                u'B03.016.006': 14,
                u'A09.19.001': 15,
                u'A04.20.001': 16, u'A04.15.001': 16, u'A04.28.002.001': 16,
                u'A04.12.003': 17,
                u'A02.26.019': 18, u'A12.26.005': 18,
                u'B04.047.001': 19, u'B04.047.001.01': 19, u'B04.047.001.02': 19, u'B04.047.001.03': 19, #TODO: Изменить на композицию LIKE'ов
                u'B04.047.001.04': 19, u'B04.047.001.05': 19, u'B04.047.001.06': 19, u'B04.047.001.07': 19,
                u'B04.047.001.08': 19, u'B04.047.001.09': 19,  u'B04.047.001.10': 19, u'B04.047.001.11': 19,
                u'B04.047.001.12': 19, u'B04.047.001.13': 19, u'B04.047.001.14': 19, u'B04.047.001.15': 19,
                u'B04.047.001.61': 19,
            }
            self.extraMaps = {u'A01.30.009': [1]} # Антропометрию проще посчитать по анкете
            # self.extraMaps = {u'A01.12.001' : [6]}

    def makeSSResultSet(self):
        self.resultSet = [
            [u'Дуплексное сканирование брахицефальных артерий', u'01', 0, 0, 0, 0, 0],
            [u'Осмотр (консультация) врачом-неврологом', u'02', 0, 0, 0, 0, 0],
            [u'Эзофагогастродуоденоскопия', u'03', 0, 0, 0, 0, 0],
            [u'Осмотр (консультация) врачом-хирургом или врачом-урологом', u'04', 0, 0, 0, 0, 0],
            [u'Осмотр (консультация) врачом-хирургом или врачом-проктологом', u'05', 0, 0, 0, 0, 0],
            [u'Колоноскопия или ректороманоскопия', u'06', 0, 0, 0, 0, 0],
            [u'Определение липидного спектра крови', u'07', 0, 0, 0, 0, 0],
            [u'Спирометрия', u'08', 0, 0, 0, 0, 0],
            [u'Осмотр (консультация) врачом-акушером-гинекологом', u'09', 0, 0, 0, 0, 0],
            [u'Определение концентрации гликированного гемоглобина в крови или тест на толерантность к глюкозе', u'10', 0, 0, 0, 0, 0],
            [u'Осмотр (консультация) врачом-оториноларингологом', u'11', 0, 0, 0, 0, 0],
            [u'Анализ крови на уровень содержания простатспецифического антигена', u'12', 0, 0, 0, 0, 0],
            [u'Осмотр (консультация) врачом-офтальмологом', u'13', 0, 0, 0, 0, 0],
            [u'Индивидуальное углубленное профилактическое консультирование', u'14', 0, 0, 0, 0, 0],
            [u'Групповое профилактическое консультирование (школа пациента)', u'15', 0, 0, 0, 0, 0],
            [u'Прием (осмотр) врачом-терапевтом', u'16', 0, 0, 0, 0, 0],
            [u'ИТОГО', u'17', 0, 0, 0, 0, 0],
        ]
        if QtGui.qApp.region() == '78':
            self.mapActionTypeRow = {u'061032': 0, u'А04.12.005': 0,
                                     u'061023': 1, u'В01.023.01': 1,
                                     u'061033': 2, u'А03.16.001': 2,
                                     u'061026': 3, u'В01.057.01': 3, u'В01.053.01': 3,
                                     u'061024': 4, u'В01.018.01': 4,
                                     u'061034': 5, u'А03.19.002': 5,
                                     u'061030': 6, u'В03.016.05': 6,
                                     u'061039': 7, u'А05.10.005*': 7,
                                     u'061035': 8, u'В01.001.01': 8,
                                     u'061031': 9, u'А09.05.084': 9,
                                     u'061040':10, u'В01.028.01': 10,
                                     u'061041': 11, u'А09.05.135': 11,
                                     u'061025': 12,
                                     u'061028':13, u'А13.29.006.001': 13,
                                     u'061027': 15, u'В01.047.01': 15
                                     }
            self.extraMaps = {
                u'061028': [14]
            }
        else:
            self.mapActionTypeRow = {
                u'A04.12.005.003': 0,
                u'B04.023.001': 1,
                u'A03.16.001': 2,
                u'B04.053.001': 3,
                u'B04.018.001': 4,
                u'A03.18.001': 5,
                u'A09.05.024': 6,
                u'A12.09.001': 7, u'A12.09.001.003': 7,
                u'B04.001.001': 8,
                u'A12.22.005': 9, u'A12.22.005.001': 9, u'A12.22.005.002': 9, u'A09.05.083': 9,
                u'B04.028.001': 10,
                u'A09.05.130': 11,
                u'B04.029.001': 12,
                u'B04.069.004': 13,
                # u'B04.069.004': 14,
                u'B04.047.001': 15
            }
            self.extraMaps = {u'B04.069.004' : [14]}

    def build(self, params):
        if self.stage == 1:
            self.makeFSResultSet()
        else:
            self.makeSSResultSet()
            self.countResult = 0

        query = selectData(params, self.mapActionTypeRow.keys(), self.stage, DDREPORT_2015)
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


        if self.stage == 1:
            tableColumns = [
                ('40%', [u'Осмотр, исследование, иное медицинское мероприятие первого этапа диспансеризации', u'', u'1'], CReportBase.AlignLeft),
                ( '5%', [u'№ строки', u'', u'2'], CReportBase.AlignCenter),
                ('10%', [u'Медицинское мероприятие', u'проведено', u'3'], CReportBase.AlignRight),
                ('10%', [u'', u'учтено, выполненных ранее (в предшествующие 12 мес.)', u'4'], CReportBase.AlignRight),
                ('10%', [u'', u'отказы', u'5'], CReportBase.AlignRight),
                ('25%', [u'Выявлены патологические отклонения', u'', u'6'], CReportBase.AlignRight),
            ]
            rowSize = 6
        else:
            tableColumns = [
                ('35%', [u'Медицинское мероприятие второго этапа диспансеризации', u'',  u'1'], CReportBase.AlignLeft),
                ( '5%', [u'№ строки', u'', u'2'], CReportBase.AlignCenter),
                ('12%', [u'Выявлено показание к дополнительному обследованию', u'', u'3'], CReportBase.AlignCenter),
                ('12%', [u'Количество выполненных медицинских мероприятий', u'в рамках диспансеризации', u'4'], CReportBase.AlignRight),
                ('12%', [u'', u'проведено ранее (в предшествующие 12 мес.)', u'4'], CReportBase.AlignRight),
                ('12%', [u'Отказы', u'', u'4'], CReportBase.AlignRight),
                ('12%', [u'Выявлено заболеваний', u'', u'5'], CReportBase.AlignRight),
            ]
            rowSize = 7
        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        if self.stage == 1:
            table.mergeCells(0, 2, 1, 3)
            table.mergeCells(0, 5, 2, 1)
        else:
            table.mergeCells(0, 2, 2, 1)
            table.mergeCells(0, 3, 1, 2)
            table.mergeCells(0, 5, 2, 1)
            table.mergeCells(0, 6, 2, 1)


        for z in range(len(self.resultSet)):
            row = self.resultSet[z]
            i = table.addRow()
            for j in range(rowSize):
                table.setText(i, j, row[j])
        if self.stage == 2:
            cursor.movePosition(cursor.End, 0)
            cursor.insertBlock()
            cursor.insertBlock()
            cursor.insertText(u'3001 По  результатам  осмотра  врачом-неврологом  и  дуплексного сканирования брахицефальных артерий выявлено медицинское показание для направления и направлено к врачу-сердечно-сосудистому хирургу %s человек.' % self.countResult)

        return doc


class CReportDDPopulationGroups2017(CReport):

    def __init__(self, parent, stage = 1):
        CReport.__init__(self, parent)
        self.stage = stage
        self.setPayPeriodVisible(False)
        if stage == 1:
            self.setTitle(u'Сведения о первом этапе диспансеризации определенных групп взрослого населения')
        else:
            self.setTitle(u'Сведения о втором этапе диспансеризации определенных групп взрослого населения')

    def getSetupDialog(self, parent):
        result = CReportDD2013WeeklySetupDialog(parent)
        result.setSocStatusVisible(True)
        result.setTitle(self.title())
        return result

    def processRow(self, row, sex, age, count):
        if 21 <= age <= 36:
            row[9] += count
            if sex:
                row[sex*3] += count
        elif 39 <= age <= 60:
            row[10] += count
            if sex:
                row[sex*3 + 1] += count
        elif age > 60:
            row[11] += count
            if sex:
                row[sex*3 + 2] += count

    def processRecord(self, record):
        if self.stage == 1:
            finished = 2
            old = 3
            canceled = 4
            ill = 5
        else:
            identified = 2
            finished = 3
            old = 4
            canceled = 5
            ill = 6

        countFinished = forceInt(record.value('countFinished'))
        countOld = forceInt(record.value('countOld'))
        countCanceled = forceInt(record.value('countCanceled'))
        countIll = forceInt(record.value('countEvents'))
        countIdentified = forceInt(record.value('countIdentified'))
        code = forceString(record.value('ddcode'))

        if code in self.mapActionTypeRow:
            i = self.mapActionTypeRow[code]
            if self.stage == 2:
                self.resultSet[i][identified] += countIdentified
            self.resultSet[i][finished] += countFinished
            self.resultSet[i][old] += countOld
            self.resultSet[i][canceled] += countCanceled
            self.resultSet[i][ill] += countIll
        if code in self.extraMaps:
            for i in self.extraMaps[code]:
                if self.stage == 2:
                    self.resultSet[i][identified] += countIdentified
                self.resultSet[i][finished] += countFinished
                self.resultSet[i][old] += countOld
                self.resultSet[i][canceled] += countCanceled
                self.resultSet[i][ill] += countIll
        if QtGui.qApp.region() == '78':
            toSurgeonCond = [u'А04.12.005', u'В04.023.01']
        else:
            toSurgeonCond = [u'A04.12.005.003', u'B04.023.001']
        if self.stage == 2 and code in toSurgeonCond:
            self.countResult += countIll  # направлено к сердечно-сосудистому хирургу

        if self.stage == 2:
            self.resultSet[-1][identified] += countIdentified
        self.resultSet[-1][finished] += countFinished
        self.resultSet[-1][old] += countOld
        self.resultSet[-1][canceled] += countCanceled
        self.resultSet[-1][ill] += countIll

    def makeFSResultSet(self):
        self.resultSet = [
            [u'Опрос (анкетирование) на выявление хронических неинфекционных заболеваний, факторов риска их развития,'
             u' потребления наркотических средств и психотропных веществ без назначения врача', u'01', 0, 0, 0, 0],
            [u'Антропометрия (измерение роста стоя, массы тела, окружности талии), расчет индекса массы тела', u'02', 0, 0, 0, 0],
            [u'Измерение артериального давления', u'03', 0, 0, 0, 0],
            [u'Определение уровня общего холестерина в крови', u'04', 0, 0, 0, 0],
            [u'Определение уровня глюкозы в крови экспресс-методом', u'05', 0, 0, 0, 0],
            [u'Определение относительного суммарного сердечно-сосудистого риска', u'06', 0, 0, 0, 0],
            [u'Определение абсолютного суммарного сердечно-сосудистого риска', u'07', 0, 0, 0, 0],
            [u'Электрокардиография в покое', u'08', 0, 0, 0, 0],
            [u'Осмотр фельдшером (акушеркой), включая взятие мазка (соскоба) с поверхности шейки матки (наружного маточного зева) '
             u'и цервикального канала на цитологическое исследование', u'09', 0, 0, 0, 0],
            [u'Флюорография легких', u'10', 0, 0, 0, 0],
            [u'Маммография обеих молочных желез', u'11', 0, 0, 0, 0],
            [u'Клинический анализ крови', u'12', 0, 0, 0, 0],
            [u'Клинический анализ крови развернутый', u'13', 0, 0, 0, 0],
            [u'Анализ крови биохимический общетерапевтический', u'14', 0, 0, 0, 0],
            [u'Общий анализ мочи', u'15', 0, 0, 0, 0],
            [u'Исследование кала на скрытую кровь иммунохимическим методом', u'16', 0, 0, 0, 0],
            [u'Ультразвуковое исследование (УЗИ) на предмет исключения новообразований органов брюшной полости, '
             u'малого таза и аневризмы брюшной аорты', u'17', 0, 0, 0, 0],
            [u'Ультразвуковое исследование (УЗИ) в целях исключения аневризмы брюшной аорты', u'18', 0, 0, 0, 0],
            [u'Измерение внутриглазного давления', u'19', 0, 0, 0, 0],
            [u'Прием (осмотр) врача-терапевта', u'20', 0, 0, 0, 0],
            [u'Всего', u'21', 0, 0, 0, 0],
        ]
        if QtGui.qApp.region() == '78':
            self.mapActionTypeRow = {
                 u'061004': 0, u'А01.31.024*': 0, u'А01.31.025*': 0,
                 u'061006': 1, u'А02.07.004': 1,
                 u'061005': 2, u'А01.31.024.001': 2,
                 u'061007':3, u'А09.05.026 ': 3, u'А09.05.026': 3,
                 u'061008':4, u'А09.05.023': 4,
                 u'А25.12.004': 5,
                 u'А25.12.004.86': 6,
                 u'061018': 7, u'А05.10.001.003*': 7,
                 u'061021': 8,
                 u'061035': 8, u'В01.001.06*': 8, u'В01.001.01*Д': 8, u'А08.20.019*': 8, u'А08.20.019': 8,
                 u'061017': 9, u'А06.09.007.001': 9, u'А06.09.007.001.': 9,
                 u'А06.09.007.002*': 9, u'А06.09.007.003*': 9, u'А06.09.007*Д': 9,
                 u'061022': 10, u'А06.20.006': 10,
                 u'061010': 11, u'В03.016.02': 11, u'В03.016.02*Д': 11,
                 u'061011': 12, u'В03.016.03': 12,
                 u'061013': 13, u'В03.016.04': 13,
                 u'061012': 14, u'В03.016.06': 14,
                 u'061015': 15, u'А09.19.002': 15,
                 u'061016': 16, u'А04.16.001': 16, u'В03.052.02*': 16, u'В03.052.03': 16,
                 u'061037': 17,  u'A04.12.003': 17, u'А04.12.003': 17,
                 u'061009': 18, u'А02.26.015.001*': 18, u'А02.26.015': 18,
                 u'061027': 19, u'В01.047.01': 19
            }
            self.extraMaps = {u'061036': [5, 6]}
        else:
            self.mapActionTypeRow = {
                u'A01.30.009': 0,
                # u'B03.069.003': 1, u'A02.07.004': 1, u'A01.30.028': 1, u'A02.01.001': 1, u'A02.03.005': 1, u'A02.03.007.004': 1,
                # u'B03.069.003': 1,
                u'A02.12.002': 2,
                u'A09.05.026': 3, u'A09.05.026.005': 3,
                u'A09.05.023': 4, u'A09.05.023.007': 4,
                u'B04.015.008': 5,
                u'B04.015.007': 6,
                u'A05.10.002': 7, u'A05.10.002.003': 7,
                u'A11.20.024': 8, u'B04.001.009': 8,
                u'A06.09.006': 9,
                u'A06.20.004': 10,
                u'B03.016.002': 11,
                u'B03.016.003': 12,
                u'B03.016.004': 13,
                u'B03.016.006': 14,
                u'A09.19.001': 15,
                u'A04.20.001': 16, u'A04.15.001': 16, u'A04.28.002.001': 16,
                u'A04.12.003': 17,
                u'A02.26.019': 18, u'A12.26.005': 18,

            }
            self.extraMaps = {u'A01.30.009': [1], u'A02.12.002': [19]} # Антропометрию проще посчитать по анкете
            # self.extraMaps = {u'A01.12.001' : [6]}

    def makeSSResultSet(self):
        self.resultSet = [
            [u'Дуплексное сканирование брахицефальных артерий', u'01', 0, 0, 0, 0, 0],
            [u'Осмотр (консультация) врачом-неврологом', u'02', 0, 0, 0, 0, 0],
            [u'Эзофагогастродуоденоскопия', u'03', 0, 0, 0, 0, 0],
            [u'Осмотр (консультация) врачом-хирургом или врачом-урологом', u'04', 0, 0, 0, 0, 0],
            [u'Осмотр (консультация) врачом-хирургом или врачом-проктологом', u'05', 0, 0, 0, 0, 0],
            [u'Колоноскопия или ректороманоскопия', u'06', 0, 0, 0, 0, 0],
            [u'Определение липидного спектра крови', u'07', 0, 0, 0, 0, 0],
            [u'Спирометрия', u'08', 0, 0, 0, 0, 0],
            [u'Осмотр (консультация) врачом-акушером-гинекологом', u'09', 0, 0, 0, 0, 0],
            [u'Определение концентрации гликированного гемоглобина в крови или тест на толерантность к глюкозе', u'10', 0, 0, 0, 0, 0],
            [u'Осмотр (консультация) врачом-оториноларингологом', u'11', 0, 0, 0, 0, 0],
            [u'Анализ крови на уровень содержания простатспецифического антигена', u'12', 0, 0, 0, 0, 0],
            [u'Осмотр (консультация) врачом-офтальмологом', u'13', 0, 0, 0, 0, 0],
            [u'Индивидуальное углубленное профилактическое консультирование', u'14', 0, 0, 0, 0, 0],
            [u'Групповое профилактическое консультирование (школа пациента)', u'15', 0, 0, 0, 0, 0],
            [u'Прием (осмотр) врачом-терапевтом', u'16', 0, 0, 0, 0, 0],
            [u'ИТОГО', u'17', 0, 0, 0, 0, 0],
        ]
        if QtGui.qApp.region() == '78':
            self.mapActionTypeRow = {u'061032': 0, u'А04.12.005': 0,
                                     u'061023': 1, u'В01.023.01': 1,
                                     u'061033': 2, u'А03.16.001': 2,
                                     u'061026': 3, u'В01.057.01': 3, u'В01.053.01': 3,
                                     u'061024': 4, u'В01.018.01': 4,
                                     u'061034': 5, u'А03.19.002': 5,
                                     u'061030': 6, u'В03.016.05': 6,
                                     u'061039': 7, u'А05.10.005*': 7,
                                     u'061035': 8, u'В01.001.01': 8,
                                     u'061031': 9, u'А09.05.084': 9,
                                     u'061040':10, u'В01.028.01': 10,
                                     u'061041': 11, u'А09.05.135': 11,
                                     u'061025': 12,
                                     u'061028':13, u'А13.29.006.001': 13,
                                     u'061027': 15, u'В01.047.01': 15
                                     }
            self.extraMaps = {
                u'061028': [14]
            }
        else:
            self.mapActionTypeRow = {
                u'A04.12.005.003': 0,
                u'B04.023.001': 1,
                u'A03.16.001': 2,
                u'B04.053.001': 3,
                u'B04.018.001': 4,
                u'A03.18.001': 5,
                u'A09.05.024': 6,
                u'A12.09.001': 7, u'A12.09.001.003': 7,
                u'B04.001.001': 8,
                u'A12.22.005': 9, u'A12.22.005.001': 9, u'A12.22.005.002': 9, u'A09.05.083': 9,
                u'B04.028.001': 10,
                u'A09.05.130': 11,
                u'B04.029.001': 12,
                u'B04.069.004': 13,
                # u'B04.069.004': 14,
                u'B04.047.001': 15
            }
            self.extraMaps = {u'B04.069.004' : [14]}

    def build(self, params):
        if self.stage == 1:
            self.makeFSResultSet()
        else:
            self.makeSSResultSet()
            self.countResult = 0

        query = selectData(params, self.mapActionTypeRow.keys(), self.stage, DDREPORT_2017)
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


        if self.stage == 1:
            tableColumns = [
                ('40%', [u'Осмотр, исследование, иное медицинское мероприятие первого этапа диспансеризации', u'', u'1'], CReportBase.AlignLeft),
                ( '5%', [u'№ строки', u'', u'2'], CReportBase.AlignCenter),
                ('10%', [u'Медицинское мероприятие', u'проведено', u'3'], CReportBase.AlignRight),
                ('10%', [u'', u'учтено, выполненных ранее (в предшествующие 12 мес.)', u'4'], CReportBase.AlignRight),
                ('10%', [u'', u'отказы', u'5'], CReportBase.AlignRight),
                ('25%', [u'Выявлены патологические отклонения', u'', u'6'], CReportBase.AlignRight),
            ]
            rowSize = 6
        else:
            tableColumns = [
                ('35%', [u'Медицинское мероприятие второго этапа диспансеризации', u'',  u'1'], CReportBase.AlignLeft),
                ( '5%', [u'№ строки', u'', u'2'], CReportBase.AlignCenter),
                ('12%', [u'Выявлено показание к дополнительному обследованию', u'', u'3'], CReportBase.AlignCenter),
                ('12%', [u'Количество выполненных медицинских мероприятий', u'в рамках диспансеризации', u'4'], CReportBase.AlignRight),
                ('12%', [u'', u'проведено ранее (в предшествующие 12 мес.)', u'4'], CReportBase.AlignRight),
                ('12%', [u'Отказы', u'', u'4'], CReportBase.AlignRight),
                ('12%', [u'Выявлено заболеваний', u'', u'5'], CReportBase.AlignRight),
            ]
            rowSize = 7

        cursor.movePosition(cursor.End)
        if self.stage == 2:
            cursor.insertText(u'3000')
        else:
            cursor.insertText(u'2000')

        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        if self.stage == 1:
            table.mergeCells(0, 2, 1, 3)
            table.mergeCells(0, 5, 2, 1)
        else:
            table.mergeCells(0, 2, 2, 1)
            table.mergeCells(0, 3, 1, 2)
            table.mergeCells(0, 5, 2, 1)
            table.mergeCells(0, 6, 2, 1)


        for z in range(len(self.resultSet)):
            row = self.resultSet[z]
            i = table.addRow()
            row[5] = ""
            for j in range(rowSize):
                table.setText(i, j, row[j])
        if self.stage == 2:
            cursor.movePosition(cursor.End, 0)
            cursor.insertBlock()
            cursor.insertBlock()
            cursor.insertText(u'3001 По  результатам  осмотра  врачом-неврологом  и  дуплексного сканирования брахицефальных артерий выявлено медицинское показание для направления и направлено к врачу-сердечно-сосудистому хирургу %s человек.' % self.countResult)

        return doc