# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.database               import addDateInRange
from library.Utils                  import forceInt, forceRef, forceString, getVal
from Orgs.Utils                     import getOrganisationInfo
from Reports.Report                 import CReport
from Reports.ReportBase             import createTable, CReportBase
from Reports.StatReportDD2013Weekly import CReportDD2013WeeklySetupDialog

DDREPORT_2013 = 0
DDREPORT_2015 = 1
DDREPORT_2017 = 2
#TODO: если возникнет необходимость строить отчет более чем за год - пересмотреть систему подсчета возраста.

def selectData(params, version):
    sex = params.get('sex', 0)
    ageFrom = params.get('ageFrom', 0)
    ageTo = params.get('ageTo', 150)
    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)
    payStatusCode = params.get('payStatusCode', None)
    eventTypeId  = params.get('eventTypeId', None)

    manualPopulation = params.get('manualPopulation', False)
    fillPopulation = params.get('fillPopulation', False)
    if manualPopulation:
        if fillPopulation:
            updatePopulationInDatabase(2015, params.get('menPopulation'),
                                   params.get('womenPopulation'),
                                   params.get('menPopulationPlan'),
                                   params.get('womenPopulationPlan'))
    db = QtGui.qApp.db
    tableClient = db.table('Client')
    tableEvent = db.table('Event')
    tableEventType = db.table('EventType')
    tableEventKind = db.table('rbEventKind')
    tableEventProfile = db.table('rbEventProfile')
    tableMedicalAidType = db.table('rbMedicalAidType')

    year = forceInt(endDate.year()) if endDate else forceInt(QtCore.QDate.currentDate().year())

    eventCond = []
    if not params.get('countUnfinished', False):
        addDateInRange(eventCond, tableEvent['execDate'], begDate, endDate)
    else:
        addDateInRange(eventCond, tableEvent['setDate'], begDate, endDate)

    queryTable = tableClient.innerJoin(tableEvent, db.joinAnd([tableEvent['client_id'].eq(tableClient['id']), tableEvent['deleted'].eq(0)] + eventCond))
    queryTable = queryTable.innerJoin(tableEventType, db.joinAnd([tableEventType['id'].eq(tableEvent['eventType_id']), tableEventType['deleted'].eq(0)]))
    if version == DDREPORT_2017:
        queryTable = queryTable.innerJoin(tableEventProfile, db.joinAnd([tableEventProfile['id'].eq(tableEventType['eventProfile_id']), tableEventProfile['code'].inlist(['211'])]))
        queryTable = queryTable.innerJoin(tableMedicalAidType, db.joinAnd([tableMedicalAidType['id'].eq(tableEventType['medicalAidType_id']), tableMedicalAidType['regionalCode'].inlist(['211'])]))

    else:
        queryTable = queryTable.innerJoin(tableEventKind, db.joinAnd([tableEventKind['id'].eq(tableEventType['eventKind_id']), tableEventKind['code'].inlist(['01', '02', '04'])]))

    if payStatusCode is not None:
        tableContract = db.table('Contract')
        queryTable = queryTable.leftJoin(tableContract, tableContract['id'].eq(tableEvent['contract_id']))
        payStatusCond = 'getPayCode(%s, %s) = %d' % (tableContract['finance_id'],
                                                     tableEvent['payStatus'],
                                                     payStatusCode)
    else:
        payStatusCond = '1'

    
    terType = params.get('terType', 0)
    if manualPopulation:
        cols = []
    elif terType == 1:
        cols = ['COUNT(DISTINCT IF(kladr.STREET.CODE, Client.id, NULL)) as totalClients',
            'COUNT(DISTINCT IF(kladr.STREET.CODE AND Client.sex = 1, Client.id, NULL)) as totalMen',
            'COUNT(DISTINCT IF(kladr.STREET.CODE AND Client.sex = 2, Client.id, NULL)) as totalWomen'
            ]
    elif terType == 2:
        cols = ['COUNT(DISTINCT IF(ClientAttach.id, Client.id, NULL)) as totalClients',
            'COUNT(DISTINCT IF(ClientAttach.id AND Client.sex = 1, Client.id, NULL)) as totalMen',
            'COUNT(DISTINCT IF(ClientAttach.id AND Client.sex = 2, Client.id, NULL)) as totalWomen']
    else:
        cols = ['COUNT(DISTINCT Client.id) as totalClients',
                'COUNT(DISTINCT IF(Client.sex = 1, Client.id, NULL)) as totalMen',
                'COUNT(DISTINCT IF(Client.sex = 2, Client.id, NULL)) as totalWomen'
                ]

    if version == DDREPORT_2013:
        cols += ['COUNT(DISTINCT IF(Event.id AND %s, Client.id, NULL)) as processedClients' % payStatusCond,
                'COUNT(DISTINCT IF(Event.id AND Client.sex = 1 AND %s, Client.id, NULL)) as processedMen' % payStatusCond,
                'COUNT(DISTINCT IF(Event.id AND Client.sex = 2 AND %s, Client.id, NULL)) as processedWomen' % payStatusCond,
                '%d - year(Client.birthDate) as clientAge' % year]
    elif (version == DDREPORT_2015):
        cols += [u'COUNT(DISTINCT IF(Event.id AND rbEventKind.code in ("01", "04") AND %s, Client.id, NULL)) as processedClientsFS' % payStatusCond,
            u'COUNT(DISTINCT IF(Event.id AND rbEventKind.code in ("02") AND %s, Client.id, NULL)) as processedClientsSS' % payStatusCond,
            u'COUNT(DISTINCT IF(Event.id AND rbEventKind.code in ("01", "04") AND Client.sex = 1 AND %s, Client.id, NULL)) as processedMenFS' % payStatusCond,
            u'COUNT(DISTINCT IF(Event.id AND rbEventKind.code in ("02") AND Client.sex = 1 AND %s, Client.id, NULL)) as processedMenSS' % payStatusCond,
            u'COUNT(DISTINCT IF(Event.id AND rbEventKind.code in ("01", "04") AND Client.sex = 2 AND %s, Client.id, NULL)) as processedWomenFS' % payStatusCond,
            u'COUNT(DISTINCT IF(Event.id AND rbEventKind.code in ("02") AND Client.sex = 2 AND %s, Client.id, NULL)) as processedWomenSS' % payStatusCond,
            '%d - year(Client.birthDate) as clientAge' % year]
    elif (version == DDREPORT_2017):
        cols += [u'COUNT(DISTINCT IF(Event.id AND rbMedicalAidType.dispStage in ("01") AND %s, Client.id, NULL)) as processedClientsFS' % payStatusCond,
            u'COUNT(DISTINCT IF(Event.id AND rbMedicalAidType.dispStage in ("02") AND %s, Client.id, NULL)) as processedClientsSS' % payStatusCond,
            u'COUNT(DISTINCT IF(Event.id AND rbMedicalAidType.dispStage in ("01") AND Client.sex = 1 AND %s, Client.id, NULL)) as processedMenFS' % payStatusCond,
            u'COUNT(DISTINCT IF(Event.id AND rbMedicalAidType.dispStage in ("02") AND Client.sex = 1 AND %s, Client.id, NULL)) as processedMenSS' % payStatusCond,
            u'COUNT(DISTINCT IF(Event.id AND rbMedicalAidType.dispStage in ("01") AND Client.sex = 2 AND %s, Client.id, NULL)) as processedWomenFS' % payStatusCond,
            u'COUNT(DISTINCT IF(Event.id AND rbMedicalAidType.dispStage in ("02") AND Client.sex = 2 AND %s, Client.id, NULL)) as processedWomenSS' % payStatusCond,
            #u'age(Client.birthDate, Event.setDate) AS clientAge']
            u'%d - year(Client.birthDate) AS clientAge' % year]

    cond = [tableClient['deleted'].eq(0)]

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
        #cond.append(tableClientAddress['id'].isNotNull())
    elif terType == 2:
        tableClientAttach = db.table('ClientAttach')
        tableRBAttachType = db.table('rbAttachType')
        attachTypeId = forceRef(db.translate(tableRBAttachType, 'code', 1, 'id'))
        queryTable = queryTable.leftJoin(tableClientAttach, db.joinAnd([
            tableClientAttach['client_id'].eq(tableClient['id']),
            tableClientAttach['deleted'].eq(0),
            tableClientAttach['LPU_id'].eq(QtGui.qApp.currentOrgId()),
            tableClientAttach['attachType_id'].eq(attachTypeId)]))
        #cond.append(tableClientAttach['id'].isNotNull())
    # if manualPopulation:
    #     tablePopulationCount = db.table('PopulationCount')
    #     queryTable = queryTable.leftJoin(tablePopulationCount, ['PopulationCount.code = CAST(age(Client.birthDate, "%s-01-01") AS CHAR)' % year,
    #                                                             tablePopulationCount['sex'].eq(tableClient['sex']),
    #                                                             tablePopulationCount['measureYear'].eq(year - 1)])

    cond.append('%d - year(Client.birthDate) IN (%s)' % (year, ', '.join([str(i) for i in xrange(21, 100, 3)])))

    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append('%d - year(Client.birthDate) >= %d'%(year, ageFrom))
        cond.append('%d - year(Client.birthDate) < %d'%(year, ageTo+1))
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    
    
    stmt = db.selectStmt(queryTable, cols, cond, group='clientAge')
    return db.query(stmt)


