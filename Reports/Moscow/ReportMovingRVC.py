# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from library.DialogBase import CDialogBase
from library.Utils      import forceInt, forceRef, forceString, formatName, forceDateTime
from library.database   import addDateInRange

from Orgs.Utils         import getOrgStructureDescendants

from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase

from Ui_ReportMovingRVCSetupDialog import Ui_ReportMovingRVCSetupDialog


def countEventsByOrgStructure(begDate, endDate, orgStructureId):
    db = QtGui.qApp.db
    Event = db.table('Event')
    Person = db.table('Person')
    queryTable = Event.leftJoin(Person, Person['id'].eq(Event['execPerson_id']))
    cond = [
        Event['deleted'].eq(0),
        Person['orgStructure_id'].eq(orgStructureId)
    ]
    addDateInRange(cond, Event['setDate'], begDate, endDate)
    record = db.getRecordEx(queryTable, 'count(*) AS cnt', cond)
    return forceInt(record.value('cnt')) if not record is None else 0


def getOperations(begDate, endDate, orgStructureId):
    db = QtGui.qApp.db
    Action = db.table('Action')
    ActionType = db.table('ActionType')
    Person = db.table('Person')

    queryTable = Action.innerJoin(ActionType, ActionType['id'].eq(Action['actionType_id']))
    queryTable = queryTable.innerJoin(Person, Person['id'].eq(Action['person_id']))

    isOperation = ActionType['serviceType'].eq(4)
    isCoronarography = ActionType['name'].eq(u'Коронарография')
    isUrgent = Action['isUrgent'].eq(1)

    cols = [
        u'count(if({0}, {1}, NULL)) AS operationTotal'.format(isOperation, Action['id']),
        u'count(if({0}, {1}, NULL)) AS operationUrgent'.format(db.joinAnd([isOperation, isUrgent]), Action['id']),
        u'count(if({0}, {1}, NULL)) AS coronaryTotal'.format(isCoronarography, Action['id']),
        u'count(if({0}, {1}, NULL)) AS coronaryUrgent'.format(db.joinAnd([isCoronarography, isUrgent]), Action['id'])
    ]
    cond = [
        Action['deleted'].eq(0),
        Person['orgStructure_id'].eq(orgStructureId)
    ]
    addDateInRange(cond, Action['begDate'], begDate, endDate)

    record = db.getRecordEx(queryTable, cols, cond)

    if not record is None:
        operationTotal = forceInt(record.value('operationTotal'))
        operationUrgent = forceInt(record.value('operationUrgent'))
        coronaryTotal = forceInt(record.value('coronaryTotal'))
        coronaryUrgent = forceInt(record.value('coronaryUrgent'))

        return operationTotal, operationUrgent, coronaryTotal, coronaryUrgent

    return 0, 0, 0, 0


