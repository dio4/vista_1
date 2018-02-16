# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2016 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from Registry.Ui_VIPStatusCommentEditDialog import Ui_VIPStatusComment
from Registry.Utils import editClientVIPStatus
from Users.Rights import urSetVIPComment, urEditSetVIPStatus
from library.Utils import forceString, forceRef


class CVIPStatusCommentEditDialog(QtGui.QDialog, Ui_VIPStatusComment):
    _buttonName = [u'Снять статус', u'Выставить статус']
    _status = [u'ВЫСТАВЛЕН', u'НЕ ВЫСТАВЛЕН']

    def __init__(self, clientId):
        QtGui.QDialog.__init__(self)
        Ui_VIPStatusComment.__init__(self)
        self.setupUi(self)
        # self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        self.setWindowFlags(
            QtCore.Qt.Dialog |
            QtCore.Qt.WindowCloseButtonHint |
            QtCore.Qt.WindowSystemMenuHint
        )
        self.clientId = clientId
        self.isVIP = False
        self.saved = False

        colorList = [forceString(x.value('color')).upper()
                     for x in QtGui.qApp.db.getRecordList(table='rbVIPColor', cols='color')]

        self.cmbColor.model().changeColorList(colorList)
        self.setData()

        if QtGui.qApp.userHasRight(urSetVIPComment) and not QtGui.qApp.userHasRight(urEditSetVIPStatus):
            self.btnStatus.setEnabled(False)

    def setData(self):
        db = QtGui.qApp.db
        tableClientVIP = db.table('ClientVIP')

        record = db.getRecordEx(
            tableClientVIP,
            ['id', 'comment', 'color'],
            [
                tableClientVIP['deleted'].eq(0),
                tableClientVIP['client_id'].eq(self.clientId)
            ]
        )
        if record:
            if forceRef(record.value('id')):
                self.isVIP = True

            comment = forceString(record.value('comment'))
            if comment:
                self.edtVIPStatusComment.setText(comment)
            self.setVIPStatus(self.isVIP)
            self.cmbColor.setColor(forceString(record.value('color')))
        else:
            self.setVIPStatus()

    def setVIPStatus(self, isSet=False):
        self.edtVIPStatusComment.setEnabled(isSet)
        if isSet:
            self.edtStatus.setText(self._status[0])
            self.btnStatus.setText(self._buttonName[0])
        else:
            self.edtStatus.setText(self._status[1])
            self.btnStatus.setText(self._buttonName[1])

    @QtCore.pyqtSlot()
    def on_btnStatus_clicked(self):
        if self.isVIP:
            self.isVIP = False
            self.setVIPStatus(False)
        else:
            self.isVIP = True
            self.setVIPStatus(True)

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Ok:
            self.save()

    def getColor(self):
        return self.cmbColor.value().name()

    def save(self):
        self.saved = True
        editClientVIPStatus(self.clientId, self.edtVIPStatusComment.text(), not self.isVIP, self.getColor())


if __name__ == '__main__':
    import sys
    QtGui.qApp = QtGui.QApplication(sys.argv)
    dlg = CVIPStatusCommentEditDialog(0)
    dlg.show()
    QtGui.qApp.exec_()

