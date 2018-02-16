# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ClientDocuments.ui'
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

class Ui_ClientDocumentsCheckDialog(object):
    def setupUi(self, ClientDocumentsCheckDialog):
        ClientDocumentsCheckDialog.setObjectName(_fromUtf8("ClientDocumentsCheckDialog"))
        ClientDocumentsCheckDialog.resize(589, 538)
        self.gridLayout = QtGui.QGridLayout(ClientDocumentsCheckDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.frmDateRange = QtGui.QWidget(ClientDocumentsCheckDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frmDateRange.sizePolicy().hasHeightForWidth())
        self.frmDateRange.setSizePolicy(sizePolicy)
        self.frmDateRange.setObjectName(_fromUtf8("frmDateRange"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.frmDateRange)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(self.frmDateRange)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.gridLayout.addWidget(self.frmDateRange, 0, 0, 1, 2)
        self.log = QtGui.QListWidget(ClientDocumentsCheckDialog)
        self.log.setObjectName(_fromUtf8("log"))
        self.gridLayout.addWidget(self.log, 3, 0, 1, 6)
        self.progressBar = CProgressBar(ClientDocumentsCheckDialog)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 2, 0, 1, 6)
        self.btnStart = QtGui.QPushButton(ClientDocumentsCheckDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnStart.sizePolicy().hasHeightForWidth())
        self.btnStart.setSizePolicy(sizePolicy)
        self.btnStart.setMinimumSize(QtCore.QSize(100, 0))
        self.btnStart.setObjectName(_fromUtf8("btnStart"))
        self.gridLayout.addWidget(self.btnStart, 5, 3, 1, 2)
        self.labelInfo = QtGui.QLabel(ClientDocumentsCheckDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelInfo.sizePolicy().hasHeightForWidth())
        self.labelInfo.setSizePolicy(sizePolicy)
        self.labelInfo.setText(_fromUtf8(""))
        self.labelInfo.setObjectName(_fromUtf8("labelInfo"))
        self.gridLayout.addWidget(self.labelInfo, 5, 0, 1, 3)
        self.btnClose = QtGui.QPushButton(ClientDocumentsCheckDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnClose.sizePolicy().hasHeightForWidth())
        self.btnClose.setSizePolicy(sizePolicy)
        self.btnClose.setMinimumSize(QtCore.QSize(100, 0))
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.gridLayout.addWidget(self.btnClose, 5, 5, 1, 1)
        self.begDate = CDateEdit(ClientDocumentsCheckDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.begDate.sizePolicy().hasHeightForWidth())
        self.begDate.setSizePolicy(sizePolicy)
        self.begDate.setDate(QtCore.QDate(2000, 1, 1))
        self.begDate.setCalendarPopup(True)
        self.begDate.setObjectName(_fromUtf8("begDate"))
        self.gridLayout.addWidget(self.begDate, 0, 2, 1, 1)
        self.label_2 = QtGui.QLabel(ClientDocumentsCheckDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 3, 1, 1)
        self.endDate = CDateEdit(ClientDocumentsCheckDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.endDate.sizePolicy().hasHeightForWidth())
        self.endDate.setSizePolicy(sizePolicy)
        self.endDate.setDate(QtCore.QDate(2000, 1, 1))
        self.endDate.setCalendarPopup(True)
        self.endDate.setObjectName(_fromUtf8("endDate"))
        self.gridLayout.addWidget(self.endDate, 0, 4, 1, 1)

        self.retranslateUi(ClientDocumentsCheckDialog)
        QtCore.QMetaObject.connectSlotsByName(ClientDocumentsCheckDialog)

    def retranslateUi(self, ClientDocumentsCheckDialog):
        ClientDocumentsCheckDialog.setWindowTitle(_translate("ClientDocumentsCheckDialog", "Проверка документов, удостоверяющих личность", None))
        self.label.setText(_translate("ClientDocumentsCheckDialog", "Дата выполнения обращения с ", None))
        self.btnStart.setText(_translate("ClientDocumentsCheckDialog", "Начать проверку", None))
        self.btnClose.setText(_translate("ClientDocumentsCheckDialog", "Прервать", None))
        self.begDate.setDisplayFormat(_translate("ClientDocumentsCheckDialog", "dd.MM.yyyy", None))
        self.label_2.setText(_translate("ClientDocumentsCheckDialog", "по", None))
        self.endDate.setDisplayFormat(_translate("ClientDocumentsCheckDialog", "dd.MM.yyyy", None))

from library.DateEdit import CDateEdit
from library.ProgressBar import CProgressBar
