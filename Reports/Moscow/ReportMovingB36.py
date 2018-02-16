# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from library.DialogBase import CDialogBase
from library.Utils      import forceInt, forceRef, forceString

from Reports.Report     import CReportOrientation
from Reports.ReportBase import createTable, CReportBase
from Reports.ReportView import CPageFormat

from Ui_ReportMovingB36SetupDialog import Ui_ReportMovingB36SetupDialog


def selectData(begDateTime, endDateTime, orgStructureIds):
    db = QtGui.qApp.db
    Action = db.table('Action')
    Event = db.table('Event')
    OrgStructure = db.table('OrgStructure')

    # mos36.s11 В одном обращении может быть несколько действий "Выписка" (до 4-х)

    stmt = u'''
    SELECT
      mainTable.id             AS id,
      mainTable.beds           AS beds,
      moving.moving            AS moving,
      received.received        AS received,
      received.isUrgent        AS isUrgent,
      received.byHimself       AS byHimself,
      received.hospRefusal     AS hospRefusal,
      received.voluntaryPolicy AS voluntaryPolicy,
      movingInto.movingInto    AS movingInto,
      movingFrom.movingFrom    AS movingFrom,
      leaved.dead              AS dead,
      leaved.leavedTotal       AS leavedTotal
    FROM
      ( # MAIN
        SELECT
          OrgStructure.id                                AS id,
          count(if(OSHB.isPermanent = 1, OSHB.id, NULL)) AS beds
        FROM
          OrgStructure
          LEFT JOIN OrgStructure_HospitalBed OSHB ON OSHB.master_id = OrgStructure.id
        WHERE
          {orgStructuresCond}
        GROUP BY
          OrgStructure.id
      ) AS mainTable

      LEFT JOIN ( # MOVING
        SELECT
          APOS.value   AS id,
          count(AP.id) AS moving
        FROM
          ActionType
          INNER JOIN Action ON Action.actionType_id = ActionType.id AND Action.deleted = 0
          INNER JOIN Event ON Event.id = Action.event_id AND Event.deleted = 0
          INNER JOIN Client ON Client.id = Event.client_id

          INNER JOIN ActionPropertyType AS APT ON APT.actionType_id = ActionType.id AND APT.name = 'Отделение пребывания' AND APT.deleted = 0
          INNER JOIN ActionProperty AS AP ON AP.action_id = Action.id AND AP.type_id = APT.id AND AP.deleted = 0
          INNER JOIN ActionProperty_OrgStructure AS APOS ON APOS.id = AP.id
        WHERE
          ActionType.flatCode = 'moving' AND ActionType.deleted = 0 AND Action.finance_id IS NOT NULL AND {movingDateCond}
        GROUP BY
          APOS.value
      ) AS moving ON moving.id = mainTable.id

      LEFT JOIN ( # RECEIVED
        SELECT
          APOS.value                                                          AS id,
          count(AP.id)                                                        AS received,
          count(if(Received.isUrgent = 1, Received.id, NULL))                 AS isUrgent,
          count(if(DeliveredByAPS.value LIKE '%самотёк%', Received.id, NULL)) AS byHimself,
          count(if(HospRefusalAPS.value IS NOT NULL, Received.id, NULL))      AS hospRefusal,
          count(if(rbFinance.code = '3', Received.id, NULL))                  AS voluntaryPolicy
        FROM
          Event

          INNER JOIN ActionType ON ActionType.flatCode = 'received' AND ActionType.deleted = 0
          INNER JOIN Action Received ON Received.id = (
            SELECT Action.id
            FROM Action
            WHERE Action.event_id = Event.id AND Action.actionType_id = ActionType.id AND Action.deleted = 0 AND {receivedDateCond}
            ORDER BY Action.begDate DESC
            LIMIT 0, 1
          ) # mos36.s11: возможно несколько действий "Постпуление" подряд

          INNER JOIN ActionPropertyType AS APT ON APT.actionType_id = ActionType.id AND APT.name = 'Направлен в отделение' AND APT.deleted = 0
          INNER JOIN ActionProperty AS AP ON AP.action_id = Received.id AND AP.type_id = APT.id AND AP.deleted = 0
          INNER JOIN ActionProperty_OrgStructure AS APOS ON APOS.id = AP.id

          INNER JOIN ActionPropertyType DeliveredByAPT ON DeliveredByAPT.name = 'Кем доставлен' AND DeliveredByAPT.actionType_id = ActionType.id AND DeliveredByAPT.deleted = 0
          LEFT JOIN ActionProperty DeliveredByAP ON DeliveredByAP.action_id = Received.id AND DeliveredByAP.type_id = DeliveredByAPT.id AND DeliveredByAP.deleted = 0
          LEFT JOIN ActionProperty_String DeliveredByAPS ON DeliveredByAPS.id = DeliveredByAP.id

          INNER JOIN ActionPropertyType HospRefusalAPT ON HospRefusalAPT.name = 'Причина отказа от госпитализации' AND HospRefusalAPT.actionType_id = ActionType.id AND HospRefusalAPT.deleted = 0
          LEFT JOIN ActionProperty HospRefusalAP ON HospRefusalAP.action_id = Received.id AND HospRefusalAP.type_id = HospRefusalAPT.id AND HospRefusalAP.deleted = 0
          LEFT JOIN ActionProperty_String HospRefusalAPS ON HospRefusalAPS.id = HospRefusalAP.id

          INNER JOIN Client ON Client.id = Event.client_id

          LEFT JOIN rbFinance ON rbFinance.id = Received.finance_id

          INNER JOIN Action FirstMoving ON FirstMoving.id = (
            SELECT min(A.id)
            FROM Action A
              INNER JOIN ActionType MovingAT ON MovingAT.flatCode = 'moving' AND A.actionType_id = MovingAT.id AND MovingAT.deleted = 0
            WHERE A.event_id = Event.id AND A.deleted = 0
          )
        WHERE
          Event.deleted = 0
        GROUP BY
          APOS.value
      ) AS received ON received.id = mainTable.id

      LEFT JOIN ( # MOVING INTO
        SELECT
          APOS.value   AS id,
          count(AP.id) AS movingInto
        FROM
          ActionType
          INNER JOIN Action ON Action.actionType_id = ActionType.id AND Action.deleted = 0
          INNER JOIN Event ON Event.id = Action.event_id AND Event.deleted = 0
          INNER JOIN Client ON Client.id = Event.client_id

          INNER JOIN ActionPropertyType AS APT ON APT.actionType_id = ActionType.id AND APT.name = 'Переведен в отделение' AND APT.deleted = 0
          INNER JOIN ActionProperty AS AP ON AP.action_id = Action.id AND AP.type_id = APT.id AND AP.deleted = 0
          INNER JOIN ActionProperty_OrgStructure AS APOS ON APOS.id = AP.id
        WHERE
          ActionType.flatCode = 'moving' AND ActionType.deleted = 0 AND {movingIntoDateCond}
        GROUP BY
          APOS.value
      ) AS movingInto ON movingInto.id = mainTable.id

      LEFT JOIN ( # MOVING FROM
        SELECT
          APOS.value   AS id,
          count(AP.id) AS movingFrom
        FROM
          ActionType
          INNER JOIN Action ON Action.actionType_id = ActionType.id AND Action.deleted = 0
          INNER JOIN Event ON Event.id = Action.event_id AND Event.deleted = 0
          INNER JOIN Client ON Client.id = Event.client_id

          INNER JOIN ActionPropertyType AS APT ON APT.actionType_id = ActionType.id AND APT.name = 'Переведен из отделения' AND APT.deleted = 0
          INNER JOIN ActionProperty AS AP ON AP.action_id = Action.id AND AP.type_id = APT.id AND AP.deleted = 0
          INNER JOIN ActionProperty_OrgStructure AS APOS ON APOS.id = AP.id
        WHERE
          ActionType.flatCode = 'moving' AND ActionType.deleted = 0 AND {movingFromDateCond}
        GROUP BY
          APOS.value
      ) AS movingFrom ON movingFrom.id = mainTable.id

      LEFT JOIN ( # LEAVED
        SELECT
          APOS.value                                              AS id,
          count(AP.id)                                            AS leavedTotal,
          count(if(ResultAPS.value = 'умер', ResultAPS.id, NULL)) AS dead
        FROM
          Event

          INNER JOIN ActionType ON ActionType.flatCode = 'leaved' AND ActionType.deleted = 0
          INNER JOIN Action LeavedAction ON LeavedAction.id = (
            SELECT Action.id
            FROM Action
            WHERE Action.event_id = Event.id AND Action.actionType_id = ActionType.id AND Action.deleted = 0 AND {leavedDateCond}
            ORDER BY Action.begDate DESC
            LIMIT 0, 1
          ) # mos36.s11: возможно несколько действий "Выписка" подряд

          INNER JOIN Client ON Client.id = Event.client_id

          INNER JOIN ActionPropertyType AS APT ON APT.actionType_id = ActionType.id AND APT.name = 'Отделение' AND APT.deleted = 0
          INNER JOIN ActionProperty AS AP ON AP.action_id = LeavedAction.id AND AP.type_id = APT.id AND AP.deleted = 0
          INNER JOIN ActionProperty_OrgStructure AS APOS ON APOS.id = AP.id

          LEFT JOIN ActionPropertyType AS ResultAPT ON ResultAPT.actionType_id = ActionType.id AND ResultAPT.name = 'Исход госпитализации' AND ResultAPT.deleted = 0
          LEFT JOIN ActionProperty AS ResultAP ON ResultAP.action_id = LeavedAction.id AND ResultAP.type_id = ResultAPT.id AND ResultAPT.deleted = 0
          LEFT JOIN ActionProperty_String AS ResultAPS ON ResultAPS.id = ResultAP.id

          INNER JOIN Action FirstMoving ON FirstMoving.id = (
            SELECT min(A.id)
            FROM Action A
              INNER JOIN ActionType MovingAT ON MovingAT.flatCode = 'moving' AND A.actionType_id = MovingAT.id AND MovingAT.deleted = 0
            WHERE A.event_id = Event.id AND A.deleted = 0
          )
      WHERE
        Event.deleted = 0
      GROUP BY
        APOS.value
      ) AS leaved ON leaved.id = mainTable.id
    '''.format(
        orgStructuresCond=OrgStructure['id'].inlist(orgStructureIds),
        eventSetDateCond=db.joinAnd([Event['setDate'].datetimeGe(begDateTime), Event['setDate'].datetimeLt(endDateTime)]),
        receivedDateCond=db.joinAnd([Action['begDate'].datetimeGe(begDateTime), Action['begDate'].datetimeLt(endDateTime)]),
        movingFromDateCond=db.joinAnd([Action['begDate'].datetimeGe(begDateTime), Action['begDate'].datetimeLt(endDateTime)]),
        movingIntoDateCond=db.joinAnd([Action['endDate'].datetimeGe(begDateTime), Action['endDate'].datetimeLt(endDateTime)]),
        movingDateCond=db.joinAnd([Action['begDate'].datetimeLt(begDateTime), db.joinOr([Action['endDate'].datetimeGe(begDateTime),
                                                                                         Action['endDate'].isNull()])]),
        leavedDateCond=db.joinAnd([Action['begDate'].datetimeGe(begDateTime), Action['begDate'].datetimeLt(endDateTime)])
    )

    return QtGui.qApp.db.query(stmt)


