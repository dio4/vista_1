# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui

from library.Utils          import forceString, forceInt, forcePrettyDouble
from library.vm_collections import OrderedDict
from Orgs.Utils             import getOrgStructureDescendants
from Reports.Report         import CReport
from Reports.ReportBase     import createTable, CReportBase
from Reports.ReportOperationsActivity import CReportOperationsActivityDialog


columns = OrderedDict()
columns['ExternalId']       = u'№ истории \n болезни'
columns['ClientId']         = u'№ Амб. карты'
columns['FullName']         = u'ФИО'
columns['DaysBefore']       = u'Кол-во дней до'
columns['DaysAfter']        = u'Кол-во дней после'
columns['ExecPerson']       = u'Лечащий врач'
columns['ExecDate']         = u'Дата выписки'
columns['Result']           = u'Результат'

def selectData(params, group=True):
    begDate = params.get('begDate')
    endDate = params.get('endDate')
    orgStructureIds = (params.get('chkOrgStructure'), params.get('orgStructureId'), params.get('lstOrgStructure'))
    result = params.get('result')
    groupOrgStructure = params.get('chkGroupOrgStructure')

    db = QtGui.qApp.db
    tableEvent = db.table('Event').alias('e')
    tableAction = db.table('Action')
    tableActionType = db.table('ActionType')
    tableOrgStructure = db.table('OrgStructure').alias('os')
    tableResult = db.table('rbResult').alias('r')

    join = u""
    condEvent = [
        tableEvent['execDate'].dateLe(endDate),
        tableEvent['execDate'].dateGe(begDate),
        tableEvent['deleted'].eq(0)]
    condAction = [
        tableAction['deleted'].eq(0),
        tableActionType['deleted'].eq(0),
        tableAction['endDate'].dateLe(endDate),
        tableAction['endDate'].dateGe(begDate),
        tableAction['endDate'].isNotNull(),
        tableAction['endDate'].ne("Date('0000-00-00')")
    ]
    if orgStructureIds[0] and orgStructureIds[2]:
        condEvent.append(tableOrgStructure['id'].inlist(orgStructureIds[2]))
    elif orgStructureIds[1]:
        condEvent.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureIds[1])))
    if result:
        condEvent.append(tableResult['id'].eq(result))
    if groupOrgStructure:
        order = u"Order by os.id, e.execDate"
    else:
        order = u"Order by e.execDate"
    stmt =  u"""
	SELECT os.code AS orgStructureCode,
		ActionType.name AS operationName,
		COUNT(DISTINCT e.client_id) AS cnt_clients,
		COUNT(*) AS cnt_operations,
		COUNT(aps.value) AS cnt_sequalae,
        SUM(TO_DAYS((Select Action.endDate
            From Action
                inner join ActionType
                    on ActionType.id = Action.actionType_id
            where ActionType.serviceType = 4
                and Action.event_id = e.id
                and not isNull(Action.endDate)
                and Action.endDate != Date('0000-00-00')
                and Action.deleted = 0
            Order by Action.endDate, Action.begDate
            Limit 0,1)) - TO_DAYS(e.setDate)) as sum_daysBefore,
        SUM(TO_DAYS(e.execDate) - TO_DAYS((Select Action.endDate
            From Action
                inner join ActionType
                    on ActionType.id = Action.actionType_id
            where ActionType.serviceType = 4
                and Action.event_id = e.id
                and not isNull(Action.endDate)
                and Action.endDate != Date('0000-00-00')
                and Action.deleted = 0
            Order by Action.endDate DESC, Action.begDate DESC
            Limit 0,1)))	as sum_daysAfter,
        Count(IF(r.name LIKE "%%смерт%%" OR r.name LIKE "%%умер%%", 1, NULL)) AS sumDeath
    From Event e
        INNER JOIN Action ON e.id = Action.event_id
        INNER JOIN ActionType ON Action.actionType_id = ActionType.id
        INNER JOIN Action a1 ON a1.event_id = e.id
        INNER JOIN ActionType at1 ON a1.actionType_id = at1.id
        LEFT JOIN (ActionProperty ap INNER JOIN	ActionPropertyType apt
            ON ap.type_id = apt.id AND apt.name IN ("Осложнение", "Осложнения")
            INNER JOIN ActionProperty_String AS aps
            ON aps.id = ap.id AND TRIM(aps.value) NOT IN ("", "нет")
            ) ON Action.id = ap.action_id
        left join rbResult r
            on r.id = e.result_id
        left join vrbPerson p
            on p.id = e.execPerson_id
        left join OrgStructure as os
            on os.id = p.orgStructure_id
    Where
        ActionType.serviceType = 4
        and at1.flatCode = 'leaved' AND at1.deleted = 0	AND a1.`endDate` <> ''
        and %(condAction)s
        and %(condEvent)s
    %(group)s
        """ % {u'condAction': QtGui.qApp.db.joinAnd(condAction),
               u'condEvent': QtGui.qApp.db.joinAnd(condEvent),
               u'group': u'''
    GROUP BY os.code, ActionType.name
    WITH ROLLUP
    ''' if group else u''}
    return db.query(stmt)

