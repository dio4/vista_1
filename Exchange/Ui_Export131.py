# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\py\s11-svn\Exchange\Export131.ui'
#
# Created: Mon Oct 01 21:36:29 2007
#      by: PyQt4 UI code generator 4.3-snapshot-20070921
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(QtCore.QSize(QtCore.QRect(0,0,400,300).size()).expandedTo(Form.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(Form)
        self.gridlayout.setObjectName("gridlayout")

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName("hboxlayout")

        self.label = QtGui.QLabel(Form)
        self.label.setObjectName("label")
        self.hboxlayout.addWidget(self.label)

        self.edtFileName = QtGui.QLineEdit(Form)
        self.edtFileName.setObjectName("edtFileName")
        self.hboxlayout.addWidget(self.edtFileName)

        self.btnSelectFile = QtGui.QToolButton(Form)
        self.btnSelectFile.setObjectName("btnSelectFile")
        self.hboxlayout.addWidget(self.btnSelectFile)
        self.gridlayout.addLayout(self.hboxlayout,0,0,1,1)

        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.setObjectName("vboxlayout")

        self.checkDate = QtGui.QCheckBox(Form)
        self.checkDate.setChecked(True)
        self.checkDate.setObjectName("checkDate")
        self.vboxlayout.addWidget(self.checkDate)

        self.checkFinished = QtGui.QCheckBox(Form)
        self.checkFinished.setChecked(True)
        self.checkFinished.setObjectName("checkFinished")
        self.vboxlayout.addWidget(self.checkFinished)

        self.checkPayed = QtGui.QCheckBox(Form)
        self.checkPayed.setEnabled(False)
        self.checkPayed.setObjectName("checkPayed")
        self.vboxlayout.addWidget(self.checkPayed)

        self.checkTIP_DD_R = QtGui.QCheckBox(Form)
        self.checkTIP_DD_R.setEnabled(False)
        self.checkTIP_DD_R.setObjectName("checkTIP_DD_R")
        self.vboxlayout.addWidget(self.checkTIP_DD_R)

        self.checkTIP_DD_V = QtGui.QCheckBox(Form)
        self.checkTIP_DD_V.setEnabled(False)
        self.checkTIP_DD_V.setObjectName("checkTIP_DD_V")
        self.vboxlayout.addWidget(self.checkTIP_DD_V)
        self.gridlayout.addLayout(self.vboxlayout,1,0,1,1)

        self.progressBar = QtGui.QProgressBar(Form)
        self.progressBar.setProperty("value",QtCore.QVariant(24))
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName("progressBar")
        self.gridlayout.addWidget(self.progressBar,2,0,1,1)

        spacerItem = QtGui.QSpacerItem(382,20,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem,3,0,1,1)

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.btnExport = QtGui.QPushButton(Form)
        self.btnExport.setObjectName("btnExport")
        self.hboxlayout1.addWidget(self.btnExport)

        spacerItem1 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem1)

        self.btnClose = QtGui.QPushButton(Form)
        self.btnClose.setObjectName("btnClose")
        self.hboxlayout1.addWidget(self.btnClose)
        self.gridlayout.addLayout(self.hboxlayout1,4,0,1,1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Экспорт формы 131", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "экспортировать в", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectFile.setText(QtGui.QApplication.translate("Form", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.checkDate.setText(QtGui.QApplication.translate("Form", "карточки только текущего года", None, QtGui.QApplication.UnicodeUTF8))
        self.checkFinished.setText(QtGui.QApplication.translate("Form", "только законченные", None, QtGui.QApplication.UnicodeUTF8))
        self.checkPayed.setText(QtGui.QApplication.translate("Form", "только оплаченные", None, QtGui.QApplication.UnicodeUTF8))
        self.checkTIP_DD_R.setText(QtGui.QApplication.translate("Form", "карточки типа Р (876)", None, QtGui.QApplication.UnicodeUTF8))
        self.checkTIP_DD_V.setText(QtGui.QApplication.translate("Form", "карточки с типа В (869/859)", None, QtGui.QApplication.UnicodeUTF8))
        self.btnExport.setText(QtGui.QApplication.translate("Form", "начать экспорт", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("Form", "закрыть", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
