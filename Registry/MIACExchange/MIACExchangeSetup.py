# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################


"""
editor of preferences of connection to MIAC
"""

from PyQt4 import QtCore, QtGui
from library.DialogBase import CDialogBase
from library.Utils      import forceStringEx

from Preferences import CMIACExchangePreferences
from Ui_MIACExchangeSetup import Ui_MIACExchangeSetupDialog


class CMIACExchangeSetupDialog(CDialogBase, Ui_MIACExchangeSetupDialog):
    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        self.btnTest =  QtGui.QPushButton(u'Проверить', self)
        self.btnTest.setObjectName('btnTest')
        self.setupUi(self)
        self.buttonBox.addButton(self.btnTest, QtGui.QDialogButtonBox.ActionRole)
        self.preferences = CMIACExchangePreferences()
        self.edtAddress.setText(self.preferences.address)
        self.edtPostBoxName.setText(self.preferences.postBoxName)
        self.chkCompress.setChecked(self.preferences.compress)
        self.chkSendByDefault.setChecked(self.preferences.sendByDefault)


    def saveData(self):
        self.preferences.address = forceStringEx(self.edtAddress.text())
        self.preferences.postBoxName = forceStringEx(self.edtPostBoxName.text())
        self.preferences.compress    = self.chkCompress.isChecked()
        self.preferences.sendByDefault = self.chkSendByDefault.isChecked()
        self.preferences.store()
        return True


    def checkConnection(self):
        address = unicode(self.edtAddress.text())
        if self.preferences.test(address):
            title = u'Тестовое соединение установлено'
            message = u'Получен ответ сервера'
            box = QtGui.QMessageBox.information
        else:
            title = u'Ошибка установления соединения'
            message = u'Ответ сервера не получен или неверен'
            box = QtGui.QMessageBox.critical
        box(self, title, message, QtGui.QMessageBox.Close)


    @QtCore.pyqtSlot()
    def on_btnTest_clicked(self):
        self.checkConnection()
