# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from library.Utils import forceInt, forceString, forceDate
from Orgs.Utils import getOrgStructureDescendants, getOrgStructureFullName
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Ui_ReportControlDischargeSetup import Ui_ReportControlDischargeSetup

def selectData(params):
    stmt = u'''
                Select
                    Client.id as clientId,
                    Event.externalId as externalId,
                    CONCAT_WS(' ', Client.lastName, Client.firstName, Client.patrName) as clientName,
                    Client.birthDate as birthDate,
                    Event.setDate as setDate,
                    Event.execDate as execDate,
                    OrgStructure.code as orgStructureCode,
                    OrgStructure.name as orgStructureName,
                    OrgStructure.id as orgStructureId,
                    PersonSpec.code as execPersonCode,
                    PersonSpec.name as execPersonName

                From Event
                    inner join EventType
                        on Event.eventType_id = EventType.id
                    inner join rbEventProfile
                        on EventType.eventProfile_id = rbEventProfile.id

                    inner join Action
                        on Action.id = (
                            Select
                                MAX(a.id)
                            From
                                Action a
                                inner join ActionType at
                                    on a.actionType_id = at.id
                                    and a.deleted = 0
                            Where
                                (a.event_id = Event.id)
                                and (at.flatCode = 'moving')
                        )

                    inner join ActionProperty
                        on ActionProperty.action_id = Action.id
                    inner join ActionPropertyType
                        on ActionPropertyType.id = ActionProperty.type_id

                    left join ActionProperty_OrgStructure
                        on ActionProperty_OrgStructure.id = ActionProperty.id
                    left join OrgStructure
                        on OrgStructure.id = ActionProperty_OrgStructure.value

                    inner join vrbPersonWithSpeciality as PersonSpec
                        on PersonSpec.id = Event.execPerson_id
                    inner join Client
                        on Client.id = Event.client_id
                    %(joinTableContract)s
                    Where
                        (Event.deleted = 0 )
                        and (Action.deleted = 0)
                        and (Client.deleted = 0)
                        and (Event.execDate is not null)
                        and (ActionProperty.deleted = 0)
                        and (ActionPropertyType.name = 'Отделение пребывания')
                        and (rbEventProfile.code in ('11', '12', '41', '42', '43', '51', '52', '71', '72', '90'))
                        and (not Exists (
                            Select
                                a.id
                            From
                                Action a
                                inner join ActionType at
                                    on at.id = a.actionType_id
                            where
                                (a.event_id = Event.id)
                                and (at.flatCode = 'leaved')
                        ))
                        %(cond)s
                Order by clientName'''
    db = QtGui.qApp.db
    begDate         = params.get('begDate')
    endDate         = params.get('endDate')
    orgStructureId  = params.get('orgStructureId', None)
    typeFinanceId       = params.get('typeFinanceId', None)

    tableContract = db.table('Contract')
    tableEvent = db.table('Event')
    joinTableContract = u''

    cond = [tableEvent['execDate'].ge(begDate),
            tableEvent['execDate'].le(endDate)]
    if orgStructureId:
        tableOrgStructure = db.table('OrgStructure')
        cond.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)))

    if typeFinanceId:
        cond.append(tableContract['finance_id'].eq(typeFinanceId))
        joinTableContract = u'''inner join Contract
		    on Contract.id = Event.contract_id'''
    cond = u'and' + db.joinAnd(cond)
    return db.query(stmt %{'joinTableContract': joinTableContract,
                           'cond': cond})

def getOrgName(orgID):
    db = QtGui.qApp.db
    table = db.table('Organisation')
    return forceString(db.translate(table,'id',orgID, 'shortName'))

class CReportControlDischarge(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Список пациентов стационара, в истории болезни которых, отсутствует действие "Выписка"')

    def getSetupDialog(self, parent):
        result = CReportControlDischargeDialog(parent)
        result.setTitle(u'Контроль наличия действия "Выписка"')
        return result

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
        Код - client.id
        Внешний идентификатор - внешний идентификатор истории болезни, при его отсутствии поле остается пустым
        ФИО пациента - Фамилия имя отчество полностью
        Дата рождения - дата рождения пациента
        Период лечения - event.setDate-event.execDate
        Подразделение - для ActionPoretyType.Name = 'Отделение пребывания'
        Врач - Event.execPerson_id - лечащий врач'''
        tableColumns = [
            ('4%', [u'№ п/п'], CReportBase.AlignLeft),
            ('4%', [u'Код'], CReportBase.AlignLeft),
            ('8%', [u'Внешний идентификатор'], CReportBase.AlignLeft),
            ('15%', [u'ФИО пациента'], CReportBase.AlignLeft),
            ('8%', [u'Д/р'], CReportBase.AlignLeft),
            ('10%', [u'Период лечения'], CReportBase.AlignLeft),
            ('20%', [u'Подразделение'], CReportBase.AlignLeft),
            ('20%', [u'Врач'], CReportBase.AlignLeft),
            ]
        table = createTable(cursor, tableColumns)
        while query.next():
            record = query.record()
            row = table.addRow()
            fields = (
                row,
                forceInt(record.value('clientId')),
                forceString(record.value('externalId')),
                forceString(record.value('clientName')),
                forceString(forceDate(record.value('birthDate')).toString('dd.MM.yyyy')),
                forceString(forceDate(record.value('setDate')).toString('dd.MM.yyyy') + ' - ' + forceDate(record.value('execDate')).toString('dd.MM.yyyy')),
                forceString(getOrgStructureFullName(record.value('orgStructureId'))),
                forceString((record.value('execPersonCode')).toString() + u' ' + (record.value('execPersonName')).toString())
            )

            for col, val in enumerate(fields):
                table.setText(row, col, val)
        return doc

class CReportControlDischargeDialog(QtGui.QDialog, Ui_ReportControlDischargeSetup):
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
        self.cmbFinance.setValue(params.get('typeFinanceId', 2))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['typeFinanceId'] = self.cmbFinance.value()
        return result