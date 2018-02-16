# -*- coding: utf-8 -*-
import os
import socket

from PyQt4 import QtGui, QtCore

from library.Utils import toVariant, forceString


class Logger():
    def __init__(self, name):
        self.name = name
        self.loggerDbName = 'logger'
        self.db = QtGui.qApp.db
        self.logPath = QtGui.qApp.logDir

    #Логирование в бд
    def insertDBLog(self, **kwargs):
        if self.name:
            table = self.db.table(self.name)
            self.__prepareKwargs(table, kwargs)
            if table:
                newRec = table.newRecord()
                for k in kwargs.keys():
                    newRec.setValue(k, toVariant("'" + forceString(kwargs[k]) + "'"))
                try:
                    self.db.insertRecord(table, newRec)
                except Exception:
                    QtGui.QMessageBox.information(None, u'Ошибка', Exception.message)

    #Логирование в файл
    def insertFileLog(self, **kwargs):
        if self.name:
            path = os.path.join(self.logPath, self.name)
            file = open(path, 'a')
            file.write(u'\n' + forceString(QtCore.QDateTime.currentDateTime()) + u'\n')
            for k in kwargs.keys():
                file.write(forceString(k) + u'=' + unicode(kwargs[k]) + u'\n\n')
            file.close()

    #Возвращает файл для записи в него трейса соапа
    def getSoapLogFile(self):
        if self.name:
            path = os.path.join(QtGui.qApp.logDir, self.name)
            try:
                file = open(path, 'a')
                return file
            except Exception:
                print Exception.message


    #Заполнение полей в таблице умолчаниями
    def __prepareKwargs(self, table, kwargs):
        if table.hasField('date') and not 'date' in kwargs:
            kwargs['date'] = unicode(QtCore.QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss'))
        if table.hasField('organisation_id') and not 'organisation_id' in kwargs:
            kwargs['organisation_id'] = QtGui.qApp.currentOrgId()
        if table.hasField('start_date') and not 'start_date' in kwargs:
            kwargs['start_date'] = unicode(QtCore.QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss'))
        if table.hasField('person_id') and not 'person_id' in kwargs:
            kwargs['person_id'] = unicode(QtGui.qApp.userId)
        if table.hasField('pc_name') and not 'pc_name' in kwargs:
            kwargs['pc_name'] = socket.gethostname()
        if table.hasField('lpu') and not 'lpu' in kwargs:
            kwargs['lpu'] = QtGui.qApp.currentOrgId()
        if table.hasField('createDateTime') and not 'createDateTime' in kwargs:
            kwargs['createDateTime'] = unicode(QtCore.QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss'))
        if table.hasField('createPerson') and not 'createPerson' in kwargs:
            kwargs['createPerson'] = unicode(QtGui.qApp.userId)
        if table.hasField('client_id') and not 'client_id' in kwargs:
            kwargs['client_id'] = QtGui.qApp.currentClientId()

    def getLoggerDbName(self):
        return self.loggerDbName

    def setLoggerDbName(self, name):
        self.loggerDbName = name