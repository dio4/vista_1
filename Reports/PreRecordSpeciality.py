# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Action              import CAction
from library.Utils              import forceDate, forceInt, forceRef, forceString, firstMonthDay, lastMonthDay, \
                                       formatName
from Orgs.Utils                 import getOrgStructureDescendants, getOrgStructureFullName, getPersonInfo
from Reports.PreRecordDoctors   import CPreRecord
from Reports.Report             import CReport
from Reports.ReportBase         import createTable, CReportBase

from Ui_PreRecordSpecialityDialog import Ui_PreRecordSpecialityDialog


def selectData(params):
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    tablePerson = db.table('Person')
    tableAction = db.table('Action')
    tableActionType = db.table('ActionType')
    tableAction = tableAction.alias('NeedAction')

    cond   = []
    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)
    begDateRecord = params.get('begDateBeforeRecord', None)
    endDateRecord = params.get('endDateBeforeRecord', None)
    personId = params.get('personId', None)
    orgStructureId = params.get('orgStructureId', None)
    specialityId = params.get('specialityId', None)
    chkPeriodRecord = params.get('chkPeriodRecord', None)
    chkPeriodBeforeRecord =  params.get('chkPeriodBeforeRecord', None)
    acceptanceType = params.get('acceptanceType', 0)
    showWithoutOverTime = params.get('showWithoutOverTime', None)
    ignoreRehabilitation = params.get('ignoreRehabilitation', None)
    
    if chkPeriodRecord:
        if begDate:
            cond.append(tableAction['createDatetime'].dateGe(begDate))
        if endDate:
            cond.append(tableAction['createDatetime'].dateLe(endDate))
    if chkPeriodBeforeRecord:
        if begDateRecord:
            cond.append(tableAction['directionDate'].dateGe(begDateRecord))
        if endDateRecord:
            cond.append(tableAction['directionDate'].dateLe(endDateRecord))
    if personId:
        cond.append(tableAction['person_id'].eq(personId))
    if orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
#    else:
#        if not personId:
#            cond.append(tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()))
    if specialityId:
        cond.append(tablePerson['speciality_id'].eq(specialityId))
    if acceptanceType:
        cond.append(tableActionType['code'].like(['amb', 'home'][acceptanceType-1]))
    if showWithoutOverTime:
        cond.append('APTime.value IS NOT NULL')
    if ignoreRehabilitation:
        cond.append(tablePerson['orgStructure_id'].notInlist(db.getIdList('OrgStructure', where = u'name LIKE "%реабилитац%"' )))
    
    stmt = '''
    SELECT Action.event_id AS eventId, Person.id, Person.lastName, Person.firstName, Person.patrName, NeedAction.id AS Action_id, ActionType.code AS ambOrHome, NeedAction.person_id AS executer, NeedAction.setPerson_id AS setPerson,
NeedAction.directionDate, NeedAction.note AS actionNote, Event.client_id, Person.speciality_id AS personSpeciality, SetPerson.speciality_id AS setPersonSpeciality, SetPerson.org_id AS setPersonOrgId,
Person.orgStructure_id AS orgStructureId, SetPerson.orgStructure_id AS setOrgStructureId

    FROM ActionProperty_Action
    LEFT JOIN ActionProperty ON ActionProperty.id = ActionProperty_Action.id
    LEFT JOIN Action ON Action.id = ActionProperty.action_id
    LEFT JOIN ActionType ON ActionType.id = Action.actionType_id
    LEFT JOIN Action AS NeedAction ON NeedAction.id = ActionProperty_Action.value
    LEFT JOIN Event ON Event.id = NeedAction.event_id
    LEFT JOIN Person ON Person.id = NeedAction.person_id
    LEFT JOIN Person AS SetPerson ON SetPerson.id = NeedAction.setPerson_id
    LEFT JOIN ActionProperty AS APTimes ON APTimes.action_id = Action.id 
                                        AND APTimes.type_id = (SELECT id 
                                                               FROM ActionPropertyType AS APT 
                                                               WHERE APT.name LIKE 'times' AND APT.actionType_id = ActionType.id 
                                                               LIMIT 1)
    LEFT JOIN ActionProperty_Time AS APTime ON APTime.id = APTimes.id AND APTime.index = ActionProperty_Action.index

    WHERE ActionProperty_Action.value IS NOT NULL AND Person.speciality_id IS NOT NULL AND %s

    ORDER BY Person.orgStructure_id, Person.speciality_id''' % (db.joinAnd(cond))
    return db.query(stmt)


