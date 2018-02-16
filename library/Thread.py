#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore
import json  # pickle под ContOS не заработал

from library.Utils import forceString


class CThreadSingleApplication(QtCore.QThread):
    error = QtCore.pyqtSignal(str)

    def __init__(self, serverName, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.serverName = serverName
        self.hasRight = False
        self.isServer = False

    def checkConnection(self):
        from PyQt4 import QtNetwork

        self.socket = QtNetwork.QLocalSocket(self)
        self.connect(self.socket, QtCore.SIGNAL('connected()'), self.onSocketConnected)
        self.socket.connectToServer(self.serverName)
        if not self.socket.waitForConnected(1000):
            self.isServer = True

        if self.isServer:
            self.server = QtNetwork.QLocalServer()
            self.connect(self.server, QtCore.SIGNAL('newConnection()'), self.onNewConnection)
            QtNetwork.QLocalServer.removeServer(self.serverName)

    def run(self):
        if self.isServer:
            self.server.listen(self.serverName)

    def setHasRight(self, value):
        self.hasRight = value

    @QtCore.pyqtSlot()
    def onNewConnection(self):
        try:
            if self.server.hasPendingConnections():
                self.serverSocket = self.server.nextPendingConnection()
                self.sendMessage()
        except:
            self.error.emit('Error on sending message from %s' % self.serverName)

    def sendMessage(self):
        buf = QtCore.QBuffer()
        buf.open(QtCore.QBuffer.ReadWrite)
        out = QtCore.QDataStream(buf)
        out.setVersion(QtCore.QDataStream.Qt_4_4)

        out << QtCore.QByteArray(json.dumps(self.hasRight))
        self.serverSocket.write(buf.data().data())
        self.serverSocket.flush()

    @QtCore.pyqtSlot()
    def onSocketConnected(self):
        try:
            if not self.socket.waitForReadyRead(1000):
                self.hasRight = False
                self.error.emit('Time out of waiting massage from %s' % self.serverName)
            else:
                self.receiveMessage()
        except:
            self.hasRight = True
            self.error.emit('Error on receiving message from %s' % self.serverName)
        finally:
            self.emit(QtCore.SIGNAL('hasRight(bool)'), self.hasRight)

    def receiveMessage(self):
        ins = QtCore.QDataStream(self.socket)
        ins.setVersion(QtCore.QDataStream.Qt_4_4)
        self.socket.bytesAvailable()

        result = QtCore.QByteArray()
        ins >> result
        self.hasRight = json.loads(forceString(result))
