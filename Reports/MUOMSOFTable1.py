# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Utils import getWorkEventTypeFilter
from Orgs.Utils import getOrgStructureDescendants
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Ui_MUOMSOF import Ui_MUOMSOFSetupDialog
from library.DialogBase import CDialogBase
from library.Utils import forceDate, forceDouble, forceInt, forceRef, forceString


def selectData(begDate, endDate, eventPurposeId, eventTypeId, orgStructureId, specialityId, personId, contractIdList, insurerId, sex, ageFrom, ageTo):
    stmt="""
SELECT
    Event.id as event_id,
    Event.client_id AS client_id,
    Action.begDate AS begDate,
    Action.endDate AS endDate,
    rbMedicalAidType.code AS medicalAidTypeCode,
    Account_Item.`amount` AS `amount`,
    (SELECT COUNT(*)
     FROM Visit
     WHERE Visit.event_id = Event.id
       AND Visit.date >= Action.begDate
       AND Visit.date < DATE_ADD(Action.endDate,INTERVAL 1 DAY)) AS visitCount
FROM
    Account_Item
    LEFT JOIN Account    ON Account.id = Account_Item.master_id AND Account.deleted = 0
    LEFT JOIN Event      ON Event.id = Account_Item.event_id
    LEFT JOIN Client     ON Client.id = Event.client_id
    LEFT JOIN EventType  ON EventType.id = Event.eventType_id
    LEFT JOIN Action     ON Action.id = Account_Item.action_id
    LEFT JOIN ActionType ON ActionType.id = Action.actionType_id
    LEFT JOIN vrbPersonWithSpeciality ON vrbPersonWithSpeciality.id = Event.execPerson_id
    LEFT JOIN rbMedicalAidType ON rbMedicalAidType.id = EventType.medicalAidType_id
    LEFT JOIN ClientPolicy ON ClientPolicy.id = getClientPolicyId(Event.client_id, 1)
WHERE
    (ActionType.isMES OR Event.MES_id)
    AND Account_Item.reexposeItem_id IS NULL
    AND Account_Item.deleted=0
    AND Event.deleted = 0
    AND %s
    ORDER BY Event.id, Event.client_id
"""
    db = QtGui.qApp.db
    tableEvent  = db.table('Event')
    tableClient = db.table('Client')
    tablePerson = db.table('vrbPersonWithSpeciality')
    tableAccount = db.table('Account')
    tableClientPolicy = db.table('ClientPolicy')
    cond = []
    cond.append(tableEvent['execDate'].ge(begDate))
    cond.append(db.joinOr([tableEvent['execDate'].lt(endDate.addDays(1)), tableEvent['execDate'].isNull()]))
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    elif eventPurposeId:
        cond.append(db.table('EventType')['purpose_id'].eq(eventPurposeId))
    if personId:
        cond.append(tableEvent['execPerson_id'].eq(personId))
    elif orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    else:
        cond.append(tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()))
    if specialityId:
        cond.append(tablePerson['speciality_id'].eq(specialityId))
    if contractIdList:
        cond.append(tableAccount['contract_id'].inlist(contractIdList))
    if insurerId:
        cond.append(tableClientPolicy['insurer_id'].eq(insurerId))
    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append('Event.setDate >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)'%ageFrom)
        cond.append('Event.setDate < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)'%(ageTo+1))
    return db.query(stmt % (db.joinAnd(cond)))


