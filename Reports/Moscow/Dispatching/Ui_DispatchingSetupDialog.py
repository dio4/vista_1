# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DispatchingSetupdialog.ui'
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

class Ui_DispatchingSetupDialog(object):
    def setupUi(self, DispatchingSetupDialog):
        DispatchingSetupDialog.setObjectName(_fromUtf8("DispatchingSetupDialog"))
        DispatchingSetupDialog.resize(407, 200)
        self.gridLayout = QtGui.QGridLayout(DispatchingSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.edtDate = CDateEdit(DispatchingSetupDialog)
        self.edtDate.setObjectName(_fromUtf8("edtDate"))
        self.gridLayout.addWidget(self.edtDate, 0, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(DispatchingSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 2)
        self.lblDate = QtGui.QLabel(DispatchingSetupDialog)
        self.lblDate.setObjectName(_fromUtf8("lblDate"))
        self.gridLayout.addWidget(self.lblDate, 0, 0, 1, 1)
        self.lblBegTime = QtGui.QLabel(DispatchingSetupDialog)
        self.lblBegTime.setObjectName(_fromUtf8("lblBegTime"))
        self.gridLayout.addWidget(self.lblBegTime, 1, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 1, 1, 1)
        self.edtBegTime = QtGui.QTimeEdit(DispatchingSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegTime.sizePolicy().hasHeightForWidth())
        self.edtBegTime.setSizePolicy(sizePolicy)
        self.edtBegTime.setObjectName(_fromUtf8("edtBegTime"))
        self.gridLayout.addWidget(self.edtBegTime, 1, 1, 1, 1)
        self.lblReportType = QtGui.QLabel(DispatchingSetupDialog)
        self.lblReportType.setObjectName(_fromUtf8("lblReportType"))
        self.gridLayout.addWidget(self.lblReportType, 2, 0, 1, 1)
        self.cmbReportType = QtGui.QComboBox(DispatchingSetupDialog)
        self.cmbReportType.setObjectName(_fromUtf8("cmbReportType"))
        self.cmbReportType.addItem(_fromUtf8(""))
        self.cmbReportType.addItem(_fromUtf8(""))
        self.cmbReportType.addItem(_fromUtf8(""))
        self.cmbReportType.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbReportType, 2, 1, 1, 1)
        self.lblBegTime.setBuddy(self.edtBegTime)
        self.lblReportType.setBuddy(self.cmbReportType)

        self.retranslateUi(DispatchingSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DispatchingSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DispatchingSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(DispatchingSetupDialog)
        DispatchingSetupDialog.setTabOrder(self.edtDate, self.edtBegTime)
        DispatchingSetupDialog.setTabOrder(self.edtBegTime, self.cmbReportType)
        DispatchingSetupDialog.setTabOrder(self.cmbReportType, self.buttonBox)

    def retranslateUi(self, DispatchingSetupDialog):
        DispatchingSetupDialog.setWindowTitle(_translate("DispatchingSetupDialog", "Dialog", None))
        self.lblDate.setText(_translate("DispatchingSetupDialog", "Текушая дата", None))
        self.lblBegTime.setText(_translate("DispatchingSetupDialog", "Время &смены суток", None))
        self.lblReportType.setText(_translate("DispatchingSetupDialog", "&Вид отчета", None))
        self.cmbReportType.setItemText(0, _translate("DispatchingSetupDialog", "Сводка для администратора", None))
        self.cmbReportType.setItemText(1, _translate("DispatchingSetupDialog", "Диспетчерские по отделениям", None))
        self.cmbReportType.setItemText(2, _translate("DispatchingSetupDialog", "Диспетчерская 3+", None))
        self.cmbReportType.setItemText(3, _translate("DispatchingSetupDialog", "Каналы госпитализации", None))

from library.DateEdit import CDateEdit
