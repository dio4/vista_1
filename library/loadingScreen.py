# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore
from threading import Timer

from library.Ui_LoadingScreen import Ui_LoadScreenForm


class CLoadingScreen(QtGui.QDialog, Ui_LoadScreenForm):
    u"""Основной класс для вывода сообщения"""

    def __init__(self, thread, parent=None):
        super(CLoadingScreen, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setStyleSheet(u'background-color: rgb(224, 224, 224);')
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) * 0.5, (screen.height() - size.height()) * 0.5)
        t = Timer(0.3, self.joinThread, [thread])
        t.start()
        self.show()
        self.exec_()

    def joinThread(self, thread):
        thread.join()
        self.close()