class CMUOMSOFTable1(CReport):
    name = u'Отчёт №1 МУОМС-ОФ, Таблица 1'

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(self.name)


    def getSetupDialog(self, parent):
        result = CMUOMSOFSetupDialog(parent)
        result.setTitle(self.title())
        return result


    def build(self, params):
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        eventPurposeId = params.get('eventPurposeId', None)
        eventTypeId = params.get('eventTypeId', None)
        orgStructureId = params.get('orgStructureId', None)
        specialityId = params.get('specialityId', None)
        personId = params.get('personId', None)
        contractIdList = params.get('contractIdList', None)
        insurerId = params.get('insurerId', None)
        sex = params.get('sex', 0)
        ageFrom = params.get('ageFrom', 0)
        ageTo = params.get('ageTo', 150)
        query = selectData(begDate, endDate, eventPurposeId, eventTypeId, orgStructureId, specialityId, personId, contractIdList, insurerId, sex, ageFrom, ageTo)

        #0) счёт клиентов
        #1) счёт дней
        #2) счёт визитов
        #3) счёт действий
        #4) счёт количества в действиях
        #5) счёт событий

        rowSize = 6
        reportData = [ [0]*rowSize for row in xrange(8) ]

        prevClientId = False
        clientRows = set([])

        prevEventId = False
        eventRows = set([])

        self.setQueryText(forceString(query.lastQuery()))
        while query.next() :
            record = query.record()
            clientId = forceRef(record.value('client_id'))
            begDate = forceDate(record.value('begDate'))
            endDate = forceDate(record.value('endDate'))
            medicalAidTypeCode = forceInt(record.value('medicalAidTypeCode'))
            amount = forceDouble(record.value('amount'))
            visitCount = forceInt(record.value('visitCount'))
            eventId = forceRef(record.value('event_id'))

            if 1<=medicalAidTypeCode<=8:
                if prevClientId != clientId:
                    prevClientId = clientId
                    clientRows = set([])

                if prevEventId != eventId:
                    prevEventId = eventId
                    eventRows = set([])

                if medicalAidTypeCode in [2, 3]:
                    rows = [0, medicalAidTypeCode-1]
                else:
                    rows = [medicalAidTypeCode-1]

                for row in rows:
                    reportLine = reportData[row]
                    if row not in clientRows:
                        clientRows.add(row)
                        reportLine[0] += 1
                    reportLine[1] += begDate.daysTo(endDate)+1
                    reportLine[2] += visitCount
                    reportLine[3] += 1
                    reportLine[4] += amount
                    if row not in eventRows:
                        eventRows.add(row)
                        reportLine[5] += 1

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.name)
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        cursor.insertText(u'Таблица 1. Объёмы медицинской помощи, оказанной в рамках ТП ОМС')
        cursor.insertBlock()

        tableColumns = [
            ('30%',[u'Показатели мониторинга',    '1'], CReportBase.AlignLeft),
            ( '8%',[u'№ строки',                  '2'], CReportBase.AlignCenter),
            ( '8%',[u'№ наименование показателя', '3'], CReportBase.AlignLeft),
            ( '8%',[u'количество',                '4'], CReportBase.AlignRight),
            ]

        table = createTable(cursor, tableColumns)
        i0 = table.addRow()
        i1 = table.addRow()
        i2 = table.addRow()
        table.mergeCells(i0, 0, 3, 1)
        table.mergeCells(i0, 1, 3, 1)
        table.setText(i0, 0, u'Стационарная медицинская помощь - всего:')
        table.setText(i0, 1, 1)
        table.setText(i0, 2, u'число койко-дней');          table.setText(i0, 3, reportData[0][1])
        table.setText(i1, 2, u'число законченных случаев'); table.setText(i1, 3, reportData[0][5])
        table.setText(i2, 2, u'число выбывших больных');    table.setText(i2, 3, reportData[0][0])

        i0 = table.addRow()
        i1 = table.addRow()
        i2 = table.addRow()
        table.mergeCells(i0, 0, 3, 1)
        table.mergeCells(i0, 1, 3, 1)
        table.setText(i0, 0, u'В том числе:\n-высокотехнологическая\nмедицинская помощь')
        table.setText(i0, 1, 2)
        table.setText(i0, 2, u'число койко-дней');          table.setText(i0, 3, reportData[1][1])
        table.setText(i1, 2, u'число законченных случаев'); table.setText(i1, 3, reportData[1][5])
        table.setText(i2, 2, u'число выбывших больных');    table.setText(i2, 3, reportData[1][0])

        i0 = table.addRow()
        i1 = table.addRow()
        i2 = table.addRow()
        table.mergeCells(i0, 0, 3, 1)
        table.mergeCells(i0, 1, 3, 1)
        table.setText(i0, 0, u'-специализированная\nмедицинская помощь')
        table.setText(i0, 1, 3)
        table.setText(i0, 2, u'число койко-дней');          table.setText(i0, 3, reportData[2][1])
        table.setText(i1, 2, u'число законченных случаев'); table.setText(i1, 3, reportData[2][5])
        table.setText(i2, 2, u'число выбывших больных');    table.setText(i2, 3, reportData[2][0])

        i0 = table.addRow()
        i1 = table.addRow()
        i2 = table.addRow()
        table.mergeCells(i0, 0, 3, 1)
        table.mergeCells(i0, 1, 3, 1)
        table.setText(i0, 0, u'Скорая медицинская помощь')
        table.setText(i0, 1, 4)
        table.setText(i0, 2, u'число вызывов');             table.setText(i0, 3, reportData[3][3])
        table.setText(i1, 2, u'число обслуживаемых лиц');   table.setText(i1, 3, reportData[3][0])
        table.setText(i2, 2, u'число законченных случаев'); table.setText(i2, 3, reportData[3][5])

        i0 = table.addRow()
        i1 = table.addRow()
        i2 = table.addRow()
        table.mergeCells(i0, 0, 3, 1)
        table.mergeCells(i0, 1, 3, 1)
        table.setText(i0, 0, u'Скорая специализированная медицинская помощь')
        table.setText(i0, 1, 5)
        table.setText(i0, 2, u'число вызывов');             table.setText(i0, 3, reportData[4][3])
        table.setText(i1, 2, u'число обслуживаемых лиц');   table.setText(i1, 3, reportData[4][0])
        table.setText(i2, 2, u'число законченных случаев'); table.setText(i2, 3, reportData[4][5])

        i0 = table.addRow()
        i1 = table.addRow()
        i2 = table.addRow()
        i3 = table.addRow()
        table.mergeCells(i0, 0, 4, 1)
        table.mergeCells(i0, 1, 4, 1)
        table.setText(i0, 0, u'Амбулаторная медицинская помощь')
        table.setText(i0, 1, 6)
        table.setText(i0, 2, u'число услуг');               table.setText(i0, 3, reportData[5][4])
        table.setText(i1, 2, u'число посещений');           table.setText(i1, 3, reportData[5][2])
        table.setText(i2, 2, u'число законченных случаев'); table.setText(i2, 3, reportData[5][5])
        table.setText(i3, 2, u'число случаев учёта по подушевому нормативу');   table.setText(i3, 3, reportData[5][3])

        i0 = table.addRow()
        i1 = table.addRow()
        i2 = table.addRow()
        table.mergeCells(i0, 0, 3, 1)
        table.mergeCells(i0, 1, 3, 1)
        table.setText(i0, 0, u'Медицинская помощь, оказанная в условиях дневных стационаров')
        table.setText(i0, 1, 7)
        table.setText(i0, 2, u'число пациенто-дней');       table.setText(i0, 3, reportData[6][1])
        table.setText(i1, 2, u'число законченных случаев'); table.setText(i1, 3, reportData[6][5])
        table.setText(i2, 2, u'число выбывших больных');    table.setText(i2, 3, reportData[6][0])


        i0 = table.addRow()
        i1 = table.addRow()
        i2 = table.addRow()
        table.mergeCells(i0, 0, 3, 1)
        table.mergeCells(i0, 1, 3, 1)
        table.setText(i0, 0, u'Санаторно-курортная медицинская помощь')
        table.setText(i0, 1, 8)
        table.setText(i0, 2, u'число койко-дней');          table.setText(i0, 3, reportData[7][1])
        table.setText(i1, 2, u'число выбывших больных');    table.setText(i1, 3, reportData[7][0])
        table.setText(i2, 2, u'число законченных случаев'); table.setText(i2, 3, reportData[7][5])

        return doc


