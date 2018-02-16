# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################
from library.Utils     import *

from Exchange.Cimport import CXMLimport
from Ui_ImportRefBooks import Ui_Dialog

# TODO: реализовать разные режимы обновления (пропуск, обновление, спросить)
# TODO: Добавить возможность выбора ключевого поля.

def importDiagnosticResult(widget):
    dlg = CImportDiagnosticResult()
    dlg.edtFileName.setText(forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportDiagnosticResultFileName', '')))
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ImportDiagnosticResultFileName'] = toVariant(dlg.edtFileName.text())



class CImportDiagnosticResult(QtGui.QDialog, Ui_Dialog, CXMLimport):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        CXMLimport.__init__(self, self.log)

        self.checkName()
        self.nProcessed = 0
        self.nUpdated = 0
        self.nAdded = 0

        self.mapPurposeCodeToId = {}
        self.mapResultCodeToId = {}



#----------- Prepare form, process signals --------------

    @pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы XML (DR*.xml)')
        if fileName != '':
            self.edtFileName.setText(QtCore.QDir.toNativeSeparators(fileName))
            self.btnImport.setEnabled(True)

#---------------------- Utils ----------------------------
    def attributes(self):
        return self._xmlReader.attributes()

    def err2log(self, e):
        self.log.append(e)

    def getResultIdByCode(self, code):
        resultId = self.mapResultCodeToId.get(code, None)
        if resultId is None:
            resultId = forceRef(QtGui.qApp.db.translate('rbResult', 'code', code, 'id'))
            self.mapResultCodeToId[code] = resultId
        return resultId

    def getPurposeIdByCode(self, code):
        purposeId = self.mapPurposeCodeToId.get(code, None)
        if purposeId is None:
            purposeId = forceRef(QtGui.qApp.db.translate('rbEventTypePurpose', 'code', code, 'id'))
            self.mapPurposeCodeToId[code] = purposeId
        return purposeId


#----------------- Parsing xml file ------------------------
    def startImport(self):
        """
            Отображение процесса импорта, вызов соответствующих функций.
        """
        self.nProcessed = 0
        self.nAdded = 0
        self.nUpdated = 0
        fileName = forceStringEx(self.edtFileName.text())

        inFile = QtCore.QFile(fileName)
        fn = QtCore.QFileInfo(fileName)
        self.filename = fn.baseName()

        if not inFile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, u'Импорт данных из XML',
                                  u'Не могу открыть файл для чтения %s:\n%s.' \
                                  % (fileName, inFile.errorString()))
            return

        self.progressBar.reset()
        self.progressBar.setValue(0)
        size = inFile.size()
        self.progressBar.setMaximum(size)
        self.progressBar.setFormat(u'%v байт')

        self.labelNum.setText(u'размер источника: '+str(size))
        self.btnImport.setEnabled(False)

        if (not self.readFile(inFile)):
            if self.abort:
                self.err2log(u'! Прервано пользователем.')
            else:
                self.err2log(u'! Ошибка: файл %s, %s' % (fileName,
                                            self.errorString()))

        self.stat.setText(
            u'обработано: %d' % \
            (self.nProcessed))
        self.err2log(u'Обработано записей: %d.' % self.nProcessed)
        self.err2log(u'Обновлено записей: %d.' % self.nUpdated)
        self.err2log(u'Добавлено записей: %d.' % self.nAdded)


    def readFile(self, device):
        """
            Обработка импортируемого файла
        """
        self.setDevice(device)

        while (not self.atEnd()):
            self.readNext()

            if self.isStartElement():
                if self.name() == 'DIAGNOSTIC_RESULT_LIST':
                    self.processDiagnosticResults()
                else:
                    self.err2log(u'Ошибка в структуре XML-файла. Импорт прерван.')
                    return False
            elif self.isEndElement():
                return True


            if self.hasError():
                self.err2log(u'Ошибка в XML-файле. Импорт прерван.')
                return False

        return True


    def processDiagnosticResults(self):
        state = 0
        db = QtGui.qApp.db
        table = db.table('rbDiagnosticResult')
        while not self.atEnd():
            self.readNext()
            if self.isStartElement() and state == 0:
                if self.name() == 'DiagnosticResult':
                    self.nProcessed += 1
                    state = 1
                    recordDict = {}
                    for attr in self.attributes():
                        recordDict[forceString(attr.name())] = forceString(attr.value())
                    if not recordDict.get('code', None):
                        self.err2log(u'Для результата "%s" не задан код. Пропускаем.' % recordDict.get('name', ''))
                        continue

                    resultId = self.getResultIdByCode(recordDict['resultCode'])
                    purposeId = self.getPurposeIdByCode(recordDict['purposeCode'])
                    if not purposeId:
                        self.err2log(u'Для результата "%s" не найдено назначение обращения. Пропускаем.' % recordDict.get('name', ''))
                        continue
                    record = db.getRecordEx(table, '*', [table['code'].eq(recordDict['code']), table['result_id'].eq(resultId), table['eventPurpose_id'].eq(purposeId)])
                    isNew = False
                    if not record:
                        record = table.newRecord()
                        isNew = True
                    for field, value in recordDict.items():
                        if field == 'resultCode':
                            record.setValue('result_id', toVariant(resultId))
                        elif field == 'purposeCode':
                            record.setValue('eventPurpose_id', toVariant(purposeId))
                        else:
                            record.setValue(field, toVariant(value))
                    db.insertOrUpdate(table, record)
                    if isNew:
                        self.nAdded += 1
                    else:
                        self.nUpdated += 1
                else:
                    self.err2log(u'Ошибка в XML-файле. Неизвестный элемент %s. Импорт прерван.' % self.name())
                    return False
            elif self.isEndElement():
                if state == 0:
                    return True
                elif state == 1:
                    state = 0