class CReportMovingB36SetupDialog(CDialogBase, Ui_ReportMovingB36SetupDialog):

    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)


    def setTitle(self, title):
        self.setWindowTitle(title)


    def params(self):
        return {
            'curDate': self.edtDate.date(),
            'begTime': self.edtBegTime.time()
        }


    def setParams(self, params):
        self.edtDate.setDate(params.get('curDate', QtCore.QDate.currentDate()))
        self.edtBegTime.setTime(params.get('begTime', QtCore.QTime()))


class CReportMovingB36(CReportOrientation):
    u"""
        Оперативная сводка движения больных
        Территориальная принадлежность: Москва
        Объект: МСК Б36
    """

    defaultBegTime = QtCore.QTime(6, 0)


    def __init__(self, parent):
        CReportOrientation.__init__(self, parent, QtGui.QPrinter.Landscape)
        self.setTitle(u'Оперативная сводка движения больных')


    def getSetupDialog(self, parent):
        result = CReportMovingB36SetupDialog(parent)
        result.setTitle(self.title())
        return result

    def getPageFormat(self):
        return CPageFormat(pageSize=CPageFormat.A4, orientation=CPageFormat.Landscape, leftMargin=10.0, topMargin=10.0, rightMargin=10.0, bottomMargin=10.0)


    def getDescription(self, params):
        curDate = params.get('curDate', QtCore.QDate())
        begDate, endDate = curDate.addDays(-1), curDate
        rows = []
        rows.append(u'С %02d/%02d/%d НА %02d/%02d/%d' % (begDate.day(), begDate.month(), begDate.year(), endDate.day(), endDate.month(), endDate.year()))
        return rows


    def dumpParams(self, cursor, params, charFormat = QtGui.QTextCharFormat()):
        description = self.getDescription(params)

        columns = [('100%', [], CReportBase.AlignCenter)]
        table = createTable(cursor, columns, headerRowCount=len(description), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(description):
            table.setText(i, 0, row, charFormat = charFormat)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()


    def build(self, params):
        curDate = params.get('curDate', QtCore.QDate.currentDate())
        begTime = params.get('begTime', self.defaultBegTime)
        begDateTime = QtCore.QDateTime(curDate.addDays(-1), begTime)
        endDateTime = QtCore.QDateTime(curDate, begTime)

        fontSizeHeader = 7
        fontSize = 6.25
        charFormatHeader = CReportBase.TableHeader
        charFormatHeader.setFontPointSize(fontSizeHeader)
        charFormatBody = CReportBase.TableBody
        charFormatBody.setFontPointSize(fontSize)
        charFormatBodyBold = CReportBase.TableBody
        charFormatBodyBold.setFontWeight(QtGui.QFont.Bold)
        charFormatBodyBold.setFontPointSize(fontSize)

        doc = QtGui.QTextDocument()
        bf = QtGui.QTextBlockFormat()
        bf.setAlignment(QtCore.Qt.AlignCenter)
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(charFormatHeader)
        cursor.setBlockFormat(bf)
        cursor.insertText(self.title().upper())
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        cursor.setCharFormat(charFormatBody)
        tableColumns = [
            ('35%', u'Отделение', CReportBase.AlignLeft),
            ('5%', u'коек', CReportBase.AlignCenter),
            ('5%', u'состояло', CReportBase.AlignCenter),
            ('5%', u'обрат', CReportBase.AlignCenter),
            ('5%', u'госп', CReportBase.AlignCenter),
            ('5%', u'отказ', CReportBase.AlignCenter),
            ('5%', u'самотёк', CReportBase.AlignCenter),
            ('5%', u'пер +', CReportBase.AlignCenter),
            ('5%', u'пер -', CReportBase.AlignCenter),
            ('5%', u'вып', CReportBase.AlignCenter),
            ('5%', u'умерло', CReportBase.AlignCenter),
            ('5%', u'сост', CReportBase.AlignCenter),
            ('5%', u'ДМС', CReportBase.AlignCenter),
            ('5%', u'коек св.', CReportBase.AlignRight)
        ]
        table = createTable(cursor, tableColumns, charFormat=charFormatBodyBold, cellPadding=1)

        orgStructuresByProfile = [
            (u'Терапевтический профиль', [
                (u'ОНК', 118),
                (u'2-Кардиология', 37),
                (u'3-Терапия', 106),
                (u'Неврология', 36)
            ]),
            (u'Хирургический профиль', [
                (u'Эндокринная хирургия', 107),
                (u'2 Х/О', 13),
                (u'Сосудистая хирургия', 39),
                (u'Ожоговое', 32),
                (u'Нейрохирургическое', 15),
                (u'Нейрохирургическое 2 (сосудистое)', 38),
                (u'1-Травматология', 17),
                (u'2-Травматология', 18),
                (u'1-ЧЛХ', 19),
                (u'2-ЧЛХ', 20),
                (u'Офтальмологическое отделение', 104),
                (u'Оториноларингологическое', 16)
            ]),
            (u'Гинекологический профиль', [
                (u'Гинекологическое', 68)
            ]),
            (u'Реанимационный профиль', [
                (u'ОАР общехирургического профиля', 25),
                (u'ОАР нейрохирургического профиля', 26),
                (u'ОАР кардиологического профиля', 27),
                (u'ОАР неврологического профиля', 28),
                (u'ОАР ожогового центра', 108),
                (u'ОАР с палатами пробуждения', 29)
            ]),
            (u'Итого за АГЦ', [
                (u'Отделение патологии беременности', 238),
                (u'1 акушерское', 230),
                (u'2 акушерское', 231),
                (u'ОАР акушерского профиля', 241),
                (u'ОАР новорожденных', 242)
            ])
        ]

        orgStructuresForTotal = [
            (u'Дневной стационар', 78),
            (u'Отделение новорожденных', 237),
        ]

        orgStructureLDO =  (u'Приемное отделение (Диагностические койки)', 264)

        receptionOrgStructures = [
            (u'Приемное отделение 9 корпус', 255),
            (u'Приемное отделение Ожог. центра', 99),
            (u'Приемное отделение РСЦ', 90),
            (u'Приемное отделение АГЦ', 240)
        ]

        orgStructureIds =  [orgStructure[1] for orgStructure in reduce(lambda x, y: x+y, [profileName[1] for profileName in orgStructuresByProfile])] + \
                           [orgStructure[1] for orgStructure in orgStructuresForTotal] + \
                           [orgStructureLDO[1]] + \
                           [orgStructure[1] for orgStructure in receptionOrgStructures]

        query = selectData(begDateTime, endDateTime, orgStructureIds)
        self.setQueryText(forceString(query.lastQuery()))

        reportData = {}
        urgencyData = {}

        while query.next():
            record = query.record()
            id = forceRef(record.value('id'))
            beds = forceInt(record.value('beds'))
            moving = forceInt(record.value('moving'))
            received = forceInt(record.value('received'))
            isUrgent = forceInt(record.value('isUrgent'))
            byHimself = forceInt(record.value('byHimself'))
            hospRefusal = forceInt(record.value('hospRefusal'))
            voluntaryPolicy = forceInt(record.value('voluntaryPolicy'))
            movingInto = forceInt(record.value('movingInto'))
            movingFrom = forceInt(record.value('movingFrom'))
            dead = forceInt(record.value('dead'))
            leavedTotal = forceInt(record.value('leavedTotal'))

            hosp = received - hospRefusal
            leaved = leavedTotal - dead
            inHosp = moving + received + movingInto - movingFrom - leavedTotal
            freeBeds = beds - inHosp

            reportData[id] = (
                beds,
                moving,
                received,
                hosp,
                hospRefusal,
                byHimself,
                movingInto,
                movingFrom,
                leaved,
                dead,
                inHosp,
                voluntaryPolicy,
                freeBeds
            )
            urgencyData[id] = isUrgent

        def printRow(table, name, row, charFormat=charFormatBody):
            i = table.addRow()
            table.setText(i, 0, name, charFormat=charFormatBodyBold)
            for j, cnt in enumerate(row):
                table.setText(i, j + 1, cnt, charFormat)

        totalByHospital = []
        for profileName, orgStructures in orgStructuresByProfile:
            totalByProfile = []
            for orgStructureName, orgStructureId in orgStructures:
                row = reportData[orgStructureId]
                totalByProfile.append(row)
                printRow(table, orgStructureName, row, charFormatBody)
            profileTotal = [sum(data) for data in zip(*totalByProfile)]
            totalByHospital.append(profileTotal)
            printRow(table, profileName, profileTotal, charFormatBodyBold)

        total = [sum(data) for data in zip(*totalByHospital)]
        printRow(table, u'БОЛЬНИЦА', total, charFormatBodyBold)

        for orgStructureName, orgStructureId in orgStructuresForTotal:
            row = reportData[orgStructureId]
            totalByHospital.append(row)
            printRow(table, orgStructureName, row, charFormatBody)

        total = [sum(data) for data in zip(*totalByHospital)]
        printRow(table, u'ИТОГО', total, charFormatBodyBold)

        i = table.addRow()
        orgStructureName, orgStructureId = orgStructureLDO
        table.setText(i, 0, orgStructureName)
        for col, cnt in enumerate(reportData[orgStructureId]):
            table.setText(i, col + 1, cnt)

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.setBlockFormat(bf)

        tableReceptionsColumns = [
            ('35?', u'', CReportBase.AlignLeft),
            ('16?', u'ОБРАТИЛОСЬ', CReportBase.AlignCenter),
            ('16?', u'ГОСПИТАЛИЗИРОВАНО', CReportBase.AlignCenter),
            ('16?', u'ИЗ НИХ ПЛАН', CReportBase.AlignCenter),
            ('16?', u'ОТКАЗ', CReportBase.AlignCenter)
        ]
        tableReceptions = createTable(cursor, tableReceptionsColumns, border=0, cellPadding=2, cellSpacing=0)

        totalByReceptions = []
        for orgStructureName, orgStructureId in receptionOrgStructures:
            data = reportData[orgStructureId]
            tableRow = [
                data[2],
                data[3],
                urgencyData[orgStructureId],
                data[4]
            ]
            totalByReceptions.append(tableRow)
            printRow(tableReceptions, orgStructureName.upper(), tableRow, charFormatBody)
        total = [sum(data) for data in zip(*totalByReceptions)]
        printRow(tableReceptions, u'ИТОГО', total, charFormatBody)

        return doc
