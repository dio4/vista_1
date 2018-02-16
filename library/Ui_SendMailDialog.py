# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\library\SendMailDialog.ui'
#
# Created: Fri Jun 15 12:15:31 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_SendMailDialog(object):
    def setupUi(self, SendMailDialog):
        SendMailDialog.setObjectName(_fromUtf8("SendMailDialog"))
        SendMailDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        SendMailDialog.resize(451, 307)
        SendMailDialog.setSizeGripEnabled(True)
        SendMailDialog.setModal(True)
        self.gridlayout = QtGui.QGridLayout(SendMailDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.lblRecipient = QtGui.QLabel(SendMailDialog)
        self.lblRecipient.setObjectName(_fromUtf8("lblRecipient"))
        self.gridlayout.addWidget(self.lblRecipient, 0, 0, 1, 1)
        self.edtRecipient = QtGui.QLineEdit(SendMailDialog)
        self.edtRecipient.setObjectName(_fromUtf8("edtRecipient"))
        self.gridlayout.addWidget(self.edtRecipient, 0, 1, 1, 1)
        self.lblSubject = QtGui.QLabel(SendMailDialog)
        self.lblSubject.setObjectName(_fromUtf8("lblSubject"))
        self.gridlayout.addWidget(self.lblSubject, 1, 0, 1, 1)
        self.edtSubject = QtGui.QLineEdit(SendMailDialog)
        self.edtSubject.setObjectName(_fromUtf8("edtSubject"))
        self.gridlayout.addWidget(self.edtSubject, 1, 1, 1, 1)
        self.lblText = QtGui.QLabel(SendMailDialog)
        self.lblText.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lblText.setObjectName(_fromUtf8("lblText"))
        self.gridlayout.addWidget(self.lblText, 2, 0, 1, 1)
        self.edtText = QtGui.QTextEdit(SendMailDialog)
        self.edtText.setObjectName(_fromUtf8("edtText"))
        self.gridlayout.addWidget(self.edtText, 2, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(SendMailDialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 4, 0, 1, 2)
        self.label = QtGui.QLabel(SendMailDialog)
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridlayout.addWidget(self.label, 3, 0, 1, 1)
        self.tblAttach = CTableView(SendMailDialog)
        self.tblAttach.setObjectName(_fromUtf8("tblAttach"))
        self.gridlayout.addWidget(self.tblAttach, 3, 1, 1, 1)
        self.lblRecipient.setBuddy(self.edtRecipient)
        self.lblSubject.setBuddy(self.edtSubject)
        self.lblText.setBuddy(self.edtText)

        self.retranslateUi(SendMailDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SendMailDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SendMailDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SendMailDialog)
        SendMailDialog.setTabOrder(self.edtRecipient, self.edtSubject)
        SendMailDialog.setTabOrder(self.edtSubject, self.edtText)
        SendMailDialog.setTabOrder(self.edtText, self.buttonBox)

    def retranslateUi(self, SendMailDialog):
        SendMailDialog.setWindowTitle(QtGui.QApplication.translate("SendMailDialog", "подготовка к отправке e-mail", None, QtGui.QApplication.UnicodeUTF8))
        self.lblRecipient.setText(QtGui.QApplication.translate("SendMailDialog", "Кому", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSubject.setText(QtGui.QApplication.translate("SendMailDialog", "Тема", None, QtGui.QApplication.UnicodeUTF8))
        self.lblText.setText(QtGui.QApplication.translate("SendMailDialog", "Текст", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("SendMailDialog", "Вложенные\n"
"файлы", None, QtGui.QApplication.UnicodeUTF8))

from TableView import CTableView

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    SendMailDialog = QtGui.QDialog()
    ui = Ui_SendMailDialog()
    ui.setupUi(SendMailDialog)
    SendMailDialog.show()
    sys.exit(app.exec_())

