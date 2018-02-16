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


def getSubClasses(classes):
    if len(classes)>0:
        return QtGui.qApp.db.getIdList('rbSocStatusClass', where = 'group_id IN (%s)' % (', '.join(str(v) for v in classes)))
    else:
        return []

DDREPORT_2013 = 0
DDREPORT_2015 = 1
DDREPORT_2017 = 2

def selectData(params, mode, version=DDREPORT_2013, resultCodes=[]):
    sex = params.get('sex', 0)
    ageFrom = params.get('ageFrom', 0)
    ageTo = params.get('ageTo', 150)
    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)
    payStatusCode = params.get('payStatusCode', None)
    eventTypeId  = params.get('eventTypeId', None)

    db = QtGui.qApp.db
    tableClient = db.table('Client')
    tableEvent = db.table('Event')
    tableEventType = db.table('EventType')
    tableEventKind = db.table('rbEventKind')
    tableResult = db.table('rbResult')
    tableDiagnostic = db.table('Diagnostic')
    tableDiagnosticResult = db.table('rbDiagnosticResult')
    tableClientSocStatus = db.table('ClientSocStatus')
    tableSocStatusClass = db.table('rbSocStatusClass')
    tableSocStatusType = db.table('rbSocStatusType')
    tableAction = db.table('Action')
    tableClientAddress = db.table('ClientAddress')
    tableAddress = db.table('Address')
    tableAddressHouse = db.table('AddressHouse')
    tableKladr = db.table('kladr.KLADR')
    tableScene = db.table('rbScene')
    tableVisit = db.table('Visit')
    tableEventProfile = db.table('rbEventProfile')
    tableMedicalAidType = db.table('rbMedicalAidType')
    tableReferral = db.table('Referral')
    tableRbReferralType = db.table('rbReferralType')


    year = forceInt(endDate.year()) if endDate else forceInt(QtCore.QDate.currentDate().year())

    eventKindCodeList = ['01', '02', '04']
    queryTable = tableClient.innerJoin(tableEvent, db.joinAnd([tableEvent['client_id'].eq(tableClient['id']), tableEvent['deleted'].eq(0), tableClient['deleted'].eq(0)]))
    queryTable = queryTable.innerJoin(tableEventType, db.joinAnd([tableEvent['eventType_id'].eq(tableEventType['id']), tableEventType['deleted'].eq(0)]))
    queryTable = queryTable.innerJoin(tableMedicalAidType, db.joinAnd([tableMedicalAidType['id'].eq(tableEventType['medicalAidType_id']), tableMedicalAidType['regionalCode'].inlist(['211'])]))
    queryTable = queryTable.leftJoin(tableReferral, db.joinAnd([tableEvent['id'].eq(tableReferral['event_id']), tableReferral['deleted'].eq(0)]))
    queryTable = queryTable.leftJoin(tableRbReferralType, db.joinAnd([tableRbReferralType['netrica_Code'].eq(tableReferral['type'])]))

    if version == DDREPORT_2017:
        queryTable = queryTable.innerJoin(tableEventProfile, db.joinAnd([tableEventProfile['id'].eq(tableEventType['eventProfile_id']), tableEventProfile['code'].inlist(['211'])]))
    else:
        #queryTable = queryTable.leftJoin(tableEventKind, db.joinAnd([tableEventKind['id'].eq(tableEventType['eventKind_id']), tableEventKind['code'].inlist(['01', '02', '04'])]))
        queryTable = queryTable.innerJoin(tableEventKind, db.joinAnd([tableEventType['eventKind_id'].eq(tableEventKind['id']), tableEventKind['code'].inlist(eventKindCodeList)]))

    if mode == 0:
        queryTable = queryTable.innerJoin(tableResult, db.joinAnd([tableResult['id'].eq(tableEvent['result_id']), tableEvent['result_id'].isNotNull()]))
    elif mode == 1:
        queryTable = queryTable.innerJoin(tableDiagnostic, db.joinAnd([tableDiagnostic['event_id'].eq(tableEvent['id']), tableDiagnostic['deleted'].eq(0)]))
        queryTable = queryTable.innerJoin(tableDiagnosticResult, tableDiagnosticResult['id'].eq(tableDiagnostic['result_id']))
    elif mode == 2:
        queryTable = queryTable.leftJoin(tableResult, db.joinAnd([tableResult['id'].eq(tableEvent['result_id']), tableEvent['result_id'].isNotNull()]))
        queryTable = queryTable.leftJoin(tableClientSocStatus, db.joinAnd([tableClientSocStatus['client_id'].eq(tableClient['id']), tableClientSocStatus['deleted'].eq(0)]))
        queryTable = queryTable.leftJoin(tableSocStatusClass, tableSocStatusClass['id'].eq(tableClientSocStatus['socStatusClass_id']))
        queryTable = queryTable.leftJoin(tableSocStatusType, tableSocStatusType['id'].eq(tableClientSocStatus['socStatusType_id']))
        queryTable = queryTable.leftJoin(tableAction, tableAction['event_id'].eq(tableEvent['id']))
        queryTable = queryTable.leftJoin(tableClientAddress, [tableClient['id'].eq(tableClientAddress['client_id'])])
        queryTable = queryTable.leftJoin(tableAddress, [tableAddress['id'].eq(tableClientAddress['address_id'])])
        queryTable = queryTable.leftJoin(tableAddressHouse, [tableAddressHouse['id'].eq(tableAddress['house_id'])])
        queryTable = queryTable.leftJoin(tableKladr, [tableAddressHouse['KLADRCode'].eq(tableKladr['CODE'])])
        queryTable = queryTable.leftJoin(tableVisit, [tableVisit['deleted'].eq(0), tableVisit['event_id'].eq(tableEvent['id'])])
        queryTable = queryTable.leftJoin(tableScene, [tableVisit['scene_id'].eq(tableScene['id'])])

    elif mode == 3:
        selectStmt = u'''
            SELECT COUNT(DISTINCT IF(E2.execDate IS NULL, Client.id, NULL)
            FROM Client
            INNER JOIN EventType ON Event.eventType_id = EventType.id AND Client.deleted = 0 AND EventType.deleted = 0%s
            INNER JOIN rbEventKind REK ON EventType.eventKind_id = REK.id AND REK.code IN ('01', '04')
            INNER JOIN Event ON Event.eventType_id = EventType.id AND Event.deleted = 0
            LEFT JOIN (Event AS E2 ON E2.client_id = Client.id AND E2.deleted = 0
            LEFT JOIN EventType AS ET2 ON E2.eventType_id = ET2.id AND ET2.deleted = 0
            LEFT JOIN rbEventKind REK2 ON ET2.eventKind_id = REK2.id AND REK2.code = '02'
            WHERE %s
            '''

    if mode <= 1:
        if version == DDREPORT_2015 or version == DDREPORT_2017:
            cols = [
                'COUNT(DISTINCT Client.id) AS count',
                'Client.id as clientId',
                '%d - year(Client.birthDate) as clientAge' % year,
                tableClient['sex'].alias('clientSex'),
                tableResult['name'] if mode == 0 else tableDiagnosticResult['name'],
                tableResult['code'].alias('resultCode') if mode == 0 else tableDiagnosticResult['code'].alias('resultCode'),
                tableRbReferralType['netrica_Code'].alias('netrica_Code') if mode == 0 else tableDiagnosticResult['code'].alias('resultCode')
            ]
        else:
            cols = [
                'COUNT(DISTINCT Client.id) AS count',
                'age(Client.birthDate, Event.setDate) as client_age',
                tableClient['sex'],
                tableResult['name'] if mode == 0 else tableDiagnosticResult['name'],
                tableResult['id'].alias('res_id') if mode == 0 else tableDiagnosticResult['id'].alias('res_id')
            ]
        group = [
            tableClient['sex'],
            'age(Client.birthDate, Event.setDate)',
            'rbMedicalAidType.dispStage',
            'rbreferraltype.netrica_Code',
            tableResult['id'] if mode == 0 else tableDiagnosticResult['id']
        ]
    elif mode == 2:
        record = db.getRecordEx(tableSocStatusClass, 'id', tableSocStatusClass['flatCode'].eq('benefits'))
        classes = [forceRef(record.value('id'))] if record else []
        newClasses = getSubClasses(classes)
        classes += newClasses
        while newClasses:
            newClasses = getSubClasses(newClasses)
            classes += newClasses

        classes = ','.join(str(class_) for class_ in classes) if classes else '0'

        resultCond = tableResult['code'].inlist(resultCodes)
        socStatusCond = {
            'working':          tableSocStatusType['code'].inlist([u'с05', u'с08']),
            'notWorking':       tableSocStatusType['code'].inlist([u'с06', u'с07']),
            'student':          tableSocStatusType['code'].eq(u'с04'),
            'disabled':         tableSocStatusType['code'].eq(u'010'),
            'warVeteran':       tableSocStatusType['code'].eq(u'020'),
            'siegeOfLeningrad': tableSocStatusType['code'].eq(u'050')
        }

        # u'COUNT(DISTINCT IF ((clientWork.org_id or clientWork.freeInput), Client.id, null)) as countWorking'
        # u'COUNT(DISTINCT IF ((clientWork.org_id or clientWork.freeInput), null, Client.id)) as countNotWorking'
        cols = [
            u'COUNT(DISTINCT IF(ClientSocStatus.socStatusClass_id IN ({classes}) AND {resultCond}, Client.id, NULL)) as countDiscount'.format(classes=classes, resultCond=resultCond),
            u'COUNT(DISTINCT IF({workingCond} AND {resultCond}, Client.id, NULL)) as countWorking'.format(
                workingCond=socStatusCond['working'], resultCond=resultCond),
            u'COUNT(DISTINCT IF({notWorkingCond} AND {resultCond}, Client.id, NULL)) as countNotWorking'.format(
                notWorkingCond=socStatusCond['notWorking'], resultCond=resultCond),
            u'COUNT(DISTINCT IF(Action.status = 3, Action.id, NULL)) as countDeclinedActions',
            u'COUNT(DISTINCT IF(Action.status = 3, Event.id, NULL)) as countDeclinedEvents',
            u'COUNT(DISTINCT Action.org_id) as countOrgs'
        ]

        if version == DDREPORT_2017:
           cols.extend([
                u'COUNT(DISTINCT IF(rbMedicalAidType.dispStage in ("01"), Event.id, NULL)) AS countFirstStep',
                u'COUNT(DISTINCT IF(rbMedicalAidType.dispStage in ("02"), Event.id, NULL)) AS countSecondStep',
                u'COUNT(DISTINCT IF((rbSocStatusClass.name LIKE ("%социальный статус%") and '
                u'rbSocStatusType.netrica_Code = "2.3"), Event.id, NULL)) AS students',
                u'COUNT(DISTINCT IF(rbSocStatusClass.name LIKE ("%Льгота%") and '
                u'rbSocStatusType.netrica_Code IN ("10", "11", "20", "50"), Event.id, NULL)) AS beneficiaries',
                u'COUNT(DISTINCT IF(rbSocStatusClass.name LIKE ("%Льгота%") and '
                u'rbSocStatusType.netrica_Code IN ("10", "11"), Event.id, NULL)) AS beneficiaries10_11',
                u'COUNT(DISTINCT IF(rbSocStatusClass.name LIKE ("%Льгота%") and '
                u'rbSocStatusType.netrica_Code IN ("20"), Event.id, NULL)) AS beneficiaries_20',
                u'COUNT(DISTINCT IF(rbSocStatusClass.name LIKE ("%Льгота%") and '
                u'rbSocStatusType.netrica_Code IN ("50"), Event.id, NULL)) AS beneficiaries_50',
                u'COUNT(DISTINCT IF(EventType.dispByMobileTeam=1, Event.id, NULL)) AS dispByMobileTeam'
           ])

        else:
            cols.extend([
                u'COUNT(DISTINCT IF(rbEventKind.code = "01", Event.id, NULL)) AS countFirstStep',
                u'COUNT(DISTINCT IF(rbEventKind.code = "02", Event.id, NULL)) AS countSecondStep'])

        if version == DDREPORT_2015 or version == DDREPORT_2017:
            cols.extend([
                u'COUNT(DISTINCT IF({disabledCond} AND {resultCond}, Client.id, NULL)) as countDisabled'.format(disabledCond=socStatusCond['disabled'], resultCond=resultCond),
                u'COUNT(DISTINCT IF({veteranCond} AND {resultCond}, Client.id, NULL)) as countWarVeterans'.format(veteranCond=socStatusCond['warVeteran'], resultCond=resultCond),
                u'COUNT(DISTINCT IF({siegeOfLCond} AND {resultCond}, Client.id, NULL)) as countBesiegedLeningrad'.format(siegeOfLCond=socStatusCond['siegeOfLeningrad'], resultCond=resultCond),
                u'COUNT(DISTINCT IF(rbScene.code = "4", Client.id, NULL)) AS countMobilePatients',
                u'COUNT(DISTINCT IF(rbScene.code = "4", Visit.person_id, NULL)) AS countMobile',
                u'''COUNT(DISTINCT IF(address_id IS NULL, NULL,
                                    IF(Address.house_id IS NULL, NULL,
                                     IF(KLADR.SOCR != 'г', Client.id, NULL)
                    ))) AS countVillagers'''
            ])
        else:
            cols.extend([
                u'''COUNT(DISTINCT IF(address_id IS NULL, NULL,
                                    IF(Address.house_id IS NULL, NULL,
                                     IF(KLADR.SOCR NOT IN ('г', 'пгт'), Client.id, NULL)
                    ))) AS countVillagers''',
                u'COUNT(DISTINCT IF({studentCond} AND {resultCond}, Client.id, NULL)) as countStudents'.format(studentCond=socStatusCond['student'], resultCond=resultCond),
                u'COUNT(DISTINCT IF(isClientVillager(Client.id) AND {resultCond}, Client.id, NULL)) as countVillagers'.format(resultCond=resultCond),
            ])
        group = []

    cond = []

    if not params.get('countUnfinished', False):
        addDateInRange(cond, tableEvent['execDate'], begDate, endDate)
    else:
        addDateInRange(cond, tableEvent['setDate'], begDate, endDate)
    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append(u'Event.setDate >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)'%ageFrom)
        cond.append(u'Event.setDate < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)'%(ageTo+1))

    if payStatusCode is not None:
        tableContract = db.table('Contract')
        queryTable = queryTable.leftJoin(tableContract, tableContract['id'].eq(tableEvent['contract_id']))
        cond.append('getPayCode(%s, %s) = %d' % (tableContract['finance_id'], tableEvent['payStatus'], payStatusCode))
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if mode <= 2:
        stmt = db.selectStmt(queryTable, cols, cond, group=group)
        return db.query(stmt)
    else:
        execDateCond = 'AND Event.execDate IS NOT NULL' if not params.get('countUnfinished', False) else ''
        return db.query(selectStmt % (execDateCond, db.joinAnd(cond)))

