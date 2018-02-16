#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from PyQt4 import QtCore, QtGui

from Exchange.Cimport           import CDBFimport
from Exchange.Utils             import dbfCheckNames
from Exchange.Ui_ImportSPR18    import Ui_Dialog
from library.constants          import dateLeftInfinity, dateRightInfinity

from library.dbfpy.dbf          import Dbf
from library.exception          import CException
from library.Utils              import forceString, forceStringEx, toVariant, getVal, forceDate


# Импорт справочника услуг для Краснодарского Края

def ImportSPR71(widget):
    dlg = CImportSPR71(widget)
    dlg.exec_()


class CImportSPR71(CDBFimport, QtGui.QDialog, Ui_Dialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        super(CImportSPR71, self).__init__(self, self.log)
        self.progressBar.setFormat('%v')
        self.edtFileName.setText(forceString(getVal(QtGui.qApp.preferences.appPrefs, 'ImportSPR71FileName', '')))
        self.setWindowTitle(u'Загрузка услуг из SPR71')

    def openDBF(self):
        dbf = None
        fileName = forceStringEx(self.edtFileName.text())
        result = os.path.isfile(fileName)
        if result:
            dbf = Dbf(fileName, readOnly=True, encoding='cp866')
            fieldsList = ['CODE', 'DATN', 'DATO']
            if not dbfCheckNames(dbf, fieldsList):
                raise CException(u'файл %s\nне содержит одного из полей:\n%s' % (fileName, ', '.join(fieldsList)))
            self.labelNum.setText(u'всего записей в источнике: '+str(dbf.recordCount))
        return dbf

    @staticmethod
    def fillSPR71Record(db, table, record, begDate=None, endDate=None, CODE=None):
        if begDate is not None:     record.setValue('begDate', begDate)
        if endDate is not None:     record.setValue('endDate', endDate)
        if CODE is not None:        record.setValue('CODE', CODE)
        db.insertOrUpdate(table, record)

    def startImport(self):
        db = QtGui.qApp.db
        dbf = self.openDBF()
        nprocessed = 0
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(dbf.recordCount)

        tblSPR71 = db.table('mes.SPR71')

        for row in dbf:
            self.progressBar.step()
            QtGui.qApp.processEvents()
            if self.abort:
                self.log.append(u'Прервано пользователем')
                return

            code = forceString(row['CODE'])
            begDate = forceDate(row['DATN'])
            if not begDate: begDate = dateLeftInfinity # Сейчас мы считаем, что так быть не может.
            endDate = forceDate(row['DATO'])
            if not endDate: endDate = dateRightInfinity

            SPR71List = db.getRecordList(tblSPR71,
                                         cols='*',
                                         where=db.joinAnd([
                                             tblSPR71['begDate'].eq(begDate),
                                             tblSPR71['endDate'].eq(endDate),
                                             tblSPR71['CODE'].eq(code)]))
            if len(SPR71List) > 1: self.addDuplicateAlertToLog(u'SPR71 (mes.SPR71)', code, [r.value('id') for r in SPR71List])
            elif len(SPR71List) == 1: continue
            else:
                SPR71List = db.getRecordList(tblSPR71,
                                            cols='*',
                                            where=db.joinAnd([
                                                tblSPR71['begDate'].eq(begDate),
                                                tblSPR71['endDate'].eq(dateRightInfinity),
                                                tblSPR71['CODE'].eq(code)]))
                if len(SPR71List) > 1:
                    self.addDuplicateAlertToLog(u'SPR71 (mes.SPR71)', code, [r.value('id') for r in SPR71List])
                    for record in SPR71List: self.fillSPR71Record(db, tblSPR71, record, endDate=endDate)
                elif len(SPR71List) == 1: self.fillSPR71Record(db, tblSPR71, SPR71List[0], endDate=endDate)
                else: self.fillSPR71Record(db, tblSPR71, tblSPR71.newRecord(), begDate, endDate, code)

            nprocessed += 1

        self.log.append(u'Обработано %d записей' % nprocessed)
        self.log.append(u'готово')
        QtGui.qApp.preferences.appPrefs['ImportSPR71FileName'] = toVariant(self.edtFileName.text())

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