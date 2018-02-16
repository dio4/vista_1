#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4 import QtCore
if 'QXmlStreamReader' in QtCore.__dict__:
    from PyQt4.QtCore import QXmlStreamReader

from Utils import *

from Ui_ImportNSI_Wizard_1 import Ui_ImportNSI_Wizard_1
from Ui_ImportNSI_Wizard_2 import Ui_ImportNSI_Wizard_2
from Ui_ImportNSI_Wizard_3 import Ui_ImportNSI_Wizard_3


def ImportNSI():
    dlg = CImportNSI(forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportNSIDirName', '')),
        fullLog = forceBool(getVal(QtGui.qApp.preferences.appPrefs, \
            'ImportNSIFullLog', 'False')),
        importAll = forceBool(getVal(QtGui.qApp.preferences.appPrefs, \
            'ImportNSIImportAll', 'False')))
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ImportNSIDirName'] \
        = toVariant(dlg.dirName)
    QtGui.qApp.preferences.appPrefs['ImportNSIFullLog'] \
        = toVariant(dlg.fullLog)
    QtGui.qApp.preferences.appPrefs['ImportNSIImportAll'] \
        = toVariant(dlg.importAll)


class CSharedStringsParser(QXmlStreamReader):
    def __init__(self,  parent,  showLog = False):
        QXmlStreamReader.__init__(self)
        self.parent = parent
        self.db=QtGui.qApp.db
        self.showLog = showLog
        self.sharedStrings = []

    def readNext(self):
        QXmlStreamReader.readNext(self)
        if hasattr(self.parent,  "progressBar"):
            self.parent.progressBar.setValue(self.device().pos())


    def raiseError(self,  str):
        QXmlStreamReader.raiseError(self, u'[%d:%d] %s' % (self.lineNumber(), self.columnNumber(), str))
        raise CException(u'Ошибка при разборе xml :[%d:%d] %s' % (self.lineNumber(), self.columnNumber(), str))


    def log(self, str,  forceLog = False):
        if (self.showLog or forceLog) and hasattr(self.parent, "logBrowser"):
            self.parent.logBrowser.append(str)
            self.parent.logBrowser.update()


    def readFile(self, device):
        """ Разбирает и загружает xml из указанного устройства device
            если makeEventsList == True - составляет список найденных
            в событий для загрузки"""

        self.setDevice(device)
        xmlns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
        self.sharedStrings = []

        while (not self.atEnd()):
            self.readNext()

            if self.isStartElement():
                if self.name() == "sst":
                        #if self.attributes().value("xmlns") == xmlns:
                    self.readData()
                        #else:
                         #   self.raiseError(u'Схема формата "%s" не поддерживается. Должна быть "%s"' \
                          #      % (self.attributes().value("xmlns").toString(), xmlns))
                else:
                    self.raiseError(u'Неверный формат данных. ожидается тег <sst>')

            if self.hasError():
                return False

        return not self.hasError()


    def readData(self):
        assert self.isStartElement() and self.name() == "sst"

        while (not self.atEnd()):
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if (self.name() == "si"):
                    self.readStringItem()
                else:
                    self.readUnknownElement()

            if self.hasError():
                break


    def readStringItem(self):
        assert self.isStartElement() and self.name() == "si"

        while (not self.atEnd()):
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if (self.name() == "t"):
                    self.readT()
                else:
                    self.readUnknownElement()

            if self.hasError():
                break


    def readT(self):
        assert self.isStartElement() and self.name() == "t"

        self.sharedStrings.append(forceString(self.readElementText()))


    def readUnknownElement(self, report = True):
        """ Читает неизвестный элемент, и сообщает об этом,
            если report ==True """

        assert self.isStartElement()

        if report:
            self.log(u'Неизвестный элемент: '+self.name().toString())

        while (not self.atEnd()):
            self.readNext()

            if (self.isEndElement()):
                break

            if (self.isStartElement()):
                self.readUnknownElement(report)

            if self.hasError():
                break


