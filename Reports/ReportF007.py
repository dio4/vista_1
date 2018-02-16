# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils                      import forceBool, forceInt, forceString, forceRef

from Orgs.Utils                         import getOrgStructureDescendants
from Reports.Report                     import CReport
from Reports.ReportBase                 import createTable, CReportBase
from Reports.ReportView                 import CPageFormat

from Ui_ReportF007 import Ui_ReportF007


def selectData(params):
    db = QtGui.qApp.db
    begDate        = params.get('begDate')
    endDate        = params.get('endDate')
    begTime        = params.get('begTime')
    begDate = QtCore.QDateTime(begDate, begTime)
    endDate = endDate.addDays(1)
    endDate = QtCore.QDateTime(endDate, begTime)
    orgStructureId = params.get('orgStructureId')
    orgStructureOAR = params.get('orgStructureOAR')
    reportType = params.get('type')
    upgroupFinance = params.get('ungroupFinance')
    typeSubQuery = {'moving'         : ('moving',      u'Отделение пребывания'),
                    'received'       : ('received',    u'Направлен в отделение'),
                    'movingInto'     : ('moving',      u'Переведен в отделение'),
                    'movingFrom'     : ('moving',      u'Переведен из отделения'),
                    'leaved'         : ('leaved',      u'Отделение'),
                    'reanimation'    : ('reanimation', u'Отделение пребывания'),
                    'reanimationInto': ('reanimation', u'Переведен в отделение'),
                    'reanimationFrom': ('reanimation', u'Переведен из отделения')}
    def subQuery(typeQuery):
        infoTypeQuery = typeSubQuery[typeQuery]
        tableActionType = db.table('ActionType')
        tableAction = db.table('Action')
        tableActionPropertyType = db.table('ActionPropertyType')
        tableActionProperty = db.table('ActionProperty')
        tableAPOrgStructure = db.table('ActionProperty_OrgStructure')
        tableEvent = db.table('Event')
        tableClient = db.table('Client')
        tableFinance = db.table('rbFinance')
        tableClientAddress = db.table('ClientAddress')
        tableAddress = db.table('Address')
        tableAddressHouse = db.table('AddressHouse')
        tableOrgStructure = db.table('OrgStructure')

        cond = [tableActionType['flatCode'].eq(infoTypeQuery[0])]
        if orgStructureId:
            cond.append(tableAPOrgStructure['value'].inlist(getOrgStructureDescendants(orgStructureId)))
        select = [tableFinance['id'] if orgStructureId and not upgroupFinance else tableAPOrgStructure['value'].alias('id')]

        if reportType == 2:
            select.append('COUNT(IF(Client.sex = 1, Client.id, NULL)) AS men, COUNT(IF(Client.sex = 2, Client.id, NULL)) AS women')

        select.extend(['COUNT(%s) %s' % (tableActionProperty['id'], typeQuery),
                          '''GROUP_CONCAT(Event.id) AS events'''])

        group = [tableFinance['id'] if orgStructureId and not upgroupFinance else tableAPOrgStructure['value']]

        queryTable = tableActionType.innerJoin(tableAction, [tableAction['actionType_id'].eq(tableActionType['id']),
                                                             tableAction['deleted'].eq(0)])
        queryTable = queryTable.innerJoin(tableEvent, [tableEvent['id'].eq(tableAction['event_id']),
                                                           tableEvent['deleted'].eq(0)])
        queryTable = queryTable.innerJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))
        queryTable = queryTable.leftJoin(tableClientAddress, [tableClientAddress['client_id'].eq(tableClient['id']),
                                                              'ClientAddress.id = getClientRegAddressId(Client.id)',
                                                              tableClientAddress['deleted'].eq(0)])
        queryTable = queryTable.leftJoin(tableAddress, [tableAddress['id'].eq(tableClientAddress['address_id']),
                                                        tableAddress['deleted'].eq(0)])
        queryTable = queryTable.leftJoin(tableAddressHouse, [tableAddressHouse['id'].eq(tableAddress['house_id']),
                                                             tableAddressHouse['deleted'].eq(0)])
        queryTable = queryTable.innerJoin(tableFinance, tableFinance['id'].eq(tableAction['finance_id']))
        queryTable = queryTable.innerJoin(tableActionPropertyType, [tableActionPropertyType['actionType_id'].eq(tableActionType['id']),
                                                                    tableActionPropertyType['name'].eq(infoTypeQuery[1]),
                                                                    tableActionPropertyType['deleted'].eq(0)])
        queryTable = queryTable.innerJoin(tableActionProperty, [tableActionProperty['action_id'].eq(tableAction['id']),
                                                                tableActionProperty['type_id'].eq(tableActionPropertyType['id']),
                                                                tableActionProperty['deleted'].eq(0)])
        queryTable = queryTable.innerJoin(tableAPOrgStructure, tableAPOrgStructure['id'].eq(tableActionProperty['id']))
        queryTable = queryTable.innerJoin(tableOrgStructure, tableOrgStructure['id'].eq(tableAPOrgStructure['value']))

        if typeQuery in ('received', 'leaved', 'moving', 'movingInto'):
            tableActionDuration = db.table('Action').alias('ActionDuration')
            additionalSelect = {'endDate': u"IF(%(aD)s < %(pD)s, %(aD)s, %(pD)s)" %({u'aD': tableAction['endDate'], u'pD': 'DATE(\'%s\')' % endDate.toString(QtCore.Qt.ISODate)})
                                    if typeQuery == 'leaved' else 'DATE(\'%s\')' % endDate.toString(QtCore.Qt.ISODate),
                                'begDate': tableAction['begDate'] if typeQuery == 'received' else 'DATE(\'%s\')' % begDate.toString(QtCore.Qt.ISODate) if typeQuery in ('moving', 'movingInto') else
                                    u"IF (%(aD)s > %(pD)s, %(aD)s, %(pD)s)" %({u'aD': tableActionDuration['begDate'], u'pD': 'DATE(\'%s\')' % begDate.toString(QtCore.Qt.ISODate)})}
            if typeQuery in ('received', 'movingInto'):
                select.extend(['sum(IF(ActionDuration.id, IF(OrgStructure.hasDayStationary = 1, datediff(%(endDate)s, %(begDate)s), datediff(%(endDate)s, %(begDate)s)), 0)) AS eventDays' % additionalSelect,
                               'sum(IF(ActionDuration.id, IF(((Client.sex = 2 AND age(Client.birthDate, Action.begDate) >= 55) OR (Client.sex = 1 AND age(Client.birthDate, Action.begDate) >= 60)), IF(OrgStructure.hasDayStationary = 1, datediff(%(endDate)s, %(begDate)s), datediff(%(endDate)s, %(begDate)s)), 0), 0)) AS eventDaysOld' % additionalSelect])
            elif typeQuery in ('moving'):
                select.extend(['sum(IF(ActionDuration.id, IF(OrgStructure.hasDayStationary = 1, datediff(%(endDate)s, %(begDate)s), datediff(%(endDate)s, %(begDate)s)), 0)) AS eventDays' % additionalSelect,
                               'sum(IF(ActionDuration.id, IF(((Client.sex = 2 AND age(Client.birthDate, Action.begDate) >= 55) OR (Client.sex = 1 AND age(Client.birthDate, Action.begDate) >= 60)), IF(OrgStructure.hasDayStationary = 1, datediff(%(endDate)s, %(begDate)s), datediff(%(endDate)s, %(begDate)s)), 0), 0)) AS eventDaysOld' % additionalSelect])
            elif typeQuery in ('leaved'):
                select.extend(['sum(IF(ActionDuration.id, IF(OrgStructure.hasDayStationary = 1, datediff(%(endDate)s, %(begDate)s) + 1, datediff(%(endDate)s, %(begDate)s)), 0)) AS eventDays' % additionalSelect,
                               'sum(IF(ActionDuration.id, IF(((Client.sex = 2 AND age(Client.birthDate, Action.begDate) >= 55) OR (Client.sex = 1 AND age(Client.birthDate, Action.begDate) >= 60)), IF(OrgStructure.hasDayStationary = 1, datediff(%(endDate)s, %(begDate)s) + 1, datediff(%(endDate)s, %(begDate)s)), 0), 0)) AS eventDaysOld' % additionalSelect])

            tableActDuration    = db.table('Action').alias('ActDuration')
            condActionType = ['ActDuration.actionType_id = (SELECT at.id FROM ActionType at WHERE at.flatCode = \'%s\' AND at.deleted = 0) ' % ('leaved' if typeQuery in ('received', 'moving') else 'moving' if typeQuery == 'movingInto' else 'received')]
            if typeQuery in ('received', 'moving', 'movingInto'):
                condActionType.append('''Not Exists(Select ActionTemp.id From Action as ActionTemp
                                         Where ActionTemp.actionType_id = (SELECT at.id FROM ActionType at WHERE at.flatCode = \'leaved\' AND at.deleted = 0)
                                         AND (ActionTemp.deleted = 0)
                                         AND ActionTemp.event_id = ActDuration.event_id)''')
            condDurationAction = [tableActDuration['event_id'].eq(tableEvent['id']),
                                  db.joinOr(condActionType),
                                  tableActDuration['deleted'].eq(0)]
            if typeQuery in ('moving'):
                condDurationAction.append(u'''(Not Exists(
			                            Select ActionTemp.id From Action as ActionTemp
			                                INNER JOIN ActionPropertyType as aptTemp
			                                    ON (aptTemp.`actionType_id` = ActionTemp.`actionType_id`)
			                                    AND (aptTemp.`name` = 'Переведен из отделения')
			                                    AND (aptTemp.`deleted` = 0)
			                                INNER JOIN ActionProperty as apTemp
			                                    ON apTemp.action_id = ActionTemp.id
			                                INNER JOIN ActionProperty_OrgStructure as aposTemp
			                                    ON aposTemp.id = apTemp.id
			                            Where ActionTemp.actionType_id = (SELECT at.id FROM ActionType at WHERE at.flatCode = 'moving' AND at.deleted = 0)
			                            AND aposTemp.value != OrgStructure.id
			                            AND ActionTemp.event_id = ActDuration.event_id
                                        AND (TIMESTAMP(ActionTemp.`begDate`) >= %s)
				                        AND (TIMESTAMP(ActionTemp.`begDate`) < %s) ))''' %('TIMESTAMP(\'%s\')' % begDate.toString(QtCore.Qt.ISODate), 'TIMESTAMP(\'%s\')' % endDate.toString(QtCore.Qt.ISODate)))

            if typeQuery in ('received', 'moving', 'movingInto'):
                condDurationAction.insert(1, db.joinOr([tableActDuration['endDate'].dateGe(endDate), tableActDuration['endDate'].isNull()]))
            queryTable = queryTable.leftJoin(tableActionDuration, [u'%s = (%s)'%(tableActionDuration['id'], db.selectStmt(tableActDuration, tableActDuration['id'], condDurationAction, limit=1))])

        if typeQuery == 'received':
            tableActionPropertyTypeHosp = db.table('ActionPropertyType').alias('ActionPropertyTypeHosp')
            tableActionPropertyHosp = db.table('ActionProperty').alias('ActionPropertyHosp')
            tableAPStringHosp = db.table('ActionProperty_String').alias('ActionPropertyStringHosp')
            queryTable = queryTable.leftJoin(tableActionPropertyTypeHosp, [tableActionPropertyTypeHosp['actionType_id'].eq(tableActionType['id']),
                                                                            tableActionPropertyTypeHosp['name'].eq(u'Госпитализирован'),
                                                                            tableActionPropertyTypeHosp['deleted'].eq(0)])
            queryTable = queryTable.leftJoin(tableActionPropertyHosp, [tableActionPropertyHosp['action_id'].eq(tableAction['id']),
                                                                         tableActionPropertyHosp['type_id'].eq(tableActionPropertyTypeHosp['id']),
                                                                         tableActionPropertyHosp['deleted'].eq(0)])
            queryTable = queryTable.leftJoin(tableAPStringHosp, tableAPStringHosp['id'].eq(tableActionPropertyHosp['id']))
            select.append(u'''COUNT(if(ClientAddress.isVillager = 1 OR isClientVillager(Client.id) = 1, ActionProperty.id, NULL)) AS receivedVillager
                            , COUNT(if(age(Client.birthDate, Action.begDate) <= 17, ActionProperty.id, NULL)) AS receivedChildren
                            , COUNT(if(age(Client.birthDate, Action.begDate) < 17, ActionProperty.id, NULL)) AS receivedBefore17
                            , COUNT(if(LEFT(AddressHouse.KLADRCode,2) != 78, ActionProperty.id, NULL)) AS receivedOther
                            , COUNT(if(ActionPropertyStringHosp.value LIKE '%экстренно', ActionPropertyHosp.id, NULL)) AS receivedExtra
                            , COUNT(if(ActionPropertyStringHosp.value LIKE '%планово', ActionPropertyHosp.id, NULL)) AS receivedPlan''')
            select.append('COUNT(if(%s, ActionProperty.id, NULL)) AS receivedOld' % ('(age(Client.birthDate, Action.begDate) >= 60)' if reportType == 2 else '(Client.sex = 2 AND age(Client.birthDate, Action.begDate) >= 55) OR (Client.sex = 1 AND age(Client.birthDate, Action.begDate) >= 60)'))
            cond.extend([tableAction['begDate'].datetimeGe(begDate), tableAction['begDate'].datetimeLt(endDate)])
        elif typeQuery in ('moving', 'reanimation', 'movingInto'):
            if typeQuery in ('moving', 'movingInto'):
                cond.append('''NOT EXISTS(SELECT a.event_id
                                          FROM Action a
                                          INNER JOIN ActionType at ON at.id = a.actionType_id AND at.flatCode = 'reanimation' AND at.deleted = 0
                                          INNER JOIN ActionProperty ap ON ap.action_id = a.id AND ap.deleted = 0
                                          WHERE a.event_id = Action.event_id
                                          GROUP BY a.event_id)''')
            cond.extend([tableAction['begDate'].datetimeLt(begDate),
                         db.joinOr([tableAction['endDate'].datetimeGe(begDate), tableAction['endDate'].isNull()])])
        elif typeQuery in ('reanimationInto'):
            cond.extend([tableAction['endDate'].datetimeGe(begDate), tableAction['endDate'].datetimeLt(endDate)])
        elif typeQuery in ('movingFrom', 'reanimationFrom'):
            cond.extend([tableAction['begDate'].datetimeGe(begDate), tableAction['begDate'].datetimeLt(endDate)])
        else:
            tableActionPropertyTypeResult = db.table('ActionPropertyType').alias('ActionPropertyTypeResult')
            tableActionPropertyResult = db.table('ActionProperty').alias('ActionPropertyResult')
            tableAPString = db.table('ActionProperty_String')
            if orgStructureId:
                select.append(u'''IF(ActionProperty_String.value = 'умер', CONCAT(Client.lastName, ' ', Client.firstName, ' ', Client.patrName), NULL) AS deathClients''' )
                select.append(u'''IF(ActionProperty_String.value = 'переведен в другой стационар', CONCAT(Client.lastName, ' ', Client.firstName, ' ', Client.patrName), NULL) AS otherClients''' )

            select.append(u'''COUNT(IF(ActionProperty_String.value = 'умер', ActionProperty_String.id, NULL)) AS leavedDeath,
                              COUNT(IF(ActionProperty_String.value = 'умер' AND age(Client.birthDate, Action.begDate) < 17, ActionProperty_String.id, NULL)) AS leavedDeathChildren
                                , COUNT(IF(ActionProperty_String.value = 'переведен в другой стационар', ActionProperty_String.id, NULL)) AS leavedOther
                                , COUNT(IF(ActionProperty_String.value = 'выписан в дневной стационар', ActionProperty_String.id, NULL)) AS leavedSt
                                , COUNT(IF(ActionProperty_String.value = 'выписан в круглосуточный стационар', ActionProperty.id, NULL)) AS leavedDCSt''')
            if reportType == 0:
                oldCond = '((Client.sex = 2 AND age(Client.birthDate, Action.begDate) >= 55) OR (Client.sex = 1 AND age(Client.birthDate, Action.begDate) >= 60))'
                select.append(u'''COUNT(if(%(oldCond)s, ActionProperty.id, NULL)) AS leavedOld,
                                  COUNT(if(ActionProperty_String.value = 'умер' and %(oldCond)s, ActionProperty_String.id, NULL)) AS leavedDeathOld''' % {'oldCond': oldCond})
            queryTable = queryTable.leftJoin(tableActionPropertyTypeResult, [tableActionPropertyTypeResult['actionType_id'].eq(tableActionType['id']),
                                                                             tableActionPropertyTypeResult['name'].eq(u'Исход госпитализации'),
                                                                             tableActionPropertyTypeResult['deleted'].eq(0)])
            queryTable = queryTable.leftJoin(tableActionPropertyResult, [tableActionPropertyResult['action_id'].eq(tableAction['id']),
                                                                         tableActionPropertyResult['type_id'].eq(tableActionPropertyTypeResult['id']),
                                                                         tableActionPropertyResult['deleted'].eq(0)])
            queryTable = queryTable.leftJoin(tableAPString, tableAPString['id'].eq(tableActionPropertyResult['id']))
            cond.extend([tableAction['endDate'].datetimeGe(begDate), tableAction['endDate'].datetimeLt(endDate)])
        return db.selectStmt(queryTable, select, cond, group)

    if upgroupFinance or not orgStructureId:
        stmtFrom = u'''(SELECT os.id
                                      , os.code
                                      , COUNT(IF(oshb.isPermanent = 1, os.id, NULL)) AS permanent
                                      , COUNT(IF(oshb.involution = 1, os.id, NULL)) AS involution,
                                      if(os.code = 'ОАР', 1, 0) AS reanimation
                                      , COUNT(IF(oshb.sex = 1, oshb.id, NULL)) AS menBed
                                      , COUNT(IF(oshb.sex = 2, oshb.id, NULL)) AS womenBed
                                 FROM OrgStructure_HospitalBed oshb, OrgStructure os
                                 WHERE oshb.master_id = os.id %s
                                 GROUP BY os.id
                                 ORDER BY reanimation, os.code)  AS mainTable''' % ('AND ' + db.table('OrgStructure').alias('os')['id'].inlist(getOrgStructureDescendants(orgStructureId)) if orgStructureId else u'''AND os.code != 'ОАР' ''' if not orgStructureOAR else '')
        select = 'mainTable.code, mainTable.permanent, mainTable.involution'
        if reportType == 0:
            select += ', received.receivedBefore17, leaved.leavedOld, leaved.leavedDeathOld, leaved.leavedDeathChildren'
        if reportType == 3:
            select += ', received.receivedPlan'
        if reportType in (0, 3):
            select += ', received.receivedExtra'
        if reportType == 2:
            select += ''', mainTable.menBed,
                           mainTable.womenBed,
                           (received.men + moving.men + movingInto.men - movingFrom.men - leaved.men) AS men,
                           (received.women + moving.women + movingInto.women - movingFrom.women - leaved.women) AS women'''
        if orgStructureOAR or reportType == 3:
            select += u''', IF(mainTable.code = 'ОАР', @sumReanimationFrom, IF (movingInto.movingInto AND reanimationInto.reanimationInto, movingInto.movingInto + reanimationInto.reanimationInto, IF(movingInto.movingInto, movingInto.movingInto, reanimationInto.reanimationInto))) AS movingInto,
                            IF(mainTable.code = 'ОАР', @sumReanimationInto, if(movingFrom.movingFrom AND reanimationFrom.reanimationFrom, movingFrom.movingFrom + reanimationFrom.reanimationFrom, IF(movingFrom.movingFrom, movingFrom.movingFrom, reanimationFrom.reanimationFrom))) AS movingFrom,
                            IF(reanimationInto.reanimationInto, @sumReanimationInto := @sumReanimationInto + reanimationInto.reanimationInto, NULL) AS reanimationInto,
                            IF(reanimationFrom.reanimationFrom, @sumReanimationFrom := @sumReanimationFrom + reanimationFrom.reanimationFrom, NULL) AS reanimationFrom,
                            reanimationFrom.reanimationFrom AS reanimation'''
            stmtFrom += ''' JOIN (SELECT @sumReanimationInto := 0, @sumReanimationFrom := 0) tmp
                            LEFT JOIN (%s) reanimation ON reanimation.id = mainTable.id
                            LEFT JOIN (%s) reanimationInto ON reanimationInto.id = mainTable.id
                            LEFT JOIN (%s) reanimationFrom ON reanimationFrom.id = mainTable.id ''' % (subQuery('reanimation'), subQuery('reanimationInto'), subQuery('reanimationFrom'))
        else:
            select += ''', movingInto.movingInto,
                           movingFrom.movingFrom '''

    if orgStructureId:
        if not upgroupFinance:
            stmtFrom = 'rbFinance AS mainTable'
            select = '''mainTable.name AS code'''
        select += ''', received.events AS receivedEvents,
                       movingInto.events AS movingIntoEvents,
                       movingFrom.events AS movingFromEvents,
                       leaved.events AS leavedEvents,
                       leaved.otherClients,
                       leaved.deathClients'''

    stmt = ''' SELECT %s,
                      received.received,
                      leaved.leaved,
                      leaved.leavedDeath,
                      received.receivedVillager,
                      received.receivedChildren,
                      received.receivedOld,
                      received.receivedOther,
                      moving.moving,
                      leaved.leavedOther,
                      leaved.leavedSt,
                      leaved.leavedDCSt,
                      IF(received.eventDays IS NOT NULL, received.eventDays, 0) + IF(moving.eventDays IS NOT NULL, moving.eventDays, 0) + IF(leaved.eventDays IS NOT NULL, leaved.eventDays, 0) + IF(movingInto.eventDays IS NOT NULL, movingInto.eventDays, 0)  AS eventDays,
                      IF(received.eventDaysOld IS NOT NULL, received.eventDaysOld, 0) + IF(moving.eventDaysOld IS NOT NULL, moving.eventDaysOld, 0)  + IF(leaved.eventDaysOld IS NOT NULL, leaved.eventDaysOld, 0) + IF(movingInto.eventDaysOld IS NOT NULL, movingInto.eventDaysOld, 0) AS eventDaysOld
                FROM %s
                LEFT JOIN (%s) received ON received.id = mainTable.id
                LEFT JOIN (%s) movingInto ON movingInto.id = mainTable.id
                LEFT JOIN (%s) movingFrom ON movingFrom.id = mainTable.id
                LEFT JOIN (%s) leaved ON leaved.id = mainTable.id
                LEFT JOIN (%s) moving ON moving.id = mainTable.id
                %s
                ORDER BY mainTable.code''' % (select,
                         stmtFrom,
                         subQuery('received'),
                         subQuery('movingInto'),
                         subQuery('movingFrom'),
                         subQuery('leaved'),
                         subQuery('moving'),
                         'WHERE %s' % (db.table('OrgStructure').alias('mainTable')['id'].inlist(getOrgStructureDescendants(orgStructureId))) if orgStructureId and upgroupFinance else 'WHERE %s ' % (u' mainTable.code != \'Отделение анестезиологии и реаниматологии\'') if reportType == 3 else '')
    return db.query(stmt)

