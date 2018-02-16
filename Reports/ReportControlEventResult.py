# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from Orgs.Utils import getOrgStructureFullName

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from library.Utils import forceString, forceDate, forceInt
from Reports.Ui_ReportControlEventResultSetup import Ui_ReportControlEventResultSetup

def selectData(params):
    stmt = u'''
SELECT
    Client.id AS clientId,
    CONCAT_WS(' ', Client.lastName, Client.firstName, Client.patrName) AS clientName,
    Client.birthDate,
    Event.setDate,
    Event.execDate,
    CONCAT_WS(' ', vrbPersonWithSpeciality.code, vrbPersonWithSpeciality.name) AS person,
    Person.orgStructure_id,
    rbEventProfile.code AS eventProfileCode,
    rbResult.regionalCode AS resultCode,
    rbDiagnosticResult.regionalCode AS diagnosticResultCode
FROM
    Event
    INNER JOIN EventType ON Event.eventType_id = EventType.id
    INNER JOIN Client ON Event.client_id = Client.id
    INNER JOIN Person ON Event.execPerson_id = Person.id
    INNER JOIN vrbPersonWithSpeciality ON Person.id = vrbPersonWithSpeciality.id
    INNER JOIN Contract ON Event.contract_id = Contract.id
    INNER JOIN Diagnostic ON Diagnostic.event_id = Event.id
    INNER JOIN rbResult ON Event.result_id = rbResult.id
    INNER JOIN rbDiagnosticResult ON Diagnostic.result_id = rbDiagnosticResult.id
    INNER JOIN rbEventProfile ON EventType.eventProfile_id = rbEventProfile.id
WHERE
    %s
    '''

    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    orgStructureId = params.get('orgStructureId', None)
    financeId = params.get('typeFinanceId', None)

    tableEvent = db.table('Event')
    tableEventType = db.table('EventType')
    tableClient = db.table('Client')
    tablePerson = db.table('Person')
    tableContract = db.table('Contract')
    tableDiagnostic = db.table('Diagnostic')

    cond = [
        tableEvent['deleted'].eq(0),
        tableEventType['deleted'].eq(0),
        tableClient['deleted'].eq(0),
        tablePerson['deleted'].eq(0),
        tableContract['deleted'].eq(0),
        tableDiagnostic['deleted'].eq(0),
        tableEvent['execDate'].dateGe(begDate),
        tableEvent['execDate'].dateLe(endDate)
    ]
    if orgStructureId is not None:
        cond.append(db.joinOr([
            tablePerson['orgStructure_id'].eq(orgStructureId),
            tablePerson['orgStructure_id'].inInnerStmt(
                "(SELECT id FROM OrgStructure_Ancestors WHERE fullPath LIKE '%" + str(orgStructureId) + "%')"
            )
        ]))
    if financeId is not None:
        cond.append(tableContract['finance_id'].eq(financeId))

    return db.query(stmt % db.joinAnd(cond))


class CReportControlEventResultSetupDialog(QtGui.QDialog, Ui_ReportControlEventResultSetup):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        currentDate = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate(currentDate.year(), currentDate.month(), 1)))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate(currentDate.year(), currentDate.month(), currentDate.daysInMonth())))

        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))

        self.cmbFinance.setTable('rbFinance', addNone=True)
        self.cmbFinance.setValue(params.get('typeFinanceId', 2))  # 2 -- код ОМС. Может, лучше бы не плодить магические константы?

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
            'endDate': self.edtEndDate.date(),
            'orgStructureId': self.cmbOrgStructure.value(),
            'typeFinanceId': self.cmbFinance.value()
        }


class CReportControlEventResult(CReport):

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u"Контроль исхода (результата) лечения и обращения")

    def getSetupDialog(self, parent):
        result = CReportControlEventResultSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        doc = QtGui.QTextDocument()

        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Проверка результатов лечения и обращения в событии')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('3%',  [u'№ п/п'], CReportBase.AlignLeft),
            ('5%',  [u'Код пациента'], CReportBase.AlignLeft),
            ('20%', [u'ФИО пациента'], CReportBase.AlignLeft),
            ('10%', [u'Дата рождения'], CReportBase.AlignLeft),
            ('10%', [u'Период лечения'], CReportBase.AlignLeft),
            ('20%', [u'Врач'], CReportBase.AlignLeft),
            ('10%', [u'Подразделение'], CReportBase.AlignLeft),
            ('10%', [u'Контроль'], CReportBase.AlignLeft),
        ]
        table = createTable(cursor, tableColumns)

        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))

        # ep - eventProfileCode, r - resultCode, dr - diagnosticResultCode
        checks = [
            (
                u'Результат лечения не соответствует условию оказания мед помощи',
                lambda ep, r, dr:
                    ep in ['11', '12', '301', '302', '401', '402'] and dr not in [str(x) for x in range(101, 106)]
                    or ep in ['41', '42', '43', '51', '52', '71', '72', '90'] and dr not in [str(x) for x in range(201, 206)]
                    or ep in ['01', '02', '21', '22', '31', '32', '60', '111', '112', '201', '202', '211', '232', '241', '242', '252', '261', '262'] and dr not in [str(x) for x in range(301, 308)]
                    or ep in ['801', '802'] and dr not in [str(x) for x in range(401, 405)]
            ),
            (
                u'Результат обращения не соответствует условию оказания мед помощи',
                lambda ep, r, dr:
                    ep in ['11', '12', '301', '302', '401', '402'] and r not in [str(x) for x in range(101, 111)]
                    or ep in ['41', '42', '43', '51', '52', '71', '72', '90'] and r not in [str(x) for x in range(201, 209)]
                    or ep in ['01', '02', '21', '22', '31', '32', '60', '111', '112', '201', '202', '211', '232', '241', '242', '252', '261', '262'] and r not in [str(x) for x in range(301, 317)]
                    or ep in ['801', '802'] and dr not in [str(x) for x in range(401, 417)]
            ),
            (
                u'Результат лечения не применяется для диспансеризации',
                lambda ep, r, dr:
                    ep in ['211', '232', '252', '261', '262'] and dr not in ['304', '306']
            ),
            (
                u'Результат обращения не применяется для диспансеризации взрослого населения',
                lambda ep, r, dr:
                    ep in ['211', '261'] and r not in ['317', '318', '355', '356']
            ),
            (
                u'Результат обращения не применяется для диспансеризации детского населения',
                lambda ep, r, dr:
                    ep in ['232', '252', '262'] and r not in ['317', '318', '319', '320', '321']
            )
        ]

        while query.next():
            record = query.record()
            eventProfileCode = forceString(record.value('eventProfileCode'))
            resultCode = forceString(record.value('resultCode'))
            diagnosticResultCode = forceString(record.value('diagnosticResultCode'))
            if any([check[1](eventProfileCode, resultCode, diagnosticResultCode) for check in checks]):
                i = table.addRow()
                table.setText(i, 0, i)
                table.setText(i, 1, forceString(record.value('clientId')))
                table.setText(i, 2, forceString(record.value('clientName')))
                table.setText(i, 3, forceString(record.value('birthDate')))
                table.setText(i, 4, forceDate(record.value('setDate')).toString('dd.MM.yyyy') + '-' + forceDate(record.value('execDate')).toString('dd.MM.yyyy'))
                table.setText(i, 5, forceString(record.value('person')))
                table.setText(i, 6, getOrgStructureFullName(forceInt(record.value('orgStructure_id'))))
                table.setText(i, 7, u'\n'.join([check[0] for check in checks if check[1](eventProfileCode, resultCode, diagnosticResultCode)]))

        return doc

