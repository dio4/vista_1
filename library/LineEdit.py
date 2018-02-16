# -*- coding: utf-8 -*-
# ############################################################################
##
## Copyright (C) 2014 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QT_VERSION

__author__ = 'atronah'

'''
    author: atronah
    date:   29.08.2014

    Класс для предоставления функционала QLineEdit из более свежих версий Qt (выше 4.5)
'''


class CLineEdit(QtGui.QLineEdit):
    def __init__(self, *args, **kwargs):
        super(CLineEdit, self).__init__(*args, **kwargs)
        self._placeholderText = u''
        self._isPlaceholderTextShowed = False
        self._savedStyleSheet = u''


    def setPlaceholderText(self, text):
        if QT_VERSION < 0x040700:
            self._placeholderText = unicode(text)
            self.updatePlaceholderText()
        else:
            super(CLineEdit, self).setPlaceholderText(text)


    def placeholderText(self):
        if QT_VERSION < 0x040700:
            return self._placeholderText
        else:
            super(CLineEdit, self).placeholderText()


    def updatePlaceholderText(self):
        if QT_VERSION >= 0x040700:
            return
        if not self._placeholderText:
            return
        if self._isPlaceholderTextShowed:
            self._isPlaceholderTextShowed = False
            self.setStyleSheet(self._savedStyleSheet)
            self.setText(u'')
        else:
            if self.text().isEmpty():
                self._savedStyleSheet = self.styleSheet()
                self.setText(self._placeholderText)
                self.setCursorPosition(0)
                self.setStyleSheet(self._savedStyleSheet + u' color:#808080')
                self._isPlaceholderTextShowed = True


    def focusInEvent(self, event):
        self.updatePlaceholderText()
        super(CLineEdit, self).focusInEvent(event)


    def focusOutEvent(self, event):
        self.updatePlaceholderText()
        super(CLineEdit, self).focusOutEvent(event)

    def setText(self, text):
        if QT_VERSION < 0x040700:
            if self._isPlaceholderTextShowed:
                self._isPlaceholderTextShowed = False
                self.setStyleSheet(self._savedStyleSheet)
        return super(CLineEdit, self).setText(text)

    def text(self):
        if QT_VERSION < 0x040700 and self._isPlaceholderTextShowed:
            return QtCore.QString(u'')
        return super(CLineEdit, self).text()
