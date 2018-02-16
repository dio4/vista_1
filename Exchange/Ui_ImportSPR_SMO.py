# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ImportSPR_SMO.ui'
#
# Created: Tue Mar 17 20:37:58 2015
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

class Ui_ImportSprSmoDialog(object):
    def setupUi(self, ImportSprSmoDialog):
        ImportSprSmoDialog.setObjectName(_fromUtf8("ImportSprSmoDialog"))
        ImportSprSmoDialog.resize(474, 503)
        self.gridLayout = QtGui.QGridLayout(ImportSprSmoDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.btnView_SPR33 = QtGui.QPushButton(ImportSprSmoDialog)
        self.btnView_SPR33.setObjectName(_fromUtf8("btnView_SPR33"))
        self.gridLayout.addWidget(self.btnView_SPR33, 4, 7, 1, 1)
        self.btnView_SPR03 = QtGui.QPushButton(ImportSprSmoDialog)
        self.btnView_SPR03.setObjectName(_fromUtf8("btnView_SPR03"))
        self.gridLayout.addWidget(self.btnView_SPR03, 2, 7, 1, 1)
        self.btnView_SPR02 = QtGui.QPushButton(ImportSprSmoDialog)
        self.btnView_SPR02.setObjectName(_fromUtf8("btnView_SPR02"))
        self.gridLayout.addWidget(self.btnView_SPR02, 0, 7, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.edtFileName_SPR02 = QtGui.QLineEdit(ImportSprSmoDialog)
        self.edtFileName_SPR02.setText(_fromUtf8(""))
        self.edtFileName_SPR02.setReadOnly(True)
        self.edtFileName_SPR02.setObjectName(_fromUtf8("edtFileName_SPR02"))
        self.horizontalLayout.addWidget(self.edtFileName_SPR02)
        self.btnSelectFile_SPR02 = QtGui.QToolButton(ImportSprSmoDialog)
        self.btnSelectFile_SPR02.setObjectName(_fromUtf8("btnSelectFile_SPR02"))
        self.horizontalLayout.addWidget(self.btnSelectFile_SPR02)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 1, 1, 6)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.edtFileName_SPR33 = QtGui.QLineEdit(ImportSprSmoDialog)
        self.edtFileName_SPR33.setObjectName(_fromUtf8("edtFileName_SPR33"))
        self.horizontalLayout_3.addWidget(self.edtFileName_SPR33)
        self.btnSelectFile_SPR33 = QtGui.QToolButton(ImportSprSmoDialog)
        self.btnSelectFile_SPR33.setObjectName(_fromUtf8("btnSelectFile_SPR33"))
        self.horizontalLayout_3.addWidget(self.btnSelectFile_SPR33)
        self.gridLayout.addLayout(self.horizontalLayout_3, 4, 1, 1, 6)
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.btnImport = QtGui.QPushButton(ImportSprSmoDialog)
        self.btnImport.setObjectName(_fromUtf8("btnImport"))
        self.hboxlayout.addWidget(self.btnImport)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.labelNum = QtGui.QLabel(ImportSprSmoDialog)
        self.labelNum.setObjectName(_fromUtf8("labelNum"))
        self.hboxlayout.addWidget(self.labelNum)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem1)
        self.btnClose = QtGui.QPushButton(ImportSprSmoDialog)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.hboxlayout.addWidget(self.btnClose)
        self.gridLayout.addLayout(self.hboxlayout, 7, 0, 1, 8)
        self.progressBar = CProgressBar(ImportSprSmoDialog)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 5, 0, 1, 8)
        self.log = QtGui.QTextBrowser(ImportSprSmoDialog)
        self.log.setObjectName(_fromUtf8("log"))
        self.gridLayout.addWidget(self.log, 6, 0, 1, 8)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.edtFileName_SPR03 = QtGui.QLineEdit(ImportSprSmoDialog)
        self.edtFileName_SPR03.setObjectName(_fromUtf8("edtFileName_SPR03"))
        self.horizontalLayout_2.addWidget(self.edtFileName_SPR03)
        self.btnSelectFile_SPR03 = QtGui.QToolButton(ImportSprSmoDialog)
        self.btnSelectFile_SPR03.setObjectName(_fromUtf8("btnSelectFile_SPR03"))
        self.horizontalLayout_2.addWidget(self.btnSelectFile_SPR03)
        self.gridLayout.addLayout(self.horizontalLayout_2, 2, 1, 1, 6)
        self.labelSPR02 = QtGui.QLabel(ImportSprSmoDialog)
        self.labelSPR02.setObjectName(_fromUtf8("labelSPR02"))
        self.gridLayout.addWidget(self.labelSPR02, 0, 0, 1, 1)
        self.labelSPR03 = QtGui.QLabel(ImportSprSmoDialog)
        self.labelSPR03.setObjectName(_fromUtf8("labelSPR03"))
        self.gridLayout.addWidget(self.labelSPR03, 2, 0, 1, 1)
        self.labelSPR33 = QtGui.QLabel(ImportSprSmoDialog)
        self.labelSPR33.setObjectName(_fromUtf8("labelSPR33"))
        self.gridLayout.addWidget(self.labelSPR33, 4, 0, 1, 1)

        self.retranslateUi(ImportSprSmoDialog)
        QtCore.QMetaObject.connectSlotsByName(ImportSprSmoDialog)

    def retranslateUi(self, ImportSprSmoDialog):
        ImportSprSmoDialog.setWindowTitle(_translate("ImportSprSmoDialog", "Загрузка Страховых Медицинских Организаций", None))
        self.btnView_SPR33.setText(_translate("ImportSprSmoDialog", "Просмотреть", None))
        self.btnView_SPR03.setText(_translate("ImportSprSmoDialog", "Просмотреть", None))
        self.btnView_SPR02.setText(_translate("ImportSprSmoDialog", "Просмотреть", None))
        self.btnSelectFile_SPR02.setText(_translate("ImportSprSmoDialog", "...", None))
        self.btnSelectFile_SPR33.setText(_translate("ImportSprSmoDialog", "...", None))
        self.btnImport.setText(_translate("ImportSprSmoDialog", "начать импортирование", None))
        self.labelNum.setText(_translate("ImportSprSmoDialog", "всего записей в источнике:", None))
        self.btnClose.setText(_translate("ImportSprSmoDialog", "закрыть", None))
        self.btnSelectFile_SPR03.setText(_translate("ImportSprSmoDialog", "...", None))
        self.labelSPR02.setText(_translate("ImportSprSmoDialog", "путь к SPR 02", None))
        self.labelSPR03.setText(_translate("ImportSprSmoDialog", "путь к SPR 03", None))
        self.labelSPR33.setText(_translate("ImportSprSmoDialog", "путь к SPR 33", None))

from library.ProgressBar import CProgressBar