class CSheetParser(QXmlStreamReader):
    def __init__(self,  parent,  showLog = False):
        QXmlStreamReader.__init__(self)
        self.parent = parent
        self.db=QtGui.qApp.db
        self.showLog = showLog
        self.sheetData = {}
        self.currentCol = ""


    def readNext(self):
        QXmlStreamReader.readNext(self)
        if hasattr(self.parent,  "progressBar"):
            self.parent.progressBar.setValue(self.device().pos())


    def raiseError(self,  str):
        QXmlStreamReader.raiseError(self, u'[%d:%d] %s' % (self.lineNumber(), self.columnNumber(), str))
        raise CException(u'Ошибка при разборе xml :[%d:%d] %s' % (self.lineNumber(), self.columnNumber(), str))


    def log(self, str,  forceLog = False):
        if (self.showLog or forceLog) and hasattr(self.parent, "logBrowser"):
            self.parent.logBrowser.append(str)
            self.parent.logBrowser.update()


    def readFile(self, device):
        """ Разбирает и загружает xml из указанного устройства device
            если makeEventsList == True - составляет список найденных
            в событий для загрузки"""

        self.setDevice(device)
        xmlns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
        self.sharedStrings = []

        while (not self.atEnd()):
            self.readNext()

            if self.isStartElement():
                if self.name() == "worksheet":
                        #if self.attributes().value("xmlns") == xmlns:
                    self.readWorkSheet()
                        #else:
                         #   self.raiseError(u'Схема формата "%s" не поддерживается. Должна быть "%s"' \
                          #      % (self.attributes().value("xmlns").toString(), xmlns))
                else:
                    self.raiseError(u'Неверный формат данных. ожидается тег <sst>')

            if self.hasError():
                return False

        return not self.hasError()


    def readWorkSheet(self):
        assert self.isStartElement() and self.name() == "worksheet"

        while (not self.atEnd()):
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if (self.name() == "sheetData"):
                    self.readSheetData()
                elif self.name() == "sheetViews":
                    self.readSheetViews()
                elif self.name() == "cols":
                    self.readCols()
                elif self.name() in ("dimension", "sheetFormatPr", \
                    "pageMargins", "pageSetup", "headerFooter",
                    "phoneticPr"):
                    self.readNext() # пропускаем
                else:
                    self.readUnknownElement()

            if self.hasError():
                break


    def readCols(self):
        assert self.isStartElement() and self.name() == "cols"

        while (not self.atEnd()):
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if (self.name() == "col"):
                    self.readUnknownElement(False)
                else:
                    self.readUnknownElement()

            if self.hasError():
                break


    def readSheetViews(self):
        assert self.isStartElement() and self.name() == "sheetViews"

        while (not self.atEnd()):
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if (self.name() == "sheetView"):
                    self.readUnknownElement(False)
                else:
                    self.readUnknownElement()

            if self.hasError():
                break

    def readSheetData(self):
        assert self.isStartElement() and self.name() == "sheetData"

        while (not self.atEnd()):
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if (self.name() == "row"):
                    self.readRow()
                else:
                    self.readUnknownElement()

            if self.hasError():
                break


    def readRow(self):
        assert self.isStartElement() and self.name() == "row"

        while (not self.atEnd()):
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if (self.name() == "c"):
                    self.readC()
                else:
                    self.readUnknownElement()

            if self.hasError():
                break


    def readC(self):
        assert self.isStartElement() and self.name() == "c"
        currentCol = forceString(self.attributes().value("r").toString())

        while (not self.atEnd()):
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if (self.name() == "v"):
                    self.sheetData[currentCol] = forceInt(self.readElementText())
                else:
                    self.readUnknownElement()

            if self.hasError():
                break



    def readUnknownElement(self, report = True):
        """ Читает неизвестный элемент, и сообщает об этом,
            если report ==True """

        assert self.isStartElement()

        if report:
            self.log(u'Неизвестный элемент: '+self.name().toString())

        while (not self.atEnd()):
            self.readNext()

            if (self.isEndElement()):
                break

            if (self.isStartElement()):
                self.readUnknownElement(report)

            if self.hasError():
                break


