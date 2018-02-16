# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'OperationInfoDialog.ui'
#
# Created: Fri Aug 15 17:57:30 2014
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_OperationInfoDialog(object):
    def setupUi(self, OperationInfoDialog):
        OperationInfoDialog.setObjectName(_fromUtf8("OperationInfoDialog"))
        OperationInfoDialog.resize(313, 296)
        self.gridLayout = QtGui.QGridLayout(OperationInfoDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblPersonName = QtGui.QLabel(OperationInfoDialog)
        self.lblPersonName.setObjectName(_fromUtf8("lblPersonName"))
        self.gridLayout.addWidget(self.lblPersonName, 0, 0, 1, 2)
        self.edtPersonName = QtGui.QLineEdit(OperationInfoDialog)
        self.edtPersonName.setObjectName(_fromUtf8("edtPersonName"))
        self.gridLayout.addWidget(self.edtPersonName, 1, 0, 1, 3)
        self.gbNaturalPersonDocument = QtGui.QGroupBox(OperationInfoDialog)
        self.gbNaturalPersonDocument.setCheckable(True)
        self.gbNaturalPersonDocument.setObjectName(_fromUtf8("gbNaturalPersonDocument"))
        self.gridLayout_14 = QtGui.QGridLayout(self.gbNaturalPersonDocument)
        self.gridLayout_14.setObjectName(_fromUtf8("gridLayout_14"))
        self.edtDocumentNumber = QtGui.QLineEdit(self.gbNaturalPersonDocument)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtDocumentNumber.sizePolicy().hasHeightForWidth())
        self.edtDocumentNumber.setSizePolicy(sizePolicy)
        self.edtDocumentNumber.setMaximumSize(QtCore.QSize(96, 16777215))
        self.edtDocumentNumber.setObjectName(_fromUtf8("edtDocumentNumber"))
        self.gridLayout_14.addWidget(self.edtDocumentNumber, 0, 3, 1, 1)
        self.cmbDocumentType = QtGui.QComboBox(self.gbNaturalPersonDocument)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbDocumentType.sizePolicy().hasHeightForWidth())
        self.cmbDocumentType.setSizePolicy(sizePolicy)
        self.cmbDocumentType.setObjectName(_fromUtf8("cmbDocumentType"))
        self.gridLayout_14.addWidget(self.cmbDocumentType, 0, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lblDocumentIssued = QtGui.QLabel(self.gbNaturalPersonDocument)
        self.lblDocumentIssued.setObjectName(_fromUtf8("lblDocumentIssued"))
        self.horizontalLayout.addWidget(self.lblDocumentIssued)
        self.edtDocumentIssuedDate = QtGui.QDateEdit(self.gbNaturalPersonDocument)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtDocumentIssuedDate.sizePolicy().hasHeightForWidth())
        self.edtDocumentIssuedDate.setSizePolicy(sizePolicy)
        self.edtDocumentIssuedDate.setObjectName(_fromUtf8("edtDocumentIssuedDate"))
        self.horizontalLayout.addWidget(self.edtDocumentIssuedDate)
        self.edtDocumentIssued = QtGui.QLineEdit(self.gbNaturalPersonDocument)
        self.edtDocumentIssued.setObjectName(_fromUtf8("edtDocumentIssued"))
        self.horizontalLayout.addWidget(self.edtDocumentIssued)
        self.gridLayout_14.addLayout(self.horizontalLayout, 1, 0, 1, 4)
        self.edtDocumentSerial = QtGui.QLineEdit(self.gbNaturalPersonDocument)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtDocumentSerial.sizePolicy().hasHeightForWidth())
        self.edtDocumentSerial.setSizePolicy(sizePolicy)
        self.edtDocumentSerial.setMaximumSize(QtCore.QSize(64, 16777215))
        self.edtDocumentSerial.setObjectName(_fromUtf8("edtDocumentSerial"))
        self.gridLayout_14.addWidget(self.edtDocumentSerial, 0, 1, 1, 2)
        self.gridLayout.addWidget(self.gbNaturalPersonDocument, 2, 0, 1, 3)
        self.lblPersonINN = QtGui.QLabel(OperationInfoDialog)
        self.lblPersonINN.setObjectName(_fromUtf8("lblPersonINN"))
        self.gridLayout.addWidget(self.lblPersonINN, 3, 0, 1, 1)
        self.edtPersonINN = QtGui.QLineEdit(OperationInfoDialog)
        self.edtPersonINN.setObjectName(_fromUtf8("edtPersonINN"))
        self.gridLayout.addWidget(self.edtPersonINN, 3, 1, 1, 2)
        self.lblSubstructure = QtGui.QLabel(OperationInfoDialog)
        self.lblSubstructure.setObjectName(_fromUtf8("lblSubstructure"))
        self.gridLayout.addWidget(self.lblSubstructure, 4, 0, 1, 1)
        self.edtSubstructure = QtGui.QLineEdit(OperationInfoDialog)
        self.edtSubstructure.setObjectName(_fromUtf8("edtSubstructure"))
        self.gridLayout.addWidget(self.edtSubstructure, 4, 1, 1, 2)
        self.lblOperationType = QtGui.QLabel(OperationInfoDialog)
        self.lblOperationType.setObjectName(_fromUtf8("lblOperationType"))
        self.gridLayout.addWidget(self.lblOperationType, 5, 0, 1, 1)
        self.cmbOperationType = QtGui.QComboBox(OperationInfoDialog)
        self.cmbOperationType.setEditable(True)
        self.cmbOperationType.setObjectName(_fromUtf8("cmbOperationType"))
        self.gridLayout.addWidget(self.cmbOperationType, 5, 1, 1, 2)
        self.lblCashFlowArticle = QtGui.QLabel(OperationInfoDialog)
        self.lblCashFlowArticle.setObjectName(_fromUtf8("lblCashFlowArticle"))
        self.gridLayout.addWidget(self.lblCashFlowArticle, 6, 0, 1, 3)
        self.edtCashFlowArticle = QtGui.QLineEdit(OperationInfoDialog)
        self.edtCashFlowArticle.setEnabled(True)
        self.edtCashFlowArticle.setObjectName(_fromUtf8("edtCashFlowArticle"))
        self.gridLayout.addWidget(self.edtCashFlowArticle, 7, 0, 1, 3)
        self.buttonBox = QtGui.QDialogButtonBox(OperationInfoDialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 8, 2, 1, 1)

        self.retranslateUi(OperationInfoDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), OperationInfoDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), OperationInfoDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(OperationInfoDialog)

    def retranslateUi(self, OperationInfoDialog):
        OperationInfoDialog.setWindowTitle(_translate("OperationInfoDialog", "Dialog", None))
        self.lblPersonName.setText(_translate("OperationInfoDialog", "Получатель/Плательщик:", None))
        self.edtPersonName.setToolTip(_translate("OperationInfoDialog", "<html><head/><body><p>Имя/Наименование лица (физического/юридического), производящего оплату товаров/услуг или получающего денежные средства.</p></body></html>", None))
        self.gbNaturalPersonDocument.setToolTip(_translate("OperationInfoDialog", "<html><head/><body><p>Указывает, что контрагент является физическим лицом.</p><p>Позволяет указать данные о документе контрагента, удостоверяющем его личность.</p></body></html>", None))
        self.gbNaturalPersonDocument.setTitle(_translate("OperationInfoDialog", "Физ. лицо. Документ:", None))
        self.edtDocumentNumber.setToolTip(_translate("OperationInfoDialog", "<html><head/><body><p>Номер документа, удостоверяющего личность.</p></body></html>", None))
        self.cmbDocumentType.setToolTip(_translate("OperationInfoDialog", "<html><head/><body><p>Тип документа, удостоверяющего личность.</p></body></html>", None))
        self.lblDocumentIssued.setText(_translate("OperationInfoDialog", "Выдан", None))
        self.edtDocumentIssuedDate.setToolTip(_translate("OperationInfoDialog", "<html><head/><body><p>Дата выдачи документа, удостоверяющего личность.</p></body></html>", None))
        self.edtDocumentIssued.setToolTip(_translate("OperationInfoDialog", "<html><head/><body><p>Организация, выдавшая документ, удостоверяющий личность.</p></body></html>", None))
        self.edtDocumentSerial.setToolTip(_translate("OperationInfoDialog", "<html><head/><body><p>Серия документа, удостоверяющего личность</p></body></html>", None))
        self.lblPersonINN.setText(_translate("OperationInfoDialog", "ИНН/КПП контрагента:", None))
        self.edtPersonINN.setToolTip(_translate("OperationInfoDialog", "<html><head/><body><p>Индивидуальный номер налогоплательщика(ИНН) и, если есть, код причины постановки на учет (КПП).</p></body></html>", None))
        self.lblSubstructure.setText(_translate("OperationInfoDialog", "Подразделение:", None))
        self.edtSubstructure.setToolTip(_translate("OperationInfoDialog", "<html><head/><body><p>Подразделение, в рамках которого производилась кассовая операция.</p></body></html>", None))
        self.lblOperationType.setText(_translate("OperationInfoDialog", "Вид операции:", None))
        self.cmbOperationType.setToolTip(_translate("OperationInfoDialog", "<html><head/><body><p>Вид текущей операции по кассе. Список доступных вариантов можно задать через базу данных (справочник rbECROperationType)</p></body></html>", None))
        self.lblCashFlowArticle.setText(_translate("OperationInfoDialog", "Статья движения денежных средств:", None))
        self.edtCashFlowArticle.setToolTip(_translate("OperationInfoDialog", "<html><head/><body><p>Информация для бухгалтерского учета.</p></body></html>", None))