def selectData(begDateTime, endDateTime):
    db = QtGui.qApp.db
    Action = db.table('Action')
    OrgStructure = db.table('OrgStructure')

    stmt = u'''
    SELECT
      mainTable.id                                                                         AS osId,
      mainTable.code                                                                       AS osCode,
      mainTable.totalBeds                                                                  AS totalBeds,
      mainTable.permanentBeds                                                              AS permanentBeds,
      mainTable.involuteBeds                                                               AS involuteBeds,
      mainTable.menBeds                                                                    AS menBeds,
      mainTable.womenBeds                                                                  AS womenBeds,
      (received.men + moving.men + movingInto.men - movingFrom.men - leaved.men)           AS men,
      (received.women + moving.women + movingInto.women - movingFrom.women - leaved.women) AS women,
      received.received                                                                    AS received,
      received.byHimself                                                                   AS byHimself,
      received.hospRefused                                                                 AS refused,
      moving.moving                                                                        AS moving,
      movingInto.movingInto                                                                AS movingInto,
      movingFrom.movingFrom                                                                AS movingFrom,
      leaved.leaved                                                                        AS leaved,
      leaved.dead                                                                          AS dead,
      received.eventsDMS                                                                   AS eventsDMS,
      received.eventsPMU                                                                   AS eventsPMU,
      leaved.eventsDeath                                                                   AS eventsDeath
    FROM
      # OrgStructures
      (SELECT
        OrgStructure.id                                                 AS id,
        OrgStructure.code                                               AS code,
        OrgStructure.name                                               AS name,
        count(OSHB.id)                                                  AS totalBeds,
        count(if(OSHB.isPermanent = 1, OSHB.id, NULL))                  AS permanentBeds,
        count(if(HBI.involuteType = 1, HBI.id, NULL))                   AS involuteBeds,
        count(if(OSHB.sex = 1 AND OSHB.isPermanent = 1, OSHB.id, NULL)) AS menBeds,
        count(if(OSHB.sex = 2 AND OSHB.isPermanent = 1, OSHB.id, NULL)) AS womenBeds
      FROM
        OrgStructure
        INNER JOIN OrgStructure_HospitalBed AS OSHB ON OSHB.master_id = OrgStructure.id
        LEFT JOIN HospitalBed_Involute AS HBI ON HBI.master_id = OSHB.id
      WHERE OrgStructure.deleted = 0
      GROUP BY OrgStructure.id) AS mainTable

      # RECEIVED
      LEFT JOIN (SELECT
        OrgStructure.id                                                     AS id,
        count(AP.id)                                                        AS received,
        count(if(DeliveredByAPS.value LIKE '%самотёк%', Action.id, NULL))   AS byHimself,
        count(if(HospRefusedAPS.value IS NOT NULL, Action.id, NULL))        AS hospRefused,
        count(if(Client.sex = 1, Client.id, NULL))                          AS men,
        count(if(Client.sex = 2, Client.id, NULL))                          AS women,
        group_concat(if(DeliveredByAPS.value LIKE 'ПМУ', Event.id, NULL))   AS eventsPMU,
        group_concat(if(DeliveredByAPS.value LIKE '%ДМС%', Event.id, NULL)) AS eventsDMS
      FROM
        Event

        INNER JOIN Client ON Client.id = Event.client_id AND Client.deleted = 0

        INNER JOIN ActionType ON ActionType.flatCode = 'received' AND ActionType.deleted = 0
        INNER JOIN Action ON Action.id = (
          SELECT MAX(A.id)
          FROM Action A
          WHERE A.event_id = Event.id AND A.actionType_id = ActionType.id AND A.deleted = 0
        )

        INNER JOIN ActionPropertyType AS APT ON APT.actionType_id = ActionType.id AND APT.name = 'Направлен в отделение' AND APT.deleted = 0
        INNER JOIN ActionProperty AS AP ON AP.action_id = Action.id AND AP.type_id = APT.id AND AP.deleted = 0
        INNER JOIN ActionProperty_OrgStructure AS APOS ON APOS.id = AP.id
        INNER JOIN OrgStructure ON OrgStructure.id = APOS.value

        INNER JOIN ActionPropertyType DeliveredByAPT ON DeliveredByAPT.name = 'Кем доставлен' AND DeliveredByAPT.actionType_id = ActionType.id AND DeliveredByAPT.deleted = 0
        LEFT JOIN ActionProperty DeliveredByAP ON DeliveredByAP.action_id = Action.id AND DeliveredByAP.type_id = DeliveredByAPT.id AND DeliveredByAP.deleted = 0
        LEFT JOIN ActionProperty_String DeliveredByAPS ON DeliveredByAPS.id = DeliveredByAP.id

        INNER JOIN ActionPropertyType HospRefusedAPT ON HospRefusedAPT.name = 'Причина отказа от госпитализации' AND HospRefusedAPT.actionType_id = ActionType.id AND HospRefusedAPT.deleted = 0
        LEFT JOIN ActionProperty HospRefusedAP ON HospRefusedAP.action_id = Action.id AND HospRefusedAP.type_id = HospRefusedAPT.id AND HospRefusedAP.deleted = 0
        LEFT JOIN ActionProperty_String HospRefusedAPS ON HospRefusedAPS.id = HospRefusedAP.id

        INNER JOIN Action FirstMoving ON FirstMoving.id = (
          SELECT min(A.id)
          FROM Action A
            INNER JOIN ActionType MovingAT ON MovingAT.flatCode = 'moving' AND A.actionType_id = MovingAT.id AND MovingAT.deleted = 0
          WHERE A.event_id = Event.id AND A.deleted = 0
        )
      WHERE
        Event.deleted = 0 AND {receivedDateCond}
      GROUP BY
        OrgStructure.id
      ) AS received ON received.id = mainTable.id

      # MOVING INTO
      LEFT JOIN (SELECT
        OrgStructure.id                            AS id,
        count(AP.id)                               AS movingInto,
        count(if(Client.sex = 1, Client.id, NULL)) AS men,
        count(if(Client.sex = 2, Client.id, NULL)) AS women
      FROM
        ActionType
        INNER JOIN Action ON Action.actionType_id = ActionType.id AND Action.deleted = 0
        INNER JOIN Event ON Event.id = Action.event_id AND Event.deleted = 0
        INNER JOIN Client ON Client.id = Event.client_id AND Client.deleted = 0

        INNER JOIN ActionPropertyType AS APT ON APT.actionType_id = ActionType.id AND APT.name = 'Переведен в отделение' AND APT.deleted = 0
        INNER JOIN ActionProperty AS AP ON AP.action_id = Action.id AND AP.type_id = APT.id AND AP.deleted = 0
        INNER JOIN ActionProperty_OrgStructure AS APOS ON APOS.id = AP.id
        INNER JOIN OrgStructure ON OrgStructure.id = APOS.value
      WHERE
        ActionType.flatCode = 'moving' AND ActionType.deleted = 0 AND {movingIntoDateCond}
      GROUP BY
        OrgStructure.id
      ) AS movingInto ON movingInto.id = mainTable.id

      # MOVING FROM
      LEFT JOIN (SELECT
        OrgStructure.id                            AS id,
        count(AP.id)                               AS movingFrom,
        count(if(Client.sex = 1, Client.id, NULL)) AS men,
        count(if(Client.sex = 2, Client.id, NULL)) AS women
      FROM
        ActionType
        INNER JOIN Action ON Action.actionType_id = ActionType.id AND Action.deleted = 0
        INNER JOIN Event ON Event.id = Action.event_id AND Event.deleted = 0
        INNER JOIN Client ON Client.id = Event.client_id AND Client.deleted = 0

        INNER JOIN ActionPropertyType AS APT ON APT.actionType_id = ActionType.id AND APT.name = 'Переведен из отделения' AND APT.deleted = 0
        INNER JOIN ActionProperty AS AP ON AP.action_id = Action.id AND AP.type_id = APT.id AND AP.deleted = 0
        INNER JOIN ActionProperty_OrgStructure AS APOS ON APOS.id = AP.id
        INNER JOIN OrgStructure ON OrgStructure.id = APOS.value
      WHERE
        ActionType.flatCode = 'moving' AND ActionType.deleted = 0 AND {movingFromDateCond}
      GROUP BY
        OrgStructure.id
      ) AS movingFrom ON movingFrom.id = mainTable.id

      # LEAVED
      LEFT JOIN (SELECT
        OrgStructure.id                                            AS id,
        count(if(ResultAPS.value != 'умер', ResultAPS.id, NULL))   AS leaved,
        count(if(ResultAPS.value = 'умер', ResultAPS.id, NULL))    AS dead,
        count(if(Client.sex = 1, Client.id, NULL))                 AS men,
        count(if(Client.sex = 2, Client.id, NULL))                 AS women,
        group_concat(if(ResultAPS.value = 'умер', Event.id, NULL)) AS eventsDeath
      FROM
        Event

        INNER JOIN ActionType ON ActionType.flatCode = 'leaved' AND ActionType.deleted = 0
        INNER JOIN Action ON Action.id = (
          SELECT MAX(A.id)
          FROM Action A
          WHERE A.event_id = Event.id AND A.actionType_id = ActionType.id AND A.deleted = 0
        )

        INNER JOIN Client ON Client.id = Event.client_id AND Client.deleted = 0

        INNER JOIN ActionPropertyType AS APT ON APT.actionType_id = ActionType.id AND APT.name = 'Отделение' AND APT.deleted = 0
        INNER JOIN ActionProperty AS AP ON AP.action_id = Action.id AND AP.type_id = APT.id AND AP.deleted = 0
        INNER JOIN ActionProperty_OrgStructure AS APOS ON APOS.id = AP.id
        INNER JOIN OrgStructure ON OrgStructure.id = APOS.value

        LEFT JOIN ActionPropertyType AS ResultAPT ON ResultAPT.actionType_id = ActionType.id AND ResultAPT.name = 'Исход госпитализации' AND ResultAPT.deleted = 0
        LEFT JOIN ActionProperty AS ResultAP ON ResultAP.action_id = Action.id AND ResultAP.type_id = ResultAPT.id AND ResultAPT.deleted = 0
        LEFT JOIN ActionProperty_String AS ResultAPS ON ResultAPS.id = ResultAP.id

        INNER JOIN Action FirstMoving ON FirstMoving.id = (
          SELECT min(A.id)
          FROM Action A
            INNER JOIN ActionType MovingAT ON MovingAT.flatCode = 'moving' AND A.actionType_id = MovingAT.id AND MovingAT.deleted = 0
          WHERE A.event_id = Event.id AND A.deleted = 0
        )
      WHERE
        Event.deleted = 0 AND {leavedDateCond}
      GROUP BY
        OrgStructure.id
      ) AS leaved ON leaved.id = mainTable.id

      # MOVING
      LEFT JOIN (SELECT
        OrgStructure.id                            AS id,
        count(AP.id)                               AS moving,
        count(if(Client.sex = 1, Client.id, NULL)) AS men,
        count(if(Client.sex = 2, Client.id, NULL)) AS women
      FROM
        ActionType
        INNER JOIN Action ON Action.actionType_id = ActionType.id AND Action.deleted = 0
        INNER JOIN Event ON Event.id = Action.event_id AND Event.deleted = 0
        INNER JOIN Client ON Client.id = Event.client_id AND Client.deleted = 0

        INNER JOIN ActionPropertyType AS APT ON APT.actionType_id = ActionType.id AND APT.name = 'Отделение пребывания' AND APT.deleted = 0
        INNER JOIN ActionProperty AS AP ON AP.action_id = Action.id AND AP.type_id = APT.id AND AP.deleted = 0
        INNER JOIN ActionProperty_OrgStructure AS APOS ON APOS.id = AP.id
        INNER JOIN OrgStructure ON OrgStructure.id = APOS.value
      WHERE
        ActionType.flatCode = 'moving' AND ActionType.deleted = 0 AND Action.finance_id IS NOT NULL AND {movingDateCond}
      GROUP BY
        OrgStructure.id
      ) AS moving ON moving.id = mainTable.id'''.format(
        receivedDateCond=db.joinAnd([Action['begDate'].datetimeGe(begDateTime), Action['begDate'].datetimeLe(endDateTime)]),
        movingFromDateCond=db.joinAnd([Action['begDate'].datetimeGe(begDateTime), Action['begDate'].datetimeLe(endDateTime)]),
        movingIntoDateCond=db.joinAnd([Action['endDate'].datetimeGe(begDateTime), Action['endDate'].datetimeLe(endDateTime)]),
        movingDateCond=db.joinAnd([Action['begDate'].datetimeLt(begDateTime), db.joinOr([Action['endDate'].datetimeGe(begDateTime), Action['endDate'].isNull()])]),
        leavedDateCond=db.joinAnd([Action['begDate'].datetimeGe(begDateTime), Action['begDate'].datetimeLe(endDateTime)])
    )
    return QtGui.qApp.db.query(stmt)


