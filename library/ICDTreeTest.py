#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from library.DialogBase import CDialogBase

from Ui_ICDTreeTest import Ui_TestDialog


def testICDTree():
    dialog = CICDTreeTestDialog()
    dialog.exec_()


class CICDTreeTestDialog(CDialogBase, Ui_TestDialog):
    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)

