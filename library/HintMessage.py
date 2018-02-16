# -*- coding: utf-8 -*-
import thread
from PyQt4 import QtGui, QtCore
from Ui_HintMessage import Ui_MessageWindow
import threading


def showErrorHint(title, text):
    u"""методы для работы с сообщениями"""
    thread.start_new_thread(CHintMessage, (title, text, u'255, 102, 102'))


def showWarningHint(title, text):
    thread.start_new_thread(CHintMessage, (title, text, u'255, 255, 153'))


def showDefaultHint(title, text):
    thread.start_new_thread(CHintMessage, (title, text))


class CHintMessage(QtGui.QDialog, Ui_MessageWindow):
    u"""основной класс для вывода сообщения"""
    def __init__(self, title, text, color=None, parent=None):
        super(CHintMessage, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.lblTitle.setText(title)
        self.lblMessage.setText(text)
        if color:
            self.setStyleSheet(u'background-color: rgb(%s); font: 75 italic 12pt "MS Shell Dlg 2";' % color)
        else:
            self.setStyleSheet(u'background-color: rgb(102, 255, 102); font: 75 italic bold 12pt "MS Shell Dlg 2";')
        self.lblMessage.setStyleSheet(u'font: 75 italic 10pt "MS Shell Dlg 2";')
        screen = QtGui.QDesktopWidget().screenGeometry()
        margineX = 20
        margineY = 50
        self.resize(QtCore.QSize(screen.width() / 6, self.geometry().height()))
        size = self.geometry()
        self.move(screen.width()-size.width()-margineX, screen.height()-size.height()-margineY)
        t = threading.Timer(5.0, self.closeWindow)
        t.start()
        self.show()
        self.exec_()

    def closeWindow(self):
        self.close()
