# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Orgs.Utils import getOrgStructureDescendants
from Reports.Moscow.Dispatching.DispatchingSetupDialog import CDispatchingSetupDialog
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase
from library.Utils      import forceInt, forceRef, forceString


def selectReceived(date, begTime, orgStructureIdList):
    db = QtGui.qApp.db

    begDateTime = QtCore.QDateTime(date.addDays(-1), begTime)
    endDateTime = QtCore.QDateTime(date, begTime)

    Event = db.table('Event')
    Received = db.table('Action').alias('Received')
    OrgStructure = db.table('OrgStructure')

    dateCond = db.joinAnd([
        Event['deleted'].eq(0),
        Received['begDate'].datetimeGe(begDateTime),
        Received['endDate'].datetimeLt(endDateTime)
    ])

    orgStructureCond = OrgStructure['id'].inlist(orgStructureIdList)

    Client = db.table('Client')
    ClientSocStatus = db.table('ClientSocStatus')
    SocStatusType = db.table('rbSocStatusType')

    def socStatusTypeCond(code):
        queryTable = ClientSocStatus.innerJoin(SocStatusType, [SocStatusType['code'].like(code),
                                                               SocStatusType['id'].eq(ClientSocStatus['socStatusType_id'])])
        return db.existsStmt(queryTable, [ClientSocStatus['client_id'].eq(Client['id']),
                                          ClientSocStatus['deleted'].eq(0)])

    bumCond = socStatusTypeCond(u'с10')  # БОМЖ

    stmt = u'''
    SELECT
      OrgStructure.id    AS id,
      T.received         AS received,
      T.planned          AS planned,
      T.refused          AS refused,
      T.byHimself        AS byHimself,
      T.byVMP            AS byVMP,
      T.byDMS            AS byDMS,
      T.byPMU            AS byPMU,
      T.receivedAlco     AS receivedAlco,
      T.receivedBum      AS receivedBum,
      T.nonMoscow        AS nonMoscow,
      T.refusedNonMoscow AS refusedNonMoscow,
      T.foreigner        AS foreigner,
      T.refusedForeigner AS refusedForeigner
    FROM
      OrgStructure
      LEFT JOIN (
        SELECT
          OrgStructureAPOS.value                                                                AS id,
          count(Received.id)                                                                    AS received,
          count(if(Received.isUrgent = 0, Received.id, NULL))                                   AS planned,
          count(if(HospRefusalAPS.value IS NOT NULL, Received.id, NULL))                        AS refused,
          count(if(DeliveredByAPS.value LIKE '%самотёк%', Received.id, NULL))                   AS byHimself,
          count(if(DeliveredByAPS.value LIKE '%ВМП%', Received.id, NULL))                       AS byVMP,
          count(if(rbFinance.code = 3, Received.id, NULL))                                      AS byDMS,
          count(if(rbFinance.code = 4, Received.id, NULL))                                      AS byPMU,
          count(if(IntoxicationAPS.value = 'Алкогольного', Received.id, NULL))                  AS receivedAlco,
          count(if({bumCond}, Received.id, NULL))                                               AS receivedBum,
          count(if(LEFT(AddressHouse.KLADRCode, 2) != 77, Received.id, NULL))                                      AS nonMoscow,
          count(if(LEFT(AddressHouse.KLADRCode, 2) != 77 AND HospRefusalAPS.value IS NOT NULL, Received.id, NULL)) AS refusedNonMoscow,
          count(if(rbDocumentType.isForeigner, Received.id, NULL))                                      AS foreigner,
          count(if(rbDocumentType.isForeigner AND HospRefusalAPS.value IS NOT NULL, Received.id, NULL)) AS refusedForeigner
        FROM
          Event
          INNER JOIN ActionType ReceivedAT ON ReceivedAT.flatCode = 'received' AND ReceivedAT.deleted = 0
          INNER JOIN Action Received ON Received.id = (SELECT MAX(A.id) FROM Action A WHERE A.event_id = Event.id AND A.actionType_id = ReceivedAT.id AND A.deleted = 0)

          INNER JOIN Client ON Client.id = Event.client_id AND Client.deleted = 0

          LEFT JOIN ClientDocument ON ClientDocument.id = getClientDocumentId(Client.id)
          LEFT JOIN rbDocumentType ON rbDocumentType.id = ClientDocument.documentType_id

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

          LEFT JOIN rbFinance ON rbFinance.id = Received.finance_id
        WHERE
          {dateCond}
        GROUP BY
          OrgStructureAPOS.value
      ) T ON T.id = OrgStructure.id
    WHERE
      {orgStructureCond}
    '''.format(dateCond=dateCond,
               orgStructureCond=orgStructureCond,
               bumCond=bumCond)

    return db.query(stmt)


