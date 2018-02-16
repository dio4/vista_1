# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui

from Ui_HospitalBedEditor import Ui_HospitalBedEditor


class CHospitalBedEditorDialog(QtGui.QDialog, Ui_HospitalBedEditor):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)


    def values(self):
        return self.cmbHospitalBed.value()

