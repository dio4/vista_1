# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ImportPACS.ui'
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

class Ui_ImportPACSDialog(object):
    def setupUi(self, ImportPACSDialog):
        ImportPACSDialog.setObjectName(_fromUtf8("ImportPACSDialog"))
        ImportPACSDialog.resize(840, 780)
        self.gridLayout = QtGui.QGridLayout(ImportPACSDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(ImportPACSDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.edtAddress = QtGui.QLineEdit(ImportPACSDialog)
        self.edtAddress.setObjectName(_fromUtf8("edtAddress"))
        self.gridLayout.addWidget(self.edtAddress, 0, 1, 1, 3)
        self.label_2 = QtGui.QLabel(ImportPACSDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 4, 1, 1)
        self.edtPort = QtGui.QLineEdit(ImportPACSDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtPort.sizePolicy().hasHeightForWidth())
        self.edtPort.setSizePolicy(sizePolicy)
        self.edtPort.setObjectName(_fromUtf8("edtPort"))
        self.gridLayout.addWidget(self.edtPort, 0, 5, 1, 1)
        self.splitter = QtGui.QSplitter(ImportPACSDialog)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.txtLog = QtGui.QTextBrowser(self.splitter)
        self.txtLog.setObjectName(_fromUtf8("txtLog"))
        self.gridLayout.addWidget(self.splitter, 2, 0, 1, 6)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.btnImport = QtGui.QPushButton(ImportPACSDialog)
        self.btnImport.setObjectName(_fromUtf8("btnImport"))
        self.horizontalLayout_3.addWidget(self.btnImport)
        self.gridLayout.addLayout(self.horizontalLayout_3, 3, 0, 1, 6)
        self.label_3 = QtGui.QLabel(ImportPACSDialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.edtFileName = QtGui.QLineEdit(ImportPACSDialog)
        self.edtFileName.setText(_fromUtf8(""))
        self.edtFileName.setReadOnly(True)
        self.edtFileName.setObjectName(_fromUtf8("edtFileName"))
        self.horizontalLayout.addWidget(self.edtFileName)
        self.btnSelectFile = QtGui.QToolButton(ImportPACSDialog)
        self.btnSelectFile.setObjectName(_fromUtf8("btnSelectFile"))
        self.horizontalLayout.addWidget(self.btnSelectFile)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 1, 1, 5)
        self.label.raise_()
        self.edtAddress.raise_()
        self.splitter.raise_()
        self.label_2.raise_()
        self.edtPort.raise_()
        self.label_3.raise_()
        self.edtFileName.raise_()

        self.retranslateUi(ImportPACSDialog)
        QtCore.QMetaObject.connectSlotsByName(ImportPACSDialog)
        ImportPACSDialog.setTabOrder(self.txtLog, self.btnImport)

    def retranslateUi(self, ImportPACSDialog):
        ImportPACSDialog.setWindowTitle(_translate("ImportPACSDialog", "Отправка ИЭМК", None))
        self.label.setText(_translate("ImportPACSDialog", "Адрес сервера", None))
        self.label_2.setText(_translate("ImportPACSDialog", "Порт", None))
        self.btnImport.setText(_translate("ImportPACSDialog", "Импортировать", None))
        self.label_3.setText(_translate("ImportPACSDialog", "Импортировать из", None))
        self.btnSelectFile.setText(_translate("ImportPACSDialog", "...", None))

