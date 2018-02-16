# -*- coding: utf-8 -*-
# ############################################################################
##
## Copyright (C) 2014 Vista Software. All rights reserved.
##
#############################################################################
import time

__author__ = 'atronah'

'''
    author: atronah
    date:   13.10.2014
    reason: To generate eq commands (such as 'next', 'prev', 'recall' ant other)
'''

from PyQt4 import QtCore
from PyQt4 import QtGui
isNetworkImport = True
try:
    from PyQt4 import QtNetwork
except:
    isNetworkImport = False

from library.ElectronicQueue.Ui_EQControlWidget import Ui_EQControlWidget

# import time #DEBUG: atronah:

class CAbstractEQControl(QtCore.QObject):
    ID_AUTOINCREMENT = 0

    class ControlButtonsState:
        AllDiasabled = 0
        PrevEnabled = 1
        ReCallEnabled = 2
        NextEnabled = 4
        StartEnabled = 8
        StopEnabled = 16
        AllEnabled = PrevEnabled | ReCallEnabled | NextEnabled | StartEnabled | StopEnabled

    calledNext = QtCore.pyqtSignal(int, bool) # (controlId, isCurrentComplete)
    calledPrev = QtCore.pyqtSignal(int, bool) # (controlId, isCurrentComplete)
    reCalled = QtCore.pyqtSignal(int) # (controlId)
    calledCustom = QtCore.pyqtSignal(int, bool, QtCore.QString) # (controlId, isCurrentComplete, value)
    # stopped = QtCore.pyqtSignal(int) # (controlId)
    # started = QtCore.pyqtSignal(int) # (controlId)
    openedSettings = QtCore.pyqtSignal()

    enabled = QtCore.pyqtSignal(int, bool) #(controlId, isEnabled)


    stateChanged = QtCore.pyqtSignal(int, int) # (controlId, state)
    stateNameChanged = QtCore.pyqtSignal(int, QtCore.QString) # (controlId, stateName)

    EnablingState = 0
    EnabledState = 1
    ActiveState = 2
    DisablingState = 3
    DisabledState = 4
    ErrorState = 5

    stateNames = {
                  EnablingState : u'Включение',
                  EnabledState : u'Включено',
                  ActiveState : u'Активно',
                  DisablingState : u'Выключение',
                  DisabledState : u'Выключено',
                  ErrorState : u'Ошибка'}


    def __init__(self, parent = None):
        super(CAbstractEQControl, self).__init__(parent)
        self._controlId = self._getNewId()
        self._buttonsState = CAbstractEQControl.ControlButtonsState.AllDiasabled
        self._lastErrorText = u'Неизвестная ошибка'
        self._state = self.DisabledState

        self._officeName = u''


    @staticmethod
    def _getNewId():
        CAbstractEQControl.ID_AUTOINCREMENT += 1
        return CAbstractEQControl.ID_AUTOINCREMENT


    def isEnabled(self):
        return self._state in [self.EnabledState, self.ActiveState]


    def isActive(self):
        return self._state in [self.ActiveState]


    def reEnable(self):
        if self.isEnabled():
            self.setDisabled(self._controlId)
            self.setEnabled(self._controlId)


    def applyButtonsState(self, state):
        pass


     #--- interface---
    def controlId(self):
        return self._controlId


    def lastErrorText(self):
        return self._lastErrorText


    def _changeState(self, state):
        self._state = state
        self.stateChanged.emit(self._controlId, state)
        self.stateNameChanged.emit(self._controlId, self.stateName(state))
        if state in [self.EnabledState, self.DisabledState]:
            self.enabled.emit(self._controlId, state == self.EnabledState)


    def stateName(self, state):
        if state in self.stateNames.keys():
            if state == self.ErrorState:
                return u'%s (%s)' % (self.stateNames[state], self.lastErrorText())
            return self.stateNames[state]
        return u'Неизвестное состояние (%s)' % state


    def currentState(self):
        return self._state


    def officeName(self):
        return self._officeName


    def setOfficeName(self, officeName):
        self._officeName = officeName


    #--- slots ---
    @QtCore.pyqtSlot(int)
    def activate(self, controlId = 0):
        if controlId not in [0, self._controlId] :
            return
        if self.isActive():
            return

        if self.isEnabled():
            self._changeState(self.ActiveState)



    @QtCore.pyqtSlot()
    @QtCore.pyqtSlot(int)
    @QtCore.pyqtSlot(int, bool)
    def setEnabled(self, controlId = 0, enabled = True):
        if controlId not in [0, self._controlId]:
            return

        if self.isEnabled() == enabled:
            return

        self.setButtonsState(controlId, self._buttonsState if enabled else CAbstractEQControl.ControlButtonsState.AllDiasabled)
        self._changeState(self.EnabledState if enabled else self.DisabledState)



    @QtCore.pyqtSlot()
    @QtCore.pyqtSlot(int)
    def setDisabled(self, controlId = 0):
        self.setEnabled(controlId, False)


    @QtCore.pyqtSlot()
    def onStartClicked(self):
        # print time.time(), 'start clicked' #debug: atronah:
        self._changeState(CAbstractEQControl.ActiveState)
        # self.started.emit(self._controlId)


    @QtCore.pyqtSlot()
    def onStopClicked(self):
        self._changeState(CAbstractEQControl.EnabledState)
        # self.stopped.emit(self._controlId)


    @QtCore.pyqtSlot(bool)
    def onPrevClicked(self, isCurrentComplete):
        if self._state == self.ActiveState:
            self.calledPrev.emit(self._controlId, isCurrentComplete)


    @QtCore.pyqtSlot()
    def onCompleteAndPrevClicked(self):
        if self._state == self.ActiveState:
            self.onPrevClicked(True)


    @QtCore.pyqtSlot()
    def onCancelAndPrevClicked(self):
        if self._state == self.ActiveState:
            self.onPrevClicked(False)


    @QtCore.pyqtSlot()
    def onReCallClicked(self):
        if self._state == self.ActiveState:
            self.reCalled.emit(self._controlId)


    @QtCore.pyqtSlot(bool)
    def onNextClicked(self, isCurrentComplete):
        if self._state == self.ActiveState:
            self.calledNext.emit(self._controlId, isCurrentComplete)


    @QtCore.pyqtSlot()
    def onCompleteAndNextClicked(self):
        if self._state == self.ActiveState:
            self.onNextClicked(True)


    @QtCore.pyqtSlot()
    def onCancelAndNextClicked(self):
        if self._state == self.ActiveState:
            self.onNextClicked(False)


    @QtCore.pyqtSlot(bool, QtCore.QString)
    def onCustomClicked(self, isCurrentComplete, value):
        if self._state == self.ActiveState:
            self.calledCustom.emit(self._controlId, isCurrentComplete, value)


    @QtCore.pyqtSlot(QtCore.QString)
    def onCompleteAndCustomClicked(self, value):
        if self._state == self.ActiveState:
            self.onCustomClicked(True, value)


    @QtCore.pyqtSlot(QtCore.QString)
    def onCancelAndCustomClicked(self, value):
        if self._state == self.ActiveState:
            self.onCustomClicked(False, value)


    @QtCore.pyqtSlot(int, QtCore.QString)
    def changePrevValue(self, controlId, value):
        pass


    @QtCore.pyqtSlot(int, QtCore.QString)
    def changeCurrentValue(self, controlId, value):
        pass


    @QtCore.pyqtSlot(int, QtCore.QString)
    def changeNextValue(self, controlId, value):
        pass


    @QtCore.pyqtSlot(int)
    def handleError(self, errorCode):
        self._changeState(self.ErrorState)
        self.setEnabled(self._controlId, False)

        #TODO: atronah: расписать текст ошибок
        self._lastErrorText = u'Код ошибки: %s' % errorCode


    @QtCore.pyqtSlot(int, int)
    def setButtonsState(self, controlId, state):
        if controlId not in [self._controlId, 0]:
            return

        self._buttonsState = state
        self.applyButtonsState(state)

    @QtCore.pyqtSlot(int, QtCore.QString)
    def changeOfficeName(self, controlId, officeName):
        if controlId not in [self._controlId, 0]:
            return
        self.setOfficeName(officeName)


