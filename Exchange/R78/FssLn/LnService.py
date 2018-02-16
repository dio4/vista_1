# -*- coding: utf-8 -*-

# Сервис листов нетрудоспособности
import json
import urllib2

from PyQt4 import QtGui

from library.Utils import forceString, AnyRequest, forceInt


class LnService():

    def __init__(self):
        self.db = QtGui.qApp.db

    def checkConfig(self):
        if forceString(QtGui.qApp.preferences.appPrefs['LNService']) and forceString(QtGui.qApp.preferences.appPrefs['LNAddress']):
            return True
        else:
            QtGui.QMessageBox.warning(self, u'Ошибка', u'Не заполнены настройки сервиса листов нетрудоспособности')
            return False

    def getNewLnNumber(self):
        if self.checkConfig():
            try:
                req = AnyRequest(forceString(QtGui.qApp.preferences.appPrefs['LNAddress']) + u'/getNewLnNumber')
                result = '\n'.join(urllib2.urlopen(req).readlines())
                result = json.loads(result)
                if forceInt(result['Status']):
                    return forceString(result['Number'])
                else:
                    QtGui.QMessageBox.warning(self, u'Ошибка', forceString(result['Errors']))
                    return
            except urllib2.HTTPError as e:
                print 'Error:' + str(e.code)
            except urllib2.URLError, e:
                print 'Error:' + str(e.reason)
            except Exception as e:
                print 'Unknown error'

    def disableLn(self, lnCode, snils, reasoncode, reason):
        if self.checkConfig():
            try:
                req = AnyRequest(forceString(QtGui.qApp.preferences.appPrefs['LNAddress']) + u'/disableLn?lncode=%s&snils=%s&reasoncode=%s&reason=%s' %(lnCode, snils, reasoncode, reason))
                result = '\n'.join(urllib2.urlopen(req).readlines())
                result = json.loads(result)
                if forceInt(result['Status']):
                    return True
                else:
                    QtGui.QMessageBox.warning(None, u'Ошибка', forceString(result['Errors']))
                    return False
            except urllib2.HTTPError as e:
                print 'Error:' + str(e.code)
            except urllib2.URLError, e:
                print 'Error:' + str(e.reason)
            except Exception as e:
                print 'Unknown error'

    def prParseFilelnlpu(self, lnCode):
        if self.checkConfig():
            try:
                req = AnyRequest(forceString(QtGui.qApp.preferences.appPrefs['LNAddress']) + u'/prParseFilelnlpu?lncode=%s' % lnCode)
                result = '\n'.join(urllib2.urlopen(req).readlines())
                result = json.loads(result)
                if forceInt(result['Status']):
                    return True
                else:
                    QtGui.QMessageBox.warning(None, u'Ошибка', forceString(result['Errors']))
                    return False
            except urllib2.HTTPError as e:
                print 'Error:' + str(e.code)
            except urllib2.URLError, e:
                print 'Error:' + str(e.reason)
            except Exception as e:
                print 'Unknown error'

    def pingService(self):
        if self.checkConfig():
            try:
                req = AnyRequest(forceString(QtGui.qApp.preferences.appPrefs['LNAddress']) + u'/ping')
                result = '\n'.join(urllib2.urlopen(req).readlines())
                if forceString(result):
                    return True
                else:
                    QtGui.QMessageBox.warning(None, u'Ошибка', u'Неудалось установить соединение')
                    return False
            except urllib2.HTTPError as e:
                QtGui.QMessageBox.warning(None, u'Ошибка', u'Неудалось установить соединение')
            except urllib2.URLError, e:
                QtGui.QMessageBox.warning(None, u'Ошибка', u'Неудалось установить соединение')
            except Exception as e:
                QtGui.QMessageBox.warning(None, u'Ошибка', u'Неудалось установить соединение')