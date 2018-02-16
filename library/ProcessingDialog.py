#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore
from threading import Timer

from PyQt4.QtCore import QThread

from Ui_LoadingScreen import Ui_LoadScreenForm


class CProcessingDialog(QtGui.QDialog, Ui_LoadScreenForm):
    u"""
    Окно выполнения вычислений.
    Запускается окно с текстом, помещенным self.lblLoading, для того, чтобы информировать пользователя о выполнеии
    каких-либо действий.

    Данный класс позволяет запустить вычисления, которые могут быть прерваны по таймеру (см. self.isTerminated).
    """
    WAIT_TIME = 0
    TIMER_TIME = 0.2
    isTerminated = False

    class ProcessingThread(QThread):
        def __init__(self, func, *args):
            QThread.__init__(self)
            self._func = func
            self._args = args

        def __del__(self):
            self.wait()

        def run(self):
            self._func(*self._args)

    def __init__(self, func, args=(), parent=None, waitTime=None):
        super(CProcessingDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setStyleSheet(u'background-color: rgb(224, 224, 224);')
        if parent:
            screen = parent.geometry()
            size = self.geometry()
            self.move((parent.width() - size.width()) * 0.5, (screen.height() - size.height()) * 0.5)
        else:
            screen = QtGui.QDesktopWidget().screenGeometry()
            size = self.geometry()
            self.move((screen.width() - size.width()) * 0.5, (screen.height() - size.height()) * 0.5)
        self.lblLoading.setText(u"Выполняется операция. Пожалуйста подождите...")

        self.WAIT_TIME = waitTime

        self._thread = CProcessingDialog.ProcessingThread(func, *args)
        self._thread.start()

        self._timer = Timer(self.TIMER_TIME, self._joinThread)
        self._timer.start()

        self.show()

    def _joinThread(self):
        if self._thread.isRunning():
            if self.WAIT_TIME:
                self._thread.wait(self.WAIT_TIME * 1000)
            else:
                self._thread.wait()

        if self._thread.isRunning():
            self._thread.terminate()
            self.isTerminated = True

        self.close()


if __name__ == '__main__':
    def slowFunc(a, b):
        import time
        time.sleep(0)
        print "THREAD ARE FINISHED!"
        print ">> " + a + " " + b


    import sys

    app = QtGui.QApplication(sys.argv)

    print "START\n"

    dialog = CProcessingDialog(slowFunc, ("a", "iop"), waitTime=4)
    dialog.exec_()

    print "\nSTOP"

    sys.exit()
