# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from HospitalBeds.Utils import getDataOrgStructure, getDataAPHB, getOrgStructureIdList, \
    getTransferPropertyIn
from HospitalBeds.models.MonitoringModel import CMonitoringModel
from library.Utils import toVariant, forceString, forceBool, forceRef, forceInt, \
    CQuotaColQuery


# Поступили
class CReceivedModel(CMonitoringModel):
    def __init__(self, parent):
        CMonitoringModel.__init__(self, parent)
        self.items = []
        self.formColumnsList(2)


    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = self.cols()[index.column()]
        columnFieldNames = column.fields()
        row = index.row()
        if role == QtCore.Qt.BackgroundColorRole:
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
        elif role == QtCore.Qt.BackgroundColorRole:
            if self.items[row].get('isVIP', None):
                return QtCore.QVariant(self.items[row].get('vipColor', self.vipClientColor))
            elif self.items[row].get('isUnconscious', None):
                return toVariant(QtGui.QColor(self.unconsciousPatientRowColor))
            if 'externalId' in columnFieldNames:
                if self.items[row].get('maternitywardActive', None):
                    return toVariant(QtGui.QColor(QtCore.Qt.green))
                elif self.items[row].get('reanimationActive', None):
                    return toVariant(QtGui.QColor(QtCore.Qt.red))
        return CMonitoringModel.data(self, index, role)


    def getRecordList(self, params):
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


        ## Поиск поступивших в отделение (т.е поиск первого действия "Движения" с заполненным свойством
        # "Отделением пребывания", НО БЕЗ значения для свойства "Переведен из"
        def findMovingAfterReceived(orgStructureIdList=None):
            if not orgStructureIdList:
                orgStructureIdList = []
            cols = self.getQueryCols(MKB=True, statusObservation=True, dateFeedFlag=True, OSHB=True, OSHBProfile=True, nameOS=True, patronage=True, provisionalDiagnosis=True, admissionDiagnosis=True, params=params, order=True)

            queryTable, cond = self.getCondAndQueryTable(u'moving%', AT=True, APT=1, AP=1, APOS=2, OS=2, PWS=True, ET=1, Ord=2)
            cols.append(  # u'QuotaType.`code`'
                CQuotaColQuery.QUOTA_COL
            )
            queryTable, cond = self.compileCommonFilter(params, queryTable, cond)
            queryTable, cond = self.getCondByFilters(queryTable, cond, params, withoutAPHB=True)
            queryTable = self.compileFinanceCols(cols, cond, queryTable, params.get('financeId', None))

            cond.append(self.tables.APT['name'].like(u'Отделение пребывания'))
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
            if orgStructureIdList:
                cond.append(self.tables.OS['deleted'].eq(0))
                cond.append(self.tables.APOS['value'].inlist(orgStructureIdList))

            #TODO: правильно ли заменены условия по dateFeed??
            cond.append('''NOT %s''' % (getTransferPropertyIn(u'Переведен из отделения')))
            permanent = params.get('permanent', 0)
            typeId = params.get('typeId', 0)
            profile = params.get('profileId', 0)
            indexLocalClient = params.get('clientLocation', 0)
            if indexLocalClient == 2:
                cond.append('''NOT %s''' % (getDataAPHB()))
            elif indexLocalClient == 1:
                cond.append('''%s''' % (getDataAPHB(permanent, typeId, profile)))
            else:
                if (permanent and permanent > 0) or typeId or profile:
                    cond.append('''%s''' % (getDataAPHB(permanent, typeId, profile)))
            orderBy = getOrderBy()
            return db.getRecordList(queryTable, cols, cond, orderBy)
        #end of sub function


        ## Поиск поступивших в ЛПУ (т.е поиск завершенных действий "Поступление")
        def findReceived(orgStructureIdList=None):
            if not orgStructureIdList:
                orgStructureIdList = []
            cols = self.getQueryCols(MKB=True, statusObservation=True, dateFeedFlag=True, currentOSHB=True, OSHBProfile=True, eventEndDate = True, provisionalDiagnosis=True, admissionDiagnosis=True, params=params, order=True)
            #cols.append(self.tables.Event['execDate']).alias('endDate')
            cols.append(self.tables.OS['name'].alias('nameOS'))
            cols.append(self.tables.OS['code'].alias('codeOS'))

            queryTable, cond = self.getCondAndQueryTable(u'received%', AT=True, APT=1, AP=1, APOS=1, OS=1, PWS=True, ET=1, Ord=2)
            cols.append(  # u'QuotaType.`code`'
                CQuotaColQuery.QUOTA_COL
            )
            queryTable, cond = self.compileCommonFilter(params, queryTable, cond)
            queryTable, cond = self.getCondByFilters(queryTable, cond, params)
            queryTable = self.compileFinanceCols(cols, cond, queryTable, params.get('financeId', None), True)

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
                cond.append(db.joinOr([self.tables.Action['begDate'].isNull(),
                                       self.tables.Action['begDate'].datetimeBetween(QtCore.QDateTime(filterBegDate, changingDayTime),
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
            return db.getRecordList(queryTable, cols, cond, orderBy, isDistinct=True)
        #end of sub function


        ## Поиск поступивших в приемное отделение (т.е поиск незавершенных действий "Поступление")
        def findReceivedNoEnd(orgStructureIdList=None):
            if not orgStructureIdList:
                orgStructureIdList = []
            cols = self.getQueryCols(MKB=True, statusObservation=True, dateFeedFlag=True, orgStructurePropertyNameList=[u'Направлен в отделение'], currentOSHB=True, OSHBProfile=True, provisionalDiagnosis=True, admissionDiagnosis=True, params=params, order=True)

            queryTable, cond = self.getCondAndQueryTable(u'received%', ET=1, PWS=True, Ord=2, APT=2, AP=2, AT=2)
            cols.append(  # u'QuotaType.`code`'
                CQuotaColQuery.QUOTA_COL
            )
            queryTable, cond = self.compileCommonFilter(params, queryTable, cond)
            queryTable, cond = self.getCondByFilters(queryTable, cond, params)
            queryTable = self.compileFinanceCols(cols, cond, queryTable, params.get('financeId', None), True)

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
            if orgStructureIdList:
                cond.append(getDataOrgStructure(u'Направлен в отделение', orgStructureIdList))

            orderBy = getOrderBy()
            return db.getRecordList(queryTable, cols, cond, orderBy)
        #end of sub function

        index = params.get('received', None)
        assert index is not None
        if index == 0:
            records = findReceived(orgStructureIdList)
        elif index == 1:
            records = findMovingAfterReceived(orgStructureIdList)
        elif index == 2:
            records = findReceivedNoEnd(orgStructureIdList)


        return records


    def loadData(self, params):
        self.items = []
        records = self.getRecordList(params)
        maternitywardEventList = [self.getItemFromRecord(record)['eventId'] for record in self.getRecordListAdditionalService(params, 'maternityward')]
        reanimationEventList = [self.getItemFromRecord(record)['eventId'] for record in self.getRecordListAdditionalService(params, 'reanimation')]
        feed = params.get('feed', 0)
        for record in records:
            countEventFeedId = forceBool(record.value('countEventFeedId'))
            if (feed == 1 and not countEventFeedId) or (feed == 2 and countEventFeedId) or not feed:
                item = self.getItemFromRecord(record)
                item.update({'provisionalDiagnosis' : forceString(record.value('provisionalDiagnosis'))
                            ,'admissionDiagnosis': forceString(record.value('admissionDiagnosis'))})
                item['eventResultId'] = forceRef(record.value('result_id'))
                item['ordChannel'] = forceString(record.value('ordChannel'))
                item['ordType'] = forceInt(record.value('ordType'))
                eventId = item.get('eventId', 0)
                if eventId in maternitywardEventList:
                    item.update({'maternitywardActive': True})
                if eventId in reanimationEventList:
                    item.update({'reanimationActive': True})
                self.items.append(item)
        self.reset()