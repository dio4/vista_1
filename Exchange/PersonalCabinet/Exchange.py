# -*- coding: utf-8 -*-
from tempfile import TemporaryFile

import requests
from PyQt4 import QtGui, QtCore
import json

from library.Utils import forceString, forceInt, forceDate

u"""
Класс работы с личным кабинетом
"""


class PersonalCabinet():
    def __init__(self, clientId):
        u"""
        vistaHostName - название, используемое на бэкенде для определения, к какой больничке относится пациент
        :param clientId:
        """
        self.db = QtGui.qApp.db
        self.url = 'http://85.143.210.27/api'
        # self.username = 'reg'
        # self.password = 'reg'
        self.username = 'admin'
        self.password = 'admin'
        self.vistaHostName = forceString(QtGui.qApp.preferences.appPrefs['HostPersCabService'])
        self.token = None
        self.newUserId = None
        self.clientId = clientId

    def getToken(self):
        header = {'Accept': 'application/json', 'Authorization': 'Basic T29Wb2Q0b2phd2FlZnU0Wjp4YVlhaDVjaFRvaHg3cGll'}
        data = {'grant_type': 'password', 'username': self.username, 'password': self.password}
        resp = requests.post(url=(self.url + '/oauth/token'), data=data, headers=header)
        if resp.status_code == 200:
            result = json.loads(resp.text)
            self.token = result['access_token']
        else:
            QtGui.QMessageBox.warning(None, u'Ошибка', u'Не удалось получить токен\n%s' % resp.text)

    def regClient(self):
        tblClient = self.db.table('Client')
        tblContacts = self.db.table('ClientContact')
        tblContactType = self.db.table('rbContactType')
        tblClientInfo = tblClient.innerJoin(tblContacts, [tblContacts['client_id'].eq(tblClient['id']), tblContacts['deleted'].eq(0)])
        tblClientInfo = tblClientInfo.innerJoin(tblContactType, [tblContactType['id'].eq(tblContacts['contactType_id']), tblContactType['code'].eq('5')])
        recClient = self.db.getRecordEx(tblClientInfo,
                                        [tblClient['firstName'],
                                         tblClient['lastName'],
                                         tblClient['patrName'],
                                         tblClient['sex'],
                                         tblClient['birthDate'],
                                         tblContacts['contact']],
                                        tblClient['id'].eq(self.clientId))
        if recClient is None:
            QtGui.QMessageBox.warning(None, u'Ошибка', u'Укажите электронную почту')
            return
        if self.token:
            header = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % self.token}
            data = {
                u"user":{
                    u"username":forceString(recClient.value('contact')),
                    u"password":forceString(recClient.value('contact')),
                    u"email":forceString(recClient.value('contact')),
                    u"birthDate":forceString(forceDate(recClient.value('birthDate')).toString('yyyy-MM-dd')),
                    u"patrName":forceString(recClient.value('patrName')),
                    u"firstName":forceString(recClient.value('firstName')),
                    u"lastName":forceString(recClient.value('lastName')),
                    u"gender":u"MALE" if forceInt(recClient.value('sex')) == 1 else u'FEMALE',
                    u"type":u"PATIENT"
                },
                u"vistaHostName": self.vistaHostName,
                u"clientId": self.clientId
            }
            resp = requests.post(url=(self.url + '/users/reg'), data=json.dumps(data), headers=header)
            if resp.status_code == 200:
                result = json.loads(resp.text)
                self.newUserId = forceInt(result['id'])
            else:
                QtGui.QMessageBox.warning(None, u'Ошибка', u'Не удалось зарегистрировать пациента\n%s' % resp.text)
        else:
            QtGui.QMessageBox.warning(None, u'Ошибка', u'Не удалось получить токен')

    def register(self):
        self.getToken()
        if self.token:
            self.regClient()
            if self.newUserId:
                return True
            else:
                return False
        else:
            return False

def main():
    pass

if __name__ == '__main__':
    main()