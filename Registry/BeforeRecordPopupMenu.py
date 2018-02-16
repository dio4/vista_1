# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.TableView import CTableView


class CBeforeRecordPopupMenu(CTableView):
    def addPopupPrintRow(self, parent):
        self._actPrintRow = QtGui.QAction(u'Напечатать направление', self)
        self._actPrintRow.setObjectName('actPrintRow')
        self.connect(self._actPrintRow, QtCore.SIGNAL('triggered()'), parent.printOrderQueueItem)
        self.addPopupAction(self._actPrintRow)