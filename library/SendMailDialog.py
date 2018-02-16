#!/usr/bin/env python
# -*- coding: utf-8 -*-

import email.utils as emutils
import hashlib
import mimetypes
import os.path
import smtplib
import stat
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import *

from Registry.Utils import getClientEmail, getEmailContactType
from Ui_SendMailClientDialog import Ui_SendMailClientDialog
from Ui_SendMailDialog import Ui_SendMailDialog
from library.DialogBase import CDialogBase
from library.Utils import *

DefaultSMTPPort = 25


def validateEmail(email):
    EMAIL_REGEXP = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$'
    return re.match(EMAIL_REGEXP, email) is not None


def sendMail(parent, recipient, subject, text, attach=None):
    if not attach:
        attach = []
    dialog = CSendMailDialog(parent)
    dialog.edtRecipient.setText(recipient)
    dialog.edtSubject.setText(subject)
    dialog.edtText.setText(text)
    dialog.setAttach(attach)
    dialog.exec_()


def sendMailClient(parent, clientId, subject, text, attach=None):
    dialog = CSendMailClientDialog(parent, clientId, subject, text, attach)
    dialog.exec_()


def getMailPrefs(params=None):
    if not params:
        params = {}
    global DefaultSMTPPort

    appPrefs = QtGui.qApp.preferences.appPrefs
    result = {}
    result['SMTPServer'] = forceString(params.get('SMTPServer', appPrefs.get('SMTPServer', 'localhost')))
    port = forceInt(params.get('SMTPPort', appPrefs.get('SMTPPort', 0)))
    result['SMTPPort'] = port if port > 0 else DefaultSMTPPort
    result['mailAddress'] = forceString(params.get('mailAddress', appPrefs.get('mailAddress', '')))
    result['SMTPAuthentification'] = forceBool(params.get('SMTPAuthentification', appPrefs.get('SMTPAuthentification', False)))
    result['SMTPLogin'] = forceString(params.get('SMTPLogin', appPrefs.get('SMTPLogin', '')))
    result['SMTPPassword'] = forceString(params.get('SMTPPassword', appPrefs.get('SMTPPassword', '')))
    return result


def prepareMail(sender, recipient, subject, text, attach):
    encoding = 'koi8-r'
    encodingErrors = 'replace'
    encodedText = text.encode(encoding, encodingErrors)
    message = MIMEMultipart()
    message['From'] = Header(sender, encoding, errors=encodingErrors)
    message['To'] = Header(recipient, encoding, errors=encodingErrors)
    message['Subject'] = Header(subject.encode(encoding, encodingErrors), encoding, errors=encodingErrors)
    message['Date'] = emutils.formatdate(localtime=True)
    checksum = hashlib.md5()
    checksum.update(emutils.formatdate(localtime=True))
    checksum.update(encodedText)
    message['Message-ID'] = checksum.hexdigest()

    message.add_header(u'X-Mailer', u'SAMSON-VISTA v.1.0')
    message.preamble = 'This is a multi-part message in MIME format. ' \
                       'If you see this message, your mail client is not ' \
                       'capable of displaying the attachments.'
    message.epilogue = ''
    textPart = MIMEText(encodedText,
                        _subtype='html',
                        _charset=encoding)
    message.attach(textPart)
    ##                        _subtype='plain',

    for fileName in attach:
        attachFileName = os.path.basename(fileName)
        attachFileName = str(Header(attachFileName.encode(encoding, encodingErrors), encoding, errors=encodingErrors))
        ctype, encoding = mimetypes.guess_type(fileName)
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        if maintype == 'text':
            attachment = MIMEText(open(fileName, 'rb').read(), _subtype=subtype)
        elif maintype == 'image':
            attachment = MIMEImage(open(fileName, 'rb').read(), _subtype=subtype)
        elif maintype == 'audio':
            attachment = MIMEAudio(open(fileName, 'rb').read(), _subtype=subtype)
        else:
            attachment = MIMEApplication(open(fileName, 'rb').read(), 'octet-stream', name=attachFileName)
        # if encoding:
        #                attachment.add_header('Content-Encoding', encoding)
        attachment.add_header('Content-Disposition', 'attachment', filename=attachFileName)
        message.attach(attachment)
    return message


