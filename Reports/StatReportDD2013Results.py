# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

from library.database   import addDateInRange
from library.Utils      import forceDouble, forceInt, forceRef, forceString, getVal
from Orgs.Utils         import getOrganisationInfo
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.StatReportDD2013Weekly import CReportDD2013WeeklySetupDialog


def selectClientsData(params):
    sex = params.get('sex', 0)
    ageFrom = params.get('ageFrom', 0)
    ageTo = params.get('ageTo', 150)
    begDate = params.get('begDate', None)
    terType = params.get('terType', None)
    eventTypeId  = params.get('eventTypeId', None)
    db = QtGui.qApp.db

    tableClient = db.table('Client')
    tableEvent = db.table('Event')
    tableClientSocStatus = db.table('ClientSocStatus')
    tableSocStatusType = db.table('rbSocStatusType')

    if terType == 1:
        cols = ['COUNT(DISTINCT IF(kladr.STREET.CODE, Client.id, NULL)) as totalClients',
                'COUNT(DISTINCT IF(kladr.STREET.CODE AND Client.sex = 1, Client.id, NULL)) as totalMen',
                'COUNT(DISTINCT IF(kladr.STREET.CODE AND Client.sex = 2, Client.id, NULL)) as totalWomen',
                u'COUNT(DISTINCT IF(kladr.STREET.CODE AND rbSocStatusType.code LIKE \'работающий%\', Client.id, NULL)) as totalWorking',
                u'COUNT(DISTINCT IF(kladr.STREET.CODE AND rbSocStatusType.code LIKE \'работающий%\' AND Client.sex = 1, Client.id, NULL)) as menWorking',
                u'COUNT(DISTINCT IF(kladr.STREET.CODE AND rbSocStatusType.code LIKE \'работающий%\' AND Client.sex = 2, Client.id, NULL)) as womenWorking',
                u'COUNT(DISTINCT IF(kladr.STREET.CODE AND rbSocStatusType.code LIKE \'неработающий%\', Client.id, NULL)) as totalUnemployed',
                u'COUNT(DISTINCT IF(kladr.STREET.CODE AND rbSocStatusType.code LIKE \'неработающий%\' AND Client.sex = 1, Client.id, NULL)) as menUnemployed',
                u'COUNT(DISTINCT IF(kladr.STREET.CODE AND rbSocStatusType.code LIKE \'неработающий%\' AND Client.sex = 2, Client.id, NULL)) as womenUnemployed',
                u'COUNT(DISTINCT IF(kladr.STREET.CODE AND rbSocStatusType.code LIKE \'студент%\', Client.id, NULL)) as totalStudents',
                u'COUNT(DISTINCT IF(kladr.STREET.CODE AND rbSocStatusType.code LIKE \'студент%\' AND Client.sex = 1, Client.id, NULL)) as menStudents',
                u'COUNT(DISTINCT IF(kladr.STREET.CODE AND rbSocStatusType.code LIKE \'студент%\' AND Client.sex = 2, Client.id, NULL)) as womenStudents'
        ]
    elif terType == 2:
        cols = ['COUNT(DISTINCT IF(ClientAttach.id, Client.id, NULL)) as totalClients',
                'COUNT(DISTINCT IF(ClientAttach.id AND Client.sex = 1, Client.id, NULL)) as totalMen',
                'COUNT(DISTINCT IF(ClientAttach.id AND Client.sex = 2, Client.id, NULL)) as totalWomen',
                u'COUNT(DISTINCT IF(ClientAttach.id AND rbSocStatusType.code LIKE \'работающий%\', Client.id, NULL)) as totalWorking',
                u'COUNT(DISTINCT IF(ClientAttach.id AND rbSocStatusType.code LIKE \'работающий%\' AND Client.sex = 1, Client.id, NULL)) as menWorking',
                u'COUNT(DISTINCT IF(ClientAttach.id AND rbSocStatusType.code LIKE \'работающий%\' AND Client.sex = 2, Client.id, NULL)) as womenWorking',
                u'COUNT(DISTINCT IF(ClientAttach.id AND rbSocStatusType.code LIKE \'неработающий%\', Client.id, NULL)) as totalUnemployed',
                u'COUNT(DISTINCT IF(ClientAttach.id AND rbSocStatusType.code LIKE \'неработающий%\' AND Client.sex = 1, Client.id, NULL)) as menUnemployed',
                u'COUNT(DISTINCT IF(ClientAttach.id AND rbSocStatusType.code LIKE \'неработающий%\' AND Client.sex = 2, Client.id, NULL)) as womenUnemployed',
                u'COUNT(DISTINCT IF(ClientAttach.id AND rbSocStatusType.code LIKE \'студент%\', Client.id, NULL)) as totalStudents',
                u'COUNT(DISTINCT IF(ClientAttach.id AND rbSocStatusType.code LIKE \'студент%\' AND Client.sex = 1, Client.id, NULL)) as menStudents',
                u'COUNT(DISTINCT IF(ClientAttach.id AND rbSocStatusType.code LIKE \'студент%\' AND Client.sex = 2, Client.id, NULL)) as womenStudents'
                ]
    else:
        cols = ['COUNT(DISTINCT Client.id) as totalClients',
                'COUNT(DISTINCT IF(Client.sex = 1, Client.id, NULL)) as totalMen',
                'COUNT(DISTINCT IF(Client.sex = 2, Client.id, NULL)) as totalWomen',
                u'COUNT(DISTINCT IF(rbSocStatusType.code LIKE \'работающий%\', Client.id, NULL)) as totalWorking',
                u'COUNT(DISTINCT IF(rbSocStatusType.code LIKE \'работающий%\' AND Client.sex = 1, Client.id, NULL)) as menWorking',
                u'COUNT(DISTINCT IF(rbSocStatusType.code LIKE \'работающий%\' AND Client.sex = 2, Client.id, NULL)) as womenWorking',
                u'COUNT(DISTINCT IF(rbSocStatusType.code LIKE \'неработающий%\', Client.id, NULL)) as totalUnemployed',
                u'COUNT(DISTINCT IF(rbSocStatusType.code LIKE \'неработающий%\' AND Client.sex = 1, Client.id, NULL)) as menUnemployed',
                u'COUNT(DISTINCT IF(rbSocStatusType.code LIKE \'неработающий%\' AND Client.sex = 2, Client.id, NULL)) as womenUnemployed',
                u'COUNT(DISTINCT IF(rbSocStatusType.code LIKE \'студент%\', Client.id, NULL)) as totalStudents',
                u'COUNT(DISTINCT IF(rbSocStatusType.code LIKE \'студент%\' AND Client.sex = 1, Client.id, NULL)) as menStudents',
                u'COUNT(DISTINCT IF(rbSocStatusType.code LIKE \'студент%\' AND Client.sex = 2, Client.id, NULL)) as womenStudents'
                ]

    queryTable = tableClient.leftJoin(tableClientSocStatus, db.joinAnd([tableClientSocStatus['client_id'].eq(tableClient['id']), tableClientSocStatus['deleted'].eq(0)]))
    queryTable = queryTable.leftJoin(tableSocStatusType, tableSocStatusType['id'].eq(tableClientSocStatus['socStatusType_id']))
    if terType == 1:
        tableClientAddress = db.table('ClientAddress')
        tableAddress = db.table('Address')
        tableAddressHouse = db.table('AddressHouse')
        tableStreet = db.table('kladr.STREET')
        OKATO=forceString(QtGui.qApp.db.translate(
                'Organisation', 'id', QtGui.qApp.currentOrgId(), 'OKATO'))

        queryTable = queryTable.leftJoin(tableClientAddress, 'ClientAddress.id = getClientLocAddressId(Client.id)')
        queryTable = queryTable.leftJoin(tableAddress, db.joinAnd([tableAddress['id'].eq(tableClientAddress['address_id']), tableAddress['deleted'].eq(0)]))
        queryTable = queryTable.leftJoin(tableAddressHouse, db.joinAnd([tableAddressHouse['id'].eq(tableAddress['house_id']), tableAddressHouse['deleted'].eq(0)]))
        queryTable = queryTable.leftJoin(tableStreet, db.joinAnd([tableStreet['CODE'].eq(tableAddressHouse['KLADRStreetCode']), tableStreet['OCATD'].like('%s%%' % OKATO[:5])]))
    elif terType == 2:
        tableClientAttach = db.table('ClientAttach')
        tableRBAttachType = db.table('rbAttachType')
        attachTypeId = forceRef(db.translate(tableRBAttachType, 'code', 1, 'id'))
        queryTable = queryTable.leftJoin(tableClientAttach, db.joinAnd([
            tableClientAttach['client_id'].eq(tableClient['id']),
            tableClientAttach['deleted'].eq(0),
            tableClientAttach['LPU_id'].eq(QtGui.qApp.currentOrgId()),
            tableClientAttach['attachType_id'].eq(attachTypeId)]))
    cond = []
    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append('%s >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)'% (db.formatDate(begDate), ageFrom))
        cond.append('%s < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)'%(db.formatDate(begDate), (ageTo+1)))
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))

    stmt = db.selectStmt(queryTable, cols, cond)
    return db.query(stmt)

