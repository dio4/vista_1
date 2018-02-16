# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DentalFormula.ui'
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

class Ui_DentalFormula(object):
    def setupUi(self, DentalFormula):
        DentalFormula.setObjectName(_fromUtf8("DentalFormula"))
        DentalFormula.resize(1194, 632)
        self.verticalLayout = QtGui.QVBoxLayout(DentalFormula)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.tblFormula = DentalFormulaView(DentalFormula)
        self.tblFormula.setObjectName(_fromUtf8("tblFormula"))
        self.horizontalLayout.addWidget(self.tblFormula)
        self.groupBox = QtGui.QGroupBox(DentalFormula)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMaximumSize(QtCore.QSize(300, 16777215))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.tblStates = StatesTableView(self.groupBox)
        self.tblStates.setEnabled(False)
        self.tblStates.setObjectName(_fromUtf8("tblStates"))
        self.verticalLayout_2.addWidget(self.tblStates)
        self.btnResetStates = QtGui.QPushButton(self.groupBox)
        self.btnResetStates.setObjectName(_fromUtf8("btnResetStates"))
        self.verticalLayout_2.addWidget(self.btnResetStates)
        self.horizontalLayout.addWidget(self.groupBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.btnHistoryToggle = QtGui.QPushButton(DentalFormula)
        self.btnHistoryToggle.setCheckable(True)
        self.btnHistoryToggle.setObjectName(_fromUtf8("btnHistoryToggle"))
        self.verticalLayout.addWidget(self.btnHistoryToggle)
        self.wdgHistory = QtGui.QWidget(DentalFormula)
        self.wdgHistory.setObjectName(_fromUtf8("wdgHistory"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.wdgHistory)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.lstHistory = QtGui.QListView(self.wdgHistory)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lstHistory.sizePolicy().hasHeightForWidth())
        self.lstHistory.setSizePolicy(sizePolicy)
        self.lstHistory.setObjectName(_fromUtf8("lstHistory"))
        self.horizontalLayout_2.addWidget(self.lstHistory)
        self.tblFormulaHistoryView = DentalFormulaView(self.wdgHistory)
        self.tblFormulaHistoryView.setObjectName(_fromUtf8("tblFormulaHistoryView"))
        self.horizontalLayout_2.addWidget(self.tblFormulaHistoryView)
        self.verticalLayout.addWidget(self.wdgHistory)

        self.retranslateUi(DentalFormula)
        QtCore.QObject.connect(self.btnHistoryToggle, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.wdgHistory.setVisible)
        QtCore.QMetaObject.connectSlotsByName(DentalFormula)
        DentalFormula.setTabOrder(self.tblFormula, self.tblStates)
        DentalFormula.setTabOrder(self.tblStates, self.btnResetStates)
        DentalFormula.setTabOrder(self.btnResetStates, self.btnHistoryToggle)
        DentalFormula.setTabOrder(self.btnHistoryToggle, self.lstHistory)
        DentalFormula.setTabOrder(self.lstHistory, self.tblFormulaHistoryView)

    def retranslateUi(self, DentalFormula):
        DentalFormula.setWindowTitle(_translate("DentalFormula", "Зубная формула", None))
        self.groupBox.setTitle(_translate("DentalFormula", "Состояния", None))
        self.btnResetStates.setText(_translate("DentalFormula", "Очистить", None))
        self.btnHistoryToggle.setText(_translate("DentalFormula", "Показать историю", None))

from Forms.F043v2.DentalFormula import DentalFormulaView, StatesTableView
