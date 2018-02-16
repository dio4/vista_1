# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
#############################################################################
from library.Utils import *

class CRecordListLockMixin:
    def __init__(self):
        self._appLockIdList = []
        self._timerProlongLock = QTimer(self)
        self._timerProlongLock.setInterval(60000) # 1 раз в минуту
        QObject.connect(self._timerProlongLock, QtCore.SIGNAL('timeout()'), self.prolongLock)

    def tryLock(self, tableName, id, propertyIndex=0):
        isSuccess = False
        appLockId = None
        lockInfo = None
        db = QtGui.qApp.db
        personId = str(QtGui.qApp.userId) if QtGui.qApp.userId else 'NULL'
        db.query('CALL getAppLock_(%s, %d, %d, %s, %s, @res)' % (quote(tableName), id, propertyIndex, personId, quote(QtGui.qApp.hostName)))
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
                personName = forceString(db.translate('vrbPersonWithSpeciality', 'id', personId, 'name')) if personId else u'аноним'
                addr = forceString(lockRecord.value('addr'))
                lockInfo = lockTime, personName, addr
        return isSuccess, appLockId, lockInfo

    def lockList(self, tableName, idList, propertyIndex = 0):
        if not idList or QtGui.qApp.disableLock:
            return True
        while True:
            ok, lockResult = QtGui.qApp.call(self, self.tryLock, (tableName, idList[len(self._appLockIdList)], propertyIndex))
            if ok:
                isSuccess, appLockId, lockInfo = lockResult
            else:
                self.releaseLockList()
                return False
            if isSuccess:
                self._appLockIdList.append(appLockId)
                if len(self._appLockIdList) == len(idList):
                    self._timerProlongLock.start()
                    return True
                else:
                    continue
            if lockInfo:
                message = u'Данные заблокированы %s\nпользователем %s\nс компьютера %s' % (
                    forceString(lockInfo[0]),
                    lockInfo[1],
                    lockInfo[2])
            else:
                message = u'Не удалось установить блокировку'
            if self.notRetryLock(self.parent() if callable(self.parent) else self.parent, message):
                self.releaseLockList()
                return False

    def notRetryLock(self, obj, message):
        result = QtGui.QMessageBox.critical(obj,
                                          u'Ограничение совместного доступа к данным',
                                          message,
                                          QtGui.QMessageBox.Retry|QtGui.QMessageBox.Cancel,
                                          QtGui.QMessageBox.Retry
                                         ) == QtGui.QMessageBox.Cancel
        if not result:
            self.prolongLock()
        return result

    def releaseLockList(self):
        if self._appLockIdList:
            self._timerProlongLock.stop()
            db = QtGui.qApp.db
            for appLockId in self._appLockIdList:
                db.query('CALL ReleaseAppLock(%d)' % appLockId)
            self._appLockIdList = []

    def prolongLock(self):
        if self._appLockIdList:
            db = QtGui.qApp.db
            for appLockId in self._appLockIdList:
                db.query('CALL ProlongAppLock(%d)' % appLockId)
