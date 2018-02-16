# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Orgs\TestComboBoxPopup.ui'
#
# Created: Fri Jun 15 12:17:40 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_TestComboBoxPopupForm(object):
    def setupUi(self, TestComboBoxPopupForm):
        TestComboBoxPopupForm.setObjectName(_fromUtf8("TestComboBoxPopupForm"))
        TestComboBoxPopupForm.resize(491, 331)
        self.gridLayout = QtGui.QGridLayout(TestComboBoxPopupForm)
        self.gridLayout.setContentsMargins(1, 2, 1, 1)
        self.gridLayout.setHorizontalSpacing(1)
        self.gridLayout.setVerticalSpacing(2)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.cmbTestGroup = CRBComboBox(TestComboBoxPopupForm)
        self.cmbTestGroup.setObjectName(_fromUtf8("cmbTestGroup"))
        self.gridLayout.addWidget(self.cmbTestGroup, 0, 1, 1, 1)
        self.tblTests = CRBPopupView(TestComboBoxPopupForm)
        self.tblTests.setObjectName(_fromUtf8("tblTests"))
        self.gridLayout.addWidget(self.tblTests, 1, 0, 1, 2)
        self.lblTestGroup = QtGui.QLabel(TestComboBoxPopupForm)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblTestGroup.sizePolicy().hasHeightForWidth())
        self.lblTestGroup.setSizePolicy(sizePolicy)
        self.lblTestGroup.setObjectName(_fromUtf8("lblTestGroup"))
        self.gridLayout.addWidget(self.lblTestGroup, 0, 0, 1, 1)

        self.retranslateUi(TestComboBoxPopupForm)
        QtCore.QMetaObject.connectSlotsByName(TestComboBoxPopupForm)

    def retranslateUi(self, TestComboBoxPopupForm):
        TestComboBoxPopupForm.setWindowTitle(QtGui.QApplication.translate("TestComboBoxPopupForm", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.lblTestGroup.setText(QtGui.QApplication.translate("TestComboBoxPopupForm", "Группа", None, QtGui.QApplication.UnicodeUTF8))

from library.crbcombobox import CRBPopupView, CRBComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    TestComboBoxPopupForm = QtGui.QWidget()
    ui = Ui_TestComboBoxPopupForm()
    ui.setupUi(TestComboBoxPopupForm)
    TestComboBoxPopupForm.show()
    sys.exit(app.exec_())

