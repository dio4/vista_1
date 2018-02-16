# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore

from library.InDocTable import CInDocTableView


class CWorkHurtTableView(CInDocTableView):
    def keyPressEvent(self, event):
        key = event.key()
        text = unicode(event.text())
        if event.key() == QtCore.Qt.Key_Tab :
            index = self.currentIndex()
            model = self.model()
            if index.column() == model.columnCount()-1 :
                self.parent().focusNextChild()
                event.accept()
                return
        elif event.key() == QtCore.Qt.Key_Backtab :
            index = self.currentIndex()
            if index.column() == 0 :
                self.parent().focusPreviousChild()
                event.accept()
                return
        CInDocTableView.keyPressEvent(self, event)