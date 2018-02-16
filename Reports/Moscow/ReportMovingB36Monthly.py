# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from library.DialogBase import CDialogBase
from library.Utils      import forceBool, forceInt, forceRef, forceString

from Orgs.Utils         import getOrgStructureDescendants

from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.ReportView import CPageFormat

from Ui_ReportMovingB36MonthlySetupDialog import Ui_ReportMovingB36MonthlySetupDialog


def selectHospitalBeds(orgStructureIds=[]):
    db = QtGui.qApp.db
    OrgStructure = db.table('OrgStructure')
    OSHB = db.table('OrgStructure_HospitalBed')

    queryTable = OrgStructure.leftJoin(OSHB, OSHB['master_id'].eq(OrgStructure['id']))

    cols = [
        OrgStructure['id'].alias('orgStructureId'),
        'count(if({isPermanent}, {oshbId}, NULL)) AS beds'.format(isPermanent=OSHB['isPermanent'].eq(1), oshbId=OSHB['id'])
    ]

    cond = []
    if orgStructureIds:
        cond.append(OrgStructure['id'].inlist(orgStructureIds))

    group = [
        OrgStructure['id']
    ]

    stmt = db.selectStmt(queryTable, cols, cond, group=group)
    return db.query(stmt)


def selectMoving(dateTime, orgStructureIds=[]):
    u"""
        Состояло пациентов в отделениях на данный момент времени
    """

    db = QtGui.qApp.db
    Action = db.table('Action')
    ActionType = db.table('ActionType')
    ActionProperty = db.table('ActionProperty')
    ActionPropertyType = db.table('ActionPropertyType')
    ActionProperty_OrgStructure = db.table('ActionProperty_OrgStructure')
    Client = db.table('Client')
    Event = db.table('Event')
    Finance = db.table('rbFinance')

    queryTable = ActionType.innerJoin(Action, [Action['actionType_id'].eq(ActionType['id']),
                                               Action['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(Event, [Event['id'].eq(Action['event_id']),
                                              Event['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(Client, Client['id'].eq(Event['client_id']))

    queryTable = queryTable.innerJoin(ActionPropertyType, [ActionPropertyType['name'].eq(u'Отделение пребывания'),
                                                           ActionPropertyType['actionType_id'].eq(ActionType['id']),
                                                           ActionPropertyType['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(ActionProperty, [ActionProperty['action_id'].eq(Action['id']),
                                                       ActionProperty['type_id'].eq(ActionPropertyType['id']),
                                                       ActionProperty['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(ActionProperty_OrgStructure, ActionProperty_OrgStructure['id'].eq(ActionProperty['id']))

    queryTable = queryTable.innerJoin(Finance, Finance['id'].eq(Action['finance_id']))

    cols = [
        ActionProperty_OrgStructure['value'].alias('orgStructureId'),
        Finance['code'].alias('financeCode'),
        'count({item}) AS moving'.format(item=ActionProperty['id'])
    ]

    cond = [
        ActionType['flatCode'].eq('moving'),
        ActionType['deleted'].eq(0),
        Action['begDate'].datetimeLt(dateTime),
        db.joinOr([Action['endDate'].datetimeGe(dateTime),
                   Action['endDate'].isNull()])
    ]

    if orgStructureIds:
        cond.append(ActionProperty_OrgStructure['value'].inlist(orgStructureIds))

    group = [
        'orgStructureId',
        'financeCode'
    ]

    stmt = db.selectStmt(queryTable, cols, cond, group=group)
    return db.query(stmt)


def selectReceived(begDateTime, endDateTime, orgStructureIds=[]):
    u"""
        Поступило пациентов в отделения за данный период времени
    """

    db = QtGui.qApp.db
    Action = db.table('Action')
    ActionType = db.table('ActionType')
    ActionProperty = db.table('ActionProperty')
    ActionPropertyType = db.table('ActionPropertyType')
    ActionProperty_OrgStructure = db.table('ActionProperty_OrgStructure')
    ActionProperty_String = db.table('ActionProperty_String')
    Address = db.table('Address')
    AddressHouse = db.table('AddressHouse')
    Client = db.table('Client')
    ClientAddress = db.table('ClientAddress')
    ClientDocument = db.table('ClientDocument')
    ClientSocStatus = db.table('ClientSocStatus')
    DocumentType = db.table('rbDocumentType')
    Event = db.table('Event')
    Finance = db.table('rbFinance')
    SocStatusType = db.table('rbSocStatusType')

    DeliveredByAPTName = u'Кем доставлен'
    DeliveredByAPT = ActionPropertyType.alias('DeliveredByAPT')
    DeliveredByAP = ActionProperty.alias('DeliveredByAP')
    DeliveredByAPS = ActionProperty_String.alias('DeliveredByAPS')

    HospRefusalAPTName = u'Причина отказа от госпитализации'
    HospRefusalAPT = ActionPropertyType.alias('HospRefusalAPT')
    HospRefusalAP = ActionProperty.alias('HospRefusalAP')
    HospRefusalAPS = ActionProperty_String.alias('HospRefusalAPS')

    queryTable = ActionType.innerJoin(Action, [Action['actionType_id'].eq(ActionType['id']),
                                               Action['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(Event, [Event['id'].eq(Action['event_id']),
                                              Event['deleted'].eq(0)])

    queryTable = queryTable.innerJoin(Client, Client['id'].eq(Event['client_id']))
    queryTable = queryTable.leftJoin(ClientDocument, '{CDId} = getClientDocumentId({clientId})'.format(CDId=ClientDocument['id'],
                                                                                                       clientId=Client['id']))
    queryTable = queryTable.leftJoin(DocumentType, DocumentType['id'].eq(ClientDocument['documentType_id']))

    queryTable = queryTable.leftJoin(ClientAddress, '{CAId} = getClientRegAddressId({clientId})'.format(CAId=ClientAddress['id'],
                                                                                                        clientId=Client['id']))
    queryTable = queryTable.leftJoin(Address, [Address['id'].eq(ClientAddress['address_id']),
                                               Address['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(AddressHouse, AddressHouse['id'].eq(Address['house_id']))

    queryTable = queryTable.innerJoin(ActionPropertyType, [ActionPropertyType['name'].eq(u'Направлен в отделение'),
                                                           ActionPropertyType['actionType_id'].eq(ActionType['id']),
                                                           ActionPropertyType['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(ActionProperty, [ActionProperty['action_id'].eq(Action['id']),
                                                       ActionProperty['type_id'].eq(ActionPropertyType['id']),
                                                       ActionProperty['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(ActionProperty_OrgStructure, ActionProperty_OrgStructure['id'].eq(ActionProperty['id']))

    queryTable = queryTable.innerJoin(DeliveredByAPT, [DeliveredByAPT['name'].eq(DeliveredByAPTName),
                                                       DeliveredByAPT['actionType_id'].eq(ActionType['id']),
                                                       DeliveredByAPT['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(DeliveredByAP, [DeliveredByAP['action_id'].eq(Action['id']),
                                                     DeliveredByAP['type_id'].eq(DeliveredByAPT['id']),
                                                     DeliveredByAP['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(DeliveredByAPS, DeliveredByAPS['id'].eq(DeliveredByAP['id']))

    queryTable = queryTable.innerJoin(HospRefusalAPT, [HospRefusalAPT['name'].eq(HospRefusalAPTName),
                                                       HospRefusalAPT['actionType_id'].eq(ActionType['id']),
                                                       HospRefusalAPT['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(HospRefusalAP, [HospRefusalAP['action_id'].eq(Action['id']),
                                                     HospRefusalAP['type_id'].eq(HospRefusalAPT['id']),
                                                     HospRefusalAP['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(HospRefusalAPS, HospRefusalAPS['id'].eq(HospRefusalAP['id']))

    queryTable = queryTable.leftJoin(Finance, Finance['id'].eq(Action['finance_id']))

    socStatusTable = ClientSocStatus.innerJoin(SocStatusType, SocStatusType['id'].eq(ClientSocStatus['socStatusType_id']))
    socStatusCond = [
        ClientSocStatus['deleted'].eq(0),
        ClientSocStatus['client_id'].eq(Client['id']),
        db.joinOr([SocStatusType['name'].like(u'%участник ВОВ%'),
                   SocStatusType['name'].like(u'%инвалид%войны%')])
    ]
    veteranCond = db.existsStmt(socStatusTable, socStatusCond)

    cols = [
        ActionProperty_OrgStructure['value'].alias('orgStructureId'),
        Finance['code'].alias('financeCode'),
        Action['isUrgent'].alias('isUrgent'),
        # DeliveredByAPS['value'].alias('deliveredBy'),
        u'''CASE
        WHEN {aps} LIKE '%скорая помощь%'  THEN 1
        WHEN {aps} LIKE '%самотёк%'        THEN 2
        WHEN {aps} LIKE '%ДМС%'            THEN 3
        WHEN {aps} LIKE 'ПМУ'              THEN 4
        WHEN {aps} LIKE '%РВК%'            THEN 5
        ELSE 0
        END AS deliveredBy'''.format(aps=DeliveredByAPS['value']),
        u'LEFT({KLADRCode}, 2) = 77 AS isMoscowResident'.format(KLADRCode=AddressHouse['KLADRCode']),
        # DocumentType['isForeigner'].alias('isForeigner'),
        u'count(if({veteranCond}, {item}, NULL)) as veterans'.format(veteranCond=veteranCond, item=ActionProperty['id']),
        u'count({item}) AS received'.format(item=ActionProperty['id']),
    ]

    cond = [
        ActionType['flatCode'].eq('received'),
        ActionType['deleted'].eq(0),
        Action['begDate'].datetimeGe(begDateTime),
        Action['begDate'].datetimeLt(endDateTime)
    ]

    if orgStructureIds:
        cond.append(ActionProperty_OrgStructure['value'].inlist(orgStructureIds))

    group = [
        'orgStructureId',
        'isUrgent',
        'deliveredBy',
        'financeCode',
        'isMoscowResident'
    ]

    stmt = db.selectStmt(queryTable, cols, cond, group=group)
    return db.query(stmt)


def selectMovingInto(begDateTime, endDateTime, orgStructureIds=[]):
    u"""
        Переведено пациентов в отделение за данный период времени
    """

    db = QtGui.qApp.db
    Action = db.table('Action')
    ActionType = db.table('ActionType')
    ActionProperty = db.table('ActionProperty')
    ActionPropertyType = db.table('ActionPropertyType')
    ActionProperty_OrgStructure = db.table('ActionProperty_OrgStructure')
    Client = db.table('Client')
    Event = db.table('Event')
    Finance = db.table('rbFinance')

    queryTable = ActionType.innerJoin(Action, [Action['actionType_id'].eq(ActionType['id']),
                                               Action['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(Event, [Event['id'].eq(Action['event_id']),
                                              Event['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(Client, Client['id'].eq(Event['client_id']))

    queryTable = queryTable.innerJoin(ActionPropertyType, [ActionPropertyType['name'].eq(u'Переведен в отделение'),
                                                           ActionPropertyType['actionType_id'].eq(ActionType['id']),
                                                           ActionPropertyType['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(ActionProperty, [ActionProperty['action_id'].eq(Action['id']),
                                                       ActionProperty['type_id'].eq(ActionPropertyType['id']),
                                                       ActionProperty['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(ActionProperty_OrgStructure, ActionProperty_OrgStructure['id'].eq(ActionProperty['id']))

    queryTable = queryTable.leftJoin(Finance, Finance['id'].eq(Action['finance_id']))

    cols = [
        ActionProperty_OrgStructure['value'].alias('orgStructureId'),
        Finance['code'].alias('financeCode'),
        'count({item}) AS movingInto'.format(item=ActionProperty['id'])
    ]

    cond = [
        ActionType['flatCode'].eq('moving'),
        ActionType['deleted'].eq(0),
        Action['endDate'].datetimeGe(begDateTime),
        Action['endDate'].datetimeLt(endDateTime)
    ]

    if orgStructureIds:
        cond.append(ActionProperty_OrgStructure['value'].inlist(orgStructureIds))

    group = [
        'orgStructureId',
        'financeCode'
    ]

    stmt = db.selectStmt(queryTable, cols, cond, group=group)
    return db.query(stmt)


def selectMovingFrom(begDateTime, endDateTime, orgStructureIds=[]):
    u"""
        Переведено пациентов из отделения за данный период времени
    """

    db = QtGui.qApp.db
    Action = db.table('Action')
    ActionType = db.table('ActionType')
    ActionProperty = db.table('ActionProperty')
    ActionPropertyType = db.table('ActionPropertyType')
    ActionProperty_OrgStructure = db.table('ActionProperty_OrgStructure')
    Client = db.table('Client')
    Event = db.table('Event')
    Finance = db.table('rbFinance')

    queryTable = ActionType.innerJoin(Action, [Action['actionType_id'].eq(ActionType['id']),
                                               Action['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(Event, [Event['id'].eq(Action['event_id']),
                                              Event['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(Client, Client['id'].eq(Event['client_id']))

    queryTable = queryTable.innerJoin(ActionPropertyType, [ActionPropertyType['name'].eq(u'Переведен из отделения'),
                                                           ActionPropertyType['actionType_id'].eq(ActionType['id']),
                                                           ActionPropertyType['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(ActionProperty, [ActionProperty['action_id'].eq(Action['id']),
                                                       ActionProperty['type_id'].eq(ActionPropertyType['id']),
                                                       ActionProperty['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(ActionProperty_OrgStructure, ActionProperty_OrgStructure['id'].eq(ActionProperty['id']))

    queryTable = queryTable.leftJoin(Finance, Finance['id'].eq(Action['finance_id']))

    cols = [
        ActionProperty_OrgStructure['value'].alias('orgStructureId'),
        Finance['code'].alias('financeCode'),
        'count({item}) AS movingFrom'.format(item=ActionProperty['id'])
    ]

    cond = [
        ActionType['flatCode'].eq('moving'),
        ActionType['deleted'].eq(0),
        Action['begDate'].datetimeGe(begDateTime),
        Action['begDate'].datetimeLt(endDateTime)
    ]

    if orgStructureIds:
        cond.append(ActionProperty_OrgStructure['value'].inlist(orgStructureIds))

    group = [
        'orgStructureId',
        'financeCode'
    ]

    stmt = db.selectStmt(queryTable, cols, cond, group=group)
    return db.query(stmt)


def selectLeaved(begDateTime, endDateTime, orgStructureIds=[]):
    u"""
        Выписано пациентов в отделение за данный период времени
    """

    db = QtGui.qApp.db
    Action = db.table('Action')
    ActionType = db.table('ActionType')
    ActionProperty = db.table('ActionProperty')
    ActionPropertyType = db.table('ActionPropertyType')
    ActionProperty_OrgStructure = db.table('ActionProperty_OrgStructure')
    ActionProperty_String = db.table('ActionProperty_String')
    Client = db.table('Client')
    Event = db.table('Event')
    Finance = db.table('rbFinance')

    ResultAPT = ActionPropertyType.alias('ResultAPT')
    ResultAP = ActionProperty.alias('ResultAP')
    ResultAPS = ActionProperty_String.alias('ResultAPS')

    ReceivedAT = ActionType.alias('ReceivedAT')
    Received = Action.alias('Received')

    queryTable = ActionType.innerJoin(Action, [Action['actionType_id'].eq(ActionType['id']),
                                               Action['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(Event, [Event['id'].eq(Action['event_id']),
                                              Event['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(Client, Client['id'].eq(Event['client_id']))

    queryTable = queryTable.innerJoin(ActionPropertyType, [ActionPropertyType['name'].eq(u'Отделение'),
                                                           ActionPropertyType['actionType_id'].eq(ActionType['id']),
                                                           ActionPropertyType['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(ActionProperty, [ActionProperty['action_id'].eq(Action['id']),
                                                       ActionProperty['type_id'].eq(ActionPropertyType['id']),
                                                       ActionProperty['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(ActionProperty_OrgStructure, ActionProperty_OrgStructure['id'].eq(ActionProperty['id']))

    queryTable = queryTable.leftJoin(ResultAPT, [ResultAPT['name'].eq(u'Исход госпитализации'),
                                                 ResultAPT['actionType_id'].eq(ActionType['id']),
                                                 ResultAPT['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(ResultAP, [ResultAP['action_id'].eq(Action['id']),
                                                ResultAP['type_id'].eq(ResultAPT['id']),
                                                ResultAP['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(ResultAPS, ResultAPS['id'].eq(ResultAP['id']))

    queryTable = queryTable.innerJoin(ReceivedAT, [ReceivedAT['flatCode'].eq('received'),
                                                   ReceivedAT['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(Received, [Received['actionType_id'].eq(ReceivedAT['id']),
                                                 Received['event_id'].eq(Event['id']),
                                                 Received['deleted'].eq(0)])

    queryTable = queryTable.leftJoin(Finance, Finance['id'].eq(Received['finance_id']))

    cols = [
        ActionProperty_OrgStructure['value'].alias('orgStructureId'),
        ResultAPS['value'].alias('result'),
        Finance['code'].alias('financeCode'),
        'sum(datediff({endDate}, {begDate})) AS bedDays'.format(begDate=Received['begDate'], endDate=Action['begDate']),
        'count({item}) AS leaved'.format(item=ActionProperty['id'])
    ]

    cond = [
        ActionType['flatCode'].eq('leaved'),
        ActionType['deleted'].eq(0),
        Action['begDate'].datetimeGe(begDateTime),
        Action['begDate'].datetimeLt(endDateTime)
    ]

    if orgStructureIds:
        cond.append(ActionProperty_OrgStructure['value'].inlist(orgStructureIds))

    group = [
        'orgStructureId',
        'result',
        'financeCode'
    ]

    stmt = db.selectStmt(queryTable, cols, cond, group=group)
    return db.query(stmt)


class CReportMovingB36MonthlySetupDialog(CDialogBase, Ui_ReportMovingB36MonthlySetupDialog):

    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)


    def setTitle(self, title):
        self.setWindowTitle(title)


    def params(self):
        return {
            'begDate': self.edtBegDate.date(),
            'endDate': self.edtEndDate.date(),
            'begTime': self.edtBegTime.time()
        }


    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.edtBegTime.setTime(params.get('begTime', QtCore.QTime()))


class CReportMovingB36Monthly(CReport):
    u"""
        Учёт больных и коечного фонда ГКБ №36
        Территориальная принадлежность: Москва
        Объект: МСК Б36
    """

    def __init__(self, parent=None):
        CReport.__init__(self, parent)
        self.setTitle(u'Учёт больных и коечного фонда Городской Клинической Больницы №36')

        self.db = QtGui.qApp.db
        self.tableOrgStructure = self.db.table('OrgStructure')
        self.tableOSHB = self.db.table('OrgStructure_HospitalBed')

    def getSetupDialog(self, parent):
        result = CReportMovingB36MonthlySetupDialog(parent)
        result.setTitle(self.title())
        return result


    def getPageFormat(self):
        return CPageFormat(pageSize=CPageFormat.A3, orientation=CPageFormat.Landscape, leftMargin=0, topMargin=0, rightMargin=0, bottomMargin=0)


    def createTable(self, cursor, charFormat):
        keyColumnWidth = 10.0
        keyColumn = ('%.4f%%' % keyColumnWidth, [u'Отделение', u''], CReportBase.AlignLeft)
        columnDescr = [
            [u'Кол-во коек', u''],
            [u'Состояло на нач. суток', u''],
            [u'Поступило', u'всего'],
            [u'', u'в т.ч. иног.'],
            [u'КАНАЛЫ ГОСПИТАЛИЗАЦИИ', u'Скорая / иног.'],
            # [u'', u'Филиал / иног.'],
            [u'', u'План / иног.'],
            [u'', u'Самотек / иног.'],
            # [u'', u'РГВ / иног.'],
            [u'', u'ДМС / иног.'],
            [u'', u'ПМУ / иног.'],
            # [u'', u'Деп здр. / иног.'],
            # [u'', u'Переводы / иног.'],
            [u'', u'РВК / иног.'],
            [u'Перевод', u'из др. отд.'],
            [u'', u'в др. отд.'],
            [u'Выписано всего', u''],
            [u'Выписано в др. стац.', u''],
            [u'Умерло', u''],
            [u'Состоит на конец суток', u''],
            [u'Транспортабельность', u'Амбулаторн.'],
            [u'', u'Сидяч.'],
            [u'', u'Лежач.'],
            [u'', u'Нетранспорт.'],
            [u'Койко-дни', u''],
            [u'ИВЛ', u''],
            [u'Кол-во незанятых коек', u''],
            # [u'Кювезы', u''],
            [u'УВОВ, ИОВ, герои', u''],
            # [u'Катетер 1', u''],
            # [u'Катетер 2', u''],
            # [u'Травма, гололед', u''],
            # [u'Иностранцы', u''],
            # [u'Пострадавшие ЧС', u''], CReportBase.AlignCenter)
        ]
        columnWidth = '%.4f%%' % ((100.0 - keyColumnWidth) / len(columnDescr))
        tableColumns = [keyColumn] + [(columnWidth, descr, CReportBase.AlignCenter) for descr in columnDescr]
        table = createTable(cursor, tableColumns, charFormat=charFormat) #, cellPadding=1, cellSpacing=0)

        for col in range(3) + range(13, 17) + range(21, 25):
            table.mergeCells(0, col, 2, 1)
        table.mergeCells(0, 3, 1, 2)
        table.mergeCells(0, 5, 1, 6)
        table.mergeCells(0, 11, 1, 2)
        table.mergeCells(0, 17, 1, 4)

        return table


    def getOrgStructures(self, profileId=None):
        db = QtGui.qApp.db
        OrgStructure = db.table('OrgStructure')
        cols = [
            OrgStructure['id'],
            OrgStructure['code'],
            OrgStructure['type']
        ]
        cond = [
            OrgStructure['deleted'].eq(0)
        ]
        if profileId:
            OSHB = db.table('OrgStructure_HospitalBed')
            cond.extend([
                OrgStructure['id'].inlist(getOrgStructureDescendants(profileId)),
                db.existsStmt(OSHB, [OSHB['master_id'].eq(OrgStructure['id']),
                                     OSHB['isPermanent'].eq(1)]),
                OrgStructure['infisCode'].ne(u'')
            ])
        else:
            cond.extend([
                OrgStructure['parent_id'].isNull(),
                OrgStructure['deleted'].eq(0)
            ])
        return dict([(forceRef(rec.value('id')), {'code': forceString(rec.value('code')), 'type': forceInt(rec.value('type'))})
                     for rec in self.db.getRecordList(OrgStructure, cols, cond)])


    def build(self, params):
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        begTime = params.get('begTime', QtCore.QTime())

        begDateTime = QtCore.QDateTime(begDate, begTime)
        endDateTime = QtCore.QDateTime(endDate, begTime)

        fontSizeHeader = 8
        fontSize = 7
        charFormatHeader = CReportBase.TableHeader
        charFormatHeader.setFontPointSize(fontSizeHeader)
        charFormatBody = CReportBase.TableBody
        charFormatBody.setFontPointSize(fontSize)
        charFormatBodyBold = CReportBase.TableBody
        charFormatBodyBold.setFontWeight(QtGui.QFont.Bold)
        charFormatBodyBold.setFontPointSize(fontSize)

        doc = QtGui.QTextDocument()
        bf = QtGui.QTextBlockFormat()
        bf.setAlignment(QtCore.Qt.AlignCenter)
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(charFormatHeader)
        cursor.setBlockFormat(bf)
        cursor.insertText(self.title().upper() + u' c %02d.%02d.%d г. по %02d.%02d.%d г.' % (begDate.day(), begDate.month(), begDate.year(), endDate.day(), endDate.month(), endDate.year()))
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()

        table = self.createTable(cursor, charFormatBodyBold)

        orgStructuresByProfile = {}
        for profileId, profile in self.getOrgStructures().iteritems():
            orgStructures = self.getOrgStructures(profileId)
            if orgStructures:
                orgStructuresByProfile[profileId] = {'code': profile['code'], 'orgStructures': orgStructures}

        orgStructureIds = reduce(lambda x,y: x+y, [profileId['orgStructures'].keys() for profileId in orgStructuresByProfile.values()])

        columnNames = [
            'beds', 'moving',
            'received', 'receivedNonMoscow',
            'byEmergency', 'byEmergencyNonMoscow',
            # 'byBranch', 'byBranchNonMoscow',
            'isUrgent', 'isUrgentNonMoscow',
            'byHimself', 'byHimselfNonMoscow',
            # 'byRGV', 'byRGVNonMoscow',
            'byDMS', 'byDMSNonMoscow',
            'byPMU', 'byPMUNonMoscow',
            # 'byDepartment', 'byDepartmentNonMoscow',
            # 'byMoving', 'byMovingNonMoscow',
            'byRVK', 'byRVKNonMoscow',
            'movingInto', 'movingFrom',
            'leavedTotal', 'leavedToOtherOrg', 'leavedDeath',
            'inHospital',
            'transp1', 'transp2', 'transp3', 'transp4',
            'bedDays',
            'ALV',
            'freeBeds',
            # 'incubators',
            'veterans',
            # 'catheter1',
            # 'catheter2',
            # 'trauma',
            # 'foreigners',
            # 'affected'
        ]
        columnIndex = dict([(name, id) for id, name in enumerate(columnNames)])
        columnWidth = [1] * 4 + [2] * 6 + [1] * 14
        columnOffset = [sum(columnWidth[:i]) for i in xrange(len(columnWidth))]

        deliveredByColumns = ('byEmergency', 'byHimself', 'byDMS', 'byPMU', 'byRVK')
        deliveredByIndex = dict([(index + 1, columnIndex[name]) for index, name in enumerate(deliveredByColumns)])

        resultColumns = {
            u'умер': columnIndex['leavedDeath'],
            u'переведен в другой стационар': columnIndex['leavedToOtherOrg']
        }

        def getEmptyDataRow():
            return [0] * sum(columnWidth)

        reportData = {}
        for orgStructureId in orgStructureIds:
            reportData[orgStructureId] = getEmptyDataRow()

        financeCodeDMS = '3'
        nonBudgetFinanceCodes = ('3', '4', '5') # ДМС, ПМУ, целевой
        reportFinanceData = {}
        for financeCode in nonBudgetFinanceCodes:
            reportFinanceData[financeCode] = getEmptyDataRow()

        def processQuery(processRecord):
            def wrapper(queryType, query):
                self.addQueryText(forceString(query.lastQuery()), queryDesc=queryType)
                while query.next():
                    record = query.record()
                    processRecord(record)
            return wrapper

        @processQuery
        def processBeds(record):
            orgStructureId = forceRef(record.value('orgStructureId'))
            beds = forceInt(record.value('beds'))

            reportData[orgStructureId][columnIndex['beds']] = beds

        @processQuery
        def processMoving(record):
            orgStructureId = forceRef(record.value('orgStructureId'))
            financeCode = forceString(record.value('financeCode'))
            moving = forceInt(record.value('moving'))

            reportData[orgStructureId][columnIndex['moving']] += moving

            if financeCode in nonBudgetFinanceCodes:
                reportFinanceData[financeCode][columnIndex['moving']] += moving


        @processQuery
        def processReceived(record):
            orgStructureId = forceRef(record.value('orgStructureId'))
            financeCode = forceString(record.value('financeCode'))
            isUrgent = forceBool(record.value('isUrgent'))
            deliveredBy = forceInt(record.value('deliveredBy'))
            isMoscowResident = forceBool(record.value('isMoscowResident'))
            received = forceInt(record.value('received'))
            veterans = forceInt(record.value('veterans'))

            dataRow = reportData[orgStructureId]

            dataRow[columnIndex['received']] += received
            if not isMoscowResident:
                dataRow[columnIndex['receivedNonMoscow']] += received

            if isUrgent:
                dataRow[columnIndex['isUrgent']] += received
                if not isMoscowResident:
                    dataRow[columnIndex['isUrgentNonMoscow']] += received

            if deliveredBy:
                dataRow[deliveredByIndex[deliveredBy]] += received
                if not isMoscowResident:
                    dataRow[deliveredByIndex[deliveredBy]] += received

            dataRow[columnIndex['veterans']] += veterans

            if financeCode in nonBudgetFinanceCodes:
                financeDataRow = reportFinanceData[financeCode]

                financeDataRow[columnIndex['received']] += received
                if not isMoscowResident:
                    financeDataRow[columnIndex['receivedNonMoscow']] += received

                if isUrgent:
                    financeDataRow[columnIndex['isUrgent']] += received
                    if not isMoscowResident:
                        financeDataRow[columnIndex['isUrgentNonMoscow']] += received

                if deliveredBy:
                    financeDataRow[deliveredByIndex[deliveredBy]] += received
                    if not isMoscowResident:
                        financeDataRow[deliveredByIndex[deliveredBy]] += received

                financeDataRow[columnIndex['veterans']] += veterans


        @processQuery
        def processMovingInto(record):
            orgStructureId = forceRef(record.value('orgStructureId'))
            financeCode = forceString(record.value('financeCode'))
            movingInto = forceInt(record.value('movingInto'))

            reportData[orgStructureId][columnIndex['movingInto']] += movingInto
            if financeCode in nonBudgetFinanceCodes:
                reportFinanceData[financeCode][columnIndex['movingInto']] += movingInto

        @processQuery
        def processMovingFrom(record):
            orgStructureId = forceRef(record.value('orgStructureId'))
            financeCode = forceString(record.value('financeCode'))
            movingFrom = forceInt(record.value('movingFrom'))

            reportData[orgStructureId][columnIndex['movingFrom']] += movingFrom
            if financeCode in nonBudgetFinanceCodes:
                reportFinanceData[financeCode][columnIndex['movingFrom']] += movingFrom

        @processQuery
        def processLeaved(record):
            orgStructureId = forceRef(record.value('orgStructureId'))
            financeCode = forceString(record.value('financeCode'))
            result = forceString(record.value('result'))
            bedDays = forceInt(record.value('bedDays'))
            leaved = forceInt(record.value('leaved'))

            reportData[orgStructureId][columnIndex['leavedTotal']] += leaved
            reportData[orgStructureId][columnIndex['bedDays']] += bedDays

            if financeCode in nonBudgetFinanceCodes:
                reportFinanceData[financeCode][columnIndex['leavedTotal']] += leaved
                reportFinanceData[financeCode][columnIndex['bedDays']] += bedDays

            if result in resultColumns:
                col = resultColumns[result]
                reportData[orgStructureId][col] += leaved
                if financeCode in nonBudgetFinanceCodes:
                    reportFinanceData[financeCode][col] += leaved

        processBeds(u'Койки', selectHospitalBeds(orgStructureIds))
        processMoving(u'Состояло', selectMoving(begDateTime, orgStructureIds))
        processReceived(u'Поступило', selectReceived(begDateTime, endDateTime, orgStructureIds))
        processMovingInto(u'Переводы в отделение', selectMovingInto(begDateTime, endDateTime, orgStructureIds))
        processMovingFrom(u'Переводы из отделения', selectMovingFrom(begDateTime, endDateTime, orgStructureIds))
        processLeaved(u'Выписано', selectLeaved(begDateTime, endDateTime, orgStructureIds))

        for row in reportData.itervalues():
            beds = row[columnIndex['beds']]
            moving = row[columnIndex['moving']]
            received = row[columnIndex['received']]
            movingInto = row[columnIndex['movingInto']]
            movingFrom = row[columnIndex['movingFrom']]
            leavedTotal = row[columnIndex['leavedTotal']]

            inHospital = moving + received + movingInto - movingFrom - leavedTotal
            freeBeds = beds - inHospital

            row[columnIndex['inHospital']] = inHospital
            row[columnIndex['freeBeds']] = freeBeds

        for row in reportFinanceData.itervalues():
            beds = row[columnIndex['beds']]
            moving = row[columnIndex['moving']]
            received = row[columnIndex['received']]
            movingInto = row[columnIndex['movingInto']]
            movingFrom = row[columnIndex['movingFrom']]
            leavedTotal = row[columnIndex['leavedTotal']]

            inHospital = moving + received + movingInto - movingFrom - leavedTotal
            freeBeds = beds - inHospital

            row[columnIndex['inHospital']] = inHospital
            row[columnIndex['freeBeds']] = freeBeds


        def printRow(name, dataRow, charFormat=charFormatBody):
            def formatCell(cnt):
                return cnt if cnt > 0 else '-'

            def formatCell2(total, foreign):
                return '%s/%s' % (formatCell(total), formatCell(foreign))

            i = table.addRow()
            table.setText(i, 0, name, charFormat=charFormat)
            for j, w in enumerate(columnWidth):
                col = columnOffset[j]
                text = formatCell2(dataRow[col], dataRow[col + 1]) if w == 2 else formatCell(dataRow[col])
                table.setText(i, j + 1, text, charFormat=charFormat)

        def processProfile(profile):
            totalByProfile = []
            orgStructures = profile['orgStructures']
            for orgStructureId in sorted(orgStructures.keys(), key=lambda id: orgStructures[id]):
                row = reportData[orgStructureId]
                totalByProfile.append(row)
                printRow(orgStructures[orgStructureId]['code'], row)
            total = [sum(data) for data in zip(*totalByProfile)]
            printRow(profile['code'], total, charFormat=charFormatBodyBold)
            return total

        totalByHospital = []
        for profileId in sorted(orgStructuresByProfile.keys(), key=lambda id: orgStructuresByProfile[id]['code']):
            profileTotal = processProfile(orgStructuresByProfile[profileId])
            totalByHospital.append(profileTotal)

        # printRow(u'Стационар', [sum(data) for data in zip(*totalByHospital)], charFormat=charFormatBodyBold)

        # accoucherTotal = processProfile(accoucherProfile)
        # totalByHospital.append(accoucherTotal)

        printRow(u'БОЛЬНИЦА', [sum(data) for data in zip(*totalByHospital)], charFormat=charFormatBodyBold)

        # processProfile(reanimationProfile)

        printRow(u'Внебюджет', [sum(data) for data in zip(*reportFinanceData.itervalues())])
        printRow(u'в т.ч. ДМС', reportFinanceData[financeCodeDMS])

        # for orgStructureName, orgStructureId in childOrgStructures:
        #     printRow(orgStructureName, reportData[orgStructureId])

        return doc


def main():
    import sys
    from s11main import CS11mainApp
    from library.database import connectDataBaseByInfo

    app = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtGui.qApp = app
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    QtGui.qApp.currentOrgId = lambda: 386271
    QtGui.qApp.currentOrgStructureId = lambda: 34

    QtGui.qApp.db = connectDataBaseByInfo({
        'driverName' :      'mysql',
        'host' :            'mos36',
        'port' :            3306,
        'database' :        's11',
        'user':             'dbuser',
        'password':         'dbpassword',
        'connectionName':   'vista-med',
        'compressData' :    True,
        'afterConnectFunc': None
    })

    CReportMovingB36Monthly(None).exec_()


if __name__ == '__main__':
    main()