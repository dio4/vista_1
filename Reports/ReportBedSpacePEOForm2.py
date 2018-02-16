# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from library.Utils import forceInt, forceString
from Orgs.Utils import getOrgStructureDescendants
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Ui_ReportBedspacePEOForm2Setup import Ui_ReportBedspacePEOForm2Setup

def selectData(params):
    stmt = u'''
        Select
            Result.orgStructureId,
            Result.orgStructureName,
            Result.bedProfileName,
            Sum(Result.events)as events,
            Sum(Result.operations) as operations
        From
        (
        (
            Select
                Count(Event.id) as events,
                0 as operations,
                os.id as orgStructureId,
                os.name as orgStructureName,
                hbp.id as bedProfileId,
                hbp.name as bedProfileName
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
                        and at.serviceType = '4'
                    Order by a.endDate desc
                    Limit 0,1
                    )
                inner join Action moving
                    on moving.id =
                    (Select a.id
                    From Action a
                        inner join ActionType at
                            on at.id = a.actionType_id
                    Where a.deleted = 0
                        and at.deleted = 0
                        and a.endDate is not null
                        and a.event_id = Event.id
                        and at.flatCode = 'moving'
                    Order by a.endDate > Action.endDate, a.endDate desc
                    Limit 0, 1 )
                left join OrgStructure os
                    on os.id =
                        (Select apos.value
                        From ActionProperty as ap
                            left join ActionProperty_OrgStructure as apos
                                on apos.id = ap.id
                        Where ap.action_id = moving.id
                            and apos.value is not Null
                        Limit 0, 1
                        )
                left join rbHospitalBedProfile hbp
                    on hbp.id =
                        (Select aphbp.value
                        From ActionProperty as ap
                            left join ActionProperty_rbHospitalBedProfile as aphbp
                                on aphbp.id = ap.id
                        Where ap.action_id = moving.id
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
        Union
        (
            Select
                0 as events,
                Count(Operations.id) as operations,
                os.id as orgStructureId,
                os.name as orgStructureName,
                hbp.id as bedProfileId,
                hbp.name as bedProfileName
            From Event
                inner join
                    (Select a.event_id, a.id, a.endDate
                    From Action a
                        inner join ActionType at
                            on at.id = a.actionType_id
                    Where  a.deleted = 0
                        and at.deleted = 0
                        and a.endDate is not null
                        and at.serviceType = '4'
                    ) as Operations
                    on Operations.event_id = Event.id
                left join Action moving
                    on moving.id =
                    (Select a.id
                    From Action a
                        inner join ActionType at
                            on at.id = a.actionType_id
                    Where a.deleted = 0
                        and at.deleted = 0
                        and a.endDate is not null
                        and a.event_id = Event.id
                        and at.flatCode = 'moving'
                    Order by a.endDate > Operations.endDate, a.endDate desc
                    Limit 0, 1 )
                left join OrgStructure os
                    on os.id =
                        (Select apos.value
                        From ActionProperty as ap
                            left join ActionProperty_OrgStructure as apos
                                on apos.id = ap.id
                        Where ap.action_id = moving.id
                            and apos.value is not Null
                        Limit 0, 1
                        )
                left join rbHospitalBedProfile hbp
                    on hbp.id =
                        (Select aphbp.value
                        From ActionProperty as ap
                            left join ActionProperty_rbHospitalBedProfile as aphbp
                                on aphbp.id = ap.id
                        Where ap.action_id = moving.id
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
                inner join Contract as cE
                    on Event.contract_id = cE.id'''
        eventCond.append(u'cE.finance_id = %d' %typeFinanceId)
    elif typeFinanceId == -1:
        eventJoin = u'''
                left join ClientDocument cd
                    on cd.client_id = cl.id
                left join rbDocumentType dt
                    on dt.id = cd.documentType_id
                left join ClientPolicy cp
                    on cp.id = getClientPolicy(cl.id, 1)'''
        eventJoin = u'''
                left join Client as cl
                    on cl.id = Event.client_id\n''' + eventJoin
        eventCond.append(u'''((dt.id is Null) OR (dt.code = '21')) AND (cp.id is Null)''')
    if not eventJoin:
        eventJoin = ''
    eventCond.append(tableEvent['execDate'].ge(begDate))
    eventCond.append(tableEvent['execDate'].le(endDate))
    eventCond.append(tableEvent['org_id'].eq(QtGui.qApp.currentOrgId()))
    orgStructureCond.append(tableOrgStructure['organisation_id'].eq(QtGui.qApp.currentOrgId()))

    orgStructureCond = db.joinAnd(orgStructureCond)
    eventCond = db.joinAnd(eventCond)
    stmt = stmt %{'orgStructureCond': orgStructureCond,
                           'eventJoin': eventJoin,
                           'eventCond': eventCond,}
    return db.query(stmt)

