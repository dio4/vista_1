# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RBSocStatusTypeItemEditor.ui'
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

class Ui_SocStatusTypeItemEditorDialog(object):
    def setupUi(self, SocStatusTypeItemEditorDialog):
        SocStatusTypeItemEditorDialog.setObjectName(_fromUtf8("SocStatusTypeItemEditorDialog"))
        SocStatusTypeItemEditorDialog.resize(290, 161)
        SocStatusTypeItemEditorDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(SocStatusTypeItemEditorDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.buttonBox = QtGui.QDialogButtonBox(SocStatusTypeItemEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 5, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(103, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 4, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(SocStatusTypeItemEditorDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridlayout.addWidget(self.edtCode, 0, 1, 1, 1)
        self.edtName = QtGui.QLineEdit(SocStatusTypeItemEditorDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridlayout.addWidget(self.edtName, 1, 1, 1, 1)
        self.lblCode = QtGui.QLabel(SocStatusTypeItemEditorDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridlayout.addWidget(self.lblCode, 0, 0, 1, 1)
        self.lblName = QtGui.QLabel(SocStatusTypeItemEditorDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridlayout.addWidget(self.lblName, 1, 0, 1, 1)
        self.lblRegionalCode = QtGui.QLabel(SocStatusTypeItemEditorDialog)
        self.lblRegionalCode.setObjectName(_fromUtf8("lblRegionalCode"))
        self.gridlayout.addWidget(self.lblRegionalCode, 2, 0, 1, 1)
        self.edtRegionalCode = QtGui.QLineEdit(SocStatusTypeItemEditorDialog)
        self.edtRegionalCode.setObjectName(_fromUtf8("edtRegionalCode"))
        self.gridlayout.addWidget(self.edtRegionalCode, 2, 1, 1, 1)
        self.lblDocumentType = QtGui.QLabel(SocStatusTypeItemEditorDialog)
        self.lblDocumentType.setObjectName(_fromUtf8("lblDocumentType"))
        self.gridlayout.addWidget(self.lblDocumentType, 3, 0, 1, 1)
        self.cmbDocumentType = CRBComboBox(SocStatusTypeItemEditorDialog)
        self.cmbDocumentType.setObjectName(_fromUtf8("cmbDocumentType"))
        self.gridlayout.addWidget(self.cmbDocumentType, 3, 1, 1, 1)
        self.lblCode.setBuddy(self.edtCode)
        self.lblName.setBuddy(self.edtName)
        self.lblRegionalCode.setBuddy(self.edtRegionalCode)
        self.lblDocumentType.setBuddy(self.cmbDocumentType)

        self.retranslateUi(SocStatusTypeItemEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SocStatusTypeItemEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SocStatusTypeItemEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SocStatusTypeItemEditorDialog)
        SocStatusTypeItemEditorDialog.setTabOrder(self.edtCode, self.edtName)
        SocStatusTypeItemEditorDialog.setTabOrder(self.edtName, self.edtRegionalCode)
        SocStatusTypeItemEditorDialog.setTabOrder(self.edtRegionalCode, self.cmbDocumentType)
        SocStatusTypeItemEditorDialog.setTabOrder(self.cmbDocumentType, self.buttonBox)

    def retranslateUi(self, SocStatusTypeItemEditorDialog):
        SocStatusTypeItemEditorDialog.setWindowTitle(_translate("SocStatusTypeItemEditorDialog", "ChangeMe!", None))
        self.lblCode.setText(_translate("SocStatusTypeItemEditorDialog", "&Код", None))
        self.lblName.setText(_translate("SocStatusTypeItemEditorDialog", "&Наименование", None))
        self.lblRegionalCode.setText(_translate("SocStatusTypeItemEditorDialog", "&Региональный код", None))
        self.lblDocumentType.setText(_translate("SocStatusTypeItemEditorDialog", "&Тип документа", None))

from library.crbcombobox import CRBComboBox