def selectDataPlan(params, eventIdList):
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    tablePerson = db.table('Person')
    tableAction = db.table('Action')
    tableAction = tableAction.alias('NeedAction')
    tableActionType = db.table('ActionType')

    cond   = []
    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)
    begDateRecord = params.get('begDateBeforeRecord', None)
    endDateRecord = params.get('endDateBeforeRecord', None)
    personId = params.get('personId', None)
    orgStructureId = params.get('orgStructureId', None)
    specialityId = params.get('specialityId', None)
    chkPeriodRecord = params.get('chkPeriodRecord', None)
    chkPeriodBeforeRecord =  params.get('chkPeriodBeforeRecord', None)
    acceptanceType = params.get('acceptanceType', 0)
    ignoreRehabilitation = params.get('ignoreRehabilitation', None)
    
    if chkPeriodRecord:
        if begDate:
            cond.append(tableEvent['createDatetime'].dateGe(begDate))
        if endDate:
            cond.append(tableEvent['createDatetime'].dateLe(endDate))
    if chkPeriodBeforeRecord:
        if begDateRecord:
            cond.append(tableEvent['setDate'].dateGe(begDateRecord))
        if endDateRecord:
            cond.append(tableEvent['setDate'].dateLe(endDateRecord))
    if personId:
        cond.append(tableEvent['execPerson_id'].eq(personId))
    if orgStructureId:
        cond.append(db.joinOr([tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)), tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId))]))
    else:
        if not personId:
            cond.append(db.joinOr([tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()), tablePerson['org_id'].eq(QtGui.qApp.currentOrgId())]))
    if specialityId:
        cond.append(db.joinOr([tablePerson['speciality_id'].eq(specialityId), tablePerson['speciality_id'].eq(specialityId)]))
    if eventIdList:
        cond.append(tableEvent['id'].notInlist(eventIdList))
    if acceptanceType:
        cond.append(tableActionType['code'].like(['amb', 'home'][acceptanceType-1]))
    if ignoreRehabilitation:
        cond.append(tablePerson['orgStructure_id'].notInlist(db.getIdList('OrgStructure', where = u'name LIKE "%реабилитац%"' )))
    stmt = '''
    SELECT Action.event_id AS eventId, Action.id AS actionId, ActionType.code AS ambOrHome, Person.id, Person.lastName, Person.firstName, Person.patrName, Person.speciality_id AS personSpeciality, Person.orgStructure_id AS orgStructureId
    FROM Event
    INNER JOIN EventType ON EventType.id = Event.eventType_id
    INNER JOIN Action ON Event.id = Action.event_id
    INNER JOIN ActionType ON ActionType.id = Action.actionType_id
    INNER JOIN Person ON Person.id = Event.execPerson_id
    WHERE EventType.code LIKE '0' AND Event.deleted = 0 AND Action.deleted = 0 AND ActionType.deleted = 0 AND EventType.deleted = 0 AND %s
    ORDER BY Person.orgStructure_id, Person.speciality_id''' % (db.joinAnd(cond))
    return db.query(stmt)


