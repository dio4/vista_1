# -*- coding: utf-8 -*-
# ############################################################################
##
## Copyright (C) 2014 Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtGui
from library.ElectronicQueue.EQTicketModel import CEQTicketViewModel
from library.ElectronicQueue.EQViewerWindow import CEQViewerWindow
from library.Utils import generalConnectionName, forceInt

__author__ = 'atronah'

'''
    author: atronah
    date:   23.10.2014
'''

import re


from PyQt4 import QtCore
from PyQt4 import QtSql


class CEQViewedTypeModel(QtCore.QAbstractTableModel):
    ciName = 0
    ciOffice = 1

    #TODO: atronah: добавить вывод информации об общем числе номерков и числе обработанных
    headerTitles = {ciName : u'Название очереди',
                    ciOffice : u'Кабинет'}

    def __init__(self, db, parent = None):
        super(CEQViewedTypeModel, self).__init__(parent)
        self._db = db
        self._queueTypeIdList = []
        self._modelInfo = {}
        self._waitersLimit = 3


    # --- inderface ---
    def addQueueTypeId(self, queueTypeId):
        if queueTypeId in self._queueTypeIdList:
            return
        row = len(self._queueTypeIdList)
        db = QtGui.qApp.db
        tblQueueType = db.table('rbEQueueType')
        orgStruct = forceInt(db.translate(tblQueueType, tblQueueType['id'], queueTypeId, tblQueueType['orgStructure_id']))
        waitersModel = CEQTicketViewModel(queueTypeId, db=self._db)
        waitersModel.setInProgressDisplayEnabled(False)
        waitersModel.setRowLimit(self._waitersLimit)
        inProgressModelList = []
        #TODO: atronah: добавить проверку на ошибки
        query = QtSql.QSqlQuery(u''' SELECT
                                        OS_A.id AS osId
                                    FROM
                                        OrgStructure_Ancestors AS OS_A
                                    WHERE
                                        OS_A.fullPath RLIKE '[[:<:]]%s[[:>:]]' ''' % waitersModel.baseOrgStructureId(),
                                self._db)
        if orgStruct:
            model = CEQTicketViewModel(queueTypeId, orgStructureId=orgStruct, db=self._db)
            model.setWaitersDisplayEnabled(False)
            inProgressModelList.append(model)
            self.beginInsertRows(QtCore.QModelIndex(), row, row)
            self._queueTypeIdList.append(queueTypeId)
            self._modelInfo[queueTypeId] = {'inProgressModelList': inProgressModelList,
                                            'waitersModel': waitersModel}
            self.endInsertRows()


    def removeRow(self, row):
        if row in xrange(len(self._queueTypeIdList)):
            self.beginRemoveRows(QtCore.QModelIndex(), row, row)
            queueTypeId = self._queueTypeIdList.pop(row)
            modelInfo = self._modelInfo.pop(queueTypeId)
            for model in modelInfo.get('inProgressModelList', []):
                model.stopTimer()
            modelInfo.get('waitersModel').stopTimer()
            self.endRemoveRows()
            return True

        return False


    # --- re-implement ---

    def rowCount(self, parentIndex = QtCore.QModelIndex()):
        return len(self._queueTypeIdList)


    def columnCount(self, parentIndex = QtCore.QModelIndex):
        return 1


    # def flags(self, index):
    #     flags = super(CEQViewedTypeModel, self).flags()
    #     if index.isValid():
    #         row = index.row()
    #         flags |= QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
    #         if row in xrange(len(self._modelList) + 1):
    #             column = index.column()
    #             if column == self.ciName:
    #                 flags |= QtCore.Qt.ItemIsEditable
    #     return flags


    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if section in self.headerTitles.keys():
                return QtCore.QVariant(self.headerTitles[section])
        return super(CEQViewedTypeModel, self).headerData(section, orientation, role)


    def data(self, index, role = QtCore.Qt.DisplayRole):
        if index.isValid():
            row = index.row()
            if row in xrange(len(self._modelInfo)):
                column = index.column()
                queueTypeId = self._queueTypeIdList[row]
                model = self._modelInfo[queueTypeId].get('waitersModel')
                if role == QtCore.Qt.DisplayRole:
                    if column == self.ciName:
                        return QtCore.QVariant(model.queueName())
                    elif column == self.ciOffice:
                        return QtCore.QVariant(model.queueOffice())
        return QtCore.QVariant()


    @QtCore.pyqtSlot(int)
    def setWaitersLimit(self, limit):
        if limit > 0:
            self._waitersLimit = limit
            for info in self._modelInfo:
                model = info.get('waitersModel', None)
                if model:
                    model.setRowLimit(limit)


    def waitersLimit(self):
        return self._waitersLimit


    def waitersModel(self, queueTypeId):
        info = self._modelInfo.get(queueTypeId, None)
        if info:
            return info.get('waitersModel', None)

        return None


    def queueTypeIdList(self):
        return self._queueTypeIdList


    def inProgressModelList(self, queueTypeId):
        info = self._modelInfo.get(queueTypeId, None)
        if info:
            return info.get('inProgressModelList', [])

        return []


    def modelInfoList(self):
        return [self._modelInfo[queueTypeId] for queueTypeId in self._queueTypeIdList]