#==========================================================================


#TODO: atronah: перенести TCP-клиент в отдельный независимый класс.
class CEQRemoteControl(CAbstractEQControl):


    CompleteAndNextMessage = u'PM_NEXT'
    CancelAndNextMessage = u'PM_NO_CLIENT'
    CompleteAndPrevMessage = u''
    CancelAndPrevMessage = u''
    ReCallMessage = u''
    StartMessage = u'PM_OPERATOR_READY'
    StopMessage = u'PM_OPERATOR_NO_READY'

    timeoutBetweenMessage = 0.5 #seconds

    # connectionStateChanged = QtCore.pyqtSignal(int, int, int) # (control_id, state, attemptCount)
    # UnknownState = 0
    # TryingToConnect = 1
    # Connected = 2
    # Disconnected = 3
    # stoppedListen = QtCore.pyqtSignal(int)

    # connectionError = QtCore.pyqtSignal(int, int)

    messageReceived = QtCore.pyqtSignal(int, QtCore.QString) #debug: atronah:



    def __init__(self, host, port, parent = None):
        super(CEQRemoteControl, self).__init__(parent)
        self._host = host
        self._port = port
        self._socket = None
        if isNetworkImport:
            self._socket = QtNetwork.QTcpSocket(self)
            self._socket.error.connect(self.handleConnectionError)
            self._socket.stateChanged.connect(self.onConnectionStateChanged)
            self._socket.readyRead.connect(self.onReadyRead)

        self._maxConnectionAttempts = 5
        self._connectionAttempts = 0
        self._isAlwaysReconnect = False #TODO: atronah: сделать интерфейс для изменения этого значения

        self._activateAfterConnect = False
        self._lastMessageTime = time.time()

        # self.startTimer(1000)#debug: atronah:

    # 
    # def timerEvent(self, QTimerEvent):#debug: atronah:
    #     print self._socket.isValid(), self._socket.state()#debug: atronah:


    def host(self):
        return self._host


    def setHost(self, newHost, reconnect = False):
        self._host = newHost
        if reconnect:
            self.reconnect()



    def port(self):
        return self._port


    def setPort(self, newPort, reconnect = False):
        self._port = newPort
        if reconnect:
            self.reconnect()



    def tryToConnect(self):
        if self._socket:
            self._connectionAttempts += 1
            self._socket.connectToHost(QtCore.QString(self._host),
                                       self._port,
                                       QtCore.QIODevice.ReadOnly)

    #--- slots ---
    @QtCore.pyqtSlot(int)
    def activate(self, controlId = 0):
        if controlId not in [self._controlId, 0]:
            return

        if self.isActive():
            return


        self._activateAfterConnect = True


    @QtCore.pyqtSlot()
    @QtCore.pyqtSlot(int)
    @QtCore.pyqtSlot(int, bool)
    def setEnabled(self, controlId = 0, enabled = True):
        # print controlId, enabled #debug: atronah:
        if controlId not in [0, self._controlId]:
            return

        if not self._socket:
            return

        if not enabled and self._socket.state() == QtNetwork.QAbstractSocket.ConnectingState:
            self._socket.abort()

        if self.isEnabled() == enabled:
            return

        if enabled:
            self.tryToConnect()
        else:
            self._socket.disconnectFromHost()
            if not (self._socket.state() == QtNetwork.QAbstractSocket.UnconnectedState \
                    or self._socket.waitForDisconnected(2000)):
                self.handleError(-1)


    @QtCore.pyqtSlot(QtNetwork.QAbstractSocket.SocketError if isNetworkImport else int)
    def handleConnectionError(self, errorCode):
        if self._isAlwaysReconnect or self._connectionAttempts <= self._maxConnectionAttempts:
            self.tryToConnect()
        else:
            self.handleError(errorCode)


    @QtCore.pyqtSlot(QtNetwork.QAbstractSocket.SocketState if isNetworkImport else int)
    def onConnectionStateChanged(self, state):
        if state == QtNetwork.QAbstractSocket.ConnectedState:
            self.setButtonsState(self._controlId, self._buttonsState)
            self._changeState(self.EnabledState)
            self._connectionAttempts = 0
            self._socket.setSocketOption(self._socket.KeepAliveOption, QtCore.QVariant(1))
            if self._activateAfterConnect:
                super(CEQRemoteControl, self).activate()
                self._activateAfterConnect = False
        else:
            self.setButtonsState(self._controlId, self.ControlButtonsState.AllDiasabled)
            if state in [QtNetwork.QAbstractSocket.UnconnectedState, QtNetwork.QAbstractSocket.ClosingState]:
                self._changeState(self.DisabledState)
            elif state in [QtNetwork.QAbstractSocket.HostLookupState, QtNetwork.QAbstractSocket.ConnectingState]:
                self._changeState(self.EnablingState)
            else:
                self.handleError(-1)


    @QtCore.pyqtSlot()
    def onReadyRead(self):
        if self._socket and self._state in [self.EnabledState, self.ActiveState]:
            message = unicode(self._socket.read(1024))
            if abs(time.time() - self._lastMessageTime) <= self.timeoutBetweenMessage:
                message = u''
            self._lastMessageTime = time.time()
            if message:
                if message.startswith(self.CompleteAndNextMessage):
                    self.onCompleteAndNextClicked()
                elif message.startswith(self.CancelAndNextMessage):
                    self.onCancelAndNextClicked()
                elif message.startswith(self.CompleteAndPrevMessage):
                    self.onCompleteAndPrevClicked()
                elif message.startswith(self.CancelAndPrevMessage):
                    self.onCancelAndPrevClicked()
                elif message.startswith(self.ReCallMessage):
                    self.onReCallClicked()
                elif message.startswith(self.StopMessage):
                    self.onStopClicked()
                elif message.startswith(self.StartMessage):
                    self.onStartClicked()

                self.messageReceived.emit(self._controlId, QtCore.QString(message)) #debug: atronah:


