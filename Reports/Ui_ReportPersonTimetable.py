# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportPersonTimetable.ui'
#
# Created: Mon Sep 28 16:37:54 2015
#      by: PyQt4 UI code generator 4.11.3
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

class Ui_ReportPersonTimetable(object):
    def setupUi(self, ReportPersonTimetable):
        ReportPersonTimetable.setObjectName(_fromUtf8("ReportPersonTimetable"))
        ReportPersonTimetable.resize(390, 159)
        self.gridLayout = QtGui.QGridLayout(ReportPersonTimetable)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.edtBegDate = CDateEdit(ReportPersonTimetable)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 4, 1, 1)
        self.cmbPerson = CPersonComboBoxEx(ReportPersonTimetable)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.gridLayout.addWidget(self.cmbPerson, 1, 3, 1, 2)
        self.cmbSpeciality = CRBComboBox(ReportPersonTimetable)
        self.cmbSpeciality.setObjectName(_fromUtf8("cmbSpeciality"))
        self.gridLayout.addWidget(self.cmbSpeciality, 2, 3, 1, 2)
        self.lblBegDate = QtGui.QLabel(ReportPersonTimetable)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.label_3 = QtGui.QLabel(ReportPersonTimetable)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportPersonTimetable)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 4, 1, 1)
        self.lblSpeciality = QtGui.QLabel(ReportPersonTimetable)
        self.lblSpeciality.setObjectName(_fromUtf8("lblSpeciality"))
        self.gridLayout.addWidget(self.lblSpeciality, 2, 0, 1, 2)
        self.lblLocationCardType = QtGui.QLabel(ReportPersonTimetable)
        self.lblLocationCardType.setTextFormat(QtCore.Qt.AutoText)
        self.lblLocationCardType.setObjectName(_fromUtf8("lblLocationCardType"))
        self.gridLayout.addWidget(self.lblLocationCardType, 3, 0, 1, 2)
        self.cmbLocationCardType = CRBComboBox(ReportPersonTimetable)
        self.cmbLocationCardType.setObjectName(_fromUtf8("cmbLocationCardType"))
        self.gridLayout.addWidget(self.cmbLocationCardType, 3, 3, 1, 2)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblSpeciality.setBuddy(self.cmbSpeciality)

        self.retranslateUi(ReportPersonTimetable)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportPersonTimetable.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportPersonTimetable.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportPersonTimetable)

    def retranslateUi(self, ReportPersonTimetable):
        ReportPersonTimetable.setWindowTitle(_translate("ReportPersonTimetable", "Dialog", None))
        self.cmbSpeciality.setWhatsThis(_translate("ReportPersonTimetable", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>", None))
        self.lblBegDate.setText(_translate("ReportPersonTimetable", "Дата", None))
        self.label_3.setText(_translate("ReportPersonTimetable", "Врач", None))
        self.lblSpeciality.setText(_translate("ReportPersonTimetable", "&Специальность", None))
        self.lblLocationCardType.setText(_translate("ReportPersonTimetable", "Место нахождения\n"
"амбулаторной карты", None))

from library.DateEdit import CDateEdit
from library.crbcombobox import CRBComboBox
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
