#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4.QtCore import *
from library.ClientRelationComboBoxPopup import CClientRelationComboBoxPopup
from Registry.Utils import *


class CClientRelationComboBox(QtGui.QComboBox):
    __pyqtSignals__ = ('textChanged(QString)',
                       'textEdited(QString)',
                       'editingFinished()',
                       'returnPressed()',
                       'saveExtraData(QString, QString)'
                      )

    def __init__(self, parent=None, mainClientId=None, regAddressInfo=None, logAddressInfo=None):
        if not regAddressInfo:
            regAddressInfo = {}
        if not logAddressInfo:
            logAddressInfo = {}
        QtGui.QComboBox.__init__(self, parent)
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self._popup=None
        self.mainClientId = mainClientId
        self.clientId = None
        self.regAddressInfo = regAddressInfo
        self.logAddressInfo = logAddressInfo
        self.date = QDate.currentDate()
        self._record = None
        self._freeInput = None


    def showPopup(self):
        if forceString(self._freeInput):
            return
        if not self._popup:
            self._popup = CClientRelationComboBoxPopup(self)
            self.connect(self._popup, SIGNAL('relatedClientIdSelected(int, QString)'), self.setValue)
        pos = self.rect().bottomLeft()
        pos2 = self.rect().topLeft()
        pos = self.mapToGlobal(pos)
        pos2 = self.mapToGlobal(pos2)
        size = self._popup.sizeHint()
        width= max(size.width(), self.width())
        size.setWidth(width)
        screen = QtGui.QApplication.desktop().availableGeometry(pos)
        pos.setX( max(min(pos.x(), screen.right()-size.width()), screen.left()) )
        pos.setY( max(min(pos.y(), screen.bottom()-size.height()), screen.top()) )
        self._popup.move(pos)
        self._popup.resize(size)
        self._popup.show()
        self._popup.setDate(self.date)
        self._popup.setClientRelationCode(self.clientId, self.mainClientId, self.regAddressInfo, self.logAddressInfo)
        self._popup.regAddressInfo = self.regAddressInfo
        self._popup.logAddressInfo = self.logAddressInfo

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            self.updateFreeInput()
        else:
            QtGui.QComboBox.keyPressEvent(self, event)

    def setRecord(self, record):
        self._record = record

    def setDate(self, date):
        self.date = date


    def setValue(self, clientId,  freeInput = u''):
        self.clientId = forceRef(clientId)
        if freeInput:
            self._freeInput = QString(freeInput)
        elif self.lineEdit().text():
            self._freeInput = self.lineEdit().text()
        else:
            self._freeInput = self._record.value('freeInput')
        if forceString(self._freeInput):
            self.lineEdit().setReadOnly(False)
        self.updateText()


    def value(self):
        if not self.clientId and forceString(self.currentText()):
            self.emit(SIGNAL('saveExtraData(QString, QString)'), QString(u'freeInput'), self.currentText())
        return self.clientId


    def updateText(self):
        if forceString(self._freeInput):
            if type(self._freeInput) == QVariant:
                self._freeInput = self._freeInput.toString()
            self.setEditText(self._freeInput)
        else:
            self.setEditText(clientIdToText(self.clientId))

    def updateFreeInput(self):
        self._freeInput = self.lineEdit().text()
        self.emit(SIGNAL('saveExtraData(QString, QString)'), QString(u'freeInput'), self._freeInput)
        self.updateText()