#TODO: объединить классы
class CReportDDCommonResults(CReport):

    def __init__(self, parent, reportType = 2014):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.reportType = reportType
        if self.reportType == 2014:
            self.setTitle(u'Сведения о распространенности факторов риска развития хронических неинфекционных заболеваний, являющихся основной причиной инвалидности и преждевременной смертности населения Российской Федерации (человек)')
        else:
            self.setTitle(u'Общие результаты диспансеризации определенных групп взрослого населения')

    def getSetupDialog(self, parent):
        result = CReportDD2013WeeklySetupDialog(parent)
        result.setTitle(self.title())
        return result

    def processQuery(self, params, mode):
        resultSet = {}
        query = selectData(params, mode)
        self.addQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            name = forceString(record.value('name'))
            age = forceInt(record.value('client_age'))
            sex = forceInt(record.value('sex'))
            count = forceInt(record.value('count'))
            res_id = forceRef(record.value('res_id'))

            if not res_id:
                continue
            if not res_id in resultSet:
                resultSet[res_id] = [name] + [0]*6
            row = resultSet[res_id]
            if sex:
                if 20 <= age <= 36:
                    row[(sex-1)*3 + 1] += count
                elif 39 <= age <= 60:
                    row[(sex-1)*3 + 2] += count
                elif age > 60:
                    row[sex*3] += count
        return resultSet

    def build(self, params):
        finalResultSet = []

        resultSet = self.processQuery(params, 0)
        diagResultSet = self.processQuery(params, 1)

        for i in sorted(resultSet.keys()):
            finalResultSet.append(resultSet[i])
        for i in sorted(diagResultSet.keys()):
            finalResultSet.append(diagResultSet[i])

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
            ( '41%', [u'Результат диспансеризации определенных групп взрослого населения\n(далее - диспансеризация)', u''], CReportBase.AlignLeft),
            ( '5%', [u'№ строки', u''], CReportBase.AlignCenter),
            ( '9%', [u'Мужчины', u'21 - 36 лет'], CReportBase.AlignRight),
            ( '9%', [u'', u'39 - 60 лет'], CReportBase.AlignRight),
            ( '9%', [u'', u'Старше 60 лет'], CReportBase.AlignRight),
            ( '9%', [u'Женщины', u'21 - 36 лет'], CReportBase.AlignRight),
            ( '9%', [u'', u'39 - 60 лет'], CReportBase.AlignRight),
            ( '9%', [u'', u'Старше 60 лет'], CReportBase.AlignRight),
        ]
        rowSize = 8
        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 1, 3)
        table.mergeCells(0, 5, 1, 3)

        i = table.addRow()

        for j in xrange(rowSize):
            table.setText(i, j, j+1, blockFormat = bf)

        for z in range(len(finalResultSet)):
            row = finalResultSet[z]
            i = table.addRow()
            table.setText(i, 0, row[0])
            table.setText(i, 1, '%2d' % z)
            for j in range(2, rowSize):
                table.setText(i, j, row[j-1])

        query = selectData(params, 2)
        query.first()
        record = query.record()
        cursor.movePosition(cursor.End)
        cursor.insertBlock()
        cursor.insertText(u'\n7001 Общее число работающих граждан, прошедших диспансеризацию: %d человек' % forceInt(record.value('countWorking')))
        cursor.insertText(u'\n7002 Общее число неработающих граждан, прошедших диспансеризацию: %d человек' % forceInt(record.value('countNotWorking')))
        cursor.insertText(u'\n7003 Общее число прошедших диспансеризацию граждан, обучающихся в образовательных организациях по очной форме: %d человек' % forceInt(record.value('countStudents')))
        if self.reportType == 2014:
            cursor.insertText(u'\n7004 Общее число прошедших диспансеризацию инвалидов Великой Отечественной войны, лиц, награжденных знаком "Жителю блокадного Ленинграда" и признанных инвалидами вследствие общего заболевания, трудового увечья и других причин (кроме лиц, инвалидность которых наступила вследствие их противоправных действий): %d человек' % forceInt(record.value('countDiscount')))
            cursor.insertText(u'\n7005 Общее число прошедших диспансеризацию граждан, принадлежащих к коренным народам Севера, Сибири и дальнего Востока Российской Федерации.')
            cursor.insertText(u'\n7006 Общее число медицинских организаций, принимавших участие в диспансеризации %d' % (forceInt(record.value('countOrgs')) + 1))
        else:
            cursor.insertText(u'\n7004 Общее число прошедших диспансеризацию инвалидов Великой Отечественной войны, лиц, награжденных знаком «Жителю блокадного Ленинграда»' \
                    u'и признанных инвалидами вследствие общего заболевания, трудового увечья и других причин (кроме лиц, инвалидность которых наступила вследствие их противоправных действий),'\
                    u'лиц награжденных знаком «Жителю блокадного Ленинграда», ветеранов, вдов (вдовцов) умерших инвалидов и ветеранов Великой Отечественной войны 1941–1945 годов, бывших несовершеннолетних узников концлагерей,'\
                    u'гетто, других мест принудительного содержания, созданных фашистами и их союзниками в период Второй мировой войны. %s человек.' % forceInt(record.value('countDiscount')))
            cursor.insertText(u'\n7005 Общее число прошедших диспансеризацию граждан, принадлежащих к коренным народам Севера, Сибири и дальнего Востока Российской Федерации ________ человек')
            cursor.insertText(u'\n7006 Общее число медицинских организаций, принимавших участие в диспансеризации %d, из них имеют кабинеты или отделения медицинской профилактики ________ медицинских организаций' % (forceInt(record.value('countOrgs')) + 1))
        cursor.insertText(u'\n7007 Общее число мобильных медицинских бригад, принимавших участие в проведении диспансеризации ______')
        cursor.insertText(u'\n7008 Общее число граждан, диспансеризация которых была проведена мобильными бригадами, _______ человек')
        cursor.insertText(u'\n7009 Число письменных отказов от прохождения отдельных осмотров (консультаций), исследований в рамках диспансеризации %d' % forceInt(record.value('countDeclinedActions')))
        cursor.insertText(u'\n7010 Число письменных отказов от прохождения диспансеризации в целом %d' % forceInt(record.value('countDeclinedEvents')))
        countFirstStep = forceInt(record.value('countFirstStep'))
        cursor.insertText(u'\n7011 Число граждан, прошедших за отчетный период первый этап диспансеризации и не завершивших второй этап диспансеризации %d человек' % ((countFirstStep - forceInt(record.value('countSecondStep'))) if countFirstStep else 0))
        cursor.insertText(u'\n7012 Число граждан, проживающих в сельской местности, прошедших диспансеризацию в отчетном периоде, %d человек' % forceInt(record.value('countVillagers')))

        return doc


