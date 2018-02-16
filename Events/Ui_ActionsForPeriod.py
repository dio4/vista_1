# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ActionsForPeriod.ui'
#
# Created: Fri Oct 16 14:29:21 2015
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

class Ui_ActionsForPeriod(object):
    def setupUi(self, ActionsForPeriod):
        ActionsForPeriod.setObjectName(_fromUtf8("ActionsForPeriod"))
        ActionsForPeriod.resize(461, 246)
        self.verticalLayout = QtGui.QVBoxLayout(ActionsForPeriod)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblPeriodDuration = QtGui.QLabel(ActionsForPeriod)
        self.lblPeriodDuration.setObjectName(_fromUtf8("lblPeriodDuration"))
        self.gridLayout.addWidget(self.lblPeriodDuration, 4, 0, 1, 1)
        self.lblPeriodInterval = QtGui.QLabel(ActionsForPeriod)
        self.lblPeriodInterval.setObjectName(_fromUtf8("lblPeriodInterval"))
        self.gridLayout.addWidget(self.lblPeriodInterval, 5, 0, 1, 1)
        self.etdAmount = QtGui.QSpinBox(ActionsForPeriod)
        self.etdAmount.setEnabled(False)
        self.etdAmount.setObjectName(_fromUtf8("etdAmount"))
        self.gridLayout.addWidget(self.etdAmount, 2, 1, 1, 1)
        self.lblPeriodBegDate = QtGui.QLabel(ActionsForPeriod)
        self.lblPeriodBegDate.setObjectName(_fromUtf8("lblPeriodBegDate"))
        self.gridLayout.addWidget(self.lblPeriodBegDate, 0, 0, 1, 1, QtCore.Qt.AlignRight)
        self.edtPeriodEndDate = CDateEdit(ActionsForPeriod)
        self.edtPeriodEndDate.setObjectName(_fromUtf8("edtPeriodEndDate"))
        self.gridLayout.addWidget(self.edtPeriodEndDate, 1, 1, 1, 1)
        self.lblPeriodEndDate = QtGui.QLabel(ActionsForPeriod)
        self.lblPeriodEndDate.setObjectName(_fromUtf8("lblPeriodEndDate"))
        self.gridLayout.addWidget(self.lblPeriodEndDate, 1, 0, 1, 1, QtCore.Qt.AlignRight)
        self.edtPeriodBegDate = CDateEdit(ActionsForPeriod)
        self.edtPeriodBegDate.setObjectName(_fromUtf8("edtPeriodBegDate"))
        self.gridLayout.addWidget(self.edtPeriodBegDate, 0, 1, 1, 1)
        self.lblAmount = QtGui.QLabel(ActionsForPeriod)
        self.lblAmount.setEnabled(False)
        self.lblAmount.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblAmount.setObjectName(_fromUtf8("lblAmount"))
        self.gridLayout.addWidget(self.lblAmount, 2, 0, 1, 1)
        self.edtInterval = QtGui.QSpinBox(ActionsForPeriod)
        self.edtInterval.setMaximum(9999999)
        self.edtInterval.setObjectName(_fromUtf8("edtInterval"))
        self.gridLayout.addWidget(self.edtInterval, 5, 1, 1, 1)
        self.edtDuration = QtGui.QSpinBox(ActionsForPeriod)
        self.edtDuration.setMinimum(1)
        self.edtDuration.setMaximum(999999)
        self.edtDuration.setObjectName(_fromUtf8("edtDuration"))
        self.gridLayout.addWidget(self.edtDuration, 4, 1, 1, 1)
        self.chkFillType = QtGui.QCheckBox(ActionsForPeriod)
        self.chkFillType.setObjectName(_fromUtf8("chkFillType"))
        self.gridLayout.addWidget(self.chkFillType, 3, 0, 1, 2)
        self.chkWeekend = QtGui.QCheckBox(ActionsForPeriod)
        self.chkWeekend.setObjectName(_fromUtf8("chkWeekend"))
        self.gridLayout.addWidget(self.chkWeekend, 6, 0, 1, 2)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(ActionsForPeriod)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(ActionsForPeriod)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ActionsForPeriod.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ActionsForPeriod.reject)
        QtCore.QObject.connect(self.chkFillType, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.etdAmount.setEnabled)
        QtCore.QObject.connect(self.chkFillType, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.lblAmount.setEnabled)
        QtCore.QObject.connect(self.chkFillType, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtPeriodEndDate.setDisabled)
        QtCore.QObject.connect(self.chkFillType, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.lblPeriodEndDate.setDisabled)
        QtCore.QMetaObject.connectSlotsByName(ActionsForPeriod)
        ActionsForPeriod.setTabOrder(self.edtPeriodBegDate, self.edtPeriodEndDate)
        ActionsForPeriod.setTabOrder(self.edtPeriodEndDate, self.etdAmount)
        ActionsForPeriod.setTabOrder(self.etdAmount, self.chkFillType)
        ActionsForPeriod.setTabOrder(self.chkFillType, self.edtDuration)
        ActionsForPeriod.setTabOrder(self.edtDuration, self.edtInterval)
        ActionsForPeriod.setTabOrder(self.edtInterval, self.chkWeekend)
        ActionsForPeriod.setTabOrder(self.chkWeekend, self.buttonBox)

    def retranslateUi(self, ActionsForPeriod):
        ActionsForPeriod.setWindowTitle(_translate("ActionsForPeriod", "Dialog", None))
        self.lblPeriodDuration.setText(_translate("ActionsForPeriod", "Длительность мероприятия (дней)", None))
        self.lblPeriodInterval.setText(_translate("ActionsForPeriod", "Интервал между мероприятиями (дней)", None))
        self.lblPeriodBegDate.setText(_translate("ActionsForPeriod", "Начало периода", None))
        self.lblPeriodEndDate.setText(_translate("ActionsForPeriod", "Окончание периода", None))
        self.lblAmount.setText(_translate("ActionsForPeriod", "Количество", None))
        self.chkFillType.setText(_translate("ActionsForPeriod", "Заполнение по количеству", None))
        self.chkWeekend.setText(_translate("ActionsForPeriod", "Учитывать выходные", None))

from library.DateEdit import CDateEdit
