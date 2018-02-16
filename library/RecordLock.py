#!/usr/bin/env python
# -*- coding: utf-8 -*-
from library.Utils import *


class CRecordLockMixin:
    def __init__(self):
        self._appLockId = None
        self._timerProlongLock = QTimer(self)
        self.timerProlongLock = QTimer(self)
        self.timerProlongLock.setObjectName('timerProlongLock')
        self._timerProlongLock.setInterval(60000) # 1 раз в минуту
        QObject.connect(self._timerProlongLock, QtCore.SIGNAL('timeout()'), self.prolongLock)

    def tryLock(self, tableName, id, propertyIndex = 0):
        isSuccess = False
        appLockId = None
        lockInfo = None
        db = QtGui.qApp.db
        personId = str(QtGui.qApp.userId) if QtGui.qApp.userId else 'NULL'
        db.query('CALL getAppLock_(%s, %d, %d, %s, %s, @res)' % (
            quote(tableName), id, propertyIndex, personId, quote(QtGui.qApp.hostName)
        ))
        query = db.query('SELECT @res')
        if query.next():
            record = query.record()
            s = forceString(record.value(0)).split()
            if len(s)>1:
                isSuccess = int(s[0])
                appLockId = int(s[1])
        if not isSuccess and appLockId:
            lockRecord = db.getRecord('AppLock', ['lockTime', 'person_id', 'addr'], appLockId)
            if lockRecord:
                lockTime = forceDateTime(lockRecord.value('lockTime'))
                personId = forceRef(lockRecord.value('person_id'))
                personName = forceString(
                    db.translate('vrbPersonWithSpeciality', 'id', personId, 'name')
                ) if personId else u'аноним'
                addr = forceString(lockRecord.value('addr'))
                lockInfo = lockTime, personName, addr
        return isSuccess, appLockId, lockInfo

    def lock(self, tableName, id, propertyIndex = 0):
        # return True
        if not id or QtGui.qApp.disableLock:
            return True
        while True:
            ok, lockResult = QtGui.qApp.call(self, self.tryLock, (tableName, id, propertyIndex))
            if ok:
                isSuccess, appLockId, lockInfo = lockResult
            else:
                return False
            if isSuccess:
                self._appLockId = appLockId
                self._timerProlongLock.start()
                return True
            if lockInfo:
                message = u'Данные заблокированы %s\nпользователем %s\nс компьютера %s' % (
                    forceString(lockInfo[0]),
                    lockInfo[1],
                    lockInfo[2])
            else:
                message = u'Не удалось установить блокировку'
            if self.notRetryLock(self.parent() if callable(self.parent) else self.parent, message):
                return False

    def notRetryLock(self, obj, message):
        return QtGui.QMessageBox.critical(
            obj,
            u'Ограничение совместного доступа к данным',
            message,
            QtGui.QMessageBox.Retry|QtGui.QMessageBox.Cancel,
            QtGui.QMessageBox.Retry
        ) == QtGui.QMessageBox.Cancel

    def releaseLock(self):
        if self._appLockId:
            self._timerProlongLock.stop()
            db = QtGui.qApp.db
            db.query('CALL ReleaseAppLock(%d)' % (self._appLockId))
            self._appLockId = None

    def prolongLock(self):
        if self._appLockId:
            db = QtGui.qApp.db
            db.query('CALL ProlongAppLock(%d)' % (self._appLockId))
