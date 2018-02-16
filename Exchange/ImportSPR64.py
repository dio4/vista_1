#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from PyQt4 import QtCore, QtGui

from Exchange.Cimport           import CDBFimport
from Exchange.Utils             import dbfCheckNames
from Exchange.Ui_ImportSPR18    import Ui_Dialog

from library.dbfpy.dbf          import Dbf
from library.exception          import CException
from library.Utils              import forceString, forceStringEx, toVariant, getVal


# Импорт справочника ошибок проверки при эимпорте в МИС

def ImportSPR64(widget):
    dlg = CImportSPR64(widget)
    dlg.exec_()


class CImportSPR64(CDBFimport, QtGui.QDialog, Ui_Dialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        super(CImportSPR64, self).__init__(self, self.log)
        self.progressBar.setFormat('%v')
        self.newServices = []
        self.edtFileName.setText(forceString(getVal(QtGui.qApp.preferences.appPrefs, 'ImportSPR64FileName', '')))
        self.setWindowTitle(u'Загрузка справочника ошибок из SPR64')

    def openDBF(self):
        dbf = None
        fileName = forceStringEx(self.edtFileName.text())
        result = os.path.isfile(fileName)
        if result:
            dbf = Dbf(fileName, readOnly=True, encoding='cp866')
            fieldsList = ['CODE', 'NAME', 'ORG', 'ISPAY', 'DATN', 'DATO']
            if not dbfCheckNames(dbf, fieldsList):
                raise CException(u'файл %s\nне содержит одного из полей:\n%s' % (fileName, ', '.join(fieldsList)))
            self.labelNum.setText(u'всего записей в источнике: '+str(dbf.recordCount))
        return dbf

    def startImport(self):
        db = QtGui.qApp.db
        dbf = self.openDBF()
        nprocessed = 0
        self.newServices = []
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(dbf.recordCount)
        self.progressBar.setFormat('%v/%m (%p%)')
        stmt = u"""
            CREATE TABLE  IF NOT EXISTS `rbcheckaccountsspr64` (
              `id` INT NOT NULL AUTO_INCREMENT,
              `CODE` VARCHAR(3) NULL COMMENT 'Код ошибки',
              `NAME` VARCHAR(100) NULL COMMENT 'Расшифровка ошибки',
              `ORG` VARCHAR(10) NULL COMMENT 'Организация',
              `ISPAY` TINYINT(1) NULL,
              `DATN` DATE NULL COMMENT 'Дата начала действия',
              `DATO` DATE NULL COMMENT 'Дата окончания',
              PRIMARY KEY (`id`))
            COMMENT = 'SPR64. Справочник ошибок выявленных при проверке данных органами МИАЦ, МИС и ТФОМС';
        """
        db.query(stmt)
        for row in dbf:
            self.progressBar.step()
            QtGui.qApp.processEvents()
            if self.abort:
                self.log.append(u'Прервано пользователем')
                return
            code        = row['CODE']
            name        = row['NAME']
            org         = row['ORG']
            isPay       = row['ISPAY']
            datn        = row['DATN']
            dato        = row['DATO']

            table = db.table('rbcheckaccountsspr64')
            record = db.getRecordEx(table, ['id', 'CODE', 'NAME', 'ORG', 'ISPAY', 'DATN', 'DATO'], [table['CODE'].eq(code)])
            if record:
                record.setValue('CODE', toVariant(code))
                record.setValue('NAME', toVariant(name))
                record.setValue('ORG', toVariant(org))
                record.setValue('ISPAY', toVariant(isPay))
                record.setValue('DATN', toVariant(datn))
                record.setValue('DATO', toVariant(dato))
                db.updateRecord(table, record)
            else:
                record = table.newRecord()
                record.setValue('CODE', toVariant(code))
                record.setValue('NAME', toVariant(name))
                record.setValue('ORG', toVariant(org))
                record.setValue('ISPAY', toVariant(isPay))
                record.setValue('DATN', toVariant(datn))
                record.setValue('DATO', toVariant(dato))
                db.insertRecord(table, record)
            nprocessed += 1
        if self.newServices:
            self.processNewActionTypes()
        self.log.append(u'Обработано %d записей' % nprocessed)
        self.log.append(u'готово')
        QtGui.qApp.preferences.appPrefs['ImportSPR64FileName'] = toVariant(self.edtFileName.text())

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
        # if QtGui.QMessageBox.critical(self,
        #                            u'Внимание!',
        #                            u'Модуль загрузки данного справочника находится в режиме тестирования.\nПожалуйста, используйте его только на тестовой базе данных, чтобы избежать потери данных.',
        #                            QtGui.QMessageBox.Ignore|QtGui.QMessageBox.Abort,
        #                            QtGui.QMessageBox.Abort) == QtGui.QMessageBox.Ignore:
        super(CImportSPR64, self).on_btnImport_clicked()


