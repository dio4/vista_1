# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtGui

class CTabBar(QtGui.QTabBar):
    def __init__(self, parent=None):
        QtGui.QTabBar.__init__(self, parent)