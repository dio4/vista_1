# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ImportTariffsR77.ui'
#
# Created: Fri Jun 15 12:16:25 2012
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
        Dialog.resize(479, 500)
        self.layoutWidget = QtGui.QWidget(Dialog)
        self.layoutWidget.setGeometry(QtCore.QRect(11, 12, 458, 480))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_5.setMargin(0)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self._2 = QtGui.QHBoxLayout()
        self._2.setObjectName(_fromUtf8("_2"))
        self.label = QtGui.QLabel(self.layoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self._2.addWidget(self.label)
        self.edtFileName = QtGui.QLineEdit(self.layoutWidget)
        self.edtFileName.setText(_fromUtf8(""))
        self.edtFileName.setReadOnly(True)
        self.edtFileName.setObjectName(_fromUtf8("edtFileName"))
        self._2.addWidget(self.edtFileName)
        self.btnSelectFile = QtGui.QToolButton(self.layoutWidget)
        self.btnSelectFile.setObjectName(_fromUtf8("btnSelectFile"))
        self._2.addWidget(self.btnSelectFile)
        self.btnView = QtGui.QPushButton(self.layoutWidget)
        self.btnView.setObjectName(_fromUtf8("btnView"))
        self._2.addWidget(self.btnView)
        self.verticalLayout_5.addLayout(self._2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.gbDublicates = QtGui.QGroupBox(self.layoutWidget)
        self.gbDublicates.setObjectName(_fromUtf8("gbDublicates"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.gbDublicates)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.chkUpdate = QtGui.QRadioButton(self.gbDublicates)
        self.chkUpdate.setChecked(True)
        self.chkUpdate.setObjectName(_fromUtf8("chkUpdate"))
        self.verticalLayout_4.addWidget(self.chkUpdate)
        self.chkSkip = QtGui.QRadioButton(self.gbDublicates)
        self.chkSkip.setObjectName(_fromUtf8("chkSkip"))
        self.verticalLayout_4.addWidget(self.chkSkip)
        self.chkAskUser = QtGui.QRadioButton(self.gbDublicates)
        self.chkAskUser.setObjectName(_fromUtf8("chkAskUser"))
        self.verticalLayout_4.addWidget(self.chkAskUser)
        self.verticalLayout_2.addWidget(self.gbDublicates)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout_5.addLayout(self.horizontalLayout)
        self.progressBar = QtGui.QProgressBar(self.layoutWidget)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.verticalLayout_5.addWidget(self.progressBar)
        self.statusLabel = QtGui.QLabel(self.layoutWidget)
        self.statusLabel.setText(_fromUtf8(""))
        self.statusLabel.setObjectName(_fromUtf8("statusLabel"))
        self.verticalLayout_5.addWidget(self.statusLabel)
        self.log = QtGui.QTextBrowser(self.layoutWidget)
        self.log.setObjectName(_fromUtf8("log"))
        self.verticalLayout_5.addWidget(self.log)
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.btnImport = QtGui.QPushButton(self.layoutWidget)
        self.btnImport.setObjectName(_fromUtf8("btnImport"))
        self.hboxlayout.addWidget(self.btnImport)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.labelNum = QtGui.QLabel(self.layoutWidget)
        self.labelNum.setObjectName(_fromUtf8("labelNum"))
        self.hboxlayout.addWidget(self.labelNum)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem1)
        self.btnClose = QtGui.QPushButton(self.layoutWidget)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.hboxlayout.addWidget(self.btnClose)
        self.verticalLayout_5.addLayout(self.hboxlayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Загрузка тарифов для Московской области", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "импортировать из", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectFile.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.btnView.setText(QtGui.QApplication.translate("Dialog", "Просмотр", None, QtGui.QApplication.UnicodeUTF8))
        self.gbDublicates.setTitle(QtGui.QApplication.translate("Dialog", "Совпадающие записи", None, QtGui.QApplication.UnicodeUTF8))
        self.chkUpdate.setText(QtGui.QApplication.translate("Dialog", "Обновить", None, QtGui.QApplication.UnicodeUTF8))
        self.chkSkip.setText(QtGui.QApplication.translate("Dialog", "Пропустить", None, QtGui.QApplication.UnicodeUTF8))
        self.chkAskUser.setText(QtGui.QApplication.translate("Dialog", "Спросить у пользователя", None, QtGui.QApplication.UnicodeUTF8))
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

