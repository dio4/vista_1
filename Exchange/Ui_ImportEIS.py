# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ImportEIS.ui'
#
# Created: Fri Jun 15 12:15:17 2012
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
        Dialog.resize(543, 469)
        self.gridLayout_2 = QtGui.QGridLayout(Dialog)
        self.gridLayout_2.setMargin(4)
        self.gridLayout_2.setSpacing(4)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(4)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.hboxlayout.addWidget(self.label)
        self.splitter = QtGui.QSplitter(Dialog)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.edtFileName = QtGui.QLineEdit(self.splitter)
        self.edtFileName.setText(_fromUtf8(""))
        self.edtFileName.setReadOnly(True)
        self.edtFileName.setObjectName(_fromUtf8("edtFileName"))
        self.edtIP = QtGui.QLineEdit(self.splitter)
        self.edtIP.setReadOnly(True)
        self.edtIP.setObjectName(_fromUtf8("edtIP"))
        self.hboxlayout.addWidget(self.splitter)
        self.gridLayout_2.addLayout(self.hboxlayout, 0, 0, 1, 3)
        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.setSpacing(4)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.label_cur_mon = QtGui.QLabel(Dialog)
        self.label_cur_mon.setObjectName(_fromUtf8("label_cur_mon"))
        self.vboxlayout.addWidget(self.label_cur_mon)
        self.label_eis_mon = QtGui.QLabel(Dialog)
        self.label_eis_mon.setObjectName(_fromUtf8("label_eis_mon"))
        self.vboxlayout.addWidget(self.label_eis_mon)
        self.chkLogImportRefuse = QtGui.QCheckBox(Dialog)
        self.chkLogImportRefuse.setObjectName(_fromUtf8("chkLogImportRefuse"))
        self.vboxlayout.addWidget(self.chkLogImportRefuse)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.vboxlayout.addItem(spacerItem)
        self.gridLayout_2.addLayout(self.vboxlayout, 1, 2, 5, 1)
        self.checkBox_3 = QtGui.QCheckBox(Dialog)
        self.checkBox_3.setEnabled(False)
        self.checkBox_3.setObjectName(_fromUtf8("checkBox_3"))
        self.gridLayout_2.addWidget(self.checkBox_3, 3, 1, 1, 1)
        self.chkOnlyNew = QtGui.QCheckBox(Dialog)
        self.chkOnlyNew.setChecked(True)
        self.chkOnlyNew.setObjectName(_fromUtf8("chkOnlyNew"))
        self.gridLayout_2.addWidget(self.chkOnlyNew, 4, 1, 1, 1)
        self.progressBar = QtGui.QProgressBar(Dialog)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout_2.addWidget(self.progressBar, 6, 0, 1, 3)
        self.statusLabel = QtGui.QLabel(Dialog)
        self.statusLabel.setText(_fromUtf8(""))
        self.statusLabel.setObjectName(_fromUtf8("statusLabel"))
        self.gridLayout_2.addWidget(self.statusLabel, 7, 0, 1, 3)
        self.logBrowser = QtGui.QTextBrowser(Dialog)
        self.logBrowser.setObjectName(_fromUtf8("logBrowser"))
        self.gridLayout_2.addWidget(self.logBrowser, 8, 0, 1, 3)
        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setSpacing(4)
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setObjectName(_fromUtf8("hboxlayout1"))
        self.btnImport = QtGui.QPushButton(Dialog)
        self.btnImport.setObjectName(_fromUtf8("btnImport"))
        self.hboxlayout1.addWidget(self.btnImport)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem1)
        self.labelNum = QtGui.QLabel(Dialog)
        self.labelNum.setObjectName(_fromUtf8("labelNum"))
        self.hboxlayout1.addWidget(self.labelNum)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem2)
        self.btnClose = QtGui.QPushButton(Dialog)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.hboxlayout1.addWidget(self.btnClose)
        self.gridLayout_2.addLayout(self.hboxlayout1, 9, 0, 1, 3)
        self.frmAge = QtGui.QFrame(Dialog)
        self.frmAge.setFrameShape(QtGui.QFrame.NoFrame)
        self.frmAge.setFrameShadow(QtGui.QFrame.Raised)
        self.frmAge.setObjectName(_fromUtf8("frmAge"))
        self._2 = QtGui.QHBoxLayout(self.frmAge)
        self._2.setSpacing(4)
        self._2.setMargin(0)
        self._2.setObjectName(_fromUtf8("_2"))
        self.edtAgeFrom = QtGui.QSpinBox(self.frmAge)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAgeFrom.sizePolicy().hasHeightForWidth())
        self.edtAgeFrom.setSizePolicy(sizePolicy)
        self.edtAgeFrom.setMaximum(150)
        self.edtAgeFrom.setObjectName(_fromUtf8("edtAgeFrom"))
        self._2.addWidget(self.edtAgeFrom)
        self.lblAgeTo = QtGui.QLabel(self.frmAge)
        self.lblAgeTo.setObjectName(_fromUtf8("lblAgeTo"))
        self._2.addWidget(self.lblAgeTo)
        self.edtAgeTo = QtGui.QSpinBox(self.frmAge)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAgeTo.sizePolicy().hasHeightForWidth())
        self.edtAgeTo.setSizePolicy(sizePolicy)
        self.edtAgeTo.setMaximum(150)
        self.edtAgeTo.setProperty("value", 150)
        self.edtAgeTo.setObjectName(_fromUtf8("edtAgeTo"))
        self._2.addWidget(self.edtAgeTo)
        self.lblAgeYears = QtGui.QLabel(self.frmAge)
        self.lblAgeYears.setObjectName(_fromUtf8("lblAgeYears"))
        self._2.addWidget(self.lblAgeYears)
        self.gridLayout_2.addWidget(self.frmAge, 5, 1, 1, 1)
        self.cmbPart = QtGui.QComboBox(Dialog)
        self.cmbPart.setObjectName(_fromUtf8("cmbPart"))
        self.cmbPart.addItem(_fromUtf8(""))
        self.cmbPart.addItem(_fromUtf8(""))
        self.gridLayout_2.addWidget(self.cmbPart, 2, 1, 1, 1)
        self.lblPart = QtGui.QLabel(Dialog)
        self.lblPart.setObjectName(_fromUtf8("lblPart"))
        self.gridLayout_2.addWidget(self.lblPart, 2, 0, 1, 1)
        self.lblAge = QtGui.QLabel(Dialog)
        self.lblAge.setObjectName(_fromUtf8("lblAge"))
        self.gridLayout_2.addWidget(self.lblAge, 5, 0, 1, 1)
        self.label.setBuddy(self.edtFileName)
        self.lblAgeTo.setBuddy(self.edtAgeTo)
        self.lblAgeYears.setBuddy(self.edtAgeTo)
        self.lblPart.setBuddy(self.cmbPart)
        self.lblAge.setBuddy(self.edtAgeFrom)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.edtFileName, self.edtIP)
        Dialog.setTabOrder(self.edtIP, self.cmbPart)
        Dialog.setTabOrder(self.cmbPart, self.checkBox_3)
        Dialog.setTabOrder(self.checkBox_3, self.chkOnlyNew)
        Dialog.setTabOrder(self.chkOnlyNew, self.edtAgeFrom)
        Dialog.setTabOrder(self.edtAgeFrom, self.edtAgeTo)
        Dialog.setTabOrder(self.edtAgeTo, self.chkLogImportRefuse)
        Dialog.setTabOrder(self.chkLogImportRefuse, self.logBrowser)
        Dialog.setTabOrder(self.logBrowser, self.btnImport)
        Dialog.setTabOrder(self.btnImport, self.btnClose)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Загрузка из ЕИС", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "импортировать из", None, QtGui.QApplication.UnicodeUTF8))
        self.label_cur_mon.setText(QtGui.QApplication.translate("Dialog", "загруженный тарифный месяц", None, QtGui.QApplication.UnicodeUTF8))
        self.label_eis_mon.setText(QtGui.QApplication.translate("Dialog", "тарифный месяц ЕИС", None, QtGui.QApplication.UnicodeUTF8))
        self.chkLogImportRefuse.setText(QtGui.QApplication.translate("Dialog", "Формировать протокол на не импортированные записи", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_3.setText(QtGui.QApplication.translate("Dialog", "жёсткий контроль", None, QtGui.QApplication.UnicodeUTF8))
        self.chkOnlyNew.setText(QtGui.QApplication.translate("Dialog", "не загружать повторно", None, QtGui.QApplication.UnicodeUTF8))
        self.btnImport.setText(QtGui.QApplication.translate("Dialog", "начать импортирование", None, QtGui.QApplication.UnicodeUTF8))
        self.labelNum.setText(QtGui.QApplication.translate("Dialog", "всего записей в источнике:", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("Dialog", "закрыть", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAgeTo.setText(QtGui.QApplication.translate("Dialog", "по", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAgeYears.setText(QtGui.QApplication.translate("Dialog", "лет", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbPart.setItemText(0, QtGui.QApplication.translate("Dialog", "РПФ", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbPart.setItemText(1, QtGui.QApplication.translate("Dialog", "МУ", None, QtGui.QApplication.UnicodeUTF8))
        self.lblPart.setText(QtGui.QApplication.translate("Dialog", "Загружать из ", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAge.setText(QtGui.QApplication.translate("Dialog", "Возраст с", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

