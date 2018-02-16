# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ImportFLCR23.ui'
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(604, 150)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self._2 = QtGui.QHBoxLayout()
        self._2.setMargin(0)
        self._2.setSpacing(6)
        self._2.setObjectName(_fromUtf8("_2"))
        self.lblLoadFrom = QtGui.QLabel(Dialog)
        self.lblLoadFrom.setObjectName(_fromUtf8("lblLoadFrom"))
        self._2.addWidget(self.lblLoadFrom)
        self.edtFileName = QtGui.QLineEdit(Dialog)
        self.edtFileName.setObjectName(_fromUtf8("edtFileName"))
        self._2.addWidget(self.edtFileName)
        self.btnSelectFile = QtGui.QToolButton(Dialog)
        self.btnSelectFile.setObjectName(_fromUtf8("btnSelectFile"))
        self._2.addWidget(self.btnSelectFile)
        self.gridLayout.addLayout(self._2, 0, 0, 1, 1)
        self.progressBar = CProgressBar(Dialog)
        self.progressBar.setMaximum(1)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setFormat(_fromUtf8(""))
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 1, 0, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.chkAgree = QtGui.QCheckBox(Dialog)
        self.chkAgree.setEnabled(False)
        self.chkAgree.setObjectName(_fromUtf8("chkAgree"))
        self.horizontalLayout_2.addWidget(self.chkAgree)
        self.chkImportExternal = QtGui.QCheckBox(Dialog)
        self.chkImportExternal.setEnabled(False)
        self.chkImportExternal.setObjectName(_fromUtf8("chkImportExternal"))
        self.horizontalLayout_2.addWidget(self.chkImportExternal)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.gridLayout.addLayout(self.horizontalLayout_2, 2, 0, 1, 1)
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.btnImport = QtGui.QPushButton(Dialog)
        self.btnImport.setEnabled(False)
        self.btnImport.setObjectName(_fromUtf8("btnImport"))
        self.hboxlayout.addWidget(self.btnImport)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem1)
        self.lblNum = QtGui.QLabel(Dialog)
        self.lblNum.setObjectName(_fromUtf8("lblNum"))
        self.hboxlayout.addWidget(self.lblNum)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem2)
        self.btnClose = QtGui.QPushButton(Dialog)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.hboxlayout.addWidget(self.btnClose)
        self.gridLayout.addLayout(self.hboxlayout, 3, 0, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem3, 4, 0, 1, 1)
        self.logBrowser = QtGui.QTextBrowser(Dialog)
        self.logBrowser.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.logBrowser.sizePolicy().hasHeightForWidth())
        self.logBrowser.setSizePolicy(sizePolicy)
        self.logBrowser.setObjectName(_fromUtf8("logBrowser"))
        self.gridLayout.addWidget(self.logBrowser, 5, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.chkAgree, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.btnImport.setEnabled)
        QtCore.QObject.connect(self.btnClose, QtCore.SIGNAL(_fromUtf8("clicked()")), Dialog.close)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.edtFileName, self.btnSelectFile)
        Dialog.setTabOrder(self.btnSelectFile, self.chkAgree)
        Dialog.setTabOrder(self.chkAgree, self.chkImportExternal)
        Dialog.setTabOrder(self.chkImportExternal, self.btnImport)
        Dialog.setTabOrder(self.btnImport, self.btnClose)
        Dialog.setTabOrder(self.btnClose, self.logBrowser)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Импорт данных ФЛК", None))
        self.lblLoadFrom.setText(_translate("Dialog", "Загрузить из", None))
        self.btnSelectFile.setText(_translate("Dialog", "...", None))
        self.chkAgree.setText(_translate("Dialog", "С протоколом ознакомлен", None))
        self.chkImportExternal.setText(_translate("Dialog", "Загружать инокраевых", None))
        self.btnImport.setText(_translate("Dialog", "начать импортирование", None))
        self.lblNum.setText(_translate("Dialog", "всего обновлённых записей в источнике:", None))
        self.btnClose.setText(_translate("Dialog", "закрыть", None))

from library.ProgressBar import CProgressBar
