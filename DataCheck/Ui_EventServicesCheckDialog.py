# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'EventServicesCheckDialog.ui'
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

class Ui_EventServiceCheckDialog(object):
    def setupUi(self, EventServiceCheckDialog):
        EventServiceCheckDialog.setObjectName(_fromUtf8("EventServiceCheckDialog"))
        EventServiceCheckDialog.resize(600, 500)
        self.gridLayout = QtGui.QGridLayout(EventServiceCheckDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.layoutFilter = QtGui.QHBoxLayout()
        self.layoutFilter.setObjectName(_fromUtf8("layoutFilter"))
        self.lblDateFrom = QtGui.QLabel(EventServiceCheckDialog)
        self.lblDateFrom.setObjectName(_fromUtf8("lblDateFrom"))
        self.layoutFilter.addWidget(self.lblDateFrom)
        self.edtDateFrom = CDateEdit(EventServiceCheckDialog)
        self.edtDateFrom.setObjectName(_fromUtf8("edtDateFrom"))
        self.layoutFilter.addWidget(self.edtDateFrom)
        self.lblDateTo = QtGui.QLabel(EventServiceCheckDialog)
        self.lblDateTo.setObjectName(_fromUtf8("lblDateTo"))
        self.layoutFilter.addWidget(self.lblDateTo)
        self.edtDateTo = CDateEdit(EventServiceCheckDialog)
        self.edtDateTo.setObjectName(_fromUtf8("edtDateTo"))
        self.layoutFilter.addWidget(self.edtDateTo)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.layoutFilter.addItem(spacerItem)
        self.gridLayout.addLayout(self.layoutFilter, 0, 1, 1, 1)
        self.lblDate = QtGui.QLabel(EventServiceCheckDialog)
        self.lblDate.setObjectName(_fromUtf8("lblDate"))
        self.gridLayout.addWidget(self.lblDate, 0, 0, 1, 1)
        self.lblEventType = QtGui.QLabel(EventServiceCheckDialog)
        self.lblEventType.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridLayout.addWidget(self.lblEventType, 1, 0, 1, 1)
        self.tblEventType = CRBListBox(EventServiceCheckDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(4)
        sizePolicy.setHeightForWidth(self.tblEventType.sizePolicy().hasHeightForWidth())
        self.tblEventType.setSizePolicy(sizePolicy)
        self.tblEventType.setObjectName(_fromUtf8("tblEventType"))
        self.gridLayout.addWidget(self.tblEventType, 1, 1, 1, 1)
        self.progressBar = CProgressBar(EventServiceCheckDialog)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 3, 0, 1, 2)
        self.log = QtGui.QListWidget(EventServiceCheckDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(6)
        sizePolicy.setHeightForWidth(self.log.sizePolicy().hasHeightForWidth())
        self.log.setSizePolicy(sizePolicy)
        self.log.setObjectName(_fromUtf8("log"))
        self.gridLayout.addWidget(self.log, 4, 0, 1, 2)
        self.layoutButtons = QtGui.QHBoxLayout()
        self.layoutButtons.setObjectName(_fromUtf8("layoutButtons"))
        self.btnStart = QtGui.QPushButton(EventServiceCheckDialog)
        self.btnStart.setMinimumSize(QtCore.QSize(100, 0))
        self.btnStart.setObjectName(_fromUtf8("btnStart"))
        self.layoutButtons.addWidget(self.btnStart)
        spacerItem1 = QtGui.QSpacerItem(361, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.layoutButtons.addItem(spacerItem1)
        self.btnClose = QtGui.QPushButton(EventServiceCheckDialog)
        self.btnClose.setMinimumSize(QtCore.QSize(100, 0))
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.layoutButtons.addWidget(self.btnClose)
        self.gridLayout.addLayout(self.layoutButtons, 5, 0, 1, 2)
        self.lblDateFrom.setBuddy(self.edtDateFrom)
        self.lblDateTo.setBuddy(self.edtDateTo)
        self.lblEventType.setBuddy(self.tblEventType)

        self.retranslateUi(EventServiceCheckDialog)
        QtCore.QMetaObject.connectSlotsByName(EventServiceCheckDialog)
        EventServiceCheckDialog.setTabOrder(self.edtDateFrom, self.edtDateTo)
        EventServiceCheckDialog.setTabOrder(self.edtDateTo, self.btnStart)
        EventServiceCheckDialog.setTabOrder(self.btnStart, self.btnClose)
        EventServiceCheckDialog.setTabOrder(self.btnClose, self.log)

    def retranslateUi(self, EventServiceCheckDialog):
        EventServiceCheckDialog.setWindowTitle(_translate("EventServiceCheckDialog", "Контроль услуг и стандартов в обращениях", None))
        self.lblDateFrom.setText(_translate("EventServiceCheckDialog", "с", None))
        self.lblDateTo.setText(_translate("EventServiceCheckDialog", "по", None))
        self.lblDate.setText(_translate("EventServiceCheckDialog", "Дата назначения:", None))
        self.lblEventType.setText(_translate("EventServiceCheckDialog", "Типы обращений:", None))
        self.btnStart.setText(_translate("EventServiceCheckDialog", "Начать проверку", None))
        self.btnClose.setText(_translate("EventServiceCheckDialog", "Прервать", None))

from library.DateEdit import CDateEdit
from library.ProgressBar import CProgressBar
from library.RBListBox import CRBListBox
