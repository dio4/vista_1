# -*- coding: utf-8 -*-
# ############################################################################
##
## Copyright (C) 2014 Vista Software. All rights reserved.
##
#############################################################################

__author__ = 'craz'

'''
    author: craz
    date:   27.10.2014
'''

import os

from PyQt4 import QtCore

from library.Utils          import forceInt, forceString, forceStringEx

class CRegIemcSettings(object):
    def __init__(self, appName):
        self.settings = QtCore.QSettings(QtCore.QSettings.IniFormat,
                                         QtCore.QSettings.UserScope,
                                         'Vista', appName)
        self.homedir = os.path.expanduser('~')

    # def getInputDir(self):
    #     return forceStringEx(self.settings.value('input_dir', self.homedir))

    # def getOutputDir(self):
    #     return forceStringEx(self.settings.value('output_dir', self.homedir))

    # def getErrorsDir(self):
    #     return forceStringEx(self.settings.value('errors_dir', self.homedir))

    # def getInputFileName(self):
    #     return forceStringEx(self.settings.value('input_file_name', ''))

    def getConnectionInfo(self):
        connectionInfo = {}
        self.settings.beginGroup('connection_info')
        connectionInfo['driverName'] = 'MYSQL'
        connectionInfo['host'] = forceString(self.settings.value('host', 'localhost'))
        connectionInfo['port'] = forceInt(self.settings.value('port', 3306))
        connectionInfo['database'] = forceString(self.settings.value('database', 's11'))
        connectionInfo['user'] = forceString(self.settings.value('user', 'dbuser'))
        connectionInfo['password'] = forceString(self.settings.value('password', 'dbpassword'))
        connectionInfo['connectionName'] = forceString(self.settings.value('connectionName', 'regiemk'))
        connectionInfo['compressData'] = True
        connectionInfo['afterConnectFunc'] = None
        self.settings.endGroup()
        return connectionInfo

    def getServicePort(self):
        self.settings.beginGroup('web_service')
        result = forceInt(self.settings.value('port', 7000))
        self.settings.endGroup()
        return result

    def getServiceHost(self):
        self.settings.beginGroup('web_service')
        result = forceString(self.settings.value('host', 'localhost'))
        self.settings.endGroup()
        return result

    def getMiacCode(self):
        return forceStringEx(self.settings.value('miac_code'))

    def getVerbose(self):
        return forceInt(self.settings.value('verbose', 1))

    def getLimit(self):
        return forceInt(self.settings.value('limit', 1000))