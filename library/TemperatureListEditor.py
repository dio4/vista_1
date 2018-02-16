# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4.QtGui  import *

from Users.Rights         import *
from Events.Utils         import setActionPropertiesColumnVisible
from Orgs.Utils           import getPersonChiefs
from Events.Action        import ActionStatus, CAction
from Events.ActionPropertiesTable import CActionPropertiesTableModel
from library.Utils        import *
from library.DialogBase   import CConstructHelperMixin

from Ui_TemperatureListEditor import Ui_TemperatureListEditor


class CTemperatureListEditorDialog(QtGui.QDialog, CConstructHelperMixin, Ui_TemperatureListEditor):
    def __init__(self, parent, clientId, eventId, actionTypeIdList, clientSex, clientAge, setDate):
        QtGui.QDialog.__init__(self, parent)
        self.addModels('APActionProperties',   CActionPropertiesTableModel(self))
        self.btnTemperatureList = QPushButton(u'Температурный лист', self)
        self.btnTemperatureList.setObjectName('btnTemperatureList')
        self.setupUi(self)
        try:
            from PyQt4.Qwt5 import Qwt
            self.btnTemperatureList.setEnabled(True)
            self.btnTemperatureList.setToolTip(u'')
        except:
            self.btnTemperatureList.setEnabled(False)
            self.btnTemperatureList.setToolTip(u'Не удалось загрузить модуль Qwt.')
        self.buttonBox.addButton(self.btnTemperatureList, QtGui.QDialogButtonBox.ActionRole)
        self.setModels(self.tblAPProps, self.modelAPActionProperties, self.selectionModelAPActionProperties)
        
        self.clientId = clientId
        self.clientSex = clientSex
        self.clientAge = clientAge
        self.setDate = setDate.date() if setDate else None
        self.eventId = eventId
        self.actionTypeIdList = actionTypeIdList
        self.action = None
        self.timeList = {}
        self.isDirty = False
        currentDateTime = QtCore.QDateTime.currentDateTime()
        self.edtDate.setDate(currentDateTime.date())
        self.edtTime.setTime(currentDateTime.time())
        self.cmbTimeEdit.setCurrentIndex(0)


    @pyqtSlot(QModelIndex, QModelIndex)
    def on_modelAPActionProperties_dataChanged(self, topLeft, bottomRight):
        self.isDirty = True


    def canClose(self):
        if self.isDirty:
            res = QtGui.QMessageBox.warning( self,
                                      u'Внимание!',
                                      u'Данные были изменены.\nСохранить изменения?',
                                      QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                      QtGui.QMessageBox.Yes)
            if res == QtGui.QMessageBox.Yes:
                self.isDirty = False
                return True
        return False


    def closeEvent(self, event):
        if self.canClose():
            self.isDirty = False
            self.action.save()
        QtGui.QDialog.closeEvent(self, event)


    def updatePropTable(self, action):
        self.tblAPProps.model().setAction(action, self.clientId, self.clientSex, self.clientAge)
        self.tblAPProps.resizeRowsToContents()


    def createAction(self):
        self.action = None
        if self.clientId:
            db = QtGui.qApp.db
            tableAction = db.table('Action')
            date = self.edtDate.date()
            time = self.edtTime.time()
            execPersonId = self.cmbExecPerson.value()
            if not execPersonId:
                execPersonId = QtGui.qApp.userId
                self.cmbExecPerson.setValue(execPersonId)
            dialogDateTime = QtCore.QDateTime(date, time)
            cond = [tableAction['deleted'].eq(0),
                    tableAction['event_id'].eq(self.eventId),
                    tableAction['actionType_id'].inlist(self.actionTypeIdList)
                    ]
            cond.append(tableAction['endDate'].eq(dialogDateTime))
            record = db.getRecordEx(tableAction, '*', cond)
            if record:
                execPersonId = forceRef(record.value('person_id'))
                if execPersonId:
                    self.cmbExecPerson.setValue(execPersonId)
                else:
                    self.cmbExecPerson.setValue(QtGui.qApp.userId)
                record.setValue('person_id', toVariant(execPersonId))
                self.action = CAction(record=record)
            else:
                actionTypeId = self.actionTypeIdList[0]
                if actionTypeId:
                    record = tableAction.newRecord()
                    record.setValue('event_id', toVariant(self.eventId))
                    record.setValue('actionType_id', toVariant(actionTypeId))
                    record.setValue('begDate', toVariant(dialogDateTime))
                    record.setValue('endDate', toVariant(dialogDateTime))
                    record.setValue('status',  toVariant(2))
                    record.setValue('person_id', toVariant(execPersonId))
                    record.setValue('org_id',  toVariant(QtGui.qApp.currentOrgId()))
                    record.setValue('amount',  toVariant(1))
                    self.action = CAction(record=record)
            if self.action:
                tableEvent = db.table('Event')
                prevSetDate = None
                prevEventId = None
                prevEventRecord = db.getRecordEx(tableEvent, [tableEvent['prevEvent_id'], tableEvent['setDate']], [tableEvent['id'].eq(self.eventId), tableEvent['deleted'].eq(0)])
                if prevEventRecord:
                    prevEventId = forceRef(prevEventRecord.value('prevEvent_id'))
                    prevSetDate = forceRef(prevEventRecord.value('setDate'))
                while prevEventId:
                    prevEventRecord = db.getRecordEx(tableEvent, [tableEvent['prevEvent_id'], tableEvent['setDate']], [tableEvent['id'].eq(prevEventId), tableEvent['deleted'].eq(0)])
                    if prevEventRecord:
                        prevEventId = forceRef(prevEventRecord.value('prevEvent_id'))
                        prevSetDate = forceRef(prevEventRecord.value('setDate'))
                    else:
                        prevEventId = None
                begDate = forceDate(record.value('begDate'))
                if (self.setDate and begDate) or (prevSetDate and begDate):
                    if prevSetDate:
                        self.action[u'День болезни'] = prevSetDate.daysTo(begDate) + 1
                    else:
                        self.action[u'День болезни'] = self.setDate.daysTo(begDate) + 1
                setActionPropertiesColumnVisible(self.action._actionType, self.tblAPProps)
                self.updatePropTable(self.action)
                self.tblAPProps.setEnabled(self.getIsLocked(self.action._record))
        self.isDirty = False
        return self.action


    def getIsLocked(self, record):
        if record:
            status = forceInt(record.value('status'))
            personId = forceRef(record.value('person_id'))
            if status == ActionStatus.Done and personId:
                return ( QtGui.qApp.userId == personId
                                 or QtGui.qApp.userHasRight(urEditOtherPeopleAction)
                                 or QtGui.qApp.userId in getPersonChiefs(personId)
                               )
        return False


    @QtCore.pyqtSlot()
    def on_btnTemperatureList_clicked(self):
        if self.canClose():
            self.isDirty = False
            self.action.save()
        try:
            from ThermalSheet.TemperatureList import CTemperatureListParameters, CTemperatureList
            dialog = CTemperatureListParameters(self, self.eventId)
            if dialog.exec_():
                demo = CTemperatureList(self, dialog.params(), self.clientId, self.eventId)
                demo.getInfo()
                demo.exec_()
        except:
            QtGui.qApp.logCurrentException()


    @pyqtSlot(QTime)
    def on_edtTime_timeChanged(self, time):
        if self.canClose():
            self.isDirty = False
            self.action.save()
        self.createAction()


    @pyqtSlot(QDate)
    def on_edtDate_dateChanged(self, date):
        if self.canClose():
            self.isDirty = False
            self.action.save()
        self.getTimeList()
        self.cmbTimeEdit.setCurrentIndex(0)
        self.createAction()


    @pyqtSlot(int)
    def on_cmbTimeEdit_currentIndexChanged(self, index):
        if index > 0:
            time = self.timeList.get(index, QtCore.QTime())
            self.edtTime.setTime(time)
        else:
            currentDateTime = QtCore.QDateTime.currentDateTime()
            self.edtTime.setTime(currentDateTime.time())
            self.cmbExecPerson.setValue(QtGui.qApp.userId)


    def getTimeList(self):
        self.timeList = {}
        countItems = self.cmbTimeEdit.count()
        countItem = countItems - 1
        while countItem > 0:
            self.cmbTimeEdit.removeItem(countItem)
            countItem -= 1
        if self.eventId and self.actionTypeIdList:
            db = QtGui.qApp.db
            tableAction = db.table('Action')
            date = forceDate(self.edtDate.date())
            cond = [tableAction['deleted'].eq(0),
                    tableAction['event_id'].eq(self.eventId),
                    tableAction['actionType_id'].inlist(self.actionTypeIdList)
                    ]
            cond.append(tableAction['endDate'].dateEq(date))
            records = db.getRecordList(tableAction, [tableAction['id'], tableAction['endDate']], cond, 'Action.endDate')
            idx = 1
            for record in records:
                actionId = forceRef(record.value('id'))
                endDate = forceDateTime(record.value('endDate'))
                endTime = endDate.time()
                self.timeList[idx] = endTime
                self.cmbTimeEdit.insertItem(idx, endTime.toString('hh:mm'))
                idx += 1
        if len(self.timeList) > 0:
            endTime = self.timeList.get(idx-1, None)
            if endTime:
                self.lblLastTime.setText(endTime.toString('hh:mm'))
            else:
                self.lblLastTime.setText(u'')
        else:
            self.lblLastTime.setText(u'нет')

