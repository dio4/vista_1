# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportPrimaryRepeatHospitalization.ui'
#
# Created: Wed Jun 11 21:09:44 2014
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_ReportPrimaryRepeatHospitalization(object):
    def setupUi(self, ReportPrimaryRepeatHospitalization):
        ReportPrimaryRepeatHospitalization.setObjectName(_fromUtf8("ReportPrimaryRepeatHospitalization"))
        ReportPrimaryRepeatHospitalization.resize(474, 223)
        self.gridLayout = QtGui.QGridLayout(ReportPrimaryRepeatHospitalization)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.gbEventDatetimeParams = QtGui.QGroupBox(ReportPrimaryRepeatHospitalization)
        self.gbEventDatetimeParams.setCheckable(True)
        self.gbEventDatetimeParams.setChecked(False)
        self.gbEventDatetimeParams.setObjectName(_fromUtf8("gbEventDatetimeParams"))
        self.label_3 = QtGui.QLabel(self.gbEventDatetimeParams)
        self.label_3.setGeometry(QtCore.QRect(10, 23, 164, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.edtEventBegDatetime = QtGui.QDateTimeEdit(self.gbEventDatetimeParams)
        self.edtEventBegDatetime.setGeometry(QtCore.QRect(180, 23, 130, 20))
        self.edtEventBegDatetime.setObjectName(_fromUtf8("edtEventBegDatetime"))
        self.edtEventEndDatetime = QtGui.QDateTimeEdit(self.gbEventDatetimeParams)
        self.edtEventEndDatetime.setGeometry(QtCore.QRect(316, 23, 130, 20))
        self.edtEventEndDatetime.setObjectName(_fromUtf8("edtEventEndDatetime"))
        self.gridLayout.addWidget(self.gbEventDatetimeParams, 3, 0, 1, 4)
        self.edtEndDate = CDateEdit(ReportPrimaryRepeatHospitalization)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 2, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 3, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportPrimaryRepeatHospitalization)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 11, 0, 1, 4)
        self.lblBegDate = QtGui.QLabel(ReportPrimaryRepeatHospitalization)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 2)
        self.lblEndDate = QtGui.QLabel(ReportPrimaryRepeatHospitalization)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 2, 0, 1, 2)
        self.edtBegDate = CDateEdit(ReportPrimaryRepeatHospitalization)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 2, 1, 1)
        self.cmbEventType = CRBComboBox(ReportPrimaryRepeatHospitalization)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 4, 2, 1, 2)
        self.label = QtGui.QLabel(ReportPrimaryRepeatHospitalization)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 4, 0, 1, 2)
        self.cmbPerson = CPersonComboBoxEx(ReportPrimaryRepeatHospitalization)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.gridLayout.addWidget(self.cmbPerson, 5, 2, 1, 2)
        self.lblPerson = QtGui.QLabel(ReportPrimaryRepeatHospitalization)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridLayout.addWidget(self.lblPerson, 5, 0, 1, 2)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)

        self.retranslateUi(ReportPrimaryRepeatHospitalization)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportPrimaryRepeatHospitalization.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportPrimaryRepeatHospitalization.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportPrimaryRepeatHospitalization)

    def retranslateUi(self, ReportPrimaryRepeatHospitalization):
        ReportPrimaryRepeatHospitalization.setWindowTitle(_translate("ReportPrimaryRepeatHospitalization", "Dialog", None))
        self.gbEventDatetimeParams.setTitle(_translate("ReportPrimaryRepeatHospitalization", "Дата и время создания обращения", None))
        self.label_3.setText(_translate("ReportPrimaryRepeatHospitalization", "Интервал дат и времени (с, по):", None))
        self.lblBegDate.setText(_translate("ReportPrimaryRepeatHospitalization", "Дата &начала периода", None))
        self.lblEndDate.setText(_translate("ReportPrimaryRepeatHospitalization", "Дата &окончания периода", None))
        self.label.setText(_translate("ReportPrimaryRepeatHospitalization", "Тип обращения", None))
        self.lblPerson.setText(_translate("ReportPrimaryRepeatHospitalization", "Врач", None))

from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