def selectClientData(receivedEvents, movingIntoEvents, otherEvents, leavedEvents, deathEvents, clients):
    db = QtGui.qApp.db
    additionalSelect = ''
    additionalFrom = ''
    cond = []
    makeReport = False
    if receivedEvents:
        additionalSelect += ', receivedEvent.id AS received'
        additionalFrom += 'LEFT JOIN Event receivedEvent ON receivedEvent.client_id = Client.id AND receivedEvent.id IN (%s)\n' % receivedEvents
        cond.append('receivedEvent.id IS NOT NULL')
        makeReport = True
    if movingIntoEvents:
        additionalSelect += ', movingIntoEvent.id AS movingInto'
        additionalFrom += 'LEFT JOIN Event movingIntoEvent ON movingIntoEvent.client_id = Client.id AND movingIntoEvent.id IN (%s)\n' % movingIntoEvents
        cond.append('movingIntoEvent.id IS NOT NULL')
        makeReport = True
    if otherEvents:
        additionalSelect += ', otherEvent.id AS other'
        additionalFrom += 'LEFT JOIN Event otherEvent ON otherEvent.client_id = Client.id AND otherEvent.id IN (%s)\n' % otherEvents
        cond.append('otherEvent.id IS NOT NULL')
        makeReport = True
    if leavedEvents:
        additionalSelect += ', leavedEvent.id AS leaved'
        additionalFrom += 'LEFT JOIN Event leavedEvent ON leavedEvent.client_id = Client.id AND leavedEvent.id IN (%s)\n' % leavedEvents
        cond.append('leavedEvent.id IS NOT NULL')
        makeReport = True
    if deathEvents:
        additionalSelect += ', deathEvent.id AS death'
        additionalFrom += 'LEFT JOIN Event deathEvent ON deathEvent.client_id = Client.id AND deathEvent.id IN (%s)\n' % deathEvents
        cond.append('deathEvent.id IS NOT NULL')
        makeReport = True

    if makeReport:
        stmt = '''SELECT CONCAT_WS(' ', Event.externalId, Client.lastName, Client.firstName, Client.patrName) AS name
                         %s
                  FROM Client
                  INNER JOIN Event ON Event.client_id = Client.id AND Event.deleted = 0
                  %s''' % (additionalSelect, additionalFrom)
        query = db.query(stmt)
        while query.next():
            record = query.record()
            client     = forceString(record.value('name'))
            received   = forceRef(record.value('received'))
            movingInto = forceRef(record.value('movingInto'))
            other      = forceRef(record.value('other'))
            leaved     = forceRef(record.value('leaved'))
            death      = forceRef(record.value('death'))
            if received:
                clients['received'].append(client)
            if movingInto:
                clients['movingInto'].append(client)
            if other:
                clients['other'].append(client)
            if leaved:
                clients['leaved'].append(client)
            if death:
                clients['death'].append(client)
    # return clients

