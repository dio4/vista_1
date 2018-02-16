#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4 import QtCore
if 'QXmlStreamReader' in QtCore.__dict__:
    from PyQt4.QtCore import QXmlStreamReader

from Utils import *

from ExportRbResult import rbResultFields

from Ui_ImportRbResult_Wizard_1 import Ui_ImportRbResult_Wizard_1
from Ui_ImportRbResult_Wizard_2 import Ui_ImportRbResult_Wizard_2
from Ui_ImportRbResult_Wizard_3 import Ui_ImportRbResult_Wizard_3


rbResultRefFields = ('eventPurpose_id',  )

def ImportRbResult(parent):
    dlg = CImportRbResult(forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportRbResultFileName', '')),
        fullLog = forceBool(getVal(QtGui.qApp.preferences.appPrefs, \
            'ImportRbResultFullLog', 'False')),
        importAll = forceBool(getVal(QtGui.qApp.preferences.appPrefs, \
            'ImportRbResultImportAll', 'False')),
        parent=parent)
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ImportRbResultFileName'] \
        = toVariant(dlg.fileName)
    QtGui.qApp.preferences.appPrefs['ImportRbResultFullLog'] \
        = toVariant(dlg.fullLog)
    QtGui.qApp.preferences.appPrefs['ImportRbResultImportAll'] \
        = toVariant(dlg.importAll)


