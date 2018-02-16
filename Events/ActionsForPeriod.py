# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013-2014 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore
from Ui_ActionsForPeriod import Ui_ActionsForPeriod

# Диалог задания параметров периодических мероприятий
class CActionsForPeriodDialog(QtGui.QDialog, Ui_ActionsForPeriod):
    def __init__(self, parent, minBegPeriod, maxEndPeriod):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        if minBegPeriod:
            self.edtPeriodBegDate.setMinimumDate(minBegPeriod.date())
            self.edtPeriodEndDate.setMinimumDate(minBegPeriod.date())
        if maxEndPeriod:
            self.edtPeriodEndDate.setMaximumDate(maxEndPeriod.date())

    def periodParameters(self):
        begDate = self.edtPeriodBegDate.date()
        if self.chkFillType.isChecked():
            endDate = QtCore.QDate()
            amount = self.etdAmount.value()
        else:
            endDate = self.edtPeriodEndDate.date()
            amount = 0
        duration = self.edtDuration.value()
        interval = self.edtInterval.value()
        weekend = self.chkWeekend.isChecked()


        return begDate, endDate, duration, interval, amount, weekend
