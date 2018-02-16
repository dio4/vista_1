# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportArchiveListSetup.ui'
#
# Created: Tue Feb 17 16:19:54 2015
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

class Ui_ReportReHospitalizationSetupDialog(object):
    def setupUi(self, ReportReHospitalizationSetupDialog):
        ReportReHospitalizationSetupDialog.setObjectName(_fromUtf8("ReportReHospitalizationSetupDialog"))
        ReportReHospitalizationSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportReHospitalizationSetupDialog.resize(373, 124)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ReportReHospitalizationSetupDialog.sizePolicy().hasHeightForWidth())
        ReportReHospitalizationSetupDialog.setSizePolicy(sizePolicy)
        ReportReHospitalizationSetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportReHospitalizationSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBegDate = QtGui.QLabel(ReportReHospitalizationSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = QtGui.QDateEdit(ReportReHospitalizationSetupDialog)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportReHospitalizationSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.edtEndDate = QtGui.QDateEdit(ReportReHospitalizationSetupDialog)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 2, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportReHospitalizationSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 2)

        self.retranslateUi(ReportReHospitalizationSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportReHospitalizationSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportReHospitalizationSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportReHospitalizationSetupDialog)

    def retranslateUi(self, ReportReHospitalizationSetupDialog):
        ReportReHospitalizationSetupDialog.setWindowTitle(_translate("ReportReHospitalizationSetupDialog", "параметры отчёта", None))
        self.lblBegDate.setText(_translate("ReportReHospitalizationSetupDialog", "Дата начала периода", None))
        self.lblEndDate.setText(_translate("ReportReHospitalizationSetupDialog", "Дата окончания периода", None))

