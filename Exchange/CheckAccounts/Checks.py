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

from Reports.ReportBase import CReportBase, createTable
from Reports.ReportView import CReportViewDialog
from library.Utils import *
from Ui_Checks import Ui_Checks

class CChecks(QtGui.QDialog, Ui_Checks):

    _colsDescription = {'id': [u'№', '3%'],
                        'UID': [u'Номер записи', '6%'],
                        'SN': [u'Номер счета', '6%'],
                        'ISTI': [u'Номер карты', '6%'],
                        'DOC_TABN': [u'Табельный номер', '6%'],
                        'FIO': [u'Фамилия', '12%'],
                        'IMA': [u'Имя', '10%'],
                        'OTCH': [u'Отчество', '12%'],
                        'DATR': [u'Дата рождения', '6%'],
                        'KUSL': [u'Код услуги', '6%'],
                        'KSTAND': [u'Код СОМП', '6%'],
                        'CODETRN': [u'Код торг. наименования', '6%'],
                        'DATN': [u'Дата начала', '6%'],
                        'DATO': [u'Дата окончания', '6%'],
                        'NAPR_N' : [u'Номер направления', '6%'],
                        'NAPR_MO' : [u'МО, в которое направлен', '6%'],
                        'NAPR_D' : [u'Дата направления', '6%'],
                        'errors': [u'Ошибки', '10%'],
                        'notes': [u'Примечания', '10%']}

    _KEYFIELDS_UID_POS = 0

    _keyFields = {'P': ['SN', 'ISTI', 'FIO', 'IMA', 'OTCH', 'DATR'],
                  'U': ['UID', 'SN', 'KUSL', 'DATN', 'DATO'],
                  'D': ['DOC_TABN', 'FIO', 'IMA', 'OTCH'],
                  'L': ['SN', 'KSTAND', 'CODETRN'],
                  'N': ['SN', 'NAPR_N', 'NAPR_MO', 'NAPR_D', 'DOC_TABN']}

    _orderedLabels = ['P', 'U', 'D', 'L', 'N']

    _additionalFields = {'SN': ['ISTI', 'FIO', 'IMA', 'OTCH', 'DATR'],
                         'DOC_TABN': ['FIO', 'IMA', 'OTCH']}

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.chkOnlyErrors.setEnabled(False)
        self.btnPrint.setEnabled(False)
        self._errors = {}
        self._errorsInfo = {}
        self._clientsInfo = {}
        self._doctorsInfo = {}
        self._logErrorsCache = []
        self._inProcess = False

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            event.accept()
            self.close()
        else:
            QtGui.QDialog.keyPressEvent(self, event)

    def closeEvent(self, event):
        if self._inProcess:
            reply = QtGui.QMessageBox.question(self, u'Проверка данных', u'Вы действительно хотите прервать проверку?',
                                               QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                event.accept()
                self._inProcess = False
            else:
                event.ignore()

    def exec_(self):
        QtCore.QTimer.singleShot(0, self._run)
        QtGui.QDialog.exec_(self)

    def _run(self):

        def addError(label, key, error):
            self._errors.setdefault(label, {}).setdefault(key, [])
            if not error['code'] in self._errors[label][key]:
                self._errors[label][key].append(error['code'])
            if not error['code'] in self._errorsInfo:
                self._errorsInfo[error['code']] = (error['name'], error['note'])

        db = QtGui.qApp.db
        rbChecks = db.table('rbCheckAccountsChecks')
        rbSPR15 = db.table('rbCheckAccountsSPR15')
        joinRBs = rbChecks.leftJoin(rbSPR15, rbSPR15['CODE'].eq(rbChecks['code']))
        checks = db.getRecordList(joinRBs, '*', [rbChecks['deleted'].eq(0), rbSPR15['deleted'].eq(0)],
                                  rbChecks['code'].name())
        if not checks:
            return
        self._inProcess = True
        try:
            checksCount = 0
            self.pbChecks.setMaximum(len(checks))
            for check in checks:
                isError = False
                error = {'code': forceString(check.value('CODE')),
                         'name': forceString(check.value('NAME')),
                         'note': forceString(check.value('KOMMENT'))}
                self.lbChecks.setText(u'Код "%s": %s...' % (error['code'], error['name']))
                QtGui.qApp.processEvents()
                if not self._inProcess:
                    return
                try:
                    label = forceString(check.value('label'))
                    if not label in self._keyFields:
                        raise Exception(u'Для проверки задан неверный файл "%s"!' % label)
                    sqlStatement = forceString(check.value('sqlStatement'))
                    records = db.query(sqlStatement)
                    QtGui.qApp.processEvents()
                    if not self._inProcess:
                        return
                    if records.size() != 0:
                        isError = True
                        while records.next():
                            record = records.record()
                            fields = []
                            for field in self._keyFields[label]:
                                if record.value(field).isValid():
                                    fields.append(forceString(record.value(field)))
                                else:
                                    raise Exception(u'Список полей проверки не соответствует файлу "%s"!' % label)
                            addError(label, tuple(fields), error)
                    checksCount += 1
                    self.pbChecks.setValue(checksCount)
                    self._viewError(error['code'], error['name'], isError)
                    tbChecksVerticalScroll = self.tbChecks.verticalScrollBar()
                    tbChecksVerticalScroll.setValue(tbChecksVerticalScroll.maximum())
                except Exception as e:
                    try:
                        exceptionMsg = unicode(e)
                    except UnicodeDecodeError:
                        exceptionMsg = str(e).decode(locale.getpreferredencoding())
                    self.tbChecks.append(u'<b><font color="red">Ошибка: </font></b>'
                                         u'Не удалось выполнить проверку с кодом "%s" (%s) - %s' % (error['code'],
                                                                                                    error['name'],
                                                                                                    exceptionMsg))
                    return
            if not self._errors:
                QtGui.QMessageBox.information(self, u'Проверка данных', u'Проверка данных успешно завершена!',
                                              QtGui.QMessageBox.Close)
            else:
                self.chkOnlyErrors.setEnabled(True)
                self.btnPrint.setEnabled(True)
        finally:
            self._inProcess = False

    def _viewError(self, errorCode, errorName, isError, isCache=True):
        if isError:
            self.tbChecks.append(u'<b><font color="red">Код "%s": </font></b>%s' %
                                 (errorCode, errorName))
        else:
            self.tbChecks.append(u'<b><font color="green">Код "%s": </font></b>%s' %
                                 (errorCode, errorName))
        if isCache:
            self._logErrorsCache.append([errorCode, errorName, isError])

    def _getErrors(self):
        errors = self._errors
        if 'U' in errors and self.chkGroupByDoctor.isChecked():
            db = QtGui.qApp.db
            recordUIDs = [forceInt(keyValue[self._KEYFIELDS_UID_POS]) for keyValue in errors['U'].iterkeys()]
            # doctorNumbers = {doctorNumber1: [recordUIDs1], doctorNumber2: [recordUIDs2], ...}
            doctorNumbers = {}
            map(lambda record: doctorNumbers.setdefault(forceString(record.value('DOC_TABN')),
                                                        []).append(forceInt(record.value('UID'))),
                db.getRecordList(db.table('rbCheckAccountsU'), 'UID, DOC_TABN',
                                 db.table('rbCheckAccountsU')['UID'].inlist(recordUIDs)))
            errors = errors.copy()
            for doctorNumber in doctorNumbers.iterkeys():
                for keyValue, errorCodes in errors['U'].iteritems():
                    if forceInt(keyValue[self._KEYFIELDS_UID_POS]) in doctorNumbers[doctorNumber]:
                        errors.setdefault(('U', doctorNumber), {}).setdefault(keyValue, errorCodes)
            del errors['U']
        return errors

    def _getAdditionalInfo(self, label, field, key, cache):
        if key not in cache:
            rbTable = QtGui.qApp.db.table('rbCheckAccounts%s' % label)
            info = QtGui.qApp.db.getRecordEx(rbTable, '*', rbTable[field].eq(key))
            cache[key] = ['' if not info else forceString(info.value(fieldCache))
                          for fieldCache in self._additionalFields[field]]
        return cache[key]

    def _toHtml(self, label, data, cursor, additionalTitle=None, processCallBack=None):

        def getColumns():

            def addColumn(field, columns, format, index=None):
                if index is None:
                    columns.append((self._colsDescription[field][1], self._colsDescription[field][0], format))
                else:
                    columns.insert(index, (self._colsDescription[field][1], self._colsDescription[field][0], format))

            formatTop = QtGui.QTextBlockFormat()
            formatTop.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
            formatVCenter = QtGui.QTextBlockFormat()
            formatVCenter.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            formatClientInfo = QtGui.QTextBlockFormat()
            formatClientInfo.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            columns = []
            addColumn('id', columns, formatTop if not self.rbGroupByData.isChecked() else formatVCenter)
            keyFields = self._keyFields[label][:]
            if not label in ('P', 'D'):
                for field in ('SN', 'DOC_TABN'):
                    if field in keyFields:
                        keyFields[keyFields.index(field) + 1:keyFields.index(field) + 1] = self._additionalFields[field]
            for field in keyFields:
                if not field in ('FIO', 'IMA', 'OTCH'):
                    addColumn(field, columns, formatVCenter)
                else:
                    addColumn(field, columns, formatClientInfo)
            addColumn('errors', columns, formatTop if not self.rbGroupByData.isChecked() else formatVCenter,
                      1 if not self.rbGroupByData.isChecked() else None)
            addColumn('notes', columns, formatTop if not self.rbGroupByData.isChecked() else formatVCenter,
                      2 if not self.rbGroupByData.isChecked() else None)
            return columns

        def insertData(table):

            def setRowText(row, column, data):
                for index, value in enumerate(data):
                    table.setText(row, column, value)
                    column += 1
                    if label not in ('P', 'D'):
                        additionalInfo = ()
                        if self._keyFields[label][index] == 'SN':
                            additionalInfo = self._getAdditionalInfo('P', 'SN', value, self._clientsInfo)
                        elif self._keyFields[label][index] == 'DOC_TABN':
                            additionalInfo = self._getAdditionalInfo('D', 'DOC_TABN', value, self._doctorsInfo)
                        for value in additionalInfo:
                            table.setText(row, column, value)
                            column += 1
                return column

            # Формат для списков ошибок и примечаний
            listFormat = QtGui.QTextListFormat()
            listFormat.setStyle(QtGui.QTextListFormat.ListDisc)
            if self.rbGroupByData.isChecked():
                # keyValue - ошибочная запись
                # errorCodes -  список кодов ошибок
                for keyValue, errorCodes in sorted(data.iteritems(),
                                                   # Сортируем по первому полю записи
                                                   key=lambda item: int(item[0][0]) if item[0][0].isdigit()
                                                                                    else item[0][0]):
                    row = table.addRow()
                    column = 1
                    table.setText(row, 0, row)
                    column = setRowText(row, column, keyValue)
                    #  Вставляем два списка: ошибки и примечания
                    table.cursorAt(row, column).createList(listFormat)
                    cursorErrors = table.cursorAt(row, column)
                    table.cursorAt(row, column + 1).createList(listFormat)
                    cursorNotes = table.cursorAt(row, column + 1)
                    for errorCode in errorCodes:
                        cursorErrors.insertText(u'%s (%s)' % (errorCode, self._errorsInfo[errorCode][0]))
                        cursorErrors.insertBlock()
                        if self._errorsInfo[errorCode][1].strip():
                            cursorNotes.insertText(u'%s' % self._errorsInfo[errorCode][1])
                            cursorNotes.insertBlock()
                    cursorErrors.deletePreviousChar()
                    cursorNotes.deletePreviousChar()
                    if processCallBack:
                        processCallBack(label, row)
            else:
                # errorCode - код ошибки
                # keyValues - список ошибочных записей
                for errorIndex, (errorCode, keyValues) in enumerate(sorted(data.iteritems(),
                                                                           # Сортируем по кодам ошибок
                                                                           key=lambda item: item[0])):
                    row = table.addRow()
                    column = 3
                    table.setText(row, 0, errorIndex + 1)
                    table.setText(row, 1, u'%s (%s)' % (errorCode, self._errorsInfo[errorCode][0]))
                    table.setText(row, 2,
                                  u'%s' % self._errorsInfo[errorCode][1] if self._errorsInfo[errorCode][1].strip()
                                                                         else u'')
                    rowError = row
                    for index, keyValue in enumerate(sorted(keyValues,
                                                            # Сортируем по первому полю записи
                                                            key=lambda value: int(value[0]) if value[0].isdigit()
                                                                                            else value[0])):
                        if index:
                            row = table.addRow()
                        setRowText(row, column, keyValue)
                        if processCallBack:
                            processCallBack(label, row)
                    table.mergeCells(rowError, 0, len(keyValues), 1)
                    table.mergeCells(rowError, 1, len(keyValues), 1)
                    table.mergeCells(rowError, 2, len(keyValues), 1)

        # Вставляем заголовок таблицы
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Файл-реестра %s' % (label.upper() if not additionalTitle
                                                else u'%s (%s)' % (label.upper(), additionalTitle)))
        cursor.insertBlock()
        # Формируем столбцы таблицы и вставляем данные в таблицу
        insertData(createTable(cursor, getColumns()))
        # Вставляем пустые строки после таблицы
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()

    @QtCore.pyqtSignature('')
    def on_chkOnlyErrors_clicked(self):
        if self.chkOnlyErrors.isChecked():
            logErrors = [error for error in self._logErrorsCache if error[2]]  # 2 - isError == True
        else:
            logErrors = self._logErrorsCache
        self.tbChecks.clear()
        for errorCode, errorName, isError in logErrors:
            self._viewError(errorCode, errorName, isError, False)

    @QtCore.pyqtSignature('')
    def on_btnPrint_clicked(self):

        def processCallBack(label, step):
            QtGui.qApp.stepProgressBar()
            QtGui.qApp.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)

        errorsMax = 0
        errors = self._getErrors()
        if self.rbGroupByData.isChecked():
            # data = {label1: {keyValue1: [errorCodes1]}, label2: {keyValue2: [errorCodes2]}, ...}
            data = errors
            for keyValues in data.itervalues():
                errorsMax += len(keyValues)
        else:
            # data = {label1: {errorCode1: [keyValues]}, label2: {errorCode2: [keyValues2]}, ...}
            allErrorCodes = set()
            map(lambda errorCodes: allErrorCodes.update(errorCodes),
                [errorCodes for keyValues in errors.itervalues() for errorCodes in keyValues.itervalues()])
            data = {}
            for errorCode in allErrorCodes:
                for label, keyValues in errors.iteritems():
                    for keyValue, errorCodes in keyValues.iteritems():
                        if errorCode in errorCodes:
                            data.setdefault(label, {}).setdefault(errorCode, []).append(keyValue)
            for errorCodes in data.itervalues():
                for keyValues in errorCodes.itervalues():
                    errorsMax += len(keyValues)
        QtGui.qApp.startProgressBar(errorsMax)
        QtGui.qApp.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
        try:
            doc = QtGui.QTextDocument()
            doc.setIndentWidth(doc.indentWidth()/4.0)
            cursor = QtGui.QTextCursor(doc)
            for label in self._orderedLabels:
                if label in data:
                    self._toHtml(label, data[label], cursor, processCallBack=processCallBack)
                elif label == 'U':
                    for label in sorted([label for label in data.iterkeys() if isinstance(label, tuple) and
                                                                               label[0] == 'U'],
                                        key=lambda label: label[1]):
                        doctorInfo = self._getAdditionalInfo('D', 'DOC_TABN', label[1], self._doctorsInfo)
                        self._toHtml(label[0], data[label], cursor, additionalTitle=u'%s: %s %s %s' % (label[1],
                                                                                                       doctorInfo[0],
                                                                                                       doctorInfo[1],
                                                                                                       doctorInfo[2]),
                                     processCallBack=processCallBack)
            view = CReportViewDialog()
            view.setText(doc.toHtml())
            view.exec_()
        finally:
            QtGui.qApp.stopProgressBar()

    @QtCore.pyqtSignature('')
    def on_btnClose_clicked(self):
        self.close()