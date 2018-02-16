# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RBMenu.ui'
#
# Created: Tue Apr 21 11:31:34 2015
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

class Ui_RBMenu(object):
    def setupUi(self, RBMenu):
        RBMenu.setObjectName(_fromUtf8("RBMenu"))
        RBMenu.resize(540, 322)
        RBMenu.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(RBMenu)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.edtName = QtGui.QLineEdit(RBMenu)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridlayout.addWidget(self.edtName, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(RBMenu)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 6, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(103, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 5, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(RBMenu)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridlayout.addWidget(self.edtCode, 0, 1, 1, 1)
        self.tblMenuContent = CInDocTableView(RBMenu)
        self.tblMenuContent.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblMenuContent.setObjectName(_fromUtf8("tblMenuContent"))
        self.gridlayout.addWidget(self.tblMenuContent, 4, 0, 1, 2)
        self.lblName = QtGui.QLabel(RBMenu)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridlayout.addWidget(self.lblName, 1, 0, 1, 1)
        self.lblCode = QtGui.QLabel(RBMenu)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridlayout.addWidget(self.lblCode, 0, 0, 1, 1)
        self.lblDiet = QtGui.QLabel(RBMenu)
        self.lblDiet.setObjectName(_fromUtf8("lblDiet"))
        self.gridlayout.addWidget(self.lblDiet, 2, 0, 1, 1)
        self.cmbDiet = CRBComboBox(RBMenu)
        self.cmbDiet.setObjectName(_fromUtf8("cmbDiet"))
        self.gridlayout.addWidget(self.cmbDiet, 2, 1, 1, 1)
        self.lblCourtingDiet = QtGui.QLabel(RBMenu)
        self.lblCourtingDiet.setObjectName(_fromUtf8("lblCourtingDiet"))
        self.gridlayout.addWidget(self.lblCourtingDiet, 3, 0, 1, 1)
        self.cmbCourtingDiet = CRBComboBox(RBMenu)
        self.cmbCourtingDiet.setObjectName(_fromUtf8("cmbCourtingDiet"))
        self.gridlayout.addWidget(self.cmbCourtingDiet, 3, 1, 1, 1)
        self.lblName.setBuddy(self.edtName)
        self.lblCode.setBuddy(self.edtCode)
        self.lblDiet.setBuddy(self.edtName)
        self.lblCourtingDiet.setBuddy(self.edtName)

        self.retranslateUi(RBMenu)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), RBMenu.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), RBMenu.reject)
        QtCore.QMetaObject.connectSlotsByName(RBMenu)
        RBMenu.setTabOrder(self.edtCode, self.edtName)
        RBMenu.setTabOrder(self.edtName, self.tblMenuContent)
        RBMenu.setTabOrder(self.tblMenuContent, self.buttonBox)

    def retranslateUi(self, RBMenu):
        RBMenu.setWindowTitle(_translate("RBMenu", "ChangeMe!", None))
        self.lblName.setText(_translate("RBMenu", "&Наименование", None))
        self.lblCode.setText(_translate("RBMenu", "&Код", None))
        self.lblDiet.setText(_translate("RBMenu", "Диета", None))
        self.lblCourtingDiet.setText(_translate("RBMenu", "Диета ухаживающего", None))

from library.InDocTable import CInDocTableView
from library.crbcombobox import CRBComboBox
