# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ImportR46XML.ui'
#
# Created: Wed Mar 04 00:55:03 2015
#      by: PyQt4 UI code generator 4.11.2
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
        Dialog.resize(581, 496)
        self.gridlayout = QtGui.QGridLayout(Dialog)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.hboxlayout.addWidget(self.label)
        self.edtFileName = QtGui.QLineEdit(Dialog)
        self.edtFileName.setObjectName(_fromUtf8("edtFileName"))
        self.hboxlayout.addWidget(self.edtFileName)
        self.btnSelectFile = QtGui.QToolButton(Dialog)
        self.btnSelectFile.setObjectName(_fromUtf8("btnSelectFile"))
        self.hboxlayout.addWidget(self.btnSelectFile)
        self.btnView = QtGui.QPushButton(Dialog)
        self.btnView.setObjectName(_fromUtf8("btnView"))
        self.hboxlayout.addWidget(self.btnView)
        self.gridlayout.addLayout(self.hboxlayout, 0, 0, 1, 1)
        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setObjectName(_fromUtf8("hboxlayout1"))
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.hboxlayout1.addWidget(self.label_2)
        self.edtConfirmation = QtGui.QLineEdit(Dialog)
        self.edtConfirmation.setObjectName(_fromUtf8("edtConfirmation"))
        self.hboxlayout1.addWidget(self.edtConfirmation)
        self.gridlayout.addLayout(self.hboxlayout1, 1, 0, 1, 1)
        self.chkOnlyCurrentAccount = QtGui.QCheckBox(Dialog)
        self.chkOnlyCurrentAccount.setChecked(True)
        self.chkOnlyCurrentAccount.setObjectName(_fromUtf8("chkOnlyCurrentAccount"))
        self.gridlayout.addWidget(self.chkOnlyCurrentAccount, 2, 0, 1, 1)
        self.chkImportPayed = QtGui.QCheckBox(Dialog)
        self.chkImportPayed.setEnabled(False)
        self.chkImportPayed.setChecked(True)
        self.chkImportPayed.setObjectName(_fromUtf8("chkImportPayed"))
        self.gridlayout.addWidget(self.chkImportPayed, 3, 0, 1, 1)
        self.chkImportRefused = QtGui.QCheckBox(Dialog)
        self.chkImportRefused.setChecked(True)
        self.chkImportRefused.setObjectName(_fromUtf8("chkImportRefused"))
        self.gridlayout.addWidget(self.chkImportRefused, 4, 0, 1, 1)
        self.progressBar = CProgressBar(Dialog)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridlayout.addWidget(self.progressBar, 5, 0, 1, 1)
        self.stat = QtGui.QLabel(Dialog)
        self.stat.setText(_fromUtf8(""))
        self.stat.setObjectName(_fromUtf8("stat"))
        self.gridlayout.addWidget(self.stat, 6, 0, 1, 1)
        self.log = QtGui.QTextBrowser(Dialog)
        self.log.setObjectName(_fromUtf8("log"))
        self.gridlayout.addWidget(self.log, 7, 0, 1, 1)
        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setSpacing(6)
        self.hboxlayout2.setMargin(0)
        self.hboxlayout2.setObjectName(_fromUtf8("hboxlayout2"))
        self.btnImport = QtGui.QPushButton(Dialog)
        self.btnImport.setObjectName(_fromUtf8("btnImport"))
        self.hboxlayout2.addWidget(self.btnImport)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout2.addItem(spacerItem)
        self.labelNum = QtGui.QLabel(Dialog)
        self.labelNum.setObjectName(_fromUtf8("labelNum"))
        self.hboxlayout2.addWidget(self.labelNum)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout2.addItem(spacerItem1)
        self.btnClose = QtGui.QPushButton(Dialog)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.hboxlayout2.addWidget(self.btnClose)
        self.gridlayout.addLayout(self.hboxlayout2, 8, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Загрузка счетов оплаты для Республики Крым", None))
        self.label.setText(_translate("Dialog", "импортировать из", None))
        self.btnSelectFile.setText(_translate("Dialog", "...", None))
        self.btnView.setText(_translate("Dialog", "Просмотреть", None))
        self.label_2.setText(_translate("Dialog", "подтверждение", None))
        self.edtConfirmation.setText(_translate("Dialog", "б/н", None))
        self.chkOnlyCurrentAccount.setText(_translate("Dialog", "только текущий счёт", None))
        self.chkImportPayed.setText(_translate("Dialog", "загружать оплаченные", None))
        self.chkImportRefused.setText(_translate("Dialog", "загружать отказы", None))
        self.btnImport.setText(_translate("Dialog", "начать импортирование", None))
        self.labelNum.setText(_translate("Dialog", "всего записей в источнике:", None))
        self.btnClose.setText(_translate("Dialog", "закрыть", None))

from library.ProgressBar import CProgressBar
