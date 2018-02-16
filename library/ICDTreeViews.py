#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4.QtGui import *
from library.TableView import *
from library.InDocTable import CInDocTableView


class CICDTreeView(QTreeView):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            event.accept()
            self.emit(QtCore.SIGNAL('doubleClicked(QModelIndex)'), self.currentIndex())
        elif event.key() == Qt.Key_Space:
            event.accept()
            self.emit(QtCore.SIGNAL('hide()'))
        else:
            QTreeView.keyPressEvent(self, event)

#    def toolTip(self):
#        return 'hello!'


class CICDSearchResult(CInDocTableView):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            event.accept()
            self.emit(QtCore.SIGNAL('doubleClicked(QModelIndex)'), self.currentIndex())
        elif event.key() == Qt.Key_Space:
            event.accept()
            self.emit(QtCore.SIGNAL('hide()'))
        else:
            CInDocTableView.keyPressEvent(self, event)