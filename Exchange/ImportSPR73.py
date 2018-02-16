#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from PyQt4 import QtCore, QtGui

from Exchange.Cimport           import CDBFimport
from Exchange.Utils             import dbfCheckNames
from Exchange.Ui_ImportSPR18    import Ui_Dialog
from library.constants import dateLeftInfinity, dateRightInfinity

from library.dbfpy.dbf          import Dbf
from library.exception          import CException
from library.Utils              import forceString, forceStringEx, toVariant, getVal, forceDate


# Импорт справочника услуг для Краснодарского Края

def ImportSPR73(widget):
    dlg = CImportSPR73(widget)
    dlg.exec_()


class CImportSPR73(CDBFimport, QtGui.QDialog, Ui_Dialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        super(CImportSPR73, self).__init__(self, self.log)
        self.progressBar.setFormat('%v')
        self.edtFileName.setText(forceString(getVal(QtGui.qApp.preferences.appPrefs, 'ImportSPR73FileName', '')))
        self.setWindowTitle(u'Загрузка услуг из SPR73')

    def openDBF(self):
        dbf = None
        fileName = forceStringEx(self.edtFileName.text())
        result = os.path.isfile(fileName)
        if result:
            dbf = Dbf(fileName, readOnly=True, encoding='cp866')
            fieldsList = ['CODE', 'CODE2', 'DATN', 'DATO']
            if not dbfCheckNames(dbf, fieldsList):
                raise CException(u'файл %s\nне содержит одного из полей:\n%s' % (fileName, ', '.join(fieldsList)))
            self.labelNum.setText(u'всего записей в источнике: '+str(dbf.recordCount))
        return dbf

    @staticmethod
    def fillSPR73Record(db, table, record, begDate=None, endDate=None, CODE=None, CODE2=None):
        if begDate is not None:     record.setValue('begDate', begDate)
        if endDate is not None:     record.setValue('endDate', endDate)
        if CODE is not None:        record.setValue('CODE', CODE)
        if CODE2 is not None:       record.setValue('CODE2', CODE2)
        db.insertOrUpdate(table, record)

    def startImport(self):
        db = QtGui.qApp.db
        dbf = self.openDBF()
        nprocessed = 0
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(dbf.recordCount)
        tblSPR73 = db.table('mes.SPR73')

        for row in dbf:
            self.progressBar.step()
            QtGui.qApp.processEvents()
            if self.abort:
                self.log.append(u'Прервано пользователем')
                return

            code = forceString(row['CODE'])
            code2 = forceString(row['CODE2'])
            if not code2: code2 = code
            begDate = forceDate(row['DATN'])
            if not begDate: begDate = dateLeftInfinity # Сейчас мы считаем, что так быть не может.
            endDate = forceDate(row['DATO'])
            if not endDate: endDate = dateRightInfinity

            SPR72List = db.getRecordList(tblSPR73,
                                         cols='*',
                                         where=db.joinAnd([
                                             tblSPR73['begDate'].eq(begDate),
                                             tblSPR73['endDate'].eq(endDate),
                                             tblSPR73['CODE'].eq(code),
                                             tblSPR73['CODE2'].eq(code2)]))
            if len(SPR72List) > 1: self.addDuplicateAlertToLog(u'SPR72 (mes.SPR72)', code, [r.value('id') for r in SPR72List])
            elif len(SPR72List) == 1: continue
            else:
                SPR72List = db.getRecordList(tblSPR73,
                                            cols='*',
                                            where=db.joinAnd([
                                                tblSPR73['begDate'].eq(begDate),
                                                tblSPR73['endDate'].eq(dateRightInfinity),
                                                tblSPR73['CODE'].eq(code),
                                                tblSPR73['CODE2'].eq(code2)]))
                if len(SPR72List) > 1:
                    self.addDuplicateAlertToLog(u'SPR72 (mes.SPR72)', code, [r.value('id') for r in SPR72List])
                    for record in SPR72List: self.fillSPR73Record(db, tblSPR73, record, endDate=endDate)
                elif len(SPR72List) == 1: self.fillSPR73Record(db, tblSPR73, SPR72List[0], endDate=endDate)
                else: self.fillSPR73Record(db, tblSPR73, tblSPR73.newRecord(), begDate, endDate, code, code2)

            nprocessed += 1

        self.log.append(u'Обработано %d записей' % nprocessed)
        self.log.append(u'готово')
        QtGui.qApp.preferences.appPrefs['ImportSPR73FileName'] = toVariant(self.edtFileName.text())

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