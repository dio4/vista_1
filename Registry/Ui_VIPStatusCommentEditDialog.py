# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'VIPStatusCommentEditDialog.ui'
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

class Ui_VIPStatusComment(object):
    def setupUi(self, VIPStatusComment):
        VIPStatusComment.setObjectName(_fromUtf8("VIPStatusComment"))
        VIPStatusComment.resize(492, 162)
        VIPStatusComment.setMaximumSize(QtCore.QSize(16777215, 162))
        self.gridLayout = QtGui.QGridLayout(VIPStatusComment)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(VIPStatusComment)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.btnStatus = QtGui.QPushButton(VIPStatusComment)
        self.btnStatus.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.btnStatus.setObjectName(_fromUtf8("btnStatus"))
        self.gridLayout.addWidget(self.btnStatus, 6, 4, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 6, 0, 1, 3)
        self.label_2 = QtGui.QLabel(VIPStatusComment)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(VIPStatusComment)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 6, 3, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 3, 0, 1, 1)
        self.lblColor = QtGui.QLabel(VIPStatusComment)
        self.lblColor.setObjectName(_fromUtf8("lblColor"))
        self.gridLayout.addWidget(self.lblColor, 4, 0, 1, 1)
        self.cmbColor = CColorComboBox(VIPStatusComment)
        self.cmbColor.setObjectName(_fromUtf8("cmbColor"))
        self.gridLayout.addWidget(self.cmbColor, 4, 2, 1, 3)
        self.edtVIPStatusComment = QtGui.QLineEdit(VIPStatusComment)
        self.edtVIPStatusComment.setAlignment(QtCore.Qt.AlignCenter)
        self.edtVIPStatusComment.setObjectName(_fromUtf8("edtVIPStatusComment"))
        self.gridLayout.addWidget(self.edtVIPStatusComment, 1, 2, 1, 3)
        self.edtStatus = QtGui.QLineEdit(VIPStatusComment)
        self.edtStatus.setStyleSheet(_fromUtf8("background-color: rgb(255, 215, 0);\n"
"border-color: rgb(0, 0, 0);\n"
"color: rgb(60, 21, 255);\n"
"font: bold 8pt \"Times New Roman\";\n"
""))
        self.edtStatus.setAlignment(QtCore.Qt.AlignCenter)
        self.edtStatus.setReadOnly(True)
        self.edtStatus.setObjectName(_fromUtf8("edtStatus"))
        self.gridLayout.addWidget(self.edtStatus, 0, 2, 1, 3)
        self.lblColor.setBuddy(self.cmbColor)

        self.retranslateUi(VIPStatusComment)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), VIPStatusComment.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), VIPStatusComment.reject)
        QtCore.QMetaObject.connectSlotsByName(VIPStatusComment)

    def retranslateUi(self, VIPStatusComment):
        VIPStatusComment.setWindowTitle(_translate("VIPStatusComment", "Комментарий к VIP-статусу", None))
        self.label.setText(_translate("VIPStatusComment", "Комментарий:", None))
        self.btnStatus.setText(_translate("VIPStatusComment", "Снять статус", None))
        self.label_2.setText(_translate("VIPStatusComment", "VIP-статус:", None))
        self.lblColor.setText(_translate("VIPStatusComment", "&Цветовая маркировка", None))
        self.edtStatus.setText(_translate("VIPStatusComment", "ВЫСТАВЛЕН", None))

from library.ColorEdit import CColorComboBox
