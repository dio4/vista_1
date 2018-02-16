# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RBSocStatusClassItemEditor.ui'
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

class Ui_SocStatusClassItemEditorDialog(object):
    def setupUi(self, SocStatusClassItemEditorDialog):
        SocStatusClassItemEditorDialog.setObjectName(_fromUtf8("SocStatusClassItemEditorDialog"))
        SocStatusClassItemEditorDialog.resize(607, 336)
        SocStatusClassItemEditorDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(SocStatusClassItemEditorDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.chkAutoDateClose = QtGui.QCheckBox(SocStatusClassItemEditorDialog)
        self.chkAutoDateClose.setObjectName(_fromUtf8("chkAutoDateClose"))
        self.gridlayout.addWidget(self.chkAutoDateClose, 6, 1, 1, 4)
        self.edtCode = QtGui.QLineEdit(SocStatusClassItemEditorDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridlayout.addWidget(self.edtCode, 0, 1, 1, 4)
        self.lblName = QtGui.QLabel(SocStatusClassItemEditorDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridlayout.addWidget(self.lblName, 1, 0, 1, 1)
        self.lblTypes = QtGui.QLabel(SocStatusClassItemEditorDialog)
        self.lblTypes.setObjectName(_fromUtf8("lblTypes"))
        self.gridlayout.addWidget(self.lblTypes, 3, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(SocStatusClassItemEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 8, 0, 1, 5)
        self.edtName = QtGui.QLineEdit(SocStatusClassItemEditorDialog)
        self.edtName.setMinimumSize(QtCore.QSize(200, 0))
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridlayout.addWidget(self.edtName, 1, 1, 1, 4)
        spacerItem = QtGui.QSpacerItem(73, 171, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 4, 0, 1, 1)
        self.lblCode = QtGui.QLabel(SocStatusClassItemEditorDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridlayout.addWidget(self.lblCode, 0, 0, 1, 1)
        self.chkTightControl = QtGui.QCheckBox(SocStatusClassItemEditorDialog)
        self.chkTightControl.setObjectName(_fromUtf8("chkTightControl"))
        self.gridlayout.addWidget(self.chkTightControl, 2, 1, 1, 1)
        self.tblTypes = CInDocTableView(SocStatusClassItemEditorDialog)
        self.tblTypes.setObjectName(_fromUtf8("tblTypes"))
        self.gridlayout.addWidget(self.tblTypes, 3, 1, 2, 4)
        self.chkShowInClientInfo = QtGui.QCheckBox(SocStatusClassItemEditorDialog)
        self.chkShowInClientInfo.setObjectName(_fromUtf8("chkShowInClientInfo"))
        self.gridlayout.addWidget(self.chkShowInClientInfo, 2, 4, 1, 1)
        self.chkSoftControl = QtGui.QCheckBox(SocStatusClassItemEditorDialog)
        self.chkSoftControl.setObjectName(_fromUtf8("chkSoftControl"))
        self.gridlayout.addWidget(self.chkSoftControl, 2, 2, 1, 1)
        self.lblName.setBuddy(self.edtName)
        self.lblTypes.setBuddy(self.tblTypes)
        self.lblCode.setBuddy(self.edtCode)

        self.retranslateUi(SocStatusClassItemEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SocStatusClassItemEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SocStatusClassItemEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SocStatusClassItemEditorDialog)
        SocStatusClassItemEditorDialog.setTabOrder(self.edtCode, self.edtName)
        SocStatusClassItemEditorDialog.setTabOrder(self.edtName, self.tblTypes)
        SocStatusClassItemEditorDialog.setTabOrder(self.tblTypes, self.buttonBox)

    def retranslateUi(self, SocStatusClassItemEditorDialog):
        SocStatusClassItemEditorDialog.setWindowTitle(_translate("SocStatusClassItemEditorDialog", "ChangeMe!", None))
        self.chkAutoDateClose.setText(_translate("SocStatusClassItemEditorDialog", "Закрывать старую запись соц.статуса данного класса \"вчерашней датой\"", None))
        self.lblName.setText(_translate("SocStatusClassItemEditorDialog", "На&именование", None))
        self.lblTypes.setText(_translate("SocStatusClassItemEditorDialog", "Льготы", None))
        self.lblCode.setText(_translate("SocStatusClassItemEditorDialog", "&Код", None))
        self.chkTightControl.setText(_translate("SocStatusClassItemEditorDialog", "Жёсткий контроль", None))
        self.chkShowInClientInfo.setText(_translate("SocStatusClassItemEditorDialog", "Отображать в шилде", None))
        self.chkSoftControl.setText(_translate("SocStatusClassItemEditorDialog", "Мягкий контроль", None))

from library.InDocTable import CInDocTableView
