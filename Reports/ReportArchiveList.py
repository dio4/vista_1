# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.Ui_ReportArchiveListSetup import Ui_ReportArchiveListSetupDialog
from library.Utils import forceString, forceDate


def selectData(params):
    stmt = u'''
SELECT DISTINCT
    CONCAT_WS(' ', Client.lastName, Client.firstName, Client.patrName) AS clientName,

    (
        SELECT
            OS.name
        FROM
            ActionPropertyType AS APT
            INNER JOIN ActionProperty AS AP ON AP.type_id=APT.id
            INNER JOIN ActionProperty_OrgStructure AS APOS ON APOS.id=AP.id
            INNER JOIN OrgStructure AS OS ON OS.id=APOS.value
        WHERE
            APT.actionType_id = A2.actionType_id
            AND AP.action_id = A2.id
            AND APT.deleted = 0
            AND (APT.name LIKE 'Отделение')
            AND OS.deleted = 0
        LIMIT 1
    )
    AS orgStructureName,

    Event.id as eventId,
    Event.externalId,

    age(Client.birthDate, A1.begDate) AS clientAge,

    (
        SELECT
            APS.value
        FROM
            ActionPropertyType AS APT
            INNER JOIN ActionProperty AS AP ON AP.type_id=APT.id
            INNER JOIN ActionProperty_String AS APS ON APS.id=AP.id
        WHERE
            APT.actionType_id = A1.actionType_id
            AND AP.action_id = A1.id
            AND APT.deleted = 0
            AND (APT.name LIKE 'Кем направлен')
        LIMIT 1
    )
    AS sender,

    IF (
        Event.order = 1,
        'плановый',
        IF (
            Event.order = 2,
            'экстренный',
            NULL
        )
    ) AS orderEvent,

    (
        SELECT
            Diagnosis.MKB
        FROM
            Diagnosis
            INNER JOIN Diagnostic ON Diagnostic.diagnosis_id = Diagnosis.id
            INNER JOIN rbDiagnosisType ON Diagnostic.diagnosisType_id = rbDiagnosisType.id
        WHERE
            Diagnostic.event_id = Event.id
            AND Diagnosis.deleted = 0
            AND Diagnostic.deleted = 0
            AND (
                rbDiagnosisType.code = '1'
                OR (
                    rbDiagnosisType.code = '2' AND Diagnostic.person_id = Event.execPerson_id
                    AND (
                        NOT EXISTS (
                            SELECT
                                DC.id
                            FROM
                                Diagnostic AS DC
                                INNER JOIN rbDiagnosisType AS DT ON DT.id = DC.diagnosisType_id
                            WHERE
                                DT.code = '1'
                                AND DC.event_id = Event.id
                        )
                    )
                )
            )
        LIMIT 1
    )
    AS MKB,

    A1.begDate,
    A2.begDate as endDate,

    IF (
        datediff(A2.begDate, A1.begDate) = 0,
        1,
        datediff(A2.begDate, A1.begDate)
    )
    AS days,

    rbResult.name AS result
FROM
    Event
    INNER JOIN Client ON Client.id = Event.client_id
    INNER JOIN Action A1 ON Event.id = A1.event_id
    INNER JOIN Action A2 ON Event.id = A2.event_id
    INNER JOIN Diagnostic ON Event.id = Diagnostic.event_id
    INNER JOIN rbResult ON Event.result_id = rbResult.id
WHERE
    A1.actionType_id IN (SELECT id FROM ActionType where name = 'Поступление')
    AND A2.actionType_id IN (SELECT id FROM ActionType where name = 'Выписка')
    AND DATE(A2.begDate) >= DATE('%s')
    AND DATE(A2.begDate) <= DATE('%s')
ORDER BY
    Client.lastName
    '''

    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())

    return db.query(stmt % (begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd')))

class CReportArchiveListSetupDialog(QtGui.QDialog, Ui_ReportArchiveListSetupDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        currentDate = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate(currentDate.year(), currentDate.month(), 1)))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate(currentDate.year(), currentDate.month(), currentDate.daysInMonth())))

    def params(self):
        return {
            'begDate': self.edtBegDate.date(),
            'endDate': self.edtEndDate.date()
        }


class CReportArchiveList(CReport):

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u"Архивный листок")

    def getSetupDialog(self, parent):
        result = CReportArchiveListSetupDialog(parent)
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
            ('5%',  [u'№ п/п'], CReportBase.AlignLeft),
            ('17%', [u'ФИО пациента'], CReportBase.AlignLeft),
            ('15%', [u'Отделение'], CReportBase.AlignLeft),
            ('5%', [u'№ истории болезни'], CReportBase.AlignLeft),
            ('5%', [u'Возраст, лет'], CReportBase.AlignLeft),
            ('5%', [u'Направл.'], CReportBase.AlignLeft),
            ('5%', [u'Госпит.'], CReportBase.AlignLeft),
            ('8%', [u'Диагноз'], CReportBase.AlignLeft),
            ('10%', [u'Дата поступления в ст.'], CReportBase.AlignLeft),
            ('10%', [u'Дата выписки'], CReportBase.AlignLeft),
            ('5%', [u'Общ. к/д'], CReportBase.AlignLeft),
            ('10%', [u'Исх.'], CReportBase.AlignLeft),
        ]
        table = createTable(cursor, tableColumns)

        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))

        while query.next():
            record = query.record()
            i = table.addRow()
            table.setText(i, 0, i)
            table.setText(i, 1, forceString(record.value('clientName')))
            table.setText(i, 2, forceString(record.value('orgStructureName')))
            table.setText(i, 3, forceString(record.value('externalId')))
            table.setText(i, 4, forceString(record.value('clientAge')))
            table.setText(i, 5, forceString(record.value('sender')))
            table.setText(i, 6, forceString(record.value('orderEvent')))
            table.setText(i, 7, forceString(record.value('MKB')))
            table.setText(i, 8, forceDate(record.value('begDate')).toString('dd.MM.yyyy'))
            table.setText(i, 9, forceDate(record.value('endDate')).toString('dd.MM.yyyy'))
            table.setText(i, 10, forceString(record.value('days')))
            table.setText(i, 11, forceString(record.value('result')))

        return doc

