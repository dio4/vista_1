# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\RefBooks\RBTestEditor.ui'
#
# Created: Fri Jun 15 12:17:22 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_RBTestEditorDialog(object):
    def setupUi(self, RBTestEditorDialog):
        RBTestEditorDialog.setObjectName(_fromUtf8("RBTestEditorDialog"))
        RBTestEditorDialog.resize(443, 328)
        RBTestEditorDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(RBTestEditorDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tabWidget = QtGui.QTabWidget(RBTestEditorDialog)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tabMain = QtGui.QWidget()
        self.tabMain.setObjectName(_fromUtf8("tabMain"))
        self.gridLayout_2 = QtGui.QGridLayout(self.tabMain)
        self.gridLayout_2.setMargin(4)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.lblCode = QtGui.QLabel(self.tabMain)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridLayout_2.addWidget(self.lblCode, 0, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(self.tabMain)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout_2.addWidget(self.edtCode, 0, 1, 1, 1)
        self.lblName = QtGui.QLabel(self.tabMain)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout_2.addWidget(self.lblName, 1, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(self.tabMain)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout_2.addWidget(self.edtName, 1, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 4, 1, 1, 1)
        self.lblTestGroup = QtGui.QLabel(self.tabMain)
        self.lblTestGroup.setObjectName(_fromUtf8("lblTestGroup"))
        self.gridLayout_2.addWidget(self.lblTestGroup, 2, 0, 1, 1)
        self.cmbTestGroup = CRBComboBox(self.tabMain)
        self.cmbTestGroup.setObjectName(_fromUtf8("cmbTestGroup"))
        self.gridLayout_2.addWidget(self.cmbTestGroup, 2, 1, 1, 1)
        self.lblPosition = QtGui.QLabel(self.tabMain)
        self.lblPosition.setObjectName(_fromUtf8("lblPosition"))
        self.gridLayout_2.addWidget(self.lblPosition, 3, 0, 1, 1)
        self.edtPosition = QtGui.QSpinBox(self.tabMain)
        self.edtPosition.setMaximum(9999999)
        self.edtPosition.setObjectName(_fromUtf8("edtPosition"))
        self.gridLayout_2.addWidget(self.edtPosition, 3, 1, 1, 1)
        self.tabWidget.addTab(self.tabMain, _fromUtf8(""))
        self.tabEquipment = QtGui.QWidget()
        self.tabEquipment.setObjectName(_fromUtf8("tabEquipment"))
        self.gridLayout_3 = QtGui.QGridLayout(self.tabEquipment)
        self.gridLayout_3.setMargin(4)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.tblEquipments = CInDocTableView(self.tabEquipment)
        self.tblEquipments.setObjectName(_fromUtf8("tblEquipments"))
        self.gridLayout_3.addWidget(self.tblEquipments, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tabEquipment, _fromUtf8(""))
        self.tabAnalogTests = QtGui.QWidget()
        self.tabAnalogTests.setObjectName(_fromUtf8("tabAnalogTests"))
        self.verticalLayout = QtGui.QVBoxLayout(self.tabAnalogTests)
        self.verticalLayout.setMargin(4)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tblTestAnalog = CInDocTableView(self.tabAnalogTests)
        self.tblTestAnalog.setObjectName(_fromUtf8("tblTestAnalog"))
        self.verticalLayout.addWidget(self.tblTestAnalog)
        self.tabWidget.addTab(self.tabAnalogTests, _fromUtf8(""))
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(RBTestEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(RBTestEditorDialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), RBTestEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), RBTestEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(RBTestEditorDialog)
        RBTestEditorDialog.setTabOrder(self.tabWidget, self.edtCode)
        RBTestEditorDialog.setTabOrder(self.edtCode, self.edtName)
        RBTestEditorDialog.setTabOrder(self.edtName, self.cmbTestGroup)
        RBTestEditorDialog.setTabOrder(self.cmbTestGroup, self.edtPosition)
        RBTestEditorDialog.setTabOrder(self.edtPosition, self.tblEquipments)
        RBTestEditorDialog.setTabOrder(self.tblEquipments, self.tblTestAnalog)
        RBTestEditorDialog.setTabOrder(self.tblTestAnalog, self.buttonBox)

    def retranslateUi(self, RBTestEditorDialog):
        RBTestEditorDialog.setWindowTitle(QtGui.QApplication.translate("RBTestEditorDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCode.setText(QtGui.QApplication.translate("RBTestEditorDialog", "Код", None, QtGui.QApplication.UnicodeUTF8))
        self.lblName.setText(QtGui.QApplication.translate("RBTestEditorDialog", "Наименование", None, QtGui.QApplication.UnicodeUTF8))
        self.lblTestGroup.setText(QtGui.QApplication.translate("RBTestEditorDialog", "Группа", None, QtGui.QApplication.UnicodeUTF8))
        self.lblPosition.setText(QtGui.QApplication.translate("RBTestEditorDialog", "Позиция", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabMain), QtGui.QApplication.translate("RBTestEditorDialog", "&Основная информация", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabEquipment), QtGui.QApplication.translate("RBTestEditorDialog", "О&борудование", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabAnalogTests), QtGui.QApplication.translate("RBTestEditorDialog", "Тесты &аналоги", None, QtGui.QApplication.UnicodeUTF8))

from library.InDocTable import CInDocTableView
from library.crbcombobox import CRBComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    RBTestEditorDialog = QtGui.QDialog()
    ui = Ui_RBTestEditorDialog()
    ui.setupUi(RBTestEditorDialog)
    RBTestEditorDialog.show()
    sys.exit(app.exec_())

