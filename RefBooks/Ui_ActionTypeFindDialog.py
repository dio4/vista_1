# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\RefBooks\ActionTypeFindDialog.ui'
#
# Created: Fri Jun 15 12:17:12 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ActionTypeFindDialog(object):
    def setupUi(self, ActionTypeFindDialog):
        ActionTypeFindDialog.setObjectName(_fromUtf8("ActionTypeFindDialog"))
        ActionTypeFindDialog.resize(706, 394)
        ActionTypeFindDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ActionTypeFindDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblCode = QtGui.QLabel(ActionTypeFindDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblCode.sizePolicy().hasHeightForWidth())
        self.lblCode.setSizePolicy(sizePolicy)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridLayout.addWidget(self.lblCode, 0, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(ActionTypeFindDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout.addWidget(self.edtCode, 0, 1, 1, 2)
        self.lblNomenclativeCode = QtGui.QLabel(ActionTypeFindDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblNomenclativeCode.sizePolicy().hasHeightForWidth())
        self.lblNomenclativeCode.setSizePolicy(sizePolicy)
        self.lblNomenclativeCode.setObjectName(_fromUtf8("lblNomenclativeCode"))
        self.gridLayout.addWidget(self.lblNomenclativeCode, 1, 0, 1, 1)
        self.edtNomenclativeCode = QtGui.QLineEdit(ActionTypeFindDialog)
        self.edtNomenclativeCode.setObjectName(_fromUtf8("edtNomenclativeCode"))
        self.gridLayout.addWidget(self.edtNomenclativeCode, 1, 1, 1, 2)
        self.lblName = QtGui.QLabel(ActionTypeFindDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblName.sizePolicy().hasHeightForWidth())
        self.lblName.setSizePolicy(sizePolicy)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout.addWidget(self.lblName, 2, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(ActionTypeFindDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 2, 1, 1, 2)
        self.lblProfilePayment = QtGui.QLabel(ActionTypeFindDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblProfilePayment.sizePolicy().hasHeightForWidth())
        self.lblProfilePayment.setSizePolicy(sizePolicy)
        self.lblProfilePayment.setObjectName(_fromUtf8("lblProfilePayment"))
        self.gridLayout.addWidget(self.lblProfilePayment, 4, 0, 1, 1)
        self.cmbService = CRBComboBox(ActionTypeFindDialog)
        self.cmbService.setObjectName(_fromUtf8("cmbService"))
        self.gridLayout.addWidget(self.cmbService, 4, 1, 1, 1)
        self.tblActionTypeFound = CTableView(ActionTypeFindDialog)
        self.tblActionTypeFound.setObjectName(_fromUtf8("tblActionTypeFound"))
        self.gridLayout.addWidget(self.tblActionTypeFound, 6, 0, 1, 3)
        self.btnSelectService = QtGui.QToolButton(ActionTypeFindDialog)
        self.btnSelectService.setObjectName(_fromUtf8("btnSelectService"))
        self.gridLayout.addWidget(self.btnSelectService, 4, 2, 1, 1)
        self.lblRecordsCount = QtGui.QLabel(ActionTypeFindDialog)
        self.lblRecordsCount.setObjectName(_fromUtf8("lblRecordsCount"))
        self.gridLayout.addWidget(self.lblRecordsCount, 8, 0, 1, 3)
        self.lblTissueType = QtGui.QLabel(ActionTypeFindDialog)
        self.lblTissueType.setObjectName(_fromUtf8("lblTissueType"))
        self.gridLayout.addWidget(self.lblTissueType, 3, 0, 1, 1)
        self.cmbTissueType = CRBComboBox(ActionTypeFindDialog)
        self.cmbTissueType.setObjectName(_fromUtf8("cmbTissueType"))
        self.gridLayout.addWidget(self.cmbTissueType, 3, 1, 1, 2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(ActionTypeFindDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Reset)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.horizontalLayout, 9, 0, 1, 3)
        self.lblCode.setBuddy(self.edtCode)
        self.lblNomenclativeCode.setBuddy(self.edtNomenclativeCode)
        self.lblName.setBuddy(self.edtName)
        self.lblProfilePayment.setBuddy(self.cmbService)
        self.lblTissueType.setBuddy(self.cmbTissueType)

        self.retranslateUi(ActionTypeFindDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ActionTypeFindDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ActionTypeFindDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ActionTypeFindDialog)
        ActionTypeFindDialog.setTabOrder(self.edtCode, self.edtNomenclativeCode)
        ActionTypeFindDialog.setTabOrder(self.edtNomenclativeCode, self.edtName)
        ActionTypeFindDialog.setTabOrder(self.edtName, self.cmbTissueType)
        ActionTypeFindDialog.setTabOrder(self.cmbTissueType, self.cmbService)
        ActionTypeFindDialog.setTabOrder(self.cmbService, self.btnSelectService)
        ActionTypeFindDialog.setTabOrder(self.btnSelectService, self.tblActionTypeFound)
        ActionTypeFindDialog.setTabOrder(self.tblActionTypeFound, self.buttonBox)

    def retranslateUi(self, ActionTypeFindDialog):
        ActionTypeFindDialog.setWindowTitle(QtGui.QApplication.translate("ActionTypeFindDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCode.setText(QtGui.QApplication.translate("ActionTypeFindDialog", "&Код", None, QtGui.QApplication.UnicodeUTF8))
        self.lblNomenclativeCode.setText(QtGui.QApplication.translate("ActionTypeFindDialog", "Номенклатурный код", None, QtGui.QApplication.UnicodeUTF8))
        self.lblName.setText(QtGui.QApplication.translate("ActionTypeFindDialog", "&Наименование", None, QtGui.QApplication.UnicodeUTF8))
        self.lblProfilePayment.setText(QtGui.QApplication.translate("ActionTypeFindDialog", "&Услуга", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectService.setText(QtGui.QApplication.translate("ActionTypeFindDialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.lblRecordsCount.setText(QtGui.QApplication.translate("ActionTypeFindDialog", "Список пуст", None, QtGui.QApplication.UnicodeUTF8))
        self.lblTissueType.setText(QtGui.QApplication.translate("ActionTypeFindDialog", "&Тип ткани", None, QtGui.QApplication.UnicodeUTF8))

from library.crbcombobox import CRBComboBox
from library.TableView import CTableView

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ActionTypeFindDialog = QtGui.QDialog()
    ui = Ui_ActionTypeFindDialog()
    ui.setupUi(ActionTypeFindDialog)
    ActionTypeFindDialog.show()
    sys.exit(app.exec_())

