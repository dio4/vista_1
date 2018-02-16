# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from HospitalBeds.Utils import getDataOrgStructure, getDataAPHB, getOrgStructureIdList
from HospitalBeds.models.MonitoringModel import CMonitoringModel
from library.Utils import toVariant, forceString


# Отказ от госпитализации
class CRenunciationModel(CMonitoringModel):

    def __init__(self, parent):
        CMonitoringModel.__init__(self, parent)
        self.items = []
        self.formColumnsList(7)
        self.getColumnByFieldName('begDateString').setTitle(u'Госпитализирован', True)


    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = self.cols()[index.column()]
        columnFieldNames = column.fields()
        row = index.row()
        if role == QtCore.Qt.BackgroundColorRole:
            if 'statusObservationCode' in columnFieldNames and self.items[row].get('statusObservationCode', None):
                return toVariant(QtGui.QColor(self.items[row].get('statusObservationColor', None)))
        return CMonitoringModel.data(self, index, role)

    #TODO: atronah: аргументы peranent, typeId, profile для этой вкладки отключены в интерфейсе, т.е. не могут быть заданы
    def loadData(self, params):
        self.items = []
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
                elif key == 'begDate':
                    orderBY = u'Event.setDate %s' % ASC
            return orderBY


        def findRenunciate(flatCode):
            orgStructurePropertyNameList = [u'подразделение', u'направлен в%']

            cols = self.getQueryCols(MKB=True, statusObservation=True, OSHB=True, orgStructurePropertyNameList = orgStructurePropertyNameList)
            cols.append(self.tables.APS['value'].alias('nameRenunciate'))

            queryTable, cond = self.getCondAndQueryTable(flatCode, AT = True, APT = 1, AP = 1, ET = 1)
            queryTable = queryTable.leftJoin(self.tables.APS, self.tables.APS['id'].eq(self.tables.AP['id']))
            queryTable = queryTable.leftJoin(self.tables.PWS, self.tables.PWS['id'].eq(self.tables.Action['person_id']))
            queryTable, cond = self.compileCommonFilter(params, queryTable, cond)
            queryTable, cond = self.getCondByFilters(
                queryTable, cond, params, withoutAPHB=params.get('renunciation', 0) == 1
            )
            queryTable = self.compileFinanceCols(cols, cond, queryTable, params.get('financeId', None), True)

            cond += [
                self.tables.APT['deleted'].eq(0),
                self.tables.Action['endDate'].isNotNull()
                    ]
            cond.append(self.tables.APT['name'].like(u'Причина отказа%'))

            if params.get('renunciation', 0) == 1:
                orgStructureIndex = params.get('orgStructureIndex', None)
                if orgStructureIndex:
                    treeItem = orgStructureIndex.internalPointer() if orgStructureIndex.isValid() else None
                    orgStructureIdList = getOrgStructureIdList(orgStructureIndex) if treeItem and treeItem._id else []

                if orgStructureIdList:
                    cond.append(getDataOrgStructure(orgStructurePropertyNameList, orgStructureIdList))
                permanent = params.get('permanent', 0)
                typeId = params.get('typeId', 0)
                profile = params.get('profileId', 0)
                if (permanent and permanent > 0) or typeId or profile:
                    cond.append('''%s''' % (getDataAPHB(permanent, typeId, profile)))
            #end if params.get('renunciation', 0) == 1

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
            orderBy = getOrderBy()

            #Условие на действия с имеющимися (не пустыми) причинами отказа
            rejectedCond = [self.tables.APS['id'].isNotNull(), u'TRIM(%s) NOT LIKE \'\'' % self.tables.APS['value'].name()]
            #Условие на определенную причину отказа
            reason = params.get('renunciationReason', '')
            reasonCond = [self.tables.APS['value'].eq(reason)]if reason and reason != u'не определено' else []
            #Если искать отказы среди осмотров врача приемного отделения (может быть несколько в одном событии и любой НЕотказ должен исключать событие из списка "откаханные"
            if u'inspectPigeonHole' in flatCode:
                #Получаем список тех событий, в котороых есть осмотры врача приемного отделения, но при этом у этого осмотра нет отказа
                #(считаем такие события - успешной госпитализацией)
                acceptedInspectionsEventIdList = db.getIdList(queryTable,
                                                  idCol = self.tables.Event['id'],
                                                  where = cond + ['(NOT (%s))' % db.joinAnd(rejectedCond)])
                withoutRejectionCond = [self.tables.Event['id'].notInlist(acceptedInspectionsEventIdList)] if acceptedInspectionsEventIdList else []
                #Возвращаем все осмотры, у которых есть ненулевая причина отказа, но при этом оно не принадлежит событию с успешной госпитализацией.
                #Группировка по Event.id позволяет свернуть все осмотры в один.
                return db.getRecordListGroupBy(queryTable,
                                               cols,
                                               cond + rejectedCond + reasonCond + withoutRejectionCond,
                                               self.tables.Event['id'],
                                               orderBy)
            return db.getRecordList(queryTable,
                                    cols,
                                    cond + rejectedCond + reasonCond,
                                    orderBy)
        #end of findRenunciate function

        index = params.get('renunciation', 0)
        columnName = u'Госпитализирован' if index == 0 else u'Поставлен' if index == 1 else u'Дата осмотра'
        actionTypeFlatCode = u'received%' if index == 0 else u'planning%' if index == 1 else u'inspectPigeonHole%'
        self.getColumnByFieldName('begDateString').setTitle(columnName)
        recordsRenunciation = findRenunciate(actionTypeFlatCode)
        for record in recordsRenunciation:
            item = self.getItemFromRecord(record)
            item.update({'nameRenunciate': forceString(record.value('nameRenunciate'))})
            self.items.append(item)
        self.reset()

