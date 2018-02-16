# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils          import forceBool, forceDouble, forceInt, forceString
from Orgs.Utils             import getOrgStructureDescendants
from Reports.Report         import CReport
from Reports.ReportBase     import createTable, CReportBase
from Reports.MUOMSOFTable1  import CMUOMSOFSetupDialog


def selectData(begDate, endDate, eventPurposeId, eventTypeId, orgStructureId, specialityId, personId, contractIdList, insurerId, sex, ageFrom, ageTo, groupType):
    stmt="""
SELECT
    rbMedicalAidType.name  AS aidTypeName,
    %s
    (Event.execDate >= ADDDATE(Client.birthDate, INTERVAL 18 YEAR)) AS isAdult,
    IF(mes.MES.id IS NOT NULL, mes.MES.code, ActionType.code) AS mesCode,
    IF(mes.MES.id IS NOT NULL, mes.MES.name, ActionType.name) AS mesName,
    (Account_Item.date IS NOT NULL AND Account_Item.number != '' AND Account_Item.refuseType_id IS NULL) AS exposed,
    (Account_Item.date IS NOT NULL AND Account_Item.number != '' AND Account_Item.refuseType_id IS NOT NULL) as refused,
    COUNT(Account_Item.id) AS cnt,
    SUM(Account_Item.`amount`)  AS `amount`,
    SUM(Account_Item.`sum`)     AS `sum`
FROM
    Account_Item
    INNER JOIN Account    ON Account.id = Account_Item.master_id
    INNER JOIN Event      ON Event.id = Account_Item.event_id
    INNER JOIN EventType  ON EventType.id = Event.eventType_id
    INNER JOIN Client     ON Client.id = Event.client_id
    LEFT  JOIN Action     ON Action.id = Account_Item.action_id
    LEFT  JOIN ActionType ON ActionType.id = Action.actionType_id
    LEFT  JOIN vrbPersonWithSpeciality ON vrbPersonWithSpeciality.id = Event.execPerson_id
    LEFT  JOIN rbMedicalAidType ON rbMedicalAidType.id = EventType.medicalAidType_id
    LEFT  JOIN rbEventProfile ON rbEventProfile.id = EventType.eventProfile_id
    LEFT  JOIN ClientPolicy ON ClientPolicy.id = getClientPolicyId(Event.client_id, 1)
    LEFT  JOIN Diagnosis  ON Diagnosis.id = getEventDiagnosis(Event.id)
    LEFT  JOIN mes.MES    ON mes.MES.id = Event.MES_id
WHERE
    (ActionType.isMES OR Event.MES_id) AND Account_Item.reexposeItem_id IS NULL AND Account_Item.deleted=0 AND Account.deleted=0 AND %s
GROUP BY
    EventType.medicalAidType_id, %s isAdult, exposed, refused, mesCode, mesName
"""
    db = QtGui.qApp.db
    tableEvent  = db.table('Event')
    tableClient = db.table('Client')
    tablePerson = db.table('vrbPersonWithSpeciality')
    tableAccount = db.table('Account')
    tableClientPolicy = db.table('ClientPolicy')
    cond = []
    cond.append(tableEvent['deleted'].eq(0))
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
    if groupType == 1:
        fieldName = 'rbEventProfile.name AS groupName, '
        groupField = 'EventType.eventProfile_id, '
    elif groupType == 2:
        fieldName = 'EventType.name AS groupName, '
        groupField = 'EventType.id, '
    else:
        fieldName = ''
        groupField = ''
    return db.query(stmt % (fieldName, db.joinAnd(cond), groupField))


