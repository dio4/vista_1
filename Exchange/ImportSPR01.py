#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from PyQt4 import QtCore, QtGui

from Exchange.Cimport import CDBFimport
from Exchange.Utils import dbfCheckNames
from Exchange.Ui_ImportSPR18 import Ui_Dialog

from library.dbfpy.dbf import Dbf
from library.exception import CException
from library.Utils import forceString, forceStringEx, toVariant, getVal, forceRef


# Импорт справочника услуг для Краснодарского Края

def ImportSPR01(widget):
    dlg = CImportSPR01(widget)
    dlg.exec_()


class CImportSPR01(CDBFimport, QtGui.QDialog, Ui_Dialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        super(CImportSPR01, self).__init__(self, self.log)
        self.progressBar.setFormat('%v')
        self.newServices = []
        self.edtFileName.setText(forceString(getVal(QtGui.qApp.preferences.appPrefs, 'ImportSPR01FileName', '')))
        self.setWindowTitle(u'Загрузка медицинских организаций из SPR01')

    def openDBF(self):
        dbf = None
        fileName = forceStringEx(self.edtFileName.text())
        result = os.path.isfile(fileName)
        if result:
            dbf = Dbf(fileName, readOnly=True, encoding='cp866')
            fieldsList = ['OGRN', 'CODE', 'CODE_PAR', 'CODE_RF', 'NAME', 'DATN', 'DATO', 'IS_FAP', 'IS_SMP', 'IS_GUZ',
                          'IS_CZ', 'RUKPOST', 'CODE_NEW']
            if not dbfCheckNames(dbf, fieldsList):
                raise CException(u'файл %s\nне содержит одного из полей:\n%s' % (fileName, ', '.join(fieldsList)))
            self.labelNum.setText(u'всего записей в источнике: ' + str(dbf.recordCount))
        return dbf

    def startImport(self):
        db = QtGui.qApp.db
        dbf = self.openDBF()
        nprocessed = 0
        self.newServices = []
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(dbf.recordCount)
        self.progressBar.setFormat('%v/%m (%p%)')
        codeToIdmap = {}
        needToUpdate = {}
        for row in dbf:
            self.progressBar.step()
            QtGui.qApp.processEvents()
            if self.abort:
                self.log.append(u'Прервано пользователем')
                return
            infisCode = row['CODE']
            infisCodeNew = row['CODE_NEW']
            infisCode_headId = row['CODE_PAR']
            OGRN = row['OGRN']
            name = row['NAME']  # fullName,shortName,title
            notes_isGuz = row['IS_GUZ']  # "Террит., федеральная МО."
            datn = row['DATN']
            dato = row['DATO']
            notes = []
            notes.append(u'Террит., федеральная МО.' if int(notes_isGuz) == 1 else '')
            notes = '\n'.join(notes).strip()

            if infisCode_headId:
                needToUpdate[infisCode] = infisCode_headId

            table = db.table('Organisation')

            # if infisCodeNew:
            #     record = db.getRecordEx(table, ['id', 'infisCode', 'OGRN', 'fullName', 'shortName', 'title', 'notes'],
            #                             table['infisCode'].eq(infisCode))
            #     infisCode = infisCodeNew
            #     record.setValue('infisCode', toVariant(infisCode))
            # else:
            record = db.getRecordEx(table,
                                    ['id', 'infisCode', 'OGRN', 'fullName', 'shortName', 'title', 'notes', 'DATN',
                                     'DATO', 'area'], table['infisCode'].eq(infisCode))
            if record:
                codeToIdmap[infisCode] = forceRef(record.value('id'))
                record.setValue('OGRN', toVariant(OGRN))
                record.setValue('fullName', toVariant(name))
                record.setValue('shortName', toVariant(name))
                record.setValue('title', toVariant(name))
                record.setValue('notes', toVariant(notes))

                if dato is None:
                    dato = '2200-01-01'
                if datn is None:
                    datn = '2000-01-01'
                record.setValue('DATN', toVariant(datn))
                record.setValue('DATO', toVariant(dato))

                area=str(QtGui.qApp.provinceKLADR())
                record.setValue('area', toVariant(area))
                db.updateRecord(table, record)
            else:
                record = table.newRecord()
                record.setValue('infisCode', toVariant(infisCode))
                record.setValue('OGRN', toVariant(OGRN))
                record.setValue('fullName', toVariant(name))
                record.setValue('shortName', toVariant(name))
                record.setValue('title', toVariant(name))
                record.setValue('notes', toVariant(notes))

                if dato is None:
                    dato = '2200-01-01'
                if datn is None:
                    datn = '2000-01-01'
                record.setValue('DATN', toVariant(datn))
                record.setValue('DATO', toVariant(dato))

                area=str(QtGui.qApp.provinceKLADR())
                record.setValue('area', toVariant(area))

                db.insertRecord(table, record)

            nprocessed += 1

        missingCodes = []
        needToUpdate2 = {}
        for CODE, CODE_PAR in needToUpdate.items():
            Id = codeToIdmap.get(CODE_PAR)
            if Id:
                db.query('UPDATE Organisation SET head_id = %s WHERE infisCode = "%s"' % (Id, CODE))
            else:
                needToUpdate2[CODE] = CODE_PAR
                missingCodes.append(CODE_PAR)

        if missingCodes:
            codeToIdmap2 = {}
            rl = db.getRecordList(table, ['id', 'infisCode'], table['infisCode'].inlist(missingCodes))
            for record in rl:
                codeToIdmap2[forceString(record.value('infisCode'))] = forceRef(record.value('id'))
            for CODE, CODE_PAR in needToUpdate2.items():
                Id = codeToIdmap2.get(CODE_PAR)
                if Id:
                    db.query('UPDATE Organisation SET head_id = %s WHERE infisCode = "%s"' % (Id, CODE))

        if self.newServices:
            self.processNewActionTypes()
        self.log.append(u'Обработано %d записей' % nprocessed)
        self.log.append(u'готово')
        QtGui.qApp.preferences.appPrefs['ImportSPR01FileName'] = toVariant(self.edtFileName.text())

    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы DBF (*.dbf)')
        if fileName != '':
            self.edtFileName.setText(QtCore.QDir.toNativeSeparators(fileName))
            self.btnImport.setEnabled(True)

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtFileName_textChanged(self, fileName):
        self.btnImport.setEnabled(fileName != '')

    @QtCore.pyqtSlot()
    def on_btnImport_clicked(self):
        if QtGui.QMessageBox.critical(self,
                                      u'Внимание!',
                                      u'Модуль загрузки данного справочника находится в режиме тестирования.\nПожалуйста, используйте его только на тестовой базе данных, чтобы избежать потери данных.',
                                      QtGui.QMessageBox.Ignore | QtGui.QMessageBox.Abort,
                                      QtGui.QMessageBox.Abort) == QtGui.QMessageBox.Ignore:
            super(CImportSPR01, self).on_btnImport_clicked()


