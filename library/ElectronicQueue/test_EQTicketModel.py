# -*- coding: utf-8 -*-
# ############################################################################
##
## Copyright (C) 2014 Vista Software. All rights reserved.
##
#############################################################################

__author__ = 'atronah'

'''
    author: atronah
    date:   19.10.2014
'''


import unittest
import sys

from PyQt4 import QtCore, QtSql


from EQTicketModel import CEQTicketControlModel



def initTestDatabase(connectionName = 'unittest'):
    hostName = '192.168.0.3'
    port = 3306
    databaseName = 'b15'
    userName = 'dbuser'
    userPassword = 'dbpassword'

    db = QtSql.QSqlDatabase.addDatabase('QMYSQL', connectionName)
    db.setHostName(hostName)
    db.setPort(port)
    db.setDatabaseName(databaseName)
    db.setUserName(userName)
    db.setPassword(userPassword)
    db.open()
    return db



class TestEqTicketModel(unittest.TestCase):
    app = None


    queueTypeId = 1


    def setUp(self):
        self.app = QtCore.QCoreApplication(sys.argv)

        initTestDatabase()




    def test_GeneralTest(self):
        class SignalHandler(QtCore.QObject):
            def __init__(self, model, parent = None):
                super(SignalHandler, self).__init__(parent)

                self._model = model
                model.prevValueChanged.connect(self.onPrevValueChanged)
                model.currentValueChanged.connect(self.onCurrentValueChanged)
                model.nextValueChanged.connect(self.onNextValueChanged)
                model.queueChanged.connect(self.onQueueChanged)

                self.prev = QtCore.QString('')
                self.curr = QtCore.QString('')
                self.next = QtCore.QString('')

            def printState(self, msg):
                pass

            @QtCore.pyqtSlot(int, QtCore.QString)
            def onPrevValueChanged(self, queueTypeId, value):
                self.prev = value
                self.printState('prev changed: ')

            @QtCore.pyqtSlot(int, QtCore.QString)
            def onCurrentValueChanged(self, queueTypeId, value):
                self.curr = value
                self.printState('curr changed: ')

            @QtCore.pyqtSlot(int, QtCore.QString)
            def onNextValueChanged(self, queueTypeId, value):
                self.next = value
                self.printState('next changed: ')

            @QtCore.pyqtSlot(int)
            def onQueueChanged(self, queueTypeId):
                self.printState('>> queue changed: ')



        db = QtSql.QSqlDatabase.database('unittest')
        if not db.isOpen():
            db.open()
        prepareQuery = QtSql.QSqlQuery(QtCore.QString("""
                                                        DELETE FROM `EQueueTicket` WHERE queue_id = %s;
                                                        INSERT INTO `EQueueTicket` (`queue_id`, `status`, `idx`, `value`) VALUES ('1', '0', '0', '0-reserved');
                                                        INSERT INTO `EQueueTicket` (`queue_id`, `status`, `idx`, `value`) VALUES ('1', '1', '1', '1');
                                                        INSERT INTO `EQueueTicket` (`queue_id`, `status`, `idx`, `value`) VALUES ('1', '1', '2', '2');
                                                        INSERT INTO `EQueueTicket` (`queue_id`, `status`, `idx`, `value`) VALUES ('1', '1', '3', '3');
                                                        INSERT INTO `EQueueTicket` (`queue_id`, `status`, `idx`, `value`) VALUES ('1', '4', '4', '4-completed');
                                                        INSERT INTO `EQueueTicket` (`queue_id`, `status`, `idx`, `value`) VALUES ('1', '1', '5', '5');
                                                        """ % self.queueTypeId),
                                       db)
        self.assertFalse(prepareQuery.lastError().isValid(), 'prepareQuery lastError')
        del prepareQuery #TODO: atronah: если эту строку убрать, то будет магия с "unable to find table `EQueueTicket`"


        model = CEQTicketControlModel(self.queueTypeId, db)
        signalHandler = SignalHandler(model)
        model.select()

        self.assertEqual(signalHandler.prev, QtCore.QString(''))
        self.assertEqual(signalHandler.curr, QtCore.QString(''))
        self.assertEqual(signalHandler.next, QtCore.QString('1'))

        model.moveToNext()
        self.assertEqual(signalHandler.prev, QtCore.QString(''))
        self.assertEqual(signalHandler.curr, QtCore.QString('1'))
        self.assertEqual(signalHandler.next, QtCore.QString('2'))

        model.moveToNext()
        self.assertEqual(signalHandler.prev, QtCore.QString('1'))
        self.assertEqual(signalHandler.curr, QtCore.QString('2'))
        self.assertEqual(signalHandler.next, QtCore.QString('3'))

        model.moveToNext()
        self.assertEqual(signalHandler.prev, QtCore.QString('2'))
        self.assertEqual(signalHandler.curr, QtCore.QString('3'))
        self.assertEqual(signalHandler.next, QtCore.QString('5'))

        model.moveToNext()
        self.assertEqual(signalHandler.prev, QtCore.QString('3'))
        self.assertEqual(signalHandler.curr, QtCore.QString('5'))
        self.assertEqual(signalHandler.next, QtCore.QString(''))

        model.moveToPrev()
        self.assertEqual(signalHandler.prev, QtCore.QString('2'))
        self.assertEqual(signalHandler.curr, QtCore.QString('3'))
        self.assertEqual(signalHandler.next, QtCore.QString(''))

        model.moveToPrev()
        self.assertEqual(signalHandler.prev, QtCore.QString('1'))
        self.assertEqual(signalHandler.curr, QtCore.QString('2'))
        self.assertEqual(signalHandler.next, QtCore.QString(''))

        model.moveToPrev()
        self.assertEqual(signalHandler.prev, QtCore.QString(''))
        self.assertEqual(signalHandler.curr, QtCore.QString('1'))
        self.assertEqual(signalHandler.next, QtCore.QString(''))



    # def tearDown(self)



def main():
    unittest.main()


if __name__ == '__main__':
    main()