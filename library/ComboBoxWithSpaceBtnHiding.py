# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore

from library.ListModel import CListModel

class CSpaceBtnHidingModel(CListModel):
    def __init__(self, lst, refBook=None):
        CListModel.__init__(self, lst, lst if refBook is None else refBook)


class CSpaceBtnHidingView(QtGui.QListView):
    def __init__(self, parent):
        QtGui.QListView.__init__(self, parent)
        self.cComboBoxWithSpaceHiding = parent


    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            CComboBoxWithSpaceBtnHiding.keyPressEvent(self.cComboBoxWithSpaceHiding, event)
        else:
            QtGui.QListView.keyPressEvent(self, event)


class CComboBoxWithSpaceBtnHiding(QtGui.QComboBox):
    """QComboBox with showing and hiding popup on space key event"""

    def __init__(self, parent, lst, refBook=None):
        QtGui.QComboBox.__init__(self, parent)
        self._model = CSpaceBtnHidingModel(lst, refBook)
        self.setModel(self._model)
        self.isShown = False
        self.popupView = CSpaceBtnHidingView(self)
        self.setView(self.popupView)


    def showPopup(self):
        super(CComboBoxWithSpaceBtnHiding, self).showPopup()
        self.isShown = True


    def hidePopup(self):
        super(CComboBoxWithSpaceBtnHiding, self).hidePopup()
        self.isShown = False


    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            if self.isShown:
                self.hidePopup()
            else:
                self.showPopup()
        else:
            QtGui.QComboBox.keyPressEvent(self, event)