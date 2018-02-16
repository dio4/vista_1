# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Orgs.Utils import getOrgStructureDescendants
from ReportAccountingWork import CAccountingWork
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from library.Utils import forceDouble, forceInt, forceString


def selectData(params):
    db = QtGui.qApp.db

    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    eventTypeId = params.get('eventTypeId', None)
    specialityId = params.get('specialityId', None)
    personId = params.get('personId', None)
    eventPurposeId = params.get('eventPurposeId', None)
    orgStructureId = params.get('orgStructureId', None)
    detailPerson = params.get('detailPerson', False)

    tableEvent = db.table('Event')
    tableAction = db.table('Action')
    tablePerson = db.table('Person')
    tableEventType = db.table('EventType')

    cond = [
        tableEvent['deleted'].eq(0),
        db.joinOr([
            db.joinAnd([
                tableAction['endDate'].dateLe(endDate),
                tableAction['endDate'].dateGe(begDate)
            ]),
            db.joinAnd([
                tableAction['begDate'].isNull(),
                tableEvent['setDate'].dateLe(endDate),
                tableEvent['setDate'].dateGe(begDate)
            ])
        ]),
    ]

    group = ''
    order = ''

    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if eventPurposeId:
        cond.append(tableEventType['purpose_id'].eq(eventPurposeId))
    if personId:
        cond.append(tablePerson['id'].eq(personId))
    if specialityId:
        cond.append(tablePerson['speciality_id'].eq(specialityId))
    if orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    if detailPerson:
        group = 'GROUP BY person'
        order = 'ORDER BY person'

    stmt = u'''
SELECT DISTINCTROW
  CONCAT_WS(' ', Person.lastName, Person.firstName, Person.patrName) AS person,
  COUNT(DISTINCT IF(
      ActionType.code IN ('1001', '1005', '2001', '2002', '3001', '3002', '1002', '1006'),
      Action.id,
      NULL
  )) AS field1,
  COUNT(DISTINCT IF(
      ActionType.code IN ('1001', '2001', '3001', '1002'),
      Action.id,
      NULL
  )) AS field2,
  SUM(IF(
      ActionType.code IN (
        '1030', '1031', '1033', '1029', '1032', '1035', '1036', '1098', 
        '1096', '1104', '1047', '1048', '1049', '1103', '1095', '1094'
      ),
      Action.amount,
      0
  )) AS field3,
  SUM(IF(
      ActionType.code IN ('1030', '1031', '1033', '1029', '1032', '1035', '1036'),
      Action.amount,
      0
  )) AS field4,
  SUM(IF(
      ActionType.code IN ('1098', '1096', '1104', '1047', '1048', '1049', '1103', '1095', '1094'),
      Action.amount,
      0
  )) AS field5,
  SUM(IF(
      ActionType.code IN ('1028', '1027'),
      Action.amount,
      0
  )) AS field6,
  SUM(IF(
      ActionType.code IN (
        '1030', '1031', '1033', '1029', '1032', '1035', '1036', '1098', 
        '1096', '1104', '1047', '1048', '1049', '1103', '1095', '1094'
      ),
      Action.amount,
      0
  )) AS field7,
  COUNT(DISTINCT IF(
      ActionType.code IN ('1063', '1064', '1065'),
      Action.id,
      NULL
  )) AS field7A,
  SUM(IF(
      ActionType.code IN ('1010', '3008', '2045'),
      Action.amount,
      0
  )) AS field8,
  SUM(IF(
      ActionType.code IN ('3009', '3012', '3067', '3068', '3015'),
      Action.amount,
      0
  )) AS field9,
  COUNT(DISTINCT IF(
      ActionType.code IN ('3040', '3034', '3037', '3018', '5008', '5013'),
      Action.id,
      NULL
  )) AS field10,
  COUNT(DISTINCT IF(
      ActionType.code IN ('3031', '2046', '2047', '2049', '2050', '2051', '2052', '2058', '2055'),
      Action.id,
      NULL
  )) AS field11,
  SUM(IF(
      ActionType.code IN ('2041'),
      Action.amount,
      0
  )) AS field12,
  SUM(IF(
      ActionType.code IN ('2006'),
      Action.amount,
      0
  )) AS field13,
  SUM(IF(
      ActionType.code IN ('5027'),
      Action.amount,
      0
  )) AS field14,
  COUNT(DISTINCT IF(
      ActionType.code IN ('9013'),
      Action.id,
      NULL
  )) AS field15,
  SUM(IF(
      ActionType.code IN ('9008'),
      Action.amount,
      0
  )) AS field16,
  ROUND(SUM(IF(
      ActionType.code IN ('3037', '3034', '3018', '5008', '5013', '3040'),
      (SELECT SUM(uet) FROM Account_Item ai WHERE ai.event_id = Event.id AND ai.deleted = 0),
      0
  )), 2) AS field17,
  ROUND(SUM(IF(
      ActionType.code IN ('3031', '2046', '2047', '2049', '2050', '2051', '2052', '2058', '2055'),
      (SELECT SUM(uet) FROM Account_Item ai WHERE ai.event_id = Event.id AND ai.deleted = 0),
      0
  )), 2) AS field18,
  ROUND(SUM(IF(
      (
        execPersonSpec.name LIKE '%%Стоматология терапевтическая'
        OR execPersonSpec.name LIKE '%%Стоматология общей практики'
        OR execPersonSpec.name LIKE '%%Стоматология'
      ),
      (SELECT uet FROM Account_Item ai WHERE ai.action_id = Action.id AND ai.deleted = 0),
      0
  )), 2) AS field19,
  ROUND(SUM(IF(
      execPersonSpec.code = '177',
      (SELECT uet FROM Account_Item ai WHERE ai.action_id = Action.id AND ai.deleted = 0),
      0
  )), 2) AS field20,
  ROUND(SUM(IF(
      execPersonSpec.name LIKE '%%парадонтолог%%',
      (SELECT uet FROM Account_Item ai WHERE ai.action_id = Action.id AND ai.deleted = 0),
      0
  )), 2) AS field21,
  0 AS field22,
  ROUND(SUM(IF(
      Event.eventType_id IS NOT NULL,
      (SELECT sum FROM Account_Item ai WHERE ai.action_id = Action.id AND ai.deleted = 0),
      0
  )), 2) AS field23
FROM Event
  # INNER JOIN Account_Item ON Event.id = Account_Item.event_id AND Account_Item.deleted = 0
  INNER JOIN EventType ON EventType.id = Event.eventType_id
  INNER JOIN Client ON Client.id = Event.client_id
  INNER JOIN Action ON Action.event_id = Event.id AND Action.deleted = 0
  INNER JOIN ActionType ON ActionType.id = Action.actionType_id AND ActionType.deleted = 0
  # view
  INNER JOIN Person ON Person.id IN (Event.setPerson_id)

  INNER JOIN Person AS setPerson ON setPerson.id = Action.setPerson_id
  INNER JOIN rbSpeciality AS setPersonSpec ON setPerson.speciality_id = setPersonSpec.id

  INNER JOIN Person AS execPerson ON execPerson.id = Action.person_id
  INNER JOIN rbSpeciality AS execPersonSpec ON execPerson.speciality_id = execPersonSpec.id
WHERE
  %s
  %s
  %s
    ''' % (db.joinAnd(cond), group, order)
    stmt = stmt.format(begDate=begDate.toString('yyyy-MM-dd'), endDate=endDate.toString('yyyy-MM-dd'))

    return db.query(stmt)


