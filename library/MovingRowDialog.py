# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtGui

from library.Ui_MovingRowDialog import Ui_MovingRowDialog


class CMovingRowDialog(QtGui.QDialog, Ui_MovingRowDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setLabelName(self, name):
        self.lblAction.setText((u'%s' % self.lblAction.text()) % name)
