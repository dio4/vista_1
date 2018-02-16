#!/usr/bin/env python
# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from HospitalBeds.Ui_ProcessingReferralWindow import Ui_ProcessingReferralWindow
from library.DialogBase import CDialogBase


class CProcessingReferralWindow(CDialogBase, Ui_ProcessingReferralWindow):
    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.parent = parent

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        code = self.buttonBox.standardButton(button)
        if code == QtGui.QDialogButtonBox.Ok:
            if len(self.edtStatus.text()) == 0:
                QtGui.QMessageBox.information(
                    self,
                    u"Обработака направления",
                    u"Вы не указали статус. Изменение данных не произошло.",
                    QtGui.QMessageBox.Ok,
                    QtGui.QMessageBox.Ok
                )
