# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Events.Utils import getWorkEventTypeFilter
from Orgs.OrgStructComboBoxes import COrgStructureModel
from Orgs.Utils import getOrgStructureDescendants
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Ui_ReportF39Setup import Ui_ReportF39SetupDialog
from library.Utils import forceBool, forceDate, forceInt, forceRef, forceString, getVal, pyDate, formatName
from library.database import addDateInRange


def getPersonInfo(personId):
    if personId is None:
        return u'', u'', u''

    db = QtGui.qApp.db
    Person = db.table('Person')
    Post = db.table('rbPost')
    Speciality = db.table('rbSpeciality')

    queryTable = Person.leftJoin(Post, Post['id'].eq(Person['post_id']))
    queryTable = queryTable.leftJoin(Speciality, Speciality['id'].eq(Person['speciality_id']))
    cols = [
        Person['lastName'].alias('lastName'),
        Person['firstName'].alias('firstName'),
        Person['patrName'].alias('patrName'),
        Post['name'].alias('post'),
        Speciality['name'].alias('speciality')
    ]
    cond = [
        Person['id'].eq(personId)
    ]

    personRecord = db.getRecordEx(queryTable, cols, cond)

    if not personRecord is None:
        lastName = forceString(personRecord.value('lastName'))
        firstName = forceString(personRecord.value('firstName'))
        patrName = forceString(personRecord.value('patrName'))
        post = forceString(personRecord.value('post'))
        speciality = forceString(personRecord.value('speciality'))

        return formatName(lastName, firstName, patrName), post, speciality

    return u'', u'', u''

