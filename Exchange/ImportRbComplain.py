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

from ExportRbComplain import rbComplainFields
from Ui_ImportRbComplain import Ui_ImportRbComplain


def ImportRbComplain(parent):
    fileName = forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportRbComplainFileName', ''))
    fullLog = forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'ImportRbComplainFullLog', ''))
    dlg = CImportRbComplain(fileName,  parent)
    dlg.chkFullLog.setChecked(fullLog)
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ImportRbComplainFileName'] = toVariant(dlg.fileName)
    QtGui.qApp.preferences.appPrefs['ImportRbComplainFullLog'] = toVariant(dlg.chkFullLog.isChecked())


class CMyXmlStreamReader(QXmlStreamReader):
    def __init__(self,  parent):
        QXmlStreamReader.__init__(self)
        self.parent = parent
        self.db=QtGui.qApp.db
        self.tableComplain = tbl('rbComplain')
        self.nadded = 0
        self.ncoincident = 0
        self.nprocessed = 0
        self.nupdated = 0
        self.mapComplainKeyToId = {}
        self.showLog = self.parent.chkFullLog.isChecked()
        self.recursionLevel = 0


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
                    if self.name() == "RbComplainExport":
                        if self.attributes().value("version") == xmlVersion:
                            self.readData()
                        else:
                            self.raiseError(u'Версия формата `%s` не поддерживается. Должна быть `%s`' \
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
        assert self.isStartElement() and self.name() == "RbComplainExport"

        while (not self.atEnd()):
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if (self.name() == "ComplainElement"):
                    self.readComplainElement()
                else:
                    self.readUnknownElement()

            if self.hasError() or self.parent.aborted:
                break


    def readComplainElement(self):
        assert self.isStartElement() and self.name() == "ComplainElement"

        groupId = None
        element = {}

        for x in rbComplainFields:
            element[x] = forceString(self.attributes().value(x).toString())

        while not self.atEnd():
            self.readNext()

            QtGui.qApp.processEvents()

            if self.isEndElement():
                break

            if self.isStartElement():
                if (self.name() == "group"):
                    groupId = self.readGroup()
                    element['group_id'] = groupId
                else:
                    self.readUnknownElement()

        name = element['name']
        code = element['code']
        self.log(u'Элемент: %s (%s)' %(name, code))
        id = self.lookupComplainElement(code, name, groupId)

        if self.hasError() or self.parent.aborted:
            return None

        if id:
            self.log(u'%% Найдена совпадающая запись (id=%d), пропускаем' % id)
            self.ncoincident += 1
        else:
            self.log(u'% Сходные записи не обнаружены. Добавляем')
            # новая запись, добавляем само действие и все его свойства + ед.изм.
            record = self.tableComplain.newRecord()

            for x in rbComplainFields:
                if element[x]:
                    record.setValue(x,  toVariant(element[x]))

            if groupId: # если есть группа, запишем её id
                record.setValue('group_id',  toVariant(groupId))


            id = self.db.insertRecord(self.tableComplain, record)
            self.mapComplainKeyToId[(code, name, groupId)] = id
            self.nadded += 1

        self.nprocessed += 1
        self.parent.statusLabel.setText(
                u'импорт типов действий: %d добавлено; %d обновлено; %d совпадений; %d обработано' % (self.nadded,
                                                                                                      self.nupdated,  self.ncoincident,  self.nprocessed))

        return id


    def readGroup(self):
        assert self.isStartElement() and self.name() == "group"

        group_id = None
        self.log(u'Группа:' )

        while not self.atEnd():
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if (self.name() == "ComplainElement"):
                    if self.recursionLevel < 10:
                        self.recursionLevel += 1
                        group_id = self.readComplainElement()
                        self.recursionLevel -= 1
                    else:
                        self.raiseError(u'Уровень вложенности групп больше 10')
                else:
                    self.readUnknownElement()

            if self.hasError() or self.parent.aborted:
                break

        return group_id


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


    def lookupComplainElement(self, code, name, group_id):

        key = (code, name, group_id)
        id = self.mapComplainKeyToId.get(key,  None)

        if id:
            return id

        cond = []
        cond.append(self.tableComplain['code'].eq(toVariant(code)))
        cond.append(self.tableComplain['name'].eq(toVariant(name)))

        if group_id:
            cond.append(self.tableComplain['group_id'].eq(toVariant(group_id)))

        record = self.db.getRecordEx(self.tableComplain, ['id'], where=cond)

        if record:
            id = forceRef(record.value('id'))
            self.mapComplainKeyToId[key] = id
            return id

        return None


class CImportRbComplain(QtGui.QDialog, Ui_ImportRbComplain):
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
            QtGui.QMessageBox.warning(self, u'Импорт справочника `Жалобы`',
                u'Не могу открыть файл для чтения %s:\n%s.' % (fileName,
                                                    inFile.errorString()))
        else:
            self.progressBar.reset()
            self.progressBar.setValue(0)
            self.progressBar.setFormat(u'%v байт')
            self.statusLabel.setText("")
            self.progressBar.setMaximum(max(inFile.size(), 1))
            myXmlStreamReader = CMyXmlStreamReader(self)
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
