# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Events\DiagnosisConfirmationDialog.ui'
#
# Created: Fri Jun 15 12:16:11 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_DiagnosisConfirmationDialog(object):
    def setupUi(self, DiagnosisConfirmationDialog):
        DiagnosisConfirmationDialog.setObjectName(_fromUtf8("DiagnosisConfirmationDialog"))
        DiagnosisConfirmationDialog.resize(593, 97)
        self.gridLayout = QtGui.QGridLayout(DiagnosisConfirmationDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblMessage = QtGui.QLabel(DiagnosisConfirmationDialog)
        self.lblMessage.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lblMessage.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.lblMessage.setObjectName(_fromUtf8("lblMessage"))
        self.gridLayout.addWidget(self.lblMessage, 0, 0, 1, 3)
        self.btnAcceptOld = QtGui.QPushButton(DiagnosisConfirmationDialog)
        self.btnAcceptOld.setDefault(True)
        self.btnAcceptOld.setObjectName(_fromUtf8("btnAcceptOld"))
        self.gridLayout.addWidget(self.btnAcceptOld, 1, 0, 1, 1)
        self.btnAcceptNew = QtGui.QPushButton(DiagnosisConfirmationDialog)
        self.btnAcceptNew.setObjectName(_fromUtf8("btnAcceptNew"))
        self.gridLayout.addWidget(self.btnAcceptNew, 1, 1, 1, 1)
        self.btnAcceptNewAndModifyOld = QtGui.QPushButton(DiagnosisConfirmationDialog)
        self.btnAcceptNewAndModifyOld.setObjectName(_fromUtf8("btnAcceptNewAndModifyOld"))
        self.gridLayout.addWidget(self.btnAcceptNewAndModifyOld, 1, 2, 1, 1)

        self.retranslateUi(DiagnosisConfirmationDialog)
        QtCore.QMetaObject.connectSlotsByName(DiagnosisConfirmationDialog)

    def retranslateUi(self, DiagnosisConfirmationDialog):
        DiagnosisConfirmationDialog.setWindowTitle(QtGui.QApplication.translate("DiagnosisConfirmationDialog", "Внимание", None, QtGui.QApplication.UnicodeUTF8))
        self.lblMessage.setText(QtGui.QApplication.translate("DiagnosisConfirmationDialog", "Ведён код J06.0 (Острый ларингофарингит)\n"
"Ранее для этого пациента был указан код J06.9 (Острая инфекция верхних дыхательных путей неуточненная)\n"
"Изменить на этот код?", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAcceptOld.setText(QtGui.QApplication.translate("DiagnosisConfirmationDialog", "Изменить на J06.9", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAcceptNew.setText(QtGui.QApplication.translate("DiagnosisConfirmationDialog", "Принять J06.0", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAcceptNewAndModifyOld.setText(QtGui.QApplication.translate("DiagnosisConfirmationDialog", "Принять J06.0 и отметить J06.9 как изменённый", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    DiagnosisConfirmationDialog = QtGui.QDialog()
    ui = Ui_DiagnosisConfirmationDialog()
    ui.setupUi(DiagnosisConfirmationDialog)
    DiagnosisConfirmationDialog.show()
    sys.exit(app.exec_())

