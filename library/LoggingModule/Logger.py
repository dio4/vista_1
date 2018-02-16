# -*- coding: utf-8 -*-
import Utils
from PyQt4 import QtGui, QtCore

loginId = 0  # Для хранения номера сессии
loggerDbName = 'logger'  # Название базы логера
disable = False


# Получение ид сессии
def getLoginId():
    if disable: return
    db = QtGui.qApp.db
    stmt = u'SELECT id FROM %s WHERE person_id = %s ORDER BY id DESC LIMIT 1' % \
           (getLoggerDbName() + u".Login",
            QtGui.qApp.userId)
    id = db.query(stmt)
    id.next()
    return id.value(0).toString()


# Авторизация
# Запись успешной авторизации
def loginInClient(**kwargs):
    if disable: return
    Utils.prepareKwargsLogin(kwargs)
    db = QtGui.qApp.db
    stmt = u"INSERT INTO %s (%s) VALUES (%s)" % \
           (getLoggerDbName() + u".Login",
            u", ".join(unicode(k) for k in kwargs.keys()),
            u", ".join("'" + unicode(v) + "'" for v in kwargs.values())
            )
    db.query(stmt)


# Закрытие сессии
def logoutInClient():
    if disable:
        return
    global loginId
    if loginId:
        db = QtGui.qApp.db
        stmt = u"UPDATE %s SET end_date='%s' WHERE id=%s" % \
               (getLoggerDbName() + u".Login", str(QtCore.QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss')), loginId)
        db.query(stmt)
        loginId = 0

################


# Запись открытия окон и вкладок
def logWindowAccess(**kwargs):
    """
    :argument   :   Utils.WINDOW_ACCESS_TABLE_COLUMNS
    """
    if disable: return
    Utils.prepareKwargsWindowAccess(kwargs)

    db = QtGui.qApp.db
    stmt = u"INSERT INTO %s (%s) VALUES (%s)" % \
           (getLoggerDbName() + u".WindowAccess",
            u", ".join(unicode(k) for k in kwargs.keys()),
            u", ".join("'" + unicode(v) + "'" for v in kwargs.values()))
    db.query(stmt)


# Запись выбора клиентов
def logClientChoice(**kwargs):
    if disable: return
    Utils.prepareKwargsClientChoice(kwargs)

    db = QtGui.qApp.db
    stmt = u"INSERT INTO %s (%s) VALUES (%s)" % \
           (getLoggerDbName() + u'.ClientChoice',
            u", ".join(unicode(k) for k in kwargs.keys()),
            u", ".join("'" + unicode(v) + "'" for v in kwargs.values()))
    db.query(stmt)


# Запись выбора обращений
def logEventChoice(**kwargs):
    if disable: return
    Utils.prepareKwargsEventChoice(kwargs)

    db = QtGui.qApp.db
    stmt = u"INSERT INTO %s (%s) VALUES (%s)" % \
           (getLoggerDbName() + u'.EventChoice',
            u", ".join(unicode(k) for k in kwargs.keys()),
            u", ".join("'" + unicode(v) + "'" for v in kwargs.values()))
    db.query(stmt)


# Запись сформированного отчета
def logReport(**kwargs):
    if disable: return
    Utils.prepareKwargsReports(kwargs)

    db = QtGui.qApp.db
    stmt = u"INSERT INTO %s (%s) VALUES (%s)" % \
           (getLoggerDbName() + u'.Reports', u", ".join(unicode(k) for k in kwargs.keys()),
            u", ".join("'" + unicode(v) + "'" for v in kwargs.values()))
    db.query(stmt)


# Запись отправленного пакета
def logPackages(**kwargs):
    if disable: return
    Utils.prepareKwargsPackages(kwargs)
    db = QtGui.qApp.db
    stmt = u"INSERT INTO %s (%s) VALUES (%s)" % \
           (getLoggerDbName() + u'.SendPackages',
            u", ".join(unicode(k) for k in kwargs.keys()),
            u", ".join("'" + unicode(v) + "'" for v in kwargs.values()))
    db.query(stmt)


# Запись удаленного двойника
def logDeletedDouble(primary, duplicate):
    QtGui.qApp.db.query(u'''INSERT INTO {tbl} (primary_client_id, duplicate_id)
                            VALUES ('{primary}', '{duplicate}')'''.format(
        tbl=(getLoggerDbName() + '.ControlDoublesLog'),
        primary=primary,
        duplicate=duplicate
    ))


# Проверка на существующий пакет
def checkAlreadyPackage(eventId, method):
    if disable: return
    db = QtGui.qApp.db
    tmpRec = db.getRecordEx(getLoggerDbName() + u'.SendPackages', 'id', "event_id = %s AND method = '%s' AND status = 1" % (eventId, method))
    if tmpRec:
        return True
    else:
        return False


# Установка статуса если пакет успешно отправлен
def updateStatusLogPackages(eventId, method):
    if disable: return
    db = QtGui.qApp.db
    tmpRec = db.getRecordEx(getLoggerDbName() + u'.SendPackages', '*', "event_id = %s AND method = %s" % (eventId, method))
    if tmpRec:
        tmpRec.setValue('status', 1)
        db.updateRecord(getLoggerDbName(), tmpRec)


# Обновление данных при открытии/записи
def updateClient(clientId):
    if disable: return
    db = QtGui.qApp.db
    stmt = u"UPDATE %s SET isOpened = 1 WHERE login_id = %s AND client_id = %s LIMIT 1" % \
           (getLoggerDbName() + u'.ClientChoice', loginId, clientId)
    db.query(stmt)


def updateEvent(eventId):
    if disable: return
    db = QtGui.qApp.db
    stmt = u"UPDATE %s SET isOpened = 1 WHERE login_id = %s AND event_id = %s LIMIT 1" % \
           (getLoggerDbName() + u'.EventChoice', loginId, eventId)
    db.query(stmt)


def updateReport(rep_name):
    if disable: return
    db = QtGui.qApp.db
    stmt = u"UPDATE %s SET isPrinted = 1 WHERE login_id = %s AND report_name= '%s' LIMIT 1" % \
           (getLoggerDbName() + u'.Reports', loginId, rep_name)
    db.query(stmt)


# Задание используемой бд
def setLoggerDbName(name):
    global loggerDbName
    loggerDbName = name


def getLoggerDbName():
    return loggerDbName