#==========================================================================

class CEQGuiControl(CAbstractEQControl):
    def __init__(self, parent = None):
        super(CEQGuiControl, self).__init__(parent)
        self._widgetList = []


    def appendWidget(self, widget):
        if isinstance(widget, CEQControlWidget) and widget not in self._widgetList:
            self._widgetList.append(widget)
            widget.started.connect(self.onStartClicked)
            widget.calledPrev.connect(self.onPrevClicked)
            widget.reCalled.connect(self.onReCallClicked)
            widget.calledNext.connect(self.onNextClicked)
            widget.calledCustom.connect(self.onCustomClicked)
            widget.stopped.connect(self.onStopClicked)
            widget.openedSettings.connect(self.openedSettings)
            widget.setOfficeName(self.officeName())

            widget.destroyed.connect(self.removeWidget)
            self.setEnabled(self._controlId, True)
            return True
        return False


    def widgetList(self):
        return self._widgetList
    
    
    def setOfficeName(self, officeName):
        super(CEQGuiControl, self).setOfficeName(officeName)
        for widget in self._widgetList:
            widget.setOfficeName(officeName)


    @QtCore.pyqtSlot(QtCore.QObject)
    def removeWidget(self, widget):
        if isinstance(widget, QtGui.QWidget):
            if widget in self._widgetList:
                self._widgetList.remove(widget)
            widget.started.disconnect(self.onStartClicked)
            widget.stopped.disconnect(self.onStopClicked)

            widget.calledPrev.disconnect(self.onPrevClicked)
            widget.reCalled.disconnect(self.onReCallClicked)
            widget.calledNext.disconnect(self.onNextClicked)
            widget.calledCustom.disconnect(self.onCustomClicked)

            widget.openedSettings.disconnect(self.openedSettings)

        if not self._widgetList:
            self.setEnabled(self._controlId, False)


    def _changeState(self, state):
        # Запрет на состояния, отличные от "включено" и "активно", если есть хотя бы одна подключенная кнопка.
        if self._widgetList and state not in [self.ActiveState, self.EnabledState]:
            state = self.EnabledState
        super(CEQGuiControl, self)._changeState(state)


    @QtCore.pyqtSlot()
    def applyButtonsState(self, state):
        for widget in self._widgetList:
            widget.setButtonsState(state)


    @QtCore.pyqtSlot(int, QtCore.QString)
    def changePrevValue(self, controlId, value):
        for widget in self._widgetList:
            widget.changePrev(value)


    @QtCore.pyqtSlot(int, QtCore.QString)
    def changeCurrentValue(self, controlId, value):
        if controlId and self._controlId != controlId:
            return
        for widget in self._widgetList:
            widget.changeCurrent(value)


    @QtCore.pyqtSlot(int, QtCore.QString)
    def changeNextValue(self, controlId, value):
        if controlId and self._controlId != controlId:
            return
        for widget in self._widgetList:
            widget.changeNext(value)