def selectReceivedClients(eventIdList):
    stmt = u'''
    SELECT
        OrgStructure.code      AS orgStructure,
        Client.lastName        AS lastName,
        Client.firstName       AS firstName,
        Client.patrName        AS patrName,
        Organisation.shortName AS insurer,
        CASE
          WHEN DeliveredByAPS.value LIKE 'ПМУ'   THEN 'ПМУ'
          WHEN DeliveredByAPS.value LIKE '%ДМС%' THEN 'ДМС'
          ELSE ''
        END AS channel
    FROM
      Event
      INNER JOIN Client ON Client.id = Event.client_id
      INNER JOIN ClientPolicy ON ClientPolicy.id = Event.clientPolicy_id
      INNER JOIN Organisation ON Organisation.id = ClientPolicy.insurer_id

      INNER JOIN ActionType ON ActionType.flatCode = 'received' AND ActionType.deleted = 0
      INNER JOIN Action ON Action.id = (
        SELECT MAX(A.id)
        FROM Action A
        WHERE A.event_id = Event.id AND A.actionType_id = ActionType.id AND A.deleted = 0
      )

      INNER JOIN ActionPropertyType AS APT ON APT.actionType_id = ActionType.id AND APT.name = 'Направлен в отделение' AND APT.deleted = 0
      INNER JOIN ActionProperty AS AP ON AP.action_id = Action.id AND AP.type_id = APT.id AND AP.deleted = 0
      INNER JOIN ActionProperty_OrgStructure AS APOS ON APOS.id = AP.id
      INNER JOIN OrgStructure ON OrgStructure.id = APOS.value

      INNER JOIN ActionPropertyType DeliveredByAPT ON DeliveredByAPT.name = 'Кем доставлен' AND DeliveredByAPT.actionType_id = ActionType.id AND DeliveredByAPT.deleted = 0
      LEFT JOIN ActionProperty DeliveredByAP ON DeliveredByAP.action_id = Action.id AND DeliveredByAP.type_id = DeliveredByAPT.id AND DeliveredByAP.deleted = 0
      LEFT JOIN ActionProperty_String DeliveredByAPS ON DeliveredByAPS.id = DeliveredByAP.id
    WHERE
      Event.id IN ({eventIdList})
    '''.format(eventIdList=','.join('%s' % id for id in eventIdList))
    return QtGui.qApp.db.query(stmt)