class CReportF14App3ksg(CReport):
    name = u'Приложение №3-КСГ к отчёту по форме №14-Ф'

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(self.name)


    def getSetupDialog(self, parent):
        result = CMUOMSOFSetupDialog(parent)
        result.setTitle(self.title())
        result.setGroupTypeVisible(True)
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
        groupType = params.get('groupType', None)

        rowSize = 5
        reportData = {}

        query = selectData(begDate, endDate, eventPurposeId, eventTypeId, orgStructureId, specialityId, personId, contractIdList, insurerId, sex, ageFrom, ageTo, groupType)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            aidTypeName = forceString(record.value('aidTypeName'))
            groupName   = forceString(record.value('groupName'))
            isAdult     = forceBool(record.value('isAdult'))
            mesCode     = forceString(record.value('mesCode'))
            mesName     = forceString(record.value('mesName'))
            exposed     = forceBool(record.value('exposed'))
            refused     = forceBool(record.value('refused'))
            cnt         = forceInt(record.value('cnt'))
            amount      = forceDouble(record.value('amount'))
            sum         = forceDouble(record.value('sum'))

            if not aidTypeName:
                aidTypeName = u'{тип помощи неопределён}'
            if groupType and not groupName:
                if groupType == 1:
                    groupName = u'{профиль события неопределён}'
                elif groupType == 2:
                    groupName = u'{тип действия неопределён}'
            reportGroupByAidType = reportData.setdefault(aidTypeName, {})
            reportGroupByAge = reportGroupByAidType.setdefault(isAdult, {})
            reportGroupByGroupName = reportGroupByAge.setdefault(groupName, {})
            key = (mesCode, mesName)
            reportLine = reportGroupByGroupName.get(key, None)
            if not reportLine:
                reportLine = [0]*rowSize
                reportGroupByGroupName[key] = reportLine
            reportLine[0] += cnt
            reportLine[1] += amount
            reportLine[2] += sum
            if refused:
                reportLine[3] += sum
            if exposed:
                reportLine[4] += sum

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.name)
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        cursor.insertText(u'Объёмы медицинской помощи и поступление средств ОМС')
        cursor.insertBlock()


        tableColumns = [
            ('3%',  [u'№'  ], CReportBase.AlignRight),
            ('5%',  [u'Код КСГ'], CReportBase.AlignLeft),
            ('20%', [u'Название КСГ'], CReportBase.AlignLeft),
            ('10%', [u'Количество случаев'], CReportBase.AlignRight),
            ('10%', [u'Наименование специалистов'], CReportBase.AlignLeft),
            ('10%', [u'Количество посещений/дней лечения'], CReportBase.AlignRight),
            ('10%', [u'Сумма по выставленным счетам, руб'], CReportBase.AlignRight),
            ('10%', [u'Сумма отказов по выставленным счетам, руб'], CReportBase.AlignRight),
            ('10%', [u'Сумма по оплаченным счетам, руб'], CReportBase.AlignRight),
            ]

        grandTotal = [0]*rowSize
        table = createTable(cursor, tableColumns)
        aidTypeList = reportData.keys()
        aidTypeList.sort()
        for aidTypeName in aidTypeList:
            aidTypeTotal = [0]*rowSize
            i = table.addRow()
            table.mergeCells(i, 0, 1, 9)
            table.setText(i, 0, aidTypeName, CReportBase.ReportSubTitle, CReportBase.AlignLeft)
            reportGroupByAidType = reportData[aidTypeName]
            for name, isAdult in [(u'Взрослая сеть',  True), (u'Детская сеть', False)]:
                reportGroupByAge = reportGroupByAidType.get(isAdult,  {})
                if reportGroupByAge:
                    i = table.addRow()
                    table.mergeCells(i, 0, 1, 9)
                    table.setText(i, 0, name, CReportBase.ReportSubTitle, CReportBase.AlignLeft)
                    total = [0]*rowSize
                    n = 0
                    groupNameList = reportGroupByAge.keys()
                    groupNameList.sort()
                    for groupName in groupNameList:
                        reportLineList = reportGroupByAge.get(groupName, [(), ()])
                        keys = reportLineList.keys()
                        keys.sort()
                        if groupType:
                            i = table.addRow()
                            table.mergeCells(i, 0, 1, 9)
                            table.setText(i, 0, groupName, CReportBase.ReportSubTitle, CReportBase.AlignLeft)
                        groupTotal = [0]*rowSize
                        for key in keys:
                            mesCode, mesName = key
                            reportLine = reportLineList[key]
                            i = table.addRow()
                            n += 1
                            table.setText(i, 1, mesCode)
                            table.setText(i, 2, mesName)
                            self.addRowData(table, i, n, reportLine)
                            groupTotal = map(lambda x,y: x+y, groupTotal, reportLine)
                        if groupType:
                            i = table.addRow()
                            table.mergeCells(i, 0, 1, 3)
                            self.addRowData(table, i, u'итого по \'%s\''%groupName, groupTotal, CReportBase.TableTotal)
                        total = map(lambda x,y: x+y, total, groupTotal)
                    i = table.addRow()
                    table.mergeCells(i, 0, 1, 3)
                    self.addRowData(table, i, u'итого', total, CReportBase.TableTotal)
                    aidTypeTotal = map(lambda x,y: x+y, aidTypeTotal, total)
            i = table.addRow()
            table.mergeCells(i, 0, 1, 3)
            self.addRowData(table, i, u'итого по '+aidTypeName, aidTypeTotal, CReportBase.TableTotal)
            grandTotal = map(lambda x,y: x+y, grandTotal, aidTypeTotal)
        i = table.addRow()
        table.mergeCells(i, 0, 1, 3)
        self.addRowData(table, i, u'Всего', grandTotal, CReportBase.TableTotal)
        return doc


    def addRowData(self, table, i, title, values, style=None):
        locale = QtCore.QLocale()
        table.setText(i, 0, title, style, CReportBase.AlignLeft)
        table.setText(i, 3, values[0], style)
        table.setText(i, 5, locale.toString(float(values[1]), 'f', 2), style)
        table.setText(i, 6, locale.toString(float(values[2]), 'f', 2), style)
        table.setText(i, 7, locale.toString(float(values[3]), 'f', 2), style)
        table.setText(i, 8, locale.toString(float(values[4]), 'f', 2), style)
