# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ImportEISOMSPage1.ui'
#
# Created: Fri Jun 15 12:15:18 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ImportEISOMSPage1(object):
    def setupUi(self, ImportEISOMSPage1):
        ImportEISOMSPage1.setObjectName(_fromUtf8("ImportEISOMSPage1"))
        ImportEISOMSPage1.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(ImportEISOMSPage1)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lblFileName = QtGui.QLabel(ImportEISOMSPage1)
        self.lblFileName.setObjectName(_fromUtf8("lblFileName"))
        self.horizontalLayout.addWidget(self.lblFileName)
        self.edtFileName = QtGui.QLineEdit(ImportEISOMSPage1)
        self.edtFileName.setObjectName(_fromUtf8("edtFileName"))
        self.horizontalLayout.addWidget(self.edtFileName)
        self.btnSelectFile = QtGui.QToolButton(ImportEISOMSPage1)
        self.btnSelectFile.setObjectName(_fromUtf8("btnSelectFile"))
        self.horizontalLayout.addWidget(self.btnSelectFile)
        self.btnView = QtGui.QPushButton(ImportEISOMSPage1)
        self.btnView.setObjectName(_fromUtf8("btnView"))
        self.horizontalLayout.addWidget(self.btnView)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 2)
        self.chkImportAfterSMOCheck = QtGui.QCheckBox(ImportEISOMSPage1)
        self.chkImportAfterSMOCheck.setObjectName(_fromUtf8("chkImportAfterSMOCheck"))
        self.gridLayout.addWidget(self.chkImportAfterSMOCheck, 1, 1, 1, 1)
        self.chkRemoveFileAfterImport = QtGui.QCheckBox(ImportEISOMSPage1)
        self.chkRemoveFileAfterImport.setObjectName(_fromUtf8("chkRemoveFileAfterImport"))
        self.gridLayout.addWidget(self.chkRemoveFileAfterImport, 2, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 251, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 1)

        self.retranslateUi(ImportEISOMSPage1)
        QtCore.QMetaObject.connectSlotsByName(ImportEISOMSPage1)

    def retranslateUi(self, ImportEISOMSPage1):
        ImportEISOMSPage1.setWindowTitle(QtGui.QApplication.translate("ImportEISOMSPage1", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.lblFileName.setText(QtGui.QApplication.translate("ImportEISOMSPage1", "Выберите файл", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectFile.setText(QtGui.QApplication.translate("ImportEISOMSPage1", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.btnView.setText(QtGui.QApplication.translate("ImportEISOMSPage1", "Просмотреть", None, QtGui.QApplication.UnicodeUTF8))
        self.chkImportAfterSMOCheck.setText(QtGui.QApplication.translate("ImportEISOMSPage1", "Импорт данных контроля СМО", None, QtGui.QApplication.UnicodeUTF8))
        self.chkRemoveFileAfterImport.setText(QtGui.QApplication.translate("ImportEISOMSPage1", "Удалить файл после успешного импорта", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ImportEISOMSPage1 = QtGui.QWidget()
    ui = Ui_ImportEISOMSPage1()
    ui.setupUi(ImportEISOMSPage1)
    ImportEISOMSPage1.show()
    sys.exit(app.exec_())

