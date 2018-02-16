# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DublicateWeekDialog.ui'
#
# Created: Fri Oct 17 16:17:01 2014
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

class Ui_DublicateWeekDialog(object):
    def setupUi(self, DublicateWeekDialog):
        DublicateWeekDialog.setObjectName(_fromUtf8("DublicateWeekDialog"))
        DublicateWeekDialog.resize(460, 390)
        self.gridLayout = QtGui.QGridLayout(DublicateWeekDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(DublicateWeekDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.edtStart = CDateEdit(DublicateWeekDialog)
        self.edtStart.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtStart.sizePolicy().hasHeightForWidth())
        self.edtStart.setSizePolicy(sizePolicy)
        self.edtStart.setObjectName(_fromUtf8("edtStart"))
        self.gridLayout.addWidget(self.edtStart, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(DublicateWeekDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.edtCountDays = QtGui.QSpinBox(DublicateWeekDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtCountDays.sizePolicy().hasHeightForWidth())
        self.edtCountDays.setSizePolicy(sizePolicy)
        self.edtCountDays.setMinimum(1)
        self.edtCountDays.setMaximum(7)
        self.edtCountDays.setObjectName(_fromUtf8("edtCountDays"))
        self.gridLayout.addWidget(self.edtCountDays, 2, 1, 1, 1)
        self.label_3 = QtGui.QLabel(DublicateWeekDialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 2, 1, 1)
        self.calendar = CCalendarWidget(DublicateWeekDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.calendar.sizePolicy().hasHeightForWidth())
        self.calendar.setSizePolicy(sizePolicy)
        self.calendar.setFirstDayOfWeek(QtCore.Qt.Monday)
        self.calendar.setGridVisible(False)
        self.calendar.setObjectName(_fromUtf8("calendar"))
        self.gridLayout.addWidget(self.calendar, 5, 0, 1, 3)
        self.buttonBox = QtGui.QDialogButtonBox(DublicateWeekDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 8, 2, 1, 1)
        self.groupBox = QtGui.QGroupBox(DublicateWeekDialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout_2.addWidget(self.label_4)
        self.label_6 = QtGui.QLabel(self.groupBox)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.horizontalLayout_2.addWidget(self.label_6)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.gridLayout_2.addLayout(self.horizontalLayout_2, 0, 1, 1, 1)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.lblGoodColor = QtGui.QLabel(self.groupBox)
        self.lblGoodColor.setObjectName(_fromUtf8("lblGoodColor"))
        self.horizontalLayout_3.addWidget(self.lblGoodColor)
        self.label_5 = QtGui.QLabel(self.groupBox)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.horizontalLayout_3.addWidget(self.label_5)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.gridLayout_2.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 6, 0, 1, 3)
        self.lblWarning = QtGui.QLabel(DublicateWeekDialog)
        self.lblWarning.setText(_fromUtf8(""))
        self.lblWarning.setObjectName(_fromUtf8("lblWarning"))
        self.gridLayout.addWidget(self.lblWarning, 4, 0, 1, 3)
        self.chkBusyDays = QtGui.QCheckBox(DublicateWeekDialog)
        self.chkBusyDays.setObjectName(_fromUtf8("chkBusyDays"))
        self.gridLayout.addWidget(self.chkBusyDays, 7, 0, 1, 1)

        self.retranslateUi(DublicateWeekDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DublicateWeekDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DublicateWeekDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(DublicateWeekDialog)

    def retranslateUi(self, DublicateWeekDialog):
        DublicateWeekDialog.setWindowTitle(_translate("DublicateWeekDialog", "Копировать за период", None))
        self.label.setText(_translate("DublicateWeekDialog", "Дата, с которой копируем", None))
        self.label_2.setText(_translate("DublicateWeekDialog", "Количество копируемых дней", None))
        self.label_3.setText(_translate("DublicateWeekDialog", "Выбирете день начала копирования:", None))
        self.groupBox.setTitle(_translate("DublicateWeekDialog", "Расшифровка цветов", None))
        self.label_4.setText(_translate("DublicateWeekDialog", "<html><head/><body><p><span style=\" color:#CD5555;background-color:#CD5555;\">Good</span></p></body></html>", None))
        self.label_6.setText(_translate("DublicateWeekDialog", "Дни с расписанием", None))
        self.lblGoodColor.setText(_translate("DublicateWeekDialog", "<html><head/><body><p><span style=\" color:#98fb98;background-color:#98fb98;\">Good</span></p></body></html>", None))
        self.label_5.setText(_translate("DublicateWeekDialog", "Свободные дни", None))
        self.chkBusyDays.setText(_translate("DublicateWeekDialog", "Перезаписать дни с расписанием", None))

from library.DateEdit import CDateEdit
from library.calendar import CCalendarWidget
