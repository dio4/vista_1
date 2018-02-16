# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from library.Utils import forceInt, forceString
from Orgs.Utils import getOrgStructureDescendants
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Ui_ReportBedspacePEOForm1Setup import Ui_ReportBedspacePEOForm1Setup

def selectData(params):
    stmt = u'''
        Select
            Result.orgStructureId,
            Result.orgStructureName,
            Result.bedProfileName,
            Sum(Result.quantity)as quantity,
            Sum(Result.treated) as treated,
            Sum(Result.days) as days
        From
        (
        (
            Select
                os.id as orgStructureId,
                os.name as orgStructureName,
                hbp.id as bedProfileId,
                hbp.name as bedProfileName,
                Count(hbp.id) as quantity,
                0 as treated,
                0 AS days
            From
                OrgStructure as os
                left join OrgStructure_HospitalBed oshb
                    on oshb.master_id = os.id
                inner join rbHospitalBedProfile hbp
                    on hbp.id = oshb.profile_id
            Where
                %(orgStructureCond)s
            Group by hbp.id, os.id
        )
        Union
        (
            Select
                os.id as orgStructureId,
                os.name as orgStructureName,
                hbp.id as bedProfileId,
                hbp.name as bedProfileName,
                0 as quantity,
                0 as treated,
                sum(if (os.hasDaystationary, datediff(m2.endDate, m1.endDate) + 1, datediff(m2.endDate, m1.endDate))) as days
            From Event
                inner join
                    (Select e.id as eventId,
                        a.endDate as endDate,
                        a.id as actionId,
                        at.flatCode
                    From Event e
                        inner join Action a
                            on a.event_id = e.id
                        inner join ActionType at
                            on at.id = a.actionType_id
                        %(movingJoin)s
                    Where  a.deleted = 0
                        and at.deleted = 0
                        and a.endDate is not null
                        and at.flatCode in ('moving')
                        %(movingCond)s
                    ) as m1
                    on m1.eventId = Event.id
                inner join
                    (Select e.id as eventId,
                        a.endDate as endDate,
                        a.id as actionId,
                        at.flatCode
                    From Event e
                        inner join Action a
                            on a.event_id = e.id
                        inner join ActionType at
                            on at.id = a.actionType_id
                        %(movingJoin)s
                    Where  a.deleted = 0
                        and at.deleted = 0
                        and a.endDate is not null
                        and at.flatCode in ('moving', 'leaved')
                        %(movingCond)s
                    ) as m2
                    on m2.eventId = Event.id
                    and m1.endDate <= m2.endDate
                    and m1.actionId != m2.actionId
                left join OrgStructure os
                    on os.id =
                        (Select apos.value
                        From ActionProperty as ap
                            left join ActionProperty_OrgStructure as apos
                                on apos.id = ap.id
                        Where ap.action_id = m1.actionId
                            and apos.value is not Null
                        Limit 0, 1
                        )
                left join rbHospitalBedProfile hbp
                    on hbp.id =
                        (Select aphbp.value
                        From ActionProperty as ap
                            left join ActionProperty_rbHospitalBedProfile as aphbp
                                on aphbp.id = ap.id
                        Where ap.action_id = m1.actionId
                            and aphbp.value is not Null
                        Limit 0, 1)
                inner join rbResult as r
                    on r.id = Event.result_id
            Where
                Exists(
                    Select a.id
                    From Action a
                    inner join ActionType at
                        on at.id = a.actionType_id
                    Where
                        a.event_id = Event.id
                        and at.flatCode = 'leaved'
                        and a.deleted = 0
                )
                and not isNull(Event.execDate)
                and (r.name LIKE 'Выписан%%'
                    or r.name LIKE '%%Умер%%'
                    or r.name LIKE 'Смерть%%'
                    or r.name LIKE 'Переведен%%')
            Group by hbp.id, os.id
            Order by m1.endDate, m2.endDate
        )
        Union
        (
            Select
                os.id as orgStructureId,
                os.name as orgStructureName,
                hbp.id as bedProfileId,
                hbp.name as bedProfileName,
                0 as quantity,
                Count(Event.id) as treated,
                0 as days
            From Event
                inner join Action
                    on Action.id =
                    (Select a.id
                    From Action a
                        inner join ActionType at
                            on at.id = a.actionType_id
                    Where  a.deleted = 0
                        and at.deleted = 0
                        and a.endDate is not null
                        and a.event_id = Event.id
                        and at.flatCode in ('moving')
                    Order by a.endDate desc
                    Limit 0, 1
                    )
                left join OrgStructure os
                    on os.id =
                        (Select apos.value
                        From ActionProperty as ap
                            left join ActionProperty_OrgStructure as apos
                                on apos.id = ap.id
                        Where ap.action_id = Action.id
                            and apos.value is not Null
                        Limit 0, 1
                        )
                left join rbHospitalBedProfile hbp
                    on hbp.id =
                        (Select aphbp.value
                        From ActionProperty as ap
                            left join ActionProperty_rbHospitalBedProfile as aphbp
                                on aphbp.id = ap.id
                        Where ap.action_id = Action.id
                            and aphbp.value is not Null
                        Limit 0, 1)
                inner join rbResult as r
                    on r.id = Event.result_id
                %(eventJoin)s
                Where
                %(eventCond)s
                and Exists(
                    Select a.id
                    From Action a
                    inner join ActionType at
                        on at.id = a.actionType_id
                    Where
                        a.event_id = Event.id
                        and at.flatCode = 'leaved'
                        and a.deleted = 0
                )
                and not isNull(Event.execDate)
                and (r.name LIKE 'Выписан%%'
                    or r.name LIKE '%%Умер%%'
                    or r.name LIKE 'Смерть%%'
                    or r.name LIKE 'Переведен%%')
            Group by os.id, hbp.id
        )
        ) as Result
        Group by Result.orgStructureId, Result.bedProfileId
        Order by (CASE WHEN Result.orgStructureId IS NULL then 1 ELSE 0 END),
            Result.orgStructureId,
            (CASE WHEN Result.bedProfileId IS NULL then 1 ELSE 0 END),
            Result.bedProfileId'''
    db = QtGui.qApp.db
    begDate         = params.get('begDate')
    endDate         = params.get('endDate')
    orgStructureId  = params.get('orgStructureId', None)
    typeFinanceId       = params.get('typeFinanceId', None)

    tableOrgStructure = db.table('OrgStructure').alias('os')
    tableOrgStructureHB = db.table('OrgStructure_HospitalBed').alias('oshb')
    tableHospitalBedProfile = db.table('rbHospitalBedProfile').alias('hbp')
    tableAction = db.table('Action').alias('a')
    tableEvent = db.table('Event')
    tableContract = db.table('Contract').alias('c')
    tableFiannce = db.table('rbFinance').alias('f')
    eventCond = []
    orgStructureCond = []
    eventJoin = ''
    movingCond = ''
    movingJoin = ''
    if orgStructureId:
        orgStructureList = getOrgStructureDescendants(orgStructureId)
        eventCond.append(tableOrgStructure['id'].inlist(orgStructureList))
        orgStructureCond.append(tableOrgStructure['id'].inlist(orgStructureList))
    if typeFinanceId > 0:
        eventJoin = u'''
                inner join Contract as cA
                    on Action.contract_id = cA.id
                inner join Contract as cE
                    on Event.contract_id = cE.id'''
        movingJoin = u'''
                inner join Contract as cA
                    on a.contract_id = cA.id
                inner join Contract as cE
                    on e.contract_id = cE.id'''
        movingCond = u'AND if (cA.finance_id, cA.finance_id = %d, cE.finance_id = %d)' %(typeFinanceId, typeFinanceId)
        eventCond.append(u'if (cA.finance_id, cA.finance_id = %d, cE.finance_id = %d)' %(typeFinanceId, typeFinanceId))
    elif typeFinanceId == -1:
        eventJoin = u'''
                left join ClientDocument cd
                    on cd.client_id = cl.id
                left join rbDocumentType dt
                    on dt.id = cd.documentType_id
                left join ClientPolicy cp
                    on cp.id = getClientPolicy(cl.id, 1)'''
        movingJoin = u'''
                left join Client as cl
                    on cl.id = e.client_id\n''' + eventJoin
        eventJoin = u'''
                left join Client as cl
                    on cl.id = Event.client_id\n''' + eventJoin
        movingCond = u'''AND((dt.id is Null) OR (dt.code = '21')) AND (cp.id is Null)'''
        eventCond.append(u'''((dt.id is Null) OR (dt.code = '21')) AND (cp.id is Null)''')
    if not eventJoin:
        eventJoin = ''
    eventCond.append(tableEvent['execDate'].ge(begDate))
    eventCond.append(tableEvent['execDate'].le(endDate))
    eventCond.append(tableEvent['org_id'].eq(QtGui.qApp.currentOrgId()))
    orgStructureCond.append(tableOrgStructure['organisation_id'].eq(QtGui.qApp.currentOrgId()))

    orgStructureCond = db.joinAnd(orgStructureCond)
    eventCond = db.joinAnd(eventCond)

    return db.query(stmt %{'orgStructureCond': orgStructureCond,
                           'eventJoin': eventJoin,
                           'eventCond': eventCond,
                           'movingJoin': movingJoin,
                           'movingCond': movingCond})

