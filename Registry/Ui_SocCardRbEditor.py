# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Registry\SocCardRbEditor.ui'
#
# Created: Fri Jun 15 12:16:28 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_RbEditor(object):
    def setupUi(self, RbEditor):
        RbEditor.setObjectName(_fromUtf8("RbEditor"))
        RbEditor.resize(317, 252)
        RbEditor.setSizeGripEnabled(False)
        self.verticalLayout = QtGui.QVBoxLayout(RbEditor)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setMargin(4)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.lblHeader = QtGui.QLabel(RbEditor)
        self.lblHeader.setObjectName(_fromUtf8("lblHeader"))
        self.verticalLayout.addWidget(self.lblHeader)
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.lblSocCode = QtGui.QLabel(RbEditor)
        self.lblSocCode.setObjectName(_fromUtf8("lblSocCode"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.lblSocCode)
        self.edtSocCode = QtGui.QLineEdit(RbEditor)
        self.edtSocCode.setReadOnly(True)
        self.edtSocCode.setObjectName(_fromUtf8("edtSocCode"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.edtSocCode)
        self.lblRbName = QtGui.QLabel(RbEditor)
        self.lblRbName.setObjectName(_fromUtf8("lblRbName"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.lblRbName)
        self.edtRbName = QtGui.QLineEdit(RbEditor)
        self.edtRbName.setReadOnly(True)
        self.edtRbName.setObjectName(_fromUtf8("edtRbName"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.edtRbName)
        self.verticalLayout.addLayout(self.formLayout)
        self.gbxUserActions = QtGui.QGroupBox(RbEditor)
        self.gbxUserActions.setObjectName(_fromUtf8("gbxUserActions"))
        self.gridLayout = QtGui.QGridLayout(self.gbxUserActions)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.chkSelect = QtGui.QRadioButton(self.gbxUserActions)
        self.chkSelect.setChecked(True)
        self.chkSelect.setObjectName(_fromUtf8("chkSelect"))
        self.gridLayout.addWidget(self.chkSelect, 0, 0, 1, 2)
        self.cmbRb = CRBComboBox(self.gbxUserActions)
        self.cmbRb.setObjectName(_fromUtf8("cmbRb"))
        self.gridLayout.addWidget(self.cmbRb, 1, 0, 1, 2)
        self.chkAddNew = QtGui.QRadioButton(self.gbxUserActions)
        self.chkAddNew.setObjectName(_fromUtf8("chkAddNew"))
        self.gridLayout.addWidget(self.chkAddNew, 2, 0, 1, 2)
        self.lblCode = QtGui.QLabel(self.gbxUserActions)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridLayout.addWidget(self.lblCode, 3, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(self.gbxUserActions)
        self.edtCode.setEnabled(False)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout.addWidget(self.edtCode, 3, 1, 1, 1)
        self.lblName = QtGui.QLabel(self.gbxUserActions)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout.addWidget(self.lblName, 4, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(self.gbxUserActions)
        self.edtName.setEnabled(False)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 4, 1, 1, 1)
        self.verticalLayout.addWidget(self.gbxUserActions)
        spacerItem = QtGui.QSpacerItem(103, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(RbEditor)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.lblSocCode.setBuddy(self.edtSocCode)
        self.lblRbName.setBuddy(self.edtRbName)
        self.lblCode.setBuddy(self.edtCode)
        self.lblName.setBuddy(self.edtName)

        self.retranslateUi(RbEditor)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), RbEditor.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), RbEditor.reject)
        QtCore.QMetaObject.connectSlotsByName(RbEditor)

    def retranslateUi(self, RbEditor):
        RbEditor.setWindowTitle(QtGui.QApplication.translate("RbEditor", "Социальная карта", None, QtGui.QApplication.UnicodeUTF8))
        self.lblHeader.setText(QtGui.QApplication.translate("RbEditor", "Тип документа на социальной карте не найден базе данных", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSocCode.setText(QtGui.QApplication.translate("RbEditor", "Соц. код", None, QtGui.QApplication.UnicodeUTF8))
        self.lblRbName.setText(QtGui.QApplication.translate("RbEditor", "Наименование", None, QtGui.QApplication.UnicodeUTF8))
        self.gbxUserActions.setTitle(QtGui.QApplication.translate("RbEditor", "Варианты действий", None, QtGui.QApplication.UnicodeUTF8))
        self.chkSelect.setText(QtGui.QApplication.translate("RbEditor", "Выбрать из существующих", None, QtGui.QApplication.UnicodeUTF8))
        self.chkAddNew.setText(QtGui.QApplication.translate("RbEditor", "Ввести новый", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCode.setText(QtGui.QApplication.translate("RbEditor", "&Код", None, QtGui.QApplication.UnicodeUTF8))
        self.lblName.setText(QtGui.QApplication.translate("RbEditor", "&Наименование", None, QtGui.QApplication.UnicodeUTF8))

from library.crbcombobox import CRBComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    RbEditor = QtGui.QDialog()
    ui = Ui_RbEditor()
    ui.setupUi(RbEditor)
    RbEditor.show()
    sys.exit(app.exec_())

