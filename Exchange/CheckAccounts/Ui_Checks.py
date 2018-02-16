# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Checks.ui'
#
# Created: Mon May  5 07:13:49 2014
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Checks(object):
    def setupUi(self, Checks):
        Checks.setObjectName(_fromUtf8("Checks"))
        Checks.resize(500, 450)
        self.verticalLayout = QtGui.QVBoxLayout(Checks)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gbChecks = QtGui.QGroupBox(Checks)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gbChecks.sizePolicy().hasHeightForWidth())
        self.gbChecks.setSizePolicy(sizePolicy)
        self.gbChecks.setObjectName(_fromUtf8("gbChecks"))
        self.lMail = QtGui.QVBoxLayout(self.gbChecks)
        self.lMail.setObjectName(_fromUtf8("lMail"))
        self.lbChecks = QtGui.QLabel(self.gbChecks)
        self.lbChecks.setText(_fromUtf8(""))
        self.lbChecks.setWordWrap(True)
        self.lbChecks.setObjectName(_fromUtf8("lbChecks"))
        self.lMail.addWidget(self.lbChecks)
        self.pbChecks = QtGui.QProgressBar(self.gbChecks)
        self.pbChecks.setProperty("value", 0)
        self.pbChecks.setObjectName(_fromUtf8("pbChecks"))
        self.lMail.addWidget(self.pbChecks)
        self.tbChecks = QtGui.QTextBrowser(self.gbChecks)
        self.tbChecks.setObjectName(_fromUtf8("tbChecks"))
        self.lMail.addWidget(self.tbChecks)
        self.chkOnlyErrors = QtGui.QCheckBox(self.gbChecks)
        self.chkOnlyErrors.setObjectName(_fromUtf8("chkOnlyErrors"))
        self.lMail.addWidget(self.chkOnlyErrors)
        self.verticalLayout.addWidget(self.gbChecks)
        self.gbGroupReport = QtGui.QGroupBox(Checks)
        self.gbGroupReport.setObjectName(_fromUtf8("gbGroupReport"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.gbGroupReport)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.rbGroupByData = QtGui.QRadioButton(self.gbGroupReport)
        self.rbGroupByData.setChecked(True)
        self.rbGroupByData.setObjectName(_fromUtf8("rbGroupByData"))
        self.verticalLayout_2.addWidget(self.rbGroupByData)
        self.rbGroupByErrors = QtGui.QRadioButton(self.gbGroupReport)
        self.rbGroupByErrors.setObjectName(_fromUtf8("rbGroupByErrors"))
        self.verticalLayout_2.addWidget(self.rbGroupByErrors)
        self.chkGroupByDoctor = QtGui.QCheckBox(self.gbGroupReport)
        self.chkGroupByDoctor.setObjectName(_fromUtf8("chkGroupByDoctor"))
        self.verticalLayout_2.addWidget(self.chkGroupByDoctor)
        self.verticalLayout.addWidget(self.gbGroupReport)
        self.lBottom = QtGui.QHBoxLayout()
        self.lBottom.setObjectName(_fromUtf8("lBottom"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.lBottom.addItem(spacerItem)
        self.btnPrint = QtGui.QPushButton(Checks)
        self.btnPrint.setObjectName(_fromUtf8("btnPrint"))
        self.lBottom.addWidget(self.btnPrint)
        self.btnClose = QtGui.QPushButton(Checks)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.lBottom.addWidget(self.btnClose)
        self.verticalLayout.addLayout(self.lBottom)

        self.retranslateUi(Checks)
        QtCore.QMetaObject.connectSlotsByName(Checks)

    def retranslateUi(self, Checks):
        Checks.setWindowTitle(_translate("Checks", "Проверка реестров", None))
        self.gbChecks.setTitle(_translate("Checks", "Проверки", None))
        self.pbChecks.setFormat(_translate("Checks", "%v", None))
        self.chkOnlyErrors.setText(_translate("Checks", "Выводить только ошибки", None))
        self.gbGroupReport.setTitle(_translate("Checks", "Сгруппировать отчёт", None))
        self.rbGroupByData.setText(_translate("Checks", "по данным", None))
        self.rbGroupByErrors.setText(_translate("Checks", "по ошибкам", None))
        self.chkGroupByDoctor.setText(_translate("Checks", "по врачам", None))
        self.btnPrint.setText(_translate("Checks", "Печать F6", None))
        self.btnPrint.setShortcut(_translate("Checks", "F6", None))
        self.btnClose.setText(_translate("Checks", "Закрыть", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Checks = QtGui.QDialog()
    ui = Ui_Checks()
    ui.setupUi(Checks)
    Checks.show()
    sys.exit(app.exec_())

