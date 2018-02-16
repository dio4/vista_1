# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'EventContractCheckDialog.ui'
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

class Ui_EventContractChecklDialog(object):
    def setupUi(self, EventContractChecklDialog):
        EventContractChecklDialog.setObjectName(_fromUtf8("EventContractChecklDialog"))
        EventContractChecklDialog.resize(600, 500)
        self.gridLayout = QtGui.QGridLayout(EventContractChecklDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblDate = QtGui.QLabel(EventContractChecklDialog)
        self.lblDate.setObjectName(_fromUtf8("lblDate"))
        self.gridLayout.addWidget(self.lblDate, 0, 0, 1, 1)
        self.layoutButtons = QtGui.QHBoxLayout()
        self.layoutButtons.setObjectName(_fromUtf8("layoutButtons"))
        self.btnStart = QtGui.QPushButton(EventContractChecklDialog)
        self.btnStart.setMinimumSize(QtCore.QSize(100, 0))
        self.btnStart.setObjectName(_fromUtf8("btnStart"))
        self.layoutButtons.addWidget(self.btnStart)
        spacerItem = QtGui.QSpacerItem(361, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.layoutButtons.addItem(spacerItem)
        self.btnClose = QtGui.QPushButton(EventContractChecklDialog)
        self.btnClose.setMinimumSize(QtCore.QSize(100, 0))
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.layoutButtons.addWidget(self.btnClose)
        self.gridLayout.addLayout(self.layoutButtons, 7, 0, 1, 2)
        self.lblInfo = QtGui.QLabel(EventContractChecklDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblInfo.sizePolicy().hasHeightForWidth())
        self.lblInfo.setSizePolicy(sizePolicy)
        self.lblInfo.setText(_fromUtf8(""))
        self.lblInfo.setObjectName(_fromUtf8("lblInfo"))
        self.gridLayout.addWidget(self.lblInfo, 6, 0, 1, 2)
        self.lblEventType = QtGui.QLabel(EventContractChecklDialog)
        self.lblEventType.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridLayout.addWidget(self.lblEventType, 1, 0, 1, 1)
        self.progressBar = CProgressBar(EventContractChecklDialog)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 4, 0, 1, 2)
        self.layoutFilter = QtGui.QHBoxLayout()
        self.layoutFilter.setObjectName(_fromUtf8("layoutFilter"))
        self.lblDateFrom = QtGui.QLabel(EventContractChecklDialog)
        self.lblDateFrom.setObjectName(_fromUtf8("lblDateFrom"))
        self.layoutFilter.addWidget(self.lblDateFrom)
        self.edtDateFrom = CDateEdit(EventContractChecklDialog)
        self.edtDateFrom.setObjectName(_fromUtf8("edtDateFrom"))
        self.layoutFilter.addWidget(self.edtDateFrom)
        self.lblDateTo = QtGui.QLabel(EventContractChecklDialog)
        self.lblDateTo.setObjectName(_fromUtf8("lblDateTo"))
        self.layoutFilter.addWidget(self.lblDateTo)
        self.edtDateTo = CDateEdit(EventContractChecklDialog)
        self.edtDateTo.setObjectName(_fromUtf8("edtDateTo"))
        self.layoutFilter.addWidget(self.edtDateTo)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.layoutFilter.addItem(spacerItem1)
        self.gridLayout.addLayout(self.layoutFilter, 0, 1, 1, 1)
        self.tblEventType = CRBListBox(EventContractChecklDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(4)
        sizePolicy.setHeightForWidth(self.tblEventType.sizePolicy().hasHeightForWidth())
        self.tblEventType.setSizePolicy(sizePolicy)
        self.tblEventType.setObjectName(_fromUtf8("tblEventType"))
        self.gridLayout.addWidget(self.tblEventType, 1, 1, 1, 1)
        self.log = QtGui.QListWidget(EventContractChecklDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(6)
        sizePolicy.setHeightForWidth(self.log.sizePolicy().hasHeightForWidth())
        self.log.setSizePolicy(sizePolicy)
        self.log.setObjectName(_fromUtf8("log"))
        self.gridLayout.addWidget(self.log, 5, 0, 1, 2)
        self.lblEventType.setBuddy(self.tblEventType)
        self.lblDateFrom.setBuddy(self.edtDateFrom)
        self.lblDateTo.setBuddy(self.edtDateTo)

        self.retranslateUi(EventContractChecklDialog)
        QtCore.QMetaObject.connectSlotsByName(EventContractChecklDialog)
        EventContractChecklDialog.setTabOrder(self.edtDateFrom, self.edtDateTo)
        EventContractChecklDialog.setTabOrder(self.edtDateTo, self.btnStart)
        EventContractChecklDialog.setTabOrder(self.btnStart, self.btnClose)
        EventContractChecklDialog.setTabOrder(self.btnClose, self.log)

    def retranslateUi(self, EventContractChecklDialog):
        EventContractChecklDialog.setWindowTitle(_translate("EventContractChecklDialog", "Контроль договоров в обращениях", None))
        self.lblDate.setText(_translate("EventContractChecklDialog", "Дата назначения:", None))
        self.btnStart.setText(_translate("EventContractChecklDialog", "Начать проверку", None))
        self.btnClose.setText(_translate("EventContractChecklDialog", "Прервать", None))
        self.lblEventType.setText(_translate("EventContractChecklDialog", "Типы обращений:", None))
        self.lblDateFrom.setText(_translate("EventContractChecklDialog", "с", None))
        self.lblDateTo.setText(_translate("EventContractChecklDialog", "по", None))

from library.DateEdit import CDateEdit
from library.ProgressBar import CProgressBar
from library.RBListBox import CRBListBox
