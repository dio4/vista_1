# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Reports.Moscow.Dispatching.DispatchingSetupDialog import CDispatchingSetupDialog
from Reports.Report     import CReport
from Reports.ReportBase import createTable
from library.Utils      import forceInt, forceRef, forceString


def selectReceived(date, begTime):
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

    Client = db.table('Client')
    ClientSocStatus = db.table('ClientSocStatus')
    SocStatusType = db.table('rbSocStatusType')

    def getSocStatusTypeCond(code):
        queryTable = ClientSocStatus.innerJoin(SocStatusType, [SocStatusType['code'].like(code),
                                                               SocStatusType['id'].eq(ClientSocStatus['socStatusType_id'])])
        return db.existsStmt(queryTable, [ClientSocStatus['client_id'].eq(Client['id']),
                                          ClientSocStatus['deleted'].eq(0)])

    orphanCond = getSocStatusTypeCond(u'с12')  # Сирота
    homelessCond = getSocStatusTypeCond(u'с10')  # БОМЖ

    stmt = u'''
    SELECT
      OrgStructure.id      AS id,
      T.received           AS received,
      T.planned            AS planned,
      T.refused            AS refused,
      T.byEmergency        AS byEmergency,
      T.receivedAlcohol    AS receivedAlcohol,
      T.refusedAlcohol     AS refusedAlcohol,
      T.receivedOrphan     AS receivedOrphan,
      T.refusedOrphan      AS refusedOrphan,
      T.receivedHomeless   AS receivedHomeless,
      T.refusedHomeless    AS refusedHomeless
    FROM
        OrgStructure
        LEFT JOIN (
        SELECT
          OrgStructureAPOS.value                                                                                    AS id,
          count(Received.id)                                                                                        AS received,
          count(if(Received.isUrgent = 0, Received.id, NULL))                                                       AS planned,
          count(if(HospRefusalAPS.value IS NOT NULL,  Received.id, NULL))                                           AS refused,
          count(if(DeliveredByAPS.value LIKE '%скорая помощь%', Received.id, NULL))                                 AS byEmergency,
          count(if(IntoxicationAPS.value = 'Алкогольного', Received.id, NULL))                                      AS receivedAlcohol,
          count(if(IntoxicationAPS.value = 'Алкогольного' AND HospRefusalAPS.value IS NOT NULL, Received.id, NULL)) AS refusedAlcohol,
          count(if({orphanCond}, Received.id, NULL))                                                                AS receivedOrphan,
          count(if({orphanCond} AND HospRefusalAPS.value IS NOT NULL, Received.id, NULL))                           AS refusedOrphan,
          count(if({homelessCond}, Received.id, NULL))                                                              AS receivedHomeless,
          count(if({homelessCond} AND HospRefusalAPS.value IS NOT NULL, Received.id, NULL))                         AS refusedHomeless
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

          LEFT JOIN ActionPropertyType IntoxicationAPT ON IntoxicationAPT.name = 'Доставлен в состоянии опьянения' AND IntoxicationAPT.actionType_id = ReceivedAT.id AND IntoxicationAPT.deleted = 0
          LEFT JOIN ActionProperty IntoxicationAP ON IntoxicationAP.action_id = Received.id AND IntoxicationAP.type_id = IntoxicationAPT.id AND IntoxicationAP.deleted = 0
          LEFT JOIN ActionProperty_String IntoxicationAPS ON IntoxicationAPS.id = IntoxicationAP.id

          LEFT JOIN ActionPropertyType HospRefusalAPT ON HospRefusalAPT.name = 'Причина отказа от госпитализации' AND HospRefusalAPT.actionType_id = ReceivedAT.id AND HospRefusalAPT.deleted = 0
          LEFT JOIN ActionProperty HospRefusalAP ON HospRefusalAP.action_id = Received.id AND HospRefusalAP.type_id = HospRefusalAPT.id AND HospRefusalAP.deleted = 0
          LEFT JOIN ActionProperty_String HospRefusalAPS ON HospRefusalAPS.id = HospRefusalAP.id

#           LEFT JOIN rbFinance ON rbFinance.id = Received.finance_id
        WHERE
          {dateCond}
        GROUP BY
          OrgStructureAPOS.value) T ON T.id = OrgStructure.id
    WHERE
        {orgStructureCond}
    '''.format(dateCond=db.joinAnd(dateCond),
               orgStructureCond=OrgStructure['deleted'].eq(0),
               orphanCond=orphanCond,
               homelessCond=homelessCond)

    return db.query(stmt)


