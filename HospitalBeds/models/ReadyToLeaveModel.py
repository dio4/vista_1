# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from HospitalBeds.Utils import getDataAPHB, getOrgStructureIdList, \
    getAgeRangeCond, getTransferPropertyIn
from HospitalBeds.models.MonitoringModel import CMonitoringModel
from Registry.Utils import getStaffCondition
from library.Utils import toVariant, forceBool


# Готовы к выбытию
class CReadyToLeaveModel(CMonitoringModel):

    def __init__(self, parent):
        CMonitoringModel.__init__(self, parent)
        self.items = []
        self.formColumnsList(5)

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
            if 'statusObservationCode' in columnFieldNames and self.items[row].get('statusObservationCode', None):
                return toVariant(QtGui.QColor(self.items[row].get('statusObservationColor', None)))
        return CMonitoringModel.data(self, index, role)

    def loadData(self, params=None):
        if not params:
            params = {}
        filterBegDateTime = params.get('begDateTime', None)
        filterEndDateTime = params.get('endDateTime', None)
        changingDayTime = params.get('changingDayTime', QtCore.QTime(0, 0))
        orgStructureIndex = params.get('orgStructureIndex', None)
        indexSex = params.get('sex', 0)
        ageFor = params.get('ageFrom', 0)
        ageTo = params.get('ageTo', 150)
        permanent = params.get('permanent', None)
        typeId = params.get('typeId', None)
        profile = params.get('profileId', None)
        finance = params.get('financeId', None)
        feed = params.get('feed', None)
        typeReadyToLeave = params.get('leaved', 0)
        personId = params.get('personId', None)
        accountingSystemId = params.get('accountingSystemId', None)
        filterClientId = params.get('clientId', None)
        filterEventId = params.get('eventId', None)
        statusObservation = params.get('statusObservation', None)
        self.items = []
        self.statusObservation = statusObservation
        if orgStructureIndex:
            treeItem = orgStructureIndex.internalPointer() if orgStructureIndex.isValid() else None
            orgStructureIdList = getOrgStructureIdList(orgStructureIndex) if treeItem and treeItem._id else []
        db = QtGui.qApp.db
        self.tables.APT = db.table('ActionPropertyType')
        tableStatusObservation= db.table('Client_StatusObservation')


        #TODO: Проверить, что общее для всех форматирование datefeed здесь корректно. Раньше было иначе
        cols = self.getQueryCols(MKB = True, statusObservation = True, dateFeedFlag = True, OSHB = True, nameOS = True, params = params)

        queryTable, cond = self.getCondAndQueryTable(u'moving%', AT = True, APT = 2, AP = 2, APOS = 2, OS = 2, PWS = True, ET = 1)
        queryTable, cond = self.getCondByFilters(queryTable, cond, params, withoutAPHB=True)
        queryTable = self.compileFinanceCols(cols, cond, queryTable, finance)

        cond += [
            self.tables.APT['deleted'].eq(0),
            self.tables.APT['name'].like(u'Отделение пребывания')
                ]
        cond.append(self.tables.Action['endDate'].isNull())
        cond.append(u'Action.plannedEndDate != 0')
        if personId:
            cond.append(self.tables.Event['execPerson_id'].eq(personId))
        if self.statusObservation:
            queryTable = queryTable.innerJoin(tableStatusObservation, tableStatusObservation['master_id'].eq(self.tables.Client['id']))
            cond.append(tableStatusObservation['deleted'].eq(0))
            cond.append(tableStatusObservation['statusObservationType_id'].eq(self.statusObservation))
        if accountingSystemId and filterClientId:
            tableIdentification = db.table('ClientIdentification')
            queryTable = queryTable.innerJoin(tableIdentification, tableIdentification['client_id'].eq(self.tables.Client['id']))
            cond.append(tableIdentification['accountingSystem_id'].eq(accountingSystemId))
            cond.append(tableIdentification['identifier'].eq(filterClientId))
            cond.append(tableIdentification['deleted'].eq(0))
        elif filterClientId:
            cond.append(self.tables.Client['id'].eq(filterClientId))
        if filterEventId:
            cond.append(self.tables.Event['externalId'].eq(filterEventId))
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

        if indexSex > 0:
            cond.append(self.tables.Client['sex'].eq(indexSex))
        if ageFor <= ageTo:
            cond.append(getAgeRangeCond(ageFor, ageTo))
        if typeReadyToLeave:
            cond.append('''%s''' % (getTransferPropertyIn(u'Переведен в отделение')))
        else:
            cond.append('''NOT %s''' % (getTransferPropertyIn(u'Переведен в отделение')))
        if (permanent and permanent > 0) or (typeId) or (profile):
            cond.append('''%s''' % (getDataAPHB(permanent, typeId, profile)))
        if not QtGui.qApp.isDisplayStaff():
            cond.append('NOT (%s)' % getStaffCondition(self.tables.Client['id'].name()))
        records = db.getRecordList(queryTable, cols, cond, u'Client.lastName ASC')
        for record in records:
            countEventFeedId = forceBool(record.value('countEventFeedId'))
            if (feed == 1 and not countEventFeedId) or (feed == 2 and countEventFeedId) or not feed:
                item = self.getItemFromRecord(record)
                self.items.append(item)
        self.reset()

