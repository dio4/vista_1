# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportServiceSpecificationSetup.ui'
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

class Ui_ReportServiceSpecification(object):
    def setupUi(self, ReportServiceSpecification):
        ReportServiceSpecification.setObjectName(_fromUtf8("ReportServiceSpecification"))
        ReportServiceSpecification.resize(261, 131)
        ReportServiceSpecification.setMinimumSize(QtCore.QSize(261, 131))
        ReportServiceSpecification.setMaximumSize(QtCore.QSize(261, 146))
        self.gridLayoutWidget = QtGui.QWidget(ReportServiceSpecification)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 10, 241, 111))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBegDate_2 = QtGui.QLabel(self.gridLayoutWidget)
        self.lblBegDate_2.setObjectName(_fromUtf8("lblBegDate_2"))
        self.gridLayout.addWidget(self.lblBegDate_2, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self.gridLayoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.edtBegDate = CDateEdit(self.gridLayoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setBaseSize(QtCore.QSize(0, 0))
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout_2.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.lblBegDate = QtGui.QLabel(self.gridLayoutWidget)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout_2.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtEndDate = CDateEdit(self.gridLayoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout_2.addWidget(self.edtEndDate, 1, 1, 1, 1)
        self.lblEndDate = QtGui.QLabel(self.gridLayoutWidget)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout_2.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 1, 0, 1, 1)
        self.lblBegDate_2.setBuddy(self.edtBegDate)

        self.retranslateUi(ReportServiceSpecification)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportServiceSpecification.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportServiceSpecification.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportServiceSpecification)

    def retranslateUi(self, ReportServiceSpecification):
        ReportServiceSpecification.setWindowTitle(_translate("ReportServiceSpecification", "Параметры отчета", None))
        self.lblBegDate_2.setText(_translate("ReportServiceSpecification", "Фильтр отчета:", None))
        self.lblBegDate.setText(_translate("ReportServiceSpecification", "с", None))
        self.lblEndDate.setText(_translate("ReportServiceSpecification", "по", None))

from library.DateEdit import CDateEdit
