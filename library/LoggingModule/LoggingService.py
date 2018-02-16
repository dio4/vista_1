# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore
from suds.sax.element import Element, os
import config
import sys
from library.Utils import forceString, forceInt, forceDateTime, toVariant, forceDate
from library.database import connectDataBaseByInfo
from wsgiref.simple_server import make_server
import soaplib
from soaplib.core.service import rpc, DefinitionBase
from soaplib.core.model.primitive import String, Integer, DateTime
from soaplib.core.server import wsgi
from soaplib.core.model.clazz import Array, ClassModel

class Data():
    def __init__(self):
        if os.name == 'nt':
            app = QtCore.QCoreApplication(sys.argv)
        self.db = connectDataBaseByInfo(config.connectionInfo)

    def saveLog(self, tableName, version, relegateMO, values):
        try:
            tbl = self.db.table(tableName)
            newLog = tbl.newRecord()
            newLog.setValue('createDatetime', toVariant(QtCore.QDateTime.currentDateTime()))
            newLog.setValue('version', toVariant(version))
            newLog.setValue('relegateMO', toVariant(relegateMO))
            for v in values:
                newLog.setValue(forceString(v.ColumnName), forceString(v.Value))
            if self.db.insertRecord(tbl, newLog):
                return True
            else:
                return False
        except:
            return False


class Values(ClassModel):
    ColumnName = String
    Value = String

class Log(ClassModel):
    tableName = String
    version = String
    relegateMO = String
    values = Array(Values)

class SendLogResponce(ClassModel):
    Result = Integer
    Error = String

class CService(DefinitionBase):
    @rpc(Log, _returns=SendLogResponce)
    def SendLog(self, Log=None):
        self.data = Data()
        tableName = Log.tableName
        version = Log.version
        relegateMO = Log.relegateMO
        values = Log.values
        if self.data.saveLog(forceString(tableName), forceString(version), forceString(relegateMO), values):
            message = SendLogResponce()
            message.Result = 1
            message.Error = ''
            return message
        else:
            message = SendLogResponce()
            message.Result = 0
            message.Error = u'При записи лога возникли ошибки'
            return message

if __name__ == '__main__':
    try:
        soap_application = soaplib.core.Application([CService], tns='http://tempuri.org/')
        wsgi_application = wsgi.Application(soap_application)
        server = make_server('127.0.0.1', 7789, wsgi_application)
        server.serve_forever()
    except ImportError:
        print "Error: example server code requires Python >= 2.5"