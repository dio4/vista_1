# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ExportRD2_Wizard_2.ui'
#
# Created: Fri Jun 15 12:15:15 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ExportRD2_Wizard_2(object):
    def setupUi(self, ExportRD2_Wizard_2):
        ExportRD2_Wizard_2.setObjectName(_fromUtf8("ExportRD2_Wizard_2"))
        ExportRD2_Wizard_2.resize(400, 300)
        self.gridlayout = QtGui.QGridLayout(ExportRD2_Wizard_2)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.label_2 = QtGui.QLabel(ExportRD2_Wizard_2)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.hboxlayout.addWidget(self.label_2)
        self.nameEdit = QtGui.QLineEdit(ExportRD2_Wizard_2)
        self.nameEdit.setObjectName(_fromUtf8("nameEdit"))
        self.hboxlayout.addWidget(self.nameEdit)
        self.gridlayout.addLayout(self.hboxlayout, 0, 0, 1, 1)
        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setObjectName(_fromUtf8("hboxlayout1"))
        self.label = QtGui.QLabel(ExportRD2_Wizard_2)
        self.label.setObjectName(_fromUtf8("label"))
        self.hboxlayout1.addWidget(self.label)
        self.edtFileDir = QtGui.QLineEdit(ExportRD2_Wizard_2)
        self.edtFileDir.setObjectName(_fromUtf8("edtFileDir"))
        self.hboxlayout1.addWidget(self.edtFileDir)
        self.btnSelectDir = QtGui.QToolButton(ExportRD2_Wizard_2)
        self.btnSelectDir.setObjectName(_fromUtf8("btnSelectDir"))
        self.hboxlayout1.addWidget(self.btnSelectDir)
        self.gridlayout.addLayout(self.hboxlayout1, 1, 0, 1, 1)
        self.saveButton = QtGui.QPushButton(ExportRD2_Wizard_2)
        self.saveButton.setEnabled(False)
        self.saveButton.setObjectName(_fromUtf8("saveButton"))
        self.gridlayout.addWidget(self.saveButton, 2, 0, 1, 1)
        self.btnSendMail = QtGui.QPushButton(ExportRD2_Wizard_2)
        self.btnSendMail.setObjectName(_fromUtf8("btnSendMail"))
        self.gridlayout.addWidget(self.btnSendMail, 4, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 3, 0, 1, 1)
        self.reportButton = QtGui.QPushButton(ExportRD2_Wizard_2)
        self.reportButton.setObjectName(_fromUtf8("reportButton"))
        self.gridlayout.addWidget(self.reportButton, 5, 0, 1, 1)

        self.retranslateUi(ExportRD2_Wizard_2)
        QtCore.QMetaObject.connectSlotsByName(ExportRD2_Wizard_2)

    def retranslateUi(self, ExportRD2_Wizard_2):
        ExportRD2_Wizard_2.setWindowTitle(QtGui.QApplication.translate("ExportRD2_Wizard_2", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("ExportRD2_Wizard_2", "имя файла (без расширения)", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ExportRD2_Wizard_2", "сохранить в", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectDir.setText(QtGui.QApplication.translate("ExportRD2_Wizard_2", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.saveButton.setText(QtGui.QApplication.translate("ExportRD2_Wizard_2", "сохранить", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSendMail.setText(QtGui.QApplication.translate("ExportRD2_Wizard_2", "послать по почте", None, QtGui.QApplication.UnicodeUTF8))
        self.reportButton.setText(QtGui.QApplication.translate("ExportRD2_Wizard_2", "сформироать акт приёма-передачи", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ExportRD2_Wizard_2 = QtGui.QDialog()
    ui = Ui_ExportRD2_Wizard_2()
    ui.setupUi(ExportRD2_Wizard_2)
    ExportRD2_Wizard_2.show()
    sys.exit(app.exec_())

