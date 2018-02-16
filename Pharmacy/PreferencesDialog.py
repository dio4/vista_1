# -*- coding: utf-8 -*-

from PyQt4 import QtGui

from Pharmacy.Service import CPharmacyService
from Pharmacy.ui.Ui_PreferencesDialog import Ui_PreferencesDialog
from library.DialogBase import CDialogBase
from library.Utils import forceStringEx


class CPreferencesDialog(CDialogBase, Ui_PreferencesDialog):
    def __init__(self, parent):
        super(CPreferencesDialog, self).__init__(parent)
        self.setupUi(self)

        self.edtURL.textChanged.connect(self.updateBtnState)
        self.edtUser.textChanged.connect(self.updateBtnState)
        self.edtPassword.textChanged.connect(self.updateBtnState)
        self.btnTestConnect.clicked.connect(self.testConnect)

    def updateBtnState(self):
        self.btnTestConnect.setEnabled(
            bool(forceStringEx(self.edtURL.text())) and
            bool(forceStringEx(self.edtUser.text())) and
            bool(forceStringEx(self.edtPassword.text()))
        )

    def getSettings(self):
        return {
            'URL'     : forceStringEx(self.edtURL.text()),
            'User'    : forceStringEx(self.edtUser.text()),
            'Password': forceStringEx(self.edtPassword.text())
        }

    def setSettings(self, settings):
        self.edtURL.setText(settings.get('URL', ''))
        self.edtUser.setText(settings.get('User', ''))
        self.edtPassword.setText(settings.get('Password', ''))

    def testConnect(self):
        settings = self.getSettings()
        srv = CPharmacyService(settings['URL'], settings['User'], settings['Password'])
        currentUser, error = srv.testConnect()
        if currentUser and currentUser.id is not None:
            QtGui.QMessageBox.information(self,
                                          u'Проверка соединения',
                                          u'Соединение успешно<br>Текущий пользователь: <b>{0} | {1}</b>'.format(
                                              currentUser.username,
                                              currentUser.fullName
                                          ),
                                          QtGui.QMessageBox.Ok)
        else:
            QtGui.QMessageBox.warning(self,
                                      u'Проверка соединения',
                                      u'Соединение не удалось:<br>{0}'.format(error),
                                      QtGui.QMessageBox.Ok)
