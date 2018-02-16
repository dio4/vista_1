# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Timeline\DublDialog.ui'
#
# Created: Fri Jun 15 12:15:58 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_DublDialog(object):
    def setupUi(self, DublDialog):
        DublDialog.setObjectName(_fromUtf8("DublDialog"))
        DublDialog.resize(320, 218)
        self.gridLayout = QtGui.QGridLayout(DublDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.textBrowser = QtGui.QTextBrowser(DublDialog)
        self.textBrowser.setObjectName(_fromUtf8("textBrowser"))
        self.gridLayout.addWidget(self.textBrowser, 0, 0, 1, 3)
        self.chkStart = QtGui.QCheckBox(DublDialog)
        self.chkStart.setObjectName(_fromUtf8("chkStart"))
        self.gridLayout.addWidget(self.chkStart, 1, 0, 1, 1)
        self.edtStart = CDateEdit(DublDialog)
        self.edtStart.setEnabled(False)
        self.edtStart.setObjectName(_fromUtf8("edtStart"))
        self.gridLayout.addWidget(self.edtStart, 1, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(134, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 2, 1, 1)
        self.groupBox = QtGui.QGroupBox(DublDialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setMargin(4)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.rbSingle = QtGui.QRadioButton(self.groupBox)
        self.rbSingle.setObjectName(_fromUtf8("rbSingle"))
        self.verticalLayout.addWidget(self.rbSingle)
        self.rbDual = QtGui.QRadioButton(self.groupBox)
        self.rbDual.setObjectName(_fromUtf8("rbDual"))
        self.verticalLayout.addWidget(self.rbDual)
        self.rbWeek = QtGui.QRadioButton(self.groupBox)
        self.rbWeek.setChecked(True)
        self.rbWeek.setObjectName(_fromUtf8("rbWeek"))
        self.verticalLayout.addWidget(self.rbWeek)
        self.gridLayout.addWidget(self.groupBox, 2, 0, 1, 3)
        self.buttonBox = QtGui.QDialogButtonBox(DublDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 3)

        self.retranslateUi(DublDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DublDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DublDialog.reject)
        QtCore.QObject.connect(self.chkStart, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.edtStart.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(DublDialog)
        DublDialog.setTabOrder(self.textBrowser, self.chkStart)
        DublDialog.setTabOrder(self.chkStart, self.edtStart)
        DublDialog.setTabOrder(self.edtStart, self.rbSingle)
        DublDialog.setTabOrder(self.rbSingle, self.rbDual)
        DublDialog.setTabOrder(self.rbDual, self.rbWeek)
        DublDialog.setTabOrder(self.rbWeek, self.buttonBox)

    def retranslateUi(self, DublDialog):
        DublDialog.setWindowTitle(QtGui.QApplication.translate("DublDialog", "Дублирование графика", None, QtGui.QApplication.UnicodeUTF8))
        self.textBrowser.setHtml(QtGui.QApplication.translate("DublDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\'; font-size:9pt;\">Выберите режим копирования для выполнения дублирования графика</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.chkStart.setText(QtGui.QApplication.translate("DublDialog", "начинать с", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("DublDialog", "режим копирования", None, QtGui.QApplication.UnicodeUTF8))
        self.rbSingle.setText(QtGui.QApplication.translate("DublDialog", "Один план", None, QtGui.QApplication.UnicodeUTF8))
        self.rbDual.setText(QtGui.QApplication.translate("DublDialog", "Нечет/чёт", None, QtGui.QApplication.UnicodeUTF8))
        self.rbWeek.setText(QtGui.QApplication.translate("DublDialog", "Неделя", None, QtGui.QApplication.UnicodeUTF8))

from library.DateEdit import CDateEdit

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    DublDialog = QtGui.QDialog()
    ui = Ui_DublDialog()
    ui.setupUi(DublDialog)
    DublDialog.show()
    sys.exit(app.exec_())

