#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4.QtGui import *

class CTextBrowser(QTextBrowser):
    def __init__(self, parent=None):
        QTextBrowser.__init__(self, parent)
        self.actions = []


    def contextMenuEvent(self, event):
        stdMenu = self.createStandardContextMenu()
        if self.actions:
            menu = QMenu(self)
            for action in self.actions:
                menu.addAction(action)
            menu.addSeparator()
            for action in stdMenu.actions():
                menu.addAction(action)
        else:
            menu = stdMenu
        menu.exec_(event.globalPos())