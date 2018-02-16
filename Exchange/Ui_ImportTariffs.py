# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ImportTariffs.ui'
#
# Created: Wed Jul 03 15:44:53 2013
#      by: PyQt4 UI code generator 4.10
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
        Dialog.resize(543, 468)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.hboxlayout.addWidget(self.label)
        self.splitter = QtGui.QSplitter(Dialog)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.edtFileName = QtGui.QLineEdit(self.splitter)
        self.edtFileName.setText(_fromUtf8(""))
        self.edtFileName.setReadOnly(True)
        self.edtFileName.setObjectName(_fromUtf8("edtFileName"))
        self.edtIP = QtGui.QLineEdit(self.splitter)
        self.edtIP.setReadOnly(True)
        self.edtIP.setObjectName(_fromUtf8("edtIP"))
        self.hboxlayout.addWidget(self.splitter)
        self.gridLayout.addLayout(self.hboxlayout, 0, 0, 1, 3)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.chkLoadChildren = QtGui.QCheckBox(Dialog)
        self.chkLoadChildren.setChecked(True)
        self.chkLoadChildren.setObjectName(_fromUtf8("chkLoadChildren"))
        self.verticalLayout.addWidget(self.chkLoadChildren)
        self.chkLoadAdult = QtGui.QCheckBox(Dialog)
        self.chkLoadAdult.setChecked(True)
        self.chkLoadAdult.setObjectName(_fromUtf8("chkLoadAdult"))
        self.verticalLayout.addWidget(self.chkLoadAdult)
        self.gridLayout.addLayout(self.verticalLayout, 1, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(57, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 1, 1, 1)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.chkAmb = QtGui.QCheckBox(Dialog)
        self.chkAmb.setChecked(True)
        self.chkAmb.setObjectName(_fromUtf8("chkAmb"))
        self.verticalLayout_2.addWidget(self.chkAmb)
        self.chkStom = QtGui.QCheckBox(Dialog)
        self.chkStom.setObjectName(_fromUtf8("chkStom"))
        self.verticalLayout_2.addWidget(self.chkStom)
        self.chkCompleteCase = QtGui.QCheckBox(Dialog)
        self.chkCompleteCase.setObjectName(_fromUtf8("chkCompleteCase"))
        self.verticalLayout_2.addWidget(self.chkCompleteCase)
        self.chkDailyStat = QtGui.QCheckBox(Dialog)
        self.chkDailyStat.setObjectName(_fromUtf8("chkDailyStat"))
        self.verticalLayout_2.addWidget(self.chkDailyStat)
        self.chkOperV = QtGui.QCheckBox(Dialog)
        self.chkOperV.setObjectName(_fromUtf8("chkOperV"))
        self.verticalLayout_2.addWidget(self.chkOperV)
        self.gridLayout.addLayout(self.verticalLayout_2, 1, 2, 1, 1)
        self.progressBar = QtGui.QProgressBar(Dialog)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 2, 0, 1, 3)
        self.statusLabel = QtGui.QLabel(Dialog)
        self.statusLabel.setText(_fromUtf8(""))
        self.statusLabel.setObjectName(_fromUtf8("statusLabel"))
        self.gridLayout.addWidget(self.statusLabel, 3, 0, 1, 3)
        self.log = QtGui.QTextBrowser(Dialog)
        self.log.setObjectName(_fromUtf8("log"))
        self.gridLayout.addWidget(self.log, 4, 0, 1, 3)
        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setObjectName(_fromUtf8("hboxlayout1"))
        self.btnImport = QtGui.QPushButton(Dialog)
        self.btnImport.setObjectName(_fromUtf8("btnImport"))
        self.hboxlayout1.addWidget(self.btnImport)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem1)
        self.labelNum = QtGui.QLabel(Dialog)
        self.labelNum.setObjectName(_fromUtf8("labelNum"))
        self.hboxlayout1.addWidget(self.labelNum)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem2)
        self.btnClose = QtGui.QPushButton(Dialog)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.hboxlayout1.addWidget(self.btnClose)
        self.gridLayout.addLayout(self.hboxlayout1, 5, 0, 1, 3)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Загрузка тарифов из ЕИС", None))
        self.label.setText(_translate("Dialog", "импортировать из", None))
        self.chkLoadChildren.setText(_translate("Dialog", "загружать детские", None))
        self.chkLoadAdult.setText(_translate("Dialog", "загружать взрослые", None))
        self.chkAmb.setText(_translate("Dialog", "загружать амбулаторные тарифы", None))
        self.chkStom.setText(_translate("Dialog", "загружать стоматологические тарифы", None))
        self.chkCompleteCase.setText(_translate("Dialog", "загружать законченные случаи", None))
        self.chkDailyStat.setText(_translate("Dialog", "загружать тарифы дневного стационара", None))
        self.chkOperV.setText(_translate("Dialog", "Загружать оперативные вмешательства (ДС)", None))
        self.btnImport.setText(_translate("Dialog", "начать импортирование", None))
        self.labelNum.setText(_translate("Dialog", "всего записей в источнике:", None))
        self.btnClose.setText(_translate("Dialog", "закрыть", None))