def updatePopulationInDatabase(year, menPopulation, womenPopulation, menPopulationPlan, womenPopulationPlan):
    db = QtGui.qApp.db
    codes = ['21', '39', '63']
    values = ['"%s", %d, 1, %d, %d' % (code, year, pop, plan)
              for  pop, plan, code in zip(menPopulation, menPopulationPlan, codes)]
    values.extend(
        '"%s", %d, 2, %d, %d' % (code, year, pop, plan)
        for  pop, plan, code in zip(womenPopulation, womenPopulationPlan, codes)
    )
    valuesString = '(' + '), ('.join(values) + ')'
    query = """INSERT INTO PopulationCount (code, measureYear, sex, population, plan)
    VALUES %s
    ON DUPLICATE KEY UPDATE population=VALUES(population), plan=VALUES(plan)""" % valuesString
    db.query(query)


class CReportDDSexAgeStructure(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Половозрастной состав населения.')


    def getSetupDialog(self, parent):
        result = CReportDD2013WeeklySetupDialog(parent)
        result.setPlanVisible(True)
        result.setTerTypeVisible(True)
        result.setTitle(self.title())
        return result

    def build(self, params):
        rowSize = 6
        planTotal = params.get('planTotal', 0)
        totals = [0] * rowSize

        resultSet = {}
        for i in xrange(21, 100, 3):
            resultSet[i] = [0] * rowSize

        query = selectData(params, DDREPORT_2013)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            age = forceInt(record.value('clientAge'))
            total = forceInt(record.value('totalClients'))
            male = forceInt(record.value('totalMen'))
            female = forceInt(record.value('totalWomen'))
            processedTotal = forceInt(record.value('processedClients'))
            processedMale = forceInt(record.value('processedMen'))
            processedFemale = forceInt(record.value('processedWomen'))

            totals[0] += male
            totals[1] += processedMale
            totals[2] += female
            totals[3] += processedFemale
            totals[4] += total
            totals[5] += processedTotal

            row = resultSet[age]
            row[0] = male
            row[1] = processedMale
            row[2] = female
            row[3] = processedFemale
            row[4] = total
            row[5] = processedTotal

        planPercent = float(planTotal)/totals[4] if totals[4] else 0

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
            ( '5%', [u'Возраст (исполняется полных лет в текущем году)', u''], CReportBase.AlignCenter),
            ( '5%', [u'№ строки', u''], CReportBase.AlignCenter),
            ( '10%', [u'Мужчины', u'Всего проживает в субъекте Российской Федерации (на территории обслуживания медицинской организации)'], CReportBase.AlignRight),
            ( '10%', [u'', u'Включено в план проведения диспансеризации на текущий календарный год с учетом возрастной категории граждан'], CReportBase.AlignRight),
            ( '10%', [u'', u'Прошли диспансеризацию'], CReportBase.AlignRight),
            ( '10%', [u'Женщины', u'Всего проживает в субъекте Российской Федерации (на территории обслуживания медицинской организации)'], CReportBase.AlignRight),
            ( '10%', [u'', u'Включено в план проведения диспансеризации на текущий календарный год с учетом возрастной категории граждан'], CReportBase.AlignRight),
            ( '10%', [u'', u'Прошли диспансеризацию'], CReportBase.AlignRight),
            ( '10%', [u'Всего', u'Всего проживает в субъекте Российской Федерации (на территории обслуживания медицинской организации)'], CReportBase.AlignRight),
            ( '10%', [u'', u'Включено в план проведения диспансеризации на текущий календарный год с учетом возрастной категории граждан'], CReportBase.AlignRight),
            ( '10%', [u'', u'Прошли диспансеризацию'], CReportBase.AlignRight)
        ]

        rowSize = 11
        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 1, 3)
        table.mergeCells(0, 5, 1, 3)
        table.mergeCells(0, 8, 1, 3)

        i = table.addRow()

        for j in xrange(rowSize):
            table.setText(i, j, j+1, blockFormat = bf)

        totalRow3 = 0
        totalRow6 = 0
        totalRow9 = 0

        tmpdateMale = []
        tmpdateFemale = []

        for number, age in enumerate(xrange(21, 100, 3)):
            row = resultSet[age]
            tmpdateMale.append(int(row[0]*planPercent))
            tmpdateFemale.append(int(row[2]*planPercent))
            totalRow3 += tmpdateMale[number]
            totalRow6 += tmpdateFemale[number]

        totalRow9 += totalRow6 + totalRow3

        for number, age in enumerate(xrange(21, 100, 3)):
            row = resultSet[age]
            if totalRow9 != planTotal:
                totalRow9 += 1
                if number % 2 == 0:
                    tmpdateMale[number] += 1
                    totalRow3 += 1
                else:
                    tmpdateFemale[number] += 1
                    totalRow6 += 1
            i = table.addRow()
            table.setText(i, 0, age)
            table.setText(i, 1, number+1)
            table.setText(i, 2, row[0])
            table.setText(i, 3, tmpdateMale[number])
            table.setText(i, 4, row[1])
            table.setText(i, 5, row[2])
            table.setText(i, 6, tmpdateFemale[number])
            table.setText(i, 7, row[3])
            table.setText(i, 8, row[4])
            table.setText(i, 9, tmpdateMale[number] + tmpdateFemale[number])
            table.setText(i, 10, row[5])

        i = table.addRow()
        table.setText(i, 0, u'ИТОГО')
        table.setText(i, 1, u'')
        table.setText(i, 2, totals[0])
