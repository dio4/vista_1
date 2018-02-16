# -*- coding: utf-8 -*-
from library.Preferences import CPreferences
from library.Utils import toVariant, forceInt, forceString, forceRef

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################


"""
editor of preferences of connection to database
"""

from PyQt4 import QtGui, QtCore

from library.vm_collections import OrderedDict

from Ui_connection          import Ui_connectionDialog


class CConnectionDialog(QtGui.QDialog, Ui_connectionDialog):

    iniFileName = 'connections.ini'
    
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.edtConnectionName.completer().setCompletionMode(QtGui.QCompleter.UnfilteredPopupCompletion)
        self.connect(self, QtCore.SIGNAL('accepted()'), self.saveConnectionInfo)
        self.connectionInfo = OrderedDict()
        self.loadConnectionInfo()
        

    def setDriverName(self, val):
        pass

    def driverName(self):
        return 'mysql'

    def setServerName(self, val):
        self.edtServerName.setText(val)
        
    
    def setConnectionName(self, name):
        defaultName = u'Основной'
        connectionIndex = self.edtConnectionName.findText(name)
        if connectionIndex < 0:
            connectionIndex = self.edtConnectionName.findText(defaultName)
        if connectionIndex < 0:
            connectionIndex = self.edtConnectionName.findText(self.serverName())
        
        if connectionIndex < 0:
            self.edtConnectionName.setEditText(defaultName)
        else:
            self.edtConnectionName.setCurrentIndex(connectionIndex)
    
    def connectionName(self):
        return self.edtConnectionName.currentText()

    def serverName(self):
        return str(self.edtServerName.text())

    def setServerPort(self, val):
        self.edtServerPort.setValue(val)

    def serverPort(self):
        return self.edtServerPort.value()

    def setDatabsaseName(self, val):
        self.edtDatabaseName.setText(val)

    def setLoggerDbName(self, val):
        self.edtLoggerDbName.setText(val)

    def databaseName(self):
        return self.edtDatabaseName.text()

    def loggerDbName(self):
        if self.edtLoggerDbName.text():
           return self.edtLoggerDbName.text()
        else:
            self.edtLoggerDbName.setText(u"logger")
            return self.edtLoggerDbName.text()

    def setCompressData(self, val):
        self.chkCompressData.setChecked(bool(val))

    def compressData(self):
        return self.chkCompressData.isChecked()

    def setUserName(self, val):
        self.edtUserName.setText(val)

    def userName(self):
        return self.edtUserName.text()

    def setPassword(self, val):
        self.edtPassword.setText(val)

    def password(self):
        return str(self.edtPassword.text())

    def setNewAuthorizationScheme(self, val):
        checkedValue = bool(val)
        self.chkAutScheme.setChecked(checkedValue)
        self.on_chkAutScheme_clicked(checkedValue)

    def newAuthorizationScheme(self):
        return self.chkAutScheme.isChecked()
    
    
    def connectionOrgId(self):
        connectionInfo = self.connectionInfo.get(self.edtConnectionName.currentText(), None)
        return connectionInfo[3] if connectionInfo else 0

    def connectionLogin(self):
        connectionInfo = self.connectionInfo.get(self.edtConnectionName.currentText(), None)
        return connectionInfo[4] if connectionInfo else u''

    def connectionOrgStructureId(self):
        connectionInfo = self.connectionInfo.get(self.edtConnectionName.currentText(), None)
        return connectionInfo[5] if connectionInfo else 0
    
    @QtCore.pyqtSlot(bool)
    def saveConnectionInfo(self):
        settings = CPreferences.getSettings(self.iniFileName)
        settings.beginGroup(self.edtConnectionName.currentText())
        settings.setValue('host', toVariant(self.serverName()))
        settings.setValue('port', toVariant(self.serverPort()))
        settings.setValue('database', toVariant(self.databaseName()))
        settings.setValue('loggerdb', toVariant(self.loggerDbName()))
#        settings.setValue('orgId', toVariant(QtGui.qApp.currentOrgId()))
        settings.endGroup()
        settings.sync()
    
    def loadConnectionInfo(self):
        self.connectionInfo.clear()
        settings = CPreferences.getSettings(self.iniFileName)
        for connectionName in settings.childGroups():
            settings.beginGroup(connectionName)
            self.connectionInfo[connectionName] = (forceString(settings.value('host', connectionName)),
                                                   forceInt(settings.value('port', 0)), 
                                                   forceString(settings.value('database', u's11')),
                                                   forceRef(settings.value('orgId', None)),
                                                   forceString(settings.value('login', u'')),
                                                   forceRef(settings.value('orgStructureId', None)),
                                                   forceString(settings.value('loggerdb', u'logger'))
                                                   )
            settings.endGroup()
        self.edtConnectionName.addItems(self.connectionInfo.keys())

    @QtCore.pyqtSlot(bool)
    def on_chkAutScheme_clicked(self, checked):
        self.groupBox.setEnabled(not checked)
        
    @QtCore.pyqtSlot(int)
    def on_edtConnectionName_currentIndexChanged(self, index):
        currentText = self.edtConnectionName.currentText()
        if currentText in self.connectionInfo.keys():
            host, port, database = self.connectionInfo[currentText][:3]
            loggerdb = self.connectionInfo[currentText][6]
            self.setServerName(host)
            self.setServerPort(port)
            self.setDatabsaseName(database)
            self.setLoggerDbName(loggerdb)
    
    
    @QtCore.pyqtSlot()
    def on_btnDelConnectionInfo_clicked(self):
        settings = CPreferences.getSettings(self.iniFileName)
        currentText = self.edtConnectionName.currentText()
        if currentText in settings.childGroups():
            settings.remove(currentText)
            settings.sync()
        self.connectionInfo.pop(currentText, None)
        self.edtConnectionName.clear()
        self.edtConnectionName.addItems(self.connectionInfo.keys())
        self.edtConnectionName.setCurrentIndex(0)