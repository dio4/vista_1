# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\DataCheck\SchemaClean.ui'
#
# Created: Fri Jun 15 12:16:05 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_SchemaCleanDialog(object):
    def setupUi(self, SchemaCleanDialog):
        SchemaCleanDialog.setObjectName(_fromUtf8("SchemaCleanDialog"))
        SchemaCleanDialog.resize(426, 385)
        self.gridLayout = QtGui.QGridLayout(SchemaCleanDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.progressBar = CProgressBar(SchemaCleanDialog)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setTextVisible(True)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 0, 0, 1, 3)
        self.logBrowser = QtGui.QTextBrowser(SchemaCleanDialog)
        self.logBrowser.setObjectName(_fromUtf8("logBrowser"))
        self.gridLayout.addWidget(self.logBrowser, 1, 0, 1, 3)
        spacerItem = QtGui.QSpacerItem(253, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
        self.btnClean = QtGui.QPushButton(SchemaCleanDialog)
        self.btnClean.setObjectName(_fromUtf8("btnClean"))
        self.gridLayout.addWidget(self.btnClean, 2, 1, 1, 1)
        self.btnClose = QtGui.QPushButton(SchemaCleanDialog)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.gridLayout.addWidget(self.btnClose, 2, 2, 1, 1)

        self.retranslateUi(SchemaCleanDialog)
        QtCore.QMetaObject.connectSlotsByName(SchemaCleanDialog)

    def retranslateUi(self, SchemaCleanDialog):
        SchemaCleanDialog.setWindowTitle(QtGui.QApplication.translate("SchemaCleanDialog", "Очистка записей, помеченных на удаление", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClean.setText(QtGui.QApplication.translate("SchemaCleanDialog", "Очистка", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("SchemaCleanDialog", "Закрыть", None, QtGui.QApplication.UnicodeUTF8))

from library.ProgressBar import CProgressBar

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    SchemaCleanDialog = QtGui.QDialog()
    ui = Ui_SchemaCleanDialog()
    ui.setupUi(SchemaCleanDialog)
    SchemaCleanDialog.show()
    sys.exit(app.exec_())

