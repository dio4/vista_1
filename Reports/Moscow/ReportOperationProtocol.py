# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Reports.Moscow.ReportNonPaidEvents import CSetupDialog
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from library.Utils import forceString, forceDate

stmt = u"""
SELECT DISTINCT
  Client.`id` AS `clientId`,
  concat_ws(' ', Client.`lastName`, Client.`firstName`, Client.`patrName`) AS clientName,
  IF(Client.`sex` = 1, 'М', 'Ж') AS clientSex,
  age(Client.`birthDate`, NOW()) AS `age`,
  (
    SELECT APS.`value`
    FROM
      ActionProperty AS AP
      INNER JOIN ActionPropertyType AS APT ON APT.`id` = AP.`type_id`
      INNER JOIN ActionProperty_String AS APS ON APS.`id` = AP.`id`
    WHERE
      AP.`action_id` = OperationAction.`id`
      AND AP.`deleted` = 0
      AND APT.`name` LIKE 'Диагноз до операции%'
    LIMIT 0, 1
  ) AS diagnosis,
  OperationAction.endDate AS operationDate,
  (
    SELECT APS.`value`
    FROM
      ActionProperty AS AP
      INNER JOIN ActionPropertyType AS APT ON APT.`id` = AP.`type_id`
      INNER JOIN ActionProperty_String AS APS ON APS.`id` = AP.`id`
    WHERE
      AP.`action_id` = OperationAction.`id`
      AND AP.`deleted` = 0
      AND APT.`name` LIKE 'Наименование операции%'
    LIMIT 0, 1
  ) AS operationName,
  (
    SELECT APS.`value`
    FROM
      ActionProperty AS AP
      INNER JOIN ActionPropertyType AS APT ON APT.`id` = AP.`type_id`
      INNER JOIN ActionProperty_String AS APS ON APS.`id` = AP.`id`
    WHERE
      AP.`action_id` = OperationAction.`id`
      AND AP.`deleted` = 0
      AND APT.`name` LIKE 'Вид операции%'
    LIMIT 0, 1
  ) AS Eks,
  (
    SELECT APS.`value`
    FROM
      ActionProperty AS AP
      INNER JOIN ActionPropertyType AS APT ON APT.`id` = AP.`type_id`
      INNER JOIN ActionProperty_String AS APS ON APS.`id` = AP.`id`
    WHERE
      AP.`action_id` = OperationAction.`id`
      AND AP.`deleted` = 0
      AND APT.`name` LIKE 'Вид анестезии%'
    LIMIT 0, 1
  ) AS anesthesiaType,
  CONCAT((
    SELECT APP.`value`
    FROM
      ActionProperty AS AP
      INNER JOIN ActionPropertyType AS APT ON APT.`id` = AP.`type_id`
      INNER JOIN ActionProperty_String AS APP ON APP.`id` = AP.`id`
    WHERE
      AP.`action_id` = OperationAction.`id`
      AND AP.`deleted` = 0
      AND APT.`name` LIKE 'Хирург%'
    LIMIT 0, 1
  ), ' / ', vOrg.name) AS personWithSpec,
  (
    SELECT APS.`value`
    FROM
      ActionProperty AS AP
      INNER JOIN ActionPropertyType AS APT ON APT.`id` = AP.`type_id`
      INNER JOIN ActionProperty_String AS APS ON APS.`id` = AP.`id`
    WHERE
      AP.`action_id` = OperationAction.`id`
      AND AP.`deleted` = 0
      AND APT.`name` LIKE 'Осложнение во время операции%'
    LIMIT 0, 1
  ) AS complicationsDuringOperation
FROM
  ActionType AS LeavedActionType
  INNER JOIN Action LeavedAction ON LeavedActionType.id = LeavedAction.actionType_id
  
  INNER JOIN ActionType AS OperationActionType ON OperationActionType.name LIKE 'Протокол операции%'
  INNER JOIN Action AS OperationAction ON OperationAction.`actionType_id` = OperationActionType.`id`
  
  INNER JOIN Event ON LeavedAction.event_id = Event.id
  
  INNER JOIN Client ON Event.client_id = Client.id
  
  INNER JOIN Person vPerson ON vPerson.id = OperationAction.person_id
  INNER JOIN OrgStructure vOrg ON vOrg.id = vPerson.orgStructure_id
  
  INNER JOIN Person execPerson ON execPerson.id = Event.execPerson_id
  INNER JOIN OrgStructure execOrg ON execOrg.id = execPerson.orgStructure_id
WHERE
  LeavedAction.deleted = 0
  AND OperationAction.deleted = 0
  AND Event.deleted = 0
  AND Client.deleted = 0
  AND LeavedActionType.flatCode = 'leaved'
  AND LeavedAction.event_id = OperationAction.event_id
  {personOrgStructure}
  AND (
    Event.setDate >= DATE('{begDate}') AND Event.setDate <= DATE('{endDate}')
  )
ORDER BY Client.`lastName`, Client.`firstName`, Client.`patrName`
"""