def sendMailInt(recipient, subject, text, attach, params=None):
    if not params:
        params = {}
    try:
        prefs = getMailPrefs(params)
        sender = prefs['mailAddress']
        message = prepareMail(sender, recipient, subject, text, attach)
        server = smtplib.SMTP(prefs['SMTPServer'], prefs['SMTPPort'])
        if prefs['SMTPAuthentification'] and server.has_extn('auth'):
            server.login(prefs['SMTPLogin'], prefs['SMTPPassword'])
        ###server.set_debuglevel(1)
        server.sendmail(sender, recipient, message.as_string())
        server.quit()
        return (True, '')
    except SMTPSenderRefused, e:
        errorMessage = u'Сервер отверг адрес отправителя\n%s' % unicode(e)
    except SMTPAuthenticationError, e:
        errorMessage = u'Сервер отверг соединение с указанным именем и паролём\n%s' % unicode(e)
    except SMTPDataError, e:
        errorMessage = u'Сервер отверг передаваемые данные\n%s' % unicode(e)
    except SMTPConnectError, e:
        errorMessage = u'Ошибка установления соединения с сервером\n%s' % unicode(e)
    except SMTPHeloError, e:
        errorMessage = u'Сервер отверг сообщение "HELO"\n%s' % unicode(e)
    except SMTPResponseException, e:
        errorMessage = u'Сервер сообщил об ошибке\n%s' % unicode(e)
    except SMTPRecipientsRefused, e:
        errorMessage = u'Сервер отверг получателей\n%s' % unicode(e)
    except SMTPServerDisconnected, e:
        errorMessage = u'Неожиданный разрыв соединения с сервером\n%s' % unicode(e)
    except SMTPException, e:
        errorMessage = u'Ошибка взаимодействия с сервером\n%s' % unicode(e)
    except IOError, e:
        if hasattr(e, 'filename'):
            errorMessage = u'Ошибка ввода/вывода %s:\n[Errno %s] %s' % (e.filename, e.errno, e.strerror)
        else:
            errorMessage = u'Ошибка ввода/вывода\n[Errno %s] %s' % (e.errno, e.strerror)
    except Exception, e:
        errorMessage = u'Ошибка\n%s' % unicode(e)
    QtGui.qApp.logCurrentException()
    return (False, errorMessage)


