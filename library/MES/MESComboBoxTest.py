#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from library.Utils import *
from library.DialogBase import CDialogBase

from Ui_MESComboBoxTest import Ui_TestDialog

def testMESComboBox():
    dialog = CMESComboBoxTestDialog()
    dialog.exec_()


class CMESComboBoxTestDialog(CDialogBase, Ui_TestDialog):
    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.cmbEventProfile.setTable('rbEventProfile', True)
        self.cmbSpeciality.setTable('rbSpeciality', True)


    @QtCore.pyqtSlot(int)
    def on_edtAge_valueChanged(self, age):
        def fakeAgeTuple(age):
            return (age*365,
                    age*365/7,
                    age*12,
                    age
                   )

        self.cmbMES.setClientAge(fakeAgeTuple(age))


    @QtCore.pyqtSlot(int)
    def on_cmbSex_currentIndexChanged(self, sex):
        self.cmbMES.setClientSex(sex)


    @QtCore.pyqtSlot(int)
    def on_cmbEventProfile_currentIndexChanged(self, sex):
        self.cmbMES.setEventProfile(self.cmbEventProfile.value())


    @QtCore.pyqtSlot(QString)
    def on_edtMESCodeTemplate_textChanged(self, text):
        self.cmbMES.setMESCodeTemplate(forceStringEx(text))


    @QtCore.pyqtSlot(QString)
    def on_edtMESNameTemplate_textChanged(self, text):
        self.cmbMES.setMESNameTemplate(forceStringEx(text))


    @QtCore.pyqtSlot(int)
    def on_cmbSpeciality_currentIndexChanged(self, sex):
        self.cmbMES.setSpeciality(self.cmbSpeciality.value())


    @QtCore.pyqtSlot(QString)
    def on_edtMKB_textChanged(self, text):
        self.cmbMES.setMKB(forceStringEx(text))