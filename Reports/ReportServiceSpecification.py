# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from library.Utils      import forceInt, forceString, forceDouble

from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.Ui_ReportServiceSpecification import Ui_ReportServiceSpecification


RServiceSpecificationQuery = [
    # Исключить из Прейскуранта следующие услуги
    # (запрос вытащен из конструктора отчетов (pes, s11))
    u'''
    SELECT
        rbService_32.`code` AS rCode,
        rbService_32.`name` AS rName,
        rbServiceSpecification_31.`price` AS rPrice,
        rbService_32.`endDate` AS end
    FROM
        rbServiceSpecification AS rbServiceSpecification_31
        INNER JOIN rbService AS rbService_32 ON rbServiceSpecification_31.`service_id` = rbService_32.`id`
        INNER JOIN ActionType ON rbService_32.id = ActionType.nomenclativeService_id
        INNER JOIN OrgStructure_ActionType ON OrgStructure_ActionType.actionType_id = ActionType.id
        INNER JOIN (SELECT
            rbServiceSpecification_30.`service_id` AS rbServiceSpecification_30_service_id,
            rbServiceSpecification_30.`price` AS rbServiceSpecification_30_price,
            rbServiceSpecification_30.`date` AS rbServiceSpecification_30_date,
            rbServiceSpecification_30.`name` AS rbServiceSpecification_30_name,
            rbServiceSpecification_30.`title` AS rbServiceSpecification_30_title
        FROM rbServiceSpecification AS rbServiceSpecification_30
            INNER JOIN rbService rs ON rbServiceSpecification_30.`service_id` = rs.`id`
        WHERE ((rbServiceSpecification_30.`date` = '{endDate}' AND rs.endDate < '{endDate}'))) AS q10
        ON rbServiceSpecification_31.`service_id` = q10.`rbServiceSpecification_30_service_id`
    WHERE rbServiceSpecification_31.`date` = '{begDate}' AND rbService_32.endDate > '{begDate}'
    ''',
    # Исключить из Прейскуранта следующие услуги
    # (запрос вытащен из комментария http://client.ivista.ru/view.php?id=2916#c12056)
    u'''
        (
            SELECT
                rbs.code AS rCode,
                rbs.name AS rName,
                s1.price AS rPrice
            FROM
                rbServiceSpecification as s1
                INNER JOIN rbService as rbs ON s1.service_id = rbs.id
                INNER JOIN ActionType ON rbService.id = ActionType.nomenclativeService_id
                INNER JOIN OrgStructure_ActionType ON OrgStructure_ActionType.actionType_id = ActionType.id
            WHERE
                rbs.endDate < {endDate} AND s1.date = {begDate}
                AND service_id IN (
                SELECT rbs.id
                FROM rbServiceSpecification as s1
                INNER JOIN rbService as rbs ON s1.service_id = rbs.id
                WHERE rbs.endDate > '{endDate}' AND s1.date = '{begDate}'
                )
        )
        UNION
        (   SELECT
                rbs.code AS rCode,
                rbs.name AS rName,
                s1.price AS rPrice
            FROM
                rbServiceSpecification as s1
                INNER JOIN rbService as rbs ON s1.service_id = rbs.id
                LEFT JOIN rbServiceSpecification as s2 ON s1.service_id = s2.service_id AND s2.date= '{begDate}'
            WHERE
                s1.date = '{begDate}' AND s2.service_id IS NULL
        )
    ''',
    # Внести в Прейскурант следующие услуги
    # (запрос вытащен из конструктора отчетов (pes, s11))
    u'''
        SELECT
            rbService_2.`code` AS rCode,
            rbService_2.`name` AS rName,
            rbServiceSpecification_1.`price` AS rPrice
        FROM
            rbServiceSpecification AS rbServiceSpecification_1
            INNER JOIN rbService AS rbService_2 ON rbServiceSpecification_1.`service_id` = rbService_2.`id`
            INNER JOIN ActionType ON rbService_2.id = ActionType.nomenclativeService_id
            INNER JOIN OrgStructure_ActionType ON OrgStructure_ActionType.actionType_id = ActionType.id
            LEFT JOIN (
                SELECT
                    rbServiceSpecification_0.`service_id` AS rbServiceSpecification_0_service_id,
                    rbServiceSpecification_0.`price` AS rbServiceSpecification_0_price,
                    rbServiceSpecification_0.`date` AS rbServiceSpecification_0_date,
                    rbServiceSpecification_0.`name` AS rbServiceSpecification_0_name,
                    rbServiceSpecification_0.`title` AS rbServiceSpecification_0_title
                FROM rbServiceSpecification AS rbServiceSpecification_0
                WHERE ((rbServiceSpecification_0.`date` = '{begDate}'))
            ) AS q6 ON rbServiceSpecification_1.`service_id` = q6.`rbServiceSpecification_0_service_id`
        WHERE (
            (ISNULL(q6.`rbServiceSpecification_0_service_id`))
            AND (rbServiceSpecification_1.`date` = '{endDate}')
        )
    ''',
    # Изменить наименование/стоимость следующих услуг
    # (запрос вытащен из конструктора отчетов (pes, s11))
    u'''
        SELECT
            rbService_9.`code` AS rCode,
            IF(
                (q14.`rbServiceSpecification_7_name`='')AND(q14.`rbServiceSpecification_7_title`=''),
                rbService_9.`name`,
                q14.`rbServiceSpecification_7_name`
            ) AS rName,
            q14.`rbServiceSpecification_7_price` AS rPrice
        FROM
            rbServiceSpecification AS rbServiceSpecification_8
            INNER JOIN (
                SELECT
                    rbServiceSpecification_7.`service_id` AS rbServiceSpecification_7_service_id,
                    rbServiceSpecification_7.`price` AS rbServiceSpecification_7_price,
                    rbServiceSpecification_7.`date` AS rbServiceSpecification_7_date,
                    rbServiceSpecification_7.`name` AS rbServiceSpecification_7_name,
                    rbServiceSpecification_7.`title` AS rbServiceSpecification_7_title
                FROM
                    rbServiceSpecification AS rbServiceSpecification_7
            ) AS q14 ON rbServiceSpecification_8.`service_id` = q14.`rbServiceSpecification_7_service_id`
            INNER JOIN rbService AS rbService_9 ON rbServiceSpecification_8.`service_id` = rbService_9.`id`
            INNER JOIN ActionType ON rbService_9.id = ActionType.nomenclativeService_id
            INNER JOIN OrgStructure_ActionType ON OrgStructure_ActionType.actionType_id = ActionType.id
        WHERE (
            (q14.`rbServiceSpecification_7_date` = '{endDate}')
            AND (rbServiceSpecification_8.`date` = '{begDate}')
            AND (
                (
                    (rbServiceSpecification_8.`price` <> q14.`rbServiceSpecification_7_price`)
                    OR (
                        (
                            (rbServiceSpecification_8.`name` <> q14.`rbServiceSpecification_7_name`)
                            AND (q14.`rbServiceSpecification_7_name`!='')
                        )
                    )
                    OR (
                        (
                            (q14.`rbServiceSpecification_7_name`='')
                            AND (rbServiceSpecification_8.`title` <> q14.`rbServiceSpecification_7_title`)
                        )
                    )
                )
            )
        )
    '''
]


