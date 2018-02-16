# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportMovingB36SetupDialog.ui'
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

class Ui_ReportMovingB36SetupDialog(object):
    def setupUi(self, ReportMovingB36SetupDialog):
        ReportMovingB36SetupDialog.setObjectName(_fromUtf8("ReportMovingB36SetupDialog"))
        ReportMovingB36SetupDialog.resize(400, 200)
        self.gridLayout = QtGui.QGridLayout(ReportMovingB36SetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblDate = QtGui.QLabel(ReportMovingB36SetupDialog)
        self.lblDate.setObjectName(_fromUtf8("lblDate"))
        self.gridLayout.addWidget(self.lblDate, 0, 0, 1, 1)
        self.edtDate = CDateEdit(ReportMovingB36SetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtDate.sizePolicy().hasHeightForWidth())
        self.edtDate.setSizePolicy(sizePolicy)
        self.edtDate.setCalendarPopup(True)
        self.edtDate.setObjectName(_fromUtf8("edtDate"))
        self.gridLayout.addWidget(self.edtDate, 0, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.lblBegTime = QtGui.QLabel(ReportMovingB36SetupDialog)
        self.lblBegTime.setObjectName(_fromUtf8("lblBegTime"))
        self.gridLayout.addWidget(self.lblBegTime, 1, 0, 1, 1)
        self.edtBegTime = QtGui.QTimeEdit(ReportMovingB36SetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegTime.sizePolicy().hasHeightForWidth())
        self.edtBegTime.setSizePolicy(sizePolicy)
        self.edtBegTime.setObjectName(_fromUtf8("edtBegTime"))
        self.gridLayout.addWidget(self.edtBegTime, 1, 1, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportMovingB36SetupDialog)
        self.lblEndDate.setText(_fromUtf8(""))
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 2, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 3, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportMovingB36SetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 2, 1, 1)
        self.lblDate.setBuddy(self.edtDate)
        self.lblBegTime.setBuddy(self.edtDate)

        self.retranslateUi(ReportMovingB36SetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportMovingB36SetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportMovingB36SetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportMovingB36SetupDialog)

    def retranslateUi(self, ReportMovingB36SetupDialog):
        ReportMovingB36SetupDialog.setWindowTitle(_translate("ReportMovingB36SetupDialog", "Dialog", None))
        self.lblDate.setText(_translate("ReportMovingB36SetupDialog", "Текущий &день", None))
        self.edtDate.setDisplayFormat(_translate("ReportMovingB36SetupDialog", "dd.MM.yyyy", None))
        self.lblBegTime.setText(_translate("ReportMovingB36SetupDialog", "Время смены суток", None))

from library.DateEdit import CDateEdit
