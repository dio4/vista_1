# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\RefBooks\QuotaTypeEditor.ui'
#
# Created: Fri Jun 15 12:16:49 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_QuotaTypeEditorDialog(object):
    def setupUi(self, QuotaTypeEditorDialog):
        QuotaTypeEditorDialog.setObjectName(_fromUtf8("QuotaTypeEditorDialog"))
        QuotaTypeEditorDialog.resize(357, 320)
        QuotaTypeEditorDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(QuotaTypeEditorDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblClass = QtGui.QLabel(QuotaTypeEditorDialog)
        self.lblClass.setObjectName(_fromUtf8("lblClass"))
        self.gridLayout.addWidget(self.lblClass, 0, 0, 1, 1)
        self.cmbClass = QtGui.QComboBox(QuotaTypeEditorDialog)
        self.cmbClass.setEnabled(False)
        self.cmbClass.setObjectName(_fromUtf8("cmbClass"))
        self.gridLayout.addWidget(self.cmbClass, 0, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(120, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.lblGroup = QtGui.QLabel(QuotaTypeEditorDialog)
        self.lblGroup.setObjectName(_fromUtf8("lblGroup"))
        self.gridLayout.addWidget(self.lblGroup, 1, 0, 1, 1)
        self.cmbGroup = CRBComboBox(QuotaTypeEditorDialog)
        self.cmbGroup.setEnabled(False)
        self.cmbGroup.setObjectName(_fromUtf8("cmbGroup"))
        self.gridLayout.addWidget(self.cmbGroup, 1, 1, 1, 2)
        self.lblCode = QtGui.QLabel(QuotaTypeEditorDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridLayout.addWidget(self.lblCode, 2, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(QuotaTypeEditorDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout.addWidget(self.edtCode, 2, 1, 1, 2)
        self.lblName = QtGui.QLabel(QuotaTypeEditorDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout.addWidget(self.lblName, 3, 0, 1, 1)
        self.edtName = QtGui.QTextEdit(QuotaTypeEditorDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 3, 1, 2, 2)
        spacerItem1 = QtGui.QSpacerItem(20, 182, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 4, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(QuotaTypeEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 3)
        self.lblClass.setBuddy(self.cmbClass)
        self.lblGroup.setBuddy(self.cmbGroup)
        self.lblCode.setBuddy(self.edtCode)
        self.lblName.setBuddy(self.edtName)

        self.retranslateUi(QuotaTypeEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), QuotaTypeEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), QuotaTypeEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(QuotaTypeEditorDialog)

    def retranslateUi(self, QuotaTypeEditorDialog):
        QuotaTypeEditorDialog.setWindowTitle(QtGui.QApplication.translate("QuotaTypeEditorDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.lblClass.setText(QtGui.QApplication.translate("QuotaTypeEditorDialog", "&Класс", None, QtGui.QApplication.UnicodeUTF8))
        self.lblGroup.setText(QtGui.QApplication.translate("QuotaTypeEditorDialog", "&Вид", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCode.setText(QtGui.QApplication.translate("QuotaTypeEditorDialog", "&Код", None, QtGui.QApplication.UnicodeUTF8))
        self.lblName.setText(QtGui.QApplication.translate("QuotaTypeEditorDialog", "&Наименование", None, QtGui.QApplication.UnicodeUTF8))

from library.crbcombobox import CRBComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    QuotaTypeEditorDialog = QtGui.QDialog()
    ui = Ui_QuotaTypeEditorDialog()
    ui.setupUi(QuotaTypeEditorDialog)
    QuotaTypeEditorDialog.show()
    sys.exit(app.exec_())