class CSendMailDialog(CDialogBase, Ui_SendMailDialog):
    def __init__(self, parent):
        CDialogBase.__init__(self, parent)

        self.mnuAttach = QtGui.QMenu(self)
        self.mnuAttach.setObjectName('mnuAttach')
        self.actAddAttach = QtGui.QAction(u'Добавить вложение', self)
        self.actAddAttach.setObjectName('actAddAttach')
        self.actDelAttach = QtGui.QAction(u'Удалить вложение', self)
        self.actDelAttach.setObjectName('actDelAttach')
        self.mnuAttach.addAction(self.actAddAttach)
        self.mnuAttach.addAction(self.actDelAttach)
        self.modelAttach = CAttachModel(self)
        self.btnSaveAsFile = QtGui.QPushButton(u'Сохранить как файл', self)
        self.btnSaveAsFile.setObjectName('btnSaveAsFile')
        self.setupUi(self)
        self.buttonBox.addButton(self.btnSaveAsFile, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setText(u'Отправить')
        self.tblAttach.setModel(self.modelAttach)
        self.tblAttach.setPopupMenu(self.mnuAttach)

    def setAttach(self, attach):
        self.modelAttach.setFiles(attach)

    def saveData(self):
        recipient = forceStringEx(self.edtRecipient.text())
        subject = forceStringEx(self.edtSubject.text())
        text = forceStringEx(self.edtText.document().toHtml(QByteArray('koi8-r')))
        attach = self.modelAttach.files()
        success, errorMessage = QtGui.qApp.callWithWaitCursor(self, sendMailInt, recipient, subject, text, attach)
        if success:
            QtGui.QMessageBox.information(self,
                                          u'Готово',
                                          u'Сообщение отправлено',
                                          QtGui.QMessageBox.Close)
            CDialogBase.accept(self)
            return True
        QtGui.QMessageBox.critical(self,
                                   u'Ошибка',
                                   errorMessage,
                                   QtGui.QMessageBox.Close)
        return False

    def saveAsFile(self):
        fileName = QtGui.QFileDialog.getSaveFileName(
            self, u'Выберите имя файла', QtGui.qApp.getSaveDir(), u'Почтовое сообщение (*.eml)')
        if fileName:
            QtGui.qApp.setSaveDir(fileName)
            recipient = forceStringEx(self.edtRecipient.text())
            subject = forceStringEx(self.edtSubject.text())
            text = forceStringEx(self.edtText.document().toHtml(QByteArray('koi8-r')))
            attach = self.modelAttach.files()
            message = prepareMail('', recipient, subject, text, attach)
            open(fileName, 'w+b').write(message.as_string())

    @QtCore.pyqtSlot()
    def on_mnuAttach_aboutToShow(self):
        currentRow = self.tblAttach.currentIndex().row()
        itemPresent = currentRow >= 0
        self.actDelAttach.setEnabled(itemPresent)

    @QtCore.pyqtSlot()
    def on_actAddAttach_triggered(self):
        fileNames = QtGui.QFileDialog.getOpenFileNames(
            self, u'Выберите один или несколько файлов', QtGui.qApp.getSaveDir())
        if fileNames:
            QtGui.qApp.setSaveDir(fileNames[0])
            self.modelAttach.appendFiles(fileNames)
            self.tblAttach.setCurrentIndex(self.modelAttach.index(self.modelAttach.rowCount() - 1, 0))

    @QtCore.pyqtSlot()
    def on_actDelAttach_triggered(self):
        self.tblAttach.removeCurrentRow()

    @QtCore.pyqtSlot()
    def on_btnSaveAsFile_clicked(self):
        QtGui.qApp.call(self, self.saveAsFile)


class CAttachModel(QAbstractTableModel):
    def __init__(self, parent):
        QAbstractTableModel.__init__(self, parent)
        self.__fileInfos = []

    def setFiles(self, files):
        self.__fileInfos = []
        self.appendFiles(files)

    def appendFiles(self, files):
        for fileName in files:
            strFileName = forceString(fileName)
            baseName = os.path.basename(forceString(strFileName))
            fileStat = os.stat(strFileName)
            size = fileStat[stat.ST_SIZE]
            self.__fileInfos.append((strFileName, baseName, size))
        self.reset()

    def files(self):
        return [fileInfo[0] for fileInfo in self.__fileInfos]

    def columnCount(self, index=QtCore.QModelIndex()):
        return 2

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self.__fileInfos)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            column = index.column()
            row = index.row()
            return toVariant(self.__fileInfos[row][column + 1])
        return QVariant()

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                if section == 0:
                    return toVariant(u'Файл')
                if section == 1:
                    return toVariant(u'Размер')
        return QVariant()

    def removeRow(self, row, parent=QModelIndex()):
        if 0 <= row < len(self.__fileInfos):
            self.beginRemoveRows(parent, row, row)
            del self.__fileInfos[row]
            self.endRemoveRows()
            return True
        return False