#        table.setText(i, 3, int(totals[0]*planPercent))
        table.setText(i, 3, totalRow3)
        table.setText(i, 4, totals[1])
        table.setText(i, 5, totals[2])
#        table.setText(i, 6, int(totals[2]*planPercent))
        table.setText(i, 6, totalRow6)
        table.setText(i, 7, totals[3])
        table.setText(i, 8, totals[4])
#        table.setText(i, 9, int(totals[4]*planPercent))
        table.setText(i, 9, totalRow9)
        table.setText(i, 10, totals[5])

        return doc


class CReportDDSexAgeStructure2015(CReport):

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Сведения о проведении диспансеризации определенных групп взрослого населения')
        self.prepareRows()

    def prepareRows(self):
        def createRow(header, index):
            rowSize = 12
            return [header, index] + [0] * rowSize
        self.junior_row = createRow(u'21-36 лет', '01')
        self.middle_row = createRow(u'39-60 лет', '02')
        self.senior_row = createRow(u'Старше 60 лет', '03')
        self.total_row = createRow(u'Итого', '04')

    def getSetupDialog(self, parent):
        result = CReportDD2013WeeklySetupDialog(parent)
        result.setPlanVisible(True)
        result.setTerTypeVisible(True)
        result.setTitle(self.title())
        result.setEventTypeVisible(False)
        return result

    def getRowByAge(self, age):
        if 21 <= age <= 36:
            return self.junior_row
        elif 39 <= age <= 60:
            return self.middle_row
        elif age > 60:
            return self.senior_row
        return None

    def build(self, params):
        self.prepareRows()
        planTotal = params.get('planTotal', 0)

        totals = self.total_row
        query = selectData(params, DDREPORT_2015)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            age = forceInt(record.value('clientAge'))
            total = forceInt(record.value('totalClients'))
            male = forceInt(record.value('totalMen'))
            female = forceInt(record.value('totalWomen'))
            processedTotalFS = forceInt(record.value('processedClientsFS'))
            processedTotalSS = forceInt(record.value('processedClientsSS'))
            processedMaleFS = forceInt(record.value('processedMenFS'))
            processedMaleSS = forceInt(record.value('processedMenSS'))
            processedFemaleFS = forceInt(record.value('processedWomenFS'))
            processedFemaleSS = forceInt(record.value('processedWomenSS'))

            totals[2] += total
            totals[4] += processedTotalFS
            totals[5] += processedTotalSS
            totals[6] += male
            totals[8] += processedMaleFS
            totals[9] += processedMaleSS
            totals[10] += female
            totals[12] += processedFemaleFS
            totals[13] += processedFemaleSS

            row = self.getRowByAge(age)
            row[2] += total
            row[4] += processedTotalFS
            row[5] += processedTotalSS
            row[6] += male
            row[8] += processedMaleFS
            row[9] += processedMaleSS
            row[10] += female
            row[12] += processedFemaleFS
            row[13] += processedFemaleSS

        planPercent = float(planTotal)/totals[2] if totals[2] else 0

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
            ( '5%', [u'Возрастная группа', u'', u'', u'1'], CReportBase.AlignLeft),
            ( '5%', [u'№ строки', u'', u'', u'2'], CReportBase.AlignCenter),
            ( '10%', [u'Все население', u'Численность населения на 01.01 текущего года', u'', u'3'], CReportBase.AlignRight),
            ( '10%', [u'', u'Подлежит диспансеризации по плану текущего года', u'', u'4'], CReportBase.AlignRight),
            ( '5%', [u'', u'Прошли диспансеризацию', u'I этап', u'5'], CReportBase.AlignRight),
            ( '5%', [u'', u'', u'II этап', u'6'], CReportBase.AlignRight),
            ( '10%', [u'Мужчины', u'Численность населения на 01.01 текущего года', u'', u'7'], CReportBase.AlignRight),
            ( '10%', [u'', u'Подлежит диспансеризации по плану текущего года', u'', u'8'], CReportBase.AlignRight),
            ( '5%', [u'', u'Прошли диспансеризацию', u'I этап', u'9'], CReportBase.AlignRight),
            ( '5%', [u'', u'', u'II этап', u'10'], CReportBase.AlignRight),
            ( '10%', [u'Женщины', u'Численность населения на 01.01 текущего года', u'', u'11'], CReportBase.AlignRight),
            ( '10%', [u'', u'Подлежит диспансеризации по плану текущего года', u'', u'12'], CReportBase.AlignRight),
            ( '5%', [u'', u'Прошли диспансеризацию', u'I этап', u'13'], CReportBase.AlignRight),
            ( '5%', [u'', u'', u'II этап', u'14'], CReportBase.AlignRight),
        ]

        rowSize = 11
        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 3, 1)
        table.mergeCells(0, 2, 1, 4)
        table.mergeCells(1, 2, 2, 1)
        table.mergeCells(1, 3, 2, 1)
        table.mergeCells(1, 4, 1, 2)
        table.mergeCells(0, 6, 1, 4)
        table.mergeCells(1, 6, 2, 1)
        table.mergeCells(1, 7, 2, 1)
        table.mergeCells(1, 8, 1, 2)
        table.mergeCells(0, 10, 1, 4)
        table.mergeCells(1, 10, 2, 1)
        table.mergeCells(1, 11, 2, 1)
        table.mergeCells(1, 12, 1, 2)

        totalPlan = 0
        totalMalePlan = 0
        totalFemalePlan = 0

        manualPopulation = params.get('manualPopulation', False)
        fillPopulation = params.get('fillPopulation', False)
        if manualPopulation:
            totalMale = 0
            totalFemale = 0
            if fillPopulation:
                menPopulationPlan = params.get('menPopulationPlan')
                menPopulation = params.get('menPopulation')
                womenPopulationPlan = params.get('womenPopulationPlan')
                womenPopulation = params.get('womenPopulation')
            else:
                db = QtGui.qApp.db
                tablePopulation = db.table('PopulationCount')
                records = db.getRecordList(tablePopulation,
                                           where=[tablePopulation['measureYear'].eq(2015)],
                                           order='sex, code')
                menPopulation, womenPopulation = [], []
                menPopulationPlan, womenPopulationPlan = [], []
                for record in records:
                    if forceInt(record.value('sex')) == 1:
                        menPopulationPlan.append(forceInt(record.value('plan')))
                        menPopulation.append(forceInt(record.value('population')))

                    else:
                        womenPopulationPlan.append(forceInt(record.value('plan')))
                        womenPopulation.append(forceInt(record.value('population')))
        else:
            planTotal = params.get('planTotal', 0)


        for i, row in enumerate([self.junior_row, self.middle_row, self.senior_row, self.total_row]):
            # Немного безумия, чтобы все цифры сходились
            if row is self.total_row:
                row[3] = planTotal # planPercent #raipc: так точно надо было?
                row[7] = totalMalePlan
                row[11] = totalFemalePlan
                if manualPopulation:
                    row[6] = totalMale
                    row[10] = totalFemale
                    row[2] = row[6] + row[10]
            elif manualPopulation:
                row[6] = menPopulation[i]
                row[7] = menPopulationPlan[i]
                row[10] = womenPopulation[i]
                row[11] = womenPopulationPlan[i]
                row[3] = row[7] + row[11]
                row[2] = row[6] + row[10]
                totalMale += row[6]
                totalMalePlan += row[7]
                totalFemale += row[10]
                totalFemalePlan += row[11]
                planTotal += row[3]
            else:
                row[7] = int(planPercent * row[6] + 0.5)
                row[11] = int(planPercent * row[10] + 0.5)
                row[3] = row[7] + row[11]
                totalPlan += row[3]
                totalMalePlan += row[7]
                totalFemalePlan += row[11]

            i = table.addRow()
            for j, value in enumerate(row):
                table.setText(i, j, value)
        return doc