class CPreRecordSpeciality(CReport, CPreRecord):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Предварительная запись по специальности')
        self.orgStructSpecialityPersonList = {}
        self.eventIdList = []
        self.orgStructureNameList = {}
        self.specialityNameList = {}
        self.orgStructureAddress = {}
        self.actionIdList = []


    def dumpParams(self, cursor, params):
        description = []
        db = QtGui.qApp.db
        def dateRangeAsStr(begDate, endDate):
            result = ''
            if begDate:
                result += u' с '+forceString(begDate)
            if endDate:
                result += u' по '+forceString(endDate)
            return result
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        begDateBeforeRecord = params.get('begDateBeforeRecord', QtCore.QDate())
        endDateBeforeRecord = params.get('endDateBeforeRecord', QtCore.QDate())
        orgStructureId = params.get('orgStructureId', None)
        specialityId = params.get('specialityId', None)
        personId = params.get('personId', None)
        detailOnOrgStructure = params.get('detailOnOrgStructure', False)
        detailOnPerson = params.get('detailOnPerson', False)
        chkPeriodRecord = params.get('chkPeriodRecord', None)
        chkPeriodBeforeRecord = params.get('chkPeriodBeforeRecord', None)
        acceptanceType = params.get('acceptanceType', 0)
        if chkPeriodRecord:
            if begDate or endDate:
                description.append(u'за период' + dateRangeAsStr(begDate, endDate))
        if chkPeriodBeforeRecord:
            if begDateBeforeRecord or endDateBeforeRecord:
                description.append(u'период предварительной записи' + dateRangeAsStr(begDateBeforeRecord, endDateBeforeRecord))
        if orgStructureId:
            description.append(u'подразделение: ' + getOrgStructureFullName(orgStructureId))
        else:
            description.append(u'подразделение: ЛПУ')
        if specialityId:
            description.append(u'специальность: ' + forceString(db.translate('rbSpeciality', 'id', specialityId, 'name')))
        if personId:
            personInfo = getPersonInfo(personId)
            description.append(u'врач: ' + personInfo['shortName']+', '+personInfo['specialityName'])
        if detailOnOrgStructure:
            description.append(u'с детализацией по подразделениям')
        if detailOnPerson:
            description.append(u'с детализацией по врачам')
        description.append(u'прием: %s'%([u'все', u'амбулаторно', u'на дому'][acceptanceType]))
        description.append(u'отчёт составлен: '+forceString(QtCore.QDateTime.currentDateTime()))
        columns = [ ('100%', [], CReportBase.AlignLeft) ]
        table = createTable(cursor, columns, headerRowCount=len(description), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(description):
            table.setText(i, 0, row)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()


    def build(self, params):
        self.eventIdList = []
        self.orgStructureNameList = {}
        self.specialityNameList = {}
        self.actionIdList = []
        self.orgStructSpecialityPersonList = {}
        self.orgStructureAddress = {}
        self.detailOnOrgStructure = params.get('detailOnOrgStructure', False)
        self.detailOnPerson = params.get('detailOnPerson', False)
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        self.makeTable(cursor, doc, params)
        return doc

    def makeTable(self, cursor, doc, params):
        tableColumns = [('2%',[u'№', u''], CReportBase.AlignLeft),
                        ('23%', [u'Врачи', u''], CReportBase.AlignLeft),
                        ('15%', [u'Количество выделенных номерков за период', u''], CReportBase.AlignCenter),
                        ('15%', [u'В том числе', u'Занято номерков на первичный прием'], CReportBase.AlignCenter),
                        ('15%', [u'', u'Занято номерков на вторичный прием'], CReportBase.AlignRight),
                        ('15%', [u'', u'Количество не использованных номерков'], CReportBase.AlignRight),
                        ('15%', [u'Выполнено', u''], CReportBase.AlignRight)
                        ]
        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 1, 3)
        table.mergeCells(0, 6, 2, 1)

        if self.detailOnOrgStructure:
            self.orgStructureNameList = {None:'ЛПУ'}
            db = QtGui.qApp.db
            tableOS = db.table('OrgStructure')
            records = db.getRecordList(tableOS, [tableOS['id'], tableOS['name']], [tableOS['deleted'].eq(0)])
            for record in records:
                orgStructureId = forceRef(record.value('id'))
                orgStructureName = forceString(record.value('name'))
                if orgStructureId:
                    self.orgStructureNameList[orgStructureId] = orgStructureName

        self.specialityNameList = {None:''}
        db = QtGui.qApp.db
        tableSP = db.table('rbSpeciality')
        records = db.getRecordList(tableSP, [tableSP['id'], tableSP['name']])
        for record in records:
            specialityId = forceRef(record.value('id'))
            specialityName = forceString(record.value('name'))
            if specialityId:
                self.specialityNameList[specialityId] = specialityName
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        acceptanceType = params.get('acceptanceType', 0)
        self.getParseQueryInfo(query, acceptanceType)
        queryPlan = selectDataPlan(params, self.eventIdList)
        self.getParseQueryInfoPlan(queryPlan, acceptanceType)
        resume = [u'Итого']+[0]*5
        n = 1
        keysOS = self.orgStructSpecialityPersonList.keys()
        keysOS.sort()
        orgStructList = []
        specialityList = []
        resultList = [u'Итого']+[0]*5
        boldChars = QtGui.QTextCharFormat()
        boldChars.setFontWeight(QtGui.QFont.Bold)
        if self.detailOnOrgStructure and self.detailOnPerson:
            for keyOS in keysOS:
                specialityPersonList = self.orgStructSpecialityPersonList[keyOS]
                i = table.addRow()
                table.setText(i, 0, n)
                table.setText(i, 1, keyOS[1], charFormat=boldChars)
                n += 1
                orgStructList = [keyOS[1]]+([0]*5)
                keysSP = specialityPersonList.keys()
                keysSP.sort()
                for keySP in keysSP:
                    personList = specialityPersonList[keySP]
                    i2 = table.addRow()
                    table.setText(i2, 0, n)
                    table.setText(i2, 1, keySP[1], charFormat=boldChars)
                    n += 1
                    specialityList = [keySP[1]]+([0]*5)
                    keysP = personList.keys()
                    keysP.sort()
                    for keyP in keysP:
                        personInfo = personList[keyP]
                        i3 = table.addRow()
                        table.setText(i3, 0, n)
                        table.setText(i3, 1, keyP[1])
                        n += 1
                        for column in range(1, 6):
                            table.setText(i3, column+1, personInfo[column])
                            orgStructList[column] += personInfo[column]
                            specialityList[column] += personInfo[column]
                            resultList[column] += personInfo[column]
                    for column in range(1, 6):
                        table.setText(i2, column+1, specialityList[column], charFormat=boldChars)
                for column in range(1, 6):
                    table.setText(i, column+1, orgStructList[column], charFormat=boldChars)
        elif self.detailOnOrgStructure:
            for keyOS in keysOS:
                specialityPersonList = self.orgStructSpecialityPersonList[keyOS]
                i = table.addRow()
                table.setText(i, 0, n)
                table.setText(i, 1, keyOS[1], charFormat=boldChars)
                n += 1
                orgStructList = [keyOS[1]]+([0]*5)
                keysSP = specialityPersonList.keys()
                keysSP.sort()
                for keySP in keysSP:
                    personList = specialityPersonList[keySP]
                    i2 = table.addRow()
                    table.setText(i2, 0, n)
                    table.setText(i2, 1, keySP[1])
                    n += 1
                    for column in range(1, 6):
                        table.setText(i2, column+1, personList[column])
                        orgStructList[column] += personList[column]
                        resultList[column] += personList[column]
                for column in range(1, 6):
                    table.setText(i, column+1, orgStructList[column], charFormat=boldChars)
        elif self.detailOnPerson:
            for keyOS in keysOS:
                specialityPersonList = self.orgStructSpecialityPersonList[keyOS]
                i = table.addRow()
                table.setText(i, 0, n)
                table.setText(i, 1, keyOS[1], charFormat=boldChars)
                n += 1
                specialityList = [keyOS[1]]+([0]*5)
                keysP = specialityPersonList.keys()
                keysP.sort()
                for keyP in keysP:
                    personInfo = specialityPersonList[keyP]
                    i3 = table.addRow()
                    table.setText(i3, 0, n)
                    table.setText(i3, 1, keyP[1])
                    n += 1
                    for column in range(1, 6):
                        table.setText(i3, column+1, personInfo[column])
                        specialityList[column] += personInfo[column]
                        resultList[column] += personInfo[column]
                for column in range(1, 6):
                    table.setText(i, column+1, specialityList[column], charFormat=boldChars)
        else:
            for keyOS in keysOS:
                specialityPersonList = self.orgStructSpecialityPersonList[keyOS]
                i3 = table.addRow()
                table.setText(i3, 0, n)
                table.setText(i3, 1, keyOS[1])
                n += 1
                for column in range(1, 6):
                    table.setText(i3, column+1, specialityPersonList[column])
                    resultList[column] += specialityPersonList[column]
        i4  = table.addRow()
        table.setText(i4, 0, n)
        for column in range(6):
            table.setText(i4, column+1, resultList[column], charFormat=boldChars)
        self.orgStructSpecialityPersonList.clear()


    def getParseQueryInfo(self, query, acceptanceType):
        self.a = 0
        recordList = self.makeNeedfulDicts(query)
        for record in recordList:
            dataList, key, name = self.parseQueryInfo(record)
            afore = dataList.get(key, None)
            if afore:
                dataList = self.addInfo(record, key, dataList, acceptanceType)
            else:
                dataList[key] = [name]+([0]*5)
                dataList = self.addInfo(record, key, dataList, acceptanceType)


    def getParseQueryInfoPlan(self, query, acceptanceType):
        self.a = 0
        while query.next():
            record = query.record()
            dataList, key, name = self.parseQueryInfo(record)
            afore = dataList.get(key, None)
            if afore:
                dataList = self.addInfoPlan(record, key, dataList, acceptanceType)
            else:
                dataList[key] = [name]+([0]*5)
                dataList = self.addInfoPlan(record, key, dataList, acceptanceType)


    def parseQueryInfo(self, record):
        self.a = 0
        specialityPersonList = {}
        dataList = {}
        personId = forceInt(record.value('id'))
        personName = formatName(record.value('lastName'),
                          record.value('firstName'),
                          record.value('patrName'))
        orgStructureId = forceRef(record.value('orgStructureId'))
        personSpecialityId = forceRef(record.value('personSpeciality'))
        if self.detailOnOrgStructure:
            orgStructureName = u''
            if orgStructureId:
                if orgStructureId not in self.orgStructureAddress.keys():
                    orgStructureInfo = self.getOrgStructureParents(orgStructureId)
                    if orgStructureInfo:
                        orgStructureIdOld = orgStructureId
                        orgStructureId = orgStructureInfo['id']
                        orgStructureName = orgStructureInfo['name'] + u' ' + orgStructureInfo['address']
                        self.orgStructureAddress[orgStructureIdOld] = (orgStructureId, orgStructureName)
                        key = (orgStructureId, orgStructureName)
                    else:
                        orgStructureName = self.orgStructureNameList.get(orgStructureId, '')
                        key = (orgStructureId, orgStructureName)
                else:
                    key = self.orgStructureAddress.get(orgStructureId, (orgStructureId, orgStructureName))
                    orgStructureName = key[1]
                    orgStructureId = key[0]
            else:
                orgStructureName = self.orgStructureNameList.get(orgStructureId, '')
                key = (orgStructureId, orgStructureName)
            name = orgStructureName
            if (orgStructureId, orgStructureName) not in self.orgStructSpecialityPersonList.keys():
                self.orgStructSpecialityPersonList[(orgStructureId, orgStructureName)] = {}
            specialityPersonList = self.orgStructSpecialityPersonList.get((orgStructureId, orgStructureName), {})
        else:
            specialityPersonList = self.orgStructSpecialityPersonList
        specialityName = self.specialityNameList.get(personSpecialityId, '')
        key = (personSpecialityId, specialityName)
        name = specialityName
        if self.detailOnPerson:
            if (personSpecialityId, specialityName) not in specialityPersonList.keys():
                specialityPersonList[(personSpecialityId, specialityName)] = {}
            dataList = specialityPersonList.get((personSpecialityId, specialityName), {})
        else:
            if (personSpecialityId, specialityName) not in specialityPersonList.keys():
                specialityPersonList[(personSpecialityId, specialityName)] = []
            dataList = specialityPersonList
        if self.detailOnPerson:
            key = (personId, personName)
            name = personName
            if (personId, personName) not in dataList.keys():
                dataList[(personId, personName)] = []
        return dataList, key, name


    def getOrgStructureParents(self, orgStructureId):
        db = QtGui.qApp.db
        table = db.table('OrgStructure')
        parentId = orgStructureId
        address = None
        orgStructureInfo = {}
        while parentId and not address:
            record = db.getRecordEx(table, [table['id'], table['parent_id'], table['name'], table['address']], [table['id'].eq(orgStructureId), table['deleted'].eq(0)])
            parentId = None
            if record:
                id = forceRef(record.value('id'))
                parentId = forceRef(record.value('parent_id'))
                name = forceString(record.value('name'))
                address = forceString(record.value('address'))
                orgStructureId = parentId
                if address:
                    orgStructureInfo = {'id':id, 'parentId':parentId, 'name':name, 'address':address}
        return orgStructureInfo


    def addInfo(self, record, key, dataList, acceptanceType):
        actionId            = forceInt(record.value('ActionId'))
        personId            = forceInt(record.value('id'))
        orgStructureId = forceRef(record.value('orgStructureId'))
        personSpecialyty = forceRef(record.value('personSpeciality'))
        actionType          = forceString(record.value('ambOrHome'))
        executer            = forceInt(record.value('executer'))
        setPerson           = forceInt(record.value('setPerson'))
        setPersonSpeciality = forceInt(record.value('setPersonSpeciality'))
        setPersonOrgId      = forceInt(record.value('setPersonOrgId'))
        clientId            = forceRef(record.value('client_id'))
        directionDateAction = forceDate(record.value('directionDate'))
        actionNote          = forceString(record.value('actionNote'))
        setOrgStructureId   = forceRef(record.value('setOrgStructureId'))
        eventId             = forceRef(record.value('eventId'))
        if actionType == 'amb' or actionType == 'home':
            column = 1
        else:
            column = None
        if column:
            if eventId and eventId not in self.eventIdList:
                self.eventIdList.append(eventId)
                if acceptanceType == 0 or acceptanceType == 1:
                    timeTableActionAmb  = CAction.getAction(eventId, 'amb')
                    timesAmb = timeTableActionAmb['times']
                    dataList[key][column] += len(timesAmb)
                    dataList[key][column+3] += len(timesAmb)
                if acceptanceType == 0 or acceptanceType == 2:
                    timeTableActionHome  = CAction.getAction(eventId, 'home')
                    timesHome = timeTableActionHome['times']
                    dataList[key][column] += len(timesHome)
                    dataList[key][column+3] += len(timesHome)
            visit, eventId = self.getVisit(directionDateAction, personId, personSpecialyty, self.recordVisitByDate, clientId)
            if visit:
                dataList[key][column+4] += 1
            if setPerson and setPersonOrgId == QtGui.qApp.currentOrgId():
                if setPersonSpeciality:
                    if executer == setPerson:
                        column += 2
                    else:
                        column += 1
                else:
                    column += 1
            else:
                column += 1
            dataList[key][column] += 1
            if dataList[key][4] > 0:
                dataList[key][4] -= 1
        return dataList


    def addInfoPlan(self, record, key, dataList, acceptanceType):
        actionType = forceString(record.value('ambOrHome'))
        eventId    = forceRef(record.value('eventId'))
        if actionType == 'amb' or actionType == 'home':
            column = 1
        else:
            column = None
        if column:
            if eventId and eventId not in self.eventIdList:
                self.eventIdList.append(eventId)
                if acceptanceType == 0 or acceptanceType == 1:
                    timeTableActionAmb  = CAction.getAction(eventId, 'amb')
                    timesAmb = timeTableActionAmb['times']
                    dataList[key][column] += len(timesAmb)
                    dataList[key][column+3] += len(timesAmb)
                if acceptanceType == 0 or acceptanceType == 2:
                    timeTableActionHome  = CAction.getAction(eventId, 'home')
                    timesHome = timeTableActionHome['times']
                    dataList[key][column] += len(timesHome)
                    dataList[key][column+3] += len(timesHome)
        return dataList


