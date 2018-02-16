# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from operator           import itemgetter

from PyQt4 import QtGui, QtCore

from library.Utils      import forceDate, forceRef, forceString, forceTime, getVal, calcAge, formatName, smartDict,forceInt
from Orgs.Utils         import getOrgStructureFullName
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase


def selectData(params, actionTypeIdList):
    begDate = params.get('begDate', QtCore.QDate())


    db = QtGui.qApp.db

    purpose_id = forceRef(db.translate('rbEventTypePurpose', 'code', '8', 'id'))
    if not purpose_id :
        stmt=''
    else:
        stmt='purpose_id=%d ' % purpose_id
    eventTypeIdList = db.getIdList('EventType', where=stmt)

    tableEvent = db.table('Event')
    tableClient = db.table('Client')
    tableAction = db.table('Action')
    tableActionPropertyType = db.table('ActionPropertyType')
    tableActionProperty = db.table('ActionProperty')
    tableActionPropertyOS = db.table('ActionProperty_OrgStructure')
    tableActionPropertyString = db.table('ActionProperty_String')
    tableAPHB = db.table('ActionProperty_HospitalBed')
    tableOSHB = db.table('OrgStructure_HospitalBed')
    tableRBHospitalBedProfile = db.table('rbHospitalBedProfile')
    tableOrgStructure = db.table('OrgStructure')

    tableFromAPT = tableActionPropertyType.alias('FromAPT')
    tableFromAP  = tableActionProperty.alias('FromAP')
    tableFromAPOS= tableActionPropertyOS.alias('FromAPOS')
    tableFromOS  = tableOrgStructure.alias('FromOS')

    tableToAPT = tableActionPropertyType.alias('ToAPT')
    tableToAP  = tableActionProperty.alias('ToAP')
    tableToAPOS= tableActionPropertyOS.alias('ToAPOS')
    tableToOS  = tableOrgStructure.alias('ToOS')

    tableCurrAPT = tableActionPropertyType.alias('CurrAPT')
    tableCurrAP  = tableActionProperty.alias('CurrAP')
    tableCurrAPOS= tableActionPropertyOS.alias('CurrAPOS')
    tableCurrOS  = tableOrgStructure.alias('CurrOS')

    tablePatronageAPT = tableActionPropertyType.alias('PatronageAPT')
    tablePatronageAP  = tableActionProperty.alias('PatronageAP')
    tablePatronageAPS = tableActionPropertyString.alias('PatronageAPS')

    tableHBProfileAPT = tableActionPropertyType.alias('HBAPT')
    tableHBProfileAP  = tableActionProperty.alias('HBAP')


    queryTable = tableEvent.innerJoin(tableClient, [tableClient['id'].eq(tableEvent['client_id']),
                                                    tableClient['deleted'].eq(0),
                                                    tableEvent['deleted'].eq(0),
                                                    tableEvent['eventType_id'].inlist(eventTypeIdList)])
    #queryTable = queryTable.innerJoin(tableActionType, [tableActionType['flatCode'].eq('reanimation', 'moving'),
    #                                                    tableActionType['deleted'].eq(0)])
    # Откуда я?
    queryTable = queryTable.innerJoin(tableAction, [tableAction['event_id'].eq(tableEvent['id']),
                                                    tableAction['actionType_id'].inlist(actionTypeIdList)])
    queryTable = queryTable.innerJoin(tableFromAPT, [tableFromAPT['name'].eq(u'Переведен из отделения'),
                                                     tableFromAPT['actionType_id'].eq(tableAction['actionType_id']),
                                                     tableFromAPT['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(tableFromAP, [tableFromAP['type_id'].eq(tableFromAPT['id']),
                                                    tableFromAP['action_id'].eq(tableAction['id']),
                                                    tableFromAP['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(tableFromAPOS, tableFromAPOS['id'].eq(tableFromAP['id']))
    queryTable = queryTable.leftJoin(tableFromOS, [tableFromOS['id'].eq(tableFromAPOS['value']),
                                                   tableFromOS['deleted'].eq(0)])

    # Куда я?
    queryTable = queryTable.innerJoin(tableToAPT, [tableToAPT['name'].eq(u'Переведен в отделение'),
                                                     tableToAPT['actionType_id'].eq(tableAction['actionType_id']),
                                                     tableToAPT['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(tableToAP, [tableToAP['type_id'].eq(tableToAPT['id']),
                                                    tableToAP['action_id'].eq(tableAction['id']),
                                                    tableToAP['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(tableToAPOS, tableToAPOS['id'].eq(tableToAP['id']))
    queryTable = queryTable.leftJoin(tableToOS, [tableToOS['id'].eq(tableToAPOS['value']),
                                                   tableToOS['deleted'].eq(0)])

    # Где я?
    queryTable = queryTable.innerJoin(tableCurrAPT, [tableCurrAPT['name'].eq(u'Отделение пребывания'),
                                                     tableCurrAPT['actionType_id'].eq(tableAction['actionType_id']),
                                                     tableCurrAPT['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(tableCurrAP, [tableCurrAP['type_id'].eq(tableCurrAPT['id']),
                                                    tableCurrAP['action_id'].eq(tableAction['id']),
                                                    tableCurrAP['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(tableCurrAPOS, tableCurrAPOS['id'].eq(tableCurrAP['id']))
    queryTable = queryTable.leftJoin(tableCurrOS, [tableCurrOS['id'].eq(tableCurrAPOS['value']),
                                                   tableCurrOS['deleted'].eq(0)])

    # Уход
    queryTable = queryTable.innerJoin(tablePatronageAPT, [tablePatronageAPT['name'].like(u'Уход'),
                                                          tablePatronageAPT['actionType_id'].eq(tableAction['actionType_id']),
                                                          tablePatronageAPT['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(tablePatronageAP, [tablePatronageAP['type_id'].eq(tablePatronageAPT['id']),
                                                        tablePatronageAP['action_id'].eq(tableAction['id']),
                                                        tablePatronageAP['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(tablePatronageAPS, tablePatronageAPS['id'].eq(tablePatronageAP['id']))

    queryTable = queryTable.leftJoin(tableHBProfileAPT, [tableHBProfileAPT['name'].eq(u'Койка'),
                                                          tableHBProfileAPT['actionType_id'].eq(tableAction['actionType_id']),
                                                          tableHBProfileAPT['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(tableHBProfileAP, [tableHBProfileAP['type_id'].eq(tableHBProfileAPT['id']),
                                                         tableHBProfileAP['action_id'].eq(tableAction['id']),
                                                         tableHBProfileAP['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(tableAPHB, tableAPHB['id'].eq(tableHBProfileAP['id']))
    queryTable = queryTable.leftJoin(tableOSHB, tableOSHB['id'].eq(tableAPHB['value']))
    queryTable = queryTable.leftJoin(tableRBHospitalBedProfile, tableRBHospitalBedProfile['id'].eq(tableOSHB['profile_id']))

    cond = [tableEvent['setDate'].dateLe(begDate), db.joinOr([tableEvent['execDate'].dateGe(begDate), tableEvent['execDate'].isNull()])]
    cols = [tableEvent['externalId'],
            tableEvent['id'].alias('eventId'),
            tableAction['id'].alias('actionId'),
            tableAction['begDate'].alias('actionBegDate'),
            tableAction['endDate'].alias('actionEndDate'),
            tableAction['actionType_id'].alias('actionTypeId'),
            tableClient['lastName'],
            tableClient['firstName'],
            tableClient['patrName'],
            tableFromOS['id'].alias('FromId'),
            tableToOS['id'].alias('ToId'),
            tableCurrOS['id'].alias('CurrId'),
            tableFromOS['name'].alias('FromName'),
            tableToOS['name'].alias('ToName'),
            tableCurrOS['name'].alias('CurrName'),
            tableRBHospitalBedProfile['name'].alias('HBProfileName'),
            tablePatronageAPS['value'].alias('patronage'),
            tableEvent['setDate'].alias('eventSetDate'),
            tableClient['birthDate'].alias('clientBirthDate'),
            tableEvent['eventType_id'],
            ]

    stmt = db.selectStmt(queryTable,
                         cols,
                         where=cond)
    return db.query(stmt)


class CStationaryReportMoved(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Сведения о переведенных')
        self.processedEvents = []
        self.deathEventResults = []
        self.params = {}

    def getSetupDialog(self, parent):
        result = CStationaryReportMovedSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def processRecord(self, record):
        externalId = forceString(record.value('externalId'))
        lastName = forceString(record.value('lastName'))
        firstName = forceString(record.value('firstName'))
        patrName = forceString(record.value('patrName'))
        eventSetDate = forceDate(record.value('eventSetDate'))
        clientBirthDate = forceDate(record.value('clientBirthDate'))
        age = calcAge(clientBirthDate, eventSetDate)
        eventTypeId = forceInt(record.value('eventType_id'))


        eventEntry = self.data.setdefault(externalId, smartDict(externalId=externalId, name=formatName(lastName, firstName, patrName), age=age))
        actionId = forceRef(record.value('actionId'))
        actionBegDate = forceDate(record.value('actionBegDate'))
        actionBegTime = forceTime(record.value('actionBegDate'))
        actionEndDate = forceDate(record.value('actionEndDate'))
        actionEndTime = forceTime(record.value('actionEndDate'))
        fromId = forceRef(record.value('FromId'))
        toId = forceRef(record.value('ToId'))
        currId = forceRef(record.value('CurrId'))

        fromName = forceString(record.value('FromName'))
        toName = forceString(record.value('ToName'))
        currName = forceString(record.value('CurrName'))
        actionTypeId = forceRef(record.value('actionTypeId'))
        isMoving = self.actionTypesMap[actionTypeId] == u'moving'
        HBProfile = forceString(record.value('HBProfileName'))
        patronage = forceString(record.value('patronage'))
        actionsEntry = eventEntry.setdefault('actions', {})
        actionsEntry[(actionId, isMoving)] = smartDict(fromName=fromName, toName=toName, currName=currName,
                                                       fromId=fromId, toId=toId, currId=currId,
                                           HBProfile=HBProfile, patronage=patronage,
                                           begDate=actionBegDate, begTime=actionBegTime,
                                           endDate=actionEndDate, endTime=actionEndTime,eventTypeId = eventTypeId)
    def checkEntryDatetime(self, entryBegDate, entryBegTime):
        begDate = QtCore.QDateTime(self.params.get('begDate', QtCore.QDate()))
        mode = self.params.get('mode', 0)
        if mode == 0:
            begDatetime = begDate
            endDatetime = begDate.addDays(1)
        elif mode == 1:
            begDatetime = begDate.addSecs(7*3600)
            endDatetime = begDate.addSecs(15*3600)
        elif mode == 2:
            begDatetime = begDate.addSecs(15*3600)
            endDatetime = begDate.addDays(1).addSecs(7*3600)
        elif mode == 3:
            begDatetime = begDate.addSecs(7*3600)
            endDatetime = begDate.addDays(1).addSecs(7*3600)
        else:
            return False
        entryDatetime = QtCore.QDateTime(entryBegDate, entryBegTime)
        if endDatetime > entryDatetime > begDatetime:
            return True
        return False

    def createResultSet(self, orgStructureId = None):
        # Много проходов по одному и тому же списку - некрасиво, но сейчас не понимаю как сделать лучше и быстро :)
        # Так что милости прошу, оптимизируйте..
        eventIdList = sorted(self.data)
        if orgStructureId is not None :
            isHaventParent = False

            db = db = QtGui.qApp.db
            orgStructureParentIds = db.getRecordList('OrgStructure','parent_id','id = %d ' % orgStructureId)
            if len(orgStructureParentIds) > 0 :
                s =forceRef(orgStructureParentIds[0].value('parent_id'))
                if  forceRef(orgStructureParentIds[0].value('parent_id')) is None:

                    orgStructureIds = db.getRecordList('OrgStructure','id','parent_id= %d ' % orgStructureId)
                    orgStructureIds = map(lambda orgId: forceRef(orgId.value('id')),orgStructureIds)
                    isHaventParent = True


        for eventId in eventIdList:
            eventEntry = self.data[eventId]
            keysList = eventEntry.actions.keys()
            keysList = sorted(keysList, key=itemgetter(0))

            for (i, (actionId, isMoving)) in enumerate(keysList):
                actionEntry = eventEntry.actions[(actionId, isMoving)]

                if isMoving:
                        # Движение -> Движение
                    actionToEntry = None
                    for j, (actionToId, isMovingTo) in enumerate(keysList):
                        if j > i and isMovingTo:
                            entry = eventEntry.actions[(actionToId, isMovingTo)]

                            if self.checkEntryDatetime(entry.begDate, entry.begTime):
                                if actionEntry.eventTypeId == entry.eventTypeId :
                                    actionToEntry = eventEntry.actions[(actionToId, isMovingTo)]
                                    break
                    checkExistOrgId = False

                    if orgStructureId is not None :
                        if actionToEntry :
                            if isHaventParent :
                                checkExistOrgIdList = filter(lambda orgId: orgId == actionToEntry.fromId, orgStructureIds)


                                if len(checkExistOrgIdList) > 0 :
                                    checkExistOrgId = True
                                else :
                                    checkExistOrgIdList = filter(lambda orgId: orgId == actionToEntry.currId, orgStructureIds)
                                    if len(checkExistOrgIdList) > 0:
                                        checkExistOrgId = True
                            else:
                                if actionToEntry.fromId == orgStructureId or orgStructureId ==actionToEntry.currId:
                                    checkExistOrgId = True

                    if actionToEntry and (not orgStructureId or checkExistOrgId):

                        fromFullName = actionToEntry.fromName + u' (' + actionEntry.HBProfile + u')'
                        toFullName = actionToEntry.currName + u' (' + actionToEntry.HBProfile + u')'
                        self.resultSet.append([eventEntry.externalId,
                                               eventEntry.name, eventEntry.age,
                                               forceString(actionToEntry.begDate), forceString(actionToEntry.begTime),
                                                        fromFullName, toFullName,
                                               u'да' if actionToEntry.patronage else u''])

                    # Движение -> Реанимация
                    reanimationToEntry = None
                    for j, (reanimationToId, isMovingTo) in enumerate(keysList):
                        if j > i and not isMovingTo:
                            reanimationTempEntry = eventEntry.actions[(reanimationToId, isMovingTo)]
                            if reanimationTempEntry.fromName == actionEntry.currName \
                                and self.checkEntryDatetime(reanimationTempEntry.begDate, reanimationTempEntry.begTime):
                                if reanimationTempEntry.eventTypeId == actionEntry.eventTypeId:
                                    reanimationToEntry = eventEntry.actions[(reanimationToId, isMovingTo)]
                                    break


                    checkExistOrgId = False
                    if orgStructureId is not None:
                        if reanimationToEntry:
                            if isHaventParent:
                                checkExistOrgIdList = filter(lambda orgId: orgId == reanimationToEntry.fromId, orgStructureIds)
                                if len(checkExistOrgIdList) > 0:
                                    checkExistOrgId = True
                                else:
                                    checkExistOrgIdList = filter(lambda orgId: orgId == reanimationToEntry.currId,
                                                             orgStructureIds)
                                    if len(checkExistOrgIdList) > 0:
                                        checkExistOrgId = True
                            else:

                                if reanimationToEntry.fromId == orgStructureId or orgStructureId == reanimationToEntry.currId:
                                    checkExistOrgId = True
                    if reanimationToEntry and (not orgStructureId or checkExistOrgId):
                        fromFullName = reanimationToEntry.fromName + u' (' + actionEntry.HBProfile + u')'
                        toFullName = reanimationToEntry.currName + u' (' + reanimationToEntry.HBProfile + u')'
                        self.resultSet.append([eventEntry.externalId, eventEntry.name, eventEntry.age,
                                               forceString(reanimationToEntry.begDate), forceString(reanimationToEntry.begTime),
                                               fromFullName, toFullName,
                                               u'да' if reanimationToEntry.patronage else u''])

                    # Реанимация -> движение
                    reanimationFromEntry = None
                    for j, (reanimationFromId, isMovingFrom) in enumerate(keysList):
                        if not isMovingFrom:
                            reanimationTempEntry = eventEntry.actions[(reanimationFromId, isMovingFrom)]
                            if reanimationTempEntry.toName == actionEntry.currName \
                                and self.checkEntryDatetime(reanimationTempEntry.endDate, reanimationTempEntry.endTime) :
                                #and reanimationTempEntry.endDate >= actionEntry.begDate and reanimationTempEntry.endDate <= actionEntry.endDate:

                                if reanimationTempEntry.eventTypeId == actionEntry.eventTypeId:
                                    reanimationFromEntry = eventEntry.actions[(reanimationFromId, isMovingFrom)]
                                    break

                    checkExistOrgId = False
                    if orgStructureId is not None:
                        if reanimationFromEntry:
                            if isHaventParent:
                                checkExistOrgIdList = filter(lambda orgId: orgId == reanimationFromEntry.toId,
                                                         orgStructureIds)
                                if len(checkExistOrgIdList) > 0:
                                    checkExistOrgId = True
                                else:
                                    checkExistOrgIdList = filter(lambda orgId: orgId == reanimationFromEntry.currId,
                                                             orgStructureIds)
                                    if len(checkExistOrgIdList) > 0:
                                        checkExistOrgId = True
                            else:

                                if reanimationFromEntry.toId == orgStructureId or orgStructureId == reanimationFromEntry.currId:
                                    checkExistOrgId = True
                    if reanimationFromEntry and (not orgStructureId or checkExistOrgId):
                        fromFullName = reanimationFromEntry.currName + u' (' + reanimationFromEntry.HBProfile + u')'
                        toFullName = reanimationFromEntry.toName + u' (' + actionEntry.HBProfile + u')'
                        self.resultSet.append([eventEntry.externalId, eventEntry.name, eventEntry.age,
                                               forceString(reanimationFromEntry.endDate), forceString(reanimationFromEntry.endTime),
                                               fromFullName, toFullName,
                                               u'Уход' if actionEntry.patronage else u''])


    def build(self, params):
        self.data = {}
        self.actionTypesMap = {}
        self.resultSet = []
        self.params = params

        db = QtGui.qApp.db
        actionTypes = db.getRecordList('ActionType', 'id, flatCode', 'flatCode IN (\'moving\', \'reanimation\')')
        for at in actionTypes:
            atId = forceRef(at.value('id'))
            atCode = forceString(at.value('flatCode'))
            self.actionTypesMap[atId] = atCode
        query = selectData(params, self.actionTypesMap.keys())
        while query.next():
            record = query.record()
            self.processRecord(record)
        self.createResultSet(params.get('orgStructureId', None))

        # now text
        bf = QtGui.QTextBlockFormat()
        bf.setAlignment(QtCore.Qt.AlignCenter)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(bf)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()

        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ( '8%',  [u'№ м/карты', u''], CReportBase.AlignLeft),
            ( '30%', [u'Фамилия Имя Отчество', u''], CReportBase.AlignLeft),
            ( '10%', [u'Возраст', u''], CReportBase.AlignLeft),
            ( '8%',  [u'Перевод', u'Дата'], CReportBase.AlignCenter),
            ( '8%',  [u'',        u'Время'], CReportBase.AlignCenter),
            ( '18%', [u'Отделение (профиль койки) (РО)', u'из'], CReportBase.AlignLeft),
            ( '18%', [u'',                               u'в'], CReportBase.AlignLeft),
            ( '10%', [u'Ухаживающие', u''], CReportBase.AlignCenter)
        ]

        rowSize = 8
        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 1, 2)
        table.mergeCells(0, 5, 1, 2)
        table.mergeCells(0, 7, 2, 1)

        for z in range(len(self.resultSet)):
            row = self.resultSet[z]
            i = table.addRow()
            for j in range(rowSize):
                table.setText(i, j, row[j])

        return doc

    def getDescription(self, params):
        date = params.get('begDate', QtCore.QDate())
        mode = params.get('mode', 0)
        orgStructureId = params.get('orgStructureId', None)
        times = u''
        if mode == 0:
            times = u'00.00 - 23.59'
        elif mode == 1:
            times = u'07.00 - 15.00'
        elif mode == 2:
            times = u'15.00 - 07.00'
        elif mode == 3:
            times = u'07.00 - 07.00'

        rows = []
        if date:
            rows.append(u'дата: ' + forceString(date))
        if times:
            rows.append(u'временной отрезок: ' + times)
        if orgStructureId:
            rows.append(u'подразделение: ' + getOrgStructureFullName(orgStructureId))
        return rows

from Ui_StationaryReportMovedSetup import Ui_StationaryReportMovedSetupDialog


class CStationaryReportMovedSetupDialog(QtGui.QDialog, Ui_StationaryReportMovedSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())

    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.cmbMode.setCurrentIndex(params.get('mode', 0))
        self.cmbOrgStructure.setValue(getVal(params, 'orgStructureId', None))


    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['mode'] = self.cmbMode.currentIndex()
        result['orgStructureId'] = self.cmbOrgStructure.value()



        return result