def selectData(params, reportNumber=0):
    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())

    stmt = RServiceSpecificationQuery[reportNumber]

    stmt = stmt.replace('{begDate}', begDate.toString('yyyy-MM-dd'))
    stmt = stmt.replace('{endDate}', endDate.toString('yyyy-MM-dd'))

    query = db.query(stmt)

    data = []
    while query.next():
        record = query.record()
        data.append({
            'code': forceString(record.value('rCode')),
            'name': forceString(record.value('rName')),
            'price': forceDouble(record.value('rPrice'))
        })
    return query, data


class CReportServiceSpecificationSetupDialog(QtGui.QDialog, Ui_ReportServiceSpecification):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        currentDate = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate(currentDate.year(), currentDate.month(), 1)))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate(currentDate.year(), currentDate.month(), currentDate.daysInMonth())))

    def accept(self):
        if not self.edtBegDate.date().isValid() or not self.edtEndDate.date().isValid() or self.edtBegDate.date() > self.edtEndDate.date():
            QtGui.QMessageBox.critical(
                QtGui.qApp.mainWindow,
                u'Внимание!',
                u'Неверно задан период. ',
                QtGui.QMessageBox.Ok
            )
            return
        QtGui.QDialog.accept(self)

    def params(self):
        return {
            'begDate': self.edtBegDate.date(),
            'endDate': self.edtEndDate.date()
        }


class CReportServiceSpecification(CReport):

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u"Отчет")
        self.reportNumber = 0

    def getSetupDialog(self, parent):
        result = CReportServiceSpecificationSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        doc = QtGui.QTextDocument()

        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('33?', [u'Код услуги'], CReportBase.AlignLeft),
            ('33?', [u'Наименование услуги'], CReportBase.AlignLeft),
            ('33?', [u'Цена'], CReportBase.AlignLeft)
        ]

        table = createTable(cursor, tableColumns)

        query, data = selectData(params, self.reportNumber)
        self.setQueryText(forceString(query.lastQuery()))

        for x in data:
            i = table.addRow()
            table.setText(i, 0, forceString(x['code']))
            table.setText(i, 1, forceString(x['name']))
            table.setText(i, 2, forceString(x['price']))

        return doc
