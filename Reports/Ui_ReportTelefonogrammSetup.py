# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportTelefonogrammSetup.ui'
#
# Created: Wed Feb 11 18:28:03 2015
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

class Ui_ReportTelefonogrammSetupDialog(object):
    def setupUi(self, ReportTelefonogrammSetupDialog):
        ReportTelefonogrammSetupDialog.setObjectName(_fromUtf8("ReportTelefonogrammSetupDialog"))
        ReportTelefonogrammSetupDialog.resize(468, 179)
        self.layoutWidget = QtGui.QWidget(ReportTelefonogrammSetupDialog)
        self.layoutWidget.setGeometry(QtCore.QRect(11, 11, 446, 161))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.layoutWidget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblCounter = QtGui.QLabel(self.layoutWidget)
        self.lblCounter.setObjectName(_fromUtf8("lblCounter"))
        self.gridLayout.addWidget(self.lblCounter, 3, 0, 1, 1)
        self.lblEndDate = QtGui.QLabel(self.layoutWidget)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 2, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(self.layoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 2, 1, 2)
        self.lblBegDate = QtGui.QLabel(self.layoutWidget)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 2)
        self.edtBegDate = CDateEdit(self.layoutWidget)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 2, 1, 2)
        self.edtBegTime = QtGui.QTimeEdit(self.layoutWidget)
        self.edtBegTime.setObjectName(_fromUtf8("edtBegTime"))
        self.gridLayout.addWidget(self.edtBegTime, 0, 4, 1, 1)
        self.edtEndDate = CDateEdit(self.layoutWidget)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 2, 2, 1, 2)
        self.edtEndTime = QtGui.QTimeEdit(self.layoutWidget)
        self.edtEndTime.setObjectName(_fromUtf8("edtEndTime"))
        self.gridLayout.addWidget(self.edtEndTime, 2, 4, 1, 1)
        self.frmAge_2 = QtGui.QFrame(self.layoutWidget)
        self.frmAge_2.setFrameShape(QtGui.QFrame.NoFrame)
        self.frmAge_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frmAge_2.setObjectName(_fromUtf8("frmAge_2"))
        self._2 = QtGui.QHBoxLayout(self.frmAge_2)
        self._2.setSpacing(4)
        self._2.setMargin(0)
        self._2.setObjectName(_fromUtf8("_2"))
        self.edtCounterFrom = QtGui.QSpinBox(self.frmAge_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtCounterFrom.sizePolicy().hasHeightForWidth())
        self.edtCounterFrom.setSizePolicy(sizePolicy)
        self.edtCounterFrom.setMaximum(99999999)
        self.edtCounterFrom.setObjectName(_fromUtf8("edtCounterFrom"))
        self._2.addWidget(self.edtCounterFrom)
        self.lblCounterTo = QtGui.QLabel(self.frmAge_2)
        self.lblCounterTo.setObjectName(_fromUtf8("lblCounterTo"))
        self._2.addWidget(self.lblCounterTo)
        self.edtCounterTo = QtGui.QSpinBox(self.frmAge_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtCounterTo.sizePolicy().hasHeightForWidth())
        self.edtCounterTo.setSizePolicy(sizePolicy)
        self.edtCounterTo.setMaximum(99999999)
        self.edtCounterTo.setProperty("value", 0)
        self.edtCounterTo.setObjectName(_fromUtf8("edtCounterTo"))
        self._2.addWidget(self.edtCounterTo)
        spacerItem = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self._2.addItem(spacerItem)
        self.gridLayout.addWidget(self.frmAge_2, 3, 2, 1, 3)
        self.chkTelefonoView = QtGui.QCheckBox(self.layoutWidget)
        self.chkTelefonoView.setEnabled(True)
        self.chkTelefonoView.setObjectName(_fromUtf8("chkTelefonoView"))
        self.gridLayout.addWidget(self.chkTelefonoView, 4, 0, 1, 1)
        self.cmbTelefonoView = CStrComboBox(self.layoutWidget)
        self.cmbTelefonoView.setEnabled(False)
        self.cmbTelefonoView.setEditable(False)
        self.cmbTelefonoView.setObjectName(_fromUtf8("cmbTelefonoView"))
        self.gridLayout.addWidget(self.cmbTelefonoView, 4, 2, 1, 3)
        self.lblCounter.setBuddy(self.edtCounterFrom)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblCounterTo.setBuddy(self.edtCounterTo)

        self.retranslateUi(ReportTelefonogrammSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportTelefonogrammSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportTelefonogrammSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportTelefonogrammSetupDialog)
        ReportTelefonogrammSetupDialog.setTabOrder(self.buttonBox, self.edtBegDate)
        ReportTelefonogrammSetupDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportTelefonogrammSetupDialog.setTabOrder(self.edtEndDate, self.edtCounterFrom)
        ReportTelefonogrammSetupDialog.setTabOrder(self.edtCounterFrom, self.edtCounterTo)

    def retranslateUi(self, ReportTelefonogrammSetupDialog):
        ReportTelefonogrammSetupDialog.setWindowTitle(_translate("ReportTelefonogrammSetupDialog", "Dialog", None))
        self.lblCounter.setText(_translate("ReportTelefonogrammSetupDialog", "Выводить по счетчику с", None))
        self.lblEndDate.setText(_translate("ReportTelefonogrammSetupDialog", "Дата окончания периода", None))
        self.lblBegDate.setText(_translate("ReportTelefonogrammSetupDialog", "Дата начала периода", None))
        self.lblCounterTo.setText(_translate("ReportTelefonogrammSetupDialog", "по", None))
        self.chkTelefonoView.setText(_translate("ReportTelefonogrammSetupDialog", "Вид телефонограммы", None))

from library.StrComboBox import CStrComboBox
from library.DateEdit import CDateEdit