class CDispatchingAdminReport(CReport):
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

        bfLeft = QtGui.QTextBlockFormat()
        bfLeft.setAlignment(QtCore.Qt.AlignLeft)

        bfCenter = QtGui.QTextBlockFormat()
        bfCenter.setAlignment(QtCore.Qt.AlignCenter)

        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReport.ReportTitle)
        cursor.setBlockFormat(bfCenter)
        cursor.insertText(u'СВОДКА ДЛЯ АДМИНИСТРАТОРА')
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()

        rececption9IdList = getOrgStructureDescendants(255)  # Приемное отделение 9 корпус

        orgStructuresAlco = [
            (u'1 ЧЛХ',    19),
            (u'2 ЧЛХ',    20),
            (u'1 Тр.',    17),
            (u'2 Тр.',    18),
            (u'НХО',      15),
            (u'НРАО',     26), # maybe not
            (u'РАО Общ.', 25),
            (u'3 ТО',     106),
            (u'2 ХО',     13),
            (u'Г/О',      68),
            (u'2 К/О',    37),
            (u'Офт',      105),
            (u'ЛОР',      16)
        ]
        orgStructuresAlcoIdList = [id for code, id in orgStructuresAlco]

        table3OrgStructures = [
            (u'АГЦ',   240),
            (u'ОЖОГИ', 99),
            (u'РСЦ',   90)
        ]
        table3OrgStructureIdList = [id for code, id, in table3OrgStructures]

        cursor.setCharFormat(CReport.ReportTitle)
        cursor.setBlockFormat(bfLeft)
        cursor.insertText(u'Приемное отделение 9 корпус')

        # 1
        receivedInfo = {}
        receivedFields = ('received', 'planned', 'refused',
                          'byHimself', 'byVMP', 'byDMS', 'byPMU',
                          'receivedAlco', 'receivedBum',
                          'nonMoscow', 'refusedNonMoscow', 'foreigner', 'refusedForeigner')
        queryReceived = selectReceived(date, begTime, rececption9IdList + orgStructuresAlcoIdList + table3OrgStructureIdList)
        self.addQueryText(forceString(queryReceived.lastQuery()))
        while queryReceived.next():
            record = queryReceived.record()
            id = forceRef(record.value('id'))
            receivedInfo[id] = dict([(field, forceInt(record.value(field))) for field in receivedFields])
            receivedInfo[id]['hospital'] = receivedInfo[id]['received'] - receivedInfo[id]['refused']

        received = sum(receivedInfo[id]['received'] for id in rececption9IdList)
        planned = sum(receivedInfo[id]['planned'] for id in rececption9IdList)
        refused = sum(receivedInfo[id]['refused'] for id in rececption9IdList)
        byHimself = sum(receivedInfo[id]['byHimself'] for id in rececption9IdList)
        byVMP = sum(receivedInfo[id]['byVMP'] for id in rececption9IdList)
        byDMS = sum(receivedInfo[id]['byDMS'] for id in rececption9IdList)
        byPMU = sum(receivedInfo[id]['byPMU'] for id in rececption9IdList)
        receivedAlco = sum(receivedInfo[id]['receivedAlco'] for id in rececption9IdList)
        receivedBum = sum(receivedInfo[id]['receivedBum'] for id in rececption9IdList)
        nonMoscow = sum(receivedInfo[id]['nonMoscow'] for id in rececption9IdList)
        refusedNonMoscow = sum(receivedInfo[id]['refusedNonMoscow'] for id in rececption9IdList)
        foreigner = sum(receivedInfo[id]['foreigner'] for id in rececption9IdList)
        refusedForeigner = sum(receivedInfo[id]['refusedForeigner'] for id in rececption9IdList)
        hospital = received - refused

        countOVD = 0
        countGAI = 0
        countProsecutor = 0

        tableColumns = [
            ('25%', u'', CReport.AlignLeft),
            ('25%', u'', CReport.AlignLeft),
            ('50%', u'', CReport.AlignLeft)
        ]
        table = createTable(cursor, tableColumns)

        leftText = u'ВСЕГО: {received}\n\n' \
                   u'ГОСПИТ: {hospital}\n\n' \
                   u'ОТКАЗ: {refused}\n\n'.format(received=received, hospital=hospital, refused=refused)

        rightText = u'ТФ (ОВД {countOVD}) (ГАИ {countGAI})\n' \
                    u'Прокуратура: {countProsecutor}\n\n' \
                    u'ИНОГОРОД.: {nonMoscow} / {refusedNonMoscow}\n' \
                    u'ИНОСТР.: {foreigner} / {refusedNonMoscow}\n\n' \
                    u'БОМЖИ: {receivedBum}\n\n' \
                    u'Плановые б-ные: {planned}\n\n' \
                    u'Самотеки: {byHimself}'.format(countOVD=countOVD, countGAI=countGAI, countProsecutor=countProsecutor,
                                                    nonMoscow=nonMoscow, refusedNonMoscow=refusedNonMoscow,
                                                    foreigner=foreigner, refusedForeigner=refusedForeigner,
                                                    receivedBum=receivedBum, planned=planned, byHimself=byHimself)

        table.mergeCells(0, 0, 1, 2)
        table.setText(0, 0, leftText, fontBold=True)

        i = table.addRow()
        table.mergeCells(i, 0, 1, 2)
        table.setText(i, 0, u'АЛК.ОПЬЯН.: {receivedAlco}'.format(receivedAlco=receivedAlco), fontBold=True)

        i = table.addRow()
        table.mergeCells(i, 0, 1, 2)
        table.setText(i, 0, u'ГОСПИТАЛИЗАЦИЯ А/О', fontBold=True)

        i = table.addRow()
        for col, orgStructures in enumerate((orgStructuresAlco[:8], orgStructuresAlco[8:])):
            table.setText(i, col, u'\n'.join(u'{code} - {cnt}'.format(code=code, cnt=receivedInfo[id]['receivedAlco']) for code, id in orgStructures), fontBold=True)

        table.mergeCells(0, 2, 4, 1)
        table.setText(0, 2, rightText, fontBold=True)

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertBlock()

        # 2

        table2Columns = [
            ('33.3%', [], CReportBase.AlignLeft),
            ('33.3%', [], CReportBase.AlignLeft),
            ('33.3%', [], CReportBase.AlignLeft)
        ]
        table2 = createTable(cursor, table2Columns, cellPadding=3)
        table2.addRow()

        table2.setText(0, 0, u'Платные мед.: {byPMU}'.format(byPMU=byPMU), fontBold=True)
        table2.setText(0, 1, u'ДМС: {byDMS}'.format(byDMS=byDMS), fontBold=True)
        table2.setText(0, 2, u'ВМП: {byVMP}'.format(byVMP=byVMP), fontBold=True)
        table2.setText(1, 0, u'отд.:', fontBold=True)
        table2.setText(1, 1, u'отд.:', fontBold=True)
        table2.setText(1, 2, u'отд.:', fontBold=True)

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertBlock()

        # 3

        table3 = createTable(cursor, table2Columns, cellPadding=3)
        table3Rows = [
            (u'обр.',     u'received'),
            (u'госп.',    u'hospital'),
            (u'отказ.',   u'refused'),
            (u'САМОТЕКИ', u'byHimself')
        ]
        for _ in xrange(len(table3Rows)):
            table3.addRow()

        for col, (orgStructureName, orgStructureId) in enumerate(table3OrgStructures):
            table3.setText(0, col, orgStructureName, fontBold=True)
            for row, (rowName, rowCode) in enumerate(table3Rows):
                table3.setText(row+1, col, u'{name}: {count}'.format(name=rowName, count=receivedInfo[orgStructureId][rowCode]), fontBold=True)

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

    CDispatchingAdminReport(None).exec_()


if __name__ == '__main__':
    main()