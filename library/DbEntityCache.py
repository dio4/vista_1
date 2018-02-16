# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui


class CDbEntityCache:
    _connected = False

    def __init__(self):
        pass

    @classmethod
    def connect(cls):
        if not cls._connected:
            QtCore.QObject.connect(QtGui.qApp, QtCore.SIGNAL('dbConnectionChanged(bool)'), cls.onConnectionChanged)
            cls._connected = True


    @classmethod
    def onConnectionChanged(cls, connected):
        cls.purge()
        cls._connected = False
        QtCore.QObject.disconnect(QtGui.qApp, QtCore.SIGNAL('dbConnectionChanged(bool)'), cls.onConnectionChanged)


    @classmethod
    def purge(cls):
        pass