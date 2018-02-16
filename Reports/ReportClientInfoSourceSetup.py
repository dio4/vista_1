# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Reports.Ui_ReportClientInfoSourceSetup import Ui_ReportClientInfoSourceSetup
from library.Utils import getVal


class CReportClientInfoSourceSetup(QtGui.QDialog, Ui_ReportClientInfoSourceSetup):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.lstSource.setTable('rbInfoSource')

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(getVal(params, 'begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(getVal(params, 'endDate', QtCore.QDate.currentDate()))
        # self.chkDocDoc.setChecked(getVal(params, 'docDoc', 0))
        # self.chkMend.setChecked(getVal(params, 'onMend', 0))
        self.chkManyEvents.setChecked(getVal(params, 'manyEvents', 0))
        self.lstSource.setValues(getVal(params, 'lstSource', []))

    def params(self):
        result = dict()
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        # result['docDoc'] = self.chkDocDoc.isChecked()
        # result['onMend'] = self.chkMend.isChecked()
        result['manyEvents'] = self.chkManyEvents.isChecked()
        result['lstSource'] = self.lstSource.nameValues().keys()
        return result
