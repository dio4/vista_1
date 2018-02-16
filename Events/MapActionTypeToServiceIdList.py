# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

class CMapActionTypeIdToServiceIdList:
    #def __init__(self):
    mapActionTypeIdToServiceIdList = {}
    _connected = False

    @classmethod
    def connect(cls):
        if not cls._connected:
            QtCore.QObject.connect(QtGui.qApp, QtCore.SIGNAL('dbConnectionChanged(bool)'), cls.onConnectionChanged)
            cls._connected = True

    @classmethod
    def getActionTypeServiceIdList(cls, actionTypeId, financeId):
        cls.connect()
        key = (actionTypeId, financeId)
        result = cls.mapActionTypeIdToServiceIdList.get(key, False)
        if result == False:
            db = QtGui.qApp.db
            table = db.table('ActionType_Service')
            result = db.getIdList(table,
                                          idCol='service_id',
                                          where=[table['master_id'].eq(actionTypeId),
                                                 table['finance_id'].eq(financeId),
                                                 table['service_id'].isNotNull()])
            if not result:
                result = db.getIdList(table,
                                          idCol='service_id',
                                          where=[table['master_id'].eq(actionTypeId),
                                                 table['finance_id'].isNull(),
                                                 table['service_id'].isNotNull()])
            cls.mapActionTypeIdToServiceIdList[key] = result
        return result

    @classmethod
    def onConnectionChanged(cls, connected):
        cls.reset()
        cls._connected = False
        QtCore.QObject.disconnect(QtGui.qApp, QtCore.SIGNAL('dbConnectionChanged(bool)'), cls.onConnectionChanged)


    @classmethod
    def reset(cls):
        cls.mapActionTypeIdToServiceIdList = {}

