# -*- coding: utf-8 -*-

"""
Module implementing LicDlg.
"""

from PyQt4 import QtGui
from PyQt4.QtGui import QDialog

from Ui_s11License import Ui_Dialog

class CLicDlg(QDialog, Ui_Dialog):
    """
    Class documentation goes here.
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.companyName.setText(QtGui.qApp.preferences.compName)
        self.productCode.setText(QtGui.qApp.preferences.licNumber)
        self.installCode.setText(QtGui.qApp.preferences.instNumber)
        self.activationCode.setText(QtGui.qApp.preferences.actNumber)
