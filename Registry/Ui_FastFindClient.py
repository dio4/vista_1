# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FastFindClient.ui'
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

class Ui_FastFindClient(object):
    def setupUi(self, FastFindClient):
        FastFindClient.setObjectName(_fromUtf8("FastFindClient"))
        FastFindClient.setWindowModality(QtCore.Qt.ApplicationModal)
        FastFindClient.resize(435, 279)
        FastFindClient.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(FastFindClient)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.lblDescription = QtGui.QLabel(FastFindClient)
        self.lblDescription.setObjectName(_fromUtf8("lblDescription"))
        self.gridlayout.addWidget(self.lblDescription, 2, 0, 1, 3)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 3, 0, 1, 1)
        self.edtTemplate = QtGui.QLineEdit(FastFindClient)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtTemplate.sizePolicy().hasHeightForWidth())
        self.edtTemplate.setSizePolicy(sizePolicy)
        self.edtTemplate.setObjectName(_fromUtf8("edtTemplate"))
        self.gridlayout.addWidget(self.edtTemplate, 0, 1, 1, 2)
        self.lblTemplate = QtGui.QLabel(FastFindClient)
        self.lblTemplate.setObjectName(_fromUtf8("lblTemplate"))
        self.gridlayout.addWidget(self.lblTemplate, 0, 0, 1, 1)
        self.btnSearch = QtGui.QPushButton(FastFindClient)
        self.btnSearch.setObjectName(_fromUtf8("btnSearch"))
        self.gridlayout.addWidget(self.btnSearch, 0, 3, 1, 1)
        self.btnClose = QtGui.QPushButton(FastFindClient)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnClose.sizePolicy().hasHeightForWidth())
        self.btnClose.setSizePolicy(sizePolicy)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.gridlayout.addWidget(self.btnClose, 4, 3, 1, 1)
        self.lblTemplate.setBuddy(self.edtTemplate)

        self.retranslateUi(FastFindClient)
        QtCore.QMetaObject.connectSlotsByName(FastFindClient)

    def retranslateUi(self, FastFindClient):
        FastFindClient.setWindowTitle(_translate("FastFindClient", "Быстрый поиск пациента", None))
        self.lblDescription.setText(_translate("FastFindClient", "<html><head/><body><p>Допустимые шаблоны поиска:</p><p>Ф* И* (Руд Его)</p><p>Ф* И* О* (Руд Его Евген)</p><p>Ф* И* О* ДДММГГ (Руд Его Евген 010295)</p><p>Ф* И* О* ДДММГГГГ (Руд Его Евген 01021995)</p><p>Ф* И* ДДММГГ (Руд Его 010295)</p><p>Ф* И* ДДММГГГГ (Руд Его 01021995)</p><p>Ф* ДДММГГ (Руд 010295)</p><p>Ф* ДДММГГГГ (Руд 01021995)</p></body></html>", None))
        self.lblTemplate.setText(_translate("FastFindClient", "&Шаблон быстрого поиска", None))
        self.btnSearch.setText(_translate("FastFindClient", "Искать", None))
        self.btnClose.setText(_translate("FastFindClient", "Закрыть", None))