class CReportF007(CReport):

    reportType = [u'Сводка для ОНКО 2', u'Сводка для НИИ Петрова', u'Сводка для Москвы', u'Сводка для Краснодарского края']
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'ЛИСТОК ежедневного учета больных и коечного фонда стационара круглосуточного пребывания, дневного стационара при больничном учреждении.')

    def getSetupDialog(self, parent):
        result = CF007(parent)
        result.setTitle(u'ф007/у-02(ОНКО)')
        return result

    def getPageFormat(self):
        return CPageFormat(pageSize=CPageFormat.A4, orientation=CPageFormat.Landscape, leftMargin=0, topMargin=0, rightMargin=0,  bottomMargin=0)

    def build(self, params):
        orgStructureId = params.get('orgStructureId')
        reportType = params.get('type')
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        if reportType == self.reportType.index(u'Сводка для Москвы'):
            table = createTable(cursor, [('20%', [], CReportBase.AlignCenter), ('60%', [], CReportBase.AlignLeft), ('20%', [], CReportBase.AlignLeft)], 0, 0, 0)
            i = table.addRow()
            table.setText(i, 0, u'МИНИСТЕРСТВО ЗДРАВООХРАНЕНИЯ\nРОССИЙСКОЙ ФЕДЕРАЦИИ\n\n....................................................\n(наименование учреждения)')
            table.setText(i, 2, u'Медицинская документация\nФорма №007/у-02\nУтверждена приказом Минздрава России\nот 30.12.2002г. №413')
            cursor.movePosition(cursor.End, 0)
            cursor.insertBlock()
        table = createTable(cursor, [('100%', [], CReportBase.AlignCenter)], 0, 0, 0)
        i = table.addRow()
        table.setText(i, 0, u'ЛИСТОК ', CReportBase.ReportTitle)
        i = table.addRow()
        table.setText(i, 0, u'\nежедневного учета движения больных и коечного фонда стационара круглосуточного пребывания,\nдневного стационара при больничном учреждении', CReportBase.TableTotal)
        if reportType == self.reportType.index(u'Сводка для Москвы'):
            i = table.addRow()
            table.setText(i, 0, u'\n(подчеркнуть)\n\n____________________________________________________________________\n(наименование отделения, профиля мест)')
            cursor.movePosition(cursor.End, 0)
            cursor.insertBlock()
        if reportType != self.reportType.index(u'Сводка для Москвы'):
            self.dumpParams(cursor, params)
        cursor.insertBlock()

        if reportType == self.reportType.index(u'Сводка для ОНКО 2'):
            tableColumns = [
                ('12%',  [u'Отделение'                                                                        ], CReportBase.AlignLeft),
                ('4%',   [u'число коек',                           u'на конец периода'                        ], CReportBase.AlignRight),
                ('4%',   [u'',                                     u'среднемесячных'                          ], CReportBase.AlignRight),
                ('4%',   [u'Состояло на конец предыдущего периода'                                            ], CReportBase.AlignRight),
                ('4%',   [u'Поступило больных всего'                                                          ], CReportBase.AlignRight),
                ('4%',   [u'в том числе',                          u'из дневного стационара'                  ], CReportBase.AlignRight),
                ('4%',   [u'',                                     u'сельских жителей'                        ], CReportBase.AlignRight),
                ('4%',   [u'',                                     u'детей до 17 лет'                         ], CReportBase.AlignRight),
                ('4%',   [u'',                                     u'старше трудоспособного возраста'         ], CReportBase.AlignRight),
                ('4%',   [u'переведено',                           u'из др.отделений'                         ], CReportBase.AlignRight),
                ('4%',   [u'',                                     u'в др.отделения'                          ], CReportBase.AlignRight),
                ('4%',   [u'Выписано больных',                     u'всего'                                   ], CReportBase.AlignRight),
                ('4%',   [u'',                                     u'в том числе старше трудоспособного возраста'], CReportBase.AlignRight),
                ('4%',   [u'',                                     u'из них в дневные стационары (всех типов)'], CReportBase.AlignRight),
                ('4%',   [u'Умерло'                                                                           ], CReportBase.AlignRight),
                ('4%',   [u'в том числе',                          u'детей до 17 лет'                         ], CReportBase.AlignRight),
                ('4%',   [u'',                                     u'старше трудоспособного возраста'         ], CReportBase.AlignRight),
                ('4%',   [u'Состоит на конец периода'                                                         ], CReportBase.AlignRight),
                ('4%',   [u'Проведено койко-дней'                                                             ], CReportBase.AlignRight),
                ('4%',   [u'в том числе старше трудоспособного возраста'                                      ], CReportBase.AlignRight),
                ('4%',   [u'число койко-дней закрытия'                                                        ], CReportBase.AlignRight),
                ('4%',   [u'поступило иногородних больных'                                                    ], CReportBase.AlignRight),
                ('4%',   [u'поступило экстренных больных'                                                     ], CReportBase.AlignRight)
            ]
        if reportType == self.reportType.index(u'Сводка для Краснодарского края'):
            tableColumns = [
                ('24%',  [u''                                                 ], CReportBase.AlignLeft),
                ('7%',   [u'Кол-во коек'                                    ], CReportBase.AlignRight),
                ('8%',   [u'Состояло больных'                                 ], CReportBase.AlignRight),
                ('7%',   [u'Поступило',                       u'всего'        ], CReportBase.AlignRight),
                ('7%',   [u'',                                u'экстрено'     ], CReportBase.AlignRight),
                ('7%',   [u'',                                u'планово'      ], CReportBase.AlignRight),
                ('7%',   [u'Внутрибольничные перемещения',   u'из отделения' ], CReportBase.AlignRight),
                ('7%',   [u'',                                u'в отделение'  ], CReportBase.AlignRight),
                ('7%',   [u'Выписано',                        u'всего'        ], CReportBase.AlignRight),
                ('7%',   [u'',                                u'из них умерло'], CReportBase.AlignRight),
                ('7%',   [u'Состоит больных на отчетную дату', u'всего'       ], CReportBase.AlignRight),
                ('6%',   [u'',                                 u'в реанимации'], CReportBase.AlignRight),
                ('8%',   [u'Свободных коек'                                   ], CReportBase.AlignRight)
            ]
        elif reportType in [self.reportType.index(u'Сводка для НИИ Петрова'), self.reportType.index(u'Сводка для Москвы')]:
            tableColumns = [
                ('20%',  [u''                                          ], CReportBase.AlignLeft),
                ('3?',   [u'Код'                                                                                                        ], CReportBase.AlignRight),
                ('3?',   [u'Фактически развернуто коек, включая койки, свернутые на ремонт'                                             ], CReportBase.AlignRight),
                ('3?',   [u'В том числе коек, свернутых на ремонт'                                                                      ], CReportBase.AlignRight),
                ('3?',   [u'Движение больных за истекшие сутки',                            u'состояло больных на начало истекших суток'], CReportBase.AlignRight),
                ('3?',   [u'',                                                              u'поступило больных',                           u'всего'      ], CReportBase.AlignRight),
                ('3?',   [u'',                                                              u'',                                            u'в т.ч. Из дневного стациолнрара'], CReportBase.AlignRight),
                ('3?',   [u'',                                                              u'',                                            u'из них(из гр.6)',                 u'сельских жителей'], CReportBase.AlignRight),
                ('3?',   [u'',                                                              u'',                                            u'',                                u'0-17 лет'        ], CReportBase.AlignRight),
                ('3?',   [u'',                                                              u'перведено больных внутри больницы',           u'из других отделений'], CReportBase.AlignRight),
                ('3?',   [u'',                                                              u'',                                            u'в другие отделения'], CReportBase.AlignRight),
                ('3?',   [u'',                                                              u'выписано больных',                            u'всего'                             ], CReportBase.AlignRight),
                ('3?',   [u'',                                                              u'',                                            u'в т.ч.',                          u'переведенных в другие стационары'                         ], CReportBase.AlignRight),
                ('3?',   [u'',                                                              u'',                                            u'',                                u'в круглосуточный стационар'], CReportBase.AlignRight),
                ('3?',   [u'',                                                              u'',                                            u'',                                u'в дневной стационар'                     ], CReportBase.AlignRight),
                ('3?',   [u'',                                                              u'умерло'], CReportBase.AlignRight),
                ('3?',   [u'На начало текущего дня',                                        u'состоит больных всего'], CReportBase.AlignRight),
                ('3?',   [u'',                                                              u'состоит матерей при больных детях'], CReportBase.AlignRight)
            ]
            if reportType == self.reportType.index(u'Сводка для НИИ Петрова'):
                tableColumns.insert(9,  ('3?',   [u'', u'', u'', u'нетрудоспособного возраста'], CReportBase.AlignRight))
                tableColumns.insert(10, ('3?',   [u'', u'', u'', u'иногородние'], CReportBase.AlignRight))
                tableColumns.append(('3?', [u'', u'свободных мест'], CReportBase.AlignRight))
            else:
                tableColumns.insert(9, ('3?', [u'', u'', u'', u'60 лет и старше'], CReportBase.AlignRight))
                tableColumns.append(('3?', [u'', u'свободных мест', u'мужских', u''], CReportBase.AlignRight))
                tableColumns.append(('3?', [u'', u'', u'женских', u''], CReportBase.AlignRight))

        table = createTable(cursor, tableColumns)

        if reportType == self.reportType.index(u'Сводка для ОНКО 2'):
            table.mergeCells(0, 0, 2, 1)
            table.mergeCells(0, 1, 1, 2)
            table.mergeCells(0, 3, 2, 1)
            table.mergeCells(0, 4, 2, 1)
            table.mergeCells(0, 5, 1, 4)
            table.mergeCells(0, 9, 1, 2)
            table.mergeCells(0, 11, 1, 3)
            table.mergeCells(0, 14, 2, 1)
            table.mergeCells(0, 15, 1, 2)
            table.mergeCells(0, 17, 2, 1)
            table.mergeCells(0, 18, 2, 1)
            table.mergeCells(0, 19, 2, 1)
            table.mergeCells(0, 20, 2, 1)
            table.mergeCells(0, 21, 2, 1)
            table.mergeCells(0, 22, 2, 1)
            self.rowSize = len(tableColumns) - 1
            begRow = 3
            shiftColumns = 1
        elif reportType == self.reportType.index(u'Сводка для Краснодарского края'):
            table.mergeCells(0, 0, 2, 1)
            table.mergeCells(0, 1, 2, 1)
            table.mergeCells(0, 2, 2, 1)
            table.mergeCells(0, 3, 1, 3)
            table.mergeCells(0, 6, 1, 2)
            table.mergeCells(0, 8, 1, 2)
            table.mergeCells(0, 10, 1, 2)
            table.mergeCells(0, 12, 2, 1)
            self.rowSize = len(tableColumns) - 1
            begRow = 3
            shiftColumns = 1
        elif reportType in [self.reportType.index(u'Сводка для НИИ Петрова'), self.reportType.index(u'Сводка для Москвы')]:
            table.mergeCells(0, 0, 4, 1)
            table.mergeCells(0, 1, 4, 1)
            table.mergeCells(0, 2, 4, 1)
            table.mergeCells(0, 3, 4, 1)
            if reportType == self.reportType.index(u'Сводка для НИИ Петрова'):
                table.mergeCells(0, 4, 1, 14)
                table.mergeCells(1, 4, 3, 1)
                table.mergeCells(1, 5, 1, 6)
                table.mergeCells(2, 5, 2, 1)
                table.mergeCells(2, 6, 2, 1)
                table.mergeCells(2, 7, 1, 4)
                table.mergeCells(1, 11, 1, 2)
                table.mergeCells(2, 11, 2, 1)
                table.mergeCells(2, 12, 2, 1)
                table.mergeCells(1, 13, 1, 4)
                table.mergeCells(2, 13, 2, 1)
                table.mergeCells(2, 14, 1, 3)
                table.mergeCells(1, 17, 3, 1)
                table.mergeCells(0, 18, 1, 4)
                table.mergeCells(1, 18, 3, 1)
                table.mergeCells(1, 19, 3, 1)
                table.mergeCells(1, 20, 3, 1)
                self.rowSize = len(tableColumns) - 4
            else:
                table.mergeCells(0, 4, 1, 13)
                table.mergeCells(1, 4, 3, 1)
                table.mergeCells(1, 5, 1, 6)
                table.mergeCells(2, 5, 2, 1)
                table.mergeCells(2, 6, 2, 1)
                table.mergeCells(2, 7, 1, 3)
                table.mergeCells(1, 10, 1, 2)
                table.mergeCells(2, 10, 2, 1)
                table.mergeCells(2, 11, 2, 1)
                table.mergeCells(1, 12, 1, 4)
                table.mergeCells(2, 12, 2, 1)
                table.mergeCells(2, 13, 1, 3)
                table.mergeCells(1, 16, 3, 1)
                table.mergeCells(0, 17, 1, 4)
                table.mergeCells(1, 17, 3, 1)
                table.mergeCells(1, 18, 3, 1)
                table.mergeCells(1, 19, 1, 2)
                table.mergeCells(2, 19, 2, 1)
                table.mergeCells(2, 20, 2, 1)
                self.rowSize = len(tableColumns) - 2
            begRow = 5
            shiftColumns = 2

        i = table.addRow()
        for column in xrange(len(tableColumns)):
            table.setText(i, column, column + 1)
        i = table.addRow()
        table.setText(i, 0, u'Всего', CReportBase.TableTotal)
        if not orgStructureId:
            i = table.addRow()
            table.setText(i, 0, u'Всего ДС', CReportBase.TableTotal)

        datasRecord, clients = self.getQueryDate(query, reportType, orgStructureId)
        total = [0]*self.rowSize
        totalDC = [0]*self.rowSize
        for datas in datasRecord:
            i = table.addRow()
            for index, data in enumerate(datas):
                if data is None:
                    continue
                if (index and reportType in (self.reportType.index(u'Сводка для Краснодарского края'), self.reportType.index(u'Сводка для ОНКО 2'))) or index > 1:
                    formIndex = index - shiftColumns
                    if ((index == 1 and reportType == self.reportType.index(u'Сводка для Краснодарского края')) or index in [2, 3]) and orgStructureId:
                        total[formIndex] = data
                    total[formIndex] += data
                    if datas[0].startswith(u'Д/С') and not orgStructureId:
                        totalDC[formIndex] += data
                table.setText(i, index, data)

        for index in xrange(self.rowSize):
            if (index == 4 and reportType == self.reportType.index(u'Сводка для НИИ Петрова')) or (index in [4, 16] and reportType == self.reportType.index(u'Сводка для Москвы')):
                continue
            table.setText(begRow, index + shiftColumns, total[index], CReportBase.TableTotal)
            if not orgStructureId:
                table.setText(begRow + 1, index + shiftColumns, totalDC[index], CReportBase.TableTotal)

        if orgStructureId:
            cursor.movePosition(QtGui.QTextCursor.End)
            cursor.insertBlock()
            cursor.insertBlock()
            cursor.insertBlock()
            tableColumns = [
                ('15%',   [u'Фамилия, и., о. поступивших'], CReportBase.AlignLeft),
                ('15%',   [u'Фамилия, и., о. поступивших из круглосуточного стационара'], CReportBase.AlignLeft),
                ('15%',   [u'Фамилия, и., о. выписанных'], CReportBase.AlignLeft),
                ('15%',   [u'Фамилия, и., о. переведенных', u'в другие отделения данной больницы'], CReportBase.AlignLeft),
                ('15%',   [u'',                             u'в другие стационары'], CReportBase.AlignLeft),
                ('15%',   [u'Фамилия, и., о. умерших'], CReportBase.AlignLeft),
                ('15%',   [u'Фамилия, и., о. больных, находящихся во временном отпуску'], CReportBase.AlignLeft)
            ]
            table = createTable(cursor, tableColumns)

            table.mergeCells(0, 0, 2, 1)
            table.mergeCells(0, 1, 2, 1)
            table.mergeCells(0, 2, 2, 1)
            table.mergeCells(0, 3, 1, 2)
            table.mergeCells(0, 5, 2, 1)
            table.mergeCells(0, 6, 2, 1)

            columns = {'received': 0, 'movingInto': 3, 'other': 4, 'leaved': 2, 'death': 5}

            i = table.addRow()
            for key, clientList in clients.iteritems():
                column = columns[key]
                for index, client in enumerate(clientList):
                    table.setText(i, column, forceString(index + 1) + '. ' + client + '\n' + ' ')
        return doc

    def getQueryDate(self, query, reportType, orgStructureId, ditail=False):
        dates = []
        clients = {'received': [], 'movingInto': [], 'other': [], 'leaved': [], 'death': []}
        keyValForDitail = lambda value: forceString(value) if ditail else forceInt(value)
        while query.next():
            record = query.record()
            code              = forceString(record.value('code'))
            permanent         = forceInt(record.value('permanent'))
            involution        = forceInt(record.value('involution'))
            moving            = forceInt(record.value('moving'))
            received          = keyValForDitail(record.value('received'))
            receivedPlan      = forceInt(record.value('receivedPlan'))
            receivedExtra     = forceInt(record.value('receivedExtra'))
            receivedVillager  = forceInt(record.value('receivedVillager'))
            receivedChildren  = forceInt(record.value('receivedChildren'))
            receivedBefore17  = forceInt(record.value('receivedBefore17'))
            receivedOld       = forceInt(record.value('receivedOld'))
            receivedOther     = forceInt(record.value('receivedOther'))
            movingFrom        = keyValForDitail(record.value('movingFrom'))
            movingInto        = keyValForDitail(record.value('movingInto'))
            leaved            = keyValForDitail(record.value('leaved'))
            leavedOld         = forceInt(record.value('leavedOld'))
            leavedOther       = forceInt(record.value('leavedOther'))
            leavedSt          = forceInt(record.value('leavedSt'))
            leavedDCSt        = forceInt(record.value('leavedDCSt'))
            leavedDeath       = forceInt(record.value('leavedDeath'))
            leavedDeathChildren = forceInt(record.value('leavedDeathChildren'))
            leavedDeathOld    = forceInt(record.value('leavedDeathOld'))
            reanimation       = forceInt(record.value('reanimation'))
            men               = forceInt(record.value('men'))
            women             = forceInt(record.value('women'))
            menBed            = forceInt(record.value('menBed'))
            womenBed          = forceInt(record.value('womenBed'))
            eventDays         = forceInt(record.value('eventDays'))
            eventDaysOld      = forceInt(record.value('eventDaysOld'))
            if orgStructureId:
                selectClientData(forceString(record.value('receivedEvents')), forceString(record.value('movingIntoEvents')), forceString(record.value('otherEvents')), forceString(record.value('leavedEvents')), forceString(record.value('deathEvents')), clients)
            isInHosp = moving + received - movingFrom + movingInto - leaved
            bookedBed = permanent - isInHosp
            leaved -= leavedDeath
            leavedOld -= leavedDeathOld
            if reportType == self.reportType.index(u'Сводка для ОНКО 2'):
                dates.append([code if not ditail else None, permanent, permanent, moving, received, None, receivedVillager, receivedBefore17, receivedOld, movingInto, movingFrom, leaved, leavedOld, leavedDCSt, leavedDeath, leavedDeathChildren, leavedDeathOld, (isInHosp if not ditail else None), eventDays, eventDaysOld, None, receivedOther, receivedExtra])
            if reportType == self.reportType.index(u'Сводка для Краснодарского края'):
                dates.append([code if not ditail else None, permanent, moving, received, receivedExtra, receivedPlan, movingFrom, movingInto, leaved, leavedDeath, isInHosp if not ditail else None, reanimation, bookedBed if bookedBed > 0 else 0])
            elif reportType == self.reportType.index(u'Сводка для НИИ Петрова'):
                dates.append([code if not ditail else None, None, permanent, involution, moving, received, None, receivedVillager, receivedChildren, receivedOld, receivedOther, movingInto, movingFrom, leaved, leavedOther, leavedSt, leavedDCSt, leavedDeath, isInHosp if not ditail else None, None, None])
            elif reportType == self.reportType.index(u'Сводка для Москвы'):
                if men < 0:
                    men = 0
                if women < 0:
                    women = 0
                menBed = menBed - men
                womenBed = womenBed - women
                dates.append([code if not ditail else None, None, permanent, involution, moving, received, None, receivedVillager, receivedChildren, receivedOld, movingInto, movingFrom, leaved, leavedOther, leavedSt, leavedDCSt, leavedDeath, isInHosp if not ditail else None, None, menBed if menBed > 0 else 0, womenBed if womenBed > 0 else 0])
        return dates, clients