class CSendMailClientDialog(CDialogBase, Ui_SendMailClientDialog):
    u"""
    Отправка email пациенту,
    Введеный адрес (или несколько) сохраняются в контактах пациента
    """

    def __init__(self, parent, clientId, subject='', text='', attachFiles=None):
        super(CSendMailClientDialog, self).__init__(parent)

        self.setupUi(self)
        self.setWindowTitle(u'Отправка email пациенту')

        self._clientId = clientId

        self.edtRecipient.setText(self.formatClientMailList())
        self.edtText.setText(text)
        self._subject = subject
        self._text = text
        self._attachFiles = attachFiles or []

    def formatClientMailList(self):
        return u'; '.join(contact for typeName, contact, notes in getClientEmail(self._clientId))

    def getClientMailList(self):
        return filter(bool, map(lambda e: e.strip(), forceStringEx(self.edtRecipient.text()).split(u';')))

    def saveClientMail(self):
        if not self._clientId: return

        db = QtGui.qApp.db
        tableClientContact = db.table('ClientContact')

        emailContactTypeId = getEmailContactType()
        for mailContact in self.getClientMailList():
            cond = [
                tableClientContact['client_id'].eq(self._clientId),
                tableClientContact['contact'].eq(mailContact),
                tableClientContact['deleted'].eq(0)
            ]
            rec = db.getRecordEx(tableClientContact, 'id', cond)
            if rec is None:
                db.insertFromDict(tableClientContact, {
                    'createDateTime' : QtCore.QDateTime.currentDateTime(),
                    'createPerson_id': QtGui.qApp.userId,
                    'client_id'      : self._clientId,
                    'contactType_id' : emailContactTypeId,
                    'contact'        : mailContact
                })

    def sendMailInt(self, emailList, subject, text):
        prefs = getMailPrefs()
        FROM_ADDR = prefs['mailAddress']
        SMTP_SERVER = prefs['SMTPServer']
        SMTP_PORT = prefs['SMTPPort']
        PASSWORD = prefs['SMTPPassword']
        USE_AUTH = prefs['SMTPAuthentification']

        mail = MIMEMultipart('alternative')
        mail['Subject'] = subject
        mail['From'] = FROM_ADDR
        mail['To'] = u';'.join(emailList)

        html = MIMEText(text, 'html', 'utf8')
        html['MIME-Version'] = "1.0"
        html['Content-Type'] = "text/html; charset=utf-8"
        mail.attach(html)

        if USE_AUTH:
            s = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
            try:
                s.login(FROM_ADDR, PASSWORD)
            except smtplib.SMTPException as e:
                QtGui.QMessageBox.critical(self, u'Внимание',
                                           u'Не удалось подключиться к почтовому серверу, отправка сообщения невозможна.',
                                           QtGui.QMessageBox.Close)
                return False, unicode(e)
        else:
            s = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)

        try:
            s.sendmail(FROM_ADDR, emailList, mail.as_string())
        except smtplib.SMTPException as e:
            QtGui.QMessageBox.critical(self, u'Внимание',
                                       u'Не удалось отправить сообщение. Пожалуйста, повторите попытку позже или свяжитесь'
                                       u'со службой поддержки по телефону.',
                                       QtGui.QMessageBox.Close)
            return False, unicode(e)

        return True, ''

    def saveData(self):
        emailList = self.getClientMailList()
        if not emailList:
            QtGui.QMessageBox.information(self,
                                          u'Внимание',
                                          u'Введите адрес электронной почты\n'
                                          u'(несколько адресов через ";")',
                                          QtGui.QMessageBox.Ok)
            return False

        for email in emailList:
            if not validateEmail(email):
                QtGui.QMessageBox.warning(self,
                                          u'Внимание',
                                          u'<b>{0}</b> не является допустимым адресом электронной почты'.format(email))
                return False

        try:
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            success, errorMessage = self.sendMailInt(emailList, self._subject, self._text)
        except Exception as e:
            success = False
            errorMessage = unicode(e)
        finally:
            QtGui.qApp.restoreOverrideCursor()

        if success:
            QtGui.QMessageBox.information(self,
                                          u'Готово',
                                          u'Сообщение отправлено',
                                          QtGui.QMessageBox.Ok)
            self.saveClientMail()
            return True
        else:
            QtGui.QMessageBox.critical(self,
                                       u'Ошибка',
                                       errorMessage,
                                       QtGui.QMessageBox.Close)
            return False
