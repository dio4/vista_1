# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtGui, QtCore

from library.PreferencesMixin import CDialogPreferencesMixin, CContainerPreferencesMixin


class CDockWidget(QtGui.QDockWidget, CDialogPreferencesMixin):
    def __init__(self, parent):
        QtGui.QDockWidget.__init__(self, parent)
#        self._sizeHint = QSize()

    def loadPreferences(self, preferences):
        CContainerPreferencesMixin.loadPreferences(self, preferences)
        floating = preferences.get('floating', None)
        if floating and type(floating) == QtCore.QVariant:
            self.setFloating(floating.toBool())
        visible = preferences.get('visible', None)
        if visible and type(visible) == QtCore.QVariant:
            self.setVisible(visible.toBool())
#        self.updateGeometry()

    def savePreferences(self):
        result = CContainerPreferencesMixin.savePreferences(self)
        result['floating'] = QtCore.QVariant(1 if self.isFloating() else 0)
        result['visible'] = QtCore.QVariant(1 if self.isVisible() else 0)
        return result

#    def setVisible(self, visible):
#        if not visible and self.isVisible():
#            self._sizeHint = self.size()
#        QtGui.QDockWidget.setVisible(self, visible)
