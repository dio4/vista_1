# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportF10Setup.ui'
#
# Created: Mon Jul 21 11:53:17 2014
#      by: PyQt4 UI code generator 4.11
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

class Ui_ReportF10SetupDialog(object):
    def setupUi(self, ReportF10SetupDialog):
        ReportF10SetupDialog.setObjectName(_fromUtf8("ReportF10SetupDialog"))
        ReportF10SetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportF10SetupDialog.resize(356, 153)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ReportF10SetupDialog.sizePolicy().hasHeightForWidth())
        ReportF10SetupDialog.setSizePolicy(sizePolicy)
        ReportF10SetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportF10SetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBegDate = QtGui.QLabel(ReportF10SetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = QtGui.QDateEdit(ReportF10SetupDialog)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportF10SetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.edtEndDate = QtGui.QDateEdit(ReportF10SetupDialog)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportF10SetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 2)
        self.chkIsRegistry = QtGui.QCheckBox(ReportF10SetupDialog)
        self.chkIsRegistry.setObjectName(_fromUtf8("chkIsRegistry"))
        self.gridLayout.addWidget(self.chkIsRegistry, 2, 0, 1, 2)
        self.chkCompliance = QtGui.QCheckBox(ReportF10SetupDialog)
        self.chkCompliance.setObjectName(_fromUtf8("chkCompliance"))
        self.gridLayout.addWidget(self.chkCompliance, 3, 0, 1, 2)

        self.retranslateUi(ReportF10SetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportF10SetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportF10SetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportF10SetupDialog)

    def retranslateUi(self, ReportF10SetupDialog):
        ReportF10SetupDialog.setWindowTitle(_translate("ReportF10SetupDialog", "параметры отчёта", None))
        self.lblBegDate.setText(_translate("ReportF10SetupDialog", "Дата начала периода", None))
        self.lblEndDate.setText(_translate("ReportF10SetupDialog", "Дата окончания периода", None))
        self.chkIsRegistry.setText(_translate("ReportF10SetupDialog", "Считать всех учетных пациентов зарегистрированными", None))
        self.chkCompliance.setText(_translate("ReportF10SetupDialog", "Проверять соответствие основного кода и дополнительного", None))

