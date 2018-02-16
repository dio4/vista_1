# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'loadingScreen.ui'
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

class Ui_LoadScreenForm(object):
    def setupUi(self, LoadScreenForm):
        LoadScreenForm.setObjectName(_fromUtf8("LoadScreenForm"))
        LoadScreenForm.setWindowModality(QtCore.Qt.NonModal)
        LoadScreenForm.resize(352, 51)
        LoadScreenForm.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        LoadScreenForm.setWindowOpacity(1.0)
        self.gridLayout = QtGui.QGridLayout(LoadScreenForm)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.frame = QtGui.QFrame(LoadScreenForm)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.gridLayout_2 = QtGui.QGridLayout(self.frame)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.lblLoading = QtGui.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.lblLoading.setFont(font)
        self.lblLoading.setFocusPolicy(QtCore.Qt.NoFocus)
        self.lblLoading.setObjectName(_fromUtf8("lblLoading"))
        self.gridLayout_2.addWidget(self.lblLoading, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)

        self.retranslateUi(LoadScreenForm)
        QtCore.QMetaObject.connectSlotsByName(LoadScreenForm)

    def retranslateUi(self, LoadScreenForm):
        LoadScreenForm.setWindowTitle(_translate("LoadScreenForm", "Loading", None))
        self.lblLoading.setText(_translate("LoadScreenForm", "Идет загрузка настроек. Пожалуйста ждите....", None))