class CImportNSIWizardPage1(QtGui.QWizardPage, Ui_ImportNSI_Wizard_1):
    def __init__(self,  parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.parent = parent
        self.setTitle(u'Параметры загрузки')
        self.setSubTitle(u'Выбор источника импорта')
        self.isPreImportDone = False
        self.setupUi(self)
        self.edtDirName.setText(parent.dirName)
        self.chkFullLog.setChecked(parent.fullLog)


    def isComplete(self):
        return self.edtDirName.text()!= ''


    def validatePage(self):
        if not self.isPreImportDone:
            self.import_()
        return self.isPreImportDone


    def import_(self):
        self.isPreImportDone = self.doPreImport()


    def doPreImport(self):
        self.log(u'* Поиск справочников НСИ в каталоге: "%s"' % self.edtDirName.text())
        dir = QtCore.QDir(self.edtDirName.text())
        listFiles = dir.entryList(QtCore.QStringList("*.xlsx"),  QtCore.QDir.Files)
        self.parent.listFiles = []
        if listFiles.count() > 0:
            self.log(u'- Найдено файлов: %d' % listFiles.count())
            for s in listFiles:
                self.log(u'  "%s"'%forceString(s))
                self.parent.listFiles.append(forceString(dir.absoluteFilePath(s)))
            return True
        else:
            self.log(u'! Файлов со справочниками не обнаружено')
            return False


    def log(self, str,  forceLog = False):
        if self.chkFullLog.isChecked() or forceLog:
            self.logBrowser.append(str)
            self.logBrowser.update()


    @QtCore.pyqtSlot()
    def on_btnSelectDir_clicked(self):
        self.parent.dirName = QtGui.QFileDialog.getExistingDirectory(
            self, u'Укажите директорию со справочниками', self.edtDirName.text())
        if self.parent.dirName != '' :
            self.edtDirName.setText(self.parent.dirName)
            self.import_()
            self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot(QString)
    def on_edtFileName_textChanged(self,  text):
        self.parent.dirName = str(text)
        if self.parent.dirName != "":
            self._import()
        self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot(bool)
    def on_chkFullLog_toggled(self,  checked):
        self.parent.fullLog = checked


class CImportNSIWizardPage2(QtGui.QWizardPage, Ui_ImportNSI_Wizard_2):
    def __init__(self,  parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.parent = parent
        self.setTitle(u'Параметры загрузки')
        self.setSubTitle(u'Выбор справочников для импорта')
        self.setupUi(self)
        self.chkImportAll.setChecked(parent.importAll)
        #self.postSetupUi()


    def isComplete(self):
        return self.parent.importAll or self.parent.listFiles != []


    def initializePage(self):
        self.tblEvents.setRowCount(len(self.parent.listFiles))
        self.tblEvents.setColumnCount(5)
        self.tblEvents.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.tblEvents.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblEvents.setHorizontalHeaderLabels((u'Дата',  u'Наименование',  u'ОИД',  u'Версия',  u'Автор'))
        self.tblEvents.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.tblEvents.horizontalHeader().setStretchLastSection(True)
        self.tblEvents.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.tblEvents.verticalHeader().hide()

        i = 0

        try:

            for x in self.parent.listFiles:
                info = self.getNSIMetaInfo(x)
                if info:
                    eventDateItem = QtGui.QTableWidgetItem(info[0])
                    eventNameItem = QtGui.QTableWidgetItem(info[1])
                    eventOIDItem = QtGui.QTableWidgetItem(info[2])
                    eventVerItem = QtGui.QTableWidgetItem(info[3])
                    eventAuthorItem = QtGui.QTableWidgetItem(info[4])
                    eventDateItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                    eventNameItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                    eventOIDItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                    eventVerItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                    eventAuthorItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                    self.tblEvents.setItem(i, 0,  eventDateItem)
                    self.tblEvents.setItem(i, 1,  eventNameItem)
                    self.tblEvents.setItem(i, 2,  eventOIDItem)
                    self.tblEvents.setItem(i, 3,  eventVerItem)
                    self.tblEvents.setItem(i, 4,  eventAuthorItem)
                    i += 1

        except IOError, e:
            QtGui.qApp.logCurrentException()
            msg=''
            if hasattr(e, 'filename'):
                msg = u'%s:\n[Errno %s] %s' % (e.filename, e.errno, e.strerror)
            else:
                msg = u'[Errno %s] %s' % (e.errno, e.strerror)
            QtGui.QMessageBox.critical (self.parent,
                u'Произошла ошибка ввода-вывода', msg, QtGui.QMessageBox.Close)
            return False
        except Exception, e:
            QtGui.qApp.logCurrentException()
            QtGui.QMessageBox.critical (self.parent,
                u'Произошла ошибка', unicode(e), QtGui.QMessageBox.Close)
            return False


    def getNSIMetaInfo(self,  fileName):

        if is_zipfile(fileName):
            archive = ZipFile(fileName, "r")
            names = archive.namelist()
            for f in requiredFiles:
                if f not in names:
                    raise CException(u'Справочник: "%s"\nОтсутствует необходимый файл: "%s"' %\
                        (fileName, f))

            sharedStringsFile = extractToTempFile(archive,  requiredFiles[0])
            sharedStringsFile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text) # fixit
            parser = CSharedStringsParser(self)
            parser.readFile(sharedStringsFile)
            sharedStringsFile.close()

            sharedString = parser.sharedStrings
            metadataSheet = extractToTempFile(archive,  requiredFiles[1])
            metadataSheet.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text) # fixit
            SheetParser = CSheetParser(self)
            SheetParser.readFile(metadataSheet)

            metadata = SheetParser.sheetData

            ref = metadata.get("B2") # OID
            OID = sharedString[ref] if ref else ""

            ref = metadata.get("B5") # name
            name = sharedString[ref] if ref else ""

            ref = metadata.get("B4") # ver
            version = sharedString[ref] if ref else ""

            ref = metadata.get("B14") # date
            date = sharedString[ref] if ref else ""

            ref = metadata.get("B12") # author
            author = sharedString[ref] if ref else ""

            archive.close()
            return (date,  name,  OID,  version,  author)

        return None

    @QtCore.pyqtSlot(bool)
    def on_chkImportAll_toggled(self,  checked):
        self.parent.importAll = checked
        self.tblEvents.setEnabled(not checked)
        self.btnClearSelection.setEnabled(not checked)

        if checked:
            self.statusLabel.setText(u'Выбраны все справочники для импорта')
        else:
            self.statusLabel.setText(u'Справочников для импорта выбрано: %d' % \
                                        (len(self.parent.selectedFiles)/5))

        self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot()
    def on_tblEvents_itemSelectionChanged(self):
        self.parent.selectedFiles = self.tblEvents.selectedIndexes()
        self.statusLabel.setText(u'Справочников для импорта выбрано: %d' % \
                                        (len(self.parent.selectedFiles)/5))
        self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot()
    def on_btnClearSelection_clicked(self):
        self.parent.selectedFiles = []
        self.tblEvents.clearSelection()


