#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui


class CProgressBar(QtGui.QProgressBar):
    def __init__(self, *args, **kwargs):
        super(CProgressBar, self).__init__(*args, **kwargs)
        self._stateFormat = '%v'


    def setProgressFormat(self, newFormat):
        self._stateFormat = newFormat


    @QtCore.pyqtSlot(int)
    def step(self, val=1):
        self.setValue( self.value()+val )


    def reset(self):
        self.setFormat(self._stateFormat)
        super(CProgressBar, self).reset()


    def setText(self, msg):
        self.setFormat(msg)
        self.update()


    @QtCore.pyqtSlot(QtCore.QString)
    def setDescription(self, description):
        self.setFormat(u'%s %s' % (description, self._stateFormat))


    @QtCore.pyqtSlot(int, int, QtCore.QString)
    def setProgress(self, current, total, description):
        self.setValue(current)
        self.setMaximum(total)
        self.setDescription(description)
