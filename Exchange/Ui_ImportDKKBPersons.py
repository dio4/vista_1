# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ImportDKKBPersons.ui'
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

class Ui_ImportDKKBPersonsDialog(object):
    def setupUi(self, ImportDKKBPersonsDialog):
        ImportDKKBPersonsDialog.setObjectName(_fromUtf8("ImportDKKBPersonsDialog"))
        ImportDKKBPersonsDialog.resize(484, 390)
        ImportDKKBPersonsDialog.setMinimumSize(QtCore.QSize(450, 350))
        self.verticalLayout = QtGui.QVBoxLayout(ImportDKKBPersonsDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.groupBox = QtGui.QGroupBox(ImportDKKBPersonsDialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.formLayout_2 = QtGui.QFormLayout(self.groupBox)
        self.formLayout_2.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.formLayout_2.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.chkCurrent = QtGui.QCheckBox(self.groupBox)
        self.chkCurrent.setChecked(True)
        self.chkCurrent.setObjectName(_fromUtf8("chkCurrent"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.SpanningRole, self.chkCurrent)
        spacerItem = QtGui.QSpacerItem(20, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.formLayout_2.setItem(3, QtGui.QFormLayout.FieldRole, spacerItem)
        self.lblDateCurrent = QtGui.QLabel(self.groupBox)
        self.lblDateCurrent.setObjectName(_fromUtf8("lblDateCurrent"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.LabelRole, self.lblDateCurrent)
        self.edtDateCurrent = CDateEdit(self.groupBox)
        self.edtDateCurrent.setObjectName(_fromUtf8("edtDateCurrent"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.FieldRole, self.edtDateCurrent)
        self.horizontalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(ImportDKKBPersonsDialog)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.formLayout_3 = QtGui.QFormLayout(self.groupBox_2)
        self.formLayout_3.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_3.setObjectName(_fromUtf8("formLayout_3"))
        self.chkRetired = QtGui.QCheckBox(self.groupBox_2)
        self.chkRetired.setChecked(True)
        self.chkRetired.setObjectName(_fromUtf8("chkRetired"))
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.SpanningRole, self.chkRetired)
        self.lblRetiredStart = QtGui.QLabel(self.groupBox_2)
        self.lblRetiredStart.setObjectName(_fromUtf8("lblRetiredStart"))
        self.formLayout_3.setWidget(1, QtGui.QFormLayout.LabelRole, self.lblRetiredStart)
        self.lblRetiredEnd = QtGui.QLabel(self.groupBox_2)
        self.lblRetiredEnd.setObjectName(_fromUtf8("lblRetiredEnd"))
        self.formLayout_3.setWidget(2, QtGui.QFormLayout.LabelRole, self.lblRetiredEnd)
        self.edtRetiredStart = CDateEdit(self.groupBox_2)
        self.edtRetiredStart.setObjectName(_fromUtf8("edtRetiredStart"))
        self.formLayout_3.setWidget(1, QtGui.QFormLayout.FieldRole, self.edtRetiredStart)
        self.edtRetiredEnd = CDateEdit(self.groupBox_2)
        self.edtRetiredEnd.setObjectName(_fromUtf8("edtRetiredEnd"))
        self.formLayout_3.setWidget(2, QtGui.QFormLayout.FieldRole, self.edtRetiredEnd)
        self.horizontalLayout.addWidget(self.groupBox_2)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.txtLog = QtGui.QTextEdit(ImportDKKBPersonsDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.txtLog.sizePolicy().hasHeightForWidth())
        self.txtLog.setSizePolicy(sizePolicy)
        self.txtLog.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse)
        self.txtLog.setObjectName(_fromUtf8("txtLog"))
        self.verticalLayout.addWidget(self.txtLog)
        self.progressBar = QtGui.QProgressBar(ImportDKKBPersonsDialog)
        self.progressBar.setEnabled(True)
        self.progressBar.setMaximum(100)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setTextVisible(False)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.verticalLayout.addWidget(self.progressBar)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.btnReport = QtGui.QPushButton(ImportDKKBPersonsDialog)
        self.btnReport.setEnabled(False)
        self.btnReport.setObjectName(_fromUtf8("btnReport"))
        self.horizontalLayout_3.addWidget(self.btnReport)
        self.btnStart = QtGui.QPushButton(ImportDKKBPersonsDialog)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("media-playback-start"))
        self.btnStart.setIcon(icon)
        self.btnStart.setDefault(True)
        self.btnStart.setObjectName(_fromUtf8("btnStart"))
        self.horizontalLayout_3.addWidget(self.btnStart)
        self.btnStop = QtGui.QPushButton(ImportDKKBPersonsDialog)
        self.btnStop.setEnabled(False)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("media-playback-stop"))
        self.btnStop.setIcon(icon)
        self.btnStop.setObjectName(_fromUtf8("btnStop"))
        self.horizontalLayout_3.addWidget(self.btnStop)
        self.btnClose = QtGui.QPushButton(ImportDKKBPersonsDialog)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("window-close"))
        self.btnClose.setIcon(icon)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.horizontalLayout_3.addWidget(self.btnClose)
        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.retranslateUi(ImportDKKBPersonsDialog)
        QtCore.QObject.connect(self.chkCurrent, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.lblDateCurrent.setEnabled)
        QtCore.QObject.connect(self.chkRetired, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.lblRetiredStart.setEnabled)
        QtCore.QObject.connect(self.chkRetired, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.lblRetiredEnd.setEnabled)
        QtCore.QObject.connect(self.chkCurrent, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtDateCurrent.setEnabled)
        QtCore.QObject.connect(self.chkRetired, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtRetiredStart.setEnabled)
        QtCore.QObject.connect(self.chkRetired, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtRetiredEnd.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(ImportDKKBPersonsDialog)

    def retranslateUi(self, ImportDKKBPersonsDialog):
        ImportDKKBPersonsDialog.setWindowTitle(_translate("ImportDKKBPersonsDialog", "Синхронизация с 1С-Кадры", None))
        self.groupBox.setTitle(_translate("ImportDKKBPersonsDialog", "Текущие сотрудники", None))
        self.chkCurrent.setText(_translate("ImportDKKBPersonsDialog", "Синхронизировать", None))
        self.lblDateCurrent.setText(_translate("ImportDKKBPersonsDialog", "Дата", None))
        self.groupBox_2.setTitle(_translate("ImportDKKBPersonsDialog", "Уволенные сотрудники", None))
        self.chkRetired.setText(_translate("ImportDKKBPersonsDialog", "Синхронизировать", None))
        self.lblRetiredStart.setText(_translate("ImportDKKBPersonsDialog", "С", None))
        self.lblRetiredEnd.setText(_translate("ImportDKKBPersonsDialog", "По", None))
        self.progressBar.setFormat(_translate("ImportDKKBPersonsDialog", "%v/%m", None))
        self.btnReport.setText(_translate("ImportDKKBPersonsDialog", "Сохранить отчет", None))
        self.btnStart.setText(_translate("ImportDKKBPersonsDialog", "Старт", None))
        self.btnStop.setText(_translate("ImportDKKBPersonsDialog", "Стоп", None))
        self.btnClose.setText(_translate("ImportDKKBPersonsDialog", "Закрыть", None))

from library.DateEdit import CDateEdit
