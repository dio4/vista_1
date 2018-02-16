# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ExportTariff_Wizard_2.ui'
#
# Created: Fri Jun 15 12:16:08 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ExportTariff_Wizard_2(object):
    def setupUi(self, ExportTariff_Wizard_2):
        ExportTariff_Wizard_2.setObjectName(_fromUtf8("ExportTariff_Wizard_2"))
        ExportTariff_Wizard_2.resize(400, 271)
        self.gridLayout = QtGui.QGridLayout(ExportTariff_Wizard_2)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lblFileName = QtGui.QLabel(ExportTariff_Wizard_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblFileName.sizePolicy().hasHeightForWidth())
        self.lblFileName.setSizePolicy(sizePolicy)
        self.lblFileName.setObjectName(_fromUtf8("lblFileName"))
        self.horizontalLayout.addWidget(self.lblFileName)
        self.edtFileName = QtGui.QLineEdit(ExportTariff_Wizard_2)
        self.edtFileName.setObjectName(_fromUtf8("edtFileName"))
        self.horizontalLayout.addWidget(self.edtFileName)
        self.btnSelectFile = QtGui.QToolButton(ExportTariff_Wizard_2)
        self.btnSelectFile.setObjectName(_fromUtf8("btnSelectFile"))
        self.horizontalLayout.addWidget(self.btnSelectFile)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 3)
        self.checkRAR = QtGui.QCheckBox(ExportTariff_Wizard_2)
        self.checkRAR.setCheckable(True)
        self.checkRAR.setObjectName(_fromUtf8("checkRAR"))
        self.gridLayout.addWidget(self.checkRAR, 1, 0, 1, 3)
        spacerItem = QtGui.QSpacerItem(397, 79, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 3)
        self.progressBar = CProgressBar(ExportTariff_Wizard_2)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 3, 0, 1, 3)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 4, 0, 1, 3)
        spacerItem2 = QtGui.QSpacerItem(278, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 5, 0, 1, 2)
        self.btnExport = QtGui.QPushButton(ExportTariff_Wizard_2)
        self.btnExport.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnExport.sizePolicy().hasHeightForWidth())
        self.btnExport.setSizePolicy(sizePolicy)
        self.btnExport.setObjectName(_fromUtf8("btnExport"))
        self.gridLayout.addWidget(self.btnExport, 5, 2, 1, 1)

        self.retranslateUi(ExportTariff_Wizard_2)
        QtCore.QMetaObject.connectSlotsByName(ExportTariff_Wizard_2)
        ExportTariff_Wizard_2.setTabOrder(self.edtFileName, self.btnSelectFile)
        ExportTariff_Wizard_2.setTabOrder(self.btnSelectFile, self.checkRAR)

    def retranslateUi(self, ExportTariff_Wizard_2):
        ExportTariff_Wizard_2.setWindowTitle(QtGui.QApplication.translate("ExportTariff_Wizard_2", "Выбор файла и процесс", None, QtGui.QApplication.UnicodeUTF8))
        self.lblFileName.setText(QtGui.QApplication.translate("ExportTariff_Wizard_2", "Экспортировать в", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectFile.setText(QtGui.QApplication.translate("ExportTariff_Wizard_2", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.checkRAR.setText(QtGui.QApplication.translate("ExportTariff_Wizard_2", "Архивировать rar", None, QtGui.QApplication.UnicodeUTF8))
        self.btnExport.setText(QtGui.QApplication.translate("ExportTariff_Wizard_2", "Начать экспорт", None, QtGui.QApplication.UnicodeUTF8))

from library.ProgressBar import CProgressBar

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ExportTariff_Wizard_2 = QtGui.QDialog()
    ui = Ui_ExportTariff_Wizard_2()
    ui.setupUi(ExportTariff_Wizard_2)
    ExportTariff_Wizard_2.show()
    sys.exit(app.exec_())

