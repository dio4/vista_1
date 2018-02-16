# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ProcessingReferralWindow.ui'
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

class Ui_ProcessingReferralWindow(object):
    def setupUi(self, ProcessingReferralWindow):
        ProcessingReferralWindow.setObjectName(_fromUtf8("ProcessingReferralWindow"))
        ProcessingReferralWindow.resize(398, 93)
        self.gridLayout = QtGui.QGridLayout(ProcessingReferralWindow)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonBox = QtGui.QDialogButtonBox(ProcessingReferralWindow)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 2)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.lblStatus = QtGui.QLabel(ProcessingReferralWindow)
        self.lblStatus.setMaximumSize(QtCore.QSize(100, 16777215))
        self.lblStatus.setObjectName(_fromUtf8("lblStatus"))
        self.gridLayout_2.addWidget(self.lblStatus, 0, 0, 1, 1)
        self.lblDate = QtGui.QLabel(ProcessingReferralWindow)
        self.lblDate.setObjectName(_fromUtf8("lblDate"))
        self.gridLayout_2.addWidget(self.lblDate, 1, 0, 1, 1)
        self.edtDate = QtGui.QDateEdit(ProcessingReferralWindow)
        self.edtDate.setObjectName(_fromUtf8("edtDate"))
        self.gridLayout_2.addWidget(self.edtDate, 1, 1, 1, 1)
        self.edtStatus = QtGui.QLineEdit(ProcessingReferralWindow)
        self.edtStatus.setMinimumSize(QtCore.QSize(215, 0))
        self.edtStatus.setObjectName(_fromUtf8("edtStatus"))
        self.gridLayout_2.addWidget(self.edtStatus, 0, 1, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 0, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)

        self.retranslateUi(ProcessingReferralWindow)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ProcessingReferralWindow.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ProcessingReferralWindow.reject)
        QtCore.QMetaObject.connectSlotsByName(ProcessingReferralWindow)

    def retranslateUi(self, ProcessingReferralWindow):
        ProcessingReferralWindow.setWindowTitle(_translate("ProcessingReferralWindow", "Обработка направления", None))
        self.lblStatus.setText(_translate("ProcessingReferralWindow", "Статус обработки", None))
        self.lblDate.setText(_translate("ProcessingReferralWindow", "Дата примерной госпитализации\n"
"(для статуса 4003)", None))

