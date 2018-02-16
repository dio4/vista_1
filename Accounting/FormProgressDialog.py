# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from Ui_FormProgressDialog import Ui_FormProgressDialog

class CFormProgressCanceled(StopIteration):
    pass


class CFormProgressDialog(QtGui.QDialog, Ui_FormProgressDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.lblContract.setText('')
        self.prbContracts.setMaximum(0)
        self.prbContracts.setValue(0)
        self.prbContract.setMaximum(0)
        self.prbContract.setValue(0)
        self.canceled = False


    def setNumContracts(self, num):
        self.prbContracts.setValue(0)
        self.prbContracts.setMaximum(num)


    def setContractName(self, contractName):
        self.lblContract.setText(contractName)
        self.prbContracts.setValue(self.prbContracts.value()+1)
###        self.prbContracts.setText(contractName)


    def setNumContractSteps(self, numSteps):
        self.prbContract.setValue(0)
        self.prbContract.setMaximum(numSteps)

    def step(self):
        if self.canceled:
            raise CFormProgressCanceled()
        self.prbContract.setValue(self.prbContract.value()+1)
        QtGui.qApp.processEvents()

    @QtCore.pyqtSlot()
    def on_btnBreak_clicked(self):
        self.canceled = True


class CContractFormProgressDialog(CFormProgressDialog):
    def setContractName(self, contractName):
        self.lblContract.setText(contractName)
