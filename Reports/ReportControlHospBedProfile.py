# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from library.Utils import forceInt, forceString, forceDate
from Orgs.Utils import getOrgStructureDescendants, getOrgStructureFullName
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Ui_ReportControlHospBedProfile import Ui_ReportControlHospBedProfile

def selectData(params):
    db = QtGui.qApp.db
    begDate         = params.get('begDate')
    endDate         = params.get('endDate')
    orgStructureId  = params.get('orgStructureId', None)
    financeId       = params.get('financeId', None)

    tableContract = db.table('Contract')
    tableHosBedProfile = db.table('rbHospitalBedProfile')
    tableEvent = db.table('Event')

    cond = [tableEvent['execDate'].ge(begDate),
            tableEvent['execDate'].le(endDate)]


    allowedCodes = ['02', '03', '05', '06', '07', '08', '11',
                    '12', '13', '14', '15', '16', '17', '18',
                    '19', '20', '21', '22', '23', '24', '25',
                    '26', '27', '28', '29', '30', '31', '32',
                    '33', '35', '36', '37', '38', '39', '40',
                    '42', '45', '47', '48', '49', '50', '51',
                    '52', '53', '54', '55', '56', '59', '60',
                    '61', '62', '63', '64', '65', '66', '67',
                    '68', '69', '70', '71', '72', '73', '74',
                    '77', '78', '84', '85', '87', '88', '91',
                    '92', '94', '96', '97', '98', '99', '1A',
                    '1B', '1C', '1D', '1E', '1F', '1G', '1H',
                    '1I', '1J', '1K', '1L', '1M', '1N', '1O',
                    '1P', '1R', '1S', '1T', '1U', '1V', '1W',
                    '1X', '1Y', '1Z', '2A', '2B', '2C']
    childAllowedCodes = ['06', '08', '12', '14', '16', '18',
                         '20', '22', '24', '28', '31', '33',
                         '35', '37', '45', '48', '50', '54',
                         '56', '60', '61', '62', '65', '67',
                         '69', '77', '78', '85', '88', '91',
                         '96', '98', '99', '1A', '1D', '1F',
                         '1J', '1L', '1N', '1T', '1W', '1Y',
                         '2A', '2C']
    adultAllowedCodes = ['02', '03', '05', '07', '11', '13',
                         '15', '17', '19', '21', '23', '25',
                         '26', '27', '29', '30', '32', '36',
                         '38', '39', '40', '42', '47', '49',
                         '51', '52', '53', '55', '59', '63',
                         '64', '66', '68', '70', '71', '72',
                         '73', '74', '84', '87', '92', '94',
                         '97', '1B', '1C', '1E', '1G', '1H',
                         '1I', '1K', '1M', '1O', '1P', '1R',
                         '1S', '1U', '1V', '1X', '1Z', '2B']


    hospBedCond = tableHosBedProfile['code'].notInlist(allowedCodes) + \
        ' OR (age(Client.birthDate, Event.setDate) < 18 AND ' + tableHosBedProfile['code'].notInlist(childAllowedCodes) + ')' + \
        ' OR (age(Client.birthDate, Event.setDate) >= 18 AND ' + tableHosBedProfile['code'].notInlist(adultAllowedCodes) + ')'

    cond.append(hospBedCond)

    if orgStructureId:
        tableOrgStructure = db.table('OrgStructure')
        cond.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)))

    if financeId:
        cond.append(tableContract['finance_id'].eq(financeId))

    stmt = u''' SELECT
                    Client.id AS clientId,
                    CONCAT_WS(' ', Client.lastName, Client.firstName, Client.patrName) AS name,
                    Client.birthDate AS birthDate,
                    Event.setDate AS startDate,
                    Event.execDate AS finishDate,
                    OrgStructure.id AS orgId,
                    IF(%s, 'ref', 'age') AS control
                FROM
                    Event
                    INNER JOIN Client ON
                        Client.id = Event.client_id
                    INNER JOIN Action ON
                        Action.id = (   SELECT
                                            MAX(a.id)
                                        FROM
                                            ActionType at
                                            INNER JOIN Action a ON
                                                a.actionType_id = at.id
                                                AND a.deleted = 0
                                        WHERE
                                            a.event_id = Event.id
                                            AND at.flatCode = 'moving'
                                            AND at.deleted = 0          )
                    -- Finance
                    LEFT JOIN Contract ON
                        IF(Action.contract_id IS NOT NULL, Action.contract_id, Event.contract_id) = Contract.id
                    -- OrgStructure
                    LEFT JOIN ActionProperty AS ActPrOrg ON
                        ActPrOrg.action_id = Action.id
                        AND ActPrOrg.type_id = (SELECT
                                                    apt.id
                                                FROM
                                                    ActionPropertyType AS apt
                                                WHERE
                                                    apt.actionType_id = Action.actionType_id
                                                    AND apt.name = 'Отделение пребывания'
                                                    AND apt.deleted = 0                     )
                        AND ActPrOrg.deleted = 0
                    LEFT JOIN ActionProperty_OrgStructure ON
                        ActionProperty_OrgStructure.id = ActPrOrg.id
                    LEFT JOIN OrgStructure ON
                        OrgStructure.id = ActionProperty_OrgStructure.value
                    -- rbHospitalBedProfile
                    LEFT JOIN rbHospitalBedProfile ON
                        rbHospitalBedProfile.id =   (
                                                        SELECT
                                                            OrgStructure_HospitalBed.profile_id
                                                        FROM
                                                            ActionProperty AP
                                                            INNER JOIN ActionProperty_HospitalBed ON
                                                                ActionProperty_HospitalBed.id = AP.id
                                                            INNER JOIN OrgStructure_HospitalBed ON
                                                                OrgStructure_HospitalBed.id = ActionProperty_HospitalBed.value
                                                        WHERE
                                                            AP.action_id = Action.id
                                                        LIMIT 1
                                                    )
                WHERE
                    %s
                GROUP BY
                    Event.id
                ORDER BY
                    name''' % (tableHosBedProfile['code'].notInlist(allowedCodes), db.joinAnd(cond))
    return db.query(stmt)


