from PyQt4 import QtCore, QtGui


class CComboBoxPopupTreeView(QtGui.QTreeView):
    def __init__(self, parent):
        QtGui.QTreeView.__init__(self, parent)

    def keyPressEvent(self, evt):
        if evt.key() == QtCore.Qt.Key_Space:
            self.emit(QtCore.SIGNAL('hide()'))
        else:
            super(CComboBoxPopupTreeView, self).keyPressEvent(evt)


class CComboBoxPopupListView(QtGui.QListView):
    def __init__(self, parent):
        QtGui.QListView.__init__(self, parent)

    def keyPressEvent(self, evt):
        if evt.key() == QtCore.Qt.Key_Space:
            self.emit(QtCore.SIGNAL('hide()'))
        else:
            super(CComboBoxPopupListView, self).keyPressEvent(evt)


class CComboBox(QtGui.QComboBox):
    def __init__(self, parent):
        super(CComboBox, self).__init__(parent)
        self._view = CComboBoxPopupListView(self)
        self.connect(self._view, QtCore.SIGNAL('hide()'), self.hidePopup)
        self.setView(self._view)
