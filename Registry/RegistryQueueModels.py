# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Action import CActionTypeCache
from Events.Utils import getEventType
from library.InDocTable import CRecordListModel, CBoolInDocTableCol, CDateTimeInDocTableCol, CInDocTableCol, \
    CRBInDocTableCol
from library.Utils import forceInt, forceDateTime, forceDate, forceRef, toVariant, forceString


class CQueueModel(CRecordListModel):
    def __init__(self,  parent):
        CRecordListModel.__init__(self, parent)
        self.addCol(CBoolInDocTableCol(u'Отметка', 'status', 6))
        self.addCol(CDateTimeInDocTableCol(u'Дата и время приема', 'directionDate', 20)).setReadOnly()
        self.addCol(CInDocTableCol(u'Каб',          'office', 6)).setReadOnly()
        self.addCol(CRBInDocTableCol(u'Специалист', 'person_id', 20, 'vrbPersonWithSpeciality')).setReadOnly()
        self.addCol(CRBInDocTableCol(u'Записал',    'setPerson_id', 20, 'vrbPersonWithSpeciality')).setReadOnly()
        self.addCol(CInDocTableCol(u'Примечания',   'note', 6)).setReadOnly()


    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.column() == 0 and role == QtCore.Qt.CheckStateRole:
            row = index.row()
            item = self.items()[row]
            status = forceInt(item.value('status'))
            return toVariant(QtCore.Qt.Checked if status==0 else QtCore.Qt.Unchecked)
        elif role == QtCore.Qt.ToolTipRole:
            row = index.row()
            item = self.items()[row]
            reason = forceString(item.value('reason'))
            if reason:
                return toVariant(reason)
        elif role == QtCore.Qt.FontRole:
            row = index.row()
            item = self.items()[row]
            reason = forceString(item.value('reason'))
            if reason:
                font = QtGui.QFont()
                font.setBold(True)
                return toVariant(font)

        else:
            return CRecordListModel.data(self, index, role)


#    def setData(self, index, value, role=Qt.EditRole):
#        column = index.column()
#        row = index.row()
#        if role == Qt.CheckStateRole and QtGui.qApp.ambulanceUserCheckable() and column == 0:
#            db = QtGui.qApp.db
#            table = db.table('Action')
#            item = self.items()[row]
#            actionId = forceRef(item.value('id'))
#            status = forceInt(item.value('status'))
#            if actionId and status in (0, 1) and self.clientId:
#                newStatus = 0 if forceBool(value) else 1
#                actionRecord  = table.newRecord(['id', 'status'])
#                actionRecord.setValue('id', QVariant(actionId))
#                actionRecord.setValue('status', QVariant(newStatus))
#                try:
#                    db.updateRecord(table, actionRecord)
#                    item.setValue('status', QVariant(newStatus))
#                    self.emitCellChanged(row, column)
#                    dockResources = QtGui.qApp.mainWindow.dockResources
#                    if dockResources and dockResources.content:
#                        dockResources.content.modelAmbQueue.setStatus(self.clientId, actionId, newStatus)
#                        dockResources.content.tblAmbQueue.setFocus(Qt.OtherFocusReason)
#                    return True
#                except:
#                    pass
#                return True
#        return False

    def loadData(self, clientId = None):
        etcQueue = 'queue'
        atcQueue = 'queue'
        if clientId:
            self.clientId = clientId
            currentDate = forceDateTime(QtCore.QDate.currentDate())
            db = QtGui.qApp.db
            tableAction = db.table('Action')
            tableEvent = db.table('Event')
            tableActionProperty = db.table('ActionProperty')
            tableActionProperty_Action = db.table('ActionProperty_Action')
            tableActionProperty_rbReason = db.table('ActionProperty_rbReasonOfAbsence')
            tableReason = db.table('rbReasonOfAbsence')
            cols = [tableAction['id'],
                    tableAction['setPerson_id'],
                    tableAction['person_id'],
                    tableAction['status'],
                    tableAction['office'],
                    tableAction['directionDate'],
                    tableAction['note'],
                    tableActionProperty_Action['id'].alias('APAction_id'),
                    tableAction['event_id'],
                    tableReason['name'].alias('reason')]
            actionType = CActionTypeCache.getByCode(atcQueue)
            actionTypeId = actionType.id
            eventType = getEventType(etcQueue)
            eventTypeId = eventType.eventTypeId
            cond = [tableEvent['client_id'].eq(self.clientId),
                    tableEvent['setDate'].ge(currentDate),
                    tableEvent['deleted'].eq(0),
                    tableAction['deleted'].eq(0),
                    tableEvent['eventType_id'].eq(eventTypeId),
                    tableAction['actionType_id'].eq(actionTypeId)
                    ]
            tableQuery = tableAction
            tableQuery = tableQuery.innerJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
            tableQuery = tableQuery.leftJoin(tableActionProperty, tableActionProperty['action_id'].eq(tableAction['id']))
            tableQuery = tableQuery.innerJoin(tableActionProperty_Action, tableActionProperty_Action['value'].eq(tableAction['id']))
            tableQuery = tableQuery.leftJoin(tableActionProperty_rbReason, tableActionProperty_rbReason['id'].eq(tableActionProperty['id']))
            tableQuery = tableQuery.leftJoin(tableReason, tableReason['id'].eq(tableActionProperty_rbReason['value']))
            records = db.getRecordList(tableQuery, cols, cond, 'Action.directionDate')
            self.setItems(records)
        else:
            self.clearItems()


