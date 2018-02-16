# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from library.DialogBase import CDialogBase
from library.Utils      import forceBool, forceDate, forceDateTime, forceInt, forceRef, forceString, formatShortNameInt, \
                               formatSex, getPref, setPref, toVariant, smartDict
from library.database   import addDateInRange

from Orgs.Utils         import getOrgStructureName, getOrgStructureDescendants

from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase

from Ui_ReportBedspaceUsageSetupDialog import Ui_ReportBedspaceUsageSetupDialog


class COrgStructureType:
    ambultory = 0  # Амбулатория
    statonary = 1  # Стационар
    emergency = 2  # Скорая помощь
    mobileStation = 3  # Мобильная станция
    stationaryReception = 4  # Приемное отделение стационара
    reanimation = 5  # Реанимация
    pharmacy = 6  # Аптека
    warehouse = 99  # Склад


def selectDataRaw(begDateTime, endDateTime, orgStructureId):
    db = QtGui.qApp.db
    Action = db.table('Action')
    OrgStructure = db.table('OrgStructure')

    orgStructureCond = [
        OrgStructure['deleted'].eq(0),
        OrgStructure['type'].notInlist([COrgStructureType.ambultory, COrgStructureType.warehouse])
    ]
    if orgStructureId:
        orgStructureCond.append(OrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)))

    actionDateCond = [
        Action['begDate'].datetimeGe(begDateTime),
        Action['endDate'].datetimeLe(endDateTime)
    ]

    stmt = u'''
SELECT
  mainTable.id              AS orgStructureId,
  mainTable.type            AS orgStructureType,
  mainTable.name            AS orgStructureName,
  mainTable.bedCount        AS bedCountPrev,
  mainTable.bedCount        AS bedCountCur,
  mainTable.bedCount        AS bedCountAvg,
  received.receivedTotal    AS receivedTotal,
  received.byEmergency      AS byEmergency,
  received.byHimself        AS byHimself,
  received.planned          AS planned,
  leaved.leavedTotal        AS leavedTotal,
  leaved.dead               AS dead,
  leaved.financeOMS         AS financeOMS,
  leaved.financeBudget      AS financeBudget,
  leaved.financeNonBudget   AS financeNonBudget,
  leaved.bedDays            AS bedDays,
  leaved.repeated           AS repeated,
  operation.operatedClients AS operatedClients
FROM
  (
    SELECT
      OrgStructure.id   AS id,
      OrgStructure.name AS name,
      OrgStructure.type AS type,
      count(OSHB.id)    AS bedCount
    FROM
      OrgStructure
      INNER JOIN OrgStructure_HospitalBed OSHB ON OSHB.master_id = OrgStructure.id AND OSHB.isPermanent = 1
    WHERE
      {orgStructureCond}
    GROUP BY
      OrgStructure.id
  ) AS mainTable

  LEFT JOIN (
    SELECT
      APOS.value                                                                       AS id,
      count(AP.id)                                                                     AS receivedTotal,
      count(if(DeliveredByAPS.value LIKE '1: скорая помощь', ReceivedAction.id, NULL)) AS byEmergency,
      count(if(DeliveredByAPS.value LIKE '2: самотёк', ReceivedAction.id, NULL))       AS byHimself,
      count(if(Event.`order` = 1, Event.id, NULL))                                     AS planned
    FROM
      Event

      INNER JOIN ActionType ReceivedAT ON ReceivedAT.flatCode = 'received' AND ReceivedAT.deleted = 0
      INNER JOIN Action ReceivedAction ON ReceivedAction.id = (
        SELECT Action.id
        FROM Action
        WHERE Action.event_id = Event.id AND Action.actionType_id = ReceivedAT.id AND Action.deleted = 0 AND {actionDateCond}
        ORDER BY Action.begDate DESC
        LIMIT 0, 1
      )

      INNER JOIN ActionPropertyType AS APT ON APT.actionType_id = ReceivedAT.id AND APT.name = 'Направлен в отделение' AND APT.deleted = 0
      INNER JOIN ActionProperty AS AP ON AP.action_id = ReceivedAction.id AND AP.type_id = APT.id AND AP.deleted = 0
      INNER JOIN ActionProperty_OrgStructure AS APOS ON APOS.id = AP.id

      INNER JOIN ActionPropertyType DeliveredByAPT ON DeliveredByAPT.name = 'Кем доставлен' AND DeliveredByAPT.actionType_id = ReceivedAT.id AND DeliveredByAPT.deleted = 0
      LEFT JOIN ActionProperty DeliveredByAP ON DeliveredByAP.action_id = ReceivedAction.id AND DeliveredByAP.type_id = DeliveredByAPT.id AND DeliveredByAP.deleted = 0
      LEFT JOIN ActionProperty_String DeliveredByAPS ON DeliveredByAPS.id = DeliveredByAP.id

      INNER JOIN ActionPropertyType HospRefusalAPT ON HospRefusalAPT.name = 'Причина отказа от госпитализации' AND HospRefusalAPT.actionType_id = ReceivedAT.id AND HospRefusalAPT.deleted = 0
      LEFT JOIN ActionProperty HospRefusalAP ON HospRefusalAP.action_id = ReceivedAction.id AND HospRefusalAP.type_id = HospRefusalAPT.id AND HospRefusalAP.deleted = 0
      LEFT JOIN ActionProperty_String HospRefusalAPS ON HospRefusalAPS.id = HospRefusalAP.id

      INNER JOIN Client ON Client.id = Event.client_id

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

  LEFT JOIN (
    SELECT
      APOS.value                                                    AS id,
      count(AP.id)                                                  AS leavedTotal,
      count(if(ResultAPS.value = 'умер', ResultAPS.id, NULL))       AS dead,
      count(if(rbFinance.code = 1, Event.id, NULL))                 AS financeBudget,
      count(if(rbFinance.code = 2, Event.id, NULL))                 AS financeOMS,
      count(if(rbFinance.code IN (3,4), Event.id, NULL))            AS financeNonBudget,
      sum(datediff(Leaved.endDate, Received.begDate))               AS bedDays,
      count(DISTINCT if(NextEvent.id IS NOT NULL, Client.id, NULL)) AS repeated
    FROM
      Event

      INNER JOIN ActionType LeavedAT ON LeavedAT.flatCode = 'leaved' AND LeavedAT.deleted = 0
      INNER JOIN Action Leaved ON Leaved.id = (
        SELECT Action.id
        FROM Action
        WHERE Action.event_id = Event.id AND Action.actionType_id = LeavedAT.id AND Action.deleted = 0 AND {actionDateCond}
        ORDER BY Action.begDate DESC
        LIMIT 0, 1
      )

      INNER JOIN ActionType ReceivedAT ON ReceivedAT.flatCode = 'received' AND ReceivedAT.deleted = 0
      INNER JOIN Action Received ON Received.id = (
        SELECT Action.id FROM Action WHERE Action.event_id = Leaved.event_id AND Action.actionType_id = ReceivedAT.id AND Action.deleted = 0
        ORDER BY Action.begDate DESC
        LIMIT 0, 1
      )

      LEFT JOIN Event NextEvent ON NextEvent.id = (
        SELECT E.id
        FROM Event E
        WHERE E.id > Event.id AND E.client_id = Event.client_id AND E.deleted = 0 AND EXISTS(
          SELECT * FROM Action
          WHERE Action.event_id = E.id AND Action.actionType_id = ReceivedAT.id AND Action.deleted = 0 AND {actionDateCond}
        )
        LIMIT 0, 1
      )

      INNER JOIN Client ON Client.id = Event.client_id

      INNER JOIN ActionPropertyType AS APT ON APT.actionType_id = LeavedAT.id AND APT.name = 'Отделение' AND APT.deleted = 0
      INNER JOIN ActionProperty AS AP ON AP.action_id = Leaved.id AND AP.type_id = APT.id AND AP.deleted = 0
      INNER JOIN ActionProperty_OrgStructure AS APOS ON APOS.id = AP.id

      LEFT JOIN ActionPropertyType AS ResultAPT ON ResultAPT.actionType_id = LeavedAT.id AND ResultAPT.name = 'Исход госпитализации' AND ResultAPT.deleted = 0
      LEFT JOIN ActionProperty AS ResultAP ON ResultAP.action_id = Leaved.id AND ResultAP.type_id = ResultAPT.id AND ResultAPT.deleted = 0
      LEFT JOIN ActionProperty_String AS ResultAPS ON ResultAPS.id = ResultAP.id

      INNER JOIN Contract ON Contract.id = Event.contract_id
      INNER JOIN rbFinance ON rbFinance.id = Contract.finance_id

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

  LEFT JOIN (
    SELECT
      Person.orgStructure_id    AS id,
      count(DISTINCT Client.id) AS operatedClients
    FROM
      ActionType
      INNER JOIN Action ON Action.actionType_id = ActionType.id AND Action.deleted = 0 AND {actionDateCond}
      INNER JOIN Event ON Event.id = Action.event_id AND Event.deleted = 0
      INNER JOIN Client ON Client.id = Event.client_id AND Client.deleted = 0
      INNER JOIN ActionType LeavedAT ON LeavedAT.flatCode = 'leaved' AND LeavedAT.deleted = 0
      INNER JOIN Action Leaved ON Leaved.event_id = Event.id AND Leaved.actionType_id = LeavedAT.id AND Leaved.deleted = 0
      INNER JOIN Person ON Person.id = Action.person_id AND Person.deleted = 0
    WHERE
      ActionType.code = '111_1_1_1' AND ActionType.deleted = 0
    GROUP BY
      Person.orgStructure_id
  ) AS operation ON operation.id = mainTable.id'''.format(orgStructureCond=db.joinAnd(orgStructureCond), actionDateCond=db.joinAnd(actionDateCond))
    return db.query(stmt)


