#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtGui
from PyQt4.QtCore import *


class CApplyResetDialogButtonBox(QtGui.QDialogButtonBox):
#    __pyqtSignals__ = ('apply()',
#                       'reset()',
#                      )


    def __init__(self, *args):
        QtGui.QDialogButtonBox.__init__(self, *args)
        self.returnShortcut = QtGui.QShortcut(QtGui.QKeySequence(Qt.Key_Return), self)
        self.enterShortcut = QtGui.QShortcut(QtGui.QKeySequence(Qt.Key_Enter), self)
        self.resetShortcut = QtGui.QShortcut(QtGui.QKeySequence(Qt.Key_Clear), self)
        self.connect(self.returnShortcut, SIGNAL('activated()'), self.apply)
        self.connect(self.enterShortcut, SIGNAL('activated()'), self.apply)
        self.connect(self.resetShortcut, SIGNAL('activated()'), self.reset)


    def apply(self):
        button = self.button(QtGui.QDialogButtonBox.Apply)
        if button:
            button.animateClick()
            # self.emit(SIGNAL('apply()'))


    def reset(self):
        button = self.button(QtGui.QDialogButtonBox.Reset)
        if button:
            button.animateClick()
            # self.emit(SIGNAL('reset()'))