def selectData(begDate, endDate, eventPurposeId, eventTypes, orgStructureId, personId, rowGrouping, visitPayStatus, visitHospital, sex, ageFrom, ageTo, visitDisp, eventDate=None):
    db = QtGui.qApp.db
    Client = db.table('Client')
    Event = db.table('Event')
    EventType = db.table('EventType')
    EventKind = db.table('rbEventKind')
    EventGoal = db.table('rbEventGoal')
    Person = db.table('Person')
    Scene = db.table('rbScene')
    Visit = db.table('Visit')

    queryTable = Visit.leftJoin(Event, Event['id'].eq(Visit['event_id']))
    queryTable = queryTable.leftJoin(EventType, EventType['id'].eq(Event['eventType_id']))
    queryTable = queryTable.leftJoin(EventKind, EventKind['id'].eq(EventType['eventKind_id']))
    queryTable = queryTable.leftJoin(EventGoal, EventGoal['id'].eq(Event['goal_id']))
    queryTable = queryTable.leftJoin(Client, Client['id'].eq(Event['client_id']))
    queryTable = queryTable.leftJoin(Person, Person['id'].eq(Visit['person_id']))
    queryTable = queryTable.leftJoin(Scene, Scene['id'].eq(Visit['scene_id']))

    groupFields = {
        0: 'date(%s)' % Visit['date'].name(),
        1: Visit['person_id'].name(),
        2: Person['orgStructure_id'].name(),
        3: Person['speciality_id'].name(),
        4: Person['post_id'].name()
    }
    rowKey = groupFields[rowGrouping if rowGrouping in groupFields else 0]

    cols = [
        'count(*) AS cnt',
        '%s AS rowKey' % rowKey,
        'isClientVillager(%s) AS clientVillager' % Client['id'].name(),
        'if(%s = \'1\', 1, 0) AS atAmbulance' % Scene['code'].name(),
        'if(%s IN (\'2\', \'3\'), 1, 0) AS atHome' % Scene['code'].name(),
        EventGoal['regionalCode'].alias('eventGoalCode'),
        'age(%s, %s) AS clientAge' % (Client['birthDate'].name(), Visit['date'].name()),
        Visit['finance_id'].alias('financeId')
    ]

    cond = [
        Visit['deleted'].eq(0),
        Event['deleted'].eq(0),
        Client['deleted'].eq(0)
    ]
    addDateInRange(cond, Visit['date'], begDate, endDate)

    if eventDate:
        eventBegDatetime, eventEndDatetime = eventDate
        addDateInRange(cond, Event['createDatetime'], eventBegDatetime, eventEndDatetime)

    if not visitHospital:
        MedicalAidType = db.table('rbMedicalAidType')
        hospitalMAT_ids  = db.selectStmt(MedicalAidType, MedicalAidType['id'], MedicalAidType['code'].eq('7'))
        cond.append(db.joinOr([EventType['medicalAidType_id'].isNull(),
                               '%s NOT IN (%s)' % (EventType['medicalAidType_id'].name(), hospitalMAT_ids)]))

    if not visitDisp:
        cond.append(db.joinOr([EventKind['code'].notInlist([u'01', u'02', u'04']), EventKind['code'].isNull()]))

    if eventTypes:
        cond.append(Event['eventType_id'].inlist(eventTypes))
    elif eventPurposeId:
        cond.append(EventType['purpose_id'].eq(eventPurposeId))

    if personId:
        cond.append(Visit['person_id'].eq(personId))
    elif orgStructureId:
        cond.append(Person['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    else:
        cond.append(Person['org_id'].eq(QtGui.qApp.currentOrgId()))

    if sex:
        cond.append(Client['sex'].eq(sex))

    if ageFrom <= ageTo:
        cond.append('Visit.date >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)' % ageFrom)
        cond.append('Visit.date < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)' % (ageTo + 1))

    if visitPayStatus >= 0:
        cond.append('getPayCode(%s, %s) = %d' % (Visit['finance_id'].name(), Visit['payStatus'].name(), visitPayStatus))

    group = [
        rowKey,
        'clientVillager',
        'atAmbulance',
        'atHome',
        'eventGoalCode',
        'clientAge',
        Visit['finance_id']
    ]

    stmt = db.selectStmt(queryTable, cols, cond, group)
    return db.query(stmt)

def selectDataForKK(begDate, endDate, eventPurposeId, eventTypes, orgStructureId, personId, rowGrouping, visitPayStatus, visitHospital, sex, ageFrom, ageTo, visitDisp, eventDate=None):
    db = QtGui.qApp.db
    Action = db.table('Action')
    ActionByIllness = Action.alias('byIllness')
    ActionType = db.table('ActionType')
    Client = db.table('Client')
    Event = db.table('Event')
    EventKind = db.table('rbEventKind')
    EventType = db.table('EventType')
    Finance = db.table('rbFinance')
    Person = db.table('Person')
    Service = db.table('rbService')
    ServiceCategory = db.table('rbServiceCategory')

    KLADR = db.table('kladr.KLADR')
    SOCRBASE = db.table('kladr.SOCRBASE')

    ClientLocAddress = db.table('ClientAddress').alias('ClientLocAddress')
    LocAddress = db.table('Address').alias('LocAddress')
    LocAddressHouse = db.table('AddressHouse').alias('LocAddressHouse')
    LocKLADR = KLADR.alias('LocKLADR')
    LocSOCR = SOCRBASE.alias('LocSOCR')

    ClientRegAddress = db.table('ClientAddress').alias('ClientRegAddress')
    RegAddress = db.table('Address').alias('RegAddress')
    RegAddressHouse = db.table('AddressHouse').alias('RegAddressHouse')
    RegKLADR = KLADR.alias('RegKLADR')
    RegSOCR = SOCRBASE.alias('RegSOCR')


    groupFields = {
        0: 'date(%s)' % Action['endDate'],
        1: Action['person_id'].name(),
        2: Person['orgStructure_id'].name(),
        3: Person['speciality_id'].name(),
        4: Person['post_id'].name()
    }
    rowKey = groupFields[rowGrouping if rowGrouping in groupFields else 0]

    subTable = Event.innerJoin(Action, [Action['event_id'].eq(Event['id']), Action['endDate'].ge(begDate), Action['endDate'].lt(endDate.addDays(1)), Action['deleted'].eq(0)])
    subTable = subTable.innerJoin(Client, [Client['id'].eq(Event['client_id']), Client['deleted'].eq(0)])
    subTable = subTable.innerJoin(ActionType, [ActionType['id'].eq(Action['actionType_id']), ActionType['deleted'].eq(0)])
    subTable = subTable.innerJoin(Service, Service['id'].eq(ActionType['nomenclativeService_id']))
    subTable = subTable.innerJoin(ServiceCategory, ServiceCategory['id'].eq(Service['category_id']))
    subTable = subTable.innerJoin(Person, [Person['id'].eq(Action['person_id']), Person['deleted'].eq(0)])

    byCategorySubCond = [
        Event['deleted'].eq(0)
    ]
    if personId:
        byCategorySubCond.append(Action['person_id'].eq(personId))
    elif orgStructureId:
        byCategorySubCond.append(Person['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    else:
        byCategorySubCond.append(Person['org_id'].eq(QtGui.qApp.currentOrgId()))

    if ageFrom <= ageTo and (ageFrom > 0 or ageTo < 150):
        byCategorySubCond.append('Action.endDate >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)' % ageFrom)
        byCategorySubCond.append('Action.endDate < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)' % (ageTo + 1))

    if visitPayStatus >= 0:
        byCategorySubCond.append('getPayCode(%s, %s) = %d' % (Action['finance_id'].name(), Action['payStatus'].name(), visitPayStatus))

    tableCountByCategory = db.table(
        db.selectStmt(subTable,
                      fields=[
                          Event['id'].alias('eventId'),
                          db.makeField(rowKey).alias('rowKey'),
                          db.func.age(Client['birthDate'], Action['endDate']).alias('clientAge'),
                          ServiceCategory['code'].alias('category'),
                          db.count('*').alias('cnt')
                      ],
                      where=byCategorySubCond,
                      group=['eventId', 'rowKey', 'clientAge', 'category'])
    ).alias('countByCategory')

    byIllnessTable = Action.innerJoin(ActionType, [ActionType['id'].eq(Action['actionType_id']), ActionType['deleted'].eq(0)])
    byIllnessTable = byIllnessTable.innerJoin(Service, Service['id'].eq(ActionType['nomenclativeService_id']))
    byIllnessTable = byIllnessTable.innerJoin(ServiceCategory, [ServiceCategory['id'].eq(Service['category_id']), ServiceCategory['code'].eq('1')])
    byIllnessStmt = db.selectStmt(byIllnessTable,
                                  fields=db.max(Action['id']),
                                  where=[Action['event_id'].eq(Event['id']), Action['deleted'].eq(0)])

    table = Event.innerJoin(EventType, [EventType['id'].eq(Event['eventType_id']), EventType['deleted'].eq(0)])
    table = table.leftJoin(EventKind, EventKind['id'].eq(EventType['eventKind_id']))
    table = table.leftJoin(Finance, Finance['id'].eq(EventType['finance_id']))
    table = table.innerJoin(tableCountByCategory, tableCountByCategory['eventId'].eq(Event['id']))
    table = table.innerJoin(Client, [Client['id'].eq(Event['client_id']), Client['deleted'].eq(0)])

    table = table.leftJoin(ClientRegAddress, ClientRegAddress['id'].eq(db.func.getClientRegAddressId(Client['id'])))
    table = table.leftJoin(RegAddress, RegAddress['id'].eq(ClientRegAddress['address_id']))
    table = table.leftJoin(RegAddressHouse, RegAddressHouse['id'].eq(RegAddress['house_id']))
    table = table.leftJoin(RegKLADR, RegKLADR['CODE'].eq(RegAddressHouse['KLADRCode']))
    table = table.leftJoin(RegSOCR, '{field} = ({stmt})'.format(field=RegSOCR['KOD_T_ST'],
                                                                stmt=db.selectStmt(SOCRBASE, 'KOD_T_ST', SOCRBASE['SCNAME'].eq(RegKLADR['SOCR']), limit=1)))

    table = table.leftJoin(ClientLocAddress, ClientLocAddress['id'].eq(db.func.getClientLocAddressId(Client['id'])))
    table = table.leftJoin(LocAddress, LocAddress['id'].eq(ClientLocAddress['address_id']))
    table = table.leftJoin(LocAddressHouse, LocAddressHouse['id'].eq(LocAddress['house_id']))
    table = table.leftJoin(LocKLADR, LocKLADR['CODE'].eq(LocAddressHouse['KLADRCode']))
    table = table.leftJoin(LocSOCR, '{field} = ({stmt})'.format(field=LocSOCR['KOD_T_ST'],
                                                                stmt=db.selectStmt(SOCRBASE, 'KOD_T_ST', SOCRBASE['SCNAME'].eq(LocKLADR['SOCR']), limit=1)))

    table = table.leftJoin(ActionByIllness, '{id} = ({stmt})'.format(id=ActionByIllness['id'], stmt=byIllnessStmt))

    villagerSOCRBASE = ('302', '303', '304', '305', '310', '314', '316', '317', '401', '402', '403', '404', '406', '407', '416', '417', '419', '421', '423', '424', '425', '429', '430', '431', '433', '434', '435', '443', '448', '449')

    cols = [
        db.sum(tableCountByCategory['cnt']).alias('cnt'),
        tableCountByCategory['rowKey'].alias('rowKey'),
        tableCountByCategory['clientAge'].alias('clientAge'),
        tableCountByCategory['category'].alias('category'),
        Finance['code'].alias('financeCode'),
        db.makeField(ActionByIllness['id'].isNotNull()).alias('hasActionByIllness'),
        db.makeField(db.joinOr([
            ClientRegAddress['isVillager'].eq(1),
            RegSOCR['KOD_T_ST'].inlist(villagerSOCRBASE),
            ClientLocAddress['isVillager'].eq(1),
            LocSOCR['KOD_T_ST'].inlist(villagerSOCRBASE)
        ])).alias('isVillager')
    ]

    group = [
        'rowKey',
        'clientAge',
        'category',
        'financeCode',
        'hasActionByIllness',
        'isVillager'
    ]

    cond = [
        Event['deleted'].eq(0)
    ]

    if eventDate:
        eventBegDatetime, eventEndDatetime = eventDate
        addDateInRange(cond, Event['createDatetime'], eventBegDatetime, eventEndDatetime)

    if not visitHospital:
        MedicalAidType = db.table('rbMedicalAidType')
        hospitalMAT_ids  = db.getIdList(MedicalAidType, MedicalAidType['id'], MedicalAidType['code'].eq('7'))
        cond.append(EventType['medicalAidType_id'].notInlist(hospitalMAT_ids))

    if not visitDisp:
        cond.append(db.joinOr([EventKind['code'].notInlist([u'01', u'02', u'04']),
                               EventKind['code'].isNull()]))

    if eventTypes:
        cond.append(Event['eventType_id'].inlist(eventTypes))
    elif eventPurposeId:
        cond.append(EventType['purpose_id'].eq(eventPurposeId))

    if sex:
        cond.append(Client['sex'].eq(sex))

    return db.query(db.selectStmt(table, cols, cond, group))


class CReportF39SetupDialog(QtGui.QDialog, Ui_ReportF39SetupDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbEventPurpose.setTable('rbEventTypePurpose', True, filter='code != \'0\'')
        self.lstEventTypes.setTable('EventType', filter=getWorkEventTypeFilter())
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbVisitPayStatus.setCurrentIndex(0)
        self.chkAmbVisits.setEnabled(True) if self.cmbRowGrouping.currentIndex() == 6 else self.chkAmbVisits.setEnabled(False)
        self.chkCombine.setEnabled(True) if self.cmbRowGrouping.currentIndex() == 6 else self.chkCombine.setEnabled(False)
        self.chkDetailChildren.setVisible(False)


    def setVisibleForPND(self, value):
        self.chkADN.setVisible(value)
        self.chkCountCall.setVisible(value)
        self.chkAmbVisits.setVisible(value)
        self.chkCombine.setVisible(value)
        self.chkVisitDisp.setVisible(not value)


    def setVisibled(self, value):
        self.lblVisitPayStatus.setVisible(value)
        self.cmbVisitPayStatus.setVisible(value)


    def addRowGrouping(self):
        self.cmbRowGrouping.setItemText(1, u'Персоналу')
        self.cmbRowGrouping.addItem(u'Врачам')
        self.cmbRowGrouping.addItem(u'Мед.сестрам')


    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.edtBegDate.setDate(getVal(params, 'begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(getVal(params, 'endDate', QtCore.QDate.currentDate()))
        self.cmbEventPurpose.setValue(params.get('eventPurposeId', None))
        self.cmbOrgStructure.setValue(getVal(params, 'orgStructureId', None))
        self.cmbPerson.setValue(getVal(params, 'personId', None))
        self.cmbRowGrouping.setCurrentIndex(getVal(params, 'advancedRowGrouping', 0))
        if self.cmbVisitPayStatus.isVisible():
            self.cmbVisitPayStatus.setCurrentIndex(params.get('visitPayStatus', 0))
        self.chkDetailChildren.setChecked(params.get('detailChildren', False))
        self.chkVisitHospital.setChecked(params.get('visitHospital', False))
        self.chkVisitDisp.setChecked(params.get('visitDisp', False))
        self.chkCountCall.setChecked(params.get('countCall', False))
        self.cmbSex.setCurrentIndex(params.get('sex', 0))
        self.edtAgeFrom.setValue(params.get('ageFrom', 0))
        self.edtAgeTo.setValue(params.get('ageTo', 150))
        self.chkADN.setChecked(params.get('ADN', False))
        self.chkAmbVisits.setChecked(params.get('ambVisits', False))
        self.chkCombine.setChecked(params.get('combine', False))
        self.edtEventBegDatetime.setDateTime(params.get('eventBegDatetime', QtCore.QDateTime.currentDateTime()))
        self.edtEventEndDatetime.setDateTime(params.get('eventEndDatetime', QtCore.QDateTime.currentDateTime()))
        self.gbEventDatetimeParams.setChecked(params.get('isEventCreateParams', False))


    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['eventPurposeId'] = self.cmbEventPurpose.value()
        result['eventTypes'] = self.lstEventTypes.nameValues()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['personId'] = self.cmbPerson.value()
        result['advancedRowGrouping'] = self.cmbRowGrouping.currentIndex()
        if self.cmbVisitPayStatus.isVisible():
            result['visitPayStatus'] = self.cmbVisitPayStatus.currentIndex()
        result['detailChildren'] = self.chkDetailChildren.isChecked()
        result['visitHospital'] = self.chkVisitHospital.isChecked()
        result['visitDisp'] = self.chkVisitDisp.isChecked()
        result['countCall'] = self.chkCountCall.isChecked()
        result['sex'] = self.cmbSex.currentIndex()
        result['ageFrom'] = self.edtAgeFrom.value()
        result['ageTo'] = self.edtAgeTo.value()
        result['ADN'] = self.chkADN.isChecked()
        result['ambVisits'] = self.chkAmbVisits.isChecked()
        result['combine'] = self.chkCombine.isChecked()
        result['isEventCreateParams'] = self.gbEventDatetimeParams.isChecked()
        result['eventBegDatetime'] = self.edtEventBegDatetime.dateTime()
        result['eventEndDatetime'] = self.edtEventEndDatetime.dateTime()
        return result


    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.cmbPerson.setEndDate(QtCore.QDate(date))


    @QtCore.pyqtSlot(int)
    def on_cmbEventPurpose_currentIndexChanged(self, index):
        eventPurposeId = self.cmbEventPurpose.value()
        if eventPurposeId:
            filter = 'EventType.purpose_id =%d' % eventPurposeId
        else:
            filter = getWorkEventTypeFilter()
        self.lstEventTypes.setFilter(filter)


    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)


    @QtCore.pyqtSlot(int)
    def on_cmbRowGrouping_currentIndexChanged(self, index):
        if self.cmbRowGrouping.currentIndex() == 6 or self.cmbRowGrouping.currentIndex() == 5:
            self.chkCombine.setEnabled(True)
            if self.cmbRowGrouping.currentIndex() == 6:
                self.chkAmbVisits.setEnabled(True)
        else:
            self.chkAmbVisits.setEnabled(False)
            self.chkCombine.setEnabled(False)
            self.chkAmbVisits.setChecked(False)
            self.chkCombine.setChecked(False)


class CReportF39(CReport):
    """
    Форма N 039/у-02
    ВЕДОМОСТЬ учета врачебных посещений в амбулаторно-поликлинических учреждениях, на дому
    """

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Форма 39')

        region = QtGui.qApp.region()
        if region == '78':  # СПб
            self.cureEventGoalCode = ['5', '7']
            self.prophylaxyEventGoalCode = '2'
        elif region == '91':  # Крым
            self.cureEventGoalCode = ['1']
            self.prophylaxyEventGoalCode = '2'
        # elif region == '23': # Краснодар
        #     self.curePurposeCode = ?
        #     self.prophylaxyPurposeCode = ?
        else:
            self.cureEventGoalCode = ['1']
            self.prophylaxyEventGoalCode = '2'

    def getSetupDialog(self, parent):
        result = CReportF39SetupDialog(parent)
        result.setTitle(self.title())
        result.setVisibleForPND(False)
        result.setVisibled(True)
        return result


    def createHeader(self, cursor, params):
        charFormatHeader = CReportBase.TableHeader
        charFormatHeader.setFontPointSize(7)

        charFormatTitle = CReportBase.ReportTitle
        charFormatTitle.setFontPointSize(12)

        charFormatDescr = CReportBase.TableHeader
        charFormatDescr.setFontPointSize(9)

        db = QtGui.qApp.db
        orgId = QtGui.qApp.currentOrgId()
        orgName = forceString(db.translate('Organisation', 'id', orgId, 'fullName'))
        if not orgName:
            orgName = u'_' * 50

        headerLeft = u'Министерство здравоохранения\n' + \
                     u'Российской Федерации\n\n' + \
                     orgName + u'\n' \
                     u'наименование учреждения'
        headerRight = u'Медицинская документация\n' \
                      u'Форма N 039/у-02\n' \
                      u'Утверждена приказом Минздрава России\n' \
                      u'от 30.12.2002 N 413'
        headerColumns = [
            ('30?', [''], CReportBase.AlignCenter),
            ('80%', [''], CReportBase.AlignCenter),
            ('30?', [''], CReportBase.AlignLeft),
        ]
        headerTable = createTable(cursor, headerColumns, border=0, cellPadding=2, cellSpacing=0, charFormat=charFormatHeader)
        headerTable.setText(0, 0, headerLeft)
        headerTable.setText(0, 2, headerRight)
        cursor.movePosition(QtGui.QTextCursor.End)

        cursor.insertBlock()
        cursor.setBlockFormat(CReportBase.AlignCenter)
        cursor.setCharFormat(charFormatTitle)
        cursor.insertText(u'ВЕДОМОСТЬ\nучета врачебных посещений в амбулаторно-поликлинических учреждениях, на дому')
        cursor.movePosition(QtGui.QTextCursor.End)

        cursor.insertBlock()
        cursor.insertBlock()

        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        periodStr = u'за период с %02d.%02d.%d г. по %02d.%02d.%d г.' % (begDate.day(), begDate.month(), begDate.year(),
                                                                         endDate.day(), endDate.month(), endDate.year())

        personId = params.get('personId', None)
        personName, personPost, personSpeciality = getPersonInfo(personId)

        if not personId is None:
            namePostStr = personName + u', ' + personPost + u'\n' + u'_' * 70
            specialityStr = personSpeciality + u'\n' + u'_' * 30
        else:
            namePostStr = u'_' * 70
            specialityStr = u'_' * 30

        descriptionL = namePostStr + u'\n' + u'Ф.И.О. и должность врача\n'
        descriptionR = specialityStr + u'\n' + u'профиль специальности\n'
        descriptionM = periodStr + u'\n\n' + u'Участок:   территориальный № __________________   цеховой № __________________\n'

        descriptionColumns = [
            ('15%', [u'', u''], CReportBase.AlignCenter),
            ('35%', [u'', u''], CReportBase.AlignCenter),
            ('35%', [u'', u''], CReportBase.AlignCenter),
            ('15%', [u'', u''], CReportBase.AlignCenter),
        ]


        descriptionTable = createTable(cursor, descriptionColumns, border=0, cellPadding=2, cellSpacing=0, charFormat=charFormatDescr)
        descriptionTable.mergeCells(1, 1, 1, 2)
        descriptionTable.setText(0, 1, descriptionL)
        descriptionTable.setText(0, 2, descriptionR)
        descriptionTable.setText(1, 1, descriptionM)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()


    def createTable(self, cursor, keyName):
        tableColumns = [
            ('5?', [keyName], CReportBase.AlignRight),
            ('5%', [u'Число посещений в поликлинике', u'всего', u'', u''], CReportBase.AlignRight),
            ('5%', [u'',                              u'из них сельских жителей', u'', u''], CReportBase.AlignRight),
            ('5%', [u'в том числе в возрасте (из графы 2)', u'0-17лет', u'', u''], CReportBase.AlignRight),
            ('5%', [u'',                                    u'60 лет и старше', u'', u''], CReportBase.AlignRight),
            ('5%', [u'из общего числа посещений в поликлинике по поводу заболеваний', u'всего', u'', u''], CReportBase.AlignRight),
            ('5%', [u'',                                                              u'в т.ч. в возрасте', u'0-17 лет', u''], CReportBase.AlignRight),
            ('5%', [u'',                                                              u'',                  u'60 лет и старше', u''], CReportBase.AlignRight),
            ('5%', [u'Профилактических', u'', u'', u''], CReportBase.AlignRight),
            ('5%', [u'Число посещений на дому (всего)', u'', u'', u''], CReportBase.AlignRight),
            ('5%', [u'из общего числа посещений на дому', u'по поводу заболеваний', u'всего', u''], CReportBase.AlignRight),
            ('5%', [u'', u'',                                                       u'в т.ч. в возрасте', u'0-17 лет'], CReportBase.AlignRight),
            ('5%', [u'', u'', u'',                                                                        u'из них 0-1 год (вкл.)'], CReportBase.AlignRight),
            ('5%', [u'', u'', u'',                                                                        u'60 лет и старше'], CReportBase.AlignRight),
            ('5%', [u'',                                  u'из числа профилактических', u'0-17 лет', u''], CReportBase.AlignRight),
            ('5%', [u'', u'',                                                           u'В т.ч. 0-1 год', u''], CReportBase.AlignRight),
            ('5%', [u'Число посещений по видам оплаты', u'ОМС', u'', u''], CReportBase.AlignRight),
            ('5%', [u'', u'бюджет', u'', u''], CReportBase.AlignRight),
            ('5%', [u'', u'платные', u'', u''], CReportBase.AlignRight),
            ('5%', [u'', u'ДМС', u'', u''], CReportBase.AlignRight)
        ]

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 1, 1, 2)
        table.mergeCells(0, 3, 1, 2)
        table.mergeCells(0, 5, 1, 3)
        table.mergeCells(1, 6, 1, 2)
        table.mergeCells(0, 10, 1, 6)
        table.mergeCells(1, 10, 1, 4)
        table.mergeCells(1, 14, 1, 2)
        table.mergeCells(2, 11, 1, 3)
        table.mergeCells(0, 16, 1, 4)

        table.mergeCells(0, 0, 4, 1)
        table.mergeCells(1, 1, 3, 1)
        table.mergeCells(1, 2, 3, 1)
        table.mergeCells(1, 3, 3, 1)
        table.mergeCells(1, 4, 3, 1)
        table.mergeCells(1, 5, 3, 1)
        table.mergeCells(2, 6, 2, 1)
        table.mergeCells(2, 7, 2, 1)
        table.mergeCells(0, 8, 4, 1)
        table.mergeCells(0, 9, 4, 1)
        table.mergeCells(2, 10, 2, 1)
        table.mergeCells(2, 14, 2, 1)
        table.mergeCells(2, 15, 2, 1)
        table.mergeCells(1, 16, 3, 1)
        table.mergeCells(1, 17, 3, 1)
        table.mergeCells(1, 18, 3, 1)
        table.mergeCells(1, 19, 3, 1)

        i = table.addRow()
        for col in xrange(len(tableColumns)):
            table.setText(i, col, col + 1, blockFormat=CReportBase.AlignCenter)

        return table

    def processRecord(self, record, reportData, forceKeyVal, rowSize, financeIndexes):
        rowKey = forceKeyVal(record.value('rowKey'))
        cnt = forceInt(record.value('cnt'))
        atAmbulance = forceBool(record.value('atAmbulance'))
        atHome = forceBool(record.value('atHome'))
        eventGoalCode = forceString(record.value('eventGoalCode'))
        clientAge = forceInt(record.value('clientAge'))
        clientVillager = forceBool(record.value('clientVillager'))
        financeId = forceInt(record.value('financeId'))

        prophylaxy = eventGoalCode == self.prophylaxyEventGoalCode

        row = reportData.setdefault(rowKey, [0] * rowSize)

        if atAmbulance:
            row[0] += cnt
            if clientVillager:
                row[1] += cnt
            if clientAge <= 17:
                row[2] += cnt
            elif clientAge >= 60:
                row[3] += cnt
            for k in self.cureEventGoalCode:
                if eventGoalCode == k:
                    row[4] += cnt
                    if clientAge <= 17:
                        row[5] += cnt
                    elif clientAge >= 60:
                        row[6] += cnt
            if prophylaxy:
                row[7] += cnt

        elif atHome:
            row[8] += cnt
            for k in self.cureEventGoalCode:
                if eventGoalCode == k:
                    row[9] += cnt
                    if clientAge <= 1:
                        row[10] += cnt
                        row[11] += cnt
                    elif clientAge <= 17:
                        row[10] += cnt
                    elif clientAge >= 60:
                        row[12] += cnt
                elif prophylaxy:
                    if clientAge <= 17:
                        row[13] += cnt
                    elif clientAge >= 60:
                        row[14] += cnt
        if financeId in financeIndexes:
            row[15 + financeIndexes[financeId]] += cnt

    def processRecordForKK(self, record, reportData, forceKeyVal, rowSize, financeIndexes):
        rowKey = forceKeyVal(record.value('rowKey'))
        clientAge = forceInt(record.value('clientAge'))
        isVillager = forceBool(record.value('isVillager'))
        financeCode = forceInt(record.value('financeCode'))
        category = forceInt(record.value('category'))
        hasActionByIllness = forceBool(record.value('hasActionByIllness'))
        cnt = forceInt(record.value('cnt'))

        row = reportData.setdefault(rowKey, [0] * rowSize)
        if category in [2, 3, 4, 5]:
            row[0] += cnt
            if isVillager:
                row[1] += cnt
            if clientAge <= 17:
                row[2] += cnt
            elif clientAge >= 60:
                row[3] += cnt
            if hasActionByIllness:
                row[4] += cnt
                if clientAge <= 17:
                    row[5] += cnt
                if clientAge >= 60:
                    row[6] += cnt
            if category == 5:
                row[7] += cnt
            if financeCode in financeIndexes:
                row[15 + financeIndexes[financeCode]] += cnt
        elif category in [6, 7, 8]:
            row[8] += cnt
            if category in [6, 7]:
                row[9] += cnt
                if clientAge <= 1:
                    row[10] += cnt
                    row[11] += cnt
                elif clientAge <= 17:
                    row[10] += cnt
                elif clientAge >= 60:
                    row[12] += cnt
            elif category == 8:
                if clientAge <= 17:
                    row[13] += cnt
                if clientAge <= 1:
                    row[14] += cnt
            if financeCode in financeIndexes:
                row[15 + financeIndexes[financeCode]] += cnt

    def processQueryForKK(self, query, forceKeyVal, rowSize):
        financeIdMap = {
            2: 0,  # ОМС
            1: 1,  # бюджет
            # 70: 1, # Федеральный бюджет
            # 71: 1, # Бюджет субъекта Российской Федерации
            # 72: 1, # Муниципальный бюджет
            4: 2,  # платные услуги
            3: 3  # ДМС
        }

        reportData = {}
        while query.next():
            record = query.record()
            self.processRecordForKK(record, reportData, forceKeyVal, rowSize, financeIdMap)

        return reportData

    def processQuery(self, query, forceKeyVal, rowSize):
        financeIdMap = {
            2: 0,  # ОМС
            1: 1,  # бюджет
            # 70: 1, # Федеральный бюджет
            # 71: 1, # Бюджет субъекта Российской Федерации
            # 72: 1, # Муниципальный бюджет
            4: 2,  # платные услуги
            3: 3   # ДМС
        }

        reportData = {}
        while query.next():
            record = query.record()
            self.processRecord(record, reportData, forceKeyVal, rowSize, financeIdMap)

        return reportData

    def genOrgStructureReport(self, table, reportData, rowSize, orgStructureId):
        model = COrgStructureModel(None, QtGui.qApp.currentOrgId())
        index = model.findItemId(orgStructureId)
        if index:
            item = index.internalPointer()
        else:
            item = model.getRootItem()
        self.genOrgStructureReportForItem(table, reportData, item, rowSize)


    def genOrgStructureReportForItem(self, table, reportData, item, rowSize):
        i = table.addRow()
        if item.childCount() == 0:
            table.setText(i, 0, item.name())
            row = reportData.get(item.id(), None)
            if row:
                for j in xrange(rowSize):
                    table.setText(i, j+1, row[j])
            return row
        else:
            table.mergeCells(i, 1, 1, rowSize+1)
            table.setText(i, 0, item.name(), CReportBase.TableHeader)
            total = [0]*rowSize
            row = reportData.get(item.id(), None)
            if row:
                i = table.addRow()
                table.setText(i, 0, '-', CReportBase.TableHeader)
                for j in xrange(rowSize):
                    table.setText(i, j+1, row[j])
                    total[j] += row[j]
            for subitem in item.items():
                row = self.genOrgStructureReportForItem(table, reportData, subitem, rowSize)
                if row:
                    for j in xrange(rowSize):
                        total[j] += row[j]
            i = table.addRow()
            table.setText(i, 0, u'Всего по '+item.name(), CReportBase.TableTotal)
            for j in xrange(rowSize):
                table.setText(i, j+1, total[j], CReportBase.TableTotal)
            return total


    def build(self, params):
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        isEventTime = params.get('isEventCreateParams', False)
        eventDate = ((params.get('eventBegDatetime', QtCore.QDate.currentDate()),
                      params.get('eventEndDatetime', QtCore.QDate.currentDate())) if isEventTime else None)
        eventPurposeId = params.get('eventPurposeId', None)
        eventTypesDict = params.get('eventTypes', {})
        eventTypes = eventTypesDict.keys()
        orgStructureId = params.get('orgStructureId', None)
        personId = params.get('personId', None)
        rowGrouping = params.get('advancedRowGrouping', 0)
        visitPayStatus = params.get('visitPayStatus', 0)
        detailChildren = params.get('detailChildren', False)
        visitHospital = params.get('visitHospital', False)
        visitDisp = params.get('visitDisp', False)
        sex = params.get('sex', 0)
        ageFrom = params.get('ageFrom', 0)
        ageTo = params.get('ageTo', 150)
        self.countCall = params.get('countCall', False)
        visitPayStatus -= 1

        if rowGrouping == 4: # by post_id
            postId = None
            forceKeyVal = forceRef
            keyValToString = lambda postId: forceString(QtGui.qApp.db.translate('rbPost', 'id', postId, 'name'))
            keyValToSort = keyValToString
            keyName = u'Должность'
        elif rowGrouping == 3: # by speciality_id
            specialityId = None
            forceKeyVal = forceRef
            keyValToString = lambda specialityId: forceString(QtGui.qApp.db.translate('rbSpeciality', 'id', specialityId, 'name'))
            keyValToSort = keyValToString
            keyName = u'Специальность'
        elif rowGrouping == 2: # by orgStructureId
            forceKeyVal = forceRef
            keyValToString = None
            keyValToSort = None
            keyName = u'Подразделение'
        elif rowGrouping == 1: # by personId
            forceKeyVal = forceRef
            keyValToString = lambda personId: forceString(QtGui.qApp.db.translate('vrbPersonWithSpeciality', 'id', personId, 'name'))
            # keyValToString = lambda personId: getPersonString(personId)
            keyValToSort = keyValToString
            keyName = u'Врач'
        else:
            forceKeyVal = lambda x: pyDate(forceDate(x))
            keyValToSort = None
            keyValToString = lambda x: forceString(QtCore.QDate(x))
            keyName = u'Дата'

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(QtGui.QTextCharFormat())
        self.createHeader(cursor, params)

        # i3149: Форма 39 для Краснодарского края1987
        if QtGui.qApp.region().startswith('23'):
            query = selectDataForKK(
                begDate,
                endDate,
                eventPurposeId,
                eventTypes,
                orgStructureId,
                personId,
                rowGrouping,
                visitPayStatus,
                visitHospital,
                sex,
                ageFrom,
                ageTo,
                visitDisp,
                eventDate
            )
            self.setQueryText(forceString(query.lastQuery()))
            rowSize = 19
            reportData = self.processQueryForKK(query, forceKeyVal, rowSize)
        else:
            query = selectData(
                begDate,
                endDate,
                eventPurposeId,
                eventTypes,
                orgStructureId,
                personId,
                rowGrouping,
                visitPayStatus,
                visitHospital,
                sex,
                ageFrom,
                ageTo,
                visitDisp,
                eventDate
            )
            self.setQueryText(forceString(query.lastQuery()))
            rowSize = 19
            reportData = self.processQuery(query, forceKeyVal, rowSize)

        table = self.createTable(cursor, keyName)

        if rowGrouping == 2:  # by orgStructureId
            self.genOrgStructureReport(table, reportData, rowSize, orgStructureId)
        else:
            keys = reportData.keys()
            if not keyValToSort is None:
                keys.sort(key=keyValToSort)
            else:
                keys.sort()
            total = [0] * rowSize
            for key in keys:
                i = table.addRow()
                table.setText(i, 0, keyValToString(key))
                row = reportData[key]
                for j in xrange(rowSize):
                    table.setText(i, j + 1, row[j])
                    total[j] += row[j]
            i = table.addRow()
            table.setText(i, 0, u'Всего', CReportBase.TableTotal)
            for j in xrange(rowSize):
                table.setText(i, j+1, total[j], CReportBase.TableTotal)

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()
        doctorSignColumns = [
            ('60%', [], CReportBase.AlignLeft),
            ('40%', [u'Подпись врача ______________________________________________'], CReportBase.AlignLeft)
        ]
        doctorSign = createTable(cursor, doctorSignColumns, border=0, cellPadding=2, cellSpacing=0)

        return doc
