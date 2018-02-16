# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Registry\ClientQuotaDiscussionEditor.ui'
#
# Created: Fri Jun 15 12:16:50 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ClientQuotaDiscussionEditor(object):
    def setupUi(self, ClientQuotaDiscussionEditor):
        ClientQuotaDiscussionEditor.setObjectName(_fromUtf8("ClientQuotaDiscussionEditor"))
        ClientQuotaDiscussionEditor.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(ClientQuotaDiscussionEditor)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.lblDateMessage = QtGui.QLabel(ClientQuotaDiscussionEditor)
        self.lblDateMessage.setObjectName(_fromUtf8("lblDateMessage"))
        self.verticalLayout.addWidget(self.lblDateMessage)
        self.lblAgreementType = QtGui.QLabel(ClientQuotaDiscussionEditor)
        self.lblAgreementType.setObjectName(_fromUtf8("lblAgreementType"))
        self.verticalLayout.addWidget(self.lblAgreementType)
        self.lblResponsiblePerson = QtGui.QLabel(ClientQuotaDiscussionEditor)
        self.lblResponsiblePerson.setObjectName(_fromUtf8("lblResponsiblePerson"))
        self.verticalLayout.addWidget(self.lblResponsiblePerson)
        self.lblCosignatory = QtGui.QLabel(ClientQuotaDiscussionEditor)
        self.lblCosignatory.setObjectName(_fromUtf8("lblCosignatory"))
        self.verticalLayout.addWidget(self.lblCosignatory)
        self.lblCosignatoryPost = QtGui.QLabel(ClientQuotaDiscussionEditor)
        self.lblCosignatoryPost.setObjectName(_fromUtf8("lblCosignatoryPost"))
        self.verticalLayout.addWidget(self.lblCosignatoryPost)
        self.lblCosignatoryName = QtGui.QLabel(ClientQuotaDiscussionEditor)
        self.lblCosignatoryName.setObjectName(_fromUtf8("lblCosignatoryName"))
        self.verticalLayout.addWidget(self.lblCosignatoryName)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.edtDateMessage = QtGui.QDateTimeEdit(ClientQuotaDiscussionEditor)
        self.edtDateMessage.setCalendarPopup(True)
        self.edtDateMessage.setObjectName(_fromUtf8("edtDateMessage"))
        self.verticalLayout_2.addWidget(self.edtDateMessage)
        self.cmbAgreementType = CRBComboBox(ClientQuotaDiscussionEditor)
        self.cmbAgreementType.setObjectName(_fromUtf8("cmbAgreementType"))
        self.verticalLayout_2.addWidget(self.cmbAgreementType)
        self.cmbResponsiblePerson = CRBComboBox(ClientQuotaDiscussionEditor)
        self.cmbResponsiblePerson.setObjectName(_fromUtf8("cmbResponsiblePerson"))
        self.verticalLayout_2.addWidget(self.cmbResponsiblePerson)
        self.edtCosignatory = QtGui.QLineEdit(ClientQuotaDiscussionEditor)
        self.edtCosignatory.setObjectName(_fromUtf8("edtCosignatory"))
        self.verticalLayout_2.addWidget(self.edtCosignatory)
        self.edtCosignatoryPost = QtGui.QLineEdit(ClientQuotaDiscussionEditor)
        self.edtCosignatoryPost.setObjectName(_fromUtf8("edtCosignatoryPost"))
        self.verticalLayout_2.addWidget(self.edtCosignatoryPost)
        self.edtCosignatoryName = QtGui.QLineEdit(ClientQuotaDiscussionEditor)
        self.edtCosignatoryName.setObjectName(_fromUtf8("edtCosignatoryName"))
        self.verticalLayout_2.addWidget(self.edtCosignatoryName)
        self.gridLayout.addLayout(self.verticalLayout_2, 0, 1, 1, 2)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.lblRemark = QtGui.QLabel(ClientQuotaDiscussionEditor)
        self.lblRemark.setObjectName(_fromUtf8("lblRemark"))
        self.verticalLayout_3.addWidget(self.lblRemark)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.gridLayout.addLayout(self.verticalLayout_3, 1, 0, 1, 1)
        self.edtRemark = QtGui.QTextEdit(ClientQuotaDiscussionEditor)
        self.edtRemark.setObjectName(_fromUtf8("edtRemark"))
        self.gridLayout.addWidget(self.edtRemark, 1, 1, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ClientQuotaDiscussionEditor)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 2, 1, 1)

        self.retranslateUi(ClientQuotaDiscussionEditor)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ClientQuotaDiscussionEditor.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ClientQuotaDiscussionEditor.reject)
        QtCore.QMetaObject.connectSlotsByName(ClientQuotaDiscussionEditor)

    def retranslateUi(self, ClientQuotaDiscussionEditor):
        ClientQuotaDiscussionEditor.setWindowTitle(QtGui.QApplication.translate("ClientQuotaDiscussionEditor", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.lblDateMessage.setText(QtGui.QApplication.translate("ClientQuotaDiscussionEditor", "Дата и время сообщения", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAgreementType.setText(QtGui.QApplication.translate("ClientQuotaDiscussionEditor", "Тип согласования", None, QtGui.QApplication.UnicodeUTF8))
        self.lblResponsiblePerson.setText(QtGui.QApplication.translate("ClientQuotaDiscussionEditor", "Ответственный ЛПУ", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCosignatory.setText(QtGui.QApplication.translate("ClientQuotaDiscussionEditor", "Контрагент", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCosignatoryPost.setText(QtGui.QApplication.translate("ClientQuotaDiscussionEditor", "Должность", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCosignatoryName.setText(QtGui.QApplication.translate("ClientQuotaDiscussionEditor", "ФИО", None, QtGui.QApplication.UnicodeUTF8))
        self.lblRemark.setText(QtGui.QApplication.translate("ClientQuotaDiscussionEditor", "Примечания", None, QtGui.QApplication.UnicodeUTF8))

from library.crbcombobox import CRBComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ClientQuotaDiscussionEditor = QtGui.QDialog()
    ui = Ui_ClientQuotaDiscussionEditor()
    ui.setupUi(ClientQuotaDiscussionEditor)
    ClientQuotaDiscussionEditor.show()
    sys.exit(app.exec_())

