# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.database               import addDateInRange
from library.Utils                  import forceDouble, forceInt, forceRef, forceString, getVal
from Orgs.Utils                     import getOrganisationInfo
from Reports.Report                 import CReport
from Reports.ReportBase             import createTable, CReportBase
from Reports.StatReportDD2013Weekly import CReportDD2013WeeklySetupDialog


def selectData(params):
    sex = params.get('sex', 0)
    ageFrom = params.get('ageFrom', 0)
    ageTo = params.get('ageTo', 150)
    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)
    eventTypeId  = params.get('eventTypeId', None)
    db = QtGui.qApp.db
    tableEvent  = db.table('Event')
    tableClient = db.table('Client')
    tableEventType = db.table('EventType')
    tableEventKind = db.table('rbEventKind')
    tableAccountItem = db.table('Account_Item')
    tableClientSocStatus = db.table('ClientSocStatus')
    tableSocStatusType = db.table('rbSocStatusType')

    cols = [tableClient['sex'], tableEvent['id'].alias('event_id'), tableEventKind['code'],
            tableSocStatusType['code'].alias('socStatusCode')]

    queryTable = tableEvent.innerJoin(tableEventType, db.joinAnd([tableEventType['id'].eq(tableEvent['eventType_id']), tableEventType['deleted'].eq(0)]))
    queryTable = queryTable.innerJoin(tableEventKind, db.joinAnd([tableEventType['eventKind_id'].eq(tableEventKind['id']), tableEventKind['code'].inlist(['01', '02', '04'])]))
    queryTable = queryTable.innerJoin(tableClient, db.joinAnd([tableClient['id'].eq(tableEvent['client_id']), tableClient['deleted'].eq(0)]))
    queryTable = queryTable.leftJoin(tableClientSocStatus, db.joinAnd([tableClientSocStatus['client_id'].eq(tableClient['id']), tableClientSocStatus['deleted'].eq(0)]))
    queryTable = queryTable.leftJoin(tableSocStatusType, tableSocStatusType['id'].eq(tableClientSocStatus['socStatusType_id']))

    cond = [tableEvent['deleted'].eq(0),
            ]
    if not params.get('countUnfinished', False):
        queryTable = queryTable.leftJoin(tableAccountItem, tableAccountItem['event_id'].eq(tableEvent['id']))
        cols.append('SUM(Account_Item.sum) as sum')
        addDateInRange(cond, tableEvent['execDate'], begDate, endDate)
        cond.append('isEventPayed(Event.id)')
    else:
        addDateInRange(cond, tableEvent['setDate'], begDate, endDate)
    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append('Event.setDate >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)'%ageFrom)
        cond.append('Event.setDate < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)'%(ageTo+1))
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    group = ['event_id', 'socStatusCode']
    stmt = db.selectStmt(queryTable, cols, cond, group = group)
    return db.query(stmt)