class CReportOnEconomicCalcServices(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'ОТЧЕТ ПО хоз. расч. услугам')

    def getSetupDialog(self, parent):
        result = CAccountingWork(parent)
        result.lblActionType.setVisible(False)
        result.cmbActionType.setVisible(False)

        result.setTitle(self.title())
        result.chkGroup.setVisible(False)
        return result

    def build(self, params):
        detailPerson = params.get('detailPerson', False)

        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
            ('%50', [u'ФИО'], CReportBase.AlignRight),
            ('%50', [u'Кол. пос.', u'', u'1'], CReportBase.AlignRight),
            ('%50', [u'Перичные пос.', u'', u'2'], CReportBase.AlignRight),
            ('%5', [u'Кол. Пломб', u'Всего', u'3'], CReportBase.AlignLeft),
            ('%5', [u'', u'Витремер', u'4'], CReportBase.AlignLeft),
            ('%5', [u'', u'СОМ', u'5'], CReportBase.AlignLeft),
            ('%5', [u'', u'Временная', u'6'], CReportBase.AlignLeft),
            ('%5', [u'Запломбировано зубов', u'', u'7'], CReportBase.AlignLeft),
            ('%5', [u'Запломбировано  зубов (осложнен. кариес)', u'', u'7A'], CReportBase.AlignLeft),
            ('%5', [u'Анастезия', u'', u'8'], CReportBase.AlignLeft),
            ('%5', [u'Удалено зубов', u'', u'9'], CReportBase.AlignLeft),
            ('%5', [u'Операции Хир.', u'', u'10'], CReportBase.AlignLeft),
            ('%5', [u'Операции Пародонт.', u'', u'11'], CReportBase.AlignLeft),
            ('%5', [u'Шинирование', u'', u'12'], CReportBase.AlignLeft),
            ('%5', [u'Ультрозвуковое Уд. Зуб. Отлож.', u'', u'13'], CReportBase.AlignLeft),
            ('%5', [u'Вектор', u'', u'14'], CReportBase.AlignLeft),
            ('%5', [u'ОРТО', u'', u'15'], CReportBase.AlignLeft),
            ('%5', [u'Прицельный снимок', u'', u'16'], CReportBase.AlignLeft),
            ('%5', [u'УЕТ опер. Хир.', u'', u'17'], CReportBase.AlignLeft),
            ('%5', [u'УЕТ опер. Пароднт.', u'', u'18'], CReportBase.AlignLeft),
            # ('%5', [u'УЕТ ОРТ', u'', u'19'], CReportBase.AlignLeft),
            # ('%5', [u'УЕТ всего рентген', u'', u'20'], CReportBase.AlignLeft),
            ('%5', [u'УЕТ по Терапии', u'', u'19'], CReportBase.AlignLeft),
            ('%5', [u'УЕТ по хир.', u'', u'20'], CReportBase.AlignLeft),
            ('%5', [u'УЕТ по пародонт.', u'', u'21'], CReportBase.AlignLeft),
            ('%5', [u'Всего УЕТ', u'', u'22'], CReportBase.AlignLeft),
            ('%5', [u'Всего сумма', u'', u'23'], CReportBase.AlignLeft),
        ]

        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 2, 1)

        table.mergeCells(0, 3, 1, 4)

        for x in range(4, len(tableColumns)):
            table.mergeCells(0, x, 2, 1)

        total = [0] * (len(tableColumns) - 1)

        while query.next():
            record = query.record()
            row = [
                forceString(record.value('person')),
                forceInt(record.value('field1')),
                forceInt(record.value('field2')),
                forceInt(record.value('field3')),
                forceInt(record.value('field4')),
                forceInt(record.value('field5')),
                forceInt(record.value('field6')),
                forceInt(record.value('field7')),
                forceInt(record.value('field7A')),
                forceInt(record.value('field8')),
                forceInt(record.value('field9')),
                forceInt(record.value('field10')),
                forceInt(record.value('field11')),
                forceInt(record.value('field12')),
                forceInt(record.value('field13')),
                forceInt(record.value('field14')),
                forceInt(record.value('field15')),
                forceInt(record.value('field16')),
                forceDouble(record.value('field17')),
                forceDouble(record.value('field18')),
                forceDouble(record.value('field19')),
                forceDouble(record.value('field20')),
                forceDouble(record.value('field21')),

                # forceDouble(record.value('field22')),
                forceDouble(record.value('field17')) + forceDouble(record.value('field18')) +
                forceDouble(record.value('field19')) + forceDouble(record.value('field20')) +
                forceDouble(record.value('field21')),

                forceDouble(record.value('field23'))
            ]

            if detailPerson:
                i = table.addRow()
                for x in range(len(row)):
                    table.setText(i, x, row[x])

            for x in range(len(total)):
                total[x] += row[x + 1]

        i = table.addRow()
        table.setText(i, 0, u'Итого', CReportBase.TableTotal)
        for index, value in enumerate(total):
            table.setText(i, index + 1, value, CReportBase.TableTotal)
        return doc


def main():
    import sys
    from s11main import CS11mainApp
    from library.database import connectDataBaseByInfo

    QtGui.qApp = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    connectionInfo = {
        'driverName': 'mysql',
        'host': 'pz12',
        'port': 3306,
        'database': 's11',
        'user': 'dbuser',
        'password': 'dbpassword',
        'connectionName': 'vista-med',
        'compressData': True,
        'afterConnectFunc': None
    }
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    w = CReportOnEconomicCalcServices(None)
    w.exec_()


if __name__ == '__main__':
    main()