def getOrgName(orgID):
    db = QtGui.qApp.db
    table = db.table('Organisation')
    return forceString(db.translate(table,'id',orgID, 'shortName'))

class CReportBedspacePEOForm1(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчёт по использованию коченого фонда. Форма 1. Стационар')

    def getSetupDialog(self, parent):
        result = CReportBedspacePEOForm1Dialog(parent)
        result.setTitle(u'Отчёт по использованию коченого фонда. Форма 1. Стационар')
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
        u'''Наименование отд./Профиль коек - подразделение и профили коек в подразделении
        Всего коек - количество коек в подразделении и по каждому профилю коек
        Пролечено больных - выписано + умерло + переведено
        Проведено койко-дней - ...
        '''
        tableColumns = [
            ('55%', [u'Наименование отд./Профиль коек'], CReportBase.AlignCenter),
            ('15%', [u'Всего коек'], CReportBase.AlignCenter),
            ('15%', [u'Пролечено больных'], CReportBase.AlignCenter),
            ('15%', [u'Проведено койко-дней'], CReportBase.AlignCenter),
            ]
        table = createTable(cursor, tableColumns)
        currentOrgStructureId = -1
        orgStructureRow = -1
        orgStructureName = ''
        totalQuantity = 0
        totalTreated = 0
        totalDays = 0
        tOSQuantity = 0
        tOSTreated = 0
        tOSDays = 0
        while query.next():
            record = query.record()
            row = table.addRow()
            orgStructureId = forceInt(record.value('orgStructureId'))
            if currentOrgStructureId != orgStructureId:
                currentOrgStructureId = orgStructureId
                if orgStructureRow > 0:
                    fields = (
                        {'name': orgStructureName if orgStructureName else u'Не указано', 'align': CReportBase.AlignLeft},
                        {'name': tOSQuantity, 'align': CReportBase.AlignRight},
                        {'name': tOSTreated, 'align': CReportBase.AlignRight},
                        {'name': tOSDays, 'align': CReportBase.AlignRight},
                    )
                    for col, val in enumerate(fields):
                        table.setText(orgStructureRow, col, val['name'], CReportBase.TableTotal, val['align'])
                orgStructureName = forceString(record.value('orgStructureName'))
                orgStructureRow = row
                tOSQuantity = 0
                tOSTreated = 0
                tOSDays = 0
            else:
                bedProfileName = forceString(record.value('bedProfileName'))
                fields = (
                    {'name': bedProfileName if bedProfileName else u'Не указано', 'align': CReportBase.AlignLeft},
                    {'name': forceInt(record.value('quantity')), 'align': CReportBase.AlignRight},
                    {'name': forceInt(record.value('treated')), 'align': CReportBase.AlignRight},
                    {'name': forceInt(record.value('days')), 'align': CReportBase.AlignRight},
                )
                tOSQuantity += forceInt(record.value('quantity'))
                tOSTreated += forceInt(record.value('treated'))
                tOSDays += forceInt(record.value('days'))
                totalQuantity += forceInt(record.value('quantity'))
                totalTreated += forceInt(record.value('treated'))
                totalDays += forceInt(record.value('days'))
                for col, val in enumerate(fields):
                    table.setText(row, col, val['name'], CReportBase.TableBody, val['align'])
        fields = (
            {'name': orgStructureName if orgStructureName else u'Не указано', 'align': CReportBase.AlignLeft},
            {'name': tOSQuantity, 'align': CReportBase.AlignRight},
            {'name': tOSTreated, 'align': CReportBase.AlignRight},
            {'name': tOSDays, 'align': CReportBase.AlignRight},
        )
        if orgStructureRow > 0:
            for col, val in enumerate(fields):
                table.setText(orgStructureRow, col, val['name'], CReportBase.TableTotal, val['align'])
        row = table.addRow()
        fields = (
            {'name': u'Всего:', 'align': CReportBase.AlignRight},
            {'name': totalQuantity, 'align': CReportBase.AlignRight},
            {'name': totalTreated, 'align': CReportBase.AlignRight},
            {'name': totalDays, 'align': CReportBase.AlignRight},
        )
        for col, val in enumerate(fields):
            table.setText(row, col, val['name'], CReportBase.TableTotal, val['align'])
        return doc

class CReportBedspacePEOForm1Dialog(QtGui.QDialog, Ui_ReportBedspacePEOForm1Setup):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbFinance.setTable('rbFinance')
        self.cmbFinance.model().d.addItem(-1,'-1', u'Иностранные граждане')

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