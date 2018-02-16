# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Appointment.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_FrmAppointment(object):
    def setupUi(self, FrmAppointment):
        FrmAppointment.setObjectName(_fromUtf8("FrmAppointment"))
        FrmAppointment.resize(155, 221)
        self.gridLayout = QtGui.QGridLayout(FrmAppointment)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.btnAppoint = QtGui.QPushButton(FrmAppointment)
        self.btnAppoint.setObjectName(_fromUtf8("btnAppoint"))
        self.gridLayout.addWidget(self.btnAppoint, 8, 0, 1, 1)
        self.lblReferral = QtGui.QLabel(FrmAppointment)
        self.lblReferral.setObjectName(_fromUtf8("lblReferral"))
        self.gridLayout.addWidget(self.lblReferral, 0, 0, 1, 1)
        self.lblTicket = QtGui.QLabel(FrmAppointment)
        self.lblTicket.setObjectName(_fromUtf8("lblTicket"))
        self.gridLayout.addWidget(self.lblTicket, 6, 0, 1, 1)
        self.cmbTickets = QtGui.QComboBox(FrmAppointment)
        self.cmbTickets.setObjectName(_fromUtf8("cmbTickets"))
        self.gridLayout.addWidget(self.cmbTickets, 7, 0, 1, 1)
        self.cmbReferral = CDbComboBox(FrmAppointment)
        self.cmbReferral.setObjectName(_fromUtf8("cmbReferral"))
        self.gridLayout.addWidget(self.cmbReferral, 1, 0, 1, 1)
        self.lblDoctor = QtGui.QLabel(FrmAppointment)
        self.lblDoctor.setObjectName(_fromUtf8("lblDoctor"))
        self.gridLayout.addWidget(self.lblDoctor, 4, 0, 1, 1)
        self.cmbDoctor = QtGui.QComboBox(FrmAppointment)
        self.cmbDoctor.setObjectName(_fromUtf8("cmbDoctor"))
        self.gridLayout.addWidget(self.cmbDoctor, 5, 0, 1, 1)
        self.lblSpeciality = QtGui.QLabel(FrmAppointment)
        self.lblSpeciality.setObjectName(_fromUtf8("lblSpeciality"))
        self.gridLayout.addWidget(self.lblSpeciality, 2, 0, 1, 1)
        self.cmbSpeciality = QtGui.QComboBox(FrmAppointment)
        self.cmbSpeciality.setObjectName(_fromUtf8("cmbSpeciality"))
        self.gridLayout.addWidget(self.cmbSpeciality, 3, 0, 1, 1)

        self.retranslateUi(FrmAppointment)
        QtCore.QMetaObject.connectSlotsByName(FrmAppointment)

    def retranslateUi(self, FrmAppointment):
        FrmAppointment.setWindowTitle(_translate("FrmAppointment", "Запись в другое ЛПУ", None))
        self.btnAppoint.setText(_translate("FrmAppointment", "Записать", None))
        self.lblReferral.setText(_translate("FrmAppointment", "Направление:", None))
        self.lblTicket.setText(_translate("FrmAppointment", "Дата и время приема:", None))
        self.lblDoctor.setText(_translate("FrmAppointment", "Врач:", None))
        self.lblSpeciality.setText(_translate("FrmAppointment", "Специальность:", None))

from library.DbComboBox import CDbComboBox
