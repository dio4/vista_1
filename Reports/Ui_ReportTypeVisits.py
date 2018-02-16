# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportTypeVisits.ui'
#
# Created: Tue May 20 19:18:10 2014
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

class Ui_ReportTypeVisits(object):
    def setupUi(self, ReportTypeVisits):
        ReportTypeVisits.setObjectName(_fromUtf8("ReportTypeVisits"))
        ReportTypeVisits.resize(334, 139)
        self.gridLayout = QtGui.QGridLayout(ReportTypeVisits)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.edtEndDate = CDateEdit(ReportTypeVisits)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 2, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 3, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportTypeVisits)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 2, 0, 1, 2)
        self.lblBegDate = QtGui.QLabel(ReportTypeVisits)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ReportTypeVisits)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 4)
        self.edtBegDate = CDateEdit(ReportTypeVisits)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 2, 1, 1)
        self.chkVisitDisp = QtGui.QCheckBox(ReportTypeVisits)
        self.chkVisitDisp.setObjectName(_fromUtf8("chkVisitDisp"))
        self.gridLayout.addWidget(self.chkVisitDisp, 3, 2, 1, 1)
        self.chkVisitEmergency = QtGui.QCheckBox(ReportTypeVisits)
        self.chkVisitEmergency.setObjectName(_fromUtf8("chkVisitEmergency"))
        self.gridLayout.addWidget(self.chkVisitEmergency, 4, 2, 1, 1)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblBegDate.setBuddy(self.edtBegDate)

        self.retranslateUi(ReportTypeVisits)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportTypeVisits.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportTypeVisits.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportTypeVisits)

    def retranslateUi(self, ReportTypeVisits):
        ReportTypeVisits.setWindowTitle(_translate("ReportTypeVisits", "Dialog", None))
        self.lblEndDate.setText(_translate("ReportTypeVisits", "Дата &окончания периода", None))
        self.lblBegDate.setText(_translate("ReportTypeVisits", "Дата &начала периода", None))
        self.chkVisitDisp.setText(_translate("ReportTypeVisits", "Учитывать посещения ДД", None))
        self.chkVisitEmergency.setText(_translate("ReportTypeVisits", "Учитывать посещения СМП", None))

from library.DateEdit import CDateEdit
