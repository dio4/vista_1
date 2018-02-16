# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Reports\ReportF12_D_3_MSave.ui'
#
# Created: Fri Jun 15 12:15:53 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ReportF12_D_3_MSaveDialog(object):
    def setupUi(self, ReportF12_D_3_MSaveDialog):
        ReportF12_D_3_MSaveDialog.setObjectName(_fromUtf8("ReportF12_D_3_MSaveDialog"))
        ReportF12_D_3_MSaveDialog.resize(400, 150)
        self.gridLayout = QtGui.QGridLayout(ReportF12_D_3_MSaveDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = QtGui.QLabel(ReportF12_D_3_MSaveDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 2)
        self.nameEdit = QtGui.QLineEdit(ReportF12_D_3_MSaveDialog)
        self.nameEdit.setReadOnly(True)
        self.nameEdit.setObjectName(_fromUtf8("nameEdit"))
        self.gridLayout.addWidget(self.nameEdit, 0, 2, 1, 3)
        self.label = QtGui.QLabel(ReportF12_D_3_MSaveDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.edtFileDir = QtGui.QLineEdit(ReportF12_D_3_MSaveDialog)
        self.edtFileDir.setObjectName(_fromUtf8("edtFileDir"))
        self.gridLayout.addWidget(self.edtFileDir, 1, 2, 1, 2)
        self.btnSelectDir = QtGui.QToolButton(ReportF12_D_3_MSaveDialog)
        self.btnSelectDir.setObjectName(_fromUtf8("btnSelectDir"))
        self.gridLayout.addWidget(self.btnSelectDir, 1, 4, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 50, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
        self.saveButton = QtGui.QPushButton(ReportF12_D_3_MSaveDialog)
        self.saveButton.setEnabled(False)
        self.saveButton.setObjectName(_fromUtf8("saveButton"))
        self.gridLayout.addWidget(self.saveButton, 3, 0, 1, 1)
        self.btnSendMail = QtGui.QPushButton(ReportF12_D_3_MSaveDialog)
        self.btnSendMail.setEnabled(False)
        self.btnSendMail.setObjectName(_fromUtf8("btnSendMail"))
        self.gridLayout.addWidget(self.btnSendMail, 3, 1, 1, 2)
        self.reportButton = QtGui.QPushButton(ReportF12_D_3_MSaveDialog)
        self.reportButton.setEnabled(False)
        self.reportButton.setObjectName(_fromUtf8("reportButton"))
        self.gridLayout.addWidget(self.reportButton, 3, 3, 1, 2)

        self.retranslateUi(ReportF12_D_3_MSaveDialog)
        QtCore.QMetaObject.connectSlotsByName(ReportF12_D_3_MSaveDialog)
        ReportF12_D_3_MSaveDialog.setTabOrder(self.nameEdit, self.edtFileDir)
        ReportF12_D_3_MSaveDialog.setTabOrder(self.edtFileDir, self.btnSelectDir)
        ReportF12_D_3_MSaveDialog.setTabOrder(self.btnSelectDir, self.saveButton)
        ReportF12_D_3_MSaveDialog.setTabOrder(self.saveButton, self.btnSendMail)
        ReportF12_D_3_MSaveDialog.setTabOrder(self.btnSendMail, self.reportButton)

    def retranslateUi(self, ReportF12_D_3_MSaveDialog):
        ReportF12_D_3_MSaveDialog.setWindowTitle(QtGui.QApplication.translate("ReportF12_D_3_MSaveDialog", "Экспорт формы 12-3-М", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("ReportF12_D_3_MSaveDialog", "Имя файла (без расширения)", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ReportF12_D_3_MSaveDialog", "Сохранить в", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectDir.setText(QtGui.QApplication.translate("ReportF12_D_3_MSaveDialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.saveButton.setText(QtGui.QApplication.translate("ReportF12_D_3_MSaveDialog", "сохранить", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSendMail.setText(QtGui.QApplication.translate("ReportF12_D_3_MSaveDialog", "послать по почте", None, QtGui.QApplication.UnicodeUTF8))
        self.reportButton.setText(QtGui.QApplication.translate("ReportF12_D_3_MSaveDialog", "сформироать акт приёма-передачи", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ReportF12_D_3_MSaveDialog = QtGui.QDialog()
    ui = Ui_ReportF12_D_3_MSaveDialog()
    ui.setupUi(ReportF12_D_3_MSaveDialog)
    ReportF12_D_3_MSaveDialog.show()
    sys.exit(app.exec_())

