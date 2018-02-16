# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################


"""
class for preferences
"""

from PyQt4          import QtGui
from library.Utils  import forceBool, forceString, toVariant, getPref, setPref

from FileService_client import FileServiceLocator, IFileService_ServiceReady_InputMessage


class CMIACExchangePreferences(object):
    defaultPostBoxName = u'Поликлиника *\\received'

    def __init__(self):
        preferences = getPref(QtGui.qApp.preferences.appPrefs, 'MIACExchange_Stattalons', {})
        self.address = forceString(getPref(preferences, 'address', '')) or FileServiceLocator.BasicHttpBinding_IFileService_address
        self.postBoxName = forceString(getPref(preferences, 'postBoxName', '')) or CMIACExchangePreferences.defaultPostBoxName
        self.compress = forceBool(getPref(preferences, 'compress', True))
        self.sendByDefault = forceBool(getPref(preferences, 'sendByDefault', False))

    def store(self):
        preferences = {}
        setPref(preferences, 'address',       toVariant(self.address))
        setPref(preferences, 'postBoxName',   toVariant(self.postBoxName))
        setPref(preferences, 'compress',      toVariant(self.compress))
        setPref(preferences, 'sendByDefault', toVariant(self.sendByDefault))
        setPref(QtGui.qApp.preferences.appPrefs, 'MIACExchange_Stattalons', preferences)

    def isValid(self):
        return self.address and self.postBoxName != CMIACExchangePreferences.defaultPostBoxName and self.test()

    def test(self, address=None):
        try:
            loc = FileServiceLocator()
            port = loc.getBasicHttpBinding_IFileService(address or self.address)
            result = port.ServiceReady(IFileService_ServiceReady_InputMessage())
            return result.ServiceReadyResult
        except:
            return False