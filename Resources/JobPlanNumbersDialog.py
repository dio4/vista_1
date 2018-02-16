# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.DialogBase         import CDialogBase
from library.Utils              import forceBool, forceDateTime, forceRef, forceTime, toVariant

from Timeline.TimeTable         import CTimeItemDelegate

from Ui_JobPlanNumbersDialog    import Ui_JobPlanNumbersDialog


class CJobPlanNumbersDialog(CDialogBase, Ui_JobPlanNumbersDialog):
    def __init__(self, parent, orgStructureId, jobTypeId, date, items):
        CDialogBase.__init__(self, parent)
        self.addModels('JobAmbNumbers', CJobPlanNumbersModel(self, orgStructureId, date, items))
        self.addModels('JobOrgStructureGaps', CJobPlanNumbersGapsModel(self, orgStructureId))
        self.setupUi(self)
        self.setModels(self.tblJobAmbNumbers,  self.modelJobAmbNumbers, self.selectionModelJobAmbNumbers)
        self.setModels(self.tblJobOrgStructureGaps,  self.modelJobOrgStructureGaps, self.selectionModelJobOrgStructureGaps)
        self.timeDelegate = CTimeItemDelegate(self)
        self.tblJobAmbNumbers.setItemDelegateForColumn(0, self.timeDelegate)
        self.modelJobAmbNumbers.loadData(orgStructureId, jobTypeId, date)
        self.modelJobOrgStructureGaps.loadData()


    def saveData(self):
        if not self.checkData(self.modelJobAmbNumbers, self.modelJobAmbNumbers.tableItems.changed, self.tblJobAmbNumbers):
            return False
        self.modelJobAmbNumbers.saveData()
        return True


    def checkData(self, model, changed, widget):
        if model.tableItems:
            if changed:
                timeRange = model.tableItems.timeRange
                begTime, endTime = timeRange if timeRange else (None, None)
            else:
                if model.tableItems.record:
                    begTime = forceTime(model.tableItems.record.value('begTime'))
                    endTime = forceTime(model.tableItems.record.value('endTime'))
                else:
                    begTime, endTime = None, None
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
            if firstTime:
                result = result and (firstTime <= date or self.checkValueMessage(u'Время предыдущего номерка %s не должно быть позже времени следующего номерка %s' % (firstTime.toString('HH:mm'), date.toString('HH:mm')), False, widget, row, column))
                result = result and (firstTime != date or self.checkValueMessage(u'Время предыдущего номерка %s не должно быть равно времени следующего номерка %s' % (firstTime.toString('HH:mm'), date.toString('HH:mm')), False, widget, row, column))
            if nextTime:
                result = result and (nextTime >= date or self.checkValueMessage(u'Время следующего номерка %s не должно быть меньше времени предыдущего номерка %s' % (nextTime.toString('HH:mm'), date.toString('HH:mm')), False, widget, row, column))
                result = result and (nextTime != date or self.checkValueMessage(u'Время следующего номерка %s не должно быть равно времени предыдущего номерка %s' % (nextTime.toString('HH:mm'), date.toString('HH:mm')), False, widget, row, column))
        else:
            result = result and (begTime or self.checkValueMessage(u'Отсутствует время начала периода по плану %s' % (begTime.toString('HH:mm')), False, widget, row, column))
            result = result and (begTime <= date or self.checkValueMessage(u'Время номерка %s не должно быть раньше начала периода по плану %s' % (date.toString('HH:mm'), begTime.toString('HH:mm')), False, widget, row, column))
        result = result and (endTime or self.checkValueMessage(u'Отсутствует время конца периода по плану %s' % (endTime.toString('HH:mm')), False, widget, row, column))
        result = result and (date <= endTime or self.checkValueMessage(u'Время номерка %s не должно быть позже конца периода по плану %s' % (date.toString('HH:mm'), endTime.toString('HH:mm')), False, widget, row, column))
        result = result and (date != endTime or self.checkValueMessage(u'Время номерка %s не должно быть равно концу периода по плану %s' % (date.toString('HH:mm'), endTime.toString('HH:mm')), False, widget, row, column))
        return result


