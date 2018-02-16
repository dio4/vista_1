# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2014 Vista Software. All rights reserved.
##
#############################################################################


"""
Dialog for sending bug report to help desk
"""

import smtplib
import os
import zipfile
import datetime

from email                      import encoders
from email.mime.text            import MIMEText
from email.mime.multipart       import MIMEMultipart
from email.mime.base            import MIMEBase

from PyQt4                      import QtGui, QtCore

from bugreport.Ui_SendBugReport import Ui_sendBugReportDialog
from library.Utils              import forceString


HELPDESKSENDER_MAIL = 'tex.vistamed.reporter@gmail.com' # Откуда шлем письма. Ящик должен регулярно очищаться (автоматически?).
HELPDESK_MAIL = 'tex.vistamed@gmail.com'       # Куда шлем письма. Обрабатываются непосредственно отделом тех.поддержки.
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465
HELPDESK_PASS  = 'googlo'
HELPDESK_WORD = 'phobia'

class CSendBugReportDialog(QtGui.QDialog, Ui_sendBugReportDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.connect(self, QtCore.SIGNAL('accepted()'), self.sendReport)

    def __getArchiveName(self, path, file):
        return path + "\\" + str(datetime.datetime.now().strftime("%Y-%m-%d")) + "." + str(file) + ".zip"

    def __getFileArchiveName(self, path, file):
        return str(datetime.datetime.now().strftime("%Y-%m-%d")) + "." + str(file) + ".zip"

    @QtCore.pyqtSlot(bool)
    def sendReport(self):
        mail = MIMEMultipart()

        userName = QtGui.qApp.userName()
        mail['Subject'] = userName
        mail['From'] = userName
        mail['To'] = u'Тех. поддержка КПС "Виста-Мед"'

        messageText = forceString(self.edtMessage.toPlainText())
        msg = MIMEText(messageText, _charset='utf8')
        mail.attach(msg)

        if self.chkAttachErrorLog.isChecked():
            logDir = QtGui.qApp.logDir
            path = os.path.join(logDir, 'error.log')
            if os.path.isfile(path):
                zf = zipfile.ZipFile(self.__getArchiveName(logDir, "error.log"), mode="w", compression=zipfile.ZIP_DEFLATED)
                try:
                    zf.writestr("error.log", open(path).read())
                    os.remove(path)  # В try потому что будет грустно, если мы удалим лог, а в архив он не запишется
                finally:
                    zf.close()

                fp = open(self.__getArchiveName(logDir, "error.log"), 'rb')
                log = MIMEBase('application', 'zip')
                log.set_payload(fp.read())
                fp.close()
                encoders.encode_base64(log)
                log.add_header('Content-Disposition', 'attachment', filename=self.__getFileArchiveName(logDir, "error.log"))
                mail.attach(log)

        s = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        try:
            s.login(HELPDESKSENDER_MAIL, HELPDESK_PASS+HELPDESK_WORD)
        except smtplib.SMTPException:
            QtGui.QMessageBox.critical(self, u'Внимание',
                                       u'Не удалось подключиться к почтовому серверу, отправка сообщения невозможна.',
                                       QtGui.QMessageBox.Close)
            return
        try:
            pass
            s.sendmail(HELPDESKSENDER_MAIL, [HELPDESK_MAIL], mail.as_string())
        except smtplib.SMTPException:
            QtGui.QMessageBox.critical(self, u'Внимание',
                                       u'Не удалось отправить сообщение. Пожалуйста, повторите попытку позже или свяжитесь'
                                       u'со службой поддержки по телефону.',
                                       QtGui.QMessageBox.Close)
            return
        s.quit()
        QtGui.QMessageBox.warning(self, u'Внимание',
                                  u'Спасибо, Ваше письмо отправлено.\nДля ускорения обработки Вашего ' \
                                  u'обращения рекомендуем также сообщить о Вашей проблеме в службу технической поддержки '
                                  u'по телефону.',
                                  QtGui.QMessageBox.Close)