#==========================================================================


class CEQControlWidget(QtGui.QWidget, Ui_EQControlWidget):
    calledNext = QtCore.pyqtSignal(bool)
    calledPrev = QtCore.pyqtSignal(bool)
    reCalled = QtCore.pyqtSignal()
    calledCustom = QtCore.pyqtSignal(bool, QtCore.QString)
    stopped = QtCore.pyqtSignal()
    started = QtCore.pyqtSignal()
    openedSettings = QtCore.pyqtSignal()

    EMPTY_VALUE = QtCore.QString(u'---')


    def __init__(self, parent = None):
        super(CEQControlWidget, self).__init__(parent)

        self._nextValue = self.EMPTY_VALUE
        self._isNextEnabled = True

        self.setupUi(self)
        self.edtNext.setText(self.EMPTY_VALUE)
        self.updateIcons()

        self.connectSlots()

        self.setButtonsState()


    def setOfficeName(self, officeName):
        self.lblOffice.setText(officeName)


    def updateIcons(self):
        iconSize = self.btnCompleteAndNext.iconSize()
        iconSize.setWidth(iconSize.width() * 2)
        pComplete = QtGui.QPixmap(u':/new/prefix1/icons/eq/clientComplete.png').scaledToHeight(iconSize.height(), QtCore.Qt.SmoothTransformation)
        pCancel = QtGui.QPixmap(u':/new/prefix1/icons/eq/clientNotAvailable.png').scaledToHeight(iconSize.height(), QtCore.Qt.SmoothTransformation)
        pNext = QtGui.QPixmap(u':/new/prefix1/icons/eq/next.png').scaledToHeight(iconSize.height(), QtCore.Qt.SmoothTransformation)

        alphaBitmap = QtGui.QBitmap(iconSize)
        alphaBitmap.clear()

        pCompleteAndNext = QtGui.QPixmap(iconSize)
        pCompleteAndNext.setMask(alphaBitmap)
        pnt = QtGui.QPainter(pCompleteAndNext)
        pnt.drawPixmap(0, 0, pComplete)
        pnt.drawPixmap(pComplete.width(), 0, pNext)
        pnt.end()
        self.btnCompleteAndNext.setIconSize(iconSize)
        self.btnCompleteAndNext.setIcon(QtGui.QIcon(pCompleteAndNext))

        pCancelAndNext = QtGui.QPixmap(iconSize)
        pCancelAndNext.setMask(alphaBitmap)
        pnt = QtGui.QPainter(pCancelAndNext)
        pnt.drawPixmap(0, 0, pCancel)
        pnt.drawPixmap(pCancel.width(), 0, pNext)
        pnt.end()
        self.btnCancelAndNext.setIconSize(iconSize)
        self.btnCancelAndNext.setIcon(QtGui.QIcon(pCancelAndNext))



    def connectSlots(self):
        self.btnMisc.clicked.connect(self.onMiscToggled)
        self.btnSettings.clicked.connect(self.openedSettings)

        self.btnStart.clicked.connect(self.started)
        self.btnStop.clicked.connect(self.stopped)

        self.btnPrev.clicked.connect(self.calledPrev)
        self.btnRecall.clicked.connect(self.reCalled)
        self.btnCompleteAndNext.clicked.connect(self.onCompleteAndNextCalled)
        self.btnCancelAndNext.clicked.connect(self.onCancelAndNextCalled)

        self.edtNext.textEdited.connect(self.onNextValueEdited)



    #--- slots ---
    @QtCore.pyqtSlot(int)
    def setButtonsState(self, state = CAbstractEQControl.ControlButtonsState.AllDiasabled):
        self.btnPrev.setEnabled(bool(state & CAbstractEQControl.ControlButtonsState.PrevEnabled))

        self._isNextEnabled = bool(state & CAbstractEQControl.ControlButtonsState.NextEnabled)
        # if self._isNextEnabled: print time.time(), 'enabled next button' #debug: atronah:
        self.btnCompleteAndNext.setEnabled(bool(self._isNextEnabled))
        self.btnCancelAndNext.setEnabled(bool(self._isNextEnabled))
        self.edtNext.setEnabled(state != CAbstractEQControl.ControlButtonsState.AllDiasabled)
        if self.edtNext.isEnabled():
            self.onNextValueEdited(self.edtNext.text())

        self.btnRecall.setEnabled(bool(state & CAbstractEQControl.ControlButtonsState.ReCallEnabled))

        self.btnStop.setEnabled(bool(state & CAbstractEQControl.ControlButtonsState.StopEnabled))
        self.btnStart.setEnabled(bool(state & CAbstractEQControl.ControlButtonsState.StartEnabled))


    def setOpenSettingsEnabled(self, enabled):
        self.btnSettings.setEnabled(enabled)


    @QtCore.pyqtSlot(QtCore.QString)
    def changeNext(self, newText):
        self.edtNext.setText(newText if newText else self.EMPTY_VALUE)
        self._nextValue = self.edtNext.text()


    @QtCore.pyqtSlot(QtCore.QString)
    def onNextValueEdited(self, newText):
        #TODO: atronah: разобраться, как быть с последним человеком (next = '---', но текущего надо либо отменить, либо успешно завершить)
        # if newText.startsWith(u'-'):
        #     self.btnCompleteAndNext.setEnabled(False)
        #     self.btnCancelAndNext.setEnabled(False)
        # else:
        self.btnCompleteAndNext.setEnabled(True if newText != self._nextValue else self._isNextEnabled)
        self.btnCancelAndNext.setEnabled(True if newText != self._nextValue else self._isNextEnabled)


    @QtCore.pyqtSlot(QtCore.QString)
    def changePrev(self, newText):
        self.edtPrev.setText(newText)


    @QtCore.pyqtSlot(QtCore.QString)
    def changeCurrent(self, newText):
        self.btnRecall.setText(newText)


    def callNext(self, isCurrentComplete):
        nextValue = self.edtNext.text()
        if nextValue.isEmpty():
            nextValue = self.EMPTY_VALUE
        if nextValue == self._nextValue:
            self.calledNext.emit(isCurrentComplete)
        else:
            self.calledCustom.emit(isCurrentComplete, nextValue)


    @QtCore.pyqtSlot()
    def onCompleteAndNextCalled(self):
        self.callNext(True)


    def onCancelAndNextCalled(self):
        self.callNext(False)


    @QtCore.pyqtSlot(bool)
    def onMiscToggled(self, checked):
        self.stackedWidget.setCurrentIndex(1 if checked else 0)

