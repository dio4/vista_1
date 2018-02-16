# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from HospitalBeds.HospitalizationEventDialog    import getActionTypeIdListByFlatCode
from HospitalBeds.Utils import getDataOrgStructure, getActionPropertyTypeName, getOrgStructureIdList
from library.Utils                              import toVariant, forceString, forceBool, forceRef, \
    forceDateTime, forceInt, forceDate, calcAge
from HospitalBeds.models.MonitoringModel import CMonitoringModel, CMonitoringCol



# Приёмное отделение
class CLobbyModel(CMonitoringModel):

    def __init__(self, parent):
        CMonitoringModel.__init__(self, parent)
        self.items = []
        self._cols = [CMonitoringCol(u'Карта',                  ['externalId'], 20, 'l'),           #0
                      CMonitoringCol(u'ФИО',                   ['clientName'], 30, 'l'),            #1
                      CMonitoringCol(u'Пол',                   ['sex'], 15, 'l'),                   #2
                      CMonitoringCol(u'Дата рождения',         ['birthDate'], 20, 'l'),             #3
                      CMonitoringCol(u'Врач',                  ['namePerson'], 30, 'l'),            #4
                      CMonitoringCol(u'Действие',               ['actionName'], 30, 'l'),           #5
                      CMonitoringCol(u'Результат',                 ['result'], 30, 'l'),            #6
                      CMonitoringCol(u'Подразделение',         ['nameOS'], 30, 'l'),                #7
                      CMonitoringCol(u'Койка',                 ['codeBed', 'nameBed'], 30, 'l'),    #8
                      CMonitoringCol(u'Начало',                 ['begDate'], 20, 'l'),              #9
                      CMonitoringCol(u'Окончание',              ['endDate'], 20, 'l')               #10
                      ]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.BackgroundColorRole:
            row = index.row()
            column = index.column()
            item = self.items[row]
            if not item['directionExecuted']:
                return toVariant(QtGui.QColor(255, 192, 192))
            else:
                return QtCore.QVariant()
        return CMonitoringModel.data(self, index, role)


    def loadReviewData(self, params):
        db = QtGui.qApp.db
        tableStatusObservation= db.table('Client_StatusObservation')
        def getOrderBy():
            orderBY = u'Client.lastName ASC'
            for key, value in self.headerSortingCol.items():
                if value:
                    ASC = u'ASC'
                else:
                    ASC = u'DESC'
                if key == 'clientId':
                    orderBY = u'Event.client_id %s'%(ASC)
                elif key == 'clientName':
                    orderBY = u'Client.lastName %s'%(ASC)
                elif key == 'begDate':
                    orderBY = u'Action.begDate %s'%(ASC)
                elif key == 'plannedEndDate':
                    orderBY = u'Action.plannedEndDate %s'%(ASC)
                elif key == 'waitingDays':
                    orderBY = u'Action.begDate %s'%(ASC)
                elif key == 'nameOS':
                    orderBY = u'nameOS %s'%(ASC)
            return orderBY

        def getReview(params, orgStructureIdList):
            filterBegDateTime = params.get('begDateTime', None)
            filterEndDateTime = params.get('endDateTime', None)
            changingDayTime = params.get('changingDayTime', QtCore.QTime(0, 0))

            cols = self.getQueryCols(orgStructurePropertyNameList=[u'Приемное отделение'])
            #cols.append(u'''APS_R.value AS renunciation''')
            #cols.append(u'''IF(TRIM(APS_D.value) = 'да', 1, 0) AS direction''')
            #cols.append(u'''IF(TRIM(APS_Dt.value) = 'да', 1, 0) AS death''')
            cols.append(u'''EXISTS(SELECT e.id
                FROM Event e
                INNER JOIN EventType ON EventType.id = e.eventType_id
                INNER JOIN rbMedicalAidType ON (rbMedicalAidType.id = EventType.medicalAidType_id AND rbMedicalAidType.federalCode IN (1, 2, 3))
                WHERE e.client_id = Event.client_id AND e.id > Event.id) AS directionExecuted''')


            queryTable = self.tables.Action.innerJoin(self.tables.ActionType, db.joinAnd([self.tables.ActionType['id'].eq(self.tables.Action['actionType_id']), self.tables.Action['actionType_id'].inlist(getActionTypeIdListByFlatCode(u'inspectPigeonHole%'))]))
            queryTable = queryTable.innerJoin(self.tables.Event, self.tables.Action['event_id'].eq(self.tables.Event['id']))
            queryTable = queryTable.innerJoin(self.tables.Client, self.tables.Event['client_id'].eq(self.tables.Client['id']))
            queryTable = queryTable.leftJoin(self.tables.PWS, self.tables.PWS['id'].eq(self.tables.Action['person_id']))


            lobbyResult = params.get('lobbyResult', 0)

            # Отказы
            if not lobbyResult or lobbyResult == 1:
                tblAPT_R = self.tables.APT.alias('APT_R')
                tblAP_R = self.tables.AP.alias('AP_R')
                tblAPS_R = self.tables.APS.alias('APS_R')
                queryTable = queryTable.leftJoin(tblAPT_R, db.joinAnd([tblAPT_R['deleted'].eq(0), tblAPT_R['actionType_id'].eq(self.tables.ActionType['id']), tblAPT_R['name'].like(u'Причина отказа%')]))
                queryTable = queryTable.leftJoin(tblAP_R, db.joinAnd([tblAP_R['deleted'].eq(0), tblAP_R['type_id'].eq(tblAPT_R['id']), tblAP_R['action_id'].eq(self.tables.Action['id'])]))
                queryTable = queryTable.leftJoin(tblAPS_R, tblAPS_R['id'].eq(tblAP_R['id']))
                cols.append(u'''APS_R.value AS renunciation''')

            # Направление на госпитализацию
            if not lobbyResult or lobbyResult == 2:
                tblAPT_D = self.tables.APT.alias('APT_D')
                tblAP_D = self.tables.AP.alias('AP_D')
                tblAPS_D = self.tables.APS.alias('APS_D')
                queryTable = queryTable.leftJoin(tblAPT_D, db.joinAnd([tblAPT_D['deleted'].eq(0), tblAPT_D['actionType_id'].eq(self.tables.ActionType['id']), tblAPT_D['name'].like(u'Направлен на госпитализацию%')]))
                queryTable = queryTable.leftJoin(tblAP_D, db.joinAnd([tblAP_D['deleted'].eq(0), tblAP_D['type_id'].eq(tblAPT_D['id']), tblAP_D['action_id'].eq(self.tables.Action['id'])]))
                queryTable = queryTable.leftJoin(tblAPS_D, tblAPS_D['id'].eq(tblAP_D['id']))
                cols.append(u'''IF(TRIM(APS_D.value) = 'да', 1, 0) AS direction''')

            # Смерть
            if not lobbyResult or lobbyResult == 3:
                tblAPT_Dt = self.tables.APT.alias('APT_Dt')
                tblAP_Dt = self.tables.AP.alias('AP_Dt')
                tblAPS_Dt = self.tables.APS.alias('APS_Dt')
                queryTable = queryTable.leftJoin(tblAPT_Dt, db.joinAnd([tblAPT_Dt['deleted'].eq(0), tblAPT_Dt['actionType_id'].eq(self.tables.ActionType['id']), tblAPT_Dt['name'].like(u'Умер%')]))
                queryTable = queryTable.leftJoin(tblAP_Dt, db.joinAnd([tblAP_Dt['deleted'].eq(0), tblAP_Dt['type_id'].eq(tblAPT_Dt['id']), tblAP_Dt['action_id'].eq(self.tables.Action['id'])]))
                queryTable = queryTable.leftJoin(tblAPS_Dt, tblAPS_Dt['id'].eq(tblAP_Dt['id']))
                cols.append(u'''IF(TRIM(APS_Dt.value) = 'да', 1, 0) AS death''')

            cond = [
                self.tables.Action['deleted'].eq(0),
                self.tables.Event['deleted'].eq(0),
                self.tables.Client['deleted'].eq(0)
                    ]

            #TODO: Как получать дату начала стационарного события??
            #tableEventType = db.table('EventType')
            #queryTable = queryTable.innerJoin(tableEventType, tableEvent['eventType_id'].eq(tableEventType['id']))