def selectDeadClients(eventIdList):
    stmt = u'''
    SELECT
        OrgStructure.code                     AS orgStructure,
        Client.lastName                       AS lastName,
        Client.firstName                      AS firstName,
        Client.patrName                       AS patrName,
        age(Client.birthDate, Leaved.begDate) AS age,
        Event.externalId                      AS externalId,
        Leaved.begDate                        AS deathTime
    FROM
      Event
      INNER JOIN Client ON Client.id = Event.client_id
      INNER JOIN ActionType ON ActionType.flatCode = 'leaved' AND ActionType.deleted = 0
      INNER JOIN Action Leaved ON Leaved.id = (
        SELECT MAX(A.id)
        FROM Action A
        WHERE A.event_id = Event.id AND A.actionType_id = ActionType.id AND A.deleted = 0
      )

      INNER JOIN ActionPropertyType AS APT ON APT.actionType_id = ActionType.id AND APT.name = 'Отделение' AND APT.deleted = 0
      INNER JOIN ActionProperty AS AP ON AP.action_id = Leaved.id AND AP.type_id = APT.id AND AP.deleted = 0
      INNER JOIN ActionProperty_OrgStructure AS APOS ON APOS.id = AP.id
      INNER JOIN OrgStructure ON OrgStructure.id = APOS.value
    WHERE
      Event.id IN ({eventIdList})
    '''.format(eventIdList=','.join('%s' % id for id in eventIdList))
    return QtGui.qApp.db.query(stmt)


