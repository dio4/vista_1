# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore

from library.DialogBase import CConstructHelperMixin
from library.Utils import forceBool


class CJobTicketReserveMixin(CConstructHelperMixin):
    def __init__(self):
        self.timerProlongReservation = QtCore.QTimer(self)
        self.timerProlongReservation.timeout.connect(self.on_timerProlongReservation_timeout)
        self.timerProlongReservation.setInterval(60000)
        self.reservation = []  # список id резервируемых Job_Ticket

    def isReservedJobTicket(self, id):
        db = QtGui.qApp.db

        query = db.query('SELECT isReservedJobTicket(%s)' % (id))

        if query.next():
            result = forceBool(query.record().value(0))
        else:
            result = False
        return result

    def addJobTicketReservation(self, id, personId='NULL', quotaId='NULL'):
        db = QtGui.qApp.db
        if personId is None:
            personId = 'NULL'
        if quotaId is None:
            quotaId = 'NULL'

        query = db.query('SELECT addJobTicketReservation(%s, %s, %s)' % (id, personId, quotaId))

        if query.next():
            result = forceBool(query.record().value(0))
        else:
            result = False

        if result:
            if not self.reservation:
                self.timerProlongReservation.start()
            self.reservation.append(id)
        return result

    def delJobTicketReservation(self, id, checkReservation=True):
        db = QtGui.qApp.db
        query = db.query('SELECT delJobTicketReservation(%d)' % id)
        if query.next():
            result = forceBool(query.record().value(0))
        else:
            result = False

        if not self.reservation:
            self.timerProlongReservation.stop()
        return result

    def delAllJobTicketReservations(self):
        for id in self.reservation:
            self.delJobTicketReservation(id)
        self.reservation = []

    def getReservedJobTickets(self):
        return self.reservation

    def on_timerProlongReservation_timeout(self):
        db = QtGui.qApp.db
        for id in self.reservation:
            db.query('SELECT checkJobTicketReservation(%d)' % id)
