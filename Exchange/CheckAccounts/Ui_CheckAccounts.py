# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_CheckAccounts.ui'
#
# Created: Mon Aug 12 13:48:26 2013
#      by: PyQt4 UI code generator 4.9.6
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

class Ui_CheckAccounts(object):
    def setupUi(self, CheckAccounts):
        CheckAccounts.setObjectName(_fromUtf8("CheckAccounts"))
        CheckAccounts.resize(515, 500)
        CheckAccounts.setSizeGripEnabled(False)
        CheckAccounts.setModal(False)
        self.lMain = QtGui.QVBoxLayout(CheckAccounts)
        self.lMain.setObjectName(_fromUtf8("lMain"))
        self.gbAdditionalRBs = QtGui.QGroupBox(CheckAccounts)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gbAdditionalRBs.sizePolicy().hasHeightForWidth())
        self.gbAdditionalRBs.setSizePolicy(sizePolicy)
        self.gbAdditionalRBs.setObjectName(_fromUtf8("gbAdditionalRBs"))
        self.verticalLayout = QtGui.QVBoxLayout(self.gbAdditionalRBs)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.lRBPath = QtGui.QHBoxLayout()
        self.lRBPath.setObjectName(_fromUtf8("lRBPath"))
        self.lblRBPath = QtGui.QLabel(self.gbAdditionalRBs)
        self.lblRBPath.setObjectName(_fromUtf8("lblRBPath"))
        self.lRBPath.addWidget(self.lblRBPath)
        self.edtRBPath = QtGui.QLineEdit(self.gbAdditionalRBs)
        self.edtRBPath.setReadOnly(True)
        self.edtRBPath.setObjectName(_fromUtf8("edtRBPath"))
        self.lRBPath.addWidget(self.edtRBPath)
        self.btnRBPath = QtGui.QPushButton(self.gbAdditionalRBs)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnRBPath.sizePolicy().hasHeightForWidth())
        self.btnRBPath.setSizePolicy(sizePolicy)
        self.btnRBPath.setMaximumSize(QtCore.QSize(25, 16777215))
        self.btnRBPath.setObjectName(_fromUtf8("btnRBPath"))
        self.lRBPath.addWidget(self.btnRBPath)
        self.verticalLayout.addLayout(self.lRBPath)
        self.pbAdditionalRBs = QtGui.QProgressBar(self.gbAdditionalRBs)
        self.pbAdditionalRBs.setProperty("value", 0)
        self.pbAdditionalRBs.setObjectName(_fromUtf8("pbAdditionalRBs"))
        self.verticalLayout.addWidget(self.pbAdditionalRBs)
        self.tbAdditionalRBs = QtGui.QTextBrowser(self.gbAdditionalRBs)
        self.tbAdditionalRBs.setObjectName(_fromUtf8("tbAdditionalRBs"))
        self.verticalLayout.addWidget(self.tbAdditionalRBs)
        self.lMain.addWidget(self.gbAdditionalRBs)
        self.gbAccount = QtGui.QGroupBox(CheckAccounts)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gbAccount.sizePolicy().hasHeightForWidth())
        self.gbAccount.setSizePolicy(sizePolicy)
        self.gbAccount.setObjectName(_fromUtf8("gbAccount"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.gbAccount)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.lPath = QtGui.QHBoxLayout()
        self.lPath.setObjectName(_fromUtf8("lPath"))
        self.lbAccountPath = QtGui.QLabel(self.gbAccount)
        self.lbAccountPath.setObjectName(_fromUtf8("lbAccountPath"))
        self.lPath.addWidget(self.lbAccountPath)
        self.edtAccountPath = QtGui.QLineEdit(self.gbAccount)
        self.edtAccountPath.setReadOnly(True)
        self.edtAccountPath.setObjectName(_fromUtf8("edtAccountPath"))
        self.lPath.addWidget(self.edtAccountPath)
        self.btnAccountPath = QtGui.QPushButton(self.gbAccount)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnAccountPath.sizePolicy().hasHeightForWidth())
        self.btnAccountPath.setSizePolicy(sizePolicy)
        self.btnAccountPath.setMaximumSize(QtCore.QSize(25, 16777215))
        self.btnAccountPath.setObjectName(_fromUtf8("btnAccountPath"))
        self.lPath.addWidget(self.btnAccountPath)
        self.verticalLayout_2.addLayout(self.lPath)
        self.pbAccount = QtGui.QProgressBar(self.gbAccount)
        self.pbAccount.setProperty("value", 0)
        self.pbAccount.setObjectName(_fromUtf8("pbAccount"))
        self.verticalLayout_2.addWidget(self.pbAccount)
        self.tbAccount = QtGui.QTextBrowser(self.gbAccount)
        self.tbAccount.setObjectName(_fromUtf8("tbAccount"))
        self.verticalLayout_2.addWidget(self.tbAccount)
        self.lMain.addWidget(self.gbAccount)
        self.chkOnlyData = QtGui.QCheckBox(CheckAccounts)
        self.chkOnlyData.setObjectName(_fromUtf8("chkOnlyData"))
        self.lMain.addWidget(self.chkOnlyData)
        self.lBottom = QtGui.QHBoxLayout()
        self.lBottom.setObjectName(_fromUtf8("lBottom"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.lBottom.addItem(spacerItem)
        self.btnCheck = QtGui.QPushButton(CheckAccounts)
        self.btnCheck.setObjectName(_fromUtf8("btnCheck"))
        self.lBottom.addWidget(self.btnCheck)
        self.btnClose = QtGui.QPushButton(CheckAccounts)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.lBottom.addWidget(self.btnClose)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.lBottom.addItem(spacerItem1)
        self.lMain.addLayout(self.lBottom)

        self.retranslateUi(CheckAccounts)
        QtCore.QMetaObject.connectSlotsByName(CheckAccounts)

    def retranslateUi(self, CheckAccounts):
        CheckAccounts.setWindowTitle(_translate("CheckAccounts", "Проверка реестров", None))
        self.gbAdditionalRBs.setTitle(_translate("CheckAccounts", "Справочники", None))
        self.pbAdditionalRBs.setFormat(_translate("CheckAccounts", "%v", None))
        self.gbAccount.setTitle(_translate("CheckAccounts", "Реестр", None))
        self.lblRBPath.setText(_translate("CheckAccounts", "Путь:", None))
        self.btnRBPath.setText(_translate("CheckAccounts", "...", None))
        self.lbAccountPath.setText(_translate("CheckAccounts", "Путь:", None))
        self.btnAccountPath.setText(_translate("CheckAccounts", "...", None))
        self.pbAccount.setFormat(_translate("CheckAccounts", "%v", None))
        self.chkOnlyData.setText(_translate("CheckAccounts", "Только загрузка данных", None))
        self.btnCheck.setText(_translate("CheckAccounts", "Проверить", None))
        self.btnClose.setText(_translate("CheckAccounts", "Закрыть", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    CheckAccounts = QtGui.QDialog()
    ui = Ui_CheckAccounts()
    ui.setupUi(CheckAccounts)
    CheckAccounts.show()
    sys.exit(app.exec_())

