# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
##############################################################################
from zipfile import is_zipfile, ZipFile
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QDateTime
from Exchange.Cimport import CDBFimport, CImport
from Exchange.R23.recipes.Ui_ImportFormularyDLOMiac import Ui_ImportFormularyDLOMiacDialog
from Exchange.XLSXReader import CXLSXReader
from library.DialogBase import CConstructHelperMixin
from library.Utils import forceString, toVariant, getPref, getClassName, setPref


def ImportFormularyDLOMiac(widget):
    dlg = CImportFormularyDLOMiac(widget)
    params = getPref(QtGui.qApp.preferences.appPrefs, getClassName(dlg), {})
    dlg.setParams(params)
    dlg.exec_()
    setPref(QtGui.qApp.preferences.appPrefs, getClassName(dlg), dlg.params())

class CImportFormularyDLOMiac(QtGui.QDialog, CConstructHelperMixin, Ui_ImportFormularyDLOMiacDialog, CDBFimport):

    tables = {
        'dlo_rbMNN': {
            'filename': 'Mnn.xlsx',
            'miacCode': 'MnnCode',
            'name': 'MnnName',
            'latinName': 'NameLat',
            'matchFields': ['name', 'latinName']
        },
        'dlo_rbTradeName': {
            'filename': 'Trn.xlsx',
            'miacCode': 'TrnName',
            'name': 'TrnName',
            'latinName': 'NameLat',
            'matchFields': ['name', 'latinName']
        }
    }

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setupUi(self)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(1)
        self.progressBar.setValue(0)
        self.btnImport.setEnabled(False)
        CImport.__init__(self, self.logBrowser)
        self.errors = 0

        self.nUpdated = 0
        self.nProcessed = 0

    def setParams(self, params):
        self.edtFileName.setText(forceString(params.get('inputfile')))

    def params(self):
        return {
            'inputfile': toVariant(self.edtFileName.text())
        }

    def importFormulary(self):
        db = QtGui.qApp.db
        try:
            db.transaction()
            zipFileName = self.edtFileName.text()
            if not is_zipfile(forceString(zipFileName)):
                self.logBrowser.append(u'Файл не является архивом')
                self.logBrowser.update()
                return

            # names = ['Mnn.xlsx', 'Trn.xlsx']
            archive = ZipFile(forceString(zipFileName), "r")
            fileList = archive.namelist()
            for table in self.tables:
                name = self.tables[table]['filename']
                if name not in fileList:
                    self.logBrowser.append(u'В архиве отсутствует файл ' + name + u'.')
                    self.logBrowser.update()
                    return

            xlsData = {}
            totalEntries = 0
            self.logBrowser.append(u'Идет загрузка данных из архива в оперативную память.')
            QtGui.qApp.processEvents()

            for table in self.tables:
                name = self.tables[table]['filename']
                outFile = QtCore.QTemporaryFile()
                if not outFile.open(QtCore.QFile.WriteOnly):
                    self.logBrowser.append(u'Не удаётся открыть файл для записи %s:\n%s.' % (outFile, outFile.errorString()))
                    self.logBrowser.update()
                    return

                data = archive.read(name)
                outFile.write(data)
                outFile.close()
                fileInfo = QtCore.QFileInfo(outFile)

                xlsData[table] = list(CXLSXReader(forceString(fileInfo.filePath())))
                totalEntries += len(xlsData[table]) - 1

            self.logBrowser.append(u'Загрузка данных в оперативную память завершена.')
            self.logBrowser.append(u'Импорт начат ' + QDateTime().currentDateTime().toString('dd.MM.yyyy H:mm:ss') + u'.')
            self.progressBar.setMaximum(totalEntries)
            self.progressBar.setFormat('%v/%m')
            QtGui.qApp.processEvents()

            self.nUpdatted = 0
            self.nProcessed = 0
            for table in self.tables:
                items = xlsData[table]
                fields, rows = items[0], items[1:]
                self.processTable(table, fields, rows)

            db.commit()
            self.logBrowser.append(u'--------------------------------------- ')
            self.logBrowser.append(u'Импорт завершён ' + QDateTime().currentDateTime().toString('dd.MM.yyyy H:mm:ss') + u'.')
            self.log.append(u'Обработано записей в справочниках: %d; обновлено записей в таблицах: %d' % (self.nProcessed, self.nUpdated) + u'.')
            self.logBrowser.append(u'Готово.')
            self.logBrowser.append(u' ')
        except Exception as ex:
            self.log.append(u'<b><font color=red>Неизвестная ошибка:</font></b> ' + ex.message)
            db.rollback()

    def processTable(self, tableName, fields, rows):
        db = QtGui.qApp.db
        table = db.table(tableName)
        tableInfo = self.tables[tableName]
        matchFields = tableInfo['matchFields']
        for row in rows:
            cond = []
            for field in matchFields:
                index = fields.index(tableInfo[field])
                if 0 <= index < len(row):
                    cond.append(table[field].eq(row[index]))
            records = db.getRecordList(table, where=db.joinOr(cond))

            bestRecord = None
            bestScore = 0
            for record in records:
                score = 0
                for field in matchFields:
                    index = fields.index(tableInfo[field])
                    if 0 <= index < len(row):
                        if forceString(record.value(field)).lower() == row[fields.index(tableInfo[field])].lower():
                            score += 1
                if score > bestScore:
                    bestRecord = record
                    bestScore = score
            if bestRecord is not None:
                bestRecord.setValue('miacCode', toVariant(row[fields.index(tableInfo['miacCode'])]))
                db.updateRecord(table, bestRecord)
                self.nUpdated += 1
            self.nProcessed += 1

            self.progressBar.setValue(self.progressBar.value() + 1)
            QtGui.qApp.processEvents()

    @QtCore.pyqtSlot()
    def on_btnClose_clicked(self):
        self.close()

    @QtCore.pyqtSlot()
    def on_btnImport_clicked(self):
        self.importFormulary()

    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл со справочниками МИАЦ', self.edtFileName.text(), u'Файлы ZIP (*.zip)')
        if fileName != '' :
            self.edtFileName.setText(QtCore.QDir.toNativeSeparators(fileName))
            self.btnImport.setEnabled(True)
