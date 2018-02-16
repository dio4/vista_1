# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Reports.Moscow.Dispatching.DispatchingSetupDialog import CDispatchingSetupDialog
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase
from library.Utils      import forceInt, forceRef, forceString


def selectData(date, begTime, orgStructureIdList):
    db = QtGui.qApp.db

    begDateTime = QtCore.QDateTime(date.addDays(-1), begTime)
    endDateTime = QtCore.QDateTime(date, begTime)

    Event = db.table('Event')
    Received = db.table('Action').alias('Received')
    OrgStructure = db.table('OrgStructure')

    dateCond = [
        Event['deleted'].eq(0),
        Received['begDate'].datetimeGe(begDateTime),
        Received['endDate'].datetimeLt(endDateTime)
    ]

    stmt = u'''
    SELECT
      OrgStructure.id      AS id,
      T.planned            AS planned,
      T.byHimself          AS byHimself,
      T.byVMP              AS byVMP,
      T.byMoving           AS byMoving,
      T.byDMS              AS byDMS,
      T.byPMU              AS byPMU,
      T.withoutOrderNumber AS withoutOrderNumber,
      T.hospRefusal        AS hospRefusal,
      T.nonMoscow          AS nonMoscow
    FROM
        OrgStructure
        LEFT JOIN (
        SELECT
          OrgStructureAPOS.value                                                     AS id,
          count(if(Received.isUrgent = 0,                        Received.id, NULL)) AS planned,
          count(if(DeliveredByAPS.value LIKE '%самотёк%',        Received.id, NULL)) AS byHimself,
          count(if(DeliveredByAPS.value LIKE '%ВМП%',            Received.id, NULL)) AS byVMP,
          count(if(DeliveredByAPS.value LIKE '%Перевод из ЛПУ%', Received.id, NULL)) AS byMoving,
          count(if(rbFinance.code = 3,                           Received.id, NULL)) AS byDMS,
          count(if(rbFinance.code = 4,                           Received.id, NULL)) AS byPMU,
          count(if(OrderNumberAPS.value IS NULL,                 Received.id, NULL)) AS withoutOrderNumber,
          count(if(HospRefusalAPS.value IS NOT NULL,             Received.id, NULL)) AS hospRefusal,
          count(if(LEFT(AddressHouse.KLADRCode, 2) != 77,        Received.id, NULL)) AS nonMoscow
        FROM
          Event
          INNER JOIN ActionType ReceivedAT ON ReceivedAT.flatCode = 'received' AND ReceivedAT.deleted = 0
          INNER JOIN Action Received ON Received.id = (SELECT MAX(A.id) FROM Action A WHERE A.event_id = Event.id AND A.actionType_id = ReceivedAT.id AND A.deleted = 0)

          INNER JOIN Client ON Client.id = Event.client_id AND Client.deleted = 0
          LEFT JOIN ClientAddress ON ClientAddress.id = getClientRegAddressId(Client.id)
          LEFT JOIN Address ON Address.id = ClientAddress.address_id AND Address.deleted = 0
          LEFT JOIN AddressHouse ON AddressHouse.id = Address.house_id

          INNER JOIN ActionPropertyType OrgStructureAPT ON OrgStructureAPT.name = 'Направлен в отделение' AND OrgStructureAPT.actionType_id = ReceivedAT.id AND OrgStructureAPT.deleted = 0
          INNER JOIN ActionProperty OrgStructureAP ON OrgStructureAP.action_id = Received.id AND OrgStructureAP.type_id = OrgStructureAPT.id AND OrgStructureAP.deleted = 0
          INNER JOIN ActionProperty_OrgStructure OrgStructureAPOS ON OrgStructureAPOS.id = OrgStructureAP.id

          LEFT JOIN ActionPropertyType DeliveredByAPT ON DeliveredByAPT.name = 'Кем доставлен' AND DeliveredByAPT.actionType_id = ReceivedAT.id AND DeliveredByAPT.deleted = 0
          LEFT JOIN ActionProperty DeliveredByAP ON DeliveredByAP.action_id = Received.id AND DeliveredByAP.type_id = DeliveredByAPT.id AND DeliveredByAP.deleted = 0
          LEFT JOIN ActionProperty_String DeliveredByAPS ON DeliveredByAPS.id = DeliveredByAP.id

          LEFT JOIN ActionPropertyType OrderNumberAPT ON OrderNumberAPT.name = '№ Наряда' AND OrderNumberAPT.actionType_id = ReceivedAT.id AND OrderNumberAPT.deleted = 0
          LEFT JOIN ActionProperty OrderNumberAP ON OrderNumberAP.action_id = Received.id AND OrderNumberAP.type_id = OrderNumberAPT.id AND OrderNumberAP.deleted = 0
          LEFT JOIN ActionProperty_String OrderNumberAPS ON OrderNumberAPS.id = OrderNumberAP.id

          LEFT JOIN ActionPropertyType HospRefusalAPT ON HospRefusalAPT.name = 'Причина отказа от госпитализации' AND HospRefusalAPT.actionType_id = ReceivedAT.id AND HospRefusalAPT.deleted = 0
          LEFT JOIN ActionProperty HospRefusalAP ON HospRefusalAP.action_id = Received.id AND HospRefusalAP.type_id = HospRefusalAPT.id AND HospRefusalAP.deleted = 0
          LEFT JOIN ActionProperty_String HospRefusalAPS ON HospRefusalAPS.id = HospRefusalAP.id

          LEFT JOIN rbFinance ON rbFinance.id = Received.finance_id
        WHERE
          {dateCond}
        GROUP BY
          OrgStructureAPOS.value) T ON T.id = OrgStructure.id
    WHERE
        {orgStructureCond}
    '''.format(dateCond=db.joinAnd(dateCond),
               orgStructureCond=OrgStructure['id'].inlist(orgStructureIdList))

    return db.query(stmt)


