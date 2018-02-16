# -*- coding: utf-8 -*-


import sip
from PyQt4 import QtCore, QtGui

class CCustomComboBoxLike(QtGui.QComboBox):
    __pyqtSignals__ = ('editingFinished()',
                      )

    def __init__(self, parent = None):
        QtGui.QComboBox.__init__(self, parent)
        self.addItem('')
        self.setCurrentIndex(0)
        self._popup = None
        self._deletePopupOnClose = True
        self._value = None


    def setValue(self, value):
        self._value = value
        self.setItemText(0, self.valueAsString(self._value))


    def getValue(self):
        return self._value


    def createPopup(self):
        return None


    def valueAsString(self):
        return unicode(self._value)


    def setValueToPopup(self):
        pass


    def showPopup(self):
        if self._popup is None:
            self._popup = self.createPopup()
        self._popup.installEventFilter(self)

        comboRect = self.rect()
        popupTop = 0
        popupLeft = 0
        screen = QtGui.qApp.desktop().screenGeometry(self)
        below = self.mapToGlobal(comboRect.bottomLeft())
        above = self.mapToGlobal(comboRect.topLeft())
        if screen.bottom() - below.y() >= self._popup.height():
            popupTop = below.y()
        elif above.y() - screen.y() >= self._popup.height():
            popupTop = above.y()-self._popup.height()
        else:
            popupTop = max(screen.top(), screen.bottom()-self._popup.height())
        if screen.right() - below.x() >= self._popup.width():
            popupLeft = below.x()
        else:
            popupLeft = max(screen.left(), screen.right()-self._popup.width())
        self._popup.move(popupLeft, popupTop)
        self.setValueToPopup()
        self._popup.show()
        self._popup.setFocus()


    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Close:
            self.hidePopup()
            return True
        return QtGui.QComboBox.eventFilter(self, obj, event)


    def hidePopup(self):
        if self._popup and self._popup.isVisible():
            self._popup.installEventFilter(None)
            self._popup.close()
            if self._deletePopupOnClose:
                if self._popup:
                    sip.delete(self._popup)
                self._popup = None
        QtGui.QComboBox.hidePopup(self)
        self.setFocus()
        self.emit(QtCore.SIGNAL('editingFinished()'))

