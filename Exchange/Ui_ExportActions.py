# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\temp1\Exchange\ExportActions.ui'
#
# Created: Wed May 14 18:42:06 2008
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(QtCore.QSize(QtCore.QRect(0,0,400,271).size()).expandedTo(Dialog.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(Dialog)
        self.gridlayout.setObjectName("gridlayout")

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName("hboxlayout")

        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName("label")
        self.hboxlayout.addWidget(self.label)

        self.edtFileName = QtGui.QLineEdit(Dialog)
        self.edtFileName.setObjectName("edtFileName")
        self.hboxlayout.addWidget(self.edtFileName)

        self.btnSelectFile = QtGui.QToolButton(Dialog)
        self.btnSelectFile.setObjectName("btnSelectFile")
        self.hboxlayout.addWidget(self.btnSelectFile)
        self.gridlayout.addLayout(self.hboxlayout,0,0,1,1)

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setObjectName("hboxlayout1")
        self.gridlayout.addLayout(self.hboxlayout1,2,0,1,1)

        self.progressBar = CProgressBar(Dialog)
        self.progressBar.setProperty("value",QtCore.QVariant(24))
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName("progressBar")
        self.gridlayout.addWidget(self.progressBar,4,0,1,1)

        self.stat = QtGui.QLabel(Dialog)
        self.stat.setObjectName("stat")
        self.gridlayout.addWidget(self.stat,5,0,1,1)

        spacerItem = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem,6,0,1,1)

        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setSpacing(6)
        self.hboxlayout2.setMargin(0)
        self.hboxlayout2.setObjectName("hboxlayout2")

        self.btnExport = QtGui.QPushButton(Dialog)
        self.btnExport.setEnabled(False)
        self.btnExport.setObjectName("btnExport")
        self.hboxlayout2.addWidget(self.btnExport)

        spacerItem1 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout2.addItem(spacerItem1)
        self.gridlayout.addLayout(self.hboxlayout2,7,0,1,1)

        self.checkBox = QtGui.QCheckBox(Dialog)
        self.checkBox.setCheckable(False)
        self.checkBox.setObjectName("checkBox")
        self.gridlayout.addWidget(self.checkBox,1,0,1,1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Экспорт типов действий", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Экспортировать в", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectFile.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.btnExport.setText(QtGui.QApplication.translate("Dialog", "Начать экспорт", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setText(QtGui.QApplication.translate("Dialog", "Архивировать rar", None, QtGui.QApplication.UnicodeUTF8))

from library.ProgressBar import CProgressBar


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())