def selectEventsData(params):
    sex = params.get('sex', 0)
    ageFrom = params.get('ageFrom', 0)
    ageTo = params.get('ageTo', 150)
    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)
    terType = params.get('terType', None)
    eventTypeId  = params.get('eventTypeId', None)
    db = QtGui.qApp.db

    tableEvent  = db.table('Event')
    tableClient = db.table('Client')
    tableEventType = db.table('EventType')
    tableEventKind = db.table('rbEventKind')
    tableAccountItem = db.table('Account_Item')
    tableClientSocStatus = db.table('ClientSocStatus')
    tableSocStatusType = db.table('rbSocStatusType')
    tableRBResult = db.table('rbResult')
    tableRBHealthGroup = db.table('rbHealthGroup')
    tableDiagnostic = db.table('Diagnostic')

    cols = ['rbEventKind.code as eventKindCode',
            'Account_Item.sum',
            'rbResult.code as resultCode',
            'rbHealthGroup.code as HGCode',
            'Client.id as client_id',
            'Event.id as event_id',
            'Account_Item.id as accountItem_id',
            'rbSocStatusType.name as socStatusName',
            'Client.sex']
    queryTable = tableClient.leftJoin(tableEvent, db.joinAnd([tableEvent['client_id'].eq(tableClient['id']), tableEvent['deleted'].eq(0)]))
    queryTable = queryTable.leftJoin(tableEventType, db.joinAnd([tableEvent['eventType_id'].eq(tableEventType['id']), tableEventType['deleted'].eq(0)]))
    queryTable = queryTable.leftJoin(tableEventKind, db.joinAnd([tableEventType['eventKind_id'].eq(tableEventKind['id']), tableEventKind['code'].inlist(['01', '02', '04'])]))
    queryTable = queryTable.leftJoin(tableDiagnostic, db.joinAnd([tableDiagnostic['event_id'].eq(tableEvent['id']), tableDiagnostic['deleted'].eq(0)]))
    queryTable = queryTable.leftJoin(tableRBResult, tableRBResult['id'].eq(tableEvent['result_id']))
    queryTable = queryTable.leftJoin(tableRBHealthGroup, tableRBHealthGroup['id'].eq(tableDiagnostic['healthGroup_id']))
    queryTable = queryTable.leftJoin(tableAccountItem, tableAccountItem['event_id'].eq(tableEvent['id']))
    queryTable = queryTable.leftJoin(tableClientSocStatus, db.joinAnd([tableClientSocStatus['client_id'].eq(tableClient['id']), tableClientSocStatus['deleted'].eq(0)]))
    queryTable = queryTable.leftJoin(tableSocStatusType, tableSocStatusType['id'].eq(tableClientSocStatus['socStatusType_id']))

    cond = ['isEventPayed(Event.id)']
    if not params.get('countUnfinished', False):
        addDateInRange(cond, tableEvent['execDate'], begDate, endDate)
    else:
        addDateInRange(cond, tableEvent['setDate'], begDate, endDate)
    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append('Event.setDate >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)'%ageFrom)
        cond.append('Event.setDate < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)'%(ageTo+1))
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    stmt = db.selectStmt(queryTable, cols, cond)
    return db.query(stmt)