class CDispatching3Report(CReport):
    u""""
        Диспетчерская
        Территориальная принадлежность: Москва
        Объект: МСК Б36
    """

    def __init__(self, parent=None):
        CReport.__init__(self, parent)
        self.setTitle(u'Диспетчерская')


    def getSetupDialog(self, parent):
        result = CDispatchingSetupDialog(parent)
        result.setTitle(self.title())
        return result


    def build(self, params):
        date = params.get('date', QtCore.QDate())
        begTime = params.get('begTime', QtCore.QTime())

        doc = QtGui.QTextDocument()

        bf = QtGui.QTextBlockFormat()
        bf.setAlignment(QtCore.Qt.AlignCenter)

        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReport.ReportTitle)
        cursor.setBlockFormat(bf)
        cursor.insertText(u'ДИСПЕТЧЕРСКАЯ')
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()


        fields = ('received', 'planned', 'refused', 'byEmergency',
                  'receivedAlcohol', 'refusedAlcohol',
                  'receivedOrphan', 'refusedOrphan',
                  'receivedHomeless', 'refusedHomeless')

        reportData = {}
        query = selectReceived(date, begTime)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            id = forceRef(record.value('id'))
            reportData[id] = dict([(field, forceInt(record.value(field))) for field in fields])

        def getSum(field):
            return sum([reportData[id][field] for id in reportData])

        received = getSum('received')
        refused = getSum('refused')
        hospital = received - refused
        receivedAlcohol = getSum('receivedAlcohol')
        refusedAlcohol = getSum('refusedAlcohol')
        hospitalAlcohol = receivedAlcohol - refusedAlcohol
        receivedOrphan = getSum('receivedOrphan')
        refusedOrphan = getSum('refusedOrphan')
        hospitalOrhpan = receivedOrphan - refusedOrphan
        receivedHomeless = getSum('receivedHomeless')
        refusedHomeless = getSum('refusedHomeless')
        hospitalHomeless = receivedHomeless - refusedHomeless
        planned = getSum('planned')
        byEmergency = getSum('byEmergency')

        tableColumns = [
            ('50%', u'', CReport.AlignLeft),
            ('50%', u'', CReport.AlignLeft)
        ]
        table = createTable(cursor, tableColumns, cellPadding=3, border=0)

        for _ in xrange(8):
            table.addRow()

        table.mergeCells(0, 0, 1, 2)
        table.mergeCells(1, 0, 1, 2)
        table.mergeCells(2, 0, 1, 2)
        table.mergeCells(3, 0, 2, 1)
        table.mergeCells(5, 0, 2, 1)
        table.mergeCells(7, 0, 2, 1)

        table.setText(0, 0, u'Количество обратившихся: {cnt}'.format(cnt=received), fontBold=True)
        table.setText(1, 0, u'Количество госпитализированных: {cnt}'.format(cnt=hospital), fontBold=True)
        table.setText(2, 0, u'Количество отказных: {cnt}'.format(cnt=refused), fontBold=True)
        table.setText(3, 0, u'В алкогольном опьянении: {cnt}'.format(cnt=receivedAlcohol), fontBold=True)
        table.setText(3, 1, u'Госпитализированные: {cnt}'.format(cnt=hospitalAlcohol), fontBold=True)
        table.setText(4, 1, u'Отказные: {cnt}'.format(cnt=refusedAlcohol), fontBold=True)
        table.setText(5, 0, u'БОМЖИ: {cnt}'.format(cnt=receivedHomeless), fontBold=True)
        table.setText(5, 1, u'Госпитализированные: {cnt}'.format(cnt=hospitalHomeless), fontBold=True)
        table.setText(6, 1, u'Отказные: {cnt}'.format(cnt=refusedHomeless), fontBold=True)
        table.setText(7, 0, u'БЕСПРИЗОРНИКИ: {cnt}'.format(cnt=receivedOrphan), fontBold=True)
        table.setText(7, 1, u'Госпитализированные: {cnt}'.format(cnt=hospitalOrhpan), fontBold=True)
        table.setText(8, 1, u'Отказные: {cnt}'.format(cnt=refusedOrphan), fontBold=True)

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()

        cursor.setCharFormat(CReport.ReportTitle)
        cursor.setBlockFormat(bf)
        cursor.insertText(u'ПЛАНОВЫЕ: {cnt}'.format(cnt=planned))

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()

        orgStructures = [
            (u'Глазные',        [105, 101]),
            (u'Дневной ст.',    [78]),
            (u'Эндо. хирургия', [107]),
            (u'1 ЧЛХ',          [19]),
            (u'2 ЧЛХ',          [20]),
            (u'Гинекология',    [68]),
            (u'ЛОР',            [16]),
            (u'1травма',        [17]),
            (u'2травма',        [18]),
            (u'НХО',            [15]),
            (u'2 ХИРУРГИЯ',     [13])
        ]
        orgStructureIdList = reduce(lambda x, y: x+y, [idList for name, idList in orgStructures])


        planTableColumns = [
            ('50%', u'', CReport.AlignLeft),
            ('30%', u'', CReport.AlignLeft),
            ('20%', u'', CReport.AlignLeft),
        ]
        planTable = createTable(cursor, planTableColumns, border=0, cellPadding=2)
        for row in xrange(len(orgStructures)):
            planTable.addRow()

        for row, (orgStructureName, idList) in enumerate(orgStructures):
            planTable.setText(row, 1, orgStructureName, fontBold=True)
            planTable.setText(row, 2, sum([reportData[id]['planned'] for id in idList]), fontBold=True)

        planTable.mergeCells(0, 0, len(orgStructures), 1)
        planTable.setText(0, 0, u'Выездная бригада: {brigade}\n\n\n\n' \
                                u'Переводы в другие ЛПУ: {moving}'.format(brigade=byEmergency, moving=0), fontBold=True)

        return doc


def main():
    import sys
    from s11main import CS11mainApp
    from library.database import connectDataBaseByInfo

    app = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtGui.qApp = app
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    QtGui.qApp.currentOrgId = lambda: 3147

    QtGui.qApp.db = connectDataBaseByInfo({
        'driverName' :      'mysql',
        'host' :            'mos36',
        'port' :            3306,
        'database' :        's11',
        'user':             'dbuser',
        'password':         'dbpassword',
        'connectionName':   'vista-med',
        'compressData' :    True,
        'afterConnectFunc': None
    })

    CDispatching3Report(None).exec_()


if __name__ == '__main__':
    main()