class CReportOperationsActivityByActions(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Сроки лечения и исходы при операциях')


    def getSetupDialog(self, parent):
        result = CReportOperationsActivityDialog(parent)
        result.setTitle(self.title())
        result.chkClientDetail.setVisible(False)
        result.groupBox.setVisible(False)
        result.chkGroupOrgStructure.setChecked(True)
        return result

    def build(self, params):
        outputColumns = params.get('outputColumns')
        groupOrgStructure = params.get('chkGroupOrgStructure')
        clientDetail = params.get('clientDetail')
        query = selectData(params) if groupOrgStructure else selectData(params, group=False)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        if groupOrgStructure:
            cursor.insertText(u'Группировка: по отделениям')

        cntOperations = 0
        cntClients = 0
        cntDaysBefore = 0
        cntDaysAfter = 0
        cntTotalDays = 0
        cntSequelae = 0
        cntDead = 0
        avgDaysBefore = 0
        avgDaysAfter = 0
        avgTotalDays = 0
        avgSequelae = 0
        avgDead = 0

        if groupOrgStructure:
            tableColumns = [
                        ('30%', [u'Отделение'], CReportBase.AlignLeft),
                        ('30%', [u'Название операции'], CReportBase.AlignLeft),
                        ('4%', [u'Всего операций'], CReportBase.AlignLeft),
                        ('4%', [u'Всего пациентов'], CReportBase.AlignLeft),
                        ('4%', [u'Дооперац. к/д', u'Всего'], CReportBase.AlignLeft),
                        ('4%', [u'', u'Средн.'], CReportBase.AlignLeft),
                        ('4%', [u'Послеооперац. к/д', u'Всего'], CReportBase.AlignLeft),
                        ('4%', [u'', u'Средн.'], CReportBase.AlignLeft),
                        ('4%', [u'Общий к/д', u'Всего'], CReportBase.AlignLeft),
                        ('4%', [u'', u'Средн'], CReportBase.AlignLeft),
                        ('4%', [u'Осложнения',  u'Всего'], CReportBase.AlignLeft),
                        ('4%', [u'', u'%'], CReportBase.AlignLeft),
                        ('4%', [u'Умерло'], CReportBase.AlignLeft),
                        ('4%', [u'Летальность'], CReportBase.AlignLeft)
                        ]
            table = createTable(cursor, tableColumns)
            for i in (4, 6, 8, 10 ):
                table.mergeCells(0, i, 1, 2)
            for i in (0, 1, 2, 3, 12, 13):
                table.mergeCells(0, i, 2, 1)
        rowSameOrgStructStart = 2
        rowSameOrgStructEnd = 2
        formatSummary = QtGui.QTextCharFormat()
        formatSummary.setFontWeight(QtGui.QFont.Bold)
        alreadyPrintedOrgStructure = False
        while query.next():
            record = query.record()
            cntOperations = forceInt(record.value('cnt_operations'))
            cntClients = forceInt(record.value('cnt_clients'))
            cntDaysBefore = forceInt(record.value('sum_daysBefore'))
            cntDaysAfter = forceInt(record.value('sum_daysAfter'))
            cntTotalDays = cntDaysBefore + cntDaysAfter
            cntSequelae = forceInt(record.value('cnt_sequelae'))
            cntDead = forceInt(record.value('sumDeath'))
            avgDaysBefore = forcePrettyDouble(cntDaysBefore * 1.0 / cntClients)
            avgDaysAfter = forcePrettyDouble(cntDaysAfter * 1.0 / cntClients)
            avgTotalDays = forcePrettyDouble(cntTotalDays * 1.0 / cntClients)
            avgSequelae = forcePrettyDouble(cntSequelae * 1.0 / cntClients)
            avgDead = forcePrettyDouble(cntDead * 1.0 / cntClients, 3)
            orgStructureCode = forceString(record.value('orgStructureCode'))
            if groupOrgStructure:
                row = table.addRow()
                operationName = forceString(record.value('operationName'))
                fields = ("",
                    operationName,
                    cntOperations,
                    cntClients,
                    cntDaysBefore,
                    avgDaysBefore,
                    cntDaysAfter,
                    avgDaysAfter,
                    cntTotalDays,
                    avgTotalDays,
                    cntSequelae,
                    avgSequelae,
                    cntDead,
                    avgDead
                )
                rowSameOrgStructEnd += 1
                if operationName:
                    for col, val in enumerate(fields):
                        table.setText(row, col, val)
                    alreadyPrintedOrgStructure = True
                else:
                    table.mergeCells(rowSameOrgStructStart, 0, rowSameOrgStructEnd - rowSameOrgStructStart, 1 )
                    rowSameOrgStructStart = rowSameOrgStructEnd
                    alreadyPrintedOrgStructure = False
                    for col, val in enumerate(fields):
                        table.setText(row, col, val, formatSummary)
                if not (orgStructureCode or operationName):
                    table.setText(row, 0, '')
                    table.setText(row, 1, u'Итого:', formatSummary, CReportBase.AlignRight)
                else:
                    table.setText(row, 0, orgStructureCode if not alreadyPrintedOrgStructure else '')
                    if not operationName:
                        table.setText(row, 1, u'Итого по отделению:', formatSummary, CReportBase.AlignRight)

        if not groupOrgStructure:
            formText = u"".join([
                    u"Всего операций: %d\n" % cntOperations,
                    u"Всего пациентов: %d\n" % cntClients,
                    u"Всего дней до операции: %d\n" % cntDaysBefore,
                    u"Среднее количество дней до операции: %s\n" % avgDaysBefore,
                    u"Всего дней после операции: %d\n" % cntDaysAfter,
                    u"Среднее количество дней после операции: %s\n" % avgDaysAfter,
                    u"Всего осложнений: %d\n" % cntSequelae,
                    u"Среднее количество осложнений: %s\n" % avgSequelae,
                    u"Всего смертей: %d\n" % cntDead,
                    u"Смертей в среднем на пациента: %s\n" % avgDead])
            cursor.movePosition(QtGui.QTextCursor.PreviousBlock)
            cursor.insertText(formText)
        return doc