class CMUOMSOFSetupDialog(CDialogBase, Ui_MUOMSOFSetupDialog):
    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.cmbEventPurpose.setTable('rbEventTypePurpose', True, filter='code != \'0\'')
        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbSpeciality.setTable('rbSpeciality', True)
        self.setGroupTypeVisible(False)


    def setGroupTypeVisible(self, value):
        self.isGroupTypeVisible = value
        self.lblGroupType.setVisible(value)
        self.cmbGroupType.setVisible(value)

    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbEventPurpose.setValue(params.get('eventPurposeId', None))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbSpeciality.setValue(params.get('specialityId', None))
        self.cmbPerson.setValue(params.get('personId', None))
        self.cmbContracts.setPath(params.get('contractPath', ''))
        self.cmbInsurer.setValue(params.get('insurerId', None))
        self.cmbSex.setCurrentIndex(params.get('sex', 0))
        self.edtAgeFrom.setValue(params.get('ageFrom', 0))
        self.edtAgeTo.setValue(params.get('ageTo', 150))
        if self.isGroupTypeVisible:
            self.cmbGroupType.setCurrentIndex(params.get('groupType', 0))


    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['eventPurposeId'] = self.cmbEventPurpose.value()
        result['eventTypeId'] = self.cmbEventType.value()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['specialityId'] = self.cmbSpeciality.value()
        result['personId'] = self.cmbPerson.value()
        result['contractPath'] = self.cmbContracts.getPath()
        result['contractIdList'] = self.cmbContracts.getIdList()
        result['insurerId'] = self.cmbInsurer.value()
        result['sex'] = self.cmbSex.currentIndex()
        result['ageFrom'] = self.edtAgeFrom.value()
        result['ageTo'] = self.edtAgeTo.value()
        if self.isGroupTypeVisible:
            result['groupType'] = self.cmbGroupType.currentIndex()
        return result


    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.cmbPerson.setEndDate(date)


    @QtCore.pyqtSlot(int)
    def on_cmbEventPurpose_currentIndexChanged(self, index):
        eventPurposeId = self.cmbEventPurpose.value()
        if eventPurposeId:
            filter = 'EventType.purpose_id =%d' % eventPurposeId
        else:
            filter = getWorkEventTypeFilter()
        self.cmbEventType.setFilter(filter)


    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)


    @QtCore.pyqtSlot(int)
    def on_cmbSpeciality_currentIndexChanged(self, index):
        specialityId = self.cmbSpeciality.value()
        self.cmbPerson.setSpecialityId(specialityId)
