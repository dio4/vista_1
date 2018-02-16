# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################


"""
editor of preferences of application output
"""

from PyQt4 import QtGui, QtCore

from Ui_decor import Ui_decorDialog


class CDecorDialog(QtGui.QDialog, Ui_decorDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        styles = list(QtGui.QStyleFactory.keys())
        try:
            styles.remove('GTK+')
        except ValueError:
            pass
        try:
            styles.remove('Cleanlooks')
        except ValueError:
            pass
        self.cmbStyle.insertItems(0, styles)


    def setStyle(self, style):
        index = self.cmbStyle.findText(style, QtCore.Qt.MatchFixedString)
        if index < 0:
            index = 0
        self.cmbStyle.setCurrentIndex(index)


    def setStandardPalette(self, standardPalette):
        self.chkStandartPalette.setChecked(standardPalette)


    def setMaximizeMainWindow(self, maximizeMainWindow):
        self.chkMaximizeMainWindow.setChecked(maximizeMainWindow)


    def setFullScreenMainWindow(self, fullScreenMainWindow):
        self.chkFullScreenMainWindow.setChecked(fullScreenMainWindow)
        
    def setFontSize(self, fontSize):
        self.sbFontSize.setValue(fontSize)    
        
    def setFontFamily(self, fontFamily):
        self.cmbFontName.setCurrentFont(QtGui.QFont(fontFamily))

    def set_crb_width_unlimited(self, unlimited):
        self.chkCRBWidthUnlimited.setChecked(bool(unlimited))

    def style(self):
        return str(self.cmbStyle.currentText())


    def standardPalette(self):
        return self.chkStandartPalette.isChecked()


    def maximizeMainWindow(self):
        return self.chkMaximizeMainWindow.isChecked()


    def fullScreenMainWindow(self):
        return self.chkFullScreenMainWindow.isChecked()
    
    def fontSize(self):
        return self.sbFontSize.value()
    
    def fontFamily(self):
        return self.cmbFontName.currentFont().family()

    def crb_width_unlimited(self):
        return self.chkCRBWidthUnlimited.isChecked()
