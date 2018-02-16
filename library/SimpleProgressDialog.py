#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtGui
from PyQt4.QtCore import *

from Ui_SimpleProgressDialog import Ui_Dialog


class CSimpleProgressDialog(QtGui.QDialog, Ui_Dialog):
    ReadyToWork = 1
    WorkInProgress = 2
    WorkCanceled = 3
    WorkDone = 4

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.state = None
        self.autoStart = True
        self.autoClose = False
        self.stepIterator = None
        self.canceled = None
        self.buttonBox.setStandardButtons(  QtGui.QDialogButtonBox.Ok
                                          | QtGui.QDialogButtonBox.Cancel
                                          | QtGui.QDialogButtonBox.Abort
                                          | QtGui.QDialogButtonBox.Close
                                         )


    def setState(self, state):
        if self.state != state:
            if state == self.ReadyToWork:
                enabledButtons = (QtGui.QDialogButtonBox.Ok , QtGui.QDialogButtonBox.Cancel)
                self.progressBar.reset()
            elif state == self.WorkInProgress:
                enabledButtons = (QtGui.QDialogButtonBox.Abort, )
                self.progressBar.reset()
            elif state == self.WorkDone:
                enabledButtons = (QtGui.QDialogButtonBox.Close, )
                self.progressBar.setText(u'Готово')
            elif state == self.WorkCanceled:
                enabledButtons = (QtGui.QDialogButtonBox.Close, )
                self.progressBar.setText(u'Прервано')
            else:
                enabledButtons = ()
            # если здесь использовать "setStandardButtons", то
            # очень часто кнопки не успевают перерисоваться, даже если явно указать repaint
            # возможно, что "setStandardButtons" для работы отрабатывает несколько событий,
            # а в нашем случае это может занять много времени.
            for button in self.buttonBox.buttons():
                button.setVisible(self.buttonBox.standardButton(button) in enabledButtons)
            self.state = state
        self.repaint()


    def setStepCount(self, cnt):
        self.progressBar.setMaximum(cnt)


    def setAutoStart(self, value=True):
        self.autoStart = value


    def setAutoClose(self, value=True):
        self.autoClose = value


    def setStepIterator(self, stepIterator):
        self.stepIterator = stepIterator


    def exec_(self):
        self.setState(self.ReadyToWork)
        if self.autoStart:
            QTimer.singleShot(200, self.onStart) # 0.2 sec
        return QtGui.QDialog.exec_(self)


    def onStart(self):
        def work():
            self.progressBar.setValue(0)
            self.canceled = False
            for s in self.stepIterator(self):
                self.progressBar.step(s)
                QtGui.qApp.processEvents()
                if self.canceled:
                    return False
            return True

        self.setState(self.WorkInProgress)
        if self.stepIterator:
            ok, done = QtGui.qApp.call(self, work)
        else:
            ok = done = True
        if ok and done:
            self.setState(self.WorkDone)
            self.onStop()
        else:
            self.onCancel()


    def onStop(self):
        if self.autoClose:
            QTimer.singleShot(300, self.close) # 0.2 sec


    def onCancel(self):
        self.setState(self.WorkCanceled)
        if self.autoClose:
            QTimer.singleShot(300, self.close) # 0.2 sec


    @pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Ok:
            self.onStart()
        elif buttonCode in (QtGui.QDialogButtonBox.Cancel, QtGui.QDialogButtonBox.Close):
            self.close()
        elif buttonCode == QtGui.QDialogButtonBox.Abort:
            self.canceled = True
