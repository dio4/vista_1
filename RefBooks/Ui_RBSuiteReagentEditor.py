# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\RefBooks\RBSuiteReagentEditor.ui'
#
# Created: Fri Jun 15 12:17:36 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_RBSuiteReagentEditorDialog(object):
    def setupUi(self, RBSuiteReagentEditorDialog):
        RBSuiteReagentEditorDialog.setObjectName(_fromUtf8("RBSuiteReagentEditorDialog"))
        RBSuiteReagentEditorDialog.resize(626, 385)
        RBSuiteReagentEditorDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(RBSuiteReagentEditorDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonBox = QtGui.QDialogButtonBox(RBSuiteReagentEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 2)
        self.tabWidget = QtGui.QTabWidget(RBSuiteReagentEditorDialog)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tabSuiteReagent = QtGui.QWidget()
        self.tabSuiteReagent.setObjectName(_fromUtf8("tabSuiteReagent"))
        self.gridLayout_2 = QtGui.QGridLayout(self.tabSuiteReagent)
        self.gridLayout_2.setMargin(4)
        self.gridLayout_2.setSpacing(4)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.lblCode = QtGui.QLabel(self.tabSuiteReagent)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblCode.sizePolicy().hasHeightForWidth())
        self.lblCode.setSizePolicy(sizePolicy)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridLayout_2.addWidget(self.lblCode, 0, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(self.tabSuiteReagent)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout_2.addWidget(self.edtCode, 0, 1, 1, 1)
        self.lblName = QtGui.QLabel(self.tabSuiteReagent)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout_2.addWidget(self.lblName, 1, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(self.tabSuiteReagent)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout_2.addWidget(self.edtName, 1, 1, 1, 1)
        self.lblRecipientPerson = QtGui.QLabel(self.tabSuiteReagent)
        self.lblRecipientPerson.setObjectName(_fromUtf8("lblRecipientPerson"))
        self.gridLayout_2.addWidget(self.lblRecipientPerson, 2, 0, 1, 1)
        self.cmbRecipientPerson = CPersonComboBoxEx(self.tabSuiteReagent)
        self.cmbRecipientPerson.setObjectName(_fromUtf8("cmbRecipientPerson"))
        self.gridLayout_2.addWidget(self.cmbRecipientPerson, 2, 1, 1, 1)
        self.lblReleaseDate = QtGui.QLabel(self.tabSuiteReagent)
        self.lblReleaseDate.setObjectName(_fromUtf8("lblReleaseDate"))
        self.gridLayout_2.addWidget(self.lblReleaseDate, 3, 0, 1, 1)
        self.edtReleaseDate = CDateEdit(self.tabSuiteReagent)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtReleaseDate.sizePolicy().hasHeightForWidth())
        self.edtReleaseDate.setSizePolicy(sizePolicy)
        self.edtReleaseDate.setObjectName(_fromUtf8("edtReleaseDate"))
        self.gridLayout_2.addWidget(self.edtReleaseDate, 3, 1, 1, 1)
        self.lblSupplyDate = QtGui.QLabel(self.tabSuiteReagent)
        self.lblSupplyDate.setObjectName(_fromUtf8("lblSupplyDate"))
        self.gridLayout_2.addWidget(self.lblSupplyDate, 4, 0, 1, 1)
        self.edtSupplyDate = CDateEdit(self.tabSuiteReagent)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtSupplyDate.sizePolicy().hasHeightForWidth())
        self.edtSupplyDate.setSizePolicy(sizePolicy)
        self.edtSupplyDate.setObjectName(_fromUtf8("edtSupplyDate"))
        self.gridLayout_2.addWidget(self.edtSupplyDate, 4, 1, 1, 1)
        self.lblExpiryDate = QtGui.QLabel(self.tabSuiteReagent)
        self.lblExpiryDate.setObjectName(_fromUtf8("lblExpiryDate"))
        self.gridLayout_2.addWidget(self.lblExpiryDate, 6, 0, 1, 1)
        self.edtExpiryDate = CDateEdit(self.tabSuiteReagent)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtExpiryDate.sizePolicy().hasHeightForWidth())
        self.edtExpiryDate.setSizePolicy(sizePolicy)
        self.edtExpiryDate.setObjectName(_fromUtf8("edtExpiryDate"))
        self.gridLayout_2.addWidget(self.edtExpiryDate, 6, 1, 1, 1)
        self.lblPlanTestQuantity = QtGui.QLabel(self.tabSuiteReagent)
        self.lblPlanTestQuantity.setObjectName(_fromUtf8("lblPlanTestQuantity"))
        self.gridLayout_2.addWidget(self.lblPlanTestQuantity, 7, 0, 1, 1)
        self.edtPlanTestQuantity = QtGui.QSpinBox(self.tabSuiteReagent)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtPlanTestQuantity.sizePolicy().hasHeightForWidth())
        self.edtPlanTestQuantity.setSizePolicy(sizePolicy)
        self.edtPlanTestQuantity.setObjectName(_fromUtf8("edtPlanTestQuantity"))
        self.gridLayout_2.addWidget(self.edtPlanTestQuantity, 7, 1, 1, 1)
        self.lblManufacturer = QtGui.QLabel(self.tabSuiteReagent)
        self.lblManufacturer.setObjectName(_fromUtf8("lblManufacturer"))
        self.gridLayout_2.addWidget(self.lblManufacturer, 8, 0, 1, 1)
        self.edtManufacturer = QtGui.QLineEdit(self.tabSuiteReagent)
        self.edtManufacturer.setObjectName(_fromUtf8("edtManufacturer"))
        self.gridLayout_2.addWidget(self.edtManufacturer, 8, 1, 1, 1)
        self.lblStorageConditions = QtGui.QLabel(self.tabSuiteReagent)
        self.lblStorageConditions.setObjectName(_fromUtf8("lblStorageConditions"))
        self.gridLayout_2.addWidget(self.lblStorageConditions, 9, 0, 1, 1)
        self.edtStorageConditions = QtGui.QLineEdit(self.tabSuiteReagent)
        self.edtStorageConditions.setObjectName(_fromUtf8("edtStorageConditions"))
        self.gridLayout_2.addWidget(self.edtStorageConditions, 9, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 10, 1, 1, 1)
        self.lblStartOperationDate = QtGui.QLabel(self.tabSuiteReagent)
        self.lblStartOperationDate.setObjectName(_fromUtf8("lblStartOperationDate"))
        self.gridLayout_2.addWidget(self.lblStartOperationDate, 5, 0, 1, 1)
        self.edtStartOperationDate = CDateEdit(self.tabSuiteReagent)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtStartOperationDate.sizePolicy().hasHeightForWidth())
        self.edtStartOperationDate.setSizePolicy(sizePolicy)
        self.edtStartOperationDate.setObjectName(_fromUtf8("edtStartOperationDate"))
        self.gridLayout_2.addWidget(self.edtStartOperationDate, 5, 1, 1, 1)
        self.tabWidget.addTab(self.tabSuiteReagent, _fromUtf8(""))
        self.tabtTests = QtGui.QWidget()
        self.tabtTests.setObjectName(_fromUtf8("tabtTests"))
        self.verticalLayout = QtGui.QVBoxLayout(self.tabtTests)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setMargin(4)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tblTests = CInDocTableView(self.tabtTests)
        self.tblTests.setObjectName(_fromUtf8("tblTests"))
        self.verticalLayout.addWidget(self.tblTests)
        self.tabWidget.addTab(self.tabtTests, _fromUtf8(""))
        self.gridLayout.addWidget(self.tabWidget, 0, 1, 1, 1)

        self.retranslateUi(RBSuiteReagentEditorDialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), RBSuiteReagentEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), RBSuiteReagentEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(RBSuiteReagentEditorDialog)
        RBSuiteReagentEditorDialog.setTabOrder(self.tabWidget, self.edtCode)
        RBSuiteReagentEditorDialog.setTabOrder(self.edtCode, self.edtName)
        RBSuiteReagentEditorDialog.setTabOrder(self.edtName, self.cmbRecipientPerson)
        RBSuiteReagentEditorDialog.setTabOrder(self.cmbRecipientPerson, self.edtReleaseDate)
        RBSuiteReagentEditorDialog.setTabOrder(self.edtReleaseDate, self.edtSupplyDate)
        RBSuiteReagentEditorDialog.setTabOrder(self.edtSupplyDate, self.edtStartOperationDate)
        RBSuiteReagentEditorDialog.setTabOrder(self.edtStartOperationDate, self.edtExpiryDate)
        RBSuiteReagentEditorDialog.setTabOrder(self.edtExpiryDate, self.edtPlanTestQuantity)
        RBSuiteReagentEditorDialog.setTabOrder(self.edtPlanTestQuantity, self.edtManufacturer)
        RBSuiteReagentEditorDialog.setTabOrder(self.edtManufacturer, self.edtStorageConditions)
        RBSuiteReagentEditorDialog.setTabOrder(self.edtStorageConditions, self.tblTests)
        RBSuiteReagentEditorDialog.setTabOrder(self.tblTests, self.buttonBox)

    def retranslateUi(self, RBSuiteReagentEditorDialog):
        RBSuiteReagentEditorDialog.setWindowTitle(QtGui.QApplication.translate("RBSuiteReagentEditorDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCode.setText(QtGui.QApplication.translate("RBSuiteReagentEditorDialog", "Код", None, QtGui.QApplication.UnicodeUTF8))
        self.lblName.setText(QtGui.QApplication.translate("RBSuiteReagentEditorDialog", "Наименование", None, QtGui.QApplication.UnicodeUTF8))
        self.lblRecipientPerson.setText(QtGui.QApplication.translate("RBSuiteReagentEditorDialog", "Ответственный", None, QtGui.QApplication.UnicodeUTF8))
        self.lblReleaseDate.setText(QtGui.QApplication.translate("RBSuiteReagentEditorDialog", "Дата выпуска", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSupplyDate.setText(QtGui.QApplication.translate("RBSuiteReagentEditorDialog", "Дата поступления", None, QtGui.QApplication.UnicodeUTF8))
        self.lblExpiryDate.setText(QtGui.QApplication.translate("RBSuiteReagentEditorDialog", "Срок годности", None, QtGui.QApplication.UnicodeUTF8))
        self.lblPlanTestQuantity.setText(QtGui.QApplication.translate("RBSuiteReagentEditorDialog", "Плановое количество тестов", None, QtGui.QApplication.UnicodeUTF8))
        self.lblManufacturer.setText(QtGui.QApplication.translate("RBSuiteReagentEditorDialog", "Производитель", None, QtGui.QApplication.UnicodeUTF8))
        self.lblStorageConditions.setText(QtGui.QApplication.translate("RBSuiteReagentEditorDialog", "Условия хранения", None, QtGui.QApplication.UnicodeUTF8))
        self.lblStartOperationDate.setText(QtGui.QApplication.translate("RBSuiteReagentEditorDialog", "Дата передачи в работу", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabSuiteReagent), QtGui.QApplication.translate("RBSuiteReagentEditorDialog", "&Набор", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabtTests), QtGui.QApplication.translate("RBSuiteReagentEditorDialog", "&Тесты", None, QtGui.QApplication.UnicodeUTF8))

from library.InDocTable import CInDocTableView
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.DateEdit import CDateEdit

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    RBSuiteReagentEditorDialog = QtGui.QDialog()
    ui = Ui_RBSuiteReagentEditorDialog()
    ui.setupUi(RBSuiteReagentEditorDialog)
    RBSuiteReagentEditorDialog.show()
    sys.exit(app.exec_())
