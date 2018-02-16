# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################


"""
editor of preferences of connection to EMSRN
"""

from PyQt4 import QtCore, QtGui

from library.DialogBase     import CDialogBase
from library.Utils          import forceString, toVariant, getPref, setPref

from EMSRNExchange_client   import EMSRNExchangeLocator
from benefitCategories      import getBenefitCategories
from Ui_EMSRNExchangeSetup  import Ui_EMSRNExchangeSetupDialog


class CEMSRNExchangeSetupDialog(CDialogBase, Ui_EMSRNExchangeSetupDialog):
    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        self.btnTest =  QtGui.QPushButton(u'Проверить', self)
        self.btnTest.setObjectName('btnTest')
        self.setupUi(self)
        self.buttonBox.addButton(self.btnTest, QtGui.QDialogButtonBox.ActionRole)
        preferences = getPref(QtGui.qApp.preferences.appPrefs, 'EMSRNExchange', {})
        self.edtAddress.setText(forceString(getPref(preferences, 'address', EMSRNExchangeLocator.EMSRNExchangeSoap_address)))
        self.edtName.setText(forceString(getPref(preferences, 'name', '')))
        self.edtPassword.setText(forceString(getPref(preferences, 'password', '')))


    def saveData(self):
        preferences = {}
        setPref(preferences, 'address', toVariant(self.edtAddress.text()))
        setPref(preferences, 'name',    toVariant(self.edtName.text()))
        setPref(preferences, 'password',toVariant(self.edtPassword.text()))
        setPref(QtGui.qApp.preferences.appPrefs, 'EMSRNExchange', preferences)
        return True


    def checkConnection(self):
        address = unicode(self.edtAddress.text())
        name = unicode(self.edtName.text())
        password = unicode(self.edtPassword.text())
        result, junk = getBenefitCategories(address=address, name=name, password=password)
        if not isinstance(result, basestring):
            title = u'Ошибка установления соединения'
            message = u'Ответ сервера не получен или неверен'
            box = QtGui.QMessageBox.critical
        elif result == u'ОШИБКА АВТОРИЗАЦИИ':
            title = u'Ошибка установления соединения'
            message = u'Неверное имя или пароль'
            box = QtGui.QMessageBox.critical
        else:
            title = u'Тестовое соединение установлено'
            message = u'Получен ответ сервера'
            if result != u'НEКОРРЕКТНЫЕ ПАРАМЕТРЫ':
                message += ':\n'+result
            box = QtGui.QMessageBox.information
        box(self, title, message, QtGui.QMessageBox.Close)


    @QtCore.pyqtSlot()
    def on_btnTest_clicked(self):
        self.checkConnection()
