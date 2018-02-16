#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from PriceListComboBoxPopup    import CPriceListComboBoxPopup
from Registry.Utils                 import codeToTextPriceList


class CPriceListComboBox(QtGui.QComboBox):
    __pyqtSignals__ = ('textChanged(QString)',
                       'textEdited(QString)'
                      )

    def __init__(self, parent = None):
        QtGui.QComboBox.__init__(self, parent)
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self._popup = None
        self.code = None
        self.date = QtCore.QDate.currentDate()
        self.priceListOnly = False


    def showPopup(self):
        if not self._popup:
            self._popup = CPriceListComboBoxPopup(self)
            self.connect(self._popup,QtCore.SIGNAL('PriceListCodeSelected(int)'), self.setValue)
        pos = self.rect().bottomLeft()
        pos2 = self.rect().topLeft()
        pos = self.mapToGlobal(pos)
        pos2 = self.mapToGlobal(pos2)
        size = self._popup.sizeHint()
        width = max(size.width(), self.width())
        size.setWidth(width)
        screen = QtGui.QApplication.desktop().availableGeometry(pos)
        pos.setX( max(min(pos.x(), screen.right()-size.width()), screen.left()) )
        pos.setY( max(min(pos.y(), screen.bottom()-size.height()), screen.top()) )
        self._popup.move(pos)
        self._popup.resize(size)
        self._popup.show()
        self._popup.setDate(self.date)
        self._popup.setPriceListCode(self.code, self.priceListOnly)


    def setPriceListOnly(self, priceListOnly):
        self.priceListOnly = priceListOnly


    def setDate(self, date):
        self.date = date


    def setValue(self, code):
        self.code = code
        self.updateText()


    def value(self):
        return self.code


    def updateText(self):
        self.setEditText(codeToTextPriceList(self.code))


    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Delete:
            self.setValue(None)
            event.accept()
        elif key == QtCore.Qt.Key_Backspace: # BS
            self.setValue(None)
            event.accept()
        else:
            QtGui.QComboBox.keyPressEvent(self, event)