class CReportDDCommonResults2015(CReport):

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Общие результаты диспансеризации определенных групп взрослого населения')

    def getSetupDialog(self, parent):
        result = CReportDD2013WeeklySetupDialog(parent)
        result.setTitle(self.title())
        return result

    def processQuery(self, params, mode):
        resultSet = {}
        query = selectData(params, mode, DDREPORT_2015)
        while query.next():
            record = query.record()
            age = forceInt(record.value('clientAge'))
            sex = forceInt(record.value('clientSex'))
            count = forceInt(record.value('count'))
            resultCode = forceRef(record.value('resultCode'))

            if not resultCode:
                continue
            if not resultCode in resultSet:
                resultSet[resultCode] = [0] * 6
            row = resultSet[resultCode]
            if sex:
                if 20 <= age <= 36:
                    row[(sex-1)*3] += count
                elif 39 <= age <= 60:
                    row[(sex-1)*3 + 1] += count
                elif age > 60:
                    row[sex*3 - 1] += count
        return resultSet

    def build(self, params):
        if QtGui.qApp.region() == '78':
            mapResultRow = {
                50: 0, 89: 0,                     # 1 группа здоровья
                51: 1, 90: 1,                     # 2
                52: 2, 53: 2, 91:2, 92: 2, 94: 2, # 3a
                54: 3, 93: 3, 95: 3,              # 3b
                32: 4,
                11: 7
            }
        else:
            mapResultRow = {
                317: 0, 352: 0,
                318: 1, 353: 1,
                355: 2, 357: 2,
                356: 3, 358: 3
            }

        finalResultSet = [
            [u'Определена I группа состояния здоровья', u'01', 0, 0, 0, 0, 0, 0],
            [u'Определена II группа состояния здоровья', u'02', 0, 0, 0, 0, 0, 0],
            [u'Определена IIIа группа состояния здоровья', u'03', 0, 0, 0, 0, 0, 0],
            [u'Определена IIIб группа состояния здоровья', u'04', 0, 0, 0, 0, 0, 0],
            [u'Назначено лечение', u'05', 0, 0, 0, 0, 0, 0],
            [u'Направлено на дополнительное обследование, не входящее в объем диспансеризации', u'06', 0, 0, 0, 0, 0, 0],
            [u'Направлено для получения специализированной, в том числе высокотехнологичной, медицинской помощи', u'07', 0, 0, 0, 0, 0, 0],
            [u'Направлено на санаторно-курортное лечение', u'08', 0, 0, 0, 0, 0, 0]
        ]

        resultSet = self.processQuery(params, 0)
        diagResultSet = self.processQuery(params, 1)

        for dataSet in (resultSet, diagResultSet):
            for resultCode in sorted(dataSet.keys()):
                if resultCode in mapResultRow:
                    row, data = mapResultRow[resultCode], dataSet[resultCode]
                    for col in xrange(len(data)):
                        finalResultSet[row][2 + col] = data[col]

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
            ( '41%', [u'Результат диспансеризации определенных групп взрослого населения\n(далее - диспансеризация)', u''], CReportBase.AlignLeft),
            ( '5%', [u'№ строки', u''], CReportBase.AlignCenter),
            ( '9%', [u'Мужчины', u'21 - 36 лет'], CReportBase.AlignRight),
            ( '9%', [u'', u'39 - 60 лет'], CReportBase.AlignRight),
            ( '9%', [u'', u'Старше 60 лет'], CReportBase.AlignRight),
            ( '9%', [u'Женщины', u'21 - 36 лет'], CReportBase.AlignRight),
            ( '9%', [u'', u'39 - 60 лет'], CReportBase.AlignRight),
            ( '9%', [u'', u'Старше 60 лет'], CReportBase.AlignRight),
        ]

        rowSize = len(tableColumns)
        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 1, 3)
        table.mergeCells(0, 5, 1, 3)

        i = table.addRow()
        for j in xrange(rowSize):
            table.setText(i, j, j+1, blockFormat = bf)

        for z in range(len(finalResultSet)):
            row = finalResultSet[z]
            i = table.addRow()
            table.setText(i, 0, row[0])
            table.setText(i, 1, row[1])
            for j in xrange(2, rowSize):
                table.setText(i, j, row[j])

        query = selectData(params, 2, DDREPORT_2015, mapResultRow.keys())
        self.addQueryText(forceString(query.lastQuery()))
        query.first()
        record = query.record()
        cursor.movePosition(cursor.End)
        cursor.insertBlock()

        countFirstStep = forceInt(record.value('countFirstStep'))
        rows = [
            u'\n7001 Общее число работающих граждан, прошедших диспансеризацию: %d человек' % forceInt(record.value('countWorking')),
            u'\n7002 Общее число неработающих граждан, прошедших диспансеризацию: %d человек' % forceInt(record.value('countNotWorking')),
            u'\n7004 Общее число граждан, имеющих право на получение государственной социальной помощи в виде набора социальных услуг, прошедших диспансеризацию, %d чел., из них:\n' % forceInt(record.value('countDiscount')),
            u'\tинвалиды войны: %d чел.;\n' % forceInt(record.value('countDisabled')),
            u'\tучастники Великой Отечественной войны, ветераны боевых действий из числа лиц, '
            u'указанных в подпунктах 1 - 4 пункта 1 статьи 3 Федерального закона от 12 января 1995 г. №5-ФЗ "О ветеранах": %d чел.;\n' % forceInt(record.value('countWarVeterans')),
            u'\tлица, награжденные знаком "Жителю блокадного Ленинграда" и признанных инвалидами вследствие общего заболевания, трудового увечья и других причин '
            u'(кроме лиц, инвалидность которых наступила вследствие их противоправных действий): %d чел.;' % forceInt(record.value('countBesiegedLeningrad')),
            u'\n7005 Общее число прошедших диспансеризацию граждан, принадлежащих к коренным малочисленным народам Севера, Сибири и Дальнего Востока Российской Федерации: %d человек' % 0,
            u'\n7006 Общее число медицинских организаций, принимавших участие в проведении диспансеризации, а также имеющих кабинеты или отделения медицинской профилактики: %d человек' % 0,
            u'\n7007 Общее число мобильных медицинских бригад, принимавших участие в проведении диспансеризации: %d человек' % forceInt(record.value('countMobile')),
            u'\n7008 Общее число граждан, диспансеризация которых была проведена мобильными медицинскими бригадами: %d человек' % forceInt(record.value('countMobilePatients')),
            u'\n7009 Число письменных отказов от прохождения медицинских мероприятий в рамках диспансеризации: %d человек' % forceInt(record.value('countDeclinedActions')),
            u'\n7010 Число письменных отказов от прохождения диспансеризации в целом: %d человек' % forceInt(record.value('countDeclinedEvents')),
            u'\n7011 Число граждан, прошедших первый этап диспансеризации и не завершивших второй этап диспансеризации: %d человек' % ((countFirstStep - forceInt(record.value('countSecondStep'))) if countFirstStep else 0),
            u'\n7012 Число граждан, проживающих в сельской местности, прошедших диспансеризацию: %d человек' % forceInt(record.value('countVillagers')),

        ]
        for row in rows:
            cursor.insertText(row)

        cursor.insertBlock()
        tableColumns = [
            ( '50%', [u''], CReportBase.AlignCenter),
            ( '15%', [u''], CReportBase.AlignCenter),
            ( '15%', [u''], CReportBase.AlignCenter),
        ]
        table = createTable(cursor, tableColumns, 0, 0)
        i = table.addRow()
        table.setText(i, 0, '_'*50)
        table.setText(i, 1, '_'*25)
        table.setText(i, 2, '_'*25)
        i = table.addRow()
        table.setText(i, 0, u'(должность)')
        table.setText(i, 1, u'(Ф.И.О.)')
        table.setText(i, 2, u'(подпись)')
        i = table.addRow()
        table.setText(i, 2, u'М.П.')
        i = table.addRow()
        table.setText(i, 1, u'Адрес электронной почты:')
        i = table.addRow()
        table.setText(i, 0, '_'*50)
        table.setText(i, 1, '_'*25)
        table.setText(i, 2, u'«____» _____________ 20___ года')
        i = table.addRow()
        table.setText(i, 0, u'(номер контактного телефона)')
        table.setText(i, 2, u'(дата составления документа)')
        return doc



