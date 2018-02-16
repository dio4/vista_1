# -*- coding: utf-8 -*-
import logging
from PyQt4 import QtGui, QtCore
from Ui_Appointment import Ui_FrmAppointment
from library.DialogBase import CDialogBase
from library.Utils import forceInt, forceString, toVariant
from services import NetricaAppointment

class Appoinment(CDialogBase, Ui_FrmAppointment):
    def __init__(self, parent, refNumber=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.refNumber = refNumber
        self.db = QtGui.qApp.db
        self.cmbReferral.setTable('Referral', 'number')
        self.cmbReferral.setFilter('deleted = 0 AND isSend = 1 AND isCancelled = 0 AND client_id = %s' % QtGui.qApp.currentClientId())
        # self.cmbReferral.sizeHint()
        self.responce = {}
        self.idLpu = None
        self.idPat = None
        self.setDefaults()
        self.setIsDirty(False)
        logging.basicConfig(filename='uo.log', format='%(asctime)-15s %(clientip)s %(user)-8s %(message)s')
        self.log = logging.getLogger('uoservice').setLevel(logging.INFO)


    def setDefaults(self):
        tableReferral = self.db.table('Referral')
        if self.refNumber:
            recReferral = self.db.getRecordEx(tableReferral, tableReferral['id'], tableReferral['number'].eq(forceString(self.refNumber)))
            if recReferral:
                referral_id = forceInt(recReferral.value('id'))
                self.cmbReferral.setValue(referral_id)

    def getTickets(self, referralId):
        tableReferral = self.db.table('Referral')
        recReferral = self.db.getRecordEx(tableReferral, '*', tableReferral['id'].eq(referralId))
        service = NetricaAppointment()
        responce = service.getTickets(recReferral)
        if responce:
            self.responce = {}
            if responce.ErrorList:
                QtGui.QMessageBox.information(self, u'Ошибка', forceString(responce.ErrorList.Error[0].ErrorDescription))
                return
            self.idLpu = responce.IdLpu
            self.idPat = responce.IdPat
            for s in responce.ListSpeciality.Speciality2:
                self.responce[forceString(s.NameSpeciality)] = {}
                for d in s.ListDoctor.Doctor2:
                    ticketsList = []
                    if d.ListAppointment:
                        for a in sorted(d.ListAppointment.Appointment):
                                ticketsList.append((forceString(a.VisitStart), forceString(a.IdAppointment)))
                        self.responce[forceString(s.NameSpeciality)][forceString(d.Name)] = ticketsList


    @QtCore.pyqtSlot(int)
    def on_cmbReferral_currentIndexChanged(self, index):
        self.cmbSpeciality.clear()
        self.cmbTickets.clear()
        self.cmbDoctor.clear()
        self.getTickets(self.cmbReferral.value())
        if self.responce:
            self.cmbSpeciality.addItems(self.responce.keys())

    @QtCore.pyqtSlot(int)
    def on_cmbSpeciality_currentIndexChanged(self, index):
        self.cmbTickets.clear()
        self.cmbDoctor.clear()
        if self.responce:
            if self.responce.has_key(forceString(self.cmbSpeciality.currentText())):
                self.cmbDoctor.addItems(self.responce[forceString(self.cmbSpeciality.currentText())].keys())


    @QtCore.pyqtSlot(int)
    def on_cmbDoctor_currentIndexChanged(self, index):
        self.cmbTickets.clear()
        if self.responce and self.responce.has_key(forceString(self.cmbSpeciality.currentText())) and self.responce[forceString(self.cmbSpeciality.currentText())].has_key(forceString(self.cmbDoctor.currentText())):
            ticketsList = [ticketValue[0] for ticketValue in self.responce[forceString(self.cmbSpeciality.currentText())][forceString(self.cmbDoctor.currentText())]]
            tics = []
            for ticket in ticketsList:
                tics.append(ticket)
            self.cmbTickets.addItems(sorted(tics))



    @QtCore.pyqtSlot()
    def on_btnAppoint_clicked(self):
        self.btnAppoint.setEnabled(False)
        self.btnAppoint.setText(u'Идет запись...')
        ticket = self.cmbTickets.currentText()
        logging.info(u'Регистрация номерка')
        if self.responce and self.responce.has_key(forceString(self.cmbSpeciality.currentText())) and self.responce[forceString(self.cmbSpeciality.currentText())].has_key(forceString(self.cmbDoctor.currentText())):
            service = NetricaAppointment()
            tableReferral = self.db.table('Referral')
            recReferral = self.db.getRecordEx(tableReferral, '*',
                                              tableReferral['number'].eq(forceString(self.cmbReferral.currentText())))
            for ticketValue in self.responce[forceString(self.cmbSpeciality.currentText())][forceString(self.cmbDoctor.currentText())]:
                if forceString(ticketValue[0]) == forceString(ticket):
                    responce = service.SetAppointment(ticketValue[1],
                                                      forceString(self.idLpu),
                                                      forceString(self.idPat), recReferral)
                    if responce:
                        if responce.ErrorList:
                            if responce.ErrorList and responce.ErrorList.Error[0]:
                                QtGui.QMessageBox.information(None, u'Ошибка', forceString(
                                    responce.ErrorList.Error[0].ErrorDescription))
                                self.btnAppoint.setText(u'Записать')
                                return
                            return
                        self.btnAppoint.setText(u'Успешно')
                        jsonTicketInfo = u'{doctor : %s, ticketId : %s, datetime : %s}' % (forceString(self.cmbDoctor.currentText()), forceString(ticketValue[1]), forceString(ticketValue[0]))
                        recReferral.setValue('ticketNumber', toVariant(jsonTicketInfo))
                        self.db.updateRecord(tableReferral, recReferral)
                        QtGui.QMessageBox.information(None, u'Успешно', u'Талончик успешно забронирован')
                        logging.info(u'Номерок %s успешно забронирован' % jsonTicketInfo)
                    else:
                        self.btnAppoint.setEnabled(True)
                        self.btnAppoint.setText(u'Записать')
                        QtGui.QMessageBox.warning(None, u'Ошибка', u'При бронировании талончика возникла ошибка')
        else:
            self.getTickets(self.cmbReferral.value())
            self.on_btnAppoint_clicked()
            logging.warning(u'Повторная попытка записи')