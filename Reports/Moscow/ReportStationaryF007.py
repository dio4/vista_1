# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Orgs.Utils import getOrgStructureDescendants
from Reports.Report import CReportOrientation
from Reports.ReportBase import CReportBase, createTable
from Reports.ReportView import CPageFormat, CReportViewOrientation
from Ui_ReportStationaryF007SetupDialog import Ui_ReportStationaryF007SetupDialog
from library.DialogBase import CDialogBase
from library.Utils import forceInt, forceRef, forceString, formatShortName


def selectClientData(eventIdList):
    db = QtGui.qApp.db
    Client = db.table('Client')
    Event = db.table('Event')

    queryTable = Event.leftJoin(Client, Client['id'].eq(Event['client_id']))
    cols = [
        Event['id'].alias('id'),
        Client['lastName'].alias('lastName'),
        Client['firstName'].alias('firstName'),
        Client['patrName'].alias('patrName')
    ]
    cond = [
        Event['id'].inlist(eventIdList)
    ]

    return db.iterRecordList(queryTable, cols, cond)


def selectData(date, begTime, orgStructureId, bedSchedule, bedProfile, detailOrgStructure):
    db = QtGui.qApp.db

    begDateTime = QtCore.QDateTime(date.addDays(-1), begTime)
    endDateTime = QtCore.QDateTime(date, begTime)

    def mainTableStmt():
        OrgStructure = db.table('OrgStructure')
        OSHB = db.table('OrgStructure_HospitalBed').alias('OSHB')
        HBI = db.table('HospitalBed_Involute').alias('HBI')

        table = OrgStructure.innerJoin(OSHB, OSHB['master_id'].eq(OrgStructure['id']))
        table = table.leftJoin(HBI, HBI['master_id'].eq(OSHB['id']))
        cols = [
            OrgStructure['id'].alias('id'),
            OrgStructure['infisCode'].alias('code'),
            db.count(OSHB['id']).alias('beds'),
            db.countIf(db.joinAnd([OSHB['sex'].eq(1), OSHB['isPermanent'].eq(1)]), OSHB['id']).alias('menBeds'),
            db.countIf(db.joinAnd([OSHB['sex'].eq(2), OSHB['isPermanent'].eq(1)]), OSHB['id']).alias('womenBeds'),
            db.countIf(OSHB['isPermanent'].eq(1), OSHB['id']).alias('permanentBeds'),
            db.countIf(HBI['involuteType'].eq(1), OSHB['id']).alias('involuteBeds'),
        ]
        cond = [
            OrgStructure['deleted'].eq(0),
            OrgStructure['infisCode'].ne(u'')
        ]
        if not orgStructureId is None:
            cond.append(OrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)))
        return db.selectStmt(table, cols, cond, group=OrgStructure['id'])

    def subQueryStmt(queryType):
        subQueryTypes = {
            'moving'         : ('moving', u'Отделение пребывания'),
            'received'       : ('received', u'Направлен в отделение'),
            'movingInto'     : ('moving', u'Переведен в отделение'),
            'movingFrom'     : ('moving', u'Переведен из отделения'),
            'leaved'         : ('leaved', u'Отделение'),
            'reanimation'    : ('reanimation', u'Отделение пребывания'),
            'reanimationInto': ('reanimation', u'Переведен в отделение'),
            'reanimationFrom': ('reanimation', u'Переведен из отделения')
        }
        actionTypeFlatCode, actionPropertyName = subQueryTypes[queryType]

        tableAction = db.table('Action')
        tableActionType = db.table('ActionType')
        tableAP = db.table('ActionProperty')
        tableAPT = db.table('ActionPropertyType')
        tableAPOS = db.table('ActionProperty_OrgStructure')
        tableAPS = db.table('ActionProperty_String')
        Address = db.table('Address')
        AddressHouse = db.table('AddressHouse')
        Client = db.table('Client')
        ClientAddress = db.table('ClientAddress')
        Event = db.table('Event')
        Finance = db.table('rbFinance')
        OrgStructure = db.table('OrgStructure')

        cond = [
            tableActionType['flatCode'].eq(actionTypeFlatCode),
            tableActionType['deleted'].eq(0)
        ]

        queryTable = tableActionType.innerJoin(tableAction, [tableAction['actionType_id'].eq(tableActionType['id']), tableAction['deleted'].eq(0)])
        queryTable = queryTable.innerJoin(Event, [Event['id'].eq(tableAction['event_id']), Event['deleted'].eq(0)])

        queryTable = queryTable.innerJoin(Client, Client['id'].eq(Event['client_id']))

        queryTable = queryTable.innerJoin(tableAPT, [tableAPT['actionType_id'].eq(tableActionType['id']),
                                                     tableAPT['name'].eq(actionPropertyName),
                                                     tableAPT['deleted'].eq(0)])
        queryTable = queryTable.innerJoin(tableAP, [tableAP['action_id'].eq(tableAction['id']),
                                                    tableAP['type_id'].eq(tableAPT['id']),
                                                    tableAP['deleted'].eq(0)])
        queryTable = queryTable.innerJoin(tableAPOS, tableAPOS['id'].eq(tableAP['id']))
        queryTable = queryTable.innerJoin(OrgStructure, OrgStructure['id'].eq(tableAPOS['value']))

        cols = [
            # Finance['id'] if orgStructureId else ActionPropertyOrgStructure['value'].alias('id'),
            tableAPOS['value'].alias('id'),
            db.count(tableAP['id']).alias(queryType),
            db.countIf(Client['sex'].eq(1), tableAP['id']).alias('men'),
            db.countIf(Client['sex'].eq(2), tableAP['id']).alias('women'),
        ]

        group = [
            tableAPOS['value']
            # Finance['id'] if orgStructureId else ActionPropertyOrgStructure['value']
        ]

        if queryType == 'moving':
            queryTable = queryTable.innerJoin(Finance, Finance['id'].eq(tableAction['finance_id']))
            cond.extend([
                tableAction['begDate'].datetimeLt(begDateTime),
                db.joinOr([tableAction['endDate'].datetimeGe(begDateTime),
                           tableAction['endDate'].isNull()])
            ])

        elif queryType == 'received':
            queryTable = queryTable.leftJoin(ClientAddress, [ClientAddress['client_id'].eq(Client['id']),
                                                             ClientAddress['id'].eq(db.func.getClientRegAddressId(Client['id'])),
                                                             ClientAddress['deleted'].eq(0)])
            queryTable = queryTable.leftJoin(Address, [Address['id'].eq(ClientAddress['address_id']),
                                                       Address['deleted'].eq(0)])
            queryTable = queryTable.leftJoin(AddressHouse, [AddressHouse['id'].eq(Address['house_id']),
                                                            AddressHouse['deleted'].eq(0)])

            isVillagerCond = db.joinOr([ClientAddress['isVillager'].eq(1),
                                        db.func.isClientVillager(Client['id']).eq(1)])
            cols.extend([
                db.group_concat(Event['id']).alias('events'),
                db.countIf(isVillagerCond, tableAP['id']).alias('receivedVillager'),
                db.countIf(db.func.age(Client['birthDate'], tableAction['begDate']) <= 17, tableAP['id']).alias('receivedChildren'),
                db.countIf(db.func.age(Client['birthDate'], tableAction['begDate']) >= 60, tableAP['id']).alias('receivedElder')
            ])

            cond.extend([
                tableAction['begDate'].datetimeGe(begDateTime),
                tableAction['begDate'].datetimeLt(endDateTime)
            ])

        elif queryType == 'movingInto':
            cols.extend([
                db.group_concat(Event['id']).alias('events')
            ])
            cond.extend([
                tableAction['endDate'].datetimeGe(begDateTime),
                tableAction['endDate'].datetimeLt(endDateTime)
            ])

        elif queryType == 'movingFrom':
            cols.extend([
                db.group_concat(Event['id']).alias('events')
            ])
            cond.extend([
                tableAction['begDate'].datetimeGe(begDateTime),
                tableAction['begDate'].datetimeLt(endDateTime)
            ])

        elif queryType == 'leaved':
            resultPropertyName = u'Исход госпитализации'
            resultAP = tableAP.alias('ResultAP')
            resultAPS = tableAPS.alias('ResultAPS')
            resultAPT = tableAPT.alias('ResultAPT')

            queryTable = queryTable.leftJoin(resultAPT, [resultAPT['name'].eq(resultPropertyName),
                                                         resultAPT['actionType_id'].eq(tableActionType['id']),
                                                         resultAPT['deleted'].eq(0)])
            queryTable = queryTable.leftJoin(resultAP, [resultAP['action_id'].eq(tableAction['id']),
                                                        resultAP['type_id'].eq(resultAPT['id']),
                                                        resultAP['deleted'].eq(0)])
            queryTable = queryTable.leftJoin(resultAPS, resultAPS['id'].eq(resultAP['id']))

            deathCond = resultAPS['value'].eq(u'умер')
            toHomeCond = resultAPS['value'].eq(u'выписан')
            toOtherOrgCond = resultAPS['value'].eq(u'переведен в другой стационар')

            cols.extend([
                db.countIf(deathCond, tableAP['id']).alias('leavedDeath'),
                db.countIf(toOtherOrgCond, tableAP['id']).alias('leavedToOtherOrg'),
                db.group_concat(db.if_(deathCond, Event['id'], db.NULL)).alias('deathEvents'),
                db.group_concat(db.if_(toHomeCond, Event['id'], db.NULL)).alias('toHomeEvents'),
                db.group_concat(db.if_(toOtherOrgCond, Event['id'], db.NULL)).alias('toOtherOrgEvents')
            ])
            cond.extend([
                tableAction['begDate'].datetimeGe(begDateTime),
                tableAction['begDate'].datetimeLt(endDateTime)
            ])

        return db.selectStmt(queryTable, cols, cond, group=group)

    mainTable = db.subQueryTable(mainTableStmt(), 'mainTable')
    moving = db.subQueryTable(subQueryStmt('moving'), 'moving')
    received = db.subQueryTable(subQueryStmt('received'), 'received')
    movingInto = db.subQueryTable(subQueryStmt('movingInto'), 'movingInto')
    movingFrom = db.subQueryTable(subQueryStmt('movingFrom'), 'movingFrom')
    leaved = db.subQueryTable(subQueryStmt('leaved'), 'leaved')

    queryTable = mainTable.leftJoin(moving, moving['id'].eq(mainTable['id']))
    queryTable = queryTable.leftJoin(received, received['id'].eq(mainTable['id']))
    queryTable = queryTable.leftJoin(movingInto, movingInto['id'].eq(mainTable['id']))
    queryTable = queryTable.leftJoin(movingFrom, movingFrom['id'].eq(mainTable['id']))
    queryTable = queryTable.leftJoin(leaved, leaved['id'].eq(mainTable['id']))

    cols = [
        mainTable['id'].alias('id'),
        mainTable['code'].alias('code'),
        mainTable['beds'].alias('beds'),
        mainTable['menBeds'].alias('menBeds'),
        mainTable['womenBeds'].alias('womenBeds'),
        mainTable['permanentBeds'].alias('permanentBeds'),
        mainTable['involuteBeds'].alias('involuteBeds'),
        moving['moving'].alias('moving'),
        received['received'].alias('received'),
        received['events'].alias('receivedEvents'),
        movingInto['movingInto'].alias('movingInto'),
        movingInto['events'].alias('movingIntoEvents'),
        movingFrom['movingFrom'].alias('movingFrom'),
        movingFrom['events'].alias('movingFromEvents'),
        leaved['leaved'].alias('leaved'),
        leaved['toHomeEvents'].alias('toHomeEvents'),
        leaved['toOtherOrgEvents'].alias('toOtherOrgEvents'),
        leaved['deathEvents'].alias('deathEvents'),
        (moving['men'] + received['men'] + movingInto['men'] - movingFrom['men'] - leaved['men']).alias('men'),
        (moving['women'] + received['women'] + movingInto['women'] - movingFrom['women'] - leaved['women']).alias('women'),
    ]

    return db.query(db.selectStmt(queryTable, cols))


