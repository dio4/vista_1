# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RightsEdit.ui'
#
# Created: Thu Apr 03 17:44:09 2014
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

class Ui_UserRightsEditDialog(object):
    def setupUi(self, UserRightsEditDialog):
        UserRightsEditDialog.setObjectName(_fromUtf8("UserRightsEditDialog"))
        UserRightsEditDialog.resize(455, 282)
        UserRightsEditDialog.setSizeGripEnabled(False)
        self.gridlayout = QtGui.QGridLayout(UserRightsEditDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.lblName = QtGui.QLabel(UserRightsEditDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridlayout.addWidget(self.lblName, 0, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(UserRightsEditDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridlayout.addWidget(self.edtName, 0, 1, 1, 1)
        self.lblRights = QtGui.QLabel(UserRightsEditDialog)
        self.lblRights.setObjectName(_fromUtf8("lblRights"))
        self.gridlayout.addWidget(self.lblRights, 1, 0, 1, 2)
        self.tblRights = CInDocTableView(UserRightsEditDialog)
        self.tblRights.setObjectName(_fromUtf8("tblRights"))
        self.gridlayout.addWidget(self.tblRights, 2, 0, 1, 2)
        self.tvVisibleGUIElements = QtGui.QTreeView(UserRightsEditDialog)
        self.tvVisibleGUIElements.setObjectName(_fromUtf8("tvVisibleGUIElements"))
        self.gridlayout.addWidget(self.tvVisibleGUIElements, 2, 2, 1, 1)
        self.lblVisibleGUIElements = QtGui.QLabel(UserRightsEditDialog)
        self.lblVisibleGUIElements.setObjectName(_fromUtf8("lblVisibleGUIElements"))
        self.gridlayout.addWidget(self.lblVisibleGUIElements, 1, 2, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(UserRightsEditDialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 3, 0, 1, 3)
        self.lblName.setBuddy(self.edtName)
        self.lblRights.setBuddy(self.tblRights)

        self.retranslateUi(UserRightsEditDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), UserRightsEditDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), UserRightsEditDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(UserRightsEditDialog)

    def retranslateUi(self, UserRightsEditDialog):
        UserRightsEditDialog.setWindowTitle(_translate("UserRightsEditDialog", "Профиль прав", None))
        self.lblName.setText(_translate("UserRightsEditDialog", "Название", None))
        self.lblRights.setText(_translate("UserRightsEditDialog", "Разрешенные действия", None))
        self.lblVisibleGUIElements.setText(_translate("UserRightsEditDialog", "Доступные элементы интерфейса", None))

from library.InDocTable import CInDocTableView