def getOrgName(orgID):
    db = QtGui.qApp.db
    table = db.table('Organisation')
    return forceString(db.translate(table,'id',orgID, 'shortName'))

class CReportBedspacePEOForm2(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчёт по использованию коченого фонда. Форма 2. Стационар-Операции')

    def getSetupDialog(self, parent):
        result = CReportBedspacePEOForm2Dialog(parent)
        result.setTitle(u'Отчёт по использованию коченого фонда. Форма 2. Стационар-Операции')
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
            ('60%', [u'Наименование отд./Профиль коек'], CReportBase.AlignCenter),
            ('20%', [u'Проведено операций'], CReportBase.AlignCenter),
            ('20%', [u'Прооперировано больных'], CReportBase.AlignCenter),
            ]
        table = createTable(cursor, tableColumns)
        currentOrgStructureId = -1
        orgStructureName = ''
        tOSOperations = 0
        tOSEvents = 0
        orgStructureRow = -1
        totalOperations = 0
        totalEvents = 0
        while query.next():
            record = query.record()
            row = table.addRow()
            orgStructureId = forceInt(record.value('orgStructureId'))
            if currentOrgStructureId != orgStructureId:
                currentOrgStructureId = orgStructureId
                if orgStructureRow > 0:
                    fields = (
                        {'name': orgStructureName if orgStructureName else u'Не указано', 'align': CReportBase.AlignLeft},
                        {'name': tOSOperations, 'align': CReportBase.AlignRight},
                        {'name': tOSEvents, 'align': CReportBase.AlignRight},
                    )
                    for col, val in enumerate(fields):
                        table.setText(orgStructureRow, col, val['name'], CReportBase.TableTotal, val['align'])
                orgStructureName = forceString(record.value('orgStructureName'))
                orgStructureRow = row
                tOSOperations = 0
                tOSEvents = 0
            else:
                bedProfileName = forceString(record.value('bedProfileName'))
                fields = (
                    {'name': bedProfileName if bedProfileName else u'Не указано', 'align': CReportBase.AlignLeft},
                    {'name': forceInt(record.value('operations')), 'align': CReportBase.AlignRight},
                    {'name': forceInt(record.value('events')), 'align': CReportBase.AlignRight},
                )
                tOSOperations += forceInt(record.value('operations'))
                tOSEvents += forceInt(record.value('events'))
                totalOperations += forceInt(record.value('operations'))
                totalEvents += forceInt(record.value('events'))
                for col, val in enumerate(fields):
                    table.setText(row, col, val['name'], CReportBase.TableBody, val['align'])
        fields = (
            {'name': orgStructureName if orgStructureName else u'Не указано', 'align': CReportBase.AlignLeft},
            {'name': tOSOperations, 'align': CReportBase.AlignRight},
            {'name': tOSEvents, 'align': CReportBase.AlignRight},
        )
        if orgStructureRow > 0:
            for col, val in enumerate(fields):
                table.setText(orgStructureRow, col, val['name'], CReportBase.TableTotal, val['align'])
        row = table.addRow()
        fields = (
            {'name': u'Всего:', 'align': CReportBase.AlignRight},
            {'name': totalOperations, 'align': CReportBase.AlignRight},
            {'name': totalEvents, 'align': CReportBase.AlignRight},
        )
        for col, val in enumerate(fields):
            table.setText(row, col, val['name'], CReportBase.TableTotal, val['align'])
        return doc

class CReportBedspacePEOForm2Dialog(QtGui.QDialog, Ui_ReportBedspacePEOForm2Setup):
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