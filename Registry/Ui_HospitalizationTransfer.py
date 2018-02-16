# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'HospitalizationTransfer.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_HospitalizationTransferDialog(object):
    def setupUi(self, HospitalizationTransferDialog):
        HospitalizationTransferDialog.setObjectName(_fromUtf8("HospitalizationTransferDialog"))
        HospitalizationTransferDialog.resize(507, 648)
        self.gridLayout = QtGui.QGridLayout(HospitalizationTransferDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.edtTransferDate = CDateEdit(HospitalizationTransferDialog)
        self.edtTransferDate.setCalendarPopup(True)
        self.edtTransferDate.setObjectName(_fromUtf8("edtTransferDate"))
        self.gridLayout.addWidget(self.edtTransferDate, 3, 0, 1, 2)
        self.lblComment = QtGui.QLabel(HospitalizationTransferDialog)
        self.lblComment.setObjectName(_fromUtf8("lblComment"))
        self.gridLayout.addWidget(self.lblComment, 0, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(HospitalizationTransferDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 1, 1, 1)
        self.lblTransferDate = QtGui.QLabel(HospitalizationTransferDialog)
        self.lblTransferDate.setObjectName(_fromUtf8("lblTransferDate"))
        self.gridLayout.addWidget(self.lblTransferDate, 2, 0, 1, 2)
        self.edtComment = QtGui.QTextEdit(HospitalizationTransferDialog)
        self.edtComment.setObjectName(_fromUtf8("edtComment"))
        self.gridLayout.addWidget(self.edtComment, 1, 0, 1, 2)
        self.grpConsultation = QtGui.QGroupBox(HospitalizationTransferDialog)
        self.grpConsultation.setEnabled(True)
        self.grpConsultation.setObjectName(_fromUtf8("grpConsultation"))
        self.gridLayout_2 = QtGui.QGridLayout(self.grpConsultation)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.scrollArea = QtGui.QScrollArea(self.grpConsultation)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 475, 347))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.gridLayout_3 = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.edtDiagnosis = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        self.edtDiagnosis.setObjectName(_fromUtf8("edtDiagnosis"))
        self.gridLayout_3.addWidget(self.edtDiagnosis, 1, 0, 1, 1)
        self.lblRecommentedTreatment = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.lblRecommentedTreatment.setObjectName(_fromUtf8("lblRecommentedTreatment"))
        self.gridLayout_3.addWidget(self.lblRecommentedTreatment, 4, 0, 1, 1)
        self.lblDiagnosis = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.lblDiagnosis.setObjectName(_fromUtf8("lblDiagnosis"))
        self.gridLayout_3.addWidget(self.lblDiagnosis, 0, 0, 1, 1)
        self.lblTreatmentMethod = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.lblTreatmentMethod.setObjectName(_fromUtf8("lblTreatmentMethod"))
        self.gridLayout_3.addWidget(self.lblTreatmentMethod, 2, 0, 1, 1)
        self.edtTreatmentMethod = QtGui.QTextEdit(self.scrollAreaWidgetContents)
        self.edtTreatmentMethod.setObjectName(_fromUtf8("edtTreatmentMethod"))
        self.gridLayout_3.addWidget(self.edtTreatmentMethod, 3, 0, 1, 1)
        self.edtRecommentedTreatment = QtGui.QTextEdit(self.scrollAreaWidgetContents)
        self.edtRecommentedTreatment.setObjectName(_fromUtf8("edtRecommentedTreatment"))
        self.gridLayout_3.addWidget(self.edtRecommentedTreatment, 5, 0, 1, 1)
        self.lblTreatmentOrgStructure = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.lblTreatmentOrgStructure.setObjectName(_fromUtf8("lblTreatmentOrgStructure"))
        self.gridLayout_3.addWidget(self.lblTreatmentOrgStructure, 6, 0, 1, 1)
        self.edtTreatmentOrgStructure = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        self.edtTreatmentOrgStructure.setObjectName(_fromUtf8("edtTreatmentOrgStructure"))
        self.gridLayout_3.addWidget(self.edtTreatmentOrgStructure, 7, 0, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout_2.addWidget(self.scrollArea, 0, 0, 1, 2)
        self.gridLayout.addWidget(self.grpConsultation, 4, 0, 1, 2)

        self.retranslateUi(HospitalizationTransferDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), HospitalizationTransferDialog.reject)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), HospitalizationTransferDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(HospitalizationTransferDialog)
        HospitalizationTransferDialog.setTabOrder(self.edtComment, self.edtTransferDate)
        HospitalizationTransferDialog.setTabOrder(self.edtTransferDate, self.scrollArea)
        HospitalizationTransferDialog.setTabOrder(self.scrollArea, self.edtDiagnosis)
        HospitalizationTransferDialog.setTabOrder(self.edtDiagnosis, self.edtTreatmentMethod)
        HospitalizationTransferDialog.setTabOrder(self.edtTreatmentMethod, self.edtRecommentedTreatment)
        HospitalizationTransferDialog.setTabOrder(self.edtRecommentedTreatment, self.edtTreatmentOrgStructure)
        HospitalizationTransferDialog.setTabOrder(self.edtTreatmentOrgStructure, self.buttonBox)

    def retranslateUi(self, HospitalizationTransferDialog):
        HospitalizationTransferDialog.setWindowTitle(_translate("HospitalizationTransferDialog", "Перенос госпитализации", None))
        self.edtTransferDate.setWhatsThis(_translate("HospitalizationTransferDialog", "дата окончания осмотра", None))
        self.lblComment.setText(_translate("HospitalizationTransferDialog", "Причина переноса:", None))
        self.lblTransferDate.setText(_translate("HospitalizationTransferDialog", "Новая плановая дата госпитализации:", None))
        self.grpConsultation.setTitle(_translate("HospitalizationTransferDialog", "Консультация врача", None))
        self.lblRecommentedTreatment.setText(_translate("HospitalizationTransferDialog", "Рекомендации:", None))
        self.lblDiagnosis.setText(_translate("HospitalizationTransferDialog", "Диагноз:", None))
        self.lblTreatmentMethod.setText(_translate("HospitalizationTransferDialog", "Метод лечения:", None))
        self.lblTreatmentOrgStructure.setText(_translate("HospitalizationTransferDialog", "Лечебное отделение:", None))

from library.DateEdit import CDateEdit
