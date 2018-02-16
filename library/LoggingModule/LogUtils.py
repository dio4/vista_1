# -*- coding: utf-8 -*-


from PyQt4 import QtGui, QtCore
from suds.client import Client

from library.Utils import forceString


class LoggerExchange():
    def __init__(self):
        self.api = Client('http://127.0.0.1:7789/?wsdl')

    def sendLog(self, tableName, version, relegateMO, **kwargs):
        """
        :param tableName: имя таблицы в базу logger
        :param version: версия обмена
        :param relegateMO: Инфис код МО
        :param kwargs: перечень названий колонок и значений (напр.: client_id = 1)
        :return: Result(Integer) (1 - успешно || 0 - не записано), Error(String) - текстовое описание ошибки
        """

        log = self.api.factory.create('ns0:Log')
        log.tableName = forceString(tableName)
        log.version = forceString(version)
        log.relegateMO = forceString(relegateMO)
        log.values = self.api.factory.create('ns0:ValuesArray')
        for k in kwargs.keys():
            value = self.api.factory.create('ns0:Values')
            value.ColumnName = k
            value.Value = kwargs[k]
            log.values.Values.append(value)
        result = self.api.service.SendLog(log)
        return result