class CReportMovingRVCSetupDialog(CDialogBase, Ui_ReportMovingRVCSetupDialog):

    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)


    def setTitle(self, title):
        self.setWindowTitle(title)


    def params(self):
        return {
            'curDate': self.edtDate.date()
        }


    def setParams(self, params):
        self.edtDate.setDate(params.get('curDate', QtCore.QDate.currentDate()))


class CReportMovingRVC(CReport):
    u"""
        Оперативная сводка движения больных в РСЦ
        Территориальная принадлежность: Москва
        Объект: МСК Б36
    """

    TodayBeginTime = QtCore.QTime(7, 0)
    YesterdayBeginTime = QtCore.QTime(9, 0)

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Оперативная сводка движения больных в РСЦ')


    def getSetupDialog(self, parent):
        result = CReportMovingRVCSetupDialog(parent)
        result.setTitle(self.title())
        return result


    def getDescription(self, params):
        curDate = params.get('curDate', QtCore.QDate())
        begDate, endDate = curDate.addDays(-1), curDate
        rows = []
        rows.append(u'c "{prevDay}" {prevMonth} {prevYear} г. на "{day}" {month} {year} г.'.format(
            prevDay=begDate.day(), prevMonth=QtCore.QDate.longMonthName(begDate.month()), prevYear=begDate.year(),
            day=endDate.day(), month=QtCore.QDate.longMonthName(endDate.month()), year=endDate.year()
        ))
        return rows


    def dumpParams(self, cursor, params, charFormat = QtGui.QTextCharFormat()):
        description = self.getDescription(params)

        columns = [('100?', [], CReportBase.AlignLeft)]
        table = createTable(cursor, columns, headerRowCount=len(description), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(description):
            table.setText(i, 0, row, charFormat = charFormat)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()


    def createTable(self, params, cursor):
        # 1
        headerTableColumns = [
            ('23?', [u''], CReportBase.AlignLeft)
        ] + [
            ('12?', [u''], CReportBase.AlignRight)
        ] * 4
        headerTable = createTable(cursor, headerTableColumns, cellPadding=3)  # , border=0, cellPadding=2, cellSpacing=0)
        for r in xrange(5):
            headerTable.addRow()

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()

        # 2
        mainTableColumns = [
            ('23?', [u'Отделение', u''], CReportBase.AlignLeft),
            ('12?', [u'кол-во\nкоек', u''], CReportBase.AlignRight),
            ('12?', [u'состояло\nна 9:00\nпредыдущих суток', u''], CReportBase.AlignRight),
            ('12?', [u'госпитализировано', u''], CReportBase.AlignRight),
            ('12?', [u'переведено\nиз\nдр. отдел.', u''], CReportBase.AlignRight),
            ('12?', [u'переведено\nв\nдр. отдел.', u''], CReportBase.AlignRight),
            ('12?', [u'выписано', u''], CReportBase.AlignRight),
            ('12?', [u'умерло', u''], CReportBase.AlignRight),
            ('12?', [u'состоит\nна 7:00\nтекущих суток', u''], CReportBase.AlignRight),
            ('12?', [u'кол-во\nсвободных коек', u'всего'], CReportBase.AlignRight),
            ('12?', [u'', u'муж'], CReportBase.AlignRight),
            ('12?', [u'', u'жен'], CReportBase.AlignRight),
        ]
        table = createTable(cursor, mainTableColumns, cellPadding=3)

        for r in xrange(10):
            table.addRow()

        for c in xrange(9):
            table.mergeCells(0, c, 2, 1)
        table.mergeCells(0, 9, 1, 3)
        table.mergeCells(11, 1, 1, 2)
        table.mergeCells(11, 4, 1, 8)

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()

        return headerTable, table


    def build(self, params):
        curDate = params.get('curDate', QtCore.QDate.currentDate())
        begDateTime = QtCore.QDateTime(curDate.addDays(-1), self.YesterdayBeginTime)
        endDateTime = QtCore.QDateTime(curDate, self.TodayBeginTime)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.movePosition(QtGui.QTextCursor.End)

        cursor.insertBlock()
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        cursor.setCharFormat(QtGui.QTextCharFormat())
        headerTable, mainTable = self.createTable(params, cursor)

        receptionRVC_Id = 119 # Приемное отделение РСЦ
        RVC_Id = 34           # Региональный сосудистый центр
        RVCDescendants = getOrgStructureDescendants(RVC_Id)
        EVDT_Id = 92          # Отделение рентгенэндоваскулярной диагностики и лечения

        orgStructuresRVC = [
            # (id, наименование, номер строки в таблице)
            (27, u'ОАР для больных с ОНМК', 2),
            (28, u'ОАР для больных с ОИМ', 3),
            (36, u'1-е неврологическое отделение', 4),
            (39, u'Отделение сосудистой хирургии', 5),
            (37, u'2-е кардиологическое отделение', 6),
            (38, u'2-е нейрохирургическое отделение (сосудистое)', 7),
            (118, u'Кардиологическое отделение для больных с ОИМ (ОНК)', 8)
        ]
        TherapeuticOS3 = (106, u'3-е терапевтическое отделение', 10)

        orgStructureIdsRVC = [id for id, name, row in orgStructuresRVC]
        # orgStructureIdList = [org[0] for org in orgStructuresRVC + [TherapeuticOS3]]

        query = selectData(begDateTime, endDateTime)
        self.setQueryText(forceString(query.lastQuery()))

        hospitalizationInfo = {}
        reportRows = {}
        orgStructureEvents = {}
        orgStructureCode = {}

        while query.next():
            record = query.record()
            id = forceRef(record.value('osId'))
            code = forceString(record.value('osCode'))
            # totalBeds = forceInt(record.value('totalBeds'))
            permanentBeds = forceInt(record.value('permanentBeds'))
            # involuteBed = forceInt(record.value('involuteBed'))
            menBed = forceInt(record.value('menBed'))
            womenBed = forceInt(record.value('womenBed'))
            men = forceInt(record.value('men'))
            women = forceInt(record.value('women'))
            received = forceInt(record.value('received'))
            byHimself = forceInt(record.value('byHimself'))
            refused = forceInt(record.value('refused'))
            moving = forceInt(record.value('moving'))
            movingInto = forceInt(record.value('movingInto'))
            movingFrom = forceInt(record.value('movingFrom'))
            leaved = forceInt(record.value('leaved'))
            dead = forceInt(record.value('dead'))
            eventsDMS = forceString(record.value('eventsDMS'))
            eventsPMU = forceString(record.value('eventsPMU'))
            eventsDeath = forceString(record.value('eventsDeath'))

            orgStructureCode[id] = code

            orgStructureEvents.setdefault(id, {'DMS': [], 'PMU': [], 'Death': []})
            if eventsDMS:
                orgStructureEvents[id]['DMS'].extend(map(int, eventsDMS.split(',')))
            if eventsPMU:
                orgStructureEvents[id]['PMU'].extend(map(int, eventsPMU.split(',')))
            if eventsDeath:
                orgStructureEvents[id]['Death'].extend(map(int, eventsDeath.split(',')))

            hospitalizationInfo[id] = {
                'byHimself': byHimself,
                'refused': refused
            }

            usedBeds = moving + received + movingInto - movingFrom - leaved - dead
            freeBeds = permanentBeds - usedBeds
            freeMenBeds = menBed - men
            freeWomenBeds = womenBed - women

            reportRows[id] = [
                permanentBeds,
                moving,
                received,
                movingInto,
                movingFrom,
                leaved,
                dead,
                usedBeds,
                freeBeds if freeBeds > 0 else 0,
                freeMenBeds if freeMenBeds > 0 else 0,
                freeWomenBeds if freeWomenBeds > 0 else 0
            ]

        totalRVC = [sum(data) for data in zip(*[reportRows[os[0]] for os in orgStructuresRVC])]
        totalB36 = [sum(data) for data in zip(*reportRows.itervalues())]

        hospitalizationTotal = totalB36[2]
        hospitalizationRVC = totalRVC[2]
        hospitalizationT3 = reportRows[TherapeuticOS3[0]][2]
        hospitalizationOther = hospitalizationTotal - hospitalizationRVC - hospitalizationT3

        hospitalizationByHimself = sum(hospitalizationInfo[osId]['byHimself'] for osId in hospitalizationInfo.iterkeys())
        hospitalizationRefused = sum(hospitalizationInfo[osId]['refused'] for osId in hospitalizationInfo.iterkeys())

        operationTotal, operationUrgent, coronaryTotal, coronaryUrgent = getOperations(begDateTime, endDateTime, EVDT_Id)

        headerTable.setText(0, 0, u'Обратилось в приемное отделение РСЦ')
        headerTable.setText(0, 1, countEventsByOrgStructure(begDateTime, endDateTime, receptionRVC_Id))
        headerTable.setText(1, 0, u'Госпитализировано')
        headerTable.setText(1, 1, hospitalizationTotal)
        headerTable.setText(1, 2, u'в РСЦ - {hospRVC}'.format(hospRVC=hospitalizationRVC), fontBold=True)
        headerTable.setText(1, 3, u'в 3 т/о - {hospT3}'.format(hospT3=hospitalizationT3), fontBold=True)
        headerTable.setText(1, 4, u'др. отд. - {hospOther}'.format(hospOther=hospitalizationOther), fontBold=True)
        headerTable.setText(2, 0, u'Отказ от госпитализации')
        headerTable.setText(2, 1, hospitalizationRefused)
        headerTable.setText(3, 0, u'Обратилось "Самотеком"')
        headerTable.setText(3, 1, hospitalizationByHimself)
        headerTable.setText(4, 0, u'Выполнено коронарографий')
        headerTable.setText(4, 1, coronaryTotal)
        headerTable.setText(4, 2, u'плановых - {count}'.format(count=coronaryTotal - coronaryUrgent))
        headerTable.setText(4, 3, u'экстренных - {count}'.format(count=coronaryUrgent))
        headerTable.setText(5, 0, u'Другие операции в ОРДЛ')
        headerTable.setText(5, 1, operationTotal)
        headerTable.setText(5, 2, u'плановых - {count}'.format(count=operationTotal - operationUrgent))
        headerTable.setText(5, 3, u'экстренных - {count}'.format(count=operationUrgent))

        for osId, osName, tableRow in orgStructuresRVC + [TherapeuticOS3]:
            mainTable.setText(tableRow, 0, osName, fontBold=(osId==TherapeuticOS3[0]))
            for col, cnt in enumerate(reportRows[osId]):
                mainTable.setText(tableRow, col + 1, cnt)

        mainTable.setText(9, 0, u'Итого по РСЦ:', fontBold=True)
        for col, cnt in enumerate(totalRVC):
            mainTable.setText(9, col + 1, cnt)

        mainTable.setText(11, 0, u'Госпитализировано в другие отделения ГКБ №36')
        mainTable.setText(11, 3, hospitalizationOther)

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()

        # 3

        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertText(u'Пациенты госпитализированные по каналу ПМУ/ДМС')
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()

        DMS_PMU_columns = [
            ('50?', [u'Ф.И.О. пациента'], CReportBase.AlignLeft),
            ('5?', [u'Канал (ПМУ или ДМС)'], CReportBase.AlignLeft),
            ('20?', [u'Отделение'], CReportBase.AlignLeft),
            ('25?', [u'Страх. компания'], CReportBase.AlignLeft),
        ]
        DMS_PMU_table = createTable(cursor, DMS_PMU_columns)

        receivedEvents = []
        deathEvents = []
        financeMap = {}
        receivedEventsMap = {}
        deathEventsMap = {}

        receivedClients = []
        deathClients = []

        for orgStructureId, eventsMap in orgStructureEvents.iteritems():
            if orgStructureId in orgStructureIdsRVC:
                receivedEvents.extend(eventsMap['DMS'])
                receivedEvents.extend(eventsMap['PMU'])
                deathEvents.extend(eventsMap['Death'])
                for eventId in eventsMap['DMS']:
                    financeMap[eventId] = 'DMS'
                    receivedEventsMap[eventId] = orgStructureId
                for eventId in eventsMap['PMU']:
                    financeMap[eventId] = 'PMU'
                    receivedEventsMap[eventId] = orgStructureId
                for eventId in eventsMap['Death']:
                    deathEventsMap[eventId] = orgStructureId


        if receivedClients:
            queryReceived = selectReceivedClients(receivedEvents)
            self.addQueryText(forceString(queryReceived.lastQuery()))
            while queryReceived.next():
                record = queryReceived.record()
                orgStructure = forceRef(record.value('orgStructure'))
                lastName = forceString(record.value('lastName'))
                firstName = forceString(record.value('firstName'))
                patrName = forceString(record.value('patrName'))
                insurer = forceString(record.value('insurer'))
                channel = forceString(record.value('channel'))

                name = formatName(lastName, firstName, patrName)

                receivedClients.append((name, channel, orgStructure, insurer))

        receivedClients = sorted(receivedClients, cmp=lambda x,y: cmp(x[0], y[0]))
        for row in receivedClients:
            i = DMS_PMU_table.addRow()
            DMS_PMU_table.setText(i, 0, row[0])
            DMS_PMU_table.setText(i, 1, row[1])
            DMS_PMU_table.setText(i, 2, row[2])
            DMS_PMU_table.setText(i, 3, row[3])

        cursor.insertBlock()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()

        # 4
        if deathEvents:
            queryDead = selectDeadClients(deathEvents)
            self.addQueryText(forceString(queryDead.lastQuery()))
            while queryDead.next():
                record = queryDead.record()
                orgStructure = forceString(record.value('orgStructure'))
                lastName = forceString(record.value('lastName'))
                firstName = forceString(record.value('firstName'))
                patrName = forceString(record.value('patrName'))
                age = forceInt(record.value('age'))
                externalId = forceString(record.value('externalId'))
                deathTime = forceDateTime(record.value('deathTime'))

                name = formatName(lastName, firstName, patrName)

                deathClients.append((name, age, externalId, orgStructure, deathTime))

        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertText(u'Умерло пациентов всего: {0}'.format(len(deathClients)))
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()

        deathClientsColumns = [
            ('50?', [u'Ф.И.О. пациента'], CReportBase.AlignLeft),
            ('5?', [u'Возраст'], CReportBase.AlignLeft),
            ('5?', [u'№ истории болезни'], CReportBase.AlignLeft),
            ('30?', [u'Отделение'], CReportBase.AlignLeft),
            ('10?', [u'Дата и время смерти'], CReportBase.AlignLeft),
        ]
        deathClientsTable = createTable(cursor, deathClientsColumns)

        deathClients = sorted(deathClients, cmp=lambda x,y: cmp(x[0], y[0]))
        for row in deathClients:
            i = deathClientsTable.addRow()
            deathClientsTable.setText(i, 0, row[0])
            deathClientsTable.setText(i, 1, row[1])
            deathClientsTable.setText(i, 2, row[2])
            deathClientsTable.setText(i, 3, row[3])
            deathClientsTable.setText(i, 4, row[4].toString('dd.MM.yyyy hh:mm'))

        return doc