#==========================================================================





class CTestRemoteControl(QtGui.QWidget):
    startedWork = QtCore.pyqtSignal()
    stoppedWork = QtCore.pyqtSignal()

    def __init__(self, parent = None):
        super(CTestRemoteControl, self).__init__(parent)

        self._remoteControl = CEQRemoteControl(u'192.168.0.209', 4001)
        self._remoteControl.messageReceived.connect(self.printMessage, QtCore.Qt.QueuedConnection)

        self._guiControl = CEQGuiControl(self)
        self._guiControl.setButtonsState(0, CAbstractEQControl.ControlButtonsState.AllEnabled)

        self.setupUi()

        for control in [self._guiControl, self._remoteControl]:
            self.startedWork.connect(control.setEnabled)
            self.stoppedWork.connect(control.setDisabled)

            control.stateNameChanged.connect(self.onControlStateNameChanged, QtCore.Qt.QueuedConnection)

            control.calledNext.connect(self.onCalledNext)
            control.calledPrev.connect(self.onCalledPrev)
            control.reCalled.connect(self.onReCalled)
            control.calledCustom.connect(self.onCalledCustom)
            # control.stopped.connect(self.onStopped)
            # control.started.connect(self.onStarted)
            control.openedSettings.connect(self.onOpenedSettings)


    def setupUi(self):
        layout = QtGui.QVBoxLayout()
        self.te = QtGui.QTextEdit()
        layout.addWidget(self.te)
        self.btnStart = QtGui.QPushButton(u'Start')
        self.btnStart.clicked.connect(self.onStartClicked)
        layout.addWidget(self.btnStart)
        self.btnStop = QtGui.QPushButton(u'Stop')
        self.btnStop.clicked.connect(self.onStopClicked)
        layout.addWidget(self.btnStop)
        self.controlWidget = CEQControlWidget(parent = self)
        self.controlWidget.setButtonsState(CAbstractEQControl.ControlButtonsState.AllEnabled)
        self._guiControl.appendWidget(self.controlWidget)
        layout.addWidget(self.controlWidget)

        self.setLayout(layout)


    @QtCore.pyqtSlot(int, int)
    def onControlStateNameChanged(self, controlId, connectiontStateName):
        self.te.append(u'control %s: %s' % (controlId, connectiontStateName))


    @QtCore.pyqtSlot(int, QtCore.QString)
    def printMessage(self, controlId, message):
        self.te.append(u'control %s: %s' % (controlId, message))


    @QtCore.pyqtSlot()
    def onStartClicked(self):
        self.startedWork.emit()


    @QtCore.pyqtSlot()
    def onStopClicked(self):
        self.stoppedWork.emit()


    @QtCore.pyqtSlot(int, bool)
    def onCalledNext(self, controlId, isCurrentComplete):
        self.te.append(u'control %s: called next (%s)' % (controlId, (u'' if isCurrentComplete else u'un') + u'complete'))


    @QtCore.pyqtSlot(int, bool)
    def onCalledPrev(self, controlId, isCurrentComplete):
        self.te.append(u'control %s: called prev (%s)' % (controlId, (u'' if isCurrentComplete else u'un') + u'complete'))


    @QtCore.pyqtSlot(int)
    def onReCalled(self, controlId):
        self.te.append(u'control %s: recall' % controlId)


    @QtCore.pyqtSlot(int, bool, QtCore.QString)
    def onCalledCustom(self, controlId, isCurrentComplete, value):
        self.te.append(u'control %s: called custom = %s (%s)' % (controlId, value, (u'' if isCurrentComplete else u'un') + u'complete'))


    @QtCore.pyqtSlot(int)
    def onStarted(self, controlId):
        self.te.append(u'control %s: started' % controlId)

    @QtCore.pyqtSlot(int)
    def onStopped(self, controlId):
        self.te.append(u'control %s: stopped' % controlId)


    @QtCore.pyqtSlot()
    def onOpenedSettings(self):
        self.te.append(u'open settings')


    def closeEvent(self, event):
        self.onStopClicked()
        return super(CTestRemoteControl, self).closeEvent(event)

#==========================================================================

def main():
    import sys
    app = QtGui.QApplication(sys.argv)

    t = CTestRemoteControl()
    t.show()

    sys.exit(app.exec_())



if __name__ == '__main__':
    main()