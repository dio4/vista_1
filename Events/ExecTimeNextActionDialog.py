# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

from library.DialogBase          import CConstructHelperMixin

from Ui_ExecTimeNextActionDialog import Ui_ExecTimeNextActionDialog


class CExecTimeNextActionDialog(QtGui.QDialog, CConstructHelperMixin, Ui_ExecTimeNextActionDialog):
    def __init__(self, parent, begDateTime, execPersonId):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbPerson.setValue(execPersonId)
        self.begDateTime = begDateTime
        self.begTime = self.begDateTime.time()
        self.edtExecTimeNew.setMinimumTime(self.begTime)
        self.btnExecTimeOld.setText(self.begTime.toString('hh:mm'))
        currentDateTime = QtCore.QDateTime.currentDateTime()
        self.execTime = currentDateTime.time()
        self.edtExecTimeNew.setTime(self.execTime if self.begTime <= self.execTime else self.begTime)
        self.connect(self.buttonBox, QtCore.SIGNAL('accepted()'), self.accept)


    @QtCore.pyqtSlot()
    def on_btnExecTimeOld_clicked(self):
        self.setExecTime(self.begTime)
        QtCore.QDialog.accept(self)


    def accept(self):
        self.setExecTime(self.edtExecTimeNew.time())
        QtCore.QDialog.accept(self)


    def getExecTime(self):
        return self.execTime


    def getExecPersonId(self):
        return self.cmbPerson.value()


    def setExecTime(self, execTime):
        self.execTime = execTime

