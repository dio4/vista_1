# -*- coding: utf-8 -*-


from PyQt4 import QtGui, QtCore
from Ui_RBCancellationReasonList import Ui_CancellationReasonDialog


class CRBCancellationReasonList(QtGui.QDialog, Ui_CancellationReasonDialog):
    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbReason.setTable('rbCancellationReason', False)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        pass


    def params(self):
        return self.cmbReason.value()