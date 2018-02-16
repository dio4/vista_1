# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore

from library.TableView import CTableView


class CExecutionPlanTableView(CTableView):
    def __init__(self, parent):
        CTableView.__init__(self, parent)


    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Space:
            QtCore.QObject.parent(self).on_btnEdit_clicked()
        else:
            CTableView.keyPressEvent(self, event)