class CReportDDCommonResults2017(CReport):

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Общие результаты диспансеризации определенных групп взрослого населения')

    def getSetupDialog(self, parent):
        result = CReportDD2013WeeklySetupDialog(parent)
        result.setTitle(self.title())
        return result

    def processQuery(self, params, mode):
        resultSet = {}
        query = selectData(params, mode, DDREPORT_2017)
        while query.next():
            record = query.record()
            age = forceInt(record.value('clientAge'))
            sex = forceInt(record.value('clientSex'))
            count = forceInt(record.value('count'))
            resultCode = forceRef(record.value('resultCode'))
            netricaCode = forceRef(record.value('netrica_Code'))
            clientId = forceInt(record.value('clientId'))

            if netricaCode:
                if not netricaCode in resultSet:
                    resultSet[netricaCode] = [0] * 6

            if not resultCode:
                continue
            if not resultCode in resultSet:
                resultSet[resultCode] = [0] * 6

            row = resultSet[resultCode]
            if netricaCode:
                rowNetrica = resultSet[netricaCode]

            if sex:
                if 20 <= age <= 36:
                    row[(sex-1)*3] += count
                    if netricaCode:
                        rowNetrica[(sex-1)*3] += count
                elif 39 <= age <= 60:
                    row[(sex-1)*3 + 1] += count
                    if netricaCode:
                        rowNetrica[(sex-1)*3 + 1] += count
                elif age > 60:
                    row[sex*3 - 1] += count
                    if netricaCode:
                        rowNetrica[sex*3 - 1] += count
        return resultSet

    def build(self, params):
        if QtGui.qApp.region() == '78':
            mapResultRow = {
                50: 0, 89: 0,                     # 1 группа здоровья
                51: 1, 90: 1,                     # 2
                52: 2, 53: 2, 91:2, 92: 2, 94: 2, # 3a
                54: 3, 93: 3, 95: 3,              # 3b
                32: 4,
                11: 7
            }
        else:
            mapResultRow = {
                317: 0,
                318: 1, 353: 1,
                355: 2, 357: 2,
                356: 3, 358: 3,
                3: 5,
                1: 6
            }

        finalResultSet = [
            [u'Определена I группа состояния здоровья', u'01', 0, 0, 0, 0, 0, 0],
            [u'Определена II группа состояния здоровья', u'02', 0, 0, 0, 0, 0, 0],
            [u'Определена IIIа группа состояния здоровья', u'03', 0, 0, 0, 0, 0, 0],
            [u'Определена IIIб группа состояния здоровья', u'04', 0, 0, 0, 0, 0, 0],
            [u'Назначено лечение', u'05', 0, 0, 0, 0, 0, 0],
            [u'Направлено на дополнительное обследование, не входящее в объем диспансеризации', u'06', 0, 0, 0, 0, 0, 0],
            [u'Направлено для получения специализированной, в том числе высокотехнологичной, медицинской помощи', u'07', 0, 0, 0, 0, 0, 0],
            [u'Направлено на санаторно-курортное лечение', u'08', 0, 0, 0, 0, 0, 0]
        ]

        resultSet = self.processQuery(params, 0)
        diagResultSet = self.processQuery(params, 1)
        for dataSet in (resultSet, diagResultSet):
            for resultCode in sorted(dataSet.keys()):
                if resultCode in mapResultRow:
                    row, data = mapResultRow[resultCode], dataSet[resultCode]
                    for col in xrange(len(data)):
                        finalResultSet[row][2 + col] += data[col]

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
            ( '41%', [u'Результат диспансеризации определенных групп взрослого населения\n(далее - диспансеризация)', u''], CReportBase.AlignLeft),
            ( '5%', [u'№ строки', u''], CReportBase.AlignCenter),
            ( '9%', [u'Мужчины', u'21 - 36 лет'], CReportBase.AlignRight),
            ( '9%', [u'', u'39 - 60 лет'], CReportBase.AlignRight),
            ( '9%', [u'', u'Старше 60 лет'], CReportBase.AlignRight),
            ( '9%', [u'Женщины', u'21 - 36 лет'], CReportBase.AlignRight),
            ( '9%', [u'', u'39 - 60 лет'], CReportBase.AlignRight),
            ( '9%', [u'', u'Старше 60 лет'], CReportBase.AlignRight),
        ]

        cursor.movePosition(cursor.End)
        cursor.insertText(u'7000')

        rowSize = len(tableColumns)
        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 1, 3)
        table.mergeCells(0, 5, 1, 3)

        i = table.addRow()
        for j in xrange(rowSize):
            table.setText(i, j, j+1, blockFormat = bf)

        for z in range(len(finalResultSet)):
            row = finalResultSet[z]
            i = table.addRow()
            table.setText(i, 0, row[0])
            table.setText(i, 1, row[1])
            for j in xrange(2, rowSize):
                table.setText(i, j, row[j])
        query = selectData(params, 2, DDREPORT_2017, mapResultRow.keys())
        self.addQueryText(forceString(query.lastQuery()))
        query.first()
        record = query.record()
        cursor.movePosition(cursor.End)
        cursor.insertBlock()

        countFirstStep = forceInt(record.value('countFirstStep'))
        rows = [
            u'\n7001 Общее число работающих граждан, прошедших диспансеризацию: %d человек' % forceInt(record.value('countWorking')),
            u'\n7002 Общее число неработающих граждан, прошедших диспансеризацию: %d человек' % forceInt(record.value('countNotWorking')),
            u'\n7003 Общее число граждан, обучающихся в образовательных организациях по очной форме, прошедших диспансеризацию: %d человек' % forceInt(record.value('students')),
            u'\n7004 Общее число граждан, имеющих право на получение государственной социальной помощи в виде набора социальных услуг, прошедших диспансеризацию, %d чел., из них:\n' % forceInt(record.value('beneficiaries')),
            u'\tинвалиды войны: %d чел.;\n' % forceInt(record.value('beneficiaries10_11')),
            u'\tучастники Великой Отечественной войны, ветераны боевых действий из числа лиц, '
            u'указанных в подпунктах 1 - 4 пункта 1 статьи 3 Федерального закона от 12 января 1995 г. №5-ФЗ "О ветеранах": %d чел.;\n' % forceInt(record.value('beneficiaries20')),
            u'\tлица, награжденные знаком "Жителю блокадного Ленинграда" и признанных инвалидами вследствие общего заболевания, трудового увечья и других причин '
            u'(кроме лиц, инвалидность которых наступила вследствие их противоправных действий): %d чел.;' % forceInt(record.value('beneficiaries50')),
            u'\n7005 Общее число прошедших диспансеризацию граждан, принадлежащих к коренным малочисленным народам Севера, Сибири и Дальнего Востока Российской Федерации: %d человек' % 0,
            u'\n7006 Общее число медицинских организаций, принимавших участие в проведении диспансеризации, а также имеющих кабинеты или отделения медицинской профилактики: %d человек' % 0,
            u'\n7007 Общее число мобильных медицинских бригад, принимавших участие в проведении диспансеризации: %d бригад' % forceInt(record.value('countMobile')),
            u'\n7008 Общее число граждан, диспансеризация которых была проведена мобильными медицинскими бригадами: %d человек' % forceInt(record.value('dispByMobileTeam')),
            u'\n7009 Число письменных отказов от прохождения медицинских мероприятий в рамках диспансеризации: %d человек' % forceInt(record.value('countDeclinedActions')),
            u'\n7010 Число письменных отказов от прохождения диспансеризации в целом: %d человек' % forceInt(record.value('countDeclinedEvents')),
            u'\n7011 Число граждан, прошедших первый этап диспансеризации и не завершивших второй этап диспансеризации: / человек', #% ((countFirstStep - forceInt(record.value('countSecondStep'))) if countFirstStep else 0),
            u'\n7012 Число граждан, проживающих в сельской местности, прошедших диспансеризацию: %d человек' % forceInt(record.value('countVillagers')),

        ]
        for row in rows:
            cursor.insertText(row)

        cursor.insertBlock()
        tableColumns = [
            ( '50%', [u''], CReportBase.AlignCenter),
            ( '15%', [u''], CReportBase.AlignCenter),
            ( '15%', [u''], CReportBase.AlignCenter),
        ]
        table = createTable(cursor, tableColumns, 0, 0)
        i = table.addRow()
        table.setText(i, 0, '_'*50)
        table.setText(i, 1, '_'*25)
        table.setText(i, 2, '_'*25)
        i = table.addRow()
        table.setText(i, 0, u'(должность)')
        table.setText(i, 1, u'(Ф.И.О.)')
        table.setText(i, 2, u'(подпись)')
        i = table.addRow()
        table.setText(i, 2, u'М.П.')
        i = table.addRow()
        table.setText(i, 1, u'Адрес электронной почты:')
        i = table.addRow()
        table.setText(i, 0, '_'*50)
        table.setText(i, 1, '_'*25)
        table.setText(i, 2, u'«____» _____________ 20___ года')
        i = table.addRow()
        table.setText(i, 0, u'(номер контактного телефона)')
        table.setText(i, 2, u'(дата составления документа)')
        return doc
