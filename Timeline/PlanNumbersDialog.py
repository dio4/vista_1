# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Action import CAction
from Timeline.TimeTable import calcTimePlan, getEvent, CTimeItemDelegate, CTimeTableModel
from Ui_PlanNumbersDialog import Ui_PlanNumbersDialog
from library import constants
from library.DialogBase import CDialogBase
from library.Utils import forceBool, forceRef, forceString, forceTime, toVariant


class CPlanNumbersDialog(CDialogBase, Ui_PlanNumbersDialog):
    def __init__(self, parent, personId, date, items, visibleAmb, ciAmbChange, visibleHome, ciHomeChange):
        CDialogBase.__init__(self, parent)
        self.addModels('AmbNumbers', CPlanNumbersModel(self, constants.atcAmbulance, personId, date, items))
        self.addModels('HomeNumbers',CPlanNumbersModel(self, constants.atcHome, personId, date, items))
        self.addModels('PersonGaps', CPlanNumbersGapsModel(self, personId))
        self.addModels('OrgStructureGaps', CPlanNumbersGapsModel(self, personId))
        self.setupUi(self)
        self.setModels(self.tblAmbNumbers,  self.modelAmbNumbers, self.selectionModelAmbNumbers)
        self.setModels(self.tblHomeNumbers,  self.modelHomeNumbers, self.selectionModelHomeNumbers)
        self.setModels(self.tblPersonGaps,  self.modelPersonGaps, self.selectionModelPersonGaps)
        self.setModels(self.tblOrgStructureGaps,  self.modelOrgStructureGaps, self.selectionModelOrgStructureGaps)
        self.timeDelegate = CTimeItemDelegate(self)
        self.tblAmbNumbers.setItemDelegateForColumn(0, self.timeDelegate)
        self.tblHomeNumbers.setItemDelegateForColumn(0, self.timeDelegate)

        self.modelOrgStructureGaps.loadData(False)
        self.modelPersonGaps.loadData(True)

        if visibleAmb:
            self.modelAmbNumbers.loadData(ciAmbChange, self.tblPersonGaps.model().items)
        if visibleHome:
            self.modelHomeNumbers.loadData(ciHomeChange, self.tblPersonGaps.model().items)

    def saveData(self):
        if not self.checkData(self.modelAmbNumbers, self.modelAmbNumbers.tableItems[CTimeTableModel.ciAmbChange], self.tblAmbNumbers):
            return False
        if not self.checkData(self.modelHomeNumbers, self.modelHomeNumbers.tableItems[CTimeTableModel.ciHomeChange], self.tblHomeNumbers):
            return False
        self.modelAmbNumbers.saveData()
        self.modelHomeNumbers.saveData()
        return True


    def checkData(self, model, ciChange, widget):
        if model.action and model.eventId:
            if ciChange:
                if model.actionTypeCode == constants.atcAmbulance:
                    timeRange = model.tableItems[CTimeTableModel.ciAmbTimeRange]
                    begTime, endTime = timeRange if timeRange else None
                elif model.actionTypeCode == constants.atcHome:
                    timeRange = model.tableItems[CTimeTableModel.ciHomeTimeRange]
                    begTime, endTime = begTime, endTime = timeRange if timeRange else None
            else:
                begTime = model.action['begTime']
                endTime = model.action['endTime']
            lenItems = len(model.items)
            for row in xrange(lenItems):
                itemTime = model.items[row][0]
                if row > 0 and (row + 1) < lenItems:
                    firstTime = model.items[row - 1][0]
                    nextTime = model.items[row + 1][0]
                else:
                    firstTime = None
                    nextTime = None
                if not self.checkDataNumbers(begTime, endTime, itemTime, firstTime, nextTime, widget, row):
                    return False
        return True


    def checkDataNumbers(self, begTime, endTime, date, firstTime, nextTime, widget, row, column=0):
        result = True
        if row > 0:
            if firstTime and date:
                result = result and (firstTime <= date or self.checkValueMessage(u'Время предыдущего номерка %s не должно быть позже времени следующего номерка %s' % (firstTime.toString('HH:mm'), date.toString('HH:mm')), False, widget, row, column))
                result = result and (firstTime != date or self.checkValueMessage(u'Время предыдущего номерка %s не должно быть равно времени следующего номерка %s' % (firstTime.toString('HH:mm'), date.toString('HH:mm')), False, widget, row, column))
            if nextTime:
                result = result and (nextTime >= date or self.checkValueMessage(u'Время следующего номерка %s не должно быть меньше времени предыдущего номерка %s' % (nextTime.toString('HH:mm'), date.toString('HH:mm')), False, widget, row, column))
                result = result and (nextTime != date or self.checkValueMessage(u'Время следующего номерка %s не должно быть равно времени предыдущего номерка %s' % (nextTime.toString('HH:mm'), date.toString('HH:mm')), False, widget, row, column))
        else:
            result = result and (begTime <= date or self.checkValueMessage(u'Время номерка %s не должно быть раньше начала периода по плану %s' % (date.toString('HH:mm'), begTime.toString('HH:mm')), False, widget, row, column))
        result = result and (date <= endTime or self.checkValueMessage(u'Время номерка %s не должно быть позже конца периода по плану %s' % (date.toString('HH:mm'), endTime.toString('HH:mm')), False, widget, row, column))
        result = result and (date != endTime or self.checkValueMessage(u'Время номерка %s не должно быть равно концу периода по плану %s' % (date.toString('HH:mm'), endTime.toString('HH:mm')), False, widget, row, column))
        return result


