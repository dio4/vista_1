# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ExportRbService_Wizard_2.ui'
#
# Created: Fri Jun 15 12:16:07 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ExportRbService_Wizard_2(object):
    def setupUi(self, ExportRbService_Wizard_2):
        ExportRbService_Wizard_2.setObjectName(_fromUtf8("ExportRbService_Wizard_2"))
        ExportRbService_Wizard_2.resize(400, 271)
        self.gridlayout = QtGui.QGridLayout(ExportRbService_Wizard_2)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.label = QtGui.QLabel(ExportRbService_Wizard_2)
        self.label.setObjectName(_fromUtf8("label"))
        self.hboxlayout.addWidget(self.label)
        self.edtFileName = QtGui.QLineEdit(ExportRbService_Wizard_2)
        self.edtFileName.setObjectName(_fromUtf8("edtFileName"))
        self.hboxlayout.addWidget(self.edtFileName)
        self.btnSelectFile = QtGui.QToolButton(ExportRbService_Wizard_2)
        self.btnSelectFile.setObjectName(_fromUtf8("btnSelectFile"))
        self.hboxlayout.addWidget(self.btnSelectFile)
        self.gridlayout.addLayout(self.hboxlayout, 0, 0, 1, 1)
        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setObjectName(_fromUtf8("hboxlayout1"))
        self.gridlayout.addLayout(self.hboxlayout1, 2, 0, 1, 1)
        self.progressBar = CProgressBar(ExportRbService_Wizard_2)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridlayout.addWidget(self.progressBar, 4, 0, 1, 1)
        self.stat = QtGui.QLabel(ExportRbService_Wizard_2)
        self.stat.setText(_fromUtf8(""))
        self.stat.setObjectName(_fromUtf8("stat"))
        self.gridlayout.addWidget(self.stat, 5, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 6, 0, 1, 1)
        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setSpacing(6)
        self.hboxlayout2.setMargin(0)
        self.hboxlayout2.setObjectName(_fromUtf8("hboxlayout2"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout2.addItem(spacerItem1)
        self.btnExport = QtGui.QPushButton(ExportRbService_Wizard_2)
        self.btnExport.setEnabled(False)
        self.btnExport.setObjectName(_fromUtf8("btnExport"))
        self.hboxlayout2.addWidget(self.btnExport)
        self.gridlayout.addLayout(self.hboxlayout2, 7, 0, 1, 1)
        self.checkRAR = QtGui.QCheckBox(ExportRbService_Wizard_2)
        self.checkRAR.setCheckable(True)
        self.checkRAR.setObjectName(_fromUtf8("checkRAR"))
        self.gridlayout.addWidget(self.checkRAR, 1, 0, 1, 1)

        self.retranslateUi(ExportRbService_Wizard_2)
        QtCore.QMetaObject.connectSlotsByName(ExportRbService_Wizard_2)
        ExportRbService_Wizard_2.setTabOrder(self.edtFileName, self.btnSelectFile)
        ExportRbService_Wizard_2.setTabOrder(self.btnSelectFile, self.checkRAR)
        ExportRbService_Wizard_2.setTabOrder(self.checkRAR, self.btnExport)

    def retranslateUi(self, ExportRbService_Wizard_2):
        ExportRbService_Wizard_2.setWindowTitle(QtGui.QApplication.translate("ExportRbService_Wizard_2", "Экспорт типов действий", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ExportRbService_Wizard_2", "Экспортировать в", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectFile.setText(QtGui.QApplication.translate("ExportRbService_Wizard_2", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.btnExport.setText(QtGui.QApplication.translate("ExportRbService_Wizard_2", "Начать экспорт", None, QtGui.QApplication.UnicodeUTF8))
        self.checkRAR.setText(QtGui.QApplication.translate("ExportRbService_Wizard_2", "Архивировать rar", None, QtGui.QApplication.UnicodeUTF8))

from library.ProgressBar import CProgressBar

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ExportRbService_Wizard_2 = QtGui.QDialog()
    ui = Ui_ExportRbService_Wizard_2()
    ui.setupUi(ExportRbService_Wizard_2)
    ExportRbService_Wizard_2.show()
    sys.exit(app.exec_())

