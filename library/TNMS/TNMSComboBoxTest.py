#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from library.Utils import *
from library.DialogBase import CDialogBase

from Ui_TNMSComboBoxTest import Ui_TestDialog

def testTNMSComboBox():
    dialog = CTNMSComboBoxTestDialog()
    dialog.exec_()


class CTNMSComboBoxTestDialog(CDialogBase, Ui_TestDialog):
    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.edtString.setText('cT3 cN2 cM0 cS1 pTis pN1 pM1 pS2')


    @QtCore.pyqtSlot(QString)
    def on_edtString_textChanged(self, value):
        self.cmbTNMS.setValue(value)


    @QtCore.pyqtSlot()
    def on_cmbTNMS_editingFinished(self):
        self.edtString.setText(self.cmbTNMS.getValue())