class CReportStationaryF007SetupDialog(CDialogBase, Ui_ReportStationaryF007SetupDialog):
    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbBedProfile.setTable('rbHospitalBedProfile', True)
        # self.chkDetailOrgStructure.setVisible(False)
        # self.chkIsHideBeds.setVisible(False)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtDate.setDate(params.get('date', QtCore.QDate.currentDate()))
        self.edtBegTime.setTime(params.get('begTime', QtCore.QTime()))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbBedSchedule.setCurrentIndex(params.get('bedSchedule', 0))
        self.cmbBedProfile.setValue(params.get('bedProfile', None))
        self.chkDetailOrgStructure.setChecked(params.get('detailOrgStructure', False))
        # self.chkIsHideBeds.setChecked(params.get('isHideBeds', False))

    def params(self):
        return {
            'date'              : self.edtDate.date(),
            'begTime'           : self.edtBegTime.time(),
            'orgStructureId'    : self.cmbOrgStructure.value(),
            'bedSchedule'       : self.cmbBedSchedule.currentIndex(),
            'bedProfile'        : self.cmbBedProfile.value(),
            'detailOrgStructure': self.chkDetailOrgStructure.isChecked(),
            # 'isHideBeds': self.chkIsHideBeds.isChecked()
        }

    @QtCore.pyqtSlot(bool)
    def on_chkIsHideBeds_toggled(self, checked):
        self.chkDetailOrgStructure.setEnabled(not checked)
        if checked:
            self.chkDetailOrgStructure.setChecked(checked)