class CMyXmlStreamReader(QXmlStreamReader):
    def __init__(self,  parent,  showLog = False):
        QXmlStreamReader.__init__(self)
        self.parent = parent
        self.db=QtGui.qApp.db
        self.tableRbResult = tbl('rbResult')
        self.tablePurpose = tbl('rbEventTypePurpose')
        self.nadded = 0
        self.ncoincident = 0
        self.nprocessed = 0
        self.nupdated = 0
        self.mapPurposeKeyToId = {}
        self.mapRbResultKeyToId = {}
        self.showLog = showLog
        self.elementsList = []


    def raiseError(self,  str):
        QXmlStreamReader.raiseError(self, u'[%d:%d] %s' % (self.lineNumber(), self.columnNumber(), str))


    def readNext(self):
        QXmlStreamReader.readNext(self)
        self.parent.progressBar.setValue(self.device().pos())


    def log(self, str,  forceLog = False):
        if self.showLog or forceLog:
            self.parent.logBrowser.append(str)
            self.parent.logBrowser.update()


    def readFile(self, device,  filter = None, makeList = False):
        """ Разбирает и загружает xml из указанного устройства device
            если makeList == True - составляет список найденных
            элементов для загрузки"""

        self.setDevice(device)
        xmlVersion = "1.0"

        try:
            while (not self.atEnd()):
                self.readNext()

                if self.isStartElement():
                    if self.name() == "RbResultExport":
                        if self.attributes().value("version") == xmlVersion:
                            self.readData(filter,  makeList)
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


        return not self.hasError()


    def readData(self, filter,  makeList):
        assert self.isStartElement() and self.name() == "RbResultExport"

        # очищаем список событий перед заполнением
        if makeList:
            self.elementsList = []

        while (not self.atEnd()):
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if (self.name() == "Result"):
                    self.readResult(filter,  makeList)
                else:
                    self.readUnknownElement()

            if self.hasError() or self.parent.aborted:
                break


    def readResult(self,  filterList,  makeList):
        assert self.isStartElement() and self.name() == "Result"

        result = {}
        result['purpose']  = {}

        if self.parent.aborted:
            return None

        for x in rbResultFields:
            result[x] = forceString(self.attributes().value(x).toString())

        name = result['name']
        code = result['code']

        while not self.atEnd():
            QtGui.qApp.processEvents()
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if (self.name() == "EventTypePurpose"):
                    result['purpose'] = self.readEventTypePurpose()
                    if result['purpose'].has_key('id'):
                        result['eventPurpose_id'] = result['purpose']['id']
                else:
                    self.readUnknownElement(not makeList)

        if not result.has_key('eventPurpose_id'):
            result['eventPurpose_id'] = None

        if makeList:
            self.elementsList.append((code,  name,  result['eventPurpose_id']))
            self.log(u' Найден элемент: (%s) "%s" [%d]' % (code,  name,  \
                        result['eventPurpose_id'] if result['eventPurpose_id'] else -1))
            return None

        if filterList != []:
            if not ((code, name,  result['eventPurpose_id']) in filterList):
                return None

        id = self.lookupRbResult(result['eventPurpose_id'],  name,  code)
        self.log(u' Элемент: %s (%s)' %(name, code))

        if self.hasError() or self.parent.aborted:
            return None

        if id:
            self.log(u'%% Найдена похожая запись (id=%d)' % id)
            # такое действие уже есть. надо проверить все его свойства
            if not self.parent.parent.page(0).rbSkip.isChecked():
                if not self.isCoincidentResult(result,  id):
                    # есть разхождения в полях. спрашиваем у пользователя что делать
                    self.log(u' поля различаются')
                    if self.parent.parent.page(0).rbAskUser.isChecked():
                        self.log(u' Запрос действия пользователя: ')
                        if QtGui.QMessageBox.question(self.parent, u'Записи различаются',
                                                    self.prepareMessageBoxText(result, id) ,
                                                    QtGui.QMessageBox.No|QtGui.QMessageBox.Yes,
                                                    QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
                            self.log(u' - обновляем')
                            self.updateRbResult(result, id)
                        else:
                            self.log(u' - пропускаем')
                    elif self.parent.parent.page(0).rbUpdate.isChecked():
                        self.log(u' - обновляем')
                        self.updateRbResult(result,  id)
            else:
                self.log(u' - пропускаем')


            self.ncoincident += 1
        elif not result['eventPurpose_id']:
            self.log(u' Элемент: %s (%s) - код ("%s") назначения типа события'
                       u' не найден.\n Пропускаем.' %(name, code,  result['purpose'].get('code', '-')))
        else:
            self.log(u'% Сходные записи не обнаружены. Добавляем')
            # новая запись, добавляем само действие и все его свойства
            record = self.tableRbResult.newRecord()

            for x in rbResultFields + rbResultRefFields:
                if result.has_key(x) and result[x]:
                    record.setValue(x,  toVariant(result[x]))

            id = self.db.insertRecord(self.tableRbResult, record)
            self.nadded += 1

        self.nprocessed += 1
        self.parent.statusLabel.setText(
                u'импорт элементов: %d добавлено; %d обновлено; %d совпадений; %d обработано' % (self.nadded,
                                                                                                      self.nupdated,  self.ncoincident,  self.nprocessed))

        return id


    def readEventTypePurpose(self):
        assert self.isStartElement() and self.name() == "EventTypePurpose"
        purpose = {}

        for fieldName in ('code', ):
            purpose[fieldName] = forceString(self.attributes().value(fieldName).toString())

        #self.log(u'Назначение: код %s' %(purpose['code']))
        purpose['id'] = self.lookupPurpose(purpose['code'])

        while not self.atEnd():
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                self.readUnknownElement()

            if self.hasError() or self.parent.aborted:
               break

        return purpose


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

            if self.hasError() or self.parent.aborted:
                break


    def lookupPurpose(self, code):
        id = self.mapPurposeKeyToId.get(code,  None)

        if id:
            return id

        cond = []
        cond.append(self.tablePurpose['code'].eq(toVariant(code)))
        record = self.db.getRecordEx(self.tablePurpose, ['id'], where=cond)

        if record:
            id = forceRef(record.value('id'))
            self.mapPurposeKeyToId[code] = id
            return id

        return None


    def lookupRbResult(self, purposeId,  name,  code):
        key = (purposeId,  name,  code)
        id = self.mapRbResultKeyToId.get(key,  None)

        if id:
            return id

        cond = []
        cond.append(self.tableRbResult['code'].eq(code))
        cond.append(self.tableRbResult['name'].eq(name))
        cond.append(self.tableRbResult['eventPurpose_id'].eq(purposeId))
        record = self.db.getRecordEx(self.tableRbResult,  'id',  where=cond)

        if record:
            id = forceRef(record.value('id'))
            self.mapRbResultKeyToId[key] = id
            return id

        return None


    def isCoincidentResult(self,  result,  id):
        record = self.db.getRecord(self.tableRbResult, \
                                rbResultFields + rbResultRefFields, id)

        if record:
            for x in rbResultFields:
                if forceString(record.value(x)) != forceString(result[x]):
                    return False

            for x in rbResultRefFields:
                a = result.get(x, 0)
                b = forceInt(record.value(x))

                if (a or (b != 0)) and (forceInt(a) != b):
                    return False

            return True

        return False


    def prepareMessageBoxText(self, result, id):
        record = self.db.getRecord(self.tableRbResult, \
                                rbResultFields + rbResultRefFields, id)
        str = u"""<h3>Обнаружены следующие различия в записях:</h3>\n\n\n
                        <table>
                        <tr>
                            <td><b>Название поля</b></td>
                            <td align=center><b>Новое</b></td>
                            <td align=center><b>Исходное</b></td>
                        </tr>"""

        if record:
            for x in rbResultFields:
                str += "<tr><td><b> "+x+": </b></td>"

                if forceString(record.value(x)) != forceString(result[x]):
                    str += "<td align=center bgcolor=""red""> "
                else:
                    str += "<td align=center>"

                str += forceString(result[x])+" </td><td align=center>" \
                        + forceString(record.value(x)) + "</td></tr>\n"

            for x in rbResultRefFields:
                a = result.get(x, 0)
                b = forceInt(record.value(x))

                if a or (b != 0) :
                    if forceInt(a) != b:
                        str += "<tr><td><b> "+x+": </b></td><td align=center bgcolor=red>" \
                                + forceString(result.get(x, '0'))
                        str += " </td><td align=center>" + forceString(record.value(x)) \
                                + "</td></tr>\n"

            str += u'</table>\n\n<p align=center>Обновить?</p>'
        return str


    def updateRbResult(self,  result,  id):
        result['id'] = id
        record = self.db.getRecord(self.tableRbResult, rbResultFields + rbResultRefFields+('id',  ) , id)

        for x in rbResultFields + rbResultRefFields:
            val = result.get(x, None)
            if val:
                record.setValue(x, toVariant(val))
            else:
                record.setNull(x)

        self.db.updateRecord(self.tableRbResult, record)
        self.nupdated += 1


class CImportRbResultWizardPage1(QtGui.QWizardPage, Ui_ImportRbResult_Wizard_1):
    def __init__(self,  parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.parent = parent
        self.setTitle(u'Параметры загрузки')
        self.setSubTitle(u'Выбор источника импорта')
        self.isPreImportDone = False
        self.aborted = False
        self.setupUi(self)
        self.progressBar.reset()
        self.progressBar.setValue(0)
        self.edtFileName.setText(parent.fileName)
        self.chkFullLog.setChecked(parent.fullLog)
        self.connect(parent, QtCore.SIGNAL('rejected()'), self.abort)


    def isComplete(self):
        return self.edtFileName.text()!= ''


    def validatePage(self):
        self.import_()
        return self.isPreImportDone


    def abort(self):
        self.aborted = True


    def import_(self):
        self.isPreImportDone = False
        self.aborted = False
        success,  result = QtGui.qApp.call(self, self.doPreImport)

        if self.aborted or not success:
            self.progressBar.setText(u'Прервано')
        else:
            self.isPreImportDone = result


    def doPreImport(self):
        inFile = QtCore.QFile(self.parent.fileName)
        if not inFile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, u'Импорт справочника "Результаты События"',
                                      u'Не могу открыть файл для чтения %s:\n%s.' % \
                                      (self.parent.fileName, inFile.errorString()))
            return False
        else:
            self.progressBar.reset()
            self.progressBar.setValue(0)
            self.progressBar.setFormat(u'%v байт')
            self.statusLabel.setText(u'Составления списка элементов для загрузки')
            self.progressBar.setMaximum(max(inFile.size(), 1))
            myXmlStreamReader = CMyXmlStreamReader(self)
            if (myXmlStreamReader.readFile(inFile,  None,  True)):
                self.progressBar.setText(u'Готово')
                # сохраняем список найденных типов событий в предке
                self.parent.elementsList = myXmlStreamReader.elementsList
                self.statusLabel.setText(u'Найдено %d элементов для импорта' % \
                                                    len(self.parent.elementsList))
            else:
                self.progressBar.setText(u'Прервано')
                if self.aborted:
                    self.logBrowser.append(u'! Прервано пользователем.')
                else:
                    self.logBrowser.append(u'! Ошибка: файл %s, %s' % \
                        (self.parent.fileName, myXmlStreamReader.errorString()))
                return False

        return True

    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        self.parent.fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы XML (*.xml)')
        if self.parent.fileName != '' :
            self.edtFileName.setText(self.parent.fileName)
            self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot(QString)
    def on_edtFileName_textChanged(self,  text):
        self.emit(QtCore.SIGNAL('completeChanged()'))
        self.parent.fileName = str(text)


    @QtCore.pyqtSlot(bool)
    def on_chkFullLog_toggled(self,  checked):
        self.parent.fullLog = checked


class CImportRbResultWizardPage2(QtGui.QWizardPage, Ui_ImportRbResult_Wizard_2):
    def __init__(self,  parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.parent = parent
        self.setTitle(u'Параметры загрузки')
        self.setSubTitle(u'Выбор элементов для импорта')
        self.setupUi(self)
        self.chkImportAll.setChecked(parent.importAll)
        #self.postSetupUi()


    def isComplete(self):
        return self.parent.importAll or self.parent.selectedItems != []


    def initializePage(self):
        self.tblEvents.setRowCount(len(self.parent.elementsList))
        self.tblEvents.setColumnCount(3) # code, name
        self.tblEvents.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.tblEvents.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblEvents.setHorizontalHeaderLabels((u'Причина', u'Код',  u'Наименование'))
        self.tblEvents.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.tblEvents.horizontalHeader().setStretchLastSection(True)
        self.tblEvents.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.tblEvents.verticalHeader().hide()

        i = 0

        for x in self.parent.elementsList:
            purpose = forceString(QtGui.qApp.db.translate('rbEventTypePurpose', 'id', x[2], 'name'))
            purposeItem = QtGui.QTableWidgetItem(purpose)
            nameItem = QtGui.QTableWidgetItem(x[1])
            codeItem = QtGui.QTableWidgetItem(x[0])
            purposeItem.setFlags(QtCore.Qt.ItemIsSelectable |QtCore.Qt.ItemIsEnabled)
            purposeItem.setData(QtCore.Qt.UserRole, QVariant(x[2]))
            nameItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            codeItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.tblEvents.setItem(i, 0, purposeItem)
            self.tblEvents.setItem(i, 1,  codeItem)
            self.tblEvents.setItem(i, 2,  nameItem)
            i += 1

        self.tblEvents.sortItems(0)

    @QtCore.pyqtSlot(bool)
    def on_chkImportAll_toggled(self,  checked):
        self.parent.importAll = checked
        self.tblEvents.setEnabled(not checked)
        self.btnClearSelection.setEnabled(not checked)

        if checked:
            self.statusLabel.setText(u'Выбраны все элементы для импорта')
        else:
            self.statusLabel.setText(u'Выбрано %d элементов для импорта' % \
                                        len(self.parent.selectedItems))

        self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot()
    def on_tblEvents_itemSelectionChanged(self):
        self.parent.selectedItems = []
        rows = list(set([index.row() for index in self.tblEvents.selectedIndexes()]))
        for i in rows:
            code = forceString(self.tblEvents.item(i, 1).text())
            name = forceString(self.tblEvents.item(i, 2).text())
            purpose = forceRef(self.tblEvents.item(i, 0).data(QtCore.Qt.UserRole))
            self.parent.selectedItems.append((code, name,  purpose))

        self.statusLabel.setText(u'Выбрано %d элементов для импорта' % \
                                        len(self.parent.selectedItems))
        self.emit(QtCore.SIGNAL('completeChanged()'))


class CImportRbResultWizardPage3(QtGui.QWizardPage, Ui_ImportRbResult_Wizard_3):
    def __init__(self,  parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.parent = parent
        self.setTitle(u'Загрузка')
        self.setSubTitle(u'Импорт справочника "Результаты События"')
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


    def doImport(self):
        self.btnAbort.setEnabled(True)
        inFile = QtCore.QFile(self.parent.fileName)
        if not inFile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, u'Импорт справочника "Результаты События"',
                                      u'Не могу открыть файл для чтения %s:\n%s.' % \
                                      (self.parent.fileName, inFile.errorString()))
            return
        else:
            self.progressBar.reset()
            self.progressBar.setValue(0)
            self.progressBar.setFormat(u'%v байт')
            self.progressBar.setMaximum(max(inFile.size(), 1))
            myXmlStreamReader = CMyXmlStreamReader(self,  self.parent.fullLog)
            if (myXmlStreamReader.readFile(inFile,  self.parent.selectedItems)):
                self.progressBar.setText(u'Готово')
                self.isImportDone = True
                self.emit(QtCore.SIGNAL('completeChanged()'))
                self.btnAbort.setEnabled(False)
            else:
                self.progressBar.setText(u'Прервано')
                if self.aborted:
                    self.logBrowser.append(u'! Прервано пользователем.')
                else:
                    self.logBrowser.append(u'! Ошибка: файл %s, %s' % (self.parent.fileName, myXmlStreamReader.errorString()))


    @QtCore.pyqtSlot()
    def on_btnAbort_clicked(self):
        self.abort()



class CImportRbResult(QtGui.QWizard):
    def __init__(self, fileName = "",  importAll = False,  fullLog = False,  parent=None):
        QtGui.QWizard.__init__(self, parent, Qt.Dialog)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.setWindowTitle(u'Импорт справочника "Результаты События"')
        self.fullLog = fullLog
        self.importAll = importAll
        self.selectedItems = []
        self.elementsList =[]
        self.fileName= fileName
        self.addPage(CImportRbResultWizardPage1(self))
        self.addPage(CImportRbResultWizardPage2(self))
        self.addPage(CImportRbResultWizardPage3(self))