class CPreRecordSpecialityEx(CPreRecordSpeciality):
    def exec_(self):
        CPreRecordSpeciality.exec_(self)

    def getSetupDialog(self, parent):
        result = CPreRecordSpecialityDialog(parent)
        result.setTitle(self.title())
        return result


class CPreRecordSpecialityDialog(QtGui.QDialog, Ui_PreRecordSpecialityDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbSpeciality.setTable('rbSpeciality', True)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())


    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        date = QtCore.QDate.currentDate().addDays(-3)
        self.edtBegDate.setDate(params.get('begDate', firstMonthDay(date)))
        self.edtEndDate.setDate(params.get('endDate', lastMonthDay(date)))
        self.edtBegDateRecord.setDate(params.get('begDateBeforeRecord', firstMonthDay(date)))
        self.edtEndDateRecord.setDate(params.get('endDateBeforeRecord', lastMonthDay(date)))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbSpeciality.setValue(params.get('specialityId', None))
        self.cmbPerson.setValue(params.get('personId', None))
        self.chkDetailOnOrgStructure.setChecked(params.get('detailOnOrgStructure', False))
        self.chkDetailOnPerson.setChecked(params.get('detailOnPerson', False))
        self.cmbAcceptanceType.setCurrentIndex(params.get('acceptanceType', 0))


    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['begDateBeforeRecord'] = self.edtBegDateRecord.date()
        result['endDateBeforeRecord'] = self.edtEndDateRecord.date()
        result['chkPeriodRecord'] = self.chkPeriodRecord.isChecked()
        result['chkPeriodBeforeRecord'] = self.chkPeriodBeforeRecord.isChecked()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['specialityId'] = self.cmbSpeciality.value()
        result['personId'] = self.cmbPerson.value()
        result['detailOnOrgStructure'] = self.chkDetailOnOrgStructure.isChecked()
        result['detailOnPerson'] = self.chkDetailOnPerson.isChecked()
        result['acceptanceType'] = self.cmbAcceptanceType.currentIndex()
        result['showWithoutOverTime'] = self.chkShowWithoutOverTime.isChecked()
        result['ignoreRehabilitation'] = self.chkIgnoreRehabilitation.isChecked()
        return result


    @QtCore.pyqtSlot(bool)
    def on_chkPeriodRecord_clicked(self, checked):
        self.edtBegDate.setEnabled(checked)
        self.edtEndDate.setEnabled(checked)
        if checked:
            self.edtBegDate.setFocus(QtCore.Qt.OtherFocusReason)


    @QtCore.pyqtSlot(bool)
    def on_chkPeriodBeforeRecord_clicked(self, checked):
        self.edtBegDateRecord.setEnabled(checked)
        self.edtEndDateRecord.setEnabled(checked)


    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.cmbPerson.setEndDate(QtCore.QDate(date))


    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)


    @QtCore.pyqtSlot(int)
    def on_cmbSpeciality_currentIndexChanged(self, index):
        specialityId = self.cmbSpeciality.value()
        self.cmbPerson.setSpecialityId(specialityId)