class CReportStationaryF007(CReportOrientation):
    DefaultBegTime = QtCore.QTime(6, 0)

    def __init__(self, parent=None):
        CReportOrientation.__init__(self, parent, QtGui.QPrinter.Landscape)
        self.setTitle(u'ЛИСТОК ежедневного учета движения больных и коечного фонда стационара круглосуточного пребывания, дневного стационара при больничном учреждении')

    def getSetupDialog(self, parent):
        result = CReportStationaryF007SetupDialog(parent)
        result.setTitle(self.title())
        return result

    def getPageFormat(self):
        return CPageFormat(pageSize=CPageFormat.A4, orientation=CPageFormat.Landscape, leftMargin=0, topMargin=0, rightMargin=0, bottomMargin=0)

    @staticmethod
    def createHeader(cursor, charFormat, orgStructureId=None):
        db = QtGui.qApp.db

        orgId = QtGui.qApp.currentOrgId()
        orgName = forceString(db.translate('Organisation', 'id', orgId, 'fullName')) if orgId else u'_' * 50 + u'\nнаименование учреждения'

        orgStructureName = forceString(db.translate('OrgStructure', 'id', orgStructureId, 'name')) if orgStructureId else u'_' * 50

        headerLeft = u'Министерство здравоохранения\n' + \
                     u'Российской Федерации\n\n' + \
                     orgName
        headerRight = u'Медицинская документация\n' \
                      u'Форма N 007/у-02\n' \
                      u'Утверждена приказом Минздрава России\n' \
                      u'от 30.12.2002 N 413'
        headerColumns = [
            ('30%', [''], CReportBase.AlignCenter),
            ('40%', [''], CReportBase.AlignCenter),
            ('30%', [''], CReportBase.AlignLeft),
        ]
        headerTable = createTable(cursor, headerColumns, border=0, cellPadding=1, cellSpacing=0, charFormat=charFormat)
        headerTable.setText(0, 0, headerLeft)
        headerTable.setText(0, 2, headerRight)
        cursor.movePosition(QtGui.QTextCursor.End)

        titleCharFormat = charFormat
        titleCharFormat.setFontWeight(QtGui.QFont.Bold)

        cursor.insertBlock()
        cursor.setBlockFormat(CReportBase.AlignCenter)
        cursor.setCharFormat(titleCharFormat)
        cursor.insertText(u'ЛИСТОК\n'
                          u'ежедневного учета движения больных и коечного фонда\n' + \
                          u'стационара круглосуточного пребывания, дневного стационара\n' + \
                          u'при больничном учреждении\n' + \
                          u'(подчеркнуть)\n' + \
                          orgStructureName + u'\n' + \
                          u'наименование отделения, профиля коек')
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()

    @staticmethod
    def createTable(cursor, charFormat):
        mainTableColumns = [
            ('10%', [u''], CReportBase.AlignLeft),
            ('4.5%', [u'Код'], CReportBase.AlignLeft),
            ('4.5%', [u'Фактически развернуто коек, включая койки, свернутые на ремонт'], CReportBase.AlignRight),
            ('4.5%', [u'В том числе коек, свернутых на ремонт'], CReportBase.AlignRight),
            ('4.5%', [u'Движение больных за истекшие сутки', u'состояло больных на начало истекших суток'], CReportBase.AlignRight),
            ('4.5%', [u'', u'поступило больных (без переведенных внутри больницы)', u'всего'], CReportBase.AlignRight),
            ('4.5%', [u'', u'', u'в т.ч. из дневного стационара'], CReportBase.AlignRight),
            ('4.5%', [u'', u'', u'из них (из гр. 6)', u'сельских жителей'], CReportBase.AlignRight),
            ('4.5%', [u'', u'', u'', u'0-17 лет'], CReportBase.AlignRight),
            ('4.5%', [u'', u'', u'', u'60 лет и старше'], CReportBase.AlignRight),
            ('4.5%', [u'', u'переведено больных внутри больницы', u'из других отделений'], CReportBase.AlignRight),
            ('4.5%', [u'', u'', u'в другие отделения'], CReportBase.AlignRight),
            ('4.5%', [u'', u'выписано больных', u'всего'], CReportBase.AlignRight),
            ('4.5%', [u'', u'', u'в т.ч.', u'переведенных в другие стационары'], CReportBase.AlignRight),
            ('4.5%', [u'', u'', u'', u'в круглосуточный стационар'], CReportBase.AlignRight),
            ('4.5%', [u'', u'', u'', u'в дневной стационар'], CReportBase.AlignRight),
            ('4.5%', [u'', u'умерло'], CReportBase.AlignRight),
            ('4.5%', [u'На начало текущего дня', u'состоит больных - всего'], CReportBase.AlignRight),
            ('4.5%', [u'', u'состоит матерей при больных детях'], CReportBase.AlignRight),
            ('4.5%', [u'', u'свободных мест', u'мужских'], CReportBase.AlignRight),
            ('4.5%', [u'', u'', u'женских'], CReportBase.AlignRight)
        ]
        mainTable = createTable(cursor, mainTableColumns, charFormat=charFormat)

        mainTable.mergeCells(0, 4, 1, 13)
        mainTable.mergeCells(0, 17, 1, 4)
        mainTable.mergeCells(1, 5, 1, 5)
        mainTable.mergeCells(1, 10, 1, 2)
        mainTable.mergeCells(1, 12, 1, 4)
        mainTable.mergeCells(1, 19, 1, 2)
        mainTable.mergeCells(2, 7, 1, 3)
        mainTable.mergeCells(2, 13, 1, 3)

        for col in xrange(4):
            mainTable.mergeCells(0, col, 4, 1)

        for col in [4, 16, 17, 18]:
            mainTable.mergeCells(1, col, 3, 1)

        for col in [5, 6, 10, 11, 12, 19, 20]:
            mainTable.mergeCells(2, col, 2, 1)

        i = mainTable.addRow()
        for col in xrange(len(mainTableColumns)):
            mainTable.setText(i, col, col + 1, blockFormat=CReportBase.AlignCenter)

        return mainTable

    @staticmethod
    def createClientsTable(cursor, charFormat):
        tableColumns = [
            ('15?', [u'Фамилия, и., о. поступивших'], CReportBase.AlignLeft),
            ('15?', [u'Фамилия, и., о. поступивших из круглосуточного стационара'], CReportBase.AlignLeft),
            ('15?', [u'Фамилия, и., о. выписанных'], CReportBase.AlignLeft),
            ('15?', [u'Фамилия, и., о. переведенных', u'в другие отделения данной больницы'], CReportBase.AlignLeft),
            ('15?', [u'', u'в другие стационары'], CReportBase.AlignLeft),
            ('15?', [u'Фамилия, и., о. умерших'], CReportBase.AlignLeft),
            ('15?', [u'Фамилия, и., о. больных, находящихся во временном отпуск'], CReportBase.AlignLeft),
        ]
        clientsTable = createTable(cursor, tableColumns, charFormat=charFormat)

        clientsTable.mergeCells(0, 3, 1, 2)
        for col in (0, 1, 2, 5, 6):
            clientsTable.mergeCells(0, col, 2, 1)

        i = clientsTable.addRow()
        for col in xrange(len(tableColumns)):
            clientsTable.setText(i, col, col + 1, blockFormat=CReportBase.AlignCenter)

        return clientsTable

    def reportLoop(self):
        params = self.getDefaultParams()
        while True:
            setupDialog = self.getSetupDialog(self.parent)
            setupDialog.setParams(params)
            if not setupDialog.exec_():
                break
            params = setupDialog.params()
            self.saveDefaultParams(params)
            try:
                QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                reportResult = self.build(params)
            finally:
                QtGui.qApp.restoreOverrideCursor()
            viewDialog = CReportViewOrientation(self.parent, self.orientation)
            if self.viewerGeometry:
                viewDialog.restoreGeometry(self.viewerGeometry)
            viewDialog.setWindowTitle(self.title())
            viewDialog.setRepeatButtonVisible()
            viewDialog.setText(reportResult)
            viewDialog.setQueryText(self.queryText())
            done = not viewDialog.exec_()
            self.viewerGeometry = viewDialog.saveGeometry()
            if done:
                break

    def createFooter(self, cursor, charFormat):
        cursor.insertBlock()
        cursor.setBlockFormat(CReportBase.AlignCenter)
        cursor.setCharFormat(charFormat)
        cursor.insertText(u'Подпись медицинской сестры ' + u'_' * 30)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()

    def build(self, params):
        date = params.get('date', QtCore.QDate())
        begTime = params.get('begTime', self.DefaultBegTime)
        orgStructureId = params.get('orgStructureId', None)
        bedSchedule = params.get('bedSchedule', 0)
        bedProfile = params.get('bedProfile', None)
        detailOrgStructure = params.get('detailOrgStructure', False)

        fontSizeHeader = 9
        fontSizeBody = 9
        charFormatHeader = QtGui.QTextCharFormat()
        charFormatHeader.setFontPointSize(fontSizeHeader)
        charFormatHeaderBold = QtGui.QTextCharFormat()
        charFormatHeaderBold.setFontPointSize(fontSizeHeader)
        charFormatHeaderBold.setFontWeight(QtGui.QFont.Bold)
        charFormatBody = QtGui.QTextCharFormat()
        charFormatBody.setFontPointSize(fontSizeBody)
        charFormatBodyBold = QtGui.QTextCharFormat()
        charFormatBodyBold.setFontWeight(QtGui.QFont.Bold)
        charFormatBodyBold.setFontPointSize(fontSizeBody)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        self.createHeader(cursor, charFormatHeader, orgStructureId)
        mainTable = self.createTable(cursor, charFormatBodyBold)

        query = selectData(date, begTime, orgStructureId, bedSchedule, bedProfile, detailOrgStructure)
        self.setQueryText(forceString(query.lastQuery()))

        receivedEvents = []
        movingIntoEvents = []
        movingFromEvents = []
        toHomeEvents = []
        toOtherOrgEvents = []
        deathEvents = []

        reportData = {}
        codes = {}

        while query.next():
            record = query.record()
            id = forceRef(record.value('id'))
            code = forceString(record.value('code'))
            menBeds = forceInt(record.value('menBeds'))
            womenBeds = forceInt(record.value('womenBeds'))
            permanentBeds = forceInt(record.value('permanentBeds'))
            involuteBeds = forceInt(record.value('involuteBeds'))
            moving = forceInt(record.value('moving'))
            received = forceInt(record.value('received'))
            receivedVillager = forceInt(record.value('receivedVillager'))
            receivedChildren = forceInt(record.value('receivedChildren'))
            receivedElder = forceInt(record.value('receivedElder'))
            movingInto = forceInt(record.value('movingInto'))
            movingFrom = forceInt(record.value('movingFrom'))
            leaved = forceInt(record.value('leaved'))
            leavedDeath = forceInt(record.value('leavedDeath'))
            leavedToOtherOrg = forceInt(record.value('leavedToOtherOrg'))
            men = forceInt(record.value('men'))
            women = forceInt(record.value('women'))

            inHospital = moving + received + movingInto - movingFrom - leaved
            freeBeds = permanentBeds - inHospital
            freeMenBeds = max(menBeds - men, 0)
            freeWomenBeds = max(womenBeds - women, 0)

            codes[id] = code
            reportData[id] = [
                permanentBeds,
                involuteBeds,
                moving,
                received,
                0,  # поступило из дневного стационара
                receivedVillager,
                receivedChildren,
                receivedElder,
                movingInto,
                movingFrom,
                leaved,
                leavedToOtherOrg,
                0,  # выписано в круглосуточный стационар
                0,  # выписано в дневной стационар
                leavedDeath,
                inHospital,
                0,  # состоит матерей при больных детях
                freeMenBeds,
                freeWomenBeds
            ]

            receivedEventsStr = forceString(record.value('receivedEvents'))
            if receivedEventsStr:
                receivedEvents.extend(map(int, receivedEventsStr.split(',')))

            movingIntoEventsStr = forceString(record.value('movingIntoEvents'))
            if movingIntoEventsStr:
                movingIntoEvents.extend(map(int, movingIntoEventsStr.split(',')))

            movingFromEventsStr = forceString(record.value('movingFromEvents'))
            if movingFromEventsStr:
                movingFromEvents.extend(map(int, movingFromEventsStr.split(',')))

            toHomeEventsStr = forceString(record.value('toHomeEvents'))
            if toHomeEventsStr:
                toHomeEvents.extend(map(int, toHomeEventsStr.split(',')))

            toOtherOrgEventsStr = forceString(record.value('toOtherOrgEvents'))
            if toOtherOrgEventsStr:
                toOtherOrgEvents.extend(map(int, toOtherOrgEventsStr.split(',')))

            deathEventsStr = forceString(record.value('deathEvents'))
            if deathEventsStr:
                deathEvents.extend(map(int, deathEventsStr.split(',')))

        movingEvents = list(set(movingIntoEvents + movingFromEvents))

        def printRow(name, row, charFormat=charFormatBody, firstCol=''):
            i = mainTable.addRow()
            mainTable.setText(i, 0, firstCol)
            mainTable.setText(i, 1, name)
            for j, data in enumerate(row):
                mainTable.setText(i, j + 2, data, charFormat=charFormat)

        orgStructureIdList = sorted(reportData.iterkeys(), key=lambda id: reportData[id][0])
        total = [sum(data) for data in zip(*reportData.itervalues())]
        printRow(u'', total, charFormat=charFormatBodyBold, firstCol=u'Всего')

        i = mainTable.addRow()
        mainTable.setText(i, 0, u'В том числе по койкам')

        for orgStructureId in orgStructureIdList:
            printRow(codes[orgStructureId], reportData[orgStructureId])

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        self.createFooter(cursor, charFormatHeaderBold)

        # PAGE 2

        blockFormat = QtGui.QTextBlockFormat()
        blockFormat.setPageBreakPolicy(QtGui.QTextBlockFormat.PageBreak_AlwaysAfter)
        cursor.insertBlock(blockFormat)

        events = list(set(receivedEvents + movingEvents + toHomeEvents + toOtherOrgEvents + deathEvents))

        clientsMap = {}
        for record in selectClientData(events):
            eventId = forceRef(record.value('id'))
            shortName = formatShortName(forceString(record.value('lastName')),
                                        forceString(record.value('firstName')),
                                        forceString(record.value('patrName')))
            clientsMap[eventId] = shortName

        cursor.insertBlock()
        clientsTable = self.createClientsTable(cursor, charFormatBodyBold)

        i = clientsTable.addRow()
        clientsTable.setText(i, 0, u'\n'.join(clientsMap[eventId] for eventId in receivedEvents))
        clientsTable.setText(i, 2, u'\n'.join(clientsMap[eventId] for eventId in movingEvents))
        clientsTable.setText(i, 3, u'\n'.join(clientsMap[eventId] for eventId in toHomeEvents))
        clientsTable.setText(i, 4, u'\n'.join(clientsMap[eventId] for eventId in toOtherOrgEvents))
        clientsTable.setText(i, 5, u'\n'.join(clientsMap[eventId] for eventId in deathEvents))

        return doc


# def main():
#     import sys
#     from s11main import CS11mainApp
#     from library.database import connectDataBaseByInfo
#
#     app = CS11mainApp(sys.argv, False, 'S11App.ini', False)
#     QtGui.qApp = app
#     QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))
#
#     QtGui.qApp.currentOrgId = lambda: 386271
#     QtGui.qApp.currentOrgStructureId = lambda: 34
#
#     QtGui.qApp.db = connectDataBaseByInfo({
#         'driverName'      : 'mysql',
#         'host'            : 'mos36',
#         'port'            : 3306,
#         'database'        : 's11',
#         'user'            : 'dbuser',
#         'password'        : 'dbpassword',
#         'connectionName'  : 'vista-med',
#         'compressData'    : True,
#         'afterConnectFunc': None
#     })
#
#     CReportStationaryF007(None).exec_()
#
#
# if __name__ == '__main__':
#     main()
