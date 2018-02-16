# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
#############################################################################
# Присутствуют - Список - 1
from PyQt4 import QtCore, QtGui

from HospitalBeds.Utils import getDataOrgStructure, getDataAPHB, getOrgStructureIdList
from HospitalBeds.models.MonitoringModel import CMonitoringModel
from library.Utils import toVariant, forceString, forceBool


# Переведены (в отделение)
class CTransferModel(CMonitoringModel):

    def __init__(self, parent):
        CMonitoringModel.__init__(self, parent)
        self.items = []
        self.formColumnsList(3)


    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = self.cols()[index.column()]
        columnFieldNames = column.fields()
        row = index.row()
        if role == QtCore.Qt.BackgroundColorRole:
            if self.items[row].get('isVIP', None):
                return QtCore.QVariant(self.items[row].get('vipColor', self.vipClientColor))
            elif self.items[row].get('isUnconscious', None):
                return toVariant(QtGui.QColor(self.unconsciousPatientRowColor))
            if 'statusObservationCode' in columnFieldNames and self.items[row].get('statusObservationCode', None):
                return toVariant(QtGui.QColor(self.items[row].get('statusObservationColor', None)))
            elif len(self.items[row].get('MKB', '')) <= 0:
                return toVariant(QtGui.QColor(200, 230, 240))
        if role == QtCore.Qt.DisplayRole:
            if 'feed' in columnFieldNames:
                return QtCore.QVariant()
        elif role == QtCore.Qt.CheckStateRole:
            if 'feed' in columnFieldNames:
                item = self.items[row]
                return toVariant(QtCore.Qt.Checked if item.get('feed', None) else QtCore.Qt.Unchecked)
        return CMonitoringModel.data(self, index, role)


    #TODO: На вкладке не используется quotingType. Исключить его из списка передаваемых параметров
    def loadData(self, params):
        self.items = []
        orgStructureIndex = params.get('orgStructureIndex', None)
        if orgStructureIndex:
            treeItem = orgStructureIndex.internalPointer() if orgStructureIndex.isValid() else None
            orgStructureIdList = getOrgStructureIdList(orgStructureIndex) if treeItem and treeItem._id else []

        #
        db = QtGui.qApp.db

        ####
        if params.get('transfer', None):
            nameTransferOS = u'Переведен в отделение'
            self.getColumnByFieldName('nameFromOS').setTitle(u'Переведен в')
        else:
            nameTransferOS = u'Переведен из отделения'
            self.getColumnByFieldName('nameFromOS').setTitle(u'Переведен из')
        ####

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
                    orderBY = u'Action.begDate %s'%(ASC)
            return orderBY

        def getTransfer(orgStructureIdList):
            cols = self.getQueryCols(MKB = True, statusObservation = True, dateFeedFlag = True, OSHB = True, OSHBProfile=False, orgStructurePropertyNameList = [u'Отделение пребывания'], patronage=True, params = params)
            cols.append(self.tables.OS['name'].alias('nameFromOS'))

            queryTable, cond = self.getCondAndQueryTable(u'moving%', AT = True, APT = 1, AP = 1, APOS = 1, OS = 1, PWS = True, ET = 1)
            queryTable, cond = self.compileCommonFilter(params, queryTable, cond)
            queryTable, cond = self.getCondByFilters(queryTable, cond, params, withoutAPHB=True)
            queryTable = self.compileFinanceCols(cols, cond, queryTable, params.get('financeId', None))

            cond += [
                    self.tables.APT['deleted'].eq(0),
                    self.tables.OS['deleted'].eq(0)
                   ]
            cond.append(self.tables.APT['name'].like(nameTransferOS))
            filterBegDateTime = params.get('begDateTime', None)
            filterEndDateTime = params.get('endDateTime', None)
            changingDayTime = params.get('changingDayTime', QtCore.QTime(0, 0))
            if not filterBegDateTime:
                filterBegDate = QtCore.QDate.currentDate()
                cond.append(db.joinOr([self.tables.Action['begDate'].isNull(),
                                       self.tables.Action['begDate'].datetimeBetween(QtCore.QDateTime(filterBegDate, changingDayTime),
                                                                                     QtCore.QDateTime(filterBegDate.addDays(1), changingDayTime))]))
            else:
                cond.append(self.tables.Action['begDate'].isNotNull())
                cond.append(self.tables.Action['begDate'].datetimeGe(filterBegDateTime))
            if filterEndDateTime:
                cond.append(self.tables.Action['begDate'].isNotNull())
                cond.append(self.tables.Action['begDate'].datetimeLe(filterEndDateTime))
            #TODO: правильно ли заменены условия по dateFeed?
            if orgStructureIdList:
                if params.get('stayOrgStructure', 1):
                    cond.append(getDataOrgStructure(u'Отделение пребывания', orgStructureIdList))
                else:
                    cond.append(getDataOrgStructure(nameTransferOS, orgStructureIdList))
            permanent = params.get('permanent', 0)
            typeId = params.get('typeId', 0)
            profile = params.get('profileId', 0)
            localClient = params.get('clientLocation', 0)
            if localClient == 2:
                cond.append('''NOT %s'''%(getDataAPHB()))
            elif localClient == 1:
                cond.append('''%s'''%(getDataAPHB(permanent, typeId, profile)))
            else:
                if (permanent and permanent > 0) or (typeId) or (profile):
                    cond.append('''%s'''%(getDataAPHB(permanent, typeId, profile)))
            orderBy = getOrderBy()
            return db.getRecordList(queryTable, cols, cond, orderBy)

        records = getTransfer(orgStructureIdList)
        for record in records:
            countEventFeedId = forceBool(record.value('countEventFeedId'))
            feed = params.get('feed', 0)
            if (feed == 1 and not countEventFeedId) or (feed == 2 and countEventFeedId) or not feed:
                item = self.getItemFromRecord(record)
                item.update({'nameFromOS' : forceString(record.value('nameFromOS'))})
                self.items.append(item)
        self.reset()
