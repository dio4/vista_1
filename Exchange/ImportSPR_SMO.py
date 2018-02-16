#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from PyQt4 import QtCore, QtGui

from Exchange.Cimport           import CDBFimport
from Exchange.Utils             import dbfCheckNames
from Exchange.Ui_ImportSPR_SMO import Ui_ImportSprSmoDialog

from library.dbfpy.dbf          import Dbf
from library.DbfViewDialog      import CDbfViewDialog
from library.exception          import CException
from library.Utils              import forceString, forceStringEx, toVariant, getVal, forceRef


# Импорт справочника услуг для Краснодарского Края

def ImportSPR_SMO(widget):
    dlg = CImportSPR_SMO(widget)
    dlg.exec_()


class CImportSPR_SMO(CDBFimport, QtGui.QDialog, Ui_ImportSprSmoDialog):
    def __init__(self, parent):
        self.totalRecordCount = 0
        self.dbfSPR02 = None
        self.dbfSPR03 = None
        self.dbfSPR33 = None
        self.OKPFcache = {}    # {OKPF_code : OKPF_id}
        self.OKATOcache = {}   # {OKATO : area}
        self.HeadOrgs = {}     # {OGRN : (CODE, id)}
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        super(CImportSPR_SMO, self).__init__(self, self.log)
        self.edtFileName_SPR02.setText(forceString(getVal(QtGui.qApp.preferences.appPrefs, 'ImportSPR02FileName', '')))
        self.edtFileName_SPR03.setText(forceString(getVal(QtGui.qApp.preferences.appPrefs, 'ImportSPR03FileName', '')))
        self.edtFileName_SPR33.setText(forceString(getVal(QtGui.qApp.preferences.appPrefs, 'ImportSPR33FileName', '')))

    def openDBF(self, fileName, fieldsList):
        dbf = None
        result = os.path.isfile(fileName)
        if result:
            dbf = Dbf(fileName, readOnly=True, encoding='cp866')
            if not dbfCheckNames(dbf, fieldsList):
                raise CException(u'файл %s\nне содержит одного из полей:\n%s' % (fileName, ', '.join(fieldsList)))
            self.totalRecordCount += dbf.recordCount
            self.labelNum.setText(u'всего записей в источниках: '+str(self.totalRecordCount))
        return dbf

    def startImport(self):
        fileName_SPR02 = forceStringEx(self.edtFileName_SPR02.text())
        if fileName_SPR02:
            fieldsList_SPR02 = ['OGRN', 'CODE', 'CODE_RF', 'NAME', 'DATN', 'DATO']
            self.dbfSPR02 = self.openDBF(fileName_SPR02, fieldsList_SPR02)

        fileName_SPR03 = forceStringEx(self.edtFileName_SPR03.text())
        if fileName_SPR03:
            fieldsList_SPR03 = ['OGRN', 'CODE', 'NAME']
            self.dbfSPR03 = self.openDBF(fileName_SPR03, fieldsList_SPR03)

        fileName_SPR33 = forceStringEx(self.edtFileName_SPR33.text())
        if fileName_SPR33:
            fieldsList_SPR33 = ['TF_OKATO', 'SMOCOD', 'NAM_SMOP', 'NAM_SMOK', 'INN', 'OGRN', 'KPP', 'INDEX_J', 'ADDR_J',
                                'INDEX_F', 'ADDR_F', 'OKOPF', 'FAM_RUK', 'IM_RUK', 'OT_RUK', 'PHONE', 'FAX', 'E_MAIL',
                                'ORG', 'D_BEGIN', 'D_END']
            self.dbfSPR33 = self.openDBF(fileName_SPR33, fieldsList_SPR33)

        self.progressBar.setValue(0)
        self.progressBar.setMaximum(self.totalRecordCount)
        self.nprocessed = 0
        self.progressBar.setFormat('%v/%m (%p%)')

        if fileName_SPR02:
            self.processSPR02()
        if fileName_SPR33:
            self.processSPR33()
        if fileName_SPR03:
            self.processSPR03()

        self.log.append(u'готово')

        QtGui.qApp.preferences.appPrefs['ImportSPR02FileName'] = toVariant(self.edtFileName_SPR02.text())
        QtGui.qApp.preferences.appPrefs['ImportSPR03FileName'] = toVariant(self.edtFileName_SPR03.text())
        QtGui.qApp.preferences.appPrefs['ImportSPR33FileName'] = toVariant(self.edtFileName_SPR33.text())

    def processSPR02(self):
        db = QtGui.qApp.db
        count = 0
        infisCode_list = []
        for row in self.dbfSPR02:
            count += 1
            self.progressBar.step()
            QtGui.qApp.processEvents()
            if self.abort:
                self.log.append(u'Прервано пользователем')
                return
            infisCode = row['CODE']
            miacCode  = row['CODE_RF']
            OGRN      = row['OGRN']
            name      = row['NAME']       # fullName,shortName,title
            infisCode_list.append(infisCode)
            table = db.table('Organisation')
            cond = [table['infisCode'].eq(infisCode), table['isInsurer'].eq(1)]
            record_infisCode = db.getRecordEx(table, ['id', 'infisCode', 'OGRN', 'fullName', 'shortName', 'title', 'miacCode'], where=db.joinAnd(cond))
            cond = [table['miacCode'].eq(miacCode), table['isInsurer'].eq(1)]
            record_miacCode = db.getRecordEx(table, ['id', 'infisCode', 'OGRN', 'fullName', 'shortName', 'title', 'miacCode'], where=db.joinAnd(cond))
            if record_infisCode:
                record = record_infisCode
            elif record_miacCode:
                record = record_miacCode
            else:
                record = table.newRecord()
            record.setValue('infisCode', toVariant(infisCode))
            record.setValue('OGRN', toVariant(OGRN))
            record.setValue('fullName', toVariant(name))
            record.setValue('shortName', toVariant(name))
            record.setValue('title', toVariant(name))
            record.setValue('miacCode', toVariant(miacCode))
            record.setValue('isInsurer', toVariant(1))
            db.insertOrUpdate(table, record)
            self.nprocessed += 1
        cond = [table['infisCode'].inlist(infisCode_list), table['isInsurer'].eq(1)]
        record_list = db.getRecordList(table, ['id', 'infisCode', 'OGRN'], where=db.joinAnd(cond))
        for record in record_list:
            OGRN = forceString(record.value('OGRN'))
            CODE = forceString(record.value('infisCode'))
            Id = forceRef(record.value('id'))
            self.HeadOrgs[OGRN] = (CODE, Id)
        self.log.append(u'Обработано %d записей из SPR02' % count)

    def processSPR03(self):
        db = QtGui.qApp.db
        count = 0
        for row in self.dbfSPR03:
            count += 1
            self.progressBar.step()
            QtGui.qApp.processEvents()
            if self.abort:
                self.log.append(u'Прервано пользователем')
                return
            infisCode = row['CODE']
            OGRN      = row['OGRN']
            name      = row['NAME']       # fullName,shortName,title
            head_id = None
            if OGRN in self.HeadOrgs:
                t = self.HeadOrgs.get(OGRN)
                head_id = t[1] if t[0] != infisCode else None
            table = db.table('Organisation')
            cond = [table['infisCode'].eq(infisCode), table['isInsurer'].eq(1)]
            record = db.getRecordEx(table, ['id', 'infisCode', 'OGRN', 'fullName', 'shortName', 'title', 'head_id'], where=db.joinAnd(cond))
            if record:
                record.setValue('OGRN', toVariant(OGRN))
                record.setValue('fullName', toVariant(name))
                record.setValue('shortName', toVariant(name))
                record.setValue('title', toVariant(name))
                if not forceRef(record.value('head_id')):
                    record.setValue('head_id', toVariant(head_id))
                db.updateRecord(table, record)
            else:
                record = table.newRecord()
                record.setValue('infisCode', toVariant(infisCode))
                record.setValue('OGRN', toVariant(OGRN))
                record.setValue('fullName', toVariant(name))
                record.setValue('shortName', toVariant(name))
                record.setValue('title', toVariant(name))
                record.setValue('head_id', toVariant(head_id))
                record.setValue('isInsurer', toVariant(1))
                db.insertRecord(table, record)
            self.nprocessed += 1
        self.log.append(u'Обработано %d записей из SPR03' % count)

    def processSPR33(self):
        db = QtGui.qApp.db
        count = 0
        for row in self.dbfSPR33:
            count += 1
            self.progressBar.step()
            QtGui.qApp.processEvents()
            if self.abort:
                self.log.append(u'Прервано пользователем')
                return
            OKATO     = row['TF_OKATO']
            miacCode  = row['SMOCOD']
            fullName  = row['NAM_SMOP']
            shortName = row['NAM_SMOK']
            title     = row['NAM_SMOK']
            INN       = row['INN']
            OGRN      = row['OGRN']
            KPP       = row['KPP']
            Address = u'%s %s' % (str(row['INDEX_J']), row['ADDR_J'])
            OKPF_code = row['OKOPF']
            OKPF_id = self.OKPFcache.get(OKPF_code, None)
            if not OKPF_id:
                OKPF_id = forceRef(db.translate('rbOKPF', 'code', OKPF_code, 'id'))
                self.OKPFcache[OKPF_code] = OKPF_id
            chief = u'%s %s %s' % (row['FAM_RUK'].strip(), row['IM_RUK'].strip(), row['OT_RUK'].strip())
            phone = row['PHONE']
            notes = u'факс: %s email: %s' % (row['FAX'], row['E_MAIL'])
            compulsoryServiceStop = 1 if row['D_END'] else 0

            table = db.table('Organisation')
            cond = [table['miacCode'].eq(miacCode), table['isInsurer'].eq(1)]
            record = db.getRecordEx(table, ['id', 'OKATO', 'fullName', 'shortName', 'title', 'INN', 'OGRN', 'KPP',
                                            'Address', 'OKPF_id', 'chief', 'phone', 'notes', 'compulsoryServiceStop',
                                            'area'],
                                    where=db.joinAnd(cond))
            area = self.OKATOcache.get(OKATO, None)
            if not area:
                stmt = '''SELECT CODE
                          FROM kladr.KLADR k
                          WHERE
                          LEFT(k.OCATD, 5) = "%s"
                          AND RIGHT(k.CODE, 11) = "00000000000"''' % OKATO
                query = db.query(stmt)
                if query.first():
                    record2 = query.record()
                    area = forceString(record2.value('CODE'))
                    self.OKATOcache[OKATO] = area
            if record:
                record.setValue('OKATO', toVariant(OKATO))
                record.setValue('fullName', toVariant(fullName))
                record.setValue('shortName', toVariant(shortName))
                record.setValue('title', toVariant(title))
                record.setValue('INN', toVariant(INN))
                record.setValue('OGRN', toVariant(OGRN))
                record.setValue('KPP', toVariant(KPP))
                record.setValue('Address', toVariant(Address))
                record.setValue('OKPF_id', toVariant(OKPF_id))
                record.setValue('chief', toVariant(chief))
                record.setValue('phone', toVariant(phone))
                record.setValue('notes', toVariant(notes))
                record.setValue('area', toVariant(area))
                record.setValue('compulsoryServiceStop', toVariant(compulsoryServiceStop))
                db.updateRecord(table, record)
            else:
                record = table.newRecord()
                record.setValue('OKATO', toVariant(OKATO))
                record.setValue('miacCode', toVariant(miacCode))
                record.setValue('fullName', toVariant(fullName))
                record.setValue('shortName', toVariant(shortName))
                record.setValue('title', toVariant(title))
                record.setValue('INN', toVariant(INN))
                record.setValue('OGRN', toVariant(OGRN))
                record.setValue('KPP', toVariant(KPP))
                record.setValue('Address', toVariant(Address))
                record.setValue('OKPF_id', toVariant(OKPF_id))
                record.setValue('chief', toVariant(chief))
                record.setValue('phone', toVariant(phone))
                record.setValue('notes', toVariant(notes))
                record.setValue('area', toVariant(area))
                record.setValue('compulsoryServiceStop', toVariant(compulsoryServiceStop))
                record.setValue('isInsurer', toVariant(1))
                db.insertRecord(table, record)

            self.nprocessed += 1
        self.log.append(u'Обработано %d записей из SPR33' % count)

    @QtCore.pyqtSlot()
    def on_btnSelectFile_SPR02_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName_SPR02.text(), u'Файлы DBF (*.dbf)')
        if fileName != '':
            self.edtFileName_SPR02.setText(QtCore.QDir.toNativeSeparators(fileName))
            self.btnImport.setEnabled(True)

    @QtCore.pyqtSlot()
    def on_btnSelectFile_SPR03_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName_SPR03.text(), u'Файлы DBF (*.dbf)')
        if fileName != '':
            self.edtFileName_SPR03.setText(QtCore.QDir.toNativeSeparators(fileName))
            self.btnImport.setEnabled(True)

    @QtCore.pyqtSlot()
    def on_btnSelectFile_SPR33_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName_SPR33.text(), u'Файлы DBF (*.dbf)')
        if fileName != '':
            self.edtFileName_SPR33.setText(QtCore.QDir.toNativeSeparators(fileName))
            self.btnImport.setEnabled(True)

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtFileName_SPR02_textChanged(self, fileName):
        self.btnImport.setEnabled(fileName != '')

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtFileName_SPR03_textChanged(self, fileName):
        self.btnImport.setEnabled(fileName != '')

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtFileName_SPR33_textChanged(self, fileName):
        self.btnImport.setEnabled(fileName != '')

    @QtCore.pyqtSlot()
    def on_btnView_SPR02_clicked(self):
        fname = forceStringEx(self.edtFileName_SPR02.text())
        if fname:
            CDbfViewDialog(self, fileName=fname).exec_()

    @QtCore.pyqtSlot()
    def on_btnView_SPR03_clicked(self):
        fname = forceStringEx(self.edtFileName_SPR03.text())
        if fname:
            CDbfViewDialog(self, fileName=fname).exec_()

    @QtCore.pyqtSlot()
    def on_btnView_SPR33_clicked(self):
        fname = forceStringEx(self.edtFileName_SPR33.text())
        if fname:
            CDbfViewDialog(self, fileName=fname).exec_()

    @QtCore.pyqtSlot()
    def on_btnImport_clicked(self):
        if QtGui.QMessageBox.critical(self,
                                   u'Внимание!',
                                   u'Модуль загрузки данных справочников находится в режиме тестирования.\nПожалуйста, используйте его только на тестовой базе данных, чтобы избежать потери данных.',
                                   QtGui.QMessageBox.Ignore|QtGui.QMessageBox.Abort,
                                   QtGui.QMessageBox.Abort) == QtGui.QMessageBox.Ignore:
            super(CImportSPR_SMO, self).on_btnImport_clicked()