class CPlanNumbersModel(QtCore.QAbstractTableModel):
    headerText = [u'Время', u'Каб', u'Занят']

    def __init__(self, parent, actionTypeCode, personId, date, tableItems):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.actionTypeCode = actionTypeCode
        self.action = None
        self.personId = personId
        self.date = date
        self.eventId = None
        self.tableItems = tableItems
        self.items = []


    def columnCount(self, index = QtCore.QModelIndex()):
        return 3


    def rowCount(self, index = QtCore.QModelIndex()):
        return len(self.items)


    def flags(self, index):
        row = index.row()
        column = index.column()
        item = self.items[row]
        if column == 0 and not forceBool(item[2]):
            return QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEditable|QtCore.Qt.ItemIsEnabled
        else:
            return QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled


    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.headerText[section])
        return QtCore.QVariant()


    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = index.column()
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            if column != 2:
                item = self.items[row]
                return QtCore.QVariant(item[column])
        if role == QtCore.Qt.EditRole:
            item = self.items[row]
            return QtCore.QVariant(item[column])
        elif role == QtCore.Qt.CheckStateRole:
            if column == 2:
                item = self.items[row]
                return toVariant(QtCore.Qt.Checked if item[column] else QtCore.Qt.Unchecked)
        return QtCore.QVariant()


    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            column = index.column()
            row = index.row()
            if column == 0:
                newValue = value.toTime()
                if self.items[row][column] != newValue:
                    self.items[row][column] = newValue
                    self.emitCellChanged(row, column)
            return True
        return False


    def emitCellChanged(self, row, column):
        index = self.index(row, column)
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)

    def loadData(self, ciChange, gaps=None):
        event = getEvent(constants.etcTimeTable, self.date, self.personId)
        if event:
            self.eventId = forceRef(event.value('id'))
            self.action = CAction.getAction(self.eventId, self.actionTypeCode)
            if self.action:
                queue = self.action['queue']
            else:
                queue = []
            notQueue = True
            for clientId in queue:
                if clientId:
                    notQueue = False
                    break
            if ciChange:
                if notQueue:
                    if self.actionTypeCode == constants.atcAmbulance:
                        office = self.tableItems[CTimeTableModel.ciAmbOffice]
                        timeRange = self.tableItems[CTimeTableModel.ciAmbTimeRange]
                        timeRange1 = self.tableItems[CTimeTableModel.ciAmbTimeRange1]
                        timeRange2 = self.tableItems[CTimeTableModel.ciAmbTimeRange2]
                        if timeRange1 and timeRange2:
                           result  = calcTimePlan(timeRange1, self.tableItems[CTimeTableModel.ciAmbPlan1], self.personId, True, result=[], interval=self.tableItems[CTimeTableModel.ciAmbInterval1])
                           result  = calcTimePlan(timeRange2, self.tableItems[CTimeTableModel.ciAmbPlan2], self.personId, True, result, self.tableItems[CTimeTableModel.ciAmbInterval2])
                           times = result
                        else:
                            times  = calcTimePlan(timeRange, self.tableItems[CTimeTableModel.ciAmbPlan], self.personId, True, result=[], interval=self.tableItems[CTimeTableModel.ciAmbInterval])
                    elif self.actionTypeCode == constants.atcHome:
                        office = u'на дому'
                        timeRange = self.tableItems[CTimeTableModel.ciHomeTimeRange]
                        timeRange1 = self.tableItems[CTimeTableModel.ciHomeTimeRange1]
                        timeRange2 = self.tableItems[CTimeTableModel.ciHomeTimeRange2]
                        if timeRange1 and timeRange2:
                           result  = calcTimePlan(timeRange1, self.tableItems[CTimeTableModel.ciHomePlan1], self.personId, True, result=[], interval=self.tableItems[CTimeTableModel.ciHomeInterval1])
                           result  = calcTimePlan(timeRange2, self.tableItems[CTimeTableModel.ciHomePlan2], self.personId, True, result, self.tableItems[CTimeTableModel.ciHomeInterval2])
                           times = result
                        else:
                            times  = calcTimePlan(timeRange, self.tableItems[CTimeTableModel.ciHomePlan], self.personId, True, result=[], interval=self.tableItems[CTimeTableModel.ciHomeInterval])
                else:
                    if self.actionTypeCode == constants.atcAmbulance:
                        office = self.action['office']
                    else:
                        office = u'на дому'
                    times = self.action['times']
            else:
                if self.action:
                    if self.actionTypeCode == constants.atcAmbulance:
                        office = self.action['office']
                    else:
                        office = u'на дому'
                    times = self.action['times']
                else:
                    office = u''
                    times = []
                    queue = []
        else:
            office = u''
            times = []
            queue = []
        try:
            if ciChange:
                if times:
                    lenQueue = len(queue) if queue else 0
                    diff = len(times)-lenQueue
                    if diff<0 :
                        times.extend([None]*(-diff))
                    elif diff>0 :
                        queue.extend([None]*diff)
                    for row in xrange(len(times)):
                        time = times[row] if row<len(times) else None
                        queueBusy = queue[row] if (queue and row<len(queue)) else None
                        item = [  time,
                                  forceString(office),
                                  forceString(queueBusy)
                               ]
                        self.items.append(item)
            else:
                diff = len(times)-len(queue)
                if diff<0 :
                    times.extend([None]*(-diff))
                elif diff>0 :
                    queue.extend([None]*diff)
                for row in xrange(len(queue)):
                    time = times[row] if row<len(times) else None
                    queueBusy = queue[row] if row<len(queue) else None
                    item = [  time,
                              forceString(office),
                              forceString(queueBusy)
                           ]
                    self.items.append(item)
        finally:
            self.reset()

    def saveData(self):
        if self.action and self.eventId:
            times = self.action['times']
            lenItems = len(self.items)
            diff = lenItems - len(times)
            if diff < 0:
                self.items.extend([None] * (-diff))
            elif diff > 0:
                times.extend([None] * diff)
            for row in xrange(lenItems):
                itemTime = self.items[row][0]
                times[row] = forceTime(itemTime)
            self.action['times'] = times
            db = QtGui.qApp.db
            db.transaction()
            try:
                self.saveDataNumbers(self.date.day() - 1)
                db.commit()
                if self.actionTypeCode == constants.atcAmbulance:
                    self.tableItems[CTimeTableModel.ciAmbChange] = False
                elif self.actionTypeCode == constants.atcHome:
                    self.tableItems[CTimeTableModel.ciHomeChange] = False
                self.action = CAction.getAction(self.eventId, self.actionTypeCode)
            except:
                db.rollback()
                QtGui.qApp.logCurrentException()
                raise

    def saveDataNumbers(self, day):
        if self.personId:
            db = QtGui.qApp.db
            eventTable = db.table('Event')
            db.transaction()
            try:
                dayInfo = self.tableItems
                event = getEvent(constants.etcTimeTable, self.date, self.personId)
                eventId = db.insertOrUpdate(eventTable, event)
                if self.actionTypeCode == constants.atcAmbulance:
                    if not self.action:
                        self.action = CAction.createByTypeCode(constants.atcAmbulance)
                    timeRange = dayInfo[CTimeTableModel.ciAmbTimeRange]
                    if timeRange:
                        self.action['begTime'], self.action['endTime'] = timeRange
                    else:
                        del self.action['begTime']
                        del self.action['endTime']
                    self.action['office'] = dayInfo[CTimeTableModel.ciAmbOffice]
                    self.action['plan'] = dayInfo[CTimeTableModel.ciAmbPlan]
                    timeRange1 = dayInfo[CTimeTableModel.ciAmbTimeRange1]
                    if timeRange1:
                        self.action['begTime1'], self.action['endTime1'] = timeRange1
                    else:
                        del self.action['begTime1']
                        del self.action['endTime1']
                    self.action['office1'] = dayInfo[CTimeTableModel.ciAmbOffice1]
                    self.action['plan1'] = dayInfo[CTimeTableModel.ciAmbPlan1]
                    timeRange2 = dayInfo[CTimeTableModel.ciAmbTimeRange2]
                    if timeRange2:
                        self.action['begTime2'], self.action['endTime2'] = timeRange2
                    else:
                        del self.action['begTime2']
                        del self.action['endTime2']
                    self.action['office2'] = dayInfo[CTimeTableModel.ciAmbOffice2]
                    self.action['plan2'] = dayInfo[CTimeTableModel.ciAmbPlan2]
                    self.action['fact'] = dayInfo[CTimeTableModel.ciAmbFact]
                    self.action['time'] = dayInfo[CTimeTableModel.ciAmbTime]
                    self.action.save(eventId)
                if self.actionTypeCode == constants.atcHome:
                    if not self.action:
                        self.action = CAction.createByTypeCode(constants.atcHome)
                    timeRange = dayInfo[CTimeTableModel.ciHomeTimeRange]
                    if timeRange:
                        self.action['begTime'], self.action['endTime'] = timeRange
                    else:
                        del self.action['begTime']
                        del self.action['endTime']
                    self.action['plan'] = dayInfo[CTimeTableModel.ciHomePlan]
                    timeRange1 = dayInfo[CTimeTableModel.ciHomeTimeRange1]
                    if timeRange1:
                        self.action['begTime1'], self.action['endTime1'] = timeRange1
                    else:
                        del self.action['begTime1']
                        del self.action['endTime1']
                    self.action['plan1'] = dayInfo[CTimeTableModel.ciHomePlan1]
                    timeRange2 = dayInfo[CTimeTableModel.ciHomeTimeRange2]
                    if timeRange2:
                        self.action['begTime2'], self.action['endTime2'] = timeRange2
                    else:
                        del self.action['begTime2']
                        del self.action['endTime2']
                    self.action['plan2'] = dayInfo[CTimeTableModel.ciHomePlan2]
                    self.action['fact'] = dayInfo[CTimeTableModel.ciHomeFact]
                    self.action['time'] = dayInfo[CTimeTableModel.ciHomeTime]
                    self.action.save(eventId)
                db.commit()
            except:
                db.rollback()
                QtGui.qApp.logCurrentException()
                raise


