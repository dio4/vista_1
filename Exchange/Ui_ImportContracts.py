# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\py\s11-svn\Exchange\ImportContracts.ui'
#
# Created: Thu Dec 27 22:51:00 2007
#      by: PyQt4 UI code generator 4.3-snapshot-20071116
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(QtCore.QSize(QtCore.QRect(0,0,543,468).size()).expandedTo(Dialog.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(Dialog)
        self.gridlayout.setObjectName("gridlayout")

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setObjectName("hboxlayout")

        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName("label")
        self.hboxlayout.addWidget(self.label)

        self.splitter = QtGui.QSplitter(Dialog)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")

        self.edtFileName = QtGui.QLineEdit(self.splitter)
        self.edtFileName.setReadOnly(True)
        self.edtFileName.setObjectName("edtFileName")

        self.edtIP = QtGui.QLineEdit(self.splitter)
        self.edtIP.setReadOnly(True)
        self.edtIP.setObjectName("edtIP")
        self.hboxlayout.addWidget(self.splitter)
        self.gridlayout.addLayout(self.hboxlayout,0,0,1,2)

        self.progressBar = QtGui.QProgressBar(Dialog)
        self.progressBar.setProperty("value",QtCore.QVariant(24))
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName("progressBar")
        self.gridlayout.addWidget(self.progressBar,2,0,1,2)

        self.statusLabel = QtGui.QLabel(Dialog)
        self.statusLabel.setObjectName("statusLabel")
        self.gridlayout.addWidget(self.statusLabel,3,0,1,2)

        self.log = QtGui.QTextBrowser(Dialog)
        self.log.setObjectName("log")
        self.gridlayout.addWidget(self.log,4,0,1,2)

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.btnImport = QtGui.QPushButton(Dialog)
        self.btnImport.setObjectName("btnImport")
        self.hboxlayout1.addWidget(self.btnImport)

        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem)

        self.labelNum = QtGui.QLabel(Dialog)
        self.labelNum.setObjectName("labelNum")
        self.hboxlayout1.addWidget(self.labelNum)

        spacerItem1 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem1)

        self.btnClose = QtGui.QPushButton(Dialog)
        self.btnClose.setObjectName("btnClose")
        self.hboxlayout1.addWidget(self.btnClose)
        self.gridlayout.addLayout(self.hboxlayout1,5,0,1,2)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Зазрузка тарифов из ЕИС", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "импортировать из", None, QtGui.QApplication.UnicodeUTF8))
        self.btnImport.setText(QtGui.QApplication.translate("Dialog", "начать импортирование", None, QtGui.QApplication.UnicodeUTF8))
        self.labelNum.setText(QtGui.QApplication.translate("Dialog", "всего записей в источнике:", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("Dialog", "закрыть", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
