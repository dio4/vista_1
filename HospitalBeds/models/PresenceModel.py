# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from HospitalBeds.HospitalizationEventDialog import getActionTypeIdListByFlatCode
from HospitalBeds.Utils import getEventPhysicalActivity, getComfortableColStmt, getExistsNonPayedActions, \
    getDataOrgStructure, getDataAPHB, getDataOrgStructureId, getActionPropertyTypeName, getOrgStructureIdList
from HospitalBeds.models.MonitoringModel import CMonitoringModel
from library.Utils import toVariant, forceString, forceBool, timeRangeColorParser, \
    CQuotaColQuery


# Присутствуют - Список - 1
class CPresenceModel(CMonitoringModel):
    def __init__(self, parent):
        CMonitoringModel.__init__(self, parent)
        self.items = []
        self.eventIdList = []
        self.formColumnsList(1)
        self.timeRangeColors = []
        self.unconsciousPatientRowColor = u'red'

    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = self.cols()[index.column()]
        columnFieldNames = column.fields()
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            if 'feed' in columnFieldNames:
                return self.items[row].get('feedTextValueItem', QtCore.QVariant())
        elif role == QtCore.Qt.CheckStateRole:
            if 'feed' in columnFieldNames:
                item = self.items[row]
                return toVariant(QtCore.Qt.Checked if item.get('feed', None) else QtCore.Qt.Unchecked)
        elif role == QtCore.Qt.FontRole:
            if 'comfortableDate' in columnFieldNames and self.items[row].get('comfortableDate', None):
                comfortDate = self.items[row]['comfortableDate']
                if comfortDate.date() == QtCore.QDate.currentDate():
                    result = QtGui.QFont()
                    result.setBold(True)
                    return QtCore.QVariant(result)
        elif role == QtCore.Qt.BackgroundColorRole:
            if self.items[row].get('isVIP', None):
                return QtCore.QVariant(self.items[row].get('vipColor', self.vipClientColor))
            elif self.items[row].get('isUnconscious', None):
                return toVariant(QtGui.QColor(self.unconsciousPatientRowColor))
            elif 'statusObservationCode' in columnFieldNames and self.items[row].get('statusObservationCode', None):
                return toVariant(QtGui.QColor(self.items[row].get('statusObservationColor', None)))
            #обработка столбца "Комфортность"
            elif 'comfortableDate' in columnFieldNames and self.items[row].get('comfortableDate', None):
                #Если статус оплаты для комфортности НЕ оплачено (comfortablePayStatus = False)
                if not self.items[row].get('comfortablePayStatus', None):
                    return toVariant(QtGui.QColor(QtCore.Qt.red))
                #Если действие Законченно И дата окончания (endDate) меньше планируемой даты (plannedEndDate) (issue 409)
                elif self.items[row].get('endDate', None) and self.items[row]['endDate'] < self.items[row]['comfortableDate']:
                    return toVariant(QtGui.QColor(QtCore.Qt.red))
            #Если столбец с ФИО и есть eventId
            elif 'clientName' in columnFieldNames and self.items[row].get('eventId', None):
                if self.items[row].get('isHasNotPayedActions', None):
                    return toVariant(QtGui.QColor(QtCore.Qt.red))
            elif 'externalId' in columnFieldNames:
                if self.items[row].get('maternitywardActive', None):
                    return toVariant(QtGui.QColor(QtCore.Qt.green))
                elif self.items[row].get('reanimationActive', None):
                    return toVariant(QtGui.QColor(QtCore.Qt.red))
            else:
                item = self.items[row]
                displayFieldName = columnFieldNames[self.cols()[index.column()].displayFieldNumber()]

                if displayFieldName == 'begDateString':
                    if not self.timeRangeColors:
                        timeRangeColorsString = forceString(QtGui.qApp.preferences.appPrefs.get('hospitalBedsTimeRangeColors', ''))
                        self.timeRangeColors = timeRangeColorParser(timeRangeColorsString)

                    if self.timeRangeColors:
                        currentDatetime = QtCore.QDateTime.currentDateTime()
                        # TODO: skkachaev: Внезапно в этом месте item.get('begDate' возвоащает QDate
                        begDatetime = QtCore.QDateTime(item.get('begDate', QtCore.QDateTime()))
                        currentTimeRange = begDatetime.secsTo(currentDatetime)/60

                        for (timeLow, timeHigh), color in self.timeRangeColors.items():
                            if currentTimeRange >= timeLow and currentTimeRange <= timeHigh:
                                return toVariant(color)

        #Во всех остальных случаях
        return CMonitoringModel.data(self, index, role)

    def loadData(self, params,):
        self.items = []
        self.eventIdList = []
        db = QtGui.qApp.db

        def getOrderBy(getBed = False):
            orderBY = u'Client.lastName ASC'
            for key, value in self.headerSortingCol.items():
                if value:
                    ASC = u'ASC'
                else:
                    ASC = u'DESC'
                if key == 'clientId':
                    orderBY = u'Event.client_id %s' % ASC
                elif key == 'externalId':
                    orderBY = u'CAST(Event.externalId AS SIGNED) %s' % ASC
                elif key == 'clientName':
                    orderBY = u'Client.lastName %s' % ASC
                elif key == 'begDateString':
                    orderBY = u'Action.begDate %s' % ASC
                elif key == 'codeBed':
                    if getBed:
                        orderBY = u'bedCodeName %s' % ASC
                    else:
                        orderBY = u''
            return orderBY

        # TODO: craz: check, if using orgStructureIdList as operator is legit (before it was taken from parent func directly
        def getDataMoving(orgStructureIdList=None):
            if not orgStructureIdList:
                orgStructureIdList = []
            currentDate = QtCore.QDate.currentDate()
            cols = self.getQueryCols(MKB=True, statusObservation=True, dateFeedFlag=True, OSHB=True, OSHBProfile=True, nameOS=True, patronage=True, provisionalDiagnosis=True, admissionDiagnosis=True, params=params)
            cols.append(getEventPhysicalActivity(db.formatDate(currentDate), 'physicalActivityName'))
            cols.append(u'OrgStructure.id AS idOS')

            comfortableIdList = getActionTypeIdListByFlatCode(u'comfortable%')
            if comfortableIdList:
                cols.append(getComfortableColStmt(comfortableIdList))
            cols.append(getExistsNonPayedActions())

            queryTable, cond = self.getCondAndQueryTable(u'moving%', AT=True, APT=2, AP=2, APOS=2, OS=2, PWS=True, ET=1)
            cols.append(  # u'QuotaType.`code`'
                CQuotaColQuery.QUOTA_COL
            )
            queryTable, cond = self.compileCommonFilter(params, queryTable, cond)
            queryTable, cond = self.getCondByFilters(queryTable, cond, params, withoutAPHB=True)
            queryTable = self.compileFinanceCols(cols, cond, queryTable, params.get('financeId', 0))

            if orgStructureIdList:
                cond.append(self.tables.OS['deleted'].eq(0))
                cond.append(getDataOrgStructure(u'Отделение пребывания', orgStructureIdList))
            cond.append(self.tables.APT['name'].like(u'Отделение пребывания'))

            cond.append(self.tables.Action['endDate'].isNull())
            presenceDay = params.get('presenceDay', 0)
            if presenceDay:
                datePresence = currentDate.addDays(-presenceDay)
                cond.append(self.tables.Action['begDate'].dateLe(datePresence))
            else:
                cond.append(self.tables.Action['begDate'].dateLe(currentDate))

            permanent = params.get('permanent', 0)
            typeId = params.get('typeId', 0)
            profile = params.get('profileId', 0)
            localClient = params.get('clientLocation', 0)
            codeBeds = params.get('codeBeds', None)
            if localClient == 2:
                cond.append('''NOT %s''' % (getDataAPHB()))
            elif localClient == 1:
                cond.append('''%s''' % (getDataAPHB(permanent, typeId, profile, codeBeds)))
            else:
                if (permanent and permanent > 0) or (typeId) or (profile) or codeBeds:
                    cond.append('''%s''' % (getDataAPHB(permanent, typeId, profile, codeBeds)))

            dateFeed = params.get('dateFeed', QtCore.QDate.currentDate())
            queryTable, cols, cond = self.compileFeedQuery(dateFeed, queryTable, cols, cond)

            orderBY = getOrderBy(True)
            return db.getRecordList(queryTable, cols, cond, orderBY, isDistinct=True)

        def findReceivedNoEnd(orgStructureIdList=None):
            if not orgStructureIdList:
                orgStructureIdList = []
            cols = self.getQueryCols(MKB=True, statusObservation=True, dateFeedFlag=True, orgStructurePropertyNameList = [u'Направлен в отделение'], OSHBProfile=True, provisionalDiagnosis=True, admissionDiagnosis=True, params = params)
            comfortableIdList = getActionTypeIdListByFlatCode(u'comfortable%')
            if comfortableIdList:
                cols.append(getComfortableColStmt(comfortableIdList))
            cols.append(getEventPhysicalActivity(db.formatDate(QtCore.QDate.currentDate()), 'physicalActivityName'))
            cols.append(getExistsNonPayedActions())
            cols.append(getDataOrgStructureId([u'Направлен в отделение']))

            queryTable, cond = self.getCondAndQueryTable(u'received%',PWS = True, ET = 1, AP=2, AT=2, APT=2)
            cols.append(  # u'QuotaType.`code`'
                CQuotaColQuery.QUOTA_COL
            )
            #cols.append(u'QuotaType.`code`')
            queryTable, cond = self.compileCommonFilter(params, queryTable, cond)
            queryTable = self.compileFinanceCols(cols, cond, queryTable, params.get('financeId', 0), True)
            queryTable, cond = self.getCondByFilters(queryTable, cond, params)

            cond.append(self.tables.Action['endDate'].isNull())
            if orgStructureIdList:
                cond.append(db.joinOr([getDataOrgStructure(u'Направлен в отделение', orgStructureIdList), 'NOT %s'%(getActionPropertyTypeName(u'Направлен в отделение'))]))
            presenceDay = params.get('presenceDay', 0)
            if presenceDay:
                datePresence = QtCore.QDate.currentDate().addDays(-presenceDay)
                cond.append(self.tables.Action['begDate'].dateLe(datePresence))
            else:
                cond.append(self.tables.Action['begDate'].dateLe(QtCore.QDate.currentDate()))

            dateFeed = params.get('dateFeed', QtCore.QDate.currentDate())
            queryTable, cols, cond = self.compileFeedQuery(dateFeed, queryTable, cols, cond)

            orderBY = getOrderBy()
            return db.getRecordList(queryTable, cols, cond, orderBY, isDistinct=True)

        movingOSIdList = []
        receivedOSIdList = []
        orgStructureIdList = []

        orgStructureIndex = params.get('orgStructureIndex', None)
        if orgStructureIndex:
            treeItem = orgStructureIndex.internalPointer() if orgStructureIndex.isValid() else None
            orgStructureIdList = getOrgStructureIdList(orgStructureIndex) if treeItem and treeItem._id else []
            if orgStructureIdList:
                movingOSIdList = db.getIdList(self.tables.OS, self.tables.OS['id'], [self.tables.OS['id'].inlist(orgStructureIdList), self.tables.OS['type'].ne(4), self.tables.OS['deleted'].eq(0)])
                receivedOSIdList = db.getIdList(self.tables.OS, self.tables.OS['id'], [self.tables.OS['id'].inlist(orgStructureIdList), self.tables.OS['type'].eq(4), self.tables.OS['deleted'].eq(0)])
        indexLocalClient = params.get('clientLocation', 0)
        if indexLocalClient == 2:
            if orgStructureIdList:
                records = []
                if receivedOSIdList:
                    records += findReceivedNoEnd(orgStructureIdList)
                if movingOSIdList:
                    records += getDataMoving(movingOSIdList)
            else:
                records = getDataMoving([])
        elif indexLocalClient == 1:
            if orgStructureIdList:
                records = getDataMoving(movingOSIdList) if movingOSIdList else []
            else:
                records = getDataMoving([])
        else:
            if orgStructureIdList:
                records = []
                if receivedOSIdList:
                    records += findReceivedNoEnd([])
                if movingOSIdList:
                    records += getDataMoving(movingOSIdList)
            else:
                records = findReceivedNoEnd([])
                records += getDataMoving([])

        feed = params.get('feed', 0)
        maternitywardEventList = [self.getItemFromRecord(record)['eventId'] for record in self.getRecordListAdditionalService(params, 'maternityward')]
        reanimationEventList = [self.getItemFromRecord(record)['eventId'] for record in self.getRecordListAdditionalService(params, 'reanimation')]

        for record in records:
            countEventFeedId = forceBool(record.value('countEventFeedId'))
            if (feed == 1 and not countEventFeedId) or (feed == 2 and countEventFeedId) or not feed:
                item = self.getItemFromRecord(record)
                item.update({'provisionalDiagnosis' : forceString(record.value('provisionalDiagnosis'))
                            ,'admissionDiagnosis': forceString(record.value('admissionDiagnosis'))
                            ,'feedTextValueItem': record.value('feedTextValueItem')})
                eventId = item.get('eventId', 0)
                if eventId in maternitywardEventList:
                    item.update({'maternitywardActive': True})
                if eventId in reanimationEventList:
                    item.update({'reanimationActive': True})
                if eventId and eventId not in self.eventIdList:
                    self.eventIdList.append(eventId)
                self.items.append(item)
        self.reset()


    def compileFeedQuery(self, dateFeed, queryTable, cols, cond):
        #TODO и тут
        db = QtGui.qApp.db
        eventFeedTable = db.table('Event_Feed')
        rbDietTable = db.table('rbDiet')

        queryTable = queryTable.leftJoin(eventFeedTable,
                [eventFeedTable['event_id'].eq(self.tables.Event['id'])
                ,eventFeedTable['date'].dateEq(dateFeed)]
            ).leftJoin(rbDietTable,
                rbDietTable['id'].eq(eventFeedTable['diet_id']))

        cols.append(rbDietTable['code'].alias('feedTextValueItem'))

        return queryTable, cols, cond


    def getClientId(self, row):
        return self.items[row].get('clientId', 0)

    def getEventId(self, row):
        return self.items[row].get('eventId', 0)
