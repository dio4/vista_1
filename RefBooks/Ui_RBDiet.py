# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\RBDiet.ui'
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

class Ui_RBDiet(object):
    def setupUi(self, RBDiet):
        RBDiet.setObjectName(_fromUtf8("RBDiet"))
        RBDiet.resize(457, 134)
        RBDiet.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(RBDiet)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        spacerItem = QtGui.QSpacerItem(103, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 4, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(RBDiet)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 5, 0, 1, 2)
        self.edtCode = QtGui.QLineEdit(RBDiet)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridlayout.addWidget(self.edtCode, 0, 1, 1, 1)
        self.edtName = QtGui.QLineEdit(RBDiet)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridlayout.addWidget(self.edtName, 1, 1, 1, 1)
        self.lblName = QtGui.QLabel(RBDiet)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridlayout.addWidget(self.lblName, 1, 0, 1, 1)
        self.chkAllowMeals = QtGui.QCheckBox(RBDiet)
        self.chkAllowMeals.setObjectName(_fromUtf8("chkAllowMeals"))
        self.gridlayout.addWidget(self.chkAllowMeals, 2, 0, 1, 2)
        self.lblCode = QtGui.QLabel(RBDiet)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridlayout.addWidget(self.lblCode, 0, 0, 1, 1)
        self.chkNoCourting = QtGui.QCheckBox(RBDiet)
        self.chkNoCourting.setObjectName(_fromUtf8("chkNoCourting"))
        self.gridlayout.addWidget(self.chkNoCourting, 3, 0, 1, 2)
        self.lblName.setBuddy(self.edtName)
        self.lblCode.setBuddy(self.edtCode)

        self.retranslateUi(RBDiet)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), RBDiet.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), RBDiet.reject)
        QtCore.QMetaObject.connectSlotsByName(RBDiet)
        RBDiet.setTabOrder(self.edtCode, self.edtName)
        RBDiet.setTabOrder(self.edtName, self.buttonBox)

    def retranslateUi(self, RBDiet):
        RBDiet.setWindowTitle(_translate("RBDiet", "ChangeMe!", None))
        self.lblName.setText(_translate("RBDiet", "&Наименование", None))
        self.chkAllowMeals.setText(_translate("RBDiet", "Разрешить указывать приемы пищи вместе с диетой", None))
        self.lblCode.setText(_translate("RBDiet", "&Код", None))
        self.chkNoCourting.setText(_translate("RBDiet", "Не выводить в порционник ухаживающего, если больной в реанимации", None))

