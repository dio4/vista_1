# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from library.Utils import forceInt, forceString
from Orgs.Utils import getOrgStructureDescendants
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Ui_ReportBedspacePEOForm3Setup import Ui_ReportBedspacePEOForm3Setup

def selectData(params):
    stmt = u'''
        Select
            osQuantity.sum as quantity,
            Count(Event.id) as treated,
            os.id as orgStructureId,
            os.name as orgStructureName,
            sum(datediff(Reanimation.endDate, Reanimation.begDate)) as days
        From Event
			inner join
				(Select a.*
				From Event e
					inner join Action a
						on a.event_id = e.id
					inner join ActionType at
						on at.id = a.actionType_id
				Where  a.deleted = 0
					and at.deleted = 0
					and a.endDate is not null
					and at.code in ('261344', '431010', '431020', '431020', '431030', '431040', '431050', '431060')
				) as Reanimation
				on Reanimation.event_id = Event.id
			inner join Person
				on Person.id = Reanimation.person_id
            left join OrgStructure os
                    on os.id = Person.orgStructure_id
            left join (
                Select Count(hbp.id) as sum, OrgStructure.id
                From OrgStructure
                    left join OrgStructure_HospitalBed oshb
                        on oshb.master_id = OrgStructure.id
                    inner join rbHospitalBedProfile hbp
                        on hbp.id = oshb.profile_id
                Group by OrgStructure.id) as osQuantity
                on osQuantity.id = os.id
            inner join rbResult as r
                on r.id = Event.result_id
            %(eventJoin)s
        Where
            %(eventCond)s
            and not isNull(Event.execDate)
            and (r.name LIKE 'Выписан%%'
                or r.name LIKE '%%Умер%%'
                or r.name LIKE 'Смерть%%'
                or r.name LIKE 'Переведен%%')
        Group by os.id'''
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
    eventJoin = ''
    movingCond = ''
    movingJoin = ''
    if orgStructureId:
        orgStructureList = getOrgStructureDescendants(orgStructureId)
        eventCond.append(tableOrgStructure['id'].inlist(orgStructureList))
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
    eventCond = db.joinAnd(eventCond)
    stmt = stmt %{
               'eventJoin': eventJoin,
               'eventCond': eventCond}
    return db.query(stmt)

def selectDataAnstezia(params):
    stmt = u'''
        Select
            Count(Actions.id) as quantity,
            Count(distinct Event.id) as treated,
            os.id as orgStructureId,
            os.name as orgStructureName
        From Event
			inner join
					(Select a.*
					From Action a
					inner join ActionType at
						on at.id = a.actionType_id
					Where (
							at.flatCode RegExp '^нК'
							)
						and a.deleted = 0
						and at.deleted = 0
					Order by a.endDate desc
					) Actions
				on Actions.event_id = Event.id
            inner join Person
                on Person.id = Actions.person_id
            left join OrgStructure os
                on os.id = Person.orgStructure_id
            left join (
                Select Count(hbp.id) as sum, OrgStructure.id
                From OrgStructure
                    left join OrgStructure_HospitalBed oshb
                        on oshb.master_id = OrgStructure.id
                    inner join rbHospitalBedProfile hbp
                        on hbp.id = oshb.profile_id
                Group by OrgStructure.id) as osQuantity
                on osQuantity.id = os.id

            inner join rbResult as r
                on r.id = Event.result_id
            %(eventJoin)s
        Where
            %(eventCond)s
            and not isNull(Event.execDate)
            and (r.name LIKE 'Выписан%%'
                or r.name LIKE '%%Умер%%'
                or r.name LIKE 'Смерть%%'
                or r.name LIKE 'Переведен%%')
        Group by os.id'''
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
    eventJoin = ''
    movingCond = ''
    movingJoin = ''
    if orgStructureId:
        orgStructureList = getOrgStructureDescendants(orgStructureId)
        eventCond.append(tableOrgStructure['id'].inlist(orgStructureList))
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
    eventCond = db.joinAnd(eventCond)
    stmt = stmt %{
               'eventJoin': eventJoin,
               'eventCond': eventCond}
    return db.query(stmt)

def getOrgName(orgID):
    db = QtGui.qApp.db
    table = db.table('Organisation')
    return forceString(db.translate(table,'id',orgID, 'shortName'))

class CReportBedspacePEOForm3(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчёт по использованию коченого фонда. Форма 3. Стационар-Реанимация')

    def getSetupDialog(self, parent):
        result = CReportBedspacePEOForm3Dialog(parent)
        result.setTitle(u'Отчёт по использованию коченого фонда. Форма 3. Стационар-Реанимация')
        return result

    def build(self, params):
        query = selectData(params)
        queryA = selectDataAnstezia(params)
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
            ('55%', [u'Наименование отделения'], CReportBase.AlignCenter),
            ('15%', [u'Койки'], CReportBase.AlignCenter),
            ('15%', [u'Пролечено больных'], CReportBase.AlignCenter),
            ('15%', [u'Проведено койко-дней'], CReportBase.AlignCenter),
            ]
        table = createTable(cursor, tableColumns)
        while query.next():
            record = query.record()
            row = table.addRow()
            orgStructureName = forceString(record.value('orgStructureName'))
            fields = (
                        {'name': orgStructureName if orgStructureName else u'Не указано', 'align': CReportBase.AlignLeft},
                        {'name': forceInt(record.value('quantity')), 'align': CReportBase.AlignRight},
                        {'name': forceInt(record.value('treated')), 'align': CReportBase.AlignRight},
                        {'name': forceInt(record.value('days')), 'align': CReportBase.AlignRight},
                    )
            for col, val in enumerate(fields):
                table.setText(row, col, val['name'], CReportBase.TableBody, val['align'])
        while queryA.next():
            record = queryA.record()
            row = table.addRow()
            orgStructureName = forceString(record.value('orgStructureName'))
            fields = (
                        {'name': orgStructureName if orgStructureName else u'Не указано', 'align': CReportBase.AlignLeft},
                        {'name': forceInt(record.value('quantity')), 'align': CReportBase.AlignRight},
                        {'name': forceInt(record.value('treated')), 'align': CReportBase.AlignRight},
                        {'name': 0, 'align': CReportBase.AlignRight},
                    )
            for col, val in enumerate(fields):
                table.setText(row, col, val['name'], CReportBase.TableTotal, val['align'])
        return doc

class CReportBedspacePEOForm3Dialog(QtGui.QDialog, Ui_ReportBedspacePEOForm3Setup):
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