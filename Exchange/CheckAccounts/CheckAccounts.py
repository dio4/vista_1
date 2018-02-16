#!/usr/bin/env python
# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
## Copyright (C) 2012 SAMSON Group. All rights reserved.
##
#############################################################################
##
## Это программа является свободным программным обеспечением.
## Вы можете использовать, распространять и/или модифицировать её согласно
## условиям GNU GPL версии 3 или любой более поздней версии.
##
#############################################################################

from library.Utils import *
from AdditionalRB import CAdditionalRB
from Account import CAccount
from Checks import CChecks
from Ui_CheckAccounts import Ui_CheckAccounts

class CCheckAccounts(QtGui.QDialog, Ui_CheckAccounts):

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.btnCheck.setEnabled(False)
        self._inProcess = False
        self._fileName = ''

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            event.accept()
            self.close()
        else:
            QtGui.QDialog.keyPressEvent(self, event)

    def closeEvent(self, event):
        if self._inProcess:
            reply = QtGui.QMessageBox.question(self, u'Загрузка данных', u'Вы действительно хотите прервать загрузку?',
                                               QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                event.accept()
                self._inProcess = False
            else:
                event.ignore()

    def exec_(self, fileName=''):
        query = QtGui.qApp.db.query(u"SHOW TABLES LIKE 'rbCheckAccounts%'")
        tables = set()
        while query.next():
            tables.add(forceString(query.record().value(0)).lower())
        necessaryTables = [
            u'rbcheckaccountsadditionalrbs',
            u'rbcheckaccountschecks',
            u'rbcheckaccountsd',
            u'rbcheckaccountsl',
            u'rbcheckaccountsn',
            u'rbcheckaccountsp',
            u'rbcheckaccountsu'
        ]
        if not tables.issuperset(necessaryTables):
            QtGui.QMessageBox.critical(
                self,
                u'Ошибка',
                u'Структура вашей базы данных не позволяет выполнять проверку счетов',
                QtGui.QMessageBox.Close
            )
            return

        if fileName:
            self._fileName = fileName
            QtCore.QTimer.singleShot(0, self.on_btnCheck_clicked)
        QtGui.QDialog.exec_(self)

    def _processReferenceBooks(self):

        def exceptionMessage(exception, referenceBookName, referenceBookFileName):
            errorTitle = u'<b><font color="red">Ошибка:</font></b>'
            if isinstance(exception, CAdditionalRB.FileNotFoundError):
                self.tbAdditionalRBs.append(
                    u'%s Файл "%s" справочника "%s" не найден!' %
                    (errorTitle, referenceBookFileName, referenceBookName))
            elif isinstance(exception, CAdditionalRB.ReferenceBookNotFoundError):
                self.tbAdditionalRBs.append(
                    u'%s Справочник %s "%s" не найден в таблице дополнительных справочников модуля!' %
                    (errorTitle, referenceBookFileName, referenceBookName))
            elif isinstance(exception, CAdditionalRB.MetadataMappingError):
                self.tbAdditionalRBs.append(
                    u'%s Структура справочника %s "%s" не соответствует файлу справочника!' %
                    (errorTitle, referenceBookFileName, referenceBookName))
            elif isinstance(exception, (CAdditionalRB.CreateError, Exception)):
                try:
                    exceptionMsg = unicode(exception)
                except UnicodeDecodeError:
                    exceptionMsg = str(exception).decode(locale.getpreferredencoding())
                self.tbAdditionalRBs.append(
                    u'%s Не удалось создать справочник %s "%s" - %s' %
                    (errorTitle, referenceBookFileName, referenceBookName, exceptionMsg))

        def callbackUpdate(currentValue, maxValue):
            if not currentValue:
                self.pbAdditionalRBs.setMaximum(maxValue)
                self.pbAdditionalRBs.setFormat('%v' + '/%s' % maxValue)
            self.pbAdditionalRBs.setValue(currentValue)
            QtGui.qApp.processEvents()
            return self._inProcess

        if not self._inProcess:
            return False
        result = True
        self.pbAdditionalRBs.setValue(0)
        self.tbAdditionalRBs.clear()
        additionalRBs = QtGui.qApp.db.table('rbCheckAccountsAdditionalRBs')
        referenceBooks = QtGui.qApp.db.getRecordList(additionalRBs, '*', additionalRBs['deleted'].eq(0), 'fileName')
        for referenceBook in referenceBooks:
            referenceBookName = forceString(referenceBook.value('name'))
            referenceBookFileName = forceString(referenceBook.value('fileName'))
            try:
                self.tbAdditionalRBs.append(
                    u'<b>Обработка: </b>Файл %s "%s"' % (referenceBookFileName, referenceBookName))
                CAdditionalRB(self.edtRBPath.text(), referenceBook, callbackUpdate).update()
                if not self._inProcess:
                    break
                else:
                    self.tbAdditionalRBs.append(
                        u'<b><font color="green">Успешно: </font></b>Файл %s "%s"' % (referenceBookFileName, referenceBookName))
            except Exception as e:
                if not self._inProcess:
                    break
                else:
                    exceptionMessage(e, referenceBookName, referenceBookFileName)
                    result = False
        return result

    def _processAccount(self):

        def exceptionMessage(exception):
            errorTitle = u'<b><font color="red">Ошибка:</font></b>'
            if isinstance(exception, CAccount.InsertError):
                self.tbAccount.append(u'%s Не удалось загрузить "%s" файл-реестра - %s' %
                                      (errorTitle, exception.fileName, exception.message))
            elif isinstance(exception, CAccount.RequiredFilesNotFoundError):
                self.tbAccount.append(
                    u'%s Не найдены данные реестра: %s' % (errorTitle, ', '.join(exception.requiredFiles)))
            elif isinstance(exception, Exception):
                try:
                    exceptionMsg = unicode(exception)
                except UnicodeDecodeError:
                    exceptionMsg = str(exception).decode(locale.getpreferredencoding())
                self.tbAccount.append(u'%s Не удалось загрузить данные - %s' % (errorTitle, exceptionMsg))

        def callbackUpdate(fileName, currentValue, maxValue):
            if not currentValue:
                self.pbAccount.setMaximum(maxValue)
                self.pbAccount.setFormat('%v' + '/%s' % maxValue)
                self.tbAccount.append(u'<b>Обработка: </b>Файл %s' % fileName)
            elif currentValue == maxValue:
                self.tbAccount.append(u'<b><font color="green">Успешно: </font></b>Файл %s' % fileName)
            self.pbAccount.setValue(currentValue)
            QtGui.qApp.processEvents()
            return self._inProcess

        if not self._inProcess:
            return False
        result = True
        self.pbAccount.setValue(0)
        self.tbAccount.clear()
        try:
            CAccount(forceStringEx(self.edtAccountPath.text()), callbackUpdate).update()
        except Exception as e:
            if self._inProcess:
                exceptionMessage(e)
                result = False
        return result

    @QtCore.pyqtSignature('')
    def on_btnAccountPath_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self, u'Укажите файл с данными', self.edtAccountPath.text(),
                                                     u'Файл ZIP (*.zip)')
        if fileName != '':
            self.edtAccountPath.setText(QtCore.QDir.toNativeSeparators(fileName))
            self.btnCheck.setEnabled(True)

    @QtCore.pyqtSignature('')
    def on_btnRBPath_clicked(self):
        dirName = QtGui.QFileDialog.getExistingDirectory(self, u'Укажите путь к файлам справочников', self.edtRBPath.text())
        if dirName != '':
            self.edtRBPath.setText(QtCore.QDir.toNativeSeparators(dirName))

    @QtCore.pyqtSignature('')
    def on_chkOnlyData_clicked(self):
        if self.chkOnlyData.isChecked():
            reply = QtGui.QMessageBox.question(self, u'Загрузка данных',
                                               u'Вы действительно хотите только загрузить данные?',
                                               QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                self.btnCheck.setText(u'Загрузить')
            else:
                self.chkOnlyData.setChecked(False)
        else:
            self.btnCheck.setText(u'Проверить')
        self.btnCheck.setEnabled(self.chkOnlyData.isChecked() or not self.edtAccountPath.text().isEmpty())

    @QtCore.pyqtSignature('')
    def on_btnCheck_clicked(self):
        if self._fileName:
            self.edtAccountPath.setText(self._fileName)
        self.btnAccountPath.setEnabled(False)
        self.btnRBPath.setEnabled(False)
        self.chkOnlyData.setEnabled(False)
        self.btnCheck.setEnabled(False)
        self._inProcess = True
        try:
            loadingResult = self._processReferenceBooks()
            if not self.edtAccountPath.text().isEmpty():
                loadingResult = self._processAccount() and loadingResult
            if self._inProcess:
                if not loadingResult:
                    QtGui.QMessageBox.critical(self, u'Загрузка данных', u'При загрузке данных произошла ошибка!',
                                               QtGui.QMessageBox.Close)
                else:
                    if self.chkOnlyData.isChecked():
                        QtGui.QMessageBox.information(self, u'Загрузка данных', u'Загрузка данных успешно завершена!',
                                                      QtGui.QMessageBox.Close)
                    else:
                        try:
                            CChecks(self).exec_()
                        finally:
                            CAccount.clear()
        finally:
            if not self._fileName:
                self.btnAccountPath.setEnabled(True)
                self.btnRBPath.setEnabled(True)
                self.chkOnlyData.setEnabled(True)
            self.btnCheck.setEnabled(True)
            self._inProcess = False

    @QtCore.pyqtSignature('')
    def on_btnClose_clicked(self):
        self.close()