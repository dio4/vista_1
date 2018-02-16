# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\RefBooks\RBComplainEditor.ui'
#
# Created: Fri Jun 15 12:15:39 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ComplainEditorDialog(object):
    def setupUi(self, ComplainEditorDialog):
        ComplainEditorDialog.setObjectName(_fromUtf8("ComplainEditorDialog"))
        ComplainEditorDialog.resize(285, 114)
        ComplainEditorDialog.setSizeGripEnabled(False)
        self.gridlayout = QtGui.QGridLayout(ComplainEditorDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.lblCode = QtGui.QLabel(ComplainEditorDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridlayout.addWidget(self.lblCode, 0, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(ComplainEditorDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridlayout.addWidget(self.edtCode, 0, 1, 1, 1)
        self.lblName = QtGui.QLabel(ComplainEditorDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridlayout.addWidget(self.lblName, 1, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(ComplainEditorDialog)
        self.edtName.setMinimumSize(QtCore.QSize(200, 0))
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridlayout.addWidget(self.edtName, 1, 1, 1, 1)
        self.lblGroup = QtGui.QLabel(ComplainEditorDialog)
        self.lblGroup.setObjectName(_fromUtf8("lblGroup"))
        self.gridlayout.addWidget(self.lblGroup, 2, 0, 1, 1)
        self.cmbGroup = CRBComboBox(ComplainEditorDialog)
        self.cmbGroup.setObjectName(_fromUtf8("cmbGroup"))
        self.gridlayout.addWidget(self.cmbGroup, 2, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(73, 41, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 3, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ComplainEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 4, 0, 1, 2)
        self.lblCode.setBuddy(self.edtCode)
        self.lblName.setBuddy(self.edtName)
        self.lblGroup.setBuddy(self.cmbGroup)

        self.retranslateUi(ComplainEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ComplainEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ComplainEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ComplainEditorDialog)
        ComplainEditorDialog.setTabOrder(self.edtCode, self.edtName)
        ComplainEditorDialog.setTabOrder(self.edtName, self.buttonBox)

    def retranslateUi(self, ComplainEditorDialog):
        ComplainEditorDialog.setWindowTitle(QtGui.QApplication.translate("ComplainEditorDialog", "ChangeMe!", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCode.setText(QtGui.QApplication.translate("ComplainEditorDialog", "&Код", None, QtGui.QApplication.UnicodeUTF8))
        self.lblName.setText(QtGui.QApplication.translate("ComplainEditorDialog", "На&именование", None, QtGui.QApplication.UnicodeUTF8))
        self.lblGroup.setText(QtGui.QApplication.translate("ComplainEditorDialog", "&Группа", None, QtGui.QApplication.UnicodeUTF8))

from library.crbcombobox import CRBComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ComplainEditorDialog = QtGui.QDialog()
    ui = Ui_ComplainEditorDialog()
    ui.setupUi(ComplainEditorDialog)
    ComplainEditorDialog.show()
    sys.exit(app.exec_())