class CDispatchingByHospChannelsReport(CReport):
    u"""
        Каналы госпитализации
        Территориальная принадлежность: Москва
        Объект: МСК Б36
    """

    def __init__(self, parent=None):
        CReport.__init__(self, parent)
        self.setTitle(u'Каналы госпитализации')


    def getSetupDialog(self, parent):
        result = CDispatchingSetupDialog(parent)
        result.setTitle(self.title())
        return result


    def build(self, params):
        date = params.get('date', QtCore.QDate())
        begTime = params.get('begTime', QtCore.QTime())

        orgStructures  = [
            (u'Офтальм. отд.',        105),
            (u'Дневной ст. офтальм.', 101),
            (u'Дневной ст.',           78),
            (u'Эндохир.',             107),
            (u'2 хирург.',             13),
            (u'Гинек. отд.',           68),
            (u'ЛОР',                   16),
            (u'1 ЧЛХ',                 19),
            (u'2 ЧЛХ',                 20),
            (u'1 травма',              17),
            (u'2 травма',              18),
            (u'НХО 1',                 15),
            (u'НХО 2 (сосуд)',         38),
            (u'ОСХ',                   39),
            (u'3 терап.',             106),
            (u'2 кард.',               37),
            (u'ОАРКП',                 27),
            (u'ОАРОХП',                25),
            (u'Неврол.',               36),
            (u'ОНК',                  118),
            (u'Ожогов.',               32),
            (u'ОАРНХП',                26),
            (u'ОАРНП',                 28)
        ]
        orgStructureIdList = [id for name, id in orgStructures]

        reportData = {}
        hospRefusalTotal = 0
        query = selectData(date, begTime, orgStructureIdList)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            id = forceRef(record.value('id'))
            planned = forceInt(record.value('planned'))
            byHimself = forceInt(record.value('byHimself'))
            byVMP = forceInt(record.value('byVMP'))
            byMoving = forceInt(record.value('byMoving'))
            byDMS = forceInt(record.value('byDMS'))
            byPMU = forceInt(record.value('byPMU'))
            withoutOrderNumber = forceInt(record.value('withoutOrderNumber'))
            hospRefusal = forceInt(record.value('hospRefusal'))
            nonMoscow = forceInt(record.value('nonMoscow'))

            reportData[id] = (
                planned,
                0, # Ф2
                byHimself,
                withoutOrderNumber,
                byVMP,
                byPMU,
                byDMS,
                nonMoscow,
                byMoving
            )
            hospRefusalTotal += hospRefusal


        doc = QtGui.QTextDocument()

        bf = QtGui.QTextBlockFormat()
        bf.setAlignment(QtCore.Qt.AlignCenter)

        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReport.ReportTitle)
        cursor.setBlockFormat(bf)
        cursor.insertText(u'КАНАЛЫ ГОСПИТАЛИЗАЦИИ ЗА {date}'.format(date=forceString(date.toString('dd.MM.yyyy'))))
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()

        tableColumns = [
            ('10%', u'Отдел.', CReportBase.AlignLeft),
            ('10%', u'План', CReportBase.AlignRight),
            ('10%', u'Ф2', CReportBase.AlignRight),
            ('10%', u'Самотёк', CReportBase.AlignRight),
            ('10%', u'П-ка без № наряда', CReportBase.AlignRight),
            ('10%', u'ВМП', CReportBase.AlignRight),
            ('10%', u'ПМУ', CReportBase.AlignRight),
            ('10%', u'ДМС', CReportBase.AlignRight),
            ('10%', u'Иног.', CReportBase.AlignRight),
            ('10%', u'Перевод', CReportBase.AlignRight),
        ]
        table = createTable(cursor, tableColumns)

        for name, id  in orgStructures:
            i = table.addRow()
            table.setText(i, 0, name, fontBold=True)
            for j, data in enumerate(reportData[id]):
                table.setText(i, j+1, data)

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()

        cursor.setCharFormat(CReport.ReportSubTitle)
        cursor.insertText(u'Отказные {refusal}'.format(refusal=hospRefusalTotal))

        return doc
