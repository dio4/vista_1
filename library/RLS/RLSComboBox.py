# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from library.RLS.RLSComboBoxPopup import CRLSComboBoxPopup
from library.Utils import forceString


class CRLSComboBox(QtGui.QComboBox):
    __pyqtSignals__ = ('textChanged(QString)',
                       'textEdited(QString)',
                       'codeSelected(int)')

    def __init__(self, parent=None):
        QtGui.QComboBox.__init__(self, parent)
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self._popup = None
        self.code = None
        self.date = QtCore.QDate.currentDate()

    def showPopup(self):
        if not self._popup:
            self._popup = CRLSComboBoxPopup(self)
            self.connect(self._popup, QtCore.SIGNAL('RLSCodeSelected(int)'), self.setValue)
        pos = self.rect().bottomLeft()
        pos2 = self.rect().topLeft()
        pos = self.mapToGlobal(pos)
        pos2 = self.mapToGlobal(pos2)
        size = self._popup.sizeHint()
        width = max(size.width(), self.width())
        size.setWidth(width)
        screen = QtGui.QApplication.desktop().availableGeometry(pos)
        pos.setX(max(min(pos.x(), screen.right() - size.width()), screen.left()))
        pos.setY(max(min(pos.y(), screen.bottom() - size.height()), screen.top()))

        self._popup.move(pos)
        self._popup.resize(size)
        self._popup.show()
        self._popup.setDate(self.date)
        self._popup.setRLSCode(self.code)

    def setDate(self, date):
        self.date = date

    def setValue(self, code):
        if code:
            self.emit(QtCore.SIGNAL('codeSelected(int)'), code)
        self.code = code
        self.updateText()

    def value(self):
        return self.code

    @staticmethod
    def codeToText(code):
        if code:
            db = QtGui.qApp.db
            tableVNomen = db.table('rls.vNomen')
            fields = ['INPName', 'tradeName', 'dosage', 'form', 'filling', 'packing']

            record = db.getRecordEx(tableVNomen, fields, tableVNomen['code'].eq(code))
            if record:
                text = u', '.join(filter(bool, [forceString(record.value(field)) for field in fields]))
            else:
                text = '{%s}' % code
        else:
            text = ''
        return text

    def updateText(self):
        self.setEditText(self.codeToText(self.code))
