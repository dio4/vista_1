# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtGui

from Ui_ExposeConfirmationDialog import Ui_ExposeConfirmationDialog
from Users.Rights import urAdmin, urEventLock
from library.DialogBase import CDialogBase


class CExposeConfirmationDialog(CDialogBase, Ui_ExposeConfirmationDialog):
    def __init__(self,  parent, message):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.lblMessage.setText(message)
        if QtGui.qApp.currentOrgStructureId():
            self.chkFilterPaymentByOrgStructure.setChecked(QtGui.qApp.filterPaymentByOrgStructure())
            self.chkFilterPaymentByOrgStructure.setEnabled(True)
        else:
            self.chkFilterPaymentByOrgStructure.setChecked(False)
            self.chkFilterPaymentByOrgStructure.setEnabled(False)
        self.chkMesCheck.setChecked(True)
        self.buttonBox.button(QtGui.QDialogButtonBox.Cancel).setDefault(True)
        if not QtGui.qApp.isEventLockEnabled():
            self.chkLock.setVisible(False)
        if not QtGui.qApp.userHasAnyRight((urAdmin, urEventLock)):
            self.chkLock.setEnabled(False)

    def options(self):
        return (
            self.chkFilterPaymentByOrgStructure.isChecked(),
            self.chkReExpose.isChecked(),
            self.chkSeparateReExpose.isChecked(),
            self.chkMesCheck.isChecked(),
            self.chkCalendarDaysLength.isChecked(),
            self.chkShowStats.isChecked(),
            self.chkLock.isChecked(),
            self.chkAcceptNewKSLPForChild.isChecked()
        )