class CReportResultsDD(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Сведения о результатах проведения диспансеризации взрослого населения')


    def getSetupDialog(self, parent):
        result = CReportDD2013WeeklySetupDialog(parent)
        result.setTitle(self.title())
        result.setPayStatusVisible(False)
        result.setTerTypeVisible(True)
        return result



    def build(self, params):
        def processRecordWithCond(processedList, processedAIList, baseRow, cond=None):

            if (cond is None or socStatus.startswith(cond)):
                if not eventId in processedList:
                    processedList.append(eventId)
                    paidEvents[baseRow] += 1
                    if sex:
                        paidEvents[baseRow+sex] += 1
                    if eventKind in ['01', u'04']:
                        if resultCode == '49':
                            eventsSS[baseRow] += 1
                            if sex:
                                eventsSS[baseRow+sex] += 1
                        else:
                            if hgCode == '1':
                                hg1Col[baseRow] += 1
                                if sex:
                                    hg1Col[baseRow+sex] += 1
                            elif hgCode in ['2', '3', '4', '5']:
                                hg2Col[baseRow] += 1
                                if sex:
                                    hg2Col[baseRow+sex] += 1
                            elif hgCode == '6':
                                hg3Col[baseRow] += 1
                                if sex:
                                    hg3Col[baseRow+sex] += 1
                        paidEventsFS[baseRow] += 1
                        if sex:
                            paidEventsFS[baseRow+sex] += 1
                    elif eventKind == '02':
                        paidEventsSS[baseRow] += 1
                        if sex:
                            paidEventsSS[baseRow+sex] += 1
                        if hgCode == '1':
                            hg1Col[baseRow] += 1
                            if sex:
                                hg1Col[baseRow+sex] += 1
                        elif hgCode in ['2', '3', '4', '5']:
                            hg2Col[baseRow] += 1
                            if sex:
                                hg2Col[baseRow+sex] += 1
                        elif hgCode == '6':
                            hg3Col[baseRow] += 1
                            if sex:
                                hg3Col[baseRow+sex] += 1

                if not accountItemId in processedAIList:
                    if eventKind in ['01', '04']:
                        paidEventsFSSum[baseRow] += sum
                        if sex:
                            paidEventsFSSum[baseRow+sex] += sum
                    elif eventKind == '02':
                        paidEventsSSSum[baseRow] += sum
                        if sex:
                            paidEventsSSSum[baseRow+sex] += sum
                    processedAIList.append(accountItemId)

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


        clientsCol = [0.0] * 12
        paidEvents = [0.0] * 12         # Всего предъявленных к оплате реестров счетов
        paidEventsFS = [0.0] * 12       # из них случаев в рамках первого этапа
        paidEventsFSSum = [0.0] * 12    # сумма оплаты
        paidEventsSS = [0.0] * 12       # из них случаев в рамках второго этапа
        paidEventsSSSum = [0.0] * 12    # сумма оплаты
        eventsSS = [0.0] * 12           # всего направленных на второй этап
        hg1Col = [0.0] * 12
        hg2Col = [0.0] * 12
        hg3Col = [0.0] * 12

        query = selectClientsData(params)
        if query.first():
            record = query.record()
            clientsCol[0] = forceInt(record.value('totalClients'))
            clientsCol[1] = forceDouble(record.value('totalMen'))
            clientsCol[2] = forceDouble(record.value('totalWomen'))
            clientsCol[3] = forceDouble(record.value('totalWorking'))
            clientsCol[4] = forceDouble(record.value('menWorking'))
            clientsCol[5] = forceDouble(record.value('womenWorking'))
            clientsCol[6] = forceDouble(record.value('totalUnemployed'))
            clientsCol[7] = forceDouble(record.value('menUnemployed'))
            clientsCol[8] = forceDouble(record.value('womenUunemployed'))
            clientsCol[9] = forceDouble(record.value('totalStudents'))
            clientsCol[10] = forceDouble(record.value('menStudents'))
            clientsCol[11] = forceDouble(record.value('womenStudents'))

        processedEvents = []
        processedEventsAI = []
        processedEmployed = []
        processedEmployedAI = []
        processedUnemployed = []
        processedUnemployedAI = []
        processedStudents = []
        processedStudentsAI = []

        query = selectEventsData(params)
        while query.next():

            record = query.record()
            eventId = forceRef(record.value('event_id'))
            eventKind = forceString(record.value('eventKindCode'))
            accountItemId = forceRef(record.value('accountItem_id'))
            sum = forceDouble(record.value('sum'))
            sex = forceInt(record.value('sex'))
            resultCode = forceString(record.value('resultCode'))
            hgCode = forceString(record.value('HGCode'))
            socStatus = forceString(record.value('socStatusName')).lower()

            processRecordWithCond(processedEvents, processedEventsAI, 0)
            processRecordWithCond(processedEmployed, processedEmployedAI, 3, u'работающ')
            processRecordWithCond(processedUnemployed, processedUnemployedAI, 6, u'неработающ')
            processRecordWithCond(processedStudents, processedStudentsAI, 9, u'студент')



        rowCount = 12

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
            ( '10%', [u'Группы', u'', u'', u'1'], CReportBase.AlignLeft),
            ( '3%', [u'№ стр.', u'', u'', u'2'], CReportBase.AlignCenter),
            ( '5%', [u'Количество медицинских организаций, проводящих диспансеризацию в отчетном периоде', u'', u'', u'3'], CReportBase.AlignCenter),
            ( '5%', [u'Численность застрахованных лиц, прикрепленных к медицинским организациям, оказывающим первичную медико-санитарную помощь на отчетную дату, человек', u'', u'', u'4'], CReportBase.AlignCenter),
            ( '5%', [u'в том числе:', u'подлежащие диспансеризации в отчетном году, согласно утвержденному плану-графику, всего человек', u'', u'5'], CReportBase.AlignCenter),
            ( '5%', [u'', u'из них:', u'на отчетный период, человек', u'6'], CReportBase.AlignCenter),
            ( '5%', [u'Всего предъявленных к оплате реестров счетов в рамках диспансеризации на отчетную дату, тыс. рублей', u'', u'', u'7'], CReportBase.AlignCenter),
            ( '4%', [u'в том числе:', u'в рамках I этапа диспансеризации', u'кол-во случаев', u'8'], CReportBase.AlignCenter),
            ( '4%', [u'', u'', u'тыс. рублей', u'9'], CReportBase.AlignCenter),
            ( '4%', [u'', u'в рамках II этапа диспансеризации', u'кол-во случаев', u'10'], CReportBase.AlignCenter),
            ( '4%', [u'', u'', u'тыс. рублей', u'11'], CReportBase.AlignCenter),
            ( '5%', [u'Всего оплачено реестров счетов в рамках диспансеризации за отчетный период, тыс. рублей', u'', u'', u'12'], CReportBase.AlignCenter),
            ( '5%', [u'в том числе:', u'в рамках I этапа', u'кол-во случаев', u'13'], CReportBase.AlignCenter),
            ( '5%', [u'', u'', u'тыс. рублей', u'14'], CReportBase.AlignCenter),
            ( '5%', [u'', u'в рамках II этапа', u'кол-во случаев', u'15'], CReportBase.AlignCenter),
            ( '5%', [u'', u'', u'тыс. рублей', u'16'], CReportBase.AlignCenter),
            ( '6%', [u'Количество граждан, направенных на II этап диспансеризации по результатам I этапа диспансеризации, человек', u'', u'', u'17'], CReportBase.AlignCenter),
            ( '5%', [u'Группы состояния здоровья застрахованны лиц, прошедших диспансеризацию', u'I группа здоровья, человек', u'', u'18'], CReportBase.AlignCenter),
            ( '5%', [u'', u'II группа здоровья, человек', u'', u'19'], CReportBase.AlignCenter),
            ( '5%', [u'', u'III группа здоровья, человек', u'', u'20'], CReportBase.AlignCenter)
        ]

        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 3, 1)
        table.mergeCells(0, 2, 3, 1)
        table.mergeCells(0, 3, 3, 1)
        table.mergeCells(0, 4, 1, 2)
        table.mergeCells(1, 4, 2, 1)
        table.mergeCells(0, 6, 3, 1)
        table.mergeCells(0, 7, 1, 4)
        table.mergeCells(1, 7, 1, 2)
        table.mergeCells(1, 9, 1, 2)
        table.mergeCells(0, 11, 3, 1)
        table.mergeCells(0, 12, 1, 4)
        table.mergeCells(1, 12, 1, 2)
        table.mergeCells(1, 14, 1, 2)
        table.mergeCells(0, 16, 3, 1)
        table.mergeCells(0, 17, 1, 3)
        table.mergeCells(1, 17, 2, 1)
        table.mergeCells(1, 18, 2, 1)
        table.mergeCells(1, 19, 2, 1)


        for k in range(rowCount):
            i = table.addRow()
            table.setText(i, 0, groups[k])
            table.setText(i, 1, k+1)
            table.setText(i, 2, 'X')
            table.setText(i, 3, '%d' % clientsCol[k])
            table.setText(i, 6, '%d' % paidEvents[k])
            table.setText(i, 7, '%d' % paidEventsFS[k])
            table.setText(i, 8, paidEventsFSSum[k])
            table.setText(i, 9, '%d' % paidEventsSS[k])
            table.setText(i, 10, paidEventsSSSum[k])
            table.setText(i, 16, '%d' % eventsSS[k])
            table.setText(i, 17, '%d' % hg1Col[k])
            table.setText(i, 18, '%d' % hg2Col[k])
            table.setText(i, 19, '%d' % hg3Col[k])

        return doc
