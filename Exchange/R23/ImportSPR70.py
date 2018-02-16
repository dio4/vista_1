 #!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import Exchange.Cimport
import Exchange.Ui_ImportSPR18
import Exchange.Utils

from PyQt4 import QtCore, QtGui

from library.dbfpy.dbf          import Dbf
from library.exception          import CException
from library.Utils              import forceString, forceStringEx, toVariant, getVal, forceDate
from library.constants          import dateLeftInfinity, dateRightInfinity

 # Импорт справочника услуг для Краснодарского Края

def ImportSPR70(widget):
        dialog = CImportSPR70(widget)
        dialog.exec_()

class CImportSPR70(Exchange.Cimport.CDBFimport, QtGui.QDialog, Exchange.Ui_ImportSPR18.Ui_Dialog):

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        super(CImportSPR70, self).__init__(self, self.log)
        self.progressBar.setFormat('%v')
        self.edtFileName.setText(forceString(getVal(QtGui.qApp.preferences.appPrefs, 'ImportSPR69FileName', '')))
        self.setWindowTitle(u'Импорт комбинации КСГ из SPR70')

    def openDBF(self):
        dbf = None

        fileName = forceStringEx(self.edtFileName.text())
        result = os.path.isfile(fileName)
        if result:
            dbf = Dbf(fileName, readOnly=True, encoding='cp866')
            fieldsList = ['KSGMKBX', 'KSGKUSL', 'KSGITOG', 'DATN', 'DATO']
            if not Exchange.Utils.dbfCheckNames(dbf, fieldsList):
                raise CException(u'файл %s\nне содержит одного из полей:\n%s' % (fileName, ', '.join(fieldsList)))
            self.labelNum.setText(u'всего записей в источнике: '+str(dbf.recordCount))
        return dbf

    @staticmethod
    def fillSPR70Record(db, table, record, begDate=None, endDate=None, KSGMKBX=None, KSGKUSL=None, KSGITOG=None):
        if begDate is not None: record.setValue('begDate', begDate)
        if endDate is not None: record.setValue('endDate', endDate)
        if KSGMKBX is not None: record.setValue('KSGMKBX', KSGMKBX)
        if KSGKUSL is not None: record.setValue('KSGKUSL', KSGKUSL)
        if KSGITOG is not None: record.setValue('KSGITOG', KSGITOG)
        db.insertOrUpdate(table, record)

    def startImport(self):
        db = QtGui.qApp.db
        dbf = self.openDBF()
        nprocessed = 0
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(dbf.recordCount)

        tblSPR70 = db.table('mes.SPR70')

        for row in dbf:
            self.progressBar.step()
            QtGui.qApp.processEvents()
            if self.abort:
                self.log.append(u'Прервано пользователем')
                return

            mesMkbCode = forceString(row['KSGMKBX'])
            mesServiceCode = forceStringEx(row['KSGKUSL'])
            mesItogCode = forceStringEx(row['KSGITOG'])
            begDate = forceDate(row['DATN'])
            if not begDate: begDate = dateLeftInfinity # Сейчас мы считаем, что так быть не может.
            endDate = forceDate(row['DATO'])
            if not endDate: endDate = dateRightInfinity

            SPR70List = db.getRecordList(tblSPR70,
                                         cols='*',
                                         where=db.joinAnd([
                                             tblSPR70['begDate'].eq(begDate),
                                             tblSPR70['endDate'].eq(endDate),
                                             tblSPR70['KSGMKBX'].eq(mesMkbCode),
                                             tblSPR70['KSGKUSL'].eq(mesServiceCode),
                                             tblSPR70['KSGITOG'].eq(mesItogCode)]))

            if len(SPR70List) > 1: # Несколько идентичных записей. Вставлять ничего не надо, но надо предупредить пользователя, что у него база в плохом состоянии
                self.addDuplicateAlertToLog(u'SPR70 (mes.SPR70)', mesMkbCode + ';' + mesServiceCode + ';' + mesItogCode, [r.value('id') for r in SPR70List])
            elif len(SPR70List) == 1: continue # Запись уже есть. Вставлять не надо.
            else: #Записи нет. Возможно, есть запись с неограниченным сроком действия (endDate == dateRightInfinity), а у нас с ограниченным
                SPR70List = db.getRecordList(tblSPR70,
                                            cols='*',
                                            where=db.joinAnd([
                                                tblSPR70['begDate'].eq(begDate),
                                                tblSPR70['endDate'].eq(dateRightInfinity),
                                                tblSPR70['KSGMKBX'].eq(mesMkbCode),
                                                tblSPR70['KSGKUSL'].eq(mesServiceCode),
                                                tblSPR70['KSGITOG'].eq(mesItogCode)]))
                if len(SPR70List) > 1: # Несколько идентичных записей. Обновляем все, но надо предупредить пользователя, что у него база в плохом состоянии
                    self.addDuplicateAlertToLog(u'SPR70 (mes.SPR70)', mesMkbCode + ';' + mesServiceCode + ';' + mesItogCode, [r.value('id') for r in SPR70List])
                    for record in SPR70List: self.fillSPR70Record(db, tblSPR70, record, endDate=endDate)   # Обновить требуется только дату окончания
                elif len(SPR70List) == 1: self.fillSPR70Record(db, tblSPR70, SPR70List[0], endDate=endDate) # Обновляем единственную запись. Всё ок
                else: self.fillSPR70Record(db, tblSPR70, tblSPR70.newRecord(), begDate, endDate, mesMkbCode, mesServiceCode, mesItogCode) # Ничего не нашли. Надо вставить запись

            nprocessed += 1

        self.log.append(u'Обработано %d записей' % nprocessed)
        self.log.append(u'готово')

        QtGui.qApp.preferences.appPrefs['ImportSPR70FileName'] = toVariant(self.edtFileName.text())

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