class CF007(QtGui.QDialog, Ui_ReportF007):
    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.edtBegTime.setTime(params.get('begTime', QtCore.QTime(0, 0)))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.chkOAR.setChecked(params.get('orgstructureOAR', False))
        self.cmbReportType.setCurrentIndex(params.get('type', 0))
        self.chkUngroupFinance.setChecked(params.get('ungroupFinance', False))

    def params(self):
        params = {}
        params['begDate']     = self.edtBegDate.date()
        params['endDate']     = self.edtEndDate.date()
        params['orgStructureId'] = self.cmbOrgStructure.value()
        params['orgStructureOAR'] = self.chkOAR.isChecked()
        params['type'] = self.cmbReportType.currentIndex()
        params['begTime'] = self.edtBegTime.time()
        params['ungroupFinance'] = self.chkUngroupFinance.isChecked()
        return params

    @QtCore.pyqtSlot(int)
    def on_cmbReportType_currentIndexChanged(self, index):
        bool = not self.cmbReportType.currentText() == u'Сводка для Краснодарского края'
        self.chkOAR.setEnabled(bool)
        if not bool:
            self.chkOAR.setChecked(bool)

    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        bool = forceBool(self.cmbOrgStructure.value())
        self.chkUngroupFinance.setEnabled(bool)
        self.chkOAR.setEnabled(bool)
        if not bool:
            self.chkUngroupFinance.setChecked(bool)
            self.chkOAR.setChecked(bool)

