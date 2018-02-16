# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from HospitalBeds.Utils import getDataAPHB
from HospitalBeds.Utils import getDataOrgStructure, getActionPropertyTypeName, getOrgStructureIdList, \
    getPropertyAPHBP
from HospitalBeds.models.MonitoringModel import CMonitoringModel
from library.Utils import toVariant, forceInt, forceString, forceDate, forceRef


# В очереди
class CQueueModel(CMonitoringModel):

    def __init__(self, parent):
        CMonitoringModel.__init__(self, parent)
        self.items = []
        self.formColumnsList(6)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = self.cols()[index.column()]
        columnFieldNames = column.fields()
        row = index.row()
        if role == QtCore.Qt.BackgroundColorRole:
            if 'statusObservationCode' in columnFieldNames and self.items[row].get('statusObservationCode', None):
                return toVariant(QtGui.QColor(self.items[row].get('statusObservationColor', None)))
            elif self.items[row].get('bedName', None):
                return toVariant(QtGui.QColor(0, 255, 0))
            elif len(self.items[row].get('MKB', '')) <= 0:
                return toVariant(QtGui.QColor(200, 230, 240))
        return CMonitoringModel.data(self, index, role)

    def loadData(self, params):
        self.items = []
        db = QtGui.qApp.db

        def joinContractTable(queryTable, cols, cond):
            tableContract = self.tables.Contract
            tableEvent = self.tables.Event
            # джойним таблицу Contract и 3 ее поля, необходимых для формирования колонки "Договор" (Д)
            joinCond = [tableContract['id'].eq(tableEvent['contract_id']),
                        tableContract['deleted'].eq(0)]
            queryTable = queryTable.leftJoin(tableContract, joinCond)
            cols.extend([tableContract['number'].alias('contract_number'),
                         tableContract['date'].alias('contract_date'),
                         tableContract['resolution'].alias('contract_resolution')])

            return queryTable, cols, cond

        def getOrderBy():
            orderBY = u'Client.lastName ASC'
            for key, value in self.headerSortingCol.items():
                if value:
                    ASC = u'ASC'
                else:
                    ASC = u'DESC'
                if key == 'nameFinance':
                    orderBY = u'CAST(financeCodeName AS SIGNED) %s' % ASC
                elif key == 'clientId':
                    orderBY = u'Event.client_id %s' % ASC
                elif key == 'clientName':
                    orderBY = u'Client.lastName %s' % ASC
                elif key == 'begDate':
                    orderBY = u'Action.begDate %s' % ASC
                elif key == 'directionDate':
                    orderBY = u'Action.directionDate %s' % ASC
                elif key == 'waitingDays':
                    orderBY = u'Action.begDate %s' % ASC
                elif key == 'nameOS':
                    orderBY = u'nameOS %s' % ASC
                elif key == 'plannedEndDate':
                    orderBY = u'Action.plannedEndDate %s' % ASC
            return orderBY

        def getPlanning(orgStructureIdList, noBeds=False):
            cols = self.getQueryCols(MKB=True, statusObservation=True, OSHB=True, orgStructurePropertyNameList=[u'подразделение'])
            if params.get('financeId', None):
                condFinance = u' AND ActionProperty_rbFinance.value = %d' % (params.get('financeId', None))
            else:
                condFinance = u''
            cols.append(u'''(SELECT CONCAT_WS(' ', CONVERT(rbFinance.id,CHAR(11)), rbFinance.code, rbFinance.name)
                            FROM  ActionType AS AT
                                INNER JOIN Action AS A ON AT.id=A.actionType_id
                                INNER JOIN ActionPropertyType AS APT ON APT.actionType_id=AT.id
                                LEFT JOIN ActionProperty AS AP ON AP.type_id=APT.id AND AP.action_id = A.id
                                LEFT JOIN ActionProperty_rbFinance ON ActionProperty_rbFinance.id=AP.id
                                LEFT JOIN rbFinance ON rbFinance.id=ActionProperty_rbFinance.value
                            WHERE  A.deleted=0 AND AT.deleted=0 AND APT.deleted=0 AND A.id = Action.id AND APT.name LIKE 'источник финансирования'%s) AS financeCodeName''' % (condFinance))

            queryTable, cond = self.getCondAndQueryTable(u'planning%', AT=True, PWS=True, ET=1, medicalAidTypeCond=False)
            # exclude personId filter from common
            queryTable, cond = self.compileCommonFilter(params, queryTable, cond)
            queryTable, cond = self.getCondByFilters(queryTable, cond, params, withoutAPHB=True)

            cond.append(self.tables.Action['status'].notInlist([2, 3]))
            personId = params.get('personId', None)
            if personId:
                cond.append(self.tables.Action['person_id'].eq(personId))
            presenceDay = params.get('presenceDay', None)
            if presenceDay:
                currentDateFormat = self.tables.Action['begDate'].formatValue(QtCore.QDate.currentDate())
                cond.append(u'DATEDIFF(%s, Action.begDate) = %d' % (forceString(currentDateFormat), presenceDay))
            if orgStructureIdList:
                cond.append(db.joinOr([getDataOrgStructure(u'подразделение', orgStructureIdList), 'NOT %s' % getActionPropertyTypeName(u'подразделение')]))

            filterBegDateTime = params.get('begDateTime', None)
            filterEndDateTime = params.get('endDateTime', None)
            changingDayTime = params.get('changingDayTime', QtCore.QTime(0, 0))
            if filterBegDateTime:
                cond.append(db.joinOr([self.tables.Action['directionDate'].isNull(),
                                       self.tables.Action['directionDate'].datetimeGe(filterBegDateTime)]))
            if filterEndDateTime:
                cond.append(db.joinOr([self.tables.Action['directionDate'].isNull(),
                                       self.tables.Action['directionDate'].datetimeLe(filterEndDateTime)]))
            if noBeds:
                cond.append('''NOT %s''' % getDataAPHB())
            else:
                permanent = params.get('permanent', 0)
                typeId = params.get('typeId', 0)
                profile = params.get('profileId', 0)
                if (permanent and permanent > 0) or typeId or profile:
                    cond.append('''%s''' % (getDataAPHB(permanent, typeId, profile)))
            orderBy = getOrderBy()

            queryTable, cols, cond = joinContractTable(queryTable, cols, cond)

            records = db.getRecordList(queryTable, cols, cond, orderBy)

            # colsToReMap = dict(
            #     (x.fieldName.replace('`', ''), x)
            #     for x in cols
            #     if hasattr(x, 'fieldName') and x.fieldName in ['`directionDate`', '`plannedEndDate`', '`begDate`']
            # )

            return records

        def getPlanningBeds(orgStructureIdList):
            cols = self.getQueryCols(MKB=True, statusObservation=True, orgStructurePropertyNameList=[u'подразделение'])
            cols.append(self.tables.OSHB['code'].alias('codeBed'))
            cols.append(self.tables.OSHB['name'].alias('nameBed'))
            cols.append(self.tables.OSHB['sex'].alias('sexBed'))
            if params.get('financeId', None):
                condFinance = u' AND ActionProperty_rbFinance.value = %d' % (params.get('financeId', None))
            else:
                condFinance = u''
            cols.append(u'''(SELECT CONCAT_WS(' ', CONVERT(rbFinance.id,CHAR(11)), rbFinance.code, rbFinance.name)
                            FROM  ActionType AS AT
                                INNER JOIN Action AS A ON AT.id=A.actionType_id
                                INNER JOIN ActionPropertyType AS APT ON APT.actionType_id=AT.id
                                LEFT JOIN ActionProperty AS AP ON AP.type_id=APT.id AND AP.action_id = A.id
                                LEFT JOIN ActionProperty_rbFinance ON ActionProperty_rbFinance.id=AP.id
                                LEFT JOIN rbFinance ON rbFinance.id=ActionProperty_rbFinance.value
                            WHERE  A.deleted=0 AND AT.deleted=0 AND APT.deleted=0 AND A.id = Action.id AND APT.name LIKE 'источник финансирования'%s) AS financeCodeName''' % condFinance)

            queryTable, cond = self.getCondAndQueryTable(u'planning%', AT = True, APT = 1, AP = 1, ET = 1, medicalAidTypeCond = False)
            queryTable = queryTable.innerJoin(self.tables.APHB, self.tables.APHB['id'].eq(self.tables.AP['id']))
            queryTable = queryTable.innerJoin(self.tables.OSHB, self.tables.OSHB['id'].eq(self.tables.APHB['value']))
            queryTable = queryTable.innerJoin(self.tables.OS, self.tables.OS['id'].eq(self.tables.OSHB['master_id']))
            queryTable, cond = self.compileCommonFilter(params, queryTable, cond)
            queryTable, cond = self.getCondByFilters(queryTable, cond, params)

            cond += [
                self.tables.APT['typeName'].like('HospitalBed'),
                    ]
            cond.append(self.tables.Action['status'].ne(3))
            cond.append(db.joinOr([self.tables.OS['id'].isNull(), self.tables.OS['deleted'].eq(0)]))
            personId = params.get('personId', None)
            if personId:
                cond.append(self.tables.Action['person_id'].eq(personId))
            presenceDay = params.get('presenceDay', None)
            if presenceDay:
                currentDateFormat = self.tables.Action['begDate'].formatValue(QtCore.QDate.currentDate())
                cond.append(u'DATEDIFF(%s, Action.begDate) = %d' % (forceString(currentDateFormat), presenceDay))
            permanent = params.get('permanent', 0)
            if permanent and permanent > 0:
                cond.append(self.tables.OSHB['isPermanent'].eq(permanent - 1))
            typeId = params.get('type', 0)
            if typeId:
                cond.append(self.tables.OSHB['type_id'].eq(typeId))
            profile = params.get('profileId', 0)
            if profile:
                if QtGui.qApp.defaultHospitalBedProfileByMoving():
                    cond.append(getPropertyAPHBP(profile))
                else:
                    cond.append(self.tables.OSHB['profile_id'].eq(profile))
            if orgStructureIdList:
                cond.append(getDataOrgStructure(u'подразделение', orgStructureIdList))
            filterBegDateTime = params.get('begDateTime', None)
            filterEndDateTime = params.get('endDateTime', None)
            changingDayTime = params.get('changingDayTime', QtCore.QTime(0, 0))
            if filterBegDateTime:
                cond.append(db.joinOr([self.tables.Action['directionDate'].isNull(),
                                       self.tables.Action['directionDate'].datetimeGe(filterBegDateTime)]))
            if filterEndDateTime:
                cond.append(db.joinOr([self.tables.Action['directionDate'].isNull(),
                                       self.tables.Action['directionDate'].datetimeLe(filterEndDateTime)]))
            orderBy = getOrderBy()

            queryTable, cols, cond = joinContractTable(queryTable, cols, cond)

            records = db.getRecordList(queryTable, cols, cond, orderBy)
            return records
        orgStructureIndex = params.get('orgStructureIndex', None)
        if orgStructureIndex:
            treeItem = orgStructureIndex.internalPointer() if orgStructureIndex.isValid() else None
            orgStructureIdList = getOrgStructureIdList(orgStructureIndex) if treeItem and treeItem._id else []
            recordType = db.getRecordEx(self.tables.OS, [self.tables.OS['id']], [self.tables.OS['deleted'].eq(0), self.tables.OS['type'].eq(4), self.tables.OS['id'].inlist(orgStructureIdList)])
            if recordType and forceRef(recordType.value('id')):
                orgStructureIdList = []

        indexLocalClient = params.get('clientLocation', None)
        if indexLocalClient == 2:
            records = getPlanning(orgStructureIdList, True)
        elif indexLocalClient == 1:
            records = getPlanningBeds(orgStructureIdList)
        else:
            records = getPlanning(orgStructureIdList, False)
        for record in records:
            financeCodeName = forceString(record.value('financeCodeName')).split(" ")
            if len(financeCodeName)>=2:
                idFinance = forceRef(financeCodeName[0]) if len(financeCodeName)>=1 else 0
                codeFinance = forceString(financeCodeName[1]) if len(financeCodeName)>=2 else u''
                nameFinance = forceString(financeCodeName[2]) if len(financeCodeName)>=3 else u''
            else:
                idFinance = 0

            finance = params.get('financeId', None)
            if not finance or finance == forceInt(idFinance):
                item = self.getItemFromRecord(record)
                if len(financeCodeName) >= 2:
                    item.update({
                            'nameFinance': nameFinance,
                            'codeFinance': codeFinance})
                if indexLocalClient == 1:
                    item.update({
                        'codeBed': forceString(record.value('codeBed')),
                        'nameBed': forceString(record.value('nameBed'))})
                # i4384@0019200 && i4384@0019156
                # Меняем местами колонки.
                # Было
                # 'plannedEndDate': forceDate(record.value('plannedEndDate'))
                # 'directionDate': forceDate(record.value('directionDate'))
                # Стало:
                item['plannedEndDate'] = forceDate(record.value('directionDate'))
                item['directionDate'] = forceDate(record.value('begDate'))

                self.items.append(item)
        self.reset()