#            cond.append(u'''(EventType.medicalAidType_id IN (SELECT rbMedicalAidType.id from rbMedicalAidType where rbMedicalAidType.code IN (\'1\', \'2\', \'3\', \'7\')))''')
            #if personId:
            #    cond.append(self.tables.Action['person_id'].eq(personId))
            if params.get('statusObservation', None):
                queryTable = queryTable.innerJoin(tableStatusObservation, tableStatusObservation['master_id'].eq(self.tables.Client['id']))
                cond.append(tableStatusObservation['deleted'].eq(0))
                cond.append(tableStatusObservation['statusObservationType_id'].eq(self.statusObservation))
            queryTable, cond = self.compileCommonFilter(params, queryTable, cond, actionPerson = True)


            if orgStructureIdList:
                cond.append(db.joinOr([getDataOrgStructure(u'Приемное отделение', orgStructureIdList), 'NOT %s'%(getActionPropertyTypeName(u'Приемное отделение'))]))
            if filterBegDateTime:
                cond.append(db.joinOr([self.tables.Action['begDate'].isNull(),
                                       self.tables.Action['begDate'].datetimeGe(filterBegDateTime)]))
            if filterEndDateTime:
                cond.append(db.joinOr([self.tables.Action['begDate'].isNull(),
                                       self.tables.Action['begDate'].datetimeLe(filterEndDateTime)]))

            orderBy = getOrderBy()
            records = db.getRecordList(queryTable, cols, cond, orderBy, isDistinct = True)
            return records

        orgStructureIndex = params.get('orgStructureIndex', None)

        if orgStructureIndex:
            treeItem = orgStructureIndex.internalPointer() if orgStructureIndex.isValid() else None
            orgStructureIdList = getOrgStructureIdList(orgStructureIndex) if treeItem and treeItem._id else []
            recordType = db.getRecordEx(self.tables.OS, [self.tables.OS['id']], [self.tables.OS['deleted'].eq(0), self.tables.OS['type'].eq(4), self.tables.OS['id'].inlist(orgStructureIdList)])
            if recordType and forceRef(recordType.value('id')):
                orgStructureIdList = []

        records = getReview(params, orgStructureIdList)

        for record in records:
            renunciation = forceString(record.value('renunciation'))
            direction = forceBool(record.value('direction'))
            directionExecuted = forceBool(record.value('directionExecuted'))
            death = forceBool(record.value('death'))
            if not params.get('showFinished') and forceDateTime(record.value('endDate')):
                continue
            item = {
                'actionId': forceRef(record.value('actionId')),
                'eventId': forceRef(record.value('eventId')),
                'clientId': forceRef(record.value('client_id')),
                'personId': forceRef(record.value('personId')),
                'externalId': forceString(record.value('externalId')),
                'clientName': forceString(record.value('lastName')) + u' ' + forceString(record.value('firstName')) + u' ' + forceString(record.value('patrName')),
                'sex': self.sex[forceInt(record.value('sex'))],
                'birthDate': forceString(forceDate(record.value('birthDate'))) + u'(' + forceString(calcAge(forceDate(record.value('birthDate')), None)) + u')',
                'codeBed': u'',
                'nameBed': u'',
                'bedProfile': u'',
                'nameOS': forceString(record.value('nameOS')),
                'namePerson': forceString(record.value('namePerson')),
                'actionName': u'Осмотр врача',
                'begDate': forceDateTime(record.value('begDate')),
                'endDate': forceDateTime(record.value('endDate')),
                'result': u'Госпитализация' if direction else u'Отказ от госпитализации: %s' % renunciation if renunciation else u'Умер' if death else u'',
                'directionExecuted': directionExecuted if direction else 1
                }
            if params.get('lobbyResult', 0) and not (direction or renunciation or death):
                continue
            self.items.append(item)


    def loadHospitalization(self, params):
        orgStructureIndex = params.get('orgStructureIndex', None)
        if orgStructureIndex:
            treeItem = orgStructureIndex.internalPointer() if orgStructureIndex.isValid() else None
            orgStructureIdList = getOrgStructureIdList(orgStructureIndex) if treeItem and treeItem._id else []

        db = QtGui.qApp.db

        def getOrderBy():
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
                elif key == 'begDateReceived':
                    orderBY = u'Event.setDate %s' % ASC
                elif key == 'begDate':
                    orderBY = u'Action.begDate %s' % ASC
            return orderBY


        def findHospitalized(orgStructureIdList=None):
            if not orgStructureIdList:
                orgStructureIdList = []
            cols = self.getQueryCols(MKB=True, statusObservation=True, dateFeedFlag=True, currentOSHB=True, eventEndDate = True, eventBegDate = True, params=params)
            #cols.append(self.tables.Event['execDate']).alias('endDate')
            cols.append(self.tables.OS['name'].alias('nameOS'))

            queryTable, cond = self.getCondAndQueryTable(u'received%', AT=True, APT=1, AP=1, APOS=1, OS=1, PWS=True, ET=1)
            queryTable, cond = self.compileCommonFilter(params, queryTable, cond, actionPerson = True)

            cond += [
                    self.tables.APT['deleted'].eq(0),
                    self.tables.OS['deleted'].eq(0),
                    self.tables.Action['endDate'].isNotNull()
                   ]
            cond.append(self.tables.APT['name'].like(u'Направлен в отделение'))
            filterBegDateTime = params.get('begDateTime', None)
            filterEndDateTime = params.get('endDateTime', None)
            changingDayTime = params.get('changingDayTime', QtCore.QTime(0, 0))
            if not filterBegDateTime:
                filterBegDate = QtCore.QDate.currentDate()
                cond.append(db.joinOr([self.tables.Action['begDate'].isNull(), self.tables.Action['begDate'].datetimeBetween(QtCore.QDateTime(filterBegDate, changingDayTime),
                                                                                                                             QtCore.QDateTime(filterBegDate.addDays(1), changingDayTime))]))
            else:
                cond.append(self.tables.Action['begDate'].isNotNull())
                cond.append(self.tables.Action['begDate'].datetimeGe(filterBegDateTime))
            if filterEndDateTime:
                cond.append(self.tables.Action['begDate'].isNotNull())
                cond.append(self.tables.Action['begDate'].datetimeLe(filterEndDateTime))
            if orgStructureIdList:
                cond.append(self.tables.APOS['value'].inlist(orgStructureIdList))

            orderBy = getOrderBy()
            return db.getRecordList(queryTable, cols, cond, orderBy)

        records = findHospitalized(orgStructureIdList)
        for record in records:
            if not params.get('showFinished') and forceDateTime(record.value('endDate')):
                continue
            bedCodeName = forceString(record.value('bedCodeName')).split("  ")
            item = {
                'actionId': forceRef(record.value('actionId')),
                'eventId': forceRef(record.value('eventId')),
                'clientId': forceRef(record.value('client_id')),
                'personId': forceRef(record.value('personId')),
                'externalId': forceString(record.value('externalId')),
                'clientName': forceString(record.value('lastName')) + u' ' + forceString(record.value('firstName')) + u' ' + forceString(record.value('patrName')),
                'sex': self.sex[forceInt(record.value('sex'))],
                'birthDate': forceString(forceDate(record.value('birthDate'))) + u'(' + forceString(calcAge(forceDate(record.value('birthDate')), None)) + u')',
                'codeBed' : forceString(bedCodeName[0]) if len(bedCodeName) >= 1 else '' + forceString(bedCodeName[2]) if len(bedCodeName)>=3 else '',
                'nameBed' : forceString(bedCodeName[1]) if len(bedCodeName) >= 2 else '',
                'nameOS': forceString(record.value('nameOS')),
                'namePerson': forceString(record.value('namePerson')),
                'actionName': u'Госпитализация',
                'begDate': forceDateTime(record.value('begDate')),
                'endDate': forceDateTime(record.value('endDate')),
                'result': u'',
                'directionExecuted': 1
            }
            self.items.append(item)



    def loadData(self, params):
        self.items = []

        action = params.get('lobbyAction', 0)

        if action != 2:
            self.loadReviewData(params)
        #self.loadDirectionData(params)
        if action != 1:
            self.loadHospitalization(params)
        #self.loadRenunciation(params)
        from operator import itemgetter
        self.items = sorted(self.items, key=itemgetter('clientName'))
        self.reset()

