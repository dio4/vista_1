# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/craz/s11_local/Exchange/ImportTariffsR67.ui'
#
# Created: Mon Feb 18 14:56:24 2013
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
        self._3 = QtGui.QHBoxLayout()
        self._3.setObjectName(_fromUtf8("_3"))
        self.label_2 = QtGui.QLabel(self.layoutWidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self._3.addWidget(self.label_2)
        self.edtCustomFileName = QtGui.QLineEdit(self.layoutWidget)
        self.edtCustomFileName.setText(_fromUtf8(""))
        self.edtCustomFileName.setReadOnly(True)
        self.edtCustomFileName.setObjectName(_fromUtf8("edtCustomFileName"))
        self._3.addWidget(self.edtCustomFileName)
        self.btnCustomSelectFile = QtGui.QToolButton(self.layoutWidget)
        self.btnCustomSelectFile.setObjectName(_fromUtf8("btnCustomSelectFile"))
        self._3.addWidget(self.btnCustomSelectFile)
        self.btnCustomView = QtGui.QPushButton(self.layoutWidget)
        self.btnCustomView.setObjectName(_fromUtf8("btnCustomView"))
        self._3.addWidget(self.btnCustomView)
        self.verticalLayout_5.addLayout(self._3)
        self.chkOnlyForCurrentOrg = QtGui.QCheckBox(self.layoutWidget)
        self.chkOnlyForCurrentOrg.setObjectName(_fromUtf8("chkOnlyForCurrentOrg"))
        self.verticalLayout_5.addWidget(self.chkOnlyForCurrentOrg)
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
        self.chkAppend = QtGui.QRadioButton(self.gbDublicates)
        self.chkAppend.setObjectName(_fromUtf8("chkAppend"))
        self.verticalLayout_4.addWidget(self.chkAppend)
        self.chkSkip = QtGui.QRadioButton(self.gbDublicates)
        self.chkSkip.setObjectName(_fromUtf8("chkSkip"))
        self.verticalLayout_4.addWidget(self.chkSkip)
        self.chkAskUser = QtGui.QRadioButton(self.gbDublicates)
        self.chkAskUser.setObjectName(_fromUtf8("chkAskUser"))
        self.verticalLayout_4.addWidget(self.chkAskUser)
        self.verticalLayout_2.addWidget(self.gbDublicates)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout_5.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.lblUetValue = QtGui.QLabel(self.layoutWidget)
        self.lblUetValue.setObjectName(_fromUtf8("lblUetValue"))
        self.horizontalLayout_2.addWidget(self.lblUetValue)
        self.edtUetValue = QtGui.QDoubleSpinBox(self.layoutWidget)
        self.edtUetValue.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.edtUetValue.setMinimum(0.01)
        self.edtUetValue.setMaximum(99999999.99)
        self.edtUetValue.setObjectName(_fromUtf8("edtUetValue"))
        self.horizontalLayout_2.addWidget(self.edtUetValue)
        self.verticalLayout_5.addLayout(self.horizontalLayout_2)
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
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Загрузка тарифов для Смоленской области", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "импортировать из", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectFile.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.btnView.setText(QtGui.QApplication.translate("Dialog", "Просмотр", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "с  настройками из", None, QtGui.QApplication.UnicodeUTF8))
        self.btnCustomSelectFile.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.btnCustomView.setText(QtGui.QApplication.translate("Dialog", "Просмотр", None, QtGui.QApplication.UnicodeUTF8))
        self.chkOnlyForCurrentOrg.setToolTip(QtGui.QApplication.translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Импортируются только те тарифы, для которых код в поле <span style=\" font-weight:600;\">MCOD </span>источника совпадает с кодом <span style=\" font-weight:600;\">ИНФИС </span>текущей организации.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.chkOnlyForCurrentOrg.setText(QtGui.QApplication.translate("Dialog", "только для текущего ЛПУ", None, QtGui.QApplication.UnicodeUTF8))
        self.gbDublicates.setTitle(QtGui.QApplication.translate("Dialog", "Совпадающие записи", None, QtGui.QApplication.UnicodeUTF8))
        self.chkUpdate.setText(QtGui.QApplication.translate("Dialog", "Обновить", None, QtGui.QApplication.UnicodeUTF8))
        self.chkAppend.setToolTip(QtGui.QApplication.translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Добавляется </span><span style=\" font-size:8pt; font-weight:600;\">новый</span><span style=\" font-size:8pt;\"> тариф, действующий с</span><span style=\" font-size:8pt; font-weight:600;\"> текущей</span><span style=\" font-size:8pt;\"> даты, а существующий тариф закрывается с днём ранее </span><span style=\" font-size:8pt; font-weight:600;\">текущей</span><span style=\" font-size:8pt;\"> даты.</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.chkAppend.setText(QtGui.QApplication.translate("Dialog", "Дополнить", None, QtGui.QApplication.UnicodeUTF8))
        self.chkSkip.setText(QtGui.QApplication.translate("Dialog", "Пропустить", None, QtGui.QApplication.UnicodeUTF8))
        self.chkAskUser.setText(QtGui.QApplication.translate("Dialog", "Спросить у пользователя", None, QtGui.QApplication.UnicodeUTF8))
        self.lblUetValue.setToolTip(QtGui.QApplication.translate("Dialog", "только для стоматологии", None, QtGui.QApplication.UnicodeUTF8))
        self.lblUetValue.setText(QtGui.QApplication.translate("Dialog", "Стоимость одного УЕТ", None, QtGui.QApplication.UnicodeUTF8))
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