class CPlanNumbersGapsModel(CPlanNumbersModel):
    headerText = [u'Начало', u'Конец']

    def __init__(self, parent, personId):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.personId = personId
        self.items = []

    def columnCount(self, index=QtCore.QModelIndex()):
        return 2

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self.items)

    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.headerText[section])
        return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = index.column()
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            item = self.items[row]
            return QtCore.QVariant(item[column])
        return QtCore.QVariant()


    def loadData(self, personGap):
        def addGap(gapList, record):
            bTime = forceTime(record.value('begTime'))
            eTime = forceTime(record.value('endTime'))
            if bTime < eTime:
                gapList.append((bTime, eTime))
            elif bTime > eTime:
                gapList.append((bTime, QtCore.QTime(23, 59, 59, 999)))
                gapList.append((QtCore.QTime(0, 0), eTime))

        if self.personId:
            db = QtGui.qApp.db
            specialityId = forceRef(db.translate('Person', 'id', self.personId, 'speciality_id'))
            orgStructureBaseId = forceRef(db.translate('Person', 'id', self.personId, 'orgStructure_id'))
            result = []
            orgStructureId = orgStructureBaseId
            if not personGap:
                while orgStructureId:
                    recordsOrgStructureGap = db.getRecordList('OrgStructure_Gap', 'begTime, endTime',  'master_id=%d AND %s AND person_id IS NULL' %(orgStructureId, '(speciality_id=%d OR speciality_id IS NULL)'%(specialityId) if specialityId else '(speciality_id IS NULL)'), 'begTime, endTime')
                    for record in recordsOrgStructureGap:
                        addGap(result, record)
                    recordInheritGaps = db.getRecordEx('OrgStructure', 'inheritGaps', 'id=%d'%(orgStructureId))
                    inheritGaps = forceBool(recordInheritGaps.value(0)) if recordInheritGaps else (False if recordsOrgStructureGap else True)
                    if not inheritGaps:
                        break
                    orgStructureId = forceRef(db.translate('OrgStructure', 'id', orgStructureId, 'parent_id'))
            if personGap:
                orgStructureId = orgStructureBaseId
                while orgStructureId:
                    recordsPersonGap = db.getRecordList('OrgStructure_Gap', 'begTime, endTime',  'master_id=%d AND person_id=%d' %(orgStructureId, self.personId), 'begTime, endTime')
                    for record in recordsPersonGap:
                        addGap(result, record)
                    orgStructureId = forceRef(db.translate('OrgStructure', 'id', orgStructureId, 'parent_id'))
            result.sort()
            for begTimeGap, endTimeGap in result:
                item = [  begTimeGap,
                          endTimeGap
                       ]
                self.items.append(item)
        self.reset()
