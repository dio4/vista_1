# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportAttachment.ui'
#
# Created: Fri Feb  7 15:28:29 2014
#      by: PyQt4 UI code generator 4.10
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

class Ui_ReportAttachment(object):
    def setupUi(self, ReportAttachment):
        ReportAttachment.setObjectName(_fromUtf8("ReportAttachment"))
        ReportAttachment.resize(366, 223)
        ReportAttachment.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.gridLayout = QtGui.QGridLayout(ReportAttachment)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBegDate = QtGui.QLabel(ReportAttachment)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = CDateEdit(ReportAttachment)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportAttachment)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportAttachment)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        self.label = QtGui.QLabel(ReportAttachment)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.chkTypeK = QtGui.QCheckBox(ReportAttachment)
        self.chkTypeK.setObjectName(_fromUtf8("chkTypeK"))
        self.gridLayout.addWidget(self.chkTypeK, 2, 1, 1, 1)
        self.chkTypeD = QtGui.QCheckBox(ReportAttachment)
        self.chkTypeD.setObjectName(_fromUtf8("chkTypeD"))
        self.gridLayout.addWidget(self.chkTypeD, 3, 1, 1, 1)
        self.chkBegDate = QtGui.QCheckBox(ReportAttachment)
        self.chkBegDate.setObjectName(_fromUtf8("chkBegDate"))
        self.gridLayout.addWidget(self.chkBegDate, 4, 1, 1, 1)
        self.chkEndDate = QtGui.QCheckBox(ReportAttachment)
        self.chkEndDate.setObjectName(_fromUtf8("chkEndDate"))
        self.gridLayout.addWidget(self.chkEndDate, 5, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportAttachment)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 6, 0, 1, 2)
        self.label_2 = QtGui.QLabel(ReportAttachment)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 4, 0, 1, 1)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)

        self.retranslateUi(ReportAttachment)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportAttachment.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportAttachment.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportAttachment)
        ReportAttachment.setTabOrder(self.edtBegDate, self.edtEndDate)

    def retranslateUi(self, ReportAttachment):
        ReportAttachment.setWindowTitle(_translate("ReportAttachment", "Dialog", None))
        self.lblBegDate.setText(_translate("ReportAttachment", "Дата &начала периода", None))
        self.lblEndDate.setText(_translate("ReportAttachment", "Дата &окончания периода", None))
        self.label.setText(_translate("ReportAttachment", "Тип прикрепления", None))
        self.chkTypeK.setText(_translate("ReportAttachment", "К", None))
        self.chkTypeD.setText(_translate("ReportAttachment", "Д", None))
        self.chkBegDate.setText(_translate("ReportAttachment", "установлено", None))
        self.chkEndDate.setText(_translate("ReportAttachment", "снято", None))
        self.label_2.setText(_translate("ReportAttachment", "Наблюдение", None))

from library.DateEdit import CDateEdit
