# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Quoting\QuotingEditorDialog.ui'
#
# Created: Fri Jun 15 12:16:57 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_QuotingEditorDialog(object):
    def setupUi(self, QuotingEditorDialog):
        QuotingEditorDialog.setObjectName(_fromUtf8("QuotingEditorDialog"))
        QuotingEditorDialog.resize(274, 154)
        self.gridLayout = QtGui.QGridLayout(QuotingEditorDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblQyotaType = QtGui.QLabel(QuotingEditorDialog)
        self.lblQyotaType.setObjectName(_fromUtf8("lblQyotaType"))
        self.gridLayout.addWidget(self.lblQyotaType, 0, 0, 1, 1)
        self.cmbQuotaType = CRBComboBox(QuotingEditorDialog)
        self.cmbQuotaType.setObjectName(_fromUtf8("cmbQuotaType"))
        self.gridLayout.addWidget(self.cmbQuotaType, 0, 1, 1, 1)
        self.lblBeginDate = QtGui.QLabel(QuotingEditorDialog)
        self.lblBeginDate.setObjectName(_fromUtf8("lblBeginDate"))
        self.gridLayout.addWidget(self.lblBeginDate, 1, 0, 1, 1)
        self.edtBeginDate = QtGui.QDateEdit(QuotingEditorDialog)
        self.edtBeginDate.setCalendarPopup(True)
        self.edtBeginDate.setObjectName(_fromUtf8("edtBeginDate"))
        self.gridLayout.addWidget(self.edtBeginDate, 1, 1, 1, 1)
        self.lblEndDate = QtGui.QLabel(QuotingEditorDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 2, 0, 1, 1)
        self.edtEndDate = QtGui.QDateEdit(QuotingEditorDialog)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 2, 1, 1, 1)
        self.lblLimit = QtGui.QLabel(QuotingEditorDialog)
        self.lblLimit.setObjectName(_fromUtf8("lblLimit"))
        self.gridLayout.addWidget(self.lblLimit, 3, 0, 1, 1)
        self.edtLimit = QtGui.QSpinBox(QuotingEditorDialog)
        self.edtLimit.setMaximum(131071)
        self.edtLimit.setObjectName(_fromUtf8("edtLimit"))
        self.gridLayout.addWidget(self.edtLimit, 3, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(QuotingEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 24, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 1, 1, 1)

        self.retranslateUi(QuotingEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), QuotingEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), QuotingEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(QuotingEditorDialog)

    def retranslateUi(self, QuotingEditorDialog):
        QuotingEditorDialog.setWindowTitle(QtGui.QApplication.translate("QuotingEditorDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.lblQyotaType.setText(QtGui.QApplication.translate("QuotingEditorDialog", "Название", None, QtGui.QApplication.UnicodeUTF8))
        self.lblBeginDate.setText(QtGui.QApplication.translate("QuotingEditorDialog", "Дата начала", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEndDate.setText(QtGui.QApplication.translate("QuotingEditorDialog", "Дата окончания", None, QtGui.QApplication.UnicodeUTF8))
        self.lblLimit.setText(QtGui.QApplication.translate("QuotingEditorDialog", "Предел", None, QtGui.QApplication.UnicodeUTF8))

from library.crbcombobox import CRBComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    QuotingEditorDialog = QtGui.QDialog()
    ui = Ui_QuotingEditorDialog()
    ui.setupUi(QuotingEditorDialog)
    QuotingEditorDialog.show()
    sys.exit(app.exec_())

