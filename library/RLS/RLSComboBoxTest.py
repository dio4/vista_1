#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from library.DialogBase import CDialogBase

from library.RLS.ui.Ui_RLSComboBoxTest import Ui_TestDialog


def testRLSComboBox():
    dialog = CRLSComboBoxTestDialog()
    dialog.exec_()


class CRLSComboBoxTestDialog(CDialogBase, Ui_TestDialog):
    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)

