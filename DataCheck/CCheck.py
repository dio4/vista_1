# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Events.EditDispatcher import getEventFormClassByType


class CCheck:
    def __init__(self):
        self.abort = False
        self.checkRun = False
        self.progressBar.setFormat('%v')
        self.progressBar.setValue(0)
        self.rows = 0
        self.err_str = u''
        self.items = {}

    @QtCore.pyqtSlot()
    def on_btnClose_clicked(self):
        if self.checkRun:
            self.abort = True
        else:
            self.close()

    @QtCore.pyqtSlot()
    def on_btnStart_clicked(self):
        self.btnStart.setEnabled(False)
        self.abort = False
        self.checkRun = True
        try:
            self.check()
        except IOError, e:
            QtGui.qApp.logCurrentException()
            msg = ''
            if hasattr(e, 'filename'):
                msg = u'%s:\n[Errno %s] %s' % (e.filename, e.errno, e.strerror)
            else:
                msg = u'[Errno %s] %s' % (e.errno, e.strerror)
            QtGui.QMessageBox.critical(self, u'Произошла ошибка ввода-вывода', msg, QtGui.QMessageBox.Close)
        except Exception, e:
            QtGui.qApp.logCurrentException()
            QtGui.QMessageBox.critical(self, u'Произошла ошибка', unicode(e), QtGui.QMessageBox.Close)
            self.abort = True
        self.progressBar.setText(u'прервано' if self.abort else u'готово')
        self.btnClose.setText(u'закрыть')
        self.abort = False
        self.checkRun = False

    def check(self):
        raise NotImplementedError

    def getEventFormClass(self, eventTypeId):
        return getEventFormClassByType(eventTypeId)

    def err2log(self, e):
        self.log.addItem(self.err_str + e)
        self.items[self.rows] = self.itemId
        item = self.log.item(self.rows)
        self.log.scrollToItem(item)
        self.rows += 1
        self.item_bad = True

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_log_doubleClicked(self, index):
        row = self.log.currentRow()
        item = self.items[row]
        if item:
            dlg = self.openItem(item)
            if dlg:
                dlg.exec_()

    def openItem(self, itemId):
        raise NotImplementedError
