#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
import thread
from threading import Thread

from Users.DirtyCrypt import encryptPassword, decryptPassword
from PyQt4 import QtGui, QtCore
import md5
import os
import sys
from uuid import getnode as get_mac
from datetime import date

from Users.Tables import demoUserName
from library.Utils import forceString, forceBool, setPref, toVariant


def isPython27():
    major, minor = sys.version_info[:2]
    return major == 2 and minor == 7


def formatSerial(val):
    val = val.upper()
    val = val[30:32] + '-' + val[0:6] + '-' + val[6:12] + '-' + val[12:18] + '-' + val[18:24] + '-' + val[24:30]
    return val


class CPreferences(object):
    defaultDriverName = 'mysql'
    defaultServerName = 'localhost'
    defaultServerPort = 0
    defaultDatabaseName = 's11'
    defaultLoggerDBName = 'logger'
    defaultDBUserName   = 'dbuser'
    defaultPassword   = 'dbpassword'
    defaultAppUserName= demoUserName
    defaultUserPassword = None
    defaultLicNumber  = ''
    defaultActNumber  = ''
    defaultCompName   = ''
    defaultNewAuthorizationScheme = False

    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance

    def updateEndDate(self):
        if (len(self.licNumber) == 19):
            try:            
                sLic = str(self.licNumber)
                a = int(sLic[0 :4 ], 16)
                b = int(sLic[5 :9 ], 16)
                c = int(sLic[10:14], 16)
                
                #  0123456789012345678901234567890123456
                #  0         1         2         3
                #  ED-3B8A94-A852D1-FB1F4E-A3580F-25E203
                #  xx xxxx     xxxx                 xxxx a1
                #       xxxx        xxxx     xxxx        b1
                #            xxxx          xxxx   xxxx   c1
                
                sIns = str(self.instNumber)
                a1 = int(sIns[0 :2 ], 16) ^ int(sIns[3 :7 ], 16) ^ int(sIns[12:16], 16) ^ int(sIns[33:37], 16)
                b1 = int(sIns[5 :9 ], 16) ^ int(sIns[17:21], 16) ^ int(sIns[26:30], 16)
                c1 = int(sIns[10:14], 16) ^ int(sIns[24:28], 16) ^ int(sIns[31:35], 16)
                
                sAct = str(self.actNumber)
                a3 = int(sAct[5 :9 ], 16)
                b3 = int(sAct[10:14], 16)
                c3 = int(sAct[15:19], 16)
                
                a4 = a ^ a1 ^ a3
                b4 = b ^ b1 ^ b3 ^ a3
                c4 = c ^ c1 ^ c3 ^ b3
                
                check1 = sAct[0:4]
                check2 = sAct[20:24]
                
                v = str(md5.new(str(a4 + b4 + c4) + 'iVista' + sLic).hexdigest())
                v = v.upper()
                
                if ((v[0:4] == check1) and (v[20:24] == check2)):
                    self.endDate = date(c4, b4, a4)
                else:
                    self.endDate = None
            except:
                self.endDate = None
        else:
            self.endDate = None

    def __init__(self, iniFileName='preferences'):

        mainMedia = md5.new(str(get_mac()))

        self.actNumber  = CPreferences.defaultActNumber
        self.licNumber  = CPreferences.defaultLicNumber
        self.compName   = CPreferences.defaultCompName
        self.instNumber = formatSerial(mainMedia.hexdigest())
        self.updateEndDate()

        self.iniFileName = iniFileName

        self.decorStyle = 'Plastique'
        self.decorStandardPalette = True
        self.decorMaximizeMainWindow = True
        self.decorFullScreenMainWindow = False
        self.decorFontSize = QtGui.qApp.font().pointSize()
        self.decorFontFamily = QtGui.qApp.font().family()
        self.decor_crb_width_unlimited = False

        self.dbDriverName             = CPreferences.defaultDriverName
        self.dbConnectionName         = None
        self.dbServerName             = CPreferences.defaultServerName
        self.dbServerPort             = CPreferences.defaultServerPort
        self.dbDatabaseName           = CPreferences.defaultDatabaseName
        self.dbLoggerName             = CPreferences.defaultLoggerDBName
        self.dbCompressData           = False
        self.dbUserName               = CPreferences.defaultDBUserName
        self.dbPassword               = CPreferences.defaultPassword
        self.dbAutoLogin              = True
        self.appUserName              = CPreferences.defaultAppUserName
        self.userPassword             = CPreferences.defaultUserPassword
        self.isSaveUserPasword        = False
        self.dbNewAuthorizationScheme = CPreferences.defaultNewAuthorizationScheme

        self.windowPrefs = {} if not hasattr(self, 'windowPrefs') else self.windowPrefs
        self.reportPrefs = {} if not hasattr(self, 'reportPrefs')else self.reportPrefs
        self.appPrefs    = {} if not hasattr(self, 'appPrefs') else self.appPrefs
        self.tablePrefs  = {} if not hasattr(self, 'tablePrefs') else self.tablePrefs

        self._loadedGoupNameList = []

    @staticmethod
    def getSettings(iniFileName):
        head, tail = os.path.split(iniFileName)
        if head:
            iniFileName = os.path.abspath(iniFileName)
            settings = QtCore.QSettings(iniFileName, QtCore.QSettings.IniFormat)
        else:
            tmpSettings = QtCore.QSettings(QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope, 'vista-med', 'tmp')
            dir = os.path.dirname(unicode(QtCore.QDir.toNativeSeparators(tmpSettings.fileName())))
            iniFileName = os.path.join(dir, iniFileName)
            settings = QtCore.QSettings(iniFileName, QtCore.QSettings.IniFormat)
        return settings

    def getAdditionalSettingFilePath(self):
        currentDir = os.path.abspath(os.path.curdir)
        root, ext = os.path.splitext(self.iniFileName)
        iniFileName = ''.join([root, '_global', ext])
        return os.path.join(currentDir, iniFileName)

    def getAdditionalSettings(self):
        iniFilePath = self.getAdditionalSettingFilePath()
        if os.path.exists(iniFilePath):
            return QtCore.QSettings(iniFilePath, QtCore.QSettings.IniFormat)
        return None

    def syncAdditionalSettingsFile(self, doDelete = False):
        self.save()
        iniFilePath = self.getAdditionalSettingFilePath()
        if doDelete and os.path.exists(iniFilePath):
            os.remove(iniFilePath)

    def getDir(self):
        settings = CPreferences.getSettings(self.iniFileName)
        fileName = settings.fileName()
        return os.path.dirname(unicode(QtCore.QDir.toNativeSeparators(fileName)))

    ## Возвращает список имен поддерживаемых групп настроек
    # (для использоваении в параметре onlyTheseGroups функции load)
    def supportedGroupNames(self):
        return [u'lic', u'decor', u'db', u'windowPrefs', u'reportPrefs', u'appPrefs', u'tablePrefs']

    ## Загружает настройки из настроенного источника
    #    @param onlyTheseGroups: список с именами тех групп настроек, которые необходимо загрузить
    #                            либо None, если необходимо загружать все
    def loadSettingsBase(self, settings, onlyTheseGroups = None):
        if not isinstance(onlyTheseGroups, list) or 'lic' in onlyTheseGroups:
            settings.beginGroup('lic')
            self.actNumber = settings.value('activation', QtCore.QVariant(self.actNumber)).toString()
            self.licNumber = settings.value('license', QtCore.QVariant(self.licNumber)).toString()
            self.compName = settings.value('company', QtCore.QVariant(self.compName)).toString()
            settings.endGroup()
            self.updateEndDate()

            self._loadedGoupNameList.append('lic')

        if not isinstance(onlyTheseGroups, list) or 'decor' in onlyTheseGroups:
            settings.beginGroup('decor')
            self.decorStyle = settings.value('style', QtCore.QVariant(self.decorStyle) ).toString()
            if self.decorStyle in ('Cleanlooks', 'GTK+'):
                self.decorStyle = 'Plastique'
            self.decorStandardPalette = settings.value('standardPalette', QtCore.QVariant(self.decorStandardPalette)).toBool()
            self.decorMaximizeMainWindow = settings.value('maximizeMainWindow', QtCore.QVariant(self.decorMaximizeMainWindow)).toBool()
            self.decorFullScreenMainWindow = settings.value('fullScreenMainWindow', QtCore.QVariant(self.decorFullScreenMainWindow)).toBool()
            self.decorFontSize = settings.value('fontSize', QtCore.QVariant(self.decorFontSize)).toInt()[0]
            self.decorFontFamily = settings.value('fontFamily', QtCore.QVariant(self.decorFontFamily)).toString()
            self.decor_crb_width_unlimited = settings.value('crbWidthUnlimited', QtCore.QVariant(self.decor_crb_width_unlimited)).toBool()
            settings.endGroup()
            self._loadedGoupNameList.append('decor')

        if not isinstance(onlyTheseGroups, list) or 'db' in onlyTheseGroups:
            settings.beginGroup('db')
            self.dbConnectionName = unicode(settings.value('connectionName', QtCore.QVariant(self.dbConnectionName)).toString())
            self.dbDriverName = unicode(settings.value('driverName', QtCore.QVariant(self.dbDriverName)).toString())
            self.dbServerName = unicode(settings.value('serverName', QtCore.QVariant(self.dbServerName)).toString())
            self.dbServerPort = settings.value('serverPort', QtCore.QVariant(self.dbServerPort)).toInt()[0]
            self.dbDatabaseName = unicode(settings.value('database', QtCore.QVariant(self.dbDatabaseName)).toString())
            self.dbLoggerName = unicode(settings.value('loggerdb', QtCore.QVariant(self.dbLoggerName)).toString())
            self.dbCompressData = settings.value('compressData', QtCore.QVariant(self.dbCompressData)).toBool()
            self.dbUserName = unicode(settings.value('userName', QtCore.QVariant(self.dbUserName)).toString())

            dbEncryptedPassword = forceString(settings.value('encryptedPassword', QtCore.QVariant()))
            self.dbPassword = decryptPassword(dbEncryptedPassword) if dbEncryptedPassword else self.defaultPassword
            userEncryptedPassword = forceString(settings.value('userEncryptedPassword', QtCore.QVariant()))
            self.userPassword = decryptPassword(userEncryptedPassword) if userEncryptedPassword else self.defaultUserPassword
            self.isSaveUserPasword = forceBool(settings.value('isSaveUserPassword', QtCore.QVariant(False)))

            self.dbAutoLogin = settings.value('autoLogin', QtCore.QVariant(self.dbAutoLogin)).toBool()
            self.appUserName = unicode(settings.value('appUserName', QtCore.QVariant(self.appUserName)).toString())
            self.dbNewAuthorizationScheme = settings.value('newAuthorizationScheme', QtCore.QVariant(self.dbNewAuthorizationScheme)).toBool()
            settings.endGroup()
            self._loadedGoupNameList.append('db')

        settings.beginGroup('windowPrefs')
        setPref(self.windowPrefs, 'mainwindow', self.loadProp(settings, 'mainwindow'))
        setPref(self.windowPrefs, 'dialog', self.loadProp(settings, 'dialog'))
        settings.endGroup()
        self._loadedGoupNameList.append('windowPrefs')

        if not isinstance(onlyTheseGroups, list) or 'reportPrefs' in onlyTheseGroups:
            settings.beginGroup('reportPrefs')
            for reportName in settings.childGroups():
                setPref(self.reportPrefs, reportName, self.loadProp(settings, reportName))
            settings.endGroup()
            self._loadedGoupNameList.append('reportPrefs')

        if not isinstance(onlyTheseGroups, list) or 'appPrefs' in onlyTheseGroups:
            settings.beginGroup('appPrefs')
            for prop in settings.childKeys():
                self.appPrefs[unicode(prop)] = settings.value(prop, QtCore.QVariant())
            for group in settings.childGroups():
                setPref(self.appPrefs, unicode(group), self.loadProp(settings, group))
            settings.endGroup()
            self._loadedGoupNameList.append('appPrefs')

        if not isinstance(onlyTheseGroups, list) or 'tablePrefs' in onlyTheseGroups and not QtGui.qApp.isWindowPrefsDisabled():
            settings.beginGroup('tablePrefs')
            tables = settings.childGroups()
            for tableName in tables:
                setPref(self.tablePrefs, tableName, self.loadProp(settings, tableName))
            settings.endGroup()
            self._loadedGoupNameList.append('tablePrefs')

    def loadWindowsPreferences(self, settings,  onlyTheseGroups = None):
        if not isinstance(onlyTheseGroups, list) or 'windowPrefs' in onlyTheseGroups and not QtGui.qApp.isWindowPrefsDisabled():
            settings.beginGroup('windowPrefs')
            windows = settings.childGroups()
            for windowName in windows:
                setPref(self.windowPrefs, windowName, self.loadProp(settings, windowName))
            settings.endGroup()
            self._loadedGoupNameList.append('windowPrefs')

    ## Инициирует загрузку настроек
    #    @param onlyTheseGroups: список с именами тех групп настроек, которые необходимо загрузить
    #                            либо None, если необходимо загружать все
    def load(self, onlyTheseGroups = None):

        try:
            settings = CPreferences.getSettings(self.iniFileName)
            self.loadSettingsBase(settings, onlyTheseGroups)
            if isPython27():
                self.thread = Thread(target=self.loadWindowsPreferences, args=(settings, onlyTheseGroups))
                self.thread.start()
            else:
                self.loadWindowsPreferences(settings, onlyTheseGroups)

            addSettings = self.getAdditionalSettings()
            if addSettings:
                self.loadSettingsBase(addSettings, onlyTheseGroups)
                self.syncAdditionalSettingsFile()

        except:
            pass

    def loadProp(self, settings, propName):
        # TODO: skkachaev: Замедляет загрузку. Если будут баги — надо в сохранении заменять, а не в загрузке
        # propName = propName.replace('/', '')
        # propName = propName.replace('\\', '')
        settings.beginGroup(propName)
        result = {}
        props = settings.childKeys()
        for prop in props:
            setPref(result, prop, settings.value(prop, QtCore.QVariant()))
        groups = settings.childGroups()
        for group in groups:
            setPref(result, group, self.loadProp(settings, group))
        settings.endGroup()
        return result

    def save(self):
        try:
            settings = CPreferences.getSettings(self.iniFileName)

            if 'lic' in self._loadedGoupNameList:
                settings.beginGroup('lic')
                settings.setValue('activation',  QtCore.QVariant(self.actNumber))
                settings.setValue('license',     QtCore.QVariant(self.licNumber))
                settings.setValue('company',     QtCore.QVariant(self.compName))
                settings.endGroup()
                self.updateEndDate()

            if 'decor' in self._loadedGoupNameList:
                settings.beginGroup('decor')
                settings.setValue('style', QtCore.QVariant(self.decorStyle))
                settings.setValue('standardPalette', QtCore.QVariant(self.decorStandardPalette))
                settings.setValue('maximizeMainWindow', QtCore.QVariant(self.decorMaximizeMainWindow))
                settings.setValue('fullScreenMainWindow', QtCore.QVariant(self.decorFullScreenMainWindow))
                settings.setValue('fontSize', QtCore.QVariant(self.decorFontSize))
                settings.setValue('fontFamily', QtCore.QVariant(self.decorFontFamily))
                settings.setValue('crbWidthUnlimited', QtCore.QVariant(self.decor_crb_width_unlimited))
                settings.endGroup()

            if 'db' in self._loadedGoupNameList:
                settings.beginGroup('db')
                settings.setValue('connectionName', QtCore.QVariant(self.dbConnectionName))
                settings.setValue('driverName', QtCore.QVariant(self.dbDriverName))
                settings.setValue('serverName', QtCore.QVariant(self.dbServerName))
                settings.setValue('serverPort', QtCore.QVariant(self.dbServerPort))
                settings.setValue('database',   QtCore.QVariant(self.dbDatabaseName))
                settings.setValue('loggerdb',   QtCore.QVariant(self.dbLoggerName))
                settings.setValue('compressData', QtCore.QVariant(self.dbCompressData))
                settings.setValue('userName',   QtCore.QVariant(self.dbUserName))
                settings.remove('password')
                settings.setValue('encryptedPassword', QtCore.QVariant(encryptPassword(self.dbPassword)))
                if self.isSaveUserPasword:
                    settings.setValue('userEncryptedPassword', QtCore.QVariant(QtCore.QByteArray(encryptPassword(self.userPassword))))
                else:
                    settings.remove('userEncryptedPassword')
                settings.setValue('isSaveUserPassword', QtCore.QVariant(self.isSaveUserPasword))
                settings.setValue('autoLogin',  QtCore.QVariant(self.dbAutoLogin))
                settings.setValue('appUserName',QtCore.QVariant(self.appUserName))
                settings.setValue('newAuthorizationScheme', QtCore.QVariant(self.dbNewAuthorizationScheme))
                settings.endGroup()

            if 'windowPrefs' in self._loadedGoupNameList and not QtGui.qApp.isWindowPrefsDisabled():
                settings.beginGroup('windowPrefs')
                for windowName in self.windowPrefs:
                    self.saveProp(settings, windowName, self.windowPrefs[windowName])
                settings.endGroup()

            if 'reportPrefs' in self._loadedGoupNameList:
                settings.beginGroup('reportPrefs')
                for reportName in self.reportPrefs:
                    self.saveProp(settings, reportName, self.reportPrefs[reportName])
                settings.endGroup()

            if 'appPrefs' in self._loadedGoupNameList:
                self.saveProp(settings, 'appPrefs', self.appPrefs)

            if 'tablePrefs' in self._loadedGoupNameList and not QtGui.qApp.isWindowPrefsDisabled():
                settings.beginGroup('tablePrefs')
                for tableName in self.tablePrefs:
                    self.saveProp(settings, tableName, self.tablePrefs[tableName])
                settings.endGroup()

            settings.sync()
        except:
            QtGui.qApp.logCurrentException()

    def saveProp(self, settings, propName, propVal):
        # Не стоит использовать слэши в имени свойства. Сделаем вид, что их нет и не было.
        propName = propName.replace('/', '')
        propName = propName.replace('\\', '')
        if type(propVal) == dict:
            settings.beginGroup(propName)
            for subPropName in propVal:
                self.saveProp(settings, forceString(subPropName), propVal[subPropName])
            settings.endGroup()
        else:
            settings.setValue(propName, toVariant(propVal))