class CEQViewer(QtCore.QObject):
    instance = None

    changedWaitersLimit = QtCore.pyqtSignal(int)

    def __init__(self, dbConnectionName, parent = None):
        super(CEQViewer, self).__init__(parent)
        self._db = QtSql.QSqlDatabase.database(dbConnectionName)

        try:
            from PyQt4 import QtNetwork
            self._notifyTCPServer = QtNetwork.QTcpServer(self)
        except:
            self._notifyTCPServer = None

        if self._notifyTCPServer:
            self._notifyTCPServer.newConnection.connect(self.onNewNotifyConnection)
        self._notifiers = {} # словарь QTCPSocket объектов

        self._notifierReadyReadMapper = QtCore.QSignalMapper()
        self._notifierReadyReadMapper.mapped.connect(self.onNotifyReadyRead)

        self._notifierDisconnectedMapper = QtCore.QSignalMapper()
        self._notifierDisconnectedMapper.mapped.connect(self.onNotifierDisconnected)

        self._notifyREPattern = re.compile(ur'queueTypeId=(\d+);')

        self._newNotifierIdx = 0


        self._viewedEQTypeModel = CEQViewedTypeModel(self._db, self)

        self._updateModelsTimerId = None
        self._updateTimeout = 1.0

        self._viewerWindow = None

        self._rowCount = 1
        self._columnCount = 1

        self._maxTicketCount = 6

        self._notifyPort = 0


    @classmethod
    def getInstance(cls, dbConnectionName = None):
        if cls.instance is None:
            if not dbConnectionName:
                dbConnectionName = generalConnectionName()
            cls.instance = cls(dbConnectionName)
        return cls.instance


    def viewedEQTypeModel(self):
        return self._viewedEQTypeModel


    @QtCore.pyqtSlot()
    @QtCore.pyqtSlot(int)
    def setAutoUpdateTimeout(self, seconds = None):
        if self._updateModelsTimerId is not None:
            self.killTimer(self._updateModelsTimerId)
        if seconds is None:
            self._updateModelsTimerId = None
        else:
            self._updateModelsTimerId = self.startTimer(int(seconds * 1000))



    def timerEvent(self, event):
        if event.timerId() == self._updateModelsTimerId:
            if self._viewerWindow.isVisible():
                self.updateModels()
            else:
                self.setAutoUpdateTimeout(None)



    def showEnent(self, event):
        self.setAutoUpdateTimeout(self._updateTimeout)
        if self._notifyTCPServer and self._notifyPort:
            self._notifyTCPServer.listen(port = self._notifyPort)


    def hideEvent(self, event):
        self.setAutoUpdateTimeout(None)
        if self._notifyTCPServer and self._notifyTCPServer.isListening():
            self._notifyTCPServer.close()



    def getNewNotifierIdx(self):
        self._newNotifierIdx += 1
        return self._newNotifierIdx


    @QtCore.pyqtSlot()
    def onNewNotifyConnection(self):
        if self._notifyTCPServer:
            tcpSocket = self._notifyTCPServer.nextPendingConnection()
            while tcpSocket:
                self.addNotifier(tcpSocket)
                tcpSocket = self._notifyTCPServer.nextPendingConnection()


    def addNotifier(self, tcpSocket):
        idx = self.getNewNotifierIdx()
        self._notifiers[idx] = tcpSocket

        self._notifierReadyReadMapper.setMapping(tcpSocket, idx)
        tcpSocket.readyRead.connect(self._notifierReadyReadMapper.map)

        self._notifierDisconnectedMapper.setMapping(tcpSocket, idx)
        tcpSocket.disconnected.connect(self._notifierReadyReadMapper.map)



    @QtCore.pyqtSlot(int)
    def onNotifyReadyRead(self, idx):
        if idx in self._notifiers.keys():
            tcpSocket = self._notifiers[idx]
            if not tcpSocket.isReadable():
                return

            notifyMessage = tcpSocket.read(tcpSocket.bytesAvailable())
            self.updateModels([int(queueTypeId) for queueTypeId in self._notifyREPattern.findall(notifyMessage)])


    @QtCore.pyqtSlot(int)
    def onNotifierDisconnected(self, idx):
        if idx in self._notifiers.keys():
            tcpSocket = self._notifiers.pop(idx)
            del tcpSocket



    def updateModels(self, updateIdList = None):
        for queueTypeId in self._viewedEQTypeModel.queueTypeIdList():
            if updateIdList is None or queueTypeId in updateIdList:
                for model in self._viewedEQTypeModel.inProgressModelList(queueTypeId):
                    model.select()
                self._viewedEQTypeModel.waitersModel(queueTypeId).select()



    def rowCount(self):
        return self._rowCount


    @QtCore.pyqtSlot(int)
    def setRowCount(self, rowCount):
        if 0 < rowCount != self._rowCount:
            self._rowCount = rowCount
            if self._viewerWindow is not None:
                self._viewerWindow.setRowCount(self._rowCount)


    def columnCount(self):
        return self._columnCount


    @QtCore.pyqtSlot(int)
    def setColumnCount(self, columnCount):
        if 0 < columnCount != self._columnCount:
            self._columnCount = columnCount
            if self._viewerWindow is not None:
                self._viewerWindow.setColumnCount(self._columnCount)



    @QtCore.pyqtSlot(float)
    def setUpdateTimeout(self, seconds):
        if 0.05 <= seconds < 99.99:
            self._updateTimeout = seconds


    def updateTimeout(self):
        return self._updateTimeout


    @QtCore.pyqtSlot(int)
    def setMaxTicketCount(self, count):
        self._viewedEQTypeModel.setWaitersLimit(count)


    def maxTicketCount(self):
        return self._viewedEQTypeModel.waitersLimit()



    @QtCore.pyqtSlot(int)
    def setNotifyPort(self, port):
        self._notifyPort = port


    def notifyPort(self):
        return self._notifyPort


    @QtCore.pyqtSlot()
    def showViewerWindow(self):
        if self._viewerWindow is None:
            self._viewerWindow = CEQViewerWindow(flags = QtCore.Qt.Dialog)
            self._viewerWindow.setWindowModality(QtCore.Qt.WindowModal)

        self._viewerWindow.clear()
        self._viewerWindow.setRowCount(self._rowCount)
        self._viewerWindow.setColumnCount(self._columnCount)

        for info in self._viewedEQTypeModel.modelInfoList():
            self._viewerWindow.addBlock(info.get('waitersModel'),
                                        info.get('inProgressModelList'))
        self.setAutoUpdateTimeout(self._updateTimeout)
        self._viewerWindow.rearrange()
        self._viewerWindow.show() #TODO: atronah: все блокируется, если вызвать из модального диалога




def main():
    import sys

    sys.exit(0)


if __name__ == '__main__':
    main()