# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from HospitalBeds.Utils import getDataOrgStructure, getDataAPHB, getDataOrgStructureId, getOrgStructureIdList, \
    getTransferPropertyIn, getStringProperty
from library.Utils                              import toVariant, forceString, forceDateTime, forceRef, CQuotaColQuery
from HospitalBeds.models.MonitoringModel import CMonitoringModel


# Выбыли
class CLeavedModel(CMonitoringModel):

    def __init__(self, parent):
        CMonitoringModel.__init__(self, parent)
        self.items = []
        self.formColumnsList(4)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = self.cols()[index.column()]
        columnFieldNames = column.fields()
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            if 'feed' in columnFieldNames:
                return QtCore.QVariant()
        elif role == QtCore.Qt.CheckStateRole:
            if 'feed' in columnFieldNames:
                item = self.items[row]
                return toVariant(QtCore.Qt.Checked if item.get('feed', None) else QtCore.Qt.Unchecked)
        elif role == QtCore.Qt.BackgroundColorRole:
            if self.items[row].get('isVIP', None):
                return QtCore.QVariant(self.items[row].get('vipColor', self.vipClientColor))
            elif self.items[row].get('isUnconscious', None):
                return toVariant(QtGui.QColor(self.unconsciousPatientRowColor))
            if 'statusObservationCode' in columnFieldNames and self.items[row].get('statusObservationCode', None):
                return toVariant(QtGui.QColor(self.items[row].get('statusObservationColor', None)))
            if 'locationCardName' in columnFieldNames and self.items[row].get('locationCardName', None):
                return toVariant(QtGui.QColor(self.items[row].get('locationCardColor', None)))
        return CMonitoringModel.data(self, index, role)

    def loadData(self, params):
        self.items = []
        db = QtGui.qApp.db
        self.tables.APT = db.table('ActionPropertyType')

        index = params.get('leaved', 0)

        def getOrderBy():
            orderBY = u'Client.lastName ASC'
            for key, value in self.headerSortingCol.items():
                if value:
                    ASC = u'ASC'
                else:
                    ASC = u'DESC'
                if key == 'clientId':
                    orderBY = u'Event.client_id %s'%(ASC)
                elif key == 'externalId':
                    orderBY = u'CAST(Event.externalId AS SIGNED) %s'%(ASC)
                elif key == 'clientName':
                    orderBY = u'Client.lastName %s'%(ASC)
                elif key == 'begDateReceived':
                    orderBY = u'Event.setDate %s'%(ASC)
                elif key == 'begDate':
                    if index == 1 or index == 2:
                        orderBY = u'Action.begDate %s'%(ASC)
                    elif index == 0:
                        orderBY = u'Event.setDate %s'%(ASC)
            return orderBY

        filterBegDateTime = params.get('begDateTime', None)
        filterEndDateTime = params.get('endDateTime', None)
        changingDayTime = params.get('changingDayTime', QtCore.QTime(0, 0))
        conclusion = params.get('death', None)
        assistantChecked = params.get('chkAssistant', False)
        assistantId = params.get('assistant', None)
        orgStructureIndex = params.get('orgStructureIndex', None)
        locationCard = params.get('locationCard', None)

        if orgStructureIndex:
            treeItem = orgStructureIndex.internalPointer() if orgStructureIndex.isValid() else None
            orgStructureIdList = getOrgStructureIdList(orgStructureIndex) if treeItem and treeItem._id else []
        if index == 1 or index == 2:
            cols = self.getQueryCols(MKB=True, statusObservation=True, OSHB=True, nameOS=True, dateFeedFlag=True)
            cols.append(u'OrgStructure.id AS idOS')

            queryTable, cond = self.getCondAndQueryTable(u'moving%', AT = True, APT = 1, AP = 1, APOS = 1, OS = 1, PWS = True, ET = 1)
            cols.append(  # u'QuotaType.`code`'
                CQuotaColQuery.QUOTA_COL
            )
            queryTable, cond = self.compileCommonFilter(params, queryTable, cond)
            queryTable, cond = self.getCondByFilters(queryTable, cond, params)
            queryTable = self.compileFinanceCols(cols, cond, queryTable, params.get('financeId', None))

            cond += [
                    self.tables.Action['endDate'].isNotNull(),
                    self.tables.APT['name'].like(u'Отделение пребывания')
                   ]
            if assistantChecked:
                if assistantId:
                    cond.append(u"EXISTS(SELECT A_A.id "
                                u"       FROM Action_Assistant AS A_A"
                                u"       INNER JOIN rbActionAssistantType AS rbAAT ON rbAAT.id = A_A.assistantType_id"
                                u"       WHERE A_A.action_id = %s "
                                u"              AND rbAAT.code like 'assistant'"
                                u"              AND A_A.person_id = %s)"  % (self.tables.Action['id'].name(),
                                                                             assistantId))
                else:
                    cond.append(u"NOT EXISTS(SELECT A_A.id "
                                u"       FROM Action_Assistant AS A_A"
                                u"       INNER JOIN rbActionAssistantType AS rbAAT ON rbAAT.id = A_A.assistantType_id"
                                u"       WHERE A_A.action_id = %s "
                                u"              AND rbAAT.code like 'assistant')"  % self.tables.Action['id'].name())
            permanent = params.get('permanent', 0)
            typeId = params.get('typeId', 0)
            profile = params.get('profileId', 0)
            if (permanent and permanent > 0) or typeId or profile:
                cond.append(getDataAPHB(permanent, typeId, profile))
            if orgStructureIdList:
                cond.append(self.tables.OS['deleted'].eq(0))
                cond.append(self.tables.APOS['value'].inlist(orgStructureIdList))

            if filterBegDateTime:
                cond.append(self.tables.Action['endDate'].datetimeGe(filterBegDateTime))
            if filterEndDateTime:
                cond.append(self.tables.Action['endDate'].datetimeLe(filterEndDateTime))
            if locationCard:
                queryTable, cols, cond = self.compileLocationCardQuery(queryTable, cols, cond, locationCard)
                cond.append(self.tables.LocationCard['locationCardType_id'].eq(locationCard))
            if index == 1:
                cond.append('''NOT %s''' % getTransferPropertyIn(u'Переведен в отделение'))
            if conclusion and conclusion != u'не определено':
                cond.append(getStringProperty(u'Исход госпитализации', u'(APS.value LIKE \'%s\')' % conclusion))
            orderBy = getOrderBy()
            records = db.getRecordList(
                queryTable,
                cols,
                cond,
                u'%s%s ASC' % (orderBy, u', Action.id' if index == 2 else u'')
            )
            for record in records:
                item = self.getItemFromRecord(record)
                self.items.append(item)
            self.reset()
        elif index == 0:
            cols = self.getQueryCols(MKB=True, statusObservation=True, orgStructurePropertyNameList=[u'Отделение'], dateFeedFlag=True)
            cols.append(getDataOrgStructureId([u'Отделение']))

            queryTable, cond = self.getCondAndQueryTable(u'leaved%', AT = True, PWS = True, ET = 1, AP=2, APT=2)
            cols.append(  # u'QuotaType.`code`'
                CQuotaColQuery.QUOTA_COL
            )
            queryTable, cond = self.compileCommonFilter(params, queryTable, cond)
            queryTable, cond = self.getCondByFilters(queryTable, cond, params)
            queryTable = self.compileFinanceCols(cols, cond, queryTable, params.get('financeId', None), True)

            if assistantChecked:
                if assistantId:
                    cond.append(u"EXISTS(SELECT A_A.id "
                                u"       FROM Action_Assistant AS A_A"
                                u"       INNER JOIN rbActionAssistantType AS rbAAT ON rbAAT.id = A_A.assistantType_id"
                                u"       WHERE A_A.action_id = %s "
                                u"              AND rbAAT.code like 'assistant'"
                                u"              AND A_A.person_id = %s)"  % (self.tables.Action['id'].name(),
                                                                             assistantId))
                else:
                    cond.append(u"NOT EXISTS(SELECT A_A.id "
                                u"       FROM Action_Assistant AS A_A"
                                u"       INNER JOIN rbActionAssistantType AS rbAAT ON rbAAT.id = A_A.assistantType_id"
                                u"       WHERE A_A.action_id = %s "
                                u"              AND rbAAT.code like 'assistant')"  % self.tables.Action['id'].name())
            if filterBegDateTime:
                cond.append(db.joinOr([self.tables.Action['endDate'].isNull(),
                                       self.tables.Action['endDate'].datetimeGe(filterBegDateTime)]))
            if filterEndDateTime:
                cond.append(db.joinOr([self.tables.Action['endDate'].isNull(),
                                       self.tables.Action['endDate'].datetimeLe(filterEndDateTime)]))
            if orgStructureIndex:
                treeItem = orgStructureIndex.internalPointer() if orgStructureIndex.isValid() else None
                orgStructureIdList = getOrgStructureIdList(orgStructureIndex) if treeItem and treeItem._id else []
            if orgStructureIdList:
                cond.append(getDataOrgStructure(u'Отделение', orgStructureIdList))
            if conclusion and conclusion != u'не определено':
                cond.append(getStringProperty(u'Исход госпитализации', u'(APS.value LIKE \'%s\')'%(conclusion)))

            queryTable, cols, cond = self.compileLocationCardQuery(queryTable, cols, cond, locationCard)

            orderBy = getOrderBy()
            records = db.getRecordList(queryTable, cols, cond, orderBy, isDistinct=True)
            for record in records:
                cardName, cardColor = self.getLocationCardView(record)

                item = self.getItemFromRecord(record)
                item.update({'begDate' : forceDateTime(record.value('setDate')),
                             'begDateString' : forceDateTime(record.value('setDate')).toString('dd.MM.yyyy hh:mm'),
                             'locationCardName' : cardName,
                             'locationCardColor' : cardColor})
                self.items.append(item)
        self.updateBedInfo(self.items)
        self.reset()

    def updateBedInfo(self, items):
        if not items:
            return
        event_list = []
        for item in items:
            if not forceRef(item['profileBed']):
                event_list.append(forceString(item['eventId']))
        db = QtGui.qApp.db
        stmt = u'''
        Select Event.id as eventId, h.name as profile, osh.code, osh.name from Event
            inner join Action
                on Action.id =
                (
                    Select a.id
                    From Action a
                    where a.event_id = Event.id
                        and a.actionType_id = (Select id From ActionType Where flatCode = 'moving' Limit 1)
                    Order by id desc
                    Limit 1
                )
            inner join ActionProperty ap
                on ap.action_id = Action.id
            inner join ActionProperty_HospitalBed aph
                on aph.id = ap.id
            inner join OrgStructure_HospitalBed osh
                on osh.id = aph.value
            inner join rbHospitalBedProfile h
                on h.id = osh.profile_id
        where %s
        ''' % db.table('Event')['id'].inlist(event_list)
        result = {}
        query = db.query(stmt)
        while query.next():
            record = query.record()
            result[forceRef(record.value('eventId'))] = {'profileBed': forceString(record.value('profile')),
                                                          'codeBed': forceString(record.value('code')),
                                                          'nameBed': forceString(record.value('name')),}
        for item in items:
            item.update(result.get(item['eventId'], {}))

    def compileLocationCardQuery(self, queryTable, cols, cond, locationCard):
        db = QtGui.qApp.db
        rbCardTypeTable = db.table('rbHospitalBedsLocationCardType')
        locationCardTable = db.table('Event_HospitalBedsLocationCard')

        if not locationCard or locationCard == u'0':
            queryTable = queryTable.leftJoin(
                locationCardTable,
                db.joinAnd([
                    locationCardTable['event_id'].eq(self.tables.Event['id']),
                    locationCardTable['deleted'].eq(0)
                ])
            )
            queryTable = queryTable.leftJoin(rbCardTypeTable,
                    rbCardTypeTable['id'].eq(locationCardTable['locationCardType_id']))
        else:
            queryTable = queryTable.innerJoin(
                locationCardTable,
                db.joinAnd([
                    locationCardTable['event_id'].eq(self.tables.Event['id']),
                    locationCardTable['deleted'].eq(0)
                ])
            )
            queryTable = queryTable.innerJoin(rbCardTypeTable,
                    rbCardTypeTable['id'].eq(locationCardTable['locationCardType_id']))
            locationCardStr = forceString(locationCard)
            if len(locationCardStr) == 1:
                locationCardStr = '0' + locationCardStr
            cond.append(rbCardTypeTable['code'].like(locationCardStr))

        cols.append(rbCardTypeTable['name'].alias('locationCardName'))
        cols.append(rbCardTypeTable['color'].alias('locationCardColor'))
        cols.append(locationCardTable['moveDate'].alias('locationCardMoveDate'))
        return queryTable, cols, cond

    @staticmethod
    def getLocationCardView(record):
        locationCardColor = u'#000000'
        locationCardName = ''

        moveDate = record.value('locationCardMoveDate')
        name = record.value('locationCardName')
        color = record.value('locationCardColor')

        if not color.isNull():
            locationCardColor = forceString(color)
        if not name.isNull() and not moveDate.isNull():
            sname, sdate = forceString(name), forceString(moveDate)
            locationCardName = sname + ' (' + sdate + ')'

        return locationCardName, locationCardColor