class CVisitByQueueModel(CRecordListModel):
    def __init__(self,  parent):
        CRecordListModel.__init__(self, parent)
        self.addCol(CBoolInDocTableCol(u'Выполнено', 'event_id', 6))
        self.addCol(CDateTimeInDocTableCol(u'Дата и время приема', 'directionDate', 20)).setReadOnly()
        self.addCol(CInDocTableCol(u'Каб',          'office', 6)).setReadOnly()
        self.addCol(CRBInDocTableCol(u'Специалист', 'person_id', 20, 'vrbPersonWithSpeciality')).setReadOnly()
        self.addCol(CRBInDocTableCol(u'Записал',    'setPerson_id', 20, 'vrbPersonWithSpeciality')).setReadOnly()
        self.addCol(CInDocTableCol(u'Примечания',   'note', 6)).setReadOnly()


    def loadData(self, clientId = None):
        if clientId:
            currentDateTime = forceDateTime(QtCore.QDateTime.currentDateTime())
            etcQueue = 'queue'
            atcQueue = 'queue'
            db = QtGui.qApp.db
            tableEvent = db.table('Event')
            tableAction = db.table('Action')
            tableVisit = db.table('Visit')
            tablePersonWithSpeciality = db.table('vrbPersonWithSpeciality')
            tableActionProperty_Action = db.table('ActionProperty_Action')
            tableOrgStructure = db.table('OrgStructure')
            cols = [tableAction['event_id'],
                    tableAction['id'],
                    tableAction['directionDate'],
                    tableAction['setPerson_id'],
                    tableAction['person_id'],
                    tableAction['office'],
                    tableAction['note'],
                    tablePersonWithSpeciality['speciality_id']
                    ]
            actionType = CActionTypeCache.getByCode(atcQueue)
            actionTypeId = actionType.id
            eventType = getEventType(etcQueue)
            eventTypeId = eventType.eventTypeId
            tableQuery = tableAction
            tableQuery = tableQuery.innerJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
            tableQuery = tableQuery.innerJoin(tableActionProperty_Action, tableActionProperty_Action['value'].eq(tableAction['id']))
            tableQuery = tableQuery.innerJoin(tablePersonWithSpeciality, tablePersonWithSpeciality['id'].eq(tableAction['person_id']))
            cond = [tableEvent['client_id'].eq(clientId),
                    tableAction['directionDate'].lt(currentDateTime),
                    tableEvent['deleted'].eq(0),
                    tableAction['deleted'].eq(0),
                    tableEvent['eventType_id'].eq(eventTypeId),
                    tableAction['actionType_id'].eq(actionTypeId)
                    ]
            recordBufferAction = db.getRecordList(tableQuery, cols, cond, 'Action.directionDate')
            listDirectionDateAction = []
            specialityIdList = []
            personIdList = []
            for recordDirectionDateAction in recordBufferAction:
                directionDate = forceDate(recordDirectionDateAction.value('directionDate'))
                if directionDate and directionDate not in listDirectionDateAction:
                    listDirectionDateAction.append(directionDate)
                specialityId = forceRef(recordDirectionDateAction.value('speciality_id'))
                if specialityId and specialityId not in specialityIdList:
                    specialityIdList.append(specialityId)
                personId = forceRef(recordDirectionDateAction.value('person_id'))
                if personId and personId not in personIdList:
                    personIdList.append(personId)
            if listDirectionDateAction:
                cols = [tableVisit['date'],
                        tableVisit['person_id'],
                        tableVisit['event_id'].alias('eventId'),
                        tablePersonWithSpeciality['speciality_id'],
                        tablePersonWithSpeciality['name'].alias('personName')
                        ]
                condVisit = [tableVisit['date'].inlist(listDirectionDateAction),
                             tableEvent['client_id'].eq(clientId),
                             tableEvent['deleted'].eq(0),
                             tableVisit['deleted'].eq(0)
                             ]
                condVisit.append(db.joinOr([tablePersonWithSpeciality['speciality_id'].inlist(specialityIdList), tableVisit['person_id'].inlist(personIdList)]))
                tableQueryVisit = tableVisit
                tableQueryVisit = tableQueryVisit.innerJoin(tableEvent, tableEvent['id'].eq(tableVisit['event_id']))
                tableQueryVisit = tableQueryVisit.innerJoin(tablePersonWithSpeciality, tablePersonWithSpeciality['id'].eq(tableVisit['person_id']))
                recordVisit = db.getRecordList(tableQueryVisit, cols, condVisit, 'Visit.date')

            for record in recordBufferAction:
                directionDate = forceDate(record.value('directionDate'))
                personId = forceRef(record.value('person_id'))
                specialityId = forceRef(record.value('speciality_id'))
                visitEventId = self.getVisit(directionDate, personId, specialityId, recordVisit)
                record.setValue('event_id', toVariant(visitEventId))
            self.setItems(recordBufferAction)
        else:
            self.clearItems()


    def getVisit(self, directionDate, personId, specialityId, recordVisit):
        for recordVisitData in recordVisit:
            if directionDate and (personId or specialityId):
                if directionDate == forceDate(recordVisitData.value('date')):
                    if personId == forceRef(recordVisitData.value('person_id')):
                        eventId = forceRef(recordVisitData.value('eventId'))
                        return eventId
                    elif specialityId == forceRef(recordVisitData.value('speciality_id')):
                        eventId = forceRef(recordVisitData.value('eventId'))
                        return eventId
        return None