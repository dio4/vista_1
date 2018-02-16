# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ArrivedDepartedPatients.ui'
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

class Ui_ArrivedDepartedPatients(object):
    def setupUi(self, ArrivedDepartedPatients):
        ArrivedDepartedPatients.setObjectName(_fromUtf8("ArrivedDepartedPatients"))
        ArrivedDepartedPatients.resize(468, 352)
        self.verticalLayout = QtGui.QVBoxLayout(ArrivedDepartedPatients)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.widget = QtGui.QWidget(ArrivedDepartedPatients)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.gridLayout_2 = QtGui.QGridLayout(self.widget)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.edtEndDate = CDateEdit(self.widget)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout_2.addWidget(self.edtEndDate, 1, 2, 1, 1)
        self.edtBegDate = CDateEdit(self.widget)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout_2.addWidget(self.edtBegDate, 1, 1, 1, 1)
        self.edtEndTime = QtGui.QTimeEdit(self.widget)
        self.edtEndTime.setObjectName(_fromUtf8("edtEndTime"))
        self.gridLayout_2.addWidget(self.edtEndTime, 2, 2, 1, 1)
        self.edtBegTime = QtGui.QTimeEdit(self.widget)
        self.edtBegTime.setObjectName(_fromUtf8("edtBegTime"))
        self.gridLayout_2.addWidget(self.edtBegTime, 2, 1, 1, 1)
        self.lblBegDateTime = QtGui.QLabel(self.widget)
        self.lblBegDateTime.setObjectName(_fromUtf8("lblBegDateTime"))
        self.gridLayout_2.addWidget(self.lblBegDateTime, 0, 1, 1, 1)
        self.lblEndDateTime = QtGui.QLabel(self.widget)
        self.lblEndDateTime.setObjectName(_fromUtf8("lblEndDateTime"))
        self.gridLayout_2.addWidget(self.lblEndDateTime, 0, 2, 1, 1)
        self.verticalLayout.addWidget(self.widget)
        self.lblLPU = QtGui.QLabel(ArrivedDepartedPatients)
        self.lblLPU.setObjectName(_fromUtf8("lblLPU"))
        self.verticalLayout.addWidget(self.lblLPU)
        self.lstLPU = CRBListBox(ArrivedDepartedPatients)
        self.lstLPU.setObjectName(_fromUtf8("lstLPU"))
        self.verticalLayout.addWidget(self.lstLPU)
        self.chkAllLPU = QtGui.QCheckBox(ArrivedDepartedPatients)
        self.chkAllLPU.setObjectName(_fromUtf8("chkAllLPU"))
        self.verticalLayout.addWidget(self.chkAllLPU)
        self.chkNoFinanceDetail = QtGui.QCheckBox(ArrivedDepartedPatients)
        self.chkNoFinanceDetail.setObjectName(_fromUtf8("chkNoFinanceDetail"))
        self.verticalLayout.addWidget(self.chkNoFinanceDetail)
        self.chkReanimation = QtGui.QCheckBox(ArrivedDepartedPatients)
        self.chkReanimation.setObjectName(_fromUtf8("chkReanimation"))
        self.verticalLayout.addWidget(self.chkReanimation)
        self.buttonBox = QtGui.QDialogButtonBox(ArrivedDepartedPatients)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(ArrivedDepartedPatients)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ArrivedDepartedPatients.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ArrivedDepartedPatients.reject)
        QtCore.QObject.connect(self.chkAllLPU, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.lstLPU.setDisabled)
        QtCore.QMetaObject.connectSlotsByName(ArrivedDepartedPatients)
        ArrivedDepartedPatients.setTabOrder(self.edtBegDate, self.edtEndDate)
        ArrivedDepartedPatients.setTabOrder(self.edtEndDate, self.edtBegTime)
        ArrivedDepartedPatients.setTabOrder(self.edtBegTime, self.edtEndTime)
        ArrivedDepartedPatients.setTabOrder(self.edtEndTime, self.lstLPU)
        ArrivedDepartedPatients.setTabOrder(self.lstLPU, self.chkAllLPU)
        ArrivedDepartedPatients.setTabOrder(self.chkAllLPU, self.chkNoFinanceDetail)
        ArrivedDepartedPatients.setTabOrder(self.chkNoFinanceDetail, self.chkReanimation)
        ArrivedDepartedPatients.setTabOrder(self.chkReanimation, self.buttonBox)

    def retranslateUi(self, ArrivedDepartedPatients):
        ArrivedDepartedPatients.setWindowTitle(_translate("ArrivedDepartedPatients", "Dialog", None))
        self.edtEndTime.setDisplayFormat(_translate("ArrivedDepartedPatients", "H:mm", None))
        self.edtBegTime.setDisplayFormat(_translate("ArrivedDepartedPatients", "H:mm", None))
        self.lblBegDateTime.setText(_translate("ArrivedDepartedPatients", "Начало промежутка", None))
        self.lblEndDateTime.setText(_translate("ArrivedDepartedPatients", "Конец промежутка", None))
        self.lblLPU.setText(_translate("ArrivedDepartedPatients", "Подразделения", None))
        self.chkAllLPU.setText(_translate("ArrivedDepartedPatients", "Построить по всему ЛПУ", None))
        self.chkNoFinanceDetail.setText(_translate("ArrivedDepartedPatients", "Не детализировать по типам финансирования", None))
        self.chkReanimation.setText(_translate("ArrivedDepartedPatients", "Включая реанимацию", None))

from library.DateEdit import CDateEdit
from library.RBListBox import CRBListBox
