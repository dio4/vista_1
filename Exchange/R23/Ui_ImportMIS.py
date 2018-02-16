# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ImportMIS.ui'
#
# Created: Mon Nov 30 10:46:53 2015
#      by: PyQt4 UI code generator 4.11.3
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(923, 688)
        self.verticalLayout_2 = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.tabHelp = QtGui.QTabWidget(Dialog)
        self.tabHelp.setObjectName(_fromUtf8("tabHelp"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.gridLayout_2 = QtGui.QGridLayout(self.tab)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setMargin(0)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.lblLoadFrom = QtGui.QLabel(self.tab)
        self.lblLoadFrom.setObjectName(_fromUtf8("lblLoadFrom"))
        self.gridLayout_3.addWidget(self.lblLoadFrom, 0, 0, 1, 1)
        self.edtFileName = QtGui.QLineEdit(self.tab)
        self.edtFileName.setObjectName(_fromUtf8("edtFileName"))
        self.gridLayout_3.addWidget(self.edtFileName, 0, 1, 1, 1)
        self.btnSelectFile = QtGui.QToolButton(self.tab)
        self.btnSelectFile.setObjectName(_fromUtf8("btnSelectFile"))
        self.gridLayout_3.addWidget(self.btnSelectFile, 0, 2, 1, 1)
        self.progressBar = CProgressBar(self.tab)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout_3.addWidget(self.progressBar, 1, 0, 1, 3)
        self.logBrowser = QtGui.QTextBrowser(self.tab)
        self.logBrowser.setObjectName(_fromUtf8("logBrowser"))
        self.gridLayout_3.addWidget(self.logBrowser, 2, 0, 1, 3)
        self.gridLayout_2.addLayout(self.gridLayout_3, 1, 1, 1, 1)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.chkReplaceClientInfo = QtGui.QCheckBox(self.tab)
        self.chkReplaceClientInfo.setObjectName(_fromUtf8("chkReplaceClientInfo"))
        self.verticalLayout.addWidget(self.chkReplaceClientInfo)
        self.chkReplaceSNILS = QtGui.QCheckBox(self.tab)
        self.chkReplaceSNILS.setObjectName(_fromUtf8("chkReplaceSNILS"))
        self.verticalLayout.addWidget(self.chkReplaceSNILS)
        self.chkReplaceUDL = QtGui.QCheckBox(self.tab)
        self.chkReplaceUDL.setObjectName(_fromUtf8("chkReplaceUDL"))
        self.verticalLayout.addWidget(self.chkReplaceUDL)
        self.chkReplacePolice = QtGui.QCheckBox(self.tab)
        self.chkReplacePolice.setObjectName(_fromUtf8("chkReplacePolice"))
        self.verticalLayout.addWidget(self.chkReplacePolice)
        self.chkDetachDead = QtGui.QCheckBox(self.tab)
        self.chkDetachDead.setObjectName(_fromUtf8("chkDetachDead"))
        self.verticalLayout.addWidget(self.chkDetachDead)
        self.gridLayout_2.addLayout(self.verticalLayout, 2, 1, 1, 1)
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.btnImport = QtGui.QPushButton(self.tab)
        self.btnImport.setObjectName(_fromUtf8("btnImport"))
        self.hboxlayout.addWidget(self.btnImport)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.lblNum = QtGui.QLabel(self.tab)
        self.lblNum.setObjectName(_fromUtf8("lblNum"))
        self.hboxlayout.addWidget(self.lblNum)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem1)
        self.btnShowErrors = QtGui.QPushButton(self.tab)
        self.btnShowErrors.setObjectName(_fromUtf8("btnShowErrors"))
        self.hboxlayout.addWidget(self.btnShowErrors)
        self.btnClose = QtGui.QPushButton(self.tab)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.hboxlayout.addWidget(self.btnClose)
        self.gridLayout_2.addLayout(self.hboxlayout, 3, 1, 1, 1)
        self.tabHelp.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.tab_2)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.txtHelp = QtGui.QTextBrowser(self.tab_2)
        self.txtHelp.setObjectName(_fromUtf8("txtHelp"))
        self.verticalLayout_3.addWidget(self.txtHelp)
        self.tabHelp.addTab(self.tab_2, _fromUtf8(""))
        self.verticalLayout_2.addWidget(self.tabHelp)

        self.retranslateUi(Dialog)
        self.tabHelp.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.chkReplaceClientInfo, self.chkReplaceSNILS)
        Dialog.setTabOrder(self.chkReplaceSNILS, self.chkReplaceUDL)
        Dialog.setTabOrder(self.chkReplaceUDL, self.chkReplacePolice)
        Dialog.setTabOrder(self.chkReplacePolice, self.chkDetachDead)
        Dialog.setTabOrder(self.chkDetachDead, self.btnImport)
        Dialog.setTabOrder(self.btnImport, self.btnShowErrors)
        Dialog.setTabOrder(self.btnShowErrors, self.btnClose)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Импорт пациентов из МИАЦ в МИС", None))
        self.lblLoadFrom.setText(_translate("Dialog", "Загрузить из", None))
        self.btnSelectFile.setText(_translate("Dialog", "...", None))
        self.chkReplaceClientInfo.setText(_translate("Dialog", "Заменить данные пациента", None))
        self.chkReplaceSNILS.setText(_translate("Dialog", "Заменить СНИЛС", None))
        self.chkReplaceUDL.setText(_translate("Dialog", "Заменить документ УДЛ", None))
        self.chkReplacePolice.setText(_translate("Dialog", "Заменить полисные данне", None))
        self.chkDetachDead.setText(_translate("Dialog", "Откретить умерших", None))
        self.btnImport.setText(_translate("Dialog", "Начать импортирование", None))
        self.lblNum.setText(_translate("Dialog", "Всего записей в источнике/не прошли контроль МИАЦ-ТФОМС: 0/0", None))
        self.btnShowErrors.setText(_translate("Dialog", "Показать ошибки", None))
        self.btnClose.setText(_translate("Dialog", "Закрыть", None))
        self.tabHelp.setTabText(self.tabHelp.indexOf(self.tab), _translate("Dialog", "Импорт", None))
        self.tabHelp.setTabText(self.tabHelp.indexOf(self.tab_2), _translate("Dialog", "Справка", None))

from library.ProgressBar import CProgressBar