class CImportNSIWizardPage3(QtGui.QWizardPage, Ui_ImportNSI_Wizard_3):
    def __init__(self,  parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.parent = parent
        self.setTitle(u'Загрузка')
        self.setSubTitle(u'Импорт типов событий')
        self.setupUi(self)
        self.isImportDone = False
        self.aborted = False
        self.connect(self, QtCore.SIGNAL('import()'), self.import_, Qt.QueuedConnection)
        self.connect(parent, QtCore.SIGNAL('rejected()'), self.abort)


    def isComplete(self):
        return self.isImportDone


    def initializePage(self):
        self.emit(QtCore.SIGNAL('import()'))


    def abort(self):
        self.aborted = True


    def import_(self):
        self.isImportDone = False
        self.aborted = False
        success,  result = QtGui.qApp.call(self, self.doImport)

        if self.aborted or not success:
            self.progressBar.setText(u'Прервано')


    def cleanupPage(self):
        self.progressBar.reset()
        self.progressBar.setValue(0)
        self.progressBar.setFormat(u'%v байт')


    def doImport(self):
        self.progressBar.reset()
        self.progressBar.setValue(0)
        self.progressBar.setFormat(u'%v байт')
        nLoaded = 0

        for fileName in self.parent.listFiles:
            if is_zipfile(fileName):
                self.log(u'* Импорт справочника: "%s"' % fileName)
                archive = ZipFile(fileName, "r")
                names = archive.namelist()
                for f in requiredFiles:
                    if f not in names:
                        raise CException(u'Справочник: "%s"\nОтсутствует необходимый файл: "%s"' %\
                            (fileName, f))

                self.log(u'+ Распаковка')
                sharedStringsFile = extractToTempFile(archive,  requiredFiles[0])
                sharedStringsFile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text) # fixit
                parser = CSharedStringsParser(self)
                self.progressBar.setValue(0)
                self.progressBar.setMaximum(max(sharedStringsFile.size(), 1))
                self.log(u'+ Чтение кэша строк')
                parser.readFile(sharedStringsFile)
                sharedStringsFile.close()
                sharedString = parser.sharedStrings

                metadataSheet = extractToTempFile(archive,  requiredFiles[1])
                metadataSheet.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text) # fixit
                SheetParser = CSheetParser(self)
                self.progressBar.setValue(0)
                self.progressBar.setMaximum(max(metadataSheet.size(), 1))
                self.log(u'+ Чтение метаданных')
                SheetParser.readFile(metadataSheet)

                metadata = SheetParser.sheetData

                dataSheet = extractToTempFile(archive,  requiredFiles[1])
                dataSheet.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text) # fixit
                dataSheetParser = CSheetParser(self)
                self.progressBar.setValue(0)
                self.progressBar.setMaximum(max(dataSheet.size(), 1))
                self.log(u'+ Чтение данных')
                dataSheetParser.readFile(dataSheet)

                data = dataSheetParser.sheetData

                ref = metadata.get("B2") # OID
                OID = sharedString[ref] if ref else ""

                ref = metadata.get("B5") # name
                name = sharedString[ref] if ref else ""

                ref = metadata.get("B4") # ver
                version = sharedString[ref] if ref else ""

                ref = metadata.get("B14") # date
                date = sharedString[ref] if ref else ""

                ref = metadata.get("B12") # author
                author = sharedString[ref] if ref else ""

                archive.close()
                self.log(u'+ Успешно импортировано %d элементов' % len(data))
                nLoaded += len(data)

            else:
                self.progressBar.setText(u'Прервано')
                if self.aborted:
                    self.logBrowser.append(u'! Прервано пользователем.')
                else:
                    self.logBrowser.append(u'! Ошибка: файл %s, %s' % (fileName))#, myXmlStreamReader.errorString()))

        self.progressBar.setText(u'Готово')
        self.isImportDone = True
        self.emit(QtCore.SIGNAL('completeChanged()'))
        self.statusLabel.setText(u'Загружено %d элементов' % nLoaded)
        self.btnAbort.setEnabled(False)


    @QtCore.pyqtSlot()
    def on_btnAbort_clicked(self):
        self.abort()


    def log(self, str,  forceLog = False):
        if self.parent.fullLog or forceLog:
            self.logBrowser.append(str)
            self.logBrowser.update()


