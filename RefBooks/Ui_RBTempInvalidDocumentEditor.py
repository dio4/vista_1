# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\RefBooks\RBTempInvalidDocumentEditor.ui'
#
# Created: Fri Jun 15 12:15:46 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_RBTempInvalidDocumentEditorDialog(object):
    def setupUi(self, RBTempInvalidDocumentEditorDialog):
        RBTempInvalidDocumentEditorDialog.setObjectName(_fromUtf8("RBTempInvalidDocumentEditorDialog"))
        RBTempInvalidDocumentEditorDialog.resize(309, 114)
        RBTempInvalidDocumentEditorDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(RBTempInvalidDocumentEditorDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblType = QtGui.QLabel(RBTempInvalidDocumentEditorDialog)
        self.lblType.setObjectName(_fromUtf8("lblType"))
        self.gridLayout.addWidget(self.lblType, 0, 0, 1, 1)
        self.cmbType = QtGui.QComboBox(RBTempInvalidDocumentEditorDialog)
        self.cmbType.setObjectName(_fromUtf8("cmbType"))
        self.gridLayout.addWidget(self.cmbType, 0, 1, 1, 1)
        self.lblCode = QtGui.QLabel(RBTempInvalidDocumentEditorDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridLayout.addWidget(self.lblCode, 1, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(RBTempInvalidDocumentEditorDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout.addWidget(self.edtCode, 1, 1, 1, 1)
        self.lblName = QtGui.QLabel(RBTempInvalidDocumentEditorDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout.addWidget(self.lblName, 2, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(RBTempInvalidDocumentEditorDialog)
        self.edtName.setMinimumSize(QtCore.QSize(200, 0))
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 2, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 71, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(RBTempInvalidDocumentEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 2)
        self.lblType.setBuddy(self.cmbType)
        self.lblCode.setBuddy(self.edtCode)
        self.lblName.setBuddy(self.edtName)

        self.retranslateUi(RBTempInvalidDocumentEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), RBTempInvalidDocumentEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), RBTempInvalidDocumentEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(RBTempInvalidDocumentEditorDialog)
        RBTempInvalidDocumentEditorDialog.setTabOrder(self.cmbType, self.edtCode)
        RBTempInvalidDocumentEditorDialog.setTabOrder(self.edtCode, self.edtName)
        RBTempInvalidDocumentEditorDialog.setTabOrder(self.edtName, self.buttonBox)

    def retranslateUi(self, RBTempInvalidDocumentEditorDialog):
        RBTempInvalidDocumentEditorDialog.setWindowTitle(QtGui.QApplication.translate("RBTempInvalidDocumentEditorDialog", "ChangeMe!", None, QtGui.QApplication.UnicodeUTF8))
        self.lblType.setText(QtGui.QApplication.translate("RBTempInvalidDocumentEditorDialog", "Кла&сс", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCode.setText(QtGui.QApplication.translate("RBTempInvalidDocumentEditorDialog", "&Код", None, QtGui.QApplication.UnicodeUTF8))
        self.lblName.setText(QtGui.QApplication.translate("RBTempInvalidDocumentEditorDialog", "На&именование", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    RBTempInvalidDocumentEditorDialog = QtGui.QDialog()
    ui = Ui_RBTempInvalidDocumentEditorDialog()
    ui.setupUi(RBTempInvalidDocumentEditorDialog)
    RBTempInvalidDocumentEditorDialog.show()
    sys.exit(app.exec_())

