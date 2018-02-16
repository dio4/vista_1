# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ImportServiceNomen.ui'
#
# Created: Fri Jun 15 12:16:35 2012
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
        Dialog.resize(543, 468)
        self.gridlayout = QtGui.QGridLayout(Dialog)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.hboxlayout.addWidget(self.label)
        self.splitter = QtGui.QSplitter(Dialog)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.edtFileName = QtGui.QLineEdit(self.splitter)
        self.edtFileName.setText(_fromUtf8(""))
        self.edtFileName.setReadOnly(False)
        self.edtFileName.setObjectName(_fromUtf8("edtFileName"))
        self.btnOpen = QtGui.QPushButton(self.splitter)
        self.btnOpen.setObjectName(_fromUtf8("btnOpen"))
        self.hboxlayout.addWidget(self.splitter)
        self.gridlayout.addLayout(self.hboxlayout, 0, 0, 1, 2)
        self.progressBar = CProgressBar(Dialog)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridlayout.addWidget(self.progressBar, 2, 0, 1, 2)
        self.statusLabel = QtGui.QLabel(Dialog)
        self.statusLabel.setText(_fromUtf8(""))
        self.statusLabel.setObjectName(_fromUtf8("statusLabel"))
        self.gridlayout.addWidget(self.statusLabel, 3, 0, 1, 2)
        self.log = QtGui.QTextBrowser(Dialog)
        self.log.setObjectName(_fromUtf8("log"))
        self.gridlayout.addWidget(self.log, 4, 0, 1, 2)
        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setObjectName(_fromUtf8("hboxlayout1"))
        self.btnImport = QtGui.QPushButton(Dialog)
        self.btnImport.setObjectName(_fromUtf8("btnImport"))
        self.hboxlayout1.addWidget(self.btnImport)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem)
        self.labelNum = QtGui.QLabel(Dialog)
        self.labelNum.setObjectName(_fromUtf8("labelNum"))
        self.hboxlayout1.addWidget(self.labelNum)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem1)
        self.btnClose = QtGui.QPushButton(Dialog)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.hboxlayout1.addWidget(self.btnClose)
        self.gridlayout.addLayout(self.hboxlayout1, 5, 0, 1, 2)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Загрузка услуг из номенкулатуры", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "импортировать из каталога", None, QtGui.QApplication.UnicodeUTF8))
        self.btnOpen.setText(QtGui.QApplication.translate("Dialog", "Выбрать...", None, QtGui.QApplication.UnicodeUTF8))
        self.btnImport.setText(QtGui.QApplication.translate("Dialog", "начать импортирование", None, QtGui.QApplication.UnicodeUTF8))
        self.labelNum.setText(QtGui.QApplication.translate("Dialog", "всего записей в источнике:", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("Dialog", "закрыть", None, QtGui.QApplication.UnicodeUTF8))

from library.ProgressBar import CProgressBar

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