class CReportControlHospBedProfile(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Контроль обращений по профилям коек')

    def getSetupDialog(self, parent):
        result = CControlHospBedProfileDialog(parent)
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
        rows = []
        if begDate or endDate:
            rows.append(u'за период' + dateRangeAsStr(begDate, endDate))
        if financeId:
            rows.append(u'Тип финансирования: ' + forceString(QtGui.qApp.db.translate('rbFinance', 'id', financeId, 'name')))
        if orgStructureId:
            rows.append(u'Подразделение: ' + getOrgStructureFullName(orgStructureId))
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
        Подразделение -(отображается полное наименование от головного до конечного)
        Контроль - отображается наименование сработавшего контроля.'''
        tableColumns = [('2%', [u'№'], CReportBase.AlignLeft),
                        ('8%', [u'Код пациента'], CReportBase.AlignLeft),
                        ('15%', [u'ФИО'], CReportBase.AlignLeft),
                        ('8%', [u'Д/р'], CReportBase.AlignLeft),
                        ('14%', [u'Период лечения'], CReportBase.AlignLeft),
                        ('15%', [u'Подразделение'], CReportBase.AlignLeft),
                        ('8%', [u'Контроль'], CReportBase.AlignLeft),
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
                forceString(forceDate(record.value('startDate')).toString('dd.MM.yyyy') + ' - ' + forceDate(record.value('finishDate')).toString('dd.MM.yyyy')),
                getOrgStructureFullName(record.value('orgId')),
                (u'Код профиля койки не соответствует справочнику'
                 if record.value('control') == 'ref'
                 else u'Профиль койки не соответствует возрасту пациента')
            )
            for col, val in enumerate(fields):
                table.setText(row, col, val)
        return doc


class CControlHospBedProfileDialog(QtGui.QDialog, Ui_ReportControlHospBedProfile):
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