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

from library.Utils import *
from Utils         import tbl
from Events.EditDispatcher import getEventFormClassByType

from Ui_Import131Errors import Ui_Import131ErrorsDialog


def Import131Errors(widget):
    dlg = CImport131Errors(widget)
    dlg.edtImportFrom.setText(forceString(QtGui.qApp.preferences.appPrefs.get('Import131ErrorsFileName', '')))
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['Import131ErrorsFileName'] = toVariant(dlg.edtImportFrom.text())


class CXmlReading:
    def __init__(self):
        self._xmlReader = QXmlStreamReader()

    def readNext(self):
        return self._xmlReader.readNext()

    def atEnd(self):
        return self._xmlReader.atEnd()

    def name(self):
        return self._xmlReader.name()

    def readElementText(self):
        return self._xmlReader.readElementText()

    def isStartElement(self):
        return self._xmlReader.isStartElement()

    def isEndElement(self):
        return self._xmlReader.isEndElement()


class CImport131Errors(QtGui.QDialog, CXmlReading, Ui_Import131ErrorsDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        CXmlReading.__init__(self)
        self.setupUi(self)
        self.errorsDict     = {}
        self.eventErrors    = {}
        self.items          = {}
        self.logRows        = 0
        self.errCount       = 0
        self.checkRun       = False
        self.abort          = False
        self.tableEvent     = tbl('Event')
        self.tableEventType = tbl('EventType')
        self.tableClient    = tbl('Client')
        self.progressBar.setFormat('%v')
        self.progressBar.setValue(0)


    def startImport(self):
        self.btnClose.setText(u'прервать')
        self.btnImport.setEnabled(False)
        self.abort    = False
        self.checkRun = True
        fileName = forceStringEx(self.edtImportFrom.text())
        _file = QtCore.QFile(fileName)
        if not _file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, u'Импорт протокола ошибок',
                                      u'Не могу открыть файл для чтения %s:\n%s.' \
                                      % (fileName, _file.errorString()))
        else:
            self.readFile(_file)
            self.lblCount.setText(u'всего записей в источнике: %d'%self.errCount)
            self.importErrors()
            self.progressBar.setText(u'прервано' if self.abort else u'готово')
            self.btnClose.setText(u'закрыть')
            self.abort    = False
            self.checkRun = False
            self.btnImport.setEnabled(True)


    def importErrors(self):
        self.progressBar.setMaximum(self.errCount)
        doneCount = 0
        for eventId in self.eventErrors.keys():
            for errCode in self.eventErrors[eventId]:
                QtGui.qApp.processEvents()
                if self.abort:
                    break
                self.addToLog(eventId, errCode)
                doneCount += 1
                self.lblDone.setText(u'Импортировано: %d'%doneCount)
                self.progressBar.setValue(doneCount)


    def readFile(self, _file):
        self._xmlReader.setDevice(_file)
        while (not self.atEnd()):
            self.readNext()
            if self.isStartElement():
                if u'Справочник' in self.name().toString():
                    self.addErrorInDict()
                if u'Протокол' in self.name().toString():
                    self.addEventIntDict()


    def addErrorInDict(self):
        if (self.isStartElement() and u'Справочник' in self.name().toString()):
            while (not self.atEnd()):
                self.readNext()
                if self.isEndElement():
                    break
                if self.isStartElement():
                    errCode = None
                    if 'Err_code' in self.name().toString():
                        errCode = self.readElementText()
                    if errCode:
                        errName = self.getErrName()
                        self.errorsDict[errCode] = errName


    def getErrName(self):
        if (u'Err_code' in self.name().toString()):
            while (not self.atEnd()):
                self.readNext()
                if self.isEndElement():
                    break
                if self.isStartElement():
                    if 'Err_name' in self.name().toString():
                        return self.readElementText()


    def addEventIntDict(self):
        if (self.isStartElement() and u'Протокол' in self.name().toString()):
            while (not self.atEnd()):
                self.readNext()
                if self.isEndElement():
                    break
                if self.isStartElement():
                    eventId = None
                    if u'ID' in self.name().toString():
                        eventId = forceInt(self.readElementText())
                    if eventId:
                        errCode = self.getErrCode()
                        existEvent = self.eventErrors.get(eventId, None)
                        if not existEvent:
                            self.eventErrors[eventId] = [errCode]
                        else:
                            self.eventErrors[eventId] += [errCode]
                        self.errCount += 1


    def getErrCode(self):
        if (u'ID' in self.name().toString()):
            while (not self.atEnd()):
                self.readNext()
                if self.isEndElement():
                    break
                if self.isStartElement():
                    if 'ERR_C' in self.name().toString():
                        return self.readElementText()


    def addToLog(self, eventId, errCode):
        db = QtGui.qApp.db
        eventRecord   = db.getRecordEx(self.tableEvent, '*', self.tableEvent['id'].eq(eventId))
        allRight    = True
        eventTypeId = None
        if eventRecord:
            clientId      = forceInt(eventRecord.value('client_id'))
            eventTypeId   = forceInt(eventRecord.value('eventType_id'))
            setDate       = forceString(eventRecord.value('setDate'))
            execDate      = forceString(eventRecord.value('execDate'))

            nameEventType = db.translate(self.tableEventType, 'id', eventTypeId, 'name')
            clientRecord  = db.getRecordEx(self.tableClient, '*', self.tableClient['id'].eq(clientId))
            if clientRecord:
                lastName      = forceString(clientRecord.value('lastName'))
                firstName     = forceString(clientRecord.value('firstName'))
                patrName      = forceString(clientRecord.value('patrName'))
                birthDate     = forceString(clientRecord.value('birthDate'))
                logMessage = u'%s, %s %s. %s. д.р. %s - %s' %(errCode,
                                                              lastName,
                                                              firstName[:1],
                                                              patrName[:1],
                                                              birthDate,
                                                              self.errorsDict[errCode])
            else:
                logMessage = u'клиент события %d не найден!'% eventId
                allRight = False
        else:
            logMessage = u'событие с id %d не найдено!'% eventId
            allRight = False
        self.logList.addItem(logMessage)
        self.items[self.logRows] = (eventTypeId, eventId, allRight)
        item = self.logList.item(self.logRows)
        self.logList.scrollToItem(item)
        self.logRows += 1


    def openItem(self, eventInfo):
        eventTypeId = eventInfo[0]
        eventId     = eventInfo[1]
        if eventInfo[2]:
            formClass = self.getEventFormClass(eventTypeId)
            form = formClass(self)
            form.load(eventId)
            return form
        return None


    def getEventFormClass(self, eventTypeId):
        return getEventFormClassByType(eventTypeId)


    @QtCore.pyqtSlot()
    def on_btnImportFrom_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtImportFrom.text(), u'Файлы XML (*.xml)')
        if fileName:
            self.edtImportFrom.setText(QtCore.QDir.toNativeSeparators(fileName))


    @QtCore.pyqtSlot()
    def on_btnImport_clicked(self):
        self.startImport()


    @QtCore.pyqtSlot()
    def on_btnClose_clicked(self):
        if self.checkRun:
            self.abort = True
        else:
            self.close()


    @QtCore.pyqtSlot(QModelIndex)
    def on_logList_doubleClicked(self, index):
        row = self.logList.currentRow()
        eventInfo = self.items[row]
        if eventInfo:
            dlg = self.openItem(eventInfo)
            if dlg:
                dlg.exec_()