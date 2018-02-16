# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from HospitalBeds.Utils import getDataOrgStructure, getOrgStructureIdList
from library.Utils                              import toVariant
from HospitalBeds.models.MonitoringModel import CMonitoringModel



# Умерло
class CDeathModel(CMonitoringModel):

    def __init__(self, parent):
        CMonitoringModel.__init__(self, parent)
        self.items = []
        self.formColumnsList(8)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = self.cols()[index.column()]
        columnFieldNames = column.fields()
        row = index.row()
        if role == QtCore.Qt.BackgroundColorRole:
            if 'statusObservationCode' in columnFieldNames and self.items[row].get('statusObservationCode', None):
                return toVariant(QtGui.QColor(self.items[row].get('statusObservationColor', None)))
        return CMonitoringModel.data(self, index, role)

    #TODO: atronah: аргументы peranent, typeId, profile не используются в функции и для этой вкладки отключены в интерфейсе
    def loadData(self, params):
        self.items = []
        db = QtGui.qApp.db

        def getDeath():
            cols = self.getQueryCols(MKB=True, statusObservation=True, orgStructurePropertyNameList=[u'Отделение'])
            tableResult = db.table('rbResult')
            queryTable, cond = self.getCondAndQueryTable(u'leaved%', AT=True, APT=1, AP=1, PWS=True, ET=1)
            queryTable = queryTable.innerJoin(self.tables.APS, self.tables.APS['id'].eq(self.tables.AP['id']))

            queryTable = queryTable.innerJoin(tableResult, self.tables.Event['result_id'].eq(tableResult['id']))
            queryTable, cond = self.compileCommonFilter(params, queryTable, cond)
            queryTable = self.compileFinanceCols(cols, cond, queryTable, params.get('financeId', None), True)
            queryTable, cond = self.getCondByFilters(queryTable, cond, params)

            cond += [
                self.tables.APT['name'].like(u'Исход госпитализации'),
                self.tables.Action['endDate'].isNotNull()
                    ]
            reason = params.get('death', None)
            if reason and reason != u'не определено':
                cond.append(u'''ActionProperty_String.value LIKE \'%s\'''' % reason)
            else:
                cond.append(db.joinOr([
                    self.tables.APS['value'].like(u'умер%'),
                    self.tables.APS['value'].like(u'смерть%'),
                    tableResult['isDeath'].eq(1)
                ]))
            orgStructureIndex = params.get('orgStructureIndex', None)
            if orgStructureIndex:
                treeItem = orgStructureIndex.internalPointer() if orgStructureIndex.isValid() else None
                orgStructureIdList = getOrgStructureIdList(orgStructureIndex) if treeItem and treeItem._id else []
            if orgStructureIdList:
                cond.append(getDataOrgStructure(u'Отделение', orgStructureIdList))
            filterBegDateTime = params.get('begDateTime', None)
            filterEndDateTime = params.get('endDateTime', None)
            changingDayTime = params.get('changingDayTime', QtCore.QTime(0, 0))
            if not filterBegDateTime:
                filterBegDate = QtCore.QDate.currentDate()
                cond.append(u'Action.begDate IS NULL OR Date(Action.begDate) = \'%s\'' % (filterBegDate.toString('yyyy-MM-dd')))
            else:
                cond.append(self.tables.Action['begDate'].isNotNull())
                cond.append(self.tables.Action['begDate'].datetimeGe(filterBegDateTime))
            if filterEndDateTime:
                cond.append(self.tables.Action['begDate'].isNotNull())
                cond.append(self.tables.Action['begDate'].datetimeLe(filterEndDateTime))
            return db.getRecordList(queryTable, cols, cond, u'Client.lastName ASC')
        self.items = []

        recordsReceived = getDeath()
        for record in recordsReceived:
            item = self.getItemFromRecord(record)
            self.items.append(item)
        self.reset()

