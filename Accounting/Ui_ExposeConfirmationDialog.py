# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ExposeConfirmationDialog.ui'
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

class Ui_ExposeConfirmationDialog(object):
    def setupUi(self, ExposeConfirmationDialog):
        ExposeConfirmationDialog.setObjectName(_fromUtf8("ExposeConfirmationDialog"))
        ExposeConfirmationDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ExposeConfirmationDialog.resize(828, 276)
        ExposeConfirmationDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(ExposeConfirmationDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.chkShowStats = QtGui.QCheckBox(ExposeConfirmationDialog)
        self.chkShowStats.setObjectName(_fromUtf8("chkShowStats"))
        self.gridlayout.addWidget(self.chkShowStats, 6, 0, 1, 1)
        self.chkMesCheck = QtGui.QCheckBox(ExposeConfirmationDialog)
        self.chkMesCheck.setObjectName(_fromUtf8("chkMesCheck"))
        self.gridlayout.addWidget(self.chkMesCheck, 4, 0, 1, 1)
        self.chkReExpose = QtGui.QCheckBox(ExposeConfirmationDialog)
        self.chkReExpose.setObjectName(_fromUtf8("chkReExpose"))
        self.gridlayout.addWidget(self.chkReExpose, 2, 0, 1, 1)
        self.chkCalendarDaysLength = QtGui.QCheckBox(ExposeConfirmationDialog)
        self.chkCalendarDaysLength.setObjectName(_fromUtf8("chkCalendarDaysLength"))
        self.gridlayout.addWidget(self.chkCalendarDaysLength, 5, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 61, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 9, 0, 1, 1)
        self.lblMessage = QtGui.QLabel(ExposeConfirmationDialog)
        self.lblMessage.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.lblMessage.setObjectName(_fromUtf8("lblMessage"))
        self.gridlayout.addWidget(self.lblMessage, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ExposeConfirmationDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 10, 0, 1, 1)
        self.chkLock = QtGui.QCheckBox(ExposeConfirmationDialog)
        self.chkLock.setObjectName(_fromUtf8("chkLock"))
        self.gridlayout.addWidget(self.chkLock, 7, 0, 1, 1)
        self.chkFilterPaymentByOrgStructure = QtGui.QCheckBox(ExposeConfirmationDialog)
        self.chkFilterPaymentByOrgStructure.setObjectName(_fromUtf8("chkFilterPaymentByOrgStructure"))
        self.gridlayout.addWidget(self.chkFilterPaymentByOrgStructure, 1, 0, 1, 2)
        self.chkSeparateReExpose = QtGui.QCheckBox(ExposeConfirmationDialog)
        self.chkSeparateReExpose.setEnabled(False)
        self.chkSeparateReExpose.setChecked(True)
        self.chkSeparateReExpose.setObjectName(_fromUtf8("chkSeparateReExpose"))
        self.gridlayout.addWidget(self.chkSeparateReExpose, 3, 0, 1, 1)
        self.chkAcceptNewKSLPForChild = QtGui.QCheckBox(ExposeConfirmationDialog)
        self.chkAcceptNewKSLPForChild.setObjectName(_fromUtf8("chkAcceptNewKSLPForChild"))
        self.gridlayout.addWidget(self.chkAcceptNewKSLPForChild, 8, 0, 1, 1)

        self.retranslateUi(ExposeConfirmationDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ExposeConfirmationDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ExposeConfirmationDialog.reject)
        QtCore.QObject.connect(self.chkReExpose, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.chkSeparateReExpose.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(ExposeConfirmationDialog)
        ExposeConfirmationDialog.setTabOrder(self.chkFilterPaymentByOrgStructure, self.chkReExpose)
        ExposeConfirmationDialog.setTabOrder(self.chkReExpose, self.chkSeparateReExpose)
        ExposeConfirmationDialog.setTabOrder(self.chkSeparateReExpose, self.chkMesCheck)
        ExposeConfirmationDialog.setTabOrder(self.chkMesCheck, self.buttonBox)

    def retranslateUi(self, ExposeConfirmationDialog):
        ExposeConfirmationDialog.setWindowTitle(_translate("ExposeConfirmationDialog", "Внимание!", None))
        self.chkShowStats.setText(_translate("ExposeConfirmationDialog", "Выводить статистику", None))
        self.chkMesCheck.setText(_translate("ExposeConfirmationDialog", "Проверять на соответствие МЭС", None))
        self.chkReExpose.setText(_translate("ExposeConfirmationDialog", "Выполнять перевыставление по имеющимся отказам", None))
        self.chkCalendarDaysLength.setText(_translate("ExposeConfirmationDialog", "Длительность лечения в круглосуточном стационаре определяется в календарных днях", None))
        self.lblMessage.setText(_translate("ExposeConfirmationDialog", "message", None))
        self.chkLock.setText(_translate("ExposeConfirmationDialog", "Блокировать обращения в выставленных счетах", None))
        self.chkFilterPaymentByOrgStructure.setText(_translate("ExposeConfirmationDialog", "При выставлении счетов учитывать текущее подразделение", None))
        self.chkSeparateReExpose.setText(_translate("ExposeConfirmationDialog", "Перевыставлять в отдельный счет", None))
        self.chkAcceptNewKSLPForChild.setText(_translate("ExposeConfirmationDialog", "Применить КСЛП=1,8 для детей до 1 года (только для специализированных инфекционных стационаров краевого уровня)", None))

