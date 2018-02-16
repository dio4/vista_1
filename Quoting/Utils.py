# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

from library.Utils import forceString
from library.crbcombobox import CRBPopupView

    
def getValueFromRecords(records, col, func=forceString):
        res = []
        for rec in records:
            res.append(func(rec.value(col)))
        return res


class CQuotaTypeComboBoxPopupView(CRBPopupView):
    def resizeEvent(self, resizeEvent):
        QtGui.QTableView.resizeEvent(self, resizeEvent)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            self.emit(QtCore.SIGNAL('hide()'))
        else:
            CRBPopupView.keyPressEvent(self, event)
