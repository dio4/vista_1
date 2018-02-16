# -*- coding: utf-8 -*-
# ############################################################################
##
## Copyright (C) 2014 Vista Software. All rights reserved.
##
#############################################################################

__author__ = 'atronah'

'''
    author: atronah
    date:   20.10.2014
'''


from PyQt4 import QtCore
from PyQt4 import QtGui
from library.ElectronicQueue.EQControl import CEQRemoteControl, CAbstractEQControl, CEQGuiControl #FIXME: atronah: убрать завязку на конкретный тип контрола (CEQRemoteControl)


# import time #debug: atronah:

class CEQControlModel(QtCore.QAbstractTableModel):
    reenableTimeout = 5000 #mseconds

    iName = 0
    iQueueType = 1
    iOrgStructure = 2
    iControlState = 3

    columnNameList = [u'Название пульта', u'Очередь', u'Кабинет', u'Состояние']

    StateColors = {CAbstractEQControl.EnablingState : QtCore.Qt.cyan,
                   CAbstractEQControl.DisablingState : QtCore.Qt.cyan,
                   CAbstractEQControl.EnabledState : QtCore.Qt.green,
                   CAbstractEQControl.ActiveState : QtCore.Qt.green,
                   CAbstractEQControl.ErrorState : QtCore.Qt.red}

    calledNext = QtCore.pyqtSignal(int, bool) # (controlId, isCurrentComplete)
    calledPrev = QtCore.pyqtSignal(int, bool) # (controlId, isCurrentComplete)
    reCalled = QtCore.pyqtSignal(int) # (controlId)
    calledCustom = QtCore.pyqtSignal(int, bool, QtCore.QString) # (controlId, isCurrentComplete, value)
    # started = QtCore.pyqtSignal(int) # (controlId) #TODO: atronah: по-моему уже не нужно
    # stopped = QtCore.pyqtSignal(int) # (controlId) #TODO: atronah: по-моему уже не нужно

    openedSettings = QtCore.pyqtSignal()

    buttonsStateUpdated = QtCore.pyqtSignal(int, int) # (controlId, state)

    addedQueueType = QtCore.pyqtSignal(int) # (queueTypeId)
    removedQueueType = QtCore.pyqtSignal(int) # (queueTypeId)

    prevValueChanged = QtCore.pyqtSignal(int, QtCore.QString)  # (controlId, value)
    currentValueChanged = QtCore.pyqtSignal(int, QtCore.QString)  # (controlId, value)
    nextValueChanged = QtCore.pyqtSignal(int, QtCore.QString)  # (controlId, value)

    controlChanged =  QtCore.pyqtSignal(int) # (controlId)
    controlActivated = QtCore.pyqtSignal(int) # (controlId)
    controlDisabled = QtCore.pyqtSignal(int) # (controlId)

    controlOfficeChanged = QtCore.pyqtSignal(int, QtCore.QString)  # (controlId, officeName)

    def __init__(self, parent = None):
        super(CEQControlModel, self).__init__(parent)
        self._mapControlIdToRow = {}
        self._queueNameResolver = {}
        self._orgStructureNameResolver = {}
        self._items = []
        self._guiControlId = None
        self._activedQueueTypesCache = None

        self._lastStateDict = {}

        self._reenableTimerId = None



    def initGuiControl(self, defaultOrgStructureId, defaultQueueTypeId = None):
        if self._guiControlId is None:
            control = CEQGuiControl()
            self.addControl(defaultOrgStructureId, defaultQueueTypeId, control, u'Локальная кнопка')
            self._guiControlId = control.controlId()
            control.setEnabled(self._guiControlId, True)



    def guiControl(self):
        return self.control(self._guiControlId)


    def guiControlId(self):
        return self._guiControlId


    def addControl(self, orgStructureId, queueTypeId, control, name = None):
        if isinstance(control, CAbstractEQControl):
            row = len(self._items)

            self._mapControlIdToRow[control.controlId()] = row

            control.stateChanged.connect(self.onStateChanged, QtCore.Qt.QueuedConnection)
            control.reCalled.connect(self.reCalled, QtCore.Qt.QueuedConnection)
            control.calledNext.connect(self.calledNext, QtCore.Qt.QueuedConnection)
            control.calledPrev.connect(self.calledPrev, QtCore.Qt.QueuedConnection)
            control.calledCustom.connect(self.calledCustom, QtCore.Qt.QueuedConnection)
            # control.started.connect(self.started, QtCore.Qt.QueuedConnection)
            # control.stopped.connect(self.stopped, QtCore.Qt.QueuedConnection)

            control.openedSettings.connect(self.openedSettings, QtCore.Qt.QueuedConnection)

            self.buttonsStateUpdated.connect(control.setButtonsState)

            self.prevValueChanged.connect(control.changePrevValue)
            self.currentValueChanged.connect(control.changeCurrentValue)
            self.nextValueChanged.connect(control.changeNextValue)

            self.controlOfficeChanged.connect(control.changeOfficeName)

            self.controlDisabled.connect(control.setDisabled)

            self.beginInsertRows(QtCore.QModelIndex(), row, row)
            if queueTypeId and queueTypeId not in self.queueTypes():
                self.addedQueueType.emit(queueTypeId)
            self._items.append({'control' : control,
                                'queueTypeId' : queueTypeId,
                                'orgStructureId' : orgStructureId,
                                'name' : name
            })
            self.controlOfficeChanged.emit(control.controlId(),
                                           self._orgStructureNameResolver.get(orgStructureId, u'{%s}' % orgStructureId))
            self.controlChanged.emit(control.controlId())
            self.endInsertRows()
            self._activedQueueTypesCache = None
            return True
        return False


    def controls(self , queueTypeId = None):
        return [item['control'] for item in self._items if queueTypeId is None or item['queueTypeId'] == queueTypeId]


    def canBeRemoved(self, controlId):
        if isinstance(self.control(controlId), CEQRemoteControl):
            return True
        return False


    def removeControl(self, controlId):
        row = self._getRowById(controlId)
        if row is not None:
            self.beginRemoveRows(QtCore.QModelIndex(), row, row)
            controlInfo = self._items.pop(row)
            self.endRemoveRows()

            queueTypeId = controlInfo['queueTypeId']
            if queueTypeId not in self.queueTypes():
                self.removedQueueType.emit(queueTypeId)

            control = controlInfo['control']
            control.setDisabled(controlId)

            control.stateChanged.disconnect(self.onStateChanged)
            control.reCalled.disconnect(self.reCalled)
            control.calledNext.disconnect(self.calledNext)
            control.calledPrev.disconnect(self.calledPrev)
            control.calledCustom.disconnect(self.calledCustom)
            control.openedSettings.disconnect(self.openedSettings)
            # control.started.disconnect(self.started)
            # control.stopped.disconnect(self.stopped)

            self.buttonsStateUpdated.disconnect(control.setButtonsState)

            self.prevValueChanged.disconnect(control.changePrevValue)
            self.currentValueChanged.disconnect(control.changeCurrentValue)
            self.nextValueChanged.disconnect(control.changeNextValue)
            self.controlOfficeChanged.disconnect(control.changeOfficeName)

            #update\regenerate _mapControlIdToRow
            for row in xrange(row, len(self._items)):
                controlId = self._items[row]['control'].controlId()
                self._mapControlIdToRow[controlId] = row

            self._activedQueueTypesCache = None


    def _getRowById(self, controlId):
        row = self._mapControlIdToRow.get(controlId, None)
        return row if row in xrange(len(self._items)) else None


    def _getDataById(self, controlId, dataName):
        row = self._getRowById(controlId)
        if row is not None:
            return self._items[row].get(dataName, None)
        return None


    def control(self, controlId):
        return self._getDataById(controlId, 'control')


    def name(self, controlId):
        return self._getDataById(controlId, 'name')


    def controlIdByIndex(self, index):
        if index.isValid():
            row = index.row()
            if row in xrange(len(self._items)):
                return self._items[row]['control'].controlId()
        return 0


    def queueTypeId(self, controlId):
        return self._getDataById(controlId, 'queueTypeId')


    def setQueueTypeId(self, controlId, queueTypeId):
        row = self._getRowById(controlId)
        if row is not None and queueTypeId:
            index = self.index(row, self.iQueueType)
            self.setData(index, QtCore.QVariant(queueTypeId))


    def orgStructureId(self, controlId):
        return self._getDataById(controlId, 'orgStructureId')


    def setOrgStructureId(self, controlId, orgStructureId):
        row = self._getRowById(controlId)
        if row is not None and orgStructureId:
            index = self.index(row, self.iOrgStructure)
            self.setData(index, QtCore.QVariant(orgStructureId))



    # def controlListByQueueId(self, queueTypeId):
    #     return [item['control'] for item in self._items if item['queueTypeId'] == queueTypeId]


    def queueTypes(self):
        return set([item['queueTypeId'] for item in self._items])


    def activedQueueTypes(self):
        if self._activedQueueTypesCache is None:
            self._activedQueueTypesCache = set()
            for controlInfo in self._items:
                if controlInfo['control'].isActive():
                    self._activedQueueTypesCache.add(controlInfo['queueTypeId'])
        return self._activedQueueTypesCache


    def setQueueNameResolver(self, resolver):
        self._queueNameResolver = resolver


    def setOrgStructureNameResolver(self, resolver):
        self._orgStructureNameResolver = resolver


    def clear(self, isRemoveAll = False):
        for controlId in self._mapControlIdToRow.keys():
            if isRemoveAll or self.canBeRemoved(controlId):
                self.removeControl(controlId)


    #--- re-implement methods ---
    def rowCount(self, index = QtCore.QModelIndex()):
        return len(self._items)


    def columnCount(self, index = QtCore.QModelIndex()):
        return len(self.columnNameList)


    def flags(self, index):
        flags = super(CEQControlModel, self).flags(index)
        if index.isValid():
            row = index.row()
            if row in xrange(self.rowCount()):
                flags |= QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

        return flags


    def data(self, index, role = QtCore.Qt.DisplayRole):
        if index.isValid():
            row = index.row()
            if row in xrange(self.rowCount()):
                column = index.column()
                controlInfo = self._items[row]
                if role == QtCore.Qt.DisplayRole:
                    if column == self.iQueueType:
                        queueTypeId = controlInfo['queueTypeId']
                        #TODO: atronah: останавливать работу с прошлой очередью и сообщать о появлении новой очереди
                        queueName = self._queueNameResolver.get(queueTypeId, u'{%s}' % queueTypeId)
                        return QtCore.QVariant(queueName)
                    elif column == self.iName:
                        name = unicode(controlInfo['name'])
                        if not name:
                            name = u'control №%s' % (row + 1)
                        control = controlInfo['control']
                        if isinstance(control, CEQRemoteControl):
                            name += ' (%s:%s)' % (control.host(), control.port())
                        return QtCore.QVariant(name)
                    elif column == self.iControlState:
                        control = controlInfo['control']
                        return QtCore.QVariant(control.stateName(control.currentState()))
                    elif column == self.iOrgStructure:
                        orgStructureId = controlInfo['orgStructureId']
                        #TODO: atronah: останавливать работу с прошлой очередью и сообщать о появлении новой очереди
                        orgStructureName = self._orgStructureNameResolver.get(orgStructureId, u'{%s}' % orgStructureId)
                        return QtCore.QVariant(orgStructureName)


                elif role == QtCore.Qt.BackgroundRole:
                    if column == self.iControlState:
                        control = controlInfo['control']
                        controlStateColor = self.StateColors.get(control.currentState(), None)
                        if controlStateColor is not None:
                            return QtCore.QVariant(QtGui.QBrush(controlStateColor))

        return QtCore.QVariant()


    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid():
            row = index.row()
            if row in xrange(self.rowCount()):
                column = index.column()
                if role == QtCore.Qt.EditRole:
                    controlInfo = self._items[row]
                    if column == self.iName:
                        if value.type() == QtCore.QVariant.String:
                            controlInfo['name'] = value.toString()
                        elif value.type() == QtCore.QVariant.List:
                            valueList = value.toList()
                            if len(valueList) == 3:
                                control = controlInfo['control']
                                controlInfo['name'] = valueList[0].toString()
                                needReconnect = False
                                host = valueList[1].toString()
                                if host != control.host():
                                    control.setHost(host)
                                    needReconnect = True
                                port, isOk = valueList[2].toInt()
                                if isOk and port != control.port():
                                    control.setPort(port)
                                    needReconnect = True
                                if needReconnect:
                                    control.reEnable()
                            else:
                                return False
                        else:
                            return False
                        self.dataChanged.emit(index, index)
                        return True
                    elif column == self.iQueueType:
                        queueTypeId, isOk = value.toInt()
                        oldQueueTypeId = controlInfo['queueTypeId']
                        if isOk and oldQueueTypeId != queueTypeId:
                            queueTypes = self.queueTypes()
                            if queueTypeId not in queueTypes:
                                self.addedQueueType.emit(queueTypeId)
                            controlInfo['queueTypeId'] = queueTypeId
                            if oldQueueTypeId not in queueTypes:
                                self.removedQueueType.emit(oldQueueTypeId)
                            self._activedQueueTypesCache = None
                            self.dataChanged.emit(index, index)
                            self.controlChanged.emit(controlInfo['control'].controlId())
                            return True
                    elif column == self.iOrgStructure:
                        orgStructureId, isOk = value.toInt()
                        oldOrgStructureId = controlInfo['orgStructureId']
                        if isOk and oldOrgStructureId != orgStructureId:
                            controlInfo['orgStructureId'] = orgStructureId
                            controlId = controlInfo['control'].controlId()
                            orgStructureName = self._orgStructureNameResolver.get(orgStructureId, u'{%s}' % orgStructureId)

                            self.dataChanged.emit(index, index)
                            self.controlChanged.emit(controlId)
                            self.controlOfficeChanged.emit(controlId, orgStructureName)
                            return True

        return super(CEQControlModel, self).setData(index, value, role)


    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if section in xrange(self.columnCount()):
                return QtCore.QVariant(self.columnNameList[section])
        return super(CEQControlModel, self).headerData(section, orientation, role)



    #--- slots ---
    @QtCore.pyqtSlot(int, int, int)
    def onStateChanged(self, controlId, state):
        row = self._getRowById(controlId)
        if row is not None:
            index = self.index(row, self.iControlState)
            if state == CAbstractEQControl.ActiveState:
                # print time.time(), 'control activated ', controlId #debug: atronah:
                self.controlActivated.emit(controlId)
            if state not in [CAbstractEQControl.DisabledState, CAbstractEQControl.DisablingState]:
                self._lastStateDict[controlId] = state

            self.dataChanged.emit(index, index)
            self.controlChanged.emit(controlId)
            self._activedQueueTypesCache = None


    @QtCore.pyqtSlot(int, int)
    def updateButtonsState(self, controlId, state):
        # print time.time(), 'update button state for', controlId #debug: atronah:
        self.buttonsStateUpdated.emit(controlId, state)


    @QtCore.pyqtSlot(int, QtCore.QString)
    def changePrevValue(self, queueTypeId, value):
        for item in self._items:
            if item['queueTypeId'] == queueTypeId:
                self.prevValueChanged.emit(item['control'].controlId(), value)




    @QtCore.pyqtSlot(int, QtCore.QString)
    def changeCurrentValue(self, queueTypeId, value):
        for item in self._items:
            if item['queueTypeId'] == queueTypeId:
                self.currentValueChanged.emit(item['control'].controlId(), value)


    @QtCore.pyqtSlot(int, QtCore.QString)
    def changeNextValue(self, queueTypeId, value):
        for item in self._items:
            if item['queueTypeId'] == queueTypeId:
                self.nextValueChanged.emit(item['control'].controlId(), value)


    @QtCore.pyqtSlot()
    def enableControls(self):
        self.reenableControls()
        if self._reenableTimerId:
            self.killTimer(self._reenableTimerId)
        self._reenableTimerId = self.startTimer(self.reenableTimeout)


    def timerEvent(self, event):
        if event.timerId() == self._reenableTimerId:
            self.reenableControls()


    def reenableControls(self):
        self.disableControls()
        # lastStateDict = dict(self._lastStateDict)
        for control in self.controls():
            controlId = control.controlId()
            control.setEnabled(controlId, True)
            # if lastStateDict.get(controlId, control.ActiveState) == control.ActiveState:
            control.activate(controlId)




    @QtCore.pyqtSlot()
    def disableControls(self):
        self.controlDisabled.emit(0) #TODO: atronah: думаю, будут проблемы с тем, что сигнал не ожидает, пока выполниться setEnabled


#==========================================================================


def main():
    import sys

    sys.exit(0)


if __name__ == '__main__':
    main()