class CJobPlanNumbersModel(QtCore.QAbstractTableModel):
    headerText = [u'Время', u'Занят']

    def __init__(self, parent, orgStructureId, date, tableItems):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.orgStructureId = orgStructureId
        self.date = date
        self.tableItems = tableItems
        self.items = []


    def columnCount(self, index = QtCore.QModelIndex()):
        return 2


    def rowCount(self, index = QtCore.QModelIndex()):
        return len(self.items)


    def flags(self, index):
        row = index.row()
        column = index.column()
        item = self.items[row]
        if column == 0 and not forceBool(item[1]):
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
            if column != 1:
                item = self.items[row]
                return QtCore.QVariant(item[column])
        if role == QtCore.Qt.EditRole:
            item = self.items[row]
            return QtCore.QVariant(item[column])
        elif role == QtCore.Qt.CheckStateRole:
            if column == 1:
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


    def loadData(self, orgStructureId, jobTypeId, date):
        self.items = []
        try:
            #FIXME: atronah: tableItems.changed - это функция (CJobPlanItem.changed()), а не атрибут типа bool
            if self.tableItems.changed() or (self.tableItems and (not self.tableItems.record or not self.tableItems.tickets)):
                self.tableItems.updateRecord(orgStructureId, jobTypeId, date)
            for ticket in self.tableItems.tickets:
                dateTime = forceDateTime(ticket.value('datetime'))
                item = [  dateTime.time(),
                          forceBool(ticket.value('status')),
                          forceRef(ticket.value('id')),
                          forceRef(ticket.value('master_id')),
                          dateTime.date()
                       ]
                self.items.append(item)
        finally:
            self.reset()


    def saveData(self):
        self.tableItems.ticketIsDirty = [False]*len(self.tableItems.tickets)
        for i, ticket in enumerate(self.tableItems.tickets):
            datetime = QtCore.QDateTime(self.items[i][4], self.items[i][0]) if i < len(self.items) else None
            ticket.setValue('datetime', toVariant(datetime))
            ticket.setValue('idx', toVariant(i))
            self.tableItems.ticketIsDirty[i] = True

        #FIXME: atronah: закомментировал строку ниже, так как tableItems.changed - это функция (CJobPlanItem.changed()), а не атрибут типа bool
        # self.tableItems.changed = False


class CJobPlanNumbersGapsModel(CJobPlanNumbersModel):
    headerText = [u'Начало', u'Конец']

    def __init__(self, parent, orgStructureId):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.orgStructureId = orgStructureId
        self.items = []


    def columnCount(self, index = QtCore.QModelIndex()):
        return 2


    def rowCount(self, index = QtCore.QModelIndex()):
        return len(self.items)


    def flags(self, index):
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
            item = self.items[row]
            return QtCore.QVariant(item[column])
        return QtCore.QVariant()


    def loadData(self):
        def addGap(gapList, record):
            bTime = forceTime(record.value('begTime'))
            eTime = forceTime(record.value('endTime'))
            if bTime < eTime:
                gapList.append((bTime, eTime))
            elif bTime > eTime:
                gapList.append((bTime, QtCore.QTime(23, 59, 59, 999)))
                gapList.append((QtCore.QTime(0, 0), eTime))

        db = QtGui.qApp.db
        orgStructureBaseId = self.orgStructureId
        result = []
        orgStructureId = orgStructureBaseId
        while orgStructureId:
            recordsOrgStructureGap = db.getRecordList('OrgStructure_Gap', 'begTime, endTime',  'master_id=%d' %(orgStructureId), 'begTime, endTime')
            for record in recordsOrgStructureGap:
                addGap(result, record)
            recordInheritGaps = db.getRecordEx('OrgStructure', 'inheritGaps', 'id=%d'%(orgStructureId))
            inheritGaps = forceBool(recordInheritGaps.value(0)) if recordInheritGaps else (False if recordsOrgStructureGap else True)
            if not inheritGaps:
                break
            orgStructureId = forceRef(db.translate('OrgStructure', 'id', orgStructureId, 'parent_id'))
        result.sort()
        for begTimeGap, endTimeGap in result:
            item = [  begTimeGap,
                      endTimeGap
                   ]
            self.items.append(item)
        self.reset()