class CImportNSI(QtGui.QWizard):
    def __init__(self, dirName = "",  importAll = False,  fullLog = False,  parent=None):
        QtGui.QWizard.__init__(self, parent, Qt.Dialog)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.setWindowTitle(u'Импорт справочников НСИ')
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.fullLog = fullLog
        self.importAll = importAll
        self.listFiles =[]
        self.selectedFiles = []
        self.dirName= dirName
        self.addPage(CImportNSIWizardPage1(self))
        self.addPage(CImportNSIWizardPage2(self))
        self.addPage(CImportNSIWizardPage3(self))


def extractToTempFile(zipFile,  fileToExtract):
    """ Распаковывает из архива zipFile(тип ZipFile) файл fileToExtract
        Возвращает QTemporaryFile"""

    outFile = QtCore.QTemporaryFile()

    if not outFile.open(QtCore.QFile.WriteOnly):
        raise CException(u'Экспорт сведений о сотрудниках',
            u'Не могу открыть файл для записи %s:\n%s.' % \
             (outFile, outFile.errorString()))

    data = zipFile.read(fileToExtract) #read the binary data
    outFile.write(data)
    outFile.close()
    return outFile

requiredFiles = ("xl/sharedStrings.xml",  "xl/worksheets/sheet1.xml",  \
    "xl/worksheets/sheet2.xml")
