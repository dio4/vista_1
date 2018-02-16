#!/usr/bin/env python
# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore
if 'QXmlStreamReader' in QtCore.__dict__:
    from PyQt4.QtCore import QXmlStreamReader

from Utils import *

from ExportRbService import rbServiceFields
from Ui_ImportRbService import Ui_ImportRbService


def ImportRbService(parent):
    fileName = forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportRbServiceFileName', ''))
    fullLog = forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'ImportRbServiceFullLog', ''))
    dlg = CImportRbService(fileName,  parent)
    dlg.chkFullLog.setChecked(fullLog)
    dlg.chkCompareOnlyByCode.setChecked(forceBool(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportRbServiceCompareOnlyByCode', False)))
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ImportRbServiceFileName'] = toVariant(dlg.fileName)
    QtGui.qApp.preferences.appPrefs['ImportRbServiceFullLog'] = toVariant(dlg.chkFullLog.isChecked())
    QtGui.qApp.preferences.appPrefs['ImportRbServiceCompareOnlyByCode'] =\
        toVariant(dlg.chkCompareOnlyByCode.isChecked())


class CMyXmlStreamReader(QXmlStreamReader):
    def __init__(self,  parent,  compareOnlyByCode):
        QXmlStreamReader.__init__(self)
        self.parent = parent
        self.db=QtGui.qApp.db
        self.table = tbl('rbService')
        self.nadded = 0
        self.ncoincident = 0
        self.nprocessed = 0
        self.nupdated = 0
        self.mapServiceKeyToId = {}
        self.showLog = self.parent.chkFullLog.isChecked()
        self.recursionLevel = 0
        self.compareOnlyByCode = compareOnlyByCode


    def raiseError(self,  str):
        QXmlStreamReader.raiseError(self, u'[%d:%d] %s' % (self.lineNumber(), self.columnNumber(), str))


    def readNext(self):
        QXmlStreamReader.readNext(self)
        self.parent.progressBar.setValue(self.device().pos())


    def log(self, str,  forceLog = False):
        if self.showLog or forceLog:
            self.parent.logBrowser.append(str)
            self.parent.logBrowser.update()


    def readFile(self, device):
        self.setDevice(device)
        xmlVersion = "1.00"

        try:
            while (not self.atEnd()):
                self.readNext()

                if self.isStartElement():
                    if self.name() == 'RbServiceExport':
                        if self.attributes().value('version') == xmlVersion:
                            self.readData()
                        else:
                            self.raiseError(u'Версия формата "%s" не поддерживается. Должна быть "%s"' \
                                % (self.attributes().value("version").toString(), xmlVersion))
                    else:
                        self.raiseError(u'Неверный формат экспорта данных.')

                if self.hasError() or self.parent.aborted:
                    return False

        except IOError, e:
            QtGui.qApp.logCurrentException()
            msg=''
            if hasattr(e, 'filename'):
                msg = u'%s:\n[Errno %s] %s' % (e.filename, e.errno, e.strerror)
            else:
                msg = u'[Errno %s] %s' % (e.errno, e.strerror)
            QtGui.QMessageBox.critical (self.parent,
                u'Произошла ошибка ввода-вывода', msg, QtGui.QMessageBox.Close)
            self.log(u'! Ошибка ввода-вывода: %s' % msg,  True)
            return False
        except Exception, e:
            QtGui.qApp.logCurrentException()
            QtGui.QMessageBox.critical (self.parent,
                u'Произошла ошибка', unicode(e), QtGui.QMessageBox.Close)
            self.log(u'! Ошибка: %s' % unicode(e),  True)
            return False


        return not (self.hasError() or self.parent.aborted)


    def readData(self):
        assert self.isStartElement() and self.name() == "RbServiceExport"

        while (not self.atEnd()):
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if (self.name() == "ServiceElement"):
                    self.readThesaurusElement()
                else:
                    self.readUnknownElement()

            if self.hasError() or self.parent.aborted:
                break


    def readThesaurusElement(self):
        assert self.isStartElement() and self.name() == "ServiceElement"

        groupId = None
        element = {}

        for x in rbServiceFields:
            element[x] = forceString(self.attributes().value(x).toString())

        while not self.atEnd():
            self.readNext()

            QtGui.qApp.processEvents()

            if self.isEndElement():
                break

            if self.isStartElement():
                self.readUnknownElement()

        name = element['name']
        code = element['code']
        self.log(u'Элемент: %s (%s)' %(name, code))
        id = self.lookupServiceElementByCode(code) if self.compareOnlyByCode \
            else self.lookupServiceElement(code, name)

        if self.hasError() or self.parent.aborted:
            return None

        if id:
            oldName = forceString(self.db.translate('rbService', 'id', id, 'name'))
            if oldName != name and QtGui.QMessageBox.question(self.parent, u'Внимание!',
                    u'Услуга с кодом "%s" уже есть в БД, но названия отличаются.\n'\
                    u'В БД: "%s",\n новое: "%s"\n Добавить как новую услугу?' % \
                    (code,  oldName, name),  QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
                    QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
                        id = self.lookupServiceElement(code, name)

        if id:
            self.log(u'%% Найдена совпадающая запись (id=%d), пропускаем' % id)
            self.ncoincident += 1
        else:
            self.log(u'% Сходные записи не обнаружены. Добавляем')
            # новая запись, добавляем само действие и все его свойства + ед.изм.
            record = self.table.newRecord()

            for x in rbServiceFields:
                if element[x]:
                    record.setValue(x,  toVariant(element[x]))

            id = self.db.insertRecord(self.table, record)
            self.mapServiceKeyToId[(code, name)] = id
            self.nadded += 1

        self.nprocessed += 1
        self.parent.statusLabel.setText(
                u'импорт типов действий: %d добавлено; %d обновлено; %d совпадений; %d обработано' % (self.nadded,
                                                                                                      self.nupdated,  self.ncoincident,  self.nprocessed))

        return id


    def readUnknownElement(self):
        assert self.isStartElement()
        self.log(u'Неизвестный элемент: '+self.name().toString())
        while (not self.atEnd()):
            self.readNext()
            if (self.isEndElement()):
                break
            if (self.isStartElement()):
                self.readUnknownElement()
            if self.hasError() or self.parent.aborted:
                break


    def lookupServiceElement(self, code, name):
        key = (code, name)
        id = self.mapServiceKeyToId.get(key,  None)

        if id:
            return id

        cond = []
        cond.append(self.table['code'].eq(toVariant(code)))
        cond.append(self.table['name'].eq(toVariant(name)))

        record = self.db.getRecordEx(self.table, ['id'], where=cond)
        if record:
            id = forceRef(record.value('id'))
            self.mapServiceKeyToId[key] = id
            return id

        return None


    def lookupServiceElementByCode(self, code):
        key = (code)
        id = self.mapServiceKeyToId.get(key,  None)

        if not id:
            record = self.db.getRecordEx(self.table, ['id'],
                where=[self.table['code'].eq(toVariant(code))])

            if record:
                id = forceRef(record.value('id'))
                self.mapServiceKeyToId[key] = id

        return id


class CImportRbService(QtGui.QDialog, Ui_ImportRbService):
    def __init__(self, fileName,  parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.progressBar.reset()
        self.progressBar.setValue(0)
        self.fileName = ''
        self.aborted = False
        self.connect(self, QtCore.SIGNAL('import()'), self.import_, Qt.QueuedConnection)
        self.connect(self, QtCore.SIGNAL('rejected()'), self.abort)
        if fileName != '' :
            self.edtFileName.setText(fileName)
            self.btnImport.setEnabled(True)
            self.fileName = fileName


    def abort(self):
        self.aborted = True


    def import_(self):
        self.aborted = False
        self.btnAbort.setEnabled(True)
        success,  result = QtGui.qApp.call(self, self.doImport)

        if self.aborted or not success:
            self.progressBar.setText(u'Прервано')

        self.btnAbort.setEnabled(False)


    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        self.fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы XML (*.xml)')
        if self.fileName != '' :
            self.edtFileName.setText(self.fileName)
            self.btnImport.setEnabled(True)


    @QtCore.pyqtSlot()
    def on_btnClose_clicked(self):
        self.close()


    @QtCore.pyqtSlot()
    def on_btnAbort_clicked(self):
        self.abort()


    @QtCore.pyqtSlot()
    def on_btnImport_clicked(self):
        self.emit(QtCore.SIGNAL('import()'))


    @QtCore.pyqtSlot(QString)
    def on_edtFileName_textChanged(self):
        self.fileName = self.edtFileName.text()
        self.btnImport.setEnabled(self.fileName != '')


    def doImport(self):
        fileName = self.edtFileName.text()

        if fileName.isEmpty():
            return

        inFile = QtCore.QFile(fileName)
        if not inFile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, u'Импорт справочника "Услуги"',
                                      QString(u'Не могу открыть файл для чтения %1:\n%2.')
                                      .arg(fileName)
                                      .arg(inFile.errorString()))
        else:
            self.progressBar.reset()
            self.progressBar.setValue(0)
            self.progressBar.setFormat(u'%v байт')
            self.statusLabel.setText('')
            self.progressBar.setMaximum(max(inFile.size(), 1))
            myXmlStreamReader = CMyXmlStreamReader(self, self.chkCompareOnlyByCode.isChecked())
            self.btnImport.setEnabled(False)
            if (myXmlStreamReader.readFile(inFile)):
                self.progressBar.setText(u'Готово')
            else:
                self.progressBar.setText(u'Прервано')
                if self.aborted:
                    self.logBrowser.append(u'! Прервано пользователем.')
                else:
                    self.logBrowser.append(u'! Ошибка: файл %s, %s' % (fileName, myXmlStreamReader.errorString()))
            self.edtFileName.setEnabled(False)
            self.btnSelectFile.setEnabled(False)
