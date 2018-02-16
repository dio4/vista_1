# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ExportTariffR23_Page2.ui'
#
# Created: Wed Jan 20 16:22:06 2016
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

class Ui_ExportTariffR23_Page2(object):
    def setupUi(self, ExportTariffR23_Page2):
        ExportTariffR23_Page2.setObjectName(_fromUtf8("ExportTariffR23_Page2"))
        ExportTariffR23_Page2.resize(397, 212)
        self.gridLayout = QtGui.QGridLayout(ExportTariffR23_Page2)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.progressBar = CProgressBar(ExportTariffR23_Page2)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 4, 0, 1, 3)
        spacerItem = QtGui.QSpacerItem(20, 50, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 0, 1, 3)
        self.lblLpuCode = QtGui.QLabel(ExportTariffR23_Page2)
        self.lblLpuCode.setObjectName(_fromUtf8("lblLpuCode"))
        self.gridLayout.addWidget(self.lblLpuCode, 2, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(397, 50, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 3, 0, 1, 3)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.edtDirName = QtGui.QLineEdit(ExportTariffR23_Page2)
        self.edtDirName.setObjectName(_fromUtf8("edtDirName"))
        self.horizontalLayout.addWidget(self.edtDirName)
        self.btnSelectDir = QtGui.QToolButton(ExportTariffR23_Page2)
        self.btnSelectDir.setObjectName(_fromUtf8("btnSelectDir"))
        self.horizontalLayout.addWidget(self.btnSelectDir)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 1, 1, 2)
        self.btnExport = QtGui.QPushButton(ExportTariffR23_Page2)
        self.btnExport.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnExport.sizePolicy().hasHeightForWidth())
        self.btnExport.setSizePolicy(sizePolicy)
        self.btnExport.setObjectName(_fromUtf8("btnExport"))
        self.gridLayout.addWidget(self.btnExport, 6, 2, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(278, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 6, 0, 1, 2)
        self.lblFileName = QtGui.QLabel(ExportTariffR23_Page2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblFileName.sizePolicy().hasHeightForWidth())
        self.lblFileName.setSizePolicy(sizePolicy)
        self.lblFileName.setObjectName(_fromUtf8("lblFileName"))
        self.gridLayout.addWidget(self.lblFileName, 0, 0, 1, 1)
        self.edtLpuCode = QtGui.QLineEdit(ExportTariffR23_Page2)
        self.edtLpuCode.setObjectName(_fromUtf8("edtLpuCode"))
        self.gridLayout.addWidget(self.edtLpuCode, 2, 1, 1, 2)

        self.retranslateUi(ExportTariffR23_Page2)
        QtCore.QMetaObject.connectSlotsByName(ExportTariffR23_Page2)
        ExportTariffR23_Page2.setTabOrder(self.edtDirName, self.btnSelectDir)

    def retranslateUi(self, ExportTariffR23_Page2):
        ExportTariffR23_Page2.setWindowTitle(_translate("ExportTariffR23_Page2", "Выбор файла и процесс", None))
        self.lblLpuCode.setText(_translate("ExportTariffR23_Page2", "Код МО", None))
        self.btnSelectDir.setText(_translate("ExportTariffR23_Page2", "...", None))
        self.btnExport.setText(_translate("ExportTariffR23_Page2", "Начать экспорт", None))
        self.lblFileName.setText(_translate("ExportTariffR23_Page2", "Экспортировать в", None))

from library.ProgressBar import CProgressBar
