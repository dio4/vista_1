#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from Blank.BlankComboBoxPopup   import CBlankComboBoxPopup, CBlankComboBoxActionsPopup
from Registry.Utils             import codeToTextForBlank


class CBlankComboBox(QtGui.QComboBox):
    __pyqtSignals__ = ('textChanged(QString)',
                       'textEdited(QString)'
                      )

    def __init__(self, parent=None, blankIdList=None, docTypeActions=False):
        if not blankIdList:
            blankIdList = []
        QtGui.QComboBox.__init__(self, parent)
        self.setEditable(True)
        self.lineEdit().setReadOnly(False)
        self._popup = None
        self.code = None
        self.blankIdList = blankIdList
        self.docTypeActions = docTypeActions


    def showPopup(self):
        if not self._popup:
            self._popup = CBlankComboBoxPopup(self, self.docTypeActions)
            self.connect(self._popup,QtCore.SIGNAL('BlankCodeSelected(int)'), self.setValue)
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
        self._popup.setBlankIdList(self.blankIdList, self.code)


    def setValue(self, code):
        self.code = code
        self.updateText()


    def value(self):
        return self.code


    def setText(self, text):
        self.lineEdit().setText(text)


    def setCursorPosition(self, position):
        self.lineEdit().setCursorPosition(position)


    def text(self):
        return self.lineEdit().text()


    def updateText(self):
        self.setEditText(codeToTextForBlank(self.code))


    def setTempInvalidBlankIdList(self, blankIdList):
        self.blankIdList = blankIdList


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


class CBlankComboBoxActions(QtGui.QComboBox):
    __pyqtSignals__ = ('textChanged(QString)',
                       'textEdited(QString)'
                      )

    def __init__(self, parent=None, blankIdList=None, docTypeActions=False):
        if not blankIdList:
            blankIdList = []
        QtGui.QComboBox.__init__(self, parent)
        self.setEditable(True)
        self.lineEdit().setReadOnly(False)
        self._popup = None
        self.code = None
        self.blankIdList = blankIdList
        self.docTypeActions = docTypeActions


    def showPopup(self):
        if not self._popup:
            self._popup = CBlankComboBoxActionsPopup(self, self.docTypeActions)
            self.connect(self._popup,QtCore.SIGNAL('BlankCodeSelected(String)'), self.setValue)
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
        self._popup.setBlankIdList(self.blankIdList, None)


    def setValue(self, code):
        self.code = code
        self.setText(self.code)
        self.code = None


    def value(self):
        if self.code:
            return self.code
        else:
            return self.text()


    def setText(self, text):
        self.lineEdit().setText(text)


    def setCursorPosition(self, position):
        self.lineEdit().setCursorPosition(position)


    def text(self):
        return self.lineEdit().text()


    def updateText(self):
        self.setEditText(codeToTextForBlank(self.code))


    def setTempInvalidBlankIdList(self, blankIdList):
        self.blankIdList = blankIdList

