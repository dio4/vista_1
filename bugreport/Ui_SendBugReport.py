# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SendBugReport.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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

class Ui_sendBugReportDialog(object):
    def setupUi(self, sendBugReportDialog):
        sendBugReportDialog.setObjectName(_fromUtf8("sendBugReportDialog"))
        sendBugReportDialog.resize(447, 279)
        sendBugReportDialog.setSizeGripEnabled(False)
        self.gridlayout = QtGui.QGridLayout(sendBugReportDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.btnCancel = QtGui.QPushButton(sendBugReportDialog)
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.gridlayout.addWidget(self.btnCancel, 4, 2, 1, 1)
        self.btnSend = QtGui.QPushButton(sendBugReportDialog)
        self.btnSend.setObjectName(_fromUtf8("btnSend"))
        self.gridlayout.addWidget(self.btnSend, 4, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem, 4, 0, 1, 1)
        self.chkAttachErrorLog = QtGui.QCheckBox(sendBugReportDialog)
        self.chkAttachErrorLog.setObjectName(_fromUtf8("chkAttachErrorLog"))
        self.gridlayout.addWidget(self.chkAttachErrorLog, 2, 0, 1, 3)
        self.edtMessage = QtGui.QTextEdit(sendBugReportDialog)
        self.edtMessage.setObjectName(_fromUtf8("edtMessage"))
        self.gridlayout.addWidget(self.edtMessage, 1, 0, 1, 3)
        self.label = QtGui.QLabel(sendBugReportDialog)
        self.label.setTextFormat(QtCore.Qt.RichText)
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridlayout.addWidget(self.label, 0, 0, 1, 3)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem1, 3, 0, 1, 3)

        self.retranslateUi(sendBugReportDialog)
        QtCore.QObject.connect(self.btnSend, QtCore.SIGNAL(_fromUtf8("clicked()")), sendBugReportDialog.accept)
        QtCore.QObject.connect(self.btnCancel, QtCore.SIGNAL(_fromUtf8("clicked()")), sendBugReportDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(sendBugReportDialog)

    def retranslateUi(self, sendBugReportDialog):
        sendBugReportDialog.setWindowTitle(_translate("sendBugReportDialog", "Написать разработчикам", None))
        self.btnCancel.setText(_translate("sendBugReportDialog", "Отмена", None))
        self.btnSend.setText(_translate("sendBugReportDialog", "Отправить", None))
        self.chkAttachErrorLog.setText(_translate("sendBugReportDialog", "Прикрепить отчет об ошибках", None))
        self.label.setText(_translate("sendBugReportDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Пожалуйста, кратко опишите суть проблемы.<br /><span style=\" font-style:italic;\">Если вы собираетесь прикрепить отчет об ошибках, рекомендуется также указать примерные дату и время возникновения ошибки.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Укажите свои контактные данные, чтобы специалист тех поддержки связался с Вами, или позвоните по номерам: 8 (812) 416-60-50, 8 (812) 416-60-51</p></body></html>", None))