def selectData(params):
    begDate = QtCore.QDate(params.get('begDate', QtCore.QDate.currentDate())).toString('yyyy-MM-dd')
    endDate = QtCore.QDate(params.get('endDate', QtCore.QDate.currentDate())).toString('yyyy-MM-dd')
    orgStructureId = params.get('orgStructureId', None)
    if orgStructureId:
        orgStructureCond = u'AND execOrg.id = %s' % orgStructureId
    else:
        orgStructureCond = u''

    return QtGui.qApp.db.query(stmt.format(begDate=begDate, endDate=endDate, personOrgStructure=orgStructureCond))


class CReportOperationProtocol(CReport):
    def __init__(self, parent=None):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчет по прооперированным пациентам')

    def getSetupDialog(self, parent):
        result = CSetupDialog(parent)

        result.lblOrgStructure.setVisible(True)
        result.cmbOrgStructure.setVisible(True)

        result.cmbContract.setVisible(False)
        result.lblContract.setVisible(False)

        result.setTitle(self.title())
        return result

    def build(self, params):
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(QtGui.QTextCharFormat())
        cursor.movePosition(QtGui.QTextCursor.End)

        cursor.insertBlock()
        cursor.setBlockFormat(CReportBase.AlignCenter)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(
            u'Отчет по прооперированным пациентам  ГБУЗ «ГКБ  имени Ф.И. Иноземцева ДЗМ»'
        )
        cursor.insertBlock()
        cursor.insertBlock()

        self.dumpParams(cursor, params)

        tableColumns = [
            ('%30', [u'ФИО'], CReportBase.AlignRight),
            ('%10', [u'Пол'], CReportBase.AlignRight),
            ('%10', [u'Возраст'], CReportBase.AlignRight),
            ('%10', [u'Диагноз'], CReportBase.AlignRight),
            ('%10', [u'Дата операции'], CReportBase.AlignRight),
            ('%10', [u'Наименование операции'], CReportBase.AlignRight),
            ('%20', [u'Экс'], CReportBase.AlignRight),
            ('%10', [u'Анестезия'], CReportBase.AlignRight),
            ('%10', [u'Врач/отделение '], CReportBase.AlignRight),
            ('%50', [u'Осложнения'], CReportBase.AlignRight)
        ]

        table = createTable(cursor, tableColumns)

        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            row = [
                forceString(record.value('clientName')),
                forceString(record.value('clientSex')),
                forceString(record.value('age')),
                forceString(record.value('diagnosis')),
                forceDate(record.value('operationDate')).toString('dd.MM.yyyy'),
                forceString(record.value('operationName')),
                forceString(record.value('Eks')),
                forceString(record.value('anesthesiaType')),
                forceString(record.value('personWithSpec')),
                forceString(record.value('complicationsDuringOperation'))
            ]

            i = table.addRow()
            for x in range(len(row)):
                table.setText(i, x, row[x])

        boldTextFormat = QtGui.QTextCharFormat()
        boldTextFormat.setFontWeight(QtGui.QFont.Bold)

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()

        headerColumns = [('50%', [''], CReportBase.AlignLeft), ('50%', [''], CReportBase.AlignRight)]

        table = createTable(cursor, headerColumns, border=0, cellPadding=2, cellSpacing=0, charFormat=boldTextFormat)
        table.setText(0, 0, u'Согласовано:___________________Абрамов О.Е.')
        table.setText(0, 1, u'Дата составлен: %s' % QtCore.QDate.currentDate().toString('dd.MM.yyyy'))
        return doc


def main():
    import sys
    from s11main import CS11mainApp
    from library.database import connectDataBaseByInfo

    QtGui.qApp = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    connectionInfo = {
        'driverName': 'mysql',
        'host': 'mos36',
        'port': 3306,
        'database': 's11',
        'user': 'dbuser',
        'password': 'dbpassword',
        'connectionName': 'vista-med',
        'compressData': True,
        'afterConnectFunc': None
    }
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    w = CReportOperationProtocol(None)
    w.exec_()


if __name__ == '__main__':
    main()
