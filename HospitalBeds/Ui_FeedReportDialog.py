# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FeedReportDialog.ui'
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

class Ui_FeedReportDialog(object):
    def setupUi(self, FeedReportDialog):
        FeedReportDialog.setObjectName(_fromUtf8("FeedReportDialog"))
        FeedReportDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        FeedReportDialog.resize(384, 169)
        FeedReportDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(FeedReportDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        spacerItem = QtGui.QSpacerItem(129, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 7, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(FeedReportDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 8, 0, 1, 3)
        self.label_2 = QtGui.QLabel(FeedReportDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.cmbIsFinal = QtGui.QComboBox(FeedReportDialog)
        self.cmbIsFinal.setObjectName(_fromUtf8("cmbIsFinal"))
        self.cmbIsFinal.addItem(_fromUtf8(""))
        self.cmbIsFinal.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbIsFinal, 1, 1, 1, 2)
        self.edtNameReg = QtGui.QLineEdit(FeedReportDialog)
        self.edtNameReg.setObjectName(_fromUtf8("edtNameReg"))
        self.gridLayout.addWidget(self.edtNameReg, 2, 1, 1, 2)
        self.edtBegDate = CDateEdit(FeedReportDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.lblBegDate = QtGui.QLabel(FeedReportDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblBegDate.sizePolicy().hasHeightForWidth())
        self.lblBegDate.setSizePolicy(sizePolicy)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 2, 1, 1)
        self.lblNameReg = QtGui.QLabel(FeedReportDialog)
        self.lblNameReg.setObjectName(_fromUtf8("lblNameReg"))
        self.gridLayout.addWidget(self.lblNameReg, 2, 0, 1, 1)
        self.edtNameDoctor = QtGui.QLineEdit(FeedReportDialog)
        self.edtNameDoctor.setObjectName(_fromUtf8("edtNameDoctor"))
        self.gridLayout.addWidget(self.edtNameDoctor, 3, 1, 1, 2)
        self.lblNameDoctor = QtGui.QLabel(FeedReportDialog)
        self.lblNameDoctor.setObjectName(_fromUtf8("lblNameDoctor"))
        self.gridLayout.addWidget(self.lblNameDoctor, 3, 0, 1, 1)
        self.lblNameNurse = QtGui.QLabel(FeedReportDialog)
        self.lblNameNurse.setObjectName(_fromUtf8("lblNameNurse"))
        self.gridLayout.addWidget(self.lblNameNurse, 5, 0, 1, 1)
        self.edtNameNurse = QtGui.QLineEdit(FeedReportDialog)
        self.edtNameNurse.setObjectName(_fromUtf8("edtNameNurse"))
        self.gridLayout.addWidget(self.edtNameNurse, 5, 1, 1, 2)
        self.lblBegDate.setBuddy(self.edtBegDate)

        self.retranslateUi(FeedReportDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), FeedReportDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), FeedReportDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(FeedReportDialog)
        FeedReportDialog.setTabOrder(self.edtBegDate, self.buttonBox)

    def retranslateUi(self, FeedReportDialog):
        FeedReportDialog.setWindowTitle(_translate("FeedReportDialog", "параметры отчёта", None))
        self.label_2.setText(_translate("FeedReportDialog", "Порционник:", None))
        self.cmbIsFinal.setItemText(0, _translate("FeedReportDialog", "На 10:00", None))
        self.cmbIsFinal.setItemText(1, _translate("FeedReportDialog", "На 7:00", None))
        self.edtBegDate.setDisplayFormat(_translate("FeedReportDialog", "dd.MM.yyyy", None))
        self.lblBegDate.setText(_translate("FeedReportDialog", "Порционник на дату", None))
        self.lblNameReg.setText(_translate("FeedReportDialog", "Регистратор", None))
        self.lblNameDoctor.setText(_translate("FeedReportDialog", "Дежурный врач", None))
        self.lblNameNurse.setText(_translate("FeedReportDialog", "Дежурная медсестра", None))

from library.DateEdit import CDateEdit