class CReportBedspaceUsageSetupDialog(CDialogBase, Ui_ReportBedspaceUsageSetupDialog):

    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def params(self):
        return {
            'begDateTime': QtCore.QDateTime(self.edtBegDate.date(), self.edtBegTime.time()),
            'endDateTime': QtCore.QDateTime(self.edtEndDate.date(), self.edtEndTime.time()),
            'showPrevYear': self.chkShowPrevYear.isChecked(),
            'orgStructureId': self.cmbOrgStructure.value()
        }

    def setParams(self, params):
        begDateTime = params.get('begDateTime', QtCore.QDateTime.currentDateTime())
        endDateTime = params.get('endDateTime', QtCore.QDateTime.currentDateTime())
        self.edtBegDate.setDate(begDateTime.date())
        self.edtBegTime.setTime(begDateTime.time())
        self.edtEndDate.setDate(endDateTime.date())
        self.edtEndTime.setTime(endDateTime.time())
        self.chkShowPrevYear.setChecked(params.get('showPrevYear', False))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))


class CReportBedspaceUsage(CReport):
    u"""
        Коечный фонд и его использование
        Территориальная принадлежность: Москва
        Объект: МСК Б36
    """

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Коечный фонд и его использование')

        self.curYear = QtCore.QDate.currentDate().year()
        self.prevYear = self.curYear - 1
        self.showPrewYear = False
        self.OrgStructureType = {}
        self.OrgStructureName = {}

        self.reportFields = ('bedCountPrev', 'bedCountCur', 'bedCountAvg', 'receivedTotal', 'byEmergency', 'byHimself', 'planned', 'leavedTotal', 'dead',
                             'financeOMS', 'financeBudget', 'financeNonBudget', 'bedDays', 'repeated', 'operatedClients')

    def getSetupDialog(self, parent):
        result = CReportBedspaceUsageSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def createTable(self, cursor, charFormat, charFormatBold):
        curYear = QtCore.QDate.currentDate().year()
        prevYear = curYear - 1
        keyColumnWidth = 10.0
        keyColumn = ('%.4f%%' % keyColumnWidth, [u'Подразделение', u'', u''], CReportBase.AlignLeft)
        commonColumns = [
            [u'Число коек, фактически развернутых и свернутых на ремонт', u'', u'на конец предыдущего периода'],
            [u'', u'', u'на конец отчетного периода'],
            [u'', u'', u'среднегодовых'],
        ]
        columnsPerYear = [
            [u'Самотёков на 1 койку', u'', u''],
            [u'За отчетный период', u'поступило пациентов - всего', u''],
            [u'', u'в т.ч. по каналам госпитализации', u'"03"'],
            [u'', u'', u'"самотек"'],
            [u'', u'', u'"план"'],
            [u'', u'', u'прочее'],
            [u'', u'выбыло пациентов (выписано + умерло)', u''],
            [u'', u'в том числе', u'умерло'],
            [u'', u'', u'по ОМС'],
            [u'', u'', u'по бюджету'],
            [u'', u'', u'внебюджетные'],
            [u'', u'', u'прочее'],
            [u'Проведено пациентами койко-дней', u'', u''],
            [u'Койко-дни закрытия на ремонт, мойку, профилактическую', u'', u''],
            [u'Занятость (работа) койки', u'', u''],
            [u'Пролечено пациентов', u'', u''],
            [u'Средняя продолжительность лечения пациентов', u'', u''],
            [u'Оборот койки', u'', u''],
            [u'Летальность', u'', u''],
            [u'Поступило пациентов повторно', u'', u''],
            [u'Количество оперированных пациентов', u'', u''],
            [u'Доля  пациентов, госпитализированных повторно от общего числа выбывших', u'', u''],
            [u'Хирургическая активность', u'', u''],
        ]
        columnWidth = '%.4f%%' % ((100.0 - keyColumnWidth) / (len(commonColumns) + len(columnsPerYear) * (2 if self.showPrevYear else 1)))
        commonColumns = [(columnWidth, descr, CReportBase.AlignCenter) for descr in commonColumns]
        if self.showPrevYear:
            columnsPerYear = reduce(lambda x,y: x+y, [[(columnWidth, descr + [u'%s' % prevYear], CReportBase.AlignCenter),
                                                       (columnWidth, [u''] * len(descr) + [u'%s' % curYear], CReportBase.AlignCenter)] for descr in columnsPerYear])
        else:
            columnsPerYear = [(columnWidth, descr, CReportBase.AlignCenter) for descr in columnsPerYear]
        tableColumns = [keyColumn] + commonColumns + columnsPerYear
        table = createTable(cursor, tableColumns, charFormat=charFormatBold, cellPadding=1)

        if self.showPrevYear:
            table.mergeCells(0, 0, 4, 1)
            table.mergeCells(0, 5, 3, 2)
            for col in [1, 2, 3]:
                table.mergeCells(2, col, 2, 1)
            table.mergeCells(0, 1, 2, 3)

            for col in [6, 16]:
                table.mergeCells(1, col, 2, 2)
            table.mergeCells(1, 8, 1, 8)
            table.mergeCells(1, 18, 1, 10)

            for col in range(8, 15, 2) + range(18, 27, 2):
                table.mergeCells(2, col, 1, 2)

            table.mergeCells(0, 6, 1, 22)
            for col in range(28, 49, 2):
                table.mergeCells(0, col, 3, 2)
        else:
            for col in [0, 4] + range(16, 28):
                table.mergeCells(0, col, 3, 1)
            for col in (5, 10):
                table.mergeCells(1, col, 2, 1)

            table.mergeCells(0, 1, 2, 3)
            table.mergeCells(0, 5, 1, 11)
            table.mergeCells(1, 6, 1, 4)
            table.mergeCells(1, 11, 1, 5)

        i = table.addRow()
        for j in xrange(len(tableColumns)):
            table.setText(i, j, j + 1, blockFormat=CReportBase.AlignCenter, charFormat=charFormat)

        return table

    def processQuery(self, begDateTime, endDateTime, orgStructureIdList):
        query = selectDataRaw(begDateTime, endDateTime, orgStructureIdList)
        self.addQueryText(forceString(query.lastQuery()))

        reportData = {}
        while query.next():
            record = query.record()
            id = forceRef(record.value('orgStructureId'))
            reportData[id] = dict([(field, forceInt(record.value(field))) for field in self.reportFields])
            self.OrgStructureType[id] = forceInt(record.value('orgStructureType'))
            self.OrgStructureName[id] = forceString(record.value('orgStructureName'))

        return reportData

    def processRow(self, data):
        clientsTotal = (data['receivedTotal'] + data['leavedTotal']) / 2
        bedCount = data['bedCountAvg']
        notInUseBedDays = 0
        return [
            data['bedCountPrev'],
            data['bedCountCur'],
            data['bedCountAvg'],
            '%.2f' % (float(data['byHimself']) / float(bedCount)) if bedCount else '-',
            data['receivedTotal'],
            data['byEmergency'],
            data['byHimself'],
            data['planned'],
            data['receivedTotal'] - data['byEmergency'] - data['byHimself'] - data['planned'],
            data['leavedTotal'],
            data['dead'],
            data['financeOMS'],
            data['financeBudget'],
            data['financeNonBudget'],
            data['leavedTotal'] - data['financeOMS'] - data['financeBudget'] - data['financeNonBudget'],
            data['bedDays'],
            notInUseBedDays,
            '%.2f' % (float(data['bedDays'] + notInUseBedDays) / float(bedCount)) if bedCount else '-',
            clientsTotal,
            '%.2f' % (float(data['bedDays']) / float(clientsTotal)) if clientsTotal else  '-',
            '%.2f' % (float(clientsTotal) / float(bedCount)) if bedCount else '-',
            '%.2f' % (100.0 * data['dead'] / data['leavedTotal']) if data['leavedTotal'] else '-',
            data['repeated'],
            data['operatedClients'],
            '%.2f' % (100.0 * data['repeated'] / data['leavedTotal']) if data['leavedTotal'] else '-',
            '%.2f' % (100.0 * data['operatedClients'] / clientsTotal) if clientsTotal else '-'
        ]

    def postProcessReport(self, reportData):
        def totalByOrgStructures(year, orgStructureIds):
            return dict([(field, sum([reportData[year][id][field] for id in orgStructureIds if id in reportData[year]])) for field in self.reportFields])

        def twoYearRow(prevRow, curRow):
            return curRow[:3] + list(reduce(lambda x, y: x + y, zip(prevRow[3:], curRow[3:])))

        def produceRow(idList):
            totalCurYear = self.processRow(totalByOrgStructures(self.curYear, idList))
            if self.showPrevYear:
                return twoYearRow(self.processRow(totalByOrgStructures(self.prevYear, idList)), totalCurYear)
            return totalCurYear

        reportRows = []
        def appendReportRow(name, dataRow, isBold=False):
            reportRows.append(([name] + dataRow, isBold))

        appendReportRow(u'ИТОГО', produceRow([id for id, type in self.OrgStructureType.iteritems() if type != COrgStructureType.reanimation]), True)

        orgStructurePorfile = [
            (u'Кардиология (всего)', [37, 118]),
            (u'Травматология (всего)', [17, 18]),
            (u'Хирургия (всего)', [13, 107]),
            (u'ЧЛХ (всего)', [19, 20]),
            (u'Реанимация (всего)', [id for id, type in self.OrgStructureType.iteritems() if type == COrgStructureType.reanimation]),
        ]
        orgStructureInProfileIdList = reduce(lambda x,y: x+y, [idList for name, idList in orgStructurePorfile])

        for profileName, orgStructureIdList in orgStructurePorfile:
            idList = filter(lambda id: id in reportData[self.curYear], orgStructureIdList)
            if idList:
                appendReportRow(profileName, produceRow(idList), True)
                for id in idList:
                    appendReportRow(self.OrgStructureName[id], produceRow([id]))

        for id in filter(lambda id: id not in orgStructureInProfileIdList, reportData[self.curYear]):
            appendReportRow(self.OrgStructureName[id], produceRow([id]))

        return reportRows

    def build(self, params):
        begDateTime = params.get('begDateTime', QtCore.QDateTime())
        endDateTime = params.get('endDateTime', QtCore.QDateTime())
        self.showPrevYear = params.get('showPrevYear', False)
        orgStructureId = params.get('orgStructureId', [])

        fontSizeHeader = 9
        fontSize = 8
        charFormatHeader = QtGui.QTextCharFormat()
        charFormatHeader.setFontPointSize(fontSizeHeader)
        charFormatHeader.setFontWeight(QtGui.QFont.Bold)
        charFormatBody = CReportBase.TableBody
        charFormatBody.setFontPointSize(fontSize)
        charFormatBodyBold = CReportBase.TableBody
        charFormatBodyBold.setFontWeight(QtGui.QFont.Bold)
        charFormatBodyBold.setFontPointSize(fontSize)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(charFormatHeader)
        cursor.insertText(self.title())
        cursor.movePosition(QtGui.QTextCursor.End)

        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        cursor.setCharFormat(charFormatBody)
        table = self.createTable(cursor, charFormatBody, charFormatBodyBold)

        reportData = {self.curYear: self.processQuery(begDateTime, endDateTime, orgStructureId)}
        if self.showPrevYear:
            reportData[self.prevYear] = self.processQuery(begDateTime.addYears(-1), endDateTime.addYears(-1), orgStructureId)

        for row, isBold in self.postProcessReport(reportData):
            i = table.addRow()
            table.setText(i, 0, row[0], charFormat=charFormatBodyBold)
            for j, text in enumerate(row[1:]):
                table.setText(i, j + 1, text, charFormat=(charFormatBodyBold if isBold else charFormatBody))

        return doc


# def main():
#     import sys
#     from s11main import CS11mainApp
#     from library.database import connectDataBaseByInfo
#
#     app = CS11mainApp(sys.argv, False, 'S11App.ini', False)
#     QtGui.qApp = app
#     QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))
#
#     QtGui.qApp.currentOrgId = lambda: 386271
#     QtGui.qApp.currentOrgStructureId = lambda: 34
#
#     QtGui.qApp.db = connectDataBaseByInfo({
#         'driverName' :      'mysql',
#         'host' :            'mos36',
#         'port' :            3306,
#         'database' :        's11',
#         'user':             'dbuser',
#         'password':         'dbpassword',
#         'connectionName':   'vista-med',
#         'compressData' :    True,
#         'afterConnectFunc': None
#     })
#
#     CReportBedspaceUsage(None).exec_()
#
#
# if __name__ == '__main__':
#     main()