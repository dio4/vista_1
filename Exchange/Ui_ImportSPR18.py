# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ImportSPR18.ui'
#
# Created: Fri Mar  6 17:15:48 2015
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(474, 503)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
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
        self.gridLayout.addLayout(self.hboxlayout, 4, 0, 1, 8)
        self.log = QtGui.QTextBrowser(Dialog)
        self.log.setObjectName(_fromUtf8("log"))
        self.gridLayout.addWidget(self.log, 3, 0, 1, 8)
        self.progressBar = CProgressBar(Dialog)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 2, 0, 1, 8)
        self.btnView = QtGui.QPushButton(Dialog)
        self.btnView.setObjectName(_fromUtf8("btnView"))
        self.gridLayout.addWidget(self.btnView, 0, 7, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.edtFileName = QtGui.QLineEdit(Dialog)
        self.edtFileName.setText(_fromUtf8(""))
        self.edtFileName.setReadOnly(True)
        self.edtFileName.setObjectName(_fromUtf8("edtFileName"))
        self.horizontalLayout.addWidget(self.edtFileName)
        self.btnSelectFile = QtGui.QToolButton(Dialog)
        self.btnSelectFile.setObjectName(_fromUtf8("btnSelectFile"))
        self.horizontalLayout.addWidget(self.btnSelectFile)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 1, 1, 6)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Загрузка услуг из SPR18", None))
        self.label.setText(_translate("Dialog", "импортировать из", None))
        self.btnImport.setText(_translate("Dialog", "начать импортирование", None))
        self.labelNum.setText(_translate("Dialog", "всего записей в источнике:", None))
        self.btnClose.setText(_translate("Dialog", "закрыть", None))
        self.btnView.setText(_translate("Dialog", "Просмотреть", None))
        self.btnSelectFile.setText(_translate("Dialog", "...", None))

from library.ProgressBar import CProgressBar
