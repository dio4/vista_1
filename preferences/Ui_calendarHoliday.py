# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'calendarHoliday.ui'
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

class Ui_HolidayDialog(object):
    def setupUi(self, HolidayDialog):
        HolidayDialog.setObjectName(_fromUtf8("HolidayDialog"))
        HolidayDialog.resize(464, 270)
        self.gridLayout = QtGui.QGridLayout(HolidayDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.spinFinish = QtGui.QSpinBox(HolidayDialog)
        self.spinFinish.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinFinish.sizePolicy().hasHeightForWidth())
        self.spinFinish.setSizePolicy(sizePolicy)
        self.spinFinish.setMinimumSize(QtCore.QSize(70, 0))
        self.spinFinish.setMinimum(1)
        self.spinFinish.setMaximum(4999)
        self.spinFinish.setProperty("value", 2000)
        self.spinFinish.setObjectName(_fromUtf8("spinFinish"))
        self.gridLayout.addWidget(self.spinFinish, 7, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(HolidayDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 9, 0, 1, 4)
        self.checkStart = QtGui.QCheckBox(HolidayDialog)
        self.checkStart.setObjectName(_fromUtf8("checkStart"))
        self.gridLayout.addWidget(self.checkStart, 6, 0, 1, 1)
        self.label_2 = QtGui.QLabel(HolidayDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.label_3 = QtGui.QLabel(HolidayDialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 4)
        spacerItem = QtGui.QSpacerItem(97, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 3, 1, 1)
        self.text = QtGui.QLineEdit(HolidayDialog)
        self.text.setObjectName(_fromUtf8("text"))
        self.gridLayout.addWidget(self.text, 2, 1, 1, 3)
        self.label_4 = QtGui.QLabel(HolidayDialog)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 4, 0, 1, 4)
        spacerItem1 = QtGui.QSpacerItem(147, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 6, 2, 1, 2)
        self.label = QtGui.QLabel(HolidayDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.date = CDateEdit(HolidayDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.date.sizePolicy().hasHeightForWidth())
        self.date.setSizePolicy(sizePolicy)
        self.date.setMinimumSize(QtCore.QSize(120, 0))
        self.date.setObjectName(_fromUtf8("date"))
        self.gridLayout.addWidget(self.date, 0, 1, 1, 2)
        spacerItem2 = QtGui.QSpacerItem(147, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 7, 2, 1, 2)
        self.checkFinish = QtGui.QCheckBox(HolidayDialog)
        self.checkFinish.setObjectName(_fromUtf8("checkFinish"))
        self.gridLayout.addWidget(self.checkFinish, 7, 0, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(20, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem3, 8, 0, 1, 1)
        self.spinStart = QtGui.QSpinBox(HolidayDialog)
        self.spinStart.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinStart.sizePolicy().hasHeightForWidth())
        self.spinStart.setSizePolicy(sizePolicy)
        self.spinStart.setMinimumSize(QtCore.QSize(70, 0))
        self.spinStart.setMinimum(1)
        self.spinStart.setMaximum(4999)
        self.spinStart.setProperty("value", 2000)
        self.spinStart.setObjectName(_fromUtf8("spinStart"))
        self.gridLayout.addWidget(self.spinStart, 6, 1, 1, 1)
        self.label_5 = QtGui.QLabel(HolidayDialog)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 1, 0, 1, 1)
        self.endDate = CDateEdit(HolidayDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.endDate.sizePolicy().hasHeightForWidth())
        self.endDate.setSizePolicy(sizePolicy)
        self.endDate.setMinimumSize(QtCore.QSize(120, 0))
        self.endDate.setObjectName(_fromUtf8("endDate"))
        self.gridLayout.addWidget(self.endDate, 1, 1, 1, 1)
        self.label_2.setBuddy(self.text)
        self.label.setBuddy(self.date)

        self.retranslateUi(HolidayDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), HolidayDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), HolidayDialog.reject)
        QtCore.QObject.connect(self.checkStart, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.spinStart.setEnabled)
        QtCore.QObject.connect(self.checkFinish, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.spinFinish.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(HolidayDialog)
        HolidayDialog.setTabOrder(self.date, self.text)
        HolidayDialog.setTabOrder(self.text, self.checkStart)
        HolidayDialog.setTabOrder(self.checkStart, self.spinStart)
        HolidayDialog.setTabOrder(self.spinStart, self.checkFinish)
        HolidayDialog.setTabOrder(self.checkFinish, self.spinFinish)
        HolidayDialog.setTabOrder(self.spinFinish, self.buttonBox)

    def retranslateUi(self, HolidayDialog):
        HolidayDialog.setWindowTitle(_translate("HolidayDialog", "Календарный праздник", None))
        self.checkStart.setText(_translate("HolidayDialog", "Есть год начала:", None))
        self.label_2.setText(_translate("HolidayDialog", "Наименование праздника", None))
        self.label_3.setText(_translate("HolidayDialog", "Если у праздника нет года начала — считается, что он был всегда.", None))
        self.label_4.setText(_translate("HolidayDialog", "Если у праздника нет года окончания — считается, что он будет всегда", None))
        self.label.setText(_translate("HolidayDialog", "Дата начала периода", None))
        self.checkFinish.setText(_translate("HolidayDialog", "Есть год окончания:", None))
        self.label_5.setText(_translate("HolidayDialog", "Дата конца периода", None))

from library.DateEdit import CDateEdit