class CReportExposedDD(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Сведения о предъявленых к оплате реестрах счетов за проведенную диспансеризацию взрослого населения')


    def getSetupDialog(self, parent):
        result = CReportDD2013WeeklySetupDialog(parent)
        result.setTitle(self.title())
        result.setPayStatusVisible(False)
        return result



    def build(self, params):
        groups = [u'Всего взрослых (в возрасте 18 лет и старше)\nиз них:',
                  u'\tмужчины',
                  u'\tженщины',
                  u'Работаюших граждан\nиз них:',
                  u'\tмужчины',
                  u'\tженщины',
                  u'Неработающих граждан\nиз них:',
                  u'\tмужчины',
                  u'\tженщины',
                  u'Справочно: из строки 1 обучающиеся в образовательных организациях по очной форме',
                  u'из строки 2 мужчины',
                  u'из строки 3 женщины']

        processedEvents = []
        totalSum = [0.0] * 12
        amountFS = [0] * 12
        sumFS = [0.0] * 12
        amountSS = [0] * 12
        sumSS = [0.0] * 12

        query = selectData(params)
        while query.next():
            record = query.record()
            eventId = forceRef(record.value('event_id'))
            if eventId in processedEvents:
                continue
            sex = forceInt(record.value('sex'))
            sum = forceDouble(record.value('sum'))
            code = forceString(record.value('code'))
            socStatus = forceString(record.value('socStatusCode'))

            totalSum[0] += sum
            if sex:
                totalSum[sex] += sum
            if socStatus == u'с05': # работающий
                totalSum[3] += sum
                if sex:
                    totalSum[3+sex] += sum
            elif socStatus == u'с06': # неработающий
                totalSum[6] += sum
                if sex:
                    totalSum[6+sex] += sum
            elif socStatus == u'с04': # студент
                totalSum[9] += sum
                if sex:
                    totalSum[9+sex] += sum

            if code in ('01', '04'):
                amountFS[0] += 1
                sumFS[0] += sum
                if sex:
                    amountFS[sex] += 1
                    sumFS[sex] += sum

                if socStatus == u'с05': # работающий
                    amountFS[3] += 1
                    sumFS[3] += sum
                    if sex:
                        amountFS[3+sex] += 1
                        sumFS[3+sex] += sum
                if socStatus == u'с06': # работающий
                    amountFS[6] += 1
                    sumFS[6] += sum
                    if sex:
                        amountFS[6+sex] += 1
                        sumFS[6+sex] += sum
                if socStatus == u'с04': # работающий
                    amountFS[9] += 1
                    sumFS[9] += sum
                    if sex:
                        amountFS[9+sex] += 1
                        sumFS[9+sex] += sum

            elif code == '02':
                amountSS[0] += 1
                sumSS[0] += sum
                if sex:
                    amountSS[sex] += 1
                    sumSS[sex] += sum

                if socStatus == u'с05': # работающий
                    amountSS[3] += 1
                    sumSS[3] += sum
                    if sex:
                        amountSS[3+sex] += 1
                        sumSS[3+sex] += sum
                if socStatus == u'с06': # работающий
                    amountSS[6] += 1
                    sumSS[6] += sum
                    if sex:
                        amountSS[6+sex] += 1
                        sumSS[6+sex] += sum
                if socStatus == u'с04': # работающий
                    amountSS[9] += 1
                    sumSS[9] += sum
                    if sex:
                        amountSS[9+sex] += 1
                        sumSS[9+sex] += sum
            processedEvents.append(eventId)
        rowSize = 7

        # now text
        bf = QtGui.QTextBlockFormat()
        bf.setAlignment(QtCore.Qt.AlignCenter)

        orgId = QtGui.qApp.currentOrgId()
        orgInfo = getOrganisationInfo(orgId)
        if not orgInfo:
            QtGui.qApp.preferences.appPrefs['orgId'] = QtCore.QVariant()
        shortName = getVal(orgInfo, 'shortName', u'не задано')


        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)


        cursor.setBlockFormat(bf)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertText(u'\nЛПУ: ' + shortName)
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ( '15%', [u'Группы', u'', u''], CReportBase.AlignLeft),
            ( '10%', [u'№ стр.', u'', u''], CReportBase.AlignCenter),
            ( '15%', [u'Объем средств, предъявленных к оплате в рамках диспансеризации на отчетную дату, всего', u'тыс. рублей', u''], CReportBase.AlignRight),
            ( '15%', [u'В том числе:', u'В рамках I этапа диспансеризации', u'кол-во случаев'], CReportBase.AlignRight),
            ( '15%', [u'', u'', u'тыс. рублей'], CReportBase.AlignRight),
            ( '15%', [u'', u'в рамках II этапа диспансеризации', u'кол-во случаев'], CReportBase.AlignRight),
            ( '15%', [u'', u'', u'тыс. рублей'], CReportBase.AlignRight)
        ]

        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 3, 1)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 1, 4)
        table.mergeCells(1, 3, 1, 2)
        table.mergeCells(1, 5, 1, 2)

        i = table.addRow()

        for j in xrange(rowSize):
            table.setText(i, j, j+1, blockFormat = bf)

        for k in range(12):
            i = table.addRow()
            table.setText(i, 0, groups[k])
            table.setText(i, 1, k+1)
            table.setText(i, 2, '%.2f' % (totalSum[k]/1000))
            table.setText(i, 3, amountFS[k])
            table.setText(i, 4, '%.2f' % (sumFS[k]/1000))
            table.setText(i, 5, amountSS[k])
            table.setText(i, 6, '%.2f' % (sumSS[k]/1000))
        return doc
