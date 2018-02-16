#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from PyQt4 import QtCore, QtGui

from Exchange.Cimport import CDBFimport
from Exchange.Utils import dbfCheckNames
from Exchange.Ui_ImportSPR18 import Ui_Dialog
from library.constants import dateLeftInfinity, dateRightInfinity
from library.dbfpy.dbf import Dbf
from library.exception import CException
from library.Utils import forceInt,forceString, forceStringEx, toVariant, getVal, forceDate, forceDouble

# Импорт справочника услуг для Краснодарского Края


def ImportSPR69(widget):
        dlg=CImportSPR69(widget)
        dlg.exec_()


class CImportSPR69(CDBFimport, QtGui.QDialog, Ui_Dialog):

    age = {0: u'0д-125г', 1: u'-27д', 2: u'28д-90д', 3: u'0г-17г', 4: u'91д-366д', 5: u'18г-', 6: u'-2г', } #TODO:skkachaev: Если будешь менять age 0 — загляни в Events\Utils\getKsgIdListByCond
    sex = {u'': 0, u'М': 1, u'Ж': 2}

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        super(CImportSPR69, self).__init__(self, self.log)
        self.progressBar.setFormat('%v')
        self.edtFileName.setText(forceString(getVal(QtGui.qApp.preferences.appPrefs, 'ImportSPR69FileName', '')))
        self.setWindowTitle(u'Импорт ограничений КСГ из SPR69')
        self.cacheRecords = []

    def openDBF(self):
        dbf = None

        fileName = forceStringEx(self.edtFileName.text())
        result = os.path.isfile(fileName)
        if result:
            dbf = Dbf(fileName, readOnly=True, encoding='cp866')
            fieldsList = ['VPNAME', 'MKBX', 'MKBX2', 'KUSL', 'AGE', 'POL', 'DLIT', 'KSGCODE', 'KSGKOEF', 'DATN', 'DATO']
            if not dbfCheckNames(dbf, fieldsList):
                raise CException(u'файл %s\nне содержит одного из полей:\n%s' % (fileName, ', '.join(fieldsList)))
            self.labelNum.setText(u'всего записей в источнике: '+str(dbf.recordCount))
        return dbf

    def startImport(self):
        db = QtGui.qApp.db
        dbf = self.openDBF()
        nprocessed = 0
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(dbf.recordCount)

        # FIXME:skkachaev:ОООчень большой прирост в скорости импорта. Пока я не вижу, зачем бы нам хранить ссылки на
        # этот справочник, так что ничего ломать это не должно
        db.query(u'TRUNCATE TABLE `mes`.`SPR69`')
        tblSPR69 = db.table('mes.SPR69')

        for row in dbf:
            self.progressBar.step()
            QtGui.qApp.processEvents()
            if self.abort:
                self.log.append(u'Прервано пользователем')
                return

            code = forceString(row['KSGCODE'])
            begDate = forceDate(row['DATN'])
            if not begDate: begDate = dateLeftInfinity # Сейчас мы считаем, что так быть не может.
            endDate = forceDate(row['DATO'])
            if not endDate: endDate = dateRightInfinity
            mkbRow = forceString(row['MKBX'])
            if mkbRow and mkbRow[-1] == '.': mkbRow = mkbRow[:-1] + u'%' # Чтобы потом уметь делать like
            mkb2Row = forceString(row['MKBX2'])
            if mkb2Row and mkb2Row[-1] == '.': mkb2Row = mkb2Row[:-1] + u'%' # Чтобы потом уметь делать like
            serviceCode = forceString(row['KUSL'])
            if serviceCode and serviceCode[-1] == '.': serviceCode = serviceCode[:-1] + u'%' # Чтобы потом уметь делать like
            age = forceInt(row['AGE'])
            sex = forceStringEx(row['POL']).upper()
            ksgKoeff = forceDouble(row['KSGKOEF'])
            duration = forceInt(row['DLIT'])

            self.fillSPR69Record(db, tblSPR69, tblSPR69.newRecord(), begDate, endDate, code, mkbRow, mkb2Row, serviceCode, self.sex[sex], self.age[age], duration, ksgKoeff)

            nprocessed += 1

        if len(self.cacheRecords) != 0:
            db.insertMultipleRecords(db.table('mes.SPR69'), self.cacheRecords)
            self.cacheRecords = []

        self.log.append(u'Обработано %d записей' % nprocessed)
        self.log.append(u'Добавление записи для КСГ 220')
        db.query(u"DELETE FROM mes.SPR69 WHERE KSG = 'G10.2917.220';"
                 u"INSERT INTO mes.SPR69 (id, begDate, endDate, KSG, MKBX, MKBX2, KUSL, sex, age, duration, KSGKoeff) "
                 u"VALUES (NULL, '2017-01-01', '2200-01-01', 'G10.2917.220', '', '', '', 0, '0д-125г', 0, 1.0);")
        self.log.append(u'готово')

        QtGui.qApp.preferences.appPrefs['ImportSPR69FileName'] = toVariant(self.edtFileName.text())

    def fillSPR69Record(self, db, table, record, begDate=None, endDate=None, ksgCode=None, mkbx=None, mkbx2=None, kusl=None, sex=None, age=None, duration=None, ksgKoeff=None):
        if begDate is not None:     record.setValue('begDate', toVariant(begDate))
        if endDate is not None:     record.setValue('endDate', toVariant(endDate))
        if ksgCode is not None:     record.setValue('KSG', toVariant(ksgCode))
        if mkbx is not None:        record.setValue('MKBX', toVariant(mkbx))
        if mkbx2 is not None:       record.setValue('MKBX2', toVariant(mkbx2))
        if kusl is not None:        record.setValue('KUSL', toVariant(kusl))
        if sex is not None:         record.setValue('sex', toVariant(sex))
        if age is not None:         record.setValue('age', toVariant(age))
        if duration is not None:    record.setValue('duration', toVariant(duration))
        if ksgKoeff is not None:    record.setValue('KSGKoeff', toVariant(ksgKoeff))
        self.cacheRecords.append(record)
        if len(self.cacheRecords) >= 1000:
            db.insertMultipleRecords(table, self.cacheRecords)
            self.cacheRecords = []

    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog().getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы DBF (*.dbf)')
        if fileName != '':
            self.edtFileName.setText(QtCore.QDir.toNativeSeparators(fileName))
            self.btnImport.setEnabled(True)

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtFileName_textChanged(self, fileName):
        self.btnImport.setEnabled(fileName != '')
