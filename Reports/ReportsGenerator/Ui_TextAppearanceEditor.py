# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TextAppearanceEditor.ui'
#
# Created: Wed Mar 13 20:48:06 2013
#      by: PyQt4 UI code generator 4.9.6
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

class Ui_TextAppearanceEditor(object):
    def setupUi(self, TextAppearanceEditor):
        TextAppearanceEditor.setObjectName(_fromUtf8("TextAppearanceEditor"))
        TextAppearanceEditor.resize(454, 41)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(TextAppearanceEditor.sizePolicy().hasHeightForWidth())
        TextAppearanceEditor.setSizePolicy(sizePolicy)
        TextAppearanceEditor.setMaximumSize(QtCore.QSize(16777215, 41))
        self.horizontalLayout = QtGui.QHBoxLayout(TextAppearanceEditor)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.fcmbFontFamily = QtGui.QFontComboBox(TextAppearanceEditor)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fcmbFontFamily.sizePolicy().hasHeightForWidth())
        self.fcmbFontFamily.setSizePolicy(sizePolicy)
        self.fcmbFontFamily.setObjectName(_fromUtf8("fcmbFontFamily"))
        self.horizontalLayout.addWidget(self.fcmbFontFamily)
        self.sbFontSize = QtGui.QSpinBox(TextAppearanceEditor)
        self.sbFontSize.setMinimum(1)
        self.sbFontSize.setProperty("value", 8)
        self.sbFontSize.setObjectName(_fromUtf8("sbFontSize"))
        self.horizontalLayout.addWidget(self.sbFontSize)
        self.btnFontBold = QtGui.QPushButton(TextAppearanceEditor)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnFontBold.sizePolicy().hasHeightForWidth())
        self.btnFontBold.setSizePolicy(sizePolicy)
        self.btnFontBold.setMaximumSize(QtCore.QSize(23, 23))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.btnFontBold.setFont(font)
        self.btnFontBold.setCheckable(True)
        self.btnFontBold.setObjectName(_fromUtf8("btnFontBold"))
        self.horizontalLayout.addWidget(self.btnFontBold)
        self.btnFontItalic = QtGui.QPushButton(TextAppearanceEditor)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnFontItalic.sizePolicy().hasHeightForWidth())
        self.btnFontItalic.setSizePolicy(sizePolicy)
        self.btnFontItalic.setMaximumSize(QtCore.QSize(23, 23))
        font = QtGui.QFont()
        font.setItalic(True)
        self.btnFontItalic.setFont(font)
        self.btnFontItalic.setCheckable(True)
        self.btnFontItalic.setObjectName(_fromUtf8("btnFontItalic"))
        self.horizontalLayout.addWidget(self.btnFontItalic)
        self.btnFontUnderline = QtGui.QPushButton(TextAppearanceEditor)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnFontUnderline.sizePolicy().hasHeightForWidth())
        self.btnFontUnderline.setSizePolicy(sizePolicy)
        self.btnFontUnderline.setMaximumSize(QtCore.QSize(23, 23))
        font = QtGui.QFont()
        font.setUnderline(True)
        self.btnFontUnderline.setFont(font)
        self.btnFontUnderline.setCheckable(True)
        self.btnFontUnderline.setObjectName(_fromUtf8("btnFontUnderline"))
        self.horizontalLayout.addWidget(self.btnFontUnderline)
        self.btnLeftAlignment = QtGui.QPushButton(TextAppearanceEditor)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnLeftAlignment.sizePolicy().hasHeightForWidth())
        self.btnLeftAlignment.setSizePolicy(sizePolicy)
        self.btnLeftAlignment.setMaximumSize(QtCore.QSize(23, 23))
        font = QtGui.QFont()
        font.setPointSize(1)
        font.setBold(True)
        font.setWeight(75)
        self.btnLeftAlignment.setFont(font)
        self.btnLeftAlignment.setStyleSheet(_fromUtf8("text-align: left;"))
        self.btnLeftAlignment.setCheckable(True)
        self.btnLeftAlignment.setObjectName(_fromUtf8("btnLeftAlignment"))
        self.horizontalLayout.addWidget(self.btnLeftAlignment)
        self.btnCenterAlignment = QtGui.QPushButton(TextAppearanceEditor)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnCenterAlignment.sizePolicy().hasHeightForWidth())
        self.btnCenterAlignment.setSizePolicy(sizePolicy)
        self.btnCenterAlignment.setMaximumSize(QtCore.QSize(23, 23))
        font = QtGui.QFont()
        font.setPointSize(1)
        font.setBold(True)
        font.setUnderline(False)
        font.setWeight(75)
        self.btnCenterAlignment.setFont(font)
        self.btnCenterAlignment.setStyleSheet(_fromUtf8("text-align: center;"))
        self.btnCenterAlignment.setCheckable(True)
        self.btnCenterAlignment.setFlat(False)
        self.btnCenterAlignment.setObjectName(_fromUtf8("btnCenterAlignment"))
        self.horizontalLayout.addWidget(self.btnCenterAlignment)
        self.btnRightAlignment = QtGui.QPushButton(TextAppearanceEditor)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnRightAlignment.sizePolicy().hasHeightForWidth())
        self.btnRightAlignment.setSizePolicy(sizePolicy)
        self.btnRightAlignment.setMaximumSize(QtCore.QSize(23, 23))
        font = QtGui.QFont()
        font.setPointSize(1)
        font.setBold(True)
        font.setWeight(75)
        self.btnRightAlignment.setFont(font)
        self.btnRightAlignment.setStyleSheet(_fromUtf8("text-align: right;"))
        self.btnRightAlignment.setCheckable(True)
        self.btnRightAlignment.setFlat(False)
        self.btnRightAlignment.setObjectName(_fromUtf8("btnRightAlignment"))
        self.horizontalLayout.addWidget(self.btnRightAlignment)

        self.retranslateUi(TextAppearanceEditor)
        QtCore.QMetaObject.connectSlotsByName(TextAppearanceEditor)

    def retranslateUi(self, TextAppearanceEditor):
        TextAppearanceEditor.setWindowTitle(_translate("TextAppearanceEditor", "Form", None))
        self.btnFontBold.setText(_translate("TextAppearanceEditor", "Ж", None))
        self.btnFontItalic.setText(_translate("TextAppearanceEditor", "К", None))
        self.btnFontUnderline.setText(_translate("TextAppearanceEditor", "П", None))
        self.btnLeftAlignment.setText(_translate("TextAppearanceEditor", "______________\n"
"_______\n"
"______________\n"
"_______\n"
"______________", None))
        self.btnCenterAlignment.setText(_translate("TextAppearanceEditor", "______________\n"
"_______\n"
"______________\n"
"_______\n"
"______________", None))
        self.btnRightAlignment.setText(_translate("TextAppearanceEditor", "______________\n"
"_______\n"
"______________\n"
"_______\n"
"______________", None))