class CReportDDSexAgeStructure2017(CReport):

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Сведения о проведении диспансеризации определенных групп взрослого населения')
        self.prepareRows()

    def prepareRows(self):
        def createRow(header, index):
            rowSize = 12
            return [header, index] + [0] * rowSize
        self.junior_row = createRow(u'21-36 лет', '01')
        self.middle_row = createRow(u'39-60 лет', '02')
        self.senior_row = createRow(u'Старше 60 лет', '03')
        self.total_row = createRow(u'Итого', '04')

    def getSetupDialog(self, parent):
        result = CReportDD2013WeeklySetupDialog(parent)
        result.setPlanVisible(True)
        result.setTerTypeVisible(True)
        result.setTitle(self.title())
        result.setEventTypeVisible(False)
        return result

    def getRowByAge(self, age):
        if 21 <= age <= 36:
            return self.junior_row
        elif 39 <= age <= 60:
            return self.middle_row
        elif age > 60:
            return self.senior_row
        return None

    def build(self, params):
        self.prepareRows()
        planTotal = params.get('planTotal', 0)

        totals = self.total_row
        query = selectData(params, DDREPORT_2017)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            age = forceInt(record.value('clientAge'))
            total = forceInt(record.value('totalClients'))
            male = forceInt(record.value('totalMen'))
            female = forceInt(record.value('totalWomen'))
            processedTotalFS = forceInt(record.value('processedClientsFS'))
            processedTotalSS = forceInt(record.value('processedClientsSS'))
            processedMaleFS = forceInt(record.value('processedMenFS'))
            processedMaleSS = forceInt(record.value('processedMenSS'))
            processedFemaleFS = forceInt(record.value('processedWomenFS'))
            processedFemaleSS = forceInt(record.value('processedWomenSS'))

            totals[2] += total
            totals[4] += processedTotalFS
            totals[5] += processedTotalSS
            totals[6] += male
            totals[8] += processedMaleFS
            totals[9] += processedMaleSS
            totals[10] += female
            totals[12] += processedFemaleFS
            totals[13] += processedFemaleSS

            row = self.getRowByAge(age)
            if row is not None:
                row[2] += total
                row[4] += processedTotalFS
                row[5] += processedTotalSS
                row[6] += male
                row[8] += processedMaleFS
                row[9] += processedMaleSS
                row[10] += female
                row[12] += processedFemaleFS
                row[13] += processedFemaleSS

        planPercent = float(planTotal)/totals[2] if totals[2] else 0

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
            ( '5%', [u'Возрастная группа', u'', u'', u'1'], CReportBase.AlignLeft),
            ( '5%', [u'№ строки', u'', u'', u'2'], CReportBase.AlignCenter),
            ( '10%', [u'Все население', u'Численность населения на 01.01 текущего года', u'', u'3'], CReportBase.AlignRight),
            ( '10%', [u'', u'Подлежит диспансеризации по плану текущего года', u'', u'4'], CReportBase.AlignRight),
            ( '5%', [u'', u'Прошли диспансеризацию', u'I этап', u'5'], CReportBase.AlignRight),
            ( '5%', [u'', u'', u'II этап', u'6'], CReportBase.AlignRight),
            ( '10%', [u'Мужчины', u'Численность населения на 01.01 текущего года', u'', u'7'], CReportBase.AlignRight),
            ( '10%', [u'', u'Подлежит диспансеризации по плану текущего года', u'', u'8'], CReportBase.AlignRight),
            ( '5%', [u'', u'Прошли диспансеризацию', u'I этап', u'9'], CReportBase.AlignRight),
            ( '5%', [u'', u'', u'II этап', u'10'], CReportBase.AlignRight),
            ( '10%', [u'Женщины', u'Численность населения на 01.01 текущего года', u'', u'11'], CReportBase.AlignRight),
            ( '10%', [u'', u'Подлежит диспансеризации по плану текущего года', u'', u'12'], CReportBase.AlignRight),
            ( '5%', [u'', u'Прошли диспансеризацию', u'I этап', u'13'], CReportBase.AlignRight),
            ( '5%', [u'', u'', u'II этап', u'14'], CReportBase.AlignRight),
        ]

        cursor.movePosition(cursor.End)
        cursor.insertText(u'1000')
        rowSize = 11
        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 3, 1)
        table.mergeCells(0, 2, 1, 4)
        table.mergeCells(1, 2, 2, 1)
        table.mergeCells(1, 3, 2, 1)
        table.mergeCells(1, 4, 1, 2)
        table.mergeCells(0, 6, 1, 4)
        table.mergeCells(1, 6, 2, 1)
        table.mergeCells(1, 7, 2, 1)
        table.mergeCells(1, 8, 1, 2)
        table.mergeCells(0, 10, 1, 4)
        table.mergeCells(1, 10, 2, 1)
        table.mergeCells(1, 11, 2, 1)
        table.mergeCells(1, 12, 1, 2)

        totalPlan = 0
        totalMalePlan = 0
        totalFemalePlan = 0

        manualPopulation = params.get('manualPopulation', False)
        fillPopulation = params.get('fillPopulation', False)
        if manualPopulation:
            totalMale = 0
            totalFemale = 0
            if fillPopulation:
                menPopulationPlan = params.get('menPopulationPlan')
                menPopulation = params.get('menPopulation')
                womenPopulationPlan = params.get('womenPopulationPlan')
                womenPopulation = params.get('womenPopulation')
            else:
                db = QtGui.qApp.db
                tablePopulation = db.table('PopulationCount')
                records = db.getRecordList(tablePopulation,
                                           where=[tablePopulation['measureYear'].eq(2017)],
                                           order='sex, code')
                menPopulation, womenPopulation = [], []
                menPopulationPlan, womenPopulationPlan = [], []
                for record in records:
                    if forceInt(record.value('sex')) == 1:
                        menPopulationPlan.append(forceInt(record.value('plan')))
                        menPopulation.append(forceInt(record.value('population')))

                    else:
                        womenPopulationPlan.append(forceInt(record.value('plan')))
                        womenPopulation.append(forceInt(record.value('population')))
        else:
            planTotal = params.get('planTotal', 0)


        for i, row in enumerate([self.junior_row, self.middle_row, self.senior_row, self.total_row]):
            # Немного безумия, чтобы все цифры сходились
            if row is self.total_row:
                row[3] = planTotal # planPercent #raipc: так точно надо было?
                row[7] = totalMalePlan
                row[11] = totalFemalePlan
                if manualPopulation:
                    row[6] = totalMale
                    row[10] = totalFemale
                    row[2] = row[6] + row[10]
            elif manualPopulation:
                row[6] = menPopulation[i]
                row[7] = menPopulationPlan[i]
                row[10] = womenPopulation[i]
                row[11] = womenPopulationPlan[i]
                row[3] = row[7] + row[11]
                row[2] = row[6] + row[10]
                totalMale += row[6]
                totalMalePlan += row[7]
                totalFemale += row[10]
                totalFemalePlan += row[11]
                planTotal += row[3]
            else:
                row[7] = int(planPercent * row[6] + 0.5)
                row[11] = int(planPercent * row[10] + 0.5)
                row[3] = row[7] + row[11]
                totalPlan += row[3]
                totalMalePlan += row[7]
                totalFemalePlan += row[11]

            i = table.addRow()
            row[2] = ""
            row[6] = ""
            row[10] = ""
            for j, value in enumerate(row):
                table.setText(i, j, value)
        return doc
