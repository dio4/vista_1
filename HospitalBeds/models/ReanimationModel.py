# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from HospitalBeds.HospitalizationEventDialog    import getActionTypeIdListByFlatCode
from HospitalBeds.Utils import getDataOrgStructure, getDataAPHB, getDataOrgStructureId, getOrgStructureIdList, \
    getDataOrgStructureName, getAPOSNameField
from library.Utils                              import forceString, forceDateTime, toVariant
from HospitalBeds.models.MonitoringModel import CMonitoringModel


# Реанимация
class CReanimationModel(CMonitoringModel):
    def __init__(self, parent):
        CMonitoringModel.__init__(self, parent)
        self.items = []
        self.formColumnsList(9)

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
            if 'externalId' in columnFieldNames:
                if self.items[row].get('maternitywardBegDate', None):
                    return toVariant(QtGui.QColor(QtCore.Qt.green))
                elif self.items[row].get('reanimationBegDate', None):
                    return toVariant(QtGui.QColor(QtCore.Qt.red))
        return CMonitoringModel.data(self, index, role)

    ## Загрузка данных модели
    #    @param params: словарь с необходимыми для загрузки настройками.
    def loadData(self, params):
        statusObservation = params.get('statusObservation', None)
        
        
        osPropertyNameList = [u'Отделение пребывания%']
        
        db = QtGui.qApp.db
        self.tables.Event = db.table('Event')
        tableStatusObservation= db.table('Client_StatusObservation')
        
        self.items = []
        cols = self.getQueryCols(statusObservation=True, orgStructurePropertyNameList=osPropertyNameList, PWS=False, dateFeedFlag=True)
        cols.append(getDataOrgStructureId(osPropertyNameList))

        reanimationActionTable = self.tables.Action.alias('reanimationAction')
        queryTable = self.tables.Action.innerJoin(self.tables.Event, self.tables.Action['event_id'].eq(self.tables.Event['id']))
        queryTable = queryTable.innerJoin(self.tables.Client, self.tables.Event['client_id'].eq(self.tables.Client['id']))
        queryTable = queryTable.innerJoin(reanimationActionTable, [reanimationActionTable['event_id'].eq(self.tables.Event['id']),
                                                              reanimationActionTable['actionType_id'].inlist(getActionTypeIdListByFlatCode('reanimation%')),
                                                              reanimationActionTable['deleted'].eq(0),
                                                              db.joinOr([reanimationActionTable['begDate'].le(self.tables.Action['endDate']),
                                                                         self.tables.Action['endDate'].isNull()]),
                                                              db.joinOr([reanimationActionTable['endDate'].ge(self.tables.Action['begDate']),
                                                                         reanimationActionTable['endDate'].isNull()])
                                                              ])
        cols.append(getDataOrgStructureName([u'Отделение%'], fieldAlias = 'currentCommonOSName', actionTableAlias = reanimationActionTable.aliasName))
        cols.append(getAPOSNameField(reanimationActionTable, u'Переведен из%', fieldAlias='nameFromOS'))
        cond = [self.tables.Action['actionType_id'].inlist(getActionTypeIdListByFlatCode('reanimation%')),
                self.tables.Action['deleted'].eq(0),
                self.tables.Event['deleted'].eq(0),
                self.tables.Client['deleted'].eq(0)
#                self.tables.Action['endDate'].isNull()
#                self.tables.Action['status'].ne(2)
                ]


        queryTable = self.compileFinanceCols(cols, cond, queryTable, params.get('financeId', None))

        begDateTime = params.get('begDateTime', None)
        endDateTime = params.get('endDateTime', None)
        changingDayTime = params.get('changingDayTime', QtCore.QTime(0, 0))
        
        orgStructureIndex = params.get('orgStructureIndex', None)
        if orgStructureIndex:
            treeItem = orgStructureIndex.internalPointer() if orgStructureIndex.isValid() else None
            orgStructureIdList = getOrgStructureIdList(orgStructureIndex) if treeItem and treeItem._id else []
        if orgStructureIdList:
            cond.append(getDataOrgStructure(osPropertyNameList, orgStructureIdList))
        
        if not begDateTime:
            begDateTime = QtCore.QDate.currentDate()

        cond.append(db.joinOr([self.tables.Action['endDate'].datetimeGe(begDateTime),
                                   self.tables.Action['endDate'].isNull()]))
        
        if endDateTime:
            cond.append(self.tables.Action['begDate'].isNotNull())
            cond.append(self.tables.Action['begDate'].datetimeLe(endDateTime))
        else:
            cond.append(reanimationActionTable['status'].ne(2))
            cond.append(reanimationActionTable['endDate'].isNull())
            

        personId = params.get('personId', None)
        if personId:
            cond.append(self.tables.Event['execPerson_id'].eq(personId))

        permanent = params.get('permanent', None)
        typeId = params.get('typeId', None)
        profileId = params.get('profileId', None)
        clientLocation = params.get('clientLocation', 0)
        if clientLocation == 2:
            cond.append('''NOT %s'''%(getDataAPHB()))
        elif clientLocation == 1:
            cond.append('''%s'''%(getDataAPHB(permanent, typeId, profileId)))
        else:
            if (permanent and permanent > 0) or (typeId) or (profileId):
                cond.append('''%s'''%(getDataAPHB(permanent, typeId, profileId)))
        
        queryTable, cond = self.getCondByFilters(queryTable, cond, params)
        
        if statusObservation:
                queryTable = queryTable.innerJoin(tableStatusObservation, tableStatusObservation['master_id'].eq(self.tables.Client['id']))
                cond.append(tableStatusObservation['deleted'].eq(0))
                cond.append(tableStatusObservation['statusObservationType_id'].eq(statusObservation))
        
        reanimationRecords = db.getRecordList(queryTable, cols, cond, u'Client.lastName, Client.firstName, Client.patrName')
        for record in reanimationRecords:
            item = self.getItemFromRecord(record)
            item.update({'reanimationBegDate' : forceDateTime(record.value('begDate')).toString('dd.MM.yyyy hh:mm')})
            item.update({'nameFromOS' : forceString(record.value('nameFromOS'))})
            self.items.append(item)
        self.reset()


