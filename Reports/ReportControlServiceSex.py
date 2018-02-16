# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from library.Utils import forceInt, forceString, forceDate
from Orgs.Utils import getOrgStructureDescendants, getOrgStructureFullName
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Ui_ReportControlServiceSex import Ui_Dialog


def selectData(params):
    db = QtGui.qApp.db
    begDate         = params.get('begDate')
    endDate         = params.get('endDate')
    orgStructureId  = params.get('orgStructureId', None)
    financeId       = params.get('financeId', None)

    tableContract = db.table('Contract')
    tableKSG = db.table('mes.MES').alias('ksg')
    tablePerson = db.table('Person')
    tableService = db.table('rbService')
    tableActionService = db.table('ActionType').alias('actService')
    tableEvent = db.table('Event')
    tableVrbPersonWithSpeciality = db.table('vrbPersonWithSpeciality')

    cond = [tableEvent['execDate'].ge(begDate),
            tableEvent['execDate'].le(endDate)]

    if orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    if financeId:
        cond.append(tableContract['finance_id'].eq(financeId))

    womanCSGList = (
        'G10.30.202',
        'G10.29.191',
        'G10.30.202',
        'G10.30.202',
        'G10.30.202',
        'G10.30.209',
        'G40.30.202',
        'G40.30.202',
        'G40.30.202',
        'G40.30.202',
        'G50.30.202',
        'G50.30.202',
        'G50.30.202',
        'G50.30.202'
    )

    codeConds = [
        tableService['code'].like('B__.001.%'),
        tableActionService['code'].like('B__.001.%'),
        tableKSG['code'].like('G__.02.%'),
        tableKSG['code'].inlist(womanCSGList)
    ]

    controlCond = 'Client.sex = 1 AND (' + codeConds[0] + ' OR ' + codeConds[1] + ' OR ' + codeConds[2] + ') OR ' + 'Client.sex = 2 AND ' + codeConds[3]
    cond.append(controlCond)

    stmt = u''' SELECT
                    Client.id AS clientId,
                    CONCAT_WS(' ', Client.lastName, Client.firstName, Client.patrName) AS name,
                    Client.birthDate AS birthDate,
                    IF(Client.sex = 1, 'М', 'Ж') AS sex,
                    Event.setDate AS startDate,
                    Event.execDate AS finishDate,
                    CONCAT_WS(' ', vrbPersonWithSpeciality.code, vrbPersonWithSpeciality.name) AS personName,
                    Person.orgStructure_id AS orgId,
                    CASE
                        WHEN %s THEN CONCAT_WS(' ', rbService.code, rbService.name)
                        WHEN %s THEN CONCAT_WS(' ', actService.code, actService.name)
                        WHEN %s THEN CONCAT_WS(' ', ksg.code, ksg.name)
                    END AS service
                FROM
                    Client
                    INNER JOIN Event ON
                        Client.id = Event.client_id
                    LEFT JOIN Action ON
                        Action.event_id = Event.id
                        AND Action.deleted = 0
                    LEFT JOIN Contract ON
                        IF(Action.contract_id IS NOT NULL, Action.contract_id, Event.contract_id) = Contract.id
                    LEFT JOIN Person ON
                        Event.execPerson_id = Person.id
                    LEFT JOIN vrbPersonWithSpeciality ON Event.execPerson_id = vrbPersonWithSpeciality.id
                    -- Service from visit
                    LEFT JOIN Visit ON
                        Visit.event_id = Event.id
                        AND Visit.deleted = 0
                    LEFT JOIN rbService ON
                        rbService.id = Visit.service_id
                    -- Service from action
                    LEFT JOIN ActionType AS actService ON
                        Action.actionType_id = actService.id
                    -- KSG
                    LEFT JOIN mes.MES AS ksg ON
                        Event.MES_id = ksg.id
                WHERE
                    %s
                GROUP BY
                    Event.id
                ORDER BY
                    name
    ''' % (
        codeConds[0],
        codeConds[1],
        db.joinOr(codeConds[2:]),
        db.joinAnd(cond)
    )

    return db.query(stmt)


class CReportControlServiceSex(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Контроль услуг по полу пациента')

    def getSetupDialog(self, parent):
        result = CControlServiceSexDialog(parent)
        result.setTitle(self.title())
        return result

    def getDescription(self, params):
        def dateRangeAsStr(begDate, endDate):
            result = ''
            if begDate:
                result += u' с '+forceString(begDate)
            if endDate:
                result += u' по '+forceString(endDate)
            return result
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        financeId = params.get('financeId', None)
        orgStructureId = params.get('orgStructureId', None)
        reportDate = params.get('reportDate')
        rows = []
        if begDate or endDate:
            rows.append(u'за период' + dateRangeAsStr(begDate, endDate))
        if financeId:
            rows.append(u'Тип финансирования: ' + forceString(QtGui.qApp.db.translate('rbFinance', 'id', financeId, 'name')))
        if orgStructureId:
            rows.append(u'Подразделение: ' + getOrgStructureFullName(orgStructureId))
        if reportDate:
            rows.append(u'отчёт составлен: '+forceString(reportDate))
        else:
            rows.append(u'отчёт составлен: '+forceString(QtCore.QDateTime.currentDateTime()))

        return rows

    def build(self, params):
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        u'''№ п/п - порядковый номер записи в таблице
        Код пациента - client.id
        ФИО пациента - Фамилия имя отчество полностью
        Дата рождения - дата рождения пациента
        Период лечения - event.setDate-event.execDate
        Врач — Код, имя полностью
        Подразделение -(отображается полное наименование от головного до конечного)
        Контроль - отображается наименование сработавшего контроля.'''
        tableColumns = [(' 2%', [u'№'], CReportBase.AlignLeft),
                        (' 8%', [u'Код пациента'], CReportBase.AlignLeft),
                        ('15%', [u'ФИО'], CReportBase.AlignLeft),
                        (' 10%', [u'Д/р'], CReportBase.AlignLeft),
                        (' 2%', [u'Пол'], CReportBase.AlignLeft),
                        ('10%', [u'Период лечения'], CReportBase.AlignLeft),
                        ('15%', [u'Врач'], CReportBase.AlignLeft),
                        ('20%', [u'Подразделение'], CReportBase.AlignLeft),
                        ('20%', [u'Код и наименование услуги'], CReportBase.AlignLeft),
                        ]
        table = createTable(cursor, tableColumns)

        while query.next():
            record = query.record()
            row = table.addRow()
            fields = (
                row,
                forceInt(record.value('clientId')),
                forceString(record.value('name')),
                forceString(record.value('birthDate')),
                forceString(record.value('sex')),
                forceString(forceDate(record.value('startDate')).toString('dd.MM.yyyy') + ' - ' + forceDate(record.value('finishDate')).toString('dd.MM.yyyy')),
                forceString(record.value('personName')),
                getOrgStructureFullName(record.value('orgId')),
                forceString(record.value('service'))
            )
            for col, val in enumerate(fields):
                table.setText(row, col, val)
        return doc


class CControlServiceSexDialog(QtGui.QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbFinance.setTable('rbFinance')

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        curDate = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate(curDate.year(), curDate.month(), 1)))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate(curDate.year(), curDate.month(), curDate.daysInMonth())))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbFinance.setValue(params.get('financeId', 2))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['financeId'] = self.cmbFinance.value()
        return result
