# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ImportLgot.ui'
#
# Created: Fri Jun 15 12:15:20 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(651, 580)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.progressBar = QtGui.QProgressBar(Dialog)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 1, 0, 1, 1)
        self.statusLabel = QtGui.QLabel(Dialog)
        self.statusLabel.setText(_fromUtf8(""))
        self.statusLabel.setObjectName(_fromUtf8("statusLabel"))
        self.gridLayout.addWidget(self.statusLabel, 2, 0, 1, 1)
        self.log = QtGui.QTextBrowser(Dialog)
        self.log.setObjectName(_fromUtf8("log"))
        self.gridLayout.addWidget(self.log, 3, 0, 1, 1)
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.btnImport = QtGui.QPushButton(Dialog)
        self.btnImport.setObjectName(_fromUtf8("btnImport"))
        self.hboxlayout.addWidget(self.btnImport)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.labelNum = QtGui.QLabel(Dialog)
        self.labelNum.setObjectName(_fromUtf8("labelNum"))
        self.hboxlayout.addWidget(self.labelNum)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem1)
        self.btnClose = QtGui.QPushButton(Dialog)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.hboxlayout.addWidget(self.btnClose)
        self.gridLayout.addLayout(self.hboxlayout, 4, 0, 1, 1)
        self.tabExportType = QtGui.QTabWidget(Dialog)
        self.tabExportType.setObjectName(_fromUtf8("tabExportType"))
        self.EMSRN = QtGui.QWidget()
        self.EMSRN.setObjectName(_fromUtf8("EMSRN"))
        self.verticalLayout = QtGui.QVBoxLayout(self.EMSRN)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setObjectName(_fromUtf8("hboxlayout1"))
        self.label = QtGui.QLabel(self.EMSRN)
        self.label.setObjectName(_fromUtf8("label"))
        self.hboxlayout1.addWidget(self.label)
        self.edtFileName = QtGui.QLineEdit(self.EMSRN)
        self.edtFileName.setText(_fromUtf8(""))
        self.edtFileName.setObjectName(_fromUtf8("edtFileName"))
        self.hboxlayout1.addWidget(self.edtFileName)
        self.btnSelectFile = QtGui.QToolButton(self.EMSRN)
        self.btnSelectFile.setObjectName(_fromUtf8("btnSelectFile"))
        self.hboxlayout1.addWidget(self.btnSelectFile)
        self.btnView = QtGui.QPushButton(self.EMSRN)
        self.btnView.setObjectName(_fromUtf8("btnView"))
        self.hboxlayout1.addWidget(self.btnView)
        self.verticalLayout.addLayout(self.hboxlayout1)
        self.chkAdr = QtGui.QCheckBox(self.EMSRN)
        self.chkAdr.setEnabled(False)
        self.chkAdr.setObjectName(_fromUtf8("chkAdr"))
        self.verticalLayout.addWidget(self.chkAdr)
        self.chkDoc = QtGui.QCheckBox(self.EMSRN)
        self.chkDoc.setObjectName(_fromUtf8("chkDoc"))
        self.verticalLayout.addWidget(self.chkDoc)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.tabExportType.addTab(self.EMSRN, _fromUtf8(""))
        self.FSS = QtGui.QWidget()
        self.FSS.setObjectName(_fromUtf8("FSS"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.FSS)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.lblPersonalDataFileName = QtGui.QLabel(self.FSS)
        self.lblPersonalDataFileName.setObjectName(_fromUtf8("lblPersonalDataFileName"))
        self.gridLayout_2.addWidget(self.lblPersonalDataFileName, 0, 0, 1, 1)
        self.edtPersonalDataFileName = QtGui.QLineEdit(self.FSS)
        self.edtPersonalDataFileName.setObjectName(_fromUtf8("edtPersonalDataFileName"))
        self.gridLayout_2.addWidget(self.edtPersonalDataFileName, 0, 1, 1, 1)
        self.btnSelectPersonalDataFile = QtGui.QToolButton(self.FSS)
        self.btnSelectPersonalDataFile.setObjectName(_fromUtf8("btnSelectPersonalDataFile"))
        self.gridLayout_2.addWidget(self.btnSelectPersonalDataFile, 0, 2, 1, 1)
        self.btnViewPersonalDataFile = QtGui.QPushButton(self.FSS)
        self.btnViewPersonalDataFile.setObjectName(_fromUtf8("btnViewPersonalDataFile"))
        self.gridLayout_2.addWidget(self.btnViewPersonalDataFile, 0, 3, 1, 1)
        self.lblDocumentDataFileName = QtGui.QLabel(self.FSS)
        self.lblDocumentDataFileName.setObjectName(_fromUtf8("lblDocumentDataFileName"))
        self.gridLayout_2.addWidget(self.lblDocumentDataFileName, 1, 0, 1, 1)
        self.edtDocumentDataFileName = QtGui.QLineEdit(self.FSS)
        self.edtDocumentDataFileName.setObjectName(_fromUtf8("edtDocumentDataFileName"))
        self.gridLayout_2.addWidget(self.edtDocumentDataFileName, 1, 1, 1, 1)
        self.btnSelectDocumentDataFile = QtGui.QToolButton(self.FSS)
        self.btnSelectDocumentDataFile.setObjectName(_fromUtf8("btnSelectDocumentDataFile"))
        self.gridLayout_2.addWidget(self.btnSelectDocumentDataFile, 1, 2, 1, 1)
        self.btnViewDocumentDataFile = QtGui.QPushButton(self.FSS)
        self.btnViewDocumentDataFile.setObjectName(_fromUtf8("btnViewDocumentDataFile"))
        self.gridLayout_2.addWidget(self.btnViewDocumentDataFile, 1, 3, 1, 1)
        self.verticalLayout_3.addLayout(self.gridLayout_2)
        self.gbBenefitType = QtGui.QGroupBox(self.FSS)
        self.gbBenefitType.setObjectName(_fromUtf8("gbBenefitType"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.gbBenefitType)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.chkFederalBenefit = QtGui.QRadioButton(self.gbBenefitType)
        self.chkFederalBenefit.setChecked(True)
        self.chkFederalBenefit.setObjectName(_fromUtf8("chkFederalBenefit"))
        self.verticalLayout_2.addWidget(self.chkFederalBenefit)
        self.chkRegionalBenefit = QtGui.QRadioButton(self.gbBenefitType)
        self.chkRegionalBenefit.setObjectName(_fromUtf8("chkRegionalBenefit"))
        self.verticalLayout_2.addWidget(self.chkRegionalBenefit)
        self.verticalLayout_3.addWidget(self.gbBenefitType)
        self.chkAddMissingClients = QtGui.QCheckBox(self.FSS)
        self.chkAddMissingClients.setObjectName(_fromUtf8("chkAddMissingClients"))
        self.verticalLayout_3.addWidget(self.chkAddMissingClients)
        self.chkAddDocumentType = QtGui.QCheckBox(self.FSS)
        self.chkAddDocumentType.setObjectName(_fromUtf8("chkAddDocumentType"))
        self.verticalLayout_3.addWidget(self.chkAddDocumentType)
        spacerItem3 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem3)
        self.tabExportType.addTab(self.FSS, _fromUtf8(""))
        self.gridLayout.addWidget(self.tabExportType, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        self.tabExportType.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Импорт льготников", None, QtGui.QApplication.UnicodeUTF8))
        self.btnImport.setText(QtGui.QApplication.translate("Dialog", "начать импортирование", None, QtGui.QApplication.UnicodeUTF8))
        self.labelNum.setText(QtGui.QApplication.translate("Dialog", "всего записей в источнике:", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("Dialog", "закрыть", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "импортировать из", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectFile.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.btnView.setText(QtGui.QApplication.translate("Dialog", "Просмотреть", None, QtGui.QApplication.UnicodeUTF8))
        self.chkAdr.setText(QtGui.QApplication.translate("Dialog", "загружать адреса", None, QtGui.QApplication.UnicodeUTF8))
        self.chkDoc.setText(QtGui.QApplication.translate("Dialog", "сообщать о неправильных паспортах", None, QtGui.QApplication.UnicodeUTF8))
        self.tabExportType.setTabText(self.tabExportType.indexOf(self.EMSRN), QtGui.QApplication.translate("Dialog", "ЭМСРН", None, QtGui.QApplication.UnicodeUTF8))
        self.lblPersonalDataFileName.setText(QtGui.QApplication.translate("Dialog", "Файл с персональными данными", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectPersonalDataFile.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.btnViewPersonalDataFile.setText(QtGui.QApplication.translate("Dialog", "Просмотреть", None, QtGui.QApplication.UnicodeUTF8))
        self.lblDocumentDataFileName.setText(QtGui.QApplication.translate("Dialog", "Файл с данными о документах", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectDocumentDataFile.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.btnViewDocumentDataFile.setText(QtGui.QApplication.translate("Dialog", "Просмотреть", None, QtGui.QApplication.UnicodeUTF8))
        self.gbBenefitType.setTitle(QtGui.QApplication.translate("Dialog", "Тип льготы", None, QtGui.QApplication.UnicodeUTF8))
        self.chkFederalBenefit.setText(QtGui.QApplication.translate("Dialog", "федеральная", None, QtGui.QApplication.UnicodeUTF8))
        self.chkRegionalBenefit.setText(QtGui.QApplication.translate("Dialog", "региональная", None, QtGui.QApplication.UnicodeUTF8))
        self.chkAddMissingClients.setText(QtGui.QApplication.translate("Dialog", "Выполнять регистрацию новых пациентов", None, QtGui.QApplication.UnicodeUTF8))
        self.chkAddDocumentType.setToolTip(QtGui.QApplication.translate("Dialog", "Добавлять новые типы документов в БД", None, QtGui.QApplication.UnicodeUTF8))
        self.chkAddDocumentType.setText(QtGui.QApplication.translate("Dialog", "Добавлять тип документа", None, QtGui.QApplication.UnicodeUTF8))
        self.tabExportType.setTabText(self.tabExportType.indexOf(self.FSS), QtGui.QApplication.translate("Dialog", "ФСС", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
