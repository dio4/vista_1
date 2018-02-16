# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ImportFormularyDLO.ui'
#
# Created: Tue Mar 17 15:06:35 2015
#      by: PyQt4 UI code generator 4.11
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
        Dialog.resize(553, 420)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.verticalLayout_5 = QtGui.QVBoxLayout()
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self._2 = QtGui.QHBoxLayout()
        self._2.setObjectName(_fromUtf8("_2"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self._2.addWidget(self.label)
        self.edtFolderName = QtGui.QLineEdit(Dialog)
        self.edtFolderName.setText(_fromUtf8(""))
        self.edtFolderName.setReadOnly(True)
        self.edtFolderName.setObjectName(_fromUtf8("edtFolderName"))
        self._2.addWidget(self.edtFolderName)
        self.btnSelectFolder = QtGui.QToolButton(Dialog)
        self.btnSelectFolder.setObjectName(_fromUtf8("btnSelectFolder"))
        self._2.addWidget(self.btnSelectFolder)
        self.verticalLayout_5.addLayout(self._2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout_5.addLayout(self.horizontalLayout)
        self.chkUpdate = QtGui.QCheckBox(Dialog)
        self.chkUpdate.setObjectName(_fromUtf8("chkUpdate"))
        self.verticalLayout_5.addWidget(self.chkUpdate)
        self.progressBar = QtGui.QProgressBar(Dialog)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.verticalLayout_5.addWidget(self.progressBar)
        self.statusLabel = QtGui.QLabel(Dialog)
        self.statusLabel.setText(_fromUtf8(""))
        self.statusLabel.setObjectName(_fromUtf8("statusLabel"))
        self.verticalLayout_5.addWidget(self.statusLabel)
        self.log = QtGui.QTextBrowser(Dialog)
        self.log.setObjectName(_fromUtf8("log"))
        self.verticalLayout_5.addWidget(self.log)
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.btnImport = QtGui.QPushButton(Dialog)
        self.btnImport.setObjectName(_fromUtf8("btnImport"))
        self.hboxlayout.addWidget(self.btnImport)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.labelNum = QtGui.QLabel(Dialog)
        self.labelNum.setObjectName(_fromUtf8("labelNum"))
        self.hboxlayout.addWidget(self.labelNum)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem1)
        self.btnClose = QtGui.QPushButton(Dialog)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.hboxlayout.addWidget(self.btnClose)
        self.verticalLayout_5.addLayout(self.hboxlayout)
        self.verticalLayout.addLayout(self.verticalLayout_5)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.edtFolderName, self.btnSelectFolder)
        Dialog.setTabOrder(self.btnSelectFolder, self.log)
        Dialog.setTabOrder(self.log, self.btnImport)
        Dialog.setTabOrder(self.btnImport, self.btnClose)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Импорт формуляра из справочника ДЛО", None))
        self.label.setText(_translate("Dialog", "Импортировать из", None))
        self.btnSelectFolder.setText(_translate("Dialog", "...", None))
        self.chkUpdate.setText(_translate("Dialog", "Режим обновления", None))
        self.btnImport.setText(_translate("Dialog", "Начать импортирование", None))
        self.labelNum.setText(_translate("Dialog", "Всего записей в источнике:", None))
        self.btnClose.setText(_translate("Dialog", "Закрыть", None))

